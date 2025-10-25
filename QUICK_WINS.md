# Quick Wins - Do Today!

These tasks take under 2 hours each. Big impact. Easy to do.

---

## Win 1: Split _create_actions() (2 hours)

**Problem**: One function with 240 lines
**Fix**: Make 5 small functions
**Benefit**: Much easier to read

### Steps

**Step 1**: Create _create_file_actions()
```python
def _create_file_actions(self) -> None:
    """Create File menu actions (New, Open, Save)."""
    # Move lines 449-490 here
```

**Step 2**: Create _create_edit_actions()
```python
def _create_edit_actions(self) -> None:
    """Create Edit menu actions (Cut, Copy, Paste)."""
    # Move lines 491-532 here
```

**Step 3**: Create _create_view_actions()
```python
def _create_view_actions(self) -> None:
    """Create View menu actions (Theme, Preview)."""
    # Move lines 533-574 here
```

**Step 4**: Create _create_git_actions()
```python
def _create_git_actions(self) -> None:
    """Create Git menu actions (Commit, Push)."""
    # Move lines 575-616 here
```

**Step 5**: Create _create_help_actions()
```python
def _create_help_actions(self) -> None:
    """Create Help menu actions (Help, About)."""
    # Move lines 617-688 here
```

**Step 6**: Update main function
```python
def _create_actions(self) -> None:
    """Create all menu actions."""
    self._create_file_actions()
    self._create_edit_actions()
    self._create_view_actions()
    self._create_git_actions()
    self._create_help_actions()
```

**Test**: Run the app. Check all menus work.

---

## Win 2: Split _setup_ui() (1 hour)

**Problem**: One function with 124 lines
**Fix**: Make 4 focused functions
**Benefit**: Clear what each part does

### Steps

**Step 1**: Create _setup_editor()
```python
def _setup_editor(self) -> QPlainTextEdit:
    """Set up the text editor."""
    # Move editor setup code here
    return editor
```

**Step 2**: Create _setup_preview()
```python
def _setup_preview(self) -> QWebEngineView:
    """Set up the HTML preview."""
    # Move preview setup code here
    return preview
```

**Step 3**: Create _setup_splitter()
```python
def _setup_splitter(self, editor, preview) -> QSplitter:
    """Set up the window layout."""
    # Move splitter code here
    return splitter
```

**Step 4**: Update main function
```python
def _setup_ui(self) -> None:
    """Set up the user interface."""
    editor = self._setup_editor()
    preview = self._setup_preview()
    splitter = self._setup_splitter(editor, preview)
    self.setCentralWidget(splitter)
```

**Test**: Open app. Check editor and preview show up.

---

## Win 3: Add docstrings (1 hour)

**Problem**: Hard to know what functions do
**Fix**: Add short comments
**Benefit**: Easy to understand

### Add to every function:

```python
def function_name(self) -> None:
    """One line saying what this does."""
```

### Examples:

```python
def save_file(self) -> bool:
    """Save the current file to disk."""

def open_file(self) -> None:
    """Open a file and load it into the editor."""

def update_preview(self) -> None:
    """Update the HTML preview with current text."""
```

**Count**: About 55 functions need comments

**Time**: 1 minute each = 1 hour total

---

## Win 4: Extract simple helpers (30 min)

**Problem**: Code repeated in many places
**Fix**: Make small helper functions
**Benefit**: Less code, fewer bugs

### Example 1: File path validation

**Before** (repeated 3 times):
```python
if file_path and Path(file_path).exists():
    # do something
```

**After** (helper function):
```python
def _is_valid_file(self, file_path: str) -> bool:
    """Check if file path exists."""
    return file_path and Path(file_path).exists()

# Use it:
if self._is_valid_file(file_path):
    # do something
```

### Example 2: Show error message

**Before** (repeated 5 times):
```python
QMessageBox.critical(self, "Error", error_message)
```

**After**:
```python
def _show_error(self, message: str) -> None:
    """Show error message to user."""
    QMessageBox.critical(self, "Error", message)

# Use it:
self._show_error("Could not save file")
```

---

## Win 5: Use constants (15 min)

**Problem**: Magic numbers and strings everywhere
**Fix**: Put them at the top
**Benefit**: Easy to change settings

### Add to top of file:

```python
# File settings
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_FAMILY = "Courier New"
MAX_RECENT_FILES = 10

# Preview settings
PREVIEW_UPDATE_DELAY = 500  # milliseconds
DEFAULT_THEME = "light"

# Window settings
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
```

### Use them:

**Before**:
```python
editor.setFont(QFont("Courier New", 12))
```

**After**:
```python
editor.setFont(QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE))
```

---

## Summary

| Win | Time | Benefit |
|-----|------|---------|
| Split _create_actions() | 2 hrs | +10 pts |
| Split _setup_ui() | 1 hr | +5 pts |
| Add docstrings | 1 hr | Much clearer |
| Extract helpers | 30 min | Less bugs |
| Use constants | 15 min | Easy changes |
| **Total** | **4.75 hrs** | **+15 pts** |

---

## Do Them In Order

1. ✅ Start with Win 5 (constants) - Easiest
2. ✅ Do Win 4 (helpers) - Quick
3. ✅ Do Win 3 (docstrings) - Simple
4. ✅ Do Win 2 (_setup_ui) - Medium
5. ✅ Do Win 1 (_create_actions) - Biggest win

**Total time**: Half a day
**Total gain**: Code much better!

---

**Reading Level**: Grade 5.0
**Status**: Ready to start
**First task**: Add constants (15 minutes)
