"""
Main window slot handlers.

MA Principle: Extracted from main_window.py to reduce file size.
Contains all @Slot decorated handlers and event methods.
"""

from __future__ import annotations

import html
import io
import logging
import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot

from asciidoc_artisan.core import APP_NAME, DEFAULT_FILENAME, GitResult, atomic_save_text

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class MainWindowSlotsMixin:
    """Mixin providing slot handlers for AsciiDocEditor."""

    @Slot()
    def open_file(self: AsciiDocEditor) -> None:
        """Open a file (delegates to FileOperationsManager)."""
        self.file_operations_manager.open_file()

    @Slot()
    def save_file(self: AsciiDocEditor, save_as: bool = False) -> bool:
        """Save file (delegates to FileOperationsManager)."""
        return self.file_operations_manager.save_file(save_as)

    @Slot(int, str)
    def _on_file_load_progress(self: AsciiDocEditor, percentage: int, message: str) -> None:
        """Handle file loading progress (delegates to DialogManager)."""
        self.dialog_manager.on_file_load_progress(percentage, message)

    @Slot()
    def update_preview(self: AsciiDocEditor) -> None:
        """Request preview rendering (delegates to PreviewHandler)."""
        self.preview_handler.update_preview()

    @Slot(str)
    def _handle_preview_complete(self: AsciiDocEditor, html_body: str) -> None:
        """Handle successful preview rendering (delegates to PreviewHandler)."""
        self.preview_handler.handle_preview_complete(html_body)

    @Slot(str)
    def _handle_preview_error(self: AsciiDocEditor, error_html: str) -> None:
        """Handle preview rendering error (delegates to PreviewHandler)."""
        self.preview_handler.handle_preview_error(error_html)

    @Slot(GitResult)
    def _handle_git_result(self: AsciiDocEditor, result: GitResult) -> None:
        """Handle Git result (delegates to GitHandler)."""
        self.git_handler.handle_git_result(result)

    @Slot(object)
    def _handle_git_status(self: AsciiDocEditor, status: Any) -> None:
        """Handle Git status update (delegates to StatusManager)."""
        from asciidoc_artisan.core import GitStatus

        if isinstance(status, GitStatus):
            self.status_manager.update_git_status(status)

    @Slot(dict)
    def _handle_detailed_git_status(self: AsciiDocEditor, status_data: dict[str, Any]) -> None:
        """Handle detailed Git status update (populates dialog)."""
        if hasattr(self, "_git_status_dialog") and self._git_status_dialog.isVisible():
            branch = status_data.get("branch", "unknown")
            modified = status_data.get("modified", [])
            staged = status_data.get("staged", [])
            untracked = status_data.get("untracked", [])
            self._git_status_dialog.populate_status(branch, modified, staged, untracked)

    @Slot(object)
    def _handle_github_result(self: AsciiDocEditor, result: Any) -> None:
        """Handle GitHub result (delegates to GitHubHandler)."""
        from asciidoc_artisan.core import GitHubResult

        if isinstance(result, GitHubResult):
            self.github_handler.handle_github_result(result)

    @Slot(str)
    def _handle_quick_commit(self: AsciiDocEditor, message: str) -> None:
        """Handle quick commit request."""
        if not self._ensure_git_ready():
            return
        logger.info(f"Quick commit requested: '{message[:50]}...'")
        self.git_handler.quick_commit(message)

    @Slot(str, str)
    def _handle_pandoc_result(self: AsciiDocEditor, result: str, context: str) -> None:
        """Handle Pandoc conversion result (delegates to PandocResultHandler)."""
        self.pandoc_result_handler.handle_pandoc_result(result, context)

    @Slot(str, str)
    def _handle_pandoc_error_result(self: AsciiDocEditor, error: str, context: str) -> None:
        """Handle Pandoc conversion error (delegates to PandocResultHandler)."""
        self.pandoc_result_handler.handle_pandoc_error_result(error, context)

    def _start_preview_timer(self: AsciiDocEditor) -> None:
        """Start preview update timer with adaptive debouncing."""
        if self._is_opening_file:
            return
        self._unsaved_changes = True
        self.status_manager.update_window_title()
        self.status_manager.update_document_metrics()

        text = self.editor.toPlainText()
        debounce_ms = self.resource_monitor.calculate_debounce_interval(text)

        if self._preview_timer.interval() != debounce_ms:
            self._preview_timer.setInterval(debounce_ms)
            logger.debug(f"Adaptive debounce: {debounce_ms}ms for {len(text)} chars")

        self._preview_timer.start()

    def _update_window_title(self: AsciiDocEditor) -> None:
        """Update window title based on current state."""
        title = APP_NAME
        if self._current_file_path:
            title = f"{APP_NAME} - {self._current_file_path.name}"
        else:
            title = f"{APP_NAME} - {DEFAULT_FILENAME}"

        if self._unsaved_changes:
            title += "*"

        self.setWindowTitle(title)

    def _auto_save(self: AsciiDocEditor) -> None:
        """Auto-save current file if there are unsaved changes."""
        if self._current_file_path and self._unsaved_changes:
            content = self.editor.toPlainText()
            if atomic_save_text(self._current_file_path, content, encoding="utf-8"):
                self.status_bar.showMessage("Auto-saved", 2000)
                logger.info(f"Auto-saved: {self._current_file_path}")
            else:
                logger.error(f"Auto-save failed: {self._current_file_path}")

    def _convert_asciidoc_to_html_body(self: AsciiDocEditor, source_text: str) -> str:
        """Convert AsciiDoc to HTML (for export operations)."""
        if self._asciidoc_api is None:
            return f"<pre>{html.escape(source_text)}</pre>"

        try:
            infile = io.StringIO(source_text)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()
        except Exception as exc:
            logger.error(f"AsciiDoc rendering failed: {exc}")
            return f"<div style='color:red'>Render Error: {html.escape(str(exc))}</div>"

    def _refresh_from_settings(self: AsciiDocEditor) -> None:
        """Refresh application state from updated settings."""
        from PySide6.QtGui import QFont

        from asciidoc_artisan.core import EDITOR_FONT_FAMILY

        settings = self._settings
        self.theme_manager.apply_theme()

        font = QFont(EDITOR_FONT_FAMILY, settings.font_size)
        self.editor.setFont(font)

        self._update_ai_status_bar()
        self._update_ai_backend_checkmarks()

        if hasattr(self, "pandoc_worker"):
            self.pandoc_worker.set_ollama_config(settings.ollama_enabled, settings.ollama_model)

        if hasattr(self, "chat_manager"):
            self.chat_manager.update_settings(settings)

        if not settings.maximized and settings.window_geometry:
            geom = settings.window_geometry
            self.setGeometry(geom["x"], geom["y"], geom["width"], geom["height"])

        if settings.splitter_sizes and hasattr(self, "splitter"):
            self.splitter.setSizes(settings.splitter_sizes)

        if hasattr(self, "dialog_manager"):
            self.dialog_manager._apply_font_settings()

        logger.info("Application refreshed from updated settings")

    def closeEvent(self: AsciiDocEditor, event: Any) -> None:  # noqa: N802
        """Handle window close event."""
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logger.info("Test mode: Shutting down worker threads...")
            if hasattr(self, "worker_manager") and self.worker_manager:
                self.worker_manager.shutdown()
            event.accept()
            return

        self.editor_state.handle_close_event(event)
