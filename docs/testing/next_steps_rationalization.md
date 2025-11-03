# Next Steps Rationalization - Path to 100% Coverage

**Date:** November 3, 2025
**Current Status:** Core tests at 100% (385/385), Overall ~60% coverage
**Goal:** 100% test coverage (CRITICAL priority)

---

## Current State Analysis

### ✅ Strengths
1. **All core module tests passing** (385/385 = 100%)
2. **Solid foundation:** 23 test files with perfect pass rates
3. **Clear documentation:** Baseline analysis and 6-week strategy in place
4. **No regressions:** Settings and adaptive_debouncer tests fixed

### ⚠️ Blockers Identified
1. **Missing dependency:** hypothesis module (property-based tests)
2. **Environment issues:** ~150 tests failing due to GPU/keyring/async
3. **Coverage gaps:** Spell checker, Git widgets, workers lack tests

### 📊 Coverage Gap Breakdown
- **Tests blocked:** ~150 (environment-specific)
- **Tests missing:** ~300-400 estimated
- **Current coverage:** 60%+
- **Target coverage:** 100%

---

## Strategic Decision Framework

### Priority Criteria
1. **Impact:** Does this increase coverage significantly?
2. **Effort:** How much work is required?
3. **Dependencies:** Does this unblock other work?
4. **Risk:** Could this break existing tests?
5. **Value:** Does this test critical business logic?

### ROI Analysis (Impact / Effort)

**High ROI (Do First):**
- Fix single-test failures (lazy_utils, search_engine) - Quick wins
- Add hypothesis dependency - Unblocks property-based tests
- Add spell checker tests - New feature (v1.8.0), high business value

**Medium ROI (Do Second):**
- Add Git quick commit widget tests - New feature (v1.9.0), moderate complexity
- Mock environment tests - Reduces noise, enables CI/CD
- Add worker coverage - Core business logic but complex

**Low ROI (Do Later):**
- Fix async tests - High effort, environment-dependent, may need infrastructure changes
- Integration tests - Dependent on unit test completion

---

## Rationalized Next Steps

### Phase 1: Quick Wins (1-2 hours) 🎯 **START HERE**

**Why:** High impact, low effort, immediate coverage gains

**Tasks:**
1. **Fix lazy_utils test failure** (15 mins)
   - Only 1 test failing out of 20
   - Quick assertion fix like settings/debouncer
   - Immediate 0.05% coverage gain

2. **Fix search_engine test failure** (15 mins)
   - Only 1 test failing out of 33
   - Likely similar to other fixes
   - Immediate 0.03% coverage gain

3. **Add hypothesis to requirements** (30 mins)
   - Unblocks property-based tests
   - Unknown test count but likely 10-20 tests
   - Edit requirements.txt or pyproject.toml
   - Verify tests run and pass
   - Potential 1-2% coverage gain

4. **Commit and document Phase 1** (30 mins)
   - Update baseline document
   - Show progress metrics

**Expected Outcome:**
- 385 → 420+ tests passing
- ~60% → ~62% coverage
- All quick wins captured
- Momentum established

---

### Phase 2: High-Value New Features (4-6 hours) 🎯 **DO NEXT**

**Why:** New features (v1.8.0, v1.9.0) need test coverage for production readiness

**Priority 1: Spell Checker Tests** (2-3 hours)
- **Files:** `core/spell_checker.py`, `ui/spell_check_manager.py`
- **Why:** New feature in v1.8.0, zero test coverage, high user impact
- **Tests needed:** 20-30 tests
  - SpellChecker class: word checking, dictionary, language support (12 tests)
  - SpellCheckManager: UI integration, context menu, highlighting (8-10 tests)
  - Integration: F7 toggle, settings persistence (5-8 tests)
- **Expected gain:** 2-3% coverage
- **Risk:** Low - new code, no existing dependencies

**Priority 2: Git Quick Commit Widget Tests** (2-3 hours)
- **File:** `ui/git_quick_commit_widget.py`
- **Why:** New feature in v1.9.0, zero test coverage, Git workflow critical
- **Tests needed:** 15-20 tests
  - Widget display/hide (Ctrl+G) (3-4 tests)
  - Commit message input validation (4-5 tests)
  - Git integration (auto-stage, commit) (5-6 tests)
  - Keyboard shortcuts (Enter/Escape) (3-4 tests)
- **Expected gain:** 1-2% coverage
- **Risk:** Low - new code, some Git worker dependencies

**Expected Outcome:**
- 420 → 470+ tests passing
- ~62% → ~67% coverage
- v1.8.0 and v1.9.0 features have test coverage
- Production readiness improved

---

### Phase 3: Environment Cleanup (2-3 hours) 🎯 **CRITICAL FOR CI/CD**

**Why:** ~150 test failures create noise, block automation, prevent accurate coverage measurement

**Strategy:** Mock or skip environment-dependent tests

**Priority 1: Secure Credentials Tests** (~30 errors)
- **File:** `test_secure_credentials.py`
- **Issue:** Keyring/DBus not available in test environment
- **Solution:** Mock keyring operations using pytest fixtures
- **Effort:** 1 hour
- **Benefit:** Enables CI/CD, removes 30 errors

**Priority 2: GPU/Hardware Detection Tests** (~90 errors)
- **Files:** `test_gpu_detection.py`, `test_hardware_detection.py`
- **Issue:** GPU hardware responses inconsistent in WSL2
- **Solution:** Mock GPU detection calls or skip in non-GPU environments
- **Effort:** 1.5 hours
- **Benefit:** Enables testing on all systems

**Priority 3: Async File Tests** (~82 failures)
- **Files:** `test_async_file_ops.py`, `test_async_file_watcher.py`, `test_qt_async_file_manager.py`
- **Issue:** Event loop / timing issues
- **Solution:** Review async test setup, proper Qt integration
- **Effort:** 2-3 hours (defer to Phase 4 if too complex)
- **Benefit:** Tests critical async I/O feature (v1.6.0)

**Expected Outcome:**
- Error/failure count: ~150 → 0
- CI/CD pipeline: Can run all tests
- Coverage measurement: Accurate baseline

---

### Phase 4: Worker Coverage (6-8 hours) 🎯 **BUSINESS LOGIC CRITICAL**

**Why:** Workers handle core business logic (preview, conversion, Git operations)

**Priority 1: Preview Worker** (2-3 hours)
- **File:** `workers/preview_worker.py`
- **Current:** Partial coverage
- **Tests needed:** 10-15 tests
  - AsciiDoc → HTML rendering (5 tests)
  - Error handling (3-4 tests)
  - Thread safety (3-4 tests)
  - Performance (2-3 tests)
- **Expected gain:** 1.5-2% coverage

**Priority 2: Pandoc Worker** (2-3 hours)
- **File:** `workers/pandoc_worker.py`
- **Current:** Partial coverage
- **Tests needed:** 10-15 tests
  - Format conversions (DOCX, PDF, HTML, MD) (6 tests)
  - Ollama AI integration (3-4 tests)
  - Error handling (2-3 tests)
  - Fallback logic (2-3 tests)
- **Expected gain:** 1.5-2% coverage

**Priority 3: Ollama Chat Worker** (2-3 hours)
- **File:** `workers/ollama_chat_worker.py`
- **Current:** Unknown coverage
- **Tests needed:** 15-20 tests
  - Chat message sending (4-5 tests)
  - 4 context modes (8 tests)
  - History persistence (3-4 tests)
  - Error handling (3-4 tests)
- **Expected gain:** 1-2% coverage

**Expected Outcome:**
- 470 → 520+ tests passing
- ~67% → ~75% coverage
- Critical business logic covered
- **Week 2 target (75%) ACHIEVED**

---

### Phase 5: UI Manager Coverage (6-8 hours) 🎯 **UI INTEGRATION**

**Why:** UI managers orchestrate user interactions, need coverage for regression prevention

**Priority Tests:**
1. **Menu Manager** (1-2 hours, 10-15 tests)
2. **Theme Manager** (1-2 hours, 10-15 tests)
3. **Status Manager** (1-2 hours, 10-15 tests)
4. **Preview Handlers** (2-3 hours, 15-20 tests)

**Expected Outcome:**
- 520 → 580+ tests passing
- ~75% → ~85% coverage

---

### Phase 6: Fill Remaining Gaps (8-10 hours) 🎯 **POLISH**

**Why:** Edge cases, error paths, integration scenarios need coverage

**Strategy:**
1. Run coverage report with --cov-report=term-missing
2. Identify uncovered lines in each module
3. Write targeted tests for each gap
4. Focus on error paths and edge cases

**Expected Outcome:**
- ~85% → ~95% coverage

---

### Phase 7: Final Push to 100% (4-6 hours) 🎯 **GOAL**

**Why:** Achieve CRITICAL priority goal documented in ROADMAP.md

**Strategy:**
1. Coverage report shows exact missing lines
2. Write tests for hardest edge cases
3. Integration tests for user workflows
4. Performance test coverage
5. Document all scenarios

**Expected Outcome:**
- **100% test coverage achieved** ✨
- All acceptance criteria met
- CRITICAL priority goal complete

---

## Recommended Execution Order

### Immediate (Today - 2 hours)
```
1. Fix lazy_utils failure     [15 min]
2. Fix search_engine failure   [15 min]
3. Add hypothesis dependency   [30 min]
4. Commit Phase 1              [30 min]
5. Start spell checker tests   [30 min]
```

### This Week (10-12 hours)
```
Day 1: Phase 1 complete (2h)
Day 2: Phase 2 complete (6h)
Day 3: Phase 3 start (3h)
Day 4: Phase 3 complete (2h)
```

### Week 2 (12-16 hours)
```
Phase 4: Worker coverage (8h)
Phase 5: UI managers start (4-8h)
TARGET: 75% coverage
```

### Weeks 3-4 (16-20 hours)
```
Phase 5: UI managers complete (4-8h)
Phase 6: Fill gaps (8-10h)
TARGET: 90% coverage
```

### Weeks 5-6 (8-12 hours)
```
Phase 7: Final push (6-8h)
Documentation (2-4h)
TARGET: 100% coverage ✨
```

---

## Risk Mitigation

### High Risk
1. **Async tests may be complex**
   - Mitigation: Defer to Phase 4, focus on mockable tests first
   - Fallback: Mark as integration tests, skip in unit tests

2. **Integration tests may crash**
   - Mitigation: Run in separate test suite
   - Fallback: Focus on unit tests for 100% coverage goal

3. **Time estimates may be optimistic**
   - Mitigation: Built in 20-30% buffer
   - Fallback: Prioritize high-ROI tasks first

### Medium Risk
1. **GPU/hardware mocking may be complex**
   - Mitigation: Use pytest.mark.skipif for non-GPU systems
   - Fallback: Run only on systems with GPU

2. **Some code may be untestable**
   - Mitigation: Refactor for testability if needed
   - Fallback: Document why coverage not possible

---

## Success Metrics

### Phase 1 (Quick Wins)
- ✅ All single-test failures fixed
- ✅ Hypothesis tests running
- ✅ 420+ tests passing
- ✅ ~62% coverage

### Phase 2 (New Features)
- ✅ Spell checker tests complete (20-30 tests)
- ✅ Git quick commit tests complete (15-20 tests)
- ✅ 470+ tests passing
- ✅ ~67% coverage

### Phase 3 (Environment Cleanup)
- ✅ Zero test errors/failures
- ✅ CI/CD pipeline functional
- ✅ Accurate coverage measurement

### Phase 4 (Workers)
- ✅ Preview/Pandoc/Chat workers at 90%+ coverage
- ✅ 520+ tests passing
- ✅ ~75% coverage (Week 2 target)

### Phase 5-7 (Final Push)
- ✅ All UI managers tested
- ✅ All edge cases covered
- ✅ **100% coverage achieved** ✨

---

## Key Decision Points

### Should we fix async tests now or later?
**Decision:** Later (Phase 3, defer if complex)
**Reasoning:**
- High effort (~82 tests)
- May require infrastructure changes
- Not blocking other work
- Environment-dependent (may be better as integration tests)

### Should we prioritize spell checker or Git widget first?
**Decision:** Spell checker first
**Reasoning:**
- More tests needed (20-30 vs 15-20)
- Higher user impact (every edit vs occasional commits)
- Fewer dependencies (no Git worker needed)
- Cleaner separation of concerns

### Should we mock GPU tests or skip them?
**Decision:** Mock for now, skip as fallback
**Reasoning:**
- Mocking tests actual detection logic
- Skipping leaves coverage gaps
- Can always add skip for non-GPU CI/CD
- GPU detection is critical feature (v1.4.0)

---

## Conclusion

**Recommended Immediate Action:**
Start with Phase 1 (Quick Wins) - 2 hours to fix single failures and add hypothesis.

**Expected Timeline:**
- Week 1: Phases 1-3 complete (15-20 hours)
- Week 2: Phase 4 complete, 75% coverage target
- Weeks 3-4: Phase 5-6 complete, 90% coverage target
- Weeks 5-6: Phase 7 complete, 100% GOAL achieved

**Key Success Factor:**
Focus on high-ROI tasks first (quick wins, new features) before tackling complex environment issues.

---

**Last Updated:** November 3, 2025
**Next Action:** Fix lazy_utils and search_engine test failures (30 minutes)
