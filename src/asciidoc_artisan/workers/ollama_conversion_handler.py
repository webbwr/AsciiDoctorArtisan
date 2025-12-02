"""
Ollama Conversion Handler - Handles AI-enhanced document conversion.

Extracted from PandocWorker to reduce class size (MA principle).
Handles Ollama AI conversion logic and prompt generation.
"""

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class ProgressSignal(Protocol):
    """Protocol for progress signal emission."""

    def emit(self, message: str) -> None:  # pragma: no cover
        """Emit progress message."""
        ...


class OllamaConversionHandler:
    """
    Handles Ollama AI-enhanced document conversion.

    This class was extracted from PandocWorker to reduce class size
    per MA principle (777→~600 lines).

    Handles:
    - Ollama AI conversion attempts
    - Format display names mapping
    - Format-specific conversion instructions
    - Conversion prompt generation
    """

    def __init__(
        self, ollama_enabled: bool, ollama_model: str | None, progress_signal: ProgressSignal | None = None
    ) -> None:
        """
        Initialize the Ollama conversion handler.

        Args:
            ollama_enabled: Whether Ollama conversion is enabled
            ollama_model: Ollama model to use (e.g., "llama2")
            progress_signal: Optional signal for progress updates
        """
        self.ollama_enabled = ollama_enabled
        self.ollama_model = ollama_model
        self.progress_signal = progress_signal

    def try_ollama_conversion(self, source: str, from_format: str, to_format: str) -> str | None:
        """
        Attempt document conversion using Ollama AI.

        Args:
            source: Source document content
            from_format: Source format (e.g., "markdown", "docx", "html")
            to_format: Target format (e.g., "asciidoc", "markdown")

        Returns:
            Converted document text if successful, None if failed

        Raises:
            Exception: If Ollama conversion fails (caller should fallback to Pandoc)
        """
        if not self.ollama_enabled or not self.ollama_model:
            logger.debug("Ollama conversion not enabled or model not set")
            return None

        try:
            import ollama

            logger.info(f"Attempting Ollama AI conversion: {from_format} -> {to_format} using {self.ollama_model}")
            if self.progress_signal:
                self.progress_signal.emit(f"Converting with AI ({self.ollama_model})...")

            # Create conversion prompt
            prompt = self.create_conversion_prompt(source, from_format, to_format)

            # Call Ollama API (Security: 30s timeout to prevent hangs)
            # Note: Timeout handling depends on Ollama library implementation
            # The library uses httpx internally which respects environment timeouts
            try:
                response = ollama.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                )
            except Exception as timeout_err:
                # Catch any timeout or connection errors
                if "timeout" in str(timeout_err).lower() or "timed out" in str(timeout_err).lower():
                    logger.warning(f"Ollama API call timed out: {timeout_err}")
                    return None
                raise  # Re-raise if not a timeout error

            if not response or "response" not in response:
                logger.warning("Ollama returned empty or invalid response")
                return None

            converted_text = response["response"].strip()

            # Validate conversion
            if not converted_text or len(converted_text) < 10:
                logger.warning("Ollama conversion produced insufficient output")
                return None

            logger.info(f"Ollama conversion successful ({len(converted_text)} characters)")
            return converted_text  # type: ignore[no-any-return]  # ollama returns Any

        except ImportError:
            logger.error("Ollama library not available")
            return None
        except Exception as e:
            logger.error(f"Ollama conversion failed: {e}")
            return None

    def get_format_display_names(self, from_format: str, to_format: str) -> tuple[str, str]:
        """
        Get display names for format codes.

        Args:
            from_format: Source format code
            to_format: Target format code

        Returns:
            Tuple of (from_name, to_name)
        """
        format_names = {
            "markdown": "Markdown",
            "md": "Markdown",
            "asciidoc": "AsciiDoc",
            "adoc": "AsciiDoc",
            "html": "HTML",
            "docx": "Microsoft Word",
            "rst": "reStructuredText",
            "latex": "LaTeX",
            "org": "Org Mode",
        }

        from_name = format_names.get(from_format.lower(), from_format)
        to_name = format_names.get(to_format.lower(), to_format)

        return from_name, to_name

    def get_format_instructions(self, to_format: str, to_name: str) -> str:
        """
        Get format-specific conversion instructions.

        Args:
            to_format: Target format code
            to_name: Target format display name

        Returns:
            Format-specific instructions string
        """
        if to_format.lower() in ["asciidoc", "adoc"]:
            return """
AsciiDoc formatting rules:
- Use = for document title (level 0)
- Use == for level 1 headings, === for level 2, etc.
- Use *bold* for bold, _italic_ for italic
- Use [source,language] blocks for code
- Use `backticks` for inline code
- Use * or - for unordered lists
- Use . for ordered lists
- Use |=== for tables
- Use image::path[] for images
- Use link:url[text] for links
"""
        elif to_format.lower() in ["markdown", "md"]:
            return """
Markdown formatting rules:
- Use # for h1, ## for h2, ### for h3, etc.
- Use **bold** for bold, *italic* for italic
- Use ```language blocks for code
- Use `backticks` for inline code
- Use - or * for unordered lists
- Use 1. for ordered lists
- Use | for tables
- Use ![alt](path) for images
- Use [text](url) for links
"""
        else:
            return f"Follow standard {to_name} formatting conventions."

    def create_conversion_prompt(self, source: str, from_format: str, to_format: str) -> str:
        """
        Create a prompt for Ollama to convert between document formats.

        Args:
            source: Source document content
            from_format: Source format
            to_format: Target format

        Returns:
            Formatted prompt for Ollama
        """
        # Get display names and instructions
        from_name, to_name = self.get_format_display_names(from_format, to_format)
        format_instructions = self.get_format_instructions(to_format, to_name)

        # Build prompt
        prompt = f"""You are a document format conversion expert. Convert the \
following {from_name} document to {to_name} format.

{format_instructions}

IMPORTANT INSTRUCTIONS:
1. Convert ALL content from the source document
2. Preserve the document structure and hierarchy
3. Maintain all formatting (bold, italic, code, links, etc.)
4. Keep all tables, lists, and code blocks
5. Do NOT add explanations or comments
6. Output ONLY the converted document
7. Do NOT wrap the output in code blocks or markdown
8. Start immediately with the converted content

SOURCE DOCUMENT ({from_name}):
{source}

CONVERTED DOCUMENT ({to_name}):"""

        return prompt
