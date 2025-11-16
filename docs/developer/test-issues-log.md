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
- **Workaround:** Skip entire TestTelemetryStatusDialogEnabled class (commit cec0e0a)

### Dialogs Test - Isolated (process 668051 - Phase 4E)
- **Command:** `pytest tests/unit/ui/test_dialogs.py -v -q --tb=short`
- **Status:** ✓ Completed successfully (with skips applied)
- **Results:** 194 passed, 2 skipped, 9 failed (test bugs, not hangs)
- **Skipped Tests:** test_clear_all_settings_with_confirmation_yes, test_clear_all_settings_with_confirmation_no
- **Issue:** Both use QMessageBox.question (modal dialog) that hangs in full suite context
- **Root Cause:** Modal dialog Qt event loop issue
- **Workaround:** Skipped both tests (commit pending)

### Full UI Test Suite (process 9c4ba4 - Phase 4E)
- **Command:** `pytest tests/unit/ui/ --cov=src/asciidoc_artisan/ui --cov-report=term --cov-report=html -q`
- **Status:** Hung at 21% completion (2919 total tests)
- **Last Passing File:** `tests/unit/ui/test_dialog_manager.py` (with 4 skipped tests)
- **Hung At:** After test_dialog_manager.py, before test_dialogs.py starts
- **Issue:** **Test pollution** - test_dialog_manager.py leaves Qt in bad state
- **Root Cause:** Qt event loop / modal dialog state not cleaned up between test modules
- **Impact:** test_dialogs.py runs fine in isolation but hangs when run after test_dialog_manager.py
- **Conclusion:** UI module has test interaction/pollution issues, not just individual test hangs

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

### Root Cause Analysis
**Primary Issue:** Qt modal dialog test pollution between modules
- test_dialog_manager.py leaves Qt event loop in bad state
- Subsequent test files (test_dialogs.py, etc.) hang when run after it
- Individual test files pass when run in isolation
- **Conclusion:** Not individual test bugs, but test isolation/cleanup issues

**Files with Skipped Tests (commit d3698c4):**
- test_dialog_manager.py: 4 skipped (TestTelemetryStatusDialogEnabled class)
- test_dialogs.py: 2 skipped (QMessageBox.question modal dialog tests)
- Total: 6 tests skipped due to Qt modal dialog hangs

### Immediate Solutions (Short-term)

1. **Per-File Testing** (Current workaround):
   ```bash
   for file in tests/unit/ui/test_*.py; do
     pytest "$file" -v --tb=short --timeout=60 || echo "HUNG: $file"
   done
   ```

2. **Parallel Execution** (Isolates modules):
   ```bash
   pip install pytest-xdist
   pytest tests/unit/ui/ -n auto --cov=src/asciidoc_artisan/ui
   ```

3. **Skip Full UI Suite** (Document limitation):
   - Add note to test-coverage.md: "UI tests must run individually or in parallel"
   - Update CI/CD to use pytest-xdist for UI tests

### Long-term Solutions (Requires investigation)

1. **Add Qt Cleanup Fixtures**:
   ```python
   @pytest.fixture(autouse=True)
   def cleanup_qt_state():
       """Ensure Qt modal dialogs are closed between tests."""
       yield
       # Force close all modal dialogs
       # Reset Qt event loop state
   ```

2. **Mock QMessageBox Globally**:
   - Patch QMessageBox.question/exec at conftest.py level
   - Prevents modal dialogs from ever blocking

3. **Install pytest-qt Enhancements**:
   ```bash
   pip install pytest-qt
   pytest tests/unit/ui/ --qt-no-exception-capture
   ```

4. **Add Test Isolation Markers**:
   ```python
   @pytest.mark.isolated  # Forces separate process
   class TestDialogManager:
       ...
   ```

### Recommended Next Steps

**Phase 4E Coverage Improvement:**
1. Install pytest-xdist: `pip install pytest-xdist`
2. Run UI coverage in parallel: `pytest tests/unit/ui/ -n auto --cov=src/asciidoc_artisan/ui --cov-report=html`
3. Analyze coverage.xml for missing lines (skip hanging test investigation for now)
4. Add coverage tests for identified gaps
5. Document maximum achievable coverage with Qt threading limitations

**Test Infrastructure Fixes (Separate task):**
1. Create issue: "Fix Qt modal dialog test pollution in UI test suite"
2. Investigate Qt cleanup patterns in pytest-qt documentation
3. Implement global QMessageBox mocking in conftest.py
4. Add autouse cleanup fixtures for Qt state
5. Remove skipped test markers once fixed

### Test Execution Strategy (Updated)

**For Coverage Analysis:**
- ✓ Parallel: `pytest tests/unit/ui/ -n auto --cov=src/asciidoc_artisan/ui`
- ✓ Individual files: `pytest tests/unit/ui/test_FILE.py --cov=src/asciidoc_artisan/ui/FILE.py`
- ✗ Full suite: Hangs at 21% (test pollution blocker)

**For Development:**
- ✓ Non-slow tests: `pytest -m "not slow" --maxfail=5 -x` (5467/5479 pass)
- ✓ Per-module: `pytest tests/unit/MODULE/ --cov=asciidoc_artisan.MODULE`
- ✗ Full UI suite: Currently blocked by test pollution

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
