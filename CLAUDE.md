# Guide for Claude Code

This file helps Claude Code work with this project.

## What Is This Program?

**AsciiDoc Artisan** helps you write AsciiDoc files. You see your work as you type.

**What It Uses:**
- PySide6 6.9.0 or newer (makes windows)
- asciidoc3 10.2.1 or newer (shows HTML)
- pypandoc 1.13 or newer (changes files)
- Python 3.11 or newer (we like 3.12 best)

**Version:** 1.1.0

**What Works:**
- All tests pass (71 out of 71)
- All features work
- Files save safely
- Code has type hints
- Lots of help docs

## How to Install

### Easy Way (Best Choice)

**On Mac or Linux:**
```bash
./install-asciidoc-artisan.sh
```

**On Windows 11:**
```powershell
.\Install-AsciiDocArtisan.ps1
```

The install script does this:
- Checks you have Python 3.11 or newer
- Gets Pandoc and Git if you need them
- Makes a safe space for tools
- Puts all tools on your computer
- Runs setup tasks
- Tests everything works

### Do It Yourself

```bash
# Get main tools
make install

# Get tools for making code
make install-dev
```

## How to Run It

```bash
make run
```

Or type:
```bash
python src/main.py
```

## How to Test It

```bash
# Run all tests
make test

# Run one test file
pytest tests/test_file_operations.py -v

# Run one test
pytest tests/test_settings.py::test_settings_save_load -v
```

## How to Check Code

```bash
# Check code (don't change it)
make lint

# Fix code style
make format
```

## How Code Is Set Up

The program has many parts:

**Main Parts:**
- `src/asciidoc_artisan/core/` - Main code
- `src/asciidoc_artisan/ui/` - Windows and buttons
- `src/asciidoc_artisan/workers/` - Background tasks
- `src/main.py` - Starts the program

**Tests:**
- `tests/` - All test files

**Docs:**
- `README.md` - Main help file
- `docs/` - How-to guides
- `SPECIFICATIONS.md` - What program must do

## Important Files

| File | What It Does |
|------|--------------|
| `src/main.py` | Starts program |
| `src/asciidoc_artisan/ui/main_window.py` | Main window |
| `src/asciidoc_artisan/core/settings.py` | Saves your choices |
| `requirements.txt` | Tools for making code |
| `requirements-production.txt` | Tools users need |
| `Makefile` | Quick commands |

## Settings Files

Your choices save here:
- **Linux**: `~/.config/AsciiDocArtisan/`
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`

## How to Add Features

1. Read `SPECIFICATIONS.md` first
2. Make your changes
3. Run tests: `make test`
4. Check code: `make lint`
5. Make it look nice: `make format`

## Common Tasks

**Run program:**
```bash
make run
```

**Test everything:**
```bash
make test
```

**Check code style:**
```bash
make lint
```

**Fix code style:**
```bash
make format
```

**Clean up:**
```bash
make clean
```

## Where Things Are

```
AsciiDoctorArtisan/
├── src/                    # Program code
│   ├── main.py            # Start here
│   └── asciidoc_artisan/  # Main code
│       ├── core/          # Basic parts
│       ├── ui/            # Windows
│       └── workers/       # Background tasks
├── tests/                 # Test code
├── docs/                  # Help files
├── templates/             # Example files
└── scripts/               # Helper scripts
```

## Need Help?

1. Read README.md first
2. Check docs/ folder
3. Look at SPECIFICATIONS.md
4. Ask on GitHub

## Key Rules

- Always test your changes
- Keep code simple
- Write at Grade 5.0 level
- Add tests for new features
- Update docs when you change things

---

**Reading Level**: Grade 5.0
**For**: Developers and AI helpers
**Last Updated**: October 2025
