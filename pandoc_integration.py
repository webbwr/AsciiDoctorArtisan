#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandoc Integration Module for AsciiDoc Artisan
=============================================

This module provides enhanced pandoc integration with automatic installation
detection, better error handling, and support for multiple conversion formats.
"""

import logging
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PandocIntegration:
    """Enhanced pandoc integration with automatic setup and conversion support."""

    def __init__(self):
        self.pandoc_path: Optional[str] = None
        self.pypandoc_available: bool = False
        self.pandoc_version: Optional[str] = None
        self.supported_formats: Dict[str, List[str]] = {"input": [], "output": []}
        self.check_installation()

    def check_installation(self) -> Tuple[bool, str]:
        """
        Check if pandoc and pypandoc are properly installed.

        Returns:
            Tuple of (is_available, status_message)
        """
        # Check pandoc binary
        self.pandoc_path = shutil.which("pandoc")
        if not self.pandoc_path:
            return False, "Pandoc binary not found. Please install pandoc."

        # Get pandoc version
        try:
            result = subprocess.run(
                ["pandoc", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.pandoc_version = result.stdout.split("\n")[0]
                logger.info(f"Found {self.pandoc_version}")
            else:
                return False, "Pandoc found but version check failed."
        except Exception as e:
            logger.error(f"Error checking pandoc version: {e}")
            return False, f"Error checking pandoc: {str(e)}"

        # Check pypandoc
        try:
            import pypandoc

            self.pypandoc_available = True

            # Get supported formats
            self._get_supported_formats()

            return True, f"{self.pandoc_version} and pypandoc are properly installed."
        except ImportError:
            return False, "pypandoc not installed. Run: pip install pypandoc"

    def _get_supported_formats(self) -> None:
        """Get list of supported input and output formats from pandoc."""
        try:
            # Get input formats
            result = subprocess.run(
                ["pandoc", "--list-input-formats"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.supported_formats["input"] = result.stdout.strip().split("\n")

            # Get output formats
            result = subprocess.run(
                ["pandoc", "--list-output-formats"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.supported_formats["output"] = result.stdout.strip().split("\n")

        except Exception as e:
            logger.error(f"Error getting supported formats: {e}")

    def get_installation_instructions(self) -> str:
        """Get platform-specific installation instructions."""
        system = platform.system()

        instructions = "To install pandoc:\n\n"

        if system == "Windows":
            instructions += """Windows:
1. Download installer from https://pandoc.org/installing.html
2. Run the installer
3. Restart your application

Or using Chocolatey:
   choco install pandoc

Or using Scoop:
   scoop install pandoc"""

        elif system == "Darwin":  # macOS
            instructions += """macOS:
Using Homebrew:
   brew install pandoc

Or download from https://pandoc.org/installing.html"""

        else:  # Linux/Unix
            instructions += """Linux:
Ubuntu/Debian:
   sudo apt-get install pandoc

Fedora/RHEL:
   sudo dnf install pandoc

Arch Linux:
   sudo pacman -S pandoc

Or download from https://pandoc.org/installing.html"""

        instructions += "\n\nThen install pypandoc:\n   pip install pypandoc"

        return instructions

    def auto_install_pypandoc(self) -> Tuple[bool, str]:
        """
        Attempt to automatically install pypandoc using pip.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if pandoc binary is available first
            if not self.pandoc_path:
                return False, "Cannot install pypandoc: pandoc binary not found."

            logger.info("Attempting to install pypandoc...")

            # Use subprocess to install pypandoc
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pypandoc"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Reload and check
                self.check_installation()
                if self.pypandoc_available:
                    return True, "pypandoc installed successfully!"
                else:
                    return False, "pypandoc installation completed but import failed."
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"Failed to install pypandoc: {error_msg}"

        except Exception as e:
            logger.error(f"Error installing pypandoc: {e}")
            return False, f"Error installing pypandoc: {str(e)}"

    def convert_file(
        self, input_file: Path, output_format: str, input_format: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Convert a file using pandoc.

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

            # Auto-detect input format from extension if not provided
            if not input_format:
                extension_map = {
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
                input_format = extension_map.get(input_file.suffix.lower(), "markdown")

            logger.info(f"Converting {input_file} from {input_format} to {output_format}")

            # Read file content
            if input_file.suffix.lower() in [".docx"]:
                # Binary files
                content = input_file.read_bytes()
            else:
                # Text files
                content = input_file.read_text(encoding="utf-8")

            # Convert using pypandoc
            result = pypandoc.convert_text(
                source=content,
                to=output_format,
                format=input_format,
                extra_args=["--wrap=preserve"],  # Preserve line breaks
            )

            return True, result, ""

        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

    def get_format_info(self, format_name: str) -> str:
        """Get information about a specific format."""
        format_descriptions = {
            "asciidoc": "AsciiDoc - A text document format for writing documentation",
            "markdown": "Markdown - Lightweight markup language",
            "docx": "Microsoft Word Document",
            "html": "HTML - HyperText Markup Language",
            "latex": "LaTeX - Document preparation system",
            "rst": "reStructuredText - Markup language",
            "org": "Org-mode - Emacs organization format",
            "mediawiki": "MediaWiki markup format",
            "textile": "Textile markup language",
        }

        return format_descriptions.get(format_name, format_name)

    def is_format_supported(self, format_name: str, direction: str = "input") -> bool:
        """
        Check if a format is supported.

        Args:
            format_name: The format to check
            direction: 'input' or 'output'

        Returns:
            True if format is supported
        """
        return format_name in self.supported_formats.get(direction, [])


# Global instance for easy access
pandoc = PandocIntegration()


def ensure_pandoc_available() -> Tuple[bool, str]:
    """
    Ensure pandoc is available, with user-friendly error handling.

    Returns:
        Tuple of (is_available, message)
    """
    is_available, status = pandoc.check_installation()

    if not is_available:
        # Try to auto-install pypandoc if pandoc binary exists
        if pandoc.pandoc_path and not pandoc.pypandoc_available:
            success, msg = pandoc.auto_install_pypandoc()
            if success:
                return True, msg

        # Return installation instructions
        return False, status + "\n\n" + pandoc.get_installation_instructions()

    return True, status


if __name__ == "__main__":
    # Test the integration
    available, message = ensure_pandoc_available()
    print(f"Pandoc available: {available}")
    print(f"Status: {message}")

    if available:
        print(f"\nSupported input formats: {len(pandoc.supported_formats['input'])}")
        print(f"Supported output formats: {len(pandoc.supported_formats['output'])}")
