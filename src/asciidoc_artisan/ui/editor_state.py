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

        # Update preview zoom factor (QWebEngineView only - QTextBrowser doesn't support zoom)
        if hasattr(self.preview, "zoomFactor") and hasattr(
            self.preview, "setZoomFactor"
        ):
            current_zoom = self.preview.zoomFactor()
            zoom_delta = 0.1 * delta  # Convert delta to zoom factor change
            new_zoom = max(0.25, min(5.0, current_zoom + zoom_delta))
            self.preview.setZoomFactor(new_zoom)
            logger.debug(
                f"Zoom changed: {delta}, new size: {new_size}, preview zoom: {new_zoom:.2f}"
            )
        else:
            # QTextBrowser fallback - only zoom editor
            logger.debug(
                f"Zoom changed: {delta}, new size: {new_size} (preview zoom not supported)"
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

        # Check if chat pane exists and is visible
        has_chat = len(self.splitter.sizes()) == 3
        chat_visible = (has_chat and hasattr(self.window, 'chat_container') and
                       self.window.chat_container.isVisible())

        if pane == "editor":
            # Maximize editor, hide preview, preserve chat visibility
            if has_chat:
                if chat_visible:
                    # Keep chat visible with its current/saved size
                    chat_size = self.saved_splitter_sizes[2] if self.saved_splitter_sizes else 200
                    self.splitter.setSizes([self.splitter.width() - chat_size, 0, chat_size])
                else:
                    # Chat hidden, only editor/preview matter
                    self.splitter.setSizes([self.splitter.width(), 0, 0])
            else:
                # Two pane layout (no chat)
                self.splitter.setSizes([self.splitter.width(), 0])

            self.editor_max_btn.setText("⬛")
            self.editor_max_btn.setToolTip("Restore editor")

            self.preview_max_btn.setEnabled(True)
            self.preview_max_btn.setText("⬜")
            self.preview_max_btn.setToolTip("Maximize preview")
            self.status_bar.showMessage("Editor maximized", 3000)
        else:
            # Maximize preview, hide editor, preserve chat visibility
            if has_chat:
                if chat_visible:
                    # Keep chat visible with its current/saved size
                    chat_size = self.saved_splitter_sizes[2] if self.saved_splitter_sizes else 200
                    self.splitter.setSizes([0, self.splitter.width() - chat_size, chat_size])
                else:
                    # Chat hidden, only editor/preview matter
                    self.splitter.setSizes([0, self.splitter.width(), 0])
            else:
                # Two pane layout (no chat)
                self.splitter.setSizes([0, self.splitter.width()])

            self.preview_max_btn.setText("⬛")
            self.preview_max_btn.setToolTip("Restore preview")

            self.editor_max_btn.setEnabled(True)
            self.editor_max_btn.setText("⬜")
            self.editor_max_btn.setToolTip("Maximize editor")
            self.status_bar.showMessage("Preview maximized", 3000)

        self.maximized_pane = pane
        logger.debug(f"Pane maximized: {pane}, chat_visible={chat_visible}")

    def restore_panes(self) -> None:
        """Restore panes to their previous sizes, preserving chat visibility."""
        has_chat = len(self.splitter.sizes()) == 3
        chat_visible = (has_chat and hasattr(self.window, 'chat_container') and
                       self.window.chat_container.isVisible())

        if self.saved_splitter_sizes:
            # Restore saved sizes
            if len(self.saved_splitter_sizes) == 3:
                # Three pane layout (editor, preview, chat)
                total = sum(self.saved_splitter_sizes)
                if total > 0:
                    self.splitter.setSizes(self.saved_splitter_sizes)
                else:
                    # Fallback proportional split
                    width = self.splitter.width()
                    if chat_visible:
                        # 2/5 editor, 2/5 preview, 1/5 chat
                        self.splitter.setSizes([int(width * 0.4), int(width * 0.4), int(width * 0.2)])
                    else:
                        # Chat hidden, 50/50 editor/preview
                        self.splitter.setSizes([width // 2, width // 2, 0])
            elif len(self.saved_splitter_sizes) == 2:
                # Two pane layout - need to adapt for three pane splitter
                total = sum(self.saved_splitter_sizes)
                if total > 0 and has_chat:
                    # Distribute saved sizes and add chat
                    if chat_visible:
                        width = self.splitter.width()
                        chat_size = int(width * 0.2)
                        remaining = width - chat_size
                        editor_size = int(remaining * 0.5)
                        preview_size = remaining - editor_size
                        self.splitter.setSizes([editor_size, preview_size, chat_size])
                    else:
                        # Chat hidden
                        self.splitter.setSizes([self.saved_splitter_sizes[0], self.saved_splitter_sizes[1], 0])
                elif total > 0:
                    # No chat pane, restore as-is
                    self.splitter.setSizes(self.saved_splitter_sizes)
                else:
                    # Fallback
                    self._apply_default_sizes(has_chat, chat_visible)
            else:
                # Invalid saved sizes, use defaults
                self._apply_default_sizes(has_chat, chat_visible)
        else:
            # No saved sizes, use defaults
            self._apply_default_sizes(has_chat, chat_visible)

        # Reset button states
        self.editor_max_btn.setText("⬜")
        self.editor_max_btn.setToolTip("Maximize editor")
        self.editor_max_btn.setEnabled(True)
        self.preview_max_btn.setText("⬜")
        self.preview_max_btn.setToolTip("Maximize preview")
        self.preview_max_btn.setEnabled(True)

        self.maximized_pane = None
        self.status_bar.showMessage("View restored", 3000)
        logger.debug(f"Panes restored, chat_visible={chat_visible}")

    def _apply_default_sizes(self, has_chat: bool, chat_visible: bool) -> None:
        """Apply default splitter sizes based on layout."""
        width = self.splitter.width()
        if has_chat:
            if chat_visible:
                # 2/5 editor, 2/5 preview, 1/5 chat
                self.splitter.setSizes([int(width * 0.4), int(width * 0.4), int(width * 0.2)])
            else:
                # Chat hidden, 50/50 editor/preview
                self.splitter.setSizes([width // 2, width // 2, 0])
        else:
            # Two pane only
            self.splitter.setSizes([width // 2, width // 2])

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

        # Save settings immediately (QA-12: must save before shutdown)
        self.window._settings_manager.save_settings_immediate(
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
