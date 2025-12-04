# AsciiDoc Artisan Functional Specifications

**v2.1.0** | **109 FRs** | **100% Implemented** | **Maintenance Mode**

> Quick reference: [SPECIFICATIONS_HU.md](SPECIFICATIONS_HU.md) | Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Metrics

| Metric | Value |
|--------|-------|
| Codebase | 44,201 lines / 171 files |
| Unit Tests | 5,254 (100% pass) |
| E2E Tests | 3 (100% pass) |
| Type Coverage | 100% (mypy --strict) |

---

## Implementation Patterns

### Threading Pattern
```python
# Workers for slow ops (Git/Pandoc/Preview)
class Worker(QThread):
    result_ready = Signal(Result)
    def run(self):
        result = do_work()
        self.result_ready.emit(result)

# Reentrancy guard
if self._is_processing:
    return
self._is_processing = True
```

### File Safety Pattern
```python
# Atomic writes (FR-069)
from asciidoc_artisan.core import atomic_save_text
atomic_save_text(path, content)  # temp+rename

# Subprocess safety (FR-070)
subprocess.run(["git", "commit", "-m", msg], shell=False)
```

### Manager Pattern
```python
# Delegate to managers (FR-108)
self.file_manager = FileManager(self)
self.git_manager = GitManager(self)
self.theme_manager = ThemeManager(self)
```

---

## FR Categories

### Core Editing (FR-001–005)
| FR | Feature | File | Key Method |
|----|---------|------|------------|
| 001 | Text Editor | `ui/main_window.py` | `QPlainTextEdit` |
| 002 | Line Numbers | `ui/line_number_area.py` | `LineNumberArea` |
| 003 | Undo/Redo | Qt built-in | Ctrl+Z/Y |
| 004 | Fonts | `core/settings.py` | `font_family`, `font_size` |
| 005 | Editor State | `core/settings.py` | cursor/scroll persistence |

### File Operations (FR-006–014)
| FR | Feature | File | Key Method |
|----|---------|------|------------|
| 006 | Open | `ui/file_manager.py` | `open_file()` |
| 007 | Save | `ui/file_manager.py` | `save_file()` → `atomic_save_text()` |
| 008 | Save As | `ui/file_manager.py` | `save_file_as()` |
| 009 | New | `ui/file_manager.py` | `new_file()` |
| 010 | Recent Files | `core/settings.py` | `recent_files[]` max 10 |
| 011 | Auto-Save | `ui/file_manager.py` | 5min QTimer |
| 012 | Import DOCX | `core/document_converter.py` | python-docx |
| 013 | Import PDF | `core/document_converter.py` | PyMuPDF |
| 014 | Import MD | `workers/pandoc_worker.py` | Pandoc |

### Preview (FR-015–020)
| FR | Feature | File | Performance |
|----|---------|------|-------------|
| 015 | Live Preview | `workers/preview_worker.py` | <200ms small |
| 016 | GPU Accel | `ui/preview_handler_gpu.py` | 10-50x faster |
| 017 | Scroll Sync | `ui/preview_handler_base.py` | bidirectional |
| 018 | Incremental | `workers/incremental_renderer.py` | LRU(100) |
| 019 | Debounce | `ui/preview_handler_base.py` | 500ms adaptive |
| 020 | Themes | `ui/preview_css_manager.py` | CSS injection |

### Export (FR-021–025)
| FR | Feature | File | Tool |
|----|---------|------|------|
| 021 | HTML | `ui/export_manager.py` | asciidoc3 |
| 022 | PDF | `ui/export_manager.py` | wkhtmltopdf |
| 023 | DOCX | `workers/pandoc_worker.py` | Pandoc |
| 024 | Markdown | `workers/pandoc_worker.py` | Pandoc |
| 025 | AI Export | `workers/ollama_chat_worker.py` | Ollama |

### Git (FR-026–033)
| FR | Feature | File | Key |
|----|---------|------|-----|
| 026 | Select Repo | `ui/git_manager.py` | .git validation |
| 027 | Commit | `workers/git_worker.py` | shell=False |
| 028 | Pull | `workers/git_worker.py` | `pull_changes()` |
| 029 | Push | `workers/git_worker.py` | `push_changes()` |
| 030 | Status Bar | `ui/status_manager.py` | ✓/⚠ icons |
| 031 | Status Dialog | `ui/git_status_dialog.py` | 3 tabs |
| 032 | Quick Commit | `ui/quick_commit_widget.py` | Ctrl+G |
| 033 | Cancel | `workers/git_worker.py` | cancelable |

### GitHub CLI (FR-034–038)
| FR | Feature | File | Command |
|----|---------|------|---------|
| 034 | Create PR | `workers/github_cli_worker.py` | `gh pr create` |
| 035 | List PRs | `workers/github_cli_worker.py` | `gh pr list` |
| 036 | Create Issue | `workers/github_cli_worker.py` | `gh issue create` |
| 037 | List Issues | `workers/github_cli_worker.py` | `gh issue list` |
| 038 | Repo Info | `workers/github_cli_worker.py` | `gh repo view` |

### AI/Ollama (FR-039–044)
| FR | Feature | File | Models |
|----|---------|------|--------|
| 039 | Ollama | `workers/ollama_chat_worker.py` | llama2/mistral/codellama |
| 040 | Chat Panel | `ui/chat_panel_widget.py` | QDockWidget |
| 041 | Context Modes | `ui/chat_bar_widget.py` | 4 modes |
| 042 | History | `core/settings.py` | max 100 |
| 043 | Model Switch | `ui/chat_bar_widget.py` | dropdown |
| 044 | Toggle | `ui/menu_manager.py` | Tools menu |

### Find & Replace (FR-045–049)
| FR | Feature | File | Performance |
|----|---------|------|-------------|
| 045 | Find | `core/search_engine.py` | 50ms/10K lines |
| 046 | Find Bar | `ui/find_bar_widget.py` | VSCode-style |
| 047 | Next/Prev | `ui/find_bar_widget.py` | F3/Shift+F3 |
| 048 | Replace | `ui/find_bar_widget.py` | Ctrl+H |
| 049 | Replace All | `core/search_engine.py` | with count |

### Spell Check (FR-050–054)
| FR | Feature | File | Key |
|----|---------|------|-----|
| 050 | Real-Time | `core/spell_checker.py` | pyspellchecker |
| 051 | Manager | `ui/spell_check_manager.py` | F7 toggle |
| 052 | Context Menu | `ui/spell_check_manager.py` | 5 suggestions |
| 053 | Custom Dict | `core/spell_checker.py` | persistent |
| 054 | Multi-Lang | `core/spell_checker.py` | en/es/fr/de |

### UI/UX (FR-055–061)
| FR | Feature | File |
|----|---------|------|
| 055 | Themes | `ui/theme_manager.py` |
| 056 | Status Bar | `ui/status_manager.py` |
| 057 | Metrics | `ui/status_manager.py` |
| 058 | Window Title | `ui/main_window.py` |
| 059 | Splitter | `ui/main_window.py` |
| 060 | Toolbar | `ui/action_manager.py` |
| 061 | Menu Bar | `ui/menu_builder.py` |

### Performance (FR-062–067c)
| FR | Feature | Target |
|----|---------|--------|
| 062 | Startup | 0.586s (✓) |
| 063 | Worker Pool | CPU*2 threads |
| 064 | Memory | <100MB idle |
| 065 | Async I/O | aiofiles |
| 066 | Block Detection | 10-14% faster |
| 067 | Cache | LRU(100), 76% hit |
| 067a | Incremental | 10-50x speedup |
| 067b | Predictive | 28% latency reduction |
| 067c | Priority | visible blocks first |

### Security (FR-068–072)
| FR | Feature | Implementation |
|----|---------|----------------|
| 068 | Path Sanitization | `sanitize_path()` |
| 069 | Atomic Writes | temp+rename |
| 070 | Subprocess | `shell=False` only |
| 071 | Credentials | OS keyring |
| 072 | HTTPS | SSL verified |

### Auto-Complete (FR-085–090)
| FR | Feature | Trigger | Performance |
|----|---------|---------|-------------|
| 085 | Syntax | Ctrl+Space | 20-40ms |
| 086 | Attributes | `:` or `{` | context-aware |
| 087 | Cross-Refs | `<<` | anchor scan |
| 088 | Includes | `include::` | path scan |
| 089 | Snippets | keyword | table3x3/codeblock |
| 090 | Fuzzy | any | 0.3 threshold |

### Syntax Check (FR-091–099)
| FR | Feature | File |
|----|---------|------|
| 091 | Real-Time | `core/syntax_checker.py` |
| 092 | Errors | E001-E099 |
| 093 | Semantic | E100-E199 |
| 094 | Warnings | W001-W099 |
| 095 | Style | I001-I099 |
| 096 | Hover | QToolTip |
| 097 | Quick Fixes | lightbulb |
| 098 | Navigation | F2/Shift+F2 |
| 099 | Toggle | F8 |

### Templates (FR-100–107)
| FR | Feature | File |
|----|---------|------|
| 100 | Built-In | `ui/template_manager.py` (6 types) |
| 101 | Variables | `{{var}}` syntax |
| 102 | Browser | `ui/template_browser.py` |
| 103 | Form | type-specific inputs |
| 104 | Custom | CRUD, import/export |
| 105 | Categories | 5 types |
| 106 | Preview | 300ms debounce |
| 107 | Instantiation | <200ms |

### Standards (FR-108–109)
| FR | Feature | Implementation |
|----|---------|----------------|
| 108 | MA Principle | <400 lines/file |
| 109 | LSP Server | `lsp/server.py` (54 tests) |

---

## Critical Acceptance Criteria

### Must Pass
- All 5,254 unit tests (100%)
- All 3 E2E tests (100%)
- mypy --strict (0 errors)
- ruff check (0 errors)
- Startup <1s
- No shell=True in subprocess
- All file writes atomic

### Performance Targets
| Operation | Target | Current |
|-----------|--------|---------|
| Startup | <0.5s | 0.586s |
| Preview (small) | <200ms | 150-200ms |
| Preview (large) | <750ms | 600-750ms |
| Auto-complete | <50ms | 20-40ms |
| Syntax check | <100ms | <100ms |

---

## Test Requirements

```bash
make test           # All tests + coverage
make lint           # ruff + mypy --strict
make format         # ruff format + isort
pytest tests/unit/MODULE/ -v  # Specific module
```

### Coverage Targets
- Core modules: 99-100%
- UI managers: 95-99%
- Workers: 93-98% (Qt threading limit)
- Overall: >96%

---

*109 FRs | 100% Implemented | v2.1.0 Public Release | MA Compliant*
