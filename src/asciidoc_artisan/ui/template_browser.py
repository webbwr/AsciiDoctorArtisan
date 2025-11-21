"""
Template browser dialog for AsciiDoc Artisan (v2.0.0+).

This module provides a visual template browser with category filtering,
search, and live preview. Users can select templates and fill in variables
to create new documents.

Key features:
- Grid layout with template cards
- Category filtering and search
- Live preview of template content
- Variable input dialog
- Recent templates tracking
- Custom template creation

Architecture:
    User clicks File → New from Template
    → TemplateBrowser shows all templates
    → User selects template → VariableInputDialog
    → User fills variables → TemplateEngine.instantiate()
    → New document created

Example:
    ```python
    from asciidoc_artisan.ui.template_browser import TemplateBrowser
    from asciidoc_artisan.core.template_manager import TemplateManager

    manager = TemplateManager(engine)
    browser = TemplateBrowser(manager)

    if browser.exec():
        template = browser.selected_template
        variables = browser.variable_values
        content = engine.instantiate(template, variables)
    ```
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
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


class TemplateCard(QWidget):
    """
    Template card widget for grid display.

    Shows template name, category, and description in a clickable card.

    Signals:
        clicked: Emitted when card is clicked
    """

    clicked = Signal(Template)

    def __init__(self, template: Template, parent: QWidget | None = None) -> None:
        """
        Initialize template card.

        Args:
            template: Template to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.template = template
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup card UI."""
        layout = QVBoxLayout(self)

        # Template name
        name_label = QLabel(self.template.name)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(12)
        name_label.setFont(name_font)

        # Category
        category_label = QLabel(f"Category: {self.template.category}")
        category_label.setStyleSheet("color: gray;")

        # Description
        desc_label = QLabel(self.template.description)
        desc_label.setWordWrap(True)

        layout.addWidget(name_label)
        layout.addWidget(category_label)
        layout.addWidget(desc_label)

        # Styling
        self.setStyleSheet(
            """
            TemplateCard {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            TemplateCard:hover {
                border-color: #0078d4;
                background-color: #f0f0f0;
            }
        """
        )

        self.setMinimumSize(200, 120)
        self.setMaximumSize(300, 150)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle mouse click."""
        self.clicked.emit(self.template)
        super().mousePressEvent(event)


class TemplateBrowser(QDialog):
    """
    Template browser dialog.

    Displays all available templates in a grid layout with category
    filtering, search, and live preview. When user selects a template,
    shows variable input dialog and creates new document.

    Attributes:
        manager: Template manager
        selected_template: Currently selected template
        variable_values: User-provided variable values

    Example:
        ```python
        browser = TemplateBrowser(template_manager)

        if browser.exec():
            template = browser.selected_template
            variables = browser.variable_values
            print(f"Creating document from: {template.name}")
        ```
    """

    def __init__(self, manager: TemplateManager, parent: QWidget | None = None) -> None:
        """
        Initialize template browser.

        Args:
            manager: Template manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.manager = manager
        self.selected_template: Template | None = None
        self.variable_values: dict[str, str] = {}

        self._setup_ui()
        self._load_templates()

    def _setup_ui(self) -> None:
        """
        Setup browser UI.

        MA principle: Reduced from 63→16 lines by extracting 4 helper methods.
        """
        self.setWindowTitle("Template Browser")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.addLayout(self._create_filter_bar())
        layout.addWidget(self._create_template_grid())
        self._create_preview_area(layout)
        layout.addLayout(self._create_buttons())

    def _create_filter_bar(self) -> QHBoxLayout:
        """Create top bar with category filter and search."""
        top_layout = QHBoxLayout()

        # Category filter
        top_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.currentTextChanged.connect(self._filter_templates)
        top_layout.addWidget(self.category_combo)

        # Search box
        top_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search templates...")
        self.search_edit.textChanged.connect(self._filter_templates)
        top_layout.addWidget(self.search_edit)

        return top_layout

    def _create_template_grid(self) -> QWidget:
        """Create template grid widget."""
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        return self.grid_widget

    def _create_preview_area(self, layout: QVBoxLayout) -> None:
        """Create preview area with label and text editor."""
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)

    def _create_buttons(self) -> QHBoxLayout:
        """Create bottom button bar."""
        button_layout = QHBoxLayout()

        self.new_template_btn = QPushButton("Create New Template")
        self.new_template_btn.clicked.connect(self._create_new_template)
        button_layout.addWidget(self.new_template_btn)

        button_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        return button_layout

    def _load_templates(self) -> None:
        """Load templates from manager."""
        # Load categories
        categories = self.manager.get_categories()
        for category in categories:
            self.category_combo.addItem(category)

        # Display all templates
        self._filter_templates()

    def _filter_templates(self) -> None:
        """Filter templates by category and search text."""
        # Clear grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Get filter criteria
        category = self.category_combo.currentText()
        search_text = self.search_edit.text().lower()

        # Get templates
        if category == "All":
            templates = self.manager.get_all_templates()
        else:
            templates = self.manager.get_templates_by_category(category)

        # Filter by search text
        if search_text:
            templates = [t for t in templates if search_text in t.name.lower() or search_text in t.description.lower()]

        # Display templates in grid
        row = 0
        col = 0
        max_cols = 3

        for template in templates:
            card = TemplateCard(template, self.grid_widget)
            card.clicked.connect(self._on_template_selected)
            self.grid_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _on_template_selected(self, template: Template) -> None:
        """
        Handle template selection.

        Args:
            template: Selected template
        """
        self.selected_template = template

        # Show preview
        preview_text = f"Name: {template.name}\n"
        preview_text += f"Category: {template.category}\n"
        preview_text += f"Description: {template.description}\n"
        preview_text += f"\n{template.content[:500]}..."
        self.preview_text.setPlainText(preview_text)

        # Enable OK button
        self.ok_btn.setEnabled(True)

    def _on_ok_clicked(self) -> None:
        """Handle OK button click."""
        if not self.selected_template:
            return

        # Show variable input dialog
        if self.selected_template.variables:
            dialog = VariableInputDialog(self.selected_template, self)
            if dialog.exec():
                self.variable_values = dialog.get_values()
                self.accept()
        else:
            # No variables - accept immediately
            self.variable_values = {}
            self.accept()

    def _create_new_template(self) -> None:
        """Create new custom template."""
        dialog = CustomTemplateDialog(self.manager, self)
        if dialog.exec():
            # Reload templates to show newly created one
            self._load_templates()


class VariableInputDialog(QDialog):
    """
    Variable input dialog for template instantiation.

    Shows input fields for all template variables with validation.

    Attributes:
        template: Template being instantiated
        inputs: Dictionary mapping variable names to input widgets

    Example:
        ```python
        dialog = VariableInputDialog(template)
        if dialog.exec():
            values = dialog.get_values()
            content = engine.instantiate(template, values)
        ```
    """

    def __init__(self, template: Template, parent: QWidget | None = None) -> None:
        """
        Initialize variable input dialog.

        Args:
            template: Template with variables to fill
            parent: Parent widget
        """
        super().__init__(parent)
        self.template = template
        self.inputs: dict[str, QLineEdit] = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """
        Setup dialog UI.

        MA principle: Reduced from 46→12 lines by extracting 2 helper methods.
        """
        self.setWindowTitle(f"Template Variables: {self.template.name}")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        self._create_variable_inputs(layout)
        layout.addLayout(self._create_dialog_buttons())

    def _create_variable_inputs(self, layout: QVBoxLayout) -> None:
        """Create input fields for each template variable."""
        for var in self.template.variables:
            # Variable name label
            label = QLabel(f"{var.name}:")
            if var.required:
                label.setText(f"{var.name}: *")
            layout.addWidget(label)

            # Input field
            input_widget = QLineEdit()
            input_widget.setPlaceholderText(var.description)

            # Set default value
            if var.default:
                input_widget.setText(var.default)

            self.inputs[var.name] = input_widget
            layout.addWidget(input_widget)

            # Description
            if var.description:
                desc_label = QLabel(var.description)
                desc_label.setStyleSheet("color: gray; font-size: 10px;")
                layout.addWidget(desc_label)

    def _create_dialog_buttons(self) -> QHBoxLayout:
        """Create OK/Cancel button layout."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        return button_layout

    def _on_ok_clicked(self) -> None:
        """Handle OK button click with validation."""
        # Validate required fields
        for var in self.template.variables:
            if var.required:
                value = self.inputs[var.name].text().strip()
                if not value:
                    # Show error - required field empty
                    self.inputs[var.name].setStyleSheet("border: 1px solid red;")
                    return

        # All valid - accept
        self.accept()

    def get_values(self) -> dict[str, str]:
        """
        Get variable values from input fields.

        Returns:
            Dictionary mapping variable names to user-provided values
        """
        values = {}
        for var_name, input_widget in self.inputs.items():
            values[var_name] = input_widget.text().strip()
        return values


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
        """Handle create button click."""
        # Validate required fields
        name = self.name_edit.text().strip()
        category = self.category_combo.currentText().strip()
        description = self.description_edit.text().strip()
        content = self.content_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Template name is required.")
            self.name_edit.setFocus()
            return

        if not category:
            QMessageBox.warning(self, "Validation Error", "Category is required.")
            self.category_combo.setFocus()
            return

        if not description:
            QMessageBox.warning(self, "Validation Error", "Description is required.")
            self.description_edit.setFocus()
            return

        if not content:
            QMessageBox.warning(self, "Validation Error", "Template content is required.")
            self.content_edit.setFocus()
            return

        # Extract variables if auto-detect enabled
        variables: list[TemplateVariable] = []
        if self.auto_detect_vars.isChecked():
            variables = self._detect_variables(content)

        # Create template object
        template = Template(
            name=name,
            category=category,
            description=description,
            author=self.author_edit.text().strip() or "Anonymous",
            version=self.version_edit.text().strip() or "1.0",
            variables=variables,
            content=content,
        )

        # Save template
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
        import re

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
