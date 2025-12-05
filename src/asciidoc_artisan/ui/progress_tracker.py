"""
Progress Tracker - Multi-stage progress display with cancel support.

Provides:
- Multi-stage progress tracking
- Cancel button for long operations
- Status messages with stage info
- Estimated time remaining
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor


class ProgressDialog(QDialog):
    """Dialog for displaying multi-stage progress."""

    cancelled = Signal()

    def __init__(
        self,
        title: str,
        stages: list[str],
        parent: QWidget | None = None,
        cancellable: bool = True,
    ) -> None:
        """Initialize progress dialog."""
        super().__init__(parent)
        self.stages = stages
        self.current_stage = 0
        self._cancellable = cancellable
        self._cancelled = False
        self._setup_ui(title)

    def _setup_ui(self, title: str) -> None:
        """Set up dialog UI."""
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel(f"<b>{title}</b>")
        layout.addWidget(self.title_label)

        # Stage label
        self.stage_label = QLabel(self.stages[0] if self.stages else "Processing...")
        self.stage_label.setStyleSheet("color: #666;")
        layout.addWidget(self.stage_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Detail label
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(self.detail_label)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if self._cancellable:
            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.clicked.connect(self._on_cancel)
            btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self._cancelled = True
        self.stage_label.setText("Cancelling...")
        self.cancel_btn.setEnabled(False)
        self.cancelled.emit()

    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled

    def set_stage(self, stage: int, detail: str = "") -> None:
        """Set current stage."""
        if 0 <= stage < len(self.stages):
            self.current_stage = stage
            self.stage_label.setText(self.stages[stage])

            # Calculate progress based on stages
            stage_progress = int((stage / len(self.stages)) * 100)
            self.progress_bar.setValue(stage_progress)

        if detail:
            self.detail_label.setText(detail)

    def set_progress(self, value: int, detail: str = "") -> None:
        """Set progress value (0-100)."""
        self.progress_bar.setValue(min(100, max(0, value)))
        if detail:
            self.detail_label.setText(detail)

    def complete(self) -> None:
        """Mark progress as complete."""
        self.progress_bar.setValue(100)
        self.stage_label.setText("Complete!")
        QTimer.singleShot(500, self.accept)


class ProgressTracker(QObject):
    """
    Manages progress tracking for long operations.

    Features:
    - Multi-stage progress display
    - Cancel support
    - Inline status bar progress
    - Dialog for longer operations
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize progress tracker."""
        super().__init__(editor)
        self.editor = editor
        self._active_dialog: ProgressDialog | None = None

    def start_operation(
        self,
        title: str,
        stages: list[str],
        cancellable: bool = True,
        use_dialog: bool = True,
    ) -> ProgressDialog | None:
        """
        Start tracking a multi-stage operation.

        Args:
            title: Operation title
            stages: List of stage names
            cancellable: Whether operation can be cancelled
            use_dialog: Whether to show a dialog (vs inline)

        Returns:
            ProgressDialog if use_dialog=True, else None
        """
        if use_dialog:
            self._active_dialog = ProgressDialog(title, stages, self.editor, cancellable)
            self._active_dialog.show()
            return self._active_dialog
        else:
            # Use status bar for inline progress
            self.editor.status_bar.showMessage(f"{title}: {stages[0]}")
            return None

    def update_progress(self, value: int, detail: str = "") -> None:
        """Update progress value."""
        if self._active_dialog:
            self._active_dialog.set_progress(value, detail)
        else:
            # Update status bar
            msg = f"Progress: {value}%"
            if detail:
                msg += f" - {detail}"
            self.editor.status_bar.showMessage(msg)

    def update_stage(self, stage: int, detail: str = "") -> None:
        """Update current stage."""
        if self._active_dialog:
            self._active_dialog.set_stage(stage, detail)

    def complete(self, message: str = "Complete") -> None:
        """Mark operation as complete."""
        if self._active_dialog:
            self._active_dialog.complete()
            self._active_dialog = None
        else:
            self.editor.status_bar.showMessage(message, 3000)

    def cancel(self) -> None:
        """Cancel current operation."""
        if self._active_dialog:
            self._active_dialog.reject()
            self._active_dialog = None

    def is_cancelled(self) -> bool:
        """Check if current operation is cancelled."""
        if self._active_dialog:
            return self._active_dialog.is_cancelled()
        return False


# Predefined operation configurations
OPERATION_STAGES = {
    "export_pdf": ["Preparing document", "Converting to HTML", "Generating PDF", "Finalizing"],
    "export_docx": ["Preparing document", "Converting format", "Writing file"],
    "git_push": ["Checking status", "Pushing to remote", "Verifying"],
    "git_pull": ["Fetching changes", "Merging", "Updating workspace"],
    "import_file": ["Reading file", "Converting to AsciiDoc", "Loading into editor"],
    "ai_request": ["Preparing context", "Sending request", "Processing response"],
}
