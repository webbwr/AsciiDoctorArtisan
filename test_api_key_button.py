#!/usr/bin/env python3
"""
Test script to verify API key button functionality.
"""
import sys
import logging
from PySide6.QtWidgets import QApplication
from asciidoc_artisan.core import Settings
from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s")

def test_dialog():
    """Test the OllamaSettingsDialog and API key button."""
    app = QApplication(sys.argv)

    # Create settings
    settings = Settings()

    # Create dialog
    print("\n=== Creating OllamaSettingsDialog ===")
    dialog = OllamaSettingsDialog(settings)

    # Show dialog (non-blocking)
    print("\n=== Showing dialog - check if 'Configure Anthropic API Key...' button is visible ===")
    print("=== Click the button to test if it opens the APIKeySetupDialog ===")
    print("=== Check console for log messages when button is clicked ===\n")

    dialog.show()

    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    test_dialog()
