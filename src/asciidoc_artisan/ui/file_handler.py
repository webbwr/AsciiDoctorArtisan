"""
File Handler - Manage file operations.

This module handles all file I/O operations for AsciiDoc Artisan:
- Opening files (all supported formats)
- Saving files (AsciiDoc, HTML)
- Creating new files
- Managing file state and unsaved changes
- Auto-save functionality

Extracted from main_window.py to improve maintainability and testability.
"""

import logging
import platform
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPlainTextEdit

from asciidoc_artisan.core import (
    SUPPORTED_OPEN_FILTER,
    SUPPORTED_SAVE_FILTER,
    atomic_save_text,
)

logger = logging.getLogger(__name__)


class FileHandler(QObject):
    """Handle all file I/O operations."""

    # Signals
    file_opened = Signal(Path)  # Emitted when file is opened
    file_saved = Signal(Path)  # Emitted when file is saved
    file_modified = Signal(bool)  # Emitted when unsaved changes state changes

    def __init__(
        self, editor: QPlainTextEdit, parent_window, settings_manager, status_manager
    ):
        """
        Initialize FileHandler.

        Args:
            editor: The text editor widget
            parent_window: Main window (for dialogs)
            settings_manager: Settings manager instance
            status_manager: Status manager instance
        """
        super().__init__(parent_window)
        self.editor = editor
        self.window = parent_window
        self.settings_manager = settings_manager
        self.status_manager = status_manager

        # File state
        self.current_file_path: Optional[Path] = None
        self.unsaved_changes = False
        self.is_opening_file = False

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)

        # Connect editor changes to track modifications
        self.editor.textChanged.connect(self._on_text_changed)

    def start_auto_save(self, interval_ms: int = 300000) -> None:
        """
        Start auto-save timer.

        Args:
            interval_ms: Auto-save interval in milliseconds (default: 5 minutes)
        """
        self.auto_save_timer.start(interval_ms)
        logger.info(f"Auto-save enabled: {interval_ms / 1000 / 60:.1f} minutes")

    def stop_auto_save(self) -> None:
        """Stop auto-save timer."""
        self.auto_save_timer.stop()
        logger.info("Auto-save disabled")

    @Slot()
    def new_file(self) -> None:
        """Create a new empty file."""
        if self.unsaved_changes:
            if not self.prompt_save_before_action("creating a new file"):
                return

        self.editor.clear()
        self.current_file_path = None
        self.unsaved_changes = False
        self.status_manager.update_window_title()
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage("New file created")

        logger.info("New file created")

    @Slot()
    def open_file(self, file_path: Optional[str] = None) -> None:
        """
        Open a file.

        Args:
            file_path: Path to file to open. If None, shows file dialog.
        """
        # Check for unsaved changes
        if self.unsaved_changes:
            if not self.prompt_save_before_action("opening a new file"):
                return

        # Show file dialog if no path provided
        if not file_path:
            settings = self.settings_manager.load_settings()
            last_dir = (
                settings.last_directory if hasattr(settings, "last_directory") else ""
            )

            file_path_str, _ = QFileDialog.getOpenFileName(
                self.window,
                "Open File",
                last_dir,
                SUPPORTED_OPEN_FILTER,
                options=(
                    QFileDialog.Option.DontUseNativeDialog
                    if platform.system() != "Windows"
                    else QFileDialog.Option(0)
                ),
            )
            if not file_path_str:
                return  # User cancelled
            file_path = file_path_str

        # Validate path
        path = Path(file_path)
        if not path.exists():
            self.status_manager.show_message(
                "critical", "Error", f"File not found:\n{path}"
            )
            return

        # Load file
        try:
            self._load_file_content(path)
        except Exception as e:
            logger.error(f"Failed to open file {path}: {e}")
            self.status_manager.show_message(
                "critical", "Error", f"Failed to open file:\n{e}"
            )

    def _load_file_content(self, file_path: Path) -> None:
        """
        Load file content into editor.

        Args:
            file_path: Path to file to load
        """
        self.is_opening_file = True

        # Optional memory profiling (enabled via environment variable)
        import os

        if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
            from asciidoc_artisan.core import get_profiler

            profiler = get_profiler()
            if profiler.is_running:
                profiler.take_snapshot(f"before_load_{file_path.name}")

        try:
            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Load into editor
            self.editor.setPlainText(content)

            # Update state
            self.current_file_path = file_path
            self.unsaved_changes = False

            # Update UI
            self.status_manager.update_window_title()
            if hasattr(self.window, "status_bar"):
                self.window.status_bar.showMessage(f"Opened: {file_path.name}")

            # Save as last directory
            settings = self.settings_manager.load_settings()
            settings.last_directory = str(file_path.parent)
            self.settings_manager.save_settings(settings)

            # Emit signal
            self.file_opened.emit(file_path)

            # Update document metrics (version, word count, grade level)
            self.status_manager.update_document_metrics()

            logger.info(f"Opened file: {file_path}")

            # Optional memory profiling
            import os

            if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
                from asciidoc_artisan.core import get_profiler

                profiler = get_profiler()
                if profiler.is_running:
                    profiler.take_snapshot(f"after_load_{file_path.name}")

        finally:
            self.is_opening_file = False

    @Slot()
    def save_file(self, save_as: bool = False) -> bool:
        """
        Save the current file.

        Args:
            save_as: If True, always show save dialog

        Returns:
            True if saved successfully, False otherwise
        """
        # Determine save path
        if save_as or not self.current_file_path:
            settings = self.settings_manager.load_settings()
            last_dir = (
                settings.last_directory if hasattr(settings, "last_directory") else ""
            )

            file_path_str, _ = QFileDialog.getSaveFileName(
                self.window,
                "Save File",
                last_dir,
                SUPPORTED_SAVE_FILTER,
                options=(
                    QFileDialog.Option.DontUseNativeDialog
                    if platform.system() != "Windows"
                    else QFileDialog.Option(0)
                ),
            )
            if not file_path_str:
                return False  # User cancelled

            save_path = Path(file_path_str)
        else:
            save_path = self.current_file_path

        # Get content
        content = self.editor.toPlainText()

        # Save file
        try:
            if atomic_save_text(save_path, content, encoding="utf-8"):
                # Update state
                self.current_file_path = save_path
                self.unsaved_changes = False

                # Update UI
                self.status_manager.update_window_title()
                if hasattr(self.window, "status_bar"):
                    self.window.status_bar.showMessage(f"Saved: {save_path.name}")

                # Save as last directory
                settings = self.settings_manager.load_settings()
                settings.last_directory = str(save_path.parent)
                self.settings_manager.save_settings(settings)

                # Emit signal
                self.file_saved.emit(save_path)

                # Update document metrics (version, word count, grade level)
                self.status_manager.update_document_metrics()

                logger.info(f"Saved file: {save_path}")
                return True
            else:
                raise IOError(f"Atomic save failed for {save_path}")

        except Exception as e:
            logger.error(f"Failed to save file {save_path}: {e}")
            self.status_manager.show_message(
                "critical", "Save Error", f"Failed to save file:\n{e}"
            )
            return False

    @Slot()
    def auto_save(self) -> None:
        """Auto-save current file if there are unsaved changes."""
        if self.unsaved_changes and self.current_file_path:
            logger.debug("Auto-saving file...")
            self.save_file(save_as=False)

    def prompt_save_before_action(self, action: str) -> bool:
        """
        Prompt user to save before performing an action.

        Args:
            action: Description of action (e.g., "opening a new file")

        Returns:
            True if user wants to continue, False to cancel
        """
        if not self.unsaved_changes:
            return True

        reply = QMessageBox.question(
            self.window,
            "Unsaved Changes",
            f"You have unsaved changes. Save before {action}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.unsaved_changes

    def get_current_file_path(self) -> Optional[Path]:
        """Get current file path."""
        return self.current_file_path

    def _on_text_changed(self) -> None:
        """Handle text changed in editor."""
        if not self.is_opening_file:
            if not self.unsaved_changes:
                self.unsaved_changes = True
                self.file_modified.emit(True)
