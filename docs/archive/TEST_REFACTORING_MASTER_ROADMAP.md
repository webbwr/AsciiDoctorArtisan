# Test Suite Refactoring - Master Roadmap

**Project:** AsciiDoc Artisan v1.7.1+
**Created:** November 2, 2025
**Status:** Ready for execution
**Total Estimated Time:** 18-27 hours

---

## Executive Summary

Comprehensive test suite refactoring to streamline and optimize 1,294 tests across 92 files while maintaining 100% code coverage.

**Current State:**
- 1,294 tests across 92 test files
- Significant duplication (21 duplicate fixtures, 1 duplicate file)
- Limited use of parametrization (only 2 files)
- Scattered test organization

**Target State:**
- 1,044-1,124 tests across 73-80 files
- Zero duplication
- Parametrized test patterns throughout
- Consolidated, well-organized structure
- 100% coverage maintained

**Impact:**
- **Test reduction:** 170-250 tests (13-19% reduction)
- **File reduction:** 8-19 files (9-21% reduction)
- **Code reduction:** ~2,000-2,500 lines
- **Maintenance savings:** 30-40% less ongoing work

---

## Four-Phase Approach

### Phase 1: Quick Wins (ZERO risk)
**Time:** 2-3 hours
**Status:** ✅ PLAN COMPLETE
**Document:** `TEST_REFACTORING_PHASE1_PLAN.md`

**Objectives:**
- Remove 21 duplicate `qapp` fixtures
- Delete 1 duplicate test file
- Move common fixtures to conftest.py

**Impact:**
- Test reduction: ~30-40 tests
- Files modified: 21
- Files deleted: 1
- Risk: ZERO (obvious duplication only)

**Key Tasks:**
1. Remove duplicate qapp fixtures from 21 files
2. Delete test_line_number_area.py (duplicate)
3. (Optional) Add pytest_plugins to conftest.py

---

### Phase 2: Parametrization (LOW risk)
**Time:** 4-6 hours
**Status:** ✅ PLAN COMPLETE
**Document:** `TEST_REFACTORING_PHASE2_PLAN.md`

**Objectives:**
- Convert 8 test groups to use `@pytest.mark.parametrize`
- Teach better testing patterns
- Reduce duplicate test logic

**Impact:**
- Test reduction: ~20-30 tests
- Files modified: 8-10
- Risk: LOW (parametrization is safe, well-tested pattern)

**Target Groups:**
1. GPU detection tests (boolean variations)
2. Git result status tests (success/error states)
3. Action enable/disable tests (state variations)
4. Format conversion tests (multiple formats)
5. Context mode tests (4 modes)
6. Model selection tests (multiple models)
7. File extension tests (multiple types)
8. Error handling tests (multiple error types)

---

### Phase 3: Consolidation (MEDIUM risk)
**Time:** 8-12 hours
**Status:** ✅ PLAN COMPLETE
**Document:** `TEST_REFACTORING_PHASE3_PLAN.md`

**Objectives:**
- Merge related test files
- Eliminate redundant test cases
- Improve test organization

**Impact:**
- Test reduction: ~110-160 tests
- Files deleted: 7-11
- Risk: MEDIUM (requires careful test migration)

**Consolidation Groups:**

1. **GPU/Hardware Detection** (HIGH impact)
   - 3 files → 1 file
   - 132 tests → 80-90 tests
   - Files: test_gpu_detection.py, test_hardware_detection.py, test_gpu_utils.py

2. **Async File Operations** (HIGH impact)
   - 4 files → 2 files
   - 115 tests → 85-95 tests
   - Files: test_async_*.py group

3. **Preview Handlers** (MEDIUM impact)
   - 3 files → 2 files
   - 36 tests → 28-32 tests
   - Files: test_preview_handler*.py group

4. **Chat System** (MEDIUM impact)
   - 7 files → 5 files
   - 149 tests → 120-130 tests
   - Files: test_chat_*.py group

---

### Phase 4: Optimization (LOW-MEDIUM risk)
**Time:** 4-6 hours
**Status:** ✅ PLAN COMPLETE
**Document:** `TEST_REFACTORING_PHASE4_PLAN.md`

**Objectives:**
- Strengthen weak tests (scaffolded tests)
- Remove truly unused tests
- Optimize slow-running tests
- Improve test quality

**Impact:**
- Test reduction: ~10-20 tests
- Test speed: 10-20% faster
- Risk: LOW-MEDIUM (quality improvements)

**Focus Areas:**
1. Scaffolded tests (0-1.1 assertions per test)
2. Weak assertions (assert x is not None only)
3. Slow tests (>1 second execution)
4. Redundant edge case tests
5. Unused mock-heavy tests

---

## Execution Strategy

### Recommended Sequence

**Week 1: Phase 1** (Quick wins, build confidence)
- Execute in single session (2-3 hours)
- Low risk, immediate value
- Validates refactoring approach

**Week 2: Phase 2** (Parametrization)
- Can be done incrementally (1-2 hours per group)
- Teaches team better testing patterns
- Low risk, builds on Phase 1

**Week 3-4: Phase 3** (Consolidation)
- Requires most careful planning
- Execute one consolidation group at a time
- Medium risk, highest impact

**Week 5: Phase 4** (Optimization)
- Polish and quality improvements
- Execute after Phase 3 to avoid rework
- Low-medium risk

### Alternative: Aggressive Schedule

Execute all phases in 1-2 weeks with dedicated time:
- Day 1-2: Phase 1 + Phase 2
- Day 3-5: Phase 3 (one group per day)
- Day 6: Phase 4
- Day 7: Final validation and documentation

---

## Success Metrics

### Required (Must-Have)
- ✅ All tests pass (100% pass rate)
- ✅ Code coverage remains at 100%
- ✅ No new warnings or errors
- ✅ Git history preserved (meaningful commits)

### Desired (Should-Have)
- ✅ Test execution time ≤ current (ideally 10-20% faster)
- ✅ Peak memory usage ≤ current
- ✅ Test count reduced by 13-19%
- ✅ File count reduced by 9-21%

### Aspirational (Nice-to-Have)
- ✅ Test execution time 20%+ faster
- ✅ Improved test readability
- ✅ Better test organization
- ✅ Documentation of testing patterns

---

## Risk Management

### Phase 1 (ZERO risk)
- **Mitigation:** Simple git rollback
- **Validation:** Run full test suite
- **Backup:** None needed (changes are trivial)

### Phase 2 (LOW risk)
- **Mitigation:** Parametrize one group at a time
- **Validation:** Run affected tests after each group
- **Backup:** Git branch for each group

### Phase 3 (MEDIUM risk)
- **Mitigation:** Create backup branch, merge one group at a time
- **Validation:** Run full suite after each consolidation
- **Backup:** Keep original files in archive until all phases complete

### Phase 4 (LOW-MEDIUM risk)
- **Mitigation:** Create backup branch, optimize incrementally
- **Validation:** Performance benchmarks before/after
- **Backup:** Git branch for performance comparison

---

## Validation Process

### Before Each Phase
```bash
# Capture baseline
source venv/bin/activate
pytest tests/ -v --tb=short > /tmp/tests_before_phase_N.txt 2>&1
echo $? > /tmp/exit_code_before_phase_N.txt

# Capture coverage
pytest tests/ --cov=src --cov-report=term > /tmp/coverage_before_phase_N.txt 2>&1
```

### After Each Phase
```bash
# Run full test suite
pytest tests/ -v --tb=short > /tmp/tests_after_phase_N.txt 2>&1
echo $? > /tmp/exit_code_after_phase_N.txt

# Check coverage
pytest tests/ --cov=src --cov-report=term > /tmp/coverage_after_phase_N.txt 2>&1

# Compare results
diff /tmp/tests_before_phase_N.txt /tmp/tests_after_phase_N.txt
diff /tmp/coverage_before_phase_N.txt /tmp/coverage_after_phase_N.txt
```

### After All Phases
```bash
# Final validation
make test  # Run with all quality checks
make lint  # Ensure code quality maintained

# Performance comparison
pytest tests/performance/ -v

# Generate final report
pytest tests/ --cov=src --cov-report=html
# Review htmlcov/index.html for 100% coverage
```

---

## Rollback Procedures

### Individual Phase Rollback
```bash
# Rollback Phase N changes
git log --oneline | grep "Phase N"  # Find commit hash
git revert <commit-hash>

# Or hard reset (if not pushed)
git reset --hard <commit-before-phase-N>
```

### Complete Rollback
```bash
# Nuclear option - revert all refactoring
git log --oneline | grep "TEST_REFACTORING"  # Find all commits
git revert <commit-hash-1> <commit-hash-2> ...

# Or restore from tag
git checkout v1.7.1
git checkout -b refactoring-rollback
```

---

## Documentation Plan

### During Execution
- Commit message for each phase completion
- Update this roadmap with actual results
- Note any deviations from plan

### After Completion
- Create TEST_REFACTORING_COMPLETION_REPORT.md
- Update docs/developer/TEST_COVERAGE_SUMMARY.md
- Update CLAUDE.md with new test structure
- Update ROADMAP.md with refactoring milestone

---

## Phase Completion Checklist

### Phase 1: Quick Wins
- [ ] Remove 21 duplicate qapp fixtures
- [ ] Delete test_line_number_area.py
- [ ] (Optional) Add pytest_plugins to conftest.py
- [ ] Run full test suite
- [ ] Verify 100% coverage
- [ ] Commit with message template
- [ ] Push to origin/main

### Phase 2: Parametrization
- [ ] Parametrize 8 test groups
- [ ] Verify each parametrized group passes
- [ ] Update test documentation
- [ ] Run full test suite
- [ ] Verify 100% coverage
- [ ] Commit with message template
- [ ] Push to origin/main

### Phase 3: Consolidation
- [ ] Consolidate GPU/Hardware tests
- [ ] Consolidate Async file operations
- [ ] Consolidate Preview handlers
- [ ] Consolidate Chat system
- [ ] Run full test suite after each
- [ ] Verify 100% coverage
- [ ] Commit with message template
- [ ] Push to origin/main

### Phase 4: Optimization
- [ ] Strengthen scaffolded tests
- [ ] Remove truly unused tests
- [ ] Optimize slow tests
- [ ] Improve weak assertions
- [ ] Run performance benchmarks
- [ ] Verify 100% coverage
- [ ] Commit with message template
- [ ] Push to origin/main

### Final Tasks
- [ ] Create completion report
- [ ] Update all documentation
- [ ] Archive refactoring plans
- [ ] Close refactoring milestone

---

## Project Files

All refactoring plans are in `docs/archive/`:

1. **TEST_REFACTORING_PHASE1_PLAN.md** (5.1 KB) - Quick wins
2. **TEST_REFACTORING_PHASE2_PLAN.md** (21 KB) - Parametrization
3. **TEST_REFACTORING_PHASE3_PLAN.md** (24 KB) - Consolidation
4. **TEST_REFACTORING_PHASE4_PLAN.md** (24 KB) - Optimization
5. **TEST_REFACTORING_MASTER_ROADMAP.md** (this file) - Overview

Total planning documentation: **~80 KB, 2,500+ lines**

---

## Expected Final State

### Test Suite Statistics
- **Tests:** 1,044-1,124 (from 1,294)
- **Files:** 73-80 (from 92)
- **Coverage:** 100% (maintained)
- **Execution time:** 10-20% faster
- **Duplication:** ZERO

### Quality Improvements
- ✅ Parametrized test patterns throughout
- ✅ Consolidated, well-organized structure
- ✅ Strong assertions (no weak tests)
- ✅ Optimized slow tests
- ✅ Best practices documented

### Maintenance Benefits
- 30-40% less test code to maintain
- Easier to add new tests (clear patterns)
- Faster test execution (CI/CD benefits)
- Better test discovery (organized structure)
- Reduced risk of test rot

---

## Notes and Recommendations

1. **Execute phases in sequence** - Don't skip ahead, each builds on previous
2. **Validate after each phase** - Don't accumulate risk
3. **Keep backups** - Use git branches liberally
4. **Document deviations** - If plans need adjustment, note why
5. **Celebrate wins** - Phase 1 alone provides significant value

---

**Last Updated:** November 2, 2025
**Status:** ✅ All plans complete, ready for execution
**Next Step:** Execute Phase 1 (TEST_REFACTORING_PHASE1_PLAN.md)
