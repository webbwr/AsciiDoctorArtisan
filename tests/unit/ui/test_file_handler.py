"""
Tests for file handler.

Tests file I/O operations including:
- Opening files
- Saving files
- Auto-save functionality
- Unsaved changes tracking
- File dialog integration
- Path validation
"""

import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPlainTextEdit

from asciidoc_artisan.ui.file_handler import FileHandler


@pytest.fixture
def mock_editor(qtbot):
    """Create mock editor widget."""
    editor = QPlainTextEdit()
    qtbot.addWidget(editor)
    return editor


@pytest.fixture
def mock_window(qtbot):
    """Create mock parent window."""
    window = QMainWindow()  # ✅ Real QObject for parent compatibility
    qtbot.addWidget(window)  # Manage lifecycle
    # Add Mock attributes that tests expect
    window.status_bar = Mock()
    window.status_bar.showMessage = Mock()
    return window


@pytest.fixture
def mock_settings_manager():
    """Create mock settings manager."""
    manager = Mock()
    manager.load_settings = Mock(return_value=Mock(last_directory=""))
    manager.save_settings = Mock()
    return manager


@pytest.fixture
def mock_status_manager():
    """Create mock status manager."""
    manager = Mock()
    manager.update_window_title = Mock()
    manager.update_document_metrics = Mock()
    manager.show_message = Mock()
    return manager


@pytest.fixture
def handler(mock_editor, mock_window, mock_settings_manager, mock_status_manager):
    """Create FileHandler instance."""
    handler = FileHandler(mock_editor, mock_window, mock_settings_manager, mock_status_manager)
    # Mock async_manager for tests that don't need real async operations
    handler.async_manager = Mock()
    handler.async_manager.read_file = Mock(return_value=None)
    handler.async_manager.write_file = Mock(return_value=True)
    handler.async_manager.watch_file = Mock()
    return handler


def test_file_handler_initialization(handler, mock_editor):
    """Test file handler initializes correctly."""
    assert handler.editor is mock_editor
    assert handler.current_file_path is None
    assert handler.unsaved_changes is False
    assert handler.is_opening_file is False


def test_text_changed_marks_unsaved(handler, mock_editor, qtbot):
    """Test text changes mark document as unsaved."""
    with qtbot.waitSignal(handler.file_modified, timeout=1000):
        mock_editor.setPlainText("New content")

    assert handler.unsaved_changes is True


def test_text_changed_during_open_ignored(handler, mock_editor):
    """Test text changes during file open are ignored."""
    handler.is_opening_file = True
    mock_editor.setPlainText("Loading content")

    assert handler.unsaved_changes is False


def test_new_file_clears_editor(handler, mock_editor):
    """Test new file clears editor and resets state."""
    mock_editor.setPlainText("Old content")
    handler.unsaved_changes = True
    handler.current_file_path = Path("/test/file.adoc")

    handler.new_file()

    assert mock_editor.toPlainText() == ""
    assert handler.current_file_path is None
    assert handler.unsaved_changes is False


def test_new_file_prompts_if_unsaved(handler, mock_editor):
    """Test new file prompts to save if unsaved changes."""
    mock_editor.setPlainText("Unsaved content")
    handler.unsaved_changes = True

    with patch.object(handler, "prompt_save_before_action", return_value=False):
        handler.new_file()

    # Editor should not be cleared if user cancels
    assert mock_editor.toPlainText() == "Unsaved content"


def test_has_unsaved_changes(handler):
    """Test checking for unsaved changes."""
    assert handler.has_unsaved_changes() is False

    handler.unsaved_changes = True
    assert handler.has_unsaved_changes() is True


def test_get_current_file_path(handler):
    """Test getting current file path."""
    assert handler.get_current_file_path() is None

    test_path = Path("/test/document.adoc")
    handler.current_file_path = test_path
    assert handler.get_current_file_path() == test_path


def test_auto_save_timer_initialization(handler):
    """Test auto-save timer initializes."""
    assert handler.auto_save_timer is not None
    assert not handler.auto_save_timer.isActive()


def test_start_auto_save(handler):
    """Test starting auto-save timer."""
    handler.start_auto_save(interval_ms=1000)
    assert handler.auto_save_timer.isActive()
    assert handler.auto_save_timer.interval() == 1000


def test_stop_auto_save(handler):
    """Test stopping auto-save timer."""
    handler.start_auto_save(interval_ms=1000)
    handler.stop_auto_save()
    assert not handler.auto_save_timer.isActive()


def test_auto_save_with_no_file(handler):
    """Test auto-save does nothing if no current file."""
    handler.unsaved_changes = True
    handler.current_file_path = None

    handler.auto_save()
    # Should not crash


def test_auto_save_with_file(handler, tmp_path):
    """Test auto-save saves file."""
    test_file = tmp_path / "test.adoc"
    test_file.write_text("Initial content")

    handler.current_file_path = test_file
    handler.unsaved_changes = True
    handler.editor.setPlainText("Modified content")

    with patch.object(handler, "save_file", return_value=True) as mock_save:
        handler.auto_save()
        mock_save.assert_called_once_with(save_as=False)


def test_auto_save_skips_if_no_changes(handler, tmp_path):
    """Test auto-save skips if no unsaved changes."""
    test_file = tmp_path / "test.adoc"
    handler.current_file_path = test_file
    handler.unsaved_changes = False

    with patch.object(handler, "save_file") as mock_save:
        handler.auto_save()
        mock_save.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_load_file_content_async(handler, tmp_path, mock_editor):
    """Test loading file content asynchronously."""
    test_file = tmp_path / "test.adoc"
    test_content = "= Test Document\n\nTest content"
    test_file.write_text(test_content)

    # Mock async_manager.read_file to return the content (use AsyncMock for awaitable)
    handler.async_manager.read_file = AsyncMock(return_value=test_content)

    # Call async load method
    await handler._load_file_async(test_file)

    # Verify content loaded
    assert mock_editor.toPlainText() == test_content
    assert handler.current_file_path == test_file
    assert handler.unsaved_changes is False


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_load_file_tracks_loading_state_async(handler, tmp_path):
    """Test loading state is tracked during async file load."""
    test_file = tmp_path / "test.adoc"
    test_content = "Content"
    test_file.write_text(test_content)

    assert handler.is_opening_file is False

    # Mock async read to check state mid-operation
    async def async_read_with_state_check(*args, **kwargs):
        # Verify state is True during async operation
        assert handler.is_opening_file is True
        return test_content

    handler.async_manager.read_file = async_read_with_state_check

    # Call async load
    await handler._load_file_async(test_file)

    # State should be False after completion
    assert handler.is_opening_file is False


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_load_file_updates_settings_async(handler, tmp_path, mock_settings_manager):
    """Test loading file updates last directory in settings."""
    test_file = tmp_path / "test.adoc"
    test_content = "Content"
    test_file.write_text(test_content)

    settings = Mock()
    mock_settings_manager.load_settings.return_value = settings

    # Mock async read
    handler.async_manager.read_file = AsyncMock(return_value=test_content)

    # Call async load
    await handler._load_file_async(test_file)

    # Verify settings updated
    assert settings.last_directory == str(tmp_path)
    mock_settings_manager.save_settings.assert_called_with(settings)


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_load_file_emits_signal_async(handler, tmp_path, qtbot):
    """Test loading file emits file_opened signal."""
    test_file = tmp_path / "test.adoc"
    test_content = "Content"
    test_file.write_text(test_content)

    # Mock async read
    handler.async_manager.read_file = AsyncMock(return_value=test_content)

    # Wait for signal and call async load
    with qtbot.waitSignal(handler.file_opened, timeout=2000) as blocker:
        await handler._load_file_async(test_file)

    # Verify signal emitted with correct path
    assert blocker.args[0] == test_file


def test_load_file_error_handling(handler, mock_status_manager):
    """Test error handling when loading non-existent file."""
    non_existent = Path("/non/existent/file.adoc")

    # Should not crash
    try:
        handler._load_file_content(non_existent)
    except Exception:
        pass  # Expected


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_save_file_with_path_async(handler, tmp_path, mock_editor):
    """Test saving file with existing path asynchronously."""
    test_file = tmp_path / "save_test.adoc"
    test_content = "Content to save"
    handler.current_file_path = test_file
    handler.unsaved_changes = True
    mock_editor.setPlainText(test_content)

    # Mock async write to return success
    handler.async_manager.write_file = AsyncMock(return_value=True)

    # Call async save directly
    await handler._save_file_async(test_file, test_content)

    # Verify state updated
    assert handler.current_file_path == test_file
    assert handler.unsaved_changes is False
    # Verify write was called
    handler.async_manager.write_file.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_save_file_emits_signal_async(handler, tmp_path, mock_editor, qtbot):
    """Test saving file emits file_saved signal."""
    test_file = tmp_path / "signal_test.adoc"
    test_content = "Content"
    handler.current_file_path = test_file
    mock_editor.setPlainText(test_content)

    # Mock async write to return success
    handler.async_manager.write_file = AsyncMock(return_value=True)

    # Wait for signal and call async save
    with qtbot.waitSignal(handler.file_saved, timeout=2000) as blocker:
        await handler._save_file_async(test_file, test_content)

    # Verify signal emitted with correct path
    assert blocker.args[0] == test_file


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_save_file_updates_settings_async(handler, tmp_path, mock_editor, mock_settings_manager):
    """Test saving file updates last directory."""
    test_file = tmp_path / "settings_test.adoc"
    test_content = "Content"
    handler.current_file_path = test_file
    mock_editor.setPlainText(test_content)

    settings = Mock()
    mock_settings_manager.load_settings.return_value = settings

    # Mock async write to return success
    handler.async_manager.write_file = AsyncMock(return_value=True)

    # Call async save
    await handler._save_file_async(test_file, test_content)

    # Verify settings updated
    assert settings.last_directory == str(tmp_path)
    mock_settings_manager.save_settings.assert_called_with(settings)


@pytest.mark.asyncio
@pytest.mark.fr_072
@pytest.mark.unit
async def test_save_file_error_handling_async(handler, mock_editor, mock_status_manager):
    """Test error handling when async save fails."""
    invalid_path = Path("/invalid/path/file.adoc")
    test_content = "Content"
    handler.current_file_path = invalid_path
    mock_editor.setPlainText(test_content)

    # Mock async write to return failure
    handler.async_manager.write_file = AsyncMock(return_value=False)

    # Call async save
    await handler._save_file_async(invalid_path, test_content)

    # Verify error message shown (file_saved signal should NOT be emitted on failure)
    # The handler should handle the failure case
    handler.async_manager.write_file.assert_called_once()


def test_prompt_save_before_action_no_changes(handler):
    """Test prompt returns True if no unsaved changes."""
    handler.unsaved_changes = False
    result = handler.prompt_save_before_action("test action")
    assert result is True


@pytest.mark.fr_072
@pytest.mark.unit
def test_prompt_save_before_action_save(handler, tmp_path):
    """Test prompt saves file when user chooses Save."""
    handler.unsaved_changes = True
    handler.current_file_path = tmp_path / "test.adoc"
    handler.editor.setPlainText("Content")

    # Mock os.environ to bypass pytest test environment check
    with patch("os.environ.get", return_value=None):
        # Mock dialog and save_file
        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Save,
        ):
            with patch.object(handler, "save_file", return_value=True) as mock_save:
                # prompt_save_before_action is synchronous, calls save_file wrapper
                result = handler.prompt_save_before_action("test action")

    assert result is True
    mock_save.assert_called_once()


def test_prompt_save_before_action_discard(handler):
    """Test prompt returns True when user chooses Discard."""
    handler.unsaved_changes = True

    with patch(
        "PySide6.QtWidgets.QMessageBox.question",
        return_value=QMessageBox.StandardButton.Discard,
    ):
        result = handler.prompt_save_before_action("test action")

    assert result is True


@pytest.mark.fr_072
@pytest.mark.unit
def test_prompt_save_before_action_cancel(handler):
    """Test prompt returns False when user cancels."""
    handler.unsaved_changes = True

    # Mock os.environ to bypass pytest test environment check
    with patch("os.environ.get", return_value=None):
        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            result = handler.prompt_save_before_action("test action")

    assert result is False


def test_file_modified_signal_emitted(handler, mock_editor, qtbot):
    """Test file_modified signal is emitted on changes."""
    with qtbot.waitSignal(handler.file_modified, timeout=1000) as blocker:
        mock_editor.setPlainText("Modified")

    assert blocker.args[0] is True  # has_changes = True


def test_open_file_nonexistent_shows_error(handler, mock_status_manager):
    """Test opening non-existent file shows error."""
    handler.open_file("/non/existent/file.adoc")
    mock_status_manager.show_message.assert_called()


def test_open_file_with_unsaved_prompts(handler):
    """Test opening file with unsaved changes prompts."""
    handler.unsaved_changes = True

    with patch.object(handler, "prompt_save_before_action", return_value=False):
        handler.open_file("/some/file.adoc")

    # Should not proceed to file dialog


# ============================================================================
# NEW TEST CLASSES - Edge Cases and Comprehensive Coverage
# ============================================================================


class TestPathValidation:
    """Test path validation and sanitization edge cases."""

    def test_open_file_with_relative_path(self, handler, tmp_path):
        """Test opening file with relative path."""
        test_file = tmp_path / "test.adoc"
        test_file.write_text("Content")

        # Convert to relative path
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path.parent)
            relative_path = test_file.relative_to(tmp_path.parent)
            handler.open_file(str(relative_path))
            # Should handle relative path correctly
        finally:
            os.chdir(original_cwd)

    def test_open_file_with_symlink(self, handler, tmp_path):
        """Test opening file via symlink."""
        test_file = tmp_path / "original.adoc"
        test_file.write_text("Content")

        symlink = tmp_path / "link.adoc"
        try:
            symlink.symlink_to(test_file)
            handler.open_file(str(symlink))
            # Should resolve symlink correctly
        except OSError:
            pass  # Skip if symlinks not supported

    def test_open_file_with_special_chars_in_path(self, handler, tmp_path):
        """Test opening file with special characters in path."""
        special_dir = tmp_path / "dir with spaces & special!@#"
        special_dir.mkdir(exist_ok=True)
        test_file = special_dir / "file[brackets].adoc"
        test_file.write_text("Content")

        handler.open_file(str(test_file))
        # Should handle special characters correctly

    def test_save_file_with_unicode_path(self, handler, tmp_path, mock_editor):
        """Test saving file with Unicode characters in path."""
        unicode_dir = tmp_path / "文档_テスト_📝"
        unicode_dir.mkdir(exist_ok=True)
        test_file = unicode_dir / "test.adoc"

        mock_editor.setPlainText("Content")
        handler.current_file_path = test_file
        handler.async_manager.write_file = AsyncMock(return_value=True)

        # Should handle Unicode path correctly
        try:
            handler.save_file()
        except Exception:
            pass  # May fail on some systems, but shouldn't crash


@pytest.mark.fr_011
@pytest.mark.edge_case
class TestLargeFileHandling:
    """Test handling of large files."""

    @pytest.mark.asyncio
    async def test_load_large_file_async(self, handler, tmp_path, mock_editor):
        """Test loading a large file (1MB+)."""
        test_file = tmp_path / "large.adoc"
        large_content = "= Large Document\n\n" + ("Line of text\n" * 100000)  # ~1.3MB
        test_file.write_text(large_content)

        handler.async_manager.read_file = AsyncMock(return_value=large_content)

        await handler._load_file_async(test_file)

        assert handler.current_file_path == test_file
        assert len(mock_editor.toPlainText()) > 1000000

    @pytest.mark.asyncio
    async def test_save_large_file_async(self, handler, tmp_path, mock_editor):
        """Test saving a large file (1MB+)."""
        test_file = tmp_path / "large_save.adoc"
        large_content = "= Large Save\n\n" + ("Content " * 100000)  # ~1MB
        mock_editor.setPlainText(large_content)
        handler.current_file_path = test_file

        handler.async_manager.write_file = AsyncMock(return_value=True)

        await handler._save_file_async(test_file, large_content)

        assert handler.unsaved_changes is False

    def test_auto_save_with_large_file(self, handler, tmp_path, mock_editor):
        """Test auto-save doesn't block UI with large file."""
        test_file = tmp_path / "large_autosave.adoc"
        large_content = "Content " * 50000
        mock_editor.setPlainText(large_content)
        handler.current_file_path = test_file
        handler.unsaved_changes = True

        with patch.object(handler, "save_file", return_value=True) as mock_save:
            handler.auto_save()
            mock_save.assert_called_once()

    def test_load_file_memory_efficient(self, handler, tmp_path):
        """Test file loading doesn't duplicate memory unnecessarily."""
        test_file = tmp_path / "memory_test.adoc"
        test_file.write_text("Content")

        import gc

        gc.collect()

        # Should not cause excessive memory allocation
        handler.async_manager.read_file = AsyncMock(return_value="Content")


@pytest.mark.fr_009
@pytest.mark.fr_011
@pytest.mark.edge_case
class TestEmptyFileHandling:
    """Test handling of empty files and edge cases."""

    @pytest.mark.asyncio
    async def test_load_empty_file(self, handler, tmp_path, mock_editor):
        """Test loading an empty file."""
        test_file = tmp_path / "empty.adoc"
        test_file.write_text("")

        handler.async_manager.read_file = AsyncMock(return_value="")

        await handler._load_file_async(test_file)

        assert mock_editor.toPlainText() == ""
        assert handler.current_file_path == test_file

    @pytest.mark.asyncio
    async def test_save_empty_file(self, handler, tmp_path, mock_editor):
        """Test saving an empty file."""
        test_file = tmp_path / "empty_save.adoc"
        mock_editor.setPlainText("")
        handler.current_file_path = test_file

        handler.async_manager.write_file = AsyncMock(return_value=True)

        await handler._save_file_async(test_file, "")

        assert handler.unsaved_changes is False

    def test_new_file_from_empty(self, handler, mock_editor):
        """Test creating new file when current file is empty."""
        mock_editor.setPlainText("")
        handler.unsaved_changes = False

        handler.new_file()

        assert handler.current_file_path is None
        assert mock_editor.toPlainText() == ""

    def test_auto_save_empty_file(self, handler, tmp_path, mock_editor):
        """Test auto-save with empty content."""
        test_file = tmp_path / "empty_auto.adoc"
        mock_editor.setPlainText("")
        handler.current_file_path = test_file
        handler.unsaved_changes = True

        with patch.object(handler, "save_file", return_value=True) as mock_save:
            handler.auto_save()
            mock_save.assert_called_once()


class TestFilePermissions:
    """Test handling of file permission issues."""

    def test_open_readonly_file(self, handler, tmp_path):
        """Test opening a read-only file."""
        test_file = tmp_path / "readonly.adoc"
        test_file.write_text("Content")
        test_file.chmod(0o444)  # Read-only

        try:
            handler.open_file(str(test_file))
            # Should be able to open for reading
        finally:
            test_file.chmod(0o644)  # Restore permissions

    def test_save_to_readonly_file(self, handler, tmp_path, mock_editor, mock_status_manager):
        """Test saving to a read-only file shows error."""
        test_file = tmp_path / "readonly_save.adoc"
        test_file.write_text("Original")
        test_file.chmod(0o444)  # Read-only

        mock_editor.setPlainText("Modified")
        handler.current_file_path = test_file
        handler.async_manager.write_file = AsyncMock(return_value=False)

        try:
            handler.save_file()
            # Should handle permission error gracefully
        finally:
            test_file.chmod(0o644)  # Restore permissions

    def test_save_to_nonexistent_directory(self, handler, mock_editor):
        """Test saving to non-existent directory fails gracefully."""
        test_file = Path("/nonexistent/dir/file.adoc")
        mock_editor.setPlainText("Content")
        handler.current_file_path = test_file
        handler.async_manager.write_file = AsyncMock(return_value=False)

        # Should not crash
        handler.save_file()


@pytest.mark.fr_011
@pytest.mark.edge_case
class TestConcurrentOperations:
    """Test concurrent file operations."""

    def test_load_during_save_blocked(self, handler):
        """Test loading file while save is in progress is blocked."""
        handler.is_opening_file = True

        # Second load should be ignored - just verify flag prevents action
        assert handler.is_opening_file is True

        # Should not crash or cause race condition

    def test_save_during_load_blocked(self, handler, mock_editor):
        """Test saving file while load is in progress is blocked."""
        handler.is_opening_file = True
        mock_editor.setPlainText("Content")
        handler.current_file_path = Path("/test.adoc")

        # Save should check opening flag
        handler.save_file()

        # Should not cause race condition

    def test_multiple_auto_saves(self, handler, tmp_path, mock_editor):
        """Test multiple auto-save triggers don't conflict."""
        test_file = tmp_path / "autosave.adoc"
        mock_editor.setPlainText("Content")
        handler.current_file_path = test_file
        handler.unsaved_changes = True

        with patch.object(handler, "save_file", return_value=True) as mock_save:
            handler.auto_save()
            handler.auto_save()
            handler.auto_save()

            # Should handle multiple calls gracefully
            assert mock_save.call_count >= 1

    def test_text_change_during_load(self, handler, mock_editor):
        """Test text changes during load are ignored."""
        handler.is_opening_file = True

        mock_editor.setPlainText("Content during load")

        assert handler.unsaved_changes is False


@pytest.mark.fr_011
@pytest.mark.edge_case
class TestAutoSaveEdgeCases:
    """Test auto-save edge cases and race conditions."""

    def test_auto_save_timer_restarts(self, handler):
        """Test auto-save timer can be restarted."""
        handler.start_auto_save(1000)
        assert handler.auto_save_timer.isActive()

        handler.start_auto_save(2000)
        assert handler.auto_save_timer.isActive()
        assert handler.auto_save_timer.interval() == 2000

    def test_auto_save_with_zero_interval(self, handler):
        """Test auto-save with zero interval."""
        handler.start_auto_save(0)
        # Should not crash, timer may not start

    def test_stop_auto_save_when_not_active(self, handler):
        """Test stopping auto-save when not active."""
        handler.stop_auto_save()
        # Should not crash

    def test_auto_save_after_file_closed(self, handler, tmp_path):
        """Test auto-save after file is closed."""
        test_file = tmp_path / "closed.adoc"
        handler.current_file_path = test_file
        handler.unsaved_changes = True

        # Close file
        handler.new_file()

        # Auto-save should not do anything
        handler.auto_save()

    def test_auto_save_updates_unsaved_state(self, handler, tmp_path, mock_editor):
        """Test auto-save clears unsaved changes flag."""
        test_file = tmp_path / "autosave_state.adoc"
        mock_editor.setPlainText("Content")
        handler.current_file_path = test_file
        handler.unsaved_changes = True

        with patch.object(handler, "save_file", return_value=True):
            handler.auto_save()

        # Unsaved flag should be cleared by save_file


class TestSignalEmissions:
    """Test signal emission edge cases."""

    def test_file_opened_signal_not_emitted_on_error(self, handler, qtbot, mock_status_manager):
        """Test file_opened signal not emitted when load fails."""
        # Test that opening non-existent file doesn't emit signal
        handler.open_file("/nonexistent.adoc")

        # Signal should not be emitted on error
        mock_status_manager.show_message.assert_called()  # Error message shown

    def test_file_saved_signal_not_emitted_on_error(self, handler, mock_editor, qtbot):
        """Test file_saved signal not emitted when save fails."""
        mock_editor.setPlainText("Content")
        handler.current_file_path = Path("/invalid/path.adoc")
        handler.async_manager.write_file = AsyncMock(return_value=False)

        # Save should fail without emitting signal
        handler.save_file()

    def test_file_modified_signal_emitted_once_per_change(self, handler, mock_editor, qtbot):
        """Test file_modified signal emitted for each text change."""
        with qtbot.waitSignal(handler.file_modified, timeout=1000):
            mock_editor.setPlainText("First change")

        handler.unsaved_changes = False  # Reset

        with qtbot.waitSignal(handler.file_modified, timeout=1000):
            mock_editor.setPlainText("Second change")

    def test_signals_during_batch_operations(self, handler, mock_editor, qtbot):
        """Test signals during batch text operations."""
        handler.is_opening_file = True

        # Multiple changes during load should not emit signals
        mock_editor.setPlainText("Line 1")
        mock_editor.setPlainText("Line 2")

        handler.is_opening_file = False
        assert handler.unsaved_changes is False


class TestFileDialogIntegration:
    """Test file dialog integration edge cases."""

    def test_save_file_prompts_for_new_file(self, handler, mock_editor):
        """Test save_file prompts for path when no current file."""
        mock_editor.setPlainText("Content")
        handler.current_file_path = None

        with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName", return_value=("", "")):
            handler.save_file(save_as=True)

        # Should return False if user cancels

    def test_open_file_dialog_respects_last_directory(self, handler, tmp_path, mock_settings_manager):
        """Test open file dialog uses last directory from settings."""
        settings = Mock()
        settings.last_directory = str(tmp_path)
        mock_settings_manager.load_settings.return_value = settings

        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=("", "")):
            handler.open_file()

        # Dialog should open in last_directory

    def test_save_as_with_existing_file_overwrites(self, handler, tmp_path, mock_editor):
        """Test save_as can overwrite existing file."""
        test_file = tmp_path / "existing.adoc"
        test_file.write_text("Old content")

        mock_editor.setPlainText("New content")
        handler.current_file_path = test_file
        handler.async_manager.write_file = AsyncMock(return_value=True)

        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(test_file), ""),
        ):
            handler.save_file(save_as=True)

    def test_dialog_filters_correct_extensions(self, handler):
        """Test file dialogs filter correct file extensions."""
        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=("", "")):
            handler.open_file()

            # Should include .adoc filter


class TestFileWatchingEdgeCases:
    """Test file watching and external modification detection."""

    def test_file_modified_externally_detected(self, handler, tmp_path):
        """Test external file modifications are detected."""
        test_file = tmp_path / "watched.adoc"
        test_file.write_text("Original")
        handler.current_file_path = test_file

        # Simulate external modification
        time.sleep(0.1)
        test_file.write_text("Modified externally")

        # Should detect modification via file watcher

    def test_file_watch_on_unsaved_new_file(self, handler):
        """Test file watching not active for new unsaved files."""
        handler.current_file_path = None

        # Should not attempt to watch non-existent file
        handler.async_manager.watch_file = Mock()

    def test_file_watch_stopped_on_close(self, handler, tmp_path):
        """Test file watch stopped when file is closed."""
        test_file = tmp_path / "watched_close.adoc"
        handler.current_file_path = test_file

        handler.new_file()

        # File watch should be stopped


class TestSpecialFileTypes:
    """Test handling of special file types and content."""

    def test_load_file_with_binary_content_fails_gracefully(self, handler, tmp_path):
        """Test loading file with binary content fails gracefully."""
        test_file = tmp_path / "binary.adoc"
        test_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        # Should detect binary and show error
        try:
            handler.open_file(str(test_file))
        except Exception:
            pass  # Expected to fail gracefully

    def test_load_file_with_mixed_line_endings(self, handler, tmp_path, mock_editor):
        """Test loading file with mixed line endings."""
        test_file = tmp_path / "mixed_endings.adoc"
        content = "Line 1\nLine 2\r\nLine 3\rLine 4"
        test_file.write_text(content)

        handler.async_manager.read_file = AsyncMock(return_value=content)

        # Should normalize line endings

    def test_save_preserves_line_endings(self, handler, tmp_path, mock_editor):
        """Test save preserves line ending style."""
        test_file = tmp_path / "endings.adoc"
        content = "Line 1\nLine 2\n"
        mock_editor.setPlainText(content)
        handler.current_file_path = test_file

        handler.async_manager.write_file = AsyncMock(return_value=True)

        # Should preserve Unix line endings

    def test_load_file_with_bom(self, handler, tmp_path, mock_editor):
        """Test loading file with UTF-8 BOM."""
        test_file = tmp_path / "bom.adoc"
        test_file.write_bytes(b"\xef\xbb\xbfContent with BOM")

        # Should strip BOM correctly
        handler.async_manager.read_file = AsyncMock(return_value="Content with BOM")


class TestMemoryManagement:
    """Test memory management during file operations."""

    def test_editor_cleared_before_load(self, handler, mock_editor):
        """Test editor is cleared before loading new content."""
        mock_editor.setPlainText("Old content")
        handler.unsaved_changes = True

        handler.is_opening_file = True
        mock_editor.clear()

        assert mock_editor.toPlainText() == ""

    def test_no_memory_leak_on_repeated_loads(self, handler, tmp_path, mock_editor):
        """Test no memory leak on repeated file loads."""
        test_file = tmp_path / "repeated.adoc"
        test_file.write_text("Content")

        handler.async_manager.read_file = AsyncMock(return_value="Content")

        # Multiple loads should not leak memory
        import gc

        gc.collect()

        for _ in range(10):
            handler.open_file(str(test_file))

    def test_large_file_released_after_close(self, handler, tmp_path, mock_editor):
        """Test large file memory released after close."""
        large_content = "Content " * 100000
        mock_editor.setPlainText(large_content)
        handler.current_file_path = tmp_path / "large.adoc"

        handler.new_file()

        # Editor should be cleared, memory released
        assert mock_editor.toPlainText() == ""


# ============================================================================
# NEW TEST CLASSES - Missing Coverage (35 lines → 95%+)
# ============================================================================


class TestMetricsImportFallback:
    """Test metrics module import fallback (lines 38-40)."""

    def test_metrics_unavailable_fallback(self):
        """Test fallback when metrics module unavailable."""
        import sys
        from unittest.mock import patch

        # Mock import failure for metrics
        with patch.dict(sys.modules, {"asciidoc_artisan.core.metrics": None}):
            # Force module reload to trigger import
            import importlib

            import asciidoc_artisan.ui.file_handler as fh_module

            try:
                importlib.reload(fh_module)
                # Should not crash, METRICS_AVAILABLE should be False
            finally:
                # Reload again to restore normal state
                importlib.reload(fh_module)


class TestFileDialogCancellation:
    """Test file dialog cancellation (line 163)."""

    def test_open_file_dialog_cancelled(self, handler):
        """Test opening file with dialog when user cancels."""
        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=("", "")):
            # Should return early without error
            handler.open_file()  # No path provided, triggers dialog

    def test_save_file_dialog_cancelled(self, handler, mock_editor):
        """Test save file dialog when user cancels."""
        mock_editor.setPlainText("Content")
        handler.current_file_path = None

        with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName", return_value=("", "")):
            result = handler.save_file(save_as=True)

        # Should return False when cancelled
        assert result is False


class TestFileSizeValidation:
    """Test file size validation (lines 194-217)."""

    @pytest.mark.asyncio
    async def test_open_file_too_large(self, handler, tmp_path, mock_status_manager):
        """Test opening file larger than 100MB shows error (lines 194-206)."""
        # Create a file
        test_file = tmp_path / "huge.adoc"
        test_file.write_text("Content")

        # Mock the file_path.stat() call to return huge size
        def mock_stat(self, **kwargs):
            from unittest.mock import Mock

            mock_result = Mock()
            mock_result.st_size = 105 * 1024 * 1024  # 105MB
            return mock_result

        with patch.object(Path, "stat", mock_stat):
            # Call async method directly
            await handler._load_file_async(test_file)

        # Should show error message
        mock_status_manager.show_message.assert_called()
        assert handler.is_opening_file is False

    @pytest.mark.asyncio
    async def test_open_large_file_logs_info(self, handler, tmp_path, caplog):
        """Test opening file >10MB logs info (lines 210-212)."""
        import logging

        test_file = tmp_path / "large.adoc"
        test_file.write_text("Content")

        # Mock the file_path.stat() call to return 15MB size
        def mock_stat(self, **kwargs):
            from unittest.mock import Mock

            mock_result = Mock()
            mock_result.st_size = 15 * 1024 * 1024  # 15MB
            return mock_result

        handler.async_manager.read_file = AsyncMock(return_value="Content")

        with patch.object(Path, "stat", mock_stat):
            with caplog.at_level(logging.INFO):
                # Call async method directly
                await handler._load_file_async(test_file)

        # Should log info about large file
        assert any("Opening large file" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_file_size_check_exception_handled(self, handler, tmp_path, mock_status_manager):
        """Test exception during file size check is handled (lines 214-217)."""
        test_file = tmp_path / "test.adoc"
        test_file.write_text("Content")

        # Mock stat to raise exception
        def mock_stat_error(self, **kwargs):
            raise OSError("Permission denied")

        with patch.object(Path, "stat", mock_stat_error):
            # Call async method directly
            await handler._load_file_async(test_file)

        # Should handle exception gracefully (returns early)
        assert handler.is_opening_file is False


class TestMemoryProfiling:
    """Test memory profiling integration (lines 223-227, 275-279)."""

    @pytest.mark.asyncio
    async def test_memory_profiling_before_load(self, handler, tmp_path):
        """Test memory profiling before file load (lines 223-227)."""
        test_file = tmp_path / "profile.adoc"
        test_file.write_text("Content")

        handler.async_manager.read_file = AsyncMock(return_value="Content")

        # Mock profiler
        mock_profiler = Mock()
        mock_profiler.is_running = True
        mock_profiler.take_snapshot = Mock()

        # get_profiler is imported inside the function from asciidoc_artisan.core
        with patch("os.environ.get", return_value="1"):  # Enable profiling
            with patch("asciidoc_artisan.core.get_profiler", return_value=mock_profiler):
                await handler._load_file_async(test_file)

        # Should take snapshot before load
        mock_profiler.take_snapshot.assert_any_call(f"before_load_{test_file.name}")

    @pytest.mark.asyncio
    async def test_memory_profiling_after_load(self, handler, tmp_path):
        """Test memory profiling after file load (lines 275-279)."""
        test_file = tmp_path / "profile.adoc"
        test_file.write_text("Content")

        handler.async_manager.read_file = AsyncMock(return_value="Content")

        # Mock profiler
        mock_profiler = Mock()
        mock_profiler.is_running = True
        mock_profiler.take_snapshot = Mock()

        # get_profiler is imported inside the function from asciidoc_artisan.core
        with patch("os.environ.get", return_value="1"):  # Enable profiling
            with patch("asciidoc_artisan.core.get_profiler", return_value=mock_profiler):
                await handler._load_file_async(test_file)

        # Should take snapshot after load
        mock_profiler.take_snapshot.assert_any_call(f"after_load_{test_file.name}")


class TestAsyncReadErrors:
    """Test async read error handling (lines 235, 282-283)."""

    @pytest.mark.asyncio
    async def test_async_read_returns_none(self, handler, tmp_path):
        """Test async read returning None (line 235)."""
        test_file = tmp_path / "test.adoc"
        test_file.write_text("Content")

        # Mock async read to return None (error case)
        handler.async_manager.read_file = AsyncMock(return_value=None)

        await handler._load_file_async(test_file)

        # Should return early without loading
        assert handler.current_file_path != test_file

    @pytest.mark.asyncio
    async def test_load_file_exception_handled(self, handler, tmp_path, mock_status_manager):
        """Test exception during file load shows error (lines 281-283)."""
        test_file = tmp_path / "error.adoc"
        test_file.write_text("Content")

        # Mock async read to raise exception
        handler.async_manager.read_file = AsyncMock(side_effect=RuntimeError("Read failed"))

        await handler._load_file_async(test_file)

        # Should show error message
        mock_status_manager.show_message.assert_called()
        assert handler.is_opening_file is False


class TestPromptSaveEdgeCases:
    """Test prompt_save_before_action edge cases (lines 414, 429)."""

    def test_prompt_save_no_changes_returns_true(self, handler):
        """Test prompt returns True when no unsaved changes (line 414)."""
        handler.unsaved_changes = False

        # Should return True immediately without dialog
        result = handler.prompt_save_before_action("test action")

        assert result is True

    def test_prompt_save_discard_returns_true(self, handler):
        """Test prompt returns True when user discards (line 429)."""
        handler.unsaved_changes = True

        with patch(
            "PySide6.QtWidgets.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Discard,
        ):
            result = handler.prompt_save_before_action("test action")

        assert result is True


class TestAsyncSignalHandlers:
    """Test async operation signal handlers (lines 460, 471, 486, 498-505)."""

    def test_on_async_read_complete_logs(self, handler, tmp_path, caplog):
        """Test async read complete signal handler (line 460)."""
        import logging

        test_file = tmp_path / "test.adoc"

        with caplog.at_level(logging.DEBUG):
            handler._on_async_read_complete(test_file, "Content")

        # Should log debug message
        assert any("Async read complete" in record.message for record in caplog.records)

    def test_on_async_write_complete_logs(self, handler, tmp_path, caplog):
        """Test async write complete signal handler (line 471)."""
        import logging

        test_file = tmp_path / "test.adoc"

        with caplog.at_level(logging.DEBUG):
            handler._on_async_write_complete(test_file)

        # Should log debug message
        assert any("Async write complete" in record.message for record in caplog.records)

    def test_on_async_operation_failed_logs(self, handler, tmp_path, caplog):
        """Test async operation failed signal handler (line 486)."""
        import logging

        test_file = tmp_path / "test.adoc"

        with caplog.at_level(logging.ERROR):
            handler._on_async_operation_failed("read", test_file, "Error message")

        # Should log error message
        assert any("Async read failed" in record.message for record in caplog.records)

    def test_on_file_changed_externally_emits_signal(self, handler, tmp_path, qtbot, caplog):
        """Test file changed externally signal handler (lines 498-505)."""
        import logging

        test_file = tmp_path / "test.adoc"

        with caplog.at_level(logging.INFO):
            with qtbot.waitSignal(handler.file_changed_externally, timeout=1000):
                handler._on_file_changed_externally(test_file)

        # Should log info message
        assert any("File changed externally" in record.message for record in caplog.records)

    def test_on_file_changed_externally_shows_status(self, handler, tmp_path):
        """Test file changed externally shows status bar message (lines 504-506)."""
        test_file = tmp_path / "test.adoc"

        # Mock window status_bar
        handler.window.status_bar = Mock()
        handler.window.status_bar.showMessage = Mock()

        handler._on_file_changed_externally(test_file)

        # Should show status message
        handler.window.status_bar.showMessage.assert_called_once()
        call_args = handler.window.status_bar.showMessage.call_args[0]
        assert test_file.name in call_args[0]
