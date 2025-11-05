"""Tests for ui.dialog_manager module."""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit, QTextBrowser, QStatusBar


@pytest.fixture
def mock_main_window(qapp):
    """Create a mock main window with required attributes."""
    window = QMainWindow()

    # Settings
    window._settings = Mock()
    window._settings.ollama_enabled = False
    window._settings.ollama_model = None
    window._settings.telemetry_enabled = False
    window._settings.telemetry_session_id = None
    window._settings.claude_model = "claude-3-5-sonnet-20241022"
    window._settings.ai_backend = "ollama"

    # UI components
    window.editor = Mock(spec=QPlainTextEdit)
    window.preview = Mock(spec=QTextBrowser)
    window.status_bar = QStatusBar()

    # Status manager (mock all methods)
    window.status_manager = Mock()
    window.status_manager.show_message = Mock()
    window.status_manager.update_window_title = Mock()

    # Workers
    window.ollama_chat_worker = Mock()
    window.ollama_chat_worker.is_ollama_running = Mock(return_value=False)

    # Telemetry
    window.telemetry_collector = Mock()
    # Create a mock Path object for telemetry_file
    from pathlib import Path
    mock_file = Mock(spec=Path)
    mock_file.parent = Mock(spec=Path)
    mock_file.exists = Mock(return_value=False)
    window.telemetry_collector.telemetry_file = mock_file

    return window


@pytest.mark.unit
class TestDialogManagerBasics:
    """Test suite for DialogManager basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        assert DialogManager is not None

    def test_creation(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert manager is not None

    def test_stores_editor_reference(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert manager.editor == mock_main_window

    def test_has_dialog_methods(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_pandoc_status")
        assert hasattr(manager, "show_supported_formats")
        assert hasattr(manager, "show_ollama_status")
        assert hasattr(manager, "show_anthropic_status")
        assert hasattr(manager, "show_telemetry_status")
        assert callable(manager.show_pandoc_status)
        assert callable(manager.show_supported_formats)


@pytest.mark.unit
class TestPandocStatusDialog:
    """Test suite for Pandoc status dialog."""

    @patch("asciidoc_artisan.ui.dialog_manager.PANDOC_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.dialog_manager.pypandoc")
    def test_show_pandoc_status_available(self, mock_pypandoc, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_pypandoc.get_pandoc_version = Mock(return_value="2.19.2")
        mock_pypandoc.get_pandoc_path = Mock(return_value="/usr/bin/pandoc")

        manager = DialogManager(mock_main_window)
        manager.show_pandoc_status()

        # Should show status message
        assert mock_main_window.status_manager.show_message.called

    @patch("asciidoc_artisan.ui.dialog_manager.PANDOC_AVAILABLE", False)
    def test_show_pandoc_status_unavailable(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(mock_main_window)
        manager.show_pandoc_status()

        # Should show info message (not warning)
        call_args = mock_main_window.status_manager.show_message.call_args
        assert call_args[0][0] == "info"


@pytest.mark.unit
class TestSupportedFormatsDialog:
    """Test suite for supported formats dialog."""

    def test_has_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_supported_formats")
        assert callable(manager.show_supported_formats)

    @patch("asciidoc_artisan.ui.dialog_manager.PANDOC_AVAILABLE", False)
    def test_show_supported_formats_unavailable(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        manager = DialogManager(mock_main_window)
        manager.show_supported_formats()

        # Should show warning
        call_args = mock_main_window.status_manager.show_message.call_args
        assert call_args[0][0] == "warning"
        assert "unavailable" in call_args[0][1].lower()


@pytest.mark.unit
class TestOllamaStatusDialog:
    """Test suite for Ollama status dialog."""

    def test_show_ollama_status_disabled(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_main_window._settings.ollama_enabled = False

        manager = DialogManager(mock_main_window)
        manager.show_ollama_status()

        # Should show disabled message
        call_args = mock_main_window.status_manager.show_message.call_args
        assert "Disabled in settings" in call_args[0][2]

    def test_show_ollama_status_enabled_no_model(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_main_window._settings.ollama_enabled = True
        mock_main_window._settings.ollama_model = None

        manager = DialogManager(mock_main_window)
        manager.show_ollama_status()

        # Should show enabled message
        call_args = mock_main_window.status_manager.show_message.call_args
        assert "Enabled" in call_args[0][2]
        assert "No model selected" in call_args[0][2]

    def test_show_ollama_status_enabled_with_model(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_main_window._settings.ollama_enabled = True
        mock_main_window._settings.ollama_model = "llama2"

        manager = DialogManager(mock_main_window)
        manager.show_ollama_status()

        # Should show enabled with model
        call_args = mock_main_window.status_manager.show_message.call_args
        assert "llama2" in call_args[0][2]


@pytest.mark.unit
class TestAnthropicStatusDialog:
    """Test suite for Anthropic status dialog."""

    def test_has_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_anthropic_status")
        assert callable(manager.show_anthropic_status)

    @patch("asciidoc_artisan.core.secure_credentials.SecureCredentials")
    def test_show_anthropic_status_no_key(self, mock_creds_cls, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_creds = Mock()
        mock_creds.has_anthropic_key = Mock(return_value=False)
        mock_creds_cls.return_value = mock_creds

        manager = DialogManager(mock_main_window)
        manager.show_anthropic_status()

        # Should call status manager
        assert mock_main_window.status_manager.show_message.called


@pytest.mark.unit
class TestTelemetryStatusDialog:
    """Test suite for telemetry status dialog."""

    def test_has_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_telemetry_status")
        assert callable(manager.show_telemetry_status)


@pytest.mark.unit
class TestSettingsDialogs:
    """Test suite for settings dialogs."""

    def test_has_ollama_settings_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_ollama_settings")
        assert callable(manager.show_ollama_settings)

    def test_has_anthropic_settings_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_anthropic_settings")
        assert callable(manager.show_anthropic_settings)

    def test_has_app_settings_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_app_settings")
        assert callable(manager.show_app_settings)

    def test_has_font_settings_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_font_settings")
        assert callable(manager.show_font_settings)


@pytest.mark.unit
class TestMessageBoxes:
    """Test suite for message box helpers."""

    @patch("asciidoc_artisan.ui.dialog_manager.QMessageBox")
    def test_show_message_info(self, mock_msgbox_cls, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_msgbox = Mock()
        mock_msgbox.exec = Mock(return_value=0)
        mock_msgbox_cls.return_value = mock_msgbox

        manager = DialogManager(mock_main_window)
        manager.show_message("Info", "Test message", "info")

        # Should create message box
        mock_msgbox_cls.assert_called_once()

    @patch("asciidoc_artisan.ui.dialog_manager.QMessageBox")
    def test_show_message_warning(self, mock_msgbox_cls, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_msgbox = Mock()
        mock_msgbox.exec = Mock(return_value=0)
        mock_msgbox_cls.return_value = mock_msgbox

        manager = DialogManager(mock_main_window)
        manager.show_message("Warning", "Test warning", "warning")

        # Should create message box
        mock_msgbox_cls.assert_called_once()

    @patch("asciidoc_artisan.ui.dialog_manager.QMessageBox")
    def test_show_message_critical(self, mock_msgbox_cls, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_msgbox = Mock()
        mock_msgbox.exec = Mock(return_value=0)
        mock_msgbox_cls.return_value = mock_msgbox

        manager = DialogManager(mock_main_window)
        manager.show_message("Error", "Test error", "critical")

        # Should create message box
        mock_msgbox_cls.assert_called_once()


@pytest.mark.unit
class TestAboutDialog:
    """Test suite for About dialog."""

    @patch("asciidoc_artisan.ui.dialog_manager.QMessageBox")
    def test_show_about(self, mock_msgbox_cls, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        mock_msgbox = Mock()
        mock_msgbox.exec = Mock(return_value=0)
        mock_msgbox_cls.return_value = mock_msgbox

        manager = DialogManager(mock_main_window)
        manager.show_about()

        # Should create message box with about info
        mock_msgbox_cls.assert_called_once()
        mock_msgbox.setText.assert_called_once()


@pytest.mark.unit
class TestInstallationValidator:
    """Test suite for installation validator dialog."""

    def test_has_method(self, mock_main_window):
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        manager = DialogManager(mock_main_window)
        assert hasattr(manager, "show_installation_validator")
        assert callable(manager.show_installation_validator)
