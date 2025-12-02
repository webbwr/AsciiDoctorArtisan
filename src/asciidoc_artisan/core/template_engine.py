"""
Template engine for AsciiDoc Artisan (v2.0.0+).

This module provides document template rendering with variable substitution.
Templates use YAML front matter for metadata and Mustache-style syntax for
variable substitution: {{variable}}, {{variable:default}}.

Key features:
- YAML front matter parsing
- Variable substitution with defaults
- Conditional sections ({{#if}}, {{#unless}})
- Include directives ({{include:file}})
- Built-in variables ({{today}}, {{user.name}}, etc.)
- <50ms template instantiation

Template Format:
    ---
    name: Template Name
    category: article
    description: Short description
    variables:
      - name: title
        description: Document title
        required: true
    ---
    = {{title}}
    {{author:Anonymous}}
    {{date:{{today}}}}

    {{#if toc}}
    :toc:
    {{/if}}

    == Introduction
    Content here...

Example:
    ```python
    from asciidoc_artisan.core.template_engine import TemplateEngine
    from asciidoc_artisan.core.models import Template, TemplateVariable

    engine = TemplateEngine()

    template = Template(
        name="Article",
        category="article",
        description="Technical article",
        variables=[
            TemplateVariable(name="title", description="Title", required=True),
            TemplateVariable(name="author", description="Author", default="Anonymous"),
        ],
        content="= {{title}}\\n{{author}}\\n\\nContent here..."
    )

    result = engine.instantiate(template, {"title": "My Article"})
    # Returns: "= My Article\\nAnonymous\\n\\nContent here..."
    ```
"""

import os
import re
from datetime import date
from pathlib import Path
from typing import Any

from asciidoc_artisan.core.models import Template
from asciidoc_artisan.core.template_parser import TemplateParser


class TemplateEngine:
    """
    Template rendering engine with variable substitution.

    Renders templates by:
    1. Resolving built-in variables ({{today}}, {{user.name}})
    2. Processing conditionals ({{#if}}, {{#unless}})
    3. Processing includes ({{include:file}})
    4. Substituting user variables ({{var}}, {{var:default}})

    Attributes:
        built_in_vars: Dictionary of built-in variable values

    Performance:
        - <50ms for template instantiation
        - <20ms for variable substitution
        - <10ms for YAML parsing
    """

    def __init__(self) -> None:
        """
        Initialize template engine with built-in variables.

        MA principle: Delegates parsing to TemplateParser (extracted class).
        """
        self.built_in_vars = self._get_built_in_vars()
        self._parser = TemplateParser(self.built_in_vars)

    def _get_built_in_vars(self) -> dict[str, str]:
        """
        Get built-in variable values.

        Built-in variables:
        - user.name: Current user name (from USER env var)
        - user.email: User email (from EMAIL env var)
        - today: Today's date (YYYY-MM-DD)
        - year: Current year
        - app.name: Application name
        - app.version: Application version

        Returns:
            Dictionary mapping variable names to values
        """
        return {
            "user.name": os.environ.get("USER", "Unknown"),
            "user.email": os.environ.get("EMAIL", ""),
            "today": date.today().strftime("%Y-%m-%d"),
            "year": str(date.today().year),
            "app.name": "AsciiDoc Artisan",
            "app.version": "2.0.0",
        }

    def instantiate(self, template: Template, variables: dict[str, Any]) -> str:
        """
        Render template with variables.

        Args:
            template: Template to render
            variables: User-provided variable values

        Returns:
            Rendered document text

        Raises:
            ValueError: If required variable not provided

        Example:
            ```python
            template = Template(
                name="Article",
                category="article",
                description="Technical article",
                variables=[
                    TemplateVariable(name="title", required=True),
                    TemplateVariable(name="author", default="Anonymous"),
                ],
                content="= {{title}}\\n{{author}}"
            )

            result = engine.instantiate(template, {"title": "My Article"})
            # Returns: "= My Article\\nAnonymous"
            ```
        """
        # Check required variables
        for var_def in template.variables:
            if var_def.required and var_def.name not in variables:
                raise ValueError(f"Required variable '{var_def.name}' not provided")

        # Merge user variables with built-in vars
        all_vars = {**self.built_in_vars, **variables}

        # Apply defaults for missing variables
        for var_def in template.variables:
            if var_def.name not in all_vars and var_def.default:
                # Resolve default value (may contain built-in vars)
                default_value = self._substitute_variables(var_def.default, all_vars, allow_missing=True)
                all_vars[var_def.name] = default_value

        # Render template
        rendered = template.content

        # Step 1: Process conditionals ({{#if}}, {{#unless}})
        rendered = self._process_conditionals(rendered, all_vars)

        # Step 2: Process includes ({{include:file}})
        rendered = self._process_includes(rendered)

        # Step 3: Substitute variables ({{var}}, {{var:default}})
        rendered = self._substitute_variables(rendered, all_vars)

        return rendered

    def _substitute_variables(self, text: str, variables: dict[str, Any], allow_missing: bool = False) -> str:
        """
        Replace {{var}} and {{var:default}} with values.

        Pattern matching:
        - {{varname}} - Simple variable
        - {{varname:default}} - Variable with default value

        Args:
            text: Text to process
            variables: Variable values
            allow_missing: If True, keep {{var}} unchanged if not found

        Returns:
            Text with variables substituted

        Example:
            ```python
            text = "Hello {{name}}, today is {{date:unknown}}"
            vars = {"name": "John"}
            result = _substitute_variables(text, vars)
            # Returns: "Hello John, today is unknown"
            ```
        """
        # Pattern: {{varname}} or {{varname:default}}
        pattern = r"\{\{([^}:]+)(?::([^}]+))?\}\}"

        def replace(match: re.Match[str]) -> str:
            var_name = match.group(1).strip()
            default = match.group(2).strip() if match.group(2) else ""

            # Look up variable
            value = variables.get(var_name)

            if value is not None:
                # Convert boolean to string
                if isinstance(value, bool):
                    return "true" if value else ""
                return str(value)
            elif default:
                # Use default value
                return default
            elif allow_missing:
                # Keep original {{var}} syntax
                return match.group(0)
            else:
                # Empty string for missing vars
                return ""

        return re.sub(pattern, replace, text)

    def _process_conditionals(self, text: str, variables: dict[str, Any]) -> str:
        """
        Process {{#if var}}...{{/if}} and {{#unless var}}...{{/unless}}.

        Conditionals allow sections to be included/excluded based on
        variable values.

        Args:
            text: Text to process
            variables: Variable values

        Returns:
            Text with conditionals resolved

        Example:
            ```python
            text = "{{#if toc}}:toc:\\n{{/if}}Content"
            vars = {"toc": True}
            result = _process_conditionals(text, vars)
            # Returns: ":toc:\\nContent"

            vars = {"toc": False}
            result = _process_conditionals(text, vars)
            # Returns: "Content"
            ```
        """
        # Process {{#if var}}...{{/if}}
        if_pattern = r"\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}"

        def replace_if(match: re.Match[str]) -> str:
            var_name = match.group(1)
            content = match.group(2)
            var_value = variables.get(var_name, False)

            # Include content if var is truthy
            return content if self._is_truthy(var_value) else ""

        text = re.sub(if_pattern, replace_if, text, flags=re.DOTALL)

        # Process {{#unless var}}...{{/unless}}
        unless_pattern = r"\{\{#unless\s+(\w+)\}\}(.*?)\{\{/unless\}\}"

        def replace_unless(match: re.Match[str]) -> str:
            var_name = match.group(1)
            content = match.group(2)
            var_value = variables.get(var_name, False)

            # Include content if var is falsy
            return content if not self._is_truthy(var_value) else ""

        text = re.sub(unless_pattern, replace_unless, text, flags=re.DOTALL)

        return text

    def _process_includes(self, text: str) -> str:
        """
        Process {{include:file}} directives.

        Includes allow template composition by inserting content from
        external files.

        Args:
            text: Text to process

        Returns:
            Text with includes resolved

        Example:
            ```python
            text = "Header\\n{{include:body.adoc}}\\nFooter"
            # If body.adoc contains "Content here"
            # Returns: "Header\\nContent here\\nFooter"
            ```
        """
        pattern = r"\{\{include:([^}]+)\}\}"

        def replace(match: re.Match[str]) -> str:
            file_path = match.group(1).strip()

            try:
                # Try to read file
                path = Path(file_path)
                if path.exists():
                    return path.read_text(encoding="utf-8")
                else:
                    return f"[ERROR: File not found: {file_path}]"
            except Exception as e:
                return f"[ERROR: Cannot read file: {e}]"

        return re.sub(pattern, replace, text)

    def _is_truthy(self, value: Any) -> bool:
        """
        Check if value is truthy.

        Truthiness rules:
        - bool: True/False
        - str: empty string is False, "false"/"0"/"no" is False
        - other: standard Python truthiness

        Args:
            value: Value to check

        Returns:
            True if value is truthy

        Example:
            ```python
            _is_truthy(True)  # True
            _is_truthy("yes")  # True
            _is_truthy("")  # False
            _is_truthy("false")  # False
            _is_truthy(0)  # False
            ```
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() not in ("", "false", "0", "no")
        return bool(value)

    def parse_template(self, file_path: str) -> Template:
        """
        Parse template file with YAML front matter.

        MA principle: Delegated to TemplateParser (class extraction pattern).
        Class size: Reduced TemplateEngine from 538→283 lines (47% reduction).

        See TemplateParser.parse_template() for implementation details.

        Args:
            file_path: Path to template file

        Returns:
            Template object

        Raises:
            ValueError: If invalid template format or missing required fields
        """
        return self._parser.parse_template(file_path)

    def validate_template(self, template: Template) -> list[str]:
        """
        Validate template for common issues.

        MA principle: Delegated to TemplateParser (class extraction pattern).

        See TemplateParser.validate_template() for implementation details.

        Args:
            template: Template to validate

        Returns:
            List of validation warnings (empty if valid)
        """
        return self._parser.validate_template(template)
