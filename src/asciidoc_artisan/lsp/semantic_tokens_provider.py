"""
Semantic Tokens Provider for AsciiDoc LSP.

MA principle: ~200 lines focused on semantic tokenization.

Provides syntax highlighting data for:
- Headings, Attributes, Blocks, Comments
- Macros, Cross-references, Formatting
"""

import logging
import re

from lsprotocol import types as lsp

logger = logging.getLogger(__name__)

# Token types for AsciiDoc
TOKEN_TYPES = [
    "type",  # 0 - Headings
    "namespace",  # 1 - Attribute definitions
    "variable",  # 2 - Attribute references
    "keyword",  # 3 - Block annotations
    "comment",  # 4 - Comments
    "function",  # 5 - Macros
    "decorator",  # 6 - Inline formatting
    "parameter",  # 7 - Cross-references
    "string",  # 8 - String literals
]

TOKEN_MODIFIERS = ["declaration", "definition"]


class AsciiDocSemanticTokensProvider:
    """
    Provides semantic tokens for syntax highlighting.

    Tokenizes AsciiDoc elements for rich editor highlighting.
    Returns data in LSP semantic tokens format (delta-encoded).

    Performance: <100ms for typical documents.
    """

    def __init__(self) -> None:
        """Initialize semantic tokens provider."""
        self._patterns = {
            "heading": re.compile(r"^(=+)\s+(.+)$"),
            "attr_def": re.compile(r"^(:[\w-]+:)\s*(.*)$"),
            "attr_ref": re.compile(r"\{([\w-]+)\}"),
            "block_type": re.compile(r"^\[([^\]]+)\]$"),
            "comment_line": re.compile(r"^//(.*)$"),
            "comment_block": re.compile(r"^(/{4,})$"),
            "macro": re.compile(r"(image|include|link|xref|mailto|kbd|btn|menu)::?"),
            "xref": re.compile(r"<<([^,>]+)(,[^>]*)?>?>"),
            "anchor": re.compile(r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"),
            "bold": re.compile(r"\*([^*]+)\*"),
            "italic": re.compile(r"_([^_]+)_"),
            "mono": re.compile(r"`([^`]+)`"),
        }

    def get_legend(self) -> lsp.SemanticTokensLegend:
        """Get token types and modifiers legend."""
        return lsp.SemanticTokensLegend(
            token_types=TOKEN_TYPES,
            token_modifiers=TOKEN_MODIFIERS,
        )

    def get_tokens(self, text: str) -> lsp.SemanticTokens:
        """
        Get semantic tokens for document.

        Args:
            text: Document text

        Returns:
            SemanticTokens with delta-encoded data
        """
        lines = text.splitlines()
        tokens: list[tuple[int, int, int, int, int]] = []
        in_comment_block = False

        for line_num, line in enumerate(lines):
            # Comment block toggle
            if self._patterns["comment_block"].match(line):
                in_comment_block = not in_comment_block
                tokens.append((line_num, 0, len(line), 4, 0))
                continue

            if in_comment_block:
                tokens.append((line_num, 0, len(line), 4, 0))
                continue

            tokens.extend(self._tokenize_line(line_num, line))

        return self._encode_tokens(tokens)

    def _tokenize_line(
        self,
        line_num: int,
        line: str,
    ) -> list[tuple[int, int, int, int, int]]:
        """Tokenize a single line."""
        tokens: list[tuple[int, int, int, int, int]] = []

        # Heading
        if match := self._patterns["heading"].match(line):
            tokens.append((line_num, 0, len(line), 0, 0))
            return tokens

        # Comment line
        if self._patterns["comment_line"].match(line):
            tokens.append((line_num, 0, len(line), 4, 0))
            return tokens

        # Attribute definition
        if match := self._patterns["attr_def"].match(line):
            tokens.append((line_num, 0, len(match.group(1)), 1, 1))
            return tokens

        # Block type annotation
        if self._patterns["block_type"].match(line):
            tokens.append((line_num, 0, len(line), 3, 0))
            return tokens

        # Inline patterns
        tokens.extend(self._tokenize_inline(line_num, line))
        return tokens

    def _tokenize_inline(
        self,
        line_num: int,
        line: str,
    ) -> list[tuple[int, int, int, int, int]]:
        """Tokenize inline elements."""
        tokens: list[tuple[int, int, int, int, int]] = []

        # Macros
        for match in self._patterns["macro"].finditer(line):
            tokens.append((line_num, match.start(), len(match.group(0)), 5, 0))

        # Cross-references
        for match in self._patterns["xref"].finditer(line):
            tokens.append((line_num, match.start(), match.end() - match.start(), 7, 0))

        # Anchors
        for match in self._patterns["anchor"].finditer(line):
            tokens.append((line_num, match.start(), match.end() - match.start(), 7, 1))

        # Attribute references
        for match in self._patterns["attr_ref"].finditer(line):
            tokens.append((line_num, match.start(), match.end() - match.start(), 2, 0))

        # Formatting (bold, italic, mono)
        for pattern_name in ("bold", "italic", "mono"):
            for match in self._patterns[pattern_name].finditer(line):
                tokens.append((line_num, match.start(), match.end() - match.start(), 6, 0))

        return tokens

    def _encode_tokens(
        self,
        tokens: list[tuple[int, int, int, int, int]],
    ) -> lsp.SemanticTokens:
        """Encode tokens in LSP delta format."""
        tokens.sort(key=lambda t: (t[0], t[1]))

        data: list[int] = []
        prev_line = 0
        prev_char = 0

        for line, char, length, token_type, modifiers in tokens:
            delta_line = line - prev_line
            delta_char = char if delta_line > 0 else char - prev_char

            data.extend([delta_line, delta_char, length, token_type, modifiers])

            prev_line = line
            prev_char = char

        return lsp.SemanticTokens(data=data)
