"""Tests for ui.pandoc_result_handler module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor with all required attributes for PandocResultHandler."""
    editor = Mock()

    # Status bar and manager
    editor.status_bar = Mock()
    editor.status_bar.showMessage = Mock()
    editor.status_manager = Mock()
    editor.status_manager.show_message = Mock()

    # File operations manager
    editor.file_operations_manager = Mock()
    editor.file_operations_manager._is_processing_pandoc = True
    editor.file_operations_manager._pending_file_path = None

    # Export manager
    editor.export_manager = Mock()
    editor.export_manager.handle_pandoc_result = Mock()
    editor.export_manager.pending_export_path = None
    editor.export_manager.pending_export_format = None

    # File load manager
    editor.file_load_manager = Mock()
    editor.file_load_manager.load_content_into_editor = Mock()

    # Editor and preview widgets
    editor.editor = Mock()
    editor.editor.clear = Mock()
    editor.preview = Mock()
    editor.preview.setHtml = Mock()

    # Signals
    editor.request_load_file_content = Mock()
    editor.request_load_file_content.emit = Mock()

    # UI state update
    editor._update_ui_state = Mock()
    editor.update_preview = Mock()

    return editor


@pytest.mark.unit
class TestPandocResultHandlerBasics:
    """Test suite for PandocResultHandler basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        assert PandocResultHandler is not None

    def test_creation(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)
        assert handler is not None

    def test_stores_editor_reference(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)
        assert handler.editor == mock_editor

    def test_has_handle_pandoc_result_method(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)
        assert hasattr(handler, "handle_pandoc_result")
        assert callable(handler.handle_pandoc_result)

    def test_has_handle_pandoc_error_result_method(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)
        assert hasattr(handler, "handle_pandoc_error_result")
        assert callable(handler.handle_pandoc_error_result)


@pytest.mark.unit
class TestHandlePandocResult:
    """Test suite for handle_pandoc_result method (success path)."""

    def test_resets_processing_flag_on_success(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True
        handler.handle_pandoc_result("= Converted Content", "importing file")

        # Should reset processing flag
        assert mock_editor.file_operations_manager._is_processing_pandoc is False

    def test_updates_ui_state_on_success(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        handler.handle_pandoc_result("= Converted Content", "importing file")

        # Should update UI state
        mock_editor._update_ui_state.assert_called_once()

    def test_delegates_to_export_manager(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        result = "= Converted Content"
        context = "exporting to DOCX"
        handler.handle_pandoc_result(result, context)

        # Should delegate to export manager
        mock_editor.export_manager.handle_pandoc_result.assert_called_once_with(
            result, context
        )

    def test_emits_load_signal_when_pending_file_path_set(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        pending_path = Path("/tmp/test.docx")
        mock_editor.file_operations_manager._pending_file_path = pending_path
        result = "= Converted Content"
        context = "importing file"

        handler.handle_pandoc_result(result, context)

        # Should emit signal to load file content
        mock_editor.request_load_file_content.emit.assert_called_once_with(
            result, pending_path, context
        )

    def test_clears_pending_file_path_after_emitting_signal(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        pending_path = Path("/tmp/test.docx")
        mock_editor.file_operations_manager._pending_file_path = pending_path

        handler.handle_pandoc_result("= Converted Content", "importing file")

        # Should clear pending file path
        assert mock_editor.file_operations_manager._pending_file_path is None

    def test_no_signal_emission_when_no_pending_file_path(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = None

        handler.handle_pandoc_result("= Converted Content", "exporting to PDF")

        # Should not emit signal
        mock_editor.request_load_file_content.emit.assert_not_called()


@pytest.mark.unit
class TestHandlePandocErrorResult:
    """Test suite for handle_pandoc_error_result method (error path)."""

    def test_resets_processing_flag_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True
        handler.handle_pandoc_error_result("Pandoc failed", "importing file")

        # Should reset processing flag
        assert mock_editor.file_operations_manager._is_processing_pandoc is False

    def test_clears_pending_file_path_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Pandoc failed", "importing file")

        # Should clear pending file path
        assert mock_editor.file_operations_manager._pending_file_path is None

    def test_clears_export_manager_state_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        mock_editor.export_manager.pending_export_format = "pdf"

        handler.handle_pandoc_error_result("Pandoc failed", "exporting to PDF")

        # Should clear export manager state
        assert mock_editor.export_manager.pending_export_path is None
        assert mock_editor.export_manager.pending_export_format is None

    def test_updates_ui_state_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        handler.handle_pandoc_error_result("Pandoc failed", "importing file")

        # Should update UI state
        mock_editor._update_ui_state.assert_called_once()

    def test_shows_status_bar_message_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        context = "importing DOCX file"
        handler.handle_pandoc_error_result("Pandoc failed", context)

        # Should show status bar message
        mock_editor.status_bar.showMessage.assert_called_once()
        assert "Conversion failed" in str(
            mock_editor.status_bar.showMessage.call_args
        )


@pytest.mark.unit
class TestPDFExportErrorHandling:
    """Test suite for special PDF export error handling."""

    def test_shows_pdf_workaround_for_pdflatex_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        error = "pdflatex not found in PATH"
        context = "Exporting to PDF"

        handler.handle_pandoc_error_result(error, context)

        # Should show PDF workaround message
        mock_editor.status_manager.show_message.assert_called_once()
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "HTML" in call_args
        assert "Ctrl+P" in call_args

    def test_shows_pdf_workaround_for_pdf_engine_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        error = "pdf-engine not found"
        context = "Exporting to PDF"

        handler.handle_pandoc_error_result(error, context)

        # Should show PDF workaround message
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "Export to HTML instead" in call_args

    def test_shows_generic_export_error_for_non_pdf(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.docx")
        error = "Pandoc conversion failed"
        context = "Exporting to DOCX"

        handler.handle_pandoc_error_result(error, context)

        # Should show generic export error
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "DOCX" in call_args
        assert "Pandoc conversion failed" in call_args


@pytest.mark.unit
class TestImportErrorHandling:
    """Test suite for import error handling."""

    def test_clears_editor_on_import_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Conversion failed", "importing file")

        # Should clear editor
        mock_editor.editor.clear.assert_called_once()

    def test_shows_error_html_on_import_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Conversion failed", "importing file")

        # Should show error HTML in preview
        mock_editor.preview.setHtml.assert_called_once()
        call_args = str(mock_editor.preview.setHtml.call_args)
        assert "Conversion Failed" in call_args

    def test_shows_error_dialog_with_file_path(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        file_path = Path("/tmp/test.docx")
        mock_editor.file_operations_manager._pending_file_path = file_path
        error = "Invalid format"
        context = "importing DOCX"

        handler.handle_pandoc_error_result(error, context)

        # Should show error dialog with file path
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "test.docx" in call_args or str(file_path) in call_args
        assert "Invalid format" in call_args


@pytest.mark.unit
class TestFileLoadRequest:
    """Test suite for _handle_file_load_request method."""

    def test_loads_content_into_editor(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        result = "= Test Document\n\nContent"
        pending_path = Path("/tmp/test.docx")
        context = "importing file"

        handler._handle_file_load_request(result, pending_path, context)

        # Should load content into editor
        mock_editor.file_load_manager.load_content_into_editor.assert_called_once_with(
            result, pending_path
        )

    def test_schedules_preview_update(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(mock_editor)

        result = "= Test Document"
        pending_path = Path("/tmp/test.docx")

        with patch("asciidoc_artisan.ui.pandoc_result_handler.QTimer.singleShot") as mock_timer:
            handler._handle_file_load_request(result, pending_path, "importing")

            # Should schedule preview update with 100ms delay
            mock_timer.assert_called_once_with(100, mock_editor.update_preview)
