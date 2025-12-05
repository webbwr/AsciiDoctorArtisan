# AsciiDoc Artisan Roadmap

**v2.1.0** | **Dec 4, 2025** | **Public Release** | **Maintenance Mode**

---

## Version History

| Version | Date | Focus |
|---------|------|-------|
| v1.5.0 | Oct 2025 | Performance (1.05s startup, worker pool) |
| v1.6.0 | Oct 2025 | Type Safety (100% hints, GitHub CLI) |
| v1.7.0 | Nov 2025 | AI Chat (Ollama, 4 modes) |
| v1.8.0 | Nov 2025 | Find/Replace, Spell Check |
| v1.9.0 | Nov 2025 | Git UX (status dialog, quick commit) |
| v2.0.0 | Nov 8-9 | Advanced Editing (autocomplete, syntax check, templates) |
| v2.0.1-8 | Nov 13-21 | Test stabilization, coverage improvements |
| v2.0.9 | Dec 3 | LSP, multi-core rendering, MA refactoring |
| v2.1.0 | Dec 3 | **Public Release** |

---

## Current State (v2.1.0)

| Metric | Value |
|--------|-------|
| Codebase | 45,677 lines / 373 files |
| Unit Tests | 5,196 (100% pass) |
| E2E Tests | 71 (100% pass) |
| Type Coverage | 100% (mypy --strict) |
| Startup | 0.586s |

### Features
- ✅ LSP Server (8 providers: completion, diagnostics, hover, symbols, code actions, folding, formatting, semantic tokens)
- ✅ Multi-core rendering (2-4x speedup)
- ✅ Auto-complete (<50ms, fuzzy matching)
- ✅ Syntax Check (real-time, quick fixes)
- ✅ Templates (6 built-in + custom)
- ✅ AI Chat (Ollama, 4 modes)
- ✅ Find/Replace (regex, VSCode-style)
- ✅ Spell Check (real-time, multi-lang)
- ✅ Git (status dialog, quick commit)
- ✅ GitHub CLI (PRs, issues)
- ✅ GPU rendering (10-50x faster)

### Architecture
- Manager Pattern: UI split into specialized managers
- Worker Threads: QThread for Git/Pandoc/Preview
- MA Principle: <400 lines/file, focused modules
- Security: shell=False, atomic writes, path sanitization

---

## Performance Budget

| Metric | Current | Target |
|--------|---------|--------|
| Startup | 0.586s ✅ | <0.5s |
| Preview (small) | 150-200ms | 80-120ms |
| Preview (large) | 600-750ms | 300-500ms |
| Auto-complete | 20-40ms ✅ | <25ms |
| Syntax Check | <100ms ✅ | <50ms |

---

## Future (Deferred)

**v3.0.0** - No planned features. Current v2.x is feature-complete.

**Rationale:** v2.x includes all planned LSP features (code actions, folding, formatting, semantic tokens). Maintenance mode only.

---

## Out of Scope

These features are explicitly not planned:
- Plugin architecture
- Plugin marketplace
- Collaborative editing
- Cloud sync

**Rationale:** AsciiDoc Artisan is a focused local-first editor. These features add complexity without serving the core use case.

---

## Test Coverage Notes

- **Maximum achievable:** ~99.5% (Qt threading prevents 100%)
- **Qt limitation:** coverage.py cannot track QThread.run()/QRunnable execution
- **Current:** 96.4% overall, 93-100% per module

---

*v2.1.0 | Production-ready | Maintenance mode*
