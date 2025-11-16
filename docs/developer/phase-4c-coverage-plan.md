# Phase 4C Coverage Plan

**Goal:** Improve 14 files from 90-99% to 100% coverage
**Estimated Effort:** 4-6 hours (~ 180 statements)
**Priority:** Low (current 96.4% is production-ready)
**Status:** In Progress

## Identified Files (6 of 14)

### Core Module (99% overall)
1. **gpu_detection.py** - 99% (2 missed statements)
   - Location: `src/asciidoc_artisan/core/gpu_detection.py`
   - Tests: `tests/unit/core/test_gpu_detection.py`
   - Missing: 338 statements, 2 uncovered

2. **lazy_utils.py** - 99% (1 missed statement)
   - Location: `src/asciidoc_artisan/core/lazy_utils.py`
   - Tests: `tests/unit/core/test_lazy_*.py`
   - Missing: 95 statements, 1 uncovered

### Workers Module (99% overall)
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

## Total Progress
- **Identified:** 6 files (16 missed statements)
- **Remaining:** 8 files (~164 statements estimated)
- **Modules pending:** UI, Claude, Conversion, Git

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
