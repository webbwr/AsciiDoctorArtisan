"""
Line Number Area Widget for AsciiDoc Editor

Provides line numbers alongside the QPlainTextEdit editor widget.
Implements specification requirement: Line Numbers (Editor Specifications).
"""

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QTextBlock
from PySide6.QtWidgets import QPlainTextEdit, QWidget


class LineNumberArea(QWidget):
    """
    Widget that displays line numbers for a QPlainTextEdit.

    This widget sits alongside the editor and shows line numbers
    for each visible line. It automatically updates when the editor
    is scrolled or text is added/removed.
    """

    def __init__(self, editor: QPlainTextEdit):
        """
        Initialize line number area.

        Args:
            editor: The QPlainTextEdit to show line numbers for
        """
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        """Return the recommended size for this widget."""
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """
        Paint line numbers.

        Args:
            event: Paint event
        """
        self.editor.line_number_area_paint_event(event)


class LineNumberMixin:
    """
    Mixin class to add line number functionality to QPlainTextEdit.

    Usage:
        class MyEditor(LineNumberMixin, QPlainTextEdit):
            def __init__(self):
                super().__init__()
                self.setup_line_numbers()
    """

    def setup_line_numbers(self):
        """Set up line number area and connect signals."""
        self.line_number_area = LineNumberArea(self)

        # Connect signals for auto-update
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        # Set initial width
        self.update_line_number_area_width(0)

    def line_number_area_width(self) -> int:
        """
        Calculate width needed for line numbers.

        Returns:
            Width in pixels for line number area
        """
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        # Width = 3px padding + digit width + 3px padding
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits + 3
        return space

    def update_line_number_area_width(self, _):
        """
        Update viewport margins to make room for line numbers.

        Args:
            _: Block count (unused, required by signal)
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect: QRect, dy: int):
        """
        Update line number area when editor scrolls or changes.

        Args:
            rect: Rectangle that needs updating
            dy: Vertical scroll offset
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """
        Handle resize events to reposition line number area.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        """
        Paint line numbers in the line number area.

        Args:
            event: Paint event
        """
        painter = QPainter(self.line_number_area)

        # Get colors based on current theme
        if self.palette().color(self.backgroundRole()).lightness() < 128:
            # Dark mode
            bg_color = QColor(53, 53, 53)  # Slightly lighter than editor
            text_color = QColor(180, 180, 180)  # Light gray
        else:
            # Light mode
            bg_color = QColor(240, 240, 240)  # Light gray
            text_color = QColor(100, 100, 100)  # Dark gray

        # Fill background
        painter.fillRect(event.rect(), bg_color)

        # Paint line numbers
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(text_color)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 3,  # 3px right padding
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class LineNumberPlainTextEdit(LineNumberMixin, QPlainTextEdit):
    """
    QPlainTextEdit with line numbers enabled.

    This is a ready-to-use QPlainTextEdit subclass that includes
    line numbers. Simply use this instead of QPlainTextEdit.

    Example:
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1\\nLine 2\\nLine 3")
    """

    def __init__(self, parent=None):
        """
        Initialize editor with line numbers.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_line_numbers()
