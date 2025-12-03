"""
Hover Provider for AsciiDoc LSP.

MA principle: ~200 lines focused on hover documentation.

Provides documentation on hover for:
- AsciiDoc syntax elements
- Document attributes
- Cross-references
- Block types
"""

import logging
import re

from lsprotocol import types as lsp

logger = logging.getLogger(__name__)


# Hover documentation for AsciiDoc elements
SYNTAX_DOCS = {
    # Headings
    r"^=\s": {
        "title": "Document Title (Level 0)",
        "docs": """
# Document Title

The document title is defined with a single equals sign.

**Syntax:** `= Title`

**Example:**
```asciidoc
= My Document Title
Author Name <email@example.com>
```
""",
    },
    r"^==\s": {
        "title": "Section Heading (Level 1)",
        "docs": """
# Section Heading

Level 1 sections are the main divisions of your document.

**Syntax:** `== Section Title`

**Example:**
```asciidoc
== Introduction

This is the introduction section.
```
""",
    },
    r"^===\s": {
        "title": "Subsection (Level 2)",
        "docs": """
# Subsection

Level 2 sections divide level 1 sections.

**Syntax:** `=== Subsection Title`
""",
    },
    # Lists
    r"^\*\s": {
        "title": "Unordered List Item",
        "docs": """
# Unordered List

Create bullet points with asterisks.

**Syntax:**
```asciidoc
* First item
* Second item
** Nested item
```
""",
    },
    r"^\.\s": {
        "title": "Ordered List Item",
        "docs": """
# Ordered List

Create numbered lists with periods.

**Syntax:**
```asciidoc
. First item
. Second item
.. Nested item
```
""",
    },
    # Blocks
    r"^\[source": {
        "title": "Source Code Block",
        "docs": """
# Source Code Block

Display formatted source code.

**Syntax:**
```asciidoc
[source,python]
----
def hello():
    print("Hello, World!")
----
```

**Attributes:**
- Language: `[source,python]`
- Line numbers: `[source,python,linenums]`
- Highlight: `[source,python,highlight=2..4]`
""",
    },
    r"^\[NOTE\]": {
        "title": "Note Admonition",
        "docs": """
# Note Admonition

Highlight important information.

**Syntax:**
```asciidoc
[NOTE]
====
This is a note.
====
```

Or inline: `NOTE: This is a note.`
""",
    },
    r"^\[TIP\]": {
        "title": "Tip Admonition",
        "docs": "# Tip\n\nProvide helpful tips. Syntax: `[TIP]` followed by `====` delimiters.",
    },
    r"^\[WARNING\]": {
        "title": "Warning Admonition",
        "docs": "# Warning\n\nWarn about potential issues. Syntax: `[WARNING]` followed by `====` delimiters.",
    },
    r"^\[IMPORTANT\]": {
        "title": "Important Admonition",
        "docs": "# Important\n\nHighlight critical information. Syntax: `[IMPORTANT]` followed by `====` delimiters.",
    },
    r"^\[CAUTION\]": {
        "title": "Caution Admonition",
        "docs": "# Caution\n\nAdvise caution. Syntax: `[CAUTION]` followed by `====` delimiters.",
    },
    # Delimiters
    r"^----$": {
        "title": "Listing Block Delimiter",
        "docs": """
# Listing Block

Used for source code and literal text.

**Syntax:**
```asciidoc
----
code goes here
----
```
""",
    },
    r"^====$": {
        "title": "Example/Admonition Block Delimiter",
        "docs": "# Example Block\n\nUsed for examples and admonitions.\n\n```asciidoc\n====\nExample content\n====\n```",
    },
    r"^____$": {
        "title": "Quote Block Delimiter",
        "docs": "# Quote Block\n\nUsed for quotations.\n\n```asciidoc\n____\nQuoted text\n____\n```",
    },
    r"^\*\*\*\*$": {
        "title": "Sidebar Block Delimiter",
        "docs": "# Sidebar Block\n\nUsed for sidebars.\n\n```asciidoc\n****\nSidebar content\n****\n```",
    },
    # Include
    r"^include::": {
        "title": "Include Directive",
        "docs": """
# Include Directive

Include content from another file.

**Syntax:** `include::path/to/file.adoc[]`

**Options:**
- `leveloffset=+1` - Adjust heading levels
- `lines=1..10` - Include specific lines
- `tag=tagname` - Include tagged region
""",
    },
    # Cross-reference
    r"<<[^>]+>>": {
        "title": "Cross-Reference",
        "docs": """
# Cross-Reference

Link to another location in the document.

**Syntax:**
- `<<anchor>>` - Link to anchor
- `<<anchor,Custom Text>>` - Link with custom text
""",
    },
    # Anchor
    r"\[\[[^\]]+\]\]": {
        "title": "Anchor Definition",
        "docs": """
# Anchor

Define a referenceable location.

**Syntax:** `[[anchor-id]]`

Reference with: `<<anchor-id>>`
""",
    },
}

# Attribute documentation
ATTRIBUTE_DOCS = {
    ":toc:": "Enable table of contents",
    ":sectnums:": "Enable section numbering",
    ":icons:": "Enable icons (font or image)",
    ":source-highlighter:": "Set code highlighting (highlight.js, rouge, etc.)",
    ":imagesdir:": "Set default images directory",
    ":experimental:": "Enable experimental features (kbd, menu, btn macros)",
    ":stem:": "Enable STEM (math) support",
    ":author:": "Document author name",
    ":email:": "Author email address",
    ":revdate:": "Revision date",
    ":revnumber:": "Revision/version number",
}


class AsciiDocHoverProvider:
    """
    Provides hover documentation for AsciiDoc elements.

    Shows contextual documentation when hovering over:
    - Syntax elements (headings, blocks, lists)
    - Document attributes
    - Cross-references
    - Directives
    """

    def __init__(self) -> None:
        """Initialize hover provider."""
        # Compile patterns for faster matching
        self._patterns = [(re.compile(pattern), docs) for pattern, docs in SYNTAX_DOCS.items()]

    def get_hover(self, text: str, position: lsp.Position) -> lsp.Hover | None:
        """
        Get hover information for position.

        Args:
            text: Document text
            position: Cursor position

        Returns:
            Hover information or None
        """
        lines = text.splitlines()
        if position.line >= len(lines):
            return None

        line = lines[position.line]

        # Try to find matching documentation
        for pattern, docs in self._patterns:
            if pattern.search(line):
                content = lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=docs["docs"],
                )
                return lsp.Hover(contents=content)

        # Check for attribute hover
        hover = self._get_attribute_hover(line, position.character)
        if hover:
            return hover

        return None

    def _get_attribute_hover(self, line: str, column: int) -> lsp.Hover | None:
        """Get hover for document attribute."""
        # Check if line starts with :
        if not line.strip().startswith(":"):
            return None

        # Find attribute name
        for attr, description in ATTRIBUTE_DOCS.items():
            if attr in line:
                content = lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=f"**{attr}**\n\n{description}",
                )
                return lsp.Hover(contents=content)

        return None
