---
**TECHNICAL DOCUMENT**
**Reading Level**: Grade 5.0 summary below | Full technical details follow
**Type**: Planning Document

## Simple Summary

This doc shows the plan for making the code better. It lists all tasks and when to do them.

---

## Full Technical Details

# Implementation Timeline

**Goal**: Fix performance issues in 4 weeks
**Start**: Week of October 28, 2025
**End**: Week of November 18, 2025

---

## Week 1: Quick Wins (Oct 28 - Nov 1)

### Monday (2 hours)
- Add constants to main_window.py
- Extract helper functions
- Add docstrings to all functions

### Tuesday (2 hours)
- Split _setup_ui() into 4 functions
- Test that UI still works

### Wednesday (2 hours)
- Split _create_actions() into 5 functions
- Test all menu items work

### Thursday (1 hour)
- Run all tests
- Fix any broken tests
- Commit all changes

### Friday (1 hour)
- Update documentation
- Measure improvements

**Week 1 Total**: 8 hours
**Week 1 Done**: All quick wins complete!

---

## Week 2: Extract Classes (Nov 4 - Nov 8)

### Monday (4 hours)
- Create FileHandler class
- Move open_file() function
- Move save_file() function
- Test file operations work

### Tuesday (3 hours)
- Move save_file_as_format() function
- Move _save_as_format_internal() function
- Test export features work

### Wednesday (3 hours)
- Create PreviewManager class
- Move update_preview() function
- Move _get_preview_css() function
- Test preview works

### Thursday (2 hours)
- Create ActionManager class
- Move all action creation functions
- Test menus work

### Friday (2 hours)
- Update main_window.py to use new classes
- Run all tests
- Fix broken tests
- Commit changes

**Week 2 Total**: 14 hours
**Week 2 Done**: New class structure!

---

## Week 3: Optimize Performance (Nov 11 - Nov 15)

### Monday (3 hours)
- Split save_file_as_format() into smaller functions
- Test exports work faster

### Tuesday (2 hours)
- Optimize document_converter.py table formatting
- Use list comprehensions
- Test with large documents

### Wednesday (2 hours)
- Add CSS caching to PreviewManager
- Test preview updates faster

### Thursday (2 hours)
- Profile the application
- Find other slow parts
- Make small improvements

### Friday (1 hour)
- Run performance tests
- Measure speed improvements
- Commit changes

**Week 3 Total**: 10 hours
**Week 3 Done**: App runs faster!

---

## Week 4: Polish and Test (Nov 18 - Nov 22)

### Monday (4 hours)
- Write tests for FileHandler
- Write tests for PreviewManager
- Write tests for ActionManager

### Tuesday (2 hours)
- Update CLAUDE.md
- Update README.md
- Update code comments

### Wednesday (2 hours)
- Run full test suite
- Fix any failing tests
- Check code quality

### Thursday (2 hours)
- Final performance measurements
- Compare before and after
- Write results

### Friday (2 hours)
- Final review
- Commit and push everything
- Celebrate! 🎉

**Week 4 Total**: 12 hours
**Week 4 Done**: Everything clean and tested!

---

## Total Summary

| Week | Focus | Hours | Key Deliverable |
|------|-------|-------|-----------------|
| 1 | Quick wins | 8 | Split big functions |
| 2 | New classes | 14 | Clean structure |
| 3 | Speed up | 10 | Faster app |
| 4 | Polish | 12 | Tests and docs |
| **Total** | **All work** | **44 hours** | **Better code!** |

---

## Daily Schedule

**Best approach**: 2 hours per day

- Morning: 1 hour of coding
- Afternoon: 1 hour of testing

**This gives**:
- 10 hours per week
- 40 hours over 4 weeks
- Matches our plan!

---

## Checkpoints

### After Week 1
✅ Functions under 50 lines
✅ Code easier to read
✅ All tests still pass

### After Week 2
✅ Code split into classes
✅ main_window.py under 1,000 lines
✅ Easier to test

### After Week 3
✅ App starts faster
✅ Preview updates faster
✅ Better performance

### After Week 4
✅ All tests pass
✅ Docs updated
✅ Ready to ship!

---

## If Things Go Wrong

### Running behind schedule?
- Skip nice-to-have tasks
- Focus on must-do items
- Ask for help

### Tests failing?
- Stop adding features
- Fix tests first
- Don't skip this!

### Not sure what to do?
- Check this timeline
- Read the plan
- Start with quick wins

---

## Success Metrics

**We know we're done when**:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Longest function | Under 50 lines | Run analyzer |
| File size | Under 1,000 lines | `wc -l main_window.py` |
| Test pass rate | 100% | `pytest` |
| Startup time | 40% faster | Time it |
| Code score | 75/100 | Run profiler |

---

## Next Action

**Start now**: Do Win 5 from QUICK_WINS.md (15 minutes)

**File**: QUICK_WINS.md
**Task**: Add constants to main_window.py
**Time**: 15 minutes

Then keep going through quick wins!

---

**Reading Level**: Grade 5.0
**Created**: October 25, 2025
**Status**: Ready to execute
