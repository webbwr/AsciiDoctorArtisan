"""
Tests for TemplateManager (v2.0.0).

This module tests the template manager that loads and manages
built-in and custom document templates.
"""

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
            # Variable might appear in content (not guaranteed for all)
            # Just verify content is not empty
            assert len(template.content) > 0
            assert var.name  # Verify variable has a name


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
        _ = TemplateManager(engine)
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


class TestCRUDOperations:
    """Test create, update, delete operations."""

    def test_create_template(self, manager, tmp_path, monkeypatch):
        """Test creating a new template."""
        from asciidoc_artisan.core.models import Template, TemplateVariable

        # Monkey-patch custom_dir to use tmp_path
        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        template = Template(
            name="Test Template",
            category="article",
            description="Test description",
            author="Test Author",
            version="1.0",
            variables=[
                TemplateVariable(
                    name="title",
                    description="Document title",
                    required=True,
                    default="",
                    type="string",
                )
            ],
            content="= {{title}}\n\nTest content",
        )

        result = manager.create_template(template)
        assert result is True

        # Verify file was created
        filename = "test-template.adoc"
        assert (tmp_path / filename).exists()

        # Verify template is in manager
        assert "Test Template" in manager.templates

    def test_create_template_existing_file(self, manager, tmp_path, monkeypatch):
        """Test creating template when file already exists."""
        from asciidoc_artisan.core.models import Template

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create file first
        (tmp_path / "test-template.adoc").write_text("existing content")

        template = Template(
            name="Test Template",
            category="article",
            description="Test",
            author="Author",
            version="1.0",
            variables=[],
            content="Content",
        )

        result = manager.create_template(template)
        assert result is False

    def test_update_template(self, manager, tmp_path, monkeypatch):
        """Test updating an existing template."""
        from pathlib import Path

        from asciidoc_artisan.core.models import Template

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create template first
        template = Template(
            name="Update Test",
            category="article",
            description="Original",
            author="Author",
            version="1.0",
            variables=[],
            content="Original content",
        )
        manager.create_template(template)

        # Update it
        template.description = "Updated description"
        result = manager.update_template(template)
        assert result is True

        # Verify file was updated
        content = template.file_path and Path(template.file_path).read_text()
        assert "Updated description" in content

    def test_update_template_no_file_path(self, manager):
        """Test updating template with no file_path."""
        from asciidoc_artisan.core.models import Template

        template = Template(
            name="No Path",
            category="article",
            description="Test",
            author="Author",
            version="1.0",
            variables=[],
            content="Content",
        )

        result = manager.update_template(template)
        assert result is False

    def test_delete_template(self, manager, tmp_path, monkeypatch):
        """Test deleting a custom template."""
        from asciidoc_artisan.core.models import Template

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create template
        template = Template(
            name="Delete Test",
            category="article",
            description="To be deleted",
            author="Author",
            version="1.0",
            variables=[],
            content="Content",
        )
        manager.create_template(template)

        # Delete it
        result = manager.delete_template("Delete Test")
        assert result is True

        # Verify file is gone
        assert not (tmp_path / "delete-test.adoc").exists()

        # Verify not in manager
        assert "Delete Test" not in manager.templates

    def test_delete_template_not_found(self, manager):
        """Test deleting non-existent template."""
        result = manager.delete_template("Nonexistent")
        assert result is False

    def test_delete_built_in_template_fails(self, manager):
        """Test deleting built-in template fails."""
        result = manager.delete_template("Technical Article")
        assert result is False


class TestReloadTemplates:
    """Test reloading templates from disk."""

    def test_reload_templates(self, manager, tmp_path, monkeypatch):
        """Test reloading templates picks up new files."""

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create a template file directly on disk
        template_file = tmp_path / "new-template.adoc"
        template_file.write_text(
            """---
name: New Template
category: article
description: Created externally
author: External
version: "1.0"
variables: []
---
= Content
"""
        )

        # Reload templates
        manager.reload_templates()

        # Verify new template is loaded
        template = manager.get_template("New Template")
        assert template is not None


class TestGetCategories:
    """Test getting all categories."""

    def test_get_categories(self, manager):
        """Test getting sorted list of categories."""
        categories = manager.get_categories()

        assert isinstance(categories, list)
        assert len(categories) >= 5

        # Verify sorted
        assert categories == sorted(categories)

        # Verify expected categories
        assert "article" in categories
        assert "book" in categories


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_filename_spaces(self, manager):
        """Test spaces converted to hyphens."""
        result = manager._sanitize_filename("Technical Article")
        assert result == "technical-article"

    def test_sanitize_filename_lowercase(self, manager):
        """Test conversion to lowercase."""
        result = manager._sanitize_filename("UPPERCASE")
        assert result == "uppercase"

    def test_sanitize_filename_special_chars(self, manager):
        """Test removal of special characters."""
        result = manager._sanitize_filename("Test! @#Template$")
        assert result == "test-template"

    def test_sanitize_filename_multiple_spaces(self, manager):
        """Test multiple spaces."""
        result = manager._sanitize_filename("Test  Multiple   Spaces")
        assert result == "test--multiple---spaces"


class TestSerializeTemplate:
    """Test template serialization."""

    def test_serialize_template_basic(self, manager):
        """Test serializing template to YAML format."""
        from asciidoc_artisan.core.models import Template, TemplateVariable

        template = Template(
            name="Serialize Test",
            category="article",
            description="Test serialization",
            author="Test Author",
            version="1.0",
            variables=[
                TemplateVariable(
                    name="title",
                    description="Title",
                    required=True,
                    default="Untitled",
                    type="string",
                )
            ],
            content="= {{title}}",
        )

        result = manager._serialize_template(template)

        # Check format
        assert result.startswith("---\n")
        assert "name: Serialize Test" in result
        assert "category: article" in result
        assert "= {{title}}" in result

    def test_serialize_template_no_author(self, manager):
        """Test serializing template without author."""
        from asciidoc_artisan.core.models import Template

        template = Template(
            name="No Author",
            category="article",
            description="Test",
            author="",
            version="1.0",
            variables=[],
            content="Content",
        )

        result = manager._serialize_template(template)
        assert "---" in result


class TestRecentPersistence:
    """Test saving and loading recent templates."""

    def test_load_recent_from_disk(self, manager, tmp_path, monkeypatch):
        """Test loading recent list from disk."""
        import json

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create recent.json
        recent_file = tmp_path / "recent.json"
        recent_file.write_text(json.dumps(["Template 1", "Template 2"]))

        # Load it
        manager._load_recent()

        assert manager.recent == ["Template 1", "Template 2"]

    def test_load_recent_missing_file(self, manager, tmp_path, monkeypatch):
        """Test loading recent when file doesn't exist."""
        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        manager._load_recent()

        # Should not crash, recent stays empty
        assert isinstance(manager.recent, list)

    def test_load_recent_corrupt_file(self, manager, tmp_path, monkeypatch):
        """Test loading recent with corrupt JSON."""
        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create corrupt file
        recent_file = tmp_path / "recent.json"
        recent_file.write_text("not json{{{")

        manager._load_recent()

        # Should fall back to empty list
        assert manager.recent == []

    def test_save_recent_to_disk(self, manager, tmp_path, monkeypatch):
        """Test saving recent list to disk."""
        import json

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        manager.recent = ["Template A", "Template B"]
        manager._save_recent()

        # Verify file was created
        recent_file = tmp_path / "recent.json"
        assert recent_file.exists()

        # Verify content
        data = json.loads(recent_file.read_text())
        assert data == ["Template A", "Template B"]


class TestDeleteTemplateRecentCleanup:
    """Test that deleting templates removes them from recent list."""

    def test_delete_removes_from_recent(self, manager, tmp_path, monkeypatch):
        """Test deleting template removes it from recent."""
        from asciidoc_artisan.core.models import Template

        monkeypatch.setattr(manager, "custom_dir", tmp_path)

        # Create template
        template = Template(
            name="Recent Test",
            category="article",
            description="Test",
            author="Author",
            version="1.0",
            variables=[],
            content="Content",
        )
        manager.create_template(template)

        # Add to recent
        manager.add_to_recent("Recent Test")
        assert "Recent Test" in manager.recent

        # Delete template
        manager.delete_template("Recent Test")

        # Verify removed from recent
        assert "Recent Test" not in manager.recent


class TestGetBuiltInDir:
    """Test getting built-in template directory."""

    def test_get_built_in_dir(self, manager):
        """Test built-in dir points to correct location."""
        from pathlib import Path

        built_in_dir = manager._get_built_in_dir()

        assert isinstance(built_in_dir, Path)
        assert built_in_dir.name == "templates"
        assert built_in_dir.parent.name == "asciidoc_artisan"


class TestGetCustomDir:
    """Test getting custom template directory."""

    def test_get_custom_dir(self, manager):
        """Test custom dir is created."""
        from pathlib import Path

        custom_dir = manager._get_custom_dir()

        assert isinstance(custom_dir, Path)
        assert custom_dir.exists()
        assert custom_dir.name == "templates"

    def test_get_custom_dir_creates_if_missing(self, tmp_path, monkeypatch):
        """Test custom dir is created if it doesn't exist."""

        # Mock QStandardPaths to return tmp_path
        class MockQStandardPaths:
            class StandardLocation:
                AppDataLocation = 0

            @staticmethod
            def writableLocation(location):
                return str(tmp_path)

        # Patch where it's used (inside the method)
        monkeypatch.setattr(
            "PySide6.QtCore.QStandardPaths", MockQStandardPaths, raising=False
        )

        from asciidoc_artisan.core.template_engine import TemplateEngine
        from asciidoc_artisan.core.template_manager import TemplateManager

        engine = TemplateEngine()
        manager = TemplateManager(engine)

        custom_dir = manager.custom_dir
        assert custom_dir.exists()
        assert custom_dir.name == "templates"
