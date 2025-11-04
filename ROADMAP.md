# AsciiDoc Artisan Development Roadmap
## 2026-2027 Strategic Plan

**Last Updated:** November 3, 2025
**Planning Horizon:** 18-24 months
**Status:** v1.5.0 ✅ | v1.6.0 ✅ | QA Initiative ✅ | **Phase 1 Optimization ✅** | **Phase 2 Optimization ✅** | **v1.7.0 ✅** | **v1.7.1 ✅** | **v1.7.2 ✅** | **v1.7.3 ✅** | **v1.8.0 ✅** | **v1.9.0 ✅ COMPLETE** (Improved Git Integration)

---

## Quick Reference

| Version | Status | Date | Focus | Key Features |
|---------|--------|------|-------|--------------|
| v1.5.0 | ✅ | Oct 2025 | Performance | 1.05s startup, worker pool, 67% code reduction |
| v1.6.0 | ✅ | Oct 2025 | Type Safety | 100% type hints, async I/O, GitHub CLI |
| v1.7.0 | ✅ | Nov 2025 | AI Chat | Ollama integration, 4 context modes |
| v1.8.0 | ✅ | Nov 2025 | Essential | Find/Replace, Spell Check, Telemetry |
| v1.9.0 | ✅ | Nov 2025 | Git UX | Status dialog, Quick Commit (Ctrl+G) |
| v2.0.0 | 📋 | Q2-Q3 2026 | Advanced Edit | Auto-complete, Syntax Check, Templates |
| v3.0.0 | 📋 | Q4 2026-Q2 2027 | Next-Gen | LSP, Plugins, Multi-core, Marketplace |

**Current Version:** v1.9.0 (November 3, 2025)
**Next Priority:** v2.0.0 Advanced Editing

---

## Table of Contents

1. [Vision & Principles](#vision-statement)
2. [Current State](#current-state-v190-)
3. [Completed Releases](#completed-releases)
4. [Planned Releases](#planned-releases)
   - [v2.0.0 Advanced Editing](#version-200-advanced-editing)
   - [v3.0.0 Next-Gen Architecture](#version-300-next-generation-architecture)
5. [Performance Budget](#performance-budget)
6. [Success Metrics](#success-metrics--kpis)
7. [Risk Management](#risk-management)

---

## Vision Statement

Transform AsciiDoc Artisan into the **definitive AsciiDoc editor** - combining exceptional performance, extensibility, and user experience to become the clear leader in technical document authoring.

**Core Principles:**
1. **Performance First** - Fast startup, responsive UI, efficient rendering
2. **MA** - Minimalism: conceptual simplicity, structural complexity achieves a greater state of humanity
3. **Extensibility** - Plugin architecture for community contributions
4. **Quality** - High test coverage, type safety, comprehensive documentation
5. **User-Centric** - Essential features, intuitive UX, accessibility

---

## Current State (v1.9.0) ✅

### Architecture Excellence
- **Modular design** with manager pattern (60+ source modules)
- **Main window:** 561 lines (down from 1,719 - 67% reduction in v1.5.0)
- **Clean separation** of concerns (core, ui, workers, git)

### Performance Achievements
- **Startup:** 1.05s (70-79% faster than v1.4.0)
- **GPU acceleration:** 10-50x faster rendering
- **Block detection:** 10-14% improvement
- **Predictive rendering:** 28% latency reduction

### Quality Metrics
- **Test coverage:** 60%+ current (Goal: 100% - CRITICAL priority)
- **Test suite:** 80 files, 1,500+ tests
- **Type hints:** 100% ✅ (mypy --strict: 0 errors, 64 files)
- **Tech debt:** LOW (<30% duplication)
- **Documentation:** Comprehensive

### Feature Completeness
- ✅ Async I/O implementation
- ✅ Incremental rendering with caching
- ✅ Memory profiling system (148.9% growth baseline documented)
- ✅ Block detection optimization
- ✅ Ollama AI Chat (4 context modes, persistent history)
- ✅ Find & Replace system (regex, collapsible UI)
- ✅ Spell checker integration (pyspellchecker)
- ✅ Telemetry system (opt-in, privacy-first)
- ✅ Improved Git integration (status dialog, quick commit, real-time status)

### Recent Achievements (Nov 2025)
- ✅ **v1.9.0**: Git workflow improvements (status dialog, quick commit, UI enhancements)
  - Git Status Dialog with file-level details (Ctrl+Shift+G)
  - Quick Commit Widget with inline commits (Ctrl+G)
  - Brief git status in status bar (color-coded: ✓ ● ⚠)
  - Chat pane toggle in Tools menu (keyboard-driven workflow)
- ✅ **v1.8.0**: Essential features (Find/Replace, Spell Check, Telemetry)
- ✅ **v1.7.0**: Ollama AI Chat with 4 context modes
- ✅ **100% Type Coverage**: mypy --strict: 0 errors across 64 files
- ✅ **Quality Score**: 97/100 (GRANDMASTER)

---

## Completed Releases

### Summary Table

| Version | Date | Key Achievements | Tests | Lines Changed |
|---------|------|------------------|-------|---------------|
| **v1.9.0** | Nov 3, 2025 | Git status dialog, Quick Commit (Ctrl+G), Real-time updates | 53 (97%) | +1,870 |
| **v1.8.0** | Nov 2, 2025 | Find/Replace, Spell Check, Telemetry, F11 theme toggle | 111 (100%) | +2,100 |
| **v1.7.3** | Nov 2, 2025 | AI model validation, Real-time status feedback | 10 (100%) | +150 |
| **v1.7.2** | Nov 2, 2025 | Undo/Redo toolbar buttons, State management | 38 (100%) | +615 |
| **v1.7.1** | Nov 2, 2025 | 100% test pass rate, Comprehensive docs | 82 (100%) | +770 |
| **v1.7.0** | Nov 1-2, 2025 | Ollama AI Chat, 4 context modes, History persistence | 82 (91%→100%) | +3,993 |
| **v1.6.0** | Oct 31, 2025 | 100% type hints, Async I/O, GitHub CLI integration | 49 (100%) | +1,200 |
| **v1.5.0** | Oct 28, 2025 | 1.05s startup, 67% code reduction, Worker pool | 621 (100%) | +817 |

### Highlights

**v1.9.0 - Improved Git Integration**
- Enhanced Git status display (real-time, color-coded)
- Git Status Dialog (file-level details, 3 tabs, Ctrl+Shift+G)
- Quick Commit Widget (inline commits, Ctrl+G, auto-stage)
- Brief git status in status bar (branch + indicator: ✓ clean, ●N changes, ⚠ conflicts)
- Chat pane toggle in Tools menu (alphabetically sorted, keyboard-accessible)
- GitStatus data model with Pydantic validation
- Real-time status updates (5-second refresh interval)

**v1.8.0 - Essential Features**
- Find & Replace (regex, collapsible UI, match counter)
- Spell Checker (red underlines, context menu, F7 toggle)
- Telemetry (opt-in, privacy-first, GDPR compliant)
- F11 keyboard shortcut for theme toggle

**v1.7.0 - AI Integration**
- Ollama AI Chat with 4 context modes
- Chat history persistence (100 messages)
- Model switching via dropdown
- Background worker (non-blocking UI)

**v1.6.0 - Type Safety & Async**
- 100% type hint coverage (mypy --strict: 0 errors)
- Async I/O complete (AsyncFileWatcher, QtAsyncFileManager)
- GitHub CLI integration (PR/Issue management)
- Block detection optimization (10-14% improvement)

**v1.5.0 - Performance & Refactoring**
- 1.05s startup (70-79% faster than v1.4.0)
- Main window: 1,719 → 561 lines (67% reduction)
- Worker pool system with task prioritization
- Operation cancellation (cancel button)
- Test coverage: 34% → 60%+

### Quality Assurance Initiative ✅

**Status:** COMPLETE (October 2025)
**Effort:** 142 hours over 10 weeks
**Score:** 82/100 → 97/100 (GRANDMASTER)

**5 Phases:**
1. Critical Fixes (20h) - Test pass rate: 91.5% → 100%
2. Coverage Push (38h) - Code coverage: 34% → 60%+
3. Quality Infrastructure (26h) - Automated quality gates
4. Performance Optimization (28h) - 15-20% performance gain
5. Continuous Improvement (30h) - Type coverage 100%, security automation

**Achievements:**
- ✅ 100% test pass rate (1,500+ tests)
- ✅ 60%+ code coverage (Goal: 100%)
- ✅ 100% type coverage
- ✅ Zero memory leaks
- ✅ Complete security automation

---

## Version 2.0.0 (Advanced Editing)

**Target:** Q2-Q3 2026 | **Effort:** 102-160h | **Status:** 📋 PLANNED

### Goals

Advanced editing features for power users and technical writers.

**Critical Features:**

1. **Auto-Complete** (24-32h)
   - AsciiDoc syntax (headings, lists, blocks)
   - Attribute names, cross-references, includes
   - Snippet expansion, Ctrl+Space trigger
   - Target: <50ms response, 100% coverage

2. **Syntax Error Detection** (16-24h)
   - Real-time checking with error/warning underlines
   - Hover explanations, quick fixes
   - Categories: syntax, semantic, style, best practices
   - Target: 100% coverage

3. **Document Templates** (16-24h)
   - Built-in templates (article, book, man page)
   - Custom template creation with variables
   - Template preview and categories
   - Target: 100% coverage

**Optional:**
- Multi-level caching, Export presets, Editor themes

### Success Criteria

- ✅ Auto-complete working (<50ms response)
- ✅ Syntax checking active (real-time)
- ✅ Templates available (built-in + custom)
- ✅ Test coverage 100% (75+ tests)
- ✅ Startup time maintained (<1.1s)

**Target Release:** September 2026

---

## Version 3.0.0 (Next-Generation Architecture)

**Target:** Q4 2026 - Q2 2027 | **Effort:** 240-360h | **Status:** 📋 BACKLOG

### Goals

Transform AsciiDoc Artisan into an extensible platform with LSP, multi-core rendering, and plugin ecosystem.

1. **Language Server Protocol (LSP)** (80-120h)
   - Features: Auto-completion, Go to Definition, Find References, Hover, Diagnostics, Rename, Code Actions
   - Deliverables: LSP server, VS Code extension, 50+ tests
   - Benefit: Use AsciiDoc Artisan from any editor

2. **Multi-Core Rendering** (60-80h)
   - Process pool with work-stealing queue
   - Automatic chunk sizing, shared memory
   - Expected: 3-5x faster for large documents (1000+ sections)

3. **Plugin Architecture** (40-60h)
   - Plugin API v1.0 with lifecycle hooks
   - Sandboxed execution, manifest validation
   - Plugin discovery and manager UI
   - Target: 5+ example plugins at launch

4. **Plugin Marketplace** (40-60h)
   - In-app browsing, install/update/uninstall
   - Ratings, reviews, search, categories
   - Security: GPG signing, automated scanning
   - Target: 20+ plugins at launch

**Deferred to v2.1+:**
- Collaborative editing (CRDT, real-time sync)
- Cloud integration (Dropbox, Drive, OneDrive)

### Success Criteria

- ✅ LSP implemented (8 core features)
- ✅ Multi-core rendering (3-5x faster)
- ✅ Plugin API v1.0 released
- ✅ Plugin marketplace live (20+ plugins)
- ✅ Test coverage 100%
- ✅ Startup time <0.7s

**Target Release:** June 2027

---

## Future Vision (v2.1+)

**v2.1.0** - Collaborative Editing & Cloud (180-240h, Q3-Q4 2027)
- Real-time multi-user editing (CRDT), presence indicators
- Cloud integration (Dropbox, Drive, OneDrive)
- WebSocket sync (<100ms latency), offline support

**v2.2.0+** - Advanced Collaboration
- Video/audio, annotations, workflows, team workspaces

**v2.3.0+** - AI Enhancement
- Writing suggestions, auto-formatting, content generation

**v2.4.0+** - Mobile & Enterprise
- iOS/Android apps, web version (Tauri)
- Self-hosted server, enterprise features (SSO, LDAP)

---

## Performance Budget

### Targets by Version

| Metric | v1.6.0 (Current) | v1.7.0 | v1.8.0 | v2.0.0 | v3.0.0 |
|--------|------------------|--------|--------|--------|--------|
| Startup Time | 1.05s | 0.9s | 0.8s | 0.7s | 0.6s |
| Preview (small, <100 sections) | 150-200ms | 100-150ms | 80-120ms | 60-100ms | 40-80ms |
| Preview (large, 1000+ sections) | 600-750ms | 500-650ms | 300-500ms | 200-300ms | 100-200ms |
| Memory (idle) | 60-100MB | 50-80MB | 45-75MB | 40-60MB | 35-55MB |
| Test Coverage | 60% | 100% | 100% | 100% | 100% |
| Type Coverage | 100% | 100% | 100% | 100% | 100% |

---


## Risk Management

**High-Risk:**
- Plugin Security → Sandboxing, code review, kill switch
- LSP Complexity → Use pygls, incremental implementation
- Test Coverage Target → Gradual increase, automated enforcement

**Medium-Risk:**
- Multi-core overhead → Benchmark, fallback to single-thread
- Collab data loss → Backups, version history, disable if needed

---

## Success Metrics

**Quality (Current):**
- Test coverage: 60%+ (Goal: 100%)
- Test pass rate: 97%+
- Startup time: 1.05s
- Quality score: 97/100 (GRANDMASTER)

**Targets by v2.0.0:**
- Weekly downloads: 1,500+
- Active users: 3,000+
- Bug reports: <8/month
- User satisfaction: >4.6/5
- Plugin ecosystem: 20+ plugins

---

## Conclusion

Transform AsciiDoc Artisan from an excellent editor into **the definitive AsciiDoc platform**.

**Strategy:**
1. ✅ v1.5-v1.9: Foundation (performance, features, quality)
2. 📋 v2.0: Advanced editing (auto-complete, syntax, templates)
3. 📋 v3.0: Platform (LSP, plugins, multi-core)

**Success Factors:**
- ✅ Solid architecture (67% code reduction, 1.05s startup)
- ✅ Low technical debt (<30% duplication)
- ✅ High quality (97/100 score, 100% type coverage)
- ✅ Competitive advantages (performance, native UI)

---

**Last Updated:** November 3, 2025
**Next Review:** Q2 2026 (v2.0.0 planning)
**Questions:** See CLAUDE.md or GitHub Discussions
