# Test Coverage Roadmap to 100%

**Current Status:** 77.64% → **Target:** 100%

**Last Updated:** November 9, 2025

---

## 📊 Coverage Summary

```
Current: 77.64%
Target: 100%
Gap: 22.36% (3,038 uncovered lines)

Files: 94 total
  - 100% coverage: 48 files ✅
  - 90-99% coverage: 15 files
  - 70-89% coverage: 8 files
  - 50-69% coverage: 6 files
  - 0-49% coverage: 4 files
  - 0% coverage: 23 files ❌
```

---

## 🎯 Phased Approach

### **Phase 1: Quick Wins (Target: 80% coverage)** ⭐ CURRENT
**Estimated Time:** 2-3 hours
**Expected Gain:** +2.5%

**Targets:**
- ✅ `json_utils.py` - 65% → 100% (COMPLETED - 17 tests)
- ✅ `syntax_checker.py` - 63% → 95% (COMPLETED - 38 tests)
- ✅ `autocomplete_engine.py` - 61% → 90% (COMPLETED - 37 tests)
- ✅ `syntax_validators.py` - 69% → 90% (COMPLETED - 66 tests)
- ⏭️ `secure_credentials.py` - 77% → 95% (~20 lines, mocking issues)

### **Phase 2: Core Modules (Target: 85% coverage)**
**Estimated Time:** 4-6 hours
**Expected Gain:** +5%

**Targets:**
- `autocomplete_providers.py` - 40% → 80% (~52 lines)
- `claude_worker.py` - 75% → 95% (~18 lines)
- `git_worker.py` - 78% → 90% (~27 lines)
- `ollama_chat_worker.py` - 86% → 95% (~12 lines)
- `worker_tasks.py` - 81% → 95% (~20 lines)

### **Phase 3: UI Components (Target: 90% coverage)**
**Estimated Time:** 6-8 hours
**Expected Gain:** +5%

**Targets:**
- `syntax_checker_manager.py` - 84% → 95% (~12 lines)
- `autocomplete_manager.py` - (TBD - check current coverage)
- `worker_manager.py` - 95% → 98% (~10 lines)
- Fix 158 failing tests (UI state, workers, etc.)

### **Phase 4: Zero Coverage Files (Target: 95% coverage)**
**Estimated Time:** 8-12 hours
**Expected Gain:** +5%

**Critical Files (0% coverage, 23 total):**
1. `dependency_validator.py` - 130 lines
2. `macos_optimizer.py` - 156 lines
3. `macos_file_ops.py` - 96 lines
4. `template_browser.py` - 177 lines
5. Plus 19 more files...

### **Phase 5: Edge Cases & Error Paths (Target: 100% coverage)**
**Estimated Time:** 4-6 hours
**Expected Gain:** +5%

**Focus:**
- Error handling paths
- Edge cases in existing modules
- Platform-specific code (macOS, Linux, Windows)
- Integration scenarios

---

## 📝 Detailed File Breakdown

### **0% Coverage (23 files - 2,000+ lines)**

| File | Lines | Priority | Complexity | Notes |
|------|-------|----------|------------|-------|
| `dependency_validator.py` | 130 | HIGH | Medium | Core validation logic |
| `macos_optimizer.py` | 156 | MEDIUM | High | Platform-specific (macOS only) |
| `macos_file_ops.py` | 96 | MEDIUM | Medium | Platform-specific (macOS only) |
| `template_browser.py` | 177 | LOW | High | Qt UI component (complex to test) |
| *(19 more files)* | ~1,500 | VARIES | VARIES | See detailed list below |

### **Low Coverage (<70%, 10 files)**

| File | Current | Target | Gap | Priority | Complexity |
|------|---------|--------|-----|----------|------------|
| `autocomplete_providers.py` | 40% | 80% | 35 lines | HIGH | Medium |
| `autocomplete_engine.py` | 61% | 90% | 25 lines | HIGH | Medium |
| `syntax_checker.py` | 63% | 95% | 28 lines | HIGH | Low |
| `json_utils.py` | ✅ 100% | ✅ 100% | 0 lines | ✅ DONE | Low |
| `syntax_validators.py` | 69% | 90% | 32 lines | MEDIUM | Medium |

### **Medium Coverage (70-89%, 8 files)**

| File | Current | Target | Gap | Priority |
|------|---------|--------|-----|----------|
| `secure_credentials.py` | 77% | 95% | 21 lines | HIGH |
| `git_worker.py` | 78% | 90% | 27 lines | MEDIUM |
| `worker_tasks.py` | 81% | 95% | 20 lines | MEDIUM |
| `syntax_checker_manager.py` | 84% | 95% | 12 lines | LOW |
| `ollama_chat_worker.py` | 86% | 95% | 12 lines | LOW |

---

## 🚧 Known Blockers

### **1. Platform-Specific Code**
**Files:** `macos_optimizer.py`, `macos_file_ops.py`
**Issue:** macOS-specific functionality can't be fully tested on all platforms
**Solution:**
- Skip tests on non-macOS platforms with `@pytest.mark.skipif`
- Mock system calls for cross-platform testing
- Document manual testing requirements

### **2. Complex Qt UI Components**
**Files:** `template_browser.py`, `*_dialog.py`
**Issue:** Qt event loop blocking, modal dialogs
**Solution:**
- Use `qtbot` fixtures from pytest-qt
- Mock Qt widgets where appropriate
- Skip tests that require user interaction with documented manual testing

### **3. Failing Tests (158 tests)**
**Areas:** UI state manager, workers, error handling
**Issue:** Tests fail due to mock setup, threading, or Qt interactions
**Solution:**
- Systematic fix approach (Phase 3)
- Focus on highest-value failures first
- Some may be legitimate bugs requiring code fixes

---

## 📈 Progress Tracking

### **Completed (November 9, 2025)**
- ✅ `json_utils.py` - 65% → 100% (17 tests)
- ✅ Committed: `0d65822` "test: Add comprehensive tests for json_utils.py"
- ✅ `syntax_checker.py` - 63% → 95% (38 tests)
- ✅ Committed: `6de3ba0` "test: Add comprehensive tests for syntax_checker.py"
- ✅ `autocomplete_engine.py` - 61% → 90% (37 tests)
- ✅ Committed: TBD "test: Add comprehensive tests for autocomplete_engine.py"
- ✅ `syntax_validators.py` - 69% → 90% (66 tests)
- ✅ Committed: TBD "test: Add comprehensive tests for syntax_validators.py"

### **In Progress**
- ⏳ Quick wins phase (1 module remaining: secure_credentials.py)

### **Next Session Goals**
1. Complete Phase 1 quick wins (→ 80% coverage)
2. Start Phase 2 core modules
3. Fix top 10 most valuable failing tests

---

## 🎯 Success Metrics

| Milestone | Coverage | Lines Covered | Tests Added | ETA |
|-----------|----------|---------------|-------------|-----|
| Phase 1 Complete | 80% | +340 | +50-80 | 2-3 hours |
| Phase 2 Complete | 85% | +680 | +80-120 | 6-9 hours |
| Phase 3 Complete | 90% | +1,020 | +120-180 | 12-17 hours |
| Phase 4 Complete | 95% | +1,700 | +200-300 | 20-29 hours |
| **100% Coverage** | **100%** | **+3,038** | **300-450** | **24-35 hours** |

---

## 🛠️ Tools & Commands

### **Run Coverage Analysis**
```bash
# Full coverage report
pytest tests/unit --cov=src/asciidoc_artisan --cov-report=html --cov-report=term-missing

# Open HTML report
open htmlcov/index.html

# Specific file coverage
pytest tests/unit/core/test_json_utils.py --cov=src/asciidoc_artisan/core/json_utils.py --cov-report=term-missing
```

### **Find Uncovered Lines**
```bash
# Show files with <80% coverage
python3 -m coverage report | grep -E " [0-7][0-9]%"

# Show missing lines for specific file
python3 -m coverage report --show-missing | grep "syntax_checker"
```

### **Test Specific Module**
```bash
# Run tests for one file
pytest tests/unit/core/test_syntax_checker.py -v

# Run with coverage
pytest tests/unit/core/test_syntax_checker.py --cov=src/asciidoc_artisan/core/syntax_checker.py
```

---

## 📚 Resources

**Documentation:**
- `TEST_LIMITATIONS.md` - Known test limitations and workarounds
- `CLAUDE.md` - Project architecture and testing guidelines
- `SPECIFICATIONS.md` - Functional requirements

**Test Examples:**
- `tests/unit/core/test_json_utils.py` - Comprehensive test example (17 tests, 100% coverage)
- `tests/unit/ui/test_spell_check_manager.py` - Qt UI testing example (66 tests, skip patterns)
- `tests/unit/workers/test_git_worker.py` - Worker thread testing example

**Pytest Plugins:**
- `pytest-qt` - Qt testing utilities
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

---

## 💡 Best Practices

### **Writing High-Quality Tests**

1. **Test Both Success and Error Paths**
   ```python
   def test_function_success(self):
       result = function(valid_input)
       assert result == expected

   def test_function_error(self):
       with pytest.raises(ValueError):
           function(invalid_input)
   ```

2. **Test Edge Cases**
   - Empty inputs
   - None values
   - Very large inputs
   - Boundary conditions

3. **Use Descriptive Test Names**
   ```python
   # Good
   def test_loads_with_empty_string_raises_error(self):

   # Bad
   def test_loads_error(self):
   ```

4. **One Assertion Per Test (when possible)**
   - Makes failures easier to diagnose
   - Each test has a clear purpose

5. **Mock External Dependencies**
   ```python
   @patch('module.external_call')
   def test_function(self, mock_external):
       mock_external.return_value = "mocked"
       # Test your code
   ```

---

## 🔄 Continuous Improvement

### **After Each Phase:**
1. ✅ Run full test suite to verify no regressions
2. ✅ Update this roadmap with actual vs estimated time
3. ✅ Commit tests with descriptive messages
4. ✅ Update coverage percentage in CLAUDE.md

### **Weekly Goals:**
- Increase coverage by 2-5% per week
- Fix 10-20 failing tests per week
- Review and refactor existing tests

### **Quality Gates:**
- All new code must have 90%+ coverage
- PR reviews must include test coverage check
- Coverage must not decrease in any PR

---

**Last Updated:** November 9, 2025
**Current Coverage:** 77.64% → **Next Milestone:** 80%
**Estimated Completion:** Late November - Early December 2025
