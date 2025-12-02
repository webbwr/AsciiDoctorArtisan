"""
GitHub Dialog Validation Helpers - Reusable Input Validation.

Extracted from github_dialogs.py for MA principle compliance.
Contains validation functions used by all GitHub dialog classes.
"""

import logging

from PySide6.QtWidgets import QLineEdit, QWidget

logger = logging.getLogger(__name__)


def show_validation_error(widget: QWidget, widget_type: str) -> None:
    """
    Show Validation Error - Make Widget Border Red.

    WHY THIS EXISTS:
    When user enters invalid data (e.g., empty required field), we need to
    show them what's wrong. A red border is the standard way to indicate errors.

    WHAT IT DOES:
    1. Apply red border CSS style to the widget
    2. Move keyboard focus to the widget (cursor appears there)

    HOW IT WORKS:
    We use Qt's CSS styling system. Each widget type (QLineEdit, QComboBox)
    needs its CSS class name in the style string.

    PARAMETERS:
        widget: The input widget with invalid data (will get red border)
        widget_type: CSS class name ("QLineEdit", "QComboBox", etc.)

    EXAMPLE:
        show_validation_error(title_input, "QLineEdit")
        # Result: title_input now has red border and keyboard focus
    """
    # Apply CSS style - red 1px border around the widget
    widget.setStyleSheet(f"{widget_type} {{ border: 1px solid red; }}")

    # Move keyboard focus to this widget so user knows where to fix the error
    widget.setFocus()


def clear_validation_error(widget: QWidget) -> None:
    """
    Clear Validation Error - Remove Red Border.

    WHY THIS EXISTS:
    After user fixes the error, we need to remove the red border.
    Otherwise, it stays red even after fixing!

    WHAT IT DOES:
    Remove all custom CSS styling from the widget (returns to default look)

    PARAMETERS:
        widget: The input widget to clear styling from

    EXAMPLE:
        clear_validation_error(title_input)
        # Result: title_input returns to normal appearance
    """
    # Empty string = remove all custom styles, use default
    widget.setStyleSheet("")


def validate_required_text(widget: QLineEdit, field_name: str) -> bool:
    """
    Validate Required Text Field - Check If Not Empty.

    WHY THIS EXISTS:
    Many fields are required (e.g., PR title, Issue title). This function
    checks if user entered something, and shows an error if they didn't.

    WHAT IT DOES:
    1. Get text from the widget
    2. Strip whitespace (remove spaces from beginning/end)
    3. If empty: Show red border + log warning, return False
    4. If not empty: Clear red border, return True

    WHY .strip()?:
    "   " (just spaces) should count as empty. .strip() removes leading/trailing
    whitespace, so "   " becomes "" (empty string).

    PARAMETERS:
        widget: QLineEdit to check (text input box)
        field_name: Name of field for logging ("PR title", "Issue title", etc.)

    RETURNS:
        True if field has text (valid)
        False if field is empty (invalid)

    USAGE PATTERN:
        if not validate_required_text(self.title_input, "PR title"):
            return  # Don't submit form, user needs to fix error

    TECHNICAL NOTE:
    This follows the "validation guard" pattern - check for errors first,
    return early if found. This avoids deep nesting (if valid: if valid: if valid:)
    """
    # Get text from input and remove leading/trailing spaces
    text = widget.text().strip()

    # Check if empty
    if not text:
        # Empty! Show error and return False
        show_validation_error(widget, "QLineEdit")
        logger.warning(f"{field_name} is required")
        return False  # Validation failed

    # Not empty! Clear any previous error and return True
    clear_validation_error(widget)
    return True  # Validation passed


# Backward compatibility aliases with underscore prefix (private convention)
_show_validation_error = show_validation_error
_clear_validation_error = clear_validation_error
_validate_required_text = validate_required_text
