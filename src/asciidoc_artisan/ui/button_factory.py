"""
Button Factory - Styled button creation for consistent UI.

Provides:
- ButtonStyle enum for predefined button colors
- StyledButtonFactory for creating styled QPushButtons
"""

from enum import Enum, auto

from PySide6.QtWidgets import QPushButton

from asciidoc_artisan.ui.style_constants import Colors


class ButtonStyle(Enum):
    """Predefined button styles for consistent UI.

    Styles follow Bootstrap-inspired color conventions:
    - SUCCESS: Green, for positive actions (accept, confirm, save)
    - DANGER: Red, for destructive/negative actions (delete, decline, cancel)
    - WARNING: Yellow/Orange, for caution actions
    - PRIMARY: Blue, for primary actions
    - SECONDARY: Gray, for neutral/secondary actions
    """

    SUCCESS = auto()  # Green - positive actions
    DANGER = auto()  # Red - destructive/negative actions
    WARNING = auto()  # Yellow/Orange - caution
    PRIMARY = auto()  # Blue - primary actions
    SECONDARY = auto()  # Gray - neutral actions


class StyledButtonFactory:
    """Factory for creating consistently styled QPushButtons.

    MA principle: Centralizes button styling to eliminate duplicate CSS across dialogs.
    Saves ~50 lines per dialog that uses styled buttons.

    Example:
        >>> btn = StyledButtonFactory.create_button("Save", ButtonStyle.SUCCESS)
        >>> btn = StyledButtonFactory.create_button("Delete", ButtonStyle.DANGER, icon="🗑️")
    """

    # Color palette (uses style_constants for consistency)
    _COLORS = {
        ButtonStyle.SUCCESS: (Colors.SUCCESS, Colors.SUCCESS_HOVER),
        ButtonStyle.DANGER: (Colors.DANGER, Colors.DANGER_HOVER),
        ButtonStyle.WARNING: (Colors.WARNING, Colors.WARNING_HOVER),
        ButtonStyle.PRIMARY: (Colors.PRIMARY, Colors.PRIMARY_HOVER),
        ButtonStyle.SECONDARY: (Colors.SECONDARY, Colors.SECONDARY_HOVER),
    }

    # Text colors (white for most, dark for warning)
    _TEXT_COLORS = {
        ButtonStyle.SUCCESS: Colors.TEXT_LIGHT,
        ButtonStyle.DANGER: Colors.TEXT_LIGHT,
        ButtonStyle.WARNING: Colors.WARNING_TEXT,
        ButtonStyle.PRIMARY: Colors.TEXT_LIGHT,
        ButtonStyle.SECONDARY: Colors.TEXT_LIGHT,
    }

    @classmethod
    def create_button(
        cls,
        text: str,
        style: ButtonStyle,
        icon: str = "",
        bold: bool = True,
        padding: str = "10px 20px",
    ) -> QPushButton:
        """Create a styled QPushButton.

        Args:
            text: Button label text
            style: ButtonStyle enum value
            icon: Optional icon prefix (emoji or text)
            bold: Whether text should be bold (default: True)
            padding: CSS padding value (default: "10px 20px")

        Returns:
            Styled QPushButton ready to use
        """
        label = f"{icon} {text}" if icon else text
        button = QPushButton(label.strip())

        normal_color, hover_color = cls._COLORS[style]
        text_color = cls._TEXT_COLORS[style]
        font_weight = "bold" if bold else "normal"

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {normal_color};
                color: {text_color};
                padding: {padding};
                font-weight: {font_weight};
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

        return button

    @classmethod
    def create_success_button(cls, text: str, icon: str = "✓") -> QPushButton:
        """Create a green success button (convenience method)."""
        return cls.create_button(text, ButtonStyle.SUCCESS, icon)

    @classmethod
    def create_danger_button(cls, text: str, icon: str = "✗") -> QPushButton:
        """Create a red danger button (convenience method)."""
        return cls.create_button(text, ButtonStyle.DANGER, icon)

    @classmethod
    def create_secondary_button(cls, text: str, icon: str = "") -> QPushButton:
        """Create a gray secondary button (convenience method)."""
        return cls.create_button(text, ButtonStyle.SECONDARY, icon, bold=False)
