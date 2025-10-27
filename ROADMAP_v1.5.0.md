# AsciiDoc Artisan Roadmap v1.5.0+

**Last Updated:** October 27, 2025
**Based on:** Deep Code Analysis v1.4.0
**Status:** Planning Phase

---

## Vision Statement

Transform AsciiDoc Artisan from a solid editor into a best-in-class, high-performance document authoring platform with exceptional user experience, maintainable codebase, and extensible architecture.

---

## Version 1.4.1 (Bug Fix & Quick Wins)

**Target:** 2 weeks (November 10, 2025)
**Focus:** Quick optimizations with high ROI

### Performance Optimizations

- [ ] **Cache GPU detection results to disk**
  - Save to `~/.config/AsciiDocArtisan/gpu_cache.json`
  - 7-day TTL
  - **Impact:** 100ms startup improvement
  - **Effort:** 2 hours
  - **Priority:** HIGH

- [ ] **Implement memory profiling system**
  - Add `MemoryProfiler` class using `tracemalloc`
  - Track top memory consumers
  - Log snapshots at key operations
  - **Impact:** Data for optimization decisions
  - **Effort:** 4 hours
  - **Priority:** HIGH

- [ ] **Clean up TODO/FIXME comments**
  - Audit all 22 files with TODOs
  - Convert actionable items to GitHub issues
  - Remove completed TODOs
  - **Impact:** Code clarity
  - **Effort:** 2 hours
  - **Priority:** MEDIUM

### Bug Fixes

- [ ] Review and fix any GPU detection edge cases
- [ ] Fix any reported UI glitches from v1.4.0
- [ ] Update outdated code comments

### Documentation

- [ ] Publish DEEP_CODE_ANALYSIS_v1.4.0.md
- [ ] Update SPECIFICATIONS.md with performance budget
- [ ] Create OPTIMIZATION_GUIDE.md for developers

**Success Criteria:**
- Startup time < 2.5 seconds (from 3-5s)
- Memory profiling active and logged
- Zero TODO comments in critical files
- All reported bugs fixed

---

## Version 1.5.0 (Architecture & Performance)

**Target:** 1-2 months (December 2025 - January 2026)
**Focus:** Major refactoring and architectural improvements

### Core Architecture Refactoring

#### 1. Worker Pool Implementation
**Priority:** HIGH | **Effort:** 8 hours

- [ ] Create `WorkerPool` class using `QThreadPool`
- [ ] Implement `QRunnable` tasks for render/convert/git operations
- [ ] Add priority queuing (high/medium/low priority)
- [ ] Implement task cancellation support
- [ ] Add worker statistics tracking

**Files:**
- New: `src/asciidoc_artisan/workers/worker_pool.py`
- Modify: `src/asciidoc_artisan/ui/main_window.py`

**Benefits:**
- Better resource utilization
- Cancellable operations
- Priority-based task scheduling
- Reduced memory overhead

#### 2. Main Window Refactoring (Phase 1)
**Priority:** CRITICAL | **Effort:** 40 hours

**Current:** 1,719 lines (too large)
**Target:** ~500 lines

**Step 1: Extract State Management (8 hours)**
- [ ] Create `EditorState` class
  - Track `current_file`, `unsaved_changes`, `is_maximized`
  - Handle state transitions
  - Emit state change signals

- [ ] Create `AppState` dataclass
  - Application-wide state
  - Settings snapshot
  - Worker status

**Step 2: Extract Operation Coordinators (24 hours)**
- [ ] Create `FileOperationCoordinator`
  - Move all file I/O logic
  - ~300 lines extracted

- [ ] Create `ConversionCoordinator`
  - Move all conversion logic
  - ~300 lines extracted

- [ ] Create `PreviewCoordinator`
  - Move preview management
  - ~200 lines extracted

- [ ] Create `GitCoordinator`
  - Move Git operations
  - ~200 lines extracted

**Step 3: Simplify Main Window (8 hours)**
- [ ] Main window becomes composition root
- [ ] Delegate to coordinators
- [ ] Keep only: UI construction, event routing, coordinator init
- [ ] Target: ~500 lines

**Files to Create:**
- `src/asciidoc_artisan/core/editor_state.py`
- `src/asciidoc_artisan/coordinators/file_coordinator.py`
- `src/asciidoc_artisan/coordinators/conversion_coordinator.py`
- `src/asciidoc_artisan/coordinators/preview_coordinator.py`
- `src/asciidoc_artisan/coordinators/git_coordinator.py`

**Success Criteria:**
- main_window.py < 600 lines
- All tests passing
- No performance regression
- Improved code coverage

#### 3. Operation Cancellation System
**Priority:** HIGH | **Effort:** 12 hours

- [ ] Add `CancellableWorker` base class
- [ ] Implement cancellation tokens
- [ ] Add UI cancel buttons for long operations
- [ ] Handle cleanup on cancellation

**Files:**
- New: `src/asciidoc_artisan/workers/cancellable_worker.py`
- Modify: All worker classes

**Benefits:**
- Stop long-running operations
- Better UX for large file operations
- Prevent worker thread accumulation

### Performance Improvements

#### 4. Lazy Import System
**Priority:** MEDIUM | **Effort:** 8 hours

- [ ] Implement `LazyImporter` for heavy modules
- [ ] Defer non-critical imports to first use
- [ ] Profile import times
- [ ] Optimize import order

**Target Modules:**
- pypandoc (only needed for conversion)
- pymupdf (only needed for PDF import)
- ollama (only needed when AI enabled)

**Impact:** 500ms+ startup improvement

#### 5. Metrics Collection System
**Priority:** MEDIUM | **Effort:** 12 hours

- [ ] Create `MetricsCollector` class
- [ ] Track operation durations
- [ ] Monitor memory usage
- [ ] Log performance statistics
- [ ] Generate performance reports

**Metrics to Track:**
- Preview render times (p50, p95, p99)
- File I/O times
- Conversion times
- Memory usage over time
- Cache hit rates

**Files:**
- New: `src/asciidoc_artisan/core/metrics.py`

### Code Quality Improvements

#### 6. Preview Handler Consolidation
**Priority:** MEDIUM | **Effort:** 16 hours

**Current:**
- `preview_handler.py` (540 lines)
- `preview_handler_gpu.py` (226 lines)
- 60% code overlap

**Proposed Structure:**
```
PreviewHandlerBase (~400 lines)
├── TextBrowserHandler (~50 lines)
└── WebEngineHandler (~100 lines)
```

- [ ] Extract common functionality to base class
- [ ] Keep GPU-specific code in WebEngineHandler
- [ ] Keep fallback code in TextBrowserHandler
- [ ] Add factory function for handler creation

**Files:**
- Refactor: `src/asciidoc_artisan/ui/preview_handler.py`
- Refactor: `src/asciidoc_artisan/ui/preview_handler_gpu.py`

**Benefits:**
- Reduce code duplication by 60%
- Easier to maintain
- Better testing

#### 7. Test Coverage Improvement
**Priority:** HIGH | **Effort:** 20 hours

**Current:** 34%
**Target:** 60%

- [ ] Add UI tests using pytest-qt (40 new tests)
- [ ] Add performance regression tests (10 new tests)
- [ ] Add memory leak tests (5 new tests)
- [ ] Add stress tests (10 new tests)

**Focus Areas:**
- Main window UI operations
- Worker thread communication
- Error handling paths
- Edge cases in file operations

---

## Version 1.6.0 (Advanced Optimizations)

**Target:** 3-4 months (February - March 2026)
**Focus:** Deep optimizations and advanced features

### Performance Optimizations

#### 1. Optimize Block Detection Algorithm
**Priority:** MEDIUM | **Effort:** 8 hours

- [ ] Profile current block detection performance
- [ ] Implement state machine for heading detection
- [ ] Optimize string operations
- [ ] Add caching for repeated scans

**File:**
- `src/asciidoc_artisan/workers/incremental_renderer.py`

**Impact:** 20-30% faster incremental rendering

#### 2. Implement Async I/O
**Priority:** LOW | **Effort:** 24 hours

- [ ] Migrate file operations to async/await
- [ ] Use `aiofiles` for non-blocking reads
- [ ] Implement async file watcher
- [ ] Add async context managers

**Benefits:**
- Non-blocking file operations
- Better responsiveness
- Concurrent file operations

#### 3. Predictive Rendering
**Priority:** MEDIUM | **Effort:** 16 hours

- [ ] Predict which sections user will view
- [ ] Pre-render common sections during debounce
- [ ] Use idle time for background rendering
- [ ] Add heuristics for prediction

**Impact:** Perceived latency reduction by 30-50%

### Advanced Features

#### 4. Plugin Architecture
**Priority:** LOW | **Effort:** 40 hours

- [ ] Design plugin API
- [ ] Implement plugin loader
- [ ] Add plugin hooks for:
  - Custom renderers
  - Custom exporters
  - Custom themes
  - Editor extensions
- [ ] Create plugin manager UI
- [ ] Write plugin development guide

**Files:**
- New: `src/asciidoc_artisan/plugins/` (package)

#### 5. Collaborative Editing (Experimental)
**Priority:** FUTURE | **Effort:** 80+ hours

- [ ] Research OT (Operational Transform) or CRDT
- [ ] Implement conflict-free editing
- [ ] Add WebSocket server
- [ ] Create session management
- [ ] Add user presence indicators

**Note:** This is a major feature requiring significant research and development.

---

## Version 2.0.0 (Major Overhaul)

**Target:** 6+ months (Mid 2026)
**Focus:** Complete architecture redesign for scalability

### Core Architecture

#### 1. Multi-Core Rendering
- [ ] Implement distributed rendering across CPU cores
- [ ] Use multiprocessing for parallel block rendering
- [ ] Add render coordinator for work distribution
- [ ] Implement result aggregation

#### 2. Advanced Caching System
- [ ] Multi-level cache (L1: memory, L2: disk)
- [ ] Distributed cache for collaborative editing
- [ ] Cache invalidation strategies
- [ ] Smart prefetching

#### 3. Language Server Protocol (LSP)
- [ ] Implement AsciiDoc LSP server
- [ ] Add autocomplete
- [ ] Add hover documentation
- [ ] Add goto definition
- [ ] Add code actions (quick fixes)

---

## Continuous Improvements

### Code Quality (Ongoing)

- [ ] **Refactor main_window.py**: 1,719 → 500 lines
- [ ] **Increase test coverage**: 34% → 80%
- [ ] **Reduce cyclomatic complexity**: Avg 8 → 6
- [ ] **Improve maintainability index**: 65 → 75
- [ ] **Add type hints**: 60% → 100%

### Performance (Ongoing)

- [ ] **Reduce startup time**: 3-5s → 2s
- [ ] **Optimize preview updates**: 950-1,250ms → 600ms (large docs)
- [ ] **Optimize memory usage**: 80-160MB → 60-100MB
- [ ] **Reduce CPU usage**: 5-15% → 3-8% (typing)

### Documentation (Ongoing)

- [ ] Keep CLAUDE.md updated
- [ ] Maintain SPECIFICATIONS.md
- [ ] Update README.md
- [ ] Write developer guides
- [ ] Create video tutorials

---

## Performance Budget

### Targets by Version

| Metric | v1.4.0 | v1.4.1 | v1.5.0 | v1.6.0 | v2.0.0 |
|--------|--------|--------|--------|--------|--------|
| Startup | 3-5s | 2.5s | 2.0s | 1.5s | 1.0s |
| Preview (small) | 250-300ms | 250ms | 200ms | 150ms | 100ms |
| Preview (large) | 950-1250ms | 900ms | 750ms | 600ms | 400ms |
| Memory (idle) | 80-160MB | 80-150MB | 70-120MB | 60-100MB | 50-80MB |
| Test Coverage | 34% | 34% | 60% | 70% | 80% |
| Code Quality | 65 | 65 | 70 | 75 | 80 |

---

## Risk Management

### High-Risk Items

1. **Main Window Refactoring**
   - Risk: Breaking existing functionality
   - Mitigation: Incremental refactoring, comprehensive tests
   - Rollback Plan: Keep old code commented during transition

2. **Async I/O Migration**
   - Risk: Complex threading issues
   - Mitigation: Thorough testing, gradual migration
   - Rollback Plan: Keep sync versions as fallback

3. **Plugin Architecture**
   - Risk: Security vulnerabilities, API instability
   - Mitigation: Sandboxing, careful API design
   - Rollback Plan: Disable plugin system if issues arise

### Medium-Risk Items

4. **Worker Pool Implementation**
   - Risk: Resource contention
   - Mitigation: Proper priority management
   - Rollback Plan: Keep current thread model

5. **Predictive Rendering**
   - Risk: Wasted resources on wrong predictions
   - Mitigation: Smart heuristics, user settings
   - Rollback Plan: Disable prediction

---

## Dependencies & Prerequisites

### Technical Requirements

- Python 3.11+ (3.12 recommended)
- PySide6 6.9.0+
- pytest 7.0+ (testing)
- pytest-qt 4.0+ (UI testing)
- tracemalloc (memory profiling)
- cProfile (performance profiling)

### Team Skills Required

- Qt/PySide6 expertise
- Python threading knowledge
- Performance optimization experience
- Testing best practices
- Architecture design patterns

---

## Success Metrics

### v1.5.0 Success Criteria

- [ ] Startup time < 2.0 seconds (from 3-5s)
- [ ] main_window.py < 600 lines (from 1,719)
- [ ] Test coverage > 60% (from 34%)
- [ ] Worker pool implemented and stable
- [ ] Operation cancellation working
- [ ] Preview handler code duplication < 30% (from 60%)
- [ ] Memory profiling active and monitored
- [ ] All performance metrics tracked
- [ ] Zero critical bugs
- [ ] User satisfaction > 4.5/5

### v1.6.0 Success Criteria

- [ ] Startup time < 1.5 seconds
- [ ] Large doc preview < 600ms (from 950-1,250ms)
- [ ] Test coverage > 70%
- [ ] Async I/O implemented
- [ ] Predictive rendering active
- [ ] Plugin architecture released (beta)
- [ ] Advanced optimization complete
- [ ] User satisfaction > 4.7/5

---

## Resource Allocation

### Estimated Effort Breakdown

| Version | Total Hours | Priority 1 | Priority 2 | Priority 3 |
|---------|-------------|------------|------------|------------|
| v1.4.1 | 8h | 6h | 2h | 0h |
| v1.5.0 | 120h | 60h | 48h | 12h |
| v1.6.0 | 180h | 80h | 80h | 20h |
| v2.0.0 | 400h | 200h | 150h | 50h |
| **Total** | **708h** | **346h** | **280h** | **82h** |

### Timeline

- **v1.4.1:** 2 weeks (1 developer, part-time)
- **v1.5.0:** 1-2 months (1 developer, full-time)
- **v1.6.0:** 3-4 months (1 developer, full-time)
- **v2.0.0:** 6+ months (2 developers, full-time)

---

## Community Feedback Integration

### Requested Features (from GitHub Issues)

1. **Find & Replace** (v1.5.0)
   - Priority: HIGH
   - Effort: 8 hours

2. **Auto-complete for AsciiDoc** (v1.6.0)
   - Priority: MEDIUM
   - Effort: 24 hours

3. **Syntax Error Detection** (v1.6.0)
   - Priority: MEDIUM
   - Effort: 16 hours

4. **Export to EPUB** (v1.6.0)
   - Priority: LOW
   - Effort: 12 hours

5. **Dark Theme Improvements** (v1.5.0)
   - Priority: LOW
   - Effort: 4 hours

---

## Conclusion

This roadmap represents an ambitious but achievable plan to transform AsciiDoc Artisan into a world-class document editor. The focus is on:

1. **Performance:** Faster, more responsive, better resource usage
2. **Architecture:** Clean, maintainable, extensible codebase
3. **Features:** Advanced capabilities while maintaining simplicity
4. **Quality:** Higher test coverage, fewer bugs, better UX

**Key Principle:** "Make it work, make it right, make it fast" - We're now in the "make it right" and "make it fast" phases.

---

**Roadmap Status:** ACTIVE
**Last Updated:** October 27, 2025
**Next Review:** After v1.5.0 release (January 2026)
**Maintainer:** Claude Code (Sonnet 4.5) + Development Team
