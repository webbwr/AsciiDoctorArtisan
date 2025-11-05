# Qt Threading Investigation - Worker Thread Isolation Issues

## Problem Statement

3 tests are skipped due to Qt worker thread isolation issues:
1. `test_ui_integration.py::test_save_file_creates_file_async` - Async file save test
2. `test_chat_integration.py::test_worker_response_connection` - Worker response connection
3. `test_async_file_handler.py` - 5 tests with Qt segfaults

All cause test hangs or Python fatal crashes when run with other tests.

## Root Cause Analysis

### Issue 1: Worker Thread Cleanup in pytest

**Problem:**
- Qt worker threads (QThread) started in fixtures persist across tests
- `QThread.deleteLater()` is asynchronous - not immediate
- Test teardown happens before threads fully cleaned up
- Next test starts with orphaned threads → crash/hang

**Evidence:**
- Tests pass individually: `pytest test_file.py::test_name` ✓
- Tests fail in suite: `pytest test_file.py` ✗
- Adding shutdown() fixed UI tests but not all cases

### Issue 2: QEventLoop and QApplication Lifecycle

**Problem:**
- `QApplication.exec()` blocks until quit() called
- Tests use `qtbot.waitSignal()` which runs sub-event loops
- Multiple event loops can interfere with each other
- Worker threads may emit signals after test completes

**Evidence:**
- Async tests especially problematic
- Tests with `@pytest.mark.asyncio` + Qt mixing two async systems

### Issue 3: Signal/Slot Connections Not Cleaned Up

**Problem:**
- Qt signals remain connected even after objects deleted
- Worker threads continue processing signals from previous tests
- Memory not freed until Python GC + Qt cleanup both complete

## Best Practices for Qt Testing with pytest

### 1. Explicit Thread Cleanup
```python
@pytest.fixture
def worker(qtbot):
    thread = QThread()
    worker = MyWorker()
    worker.moveToThread(thread)
    thread.start()

    yield worker

    # Explicit cleanup
    thread.quit()
    thread.wait(2000)  # Wait up to 2s
    worker.deleteLater()
    thread.deleteLater()
    qtbot.waitUntil(lambda: not thread.isRunning(), timeout=3000)
```

### 2. Process Isolation for Problematic Tests
```python
@pytest.mark.forked  # pytest-forked plugin
def test_with_worker_threads():
    # Runs in separate process
    # Clean slate each time
```

### 3. Fixture Scope Management
```python
@pytest.fixture(scope="function")  # New instance per test
def isolated_worker(qtbot):
    # Fresh worker each test
```

### 4. Mock Worker Threads in Unit Tests
```python
@pytest.fixture
def mock_worker(monkeypatch):
    # Don't actually start threads in unit tests
    mock = Mock(spec=MyWorker)
    monkeypatch.setattr("module.MyWorker", lambda: mock)
    return mock
```

## Recommended Solutions

### Short-term (v1.9.1):
✓ Skip problematic tests (done)
✓ Document in skip reason (done)
✓ Add worker shutdown to fixtures (done)

### Medium-term (v1.9.2):
1. **Install pytest-forked**: `pip install pytest-forked`
2. **Mark problematic tests**: `@pytest.mark.forked`
3. **Add explicit cleanup**: `qtbot.waitUntil()` for thread termination
4. **Separate async tests**: Don't mix `asyncio` + `QThread`

### Long-term (v2.0.0):
1. **Redesign async architecture**: Use pure asyncio or pure Qt, not both
2. **Worker pool refactor**: Better lifecycle management
3. **Test isolation layer**: Separate integration tests from worker thread tests

## Code Examples

### Fix 1: Better Fixture Cleanup
```python
@pytest.fixture
def editor_with_workers(qtbot):
    from unittest.mock import patch, Mock

    with patch("module.ClaudeWorker") as mock_claude:
        # Mock workers instead of real threads
        mock_instance = Mock()
        mock_claude.return_value = mock_instance

        editor = AsciiDocEditor()
        qtbot.addWidget(editor)

        yield editor

        # Cleanup mocked, no threads to clean
        editor.close()
```

### Fix 2: Process Isolation
```python
# In pytest.ini
[pytest]
markers =
    forked: Tests requiring process isolation

# In test file
@pytest.mark.forked
def test_worker_thread_isolation():
    # Runs in subprocess, can't interfere with other tests
```

### Fix 3: Explicit Thread Waits
```python
def test_with_proper_cleanup(editor, qtbot):
    # Test code...

    # Before fixture teardown
    if hasattr(editor, 'worker_manager'):
        editor.worker_manager.shutdown()

        # Wait for all threads to actually stop
        for thread in [editor.git_thread, editor.claude_thread]:
            if thread and thread.isRunning():
                qtbot.waitUntil(
                    lambda t=thread: not t.isRunning(),
                    timeout=3000
                )
```

## Dependencies Needed

```bash
# For process isolation
pip install pytest-forked

# For better async testing
pip install pytest-asyncio>=0.23.0

# Already have
pip install pytest-qt>=4.0.0
```

## Success Metrics

- [ ] All 3 skipped worker tests pass in isolation
- [ ] All 3 skipped worker tests pass in full suite
- [ ] No test hangs or crashes
- [ ] Test suite < 5 minutes total runtime

## Implementation Plan

### Phase 1: Add pytest-forked marker (v1.9.2)
```bash
# Add to requirements.txt
echo "pytest-forked>=1.6.0" >> requirements.txt

# Add to pytest.ini
markers =
    forked: Tests requiring process isolation (pytest-forked)
```

### Phase 2: Mark and test problematic tests (v1.9.2)
```python
@pytest.mark.forked
def test_save_file_creates_file_async():
    # Previously skipped test
    # Now runs in isolated subprocess
```

### Phase 3: Improve fixture cleanup (v1.9.2)
- Add `qtbot.waitUntil()` for thread termination
- Verify threads stopped before fixture teardown
- Add explicit signal disconnection

### Phase 4: Architecture review (v2.0.0)
- Evaluate async/Qt mixing
- Consider redesign if issues persist
- Document lessons learned

## References

- pytest-qt docs: https://pytest-qt.readthedocs.io/
- Qt threading best practices: https://doc.qt.io/qt-6/threads-qobject.html
- pytest-forked: https://github.com/pytest-dev/pytest-forked
- Qt QThread documentation: https://doc.qt.io/qt-6/qthread.html

## Related Issues

- Worker thread shutdown fixes: Commit 98c679f (Nov 5, 2025)
- Test hang investigation: This document
- Skipped tests tracking: See test files for `@pytest.mark.skip` decorators

---

*Last updated: November 5, 2025*
*Status: Investigation complete, implementation planned for v1.9.2*
