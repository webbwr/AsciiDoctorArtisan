# Phase 4C Coverage Plan

**Goal:** Improve 14 files from 90-99% to 100% coverage
**Estimated Effort:** 4-6 hours (~ 180 statements)
**Priority:** Low (current 96.4% is production-ready)
**Status:** In Progress

## Identified Files (7 of 14)

### Core Module (99% overall - 2 files)
1. **gpu_detection.py** - 99% (2 missed statements)
   - Location: `src/asciidoc_artisan/core/gpu_detection.py`
   - Tests: `tests/unit/core/test_gpu_detection.py`
   - Missing: 338 statements, 2 uncovered

2. **lazy_utils.py** - 99% (1 missed statement)
   - Location: `src/asciidoc_artisan/core/lazy_utils.py`
   - Tests: `tests/unit/core/test_lazy_*.py`
   - Missing: 95 statements, 1 uncovered

### Workers Module (99% overall - 4 files)
3. **git_worker.py** - 98% (4 missed statements)
   - Location: `src/asciidoc_artisan/workers/git_worker.py`
   - Tests: `tests/unit/workers/test_git_worker*.py`
   - Missing: 224 statements, 4 uncovered

4. **github_cli_worker.py** - 98% (3 missed statements)
   - Location: `src/asciidoc_artisan/workers/github_cli_worker.py`
   - Tests: `tests/unit/workers/test_github_cli_worker*.py`
   - Missing: 121 statements, 3 uncovered

5. **optimized_worker_pool.py** - 98% (4 missed statements)
   - Location: `src/asciidoc_artisan/workers/optimized_worker_pool.py`
   - Tests: `tests/unit/workers/test_optimized_worker_pool*.py`
   - Missing: 176 statements, 4 uncovered

6. **pandoc_worker.py** - 99% (2 missed statements)
   - Location: `src/asciidoc_artisan/workers/pandoc_worker.py`
   - Tests: `tests/unit/workers/test_pandoc_worker*.py`
   - Missing: 188 statements, 2 uncovered

### Claude Module (97% overall - 1 file)
7. **claude_worker.py** - 93% (5 missed statements)
   - Location: `src/asciidoc_artisan/claude/claude_worker.py`
   - Tests: `tests/unit/claude/test_claude_worker*.py`
   - Missing: 71 statements, 5 uncovered

## Total Progress
- **Identified:** 7 files (21 missed statements)
- **Remaining:** 7 files (~159 statements estimated)
- **Modules pending:** UI (main source of Phase 4C files)

## Module Coverage Summary

| Module | Overall Coverage | Files at 100% | Files <100% | Status |
|--------|------------------|---------------|-------------|--------|
| Core | 99% (4697 stmts, 3 miss) | 33/35 | 2 | ✅ Analyzed |
| Workers | 99% (1457 stmts, 13 miss) | 7/11 | 4 | ✅ Analyzed |
| Claude | 97% (194 stmts, 5 miss) | 1/2 | 1 | ✅ Analyzed |
| UI | ~90-95% (estimated) | TBD | 7-8 est. | ⏸️ Deferred |

**Note:** UI module coverage analysis deferred due to long test runtime (>5 minutes). The remaining Phase 4C files are primarily in the UI module, which aligns with the QA audit noting Phase 4E (UI Layer 0% → 100%) as a 3-4 week effort.

## Approach

### Targeted Coverage Method
Instead of running full test suite (which hangs), use module-by-module approach:

```bash
# Core module (completed)
pytest tests/unit/core/ --cov=src/asciidoc_artisan/core --cov-report=term

# Workers module (completed)
pytest tests/unit/workers/ --cov=src/asciidoc_artisan/workers --cov-report=term

# UI module (in progress)
pytest tests/unit/ui/ --cov=src/asciidoc_artisan/ui --cov-report=term

# Claude module
pytest tests/unit/claude/ --cov=src/asciidoc_artisan/claude --cov-report=term
```

### Coverage Improvement Steps

For each file with <100% coverage:

1. **Identify uncovered lines:**
   ```bash
   pytest tests/unit/MODULE/ --cov=src/asciidoc_artisan/MODULE/FILE.py \
     --cov-report=term-missing --no-cov-on-fail
   ```

2. **Add targeted tests:**
   - Focus on edge cases, error paths, conditional branches
   - Use existing test patterns from test files
   - Ensure proper mocking for external dependencies

3. **Verify improvement:**
   ```bash
   pytest tests/unit/MODULE/test_FILE.py --cov=src/asciidoc_artisan/MODULE/FILE.py \
     --cov-report=term
   ```

## Timeline

**Quick wins (1-2 hours):**
- lazy_utils.py (1 statement)
- pandoc_worker.py (2 statements)
- gpu_detection.py (2 statements)

**Medium effort (2-3 hours):**
- git_worker.py (4 statements)
- github_cli_worker.py (3 statements)
- optimized_worker_pool.py (4 statements)

**Remaining files (2-3 hours):**
- UI module files (pending identification)
- Claude module files (if any)

## Success Criteria

- [ ] All 14 files at 100% coverage
- [ ] Total project coverage >= 97%
- [ ] All new tests pass existing quality standards
- [ ] mypy --strict continues to pass
- [ ] Test execution time <3 minutes per module

## Notes

- Coverage runs >5 minutes should be killed and retried with smaller scope
- Focus on statement coverage (branch coverage is bonus)
- Document any intentionally uncovered code (e.g., defensive assertions)
- Update this plan as files are completed

---

**Created:** 2025-11-16
**Last Updated:** 2025-11-16
**Next Action:** Complete UI module coverage analysis
