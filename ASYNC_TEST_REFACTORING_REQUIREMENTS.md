# Async Test Refactoring Requirements

**Date:** November 4, 2025
**Status:** Planning Document
**Priority:** Medium

## Overview

Four tests are currently skipped due to FileHandler migration to async I/O in v1.7.0. These tests need refactoring to use async/await patterns with pytest-asyncio.

## Affected Tests

### 1. test_save_file_creates_file
**File:** `tests/integration/test_ui_integration.py:88`
**Current Status:** `@pytest.mark.skip`
**Reason:** FileHandler now uses async I/O
**Complexity:** Medium (1-2 hours)

**Current Implementation:**
```python
@pytest.mark.skip(reason="Requires async refactoring - FileHandler now uses async I/O (v1.7.0)")
@patch("asciidoc_artisan.ui.main_window.atomic_save_text", return_value=True)
def test_save_file_creates_file(self, mock_save, editor, qtbot):
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.adoc"
        editor._current_file_path = test_file
        editor.editor.setPlainText("= Test")

        result = editor.save_file(save_as=False)  # Now async method
        assert result is True
```

**Required Changes:**
- Convert test to async: `async def test_save_file_creates_file_async(...)`
- Add `@pytest.mark.asyncio` decorator
- Mock `AsyncFileHandler.save_async()` instead of `atomic_save_text`
- Use `await editor.file_handler.save_file_async()`
- Update fixture to support async tests

**Target Implementation:**
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_file_creates_file_async(editor, qtbot):
    """Test async file save operation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.adoc"
        editor.file_handler.current_file_path = test_file
        editor.editor.setPlainText("= Test")

        with patch("asciidoc_artisan.core.async_file_handler.AsyncFileHandler.save_async") as mock_save:
            mock_save.return_value = True
            result = await editor.file_handler.save_file_async()
            assert result is True
            mock_save.assert_called_once()
```

---

### 2. test_file_handler_no_handle_leak
**File:** `tests/integration/test_memory_leaks.py:84`
**Current Status:** `@pytest.mark.skip`
**Reason:** FileHandler now uses async I/O
**Complexity:** Medium (1-2 hours)

**Current Implementation:**
```python
@pytest.mark.memory
@pytest.mark.skip(reason="FileHandler now uses async I/O - requires AsyncFileManager mock")
def test_file_handler_no_handle_leak(qtbot):
    """Test file handler doesn't leak file handles.

    SKIPPED: FileHandler migrated to async I/O in v1.7.0.
    Method _load_file_content() renamed to _load_file_async().
    Needs async test pattern with proper file handle mocking.
    """
    # ... test code ...
```

**Required Changes:**
- Convert to async test
- Mock `AsyncFileHandler._load_file_async()`
- Use async context managers for file operations
- Add file handle tracking with `psutil`

**Target Implementation:**
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
        # Load file multiple times
        for _ in range(100):
            async with AsyncFileHandler() as handler:
                content = await handler.read_async(test_file)
                assert content is not None

        # Check no file handles leaked
        final_handles = len(process.open_files())
        assert final_handles <= initial_handles + 2  # Allow some variance
    finally:
        test_file.unlink()
```

---

### 3. test_large_file_open_save
**File:** `tests/integration/test_stress.py:148`
**Current Status:** `@pytest.mark.skip`
**Reason:** FileHandler now uses async I/O
**Complexity:** High (2-3 hours)

**Current Implementation:**
```python
@pytest.mark.skip(reason="Requires async refactoring - FileHandler now uses async I/O (v1.7.0)")
@pytest.mark.stress
@pytest.mark.slow
def test_large_file_open_save(qtbot):
    """Test opening and saving very large files."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    # ... test code ...
```

**Required Changes:**
- Convert to async test
- Use `aiofiles` for large file operations
- Mock `LargeFileHandler` with streaming support
- Add progress tracking assertions
- Handle memory constraints

**Target Implementation:**
```python
@pytest.mark.asyncio
@pytest.mark.stress
@pytest.mark.slow
async def test_large_file_open_save_async(qtbot):
    """Test async opening and saving of very large files."""
    import aiofiles
    import tempfile

    # Create large test file (10MB)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        test_file = Path(f.name)
        large_content = "= Large Document\n\n" + ("Test line\n" * 100000)
        f.write(large_content)

    try:
        # Test async load
        async with AsyncFileHandler() as handler:
            start_time = time.time()
            content = await handler.read_async(test_file)
            load_time = time.time() - start_time

            assert content == large_content
            assert load_time < 5.0  # Should load in <5 seconds

            # Test async save
            modified_content = content + "\n\nAppended text"
            start_time = time.time()
            await handler.write_async(test_file, modified_content)
            save_time = time.time() - start_time

            assert save_time < 5.0  # Should save in <5 seconds
    finally:
        test_file.unlink()
```

---

### 4. test_file_open_performance
**File:** `tests/integration/test_performance_regression.py:66`
**Current Status:** `@pytest.mark.skip`
**Reason:** FileHandler now uses async I/O
**Complexity:** Low-Medium (1 hour)

**Current Implementation:**
```python
@pytest.mark.skip(reason="Requires async refactoring - FileHandler now uses async I/O (v1.7.0)")
@pytest.mark.performance
def test_file_open_performance(qtbot):
    """Test file opening performance."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    # ... test code ...
```

**Required Changes:**
- Convert to async test
- Use async benchmarking
- Mock async file operations
- Add performance thresholds

**Target Implementation:**
```python
@pytest.mark.asyncio
@pytest.mark.performance
async def test_file_open_performance_async(qtbot, benchmark):
    """Test async file opening performance."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        test_file = Path(f.name)
        f.write("= Test Document\n\n" + ("Line\n" * 1000))

    try:
        async def load_file():
            async with AsyncFileHandler() as handler:
                return await handler.read_async(test_file)

        # Benchmark async operation
        import asyncio
        loop = asyncio.get_event_loop()
        result = benchmark(lambda: loop.run_until_complete(load_file()))

        assert result is not None
        # Performance threshold: <100ms for 1000-line file
        assert benchmark.stats['mean'] < 0.1
    finally:
        test_file.unlink()
```

---

## Common Requirements for All Tests

### 1. pytest-asyncio Configuration

**File:** `pytest.ini`

Already configured:
```ini
# Asyncio configuration (pytest-asyncio >= 0.23.0)
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

### 2. Async Fixtures

Need to create async-compatible fixtures:

```python
# conftest.py or test file

@pytest.fixture
async def async_file_handler():
    """Provide AsyncFileHandler for tests."""
    handler = AsyncFileHandler()
    yield handler
    await handler.close()  # Cleanup

@pytest.fixture
async def temp_async_file():
    """Create temporary file for async tests."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        test_file = Path(f.name)
        f.write("= Test Document\n\nTest content")

    yield test_file

    # Cleanup
    if test_file.exists():
        test_file.unlink()
```

### 3. Qt + Async Integration

**Challenge:** Qt's event loop conflicts with asyncio event loop

**Solution:** Use `qasync` or `pytest-qt` with async support:

```python
from qasync import QEventLoop
import asyncio

@pytest.fixture
def event_loop(qapp):
    """Create Qt-compatible async event loop."""
    loop = QEventLoop(qapp)
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
```

### 4. Async Mocking

Use `unittest.mock.AsyncMock` for async methods:

```python
from unittest.mock import AsyncMock, patch

@patch("asciidoc_artisan.core.async_file_handler.AsyncFileHandler.read_async")
async def test_with_async_mock(mock_read):
    mock_read.return_value = "Mock content"
    # Or use AsyncMock
    mock_read = AsyncMock(return_value="Mock content")
```

---

## Implementation Plan

### Phase 1: Setup (30 minutes)
1. Create async fixtures in `conftest.py`
2. Add `qasync` dependency if needed
3. Create base async test class

### Phase 2: Convert Tests (4-6 hours)
1. **test_file_open_performance** (easiest, 1 hour)
2. **test_save_file_creates_file** (medium, 1-2 hours)
3. **test_file_handler_no_handle_leak** (medium, 1-2 hours)
4. **test_large_file_open_save** (hardest, 2-3 hours)

### Phase 3: Verification (1 hour)
1. Run all converted tests individually
2. Run all 4 tests together (check for conflicts)
3. Run with full test suite
4. Update documentation

---

## Dependencies

**Required:**
- pytest-asyncio (already installed)
- aiofiles (may need to add)

**Optional:**
- qasync (for Qt + async integration)
- pytest-benchmark (for performance tests)

**Check installation:**
```bash
pip list | grep -E "pytest-asyncio|aiofiles|qasync"
```

**Install if needed:**
```bash
pip install aiofiles qasync
```

---

## Testing Strategy

### Unit Test Each Conversion
```bash
# Test individually first
pytest tests/integration/test_ui_integration.py::test_save_file_creates_file_async -v
pytest tests/integration/test_memory_leaks.py::test_file_handler_no_handle_leak_async -v
pytest tests/integration/test_stress.py::test_large_file_open_save_async -v
pytest tests/integration/test_performance_regression.py::test_file_open_performance_async -v
```

### Integration Test
```bash
# Test all 4 together
pytest \
  tests/integration/test_ui_integration.py::test_save_file_creates_file_async \
  tests/integration/test_memory_leaks.py::test_file_handler_no_handle_leak_async \
  tests/integration/test_stress.py::test_large_file_open_save_async \
  tests/integration/test_performance_regression.py::test_file_open_performance_async \
  -v
```

### Full Suite Test
```bash
# Verify no regressions
pytest tests/ -v -m "asyncio"
```

---

## Success Criteria

1. **All 4 tests passing** ✅
2. **No `@pytest.mark.skip` decorators** ✅
3. **Tests run in <10 seconds total** (excluding slow stress test)
4. **No event loop conflicts** with Qt
5. **Proper async/await patterns** throughout
6. **Mock all I/O operations** (no real file system hits in unit tests)

---

## Risks & Mitigation

### Risk 1: Qt Event Loop Conflicts
**Mitigation:** Use `qasync` or run async operations in separate thread

### Risk 2: File Handle Leaks in Tests
**Mitigation:** Use `try/finally` blocks, ensure all files closed

### Risk 3: Slow Test Execution
**Mitigation:** Mark slow tests with `@pytest.mark.slow`, use mocks

### Risk 4: Flaky Tests (Timing Issues)
**Mitigation:** Add `@pytest.mark.flaky(reruns=3)`, increase timeouts

---

## Timeline

**Estimated Total Time:** 6-8 hours

- Setup: 30 minutes
- Test #1 (performance): 1 hour
- Test #2 (save file): 1-2 hours
- Test #3 (handle leak): 1-2 hours
- Test #4 (large file): 2-3 hours
- Verification: 1 hour

**Recommended Approach:** Convert one test at a time, verify individually before moving to next.

---

## References

- pytest-asyncio docs: https://pytest-asyncio.readthedocs.io/
- aiofiles docs: https://github.com/Tinche/aiofiles
- qasync docs: https://github.com/CabbageDevelopment/qasync
- AsciiDoc Artisan async file handler: `src/asciidoc_artisan/core/async_file_handler.py`

---

*Document created: November 4, 2025*
*Status: Ready for implementation*
*Priority: Medium (not blocking releases)*
