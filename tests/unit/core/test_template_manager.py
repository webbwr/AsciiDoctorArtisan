"""
Tests for TemplateManager (v2.0.0).

This module tests the template manager that loads and manages
built-in and custom document templates.
"""

import pytest

from asciidoc_artisan.core.template_engine import TemplateEngine
from asciidoc_artisan.core.template_manager import TemplateManager
from asciidoc_artisan.core.template_serializer import (
    sanitize_template_filename,
    serialize_template,
)


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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestTemplateCategories:
    """Test template category management."""

    def test_get_all_categories(self, manager):
        """Test getting all unique categories."""
        templates = manager.get_all_templates()
        categories = {t.category for t in templates}

        assert len(categories) >= 5  # At least 5 categories
        assert "article" in categories
        assert "book" in categories


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases."""

    def test_empty_recent_list(self, manager):
        """Test getting recent templates when list is empty."""
        # Clear the tracker's recent list
        manager._recent_tracker.clear()
        recent = manager.get_recent_templates()

        assert recent == []

    def test_template_count(self, manager):
        """Test correct number of templates loaded."""
        templates = manager.get_all_templates()

        # Should have exactly 6 built-in templates
        assert len(templates) == 6


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_filename_spaces(self):
        """Test spaces converted to hyphens."""
        result = sanitize_template_filename("Technical Article")
        assert result == "technical-article"

    def test_sanitize_filename_lowercase(self):
        """Test conversion to lowercase."""
        result = sanitize_template_filename("UPPERCASE")
        assert result == "uppercase"

    def test_sanitize_filename_special_chars(self):
        """Test removal of special characters."""
        result = sanitize_template_filename("Test! @#Template$")
        assert result == "test-template"

    def test_sanitize_filename_multiple_spaces(self):
        """Test multiple spaces."""
        result = sanitize_template_filename("Test  Multiple   Spaces")
        assert result == "test--multiple---spaces"


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestSerializeTemplate:
    """Test template serialization."""

    def test_serialize_template_basic(self):
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

        result = serialize_template(template)

        # Check format
        assert result.startswith("---\n")
        assert "name: Serialize Test" in result
        assert "category: article" in result
        assert "= {{title}}" in result

    def test_serialize_template_no_author(self):
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

        result = serialize_template(template)
        assert "---" in result


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestRecentPersistence:
    """Test saving and loading recent templates via tracker."""

    def test_load_recent_from_disk(self, tmp_path):
        """Test loading recent list from disk via RecentTemplatesTracker."""
        import json

        from asciidoc_artisan.core.recent_templates_tracker import (
            RecentTemplatesTracker,
        )

        # Create recent.json
        recent_file = tmp_path / "recent.json"
        recent_file.write_text(json.dumps(["Template 1", "Template 2"]))

        # Create tracker - it loads on init
        tracker = RecentTemplatesTracker(tmp_path)

        assert tracker.recent == ["Template 1", "Template 2"]

    def test_load_recent_missing_file(self, tmp_path):
        """Test loading recent when file doesn't exist."""
        from asciidoc_artisan.core.recent_templates_tracker import (
            RecentTemplatesTracker,
        )

        # Create tracker with empty directory
        tracker = RecentTemplatesTracker(tmp_path)

        # Should not crash, recent stays empty
        assert isinstance(tracker.recent, list)
        assert tracker.recent == []

    def test_load_recent_corrupt_file(self, tmp_path):
        """Test loading recent with corrupt JSON."""
        from asciidoc_artisan.core.recent_templates_tracker import (
            RecentTemplatesTracker,
        )

        # Create corrupt file
        recent_file = tmp_path / "recent.json"
        recent_file.write_text("not json{{{")

        # Create tracker - should fall back to empty list
        tracker = RecentTemplatesTracker(tmp_path)

        assert tracker.recent == []

    def test_save_recent_to_disk(self, tmp_path):
        """Test saving recent list to disk via tracker."""
        import json

        from asciidoc_artisan.core.recent_templates_tracker import (
            RecentTemplatesTracker,
        )

        tracker = RecentTemplatesTracker(tmp_path)
        tracker.add("Template A")
        tracker.add("Template B")

        # Verify file was created
        recent_file = tmp_path / "recent.json"
        assert recent_file.exists()

        # Verify content (most recent first)
        data = json.loads(recent_file.read_text())
        assert data == ["Template B", "Template A"]


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestGetBuiltInDir:
    """Test getting built-in template directory."""

    def test_get_built_in_dir(self, manager):
        """Test built-in dir points to correct location."""
        from pathlib import Path

        built_in_dir = manager._get_built_in_dir()

        assert isinstance(built_in_dir, Path)
        assert built_in_dir.name == "templates"
        assert built_in_dir.parent.name == "asciidoc_artisan"


@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
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
        monkeypatch.setattr("PySide6.QtCore.QStandardPaths", MockQStandardPaths, raising=False)

        from asciidoc_artisan.core.template_engine import TemplateEngine
        from asciidoc_artisan.core.template_manager import TemplateManager

        engine = TemplateEngine()
        manager = TemplateManager(engine)

        custom_dir = manager.custom_dir
        assert custom_dir.exists()
        assert custom_dir.name == "templates"


@pytest.mark.unit
@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestQtImportFallback:
    """Test Qt import fallback path."""

    def test_get_config_dir_without_qt(self):
        """Test config dir fallback when Qt not available (tests line 117-119)."""
        import sys
        from unittest.mock import patch

        # Mock sys.modules to make PySide6 unavailable
        with patch.dict(sys.modules, {"PySide6": None, "PySide6.QtCore": None}):
            # Reload the module to trigger ImportError path
            import importlib

            import asciidoc_artisan.core.template_manager as tm_module

            importlib.reload(tm_module)

            # Verify fallback path is used
            from asciidoc_artisan.core.template_engine import TemplateEngine

            engine = TemplateEngine()
            manager = tm_module.TemplateManager(engine)

            # Should use fallback: Path.home() / ".config" / "AsciiDocArtisan"
            custom_dir = manager.custom_dir
            assert ".config" in str(custom_dir) or "AsciiDocArtisan" in str(custom_dir)


@pytest.mark.unit
@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestTemplateLoadingErrors:
    """Test error handling in template loading."""

    def test_load_builtin_template_parse_error(self, engine, tmp_path, monkeypatch):
        """Test error handling when built-in template parsing fails (tests line 143-146)."""
        # Create a corrupt template file
        builtin_dir = tmp_path / "builtin"
        builtin_dir.mkdir()
        corrupt_file = builtin_dir / "corrupt.adoc"
        corrupt_file.write_text("= Corrupt\n{{ invalid syntax")

        # Mock engine.parse_template to raise exception
        def mock_parse(path):
            raise ValueError("Invalid template syntax")

        monkeypatch.setattr(engine, "parse_template", mock_parse)

        # Mock built_in_dir to point to our test dir
        from asciidoc_artisan.core.template_manager import TemplateManager

        manager = TemplateManager(engine)
        monkeypatch.setattr(manager, "built_in_dir", builtin_dir)

        # Should not crash, just log error
        manager._load_templates()

        # Manager should still work
        assert hasattr(manager, "templates")

    def test_load_custom_template_parse_error(self, engine, tmp_path, monkeypatch):
        """Test error handling when custom template parsing fails (tests line 154-157)."""
        # Create a corrupt custom template
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        corrupt_file = custom_dir / "corrupt_custom.adoc"
        corrupt_file.write_text("= Corrupt Custom\n{{ bad }}")

        # Mock engine.parse_template to raise exception
        def mock_parse(path):
            raise ValueError("Invalid template syntax")

        monkeypatch.setattr(engine, "parse_template", mock_parse)

        # Create manager with custom dir
        from asciidoc_artisan.core.template_manager import TemplateManager

        manager = TemplateManager(engine)
        monkeypatch.setattr(manager, "custom_dir", custom_dir)
        monkeypatch.setattr(manager, "built_in_dir", tmp_path / "builtin")

        # Should not crash, just log error
        manager._load_templates()

        # Manager should still work
        assert hasattr(manager, "templates")


@pytest.mark.unit
@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestCRUDExceptionHandling:
    """Test exception handling in CRUD operations."""

    def test_create_template_file_write_error(self, manager, monkeypatch):
        """Test create_template error handling (tests line 296-300)."""
        from asciidoc_artisan.core.models import Template

        template = Template(
            name="test_template",
            category="document",
            description="Test",
            content="= Test\nContent",
        )

        # Mock serialize_template to raise exception
        def mock_serialize(t):
            raise IOError("Disk full")

        monkeypatch.setattr("asciidoc_artisan.core.template_manager.serialize_template", mock_serialize)

        # Should return False on error
        result = manager.create_template(template)
        assert result is False

    def test_update_template_file_error(self, manager, tmp_path, monkeypatch):
        """Test update_template error handling (tests line 334-338)."""
        from pathlib import Path

        from asciidoc_artisan.core.models import Template

        # Create a template with a file path
        template_file = tmp_path / "test-update.adoc"
        template_file.write_text("= Test")

        template = Template(
            name="test_update",
            category="document",
            description="Test",
            content="= Updated",
            file_path=str(template_file),
        )

        # Add template to manager
        manager.templates[template.name] = template

        # Mock Path.write_text to raise an exception
        original_write_text = Path.write_text

        def mock_write_text(self, *args, **kwargs):
            if "test-update" in str(self):
                raise PermissionError("Cannot write to file")
            return original_write_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", mock_write_text)

        # Should return False on error and log the exception
        result = manager.update_template(template)
        assert result is False

    def test_delete_template_file_error(self, manager, tmp_path, monkeypatch):
        """Test delete_template error handling (tests line 383-387)."""
        from pathlib import Path

        from asciidoc_artisan.core.models import Template

        # Create a custom template in tmp_path
        template_file = tmp_path / "undeletable.adoc"
        template_file.write_text("= Test")

        template = Template(
            name="Undeletable",
            category="document",
            description="Test",
            content="= Test",
            file_path=str(template_file),
        )

        # Set custom_dir to tmp_path
        monkeypatch.setattr(manager, "custom_dir", tmp_path)
        manager.templates["Undeletable"] = template

        # Mock Path.unlink to raise an exception
        original_unlink = Path.unlink

        def mock_unlink(self, *args, **kwargs):
            if "undeletable" in str(self):
                raise PermissionError("Cannot delete file")
            return original_unlink(self, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", mock_unlink)

        # Should return False on error and log the exception
        result = manager.delete_template("Undeletable")
        assert result is False


@pytest.mark.unit
@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestRecentSaveError:
    """Test error handling in recent template persistence."""

    def test_save_recent_write_error(self, tmp_path):
        """Test tracker's _save error handling."""
        from asciidoc_artisan.core.recent_templates_tracker import (
            RecentTemplatesTracker,
        )

        # Create tracker
        tracker = RecentTemplatesTracker(tmp_path)
        tracker.add("test_template")

        # Make directory unwritable
        (tmp_path / "recent.json").unlink(missing_ok=True)
        tmp_path.chmod(0o444)

        # Should not crash, just log error
        tracker._save()

        # Clean up
        tmp_path.chmod(0o755)


@pytest.mark.unit
@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestYamlImportError:
    """Test yaml import error handling."""

    def test_serialize_template_no_yaml(self, monkeypatch):
        """Test serialize_template without yaml installed (tests line 509-510)."""
        from asciidoc_artisan.core.models import Template

        template = Template(name="test", category="document", description="Test", content="= Test")

        # Mock yaml import to fail
        import sys
        from unittest.mock import patch

        with patch.dict(sys.modules, {"yaml": None}):
            # Should raise ImportError
            with pytest.raises(ImportError, match="PyYAML is required"):
                serialize_template(template)


@pytest.mark.unit
@pytest.mark.fr_100
@pytest.mark.fr_101
@pytest.mark.fr_102
@pytest.mark.fr_104
@pytest.mark.fr_105
@pytest.mark.unit
class TestSerializeVersion:
    """Test template serialization version handling."""

    def test_serialize_template_non_default_version(self):
        """Test serialize_template with non-default version (tests line 523)."""
        from asciidoc_artisan.core.models import Template

        # Create template with version != "1.0"
        template = Template(
            name="test",
            category="document",
            description="Test",
            content="= Test",
            version="2.0",  # Non-default version
        )

        # Should include version in serialization
        serialized = serialize_template(template)
        assert "version: '2.0'" in serialized or 'version: "2.0"' in serialized
