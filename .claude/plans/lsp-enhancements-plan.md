# LSP Enhancement Plan

**Status:** Deferred | **Est:** 22-30 hrs | **New Lines:** ~930

---

## Features

| # | Feature | LSP Method | File | Lines | Tests |
|---|---------|------------|------|-------|-------|
| 1 | Quick Fixes | `codeAction` | `code_action_provider.py` | ~180 | 10 |
| 2 | Folding | `foldingRange` | `folding_provider.py` | ~200 | 13 |
| 3 | Formatting | `formatting` | `formatting_provider.py` | ~250 | 12 |
| 4 | Semantic Tokens | `semanticTokens/full` | `semantic_tokens_provider.py` | ~300 | 15 |

---

## 1. Quick Fixes

Convert `SyntaxErrorModel.fixes` → LSP `CodeAction`.

**Modify:** `diagnostics_provider.py` (store fixes), `server.py` (handler)

**Acceptance:** Lightbulb menu, <10ms, fixes E001-E003/W001/W029

---

## 2. Folding Ranges

Collapse sections, blocks, comments.

**Foldable:** `=` headings, `----/====/****/____/////++++` blocks, `//` comments

**Acceptance:** Hierarchy correct, <50ms/1K lines

---

## 3. Document Formatting

Standardize: trailing whitespace, heading spacing, block attributes.

**Rules:**
- Remove trailing whitespace
- One blank before headings
- No blank after `[source]`

**Acceptance:** No data loss, <100ms/1K lines

---

## 4. Semantic Tokens

Syntax highlighting via LSP.

**Token Types:** type(headings), namespace(`:attr:`), variable(`{ref}`), keyword(`[block]`), comment, function(macros), decorator(formatting), parameter(xrefs)

**Acceptance:** Delta encoding, <100ms/1K lines

---

## Server.py Changes

```python
# Imports
from .code_action_provider import AsciiDocCodeActionProvider
from .folding_provider import AsciiDocFoldingProvider
from .formatting_provider import AsciiDocFormattingProvider
from .semantic_tokens_provider import AsciiDocSemanticTokensProvider

# Init
self.code_action_provider = AsciiDocCodeActionProvider()
self.folding_provider = AsciiDocFoldingProvider()
self.formatting_provider = AsciiDocFormattingProvider()
self.semantic_tokens_provider = AsciiDocSemanticTokensProvider()

# Handlers
self.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)(self._on_code_action)
self.feature(lsp.TEXT_DOCUMENT_FOLDING_RANGE)(self._on_folding_range)
self.feature(lsp.TEXT_DOCUMENT_FORMATTING)(self._on_formatting)
self.feature(lsp.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)(self._on_semantic_tokens)
```

---

## Metrics After

| Metric | Current | After |
|--------|---------|-------|
| LSP Lines | 1,362 | ~2,350 |
| LSP Tests | 54 | ~104 |
| Providers | 5 | 9 |

---

*Dec 4, 2025 | Deferred per ROADMAP.md*
