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
- **Python 3.11+**: Minimum version (3.12 recommended for best performance)

**Version:** 1.4.0 (Production Ready Beta)

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
- **Current**: Hardware-accelerated modular architecture with intelligent fallbacks

## What's New in v1.4.0

**Key Changes for Developers:**

1. **GPU/NPU Hardware Acceleration** ⚡
   - New files: `core/gpu_detection.py`, `ui/preview_handler_gpu.py`
   - Automatic GPU detection with 24-hour cache (100ms startup improvement)
   - QWebEngineView (GPU) vs QTextBrowser (fallback) automatic selection
   - Environment variables set in `main.py` before Qt init
   - 10-50x performance improvement with GPU, 70-90% less CPU usage

2. **Document Version Display** 📊
   - New feature in `status_manager.py`
   - Extracts version from AsciiDoc attributes, text labels, or titles
   - Real-time updates in status bar

3. **Memory Profiling** 🔍
   - New file: `core/memory_profiler.py`
   - Identifies memory hotspots and optimization opportunities

4. **Grammar System Removed** 🗑️
   - Removed 2,067 lines of code
   - Improves performance and reduces complexity
   - Users should use external grammar tools

**Breaking Changes:**
- None! v1.4.0 is fully backward compatible
- GPU acceleration is automatic and transparent
- Existing code continues to work without modification

**Testing Priority for v1.4.0:**
- Test GPU detection on different hardware (NVIDIA, AMD, Intel)
- Verify fallback to QTextBrowser when GPU unavailable
- Test in WSLg environment (should auto-detect and handle correctly)
- Verify document version extraction from various formats

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
   - SPECIFICATIONS.md - Functional requirements (FR-001 to FR-053)
   - Code in `src/asciidoc_artisan/ui/main_window.py` - Main UI controller

**System dependencies required:**
- Pandoc (`sudo apt install pandoc`)
- wkhtmltopdf (`sudo apt install wkhtmltopdf`)
- Git (optional, for version control features)

## Common Commands

### Daily Development Workflow

```bash
# Run the app
make run                    # or: python src/main.py

# Test your changes
make test                   # Run all 481+ tests with coverage
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
│   ├── main_window.py          # AsciiDocEditor (main window controller, 1614 lines in v1.4.1)
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
│   ├── pandoc_worker.py        # Document format conversion (Ollama + Pandoc)
│   ├── preview_worker.py       # AsciiDoc → HTML rendering
│   ├── incremental_renderer.py # Partial document rendering (block-based cache)
│   └── optimized_worker_pool.py # Worker thread pool management
├── conversion/                 # Format conversion utilities
├── git/                        # Git integration utilities
└── claude/                     # Claude AI integration (future)
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

safe_path = sanitize_path(user_input)  # FR-016: Prevent directory traversal
atomic_save_text(path, content)        # FR-015: Atomic write (no corruption)

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
1. Read `SPECIFICATIONS.md` (FR-001 to FR-053) for requirements
2. Make changes (follow patterns, respect reentrancy guards)
3. `make test` - Ensure 481+ tests pass
4. `make format` - Auto-format code
5. `make lint` - Check for issues
6. Update docs if changing public APIs

**Pre-commit hooks:** `.pre-commit-config.yaml` (black, isort, ruff)
```bash
pre-commit install        # Enable
pre-commit run --all-files  # Manual run
```

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
2. **PDF Reading:** `document_converter.py:283-365` - PyMuPDF (3-5x faster than pdfplumber)
3. **Incremental Render:** `workers/incremental_renderer.py` - Block cache with LRU (3-5x faster edits)
4. **String Processing:** `document_converter.py:_clean_cell()` - Called in tight loops

**Benchmark:** Use `scripts/benchmark_performance.py` to measure changes

### Ollama AI Integration (v1.2+)

**Location:** `workers/pandoc_worker.py`, `ui/dialogs.py`

Local AI for document conversion with automatic Pandoc fallback:
- Enable via Tools → AI Status → Settings
- Supports: `phi3:mini` (recommended), `llama2`, `mistral`, `codellama`
- Status bar shows active conversion method
- Settings: `ollama_enabled: bool`, `ollama_model: Optional[str]`

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
| `src/asciidoc_artisan/workers/pandoc_worker.py` | Document format conversion (Ollama + Pandoc) |
| `src/asciidoc_artisan/workers/preview_worker.py` | AsciiDoc → HTML rendering |
| `src/document_converter.py` | Document import/export (DOCX, PDF) |
| `requirements-production.txt` | Production dependencies |
| `requirements.txt` | Development dependencies (includes test/lint tools) |
| `pyproject.toml` | Package metadata, build config, tool settings |
| `Makefile` | Build automation (run, test, lint, format) |
| `SPECIFICATIONS.md` | Complete functional requirements (FR-001 to FR-053) |
| `RELEASE_NOTES_v1.4.0.md` | v1.4.0 release notes and changelog |
| `README.md` | User-facing documentation and installation guide |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `.ruff.toml` | Ruff linter configuration |

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

- **Style:** Black (88 char), isort, ruff - enforced by pre-commit hooks
- **Types:** Required for new code (mypy lenient)
- **Testing:** pytest + pytest-qt, 481+ tests, use `qtbot` for GUI tests
- **Docs:** Docstrings for public APIs, update SPECIFICATIONS.md for new features
- **Python:** 3.11+ (3.12 recommended)

## Dependencies

**System (required):** Pandoc, wkhtmltopdf
**System (optional):** Git (for version control features)

**Python (production):** PySide6 6.9.0+, asciidoc3 3.2.0+, pypandoc 1.13+, pymupdf 1.23.0+
**Python (dev):** pytest, pytest-qt, pytest-cov, black, ruff, mypy, pre-commit

Install: `pip install -r requirements.txt` (dev) or `requirements-production.txt` (prod)

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

## Additional Resources

- **SPECIFICATIONS.md** — Complete functional requirements (FR-001 to FR-053)
- **README.md** — User-facing installation and usage guide (Grade 5.0 reading level)
- **RELEASE_NOTES_v1.4.0.md** — v1.4.0 release notes and GPU acceleration details
- **ROADMAP_v1.5.0.md** — Future feature roadmap
- **DEEP_CODE_ANALYSIS_v1.4.0.md** — Codebase analysis and optimization opportunities

---

**Note on Copilot Instructions:**
The `.github/copilot-instructions.md` file is outdated. It references the old WSLg compatibility note about QTextBrowser. As of v1.4.0, GPU detection is automatic and the app uses QWebEngineView (GPU) or QTextBrowser (fallback) based on hardware availability. Refer to this file (CLAUDE.md) for current architecture.

---

*This file is for Claude Code (claude.ai/code). Last updated for v1.4.1: October 28, 2025*
