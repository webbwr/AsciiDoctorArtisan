# Phase 4 - Next Session Quick Start

**Last Session:** 2025-11-17 (4 hours, highly productive)
**Status:** Ready to continue
**Documentation:** PHASE4_SESSION_2025-11-17.md, HANGING_TESTS.md

---

## Quick Start Commands

```bash
# Start with file_operations_manager (recommended)
pytest tests/unit/ui/test_file_operations_manager.py \
  --cov=asciidoc_artisan.ui.file_operations_manager \
  --cov-report=term-missing -v

# Current coverage: 90% (22 missed lines)
# Lines to cover: 107, 433, 542-545, 577-583, 601, 666-671, 675, 696, 700, 704, 708, 710, 716, 720, 722
```

---

## Priority Files (High → Medium → Low)

### High Priority (Good ROI)
1. **file_operations_manager.py** - 90% (22 lines)
   - 44 existing tests, 932 line test file
   - Good test infrastructure
   - File format detection, error paths uncovered
   - **Recommended starting point** ⭐

2. **chat_manager.py** - 95% (22 lines)
   - 89 existing tests, 1,530 line test file
   - Complex fixture setup (mock_chat_bar, mock_chat_panel, mock_settings)
   - Error handlers and validation paths uncovered
   - Save for when you have more time

### Medium Priority
3. **status_manager.py** - 84% (39 lines)
   - Status bar and message handling
   - Moderate complexity

### Low Priority (Deferred)
4. **dialog_manager.py** - 58% (hangs in full suite)
5. **main_window.py** - 69% (hangs in full suite)

---

## Established Patterns

### Test Class Naming
```python
@pytest.mark.unit
class TestModuleCoverageEdgeCases:
    """Additional tests to achieve 99-100% coverage for module."""

    def test_specific_uncovered_line(self, fixture_name):
        """Test description (line X)."""
        # Test implementation
```

### Common Coverage Gaps
1. **TYPE_CHECKING imports** - Always uncovered (expected)
2. **Exception handlers** - Need explicit tests
3. **Atomic save failures** - Test with `return_value=False`
4. **File format detection** - Test extension logic
5. **Qt threading code** - Maximum achievable <100%

### Testing Strategy
1. Check existing fixtures before writing tests
2. Add tests incrementally
3. Run after each addition to verify
4. Focus on error paths and edge cases
5. Document Qt limitations as encountered

---

## Files Already at 99-100%

### This Session (Nov 17)
- export_manager.py - 99% (effectively 100%)
- worker_manager.py - 98%
- preview_handler_base.py - 98%

### Previous Sessions (Nov 14-16)
- installation_validator_dialog - 100%
- base_vcs_handler - 100%
- chat_bar_widget - 100%
- autocomplete_manager - 100%
- template_browser - 100%
- spell_check_manager - 100%
- syntax_checker_manager - 100%
- ui_state_manager - 100%
- theme_manager - 100%
- file_handler - 100%
- git_status_dialog - 100%
- editor_state - 100%
- git_handler - 100%

**Total:** 16 UI files at 98-100% coverage

---

## Known Issues

### Hanging Test Files (4 total)
- test_dialog_manager.py (101 tests)
- test_dialogs.py
- test_main_window.py
- test_undo_redo.py

**Cause:** Qt event loop cleanup issues
**Impact:** Minimal - tests work individually
**Workarounds:** See HANGING_TESTS.md
**Action:** Skip for now, can run individually if needed

---

## Quick Reference

### Run Single File Coverage
```bash
pytest tests/unit/ui/test_FILE.py \
  --cov=asciidoc_artisan.ui.FILE \
  --cov-report=term-missing \
  --no-cov-on-fail -v
```

### Check Uncovered Lines
```bash
# Will show: Name, Stmts, Miss, Cover, Missing
# Missing column shows line numbers
```

### Add Test Pattern
```python
def test_feature_edge_case(self, mock_editor, tmp_path):
    """Test feature with edge case (lines X-Y)."""
    from asciidoc_artisan.ui.module import Class

    manager = Class(mock_editor)

    with patch("module.function", return_value=False):
        result = manager.method()
        assert result is False
```

---

## Session Goals

**Minimum:** 1 file to 95%+ coverage
**Target:** 2 files to 98%+ coverage
**Stretch:** 3 files to 98%+ coverage

**Time Estimate:**
- file_operations_manager: 1-2 hours
- status_manager: 1-1.5 hours
- chat_manager: 2-3 hours (complex)

---

## Pre-Session Checklist

- [ ] Review PHASE4_SESSION_2025-11-17.md
- [ ] Check git status (should be clean)
- [ ] Review uncovered lines for target file
- [ ] Check existing test fixtures
- [ ] Plan 3-5 tests to add

---

## Post-Session Checklist

- [ ] Run tests to verify coverage improvement
- [ ] Commit with descriptive message
- [ ] Update phase-4c-coverage-plan.md
- [ ] Push to main
- [ ] Document any new patterns or issues

---

**Last Updated:** 2025-11-17
**Next File:** file_operations_manager.py (90% → target 98%+)
**Estimated Duration:** 1-2 hours
**Ready:** ✅ YES
