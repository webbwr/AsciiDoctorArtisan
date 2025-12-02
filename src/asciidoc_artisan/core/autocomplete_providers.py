"""
Auto-complete providers for AsciiDoc Artisan (v2.0.0+).

This module provides completion item providers for different context types:
- SyntaxProvider: AsciiDoc syntax elements (headings, lists, blocks)
- AttributeProvider: Document attributes and attribute references
- CrossRefProvider: Cross-references to anchors
- IncludeProvider: Include file paths
- SnippetProvider: Expandable code snippets

Each provider returns a list of CompletionItem objects for the engine to rank.

MA principle: Reduced from 670→320 lines by extracting completion_data.py.

Example:
    ```python
    from asciidoc_artisan.core.autocomplete_providers import SyntaxProvider
    from asciidoc_artisan.core.models import CompletionContext

    provider = SyntaxProvider()
    context = CompletionContext(
        line="== ",
        line_number=5,
        column=3,
        prefix="== ",
        trigger_char="=",
        manual=False
    )

    items = provider.get_completions(context)
    # Returns: [CompletionItem(text="== Heading", kind=SYNTAX, ...)]
    ```
"""

from pathlib import Path

from asciidoc_artisan.core.completion_data import (
    get_cached_snippet_completions,
    get_cached_syntax_completions,
)
from asciidoc_artisan.core.models import (
    CompletionContext,
    CompletionItem,
    CompletionKind,
)


class SyntaxProvider:
    """
    Provides AsciiDoc syntax completions.

    Suggests syntax elements like headings, lists, blocks, inline formatting,
    and AsciiDoc directives based on the current context.

    Uses module-level caching for performance (~50-100ms faster on repeated instantiation).

    Examples:
    - "=" → "= Heading" (level 1)
    - "==" → "== Heading" (level 2)
    - "[" → "[source,python]", "[example]", etc.
    - "*" → "* List item"
    - "link:" → "link:URL[text]"
    """

    def __init__(self) -> None:
        """Initialize syntax provider with cached completion items."""
        self.completions = get_cached_syntax_completions()

    def get_completions(self, context: CompletionContext) -> list[CompletionItem]:
        """
        Return syntax completions for given context.

        Args:
            context: Current editor context

        Returns:
            List of syntax completion items

        Context-aware filtering:
        - Heading context: Show only heading completions
        - Block context (starts with "["): Show block completions
        - List context: Show list completions
        - Default: Show all syntax items
        """
        line = context.line.strip()

        # Special handling for headings
        if line.startswith("=") and not line.startswith("=="):
            return self._get_heading_completions(context)

        # Special handling for blocks (starts with "[")
        if context.prefix.strip().endswith("["):
            return self._get_block_completions()

        # Special handling for lists
        if line.startswith(("*", "-", ".")):
            return self._get_list_completions()

        # Default: return all syntax items
        return self.completions

    def _get_heading_completions(self, context: CompletionContext) -> list[CompletionItem]:
        """Get heading-specific completions based on level."""
        level = len(context.line) - len(context.line.lstrip("="))
        heading_items = [item for item in self.completions if item.text.startswith("=" * level + " ")]
        return heading_items if heading_items else self.completions

    def _get_block_completions(self) -> list[CompletionItem]:
        """Get block-specific completions."""
        return [item for item in self.completions if item.text.startswith("[")]

    def _get_list_completions(self) -> list[CompletionItem]:
        """Get list-specific completions."""
        return [
            item for item in self.completions if item.text.startswith(("*", "-", ".")) and "list" in item.detail.lower()
        ]


class AttributeProvider:
    """
    Provides document attribute completions.

    Suggests:
    - Built-in attributes (:author:, :version:, :toc:)
    - Custom attributes from document
    - Attribute references ({author}, {version})
    """

    def __init__(self, document: str = "") -> None:
        """
        Initialize attribute provider.

        Args:
            document: Full document text for extracting custom attributes
        """
        self.document = document
        self.built_in_attributes = self._get_built_in_attributes()

    def get_completions(self, context: CompletionContext) -> list[CompletionItem]:
        """
        Return attribute completions.

        Args:
            context: Current editor context

        Returns:
            List of attribute completion items
        """
        # Check if we're in attribute reference context ({attr})
        if context.prefix.endswith("{"):
            return self._get_attribute_references()

        # Check if we're in attribute definition context (:attr:)
        if context.line.strip().startswith(":"):
            return self.built_in_attributes

        return []

    def _get_built_in_attributes(self) -> list[CompletionItem]:
        """Get built-in AsciiDoc attributes."""
        return [
            CompletionItem(
                text=":author:",
                kind=CompletionKind.ATTRIBUTE,
                detail="Document author",
                documentation=":author: John Doe",
                insert_text=":author: ",
            ),
            CompletionItem(
                text=":version:",
                kind=CompletionKind.ATTRIBUTE,
                detail="Document version",
                documentation=":version: 1.0",
                insert_text=":version: ",
            ),
            CompletionItem(
                text=":toc:",
                kind=CompletionKind.ATTRIBUTE,
                detail="Table of contents",
                documentation=":toc:\n:toc-title: Contents",
                insert_text=":toc:",
            ),
            CompletionItem(
                text=":icons:",
                kind=CompletionKind.ATTRIBUTE,
                detail="Icon mode",
                documentation=":icons: font",
                insert_text=":icons: ",
            ),
            CompletionItem(
                text=":doctype:",
                kind=CompletionKind.ATTRIBUTE,
                detail="Document type",
                documentation=":doctype: article\n(article, book, manpage)",
                insert_text=":doctype: ",
            ),
        ]

    def _get_attribute_references(self) -> list[CompletionItem]:
        """Get attribute references for {attr} syntax."""
        # Extract defined attributes from document
        import re

        pattern = r"^:([^:]+):"
        matches = re.findall(pattern, self.document, re.MULTILINE)

        items = []
        for attr_name in matches:
            items.append(
                CompletionItem(
                    text=f"{{{attr_name}}}",
                    kind=CompletionKind.ATTRIBUTE,
                    detail=f"Reference to :{attr_name}:",
                    documentation=f"Insert value of {attr_name} attribute",
                    insert_text=f"{attr_name}}}",
                )
            )

        return items


class CrossRefProvider:
    """
    Provides cross-reference completions.

    Suggests anchor IDs for <<anchor>> syntax with fuzzy matching.
    """

    def __init__(self, document: str = "") -> None:
        """
        Initialize cross-reference provider.

        Args:
            document: Full document text for extracting anchors
        """
        self.document = document
        self.anchors = self._extract_anchors()

    def get_completions(self, context: CompletionContext) -> list[CompletionItem]:
        """
        Return cross-reference completions.

        Args:
            context: Current editor context

        Returns:
            List of cross-reference completion items
        """
        # Check if we're in xref context (<<)
        if context.prefix.endswith("<<"):
            return self._get_anchor_completions()

        return []

    def _extract_anchors(self) -> list[str]:
        """Extract all anchor IDs from document."""
        import re

        # Match [[id]] and [#id] patterns
        pattern = r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"
        matches = re.findall(pattern, self.document)
        # Flatten tuples (each match has 2 groups)
        return [m[0] or m[1] for m in matches]

    def _get_anchor_completions(self) -> list[CompletionItem]:
        """Get anchor completions for <<>> syntax."""
        items = []
        for anchor in self.anchors:
            items.append(
                CompletionItem(
                    text=f"<<{anchor}>>",
                    kind=CompletionKind.XREF,
                    detail=f"Cross-reference to {anchor}",
                    documentation=f"Link to anchor [[{anchor}]]",
                    insert_text=f"{anchor}>>",
                )
            )
        return items


class IncludeProvider:
    """
    Provides include path completions.

    Suggests .adoc files in the current directory and subdirectories.
    """

    def __init__(self, current_file_path: str = "") -> None:
        """
        Initialize include provider.

        Args:
            current_file_path: Path to current document (for relative paths)
        """
        self.current_file_path = Path(current_file_path) if current_file_path else Path.cwd()
        self.base_dir = self.current_file_path.parent if self.current_file_path.is_file() else self.current_file_path

    def get_completions(self, context: CompletionContext) -> list[CompletionItem]:
        """
        Return include path completions.

        Args:
            context: Current editor context

        Returns:
            List of include path completion items
        """
        # Check if we're in include context
        if "include::" in context.prefix:
            return self._get_file_completions()

        return []

    def _get_file_completions(self) -> list[CompletionItem]:
        """Get .adoc file completions."""
        items = []

        try:
            # Find all .adoc files in base directory and subdirectories
            for adoc_file in self.base_dir.rglob("*.adoc"):
                # Get relative path from base directory
                rel_path = adoc_file.relative_to(self.base_dir)

                items.append(
                    CompletionItem(
                        text=f"include::{rel_path}[]",
                        kind=CompletionKind.INCLUDE,
                        detail=f"Include {rel_path}",
                        documentation=f"Insert contents of {rel_path}",
                        insert_text=f"{rel_path}[]",
                    )
                )
        except Exception:
            # If path operations fail, return empty list
            pass

        return items


class SnippetProvider:
    """
    Provides code snippet completions.

    Suggests expandable snippets for common patterns like tables,
    figures, code blocks with common languages.

    Uses module-level caching for performance (~50-100ms faster on repeated instantiation).
    """

    def __init__(self) -> None:
        """Initialize snippet provider with cached snippets."""
        self.snippets = get_cached_snippet_completions()

    def get_completions(self, context: CompletionContext) -> list[CompletionItem]:
        """
        Return snippet completions.

        Args:
            context: Current editor context

        Returns:
            List of snippet completion items
        """
        # Snippets are always available (manual trigger or specific keywords)
        return self.snippets
