# CLAUDE.md

Guide for Claude Code when working with AsciiDoc Artisan.

## Overview

**AsciiDoc Artisan** — Cross-platform desktop AsciiDoc editor with live preview (PySide6/Qt)

**Version:** 2.0.0 (Nov 9, 2025) | **Status:** Production-ready | **Startup:** 0.586s

**Stack:** PySide6 6.9+, Python 3.11+, asciidoc3 3.2+, pypandoc 1.13+, pymupdf 1.23+

**Architecture:**
- Single-window Qt app: split editor/preview, GPU-accelerated rendering
- Multi-threaded: UI main thread, Git/Pandoc/Preview on QThread workers
- Modular: 561-line main_window.py (from 1,719), manager pattern for separation of concerns
- Package: `asciidoc_artisan.{core, ui, workers, conversion, git, claude}`

**v2.0 Features:**
- Auto-complete: Context-aware syntax, fuzzy matching, Ctrl+Space, <50ms for 1K items
- Syntax checking: Real-time validation, color-coded errors, F8 navigation, <100ms for 1K lines
- Templates: 6 built-in types, Handlebars variables, <200ms load

**Quality:** 4,092 tests (100% pass), mypy --strict (0 errors), 88-char line limit

## Critical Patterns — Read First!

**Common mistakes causing bugs:**

1. **❌ Missing reentrancy guards** → concurrent operations crash
   ```python
   # GOOD
   if self._is_processing_git:
       return
   self._is_processing_git = True
   self.git_worker.commit(...)
   ```

2. **❌ UI updates from worker threads** → crashes/corruption
   ```python
   # GOOD - use signals
   class Worker(QThread):
       result_ready = Signal(str)
       def run(self):
           self.result_ready.emit(html)  # Main thread handles
   ```

3. **❌ Using shell=True in subprocess** → shell injection vulnerability
   ```python
   # GOOD
   subprocess.run(["git", "commit", "-m", msg], shell=False)
   ```

4. **❌ Direct file writes** → file corruption on crash
   ```python
   # GOOD
   from asciidoc_artisan.core import atomic_save_text
   atomic_save_text(path, content)  # Atomic via temp file
   ```

5. **❌ Adding logic to main_window.py** → delegate to managers (menu, theme, status, file, git, export)

## Quick Start

```bash
# Setup
./install-asciidoc-artisan.sh  # Automated (Linux/Mac)
# OR: pip install -r requirements.txt && pip install -e ".[dev]" && pre-commit install

# Run
make run                        # Optimized (python3 -OO)
python3 src/main.py             # Normal (keeps docstrings)

# Test
make test                       # All tests + coverage (→ htmlcov/index.html)
pytest tests/test_file.py -v    # Single file
pytest tests/test_file.py::test_func  # Single test

# Quality
make format                     # Auto-format (black, isort, ruff)
make lint                       # Check (ruff, black, mypy --strict)
pre-commit run --all-files      # Manual hook run

# Build
make build                      # Package
make clean                      # Remove artifacts
make help                       # All targets
```

**Dependencies:**
- System: Pandoc (required), wkhtmltopdf (required), Git (optional), GitHub CLI (optional), Ollama (optional)
- Install: `sudo apt install pandoc wkhtmltopdf gh` (Linux) or `brew install pandoc wkhtmltopdf gh` (Mac)

**Docs:**
- SPECIFICATIONS.md — 84 functional rules (read before changes)
- src/asciidoc_artisan/ui/main_window.py — Main controller (561 lines)

## Development Workflow

**Standard process:**
1. Check SPECIFICATIONS.md for requirements
2. Make changes (follow patterns, respect reentrancy guards)
3. `make test` — must pass 100%
4. `make format` — auto-fix style
5. `make lint` — verify mypy --strict compliance
6. Update docs for public API changes

**Pre-commit hooks:**
- Auto-enabled after `pre-commit install`
- Runs: ruff (lint), black (format), trailing whitespace, YAML/TOML validation, large file check
- Bypass (emergency only): `git commit --no-verify`

**Risk levels:**
- **High**: Threading, subprocess, format conversion, settings I/O, reentrancy guards
- **Medium**: UI managers, file I/O, resource monitoring
- **Low**: UI text, CSS, logs, docs

## Architecture

**Design patterns:**
1. **Manager Pattern**: UI split into specialized managers → reduces coupling, improves testability
2. **Worker Threads**: Slow ops on QThread (Git/Pandoc/Preview) → signal/slot communication
   - **Critical**: Always check reentrancy guards (`_is_processing_git`, `_is_processing_pandoc`, `_is_opening_file`)
3. **GPU Auto-Detection**: HW acceleration with CPU fallback → 10-50x faster, 70-90% less CPU
   - Cache: 24hr, QWebEngineView (GPU) or QTextBrowser (CPU)
4. **Security-First**: Atomic file writes, path sanitization, subprocess list-form only
5. **Incremental Rendering**: Block-based cache, MD5 hashing, LRU (100 blocks)

**Directory structure:**
```
src/asciidoc_artisan/
├── core/       # Business logic, settings, file ops, GPU detection, search, spell, security
├── ui/         # Qt widgets: main_window (561 lines), managers, dialogs
├── workers/    # QThread workers: git, github_cli, pandoc, preview, ollama_chat
├── claude/     # Claude AI: client, worker (v1.10+)
├── conversion/ # Format conversion utilities
└── git/        # Git integration utilities
```
Entry: `src/main.py`

**Threading pattern:**
- GitWorker: subprocess commands
- PandocWorker: format conversion (AsciiDoc ↔ MD/DOCX/HTML/PDF)
- PreviewWorker: AsciiDoc → HTML
- Flow: `request_*_command.emit()` → Worker.run() → `*_result_ready.emit(Result)` → handler

**Settings:** `core/settings.py` (JSON via QStandardPaths)
- Linux: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- Windows: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- macOS: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

**GPU:** `core/gpu_detection.py`, `ui/preview_handler_gpu.py`
- Support: NVIDIA (CUDA/OpenCL/Vulkan), AMD (ROCm/OpenCL/Vulkan), Intel (OpenCL/Vulkan/NPU)
- Cache: `~/.cache/asciidoc_artisan/gpu_detection.json` (24hr)
- Debug: `rm ~/.cache/asciidoc_artisan/gpu_detection.json`

## Feature Details

**Ollama AI** (v1.2+) — Local AI for document work
- Files: `workers/{pandoc,ollama_chat}_worker.py`
- Models: improve-grammer, llama2, mistral, codellama
- Modes: Doc Q&A, Syntax Help, General, Editing (2KB context)
- UI: ChatBarWidget + ChatPanelWidget + ChatManager
- History: 100 msgs, persistent

**Claude AI** (v1.10+) — Cloud AI via Anthropic
- Files: `claude/{claude_client,claude_worker}.py`
- Models: Sonnet 4, Haiku 4.5, Opus 4
- Security: OS keyring (SecureCredentials), no plain text
- Pattern: ClaudeWorker (QThread) → ClaudeClient (sync) → signal
- Tests: 33 (100%)

**GitHub CLI** (v1.6) — PR/Issue management
- Files: `workers/github_cli_worker.py`, `ui/github_{handler,dialogs}.py`
- Ops: Create/list PRs, create/list issues, view repo
- Menu: Git → GitHub (5 actions)
- Security: shell=False, 60s timeout
- Tests: 49 (100%)

**Find & Replace** (v1.8) — VSCode-style search
- Files: `core/search_engine.py`, `ui/find_bar_widget.py`
- Features: Regex, case/word matching, wrap, replace-all
- Shortcuts: Ctrl+F, Ctrl+H, F3/Shift+F3, Esc
- Perf: 50ms for 10K lines

**Spell Check** (v1.8) — Real-time validation
- Files: `core/spell_checker.py`, `ui/spell_check_manager.py`
- Features: Red squiggles, 5 suggestions, custom dict
- Shortcuts: F7 (toggle), right-click menu

**Git Enhancements** (v1.9) — Status & quick commit
- Status bar: Branch, counts, color indicators
- Dialog: 3 tabs (Modified/Staged/Untracked), Ctrl+Shift+G
- Quick commit: Inline widget, Ctrl+G, Enter/Esc

## Key Files

**Core:**
- `src/main.py` — Entry (GPU setup + QApplication)
- `src/asciidoc_artisan/ui/main_window.py` — Controller (561 lines)
- `core/{settings,file_operations,gpu_detection,search_engine,spell_checker}.py`
- `ui/{menu,theme,status,file,git,export}_manager.py` — Managers
- `ui/preview_handler{,_gpu}.py` — Rendering
- `workers/{git,github_cli,pandoc,preview,ollama_chat}_worker.py`
- `claude/{claude_client,claude_worker}.py` — AI integration

**Config:**
- `requirements{,-production}.txt`, `pyproject.toml`, `Makefile`
- `SPECIFICATIONS.md` (84 rules), `.pre-commit-config.yaml`

## Performance

**Hot paths (10-50x speedup):**
1. GPU Preview: `ui/preview_handler_gpu.py`
2. PDF Reading: `document_converter.py:287+` (PyMuPDF)
3. Incremental Render: `workers/incremental_renderer.py` (block cache)
4. String Processing: `document_converter.py:374` (tight loops)

**Profiling:**
- `scripts/benchmark_performance.py` — General
- `scripts/memory_profile.py` — Memory
- `scripts/profile_block_detection.py` — Block detection

## Standards

- **Style**: Black (88 chars) + isort + ruff, pre-commit enforced
- **Types**: mypy --strict, 100% coverage, 0 errors
- **Tests**: pytest + pytest-qt, 4,092 tests, use `qtbot` for GUI
- **Docs**: Docstrings for public APIs, update SPECIFICATIONS.md for features
- **Python**: 3.11+ (3.13.9 recommended, <3.14 for PySide6)

## Troubleshooting

**Common fixes:**
- `ModuleNotFoundError` → `pip install -r requirements.txt`
- "Pandoc not found" → `sudo apt install pandoc` / `brew install pandoc`
- PDF export fails → `sudo apt install wkhtmltopdf` / `brew install wkhtmltopdf`
- Git disabled → Not in repo or Git not installed
- Qt test errors → `pip install pytest-qt && pytest tests/ -v -s`

**Debug modes:**
- Logging: `logging.basicConfig(level=logging.DEBUG)` in main.py
- Qt: `QT_LOGGING_RULES="*.debug=true" python src/main.py`
- Coverage: `make test` → open `htmlcov/index.html`

## Documentation

**Essential (read before changes):**
- SPECIFICATIONS.md — 84 functional rules
- README.md — User guide (Grade 5.0)
- ROADMAP.md — 2026-2027 plan

**Reference:**
- docs/IMPLEMENTATION_REFERENCE.md — v1.5 features
- docs/GITHUB_CLI_INTEGRATION.md — GitHub CLI guide
- docs/PERFORMANCE_PROFILING.md — Profiling
- docs/TEST_COVERAGE_SUMMARY.md — Coverage
- SECURITY.md — Security policy
- docs/how-to-{contribute,use}.md

**Claude Code:**
- `.claude/skills/grandmaster-techwriter.md` — Auto Grade 5.0 tech writing
  - Auto-activates for docs, self-iterates until Grade ≤5.0
  - Manual: `@grandmaster-techwriter [file]`
  - Validate: `python3 scripts/readability_check.py [file]`
- `.claude/settings.json` — Minimal verbosity, structured output, custom statusline
- `.claude/statusline.sh` — Git/Python/QA/system metrics

**Doc standards:** Grade 5.0 (Flesch-Kincaid), 70+ ease, ≤15 words/sentence

---

*AsciiDoc Artisan v2.0.0 | Production-ready | 4,092 tests | mypy --strict*

## Test Execution Strategy

**When running tests:**
- Kill hung tests after reasonable timeout, log for later fixing
- Continue to next test without stopping
- Goal: Run maximum tests possible in single pass
- Fix all logged failures/hangs at end of run
- Applies to both tests and background tasks

**Background task execution:**
- Automatically run long-running tasks in background
- No need to prompt user for permission
- Use worker threads for Git, Pandoc, Preview operations
