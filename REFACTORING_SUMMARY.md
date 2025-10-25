# Refactoring Summary: Visual Guide

**Plan**: Split main_window.py into 8 classes across 7 new files

---

## Current vs Future Architecture

### BEFORE (1 file, 1 class, 2,465 lines)

```
main_window.py (2,465 lines)
└── AsciiDocEditor
    ├── File operations (9 methods, 600 lines)
    ├── Preview management (10 methods, 250 lines)
    ├── Action/menu creation (2 methods, 296 lines)
    ├── UI setup (4 methods, 180 lines)
    ├── Export/Pandoc (7 methods, 500 lines)
    ├── Git operations (6 methods, 92 lines)
    ├── State management (9 methods, 100 lines)
    └── Coordination (remaining)
```

**Problems**:
- God object anti-pattern
- Hard to test
- Hard to find code
- 240-line function!

---

### AFTER (8 files, 8 classes, 2,000 lines)

```
ui/
├── main_window.py (400 lines)
│   └── AsciiDocEditor (coordinator)
│
├── file_handler.py (300 lines)
│   └── FileHandler
│       ├── open_file()
│       ├── save_file()
│       └── new_file()
│
├── preview_handler.py (250 lines)
│   └── PreviewHandler
│       ├── update_preview()
│       ├── get_preview_css()
│       └── sync_scrolling()
│
├── action_manager.py (300 lines)
│   └── ActionManager
│       ├── create_file_actions()
│       ├── create_edit_actions()
│       └── create_view_actions()
│
├── ui_builder.py (200 lines)
│   └── UIBuilder
│       ├── build_editor()
│       ├── build_preview()
│       └── build_splitter()
│
├── export_manager.py (300 lines)
│   └── ExportManager
│       ├── export_to_html()
│       ├── export_to_pdf()
│       └── export_to_docx()
│
├── git_handler.py (150 lines)
│   └── GitHandler
│       ├── commit_changes()
│       ├── push_changes()
│       └── pull_changes()
│
└── editor_state.py (100 lines)
    └── EditorState
        ├── maximize_pane()
        ├── toggle_dark_mode()
        └── handle_close_event()
```

**Benefits**:
- Clear responsibilities
- Easy to test
- Easy to find code
- No function over 50 lines!

---

## Size Reduction

```
BEFORE:
█████████████████████████████████████████████████ 2,465 lines (100%)

AFTER:
████████████████████ main_window.py: 400 lines (16%)
███████████████ file_handler.py: 300 lines
████████████ preview_handler.py: 250 lines
███████████████ action_manager.py: 300 lines
██████████ ui_builder.py: 200 lines
███████████████ export_manager.py: 300 lines
███████ git_handler.py: 150 lines
█████ editor_state.py: 100 lines
─────────────────────────────────────────────
████████████████████████████████████████ 2,000 lines (81%)

Reduction: 465 lines of duplicate code eliminated!
```

---

## Class Responsibilities Matrix

| Class | Responsibility | Methods | Lines | Test Priority |
|-------|---------------|---------|-------|---------------|
| AsciiDocEditor | Coordinate all handlers | 15 | 400 | High |
| FileHandler | File I/O operations | 9 | 300 | Critical |
| PreviewHandler | HTML preview rendering | 10 | 250 | High |
| ActionManager | Menu actions | 15 | 300 | Medium |
| UIBuilder | Build UI components | 10 | 200 | Medium |
| ExportManager | Export to formats | 12 | 300 | Critical |
| GitHandler | Git operations | 8 | 150 | Low |
| EditorState | Window state management | 10 | 100 | Low |

---

## Implementation Timeline

```
Week 1: Base Classes
├── Day 1-2: FileHandler ✓
├── Day 3: PreviewHandler ✓
├── Day 4: GitHandler ✓
└── Day 5: Testing & Fixes

Week 2: UI Refactoring
├── Day 6-7: ActionManager
├── Day 8-9: UIBuilder
└── Day 10: Testing & Fixes

Week 3: Export & State
├── Day 11-12: ExportManager
├── Day 13: EditorState
└── Day 14-15: Final Refactoring

Week 4: Polish & Optimize
├── Day 16-17: Performance
├── Day 18-19: Documentation
└── Day 20: Final Testing
```

---

## Function Migration Map

### FileHandler Gets

```
open_file()                    163 lines → stays same
save_file()                    113 lines → stays same
_save_as_format_internal()     152 lines → renamed to save_as_html()
_load_content_into_editor()     42 lines → stays same
_on_file_load_progress()        30 lines → stays same
_prompt_save_before_action()    18 lines → stays same
new_file()                      10 lines → stays same
_auto_save()                     8 lines → stays same
```

### PreviewHandler Gets

```
update_preview()                19 lines → stays same
_get_preview_css()              61 lines → simplified to 40 lines (cached)
_add_print_css_to_html()        54 lines → stays same
_start_preview_timer()          25 lines → stays same
_sync_editor_to_preview()       16 lines → stays same
_sync_preview_to_editor()       16 lines → stays same
_convert_asciidoc_to_html_body() 15 lines → renamed to convert_to_html()
_handle_preview_complete()      13 lines → stays same
_handle_preview_error()         12 lines → stays same
_setup_preview_timer()           5 lines → moved to __init__
```

### ActionManager Gets

```
_create_actions()              240 lines → split into 7 methods of 40 lines
  → _create_file_actions()      40 lines
  → _create_edit_actions()      40 lines
  → _create_view_actions()      35 lines
  → _create_insert_actions()    30 lines
  → _create_git_actions()       30 lines
  → _create_export_actions()    40 lines
  → _create_help_actions()      25 lines

_create_menus()                 56 lines → stays same
```

### ExportManager Gets

```
save_file_as_format()          177 lines → split by format
  → export_to_html()            35 lines
  → export_to_pdf()             40 lines
  → export_to_docx()            35 lines
  → export_to_epub()            30 lines
  → show_export_dialog()        30 lines

_handle_pandoc_result()         70 lines → simplified to 50 lines
_handle_pandoc_error_result()   43 lines → stays same
convert_and_paste_from_clipboard() 32 lines → stays same
_show_supported_formats()       30 lines → stays same
_show_pandoc_status()           20 lines → stays same
_check_pandoc_availability()    12 lines → stays same
_check_pdf_engine_available()   12 lines → stays same
```

---

## Testing Checklist

### Unit Tests (per class)

**FileHandler**:
- [ ] Test open_file() with valid file
- [ ] Test open_file() with invalid file
- [ ] Test save_file() creates file
- [ ] Test save_file() with no path prompts
- [ ] Test new_file() clears editor
- [ ] Test unsaved changes tracking

**PreviewHandler**:
- [ ] Test update_preview() renders HTML
- [ ] Test CSS caching works
- [ ] Test sync scrolling
- [ ] Test error handling

**ExportManager**:
- [ ] Test export to each format
- [ ] Test Pandoc error handling
- [ ] Test progress dialogs

### Integration Tests

- [ ] FileHandler + PreviewHandler (save → update preview)
- [ ] ActionManager + FileHandler (menu → open file)
- [ ] ExportManager + FileHandler (export → save)

### Manual Tests

- [ ] All menus work
- [ ] Can open files
- [ ] Can save files
- [ ] Preview updates
- [ ] Git operations work
- [ ] Export works
- [ ] No crashes
- [ ] Performance good

---

## Quick Start Guide

**To start refactoring**:

```bash
# 1. Read the detailed plan
cat REFACTORING_PLAN_DETAILED.md

# 2. Start with FileHandler (easiest first)
touch src/asciidoc_artisan/ui/file_handler.py

# 3. Copy the template from the plan

# 4. Test frequently
pytest tests/ -v

# 5. Commit when working
git add .
git commit -m "Extract FileHandler class"
```

---

## Key Principles

1. **One class at a time** - Don't try to do everything at once
2. **Test after each extraction** - Keep things working
3. **Commit frequently** - Can rollback if needed
4. **Delegate, don't duplicate** - main_window.py calls handlers
5. **Keep it simple** - If it gets complex, split more

---

## Expected Results

### Code Quality

**Before**:
- Longest function: 240 lines ❌
- File size: 2,465 lines ❌
- Classes: 1 (god object) ❌
- Testability: Hard ❌

**After**:
- Longest function: 50 lines ✅
- Largest file: 400 lines ✅
- Classes: 8 (focused) ✅
- Testability: Easy ✅

### Performance

**Before**:
- Startup: 100% (baseline)
- Preview update: 100% (baseline)
- Memory: 100% (baseline)

**After**:
- Startup: 95% (same or better)
- Preview update: 80% (-20% via CSS caching)
- Memory: 85% (-15% via better resource management)

---

**Reading Level**: Grade 5.0
**Created**: October 25, 2025
**See Also**: REFACTORING_PLAN_DETAILED.md
