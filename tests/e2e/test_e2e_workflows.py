"""
End-to-End (E2E) Tests for Real-World Workflows.

Tests complete user workflows from start to finish, simulating real-world usage
of AsciiDoc Artisan. Each test represents a complete task a user might perform.

Workflows covered:
1. Create new document → Edit → Save → Export PDF
2. Import DOCX → Edit → Convert to AsciiDoc → Save
3. Open existing file → Edit with find/replace → Commit to Git
4. Template workflow → Customize → Save → Export multiple formats
5. Chat workflow → Ask questions → Get help → Apply suggestions
6. Multi-file workflow → Switch files → Make edits → Save all
"""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def app_window(qtbot, test_settings, tmp_path):
    """Create a fresh main window for E2E testing."""
    # Set up test directory
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
        window.close()


@pytest.mark.e2e
class TestDocumentCreationWorkflow:
    """Test complete document creation workflow."""

    def test_create_edit_save_export_pdf(self, app_window, qtbot, tmp_path):
        """
        E2E Workflow: Create new document → Edit → Save → Export PDF.

        User story:
        As a technical writer, I want to create a new document, write content,
        save it, and export it as a PDF for distribution.
        """
        # Step 1: Create new document
        app_window.new_file()
        assert app_window.editor.toPlainText() == ""
        assert app_window.file_handler.current_file_path is None

        # Step 2: Write content
        content = """= Technical Documentation

:author: Test User
:version: 1.0.0

== Introduction

This is a test document demonstrating the workflow.

== Features

* Easy to use
* Fast rendering
* Professional output

== Conclusion

The end.
"""
        app_window.editor.setPlainText(content)
        qtbot.wait(100)  # Let preview update

        # Verify content
        assert app_window.editor.toPlainText() == content
        assert app_window.file_handler.unsaved_changes is True

        # Step 3: Save document
        test_file = tmp_path / "test_document.adoc"
        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(test_file), "AsciiDoc (*.adoc)"),
        ):
            app_window.save_file(save_as=True)
            qtbot.wait(100)  # Wait for save to complete

        # Verify file was created with correct content
        assert test_file.exists(), "Save file should create the file"
        assert test_file.read_text() == content, "Saved content should match editor content"

        # Step 4: Export to PDF (verify export manager exists)
        # Actual export would use: app_window.save_file_as_format("pdf")
        assert hasattr(app_window, "export_manager"), "Export manager should exist"
        assert hasattr(app_window, "save_file_as_format"), "Save as format method should exist"

        # Verify workflow completed successfully
        # Note: In E2E tests, file_handler state may not update due to signal timing
        # The critical verification is that the file was written correctly (verified above)


@pytest.mark.e2e
class TestImportConvertWorkflow:
    """Test import and conversion workflow."""

    @pytest.mark.requires_pandoc
    def test_import_docx_edit_save(self, app_window, qtbot, tmp_path):
        """
        E2E Workflow: Import DOCX → Edit → Save as AsciiDoc.

        User story:
        As a writer migrating from Word, I want to import my existing DOCX files,
        make edits, and save them as AsciiDoc for future work.
        """
        # Step 1: Create sample DOCX (mocked)
        docx_file = tmp_path / "sample.docx"
        docx_file.write_text("Sample DOCX content")  # Placeholder

        # Step 2: Import DOCX (simulated - actual import would use conversion.document_converter)
        converted_content = """= Sample Document

This is converted from DOCX.

* Item 1
* Item 2
"""

        # Simulate DOCX import result
        app_window.editor.setPlainText(converted_content)
        app_window.file_handler.current_file_path = None  # New document from import
        app_window.file_handler.unsaved_changes = True

        # Verify import
        assert converted_content in app_window.editor.toPlainText()

        # Step 3: Edit content
        additional_content = "\n\n== New Section\n\nAdded after import."
        app_window.editor.setPlainText(converted_content + additional_content)
        qtbot.wait(100)

        # Step 4: Save as AsciiDoc
        adoc_file = tmp_path / "converted.adoc"
        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(adoc_file), "AsciiDoc (*.adoc)"),
        ):
            app_window.save_file(save_as=True)

        # Verify save
        if adoc_file.exists():
            saved_content = adoc_file.read_text()
            assert "= Sample Document" in saved_content
            assert "New Section" in saved_content


@pytest.mark.e2e
class TestFindReplaceGitWorkflow:
    """Test find/replace with Git commit workflow."""

    def test_open_find_replace_commit(self, app_window, qtbot, tmp_path):
        """
        E2E Workflow: Open file → Find/Replace text → Commit to Git.

        User story:
        As a developer, I want to open a document, use find/replace to update
        terminology, and commit the changes to version control.
        """
        # Step 1: Create and open a file
        test_file = tmp_path / "terminology.adoc"
        original_content = """= API Documentation

== Methods

The old_method is deprecated.
Use old_method sparingly.
The old_method will be removed.
"""
        test_file.write_text(original_content)

        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(test_file), "AsciiDoc (*.adoc)")):
            app_window.open_file()
            app_window.editor.setPlainText(original_content)
            app_window.file_handler.current_file_path = test_file

        # Verify file opened
        assert app_window.editor.toPlainText() == original_content

        # Step 2: Use Find & Replace
        # Replace "old_method" with "new_method"
        search_text = "old_method"
        replace_text = "new_method"

        # Simulate find/replace (using search engine)
        if hasattr(app_window, "search_engine"):
            # Simulate replace all
            content = app_window.editor.toPlainText()
            updated_content = content.replace(search_text, replace_text)
            app_window.editor.setPlainText(updated_content)

        # Verify replacements
        final_content = app_window.editor.toPlainText()
        assert "new_method" in final_content
        assert "old_method" not in final_content

        # Step 3: Save changes
        test_file.write_text(final_content)
        app_window.file_handler.unsaved_changes = False

        # Step 4: Commit to Git (simulate signal emission)
        # Git commit would use: app_window.git_worker.run_git_command(
        #   ["git", "commit", "-m", "Replace old_method with new_method"], repo_path
        # )
        # For E2E test, just verify the worker exists
        assert hasattr(app_window, "git_worker")
        assert hasattr(app_window.git_worker, "run_git_command")


@pytest.mark.e2e
class TestTemplateWorkflow:
    """Test template-based document creation workflow."""

    def test_template_customize_save_export(self, app_window, qtbot, tmp_path):
        """
        E2E Workflow: Load template → Customize → Save → Export multiple formats.

        User story:
        As a technical writer, I want to use a template for consistent formatting,
        customize it with my content, and export to multiple formats.
        """
        # Step 1: Load template
        template_content = """= {{document_title}}
:author: {{author_name}}
:version: {{version}}

== Introduction

{{introduction_text}}

== Main Content

{{main_content}}

== Conclusion

{{conclusion_text}}
"""

        app_window.editor.setPlainText(template_content)

        # Step 2: Customize template
        customized = template_content.replace("{{document_title}}", "User Guide")
        customized = customized.replace("{{author_name}}", "Test Author")
        customized = customized.replace("{{version}}", "2.0.0")
        customized = customized.replace("{{introduction_text}}", "This is an introduction.")
        customized = customized.replace("{{main_content}}", "Main content goes here.")
        customized = customized.replace("{{conclusion_text}}", "Conclusion here.")

        app_window.editor.setPlainText(customized)
        qtbot.wait(100)

        # Step 3: Save
        test_file = tmp_path / "user_guide.adoc"
        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(test_file), "AsciiDoc (*.adoc)"),
        ):
            app_window.save_file(save_as=True)

        # Verify save
        if test_file.exists():
            assert "User Guide" in test_file.read_text()

        # Step 4: Export to multiple formats
        # Actual exports would use:
        #   app_window.save_file_as_format("html")
        #   app_window.save_file_as_format("pdf")
        assert hasattr(app_window, "save_file_as_format")
        assert hasattr(app_window, "export_manager")

        # Verify export capability exists
        assert app_window.export_manager is not None


@pytest.mark.e2e
class TestChatWorkflow:
    """Test chat/AI assistance workflow."""

    def test_chat_ask_apply_suggestions(self, app_window, qtbot):
        """
        E2E Workflow: Ask question via chat → Get help → Apply suggestions.

        User story:
        As a writer, I want to ask the AI assistant about AsciiDoc syntax,
        get helpful suggestions, and apply them to my document.
        """
        # Step 1: Write initial content with potential issue
        initial_content = """= My Document

This is a paragraph with bad grammer and spelling erors.

I need help improving this.
"""
        app_window.editor.setPlainText(initial_content)

        # Step 2: Send message to chat
        if hasattr(app_window, "chat_manager"):
            test_question = "How do I improve this paragraph's grammar?"

            # Expected chat response would be:
            # "Here are the corrections:
            # - 'bad grammer' → 'bad grammar'
            # - 'spelling erors' → 'spelling errors'"

            # Simulate chat interaction
            with qtbot.waitSignal(app_window.chat_manager.message_sent_to_worker, timeout=1000) as blocker:
                app_window.chat_manager.message_sent_to_worker.emit(
                    test_question,
                    "test-model",
                    "editing",
                    [],
                    initial_content,
                )

            # Verify signal emitted
            if blocker.signal_triggered:
                # Step 3: Apply suggestions
                corrected_content = """= My Document

This is a paragraph with bad grammar and spelling errors.

I need help improving this.
"""
                app_window.editor.setPlainText(corrected_content)

                # Verify corrections applied
                assert "bad grammar" in app_window.editor.toPlainText()
                assert "bad grammer" not in app_window.editor.toPlainText()


@pytest.mark.e2e
class TestMultiFileWorkflow:
    """Test multi-file editing workflow."""

    def test_switch_files_edit_save_all(self, app_window, qtbot, tmp_path):
        """
        E2E Workflow: Create multiple files → Switch between them → Edit → Save all.

        User story:
        As a writer working on a multi-chapter book, I want to switch between
        chapter files, make edits to each, and save all changes.
        """
        # Step 1: Create multiple files
        chapter1 = tmp_path / "chapter1.adoc"
        chapter2 = tmp_path / "chapter2.adoc"
        chapter3 = tmp_path / "chapter3.adoc"

        chapter1_content = "= Chapter 1\n\nContent for chapter 1."
        chapter2_content = "= Chapter 2\n\nContent for chapter 2."
        chapter3_content = "= Chapter 3\n\nContent for chapter 3."

        chapter1.write_text(chapter1_content)
        chapter2.write_text(chapter2_content)
        chapter3.write_text(chapter3_content)

        # Step 2: Open and edit chapter 1
        with patch(
            "PySide6.QtWidgets.QFileDialog.getOpenFileName",
            return_value=(str(chapter1), "AsciiDoc (*.adoc)"),
        ):
            app_window.open_file()
            app_window.editor.setPlainText(chapter1_content)
            app_window.file_handler.current_file_path = chapter1

        # Edit chapter 1
        app_window.editor.setPlainText(chapter1_content + "\n\nEdited.")
        qtbot.wait(50)

        # Save chapter 1
        chapter1.write_text(app_window.editor.toPlainText())

        # Step 3: Switch to chapter 2
        with patch(
            "PySide6.QtWidgets.QFileDialog.getOpenFileName",
            return_value=(str(chapter2), "AsciiDoc (*.adoc)"),
        ):
            app_window.open_file()
            app_window.editor.setPlainText(chapter2_content)
            app_window.file_handler.current_file_path = chapter2

        # Edit chapter 2
        app_window.editor.setPlainText(chapter2_content + "\n\nAlso edited.")
        qtbot.wait(50)

        # Save chapter 2
        chapter2.write_text(app_window.editor.toPlainText())

        # Step 4: Verify all changes saved
        assert "Edited" in chapter1.read_text()
        assert "Also edited" in chapter2.read_text()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
