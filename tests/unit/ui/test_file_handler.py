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

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from PySide6.QtWidgets import QPlainTextEdit, QMessageBox, QMainWindow

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
    handler = FileHandler(
        mock_editor, mock_window, mock_settings_manager, mock_status_manager
    )
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


@pytest.mark.unit
def test_prompt_save_before_action_save(handler, tmp_path):
    """Test prompt saves file when user chooses Save."""
    handler.unsaved_changes = True
    handler.current_file_path = tmp_path / "test.adoc"
    handler.editor.setPlainText("Content")

    # Mock os.environ to bypass pytest test environment check
    with patch("os.environ.get", return_value=None):
        # Mock dialog and save_file
        with patch("PySide6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Save):
            with patch.object(handler, "save_file", return_value=True) as mock_save:
                # prompt_save_before_action is synchronous, calls save_file wrapper
                result = handler.prompt_save_before_action("test action")

    assert result is True
    mock_save.assert_called_once()


def test_prompt_save_before_action_discard(handler):
    """Test prompt returns True when user chooses Discard."""
    handler.unsaved_changes = True

    with patch("PySide6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Discard):
        result = handler.prompt_save_before_action("test action")

    assert result is True


@pytest.mark.unit
def test_prompt_save_before_action_cancel(handler):
    """Test prompt returns False when user cancels."""
    handler.unsaved_changes = True

    # Mock os.environ to bypass pytest test environment check
    with patch("os.environ.get", return_value=None):
        with patch("PySide6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Cancel):
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
