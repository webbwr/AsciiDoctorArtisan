# Changelog

## [2.1.0] - 2025-12-05 - Public Release

**First production-stable release with S-tier code quality**

### Added
- LSP Server (completion, diagnostics, hover, symbols)
- Multi-core rendering (2-4x speedup)
- Claude AI integration (Anthropic API client + worker)
- Architecture documentation with FR mapping
- Comprehensive API reference documentation
- User guide with keyboard shortcuts
- **TOON format** for settings (30-60% smaller than JSON)
  - Automatic migration from JSON to TOON
  - Human-readable, LLM-optimized format

### Changed
- S-tier MA compliance: 100% of 195 files under 400 lines
- Deprecated `datetime.utcnow()` → `datetime.now(timezone.utc)`
- Improved test isolation with tmp_path fixtures
- Settings format migration: .json → .toon

### Testing
- Integration tests for export, settings, worker coordination
- E2E workflow tests (file operations, settings, search, export)
- 98% core test coverage
- All 109 Functional Requirements mapped to tests

### Documentation
- docs/API_REFERENCE.md - Complete public API
- docs/USER_GUIDE.md - End-user documentation
- docs/ARCHITECTURE.md - System design
- SPECIFICATIONS.md - 109 FRs with file locations

### Metrics
- 46,457 lines / 180 files
- 5,628 unit + 17 E2E tests (95% coverage)
- mypy --strict (0 errors)
- Startup: 0.27s
- Core imports: 90ms
- Memory baseline: 12.5MB

---

## [2.0.0] - 2025-11-09 - Advanced Editing

### Added
- Auto-complete (20-40ms, Ctrl+Space)
- Syntax checking (real-time, quick fixes)
- Templates (6 built-in + custom)

### Performance
- Startup: 0.27s

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
