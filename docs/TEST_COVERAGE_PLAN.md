# Test Coverage Push: 92.1% → 100%

**Status:** 📋 PLANNED
**Date:** November 5, 2025
**Current Coverage:** 92.1% (4528/4917 statements)
**Target:** 100% (need 389 more statements)
**Estimated Effort:** 16-24 hours

---

## Executive Summary

Current test coverage is **92.1%**, significantly higher than the 60% mentioned in ROADMAP.md. This is excellent progress! However, to achieve GRANDMASTER quality status and meet the critical Phase 2 goal, we need to push to **100% coverage**.

**Key Stats:**
- **Missing statements:** 389 (7.9% of codebase)
- **Files needing attention:** 23 files
- **Perfect coverage files:** 16 files (already at 100%)
- **Estimated new tests:** ~40-50 test cases

---

## Priority Breakdown

### 🔴 CRITICAL Priority (1 file, 30 statements)

**Effort:** 2-3 hours | **Impact:** High

| File | Coverage | Missing | Priority |
|------|----------|---------|----------|
| `src/asciidoc_artisan/core/__init__.py` | 45.5% | 30 | 🔴 CRITICAL |

**Action Plan:**
- Review `__init__.py` exports and module-level functions
- Create `tests/unit/core/test_core_init.py`
- Test cases:
  - Import verification (ensure all exports are valid)
  - Module-level constants
  - Package metadata
  - Lazy import fallbacks (if any)

---

### ⚠️ HIGH Priority (4 files, 161 statements)

**Effort:** 6-8 hours | **Impact:** High

| File | Coverage | Missing | Priority |
|------|----------|---------|----------|
| `src/asciidoc_artisan/claude/claude_client.py` | 58.3% | 48 | ⚠️ HIGH |
| `src/asciidoc_artisan/workers/worker_tasks.py` | 66.7% | 35 | ⚠️ HIGH |
| `src/asciidoc_artisan/workers/github_cli_worker.py` | 68.6% | 38 | ⚠️ HIGH |
| `src/asciidoc_artisan/workers/preview_worker.py` | 74.4% | 40 | ⚠️ HIGH |

**Action Plans:**

#### 1. `claude/claude_client.py` (48 missing)
- **Current tests:** `tests/unit/claude/test_claude_client.py` (14 tests)
- **Gaps:** Error handling, edge cases, connection failures
- **New tests needed:**
  - Invalid API key scenarios
  - Network timeouts
  - Rate limiting
  - Invalid model names
  - Malformed responses
  - Token counting edge cases

#### 2. `workers/worker_tasks.py` (35 missing)
- **Current tests:** Limited coverage
- **Gaps:** Task lifecycle, error propagation
- **New tests needed:**
  - Task priority queuing
  - Task cancellation mid-execution
  - Worker pool exhaustion
  - Task timeout handling
  - Exception propagation

#### 3. `workers/github_cli_worker.py` (38 missing)
- **Current tests:** `tests/test_github_cli_worker.py` (21 tests)
- **Gaps:** Error conditions, edge cases
- **New tests needed:**
  - GitHub CLI not installed
  - Authentication failures
  - Network errors
  - Invalid JSON responses
  - Rate limit handling
  - Subprocess timeout

#### 4. `workers/preview_worker.py` (40 missing)
- **Current tests:** Basic rendering tests
- **Gaps:** Error handling, edge cases
- **New tests needed:**
  - Invalid AsciiDoc syntax
  - Large document handling
  - Rendering cancellation
  - Cache invalidation
  - Resource cleanup

---

### 📋 MEDIUM Priority (4 files, 90 statements)

**Effort:** 4-6 hours | **Impact:** Medium

| File | Coverage | Missing | Priority |
|------|----------|---------|----------|
| `src/asciidoc_artisan/claude/claude_worker.py` | 75.0% | 18 | 📋 MEDIUM |
| `src/asciidoc_artisan/workers/git_worker.py` | 77.7% | 50 | 📋 MEDIUM |
| `src/asciidoc_artisan/workers/base_worker.py` | 77.8% | 6 | 📋 MEDIUM |
| `src/asciidoc_artisan/core/lazy_utils.py` | 83.0% | 16 | 📋 MEDIUM |

**Action Plans:**

#### 1. `claude/claude_worker.py` (18 missing)
- **Current tests:** `tests/unit/claude/test_claude_worker.py` (19 tests)
- **Gaps:** Worker lifecycle, thread safety
- **New tests needed:**
  - Worker thread cleanup
  - Concurrent operation prevention
  - Signal emission edge cases

#### 2. `workers/git_worker.py` (50 missing)
- **Current tests:** `tests/unit/workers/test_git_worker.py` (multiple)
- **Gaps:** Git command failures, edge cases
- **New tests needed:**
  - Git not installed
  - Repository corruption
  - Merge conflicts
  - Detached HEAD state
  - Subprocess errors

#### 3. `workers/base_worker.py` (6 missing)
- **Current tests:** Indirectly tested via subclasses
- **Gaps:** Base class methods
- **New tests needed:**
  - Abstract method enforcement
  - Worker lifecycle management
  - Signal/slot connections

#### 4. `core/lazy_utils.py` (16 missing)
- **Current tests:** Limited
- **Gaps:** Lazy loading edge cases
- **New tests needed:**
  - Module import failures
  - Circular dependencies
  - Import errors propagation

---

### ✅ LOW Priority (14 files, 108 statements)

**Effort:** 4-6 hours | **Impact:** Low

Files with 90-99% coverage that need minor polish. These are mostly edge cases and error conditions.

**Strategy:**
- Review each file's coverage report (htmlcov/*.html)
- Identify missing lines
- Add targeted test cases
- Focus on error handling and edge cases

---

## Implementation Strategy

### Phase 1: CRITICAL ✅ COMPLETE
**Goal:** Fix core/__init__.py (45.5% → 100%)
- ✅ Create comprehensive import tests (89 tests created)
- ✅ Test all module-level functions
- ✅ Verify package metadata
- ✅ **Success Criteria:** core/__init__.py at 100%
- **Completion Date:** November 5, 2025
- **Duration:** 1 hour

### Phase 2: HIGH Priority (Week 1-2)
**Goal:** Fix 4 high-priority files (58-74% → 100%)
- claude/claude_client.py
- workers/worker_tasks.py
- workers/github_cli_worker.py
- workers/preview_worker.py
- **Success Criteria:** All 4 files at 90%+

### Phase 3: MEDIUM Priority (Week 2)
**Goal:** Fix 4 medium-priority files (75-83% → 100%)
- claude/claude_worker.py
- workers/git_worker.py
- workers/base_worker.py
- core/lazy_utils.py
- **Success Criteria:** All 4 files at 95%+

### Phase 4: LOW Priority (Week 3)
**Goal:** Polish 14 low-priority files (90-99% → 100%)
- Address minor gaps
- Edge case testing
- Error condition coverage
- **Success Criteria:** All files at 100%

---

## Testing Best Practices

### 1. Mock External Dependencies
```python
@pytest.fixture
def mock_anthropic_client(mocker):
    """Mock Anthropic API client."""
    return mocker.patch("anthropic.Anthropic")
```

### 2. Test Error Conditions
```python
def test_api_error_handling(mock_client):
    """Test API error handling."""
    mock_client.messages.create.side_effect = APIError("Rate limit")
    result = client.send_message("test")
    assert not result.success
    assert "rate limit" in result.error.lower()
```

### 3. Test Thread Safety
```python
def test_concurrent_operations_prevented(qtbot):
    """Test reentrancy guard."""
    worker._is_processing = True
    worker.send_message("test")
    # Should not start new operation
    assert worker._operation is None
```

### 4. Test Resource Cleanup
```python
def test_worker_cleanup():
    """Test worker resources are released."""
    worker.start()
    worker.quit()
    worker.wait(1000)
    assert not worker.isRunning()
```

---

## Success Criteria

- ✅ **Overall coverage:** 100% (from 92.1%)
- ✅ **All CRITICAL files:** 100%
- ✅ **All HIGH priority files:** 95%+
- ✅ **All MEDIUM priority files:** 95%+
- ✅ **All LOW priority files:** 98%+
- ✅ **Test pass rate:** 100%
- ✅ **No Python fatal crashes:** Zero crashes
- ✅ **CI/CD:** All checks pass

---

## Tracking Progress

### Week 1 Goals
- [ ] Phase 1: CRITICAL complete (core/__init__.py)
- [ ] Phase 2: Start HIGH priority (2/4 files)

### Week 2 Goals
- [ ] Phase 2: Complete HIGH priority (4/4 files)
- [ ] Phase 3: Start MEDIUM priority (2/4 files)

### Week 3 Goals
- [ ] Phase 3: Complete MEDIUM priority (4/4 files)
- [ ] Phase 4: Start LOW priority (7/14 files)

### Week 4 Goals
- [ ] Phase 4: Complete LOW priority (14/14 files)
- [ ] Final verification: 100% coverage achieved
- [ ] Documentation updated

---

## Resources

- **Coverage Report:** `htmlcov/index.html`
- **Analysis Script:** `scripts/analyze_coverage.py`
- **Test Guide:** `docs/TESTING.md`
- **Async Test Guide:** `docs/ASYNC_TEST_REFACTORING_REQUIREMENTS.md`
- **Thread Isolation Guide:** `docs/WORKER_THREAD_ISOLATION_FIX.md`

---

**Last Updated:** November 5, 2025
**Next Review:** November 12, 2025 (Phase 2 checkpoint)
