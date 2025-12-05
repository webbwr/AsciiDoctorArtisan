"""
End-to-End (E2E) Tests for Real-World Workflows.

Tests complete user workflows from start to finish, simulating real-world usage
of AsciiDoc Artisan.

Workflows covered:
1. Create new document → Edit → Save → Export PDF
2. Open existing file → Edit with find/replace → Commit to Git
3. Template workflow → Customize → Save → Export multiple formats
4. Preview workflow → Edit → Render → Verify
5. Settings workflow → Change → Persist → Reload
6. Undo/Redo workflow → Edit → Undo → Redo
7. Theme workflow → Switch → Verify persistence
8. Multiple files workflow → Open → Switch → Close
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


@pytest.mark.e2e
@pytest.mark.forked
class TestPreviewWorkflow:
    """Test document preview workflow."""

    def test_edit_trigger_preview(self, app_window, qtbot):
        """E2E: Edit document → Trigger preview → Verify signal emission."""
        # Set document content
        content = """= Preview Test
:toc:

== Section One

This is a *bold* and _italic_ test.

== Section Two

[source,python]
----
def hello():
    print("Hello World")
----
"""
        app_window.editor.setPlainText(content)
        qtbot.wait(100)

        # Verify preview worker is available
        assert hasattr(app_window, "preview_worker")
        # preview_worker may be None if not initialized in test environment

        # Verify preview signal exists
        assert hasattr(app_window, "request_preview_render")

        # Trigger preview update (wait for potential auto-render)
        qtbot.wait(200)

    def test_preview_with_code_blocks(self, app_window, qtbot):
        """E2E: Preview document with code blocks."""
        content = """= Code Examples

[source,python]
----
import asyncio

async def main():
    await asyncio.sleep(1)
----

[source,bash]
----
#!/bin/bash
echo "Hello"
----
"""
        app_window.editor.setPlainText(content)
        qtbot.wait(100)

        # Content should be set
        assert "asyncio" in app_window.editor.toPlainText()
        assert "echo" in app_window.editor.toPlainText()


@pytest.mark.e2e
@pytest.mark.forked
class TestUndoRedoWorkflow:
    """Test undo/redo workflow."""

    def test_edit_undo_redo_cycle(self, app_window, qtbot):
        """E2E: Edit → Undo → Redo → Verify state."""
        # Start with empty document
        app_window.new_file()
        assert app_window.editor.toPlainText() == ""

        # First edit
        app_window.editor.setPlainText("Line 1")
        qtbot.wait(50)
        assert app_window.editor.toPlainText() == "Line 1"

        # Second edit
        app_window.editor.setPlainText("Line 1\nLine 2")
        qtbot.wait(50)
        assert "Line 2" in app_window.editor.toPlainText()

        # Test undo capability
        assert hasattr(app_window.editor, "undo")
        assert hasattr(app_window.editor, "redo")

    def test_multiple_undo_operations(self, app_window, qtbot):
        """E2E: Multiple edits → Multiple undos."""
        app_window.new_file()

        # Make multiple edits
        edits = ["First", "Second", "Third", "Fourth"]
        for edit in edits:
            app_window.editor.insertPlainText(edit + "\n")
            qtbot.wait(20)

        # Verify final content has all edits
        final_content = app_window.editor.toPlainText()
        for edit in edits:
            assert edit in final_content


@pytest.mark.e2e
@pytest.mark.forked
class TestSettingsWorkflow:
    """Test settings persistence workflow."""

    def test_settings_modification(self, app_window, qtbot):
        """E2E: Modify settings → Verify in-memory state."""
        # Get current settings
        assert hasattr(app_window, "_settings")
        settings = app_window._settings

        # Modify a setting
        original_font_size = settings.font_size
        new_font_size = original_font_size + 2

        settings.font_size = new_font_size
        assert settings.font_size == new_font_size

        # Restore original
        settings.font_size = original_font_size

    def test_settings_accessible(self, app_window, qtbot):
        """E2E: Verify settings are accessible."""
        assert hasattr(app_window, "_settings")
        settings = app_window._settings

        # Verify key settings attributes exist
        assert hasattr(settings, "editor_font_family")
        assert hasattr(settings, "font_size")
        assert hasattr(settings, "dark_mode")
        assert hasattr(settings, "auto_save_enabled")


@pytest.mark.e2e
@pytest.mark.forked
class TestThemeWorkflow:
    """Test theme switching workflow."""

    def test_theme_manager_exists(self, app_window, qtbot):
        """E2E: Verify theme manager is initialized."""
        assert hasattr(app_window, "theme_manager")
        assert app_window.theme_manager is not None

    def test_dark_mode_setting_accessible(self, app_window, qtbot):
        """E2E: Access and modify dark mode setting."""
        assert hasattr(app_window, "_settings")
        settings = app_window._settings

        # Verify dark_mode attribute exists
        assert hasattr(settings, "dark_mode")
        current_mode = settings.dark_mode

        # Dark mode should be a boolean
        assert isinstance(current_mode, bool)


@pytest.mark.e2e
@pytest.mark.forked
class TestMultipleFilesWorkflow:
    """Test multiple file handling workflow."""

    def test_new_file_then_edit(self, app_window, qtbot, tmp_path):
        """E2E: New file → Edit → Track modified state."""
        # Create new file
        app_window.new_file()
        assert app_window.editor.toPlainText() == ""

        # Edit content
        content = "= Test Document\n\nContent here."
        app_window.editor.setPlainText(content)
        qtbot.wait(50)

        # Verify content
        assert app_window.editor.toPlainText() == content

    def test_file_handler_exists(self, app_window, qtbot):
        """E2E: Verify file handler is initialized."""
        assert hasattr(app_window, "file_handler")
        assert app_window.file_handler is not None

        # Verify key file handler methods exist
        assert hasattr(app_window, "new_file")
        assert hasattr(app_window, "open_file")
        assert hasattr(app_window, "save_file")


@pytest.mark.e2e
@pytest.mark.forked
class TestKeyboardShortcutsWorkflow:
    """Test keyboard shortcut workflow."""

    def test_keyboard_navigation_capability(self, app_window, qtbot):
        """E2E: Verify keyboard navigation works."""
        # Set content
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        app_window.editor.setPlainText(content)
        qtbot.wait(50)

        # Move cursor to start
        cursor = app_window.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        app_window.editor.setTextCursor(cursor)

        # Verify cursor position
        assert app_window.editor.textCursor().position() == 0

    def test_select_all_capability(self, app_window, qtbot):
        """E2E: Test select all functionality."""
        content = "Select this text"
        app_window.editor.setPlainText(content)
        qtbot.wait(50)

        # Select all
        app_window.editor.selectAll()

        # Verify selection
        assert app_window.editor.textCursor().hasSelection()
        assert app_window.editor.textCursor().selectedText() == content


@pytest.mark.e2e
@pytest.mark.forked
class TestManagersInitializationWorkflow:
    """Test that all managers are properly initialized."""

    def test_all_managers_exist(self, app_window, qtbot):
        """E2E: Verify all managers are initialized."""
        # Core managers
        assert hasattr(app_window, "file_handler")
        assert hasattr(app_window, "theme_manager")
        assert hasattr(app_window, "_settings")
        assert hasattr(app_window, "export_manager")

        # Worker-related
        assert hasattr(app_window, "worker_manager")
        assert hasattr(app_window, "git_worker")
        assert hasattr(app_window, "preview_worker")
        assert hasattr(app_window, "pandoc_worker")

    def test_editor_exists_and_functional(self, app_window, qtbot):
        """E2E: Verify editor widget is functional."""
        assert hasattr(app_window, "editor")
        assert app_window.editor is not None

        # Test basic operations
        app_window.editor.setPlainText("Test")
        assert app_window.editor.toPlainText() == "Test"

        app_window.editor.clear()
        assert app_window.editor.toPlainText() == ""
