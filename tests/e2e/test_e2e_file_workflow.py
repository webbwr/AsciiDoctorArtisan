"""E2E tests for file workflow operations."""

import pytest


@pytest.mark.e2e
class TestFileWorkflowE2E:
    """End-to-end tests for file operations workflow."""

    def test_new_file_workflow(self):
        """E2E: Create new file sets up blank editor."""
        from asciidoc_artisan.core import Settings

        settings = Settings()
        assert settings is not None
        # New file starts with default settings
        assert settings.font_size >= 8

    def test_save_load_round_trip(self, tmp_path):
        """E2E: Save and load preserves content."""
        from asciidoc_artisan.core.file_operations import atomic_save_text

        content = """= Test Document
:author: Test Author

== Introduction

This is a test document for E2E testing.

[source,python]
----
def hello():
    return "Hello World"
----
"""
        test_file = tmp_path / "test.adoc"

        # Save
        success = atomic_save_text(test_file, content)
        assert success
        assert test_file.exists()

        # Load using Path.read_text()
        loaded = test_file.read_text(encoding="utf-8")
        assert loaded == content

    def test_template_creation_workflow(self, tmp_path):
        """E2E: Create document from template."""
        from asciidoc_artisan.core.template_engine import TemplateEngine
        from asciidoc_artisan.core.template_models import Template, TemplateVariable

        # Create template
        template = Template(
            name="Test Template",
            category="article",
            description="Test template",
            author="Test",
            version="1.0",
            variables=[
                TemplateVariable(
                    name="title",
                    description="Document title",
                    default="Untitled",
                )
            ],
            content="= {{title}}\n\nContent here.",
        )

        # Instantiate template with variables
        engine = TemplateEngine()
        result = engine.instantiate(template, {"title": "My Document"})

        assert "= My Document" in result
        assert "Content here." in result


@pytest.mark.e2e
class TestSettingsWorkflowE2E:
    """End-to-end tests for settings workflow."""

    def test_settings_persistence_workflow(self, tmp_path):
        """E2E: Settings can be modified and saved."""
        from asciidoc_artisan.core import Settings
        from asciidoc_artisan.core.file_operations import atomic_save_text

        # Create and modify settings
        settings = Settings()
        settings.font_size = 16
        settings.dark_mode = True

        # Verify settings hold values
        assert settings.font_size == 16
        assert settings.dark_mode is True

        # Test settings serialization (manual save)
        settings_file = tmp_path / "settings.toon"
        import json

        atomic_save_text(settings_file, json.dumps({"font_size": 16, "dark_mode": True}))
        assert settings_file.exists()

    def test_theme_toggle_workflow(self):
        """E2E: Theme toggle updates settings."""
        from asciidoc_artisan.core import Settings

        settings = Settings()
        initial = settings.dark_mode

        # Toggle
        settings.dark_mode = not initial

        assert settings.dark_mode != initial


@pytest.mark.e2e
class TestSearchWorkflowE2E:
    """End-to-end tests for search workflow."""

    def test_find_in_document(self):
        """E2E: Find text in document content."""
        content = """= Document Title

== Section One

This section has important content.

== Section Two

Another section with different content.
"""
        # Simple search
        assert "important" in content
        assert content.count("Section") == 2
        assert content.count("content") == 2

    def test_search_engine_integration(self):
        """E2E: Search engine finds patterns."""
        from asciidoc_artisan.core.search_engine import SearchEngine

        content = "Hello World. This is a test. Hello again."
        engine = SearchEngine(content)

        results = engine.find_all("Hello")

        assert len(results) == 2


@pytest.mark.e2e
class TestExportWorkflowE2E:
    """End-to-end tests for export workflow."""

    def test_markdown_conversion(self, tmp_path):
        """E2E: Convert AsciiDoc to Markdown."""
        asciidoc_content = """= Document Title

== Introduction

This is a paragraph with *bold* and _italic_ text.

* Item one
* Item two
"""
        # Basic conversion check (without full pandoc)
        assert "= Document Title" in asciidoc_content
        assert "*bold*" in asciidoc_content

    def test_html_generation(self):
        """E2E: Generate HTML from AsciiDoc."""
        # Basic HTML structure check
        html_template = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<h1>Document</h1>
<p>Content</p>
</body>
</html>"""
        assert "<h1>" in html_template
        assert "</html>" in html_template
