<!-- .github/copilot-instructions.md: guidance for AI coding agents -->
# Copilot instructions — AsciiDoc Artisan

⚠️ **This file is outdated.** The application has been refactored from a monolithic `adp.py` file into a modular package structure.

**Please refer to the current documentation:**
- **[CLAUDE.md](../CLAUDE.md)** — Comprehensive developer guide (architecture, commands, best practices)
- **[README.md](../README.md)** — User-facing installation and usage guide
- **[SPECIFICATIONS.md](../SPECIFICATIONS.md)** — Complete functional requirements

---

## Quick Reference (Updated)

### Current Architecture (v1.4.0-beta)

The application is now organized as a modular Python package:

```
src/
├── main.py                          # Entry point
├── document_converter.py            # PDF/document conversion utilities
└── asciidoc_artisan/               # Main package
    ├── core/                        # Business logic & utilities
    ├── ui/                          # UI components (managers + main window)
    ├── workers/                     # QThread worker classes
    ├── conversion/                  # Format conversion utilities
    ├── git/                         # Git integration utilities
    └── claude/                      # Claude AI integration (future)
```

### Key Files (Updated Locations)

| Old Location | New Location | Purpose |
|--------------|--------------|---------|
| `adp.py` (monolithic) | **Refactored into:** | |
| | `src/main.py` | Entry point (127 lines) |
| | `src/asciidoc_artisan/ui/main_window.py` | Main window controller (1714 lines) |
| | `src/asciidoc_artisan/core/*.py` | Core utilities (settings, file ops, models) |
| | `src/asciidoc_artisan/workers/*.py` | Background workers (Git, Pandoc, Preview) |
| | `src/asciidoc_artisan/ui/*_manager.py` | UI managers (menu, theme, status, etc.) |

### Common Commands (Updated)

```bash
# Run the application
make run
# or
python src/main.py

# Run tests
make test
pytest tests/ -v

# Lint and format
make lint
make format

# Clean build artifacts
make clean
```

### Developer Workflows

1. **Read CLAUDE.md first** — Contains complete architecture documentation
2. **Follow manager pattern** — Don't put UI logic in main_window.py; use specialized managers
3. **Respect reentrancy guards** — Check `_is_processing_git`, `_is_processing_pandoc` flags
4. **Use atomic file operations** — Import from `asciidoc_artisan.core.file_operations`
5. **Never use shell=True** — Always pass list args to subprocess.run()

### Testing Notes

- **Framework:** pytest + pytest-qt
- **Coverage:** 34 test files, 481+ tests
- **GUI Testing:** Use `qtbot` fixture for widget interactions
- **Run single test:** `pytest tests/test_file_operations.py -v`

### High-Risk Areas (Review Before Changing)

1. **Threading:** Worker initialization/shutdown in `ui/main_window.py`
2. **Subprocess calls:** Git commands in `workers/git_worker.py`
3. **Format conversion:** Pandoc + Ollama in `workers/pandoc_worker.py`
4. **Settings I/O:** Atomic writes in `core/settings.py`
5. **Performance paths:** Incremental rendering in `workers/incremental_renderer.py`
6. **WSLg compatibility:** Preview widget in `ui/main_window.py` and `ui/preview_handler.py`

### New Features (v1.2+)

- **Ollama AI Integration:** Local AI for document conversion (phi3:mini, llama2, mistral)
- **Incremental Rendering:** Block-based caching for 3-5x faster preview updates
- **WSLg Compatibility:** Uses QTextBrowser instead of QWebEngineView

---

**For complete documentation, see [CLAUDE.md](../CLAUDE.md)**
