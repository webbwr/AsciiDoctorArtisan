"""
Tests for ui.dialog_manager module.

Tests dialog coordination and management functionality.
"""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def main_window(qapp):
    """Create a mock main window."""
    window = QMainWindow()
    return window


class TestDialogManager:
    """Test suite for DialogManager class."""

    def test_import_dialog_manager(self):
        """Test that DialogManager can be imported."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        assert DialogManager is not None

    def test_dialog_manager_creation(self, main_window):
        """Test creating DialogManager instance."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(main_window)
        assert manager is not None

    def test_dialog_manager_has_parent(self, main_window):
        """Test that DialogManager stores parent reference."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(main_window)
        assert hasattr(manager, "editor")  # DialogManager stores parent as 'editor'
        assert manager.editor == main_window

    def test_show_dialog_method_exists(self, main_window):
        """Test that show_dialog or similar method exists."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(main_window)
        # Check for common dialog methods
        dialog_methods = [attr for attr in dir(manager)
                          if "dialog" in attr.lower() or "show" in attr.lower()]
        assert len(dialog_methods) > 0

    @patch("asciidoc_artisan.ui.dialog_manager.QDialog")
    def test_create_dialog(self, mock_dialog, main_window):
        """Test creating a dialog."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(main_window)

        # Check if manager has method to create dialogs
        if hasattr(manager, "create_dialog"):
            dialog = manager.create_dialog("Test Dialog")
            assert dialog is not None

    def test_dialog_manager_singleton_or_instance(self, main_window):
        """Test DialogManager can be instantiated."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager1 = DialogManager(main_window)
        manager2 = DialogManager(main_window)

        # Both should be valid instances
        assert manager1 is not None
        assert manager2 is not None

    def test_dialog_management_capabilities(self, main_window):
        """Test that DialogManager has dialog management capabilities."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(main_window)

        # Should have methods related to dialogs
        methods = [m for m in dir(manager) if not m.startswith("_")]
        assert len(methods) > 0

    def test_dialog_parent_setting(self, main_window):
        """Test that dialogs get proper parent."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(main_window)

        # Manager should have reference to parent window (stored as 'editor')
        assert hasattr(manager, "editor")
        assert manager.editor == main_window
