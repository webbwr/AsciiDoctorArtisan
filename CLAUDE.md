# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AsciiDoc Artisan** is a cross-platform desktop AsciiDoc editor with live preview built on PySide6 (Qt).

**Tech Stack:**
- **PySide6 6.9.0+**: Qt GUI framework with GPU-accelerated rendering
- **asciidoc3 3.2.0+**: AsciiDoc to HTML conversion
- **pypandoc 1.13+**: Multi-format document conversion (requires Pandoc system binary)
- **pymupdf 1.23.0+**: Fast PDF reading (3-5x faster than pdfplumber)
- **numba 0.58.0+**: Optional JIT compilation for performance-critical loops (10-50x speedup)
- **wkhtmltopdf**: System binary for PDF generation
- **Python 3.11+**: Minimum version (3.12 recommended for best performance)

**Version:** 1.1.0-beta

**Architecture:**
- Single-window Qt application with editor/preview split pane
- Multi-threaded: UI on main thread, Git/Pandoc/Preview on worker threads
- Event-driven with Qt signals/slots for thread communication
- Modular design: UI managers separated from business logic (v1.1 refactoring)

## Development Setup

### Quick Setup

**Automated installation scripts:**
```bash
# Linux/Mac
./install-asciidoc-artisan.sh

# Windows
.\Install-AsciiDocArtisan.ps1
```

These scripts install system dependencies (Pandoc, wkhtmltopdf), create a virtual environment, and install Python packages.

### Manual Setup

```bash
# Production dependencies only
pip install -r requirements-production.txt

# Full dev environment (includes pytest, ruff, mypy, black, pre-commit)
pip install -r requirements.txt
pip install -e ".[dev]"
pre-commit install
```

**System dependencies (required):**
- Pandoc (`sudo apt install pandoc` on Linux, `brew install pandoc` on Mac)
- wkhtmltopdf (`sudo apt install wkhtmltopdf` on Linux, `brew install wkhtmltopdf` on Mac)

## Common Commands

### Running the Application

```bash
make run              # Recommended
python src/main.py    # Direct execution
```

### Testing

```bash
make test                                    # Run all tests with coverage
pytest tests/ -v                             # Verbose output, all tests
pytest tests/test_file_operations.py -v     # Single test file
pytest tests/test_settings.py::test_settings_save_load -v  # Specific test
pytest tests/ --cov=src --cov-report=html   # HTML coverage report
```

**Current test coverage:** 28 test files, 371+ tests

### Code Quality & Formatting

```bash
make lint      # Run ruff, black --check, isort --check, mypy
make format    # Auto-format with black, isort, ruff --fix
make clean     # Remove build artifacts, __pycache__, .pytest_cache
```

**Linting tools:**
- **ruff**: Fast Python linter (replaces flake8, pylint for most checks)
- **black**: Code formatter (88 char line length)
- **isort**: Import sorting
- **mypy**: Type checking (lenient config, use for new code)

## Architecture

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
│   └── hardware_detection.py   # GPU/CPU capability detection
├── ui/                         # UI components (Qt widgets)
│   ├── main_window.py          # AsciiDocEditor (main window controller)
│   ├── menu_manager.py         # Menu bar creation and actions
│   ├── theme_manager.py        # Dark/light theme management
│   ├── status_manager.py       # Status bar, window title, message boxes
│   ├── file_handler.py         # File open/save/import dialogs
│   ├── export_manager.py       # Export to DOCX/PDF/HTML/MD
│   ├── preview_handler.py      # QWebEngineView preview (GPU-accelerated)
│   ├── git_handler.py          # Git UI operations
│   ├── action_manager.py       # QAction creation and management
│   ├── settings_manager.py     # Settings UI and persistence
│   ├── line_number_area.py     # Editor with line numbers
│   ├── editor_state.py         # Editor state tracking
│   └── dialogs.py              # Custom dialogs (preferences, etc.)
├── workers/                    # QThread worker classes
│   ├── git_worker.py           # Git operations (pull, commit, push)
│   ├── pandoc_worker.py        # Document format conversion
│   ├── preview_worker.py       # AsciiDoc → HTML rendering
│   ├── incremental_renderer.py # Partial document rendering (Numba-optimized)
│   └── optimized_worker_pool.py # Worker thread pool management
├── conversion/                 # Format conversion utilities
├── git/                        # Git integration utilities
└── claude/                     # Claude AI integration (future)
```

**Key entry point:** `src/main.py` (launches QApplication and AsciiDocEditor)

### Threading Model

The application uses Qt's threading model with QThread workers for long-running operations:

**Worker Threads:**
- **GitWorker** (`workers/git_worker.py`): Executes Git commands via subprocess
  - Operations: pull, commit, push
  - Communicates via `request_git_command` signal → `git_result_ready` signal
- **PandocWorker** (`workers/pandoc_worker.py`): Document format conversion
  - Formats: AsciiDoc ↔ Markdown ↔ DOCX ↔ HTML ↔ PDF
  - Uses pypandoc wrapper around Pandoc system binary
  - Falls back gracefully if Pandoc unavailable
- **PreviewWorker** (`workers/preview_worker.py`): AsciiDoc → HTML rendering
  - Uses asciidoc3 library
  - Triggered by editor text changes with adaptive debouncing

**Thread Communication Pattern:**
```python
# Main thread emits request signal
self.request_git_command.emit(["git", "status"], repo_path)

# Worker processes in background thread
class GitWorker(QThread):
    git_result_ready = Signal(GitResult)

    def run(self):
        result = self.run_git_command(...)
        self.git_result_ready.emit(result)

# Main thread receives result via slot
@Slot(GitResult)
def _handle_git_result(self, result: GitResult):
    # Update UI based on result
```

**Reentrancy Guards (Critical):**
These flags prevent concurrent operations from corrupting state:
- `_is_processing_git`: Prevents multiple simultaneous Git operations
- `_is_processing_pandoc`: Prevents multiple simultaneous Pandoc conversions
- `_is_opening_file`: Prevents reentrancy during file load operations

**Always check these flags before starting async operations!**

### Security Best Practices

**Path Sanitization (FR-016):**
```python
from asciidoc_artisan.core import sanitize_path

# Always sanitize user-provided paths
safe_path = sanitize_path(user_input)
```

**Atomic File Writes (FR-015):**
```python
from asciidoc_artisan.core import atomic_save_text

# Prevents partial writes and data loss
atomic_save_text(filepath, content)  # Writes to temp, then atomic rename
```

**Subprocess Security:**
- **Always use list form** for subprocess calls (prevents shell injection)
- **Good:** `subprocess.run(["git", "commit", "-m", message])`
- **Bad:** `subprocess.run(f"git commit -m {message}", shell=True)`  # NEVER DO THIS

**Git Command Pattern:**
```python
# GitWorker uses this pattern - follow it for all subprocess calls
cmd = ["git", operation, *args]
result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path)
```

### Settings Persistence

Settings are stored as JSON in platform-specific locations via `QStandardPaths.AppDataLocation`:

- **Linux:** `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows:** `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **macOS:** `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

**Implementation:**
- Managed by `Settings` class (`core/settings.py`)
- Auto-saved on application exit
- Includes: window geometry, theme, font, recent files, Git preferences
- Uses atomic writes via `atomic_save_text()` to prevent corruption

## Development Workflow

### Making Changes

1. **Read specifications:** `SPECIFICATIONS.md` contains all functional requirements (FR-001 to FR-053)
2. **Make changes:** Follow existing patterns, respect reentrancy guards
3. **Run tests:** `make test` (ensure all 371+ tests pass)
4. **Lint:** `make lint` (fix any ruff/black/isort issues)
5. **Format:** `make format` (auto-fix formatting)
6. **Update docs:** If changing public APIs or behavior

### Pre-commit Hooks

This project uses pre-commit hooks (`.pre-commit-config.yaml`):
```bash
pre-commit install        # Enable hooks
pre-commit run --all-files  # Manual run
```

Hooks run: black, isort, ruff, trailing whitespace checks

### Change Risk Assessment

**High-risk areas (require careful testing):**
- **Threading:** Worker initialization/shutdown in `main_window.py`
- **Subprocess:** Git commands in `git_worker.py`
- **Format conversion:** Pandoc calls in `pandoc_worker.py`
- **Settings I/O:** Load/save in `settings.py`
- **Performance hot paths:** GPU settings (`preview_handler.py`), PyMuPDF (`document_converter.py`), Numba JIT functions
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

### Performance Optimizations (v1.1)

The application includes several performance-critical code paths:

**1. GPU-Accelerated Preview (2-5x speedup)**
- **Location:** `ui/preview_handler.py:61-79`, `ui/main_window.py:457-467`
- **Tech:** QWebEngineView with `Accelerated2dCanvas` and `WebGL` enabled
- **Fallback:** Automatically falls back to CPU rendering if GPU unavailable
- **Detection:** `hardware_detection.py` checks GPU capability at startup

**2. PyMuPDF PDF Reading (3-5x speedup)**
- **Location:** `src/document_converter.py:283-365`
- **Tech:** Uses `fitz.open()` (PyMuPDF) instead of pdfplumber
- **Benefits:** Faster parsing, lower memory usage, GPU acceleration where supported

**3. Numba JIT Compilation (10-50x speedup)**
- **Table cell processing:** `src/document_converter.py:387-426` (`_clean_cell()`)
- **Text splitting:** `workers/incremental_renderer.py:173-202` (`count_leading_equals()`)
- **Requirements:** Numba must be installed and function must be Numba-compatible
- **Fallback:** Pure Python implementation if Numba unavailable
- **Note:** Called in tight loops (every table cell, every line)

**When modifying hot paths:**
1. Profile before/after changes
2. Test with Numba installed and uninstalled
3. Verify GPU fallback still works
4. Check logs show correct optimization status
5. Run benchmark scripts: `benchmark_performance.py`, `benchmark_numba.py`

## Important Files Reference

| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point (launches QApplication) |
| `src/asciidoc_artisan/ui/main_window.py` | Main window controller (AsciiDocEditor class) |
| `src/asciidoc_artisan/core/settings.py` | Settings persistence and management |
| `src/asciidoc_artisan/core/file_operations.py` | Atomic file I/O and path sanitization |
| `src/asciidoc_artisan/workers/git_worker.py` | Git subprocess operations |
| `src/asciidoc_artisan/workers/pandoc_worker.py` | Document format conversion |
| `src/asciidoc_artisan/workers/preview_worker.py` | AsciiDoc → HTML rendering |
| `src/document_converter.py` | Document import/export (DOCX, PDF) |
| `requirements-production.txt` | Production dependencies |
| `requirements.txt` | Development dependencies (includes test/lint tools) |
| `pyproject.toml` | Package metadata, build config, tool settings |
| `Makefile` | Build automation (run, test, lint, format) |
| `SPECIFICATIONS.md` | Complete functional requirements (FR-001 to FR-053) |
| `README.md` | User-facing documentation and installation guide |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `.ruff.toml` | Ruff linter configuration |

## Coding Standards

### Style Guide
- **Line length:** 88 characters (Black formatter enforces this)
- **Type hints:** Required for new code (mypy checking enabled but lenient)
- **Docstrings:** All public functions, classes, and modules
- **Imports:** Sorted with isort (black-compatible profile)
- **Python version:** Minimum 3.11, recommended 3.12

### Testing Requirements
- **Framework:** pytest + pytest-qt (for Qt GUI testing)
- **Coverage target:** 100% (currently 28 test files, 371+ tests)
- **Test all:**
  - New features (per SPECIFICATIONS.md requirements)
  - Security-critical code (path sanitization, atomic writes, subprocess calls)
  - Edge cases (large files, missing dependencies, Git errors)
- **GUI testing:** Use `pytest-qt` fixtures (`qtbot`) for widget interactions

### Documentation Standards
- **User docs:** README.md (Grade 5.0 reading level)
- **Specs:** SPECIFICATIONS.md (FR-XXX functional requirements)
- **Code docs:** Docstrings for all public APIs
- **This file:** Update when architecture changes

## Dependencies

### System Requirements (External Binaries)

**Required:**
- **Pandoc** (document conversion engine)
  - Linux: `sudo apt install pandoc`
  - macOS: `brew install pandoc`
  - Windows: Download from pandoc.org
  - Verify: `pandoc --version`

- **wkhtmltopdf** (HTML → PDF conversion)
  - Linux: `sudo apt install wkhtmltopdf`
  - macOS: `brew install wkhtmltopdf`
  - Windows: Download from wkhtmltopdf.org
  - Verify: `wkhtmltopdf --version`

**Optional:**
- **Git** (version control integration)
  - Must be in PATH for Git features to work
  - Verify: `git --version`
  - Application gracefully disables Git features if unavailable

### Python Dependencies

**Production (`requirements-production.txt`):**
- PySide6 6.9.0+ (Qt6 bindings)
- asciidoc3 3.2.0+ (AsciiDoc processor)
- pypandoc 1.13+ (Pandoc Python wrapper)
- pymupdf 1.23.0+ (fast PDF parsing)
- keyring 24.0.0+ (secure credential storage)
- psutil 5.9.0+ (system resource monitoring)

**Development (`requirements.txt`):**
- All production deps plus:
- pytest 7.0.0+ (testing framework)
- pytest-qt 4.0.0+ (Qt testing)
- pytest-cov 4.0.0+ (coverage reporting)
- black 23.0.0+ (code formatter)
- ruff 0.1.0+ (linter)
- mypy 1.0.0+ (type checker)
- pre-commit 3.0.0+ (Git hooks)

## Troubleshooting

### Common Development Issues

**Import errors: `ModuleNotFoundError: No module named 'pypandoc'`**
```bash
pip install -r requirements.txt  # Install all dependencies
```

**Runtime error: "Pandoc not found"**
- Pandoc system binary not installed or not in PATH
- Solution: Install Pandoc (see Dependencies section)
- Verify: `pandoc --version`

**PDF export fails**
- wkhtmltopdf system binary not installed or not in PATH
- Solution: Install wkhtmltopdf (see Dependencies section)
- Verify: `wkhtmltopdf --version`

**Git operations fail / Git menu disabled**
- Not in a Git repository or Git not installed
- Verify: `git status` (should not error)
- Note: Application gracefully disables Git features if unavailable

**Tests fail with Qt errors**
```bash
# Install Qt test dependencies
pip install pytest-qt

# Run with verbose output to see Qt errors
pytest tests/ -v -s
```

**Pre-commit hooks fail**
```bash
pre-commit run --all-files  # See what's failing
make format                  # Auto-fix formatting issues
```

### Debugging Tips

- **Verbose logging:** Set `logging.basicConfig(level=logging.DEBUG)` in `main.py`
- **Qt debug:** Run with `QT_LOGGING_RULES="*.debug=true"`
- **Profile performance:** Use `benchmark_performance.py` or `benchmark_numba.py`
- **Memory profiling:** Use `memory_profile.py`

## Additional Resources

- **README.md** — User-facing installation and usage guide
- **SPECIFICATIONS.md** — Complete functional requirements (FR-001 to FR-053)
- **DOCUMENTATION.md** — Additional developer documentation
- **.github/copilot-instructions.md** — Notes for AI coding assistants
- **GitHub Issues** — Bug reports and feature requests

---

*This file is for Claude Code (claude.ai/code). Last updated: October 2025*
