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
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QPushButton, QSplitter, QStatusBar

from asciidoc_artisan.core import MIN_FONT_SIZE

if TYPE_CHECKING:  # pragma: no cover
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
        self.maximized_pane: str | None = None
        self.saved_splitter_sizes: list[int] | None = None

        # Sync scrolling state (shared with main window)
        self.sync_scrolling = True

    def zoom(self, delta: int) -> None:
        """Zoom editor and preview by delta points."""
        font = self.editor.font()
        new_size = max(MIN_FONT_SIZE, font.pointSize() + delta)
        font.setPointSize(new_size)
        self.editor.setFont(font)

        # Preview zoom only works with GPU-accelerated QWebEngineView
        if hasattr(self.preview, "zoomFactor") and hasattr(self.preview, "setZoomFactor"):
            current_zoom = self.preview.zoomFactor()
            zoom_delta = 0.1 * delta
            new_zoom = max(0.25, min(5.0, current_zoom + zoom_delta))
            self.preview.setZoomFactor(new_zoom)
            logger.debug(f"Zoom changed: {delta}, new size: {new_size}, preview zoom: {new_zoom:.2f}")
        else:
            logger.debug(f"Zoom changed: {delta}, new size: {new_size} (preview zoom not supported)")

    def toggle_dark_mode(self) -> None:
        """Toggle dark mode and sync View menu checkbox."""
        dark_mode = not self._settings.dark_mode

        # Block signals to prevent recursive calls
        self.action_manager.dark_mode_act.blockSignals(True)
        self.action_manager.dark_mode_act.setChecked(dark_mode)
        self.action_manager.dark_mode_act.blockSignals(False)

        self._settings.dark_mode = dark_mode
        self.theme_manager.apply_theme()

        if hasattr(self.window, "preview_handler"):
            self.window.preview_handler.clear_css_cache()

        self.window.update_preview()
        logger.info(f"Dark mode: {self._settings.dark_mode}")

    def toggle_sync_scrolling(self) -> None:
        """Toggle synchronized scrolling between editor and preview."""
        self.sync_scrolling = self.action_manager.sync_scrolling_act.isChecked()
        self.window._sync_scrolling = self.sync_scrolling
        self.status_bar.showMessage(
            f"Synchronized scrolling {'enabled' if self.sync_scrolling else 'disabled'}",
            5000,
        )
        logger.info(f"Sync scrolling: {self.sync_scrolling}")

    def toggle_pane_maximize(self, pane: str) -> None:
        """Toggle maximize/restore for editor or preview pane."""
        if self.maximized_pane == pane:
            self.restore_panes()
        else:
            self.maximize_pane(pane)

    def maximize_pane(self, pane: str) -> None:
        """Maximize editor or preview pane."""
        if self.maximized_pane is None:
            self.saved_splitter_sizes = self.splitter.sizes()

        has_chat, chat_visible = self._detect_chat_state()

        if pane == "editor":
            self._maximize_editor(has_chat, chat_visible)
        else:
            self._maximize_preview(has_chat, chat_visible)

        self.maximized_pane = pane
        logger.debug(f"Pane maximized: {pane}, chat_visible={chat_visible}")

    def _detect_chat_state(self) -> tuple[bool, bool]:
        """Return (has_chat, chat_visible) tuple."""
        has_chat = len(self.splitter.sizes()) == 3
        chat_visible = has_chat and hasattr(self.window, "chat_container") and self.window.chat_container.isVisible()
        return has_chat, chat_visible

    def _maximize_editor(self, has_chat: bool, chat_visible: bool) -> None:
        """Maximize editor pane and update buttons."""
        if has_chat:
            if chat_visible:
                chat_size = self.saved_splitter_sizes[2] if self.saved_splitter_sizes else 200
                self.splitter.setSizes([self.splitter.width() - chat_size, 0, chat_size])
            else:
                self.splitter.setSizes([self.splitter.width(), 0, 0])
        else:
            self.splitter.setSizes([self.splitter.width(), 0])

        self.editor_max_btn.setText("⬛")
        self.editor_max_btn.setToolTip("Restore editor")
        self.preview_max_btn.setEnabled(True)
        self.preview_max_btn.setText("⬜")
        self.preview_max_btn.setToolTip("Maximize preview")
        self.status_bar.showMessage("Editor maximized", 3000)

    def _maximize_preview(self, has_chat: bool, chat_visible: bool) -> None:
        """Maximize preview pane and update buttons."""
        if has_chat:
            if chat_visible:
                chat_size = self.saved_splitter_sizes[2] if self.saved_splitter_sizes else 200
                self.splitter.setSizes([0, self.splitter.width() - chat_size, chat_size])
            else:
                self.splitter.setSizes([0, self.splitter.width(), 0])
        else:
            self.splitter.setSizes([0, self.splitter.width()])

        self.preview_max_btn.setText("⬛")
        self.preview_max_btn.setToolTip("Restore preview")
        self.editor_max_btn.setEnabled(True)
        self.editor_max_btn.setText("⬜")
        self.editor_max_btn.setToolTip("Maximize editor")
        self.status_bar.showMessage("Preview maximized", 3000)

    def restore_panes(self) -> None:
        """Restore panes to their previous sizes."""
        has_chat, chat_visible = self._detect_chat_state()

        if self.saved_splitter_sizes:
            if len(self.saved_splitter_sizes) == 3:
                self._restore_from_three_pane_sizes(has_chat, chat_visible)
            elif len(self.saved_splitter_sizes) == 2:
                self._restore_from_two_pane_sizes(has_chat, chat_visible)
            else:
                self._apply_default_sizes(has_chat, chat_visible)
        else:
            self._apply_default_sizes(has_chat, chat_visible)

        self._reset_maximize_buttons()
        self.maximized_pane = None
        self.status_bar.showMessage("View restored", 3000)
        logger.debug(f"Panes restored, chat_visible={chat_visible}")

    def _restore_from_three_pane_sizes(self, has_chat: bool, chat_visible: bool) -> None:
        """Restore from saved three-pane layout."""
        assert self.saved_splitter_sizes is not None
        total = sum(self.saved_splitter_sizes)
        if total > 0:
            self.splitter.setSizes(self.saved_splitter_sizes)
        else:
            width = self.splitter.width()
            if chat_visible:
                self.splitter.setSizes([int(width * 0.4), int(width * 0.4), int(width * 0.2)])
            else:  # pragma: no cover
                self.splitter.setSizes([width // 2, width // 2, 0])

    def _restore_from_two_pane_sizes(self, has_chat: bool, chat_visible: bool) -> None:
        """Restore from saved two-pane layout to current layout."""
        assert self.saved_splitter_sizes is not None
        total = sum(self.saved_splitter_sizes)
        if total > 0 and has_chat:
            if chat_visible:
                width = self.splitter.width()
                chat_size = int(width * 0.2)
                remaining = width - chat_size
                editor_size = int(remaining * 0.5)
                preview_size = remaining - editor_size
                self.splitter.setSizes([editor_size, preview_size, chat_size])
            else:  # pragma: no cover
                self.splitter.setSizes([self.saved_splitter_sizes[0], self.saved_splitter_sizes[1], 0])
        elif total > 0:
            self.splitter.setSizes(self.saved_splitter_sizes)
        else:  # pragma: no cover
            self._apply_default_sizes(has_chat, chat_visible)

    def _reset_maximize_buttons(self) -> None:
        """Reset maximize button states to normal."""
        self.editor_max_btn.setText("⬜")
        self.editor_max_btn.setToolTip("Maximize editor")
        self.editor_max_btn.setEnabled(True)
        self.preview_max_btn.setText("⬜")
        self.preview_max_btn.setToolTip("Maximize preview")
        self.preview_max_btn.setEnabled(True)

    def _apply_default_sizes(self, has_chat: bool, chat_visible: bool) -> None:
        """Apply default splitter sizes based on layout."""
        width = self.splitter.width()
        if has_chat:
            if chat_visible:
                self.splitter.setSizes([int(width * 0.4), int(width * 0.4), int(width * 0.2)])
            else:
                self.splitter.setSizes([width // 2, width // 2, 0])
        else:
            self.splitter.setSizes([width // 2, width // 2])

    def handle_close_event(self, event: Any) -> None:
        """Handle window close event with save prompt and cleanup."""
        if not self.window.status_manager.prompt_save_before_action("closing"):
            event.ignore()
            return

        self.window._settings_manager.save_settings_immediate(
            self._settings, self.window, self.window._current_file_path
        )

        logger.info("Shutting down worker threads...")
        self._shutdown_threads()
        self._cleanup_temp_files()

        event.accept()
        logger.info("Application closed")

    def _shutdown_threads(self) -> None:
        """Safely shut down worker threads via WorkerManager."""
        if hasattr(self.window, "worker_manager") and self.window.worker_manager:
            self.window.worker_manager.shutdown()
        else:
            logger.warning("WorkerManager not found, using fallback shutdown")
            self._shutdown_threads_fallback()

    def _shutdown_threads_fallback(self) -> None:
        """Fallback shutdown for legacy compatibility."""
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
            if hasattr(self.window, "export_manager"):
                self.window.export_manager.cleanup()
            if hasattr(self.window, "_temp_dir"):
                self.window._temp_dir.cleanup()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
