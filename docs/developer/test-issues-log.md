# Test Issues Log

**Purpose:** Track hung tests and failures for remediation

**Date:** 2025-11-16 (Phase 4C/4E Coverage Session)

## Hung Tests

### Full Test Suite (process 26795d - Phase 4C)
- **Command:** `pytest tests/ -v --tb=short --cov=src/asciidoc_artisan --cov-report=html --cov-report=term-missing`
- **Status:** Hung at 47% completion
- **Last Passing Test:** `tests/unit/ui/test_context_modes.py::TestSignalEmissionEdgeCases::test_programmatic_vs_user_change_signals`
- **Hung At:** `tests/unit/ui/test_dependency_dialog.py::TestTelemetryStatusDialogEnabled::test_show_telemetry_enabled_with_session_id`
- **Issue:** UI tests in dialog_manager.py hang indefinitely
- **Impact:** Prevents full test suite completion with HTML coverage report
- **Workaround:** Run non-slow tests with `pytest -m "not slow"` (5467/5479 tests, 99.8% pass)

### UI Module Coverage (process 3fd137 - Phase 4E)
- **Command:** `pytest tests/unit/ui/ --cov=src/asciidoc_artisan/ui --cov-report=term-missing --no-cov-on-fail -q`
- **Status:** Hung at 21% completion (2919 total tests)
- **Last Passing Test:** `tests/unit/ui/test_dependency_dialog.py` (31 tests passed)
- **Hung At:** `tests/unit/ui/test_dialog_manager.py` (10 tests passed, then hung)
- **Issue:** Same dialog_manager.py hanging pattern as full suite
- **Impact:** Cannot complete UI module coverage analysis
- **Workaround:** Test UI files individually, skip dialog_manager.py or identify specific hanging test

### Dialog Manager Test (process 9d4ae9 - Phase 4E)
- **Command:** `pytest tests/unit/ui/test_dialog_manager.py -v --tb=short`
- **Status:** Hung at 45% completion (101 total tests in file)
- **Last Passing Test:** `test_dialog_manager.py::TestDialogManagerStateManagement::test_manager_can_be_recreated` (test #45)
- **Hung At:** `test_dialog_manager.py::TestTelemetryStatusDialogEnabled::test_show_telemetry_enabled_with_session_id` (test #46)
- **Issue:** Specific test hangs indefinitely (this is the root cause of all UI test hangs)
- **Root Cause:** Telemetry status dialog with session ID - likely Qt event loop or modal dialog issue
- **Workaround:** Skip this test with `@pytest.mark.skip` or fix the underlying issue

## Successful Test Runs

### Non-Slow Tests (process 8c0959)
- **Command:** `pytest tests/ -v --tb=short --cov=src/asciidoc_artisan --cov-report=html --cov-report=term-missing -m "not slow" --maxfail=5 -x`
- **Status:** ✓ Completed successfully
- **Results:** 5467 passed, 3 skipped, 12 deselected
- **Duration:** Completed in reasonable time
- **Recommendation:** Use this as primary test command

### Core Module Tests (process fbf256)
- **Command:** `pytest tests/unit/core/ --cov=src/asciidoc_artisan/core/lazy_utils.py --cov-report=term-missing --no-cov-on-fail -q`
- **Status:** ✓ Completed successfully
- **Results:** 1477 passed, 38 warnings
- **Notes:** Confirmed lazy_utils.py never imported (0% coverage expected)

### XML Coverage Report (process 125771)
- **Command:** `pytest --cov=src/asciidoc_artisan --cov-report=xml --cov-report=term -q --tb=no`
- **Status:** ✓ Completed successfully
- **Results:** Generated coverage.xml for statusline parsing
- **Coverage:** 117/117 lines (100% of tested subset)

## Deferred Coverage Items

### Complex Integration Scenarios
1. **document_converter.py:293-296** - Auto-install success path
   - Requires complex mocking of PandocIntegration state
   - Test would need to mock: check_installation(), pandoc_path, pypandoc_available, auto_install_pypandoc()
   - Impact: 3 statements
   - Priority: Low (defensive code, rarely executed)

### Unreachable Defensive Code
1. **document_converter.py:475** - Empty normalized_table check
   - Similar to github_cli_worker dead code (removed in commit 0d2cefe)
   - Logic: If filtered_table passes (line 458), normalized_table will also pass
   - Impact: 1 statement
   - Priority: Low (consider removing like github_cli_worker)

### Qt Threading Limitations (Cannot Improve)
1. **optimized_worker_pool.py:123-124, 363-364** - QRunnable execution
   - coverage.py cannot track across QThreadPool boundaries
   - Maximum achievable: 98% (172/176 statements)
   - Tests exist and pass: test_task_exception_handling, test_cancel_coalesced_task

2. **claude_worker.py:90-95** - QThread.run() execution
   - coverage.py cannot track across QThread boundaries
   - Maximum achievable: 93% (66/71 statements)
   - Tests exist and pass: test_run_with_unknown_operation, test_run_exception_*

### Dead Code (No Tests Needed)
1. **lazy_utils.py** - Never imported
   - 0% coverage expected
   - Recommendation: Remove file or add to codebase if needed
   - Impact: N/A

## Recommendations for Phase 4E (UI Module)

### Known Issues
- Full test suite hangs on UI dialog tests around 47% mark
- Specific hanging area: `test_dependency_dialog.py` → `test_dialog_manager.py`
- Affects: ~8 UI module files remaining in Phase 4C scope

### Suggested Approach
1. Run UI tests in isolation: `pytest tests/unit/ui/ --cov=src/asciidoc_artisan/ui`
2. Identify specific hanging tests with timeout: `pytest --timeout=30`
3. Skip problematic tests temporarily: `@pytest.mark.skip(reason="Hangs, needs investigation")`
4. Use module-by-module testing to isolate issues

### Test Execution Strategy
- Primary: `pytest -m "not slow" --maxfail=5 -x` (fast, reliable)
- Per-module: `pytest tests/unit/MODULE/ --cov=asciidoc_artisan.MODULE`
- Avoid: Full suite with HTML coverage (hangs at 47%)

## Summary Statistics

**Phase 4C Results:**
- Files improved: 7/14 (50%)
- Files at 100%: 4 (gpu_detection, git_worker, github_cli_worker, pandoc_worker)
- Files at 97%+: 1 (document_converter)
- Files at Qt max: 2 (optimized_worker_pool 98%, claude_worker 93%)
- Dead code identified: 1 (lazy_utils)
- Test pass rate: 99.8% (5467/5479 non-slow tests)

**Remaining for Phase 4E:**
- UI module files: ~7-8 files
- Estimated effort: 3-4 weeks (per QA audit)
- Known blocker: UI test suite hangs

---

**Created:** 2025-11-16
**Last Updated:** 2025-11-16
**Status:** Active tracking for Phase 4C completion, informational for Phase 4E
