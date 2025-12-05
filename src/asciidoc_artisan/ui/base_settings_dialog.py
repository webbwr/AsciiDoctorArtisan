"""
Base Settings Dialog - Common structure for settings dialogs.

Provides:
- BaseSettingsDialog class with standard layout
- Header, content, and button sections
"""

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from asciidoc_artisan.ui.style_constants import Colors, Fonts


class BaseSettingsDialog(QDialog):
    """Base class for settings dialogs with common structure.

    MA principle: Eliminates duplicate code across settings dialogs.
    Provides consistent structure:
    - Window title and minimum width
    - Optional header section
    - Settings content (implemented by subclass)
    - OK/Cancel buttons

    Subclasses should override:
    - _get_title(): Return window title
    - _get_header_text(): Return (title, description) tuple or None
    - _create_content(layout): Add settings widgets to layout

    Example:
        class MySettingsDialog(BaseSettingsDialog):
            def _get_title(self) -> str:
                return "My Settings"

            def _get_header_text(self) -> tuple[str, str] | None:
                return ("Configure Settings", "Adjust these options to customize behavior.")

            def _create_content(self, layout: QVBoxLayout) -> None:
                layout.addWidget(self.my_checkbox)
    """

    def __init__(self, parent: QWidget | None = None, min_width: int = 500) -> None:
        """Initialize base settings dialog.

        Args:
            parent: Parent widget (optional)
            min_width: Minimum dialog width (default: 500)
        """
        super().__init__(parent)
        self._min_width = min_width
        self._init_base_ui()

    def _get_title(self) -> str:
        """Return window title. Override in subclass."""
        return "Settings"

    def _get_header_text(self) -> tuple[str, str] | None:
        """Return header (title, description) tuple or None to skip header.

        Override in subclass to customize header.
        """
        return None

    def _create_content(self, layout: QVBoxLayout) -> None:
        """Add settings widgets to layout. Override in subclass."""
        pass

    def _init_base_ui(self) -> None:
        """Initialize the common UI structure."""
        from asciidoc_artisan.ui.dialog_factory import DialogFactory

        self.setWindowTitle(self._get_title())
        self.setMinimumWidth(self._min_width)

        layout = QVBoxLayout(self)

        # Optional header section
        header = self._get_header_text()
        if header:
            self._add_header(layout, header[0], header[1])

        # Subclass content
        self._create_content(layout)

        # Dialog buttons
        layout.addLayout(DialogFactory.create_ok_cancel_layout(self))

    def _add_header(self, layout: QVBoxLayout, title: str, description: str) -> None:
        """Add styled header section to layout."""
        header_label = QLabel(title)
        header_label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_HEADER} }}")
        layout.addWidget(header_label)

        if description:
            info_label = QLabel(description)
            info_label.setWordWrap(True)
            info_label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_INFO} }}")
            layout.addWidget(info_label)

    def create_info_label(self, text: str) -> QLabel:
        """Create an info/help label with standard styling.

        Args:
            text: Information text to display

        Returns:
            Styled QLabel
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_INFO} }}")
        return label

    def create_status_label(self, text: str, status: str = "normal") -> QLabel:
        """Create a status label with color based on status.

        Args:
            text: Status text to display
            status: One of "success", "warning", "error", "normal"

        Returns:
            Styled QLabel
        """
        label = QLabel(text)
        colors = {
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.DANGER,
            "normal": Colors.TEXT_MUTED,
        }
        color = colors.get(status, Colors.TEXT_MUTED)
        label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 10pt; }}")
        return label
