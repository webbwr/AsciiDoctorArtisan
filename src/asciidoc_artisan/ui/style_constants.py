"""
Style Constants - Centralized UI styling values (MA principle extraction).

This module provides a single source of truth for colors, fonts, and spacing
used across the UI. Eliminates hardcoded values scattered throughout dialogs,
widgets, and managers.

Categories:
- COLORS: Bootstrap-inspired semantic colors (success, danger, warning, etc.)
- THEME: Dark/light mode color schemes
- FONTS: Font families, sizes, and weights
- SPACING: Padding, margins, and border radius values
- HIGHLIGHTS: Editor/preview highlight colors

Example:
    from asciidoc_artisan.ui.style_constants import Colors, Fonts, Spacing

    button.setStyleSheet(f'''
        background-color: {Colors.SUCCESS};
        font-size: {Fonts.SIZE_NORMAL}pt;
        padding: {Spacing.BUTTON_PADDING};
    ''')
"""

from dataclasses import dataclass
from typing import NamedTuple

# === SEMANTIC COLORS (Bootstrap-inspired) ===


class ColorPair(NamedTuple):
    """Color pair for normal and hover states."""

    normal: str
    hover: str


@dataclass(frozen=True)
class Colors:
    """Semantic color palette for consistent UI theming.

    All colors follow Bootstrap 5 conventions for familiarity.
    """

    # Primary actions (blue)
    PRIMARY = "#007bff"
    PRIMARY_HOVER = "#0069d9"

    # Success/positive actions (green)
    SUCCESS = "#28a745"
    SUCCESS_HOVER = "#218838"

    # Danger/destructive actions (red)
    DANGER = "#dc3545"
    DANGER_HOVER = "#c82333"

    # Warning/caution (yellow)
    WARNING = "#ffc107"
    WARNING_HOVER = "#e0a800"
    WARNING_TEXT = "#212529"  # Dark text for yellow background

    # Secondary/neutral (gray)
    SECONDARY = "#6c757d"
    SECONDARY_HOVER = "#5a6268"

    # Info (light blue)
    INFO = "#17a2b8"
    INFO_HOVER = "#138496"

    # Text colors
    TEXT_LIGHT = "#ffffff"
    TEXT_DARK = "#212529"
    TEXT_MUTED = "#6c757d"
    TEXT_GRAY = "gray"

    # Pairs for button factory
    BUTTON_PAIRS = {
        "success": ColorPair(SUCCESS, SUCCESS_HOVER),
        "danger": ColorPair(DANGER, DANGER_HOVER),
        "warning": ColorPair(WARNING, WARNING_HOVER),
        "primary": ColorPair(PRIMARY, PRIMARY_HOVER),
        "secondary": ColorPair(SECONDARY, SECONDARY_HOVER),
        "info": ColorPair(INFO, INFO_HOVER),
    }


# === THEME COLORS ===


@dataclass(frozen=True)
class DarkTheme:
    """Dark theme color scheme."""

    # Backgrounds
    BG_PRIMARY = "#1e1e1e"
    BG_SECONDARY = "#2a2a2a"
    BG_TERTIARY = "#2b2b2b"
    BG_INPUT = "#3c3c3c"

    # Text
    TEXT_PRIMARY = "#dcdcdc"
    TEXT_SECONDARY = "#e0e0e0"
    TEXT_MUTED = "#a0a0a0"
    TEXT_HEADING = "#ececec"

    # Links
    LINK = "#80d0ff"

    # Borders
    BORDER = "#3c3c3c"

    # Code blocks
    CODE_BG = "#2a2a2a"
    CODE_TEXT = "#f0f0f0"

    # Admonition blocks
    NOTE_BG = "#1e3a5f"
    NOTE_BORDER = "#4a90e2"
    TIP_BG = "#1e4d2b"
    TIP_BORDER = "#5cb85c"
    WARNING_BG = "#5d4037"
    WARNING_BORDER = "#ff9800"
    CAUTION_BG = "#5d4037"
    CAUTION_BORDER = "#f44336"
    IMPORTANT_BG = "#4a148c"
    IMPORTANT_BORDER = "#9c27b0"

    # Error display
    ERROR_BG = "#3a2a1a"
    ERROR_TEXT = "#ffcc99"
    ERROR_HEADING = "#ff6666"
    ERROR_PRE_BG = "#2a2a2a"


@dataclass(frozen=True)
class LightTheme:
    """Light theme color scheme."""

    # Backgrounds
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8f8f8"
    BG_TERTIARY = "#f5f5f5"
    BG_INPUT = "#f0f0f0"

    # Text
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#000000"
    TEXT_MUTED = "#666666"
    TEXT_HEADING = "#111111"

    # Links
    LINK = "#007bff"

    # Borders
    BORDER = "#e1e4e8"

    # Code blocks
    CODE_BG = "#f8f8f8"
    CODE_TEXT = "#333333"

    # Admonition blocks
    NOTE_BG = "#e3f2fd"
    NOTE_BORDER = "#2196f3"
    TIP_BG = "#e8f5e9"
    TIP_BORDER = "#4caf50"
    WARNING_BG = "#fff3e0"
    WARNING_BORDER = "#ff9800"
    CAUTION_BG = "#ffebee"
    CAUTION_BORDER = "#f44336"
    IMPORTANT_BG = "#f3e5f5"
    IMPORTANT_BORDER = "#9c27b0"

    # Error display
    ERROR_BG = "#fff3cd"
    ERROR_TEXT = "#856404"
    ERROR_HEADING = "#dc3545"
    ERROR_PRE_BG = "#f8f9fa"


# === HIGHLIGHT COLORS ===


@dataclass(frozen=True)
class HighlightColors:
    """Highlight colors for editor and preview sync."""

    # Separator
    SEPARATOR_BG = "rgba(128, 128, 128, 0.1)"

    # Editor highlights (green tint)
    EDITOR_ADD = "rgba(74, 222, 128, 0.2)"
    EDITOR_ADD_HOVER = "rgba(74, 222, 128, 0.3)"

    # Preview highlights (blue tint)
    PREVIEW_ADD = "rgba(74, 158, 255, 0.2)"
    PREVIEW_ADD_HOVER = "rgba(74, 158, 255, 0.3)"
    PREVIEW_BORDER = "rgba(74, 158, 255, 0.5)"

    # Chat toolbar
    CHAT_ACCENT = "#ff9800"
    CHAT_BG = "rgba(255, 152, 0, 0.2)"


# === FONTS ===


@dataclass(frozen=True)
class Fonts:
    """Font families and sizes for consistent typography."""

    # Font families
    FAMILY_SANS = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    FAMILY_MONO = "'Courier New', Courier, monospace"
    FAMILY_SYSTEM = "Arial, sans-serif"

    # Font sizes (in pt)
    SIZE_TINY = 9
    SIZE_SMALL = 10
    SIZE_NORMAL = 11
    SIZE_MEDIUM = 12
    SIZE_LARGE = 14
    SIZE_XLARGE = 16
    SIZE_HEADING3 = 16
    SIZE_HEADING2 = 20
    SIZE_HEADING1 = 24

    # Font weights
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"

    # CSS snippets for common styles
    STYLE_MUTED = "color: gray; font-size: 10px;"
    STYLE_MUTED_PT = "color: gray; font-size: 10pt;"
    STYLE_REQUIRED = "color: gray; font-size: 9pt;"
    STYLE_HEADER = "font-size: 14pt; font-weight: bold;"
    STYLE_INFO = "color: gray; font-size: 10pt;"


# === SPACING ===


@dataclass(frozen=True)
class Spacing:
    """Consistent spacing values for padding, margins, and borders."""

    # Padding
    NONE = "0"
    TINY = "2px"
    SMALL = "5px"
    NORMAL = "10px"
    MEDIUM = "15px"
    LARGE = "20px"

    # Button padding
    BUTTON_PADDING = "10px 20px"
    BUTTON_PADDING_SMALL = "5px 10px"
    BUTTON_PADDING_LARGE = "15px 30px"

    # Code padding
    CODE_PADDING_INLINE = "2px 6px"
    CODE_PADDING_BLOCK = "15px"

    # Border radius
    RADIUS_SMALL = "3px"
    RADIUS_NORMAL = "5px"
    RADIUS_LARGE = "8px"

    # Margins
    MARGIN_HEADING_TOP = "1.5em"
    MARGIN_HEADING_BOTTOM = "0.5em"

    # Line height
    LINE_HEIGHT = "1.6"


# === DIALOG DIMENSIONS ===


@dataclass(frozen=True)
class DialogSize:
    """Standard dialog dimensions."""

    MIN_WIDTH_SMALL = 300
    MIN_WIDTH_NORMAL = 400
    MIN_WIDTH_LARGE = 600
    MIN_WIDTH_XLARGE = 800

    MIN_HEIGHT_SMALL = 200
    MIN_HEIGHT_NORMAL = 300
    MIN_HEIGHT_LARGE = 500


# === CSS TEMPLATES ===


class CSSTemplates:
    """Pre-built CSS template strings for common patterns."""

    @staticmethod
    def button(bg: str, hover: str, text: str = "white", padding: str = Spacing.BUTTON_PADDING) -> str:
        """Generate button stylesheet."""
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                padding: {padding};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

    @staticmethod
    def success_button() -> str:
        """Green success button stylesheet."""
        return CSSTemplates.button(Colors.SUCCESS, Colors.SUCCESS_HOVER)

    @staticmethod
    def danger_button() -> str:
        """Red danger button stylesheet."""
        return CSSTemplates.button(Colors.DANGER, Colors.DANGER_HOVER)

    @staticmethod
    def warning_button() -> str:
        """Yellow warning button stylesheet."""
        return CSSTemplates.button(Colors.WARNING, Colors.WARNING_HOVER, Colors.WARNING_TEXT)

    @staticmethod
    def primary_button() -> str:
        """Blue primary button stylesheet."""
        return CSSTemplates.button(Colors.PRIMARY, Colors.PRIMARY_HOVER)

    @staticmethod
    def secondary_button() -> str:
        """Gray secondary button stylesheet."""
        return CSSTemplates.button(Colors.SECONDARY, Colors.SECONDARY_HOVER)
