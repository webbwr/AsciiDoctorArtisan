# AsciiDoc Artisan - Project Overview

## Purpose
Desktop AsciiDoc editor with live preview, built with PySide6/Qt for Python.

## Version & Metrics
- **Version**: 2.1.0
- **Code**: ~46,500 lines / 180 files
- **Tests**: 5,628 tests (95% coverage)
- **Types**: mypy --strict (0 errors)
- **Startup**: 0.27s

## Tech Stack
- **Python**: 3.11+ (targeting 3.13)
- **GUI**: PySide6 6.9+
- **AsciiDoc**: asciidoc3
- **Document conversion**: pypandoc, pymupdf
- **Settings**: TOON format (.toon) - auto-migrates from JSON
- **AI**: ollama, anthropic (Claude)
- **Async**: qasync, aiofiles

## Package Structure
```
src/asciidoc_artisan/
├── core/        13,085 lines   Business logic, utilities
├── ui/          22,794 lines   Qt widgets, handlers
├── workers/      5,915 lines   QThread workers
├── lsp/          2,134 lines   Language Server Protocol
└── claude/         658 lines   Claude AI integration
```

## Key Patterns
- **Handler Pattern**: `ui/*_handler.py` for domain logic delegation
- **Worker Threads**: QThread for blocking ops, signal/slot communication
- **Reentrancy Guards**: `_is_processing` flags prevent concurrent execution
- **Atomic Writes**: temp file + rename for data safety

## Critical Anti-Patterns (AVOID)
| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Missing reentrancy guard | `if self._is_processing: return` |
| UI updates from threads | `result_ready.emit(data)` |
| `shell=True` subprocess | Always `shell=False`, list args |
| Direct file writes | `atomic_save_text(path, content)` |
| Logic in main_window.py | Delegate to handlers |

## Key Entry Points
- `src/main.py` - Application entry
- `ui/main_window.py` - Main controller (1,167 lines)
- `ui/{file,git,github,preview,search}_handler.py` - Domain handlers
