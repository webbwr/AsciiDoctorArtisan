"""
Settings Dialog Helper - Creates and manages settings dialogs.

Extracted from main_window.py to reduce class size (MA principle).
Handles autocomplete and syntax checking settings dialogs.
"""

import logging
from typing import Any, Protocol

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.ui.dialog_factory import DialogFactory

logger = logging.getLogger(__name__)


class SettingsContext(Protocol):
    """Protocol for settings dialog context (avoid circular imports)."""

    _settings: Any
    autocomplete_manager: Any
    syntax_checker_manager: Any

    def __getattr__(self, name: str) -> Any:  # pragma: no cover
        """Allow access to any attribute."""
        ...


class SettingsDialogHelper:
    """
    Settings dialog creation helper.

    This class was extracted from AsciiDocEditor to reduce class size
    per MA principle (~170 lines extracted).

    Handles:
    - Dialog creation with standard layout
    - Autocomplete settings dialog
    - Syntax checking settings dialog
    """

    def __init__(self, parent: QWidget, ctx: SettingsContext) -> None:
        """
        Initialize settings dialog helper.

        Args:
            parent: Parent widget for dialogs
            ctx: Context providing settings and managers
        """
        self.parent = parent
        self.ctx = ctx

    def create_settings_dialog(self, title: str) -> tuple[QDialog, QVBoxLayout, QFormLayout]:
        """
        Create settings dialog with standard layout.

        Delegates to DialogFactory (MA principle).

        Args:
            title: Dialog window title

        Returns:
            Tuple of (dialog, layout, form)
        """
        return DialogFactory.create_form_dialog(title, self.parent)

    def add_help_label(self, layout: QVBoxLayout, help_text: str) -> None:
        """
        Add help text label to dialog layout.

        Delegates to DialogFactory (MA principle).

        Args:
            layout: QVBoxLayout to add label to
            help_text: Help text content
        """
        layout.addWidget(DialogFactory.create_help_label(help_text))

    def add_dialog_buttons(self, layout: QVBoxLayout, dialog: QDialog) -> None:
        """
        Add OK/Cancel buttons to dialog.

        Delegates to DialogFactory (MA principle).

        Args:
            layout: QVBoxLayout to add buttons to
            dialog: QDialog to connect accept/reject signals
        """
        DialogFactory.add_buttons_to_dialog(dialog, layout)

    def show_autocomplete_settings(self) -> None:
        """
        Show auto-complete settings dialog (v2.0.0).

        Allows user to configure:
        - Enable/disable auto-complete
        - Debounce delay (100-1000ms)
        - Minimum characters to trigger (1-5)
        """
        dialog, layout, form = self.create_settings_dialog("Auto-Complete Settings")

        # Form controls
        enabled_cb = QCheckBox()
        enabled_cb.setChecked(self.ctx.autocomplete_manager.enabled)
        form.addRow("&Enabled:", enabled_cb)

        delay_spin = QSpinBox()
        delay_spin.setRange(100, 1000)
        delay_spin.setValue(self.ctx.autocomplete_manager.auto_delay)
        delay_spin.setSuffix(" ms")
        form.addRow("&Delay:", delay_spin)

        min_chars_spin = QSpinBox()
        min_chars_spin.setRange(1, 5)
        min_chars_spin.setValue(self.ctx.autocomplete_manager.min_chars)
        form.addRow("&Min Characters:", min_chars_spin)

        layout.addLayout(form)

        self.add_help_label(
            layout,
            "Delay: Time to wait after typing before showing suggestions\n"
            "Min Characters: Minimum characters needed to trigger auto-complete",
        )
        self.add_dialog_buttons(layout, dialog)

        if dialog.exec():
            self.ctx.autocomplete_manager.enabled = enabled_cb.isChecked()
            self.ctx.autocomplete_manager.auto_delay = delay_spin.value()
            self.ctx.autocomplete_manager.min_chars = min_chars_spin.value()

            self.ctx._settings.autocomplete_enabled = enabled_cb.isChecked()
            self.ctx._settings.autocomplete_delay = delay_spin.value()
            self.ctx._settings.autocomplete_min_chars = min_chars_spin.value()
            self.ctx._settings.save()

            logger.info(
                f"Auto-complete settings updated: enabled={enabled_cb.isChecked()}, "
                f"delay={delay_spin.value()}ms, min_chars={min_chars_spin.value()}"
            )

    def show_syntax_check_settings(self) -> None:
        """
        Show syntax checking settings dialog (v2.0.0).

        Allows user to configure:
        - Enable/disable syntax checking
        - Check delay (100-2000ms)
        - Show/hide error underlines
        """
        dialog, layout, form = self.create_settings_dialog("Syntax Checking Settings")

        # Form controls
        enabled_cb = QCheckBox()
        enabled_cb.setChecked(self.ctx.syntax_checker_manager.enabled)
        form.addRow("&Enabled:", enabled_cb)

        delay_spin = QSpinBox()
        delay_spin.setRange(100, 2000)
        delay_spin.setValue(self.ctx.syntax_checker_manager.check_delay)
        delay_spin.setSuffix(" ms")
        form.addRow("&Check Delay:", delay_spin)

        underlines_cb = QCheckBox()
        underlines_cb.setChecked(self.ctx.syntax_checker_manager.show_underlines)
        form.addRow("&Show Underlines:", underlines_cb)

        layout.addLayout(form)

        self.add_help_label(
            layout,
            "Check Delay: Time to wait after typing before checking syntax\n"
            "Show Underlines: Display red squiggly lines under errors",
        )
        self.add_dialog_buttons(layout, dialog)

        if dialog.exec():
            self.ctx.syntax_checker_manager.enabled = enabled_cb.isChecked()
            self.ctx.syntax_checker_manager.check_delay = delay_spin.value()
            self.ctx.syntax_checker_manager.show_underlines = underlines_cb.isChecked()

            self.ctx._settings.syntax_check_realtime_enabled = enabled_cb.isChecked()
            self.ctx._settings.syntax_check_delay = delay_spin.value()
            self.ctx._settings.syntax_check_show_underlines = underlines_cb.isChecked()
            self.ctx._settings.save()

            logger.info(
                f"Syntax checking settings updated: enabled={enabled_cb.isChecked()}, "
                f"delay={delay_spin.value()}ms, underlines={underlines_cb.isChecked()}"
            )
