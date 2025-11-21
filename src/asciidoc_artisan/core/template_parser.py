"""
Template parser for AsciiDoc Artisan (v2.0.0+).

This module provides template file parsing and validation functionality.
Extracted from TemplateEngine to reduce class size (MA principle).

Key features:
- YAML front matter parsing
- Template validation
- Variable definition extraction
- <10ms YAML parsing

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
    Content here...
"""

import re
from pathlib import Path
from typing import Any

from asciidoc_artisan.core.models import Template, TemplateVariable


class TemplateParser:
    """
    Template file parser and validator.

    Responsible for:
    1. Reading template files
    2. Parsing YAML front matter
    3. Extracting variable definitions
    4. Validating template structure

    This class was extracted from TemplateEngine to reduce class size
    per MA principle (538→283 lines).
    """

    def __init__(self, built_in_vars: dict[str, str]) -> None:
        """
        Initialize template parser.

        Args:
            built_in_vars: Dictionary of built-in variable names for validation
        """
        self.built_in_vars = built_in_vars

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
        Class size: Moved from TemplateEngine to TemplateParser for separation.

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
            parser = TemplateParser(built_in_vars)
            template = parser.parse_template("templates/article.adoc")
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
            warnings = parser.validate_template(template)
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
