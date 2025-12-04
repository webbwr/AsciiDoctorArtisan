# LSP Enhancement Implementation Plan

**Created:** Dec 4, 2025 | **Status:** Planning | **Priority:** Deferred

---

## Summary

4 LSP enhancements for AsciiDoc Artisan, ordered by priority:

| # | Feature | New File | Lines | Tests |
|---|---------|----------|-------|-------|
| 1 | Quick Fixes | `code_action_provider.py` | ~180 | 10 |
| 2 | Folding Ranges | `folding_provider.py` | ~200 | 13 |
| 3 | Document Formatting | `formatting_provider.py` | ~250 | 12 |
| 4 | Semantic Tokens | `semantic_tokens_provider.py` | ~300 | 15 |

**Total:** ~930 new lines + ~600 test lines + ~60 server.py additions

---

## Feature 1: Quick Fixes (Code Actions)

**LSP Method:** `textDocument/codeAction`

**Purpose:** Auto-fix diagnostics (skeleton exists at `diagnostics_provider.py:147`)

### Files

| Action | File | Changes |
|--------|------|---------|
| Create | `lsp/code_action_provider.py` | ~180 lines |
| Modify | `lsp/diagnostics_provider.py` | Store fixes during conversion |
| Modify | `lsp/server.py` | Register handler, add capability |
| Create | `tests/unit/lsp/test_code_action_provider.py` | 10 tests |

### Implementation

```python
class AsciiDocCodeActionProvider:
    def get_code_actions(self, text, range_, context, uri) -> list[CodeAction]:
        # Convert QuickFix from SyntaxErrorModel.fixes to LSP CodeAction
        pass
```

### Tests
1. `test_convert_single_edit_fix`
2. `test_convert_multi_edit_fix`
3. `test_unclosed_block_fix` (E001)
4. `test_invalid_attribute_fix` (E002)
5. `test_malformed_xref_fix` (E003)
6. `test_trailing_whitespace_fix` (W029)
7. `test_broken_xref_suggestions` (W001)
8. `test_no_fixes_returns_empty`
9. `test_diagnostic_filtering`
10. `test_provider_initialization`

### Acceptance Criteria
- [ ] Code actions appear in editor lightbulb menu
- [ ] Clicking action applies fix correctly
- [ ] Performance: <10ms per request

---

## Feature 2: Folding Ranges

**LSP Method:** `textDocument/foldingRange`

**Purpose:** Collapse sections, blocks, comments in editor

### Files

| Action | File | Changes |
|--------|------|---------|
| Create | `lsp/folding_provider.py` | ~200 lines |
| Modify | `lsp/server.py` | Register handler, add capability |
| Create | `tests/unit/lsp/test_folding_provider.py` | 13 tests |

### Foldable Elements

| Element | Delimiter | Kind |
|---------|-----------|------|
| Sections | `=` headings | Region |
| Source blocks | `----` | Region |
| Example blocks | `====` | Region |
| Sidebar blocks | `****` | Region |
| Quote blocks | `____` | Region |
| Comment blocks | `////` | Comment |
| Passthrough | `++++` | Region |
| Comment lines | `//` (consecutive) | Comment |

### Tests
1. `test_section_folding_single`
2. `test_section_folding_nested`
3. `test_section_folding_same_level`
4. `test_source_block_folding`
5. `test_example_block_folding`
6. `test_sidebar_block_folding`
7. `test_quote_block_folding`
8. `test_comment_block_folding`
9. `test_consecutive_comments`
10. `test_nested_blocks`
11. `test_empty_document`
12. `test_no_foldable_content`
13. `test_provider_initialization`

### Acceptance Criteria
- [ ] Sections collapse to next same/higher level heading
- [ ] All block types fold correctly
- [ ] Comment blocks use `FoldingRangeKind.Comment`
- [ ] Performance: <50ms for 1000-line document

---

## Feature 3: Document Formatting

**LSP Method:** `textDocument/formatting`

**Purpose:** Standardize AsciiDoc formatting

### Files

| Action | File | Changes |
|--------|------|---------|
| Create | `lsp/formatting_provider.py` | ~250 lines |
| Modify | `lsp/server.py` | Register handler, add capability |
| Create | `tests/unit/lsp/test_formatting_provider.py` | 12 tests |

### Formatting Rules
1. Remove trailing whitespace
2. One blank line before headings (not at doc start)
3. Remove multiple consecutive blank lines
4. No blank line after block attributes (`[source]`)

### Tests
1. `test_remove_trailing_whitespace`
2. `test_preserve_no_trailing`
3. `test_heading_spacing_add_blank`
4. `test_heading_spacing_already_blank`
5. `test_heading_spacing_remove_extra`
6. `test_first_line_heading`
7. `test_block_attribute_no_blank`
8. `test_range_formatting`
9. `test_edit_ordering`
10. `test_empty_document`
11. `test_already_formatted`
12. `test_provider_initialization`

### Acceptance Criteria
- [ ] Trailing whitespace removed
- [ ] Consistent heading spacing
- [ ] No data loss
- [ ] Performance: <100ms for 1000-line document

---

## Feature 4: Semantic Tokens

**LSP Method:** `textDocument/semanticTokens/full`

**Purpose:** Syntax highlighting via LSP

### Files

| Action | File | Changes |
|--------|------|---------|
| Create | `lsp/semantic_tokens_provider.py` | ~300 lines |
| Modify | `lsp/server.py` | Register handler, add capability with legend |
| Create | `tests/unit/lsp/test_semantic_tokens_provider.py` | 15 tests |

### Token Types

| Type | Index | Elements |
|------|-------|----------|
| `type` | 0 | Headings |
| `namespace` | 1 | Attribute definitions (`:key:`) |
| `variable` | 2 | Attribute references (`{key}`) |
| `keyword` | 3 | Block annotations (`[source]`) |
| `comment` | 4 | Comments (`//`, `////`) |
| `function` | 5 | Macros (`image::`, `include::`) |
| `decorator` | 6 | Formatting (`*bold*`, `_italic_`) |
| `parameter` | 7 | Cross-references (`<<anchor>>`) |
| `string` | 8 | String literals |

### Tests
1. `test_legend_types`
2. `test_heading_tokens`
3. `test_attribute_definition_tokens`
4. `test_attribute_reference_tokens`
5. `test_block_type_tokens`
6. `test_comment_line_tokens`
7. `test_comment_block_tokens`
8. `test_macro_tokens`
9. `test_xref_tokens`
10. `test_anchor_definition_tokens`
11. `test_bold_italic_mono_tokens`
12. `test_delta_encoding`
13. `test_empty_document`
14. `test_performance_large_doc`
15. `test_provider_initialization`

### Acceptance Criteria
- [ ] All element types tokenized correctly
- [ ] Delta encoding correct
- [ ] Comment blocks toggle state
- [ ] Performance: <100ms for 1000-line document

---

## Server.py Modifications

All features require these changes to `lsp/server.py`:

### Imports
```python
from asciidoc_artisan.lsp.code_action_provider import AsciiDocCodeActionProvider
from asciidoc_artisan.lsp.folding_provider import AsciiDocFoldingProvider
from asciidoc_artisan.lsp.formatting_provider import AsciiDocFormattingProvider
from asciidoc_artisan.lsp.semantic_tokens_provider import AsciiDocSemanticTokensProvider
```

### Provider Init (in `__init__`)
```python
self.code_action_provider = AsciiDocCodeActionProvider()
self.folding_provider = AsciiDocFoldingProvider()
self.formatting_provider = AsciiDocFormattingProvider()
self.semantic_tokens_provider = AsciiDocSemanticTokensProvider()
```

### Handler Registration
```python
self.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)(self._on_code_action)
self.feature(lsp.TEXT_DOCUMENT_FOLDING_RANGE)(self._on_folding_range)
self.feature(lsp.TEXT_DOCUMENT_FORMATTING)(self._on_formatting)
self.feature(lsp.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)(self._on_semantic_tokens)
```

### Capabilities
```python
code_action_provider=lsp.CodeActionOptions(
    code_action_kinds=[lsp.CodeActionKind.QuickFix],
),
folding_range_provider=lsp.FoldingRangeOptions(),
document_formatting_provider=lsp.DocumentFormattingOptions(),
semantic_tokens_provider=lsp.SemanticTokensOptions(
    legend=self.semantic_tokens_provider.get_legend(),
    full=True,
),
```

---

## Implementation Order

```
1. Quick Fixes     [Est: 4-6 hrs]  - Highest user value
2. Folding Ranges  [Est: 4-6 hrs]  - Common IDE expectation
3. Formatting      [Est: 6-8 hrs]  - Document standardization
4. Semantic Tokens [Est: 8-10 hrs] - Rich highlighting
```

**Total Estimate:** 22-30 hours

---

## Dependencies

- pygls (existing)
- lsprotocol (existing)
- `SyntaxErrorModel.fixes` for Quick Fixes
- Heading patterns from `symbols_provider.py` for Folding

---

## Metrics After Implementation

| Metric | Current | After |
|--------|---------|-------|
| LSP Lines | 1,362 | ~2,350 |
| LSP Tests | 54 | ~104 |
| Providers | 5 | 9 |
| LSP Features | 5 | 9 |

---

*Plan created: Dec 4, 2025 | Status: Deferred per ROADMAP.md*
