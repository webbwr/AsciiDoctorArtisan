"""Tests for ui.file_operations_manager module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


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
    editor.large_file_handler.load_file_optimized = Mock(
        return_value=(True, "= Test\n\nContent", None)
    )

    # Preview widget
    editor.preview = Mock()
    editor.preview.setHtml = Mock()

    # Signals
    editor.request_pandoc_conversion = Mock()
    editor.request_pandoc_conversion.emit = Mock()

    # UI state update
    editor._update_ui_state = Mock()

    return editor


@pytest.mark.unit
class TestFileOperationsManagerBasics:
    """Test suite for FileOperationsManager basic functionality."""

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


@pytest.mark.unit
class TestOpenFile:
    """Test suite for open_file method."""

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getOpenFileName")
    def test_open_file_prompts_save_if_unsaved_changes(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        mock_editor._unsaved_changes = True
        mock_editor.status_manager.prompt_save_before_action = Mock(return_value=False)

        manager.open_file()

        # Should prompt to save and return early if user cancels
        mock_editor.status_manager.prompt_save_before_action.assert_called_once()
        mock_dialog.assert_not_called()

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getOpenFileName")
    def test_open_file_blocked_when_processing(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        manager._is_processing_pandoc = True
        manager.open_file()

        # Should show warning and not open dialog
        mock_editor.status_manager.show_message.assert_called_once()
        mock_dialog.assert_not_called()

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getOpenFileName")
    def test_open_file_cancelled_dialog_returns_early(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        # User cancels dialog
        mock_dialog.return_value = ("", "")
        manager.open_file()

        # Should not attempt to load any file
        mock_editor.file_load_manager.load_content_into_editor.assert_not_called()

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getOpenFileName")
    def test_open_pdf_calls_pdf_extraction(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf")
        mock_dialog.return_value = (str(pdf_file), "")

        with patch.object(manager, "_open_pdf_with_extraction") as mock_pdf:
            manager.open_file()
            mock_pdf.assert_called_once_with(pdf_file)

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getOpenFileName")
    def test_open_docx_calls_pandoc_conversion(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"
        docx_file.write_text("fake docx")
        mock_dialog.return_value = (str(docx_file), "")

        with patch.object(manager, "_open_with_pandoc_conversion") as mock_pandoc:
            manager.open_file()
            mock_pandoc.assert_called_once()

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getOpenFileName")
    def test_open_asciidoc_loads_directly(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        adoc_file = tmp_path / "test.adoc"
        adoc_file.write_text("= Test\n\nContent")
        mock_dialog.return_value = (str(adoc_file), "")

        with patch.object(manager, "_open_native_file") as mock_native:
            manager.open_file()
            mock_native.assert_called_once_with(adoc_file)


@pytest.mark.unit
class TestSaveFile:
    """Test suite for save_file method."""

    def test_save_file_uses_current_path_when_available(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        current_file = tmp_path / "test.adoc"
        mock_editor._current_file_path = current_file

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text", return_value=True):
            result = manager.save_file(save_as=False)

        # Should save to current path without showing dialog
        assert result is True
        assert mock_editor._unsaved_changes is False

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getSaveFileName")
    def test_save_file_shows_dialog_when_save_as(self, mock_dialog, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        save_file = tmp_path / "new.adoc"
        mock_dialog.return_value = (str(save_file), "")

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text", return_value=True):
            result = manager.save_file(save_as=True)

        # Should show dialog even if current file exists
        mock_dialog.assert_called_once()
        assert result is True

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getSaveFileName")
    def test_save_file_cancelled_dialog_returns_false(self, mock_dialog, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        # User cancels dialog
        mock_dialog.return_value = ("", "")
        result = manager.save_file(save_as=True)

        # Should return False
        assert result is False

    @patch("asciidoc_artisan.ui.file_operations_manager.QFileDialog.getSaveFileName")
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

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text", return_value=True):
            manager.save_file()

        # Should clear unsaved changes flag
        assert mock_editor._unsaved_changes is False


@pytest.mark.unit
class TestSaveAsFormatInternal:
    """Test suite for save_as_format_internal method."""

    def test_save_as_asciidoc_uses_atomic_save(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        adoc_file = tmp_path / "test.adoc"

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text", return_value=True) as mock_save:
            result = manager.save_as_format_internal(adoc_file, "adoc")

        # Should use atomic_save_text
        mock_save.assert_called_once()
        assert result is True

    def test_save_as_html_uses_asciidoc_api(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        html_file = tmp_path / "test.html"

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text", return_value=True):
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

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text"):
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

        with patch("asciidoc_artisan.ui.file_operations_manager.atomic_save_text"):
            manager.save_as_format_internal(pdf_file, "pdf")

        # Should emit pandoc conversion signal for PDF
        mock_editor.request_pandoc_conversion.emit.assert_called()


@pytest.mark.unit
class TestPDFExtraction:
    """Test suite for PDF extraction functionality."""

    def test_pdf_extraction_checks_availability(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake")

        # Patch where pdf_extractor is imported (inside the method)
        with patch("asciidoc_artisan.document_converter.pdf_extractor") as mock_pdf:
            mock_pdf.is_available.return_value = True
            mock_pdf.convert_to_asciidoc.return_value = (True, "= Test", None)

            manager._open_pdf_with_extraction(pdf_file)

            # Should check if PDF extractor is available
            mock_pdf.is_available.assert_called_once()

    def test_pdf_extraction_shows_error_if_unavailable(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"

        # Patch where pdf_extractor is imported (inside the method)
        with patch("asciidoc_artisan.document_converter.pdf_extractor") as mock_pdf:
            mock_pdf.is_available.return_value = False

            manager._open_pdf_with_extraction(pdf_file)

            # Should show error message
            mock_editor.status_manager.show_message.assert_called_once()
            assert "PyMuPDF" in str(mock_editor.status_manager.show_message.call_args)

    def test_pdf_extraction_loads_content_on_success(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        pdf_file = tmp_path / "test.pdf"

        # Patch where pdf_extractor is imported (inside the method)
        with patch("asciidoc_artisan.document_converter.pdf_extractor") as mock_pdf:
            mock_pdf.is_available.return_value = True
            mock_pdf.convert_to_asciidoc.return_value = (True, "= Extracted Text", None)

            manager._open_pdf_with_extraction(pdf_file)

            # Should load extracted content into editor
            mock_editor.file_load_manager.load_content_into_editor.assert_called_once()


@pytest.mark.unit
class TestPandocConversion:
    """Test suite for Pandoc conversion workflow."""

    def test_pandoc_conversion_checks_availability(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"fake docx")

        manager._open_with_pandoc_conversion(docx_file, ".docx")

        # Should check Pandoc availability
        mock_editor.ui_state_manager.check_pandoc_availability.assert_called_once()

    def test_pandoc_conversion_sets_processing_flag(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        docx_file = tmp_path / "test.docx"
        docx_file.write_bytes(b"fake docx")

        manager._open_with_pandoc_conversion(docx_file, ".docx")

        # Should set processing flag
        assert manager._is_processing_pandoc is True
        assert manager._pending_file_path == docx_file

    def test_pandoc_conversion_emits_signal(self, mock_editor, tmp_path):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(mock_editor)

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test Markdown")

        manager._open_with_pandoc_conversion(md_file, ".md")

        # Should emit pandoc conversion signal
        mock_editor.request_pandoc_conversion.emit.assert_called_once()


@pytest.mark.unit
class TestDetermineSaveFormat:
    """Test suite for _determine_save_format method."""

    def test_determine_format_from_filter(self, mock_editor):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        from asciidoc_artisan.core import MD_FILTER
        manager = FileOperationsManager(mock_editor)

        file_path = Path("/tmp/test")
        # Use actual MD_FILTER constant from core
        format_type, corrected_path = manager._determine_save_format(
            file_path, MD_FILTER
        )

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
        format_type, corrected_path = manager._determine_save_format(
            file_path, "HTML Files (*.html *.htm)"
        )

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
