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
- **v1.2+**: Ollama AI integration for smart document conversion
- **v1.3.0**: Grammar system (later removed in v1.4.0)
- **v1.4.0**: Full GPU/NPU hardware acceleration, automatic detection, document version display
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

**Current test coverage:** 34 test files, 481+ tests

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
│   ├── hardware_detection.py   # GPU/CPU capability detection (legacy)
│   ├── gpu_detection.py        # GPU/NPU detection with caching (v1.4.0)
│   ├── memory_profiler.py      # Memory usage profiling and analysis
│   ├── async_file_handler.py   # Asynchronous file operations
│   ├── lazy_importer.py        # Lazy module loading for performance
│   └── lazy_utils.py           # Utility functions for lazy evaluation
├── ui/                         # UI components (Qt widgets)
│   ├── main_window.py          # AsciiDocEditor (main window controller, 1714 lines)
│   ├── menu_manager.py         # Menu bar creation and actions
│   ├── theme_manager.py        # Dark/light theme management
│   ├── status_manager.py       # Status bar, document version display, messages
│   ├── file_handler.py         # File open/save/import dialogs
│   ├── export_manager.py       # Export to DOCX/PDF/HTML/MD
│   ├── preview_handler.py      # QTextBrowser preview (software fallback)
│   ├── preview_handler_gpu.py  # GPU-accelerated QWebEngineView (v1.4.0)
│   ├── git_handler.py          # Git UI operations
│   ├── action_manager.py       # QAction creation and management
│   ├── settings_manager.py     # Settings UI and persistence
│   ├── line_number_area.py     # Editor with line numbers
│   ├── editor_state.py         # Editor state tracking
│   ├── dialogs.py              # Custom dialogs (preferences, etc.)
│   ├── api_key_dialog.py       # API key management dialog
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

### Performance Optimizations

The application includes several performance-critical code paths:

**1. GPU-Accelerated Preview Rendering (v1.4.0)**
- **Location:** `ui/preview_handler_gpu.py`, `core/gpu_detection.py`, `src/main.py`
- **Tech:** Automatic GPU detection with intelligent fallback
  - **GPU available:** QWebEngineView with hardware acceleration (10-50x faster)
  - **No GPU/WSLg:** QTextBrowser software rendering (stable fallback)
- **Features:**
  - NVIDIA, AMD, Intel GPU auto-detection
  - Intel NPU support with OpenVINO
  - Compute capability detection (CUDA, OpenCL, Vulkan, ROCm)
  - GPU detection caching (100ms startup improvement)
  - Zero-copy texture sharing, hardware compositing
  - 70-90% reduction in CPU usage
  - Smooth 60fps+ scrolling
- **Environment Variables:** Automatically set in `main.py` before Qt initialization
  - `QT_OPENGL=desktop` - Desktop OpenGL rendering
  - `QT_XCB_GL_INTEGRATION=xcb_egl` - EGL integration
  - `QTWEBENGINE_CHROMIUM_FLAGS` - GPU optimization flags
- **Detection Cache:** `~/.cache/asciidoc_artisan/gpu_detection.json` (24-hour TTL)
- **Fallback Logic:** Automatically uses QTextBrowser if GPU unavailable or WSLg detected

**2. PyMuPDF PDF Reading (3-5x speedup)**
- **Location:** `src/document_converter.py:283-365`
- **Tech:** Uses `fitz.open()` (PyMuPDF) instead of pdfplumber
- **Benefits:** Faster parsing, lower memory usage, GPU acceleration where supported

**3. Incremental Rendering with Block Cache**
- **Location:** `workers/incremental_renderer.py` (460 lines)
- **Tech:** Block-based document splitting with LRU cache
- **How it works:**
  1. Split document into blocks by heading levels (=, ==, ===)
  2. Hash each block with MD5 for change detection
  3. Cache rendered HTML for unchanged blocks (LRU, 100 blocks max)
  4. Only re-render blocks that changed
  5. Assemble final HTML from cached + newly rendered blocks
- **Performance:** 3-5x faster for minor edits, enabled for docs >1000 chars
- **Cache:** `BlockCache` class with LRU eviction

**4. Optimized String Processing**
- **Table cell processing:** `src/document_converter.py` (`_clean_cell()`)
- **Heading detection:** `workers/incremental_renderer.py` (`count_leading_equals()`)
- **Tech:** Native Python string operations (C-optimized)
- **Note:** Called in tight loops (every table cell, every line)

**When modifying hot paths:**
1. Profile before/after changes
2. Test in both native and WSLg environments
3. Check logs show correct optimization status
4. Run benchmark scripts: `benchmark_performance.py`

### Ollama AI Integration (v1.2+)

The application integrates with Ollama for AI-powered document conversion:

**Location:** `workers/pandoc_worker.py` (Ollama logic), `ui/dialogs.py` (settings UI)

**Features:**
- Local AI processing (no cloud, privacy-focused)
- Model selection via UI (Tools → AI Status → Settings)
- Automatic fallback to Pandoc if Ollama unavailable or conversion fails
- Real-time status indicator in status bar

**Supported Models:**
- `phi3:mini` (recommended, fast, lightweight)
- `llama2` (better quality, slower)
- `mistral` (balanced performance)
- `codellama` (best for code-heavy documents)

**Conversion Flow:**
1. User enables Ollama in preferences
2. User selects model from dropdown
3. On import/export, PandocWorker tries Ollama first
4. If Ollama fails or unavailable, falls back to Pandoc
5. Status bar shows active conversion method

**Settings Storage:**
```python
# In Settings dataclass
ollama_enabled: bool = False
ollama_model: Optional[str] = None
```

**Testing:**
- Test with Ollama installed and running
- Test with Ollama disabled (fallback to Pandoc)
- Test with invalid model name (should show error and fallback)

### Document Version Display (v1.4.0)

**Real-time version detection in status bar:**

The application automatically extracts and displays document version from AsciiDoc content:

**Location:** `ui/status_manager.py:extract_document_version()`

**Detection Methods (in priority order):**
1. **AsciiDoc attributes:** `:version: 1.0.0` or `:revnumber: 1.0.0`
2. **Text labels:** `*Version*: 1.0.0` or `**Version**: 1.0.0`
3. **Title parsing:** Extracts from titles like "AsciiDoc v1.4.0 Roadmap"

**Display Format:**
- Status bar shows: `v{version}` (e.g., "v1.4.0")
- Shows "None" if no version detected
- Updates automatically when:
  - Opening a file
  - Saving a file
  - Editing document (real-time)

**Regex Patterns:**
```python
# Matches multiple version formats
r':(?:version|revnumber):\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[a-zA-Z0-9]+)?)'
r'\*\*?Version\*\*?:?\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[a-zA-Z0-9]+)?)'
r'v?([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[a-zA-Z0-9]+)?)\s*$'
```

**Integration Points:**
- `file_handler.py`: Calls `status_manager.update_version()` on open/save
- `main_window.py`: Updates on text change with debouncing
- `status_manager.py`: Handles extraction and display logic

### GPU/NPU Hardware Acceleration (v1.4.0)

**Automatic Detection and Fallback:**

The application automatically detects hardware capabilities and configures rendering accordingly:

1. **GPU Detection Flow:**
   - Check cache (`~/.cache/asciidoc_artisan/gpu_detection.json`, 24-hour TTL)
   - If cache miss: Run detection (NVIDIA, AMD, Intel GPUs + NPU)
   - Save results to cache for fast startup
   - Configure environment variables before Qt initialization
   - Select preview widget: QWebEngineView (GPU) or QTextBrowser (fallback)

2. **Supported Hardware:**
   - **NVIDIA GPUs:** Detected via `nvidia-smi`, supports CUDA/OpenCL/Vulkan
   - **AMD GPUs:** Detected via `rocm-smi`, supports ROCm/OpenCL/Vulkan
   - **Intel GPUs:** Detected via DRI devices + `clinfo`, supports OpenCL/Vulkan
   - **Intel NPU:** Detected via `/dev/accel*`, supports OpenVINO

3. **WSLg Compatibility:**
   - GPU detection works in WSLg environments
   - Automatic fallback to QTextBrowser if GPU initialization fails
   - Test in both native Linux and WSLg to ensure fallback works
   - No manual configuration required

4. **Code Locations:**
   - GPU detection: `core/gpu_detection.py`
   - Preview widget factory: `ui/preview_handler_gpu.py:create_preview_widget()`
   - Environment setup: `src/main.py` (before `QApplication` initialization)
   - Main window integration: `ui/main_window.py`

5. **Debugging GPU Issues:**
   ```bash
   # Check GPU detection cache
   cat ~/.cache/asciidoc_artisan/gpu_detection.json

   # Force cache refresh (delete cache file)
   rm ~/.cache/asciidoc_artisan/gpu_detection.json

   # Run with debug logging
   QTWEBENGINE_CHROMIUM_FLAGS="--enable-logging --v=1" python src/main.py

   # Check GPU status from app logs
   grep "GPU" ~/.asciidoc_artisan.log
   ```

6. **Performance Comparison:**
   - **With GPU:** 10-50x faster rendering, 70-90% less CPU usage
   - **Without GPU:** Same performance as v1.3.0 (QTextBrowser)
   - **Memory:** GPU uses ~100-200MB more VRAM but reduces system RAM usage

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
- **Profile performance:** Use `benchmark_performance.py`
- **Memory profiling:** Use `memory_profile.py`

## Common Pitfalls & Best Practices

### Threading Mistakes

**❌ Bad: Direct UI update from worker thread**
```python
class PreviewWorker(QObject):
    def render_preview(self, text):
        html = self.render(text)
        self.preview_widget.setHtml(html)  # WRONG: Not thread-safe!
```

**✅ Good: Use signals to communicate results**
```python
class PreviewWorker(QObject):
    render_complete = Signal(str)

    def render_preview(self, text):
        html = self.render(text)
        self.render_complete.emit(html)  # Main thread handles UI update
```

### Reentrancy Issues

**❌ Bad: No guard against concurrent operations**
```python
def _trigger_git_commit(self):
    self.request_git_command.emit(["git", "commit", ...])
    # User clicks again before first completes → corruption!
```

**✅ Good: Use reentrancy guards**
```python
def _trigger_git_commit(self):
    if self._is_processing_git:
        return  # Already processing

    self._is_processing_git = True
    self.request_git_command.emit(["git", "commit", ...])
    # Reset flag in handler after completion
```

### Subprocess Security

**❌ Bad: Shell injection vulnerability**
```python
message = user_input
subprocess.run(f"git commit -m {message}", shell=True)  # DANGEROUS!
```

**✅ Good: Always use list form**
```python
message = user_input
subprocess.run(["git", "commit", "-m", message], shell=False)
```

### File Operations

**❌ Bad: Non-atomic write (data loss on crash)**
```python
with open(filepath, 'w') as f:
    f.write(content)  # If crash happens here, file is corrupted
```

**✅ Good: Atomic write pattern**
```python
from asciidoc_artisan.core import atomic_save_text
atomic_save_text(filepath, content)  # Temp file + atomic rename
```

### Manager Pattern

**❌ Bad: Main window doing everything**
```python
class MainWindow:
    def __init__(self):
        self._create_menus()
        self._setup_theme()
        self._init_status_bar()
        # ... 2000+ lines of mixed concerns
```

**✅ Good: Delegate to specialized managers**
```python
class MainWindow:
    def __init__(self):
        self.menu_manager = MenuManager(self)
        self.theme_manager = ThemeManager(self)
        self.status_manager = StatusManager(self)
        # Each manager handles its own domain
```

### Preview Updates

**❌ Bad: Update on every keystroke (slow for large docs)**
```python
self.editor.textChanged.connect(self.update_preview)  # Too frequent!
```

**✅ Good: Use adaptive debouncing**
```python
self.editor.textChanged.connect(self._start_preview_timer)
# Timer delay adapts based on document size
```

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

- **README.md** — User-facing installation and usage guide (Grade 5.0 reading level)
- **SPECIFICATIONS.md** — Complete functional requirements (FR-001 to FR-053)
- **RELEASE_NOTES_v1.4.0.md** — v1.4.0 release notes and GPU acceleration details
- **ROADMAP_v1.5.0.md** — Future feature roadmap
- **DEEP_CODE_ANALYSIS_v1.4.0.md** — Codebase analysis and optimization opportunities
- **GitHub Issues** — Bug reports and feature requests

**Note:** `.github/copilot-instructions.md` is outdated (references old `adp.py` monolithic file). The application has been refactored into modular architecture. Use this CLAUDE.md for current guidance.

---

*This file is for Claude Code (claude.ai/code). Last updated for v1.4.0: October 27, 2025*
