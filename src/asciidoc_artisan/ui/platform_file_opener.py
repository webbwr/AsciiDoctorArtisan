"""
Platform File Opener - Cross-platform file opening utilities.

Extracted from TelemetryDialogHandler to reduce class size (MA principle).
Handles platform-specific file opening for Windows, macOS, WSL, and Linux.
"""

import logging
import platform
import subprocess
from pathlib import Path
from typing import Protocol

from PySide6.QtWidgets import QMessageBox, QWidget

logger = logging.getLogger(__name__)


class ParentWidgetProtocol(Protocol):
    """Protocol for parent widget that can show message boxes."""

    pass


class PlatformFileOpener:
    """
    Cross-platform file opening utility.

    Extracted from TelemetryDialogHandler per MA principle (~100 lines).

    Handles:
    - Windows: Opens with notepad
    - macOS: Opens with default application via 'open' command
    - WSL: Converts path and opens with Windows notepad
    - Linux: Opens with xdg-open, falls back to less in terminal
    """

    def __init__(self, parent_widget: QWidget | None = None) -> None:
        """
        Initialize file opener.

        Args:
            parent_widget: Parent widget for error dialogs (optional)
        """
        self.parent_widget = parent_widget

    def open_file(self, file_path: Path) -> bool:
        """
        Open file in platform-appropriate application.

        Args:
            file_path: Path to file to open

        Returns:
            True if file opened successfully, False otherwise
        """
        logger.info(f"Opening file: {file_path}")
        try:
            system = platform.system()
            if system == "Windows":
                self._open_file_windows(file_path)
            elif system == "Darwin":  # macOS
                self._open_file_macos(file_path)
            else:  # Linux/Unix
                if self._check_wsl_environment():
                    self._open_file_wsl(file_path)
                else:
                    self._open_file_linux(file_path)

            logger.info(f"Successfully opened file: {file_path.name}")
            return True
        except (subprocess.CalledProcessError, Exception) as e:
            self._handle_file_open_error(e, file_path)
            return False

    def _check_wsl_environment(self) -> bool:
        """
        Check if running in Windows Subsystem for Linux.

        Returns:
            True if running in WSL, False otherwise
        """
        try:
            with open("/proc/version") as f:
                return "microsoft" in f.read().lower()
        except (FileNotFoundError, PermissionError, OSError):
            return False

    def _open_file_windows(self, file_path: Path) -> None:
        """
        Open file with Windows notepad.

        Args:
            file_path: Path to file to open
        """
        result = subprocess.run(
            ["notepad", str(file_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Notepad command succeeded: {result}")

    def _open_file_macos(self, file_path: Path) -> None:
        """
        Open file with macOS default application.

        Args:
            file_path: Path to file to open
        """
        result = subprocess.run(
            ["open", str(file_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Open command succeeded: {result}")

    def _open_file_wsl(self, file_path: Path) -> None:
        """
        Open file in WSL using Windows notepad.

        Args:
            file_path: Path to file to open
        """
        try:
            # Convert Linux path to Windows path
            win_path_result = subprocess.run(
                ["wslpath", "-w", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            win_path = win_path_result.stdout.strip()

            # Open with Windows notepad
            subprocess.run(
                ["/mnt/c/Windows/System32/notepad.exe", win_path],
                check=False,  # Don't check return code
                capture_output=True,
                text=True,
            )
            logger.info("WSL notepad.exe command succeeded")
        except Exception as wsl_error:
            logger.warning(f"WSL notepad failed: {wsl_error}, falling back to less")
            # Fall back to less (simple viewer)
            subprocess.run(
                [
                    "x-terminal-emulator",
                    "-e",
                    "less",
                    str(file_path),
                ]
            )

    def _open_file_linux(self, file_path: Path) -> None:
        """
        Open file on Linux with xdg-open or fallback to less.

        Args:
            file_path: Path to file to open
        """
        try:
            result = subprocess.run(
                ["xdg-open", str(file_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info(f"xdg-open command succeeded: {result}")
        except FileNotFoundError:
            # xdg-open not available, use less as fallback
            logger.info("xdg-open not found, using less as viewer")
            subprocess.run(
                [
                    "x-terminal-emulator",
                    "-e",
                    "less",
                    str(file_path),
                ]
            )

    def _handle_file_open_error(self, error: Exception, file_path: Path) -> None:
        """
        Handle file opening errors with user-friendly dialogs.

        Args:
            error: Exception that occurred
            file_path: Path to file that failed to open
        """
        if isinstance(error, subprocess.CalledProcessError):
            error_msg = f"Failed to open file: {error}\nStderr: {error.stderr}"
            logger.error(error_msg)
            if self.parent_widget:
                QMessageBox.warning(
                    self.parent_widget,
                    "Open File Failed",
                    f"Could not open file:\n{file_path}\n\nError: {error.stderr or str(error)}",
                )
        else:
            error_msg = f"Unexpected error opening file: {type(error).__name__}: {error}"
            logger.error(error_msg, exc_info=True)
            if self.parent_widget:
                QMessageBox.warning(
                    self.parent_widget,
                    "Open File Failed",
                    f"Unexpected error:\n{str(error)}",
                )
