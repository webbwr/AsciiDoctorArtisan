# AsciiDoc Artisan v2.1.0

**Release Date:** December 4, 2025 | **Type:** Public Release | **Status:** Production Ready

## Highlights

First production-stable release with LSP support and multi-core rendering.

### Features

- **LSP Server** - IDE integration (completion, diagnostics, hover, symbols)
- **Multi-core Rendering** - 2-4x speedup on 4+ core systems
- **GPU Acceleration** - 10-50x faster preview (NVIDIA/AMD/Intel)

## Metrics

| Metric | Value |
|--------|-------|
| Codebase | 44,201 lines / 171 files |
| Unit Tests | 5,254 (100% pass) |
| E2E Scenarios | 71 (91.5% pass) |
| Type Coverage | 100% (mypy --strict) |
| Requirements | 109 FRs implemented |
| Startup | 0.586s |

## Install

```bash
# From source
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
pip install -e ".[dev]"
```

## Requirements

- Python 3.11+
- PySide6 6.9+
- Pandoc, wkhtmltopdf

## What's New

- LSP: `python -m asciidoc_artisan.lsp`
- ParallelBlockRenderer with ThreadPoolExecutor
- Architecture documentation with FR mapping

---

*v2.1.0 | Production Ready | MIT License*
