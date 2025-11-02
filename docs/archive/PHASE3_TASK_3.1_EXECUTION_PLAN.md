# Phase 3 Task 3.1: GPU/Hardware Detection Consolidation - Execution Plan

**Date:** November 2, 2025
**Status:** READY FOR EXECUTION
**Risk Level:** MEDIUM (file consolidation with 127 tests)
**Estimated Time:** 2-3 hours

---

## Current State Analysis

### Files to Consolidate
1. **test_gpu_detection.py** (1,019 lines, 71 tests, 16 classes) - **KEEP AS BASE**
2. **test_gpu_cache.py** (296 lines, 16 tests, module-level functions) - **MERGE IN**
3. **test_hardware_detection.py** (567 lines, 40 tests, 9 classes) - **MERGE IN**

**Total:** 1,882 lines, 127 unique test functions (132 test executions due to parametrization)

### Duplicate Tests Identified
```bash
test_cache_entry_creation       # In both gpu_detection.py and gpu_cache.py
test_cache_entry_to_gpu_info    # In both gpu_detection.py and gpu_cache.py
test_get_gpu_info_force_redetect # In both gpu_detection.py and gpu_cache.py
```

**Strategy:** Keep versions in `test_gpu_detection.py` (more comprehensive class-based tests)

---

## Consolidation Strategy

### Step 1: Backup Current State ✅
```bash
# Create backup branch
git checkout -b phase3-task-3.1-gpu-consolidation

# Copy files to archive for reference
cp tests/unit/core/test_gpu_cache.py docs/archive/test_gpu_cache.py.backup
cp tests/unit/core/test_hardware_detection.py docs/archive/test_hardware_detection.py.backup
```

### Step 2: Analyze test_gpu_detection.py Structure
**Current Classes (16):**
1. `TestGPUInfo` - GPUInfo dataclass tests
2. `TestGPUCacheEntry` - Cache entry tests (OVERLAP with test_gpu_cache.py)
3. `TestGPUDetectionCache` - Cache operations (OVERLAP with test_gpu_cache.py)
4. `TestCacheClear` - Cache clearing
5. `TestCheckDRIDevices` - DRI device detection
6. `TestCheckNvidiaGPU` - NVIDIA detection
7. `TestCheckAMDGPU` - AMD detection
8. `TestCheckIntelGPU` - Intel detection
9. `TestCheckOpenGLRenderer` - OpenGL checks
10. `TestCheckWSLgEnvironment` - WSLg detection
11. `TestCheckIntelNPU` - NPU detection
12. `TestDetectComputeCapabilities` - Compute capability detection
13. `TestDetectGPU` - Main GPU detection (parametrized)
14. `TestLogGPUInfo` - Logging functionality
15. `TestGetGPUInfo` - High-level API
16. `TestMainCLI` - CLI interface

### Step 3: Merge test_gpu_cache.py Tests
**Tests to merge (13 non-duplicate tests):**
1. ~~`test_cache_entry_creation`~~ - DUPLICATE (skip)
2. ~~`test_cache_entry_to_gpu_info`~~ - DUPLICATE (skip)
3. `test_cache_entry_validation` - UNIQUE (parametrized, add to TestGPUCacheEntry)
4. `test_cache_save_creates_file` - UNIQUE (add to TestGPUDetectionCache)
5. `test_cache_save_and_load` - UNIQUE (add to TestGPUDetectionCache)
6. `test_cache_load_nonexistent_file` - UNIQUE (add to TestGPUDetectionCache)
7. `test_cache_load_expired` - UNIQUE (add to TestGPUDetectionCache)
8. `test_cache_load_invalid_json` - UNIQUE (add to TestGPUDetectionCache)
9. `test_cache_clear` - UNIQUE (add to TestCacheClear)
10. `test_cache_clear_nonexistent` - UNIQUE (add to TestCacheClear)
11. `test_cache_format` - UNIQUE (add to TestGPUDetectionCache)
12. `test_get_gpu_info_uses_cache` - UNIQUE (add to TestGetGPUInfo)
13. ~~`test_get_gpu_info_force_redetect`~~ - DUPLICATE (skip)
14. `test_cache_with_npu` - UNIQUE (add to TestGPUDetectionCache)
15. `test_cache_without_gpu` - UNIQUE (add to TestGPUDetectionCache)
16. `test_cache_ttl_boundary` - UNIQUE (add to TestGPUDetectionCache)

**Fixtures to merge:**
- `mock_cache_file` - ADD to test_gpu_detection.py fixtures
- `sample_gpu_info` - ALREADY EXISTS in test_gpu_detection.py (verify compatibility)

### Step 4: Merge test_hardware_detection.py Tests
**Classes to merge (9 classes):**
1. `TestGPUDetection` - General GPU tests → Merge into TestDetectGPU
2. `TestHardwareCapabilities` - Capability tests → Merge into TestDetectComputeCapabilities
3. `TestEdgeCases` - Edge cases → Distribute to relevant classes
4. `TestIntelGPUDetection` - Intel GPU → Merge into TestCheckIntelGPU
5. `TestAMDGPULspciPath` - AMD lspci → Merge into TestCheckAMDGPU
6. `TestNPUDetection` - NPU tests → Merge into TestCheckIntelNPU
7. `TestCPUInfo` - CPU detection → ADD as new class (not GPU-specific but related)
8. `TestDetectAll` - Comprehensive tests → Merge into TestDetectGPU
9. `TestPrintHardwareReport` - Reporting → ADD as new class or merge into TestLogGPUInfo

**Estimated unique tests:** ~35-38 (allowing for 2-5 duplicates/overlap)

### Step 5: Create New Consolidated File Structure

**Proposed Organization:**

```python
"""
Tests for GPU and hardware detection.

Comprehensive test suite for:
- GPU detection (NVIDIA, AMD, Intel)
- NPU detection (Intel Neural Processing Unit)
- GPU caching and persistence
- Hardware capability detection
- Compute framework detection (CUDA, OpenCL, Vulkan, OpenVINO)
- CPU information retrieval

Consolidated from:
- test_gpu_detection.py (71 tests)
- test_gpu_cache.py (16 tests, 3 duplicates removed = 13 unique)
- test_hardware_detection.py (40 tests, estimated 2-5 duplicates = 35-38 unique)

Total tests: ~119-122 tests (reduced from 127)
"""

# SECTION 1: IMPORTS
# ... (combined imports from all files)

# SECTION 2: FIXTURES
# ... (combined fixtures, deduplicated)

# SECTION 3: GPU INFO TESTS
class TestGPUInfo:
    """Test GPUInfo dataclass creation and properties."""
    # ... (existing tests from test_gpu_detection.py)

# SECTION 4: CACHE ENTRY TESTS
class TestGPUCacheEntry:
    """Test GPU cache entry validation and serialization."""
    # ... (existing + merged from test_gpu_cache.py)
    # ADD: test_cache_entry_validation (parametrized)

# SECTION 5: CACHE OPERATIONS
class TestGPUDetectionCache:
    """Test GPU detection cache save/load operations."""
    # ... (existing + merged from test_gpu_cache.py)
    # ADD: test_cache_save_creates_file
    # ADD: test_cache_save_and_load
    # ADD: test_cache_load_nonexistent_file
    # ADD: test_cache_load_expired
    # ADD: test_cache_load_invalid_json
    # ADD: test_cache_format
    # ADD: test_cache_with_npu
    # ADD: test_cache_without_gpu
    # ADD: test_cache_ttl_boundary

# SECTION 6: CACHE CLEARING
class TestCacheClear:
    """Test cache clearing operations."""
    # ... (existing + merged)
    # ADD: test_cache_clear
    # ADD: test_cache_clear_nonexistent

# SECTION 7: DRI DEVICE DETECTION
class TestCheckDRIDevices:
    """Test DRI device detection."""
    # ... (existing tests)

# SECTION 8: NVIDIA GPU DETECTION
class TestCheckNvidiaGPU:
    """Test NVIDIA GPU detection."""
    # ... (existing tests)

# SECTION 9: AMD GPU DETECTION
class TestCheckAMDGPU:
    """Test AMD GPU detection."""
    # ... (existing tests)
    # ADD: Tests from TestAMDGPULspciPath

# SECTION 10: INTEL GPU DETECTION
class TestCheckIntelGPU:
    """Test Intel GPU detection."""
    # ... (existing tests)
    # ADD: Tests from TestIntelGPUDetection

# SECTION 11: OPENGL RENDERER
class TestCheckOpenGLRenderer:
    """Test OpenGL renderer detection."""
    # ... (existing tests)

# SECTION 12: WSLG ENVIRONMENT
class TestCheckWSLgEnvironment:
    """Test WSLg environment detection."""
    # ... (existing tests)

# SECTION 13: INTEL NPU DETECTION
class TestCheckIntelNPU:
    """Test Intel NPU (Neural Processing Unit) detection."""
    # ... (existing tests)
    # ADD: Tests from TestNPUDetection

# SECTION 14: COMPUTE CAPABILITIES
class TestDetectComputeCapabilities:
    """Test compute capability detection (CUDA, OpenCL, Vulkan, OpenVINO)."""
    # ... (existing tests)
    # ADD: Tests from TestHardwareCapabilities

# SECTION 15: MAIN GPU DETECTION
class TestDetectGPU:
    """Test main GPU detection logic."""
    # ... (existing tests including parametrized)
    # ADD: Tests from TestGPUDetection, TestDetectAll, TestEdgeCases

# SECTION 16: CPU INFORMATION (NEW)
class TestCPUInfo:
    """Test CPU information retrieval."""
    # ADD: All tests from test_hardware_detection.py::TestCPUInfo

# SECTION 17: LOGGING AND REPORTING
class TestLogGPUInfo:
    """Test GPU information logging."""
    # ... (existing tests)
    # CONSIDER: Merge TestPrintHardwareReport here

# SECTION 18: HIGH-LEVEL API
class TestGetGPUInfo:
    """Test high-level get_gpu_info() API."""
    # ... (existing tests)
    # ADD: test_get_gpu_info_uses_cache

# SECTION 19: CLI INTERFACE
class TestMainCLI:
    """Test CLI interface for GPU detection."""
    # ... (existing tests)

# SECTION 20: HARDWARE REPORTING (NEW)
class TestPrintHardwareReport:
    """Test hardware reporting functionality."""
    # ADD: Tests from test_hardware_detection.py::TestPrintHardwareReport
    # OR: Merge into TestLogGPUInfo
```

---

## Execution Steps

### Step 1: Preparation
```bash
# Ensure we're on main with clean state
git checkout main
git status

# Create working branch
git checkout -b phase3-task-3.1-gpu-consolidation

# Run baseline tests
pytest tests/unit/core/test_gpu*.py tests/unit/core/test_hardware*.py -v --tb=short
# Expected: 132 passed

# Count tests
pytest tests/unit/core/test_gpu*.py tests/unit/core/test_hardware*.py --collect-only -q
# Expected: 132 tests collected
```

### Step 2: Create Backup
```bash
# Backup files
mkdir -p docs/archive/phase3_backups
cp tests/unit/core/test_gpu_cache.py docs/archive/phase3_backups/
cp tests/unit/core/test_hardware_detection.py docs/archive/phase3_backups/
cp tests/unit/core/test_gpu_detection.py docs/archive/phase3_backups/
```

### Step 3: Manual Consolidation
**Option A: Manual merge (safer, 2-3 hours)**
1. Open test_gpu_detection.py in editor
2. Add fixtures from test_gpu_cache.py (mock_cache_file if not present)
3. Add 13 unique tests from test_gpu_cache.py to appropriate classes
4. Add 35-38 tests from test_hardware_detection.py to appropriate classes
5. Verify imports are complete
6. Add section comments for organization

**Option B: Automated merge script (riskier, 30 minutes + 1 hour validation)**
- Create Python script to parse and merge test files
- Higher risk of missing edge cases

**RECOMMENDATION: Use Option A (Manual merge) for first consolidation**

### Step 4: Validation
```bash
# Test consolidated file
pytest tests/unit/core/test_gpu_detection.py -v --tb=short
# Expected: ~119-122 tests passed (reduction of 10-13 tests from duplicates)

# Check coverage maintained
pytest tests/unit/core/test_gpu_detection.py --cov=src/asciidoc_artisan/core/gpu_detection --cov-report=term-missing
# Expected: 100% coverage maintained
```

### Step 5: Delete Old Files
```bash
# Only after validation passes
git rm tests/unit/core/test_gpu_cache.py
git rm tests/unit/core/test_hardware_detection.py
```

### Step 6: Final Validation
```bash
# Run full test suite
pytest tests/ -v --tb=short
# Expected: All tests pass (total count reduced by 10-13)

# Run just GPU tests again
pytest tests/unit/core/test_gpu_detection.py -v
# Expected: 119-122 passed in <1 second
```

### Step 7: Commit
```bash
git add tests/unit/core/test_gpu_detection.py
git add docs/archive/phase3_backups/
git commit -m "$(cat <<'EOF'
Phase 3 Task 3.1: Consolidate GPU/Hardware Detection tests (3→1 file)

**Summary:**
Consolidated 3 related test files into single comprehensive test file
for GPU and hardware detection functionality.

**Files consolidated:**
- test_gpu_detection.py (71 tests) - BASE FILE (kept)
- test_gpu_cache.py (16 tests) - MERGED IN
- test_hardware_detection.py (40 tests) - MERGED IN

**Impact:**
- Test reduction: 127 → ~119-122 tests (10-13 duplicates removed)
- File reduction: 3 → 1 file (-2 files)
- Line reduction: 1,882 → ~1,650 lines (-232 lines, 12% reduction)
- Test pass rate: 100% maintained
- Coverage: 100% maintained
- Execution time: <1 second maintained

**Duplicates removed:**
- test_cache_entry_creation (kept in TestGPUCacheEntry)
- test_cache_entry_to_gpu_info (kept in TestGPUCacheEntry)
- test_get_gpu_info_force_redetect (kept in TestGetGPUInfo)

**New organization:**
- 20 test classes (up from 16)
- Clear section comments for navigation
- All cache tests under Cache sections
- All vendor-specific tests grouped (NVIDIA, AMD, Intel)
- New TestCPUInfo class for CPU detection
- Comprehensive docstring explaining consolidation

**Backups:** docs/archive/phase3_backups/

**Next:** Phase 3 Task 3.2 (Async File Operations consolidation)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Risk Mitigation

### Risks
1. **Test duplication missed** → Some tests may have subtle differences
2. **Fixture incompatibility** → Fixtures from different files may conflict
3. **Import issues** → Missing imports after consolidation
4. **Test execution order dependencies** → Some tests may depend on execution order

### Mitigations
1. **Careful duplicate analysis** - Compare test logic, not just names
2. **Fixture review** - Verify all fixtures are compatible before merge
3. **Import validation** - Run linter after consolidation
4. **Isolated test runs** - Run tests in random order to catch dependencies

### Rollback Plan
```bash
# If consolidation fails
git checkout main
git branch -D phase3-task-3.1-gpu-consolidation

# Restore from backup
cp docs/archive/phase3_backups/* tests/unit/core/
```

---

## Success Criteria

- [ ] All 119-122 tests pass in consolidated file
- [ ] Test execution time < 1 second
- [ ] 100% code coverage maintained
- [ ] No new warnings or errors
- [ ] Full test suite passes
- [ ] Git history clean and well-documented
- [ ] Backup files archived

---

## Time Estimate

**Manual consolidation:** 2-3 hours
- Analysis: 30 minutes (DONE)
- Merge gpu_cache.py: 45 minutes
- Merge hardware_detection.py: 60 minutes
- Validation: 30 minutes
- Commit: 15 minutes

**Total:** 2-3 hours

---

**Status:** READY FOR EXECUTION
**Next Action:** Execute Step 1 (Preparation)
**Expected Completion:** November 2, 2025 (today)
