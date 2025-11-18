# Mock Assertion Failures Analysis

**Date:** 2025-11-16
**Category:** Priority 2 Test Logic Bugs (6 tests)

## Root Cause Analysis

### Test Category 1: prompt_save_before_action Tests (4 failures)

**Affected Tests:**
1. `test_prompt_save_user_clicks_save` - save_file not called (expected 1, actual 0)
2. `test_prompt_save_user_clicks_cancel` - returns True instead of False
3. `test_prompt_save_with_different_actions` - save_file not called (expected 3, actual 0)
4. `test_prompt_save_file_fails` - returns True instead of False

**Root Cause:** `dialog_manager.py:712` early return for pytest environment

```python
# Auto-continue in tests to prevent blocking.
if os.environ.get("PYTEST_CURRENT_TEST"):
    return True  # ❌ Bypasses entire dialog logic!
```

**Why Tests Fail:**
- pytest automatically sets `PYTEST_CURRENT_TEST` environment variable
- Method returns `True` immediately without showing dialog or calling `save_file()`
- Tests mock `QMessageBox.question` but it never gets executed
- Tests expect `save_file()` to be called but early return prevents it

**Solution:** Tests must bypass the pytest guard by mocking `os.environ.get`

**Fix Strategy:**
```python
@patch("asciidoc_artisan.ui.dialog_manager.QMessageBox")
@patch("os.environ.get", return_value=None)  # ← Add this
def test_prompt_save_user_clicks_save(self, mock_env, mock_msgbox_cls, mock_main_window):
    ...
```

**Alternative (monkeypatch):**
```python
def test_prompt_save_user_clicks_save(self, mock_msgbox_cls, mock_main_window, monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    ...
```

---

### Test Category 2: test_close_event_delegates_to_editor_state (1 failure)

**Error:** `window.editor_state.handle_close_event` not called (expected 1, actual 0)

**Additional Error:** RuntimeError during teardown - "Signal source has been deleted"

**Root Cause:** Unknown - need to examine `closeEvent` implementation in main_window.py

**Test Location:** `test_main_window.py:1453`

**Next Step:** Read main_window.py closeEvent method to understand delegation logic

---

### Test Category 3: test_workers_initialized (1 failure)

**Error:** `assert hasattr(window, "github_cli_worker")` - returns False

**Root Cause:** Workers refactored - architectural mismatch between test expectations and implementation

**Investigation Results (Commit 7faa3c1):**
- Workers managed by `worker_manager` (main_window.py:312)
- Test expects: `window.{git,pandoc,preview,github_cli,ollama_chat}_worker`
- Actual: Workers in `window.worker_manager.setup_workers_and_threads()`
- No direct worker attributes found on window or worker_manager

**Fix Options:**
1. Update test to check `worker_manager` existence (minimal fix)
2. Add property accessors: `@property def github_cli_worker() -> Worker`
3. Refactor test to match new architecture

**Status:** Deferred - requires architectural decision or test refactoring

---

## Implementation Plan

### Phase 1: Fix prompt_save Tests (4 tests)
**Approach:** Add `os.environ.get` mock to bypass pytest guard

**Changes:** `tests/unit/ui/test_dialog_manager.py`

For each of these 4 tests:
- `test_prompt_save_user_clicks_save` (line 1698)
- `test_prompt_save_user_clicks_cancel` (line 1734)
- `test_prompt_save_with_different_actions` (line 1752)
- `test_prompt_save_file_fails` (line 1777)

Add `@patch("os.environ.get", return_value=None)` above `@patch("asciidoc_artisan.ui.dialog_manager.QMessageBox")`

Update function signatures to include `mock_env` parameter first.

### Phase 2: Investigate closeEvent Delegation (1 test)
1. Read main_window.py closeEvent method
2. Verify editor_state.handle_close_event exists and is called
3. Determine why mock isn't being called
4. Fix test or implementation as needed

### Phase 3: Investigate Worker Initialization (1 test)
1. Search main_window.py for worker initialization
2. Verify actual attribute names
3. Check if workers are in worker_manager instead
4. Fix test expectations to match actual implementation

---

## Expected Results

**After Phase 1:** 4/6 tests pass (prompt_save tests fixed)
**After Phase 2:** 5/6 tests pass (closeEvent test fixed)
**After Phase 3:** 6/6 tests pass (worker test fixed)

**Total Progress:**
- Fixed so far: 6 (3 Theme Manager + 3 QLabel)
- After mock fixes: 12/24 Priority 2 tests passing
- Remaining: 12 tests (4 other assertions + 6 dialog init + 3 GPU)
