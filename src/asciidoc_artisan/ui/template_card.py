"""
Template Card Widget - Clickable card for template display.

Extracted from template_browser.py for MA principle compliance.
Shows template name, category, and description in a grid layout.
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from asciidoc_artisan.core.models import Template


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
