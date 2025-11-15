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
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core.models import Template
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
        """Setup browser UI."""
        self.setWindowTitle("Template Browser")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Top bar: Category filter and search
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

        layout.addLayout(top_layout)

        # Template grid
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        layout.addWidget(self.grid_widget)

        # Preview area
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)

        # Bottom buttons
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

        layout.addLayout(button_layout)

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
            templates = [
                t
                for t in templates
                if search_text in t.name.lower() or search_text in t.description.lower()
            ]

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
        # TODO: Implement custom template creation dialog
        pass


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
        """Setup dialog UI."""
        self.setWindowTitle(f"Template Variables: {self.template.name}")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Create input fields for each variable
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

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

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
