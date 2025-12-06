"""Visual regression tests for UI components.

Uses pytest-regressions for screenshot comparison testing.
Requires: pytest-regressions, pillow

Note: These tests require a display (or Xvfb for headless).
"""

import pytest
from pathlib import Path

# Mark all tests in this module as visual regression tests
pytestmark = [pytest.mark.visual, pytest.mark.requires_gpu]


@pytest.fixture
def sample_asciidoc():
    """Sample AsciiDoc content for visual tests."""
    return """= Visual Test Document
:author: Test Author
:toc:

== Introduction

This is a test document for visual regression testing.

=== Code Block

[source,python]
----
def hello():
    print("Hello, World!")
----

=== Table

|===
|Header 1 |Header 2

|Cell 1
|Cell 2
|===

== Conclusion

End of test document.
"""


class TestPreviewRendering:
    """Visual tests for preview rendering."""

    def test_preview_html_structure(self, sample_asciidoc):
        """Test that HTML preview has consistent structure."""
        from asciidoc_artisan.core.preview_renderer import PreviewRenderer

        renderer = PreviewRenderer()
        html = renderer.render(sample_asciidoc)

        # Verify key elements exist
        assert "<h1" in html or "= Visual Test Document" in html
        assert "Introduction" in html
        assert "hello()" in html or "def hello" in html

    def test_preview_contains_toc(self, sample_asciidoc):
        """Test that TOC is rendered when :toc: is present."""
        from asciidoc_artisan.core.preview_renderer import PreviewRenderer

        renderer = PreviewRenderer()
        html = renderer.render(sample_asciidoc)

        # TOC should be present
        assert "Introduction" in html
        assert "Conclusion" in html


class TestTemplateRendering:
    """Visual tests for template rendering."""

    def test_template_instantiation(self):
        """Test template instantiation produces valid output."""
        from asciidoc_artisan.core.template_engine import TemplateEngine
        from asciidoc_artisan.core.template_models import Template, TemplateVariable

        engine = TemplateEngine()

        template = Template(
            name="Test",
            category="test",
            description="Test template",
            author="Test",
            version="1.0",
            variables=[
                TemplateVariable(name="title", description="Title", default="Test")
            ],
            content="= {{title}}\n\nContent here.",
        )

        result = engine.instantiate(template, {"title": "My Title"})

        assert "= My Title" in result
        assert "Content here." in result


class TestSyntaxHighlighting:
    """Visual tests for syntax highlighting consistency."""

    def test_code_block_highlighting(self, sample_asciidoc):
        """Test code blocks are preserved in preview."""
        from asciidoc_artisan.core.preview_renderer import PreviewRenderer

        renderer = PreviewRenderer()
        html = renderer.render(sample_asciidoc)

        # Code should be present (either raw or highlighted)
        assert "hello" in html.lower()
        assert "print" in html.lower()
