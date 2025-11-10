"""
Tests for document_converter.py (v2.0.0).

Tests Pandoc integration and PDF extraction with mocked subprocess calls.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.document_converter import (
    PDFExtractor,
    PandocIntegration,
    ensure_pandoc_available,
)


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
        output_formats = MagicMock(returncode=0, stdout="asciidoc\nmarkdown\nhtml\nlatex")

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


@pytest.mark.unit
class TestStaticMethods:
    """Test static methods."""

    def test_get_installation_instructions(self):
        """Test installation instructions generation."""
        instructions = PandocIntegration.get_installation_instructions()

        assert "pandoc" in instructions.lower()
        # Should include platform-specific instructions
        assert any(word in instructions.lower() for word in ["install", "download", "brew", "apt", "choco"])

    def test_get_format_info(self):
        """Test format information retrieval."""
        # Test known format
        info = PandocIntegration.get_format_info("markdown")
        assert "Markdown" in info

        # Test unknown format
        info_unknown = PandocIntegration.get_format_info("unknown_format")
        assert "unknown" in info_unknown.lower() or "not found" in info_unknown.lower()


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


@pytest.mark.unit
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


@pytest.mark.unit
@pytest.mark.unit
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


@pytest.mark.unit
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
