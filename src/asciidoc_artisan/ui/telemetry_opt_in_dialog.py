"""
Telemetry Opt-In Dialog - Privacy-First Analytics Consent.

This module provides a GDPR-compliant dialog for requesting user consent
to enable telemetry collection. Part of v1.8.0 Telemetry System.

Privacy Principles:
- Opt-in only (user must actively consent)
- Clear disclosure of what data is collected
- Transparent privacy policy
- Easy opt-out anytime
- No penalties for declining

GDPR Compliance:
- Informed consent (explains exactly what is collected)
- Freely given (no pressure to accept)
- Specific (clear purpose for data collection)
- Unambiguous (clear buttons, no dark patterns)
- Withdrawable (can disable in Settings anytime)
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from asciidoc_artisan.ui.dialog_factory import ButtonStyle, StyledButtonFactory

logger = logging.getLogger(__name__)


class TelemetryOptInDialog(QDialog):
    """GDPR-compliant dialog for telemetry opt-in consent.

    This dialog explains telemetry collection and requests user consent.
    Shown on first launch (or when user clicks "Remind Me Later").

    Privacy Features:
    - Clear explanation of what is collected
    - Transparent privacy policy
    - No dark patterns (equal emphasis on Accept/Decline)
    - "Remind Me Later" option
    - Can change decision anytime in Settings

    GDPR Compliance:
    - Informed consent
    - Freely given
    - Specific purpose
    - Unambiguous choice
    - Withdrawable consent

    Example:
        >>> dialog = TelemetryOptInDialog(parent)
        >>> result = dialog.exec()
        >>> if result == TelemetryOptInDialog.Result.ACCEPTED:
        ...     settings.telemetry_enabled = True
        ... elif result == TelemetryOptInDialog.Result.DECLINED:
        ...     settings.telemetry_enabled = False
        ... # Result.REMIND_LATER means user wants to decide later
    """

    # Dialog result codes
    class Result:
        """Dialog result codes."""

        ACCEPTED = QDialog.DialogCode.Accepted
        DECLINED = QDialog.DialogCode.Rejected
        REMIND_LATER = QDialog.DialogCode.Rejected + 1

    def __init__(self, parent: Any | None = None) -> None:
        """Initialize the Telemetry Opt-In Dialog.

        Args:
            parent: Parent widget (typically the main window)
        """
        super().__init__(parent)
        self.setWindowTitle("Help Improve AsciiDoc Artisan")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._result_code = self.Result.REMIND_LATER
        self._setup_ui()

    def _create_header(self) -> QLabel:
        """
        Create header label.

        Returns:
            Header QLabel with title and subtitle

        MA principle: Extracted from _setup_ui (4 lines).
        """
        header = QLabel("<h2>Help Improve AsciiDoc Artisan</h2><p>We would like your help to improve this app.</p>")
        header.setWordWrap(True)
        return header

    def _create_explanation_browser(self) -> QTextBrowser:
        """
        Create explanation text browser with telemetry information.

        MA principle: Reduced from 62→8 lines by extracting HTML content (87% reduction).

        Returns:
            QTextBrowser with HTML content explaining telemetry
        """
        explanation = QTextBrowser()
        explanation.setOpenExternalLinks(True)
        explanation.setHtml(self._get_telemetry_explanation_html())
        explanation.setMinimumHeight(300)
        return explanation

    def _get_telemetry_explanation_html(self) -> str:
        """
        MA principle: Extracted helper (52 lines) - focused HTML content.

        Get HTML content explaining telemetry features and privacy.

        Returns:
            HTML string with telemetry explanation
        """
        return """
            <h3>What is Telemetry?</h3>
            <p>Telemetry helps us see how you use the app. This lets us fix bugs
            and add features you want.</p>

            <h3>What We Collect</h3>
            <ul>
                <li><b>Feature usage</b> - Menu clicks, dialogs opened</li>
                <li><b>Error patterns</b> - Error types (NO personal data)</li>
                <li><b>Performance</b> - Startup time, render speed</li>
                <li><b>System info</b> - OS, Python version, GPU type</li>
            </ul>

            <h3>What We DO NOT Collect</h3>
            <ul>
                <li>❌ Your name, email, or IP address</li>
                <li>❌ Your document content or file paths</li>
                <li>❌ Keystrokes or typing patterns</li>
                <li>❌ Any personal information (PII)</li>
            </ul>

            <h3>Privacy Protections</h3>
            <ul>
                <li>🔒 <b>Local only</b> - Data stays on your computer</li>
                <li>🔒 <b>NO cloud upload</b> - Never sent to servers</li>
                <li>🔒 <b>Anonymous</b> - Uses random session IDs (UUIDs)</li>
                <li>🔒 <b>Auto-delete</b> - Removed after 30 days</li>
                <li>🔒 <b>Opt-out anytime</b> - Change in Settings</li>
            </ul>

            <h3>Where Is Data Stored?</h3>
            <p>All data is saved locally in:</p>
            <ul>
                <li><b>Linux:</b> <code>~/.config/AsciiDocArtisan/telemetry.json</code></li>
                <li><b>Windows:</b> <code>%APPDATA%/AsciiDocArtisan/telemetry.json</code></li>
                <li><b>macOS:</b> <code>~/Library/Application Support/AsciiDocArtisan/telemetry.json</code></li>
            </ul>
            <p><small>Max size: 10MB. Auto-rotated after 30 days.</small></p>

            <h3>Your Choice</h3>
            <p>Telemetry is <b>completely optional</b>. The app works the same
            whether you enable it or not. You can change your decision anytime in
            <b>Tools → Settings → Privacy</b>.</p>

            <p><small>This complies with GDPR (General Data Protection Regulation)
            for user privacy.</small></p>
            """

    def _create_accept_button(self) -> QPushButton:
        """Create accept telemetry button with green styling.

        Returns:
            Styled QPushButton for accepting telemetry (uses StyledButtonFactory)
        """
        btn = StyledButtonFactory.create_success_button("Enable Telemetry")
        btn.clicked.connect(self._accept_telemetry)
        return btn

    def _create_decline_button(self) -> QPushButton:
        """Create decline telemetry button with red styling.

        Returns:
            Styled QPushButton for declining telemetry (uses StyledButtonFactory)
        """
        btn = StyledButtonFactory.create_danger_button("No Thanks")
        btn.clicked.connect(self._decline_telemetry)
        return btn

    def _create_remind_button(self) -> QPushButton:
        """Create remind later button with neutral styling.

        Returns:
            Styled QPushButton for reminding later (uses StyledButtonFactory)
        """
        btn = StyledButtonFactory.create_button("Remind Me Later", ButtonStyle.SECONDARY, icon="⏰")
        btn.clicked.connect(self._remind_later)
        return btn

    def _create_privacy_note(self) -> QLabel:
        """
        Create privacy note label.

        Returns:
            QLabel with centered privacy note

        MA principle: Extracted from _setup_ui (8 lines).
        """
        privacy_note = QLabel(
            "<small><i>Privacy is important. All choices are respected. "
            "You can change your decision anytime in Settings.</i></small>"
        )
        privacy_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        privacy_note.setWordWrap(True)
        return privacy_note

    def _setup_ui(self) -> None:
        """
        Set up the dialog UI components.

        MA principle: Reduced from 131→25 lines by extracting 6 helper methods.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Add header and explanation
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_explanation_browser())

        # Create button box with all three options (equal emphasis)
        button_box = QDialogButtonBox()
        button_box.addButton(self._create_accept_button(), QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self._create_decline_button(), QDialogButtonBox.ButtonRole.RejectRole)
        button_box.addButton(self._create_remind_button(), QDialogButtonBox.ButtonRole.ActionRole)
        layout.addWidget(button_box)

        # Add privacy note
        layout.addWidget(self._create_privacy_note())

    def _accept_telemetry(self) -> None:
        """User accepted telemetry collection."""
        logger.info("User accepted telemetry collection")
        self._result_code = self.Result.ACCEPTED
        self.done(self.Result.ACCEPTED)

    def _decline_telemetry(self) -> None:
        """User declined telemetry collection."""
        logger.info("User declined telemetry collection")
        self._result_code = self.Result.DECLINED
        self.done(self.Result.DECLINED)

    def _remind_later(self) -> None:
        """User wants to decide later."""
        logger.info("User chose to decide on telemetry later")
        self._result_code = self.Result.REMIND_LATER
        self.done(self.Result.REMIND_LATER)

    def get_result(self) -> int:
        """Get the user's decision.

        Returns:
            Result code: ACCEPTED, DECLINED, or REMIND_LATER
        """
        return self._result_code
