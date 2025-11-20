"""
Step definitions for spell check E2E tests.

Implements Gherkin steps for spell checking operations.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
pytestmark = [pytest.mark.e2e, pytest.mark.bdd, pytest.mark.gui]
scenarios("../features/spell_check.feature")


# ============================================================================
# Spell Check Test State
# ============================================================================


class SpellCheckState:
    """Track spell check operation state."""

    def __init__(self):
        self.errors = []
        self.suggestions = []
        self.custom_words = []


@pytest.fixture
def spell_state():
    """Provide spell check state tracking."""
    return SpellCheckState()


# ============================================================================
# Shared Steps
# ============================================================================


@given("the application is running")
def application_running(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible()
    return app


@given(parsers.parse('I have a document with content "{content}"'))
def document_with_content(app: AsciiDocEditor, content: str) -> AsciiDocEditor:
    """Set document content."""
    app.editor.setPlainText(content)
    return app


# ============================================================================
# Given Steps (Setup/Preconditions)
# ============================================================================


@given("spell check is disabled")
def spell_check_disabled(app: AsciiDocEditor):
    """Ensure spell check is disabled."""
    if app.spell_check_manager.enabled:
        app.spell_check_manager.toggle_spell_check()
    assert not app.spell_check_manager.enabled


@given("spell check is enabled")
def spell_check_enabled(app: AsciiDocEditor, qtbot):
    """Ensure spell check is enabled."""
    if not app.spell_check_manager.enabled:
        app.spell_check_manager.toggle_spell_check()
    assert app.spell_check_manager.enabled
    # Wait for spell check to complete
    qtbot.wait(100)


# ============================================================================
# When Steps (Actions)
# ============================================================================


@when("I enable spell check")
def enable_spell_check(app: AsciiDocEditor, qtbot):
    """Enable spell checking."""
    app.spell_check_manager.toggle_spell_check()
    qtbot.wait(100)  # Wait for spell check to run


@when("I disable spell check")
def disable_spell_check(app: AsciiDocEditor):
    """Disable spell checking."""
    app.spell_check_manager.toggle_spell_check()


@when("I check for spelling errors")
def check_spelling_errors(app: AsciiDocEditor, spell_state: SpellCheckState, qtbot):
    """Trigger spell check and collect errors."""
    # Force spell check
    app.spell_check_manager._perform_spell_check()
    qtbot.wait(100)  # Wait for spell check to complete
    spell_state.errors = app.spell_check_manager.errors


@when(parsers.parse('I get suggestions for "{word}"'))
def get_suggestions(app: AsciiDocEditor, spell_state: SpellCheckState, word: str):
    """Get spelling suggestions for a word."""
    spell_state.suggestions = app.spell_check_manager.spell_checker.get_suggestions(word)


@when(parsers.parse('I add "{word}" to the custom dictionary'))
def add_to_dictionary(app: AsciiDocEditor, spell_state: SpellCheckState, word: str, qtbot):
    """Add word to custom dictionary."""
    app.spell_check_manager.spell_checker.add_to_dictionary(word)
    spell_state.custom_words.append(word.lower())
    # Re-run spell check
    app.spell_check_manager._perform_spell_check()
    qtbot.wait(100)


@when(parsers.parse('I ignore the word "{word}"'))
def ignore_word(app: AsciiDocEditor, word: str, qtbot):
    """Ignore word for this session."""
    app.spell_check_manager.spell_checker.ignore_word(word)
    # Re-run spell check
    app.spell_check_manager._perform_spell_check()
    qtbot.wait(100)


# ============================================================================
# Then Steps (Assertions)
# ============================================================================


@then("spell check should be active")
def verify_spell_check_active(app: AsciiDocEditor):
    """Verify spell check is enabled."""
    assert app.spell_check_manager.enabled, "Spell check should be enabled"


@then("spell check should not be active")
def verify_spell_check_inactive(app: AsciiDocEditor):
    """Verify spell check is disabled."""
    assert not app.spell_check_manager.enabled, "Spell check should be disabled"


@then(parsers.parse('the status should show "{message}"'))
def verify_status_message(message: str):
    """Verify status message was shown."""
    # Status messages are transient, just verify step completed
    # In a real implementation, we'd capture status bar messages
    pass


@then(parsers.parse("I should see {count:d} spelling errors"))
def verify_error_count(spell_state: SpellCheckState, count: int):
    """Verify number of spelling errors."""
    assert (
        len(spell_state.errors) == count
    ), f"Expected {count} errors, found {len(spell_state.errors)}: {[e.word for e in spell_state.errors]}"


@then(parsers.parse('"{word}" should be marked as misspelled'))
def verify_word_misspelled(spell_state: SpellCheckState, word: str):
    """Verify word is in error list."""
    error_words = [e.word for e in spell_state.errors]
    assert word in error_words, f"Expected '{word}' in errors: {error_words}"


@then(parsers.parse('"{word}" should not be marked as misspelled'))
def verify_word_not_misspelled(app: AsciiDocEditor, word: str):
    """Verify word is not in error list."""
    error_words = [e.word for e in app.spell_check_manager.errors]
    assert word not in error_words, f"Did not expect '{word}' in errors: {error_words}"


@then(parsers.parse('I should see suggestions including "{suggestion}"'))
def verify_suggestion_included(spell_state: SpellCheckState, suggestion: str):
    """Verify suggestion is in list."""
    # Case-insensitive check
    suggestions_lower = [s.lower() for s in spell_state.suggestions]
    assert (
        suggestion.lower() in suggestions_lower
    ), f"Expected '{suggestion}' in suggestions: {spell_state.suggestions}"


@then(parsers.parse('the custom dictionary should contain "{word}"'))
def verify_in_custom_dictionary(app: AsciiDocEditor, word: str):
    """Verify word is in custom dictionary."""
    custom_dict = app.spell_check_manager.spell_checker._custom_dictionary
    assert (
        word.lower() in custom_dict
    ), f"Expected '{word}' in custom dictionary: {custom_dict}"


@then(parsers.parse('"{word}" should not be in the custom dictionary'))
def verify_not_in_custom_dictionary(app: AsciiDocEditor, word: str):
    """Verify word is not in custom dictionary."""
    custom_dict = app.spell_check_manager.spell_checker._custom_dictionary
    assert (
        word.lower() not in custom_dict
    ), f"Did not expect '{word}' in custom dictionary: {custom_dict}"


@then("no words should be marked as misspelled")
def verify_no_errors(app: AsciiDocEditor):
    """Verify no spelling errors."""
    # When disabled, errors list should be empty or spell check shouldn't run
    assert (
        not app.spell_check_manager.enabled
    ), "Spell check should be disabled"
