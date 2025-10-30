"""
Tests for PDF extraction functionality.
"""

import builtins
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from asciidoc_artisan.document_converter import PDFExtractor


class TestPDFExtractor:
    """Test PDFExtractor functionality."""

    def test_is_available_with_pymupdf(self):
        """Test is_available returns True when PyMuPDF (fitz) is installed."""
        mock_fitz = Mock()
        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            result = PDFExtractor.is_available()
            assert result is True

    def test_is_available_without_pymupdf(self):
        """Test is_available returns False when PyMuPDF (fitz) is not installed."""
        # Remove fitz from sys.modules temporarily
        original = sys.modules.get("fitz")
        if "fitz" in sys.modules:
            del sys.modules["fitz"]

        try:
            # Make import fail
            with patch.dict(sys.modules, {"fitz": None}):
                # Patch __import__ to raise ImportError for fitz
                original_import = builtins.__import__

                def mock_import(name, *args, **kwargs):
                    if name == "fitz":
                        raise ImportError("No module named 'fitz'")
                    return original_import(name, *args, **kwargs)

                with patch("builtins.__import__", side_effect=mock_import):
                    result = PDFExtractor.is_available()
                    assert result is False
        finally:
            # Restore original state
            if original is not None:
                sys.modules["fitz"] = original

    def test_extract_text_without_pymupdf(self):
        """Test extract_text returns error when PyMuPDF not installed."""
        # Remove fitz from sys.modules temporarily
        original = sys.modules.get("fitz")
        if "fitz" in sys.modules:
            del sys.modules["fitz"]

        try:
            # Make import fail
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "fitz":
                    raise ImportError("No module named 'fitz'")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                pdf_path = Path("test.pdf")
                success, text, error = PDFExtractor.extract_text(pdf_path)

                assert success is False
                assert text == ""
                assert "PyMuPDF not installed" in error
        finally:
            # Restore original state
            if original is not None:
                sys.modules["fitz"] = original

    def test_extract_text_single_page(self):
        """Test extracting text from single-page PDF."""
        mock_page = Mock()
        mock_page.get_text.return_value = "Test content from PDF"

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.close = Mock()

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("test.pdf")
            success, text, error = PDFExtractor.extract_text(pdf_path)

            assert success is True
            assert "Test content from PDF" in text
            assert error == ""
            # Single page should not have page markers
            assert "Page 1 of 1" not in text

    def test_extract_text_multi_page(self):
        """Test extracting text from multi-page PDF with page markers."""
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Page 1 content"

        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Page 2 content"

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2

        def getitem_side_effect(index):
            if index == 0:
                return mock_page1
            elif index == 1:
                return mock_page2
            raise IndexError()

        mock_doc.__getitem__.side_effect = getitem_side_effect
        mock_doc.close = Mock()

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("test.pdf")
            success, text, error = PDFExtractor.extract_text(pdf_path)

            assert success is True
            assert "Page 1 content" in text
            assert "Page 2 content" in text
            assert "// Page 1 of 2" in text
            assert "// Page 2 of 2" in text
            assert error == ""

    def test_extract_text_with_tables(self):
        """Test extracting text that includes table data from PDF.

        Note: PyMuPDF doesn't extract tables separately but includes them
        in the text content, which is faster than dedicated table extraction.
        """
        # Text content that includes a table representation
        table_text = """Text before table
        Header 1    Header 2    Header 3
        Row 1 Col 1 Row 1 Col 2 Row 1 Col 3
        Row 2 Col 1 Row 2 Col 2 Row 2 Col 3"""

        mock_page = Mock()
        mock_page.get_text.return_value = table_text

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.close = Mock()

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("test.pdf")
            success, text, error = PDFExtractor.extract_text(pdf_path)

            assert success is True
            assert "Text before table" in text
            assert "Header 1" in text
            assert "Row 1 Col 1" in text
            assert error == ""

    def test_extract_text_empty_pdf(self):
        """Test extracting text from PDF with no content."""
        mock_page = Mock()
        mock_page.get_text.return_value = ""

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.close = Mock()

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("empty.pdf")
            success, text, error = PDFExtractor.extract_text(pdf_path)

            assert success is False
            assert text == ""
            assert "No text content found" in error
            assert "may contain only images" in error

    def test_extract_text_file_not_found(self):
        """Test extracting text from non-existent PDF."""
        mock_fitz = Mock()
        mock_fitz.open.side_effect = FileNotFoundError("File not found")

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("nonexistent.pdf")
            success, text, error = PDFExtractor.extract_text(pdf_path)

            assert success is False
            assert text == ""
            assert "Failed to extract PDF" in error

    def test_extract_text_corrupted_pdf(self):
        """Test extracting text from corrupted PDF."""
        mock_fitz = Mock()
        mock_fitz.open.side_effect = Exception("PDF is corrupted")

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("corrupted.pdf")
            success, text, error = PDFExtractor.extract_text(pdf_path)

            assert success is False
            assert text == ""
            assert "Failed to extract PDF" in error
            assert "corrupted" in error.lower()

    def test_format_table_as_asciidoc(self):
        """Test table formatting as AsciiDoc."""
        table = [
            ["Col1", "Col2", "Col3"],
            ["Data1", "Data2", "Data3"],
            ["Data4", "Data5", "Data6"],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        assert (
            'options="header"' in result
        )  # Fixed: Check for substring without brackets
        assert "|===" in result
        assert "Col1" in result
        assert "Data1" in result
        assert "| Col1 | Col2 | Col3" in result

    def test_format_table_with_none_values(self):
        """Test table formatting with None values."""
        table = [
            ["Header1", None, "Header3"],
            ["Data1", "Data2", None],
        ]

        result = PDFExtractor._format_table_as_asciidoc(table)

        assert (
            'options="header"' in result
        )  # Fixed: Check for substring without brackets
        assert "|===" in result
        # None values should be converted to empty strings
        assert "| Header1 |  | Header3" in result
        assert "| Data1 | Data2 |" in result

    def test_format_empty_table(self):
        """Test formatting empty table."""
        result = PDFExtractor._format_table_as_asciidoc([])
        assert result == ""

        result = PDFExtractor._format_table_as_asciidoc([[]])
        assert result == ""

    def test_convert_to_asciidoc_success(self):
        """Test complete conversion to AsciiDoc format."""
        mock_page = Mock()
        mock_page.get_text.return_value = "Test PDF content"

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.close = Mock()

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("test.pdf")
            success, asciidoc_text, error = PDFExtractor.convert_to_asciidoc(pdf_path)

            assert success is True
            assert error == ""
            # Check for document header
            assert "= Document from test.pdf" in asciidoc_text
            assert ":toc:" in asciidoc_text
            assert ":toc-placement: preamble" in asciidoc_text
            assert "// Extracted from PDF" in asciidoc_text
            assert "Test PDF content" in asciidoc_text

    def test_convert_to_asciidoc_failure(self):
        """Test conversion failure propagates correctly."""
        mock_fitz = Mock()
        mock_fitz.open.side_effect = Exception("Extraction failed")

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("test.pdf")
            success, asciidoc_text, error = PDFExtractor.convert_to_asciidoc(pdf_path)

            assert success is False
            assert asciidoc_text == ""
            assert "Failed to extract PDF" in error

    def test_convert_to_asciidoc_with_complex_content(self):
        """Test conversion with complex content from multi-page PDF."""
        mock_page1 = Mock()
        mock_page1.get_text.return_value = (
            "First page content\nName    Value\nItem 1  100"
        )

        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Second page content"

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2

        def getitem_side_effect(index):
            if index == 0:
                return mock_page1
            elif index == 1:
                return mock_page2
            raise IndexError()

        mock_doc.__getitem__.side_effect = getitem_side_effect
        mock_doc.close = Mock()

        mock_fitz = Mock()
        mock_fitz.open.return_value = mock_doc

        with patch.dict(sys.modules, {"fitz": mock_fitz}):
            pdf_path = Path("complex.pdf")
            success, asciidoc_text, error = PDFExtractor.convert_to_asciidoc(pdf_path)

            assert success is True
            assert "First page content" in asciidoc_text
            assert "Second page content" in asciidoc_text
            assert "Name" in asciidoc_text
            assert "// Page 1 of 2" in asciidoc_text
            assert "// Page 2 of 2" in asciidoc_text
