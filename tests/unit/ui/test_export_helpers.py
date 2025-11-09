"""
Tests for ui.export_helpers module.

Tests export helper classes including:
- HTMLConverter: AsciiDoc to HTML conversion
- PDFHelper: PDF engine detection and CSS generation
- ClipboardHelper: Clipboard format detection
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.export_helpers import (
    ClipboardHelper,
    HTMLConverter,
    PDFHelper,
)


class TestHTMLConverter:
    """Test HTMLConverter class."""

    def test_initialization(self):
        """Test HTMLConverter initializes with API."""
        mock_api = Mock()
        converter = HTMLConverter(mock_api)

        assert converter.asciidoc_api is mock_api

    def test_asciidoc_to_html_success(self):
        """Test successful AsciiDoc to HTML conversion."""
        # Mock AsciiDoc API
        mock_api = Mock()
        mock_api.execute = Mock()

        converter = HTMLConverter(mock_api)

        # Mock the execute method to write HTML to outfile
        def mock_execute(infile, outfile, backend):
            outfile.write("<html><body><p>Test content</p></body></html>")

        mock_api.execute = mock_execute

        result = converter.asciidoc_to_html("= Test\n\nTest content")

        assert "<html>" in result
        assert "Test content" in result

    def test_asciidoc_to_html_custom_backend(self):
        """Test conversion with custom backend."""
        mock_api = Mock()
        mock_api.execute = Mock()

        def mock_execute(infile, outfile, backend):
            outfile.write(f"<html backend={backend}></html>")

        mock_api.execute = mock_execute

        converter = HTMLConverter(mock_api)
        result = converter.asciidoc_to_html("= Test", backend="xhtml11")

        assert "xhtml11" in result

    def test_asciidoc_to_html_no_api_raises_error(self):
        """Test error when API not initialized."""
        converter = HTMLConverter(None)

        with pytest.raises(RuntimeError, match="AsciiDoc renderer not initialized"):
            converter.asciidoc_to_html("= Test")

    def test_asciidoc_to_html_handles_empty_content(self):
        """Test handling empty content."""
        mock_api = Mock()

        def mock_execute(infile, outfile, backend):
            outfile.write("")

        mock_api.execute = mock_execute

        converter = HTMLConverter(mock_api)
        result = converter.asciidoc_to_html("")

        assert result == ""


class TestPDFHelper:
    """Test PDFHelper class."""

    def test_pdf_engines_list(self):
        """Test PDF_ENGINES constant exists and has engines."""
        assert hasattr(PDFHelper, "PDF_ENGINES")
        assert len(PDFHelper.PDF_ENGINES) > 0
        assert "wkhtmltopdf" in PDFHelper.PDF_ENGINES

    def test_check_pdf_engine_available_specific_engine_found(self):
        """Test checking specific engine that is available."""
        with patch("subprocess.run") as mock_run:
            # Mock successful engine check
            mock_run.return_value = Mock(returncode=0)

            result = PDFHelper.check_pdf_engine_available("wkhtmltopdf")

            assert result is True
            mock_run.assert_called_once()
            # Verify it called with correct command
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "wkhtmltopdf"
            assert "--version" in call_args

    def test_check_pdf_engine_available_specific_engine_not_found(self):
        """Test checking specific engine that is not available."""
        with patch("subprocess.run") as mock_run:
            # Mock FileNotFoundError (engine not installed)
            mock_run.side_effect = FileNotFoundError()

            result = PDFHelper.check_pdf_engine_available("nonexistent_engine")

            assert result is False

    def test_check_pdf_engine_available_engine_returns_error(self):
        """Test checking engine that returns non-zero exit code."""
        with patch("subprocess.run") as mock_run:
            # Mock failed engine check
            mock_run.return_value = Mock(returncode=1)

            result = PDFHelper.check_pdf_engine_available("broken_engine")

            assert result is False

    def test_check_pdf_engine_available_any_engine_found(self):
        """Test checking for any available engine (first one works)."""
        with patch("subprocess.run") as mock_run:
            # First engine works
            mock_run.return_value = Mock(returncode=0)

            result = PDFHelper.check_pdf_engine_available(None)

            assert result is True
            # Should check first engine in list
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == PDFHelper.PDF_ENGINES[0]

    def test_check_pdf_engine_available_any_engine_second_works(self):
        """Test checking for any engine when first fails but second works."""
        with patch("subprocess.run") as mock_run:
            # First fails, second succeeds
            mock_run.side_effect = [
                FileNotFoundError(),  # First engine not found
                Mock(returncode=0),  # Second engine works
            ]

            result = PDFHelper.check_pdf_engine_available(None)

            assert result is True
            assert mock_run.call_count == 2

    def test_check_pdf_engine_available_no_engines_available(self):
        """Test when no PDF engines are available."""
        with patch("subprocess.run") as mock_run:
            # All engines fail
            mock_run.side_effect = FileNotFoundError()

            result = PDFHelper.check_pdf_engine_available(None)

            assert result is False
            # Should have tried all engines
            assert mock_run.call_count == len(PDFHelper.PDF_ENGINES)

    def test_check_pdf_engine_available_timeout(self):
        """Test handling subprocess timeout."""
        with patch("subprocess.run") as mock_run:
            # Mock timeout
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)

            result = PDFHelper.check_pdf_engine_available("slow_engine")

            assert result is False

    def test_add_print_css_to_html_with_head_tag(self):
        """Test adding CSS when HTML has </head> tag."""
        html_content = (
            "<html><head><title>Test</title></head><body>Content</body></html>"
        )

        result = PDFHelper.add_print_css_to_html(html_content)

        assert "<style>" in result
        assert "@page" in result
        assert "font-family:" in result
        # CSS should be before </head>
        assert result.index("<style>") < result.index("</head>")

    def test_add_print_css_to_html_with_body_tag_no_head(self):
        """Test adding CSS when HTML has <body> but no </head>."""
        html_content = "<body>Content</body>"

        result = PDFHelper.add_print_css_to_html(html_content)

        assert "<style>" in result
        # CSS should be after <body> (may have newline)
        assert "<body>" in result and result.index("<body>") < result.index("<style>")

    def test_add_print_css_to_html_no_head_or_body(self):
        """Test adding CSS when HTML has no <head> or <body> tags."""
        html_content = "<p>Plain content</p>"

        result = PDFHelper.add_print_css_to_html(html_content)

        assert "<style>" in result
        # CSS should be prepended
        assert result.startswith("<style>") or result.startswith("\n<style>")

    def test_add_print_css_contains_print_styles(self):
        """Test that added CSS contains print-specific styles."""
        html_content = "<html><head></head><body></body></html>"

        result = PDFHelper.add_print_css_to_html(html_content)

        # Check for key print styles
        assert "@page" in result
        assert "size: A4" in result
        assert "margin: 2cm" in result
        assert "@media print" in result

    def test_add_print_css_contains_typography_styles(self):
        """Test that added CSS contains typography styles."""
        html_content = "<html><head></head><body></body></html>"

        result = PDFHelper.add_print_css_to_html(html_content)

        # Check for typography
        assert "font-family:" in result
        assert "font-size:" in result
        assert "line-height:" in result
        assert "h1, h2, h3" in result

    def test_add_print_css_contains_code_styles(self):
        """Test that added CSS contains code block styles."""
        html_content = "<html><head></head><body></body></html>"

        result = PDFHelper.add_print_css_to_html(html_content)

        # Check for code styles
        assert "pre, code" in result
        assert "Courier" in result
        assert "page-break-inside: avoid" in result

    def test_add_print_css_contains_table_styles(self):
        """Test that added CSS contains table styles."""
        html_content = "<html><head></head><body></body></html>"

        result = PDFHelper.add_print_css_to_html(html_content)

        # Check for table styles
        assert "table" in result
        assert "th, td" in result
        assert "border-collapse:" in result


class TestClipboardHelper:
    """Test ClipboardHelper class."""

    def test_parse_format_html_doctype(self):
        """Test detecting HTML with DOCTYPE."""
        clipboard_text = "<!DOCTYPE html>\n<html><body><p>Test</p></body></html>"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "html"

    def test_parse_format_html_tag(self):
        """Test detecting HTML with <html> tag."""
        clipboard_text = "<html><body><p>Test</p></body></html>"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "html"

    def test_parse_format_html_paragraph_tag(self):
        """Test detecting HTML with <p> tag."""
        clipboard_text = "<p>This is a paragraph</p>"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "html"

    def test_parse_format_html_div_tag(self):
        """Test detecting HTML with <div> tag."""
        clipboard_text = "<div>Content</div>"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "html"

    def test_parse_format_markdown_heading(self):
        """Test detecting Markdown with heading."""
        clipboard_text = "# Heading\n\nSome content"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_markdown_heading_level_2(self):
        """Test detecting Markdown with level 2 heading."""
        clipboard_text = "## Subheading"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_markdown_bold(self):
        """Test detecting Markdown with bold text."""
        clipboard_text = "Some **bold text** here"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_markdown_code_block(self):
        """Test detecting Markdown with code block."""
        clipboard_text = "```python\nprint('hello')\n```"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_markdown_link(self):
        """Test detecting Markdown with empty link pattern."""
        # Note: Detection looks for "[](" pattern (empty link)
        clipboard_text = "Check [](https://example.com)"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_markdown_list_asterisk(self):
        """Test detecting Markdown with asterisk list."""
        clipboard_text = "* Item 1\n* Item 2"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_markdown_list_dash(self):
        """Test detecting Markdown with dash list."""
        clipboard_text = "- Item 1\n- Item 2"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"

    def test_parse_format_plain_text(self):
        """Test detecting plain text (no special markers)."""
        clipboard_text = "Just some plain text content without any formatting"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result is None

    def test_parse_format_empty_string(self):
        """Test handling empty clipboard text."""
        clipboard_text = ""

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result is None

    def test_parse_format_whitespace_only(self):
        """Test handling whitespace-only clipboard text."""
        clipboard_text = "   \n\t  \n  "

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result is None

    def test_parse_format_case_insensitive_html(self):
        """Test HTML detection is case-insensitive."""
        clipboard_text = "<HTML><BODY><P>Test</P></BODY></HTML>"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "html"

    def test_parse_format_html_with_leading_whitespace(self):
        """Test HTML detection with leading whitespace."""
        clipboard_text = "  \n  <!DOCTYPE html>\n<html></html>"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "html"

    def test_parse_format_markdown_mixed_markers(self):
        """Test Markdown with multiple markers."""
        clipboard_text = "# Title\n\nSome **bold** and `code`\n\n```\ncode block\n```"

        result = ClipboardHelper.parse_format_from_clipboard(clipboard_text)

        assert result == "markdown"
