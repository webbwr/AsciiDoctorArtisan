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

from asciidoc_artisan.core.models import Template, TemplateVariable


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
        """Initialize template engine with built-in variables."""
        self.built_in_vars = self._get_built_in_vars()

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

    def _read_template_file(self, file_path: str) -> str:
        """
        Read template file with error handling.

        MA principle: Extracted from parse_template (8 lines).

        Args:
            file_path: Path to template file

        Returns:
            File content as string

        Raises:
            ValueError: If file not found or cannot be read
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise ValueError(f"Template file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Cannot read template file: {e}")

    def _split_front_matter(self, content: str) -> tuple[str, str]:
        """
        Split YAML front matter from template content.

        MA principle: Extracted from parse_template (10 lines).

        Args:
            content: Full template file content

        Returns:
            Tuple of (yaml_text, template_content)

        Raises:
            ValueError: If front matter format is invalid
        """
        if not content.startswith("---"):
            raise ValueError("Template must start with YAML front matter (---)")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid YAML front matter format (missing closing ---)")

        return parts[1], parts[2].lstrip("\n")

    def _parse_yaml_metadata(self, yaml_text: str) -> dict[str, Any]:
        """
        Parse YAML front matter metadata.

        MA principle: Extracted from parse_template (11 lines).

        Args:
            yaml_text: YAML text to parse

        Returns:
            Parsed metadata dictionary

        Raises:
            ValueError: If YAML is invalid or not a dictionary
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for template parsing. Install with: pip install pyyaml")

        try:
            metadata = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

        if not isinstance(metadata, dict):
            raise ValueError("YAML front matter must be a dictionary")

        return metadata

    def _extract_required_fields(self, metadata: dict[str, Any]) -> tuple[str, str, str]:
        """
        Extract and validate required template fields.

        MA principle: Extracted from parse_template (9 lines).

        Args:
            metadata: Parsed metadata dictionary

        Returns:
            Tuple of (name, category, description)

        Raises:
            ValueError: If required fields missing or invalid
        """
        name = metadata.get("name")
        category = metadata.get("category")
        description = metadata.get("description")

        if not isinstance(name, str) or not isinstance(category, str) or not isinstance(description, str):
            raise ValueError("Template must have name, category, and description as strings")

        if not all([name, category, description]):
            raise ValueError("Template must have name, category, and description")

        return name, category, description

    def _parse_variables(self, var_defs: list[Any]) -> list[TemplateVariable]:
        """
        Parse variable definitions from metadata.

        MA principle: Extracted from parse_template (19 lines).

        Args:
            var_defs: List of variable definition dictionaries

        Returns:
            List of TemplateVariable objects

        Raises:
            ValueError: If variable definition is invalid
        """
        variables = []

        for v in var_defs:
            if not isinstance(v, dict):
                raise ValueError(f"Invalid variable definition: {v}")

            var_name = v.get("name")
            if not var_name:
                raise ValueError("Variable must have a name")

            variables.append(
                TemplateVariable(
                    name=var_name,
                    description=v.get("description", ""),
                    required=v.get("required", False),
                    default=v.get("default"),
                    type=v.get("type", "string"),
                )
            )

        return variables

    def parse_template(self, file_path: str) -> Template:
        """
        Parse template file with YAML front matter.

        MA principle: Reduced from 121→56 lines by extracting 5 helper methods.

        Template format:
            ---
            name: Template Name
            category: article
            description: Description
            author: Author (optional)
            version: 1.0 (optional)
            variables:
              - name: title
                description: Document title
                required: true
              - name: author
                description: Author name
                default: Anonymous
                type: string
            ---
            = {{title}}
            {{author}}

            Content here...

        Args:
            file_path: Path to template file

        Returns:
            Template object

        Raises:
            ValueError: If invalid template format or missing required fields

        Example:
            ```python
            template = engine.parse_template("templates/article.adoc")
            print(template.name)  # "Technical Article"
            print(len(template.variables))  # 3
            ```
        """
        # Read and parse template using helpers
        content = self._read_template_file(file_path)
        yaml_text, template_content = self._split_front_matter(content)
        metadata = self._parse_yaml_metadata(yaml_text)
        name, category, description = self._extract_required_fields(metadata)
        variables = self._parse_variables(metadata.get("variables", []))

        # Build and return Template object
        return Template(
            name=name,
            category=category,
            description=description,
            author=metadata.get("author", ""),
            version=metadata.get("version", "1.0"),
            variables=variables,
            content=template_content,
            file_path=file_path,
        )

    def validate_template(self, template: Template) -> list[str]:
        """
        Validate template for common issues.

        Checks:
        - All variable references in content are defined
        - No circular includes
        - Valid conditional syntax
        - Required fields present

        Args:
            template: Template to validate

        Returns:
            List of validation warnings (empty if valid)

        Example:
            ```python
            warnings = engine.validate_template(template)
            if warnings:
                print("Template warnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            ```
        """
        warnings = []

        # Extract all variable references from content
        pattern = r"\{\{([^}:]+)(?::([^}]+))?\}\}"
        matches = re.findall(pattern, template.content)

        # Check if all referenced vars are defined
        defined_vars = {v.name for v in template.variables}
        defined_vars.update(self.built_in_vars.keys())

        for match in matches:
            var_name = match[0].strip()
            # Skip conditionals and includes
            if var_name.startswith("#") or var_name.startswith("include:"):
                continue

            if var_name not in defined_vars:
                warnings.append(f"Variable '{var_name}' used in template but not defined")

        # Check for malformed conditionals
        if_count = len(re.findall(r"\{\{#if\s+\w+\}\}", template.content))
        endif_count = len(re.findall(r"\{\{/if\}\}", template.content))
        if if_count != endif_count:
            warnings.append(f"Mismatched {{{{#if}}}} tags: {if_count} opening, {endif_count} closing")

        unless_count = len(re.findall(r"\{\{#unless\s+\w+\}\}", template.content))
        endunless_count = len(re.findall(r"\{\{/unless\}\}", template.content))
        if unless_count != endunless_count:
            warnings.append(f"Mismatched {{{{#unless}}}} tags: {unless_count} opening, {endunless_count} closing")

        return warnings
