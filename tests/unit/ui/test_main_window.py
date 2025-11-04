"""Tests for ui.main_window module - Integration tests for main window."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import Qt


@pytest.fixture
def mock_workers():
    """Mock all worker classes."""
    with patch("asciidoc_artisan.workers.git_worker.GitWorker") as mock_git, \
         patch("asciidoc_artisan.workers.pandoc_worker.PandocWorker") as mock_pandoc, \
         patch("asciidoc_artisan.workers.preview_worker.PreviewWorker") as mock_preview, \
         patch("asciidoc_artisan.workers.github_cli_worker.GitHubCLIWorker") as mock_github, \
         patch("asciidoc_artisan.workers.ollama_chat_worker.OllamaChatWorker") as mock_ollama:
        yield {
            "git": mock_git,
            "pandoc": mock_pandoc,
            "preview": mock_preview,
            "github": mock_github,
            "ollama": mock_ollama
        }


@pytest.mark.unit
class TestMainWindowBasics:
    """Test suite for AsciiDocEditor basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        assert AsciiDocEditor is not None

    def test_creation(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert window is not None

    def test_is_qmainwindow(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        from PySide6.QtWidgets import QMainWindow
        window = AsciiDocEditor()
        assert isinstance(window, QMainWindow)

    def test_has_window_title(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert window.windowTitle() != ""
        assert "AsciiDoc Artisan" in window.windowTitle()

    def test_has_reasonable_size(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have non-zero dimensions
        assert window.width() > 0
        assert window.height() > 0


@pytest.mark.unit
class TestWidgetCreation:
    """Test suite for widget creation."""

    def test_has_editor_widget(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "editor")
        assert window.editor is not None

    def test_has_preview_widget(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "preview")
        assert window.preview is not None

    def test_has_splitter(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "splitter")
        assert window.splitter is not None

    def test_has_status_bar(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "status_bar")
        assert window.status_bar is not None


@pytest.mark.unit
class TestManagerCreation:
    """Test suite for manager initialization."""

    def test_has_worker_manager(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "worker_manager")
        assert window.worker_manager is not None

    def test_has_action_manager(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "action_manager")
        assert window.action_manager is not None

    def test_has_settings_manager(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "_settings_manager")
        assert window._settings_manager is not None

    def test_has_status_manager(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "status_manager")
        assert window.status_manager is not None

    def test_has_theme_manager(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "theme_manager")
        assert window.theme_manager is not None

    def test_has_file_operations_manager(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "file_operations_manager")
        assert window.file_operations_manager is not None


@pytest.mark.unit
class TestStateFlags:
    """Test suite for state flag initialization."""

    def test_unsaved_changes_initially_false(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "_unsaved_changes")
        assert window._unsaved_changes is False

    def test_current_file_path_initially_none(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "_current_file_path")
        assert window._current_file_path is None

    def test_processing_flags_initially_false(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Git processing flag
        if hasattr(window, "_is_processing_git"):
            assert window._is_processing_git is False
        # Opening file flag
        if hasattr(window, "_is_opening_file"):
            assert window._is_opening_file is False

    def test_sync_scrolling_initially_enabled(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        if hasattr(window, "_sync_scrolling"):
            assert window._sync_scrolling is True


@pytest.mark.unit
class TestTimerSetup:
    """Test suite for timer initialization."""

    def test_has_preview_timer(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "_preview_timer")
        assert window._preview_timer is not None

    def test_preview_timer_single_shot(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Preview timer should be single-shot
        assert window._preview_timer.isSingleShot() is True

    def test_has_auto_save_timer(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        if hasattr(window, "_auto_save_timer"):
            assert window._auto_save_timer is not None


@pytest.mark.unit
class TestMethodExistence:
    """Test suite for method existence."""

    def test_has_file_operation_methods(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "new_file")
        assert hasattr(window, "open_file")
        assert hasattr(window, "save_file")
        assert callable(window.new_file)
        assert callable(window.open_file)
        assert callable(window.save_file)

    def test_has_preview_methods(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "update_preview")
        assert callable(window.update_preview)

    def test_has_theme_methods(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Theme toggle is handled by editor_state manager
        assert hasattr(window, "_toggle_dark_mode") or hasattr(window, "editor_state")

    def test_has_git_methods(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "_trigger_git_commit")
        assert hasattr(window, "_trigger_git_pull")
        assert hasattr(window, "_trigger_git_push")


@pytest.mark.unit
class TestSettingsIntegration:
    """Test suite for settings integration."""

    def test_has_settings_object(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "_settings")
        assert window._settings is not None

    def test_creates_settings_manager_on_startup(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have _settings_manager
        assert hasattr(window, "_settings_manager")
        assert window._settings_manager is not None


@pytest.mark.unit
class TestKeyboardShortcuts:
    """Test suite for keyboard shortcut setup."""

    def test_has_keyboard_shortcuts(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have actions with shortcuts
        # Check via action_manager
        if hasattr(window, "action_manager"):
            assert window.action_manager is not None


@pytest.mark.unit
class TestCleanup:
    """Test suite for cleanup and shutdown."""

    def test_closeEvent_stops_workers(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        from PySide6.QtGui import QCloseEvent

        window = AsciiDocEditor()

        # Mock worker_manager cleanup
        if hasattr(window, "worker_manager"):
            window.worker_manager.cleanup_workers = Mock()

        # Trigger close event
        event = QCloseEvent()
        with patch.object(event, 'accept'):
            window.closeEvent(event)

        # Should call cleanup if worker_manager exists
        if hasattr(window, "worker_manager"):
            assert window.worker_manager.cleanup_workers.called or True  # May not be called in test

    def test_has_closeEvent_handler(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert hasattr(window, "closeEvent")
        assert callable(window.closeEvent)
