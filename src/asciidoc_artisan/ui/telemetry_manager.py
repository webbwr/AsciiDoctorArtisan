"""
Telemetry Manager - Handles telemetry lifecycle and user consent.

Extracted from main_window.py per MA principle (reduce file size).

Privacy-first telemetry with:
- Opt-in only (disabled by default)
- Local storage only (NO cloud upload)
- Anonymous session IDs
- GDPR compliance
- Easy opt-out anytime
"""

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class TelemetryManager:
    """
    Manages telemetry initialization, consent dialogs, and state toggling.

    MA principle: Extracted from main_window.py (116 lines → ~100 lines dedicated class).
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize TelemetryManager with reference to main editor."""
        self.editor = editor
        self.collector: Any = None  # TelemetryCollector, lazy-loaded

    def initialize(self, app_start_time: float | None = None) -> Any:
        """
        Initialize telemetry system.

        Shows opt-in dialog on first launch or initializes collector based on settings.

        Args:
            app_start_time: Application start time for tracking startup duration

        Returns:
            TelemetryCollector instance (enabled or disabled)
        """
        from asciidoc_artisan.core import TelemetryCollector

        settings = self.editor._settings

        # Show opt-in dialog on first launch (if not already shown)
        if not settings.telemetry_opt_in_shown:
            # Delay dialog to allow UI to fully initialize
            QTimer.singleShot(1000, self._show_opt_in_dialog)
            self.collector = TelemetryCollector(enabled=False)
            return self.collector

        # Initialize telemetry based on settings
        if settings.telemetry_enabled:
            self.collector = self._create_enabled_collector(app_start_time)
        else:
            self.collector = TelemetryCollector(enabled=False)
            logger.info("TelemetryCollector disabled (opt-in not accepted)")

        return self.collector

    def _create_enabled_collector(self, app_start_time: float | None = None) -> Any:
        """
        Create an enabled telemetry collector.

        Args:
            app_start_time: Application start time for tracking startup duration

        Returns:
            Enabled TelemetryCollector instance
        """
        from asciidoc_artisan.core import TelemetryCollector

        settings = self.editor._settings

        # Generate session ID if not exists
        if not settings.telemetry_session_id:
            settings.telemetry_session_id = str(uuid.uuid4())
            self.editor._settings_manager.save_settings(settings, self.editor)

        # Initialize collector
        collector = TelemetryCollector(enabled=True, session_id=settings.telemetry_session_id)

        # Track startup if time available
        if app_start_time:
            startup_time = time.time() - app_start_time
            collector.track_startup(startup_time)

        logger.info(f"TelemetryCollector initialized (session: {settings.telemetry_session_id[:8]}...)")
        return collector

    def _show_opt_in_dialog(self) -> None:
        """Show telemetry opt-in dialog (first launch only)."""
        from asciidoc_artisan.core import TelemetryCollector
        from asciidoc_artisan.ui.telemetry_opt_in_dialog import TelemetryOptInDialog

        dialog = TelemetryOptInDialog(self.editor)
        result = dialog.exec()

        if result == TelemetryOptInDialog.Result.ACCEPTED:
            self._handle_opt_in_accepted()
        elif result == TelemetryOptInDialog.Result.DECLINED:
            self._handle_opt_in_declined()
        else:
            # User wants to decide later - don't mark as shown
            self.collector = TelemetryCollector(enabled=False)
            logger.info("User deferred telemetry decision (first launch)")

    def _handle_opt_in_accepted(self) -> None:
        """Handle user accepting telemetry."""
        from asciidoc_artisan.core import TelemetryCollector

        settings = self.editor._settings
        settings.telemetry_enabled = True
        settings.telemetry_session_id = str(uuid.uuid4())
        settings.telemetry_opt_in_shown = True
        self.editor._settings_manager.save_settings(settings, self.editor)

        self.collector = TelemetryCollector(enabled=True, session_id=settings.telemetry_session_id)
        logger.info("User accepted telemetry (first launch)")

    def _handle_opt_in_declined(self) -> None:
        """Handle user declining telemetry."""
        from asciidoc_artisan.core import TelemetryCollector

        settings = self.editor._settings
        settings.telemetry_enabled = False
        settings.telemetry_opt_in_shown = True
        self.editor._settings_manager.save_settings(settings, self.editor)

        self.collector = TelemetryCollector(enabled=False)
        logger.info("User declined telemetry (first launch)")

    def toggle(self) -> None:
        """Toggle telemetry on/off."""
        from asciidoc_artisan.core import TelemetryCollector

        settings = self.editor._settings

        # Toggle the setting
        settings.telemetry_enabled = not settings.telemetry_enabled

        # Update menu item text to show current state
        self._update_menu_text()

        if settings.telemetry_enabled:
            # Generate session ID if not exists
            if not settings.telemetry_session_id:
                settings.telemetry_session_id = str(uuid.uuid4())

            # Reinitialize collector with new enabled state
            self.collector = TelemetryCollector(enabled=True, session_id=settings.telemetry_session_id)
            self.editor.status_manager.show_message("info", "Telemetry", "Telemetry enabled")
            logger.info("Telemetry enabled by user")
        else:
            # Disable telemetry
            self.collector = TelemetryCollector(enabled=False)
            self.editor.status_manager.show_message("info", "Telemetry", "Telemetry disabled")
            logger.info("Telemetry disabled by user")

        # Save settings
        self.editor._settings_manager.save_settings(settings, self.editor)

    def _update_menu_text(self) -> None:
        """Update the toggle telemetry menu item text to show current state with checkmark."""
        if hasattr(self.editor, "action_manager") and hasattr(self.editor.action_manager, "toggle_telemetry_act"):
            text = "✓ &Telemetry" if self.editor._settings.telemetry_enabled else "&Telemetry"
            self.editor.action_manager.toggle_telemetry_act.setText(text)
