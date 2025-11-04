"""Tests for ui.dialogs module."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel

from asciidoc_artisan.core import Settings


@pytest.fixture
def mock_settings(qapp):
    """Create mock settings for dialog testing."""
    settings = Settings()
    settings.dark_mode = False
    settings.font_size = 12
    settings.sync_scroll = True
    settings.auto_preview = True
    settings.ai_conversion_enabled = False
    settings.ollama_enabled = False
    settings.ollama_model = None
    return settings


@pytest.mark.unit
class TestDialogs:
    """Test suite for basic dialog functionality."""

    def test_import_dialogs(self):
        """Test dialogs module can be imported."""
        from asciidoc_artisan.ui import dialogs
        assert dialogs is not None

    def test_preferences_dialog_exists(self, mock_settings):
        """Test PreferencesDialog can be instantiated."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        assert dialog is not None
        assert dialog.windowTitle() != ""

    def test_dialog_has_accept_reject(self, mock_settings):
        """Test dialog has accept/reject methods."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        assert hasattr(dialog, "accept")
        assert hasattr(dialog, "reject")


@pytest.mark.unit
class TestPreferencesDialog:
    """Test suite for PreferencesDialog class."""

    def test_preferences_dialog_title(self, mock_settings):
        """Test dialog has correct title."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        assert dialog.windowTitle() == "Preferences"

    def test_preferences_dialog_minimum_width(self, mock_settings):
        """Test dialog has minimum width set."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        assert dialog.minimumWidth() == 500

    def test_ai_enabled_checkbox_exists(self, mock_settings):
        """Test AI enabled checkbox is created."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        assert hasattr(dialog, "ai_enabled_checkbox")
        assert isinstance(dialog.ai_enabled_checkbox, QCheckBox)

    def test_ai_enabled_checkbox_initial_state_false(self, mock_settings):
        """Test AI checkbox reflects initial disabled state."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        mock_settings.ai_conversion_enabled = False
        dialog = PreferencesDialog(mock_settings)
        assert not dialog.ai_enabled_checkbox.isChecked()

    def test_ai_enabled_checkbox_initial_state_true(self, mock_settings):
        """Test AI checkbox reflects initial enabled state."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        mock_settings.ai_conversion_enabled = True
        dialog = PreferencesDialog(mock_settings)
        assert dialog.ai_enabled_checkbox.isChecked()

    def test_get_settings_returns_updated_ai_enabled(self, mock_settings):
        """Test get_settings returns updated AI enabled state."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Change checkbox state
        dialog.ai_enabled_checkbox.setChecked(True)

        # Get updated settings
        updated_settings = dialog.get_settings()
        assert updated_settings.ai_conversion_enabled is True

    def test_get_settings_returns_updated_ai_disabled(self, mock_settings):
        """Test get_settings returns updated AI disabled state."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        mock_settings.ai_conversion_enabled = True
        dialog = PreferencesDialog(mock_settings)

        # Change checkbox state
        dialog.ai_enabled_checkbox.setChecked(False)

        # Get updated settings
        updated_settings = dialog.get_settings()
        assert updated_settings.ai_conversion_enabled is False

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key-123"}, clear=True)
    def test_api_key_status_configured(self, mock_settings):
        """Test API key status shows configured when key is set."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        status = dialog._get_api_key_status()
        assert status == "✓ Configured"

    @patch.dict(os.environ, {}, clear=True)
    def test_api_key_status_not_set(self, mock_settings):
        """Test API key status shows not set when key is missing."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        status = dialog._get_api_key_status()
        assert status == "✗ Not Set"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=True)
    def test_api_key_status_empty_string(self, mock_settings):
        """Test API key status shows not set for empty string."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        status = dialog._get_api_key_status()
        assert status == "✗ Not Set"


@pytest.mark.unit
class TestOllamaSettingsDialog:
    """Test suite for OllamaSettingsDialog class."""

    def test_ollama_dialog_title(self, mock_settings):
        """Test dialog has correct title."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)
        assert dialog.windowTitle() == "Ollama AI Settings"

    def test_ollama_dialog_minimum_width(self, mock_settings):
        """Test dialog has minimum width set."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)
        assert dialog.minimumWidth() == 500

    def test_ollama_enabled_checkbox_exists(self, mock_settings):
        """Test Ollama enabled checkbox is created."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)
        assert hasattr(dialog, "ollama_enabled_checkbox")
        assert isinstance(dialog.ollama_enabled_checkbox, QCheckBox)

    def test_ollama_model_combo_exists(self, mock_settings):
        """Test Ollama model combo box is created."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)
        assert hasattr(dialog, "model_combo")
        assert isinstance(dialog.model_combo, QComboBox)

    def test_ollama_enabled_checkbox_initial_state(self, mock_settings):
        """Test Ollama checkbox reflects initial state."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        mock_settings.ollama_enabled = True
        dialog = OllamaSettingsDialog(mock_settings)
        assert dialog.ollama_enabled_checkbox.isChecked()

    @patch("subprocess.run")
    def test_load_models_success(self, mock_run, mock_settings):
        """Test loading models from Ollama succeeds."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # Mock successful Ollama response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "model1\nmodel2\nmodel3"
        mock_run.return_value = mock_result

        dialog = OllamaSettingsDialog(mock_settings)

        # Verify models were loaded
        assert len(dialog.models) > 0

    def test_dialog_handles_ollama_availability(self, mock_settings):
        """Test dialog handles Ollama availability status gracefully."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # Dialog should handle both cases: Ollama available or not available
        dialog = OllamaSettingsDialog(mock_settings)

        # Verify dialog was created successfully (doesn't crash)
        assert dialog is not None
        # Models list should be either populated (if Ollama available) or empty
        assert isinstance(dialog.models, list)

    def test_get_settings_returns_updated_ollama_enabled(self, mock_settings):
        """Test get_settings returns updated Ollama enabled state."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        # Change checkbox state
        dialog.ollama_enabled_checkbox.setChecked(True)

        # Get updated settings
        updated_settings = dialog.get_settings()
        assert updated_settings.ollama_enabled is True


@pytest.mark.unit
class TestDialogHelperFunctions:
    """Test suite for dialog helper functions."""

    def test_create_ok_cancel_buttons_returns_layout(self, qapp):
        """Test helper function returns button layout."""
        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons
        from PySide6.QtWidgets import QDialog, QHBoxLayout

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        assert layout is not None
        assert isinstance(layout, QHBoxLayout)
        assert layout.count() >= 2  # Should have at least OK and Cancel buttons
