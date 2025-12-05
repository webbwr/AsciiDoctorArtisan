"""
Focus Manager - Enhanced keyboard navigation and focus indicators.

Provides:
- Visible focus indicators on all interactive elements
- Logical tab order management
- Focus ring styling for accessibility
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QWidget

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Focus indicator styles
FOCUS_STYLE_LIGHT = """
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #0078d4;
        border-radius: 3px;
    }
    QPushButton:focus {
        border: 2px solid #0078d4;
        border-radius: 3px;
        outline: none;
    }
    QComboBox:focus {
        border: 2px solid #0078d4;
        border-radius: 3px;
    }
    QCheckBox:focus {
        outline: 2px solid #0078d4;
        outline-offset: 2px;
    }
"""

FOCUS_STYLE_DARK = """
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #4fc3f7;
        border-radius: 3px;
    }
    QPushButton:focus {
        border: 2px solid #4fc3f7;
        border-radius: 3px;
        outline: none;
    }
    QComboBox:focus {
        border: 2px solid #4fc3f7;
        border-radius: 3px;
    }
    QCheckBox:focus {
        outline: 2px solid #4fc3f7;
        outline-offset: 2px;
    }
"""


class FocusManager(QObject):
    """
    Manages focus indicators and keyboard navigation.

    Features:
    - Visible focus rings on interactive elements
    - Tab order optimization
    - Focus restoration after dialogs
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize focus manager."""
        super().__init__(editor)
        self.editor = editor
        self._last_focused_widget: QWidget | None = None
        self._setup_focus_tracking()

    def _setup_focus_tracking(self) -> None:
        """Set up focus change tracking."""
        app = QApplication.instance()
        if app:
            app.focusChanged.connect(self._on_focus_changed)

    def _on_focus_changed(self, old: QWidget | None, new: QWidget | None) -> None:
        """Track focus changes for restoration."""
        if new and self._is_main_widget(new):
            self._last_focused_widget = new

    def _is_main_widget(self, widget: QWidget) -> bool:
        """Check if widget is a main editing widget."""
        main_widgets = [
            self.editor.editor,
            self.editor.preview,
        ]
        if hasattr(self.editor, "chat_bar"):
            main_widgets.append(self.editor.chat_bar)
        return widget in main_widgets or widget.parent() in main_widgets

    def restore_focus(self) -> None:
        """Restore focus to last focused main widget."""
        if self._last_focused_widget and self._last_focused_widget.isVisible():
            self._last_focused_widget.setFocus()
        else:
            self.editor.editor.setFocus()

    def apply_focus_style(self, dark_mode: bool) -> str:
        """Get focus style for current theme."""
        return FOCUS_STYLE_DARK if dark_mode else FOCUS_STYLE_LIGHT

    def setup_tab_order(self) -> None:
        """Set up logical tab order for main widgets."""
        # Editor → Find Bar → Preview → Chat
        widgets = [self.editor.editor]

        if hasattr(self.editor, "find_bar") and self.editor.find_bar.isVisible():
            widgets.append(self.editor.find_bar)

        if hasattr(self.editor, "chat_bar") and self.editor.chat_bar.isVisible():
            widgets.append(self.editor.chat_bar)

        # Set tab order
        for i in range(len(widgets) - 1):
            QWidget.setTabOrder(widgets[i], widgets[i + 1])
