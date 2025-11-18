# Archived Test Investigations (Nov 16-17, 2025)

**Archive Date:** 2025-11-18
**Reason:** Superseded by comprehensive TEST_ISSUES_SUMMARY.md
**Status:** Historical reference only

---

## Archived Files

### Investigation Documents (Nov 16, 2025)

1. **gpu-test-failures-analysis.md** (11K)
   - GPU/WebEngine test failures analysis
   - 3 tests marked for skip/investigation
   - **Superseded by:** TEST_ISSUES_SUMMARY.md (covers all skipped tests)

2. **skipped-test-analysis.md** (6.6K)
   - Analysis of 2 skipped tests
   - Investigation complete
   - **Superseded by:** TEST_ISSUES_SUMMARY.md (comprehensive skip analysis)

3. **test-issues-log.md** (16K)
   - Hung tests and failures tracking log
   - Phase 4C/4E coverage session notes
   - **Superseded by:** HANGING_TESTS.md + TEST_ISSUES_SUMMARY.md

4. **ui-test-failures-analysis.md** (7.8K)
   - UI test failures from Nov 16 run
   - 62 failed, 2850 passed, 7 skipped
   - **Superseded by:** All failures resolved, TEST_ISSUES_SUMMARY.md

5. **ui-test-fixes-summary.md** (12K)
   - Priority 2 test logic bugs
   - 11/24 fixed (46% complete)
   - **Superseded by:** All tests now passing (204/204)

6. **assertion-failures-analysis.md** (Added Nov 18, 2025)
   - Analysis of assertion failures in dialog tests
   - Mock/parent initialization issues
   - **Superseded by:** All tests fixed, MockParentWidget pattern documented

7. **dialog-init-failures-analysis.md** (Added Nov 18, 2025)
   - Dialog initialization failure investigation
   - PySide6 C++ parent validation issues
   - **Superseded by:** MockParentWidget pattern in conftest.py

8. **mock-assertion-analysis.md** (Added Nov 18, 2025)
   - Mock assertion failures in dialog tests
   - MagicMock compatibility with Qt C++ layer
   - **Superseded by:** Real QWidget fixtures with trackable methods

### Session Documentation (Nov 17, 2025)

9. **PHASE4_SESSION_2025-11-17.md** (9.5K)
   - Phase 4 coverage improvement session summary
   - 4-hour session, 3 files improved to 98-99%
   - Documents hanging test investigation
   - **Status:** Historical record of completed work

10. **PHASE4_NEXT_SESSION.md** (4.6K)
    - Quick start guide for next coverage session
    - File priorities and uncovered line numbers
    - **Outdated:** Mentions file_operations_manager at 90% (now 98%)
    - **Superseded by:** Work completed, no longer applicable

---

## Current Documentation

See `docs/developer/TESTING_README.md` for current test documentation index.

**Active References:**
- `docs/developer/TEST_ISSUES_SUMMARY.md` - Comprehensive test health report
- `docs/developer/HANGING_TESTS.md` - Hanging test analysis
- `docs/developer/test-coverage.md` - Coverage guide
- `docs/developer/phase-4c-coverage-plan.md` - Coverage planning

---

## Why Archived

**Consolidation:** All test issue investigations consolidated into TEST_ISSUES_SUMMARY.md

**Resolution:** Issues documented in archived files have been resolved:
- All test failures fixed (204/204 passing)
- All skipped tests analyzed and documented
- Hanging tests fully investigated with workarounds
- Coverage improvements completed

**Redundancy:** Information duplicated in multiple files, now centralized

**Staleness:** Session notes and next-step guides outdated by completed work

---

## Historical Value

These files provide:
- Investigation methodology reference
- Historical context for test improvements (Nov 16-17, 2025)
- Coverage improvement session patterns
- Problem-solving approaches for similar future issues

---

**Archived:** 2025-11-18
**By:** Test documentation consolidation
**Superseded By:** docs/developer/TEST_ISSUES_SUMMARY.md + HANGING_TESTS.md
