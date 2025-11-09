"""Tests for ui.ui_setup_manager module."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QMainWindow, QSplitter, QStatusBar


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor with all required attributes for UISetupManager."""
    editor = QMainWindow()

    # Settings
    editor._settings = Mock()
    editor._settings.dark_mode = False
    editor._start_maximized = False
    editor._initial_geometry = None

    # Managers (need to exist but can be mocked)
    editor.status_manager = Mock()
    editor.status_manager.initialize_widgets = Mock()

    # Methods that will be called
    editor._setup_synchronized_scrolling = Mock()
    editor._start_preview_timer = Mock()
    editor._toggle_pane_maximize = Mock()
    editor._show_quick_commit = Mock()

    # Widgets that will be created by setup
    # (Don't pre-create them - let setup create them)

    return editor


@pytest.mark.unit
class TestUISetupManagerBasics:
    """Test suite for UISetupManager basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        assert UISetupManager is not None

    def test_creation(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)
        assert manager is not None

    def test_stores_editor_reference(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)
        assert manager.editor == mock_editor

    def test_has_setup_methods(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)
        assert hasattr(manager, "setup_ui")
        assert hasattr(manager, "setup_dynamic_sizing")
        assert callable(manager.setup_ui)
        assert callable(manager.setup_dynamic_sizing)

    def test_has_private_creation_methods(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)
        assert hasattr(manager, "_create_editor_pane")
        assert hasattr(manager, "_create_preview_pane")
        assert hasattr(manager, "_create_chat_pane")
        assert hasattr(manager, "_create_toolbar")
        assert callable(manager._create_editor_pane)
        assert callable(manager._create_preview_pane)


@pytest.mark.unit
class TestSetupUI:
    """Test suite for setup_ui method."""

    def test_sets_minimum_window_size(self, mock_editor):
        from asciidoc_artisan.core import MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager.setup_ui()

        # Should set minimum size
        assert mock_editor.minimumWidth() == MIN_WINDOW_WIDTH
        assert mock_editor.minimumHeight() == MIN_WINDOW_HEIGHT

    def test_creates_splitter(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager.setup_ui()

        # Should create horizontal splitter
        assert hasattr(mock_editor, "splitter")
        assert isinstance(mock_editor.splitter, QSplitter)
        assert mock_editor.splitter.orientation() == Qt.Orientation.Horizontal

    def test_creates_status_bar(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager.setup_ui()

        # Should create status bar
        assert hasattr(mock_editor, "status_bar")
        assert isinstance(mock_editor.status_bar, QStatusBar)

    def test_initializes_status_manager_widgets(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager.setup_ui()

        # Should call status manager initialization
        mock_editor.status_manager.initialize_widgets.assert_called_once()

    def test_calls_setup_dynamic_sizing(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        with patch.object(manager, "setup_dynamic_sizing") as mock_sizing:
            manager.setup_ui()
            mock_sizing.assert_called_once()

    def test_creates_find_bar(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager.setup_ui()

        # Should create find bar
        assert hasattr(mock_editor, "find_bar")

    def test_creates_quick_commit_widget(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager.setup_ui()

        # Should create quick commit widget
        assert hasattr(mock_editor, "quick_commit_widget")


@pytest.mark.unit
class TestEditorPaneCreation:
    """Test suite for _create_editor_pane method."""

    def test_creates_editor_widget(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        pane = manager._create_editor_pane()

        # Should create editor widget
        assert hasattr(mock_editor, "editor")
        assert pane is not None

    def test_creates_undo_redo_buttons(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_editor_pane()

        # Should create undo/redo buttons
        assert hasattr(mock_editor, "editor_undo_btn")
        assert hasattr(mock_editor, "editor_redo_btn")

    def test_creates_quick_commit_button(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_editor_pane()

        # Should create quick commit button
        assert hasattr(mock_editor, "quick_commit_btn")

    def test_connects_editor_text_changed(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_editor_pane()

        # Should connect textChanged signal
        # (Can't directly test signal connection, but editor is created)
        assert mock_editor.editor is not None


@pytest.mark.unit
class TestPreviewPaneCreation:
    """Test suite for _create_preview_pane method."""

    def test_creates_preview_widget(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        pane = manager._create_preview_pane()

        # Should create preview widget
        assert hasattr(mock_editor, "preview")
        assert pane is not None

    def test_sets_open_external_links(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # Keep reference to pane to prevent C++ object deletion
        pane = manager._create_preview_pane()

        # Should enable external links
        assert mock_editor.preview.openExternalLinks() is True
        # Keep pane alive for assertion
        assert pane is not None


@pytest.mark.unit
class TestChatPaneCreation:
    """Test suite for _create_chat_pane method."""

    def test_creates_chat_panel(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        pane = manager._create_chat_pane()

        # Should create chat panel
        assert hasattr(mock_editor, "chat_panel")
        assert pane is not None

    def test_creates_chat_bar(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_chat_pane()

        # Should create chat bar
        assert hasattr(mock_editor, "chat_bar")

    def test_stores_chat_container_reference(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_chat_pane()

        # Should store container reference
        assert hasattr(mock_editor, "chat_container")

    def test_chat_pane_initially_hidden(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_chat_pane()

        # Should be hidden by default
        assert mock_editor.chat_container.isVisible() is False

    def test_chat_pane_width_constraints(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_chat_pane()

        # Should have width constraints
        assert mock_editor.chat_container.minimumWidth() == 250
        assert mock_editor.chat_container.maximumWidth() == 600


@pytest.mark.unit
class TestToolbarCreation:
    """Test suite for _create_toolbar method."""

    def test_creates_toolbar_widget(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        toolbar = manager._create_toolbar(
            "Test", "#4ade80", "editor", "rgba(74, 222, 128, 0.2)"
        )

        # Should create toolbar widget
        assert toolbar is not None

    def test_toolbar_height(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        toolbar = manager._create_toolbar(
            "Test", "#4ade80", "editor", "rgba(74, 222, 128, 0.2)"
        )

        # Should have fixed height
        assert toolbar.height() == 30

    def test_stores_label_references(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_toolbar(
            "Editor", "#4ade80", "editor", "rgba(74, 222, 128, 0.2)"
        )

        # Should store label reference
        assert hasattr(mock_editor, "editor_label")

    def test_stores_max_button_references(self, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        manager._create_toolbar(
            "Preview", "#4a9eff", "preview", "rgba(74, 158, 255, 0.2)"
        )

        # Should store max button reference
        assert hasattr(mock_editor, "preview_max_btn")


@pytest.mark.unit
class TestSplitterSizes:
    """Test suite for _set_default_splitter_sizes method."""

    def test_sets_sizes_without_chat(self, mock_editor):
        from PySide6.QtWidgets import QWidget

        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # Create splitter with placeholder widgets
        mock_editor.splitter = QSplitter(Qt.Orientation.Horizontal)
        mock_editor.splitter.addWidget(QWidget())  # Editor
        mock_editor.splitter.addWidget(QWidget())  # Preview
        mock_editor.splitter.addWidget(QWidget())  # Chat
        mock_editor.chat_container = Mock()
        mock_editor.chat_container.isVisible = Mock(return_value=False)
        mock_editor.resize(1000, 600)

        manager._set_default_splitter_sizes()

        # Should set 50/50 split (without chat)
        sizes = mock_editor.splitter.sizes()
        assert len(sizes) == 3
        assert sizes[2] == 0  # Chat should be 0

    def test_sets_sizes_with_chat(self, mock_editor):
        from PySide6.QtWidgets import QWidget

        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # Create splitter with placeholder widgets
        mock_editor.splitter = QSplitter(Qt.Orientation.Horizontal)
        mock_editor.splitter.addWidget(QWidget())  # Editor
        mock_editor.splitter.addWidget(QWidget())  # Preview
        mock_editor.splitter.addWidget(QWidget())  # Chat
        mock_editor.chat_container = Mock()
        mock_editor.chat_container.isVisible = Mock(return_value=True)
        mock_editor.resize(1000, 600)

        manager._set_default_splitter_sizes()

        # Should set proportional split (2/5, 2/5, 1/5)
        sizes = mock_editor.splitter.sizes()
        assert len(sizes) == 3
        assert sizes[2] > 0  # Chat should have width


@pytest.mark.unit
class TestDynamicSizing:
    """Test suite for setup_dynamic_sizing method."""

    @patch("asciidoc_artisan.ui.ui_setup_manager.QGuiApplication.primaryScreen")
    def test_maximizes_when_start_maximized_true(self, mock_screen, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # Mock screen
        mock_screen_obj = Mock()
        mock_screen_obj.availableGeometry = Mock(return_value=QRect(0, 0, 1920, 1080))
        mock_screen.return_value = mock_screen_obj

        mock_editor._start_maximized = True

        with patch.object(mock_editor, "showMaximized") as mock_maximize:
            manager.setup_dynamic_sizing()
            mock_maximize.assert_called_once()

    @patch("asciidoc_artisan.ui.ui_setup_manager.QGuiApplication.primaryScreen")
    def test_calculates_dimensions_when_not_maximized(self, mock_screen, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # Mock screen
        mock_screen_obj = Mock()
        mock_screen_obj.availableGeometry = Mock(return_value=QRect(0, 0, 1920, 1080))
        mock_screen.return_value = mock_screen_obj

        mock_editor._start_maximized = False
        mock_editor._initial_geometry = None

        with patch.object(mock_editor, "setGeometry") as mock_set_geom:
            manager.setup_dynamic_sizing()
            # Should call setGeometry with calculated dimensions
            mock_set_geom.assert_called_once()

    @patch("asciidoc_artisan.ui.ui_setup_manager.QGuiApplication.primaryScreen")
    def test_uses_initial_geometry_when_provided(self, mock_screen, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # Mock screen
        mock_screen_obj = Mock()
        mock_screen_obj.availableGeometry = Mock(return_value=QRect(0, 0, 1920, 1080))
        mock_screen.return_value = mock_screen_obj

        mock_editor._start_maximized = False
        mock_editor._initial_geometry = QRect(100, 100, 800, 600)

        with patch.object(mock_editor, "setGeometry") as mock_set_geom:
            manager.setup_dynamic_sizing()
            # Should use initial geometry
            mock_set_geom.assert_called_once_with(mock_editor._initial_geometry)

    @patch("asciidoc_artisan.ui.ui_setup_manager.QGuiApplication.primaryScreen")
    def test_handles_no_screen(self, mock_screen, mock_editor):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        manager = UISetupManager(mock_editor)

        # No screen available
        mock_screen.return_value = None

        # Should not crash
        manager.setup_dynamic_sizing()
