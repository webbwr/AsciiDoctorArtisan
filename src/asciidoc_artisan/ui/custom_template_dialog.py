"""
Custom Template Dialog - Create new templates.

Extracted from template_browser.py for MA principle compliance.
Allows users to create custom templates with variable detection.
"""

import re

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core.models import Template, TemplateVariable
from asciidoc_artisan.core.template_manager import TemplateManager


class CustomTemplateDialog(QDialog):
    """
    Dialog for creating custom templates.

    Allows users to create new templates by providing:
    - Template metadata (name, category, description, author)
    - Template content (AsciiDoc with {{variable}} placeholders)
    - Variable definitions (optional)

    The dialog automatically saves the template to the custom templates directory.

    Example:
        ```python
        dialog = CustomTemplateDialog(template_manager, parent)
        if dialog.exec():
            print("Template created successfully")
        ```
    """

    def __init__(self, manager: TemplateManager, parent: QWidget | None = None) -> None:
        """
        Initialize custom template dialog.

        Args:
            manager: Template manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.manager = manager
        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Setup dialog UI.

        MA principle: Reduced from 73→14 lines by extracting 3 helper methods.
        """
        self.setWindowTitle("Create Custom Template")
        self.setModal(True)
        self.resize(700, 600)

        layout = QVBoxLayout(self)
        layout.addLayout(self._create_metadata_form())
        self._create_content_editor(layout)
        layout.addLayout(self._create_action_buttons())

    def _create_metadata_form(self) -> QFormLayout:
        """Create form for template metadata fields."""
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Custom Template")
        form.addRow("Template Name*:", self.name_edit)

        self.category_combo = QComboBox()
        # Get existing categories from manager
        categories = self.manager.get_categories()
        self.category_combo.addItems(categories if categories else ["article", "book", "report", "general"])
        self.category_combo.setEditable(True)  # Allow custom categories
        form.addRow("Category*:", self.category_combo)

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Brief description of the template")
        form.addRow("Description*:", self.description_edit)

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Your Name")
        form.addRow("Author:", self.author_edit)

        self.version_edit = QLineEdit()
        self.version_edit.setText("1.0")
        form.addRow("Version:", self.version_edit)

        return form

    def _create_content_editor(self, layout: QVBoxLayout) -> None:
        """Create content editor section with help text."""
        content_label = QLabel("Template Content*:")
        content_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(content_label)

        help_label = QLabel("Use {{variable_name}} for placeholders. Example: {{title}}, {{author}}, {{date}}")
        help_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(help_label)

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText(
            "= {{title}}\n:author: {{author}}\n:date: {{date}}\n\n== Introduction\n\n{{content}}"
        )
        self.content_edit.setMinimumHeight(200)
        layout.addWidget(self.content_edit)

        # Variable detection checkbox
        self.auto_detect_vars = QCheckBox("Auto-detect variables from content")
        self.auto_detect_vars.setChecked(True)
        self.auto_detect_vars.setToolTip("Automatically find {{variable}} patterns and create variable definitions")
        layout.addWidget(self.auto_detect_vars)

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create Create/Cancel button layout."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.create_btn = QPushButton("Create Template")
        self.create_btn.clicked.connect(self._on_create_clicked)
        button_layout.addWidget(self.create_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        return button_layout

    def _on_create_clicked(self) -> None:
        """
        Handle create button click.

        MA principle: Reduced from 58→34 lines by extracting validation helper (41% reduction).
        """
        # Validate required fields
        name = self.name_edit.text().strip()
        category = self.category_combo.currentText().strip()
        description = self.description_edit.text().strip()
        content = self.content_edit.toPlainText().strip()

        # Run validation
        if not self._validate_template_fields(name, category, description, content):
            return

        # Extract variables if auto-detect enabled
        variables: list[TemplateVariable] = []
        if self.auto_detect_vars.isChecked():
            variables = self._detect_variables(content)

        # Create and save template
        template = Template(
            name=name,
            category=category,
            description=description,
            author=self.author_edit.text().strip() or "Anonymous",
            version=self.version_edit.text().strip() or "1.0",
            variables=variables,
            content=content,
        )

        self._save_template_and_show_result(template, name)

    def _validate_template_fields(self, name: str, category: str, description: str, content: str) -> bool:
        """
        Validate template form fields.

        Args:
            name: Template name
            category: Template category
            description: Template description
            content: Template content

        Returns:
            True if all fields valid, False otherwise
        """
        if not name:
            QMessageBox.warning(self, "Validation Error", "Template name is required.")
            self.name_edit.setFocus()
            return False

        if not category:
            QMessageBox.warning(self, "Validation Error", "Category is required.")
            self.category_combo.setFocus()
            return False

        if not description:
            QMessageBox.warning(self, "Validation Error", "Description is required.")
            self.description_edit.setFocus()
            return False

        if not content:
            QMessageBox.warning(self, "Validation Error", "Template content is required.")
            self.content_edit.setFocus()
            return False

        return True

    def _save_template_and_show_result(self, template: Template, name: str) -> None:
        """
        Save template and display result message.

        Args:
            template: Template to save
            name: Template name for display
        """
        if self.manager.create_template(template, custom=True):
            QMessageBox.information(
                self,
                "Success",
                f"Template '{name}' created successfully!\n\nYou can now use it from the template browser.",
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create template '{name}'.\n\nPlease check the logs for details.",
            )

    def _detect_variables(self, content: str) -> list[TemplateVariable]:
        """
        Auto-detect variables from template content.

        Finds all {{variable}} patterns and creates TemplateVariable objects.

        Args:
            content: Template content to scan

        Returns:
            List of detected variables
        """
        # Find all {{variable}} patterns
        pattern = r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}"
        matches = re.findall(pattern, content)

        # Create unique list
        unique_vars = sorted(set(matches))

        # Create TemplateVariable objects
        variables = []
        for var_name in unique_vars:
            variables.append(
                TemplateVariable(
                    name=var_name,
                    description=f"Value for {var_name}",
                    required=True,  # Mark all detected variables as required
                    default=None,
                    type="string",
                )
            )

        return variables
