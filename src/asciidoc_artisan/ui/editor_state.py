"""
Editor State Manager - Manage editor and window state.

This module handles:
- Pane maximize/restore functionality
- Zoom operations for editor and preview
- Dark mode toggle
- Synchronized scrolling toggle
- Window close event handling
- State persistence

Extracted from main_window.py to improve maintainability and testability.
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtWidgets import QPushButton, QSplitter, QStatusBar

from asciidoc_artisan.core import MIN_FONT_SIZE

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class EditorState:
    """Manage editor and window state."""

    def __init__(self, main_window: "AsciiDocEditor"):
        """
        Initialize EditorState.

        Args:
            main_window: Main window instance (for accessing widgets and settings)
        """
        self.window = main_window
        self.editor = main_window.editor
        self.preview = main_window.preview
        self.splitter: QSplitter = main_window.splitter
        self.status_bar: QStatusBar = main_window.status_bar
        self.editor_max_btn: QPushButton = main_window.editor_max_btn
        self.preview_max_btn: QPushButton = main_window.preview_max_btn
        self.theme_manager = main_window.theme_manager
        self._settings = main_window._settings
        self.action_manager = main_window.action_manager

        # Pane state
        self.maximized_pane: Optional[str] = None
        self.saved_splitter_sizes: Optional[list[int]] = None

        # Sync scrolling state (shared with main window)
        self.sync_scrolling = True

    def zoom(self, delta: int) -> None:
        """
        Zoom editor and preview.

        Args:
            delta: Zoom delta (positive to zoom in, negative to zoom out)
        """
        font = self.editor.font()
        new_size = max(MIN_FONT_SIZE, font.pointSize() + delta)
        font.setPointSize(new_size)
        self.editor.setFont(font)

        # Update preview zoom factor (QWebEngineView uses setZoomFactor)
        current_zoom = self.preview.zoomFactor()
        zoom_delta = 0.1 * delta  # Convert delta to zoom factor change
        new_zoom = max(0.25, min(5.0, current_zoom + zoom_delta))
        self.preview.setZoomFactor(new_zoom)

        logger.debug(
            f"Zoom changed: {delta}, new size: {new_size}, preview zoom: {new_zoom:.2f}"
        )

    def toggle_dark_mode(self) -> None:
        """Toggle dark mode on/off."""
        self._settings.dark_mode = self.action_manager.dark_mode_act.isChecked()
        self.theme_manager.apply_theme()
        self.window.update_preview()
        logger.info(f"Dark mode: {self._settings.dark_mode}")

    def toggle_sync_scrolling(self) -> None:
        """Toggle synchronized scrolling between editor and preview."""
        self.sync_scrolling = self.action_manager.sync_scrolling_act.isChecked()
        # Update main window's sync scrolling state
        self.window._sync_scrolling = self.sync_scrolling
        self.status_bar.showMessage(
            f"Synchronized scrolling {'enabled' if self.sync_scrolling else 'disabled'}",
            5000,
        )
        logger.info(f"Sync scrolling: {self.sync_scrolling}")

    def toggle_pane_maximize(self, pane: str) -> None:
        """
        Toggle maximize/restore for a specific pane.

        Args:
            pane: Pane to toggle ("editor" or "preview")
        """
        if self.maximized_pane == pane:
            # Restore if already maximized
            self.restore_panes()
        elif self.maximized_pane is not None:
            # Switch to other pane
            self.maximize_pane(pane)
        else:
            # Maximize from normal view
            self.maximize_pane(pane)

    def maximize_pane(self, pane: str) -> None:
        """
        Maximize a specific pane.

        Args:
            pane: Pane to maximize ("editor" or "preview")
        """
        # Save current sizes if not already maximized
        if self.maximized_pane is None:
            self.saved_splitter_sizes = self.splitter.sizes()

        if pane == "editor":
            # Maximize editor, hide preview
            self.splitter.setSizes([self.splitter.width(), 0])
            self.editor_max_btn.setText("⬛")
            self.editor_max_btn.setToolTip("Restore editor")

            self.preview_max_btn.setEnabled(True)
            self.preview_max_btn.setText("⬜")
            self.preview_max_btn.setToolTip("Maximize preview")
            self.status_bar.showMessage("Editor maximized", 3000)
        else:
            # Maximize preview, hide editor
            self.splitter.setSizes([0, self.splitter.width()])
            self.preview_max_btn.setText("⬛")
            self.preview_max_btn.setToolTip("Restore preview")

            self.editor_max_btn.setEnabled(True)
            self.editor_max_btn.setText("⬜")
            self.editor_max_btn.setToolTip("Maximize editor")
            self.status_bar.showMessage("Preview maximized", 3000)

        self.maximized_pane = pane
        logger.debug(f"Pane maximized: {pane}")

    def restore_panes(self) -> None:
        """Restore panes to their previous sizes."""
        if self.saved_splitter_sizes and len(self.saved_splitter_sizes) == 2:
            total = sum(self.saved_splitter_sizes)
            if total > 0:
                self.splitter.setSizes(self.saved_splitter_sizes)
            else:
                # Fallback to 50/50 split
                width = self.splitter.width()
                self.splitter.setSizes([width // 2, width // 2])
        else:
            # No saved sizes, use 50/50 split
            width = self.splitter.width()
            self.splitter.setSizes([width // 2, width // 2])

        # Reset button states
        self.editor_max_btn.setText("⬜")
        self.editor_max_btn.setToolTip("Maximize editor")
        self.editor_max_btn.setEnabled(True)
        self.preview_max_btn.setText("⬜")
        self.preview_max_btn.setToolTip("Maximize preview")
        self.preview_max_btn.setEnabled(True)

        self.maximized_pane = None
        self.status_bar.showMessage("View restored", 3000)
        logger.debug("Panes restored")

    def handle_close_event(self, event: Any) -> None:
        """
        Handle window close event.

        Args:
            event: Close event from Qt
        """
        # Check if we need to save
        if not self.window.status_manager.prompt_save_before_action("closing"):
            event.ignore()
            return

        # Save settings
        self.window._settings_manager.save_settings(
            self._settings, self.window, self.window._current_file_path
        )

        # Shutdown worker threads
        logger.info("Shutting down worker threads...")
        self._shutdown_threads()

        # Cleanup temporary files
        self._cleanup_temp_files()

        event.accept()
        logger.info("Application closed")

    def _shutdown_threads(self) -> None:
        """Safely shut down worker threads."""
        # Grammar functionality removed - no cleanup needed
        # (grammar_manager is now None)

        # Shutdown main worker threads
        threads = [
            ("git_thread", self.window.git_thread),
            ("pandoc_thread", self.window.pandoc_thread),
            ("preview_thread", self.window.preview_thread),
        ]

        for name, thread in threads:
            if thread and thread.isRunning():
                logger.debug(f"Stopping {name}...")
                thread.quit()
                if not thread.wait(1000):
                    logger.warning(f"{name} did not stop within timeout")
                else:
                    logger.debug(f"{name} stopped successfully")

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            # Cleanup export manager temp dir
            if hasattr(self.window, "export_manager"):
                self.window.export_manager.cleanup()

            # Legacy temp dir cleanup (for backward compatibility)
            if hasattr(self.window, "_temp_dir"):
                self.window._temp_dir.cleanup()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
