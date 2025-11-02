"""
Tests for ui.action_manager module.

Tests QAction creation and management functionality.
"""

import pytest
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction
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


class TestActionManager:
    """Test suite for ActionManager class."""

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

    def test_action_with_tooltip(self, main_window):
        """Test creating action with tooltip."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Help", lambda: None, tooltip="Show help")

        assert action.toolTip() == "Show help"

    def test_action_enabled_state(self, main_window):
        """Test that actions can be enabled/disabled."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, enabled=False)

        assert action.isEnabled() is False

        action.setEnabled(True)
        assert action.isEnabled() is True

    def test_action_checkable(self, main_window):
        """Test creating checkable action."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Toggle", lambda: None, checkable=True)

        assert action.isCheckable() is True

    def test_multiple_actions_creation(self, main_window):
        """Test creating multiple actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        action1 = manager.create_action("Action 1", lambda: None)
        action2 = manager.create_action("Action 2", lambda: None)
        action3 = manager.create_action("Action 3", lambda: None)

        assert action1 != action2 != action3
        assert all(isinstance(a, QAction) for a in [action1, action2, action3])

    def test_action_manager_stores_actions(self, main_window):
        """Test that ActionManager optionally stores created actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        # Create several actions
        for i in range(5):
            manager.create_action(f"Action {i}", lambda: None)

        # Check if manager has a way to retrieve actions
        if hasattr(manager, "actions") or hasattr(manager, "_actions"):
            actions = getattr(manager, "actions", getattr(manager, "_actions", []))
            assert len(actions) >= 5
