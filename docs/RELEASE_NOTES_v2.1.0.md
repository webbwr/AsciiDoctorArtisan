# AsciiDoc Artisan v2.1.0 Release Notes

**Release Date:** December 3, 2025
**Type:** Public Release (First Stable)
**Status:** Production Ready

---

## Overview

AsciiDoc Artisan v2.1.0 is the **first public release** of a production-stable, feature-complete AsciiDoc editor. This release marks the transition from beta to stable, with full Language Server Protocol support, multi-core rendering, and comprehensive documentation.

## Key Features

### Language Server Protocol (LSP)

Full LSP implementation enables IDE integration with any LSP-compatible editor:

| Feature | Description |
|---------|-------------|
| `textDocument/completion` | Context-aware auto-complete for syntax, attributes, xrefs |
| `textDocument/publishDiagnostics` | Real-time syntax validation with error highlighting |
| `textDocument/hover` | Documentation on hover for AsciiDoc elements |
| `textDocument/documentSymbol` | Document outline with heading hierarchy |
| `textDocument/definition` | Go-to-definition for cross-references |

**Start the LSP server:**
```bash
python -m asciidoc_artisan.lsp
```

**Implementation:** 6 provider modules, 1,359 lines, 54 tests

### Multi-core Rendering

ParallelBlockRenderer leverages ThreadPoolExecutor for 2-4x speedup:

- Thread-local AsciiDoc instances for thread safety
- Block-based parallelization for independent units
- Graceful fallback on single-core systems
- Automatic CPU core detection

### Architecture Documentation

New `docs/ARCHITECTURE.md` provides comprehensive system design:

- ASCII diagrams for threading model and data flow
- FR-to-code mapping for all 109 functional requirements
- Security patterns and performance characteristics
- Extension points for workers, LSP features, and UI managers

## Metrics

| Metric | Value |
|--------|-------|
| Codebase | 44,201 lines across 171 files |
| Unit Tests | 5,254 passing |
| E2E Scenarios | 71 (65 passing, 91.5%) |
| Type Coverage | 100% (mypy --strict, 0 errors) |
| Requirements | 109 FRs, 100% implemented |
| Startup Time | 0.586s |

## Installation

### From PyPI (Recommended)
```bash
pip install asciidoc-artisan
```

### From Source
```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
pip install -e ".[dev]"
```

### Using Installer Scripts
```bash
# Linux/macOS
./install-asciidoc-artisan.sh

# Windows PowerShell
.\install-asciidoc-artisan.ps1
```

## Dependencies

### Required
- Python 3.11+
- PySide6 6.9+
- Pandoc (for format conversion)
- wkhtmltopdf (for PDF export)

### Optional
- Git (for version control integration)
- GitHub CLI (`gh`) for GitHub features
- Ollama (for AI chat assistance)
- GPU drivers (NVIDIA/AMD for hardware acceleration)

### New in v2.1.0
- `pygls>=2.0.0` - Python LSP server framework
- `lsprotocol>=2025.0.0` - LSP type definitions

## Upgrade Guide

### From v2.0.x
```bash
pip install --upgrade asciidoc-artisan
```

No breaking changes. All existing functionality preserved.

### From v1.x
1. Backup your settings (`~/.config/AsciiDocArtisan/`)
2. Uninstall old version: `pip uninstall asciidoc-artisan`
3. Install new version: `pip install asciidoc-artisan`
4. Settings will be migrated automatically on first run

## Known Limitations

- E2E test suite: 6 scenarios skipped (spell check, suite execution timing)
- GPU detection cache: 24hr TTL (clear `~/.cache/asciidoc_artisan/gpu_detection.json` to refresh)
- LSP server: Standalone process (not yet integrated into main app)

## What's Next

v2.1.x will focus on maintenance and stability:
- Bug fixes as reported
- Performance optimizations
- Documentation improvements

v3.0.0 (deferred) will add:
- Plugin architecture
- Real-time collaboration
- Marketplace for extensions

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

Report issues: https://github.com/webbwr/AsciiDoctorArtisan/issues

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

**Thank you for using AsciiDoc Artisan!**

*AsciiDoc Artisan v2.1.0 - First Public Release*
