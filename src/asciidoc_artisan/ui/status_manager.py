"""
Status Manager - Handles status bar and UI feedback for AsciiDoc Artisan.

Implements:
- FR-045: Status bar with contextual messages
- FR-051: Window title (filename with unsaved indicator)
- Document metrics: version, word count, grade level
- AI status indicator

This module manages status messages, window titles, and user notifications,
extracted from main_window.py as part of Phase 2 architectural refactoring.

The StatusManager provides centralized UI feedback management.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QPushButton

from asciidoc_artisan.core import APP_NAME, DEFAULT_FILENAME, GitStatus
from asciidoc_artisan.ui.document_metrics_calculator import DocumentMetricsCalculator
from asciidoc_artisan.ui.git_status_formatter import GitStatusFormatter
from asciidoc_artisan.ui.status_bar_label_updater import StatusBarLabelUpdater
from asciidoc_artisan.ui.status_bar_widget_factory import StatusBarWidgetFactory
from asciidoc_artisan.ui.user_message_handler import UserMessageHandler

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor


class StatusManager:
    """Manages status display and UI feedback for AsciiDoc Artisan.

    This class encapsulates all status bar, window title, and message dialog
    functionality, plus document metrics display.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the StatusManager with a reference to the main editor."""
        self.editor = editor

        # Widgets will be created later when status bar is ready
        self.version_label: QLabel | None = None
        self.word_count_label: QLabel | None = None
        self.grade_level_label: QLabel | None = None
        self.git_status_label: QLabel | None = None
        self.ai_status_label: QLabel | None = None
        self.cancel_button: QPushButton | None = None

        # Track current operation for cancellation
        self._current_operation: str | None = None  # 'git', 'pandoc', or 'preview'

        # Git status color tracking for theme changes
        self._current_git_color: str | None = None
        self._current_git_text: str | None = None

        # Debounced metrics update timer (MA principle: reduce CPU during rapid typing)
        self._metrics_timer: QTimer | None = None
        self._metrics_debounce_ms = 200  # 200ms debounce delay

    @property
    def _metrics_calculator(self) -> DocumentMetricsCalculator:
        """
        Lazy-initialized document metrics calculator.

        MA principle: Delegates metrics calculation to DocumentMetricsCalculator (extracted class).
        """
        if not hasattr(self, "_calculator_instance"):
            self._calculator_instance = DocumentMetricsCalculator()
        return self._calculator_instance

    @property
    def _git_formatter(self) -> GitStatusFormatter:
        """
        Lazy-initialized Git status formatter.

        MA principle: Delegates Git formatting to GitStatusFormatter (extracted class).
        """
        if not hasattr(self, "_formatter_instance"):
            self._formatter_instance = GitStatusFormatter()
        return self._formatter_instance

    @property
    def _widget_factory(self) -> StatusBarWidgetFactory:
        """
        Lazy-initialized status bar widget factory.

        MA principle: Delegates widget creation to StatusBarWidgetFactory (extracted class).
        """
        if not hasattr(self, "_factory_instance"):
            self._factory_instance = StatusBarWidgetFactory(self)
        return self._factory_instance

    @property
    def _label_updater(self) -> StatusBarLabelUpdater:
        """
        Lazy-initialized status bar label updater.

        MA principle: Delegates label updates to StatusBarLabelUpdater (extracted class).
        """
        if not hasattr(self, "_updater_instance"):
            self._updater_instance = StatusBarLabelUpdater(self)
        return self._updater_instance

    @property
    def _message_handler(self) -> UserMessageHandler:
        """
        Lazy-initialized user message handler.

        MA principle: Delegates message/dialog handling to UserMessageHandler (extracted class).
        """
        if not hasattr(self, "_handler_instance"):
            self._handler_instance = UserMessageHandler(self.editor)
        return self._handler_instance

    def initialize_widgets(self) -> None:
        """Initialize status bar widgets (delegates to widget_factory)."""
        self._widget_factory.initialize_widgets()

        # Initialize debounce timer for metrics updates
        self._metrics_timer = QTimer()
        self._metrics_timer.setSingleShot(True)
        self._metrics_timer.setInterval(self._metrics_debounce_ms)
        self._metrics_timer.timeout.connect(self._do_update_document_metrics)

    def update_window_title(self) -> None:
        """Update the window title based on current file and save status."""
        title = APP_NAME

        if self.editor._current_file_path:
            title = f"{APP_NAME} - {self.editor._current_file_path.name}"
        else:
            title = f"{APP_NAME} - {DEFAULT_FILENAME}"

        if self.editor._unsaved_changes:
            title += "*"

        self.editor.setWindowTitle(title)

    def show_message(self, level: str, title: str, text: str) -> None:
        """Show message dialog (delegates to message_handler)."""
        self._message_handler.show_message(level, title, text)

    def show_status(self, message: str, timeout: int = 0) -> None:
        """Show status bar message (delegates to message_handler)."""
        self._message_handler.show_status(message, timeout)

    def prompt_save_before_action(self, action: str) -> bool:
        """Prompt save before action (delegates to message_handler)."""
        return self._message_handler.prompt_save_before_action(action)

    def extract_document_version(self, text: str) -> str | None:
        """Extract document version (delegates to metrics_calculator)."""
        return self._metrics_calculator.extract_document_version(text)

    def count_words(self, text: str) -> int:
        """Count words (delegates to metrics_calculator)."""
        return self._metrics_calculator.count_words(text)

    def calculate_grade_level(self, text: str) -> float:
        """Calculate grade level (delegates to metrics_calculator)."""
        return self._metrics_calculator.calculate_grade_level(text)

    def _update_version_label(self, text: str) -> None:
        """Update version label (delegates to label_updater)."""
        self._label_updater.update_version_label(text)

    def _update_word_count_label(self, text: str, word_count: int) -> None:
        """Update word count label (delegates to label_updater)."""
        self._label_updater.update_word_count_label(text, word_count)

    def _interpret_grade_level(self, grade: float) -> tuple[str, str]:
        """Interpret grade level (delegates to metrics_calculator)."""
        return self._metrics_calculator.interpret_grade_level(grade)

    def _update_grade_level_label(self, text: str, word_count: int) -> None:
        """Update grade level label (delegates to label_updater)."""
        self._label_updater.update_grade_level_label(text, word_count)

    def update_document_metrics(self) -> None:
        """
        Schedule debounced document metrics update.

        MA principle: Debouncing reduces CPU usage during rapid typing.
        Metrics calculation is deferred by 200ms after last call.
        """
        if self._metrics_timer is not None:
            # Timer exists - restart it (debounce)
            if self._metrics_timer.isActive():
                self._metrics_timer.stop()
            self._metrics_timer.start()
        else:
            # Timer not initialized - update immediately (fallback)
            self._do_update_document_metrics()

    def _do_update_document_metrics(self) -> None:
        """
        Actually update all document metrics in status bar.

        Called by debounce timer after typing pause.
        MA principle: Reduced from 72→17 lines by extracting 4 helpers (76% reduction).
        """
        # Skip if widgets not yet initialized
        if not self.version_label:
            return

        text = self.editor.editor.toPlainText()
        word_count = self.count_words(text)

        # Update all metric labels
        self._update_version_label(text)
        self._update_word_count_label(text, word_count)
        self._update_grade_level_label(text, word_count)

    def set_ai_model(self, model_name: str | None = None) -> None:
        """Set AI model name in status bar.

        Args:
            model_name: Name of the active AI model, "Pandoc" for standard conversion, or None to clear
        """
        if model_name:
            if model_name == "Pandoc":
                # Show Pandoc as the conversion method
                self.ai_status_label.setText("Conversion: Pandoc")
                self.ai_status_label.setToolTip("Using Pandoc for document conversion")
            else:
                # Show Ollama model name
                self.ai_status_label.setText(f"AI: {model_name}")
                self.ai_status_label.setToolTip(f"Ollama model: {model_name}")
        else:
            self.ai_status_label.setText("")
            self.ai_status_label.setToolTip("")

    def set_ai_active(self, active: bool) -> None:
        """Deprecated: Use set_ai_model() instead.

        Args:
            active: True if AI is active, False otherwise
        """
        # This method is kept for backward compatibility but does nothing
        # Use set_ai_model() to set the model name instead
        pass

    def show_cancel_button(self, operation: str) -> None:
        """Show cancel button for the given operation.

        Args:
            operation: Type of operation ('git', 'pandoc', or 'preview')
        """
        self._current_operation = operation
        if self.cancel_button:
            self.cancel_button.show()

    def hide_cancel_button(self) -> None:
        """Hide cancel button when operation completes."""
        self._current_operation = None
        if self.cancel_button:
            self.cancel_button.hide()

    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        if not self._current_operation:
            return

        # Delegate cancellation to worker_manager
        if hasattr(self.editor, "worker_manager"):
            if self._current_operation == "git":
                self.editor.worker_manager.cancel_git_operation()
            elif self._current_operation == "pandoc":
                self.editor.worker_manager.cancel_pandoc_operation()
            elif self._current_operation == "preview":
                self.editor.worker_manager.cancel_preview_operation()

        # Hide button
        self.hide_cancel_button()

        # Show feedback
        self.editor.status_bar.showMessage(f"Cancelled {self._current_operation} operation", 3000)

    def _determine_git_display_state(self, status: GitStatus) -> tuple[str, str, str]:
        """Determine Git display state (delegates to git_formatter)."""
        return self._git_formatter.determine_git_display_state(status)

    def _build_git_tooltip(self, status: GitStatus, status_desc: str, total_changes: int) -> str:
        """Build Git tooltip (delegates to git_formatter)."""
        return self._git_formatter.build_git_tooltip(status, status_desc, total_changes)

    def update_git_status(self, status: GitStatus) -> None:
        """
        Update Git status display with brief format and color coding.

        MA principle: Reduced from 71→23 lines by extracting 2 helpers (68% reduction).

        Brief format:
        - Clean: "main ✓" (green)
        - Dirty: "main ●2" (yellow, showing total changes)
        - Conflicts: "main ⚠" (red)

        Args:
            status: GitStatus object with repository information
        """
        if not self.git_status_label:
            return

        # Determine display state
        text, color, status_desc = self._determine_git_display_state(status)
        total_changes = status.modified_count + status.staged_count + status.untracked_count

        # Store current state for theme restoration
        self._current_git_color = color
        self._current_git_text = text

        # Apply color and text
        self.git_status_label.setStyleSheet(f"color: {color};")
        self.git_status_label.setText(text)

        # Build and set tooltip
        tooltip = self._build_git_tooltip(status, status_desc, total_changes)
        self.git_status_label.setToolTip(tooltip)

        logger.debug(f"Git status updated: {text} ({color})")

    def restore_git_status_color(self) -> None:
        """
        Restore git status label color after theme changes.

        Theme changes can override inline stylesheets with global palette.
        This method re-applies the git status color from stored state.
        """
        if not self.git_status_label or not self._current_git_color or not self._current_git_text:
            return

        # Re-apply stored color and text
        self.git_status_label.setStyleSheet(f"color: {self._current_git_color};")
        self.git_status_label.setText(self._current_git_text)

        logger.debug(f"Git status color restored: {self._current_git_text} ({self._current_git_color})")
