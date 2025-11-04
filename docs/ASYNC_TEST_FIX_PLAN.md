# Async Test Fix Plan - Phase 2 Quick Wins

**Date:** November 4, 2025
**Status:** In Progress
**Priority:** HIGH
**Estimated Effort:** 12-16 hours

---

## Executive Summary

**Scope:** Fix 14 skipped async tests + 1 worker thread isolation test
**Total Tests to Fix:** 15
**Current Test Health:** 98%+ pass rate
**Target:** 100% pass rate with all skipped tests enabled

### Tests Breakdown

| Category | File | Tests | Effort |
|----------|------|-------|--------|
| Unit Tests | test_file_handler.py | 10 | 8-10 hours |
| Integration | test_ui_integration.py | 1 | 1-2 hours |
| Integration | test_memory_leaks.py | 1 | 1-2 hours |
| Integration | test_stress.py | 1 | 1 hour |
| Integration | test_performance_regression.py | 1 | 1 hour |
| Thread Isolation | test_chat_integration.py | 1 | 2-3 hours |
| **TOTAL** | **6 files** | **15** | **14-19 hours** |

---

## Phase 1: Unit Tests (10 tests, 8-10 hours)

### File: `tests/unit/ui/test_file_handler.py`

All tests use `FileHandler` which migrated to async I/O in v1.7.0. Methods changed:
- `_load_file_content()` → `_load_file_async()`
- `save_file()` → `save_file_async()`

**Tests to Fix:**

#### 1. test_load_file_content (Line 195)
**What it tests:** Loading file content into editor
**Required changes:**
- Add `@pytest.mark.asyncio` decorator
- Convert to `async def`
- Use `await handler._load_file_async(test_file)`
- Mock `AsyncFileHandler` signals

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_load_file_content_async(handler, tmp_path, mock_editor, qtbot):
    """Test loading file content asynchronously."""
    test_file = tmp_path / "test.adoc"
    test_content = "= Test Document\n\nTest content"
    test_file.write_text(test_content)

    with qtbot.waitSignal(handler.file_opened, timeout=2000):
        await handler._load_file_async(test_file)

    assert mock_editor.toPlainText() == test_content
    assert handler.current_file_path == test_file
    assert handler.unsaved_changes is False
```

#### 2. test_load_file_tracks_loading_state (Line 210)
**What it tests:** `is_opening_file` flag during async load
**Required changes:**
- Convert to async
- Use `await handler._load_file_async()`
- Verify flag state during I/O operation

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_load_file_tracks_loading_state_async(handler, tmp_path):
    """Test loading state is tracked during async file load."""
    test_file = tmp_path / "test.adoc"
    test_file.write_text("Content")

    assert handler.is_opening_file is False

    # Mock async read to check state mid-operation
    original_load = handler._load_file_async

    async def tracked_load(*args, **kwargs):
        assert handler.is_opening_file is True
        return await original_load(*args, **kwargs)

    with patch.object(handler, "_load_file_async", tracked_load):
        await handler._load_file_async(test_file)

    assert handler.is_opening_file is False
```

#### 3. test_load_file_updates_settings (Line 231)
**What it tests:** Settings updated with last directory
**Required changes:**
- Convert to async
- Verify settings persistence after async load

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_load_file_updates_settings_async(handler, tmp_path, mock_settings_manager):
    """Test loading file updates last directory in settings."""
    test_file = tmp_path / "test.adoc"
    test_file.write_text("Content")

    settings = Mock()
    mock_settings_manager.load_settings.return_value = settings

    await handler._load_file_async(test_file)

    assert settings.last_directory == str(tmp_path)
    mock_settings_manager.save_settings.assert_called_with(settings)
```

#### 4. test_load_file_emits_signal (Line 246)
**What it tests:** `file_opened` signal emitted on load
**Required changes:**
- Convert to async
- Use `qtbot.waitSignal()` with async operation

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_load_file_emits_signal_async(handler, tmp_path, qtbot):
    """Test loading file emits file_opened signal."""
    test_file = tmp_path / "test.adoc"
    test_file.write_text("Content")

    with qtbot.waitSignal(handler.file_opened, timeout=2000) as blocker:
        await handler._load_file_async(test_file)

    assert blocker.args[0] == test_file
```

#### 5. test_save_file_with_path (Line 269)
**What it tests:** Saving file with existing path
**Required changes:**
- Convert to async
- Use `await handler.save_file_async(save_as=False)`

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_file_with_path_async(handler, tmp_path, mock_editor):
    """Test saving file with existing path asynchronously."""
    test_file = tmp_path / "save_test.adoc"
    handler.current_file_path = test_file
    handler.unsaved_changes = True
    mock_editor.setPlainText("Content to save")

    result = await handler.save_file_async(save_as=False)

    assert result is True
    assert test_file.read_text() == "Content to save"
    assert handler.unsaved_changes is False
```

#### 6. test_save_file_emits_signal (Line 284)
**What it tests:** `file_saved` signal on save
**Required changes:**
- Convert to async
- Wait for signal during async save

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_file_emits_signal_async(handler, tmp_path, mock_editor, qtbot):
    """Test saving file emits file_saved signal."""
    test_file = tmp_path / "signal_test.adoc"
    handler.current_file_path = test_file
    mock_editor.setPlainText("Content")

    with qtbot.waitSignal(handler.file_saved, timeout=2000) as blocker:
        await handler.save_file_async(save_as=False)

    assert blocker.args[0] == test_file
```

#### 7. test_save_file_updates_settings (Line 297)
**What it tests:** Settings updated after save
**Required changes:**
- Convert to async
- Verify settings persistence

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_file_updates_settings_async(handler, tmp_path, mock_editor, mock_settings_manager):
    """Test saving file updates last directory."""
    test_file = tmp_path / "settings_test.adoc"
    handler.current_file_path = test_file
    mock_editor.setPlainText("Content")

    settings = Mock()
    mock_settings_manager.load_settings.return_value = settings

    await handler.save_file_async(save_as=False)

    assert settings.last_directory == str(tmp_path)
    mock_settings_manager.save_settings.assert_called_with(settings)
```

#### 8. test_save_file_error_handling (Line 313)
**What it tests:** Error handling on save failure
**Required changes:**
- Convert to async
- Verify error messages on invalid paths

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_save_file_error_handling_async(handler, mock_editor, mock_status_manager):
    """Test error handling when async save fails."""
    handler.current_file_path = Path("/invalid/path/file.adoc")
    mock_editor.setPlainText("Content")

    result = await handler.save_file_async(save_as=False)

    assert result is False
    mock_status_manager.show_message.assert_called()
```

#### 9. test_prompt_save_before_action_save (Line 332)
**What it tests:** Prompt saves file when user chooses Save
**Required changes:**
- Convert to async
- Mock `save_file_async` instead of `save_file`

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_prompt_save_before_action_save_async(handler, tmp_path):
    """Test prompt saves file when user chooses Save."""
    handler.unsaved_changes = True
    handler.current_file_path = tmp_path / "test.adoc"
    handler.editor.setPlainText("Content")

    with patch("PySide6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
        with patch.object(handler, "save_file_async", return_value=True) as mock_save:
            result = await handler.prompt_save_before_action_async("test action")

    assert result is True
    mock_save.assert_called_once()
```

#### 10. test_prompt_save_before_action_cancel (Line 357)
**What it tests:** Prompt returns False when user cancels
**Required changes:**
- Convert to async (if prompt_save_before_action is async)

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_prompt_save_before_action_cancel_async(handler):
    """Test prompt returns False when user cancels."""
    handler.unsaved_changes = True

    with patch("PySide6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Cancel):
        result = await handler.prompt_save_before_action_async("test action")

    assert result is False
```

---

## Phase 2: Integration Tests (4 tests, 4-5 hours)

### Test 1: test_save_file_creates_file (test_ui_integration.py:88)
**What it tests:** File save creates file on disk
**Estimated effort:** 1-2 hours

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_file_creates_file_async(editor, qtbot):
    """Test async file save operation creates file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.adoc"
        editor.file_handler.current_file_path = test_file
        editor.editor.setPlainText("= Test Document\n\nContent")

        with qtbot.waitSignal(editor.file_handler.file_saved, timeout=2000):
            result = await editor.file_handler.save_file_async(save_as=False)

        assert result is True
        assert test_file.exists()
        assert "Test Document" in test_file.read_text()
```

### Test 2: test_file_handler_no_handle_leak (test_memory_leaks.py:84)
**What it tests:** File handles released after async operations
**Estimated effort:** 1-2 hours

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.memory
async def test_file_handler_no_handle_leak_async(qtbot):
    """Test async file handler doesn't leak file handles."""
    import psutil
    import tempfile

    process = psutil.Process()
    initial_handles = len(process.open_files())

    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        test_file = Path(f.name)
        f.write("= Test Document\n\nContent here.")

    try:
        handler = AsyncFileHandler()

        # Read file async
        read_result = None
        def on_read_complete(result):
            nonlocal read_result
            read_result = result

        handler.read_complete.connect(on_read_complete)
        handler.read_file_async(str(test_file))

        # Wait for read to complete
        await asyncio.sleep(0.1)

        # Verify file was read
        assert read_result is not None
        assert read_result.success

        # Check handles released
        final_handles = len(process.open_files())
        assert final_handles == initial_handles, f"Handle leak: {final_handles} vs {initial_handles}"
    finally:
        test_file.unlink()
```

### Test 3: test_large_file_handling (test_stress.py:148)
**What it tests:** Streaming large files with async I/O
**Estimated effort:** 1 hour

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_large_file_handling_async():
    """Test async handling of large files (>10MB)."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        # Create 10MB file
        large_content = "= Large Document\n\n" + ("Test line\n" * 500000)
        f.write(large_content)
        test_file = Path(f.name)

    try:
        handler = AsyncFileHandler()

        # Track chunks
        chunks_received = []
        def on_progress(chunk):
            chunks_received.append(chunk)

        handler.read_progress.connect(on_progress)

        # Read large file async
        read_complete = False
        def on_complete(result):
            nonlocal read_complete
            read_complete = True

        handler.read_complete.connect(on_complete)
        handler.read_file_async(str(test_file))

        # Wait for completion (max 10 seconds)
        timeout = 10
        while not read_complete and timeout > 0:
            await asyncio.sleep(0.1)
            timeout -= 0.1

        assert read_complete, "Large file read timed out"
        assert len(chunks_received) > 0, "No chunks received"
    finally:
        test_file.unlink()
```

### Test 4: test_file_save_performance (test_performance_regression.py:66)
**What it tests:** Async save meets performance requirements
**Estimated effort:** 1 hour

**Target code:**
```python
@pytest.mark.asyncio
@pytest.mark.performance
async def test_file_save_performance_async():
    """Test async file save meets performance requirements (<100ms)."""
    import tempfile
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "perf_test.adoc"
        content = "= Performance Test\n\n" + ("Test content\n" * 1000)

        handler = AsyncFileHandler()

        # Measure async save time
        save_complete = False
        save_time = None

        def on_complete(result):
            nonlocal save_complete
            save_complete = True

        handler.write_complete.connect(on_complete)

        start = time.perf_counter()
        handler.write_file_async(str(test_file), content)

        # Wait for completion
        timeout = 1.0
        while not save_complete and timeout > 0:
            await asyncio.sleep(0.01)
            timeout -= 0.01

        save_time = (time.perf_counter() - start) * 1000  # Convert to ms

        assert save_complete, "Save did not complete"
        assert save_time < 100, f"Save too slow: {save_time:.2f}ms > 100ms"
```

---

## Phase 3: Worker Thread Isolation (1 test, 2-3 hours)

### Test: test_worker_response_connection (test_chat_integration.py:199)

**Root Cause:** Qt worker threads not properly cleaned up between tests, causing Python fatal crash.

**Solution:** Implement comprehensive worker thread cleanup in fixture teardown.

**Required changes:**

1. **Update conftest.py** with worker cleanup fixture:
```python
@pytest.fixture
def cleanup_workers():
    """Ensure all worker threads are properly terminated after test."""
    yield

    # Cleanup phase
    import gc
    from PySide6.QtCore import QThreadPool

    # Force thread pool cleanup
    QThreadPool.globalInstance().waitForDone(2000)

    # Force garbage collection
    gc.collect()
```

2. **Update test** with proper thread lifecycle:
```python
@pytest.mark.unit
def test_worker_response_connection(main_window, qtbot, cleanup_workers):
    """Test that worker responses connect to chat manager.

    Uses cleanup_workers fixture to ensure proper thread termination.
    """
    # Get the Ollama chat worker
    worker = main_window.ollama_chat_worker
    chat_manager = main_window.chat_manager

    # Test signal connection
    with qtbot.waitSignal(chat_manager.response_received, timeout=5000) as blocker:
        # Trigger worker response
        mock_result = OllamaChatResult(
            success=True,
            message="Test response",
            model="test-model"
        )
        worker.chat_response_ready.emit(mock_result)

    # Verify signal received
    assert blocker.signal_triggered
    assert blocker.args[0].message == "Test response"

    # Explicit cleanup before test ends
    if worker.isRunning():
        worker.stop()
        worker.quit()
        worker.wait(2000)
```

3. **Update main_window fixture** in test_chat_integration.py:
```python
@pytest.fixture
def main_window(qtbot, test_settings):
    """Create main window for testing with comprehensive cleanup."""
    from unittest.mock import patch, Mock

    with patch(
        "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings",
        return_value=test_settings,
    ), patch(
        "asciidoc_artisan.claude.claude_client.Anthropic"
    ) as mock_anthropic, patch(
        "asciidoc_artisan.claude.claude_client.SecureCredentials"
    ) as mock_creds:
        mock_creds_instance = Mock()
        mock_creds_instance.get_anthropic_key.return_value = None
        mock_creds.return_value = mock_creds_instance

        window = AsciiDocEditor()
        qtbot.addWidget(window)

        yield window

        # Comprehensive cleanup
        workers = [
            ('git_thread', 'git_worker'),
            ('pandoc_thread', 'pandoc_worker'),
            ('preview_thread', 'preview_worker'),
            ('ollama_chat_thread', 'ollama_chat_worker'),
        ]

        for thread_attr, worker_attr in workers:
            if hasattr(window, thread_attr):
                thread = getattr(window, thread_attr)
                worker = getattr(window, worker_attr, None)

                if worker and hasattr(worker, 'stop'):
                    worker.stop()

                if thread and thread.isRunning():
                    thread.quit()
                    if not thread.wait(2000):
                        thread.terminate()
                        thread.wait(500)

        window.close()
        window.deleteLater()
```

**Testing strategy:**
1. Run test alone: `pytest tests/integration/test_chat_integration.py::TestChatIntegration::test_worker_response_connection -v`
2. Run with full suite to verify no crashes
3. Run 10 times in a row to verify stability: `for i in {1..10}; do pytest tests/integration/test_chat_integration.py -v || break; done`

---

## Implementation Strategy

### Step 1: Setup (30 minutes)
1. ✅ Create this plan document
2. Install/verify dependencies:
   ```bash
   pip install pytest-asyncio anyio psutil
   ```
3. Update pytest.ini with asyncio settings:
   ```ini
   [pytest]
   asyncio_mode = auto
   ```

### Step 2: Phase 1 - Unit Tests (8-10 hours)
**Priority: HIGH**
**Order:** Fix tests 1-10 in test_file_handler.py

1. Read FileHandler implementation to understand async API
2. Fix test 1 (test_load_file_content)
3. Run test, verify passing
4. Fix tests 2-10 sequentially
5. Run full test_file_handler.py suite
6. Verify all 10 tests passing

**Validation:**
```bash
pytest tests/unit/ui/test_file_handler.py -v -k async
```

### Step 3: Phase 2 - Integration Tests (4-5 hours)
**Priority: MEDIUM**
**Order:** Fix integration tests sequentially

1. Fix test_save_file_creates_file
2. Fix test_file_handler_no_handle_leak
3. Fix test_large_file_handling
4. Fix test_file_save_performance
5. Run full integration suite

**Validation:**
```bash
pytest tests/integration/ -v -m asyncio
```

### Step 4: Phase 3 - Worker Thread Isolation (2-3 hours)
**Priority: HIGH (prevents Python crashes)**
**Order:** Single test fix with comprehensive cleanup

1. Implement cleanup_workers fixture
2. Update main_window fixture
3. Update test_worker_response_connection
4. Test isolation thoroughly

**Validation:**
```bash
# Test alone
pytest tests/integration/test_chat_integration.py::TestChatIntegration::test_worker_response_connection -v

# Test with full suite
pytest tests/ -v

# Stress test (10 runs)
for i in {1..10}; do
    pytest tests/integration/test_chat_integration.py -v || break
done
```

### Step 5: Verification (1 hour)
1. Run full test suite: `pytest tests/ -v`
2. Check for any remaining skipped tests
3. Verify 100% pass rate (no failures, no crashes)
4. Generate coverage report

**Validation:**
```bash
pytest tests/ -v --cov=src/asciidoc_artisan --cov-report=html
```

### Step 6: Documentation (1 hour)
1. Update TEST_STATUS.md with new test counts
2. Update ASYNC_TEST_REFACTORING_REQUIREMENTS.md (mark as complete)
3. Update WORKER_THREAD_ISOLATION_FIX.md (mark as complete)
4. Update PHASE_2_ROADMAP.md

### Step 7: Commit & Push (30 minutes)
1. Commit changes with detailed message
2. Push to origin/main
3. Verify CI/CD passes (if configured)

---

## Success Criteria

- ✅ All 14 async tests converted and passing
- ✅ Worker thread isolation test passing
- ✅ Zero Python fatal crashes
- ✅ 100% test pass rate (no failures, no skips except live_api)
- ✅ Full test suite runs without crashes
- ✅ Documentation updated
- ✅ Changes committed and pushed

---

## Risk Mitigation

### Risk 1: Async test complexity
**Mitigation:** Start with simplest test (test_load_file_content), use as template

### Risk 2: Qt signal/async integration
**Mitigation:** Use `qtbot.waitSignal()` with proper timeout (2000ms minimum)

### Risk 3: Thread cleanup still causes crashes
**Mitigation:** Implement multiple cleanup strategies (stop, quit, terminate, wait)

### Risk 4: Time overrun
**Mitigation:** Break work into 2-3 hour sessions, commit after each phase

---

## Timeline

**Total Effort:** 14-19 hours
**Recommended Schedule:** 2-3 days, 4-6 hours per day

**Day 1 (6 hours):**
- Setup + Phase 1 (tests 1-5)

**Day 2 (6 hours):**
- Phase 1 (tests 6-10) + Phase 2 (tests 1-2)

**Day 3 (4-6 hours):**
- Phase 2 (tests 3-4) + Phase 3 + Verification + Documentation + Commit

---

**Created:** November 4, 2025
**Status:** Ready for implementation
**Next Step:** Begin Phase 1, Test 1 (test_load_file_content)
