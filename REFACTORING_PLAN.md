# AsciiDoc Artisan - Code Optimization & Refactoring Plan
## Comprehensive Performance Improvement Strategy

**Created:** November 1, 2025
**Target Version:** v1.7.0 - v1.8.0
**Estimated Effort:** 80-120 hours over 2-3 months
**Quality Score:** Current 82/100 → Target 95/100 (LEGENDARY)

---

## Executive Summary

This plan focuses on systematic performance optimization and code quality improvements to make AsciiDoc Artisan faster, more maintainable, and more scalable.

**Key Goals:**
- Reduce startup time: 1.05s → **<0.7s** (33% improvement)
- Improve preview latency: Current 100-300ms → **<50ms** (50-83% reduction)
- Lower memory footprint: Current growth 148.9% → **<100%** (33% reduction)
- Enhance code quality: 82/100 → **95/100** (16% improvement)

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Performance Bottlenecks](#performance-bottlenecks-identified)
3. [Optimization Roadmap](#optimization-roadmap)
4. [Phase 1: Quick Wins](#phase-1-quick-wins-1-2-weeks)
5. [Phase 2: Core Optimizations](#phase-2-core-optimizations-3-4-weeks)
6. [Phase 3: Advanced Refactoring](#phase-3-advanced-refactoring-4-6-weeks)
7. [Success Metrics](#success-metrics)
8. [Risk Assessment](#risk-assessment)

---

## Current State Analysis

### Architecture Overview

**Strengths:**
- ✅ Modular design with manager pattern (59 source modules)
- ✅ Clean separation: core (18 files), ui (33 files), workers (8 files)
- ✅ 100% type hints coverage (mypy --strict: 0 errors)
- ✅ 60%+ test coverage (621+ tests across 74 files)
- ✅ GPU acceleration enabled (10-50x faster rendering)
- ✅ Async I/O implementation complete

**Areas for Improvement:**
- ⚠️ Some large files (dialogs.py: 970 lines, action_manager.py: 950 lines)
- ⚠️ Memory growth 148.9% over 30 minutes of use
- ⚠️ 53 timing-related imports (potential for optimization)
- ⚠️ Preview latency 100-300ms (can be reduced)
- ⚠️ Worker pool not fully migrated (only partially used)

### Code Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Startup Time | 1.05s | <0.7s | 🟡 Good |
| Preview Latency | 100-300ms | <50ms | 🟡 Good |
| Memory Growth | 148.9% | <100% | 🔴 Needs Work |
| Test Coverage | 60% | 80% | 🟡 Good |
| Type Hints | 100% | 100% | ✅ Excellent |
| Code Duplication | <30% | <20% | 🟡 Good |
| Largest File | 970 lines | <600 lines | 🔴 Needs Work |

---

## Performance Bottlenecks Identified

### Critical Hot Paths (Profile Before/After Changes)

**1. Preview Rendering Pipeline** ⚡ HIGH PRIORITY
- **Location:** `workers/preview_worker.py`, `ui/preview_handler_base.py`
- **Current:** 100-300ms latency
- **Issue:** Excessive timer delays, full re-render on small edits
- **Impact:** User experience (typing feels laggy)
- **Opportunity:** 50-83% latency reduction

**2. Memory Management** ⚡ HIGH PRIORITY
- **Location:** `workers/incremental_renderer.py`, `core/lru_cache.py`
- **Current:** 148.9% growth over 30 minutes
- **Issue:** Cache not evicting old entries, string interning issues
- **Impact:** Performance degrades over time
- **Opportunity:** 33% memory reduction

**3. Worker Thread Overhead** ⚡ MEDIUM PRIORITY
- **Location:** `workers/*.py`, individual QThread instances
- **Current:** 5+ worker threads, each with overhead
- **Issue:** Not using optimized worker pool
- **Impact:** Thread creation/destruction costs
- **Opportunity:** 20-40% thread overhead reduction

**4. File I/O Operations** ⚡ MEDIUM PRIORITY
- **Location:** `core/async_file_handler.py`, `ui/file_operations_manager.py`
- **Current:** Async I/O partially implemented
- **Issue:** Not all file operations use async
- **Impact:** UI freezes on large files
- **Opportunity:** 30-50% I/O speed improvement

**5. String Processing** ⚡ LOW PRIORITY
- **Location:** `document_converter.py:374` (_clean_cell method)
- **Current:** Called in tight loops
- **Issue:** Repeated string operations
- **Impact:** Slower DOCX/PDF imports
- **Opportunity:** 10-20% import speed improvement

### Non-Critical Areas (Lower Priority)

**6. Large Dialog Files**
- `dialogs.py`: 970 lines → Split into focused dialog modules
- `action_manager.py`: 950 lines → Extract action groups

**7. CSS Generation**
- `theme_manager.py`: CSS generated every time
- **Opportunity:** Pre-generate and cache CSS

**8. Settings I/O**
- `core/settings.py`: JSON serialization on every save
- **Opportunity:** Batch saves, debounce writes

---

## Optimization Roadmap

### Timeline Overview

```
Month 1: Quick Wins (Phase 1)
├── Week 1-2: Preview latency reduction + cache tuning
└── Estimated Gain: 30-50% latency reduction

Month 2: Core Optimizations (Phase 2)
├── Week 3-4: Worker pool migration
├── Week 5-6: Memory optimization + string interning
└── Estimated Gain: 30% memory reduction, 20% thread overhead

Month 3: Advanced Refactoring (Phase 3)
├── Week 7-8: File splitting + code organization
├── Week 9-10: Async I/O completion + final tuning
└── Estimated Gain: Better maintainability, full async I/O
```

---

## Phase 1: Quick Wins (1-2 Weeks)

**Effort:** 20-30 hours
**Risk:** LOW
**Impact:** HIGH

### Task 1.1: Preview Latency Reduction ⚡⚡⚡

**Goal:** Reduce preview latency from 100-300ms to <50ms

**Changes:**
1. Reduce preview timer delays (currently 200-500ms)
2. Implement smarter debouncing (adaptive to edit rate)
3. Use incremental DOM updates (only changed blocks)
4. Pre-compile regex patterns in preview worker
5. Cache rendered HTML blocks more aggressively

**Files to Modify:**
- `ui/preview_handler_base.py` (564 lines)
- `workers/preview_worker.py`
- `core/adaptive_debouncer.py`

**Expected Results:**
- Preview latency: 100-300ms → **<50ms**
- Typing feels instant
- No CPU spikes during typing

**Testing:**
```bash
# Before/after benchmarks
python scripts/benchmarking/benchmark_predictive_rendering.py
```

---

### Task 1.2: Cache Tuning & Memory Optimization ⚡⚡

**Goal:** Reduce memory growth from 148.9% to <100%

**Changes:**
1. Tune LRU cache sizes (currently 100 blocks)
   - Editor: 50 blocks (most recent edits)
   - Preview: 100 blocks (frequently viewed)
2. Implement aggressive cache eviction on memory pressure
3. Enable string interning for repeated content
4. Add periodic garbage collection triggers
5. Implement cache statistics monitoring

**Files to Modify:**
- `workers/incremental_renderer.py` (477 lines)
- `core/lru_cache.py`
- `core/resource_monitor.py`

**Expected Results:**
- Memory growth: 148.9% → **<100%**
- No memory leaks
- Cache hit rate >80%

**Testing:**
```bash
# Memory profiling
python scripts/memory_profile.py
```

---

### Task 1.3: CSS Caching ⚡

**Goal:** Eliminate redundant CSS generation

**Changes:**
1. Pre-generate CSS for light/dark themes
2. Cache CSS in memory with theme key
3. Only regenerate on theme change
4. Store CSS in constants file for zero runtime cost

**Files to Modify:**
- `ui/theme_manager.py`
- `core/constants.py`

**Expected Results:**
- Theme switching: instant
- Startup time: 50-100ms faster
- No CSS generation during runtime

---

## Phase 2: Core Optimizations (3-4 Weeks)

**Effort:** 35-50 hours
**Risk:** MEDIUM
**Impact:** HIGH

### Task 2.1: Worker Pool Migration ⚡⚡⚡

**Goal:** Migrate all workers to optimized worker pool

**Current State:**
- Optimized worker pool exists (`workers/optimized_worker_pool.py`)
- Only partially used
- 5+ individual QThread instances still active

**Changes:**
1. Migrate GitWorker to pool
2. Migrate PandocWorker to pool
3. Migrate PreviewWorker to pool (high priority for preview latency)
4. Migrate GitHubCLIWorker to pool
5. Migrate OllamaChatWorker to pool
6. Configure pool size based on CPU cores
7. Implement task prioritization (CRITICAL, HIGH, NORMAL, LOW)
8. Add task coalescing for rapid edits

**Files to Modify:**
- `workers/git_worker.py`
- `workers/pandoc_worker.py`
- `workers/preview_worker.py`
- `workers/github_cli_worker.py`
- `workers/ollama_chat_worker.py`
- `workers/optimized_worker_pool.py`
- `ui/worker_manager.py`

**Expected Results:**
- Thread overhead: 20-40% reduction
- Task queue visible in status bar
- Faster task execution (parallel when possible)
- Better resource utilization

**Testing:**
```python
# Load test with multiple operations
def test_worker_pool_stress():
    - Start 20 git operations
    - Start 10 preview updates
    - Start 5 pandoc conversions
    - Verify all complete successfully
    - Measure throughput improvement
```

---

### Task 2.2: String Interning & Optimization ⚡⚡

**Goal:** Reduce string memory usage by 20-30%

**Changes:**
1. Enable string interning for:
   - Repeated AsciiDoc syntax tokens (`:`, `=`, `*`, etc.)
   - Common attribute names (`:author:`, `:version:`, etc.)
   - CSS class names
   - HTML tag names
2. Use `sys.intern()` for frequently repeated strings
3. Implement string pool for document blocks
4. Pre-compile regex patterns (store in constants)

**Files to Modify:**
- `workers/preview_worker.py`
- `workers/incremental_renderer.py`
- `document_converter.py`
- `core/constants.py`

**Expected Results:**
- Memory usage: 20-30% reduction
- String comparison: faster (identity check)
- Preview rendering: 5-10% faster

---

### Task 2.3: Async I/O Completion ⚡⚡

**Goal:** Migrate all blocking file operations to async

**Current State:**
- Async I/O framework exists (`core/async_file_handler.py`)
- Not all file operations use it

**Changes:**
1. Audit all file operations (53 timing-related imports found)
2. Migrate blocking operations:
   - Settings save/load
   - Recent files list
   - Cache file writes
   - Log file writes
3. Use `aiofiles` for all disk I/O
4. Add async file watcher for external changes

**Files to Modify:**
- `core/settings.py`
- `ui/file_operations_manager.py`
- `ui/file_load_manager.py`
- `core/async_file_handler.py`

**Expected Results:**
- No UI freezes on file operations
- Faster file open/save (30-50%)
- Better responsiveness

---

## Phase 3: Advanced Refactoring (4-6 Weeks)

**Effort:** 25-40 hours
**Risk:** MEDIUM-HIGH
**Impact:** MEDIUM (Maintainability)

### Task 3.1: File Splitting & Modularization ⚡

**Goal:** Split large files for better maintainability

**Targets:**
1. `dialogs.py` (970 lines) → Split into:
   - `dialogs/preferences_dialog.py`
   - `dialogs/ollama_settings_dialog.py`
   - `dialogs/settings_editor_dialog.py`
   - `dialogs/font_settings_dialog.py`
   - `dialogs/__init__.py` (exports all)

2. `action_manager.py` (950 lines) → Split into:
   - `actions/file_actions.py`
   - `actions/edit_actions.py`
   - `actions/view_actions.py`
   - `actions/tools_actions.py`
   - `actions/help_actions.py`
   - `action_manager.py` (coordinator only)

**Expected Results:**
- Max file size: <600 lines
- Easier to navigate
- Faster IDE loading
- Better test organization

---

### Task 3.2: Code Organization Cleanup ⚡

**Goal:** Improve code organization and reduce coupling

**Changes:**
1. Move constants from multiple files to `core/constants.py`
2. Consolidate utility functions in `core/utils.py`
3. Remove dead code (unused imports, functions)
4. Standardize naming conventions
5. Add missing docstrings (currently ~90% coverage)

**Tools:**
```bash
# Find dead code
vulture src/

# Find unused imports
ruff check --select F401

# Analyze complexity
radon cc src/ -a
```

**Expected Results:**
- Code complexity: lower
- Import graph: cleaner
- Documentation: 100% coverage

---

### Task 3.3: Performance Monitoring Infrastructure ⚡

**Goal:** Add runtime performance monitoring

**Changes:**
1. Implement performance metrics collection:
   - Startup time breakdown
   - Preview latency histogram
   - Memory usage trends
   - Cache hit rates
2. Add performance dashboard (debug mode)
3. Log slow operations (>100ms)
4. Generate performance reports

**Files to Create:**
- `core/performance_monitor.py`
- `ui/performance_dashboard.py` (optional, debug only)

**Expected Results:**
- Real-time performance visibility
- Proactive detection of regressions
- Data-driven optimization decisions

---

## Success Metrics

### Performance Targets

| Metric | Baseline (v1.6.0) | Target (v1.8.0) | Method |
|--------|-------------------|-----------------|--------|
| Startup Time | 1.05s | <0.7s | `time python src/main.py` |
| Preview Latency | 100-300ms | <50ms | benchmark_predictive_rendering.py |
| Memory Growth (30min) | 148.9% | <100% | memory_profile.py |
| Preview FPS | 3-10 fps | >20 fps | Manual testing |
| File Open Time (1MB) | 200-500ms | <100ms | Timed file operations |
| Worker Pool Utilization | N/A | >70% | Pool statistics |

### Quality Targets

| Metric | Baseline (v1.6.0) | Target (v1.8.0) | Method |
|--------|-------------------|-----------------|--------|
| Test Coverage | 60% | 80% | pytest --cov |
| Code Duplication | <30% | <20% | ruff, manual review |
| Max File Size | 970 lines | <600 lines | wc -l |
| Type Hints | 100% | 100% | mypy --strict |
| Code Quality Score | 82/100 | 95/100 | Manual assessment |

### User Experience Targets

| Metric | Baseline | Target | Method |
|--------|----------|--------|--------|
| Typing Lag | Noticeable | None | Manual testing |
| UI Freezes | Occasional | Never | Manual testing |
| Responsiveness | Good | Excellent | User feedback |
| Startup Feel | Fast | Instant | User perception |

---

## Implementation Strategy

### Development Workflow

**For Each Task:**

1. **Baseline Measurement**
   ```bash
   # Run benchmarks before changes
   python scripts/benchmarking/benchmark_performance.py > baseline.txt
   python scripts/memory_profile.py > baseline_memory.txt
   ```

2. **Implement Changes**
   - Create feature branch: `git checkout -b optimize/task-name`
   - Make incremental changes
   - Commit frequently with clear messages

3. **Testing**
   ```bash
   # Run full test suite
   make test

   # Run specific performance tests
   pytest tests/test_performance*.py -v

   # Profile the changes
   python -m cProfile -o profile.stats src/main.py
   ```

4. **Measurement**
   ```bash
   # Compare against baseline
   python scripts/benchmarking/benchmark_performance.py > after.txt
   diff baseline.txt after.txt
   ```

5. **Code Review**
   - Self-review checklist:
     - [ ] Tests pass (make test)
     - [ ] Type checks pass (mypy --strict)
     - [ ] Performance improved (benchmarks)
     - [ ] No new warnings (ruff)
     - [ ] Documentation updated

6. **Merge**
   - Squash commits if needed
   - Update CHANGELOG.md
   - Tag with version if milestone

---

## Risk Assessment

### High-Risk Changes (Require Extensive Testing)

**1. Worker Pool Migration (Task 2.1)**
- **Risk:** Breaking existing threading model
- **Mitigation:**
  - Migrate one worker at a time
  - Keep fallback to old threading
  - Extensive integration testing
  - Monitor for race conditions

**2. Memory Optimization (Task 1.2)**
- **Risk:** Premature cache eviction, data loss
- **Mitigation:**
  - Conservative cache sizes initially
  - Monitor cache hit rates
  - Add cache statistics dashboard
  - Stress test with large documents

**3. Async I/O Completion (Task 2.3)**
- **Risk:** Deadlocks, race conditions
- **Mitigation:**
  - Use proven async patterns
  - Add timeout guards (60s max)
  - Comprehensive async tests
  - Fallback to sync I/O on errors

### Medium-Risk Changes

**4. File Splitting (Task 3.1)**
- **Risk:** Import cycles, broken references
- **Mitigation:**
  - Update imports methodically
  - Use TYPE_CHECKING for circular imports
  - Run full test suite after each split

**5. Preview Latency Reduction (Task 1.1)**
- **Risk:** Missing updates, stale previews
- **Mitigation:**
  - Test with rapid typing
  - Verify all edits trigger updates
  - Add update verification tests

### Low-Risk Changes (Safe to Implement)

**6. CSS Caching (Task 1.3)**
- **Risk:** Minimal (CSS is static)
- **Testing:** Visual inspection of themes

**7. Code Organization (Task 3.2)**
- **Risk:** Minimal (no logic changes)
- **Testing:** Ensure tests still pass

---

## Dependencies & Prerequisites

### Required Tools
- Python 3.12+ (for best performance)
- pytest + pytest-cov (testing)
- mypy (type checking)
- ruff (linting)
- vulture (dead code detection)
- radon (complexity analysis)

### Optional Tools
- cProfile (profiling)
- memory_profiler (memory analysis)
- py-spy (sampling profiler)
- line_profiler (line-by-line profiling)

### Knowledge Required
- Qt threading model (QThread, signals/slots)
- Python asyncio (for async I/O)
- Memory management (gc, weakref)
- Profiling techniques (cProfile, py-spy)

---

## Progress Tracking

### Phase 1: Quick Wins (Weeks 1-2)
- [ ] Task 1.1: Preview Latency Reduction (8-12h)
- [ ] Task 1.2: Cache Tuning & Memory Optimization (8-12h)
- [ ] Task 1.3: CSS Caching (4-6h)
- **Total:** 20-30 hours

### Phase 2: Core Optimizations (Weeks 3-6)
- [ ] Task 2.1: Worker Pool Migration (15-20h)
- [ ] Task 2.2: String Interning & Optimization (10-15h)
- [ ] Task 2.3: Async I/O Completion (10-15h)
- **Total:** 35-50 hours

### Phase 3: Advanced Refactoring (Weeks 7-10)
- [ ] Task 3.1: File Splitting & Modularization (12-18h)
- [ ] Task 3.2: Code Organization Cleanup (8-12h)
- [ ] Task 3.3: Performance Monitoring Infrastructure (5-10h)
- **Total:** 25-40 hours

**Grand Total:** 80-120 hours over 10 weeks

---

## Rollout Plan

### Alpha Phase (Internal Testing)
- Implement Phase 1 (Quick Wins)
- Run benchmarks
- Verify no regressions
- **Duration:** 2 weeks

### Beta Phase (Limited Testing)
- Implement Phase 2 (Core Optimizations)
- Invite beta testers
- Collect performance data
- **Duration:** 4 weeks

### Release Candidate
- Implement Phase 3 (Advanced Refactoring)
- Final performance tuning
- Documentation updates
- **Duration:** 3 weeks

### Stable Release (v1.8.0)
- All optimizations complete
- Quality score: 95/100
- Performance targets met
- **Target Date:** Q2-Q3 2026

---

## Monitoring & Validation

### Continuous Benchmarking

**Automated Tests (CI/CD):**
```bash
# Run on every commit
make test
mypy src/ --strict

# Run on every PR
python scripts/benchmarking/benchmark_performance.py
python scripts/memory_profile.py
```

**Weekly Performance Reports:**
- Startup time trend
- Memory usage trend
- Preview latency trend
- Test coverage trend

**Monthly Code Quality Audit:**
- Code complexity analysis
- Dead code detection
- Dependency audit
- Security scan

---

## Conclusion

This refactoring plan provides a systematic approach to optimizing AsciiDoc Artisan for maximum performance and maintainability. By following the phased approach and measuring results at each step, we can ensure continuous improvement while maintaining stability.

**Key Takeaways:**
- Start with quick wins (Phase 1) for immediate impact
- Tackle core optimizations (Phase 2) for long-term gains
- Finish with refactoring (Phase 3) for maintainability
- Measure everything, optimize based on data
- Test extensively, ship confidently

**Expected Outcomes:**
- 33% faster startup (<0.7s)
- 50-83% lower preview latency (<50ms)
- 33% lower memory growth (<100%)
- 16% higher quality score (95/100)
- Better developer experience
- Happier users

---

**Document Version:** 1.0
**Last Updated:** November 1, 2025
**Next Review:** December 1, 2025 (after Phase 1 completion)
