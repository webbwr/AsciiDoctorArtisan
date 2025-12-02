"""
Settings Editor Dialog - View and edit all application settings.

Extracted from dialogs.py for MA principle compliance.
Provides table-based editing of all settings with real-time saving.
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import Settings


class SettingsEditorDialog(QDialog):
    """
    Settings Editor dialog for viewing and editing all application settings.

    Allows users to:
    - View all stored settings in a table format
    - Edit individual settings with real-time validation
    - Clear all settings to defaults
    - Save changes automatically on edit

    Args:
        settings: Current Settings instance to edit
        settings_manager: SettingsManager instance for saving
        parent: Parent QWidget (optional)
    """

    def __init__(
        self,
        settings: Settings,
        settings_manager: Any,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize settings editor dialog."""
        super().__init__(parent)
        self.settings = settings
        self.settings_manager = settings_manager
        self.parent_window = parent
        self._init_ui()
        self._load_settings()

    def _init_ui(self) -> None:
        """Initialize the settings editor UI."""
        self.setWindowTitle("Application Settings")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Edit Application Settings")
        header_label.setStyleSheet("QLabel { font-size: 14pt; font-weight: bold; }")
        layout.addWidget(header_label)

        info_label = QLabel("Changes are saved automatically. Click 'Clear All' to reset to defaults.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        layout.addWidget(info_label)

        # Settings Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Setting", "Value", "Type"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 350)
        self.table.setColumnWidth(2, 150)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        clear_all_button = QPushButton("Clear All Settings")
        clear_all_button.setToolTip("Reset all settings to default values")
        clear_all_button.clicked.connect(self._clear_all_settings)
        button_layout.addWidget(clear_all_button)

        button_layout.addStretch()

        # Close button (settings are saved automatically)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _load_settings(self) -> None:
        """Load settings into the table."""
        # Convert settings to dictionary
        settings_dict = self.settings.to_dict()

        # Block signals while populating
        self.table.blockSignals(True)

        # Set row count
        self.table.setRowCount(len(settings_dict))

        # Populate table
        row = 0
        for key, value in sorted(settings_dict.items()):
            # Setting name (read-only)
            name_item = QTableWidgetItem(key)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            # Setting value (editable)
            value_str = self._value_to_string(value)
            value_item = QTableWidgetItem(value_str)
            self.table.setItem(row, 1, value_item)

            # Setting type (read-only)
            type_name = type(value).__name__
            type_item = QTableWidgetItem(type_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, type_item)

            row += 1

        # Re-enable signals
        self.table.blockSignals(False)

    def _value_to_string(self, value: Any) -> str:
        """Convert a setting value to string for display."""
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return "True" if value else "False"
        elif isinstance(value, (list, dict)):
            return str(value)
        else:
            return str(value)

    def _string_to_value(self, value_str: str, value_type: str) -> Any:  # noqa: C901
        """Convert string back to appropriate type."""
        if value_type == "NoneType":
            return None
        elif value_type == "bool":
            return value_str.lower() in ("true", "1", "yes")
        elif value_type == "int":
            try:
                return int(value_str)
            except ValueError:
                return 0
        elif value_type == "float":
            try:
                return float(value_str)
            except ValueError:
                return 0.0
        elif value_type == "list":
            try:
                import ast

                return ast.literal_eval(value_str)
            except (ValueError, SyntaxError):
                return []
        elif value_type == "dict":
            try:
                import ast

                return ast.literal_eval(value_str)
            except (ValueError, SyntaxError):
                return {}
        else:
            return value_str

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle setting value change - save automatically."""
        # Only handle value column changes
        if item.column() != 1:
            return

        row = item.row()
        name_item = self.table.item(row, 0)
        type_item = self.table.item(row, 2)

        if not name_item or not type_item:
            return

        setting_name = name_item.text()
        new_value_str = item.text()
        value_type = type_item.text()

        # Convert string to appropriate type
        new_value = self._string_to_value(new_value_str, value_type)

        # Update settings object
        setattr(self.settings, setting_name, new_value)

        # Save settings automatically
        self.settings_manager.save_settings(self.settings, self.parent_window)

        # Refresh parent window if available
        if self.parent_window and hasattr(self.parent_window, "_refresh_from_settings"):
            self.parent_window._refresh_from_settings()

    def _clear_all_settings(self) -> None:
        """Clear all settings to defaults after confirmation."""
        reply = QMessageBox.question(
            self,
            "Clear All Settings",
            "Are you sure you want to reset all settings to defaults?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Create new default settings
            self.settings = Settings()

            # Save to disk
            self.settings_manager.save_settings(self.settings, self.parent_window)

            # Reload table
            self._load_settings()

            # Refresh parent window if available
            if self.parent_window and hasattr(self.parent_window, "_refresh_from_settings"):
                self.parent_window._refresh_from_settings()

            QMessageBox.information(self, "Settings Cleared", "All settings have been reset to defaults.")
