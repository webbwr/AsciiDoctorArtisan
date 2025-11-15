"""
Tests for TemplateEngine (v2.0.0).

Tests the template rendering engine with variable substitution,
conditionals, includes, and YAML front matter parsing.
"""

import os
from unittest.mock import patch

import pytest

from asciidoc_artisan.core.models import Template, TemplateVariable
from asciidoc_artisan.core.template_engine import TemplateEngine



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestInitialization:
    """Test TemplateEngine initialization."""

    def test_engine_initialization(self):
        """Test engine initializes with built-in variables."""
        engine = TemplateEngine()

        assert engine is not None
        assert isinstance(engine.built_in_vars, dict)
        assert "today" in engine.built_in_vars
        assert "year" in engine.built_in_vars



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestBuiltInVariables:
    """Test built-in variable generation."""

    def test_get_built_in_vars_has_today(self):
        """Test built-in vars include today's date."""
        engine = TemplateEngine()

        assert "today" in engine.built_in_vars
        # Should be in YYYY-MM-DD format
        assert len(engine.built_in_vars["today"]) == 10
        assert engine.built_in_vars["today"].count("-") == 2

    def test_get_built_in_vars_has_year(self):
        """Test built-in vars include current year."""
        engine = TemplateEngine()

        assert "year" in engine.built_in_vars
        year = int(engine.built_in_vars["year"])
        assert 2020 <= year <= 2030  # Reasonable year range

    @patch.dict(os.environ, {"USER": "testuser"})
    def test_get_built_in_vars_user_name_from_env(self):
        """Test user.name comes from USER env var."""
        engine = TemplateEngine()

        assert "user.name" in engine.built_in_vars
        assert engine.built_in_vars["user.name"] == "testuser"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_built_in_vars_user_name_default(self):
        """Test user.name defaults when not in env."""
        engine = TemplateEngine()

        assert "user.name" in engine.built_in_vars
        # Implementation uses "Unknown" as default
        assert engine.built_in_vars["user.name"] in ["User", "Unknown"]

    @patch.dict(os.environ, {"EMAIL": "test@example.com"})
    def test_get_built_in_vars_user_email_from_env(self):
        """Test user.email comes from EMAIL env var."""
        engine = TemplateEngine()

        assert "user.email" in engine.built_in_vars
        assert engine.built_in_vars["user.email"] == "test@example.com"



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestVariableSubstitution:
    """Test variable substitution in templates."""

    def test_substitute_simple_variable(self):
        """Test simple variable substitution."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test template",
            variables=[TemplateVariable(name="title", description="Title")],
            content="= {{title}}",
        )

        result = engine.instantiate(template, {"title": "My Document"})

        assert result == "= My Document"

    def test_substitute_multiple_variables(self):
        """Test multiple variable substitutions."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="= {{title}}\n{{author}}\n\n{{content}}",
        )

        result = engine.instantiate(
            template, {"title": "Title", "author": "Author", "content": "Body"}
        )

        assert "Title" in result
        assert "Author" in result
        assert "Body" in result

    def test_substitute_variable_with_default(self):
        """Test variable substitution with default value."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="= {{title:Default Title}}",
        )

        # Without providing title
        result = engine.instantiate(template, {})

        assert "Default Title" in result

    def test_substitute_variable_overrides_default(self):
        """Test provided variable overrides default."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="= {{title:Default}}",
        )

        result = engine.instantiate(template, {"title": "Custom"})

        assert "Custom" in result
        assert "Default" not in result

    def test_substitute_built_in_variable(self):
        """Test built-in variable substitution."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="Date: {{today}}",
        )

        result = engine.instantiate(template, {})

        # Should contain a date in YYYY-MM-DD format
        assert "Date: " in result
        assert len(result.split("Date: ")[1].strip()) == 10



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestConditionals:
    """Test conditional processing."""

    def test_if_condition_true(self):
        """Test {{#if}} with true condition."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#if toc}}:toc:{{/if}}",
        )

        result = engine.instantiate(template, {"toc": True})

        assert ":toc:" in result

    def test_if_condition_false(self):
        """Test {{#if}} with false condition."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#if toc}}:toc:{{/if}}",
        )

        result = engine.instantiate(template, {"toc": False})

        assert ":toc:" not in result

    def test_unless_condition_true(self):
        """Test {{#unless}} with true condition."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#unless draft}}Published{{/unless}}",
        )

        result = engine.instantiate(template, {"draft": True})

        assert "Published" not in result

    def test_unless_condition_false(self):
        """Test {{#unless}} with false condition."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#unless draft}}Published{{/unless}}",
        )

        result = engine.instantiate(template, {"draft": False})

        assert "Published" in result

    def test_nested_conditionals(self):
        """Test nested conditional blocks."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#if outer}}Outer{{#if inner}}Inner{{/if}}{{/if}}",
        )

        result = engine.instantiate(template, {"outer": True, "inner": True})

        assert "Outer" in result
        assert "Inner" in result



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestTruthyEvaluation:
    """Test truthiness evaluation for conditionals."""

    def test_is_truthy_with_true(self):
        """Test is_truthy with boolean True."""
        engine = TemplateEngine()

        assert engine._is_truthy(True) is True

    def test_is_truthy_with_false(self):
        """Test is_truthy with boolean False."""
        engine = TemplateEngine()

        assert engine._is_truthy(False) is False

    def test_is_truthy_with_non_empty_string(self):
        """Test is_truthy with non-empty string."""
        engine = TemplateEngine()

        assert engine._is_truthy("yes") is True
        assert engine._is_truthy("true") is True

    def test_is_truthy_with_empty_string(self):
        """Test is_truthy with empty string."""
        engine = TemplateEngine()

        assert engine._is_truthy("") is False

    def test_is_truthy_with_number(self):
        """Test is_truthy with numbers."""
        engine = TemplateEngine()

        assert engine._is_truthy(1) is True
        assert engine._is_truthy(0) is False
        assert engine._is_truthy(42) is True

    def test_is_truthy_with_none(self):
        """Test is_truthy with None."""
        engine = TemplateEngine()

        assert engine._is_truthy(None) is False

    def test_is_truthy_with_list(self):
        """Test is_truthy with lists."""
        engine = TemplateEngine()

        assert engine._is_truthy([1, 2, 3]) is True
        assert engine._is_truthy([]) is False



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestTemplateValidation:
    """Test template validation."""

    def test_validate_valid_template(self):
        """Test validating a valid template."""
        engine = TemplateEngine()
        template = Template(
            name="Valid",
            category="article",
            description="Valid template",
            variables=[
                TemplateVariable(name="title", description="Title", required=True)
            ],
            content="= {{title}}",
        )

        errors = engine.validate_template(template)

        assert len(errors) == 0

    def test_validate_template_missing_name(self):
        """Test Pydantic prevents empty name at model level."""
        engine = TemplateEngine()

        # Pydantic validation should prevent empty name
        with pytest.raises(Exception):  # ValidationError
            template = Template(
                name="",
                category="article",
                description="Test",
                variables=[],
                content="Content",
            )

    def test_validate_template_with_variables(self):
        """Test validation accepts template with variables."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="article",
            description="Test with variables",
            variables=[
                TemplateVariable(name="var1", description="Variable 1"),
                TemplateVariable(
                    name="var2", description="Variable 2", default="default"
                ),
            ],
            content="{{var1}} {{var2}}",
        )

        errors = engine.validate_template(template)

        # Should have no errors for valid template
        assert len(errors) == 0



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestInstantiation:
    """Test complete template instantiation."""

    def test_instantiate_complete_template(self):
        """Test instantiating a complete template."""
        engine = TemplateEngine()
        template = Template(
            name="Article",
            category="article",
            description="Technical article",
            variables=[
                TemplateVariable(name="title", description="Title", required=True),
                TemplateVariable(
                    name="author", description="Author", default="Anonymous"
                ),
            ],
            content="= {{title}}\n{{author}}\n{{today}}\n\n{{#if toc}}:toc:{{/if}}\n\n== Introduction",
        )

        result = engine.instantiate(template, {"title": "My Article", "toc": True})

        assert "= My Article" in result
        assert "Anonymous" in result  # Default author
        assert ":toc:" in result  # Conditional included
        assert "== Introduction" in result

    def test_instantiate_with_all_variables_provided(self):
        """Test instantiation with all variables provided."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="= {{title}}\n{{author}}\n{{date}}",
        )

        result = engine.instantiate(
            template, {"title": "Title", "author": "Author", "date": "2025-01-01"}
        )

        assert "Title" in result
        assert "Author" in result
        assert "2025-01-01" in result



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_instantiate_with_missing_required_variable(self):
        """Test instantiation raises error for missing required variable."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[
                TemplateVariable(name="title", description="Title", required=True)
            ],
            content="= {{title}}",
        )

        # Should raise ValueError for missing required variable
        with pytest.raises(ValueError, match="Required variable"):
            engine.instantiate(template, {})

    def test_instantiate_with_empty_content(self):
        """Test instantiation with empty template content."""
        engine = TemplateEngine()
        template = Template(
            name="Empty",
            category="test",
            description="Empty template",
            variables=[],
            content="",
        )

        result = engine.instantiate(template, {})

        assert result == ""

    def test_substitute_variables_with_special_characters(self):
        """Test variable substitution with special characters."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="= {{title}}",
        )

        result = engine.instantiate(template, {"title": "Title with $pecial & <chars>"})

        assert "Title with $pecial & <chars>" in result

    def test_conditional_with_undefined_variable(self):
        """Test conditional with undefined variable."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#if undefined}}Content{{/if}}",
        )

        result = engine.instantiate(template, {})

        # Undefined variable should be falsy
        assert "Content" not in result



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestTemplateEngineErrorHandling:
    """Test suite for template engine error handling."""

    def test_substitute_variables_with_boolean_true(self):
        """Test boolean variable substitution returns 'true'."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="Value: {{flag}}",
        )

        result = engine.instantiate(template, {"flag": True})

        assert "Value: true" in result

    def test_substitute_variables_with_boolean_false(self):
        """Test boolean variable substitution returns empty string."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="Value: {{flag}}",
        )

        result = engine.instantiate(template, {"flag": False})

        assert "Value: " in result
        assert "false" not in result

    def test_substitute_variables_keep_original_syntax(self):
        """Test allow_missing keeps original {{var}} syntax."""
        engine = TemplateEngine()

        # With allow_missing=True in _substitute_variables
        result = engine._substitute_variables(
            "Keep: {{undefined_var}}", {}, allow_missing=True
        )

        assert "{{undefined_var}}" in result

    def test_include_file_not_found(self, tmp_path):
        """Test file inclusion with non-existent file."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{include:nonexistent.txt}}",
        )

        result = engine.instantiate(template, {})

        assert "[ERROR: File not found:" in result

    def test_include_file_read_error(self, tmp_path):
        """Test file inclusion with read error."""
        engine = TemplateEngine()

        # Create a directory instead of file to trigger read error
        bad_file = tmp_path / "bad_file"
        bad_file.mkdir()

        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content=f"{{{{include:{bad_file}}}}}",
        )

        result = engine.instantiate(template, {})

        assert "[ERROR: Cannot read file:" in result



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestTemplateEngineParseErrors:
    """Test suite for parse_template error handling."""

    def test_parse_template_missing_yaml(self, tmp_path, monkeypatch):
        """Test parsing when yaml module is not available."""
        from asciidoc_artisan.core.template_engine import TemplateEngine

        engine = TemplateEngine()

        # Create valid template file
        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
name: Test
category: test
description: Test template
---
Content"""
        )

        # Mock yaml import to fail
        import builtins
        import sys

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Remove yaml from sys.modules if present
        if "yaml" in sys.modules:
            monkeypatch.delitem(sys.modules, "yaml")

        with pytest.raises(ImportError, match="PyYAML is required"):
            engine.parse_template(str(template_file))

    def test_parse_template_not_found(self):
        """Test parsing non-existent file."""
        engine = TemplateEngine()

        with pytest.raises(ValueError, match="Template file not found"):
            engine.parse_template("/nonexistent/file.adoc")

    def test_parse_template_read_exception(self, tmp_path, monkeypatch):
        """Test parsing with read exception."""
        engine = TemplateEngine()

        # Create file
        template_file = tmp_path / "template.adoc"
        template_file.write_text("content")

        # Mock open to raise exception
        def mock_open(*args, **kwargs):
            raise PermissionError("Cannot read file")

        monkeypatch.setattr("builtins.open", mock_open)

        with pytest.raises(ValueError, match="Cannot read template file"):
            engine.parse_template(str(template_file))

    def test_parse_template_missing_front_matter(self, tmp_path):
        """Test parsing file without YAML front matter."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text("Just content, no front matter")

        with pytest.raises(ValueError, match="must start with YAML front matter"):
            engine.parse_template(str(template_file))

    def test_parse_template_missing_closing_front_matter(self, tmp_path):
        """Test parsing file with incomplete YAML front matter."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        # Only one --- means it will split into 2 parts instead of 3
        template_file.write_text(
            """---
name: Test"""
        )

        with pytest.raises(ValueError, match="missing closing ---"):
            engine.parse_template(str(template_file))

    def test_parse_template_invalid_yaml(self, tmp_path):
        """Test parsing file with invalid YAML."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
name: Test
category: [unclosed list
description: Test
---
Content"""
        )

        with pytest.raises(ValueError, match="Invalid YAML"):
            engine.parse_template(str(template_file))

    def test_parse_template_yaml_not_dict(self, tmp_path):
        """Test parsing file where YAML is not a dictionary."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
- item1
- item2
---
Content"""
        )

        with pytest.raises(ValueError, match="must be a dictionary"):
            engine.parse_template(str(template_file))

    def test_parse_template_missing_name_field(self, tmp_path):
        """Test parsing file without name field."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
category: test
description: Test template
---
Content"""
        )

        with pytest.raises(
            ValueError, match="must have name, category, and description"
        ):
            engine.parse_template(str(template_file))

    def test_parse_template_non_string_fields(self, tmp_path):
        """Test parsing file with non-string required fields."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
name: 123
category: test
description: Test template
---
Content"""
        )

        with pytest.raises(
            ValueError, match="must have name, category, and description as strings"
        ):
            engine.parse_template(str(template_file))

    def test_parse_template_empty_required_fields(self, tmp_path):
        """Test parsing file with empty required fields."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
name: ""
category: test
description: Test template
---
Content"""
        )

        with pytest.raises(
            ValueError, match="must have name, category, and description"
        ):
            engine.parse_template(str(template_file))

    def test_parse_template_invalid_variable_definition(self, tmp_path):
        """Test parsing file with invalid variable definition."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
name: Test
category: test
description: Test template
variables:
  - "not a dict"
---
Content"""
        )

        with pytest.raises(ValueError, match="Invalid variable definition"):
            engine.parse_template(str(template_file))

    def test_parse_template_variable_without_name(self, tmp_path):
        """Test parsing file with variable missing name."""
        engine = TemplateEngine()

        template_file = tmp_path / "template.adoc"
        template_file.write_text(
            """---
name: Test
category: test
description: Test template
variables:
  - description: "Variable without name"
---
Content"""
        )

        with pytest.raises(ValueError, match="Variable must have a name"):
            engine.parse_template(str(template_file))



@pytest.mark.fr_101
@pytest.mark.fr_107
@pytest.mark.unit
class TestTemplateEngineValidation:
    """Test suite for template validation warnings."""

    def test_validate_template_undefined_variable(self):
        """Test validation warns about undefined variables."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{undefined_var}}",
        )

        warnings = engine.validate_template(template)

        assert len(warnings) == 1
        assert "undefined_var" in warnings[0]
        assert "not defined" in warnings[0]

    def test_validate_template_mismatched_if_tags(self):
        """Test validation warns about mismatched #if tags."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#if condition}}Content",  # Missing {{/if}}
        )

        warnings = engine.validate_template(template)

        assert any("Mismatched {{#if}}" in w for w in warnings)

    def test_validate_template_mismatched_unless_tags(self):
        """Test validation warns about mismatched #unless tags."""
        engine = TemplateEngine()
        template = Template(
            name="Test",
            category="test",
            description="Test",
            variables=[],
            content="{{#unless condition}}Content",  # Missing {{/unless}}
        )

        warnings = engine.validate_template(template)

        assert any("Mismatched {{#unless}}" in w for w in warnings)
