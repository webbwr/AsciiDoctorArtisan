# CLAUDE.md

Guidance for Claude Code working with this repository.

## Overview

**AsciiDoc Artisan** — Desktop AsciiDoc editor with live preview (PySide6/Qt)

| Metric | Value |
|--------|-------|
| Version | 2.1.0 |
| Code | 45,900 lines / 180 files |
| Tests | 5,139 (95% coverage) |
| Types | mypy --strict (0 errors) |
| Startup | 0.27s |

**Stack:** PySide6 6.9+, Python 3.11+, asciidoc3, pypandoc, pymupdf, python-toon

**Package:** `asciidoc_artisan.{core, ui, workers, lsp, claude}`

**Settings:** TOON format (`.toon`) — auto-migrates from JSON

---

## Critical Patterns

Violations cause bugs. Follow exactly.

| Anti-Pattern | Correct |
|--------------|---------|
| Missing reentrancy guard | `if self._is_processing: return` |
| UI updates from threads | `result_ready.emit(data)` |
| `shell=True` subprocess | Always `shell=False`, list args |
| Direct file writes | `atomic_save_text(path, content)` |
| Logic in main_window.py | Delegate to handlers |

---

## Commands

```bash
# Run
make run                    # Optimized (-OO)
python3 src/main.py         # Normal

# Test
make test                   # All + coverage
pytest tests/unit/MODULE/   # Single module

# Quality
make format                 # ruff-format, isort
make lint                   # ruff, mypy --strict
```

**System deps:** `sudo apt install pandoc wkhtmltopdf gh`

---

## Architecture

```
src/asciidoc_artisan/
├── core/        13,085 lines   Business logic
├── ui/          22,794 lines   Qt widgets, handlers
├── workers/      5,915 lines   QThread workers
├── lsp/          2,134 lines   Language Server
└── claude/         658 lines   Claude AI
```

**Patterns:**
- Handler Pattern: `ui/*_handler.py` for domain logic
- Worker Threads: QThread for slow ops, signal/slot
- Reentrancy Guards: `_is_processing` flags
- Atomic Writes: temp file + rename

---

## Key Files

| Purpose | Files |
|---------|-------|
| Entry | `src/main.py` |
| Controller | `ui/main_window.py` (1,167 lines) |
| Handlers | `ui/{file,git,github,preview,search}_handler.py` |
| Workers | `workers/{git,pandoc,preview,ollama_chat}_worker.py` |
| AI | `claude/{claude_client,claude_worker}.py` |
| LSP | `lsp/{server,*_provider}.py` |

---

## Testing

**Markers:**
- `@pytest.mark.requires_gpu` — Qt WebEngine + GPU
- `@pytest.mark.live_api` — Requires Ollama

**Qt testing:** Use `MockParentWidget` from `tests/unit/ui/conftest.py`

**Coverage:** Max ~99% (Qt threading limits)

---

## Docs

| Doc | Purpose |
|-----|---------|
| SPECIFICATIONS.md | 109 FRs, code-gen schemas |
| docs/ARCHITECTURE.md | UML diagrams, patterns |
| ROADMAP.md | Version history |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Pandoc not found | `sudo apt install pandoc` |
| PDF export fails | `sudo apt install wkhtmltopdf` |
| Qt test errors | `pip install pytest-qt` |

---

*v2.1.0 | 45,900 lines | 5,139 tests | mypy --strict*

**Always apply MA principles: <400 lines/file, focused modules**
