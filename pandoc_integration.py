"""
Pandoc Integration Module for AsciiDoc Artisan

Provides high-performance pandoc integration with automatic installation detection,
format support querying, and intelligent error handling.
"""

import logging
import platform
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PandocIntegration:
    """High-performance pandoc integration with caching and optimized format detection."""

    EXTENSION_MAP = {
        ".md": "markdown",
        ".markdown": "markdown",
        ".docx": "docx",
        ".html": "html",
        ".htm": "html",
        ".tex": "latex",
        ".rst": "rst",
        ".org": "org",
        ".wiki": "mediawiki",
        ".textile": "textile",
    }

    FORMAT_DESCRIPTIONS = {
        "asciidoc": "AsciiDoc - Text document format for documentation",
        "markdown": "Markdown - Lightweight markup language",
        "docx": "Microsoft Word Document",
        "html": "HTML - HyperText Markup Language",
        "latex": "LaTeX - Document preparation system",
        "rst": "reStructuredText - Markup language",
        "org": "Org-mode - Emacs organization format",
        "mediawiki": "MediaWiki markup format",
        "textile": "Textile markup language",
    }

    __slots__ = (
        "pandoc_path",
        "pypandoc_available",
        "pandoc_version",
        "supported_formats",
    )

    def __init__(self):
        self.pandoc_path: Optional[str] = None
        self.pypandoc_available: bool = False
        self.pandoc_version: Optional[str] = None
        self.supported_formats: Dict[str, List[str]] = {"input": [], "output": []}
        self.check_installation()

    def check_installation(self) -> Tuple[bool, str]:
        """
        Check pandoc and pypandoc installation status.

        Returns:
            Tuple of (is_available, status_message)
        """
        self.pandoc_path = shutil.which("pandoc")
        if not self.pandoc_path:
            return False, "Pandoc binary not found. Please install pandoc."

        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                self.pandoc_version = result.stdout.split("\n")[0]
                logger.info(f"Found {self.pandoc_version}")
            else:
                return False, "Pandoc found but version check failed."
        except Exception as e:
            logger.error(f"Error checking pandoc version: {e}")
            return False, f"Error checking pandoc: {e}"

        try:
            import pypandoc

            self.pypandoc_available = True
            self._get_supported_formats()
            return True, f"{self.pandoc_version} and pypandoc properly installed."
        except ImportError:
            return False, "pypandoc not installed. Run: pip install pypandoc"

    def _get_supported_formats(self) -> None:
        """Query pandoc for supported input/output formats."""
        for direction, flag in [
            ("input", "--list-input-formats"),
            ("output", "--list-output-formats"),
        ]:
            try:
                result = subprocess.run(
                    ["pandoc", flag],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    self.supported_formats[direction] = result.stdout.strip().split(
                        "\n"
                    )
            except Exception as e:
                logger.error(f"Error getting {direction} formats: {e}")

    @staticmethod
    @lru_cache(maxsize=1)
    def get_installation_instructions() -> str:
        """Get platform-specific installation instructions. Cached."""
        system = platform.system()
        base = "To install pandoc:\n\n"

        instructions = {
            "Windows": """Windows:
1. Download from https://pandoc.org/installing.html
2. Run installer and restart application

Chocolatey: choco install pandoc
Scoop: scoop install pandoc""",
            "Darwin": """macOS:
Homebrew: brew install pandoc
Or download from https://pandoc.org/installing.html""",
            "Linux": """Linux:
Ubuntu/Debian: sudo apt-get install pandoc
Fedora/RHEL: sudo dnf install pandoc
Arch: sudo pacman -S pandoc
Or download from https://pandoc.org/installing.html""",
        }

        return (
            base
            + instructions.get(system, instructions["Linux"])
            + "\n\nThen: pip install pypandoc"
        )

    def auto_install_pypandoc(self) -> Tuple[bool, str]:
        """
        Attempt automatic pypandoc installation via pip.

        Returns:
            Tuple of (success, message)
        """
        if not self.pandoc_path:
            return False, "Cannot install pypandoc: pandoc binary not found."

        try:
            logger.info("Installing pypandoc...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pypandoc"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode == 0:
                self.check_installation()
                return (
                    (True, "pypandoc installed successfully!")
                    if self.pypandoc_available
                    else (False, "pypandoc installation completed but import failed.")
                )

            return (
                False,
                f"Failed to install pypandoc: {result.stderr or result.stdout}",
            )

        except Exception as e:
            logger.error(f"Error installing pypandoc: {e}")
            return False, f"Error installing pypandoc: {e}"

    def convert_file(
        self, input_file: Path, output_format: str, input_format: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Convert file using pandoc with automatic format detection.

        Args:
            input_file: Path to input file
            output_format: Target format (e.g., 'asciidoc')
            input_format: Source format (auto-detected if None)

        Returns:
            Tuple of (success, converted_text, error_message)
        """
        if not self.pypandoc_available:
            return False, "", "pypandoc not available"

        try:
            import pypandoc

            if not input_format:
                input_format = self.EXTENSION_MAP.get(
                    input_file.suffix.lower(), "markdown"
                )

            logger.info(
                f"Converting {input_file.name}: {input_format} → {output_format}"
            )

            content = (
                input_file.read_bytes()
                if input_file.suffix.lower() == ".docx"
                else input_file.read_text(encoding="utf-8")
            )

            result = pypandoc.convert_text(
                source=content,
                to=output_format,
                format=input_format,
                extra_args=["--wrap=preserve"],
            )

            return True, result, ""

        except Exception as e:
            error_msg = f"Conversion error: {e}"
            logger.error(error_msg)
            return False, "", error_msg

    @staticmethod
    def get_format_info(format_name: str) -> str:
        """Get human-readable format description."""
        return PandocIntegration.FORMAT_DESCRIPTIONS.get(format_name, format_name)

    def is_format_supported(self, format_name: str, direction: str = "input") -> bool:
        """
        Check if format is supported by pandoc.

        Args:
            format_name: Format identifier
            direction: 'input' or 'output'

        Returns:
            True if format is supported
        """
        return format_name in self.supported_formats.get(direction, [])


pandoc = PandocIntegration()


def ensure_pandoc_available() -> Tuple[bool, str]:
    """
    Ensure pandoc is available with user-friendly error handling.

    Returns:
        Tuple of (is_available, message)
    """
    is_available, status = pandoc.check_installation()

    if not is_available and pandoc.pandoc_path and not pandoc.pypandoc_available:
        success, msg = pandoc.auto_install_pypandoc()
        if success:
            return True, msg
        return (
            False,
            status + "\n\n" + PandocIntegration.get_installation_instructions(),
        )

    return is_available, (
        status
        if is_available
        else status + "\n\n" + PandocIntegration.get_installation_instructions()
    )


if __name__ == "__main__":
    available, message = ensure_pandoc_available()
    print(f"Pandoc available: {available}")
    print(f"Status: {message}")

    if available:
        print("\nSupported formats:")
        print(f"  Input: {len(pandoc.supported_formats['input'])}")
        print(f"  Output: {len(pandoc.supported_formats['output'])}")
