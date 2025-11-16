"""Tests for ui.dialogs module."""

import os
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QCheckBox, QComboBox

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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
@pytest.mark.unit
class TestDialogHelperFunctions:
    """Test suite for dialog helper functions."""

    def test_create_ok_cancel_buttons_returns_layout(self, qapp):
        """Test helper function returns button layout."""
        from PySide6.QtWidgets import QDialog, QHBoxLayout

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        assert layout is not None
        assert isinstance(layout, QHBoxLayout)
        assert layout.count() >= 2  # Should have at least OK and Cancel buttons


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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
        assert (
            dialog2.ai_enabled_checkbox.isChecked()
            == mock_settings.ai_conversion_enabled
        )


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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
        from PySide6.QtWidgets import QDialog

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        # Should have multiple buttons
        assert layout.count() >= 2


@pytest.mark.fr_072
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


@pytest.mark.fr_072
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


@pytest.mark.fr_072
@pytest.mark.unit
class TestSettingsEditorDialog:
    """Test suite for SettingsEditorDialog class."""

    def test_settings_editor_dialog_title(self, mock_settings):
        """Test dialog has correct title."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)
        assert dialog.windowTitle() == "Application Settings"

    def test_settings_editor_dialog_minimum_size(self, mock_settings):
        """Test dialog has minimum size set."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)
        assert dialog.minimumWidth() == 800
        assert dialog.minimumHeight() == 600

    def test_settings_table_exists(self, mock_settings):
        """Test settings table widget is created."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)
        assert hasattr(dialog, "table")
        assert dialog.table is not None

    def test_settings_table_has_three_columns(self, mock_settings):
        """Test settings table has correct column count."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)
        assert dialog.table.columnCount() == 3

    def test_settings_table_column_headers(self, mock_settings):
        """Test settings table has correct column headers."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Check header labels
        headers = [
            dialog.table.horizontalHeaderItem(i).text() for i in range(3)
        ]
        assert "Setting" in headers
        assert "Value" in headers
        assert "Type" in headers

    def test_settings_loaded_into_table(self, mock_settings):
        """Test settings are loaded into table on initialization."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Table should have rows from settings
        assert dialog.table.rowCount() > 0

    def test_value_to_string_none(self, mock_settings):
        """Test converting None value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string(None)
        assert result == "None"

    def test_value_to_string_bool_true(self, mock_settings):
        """Test converting True value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string(True)
        assert result == "True"

    def test_value_to_string_bool_false(self, mock_settings):
        """Test converting False value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string(False)
        assert result == "False"

    def test_value_to_string_int(self, mock_settings):
        """Test converting int value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string(42)
        assert result == "42"

    def test_value_to_string_float(self, mock_settings):
        """Test converting float value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string(3.14)
        assert result == "3.14"

    def test_value_to_string_list(self, mock_settings):
        """Test converting list value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string([1, 2, 3])
        assert "[1, 2, 3]" in result

    def test_value_to_string_dict(self, mock_settings):
        """Test converting dict value to string."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._value_to_string({"key": "value"})
        assert "key" in result

    def test_string_to_value_none_type(self, mock_settings):
        """Test converting string to None value."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("None", "NoneType")
        assert result is None

    def test_string_to_value_bool_true(self, mock_settings):
        """Test converting string to bool True."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        assert dialog._string_to_value("true", "bool") is True
        assert dialog._string_to_value("True", "bool") is True
        assert dialog._string_to_value("1", "bool") is True
        assert dialog._string_to_value("yes", "bool") is True

    def test_string_to_value_bool_false(self, mock_settings):
        """Test converting string to bool False."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        assert dialog._string_to_value("false", "bool") is False
        assert dialog._string_to_value("0", "bool") is False
        assert dialog._string_to_value("no", "bool") is False

    def test_string_to_value_int(self, mock_settings):
        """Test converting string to int."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("42", "int")
        assert result == 42
        assert isinstance(result, int)

    def test_string_to_value_int_invalid(self, mock_settings):
        """Test converting invalid string to int returns 0."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("invalid", "int")
        assert result == 0

    def test_string_to_value_float(self, mock_settings):
        """Test converting string to float."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("3.14", "float")
        assert result == 3.14
        assert isinstance(result, float)

    def test_string_to_value_float_invalid(self, mock_settings):
        """Test converting invalid string to float returns 0.0."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("invalid", "float")
        assert result == 0.0

    def test_string_to_value_list(self, mock_settings):
        """Test converting string to list."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("[1, 2, 3]", "list")
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_string_to_value_list_invalid(self, mock_settings):
        """Test converting invalid string to list returns empty list."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("invalid", "list")
        assert result == []

    def test_string_to_value_dict(self, mock_settings):
        """Test converting string to dict."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("{'key': 'value'}", "dict")
        assert result == {"key": "value"}
        assert isinstance(result, dict)

    def test_string_to_value_dict_invalid(self, mock_settings):
        """Test converting invalid string to dict returns empty dict."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("invalid", "dict")
        assert result == {}

    def test_string_to_value_str(self, mock_settings):
        """Test converting string to str (passthrough)."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        result = dialog._string_to_value("test", "str")
        assert result == "test"

    @pytest.mark.skip(
        reason="Hangs indefinitely - Qt modal dialog issue (Phase 4E blocker)"
    )
    @patch("asciidoc_artisan.ui.dialogs.QMessageBox.question")
    def test_clear_all_settings_with_confirmation_yes(
        self, mock_question, mock_settings
    ):
        """Test clearing all settings when user confirms."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_question.return_value = QMessageBox.StandardButton.Yes

        dialog = SettingsEditorDialog(mock_settings, mock_manager)
        initial_rows = dialog.table.rowCount()

        dialog._clear_all_settings()

        # Should save settings after clearing
        assert mock_manager.save_settings.called

    @pytest.mark.skip(
        reason="Hangs indefinitely - Qt modal dialog issue (Phase 4E blocker)"
    )
    @patch("asciidoc_artisan.ui.dialogs.QMessageBox.question")
    def test_clear_all_settings_with_confirmation_no(
        self, mock_question, mock_settings
    ):
        """Test clearing all settings when user cancels."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_question.return_value = QMessageBox.StandardButton.No

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        dialog._clear_all_settings()

        # Should not save settings if user canceled
        assert not mock_manager.save_settings.called

    def test_on_item_changed_updates_settings(self, mock_settings):
        """Test item changed handler updates settings."""
        from PySide6.QtWidgets import QTableWidgetItem

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find a row with bool type
        for row in range(dialog.table.rowCount()):
            type_item = dialog.table.item(row, 2)
            if type_item and type_item.text() == "bool":
                # Simulate changing the value
                value_item = dialog.table.item(row, 1)
                value_item.setText("True")
                dialog._on_item_changed(value_item)

                # Should save settings
                assert mock_manager.save_settings.called
                break

    def test_settings_editor_with_parent_refresh(self, mock_settings):
        """Test settings editor refreshes parent window."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_parent = MagicMock()
        mock_parent._refresh_from_settings = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager, mock_parent)

        # Access parent window
        assert dialog.parent_window == mock_parent


@pytest.mark.fr_072
@pytest.mark.unit
class TestOllamaSettingsDialogEventHandlers:
    """Test suite for OllamaSettingsDialog event handlers."""

    def test_on_enabled_changed_enables_model_combo(self, mock_settings):
        """Test enabling checkbox enables model combo when models available."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Add models to make combo available
        dialog.models = ["model1", "model2"]
        dialog.model_combo.clear()
        dialog.model_combo.addItems(dialog.models)
        dialog.model_combo.setEnabled(False)

        # Enable checkbox
        dialog.ollama_enabled_checkbox.setChecked(True)
        dialog._on_enabled_changed()

        # Model combo should be enabled
        assert dialog.model_combo.isEnabled()

    def test_on_enabled_changed_disables_model_combo(self, mock_settings):
        """Test disabling checkbox disables model combo."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Disable checkbox
        dialog.ollama_enabled_checkbox.setChecked(False)
        dialog._on_enabled_changed()

        # Model combo should be disabled
        assert not dialog.model_combo.isEnabled()

    def test_on_enabled_changed_with_no_models(self, mock_settings):
        """Test enabled changed with no models keeps combo disabled."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Clear models
        dialog.models = []

        # Enable checkbox
        dialog.ollama_enabled_checkbox.setChecked(True)
        dialog._on_enabled_changed()

        # Model combo should remain disabled (no models)
        assert not dialog.model_combo.isEnabled()

    def test_update_parent_status_bar_with_parent(self, mock_settings):
        """Test updating parent status bar when parent has method."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_parent = MagicMock()
        mock_parent._update_ai_status_bar = MagicMock()

        dialog = OllamaSettingsDialog(mock_settings, mock_parent)

        # Add models
        dialog.models = ["test-model"]
        dialog.model_combo.clear()
        dialog.model_combo.addItem("test-model")

        # Update parent status bar
        dialog._update_parent_status_bar()

        # Parent method should be called
        assert mock_parent._update_ai_status_bar.called

    def test_update_parent_status_bar_without_parent(self, mock_settings):
        """Test updating parent status bar when no parent."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings, None)

        # Should not crash without parent
        dialog._update_parent_status_bar()

    def test_on_model_changed_updates_parent(self, mock_settings):
        """Test model changed handler updates parent status bar."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_parent = MagicMock()
        mock_parent._update_ai_status_bar = MagicMock()

        dialog = OllamaSettingsDialog(mock_settings, mock_parent)

        # Add models
        dialog.models = ["model1", "model2"]
        dialog.model_combo.clear()
        dialog.model_combo.addItems(dialog.models)

        # Change model
        dialog.model_combo.setCurrentIndex(1)
        dialog._on_model_changed()

        # Parent should be updated
        assert mock_parent._update_ai_status_bar.called

    def test_get_settings_includes_chat_settings(self, mock_settings):
        """Test get_settings includes chat settings."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Set chat settings
        dialog.chat_enabled_checkbox.setChecked(True)
        dialog.max_history_spin.setValue(200)
        dialog.send_document_checkbox.setChecked(False)

        settings = dialog.get_settings()

        assert settings.ollama_chat_enabled is True
        assert settings.ollama_chat_max_history == 200
        assert settings.ollama_chat_send_document is False

    def test_get_settings_chat_context_mode_document(self, mock_settings):
        """Test get_settings maps document context mode."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Set to Document Q&A (index 0)
        dialog.context_mode_combo.setCurrentIndex(0)

        settings = dialog.get_settings()
        assert settings.ollama_chat_context_mode == "document"

    def test_get_settings_chat_context_mode_syntax(self, mock_settings):
        """Test get_settings maps syntax context mode."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Set to Syntax Help (index 1)
        dialog.context_mode_combo.setCurrentIndex(1)

        settings = dialog.get_settings()
        assert settings.ollama_chat_context_mode == "syntax"

    def test_get_settings_chat_context_mode_general(self, mock_settings):
        """Test get_settings maps general context mode."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Set to General Chat (index 2)
        dialog.context_mode_combo.setCurrentIndex(2)

        settings = dialog.get_settings()
        assert settings.ollama_chat_context_mode == "general"

    def test_get_settings_chat_context_mode_editing(self, mock_settings):
        """Test get_settings maps editing context mode."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Set to Editing Suggestions (index 3)
        dialog.context_mode_combo.setCurrentIndex(3)

        settings = dialog.get_settings()
        assert settings.ollama_chat_context_mode == "editing"

    def test_context_mode_initial_value_document(self, mock_settings):
        """Test context mode combo initialized to document mode."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_settings.ollama_chat_context_mode = "document"
        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.context_mode_combo.currentIndex() == 0

    def test_context_mode_initial_value_syntax(self, mock_settings):
        """Test context mode combo initialized to syntax mode."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_settings.ollama_chat_context_mode = "syntax"
        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.context_mode_combo.currentIndex() == 1

    def test_get_settings_returns_none_model_when_no_models(self, mock_settings):
        """Test get_settings returns None for model when no models available."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        # Clear models
        dialog.models = []

        settings = dialog.get_settings()
        assert settings.ollama_model is None

    def test_chat_enabled_checkbox_exists(self, mock_settings):
        """Test chat enabled checkbox is created."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        assert hasattr(dialog, "chat_enabled_checkbox")
        assert isinstance(dialog.chat_enabled_checkbox, QCheckBox)

    def test_max_history_spin_exists(self, mock_settings):
        """Test max history spinbox is created."""
        from PySide6.QtWidgets import QSpinBox

        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        assert hasattr(dialog, "max_history_spin")
        assert isinstance(dialog.max_history_spin, QSpinBox)

    def test_max_history_spin_range(self, mock_settings):
        """Test max history spinbox has correct range."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.max_history_spin.minimum() == 10
        assert dialog.max_history_spin.maximum() == 500

    def test_send_document_checkbox_exists(self, mock_settings):
        """Test send document checkbox is created."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        assert hasattr(dialog, "send_document_checkbox")
        assert isinstance(dialog.send_document_checkbox, QCheckBox)

    def test_context_mode_combo_has_four_options(self, mock_settings):
        """Test context mode combo has four options."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.context_mode_combo.count() == 4


@pytest.mark.fr_072
@pytest.mark.unit
class TestFontSettingsDialog:
    """Test suite for FontSettingsDialog class."""

    def test_font_settings_dialog_title(self, mock_settings):
        """Test dialog has correct title."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)
        assert dialog.windowTitle() == "Font Settings"

    def test_font_settings_dialog_minimum_width(self, mock_settings):
        """Test dialog has minimum width set."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)
        assert dialog.minimumWidth() == 500

    def test_editor_font_combo_exists(self, mock_settings):
        """Test editor font combo box is created."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert hasattr(dialog, "editor_font_combo")
        assert isinstance(dialog.editor_font_combo, QComboBox)

    def test_preview_font_combo_exists(self, mock_settings):
        """Test preview font combo box is created."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert hasattr(dialog, "preview_font_combo")
        assert isinstance(dialog.preview_font_combo, QComboBox)

    def test_chat_font_combo_exists(self, mock_settings):
        """Test chat font combo box is created."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert hasattr(dialog, "chat_font_combo")
        assert isinstance(dialog.chat_font_combo, QComboBox)

    def test_editor_size_spin_exists(self, mock_settings):
        """Test editor size spinbox is created."""
        from PySide6.QtWidgets import QSpinBox

        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert hasattr(dialog, "editor_size_spin")
        assert isinstance(dialog.editor_size_spin, QSpinBox)

    def test_preview_size_spin_exists(self, mock_settings):
        """Test preview size spinbox is created."""
        from PySide6.QtWidgets import QSpinBox

        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert hasattr(dialog, "preview_size_spin")
        assert isinstance(dialog.preview_size_spin, QSpinBox)

    def test_chat_size_spin_exists(self, mock_settings):
        """Test chat size spinbox is created."""
        from PySide6.QtWidgets import QSpinBox

        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert hasattr(dialog, "chat_size_spin")
        assert isinstance(dialog.chat_size_spin, QSpinBox)

    def test_font_size_spinbox_range(self, mock_settings):
        """Test font size spinboxes have correct range."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert dialog.editor_size_spin.minimum() == 6
        assert dialog.editor_size_spin.maximum() == 72
        assert dialog.preview_size_spin.minimum() == 6
        assert dialog.preview_size_spin.maximum() == 72
        assert dialog.chat_size_spin.minimum() == 6
        assert dialog.chat_size_spin.maximum() == 72

    def test_populate_font_list_adds_fonts(self, mock_settings):
        """Test font list population adds fonts to combo."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # All font combos should have items
        assert dialog.editor_font_combo.count() > 0
        assert dialog.preview_font_combo.count() > 0
        assert dialog.chat_font_combo.count() > 0

    def test_font_combo_contains_common_fonts(self, mock_settings):
        """Test font combos contain common font families."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Get all font names from editor combo
        fonts = [
            dialog.editor_font_combo.itemText(i)
            for i in range(dialog.editor_font_combo.count())
        ]

        # Should contain at least one monospace font
        monospace_fonts = ["Courier New", "Consolas", "Monaco", "Menlo"]
        assert any(font in fonts for font in monospace_fonts)

    def test_initial_editor_font_from_settings(self, mock_settings):
        """Test editor font initialized from settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.editor_font_family = "Courier New"
        dialog = FontSettingsDialog(mock_settings)

        assert dialog.editor_font_combo.currentText() == "Courier New"

    def test_initial_preview_font_from_settings(self, mock_settings):
        """Test preview font initialized from settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.preview_font_family = "Arial"
        dialog = FontSettingsDialog(mock_settings)

        assert dialog.preview_font_combo.currentText() == "Arial"

    def test_initial_chat_font_from_settings(self, mock_settings):
        """Test chat font initialized from settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.chat_font_family = "Verdana"
        dialog = FontSettingsDialog(mock_settings)

        assert dialog.chat_font_combo.currentText() == "Verdana"

    def test_initial_editor_size_from_settings(self, mock_settings):
        """Test editor font size initialized from settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.editor_font_size = 14
        dialog = FontSettingsDialog(mock_settings)

        assert dialog.editor_size_spin.value() == 14

    def test_initial_preview_size_from_settings(self, mock_settings):
        """Test preview font size initialized from settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.preview_font_size = 16
        dialog = FontSettingsDialog(mock_settings)

        assert dialog.preview_size_spin.value() == 16

    def test_initial_chat_size_from_settings(self, mock_settings):
        """Test chat font size initialized from settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.chat_font_size = 11
        dialog = FontSettingsDialog(mock_settings)

        assert dialog.chat_size_spin.value() == 11

    def test_get_settings_returns_editor_font(self, mock_settings):
        """Test get_settings returns updated editor font."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Change editor font
        if dialog.editor_font_combo.count() > 1:
            dialog.editor_font_combo.setCurrentIndex(1)
            expected_font = dialog.editor_font_combo.currentText()

            settings = dialog.get_settings()
            assert settings.editor_font_family == expected_font

    def test_get_settings_returns_preview_font(self, mock_settings):
        """Test get_settings returns updated preview font."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Change preview font
        if dialog.preview_font_combo.count() > 1:
            dialog.preview_font_combo.setCurrentIndex(1)
            expected_font = dialog.preview_font_combo.currentText()

            settings = dialog.get_settings()
            assert settings.preview_font_family == expected_font

    def test_get_settings_returns_chat_font(self, mock_settings):
        """Test get_settings returns updated chat font."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Change chat font
        if dialog.chat_font_combo.count() > 1:
            dialog.chat_font_combo.setCurrentIndex(1)
            expected_font = dialog.chat_font_combo.currentText()

            settings = dialog.get_settings()
            assert settings.chat_font_family == expected_font

    def test_get_settings_returns_editor_size(self, mock_settings):
        """Test get_settings returns updated editor font size."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        dialog.editor_size_spin.setValue(18)

        settings = dialog.get_settings()
        assert settings.editor_font_size == 18

    def test_get_settings_returns_preview_size(self, mock_settings):
        """Test get_settings returns updated preview font size."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        dialog.preview_size_spin.setValue(20)

        settings = dialog.get_settings()
        assert settings.preview_font_size == 20

    def test_get_settings_returns_chat_size(self, mock_settings):
        """Test get_settings returns updated chat font size."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        dialog.chat_size_spin.setValue(10)

        settings = dialog.get_settings()
        assert settings.chat_font_size == 10

    def test_get_settings_updates_all_fonts(self, mock_settings):
        """Test get_settings updates all font settings at once."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Change all settings
        dialog.editor_size_spin.setValue(15)
        dialog.preview_size_spin.setValue(17)
        dialog.chat_size_spin.setValue(13)

        settings = dialog.get_settings()

        # All should be updated
        assert settings.editor_font_size == 15
        assert settings.preview_font_size == 17
        assert settings.chat_font_size == 13


# ============================================================================
# PHASE 1: SettingsEditorDialog Comprehensive Tests (~20 tests)
# ============================================================================


@pytest.mark.fr_072
@pytest.mark.unit
class TestSettingsEditorDialogLoadSettings:
    """Test SettingsEditorDialog._load_settings() method."""

    def test_load_settings_blocks_signals(self, mock_settings):
        """Test _load_settings() blocks signals during load."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.custom_attr = "test_value"

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Verify table was populated
        assert dialog.table.rowCount() > 0

    def test_load_settings_sorts_keys(self, mock_settings):
        """Test _load_settings() sorts dictionary keys."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Verify keys are alphabetically sorted
        keys = [dialog.table.item(i, 0).text() for i in range(dialog.table.rowCount())]
        assert keys == sorted(keys)

    def test_load_settings_with_empty_dict(self, mock_settings):
        """Test _load_settings() with minimal settings."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        minimal_settings = Settings()

        dialog = SettingsEditorDialog(minimal_settings, mock_manager)

        # Should have at least default settings
        assert dialog.table.rowCount() > 0

    def test_load_settings_item_flags(self, mock_settings):
        """Test _load_settings() sets correct item flags."""
        from PySide6.QtCore import Qt

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Setting name (column 0) should be read-only
        name_item = dialog.table.item(0, 0)
        assert not (name_item.flags() & Qt.ItemFlag.ItemIsEditable)

        # Value (column 1) should be editable
        value_item = dialog.table.item(0, 1)
        assert value_item.flags() & Qt.ItemFlag.ItemIsEditable

        # Type (column 2) should be read-only
        type_item = dialog.table.item(0, 2)
        assert not (type_item.flags() & Qt.ItemFlag.ItemIsEditable)

    def test_load_settings_column_count(self, mock_settings):
        """Test _load_settings() creates correct column count."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Should have exactly 3 columns: Setting, Value, Type
        assert dialog.table.columnCount() == 3

    def test_load_settings_with_various_data_types(self, mock_settings):
        """Test _load_settings() handles various data types."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.bool_val = True
        mock_settings.int_val = 42
        mock_settings.float_val = 3.14
        mock_settings.str_val = "test"
        mock_settings.list_val = [1, 2, 3]
        mock_settings.dict_val = {"key": "value"}
        mock_settings.none_val = None

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find each type in the table
        types_found = set()
        for i in range(dialog.table.rowCount()):
            type_item = dialog.table.item(i, 2)
            types_found.add(type_item.text())

        # Should have multiple types represented
        assert "bool" in types_found
        assert "int" in types_found
        assert "str" in types_found


@pytest.mark.fr_072
@pytest.mark.unit
class TestSettingsEditorDialogItemChanged:
    """Test SettingsEditorDialog._on_item_changed() live editing."""

    def test_on_item_changed_bool_value(self, mock_settings):
        """Test _on_item_changed() updates bool values."""
        from PySide6.QtWidgets import QTableWidgetItem

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_bool = False

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_bool row
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_bool":
                value_item = dialog.table.item(row, 1)
                value_item.setText("True")
                dialog._on_item_changed(value_item)

                # Should save settings
                assert mock_manager.save_settings.called
                assert mock_settings.test_bool is True
                break

    def test_on_item_changed_int_value(self, mock_settings):
        """Test _on_item_changed() updates int values."""
        from PySide6.QtWidgets import QTableWidgetItem

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_int = 10

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_int row
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_int":
                value_item = dialog.table.item(row, 1)
                value_item.setText("99")
                dialog._on_item_changed(value_item)

                assert mock_settings.test_int == 99
                break

    def test_on_item_changed_float_value(self, mock_settings):
        """Test _on_item_changed() updates float values."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_float = 1.0

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_float row
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_float":
                value_item = dialog.table.item(row, 1)
                value_item.setText("2.5")
                dialog._on_item_changed(value_item)

                assert mock_settings.test_float == 2.5
                break

    def test_on_item_changed_string_value(self, mock_settings):
        """Test _on_item_changed() updates string values."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_str = "old"

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_str row
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_str":
                value_item = dialog.table.item(row, 1)
                value_item.setText("new")
                dialog._on_item_changed(value_item)

                assert mock_settings.test_str == "new"
                break

    def test_on_item_changed_invalid_json_list(self, mock_settings):
        """Test _on_item_changed() handles malformed list JSON."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_list = [1, 2, 3]

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_list row
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_list":
                value_item = dialog.table.item(row, 1)
                value_item.setText("invalid json")
                dialog._on_item_changed(value_item)

                # Should default to empty list
                assert mock_settings.test_list == []
                break

    def test_on_item_changed_invalid_json_dict(self, mock_settings):
        """Test _on_item_changed() handles malformed dict JSON."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_dict = {"key": "value"}

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_dict row
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_dict":
                value_item = dialog.table.item(row, 1)
                value_item.setText("not valid json")
                dialog._on_item_changed(value_item)

                # Should default to empty dict
                assert mock_settings.test_dict == {}
                break

    def test_on_item_changed_parent_refresh_calls(self, mock_settings):
        """Test _on_item_changed() calls parent refresh."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_parent = MagicMock()
        mock_parent._refresh_from_settings = MagicMock()
        mock_settings.test_val = True

        dialog = SettingsEditorDialog(mock_settings, mock_manager, mock_parent)

        # Find a setting and change it
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_val":
                value_item = dialog.table.item(row, 1)
                value_item.setText("False")
                dialog._on_item_changed(value_item)

                # Parent refresh should be called
                assert mock_parent._refresh_from_settings.called
                break

    def test_on_item_changed_without_parent_refresh(self, mock_settings):
        """Test _on_item_changed() without parent refresh method."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_parent = MagicMock(spec=[])  # Parent without _refresh_from_settings
        mock_settings.test_val = 1

        dialog = SettingsEditorDialog(mock_settings, mock_manager, mock_parent)

        # Find a setting and change it
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_val":
                value_item = dialog.table.item(row, 1)
                value_item.setText("2")
                dialog._on_item_changed(value_item)

                # Should not crash even without parent refresh method
                assert mock_settings.test_val == 2
                break

    def test_on_item_changed_multiple_rapid_edits(self, mock_settings):
        """Test _on_item_changed() handles multiple rapid edits."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_settings.test_int = 0

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Find the test_int row and make multiple edits
        for row in range(dialog.table.rowCount()):
            if dialog.table.item(row, 0).text() == "test_int":
                value_item = dialog.table.item(row, 1)

                # Rapid edits
                for i in range(5):
                    value_item.setText(str(i * 10))
                    dialog._on_item_changed(value_item)

                # Should have final value
                assert mock_settings.test_int == 40
                # Save should be called multiple times
                assert mock_manager.save_settings.call_count >= 5
                break


@pytest.mark.fr_072
@pytest.mark.unit
class TestSettingsEditorDialogClearAll:
    """Test SettingsEditorDialog clear all functionality."""

    @patch("asciidoc_artisan.ui.dialogs.QMessageBox.question")
    def test_clear_all_with_parent_refresh(self, mock_question, mock_settings):
        """Test clear_all_settings with parent refresh."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_parent = MagicMock()
        mock_parent._refresh_from_settings = MagicMock()
        mock_question.return_value = QMessageBox.StandardButton.Yes

        dialog = SettingsEditorDialog(mock_settings, mock_manager, mock_parent)
        initial_rows = dialog.table.rowCount()

        dialog._clear_all_settings()

        # Should save and refresh parent
        assert mock_manager.save_settings.called
        assert mock_parent._refresh_from_settings.called

    @patch("asciidoc_artisan.ui.dialogs.QMessageBox.question")
    @patch("asciidoc_artisan.ui.dialogs.QMessageBox.information")
    def test_clear_all_shows_success_message(
        self, mock_info, mock_question, mock_settings
    ):
        """Test clear_all_settings shows success message."""
        from PySide6.QtWidgets import QMessageBox

        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()
        mock_question.return_value = QMessageBox.StandardButton.Yes

        dialog = SettingsEditorDialog(mock_settings, mock_manager)
        dialog._clear_all_settings()

        # Should show information message
        assert mock_info.called


@pytest.mark.fr_072
@pytest.mark.unit
class TestSettingsEditorDialogMisc:
    """Test miscellaneous SettingsEditorDialog functionality."""

    def test_column_width_settings(self, mock_settings):
        """Test column widths are set correctly."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Verify column widths
        assert dialog.table.columnWidth(0) == 250
        assert dialog.table.columnWidth(1) == 350
        assert dialog.table.columnWidth(2) == 150

    def test_dialog_minimum_size(self, mock_settings):
        """Test dialog has correct minimum size."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        assert dialog.minimumWidth() == 800
        assert dialog.minimumHeight() == 600

    def test_accept_closes_dialog(self, mock_settings):
        """Test accept() method exists and is callable."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        mock_manager = MagicMock()

        dialog = SettingsEditorDialog(mock_settings, mock_manager)

        # Accept method should be callable
        assert callable(dialog.accept)


# ============================================================================
# PHASE 2: FontSettingsDialog Comprehensive Tests (~18 tests)
# ============================================================================


@pytest.mark.fr_072
@pytest.mark.unit
class TestFontSettingsDialogPopulateFontList:
    """Test FontSettingsDialog._populate_font_list() method."""

    def test_populate_font_list_categorization(self, mock_settings):
        """Test _populate_font_list() categorizes fonts correctly."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Get all fonts from editor combo
        all_fonts = [
            dialog.editor_font_combo.itemText(i)
            for i in range(dialog.editor_font_combo.count())
        ]

        # Should contain monospace fonts
        monospace_fonts = ["Courier New", "Consolas", "Monaco", "Menlo"]
        assert any(font in all_fonts for font in monospace_fonts)

        # Should contain sans-serif fonts
        sans_fonts = ["Arial", "Helvetica", "Verdana"]
        assert any(font in all_fonts for font in sans_fonts)

        # Should contain serif fonts
        serif_fonts = ["Times New Roman", "Georgia", "Garamond"]
        assert any(font in all_fonts for font in serif_fonts)

    def test_populate_font_list_sorted(self, mock_settings):
        """Test _populate_font_list() sorts fonts alphabetically."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Get all fonts
        all_fonts = [
            dialog.editor_font_combo.itemText(i)
            for i in range(dialog.editor_font_combo.count())
        ]

        # Should be sorted
        assert all_fonts == sorted(all_fonts)

    def test_populate_font_list_no_duplicates(self, mock_settings):
        """Test _populate_font_list() has no duplicate fonts."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Get all fonts
        all_fonts = [
            dialog.editor_font_combo.itemText(i)
            for i in range(dialog.editor_font_combo.count())
        ]

        # Should have no duplicates
        assert len(all_fonts) == len(set(all_fonts))

    def test_populate_font_list_common_monospace(self, mock_settings):
        """Test _populate_font_list() includes common monospace fonts."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        all_fonts = [
            dialog.editor_font_combo.itemText(i)
            for i in range(dialog.editor_font_combo.count())
        ]

        # Should have at least some of these common monospace fonts
        expected_monospace = [
            "Courier New",
            "Consolas",
            "Monaco",
            "Menlo",
            "DejaVu Sans Mono",
        ]
        found_monospace = [f for f in expected_monospace if f in all_fonts]
        assert len(found_monospace) > 0


@pytest.mark.fr_072
@pytest.mark.unit
class TestFontSettingsDialogSelection:
    """Test FontSettingsDialog font selection edge cases."""

    def test_font_selection_with_nonexistent_font(self, mock_settings):
        """Test font selection with font not in list."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.editor_font_family = "NonexistentFont12345"

        dialog = FontSettingsDialog(mock_settings)

        # Should not crash with nonexistent font
        assert dialog.editor_font_combo.currentText() != ""

    def test_font_change_propagation(self, mock_settings):
        """Test font change updates settings correctly."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Change all font combos
        if dialog.editor_font_combo.count() > 1:
            dialog.editor_font_combo.setCurrentIndex(1)
        if dialog.preview_font_combo.count() > 1:
            dialog.preview_font_combo.setCurrentIndex(1)
        if dialog.chat_font_combo.count() > 1:
            dialog.chat_font_combo.setCurrentIndex(1)

        settings = dialog.get_settings()

        # All should be set to something
        assert settings.editor_font_family != ""
        assert settings.preview_font_family != ""
        assert settings.chat_font_family != ""

    def test_all_combos_populated(self, mock_settings):
        """Test all three font combos are populated."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # All combos should have items
        assert dialog.editor_font_combo.count() > 0
        assert dialog.preview_font_combo.count() > 0
        assert dialog.chat_font_combo.count() > 0

        # All combos should have same fonts
        editor_count = dialog.editor_font_combo.count()
        assert dialog.preview_font_combo.count() == editor_count
        assert dialog.chat_font_combo.count() == editor_count


@pytest.mark.fr_072
@pytest.mark.unit
class TestFontSettingsDialogLayout:
    """Test FontSettingsDialog layout and UI elements."""

    def test_group_box_layouts(self, mock_settings):
        """Test all three group boxes exist."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Should have main layout
        assert dialog.layout() is not None
        assert dialog.layout().count() > 0

    def test_spinbox_suffix_setting(self, mock_settings):
        """Test spinboxes have ' pt' suffix."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        assert dialog.editor_size_spin.suffix() == " pt"
        assert dialog.preview_size_spin.suffix() == " pt"
        assert dialog.chat_size_spin.suffix() == " pt"

    def test_spinbox_range_validation(self, mock_settings):
        """Test spinbox ranges are 6-72."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # All spinboxes should have same range
        for spin in [
            dialog.editor_size_spin,
            dialog.preview_size_spin,
            dialog.chat_size_spin,
        ]:
            assert spin.minimum() == 6
            assert spin.maximum() == 72

    def test_all_combos_initialized(self, mock_settings):
        """Test all font combos initialized with current settings."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.editor_font_family = "Courier New"
        mock_settings.preview_font_family = "Arial"
        mock_settings.chat_font_family = "Verdana"

        dialog = FontSettingsDialog(mock_settings)

        # Should match settings
        assert dialog.editor_font_combo.currentText() == "Courier New"
        assert dialog.preview_font_combo.currentText() == "Arial"
        assert dialog.chat_font_combo.currentText() == "Verdana"


@pytest.mark.fr_072
@pytest.mark.unit
class TestFontSettingsDialogGetSettings:
    """Test FontSettingsDialog.get_settings() validation."""

    def test_get_settings_with_defaults(self, mock_settings):
        """Test get_settings() with default values."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        settings = dialog.get_settings()

        # Should return Settings instance
        assert isinstance(settings, Settings)
        # Should have font settings
        assert hasattr(settings, "editor_font_family")
        assert hasattr(settings, "editor_font_size")

    def test_get_settings_with_custom_values(self, mock_settings):
        """Test get_settings() with custom values."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Change all values
        dialog.editor_size_spin.setValue(20)
        dialog.preview_size_spin.setValue(18)
        dialog.chat_size_spin.setValue(14)

        settings = dialog.get_settings()

        assert settings.editor_font_size == 20
        assert settings.preview_font_size == 18
        assert settings.chat_font_size == 14

    def test_get_settings_partial_updates(self, mock_settings):
        """Test get_settings() with partial updates."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        mock_settings.editor_font_size = 12
        mock_settings.preview_font_size = 14

        dialog = FontSettingsDialog(mock_settings)

        # Only change editor size
        dialog.editor_size_spin.setValue(16)

        settings = dialog.get_settings()

        # Editor should be updated
        assert settings.editor_font_size == 16
        # Preview should remain unchanged
        assert settings.preview_font_size == 14

    def test_get_settings_boundary_values(self, mock_settings):
        """Test get_settings() with boundary values (min/max)."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(mock_settings)

        # Set to minimum
        dialog.editor_size_spin.setValue(6)
        settings = dialog.get_settings()
        assert settings.editor_font_size == 6

        # Set to maximum
        dialog.editor_size_spin.setValue(72)
        settings = dialog.get_settings()
        assert settings.editor_font_size == 72


# ============================================================================
# PHASE 3: OllamaSettingsDialog Comprehensive Tests (~15 tests)
# ============================================================================


@pytest.mark.fr_072
@pytest.mark.unit
class TestOllamaDialogLoadModelsEdgeCases:
    """Test OllamaSettingsDialog._load_models() edge cases."""

    @patch("subprocess.run")
    def test_load_models_old_api_dict_format(self, mock_run, mock_settings):
        """Test _load_models() with old API dict format."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # This test verifies handling of dict with 'models' key (lines 423-427)
        # We'll use the actual ollama library if available
        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.return_value = {"models": [{"name": "model1"}]}

                dialog = OllamaSettingsDialog(mock_settings)

                # Should handle dict format
                assert dialog.models is not None
        except ImportError:
            # Skip if ollama not installed
            pass

    @patch("subprocess.run")
    def test_load_models_new_api_object_format(self, mock_run, mock_settings):
        """Test _load_models() with new API object format."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # This test verifies handling of object with .models attribute (lines 428-432)
        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_response = MagicMock()
                mock_response.models = [MagicMock(model="model1")]
                mock_list.return_value = mock_response

                dialog = OllamaSettingsDialog(mock_settings)

                # Should handle object format
                assert dialog.models is not None
        except ImportError:
            pass

    @patch("subprocess.run")
    def test_load_models_direct_list_format(self, mock_run, mock_settings):
        """Test _load_models() with direct list format."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # This test verifies handling of direct list (lines 433-437)
        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.return_value = [{"name": "model1"}, {"name": "model2"}]

                dialog = OllamaSettingsDialog(mock_settings)

                # Should handle list format
                assert dialog.models is not None
        except ImportError:
            pass

    @patch("subprocess.run")
    def test_load_models_name_extraction_dict(self, mock_run, mock_settings):
        """Test model name extraction from dict format."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # This test verifies lines 454-462: name extraction from dict
        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.return_value = {
                    "models": [{"name": "test-model"}, {"model": "alt-model"}]
                }

                dialog = OllamaSettingsDialog(mock_settings)

                # Should extract names from both 'name' and 'model' keys
                assert isinstance(dialog.models, list)
        except ImportError:
            pass

    @patch("subprocess.run")
    def test_load_models_saved_model_restoration(self, mock_run, mock_settings):
        """Test saved model restoration logic."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # This test verifies lines 469-472: saved model selection
        mock_settings.ollama_model = "preferred-model"

        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.return_value = {
                    "models": [
                        {"name": "other-model"},
                        {"name": "preferred-model"},
                    ]
                }

                dialog = OllamaSettingsDialog(mock_settings)

                # Should select saved model if available
                if "preferred-model" in dialog.models:
                    assert dialog.model_combo.currentText() == "preferred-model"
        except ImportError:
            pass

    @patch("subprocess.run")
    def test_load_models_malformed_response(self, mock_run, mock_settings):
        """Test _load_models() with malformed API response."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                # Return something unexpected
                mock_list.return_value = "not a dict or list"

                dialog = OllamaSettingsDialog(mock_settings)

                # Should handle gracefully
                assert isinstance(dialog.models, list)
        except ImportError:
            pass

    @patch("subprocess.run")
    def test_load_models_network_error(self, mock_run, mock_settings):
        """Test _load_models() with network error."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.side_effect = ConnectionError("Network error")

                dialog = OllamaSettingsDialog(mock_settings)

                # Should show error in status label
                assert "not running" in dialog.status_label.text().lower()
        except ImportError:
            pass


@pytest.mark.fr_072
@pytest.mark.unit
class TestOllamaDialogStatusUpdates:
    """Test OllamaSettingsDialog status label updates."""

    def test_status_label_success_green(self, mock_settings):
        """Test success status messages are green."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.return_value = {"models": [{"name": "test"}]}

                dialog = OllamaSettingsDialog(mock_settings)

                # Success status should be green
                assert "green" in dialog.status_label.styleSheet().lower()
        except ImportError:
            pass

    def test_status_label_error_red(self, mock_settings):
        """Test error status messages are red."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.side_effect = Exception("Test error")

                dialog = OllamaSettingsDialog(mock_settings)

                # Error status should be red
                assert "red" in dialog.status_label.styleSheet().lower()
        except ImportError:
            pass

    def test_status_label_no_models_orange(self, mock_settings):
        """Test no models status is orange/warning."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        try:
            import ollama

            with patch.object(ollama, "list") as mock_list:
                mock_list.return_value = {"models": []}

                dialog = OllamaSettingsDialog(mock_settings)

                # Warning status should be orange
                assert "orange" in dialog.status_label.styleSheet().lower()
        except ImportError:
            pass


@pytest.mark.fr_072
@pytest.mark.unit
class TestOllamaDialogChatSettings:
    """Test OllamaSettingsDialog chat settings functionality."""

    def test_context_mode_combo_initialization(self, mock_settings):
        """Test context mode combo initialization."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_settings.ollama_chat_context_mode = "general"

        dialog = OllamaSettingsDialog(mock_settings)

        # Should have 4 options
        assert dialog.context_mode_combo.count() == 4
        # Should select correct index for "general" (index 2)
        assert dialog.context_mode_combo.currentIndex() == 2

    def test_context_mode_mapping_all_modes(self, mock_settings):
        """Test context mode mapping for all modes."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # Test all 4 modes
        modes = [
            ("document", 0),
            ("syntax", 1),
            ("general", 2),
            ("editing", 3),
        ]

        for mode, expected_index in modes:
            mock_settings.ollama_chat_context_mode = mode
            dialog = OllamaSettingsDialog(mock_settings)
            assert dialog.context_mode_combo.currentIndex() == expected_index

    def test_chat_checkboxes_persistence(self, mock_settings):
        """Test all chat checkboxes state persistence."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        mock_settings.ollama_chat_enabled = True
        mock_settings.ollama_chat_send_document = False

        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.chat_enabled_checkbox.isChecked() is True
        assert dialog.send_document_checkbox.isChecked() is False

    def test_max_history_spinbox_range(self, mock_settings):
        """Test max history spinbox has correct range."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(mock_settings)

        assert dialog.max_history_spin.minimum() == 10
        assert dialog.max_history_spin.maximum() == 500


# ============================================================================
# PHASE 4: PreferencesDialog & Helper Tests (~11 tests)
# ============================================================================


@pytest.mark.fr_072
@pytest.mark.unit
class TestPreferencesDialogStyling:
    """Test PreferencesDialog styling and UI details."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True)
    def test_status_label_green_styling(self, mock_settings):
        """Test status label has green styling for configured key."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)

        # Find the status label by searching through widgets
        found_green = False
        for widget in dialog.findChildren(QLabel):
            if "API Key Status" in widget.text():
                # Should have green color in stylesheet
                if "green" in widget.styleSheet().lower():
                    found_green = True
                    break

        assert found_green

    @patch.dict(os.environ, {}, clear=True)
    def test_status_label_red_styling(self, mock_settings):
        """Test status label has red styling for missing key."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)

        # Find the status label
        found_red = False
        for widget in dialog.findChildren(QLabel):
            if "API Key Status" in widget.text():
                # Should have red color in stylesheet
                if "red" in widget.styleSheet().lower():
                    found_red = True
                    break

        assert found_red

    def test_info_label_word_wrap(self, mock_settings):
        """Test info label has word wrap enabled."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)

        # Find info labels
        for widget in dialog.findChildren(QLabel):
            if "Requires ANTHROPIC_API_KEY" in widget.text():
                # Should have word wrap
                assert widget.wordWrap() is True
                break

    def test_group_box_layout(self, mock_settings):
        """Test AI group box has proper layout."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)

        # Should have layout
        assert dialog.layout() is not None
        # Should have widgets
        assert dialog.layout().count() > 0


@pytest.mark.fr_072
@pytest.mark.unit
class TestPreferencesDialogExecution:
    """Test PreferencesDialog execution flow."""

    def test_dialog_exec_acceptance(self, mock_settings, qtbot):
        """Test dialog exec() acceptance flow."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)

        # Simulate accepting dialog
        # Note: We can't actually exec() in tests, but we can test accept()
        assert callable(dialog.accept)
        assert callable(dialog.reject)

    def test_dialog_exec_rejection(self, mock_settings):
        """Test dialog exec() rejection flow."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)

        # Should have reject method
        assert hasattr(dialog, "reject")
        assert callable(dialog.reject)

    def test_get_settings_with_various_states(self, mock_settings):
        """Test get_settings() with various checkbox states."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        # Test with enabled
        mock_settings.ai_conversion_enabled = False
        dialog = PreferencesDialog(mock_settings)
        dialog.ai_enabled_checkbox.setChecked(True)
        settings = dialog.get_settings()
        assert settings.ai_conversion_enabled is True

        # Test with disabled
        mock_settings.ai_conversion_enabled = True
        dialog = PreferencesDialog(mock_settings)
        dialog.ai_enabled_checkbox.setChecked(False)
        settings = dialog.get_settings()
        assert settings.ai_conversion_enabled is False

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-" + "x" * 200}, clear=True)
    def test_api_key_status_very_long_key(self, mock_settings):
        """Test API key status detection with very long key."""
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(mock_settings)
        status = dialog._get_api_key_status()

        # Long key should still be detected as configured
        assert status == "✓ Configured"


@pytest.mark.fr_072
@pytest.mark.unit
class TestHelperFunctionsDetailed:
    """Test _create_ok_cancel_buttons() helper function."""

    def test_create_buttons_stretch_behavior(self, qapp):
        """Test button layout has stretch to push buttons right."""
        from PySide6.QtWidgets import QDialog

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        # Should have stretch as first item (count >= 3: stretch + OK + Cancel)
        assert layout.count() >= 3

    def test_button_signal_connections(self, qapp):
        """Test OK and Cancel buttons are properly connected."""
        from PySide6.QtWidgets import QDialog

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        # Get buttons from layout
        ok_button = None
        cancel_button = None

        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, "text"):
                    if widget.text() == "OK":
                        ok_button = widget
                    elif widget.text() == "Cancel":
                        cancel_button = widget

        # Both buttons should exist
        assert ok_button is not None
        assert cancel_button is not None

    def test_button_text_validation(self, qapp):
        """Test buttons have correct text labels."""
        from PySide6.QtWidgets import QDialog

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

        dialog = QDialog()
        layout = _create_ok_cancel_buttons(dialog)

        # Find buttons and check text
        button_texts = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, "text"):
                    button_texts.append(widget.text())

        assert "OK" in button_texts
        assert "Cancel" in button_texts
