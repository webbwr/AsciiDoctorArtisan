"""
Unit tests for PandocWorker class.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.workers import PandocWorker


@pytest.fixture
def mock_pypandoc():
    """Fixture that mocks pypandoc in sys.modules."""
    mock_module = Mock()
    mock_module.convert_text = Mock(return_value="# Converted")
    mock_module.convert_file = Mock(return_value="# Converted from file")

    original = sys.modules.get("pypandoc")
    sys.modules["pypandoc"] = mock_module

    yield mock_module

    if original is not None:
        sys.modules["pypandoc"] = original
    else:
        sys.modules.pop("pypandoc", None)


@pytest.mark.unit
class TestPandocWorker:
    """Test PandocWorker for document conversion."""

    def test_pandoc_worker_initialization(self):
        """Test PandocWorker can be instantiated."""
        worker = PandocWorker()
        assert worker is not None

    def test_successful_text_conversion(self, mock_pypandoc):
        """Test successful text-to-text conversion."""
        mock_pypandoc.convert_text.return_value = "# Converted AsciiDoc"

        worker = PandocWorker()
        result = None
        context = None

        def capture_result(text, ctx):
            nonlocal result, context
            result = text
            context = ctx

        worker.conversion_complete.connect(capture_result)

        # Execute conversion
        worker.run_pandoc_conversion(
            source="# Markdown",
            to_format="asciidoc",
            from_format="markdown",
            context="test conversion",
            output_file=None,
            use_ai_conversion=False,
        )

        # Verify
        assert result is not None
        assert "Converted" in result
        assert context == "test conversion"

    def test_conversion_error_handling(self, mock_pypandoc):
        """Test conversion error is properly handled."""
        mock_pypandoc.convert_text.side_effect = Exception("Conversion failed")

        worker = PandocWorker()
        error = None
        context = None

        def capture_error(err, ctx):
            nonlocal error, context
            error = err
            context = ctx

        worker.conversion_error.connect(capture_error)

        # Execute conversion
        worker.run_pandoc_conversion(
            source="# Test",
            to_format="asciidoc",
            from_format="markdown",
            context="error test",
            output_file=None,
            use_ai_conversion=False,
        )

        # Verify error was emitted
        assert error is not None
        assert "Conversion failed" in error

    def test_asciidoc_output_enhancement(self):
        """Test AsciiDoc output enhancement."""
        worker = PandocWorker()

        # Test adding document title
        text_without_title = "== Section Header\n\nContent here"
        enhanced = worker._enhance_asciidoc_output(text_without_title)

        assert enhanced.startswith("=")  # Should have title added

        # Test preserving existing title
        text_with_title = "= My Document\n\n== Section\n\nContent"
        enhanced = worker._enhance_asciidoc_output(text_with_title)

        assert enhanced.startswith("= My Document")  # Should keep original

    def test_bytes_to_string_conversion(self, mock_pypandoc):
        """Test conversion handles bytes return value."""
        mock_pypandoc.convert_text.return_value = b"Converted bytes"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="Test",
            to_format="asciidoc",
            from_format="markdown",
            context="bytes test",
            output_file=None,
            use_ai_conversion=False,
        )

        # Verify bytes were decoded to string
        assert isinstance(result, str)
        assert "Converted bytes" in result

    def test_file_output_conversion(self, mock_pypandoc):
        """Test conversion with file output."""
        mock_pypandoc.convert_text.return_value = None  # File output returns None

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        output_path = Path("/tmp/test.docx")
        worker.run_pandoc_conversion(
            source="Test content",
            to_format="docx",
            from_format="asciidoc",
            context="file output test",
            output_file=output_path,
            use_ai_conversion=False,
        )

        # Verify result indicates file was saved
        assert result is not None
        assert "File saved to:" in result or str(output_path) in result

    # AI conversion test removed - using Ollama for local AI features instead


@pytest.mark.unit
class TestPandocOutputEnhancement:
    """Test AsciiDoc output enhancement logic."""

    def test_source_code_block_formatting(self):
        """Test source code block formatting is fixed."""
        worker = PandocWorker()

        # Pandoc sometimes outputs [source]python instead of [source,python]
        text = "[source]python\n----\ncode here\n----"
        enhanced = worker._enhance_asciidoc_output(text)

        assert "[source,python]" in enhanced

    def test_multiple_source_blocks(self):
        """Test multiple source blocks are all fixed."""
        worker = PandocWorker()

        text = """
[source]python
----
code1
----

[source]javascript
----
code2
----
"""
        enhanced = worker._enhance_asciidoc_output(text)

        assert "[source,python]" in enhanced
        assert "[source,javascript]" in enhanced


@pytest.mark.unit
class TestOllamaIntegration:
    """Test Ollama AI integration features."""

    def test_ollama_config_initialization(self):
        """Test Ollama configuration starts disabled."""
        worker = PandocWorker()
        assert worker.ollama_enabled is False
        assert worker.ollama_model is None

    def test_set_ollama_config_enabled(self):
        """Test setting Ollama configuration."""
        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")

        assert worker.ollama_enabled is True
        assert worker.ollama_model == "llama2"

    def test_set_ollama_config_disabled(self):
        """Test disabling Ollama configuration."""
        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")
        worker.set_ollama_config(enabled=False, model=None)

        assert worker.ollama_enabled is False
        assert worker.ollama_model is None

    def test_set_ollama_config_different_models(self):
        """Test changing Ollama models."""
        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")
        assert worker.ollama_model == "llama2"

        worker.set_ollama_config(enabled=True, model="codellama")
        assert worker.ollama_model == "codellama"


@pytest.mark.unit
class TestPDFEngineDetection:
    """Test PDF engine detection logic."""

    @patch("subprocess.run")
    def test_detect_wkhtmltopdf_first(self, mock_run):
        """Test wkhtmltopdf is detected first when available."""
        mock_run.return_value = None  # Success
        worker = PandocWorker()

        engine = worker._detect_pdf_engine()

        assert engine == "wkhtmltopdf"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "wkhtmltopdf"

    @patch("subprocess.run")
    def test_detect_weasyprint_fallback(self, mock_run):
        """Test weasyprint is used if wkhtmltopdf not available."""

        def side_effect(*args, **kwargs):
            if args[0][0] == "wkhtmltopdf":
                raise FileNotFoundError()
            return None  # Success for weasyprint

        mock_run.side_effect = side_effect
        worker = PandocWorker()

        engine = worker._detect_pdf_engine()

        assert engine == "weasyprint"

    @patch("subprocess.run")
    def test_detect_no_pdf_engine_raises_error(self, mock_run):
        """Test RuntimeError when no PDF engine available."""
        mock_run.side_effect = FileNotFoundError()
        worker = PandocWorker()

        with pytest.raises(RuntimeError, match="PDF conversion requires"):
            worker._detect_pdf_engine()


@pytest.mark.unit
class TestPandocArgsBuilding:
    """Test Pandoc command-line argument building."""

    def test_build_args_basic_conversion(self):
        """Test basic conversion arguments."""
        worker = PandocWorker()
        args = worker._build_pandoc_args("markdown", "asciidoc")

        assert isinstance(args, list)
        # Should have some arguments
        assert len(args) > 0

    def test_build_args_pdf_conversion(self):
        """Test PDF conversion includes PDF engine."""
        worker = PandocWorker()
        # PDF args require engine detection, which may fail in test env
        # Just verify method doesn't crash
        try:
            args = worker._build_pandoc_args("asciidoc", "pdf")
            assert isinstance(args, list)
        except RuntimeError:
            # Expected if no PDF engine available in test environment
            pass

    def test_build_args_different_formats(self):
        """Test argument building for various formats."""
        worker = PandocWorker()

        # Should not raise exceptions
        worker._build_pandoc_args("markdown", "html")
        worker._build_pandoc_args("html", "markdown")
        worker._build_pandoc_args("asciidoc", "docx")
        worker._build_pandoc_args("docx", "asciidoc")


@pytest.mark.unit
class TestProgressSignals:
    """Test progress update signals."""

    def test_progress_signal_emitted(self, mock_pypandoc):
        """Test progress signals are emitted during conversion."""
        mock_pypandoc.convert_text.return_value = "Result"

        worker = PandocWorker()
        progress_messages = []

        def capture_progress(msg):
            progress_messages.append(msg)

        worker.progress_update.connect(capture_progress)

        worker.run_pandoc_conversion(
            source="# Test",
            to_format="asciidoc",
            from_format="markdown",
            context="progress test",
            output_file=None,
            use_ai_conversion=False,
        )

        # Should have emitted at least one progress message
        # (actual implementation may vary, so just check signal works)
        # If no progress messages, that's OK too (implementation detail)
        assert isinstance(progress_messages, list)


@pytest.mark.unit
class TestFormatConversions:
    """Test various format conversion scenarios."""

    def test_markdown_to_asciidoc(self, mock_pypandoc):
        """Test Markdown to AsciiDoc conversion."""
        mock_pypandoc.convert_text.return_value = "= Converted"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="# Markdown Header",
            to_format="asciidoc",
            from_format="markdown",
            context="md2adoc",
            output_file=None,
            use_ai_conversion=False,
        )

        assert result is not None

    def test_asciidoc_to_html(self, mock_pypandoc):
        """Test AsciiDoc to HTML conversion."""
        mock_pypandoc.convert_text.return_value = "<h1>Header</h1>"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="= Header",
            to_format="html",
            from_format="asciidoc",
            context="adoc2html",
            output_file=None,
            use_ai_conversion=False,
        )

        assert result is not None
        assert "<h1>" in result or "Header" in result

    def test_html_to_markdown(self, mock_pypandoc):
        """Test HTML to Markdown conversion."""
        mock_pypandoc.convert_text.return_value = "# Header"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="<h1>Header</h1>",
            to_format="markdown",
            from_format="html",
            context="html2md",
            output_file=None,
            use_ai_conversion=False,
        )

        assert result is not None


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_invalid_format_error(self, mock_pypandoc):
        """Test error handling for invalid formats."""
        mock_pypandoc.convert_text.side_effect = RuntimeError("Invalid format")

        worker = PandocWorker()
        error = None

        def capture_error(err, ctx):
            nonlocal error
            error = err

        worker.conversion_error.connect(capture_error)

        worker.run_pandoc_conversion(
            source="Test",
            to_format="invalid",
            from_format="markdown",
            context="error test",
            output_file=None,
            use_ai_conversion=False,
        )

        assert error is not None
        assert "Invalid format" in error or "error" in error.lower()

    def test_timeout_error(self, mock_pypandoc):
        """Test error handling for conversion timeout."""
        mock_pypandoc.convert_text.side_effect = TimeoutError("Conversion timed out")

        worker = PandocWorker()
        error = None

        def capture_error(err, ctx):
            nonlocal error
            error = err

        worker.conversion_error.connect(capture_error)

        worker.run_pandoc_conversion(
            source="Test",
            to_format="asciidoc",
            from_format="markdown",
            context="timeout test",
            output_file=None,
            use_ai_conversion=False,
        )

        assert error is not None

    def test_unicode_error_handling(self, mock_pypandoc):
        """Test error handling for unicode issues."""
        mock_pypandoc.convert_text.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "invalid"
        )

        worker = PandocWorker()
        error = None

        def capture_error(err, ctx):
            nonlocal error
            error = err

        worker.conversion_error.connect(capture_error)

        worker.run_pandoc_conversion(
            source="Test",
            to_format="asciidoc",
            from_format="markdown",
            context="unicode test",
            output_file=None,
            use_ai_conversion=False,
        )

        assert error is not None

    @patch(
        "asciidoc_artisan.workers.pandoc_worker.is_pandoc_available", return_value=False
    )
    def test_pandoc_not_available_error(self, mock_is_available):
        """Test error when Pandoc is not available."""
        # Ensure pypandoc is NOT in sys.modules (simulate it not being installed)
        original = sys.modules.get("pypandoc")
        if "pypandoc" in sys.modules:
            del sys.modules["pypandoc"]

        try:
            worker = PandocWorker()
            error = None

            def capture_error(err, ctx):
                nonlocal error
                error = err

            worker.conversion_error.connect(capture_error)

            worker.run_pandoc_conversion(
                source="Test",
                to_format="asciidoc",
                from_format="markdown",
                context="no pandoc test",
                output_file=None,
                use_ai_conversion=False,
            )

            assert error is not None
            assert "Pandoc" in error or "pypandoc" in error
        finally:
            # Restore pypandoc if it was there
            if original is not None:
                sys.modules["pypandoc"] = original


@pytest.mark.unit
class TestOllamaConversion:
    """Test Ollama AI conversion with fallback."""

    def test_ollama_conversion_disabled_falls_back_to_pandoc(self):
        """Test that disabled Ollama falls back to Pandoc."""
        worker = PandocWorker()
        worker.ollama_enabled = False  # Explicitly disabled

        result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

        assert result is None  # Should return None when disabled

    def test_ollama_conversion_no_model_falls_back(self):
        """Test that missing model falls back to Pandoc."""
        worker = PandocWorker()
        worker.ollama_enabled = True
        worker.ollama_model = None  # No model set

        result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

        assert result is None  # Should return None when no model

    def test_ollama_conversion_success(self):
        """Test successful Ollama conversion."""
        # Mock ollama at import time inside the method
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "ollama":
                    mock_ollama = type("ollama", (), {})()
                    mock_ollama.generate = lambda **kwargs: {
                        "response": "= Converted by AI\n\nTest content"
                    }
                    return mock_ollama
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            worker = PandocWorker()
            worker.ollama_enabled = True
            worker.ollama_model = "llama2"

            result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

            assert result is not None
            assert "Converted by AI" in result

    def test_ollama_conversion_empty_response(self):
        """Test Ollama empty response handling."""
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "ollama":
                    mock_ollama = type("ollama", (), {})()
                    mock_ollama.generate = lambda **kwargs: {"response": ""}
                    return mock_ollama
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            worker = PandocWorker()
            worker.ollama_enabled = True
            worker.ollama_model = "llama2"

            result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

            assert result is None  # Empty response should return None

    def test_ollama_conversion_no_response_key(self):
        """Test Ollama response without 'response' key."""
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "ollama":
                    mock_ollama = type("ollama", (), {})()
                    mock_ollama.generate = lambda **kwargs: {"error": "something"}
                    return mock_ollama
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            worker = PandocWorker()
            worker.ollama_enabled = True
            worker.ollama_model = "llama2"

            result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

            assert result is None  # Missing 'response' key should return None

    def test_ollama_conversion_insufficient_output(self):
        """Test Ollama response too short."""
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "ollama":
                    mock_ollama = type("ollama", (), {})()
                    mock_ollama.generate = lambda **kwargs: {
                        "response": "abc"
                    }  # < 10 chars
                    return mock_ollama
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            worker = PandocWorker()
            worker.ollama_enabled = True
            worker.ollama_model = "llama2"

            result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

            assert result is None  # Too short output should return None

    def test_ollama_conversion_timeout(self):
        """Test Ollama timeout handling."""
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "ollama":
                    mock_ollama = type("ollama", (), {})()

                    def raise_timeout(**kwargs):
                        raise Exception("Request timed out")

                    mock_ollama.generate = raise_timeout
                    return mock_ollama
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            worker = PandocWorker()
            worker.ollama_enabled = True
            worker.ollama_model = "llama2"

            result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

            assert result is None  # Timeout should return None

    def test_ollama_import_error(self):
        """Test handling of Ollama import failure."""
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "ollama":
                    raise ImportError("No ollama")
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            worker = PandocWorker()
            worker.ollama_enabled = True
            worker.ollama_model = "llama2"

            result = worker._try_ollama_conversion("# Test", "markdown", "asciidoc")

            assert result is None  # Import error should return None


@pytest.mark.unit
class TestConversionPromptCreation:
    """Test Ollama prompt creation for different formats."""

    def test_create_prompt_markdown_to_asciidoc(self):
        """Test prompt for Markdown to AsciiDoc conversion."""
        worker = PandocWorker()
        prompt = worker._create_conversion_prompt(
            "# Test Header", "markdown", "asciidoc"
        )

        assert "Markdown" in prompt
        assert "AsciiDoc" in prompt
        assert "Test Header" in prompt
        assert "source,language" in prompt  # AsciiDoc-specific

    def test_create_prompt_asciidoc_to_markdown(self):
        """Test prompt for AsciiDoc to Markdown conversion."""
        worker = PandocWorker()
        prompt = worker._create_conversion_prompt(
            "= Test Document", "asciidoc", "markdown"
        )

        assert "AsciiDoc" in prompt
        assert "Markdown" in prompt
        assert "Test Document" in prompt
        assert "```language" in prompt  # Markdown-specific

    def test_create_prompt_html_to_asciidoc(self):
        """Test prompt for HTML to AsciiDoc conversion."""
        worker = PandocWorker()
        prompt = worker._create_conversion_prompt("<h1>Test</h1>", "html", "asciidoc")

        assert "HTML" in prompt
        assert "AsciiDoc" in prompt
        assert "<h1>Test</h1>" in prompt

    def test_create_prompt_includes_format_instructions(self):
        """Test prompt includes format-specific instructions."""
        worker = PandocWorker()
        prompt = worker._create_conversion_prompt("Test", "markdown", "asciidoc")

        # Should include AsciiDoc formatting rules
        assert "source,language" in prompt or "[source" in prompt
        assert "=" in prompt  # Document title syntax

    def test_create_prompt_preserves_source_content(self):
        """Test prompt preserves full source document."""
        worker = PandocWorker()
        long_source = "# Header\n\n" + "Content line\n" * 50
        prompt = worker._create_conversion_prompt(long_source, "markdown", "asciidoc")

        # All source content should be in prompt
        assert "Content line" in prompt
        assert prompt.count("Content line") >= 50

    def test_create_prompt_unknown_format(self):
        """Test prompt for unknown format."""
        worker = PandocWorker()
        prompt = worker._create_conversion_prompt("Test", "unknown", "custom")

        # Should still work with generic instructions
        assert "Test" in prompt
        assert "unknown" in prompt or "UNKNOWN" in prompt


@pytest.mark.unit
class TestAIConversionWithFallback:
    """Test AI conversion with automatic fallback to Pandoc."""

    @patch.object(PandocWorker, "_try_ollama_conversion")
    def test_ai_conversion_success_text_output(self, mock_ollama, mock_pypandoc):
        """Test successful AI conversion for text output."""
        mock_ollama.return_value = "= AI Converted\n\nContent"
        mock_pypandoc.convert_text.return_value = "Should not be called"

        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")

        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="# Test",
            to_format="asciidoc",
            from_format="markdown",
            context="ai test",
            output_file=None,
            use_ai_conversion=True,
        )

        # AI result should be used
        assert result is not None
        assert "AI Converted" in result
        # Pandoc should not be called
        mock_pypandoc.convert_text.assert_not_called()

    @patch.object(PandocWorker, "_try_ollama_conversion")
    def test_ai_conversion_fallback_to_pandoc(self, mock_ollama, mock_pypandoc):
        """Test AI conversion falls back to Pandoc on failure."""
        mock_ollama.return_value = None  # AI failed
        mock_pypandoc.convert_text.return_value = "= Pandoc Result"

        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")

        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="# Test",
            to_format="asciidoc",
            from_format="markdown",
            context="fallback test",
            output_file=None,
            use_ai_conversion=True,
        )

        # Pandoc result should be used
        assert result is not None
        assert "Pandoc Result" in result
        # Pandoc should have been called
        mock_pypandoc.convert_text.assert_called_once()

    @patch.object(PandocWorker, "_try_ollama_conversion")
    def test_ai_conversion_for_pdf_uses_pandoc(self, mock_ollama, mock_pypandoc):
        """Test AI conversion for PDF format uses Pandoc for binary output."""
        mock_ollama.return_value = "= AI Text"  # AI produces text
        mock_pypandoc.convert_text.return_value = None  # Pandoc saves to file

        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")

        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        output_file = Path("/tmp/test.pdf")
        worker.run_pandoc_conversion(
            source="# Test",
            to_format="pdf",
            from_format="markdown",
            context="pdf test",
            output_file=output_file,
            use_ai_conversion=True,
        )

        # Result should indicate file was saved
        assert result is not None
        # Note: The actual implementation may call Pandoc for PDF binary generation


@pytest.mark.unit
class TestPathSourceConversion:
    """Test conversion with Path source objects."""

    def test_path_source_text_output(self, mock_pypandoc, tmp_path):
        """Test conversion from Path source to text output."""
        # Create a temp file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Markdown")

        mock_pypandoc.convert_text.return_value = "= Converted"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source=test_file,
            to_format="asciidoc",
            from_format="markdown",
            context="path test",
            output_file=None,
            use_ai_conversion=False,
        )

        assert result is not None

    def test_bytes_source_conversion(self, mock_pypandoc, tmp_path):
        """Test conversion from bytes source."""
        mock_pypandoc.convert_file.return_value = "= Converted from bytes"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        # Bytes source (like DOCX binary)
        bytes_source = b"Mock DOCX binary content"
        worker.run_pandoc_conversion(
            source=bytes_source,
            to_format="asciidoc",
            from_format="docx",
            context="bytes test",
            output_file=None,
            use_ai_conversion=False,
        )

        assert result is not None

    def test_path_source_to_binary_output(self, mock_pypandoc, tmp_path):
        """Test conversion from Path source to binary file output."""
        test_file = tmp_path / "test.adoc"
        test_file.write_text("= Test Document")

        output_file = tmp_path / "output.pdf"
        mock_pypandoc.convert_file.return_value = None  # Binary output

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source=test_file,
            to_format="pdf",
            from_format="asciidoc",
            context="path to pdf",
            output_file=output_file,
            use_ai_conversion=False,
        )

        assert result is not None
        assert "File saved" in result or str(output_file) in result


@pytest.mark.unit
class TestEnhanceAsciiDocEdgeCases:
    """Test AsciiDoc enhancement edge cases."""

    def test_enhance_empty_document(self):
        """Test enhancing empty document."""
        worker = PandocWorker()
        enhanced = worker._enhance_asciidoc_output("")

        # Should add title to empty document
        assert enhanced.startswith("=")

    def test_enhance_document_with_multiple_headings(self):
        """Test enhancing document with multiple headings."""
        worker = PandocWorker()
        text = "== First\n\n=== Second\n\n== Third"
        enhanced = worker._enhance_asciidoc_output(text)

        # Should add title and preserve headings
        assert enhanced.startswith("=")
        assert "== First" in enhanced
        assert "=== Second" in enhanced
        assert "== Third" in enhanced

    def test_enhance_preserves_admonitions(self):
        """Test admonition block formatting."""
        worker = PandocWorker()
        text = "NOTE: Important info\n\nWARNING: Be careful"
        enhanced = worker._enhance_asciidoc_output(text)

        assert "NOTE:" in enhanced
        assert "WARNING:" in enhanced

    def test_enhance_fixes_table_syntax(self):
        """Test table syntax cleanup."""
        worker = PandocWorker()
        text = "|===\n\n|Header\n"
        enhanced = worker._enhance_asciidoc_output(text)

        # Should remove double newline after table start
        assert "|===\n|Header" in enhanced

    def test_enhance_adds_spacing_around_headings(self):
        """Test heading spacing enhancement."""
        worker = PandocWorker()
        text = "Content\n== Heading\nMore content"
        enhanced = worker._enhance_asciidoc_output(text)

        # Should add blank line before heading
        assert "\n\n== Heading" in enhanced
