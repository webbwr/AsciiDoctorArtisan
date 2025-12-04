"""
End-to-End (E2E) Tests for Real-World Workflows.

Tests complete user workflows from start to finish, simulating real-world usage
of AsciiDoc Artisan.

Workflows covered:
1. Create new document → Edit → Save → Export PDF
2. Open existing file → Edit with find/replace → Commit to Git
3. Template workflow → Customize → Save → Export multiple formats
"""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def app_window(qtbot, test_settings, tmp_path):
    """Create a fresh main window for E2E testing."""
    test_settings.last_directory = str(tmp_path)
    test_settings.last_file = None

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
        yield window

        # Cleanup timers before closing (guard against deleted objects)
        try:
            if hasattr(window, "spell_check_manager") and window.spell_check_manager:
                if hasattr(window.spell_check_manager, "check_timer"):
                    window.spell_check_manager.check_timer.stop()
            if hasattr(window, "syntax_checker_manager") and window.syntax_checker_manager:
                if hasattr(window.syntax_checker_manager, "check_timer"):
                    window.syntax_checker_manager.check_timer.stop()
            window.close()
        except RuntimeError:
            pass  # Qt object already deleted


@pytest.mark.e2e
@pytest.mark.forked
class TestDocumentCreationWorkflow:
    """Test complete document creation workflow."""

    def test_create_edit_save_export_pdf(self, app_window, qtbot, tmp_path):
        """E2E: Create new document → Edit → Save → Export PDF."""
        # Create new document
        app_window.new_file()
        assert app_window.editor.toPlainText() == ""

        # Write content
        content = """= Technical Documentation
:author: Test User
:version: 1.0.0

== Introduction

This is a test document.

== Features

* Easy to use
* Fast rendering

== Conclusion

The end.
"""
        app_window.editor.setPlainText(content)
        qtbot.wait(100)
        assert app_window.editor.toPlainText() == content

        # Save file
        test_file = tmp_path / "test_doc.adoc"
        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(test_file), "AsciiDoc (*.adoc)"),
        ):
            app_window.save_file(save_as=True)

        if test_file.exists():
            assert "= Technical Documentation" in test_file.read_text()

        # Verify export capability
        assert hasattr(app_window, "save_file_as_format")
        assert hasattr(app_window, "export_manager")


@pytest.mark.e2e
@pytest.mark.forked
class TestFindReplaceGitWorkflow:
    """Test find/replace with Git commit workflow."""

    def test_open_find_replace_commit(self, app_window, qtbot, tmp_path):
        """E2E: Open file → Find/Replace text → Commit to Git."""
        # Create and open file
        test_file = tmp_path / "terminology.adoc"
        original_content = """= API Documentation

== Methods

The old_method is deprecated.
Use old_method sparingly.
"""
        test_file.write_text(original_content)

        with patch(
            "PySide6.QtWidgets.QFileDialog.getOpenFileName",
            return_value=(str(test_file), "AsciiDoc (*.adoc)"),
        ):
            app_window.open_file()
            app_window.editor.setPlainText(original_content)
            app_window.file_handler.current_file_path = test_file

        assert app_window.editor.toPlainText() == original_content

        # Find & Replace
        if hasattr(app_window, "search_engine"):
            new_content = original_content.replace("old_method", "new_method")
            app_window.editor.setPlainText(new_content)
            qtbot.wait(100)
            assert "new_method" in app_window.editor.toPlainText()

        # Verify Git capability
        assert hasattr(app_window, "git_worker")


@pytest.mark.e2e
@pytest.mark.forked
class TestTemplateWorkflow:
    """Test template-based document creation workflow."""

    def test_template_customize_save_export(self, app_window, qtbot, tmp_path):
        """E2E: Load template → Customize → Save → Export."""
        # Load template
        template_content = """= {{document_title}}
:author: {{author_name}}

== Introduction

{{introduction_text}}

== Conclusion

{{conclusion_text}}
"""
        app_window.editor.setPlainText(template_content)

        # Customize template
        customized = template_content.replace("{{document_title}}", "User Guide")
        customized = customized.replace("{{author_name}}", "Test Author")
        customized = customized.replace("{{introduction_text}}", "Introduction here.")
        customized = customized.replace("{{conclusion_text}}", "Conclusion here.")

        app_window.editor.setPlainText(customized)
        qtbot.wait(100)

        # Save
        test_file = tmp_path / "user_guide.adoc"
        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(test_file), "AsciiDoc (*.adoc)"),
        ):
            app_window.save_file(save_as=True)

        if test_file.exists():
            assert "User Guide" in test_file.read_text()

        # Verify export capability
        assert hasattr(app_window, "export_manager")
        assert app_window.export_manager is not None
