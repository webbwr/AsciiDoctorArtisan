# Refactoring Plan: main_window.py

**Current Size:** 1,716 lines
**Target Size:** 300-400 lines
**Goal:** Extract 5-7 specialized manager classes
**Estimated Effort:** 12-16 hours

---

## Problem Statement

The `main_window.py` file (AsciiDocEditor class) has grown to 1,716 lines, making it:
- Hard to understand and navigate
- Prone to merge conflicts
- Difficult to test in isolation
- Challenging for new contributors

This violates the Single Responsibility Principle and makes maintenance harder.

---

## Proposed Architecture

### Current Structure
```
main_window.py (1,716 lines)
└── AsciiDocEditor
    ├── Initialization (~200 lines)
    ├── UI Setup (~300 lines)
    ├── Event Handlers (~400 lines)
    ├── File Operations (~200 lines)
    ├── Git Operations (~150 lines)
    ├── Export Operations (~150 lines)
    └── Helper Methods (~300 lines)
```

### Target Structure
```
main_window.py (300-400 lines) - Orchestration only
├── toolbar_manager.py (150-200 lines) - Toolbar setup
├── dock_manager.py (100-150 lines) - Dock widgets
├── keyboard_manager.py (100-150 lines) - Shortcuts
├── layout_manager.py (150-200 lines) - Window layout
├── window_state_manager.py (100-150 lines) - State persistence
└── connection_manager.py (100-150 lines) - Signal/slot connections
```

---

## Phase 1: Extract ToolbarManager

**Lines to Extract:** ~150-200
**Estimated Time:** 3-4 hours

### Responsibilities
- Create and configure toolbar
- Add toolbar actions
- Update toolbar state based on context
- Handle toolbar button clicks

### Methods to Move
```python
class ToolbarManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.toolbar = None

    def setup_toolbar(self):
        """Create and configure the main toolbar."""

    def add_toolbar_actions(self):
        """Add actions to toolbar."""

    def update_toolbar_state(self):
        """Update toolbar button states."""

    def _create_toolbar_button(self, action, icon_name):
        """Helper to create toolbar button."""
```

### Integration Pattern
```python
# In main_window.py
from .toolbar_manager import ToolbarManager

class AsciiDocEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toolbar_manager = ToolbarManager(self)
        self.toolbar_manager.setup_toolbar()
```

### Testing Strategy
- Unit tests for ToolbarManager in isolation
- Integration tests for toolbar functionality
- Manual UI testing

---

## Phase 2: Extract DockManager

**Lines to Extract:** ~100-150
**Estimated Time:** 2-3 hours

### Responsibilities
- Create and manage dock widgets
- Handle dock visibility
- Manage dock placement and sizing
- Persist dock state

### Methods to Move
```python
class DockManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.docks = {}

    def setup_docks(self):
        """Create and configure all dock widgets."""

    def create_dock(self, name, widget, area):
        """Create a new dock widget."""

    def toggle_dock_visibility(self, name):
        """Show/hide specific dock."""

    def save_dock_state(self):
        """Save dock positions and visibility."""

    def restore_dock_state(self):
        """Restore saved dock state."""
```

---

## Phase 3: Extract KeyboardManager

**Lines to Extract:** ~100-150
**Estimated Time:** 2-3 hours

### Responsibilities
- Register keyboard shortcuts
- Handle shortcut conflicts
- Provide shortcut documentation
- Allow shortcut customization

### Methods to Move
```python
class KeyboardManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.shortcuts = {}

    def setup_shortcuts(self):
        """Register all keyboard shortcuts."""

    def register_shortcut(self, key, action, description):
        """Register a keyboard shortcut."""

    def get_shortcuts_list(self):
        """Get list of all shortcuts for documentation."""

    def handle_key_press(self, event):
        """Handle custom key press events."""
```

---

## Phase 4: Extract LayoutManager

**Lines to Extract:** ~150-200
**Estimated Time:** 3-4 hours

### Responsibilities
- Manage window layout and splitters
- Handle resize events
- Provide layout presets (editor-only, preview-only, split)
- Persist layout state

### Methods to Move
```python
class LayoutManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.splitter = None

    def setup_layout(self):
        """Create and configure main layout."""

    def setup_splitter(self):
        """Create and configure splitter widget."""

    def set_layout_preset(self, preset_name):
        """Apply layout preset (editor-only, split, preview-only)."""

    def save_layout_state(self):
        """Save splitter positions and sizes."""

    def restore_layout_state(self):
        """Restore saved layout state."""
```

---

## Phase 5: Extract WindowStateManager

**Lines to Extract:** ~100-150
**Estimated Time:** 2-3 hours

### Responsibilities
- Save/restore window geometry
- Save/restore window state (maximized, etc.)
- Manage recent files list
- Persist user preferences

### Methods to Move
```python
class WindowStateManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = Settings()

    def save_window_state(self):
        """Save window geometry and state."""

    def restore_window_state(self):
        """Restore window geometry and state."""

    def add_recent_file(self, filepath):
        """Add file to recent files list."""

    def get_recent_files(self):
        """Get list of recent files."""
```

---

## Phase 6: Extract ConnectionManager

**Lines to Extract:** ~100-150
**Estimated Time:** 2-3 hours

### Responsibilities
- Connect signals to slots
- Manage signal/slot lifecycle
- Provide connection documentation
- Handle connection errors

### Methods to Move
```python
class ConnectionManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.connections = []

    def setup_connections(self):
        """Connect all signals to slots."""

    def connect_signal(self, signal, slot, description=""):
        """Connect a signal to a slot with tracking."""

    def disconnect_all(self):
        """Disconnect all tracked connections."""

    def get_connections_list(self):
        """Get list of all connections for debugging."""
```

---

## Remaining in main_window.py

After extraction, main_window.py should contain only:

1. **Initialization** (~50 lines)
   - Create managers
   - Initialize workers
   - Set up basic window properties

2. **Orchestration** (~100 lines)
   - Coordinate between managers
   - Handle high-level application logic
   - Manage application lifecycle

3. **Event Handlers** (~100 lines)
   - High-level event handling
   - Delegate to appropriate managers
   - Application-wide state changes

4. **Public API** (~50 lines)
   - Methods called by other modules
   - Main entry points
   - Public properties

**Total:** 300-400 lines

---

## Implementation Steps

### For Each Manager Extraction:

1. **Create New File**
   ```bash
   touch src/asciidoc_artisan/ui/{manager_name}.py
   ```

2. **Define Manager Class**
   - Create class skeleton
   - Define __init__ method
   - Document class purpose

3. **Move Methods**
   - Copy relevant methods from main_window.py
   - Update self references
   - Add proper type hints

4. **Update main_window.py**
   - Import new manager
   - Instantiate in __init__
   - Replace method calls with manager.method()

5. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

6. **Manual Testing**
   - Launch application
   - Test affected functionality
   - Check for regressions

7. **Commit Changes**
   ```bash
   git add .
   git commit -m "refactor: Extract {ManagerName} from main_window"
   ```

---

## Testing Strategy

### Unit Tests
- Test each manager in isolation
- Mock main_window dependencies
- Test error handling
- Test edge cases

### Integration Tests
- Test managers working together
- Test signal/slot connections
- Test state persistence
- Test UI interactions

### Manual Testing Checklist
- [ ] Application launches successfully
- [ ] All toolbar buttons work
- [ ] Keyboard shortcuts work
- [ ] Dock widgets work
- [ ] Window resize works
- [ ] Window state persists
- [ ] Layout presets work
- [ ] File operations work
- [ ] Git operations work
- [ ] Export operations work

---

## Risk Mitigation

### Risk 1: Breaking UI Functionality
**Mitigation:**
- Comprehensive testing after each extraction
- Keep changes small and incremental
- Use feature branch for all changes
- Have rollback plan (git revert)

### Risk 2: Performance Regression
**Mitigation:**
- Profile before/after each change
- Monitor startup time
- Check memory usage
- Run benchmark suite

### Risk 3: Merge Conflicts
**Mitigation:**
- Coordinate with team
- Work on feature branch
- Regular rebasing
- Clear communication

---

## Success Criteria

✅ **Phase Complete When:**
1. main_window.py is under 500 lines
2. All managers extracted successfully
3. All tests passing (360+/361)
4. No regressions in functionality
5. Documentation updated
6. Code reviewed and approved

✅ **Project Complete When:**
1. main_window.py is 300-400 lines
2. 6 manager classes created
3. Test coverage maintained or improved
4. No functional regressions
5. Performance maintained or improved
6. Documentation complete

---

## Timeline

| Phase | Task | Duration | Start | End |
|-------|------|----------|-------|-----|
| 1 | Extract ToolbarManager | 3-4 hours | Day 1 | Day 1 |
| 2 | Extract DockManager | 2-3 hours | Day 2 | Day 2 |
| 3 | Extract KeyboardManager | 2-3 hours | Day 3 | Day 3 |
| 4 | Extract LayoutManager | 3-4 hours | Day 4 | Day 4 |
| 5 | Extract WindowStateManager | 2-3 hours | Day 5 | Day 5 |
| 6 | Extract ConnectionManager | 2-3 hours | Day 6 | Day 6 |
| 7 | Testing & Polish | 2-3 hours | Day 7 | Day 7 |

**Total:** 16-23 hours over 7 days

---

## Next Actions

1. **Review this plan** with the team
2. **Create feature branch** `feature/refactor-main-window`
3. **Start with Phase 1** (ToolbarManager)
4. **Test thoroughly** after each phase
5. **Document lessons learned** along the way

---

**Status:** 📝 Ready to Start
**Priority:** HIGH
**Complexity:** MEDIUM-HIGH
**Impact:** HIGH (Improves maintainability significantly)

**Last Updated:** October 27, 2025
