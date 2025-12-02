"""Tests for ui.file_operations_manager module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor with all required attributes for FileOperationsManager."""
    editor = Mock()

    # Editor widget
    editor.editor = Mock()
    editor.editor.toPlainText = Mock(return_value="= Test Document\n\nContent.")
    editor.editor.setPlainText = Mock()

    # Status bar and manager
    editor.status_bar = Mock()
    editor.status_bar.showMessage = Mock()
    editor.status_manager = Mock()
    editor.status_manager.show_message = Mock()
    editor.status_manager.prompt_save_before_action = Mock(return_value=True)
    editor.status_manager.update_window_title = Mock()

    # Settings
    editor._settings = Mock()
    editor._settings.last_directory = "/tmp"

    # Settings manager
    editor._settings_manager = Mock()
    editor._settings_manager.get_ai_conversion_preference = Mock(return_value=False)

    # File state
    editor._current_file_path = None
    editor._unsaved_changes = False
    editor._pending_export_path = None
    editor._pending_export_format = None

    # AsciiDoc API
    editor._asciidoc_api = Mock()
    editor._asciidoc_api.execute = Mock()

    # Temp directory
    editor._temp_dir = Mock()
    editor._temp_dir.name = "/tmp/asciidoc_test"

    # Managers
    editor.export_manager = Mock()
    editor.export_manager.pending_export_path = None
    editor.export_manager.pending_export_format = None

    editor.file_load_manager = Mock()
    editor.file_load_manager.load_content_into_editor = Mock()

    editor.ui_state_manager = Mock()
    editor.ui_state_manager.check_pandoc_availability = Mock(return_value=True)

    editor.large_file_handler = Mock()
    editor.large_file_handler.load_file_optimized = Mock(return_value=(True, "= Test\n\nContent", None))

    # Preview widget
    editor.preview = Mock()
    editor.preview.setHtml = Mock()

    # Signals
    editor.request_pandoc_conversion = Mock()
    editor.request_pandoc_conversion.emit = Mock()

    # UI state update
    editor._update_ui_state = Mock()

    return editor


@pytest.mark.fr_007
@pytest.mark.unit
class TestFileOperationsManagerBasics:
    """Test suite for FileOperationsManager basic functionality.

    FR-007: Save Files (Manager initialization)
    """

    def test_import(self):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        assert FileOperationsManager is not None

    def test_creation(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        assert manager is not None

    def test_stores_editor_reference(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        assert manager.editor == mock_editor

    def test_initialization_sets_processing_flag(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        assert hasattr(manager, "_is_processing_pandoc")
        assert manager._is_processing_pandoc is False

    def test_initialization_sets_pending_file_path(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        assert hasattr(manager, "_pending_file_path")
        assert manager._pending_file_path is None


@pytest.mark.fr_006
@pytest.mark.unit
class TestOpenFile:
    """Test suite for open_file method.

    FR-006: Open Files

    Note: open_file() delegates to FileOpenHandler._open_handler after MA refactoring.
    Patches must target asciidoc_artisan.ui.file_open_handler module.
    """

    @patch("asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName")
    def test_open_file_prompts_save_if_unsaved_changes(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        mock_editor._unsaved_changes = True
        mock_editor.status_manager.prompt_save_before_action = Mock(return_value=False)

        manager.open_file()

        # Should prompt to save and return early if user cancels
        mock_editor.status_manager.prompt_save_before_action.assert_called_once()
        mock_dialog.assert_not_called()

    @patch("asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName")
    def test_open_file_blocked_when_processing(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        manager._is_processing_pandoc = True
        manager.open_file()

        # Should show warning and not open dialog
        mock_editor.status_manager.show_message.assert_called_once()
        mock_dialog.assert_not_called()

    @patch("asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName")
    def test_open_file_cancelled_dialog_returns_early(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        # User cancels dialog
        mock_dialog.return_value = ("", "")
        manager.open_file()

        # Should not attempt to load any file
        mock_editor.file_load_manager.load_content_into_editor.assert_not_called()

    @patch("asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName")
    def test_open_pdf_calls_pdf_extraction(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf")
        mock_dialog.return_value = (str(pdf_file), "")

        # Patch on the handler, not the manager (MA refactoring moved methods)
        with patch.object(manager._open_handler, "open_pdf_with_extraction") as mock_pdf:
            manager.open_file()
            mock_pdf.assert_called_once_with(pdf_file)

    @patch("asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName")
    def test_open_docx_calls_pandoc_conversion(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"
        docx_file.write_text("fake docx")
        mock_dialog.return_value = (str(docx_file), "")

        # Patch on the handler, not the manager (MA refactoring moved methods)
        with patch.object(manager._open_handler, "open_with_pandoc_conversion") as mock_pandoc:
            manager.open_file()
            mock_pandoc.assert_called_once()

    @patch("asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName")
    def test_open_asciidoc_loads_directly(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        adoc_file = tmp_path / "test.adoc"
        adoc_file.write_text("= Test\n\nContent")
        mock_dialog.return_value = (str(adoc_file), "")

        # Patch on the handler, not the manager (MA refactoring moved methods)
        with patch.object(manager._open_handler, "open_native_file") as mock_native:
            manager.open_file()
            mock_native.assert_called_once_with(adoc_file)


@pytest.mark.fr_007
@pytest.mark.unit
class TestSaveFile:
    """Test suite for save_file method.

    FR-007: Save Files

    Note: save_file() delegates to FileSaveHandler after MA refactoring.
    Patches must target asciidoc_artisan.ui.file_save_handler module.
    """

    def test_save_file_uses_current_path_when_available(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        current_file = tmp_path / "test.adoc"
        mock_editor._current_file_path = current_file

        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ):
            result = manager.save_file(save_as=False)

        # Should save to current path without showing dialog
        assert result is True
        assert mock_editor._unsaved_changes is False

    @patch("asciidoc_artisan.ui.file_save_handler.QFileDialog.getSaveFileName")
    def test_save_file_shows_dialog_when_save_as(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        save_file = tmp_path / "new.adoc"
        mock_dialog.return_value = (str(save_file), "")

        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ):
            result = manager.save_file(save_as=True)

        # Should show dialog even if current file exists
        mock_dialog.assert_called_once()
        assert result is True

    @patch("asciidoc_artisan.ui.file_save_handler.QFileDialog.getSaveFileName")
    def test_save_file_cancelled_dialog_returns_false(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        # User cancels dialog
        mock_dialog.return_value = ("", "")
        result = manager.save_file(save_as=True)

        # Should return False
        assert result is False

    @patch("asciidoc_artisan.ui.file_save_handler.QFileDialog.getSaveFileName")
    def test_save_file_delegates_to_export_for_non_adoc(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "export.docx"
        mock_dialog.return_value = (str(docx_file), "Word Documents (*.docx)")

        with patch.object(manager, "save_as_format_internal") as mock_export:
            manager.save_file(save_as=True)
            mock_export.assert_called_once()

    def test_save_file_updates_unsaved_changes_flag(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        current_file = tmp_path / "test.adoc"
        mock_editor._current_file_path = current_file
        mock_editor._unsaved_changes = True

        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ):
            manager.save_file()

        # Should clear unsaved changes flag
        assert mock_editor._unsaved_changes is False


@pytest.mark.fr_007
@pytest.mark.fr_008
@pytest.mark.unit
class TestSaveAsFormatInternal:
    """Test suite for save_as_format_internal method.

    FR-007: Save Files
    FR-008: Save As
    """

    def test_save_as_asciidoc_uses_atomic_save(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        adoc_file = tmp_path / "test.adoc"

        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ) as mock_save:
            result = manager.save_as_format_internal(adoc_file, "adoc")

        # Should use atomic_save_text
        mock_save.assert_called_once()
        assert result is True

    def test_save_as_html_uses_asciidoc_api(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        html_file = tmp_path / "test.html"

        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ):
            result = manager.save_as_format_internal(html_file, "html")

        # Should call asciidoc_api.execute for HTML conversion
        mock_editor._asciidoc_api.execute.assert_called_once()
        assert result is True

    def test_save_as_docx_emits_pandoc_signal(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"

        # Create actual temp directory for temp file creation
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        mock_editor._temp_dir.name = str(temp_dir)

        with patch("asciidoc_artisan.ui.file_save_handler.atomic_save_text"):
            manager.save_as_format_internal(docx_file, "docx")

        # Should emit pandoc conversion signal
        mock_editor.request_pandoc_conversion.emit.assert_called()

    def test_save_as_pdf_emits_pandoc_signal(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"

        # Create actual temp directory for temp file creation
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        mock_editor._temp_dir.name = str(temp_dir)

        with patch("asciidoc_artisan.ui.file_save_handler.atomic_save_text"):
            manager.save_as_format_internal(pdf_file, "pdf")

        # Should emit pandoc conversion signal for PDF
        mock_editor.request_pandoc_conversion.emit.assert_called()


@pytest.mark.fr_006
@pytest.mark.fr_013
@pytest.mark.unit
class TestPDFExtraction:
    """Test suite for PDF extraction functionality.

    FR-006: Open Files
    FR-013: Import PDF

    Note: PDF extraction is handled by FileOpenHandler after MA refactoring.
    Tests call manager._open_handler.open_pdf_with_extraction().
    """

    def test_pdf_extraction_checks_availability(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake")

        # Patch where pdf_extractor is imported (lazy import inside method)
        with patch("asciidoc_artisan.document_converter.pdf_extractor") as mock_pdf:
            mock_pdf.is_available.return_value = True
            mock_pdf.convert_to_asciidoc.return_value = (True, "= Test", None)

            manager._open_handler.open_pdf_with_extraction(pdf_file)

            # Should check if PDF extractor is available
            mock_pdf.is_available.assert_called_once()

    def test_pdf_extraction_shows_error_if_unavailable(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"

        # Patch where pdf_extractor is imported (lazy import inside method)
        with patch("asciidoc_artisan.document_converter.pdf_extractor") as mock_pdf:
            mock_pdf.is_available.return_value = False

            manager._open_handler.open_pdf_with_extraction(pdf_file)

            # Should show error message
            mock_editor.status_manager.show_message.assert_called_once()
            assert "PyMuPDF" in str(mock_editor.status_manager.show_message.call_args)

    def test_pdf_extraction_loads_content_on_success(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"

        # Patch where pdf_extractor is imported (lazy import inside method)
        with patch("asciidoc_artisan.document_converter.pdf_extractor") as mock_pdf:
            mock_pdf.is_available.return_value = True
            mock_pdf.convert_to_asciidoc.return_value = (True, "= Extracted Text", None)

            manager._open_handler.open_pdf_with_extraction(pdf_file)

            # Should load extracted content into editor
            mock_editor.file_load_manager.load_content_into_editor.assert_called_once()


@pytest.mark.fr_006
@pytest.mark.fr_012
@pytest.mark.fr_014
@pytest.mark.integration
@pytest.mark.unit
class TestPandocConversion:
    """Test suite for Pandoc conversion workflow.

    FR-006: Open Files
    FR-012: Import DOCX
    FR-014: Import Markdown

    Note: Pandoc conversion is handled by FileOpenHandler after MA refactoring.
    Tests call manager._open_handler.open_with_pandoc_conversion().
    """

    def test_pandoc_conversion_checks_availability(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"fake docx")

        manager._open_handler.open_with_pandoc_conversion(docx_file, ".docx")

        # Should check Pandoc availability
        mock_editor.ui_state_manager.check_pandoc_availability.assert_called_once()

    def test_pandoc_conversion_sets_processing_flag(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"fake docx")

        manager._open_handler.open_with_pandoc_conversion(docx_file, ".docx")

        # Should set processing flag
        assert manager._is_processing_pandoc is True
        assert manager._pending_file_path == docx_file

    def test_pandoc_conversion_emits_signal(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test Markdown")

        manager._open_handler.open_with_pandoc_conversion(md_file, ".md")

        # Should emit pandoc conversion signal
        mock_editor.request_pandoc_conversion.emit.assert_called_once()


@pytest.mark.fr_007
@pytest.mark.fr_008
@pytest.mark.unit
class TestDetermineSaveFormat:
    """Test suite for _determine_save_format method.

    FR-007: Save Files
    FR-008: Save As
    """

    def test_determine_format_from_filter(self, mock_editor):
        from asciidoc_artisan.core import MD_FILTER
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        file_path = Path("/tmp/test")
        # Use actual MD_FILTER constant from core
        format_type, corrected_path = manager._determine_save_format(file_path, MD_FILTER)

        # Should detect format from filter
        assert format_type == "md"
        assert corrected_path.suffix == ".md"

    def test_determine_format_from_extension(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        file_path = Path("/tmp/test.docx")
        format_type, corrected_path = manager._determine_save_format(file_path, "")

        # Should detect format from file extension
        assert format_type == "docx"
        assert corrected_path.suffix == ".docx"

    def test_determine_format_adds_extension_if_missing(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        file_path = Path("/tmp/test")
        format_type, corrected_path = manager._determine_save_format(file_path, "HTML Files (*.html *.htm)")

        # Should add extension if missing
        assert format_type == "html"
        assert corrected_path.suffix == ".html"

    def test_determine_format_defaults_to_adoc(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        file_path = Path("/tmp/test.unknown")
        format_type, corrected_path = manager._determine_save_format(file_path, "")

        # Should default to adoc for unknown types
        assert format_type == "adoc"


@pytest.mark.fr_006
@pytest.mark.fr_007
@pytest.mark.edge_case
@pytest.mark.unit
class TestFileOperationsErrorHandling:
    """Test error handling in file operations (lines 280-284, 368-373, 408-413).

    FR-006: Open Files (error handling)
    FR-007: Save Files (error handling)
    """

    def test_open_file_generic_exception(self, mock_editor, tmp_path):
        """Test generic exception handling during file open (lines 280-284)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        # Create a test file
        test_file = tmp_path / "test.adoc"
        test_file.write_text("test content")

        # Mock QFileDialog to return the file path (in file_open_handler after MA refactoring)
        # Mock Path.read_text to raise an exception
        with patch(
            "asciidoc_artisan.ui.file_open_handler.QFileDialog.getOpenFileName",
            return_value=(str(test_file), ""),
        ):
            with patch("pathlib.Path.read_text", side_effect=Exception("Read error")):
                manager.open_file()

                # Should show error message
                mock_editor.status_manager.show_message.assert_called()
                call_args = mock_editor.status_manager.show_message.call_args[0]
                assert call_args[0] == "critical"
                assert "Failed to open file" in call_args[2]

    def test_save_file_atomic_save_failure(self, mock_editor, tmp_path):
        """Test save failure error handler (lines 368-373)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "test.adoc"

        # Mock atomic_save_text to return False (save failure)
        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=False,
        ):
            result = manager.save_file()

            # Should return False and show error message
            assert result is False
            mock_editor.status_manager.show_message.assert_called()
            call_args = mock_editor.status_manager.show_message.call_args[0]
            assert call_args[0] == "critical"
            assert "Save Error" in call_args[1]
            assert "Failed to save file" in call_args[2]

    def test_save_as_format_asciidoc_save_failure(self, mock_editor, tmp_path):
        """Test AsciiDoc save failure in format conversion (lines 408-413)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        target_file = tmp_path / "output.adoc"

        # Mock atomic_save_text to return False
        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=False,
        ):
            result = manager.save_as_format_internal(target_file, "adoc")

            # Should return False and show error message
            assert result is False
            mock_editor.status_manager.show_message.assert_called()
            call_args = mock_editor.status_manager.show_message.call_args[0]
            assert call_args[0] == "critical"
            assert "Save Error" in call_args[1]
            assert "Failed to save AsciiDoc file" in call_args[2]


@pytest.mark.fr_007
@pytest.mark.fr_021
@pytest.mark.fr_022
@pytest.mark.edge_case
@pytest.mark.unit
class TestFormatConversionErrors:
    """Test format conversion error handling (lines 419, 431-437, 466, 478-485).

    FR-007: Save Files (export error handling)
    FR-021: Export HTML
    FR-022: Export PDF
    """

    def test_html_export_asciidoc_api_none(self, mock_editor, tmp_path):
        """Test HTML export when asciidoc_api is None (line 419, caught at 432)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._asciidoc_api = None  # Set to None
        target_file = tmp_path / "output.html"

        # Exception is caught in try-except block (line 432)
        result = manager.save_as_format_internal(target_file, "html")

        # Should return False and show error message
        assert result is False
        mock_editor.status_manager.show_message.assert_called()
        call_args = mock_editor.status_manager.show_message.call_args[0]
        assert call_args[0] == "critical"
        assert "Save Error" in call_args[1]
        assert "Failed to save HTML file" in call_args[2]

    def test_html_save_exception_handler(self, mock_editor, tmp_path):
        """Test HTML save exception handler (lines 431-437)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        target_file = tmp_path / "output.html"

        # Mock execute to succeed but atomic_save_text to raise IOError
        mock_editor._asciidoc_api.execute.return_value = "<html>test</html>"
        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            side_effect=IOError("Disk full"),
        ):
            result = manager.save_as_format_internal(target_file, "html")

            # Should return False and show error message
            assert result is False
            mock_editor.status_manager.show_message.assert_called()
            call_args = mock_editor.status_manager.show_message.call_args[0]
            assert call_args[0] == "critical"
            assert "Failed to save HTML file" in call_args[2]

    def test_asciidoc_to_html_conversion_error(self, mock_editor, tmp_path):
        """Test AsciiDoc→HTML conversion exception (lines 478-485)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "source.adoc"
        target_file = tmp_path / "output.pdf"

        # Mock asciidoc_api.execute to raise exception
        mock_editor._asciidoc_api.execute.side_effect = Exception("Conversion failed")

        # Exception is caught in try-except block (lines 478-485)
        result = manager.save_as_format_internal(target_file, "pdf")

        # Should return False and show error message
        assert result is False
        mock_editor.status_manager.show_message.assert_called()
        call_args = mock_editor.status_manager.show_message.call_args[0]
        assert call_args[0] == "critical"
        assert "Failed to convert AsciiDoc to HTML" in call_args[2]

    def test_non_asciidoc_format_asciidoc_api_none(self, mock_editor, tmp_path):
        """Test non-HTML format export when asciidoc_api is None (line 466, caught at 478)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._asciidoc_api = None  # Set to None
        mock_editor._current_file_path = tmp_path / "source.adoc"
        target_file = tmp_path / "output.pdf"

        # Exception is caught in try-except block (lines 478-485)
        result = manager.save_as_format_internal(target_file, "pdf")

        # Should return False and show error message
        assert result is False
        mock_editor.status_manager.show_message.assert_called()
        call_args = mock_editor.status_manager.show_message.call_args[0]
        assert call_args[0] == "critical"
        assert "Failed to convert AsciiDoc to HTML" in call_args[2]


@pytest.mark.fr_007
@pytest.mark.fr_023
@pytest.mark.edge_case
@pytest.mark.unit
class TestPandocAvailability:
    """Test Pandoc availability checking (line 442).

    FR-007: Save Files
    FR-023: Export DOCX
    """

    def test_save_as_format_pandoc_unavailable(self, mock_editor, tmp_path):
        """Test early return when Pandoc unavailable (line 442)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        target_file = tmp_path / "output.docx"

        # Set ui_state_manager.check_pandoc_availability to return False
        mock_editor.ui_state_manager.check_pandoc_availability.return_value = False

        result = manager.save_as_format_internal(target_file, "docx")

        # Should return False without attempting conversion
        assert result is False
        mock_editor.ui_state_manager.check_pandoc_availability.assert_called_once()


@pytest.mark.fr_007
@pytest.mark.fr_014
@pytest.mark.fr_023
@pytest.mark.unit
class TestSourceFormatDetection:
    """Test source format mapping (lines 451-460).

    FR-007: Save Files
    FR-014: Import Markdown
    FR-023: Export DOCX
    """

    def test_source_format_markdown(self, mock_editor, tmp_path):
        """Test source format detection for .md files (lines 451-460)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "source.md"
        target_file = tmp_path / "output.pdf"

        # Mock Path.write_text for temp file creation
        with patch("pathlib.Path.write_text"):
            result = manager.save_as_format_internal(target_file, "pdf")

            # Should emit pandoc conversion signal
            assert result is True
            mock_editor.request_pandoc_conversion.emit.assert_called_once()
            call_args = mock_editor.request_pandoc_conversion.emit.call_args[0]
            assert call_args[2] == "markdown"  # source_format argument

    def test_source_format_docx(self, mock_editor, tmp_path):
        """Test source format detection for .docx files (lines 451-460)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "source.docx"
        target_file = tmp_path / "output.pdf"

        # Mock Path.write_text for temp file creation
        with patch("pathlib.Path.write_text"):
            result = manager.save_as_format_internal(target_file, "pdf")

            # Should emit pandoc conversion signal
            assert result is True
            mock_editor.request_pandoc_conversion.emit.assert_called_once()
            call_args = mock_editor.request_pandoc_conversion.emit.call_args[0]
            assert call_args[2] == "docx"  # source_format argument

    def test_source_format_html(self, mock_editor, tmp_path):
        """Test source format detection for .html files (lines 451-460)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "source.html"
        target_file = tmp_path / "output.pdf"

        # Mock Path.write_text for temp file creation
        with patch("pathlib.Path.write_text"):
            result = manager.save_as_format_internal(target_file, "pdf")

            # Should emit pandoc conversion signal
            assert result is True
            mock_editor.request_pandoc_conversion.emit.assert_called_once()
            call_args = mock_editor.request_pandoc_conversion.emit.call_args[0]
            assert call_args[2] == "html"  # source_format argument


@pytest.mark.fr_007
@pytest.mark.edge_case
@pytest.mark.unit
class TestTempFileCreation:
    """Test temp file creation error handling (lines 489-499).

    FR-007: Save Files (temp file handling)
    """

    def test_temp_file_creation_exception(self, mock_editor, tmp_path):
        """Test exception during temp file creation (lines 489-499)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "source.md"
        target_file = tmp_path / "output.pdf"

        # Mock Path.write_text to raise an exception
        with patch("pathlib.Path.write_text", side_effect=Exception("Permission denied")):
            result = manager.save_as_format_internal(target_file, "pdf")

            # Should return False and show error message
            assert result is False
            mock_editor.status_manager.show_message.assert_called()
            call_args = mock_editor.status_manager.show_message.call_args[0]
            assert call_args[0] == "critical"
            assert "Failed to create temporary file" in call_args[2]


@pytest.mark.fr_007
@pytest.mark.fr_024
@pytest.mark.unit
class TestNonStandardExportFormats:
    """Test non-PDF/DOCX export signal emission (lines 522-531).

    FR-007: Save Files
    FR-024: Export Markdown
    """

    def test_markdown_export_signal_emission(self, mock_editor, tmp_path):
        """Test markdown export emits pandoc signal (lines 522-531)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        mock_editor._current_file_path = tmp_path / "source.adoc"
        target_file = tmp_path / "output.md"

        # Mock Path.write_text for temp file creation
        with patch("pathlib.Path.write_text"):
            result = manager.save_as_format_internal(target_file, "md")

            # Should emit signal for pandoc conversion
            assert result is True
            mock_editor.request_pandoc_conversion.emit.assert_called_once()
            call_args = mock_editor.request_pandoc_conversion.emit.call_args[0]
            assert call_args[1] == "md"  # format_type


@pytest.mark.fr_007
@pytest.mark.edge_case
@pytest.mark.unit
class TestNonAsciidocExtensionConversion:
    """Test non-AsciiDoc extension conversion (lines 352-355).

    FR-007: Save Files (extension handling)
    """

    def test_save_converts_non_adoc_extension(self, mock_editor, tmp_path):
        """Test save converts non-.adoc extensions (lines 352-355)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)

        # Set current file to have a .txt extension
        mock_editor._current_file_path = tmp_path / "test.txt"

        # Mock atomic_save_text to return True
        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ) as mock_save:
            result = manager.save_file()

            # Should succeed and convert to .adoc
            assert result is True

            # Verify atomic_save_text was called with .adoc extension
            mock_save.assert_called_once()
            saved_path = mock_save.call_args[0][0]
            assert saved_path.suffix == ".adoc"
            assert saved_path.name == "test.adoc"


@pytest.mark.fr_007
@pytest.mark.edge_case
@pytest.mark.unit
class TestFileOperationsCoverageEdgeCases:
    """Additional tests to achieve 99-100% coverage for file_operations_manager.

    FR-007: Save Files
    FR-006: Open Files
    """

    def test_html_atomic_save_failure_raises_oserror(self, mock_editor, tmp_path):
        """Test HTML save raises OSError when atomic save fails (line 433)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.html"

        # Mock atomic_save_text to return False
        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=False,
        ):
            result = manager.save_as_format_internal(file_path, "html", use_ai=False)

            # Should return False and show error
            assert result is False
            mock_editor.status_manager.show_message.assert_called_once()
            args = mock_editor.status_manager.show_message.call_args[0]
            assert args[0] == "critical"
            assert "Save Error" in args[1]

    def test_save_as_adoc_updates_file_state(self, mock_editor, tmp_path):
        """Test saving as adoc updates file state (lines 542-545)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.adoc"

        # Mock atomic_save_text
        with patch(
            "asciidoc_artisan.ui.file_save_handler.atomic_save_text",
            return_value=True,
        ):
            result = manager.save_as_format_internal(file_path, "adoc", use_ai=False)

            # Should succeed and update state
            assert result is True
            assert mock_editor._current_file_path == file_path
            assert mock_editor._settings.last_directory == str(file_path.parent)
            assert mock_editor._unsaved_changes is False
            mock_editor.status_manager.update_window_title.assert_called_once()

    def test_pdf_extraction_failure_shows_error(self, mock_editor, tmp_path):
        """Test PDF extraction failure shows error dialog (lines 577-583)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.pdf"

        # Mock pdf_extractor to return failure (lazy import inside method)
        with patch(
            "asciidoc_artisan.document_converter.pdf_extractor.convert_to_asciidoc",
            return_value=(False, "", "Encryption error"),
        ):
            manager._open_handler.open_pdf_with_extraction(file_path)

            # Should show error dialog
            mock_editor.status_manager.show_message.assert_called_once()
            args = mock_editor.status_manager.show_message.call_args[0]
            assert args[0] == "critical"
            assert "PDF Extraction Failed" in args[1]
            assert "Encryption error" in args[2]

    def test_open_non_adoc_pandoc_unavailable_returns_early(self, mock_editor, tmp_path):
        """Test opening non-adoc file returns early if Pandoc unavailable (line 601)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.docx"

        # Mock check_pandoc_availability to return False
        mock_editor.ui_state_manager.check_pandoc_availability = Mock(return_value=False)

        manager._open_handler.open_with_pandoc_conversion(file_path, ".docx")

        # Should return early without emitting signal
        mock_editor.request_pandoc_conversion.emit.assert_not_called()

    def test_load_asciidoc_large_file_error_handling(self, mock_editor, tmp_path):
        """Test large file handler error path (lines 666-671)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "large_test.adoc"
        file_path.write_text("= Test\n\nContent", encoding="utf-8")

        # Mock large file handler to return error
        mock_editor.large_file_handler.load_file_optimized = Mock(return_value=(False, None, "Memory error"))

        # Mock get_file_size_category to return "large" (in file_open_handler after MA refactoring)
        with patch(
            "asciidoc_artisan.ui.file_open_handler.LargeFileHandler.get_file_size_category",
            return_value="large",
        ):
            with pytest.raises(Exception, match="Memory error"):
                manager._open_handler.open_native_file(file_path)

    def test_load_asciidoc_normal_file_loads_content(self, mock_editor, tmp_path):
        """Test normal file loading calls load_content_into_editor (line 675)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.adoc"
        content = "= Test Document\n\nContent"
        file_path.write_text(content, encoding="utf-8")

        # Mock get_file_size_category to return "small" (in file_open_handler after MA refactoring)
        with patch(
            "asciidoc_artisan.ui.file_open_handler.LargeFileHandler.get_file_size_category",
            return_value="small",
        ):
            manager._open_handler.open_native_file(file_path)

            # Should load content into editor
            mock_editor.file_load_manager.load_content_into_editor.assert_called_once()
            loaded_content = mock_editor.file_load_manager.load_content_into_editor.call_args[0][0]
            assert loaded_content == content

    def test_determine_format_from_docx_filter(self, mock_editor, tmp_path):
        """Test format detection from DOCX filter (lines 695-696)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test"

        format_type, result_path = manager._determine_save_format(file_path, "Microsoft Word 365 Documents (*.docx)")

        assert format_type == "docx"
        assert result_path.suffix == ".docx"

    def test_determine_format_from_pdf_filter(self, mock_editor, tmp_path):
        """Test format detection from PDF filter (lines 699-700)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test"

        format_type, result_path = manager._determine_save_format(file_path, "Adobe Acrobat PDF Files (*.pdf)")

        assert format_type == "pdf"
        assert result_path.suffix == ".pdf"

    def test_determine_format_from_extension_md(self, mock_editor, tmp_path):
        """Test format detection from .md extension (line 704)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.md"

        format_type, result_path = manager._determine_save_format(file_path, "AsciiDoc Files (*.adoc)")

        assert format_type == "md"

    def test_determine_format_from_extension_docx(self, mock_editor, tmp_path):
        """Test format detection from .docx extension (lines 705-706)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.docx"

        format_type, result_path = manager._determine_save_format(file_path, "AsciiDoc Files (*.adoc)")

        assert format_type == "docx"

    def test_determine_format_from_extension_html(self, mock_editor, tmp_path):
        """Test format detection from .html extension (lines 707-708)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.html"

        format_type, result_path = manager._determine_save_format(file_path, "AsciiDoc Files (*.adoc)")

        assert format_type == "html"

    def test_determine_format_from_extension_pdf(self, mock_editor, tmp_path):
        """Test format detection from .pdf extension (lines 709-710)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test.pdf"

        format_type, result_path = manager._determine_save_format(file_path, "AsciiDoc Files (*.adoc)")

        assert format_type == "pdf"

    def test_determine_format_adds_docx_extension(self, mock_editor, tmp_path):
        """Test adding .docx extension when missing (lines 715-716)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test"

        format_type, result_path = manager._determine_save_format(file_path, "Microsoft Word 365 Documents (*.docx)")

        assert format_type == "docx"
        assert result_path.suffix == ".docx"

    def test_determine_format_adds_pdf_extension(self, mock_editor, tmp_path):
        """Test adding .pdf extension when missing (lines 719-720)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test"

        format_type, result_path = manager._determine_save_format(file_path, "Adobe Acrobat PDF Files (*.pdf)")

        assert format_type == "pdf"
        assert result_path.suffix == ".pdf"

    def test_determine_format_adds_adoc_extension(self, mock_editor, tmp_path):
        """Test adding .adoc extension when missing (lines 721-722)."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager

        manager = FileOperationsManager(mock_editor)
        file_path = tmp_path / "test"

        format_type, result_path = manager._determine_save_format(file_path, "AsciiDoc Files (*.adoc)")

        assert format_type == "adoc"
        assert result_path.suffix == ".adoc"
