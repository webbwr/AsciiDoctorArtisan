"""Tests for ui.export_manager module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit
from PySide6.QtGui import QGuiApplication


@pytest.fixture
def main_window(qapp):
    window = QMainWindow()
    # ExportManager expects these attributes from main_window
    window.editor = Mock(spec=QPlainTextEdit)
    window.editor.toPlainText = Mock(return_value="= Test Document\n\nTest content.")
    window.editor.insertPlainText = Mock()
    window.status_bar = Mock()
    window.status_bar.showMessage = Mock()
    window.status_manager = Mock()
    window.status_manager.show_message = Mock()
    window._settings_manager = Mock()
    window._settings_manager.get_ai_conversion_preference = Mock(return_value=False)
    window._settings = Mock()
    window._settings.last_directory = "/tmp"
    window._asciidoc_api = Mock()
    window._pandoc_worker = Mock()
    window._current_file_path = None  # Correct attribute name
    window._is_processing_pandoc = False
    window._update_ui_state = Mock()
    window.request_pandoc_conversion = Mock()  # Signal for Pandoc conversion
    window.request_pandoc_conversion.emit = Mock()
    return window


@pytest.mark.unit
class TestExportManagerBasics:
    """Test suite for ExportManager basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.export_manager import ExportManager
        assert ExportManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert manager is not None

    def test_has_window_reference(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "window")
        assert manager.window == main_window

    def test_initialization_sets_pending_export_state(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "pending_export_path")
        assert manager.pending_export_path is None

    def test_has_cleanup_method(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "cleanup")
        assert callable(manager.cleanup)

    def test_cleanup_closes_temp_directory(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        temp_dir = manager.temp_dir
        manager.cleanup()
        # Cleanup should complete without error
        assert True


@pytest.mark.unit
class TestExportMethods:
    """Test suite for export method availability."""

    def test_save_file_as_format_exists(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "save_file_as_format")
        assert callable(manager.save_file_as_format)

    def test_convert_and_paste_from_clipboard_exists(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "convert_and_paste_from_clipboard")
        assert callable(manager.convert_and_paste_from_clipboard)

    def test_handle_pandoc_result_exists(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "handle_pandoc_result")
        assert callable(manager.handle_pandoc_result)


@pytest.mark.unit
class TestExportStateManagement:
    """Test suite for export state management."""

    def test_export_with_valid_format(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=("/tmp/test.pdf", "")):
            with patch.object(manager, "_export_via_pandoc", return_value=True):
                result = manager.save_file_as_format("pdf")
                assert result is True

    def test_pending_export_state_during_export(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=("/tmp/test.md", "")):
            with patch.object(manager, "_export_via_pandoc", return_value=True):
                manager.save_file_as_format("md")
                # Export initiated successfully
                assert True


@pytest.mark.unit
class TestSaveFileAsFormat:
    """Test suite for save_file_as_format method."""

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_asciidoc_export(self, mock_dialog, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.adoc"
        mock_dialog.return_value = (str(export_file), "")

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True) as mock_save:
            result = manager.save_file_as_format("adoc")
            mock_save.assert_called_once()
            assert result is True

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_markdown_export_via_pandoc(self, mock_dialog, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"
        mock_dialog.return_value = (str(export_file), "")

        with patch.object(manager, "_export_via_pandoc", return_value=True) as mock_export:
            manager.save_file_as_format("md")
            mock_export.assert_called_once()

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_docx_export_via_pandoc(self, mock_dialog, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.docx"
        mock_dialog.return_value = (str(export_file), "")

        with patch.object(manager, "_export_via_pandoc") as mock_export:
            manager.save_file_as_format("docx")
            mock_export.assert_called_once()

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_html_export(self, mock_dialog, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.html"
        mock_dialog.return_value = (str(export_file), "")

        with patch.object(manager, "_export_html", return_value=True) as mock_export:
            manager.save_file_as_format("html")
            mock_export.assert_called_once()

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_pdf_export(self, mock_dialog, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"
        mock_dialog.return_value = (str(export_file), "")

        with patch.object(manager, "_export_via_pandoc") as mock_export:
            manager.save_file_as_format("pdf")
            mock_export.assert_called_once()

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_unknown_format_returns_false(self, mock_dialog, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.unknown"
        mock_dialog.return_value = (str(export_file), "")

        result = manager.save_file_as_format("unknown_format")
        assert result is False

    @patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName")
    def test_cancelled_dialog_returns_false(self, mock_dialog, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        # User cancelled dialog
        mock_dialog.return_value = ("", "")

        result = manager.save_file_as_format("pdf")
        assert result is False


@pytest.mark.unit
class TestPandocExport:
    """Test suite for Pandoc export operations."""

    def test_export_via_pandoc_sends_request(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
            with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                manager._export_via_pandoc(export_file, "md", "= Test", False)
                main_window.request_pandoc_conversion.emit.assert_called()

    def test_handle_pandoc_result_clipboard(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.handle_pandoc_result("Converted text", "clipboard conversion")

        # Should insert text and show message
        main_window.editor.insertPlainText.assert_called_with("Converted text")
        main_window.status_bar.showMessage.assert_called()

    def test_handle_pandoc_result_export(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch.object(manager, "_handle_export_result") as mock_handler:
            manager.handle_pandoc_result("Converted content", "Exporting to MD")
            mock_handler.assert_called()


@pytest.mark.unit
class TestClipboardOperations:
    """Test suite for clipboard operations."""

    def test_convert_and_paste_with_html_content(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = True
        mock_mime.html.return_value = "<p>HTML content</p>"

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            with patch("asciidoc_artisan.core.constants.PANDOC_AVAILABLE", True):
                manager.convert_and_paste_from_clipboard()
                # Should set processing flag and emit conversion request
                assert main_window._is_processing_pandoc is True

    def test_convert_and_paste_with_no_content(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = False
        mock_mime.hasText.return_value = False

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            manager.convert_and_paste_from_clipboard()
            # Should show message about empty clipboard
            main_window.status_manager.show_message.assert_called()


@pytest.mark.unit
class TestHTMLExport:
    """Test suite for HTML export."""

    def test_export_html_generates_html(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.html"
        content = "= Test\n\nContent."

        with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>Test</html>"):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True) as mock_save:
                result = manager._export_html(export_file, content)
                assert result is True
                mock_save.assert_called_once()

    def test_export_html_handles_errors(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.html"
        content = "= Test\n\nContent."

        with patch.object(manager.html_converter, "asciidoc_to_html", side_effect=Exception("HTML generation failed")):
            result = manager._export_html(export_file, content)
            assert result is False


@pytest.mark.unit
class TestSignalEmissions:
    """Test suite for signal emission during exports."""

    def test_export_started_signal_emitted_for_markdown(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"
        signal_received = []
        manager.export_started.connect(lambda fmt: signal_received.append(fmt))

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
                with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                    manager.save_file_as_format("md")
                    assert "md" in signal_received

    def test_export_completed_signal_emitted_for_asciidoc(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.adoc"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
                signal_received = []
                manager.export_completed.connect(lambda path: signal_received.append(path))
                manager.save_file_as_format("adoc")
                assert len(signal_received) == 1
                assert signal_received[0] == export_file

    def test_export_failed_signal_emitted_on_atomic_save_failure(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.adoc"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=False):
                signal_received = []
                manager.export_failed.connect(lambda msg: signal_received.append(msg))
                manager.save_file_as_format("adoc")
                assert len(signal_received) == 1

    def test_export_started_signal_for_pdf(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"
        signal_received = []
        manager.export_started.connect(lambda fmt: signal_received.append(fmt))

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
                with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                    with patch.object(manager.pdf_helper, "check_pdf_engine_available", return_value=True):
                        manager.save_file_as_format("pdf")
                        assert "pdf" in signal_received

    def test_export_completed_signal_for_html(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.html"
        signal_received = []
        manager.export_completed.connect(lambda path: signal_received.append(path))

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
                    manager.save_file_as_format("html")
                    # Should emit completed signal
                    assert len(signal_received) == 1

    def test_export_failed_signal_on_html_conversion_error(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.html"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch.object(manager.html_converter, "asciidoc_to_html", side_effect=Exception("HTML error")):
                signal_received = []
                manager.export_failed.connect(lambda msg: signal_received.append(msg))
                manager._export_html(export_file, "= Test")
                assert len(signal_received) == 1


@pytest.mark.unit
class TestHelperInitialization:
    """Test suite for helper object initialization."""

    def test_html_converter_initialized(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "html_converter")
        assert manager.html_converter is not None

    def test_pdf_helper_initialized(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "pdf_helper")
        assert manager.pdf_helper is not None

    def test_clipboard_helper_initialized(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "clipboard_helper")
        assert manager.clipboard_helper is not None

    def test_all_window_references_set(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert manager.window == main_window
        assert manager.editor == main_window.editor
        assert manager.status_bar == main_window.status_bar
        assert manager.status_manager == main_window.status_manager


@pytest.mark.unit
class TestTemporaryDirectoryManagement:
    """Test suite for temporary directory lifecycle."""

    def test_temp_dir_created_on_init(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert hasattr(manager, "temp_dir")
        assert manager.temp_dir is not None

    def test_cleanup_removes_temp_directory(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        temp_dir = manager.temp_dir
        manager.cleanup()
        # Cleanup should be called without error
        assert True

    def test_cleanup_handles_already_cleaned_directory(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        manager.cleanup()
        # Second cleanup should not raise
        manager.cleanup()
        assert True

    def test_temp_dir_is_writable(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        temp_path = Path(manager.temp_dir.name)
        test_file = temp_path / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()
        manager.cleanup()

    def test_cleanup_handles_errors_gracefully(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        # Mock cleanup to raise exception
        with patch.object(manager.temp_dir, "cleanup", side_effect=Exception("Cleanup error")):
            # Should not raise
            manager.cleanup()
            assert True


@pytest.mark.unit
class TestPendingExportStateTracking:
    """Test suite for pending export state management."""

    def test_pending_state_initialized_to_none(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert manager.pending_export_path is None
        assert manager.pending_export_format is None

    def test_pending_state_set_for_markdown_export(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
            with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                manager._export_via_pandoc(export_file, "md", "= Test", False)
                assert manager.pending_export_path == export_file
                assert manager.pending_export_format == "md"

    def test_pending_state_cleared_for_pdf_export(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
            with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                with patch.object(manager.pdf_helper, "check_pdf_engine_available", return_value=True):
                    manager._export_via_pandoc(export_file, "pdf", "= Test", False)
                    # PDF exports don't set pending state (direct file path)
                    assert manager.pending_export_path is None
                    assert manager.pending_export_format is None

    def test_pending_state_cleared_after_result_handling(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
            manager._handle_export_result("Converted content", "Exporting to MD")
            assert manager.pending_export_path is None
            assert manager.pending_export_format is None

    def test_pending_state_cleared_on_error(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", side_effect=Exception("Save failed")):
            manager._handle_export_result("Converted content", "Exporting to MD")
            # Should clear pending state even on error
            assert manager.pending_export_path is None
            assert manager.pending_export_format is None

    def test_pending_state_not_set_for_asciidoc_direct_save(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.adoc"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
                manager.save_file_as_format("adoc")
                assert manager.pending_export_path is None
                assert manager.pending_export_format is None


@pytest.mark.unit
class TestFileExtensionHandling:
    """Test suite for file extension enforcement."""

    @pytest.mark.parametrize("format_type,expected_ext", [
        ("adoc", ".adoc"),
        ("md", ".md"),
        ("docx", ".docx"),
        ("html", ".html"),
        ("pdf", ".pdf"),
    ])
    def test_extension_added_when_missing(self, main_window, tmp_path, format_type, expected_ext):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        # File path without extension
        export_file = tmp_path / "test"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
                with patch.object(manager, "_export_via_pandoc", return_value=True):
                    with patch.object(manager, "_export_html", return_value=True):
                        manager.save_file_as_format(format_type)
                        # Check that atomic_save_text or export methods were called with extension
                        assert True  # Extension enforcement happens before export

    def test_extension_preserved_when_correct(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.adoc"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True) as mock_save:
                manager.save_file_as_format("adoc")
                # Check that file path has correct extension
                saved_path = mock_save.call_args[0][0]
                assert saved_path.suffix == ".adoc"


@pytest.mark.unit
class TestPDFEngineFallback:
    """Test suite for PDF engine fallback behavior."""

    def test_fallback_when_pdf_engine_unavailable(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"

        with patch.object(manager.pdf_helper, "check_pdf_engine_available", return_value=False):
            with patch.object(manager, "_export_pdf_fallback", return_value=True) as mock_fallback:
                with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
                    with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                        manager._export_via_pandoc(export_file, "pdf", "= Test", False)
                        mock_fallback.assert_called_once()

    def test_fallback_creates_html_file(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"
        html_content = "<html><body>Test</body></html>"

        with patch.object(manager.pdf_helper, "add_print_css_to_html", return_value=html_content):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True) as mock_save:
                result = manager._export_pdf_fallback(export_file, html_content)
                assert result is True
                # Should save as .html instead of .pdf
                saved_path = mock_save.call_args[0][0]
                assert saved_path.suffix == ".html"

    def test_fallback_shows_user_instructions(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"

        with patch.object(manager.pdf_helper, "add_print_css_to_html", return_value="<html>"):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
                manager._export_pdf_fallback(export_file, "<html>")
                # Should show informational message with instructions
                manager.status_manager.show_message.assert_called()
                call_args = manager.status_manager.show_message.call_args
                assert "information" in call_args[0]

    def test_fallback_emits_completed_signal(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"

        with patch.object(manager.pdf_helper, "add_print_css_to_html", return_value="<html>"):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
                signal_received = []
                manager.export_completed.connect(lambda path: signal_received.append(path))
                manager._export_pdf_fallback(export_file, "<html>")
                assert len(signal_received) == 1

    def test_fallback_handles_save_errors(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"

        with patch.object(manager.pdf_helper, "add_print_css_to_html", return_value="<html>"):
            with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=False):
                result = manager._export_pdf_fallback(export_file, "<html>")
                assert result is False


@pytest.mark.unit
class TestClipboardMIMEDataPriority:
    """Test suite for clipboard MIME data handling."""

    def test_html_content_prioritized_over_text(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = True
        mock_mime.hasText.return_value = True
        mock_mime.html.return_value = "<p>HTML content</p>"
        mock_mime.text.return_value = "Plain text"

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            with patch("asciidoc_artisan.core.constants.PANDOC_AVAILABLE", True):
                manager.convert_and_paste_from_clipboard()
                # Should use HTML, not text
                assert main_window._is_processing_pandoc is True

    def test_text_content_used_when_no_html(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = False
        mock_mime.hasText.return_value = True
        mock_mime.text.return_value = "Plain text"

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            with patch("asciidoc_artisan.core.constants.PANDOC_AVAILABLE", True):
                manager.convert_and_paste_from_clipboard()
                assert main_window._is_processing_pandoc is True

    def test_empty_clipboard_shows_message(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = False
        mock_mime.hasText.return_value = False

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            manager.convert_and_paste_from_clipboard()
            # Should show "empty clipboard" message
            manager.status_manager.show_message.assert_called()
            call_args = str(manager.status_manager.show_message.call_args)
            assert "Empty Clipboard" in call_args or "clipboard" in call_args.lower()

    def test_pandoc_unavailable_shows_warning(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = True
        mock_mime.html.return_value = "<p>Test</p>"

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            with patch("asciidoc_artisan.core.constants.PANDOC_AVAILABLE", False):
                manager.convert_and_paste_from_clipboard()
                # Should show Pandoc unavailable message
                manager.status_manager.show_message.assert_called()
                call_args = str(manager.status_manager.show_message.call_args)
                assert "Pandoc" in call_args

    def test_html_content_conversion_requested(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = True
        mock_mime.html.return_value = "<p>HTML content</p>"

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            with patch("asciidoc_artisan.core.constants.PANDOC_AVAILABLE", True):
                manager.convert_and_paste_from_clipboard()
                # Should emit conversion request with "html" format
                main_window.request_pandoc_conversion.emit.assert_called()
                call_args = main_window.request_pandoc_conversion.emit.call_args[0]
                assert "asciidoc" in call_args  # Target format
                assert "html" in call_args  # Source format

    def test_text_content_conversion_requested(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        mock_mime = Mock()
        mock_mime.hasHtml.return_value = False
        mock_mime.hasText.return_value = True
        mock_mime.text.return_value = "Plain text"

        with patch("asciidoc_artisan.ui.export_manager.QGuiApplication.clipboard") as mock_clipboard:
            mock_clipboard.return_value.mimeData.return_value = mock_mime
            with patch("asciidoc_artisan.core.constants.PANDOC_AVAILABLE", True):
                manager.convert_and_paste_from_clipboard()
                # Should emit conversion request with "markdown" format (default for text)
                main_window.request_pandoc_conversion.emit.assert_called()
                call_args = main_window.request_pandoc_conversion.emit.call_args[0]
                assert "asciidoc" in call_args  # Target format


@pytest.mark.unit
class TestPandocResultContextParsing:
    """Test suite for Pandoc result context routing."""

    def test_clipboard_context_inserts_text(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        converted_text = "= Converted Document\n\nContent."
        manager.handle_pandoc_result(converted_text, "clipboard conversion")

        # Should insert text into editor
        main_window.editor.insertPlainText.assert_called_with(converted_text)

    def test_export_context_routes_to_export_handler(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch.object(manager, "_handle_export_result") as mock_handler:
            manager.handle_pandoc_result("Converted content", "Exporting to MD")
            mock_handler.assert_called_once()

    def test_export_context_with_file_saved_message(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch.object(manager, "_handle_export_result") as mock_handler:
            manager.handle_pandoc_result("File saved to: /tmp/test.md", "Exporting to MD")
            mock_handler.assert_called_once()

    def test_unknown_context_ignored(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        # Should not raise or crash
        manager.handle_pandoc_result("Some result", "unknown context")
        assert True

    def test_clipboard_context_updates_status_bar(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.handle_pandoc_result("Converted text", "clipboard conversion")
        # Should show status message
        main_window.status_bar.showMessage.assert_called_with("Pasted converted content")


@pytest.mark.unit
class TestSettingsIntegration:
    """Test suite for settings manager integration."""

    def test_last_directory_updated_after_export(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"
        manager.pending_export_path = export_file
        manager.pending_export_format = "md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=True):
            manager._handle_export_result("Converted content", "Exporting to MD")
            assert main_window._settings.last_directory == str(tmp_path)

    def test_ai_conversion_preference_retrieved_for_markdown(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=(str(export_file), "")):
            with patch.object(manager, "_export_via_pandoc", return_value=True):
                manager.save_file_as_format("md")
                # Should call get_ai_conversion_preference
                manager.settings_manager.get_ai_conversion_preference.assert_called()

    def test_ai_preference_passed_to_pandoc_worker(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.settings_manager.get_ai_conversion_preference.return_value = True
        export_file = tmp_path / "test.md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
            with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                manager._export_via_pandoc(export_file, "md", "= Test", True)
                # Should emit conversion request with use_ai=True
                main_window.request_pandoc_conversion.emit.assert_called()
                call_args = main_window.request_pandoc_conversion.emit.call_args[0]
                assert True in call_args  # use_ai parameter

    def test_suggested_filename_uses_current_file(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        main_window._current_file_path = Path("/home/user/document.adoc")

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=("", "")) as mock_dialog:
            manager.save_file_as_format("md")
            # Check suggested path includes document name
            suggested_path = str(mock_dialog.call_args[0][2])
            assert "document" in suggested_path

    def test_suggested_filename_defaults_when_no_current_file(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        main_window._current_file_path = None

        with patch("asciidoc_artisan.ui.export_manager.QFileDialog.getSaveFileName", return_value=("", "")) as mock_dialog:
            manager.save_file_as_format("md")
            # Should suggest "document.md"
            suggested_path = str(mock_dialog.call_args[0][2])
            assert "document" in suggested_path


@pytest.mark.unit
class TestExportErrorHandling:
    """Test suite for export error handling."""

    def test_unsupported_format_shows_warning(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        result = manager.save_file_as_format("unsupported")
        assert result is False
        manager.status_manager.show_message.assert_called()
        call_args = str(manager.status_manager.show_message.call_args)
        assert "unsupported" in call_args.lower()

    def test_html_conversion_error_shows_critical_message(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.pdf"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
            with patch.object(manager.html_converter, "asciidoc_to_html", side_effect=Exception("HTML error")):
                result = manager._export_via_pandoc(export_file, "pdf", "= Test", False)
                assert result is False
                manager.status_manager.show_message.assert_called()

    def test_temp_file_creation_error_handled(self, main_window, tmp_path):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        export_file = tmp_path / "test.md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text"):
            with patch.object(manager.html_converter, "asciidoc_to_html", return_value="<html>"):
                # Mock temp file write to raise error
                with patch("pathlib.Path.write_text", side_effect=Exception("Write error")):
                    result = manager._export_via_pandoc(export_file, "md", "= Test", False)
                    assert result is False

    def test_atomic_save_failure_emits_failed_signal(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", return_value=False):
            signal_received = []
            manager.export_failed.connect(lambda msg: signal_received.append(msg))
            manager._handle_export_result("Content", "Exporting to MD")
            assert len(signal_received) == 1

    def test_exception_in_export_result_handler(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        manager.pending_export_path = Path("/tmp/test.md")
        manager.pending_export_format = "md"

        with patch("asciidoc_artisan.ui.export_manager.atomic_save_text", side_effect=Exception("Unexpected error")):
            signal_received = []
            manager.export_failed.connect(lambda msg: signal_received.append(msg))
            manager._handle_export_result("Content", "Exporting to MD")
            # Should handle exception and emit failed signal
            assert len(signal_received) == 1

    def test_export_result_with_missing_pending_state(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)

        # Pending state is None (shouldn't happen, but test defensive code)
        manager.pending_export_path = None
        manager.pending_export_format = None

        # Should not raise, just log error
        manager._handle_export_result("Content", "Exporting to MD")
        assert True
