"""
Escape Handler - Manages escape key chain for closing UI elements.

Provides:
- Escape closes dialogs → popups → find bar → returns to editor
- Consistent escape behavior across application
- Focus restoration after closing
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QApplication, QDialog

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor


class EscapeHandler(QObject):
    """
    Manages escape key chain for consistent UI dismissal.

    Escape key priority:
    1. Close any open dialog
    2. Close autocomplete popup
    3. Close find bar
    4. Close quick commit
    5. Return focus to editor
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize escape handler."""
        super().__init__(editor)
        self.editor = editor
        self._install_filter()

    def _install_filter(self) -> None:
        """Install event filter on application."""
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filter escape key events."""
        if event.type() == QEvent.Type.KeyPress:
            from PySide6.QtGui import QKeyEvent

            key_event = event
            if isinstance(key_event, QKeyEvent) and key_event.key() == Qt.Key.Key_Escape:
                if self._handle_escape():
                    return True  # Event handled
        return super().eventFilter(obj, event)

    def _handle_escape(self) -> bool:
        """
        Handle escape key press with priority chain.

        Returns:
            True if escape was handled, False to propagate
        """
        # 1. Check for open dialogs (let them handle their own escape)
        active_modal = QApplication.activeModalWidget()
        if active_modal and isinstance(active_modal, QDialog):
            return False  # Let dialog handle it

        # 2. Close autocomplete popup
        if hasattr(self.editor, "autocomplete_manager"):
            if self.editor.autocomplete_manager.is_popup_visible():
                self.editor.autocomplete_manager.hide_popup()
                return True

        # 3. Close find bar
        if hasattr(self.editor, "find_bar") and self.editor.find_bar.isVisible():
            self.editor.find_bar.hide()
            self.editor.editor.setFocus()
            return True

        # 4. Close quick commit
        if hasattr(self.editor, "quick_commit_widget") and self.editor.quick_commit_widget.isVisible():
            self.editor.quick_commit_widget.hide()
            self.editor.editor.setFocus()
            return True

        # 5. Clear selection in editor
        cursor = self.editor.editor.textCursor()
        if cursor.hasSelection():
            cursor.clearSelection()
            self.editor.editor.setTextCursor(cursor)
            return True

        # 6. Focus editor if not focused
        if not self.editor.editor.hasFocus():
            self.editor.editor.setFocus()
            return True

        return False
