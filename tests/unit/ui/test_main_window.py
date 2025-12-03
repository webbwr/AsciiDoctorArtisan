"""Tests for ui.main_window module - Integration tests for main window."""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_workers():
    """Mock all worker classes."""
    with (
        patch("asciidoc_artisan.workers.git_worker.GitWorker") as mock_git,
        patch("asciidoc_artisan.workers.pandoc_worker.PandocWorker") as mock_pandoc,
        patch("asciidoc_artisan.workers.preview_worker.PreviewWorker") as mock_preview,
        patch("asciidoc_artisan.workers.github_cli_worker.GitHubCLIWorker") as mock_github,
        patch("asciidoc_artisan.workers.ollama_chat_worker.OllamaChatWorker") as mock_ollama,
    ):
        yield {
            "git": mock_git,
            "pandoc": mock_pandoc,
            "preview": mock_preview,
            "github": mock_github,
            "ollama": mock_ollama,
        }


@pytest.fixture(scope="class")
def main_window(mock_workers, qapp):
    """Create a single main window instance for the entire test class."""
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

    window = AsciiDocEditor()
    yield window
    # Cleanup
    window.close()
    qapp.processEvents()


@pytest.mark.fr_001
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
        from PySide6.QtWidgets import QMainWindow

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
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


@pytest.mark.fr_001
@pytest.mark.unit
class TestCleanup:
    """Test suite for cleanup and shutdown."""

    # NOTE: test_closeEvent_stops_workers removed - complex async worker cleanup, better tested in E2E

    def test_has_closeEvent_handler(self, mock_workers, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        assert hasattr(window, "closeEvent")
        assert callable(window.closeEvent)


# ============================================================================
# PHASE 1: HIGH-PRIORITY METHODS (Target: 50% → 70% coverage)
# ============================================================================


@pytest.mark.fr_001
@pytest.mark.unit
class TestHandleSearchRequested:
    """Test _handle_search_requested() method (Priority #1)."""

    def test_search_with_multiple_matches(self, mock_workers, qapp):
        """Test searching for text with multiple matches."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("test text test more test")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()
        window.find_bar.set_not_found_style = Mock()
        window.find_bar.clear_not_found_style = Mock()

        # Trigger search
        window.search_handler.handle_search_requested("test", case_sensitive=False)

        # Verify match count was updated (should find 3 matches)
        window.find_bar.update_match_count.assert_called()
        call_args = window.find_bar.update_match_count.call_args[0]
        assert call_args[1] == 3  # Total matches should be 3

    def test_search_with_no_matches(self, mock_workers, qapp):
        """Test searching for text with no matches."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("hello world")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()
        window.find_bar.set_not_found_style = Mock()

        # Trigger search for non-existent text
        window.search_handler.handle_search_requested("xyz", case_sensitive=False)

        # Verify no matches found
        window.find_bar.update_match_count.assert_called_with(0, 0)
        window.find_bar.set_not_found_style.assert_called_once()

    def test_search_with_empty_text(self, mock_workers, qapp):
        """Test searching with empty search text clears highlighting."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("some text")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()

        # Trigger search with empty text
        window.search_handler.handle_search_requested("", case_sensitive=False)

        # Verify match count cleared
        window.find_bar.update_match_count.assert_called_with(0, 0)

    def test_search_case_sensitive(self, mock_workers, qapp):
        """Test case-sensitive search."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("Test test TEST")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()

        # Trigger case-sensitive search for "test"
        window.search_handler.handle_search_requested("test", case_sensitive=True)

        # Should find only 1 match (not "Test" or "TEST")
        call_args = window.find_bar.update_match_count.call_args[0]
        assert call_args[1] == 1  # Only lowercase "test"

    def test_search_case_insensitive(self, mock_workers, qapp):
        """Test case-insensitive search."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("Test test TEST")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()

        # Trigger case-insensitive search for "test"
        window.search_handler.handle_search_requested("test", case_sensitive=False)

        # Should find all 3 matches
        call_args = window.find_bar.update_match_count.call_args[0]
        assert call_args[1] == 3

    def test_search_highlights_matches(self, mock_workers, qapp):
        """Test that search highlights all matches in editor."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("foo bar foo")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()

        # Trigger search
        window.search_handler.handle_search_requested("foo", case_sensitive=False)

        # Verify search selections were created
        assert hasattr(window.editor, "search_selections")
        assert len(window.editor.search_selections) == 2  # Two "foo" matches

    def test_search_error_handling(self, mock_workers, qapp):
        """Test search handles errors gracefully."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("test")

        # Mock find_bar methods
        window.find_bar.update_match_count = Mock()

        # Mock search_engine to raise exception
        window.search_engine.find_all = Mock(side_effect=Exception("Search error"))

        # Trigger search - should not crash
        window.search_handler.handle_search_requested("test", case_sensitive=False)

        # Should update match count to 0
        window.find_bar.update_match_count.assert_called_with(0, 0)


@pytest.mark.fr_001
@pytest.mark.unit
class TestHandleReplaceAll:
    """Test _handle_replace_all() method (Priority #2)."""

    def test_replace_all_with_confirmation_accepted(self, mock_workers, qapp):
        """Test replace all when user accepts confirmation."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("foo bar foo")

        # Mock find_bar methods
        window.find_bar.get_search_text = Mock(return_value="foo")
        window.find_bar.is_case_sensitive = Mock(return_value=False)
        window.find_bar.update_match_count = Mock()

        # Mock status_manager
        window.status_manager.show_status = Mock()

        # Mock QMessageBox.question to return Yes
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
            window.search_handler.handle_replace_all("baz")

        # Verify text was replaced
        assert window.editor.toPlainText() == "baz bar baz"

        # Verify status message shown
        window.status_manager.show_status.assert_called()

    def test_replace_all_with_confirmation_declined(self, mock_workers, qapp):
        """Test replace all when user declines confirmation."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        original_text = "foo bar foo"
        window.editor.setPlainText(original_text)

        # Mock find_bar methods
        window.find_bar.get_search_text = Mock(return_value="foo")
        window.find_bar.is_case_sensitive = Mock(return_value=False)

        # Mock QMessageBox.question to return No
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No):
            window.search_handler.handle_replace_all("baz")

        # Verify text was NOT replaced
        assert window.editor.toPlainText() == original_text

    def test_replace_all_with_no_matches(self, mock_workers, qapp):
        """Test replace all when no matches found."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("hello world")

        # Mock find_bar methods
        window.find_bar.get_search_text = Mock(return_value="xyz")
        window.find_bar.is_case_sensitive = Mock(return_value=False)

        # Mock status_manager
        window.status_manager.show_status = Mock()

        # Trigger replace all
        window.search_handler.handle_replace_all("abc")

        # Verify status message shown
        window.status_manager.show_status.assert_called()

    def test_replace_all_with_empty_search(self, mock_workers, qapp):
        """Test replace all with empty search text."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("test")

        # Mock find_bar methods
        window.find_bar.get_search_text = Mock(return_value="")

        # Trigger replace all - should return early
        window.search_handler.handle_replace_all("replacement")

        # Text should be unchanged
        assert window.editor.toPlainText() == "test"

    def test_replace_all_preserves_cursor_position(self, mock_workers, qapp):
        """Test replace all preserves cursor position approximately."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("foo bar foo")

        # Set cursor to middle of text
        cursor = window.editor.textCursor()
        cursor.setPosition(7)  # After "foo bar "
        window.editor.setTextCursor(cursor)

        # Mock find_bar methods
        window.find_bar.get_search_text = Mock(return_value="foo")
        window.find_bar.is_case_sensitive = Mock(return_value=False)
        window.find_bar.update_match_count = Mock()

        # Mock status_manager
        window.status_manager.show_status = Mock()

        # Mock QMessageBox.question to return Yes
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
            window.search_handler.handle_replace_all("x")

        # Cursor should still be valid (not past end of text)
        assert window.editor.textCursor().position() <= len(window.editor.toPlainText())

    def test_replace_all_error_handling(self, mock_workers, qapp):
        """Test replace all handles errors gracefully."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("test")

        # Mock find_bar methods
        window.find_bar.get_search_text = Mock(return_value="test")
        window.find_bar.is_case_sensitive = Mock(return_value=False)

        # Mock status_manager
        window.status_manager.show_status = Mock()

        # Mock search_engine to raise exception
        window.search_engine.find_all = Mock(side_effect=Exception("Replace error"))

        # Trigger replace all - should not crash
        window.search_handler.handle_replace_all("replacement")

        # Should show error status
        window.status_manager.show_status.assert_called()


@pytest.mark.fr_001
@pytest.mark.unit
class TestStartPreviewTimer:
    """Test _start_preview_timer() method (Priority #3)."""

    def test_preview_timer_starts(self, mock_workers, qapp):
        """Test that preview timer starts when called."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window._is_opening_file = False
        window.editor.setPlainText("test")

        # Mock status_manager
        window.status_manager.update_window_title = Mock()
        window.status_manager.update_document_metrics = Mock()

        # Call _start_preview_timer
        window._start_preview_timer()

        # Verify timer is running
        assert window._preview_timer.isActive()

    def test_preview_timer_skips_when_opening_file(self, mock_workers, qapp):
        """Test that preview timer doesn't start when opening file."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window._is_opening_file = True
        window._preview_timer.stop()  # Ensure timer is stopped

        # Call _start_preview_timer
        window._start_preview_timer()

        # Verify timer is NOT running
        assert not window._preview_timer.isActive()

    def test_preview_timer_sets_unsaved_changes(self, mock_workers, qapp):
        """Test that preview timer sets unsaved changes flag."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window._is_opening_file = False
        window._unsaved_changes = False
        window.editor.setPlainText("test")

        # Mock status_manager
        window.status_manager.update_window_title = Mock()
        window.status_manager.update_document_metrics = Mock()

        # Call _start_preview_timer
        window._start_preview_timer()

        # Verify unsaved changes flag set
        assert window._unsaved_changes is True

    def test_preview_timer_adaptive_debounce_small_doc(self, mock_workers, qapp):
        """Test adaptive debounce for small documents (<1000 chars)."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window._is_opening_file = False
        window.editor.setPlainText("small document")  # <1000 chars

        # Mock status_manager
        window.status_manager.update_window_title = Mock()
        window.status_manager.update_document_metrics = Mock()

        # Call _start_preview_timer
        window._start_preview_timer()

        # Verify timer interval is small (200ms for small docs)
        assert window._preview_timer.interval() <= 300

    def test_preview_timer_adaptive_debounce_large_doc(self, mock_workers, qapp):
        """Test adaptive debounce for medium documents (10-100KB)."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window._is_opening_file = False
        # Create medium document (15KB falls into medium category <100KB)
        medium_text = "x" * 15000
        window.editor.setPlainText(medium_text)

        # Mock status_manager
        window.status_manager.update_window_title = Mock()
        window.status_manager.update_document_metrics = Mock()

        # Call _start_preview_timer
        window._start_preview_timer()

        # Verify timer interval for medium docs (100ms per resource_monitor)
        assert window._preview_timer.interval() >= 100

    def test_preview_timer_updates_document_metrics(self, mock_workers, qapp):
        """Test that preview timer updates document metrics."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window._is_opening_file = False
        window.editor.setPlainText("test")

        # Mock status_manager
        window.status_manager.update_window_title = Mock()
        window.status_manager.update_document_metrics = Mock()

        # Call _start_preview_timer
        window._start_preview_timer()

        # Verify document metrics updated
        window.status_manager.update_document_metrics.assert_called_once()


@pytest.mark.fr_001
@pytest.mark.unit
class TestSetupWorkersAndThreads:
    """Test _setup_workers_and_threads() method (Priority #4)."""

    def test_workers_initialized(self, mock_workers, qapp):
        """Test that all workers are initialized."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Verify workers exist
        assert hasattr(window, "git_worker")
        assert hasattr(window, "pandoc_worker")
        assert hasattr(window, "preview_worker")
        # Note: github_cli_worker is managed internally by github_handler
        assert hasattr(window, "github_handler")
        assert hasattr(window, "ollama_chat_worker")

    def test_chat_manager_initialized(self, mock_workers, qapp):
        """Test that chat manager is initialized."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Verify chat manager exists and has document content provider
        assert hasattr(window, "chat_manager")
        assert window.chat_manager is not None

    def test_signal_connections_established(self, mock_workers, qapp):
        """Test that signal connections are established."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Verify chat manager signals connected
        # Note: Cannot easily test signal connections directly,
        # but we can verify the objects exist and have the signals
        assert hasattr(window, "chat_manager")
        assert hasattr(window.chat_manager, "message_sent_to_worker")
        assert hasattr(window.chat_manager, "status_message")

    def test_github_handler_initialized(self, mock_workers, qapp):
        """Test that GitHub handler is initialized."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Verify GitHub handler exists
        assert hasattr(window, "github_handler")
        assert window.github_handler is not None


@pytest.mark.fr_001
@pytest.mark.unit
class TestRefreshFromSettings:
    """Test _refresh_from_settings() method (Priority #5)."""

    def test_applies_dark_theme(self, mock_workers, qapp):
        """Test that dark theme is applied when enabled."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set dark mode in settings
        window._settings.dark_mode = True

        # Mock theme_manager method
        window.theme_manager.apply_theme = Mock()

        # Mock other methods
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()

        # Refresh from settings
        window._refresh_from_settings()

        # Verify apply_theme was called (which checks dark_mode internally)
        window.theme_manager.apply_theme.assert_called_once()

    def test_applies_light_theme(self, mock_workers, qapp):
        """Test that light theme is applied when disabled."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set light mode in settings
        window._settings.dark_mode = False

        # Mock theme_manager method
        window.theme_manager.apply_theme = Mock()

        # Mock other methods
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()

        # Refresh from settings
        window._refresh_from_settings()

        # Verify apply_theme was called (which checks dark_mode internally)
        window.theme_manager.apply_theme.assert_called_once()

    def test_updates_font_size(self, mock_workers, qapp):
        """Test that font size setting triggers setFont call."""
        from asciidoc_artisan.core import EDITOR_FONT_FAMILY
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set font size in settings
        window._settings.font_size = 14

        # Mock other methods
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()
        window.theme_manager.apply_dark_theme = Mock()

        # Mock setFont to capture calls
        mock_setFont = Mock()
        window.editor.setFont = mock_setFont

        # Refresh from settings
        window._refresh_from_settings()

        # Verify setFont was called
        assert mock_setFont.called, "setFont should have been called"

        # Get the font argument
        font_arg = mock_setFont.call_args[0][0]

        # Verify font properties (family check is reliable even in headless)
        assert font_arg.family() == EDITOR_FONT_FAMILY

    def test_updates_ai_status_bar(self, mock_workers, qapp):
        """Test that AI status bar is updated."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock methods
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()
        window.theme_manager.apply_light_theme = Mock()

        # Refresh from settings
        window._refresh_from_settings()

        # Verify AI status bar updated
        window._update_ai_status_bar.assert_called_once()

    def test_updates_ai_backend_checkmarks(self, mock_workers, qapp):
        """Test that AI backend checkmarks are updated."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock methods
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()
        window.theme_manager.apply_light_theme = Mock()

        # Refresh from settings
        window._refresh_from_settings()

        # Verify AI backend checkmarks updated
        window._update_ai_backend_checkmarks.assert_called_once()

    def test_updates_chat_manager_settings(self, mock_workers, qapp):
        """Test that chat manager settings are updated."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock methods
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()
        window.theme_manager.apply_light_theme = Mock()
        window.chat_manager.update_settings = Mock()

        # Refresh from settings
        window._refresh_from_settings()

        # Verify chat manager settings updated
        window.chat_manager.update_settings.assert_called_once_with(window._settings)

    def test_updates_window_geometry(self, mock_workers, qapp):
        """Test that window geometry is updated from settings."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock save_settings to prevent it from overwriting settings.maximized
        window._settings_manager.save_settings = Mock()

        # Set window geometry in settings
        window._settings.maximized = False
        window._settings.window_geometry = {
            "x": 100,
            "y": 100,
            "width": 800,
            "height": 600,
        }

        # Mock other methods to prevent side effects
        window._update_ai_status_bar = Mock()
        window._update_ai_backend_checkmarks = Mock()
        window.theme_manager.apply_theme = Mock()

        # Mock dialog_manager to prevent _apply_font_settings side effects
        window.dialog_manager._apply_font_settings = Mock()

        # Mock setGeometry to verify it's called (Qt may not honor it in headless tests)
        with patch.object(window, "setGeometry") as mock_set_geometry:
            # Refresh from settings
            window._refresh_from_settings()

            # Verify setGeometry was called with correct values
            mock_set_geometry.assert_called_once_with(100, 100, 800, 600)


@pytest.mark.fr_001
@pytest.mark.unit
class TestRouteChatMessageToWorker:
    """Test _route_chat_message_to_worker() method (Priority #6)."""

    def test_routes_to_ollama_backend(self, mock_workers, qapp):
        """Test routing message to Ollama backend."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set Ollama as active backend
        window._settings.ai_backend = "ollama"

        # Mock ollama_chat_worker
        window.ollama_chat_worker.send_message = Mock()

        # Route message
        message = "test message"
        model = "llama2"
        context_mode = "general"
        history = []
        document_content = None

        window._route_chat_message_to_worker(message, model, context_mode, history, document_content)

        # Verify routed to Ollama
        window.ollama_chat_worker.send_message.assert_called_once_with(
            message, model, context_mode, history, document_content
        )

    def test_routes_to_claude_backend(self, mock_workers, qapp):
        """Test routing message to Claude backend."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set Claude as active backend
        window._settings.ai_backend = "claude"

        # Mock claude_worker
        window.claude_worker.send_message = Mock()

        # Route message
        message = "test message"
        model = "claude-sonnet-4"
        context_mode = "general"
        history = []
        document_content = None

        window._route_chat_message_to_worker(message, model, context_mode, history, document_content)

        # Verify routed to Claude
        window.claude_worker.send_message.assert_called()

    def test_claude_routing_with_document_context(self, mock_workers, qapp):
        """Test Claude routing includes document content in message."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set Claude as active backend
        window._settings.ai_backend = "claude"

        # Mock claude_worker
        window.claude_worker.send_message = Mock()

        # Route message with document context
        message = "what does this document say?"
        model = "claude-sonnet-4"
        context_mode = "document"
        history = []
        document_content = "= My Document\n\nThis is content."

        window._route_chat_message_to_worker(message, model, context_mode, history, document_content)

        # Verify Claude was called with document content in message
        call_args = window.claude_worker.send_message.call_args
        assert "My Document" in call_args[1]["message"]

    def test_claude_routing_converts_history_format(self, mock_workers, qapp):
        """Test Claude routing converts ChatMessage history to ClaudeMessage format."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set Claude as active backend
        window._settings.ai_backend = "claude"

        # Mock claude_worker
        window.claude_worker.send_message = Mock()

        # Create mock chat history
        from asciidoc_artisan.core.models import ChatMessage

        history = [
            ChatMessage(
                role="user",
                content="hello",
                timestamp=0,
                model="test",
                context_mode="general",
            ),
            ChatMessage(
                role="assistant",
                content="hi there",
                timestamp=1,
                model="test",
                context_mode="general",
            ),
        ]

        # Route message
        window._route_chat_message_to_worker("test", "claude-sonnet-4", "general", history, None)

        # Verify Claude was called with conversation history
        call_args = window.claude_worker.send_message.call_args
        assert "conversation_history" in call_args[1]

    def test_unknown_backend_shows_error(self, mock_workers, qapp):
        """Test unknown backend shows error message."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set unknown backend
        window._settings.ai_backend = "unknown_backend"

        # Mock status_manager
        window.status_manager.show_status = Mock()

        # Route message
        window._route_chat_message_to_worker("test", "model", "general", [], None)

        # Verify error shown
        window.status_manager.show_status.assert_called()
        assert "Unknown AI backend" in str(window.status_manager.show_status.call_args)

    def test_claude_system_prompt_for_document_mode(self, mock_workers, qapp):
        """Test Claude gets document-specific system prompt for document mode."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Test document mode system prompt
        prompt = window._build_claude_system_prompt("document", "claude-sonnet-4")

        assert "AsciiDoc document" in prompt
        assert "document content" in prompt.lower()

    def test_claude_system_prompt_for_syntax_mode(self, mock_workers, qapp):
        """Test Claude gets syntax-specific system prompt for syntax mode."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Test syntax mode system prompt
        prompt = window._build_claude_system_prompt("syntax", "claude-sonnet-4")

        assert "AsciiDoc syntax" in prompt
        assert "syntax" in prompt.lower()

    def test_claude_system_prompt_for_editing_mode(self, mock_workers, qapp):
        """Test Claude gets editing-specific system prompt for editing mode."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Test editing mode system prompt
        prompt = window._build_claude_system_prompt("editing", "claude-sonnet-4")

        assert "editing assistant" in prompt.lower()
        assert "improve" in prompt.lower()

    def test_claude_system_prompt_for_general_mode(self, mock_workers, qapp):
        """Test Claude gets general system prompt for general mode."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Test general mode system prompt
        prompt = window._build_claude_system_prompt("general", "claude-sonnet-4")

        assert "helpful" in prompt.lower()
        assert "AI assistant" in prompt


# ============================================================================
# PHASE 2: MEDIUM-PRIORITY METHODS (Target: 70% → 85% coverage)
# ============================================================================


@pytest.mark.fr_001
@pytest.mark.unit
class TestNewFromTemplate:
    """Test new_from_template() method (Priority #7)."""

    def test_creates_new_document_from_template(self, mock_workers, qapp):
        """Test creating new document from template."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock TemplateBrowser dialog
        with patch("asciidoc_artisan.ui.main_window.TemplateBrowser") as mock_browser:
            # Configure mock template
            mock_template = Mock()
            mock_template.name = "Article"
            mock_template.content = "= {{title}}\n\nContent here"
            mock_template.variables = []  # Template engine expects an iterable

            # Configure mock browser instance
            mock_browser_instance = Mock()
            mock_browser_instance.exec.return_value = True
            mock_browser_instance.selected_template = mock_template
            mock_browser_instance.variable_values = {"title": "Test Article"}
            mock_browser.return_value = mock_browser_instance

            # Mock file_handler
            window.file_handler.new_file = Mock()

            # Call new_from_template
            window.new_from_template()

            # Verify new file was created
            window.file_handler.new_file.assert_called_once()

            # Verify editor has template content
            assert "Test Article" in window.editor.toPlainText()

    def test_handles_dialog_cancellation(self, mock_workers, qapp):
        """Test handling when user cancels template browser."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock TemplateBrowser dialog
        with patch("asciidoc_artisan.ui.main_window.TemplateBrowser") as mock_browser:
            # Configure mock browser to return False (cancelled)
            mock_browser_instance = Mock()
            mock_browser_instance.exec.return_value = False
            mock_browser.return_value = mock_browser_instance

            # Mock file_handler
            window.file_handler.new_file = Mock()

            original_text = window.editor.toPlainText()

            # Call new_from_template
            window.new_from_template()

            # Verify new file was NOT created
            window.file_handler.new_file.assert_not_called()

            # Editor content should be unchanged
            assert window.editor.toPlainText() == original_text


@pytest.mark.fr_001
@pytest.mark.unit
class TestSaveFile:
    """Test save_file() method (Priority #8)."""

    def test_saves_file_normally(self, mock_workers, qapp):
        """Test saving file delegates to file_operations_manager."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock file_operations_manager
        window.file_operations_manager.save_file = Mock(return_value=True)

        # Save file
        result = window.save_file(save_as=False)

        # Verify delegation
        window.file_operations_manager.save_file.assert_called_once_with(False)
        assert result is True

    def test_saves_file_as(self, mock_workers, qapp):
        """Test saving file with save_as flag."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock file_operations_manager
        window.file_operations_manager.save_file = Mock(return_value=True)

        # Save file as
        result = window.save_file(save_as=True)

        # Verify delegation with save_as=True
        window.file_operations_manager.save_file.assert_called_once_with(True)
        assert result is True


@pytest.mark.fr_001
@pytest.mark.unit
class TestAutoSave:
    """Test _auto_save() method (Priority #9)."""

    def test_auto_saves_when_changes_exist(self, mock_workers, qapp):
        """Test auto-save saves file when unsaved changes exist."""
        from pathlib import Path

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set up test conditions
        window._current_file_path = Path("/tmp/test.adoc")
        window._unsaved_changes = True
        window.editor.setPlainText("test content")

        # Mock atomic_save_text
        with patch("asciidoc_artisan.ui.main_window.atomic_save_text", return_value=True) as mock_save:
            # Call auto-save
            window._auto_save()

            # Verify save was called
            mock_save.assert_called_once()

    def test_auto_save_skips_when_no_changes(self, mock_workers, qapp):
        """Test auto-save skips when no unsaved changes."""
        from pathlib import Path

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set up test conditions
        window._current_file_path = Path("/tmp/test.adoc")
        window._unsaved_changes = False

        # Mock atomic_save_text
        with patch("asciidoc_artisan.ui.main_window.atomic_save_text") as mock_save:
            # Call auto-save
            window._auto_save()

            # Verify save was NOT called
            mock_save.assert_not_called()

    def test_auto_save_skips_when_no_file_path(self, mock_workers, qapp):
        """Test auto-save skips when no file path set."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set up test conditions
        window._current_file_path = None
        window._unsaved_changes = True

        # Mock atomic_save_text
        with patch("asciidoc_artisan.ui.main_window.atomic_save_text") as mock_save:
            # Call auto-save
            window._auto_save()

            # Verify save was NOT called
            mock_save.assert_not_called()


@pytest.mark.fr_001
@pytest.mark.unit
class TestHandleQuickCommit:
    """Test _handle_quick_commit() method (Priority #10)."""

    def test_quick_commit_delegates_to_git_handler(self, mock_workers, qapp):
        """Test quick commit delegates to git_handler."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock git_handler methods
        window.git_handler._ensure_ready = Mock(return_value=True)
        window.git_handler.quick_commit = Mock()

        # Call quick commit
        message = "Test commit message"
        window._handle_quick_commit(message)

        # Verify delegation
        window.git_handler.quick_commit.assert_called_once_with(message)

    def test_quick_commit_checks_git_ready(self, mock_workers, qapp):
        """Test quick commit checks if Git is ready."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock git_handler methods
        window.git_handler._ensure_ready = Mock(return_value=False)
        window.git_handler.quick_commit = Mock()

        # Call quick commit
        window._handle_quick_commit("test")

        # Verify quick_commit was NOT called
        window.git_handler.quick_commit.assert_not_called()


@pytest.mark.fr_001
@pytest.mark.unit
class TestToggleTelemetry:
    """Test toggle_telemetry() method (Priority #11)."""

    def test_enables_telemetry_when_disabled(self, mock_workers, qapp):
        """Test enabling telemetry."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set initial state
        window._settings.telemetry_enabled = False

        # Mock methods
        window._update_telemetry_menu_text = Mock()
        window.status_manager.show_message = Mock()
        window._settings_manager.save_settings = Mock()

        # Toggle telemetry
        window.toggle_telemetry()

        # Verify telemetry enabled
        assert window._settings.telemetry_enabled is True
        window.status_manager.show_message.assert_called()

    def test_disables_telemetry_when_enabled(self, mock_workers, qapp):
        """Test disabling telemetry."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set initial state
        window._settings.telemetry_enabled = True

        # Mock methods
        window._update_telemetry_menu_text = Mock()
        window.status_manager.show_message = Mock()
        window._settings_manager.save_settings = Mock()

        # Toggle telemetry
        window.toggle_telemetry()

        # Verify telemetry disabled
        assert window._settings.telemetry_enabled is False
        window.status_manager.show_message.assert_called()

    def test_saves_settings_after_toggle(self, mock_workers, qapp):
        """Test that settings are saved after toggling telemetry."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock methods
        window._update_telemetry_menu_text = Mock()
        window.status_manager.show_message = Mock()
        window._settings_manager.save_settings = Mock()

        # Toggle telemetry
        window.toggle_telemetry()

        # Verify settings saved
        window._settings_manager.save_settings.assert_called_once()


@pytest.mark.fr_001
@pytest.mark.unit
class TestCloseEvent:
    """Test closeEvent() method (Priority #12)."""

    def test_close_event_in_test_mode_accepts(self, mock_workers, qapp):
        """Test that close event is accepted in test mode."""
        import os

        from PySide6.QtGui import QCloseEvent

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set test environment variable
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        # Mock worker_manager
        window.worker_manager.shutdown = Mock()

        # Create close event
        event = QCloseEvent()

        try:
            # Call closeEvent
            window.closeEvent(event)

            # Verify event accepted
            assert event.isAccepted()

            # Verify worker shutdown called
            window.worker_manager.shutdown.assert_called_once()
        finally:
            # Clean up environment
            del os.environ["PYTEST_CURRENT_TEST"]

    @patch("asciidoc_artisan.ui.main_window.os.environ.get")
    def test_close_event_delegates_to_editor_state(self, mock_env_get, mock_workers, qapp):
        """Test that close event delegates to editor_state in normal mode."""
        from PySide6.QtGui import QCloseEvent

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        # Mock os.environ.get to return None (not in pytest mode)
        mock_env_get.return_value = None

        window = AsciiDocEditor()

        # Mock editor_state
        window.editor_state.handle_close_event = Mock()

        # Create close event
        event = QCloseEvent()

        # Call closeEvent (not in test mode)
        window.closeEvent(event)

        # Verify delegation
        window.editor_state.handle_close_event.assert_called_once_with(event)


# ============================================================================
# PHASE 3: LOW-PRIORITY METHODS (Target: 85% → 90%+ coverage)
# ============================================================================


@pytest.mark.fr_001
@pytest.mark.unit
class TestInitializeAsciidoc:
    """Test _initialize_asciidoc() method (Priority #13)."""

    def test_initializes_asciidoc_api_when_available(self, mock_workers, qapp):
        """Test AsciiDoc API initialization when available."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Verify asciidoc_api initialized
        # Note: May be None if asciidoc3 not available
        assert hasattr(window, "_asciidoc_api")

    def test_handles_asciidoc_initialization_failure(self, mock_workers, qapp):
        """Test handles AsciiDoc API initialization failure."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        # Mock AsciiDoc3API to raise exception
        with patch(
            "asciidoc_artisan.ui.main_window.AsciiDoc3API",
            side_effect=Exception("Init error"),
        ):
            window = AsciiDocEditor()

            # Should handle error gracefully
            assert hasattr(window, "_asciidoc_api")


@pytest.mark.fr_001
@pytest.mark.unit
class TestUpdateWindowTitle:
    """Test _update_window_title() method (Priority #14)."""

    def test_updates_title_with_filename(self, mock_workers, qapp):
        """Test window title updates with filename."""
        from pathlib import Path

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set file path
        window._current_file_path = Path("/tmp/test.adoc")
        window._unsaved_changes = False

        # Update title
        window._update_window_title()

        # Verify title includes filename
        assert "test.adoc" in window.windowTitle()

    def test_updates_title_with_unsaved_indicator(self, mock_workers, qapp):
        """Test window title includes asterisk for unsaved changes."""
        from pathlib import Path

        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set file path and unsaved changes
        window._current_file_path = Path("/tmp/test.adoc")
        window._unsaved_changes = True

        # Update title
        window._update_window_title()

        # Verify title includes asterisk
        assert window.windowTitle().endswith("*")

    def test_updates_title_with_default_filename(self, mock_workers, qapp):
        """Test window title uses default filename when no file."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # No file path
        window._current_file_path = None
        window._unsaved_changes = False

        # Update title
        window._update_window_title()

        # Verify title includes default filename (lowercase "untitled.adoc")
        assert "untitled" in window.windowTitle().lower()


@pytest.mark.fr_001
@pytest.mark.unit
class TestHandlePreviewError:
    """Test _handle_preview_error() method (Priority #15)."""

    def test_delegates_preview_error_to_handler(self, mock_workers, qapp):
        """Test preview error delegates to preview_handler."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Mock preview_handler
        window.preview_handler.handle_preview_error = Mock()

        # Handle preview error
        error_html = "<div>Error message</div>"
        window._handle_preview_error(error_html)

        # Verify delegation
        window.preview_handler.handle_preview_error.assert_called_once_with(error_html)


# ============================================================================
# ADDITIONAL COVERAGE: Find & Search Handlers
# ============================================================================


@pytest.mark.fr_001
@pytest.mark.unit
class TestFindNextPrevious:
    """Test _handle_find_next() and _handle_find_previous() methods."""

    def test_find_next_navigates_to_next_match(self, mock_workers, qapp):
        """Test finding next match."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("foo bar foo baz foo")

        # Mock find_bar
        window.find_bar.get_search_text = Mock(return_value="foo")
        window.find_bar.is_case_sensitive = Mock(return_value=False)
        window.find_bar.update_match_count = Mock()

        # Position cursor at start
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)

        # Find next
        window.search_handler.handle_find_next()

        # Verify cursor moved to first match
        assert window.editor.textCursor().hasSelection()

    def test_find_previous_navigates_to_previous_match(self, mock_workers, qapp):
        """Test finding previous match."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("foo bar foo baz foo")

        # Mock find_bar
        window.find_bar.get_search_text = Mock(return_value="foo")
        window.find_bar.is_case_sensitive = Mock(return_value=False)
        window.find_bar.update_match_count = Mock()

        # Position cursor at end
        cursor = window.editor.textCursor()
        cursor.setPosition(len(window.editor.toPlainText()))
        window.editor.setTextCursor(cursor)

        # Find previous
        window.search_handler.handle_find_previous()

        # Verify cursor moved
        assert window.editor.textCursor().hasSelection()

    def test_find_closed_clears_highlighting(self, mock_workers, qapp):
        """Test closing find bar clears highlighting."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("test text")

        # Set up search selections
        window.editor.search_selections = [Mock()]

        # Mock editor focus
        window.editor.setFocus = Mock()

        # Handle find closed
        window.search_handler.handle_find_closed()

        # Verify highlighting cleared
        assert window.editor.search_selections == []


@pytest.mark.fr_001
@pytest.mark.unit
class TestHandleReplace:
    """Test _handle_replace() method."""

    def test_replaces_current_match(self, mock_workers, qapp):
        """Test replacing current match."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("foo bar foo")

        # Mock find_bar
        window.find_bar.get_search_text = Mock(return_value="foo")
        window.find_bar.is_case_sensitive = Mock(return_value=False)

        # Select first "foo"
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(3, cursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)

        # Mock _handle_find_next
        window.search_handler.handle_find_next = Mock()

        # Replace
        window.search_handler.handle_replace("baz")

        # Verify replacement
        assert "baz" in window.editor.toPlainText()

    def test_replace_skips_empty_search(self, mock_workers, qapp):
        """Test replace skips when search text is empty."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        window.editor.setPlainText("test")

        # Mock find_bar
        window.find_bar.get_search_text = Mock(return_value="")

        original_text = window.editor.toPlainText()

        # Replace
        window.search_handler.handle_replace("replacement")

        # Verify text unchanged
        assert window.editor.toPlainText() == original_text


# ============================================================================
# ADDITIONAL COVERAGE: Helper Methods
# ============================================================================


@pytest.mark.fr_001
@pytest.mark.unit
class TestApplyCombinedSelections:
    """Test _apply_combined_selections() method."""

    def test_combines_search_and_spell_selections(self, mock_workers, qapp):
        """Test combining search and spell check selections."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set up test selections
        window.editor.search_selections = [Mock()]
        window.editor.spell_check_selections = [Mock()]

        # Mock setExtraSelections
        window.editor.setExtraSelections = Mock()

        # Apply combined selections
        window._apply_combined_selections()

        # Verify setExtraSelections called with combined list
        window.editor.setExtraSelections.assert_called_once()
        call_args = window.editor.setExtraSelections.call_args[0][0]
        assert len(call_args) == 2  # Both selections included


@pytest.mark.fr_001
@pytest.mark.unit
class TestUpdateAIBackendCheckmarks:
    """Test _update_ai_backend_checkmarks() method."""

    def test_updates_ollama_checkmark_when_active(self, mock_workers, qapp):
        """Test Ollama checkmark when active."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set Ollama as active
        window._settings.ai_backend = "ollama"

        # Mock action_manager
        window.action_manager.ollama_status_act = Mock()
        window.action_manager.anthropic_status_act = Mock()

        # Update checkmarks
        window._update_ai_backend_checkmarks()

        # Verify Ollama has checkmark
        ollama_text = window.action_manager.ollama_status_act.setText.call_args[0][0]
        assert "✓" in ollama_text

    def test_updates_claude_checkmark_when_active(self, mock_workers, qapp):
        """Test Claude checkmark when active."""
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()

        # Set Claude as active
        window._settings.ai_backend = "claude"

        # Mock action_manager
        window.action_manager.ollama_status_act = Mock()
        window.action_manager.anthropic_status_act = Mock()

        # Update checkmarks
        window._update_ai_backend_checkmarks()

        # Verify Claude has checkmark
        claude_text = window.action_manager.anthropic_status_act.setText.call_args[0][0]
        assert "✓" in claude_text
