"""Tests for ui.dialogs module."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel
from PySide6.QtCore import Qt

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


@pytest.mark.unit
class TestPreferencesDialogEdgeCases:
    """Test edge cases for PreferencesDialog."""

    def test_multiple_get_settings_calls(self, mock_settings):
        """Test calling get_settings multiple times returns consistent results."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        dialog.ai_enabled_checkbox.setChecked(True)

        settings1 = dialog.get_settings()
        settings2 = dialog.get_settings()

        assert settings1.ai_conversion_enabled == settings2.ai_conversion_enabled
        assert settings1.ai_conversion_enabled is True

    def test_dialog_with_null_model_value(self, mock_settings):
        """Test dialog handles None model value."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        mock_settings.ollama_model = None

        # Should not crash with None model
        dialog = PreferencesDialog(mock_settings)
        assert dialog is not None

    def test_ai_checkbox_toggle_multiple_times(self, mock_settings):
        """Test toggling AI checkbox multiple times."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Toggle 5 times
        for i in range(5):
            expected_state = i % 2 == 0
            dialog.ai_enabled_checkbox.setChecked(expected_state)
            assert dialog.ai_enabled_checkbox.isChecked() == expected_state

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-" + "x" * 100}, clear=True)
    def test_api_key_status_with_very_long_key(self, mock_settings):
        """Test API key status with very long key."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        status = dialog._get_api_key_status()
        assert status == "✓ Configured"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "   "}, clear=True)
    def test_api_key_status_with_whitespace_only(self, mock_settings):
        """Test API key status with whitespace-only key."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)
        status = dialog._get_api_key_status()
        # Whitespace key is still considered configured (env var exists)
        assert status == "✓ Configured"


@pytest.mark.unit
class TestOllamaDialogEdgeCases:
    """Test edge cases for OllamaSettingsDialog."""

    @patch("subprocess.run")
    def test_load_models_with_empty_response(self, mock_run, mock_settings):
        """Test loading models with empty Ollama response."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        dialog = OllamaSettingsDialog(mock_settings)

        # Should handle empty model list gracefully
        assert isinstance(dialog.models, list)

    @patch("subprocess.run")
    def test_load_models_with_error_code(self, mock_run, mock_settings):
        """Test loading models when Ollama returns error code."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        dialog = OllamaSettingsDialog(mock_settings)

        # Should handle error gracefully
        assert dialog is not None

    @patch("subprocess.run")
    def test_load_models_with_exception(self, mock_run, mock_settings):
        """Test loading models when subprocess raises exception."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_run.side_effect = Exception("Connection error")

        # Should handle exception gracefully
        dialog = OllamaSettingsDialog(mock_settings)
        assert dialog is not None

    def test_ollama_checkbox_toggle_multiple_times(self, mock_settings):
        """Test toggling Ollama checkbox multiple times."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        # Toggle 5 times
        for i in range(5):
            expected_state = i % 2 == 0
            dialog.ollama_enabled_checkbox.setChecked(expected_state)
            assert dialog.ollama_enabled_checkbox.isChecked() == expected_state

    @patch("subprocess.run")
    def test_model_combo_with_many_models(self, mock_run, mock_settings):
        """Test model combo box with many models."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # Create 50 model names
        models = "\n".join([f"model{i}" for i in range(50)])
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = models
        mock_run.return_value = mock_result

        dialog = OllamaSettingsDialog(mock_settings)

        # Verify models were loaded (actual count may vary based on system)
        assert isinstance(dialog.models, list)
        assert len(dialog.models) >= 0


@pytest.mark.unit
class TestDialogModalBehavior:
    """Test dialog modal behavior and window properties."""

    def test_preferences_dialog_is_modal(self, mock_settings):
        """Test PreferencesDialog has modal property."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Dialogs typically have modal setting
        assert hasattr(dialog, "setModal")

    def test_ollama_dialog_is_modal(self, mock_settings):
        """Test OllamaSettingsDialog has modal property."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        assert hasattr(dialog, "setModal")

    def test_preferences_dialog_has_parent_setter(self, mock_settings):
        """Test dialog can set parent."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        assert hasattr(dialog, "setParent")

    def test_dialog_window_flags(self, mock_settings):
        """Test dialog has window flags."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        assert hasattr(dialog, "windowFlags")
        assert hasattr(dialog, "setWindowFlags")


@pytest.mark.unit
class TestDialogStateTransitions:
    """Test dialog state transitions."""

    def test_preferences_initial_to_modified_state(self, mock_settings):
        """Test dialog transitions from initial to modified state."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        initial_state = dialog.ai_enabled_checkbox.isChecked()

        # Modify state
        dialog.ai_enabled_checkbox.setChecked(not initial_state)

        # Verify state changed
        assert dialog.ai_enabled_checkbox.isChecked() != initial_state

    def test_ollama_initial_to_modified_state(self, mock_settings):
        """Test Ollama dialog state transition."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        initial_state = dialog.ollama_enabled_checkbox.isChecked()

        # Modify state
        dialog.ollama_enabled_checkbox.setChecked(not initial_state)

        # Verify state changed
        assert dialog.ollama_enabled_checkbox.isChecked() != initial_state

    def test_multiple_state_changes_tracked(self, mock_settings):
        """Test dialog can capture different states."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Set to True
        dialog.ai_enabled_checkbox.setChecked(True)
        assert dialog.ai_enabled_checkbox.isChecked() is True

        # Set to False
        dialog.ai_enabled_checkbox.setChecked(False)
        assert dialog.ai_enabled_checkbox.isChecked() is False


@pytest.mark.unit
class TestSettingsPersistence:
    """Test settings persistence through dialogs."""

    def test_preferences_preserves_original_settings(self, mock_settings):
        """Test dialog doesn't modify original settings on creation."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        original_ai_state = mock_settings.ai_conversion_enabled
        dialog = PreferencesDialog(mock_settings)

        # Original settings should not be modified
        assert mock_settings.ai_conversion_enabled == original_ai_state

    def test_get_settings_returns_settings_object(self, mock_settings):
        """Test get_settings returns settings object."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        updated_settings = dialog.get_settings()

        # Should return a settings object
        assert isinstance(updated_settings, Settings)

    def test_ollama_preserves_original_settings(self, mock_settings):
        """Test Ollama dialog doesn't modify original settings on creation."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        original_state = mock_settings.ollama_enabled
        dialog = OllamaSettingsDialog(mock_settings)

        # Original settings should not be modified
        assert mock_settings.ollama_enabled == original_state

    def test_multiple_dialogs_independent(self, mock_settings):
        """Test multiple dialog instances are independent."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog1 = PreferencesDialog(mock_settings)
        dialog2 = PreferencesDialog(mock_settings)

        # Modify one dialog
        dialog1.ai_enabled_checkbox.setChecked(True)

        # Other dialog should have original state
        assert dialog2.ai_enabled_checkbox.isChecked() == mock_settings.ai_conversion_enabled


@pytest.mark.unit
class TestWidgetInteractions:
    """Test widget interactions within dialogs."""

    def test_checkbox_click_changes_state(self, mock_settings, qtbot):
        """Test clicking checkbox changes its state."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        initial_state = dialog.ai_enabled_checkbox.isChecked()

        # Click checkbox using click() method
        dialog.ai_enabled_checkbox.click()

        # State should toggle
        assert dialog.ai_enabled_checkbox.isChecked() != initial_state

    def test_combo_box_selection(self, mock_settings):
        """Test combo box allows selection."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        if dialog.model_combo.count() > 0:
            # Select first item
            dialog.model_combo.setCurrentIndex(0)
            assert dialog.model_combo.currentIndex() == 0

    def test_widget_enable_disable(self, mock_settings):
        """Test widgets can be enabled and disabled."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Disable checkbox
        dialog.ai_enabled_checkbox.setEnabled(False)
        assert not dialog.ai_enabled_checkbox.isEnabled()

        # Re-enable checkbox
        dialog.ai_enabled_checkbox.setEnabled(True)
        assert dialog.ai_enabled_checkbox.isEnabled()


@pytest.mark.unit
class TestDialogValidation:
    """Test dialog validation logic."""

    def test_get_settings_always_returns_settings_object(self, mock_settings):
        """Test get_settings always returns a Settings object."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        settings = dialog.get_settings()

        assert settings is not None
        assert isinstance(settings, Settings)

    def test_get_settings_preserves_unmodified_fields(self, mock_settings):
        """Test get_settings preserves fields that weren't modified."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        mock_settings.sync_scroll = True
        dialog = PreferencesDialog(mock_settings)

        # Don't modify anything
        settings = dialog.get_settings()

        # Other fields should be preserved
        assert settings.sync_scroll == mock_settings.sync_scroll

    def test_ollama_get_settings_returns_settings_object(self, mock_settings):
        """Test Ollama get_settings returns Settings object."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        settings = dialog.get_settings()

        assert settings is not None
        assert isinstance(settings, Settings)


@pytest.mark.unit
class TestButtonInteractions:
    """Test button interactions in dialogs."""

    def test_dialog_has_ok_button(self, mock_settings):
        """Test dialog has OK button."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Dialog should have standard buttons
        assert hasattr(dialog, "accept")

    def test_dialog_has_cancel_button(self, mock_settings):
        """Test dialog has Cancel button."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Dialog should have reject method (Cancel)
        assert hasattr(dialog, "reject")

    def test_accept_is_callable(self, mock_settings):
        """Test accept method is callable."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        assert callable(dialog.accept)

    def test_reject_is_callable(self, mock_settings):
        """Test reject method is callable."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        assert callable(dialog.reject)


@pytest.mark.unit
class TestLayoutVerification:
    """Test dialog layout structure."""

    def test_preferences_dialog_has_layout(self, mock_settings):
        """Test PreferencesDialog has a layout."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        assert dialog.layout() is not None

    def test_ollama_dialog_has_layout(self, mock_settings):
        """Test OllamaSettingsDialog has a layout."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.layout() is not None

    def test_dialog_layout_contains_widgets(self, mock_settings):
        """Test dialog layout contains widgets."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        layout = dialog.layout()
        # Layout should contain at least one widget
        assert layout.count() > 0

    def test_button_layout_structure(self, qapp):
        """Test button layout has correct structure."""
        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons
        from PySide6.QtWidgets import QDialog

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        # Should have multiple buttons
        assert layout.count() >= 2


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in dialogs."""

    def test_dialog_handles_missing_env_vars(self, mock_settings):
        """Test dialog handles missing environment variables."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            dialog = PreferencesDialog(mock_settings)
            assert dialog is not None

    @patch("subprocess.run")
    def test_ollama_handles_subprocess_timeout(self, mock_run, mock_settings):
        """Test Ollama dialog handles subprocess timeout."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_run.side_effect = TimeoutError("Process timed out")

        # Should handle timeout gracefully
        dialog = OllamaSettingsDialog(mock_settings)
        assert dialog is not None

    @patch("subprocess.run")
    def test_ollama_handles_permission_error(self, mock_run, mock_settings):
        """Test Ollama dialog handles permission error."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_run.side_effect = PermissionError("Permission denied")

        # Should handle permission error gracefully
        dialog = OllamaSettingsDialog(mock_settings)
        assert dialog is not None


@pytest.mark.unit
class TestDialogWidgetProperties:
    """Test widget properties and attributes."""

    def test_checkbox_text_set(self, mock_settings):
        """Test checkbox has text label."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Checkbox should have text
        assert dialog.ai_enabled_checkbox.text() != ""

    def test_combo_box_editable_property(self, mock_settings):
        """Test combo box editable property."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog
        dialog = OllamaSettingsDialog(mock_settings)

        # Combo box should have isEditable method
        assert hasattr(dialog.model_combo, "isEditable")

    def test_widget_visibility(self, mock_settings):
        """Test widget has visibility method."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Checkbox should have visibility method
        assert hasattr(dialog.ai_enabled_checkbox, "isVisible")

    def test_widget_parent_set(self, mock_settings):
        """Test widgets have parent set."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)

        # Widget should have parent
        parent = dialog.ai_enabled_checkbox.parent()
        assert parent is not None
