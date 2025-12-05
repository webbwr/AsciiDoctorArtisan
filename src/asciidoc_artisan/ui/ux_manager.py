"""
UX Manager - Coordinates all UX enhancement features.

Integrates:
- Focus management and keyboard navigation
- Micro-animations for visual feedback
- F1 contextual help system
- Enhanced error messages
- Escape key chain handling
- Progress tracking with cancel

This is the central coordinator for S-tier UX features.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QKeyEvent

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

import logging

logger = logging.getLogger(__name__)


class UXManager(QObject):
    """
    Central coordinator for UX enhancements.

    Manages:
    - FocusManager: Focus indicators and tab order
    - MicroAnimations: Visual feedback animations
    - ContextualHelp: F1 help system
    - EnhancedErrorManager: User-friendly error dialogs
    - EscapeHandler: Escape key chain
    - ProgressTracker: Multi-stage progress
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize UX manager and all sub-managers."""
        super().__init__(editor)
        self.editor = editor
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all UX components."""
        if self._initialized:
            return

        # Import components
        from asciidoc_artisan.ui.contextual_help import ContextualHelp
        from asciidoc_artisan.ui.enhanced_errors import EnhancedErrorManager
        from asciidoc_artisan.ui.escape_handler import EscapeHandler
        from asciidoc_artisan.ui.focus_manager import FocusManager
        from asciidoc_artisan.ui.micro_animations import MicroAnimations
        from asciidoc_artisan.ui.progress_tracker import ProgressTracker

        # Initialize managers
        self.focus_manager = FocusManager(self.editor)
        self.animations = MicroAnimations(self.editor)
        self.contextual_help = ContextualHelp(self.editor)
        self.error_manager = EnhancedErrorManager(self.editor)
        self.escape_handler = EscapeHandler(self.editor)
        self.progress_tracker = ProgressTracker(self.editor)

        # Store references on editor for easy access
        self.editor.focus_manager = self.focus_manager
        self.editor.animations = self.animations
        self.editor.contextual_help = self.contextual_help
        self.editor.error_manager = self.error_manager
        self.editor.progress_tracker = self.progress_tracker

        # Install F1 key handler
        self._install_f1_handler()

        # Apply focus styles
        self._apply_focus_styles()

        self._initialized = True
        logger.info("UX Manager initialized with all S-tier features")

    def _install_f1_handler(self) -> None:
        """Install F1 key handler for contextual help."""
        # Override keyPressEvent on main window
        original_key_press = self.editor.keyPressEvent

        def enhanced_key_press(event: QKeyEvent) -> None:
            if event.key() == Qt.Key.Key_F1:
                self.contextual_help.show_help_for_widget()
                event.accept()
                return
            original_key_press(event)

        self.editor.keyPressEvent = enhanced_key_press  # type: ignore[method-assign]

    def _apply_focus_styles(self) -> None:
        """Apply focus indicator styles."""
        focus_style = self.focus_manager.apply_focus_style(self.editor._settings.dark_mode)
        current_style = self.editor.styleSheet()
        self.editor.setStyleSheet(current_style + focus_style)

    # === Convenience Methods ===

    def flash_success(self) -> None:
        """Flash green for success feedback."""
        self.animations.flash_success()

    def flash_error(self) -> None:
        """Flash red for error feedback."""
        self.animations.flash_error()

    def show_error(self, error_type: str, details: str = "") -> None:
        """Show enhanced error dialog."""
        self.error_manager.show_error(error_type, details)

    def show_help(self) -> None:
        """Show contextual help for focused widget."""
        self.contextual_help.show_help_for_widget()

    def start_progress(
        self,
        title: str,
        stages: list[str],
        cancellable: bool = True,
    ) -> None:
        """Start progress tracking dialog."""
        self.progress_tracker.start_operation(title, stages, cancellable)

    def update_progress(self, value: int, detail: str = "") -> None:
        """Update progress value."""
        self.progress_tracker.update_progress(value, detail)

    def complete_progress(self, message: str = "Complete") -> None:
        """Complete progress tracking."""
        self.progress_tracker.complete(message)

    def restore_focus(self) -> None:
        """Restore focus to last focused widget."""
        self.focus_manager.restore_focus()


def create_ux_manager(editor: "AsciiDocEditor") -> UXManager:
    """Factory function to create and initialize UX manager."""
    manager = UXManager(editor)
    manager.initialize()
    return manager
