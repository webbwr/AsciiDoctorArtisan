# Worker Thread Isolation Fix

**Date:** November 4, 2025
**Status:** Planning Document
**Priority:** Medium
**Estimated Effort:** 2-3 hours

## Problem

The test `test_worker_response_connection` in `tests/integration/test_chat_integration.py` passes when run alone but causes Python fatal crash when run with other tests.

**Current Status:** `@pytest.mark.skip`

**Error:**
```
Fatal Python error: Aborted

Thread 0x00007773ae0f06c0 (most recent call first):
  File "/usr/lib/python3.12/threading.py", line 359 in wait
  ...
```

## Root Cause

### Issue 1: Qt Worker Thread Lifecycle Management

Multiple tests create `AsciiDocEditor` instances, each initializing:
- `OllamaChatWorker` (QThread)
- `ClaudeWorker` (QThread)
- `GitWorker` (QThread)
- `PandocWorker` (QThread)
- `PreviewWorker` (QThread)

**Problem:** Worker threads from previous tests don't fully terminate before next test starts.

**Evidence:**
- Test passes when run alone (clean state)
- Test crashes when run with others (thread overlap)
- Crash occurs during QThread cleanup phase

### Issue 2: Qt Event Loop + Python Threading Conflicts

Qt's event loop and Python's threading model conflict during test teardown:

1. Test creates `QApplication` and `QThread` workers
2. Test completes, `qtbot` calls `window.close()`
3. Qt tries to clean up worker threads
4. Some threads are blocked waiting for signals/slots
5. Python's threading module tries to force cleanup
6. Threads can't terminate → Fatal abort

---

## Current Test Implementation

**File:** `tests/integration/test_chat_integration.py:199-226`

```python
@pytest.mark.skip(reason="Causes Python fatal crash when run with other tests - needs better worker thread isolation (Nov 2025)")
def test_worker_response_connection(self, main_window, qtbot):
    """Test that worker responses connect to chat manager."""
    import time
    from asciidoc_artisan.core.models import ChatMessage

    with qtbot.waitSignal(
        main_window.ollama_chat_worker.chat_response_ready, timeout=100
    ) as blocker:
        test_message = ChatMessage(
            role="assistant",
            content="Test response",
            timestamp=time.time(),
            model="test-model",
            context_mode="general"
        )
        main_window.ollama_chat_worker.chat_response_ready.emit(test_message)

    assert blocker.signal_triggered
```

---

## Solution: Proper Worker Thread Teardown

### Phase 1: Add Explicit Worker Cleanup to Fixture

**File:** `tests/integration/test_chat_integration.py`

**Before:**
```python
@pytest.fixture
def main_window(qtbot, test_settings):
    from unittest.mock import patch, Mock

    with patch(...):
        window = AsciiDocEditor()
        qtbot.addWidget(window)
        return window
    # qtbot handles cleanup (NOT sufficient for threads)
```

**After:**
```python
@pytest.fixture
def main_window(qtbot, test_settings):
    from unittest.mock import patch, Mock

    with patch(...):
        window = AsciiDocEditor()
        qtbot.addWidget(window)

        yield window

        # CRITICAL: Explicit worker cleanup BEFORE qtbot cleanup
        _cleanup_worker_threads(window, qtbot)


def _cleanup_worker_threads(window, qtbot):
    """Properly terminate all worker threads."""
    workers = [
        ('git_thread', 'git_worker'),
        ('pandoc_thread', 'pandoc_worker'),
        ('preview_thread', 'preview_worker'),
        ('ollama_chat_thread', 'ollama_chat_worker'),
        # Note: claude_thread added in v1.10.0
    ]

    for thread_attr, worker_attr in workers:
        if hasattr(window, thread_attr):
            thread = getattr(window, thread_attr)
            worker = getattr(window, worker_attr, None)

            if thread and thread.isRunning():
                # Step 1: Stop worker gracefully
                if worker and hasattr(worker, 'stop'):
                    worker.stop()

                # Step 2: Quit thread
                thread.quit()

                # Step 3: Wait for termination (with timeout)
                if not thread.wait(2000):  # 2 second timeout
                    # Step 4: Force terminate if needed
                    thread.terminate()
                    thread.wait(500)  # Wait 500ms for termination

                # Step 5: Verify thread stopped
                assert not thread.isRunning(), f"{thread_attr} still running after cleanup"
```

### Phase 2: Add Worker State Validation

**File:** `tests/integration/test_chat_integration.py`

```python
def test_worker_response_connection(self, main_window, qtbot):
    """Test that worker responses connect to chat manager."""
    import time
    from asciidoc_artisan.core.models import ChatMessage

    # Verify worker is in clean state
    assert main_window.ollama_chat_thread.isRunning()
    assert not main_window.ollama_chat_worker.isRunning()  # Not processing

    with qtbot.waitSignal(
        main_window.ollama_chat_worker.chat_response_ready, timeout=100
    ) as blocker:
        test_message = ChatMessage(
            role="assistant",
            content="Test response",
            timestamp=time.time(),
            model="test-model",
            context_mode="general"
        )
        main_window.ollama_chat_worker.chat_response_ready.emit(test_message)

    assert blocker.signal_triggered

    # Verify worker still in good state after test
    assert main_window.ollama_chat_thread.isRunning()
```

### Phase 3: Add Test Isolation with Module-Scoped Fixture

For tests that don't modify state, share window across tests:

```python
@pytest.fixture(scope="module")
def shared_main_window(qapp, test_settings):
    """Module-scoped window for read-only tests."""
    from unittest.mock import patch, Mock

    with patch(...):
        window = AsciiDocEditor()
        yield window

        # Cleanup at module end
        _cleanup_worker_threads(window, None)
        window.close()
        window.deleteLater()
```

---

## Alternative Solution: Mock Worker Threads Entirely

If proper cleanup is too complex, mock the workers:

```python
@pytest.fixture
def main_window_with_mocked_workers(qtbot, test_settings):
    """Create window with mocked worker threads (no real threads)."""
    from unittest.mock import patch, Mock, MagicMock

    with patch(...), \
         patch("asciidoc_artisan.workers.ollama_chat_worker.OllamaChatWorker") as mock_worker, \
         patch("PySide6.QtCore.QThread") as mock_thread:

        # Setup mocks
        mock_worker_instance = MagicMock()
        mock_worker_instance.chat_response_ready = MagicMock()
        mock_worker.return_value = mock_worker_instance

        mock_thread_instance = MagicMock()
        mock_thread_instance.isRunning.return_value = True
        mock_thread.return_value = mock_thread_instance

        window = AsciiDocEditor()
        qtbot.addWidget(window)

        # Replace real workers with mocks
        window.ollama_chat_worker = mock_worker_instance
        window.ollama_chat_thread = mock_thread_instance

        return window

    # No cleanup needed (no real threads)
```

---

## Implementation Plan

### Step 1: Add Helper Function (30 minutes)
```python
def _cleanup_worker_threads(window, qtbot):
    """Helper to properly cleanup all worker threads."""
    # Implementation as shown above
```

### Step 2: Update Fixture (15 minutes)
Convert `return` to `yield` and add cleanup call.

### Step 3: Test with Single Test (15 minutes)
```bash
pytest tests/integration/test_chat_integration.py::TestChatWorkerIntegration::test_worker_response_connection -v
```

### Step 4: Test with Full Suite (30 minutes)
```bash
pytest tests/integration/test_chat_integration.py -v
```

### Step 5: Remove Skip Decorator (5 minutes)
Remove `@pytest.mark.skip` from test.

### Step 6: Verify No Crashes (1 hour)
Run full test suite multiple times to ensure stability.

**Total Time:** ~2-3 hours

---

## Success Criteria

1. ✅ Test passes when run alone
2. ✅ Test passes when run with other chat integration tests
3. ✅ Test passes when run in full test suite
4. ✅ No Python fatal crashes
5. ✅ All worker threads properly terminated after test
6. ✅ No memory leaks from lingering threads

---

## Testing Strategy

### Level 1: Single Test
```bash
pytest tests/integration/test_chat_integration.py::TestChatWorkerIntegration::test_worker_response_connection -v --count=10
```
Run 10 times to verify stability.

### Level 2: Test Class
```bash
pytest tests/integration/test_chat_integration.py::TestChatWorkerIntegration -v
```

### Level 3: Test File
```bash
pytest tests/integration/test_chat_integration.py -v
```

### Level 4: Full Integration Suite
```bash
pytest tests/integration/ -v --timeout=180
```

### Level 5: Full Test Suite
```bash
pytest tests/ -v -m "not slow"
```

---

## Risks & Mitigation

### Risk 1: Deadlock During Cleanup
**Symptom:** Thread.wait() times out
**Mitigation:** Use terminate() as fallback, log warning

### Risk 2: Crash Moves to Different Test
**Symptom:** Different test now crashes
**Mitigation:** Apply cleanup to ALL fixtures creating windows

### Risk 3: Tests Become Flaky
**Symptom:** Random failures due to timing
**Mitigation:** Increase wait timeouts, add retry logic

---

## Verification Checklist

After implementation:

- [ ] Test passes individually (10/10 runs)
- [ ] Test passes in class (no crashes)
- [ ] Test passes in file (no crashes)
- [ ] Test passes in full suite (no crashes)
- [ ] Thread cleanup verified (no lingering threads)
- [ ] Memory usage stable (no leaks)
- [ ] No performance regression
- [ ] Documentation updated (remove skip reason)

---

## Related Files

- `tests/integration/test_chat_integration.py` - Test file
- `src/asciidoc_artisan/workers/ollama_chat_worker.py` - Worker implementation
- `src/asciidoc_artisan/ui/main_window.py` - Window worker initialization
- `CHAT_INTEGRATION_TEST_FIX.md` - Related crash fix documentation

---

## References

- Qt QThread docs: https://doc.qt.io/qt-6/qthread.html
- pytest-qt docs: https://pytest-qt.readthedocs.io/
- Python threading: https://docs.python.org/3/library/threading.html

---

*Document created: November 4, 2025*
*Status: Ready for implementation*
*Priority: Medium*
*Estimated effort: 2-3 hours*
