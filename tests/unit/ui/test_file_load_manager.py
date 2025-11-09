"""Tests for ui.file_load_manager module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PySide6.QtWidgets import QPlainTextEdit, QProgressDialog, QStatusBar


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor with all required attributes for FileLoadManager."""
    from PySide6.QtWidgets import QMainWindow

    # Use real QMainWindow so QProgressDialog can use it as parent
    editor = QMainWindow()

    # Editor widget
    editor.editor = Mock(spec=QPlainTextEdit)
    editor.editor.setPlainText = Mock()

    # Status bar (use real QStatusBar)
    editor.status_bar = QStatusBar()

    # Mock showMessage to track calls
    editor.status_bar._original_showMessage = editor.status_bar.showMessage
    editor.status_bar.showMessage = Mock(
        side_effect=editor.status_bar._original_showMessage
    )

    # Status manager
    editor.status_manager = Mock()
    editor.status_manager.update_window_title = Mock()
    editor.status_manager.update_document_metrics = Mock()

    # File state
    editor._current_file_path = None
    editor._unsaved_changes = False
    editor._is_opening_file = False

    # Progress dialog
    editor._progress_dialog = None

    # Methods
    editor.update_preview = Mock()

    return editor


@pytest.mark.unit
class TestFileLoadManagerBasics:
    """Test suite for FileLoadManager basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        assert FileLoadManager is not None

    def test_creation(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)
        assert manager is not None

    def test_stores_editor_reference(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)
        assert manager.editor == mock_editor

    def test_has_load_methods(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)
        assert hasattr(manager, "load_content_into_editor")
        assert hasattr(manager, "on_file_load_progress")
        assert callable(manager.load_content_into_editor)
        assert callable(manager.on_file_load_progress)


@pytest.mark.unit
class TestLoadContentIntoEditor:
    """Test suite for load_content_into_editor method."""

    def test_sets_is_opening_file_flag(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should clear flag after loading
        assert mock_editor._is_opening_file is False

    def test_sets_editor_content(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should set editor content
        mock_editor.editor.setPlainText.assert_called_once_with(content)

    def test_updates_current_file_path(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should update current file path
        assert mock_editor._current_file_path == file_path

    def test_clears_unsaved_changes_flag(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        mock_editor._unsaved_changes = True
        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should clear unsaved changes flag
        assert mock_editor._unsaved_changes is False

    def test_updates_window_title(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should update window title
        mock_editor.status_manager.update_window_title.assert_called_once()

    def test_updates_document_metrics(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should update document metrics
        mock_editor.status_manager.update_document_metrics.assert_called_once()

    def test_shows_status_message_for_native_file(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should show "Opened:" message
        call_args = str(mock_editor.status_bar.showMessage.call_args)
        assert "Opened:" in call_args
        assert "test.adoc" in call_args

    def test_shows_converted_message_for_markdown(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "# Test Document"
        file_path = Path("/tmp/test.md")

        manager.load_content_into_editor(content, file_path)

        # Should show "Converted and opened:" message
        call_args = str(mock_editor.status_bar.showMessage.call_args)
        assert "Converted and opened:" in call_args
        assert "test.md" in call_args

    def test_shows_converted_message_for_docx(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "Test Document Content"
        file_path = Path("/tmp/test.docx")

        manager.load_content_into_editor(content, file_path)

        # Should show "Converted and opened:" message
        call_args = str(mock_editor.status_bar.showMessage.call_args)
        assert "Converted and opened:" in call_args

    def test_triggers_preview_update(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should trigger preview update
        mock_editor.update_preview.assert_called_once()

    def test_clears_flag_even_if_error_occurs(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        # Make setPlainText raise an error
        mock_editor.editor.setPlainText.side_effect = RuntimeError("Test error")

        content = "= Test Document"
        file_path = Path("/tmp/test.adoc")

        try:
            manager.load_content_into_editor(content, file_path)
        except RuntimeError:
            pass

        # Should clear flag even after error (finally block)
        assert mock_editor._is_opening_file is False


@pytest.mark.unit
class TestLargeFileHandling:
    """Test suite for large file optimization."""

    @patch("asciidoc_artisan.ui.file_load_manager.LARGE_FILE_THRESHOLD_BYTES", 100)
    def test_detects_large_file(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        # Content larger than threshold (100 bytes)
        content = "x" * 200
        file_path = Path("/tmp/large.adoc")

        with patch("asciidoc_artisan.ui.file_load_manager.logger") as mock_logger:
            manager.load_content_into_editor(content, file_path)
            # Should log large file message
            mock_logger.info.assert_called()

    @patch("asciidoc_artisan.ui.file_load_manager.LARGE_FILE_THRESHOLD_BYTES", 100)
    def test_handles_small_file_normally(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        # Content smaller than threshold (100 bytes)
        content = "= Small File"
        file_path = Path("/tmp/small.adoc")

        manager.load_content_into_editor(content, file_path)

        # Should still set content normally
        mock_editor.editor.setPlainText.assert_called_once_with(content)


@pytest.mark.unit
class TestProgressTracking:
    """Test suite for on_file_load_progress method."""

    def test_creates_progress_dialog_on_first_update(self, mock_editor, qapp):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        manager.on_file_load_progress(50, "Loading...")

        # Should create progress dialog
        assert mock_editor._progress_dialog is not None
        assert isinstance(mock_editor._progress_dialog, QProgressDialog)

    def test_does_not_create_dialog_at_zero_percent(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        manager.on_file_load_progress(0, "Starting...")

        # Should not create progress dialog
        assert mock_editor._progress_dialog is None

    def test_does_not_create_dialog_at_hundred_percent(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        manager.on_file_load_progress(100, "Complete")

        # Should not create progress dialog
        assert mock_editor._progress_dialog is None

    def test_updates_existing_progress_dialog(self, mock_editor, qapp):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        # First update creates dialog
        manager.on_file_load_progress(25, "Loading...")
        dialog = mock_editor._progress_dialog

        # Second update uses same dialog
        manager.on_file_load_progress(75, "Almost done...")
        assert mock_editor._progress_dialog is dialog

    def test_closes_progress_dialog_on_completion(self, mock_editor, qapp):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        # Create dialog
        manager.on_file_load_progress(50, "Loading...")
        assert mock_editor._progress_dialog is not None

        # Complete loading
        manager.on_file_load_progress(100, "Complete")

        # Should close and clear dialog
        assert mock_editor._progress_dialog is None

    def test_shows_status_bar_message_on_completion(self, mock_editor, qapp):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        # Create dialog first
        manager.on_file_load_progress(50, "Loading...")

        # Complete loading
        manager.on_file_load_progress(100, "File loaded successfully")

        # Should show status bar message
        mock_editor.status_bar.showMessage.assert_called_with(
            "File loaded successfully", 3000
        )

    def test_shows_status_bar_message_for_initial_progress(self, mock_editor):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        manager.on_file_load_progress(0, "Starting load...")

        # Should show status bar message
        mock_editor.status_bar.showMessage.assert_called_with("Starting load...", 2000)

    def test_progress_dialog_has_no_cancel_button(self, mock_editor, qapp):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        manager.on_file_load_progress(50, "Loading...")

        # Should have no cancel button
        assert mock_editor._progress_dialog.autoClose() is True
        assert mock_editor._progress_dialog.autoReset() is True


@pytest.mark.unit
class TestConvertedFormats:
    """Test suite for converted format detection."""

    @pytest.mark.parametrize(
        "extension,content",
        [
            (".md", "# Markdown"),
            (".markdown", "# Markdown"),
            (".docx", "DOCX content"),
            (".html", "<h1>HTML</h1>"),
            (".htm", "<h1>HTML</h1>"),
            (".tex", "\\section{LaTeX}"),
            (".rst", "reStructuredText"),
            (".org", "* Org Mode"),
            (".textile", "h1. Textile"),
        ],
    )
    def test_shows_converted_message_for_format(self, mock_editor, extension, content):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager

        manager = FileLoadManager(mock_editor)

        file_path = Path(f"/tmp/test{extension}")

        manager.load_content_into_editor(content, file_path)

        # Should show "Converted and opened:" message
        call_args = str(mock_editor.status_bar.showMessage.call_args)
        assert "Converted and opened:" in call_args
