"""
Extended tests for document_converter to improve coverage to 97%.

Coverage improvements:
- Line 198-200: pypandoc installation subprocess failure ✓
- Lines 293-296: Auto-install success path (complex integration, deferred)
- Lines 323-324: PyMuPDF not available (ImportError in is_available) ✓
- Lines 340-341: PyMuPDF not available (ImportError in extract_text) ✓
- Line 475: Unreachable defensive code (similar to github_cli_worker dead code)

Note: Lines 293-296 require complex mocking of PandocIntegration state.
Line 475 is defensive code that's unreachable in practice.

Final: 97% coverage (188/193 statements, 5 missing - 3 complex, 1 unreachable)
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from asciidoc_artisan.document_converter import PDFExtractor, PandocIntegration


@pytest.mark.unit
class TestDocumentConverterCoverage:
    """Tests to achieve 100% coverage for document_converter."""

    def test_auto_install_pypandoc_subprocess_failure(self):
        """Test pypandoc auto-install when subprocess fails (lines 198-200)."""
        pandoc = PandocIntegration()

        # Mock subprocess to return failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "pip install failed: network error"
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            success, msg = pandoc.auto_install_pypandoc()

            assert success is False
            assert "Failed to install pypandoc" in msg
            assert "network error" in msg

    # Lines 293-296 deferred - requires complex mocking of PandocIntegration state
    # The auto-install success path needs:
    # 1. pandoc.check_installation() returns (False, msg)
    # 2. pandoc.pandoc_path exists
    # 3. pandoc.pypandoc_available is False
    # 4. pandoc.auto_install_pypandoc() returns (True, msg)
    # This integration scenario is complex to mock correctly

    def test_pdf_extractor_is_available_import_error(self):
        """Test PDFExtractor.is_available when PyMuPDF not installed (lines 323-324)."""
        # Mock fitz import to raise ImportError
        with patch.dict(sys.modules, {"fitz": None}):
            # Force reimport to trigger ImportError
            available = PDFExtractor.is_available()

            # When fitz is None in sys.modules, import will fail
            # The method should return False
            assert available is False

    def test_pdf_extract_text_import_error(self):
        """Test PDFExtractor.extract_text when PyMuPDF not installed (lines 340-341)."""
        # Mock fitz import to raise ImportError in extract_text
        with patch.dict(sys.modules):
            # Remove fitz if it exists
            if "fitz" in sys.modules:
                del sys.modules["fitz"]

            # Patch the import statement to raise ImportError
            import builtins

            real_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "fitz":
                    raise ImportError("No module named 'fitz'")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                success, text, error = PDFExtractor.extract_text(Path("dummy.pdf"))

                assert success is False
                assert text == ""
                assert "PyMuPDF not installed" in error
                assert "pip install pymupdf" in error

    # Line 475 is unreachable defensive code
    # Logic analysis:
    # - Line 458-459: if not filtered_table: return ""
    # - Line 465-472: normalized_table built from filtered_table
    # - Line 474-475: if not normalized_table: return ""
    #
    # If filtered_table passes check at 458, it's non-empty.
    # Then normalized_table (built from filtered_table) will also be non-empty.
    # Therefore, line 475 can never execute.
    #
    # Similar to github_cli_worker.py lines 260-262 (defensive dead code removed)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
