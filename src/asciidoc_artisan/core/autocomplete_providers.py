"""
Auto-complete providers for AsciiDoc Artisan (v2.0.0+).

This module provides completion item providers for different context types:
- SyntaxProvider: AsciiDoc syntax elements (headings, lists, blocks)
- AttributeProvider: Document attributes and attribute references
- CrossRefProvider: Cross-references to anchors
- IncludeProvider: Include file paths
- SnippetProvider: Expandable code snippets

Each provider returns a list of CompletionItem objects for the engine to rank.

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
from typing import List

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

    Examples:
    - "=" → "= Heading" (level 1)
    - "==" → "== Heading" (level 2)
    - "[" → "[source,python]", "[example]", etc.
    - "*" → "* List item"
    - "link:" → "link:URL[text]"
    """

    def __init__(self) -> None:
        """Initialize syntax provider with completion items."""
        self.completions = self._build_completion_items()

    def get_completions(self, context: CompletionContext) -> List[CompletionItem]:
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

    def _build_completion_items(self) -> List[CompletionItem]:
        """
        Build static list of syntax completions.

        Returns:
            List of all syntax completion items
        """
        return [
            # Headings (Level 1-5)
            CompletionItem(
                text="= Document Title",
                kind=CompletionKind.SYNTAX,
                detail="Level 1 heading (document title)",
                documentation="# Document Title\n\nTop-level heading, typically used once per document.",
                insert_text="= ",
                sort_text="h1",
            ),
            CompletionItem(
                text="== Section",
                kind=CompletionKind.SYNTAX,
                detail="Level 2 heading (major section)",
                documentation="## Major Section\n\nMain document sections.",
                insert_text="== ",
                sort_text="h2",
            ),
            CompletionItem(
                text="=== Subsection",
                kind=CompletionKind.SYNTAX,
                detail="Level 3 heading (subsection)",
                documentation="### Subsection\n\nSubsections within major sections.",
                insert_text="=== ",
                sort_text="h3",
            ),
            CompletionItem(
                text="==== Sub-subsection",
                kind=CompletionKind.SYNTAX,
                detail="Level 4 heading (sub-subsection)",
                documentation="#### Sub-subsection\n\nDetailed subsections.",
                insert_text="==== ",
                sort_text="h4",
            ),
            CompletionItem(
                text="===== Paragraph",
                kind=CompletionKind.SYNTAX,
                detail="Level 5 heading (paragraph title)",
                documentation="##### Paragraph Title\n\nSmallest heading level.",
                insert_text="===== ",
                sort_text="h5",
            ),
            # Lists
            CompletionItem(
                text="* Unordered list item",
                kind=CompletionKind.SYNTAX,
                detail="Unordered list item (bullet)",
                documentation="* Item\n* Another item\n* Yet another",
                insert_text="* ",
                sort_text="list1",
            ),
            CompletionItem(
                text="- Unordered list item (dash)",
                kind=CompletionKind.SYNTAX,
                detail="Unordered list item (dash style)",
                documentation="- Item\n- Another item",
                insert_text="- ",
                sort_text="list2",
            ),
            CompletionItem(
                text=". Ordered list item",
                kind=CompletionKind.SYNTAX,
                detail="Ordered list item (numbered)",
                documentation=". First\n. Second\n. Third",
                insert_text=". ",
                sort_text="list3",
            ),
            # Blocks
            CompletionItem(
                text="[source,python]",
                kind=CompletionKind.SYNTAX,
                detail="Source code block",
                documentation="[source,python]\n----\ndef hello():\n    print('hi')\n----",
                insert_text="[source,python]\n----\n\n----",
                sort_text="block1",
            ),
            CompletionItem(
                text="[example]",
                kind=CompletionKind.SYNTAX,
                detail="Example block",
                documentation="[example]\n====\nExample content here\n====",
                insert_text="[example]\n====\n\n====",
                sort_text="block2",
            ),
            CompletionItem(
                text="[NOTE]",
                kind=CompletionKind.SYNTAX,
                detail="Note admonition",
                documentation="[NOTE]\n====\nImportant note here\n====",
                insert_text="[NOTE]\n====\n\n====",
                sort_text="block3",
            ),
            CompletionItem(
                text="[TIP]",
                kind=CompletionKind.SYNTAX,
                detail="Tip admonition",
                documentation="[TIP]\n====\nHelpful tip here\n====",
                insert_text="[TIP]\n====\n\n====",
                sort_text="block4",
            ),
            CompletionItem(
                text="[WARNING]",
                kind=CompletionKind.SYNTAX,
                detail="Warning admonition",
                documentation="[WARNING]\n====\nWarning message here\n====",
                insert_text="[WARNING]\n====\n\n====",
                sort_text="block5",
            ),
            CompletionItem(
                text="[IMPORTANT]",
                kind=CompletionKind.SYNTAX,
                detail="Important admonition",
                documentation="[IMPORTANT]\n====\nImportant information\n====",
                insert_text="[IMPORTANT]\n====\n\n====",
                sort_text="block6",
            ),
            CompletionItem(
                text="[CAUTION]",
                kind=CompletionKind.SYNTAX,
                detail="Caution admonition",
                documentation="[CAUTION]\n====\nBe careful about this\n====",
                insert_text="[CAUTION]\n====\n\n====",
                sort_text="block7",
            ),
            # Inline formatting
            CompletionItem(
                text="*bold*",
                kind=CompletionKind.SYNTAX,
                detail="Bold text",
                documentation="*bold* for **strong** text",
                insert_text="*",
                sort_text="inline1",
            ),
            CompletionItem(
                text="_italic_",
                kind=CompletionKind.SYNTAX,
                detail="Italic text",
                documentation="_italic_ for *emphasized* text",
                insert_text="_",
                sort_text="inline2",
            ),
            CompletionItem(
                text="`monospace`",
                kind=CompletionKind.SYNTAX,
                detail="Monospace text",
                documentation="`code` for inline code",
                insert_text="`",
                sort_text="inline3",
            ),
            # Links and images
            CompletionItem(
                text="link:URL[text]",
                kind=CompletionKind.SYNTAX,
                detail="External link",
                documentation="link:https://example.com[Example Site]",
                insert_text="link:",
                sort_text="link1",
            ),
            CompletionItem(
                text="https://URL[text]",
                kind=CompletionKind.SYNTAX,
                detail="URL with label",
                documentation="https://example.com[Link Text]",
                insert_text="https://",
                sort_text="link2",
            ),
            CompletionItem(
                text="image::path[]",
                kind=CompletionKind.SYNTAX,
                detail="Block image",
                documentation="image::path/to/image.png[Alt text]",
                insert_text="image::",
                sort_text="image1",
            ),
            CompletionItem(
                text="image:path[]",
                kind=CompletionKind.SYNTAX,
                detail="Inline image",
                documentation="image:icon.png[Icon,16,16]",
                insert_text="image:",
                sort_text="image2",
            ),
        ]

    def _get_heading_completions(
        self, context: CompletionContext
    ) -> List[CompletionItem]:
        """Get heading-specific completions based on level."""
        level = len(context.line) - len(context.line.lstrip("="))
        heading_items = [
            item for item in self.completions if item.text.startswith("=" * level + " ")
        ]
        return heading_items if heading_items else self.completions

    def _get_block_completions(self) -> List[CompletionItem]:
        """Get block-specific completions."""
        return [item for item in self.completions if item.text.startswith("[")]

    def _get_list_completions(self) -> List[CompletionItem]:
        """Get list-specific completions."""
        return [
            item
            for item in self.completions
            if item.text.startswith(("*", "-", ".")) and "list" in item.detail.lower()
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

    def get_completions(self, context: CompletionContext) -> List[CompletionItem]:
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

    def _get_built_in_attributes(self) -> List[CompletionItem]:
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

    def _get_attribute_references(self) -> List[CompletionItem]:
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

    def get_completions(self, context: CompletionContext) -> List[CompletionItem]:
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

    def _extract_anchors(self) -> List[str]:
        """Extract all anchor IDs from document."""
        import re

        # Match [[id]] and [#id] patterns
        pattern = r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"
        matches = re.findall(pattern, self.document)
        # Flatten tuples (each match has 2 groups)
        return [m[0] or m[1] for m in matches]

    def _get_anchor_completions(self) -> List[CompletionItem]:
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
        self.current_file_path = (
            Path(current_file_path) if current_file_path else Path.cwd()
        )
        self.base_dir = (
            self.current_file_path.parent
            if self.current_file_path.is_file()
            else self.current_file_path
        )

    def get_completions(self, context: CompletionContext) -> List[CompletionItem]:
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

    def _get_file_completions(self) -> List[CompletionItem]:
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
    """

    def __init__(self) -> None:
        """Initialize snippet provider with built-in snippets."""
        self.snippets = self._get_built_in_snippets()

    def get_completions(self, context: CompletionContext) -> List[CompletionItem]:
        """
        Return snippet completions.

        Args:
            context: Current editor context

        Returns:
            List of snippet completion items
        """
        # Snippets are always available (manual trigger or specific keywords)
        return self.snippets

    def _get_built_in_snippets(self) -> List[CompletionItem]:
        """Get built-in code snippets."""
        return [
            CompletionItem(
                text="table",
                kind=CompletionKind.SNIPPET,
                detail="Insert table",
                documentation="Create a basic table",
                insert_text=(
                    "|===\n|Header 1 |Header 2 |Header 3\n\n"
                    "|Cell 1   |Cell 2   |Cell 3\n"
                    "|Cell 4   |Cell 5   |Cell 6\n|==="
                ),
            ),
            CompletionItem(
                text="figure",
                kind=CompletionKind.SNIPPET,
                detail="Insert figure with caption",
                documentation="Image with caption",
                insert_text=".Figure caption\nimage::path/to/image.png[Alt text]",
            ),
            CompletionItem(
                text="codeblock",
                kind=CompletionKind.SNIPPET,
                detail="Insert code block",
                documentation="Source code block with syntax highlighting",
                insert_text="[source,python]\n----\n# Your code here\n----",
            ),
            CompletionItem(
                text="listing",
                kind=CompletionKind.SNIPPET,
                detail="Insert listing block",
                documentation="Listing block for code or console output",
                insert_text="[listing]\n----\n# Listing content\n----",
            ),
            CompletionItem(
                text="sidebar",
                kind=CompletionKind.SNIPPET,
                detail="Insert sidebar",
                documentation="Sidebar for supplementary content",
                insert_text=".Sidebar Title\n****\nSidebar content here\n****",
            ),
        ]
