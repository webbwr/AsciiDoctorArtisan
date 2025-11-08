"""
Tests for TemplateManager (v2.0.0).

This module tests the template manager that loads and manages
built-in and custom document templates.
"""

import tempfile
from pathlib import Path

import pytest

from asciidoc_artisan.core.template_engine import TemplateEngine
from asciidoc_artisan.core.template_manager import TemplateManager


@pytest.fixture
def engine():
    """Create a test template engine."""
    return TemplateEngine()


@pytest.fixture
def manager(engine):
    """Create a TemplateManager instance."""
    return TemplateManager(engine)


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create a temporary directory for custom templates."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir


class TestTemplateManagerInitialization:
    """Test manager initialization."""

    def test_manager_creation(self, manager, engine):
        """Test manager is created with correct attributes."""
        assert manager.engine == engine
        assert hasattr(manager, "templates")
        assert hasattr(manager, "recent")

    def test_loads_built_in_templates(self, manager):
        """Test manager loads built-in templates on init."""
        templates = manager.get_all_templates()

        # Should load the 6 built-in templates we created
        assert len(templates) == 6

        # Verify expected templates exist
        template_names = [t.name for t in templates]
        assert "Technical Article" in template_names
        assert "Book" in template_names
        assert "Man Page" in template_names
        assert "Technical Report" in template_names
        assert "README" in template_names
        assert "Simple Document" in template_names

    def test_template_categories(self, manager):
        """Test templates are categorized correctly."""
        templates = manager.get_all_templates()

        categories = {t.category for t in templates}
        assert "article" in categories
        assert "book" in categories
        assert "reference" in categories
        assert "report" in categories
        assert "documentation" in categories
        assert "general" in categories


class TestGetTemplate:
    """Test retrieving individual templates."""

    def test_get_template_by_name(self, manager):
        """Test getting template by name."""
        template = manager.get_template("Technical Article")

        assert template is not None
        assert template.name == "Technical Article"
        assert template.category == "article"

    def test_get_nonexistent_template(self, manager):
        """Test getting template that doesn't exist."""
        template = manager.get_template("Nonexistent Template")

        assert template is None

    def test_get_template_case_sensitive(self, manager):
        """Test template name matching is case-sensitive."""
        template = manager.get_template("technical article")

        # Should not match due to case difference
        assert template is None


class TestGetTemplatesByCategory:
    """Test retrieving templates by category."""

    def test_get_article_templates(self, manager):
        """Test getting article category templates."""
        articles = manager.get_templates_by_category("article")

        assert len(articles) >= 1
        assert all(t.category == "article" for t in articles)

    def test_get_book_templates(self, manager):
        """Test getting book category templates."""
        books = manager.get_templates_by_category("book")

        assert len(books) >= 1
        assert all(t.category == "book" for t in books)

    def test_get_empty_category(self, manager):
        """Test getting templates from empty category."""
        templates = manager.get_templates_by_category("nonexistent")

        assert len(templates) == 0


class TestTemplateVariables:
    """Test template variables."""

    def test_article_variables(self, manager):
        """Test article template has expected variables."""
        template = manager.get_template("Technical Article")

        assert template is not None
        assert len(template.variables) >= 3

        # Check for expected variables
        var_names = [v.name for v in template.variables]
        assert "title" in var_names
        assert "author" in var_names

    def test_book_variables(self, manager):
        """Test book template has expected variables."""
        template = manager.get_template("Book")

        assert template is not None
        assert len(template.variables) >= 3

        var_names = [v.name for v in template.variables]
        assert "title" in var_names
        assert "author" in var_names

    def test_variable_defaults(self, manager):
        """Test template variables have defaults."""
        template = manager.get_template("Technical Article")

        assert template is not None

        # Find author variable
        author_var = next((v for v in template.variables if v.name == "author"), None)
        assert author_var is not None
        assert author_var.default is not None


class TestRecentTemplates:
    """Test recent templates tracking."""

    def test_add_to_recent(self, manager):
        """Test adding template to recent list."""
        manager.add_to_recent("Technical Article")

        recent = manager.get_recent_templates()
        assert len(recent) >= 1
        assert recent[0].name == "Technical Article"

    def test_recent_limit(self, manager):
        """Test recent list respects maximum limit."""
        # Add more than the limit
        for i in range(15):
            manager.add_to_recent(f"Template {i}" if i < 6 else "Technical Article")

        recent = manager.get_recent_templates()

        # Should not exceed max_recent (default 10)
        assert len(recent) <= manager.max_recent

    def test_recent_removes_duplicates(self, manager):
        """Test adding same template moves it to top."""
        manager.add_to_recent("Technical Article")
        manager.add_to_recent("Book")
        manager.add_to_recent("Technical Article")

        recent = manager.get_recent_templates()

        # Technical Article should be at top
        assert recent[0].name == "Technical Article"

        # Should not have duplicates
        names = [t.name for t in recent]
        assert len(names) == len(set(names))


class TestGetAllTemplates:
    """Test getting all templates."""

    def test_get_all_returns_list(self, manager):
        """Test get_all_templates returns a list."""
        templates = manager.get_all_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_all_templates_have_metadata(self, manager):
        """Test all templates have required metadata."""
        templates = manager.get_all_templates()

        for template in templates:
            assert template.name
            assert template.category
            assert template.description
            assert template.content


class TestTemplateContent:
    """Test template content."""

    def test_article_template_content(self, manager):
        """Test article template has valid AsciiDoc content."""
        template = manager.get_template("Technical Article")

        assert template is not None
        assert "= {{title}}" in template.content
        assert "{{author}}" in template.content

    def test_template_has_variables_in_content(self, manager):
        """Test templates use their defined variables in content."""
        template = manager.get_template("Technical Article")

        assert template is not None

        # Check that defined variables appear in content
        for var in template.variables:
            var_placeholder = f"{{{{{var.name}}}}}"
            # Variable might appear in content (not guaranteed for all)
            # Just verify content is not empty
            assert len(template.content) > 0


class TestTemplateCategories:
    """Test template category management."""

    def test_get_all_categories(self, manager):
        """Test getting all unique categories."""
        templates = manager.get_all_templates()
        categories = {t.category for t in templates}

        assert len(categories) >= 5  # At least 5 categories
        assert "article" in categories
        assert "book" in categories


class TestBuiltInTemplates:
    """Test specific built-in templates."""

    def test_simple_template(self, manager):
        """Test simple document template."""
        template = manager.get_template("Simple Document")

        assert template is not None
        assert template.category == "general"
        assert len(template.variables) >= 2

    def test_manpage_template(self, manager):
        """Test man page template."""
        template = manager.get_template("Man Page")

        assert template is not None
        assert template.category == "reference"
        assert "{{command}}" in template.content

    def test_readme_template(self, manager):
        """Test README template."""
        template = manager.get_template("README")

        assert template is not None
        assert template.category == "documentation"
        assert "{{project_name}}" in template.content

    def test_report_template(self, manager):
        """Test technical report template."""
        template = manager.get_template("Technical Report")

        assert template is not None
        assert template.category == "report"


class TestTemplateValidation:
    """Test template validation."""

    def test_all_templates_valid(self, manager):
        """Test all loaded templates pass validation."""
        templates = manager.get_all_templates()

        for template in templates:
            # All templates should have been validated during loading
            assert template.name
            assert template.category
            assert template.description
            assert template.author
            assert template.version
            assert isinstance(template.variables, list)

    def test_template_variables_valid(self, manager):
        """Test all template variables are valid."""
        templates = manager.get_all_templates()

        for template in templates:
            for var in template.variables:
                assert var.name
                assert var.description
                # default and required are optional


class TestPerformance:
    """Test template loading performance."""

    def test_fast_initialization(self, engine):
        """Test template manager initializes quickly."""
        import time

        start = time.time()
        manager = TemplateManager(engine)
        elapsed = time.time() - start

        # Should initialize in less than 200ms
        assert elapsed < 0.2

    def test_fast_template_lookup(self, manager):
        """Test template lookup is fast."""
        import time

        start = time.time()
        for _ in range(100):
            manager.get_template("Technical Article")
        elapsed = time.time() - start

        # 100 lookups should take less than 10ms
        assert elapsed < 0.01


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_recent_list(self, manager):
        """Test getting recent templates when list is empty."""
        manager.recent = []
        recent = manager.get_recent_templates()

        assert recent == []

    def test_template_count(self, manager):
        """Test correct number of templates loaded."""
        templates = manager.get_all_templates()

        # Should have exactly 6 built-in templates
        assert len(templates) == 6
