# Test Refactoring Phase 4: Optimization

**Status:** Ready for execution
**Risk Level:** LOW-MEDIUM - Requires careful analysis before deletion
**Estimated Time:** 4-6 hours
**Expected Impact:** ~10-20 test reduction, improved test quality and speed
**Coverage Impact:** POSITIVE - Remove weak tests, strengthen important tests

---

## Summary

Phase 4 optimizes the test suite by:
1. Identifying and removing truly unused/scaffolded tests
2. Strengthening weak tests with better assertions
3. Optimizing slow-running tests
4. Adding missing edge case tests where gaps exist

**Philosophy:** Quality over quantity. A test suite with 500 strong tests is better than 600 tests where 100 are weak, slow, or scaffolded.

---

## Optimization Categories

### Category 1: Scaffolded Tests (HIGH PRIORITY)
**Definition:** Tests with only `pass` or minimal assertions
**Risk:** ZERO - These provide no value
**Expected:** ~5-10 tests to remove

### Category 2: Weak Tests (MEDIUM PRIORITY)
**Definition:** Tests with only 1-2 trivial assertions (e.g., `assert x is not None`)
**Risk:** LOW - Strengthen rather than remove when possible
**Expected:** ~10-15 tests to strengthen or remove

### Category 3: Slow Tests (LOW PRIORITY)
**Definition:** Tests taking >2 seconds that could be optimized
**Risk:** MEDIUM - Must ensure optimization doesn't reduce coverage
**Expected:** ~3-5 tests to optimize

### Category 4: Redundant Tests (MEDIUM PRIORITY)
**Definition:** Tests that verify the same behavior after Phases 1-3
**Risk:** LOW-MEDIUM - Must verify true redundancy
**Expected:** ~5-10 tests to remove

---

## Detailed Task Breakdown

### Task 4.1: Identify and Remove Scaffolded Tests

**Goal:** Find tests that are placeholders with no real implementation.

#### Step 1: Find scaffolded tests
```bash
# Find tests with only 'pass'
grep -r "def test_" tests/ -A 2 | grep -B 1 "^\s*pass\s*$" | \
  grep "def test_" | wc -l
# Expected: ~26 tests (from earlier grep)

# Find tests with only trivial docstrings + pass
grep -r "def test_" tests/ -A 3 | \
  grep -B 2 "pass.*#.*TODO" | \
  grep "def test_"
```

#### Step 2: Categorize scaffolded tests

**Example findings:**
```python
# File: tests/unit/ui/test_action_manager.py
def test_connects_to_chat_bar(self, chat_manager, mock_chat_bar):
    """Test manager connects to chat bar signals."""
    # Signals should be connected during initialization
    # This is tested implicitly by other tests
    pass  # This is truly unused - DELETE

# File: tests/unit/workers/test_preview_worker.py
def test_worker_initialization(preview_worker):
    """Test worker can be initialized."""
    assert preview_worker is not None  # Weak but valid - STRENGTHEN
```

#### Step 3: Create deletion list

**Files to check (known to have scaffolded tests):**
- `tests/unit/ui/test_action_manager.py` (2-3 scaffolded tests)
- `tests/unit/ui/test_ui_state_manager.py` (1-2 scaffolded tests)
- `tests/unit/ui/test_worker_manager.py` (2-3 scaffolded tests)
- `tests/unit/workers/test_preview_worker.py` (1-2 scaffolded tests)

#### Step 4: Delete scaffolded tests

**Example deletions:**
```python
# BEFORE: tests/unit/ui/test_action_manager.py (line 85-89)
def test_connects_to_chat_bar(self, chat_manager, mock_chat_bar):
    """Test manager connects to chat bar signals."""
    pass

# AFTER: DELETE THIS TEST
# Justification: This behavior is tested implicitly by tests that actually send signals
```

**Validation after each deletion:**
```bash
# Run tests for the modified file
pytest tests/unit/ui/test_action_manager.py -v

# Check coverage hasn't dropped
pytest tests/unit/ui/test_action_manager.py --cov=src/asciidoc_artisan/ui/action_manager.py \
  --cov-report=term-missing
```

**Expected deletions:** 5-10 tests

---

### Task 4.2: Strengthen Weak Tests

**Goal:** Find tests with minimal assertions and either strengthen or remove them.

#### Step 1: Find weak tests
```bash
# Find tests with only "assert x is not None"
grep -r "def test_" tests/ -A 5 | \
  grep -B 5 "assert.*is not None" | \
  grep -A 5 "def test_" | \
  grep -v "assert.*==" | \
  grep "def test_"

# Find tests with only "assert True" or "assert False"
grep -r "assert True\|assert False" tests/ --include="test_*.py"
```

#### Step 2: Analyze and strengthen

**Example weak test:**
```python
# BEFORE: tests/unit/core/test_settings.py
def test_settings_creation(settings):
    """Test settings can be created."""
    assert settings is not None  # Weak!

# AFTER: Strengthen with meaningful assertions
def test_settings_creation():
    """Test settings initialized with correct defaults."""
    settings = Settings()
    # Verify critical defaults
    assert settings.theme == "dark"
    assert settings.font_size == 12
    assert settings.auto_save_interval == 60
    assert settings.ollama_enabled is False
    assert isinstance(settings.recent_files, list)
```

**Example weak test to remove:**
```python
# BEFORE: tests/unit/ui/test_menu_manager.py
def test_menu_exists(menu_manager):
    """Test menu manager has menus."""
    assert menu_manager._file_menu is not None  # Too weak to be useful

# AFTER: DELETE
# Justification: Other tests verify menu functionality comprehensively
```

#### Step 3: Create strengthening list

**Files with weak tests:**
- `tests/unit/core/test_settings.py` (3-5 weak initialization tests)
- `tests/unit/ui/test_*_manager.py` (10-15 weak "object exists" tests)
- `tests/unit/workers/test_*_worker.py` (2-3 weak initialization tests)

**Decision criteria:**
- **Strengthen** if test covers unique initialization logic
- **Remove** if other tests cover the behavior comprehensively
- **Strengthen** if adding assertions is easy (1-2 lines)
- **Remove** if strengthening requires complex setup

**Expected changes:** Strengthen 5-8 tests, remove 5-7 tests

---

### Task 4.3: Optimize Slow Tests

**Goal:** Identify and optimize tests taking >2 seconds.

#### Step 1: Find slow tests
```bash
# Run tests with duration report
pytest tests/ -v --durations=20 > /tmp/slow_tests.txt

# Extract slowest tests (>2 seconds)
grep "test_" /tmp/slow_tests.txt | awk '$1 > 2.0 {print $0}'
```

#### Step 2: Analyze slow tests

**Common causes of slow tests:**
1. **Large file operations**: Reading/writing large files unnecessarily
2. **Sleep statements**: `time.sleep()` calls for timing tests
3. **Subprocess calls**: Calling external commands (git, pandoc)
4. **Qt event loop**: Excessive QTimer delays
5. **Network operations**: HTTP requests (should be mocked)

**Example slow test:**
```python
# BEFORE: tests/integration/test_git_integration.py (5.2s)
def test_git_commit_and_push(temp_repo):
    """Test full git workflow."""
    # Writes 100KB file
    large_file = temp_repo / "large.txt"
    large_file.write_text("x" * 100_000)

    # Waits for git operations (2s each)
    time.sleep(2)  # Artificial delay
    git_worker.commit(...)
    time.sleep(2)
    git_worker.push(...)
    time.sleep(2)

# AFTER: Optimized (0.5s)
def test_git_commit_and_push(temp_repo):
    """Test full git workflow."""
    # Use smaller file (100 bytes is enough)
    small_file = temp_repo / "test.txt"
    small_file.write_text("test content")

    # Mock git operations (instant)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="")
        git_worker.commit(...)
        git_worker.push(...)
    # No delays needed
```

#### Step 3: Optimization strategies

**Strategy 1: Reduce data sizes**
- Use 100-byte files instead of 100KB files
- Use 10-line test data instead of 1000-line data
- Test edge cases with minimal data

**Strategy 2: Mock expensive operations**
- Mock subprocess calls for git/pandoc
- Mock file I/O for large files
- Mock network requests

**Strategy 3: Remove artificial delays**
- Remove `time.sleep()` unless testing timing behavior
- Use `QTimer.singleShot(0, ...)` instead of `QTimer.singleShot(1000, ...)`
- Use pytest-timeout to catch tests that hang

**Strategy 4: Parallelize test execution**
- Ensure tests are independent (no shared state)
- Use pytest-xdist for parallel execution
- Tag slow tests with `@pytest.mark.slow` for selective running

#### Step 4: Apply optimizations

**Expected slowest tests:**
1. `test_large_file_streaming` (async operations)
2. `test_git_commit_and_push` (git subprocess)
3. `test_pandoc_conversion_all_formats` (pandoc subprocess)
4. `test_preview_rendering_complex_doc` (HTML rendering)
5. `test_memory_leak_detection` (runs multiple iterations)

**Optimization targets:** 3-5 tests

---

### Task 4.4: Remove Redundant Tests

**Goal:** Identify tests that duplicate coverage after Phases 1-3 consolidation.

#### Step 1: Find potential redundancy

**Method 1: Check test names**
```bash
# Find tests with similar names in different files
find tests/ -name "test_*.py" -exec basename {} \; | \
  sort | uniq -d
```

**Method 2: Check coverage overlap**
```bash
# Run coverage for specific modules
pytest tests/unit/core/test_gpu_detection.py \
  --cov=src/asciidoc_artisan/core/gpu_detection.py \
  --cov-report=term-missing > /tmp/gpu_cov1.txt

# Check if other files cover same lines
pytest tests/integration/test_hardware_integration.py \
  --cov=src/asciidoc_artisan/core/gpu_detection.py \
  --cov-report=term-missing > /tmp/gpu_cov2.txt

# Compare coverage
diff /tmp/gpu_cov1.txt /tmp/gpu_cov2.txt
```

#### Step 2: Identify true redundancy

**Example redundant tests:**
```python
# File 1: tests/unit/core/test_gpu_detection.py
def test_detect_gpu_no_hardware(mocker):
    """Test GPU detection when no GPU present."""
    mocker.patch("...", return_value=(False, None))
    result = detect_gpu()
    assert result.has_gpu is False

# File 2: tests/integration/test_hardware_integration.py
def test_fallback_to_software_rendering(mocker):
    """Test fallback when no GPU available."""
    mocker.patch("...", return_value=(False, None))
    result = detect_gpu()
    assert result.has_gpu is False
    assert result.can_use_webengine is False

# DECISION: Keep integration test (more comprehensive), remove unit test
```

#### Step 3: Decision criteria

**Keep the test if:**
- ✅ It tests a unique code path
- ✅ It tests a unique input/edge case
- ✅ It's the only test for critical functionality
- ✅ It provides significantly different assertions

**Remove the test if:**
- ❌ Another test covers the exact same code path
- ❌ It's a weak version of a stronger test elsewhere
- ❌ It was kept during Phases 1-3 but is now redundant
- ❌ Removing it doesn't reduce coverage

**Expected removals:** 5-10 tests

---

### Task 4.5: Add Missing Edge Case Tests (Optional)

**Goal:** Identify gaps in coverage and add focused tests.

**Note:** This task is ADDITIVE, so it increases test count. Only do this if coverage gaps are found.

#### Step 1: Identify coverage gaps
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# Open htmlcov/index.html
# Look for modules with <100% coverage

# Find specific uncovered lines
pytest tests/ --cov=src --cov-report=term-missing | grep "TOTAL"
```

#### Step 2: Analyze gaps

**Example gap:**
```python
# src/asciidoc_artisan/core/file_operations.py:145
def atomic_save_text(path: Path, content: str) -> bool:
    try:
        # ... save logic ...
        return True
    except PermissionError:
        logger.error(f"Permission denied: {path}")
        return False
    except OSError as e:  # <-- Line 145: Not covered!
        logger.error(f"OS error: {e}")
        return False
```

#### Step 3: Add focused tests

**Example new test:**
```python
# tests/unit/core/test_file_operations.py
def test_atomic_save_text_os_error(tmp_path, mocker):
    """Test atomic_save_text handles OSError (disk full, etc.)."""
    mock_open = mocker.patch("pathlib.Path.open")
    mock_open.side_effect = OSError("Disk full")

    result = atomic_save_text(tmp_path / "test.txt", "content")

    assert result is False
    # Verify error was logged
    # (requires caplog fixture or mock logger)
```

**Expected additions:** 0-5 tests (only if gaps found)

---

## Validation Steps

### Step 1: Run full test suite BEFORE Phase 4
```bash
source venv/bin/activate
pytest tests/ -v --tb=short --durations=20 > /tmp/phase4_before.txt 2>&1
echo $? > /tmp/phase4_exit_before.txt

# Save coverage baseline
pytest tests/ --cov=src --cov-report=term > /tmp/phase4_coverage_before.txt
```

### Step 2: Execute tasks one at a time

**Task 4.1: Remove scaffolded tests**
```bash
# Find and review scaffolded tests
grep -r "pass\s*$" tests/ -B 2 | grep "def test_"

# Remove identified tests (edit files)
# ... make changes ...

# Test affected files
pytest tests/unit/ui/test_action_manager.py -v

# Commit
git add tests/
git commit -m "Remove scaffolded tests (Task 4.1)"
```

**Task 4.2: Strengthen weak tests**
```bash
# Find weak tests
grep -r "assert.*is not None" tests/ -B 5 | grep "def test_"

# Strengthen or remove (edit files)
# ... make changes ...

# Test affected files
pytest tests/unit/core/test_settings.py -v

# Commit
git add tests/
git commit -m "Strengthen weak tests (Task 4.2)"
```

**Task 4.3: Optimize slow tests**
```bash
# Identify slow tests
pytest tests/ --durations=10

# Optimize identified tests (edit files)
# ... make changes ...

# Verify optimization (should be faster)
pytest tests/integration/test_git_integration.py -v --durations=10

# Commit
git add tests/
git commit -m "Optimize slow-running tests (Task 4.3)"
```

**Task 4.4: Remove redundant tests**
```bash
# Analyze coverage overlap
pytest tests/unit/core/test_gpu_detection.py --cov=src/asciidoc_artisan/core/gpu_detection.py

# Remove redundant tests (edit files)
# ... make changes ...

# Verify coverage maintained
pytest tests/ --cov=src --cov-report=term-missing

# Commit
git add tests/
git commit -m "Remove redundant tests (Task 4.4)"
```

**Task 4.5: Add edge case tests (if needed)**
```bash
# Check coverage gaps
pytest tests/ --cov=src --cov-report=html
firefox htmlcov/index.html  # Review gaps

# Add focused tests (edit files)
# ... make changes ...

# Verify coverage improved
pytest tests/ --cov=src --cov-report=term

# Commit
git add tests/
git commit -m "Add edge case tests for coverage gaps (Task 4.5)"
```

### Step 3: Run full test suite AFTER Phase 4
```bash
pytest tests/ -v --tb=short --durations=20 > /tmp/phase4_after.txt 2>&1
echo $? > /tmp/phase4_exit_after.txt

# Save coverage after
pytest tests/ --cov=src --cov-report=term > /tmp/phase4_coverage_after.txt
```

### Step 4: Compare results
```bash
# Test count comparison
echo "Tests BEFORE:"
grep "passed" /tmp/phase4_before.txt
echo "Tests AFTER:"
grep "passed" /tmp/phase4_after.txt

# Coverage comparison
echo "Coverage BEFORE:"
grep "TOTAL" /tmp/phase4_coverage_before.txt
echo "Coverage AFTER:"
grep "TOTAL" /tmp/phase4_coverage_after.txt

# Execution time comparison
echo "Slowest tests BEFORE:"
grep "slowest durations" /tmp/phase4_before.txt -A 10
echo "Slowest tests AFTER:"
grep "slowest durations" /tmp/phase4_after.txt -A 10
```

### Step 5: Quality metrics
```bash
# Check for remaining weak tests
grep -r "assert.*is not None" tests/ | wc -l  # Should be minimal

# Check for remaining scaffolded tests
grep -r "^\s*pass\s*$" tests/ | wc -l  # Should be 0

# Check test execution speed
pytest tests/ --durations=5  # All tests should be <2s ideally
```

---

## Rollback Plan

### Per-Task Rollback
```bash
# Rollback specific task
git log --oneline | head -5
git revert <commit-hash>

# Or restore specific file
git checkout HEAD~1 tests/unit/core/test_settings.py
pytest tests/unit/core/test_settings.py -v
```

### Full Rollback
```bash
# Rollback all Phase 4 changes
git reset --hard <commit-before-phase4>
```

---

## Success Criteria

✅ All tests pass (exit code 0)
✅ Test count reduced by 10-20 tests (scaffolded + weak + redundant)
✅ Coverage maintained at 100% (or increased if gaps filled)
✅ No scaffolded tests remain (grep finds 0)
✅ Weak tests either strengthened or removed
✅ Slowest test <2 seconds (or documented why it's slow)
✅ Test execution time reduced by 5-10%
✅ No false positives (tests that always pass)

---

## Implementation Checklist

### Pre-Phase Checks
- [ ] Phases 1, 2, 3 complete and committed
- [ ] Run full test suite (baseline)
- [ ] Generate coverage report (baseline)
- [ ] Identify slow tests (baseline)
- [ ] Create backups if needed

### Task 4.1: Remove Scaffolded Tests
- [ ] Find all tests with only `pass`
- [ ] Review each scaffolded test
- [ ] Confirm test is truly unused
- [ ] Delete scaffolded tests (5-10 tests)
- [ ] Run affected test files
- [ ] Commit changes

### Task 4.2: Strengthen Weak Tests
- [ ] Find tests with minimal assertions
- [ ] Review each weak test
- [ ] Decide: strengthen or remove
- [ ] Strengthen 5-8 tests
- [ ] Remove 5-7 weak tests
- [ ] Run affected test files
- [ ] Commit changes

### Task 4.3: Optimize Slow Tests
- [ ] Run pytest --durations=20
- [ ] Identify tests >2 seconds
- [ ] Analyze why tests are slow
- [ ] Apply optimization strategies
- [ ] Verify tests still pass
- [ ] Measure speedup
- [ ] Commit changes

### Task 4.4: Remove Redundant Tests
- [ ] Analyze coverage overlap
- [ ] Identify redundant tests
- [ ] Verify redundancy with coverage reports
- [ ] Remove redundant tests (5-10 tests)
- [ ] Verify coverage maintained
- [ ] Commit changes

### Task 4.5: Add Edge Case Tests (Optional)
- [ ] Generate coverage report
- [ ] Identify any gaps
- [ ] Add focused tests for gaps (0-5 tests)
- [ ] Verify coverage improved
- [ ] Commit changes

### Post-Phase Validation
- [ ] Run full test suite
- [ ] Compare test counts (before vs after)
- [ ] Check coverage report (should be ≥100%)
- [ ] Verify no scaffolded tests remain
- [ ] Check test execution time (should be faster)
- [ ] Update TEST_COVERAGE_SUMMARY.md
- [ ] Create summary commit message
- [ ] Push to origin/main

---

## Expected Commit Messages

### Task 4.1 Commit
```
Remove scaffolded tests (Phase 4.1)

Delete tests with no real implementation:
- test_action_manager.py: 2 tests removed
- test_ui_state_manager.py: 1 test removed
- test_worker_manager.py: 2 tests removed
- test_preview_worker.py: 1 test removed

Impact:
- Tests removed: 6
- Coverage: 100% maintained (tests provided no coverage)
- Test quality: Improved (no false positives)

Justification: These tests only had 'pass' statements and tested
behavior already covered by other tests.

All tests passing: ✅
Coverage maintained: ✅
```

### Task 4.2 Commit
```
Strengthen weak tests (Phase 4.2)

Improve or remove tests with minimal assertions:
- Strengthened 7 tests with meaningful assertions
- Removed 5 weak tests (duplicated by stronger tests)

Impact:
- Tests modified: 7 (strengthened)
- Tests removed: 5 (redundant)
- Coverage: 100% maintained
- Test quality: Significantly improved

Example improvements:
- test_settings_creation: Added 5 default value assertions
- test_worker_initialization: Added state verification assertions
- test_menu_exists: Removed (covered by functional tests)

All tests passing: ✅
Coverage maintained: ✅
```

### Task 4.3 Commit
```
Optimize slow-running tests (Phase 4.3)

Reduce execution time of slowest tests:
- test_large_file_streaming: 4.2s → 0.8s (used 100-byte file)
- test_git_commit_and_push: 6.1s → 0.3s (mocked subprocess)
- test_pandoc_conversion: 3.8s → 0.5s (mocked pandoc)

Impact:
- Tests optimized: 4
- Total speedup: 12.8s → 2.1s (84% faster)
- Coverage: 100% maintained
- Test suite execution: 5-10% faster overall

Optimization techniques:
- Reduced test data sizes
- Mocked expensive subprocess calls
- Removed artificial time.sleep() delays

All tests passing: ✅
Coverage maintained: ✅
Execution time: Significantly improved ✅
```

### Task 4.4 Commit
```
Remove redundant tests (Phase 4.4)

Delete tests that duplicate coverage after consolidation:
- test_gpu_detection: 2 tests removed (covered by integration tests)
- test_async_operations: 3 tests removed (covered by handler tests)
- test_preview_rendering: 2 tests removed (covered by base tests)

Impact:
- Tests removed: 7
- Coverage: 100% maintained
- Test clarity: Improved (less duplication)

Verification:
- Compared coverage reports before/after
- Confirmed all removed tests had full coverage elsewhere
- No drop in line or branch coverage

All tests passing: ✅
Coverage maintained: ✅
```

### Task 4.5 Commit (if applicable)
```
Add edge case tests for coverage gaps (Phase 4.5)

Fill identified coverage gaps with focused tests:
- file_operations.py: Added OSError handling test
- gpu_detection.py: Added invalid cache format test
- settings.py: Added malformed JSON handling test

Impact:
- Tests added: 3
- Coverage: 99.2% → 100%
- Lines covered: +12 lines
- Edge cases: Better protected

All tests passing: ✅
Coverage improved: ✅
```

### Final Summary Commit
```
Complete Phase 4: Test optimization (5 tasks)

Optimization Summary:
- Scaffolded tests: -6 tests
- Weak tests: +7 strengthened, -5 removed
- Slow tests: 4 optimized (84% faster)
- Redundant tests: -7 tests
- Edge case tests: +3 tests (optional)

Total Impact:
- Tests: -15 net (removed 18, added 3)
- Coverage: 99.2% → 100% (+0.8%)
- Execution time: -5-10% faster
- Test quality: Significantly improved

Quality improvements:
- No scaffolded tests remain
- All tests have meaningful assertions
- Slowest test now <2 seconds
- No redundant coverage
- All edge cases covered

All tests passing: ✅
Coverage: 100% ✅
Test speed: Improved ✅
Test quality: Excellent ✅
```

---

## Notes for Implementer

**Critical Principles:**
1. **Quality over quantity**: Better to have 500 strong tests than 600 weak tests
2. **Coverage is king**: Never sacrifice coverage for test count reduction
3. **Speed matters**: Fast tests encourage frequent testing
4. **Clarity is essential**: Every test should have a clear purpose

**Decision Framework:**

**When to REMOVE a test:**
- ✅ Test has only `pass` (scaffolded)
- ✅ Test has only `assert x is not None` and nothing else
- ✅ Test duplicates coverage of another, stronger test
- ✅ Test always passes (false positive)
- ❌ Test provides unique coverage
- ❌ Test is the only test for critical functionality

**When to STRENGTHEN a test:**
- ✅ Test covers unique behavior but has weak assertions
- ✅ Adding assertions is straightforward (1-2 lines)
- ✅ Test is for critical functionality
- ❌ Strengthening requires complex setup
- ❌ Another test already covers the behavior comprehensively

**When to OPTIMIZE a test:**
- ✅ Test takes >2 seconds
- ✅ Optimization doesn't reduce coverage
- ✅ Optimization doesn't make test harder to understand
- ❌ Test speed is inherent to what's being tested
- ❌ Optimization requires mocking critical behavior

**Red Flags (DO NOT REMOVE):**
- ⚠️ Test is the only one for a feature
- ⚠️ Test covers security-critical code (file operations, sanitization)
- ⚠️ Test verifies fix for a known bug
- ⚠️ Test covers edge case that's easy to break
- ⚠️ Test is referenced in documentation or bug reports

**Best Practices:**
1. **Validate incrementally**: Test after every few changes
2. **Use coverage reports**: Don't guess, measure
3. **Document decisions**: Comment why you removed a test
4. **Keep commits small**: One task per commit for easy rollback
5. **Ask for review**: If unsure whether to remove a test, keep it

---

**Last Updated:** November 2, 2025
**Status:** READY FOR EXECUTION
**Prerequisites:** Phases 1, 2, and 3 must be complete
**Estimated Total Time:** 4-6 hours (1 hour per task)
