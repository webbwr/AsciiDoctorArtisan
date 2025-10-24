# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AsciiDoc Artisan** is a modern PySide6 desktop application for editing AsciiDoc files with live HTML preview. It provides document conversion (via Pandoc), Git integration, and cross-platform support for Windows, Linux, and macOS.

**Core Technology Stack:**
- **UI Framework:** PySide6 (Qt for Python) 6.9.0+
- **AsciiDoc Processing:** asciidoc3 10.2.1+
- **Document Conversion:** pypandoc 1.13+ with Pandoc system binary
- **Python:** 3.11+ (3.12 recommended)

## Development Commands

### Setup
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

### Single-File Monolithic Design
The application is primarily contained in `adp_windows.py` (~3000 lines). This is intentional for simplicity and ease of deployment.

**Main Components:**
1. **`AsciiDocEditor` (QMainWindow)** - Main application class
   - UI setup and layout
   - File I/O operations
   - Settings persistence
   - Signal/slot coordination

2. **Worker Threads** - Background processing to keep UI responsive
   - `GitWorker` - Git operations (commit, pull, push)
   - `PandocWorker` - Document format conversion
   - `ClaudeWorker` - AI-enhanced conversion (optional)

3. **Supporting Modules:**
   - `pandoc_integration.py` - Enhanced Pandoc wrapper with error handling and PDF extraction
   - `claude_client.py` - Claude AI integration for conversions (optional)
   - `setup.py` - Package configuration

### Threading Model & State Management

**Critical State Flags (respect these when adding operations):**
- `_is_processing_git` - Prevents concurrent Git operations
- `_is_processing_pandoc` - Prevents concurrent Pandoc operations
- `_is_opening_file` - Prevents preview updates during file load
- `_is_syncing_scroll` - Prevents scroll recursion

**Thread Communication Pattern:**
```python
# Request work from UI thread
self.request_git_command.emit(["git", "commit", "-m", msg], repo_path)

# Worker processes in background
class GitWorker(QObject):
    @Slot(list, Path)
    def run_git_command(self, args, working_dir):
        result = subprocess.run(args, cwd=working_dir, ...)
        self.command_complete.emit(result.stdout, result.returncode)

# UI thread receives results
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

| File | Purpose |
|------|---------|
| `adp_windows.py` | Main application (UI, logic, workers) |
| `pandoc_integration.py` | Enhanced Pandoc wrapper with validation and PDF extraction |
| `claude_client.py` | Optional Claude AI integration |
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

Current test coverage is **basic**. Tests exist for:
- File operations (read/write/save)
- Settings persistence (load/save)

**When adding tests:**
- Use `pytest` with `pytest-qt` for Qt testing
- Mock file I/O and subprocess calls
- Avoid launching full GUI in tests (use QApplication fixture sparingly)
- Target 80%+ coverage for new features

## High-Risk Areas

### Before modifying these, review carefully:

1. **Thread lifecycle management** (`closeEvent`, worker startup/shutdown)
   - Workers must be properly cleaned up on exit
   - Signals must be disconnected before thread termination

2. **Git subprocess invocation** (`GitWorker.run_git_command`)
   - Security-sensitive: always validate paths and use list arguments
   - Cross-platform: test on Windows AND Linux

3. **Pandoc integration** (`PandocWorker`, `pandoc_integration.py`)
   - Environment-sensitive: Pandoc must be in PATH
   - Error handling is critical for user experience

4. **Settings JSON handling** (`_load_settings`, `_save_settings`)
   - Malformed JSON must not crash application
   - Path handling differs per platform

5. **State flags** (`_is_processing_*`)
   - Race conditions possible if not respected
   - Always reset flags in error handlers

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
# 1. Define signals in main class
request_work = Signal(str)  # input
work_complete = Signal(str)  # output

# 2. Create worker class
class MyWorker(QObject):
    result_ready = Signal(str)

    @Slot(str)
    def do_work(self, input_data):
        result = process(input_data)
        self.result_ready.emit(result)

# 3. Setup thread in __init__()
self.worker_thread = QThread()
self.worker = MyWorker()
self.worker.moveToThread(self.worker_thread)
self.request_work.connect(self.worker.do_work)
self.worker.result_ready.connect(self.handle_result)
self.worker_thread.start()

# 4. Clean up in closeEvent()
self.worker_thread.quit()
self.worker_thread.wait()
```

## Related Documentation

- **Copilot Instructions:** `.github/copilot-instructions.md` - AI assistant guidance
- **Contributing Guide:** `CONTRIBUTING.md` - Detailed contribution workflow
- **Changelog:** `CHANGELOG.md` - Version history
- **Optimization Report:** `OPTIMIZATION_REPORT.md` - Performance improvements
- **Quick Start:** `docs/QUICK_START.md` - New user guide
