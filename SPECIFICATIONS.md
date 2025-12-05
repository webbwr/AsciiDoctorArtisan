# AsciiDoc Artisan Specifications

**v2.1.0** | **109 FRs** | **100% Implemented** | **Maintenance Mode**

---

## Metrics

| Metric | Value |
|--------|-------|
| Codebase | 46,457 lines / 180 files |
| Unit Tests | 5,122 (100% pass) |
| E2E Tests | 17 (100% pass) |
| Type Coverage | 100% (mypy --strict) |
| Startup | 0.27s |

---

## Patterns

```python
# Threading (FR-027+)
class Worker(QThread):
    result_ready = Signal(Result)
    def run(self):
        self.result_ready.emit(do_work())

# Reentrancy guard
if self._is_processing: return
self._is_processing = True

# Atomic writes (FR-069)
atomic_save_text(path, content)

# Subprocess safety (FR-070)
subprocess.run(["git", "commit", "-m", msg], shell=False)

# Manager delegation (FR-108)
self.file_manager = FileManager(self)
```

---

## FR Reference

### Core (001–005)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 001 | Editor | `ui/main_window.py` | QPlainTextEdit |
| 002 | Line Numbers | `ui/line_number_area.py` | 8 tests |
| 003 | Undo/Redo | Qt built-in | Ctrl+Z/Y |
| 004 | Fonts | `core/settings.py` | Monospace 10pt |
| 005 | State | `core/settings.py` | cursor/scroll |

### Files (006–014)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 006 | Open | `ui/file_manager.py` | Ctrl+O |
| 007 | Save | `ui/file_manager.py` | atomic, 15 tests |
| 008 | Save As | `ui/file_manager.py` | Ctrl+Shift+S |
| 009 | New | `ui/file_manager.py` | Ctrl+N |
| 010 | Recent | `core/settings.py` | max 10 |
| 011 | Auto-Save | `ui/file_manager.py` | 5min |
| 012 | DOCX | `core/document_converter.py` | python-docx |
| 013 | PDF | `core/document_converter.py` | PyMuPDF |
| 014 | Markdown | `workers/pandoc_worker.py` | Pandoc |

### Preview (015–020)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 015 | Live | `workers/preview_worker.py` | <200ms |
| 016 | GPU | `ui/preview_handler_gpu.py` | 10-50x |
| 017 | Sync | `ui/preview_handler_base.py` | 8 tests |
| 018 | Incremental | `workers/incremental_renderer.py` | LRU(100) |
| 019 | Debounce | `ui/preview_handler_base.py` | 500ms |
| 020 | Themes | `ui/preview_css_manager.py` | CSS |

### Export (021–025)
| FR | Feature | File | Tool |
|----|---------|------|------|
| 021 | HTML | `ui/export_manager.py` | asciidoc3 |
| 022 | PDF | `ui/export_manager.py` | wkhtmltopdf |
| 023 | DOCX | `workers/pandoc_worker.py` | Pandoc |
| 024 | Markdown | `workers/pandoc_worker.py` | Pandoc |
| 025 | AI | `workers/ollama_chat_worker.py` | Ollama |

### Git (026–033)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 026 | Repo | `ui/git_manager.py` | .git check |
| 027 | Commit | `workers/git_worker.py` | shell=False |
| 028 | Pull | `workers/git_worker.py` | 8 tests |
| 029 | Push | `workers/git_worker.py` | |
| 030 | Status | `ui/status_manager.py` | ✓/⚠ icons |
| 031 | Dialog | `ui/git_status_dialog.py` | 3 tabs |
| 032 | Quick | `ui/quick_commit_widget.py` | Ctrl+G |
| 033 | Cancel | `workers/git_worker.py` | cancelable |

### GitHub (034–038)
| FR | Feature | File | Command |
|----|---------|------|---------|
| 034 | PR Create | `workers/github_cli_worker.py` | gh pr create |
| 035 | PR List | `workers/github_cli_worker.py` | gh pr list |
| 036 | Issue Create | `workers/github_cli_worker.py` | gh issue create |
| 037 | Issue List | `workers/github_cli_worker.py` | gh issue list |
| 038 | Repo Info | `workers/github_cli_worker.py` | gh repo view |

### AI (039–044)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 039 | Ollama | `workers/ollama_chat_worker.py` | 82 tests |
| 040 | Panel | `ui/chat_panel_widget.py` | |
| 041 | Modes | `ui/chat_bar_widget.py` | 4 modes |
| 042 | History | `core/settings.py` | max 100 |
| 043 | Model | `ui/chat_bar_widget.py` | dropdown |
| 044 | Toggle | `ui/menu_manager.py` | Tools |

### Find (045–049)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 045 | Search | `core/search_engine.py` | 33 tests |
| 046 | Bar | `ui/find_bar_widget.py` | 21 tests |
| 047 | Nav | `ui/find_bar_widget.py` | F3 |
| 048 | Replace | `ui/find_bar_widget.py` | Ctrl+H |
| 049 | All | `core/search_engine.py` | count |

### Spell (050–054)
| FR | Feature | File | Notes |
|----|---------|------|-------|
| 050 | Check | `core/spell_checker.py` | pyspellchecker |
| 051 | Manager | `ui/spell_check_manager.py` | F7 |
| 052 | Menu | `ui/spell_check_manager.py` | 5 suggestions |
| 053 | Dict | `core/spell_checker.py` | persistent |
| 054 | Lang | `core/spell_checker.py` | en/es/fr/de |

### UI (055–061)
| FR | Feature | File |
|----|---------|------|
| 055 | Themes | `ui/theme_manager.py` |
| 056 | Status | `ui/status_manager.py` |
| 057 | Metrics | `ui/status_manager.py` |
| 058 | Title | `ui/main_window.py` |
| 059 | Splitter | `ui/main_window.py` |
| 060 | Toolbar | `ui/action_manager.py` |
| 061 | Menu | `ui/menu_builder.py` |

### Perf (062–067c)
| FR | Feature | Target |
|----|---------|--------|
| 062 | Startup | 0.586s |
| 063 | Pool | CPU*2 |
| 064 | Memory | <100MB |
| 065 | Async | aiofiles |
| 066 | Blocks | 10-14% |
| 067 | Cache | 76% hit |
| 067a | Incremental | 10-50x |
| 067b | Predictive | 28% |
| 067c | Priority | visible |

### Security (068–072)
| FR | Feature | Implementation |
|----|---------|----------------|
| 068 | Path | `sanitize_path()` |
| 069 | Atomic | temp+rename |
| 070 | Subprocess | shell=False |
| 071 | Creds | OS keyring |
| 072 | HTTPS | SSL |

### Infra (073–084)
| FR | Feature | Notes |
|----|---------|-------|
| 073 | Telemetry | opt-in |
| 074 | Settings | JSON/Pydantic |
| 075 | Types | mypy --strict |
| 076 | Tests | 96.4% |
| 077 | Pre-commit | ruff |
| 078 | Docs | Grade 5.0 |
| 079 | A11y | keyboard |
| 080 | Recovery | auto-save |
| 081 | Version | auto |
| 082 | Monitor | psutil |
| 083 | Large | 10MB chunk |
| 084 | LRU | 100 blocks |

### Autocomplete (085–090)
| FR | Feature | Trigger | Perf |
|----|---------|---------|------|
| 085 | Syntax | Ctrl+Space | 20-40ms |
| 086 | Attrs | `:` `{` | |
| 087 | Xrefs | `<<` | |
| 088 | Include | `include::` | |
| 089 | Snippets | keyword | |
| 090 | Fuzzy | any | 0.3 |

### Syntax (091–099)
| FR | Feature | Notes |
|----|---------|-------|
| 091 | Real-Time | <100ms |
| 092 | Errors | E001-E099 |
| 093 | Semantic | E100-E199 |
| 094 | Warnings | W001-W099 |
| 095 | Style | I001-I099 |
| 096 | Hover | QToolTip |
| 097 | Fixes | lightbulb |
| 098 | Nav | F2 |
| 099 | Toggle | F8 |

### Templates (100–107)
| FR | Feature | Notes |
|----|---------|-------|
| 100 | Built-In | 6 types |
| 101 | Vars | `{{var}}` |
| 102 | Browser | Ctrl+Shift+N |
| 103 | Form | inputs |
| 104 | Custom | CRUD |
| 105 | Categories | 5 types |
| 106 | Preview | 300ms |
| 107 | Create | <200ms |

### Standards (108–109)
| FR | Feature | Notes |
|----|---------|-------|
| 108 | MA | <400 lines |
| 109 | LSP | 108 tests |

---

## Acceptance

**Must Pass:**
- 5,196 unit + 3 E2E tests (100%)
- mypy --strict (0 errors)
- No shell=True
- Atomic writes only

**Performance:**
| Op | Target | Current |
|----|--------|---------|
| Startup | <0.5s | 0.27s ✅ |
| Preview | <200ms | 150-200ms ✅ |
| Complete | <50ms | 20-40ms ✅ |

---

*v2.1.0 | 109 FRs | MA Compliant | Dec 5, 2025*
