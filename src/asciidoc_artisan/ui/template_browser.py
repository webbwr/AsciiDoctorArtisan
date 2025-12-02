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

MA principle: Reduced from 695→210 lines by extracting 3 dialog classes.
"""

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

# Import extracted classes for use and backward compatibility
from asciidoc_artisan.ui.custom_template_dialog import CustomTemplateDialog
from asciidoc_artisan.ui.template_card import TemplateCard
from asciidoc_artisan.ui.variable_input_dialog import VariableInputDialog

# Re-export for backward compatibility
__all__ = [
    "CustomTemplateDialog",
    "TemplateBrowser",
    "TemplateCard",
    "VariableInputDialog",
]


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
