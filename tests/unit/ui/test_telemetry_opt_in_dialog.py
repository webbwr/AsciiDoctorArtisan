"""
Tests for ui.telemetry_opt_in_dialog module.

Tests GDPR-compliant telemetry consent dialog including:
- Dialog initialization and properties
- Result code constants
- UI components and layout
- Button handlers (Accept, Decline, Remind Later)
- Privacy-first messaging
"""

from unittest.mock import Mock, patch

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QTextBrowser

from asciidoc_artisan.ui.telemetry_opt_in_dialog import TelemetryOptInDialog


class TestTelemetryOptInDialogInitialization:
    """Test TelemetryOptInDialog initialization."""

    def test_initialization_without_parent(self, qapp):
        """Test dialog initializes without parent."""
        dialog = TelemetryOptInDialog()

        assert dialog is not None
        assert isinstance(dialog, QDialog)

    def test_initialization_with_parent(self, qapp):
        """Test dialog initializes with parent widget."""
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        dialog = TelemetryOptInDialog(parent)

        assert dialog.parent() is parent

    def test_window_title(self, qapp):
        """Test dialog has correct window title."""
        dialog = TelemetryOptInDialog()

        assert dialog.windowTitle() == "Help Improve AsciiDoc Artisan"

    def test_modal_dialog(self, qapp):
        """Test dialog is modal."""
        dialog = TelemetryOptInDialog()

        assert dialog.isModal() is True

    def test_minimum_size(self, qapp):
        """Test dialog has minimum size set."""
        dialog = TelemetryOptInDialog()

        assert dialog.minimumWidth() == 600
        assert dialog.minimumHeight() == 500

    def test_initial_result_code(self, qapp):
        """Test initial result code is REMIND_LATER."""
        dialog = TelemetryOptInDialog()

        assert dialog.get_result() == TelemetryOptInDialog.Result.REMIND_LATER


class TestResultCodes:
    """Test Result class constants."""

    def test_accepted_result_code(self):
        """Test ACCEPTED result code."""
        assert TelemetryOptInDialog.Result.ACCEPTED == QDialog.DialogCode.Accepted

    def test_declined_result_code(self):
        """Test DECLINED result code."""
        assert TelemetryOptInDialog.Result.DECLINED == QDialog.DialogCode.Rejected

    def test_remind_later_result_code(self):
        """Test REMIND_LATER result code."""
        assert (
            TelemetryOptInDialog.Result.REMIND_LATER == QDialog.DialogCode.Rejected + 1
        )


class TestUIComponents:
    """Test UI components are created correctly."""

    def test_has_header_label(self, qapp):
        """Test dialog has header label."""
        dialog = TelemetryOptInDialog()

        # Find header label
        labels = dialog.findChildren(QLabel)
        assert len(labels) > 0

        # Check header text contains title
        header_found = any(
            "Help Improve AsciiDoc Artisan" in label.text() for label in labels
        )
        assert header_found

    def test_has_explanation_text_browser(self, qapp):
        """Test dialog has explanation text browser."""
        dialog = TelemetryOptInDialog()

        text_browsers = dialog.findChildren(QTextBrowser)
        assert len(text_browsers) == 1

        explanation = text_browsers[0]
        assert explanation.openExternalLinks() is True

    def test_explanation_contains_telemetry_info(self, qapp):
        """Test explanation contains telemetry information."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        # Check for key sections
        assert "What is Telemetry?" in html
        assert "What We Collect" in html
        assert "What We DO NOT Collect" in html
        assert "Privacy Protections" in html

    def test_explanation_contains_data_collected(self, qapp):
        """Test explanation lists data that IS collected."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        # Check for specific data types collected
        assert "Feature usage" in html
        assert "Error patterns" in html
        assert "Performance" in html
        assert "System info" in html

    def test_explanation_contains_data_not_collected(self, qapp):
        """Test explanation lists data that is NOT collected."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        # Check for privacy protections
        assert "name" in html or "email" in html or "IP address" in html
        assert "document content" in html or "file paths" in html
        assert "Keystrokes" in html or "typing patterns" in html
        assert "personal information" in html or "PII" in html

    def test_explanation_contains_storage_locations(self, qapp):
        """Test explanation shows where data is stored."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        # Check for platform-specific paths
        assert "Linux:" in html
        assert "Windows:" in html
        assert "macOS:" in html
        assert "telemetry.json" in html

    def test_explanation_mentions_gdpr(self, qapp):
        """Test explanation mentions GDPR compliance."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        assert "GDPR" in html or "General Data Protection Regulation" in html

    def test_has_three_buttons(self, qapp):
        """Test dialog has three buttons."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        assert len(buttons) == 3

    def test_accept_button_exists(self, qapp):
        """Test Accept button exists with correct text."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        accept_button = [b for b in buttons if "Enable" in b.text()]

        assert len(accept_button) == 1
        assert "Telemetry" in accept_button[0].text()

    def test_decline_button_exists(self, qapp):
        """Test Decline button exists with correct text."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        decline_button = [b for b in buttons if "No Thanks" in b.text()]

        assert len(decline_button) == 1

    def test_remind_later_button_exists(self, qapp):
        """Test Remind Later button exists with correct text."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        remind_button = [b for b in buttons if "Remind" in b.text()]

        assert len(remind_button) == 1
        assert "Later" in remind_button[0].text()

    def test_has_privacy_note_label(self, qapp):
        """Test dialog has privacy note at bottom."""
        dialog = TelemetryOptInDialog()

        labels = dialog.findChildren(QLabel)
        privacy_note = [
            label for label in labels if "Privacy is important" in label.text()
        ]

        assert len(privacy_note) == 1
        assert "Settings" in privacy_note[0].text()


class TestButtonHandlers:
    """Test button click handlers."""

    def test_accept_button_sets_result(self, qapp):
        """Test Accept button sets result to ACCEPTED."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        accept_button = [b for b in buttons if "Enable" in b.text()][0]

        # Mock done method to prevent dialog from closing
        dialog.done = Mock()

        accept_button.click()

        assert dialog.get_result() == TelemetryOptInDialog.Result.ACCEPTED
        dialog.done.assert_called_once_with(TelemetryOptInDialog.Result.ACCEPTED)

    def test_decline_button_sets_result(self, qapp):
        """Test Decline button sets result to DECLINED."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        decline_button = [b for b in buttons if "No Thanks" in b.text()][0]

        # Mock done method
        dialog.done = Mock()

        decline_button.click()

        assert dialog.get_result() == TelemetryOptInDialog.Result.DECLINED
        dialog.done.assert_called_once_with(TelemetryOptInDialog.Result.DECLINED)

    def test_remind_later_button_sets_result(self, qapp):
        """Test Remind Later button sets result to REMIND_LATER."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)
        remind_button = [b for b in buttons if "Remind" in b.text()][0]

        # Mock done method
        dialog.done = Mock()

        remind_button.click()

        assert dialog.get_result() == TelemetryOptInDialog.Result.REMIND_LATER
        dialog.done.assert_called_once_with(TelemetryOptInDialog.Result.REMIND_LATER)

    def test_accept_handler_logs_decision(self, qapp):
        """Test Accept handler logs user decision."""
        dialog = TelemetryOptInDialog()
        dialog.done = Mock()

        with patch("asciidoc_artisan.ui.telemetry_opt_in_dialog.logger") as mock_logger:
            dialog._accept_telemetry()

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "accepted" in call_args.lower()

    def test_decline_handler_logs_decision(self, qapp):
        """Test Decline handler logs user decision."""
        dialog = TelemetryOptInDialog()
        dialog.done = Mock()

        with patch("asciidoc_artisan.ui.telemetry_opt_in_dialog.logger") as mock_logger:
            dialog._decline_telemetry()

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "declined" in call_args.lower()

    def test_remind_later_handler_logs_decision(self, qapp):
        """Test Remind Later handler logs user decision."""
        dialog = TelemetryOptInDialog()
        dialog.done = Mock()

        with patch("asciidoc_artisan.ui.telemetry_opt_in_dialog.logger") as mock_logger:
            dialog._remind_later()

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "later" in call_args.lower()


class TestGetResult:
    """Test get_result method."""

    def test_get_result_returns_initial_value(self, qapp):
        """Test get_result returns initial REMIND_LATER."""
        dialog = TelemetryOptInDialog()

        result = dialog.get_result()

        assert result == TelemetryOptInDialog.Result.REMIND_LATER

    def test_get_result_after_accept(self, qapp):
        """Test get_result returns ACCEPTED after accepting."""
        dialog = TelemetryOptInDialog()
        dialog.done = Mock()

        dialog._accept_telemetry()

        assert dialog.get_result() == TelemetryOptInDialog.Result.ACCEPTED

    def test_get_result_after_decline(self, qapp):
        """Test get_result returns DECLINED after declining."""
        dialog = TelemetryOptInDialog()
        dialog.done = Mock()

        dialog._decline_telemetry()

        assert dialog.get_result() == TelemetryOptInDialog.Result.DECLINED

    def test_get_result_after_remind_later(self, qapp):
        """Test get_result returns REMIND_LATER after choosing remind."""
        dialog = TelemetryOptInDialog()
        dialog.done = Mock()

        dialog._remind_later()

        assert dialog.get_result() == TelemetryOptInDialog.Result.REMIND_LATER


class TestPrivacyPrinciples:
    """Test privacy-first design principles."""

    def test_no_dark_patterns_equal_button_emphasis(self, qapp):
        """Test all buttons have equal visual weight (no dark patterns)."""
        dialog = TelemetryOptInDialog()

        buttons = dialog.findChildren(QPushButton)

        # All buttons should have custom styling
        for button in buttons:
            assert button.styleSheet() != ""

        # All buttons should have padding (equal emphasis)
        for button in buttons:
            assert "padding" in button.styleSheet().lower()

    def test_clear_privacy_messaging(self, qapp):
        """Test privacy messaging is clear and prominent."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml().lower()

        # Check for privacy-related keywords
        privacy_keywords = ["privacy", "anonymous", "local", "no cloud", "opt-out"]
        found_keywords = [kw for kw in privacy_keywords if kw in html]

        assert len(found_keywords) >= 3  # At least 3 privacy keywords

    def test_gdpr_compliance_mentioned(self, qapp):
        """Test GDPR compliance is explicitly mentioned."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        assert "GDPR" in html or "General Data Protection Regulation" in html

    def test_opt_out_instructions_provided(self, qapp):
        """Test instructions for opting out are provided."""
        dialog = TelemetryOptInDialog()

        text_browser = dialog.findChildren(QTextBrowser)[0]
        html = text_browser.toHtml()

        # Check for Settings mention
        assert "Settings" in html
        # Check for ability to change decision
        assert "change" in html.lower() or "opt" in html.lower()
