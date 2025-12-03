"""
Completion Provider for AsciiDoc LSP.

MA principle: ~250 lines focused on completion logic.

Provides intelligent auto-completion for AsciiDoc documents:
- Syntax elements (headings, blocks, lists)
- Document attributes (:attribute:)
- Cross-references (<<anchor>>)
- Include directives (include::path[])
- Block delimiters (----, ====, etc.)

Uses the existing autocomplete_engine where possible.
"""

import logging
import re

from lsprotocol import types as lsp

logger = logging.getLogger(__name__)


# AsciiDoc syntax completions
SYNTAX_COMPLETIONS = [
    # Headings
    ("= Title (Level 0)", "= ", "Document title", lsp.CompletionItemKind.Text),
    ("== Heading (Level 1)", "== ", "Section heading", lsp.CompletionItemKind.Text),
    ("=== Heading (Level 2)", "=== ", "Subsection", lsp.CompletionItemKind.Text),
    ("==== Heading (Level 3)", "==== ", "Sub-subsection", lsp.CompletionItemKind.Text),
    ("===== Heading (Level 4)", "===== ", "Paragraph heading", lsp.CompletionItemKind.Text),
    # Lists
    ("* Unordered list", "* ", "Bullet list item", lsp.CompletionItemKind.Text),
    (". Ordered list", ". ", "Numbered list item", lsp.CompletionItemKind.Text),
    ("- Unordered list", "- ", "Dash list item", lsp.CompletionItemKind.Text),
    # Blocks
    ("[source]", "[source]\n----\n\n----", "Source code block", lsp.CompletionItemKind.Snippet),
    ("[source,python]", "[source,python]\n----\n\n----", "Python code block", lsp.CompletionItemKind.Snippet),
    ("[source,bash]", "[source,bash]\n----\n\n----", "Bash code block", lsp.CompletionItemKind.Snippet),
    ("[NOTE]", "[NOTE]\n====\n\n====", "Note admonition", lsp.CompletionItemKind.Snippet),
    ("[TIP]", "[TIP]\n====\n\n====", "Tip admonition", lsp.CompletionItemKind.Snippet),
    ("[WARNING]", "[WARNING]\n====\n\n====", "Warning admonition", lsp.CompletionItemKind.Snippet),
    ("[IMPORTANT]", "[IMPORTANT]\n====\n\n====", "Important admonition", lsp.CompletionItemKind.Snippet),
    ("[CAUTION]", "[CAUTION]\n====\n\n====", "Caution admonition", lsp.CompletionItemKind.Snippet),
    ("[quote]", "[quote]\n____\n\n____", "Quote block", lsp.CompletionItemKind.Snippet),
    ("[verse]", "[verse]\n____\n\n____", "Verse block", lsp.CompletionItemKind.Snippet),
    ("[sidebar]", "[sidebar]\n****\n\n****", "Sidebar block", lsp.CompletionItemKind.Snippet),
    ("[example]", "[example]\n====\n\n====", "Example block", lsp.CompletionItemKind.Snippet),
    # Block delimiters
    ("----", "----\n\n----", "Listing block", lsp.CompletionItemKind.Snippet),
    ("====", "====\n\n====", "Example/Admonition block", lsp.CompletionItemKind.Snippet),
    ("****", "****\n\n****", "Sidebar block", lsp.CompletionItemKind.Snippet),
    ("____", "____\n\n____", "Quote block", lsp.CompletionItemKind.Snippet),
    ("////", "////\n\n////", "Comment block", lsp.CompletionItemKind.Snippet),
    ("++++", "++++\n\n++++", "Passthrough block", lsp.CompletionItemKind.Snippet),
    # Formatting
    ("*bold*", "*${1:text}*", "Bold text", lsp.CompletionItemKind.Snippet),
    ("_italic_", "_${1:text}_", "Italic text", lsp.CompletionItemKind.Snippet),
    ("`monospace`", "`${1:text}`", "Monospace text", lsp.CompletionItemKind.Snippet),
    ("^superscript^", "^${1:text}^", "Superscript", lsp.CompletionItemKind.Snippet),
    ("~subscript~", "~${1:text}~", "Subscript", lsp.CompletionItemKind.Snippet),
    ("#highlight#", "#${1:text}#", "Highlighted text", lsp.CompletionItemKind.Snippet),
    # Links and references
    ("link:url[text]", "link:${1:url}[${2:text}]", "External link", lsp.CompletionItemKind.Snippet),
    ("<<anchor>>", "<<${1:anchor}>>", "Cross-reference", lsp.CompletionItemKind.Snippet),
    ("<<anchor,text>>", "<<${1:anchor},${2:text}>>", "Cross-reference with text", lsp.CompletionItemKind.Snippet),
    ("[[anchor]]", "[[${1:anchor}]]", "Anchor definition", lsp.CompletionItemKind.Snippet),
    ("[#anchor]", "[#${1:anchor}]", "Block anchor", lsp.CompletionItemKind.Snippet),
    # Images
    ("image::path[]", "image::${1:path}[${2:alt}]", "Block image", lsp.CompletionItemKind.Snippet),
    ("image:path[]", "image:${1:path}[${2:alt}]", "Inline image", lsp.CompletionItemKind.Snippet),
    # Includes
    ("include::path[]", "include::${1:path}[]", "Include file", lsp.CompletionItemKind.Snippet),
    # Tables
    ("|===", "|===\n|${1:cell}\n|===", "Table", lsp.CompletionItemKind.Snippet),
    ('[cols="1,1"]', '[cols="${1:1,1}"]\n|===\n|${2:cell}\n|===', "Table with columns", lsp.CompletionItemKind.Snippet),
]

# Common document attributes
ATTRIBUTE_COMPLETIONS = [
    (":author:", ":author: ", "Document author"),
    (":email:", ":email: ", "Author email"),
    (":revdate:", ":revdate: ", "Revision date"),
    (":revnumber:", ":revnumber: ", "Revision number"),
    (":version:", ":version: ", "Version number"),
    (":toc:", ":toc:", "Enable table of contents"),
    (":toc-title:", ":toc-title: ", "TOC title"),
    (":toclevels:", ":toclevels: ", "TOC depth"),
    (":sectnums:", ":sectnums:", "Enable section numbering"),
    (":sectnumlevels:", ":sectnumlevels: ", "Section numbering depth"),
    (":icons:", ":icons: font", "Enable icons"),
    (":imagesdir:", ":imagesdir: ", "Images directory"),
    (":source-highlighter:", ":source-highlighter: ", "Code highlighter"),
    (":doctype:", ":doctype: ", "Document type"),
    (":description:", ":description: ", "Document description"),
    (":keywords:", ":keywords: ", "Document keywords"),
    (":experimental:", ":experimental:", "Enable experimental features"),
    (":stem:", ":stem:", "Enable STEM support"),
]


class AsciiDocCompletionProvider:
    """
    Provides auto-completion for AsciiDoc documents.

    Supports:
    - Context-aware syntax completion
    - Document attributes
    - Cross-references to anchors in document
    - Include paths

    Performance: <50ms for typical completion requests.
    """

    def __init__(self) -> None:
        """Initialize completion provider."""
        self._anchor_pattern = re.compile(r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]")
        self._attribute_pattern = re.compile(r"^:([^:]+):", re.MULTILINE)

    def get_completions(self, text: str, position: lsp.Position) -> list[lsp.CompletionItem]:
        """
        Get completion items for given position.

        Args:
            text: Document text
            position: Cursor position

        Returns:
            List of completion items
        """
        lines = text.splitlines()
        if position.line >= len(lines):
            return []

        line = lines[position.line]
        prefix = line[: position.character]

        # Determine completion context
        if self._is_attribute_context(prefix):
            return self._get_attribute_completions(prefix)
        elif self._is_xref_context(prefix):
            return self._get_xref_completions(text, prefix)
        elif self._is_include_context(prefix):
            return self._get_include_completions(prefix)
        else:
            return self._get_syntax_completions(prefix, line)

    def _is_attribute_context(self, prefix: str) -> bool:
        """Check if cursor is in attribute context (: at line start)."""
        return prefix.startswith(":") and not prefix.endswith(":")

    def _is_xref_context(self, prefix: str) -> bool:
        """Check if cursor is in cross-reference context (<<)."""
        return "<<" in prefix and ">>" not in prefix

    def _is_include_context(self, prefix: str) -> bool:
        """Check if cursor is in include context (include::)."""
        return "include::" in prefix

    def _get_syntax_completions(self, prefix: str, line: str) -> list[lsp.CompletionItem]:
        """Get syntax-based completions."""
        items = []
        prefix_lower = prefix.lower().strip()

        for label, insert_text, detail, kind in SYNTAX_COMPLETIONS:
            # Filter by prefix
            if not prefix_lower or label.lower().startswith(prefix_lower):
                item = lsp.CompletionItem(
                    label=label,
                    kind=kind,
                    detail=detail,
                    insert_text=insert_text,
                    insert_text_format=lsp.InsertTextFormat.Snippet
                    if kind == lsp.CompletionItemKind.Snippet
                    else lsp.InsertTextFormat.PlainText,
                )
                items.append(item)

        return items[:50]  # Limit results

    def _get_attribute_completions(self, prefix: str) -> list[lsp.CompletionItem]:
        """Get document attribute completions."""
        items = []
        prefix_lower = prefix.lower()

        for label, insert_text, detail in ATTRIBUTE_COMPLETIONS:
            if label.lower().startswith(prefix_lower):
                item = lsp.CompletionItem(
                    label=label,
                    kind=lsp.CompletionItemKind.Property,
                    detail=detail,
                    insert_text=insert_text,
                )
                items.append(item)

        return items

    def _get_xref_completions(self, text: str, prefix: str) -> list[lsp.CompletionItem]:
        """Get cross-reference completions (anchors in document)."""
        items = []

        # Find all anchors in document
        anchors = self._extract_anchors(text)

        # Get partial anchor text after <<
        partial = ""
        if "<<" in prefix:
            partial = prefix.split("<<")[-1].lower()

        for anchor in anchors:
            if not partial or anchor.lower().startswith(partial):
                item = lsp.CompletionItem(
                    label=anchor,
                    kind=lsp.CompletionItemKind.Reference,
                    detail=f"Reference to {anchor}",
                    insert_text=f"{anchor}>>",
                )
                items.append(item)

        return items

    def _get_include_completions(self, prefix: str) -> list[lsp.CompletionItem]:
        """Get include directive completions."""
        # Basic include completions - could be extended with file system lookup
        items = [
            lsp.CompletionItem(
                label="include::[]",
                kind=lsp.CompletionItemKind.File,
                detail="Include file",
                insert_text="include::${1:path}[]",
                insert_text_format=lsp.InsertTextFormat.Snippet,
            ),
            lsp.CompletionItem(
                label="include::[leveloffset=+1]",
                kind=lsp.CompletionItemKind.File,
                detail="Include with level offset",
                insert_text="include::${1:path}[leveloffset=+1]",
                insert_text_format=lsp.InsertTextFormat.Snippet,
            ),
            lsp.CompletionItem(
                label="include::[lines=1..10]",
                kind=lsp.CompletionItemKind.File,
                detail="Include specific lines",
                insert_text="include::${1:path}[lines=${2:1..10}]",
                insert_text_format=lsp.InsertTextFormat.Snippet,
            ),
        ]
        return items

    def _extract_anchors(self, text: str) -> list[str]:
        """Extract all anchor IDs from document."""
        matches = self._anchor_pattern.findall(text)
        # Flatten tuples (each match has 2 groups)
        return [m[0] or m[1] for m in matches]
