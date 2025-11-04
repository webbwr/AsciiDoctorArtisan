"""
Tests for ui.action_manager module.

Tests QAction creation and management functionality.
"""

import pytest
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction, QKeySequence
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def main_window(qapp):
    """Create a mock main window with required attributes."""
    window = QMainWindow()
    # Add required attributes that ActionManager expects
    window.editor = Mock()  # Text editor widget
    window._settings = Mock()  # Application settings
    window._sync_scrolling = False  # Scroll sync state
    return window


@pytest.mark.unit
class TestActionManagerBasics:
    """Test suite for ActionManager basic functionality."""

    def test_import_action_manager(self):
        """Test that ActionManager can be imported."""
        from asciidoc_artisan.ui.action_manager import ActionManager
        assert ActionManager is not None

    def test_action_manager_creation(self, main_window):
        """Test creating ActionManager instance."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert manager is not None

    def test_action_manager_has_parent(self, main_window):
        """Test that ActionManager stores parent reference."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert hasattr(manager, "window")
        assert manager.window == main_window

    def test_create_action_method_exists(self, main_window):
        """Test that create_action method exists."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert hasattr(manager, "create_action")
        assert callable(getattr(manager, "create_action"))

    def test_private_create_action_exists(self, main_window):
        """Test that _create_action private method exists."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert hasattr(manager, "_create_action")
        assert callable(getattr(manager, "_create_action"))


@pytest.mark.unit
class TestActionCreation:
    """Test suite for action creation functionality."""

    def test_create_action_returns_qaction(self, main_window):
        """Test that create_action returns QAction."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test Action", lambda: None)

        assert isinstance(action, QAction)
        assert action.text() == "Test Action"

    def test_action_with_shortcut(self, main_window):
        """Test creating action with keyboard shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Save", lambda: None, shortcut="Ctrl+S")

        assert action.shortcut().toString() == "Ctrl+S"

    def test_action_with_standard_key_shortcut(self, main_window):
        """Test creating action with StandardKey shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager._create_action(
            "New",
            "Create new file",
            lambda: None,
            shortcut=QKeySequence.StandardKey.New
        )

        # StandardKey.New is platform-specific (Ctrl+N or Cmd+N)
        shortcut_str = action.shortcut().toString()
        assert "N" in shortcut_str  # Should contain N key

    def test_action_with_icon(self, main_window):
        """Test creating action with icon."""
        from asciidoc_artisan.ui.action_manager import ActionManager
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QStyle

        manager = ActionManager(main_window)
        # Use a standard icon instead of null icon for testing
        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        action = manager.create_action("Open", lambda: None, icon=icon)

        assert not action.icon().isNull()

    def test_action_with_tooltip(self, main_window):
        """Test creating action with tooltip."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Help", lambda: None, tooltip="Show help")

        assert action.toolTip() == "Show help"
        assert action.statusTip() == "Show help"  # Tooltip used as status tip

    def test_action_without_tooltip_uses_text(self, main_window):
        """Test that action without tooltip uses text as status tip."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Save", lambda: None)

        assert action.statusTip() == "Save"


@pytest.mark.unit
class TestActionState:
    """Test suite for action state management."""

    def test_action_enabled_state(self, main_window):
        """Test that actions can be enabled/disabled."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, enabled=False)

        assert action.isEnabled() is False

        action.setEnabled(True)
        assert action.isEnabled() is True

    def test_action_default_enabled(self, main_window):
        """Test that actions are enabled by default."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None)

        assert action.isEnabled() is True

    def test_action_checkable(self, main_window):
        """Test creating checkable action."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Toggle", lambda: None, checkable=True)

        assert action.isCheckable() is True

    def test_action_checkable_with_initial_state(self, main_window):
        """Test checkable action with initial checked state."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Dark Mode", lambda: None, checkable=True, checked=True)

        assert action.isCheckable() is True
        assert action.isChecked() is True

    def test_action_check_state_change(self, main_window):
        """Test changing action check state."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Toggle", lambda: None, checkable=True)

        assert action.isChecked() is False
        action.setChecked(True)
        assert action.isChecked() is True
        action.setChecked(False)
        assert action.isChecked() is False


@pytest.mark.unit
class TestActionCallbacks:
    """Test suite for action callback connections."""

    def test_action_callback_connection(self, main_window):
        """Test that action callback is properly connected."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        callback_called = [False]

        def callback():
            callback_called[0] = True

        action = manager.create_action("Test", callback)
        action.trigger()

        assert callback_called[0] is True

    def test_action_callback_with_arguments(self, main_window):
        """Test action callback that expects arguments."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        callback_args = []

        def callback(checked):
            callback_args.append(checked)

        action = manager.create_action("Toggle", callback, checkable=True)
        action.trigger()  # Triggers with checked state

        assert len(callback_args) == 1
        assert isinstance(callback_args[0], bool)

    def test_multiple_action_triggers(self, main_window):
        """Test triggering action multiple times."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        counter = [0]

        def callback():
            counter[0] += 1

        action = manager.create_action("Increment", callback)

        action.trigger()
        action.trigger()
        action.trigger()

        assert counter[0] == 3


@pytest.mark.unit
class TestMultipleActions:
    """Test suite for managing multiple actions."""

    def test_multiple_actions_creation(self, main_window):
        """Test creating multiple actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        action1 = manager.create_action("Action 1", lambda: None)
        action2 = manager.create_action("Action 2", lambda: None)
        action3 = manager.create_action("Action 3", lambda: None)

        assert action1 != action2 != action3
        assert all(isinstance(a, QAction) for a in [action1, action2, action3])

    def test_actions_have_unique_text(self, main_window):
        """Test that each action has its own text."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        actions = [
            manager.create_action("New", lambda: None),
            manager.create_action("Open", lambda: None),
            manager.create_action("Save", lambda: None),
        ]

        texts = [action.text() for action in actions]
        assert texts == ["New", "Open", "Save"]

    def test_actions_have_independent_callbacks(self, main_window):
        """Test that actions have independent callbacks."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        results = []

        action1 = manager.create_action("A", lambda: results.append("A"))
        action2 = manager.create_action("B", lambda: results.append("B"))

        action1.trigger()
        action2.trigger()

        assert results == ["A", "B"]


@pytest.mark.unit
class TestActionMnemonics:
    """Test suite for action mnemonics (& in text)."""

    def test_action_with_mnemonic(self, main_window):
        """Test action with mnemonic (&N for Alt+N)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("&New", lambda: None)

        # Text includes &, which Qt uses for mnemonic
        assert "&New" in action.text() or "New" in action.text()

    def test_multiple_actions_with_mnemonics(self, main_window):
        """Test multiple actions with different mnemonics."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        actions = [
            manager.create_action("&File", lambda: None),
            manager.create_action("&Edit", lambda: None),
            manager.create_action("&View", lambda: None),
        ]

        assert all(isinstance(action, QAction) for action in actions)


@pytest.mark.unit
class TestActionEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_action_with_empty_text(self, main_window):
        """Test creating action with empty text."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("", lambda: None)

        assert action.text() == ""
        assert isinstance(action, QAction)

    def test_action_with_none_shortcut(self, main_window):
        """Test action with explicitly None shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, shortcut=None)

        assert action.shortcut().isEmpty()

    def test_action_with_none_icon(self, main_window):
        """Test action with None icon."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, icon=None)

        assert action.icon().isNull()

    def test_checkable_false_ignores_checked_parameter(self, main_window):
        """Test that non-checkable action ignores checked parameter."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, checkable=False, checked=True)

        assert action.isCheckable() is False
        # Non-checkable actions can't be checked
        assert action.isChecked() is False
