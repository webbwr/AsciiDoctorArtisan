"""
Installation Validator Dialog - Validates app requirements and updates dependencies.

This dialog checks all application requirements (Python packages, system binaries,
optional tools) and provides one-click dependency updates.

Author: AsciiDoc Artisan Team
Version: 1.7.4
"""

import logging

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.ui.validation_worker import ValidationWorker

logger = logging.getLogger(__name__)


class InstallationValidatorDialog(QDialog):
    """Dialog for validating installation and updating dependencies."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize installation validator dialog."""
        super().__init__(parent)
        self.setWindowTitle("Installation Validator")
        self.setMinimumSize(700, 600)
        self.worker: ValidationWorker | None = None
        self.parent_editor = parent  # Store reference to parent for theme access

        self._setup_ui()
        self._apply_theme()  # Apply theme before validation
        self._start_validation()

    def _setup_ui(self) -> None:
        """
        Setup dialog UI.

        MA principle: Reduced from 53→10 lines by extracting 3 helper methods.
        """
        layout = QVBoxLayout(self)
        self._create_header_section(layout)
        self._create_progress_section(layout)
        layout.addLayout(self._create_button_bar())

    def _create_header_section(self, layout: QVBoxLayout) -> None:
        """Create header and description section."""
        self.header = QLabel("Installation Validator")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.header)

        self.description = QLabel(
            "This tool validates all application requirements and allows you to\n"
            "update Python dependencies to their latest versions."
        )
        self.description.setStyleSheet("padding: 5px 10px;")
        layout.addWidget(self.description)

    def _create_progress_section(self, layout: QVBoxLayout) -> None:
        """Create results display and progress indicators."""
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("font-family: monospace; padding: 10px;")
        layout.addWidget(self.results_text)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Progress label (hidden initially)
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("padding: 5px; font-style: italic;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

    def _create_button_bar(self) -> QHBoxLayout:
        """Create button bar with validation and update controls."""
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Re-validate")
        self.validate_btn.clicked.connect(self._start_validation)
        button_layout.addWidget(self.validate_btn)

        self.update_btn = QPushButton("Update Dependencies")
        self.update_btn.clicked.connect(self._start_update)
        button_layout.addWidget(self.update_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        return button_layout

    def _apply_theme(self) -> None:
        """Apply theme based on parent editor's dark mode setting.

        MA principle: Reduced from 55→10 lines by extracting 2 helpers (82% reduction).
        """
        dark_mode = self._get_dark_mode_setting()
        colors = self._get_theme_colors(dark_mode)
        self._apply_widget_styles(colors)

    def _get_dark_mode_setting(self) -> bool:
        """Get dark mode setting from parent editor.

        Returns:
            True if dark mode enabled, False otherwise
        """
        if self.parent_editor and hasattr(self.parent_editor, "_settings"):
            return bool(self.parent_editor._settings.dark_mode)
        return False

    def _get_theme_colors(self, dark_mode: bool) -> dict[str, str]:
        """Get color scheme for theme.

        Args:
            dark_mode: Whether dark mode is enabled

        Returns:
            Dictionary with color keys for all UI elements
        """
        if dark_mode:
            return {
                "dialog_bg": "#2b2b2b",
                "text": "#e0e0e0",
                "desc": "#a0a0a0",
                "results_bg": "#1e1e1e",
                "results_text": "#d0d0d0",
                "button_bg": "#3c3c3c",
                "button_text": "#e0e0e0",
                "update_btn_bg": "#2e7d32",  # Darker green for dark mode
                "update_btn_text": "#ffffff",
            }
        else:
            return {
                "dialog_bg": "#ffffff",
                "text": "#000000",
                "desc": "#666666",
                "results_bg": "#f5f5f5",
                "results_text": "#000000",
                "button_bg": "#f0f0f0",
                "button_text": "#000000",
                "update_btn_bg": "#4CAF50",  # Bright green for light mode
                "update_btn_text": "#ffffff",
            }

    def _apply_widget_styles(self, colors: dict[str, str]) -> None:
        """Apply color scheme to all widgets.

        Args:
            colors: Color dictionary from _get_theme_colors
        """
        # Apply to dialog
        self.setStyleSheet(f"background-color: {colors['dialog_bg']}; color: {colors['text']};")

        # Apply to header
        self.header.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 10px; color: {colors['text']};")

        # Apply to description
        self.description.setStyleSheet(f"padding: 5px 10px; color: {colors['desc']};")

        # Apply to results text
        self.results_text.setStyleSheet(
            f"font-family: monospace; padding: 10px; background-color: {colors['results_bg']}; color: {colors['results_text']};"
        )

        # Apply to buttons
        self.validate_btn.setStyleSheet(
            f"background-color: {colors['button_bg']}; color: {colors['button_text']}; padding: 8px;"
        )
        self.update_btn.setStyleSheet(
            f"background-color: {colors['update_btn_bg']}; color: {colors['update_btn_text']}; font-weight: bold; padding: 8px;"
        )
        self.close_btn.setStyleSheet(
            f"background-color: {colors['button_bg']}; color: {colors['button_text']}; padding: 8px;"
        )

    def _start_validation(self) -> None:
        """Start validation in background thread."""
        if self.worker and self.worker.isRunning():
            return

        logger.info("Starting validation UI...")
        self.results_text.setPlainText("Validating installation...\n")
        self.validate_btn.setEnabled(False)
        self.update_btn.setEnabled(False)

        self.worker = ValidationWorker(action="validate")
        logger.info("Connecting signals...")
        self.worker.validation_complete.connect(self._show_validation_results)
        self.worker.finished.connect(self._validation_finished)
        logger.info("Starting worker thread...")
        self.worker.start()

    def _validation_finished(self) -> None:
        """Handle validation worker finished."""
        self.validate_btn.setEnabled(True)
        self.update_btn.setEnabled(True)

    def _show_validation_results(self, results: dict[str, list[tuple[str, ...]]]) -> None:
        """
        Display validation results.

        Args:
            results: {category: [(name, status, version, message)]}
        """
        logger.info(f"Displaying validation results: {len(results)} categories")
        logger.info(f"Python packages: {len(results.get('python_packages', []))}")
        logger.info(f"System binaries: {len(results.get('system_binaries', []))}")
        logger.info(f"Optional tools: {len(results.get('optional_tools', []))}")

        output = []

        # Python packages
        output.append("=" * 70)
        output.append("PYTHON PACKAGES")
        output.append("=" * 70)
        output.append("")

        for name, status, version, message in results.get("python_packages", []):
            output.append(f"{status} {name:20} {version:20} {message}")

        output.append("")

        # System binaries (required)
        output.append("=" * 70)
        output.append("SYSTEM BINARIES (Required)")
        output.append("=" * 70)
        output.append("")

        for name, status, version, message in results.get("system_binaries", []):
            output.append(f"{status} {name:20} {version:20} {message}")

        output.append("")

        # Optional tools
        output.append("=" * 70)
        output.append("OPTIONAL TOOLS")
        output.append("=" * 70)
        output.append("")

        for name, status, version, message in results.get("optional_tools", []):
            output.append(f"{status} {name:20} {version:20} {message}")

        output.append("")
        output.append("=" * 70)
        output.append("Legend: ✓=OK, ⚠=Warning, ✗=Missing/Error, ○=Optional not installed")
        output.append("=" * 70)

        result_text = "\n".join(output)
        logger.info(f"Setting text with {len(result_text)} characters, {len(output)} lines")
        self.results_text.setPlainText(result_text)
        logger.info("Text set successfully")

    def _start_update(self) -> None:
        """Start dependency update in background thread."""
        if self.worker and self.worker.isRunning():
            return

        # Confirm action
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Update Dependencies",
            "This will update all Python dependencies to their latest versions.\n\n"
            "The application will need to be restarted after the update.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.results_text.setPlainText("")
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.validate_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.close_btn.setEnabled(False)

        self.worker = ValidationWorker(action="update")
        self.worker.update_progress.connect(self._show_update_progress)
        self.worker.update_complete.connect(self._show_update_complete)
        self.worker.finished.connect(self._update_finished)
        self.worker.start()

    def _show_update_progress(self, message: str) -> None:
        """Show update progress message."""
        self.progress_label.setText(message)
        current = self.results_text.toPlainText()
        self.results_text.setPlainText(current + message + "\n")
        # Scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.results_text.setTextCursor(cursor)

    def _show_update_complete(self, success: bool, message: str) -> None:
        """Show update completion message."""
        from PySide6.QtWidgets import QMessageBox

        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if success:
            QMessageBox.information(self, "Update Complete", message)
            # Re-validate after successful update
            self._start_validation()
        else:
            QMessageBox.warning(self, "Update Failed", message)

    def _update_finished(self) -> None:
        """Handle update worker finished."""
        self.validate_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
