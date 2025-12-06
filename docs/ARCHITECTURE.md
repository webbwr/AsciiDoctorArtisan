# AsciiDoc Artisan Architecture

**v2.1.0** | **Dec 5, 2025** | **Public Release**

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Source files | 180 |
| Source lines | 46,457 |
| Unit tests | 5,628 |
| E2E tests | 17 |
| Integration tests | 17 |
| Test coverage | 95% |
| Type coverage | 100% (mypy --strict) |
| Startup time | 0.27s |
| Storage format | TOON (30-60% smaller than JSON) |

---

## Design Principles

**MA Principle (間)** — Each module does one thing. Target: <400 lines per file.

**Handler Pattern** — UI logic lives in focused handler classes. MainWindow delegates.

**Thread Safety** — Slow operations run in QThread workers. UI updates via signals.

**Atomic Writes** — File saves use temp+rename. No partial writes on crash.

---

## Package Structure

```
src/asciidoc_artisan/
├── core/        13,085 lines   Business logic, no Qt UI
├── ui/          22,794 lines   Qt widgets and handlers
├── workers/      5,915 lines   QThread background workers
├── lsp/          2,134 lines   Language Server Protocol
├── claude/         658 lines   Claude AI integration
└── templates/                  Built-in document templates
```

### Component Diagram

```mermaid
graph TB
    subgraph "UI Layer (22,794 lines)"
        MW[MainWindow<br/>1,167 lines]
        ED[Editor]
        PV[Preview]
    end

    subgraph "Handler Layer"
        FH[FileHandler]
        GH[GitHandler]
        PH[PreviewHandler]
        CH[ChatManager]
    end

    subgraph "Worker Layer (5,915 lines)"
        GW[GitWorker]
        PW[PreviewWorker]
        OW[OllamaChatWorker]
        PD[PandocWorker]
    end

    subgraph "Core Layer (13,085 lines)"
        ST[Settings]
        FO[FileOperations]
        SC[SyntaxChecker]
        SE[SearchEngine]
    end

    subgraph "LSP Layer (2,134 lines)"
        LS[Server]
        CP[CompletionProvider]
        DP[DiagnosticsProvider]
    end

    MW --> FH & GH & PH & CH
    FH --> FO
    GH --> GW
    PH --> PW
    CH --> OW
    LS --> CP & DP
    CP & DP --> SC
```

---

## Core Package

Business logic. No Qt dependencies except models.

```
core/
├── settings.py           # App configuration
├── toon_utils.py         # TOON format serialization
├── file_operations.py    # Atomic file I/O (text, JSON, TOON)
├── search_engine.py      # Find & replace
├── spell_checker.py      # Spell validation
├── syntax_checker.py     # AsciiDoc validation
├── template_engine.py    # Template processing
├── gpu_detection.py      # Hardware detection
├── gpu_cache.py          # GPU cache (TOON format)
├── secure_credentials.py # OS keyring storage
│
├── *_models.py           # Pydantic data models
│   ├── git_models.py     # GitResult, GitStatus
│   ├── chat_models.py    # ChatMessage
│   ├── syntax_models.py  # SyntaxErrorModel, QuickFix
│   └── completion_models.py  # CompletionItem
│
└── *_rules.py            # Validation rules
    ├── syntax_error_rules.py
    ├── warning_rules.py
    └── info_rules.py
```

### Data Models

```mermaid
classDiagram
    class GitResult {
        +bool success
        +str stdout
        +str stderr
        +int exit_code
        +str user_message
    }

    class GitStatus {
        +str branch
        +int modified_count
        +int staged_count
        +int untracked_count
        +bool is_dirty
    }

    class ChatMessage {
        +str role
        +str content
        +float timestamp
        +str model
        +str context_mode
    }

    class SyntaxErrorModel {
        +str code
        +ErrorSeverity severity
        +str message
        +int line
        +int column
        +list~QuickFix~ fixes
    }

    class CompletionItem {
        +str text
        +CompletionKind kind
        +str detail
        +float score
    }
```

---

## UI Package

Qt widgets and handlers. MainWindow is the coordinator.

```
ui/
├── main_window.py        # App controller (1,167 lines)
│
├── *_handler.py          # Domain handlers
│   ├── file_handler.py       # File operations
│   ├── file_open_handler.py  # Open dialogs
│   ├── file_save_handler.py  # Save dialogs
│   ├── git_handler.py        # Git operations
│   ├── github_handler.py     # GitHub CLI
│   ├── preview_handler.py    # Preview coordination
│   ├── preview_handler_base.py  # Preview base class
│   ├── preview_handler_gpu.py   # GPU rendering
│   └── search_handler.py     # Find & replace
│
├── *_manager.py          # Feature managers
│   ├── chat_manager.py       # AI chat (441 lines)
│   ├── action_manager.py     # QAction factory
│   ├── worker_manager.py     # Worker lifecycle
│   └── syntax_checker_manager.py  # Validation UI
│
├── *_widget.py           # UI components
│   ├── chat_bar_widget.py    # Chat input
│   ├── chat_panel_widget.py  # Chat display
│   ├── find_bar_widget.py    # Search bar
│   └── quick_commit_widget.py # Git commit
│
└── *_dialog.py           # Dialog windows
```

### Handler Hierarchy

```mermaid
classDiagram
    class MainWindow {
        +QPlainTextEdit editor
        +PreviewHandler preview_handler
        +FileHandler file_handler
        +GitHandler git_handler
        +ChatManager chat_manager
    }

    class FileHandler {
        -Path current_file
        -bool is_modified
        +Signal file_opened
        +Signal file_saved
        +new_file()
        +open_file()
        +save_file()
    }

    class GitHandler {
        -GitWorker worker
        -bool is_processing
        +commit(message)
        +pull()
        +push()
    }

    class PreviewHandler {
        -PreviewWorker worker
        +update_preview(content)
    }

    class ChatManager {
        -OllamaChatWorker worker
        +send_message(text)
    }

    MainWindow --> FileHandler
    MainWindow --> GitHandler
    MainWindow --> PreviewHandler
    MainWindow --> ChatManager
```

---

## Workers Package

QThread workers for background operations.

```
workers/
├── base_worker.py         # Shared worker logic
├── git_worker.py          # Git commands
├── github_cli_worker.py   # GitHub CLI
├── pandoc_worker.py       # Format conversion
├── preview_worker.py      # AsciiDoc rendering
├── ollama_chat_worker.py  # AI chat
│
├── Rendering
│   ├── incremental_renderer.py    # Block caching
│   ├── parallel_block_renderer.py # Multi-core
│   ├── predictive_renderer.py     # Prefetch
│   ├── block_splitter.py          # Document parsing
│   └── render_cache.py            # LRU cache
│
└── Helpers
    ├── git_command_executor.py
    ├── git_status_parser.py
    ├── git_error_handler.py
    └── pandoc_executor.py
```

### Worker Class Hierarchy

```mermaid
classDiagram
    class QThread {
        <<PySide6>>
        +start()
        +quit()
    }

    class BaseWorker {
        -bool _cancelled
        +cancel()
        +reset_cancellation()
        #_check_cancellation()
        #_execute_subprocess(cmd)
    }

    class GitWorker {
        +Signal command_complete
        +Signal status_ready
        +commit(message)
        +pull()
        +push()
    }

    class GitHubCLIWorker {
        +Signal github_result_ready
        +create_pr(title, body)
        +list_prs()
    }

    class PreviewWorker {
        +Signal render_complete
        +Signal render_error
        +render(content)
    }

    class OllamaChatWorker {
        +Signal chat_response_ready
        +Signal chat_response_chunk
        +send_message(msg)
    }

    QThread <|-- PreviewWorker
    QThread <|-- OllamaChatWorker
    BaseWorker <|-- GitWorker
    BaseWorker <|-- GitHubCLIWorker
```

---

## LSP Package

Language Server Protocol for editor integration.

```
lsp/
├── server.py              # LSP server core
├── document_state.py      # Thread-safe doc storage
├── completion_provider.py # Auto-complete
├── diagnostics_provider.py # Syntax errors
├── hover_provider.py      # Documentation
├── symbols_provider.py    # Document outline
├── code_action_provider.py # Quick fixes
├── folding_provider.py    # Code folding
├── formatting_provider.py # Document format
└── semantic_tokens_provider.py # Highlighting
```

### LSP Architecture

```mermaid
classDiagram
    class Server {
        +DocumentState documents
        +start()
        +shutdown()
    }

    class DocumentState {
        -dict documents
        -Lock lock
        +get(uri)
        +set(uri, content)
    }

    class CompletionProvider {
        +get_completions(doc, pos)
    }

    class DiagnosticsProvider {
        +get_diagnostics(doc)
    }

    class HoverProvider {
        +get_hover(doc, pos)
    }

    Server --> DocumentState
    Server --> CompletionProvider
    Server --> DiagnosticsProvider
    Server --> HoverProvider
```

---

## Threading Model

```mermaid
graph TB
    subgraph "Main Thread"
        MW[MainWindow]
        ED[Editor]
        PV[Preview]
        SIG[Signal/Slot Bus]
    end

    subgraph "Worker Threads"
        GW[GitWorker]
        PW[PreviewWorker]
        OW[OllamaWorker]
        PD[PandocWorker]
    end

    subgraph "Thread Pool"
        TP[ThreadPoolExecutor]
        W1[Block Renderer 1]
        W2[Block Renderer 2]
        WN[Block Renderer N]
    end

    MW & ED & PV --> SIG
    SIG -.->|Commands| GW & PW & OW & PD
    GW & PW & OW & PD -.->|Results| SIG
    PW --> TP
    TP --> W1 & W2 & WN
```

### Worker Pattern

```python
class Worker(QThread):
    result_ready = Signal(Result)

    def __init__(self):
        super().__init__()
        self._cancelled = False

    def run(self):
        while not self._cancelled:
            cmd = self._queue.get()
            if cmd is None:
                break
            result = self._process(cmd)
            self.result_ready.emit(result)

    def cancel(self):
        self._cancelled = True
```

### Reentrancy Guard

```python
def start_operation(self):
    if self._is_processing:
        return  # Already running
    self._is_processing = True
    try:
        self.worker.start()
    finally:
        self._is_processing = False
```

---

## Key Workflows

### Document Edit Flow

```mermaid
sequenceDiagram
    participant U as User
    participant E as Editor
    participant D as Debouncer
    participant PW as PreviewWorker
    participant SX as SyntaxChecker
    participant P as Preview

    U->>E: Type text
    E->>D: textChanged
    D->>D: Wait 300ms

    par Parallel
        D->>PW: Render
        PW->>P: HTML result
    and
        D->>SX: Validate
        SX->>E: Error marks
    end
```

### Git Commit Flow

```mermaid
sequenceDiagram
    participant U as User
    participant GH as GitHandler
    participant GW as GitWorker
    participant SP as subprocess

    U->>GH: Commit
    GH->>GH: Check busy
    alt Busy
        GH->>U: Ignore
    else Free
        GH->>GW: Queue command
        GW->>SP: git commit
        SP-->>GW: Result
        GW-->>GH: Signal
        GH->>U: Status update
    end
```

### Atomic File Save

```mermaid
sequenceDiagram
    participant FH as FileHandler
    participant FO as FileOperations
    participant FS as FileSystem

    FH->>FO: atomic_save_text(path, content)
    FO->>FS: Write temp file
    FO->>FO: Verify write
    FO->>FS: os.replace(temp, target)
    FO-->>FH: Success
```

### AI Chat Flow

```mermaid
sequenceDiagram
    participant U as User
    participant CM as ChatManager
    participant OW as OllamaWorker
    participant API as Ollama

    U->>CM: Send message
    CM->>OW: Queue request
    OW->>API: POST /api/chat

    loop Streaming
        API-->>OW: Chunk
        OW-->>CM: Signal
        CM->>CM: Append display
    end

    OW-->>CM: Complete
```

---

## State Machines

### Application State

```mermaid
stateDiagram-v2
    [*] --> Ready: Launch

    Ready --> Editing: Open file
    Editing --> Modified: Text change
    Modified --> Editing: Save
    Modified --> Confirm: Close

    Confirm --> Editing: Cancel
    Confirm --> Ready: Discard

    Editing --> Exporting: Export
    Exporting --> Editing: Done

    Ready --> [*]: Quit
    Editing --> [*]: Quit
```

### Git Operation State

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Check: Request
    Check --> Idle: Busy
    Check --> Run: Free

    Run --> Done: Success
    Run --> Fail: Error
    Run --> Cancel: User cancel

    Done --> Idle
    Fail --> Idle
    Cancel --> Idle
```

### Preview State

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Debounce: Text change
    Debounce --> Debounce: More input
    Debounce --> Render: Timeout

    Render --> Cache: Done
    Cache --> Display: Updated
    Display --> Idle

    Render --> Error: Failed
    Error --> Idle
```

---

## Security

### Subprocess Execution

```python
# CORRECT: List prevents injection
subprocess.run(["git", "commit", "-m", message], shell=False)

# WRONG: Shell is vulnerable
subprocess.run(f"git commit -m '{message}'", shell=True)  # NEVER
```

### Atomic Writes

```python
# CORRECT: Temp + rename
from asciidoc_artisan.core import atomic_save_text
atomic_save_text(path, content)

# WRONG: Direct write corrupts on crash
with open(path, 'w') as f:
    f.write(content)  # AVOID
```

### Credentials

```python
# CORRECT: OS keyring
from asciidoc_artisan.core import SecureCredentials
creds = SecureCredentials()
creds.store_api_key("claude", key)

# WRONG: Plain text
config["api_key"] = key  # NEVER
```

---

## Performance

| Operation | Target | Actual |
|-----------|--------|--------|
| Startup | <1.0s | 0.27s |
| Preview | <200ms | <100ms |
| Autocomplete | <50ms | 20-40ms |
| Syntax check | <100ms | <50ms |
| File open | <500ms | <200ms |

### Multi-Core Rendering

```mermaid
graph LR
    DOC[Document] --> SP[Splitter]
    SP --> W1[Worker 1]
    SP --> W2[Worker 2]
    SP --> WN[Worker N]
    W1 & W2 & WN --> MG[Merger]
    MG --> OUT[HTML]
```

- Thread-local AsciiDoc instances
- Block-based parallelization
- 2-4x speedup on multi-core
- Graceful single-core fallback

### GPU Rendering

```mermaid
flowchart LR
    SRC[AsciiDoc] --> HTML
    HTML --> GPU{GPU?}
    GPU -->|Yes| WEB[QWebEngineView]
    GPU -->|No| TXT[QTextBrowser]
```

Detection cached 7 days at `~/.config/AsciiDocArtisan/gpu_cache.toon`

---

## Extension Points

### Add a Worker

1. Create `workers/new_worker.py`
2. Define signals
3. Implement `run()`
4. Export in `workers/__init__.py`
5. Initialize in MainWindow
6. Connect signals

### Add an LSP Feature

1. Create `lsp/new_provider.py`
2. Implement provider method
3. Register handler in `server.py`
4. Add tests

### Add a Handler

1. Create `ui/new_handler.py`
2. Implement methods
3. Initialize in MainWindow
4. Delegate from UI

---

## FR Mapping

| Category | FRs | Location |
|----------|-----|----------|
| Editor | FR-001–005 | `ui/main_window.py` |
| Files | FR-006–014 | `core/file_operations.py`, `ui/file_handler.py` |
| Preview | FR-015–020 | `workers/preview_worker.py`, `ui/preview_handler*.py` |
| Export | FR-021–025 | `workers/pandoc_worker.py` |
| Git | FR-026–033 | `workers/git_worker.py`, `ui/git_handler.py` |
| GitHub | FR-034–038 | `workers/github_cli_worker.py` |
| AI | FR-039–044 | `workers/ollama_chat_worker.py`, `ui/chat_manager.py` |
| Search | FR-045–049 | `core/search_engine.py` |
| Spell | FR-050–054 | `core/spell_checker.py` |
| Autocomplete | FR-085–090 | `lsp/completion_provider.py` |
| Syntax | FR-091–099 | `core/syntax_checker.py`, `lsp/diagnostics_provider.py` |
| Templates | FR-100–107 | `core/template_engine.py` |
| LSP | FR-109 | `lsp/*.py` |

---

## Related Docs

- [SPECIFICATIONS.md](../SPECIFICATIONS.md) — 109 FRs with schemas
- [ROADMAP.md](../ROADMAP.md) — Version history

---

*v2.1.0 | 180 files | 46,457 lines | 95% coverage | TOON format | MA Principle*
