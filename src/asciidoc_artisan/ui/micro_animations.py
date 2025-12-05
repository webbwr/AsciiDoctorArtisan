"""
Micro-Animations - Subtle visual feedback for user actions.

Provides:
- Flash indicators for save success/failure
- Shake animation for errors
- Fade transitions for state changes
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor


class FlashOverlay(QWidget):
    """Transparent overlay for flash effects."""

    def __init__(self, parent: QWidget) -> None:
        """Initialize flash overlay."""
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._opacity = 0.0
        self._color = QColor(74, 222, 128, 100)  # Green
        self.hide()

    def get_opacity(self) -> float:
        """Get current opacity."""
        return self._opacity

    def set_opacity(self, value: float) -> None:
        """Set opacity and update."""
        self._opacity = value
        self.update()

    opacity = Property(float, get_opacity, set_opacity)

    def set_color(self, color: QColor) -> None:
        """Set flash color."""
        self._color = color

    def paintEvent(self, event: object) -> None:
        """Paint the flash overlay."""
        from PySide6.QtGui import QPainter

        if self._opacity > 0:
            painter = QPainter(self)
            color = QColor(self._color)
            color.setAlphaF(self._opacity * 0.3)
            painter.fillRect(self.rect(), color)


class MicroAnimations(QObject):
    """
    Provides micro-animations for visual feedback.

    Features:
    - Flash on save (green for success, red for error)
    - Shake animation for validation errors
    - Smooth fade transitions
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize micro-animations manager."""
        super().__init__(editor)
        self.editor = editor
        self._flash_overlay: FlashOverlay | None = None
        self._shake_animations: dict[int, QPropertyAnimation] = {}

    def _ensure_flash_overlay(self) -> FlashOverlay:
        """Create flash overlay if needed."""
        if self._flash_overlay is None:
            self._flash_overlay = FlashOverlay(self.editor)
        return self._flash_overlay

    def flash_success(self, duration: int = 300) -> None:
        """Flash green to indicate success."""
        self._flash(QColor(74, 222, 128), duration)

    def flash_error(self, duration: int = 400) -> None:
        """Flash red to indicate error."""
        self._flash(QColor(239, 68, 68), duration)

    def flash_warning(self, duration: int = 350) -> None:
        """Flash yellow to indicate warning."""
        self._flash(QColor(251, 191, 36), duration)

    def _flash(self, color: QColor, duration: int) -> None:
        """Perform flash animation."""
        overlay = self._ensure_flash_overlay()
        overlay.set_color(color)
        overlay.setGeometry(self.editor.editor.geometry())
        overlay.show()
        overlay.raise_()

        # Animate opacity: 0 → 1 → 0
        anim = QPropertyAnimation(overlay, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setKeyValueAt(0.3, 1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.finished.connect(overlay.hide)
        anim.start()

    def shake_widget(self, widget: QWidget, amplitude: int = 5, duration: int = 300) -> None:
        """Shake a widget to indicate error."""
        widget_id = id(widget)

        # Stop existing animation
        if widget_id in self._shake_animations:
            self._shake_animations[widget_id].stop()

        original_pos = widget.pos()

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Create shake keyframes
        from PySide6.QtCore import QPoint

        anim.setStartValue(original_pos)
        anim.setKeyValueAt(0.1, original_pos + QPoint(amplitude, 0))
        anim.setKeyValueAt(0.2, original_pos + QPoint(-amplitude, 0))
        anim.setKeyValueAt(0.3, original_pos + QPoint(amplitude, 0))
        anim.setKeyValueAt(0.4, original_pos + QPoint(-amplitude, 0))
        anim.setKeyValueAt(0.5, original_pos + QPoint(amplitude // 2, 0))
        anim.setKeyValueAt(0.6, original_pos + QPoint(-amplitude // 2, 0))
        anim.setEndValue(original_pos)

        self._shake_animations[widget_id] = anim
        anim.finished.connect(lambda: self._cleanup_shake(widget_id))
        anim.start()

    def _cleanup_shake(self, widget_id: int) -> None:
        """Clean up shake animation."""
        if widget_id in self._shake_animations:
            del self._shake_animations[widget_id]

    def pulse_widget(self, widget: QWidget, duration: int = 500) -> None:
        """Pulse widget opacity to draw attention."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setKeyValueAt(0.5, 0.5)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(lambda: self._clear_graphics_effect(widget))
        anim.start()

    def _clear_graphics_effect(self, widget: QWidget) -> None:
        """Clear graphics effect from widget."""
        # Use deleteLater on the effect instead of setting to None
        current_effect = widget.graphicsEffect()
        if current_effect:
            current_effect.deleteLater()
        widget.setGraphicsEffect(QGraphicsOpacityEffect())  # Reset with new effect
        widget.graphicsEffect().deleteLater()  # Then remove it
