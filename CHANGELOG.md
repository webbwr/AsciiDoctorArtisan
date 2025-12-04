# Changelog

## [2.1.0] - 2025-12-03 - Public Release

**First production-stable release**

### Added
- LSP Server (completion, diagnostics, hover, symbols)
- Multi-core rendering (2-4x speedup)
- Architecture documentation with FR mapping

### Metrics
- 44,201 lines / 171 files
- 5,254 unit + 71 E2E tests
- mypy --strict (0 errors)

---

## [2.0.0] - 2025-11-09 - Advanced Editing

### Added
- Auto-complete (20-40ms, Ctrl+Space)
- Syntax checking (real-time, quick fixes)
- Templates (6 built-in + custom)

### Performance
- Startup: 0.586s (46% faster)

---

## [1.9.0] - 2025-11-03 - Git UX

- Git status in status bar
- Status dialog (Ctrl+Shift+G)
- Quick commit (Ctrl+G)

## [1.8.0] - 2025-11-02 - Essential Features

- Find & Replace (Ctrl+F, Ctrl+H)
- Spell Check (F7)
- Theme toggle (F11)
- Telemetry (opt-in)

## [1.7.0] - 2025-11-01 - AI Chat

- Ollama chat (4 modes)
- Chat panel with history
- Document context injection

## [1.6.0] - 2025-10-31 - Type Safety

- GitHub CLI (PRs, issues)
- 100% type hints (mypy --strict)
- Async I/O

## [1.5.0] - 2025-10-28 - Performance

- 1.05s startup (lazy imports)
- Worker pool with priorities
- 67% code reduction

## [1.4.0] - 2025-10-15 - GPU

- GPU acceleration (10-50x faster)
- Auto-detection (NVIDIA/AMD/Intel)
- 24hr detection cache

## [1.2.0] - 2025-08-15 - AI

- Ollama AI conversion
- Pandoc fallback

## [1.0.0] - 2025-06-01 - Initial

- Live preview
- Theme support
- Git integration
- Document conversion

---

*[Full history in git log]*
