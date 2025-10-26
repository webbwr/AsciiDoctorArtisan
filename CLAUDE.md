# CLAUDE.md

This file helps Claude Code work with this code.

## What Is This?

**AsciiDoc Artisan** is a desktop editor. It lets users write AsciiDoc files. Users see output as they type.

**Key Tech:**
- PySide6 6.9.0+ (Qt GUI with GPU support)
- asciidoc3 3.2.0+ (turns AsciiDoc to HTML)
- pypandoc 1.13+ (changes files)
- pymupdf 1.23.0+ (3-5x faster PDF reading)
- numba 0.58.0+ (optional, 10-50x faster tables)
- wkhtmltopdf (makes PDF)
- Python 3.11+ (3.12 best)

**Version:** 1.1.0-beta

**Key Features:**
- Opens any format
- Saves any format
- No pop-ups (Pandoc is default)
- AI help is optional
- Uses background threads
- GPU speed (2-5x faster preview)
- Fast PDF reading (3-5x faster)
- Smart optimizations (10-50x faster with Numba)

## Install

### Quick Install

**Linux/Mac:**
```bash
./install-asciidoc-artisan.sh
```

**Windows:**
```powershell
.\Install-AsciiDocArtisan.ps1
```

### Manual Install

```bash
# Install main parts
make install

# Install dev parts
make install-dev
```

## Run & Test

### Start App

```bash
make run
# Or: python src/main.py
```

### Run Tests

```bash
# Run all
make test

# Run one file
pytest tests/test_file_operations.py -v

# Run single test
pytest tests/test_settings.py::test_settings_save_load -v

# With coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Check code
make lint

# Format code
make format
```

## How It Works

### Module Layout

Code is split into parts (v1.1.0):

```
src/asciidoc_artisan/
├── core/           # Main logic
│   ├── settings.py             # Settings save
│   ├── models.py               # Data shapes
│   ├── file_operations.py      # File read/write
│   ├── constants.py            # Fixed values
│   ├── resource_manager.py     # Memory/CPU watch
│   └── secure_credentials.py   # API keys
├── ui/             # User interface
│   ├── main_window.py          # Main window (GPU enabled)
│   ├── menu_manager.py         # Menus
│   ├── theme_manager.py        # Dark/light mode
│   ├── status_manager.py       # Status bar
│   ├── file_handler.py         # File open/save
│   ├── export_manager.py       # Export files
│   ├── preview_handler.py      # Preview pane (GPU boost)
│   └── dialogs.py              # Pop-ups
├── workers/        # Background tasks
│   ├── git_worker.py           # Git work
│   ├── pandoc_worker.py        # File changes
│   ├── preview_worker.py       # Show preview
│   └── incremental_renderer.py # Speed boost (JIT optimized)
└── conversion/     # File change tools
└── git/           # Git tools
```

### Threading

Long tasks use Qt threads:

- **GitWorker**: Does `git pull`, `git commit`, `git push`
- **PandocWorker**: Changes any format to any format
  - Works with: AsciiDoc, Markdown, DOCX, HTML, PDF
  - Can use AI help
  - Falls back to Pandoc if AI fails
- **PreviewWorker**: Turns AsciiDoc into HTML

**How They Talk:**
- Main thread → Worker: Send signals
- Worker → Main thread: Send results
- Use `@Slot` for signal handlers

**Important Flags:**
- `_is_processing_git`: Stops multiple Git tasks
- `_is_processing_pandoc`: Stops multiple Pandoc tasks
- `_is_opening_file`: Stops re-entry during file loads

Use these flags when you add new work.

### Security

From specs FR-016 and FR-015:

```python
from asciidoc_artisan.core import sanitize_path, atomic_save_text

# Stop bad paths (FR-016)
safe_path = sanitize_path(user_input)

# Safe file writes (FR-015)
atomic_save_text(filepath, content)
```

**Git safety:**
- Use list form for subprocess
- Example: `subprocess.run(["git", "commit", "-m", message])`

### Settings Save

Settings save to:
- **Linux**: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows**: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

Managed by `Settings` class and `QStandardPaths`.

## Make Changes

### Steps

1. Read `SPECIFICATIONS.md` for rules
2. Make your changes
3. Run tests: `make test`
4. Check code: `make lint`
5. Format code: `make format`
6. Update docs if needed

### Common Tasks

```bash
# Run app
make run

# Run tests
make test

# Check code
make lint

# Format code
make format

# Clean build
make clean
```

### High-Risk Areas

**Be careful with:**
- Worker threads in `main_window.py`
- Git subprocess commands
- Pandoc calls
- Settings load/save
- GPU settings in `preview_handler.py`
- PyMuPDF calls in `document_converter.py`
- Numba JIT functions (must be Numba-compatible)

**Low-risk changes:**
- UI text
- CSS/styling
- Adding logs
- Doc updates

### Performance Hot Paths (v1.1)

**GPU Acceleration** (2-5x faster preview):
- Location: `src/asciidoc_artisan/ui/main_window.py:457-467`
- Location: `src/asciidoc_artisan/ui/preview_handler.py:61-79`
- Uses: QWebEngineView with Accelerated2dCanvas + WebGL
- Falls back to CPU if GPU unavailable

**PyMuPDF** (3-5x faster PDF reading):
- Location: `src/document_converter.py:283-365`
- Uses: `fitz.open()` instead of pdfplumber
- GPU-accelerated where supported

**Numba JIT Cell Processing** (10-50x faster):
- Location: `src/document_converter.py:387-426`
- Function: `_clean_cell()`
- Optional: Falls back to Python if Numba not installed
- Hot path: Called for every table cell

**Numba JIT Text Splitting** (5-10x faster):
- Location: `src/asciidoc_artisan/workers/incremental_renderer.py:173-202`
- Function: `count_leading_equals()`
- Optional: Falls back to Python if Numba not installed
- Hot path: Called for every line during document splitting

**When modifying hot paths:**
- Test with and without Numba
- Check GPU fallback works
- Verify no performance regressions
- Update logs to show optimization status

### File References

When you mention code, use `file_path:line_number`:

```
Editor state is in src/asciidoc_artisan/ui/main_window.py:145
```

## Key Files

| File | What It Does |
|------|---------|
| `src/main.py` | App starts here |
| `src/asciidoc_artisan/ui/main_window.py` | Main window |
| `src/asciidoc_artisan/core/settings.py` | Settings save |
| `src/asciidoc_artisan/workers/git_worker.py` | Git work |
| `src/asciidoc_artisan/workers/pandoc_worker.py` | Format changes |
| `requirements.txt` | Dev tools |
| `requirements-production.txt` | Main tools |
| `Makefile` | Build help |
| `pyproject.toml` | Project info |
| `SPECIFICATIONS.md` | Full rules |

## Project Rules

### Code Style
- Line length: 88 chars (Black)
- Type hints needed (mypy check)
- All functions need docs
- Target Python 3.11+ (3.12 best)

### Testing
- Use: pytest + pytest-qt
- Goal: 100% coverage (now 371 tests)
- Test all new features
- Test all security functions

### Docs
- Keep README.md updated
- Update SPECIFICATIONS.md for changes
- Document all public APIs
- Writing level: Grade 5.0

## What You Need

**System:**
- **Pandoc**: Needed for format changes
  - Linux: `sudo apt install pandoc wkhtmltopdf`
  - Mac: `brew install pandoc wkhtmltopdf`
  - Windows: Get from pandoc.org and wkhtmltopdf.org

- **wkhtmltopdf**: Needed for PDF
  - Linux: `sudo apt install wkhtmltopdf`
  - Mac: `brew install wkhtmltopdf`
  - Windows: Get from wkhtmltopdf.org

- **Git**: Optional for version control
  - Must be in PATH
  - Check: `git --version`

**Python Parts:**
- See `requirements-production.txt` for runtime
- See `requirements.txt` for dev

## Fix Problems

### Common Issues

**"Can't find pypandoc"**
```bash
pip install pypandoc
```

**"Can't find Pandoc"**
- Install Pandoc (see What You Need)

**"PDF fails"**
```bash
# Install wkhtmltopdf
sudo apt install wkhtmltopdf  # Linux
brew install wkhtmltopdf      # Mac
```

**"Git doesn't work"**
- Make sure file is in Git repo
- Check: `git status`

**Tests fail**
```bash
# Check output
pytest tests/ -v

# Run single test
pytest tests/test_name.py::test_function -v
```

## More Help

- **README.md** - User docs
- **SPECIFICATIONS.md** - Full rules
- **docs/** - User guides
- **.github/copilot-instructions.md** - AI help
- **GitHub Issues** - Bug reports

---

**Reading Level**: Grade 5.0
**For**: Claude Code and developers
**Last Updated**: October 2025
