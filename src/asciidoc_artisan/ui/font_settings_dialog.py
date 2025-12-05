"""
Font Settings Dialog - Customize fonts for editor, preview, and chat.

Extracted from dialogs.py for MA principle compliance.
Allows setting font family and size for all panes.

Refactored to use BaseSettingsDialog for consistent structure.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import Settings
from asciidoc_artisan.ui.dialog_factory import BaseSettingsDialog


class FontSettingsDialog(BaseSettingsDialog):
    """
    Font Settings dialog for customizing fonts in editor, preview, and chat.

    Allows users to:
    - Set font family for editor pane (monospace recommended)
    - Set font size for editor pane
    - Set font family for preview pane
    - Set font size for preview pane
    - Set font family for chat pane
    - Set font size for chat pane

    Args:
        settings: Current Settings instance to edit
        parent: Parent QWidget (optional)
    """

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        """Initialize font settings dialog."""
        self.settings = settings
        # Create widgets before super().__init__ since _create_content needs them
        self.editor_font_combo = QComboBox()
        self.editor_size_spin = QSpinBox()
        self.preview_font_combo = QComboBox()
        self.preview_size_spin = QSpinBox()
        self.chat_font_combo = QComboBox()
        self.chat_size_spin = QSpinBox()
        super().__init__(parent)

    def _get_title(self) -> str:
        """Return window title."""
        return "Font Settings"

    def _get_header_text(self) -> tuple[str, str] | None:
        """Return header text."""
        return ("Customize Fonts", "Set font family and size for editor, preview, and chat panes.")

    def _create_content(self, layout: QVBoxLayout) -> None:
        """Add font settings groups to layout."""
        # Add font groups
        layout.addWidget(
            self._create_font_group(
                "Editor Font",
                self.editor_font_combo,
                self.editor_size_spin,
                self.settings.editor_font_family,
                self.settings.editor_font_size,
            )
        )
        layout.addWidget(
            self._create_font_group(
                "Preview Font",
                self.preview_font_combo,
                self.preview_size_spin,
                self.settings.preview_font_family,
                self.settings.preview_font_size,
            )
        )
        layout.addWidget(
            self._create_font_group(
                "Chat Font",
                self.chat_font_combo,
                self.chat_size_spin,
                self.settings.chat_font_family,
                self.settings.chat_font_size,
            )
        )

    def _create_font_group(
        self, title: str, font_combo: QComboBox, size_spin: QSpinBox, current_family: str, current_size: int
    ) -> QGroupBox:
        """Create a font settings group with family and size controls."""
        group = QGroupBox(title)
        group_layout = QVBoxLayout()

        # Font family selection
        family_layout = QHBoxLayout()
        family_layout.addWidget(QLabel("Font Family:"))
        self._populate_font_list(font_combo)
        font_combo.setCurrentText(current_family)
        family_layout.addWidget(font_combo)
        group_layout.addLayout(family_layout)

        # Font size selection
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        size_spin.setRange(6, 72)
        size_spin.setValue(current_size)
        size_spin.setSuffix(" pt")
        size_layout.addWidget(size_spin)
        size_layout.addStretch()
        group_layout.addLayout(size_layout)

        group.setLayout(group_layout)
        return group

    def _populate_font_list(self, combo: QComboBox) -> None:
        """Populate combo box with common fonts."""
        # Common monospace fonts for editor
        monospace_fonts = [
            "Courier New",
            "Consolas",
            "Monaco",
            "Menlo",
            "Ubuntu Mono",
            "Fira Code",
            "Source Code Pro",
            "JetBrains Mono",
            "DejaVu Sans Mono",
        ]

        # Common sans-serif fonts for preview/chat
        sans_fonts = [
            "Arial",
            "Helvetica",
            "Verdana",
            "Tahoma",
            "Trebuchet MS",
            "Segoe UI",
            "Ubuntu",
            "Roboto",
            "Open Sans",
        ]

        # Common serif fonts
        serif_fonts = [
            "Times New Roman",
            "Georgia",
            "Garamond",
            "Palatino",
            "Book Antiqua",
        ]

        # Combine all fonts
        all_fonts = sorted(set(monospace_fonts + sans_fonts + serif_fonts))
        combo.addItems(all_fonts)

    def get_settings(self) -> Settings:
        """Get updated settings with font changes."""
        self.settings.editor_font_family = self.editor_font_combo.currentText()
        self.settings.editor_font_size = self.editor_size_spin.value()
        self.settings.preview_font_family = self.preview_font_combo.currentText()
        self.settings.preview_font_size = self.preview_size_spin.value()
        self.settings.chat_font_family = self.chat_font_combo.currentText()
        self.settings.chat_font_size = self.chat_size_spin.value()

        return self.settings
