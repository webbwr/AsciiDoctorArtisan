# AsciiDoc Artisan Architecture

**Version:** 2.0.9 | **Last Updated:** 2025-12-03

## Design Philosophy

**MA Principle (間)** — Japanese concept of negative space. Each module focuses on one thing. Target: <400 lines per file.

**Key Metrics:**
- Core: 13,216 lines across 45+ files (avg ~290 lines/file)
- Workers: 4,718 lines across 19 files (avg ~248 lines/file)
- UI: 21,571 lines across 60+ files (avg ~360 lines/file)
- LSP: 1,359 lines across 8 files (avg ~170 lines/file)

## Package Structure

```
src/asciidoc_artisan/
├── core/           # Business logic (13,216 lines)
│   ├── settings.py              # JSON config management
│   ├── file_operations.py       # Atomic file I/O
│   ├── gpu_detection.py         # Hardware acceleration
│   ├── search_engine.py         # Find & replace
│   ├── spell_checker.py         # Spell validation
│   ├── syntax_checker.py        # AsciiDoc validation
│   ├── template_*.py            # Template system
│   └── ...                      # 45+ focused modules
│
├── ui/             # Qt widgets (21,571 lines)
│   ├── main_window.py           # App controller (1,798 lines)
│   ├── *_manager.py             # Specialized managers
│   ├── preview_handler*.py      # Rendering system
│   └── ...                      # 60+ widget files
│
├── workers/        # QThread workers (4,718 lines)
│   ├── git_worker.py            # Git operations
│   ├── pandoc_worker.py         # Format conversion
│   ├── preview_worker.py        # AsciiDoc→HTML
│   ├── parallel_block_renderer.py  # Multi-core rendering
│   └── ...                      # 19 worker files
│
├── lsp/            # Language Server Protocol (1,359 lines)
│   ├── server.py                # LSP server core
│   ├── completion_provider.py   # Auto-complete
│   ├── diagnostics_provider.py  # Syntax validation
│   ├── hover_provider.py        # Documentation
│   └── symbols_provider.py      # Document outline
│
├── claude/         # Claude AI integration
│   ├── claude_client.py         # API client
│   └── claude_worker.py         # Async worker
│
└── templates/      # Built-in AsciiDoc templates
```

## Threading Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Thread (UI)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ MainWindow  │  │  Editors    │  │  Preview    │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Signal/Slot Connections                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐
│  GitWorker  │  │PandocWorker │  │ ParallelBlockRenderer│
│  (QThread)  │  │  (QThread)  │  │ (ThreadPoolExecutor) │
└─────────────┘  └─────────────┘  └─────────────────────┘
```

### Worker Pattern

All workers follow this pattern:

```python
class Worker(QThread):
    result_ready = Signal(Result)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._command_queue: Queue[Command] = Queue()

    def run(self) -> None:
        while True:
            cmd = self._command_queue.get()
            if cmd is None:  # Shutdown signal
                break
            result = self._process(cmd)
            self.result_ready.emit(result)
```

### Reentrancy Guards

Prevent concurrent operations:

```python
def start_operation(self) -> None:
    if self._is_processing:
        return  # Already running
    self._is_processing = True
    try:
        self.worker.start()
    finally:
        self._is_processing = False  # Reset in signal handler
```

## Multi-Core Rendering (v2.0.9)

### ParallelBlockRenderer

Uses `ThreadPoolExecutor` for CPU-bound AsciiDoc rendering:

```
┌─────────────────────────────────────────────────────────┐
│                  ParallelBlockRenderer                   │
├─────────────────────────────────────────────────────────┤
│  ThreadPoolExecutor (N workers = CPU cores)              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Worker 1 │ │ Worker 2 │ │ Worker 3 │ │ Worker N │   │
│  │  Block A │ │  Block B │ │  Block C │ │  Block N │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       │            │            │            │          │
│       ▼            ▼            ▼            ▼          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Thread-Local AsciiDoc Instances           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- Thread-local storage for AsciiDoc API (thread-safe)
- Block-based parallelization (independent units)
- 2-4x speedup on multi-core systems
- Graceful fallback on single-core

## LSP Architecture (v2.0.9)

### Server Design

```
┌──────────────────────────────────────────────────────────┐
│                  AsciiDocLanguageServer                   │
├──────────────────────────────────────────────────────────┤
│  pygls LanguageServer                                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │                   DocumentState                     │  │
│  │         Thread-safe document storage                │  │
│  └────────────────────────────────────────────────────┘  │
│                          │                                │
│    ┌─────────────────────┼─────────────────────┐         │
│    ▼                     ▼                     ▼         │
│ ┌──────────┐      ┌──────────┐          ┌──────────┐    │
│ │Completion│      │Diagnostics│         │  Hover   │    │
│ │ Provider │      │ Provider │          │ Provider │    │
│ └──────────┘      └──────────┘          └──────────┘    │
│                          │                               │
│                     ┌────┴────┐                          │
│                     ▼         ▼                          │
│               ┌──────────┐ ┌──────────┐                 │
│               │ Symbols  │ │Definition│                 │
│               │ Provider │ │ Provider │                 │
│               └──────────┘ └──────────┘                 │
└──────────────────────────────────────────────────────────┘
```

### Provider Modules

| Provider | Lines | Function |
|----------|-------|----------|
| `server.py` | 258 | Core LSP server, handler registration |
| `completion_provider.py` | 254 | Context-aware auto-complete |
| `diagnostics_provider.py` | 148 | Syntax validation via SyntaxChecker |
| `hover_provider.py` | 307 | Documentation on hover |
| `symbols_provider.py` | 208 | Document outline, go-to-definition |
| `document_state.py` | 135 | Thread-safe document storage |

### LSP Features

- **textDocument/completion**: Syntax, attributes, xrefs, includes
- **textDocument/publishDiagnostics**: Real-time error highlighting
- **textDocument/hover**: AsciiDoc element documentation
- **textDocument/documentSymbol**: Heading hierarchy, anchors
- **textDocument/definition**: Cross-reference navigation

## GPU Rendering Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│  AsciiDoc   │───▶│  HTML + CSS  │───▶│ QWebEngineView│
│   Source    │    │   Content    │    │   (GPU)       │
└─────────────┘    └──────────────┘    └───────────────┘
                          │
                   ┌──────┴───────┐
                   ▼              ▼
            ┌──────────┐   ┌──────────┐
            │  NVIDIA  │   │   AMD    │
            │  (CUDA)  │   │  (ROCm)  │
            └──────────┘   └──────────┘
                   │              │
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │   Fallback   │
                   │ QTextBrowser │
                   │    (CPU)     │
                   └──────────────┘
```

**Detection Cache:** `~/.cache/asciidoc_artisan/gpu_detection.json` (24hr TTL)

## Manager Pattern (UI)

MainWindow delegates to specialized managers:

```
┌─────────────────────────────────────────────────────────┐
│                      MainWindow                          │
│                    (1,798 lines)                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ MenuManager │  │ThemeManager │  │StatusManager│     │
│  │  (actions)  │  │  (styling)  │  │ (status bar)│     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ FileManager │  │ GitManager  │  │ExportManager│     │
│  │  (file I/O) │  │  (version)  │  │ (formats)   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ ChatManager │  │SpellManager │  │SyntaxManager│     │
│  │  (AI chat)  │  │ (spelling)  │  │ (validation)│     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### Document Edit Flow

```
User Input → QPlainTextEdit → textChanged signal
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  Debounce Timer │
                           │    (300ms)      │
                           └────────┬────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │ PreviewWorker│        │ SyntaxChecker│        │  SpellChecker│
    │   (HTML)     │        │  (Errors)    │        │  (Squiggles) │
    └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
           │                       │                       │
           ▼                       ▼                       ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │ PreviewPanel │        │  Error List  │        │   Underlines │
    │   (Render)   │        │  (Highlight) │        │   (Visual)   │
    └──────────────┘        └──────────────┘        └──────────────┘
```

### Git Operation Flow

```
User Action → GitManager → Reentrancy Check
                                │
                    ┌───────────┴───────────┐
                    │     If Not Busy       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      GitWorker        │
                    │    (Background)       │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │   subprocess.run()    │
                    │   (shell=False)       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    result_ready       │
                    │      Signal           │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    UI Update          │
                    │   (Main Thread)       │
                    └───────────────────────┘
```

## Security Model

### Subprocess Execution

```python
# CORRECT: List form prevents shell injection
subprocess.run(["git", "commit", "-m", user_message], shell=False)

# WRONG: Shell form is vulnerable
subprocess.run(f"git commit -m '{user_message}'", shell=True)  # NEVER
```

### File Operations

```python
# CORRECT: Atomic write via temp file
from asciidoc_artisan.core import atomic_save_text
atomic_save_text(path, content)

# WRONG: Direct write can corrupt on crash
with open(path, 'w') as f:  # AVOID
    f.write(content)
```

### Credential Storage

```python
# CORRECT: OS keyring
from asciidoc_artisan.core import SecureCredentials
creds = SecureCredentials()
creds.store_api_key("claude", key)

# WRONG: Plain text storage
config["api_key"] = key  # NEVER
```

## Performance Characteristics

| Operation | Target | Implementation |
|-----------|--------|----------------|
| Preview render | <100ms | Incremental block cache |
| Syntax check | <100ms | Rule-based validation |
| Auto-complete | <50ms | Pre-built completion lists |
| File open | <500ms | Async file loading |
| Startup | <600ms | Lazy imports, deferred init |
| GPU detect | <100ms | 24hr cache |

## Extension Points

### Adding a New Worker

1. Create `workers/new_worker.py`:
```python
class NewWorker(QThread):
    result_ready = Signal(NewResult)

    def run(self) -> None:
        # Process in background
        self.result_ready.emit(result)
```

2. Add to `workers/__init__.py`
3. Connect in `MainWindow.__init__`

### Adding an LSP Feature

1. Create provider in `lsp/new_provider.py`
2. Register handler in `lsp/server.py`
3. Add tests in `tests/unit/lsp/test_new_provider.py`

### Adding a UI Manager

1. Create `ui/new_manager.py`
2. Initialize in `MainWindow.__init__`
3. Delegate actions from MainWindow

## Testing Strategy

```
tests/
├── unit/           # Module-level tests
│   ├── core/       # Business logic
│   ├── ui/         # Widget tests (with qtbot)
│   ├── workers/    # Worker tests
│   └── lsp/        # LSP provider tests
│
├── integration/    # Cross-module tests
│
└── e2e/            # End-to-end BDD scenarios
    └── step_defs/  # Gherkin step definitions
```

**Coverage Targets:**
- Core modules: 99-100%
- Qt workers: 93-98% (threading limitations)
- LSP providers: 98-100%
- Overall: >96%

---

*AsciiDoc Artisan v2.0.9 — MA Principle Architecture*
