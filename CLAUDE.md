# CLAUDE.md

Guidance for Claude Code working with this repository.

## Overview

**AsciiDoc Artisan** — Desktop AsciiDoc editor with live preview (PySide6/Qt)

| Metric | Value |
|--------|-------|
| Version | 2.1.0 (Dec 5, 2025) |
| Status | Public Release |
| Codebase | 46,457 lines / 180 files |
| Tests | 5,122 unit + 17 E2E (95% cov) |
| Types | mypy --strict (0 errors) |
| Startup | 0.27s |

**Stack:** PySide6 6.9+, Python 3.11+, asciidoc3, pypandoc, pymupdf

**Package:** `asciidoc_artisan.{core, ui, workers, lsp, claude}`

## Critical Patterns

**Must follow — bugs result from violations:**

| ❌ Anti-Pattern | ✅ Correct |
|----------------|-----------|
| Missing reentrancy guard | `if self._is_processing: return` before async ops |
| UI updates from threads | Use signals: `result_ready.emit(data)` |
| `shell=True` subprocess | Always `shell=False`, list args |
| Direct file writes | `atomic_save_text(path, content)` |
| Logic in main_window.py | Delegate to managers |

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

## Architecture

```
src/asciidoc_artisan/
├── core/       # Settings, file ops, GPU, search, spell
├── ui/         # main_window, managers, dialogs
├── workers/    # QThread: git, pandoc, preview, ollama
├── claude/     # AI client/worker
└── lsp/        # Language Server Protocol
```

**Patterns:**
- Manager Pattern: UI split into {menu,theme,status,file,git,export,telemetry,chat_worker_router}_manager
- Worker Threads: QThread for slow ops, signal/slot communication
- Reentrancy Guards: `_is_processing_*` flags prevent concurrent ops
- GPU Detection: Auto CPU fallback, 24hr cache

**Settings paths:**
- Linux: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- macOS: `~/Library/Application Support/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`

## Testing

**Markers:**
- `@pytest.mark.requires_gpu` — Qt WebEngine + GPU
- `@pytest.mark.live_api` — Requires Ollama service

**Qt dialog testing:** Use `MockParentWidget` from `tests/unit/ui/conftest.py`

**Coverage limits:** Qt threading prevents 100% — max ~99% achievable

## Key Files

| Purpose | Files |
|---------|-------|
| Entry | `src/main.py` |
| Controller | `ui/main_window.py` (1,167 lines) |
| Managers | `ui/{menu,theme,status,file,git,export,telemetry,chat_worker_router}_manager.py` |
| Workers | `workers/{git,pandoc,preview,ollama_chat}_worker.py` |
| AI | `claude/{claude_client,claude_worker}.py` |
| LSP | `lsp/{server,providers/*}.py` |

## Docs

| Doc | Purpose |
|-----|---------|
| SPECIFICATIONS.md | 109 FRs with file locations |
| docs/ARCHITECTURE.md | System design, FR mapping |
| ROADMAP.md | Version history |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Pandoc not found | `sudo apt install pandoc` |
| PDF export fails | `sudo apt install wkhtmltopdf` |
| Qt test errors | `pip install pytest-qt` |

---

*v2.1.0 | 46,457 lines | 5,139 tests | mypy --strict*
- always apply MA principles
