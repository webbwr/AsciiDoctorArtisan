"""
Completion data builders for AsciiDoc Artisan autocomplete.

This module provides cached completion item data for syntax and snippets.
Extracted from autocomplete_providers.py for MA principle compliance.

Module-level caching:
- Syntax and snippet data is cached at module level (lazy singleton pattern)
- This saves ~50-100ms on repeated provider instantiation

Example:
    ```python
    from asciidoc_artisan.core.completion_data import (
        get_cached_syntax_completions,
        get_cached_snippet_completions,
    )

    syntax_items = get_cached_syntax_completions()
    snippet_items = get_cached_snippet_completions()
    ```
"""

from asciidoc_artisan.core.models import CompletionItem, CompletionKind

# =============================================================================
# MODULE-LEVEL CACHING (MA principle: avoid regenerating static data)
# =============================================================================
# These caches store immutable completion data, loaded once per process.
# Cache invalidation not needed since data is static.

_SYNTAX_COMPLETIONS_CACHE: list[CompletionItem] | None = None
_SNIPPET_COMPLETIONS_CACHE: list[CompletionItem] | None = None


def get_cached_syntax_completions() -> list[CompletionItem]:
    """Get syntax completions with module-level caching.

    Returns:
        Cached list of syntax completion items (shared across all instances)
    """
    global _SYNTAX_COMPLETIONS_CACHE
    if _SYNTAX_COMPLETIONS_CACHE is None:
        _SYNTAX_COMPLETIONS_CACHE = _build_syntax_completions()
    return _SYNTAX_COMPLETIONS_CACHE


def get_cached_snippet_completions() -> list[CompletionItem]:
    """Get snippet completions with module-level caching.

    Returns:
        Cached list of snippet completion items (shared across all instances)
    """
    global _SNIPPET_COMPLETIONS_CACHE
    if _SNIPPET_COMPLETIONS_CACHE is None:
        _SNIPPET_COMPLETIONS_CACHE = _build_snippet_completions()
    return _SNIPPET_COMPLETIONS_CACHE


def _build_syntax_completions() -> list[CompletionItem]:
    """Build static list of syntax completions (called once per process)."""
    return [
        *_get_heading_items(),
        *_get_list_items(),
        *_get_block_items(),
        *_get_inline_items(),
        *_get_link_items(),
    ]


def _build_snippet_completions() -> list[CompletionItem]:
    """Build static list of snippet completions (called once per process)."""
    return [
        CompletionItem(
            text="table",
            kind=CompletionKind.SNIPPET,
            detail="Insert table",
            documentation="Create a basic table",
            insert_text=(
                "|===\n|Header 1 |Header 2 |Header 3\n\n|Cell 1   |Cell 2   |Cell 3\n|Cell 4   |Cell 5   |Cell 6\n|==="
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


# =============================================================================
# HELPER FUNCTIONS FOR SYNTAX ITEMS (used by cache builder)
# =============================================================================


def _get_heading_items() -> list[CompletionItem]:
    """Get heading completion items (levels 1-5)."""
    return [
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
    ]


def _get_list_items() -> list[CompletionItem]:
    """Get list completion items."""
    return [
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
    ]


def _get_block_data() -> list[tuple[str, str, str, str]]:
    """Get block and admonition data as tuples.

    Returns:
        List of (text, detail, documentation, insert_text) tuples
    """
    return [
        (
            "[source,python]",
            "Source code block",
            "[source,python]\n----\ndef hello():\n    print('hi')\n----",
            "[source,python]\n----\n\n----",
        ),
        (
            "[example]",
            "Example block",
            "[example]\n====\nExample content here\n====",
            "[example]\n====\n\n====",
        ),
        (
            "[NOTE]",
            "Note admonition",
            "[NOTE]\n====\nImportant note here\n====",
            "[NOTE]\n====\n\n====",
        ),
        (
            "[TIP]",
            "Tip admonition",
            "[TIP]\n====\nHelpful tip here\n====",
            "[TIP]\n====\n\n====",
        ),
        (
            "[WARNING]",
            "Warning admonition",
            "[WARNING]\n====\nWarning message here\n====",
            "[WARNING]\n====\n\n====",
        ),
        (
            "[IMPORTANT]",
            "Important admonition",
            "[IMPORTANT]\n====\nImportant information\n====",
            "[IMPORTANT]\n====\n\n====",
        ),
        (
            "[CAUTION]",
            "Caution admonition",
            "[CAUTION]\n====\nBe careful about this\n====",
            "[CAUTION]\n====\n\n====",
        ),
    ]


def _get_block_items() -> list[CompletionItem]:
    """Get block and admonition completion items."""
    block_data = _get_block_data()
    return [
        CompletionItem(
            text=text,
            kind=CompletionKind.SYNTAX,
            detail=detail,
            documentation=doc,
            insert_text=insert,
            sort_text=f"block{i + 1}",
        )
        for i, (text, detail, doc, insert) in enumerate(block_data)
    ]


def _get_inline_items() -> list[CompletionItem]:
    """Get inline formatting completion items."""
    return [
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
    ]


def _get_link_items() -> list[CompletionItem]:
    """Get link and image completion items."""
    return [
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
