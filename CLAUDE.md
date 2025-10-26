# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Is This Program?

**AsciiDoc Artisan** is a desktop editor for AsciiDoc files with live preview. Users see rendered output as they type.

**Key Technologies:**
- PySide6 6.9.0+ (Qt GUI framework)
- asciidoc3 10.2.1+ (AsciiDoc to HTML rendering)
- pypandoc 1.13+ (document format conversion)
- wkhtmltopdf (PDF creation)
- Python 3.11+ (3.12 recommended)

**Version:** 1.1.0-beta

**Key Features:**
- Universal format support (open and save any format)
- No conversion dialogs (Pandoc is default)
- AI conversion is optional setting
- Background conversion threads

## Installation & Setup

### Quick Install (Recommended)

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
# Install production dependencies
make install

# Install development dependencies
make install-dev
```

## Running & Testing

### Start Application

```bash
make run
# Or: python src/main.py
```

### Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_file_operations.py -v

# Run single test
pytest tests/test_settings.py::test_settings_save_load -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Check code (non-destructive)
make lint

# Auto-format code
make format
```

## Architecture

### Module Structure

The codebase follows a modular architecture (v1.1.0 refactoring):

```
src/asciidoc_artisan/
├── core/           # Business logic and data models
│   ├── settings.py             # Settings persistence
│   ├── models.py               # Data models (Settings, GitResult)
│   ├── file_operations.py      # Secure file I/O
│   ├── constants.py            # App-wide constants
│   ├── resource_manager.py     # Memory/CPU monitoring
│   └── secure_credentials.py   # API key management
├── ui/             # User interface components
│   ├── main_window.py          # Main application window
│   ├── menu_manager.py         # Menu creation and actions
│   ├── theme_manager.py        # Dark/light mode theming
│   ├── status_manager.py       # Status bar and messages
│   ├── file_handler.py         # File open/save logic
│   ├── export_manager.py       # Export and format conversion
│   ├── preview_handler.py      # Preview pane management
│   └── dialogs.py              # Custom dialogs (PreferencesDialog only)
├── workers/        # Background thread workers
│   ├── git_worker.py           # Git operations (pull/commit/push)
│   ├── pandoc_worker.py        # Document conversion + AI
│   ├── preview_worker.py       # AsciiDoc rendering
│   └── incremental_renderer.py # Performance optimization
└── conversion/     # Format conversion utilities
└── git/           # Git integration utilities
```

### Threading Model

Long-running operations use Qt's QThread pattern:

- **GitWorker**: Handles `git pull`, `git commit`, `git push` via subprocess
- **PandocWorker**: Universal format conversion (any format to any format)
  - Supports: AsciiDoc, Markdown, DOCX, HTML, PDF
  - Optional AI enhancement via Claude API
  - Automatic fallback to Pandoc if AI fails
- **PreviewWorker**: Renders AsciiDoc → HTML for live preview

**Communication Pattern:**
- Main thread → Worker: Emit signals (`request_git_command`, `request_pandoc_conversion`)
- Worker → Main thread: Emit result signals (`git_result`, `pandoc_result`)
- Use `@Slot` decorators for signal handlers

**Important Guards:**
- `_is_processing_git`: Prevents concurrent Git operations
- `_is_processing_pandoc`: Prevents concurrent Pandoc operations
- `_is_opening_file`: Prevents re-entry during file loads

Respect these flags when adding new operations.

### Security Features

Per specification FR-016 and FR-015:

```python
from asciidoc_artisan.core import sanitize_path, atomic_save_text

# Path traversal prevention (FR-016)
safe_path = sanitize_path(user_input)

# Atomic file writes (FR-015)
atomic_save_text(filepath, content)
```

**Git command safety:**
- Use list-form subprocess arguments (not shell strings)
- Example: `subprocess.run(["git", "commit", "-m", message])`

### Settings Persistence

Settings save to platform-specific locations:
- **Linux**: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows**: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

Managed by `Settings` dataclass and `QStandardPaths`.

## Development Workflow

### Making Changes

1. Read `SPECIFICATIONS.md` for requirements
2. Make your changes
3. Run tests: `make test`
4. Check code quality: `make lint`
5. Format code: `make format`
6. Update docs if needed

### Common Tasks

```bash
# Run application
make run

# Run tests with coverage
make test

# Check code style
make lint

# Auto-format code
make format

# Clean build artifacts
make clean
```

### High-Risk Areas

**Be careful when modifying:**
- Worker thread lifecycle in `main_window.py` (startup/shutdown in `closeEvent`)
- Git subprocess commands (security-sensitive)
- Pandoc invocation (environment-sensitive)
- Settings load/save (cross-platform path handling)

**Low-risk changes:**
- UI text updates
- CSS/styling tweaks
- Adding logging statements
- Documentation updates

### File References

When referencing code, use the pattern `file_path:line_number`:

```
Editor state is managed in src/asciidoc_artisan/ui/main_window.py:145
```

## Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point |
| `src/asciidoc_artisan/ui/main_window.py` | Main window controller |
| `src/asciidoc_artisan/core/settings.py` | Settings persistence |
| `src/asciidoc_artisan/workers/git_worker.py` | Git integration |
| `src/asciidoc_artisan/workers/pandoc_worker.py` | Format conversion |
| `requirements.txt` | Development dependencies |
| `requirements-production.txt` | Production dependencies |
| `Makefile` | Build automation |
| `pyproject.toml` | Project metadata and tool config |
| `SPECIFICATIONS.md` | Complete requirements (OpenSpec format) |

## Project Standards

### Code Style
- Line length: 88 characters (Black formatter)
- Type hints required (mypy checked)
- All functions/classes must be documented
- Target Python 3.11+ (3.12 recommended)

### Testing
- Framework: pytest + pytest-qt
- Coverage target: 100% (currently 71/71 tests passing)
- Test all new features
- Test all security-critical functions

### Documentation
- Keep README.md updated
- Update SPECIFICATIONS.md for requirement changes
- Document all public APIs
- Writing level: Grade 5.0 (elementary school reading level)

## External Dependencies

**System Requirements:**
- **Pandoc**: Required for format conversion
  - Linux: `sudo apt install pandoc wkhtmltopdf`
  - Mac: `brew install pandoc wkhtmltopdf`
  - Windows: Get from pandoc.org and wkhtmltopdf.org

- **wkhtmltopdf**: Required for PDF creation
  - Included in commands above
  - Linux: `sudo apt install wkhtmltopdf`
  - Mac: `brew install wkhtmltopdf`
  - Windows: Get from wkhtmltopdf.org

- **Git**: Optional for version control
  - Must be in PATH
  - Verify: `git --version`

**Python Packages:**
- See `requirements-production.txt` for runtime deps
- See `requirements.txt` for dev deps

## Troubleshooting

### Common Issues

**"Can't find pypandoc"**
```bash
pip install pypandoc
```

**"Can't find Pandoc"**
- Install Pandoc system binary (see External Dependencies)

**"PDF conversion fails"**
```bash
# Install wkhtmltopdf
sudo apt install wkhtmltopdf  # Linux
brew install wkhtmltopdf      # Mac
```

**"Git doesn't work"**
- Ensure file is in a Git repository
- Verify: `git status`

**Tests fail**
```bash
# Check test output for details
pytest tests/ -v

# Run single failing test
pytest tests/test_name.py::test_function -v
```

## Additional Resources

- **README.md** - User-facing documentation
- **SPECIFICATIONS.md** - Complete requirements (Grade 6.0)
- **docs/** - User guides and how-tos
- **.github/copilot-instructions.md** - AI assistant guidance
- **GitHub Issues** - Bug reports and feature requests

---

**Reading Level**: Grade 5.0
**For**: Claude Code and developers
**Last Updated**: October 2025
