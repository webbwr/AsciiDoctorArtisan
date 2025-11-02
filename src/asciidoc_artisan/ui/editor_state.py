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
        # Get current font and adjust size.
        font = self.editor.font()
        # Prevent font from getting too small.
        new_size = max(MIN_FONT_SIZE, font.pointSize() + delta)
        font.setPointSize(new_size)
        self.editor.setFont(font)

        # Preview zoom only works with GPU widget.
        if hasattr(self.preview, "zoomFactor") and hasattr(
            self.preview, "setZoomFactor"
        ):
            current_zoom = self.preview.zoomFactor()
            # Scale delta to zoom factor range.
            zoom_delta = 0.1 * delta
            # Clamp zoom between 25% and 500%.
            new_zoom = max(0.25, min(5.0, current_zoom + zoom_delta))
            self.preview.setZoomFactor(new_zoom)
            logger.debug(
                f"Zoom changed: {delta}, new size: {new_size}, preview zoom: {new_zoom:.2f}"
            )
        else:
            # Software renderer cannot zoom.
            logger.debug(
                f"Zoom changed: {delta}, new size: {new_size} (preview zoom not supported)"
            )

    def toggle_dark_mode(self) -> None:
        """Toggle dark mode on/off - syncs View menu checkbox."""
        # Simply flip the current dark mode state
        dark_mode = not self._settings.dark_mode

        # Update View menu checkbox (dark_mode_act is still checkable)
        # Block signals to prevent recursive calls
        self.action_manager.dark_mode_act.blockSignals(True)
        self.action_manager.dark_mode_act.setChecked(dark_mode)
        self.action_manager.dark_mode_act.blockSignals(False)

        # Apply the theme
        self._settings.dark_mode = dark_mode
        self.theme_manager.apply_theme()

        # Clear CSS cache so preview regenerates with new theme colors
        if hasattr(self.window, "preview_handler"):
            self.window.preview_handler.clear_css_cache()

        self.window.update_preview()
        logger.info(f"Dark mode: {self._settings.dark_mode}")

    def toggle_sync_scrolling(self) -> None:
        """Toggle synchronized scrolling between editor and preview."""
        # Get state from menu action checkbox.
        self.sync_scrolling = self.action_manager.sync_scrolling_act.isChecked()
        # Keep main window in sync with this state.
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
            # Same pane clicked again means restore.
            self.restore_panes()
        elif self.maximized_pane is not None:
            # Different pane already maximized so switch to this one.
            self.maximize_pane(pane)
        else:
            # No pane maximized yet so maximize this one.
            self.maximize_pane(pane)

    def maximize_pane(self, pane: str) -> None:
        """
        Maximize a specific pane.

        Args:
            pane: Pane to maximize ("editor" or "preview")
        """
        # Save sizes so we can restore later.
        if self.maximized_pane is None:
            self.saved_splitter_sizes = self.splitter.sizes()

        # Detect if chat pane is part of the layout.
        has_chat = len(self.splitter.sizes()) == 3
        # Check if chat is both present and visible.
        chat_visible = (
            has_chat
            and hasattr(self.window, "chat_container")
            and self.window.chat_container.isVisible()
        )

        if pane == "editor":
            # Maximize editor and hide preview.
            if has_chat:
                if chat_visible:
                    # Preserve chat size from saved state.
                    chat_size = (
                        self.saved_splitter_sizes[2]
                        if self.saved_splitter_sizes
                        else 200
                    )
                    # Give all space to editor except chat.
                    self.splitter.setSizes(
                        [self.splitter.width() - chat_size, 0, chat_size]
                    )
                else:
                    # Chat exists but hidden so collapse both preview and chat.
                    self.splitter.setSizes([self.splitter.width(), 0, 0])
            else:
                # Two pane layout so just hide preview.
                self.splitter.setSizes([self.splitter.width(), 0])

            # Update button to show restore icon.
            self.editor_max_btn.setText("⬛")
            self.editor_max_btn.setToolTip("Restore editor")

            # Allow preview maximize button to work.
            self.preview_max_btn.setEnabled(True)
            self.preview_max_btn.setText("⬜")
            self.preview_max_btn.setToolTip("Maximize preview")
            self.status_bar.showMessage("Editor maximized", 3000)
        else:
            # Maximize preview and hide editor.
            if has_chat:
                if chat_visible:
                    # Preserve chat size from saved state.
                    chat_size = (
                        self.saved_splitter_sizes[2]
                        if self.saved_splitter_sizes
                        else 200
                    )
                    # Give all space to preview except chat.
                    self.splitter.setSizes(
                        [0, self.splitter.width() - chat_size, chat_size]
                    )
                else:
                    # Chat exists but hidden so collapse both editor and chat.
                    self.splitter.setSizes([0, self.splitter.width(), 0])
            else:
                # Two pane layout so just hide editor.
                self.splitter.setSizes([0, self.splitter.width()])

            # Update button to show restore icon.
            self.preview_max_btn.setText("⬛")
            self.preview_max_btn.setToolTip("Restore preview")

            # Allow editor maximize button to work.
            self.editor_max_btn.setEnabled(True)
            self.editor_max_btn.setText("⬜")
            self.editor_max_btn.setToolTip("Maximize editor")
            self.status_bar.showMessage("Preview maximized", 3000)

        self.maximized_pane = pane
        logger.debug(f"Pane maximized: {pane}, chat_visible={chat_visible}")

    def restore_panes(self) -> None:
        """Restore panes to their previous sizes, preserving chat visibility."""
        # Detect current layout configuration.
        has_chat = len(self.splitter.sizes()) == 3
        chat_visible = (
            has_chat
            and hasattr(self.window, "chat_container")
            and self.window.chat_container.isVisible()
        )

        if self.saved_splitter_sizes:
            # Try to restore to sizes before maximize.
            if len(self.saved_splitter_sizes) == 3:
                # Three pane layout was saved.
                total = sum(self.saved_splitter_sizes)
                if total > 0:
                    # Sizes are valid so restore them.
                    self.splitter.setSizes(self.saved_splitter_sizes)
                else:
                    # Saved sizes are invalid so use defaults.
                    width = self.splitter.width()
                    if chat_visible:
                        # Split: 40% editor, 40% preview, 20% chat.
                        self.splitter.setSizes(
                            [int(width * 0.4), int(width * 0.4), int(width * 0.2)]
                        )
                    else:
                        # Chat hidden so split 50/50 editor and preview.
                        self.splitter.setSizes([width // 2, width // 2, 0])
            elif len(self.saved_splitter_sizes) == 2:
                # Two pane layout was saved but now we have three.
                total = sum(self.saved_splitter_sizes)
                if total > 0 and has_chat:
                    # Need to add chat pane to saved sizes.
                    if chat_visible:
                        width = self.splitter.width()
                        # Reserve 20% for chat.
                        chat_size = int(width * 0.2)
                        remaining = width - chat_size
                        # Split remaining 50/50 for editor and preview.
                        editor_size = int(remaining * 0.5)
                        preview_size = remaining - editor_size
                        self.splitter.setSizes([editor_size, preview_size, chat_size])
                    else:
                        # Chat hidden so just add zero for third pane.
                        self.splitter.setSizes(
                            [
                                self.saved_splitter_sizes[0],
                                self.saved_splitter_sizes[1],
                                0,
                            ]
                        )
                elif total > 0:
                    # No chat pane so restore two pane sizes.
                    self.splitter.setSizes(self.saved_splitter_sizes)
                else:
                    # Saved sizes invalid so use defaults.
                    self._apply_default_sizes(has_chat, chat_visible)
            else:
                # Saved sizes have wrong number of items.
                self._apply_default_sizes(has_chat, chat_visible)
        else:
            # Nothing saved so use defaults.
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
                # Three pane: 40% editor, 40% preview, 20% chat.
                self.splitter.setSizes(
                    [int(width * 0.4), int(width * 0.4), int(width * 0.2)]
                )
            else:
                # Three pane but chat hidden: 50/50 with zero for chat.
                self.splitter.setSizes([width // 2, width // 2, 0])
        else:
            # Two pane: 50/50 split.
            self.splitter.setSizes([width // 2, width // 2])

    def handle_close_event(self, event: Any) -> None:
        """
        Handle window close event.

        Args:
            event: Close event from Qt
        """
        # Ask user to save if there are unsaved changes.
        if not self.window.status_manager.prompt_save_before_action("closing"):
            # User cancelled so stop closing.
            event.ignore()
            return

        # Save settings now before threads shut down.
        self.window._settings_manager.save_settings_immediate(
            self._settings, self.window, self.window._current_file_path
        )

        # Stop all background threads.
        logger.info("Shutting down worker threads...")
        self._shutdown_threads()

        # Delete temporary files.
        self._cleanup_temp_files()

        # Allow window to close.
        event.accept()
        logger.info("Application closed")

    def _shutdown_threads(self) -> None:
        """Safely shut down worker threads."""
        # List of threads to stop.
        threads = [
            ("git_thread", self.window.git_thread),
            ("pandoc_thread", self.window.pandoc_thread),
            ("preview_thread", self.window.preview_thread),
        ]

        for name, thread in threads:
            if thread and thread.isRunning():
                logger.debug(f"Stopping {name}...")
                # Ask thread to stop.
                thread.quit()
                # Wait up to 1 second for clean shutdown.
                if not thread.wait(1000):
                    # Thread is stuck or busy.
                    logger.warning(f"{name} did not stop within timeout")
                else:
                    logger.debug(f"{name} stopped successfully")

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            # Delete export temp files.
            if hasattr(self.window, "export_manager"):
                self.window.export_manager.cleanup()

            # Delete old temp dir for backward compatibility.
            if hasattr(self.window, "_temp_dir"):
                self.window._temp_dir.cleanup()
        except Exception as e:
            # Log but do not crash on cleanup failure.
            logger.warning(f"Failed to cleanup temp files: {e}")
