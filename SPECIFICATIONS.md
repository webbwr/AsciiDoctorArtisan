# AsciiDoc Artisan Specifications

**v2.1.0** | **109 FRs** | **Specification-Driven Coding**

---

## Document Structure

| Marker | Purpose | Audience |
|--------|---------|----------|
| `[CONTEXT]` | Rationale, decisions | Human readers |
| `[SPEC]` | Machine-parseable requirements | AI assistants |
| `[VALIDATE]` | Acceptance criteria | Both |

**Related Docs:**
- [SCHEMAS.md](docs/SCHEMAS.md) — Pydantic model definitions
- [SIGNALS.md](docs/SIGNALS.md) — Qt signal/slot contracts

---

## [CONTEXT] Overview

Desktop AsciiDoc editor with live preview (PySide6/Qt).

**Principles:**
- Handler Architecture: No file >400 lines
- Thread Safety: QThread for slow operations
- Atomic Operations: temp+rename file writes
- Type Safety: mypy --strict compliance

**Stack:** PySide6 6.9+, Python 3.11+, asciidoc3, pypandoc, pymupdf

---

## [SPEC] Metrics

```yaml
version: 2.1.0
release_date: 2025-12-05

codebase:
  lines: 45900
  files: 180

testing:
  unit_tests: 5122
  e2e_tests: 17
  coverage: 95%

performance:
  startup: 0.27s
  preview: <200ms
  autocomplete: 20-40ms
```

---

## [SPEC] Critical Patterns

### Threading

```python
# All slow ops use QThread
class Worker(QThread):
    result_ready = Signal(Result)

    def run(self) -> None:
        if self._cancelled:
            return
        result = self._do_work()
        self.result_ready.emit(result)
```

### Reentrancy Guard

```python
def start_operation(self) -> None:
    if self._is_processing:
        return
    self._is_processing = True
    try:
        # ... operation ...
    finally:
        self._is_processing = False
```

### Atomic Write

```python
from asciidoc_artisan.core.file_operations import atomic_save_text
atomic_save_text(path, content)  # temp + rename
```

### Subprocess Safety

```python
# ALWAYS shell=False
subprocess.run(["git", "commit", "-m", msg], shell=False)
# NEVER: subprocess.run(f"git commit -m {msg}", shell=True)
```

---

## [SPEC] Directory Structure

```
src/asciidoc_artisan/
├── core/       # Domain logic (no Qt UI)
├── ui/         # Qt widgets, handlers
├── workers/    # QThread workers
├── claude/     # Claude AI
└── lsp/        # Language Server
```

---

## [SPEC] Functional Requirements

### Core Editor (FR-001 to FR-005)

| FR | Feature | File |
|----|---------|------|
| 001 | Text Editor | `ui/main_window.py` |
| 002 | Line Numbers | `ui/line_number_area.py` |
| 003 | Undo/Redo | Qt built-in |
| 004 | Font Config | `core/settings.py` |
| 005 | State Persist | `core/settings.py` |

### File Operations (FR-006 to FR-014)

| FR | Feature | Notes |
|----|---------|-------|
| 006 | Open File | Ctrl+O |
| 007 | Save File | Atomic write |
| 008 | Save As | Ctrl+Shift+S |
| 009 | New File | Ctrl+N |
| 010 | Recent Files | Max 10 |
| 011 | Auto-Save | 5-minute |
| 012-014 | Import | DOCX, PDF, Markdown |

### Live Preview (FR-015 to FR-020)

| FR | Feature | Performance |
|----|---------|-------------|
| 015 | Live Preview | <200ms |
| 016 | GPU Accel | 10-50x |
| 017 | Scroll Sync | Bidirectional |
| 018 | Incremental | LRU(100) |
| 019 | Debounce | 500ms |
| 020 | Themes | CSS injection |

### Export (FR-021 to FR-025)

| FR | Feature | Tool |
|----|---------|------|
| 021 | HTML | asciidoc3 |
| 022 | PDF | wkhtmltopdf |
| 023 | DOCX | Pandoc |
| 024 | Markdown | Pandoc |
| 025 | AI Assist | Ollama |

### Git (FR-026 to FR-033)

| FR | Feature | File |
|----|---------|------|
| 026 | Repo Detection | `ui/git_handler.py` |
| 027 | Commit | `workers/git_worker.py` |
| 028 | Pull | `workers/git_worker.py` |
| 029 | Push | `workers/git_worker.py` |
| 030-033 | Status/UI | Status bar, dialogs |

### GitHub CLI (FR-034 to FR-038)

| FR | Feature | Command |
|----|---------|---------|
| 034 | Create PR | gh pr create |
| 035 | List PRs | gh pr list |
| 036 | Create Issue | gh issue create |
| 037 | List Issues | gh issue list |
| 038 | Repo Info | gh repo view |

### AI (FR-039 to FR-044)

| FR | Feature | File |
|----|---------|------|
| 039 | Ollama | `workers/ollama_chat_worker.py` |
| 040 | Chat Panel | `ui/chat_panel_widget.py` |
| 041 | Chat Modes | 4 modes |
| 042 | History | Max 100 |
| 043-044 | Model/Toggle | Settings |

### Find & Spell (FR-045 to FR-054)

| FR | Feature |
|----|---------|
| 045-049 | Search Engine, Find Bar, Replace |
| 050-054 | Spell Check, Languages |

### UI & Performance (FR-055 to FR-067)

| FR | Feature | Target |
|----|---------|--------|
| 055-061 | Theme, Status, Menus | Full UI |
| 062 | Startup | <1.0s |
| 063 | Thread Pool | CPU x 2 |
| 064 | Memory | <100MB |
| 065-067 | Async, Cache | Optimized |

### Security (FR-068 to FR-072)

| FR | Feature |
|----|---------|
| 068 | Path Sanitization |
| 069 | Atomic Writes |
| 070 | Subprocess Safety |
| 071 | Credential Storage |
| 072 | HTTPS Only |

### Infrastructure (FR-073 to FR-109)

| FR | Feature |
|----|---------|
| 073-084 | Telemetry, Settings, Tests |
| 085-090 | Autocomplete (<50ms) |
| 091-099 | Syntax Check |
| 100-107 | Templates (6 built-in) |
| 108 | MA Compliance |
| 109 | LSP Protocol |

---

## [VALIDATE] Acceptance Criteria

```bash
# All must pass
make test                        # 5,139 tests
mypy --strict src/               # 0 errors
grep -r "shell=True" src/        # No matches
```

| Operation | Target |
|-----------|--------|
| Startup | <1.0s |
| Preview | <200ms |
| Autocomplete | <50ms |

---

## [CONTEXT] Architecture Decisions

**Why Handler Architecture?**
Original main_window.py exceeded 2,000 lines. Handlers split responsibilities into focused modules under 400 lines.

**Why QThread?**
PySide6 signal/slot threading integrates with Qt event loop. Workers communicate via signals.

**Why Atomic Writes?**
temp+rename ensures complete file or nothing—never partial writes.

---

*v2.1.0 | 109 FRs | Dec 5, 2025*
