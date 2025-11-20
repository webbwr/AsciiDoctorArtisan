"""
Step definitions for find and replace E2E tests.

Implements Gherkin steps for text search and replacement operations.
"""

import pytest
from PySide6.QtGui import QTextDocument
from pytest_bdd import given, parsers, scenarios, then, when

from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
pytestmark = [pytest.mark.e2e, pytest.mark.bdd, pytest.mark.gui]
scenarios("../features/find_replace.feature")


# ============================================================================
# Shared Steps (duplicated for pytest-bdd)
# ============================================================================


@given("the application is running")
def application_running(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible()
    return app


@given(parsers.parse('I have a document with content "{content}"'))
def document_with_content(app: AsciiDocEditor, content: str) -> AsciiDocEditor:
    """Set document content (interpret \n as newlines)."""
    actual_content = content.replace("\\n", "\n")
    app.editor.setPlainText(actual_content)
    return app


@then(parsers.parse('the document should contain "{text}"'))
def document_contains(app: AsciiDocEditor, text: str):
    """Verify document contains text."""
    content = app.editor.toPlainText()
    assert text in content, f"Expected '{text}' in document"


@then(parsers.parse('the document should not contain "{text}"'))
def document_not_contains(app: AsciiDocEditor, text: str):
    """Verify document does not contain text."""
    content = app.editor.toPlainText()
    assert text not in content, f"Did not expect '{text}' in document"


@then(parsers.parse('the editor should contain "{text}"'))
def editor_contains(app: AsciiDocEditor, text: str):
    """Verify editor contains specific text."""
    content = app.editor.toPlainText()
    assert text in content, f"Expected '{text}' in editor"


# ============================================================================
# Find/Replace Test State
# ============================================================================


class FindReplaceState:
    """Track find/replace operation state."""

    def __init__(self):
        self.search_term = ""
        self.replace_term = ""
        self.case_sensitive = False
        self.whole_word = False
        self.regex_mode = False
        self.current_match = 0
        self.total_matches = 0


# Store state in pytest fixture
@pytest.fixture
def find_state():
    """Provide find/replace state tracking."""
    return FindReplaceState()


# ============================================================================
# When Steps (Actions)
# ============================================================================


@when("I open the find dialog")
def open_find_dialog(app: AsciiDocEditor):
    """Open find dialog (simulated for E2E)."""
    # In E2E tests, we simulate the dialog being open
    # Real implementation would use Ctrl+F or menu action
    pass


@when("I open the find and replace dialog")
def open_find_replace_dialog(app: AsciiDocEditor):
    """Open find and replace dialog (simulated for E2E)."""
    # In E2E tests, we simulate the dialog being open
    # Real implementation would use Ctrl+H or menu action
    pass


@when(parsers.parse('I search for "{text}"'))
def search_for_text(app: AsciiDocEditor, text: str, find_state: FindReplaceState):
    """Perform text search."""
    find_state.search_term = text

    # Perform the search in the editor
    content = app.editor.toPlainText()
    count = content.count(text)
    find_state.total_matches = count

    # Find and select first occurrence
    if count > 0:
        cursor = app.editor.textCursor()
        cursor.setPosition(0)
        app.editor.setTextCursor(cursor)
        if app.editor.find(text):
            find_state.current_match = 1


@when(parsers.parse('I search for "{text}" with case sensitivity enabled'))
def search_case_sensitive(app: AsciiDocEditor, text: str, find_state: FindReplaceState):
    """Perform case-sensitive search."""
    find_state.search_term = text
    find_state.case_sensitive = True

    content = app.editor.toPlainText()
    # Case-sensitive count
    count = content.count(text)
    find_state.total_matches = count

    if count > 0:
        cursor = app.editor.textCursor()
        cursor.setPosition(0)
        app.editor.setTextCursor(cursor)
        if app.editor.find(text, QTextDocument.FindFlag.FindCaseSensitively):
            find_state.current_match = 1


@when(parsers.parse('I search for "{text}" as whole word'))
def search_whole_word(app: AsciiDocEditor, text: str, find_state: FindReplaceState):
    """Perform whole-word search."""
    find_state.search_term = text
    find_state.whole_word = True

    content = app.editor.toPlainText()

    # Count whole-word matches
    import re

    pattern = r"\b" + re.escape(text) + r"\b"
    matches = re.findall(pattern, content)
    find_state.total_matches = len(matches)

    if len(matches) > 0:
        cursor = app.editor.textCursor()
        cursor.setPosition(0)
        app.editor.setTextCursor(cursor)
        if app.editor.find(text, QTextDocument.FindFlag.FindWholeWords):
            find_state.current_match = 1


@when(parsers.parse('I replace it with "{text}"'))
def set_replacement_text(find_state: FindReplaceState, text: str):
    """Set the replacement text."""
    find_state.replace_term = text


@when("I click replace next")
def replace_next_occurrence(app: AsciiDocEditor, find_state: FindReplaceState):
    """Replace the current occurrence and find next."""
    cursor = app.editor.textCursor()
    if cursor.hasSelection():
        cursor.insertText(find_state.replace_term)
        # Find next
        app.editor.find(find_state.search_term)


@when("I click replace all")
def replace_all_occurrences(app: AsciiDocEditor, find_state: FindReplaceState):
    """Replace all occurrences."""
    content = app.editor.toPlainText()

    if find_state.regex_mode:
        import re

        new_content = re.sub(find_state.search_term, find_state.replace_term, content)
    else:
        new_content = content.replace(find_state.search_term, find_state.replace_term)

    app.editor.setPlainText(new_content)


@when("I enable regex mode")
def enable_regex(find_state: FindReplaceState):
    """Enable regex search mode."""
    find_state.regex_mode = True


@when("I click find next")
def find_next(app: AsciiDocEditor, find_state: FindReplaceState):
    """Find next occurrence."""
    if app.editor.find(find_state.search_term):
        find_state.current_match += 1


@when("I click find previous")
def find_previous(app: AsciiDocEditor, find_state: FindReplaceState):
    """Find previous occurrence."""
    if app.editor.find(find_state.search_term, QTextDocument.FindFlag.FindBackward):
        find_state.current_match -= 1


# ============================================================================
# Then Steps (Assertions)
# ============================================================================


@then(parsers.parse("the search should find {count:d} occurrences"))
def verify_occurrence_count(find_state: FindReplaceState, count: int):
    """Verify number of search results."""
    assert find_state.total_matches == count, f"Expected {count} matches, found {find_state.total_matches}"


@then("the first occurrence should be highlighted")
def verify_first_highlighted(app: AsciiDocEditor, find_state: FindReplaceState):
    """Verify first occurrence is selected."""
    cursor = app.editor.textCursor()
    assert cursor.hasSelection(), "Expected text to be selected"
    assert find_state.current_match == 1, "Expected to be at first match"


@then("the second occurrence should be highlighted")
def verify_second_highlighted(app: AsciiDocEditor, find_state: FindReplaceState):
    """Verify second occurrence is selected."""
    cursor = app.editor.textCursor()
    assert cursor.hasSelection(), "Expected text to be selected"
    assert find_state.current_match == 2, "Expected to be at second match"
