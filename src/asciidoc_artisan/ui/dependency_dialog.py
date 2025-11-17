"""
Dependency Validation Dialog - Shows dependency check results at startup.

Displays:
- List of all checked dependencies with status
- Missing required dependencies (critical)
- Missing optional dependencies (warnings)
- Installation instructions for missing items
- Visual indicators (✓, ✗, ⚠️)

v2.0.1: Created for startup validation feedback
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import (
    Dependency,
    DependencyStatus,
    DependencyType,
)

logger = logging.getLogger(__name__)


class DependencyValidationDialog(QDialog):
    """Dialog for displaying dependency validation results."""

    def __init__(
        self, dependencies: list[Dependency], parent: QWidget | None = None
    ) -> None:
        """
        Initialize the dependency validation dialog.

        Args:
            dependencies: List of Dependency objects from validation
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.dependencies = dependencies
        self.has_critical = self._has_critical_issues()

        self._setup_ui()

    def _has_critical_issues(self) -> bool:
        """Check if there are critical dependency issues."""
        return any(
            dep.dep_type == DependencyType.REQUIRED
            and dep.status != DependencyStatus.INSTALLED
            for dep in self.dependencies
        )

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        # Set window properties
        if self.has_critical:
            self.setWindowTitle("❌ Critical Dependencies Missing")
        else:
            self.setWindowTitle("✓ Dependency Check")

        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        # Create main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add header
        header = self._create_header()
        layout.addWidget(header)

        # Add dependency details
        details = self._create_details_view()
        layout.addWidget(details)

        # Add footer with buttons
        footer = self._create_footer()
        layout.addLayout(footer)

    def _create_header(self) -> QLabel:
        """Create the header label with summary."""
        total = len(self.dependencies)
        installed = len(
            [d for d in self.dependencies if d.status == DependencyStatus.INSTALLED]
        )
        missing_required = len(
            [
                d
                for d in self.dependencies
                if d.dep_type == DependencyType.REQUIRED
                and d.status != DependencyStatus.INSTALLED
            ]
        )
        missing_optional = len(
            [
                d
                for d in self.dependencies
                if d.dep_type == DependencyType.OPTIONAL
                and d.status != DependencyStatus.INSTALLED
            ]
        )

        header_label = QLabel()
        header_label.setWordWrap(True)

        if self.has_critical:
            header_text = (
                f"<h2 style='color: #d32f2f;'>⚠️ Critical Dependencies Missing</h2>"
                f"<p><b>{missing_required}</b> required dependencies are missing. "
                f"The application may not work correctly.</p>"
            )
        else:
            header_text = (
                f"<h2 style='color: #388e3c;'>✓ Dependency Check Complete</h2>"
                f"<p>All required dependencies are installed. "
                f"{missing_optional} optional features are unavailable.</p>"
            )

        header_text += (
            f"<p><b>Summary:</b> {installed}/{total} dependencies installed</p>"
        )

        header_label.setText(header_text)
        header_label.setTextFormat(Qt.TextFormat.RichText)
        return header_label

    def _create_details_view(self) -> QTextEdit:
        """Create the detailed dependency list view."""
        details = QTextEdit()
        details.setReadOnly(True)

        # Build HTML content
        html = "<html><body style='font-family: monospace;'>"

        # Group by type
        required_deps = [
            d for d in self.dependencies if d.dep_type == DependencyType.REQUIRED
        ]
        optional_deps = [
            d for d in self.dependencies if d.dep_type == DependencyType.OPTIONAL
        ]

        # Required dependencies
        if required_deps:
            html += "<h3>Required Dependencies:</h3>"
            html += "<table style='width: 100%; border-collapse: collapse;'>"
            for dep in required_deps:
                html += self._format_dependency_row(dep)
            html += "</table>"

        # Optional dependencies
        if optional_deps:
            html += "<h3>Optional Dependencies:</h3>"
            html += "<table style='width: 100%; border-collapse: collapse;'>"
            for dep in optional_deps:
                html += self._format_dependency_row(dep)
            html += "</table>"

        html += "</body></html>"

        details.setHtml(html)
        return details

    def _format_dependency_row(self, dep: Dependency) -> str:
        """
        Format a single dependency as HTML table row.

        Args:
            dep: Dependency object to format

        Returns:
            HTML string for table row
        """
        # Choose icon and color based on status
        if dep.status == DependencyStatus.INSTALLED:
            icon = "✓"
            color = "#388e3c"  # Green
        elif dep.status == DependencyStatus.MISSING:
            if dep.dep_type == DependencyType.REQUIRED:
                icon = "✗"
                color = "#d32f2f"  # Red
            else:
                icon = "○"
                color = "#f57c00"  # Orange
        else:
            icon = "⚠️"
            color = "#f57c00"  # Orange

        # Build row
        row = "<tr style='border-bottom: 1px solid #e0e0e0;'>"
        row += f"<td style='padding: 8px; color: {color}; font-size: 16px;'>{icon}</td>"
        row += f"<td style='padding: 8px;'><b>{dep.name}</b>"

        # Add version info if available
        if dep.status == DependencyStatus.INSTALLED and dep.version:
            row += f" <span style='color: #666;'>(v{dep.version})</span>"
        elif dep.min_version:
            row += f" <span style='color: #666;'>(≥{dep.min_version})</span>"

        row += "</td>"
        row += "</tr>"

        # Add installation instructions if missing
        if dep.status != DependencyStatus.INSTALLED and dep.install_instructions:
            row += "<tr>"
            row += "<td></td>"
            row += "<td style='padding: 4px 8px; color: #666; font-size: 11px;'>"
            row += f"<pre style='margin: 0; white-space: pre-wrap;'>{dep.install_instructions}</pre>"
            row += "</td>"
            row += "</tr>"

        return row

    def _create_footer(self) -> QHBoxLayout:
        """Create the footer with action buttons."""
        footer_layout = QHBoxLayout()

        # Add stretch to push buttons to the right
        footer_layout.addStretch()

        # Close button
        if self.has_critical:
            close_btn = QPushButton("Exit Application")
            close_btn.clicked.connect(self.reject)
            close_btn.setStyleSheet("background-color: #d32f2f; color: white;")
        else:
            close_btn = QPushButton("Continue")
            close_btn.clicked.connect(self.accept)

        footer_layout.addWidget(close_btn)

        return footer_layout


def show_dependency_validation(
    dependencies: list[Dependency], parent: QWidget | None = None
) -> bool:
    """
    Show dependency validation results in a dialog.

    Args:
        dependencies: List of Dependency objects
        parent: Parent widget (optional)

    Returns:
        True if user can continue (no critical issues or acknowledged),
        False if user chose to exit
    """
    dialog = DependencyValidationDialog(dependencies, parent)

    # If critical issues, show modal dialog that must be acknowledged
    if dialog.has_critical:
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
    else:
        # If no critical issues, just show informational dialog
        # and auto-continue after a few seconds or when dismissed
        dialog.show()
        return True


def show_dependency_summary_message(
    dependencies: list[Dependency], parent: QWidget | None = None
) -> None:
    """
    Show a brief summary message box for dependency validation.

    Args:
        dependencies: List of Dependency objects
        parent: Parent widget (optional)
    """
    missing_required = [
        d
        for d in dependencies
        if d.dep_type == DependencyType.REQUIRED
        and d.status != DependencyStatus.INSTALLED
    ]
    missing_optional = [
        d
        for d in dependencies
        if d.dep_type == DependencyType.OPTIONAL
        and d.status != DependencyStatus.INSTALLED
    ]

    if missing_required:
        # Critical: Show error message
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Critical Dependencies Missing")
        msg_box.setText(
            f"{len(missing_required)} required dependencies are missing!\n\nThe application may not function correctly."
        )

        # List missing dependencies
        details = "Missing required dependencies:\n"
        for dep in missing_required:
            details += f"\n• {dep.name}"
            if dep.install_instructions:
                details += f"\n  {dep.install_instructions.split(chr(10))[0]}"

        msg_box.setDetailedText(details)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Abort
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.Abort)

        result = msg_box.exec()
        if result == QMessageBox.StandardButton.Abort:  # pragma: no cover
            import sys

            sys.exit(1)

    elif missing_optional and len(missing_optional) > 0:
        # Warning: Some optional features unavailable
        logger.info(
            f"{len(missing_optional)} optional dependencies missing - some features will be unavailable"
        )
