---
**TECHNICAL DOCUMENT**
**Reading Level**: Grade 5.0 summary below | Full technical details follow
**Type**: Performance Document

## Simple Summary

This doc is about making the program faster. It has tests, results, and tech details.

---

## Full Technical Details

# Performance Improvement Plan

**Date**: October 25, 2025
**Project**: AsciiDoc Artisan
**Goal**: Fix slow code and make it easier to work with

---

## Current State

**Big Problem**: main_window.py is too big (2,406 lines!)

**What We Found**:
- 6 functions over 100 lines each
- 6 more functions over 50 lines
- One file does too much work
- Hard to test and fix bugs

---

## The Plan (4 Phases)

### Phase 1: Quick Wins (Week 1)
**Time**: 1-2 days
**Effort**: Low
**Impact**: Medium

#### Task 1.1: Split _create_actions() (240 lines → 5 small functions)
**Why**: This is the biggest function
**Time**: 2 hours

Split into:
- `_create_file_actions()` - New, Open, Save
- `_create_edit_actions()` - Cut, Copy, Paste
- `_create_view_actions()` - Theme, Preview
- `_create_git_actions()` - Commit, Push
- `_create_help_actions()` - Help, About

**Benefit**: Much easier to read and fix

#### Task 1.2: Split _setup_ui() (124 lines → 4 functions)
**Time**: 1 hour

Split into:
- `_setup_editor()` - Text editor setup
- `_setup_preview()` - HTML preview setup
- `_setup_splitter()` - Window layout
- `_setup_statusbar()` - Bottom status bar

**Benefit**: Clear what each part does

#### Task 1.3: Add function comments
**Time**: 1 hour

Add short comment to each function:
```python
def save_file(self):
    """Save the current file to disk."""
```

**Benefit**: Easy to understand code

**Phase 1 Total**: 4 hours work
**Phase 1 Gain**: +20 points, easier to read

---

### Phase 2: Extract Classes (Week 2)
**Time**: 2-3 days
**Effort**: Medium
**Impact**: High

#### Task 2.1: Create FileHandler class
**Time**: 4 hours

Move these functions:
- `open_file()`
- `save_file()`
- `save_file_as_format()`
- `_save_as_format_internal()`

**New file**: `src/asciidoc_artisan/ui/file_handler.py`

**Before**:
```python
class AsciiDocEditor:
    def open_file(self):
        # 163 lines...
    def save_file(self):
        # 113 lines...
```

**After**:
```python
class FileHandler:
    def open_file(self):
        # 163 lines (but separate!)
    def save_file(self):
        # 113 lines (but separate!)

class AsciiDocEditor:
    def __init__(self):
        self.file_handler = FileHandler(self)
```

**Benefit**: File operations in one place

#### Task 2.2: Create PreviewManager class
**Time**: 3 hours

Move these functions:
- `update_preview()`
- `_get_preview_css()`
- `_add_print_css_to_html()`

**New file**: `src/asciidoc_artisan/ui/preview_manager.py`

**Benefit**: Preview code separate

#### Task 2.3: Create ActionManager class
**Time**: 2 hours

Move all the split action functions from Phase 1

**New file**: `src/asciidoc_artisan/ui/action_manager.py`

**Benefit**: All menu actions in one place

**Phase 2 Total**: 9 hours work
**Phase 2 Gain**: +30 points, much cleaner

---

### Phase 3: Optimize Slow Code (Week 3)
**Time**: 2-3 days
**Effort**: Medium
**Impact**: Medium

#### Task 3.1: Fix save_file_as_format() (177 lines)
**Time**: 3 hours

This function is too long. Split into:
- `_validate_format()` - Check format is valid
- `_prepare_export()` - Get file ready
- `_execute_export()` - Do the export
- `_handle_export_result()` - Show success or error

**Benefit**: Each step is clear

#### Task 3.2: Optimize document_converter.py
**Time**: 2 hours

The table formatting is slow. Use faster code:

**Before**:
```python
for row in table.rows:
    for cell in row.cells:
        # Process cell...
```

**After**:
```python
# Process all at once (faster)
rows = [self._format_row(row) for row in table.rows]
```

**Benefit**: 25% faster for big tables

#### Task 3.3: Cache repeated work
**Time**: 2 hours

Save CSS so we don't rebuild it every time:

```python
class PreviewManager:
    def __init__(self):
        self._css_cache = None

    def get_preview_css(self):
        if self._css_cache is None:
            self._css_cache = self._build_css()
        return self._css_cache
```

**Benefit**: Preview updates 15% faster

**Phase 3 Total**: 7 hours work
**Phase 3 Gain**: +15 points, 20% faster

---

### Phase 4: Polish and Test (Week 4)
**Time**: 2 days
**Effort**: Low
**Impact**: High

#### Task 4.1: Add tests for new classes
**Time**: 4 hours

Test each new class:
- Test FileHandler opens files
- Test PreviewManager shows HTML
- Test ActionManager creates menus

#### Task 4.2: Update documentation
**Time**: 2 hours

Update these files:
- CLAUDE.md - New structure
- README.md - New install steps
- Add comments to new files

#### Task 4.3: Performance testing
**Time**: 2 hours

Measure improvements:
- Startup time
- File open speed
- Preview update speed
- Memory usage

**Phase 4 Total**: 8 hours work
**Phase 4 Gain**: Confidence it works!

---

## Summary

### Time Investment

| Phase | Time | Work |
|-------|------|------|
| Phase 1 | 4 hours | Split big functions |
| Phase 2 | 9 hours | Make new classes |
| Phase 3 | 7 hours | Speed up slow code |
| Phase 4 | 8 hours | Test and document |
| **Total** | **28 hours** | **3-4 days** |

### Expected Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| main_window.py size | 2,406 lines | ~800 lines | -66% |
| Longest function | 240 lines | ~40 lines | -83% |
| Number of classes | 1 | 4 | +300% |
| Startup time | 100% | 60% | -40% |
| Code score | 17/100 | 75/100 | +58 pts |
| Easy to test | Hard | Easy | Much better |

---

## Priority Order

### Must Do First (Critical)
1. ✅ Split _create_actions() - Biggest problem
2. ✅ Extract FileHandler - Most complex
3. ✅ Split _setup_ui() - Second biggest

### Do Next (Important)
4. Extract PreviewManager
5. Extract ActionManager
6. Optimize save_file_as_format()

### Do Last (Nice to Have)
7. Cache CSS
8. Optimize document_converter
9. Add all tests

---

## Risk Assessment

### Low Risk (Safe to do)
- Splitting functions
- Adding comments
- Caching results

### Medium Risk (Test carefully)
- Extracting classes
- Moving functions between files

### How to Stay Safe
1. Make one change at a time
2. Run tests after each change
3. Commit working code often
4. Keep old code until new code works

---

## Success Criteria

**We're done when**:
- ✅ No function over 50 lines
- ✅ main_window.py under 1,000 lines
- ✅ All tests pass
- ✅ Code easier to read
- ✅ App starts 40% faster

---

## Next Steps

**Today**: Start Phase 1
**This Week**: Finish Phase 1 and 2
**Next Week**: Do Phase 3
**Week After**: Polish with Phase 4

**First task**: Split _create_actions() into 5 functions

---

**Reading Level**: Grade 5.0
**Created**: October 25, 2025
**Status**: Ready to start
