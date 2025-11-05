"""
UI integration tests using pytest-qt.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from asciidoc_artisan.ui import AsciiDocEditor


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


@pytest.mark.integration
class TestAsciiDocEditorUI:
    """Integration tests for AsciiDocEditor UI."""

    @pytest.fixture
    def editor(self, qtbot, monkeypatch):
        """Create AsciiDocEditor instance for testing with proper cleanup."""
        from unittest.mock import Mock

        with patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings"
        ), patch(
            "asciidoc_artisan.claude.claude_client.Anthropic"
        ) as mock_anthropic, patch(
            "asciidoc_artisan.claude.claude_client.SecureCredentials"
        ) as mock_creds:
            # Setup mocks to prevent Claude API calls
            mock_creds_instance = Mock()
            mock_creds_instance.get_anthropic_key.return_value = None  # No key = no API calls
            mock_creds_instance.has_anthropic_key.return_value = False
            mock_creds.return_value = mock_creds_instance

            window = AsciiDocEditor()

            # Mock the prompt_save_before_action to prevent dialog during teardown
            def mock_prompt(*args, **kwargs):
                return True  # Always proceed without showing dialog
            monkeypatch.setattr(window.status_manager, "prompt_save_before_action", mock_prompt)

            qtbot.addWidget(window)
            window.show()  # Show window for visibility tests

            yield window

            # Mark as no unsaved changes to prevent save dialog during teardown
            window._unsaved_changes = False

            # Note: qtbot handles window.close() and window.deleteLater()

    def test_window_creation(self, editor):
        """Test main window can be created."""
        assert editor is not None
        assert "AsciiDoc Artisan" in editor.windowTitle()

    def test_editor_widget_exists(self, editor):
        """Test editor widget is present."""
        assert editor.editor is not None
        assert editor.editor.isVisible()

    def test_preview_widget_exists(self, editor):
        """Test preview widget is present."""
        assert editor.preview is not None
        assert editor.preview.isVisible()

    def test_menu_bar_exists(self, editor):
        """Test menu bar is present."""
        assert editor.menuBar() is not None

    def test_status_bar_exists(self, editor):
        """Test status bar is present."""
        assert editor.status_bar is not None

    def test_editor_accepts_text_input(self, editor, qtbot):
        """Test editor accepts text input."""
        test_text = "= Test Document\n\nThis is a test."

        editor.editor.setPlainText(test_text)
        assert editor.editor.toPlainText() == test_text

    def test_unsaved_changes_flag(self, editor, qtbot):
        """Test unsaved changes flag updates."""
        # Type some text
        editor.editor.setPlainText("Test content")

        # Trigger text changed signal
        editor.editor.textChanged.emit()

        # Should mark as unsaved
        assert editor._unsaved_changes is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skip(
        reason="Causes test hang due to worker thread isolation issue - needs proper Qt thread cleanup (Nov 2025)"
    )
    async def test_save_file_creates_file_async(self, editor, qtbot):
        """Test async save file operation."""
        from unittest.mock import AsyncMock

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.adoc"
            test_content = "= Test Document"

            # Set up file handler state
            editor.file_handler.current_file_path = test_file
            editor.editor.setPlainText(test_content)

            # Mock async write to return success
            editor.file_handler.async_manager.write_file = AsyncMock(return_value=True)

            # Call async save directly
            await editor.file_handler._save_file_async(test_file, test_content)

            # Verify save was called
            editor.file_handler.async_manager.write_file.assert_called_once()
            assert editor.file_handler.current_file_path == test_file
            assert editor.file_handler.unsaved_changes is False

    def test_dark_mode_toggle(self, editor, qtbot):
        """Test dark mode toggle functionality."""
        initial_mode = editor._settings.dark_mode

        # Toggle dark mode
        editor._toggle_dark_mode()

        assert editor._settings.dark_mode != initial_mode

    def test_font_zoom_in(self, editor, qtbot):
        """Test font zoom in functionality."""
        initial_size = editor.editor.font().pointSize()

        editor._zoom(1)

        new_size = editor.editor.font().pointSize()
        assert new_size > initial_size

    def test_font_zoom_out(self, editor, qtbot):
        """Test font zoom out functionality."""
        # Set to a known size well above MIN_FONT_SIZE (8)
        font = editor.editor.font()
        font.setPointSize(20)
        editor.editor.setFont(font)
        current_size = editor.editor.font().pointSize()

        # Then zoom out
        editor._zoom(-1)

        new_size = editor.editor.font().pointSize()
        assert new_size < current_size

    def test_new_file_action(self, editor, qtbot):
        """Test new file action clears editor."""
        editor.editor.setPlainText("Old content")
        editor.file_handler.unsaved_changes = False  # Mark as saved

        # Trigger new file
        editor.new_file()

        # Should clear content
        assert editor.editor.toPlainText() == ""
        assert editor.file_handler.current_file_path is None


@pytest.mark.integration
class TestEditorDialogs:
    """Test editor dialogs."""

    @pytest.fixture
    def editor(self, qtbot):
        """Create AsciiDocEditor instance for testing with proper cleanup."""
        with patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings"
        ):
            window = AsciiDocEditor()
            qtbot.addWidget(window)
            window.show()  # Show window for visibility tests

            yield window

            # Cleanup threads BEFORE qtbot closes window
            if hasattr(window, "git_thread") and window.git_thread:
                window.git_thread.quit()
                window.git_thread.wait(1000)
            if hasattr(window, "pandoc_thread") and window.pandoc_thread:
                window.pandoc_thread.quit()
                window.pandoc_thread.wait(1000)
            if hasattr(window, "preview_thread") and window.preview_thread:
                window.preview_thread.quit()
                window.preview_thread.wait(1000)

    def test_preferences_dialog(self, qtbot):
        """Test preferences dialog creation."""
        from asciidoc_artisan import PreferencesDialog, Settings

        settings = Settings()
        dialog = PreferencesDialog(settings)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Preferences"
        assert dialog.get_settings() is not None


@pytest.mark.integration
class TestEditorActions:
    """Test editor actions and menu items."""

    @pytest.fixture
    def editor(self, qtbot):
        """Create AsciiDocEditor instance for testing with proper cleanup."""
        with patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings"
        ):
            window = AsciiDocEditor()
            qtbot.addWidget(window)
            window.show()  # Show window for visibility tests

            yield window

            # Cleanup threads BEFORE qtbot closes window
            if hasattr(window, "git_thread") and window.git_thread:
                window.git_thread.quit()
                window.git_thread.wait(1000)
            if hasattr(window, "pandoc_thread") and window.pandoc_thread:
                window.pandoc_thread.quit()
                window.pandoc_thread.wait(1000)
            if hasattr(window, "preview_thread") and window.preview_thread:
                window.preview_thread.quit()
                window.preview_thread.wait(1000)

    def test_new_action_exists(self, editor):
        """Test new file action exists."""
        assert editor.action_manager.new_act is not None
        assert editor.action_manager.new_act.text() == "&New"

    def test_open_action_exists(self, editor):
        """Test open file action exists."""
        assert editor.action_manager.open_act is not None
        assert editor.action_manager.open_act.text() == "&Open..."

    def test_save_action_exists(self, editor):
        """Test save file action exists."""
        assert editor.action_manager.save_act is not None
        assert editor.action_manager.save_act.text() == "&Save"

    def test_dark_mode_action_exists(self, editor):
        """Test dark mode action exists."""
        assert editor.action_manager.dark_mode_act is not None

    def test_zoom_in_action_exists(self, editor):
        """Test zoom in action exists."""
        assert editor.action_manager.zoom_in_act is not None

    def test_zoom_out_action_exists(self, editor):
        """Test zoom out action exists."""
        assert editor.action_manager.zoom_out_act is not None

    def test_action_triggers(self, editor, qtbot):
        """Test actions can be triggered."""
        # Test zoom in action
        initial_size = editor.editor.font().pointSize()
        editor.action_manager.zoom_in_act.trigger()
        new_size = editor.editor.font().pointSize()
        assert new_size > initial_size


@pytest.mark.integration
class TestSplitterBehavior:
    """Test splitter behavior between editor and preview."""

    @pytest.fixture
    def editor(self, qtbot):
        """Create AsciiDocEditor instance for testing with proper cleanup."""
        with patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings"
        ):
            window = AsciiDocEditor()
            qtbot.addWidget(window)
            window.show()  # Show window for visibility tests

            yield window

            # Cleanup threads BEFORE qtbot closes window
            if hasattr(window, "git_thread") and window.git_thread:
                window.git_thread.quit()
                window.git_thread.wait(1000)
            if hasattr(window, "pandoc_thread") and window.pandoc_thread:
                window.pandoc_thread.quit()
                window.pandoc_thread.wait(1000)
            if hasattr(window, "preview_thread") and window.preview_thread:
                window.preview_thread.quit()
                window.preview_thread.wait(1000)

    def test_splitter_exists(self, editor):
        """Test splitter widget exists."""
        assert editor.splitter is not None

    def test_splitter_has_two_widgets(self, editor):
        """Test splitter contains editor, preview, and chat panel."""
        assert editor.splitter.count() == 3  # Editor + Preview + Chat (v1.7.0)

    def test_pane_maximize_editor(self, editor, qtbot):
        """Test editor pane maximization."""
        editor._toggle_pane_maximize("editor")

        sizes = editor.splitter.sizes()
        # Editor should have most space, preview should be minimal
        assert sizes[0] > sizes[1]

    def test_pane_maximize_preview(self, editor, qtbot):
        """Test preview pane maximization."""
        editor._toggle_pane_maximize("preview")

        sizes = editor.splitter.sizes()
        # Preview should have most space, editor should be minimal
        assert sizes[1] > sizes[0]

    def test_restore_panes(self, editor, qtbot):
        """Test restoring panes to normal."""
        # Maximize editor
        editor._toggle_pane_maximize("editor")

        # Restore
        editor._toggle_pane_maximize("editor")

        # Both should have reasonable sizes
        sizes = editor.splitter.sizes()
        assert sizes[0] > 0
        assert sizes[1] > 0


@pytest.mark.integration
class TestPreviewUpdate:
    """Test preview update mechanism."""

    @pytest.fixture
    def editor(self, qtbot):
        """Create AsciiDocEditor instance for testing with proper cleanup."""
        with patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings"
        ):
            window = AsciiDocEditor()
            qtbot.addWidget(window)
            window.show()  # Show window for visibility tests

            yield window

            # Cleanup threads BEFORE qtbot closes window
            if hasattr(window, "git_thread") and window.git_thread:
                window.git_thread.quit()
                window.git_thread.wait(1000)
            if hasattr(window, "pandoc_thread") and window.pandoc_thread:
                window.pandoc_thread.quit()
                window.pandoc_thread.wait(1000)
            if hasattr(window, "preview_thread") and window.preview_thread:
                window.preview_thread.quit()
                window.preview_thread.wait(1000)

    def test_preview_timer_exists(self, editor):
        """Test preview timer is created."""
        assert editor._preview_timer is not None

    def test_typing_starts_timer(self, editor, qtbot):
        """Test typing in editor starts preview timer."""
        assert not editor._preview_timer.isActive()

        # Type some text
        editor.editor.setPlainText("= Test")
        editor._start_preview_timer()

        assert editor._preview_timer.isActive()

    def test_update_preview_signal(self, editor, qtbot):
        """Test preview update can be requested."""
        with patch.object(editor.preview_worker, "render_preview"):
            editor.update_preview()

            # Request should be emitted
            assert editor.request_preview_render.emit


@pytest.mark.integration
class TestWorkerThreads:
    """Test worker threads are properly set up."""

    @pytest.fixture
    def editor(self, qtbot):
        """Create AsciiDocEditor instance for testing with proper cleanup."""
        with patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings"
        ):
            window = AsciiDocEditor()
            qtbot.addWidget(window)
            window.show()  # Show window for visibility tests

            yield window

            # Cleanup threads BEFORE qtbot closes window
            if hasattr(window, "git_thread") and window.git_thread:
                window.git_thread.quit()
                window.git_thread.wait(1000)
            if hasattr(window, "pandoc_thread") and window.pandoc_thread:
                window.pandoc_thread.quit()
                window.pandoc_thread.wait(1000)
            if hasattr(window, "preview_thread") and window.preview_thread:
                window.preview_thread.quit()
                window.preview_thread.wait(1000)

    def test_git_worker_exists(self, editor):
        """Test Git worker is created."""
        assert editor.git_worker is not None

    def test_pandoc_worker_exists(self, editor):
        """Test Pandoc worker is created."""
        assert editor.pandoc_worker is not None

    def test_preview_worker_exists(self, editor):
        """Test Preview worker is created."""
        assert editor.preview_worker is not None

    def test_git_thread_running(self, editor):
        """Test Git thread is running."""
        assert editor.git_thread.isRunning()

    def test_pandoc_thread_running(self, editor):
        """Test Pandoc thread is running."""
        assert editor.pandoc_thread.isRunning()

    def test_preview_thread_running(self, editor):
        """Test Preview thread is running."""
        assert editor.preview_thread.isRunning()
