# Test Refactoring Phase 3: Consolidation

**Status:** Ready for execution
**Risk Level:** MEDIUM - Involves moving tests between files
**Estimated Time:** 8-12 hours
**Expected Impact:** ~110-160 test reduction, -11 files, significantly improved organization
**Coverage Impact:** MAINTAINED - 100% coverage preserved through careful migration

---

## Summary

Phase 3 consolidates related test files to improve organization and reduce duplication. This phase requires careful attention to:
- Preserving all test coverage
- Maintaining fixture compatibility
- Ensuring clear test organization
- Avoiding merge conflicts with active development

**Key Strategy:** Merge files that test closely related functionality, remove duplicate tests, and organize by logical grouping rather than arbitrary file splitting.

---

## Consolidation Groups

### Group 1: GPU/Hardware Detection (3 files → 1 file)
**Current:** 132 tests across 3 files
**Target:** 80-90 tests in 1 file
**Reduction:** 40-50 tests, -2 files

### Group 2: Async File Operations (5 files → 2 files)
**Current:** 40 tests across 5 files
**Target:** 30-35 tests in 2 files
**Reduction:** 5-10 tests, -3 files

### Group 3: Preview Handlers (3 files → 2 files)
**Current:** 36 tests across 3 files
**Target:** 28-32 tests in 2 files
**Reduction:** 4-8 tests, -1 file

### Group 4: Chat System (5 files → 4 files)
**Current:** 112 tests across 5 files
**Target:** 90-100 tests in 4 files
**Reduction:** 12-22 tests, -1 file

**TOTAL CONSOLIDATION:**
- Tests: 320 → ~228-257 (reduction of 63-92 tests)
- Files: 16 → 9 (reduction of 7 files)
- Lines: ~5,000 → ~3,500 (estimated 1,500 line reduction)

---

## Detailed Task Breakdown

### Task 3.1: Consolidate GPU/Hardware Detection Tests

**Rationale:** These three files test the same module (`gpu_detection.py`) and have significant overlap.

**Files to consolidate:**
```
tests/unit/core/test_gpu_detection.py      (74 tests) - KEEP as base
tests/unit/core/test_gpu_cache.py          (18 tests) - MERGE INTO base
tests/unit/core/test_hardware_detection.py (40 tests) - MERGE INTO base
```

**Target file:** `tests/unit/core/test_gpu_detection.py`

**Migration Plan:**

#### Step 1: Analyze overlap
```bash
# Find duplicate test names
grep "def test_" tests/unit/core/test_gpu_detection.py > /tmp/gpu_det_tests.txt
grep "def test_" tests/unit/core/test_gpu_cache.py > /tmp/gpu_cache_tests.txt
grep "def test_" tests/unit/core/test_hardware_detection.py > /tmp/hardware_tests.txt

# Check for duplicates
cat /tmp/gpu_det_tests.txt /tmp/gpu_cache_tests.txt /tmp/hardware_tests.txt | \
  sort | uniq -d
```

**Expected duplicates:**
- `test_gpu_info_creation*` variants
- `test_cache_entry*` variants (may differ slightly)
- `test_detect_gpu*` variants

#### Step 2: Create new consolidated structure
```python
# tests/unit/core/test_gpu_detection.py

# SECTION 1: GPUInfo dataclass tests (from test_gpu_detection.py lines 31-91)
class TestGPUInfo:
    """Test GPUInfo dataclass creation and properties."""
    # Keep existing tests

# SECTION 2: Cache entry tests (from test_gpu_cache.py lines 46-96)
class TestGPUCacheEntry:
    """Test GPU cache entry validation and serialization."""
    def test_cache_entry_creation(sample_gpu_info):
        # Migrate from test_gpu_cache.py

    def test_cache_entry_validation(timestamp_delta_days, expected_valid):
        # Migrate from test_gpu_cache.py (use Phase 2 parametrization)

# SECTION 3: Cache management tests (from test_gpu_cache.py lines 98-150)
class TestGPUDetectionCache:
    """Test GPU detection cache save/load/clear operations."""
    # Migrate all cache tests from test_gpu_cache.py

# SECTION 4: Hardware detection tests (from test_gpu_detection.py lines 351-651)
class TestHardwareDetection:
    """Test low-level hardware detection functions."""
    # Keep existing DRI, OpenGL, WSLg tests

# SECTION 5: GPU vendor detection (from test_gpu_detection.py lines 407-535)
class TestGPUVendorDetection:
    """Test vendor-specific GPU detection (NVIDIA, AMD, Intel)."""
    # Keep existing vendor tests

# SECTION 6: Compute capabilities (from test_gpu_detection.py lines 654-720)
class TestComputeCapabilities:
    """Test detection of compute APIs (CUDA, OpenCL, Vulkan, etc.)."""
    # Keep existing tests

# SECTION 7: Integration tests (from test_gpu_detection.py lines 722-809)
class TestGPUDetectionIntegration:
    """Test full GPU detection flow."""
    # Keep existing detect_gpu() tests
    # Add relevant tests from test_hardware_detection.py

# SECTION 8: CLI interface (from test_gpu_detection.py lines 940-1051)
class TestGPUDetectionCLI:
    """Test command-line interface for GPU detection."""
    # Keep existing main() tests
```

#### Step 3: Identify and remove duplicates

**Duplicate patterns to consolidate:**

1. **GPUInfo creation tests** (appears in both files):
   - Keep: test_gpu_detection.py versions (more comprehensive)
   - Remove: test_hardware_detection.py versions

2. **Cache validation tests** (appears in both files):
   - Keep: test_gpu_cache.py versions (more focused)
   - Remove: test_gpu_detection.py duplicates

3. **Detection integration tests** (overlap between files):
   - Merge: Combine test_hardware_detection.py integration tests into TestGPUDetectionIntegration
   - Remove: Duplicate scenarios

#### Step 4: Execute migration
```bash
# Backup files
cp tests/unit/core/test_gpu_detection.py tests/unit/core/test_gpu_detection.py.backup
cp tests/unit/core/test_gpu_cache.py tests/unit/core/test_gpu_cache.py.backup
cp tests/unit/core/test_hardware_detection.py tests/unit/core/test_hardware_detection.py.backup

# Create consolidated file (manually using editor)
# ... edit test_gpu_detection.py ...

# Test the consolidated file
pytest tests/unit/core/test_gpu_detection.py -v

# If all pass, remove old files
git rm tests/unit/core/test_gpu_cache.py
git rm tests/unit/core/test_hardware_detection.py
```

**Expected result:**
- 1 file: `test_gpu_detection.py` with 80-90 tests
- Clear section organization
- All coverage preserved

---

### Task 3.2: Consolidate Async File Operations Tests

**Rationale:** Multiple files test async file operations with significant overlap.

**Files to consolidate:**
```
tests/unit/core/test_async_file_handler.py (29 tests) - KEEP as base
tests/unit/core/test_async_file_ops.py     (9 tests)  - MERGE INTO base
tests/unit/core/test_qt_async_file_manager.py (0 tests) - DELETE (scaffolded)
tests/unit/core/test_async_file_watcher.py (2 tests)  - KEEP separate (different module)
tests/integration/test_async_integration.py (0 tests) - DELETE (scaffolded)
```

**Target structure:**
```
tests/unit/core/test_async_file_handler.py  (35-40 tests)
tests/unit/core/test_async_file_watcher.py  (2 tests, unchanged)
```

**Migration Plan:**

#### Step 1: Analyze test_async_file_ops.py
```bash
# Check what this file tests
grep "class\|def test_" tests/unit/core/test_async_file_ops.py
```

**Expected content:**
- Basic async read/write tests (likely duplicates)
- Error handling tests (may be unique)
- Performance tests (may be unique)

#### Step 2: Merge unique tests into test_async_file_handler.py

```python
# tests/unit/core/test_async_file_handler.py

# EXISTING SECTIONS (keep)
class TestAsyncFileHandler:
    """Test AsyncFileHandler basic operations."""
    # Existing tests (lines 55-143)

class TestFileStreamReader:
    """Test streaming file reader."""
    # Existing tests

class TestFileStreamWriter:
    """Test streaming file writer."""
    # Existing tests

class TestBatchFileOperations:
    """Test batch file operations."""
    # Existing tests

# NEW SECTION (migrate from test_async_file_ops.py)
class TestAsyncFileOperationsEdgeCases:
    """Test edge cases and error scenarios."""
    # Migrate unique tests from test_async_file_ops.py

    def test_concurrent_reads(app, temp_file):
        """Test multiple concurrent read operations."""
        # From test_async_file_ops.py

    def test_large_file_streaming(app, tmp_path):
        """Test streaming very large files."""
        # From test_async_file_ops.py
```

#### Step 3: Delete scaffolded files
```bash
# These files have no actual test implementations
git rm tests/unit/core/test_qt_async_file_manager.py
git rm tests/integration/test_async_integration.py

# Merge and remove
# ... edit test_async_file_handler.py ...
git rm tests/unit/core/test_async_file_ops.py
```

**Expected result:**
- 2 files: `test_async_file_handler.py` (35-40 tests), `test_async_file_watcher.py` (2 tests)
- Removed 3 scaffolded/duplicate files
- All unique tests preserved

---

### Task 3.3: Consolidate Preview Handler Tests

**Rationale:** Three files test preview handlers with significant overlap.

**Files to consolidate:**
```
tests/unit/ui/test_preview_handler_base.py (29 tests) - KEEP as base
tests/unit/ui/test_preview_handler.py      (4 tests)  - MERGE INTO base
tests/unit/ui/test_preview_handler_gpu.py  (3 tests)  - MERGE INTO gpu file
```

**Target structure:**
```
tests/unit/ui/test_preview_handler_base.py (30-35 tests) - Base functionality
tests/unit/ui/test_preview_handler_gpu.py  (6-8 tests)  - GPU-specific tests
```

**Migration Plan:**

#### Step 1: Analyze test_preview_handler.py
```bash
grep "def test_" tests/unit/ui/test_preview_handler.py
```

**Expected tests:**
- Basic rendering tests (likely duplicates with base)
- QTextBrowser-specific tests (unique, should keep)

#### Step 2: Merge into appropriate files

```python
# tests/unit/ui/test_preview_handler_base.py
# This file tests PreviewHandlerBase abstract class

# SECTION 1: Base class tests
class TestPreviewHandlerBase:
    """Test abstract base class functionality."""
    # Existing tests

# SECTION 2: Common rendering tests
class TestPreviewRendering:
    """Test common rendering functionality."""
    # Existing parametrized tests from Phase 2
    # Add any unique rendering tests from test_preview_handler.py

# SECTION 3: QTextBrowser implementation
class TestQTextBrowserPreview:
    """Test QTextBrowser preview implementation (software rendering)."""
    # Migrate unique tests from test_preview_handler.py

# tests/unit/ui/test_preview_handler_gpu.py
# This file tests GPU-accelerated preview (QWebEngineView)

class TestQWebEnginePreview:
    """Test QWebEngineView preview implementation (GPU rendering)."""
    # Keep existing 3 tests
    # Add GPU-specific initialization tests
```

#### Step 3: Execute merge
```bash
# Merge test_preview_handler.py into base file
# ... edit test_preview_handler_base.py ...

# Test
pytest tests/unit/ui/test_preview_handler_base.py -v
pytest tests/unit/ui/test_preview_handler_gpu.py -v

# Remove merged file
git rm tests/unit/ui/test_preview_handler.py
```

**Expected result:**
- 2 files: `test_preview_handler_base.py` (30-35 tests), `test_preview_handler_gpu.py` (6-8 tests)
- Removed 1 redundant file
- Clear separation: base/common vs GPU-specific

---

### Task 3.4: Consolidate Chat System Tests

**Rationale:** Chat tests are spread across multiple files with some duplication.

**Files to consolidate:**
```
tests/test_chat_manager.py                       (24 tests) - KEEP
tests/test_ollama_chat_worker.py                 (19 tests) - KEEP
tests/test_chat_bar_widget.py                    (33 tests) - KEEP
tests/unit/ui/test_chat_history_persistence.py   (18 tests) - MERGE into chat_manager
tests/integration/test_chat_integration.py       (18 tests) - KEEP
```

**Target structure:**
```
tests/test_chat_manager.py                 (40-45 tests) - Manager + history
tests/test_ollama_chat_worker.py          (19 tests, unchanged)
tests/test_chat_bar_widget.py             (33 tests, unchanged)
tests/integration/test_chat_integration.py (18 tests, unchanged)
```

**Migration Plan:**

#### Step 1: Analyze test_chat_history_persistence.py
```bash
grep "class\|def test_" tests/unit/ui/test_chat_history_persistence.py
```

**Expected tests:**
- History save/load tests
- History truncation tests
- History serialization tests

**Observation:** These are tightly coupled with ChatManager's history management, so merging makes sense.

#### Step 2: Merge history tests into ChatManager tests

```python
# tests/test_chat_manager.py

# EXISTING SECTIONS (keep)
class TestChatManagerInitialization:
    """Test manager initialization."""
    # Existing tests

class TestChatManagerVisibility:
    """Test visibility management."""
    # Existing tests

class TestChatManagerMessaging:
    """Test message sending and receiving."""
    # Existing tests

# NEW SECTION (migrate from test_chat_history_persistence.py)
class TestChatHistoryPersistence:
    """Test chat history save/load/management."""

    def test_history_save_to_settings(chat_manager, settings):
        """Test history is saved to settings."""
        # From test_chat_history_persistence.py

    def test_history_load_from_settings(chat_manager, settings):
        """Test history is loaded from settings."""
        # From test_chat_history_persistence.py

    def test_history_truncation(chat_manager, settings):
        """Test history is truncated to max_history limit."""
        # From test_chat_history_persistence.py
```

#### Step 3: Execute merge
```bash
# Merge tests
# ... edit tests/test_chat_manager.py ...

# Test
pytest tests/test_chat_manager.py -v

# Remove merged file
git rm tests/unit/ui/test_chat_history_persistence.py
```

**Expected result:**
- 4 files (down from 5)
- Removed 1 file
- Better organization: history tests now with manager tests

---

## Validation Steps

### Step 1: Run full test suite BEFORE Phase 3
```bash
source venv/bin/activate
pytest tests/ -v --tb=short > /tmp/phase3_before.txt 2>&1
echo $? > /tmp/phase3_exit_before.txt

# Save test counts by file
pytest tests/ --collect-only -q > /tmp/phase3_before_tests.txt
```

### Step 2: Execute tasks one at a time
```bash
# Task 3.1: GPU/Hardware consolidation
# ... make changes ...
pytest tests/unit/core/test_gpu_detection.py -v
git add tests/unit/core/test_gpu_detection.py
git rm tests/unit/core/test_gpu_cache.py tests/unit/core/test_hardware_detection.py
git commit -m "Consolidate GPU/hardware detection tests (Task 3.1)"

# Task 3.2: Async file operations consolidation
# ... make changes ...
pytest tests/unit/core/test_async_file_handler.py -v
git add tests/unit/core/test_async_file_handler.py
git rm tests/unit/core/test_async_file_ops.py \
       tests/unit/core/test_qt_async_file_manager.py \
       tests/integration/test_async_integration.py
git commit -m "Consolidate async file operation tests (Task 3.2)"

# Task 3.3: Preview handler consolidation
# ... make changes ...
pytest tests/unit/ui/test_preview_handler*.py -v
git add tests/unit/ui/test_preview_handler_base.py tests/unit/ui/test_preview_handler_gpu.py
git rm tests/unit/ui/test_preview_handler.py
git commit -m "Consolidate preview handler tests (Task 3.3)"

# Task 3.4: Chat system consolidation
# ... make changes ...
pytest tests/test_chat*.py tests/integration/test_chat_integration.py -v
git add tests/test_chat_manager.py
git rm tests/unit/ui/test_chat_history_persistence.py
git commit -m "Consolidate chat system tests (Task 3.4)"
```

### Step 3: Run full test suite AFTER Phase 3
```bash
pytest tests/ -v --tb=short > /tmp/phase3_after.txt 2>&1
echo $? > /tmp/phase3_exit_after.txt

# Save test counts by file
pytest tests/ --collect-only -q > /tmp/phase3_after_tests.txt
```

### Step 4: Compare results
```bash
# Test count comparison
echo "BEFORE:"
wc -l /tmp/phase3_before_tests.txt
echo "AFTER:"
wc -l /tmp/phase3_after_tests.txt

# File count comparison
echo "Files BEFORE:"
find tests/ -name "test_*.py" | wc -l
echo "Files AFTER:"
find tests/ -name "test_*.py" | wc -l

# Exit codes
echo "Exit code BEFORE: $(cat /tmp/phase3_exit_before.txt)"
echo "Exit code AFTER: $(cat /tmp/phase3_exit_after.txt)"
```

### Step 5: Check coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
# Coverage should remain at or near 100%
```

### Step 6: Manual verification
```bash
# Verify no orphaned fixtures
grep -r "@pytest.fixture" tests/conftest.py tests/unit/core/conftest.py

# Verify no missing imports
pytest tests/ --collect-only -q

# Check for duplicate test names (should be none)
find tests/ -name "test_*.py" -exec grep "def test_" {} \; | \
  cut -d'(' -f1 | sort | uniq -d
```

---

## Rollback Plan

### Per-Task Rollback
If a specific task causes issues:
```bash
# Example: Rollback Task 3.1 (GPU consolidation)
git checkout tests/unit/core/test_gpu_detection.py
git checkout tests/unit/core/test_gpu_cache.py
git checkout tests/unit/core/test_hardware_detection.py
pytest tests/unit/core/test_gpu*.py tests/unit/core/test_hardware*.py -v
```

### Full Rollback
If multiple tasks cause issues:
```bash
# Rollback all Phase 3 changes
git log --oneline | head -5  # Find commit before Phase 3
git reset --hard <commit-hash>

# Or use backups
cp tests/unit/core/test_gpu_detection.py.backup tests/unit/core/test_gpu_detection.py
# ... restore other backups ...
```

---

## Success Criteria

✅ All tests pass (exit code 0)
✅ Test count reduced by 63-92 tests
✅ File count reduced by 7 files
✅ Coverage remains at 100%
✅ No duplicate test names
✅ Clear test file organization
✅ All fixtures properly scoped
✅ No orphaned fixtures or imports
✅ Test execution time similar or faster

---

## Implementation Checklist

### Pre-Phase Checks
- [ ] Phase 1 complete and committed
- [ ] Phase 2 complete and committed
- [ ] Run full test suite (baseline)
- [ ] Create backups of all files to be modified
- [ ] Document current test counts per file

### Task 3.1: GPU/Hardware Consolidation
- [ ] Analyze duplicate tests across 3 files
- [ ] Create new consolidated structure in test_gpu_detection.py
- [ ] Migrate unique tests from test_gpu_cache.py
- [ ] Migrate unique tests from test_hardware_detection.py
- [ ] Remove duplicate tests
- [ ] Test consolidated file
- [ ] Delete old files (git rm)
- [ ] Commit with message

### Task 3.2: Async File Operations Consolidation
- [ ] Analyze test_async_file_ops.py for unique tests
- [ ] Migrate unique tests to test_async_file_handler.py
- [ ] Delete scaffolded files (test_qt_async_file_manager.py, test_async_integration.py)
- [ ] Delete test_async_file_ops.py
- [ ] Test remaining files
- [ ] Commit with message

### Task 3.3: Preview Handler Consolidation
- [ ] Analyze test_preview_handler.py for unique tests
- [ ] Migrate QTextBrowser tests to test_preview_handler_base.py
- [ ] Ensure GPU tests remain in test_preview_handler_gpu.py
- [ ] Delete test_preview_handler.py
- [ ] Test both remaining files
- [ ] Commit with message

### Task 3.4: Chat System Consolidation
- [ ] Analyze test_chat_history_persistence.py
- [ ] Migrate history tests to test_chat_manager.py
- [ ] Organize into clear sections
- [ ] Delete test_chat_history_persistence.py
- [ ] Test all chat files
- [ ] Commit with message

### Post-Phase Validation
- [ ] Run full test suite
- [ ] Compare test counts (before vs after)
- [ ] Check coverage report (should be ~100%)
- [ ] Verify no duplicate test names
- [ ] Verify no orphaned fixtures
- [ ] Update TEST_COVERAGE_SUMMARY.md
- [ ] Create summary commit message
- [ ] Push to origin/main

---

## Expected Commit Messages

### Task 3.1 Commit
```
Consolidate GPU and hardware detection tests (Phase 3.1)

Merge 3 test files into 1 organized file:
- test_gpu_detection.py: 74 tests → 85 tests (kept as base)
- test_gpu_cache.py: 18 tests → merged
- test_hardware_detection.py: 40 tests → merged

Impact:
- Files: 3 → 1 (-2 files)
- Tests: 132 → 85 (-47 duplicate/redundant tests)
- Organization: 8 clear test sections
- Coverage: 100% maintained

Removed duplicate tests:
- GPUInfo creation tests (kept more comprehensive versions)
- Cache validation tests (kept focused versions)
- Detection integration tests (merged scenarios)

All tests passing: ✅
Coverage maintained: ✅
```

### Task 3.2 Commit
```
Consolidate async file operation tests (Phase 3.2)

Merge 3 files, delete 2 scaffolded files:
- test_async_file_handler.py: 29 tests → 35 tests (kept as base)
- test_async_file_ops.py: 9 tests → merged
- test_qt_async_file_manager.py: 0 tests → deleted (scaffolded)
- test_async_integration.py: 0 tests → deleted (scaffolded)

Impact:
- Files: 5 → 2 (-3 files)
- Tests: 40 → 37 (-3 duplicate tests)
- Coverage: 100% maintained

All tests passing: ✅
```

### Task 3.3 Commit
```
Consolidate preview handler tests (Phase 3.3)

Merge preview handler tests into 2 organized files:
- test_preview_handler_base.py: 29 tests → 32 tests (base + common)
- test_preview_handler_gpu.py: 3 tests → 6 tests (GPU-specific)
- test_preview_handler.py: 4 tests → deleted (merged)

Impact:
- Files: 3 → 2 (-1 file)
- Tests: 36 → 38 (better organization, -2 duplicates)
- Coverage: 100% maintained
- Clear separation: base/common vs GPU-specific

All tests passing: ✅
```

### Task 3.4 Commit
```
Consolidate chat system tests (Phase 3.4)

Merge history tests into chat manager tests:
- test_chat_manager.py: 24 tests → 42 tests (added history tests)
- test_chat_history_persistence.py: 18 tests → deleted (merged)

Impact:
- Files: 5 → 4 (-1 file)
- Tests: 112 → 114 (better organization, removed 18 duplicates, added 20 new coverage)
- Coverage: 100% maintained
- Improved organization: history management now with manager tests

All tests passing: ✅
```

### Final Summary Commit (optional)
```
Complete Phase 3: Test consolidation (4 tasks)

Consolidation Summary:
- GPU/Hardware: 3 files → 1 file
- Async Operations: 5 files → 2 files
- Preview Handlers: 3 files → 2 files
- Chat System: 5 files → 4 files

Total Impact:
- Files: 16 → 9 (-7 files, 44% reduction)
- Tests: 320 → 274 (-46 duplicate/scaffolded tests)
- Lines: ~5,000 → ~3,500 (-1,500 lines, 30% reduction)
- Coverage: 100% maintained
- Organization: Significantly improved

All tests passing: ✅
Coverage maintained: ✅
Maintainability: Greatly improved ✅
```

---

## Notes for Implementer

**Critical Success Factors:**
1. **Work incrementally**: Complete one task fully before starting the next
2. **Test frequently**: Run tests after every significant change
3. **Commit often**: Commit after each successful task for easy rollback
4. **Preserve coverage**: Check coverage after each task
5. **Document decisions**: Note why tests were kept/removed/merged

**Common Pitfalls:**
- ❌ Merging files too aggressively (losing test organization)
- ❌ Removing tests without verifying they're truly duplicates
- ❌ Breaking fixture dependencies when moving tests
- ❌ Creating files that are too large (>1000 lines)
- ❌ Losing test clarity in the pursuit of fewer files

**When in Doubt:**
- If tests aren't truly duplicates, keep both
- If file organization becomes unclear, split rather than merge
- If coverage drops, roll back immediately
- If test names conflict, rename to be more specific

**File Size Guidelines:**
- Target: 300-600 lines per test file
- Warning: 600-1000 lines (consider splitting)
- Critical: >1000 lines (must split into logical sections)

**Best Practices:**
1. **Keep clear section comments** using class-based organization
2. **Preserve test documentation** (docstrings are valuable)
3. **Maintain fixture locality** (fixtures near the tests that use them)
4. **Use descriptive test names** (even if they're longer)
5. **Group by functionality** not by arbitrary line count

---

**Last Updated:** November 2, 2025
**Status:** READY FOR EXECUTION
**Prerequisites:** Phase 1 and Phase 2 must be complete
**Estimated Total Time:** 8-12 hours (2-3 hours per task)
