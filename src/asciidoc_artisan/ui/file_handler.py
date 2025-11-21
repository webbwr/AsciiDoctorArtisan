"""
File Handler - Manage file operations.

This module handles all file I/O operations for AsciiDoc Artisan:
- Opening files (all supported formats)
- Saving files (AsciiDoc, HTML)
- Creating new files
- Managing file state and unsaved changes
- Auto-save functionality
- Async file I/O with Qt integration (v1.7.0)
- File watching for external changes (v1.7.0)

Extracted from main_window.py to improve maintainability and testability.
"""

import asyncio
import logging
import platform
import time
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QMessageBox, QPlainTextEdit

from asciidoc_artisan.core import (
    MAX_FILE_SIZE_MB,
    SUPPORTED_OPEN_FILTER,
    SUPPORTED_SAVE_FILTER,
    QtAsyncFileManager,
)

# Import metrics
try:
    from asciidoc_artisan.core.metrics import get_metrics_collector

    METRICS_AVAILABLE = True
except ImportError:
    get_metrics_collector = None
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class FileHandler(QObject):
    """Handle all file I/O operations."""

    # Signals
    file_opened = Signal(Path)  # Emitted when file is opened
    file_saved = Signal(Path)  # Emitted when file is saved
    file_modified = Signal(bool)  # Emitted when unsaved changes state changes
    file_changed_externally = Signal(Path)  # Emitted when file modified externally (v1.7.0)

    def __init__(
        self,
        editor: QPlainTextEdit,
        parent_window: Any,
        settings_manager: Any,
        status_manager: Any,
    ) -> None:
        """Initialize FileHandler with editor, parent window, and managers."""
        super().__init__(parent_window)
        self.editor = editor
        self.window = parent_window
        self.settings_manager = settings_manager
        self.status_manager = status_manager

        # File state
        self.current_file_path: Path | None = None
        self.unsaved_changes = False
        self.is_opening_file = False

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)

        # Async file manager (v1.7.0)
        self.async_manager = QtAsyncFileManager()
        self.async_manager.read_complete.connect(self._on_async_read_complete)
        self.async_manager.write_complete.connect(self._on_async_write_complete)
        self.async_manager.operation_failed.connect(self._on_async_operation_failed)
        self.async_manager.file_changed_externally.connect(self._on_file_changed_externally)

        # Connect editor changes to track modifications
        self.editor.textChanged.connect(self._on_text_changed)

    def start_auto_save(self, interval_ms: int = 300000) -> None:
        """Start auto-save timer (default: 5 minutes)."""
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
    def open_file(self, file_path: str | None = None) -> None:
        """Open file (shows dialog if path not provided)."""
        # Check for unsaved changes
        if self.unsaved_changes:
            if not self.prompt_save_before_action("opening a new file"):
                return

        # Show file dialog if no path provided
        if not file_path:
            settings = self.settings_manager.load_settings()
            last_dir = settings.last_directory if hasattr(settings, "last_directory") else ""

            file_path_str, _ = QFileDialog.getOpenFileName(
                self.window,
                "Open File",
                last_dir,
                SUPPORTED_OPEN_FILTER,
                options=(
                    QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option(0)
                ),
            )
            if not file_path_str:  # pragma: no cover
                return  # User cancelled
            file_path = file_path_str  # pragma: no cover

        # Validate path
        path = Path(file_path)
        if not path.exists():
            self.status_manager.show_message("critical", "Error", f"File not found:\n{path}")
            return

        # Load file - launch async operation
        asyncio.ensure_future(self._load_file_async(path))

    def _validate_file_size(self, file_path: Path) -> bool:
        """Validate file size before loading (MA: extracted 24 lines)."""
        try:
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:  # pragma: no cover
                error_msg = (
                    f"File too large: {file_size_mb:.1f}MB\n"
                    f"Maximum allowed: {MAX_FILE_SIZE_MB}MB\n\n"
                    f"Large files may cause the application to freeze or crash."
                )
                self.status_manager.show_message("critical", "File Too Large", error_msg)
                logger.warning(f"Rejected file {file_path.name}: {file_size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB")
                return False

            # Log file size for monitoring
            if file_size_mb > 10:
                logger.info(f"Opening large file: {file_path.name} ({file_size_mb:.1f}MB)")

            return True

        except Exception as e:
            logger.error(f"Failed to check file size for {file_path}: {e}")
            return False

    def _take_memory_snapshot(self, snapshot_name: str) -> None:
        """Take memory profiling snapshot if enabled (MA: extracted 9 lines)."""
        import os

        if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
            from asciidoc_artisan.core import get_profiler

            profiler = get_profiler()
            if profiler.is_running:
                profiler.take_snapshot(snapshot_name)

    def _update_editor_and_state(self, file_path: Path, content: str) -> None:
        """Load content into editor and update state (MA: extracted 8 lines)."""
        self.editor.setPlainText(content)
        self.current_file_path = file_path
        self.unsaved_changes = False

    def _update_ui_after_load(self, file_path: Path) -> None:
        """Update UI components after file load (MA: extracted 8 lines)."""
        self.status_manager.update_window_title()
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage(f"Opened: {file_path.name}")

    def _finalize_file_load(self, file_path: Path, start_time: float) -> None:
        """Finalize file load: save settings, emit signals, record metrics (MA: extracted 18 lines)."""
        # Save as last directory
        settings = self.settings_manager.load_settings()
        settings.last_directory = str(file_path.parent)
        self.settings_manager.save_settings(settings)

        # Emit signal
        self.file_opened.emit(file_path)

        # Update document metrics (version, word count, grade level)
        self.status_manager.update_document_metrics()

        # Start watching file for external changes (v1.7.0)
        self.async_manager.watch_file(file_path)

        # Record metrics
        if METRICS_AVAILABLE and get_metrics_collector:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics = get_metrics_collector()
            metrics.record_operation("file_open", duration_ms)

        logger.info(f"Opened file: {file_path} (async)")

    async def _load_file_async(self, file_path: Path) -> None:
        """Load file asynchronously (MA: 105→28 lines, 5 helpers, 73% reduction). v1.7.0: async I/O."""
        start_time = time.perf_counter()
        self.is_opening_file = True

        # Validate file size (Security: Prevent memory exhaustion - DoS prevention)
        if not self._validate_file_size(file_path):
            self.is_opening_file = False
            return

        # Optional memory profiling before load
        self._take_memory_snapshot(f"before_load_{file_path.name}")

        try:
            # Read file asynchronously (v1.7.0)
            content = await self.async_manager.read_file(file_path, encoding="utf-8")

            if content is None:
                # Error already handled by async_manager signal
                return

            # Load content and update state
            self._update_editor_and_state(file_path, content)

            # Update UI components
            self._update_ui_after_load(file_path)

            # Finalize: save settings, emit signals, record metrics
            self._finalize_file_load(file_path, start_time)

            # Optional memory profiling after load
            self._take_memory_snapshot(f"after_load_{file_path.name}")

        except Exception as e:
            logger.error(f"Failed to open file {file_path}: {e}")
            self.status_manager.show_message("critical", "Error", f"Failed to open file:\n{e}")
        finally:
            self.is_opening_file = False

    @Slot()
    def save_file(self, save_as: bool = False) -> bool:
        """Save file (v1.7.0: async operation, success via file_saved signal)."""
        # Determine save path
        if save_as or not self.current_file_path:
            settings = self.settings_manager.load_settings()
            last_dir = settings.last_directory if hasattr(settings, "last_directory") else ""

            file_path_str, _ = QFileDialog.getSaveFileName(
                self.window,
                "Save File",
                last_dir,
                SUPPORTED_SAVE_FILTER,
                options=(
                    QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option(0)
                ),
            )
            if not file_path_str:
                return False  # User cancelled

            save_path = Path(file_path_str)
        else:
            save_path = self.current_file_path

        # Get content
        content = self.editor.toPlainText()

        # Launch async save operation (v1.7.0)
        asyncio.ensure_future(self._save_file_async(save_path, content))
        return True  # Operation started

    async def _save_file_async(self, save_path: Path, content: str) -> None:
        """Save file asynchronously (v1.7.0: async I/O)."""
        start_time = time.perf_counter()

        try:
            # Save file asynchronously (v1.7.0)
            success = await self.async_manager.write_file(save_path, content, encoding="utf-8")

            if success:
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

                # Record metrics
                if METRICS_AVAILABLE and get_metrics_collector:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    metrics = get_metrics_collector()
                    metrics.record_operation("file_save", duration_ms)

                logger.info(f"Saved file: {save_path} (async)")
            else:
                raise OSError(f"Async atomic save failed for {save_path}")

        except Exception as e:
            logger.error(f"Failed to save file {save_path}: {e}")
            self.status_manager.show_message("critical", "Save Error", f"Failed to save file:\n{e}")

    @Slot()
    def auto_save(self) -> None:
        """Auto-save current file if there are unsaved changes."""
        if self.unsaved_changes and self.current_file_path:
            logger.debug("Auto-saving file...")
            self.save_file(save_as=False)

    def prompt_save_before_action(self, action: str) -> bool:
        """Prompt user to save before action (returns True to continue, False to cancel)."""
        import os

        # Skip prompts in test environment to prevent blocking
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return True

        if not self.unsaved_changes:  # pragma: no cover
            return True

        reply = QMessageBox.question(
            self.window,
            "Unsaved Changes",
            f"You have unsaved changes. Save before {action}?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()  # type: ignore[no-any-return]  # save_file returns bool but QMessageBox comparison returns Any
        elif reply == QMessageBox.StandardButton.Discard:  # pragma: no cover
            return True
        else:  # Cancel
            return False

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.unsaved_changes

    def get_current_file_path(self) -> Path | None:
        """Get current file path."""
        return self.current_file_path

    def _on_text_changed(self) -> None:
        """Handle text changed in editor."""
        if not self.is_opening_file:
            if not self.unsaved_changes:
                self.unsaved_changes = True
                self.file_modified.emit(True)

    # === ASYNC OPERATION SIGNAL HANDLERS (v1.7.0) ===

    def _on_async_read_complete(self, file_path: Path, content: str) -> None:
        """Handle async read complete signal (v1.7.0)."""
        logger.debug(f"Async read complete: {file_path}")

    def _on_async_write_complete(self, file_path: Path) -> None:
        """Handle async write complete signal (v1.7.0)."""
        logger.debug(f"Async write complete: {file_path}")

    def _on_async_operation_failed(self, operation: str, file_path: Path, error: str) -> None:
        """Handle async operation failure signal (v1.7.0)."""
        logger.error(f"Async {operation} failed for {file_path}: {error}")
        # Error message already shown by async operation handlers

    def _on_file_changed_externally(self, file_path: Path) -> None:
        """Handle file changed externally signal (v1.7.0: file watcher)."""
        logger.info(f"File changed externally: {file_path}")

        # Emit signal for main window to handle
        self.file_changed_externally.emit(file_path)

        # Show message to user
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage(f"File modified externally: {file_path.name}", 5000)
