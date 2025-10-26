---
**TECHNICAL DOCUMENT**
**Reading Level**: Grade 5.0 summary below | Full technical details follow
**Type**: Planning Document

## Simple Summary

This doc shows the plan for making the code better. It lists all tasks and when to do them.

---

## Full Technical Details

# Detailed Refactoring Plan: main_window.py

**Goal**: Split 2,465-line main_window.py into 8 focused classes across 7 new files
**Timeline**: 3-4 weeks
**Impact**: Better architecture, easier testing, faster performance

---

## Current State Analysis

**File**: `src/asciidoc_artisan/ui/main_window.py`
**Lines**: 2,465
**Methods**: 55 total (7 public, 48 private)
**Classes**: 1 (AsciiDocEditor - god object)

### Problem Areas

**🔴 Critical (4 functions over 100 lines)**:
- `_create_actions()` - 240 lines
- `save_file_as_format()` - 177 lines
- `open_file()` - 163 lines
- `_save_as_format_internal()` - 152 lines
- `_setup_ui()` - 124 lines
- `save_file()` - 113 lines

**🟡 Warning (6 functions 50-100 lines)**:
- `__init__()` - 87 lines
- `_show_ai_setup_help()` - 78 lines
- `_handle_pandoc_result()` - 70 lines
- `_get_preview_css()` - 61 lines
- `_create_menus()` - 56 lines
- `_add_print_css_to_html()` - 54 lines

---

## New Architecture Design

### File Structure

```
src/asciidoc_artisan/ui/
├── main_window.py           (400 lines - coordination only)
├── file_handler.py          (NEW - 300 lines)
├── preview_handler.py       (NEW - 250 lines)
├── action_manager.py        (NEW - 300 lines)
├── ui_builder.py            (NEW - 200 lines)
├── export_manager.py        (NEW - 300 lines)
├── git_handler.py           (NEW - 150 lines)
└── editor_state.py          (NEW - 100 lines)
```

**Total**: 2,000 lines across 8 files (vs 2,465 in 1 file)
**Reduction**: ~465 lines removed (duplicated code eliminated)

---

## Class Extraction Plan

### Class 1: FileHandler
**File**: `src/asciidoc_artisan/ui/file_handler.py`
**Purpose**: All file I/O operations
**Lines**: ~300

#### Responsibilities
- Open files (all formats)
- Save files (AsciiDoc, HTML)
- Load content into editor
- Manage file state
- Handle unsaved changes

#### Methods to Extract (9 methods, 600 lines → 300 lines)

**From main_window.py**:
```python
# Public methods
def open_file(self) -> None                          # 163 lines
def save_file(self, save_as: bool = False) -> bool   # 113 lines
def new_file(self) -> None                           # 10 lines

# Private methods
def _load_content_into_editor(content, path) -> None # 42 lines
def _on_file_load_progress(loaded, total) -> None    # 30 lines
def _prompt_save_before_action(action) -> bool       # 18 lines
def _auto_save(self) -> None                         # 8 lines
```

#### New FileHandler Class
```python
class FileHandler:
    """Handle all file operations."""

    def __init__(self, editor_widget, settings_manager):
        self.editor = editor_widget
        self.settings = settings_manager
        self.current_file_path: Optional[Path] = None
        self.unsaved_changes = False
        self.is_opening_file = False

    # Public API
    def open_file(self, file_path: Optional[str] = None) -> None
    def save_file(self, save_as: bool = False) -> bool
    def new_file(self) -> None
    def has_unsaved_changes(self) -> bool
    def get_current_file_path(self) -> Optional[Path]

    # Private helpers
    def _load_content_into_editor(self, content: str, path: Path) -> None
    def _prompt_save_before_action(self, action: str) -> bool
    def _auto_save(self) -> None
    def _validate_file_path(self, path: Path) -> bool
```

#### Benefits
- All file logic in one place
- Easy to test file operations
- Clear responsibility
- Reduces main_window.py by 600 lines

---

### Class 2: PreviewHandler
**File**: `src/asciidoc_artisan/ui/preview_handler.py`
**Purpose**: Manage HTML preview rendering
**Lines**: ~250

#### Responsibilities
- Update preview from editor text
- Generate preview CSS
- Handle preview rendering
- Manage preview timer
- Sync scrolling between editor/preview

#### Methods to Extract (10 methods, 250 lines)

**From main_window.py**:
```python
# Public methods
def update_preview(self) -> None                     # 19 lines

# Private methods
def _get_preview_css(self) -> str                    # 61 lines
def _add_print_css_to_html(html) -> str              # 54 lines
def _start_preview_timer(self) -> None               # 25 lines
def _sync_editor_to_preview(value) -> None           # 16 lines
def _sync_preview_to_editor(value) -> None           # 16 lines
def _convert_asciidoc_to_html_body(text) -> str      # 15 lines
def _handle_preview_complete(html) -> None           # 13 lines
def _handle_preview_error(error) -> None             # 12 lines
def _setup_preview_timer(self) -> QTimer             # 5 lines
```

#### New PreviewHandler Class
```python
class PreviewHandler:
    """Handle preview rendering and synchronization."""

    def __init__(self, editor_widget, preview_widget, asciidoc_api):
        self.editor = editor_widget
        self.preview = preview_widget
        self.asciidoc_api = asciidoc_api
        self.preview_timer = QTimer()
        self.sync_enabled = True
        self._css_cache: Optional[str] = None

    # Public API
    def update_preview(self) -> None
    def enable_sync_scrolling(self, enabled: bool) -> None
    def clear_preview(self) -> None
    def get_preview_html(self) -> str

    # Private helpers
    def _get_preview_css(self) -> str
    def _add_print_css_to_html(self, html: str) -> str
    def _convert_asciidoc_to_html(self, text: str) -> str
    def _handle_preview_complete(self, html: str) -> None
    def _sync_editor_to_preview(self, value: int) -> None
```

#### Benefits
- Preview logic isolated
- CSS can be cached
- Easy to optimize rendering
- Reduces main_window.py by 250 lines

---

### Class 3: ActionManager
**File**: `src/asciidoc_artisan/ui/action_manager.py`
**Purpose**: Create and manage all menu actions
**Lines**: ~300

#### Responsibilities
- Create all QAction objects
- Organize actions by category
- Connect actions to handlers
- Provide action access to menus

#### Methods to Extract (2 methods, 296 lines → 300 lines split)

**From main_window.py**:
```python
def _create_actions(self) -> None                    # 240 lines
def _create_menus(self) -> None                      # 56 lines
```

#### New ActionManager Class
```python
class ActionManager:
    """Manage all application actions."""

    def __init__(self, main_window):
        self.window = main_window
        self.actions = {}

    # Public API
    def create_all_actions(self) -> None
    def get_action(self, name: str) -> QAction
    def enable_action(self, name: str, enabled: bool) -> None

    # Action creation (split from 240-line monster)
    def _create_file_actions(self) -> Dict[str, QAction]
    def _create_edit_actions(self) -> Dict[str, QAction]
    def _create_view_actions(self) -> Dict[str, QAction]
    def _create_insert_actions(self) -> Dict[str, QAction]
    def _create_git_actions(self) -> Dict[str, QAction]
    def _create_export_actions(self) -> Dict[str, QAction]
    def _create_help_actions(self) -> Dict[str, QAction]

    # Helper methods
    def _create_action(self, name, text, shortcut, handler, **kwargs) -> QAction
```

#### Split Strategy for _create_actions()

**Original** (240 lines):
```python
def _create_actions(self):
    # File actions (40 lines)
    # Edit actions (40 lines)
    # View actions (35 lines)
    # Insert actions (30 lines)
    # Git actions (30 lines)
    # Export actions (40 lines)
    # Help actions (25 lines)
```

**After Split** (7 methods of ~40 lines each):
```python
def create_all_actions(self):
    """Create all actions (coordination only)."""
    self.actions.update(self._create_file_actions())
    self.actions.update(self._create_edit_actions())
    self.actions.update(self._create_view_actions())
    self.actions.update(self._create_insert_actions())
    self.actions.update(self._create_git_actions())
    self.actions.update(self._create_export_actions())
    self.actions.update(self._create_help_actions())

def _create_file_actions(self) -> Dict[str, QAction]:
    """Create File menu actions."""
    return {
        'new': self._create_action('new', '&New', 'Ctrl+N', self.window.new_file),
        'open': self._create_action('open', '&Open', 'Ctrl+O', self.window.open_file),
        # ... more file actions
    }
```

#### Benefits
- 240-line function becomes 7 functions of 40 lines
- Each category isolated
- Easy to add new actions
- Clear organization

---

### Class 4: UIBuilder
**File**: `src/asciidoc_artisan/ui/ui_builder.py`
**Purpose**: Build UI components
**Lines**: ~200

#### Responsibilities
- Create editor widget
- Create preview widget
- Create splitter layout
- Setup toolbars
- Build status bar

#### Methods to Extract (4 methods, 180 lines)

**From main_window.py**:
```python
def _setup_ui(self) -> None                          # 124 lines
def _setup_dynamic_sizing(self) -> None              # 20 lines
def _setup_synchronized_scrolling(self) -> None      # 7 lines
def _initialize_asciidoc(self) -> Optional[AsciiDoc3API]  # 18 lines
```

#### New UIBuilder Class
```python
class UIBuilder:
    """Build user interface components."""

    def __init__(self, main_window):
        self.window = main_window

    # Public API
    def build_main_ui(self) -> None
    def build_editor(self) -> QPlainTextEdit
    def build_preview(self) -> QWebEngineView
    def build_splitter(self, editor, preview) -> QSplitter
    def build_toolbars(self) -> None
    def build_status_bar(self) -> QStatusBar

    # Private helpers
    def _setup_dynamic_sizing(self) -> None
    def _setup_synchronized_scrolling(self) -> None
    def _create_editor_toolbar(self) -> QWidget
    def _create_preview_toolbar(self) -> QWidget
```

#### Split Strategy for _setup_ui()

**Original** (124 lines):
```python
def _setup_ui(self):
    # Window setup (10 lines)
    # Editor creation (40 lines)
    # Preview creation (40 lines)
    # Splitter setup (20 lines)
    # Toolbar creation (14 lines)
```

**After Split** (5 methods of ~25 lines each):
```python
def build_main_ui(self):
    """Build complete UI (coordination)."""
    editor = self.build_editor()
    preview = self.build_preview()
    splitter = self.build_splitter(editor, preview)
    self.build_toolbars()
    self.window.setCentralWidget(splitter)

def build_editor(self) -> QPlainTextEdit:
    """Build editor widget."""
    # 25 lines of editor setup

def build_preview(self) -> QWebEngineView:
    """Build preview widget."""
    # 25 lines of preview setup
```

#### Benefits
- UI creation separated from logic
- Each widget isolated
- Easy to modify layout
- Reduces main_window.py by 180 lines

---

### Class 5: ExportManager
**File**: `src/asciidoc_artisan/ui/export_manager.py`
**Purpose**: Handle file export/conversion
**Lines**: ~300

#### Responsibilities
- Export to different formats (HTML, PDF, DOCX)
- Handle Pandoc conversions
- Manage export dialogs
- Show export progress

#### Methods to Extract (7 methods, 500 lines → 300 lines)

**From main_window.py**:
```python
def save_file_as_format(self) -> None                # 177 lines
def _save_as_format_internal(...) -> bool            # 152 lines
def _handle_pandoc_result(...) -> None               # 70 lines
def _handle_pandoc_error_result(...) -> None         # 43 lines
def convert_and_paste_from_clipboard(self) -> None   # 32 lines
def _show_supported_formats(self) -> None            # 30 lines
def _show_pandoc_status(...) -> None                 # 20 lines
def _check_pandoc_availability(self) -> bool         # 12 lines
def _check_pdf_engine_available(self) -> bool        # 12 lines
```

#### New ExportManager Class
```python
class ExportManager:
    """Manage file exports and conversions."""

    def __init__(self, main_window, pandoc_worker):
        self.window = main_window
        self.pandoc_worker = pandoc_worker
        self.export_in_progress = False

    # Public API
    def export_to_format(self, format_type: str) -> None
    def convert_and_paste_from_clipboard(self) -> None
    def show_supported_formats(self) -> None
    def is_pandoc_available(self) -> bool

    # Private helpers
    def _export_to_html(self, file_path: Path) -> bool
    def _export_to_pdf(self, file_path: Path) -> bool
    def _export_to_docx(self, file_path: Path) -> bool
    def _handle_pandoc_result(self, result) -> None
    def _handle_pandoc_error(self, error) -> None
    def _show_export_progress(self, format_type: str) -> None
```

#### Split Strategy for save_file_as_format()

**Original** (177 lines):
```python
def save_file_as_format(self):
    # Get format dialog (30 lines)
    # Validate format (20 lines)
    # AsciiDoc export (25 lines)
    # HTML export (30 lines)
    # PDF export (40 lines)
    # DOCX export (32 lines)
```

**After Split** (5 methods of ~35 lines each):
```python
def export_to_format(self, format_type: str):
    """Export to format (coordination)."""
    if format_type == 'html':
        return self._export_to_html()
    elif format_type == 'pdf':
        return self._export_to_pdf()
    # ...

def _export_to_html(self, file_path: Path) -> bool:
    """Export to HTML format."""
    # 35 lines of HTML export logic

def _export_to_pdf(self, file_path: Path) -> bool:
    """Export to PDF format."""
    # 35 lines of PDF export logic
```

#### Benefits
- Export logic centralized
- Each format isolated
- Easy to add new formats
- Reduces main_window.py by 500 lines

---

### Class 6: GitHandler
**File**: `src/asciidoc_artisan/ui/git_handler.py`
**Purpose**: Handle Git operations
**Lines**: ~150

#### Responsibilities
- Select Git repository
- Trigger Git commands (commit, push, pull)
- Handle Git results
- Show Git status

#### Methods to Extract (6 methods, 92 lines)

**From main_window.py**:
```python
def _select_git_repository(self) -> Optional[Path]  # 21 lines
def _trigger_git_commit(self) -> None                # 21 lines
def _handle_git_result(self, result) -> None         # 21 lines
def _ensure_git_ready(self) -> bool                  # 11 lines
def _trigger_git_pull(self) -> None                  # 9 lines
def _trigger_git_push(self) -> None                  # 9 lines
```

#### New GitHandler Class
```python
class GitHandler:
    """Handle Git version control operations."""

    def __init__(self, main_window, git_worker):
        self.window = main_window
        self.git_worker = git_worker
        self.current_repo: Optional[Path] = None

    # Public API
    def select_repository(self) -> Optional[Path]
    def commit_changes(self) -> None
    def push_changes(self) -> None
    def pull_changes(self) -> None
    def get_repository_status(self) -> str

    # Private helpers
    def _ensure_git_ready(self) -> bool
    def _handle_git_result(self, result) -> None
    def _handle_git_error(self, error) -> None
```

#### Benefits
- Git operations isolated
- Easy to mock for testing
- Clear Git-related API
- Reduces main_window.py by 92 lines

---

### Class 7: EditorState
**File**: `src/asciidoc_artisan/ui/editor_state.py`
**Purpose**: Manage editor UI state
**Lines**: ~100

#### Responsibilities
- Track window state (maximized panes)
- Update UI enabled/disabled states
- Handle window events (close, resize)
- Manage zoom level

#### Methods to Extract (9 methods, 100 lines)

**From main_window.py**:
```python
def closeEvent(self, event) -> None                  # 30 lines
def _maximize_pane(self, pane) -> None               # 29 lines
def _restore_panes(self) -> None                     # 24 lines
def _update_ui_state(self) -> None                   # 19 lines
def _update_window_title(self) -> None               # 10 lines
def _toggle_pane_maximize(self, pane) -> None        # 10 lines
def _toggle_sync_scrolling(self) -> None             # 5 lines
def _toggle_dark_mode(self) -> None                  # 3 lines
def _zoom(self, delta) -> None                       # 5 lines
```

#### New EditorState Class
```python
class EditorState:
    """Manage editor window state."""

    def __init__(self, main_window):
        self.window = main_window
        self.pane_states = {
            'editor_maximized': False,
            'preview_maximized': False,
            'sync_scrolling': True,
            'dark_mode': False
        }
        self.zoom_level = 0

    # Public API
    def maximize_pane(self, pane: str) -> None
    def restore_panes(self) -> None
    def toggle_pane(self, pane: str) -> None
    def toggle_sync_scrolling(self) -> None
    def toggle_dark_mode(self) -> None
    def zoom_in(self) -> None
    def zoom_out(self) -> None
    def update_ui_enabled_state(self) -> None
    def handle_close_event(self, event: QCloseEvent) -> None

    # Private helpers
    def _save_window_state(self) -> None
    def _restore_window_state(self) -> None
```

#### Benefits
- State management separated
- UI state testable
- Clear state transitions
- Reduces main_window.py by 100 lines

---

### Class 8: AsciiDocEditor (Refactored)
**File**: `src/asciidoc_artisan/ui/main_window.py`
**Purpose**: Coordinate all other classes
**Lines**: ~400 (down from 2,465!)

#### New Responsibilities
- Initialize all handler classes
- Coordinate between handlers
- Provide public API
- Handle Qt signals/slots

#### New Structure
```python
class AsciiDocEditor(QMainWindow):
    """Main application window (coordinator)."""

    # Signals
    request_git_command = Signal(list, str)
    request_pandoc_conversion = Signal(object, str, str, str, object, bool)
    request_preview_render = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        # Initialize managers (already exist)
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager()
        self.status_manager = StatusManager()
        self.menu_manager = MenuManager()

        # Initialize new handlers
        self.ui_builder = UIBuilder(self)
        self.file_handler = FileHandler(self.editor, self.settings_manager)
        self.preview_handler = PreviewHandler(self.editor, self.preview, self._asciidoc_api)
        self.action_manager = ActionManager(self)
        self.export_manager = ExportManager(self, self.pandoc_worker)
        self.git_handler = GitHandler(self, self.git_worker)
        self.editor_state = EditorState(self)

        # Build UI
        self.ui_builder.build_main_ui()
        self.action_manager.create_all_actions()
        self.menu_manager.create_menus(self.action_manager.actions)

        # Apply settings
        self.theme_manager.apply_theme()
        self.editor_state.restore_window_state()

    # Public API (delegate to handlers)
    def new_file(self) -> None:
        """Create new file."""
        self.file_handler.new_file()

    def open_file(self) -> None:
        """Open file."""
        self.file_handler.open_file()

    def save_file(self, save_as: bool = False) -> bool:
        """Save file."""
        return self.file_handler.save_file(save_as)

    def save_file_as_format(self) -> None:
        """Export to format."""
        self.export_manager.export_to_format()

    def update_preview(self) -> None:
        """Update preview."""
        self.preview_handler.update_preview()

    # Event handlers
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close."""
        self.editor_state.handle_close_event(event)
```

#### Benefits
- Simple coordination logic
- Delegates to specialists
- 83% size reduction (2,465 → 400 lines!)
- Much easier to understand

---

## Implementation Strategy

### Phase 1: Create Base Classes (Week 1)

#### Day 1-2: FileHandler
1. Create `file_handler.py`
2. Copy file-related methods
3. Adapt to work standalone
4. Add unit tests
5. Update main_window.py to use FileHandler

#### Day 3: PreviewHandler
1. Create `preview_handler.py`
2. Copy preview methods
3. Add CSS caching
4. Add unit tests
5. Update main_window.py to use PreviewHandler

#### Day 4: GitHandler
1. Create `git_handler.py`
2. Copy Git methods
3. Add unit tests
4. Update main_window.py to use GitHandler

#### Day 5: Testing & Bug Fixes
1. Run full test suite
2. Manual testing
3. Fix integration issues
4. Commit Phase 1

**Phase 1 Result**: 3 new classes, 942 lines extracted

---

### Phase 2: UI Refactoring (Week 2)

#### Day 6-7: ActionManager
1. Create `action_manager.py`
2. Split `_create_actions()` into 7 methods
3. Refactor `_create_menus()` to use ActionManager
4. Add tests
5. Update main_window.py

#### Day 8-9: UIBuilder
1. Create `ui_builder.py`
2. Split `_setup_ui()` into 5 methods
3. Extract toolbar creation
4. Add tests
5. Update main_window.py

#### Day 10: Testing & Bug Fixes
1. Test all UI interactions
2. Test menu actions
3. Fix issues
4. Commit Phase 2

**Phase 2 Result**: 2 new classes, 500 lines extracted

---

### Phase 3: Export & State (Week 3)

#### Day 11-12: ExportManager
1. Create `export_manager.py`
2. Split `save_file_as_format()` by format type
3. Extract Pandoc handlers
4. Add tests
5. Update main_window.py

#### Day 13: EditorState
1. Create `editor_state.py`
2. Extract state management
3. Add state tests
4. Update main_window.py

#### Day 14-15: Final Refactoring
1. Clean up main_window.py
2. Remove duplicate code
3. Add docstrings
4. Full testing
5. Commit Phase 3

**Phase 3 Result**: 2 new classes, 600 lines extracted

---

### Phase 4: Polish & Optimize (Week 4)

#### Day 16-17: Performance Optimization
1. Add caching where appropriate
2. Optimize preview updates
3. Profile and benchmark
4. Fix bottlenecks

#### Day 18-19: Documentation
1. Update CLAUDE.md
2. Update README.md
3. Add class diagrams
4. Write migration guide

#### Day 20: Final Testing
1. Full regression testing
2. Performance testing
3. User acceptance testing
4. Final commit and release

---

## Detailed Migration Steps

### Step-by-Step: FileHandler Extraction

**Step 1**: Create new file
```bash
touch src/asciidoc_artisan/ui/file_handler.py
```

**Step 2**: Add imports and class skeleton
```python
# file_handler.py
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QPlainTextEdit, QFileDialog, QMessageBox
from asciidoc_artisan.core import atomic_save_text, SUPPORTED_OPEN_FILTER

class FileHandler:
    """Handle file operations."""

    def __init__(self, editor: QPlainTextEdit, settings_manager):
        self.editor = editor
        self.settings = settings_manager
        self.current_file_path: Optional[Path] = None
        self.unsaved_changes = False
```

**Step 3**: Copy open_file() method
```python
def open_file(self, file_path: Optional[str] = None) -> None:
    """Open a file."""
    # Copy entire open_file() method from main_window.py
    # Change self.editor references to use self.editor
    # Change self._current_file_path to self.current_file_path
    # Change self._unsaved_changes to self.unsaved_changes
```

**Step 4**: Update main_window.py
```python
# main_window.py
from asciidoc_artisan.ui.file_handler import FileHandler

class AsciiDocEditor(QMainWindow):
    def __init__(self):
        # ... existing code ...
        self.file_handler = FileHandler(self.editor, self._settings_manager)

    def open_file(self) -> None:
        """Delegate to file handler."""
        self.file_handler.open_file()
```

**Step 5**: Test
```bash
pytest tests/test_file_operations.py -v
python src/main.py  # Manual test
```

**Step 6**: Repeat for all file methods

**Step 7**: Remove old methods from main_window.py

---

## Testing Strategy

### Unit Tests

**For each new class**:
```python
# tests/test_file_handler.py
def test_open_file_success():
    handler = FileHandler(mock_editor, mock_settings)
    handler.open_file('/path/to/test.adoc')
    assert handler.current_file_path == Path('/path/to/test.adoc')

def test_save_file_creates_backup():
    handler = FileHandler(mock_editor, mock_settings)
    result = handler.save_file()
    assert result == True
    assert backup_file_exists()
```

### Integration Tests

```python
# tests/test_integration.py
def test_file_handler_preview_handler_integration():
    """Test that saving file updates preview."""
    file_handler = FileHandler(editor, settings)
    preview_handler = PreviewHandler(editor, preview, api)

    file_handler.save_file()
    preview_handler.update_preview()

    assert preview_has_content()
```

### Manual Test Checklist

- [ ] Open file works
- [ ] Save file works
- [ ] Preview updates
- [ ] Git operations work
- [ ] Export to all formats works
- [ ] All menus clickable
- [ ] No crashes
- [ ] Performance same or better

---

## Risk Mitigation

### Risks

1. **Breaking existing functionality**
   - Mitigation: Test after each extraction
   - Mitigation: Keep old code until verified

2. **Performance regression**
   - Mitigation: Benchmark before/after
   - Mitigation: Profile to find issues

3. **Integration bugs**
   - Mitigation: Integration tests
   - Mitigation: Manual testing

4. **Too much time**
   - Mitigation: Do one class at a time
   - Mitigation: Can stop after any phase

### Rollback Strategy

Each phase is committed separately:
- Can rollback to previous phase
- Can cherry-pick successful parts
- Can pause and resume later

---

## Success Metrics

### Code Quality
- [ ] No function over 50 lines
- [ ] main_window.py under 500 lines
- [ ] 7 new focused classes
- [ ] 90%+ test coverage

### Performance
- [ ] Startup time same or faster
- [ ] Preview updates 20% faster (CSS caching)
- [ ] Memory usage 15% lower
- [ ] No UI lag

### Maintainability
- [ ] Each class has single responsibility
- [ ] Easy to find code
- [ ] New developers understand structure
- [ ] Can modify one area without breaking others

---

## File Size Comparison

### Before
```
main_window.py:  2,465 lines (100%)
```

### After
```
main_window.py:    400 lines (16%)
file_handler.py:   300 lines
preview_handler.py: 250 lines
action_manager.py:  300 lines
ui_builder.py:      200 lines
export_manager.py:  300 lines
git_handler.py:     150 lines
editor_state.py:    100 lines
─────────────────────────────
Total:           2,000 lines (81%)
```

**Savings**: 465 lines removed (duplicate code eliminated)

---

## Next Actions

**Start with**: FileHandler extraction (Day 1)

**Command**:
```bash
# Create new file
touch src/asciidoc_artisan/ui/file_handler.py

# Start coding!
code src/asciidoc_artisan/ui/file_handler.py
```

---

**Reading Level**: Grade 5.0
**Created**: October 25, 2025
**Status**: Ready to execute
**Estimated Time**: 3-4 weeks (2 hours/day)
