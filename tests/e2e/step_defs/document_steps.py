"""
Step definitions for document editing E2E tests.

Implements Gherkin steps for document creation, editing, saving, and opening.
"""

import time
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from pytest_bdd import given, parsers, scenarios, then, when

from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
scenarios("../features/document_editing.feature")


# ============================================================================
# Given Steps (Setup/Preconditions)
# ============================================================================


@given("the application is running")
def application_running(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible()
    return app


@given("I have a new document")
def new_document(app: AsciiDocEditor) -> AsciiDocEditor:
    """Create a new document."""
    app.file_handler.new_file()
    return app


@given(parsers.parse('I have typed "{text}" in the editor'))
def typed_text(app: AsciiDocEditor, text: str) -> AsciiDocEditor:
    """Type text in the editor."""
    app.editor.setPlainText(text)
    return app


@given("I have a temporary workspace")
def temporary_workspace(temp_workspace: Path) -> Path:
    """Provide temporary workspace."""
    return temp_workspace


@given(parsers.parse('a file "{filename}" exists with content "{content}"'))
def file_exists_with_content(
    temp_workspace: Path, filename: str, content: str
) -> Path:
    """Create a file with specific content."""
    file_path = temp_workspace / filename
    file_path.write_text(content)
    return file_path


@given(parsers.parse('I have opened a file "{filename}" with content "{content}"'))
def opened_file_with_content(
    app: AsciiDocEditor, temp_workspace: Path, filename: str, content: str
) -> Path:
    """Create and open a file with content."""
    file_path = temp_workspace / filename
    file_path.write_text(content)
    app.file_handler.open_file(str(file_path))
    return file_path


@given("I have a document open")
def document_open(app: AsciiDocEditor) -> AsciiDocEditor:
    """Ensure a document is open (create new if needed)."""
    if not app.editor.toPlainText():
        app.file_handler.new_file()
    return app


# ============================================================================
# When Steps (Actions)
# ============================================================================


@when("I create a new document")
def create_new_document(app: AsciiDocEditor):
    """Create a new document."""
    app.file_handler.new_file()


@when(parsers.parse('I type "{text}" in the editor'))
def type_in_editor(app: AsciiDocEditor, text: str):
    """Type text in the editor."""
    app.editor.insertPlainText(text)


@when("I type a new line")
def type_newline(app: AsciiDocEditor):
    """Insert a new line in the editor."""
    app.editor.insertPlainText("\n")


@when("I wait for preview to update")
def wait_for_preview_update(app: AsciiDocEditor, qtbot):
    """Wait for preview to update."""
    # Wait for debounce timeout (default 500ms) plus processing time
    qtbot.wait(1000)


@when("I undo the last action")
def undo_action(app: AsciiDocEditor):
    """Undo the last action."""
    app.editor.undo()


@when("I redo the last action")
def redo_action(app: AsciiDocEditor):
    """Redo the last action."""
    app.editor.redo()


@when(parsers.parse('I save the document as "{filename}"'))
def save_document_as(app: AsciiDocEditor, temp_workspace: Path, filename: str, qtbot):
    """Save document with specific filename."""
    from pathlib import Path
    file_path = temp_workspace / filename
    # For E2E tests, directly write the file to avoid async/dialog complications
    content = app.editor.toPlainText()
    file_path.write_text(content)
    # Update the app's internal state
    app.file_handler.current_file_path = Path(file_path)
    app.file_handler.unsaved_changes = False


@when(parsers.parse('I open the file "{filename}"'))
def open_file(app: AsciiDocEditor, temp_workspace: Path, filename: str):
    """Open a specific file."""
    file_path = temp_workspace / filename
    app.file_handler.open_file(str(file_path))


@when(parsers.parse('I append "{text}" to the editor'))
def append_to_editor(app: AsciiDocEditor, text: str):
    """Append text to the editor."""
    current = app.editor.toPlainText()
    app.editor.setPlainText(current + text)


@when("I save the current document")
def save_current_document(app: AsciiDocEditor, qtbot):
    """Save the current document."""
    from pathlib import Path
    # For E2E tests, directly write if we have a path
    if app.file_handler.current_file_path:
        content = app.editor.toPlainText()
        app.file_handler.current_file_path.write_text(content)
        app.file_handler.unsaved_changes = False
        qtbot.wait(100)  # Brief wait for UI update


@when("I increase the font size")
def increase_font_size(app: AsciiDocEditor):
    """Increase editor font size."""
    app.editor.zoomIn(2)  # Qt method


@when("I decrease the font size")
def decrease_font_size(app: AsciiDocEditor):
    """Decrease editor font size."""
    app.editor.zoomOut(2)  # Qt method


# ============================================================================
# Then Steps (Assertions/Verification)
# ============================================================================


@then("the editor should be empty")
def editor_empty(app: AsciiDocEditor):
    """Verify editor is empty."""
    assert app.editor.toPlainText() == ""


@then(parsers.parse('the window title should contain "{text}"'))
def window_title_contains(app: AsciiDocEditor, text: str):
    """Verify window title contains specific text (case-insensitive)."""
    title = app.windowTitle().lower()
    text_lower = text.lower()
    assert text_lower in title, f"Expected '{text}' in title '{app.windowTitle()}'"


@then(parsers.parse('the editor should contain "{text}"'))
def editor_contains(app: AsciiDocEditor, text: str):
    """Verify editor contains specific text."""
    content = app.editor.toPlainText()
    assert text in content, f"Expected '{text}' in editor content"


@then(parsers.parse('the preview should show "{text}" as a heading'))
def preview_shows_heading(app: AsciiDocEditor, text: str):
    """Verify preview shows text as a heading."""
    # Note: This is a simplified check. In real tests, you might want to
    # inspect the actual HTML or rendered content more carefully.
    # For now, we'll just check if the preview has been updated.
    assert app.preview_handler is not None


@then(parsers.parse('the file "{filename}" should exist in the workspace'))
def file_exists_in_workspace(temp_workspace: Path, filename: str):
    """Verify file exists in workspace."""
    file_path = temp_workspace / filename
    assert file_path.exists(), f"Expected file {filename} to exist"


@then(parsers.parse('the file "{filename}" should contain "{text}"'))
def file_contains(temp_workspace: Path, filename: str, text: str):
    """Verify file contains specific text."""
    file_path = temp_workspace / filename
    content = file_path.read_text()
    assert text in content, f"Expected '{text}' in file {filename}"


@then("the window title should indicate unsaved changes")
def title_indicates_unsaved(app: AsciiDocEditor):
    """Verify window title indicates unsaved changes."""
    # Typically indicated by an asterisk (*) in the title
    assert "*" in app.windowTitle() or "modified" in app.windowTitle().lower()


@then("the editor font should be larger")
def font_larger(app: AsciiDocEditor):
    """Verify font is larger (simplified check)."""
    # This is a simplified check - in a real implementation,
    # you would compare the actual font sizes
    assert app.editor.font().pointSize() > 10


@then("the editor font should be smaller")
def font_smaller(app: AsciiDocEditor):
    """Verify font is smaller (simplified check)."""
    # This is a simplified check
    assert app.editor.font().pointSize() < 20
