"""Tests for ui.pandoc_result_handler module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest


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
        assert "Conversion failed" in str(mock_editor.status_bar.showMessage.call_args)


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

        with patch(
            "asciidoc_artisan.ui.pandoc_result_handler.QTimer.singleShot"
        ) as mock_timer:
            handler._handle_file_load_request(result, pending_path, "importing")

            # Should schedule preview update with 100ms delay
            mock_timer.assert_called_once_with(100, mock_editor.update_preview)


@pytest.mark.unit
class TestSuccessResultSequencing:
    """Test suite for multiple successful conversion sequences."""

    def test_consecutive_import_operations(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # First import
        result1 = "= Document 1"
        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/file1.docx")
        handler.handle_pandoc_result(result1, "importing file1")

        # Second import
        result2 = "= Document 2"
        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/file2.docx")
        handler.handle_pandoc_result(result2, "importing file2")

        # Both should emit signals
        assert mock_editor.request_load_file_content.emit.call_count == 2

    def test_consecutive_export_operations(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # First export
        handler.handle_pandoc_result("Export result 1", "exporting to PDF")

        # Second export
        handler.handle_pandoc_result("Export result 2", "exporting to DOCX")

        # Export manager should handle both
        assert mock_editor.export_manager.handle_pandoc_result.call_count == 2

    def test_alternating_import_export_operations(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # Import
        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_result("= Import", "importing")
        assert mock_editor.request_load_file_content.emit.call_count == 1

        # Export
        handler.handle_pandoc_result("Export", "exporting")
        assert mock_editor.export_manager.handle_pandoc_result.call_count == 2

    def test_processing_flag_reset_after_each_success(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        for i in range(5):
            mock_editor.file_operations_manager._is_processing_pandoc = True
            handler.handle_pandoc_result(f"Result {i}", f"operation {i}")
            assert mock_editor.file_operations_manager._is_processing_pandoc is False

    def test_ui_state_update_called_after_each_success(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        for i in range(3):
            handler.handle_pandoc_result(f"Result {i}", f"operation {i}")

        # Should update UI state 3 times
        assert mock_editor._update_ui_state.call_count == 3


@pytest.mark.unit
class TestErrorResultVariations:
    """Test suite for different error result scenarios."""

    def test_error_with_very_long_message(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        error = "x" * 1000  # Very long error message
        handler.handle_pandoc_error_result(error, "importing")

        # Should still show error dialog
        mock_editor.status_manager.show_message.assert_called_once()

    def test_error_with_special_characters(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        error = "Error: \n\t特殊字符\n@#$%^&*()"
        context = "importing test"
        handler.handle_pandoc_error_result(error, context)

        # Should handle special chars
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert context in call_args

    def test_error_with_empty_message(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("", "importing")

        # Should still show error dialog
        mock_editor.status_manager.show_message.assert_called_once()

    def test_error_resets_all_state_flags(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # Set all flags
        mock_editor.file_operations_manager._is_processing_pandoc = True
        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        mock_editor.export_manager.pending_export_format = "pdf"

        handler.handle_pandoc_error_result("Error", "exporting")

        # All should be reset
        assert mock_editor.file_operations_manager._is_processing_pandoc is False
        assert mock_editor.file_operations_manager._pending_file_path is None
        assert mock_editor.export_manager.pending_export_path is None
        assert mock_editor.export_manager.pending_export_format is None

    def test_consecutive_errors(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        for i in range(3):
            handler.handle_pandoc_error_result(f"Error {i}", f"operation {i}")

        # Should show 3 error dialogs
        assert mock_editor.status_manager.show_message.call_count == 3


@pytest.mark.unit
class TestNonPDFExportErrors:
    """Test suite for non-PDF export error handling."""

    def test_docx_export_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.docx")
        handler.handle_pandoc_error_result("Pandoc error", "Exporting to DOCX")

        # Should show generic export error
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "DOCX" in call_args
        assert "Pandoc error" in call_args

    def test_html_export_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.html")
        handler.handle_pandoc_error_result("Conversion failed", "Exporting to HTML")

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "HTML" in call_args

    def test_markdown_export_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.md")
        handler.handle_pandoc_error_result("Error", "Exporting to Markdown")

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "MD" in call_args

    def test_export_error_with_path_suffix_uppercase(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.DOCX")
        handler.handle_pandoc_error_result("Error", "Exporting to DOCX")

        # Should handle .DOCX suffix
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "DOCX" in call_args

    def test_export_error_returns_early(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result("Error", "Exporting to PDF")

        # Should not clear editor or set preview HTML (returns early)
        mock_editor.editor.clear.assert_not_called()
        mock_editor.preview.setHtml.assert_not_called()


@pytest.mark.unit
class TestPDFErrorPatterns:
    """Test suite for different PDF error patterns."""

    def test_pdflatex_error_shows_workaround(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result("pdflatex not found", "Exporting to PDF")

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "Export to HTML instead" in call_args
        assert "Ctrl+P" in call_args

    def test_pdf_engine_error_shows_workaround(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result("pdf-engine not found", "Exporting to PDF")

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "HTML" in call_args

    def test_no_such_file_error_shows_workaround(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result(
            "No such file or directory", "Exporting to PDF"
        )

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "Export to HTML" in call_args

    def test_pdf_error_includes_technical_details(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        error = "pdflatex: command not found"
        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result(error, "Exporting to PDF")

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert error in call_args


@pytest.mark.unit
class TestFileLoadRequestDetails:
    """Test suite for _handle_file_load_request method details."""

    @patch("asciidoc_artisan.ui.pandoc_result_handler.QTimer")
    def test_qtimer_single_shot_called_with_correct_delay(
        self, mock_qtimer, mock_editor
    ):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        result = "= Test"
        pending_path = Path("/tmp/test.docx")
        handler._handle_file_load_request(result, pending_path, "importing")

        # Should schedule preview update with 100ms delay
        mock_qtimer.singleShot.assert_called_once_with(100, mock_editor.update_preview)

    def test_file_load_manager_called_before_preview_update(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        result = "= Test"
        pending_path = Path("/tmp/test.docx")
        handler._handle_file_load_request(result, pending_path, "importing")

        # File load manager should be called
        mock_editor.file_load_manager.load_content_into_editor.assert_called_once_with(
            result, pending_path
        )

    def test_context_logged_successfully(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        with patch("asciidoc_artisan.ui.pandoc_result_handler.logger") as mock_logger:
            handler._handle_file_load_request(
                "= Test", Path("/tmp/test.docx"), "importing DOCX"
            )
            # Should log success message
            mock_logger.info.assert_called_once()

    def test_multiple_file_load_requests(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        for i in range(3):
            handler._handle_file_load_request(
                f"= Document {i}", Path(f"/tmp/doc{i}.docx"), f"importing doc{i}"
            )

        # Should call load_content_into_editor 3 times
        assert mock_editor.file_load_manager.load_content_into_editor.call_count == 3


@pytest.mark.unit
class TestStateTransitions:
    """Test suite for state flag transitions."""

    def test_pending_file_path_cleared_on_success(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_result("= Test", "importing")

        # Pending path should be cleared
        assert mock_editor.file_operations_manager._pending_file_path is None

    def test_pending_file_path_cleared_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Error", "importing")

        # Pending path should be cleared
        assert mock_editor.file_operations_manager._pending_file_path is None

    def test_processing_flag_always_reset_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True

        # Try both import and export errors
        handler.handle_pandoc_error_result("Error 1", "importing")
        assert mock_editor.file_operations_manager._is_processing_pandoc is False

        mock_editor.file_operations_manager._is_processing_pandoc = True
        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result("Error 2", "Exporting to PDF")
        assert mock_editor.file_operations_manager._is_processing_pandoc is False

    def test_export_state_cleared_only_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # Success: export manager handles clearing
        handler.handle_pandoc_result("Result", "exporting")
        # handler doesn't clear export state on success

        # Error: handler clears export state
        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        mock_editor.export_manager.pending_export_format = "pdf"
        handler.handle_pandoc_error_result("Error", "exporting")

        assert mock_editor.export_manager.pending_export_path is None
        assert mock_editor.export_manager.pending_export_format is None


@pytest.mark.unit
class TestContextStringVariations:
    """Test suite for different context string patterns."""

    @pytest.mark.parametrize(
        "context",
        [
            "importing file",
            "Exporting to PDF",
            "Exporting to DOCX",
            "Converting from Markdown",
            "Processing document",
            "Handling user request",
        ],
    )
    def test_success_with_various_contexts(self, mock_editor, context):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        handler.handle_pandoc_result("= Result", context)

        # Export manager should receive same context
        mock_editor.export_manager.handle_pandoc_result.assert_called_once_with(
            "= Result", context
        )

    @pytest.mark.parametrize(
        "context", ["importing", "exporting", "Exporting to PDF", "Converting markdown"]
    )
    def test_error_with_various_contexts(self, mock_editor, context):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Error", context)

        # Context should appear in error message
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert context in call_args

    def test_context_with_special_characters(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        context = "Exporting to 文件.pdf"
        handler.handle_pandoc_result("Result", context)

        mock_editor.export_manager.handle_pandoc_result.assert_called_once_with(
            "Result", context
        )


@pytest.mark.unit
class TestStatusBarMessages:
    """Test suite for status bar message generation."""

    def test_conversion_failed_message_on_error(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        context = "importing test file"
        handler.handle_pandoc_error_result("Error", context)

        # Should show "Conversion failed" in status bar
        mock_editor.status_bar.showMessage.assert_called_once()
        call_args = str(mock_editor.status_bar.showMessage.call_args)
        assert "Conversion failed" in call_args
        assert context in call_args

    def test_status_bar_message_includes_context(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        contexts = ["importing DOCX", "exporting PDF", "converting Markdown"]
        for context in contexts:
            handler.handle_pandoc_error_result("Error", context)

        # Should show message for each context
        assert mock_editor.status_bar.showMessage.call_count == 3


@pytest.mark.unit
class TestErrorDialogContent:
    """Test suite for error dialog message content."""

    def test_import_error_includes_file_path(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        file_path = Path("/tmp/test.docx")
        mock_editor.file_operations_manager._pending_file_path = file_path
        handler.handle_pandoc_error_result("Conversion error", "importing")

        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert str(file_path) in call_args or file_path.name in call_args

    def test_import_error_shows_critical_severity(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Error", "importing")

        # Should show critical severity
        call_args = mock_editor.status_manager.show_message.call_args
        assert call_args[0][0] == "critical"

    def test_export_error_shows_critical_severity(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result("Error", "Exporting to PDF")

        call_args = mock_editor.status_manager.show_message.call_args
        assert call_args[0][0] == "critical"

    def test_error_dialog_title_varies_by_operation(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # Export error
        mock_editor.export_manager.pending_export_path = Path("/tmp/export.pdf")
        handler.handle_pandoc_error_result("Error", "Exporting to PDF")
        call_args = mock_editor.status_manager.show_message.call_args
        assert call_args[0][1] == "Export Error"

        # Import error
        mock_editor.file_operations_manager._pending_file_path = Path("/tmp/test.docx")
        handler.handle_pandoc_error_result("Error", "importing")
        call_args = mock_editor.status_manager.show_message.call_args
        assert call_args[0][1] == "Conversion Error"


@pytest.mark.unit
class TestSignalEmissions:
    """Test suite for signal emission verification."""

    def test_request_load_file_content_signal_emitted(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        result = "= Test Document"
        pending_path = Path("/tmp/test.docx")
        context = "importing file"

        mock_editor.file_operations_manager._pending_file_path = pending_path
        handler.handle_pandoc_result(result, context)

        # Should emit signal with correct arguments
        mock_editor.request_load_file_content.emit.assert_called_once_with(
            result, pending_path, context
        )

    def test_signal_emitted_only_when_pending_path_exists(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        # No pending path
        mock_editor.file_operations_manager._pending_file_path = None
        handler.handle_pandoc_result("= Test", "exporting")

        # Should not emit signal
        mock_editor.request_load_file_content.emit.assert_not_called()

    def test_signal_emission_with_different_result_types(self, mock_editor):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        handler = PandocResultHandler(mock_editor)

        results = [
            "= AsciiDoc content",
            "# Markdown content",
            "<html><body>HTML content</body></html>",
        ]

        for i, result in enumerate(results):
            mock_editor.file_operations_manager._pending_file_path = Path(
                f"/tmp/file{i}.txt"
            )
            handler.handle_pandoc_result(result, f"operation {i}")

        # Should emit signal 3 times
        assert mock_editor.request_load_file_content.emit.call_count == 3
