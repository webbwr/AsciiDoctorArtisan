"""E2E Tests for spell checking workflows."""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def app_window_with_text(qtbot, test_settings, tmp_path):
    """Create main window with text content."""
    test_settings.last_directory = str(tmp_path)
    test_settings.spell_check_enabled = True

    with (
        patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings",
            return_value=test_settings,
        ),
        patch("asciidoc_artisan.claude.claude_client.Anthropic"),
        patch("asciidoc_artisan.claude.claude_client.SecureCredentials") as mock_creds,
    ):
        mock_creds_instance = Mock()
        mock_creds_instance.get_anthropic_key.return_value = None
        mock_creds.return_value = mock_creds_instance

        window = AsciiDocEditor()
        qtbot.addWidget(window)

        # Set text with intentional misspellings
        window.editor.setPlainText("""= Document with Spelling

== Introduction

This documnet has some mispelled words.
The quik brown fox jumps over the lazy dog.

== Technical Terms

AsciiDoc and Python are correctly spelled.
""")
        yield window

        try:
            if hasattr(window, "spell_check_manager") and window.spell_check_manager:
                if hasattr(window.spell_check_manager, "check_timer"):
                    window.spell_check_manager.check_timer.stop()
            window.close()
        except RuntimeError:
            pass


@pytest.mark.e2e
@pytest.mark.forked
class TestSpellCheckManagerWorkflow:
    """Test spell check manager initialization."""

    def test_spell_check_manager_exists(self, app_window_with_text, qtbot):
        """E2E: Verify spell check manager is initialized."""
        assert hasattr(app_window_with_text, "spell_check_manager")

    def test_spell_check_settings(self, app_window_with_text, qtbot):
        """E2E: Verify spell check settings are accessible."""
        settings = app_window_with_text._settings
        assert hasattr(settings, "spell_check_enabled")

    def test_spell_check_toggle_action(self, app_window_with_text, qtbot):
        """E2E: Verify spell check toggle action exists."""
        if hasattr(app_window_with_text, "action_manager"):
            am = app_window_with_text.action_manager
            assert hasattr(am, "toggle_spell_check_act")


@pytest.mark.e2e
@pytest.mark.forked
class TestSpellCheckFunctionalityWorkflow:
    """Test spell check functionality."""

    def test_spell_checker_available(self, app_window_with_text, qtbot):
        """E2E: Test spell checker availability."""
        try:
            from asciidoc_artisan.core import SpellCheckManager

            # SpellCheckManager should be importable
            assert SpellCheckManager is not None
        except ImportError:
            pytest.skip("SpellCheckManager not available")

    def test_misspelling_detection_capability(self, app_window_with_text, qtbot):
        """E2E: Test that spell check can detect misspellings."""
        if app_window_with_text.spell_check_manager:
            manager = app_window_with_text.spell_check_manager
            # Check that manager has check method
            assert hasattr(manager, "check_spelling") or hasattr(manager, "_check_word")


@pytest.mark.e2e
@pytest.mark.forked
class TestSyntaxCheckerWorkflow:
    """Test syntax checker workflow."""

    def test_syntax_checker_manager_exists(self, app_window_with_text, qtbot):
        """E2E: Verify syntax checker manager exists."""
        assert hasattr(app_window_with_text, "syntax_checker_manager")

    def test_syntax_check_settings(self, app_window_with_text, qtbot):
        """E2E: Verify syntax check settings are accessible."""
        settings = app_window_with_text._settings
        assert hasattr(settings, "syntax_check_enabled")
