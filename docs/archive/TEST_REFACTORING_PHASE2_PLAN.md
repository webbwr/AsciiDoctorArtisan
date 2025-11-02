# Test Refactoring Phase 2: Parametrization

**Status:** Ready for execution
**Risk Level:** LOW - Mechanical refactoring with improved test coverage
**Estimated Time:** 4-6 hours
**Expected Impact:** ~20-30 test reduction, significantly improved maintainability
**Coverage Impact:** POSITIVE - Better test case documentation and edge case coverage

---

## Summary

Phase 2 converts repeated test patterns into parametrized tests using `@pytest.mark.parametrize`. This approach:
- Reduces code duplication
- Makes test variations explicit and easy to understand
- Simplifies adding new test cases
- Improves test documentation through parameter names

**Key Principle:** Only parametrize tests that follow the same logical pattern with different inputs. Do NOT force-fit unrelated tests into parametrization.

---

## Parametrization Opportunities

### Group 1: Cache Entry Validation Tests (test_gpu_cache.py)
**Current:** 3 separate tests
**Target:** 1 parametrized test
**Reduction:** 2 tests

### Group 2: GPU Detection by Type (test_gpu_detection.py)
**Current:** 3 separate tests (nvidia, amd, intel)
**Target:** 1 parametrized test
**Reduction:** 2 tests

### Group 3: File Operation Error Cases (test_file_handler.py)
**Current:** 5 separate error handling tests
**Target:** 1-2 parametrized tests
**Reduction:** 3-4 tests

### Group 4: Settings Validation (test_settings.py)
**Current:** Multiple getter/setter tests
**Target:** 1-2 parametrized tests
**Reduction:** 3-5 tests

### Group 5: Async Operation Patterns (test_async_file_handler.py)
**Current:** Repeated read/write/error patterns
**Target:** 2 parametrized tests
**Reduction:** 3-5 tests

### Group 6: Preview Handler Tests (test_preview_handler_base.py)
**Current:** Multiple rendering tests with similar patterns
**Target:** 1-2 parametrized tests
**Reduction:** 3-5 tests

### Group 7: Dialog Validation Tests (test_github_dialogs.py)
**Current:** Repeated validation tests
**Target:** 1 parametrized test
**Reduction:** 2-3 tests

### Group 8: Worker Thread Lifecycle (test_*_worker.py)
**Current:** Similar start/stop/cleanup patterns
**Target:** 1-2 parametrized tests
**Reduction:** 2-3 tests

---

## Detailed Task Breakdown

### Task 2.1: Parametrize Cache Entry Validation Tests

**File:** `tests/unit/core/test_gpu_cache.py`

**Before (lines 68-96, 3 tests):**
```python
def test_cache_entry_validation_fresh():
    """Test cache entry is valid when fresh."""
    entry = GPUCacheEntry(
        timestamp=datetime.now().isoformat(),
        gpu_info={},
        version="1.4.1"
    )
    assert entry.is_valid(ttl_days=7)


def test_cache_entry_validation_expired():
    """Test cache entry is invalid when expired."""
    old_entry = GPUCacheEntry(
        timestamp=(datetime.now() - timedelta(days=10)).isoformat(),
        gpu_info={},
        version="1.4.1"
    )
    assert not old_entry.is_valid(ttl_days=7)


def test_cache_entry_validation_invalid_timestamp():
    """Test cache entry handles invalid timestamp."""
    bad_entry = GPUCacheEntry(
        timestamp="invalid-timestamp",
        gpu_info={},
        version="1.4.1"
    )
    assert not bad_entry.is_valid(ttl_days=7)
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "timestamp_delta_days,expected_valid,test_id",
    [
        (0, True, "fresh"),  # Fresh entry
        (-10, False, "expired"),  # Expired entry (10 days old)
        ("invalid", False, "invalid_timestamp"),  # Invalid timestamp format
    ],
    ids=lambda x: x[2] if isinstance(x, tuple) else str(x)
)
def test_cache_entry_validation(timestamp_delta_days, expected_valid, test_id):
    """Test cache entry validation with different timestamps."""
    if timestamp_delta_days == "invalid":
        timestamp = "invalid-timestamp"
    else:
        timestamp = (datetime.now() - timedelta(days=timestamp_delta_days)).isoformat()

    entry = GPUCacheEntry(
        timestamp=timestamp,
        gpu_info={},
        version="1.4.1"
    )

    assert entry.is_valid(ttl_days=7) == expected_valid
```

**Test IDs Generated:**
- `test_cache_entry_validation[fresh]`
- `test_cache_entry_validation[expired]`
- `test_cache_entry_validation[invalid_timestamp]`

**Lines Saved:** ~20 lines

---

### Task 2.2: Parametrize GPU Detection by Type

**File:** `tests/unit/core/test_gpu_detection.py`

**Before (lines 744-794, 3 tests):**
```python
def test_detect_gpu_nvidia(self, mocker):
    """Test GPU detection with NVIDIA GPU."""
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_dri_devices", return_value=(True, "/dev/dri/renderD128"))
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_opengl_renderer", return_value=(True, "NVIDIA RTX 4060"))
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_nvidia_gpu", return_value=(True, "NVIDIA RTX 4060", "535.104"))
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_amd_gpu", return_value=(False, None))
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_intel_gpu", return_value=(False, None))
    # ... more setup ...

    gpu_info = detect_gpu()
    assert gpu_info.has_gpu is True
    assert gpu_info.gpu_type == "nvidia"
    assert "RTX 4060" in gpu_info.gpu_name

def test_detect_gpu_amd(self, mocker):
    # Similar pattern for AMD

def test_detect_gpu_intel(self, mocker):
    # Similar pattern for Intel
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "gpu_type,gpu_name,driver_version,capabilities",
    [
        ("nvidia", "NVIDIA RTX 4060", "535.104", ["cuda", "vulkan"]),
        ("amd", "AMD Radeon RX 6800", None, ["rocm"]),
        ("intel", "Intel UHD 620", None, ["opencl", "openvino"]),
    ],
    ids=["nvidia", "amd", "intel"]
)
def test_detect_gpu_by_type(self, mocker, gpu_type, gpu_name, driver_version, capabilities):
    """Test GPU detection for different GPU types."""
    # Common setup
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_dri_devices",
                 return_value=(True, "/dev/dri/renderD128"))
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_opengl_renderer",
                 return_value=(True, gpu_name))

    # Type-specific mocks
    nvidia_result = (True, gpu_name, driver_version) if gpu_type == "nvidia" else (False, None, None)
    amd_result = (True, gpu_name) if gpu_type == "amd" else (False, None)
    intel_result = (True, gpu_name) if gpu_type == "intel" else (False, None)

    mocker.patch("asciidoc_artisan.core.gpu_detection.check_nvidia_gpu", return_value=nvidia_result)
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_amd_gpu", return_value=amd_result)
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_intel_gpu", return_value=intel_result)
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_wslg_environment", return_value=False)
    mocker.patch("asciidoc_artisan.core.gpu_detection.check_intel_npu",
                 return_value=(True, "Intel NPU") if gpu_type == "intel" else (False, None))
    mocker.patch("asciidoc_artisan.core.gpu_detection.detect_compute_capabilities",
                 return_value=capabilities)

    # Execute
    gpu_info = detect_gpu()

    # Verify
    assert gpu_info.has_gpu is True
    assert gpu_info.gpu_type == gpu_type
    assert gpu_name.split()[-1] in gpu_info.gpu_name  # Check model number
```

**Lines Saved:** ~35 lines

---

### Task 2.3: Parametrize File Operation Error Cases

**File:** `tests/unit/ui/test_file_handler.py`

**Before (5 separate error tests):**
```python
def test_load_file_not_found(handler, mock_status_manager):
    """Test loading non-existent file."""
    # test code

def test_load_file_permission_denied(handler, mock_status_manager):
    """Test loading file with no read permission."""
    # test code

def test_save_file_permission_denied(handler, tmp_path, mock_editor):
    """Test saving file with no write permission."""
    # test code

def test_save_file_disk_full(handler, tmp_path, mock_editor):
    """Test saving file when disk is full."""
    # test code

def test_save_file_invalid_path(handler, mock_editor):
    """Test saving file with invalid path."""
    # test code
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "operation,error_type,error_msg_contains",
    [
        ("load", FileNotFoundError, "not found"),
        ("load", PermissionError, "permission"),
        ("save", PermissionError, "permission"),
        ("save", OSError, "disk"),
        ("save", ValueError, "invalid path"),
    ],
    ids=["load-not-found", "load-permission", "save-permission", "save-disk-full", "save-invalid-path"]
)
def test_file_operation_errors(handler, tmp_path, mock_editor, mock_status_manager,
                               operation, error_type, error_msg_contains):
    """Test file operation error handling."""
    if operation == "load":
        # Setup mock to raise error
        with patch("pathlib.Path.read_text", side_effect=error_type(error_msg_contains)):
            handler.load_file(str(tmp_path / "test.txt"))
            # Verify error was handled
            assert mock_status_manager.show_error.called
    else:  # save
        with patch("pathlib.Path.write_text", side_effect=error_type(error_msg_contains)):
            handler.save_file(str(tmp_path / "test.txt"))
            assert mock_status_manager.show_error.called
```

**Lines Saved:** ~25 lines

---

### Task 2.4: Parametrize Settings Getter/Setter Tests

**File:** `tests/unit/core/test_settings.py`

**Before (multiple getter/setter tests):**
```python
def test_get_theme(settings):
    assert settings.theme == "dark"

def test_set_theme(settings):
    settings.theme = "light"
    assert settings.theme == "light"

def test_get_font_size(settings):
    assert settings.font_size == 12

def test_set_font_size(settings):
    settings.font_size = 14
    assert settings.font_size == 14
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "property_name,default_value,new_value",
    [
        ("theme", "dark", "light"),
        ("font_size", 12, 14),
        ("font_family", "Monospace", "Arial"),
        ("auto_save_interval", 60, 120),
        ("show_line_numbers", True, False),
    ],
    ids=["theme", "font_size", "font_family", "auto_save", "line_numbers"]
)
def test_settings_property(settings, property_name, default_value, new_value):
    """Test getting and setting properties."""
    # Test getter (default value)
    assert getattr(settings, property_name) == default_value

    # Test setter
    setattr(settings, property_name, new_value)
    assert getattr(settings, property_name) == new_value
```

**Lines Saved:** ~20 lines

---

### Task 2.5: Parametrize Async Operation Patterns

**File:** `tests/unit/core/test_async_file_handler.py`

**Before (3 tests with similar patterns):**
```python
def test_read_file_async(self, app, temp_file):
    """Test async file read."""
    # setup, execute, verify

def test_write_file_async(self, app, temp_dir):
    """Test async file write."""
    # setup, execute, verify

def test_read_error(self, app):
    """Test read error for non-existent file."""
    # setup, execute, verify
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "operation,should_succeed,file_exists",
    [
        ("read", True, True),
        ("read", False, False),
        ("write", True, True),
        ("write", False, True),  # Write to read-only location
    ],
    ids=["read-success", "read-fail", "write-success", "write-fail"]
)
def test_async_file_operations(app, temp_file, temp_dir, operation, should_succeed, file_exists):
    """Test async file operations with different scenarios."""
    handler = AsyncFileHandler()
    result_holder = []
    error_holder = []

    def on_complete(result):
        result_holder.append(result)
        app.quit()

    def on_error(path, error):
        error_holder.append((path, error))
        app.quit()

    if operation == "read":
        handler.read_complete.connect(on_complete)
        handler.read_error.connect(on_error)
        path = temp_file if file_exists else "/nonexistent/file.txt"
        handler.read_file_async(path)
    else:  # write
        handler.write_complete.connect(on_complete)
        handler.write_error.connect(on_error)
        path = str(Path(temp_dir) / "output.txt") if file_exists else "/root/forbidden.txt"
        handler.write_file_async(path, "test content")

    QTimer.singleShot(2000, app.quit)
    app.exec()

    if should_succeed:
        assert len(result_holder) == 1
        assert result_holder[0].success is True
    else:
        assert len(error_holder) == 1

    handler.cleanup()
```

**Lines Saved:** ~30 lines

---

### Task 2.6: Parametrize Preview Handler Rendering Tests

**File:** `tests/unit/ui/test_preview_handler_base.py`

**Before (multiple similar rendering tests):**
```python
def test_render_heading(preview_handler):
    """Test rendering heading."""
    # test code

def test_render_bold(preview_handler):
    """Test rendering bold text."""
    # test code

def test_render_italic(preview_handler):
    """Test rendering italic text."""
    # test code

def test_render_list(preview_handler):
    """Test rendering list."""
    # test code
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "asciidoc_input,expected_html_contains",
    [
        ("= Heading 1", "<h1>Heading 1</h1>"),
        ("== Heading 2", "<h2>Heading 2</h2>"),
        ("*bold text*", "<strong>bold text</strong>"),
        ("_italic text_", "<em>italic text</em>"),
        ("* list item", "<li>list item</li>"),
        ("`code`", "<code>code</code>"),
    ],
    ids=["h1", "h2", "bold", "italic", "list", "code"]
)
def test_render_asciidoc_elements(preview_handler, asciidoc_input, expected_html_contains):
    """Test rendering various AsciiDoc elements."""
    html = preview_handler.render(asciidoc_input)
    assert expected_html_contains in html
```

**Lines Saved:** ~25 lines

---

### Task 2.7: Parametrize Dialog Validation Tests

**File:** `tests/unit/ui/test_github_dialogs.py`

**Before (multiple validation tests):**
```python
def test_title_validation_empty(dialog):
    """Test title cannot be empty."""
    # test code

def test_title_validation_whitespace(dialog):
    """Test title with only whitespace."""
    # test code

def test_title_validation_valid(dialog):
    """Test valid title."""
    # test code
```

**After (1 parametrized test):**
```python
@pytest.mark.parametrize(
    "title,is_valid",
    [
        ("", False),
        ("   ", False),
        ("Valid Title", True),
        ("Title with spaces", True),
        ("T", True),  # Single character is valid
    ],
    ids=["empty", "whitespace", "normal", "with-spaces", "single-char"]
)
def test_title_validation(dialog, title, is_valid):
    """Test title validation with various inputs."""
    dialog.title_input.setText(title)
    assert dialog.validate() == is_valid
```

**Lines Saved:** ~15 lines

---

### Task 2.8: Parametrize Worker Thread Lifecycle Tests

**File:** `tests/unit/workers/test_git_worker.py`, `test_pandoc_worker.py`, `test_preview_worker.py`

**Note:** This is more complex and may not save as many lines, but improves consistency.

**Before (in each worker file):**
```python
def test_worker_start(worker):
    """Test worker can start."""
    # test code

def test_worker_cleanup(worker):
    """Test worker cleanup."""
    # test code
```

**After (add to conftest.py):**
```python
@pytest.fixture(params=[
    ("git", GitWorker),
    ("pandoc", PandocWorker),
    ("preview", PreviewWorker),
], ids=["git", "pandoc", "preview"])
def worker_class(request):
    """Parametrized worker classes for lifecycle tests."""
    return request.param

def test_worker_lifecycle(worker_class):
    """Test worker lifecycle (start, run, cleanup)."""
    name, cls = worker_class
    worker = cls()

    # Test start
    worker.start()
    assert worker.isRunning()

    # Test cleanup
    worker.cleanup()
    worker.wait(1000)
    assert not worker.isRunning()
```

**Lines Saved:** ~10 lines per worker file (30 total)

---

## Validation Steps

### Step 1: Run tests BEFORE changes
```bash
source venv/bin/activate
pytest tests/ -v --tb=short > /tmp/phase2_before.txt 2>&1
echo $? > /tmp/phase2_exit_before.txt

# Count test totals
grep -E "passed|failed" /tmp/phase2_before.txt | tail -1
```

### Step 2: Make changes (Tasks 2.1-2.8)
- Work on one task at a time
- Run tests after each task to ensure no breakage
- Commit after each successful task

### Step 3: Run tests AFTER changes
```bash
pytest tests/ -v --tb=short > /tmp/phase2_after.txt 2>&1
echo $? > /tmp/phase2_exit_after.txt

# Count test totals
grep -E "passed|failed" /tmp/phase2_after.txt | tail -1
```

### Step 4: Compare results
```bash
# Should see 20-30 fewer tests but all passing
diff -u <(grep "PASSED" /tmp/phase2_before.txt | wc -l) \
        <(grep "PASSED" /tmp/phase2_after.txt | wc -l)

# Both should exit with 0
cat /tmp/phase2_exit_before.txt /tmp/phase2_exit_after.txt
```

### Step 5: Check coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
# Open htmlcov/index.html to verify coverage maintained
```

### Step 6: Verify parametrized test IDs
```bash
# Should see readable test IDs like:
# test_cache_entry_validation[fresh]
# test_cache_entry_validation[expired]
pytest tests/ --collect-only | grep "\[.*\]"
```

---

## Rollback Plan

### Per-Task Rollback
If a specific task causes issues:
```bash
# Rollback specific file
git checkout tests/unit/core/test_gpu_cache.py
pytest tests/unit/core/test_gpu_cache.py -v
```

### Full Rollback
If multiple issues arise:
```bash
# Rollback all test changes
git checkout tests/

# Or rollback to last commit
git reset --hard HEAD~1
```

---

## Success Criteria

✅ All tests pass (exit code 0)
✅ Test count reduced by 20-30 tests
✅ Coverage remains at or near 100%
✅ No new warnings or errors
✅ Parametrized tests have clear, readable IDs
✅ Test execution time similar or faster
✅ Each parametrized test still tests one logical concept

---

## Implementation Checklist

- [ ] Run tests BEFORE (baseline)
- [ ] Task 2.1: Parametrize cache entry validation (test_gpu_cache.py)
- [ ] Task 2.2: Parametrize GPU detection by type (test_gpu_detection.py)
- [ ] Task 2.3: Parametrize file operation errors (test_file_handler.py)
- [ ] Task 2.4: Parametrize settings properties (test_settings.py)
- [ ] Task 2.5: Parametrize async operations (test_async_file_handler.py)
- [ ] Task 2.6: Parametrize preview rendering (test_preview_handler_base.py)
- [ ] Task 2.7: Parametrize dialog validation (test_github_dialogs.py)
- [ ] Task 2.8: Parametrize worker lifecycle (conftest.py + worker tests)
- [ ] Run tests AFTER each task
- [ ] Final validation: all tests pass
- [ ] Check coverage report
- [ ] Review parametrized test IDs for readability
- [ ] Commit changes with descriptive message
- [ ] Update TEST_COVERAGE_SUMMARY.md with new test counts

---

## Expected Commit Message

```
Refactor tests: Convert repeated patterns to parametrized tests (Phase 2)

Parametrization - Improved Test Documentation:
- Convert 8 test groups to use @pytest.mark.parametrize
- Cache entry validation: 3 tests → 1 parametrized test
- GPU detection by type: 3 tests → 1 parametrized test
- File operation errors: 5 tests → 1 parametrized test
- Settings properties: 5 tests → 1 parametrized test
- Async operations: 3 tests → 1 parametrized test
- Preview rendering: 6 tests → 1 parametrized test
- Dialog validation: 3 tests → 1 parametrized test
- Worker lifecycle: 6 tests → 2 parametrized tests

Impact:
- Files modified: 9
- Test count: -25 tests (better organized)
- Lines saved: ~180 lines of duplicate code
- Coverage: 100% maintained
- Maintainability: Significantly improved (easier to add test cases)

Benefits:
- Clear test IDs show what each variation tests
- Adding new test cases now requires 1 line instead of 10+
- Test patterns are now self-documenting
- Reduced maintenance burden

All tests passing: ✅
Coverage maintained: ✅
Test IDs readable: ✅
```

---

## Notes for Implementer

**Best Practices:**
1. **Keep test IDs readable**: Use descriptive IDs, not just "test0", "test1"
2. **Don't force-fit**: If tests don't follow the same pattern, don't parametrize
3. **One concept per test**: Each parametrized test should still test ONE logical concept
4. **Document parameters**: Use clear parameter names that explain what's being tested
5. **Test incrementally**: Run tests after each parametrization to catch issues early

**Common Pitfalls:**
- ❌ Parametrizing tests that need different setup/teardown
- ❌ Over-parametrizing to the point where test logic becomes complex
- ❌ Using unclear parameter names like "input1", "input2"
- ❌ Combining unrelated test cases just to reduce count

**When in Doubt:**
- If adding a new test case requires significant `if/else` logic in the test, DON'T parametrize
- If the test IDs would be unclear, DON'T parametrize
- If tests need different fixtures, DON'T parametrize

---

**Last Updated:** November 2, 2025
**Status:** READY FOR EXECUTION
**Prerequisites:** Phase 1 must be complete
