"""
Example integration of Claude AI features into AsciiDoc Artisan.
This shows how to add AI-powered menu items and functionality to the editor.
"""

from PySide6.QtWidgets import QAction, QInputDialog, QMessageBox, QTextEdit
from PySide6.QtCore import QThread, Signal, QObject
import logging
from claude_client import get_claude_client


logger = logging.getLogger(__name__)


class ClaudeWorker(QObject):
    """Worker for handling Claude AI operations in a separate thread."""

    finished = Signal(bool, str, str)  # success, result, error_type

    def __init__(self):
        super().__init__()
        self.claude = get_claude_client()
        self.operation = None
        self.params = None

    def set_operation(self, operation: str, params: dict):
        """Set the operation to perform."""
        self.operation = operation
        self.params = params

    def run(self):
        """Execute the Claude operation."""
        try:
            if self.operation == "generate":
                success, result, error = self.claude.generate_asciidoc(
                    self.params.get("prompt"),
                    self.params.get("context")
                )
            elif self.operation == "improve":
                success, result, error = self.claude.improve_asciidoc(
                    self.params.get("content"),
                    self.params.get("instruction")
                )
            elif self.operation == "outline":
                success, result, error = self.claude.generate_outline(
                    self.params.get("topic"),
                    self.params.get("style")
                )
            elif self.operation == "help":
                success, result, error = self.claude.get_asciidoc_help(
                    self.params.get("question")
                )
            else:
                success, result, error = False, "Unknown operation", "INVALID_OP"

            self.finished.emit(success, result, error)
        except Exception as e:
            logger.exception("Error in Claude worker")
            self.finished.emit(False, str(e), "EXCEPTION")


class ClaudeIntegration:
    """Integration class to add Claude AI features to AsciiDoc Artisan."""

    def __init__(self, main_window):
        """
        Initialize Claude integration.

        Args:
            main_window: The AsciiDocEditor instance
        """
        self.main_window = main_window
        self.claude_thread = QThread()
        self.claude_worker = ClaudeWorker()
        self.claude_worker.moveToThread(self.claude_thread)

        # Connect signals
        self.claude_thread.started.connect(self.claude_worker.run)
        self.claude_worker.finished.connect(self._handle_claude_result)
        self.claude_worker.finished.connect(self.claude_thread.quit)

        # Add Claude menu
        self._create_claude_menu()

        # Check Claude availability
        self._check_claude_service()

    def _create_claude_menu(self):
        """Create the Claude AI menu in the menu bar."""
        claude_menu = self.main_window.menuBar().addMenu("&Claude AI")

        # Generate content action
        self.generate_action = QAction("&Generate AsciiDoc...", self.main_window)
        self.generate_action.setStatusTip("Generate AsciiDoc content using AI")
        self.generate_action.triggered.connect(self._generate_content)
        claude_menu.addAction(self.generate_action)

        # Improve content action
        self.improve_action = QAction("&Improve Selection...", self.main_window)
        self.improve_action.setStatusTip("Improve selected AsciiDoc content")
        self.improve_action.triggered.connect(self._improve_content)
        claude_menu.addAction(self.improve_action)

        # Generate outline action
        self.outline_action = QAction("Generate &Outline...", self.main_window)
        self.outline_action.setStatusTip("Generate a documentation outline")
        self.outline_action.triggered.connect(self._generate_outline)
        claude_menu.addAction(self.outline_action)

        claude_menu.addSeparator()

        # AsciiDoc help action
        self.help_action = QAction("AsciiDoc &Help...", self.main_window)
        self.help_action.setStatusTip("Get help with AsciiDoc syntax")
        self.help_action.triggered.connect(self._get_help)
        claude_menu.addAction(self.help_action)

        # Initially disable actions
        self._set_claude_actions_enabled(False)

    def _check_claude_service(self):
        """Check if Claude service is available."""
        claude = get_claude_client()
        if claude.is_available():
            self._set_claude_actions_enabled(True)
            self.main_window.statusBar.showMessage("Claude AI service connected", 3000)
        else:
            self._set_claude_actions_enabled(False)
            logger.info("Claude AI service not available. Start the Node.js service to enable AI features.")

    def _set_claude_actions_enabled(self, enabled: bool):
        """Enable or disable Claude menu actions."""
        self.generate_action.setEnabled(enabled)
        self.improve_action.setEnabled(enabled)
        self.outline_action.setEnabled(enabled)
        self.help_action.setEnabled(enabled)

    def _generate_content(self):
        """Handle generate content action."""
        prompt, ok = QInputDialog.getMultiLineText(
            self.main_window,
            "Generate AsciiDoc Content",
            "Describe what content you want to generate:",
            ""
        )

        if ok and prompt.strip():
            self._execute_claude_operation("generate", {
                "prompt": prompt,
                "context": "AsciiDoc technical documentation"
            })

    def _improve_content(self):
        """Handle improve content action."""
        # Get selected text or all text
        cursor = self.main_window.editor.textCursor()
        selected_text = cursor.selectedText()

        if not selected_text:
            # No selection, use all text
            selected_text = self.main_window.editor.toPlainText()
            if not selected_text.strip():
                QMessageBox.warning(
                    self.main_window,
                    "No Content",
                    "Please write or select some content to improve."
                )
                return

        instruction, ok = QInputDialog.getMultiLineText(
            self.main_window,
            "Improve AsciiDoc Content",
            "How should the content be improved?",
            "Make it more clear and well-structured"
        )

        if ok and instruction.strip():
            self._execute_claude_operation("improve", {
                "content": selected_text,
                "instruction": instruction
            })

    def _generate_outline(self):
        """Handle generate outline action."""
        topic, ok = QInputDialog.getText(
            self.main_window,
            "Generate Documentation Outline",
            "Enter the topic for the outline:"
        )

        if ok and topic.strip():
            style, ok = QInputDialog.getItem(
                self.main_window,
                "Outline Style",
                "Select documentation style:",
                ["Technical Documentation", "User Guide", "API Reference", "Tutorial"],
                0,
                False
            )

            if ok:
                self._execute_claude_operation("outline", {
                    "topic": topic,
                    "style": style
                })

    def _get_help(self):
        """Handle AsciiDoc help action."""
        question, ok = QInputDialog.getText(
            self.main_window,
            "AsciiDoc Help",
            "What would you like to know about AsciiDoc?"
        )

        if ok and question.strip():
            self._execute_claude_operation("help", {
                "question": question
            })

    def _execute_claude_operation(self, operation: str, params: dict):
        """Execute a Claude operation in a background thread."""
        if self.claude_thread.isRunning():
            QMessageBox.warning(
                self.main_window,
                "Operation in Progress",
                "Please wait for the current operation to complete."
            )
            return

        # Show progress in status bar
        self.main_window.statusBar.showMessage(f"Claude AI: {operation}...", 0)

        # Set up and start the operation
        self.claude_worker.set_operation(operation, params)
        self.claude_thread.start()

    def _handle_claude_result(self, success: bool, result: str, error_type: str):
        """Handle the result from Claude operation."""
        self.main_window.statusBar.clearMessage()

        if success:
            # Handle successful result based on operation
            if self.claude_worker.operation == "help":
                # Show help in a dialog
                msg = QMessageBox(self.main_window)
                msg.setWindowTitle("AsciiDoc Help")
                msg.setText("Claude AI Response:")
                msg.setDetailedText(result)
                msg.setIcon(QMessageBox.Information)
                msg.exec()
            else:
                # Insert or replace text in editor
                cursor = self.main_window.editor.textCursor()

                if self.claude_worker.operation == "improve" and cursor.hasSelection():
                    # Replace selected text
                    cursor.insertText(result)
                else:
                    # Insert at cursor or append
                    if not cursor.hasSelection():
                        cursor.movePosition(cursor.End)
                        if self.main_window.editor.toPlainText():
                            cursor.insertText("\n\n")
                    cursor.insertText(result)

                self.main_window.statusBar.showMessage("Claude AI operation completed", 5000)
        else:
            # Show error
            error_title = {
                "TIMEOUT": "Request Timeout",
                "CONNECTION": "Connection Error",
                "API_ERROR": "API Error",
            }.get(error_type, "Error")

            QMessageBox.critical(
                self.main_window,
                f"Claude AI - {error_title}",
                result
            )
            self.main_window.statusBar.showMessage("Claude AI operation failed", 5000)


def integrate_claude(main_window):
    """
    Integrate Claude AI features into the AsciiDoc Artisan main window.

    Args:
        main_window: The AsciiDocEditor instance

    Returns:
        ClaudeIntegration instance
    """
    return ClaudeIntegration(main_window)


# Example of how to add this to the main application:
# In adp.py, after creating the main window:
#
# from claude_integration_example import integrate_claude
#
# # In the __init__ method of AsciiDocEditor, add:
# try:
#     self.claude_integration = integrate_claude(self)
# except Exception as e:
#     print(f"Failed to initialize Claude integration: {e}")
#     self.claude_integration = None