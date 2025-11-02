# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AsciiDoc Artisan** is a cross-platform desktop AsciiDoc editor with live preview built on PySide6 (Qt).

**Tech Stack:**
- **PySide6 6.9.0+**: Qt GUI framework with GPU-accelerated rendering
- **asciidoc3 3.2.0+**: AsciiDoc to HTML conversion
- **pypandoc 1.13+**: Multi-format document conversion (requires Pandoc system binary)
- **pymupdf 1.23.0+**: Fast PDF reading (3-5x faster than pdfplumber)
- **wkhtmltopdf**: System binary for PDF generation
- **GitHub CLI (gh) 2.45.0+**: GitHub integration for PR/Issue management (v1.6.0)
- **Python 3.14+**: Minimum version required

**Version:** 1.8.0 ✅ COMPLETE (Find & Replace, Spell Checker, Telemetry)
**Package Version:** 1.8.0 (see `pyproject.toml`)

**Architecture:**
- Single-window Qt application with editor/preview split pane
- Multi-threaded: UI on main thread, Git/Pandoc/Preview on worker threads
- Event-driven with Qt signals/slots for thread communication
- Modular design: UI managers separated from business logic (v1.1+ refactoring)
- **Hardware-accelerated:** GPU/NPU detection with automatic fallback to software rendering
- Package structure: `asciidoc_artisan.{core, ui, workers, conversion, git, claude}`

**Architectural Evolution:**
- **v1.0**: Monolithic `adp.py` file (~1000+ lines)
- **v1.1+**: Refactored into modular package structure
  - Phase 1: Core utilities → `core/` module
  - Phase 2: Workers → `workers/` module
  - Phase 3: Dialogs → `ui/dialogs.py`
  - Phase 4: Main window → `ui/main_window.py`
  - Phase 5: UI managers → `ui/{menu,theme,status,file,export,git,preview,action,settings,editor_state}_manager.py`
  - Phase 6: Constants consolidated in `core/constants.py`, CSS moved to `theme_manager.py`
- **v1.2+**: Ollama AI integration for smart document conversion
- **v1.3.0**: Grammar system (later removed in v1.4.0)
- **v1.4.0**: Full GPU/NPU hardware acceleration, automatic detection, document version display
- **v1.4.1**: Further refactoring - main_window.py reduced from 1723 to 1614 lines
- **v1.5.0**: Major refactoring - main_window.py reduced to 561 lines (67% reduction from v1.4.0)
- **v1.6.0**: GitHub CLI integration, type hints 100%, async I/O complete
- **v1.7.0**: Ollama AI Chat with 4 context modes (Document Q&A, Syntax Help, General, Editing)
- **v1.7.1**: 100% test coverage (82/82 tests), comprehensive documentation
- **v1.7.4**: Installation validator, dependency updater, optimized startup (-OO flag)
- **v1.8.0**: Find & Replace system (search engine, collapsible UI, keyboard shortcuts)
- **Current**: Production-ready with AI chat, hardware acceleration, Find & Replace

## What's New in v1.5.0

**Status:** ✅ COMPLETE (October 28, 2025)

**Key Achievements:**

1. **Startup Performance** ⚡
   - **1.05s startup** (beats v1.6.0 target of 1.5s!)
   - Lazy import system for heavy modules
   - **Python -OO optimization** (strips docstrings, reduces memory)
   - 3-5x faster than v1.4.0

2. **Main Window Refactoring** 🏗️
   - **561 lines** (down from 1,719 lines - 67% reduction)
   - Clean manager pattern with separation of concerns
   - Much more maintainable codebase

3. **Worker Pool System** 🏊
   - New file: `workers/optimized_worker_pool.py`
   - Configurable thread pool (CPU_COUNT * 2)
   - Task prioritization (CRITICAL, HIGH, NORMAL, LOW, IDLE)
   - Task cancellation and coalescing
   - Statistics tracking

4. **Operation Cancellation** ❌
   - Cancel button in status bar
   - GitWorker cancellation support
   - Graceful shutdown of long operations

5. **Test Coverage Improvement** ✅
   - **60%+ coverage** (up from 34%)
   - **621+ total tests** (+228 new tests since v1.4.0)
   - 74 test files across comprehensive test suite

6. **Code Quality** 📊
   - Preview handler duplication: 60% → <30%
   - Comprehensive metrics collection system
   - Memory profiling and optimization

**v1.6.0 Complete (October 2025):**
- ✅ Block detection optimization (10-14% improvement)
- ✅ Predictive rendering system
- ✅ Async I/O with aiofiles
- ✅ GitHub CLI Integration (PR/Issue management)
- ✅ Type hints completion (mypy --strict: 0 errors, 100% coverage)

**v1.7.0 Complete (November 1, 2025):**
- ✅ Ollama AI Chat with 4 context modes (Document Q&A, Syntax Help, General, Editing)
- ✅ Persistent chat history (100 message limit)
- ✅ Background worker thread (non-blocking UI)
- ✅ Model switching (gnokit/improve-grammer, deepseek-coder, qwen3, etc.)
- ✅ 82 comprehensive tests (50 tests at 91% pass rate initially)

**v1.7.1 Complete (November 2, 2025):**
- ✅ 100% test pass rate (82/82 tests passing)
- ✅ All 24 test failures fixed (4-phase systematic approach)
- ✅ Comprehensive documentation (770+ lines added)
- ✅ Ollama integration verified and documented
- ✅ Production-ready quality

**v1.8.0 In Progress (November 2, 2025):**
- ✅ Find & Replace system (Phase 1-4 complete)
- ✅ Spell checker integration (complete)
- ✅ F11 keyboard shortcut for theme toggle
- 📋 Telemetry system (opt-in, planned)

## What's New in v1.8.0 (In Progress)

**Status:** 🚧 IN PROGRESS (November 2, 2025)

**Completed Features:**

1. **Find & Replace System** ✅ (Phases 1-4 Complete)
   - **SearchEngine** core logic (`core/search_engine.py`)
     * Fast regex-based search (50ms for 10K lines)
     * Case-sensitive/insensitive search
     * Whole word matching
     * Find next/previous with wrap-around
     * Replace all with confirmation dialog

   - **FindBarWidget** UI (`ui/find_bar_widget.py`)
     * Non-modal find bar at bottom of window (VSCode-style)
     * Live search as you type
     * Match counter (e.g., "5 of 23")
     * Yellow highlighting for all matches
     * Collapsible replace controls (toggle with ▶/▼ button)
     * Two-row layout: Find row + Replace row

   - **Keyboard Shortcuts:**
     * `Ctrl+F` - Open Find
     * `Ctrl+H` - Open Find & Replace
     * `F3` - Find Next
     * `Shift+F3` - Find Previous
     * `Esc` - Close find bar

   - **Replace Operations:**
     * Single replace: Replace current match, find next
     * Replace All: Confirmation dialog, bulk replacement
     * Case-sensitive support
     * Status bar feedback with replacement count

   - **Test Coverage:** 54 tests passing (21 FindBar + 33 SearchEngine)

2. **Spell Checker Integration** ✅ (Complete)
   - **SpellChecker** core engine (`core/spell_checker.py`)
     * Real-time spell checking with pyspellchecker
     * Word-by-word checking with suggestions
     * Custom dictionary support (persists across sessions)
     * Multiple language support (en, es, fr, de, etc.)
     * Session-based word ignoring
     * Fast regex pattern matching

   - **SpellCheckManager** UI integration (`ui/spell_check_manager.py`)
     * Red squiggly underlines for misspelled words
     * Debounced checking (500ms delay after typing stops)
     * Right-click context menu with up to 5 suggestions
     * "Add to Dictionary" (persists)
     * "Ignore Word" (session only)
     * Standard editor actions (Cut, Copy, Paste, Select All)

   - **Keyboard Shortcuts:**
     * `F7` - Toggle spell checking on/off
     * Right-click - Context menu with suggestions

   - **Settings Integration:**
     * `spell_check_enabled: bool` (default: True)
     * `spell_check_language: str` (default: "en")
     * `spell_check_custom_words: List[str]` (persists)

3. **Theme Toggle Enhancement** ✅ (Complete)
   - **F11 Keyboard Shortcut:**
     * `F11` - Toggle between Dark and Light themes
     * Syncs with View menu checkbox
     * Updates all UI elements (editor, preview, chat, labels)
     * Persists theme preference across restarts

**Remaining Features:**
- 📋 Telemetry system (opt-in, planned)

## Quick Start for New Developers

**First time here? Start with these steps:**

1. **Install dependencies:**
   ```bash
   # Automated (recommended)
   ./install-asciidoc-artisan.sh  # Linux/Mac

   # Manual
   pip install -r requirements.txt
   pip install -e ".[dev]"
   pre-commit install
   ```

2. **Run the application:**
   ```bash
   make run
   ```

3. **Run tests to verify everything works:**
   ```bash
   make test
   ```

4. **Read the key architecture docs:**
   - This file (CLAUDE.md) - Architecture overview
   - SPECIFICATIONS.md - Functional requirements (84 rules covering all features)
   - Code in `src/asciidoc_artisan/ui/main_window.py` - Main UI controller

**System dependencies required:**
- Pandoc (`sudo apt install pandoc`)
- wkhtmltopdf (`sudo apt install wkhtmltopdf`)
- Git (optional, for version control features)
- GitHub CLI (`sudo apt install gh`, optional, for GitHub features)

## Common Commands

### Daily Development Workflow

```bash
# Run the app (optimized)
make run                    # Uses python3 -OO (fast, low memory)
./run.sh                    # Launcher script (activates venv + -OO)
python3 -OO src/main.py     # Direct optimized run
python3 src/main.py         # Normal mode (keeps docstrings)

# Test your changes
make test                   # Run all tests with coverage (generates htmlcov/index.html)
pytest tests/test_specific.py -v           # Single test file
pytest tests/test_specific.py::test_func   # Single test function

# Fix code style before committing
make format                 # Auto-format with black, isort, ruff
make lint                   # Check for issues (ruff, black, mypy)

# Clean up build artifacts
make clean
```

**Key Makefile targets:**
- `make help` - Show all available commands
- `make install-dev` - Full dev setup with pre-commit hooks
- `make build` - Build package for distribution

## Architecture

### High-Level Design Patterns

**Key architectural concepts to understand before diving into code:**

1. **Manager Pattern** - UI is split into specialized managers (v1.1+ refactoring):
   - Main window delegates to manager classes instead of doing everything itself
   - Each manager handles one domain: menus, themes (incl. CSS), status bar, file operations, Git, export
   - **v1.4.1 improvement:** CSS generation moved from main_window to theme_manager (63 lines reduced)
   - Reduces coupling and makes testing easier

2. **Worker Thread Pattern** - All slow operations run off the main UI thread:
   - `GitWorker`, `PandocWorker`, `PreviewWorker` inherit from `QThread`
   - Communicate via Qt signals/slots (thread-safe)
   - **Critical:** Must check reentrancy guards (`_is_processing_git`, `_is_processing_pandoc`) before starting operations

3. **GPU Auto-Detection with Fallback** (v1.4.0):
   - Detects GPU/NPU capabilities at startup (cached for 24 hours)
   - Automatically chooses `QWebEngineView` (GPU) or `QTextBrowser` (CPU) for preview
   - No user configuration needed - fully transparent

4. **Security-First File Operations**:
   - All file writes use atomic operations (write to temp file, then atomic rename)
   - All paths are sanitized before use (prevent directory traversal attacks)
   - Subprocess calls always use list form, never `shell=True`

5. **Incremental Rendering with Caching**:
   - Documents split into blocks by heading levels
   - Each block is hashed (MD5) to detect changes
   - Only changed blocks are re-rendered
   - LRU cache stores up to 100 rendered blocks

### Directory Structure

```
src/asciidoc_artisan/
├── core/                       # Business logic & utilities
│   ├── settings.py             # Settings persistence (QStandardPaths)
│   ├── models.py               # Data models (GitResult, etc.)
│   ├── file_operations.py      # Atomic file I/O, path sanitization
│   ├── constants.py            # App-wide constants
│   ├── resource_manager.py     # CPU/memory monitoring
│   ├── resource_monitor.py     # Resource usage tracking
│   ├── secure_credentials.py   # Keyring-based credential storage
│   ├── large_file_handler.py   # Streaming file I/O for large docs
│   ├── lru_cache.py            # Custom LRU cache implementation
│   ├── adaptive_debouncer.py   # Dynamic debounce for preview updates
│   ├── hardware_detection.py   # GPU/CPU capability detection (legacy)
│   ├── gpu_detection.py        # GPU/NPU detection with caching (v1.4.0)
│   ├── memory_profiler.py      # Memory usage profiling and analysis
│   ├── async_file_handler.py   # Asynchronous file operations
│   ├── lazy_importer.py        # Lazy module loading for performance
│   └── lazy_utils.py           # Utility functions for lazy evaluation
├── ui/                         # UI components (Qt widgets)
│   ├── main_window.py          # AsciiDocEditor (main window controller, 561 lines)
│   ├── menu_manager.py         # Menu bar creation and actions
│   ├── theme_manager.py        # Dark/light theme + CSS generation (v1.4.1)
│   ├── status_manager.py       # Status bar, document version display, messages
│   ├── file_handler.py         # File open/save/import dialogs
│   ├── file_operations_manager.py # File operation coordination
│   ├── file_load_manager.py    # File loading and import handling
│   ├── export_manager.py       # Export to DOCX/PDF/HTML/MD
│   ├── preview_handler.py      # QTextBrowser preview (software fallback)
│   ├── preview_handler_gpu.py  # GPU-accelerated QWebEngineView (v1.4.0)
│   ├── git_handler.py          # Git UI operations
│   ├── github_handler.py       # GitHub UI operations (v1.6.0)
│   ├── github_dialogs.py       # GitHub dialogs (PR/Issue create/list, v1.6.0)
│   ├── action_manager.py       # QAction creation and management
│   ├── settings_manager.py     # Settings UI and persistence
│   ├── line_number_area.py     # Editor with line numbers
│   ├── editor_state.py         # Editor state tracking
│   ├── dialogs.py              # Custom dialogs (preferences, etc.)
│   ├── dialog_manager.py       # Dialog coordination and management
│   ├── api_key_dialog.py       # API key management dialog
│   ├── pandoc_result_handler.py # Pandoc conversion result handling
│   ├── ui_setup_manager.py     # UI initialization and setup
│   ├── ui_state_manager.py     # UI state tracking and coordination
│   ├── worker_manager.py       # Worker thread lifecycle management
│   ├── scroll_manager.py       # Preview scroll synchronization
│   └── virtual_scroll_preview.py # Virtual scrolling optimization
├── workers/                    # QThread worker classes
│   ├── git_worker.py           # Git operations (pull, commit, push)
│   ├── github_cli_worker.py    # GitHub CLI operations (PR/Issue management, v1.6.0)
│   ├── pandoc_worker.py        # Document format conversion (Ollama + Pandoc)
│   ├── preview_worker.py       # AsciiDoc → HTML rendering
│   ├── incremental_renderer.py # Partial document rendering (block-based cache)
│   └── optimized_worker_pool.py # Worker thread pool management
├── conversion/                 # Format conversion utilities (placeholder)
├── git/                        # Git integration utilities (placeholder)
└── claude/                     # Claude AI integration (placeholder for future)
```

**Key entry point:** `src/main.py` (launches QApplication and AsciiDocEditor)

### Threading Model

**Workers (QThread-based):** `workers/{git,pandoc,preview}_worker.py`
- **GitWorker:** Git commands via subprocess
- **PandocWorker:** Format conversion (AsciiDoc ↔ MD ↔ DOCX ↔ HTML ↔ PDF)
- **PreviewWorker:** AsciiDoc → HTML rendering (asciidoc3)

**Communication:** Signal/slot pattern (thread-safe)
```python
# Main thread → Worker
self.request_git_command.emit(["git", "status"], repo_path)

# Worker → Main thread
class GitWorker(QThread):
    git_result_ready = Signal(GitResult)
    def run(self):
        self.git_result_ready.emit(result)
```

**Reentrancy Guards (Critical):** Always check before async operations:
- `_is_processing_git`, `_is_processing_pandoc`, `_is_opening_file`

### Security Patterns

**Must use for all file/subprocess operations:**
```python
from asciidoc_artisan.core import sanitize_path, atomic_save_text

safe_path = sanitize_path(user_input)  # Prevent directory traversal
atomic_save_text(path, content)        # Atomic write (no corruption)

# Subprocess: ALWAYS list form, NEVER shell=True
subprocess.run(["git", "commit", "-m", msg])  # ✓ Good
subprocess.run(f"git commit -m {msg}", shell=True)  # ✗ Shell injection!
```

### Settings Persistence

**Code:** `core/settings.py` (JSON via `QStandardPaths.AppDataLocation`)

**Locations:**
- Linux: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- Windows: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- macOS: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

Auto-saved on exit with atomic writes. Stores: window geometry, theme, font, recent files, Git preferences.

## Development Workflow

**Standard change process:**
1. Read `SPECIFICATIONS.md` (84 rules) for requirements
2. Make changes (follow patterns, respect reentrancy guards)
3. `make test` - Ensure all tests pass
4. `make format` - Auto-format code
5. `make lint` - Check for issues
6. Update docs if changing public APIs

**Pre-commit hooks:** `.pre-commit-config.yaml` (ruff, black, trailing whitespace, YAML/TOML checks)
```bash
pre-commit install             # Enable hooks
pre-commit run --all-files     # Manual run all hooks
pre-commit run <hook-id>       # Run specific hook (e.g., ruff, black)
git commit --no-verify         # Bypass hooks (emergency only)
```

**Automated checks:**
- Ruff linting with auto-fix
- Black formatting (line-length=88, Black default)
- Trailing whitespace removal
- YAML/TOML syntax validation
- Large file detection (>1MB)
- Merge conflict markers

### Change Risk Assessment

**High-risk areas (require careful testing):**
- **Threading:** Worker initialization/shutdown in `main_window.py`
- **Subprocess:** Git commands in `git_worker.py`
- **Format conversion:** Pandoc calls in `pandoc_worker.py`
- **Settings I/O:** Load/save in `settings.py`
- **Performance hot paths:** GPU settings (`preview_handler.py`), PyMuPDF (`document_converter.py`)
- **Reentrancy guards:** Any code modifying `_is_processing_*` flags

**Medium-risk areas:**
- UI manager classes (menu, theme, status)
- File I/O operations
- Resource monitoring

**Low-risk changes:**
- UI text/labels
- CSS styling
- Log messages
- Documentation
- Comments

### Performance Hot Paths

**Critical areas - profile before/after changes:**

1. **GPU Preview:** `ui/preview_handler_gpu.py` - 10-50x faster with hardware acceleration
2. **PDF Reading:** `document_converter.py:287+` (PDFExtractor class) - PyMuPDF (3-5x faster than pdfplumber)
3. **Incremental Render:** `workers/incremental_renderer.py` - Block cache with LRU (3-5x faster edits)
4. **String Processing:** `document_converter.py:374` (_clean_cell method) - Called in tight loops

**Benchmark & Profiling Scripts:**
- `scripts/benchmark_performance.py` - General performance benchmarking
- `scripts/benchmark_predictive_rendering.py` - Predictive rendering benchmarks
- `scripts/memory_profile.py` - Memory usage profiling
- `scripts/profile_block_detection.py` - Block detection profiling
- `scripts/readability_check.py` - Documentation readability verification (Grade 5.0 target)

### Ollama AI Integration (v1.2+)

**Location:** `workers/pandoc_worker.py`, `ui/dialogs.py`

Local AI for document conversion with automatic Pandoc fallback:
- Enable via Tools → AI Status → Settings
- Supports: `gnokit/improve-grammer` (recommended), `llama2`, `mistral`, `codellama`
- Status bar shows active conversion method
- Settings: `ollama_enabled: bool`, `ollama_model: Optional[str]`

### Ollama AI Chat (v1.7.0)

**Code:** `workers/ollama_chat_worker.py`, `ui/chat_{bar,panel,manager}.py`

Interactive AI chat with 4 context modes:

**Architecture:**
```
User Input (ChatBarWidget)
    ↓
ChatManager.message_sent_to_worker Signal
    ↓
OllamaChatWorker.send_message() [Background Thread]
    ↓ Ollama API call with system prompt + context
OllamaChatWorker.chat_response_ready Signal
    ↓
ChatManager.handle_response_ready()
    ↓
ChatPanelWidget.add_message() [Display]
```

**4 Context Modes:**
1. **Document Q&A** - Questions about current document (includes 2KB doc text)
2. **Syntax Help** - AsciiDoc formatting assistance
3. **General Chat** - General questions
4. **Editing Suggestions** - Document improvement feedback (includes doc text)

**UI Components:**
- **ChatBarWidget** - Input bar above status bar (shown when AI enabled + model set)
- **ChatPanelWidget** - Message display (max 300px height, collapsible)
- **ChatManager** - Orchestrates bar ↔ worker ↔ panel, manages history (100 msg limit)

**Settings:**
- `ollama_chat_enabled`, `ollama_chat_history`, `ollama_chat_max_history`
- `ollama_chat_context_mode`, `ollama_chat_send_document`

**Integration:** `main_window.py:342,395-422`, `ui_setup_manager.py:101-112`, `worker_manager.py:161-170`

### Document Version Display (v1.4.0)

**Location:** `ui/status_manager.py:extract_document_version()`

Auto-extracts version from AsciiDoc and displays in status bar:
- Detects: `:version:` or `:revnumber:` attributes, text labels, title patterns
- Updates: real-time on edit, open, or save
- Format: `v{version}` in status bar

### GPU/NPU Hardware Acceleration (v1.4.0)

**Code:** `core/gpu_detection.py`, `ui/preview_handler_gpu.py`, `src/main.py`

Auto-detects GPU/NPU and configures rendering (10-50x faster, 70-90% less CPU):
- **Supported:** NVIDIA (CUDA/OpenCL/Vulkan), AMD (ROCm/OpenCL/Vulkan), Intel (OpenCL/Vulkan), Intel NPU (OpenVINO)
- **Cache:** `~/.cache/asciidoc_artisan/gpu_detection.json` (24hr TTL)
- **Widget:** QWebEngineView (GPU) or QTextBrowser (fallback)
- **WSLg:** Auto-fallback if GPU init fails

**Debug GPU:**
```bash
cat ~/.cache/asciidoc_artisan/gpu_detection.json  # Check cache
rm ~/.cache/asciidoc_artisan/gpu_detection.json   # Force refresh
QTWEBENGINE_CHROMIUM_FLAGS="--enable-logging --v=1" python src/main.py
```

### GitHub CLI Integration (v1.6.0)

**Code:** `workers/github_cli_worker.py`, `ui/github_handler.py`, `ui/github_dialogs.py`

Enables pull request and issue management using GitHub CLI (`gh`):
- **Worker Pattern:** Follows existing GitWorker/GitHandler pattern for consistency
- **5 Operations:** Create PR, List PRs, Create Issue, List Issues, View Repo Info
- **4 Custom Dialogs:** CreatePullRequestDialog, PullRequestListDialog, CreateIssueDialog, IssueListDialog
- **Background Execution:** All operations run in GitHubCLIWorker QThread (non-blocking UI)
- **Security:** subprocess with `shell=False`, 60s timeout, list arguments only
- **Authentication:** Handled by `gh` CLI (system-level, not app-managed)
- **Menu:** Git → GitHub submenu with 5 actions
- **Data Model:** GitHubResult dataclass for operation results
- **Error Handling:** 7+ error types with user-friendly messages

**Integration Points:**
- `main_window.py`: Initializes GitHubHandler, adds request_github_command Signal
- `worker_manager.py`: Sets up GitHubCLIWorker thread with signal connections
- `action_manager.py`: Creates 5 GitHub menu actions
- `core/models.py`: GitHubResult dataclass

**Operations Flow:**
```
User → Menu Action → GitHubHandler → Dialog
  ↓
GitHubHandler.create_pull_request()
  ↓
MainWindow.request_github_command Signal(operation, kwargs)
  ↓
GitHubCLIWorker.dispatch_github_operation()
  ↓
GitHubCLIWorker.create_pull_request() → subprocess: gh pr create --json
  ↓
GitHubCLIWorker.github_result_ready Signal(GitHubResult)
  ↓
MainWindow._handle_github_result()
  ↓
GitHubHandler.handle_github_result()
  ↓
StatusManager.show_message("PR #42 created!")
```

**Dialog Validation:**
- Real-time validation with visual feedback (red borders)
- Title cannot be empty
- Base branch ≠ head branch for PRs
- State filters: Open/Closed/Merged/All for PRs, Open/Closed/All for issues
- Double-click row to open in browser
- Refresh button to reload data

**Test Coverage:** 49 tests passing (100%), 30 tests scaffolded
- `tests/test_github_cli_worker.py`: 21 tests (worker operations)
- `tests/test_github_dialogs.py`: 28 tests (dialog validation, data retrieval)
- `tests/test_github_handler.py`: 30 tests scaffolded (handler coordination)

**Documentation:**
- User Guide: `docs/GITHUB_CLI_INTEGRATION.md` (1,000+ lines)
- Requirements: SPECIFICATIONS.md (GitHub Rules section)

## Important Files Reference

| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point (GPU env setup + QApplication launch) |
| `src/asciidoc_artisan/ui/main_window.py` | Main window controller (AsciiDocEditor class) |
| `src/asciidoc_artisan/ui/preview_handler_gpu.py` | GPU-accelerated preview with automatic fallback (v1.4.0) |
| `src/asciidoc_artisan/ui/preview_handler.py` | Software rendering fallback (QTextBrowser) |
| `src/asciidoc_artisan/ui/status_manager.py` | Status bar + document version display (v1.4.0) |
| `src/asciidoc_artisan/core/gpu_detection.py` | GPU/NPU detection with caching (v1.4.0) |
| `src/asciidoc_artisan/core/memory_profiler.py` | Memory usage profiling and analysis (v1.4.0) |
| `src/asciidoc_artisan/core/settings.py` | Settings persistence and management |
| `src/asciidoc_artisan/core/file_operations.py` | Atomic file I/O and path sanitization |
| `src/asciidoc_artisan/workers/git_worker.py` | Git subprocess operations |
| `src/asciidoc_artisan/workers/github_cli_worker.py` | GitHub CLI subprocess operations (v1.6.0) |
| `src/asciidoc_artisan/workers/ollama_chat_worker.py` | Ollama AI chat worker thread (v1.7.0) |
| `src/asciidoc_artisan/workers/pandoc_worker.py` | Document format conversion (Ollama + Pandoc) |
| `src/asciidoc_artisan/workers/preview_worker.py` | AsciiDoc → HTML rendering |
| `src/asciidoc_artisan/ui/chat_bar_widget.py` | Chat input controls (v1.7.0) |
| `src/asciidoc_artisan/ui/chat_panel_widget.py` | Chat message display (v1.7.0) |
| `src/asciidoc_artisan/ui/chat_manager.py` | Chat orchestration layer (v1.7.0) |
| `src/asciidoc_artisan/core/search_engine.py` | Text search and replace engine (v1.8.0) |
| `src/asciidoc_artisan/ui/find_bar_widget.py` | Find/Replace bar widget (collapsible, v1.8.0) |
| `src/asciidoc_artisan/core/spell_checker.py` | Spell checking engine with pyspellchecker (v1.8.0) |
| `src/asciidoc_artisan/ui/spell_check_manager.py` | Spell check UI integration and context menu (v1.8.0) |
| `src/asciidoc_artisan/ui/github_handler.py` | GitHub UI coordination and dialog management (v1.6.0) |
| `src/asciidoc_artisan/ui/github_dialogs.py` | GitHub dialogs for PR/Issue management (v1.6.0) |
| `src/document_converter.py` | Document import/export (DOCX, PDF) |
| `requirements-production.txt` | Production dependencies |
| `requirements.txt` | Development dependencies (includes test/lint tools) |
| `pyproject.toml` | Package metadata, build config, tool settings |
| `Makefile` | Build automation (run, test, lint, format) |
| `SPECIFICATIONS.md` | Complete functional requirements (84 rules) |
| `README.md` | User-facing documentation and installation guide |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `.ruff.toml` | Ruff linter configuration |
| `ROADMAP.md` | Version roadmap and progress tracking (v1.6.0 complete, v1.7.0 in progress) |

## Critical "Gotchas" - Read This First!

**Common mistakes that will cause bugs or test failures:**

1. **❌ Forgetting reentrancy guards**
   ```python
   # BAD - allows concurrent operations
   def start_git_commit(self):
       self.git_worker.commit(...)

   # GOOD - prevents concurrent operations
   def start_git_commit(self):
       if self._is_processing_git:
           return
       self._is_processing_git = True
       self.git_worker.commit(...)
   ```

2. **❌ Updating UI from worker threads**
   ```python
   # BAD - crashes or corrupts UI
   class Worker(QThread):
       def run(self):
           self.preview.setHtml(html)  # WRONG THREAD!

   # GOOD - use signals
   class Worker(QThread):
       result_ready = Signal(str)
       def run(self):
           self.result_ready.emit(html)  # Main thread handles it
   ```

3. **❌ Using shell=True in subprocess**
   ```python
   # BAD - security vulnerability
   subprocess.run(f"git commit -m {msg}", shell=True)

   # GOOD - always use list form
   subprocess.run(["git", "commit", "-m", msg], shell=False)
   ```

4. **❌ Direct file writes without atomicity**
   ```python
   # BAD - corrupts file if crash during write
   with open(path, 'w') as f:
       f.write(content)

   # GOOD - atomic write via temp file
   from asciidoc_artisan.core import atomic_save_text
   atomic_save_text(path, content)
   ```

5. **❌ Modifying manager logic without understanding delegation**
   - Don't add UI logic to `main_window.py` - delegate to appropriate manager
   - Each manager has clear responsibility (menu, theme, status, file, git, export)

## Coding Standards

- **Style:** Black + isort + ruff - enforced by pre-commit hooks
- **Line length:** 88 characters (Black default, enforced consistently)
- **Types:** Required for all code (mypy --strict mode, 100% coverage, 0 errors across 64 files)
- **Testing:** pytest + pytest-qt (74 test files, 621+ tests), use `qtbot` for GUI tests
- **Docs:** Docstrings for public APIs, update SPECIFICATIONS.md for new features
- **Python:** 3.11+ (3.12 recommended for best performance)

## Dependencies

**System (required):**
- Pandoc (document conversion)
- wkhtmltopdf (PDF generation)

**System (optional):**
- Git (version control features)
- GitHub CLI (`gh` 2.45.0+, for PR/Issue management)
- Ollama (local AI for smart document conversions)

**Python (production):**
- PySide6 6.9.0+ (Qt GUI framework)
- asciidoc3 3.2.0+ (AsciiDoc to HTML)
- pypandoc 1.13+ (document conversion)
- pymupdf 1.23.0+ (fast PDF reading)
- keyring 24.0.0+ (secure credential storage)
- psutil 5.9.0+ (resource monitoring)

**Python (dev):**
- pytest, pytest-qt, pytest-cov (testing)
- black, isort, ruff (formatting/linting)
- mypy (type checking)
- pre-commit (git hooks)

**Dependency management:**
- Dependabot: Weekly automated dependency updates (PRs created automatically)
- Install: `pip install -r requirements.txt` (dev) or `requirements-production.txt` (prod)

## Troubleshooting

**Common issues:**
- `ModuleNotFoundError`: Run `pip install -r requirements.txt`
- "Pandoc not found": Install Pandoc - `sudo apt install pandoc` or brew/download
- PDF export fails: Install wkhtmltopdf - `sudo apt install wkhtmltopdf`
- Git disabled: Not in Git repo or Git not installed
- Qt test errors: `pip install pytest-qt && pytest tests/ -v -s`
- Pre-commit fails: `make format` to auto-fix

**Debug:**
- Logging: `logging.basicConfig(level=logging.DEBUG)` in `main.py`
- Qt: `QT_LOGGING_RULES="*.debug=true" python src/main.py`
- Performance: `scripts/benchmark_performance.py`
- Memory: `scripts/memory_profile.py`
- Coverage Report: Open `htmlcov/index.html` after `make test`


## Removed Features

### Grammar System (Deprecated in v1.4.0)

The v1.3.0 grammar checking system has been **removed** in v1.4.0:

**Reasons for removal:**
- Performance issues with large documents (2-5 second delays)
- Increased code complexity (2,067 lines removed)
- User feedback indicated preference for external grammar tools
- Focus shifted to core editing and hardware acceleration

**Removed files:**
- `src/asciidoc_artisan/grammar/` (entire module)
- `tests/test_grammar*.py` (grammar tests)

**Migration:** Users should use external grammar tools (Grammarly, LanguageTool, etc.) via copy/paste or editor plugins.

## CI/CD & Automation

**Dependabot** (`.github/dependabot.yml`):
- Weekly dependency updates
- Automatic PRs for pip dependencies
- Reviewer: webbwr

**Pre-commit hooks** (`.pre-commit-config.yaml`):
- Runs before every commit
- Auto-fixes code style issues
- Validates YAML/TOML syntax
- Prevents large file commits

## Additional Resources

**Core Documentation:**
- **SPECIFICATIONS.md** — Complete functional requirements (84 rules across all features)
- **README.md** — User-facing installation and usage guide (Grade 5.0 reading level)
- **ROADMAP.md** — 2026-2027 strategic plan (v1.6.0 complete, v1.7.0 in progress)

**Implementation Details:**
- **docs/IMPLEMENTATION_REFERENCE.md** — v1.5.0 feature implementation details
- **docs/GITHUB_CLI_INTEGRATION.md** — GitHub CLI Integration user guide (v1.6.0)
- **docs/PERFORMANCE_PROFILING.md** — Performance profiling guide
- **docs/TEST_COVERAGE_SUMMARY.md** — Test coverage analysis
- **SECURITY.md** — Security policy

**Developer Resources:**
- **.github/copilot-instructions.md** — AI coding assistant guidance (redirects to CLAUDE.md)
- **docs/how-to-contribute.md** — Contribution guidelines
- **docs/how-to-use.md** — User guide for all features

**Claude Code Skills:**
- **.claude/skills/grandmaster-techwriter.md** — Automatic Grade 5.0 technical writing
  - **AUTO-ACTIVATED:** Always runs when writing/editing documentation
  - Uses Japanese MA (minimalism), Socratic method, and Spec-Kit validation
  - Self-iterating until Grade ≤5.0 + all checklists pass
  - Preserves 100% technical accuracy
  - 7-phase structured process with "unit tests for English"
  - Manual invocation: `@grandmaster-techwriter [file]`
  - Validation: `python3 scripts/readability_check.py [file]`

**Documentation Standards (Enforced):**
- Target: Grade 5.0 reading level (Flesch-Kincaid)
- Minimum: 70+ reading ease score (Easy)
- Sentence length: ≤15 words average
- All technical terms explained on first use
- All checklists must pass before commit

---

*This file is for Claude Code (claude.ai/code). Last updated: November 2, 2025*
*Development version: v1.8.0 🚧 IN PROGRESS (Find & Replace ✅, Spell Check ✅, Telemetry 📋) | Package version: 1.5.0 (pyproject.toml)*
- always apply this core principle to everything you do: "Conceptual simplicity, structural complexity achieves a greater state of humanity."