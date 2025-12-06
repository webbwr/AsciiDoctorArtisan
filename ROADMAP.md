# AsciiDoc Artisan Roadmap

**v2.1.0** | **Dec 5, 2025** | **Public Release**

---

## Current State

| Metric | Value |
|--------|-------|
| Code | 46,457 lines / 180 files |
| Unit Tests | 5,628 |
| E2E Tests | 17 |
| Integration Tests | 17 |
| Coverage | 95% |
| Type Check | 100% (mypy --strict) |
| Startup | 0.27s |
| Storage | TOON format (30-60% smaller) |

---

## Features

| Category | Features |
|----------|----------|
| Editor | Live preview, GPU accelerated |
| Editing | Auto-complete, syntax check, spell check |
| Templates | 9 built-in + custom |
| Search | Find/replace with regex |
| Git | Commit, push, pull, status |
| GitHub | PRs, issues via CLI |
| AI | Ollama chat, Claude |
| Import | DOCX, PDF, Markdown, HTML |
| Export | HTML, PDF, DOCX, Markdown |
| LSP | 9 providers |
| Storage | TOON format (auto-migrates JSON) |
| Build | PyInstaller desktop installer |

---

## Version History

| Version | Date | Focus |
|---------|------|-------|
| v2.1.0 | Dec 5, 2025 | Public Release, TOON format |
| v2.0.9 | Dec 3, 2025 | LSP, multi-core rendering |
| v2.0.1-8 | Nov 13-21 | Test stabilization |
| v2.0.0 | Nov 8-9 | Autocomplete, syntax, templates |
| v1.9.0 | Nov 2025 | Git UX improvements |
| v1.8.0 | Nov 2025 | Find/Replace, Spell Check |
| v1.7.0 | Nov 2025 | AI Chat (Ollama) |
| v1.6.0 | Oct 2025 | Type Safety, GitHub CLI |
| v1.5.0 | Oct 2025 | Performance (worker pool) |

---

## Performance

| Operation | Target | Actual |
|-----------|--------|--------|
| Startup | <1.0s | 0.27s |
| Preview (small) | <200ms | 150ms |
| Preview (large) | <500ms | 400ms |
| Auto-complete | <50ms | 20-40ms |
| Syntax check | <100ms | <50ms |

---

## Architecture

| Principle | Implementation |
|-----------|----------------|
| MA Principle | <400 lines/file |
| Handler Pattern | UI logic in focused handlers |
| Worker Threads | QThread for slow operations |
| Security | shell=False, atomic writes |
| Storage | TOON format with JSON fallback |

---

## Future

**v3.0.0** — No planned features. v2.x is feature-complete.

**Maintenance mode:** Bug fixes only.

---

## Out of Scope

Not planned:
- Plugin architecture
- Plugin marketplace
- Collaborative editing
- Cloud sync

**Rationale:** Local-first editor. These add complexity without serving core use case.

---

## Test Coverage Notes

| Limit | Reason |
|-------|--------|
| Max 99% | Qt threading prevents 100% |
| Current | 95% overall |

coverage.py cannot track QThread.run() execution.

---

*v2.1.0 | Production-ready | Maintenance mode*
