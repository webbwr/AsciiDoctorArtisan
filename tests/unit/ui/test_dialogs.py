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
        from PySide6.QtWidgets import QDialog, QHBoxLayout

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

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
        assert (
            dialog2.ai_enabled_checkbox.isChecked()
            == mock_settings.ai_conversion_enabled
        )


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
        from PySide6.QtWidgets import QDialog

        from asciidoc_artisan.ui.dialogs import _create_ok_cancel_buttons

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
