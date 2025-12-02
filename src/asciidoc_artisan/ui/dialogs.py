"""
User Dialogs - Pop-up Windows for Settings and Configuration.

This module re-exports dialog classes from their individual modules
for backward compatibility after MA principle extraction.

Dialog classes:
- PreferencesDialog: Main user preferences (preferences_dialog.py)
- OllamaSettingsDialog: AI model selection (ollama_settings_dialog.py)
- SettingsEditorDialog: All settings table view (settings_editor_dialog.py)
- FontSettingsDialog: Font customization (font_settings_dialog.py)
"""

# Re-export all dialog classes for backward compatibility
from asciidoc_artisan.ui.font_settings_dialog import FontSettingsDialog
from asciidoc_artisan.ui.ollama_settings_dialog import OllamaSettingsDialog
from asciidoc_artisan.ui.preferences_dialog import PreferencesDialog
from asciidoc_artisan.ui.settings_editor_dialog import SettingsEditorDialog

__all__ = [
    "PreferencesDialog",
    "OllamaSettingsDialog",
    "SettingsEditorDialog",
    "FontSettingsDialog",
]
