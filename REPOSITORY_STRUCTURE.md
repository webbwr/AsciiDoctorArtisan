# AsciiDoc Artisan Repository Structure

**Date**: October 2025
**Version**: 1.1.0

## Overview

This document shows the complete structure of the AsciiDoc Artisan repository.

## Root Directory

```
AsciiDoctorArtisan/
├── .claude/                    # Claude Code configuration
│   ├── settings.local.json
│   └── (private config files)
├── .github/                    # GitHub workflows and templates
├── src/                        # Application source code ⭐
├── tests/                      # Test suite
├── docs/                       # User documentation
├── templates/                  # AsciiDoc project templates
├── scripts/                    # Utility scripts
├── openspec/                   # Specification system ⭐
├── SPECIFICATIONS.md           # Main specification (single source of truth) ⭐
├── README.md                   # Project overview
├── CLAUDE.md                   # Claude Code instructions
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT License
├── SECURITY.md                 # Security policy
├── Makefile                    # Build commands
├── pyproject.toml             # Python project configuration
├── setup.py                    # Package setup
├── pytest.ini                  # Test configuration
├── requirements.txt            # Python dependencies (flexible)
├── requirements-production.txt # Python dependencies (pinned)
├── check_readability.py       # Reading level checker
├── launch_gui.sh              # Linux/Mac launcher
└── launch_gui.bat             # Windows launcher
```

## Source Code (`src/`)

```
src/
├── main.py                     # Application entry point
├── ai_client.py               # Legacy AI integration
├── document_converter.py      # Legacy document converter
├── performance_profiler.py    # Performance monitoring
└── asciidoc_artisan/          # Main application package
    ├── __init__.py
    ├── core/                  # Core functionality
    │   ├── __init__.py
    │   ├── constants.py       # Application constants
    │   ├── models.py          # Data models
    │   ├── settings.py        # Settings persistence
    │   ├── file_operations.py # Secure file I/O
    │   ├── secure_credentials.py # Credential management
    │   └── resource_monitor.py # System resource monitoring
    ├── ui/                    # User interface
    │   ├── __init__.py
    │   ├── main_window.py     # Main application window
    │   ├── dialogs.py         # Dialog windows
    │   ├── api_key_dialog.py  # API key entry
    │   ├── menu_manager.py    # Menu management
    │   ├── settings_manager.py # Settings UI
    │   ├── status_manager.py  # Status bar
    │   └── theme_manager.py   # Theme/dark mode
    ├── workers/               # Background processing
    │   ├── __init__.py
    │   ├── pandoc_worker.py   # Document conversion worker
    │   └── preview_worker.py  # HTML preview worker
    ├── claude/                # AI integration (optional)
    │   └── __init__.py
    └── conversion/            # Document conversion utilities
        └── __init__.py
```

## Tests (`tests/`)

```
tests/
├── __init__.py
├── test_file_operations.py    # File I/O tests
├── test_settings.py           # Settings tests
├── test_claude_client.py      # AI client tests
├── test_pandoc_worker.py      # Pandoc worker tests
├── test_preview_worker.py     # Preview worker tests
├── test_pdf_extractor.py      # PDF extraction tests
├── test_performance.py        # Performance tests
└── test_ui_integration.py     # UI integration tests
```

**Test Coverage**: 71/71 tests passing

## Documentation (`docs/`)

```
docs/
├── index.md                   # Documentation index
├── how-to-install.md         # Installation guide (Grade 3.2)
├── how-to-use.md             # User guide (Grade 5.1)
├── how-to-contribute.md      # Contribution guide (Grade 4.0)
└── old-docs/                 # Archived documentation
```

## Templates (`templates/`)

```
templates/
├── README.md                  # Template system guide
└── default/                   # Default AsciiDoc project template
    ├── README.adoc
    ├── asciidoc-config.yml
    ├── build.sh
    ├── docs/
    │   ├── index.adoc
    │   ├── chapter1.adoc
    │   └── chapter2.adoc
    ├── images/
    ├── themes/
    └── output/
```

## Scripts (`scripts/`)

```
scripts/
├── validate-spec.sh           # Specification validator ⭐
├── AsciiDocArtisanVerify.ps1 # Windows verification script
└── remove_old_settings_methods.py # Maintenance script
```

## OpenSpec System (`openspec/`)

```
openspec/
├── README.md                  # OpenSpec system guide
├── changes/                   # Proposed changes
│   └── _template/            # Reusable templates for proposals
│       ├── proposal.md       # Proposal template
│       ├── tasks.md          # Tasks template
│       ├── design.md         # Design template
│       └── specs/
│           └── example.md    # Spec changes template
└── archive/                   # Completed changes (empty)
```

**Purpose**: OpenSpec-inspired change proposal system for tracking feature additions and modifications.

## Configuration Files

### Python Configuration
- **pyproject.toml** - Project metadata, build config, tool settings (black, ruff, mypy, pytest)
- **setup.py** - Package installation
- **pytest.ini** - Test runner configuration
- **requirements.txt** - Development dependencies (flexible versions)
- **requirements-production.txt** - Production dependencies (pinned versions)

### Code Quality
- **.pre-commit-config.yaml** - Pre-commit hooks (black, ruff, mypy)
- **.ruff.toml** - Ruff linter configuration
- **.editorconfig** - Editor configuration

### Other
- **.claude.json** - Claude Code project configuration
- **.gitignore** - Git ignore patterns
- **Makefile** - Common development commands

## Key Files

### Documentation
- **README.md** - Main project documentation (Grade 5.0)
- **SPECIFICATIONS.md** - Complete requirements specification (Grade 6.0) ⭐
- **CLAUDE.md** - Instructions for Claude Code AI assistant
- **CHANGELOG.md** - Version history
- **SECURITY.md** - Security policy and reporting

### Entry Points
- **src/main.py** - Main application entry point
- **launch_gui.sh** - Linux/Mac launcher script
- **launch_gui.bat** - Windows launcher script

### Validation
- **check_readability.py** - Measures document reading level
- **scripts/validate-spec.sh** - Validates specification format

## Directory Purposes

### Production Code
- **src/** - All application code
- **src/asciidoc_artisan/** - Modular package architecture
- **src/main.py** - Entry point (backwards compatibility)

### Quality Assurance
- **tests/** - Comprehensive test suite (71 tests)
- **scripts/** - Validation and maintenance scripts

### Documentation
- **docs/** - User-facing documentation
- **SPECIFICATIONS.md** - Technical specifications
- **openspec/** - Change proposal system

### User Resources
- **templates/** - Project templates for users

### Development
- Configuration files at root
- **.github/** - CI/CD workflows

## Important Notes

### Single Source of Truth
**SPECIFICATIONS.md** is the authoritative specification. All requirements are documented there using:
- 6 domain sections (Core, Editor, Preview, Git, Conversion, UI)
- 44 requirements with SHALL language
- 76 Given/When/Then scenarios
- Grade 6.0 reading level

### OpenSpec System
The **openspec/** directory provides a framework for proposing changes:
- **changes/_template/** - Copy to create new proposals
- **changes/** - Active proposals (currently empty)
- **archive/** - Completed changes

### Legacy Files
- **src/ai_client.py** - Legacy Claude integration (being refactored)
- **src/document_converter.py** - Legacy converter (being refactored)
- **src/performance_profiler.py** - Performance monitoring utility

### Reading Levels
All documentation targets Grade 5-6 (elementary/middle school):
- README.md: Grade 5.0
- SPECIFICATIONS.md: Grade 6.0
- how-to-install.md: Grade 3.2
- how-to-use.md: Grade 5.1
- how-to-contribute.md: Grade 4.0

## File Counts

```
Total Files: ~100
Source Code: ~25 Python files
Tests: 8 test files
Documentation: ~15 markdown files
Templates: ~10 AsciiDoc files
Configuration: ~10 config files
```

## Repository Size

```
Code: ~20,000 lines of Python
Tests: ~5,000 lines
Documentation: ~10,000 lines
Total: ~35,000 lines
```

---

**Document Info**: Repository structure | October 2025 | v1.1.0
