"""E2E Tests for document export workflows."""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def app_window_with_content(qtbot, test_settings, tmp_path):
    """Create main window with document content."""
    test_settings.last_directory = str(tmp_path)

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

        # Set test content
        window.editor.setPlainText("""= Export Test Document
:author: Test Author

== Introduction

This document tests export functionality.

== Code Example

[source,python]
----
def hello():
    return "Hello World"
----

== Conclusion

Export complete.
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
class TestExportManagerWorkflow:
    """Test export manager initialization and capabilities."""

    def test_export_manager_exists(self, app_window_with_content, qtbot):
        """E2E: Verify export manager is initialized."""
        assert hasattr(app_window_with_content, "export_manager")
        assert app_window_with_content.export_manager is not None

    def test_export_formats_available(self, app_window_with_content, qtbot):
        """E2E: Verify export format methods exist."""
        assert hasattr(app_window_with_content, "save_file_as_format")

        # Check action manager has export actions
        if hasattr(app_window_with_content, "action_manager"):
            am = app_window_with_content.action_manager
            assert hasattr(am, "save_as_html_act")
            assert hasattr(am, "save_as_adoc_act")


@pytest.mark.e2e
@pytest.mark.forked
class TestHTMLExportWorkflow:
    """Test HTML export workflow."""

    def test_html_export_capability(self, app_window_with_content, qtbot, tmp_path):
        """E2E: Test HTML export functionality."""
        # Verify export action exists
        if hasattr(app_window_with_content, "action_manager"):
            am = app_window_with_content.action_manager
            assert hasattr(am, "save_as_html_act")

        # Test export with mocked dialog
        html_file = tmp_path / "export.html"
        with patch(
            "PySide6.QtWidgets.QFileDialog.getSaveFileName",
            return_value=(str(html_file), "HTML (*.html)"),
        ):
            app_window_with_content.save_file_as_format("html")


@pytest.mark.e2e
@pytest.mark.forked
class TestPDFExportWorkflow:
    """Test PDF export workflow."""

    def test_pdf_export_capability(self, app_window_with_content, qtbot):
        """E2E: Test PDF export capability exists."""
        if hasattr(app_window_with_content, "action_manager"):
            am = app_window_with_content.action_manager
            assert hasattr(am, "save_as_pdf_act")

    def test_pandoc_availability_check(self, app_window_with_content, qtbot):
        """E2E: Verify Pandoc availability check."""
        from asciidoc_artisan.core.constants import is_pandoc_available

        # Function should exist and return boolean
        result = is_pandoc_available()
        assert isinstance(result, bool)


@pytest.mark.e2e
@pytest.mark.forked
class TestMarkdownExportWorkflow:
    """Test Markdown export workflow."""

    def test_markdown_export_capability(self, app_window_with_content, qtbot):
        """E2E: Test Markdown export capability exists."""
        if hasattr(app_window_with_content, "action_manager"):
            am = app_window_with_content.action_manager
            assert hasattr(am, "save_as_md_act")


@pytest.mark.e2e
@pytest.mark.forked
class TestDOCXExportWorkflow:
    """Test DOCX export workflow."""

    def test_docx_export_capability(self, app_window_with_content, qtbot):
        """E2E: Test DOCX export capability exists."""
        if hasattr(app_window_with_content, "action_manager"):
            am = app_window_with_content.action_manager
            assert hasattr(am, "save_as_docx_act")
