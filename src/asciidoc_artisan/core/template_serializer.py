"""
Template Serializer - Serialize and deserialize templates to/from files.

MA principle: Extracted from template_manager.py for focused responsibility.

This module provides:
- Template serialization to YAML front matter format
- Filename sanitization for safe file storage
"""

from typing import Any

from asciidoc_artisan.core.models import Template


def sanitize_template_filename(name: str) -> str:
    """
    Sanitize template name for use as filename.

    Args:
        name: Template name

    Returns:
        Safe filename (lowercase, hyphens, no spaces)

    Example:
        ```python
        filename = sanitize_template_filename("Technical Article")
        # Returns: "technical-article"
        ```
    """
    # Convert to lowercase, replace spaces with hyphens
    safe_name = name.lower().replace(" ", "-")

    # Remove non-alphanumeric characters (except hyphens)
    safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")

    return safe_name


def serialize_template(template: Template) -> str:
    """
    Serialize template to file format.

    Args:
        template: Template to serialize

    Returns:
        Template content with YAML front matter

    Format:
        ---
        name: Template Name
        category: article
        description: Description
        variables:
          - name: title
            description: Title
            required: true
        ---
        = {{title}}
        Content...
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for template serialization")

    # Build YAML front matter
    metadata: dict[str, Any] = {
        "name": template.name,
        "category": template.category,
        "description": template.description,
    }

    if template.author:
        metadata["author"] = template.author

    if template.version != "1.0":
        metadata["version"] = template.version

    if template.variables:
        metadata["variables"] = [
            {
                "name": v.name,
                "description": v.description,
                "required": v.required,
                "default": v.default,
                "type": v.type,
            }
            for v in template.variables
        ]

    # Serialize to YAML
    yaml_text = yaml.dump(metadata, default_flow_style=False, sort_keys=False)

    # Combine with content
    return f"---\n{yaml_text}---\n{template.content}"
