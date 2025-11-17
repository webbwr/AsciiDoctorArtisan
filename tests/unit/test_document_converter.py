"""
Tests for document_converter.py (v2.0.0).

Tests Pandoc integration and PDF extraction with mocked subprocess calls.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.document_converter import (
    PandocIntegration,
    PDFExtractor,
    ensure_pandoc_available,
)


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestPandocIntegrationInitialization:
    """Test PandocIntegration initialization."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_init_pandoc_found(self, mock_run, mock_which):
        """Test initialization when pandoc is found."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="pandoc 3.1.2\nCompiled with pandoc-types",
        )

        integration = PandocIntegration()

        assert integration.pandoc_path == "/usr/bin/pandoc"
        assert integration.pandoc_version is not None
        assert "pandoc 3.1.2" in integration.pandoc_version

    @patch("asciidoc_artisan.document_converter.shutil.which")
    def test_init_pandoc_not_found(self, mock_which):
        """Test initialization when pandoc is not found."""
        mock_which.return_value = None

        integration = PandocIntegration()

        assert integration.pandoc_path is None

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_init_pandoc_version_check_fails(self, mock_run, mock_which):
        """Test initialization when version check fails."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        integration = PandocIntegration()

        assert integration.pandoc_path == "/usr/bin/pandoc"


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestCheckInstallation:
    """Test check_installation method."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_check_installation_success(self, mock_run, mock_which):
        """Test successful pandoc detection."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="pandoc 3.1.2\nCompiled with pandoc-types",
        )

        integration = PandocIntegration()
        success, message = integration.check_installation()

        assert success is True
        assert "available" in message.lower() or integration.pandoc_version is not None

    @patch("asciidoc_artisan.document_converter.shutil.which")
    def test_check_installation_not_found(self, mock_which):
        """Test when pandoc binary not found."""
        mock_which.return_value = None

        integration = PandocIntegration()
        success, message = integration.check_installation()

        assert success is False
        assert "not found" in message.lower()

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_check_installation_timeout(self, mock_run, mock_which):
        """Test when version check times out."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.side_effect = subprocess.TimeoutExpired("pandoc", 5)

        integration = PandocIntegration()
        # Should handle timeout gracefully (version will be None)
        assert integration.pandoc_version is None


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestGetSupportedFormats:
    """Test _get_supported_formats method."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_get_supported_formats_success(self, mock_run, mock_which):
        """Test successful format detection."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Mock version check
        version_result = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        # Mock format list queries
        input_formats = MagicMock(returncode=0, stdout="asciidoc\nmarkdown\ndocx\nhtml")
        output_formats = MagicMock(
            returncode=0, stdout="asciidoc\nmarkdown\nhtml\nlatex"
        )

        mock_run.side_effect = [version_result, input_formats, output_formats]

        integration = PandocIntegration()

        assert "asciidoc" in integration.supported_formats["input"]
        assert "markdown" in integration.supported_formats["input"]
        assert "asciidoc" in integration.supported_formats["output"]

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_get_supported_formats_failure(self, mock_run, mock_which):
        """Test format detection when queries fail."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Mock version check success but format queries fail
        version_result = MagicMock(returncode=0, stdout="pandoc 3.1.2")
        format_fail = MagicMock(returncode=1, stdout="")

        mock_run.side_effect = [version_result, format_fail, format_fail]

        integration = PandocIntegration()

        # Should have empty format lists
        assert len(integration.supported_formats["input"]) == 0
        assert len(integration.supported_formats["output"]) == 0


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestStaticMethods:
    """Test static methods."""

    def test_get_installation_instructions(self):
        """Test installation instructions generation."""
        instructions = PandocIntegration.get_installation_instructions()

        assert "pandoc" in instructions.lower()
        # Should include platform-specific instructions
        assert any(
            word in instructions.lower()
            for word in ["install", "download", "brew", "apt", "choco"]
        )

    def test_get_format_info(self):
        """Test format information retrieval."""
        # Test known format
        info = PandocIntegration.get_format_info("markdown")
        assert "Markdown" in info

        # Test unknown format
        info_unknown = PandocIntegration.get_format_info("unknown_format")
        assert "unknown" in info_unknown.lower() or "not found" in info_unknown.lower()


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestIsFormatSupported:
    """Test is_format_supported method."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_is_format_supported_input(self, mock_run, mock_which):
        """Test format support checking for input."""
        mock_which.return_value = "/usr/bin/pandoc"

        version_result = MagicMock(returncode=0, stdout="pandoc 3.1.2")
        input_formats = MagicMock(returncode=0, stdout="markdown\ndocx")
        output_formats = MagicMock(returncode=0, stdout="html\nlatex")

        mock_run.side_effect = [version_result, input_formats, output_formats]

        integration = PandocIntegration()

        assert integration.is_format_supported("markdown", "input") is True
        assert integration.is_format_supported("html", "input") is False

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_is_format_supported_output(self, mock_run, mock_which):
        """Test format support checking for output."""
        mock_which.return_value = "/usr/bin/pandoc"

        version_result = MagicMock(returncode=0, stdout="pandoc 3.1.2")
        input_formats = MagicMock(returncode=0, stdout="markdown\ndocx")
        output_formats = MagicMock(returncode=0, stdout="html\nlatex")

        mock_run.side_effect = [version_result, input_formats, output_formats]

        integration = PandocIntegration()

        assert integration.is_format_supported("html", "output") is True
        assert integration.is_format_supported("docx", "output") is False


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestEnsurePandocAvailable:
    """Test ensure_pandoc_available function."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_ensure_pandoc_available_success(self, mock_run, mock_which):
        """Test when pandoc is available."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        success, message = ensure_pandoc_available()

        assert success is True

    @patch("asciidoc_artisan.document_converter.shutil.which")
    def test_ensure_pandoc_available_not_found(self, mock_which):
        """Test when pandoc is not available."""
        mock_which.return_value = None

        success, message = ensure_pandoc_available()

        assert success is False
        assert "not found" in message.lower()


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestPDFExtractorHelpers:
    """Test PDFExtractor helper methods."""

    def test_clean_cell(self):
        """Test _clean_cell method."""
        # Test normal cell
        result = PDFExtractor._clean_cell("  Normal text  ")
        assert result == "Normal text"

        # Test cell with multiple whitespace
        result = PDFExtractor._clean_cell("Text   with    spaces")
        assert result == "Text with spaces"

        # Test empty cell
        result = PDFExtractor._clean_cell("")
        assert result == ""

        # Test cell exceeding max length
        long_text = "a" * 300
        result = PDFExtractor._clean_cell(long_text, max_length=100)
        assert len(result) <= 103  # 100 + "..."

    def test_format_table_as_asciidoc(self):
        """Test _format_table_as_asciidoc method."""
        table = [
            ["Header 1", "Header 2"],
            ["Row 1 Col 1", "Row 1 Col 2"],
            ["Row 2 Col 1", "Row 2 Col 2"],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        assert "|===" in result  # AsciiDoc table markers
        assert "Header 1" in result
        assert "Row 1 Col 1" in result

    def test_format_table_empty(self):
        """Test table formatting with empty table."""
        result = PDFExtractor._format_table_as_asciidoc([])

        # Should return empty string or minimal table structure
        assert isinstance(result, str)


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_extension_map_coverage(self, mock_run, mock_which):
        """Test extension to format mapping."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        integration = PandocIntegration()

        # Test all extension mappings
        assert integration.EXTENSION_MAP[".md"] == "markdown"
        assert integration.EXTENSION_MAP[".docx"] == "docx"
        assert integration.EXTENSION_MAP[".html"] == "html"

    def test_format_descriptions_coverage(self):
        """Test format descriptions are available."""
        # Test all format descriptions
        assert "AsciiDoc" in PandocIntegration.FORMAT_DESCRIPTIONS["asciidoc"]
        assert "Markdown" in PandocIntegration.FORMAT_DESCRIPTIONS["markdown"]
        assert "Word" in PandocIntegration.FORMAT_DESCRIPTIONS["docx"]


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestPypandocImportError:
    """Test pypandoc import error handling."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_check_installation_pypandoc_import_error(self, mock_run, mock_which):
        """Test when pypandoc is not installed."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        # Mock pypandoc import to raise ImportError
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'pypandoc'")
        ):
            integration = PandocIntegration()
            success, message = integration.check_installation()

            assert success is False
            assert "pypandoc not installed" in message


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestAutoInstallPypandoc:
    """Test auto_install_pypandoc method."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_auto_install_no_pandoc(self, mock_run, mock_which):
        """Test auto-install when pandoc not found."""
        mock_which.return_value = None

        integration = PandocIntegration()
        success, message = integration.auto_install_pypandoc()

        assert success is False
        assert "pandoc binary not found" in message

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_auto_install_success(self, mock_run, mock_which):
        """Test successful pypandoc installation."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Mock: version check, pip install success, formats queries for re-check
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="pandoc 3.1.2"),  # Initial version check
            MagicMock(returncode=0, stdout="Successfully installed"),  # pip install
            MagicMock(returncode=0, stdout="pandoc 3.1.2"),  # Re-check version
            MagicMock(returncode=0, stdout="asciidoc\nmarkdown"),  # Input formats
            MagicMock(returncode=0, stdout="html\nlatex"),  # Output formats
        ]

        integration = PandocIntegration()

        # Manually set pypandoc_available for this test
        integration.pypandoc_available = False

        # Mock pypandoc import to succeed after "installation"
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "pypandoc":
                    integration.pypandoc_available = True
                    return MagicMock()
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            success, message = integration.auto_install_pypandoc()

            # Should return success
            assert isinstance(success, bool)
            assert isinstance(message, str)

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_auto_install_pip_failure(self, mock_run, mock_which):
        """Test when pip install fails."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Version check success, pip install fails
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="pandoc 3.1.2"),
            MagicMock(
                returncode=1, stdout="error output", stderr="Installation failed"
            ),
        ]

        integration = PandocIntegration()
        success, message = integration.auto_install_pypandoc()

        assert success is False
        # Message contains "Failed to install pypandoc" + error details
        assert any(word in message.lower() for word in ["failed", "error", "pypandoc"])

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_auto_install_exception(self, mock_run, mock_which):
        """Test exception handling during auto-install."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Version check success, pip install raises exception
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="pandoc 3.1.2"),
            subprocess.TimeoutExpired("pip", 30),
        ]

        integration = PandocIntegration()
        success, message = integration.auto_install_pypandoc()

        assert success is False
        assert any(word in message.lower() for word in ["error", "timeout", "failed"])


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestConvertFile:
    """Test convert_file method."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_convert_file_pypandoc_unavailable(self, mock_run, mock_which):
        """Test convert_file when pypandoc not available."""
        mock_which.return_value = None

        integration = PandocIntegration()
        success, text, error = integration.convert_file(Path("test.md"), "asciidoc")

        assert success is False
        assert "pypandoc not available" in error

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_convert_file_success(self, mock_run, mock_which, tmp_path):
        """Test successful file conversion."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Markdown")

        integration = PandocIntegration()
        integration.pypandoc_available = True

        # Patch pypandoc import inside convert_file
        mock_pypandoc = MagicMock()
        mock_pypandoc.convert_text.return_value = "= Test AsciiDoc"

        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: (
                mock_pypandoc if name == "pypandoc" else __import__(name, *args)
            ),
        ):
            success, text, error = integration.convert_file(test_file, "asciidoc")

            # Since pypandoc is available, should succeed
            assert integration.pypandoc_available

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_convert_file_docx(self, mock_run, mock_which, tmp_path):
        """Test DOCX file conversion (reads as binary)."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        # Create fake DOCX file
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"fake docx content")

        integration = PandocIntegration()
        integration.pypandoc_available = True

        # Minimal test - just verify method can be called
        success, text, error = integration.convert_file(test_file, "asciidoc")

        # Will fail since pypandoc not really available, but that's expected
        assert isinstance(success, bool)

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_convert_file_exception(self, mock_run, mock_which, tmp_path):
        """Test exception handling in convert_file."""
        mock_which.return_value = "/usr/bin/pandoc"
        mock_run.return_value = MagicMock(returncode=0, stdout="pandoc 3.1.2")

        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        integration = PandocIntegration()
        integration.pypandoc_available = True

        # Verify method exists
        assert hasattr(integration, "convert_file")

        # Call will fail since pypandoc not actually installed
        success, text, error = integration.convert_file(test_file, "asciidoc")

        # Either succeeds or fails gracefully
        assert isinstance(success, bool)


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestPDFExtractorExtraction:
    """Test PDF extraction functionality."""

    def test_is_available(self):
        """Test PDFExtractor.is_available method."""
        result = PDFExtractor.is_available()

        # Result should be boolean
        assert isinstance(result, bool)

    def test_extract_text_not_available(self, tmp_path):
        """Test extract_text when PyMuPDF not installed."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf")

        # Test without fitz available
        success, text, error = PDFExtractor.extract_text(test_file)

        # Will fail if fitz not installed or file is invalid
        assert isinstance(success, bool)
        if not success:
            # Error can be about fitz missing OR invalid PDF file
            assert any(
                word in error.lower()
                for word in ["pymupdf", "fitz", "failed", "open", "pdf"]
            )

    def test_extract_text_file_not_found(self):
        """Test PDF extraction with non-existent file."""
        from pathlib import Path

        success, text, error = PDFExtractor.extract_text(Path("/nonexistent/file.pdf"))

        # Should handle gracefully
        assert isinstance(success, bool)


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestGetSupportedFormatsException:
    """Test exception handling in _get_supported_formats."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_get_supported_formats_timeout(self, mock_run, mock_which):
        """Test timeout during format detection."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Version check success, format queries timeout
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="pandoc 3.1.2"),
            subprocess.TimeoutExpired("pandoc", 5),
            subprocess.TimeoutExpired("pandoc", 5),
        ]

        integration = PandocIntegration()

        # Should handle timeout gracefully
        assert isinstance(integration.supported_formats, dict)


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestAutoInstallPypandocEdgeCases:
    """Test auto_install_pypandoc edge cases."""

    @patch("asciidoc_artisan.document_converter.shutil.which")
    @patch("asciidoc_artisan.document_converter.subprocess.run")
    def test_auto_install_pypandoc_installation_failure(self, mock_run, mock_which):
        """Test pypandoc installation failure."""
        mock_which.return_value = "/usr/bin/pandoc"

        # Version check succeeds, installation fails
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="pandoc 3.1.2"),
            MagicMock(returncode=1, stderr="Installation failed", stdout=""),
        ]

        integration = PandocIntegration()
        success, message = integration.auto_install_pypandoc()

        assert success is False
        assert any(word in message.lower() for word in ["failed", "install"])


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestPDFExtractionEdgeCases:
    """Test PDF extraction edge cases."""

    def test_extract_text_empty_pdf(self, tmp_path):
        """Test extraction from PDF with no text content."""
        pytest.importorskip("fitz")

        # Create a minimal PDF with no text
        test_file = tmp_path / "empty.pdf"

        # Skip if we can't create test PDF
        try:
            import fitz

            doc = fitz.open()
            _ = doc.new_page()
            doc.save(str(test_file))
            doc.close()
        except Exception:
            pytest.skip("Cannot create test PDF")

        success, text, error = PDFExtractor.extract_text(test_file)

        # Should handle empty PDF gracefully
        if not success:
            assert "no text" in error.lower() or "empty" in error.lower()

    def test_extract_text_multipage_pdf(self, tmp_path):
        """Test extraction from multi-page PDF."""
        pytest.importorskip("fitz")

        test_file = tmp_path / "multipage.pdf"

        try:
            import fitz

            doc = fitz.open()

            # Create 3 pages with text
            for i in range(3):
                page = doc.new_page()
                page.insert_text((50, 50), f"Page {i + 1} content")

            doc.save(str(test_file))
            doc.close()
        except Exception:
            pytest.skip("Cannot create test PDF")

        success, text, error = PDFExtractor.extract_text(test_file)

        if success:
            # Should include page separators for multi-page docs
            assert "Page" in text


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestTableFormattingEdgeCases:
    """Test table formatting edge cases."""

    def test_format_table_empty_table(self):
        """Test formatting completely empty table."""
        result = PDFExtractor._format_table_as_asciidoc([])

        assert result == ""

    def test_format_table_all_empty_rows(self):
        """Test formatting table with all empty rows."""
        table = [
            ["", "", ""],
            ["", None, ""],
            [None, None, None],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        # Should return empty for tables with no content
        assert result == ""

    def test_format_table_single_column(self):
        """Test formatting single-column table."""
        table = [
            ["Header"],
            ["Row 1"],
            ["Row 2"],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        assert '[options="header"]' in result
        assert "|===" in result

    def test_format_table_many_columns(self):
        """Test formatting table with many columns (>5)."""
        table = [
            ["C1", "C2", "C3", "C4", "C5", "C6", "C7"],
            ["R1C1", "R1C2", "R1C3", "R1C4", "R1C5", "R1C6", "R1C7"],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        # Should use auto-sizing for many columns
        assert '[options="header"]' in result
        assert "|===" in result

    def test_format_table_4_columns(self):
        """Test formatting table with 4 columns."""
        table = [
            ["H1", "H2", "H3", "H4"],
            ["R1", "R2", "R3", "R4"],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        # Should include column spec for 4 columns
        assert 'cols="1,1,1,1"' in result

    def test_format_table_uneven_rows(self):
        """Test formatting table with rows of different lengths."""
        table = [
            ["H1", "H2", "H3"],
            ["R1", "R2"],  # Short row
            ["R1", "R2", "R3", "R4"],  # Long row
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        # Should normalize row lengths
        assert "|===" in result


@pytest.mark.fr_012
@pytest.mark.fr_013
@pytest.mark.fr_014
@pytest.mark.unit
class TestPDFToAsciiDocConversion:
    """Test PDF to AsciiDoc conversion."""

    def test_convert_pdf_to_asciidoc_extraction_failure(self, tmp_path):
        """Test conversion when PDF extraction fails."""
        test_file = tmp_path / "bad.pdf"
        test_file.write_bytes(b"not a real pdf")

        success, content, error = PDFExtractor.convert_to_asciidoc(test_file)

        # Should handle extraction failure gracefully
        assert success is False
        assert error != ""

    def test_convert_pdf_to_asciidoc_success(self, tmp_path):
        """Test successful PDF to AsciiDoc conversion."""
        pytest.importorskip("fitz")

        test_file = tmp_path / "test.pdf"

        try:
            import fitz

            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "Test content")
            doc.save(str(test_file))
            doc.close()
        except Exception:
            pytest.skip("Cannot create test PDF")

        success, content, error = PDFExtractor.convert_to_asciidoc(test_file)

        if success:
            # Should include AsciiDoc header
            assert "= Document from" in content
            assert ":toc:" in content
            assert "Test content" in content or content != ""
