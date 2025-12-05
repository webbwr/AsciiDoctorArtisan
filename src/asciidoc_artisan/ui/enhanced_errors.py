"""
Enhanced Error Messages - User-friendly error handling with actions.

Provides:
- Detailed error messages with context
- Actionable buttons (Retry, Settings, Help)
- Automatic error recovery suggestions
"""

from typing import TYPE_CHECKING, Callable, TypedDict

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor


class ErrorTemplate(TypedDict):
    """Type definition for error templates."""

    title: str
    message: str
    details: str
    actions: list[tuple[str, str]]


# Error templates with actions
ERROR_TEMPLATES: dict[str, ErrorTemplate] = {
    "git_no_repo": {
        "title": "No Git Repository",
        "message": "No Git repository is configured for this project.",
        "details": "To use Git features, you need to set up a repository first.",
        "actions": [
            ("Set Repository", "select_repo"),
            ("Learn More", "help_git"),
        ],
    },
    "git_no_changes": {
        "title": "No Changes to Commit",
        "message": "There are no staged changes to commit.",
        "details": "Use 'Git → Status' to see modified files, then stage them before committing.",
        "actions": [
            ("View Status", "git_status"),
        ],
    },
    "git_conflict": {
        "title": "Merge Conflict",
        "message": "There are merge conflicts that need to be resolved.",
        "details": "Open the conflicting files and resolve the conflicts marked with <<<<<<< and >>>>>>>.",
        "actions": [
            ("View Status", "git_status"),
        ],
    },
    "pandoc_not_found": {
        "title": "Pandoc Not Installed",
        "message": "Pandoc is required for this operation but was not found.",
        "details": "Pandoc is needed for converting between document formats (Markdown, Word, PDF).",
        "actions": [
            ("Install Guide", "help_pandoc"),
            ("Check Installation", "check_pandoc"),
        ],
    },
    "ollama_not_running": {
        "title": "Ollama Not Available",
        "message": "Cannot connect to Ollama service at localhost:11434.",
        "details": "Make sure Ollama is installed and running. Start it with 'ollama serve' in terminal.",
        "actions": [
            ("Retry", "retry_ollama"),
            ("Settings", "ollama_settings"),
        ],
    },
    "file_not_found": {
        "title": "File Not Found",
        "message": "The requested file could not be found.",
        "details": "The file may have been moved, renamed, or deleted.",
        "actions": [
            ("Browse", "open_file"),
        ],
    },
    "permission_denied": {
        "title": "Permission Denied",
        "message": "Cannot write to this location.",
        "details": "You may not have permission to write to this folder. Try saving to a different location.",
        "actions": [
            ("Save As", "save_as"),
        ],
    },
    "export_failed": {
        "title": "Export Failed",
        "message": "Could not export the document.",
        "details": "Check that all required tools are installed and the output path is writable.",
        "actions": [
            ("Check Tools", "validate_install"),
            ("Try Again", "retry_export"),
        ],
    },
}


class EnhancedErrorDialog(QDialog):
    """Error dialog with actionable buttons."""

    def __init__(
        self,
        error_type: str,
        extra_details: str = "",
        parent: QWidget | None = None,
        action_handler: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize enhanced error dialog."""
        super().__init__(parent)
        self.action_handler = action_handler
        self._setup_ui(error_type, extra_details)

    def _setup_ui(self, error_type: str, extra_details: str) -> None:
        """Set up dialog UI."""
        default_template: ErrorTemplate = {
            "title": "Error",
            "message": "An error occurred.",
            "details": extra_details or "Please try again.",
            "actions": [],
        }
        template: ErrorTemplate = ERROR_TEMPLATES.get(error_type, default_template)

        self.setWindowTitle(template["title"])
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Icon and title
        title_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 32px;")
        title_layout.addWidget(icon_label)

        title_label = QLabel(f"<h3>{template['title']}</h3>")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Message
        msg_label = QLabel(template["message"])
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; margin: 10px 0;")
        layout.addWidget(msg_label)

        # Details
        details = template["details"]
        if extra_details:
            details += f"\n\nDetails: {extra_details}"

        details_browser = QTextBrowser()
        details_browser.setPlainText(details)
        details_browser.setMaximumHeight(100)
        layout.addWidget(details_browser)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        for action_text, action_id in template.get("actions", []):
            btn = QPushButton(action_text)
            btn.clicked.connect(lambda checked, aid=action_id: self._handle_action(aid))
            btn_layout.addWidget(btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _handle_action(self, action_id: str) -> None:
        """Handle action button click."""
        if self.action_handler:
            self.action_handler(action_id)
        self.accept()


class EnhancedErrorManager:
    """
    Manages enhanced error display and handling.

    Features:
    - User-friendly error messages
    - Actionable recovery options
    - Automatic context detection
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize error manager."""
        self.editor = editor

    def show_error(self, error_type: str, extra_details: str = "") -> None:
        """Show enhanced error dialog."""
        dialog = EnhancedErrorDialog(
            error_type,
            extra_details,
            self.editor,
            self._handle_action,
        )
        dialog.exec()

    def _handle_action(self, action_id: str) -> None:
        """Handle error dialog action."""
        action_map = {
            "select_repo": lambda: self.editor.git_handler.select_repository(),
            "git_status": lambda: self.editor._show_git_status(),
            "help_git": lambda: self.editor.contextual_help.show_help_for_widget(),
            "help_pandoc": lambda: self.editor.dialog_manager.show_pandoc_status(),
            "check_pandoc": lambda: self.editor.dialog_manager.show_pandoc_status(),
            "retry_ollama": lambda: self.editor.dialog_manager.show_ollama_status(),
            "ollama_settings": lambda: self.editor.dialog_manager.show_ollama_settings(),
            "open_file": lambda: self.editor.open_file(),
            "save_as": lambda: self.editor.save_file(save_as=True),
            "validate_install": lambda: self.editor.dialog_manager.show_installation_validator(),
        }

        handler = action_map.get(action_id)
        if handler:
            handler()

    def classify_exception(self, exc: Exception) -> str:
        """Classify exception to error type."""
        exc_str = str(exc).lower()

        if "permission" in exc_str:
            return "permission_denied"
        if "not found" in exc_str or "no such file" in exc_str:
            return "file_not_found"
        if "pandoc" in exc_str:
            return "pandoc_not_found"
        if "ollama" in exc_str or "11434" in exc_str:
            return "ollama_not_running"
        if "git" in exc_str and "repository" in exc_str:
            return "git_no_repo"

        return "generic"
