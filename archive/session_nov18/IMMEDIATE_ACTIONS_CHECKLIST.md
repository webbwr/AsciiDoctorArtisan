# Immediate Actions Checklist - v2.0.5 Planning

**Date:** November 18, 2025
**Status:** Ready for execution

---

## ✅ Session Complete - Documentation Ready

All session work complete. **1,785 lines** of documentation created across 6 files.

### Documentation Files (Ready to Review)
- ✅ `README_SESSION_NOV18.md` (223 lines) - **START HERE**
- ✅ `docs/v2.0.5_PLAN.md` (286 lines) - v2.0.5 roadmap
- ✅ `docs/testing/MAIN_WINDOW_COVERAGE_ANALYSIS.md` (242 lines) - Coverage findings
- ✅ `TESTING_SESSION_SUMMARY.md` (294 lines) - Async test investigation
- ✅ `SESSION_FINAL_SUMMARY.md` (409 lines) - Complete notes
- ✅ `WORK_SESSION_COMPLETE.md` (331 lines) - Work summary

---

## 🎯 DECISION REQUIRED: Coverage Target

### Critical Finding
**Original claim:** 84.8% coverage, need +0.2% → 85%
**Reality:** 74% coverage, need +11% → 85%
**Effort:** 24-37 hours (not 4-6 hours)

### Options

#### ⭐ Option A: 80% Target (RECOMMENDED)
- **Effort:** 8-12 hours
- **Timeline:** 1-2 weeks (v2.0.5)
- **Value:** High-value code paths, realistic goal
- **Why:** Achievable, excellent for UI code, avoids diminishing returns

#### Option B: Phased to 85%
- **Phase 4G.1 (v2.0.5):** 74% → 80% (8-12h)
- **Phase 4G.2 (v2.0.6):** 80% → 85% (12-18h)
- **Phase 4G.3 (v2.1.0):** 85%+ (10-15h)
- **Total:** 30-45 hours over 3 releases

#### Option C: Full 85% Push (NOT RECOMMENDED)
- **Effort:** 24-37 hours (single release)
- **Risk:** High - Qt limitations, diminishing returns
- **Value:** Low - last 5% provides minimal confidence gain

---

## 📋 Next Actions (After Decision)

### Step 1: Make Coverage Decision (5 minutes)
**Choose:** Option A (recommended), B, or C

**Record decision:**
```bash
# Edit this file and mark your choice:
echo "DECISION: Option A - 80% target" >> COVERAGE_DECISION.txt
```

### Step 2: Review Documentation (30-60 minutes)
Read in this order:
1. **README_SESSION_NOV18.md** - Executive summary (5 min)
2. **docs/v2.0.5_PLAN.md** - Release planning (10 min)
3. **docs/testing/MAIN_WINDOW_COVERAGE_ANALYSIS.md** - Coverage details (15 min)

### Step 3: Update ROADMAP (15 minutes)
If choosing Option A (80% target):
```bash
# Edit ROADMAP.md:
# - Update v2.0.5 coverage target from 85% to 80%
# - Revise effort estimate to 8-12 hours
# - Update Phase 4G description
```

### Step 4: Create v2.0.5 Branch (5 minutes)
```bash
git checkout -b v2.0.5-coverage-improvements
git add .
git commit -m "docs: Add Nov 18 testing session documentation

- Fixed 2 async integration tests
- Created 6 E2E workflow tests
- Identified coverage gap (74% vs 84.8%)
- Created v2.0.5 plan with 3 options
- Recommend 80% coverage target (Option A)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 🔨 Development Tasks (If Option A Chosen)

### Week 1: Main Window Coverage (8-12 hours)

#### Day 1-2: Identify & Plan (2-3 hours)
- [ ] Review coverage report: `open htmlcov/index.html`
- [ ] Navigate to `main_window.py` coverage
- [ ] Identify top 5 largest uncovered blocks:
  - [ ] Lines 1586-1651 (66 lines)
  - [ ] Lines 1506-1572 (67 lines)
  - [ ] Lines 514-549 (36 lines)
  - [ ] Lines 891-912 (22 lines)
  - [ ] Lines 830-840 (11 lines)
- [ ] For each block, determine:
  - Testable vs Qt limitation vs defensive code
  - Priority (user-facing vs internal)
  - Test complexity estimate

#### Day 3-5: Write Tests (6-9 hours)
- [ ] Write 8-15 new tests targeting:
  - [ ] High-value user workflows (~3-5 tests)
  - [ ] Error handling paths (~2-3 tests)
  - [ ] Edge cases (~3-7 tests)
- [ ] Run coverage after each batch:
  ```bash
  pytest tests/unit/ui/test_main_window*.py \
    --cov=asciidoc_artisan.ui.main_window \
    --cov-report=html \
    --cov-report=term-missing
  ```
- [ ] Target: Cover ~45 statements to reach 80%

#### Day 6: Verify & Document (1 hour)
- [ ] Final coverage check (should be ≥80%)
- [ ] Document any untestable lines with `# pragma: no cover`
- [ ] Update `docs/testing/MAIN_WINDOW_COVERAGE_ANALYSIS.md` with results

### Week 2: Qt Limitations Documentation (3-4 hours)

#### Create QT_THREADING_LIMITATIONS.md
- [ ] Inventory all Qt-limited tests (2 hours)
  ```bash
  grep -r "@pytest.mark.skip" tests/ | grep -i "qt\|thread\|event loop"
  ```
- [ ] Document each limitation (1-2 hours):
  - Technical explanation
  - Qt documentation links
  - Alternative testing approaches
  - Code examples
- [ ] File: `docs/testing/QT_THREADING_LIMITATIONS.md`

### Week 3: Defensive Code Audit (3-4 hours)

#### Create DEFENSIVE_CODE_AUDIT.md
- [ ] Review uncovered defensive code (2 hours)
- [ ] For each unreachable block, apply:
  - [ ] **Remove** if truly unreachable
  - [ ] **Document** if kept for safety (add `# pragma: no cover`)
  - [ ] **Refactor** if should be testable
- [ ] File: `docs/developer/DEFENSIVE_CODE_AUDIT.md`

### Week 3: E2E Stability (2-3 hours)

#### Fix Qt Segfaults
- [ ] Option 1: Use pytest-forked (1 hour)
  ```bash
  pip install pytest-forked
  # Add @pytest.mark.forked to E2E tests
  ```
- [ ] Option 2: Refactor fixture (2 hours)
  ```python
  # Reuse single QApplication across all E2E tests
  ```
- [ ] Run E2E suite: `pytest tests/e2e/ -v`
- [ ] Target: 6/6 tests passing

#### Optional: Add More Workflows (1-2 hours)
- [ ] Theme switching workflow
- [ ] Settings modification workflow
- [ ] All export formats sequentially

### Final: Release Prep (2 hours)

- [ ] Update ROADMAP.md with v2.0.5 entry
- [ ] Create CHANGELOG.md entry
- [ ] Run full test suite: `make test`
- [ ] Verify quality gates:
  - [ ] 99%+ test pass rate
  - [ ] 0 mypy errors
  - [ ] 100% type coverage
  - [ ] All pre-commit hooks passing

---

## 📊 Success Criteria (v2.0.5)

### Coverage
- [ ] main_window.py: ≥80% (currently 74%)
- [ ] Overall project: maintained at 91-92%

### Tests
- [ ] +8-15 new main_window tests
- [ ] 6/6 E2E tests passing (no segfaults)
- [ ] 99%+ test pass rate maintained
- [ ] 0 test failures

### Documentation
- [ ] `docs/testing/QT_THREADING_LIMITATIONS.md` complete
- [ ] `docs/developer/DEFENSIVE_CODE_AUDIT.md` complete
- [ ] ROADMAP.md updated
- [ ] CHANGELOG.md updated

### Quality
- [ ] 0 mypy errors (strict mode)
- [ ] 100% type coverage
- [ ] All pre-commit hooks passing
- [ ] No regressions

---

## 🎯 Quick Start (Today)

**5-Minute Action Plan:**

1. **Read:** `README_SESSION_NOV18.md` (5 min)
2. **Decide:** Choose coverage target (Option A recommended)
3. **Record:** Create `COVERAGE_DECISION.txt` with choice
4. **Commit:** Save session documentation to git
5. **Schedule:** Block time for Week 1 tasks

**Done!** You're ready to start v2.0.5 development.

---

## 📞 Questions?

Refer to comprehensive documentation:
- **Coverage details:** `docs/testing/MAIN_WINDOW_COVERAGE_ANALYSIS.md`
- **v2.0.5 plan:** `docs/v2.0.5_PLAN.md`
- **Complete notes:** `SESSION_FINAL_SUMMARY.md`

---

**Checklist created:** November 18, 2025
**Status:** Ready for execution
**Recommendation:** Option A (80% target)
**Total v2.0.5 effort:** 13-19 hours over 2-3 weeks
