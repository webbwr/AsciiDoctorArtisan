"""
Tests for autocomplete_providers module.

Tests all 5 provider classes for AsciiDoc auto-completion.
"""

from pathlib import Path

import pytest

from asciidoc_artisan.core.autocomplete_providers import (
    AttributeProvider,
    CrossRefProvider,
    IncludeProvider,
    SnippetProvider,
    SyntaxProvider,
)
from asciidoc_artisan.core.models import CompletionContext, CompletionKind


@pytest.mark.unit
class TestSyntaxProvider:
    """Test SyntaxProvider class."""

    def test_init(self):
        """Test provider initialization."""
        provider = SyntaxProvider()

        assert provider.completions is not None
        assert isinstance(provider.completions, list)
        assert len(provider.completions) > 0

    def test_build_completion_items_has_headings(self):
        """Test built-in completions include headings."""
        provider = SyntaxProvider()

        heading_items = [
            item for item in provider.completions if item.text.startswith("=")
        ]
        assert len(heading_items) >= 5  # 5 heading levels

    def test_build_completion_items_has_lists(self):
        """Test built-in completions include list items."""
        provider = SyntaxProvider()

        list_items = [
            item
            for item in provider.completions
            if item.text.startswith(("*", "-", "."))
        ]
        assert len(list_items) >= 3  # *, -, .

    def test_build_completion_items_has_blocks(self):
        """Test built-in completions include block elements."""
        provider = SyntaxProvider()

        block_items = [
            item for item in provider.completions if item.text.startswith("[")
        ]
        assert len(block_items) >= 7  # source, example, NOTE, TIP, etc.

    def test_get_completions_default_returns_all(self):
        """Test get_completions returns all items by default."""
        provider = SyntaxProvider()
        context = CompletionContext(
            line="Some text",
            line_number=5,
            column=9,
            word_before_cursor="text",
            prefix="Some ",
            trigger_char=None,
            manual=True,
        )

        items = provider.get_completions(context)

        assert len(items) == len(provider.completions)

    def test_get_completions_heading_context(self):
        """Test heading context returns heading-specific completions."""
        provider = SyntaxProvider()
        context = CompletionContext(
            line="==",
            line_number=1,
            column=2,
            word_before_cursor="==",
            prefix="==",
            trigger_char="=",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return level 2 headings (may also include others based on implementation)
        # At minimum, should include level 2 headings
        level_2_items = [item for item in items if item.text.startswith("== ")]
        assert len(level_2_items) > 0

    def test_get_completions_block_context(self):
        """Test block context returns block completions."""
        provider = SyntaxProvider()
        context = CompletionContext(
            line="[",
            line_number=1,
            column=1,
            word_before_cursor="[",
            prefix="[",
            trigger_char="[",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return only block items
        assert all(item.text.startswith("[") for item in items)
        assert len(items) > 0

    def test_get_completions_list_context(self):
        """Test list context returns list completions."""
        provider = SyntaxProvider()
        context = CompletionContext(
            line="* ",
            line_number=1,
            column=2,
            word_before_cursor="* ",
            prefix="* ",
            trigger_char="*",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return list items
        assert all("list" in item.detail.lower() for item in items)
        assert len(items) > 0

    def test_get_heading_completions_level_1(self):
        """Test level 1 heading completion."""
        provider = SyntaxProvider()
        context = CompletionContext(
            line="=",
            line_number=1,
            column=1,
            word_before_cursor="=",
            prefix="=",
            trigger_char="=",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should include "= Document Title"
        titles = [item for item in items if "Document Title" in item.text]
        assert len(titles) > 0

    def test_get_block_completions(self):
        """Test block completions filtering."""
        provider = SyntaxProvider()

        items = provider._get_block_completions()

        assert all(item.text.startswith("[") for item in items)
        assert len(items) >= 7

    def test_get_list_completions(self):
        """Test list completions filtering."""
        provider = SyntaxProvider()

        items = provider._get_list_completions()

        assert all(item.text.startswith(("*", "-", ".")) for item in items)
        assert all("list" in item.detail.lower() for item in items)


@pytest.mark.unit
class TestAttributeProvider:
    """Test AttributeProvider class."""

    def test_init(self):
        """Test provider initialization."""
        provider = AttributeProvider(document="")

        assert provider.document == ""
        assert provider.built_in_attributes is not None
        assert len(provider.built_in_attributes) > 0

    def test_init_with_document(self):
        """Test provider initialization with document text."""
        doc = ":author: John\n:version: 1.0"
        provider = AttributeProvider(document=doc)

        assert provider.document == doc

    def test_get_built_in_attributes_includes_common_attrs(self):
        """Test built-in attributes include common ones."""
        provider = AttributeProvider()

        attr_texts = [item.text for item in provider.built_in_attributes]

        assert ":author:" in attr_texts
        assert ":version:" in attr_texts
        assert ":toc:" in attr_texts

    def test_get_completions_attribute_definition_context(self):
        """Test completions for :attr: definition context."""
        provider = AttributeProvider()
        context = CompletionContext(
            line=":author",
            line_number=1,
            column=7,
            word_before_cursor="author",
            prefix=":author",
            trigger_char=":",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return built-in attributes
        assert len(items) == len(provider.built_in_attributes)

    def test_get_completions_attribute_reference_context(self):
        """Test completions for {attr} reference context."""
        doc = ":author: John Doe\n:version: 1.0"
        provider = AttributeProvider(document=doc)
        context = CompletionContext(
            line="Author: {",
            line_number=5,
            column=9,
            word_before_cursor="{",
            prefix="Author: {",
            trigger_char="{",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return references to defined attributes
        assert len(items) >= 2
        texts = [item.text for item in items]
        assert "{author}" in texts
        assert "{version}" in texts

    def test_get_completions_no_context(self):
        """Test completions return empty for non-attribute context."""
        provider = AttributeProvider()
        context = CompletionContext(
            line="Regular text",
            line_number=5,
            column=12,
            word_before_cursor="text",
            prefix="Regular ",
            trigger_char=None,
            manual=False,
        )

        items = provider.get_completions(context)

        assert len(items) == 0

    def test_get_attribute_references_extracts_defined_attrs(self):
        """Test extraction of defined attributes from document."""
        doc = ":author: John\n:version: 1.0\n:custom: Value"
        provider = AttributeProvider(document=doc)

        items = provider._get_attribute_references()

        texts = [item.text for item in items]
        assert "{author}" in texts
        assert "{version}" in texts
        assert "{custom}" in texts

    def test_get_attribute_references_empty_document(self):
        """Test attribute references with no defined attributes."""
        provider = AttributeProvider(document="")

        items = provider._get_attribute_references()

        assert len(items) == 0


@pytest.mark.unit
class TestCrossRefProvider:
    """Test CrossRefProvider class."""

    def test_init(self):
        """Test provider initialization."""
        provider = CrossRefProvider(document="")

        assert provider.document == ""
        assert provider.anchors is not None
        assert isinstance(provider.anchors, list)

    def test_init_with_document(self):
        """Test provider initialization with document containing anchors."""
        doc = "[[intro]]\n== Introduction\n\n[[summary]]\n== Summary"
        provider = CrossRefProvider(document=doc)

        assert "intro" in provider.anchors
        assert "summary" in provider.anchors

    def test_extract_anchors_double_bracket_syntax(self):
        """Test extraction of [[id]] anchors."""
        doc = "[[first]]\n== First\n\n[[second]]\n== Second"
        provider = CrossRefProvider(document=doc)

        assert "first" in provider.anchors
        assert "second" in provider.anchors

    def test_extract_anchors_hash_syntax(self):
        """Test extraction of [#id] anchors."""
        doc = "[#first]\n== First\n\n[#second]\n== Second"
        provider = CrossRefProvider(document=doc)

        assert "first" in provider.anchors
        assert "second" in provider.anchors

    def test_extract_anchors_mixed_syntax(self):
        """Test extraction of mixed anchor styles."""
        doc = "[[bracket]]\n== First\n\n[#hash]\n== Second"
        provider = CrossRefProvider(document=doc)

        assert "bracket" in provider.anchors
        assert "hash" in provider.anchors

    def test_extract_anchors_empty_document(self):
        """Test anchor extraction from empty document."""
        provider = CrossRefProvider(document="")

        assert len(provider.anchors) == 0

    def test_get_completions_xref_context(self):
        """Test completions for <<>> cross-reference context."""
        doc = "[[intro]]\n== Introduction"
        provider = CrossRefProvider(document=doc)
        context = CompletionContext(
            line="See <<",
            line_number=5,
            column=6,
            word_before_cursor="<<",
            prefix="See <<",
            trigger_char="<",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return anchor completions
        assert len(items) >= 1
        texts = [item.text for item in items]
        assert "<<intro>>" in texts

    def test_get_completions_no_context(self):
        """Test completions return empty for non-xref context."""
        doc = "[[intro]]\n== Introduction"
        provider = CrossRefProvider(document=doc)
        context = CompletionContext(
            line="Regular text",
            line_number=5,
            column=12,
            word_before_cursor="text",
            prefix="Regular ",
            trigger_char=None,
            manual=False,
        )

        items = provider.get_completions(context)

        assert len(items) == 0

    def test_get_anchor_completions(self):
        """Test anchor completion generation."""
        doc = "[[first]]\n[[second]]\n[[third]]"
        provider = CrossRefProvider(document=doc)

        items = provider._get_anchor_completions()

        assert len(items) == 3
        texts = [item.text for item in items]
        assert "<<first>>" in texts
        assert "<<second>>" in texts
        assert "<<third>>" in texts

    def test_get_anchor_completions_empty(self):
        """Test anchor completions with no anchors."""
        provider = CrossRefProvider(document="")

        items = provider._get_anchor_completions()

        assert len(items) == 0


@pytest.mark.unit
class TestIncludeProvider:
    """Test IncludeProvider class."""

    def test_init_default(self):
        """Test provider initialization with default path."""
        provider = IncludeProvider()

        assert provider.current_file_path == Path.cwd()
        assert provider.base_dir is not None

    def test_init_with_file_path(self, tmp_path):
        """Test provider initialization with file path."""
        test_file = tmp_path / "test.adoc"
        test_file.touch()

        provider = IncludeProvider(current_file_path=str(test_file))

        assert provider.current_file_path == test_file
        assert provider.base_dir == tmp_path

    def test_init_with_directory_path(self, tmp_path):
        """Test provider initialization with directory path."""
        provider = IncludeProvider(current_file_path=str(tmp_path))

        assert provider.current_file_path == tmp_path
        assert provider.base_dir == tmp_path

    def test_get_completions_include_context(self, tmp_path):
        """Test completions for include:: context."""
        # Create test .adoc files
        (tmp_path / "chapter1.adoc").touch()
        (tmp_path / "chapter2.adoc").touch()

        provider = IncludeProvider(current_file_path=str(tmp_path))
        context = CompletionContext(
            line="include::",
            line_number=1,
            column=9,
            word_before_cursor="include::",
            prefix="include::",
            trigger_char=":",
            manual=False,
        )

        items = provider.get_completions(context)

        # Should return .adoc file completions
        assert len(items) >= 2
        texts = [item.text for item in items]
        assert any("chapter1.adoc" in text for text in texts)
        assert any("chapter2.adoc" in text for text in texts)

    def test_get_completions_no_context(self, tmp_path):
        """Test completions return empty for non-include context."""
        provider = IncludeProvider(current_file_path=str(tmp_path))
        context = CompletionContext(
            line="Regular text",
            line_number=5,
            column=12,
            word_before_cursor="text",
            prefix="Regular ",
            trigger_char=None,
            manual=False,
        )

        items = provider.get_completions(context)

        assert len(items) == 0

    def test_get_file_completions_finds_adoc_files(self, tmp_path):
        """Test finding .adoc files in directory."""
        # Create test files
        (tmp_path / "doc1.adoc").touch()
        (tmp_path / "doc2.adoc").touch()
        (tmp_path / "other.txt").touch()  # Should be ignored

        provider = IncludeProvider(current_file_path=str(tmp_path))

        items = provider._get_file_completions()

        assert len(items) == 2
        texts = [item.text for item in items]
        assert any("doc1.adoc" in text for text in texts)
        assert any("doc2.adoc" in text for text in texts)
        assert not any("other.txt" in text for text in texts)

    def test_get_file_completions_finds_nested_files(self, tmp_path):
        """Test finding .adoc files in subdirectories."""
        # Create nested structure
        subdir = tmp_path / "chapters"
        subdir.mkdir()
        (subdir / "intro.adoc").touch()

        provider = IncludeProvider(current_file_path=str(tmp_path))

        items = provider._get_file_completions()

        assert len(items) >= 1
        texts = [item.text for item in items]
        assert any("intro.adoc" in text for text in texts)

    def test_get_file_completions_handles_errors_gracefully(self):
        """Test file completions handle errors gracefully (lines 529-531)."""
        from unittest.mock import Mock

        provider = IncludeProvider()

        # Mock base_dir.rglob to raise an exception
        provider.base_dir = Mock()
        provider.base_dir.rglob.side_effect = PermissionError("Access denied")

        # Should not raise exception - should catch and return empty list
        items = provider._get_file_completions()

        # Should return empty list after exception
        assert isinstance(items, list)
        assert len(items) == 0


@pytest.mark.unit
class TestSnippetProvider:
    """Test SnippetProvider class."""

    def test_init(self):
        """Test provider initialization."""
        provider = SnippetProvider()

        assert provider.snippets is not None
        assert isinstance(provider.snippets, list)
        assert len(provider.snippets) > 0

    def test_get_built_in_snippets_includes_table(self):
        """Test built-in snippets include table."""
        provider = SnippetProvider()

        texts = [item.text for item in provider.snippets]
        assert "table" in texts

    def test_get_built_in_snippets_includes_figure(self):
        """Test built-in snippets include figure."""
        provider = SnippetProvider()

        texts = [item.text for item in provider.snippets]
        assert "figure" in texts

    def test_get_built_in_snippets_includes_codeblock(self):
        """Test built-in snippets include code block."""
        provider = SnippetProvider()

        texts = [item.text for item in provider.snippets]
        assert "codeblock" in texts

    def test_get_completions_returns_all_snippets(self):
        """Test get_completions always returns all snippets."""
        provider = SnippetProvider()
        context = CompletionContext(
            line="Some text",
            line_number=5,
            column=9,
            word_before_cursor="text",
            prefix="Some ",
            trigger_char=None,
            manual=True,
        )

        items = provider.get_completions(context)

        # Should return all snippets
        assert len(items) == len(provider.snippets)

    def test_get_completions_works_with_any_context(self):
        """Test snippets work regardless of context."""
        provider = SnippetProvider()

        # Try different contexts
        contexts = [
            CompletionContext(
                line="",
                line_number=1,
                column=0,
                word_before_cursor="",
                prefix="",
                trigger_char=None,
                manual=True,
            ),
            CompletionContext(
                line="==",
                line_number=1,
                column=2,
                word_before_cursor="==",
                prefix="==",
                trigger_char="=",
                manual=False,
            ),
            CompletionContext(
                line="text",
                line_number=5,
                column=4,
                word_before_cursor="text",
                prefix="text",
                trigger_char=None,
                manual=False,
            ),
        ]

        for context in contexts:
            items = provider.get_completions(context)
            assert len(items) == len(provider.snippets)

    def test_snippet_items_have_correct_kind(self):
        """Test snippet items have SNIPPET kind."""
        provider = SnippetProvider()

        for item in provider.snippets:
            assert item.kind == CompletionKind.SNIPPET

    def test_snippet_items_have_insert_text(self):
        """Test snippet items have insert_text."""
        provider = SnippetProvider()

        for item in provider.snippets:
            assert item.insert_text is not None
            assert len(item.insert_text) > 0
