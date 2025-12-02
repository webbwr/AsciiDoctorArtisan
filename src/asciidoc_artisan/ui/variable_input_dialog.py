"""
Variable Input Dialog - Form for template variable values.

Extracted from template_browser.py for MA principle compliance.
Shows input fields for all template variables with validation.
"""

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core.models import Template


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
