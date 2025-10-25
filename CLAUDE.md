# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AsciiDoc Artisan** is a modern PySide6 desktop application for editing AsciiDoc files with live HTML preview. It provides document conversion (via Pandoc), Git integration, and cross-platform support for Windows, Linux, and macOS.

**Core Technology Stack:**
- **UI Framework:** PySide6 (Qt for Python) 6.9.0+
- **AsciiDoc Processing:** asciidoc3 10.2.1+
- **Document Conversion:** pypandoc 1.13+ with Pandoc system binary
- **Python:** 3.11+ (3.12 recommended)

**Current Version:** 1.1.0 (per specification v1.1.0)
- Modular architecture with comprehensive test coverage (71/71 tests)
- All functional requirements (FR-001 to FR-062) implemented
- Security features: atomic file saves (FR-015), path sanitization (FR-016)
- Full type hints (NFR-016) and comprehensive documentation (NFR-017)

## Development Commands

### Installation

**Automated Installation (Recommended):**
```bash
# Mac/Linux - Full automated install with validation
./install-asciidoc-artisan.sh

# Windows 11 - Full automated install with validation (PowerShell 7)
.\Install-AsciiDocArtisan.ps1
```

The installation scripts will:
- Validate Python 3.11+ installation
- Check and install system dependencies (Pandoc, Git)
- Create optional virtual environment
- Install all Python dependencies
- Run post-install tasks
- Validate the complete installation

**Manual Setup:**
```bash
# Install production dependencies
make install
# or: pip install -r requirements-production.txt

# Install development dependencies (includes linters, test tools)
make install-dev
# or: pip install -r requirements.txt && pip install -e ".[dev]" && pre-commit install
```

### Running the Application
```bash
make run
# or: python adp_windows.py
# or: python3 adp_windows.py  (on Linux/macOS)
```

### Testing
```bash
# Run all tests with coverage
make test
# or: pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_file_operations.py -v

# Run specific test function
pytest tests/test_settings.py::test_settings_save_load -v
```

### Linting & Formatting
```bash
# Run all linters (does not modify files)
make lint
# or: ruff check . && black --check . && isort --check-only . && mypy .

# Auto-format code
make format
# or: black . && isort . && ruff check --fix .

# Individual tools
ruff check .              # Fast Python linter
black .                   # Code formatter
isort .                   # Import sorter
mypy .                    # Type checker (warnings only, does not block)
```

### Build & Distribution
```bash
# Build package
make build
# or: python -m build

# Clean build artifacts
make clean
```

## Architecture Overview

### Modular Package Architecture
The application has been refactored from a single-file design into a well-structured Python package (`asciidoc_artisan/`) with clear separation of concerns. The legacy `adp_windows.py` remains as the main entry point for backwards compatibility.

**Package Structure:**
```
asciidoc_artisan/
├── core/           # Core functionality and models
│   ├── constants.py      # App constants and configuration
│   ├── models.py         # Data models (Settings, GitResult)
│   ├── settings.py       # Settings persistence
│   └── file_operations.py # Secure file I/O (atomic saves, path sanitization)
├── workers/        # Background QThread workers
│   ├── git_worker.py     # Git operations
│   ├── pandoc_worker.py  # Document conversion
│   └── preview_worker.py # AsciiDoc rendering
├── ui/            # User interface components
│   ├── main_window.py    # AsciiDocEditor (QMainWindow)
│   └── dialogs.py        # Import/Export/Preferences dialogs
├── git/           # Git integration utilities
├── conversion/    # Document conversion utilities
└── claude/        # Optional AI integration
```

**Main Components:**
1. **`AsciiDocEditor` (QMainWindow)** - Main application class in `ui/main_window.py`
   - UI setup and layout
   - Coordinates workers via signals/slots
   - File operations delegated to `core/file_operations.py`

2. **Worker Threads** - Background processing in `workers/`
   - `GitWorker` - Git operations (commit, pull, push)
   - `PandocWorker` - Document format conversion (with optional AI)
   - `PreviewWorker` - AsciiDoc to HTML rendering

3. **Core Models & Settings** - in `core/`
   - `Settings` - Application settings dataclass
   - `GitResult` - Git operation results
   - `atomic_save_text/json` - Secure file writing (FR-015)
   - `sanitize_path` - Path traversal prevention (FR-016)

4. **Legacy Entry Point:**
   - `adp_windows.py` - Main entry point (imports from `asciidoc_artisan`)
   - `pandoc_integration.py` - Enhanced Pandoc wrapper (being phased out)
   - `claude_client.py` - AI integration (being phased out)

### Threading Model & State Management

**Critical State Flags (respect these when adding operations):**
- `_is_processing_git` - Prevents concurrent Git operations
- `_is_processing_pandoc` - Prevents concurrent Pandoc operations
- `_is_opening_file` - Prevents preview updates during file load
- `_is_syncing_scroll` - Prevents scroll recursion

**Thread Communication Pattern:**
```python
# In ui/main_window.py - Request work from UI thread
self.request_git_command.emit(["git", "commit", "-m", msg], repo_path)

# In workers/git_worker.py - Worker processes in background
class GitWorker(QObject):
    @Slot(list, Path)
    def run_git_command(self, args, working_dir):
        result = subprocess.run(args, cwd=working_dir, ...)
        self.command_complete.emit(result.stdout, result.returncode)

# In ui/main_window.py - UI thread receives results
@Slot(str, int)
def _on_git_command_complete(self, output, return_code):
    self._is_processing_git = False
    # Update UI
```

### Settings Persistence
Settings are stored as JSON in platform-appropriate locations:
- **Linux/WSL:** `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows:** `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **macOS:** `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

Uses `QStandardPaths.AppDataLocation` for cross-platform path resolution.

### Preview System
- **Live preview:** 350ms debounced QTimer triggers HTML regeneration
- **Rendering:** asciidoc3 API converts AsciiDoc → HTML
- **Fallback:** If asciidoc3 unavailable, shows plain text with line numbers
- **Synchronized scrolling:** Editor scroll position maps to preview viewport

### Document Conversion Pipeline
1. **DOCX → AsciiDoc:** Pandoc via `pypandoc` with TOC directives prepended
2. **PDF → AsciiDoc:** Direct extraction via `pdfplumber` with table formatting
3. **Clipboard HTML → AsciiDoc:** Direct Pandoc conversion from clipboard
4. **Export formats:** HTML, DOCX, Markdown, LaTeX, RST, PDF (all via Pandoc)

## Code Conventions & Patterns

### Type Hints & Mypy
- Type hints required for public methods
- Mypy runs in permissive mode (warnings only, see `pyproject.toml`)
- PySide6 type stubs have limitations - use `# type: ignore[call-overload]` for QAction constructors

### Error Handling
```python
# Always log errors AND show user-friendly messages
try:
    result = subprocess.run(git_cmd, capture_output=True, check=True)
except subprocess.CalledProcessError as e:
    logger.error(f"Git command failed: {e.stderr}")
    QMessageBox.critical(self, "Git Error", "Failed to commit. Ensure file is in a Git repository.")
```

### Git Command Safety
- Use list arguments (not shell strings) for `subprocess.run()`
- Always specify `cwd` parameter for repository operations
- Validate repository existence before Git operations
- Never use `shell=True` unless absolutely necessary

### UI State Updates
```python
# Disable buttons during processing
self.git_commit_act.setEnabled(False)
# ... perform operation ...
self.git_commit_act.setEnabled(True)
```

## Important Files

| File/Directory | Purpose |
|----------------|---------|
| `adp_windows.py` | Legacy main entry point (imports from `asciidoc_artisan`) |
| `asciidoc_artisan/` | Main application package (modular architecture) |
| `asciidoc_artisan/ui/main_window.py` | Main application window and UI logic |
| `asciidoc_artisan/core/` | Core models, settings, and secure file operations |
| `asciidoc_artisan/workers/` | Background thread workers (Git, Pandoc, Preview) |
| `pandoc_integration.py` | Legacy Pandoc wrapper (being phased out) |
| `claude_client.py` | Legacy AI integration (being phased out) |
| `pyproject.toml` | Build config, tool settings (black, ruff, mypy, pytest) |
| `Makefile` | Development commands |
| `.pre-commit-config.yaml` | Pre-commit hooks (black, ruff, mypy) |
| `requirements.txt` | Flexible dependencies for development |
| `requirements-production.txt` | Pinned versions for production |

## Platform-Specific Notes

### Windows
- Uses `adp_windows.py` as main entry point
- PowerShell script `scripts/AsciiDocArtisanVerify.ps1` for setup verification
- Pandoc must be in PATH (common issue - check with `where pandoc`)

### Linux/WSL
- Setup script: `./setup.sh`
- Verification: `./verify.sh`
- Install Pandoc: `sudo apt install pandoc`

### macOS
- Install Pandoc: `brew install pandoc`
- Same Python commands as Linux

## Testing Strategy

Current test coverage is **comprehensive** (71/71 tests passing, 100% coverage per specification v1.1.0).

**Test Organization:**
- `tests/` - All test files follow `test_*.py` naming convention
- Tests cover: core models, settings, file operations, workers, UI components
- Uses `pytest` with `pytest-qt` for Qt testing

**When adding tests:**
- Use `pytest` with `pytest-qt` for Qt testing
- Mock file I/O and subprocess calls
- Avoid launching full GUI in tests (use QApplication fixture sparingly)
- Target 80%+ coverage for new features
- Run tests with: `make test` or `pytest tests/ -v --cov`

## High-Risk Areas

### Before modifying these, review carefully:

1. **Thread lifecycle management** (`ui/main_window.py`: `closeEvent`, worker startup/shutdown)
   - Workers must be properly cleaned up on exit
   - Signals must be disconnected before thread termination

2. **Git subprocess invocation** (`workers/git_worker.py`)
   - Security-sensitive: always validate paths and use list arguments
   - Cross-platform: test on Windows AND Linux

3. **Pandoc integration** (`workers/pandoc_worker.py`)
   - Environment-sensitive: Pandoc must be in PATH
   - Error handling is critical for user experience

4. **Settings JSON handling** (`core/settings.py`, `core/file_operations.py`)
   - Uses atomic saves (`atomic_save_json`) to prevent corruption
   - Malformed JSON must not crash application
   - Path handling differs per platform

5. **State flags** (`ui/main_window.py`: `_is_processing_*`)
   - Race conditions possible if not respected
   - Always reset flags in error handlers

6. **File security** (`core/file_operations.py`)
   - `sanitize_path` prevents path traversal attacks (FR-016)
   - `atomic_save_text/json` ensures data integrity (FR-015)
   - Never bypass these security functions

## Low-Risk Changes

Safe to modify without extensive testing:
- CSS/styling in preview HTML
- Menu text, keyboard shortcuts
- Status bar messages
- README/documentation updates
- Adding logging statements (prefer `logging` module over `print()`)

## External Dependencies

### Required System Binaries
- **Pandoc:** Document conversion - must be in PATH
- **Git:** Version control features - optional but recommended

### Verifying Dependencies
```bash
# Check Python packages
python -c "import PySide6, asciidoc3, pypandoc; print('All OK')"

# Check system binaries
pandoc --version
git --version
```

## Linter Configuration

### Ruff (Primary Linter)
- Line length: 88 characters
- Checks: pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade
- Ignores: E501 (line length, handled by black), C901 (complexity)

### Black (Formatter)
- Line length: 88 characters
- Target: Python 3.11, 3.12
- Style: Default black style

### Mypy (Type Checker)
- Permissive mode (warnings only)
- `ignore_missing_imports = true`
- Special overrides for `adp_windows` module (disables some PySide6-related errors)

### Pre-commit Hooks
Installed via `pre-commit install`. Runs on every commit:
- Trailing whitespace removal
- YAML validation
- Black formatting
- Ruff linting
- Mypy type checking (non-blocking)

## Common Development Workflows

### Adding a New Menu Action
```python
# In ui/main_window.py

# 1. Create QAction in _create_actions()
self.my_action = QAction("&My Feature", self,
    shortcut=QKeySequence("Ctrl+M"),
    statusTip="Description",
    triggered=self.my_feature_handler)

# 2. Add to menu in appropriate method
self.my_menu.addAction(self.my_action)

# 3. Implement handler
def my_feature_handler(self):
    # Disable button during processing
    self.my_action.setEnabled(False)
    try:
        # Do work
        pass
    finally:
        self.my_action.setEnabled(True)
```

### Adding a Worker Thread
```python
# 1. Create worker class in asciidoc_artisan/workers/my_worker.py
from PySide6.QtCore import QObject, Signal, Slot

class MyWorker(QObject):
    result_ready = Signal(str)

    @Slot(str)
    def do_work(self, input_data):
        result = process(input_data)
        self.result_ready.emit(result)

# 2. In ui/main_window.py __init__()
from asciidoc_artisan.workers import MyWorker

self.worker_thread = QThread()
self.worker = MyWorker()
self.worker.moveToThread(self.worker_thread)
self.request_work.connect(self.worker.do_work)
self.worker.result_ready.connect(self.handle_result)
self.worker_thread.start()

# 3. Clean up in closeEvent()
self.worker_thread.quit()
self.worker_thread.wait()

# 4. Export in asciidoc_artisan/workers/__init__.py
from .my_worker import MyWorker
__all__ = [..., "MyWorker"]
```

### Adding Secure File Operations
```python
# Always use core utilities for file operations
from asciidoc_artisan.core import atomic_save_text, sanitize_path

# Sanitize user-provided paths
safe_path = sanitize_path(user_provided_path, base_dir="/safe/base")

# Atomic file writes (prevents corruption)
atomic_save_text(file_path, content, encoding="utf-8")
```

## Architectural Notes

### Transition from Monolith to Modular (v1.0 → v1.1)
The codebase underwent a major refactoring from a single-file `adp.py` (~3000 lines) to a modular package structure:
- **Old (v1.0)**: Single `adp.py` with all logic
- **New (v1.1)**: Package `asciidoc_artisan/` with separate modules for UI, workers, core
- **Entry Point**: `adp_windows.py` remains for backwards compatibility but imports from `asciidoc_artisan`

**When working with code:**
- New features should be added to the appropriate module in `asciidoc_artisan/`
- Follow the existing module organization (core, workers, ui)
- Update both `adp_windows.py` and package modules if needed for compatibility

**Note:** The `.github/copilot-instructions.md` still references the old `adp.py` structure. When in doubt, trust the current package structure in `asciidoc_artisan/` over the copilot instructions.

## Related Documentation

- **Package API:** `asciidoc_artisan/__init__.py` - Public API exports
- **Copilot Instructions:** `.github/copilot-instructions.md` - AI assistant guidance (outdated, refers to old structure)
- **Contributing Guide:** `CONTRIBUTING.md` - Detailed contribution workflow
- **Changelog:** `CHANGELOG.md` - Version history
- **Refactoring Reports:** `REFACTORING_*.md` - Architectural change documentation
- **Performance Reports:** `PERFORMANCE_SUMMARY.md`, `OPTIMIZATION_REPORT.md`
- **Quick Start:** `docs/QUICK_START.md` - New user guide
