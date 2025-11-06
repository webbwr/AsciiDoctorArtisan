# Issue #15: Preview Handler Duplication Analysis

**Date:** November 6, 2025
**Status:** Analysis Complete
**Estimated Impact:** Reduce duplication from ~70% to <20%

## Executive Summary

The preview handler classes show **~70% code duplication** in their three core methods:
- `handle_preview_complete()` - **~85% duplicate**
- `sync_editor_to_preview()` - **~75% duplicate**
- `sync_preview_to_editor()` - **~60% duplicate**

Most duplication is boilerplate logic that can be moved to the base class using the **Template Method Pattern**. This will reduce duplication to <20% while maintaining the same public API and test compatibility.

---

## File Statistics

| File | Lines | Purpose |
|------|-------|---------|
| `preview_handler_base.py` | 564 | Abstract base with shared logic |
| `preview_handler.py` | 146 | QTextBrowser (software rendering) |
| `preview_handler_gpu.py` | 306 | QWebEngineView (GPU) + factory functions |
| **Total** | **1,016** | |

**Note:** `preview_handler_gpu.py` is larger due to factory functions (lines 172-306) which are NOT duplicated. The actual handler class is only ~170 lines.

---

## Detailed Duplication Analysis

### 1. `handle_preview_complete()` - 85% Duplicate

**Location:**
- `preview_handler.py:60-86` (27 lines)
- `preview_handler_gpu.py:85-111` (27 lines)

**Common Logic (23/27 lines):**
```python
# Calculate render time (IDENTICAL)
if self._last_render_start is not None:
    render_time = time.time() - self._last_render_start

    # Update adaptive debouncer (IDENTICAL)
    if self._adaptive_debouncer:
        self._adaptive_debouncer.on_render_complete(render_time)

    logger.debug(f"Render completed in {render_time:.3f}s")

# Add CSS styling (IDENTICAL)
styled_html = self._wrap_with_css(html)

# Emit signal (IDENTICAL)
self.preview_updated.emit(html)

logger.debug("Preview updated successfully")  # Minor log message diff
```

**Widget-Specific Logic (4/27 lines):**
```python
# QTextBrowser (preview_handler.py:81)
self.preview.setHtml(styled_html)

# QWebEngineView (preview_handler_gpu.py:106)
self.preview.setHtml(styled_html, QUrl("file://"))
```

**Duplication:** 23/27 = **85% duplicate**

---

### 2. `sync_editor_to_preview()` - 75% Duplicate

**Location:**
- `preview_handler.py:88-116` (29 lines)
- `preview_handler_gpu.py:113-148` (36 lines)

**Common Logic (22/29 lines):**
```python
# Guard checks (IDENTICAL)
if not self.sync_scrolling_enabled or self.is_syncing_scroll:
    return

# Try/finally pattern (IDENTICAL)
self.is_syncing_scroll = True
try:
    # Calculate scroll percentage (IDENTICAL)
    editor_scrollbar = self.editor.verticalScrollBar()
    editor_max = editor_scrollbar.maximum()

    if editor_max > 0:
        scroll_percentage = editor_value / editor_max

        # Widget-specific scrolling here

finally:
    self.is_syncing_scroll = False
```

**Widget-Specific Logic:**
```python
# QTextBrowser (preview_handler.py:109-113) - Direct scrollbar
preview_scrollbar = self.preview.verticalScrollBar()
preview_max = preview_scrollbar.maximum()
preview_value = int(preview_max * scroll_percentage)
preview_scrollbar.setValue(preview_value)

# QWebEngineView (preview_handler_gpu.py:135-145) - JavaScript
js_code = f"""
    var body = document.body;
    var html = document.documentElement;
    var height = Math.max(
        body.scrollHeight, body.offsetHeight,
        html.clientHeight, html.scrollHeight, html.offsetHeight
    );
    var maxScroll = height - window.innerHeight;
    window.scrollTo(0, maxScroll * {scroll_percentage});
"""
self.preview.page().runJavaScript(js_code)
```

**Duplication:** 22/29 = **76% duplicate**

---

### 3. `sync_preview_to_editor()` - 60% Duplicate

**Location:**
- `preview_handler.py:118-146` (29 lines)
- `preview_handler_gpu.py:150-169` (20 lines)

**Common Logic:**
```python
# Guard checks (IDENTICAL)
if not self.sync_scrolling_enabled or self.is_syncing_scroll:
    return

# Try/finally pattern (IDENTICAL)
self.is_syncing_scroll = True
try:
    # Implementation here
finally:
    self.is_syncing_scroll = False
```

**Implementation Difference:**
- QTextBrowser: Full scrollbar-based implementation (18 lines of logic)
- QWebEngineView: Stub with TODO comment (2 lines - not implemented)

**Duplication:** 12/20 = **60% duplicate** (guard/try/finally only)

---

## Consolidation Strategy: Template Method Pattern

### Overview

Move common logic to `PreviewHandlerBase` as **concrete methods** with small **abstract hooks** for widget-specific operations.

### Benefits

1. **DRY Principle:** Eliminate 80%+ of duplicated code
2. **Maintainability:** Fix bugs once, applies to all handlers
3. **Testability:** Test common logic once in base class
4. **Extensibility:** Easy to add new preview widget types
5. **Zero API Changes:** Public API remains identical
6. **Test Compatibility:** All existing tests continue to work

---

## Proposed Refactoring

### Step 1: Move `handle_preview_complete()` to Base Class

**In `preview_handler_base.py`:** (add concrete method)

```python
def handle_preview_complete(self, html: str) -> None:
    """
    Handle completed preview rendering (template method).

    This is a concrete implementation that coordinates common logic
    and delegates widget-specific operations to abstract methods.

    Args:
        html: Rendered HTML content
    """
    # Calculate render time (COMMON)
    if self._last_render_start is not None:
        render_time = time.time() - self._last_render_start

        # Update adaptive debouncer (COMMON)
        if self._adaptive_debouncer:
            self._adaptive_debouncer.on_render_complete(render_time)

        logger.debug(f"Render completed in {render_time:.3f}s")

    # Add CSS styling (COMMON)
    styled_html = self._wrap_with_css(html)

    # Update widget (WIDGET-SPECIFIC - delegate to subclass)
    self._set_preview_html(styled_html)

    # Emit signal (COMMON)
    self.preview_updated.emit(html)

    # Log success (COMMON)
    logger.debug(f"Preview updated successfully ({self.__class__.__name__})")

@abstractmethod
def _set_preview_html(self, html: str) -> None:
    """
    Set HTML in preview widget (widget-specific implementation).

    Args:
        html: Styled HTML content to display
    """
    pass
```

**In `preview_handler.py`:** (implement abstract method)

```python
def _set_preview_html(self, html: str) -> None:
    """Set HTML in QTextBrowser."""
    self.preview.setHtml(html)
```

**In `preview_handler_gpu.py`:** (implement abstract method)

```python
def _set_preview_html(self, html: str) -> None:
    """Set HTML in QWebEngineView with base URL."""
    self.preview.setHtml(html, QUrl("file://"))
```

**Impact:**
- **Before:** 27 lines in each handler (54 total)
- **After:** 1-2 lines in each handler + 18 lines in base (22 total)
- **Reduction:** 54 → 22 = **59% fewer lines**

---

### Step 2: Move `sync_editor_to_preview()` to Base Class

**In `preview_handler_base.py`:** (add concrete method)

```python
def sync_editor_to_preview(self, editor_value: int) -> None:
    """
    Sync preview scroll position to editor (template method).

    Implements common scrolling logic with widget-specific delegation.

    Args:
        editor_value: Editor scroll bar value (0-max)
    """
    # Guard checks (COMMON)
    if not self.sync_scrolling_enabled or self.is_syncing_scroll:
        return

    self.is_syncing_scroll = True
    try:
        # Calculate scroll percentage (COMMON)
        editor_scrollbar = self.editor.verticalScrollBar()
        editor_max = editor_scrollbar.maximum()

        if editor_max > 0:
            scroll_percentage = editor_value / editor_max

            # Apply scroll (WIDGET-SPECIFIC - delegate to subclass)
            self._scroll_preview_to_percentage(scroll_percentage)

    finally:
        self.is_syncing_scroll = False

@abstractmethod
def _scroll_preview_to_percentage(self, percentage: float) -> None:
    """
    Scroll preview widget to percentage (widget-specific implementation).

    Args:
        percentage: Scroll position as percentage (0.0 to 1.0)
    """
    pass
```

**In `preview_handler.py`:** (implement abstract method)

```python
def _scroll_preview_to_percentage(self, percentage: float) -> None:
    """Scroll QTextBrowser to percentage via scrollbar."""
    preview_scrollbar = self.preview.verticalScrollBar()
    preview_max = preview_scrollbar.maximum()
    preview_value = int(preview_max * percentage)
    preview_scrollbar.setValue(preview_value)
```

**In `preview_handler_gpu.py`:** (implement abstract method)

```python
def _scroll_preview_to_percentage(self, percentage: float) -> None:
    """Scroll QWebEngineView to percentage via JavaScript."""
    js_code = f"""
        var body = document.body;
        var html = document.documentElement;
        var height = Math.max(
            body.scrollHeight, body.offsetHeight,
            html.clientHeight, html.scrollHeight, html.offsetHeight
        );
        var maxScroll = height - window.innerHeight;
        window.scrollTo(0, maxScroll * {percentage});
    """
    self.preview.page().runJavaScript(js_code)
```

**Impact:**
- **Before:** 29 lines (QTextBrowser) + 36 lines (QWebEngineView) = 65 total
- **After:** 4 lines + 11 lines in handlers + 16 lines in base = 31 total
- **Reduction:** 65 → 31 = **52% fewer lines**

---

### Step 3: Move `sync_preview_to_editor()` to Base Class

**In `preview_handler_base.py`:** (add concrete method)

```python
def sync_preview_to_editor(self, preview_value: int) -> None:
    """
    Sync editor scroll position to preview (template method).

    Implements common logic with widget-specific scroll retrieval.

    Args:
        preview_value: Preview scroll value (widget-specific units)
    """
    # Guard checks (COMMON)
    if not self.sync_scrolling_enabled or self.is_syncing_scroll:
        return

    self.is_syncing_scroll = True
    try:
        # Get scroll percentage from widget (WIDGET-SPECIFIC)
        scroll_percentage = self._get_preview_scroll_percentage()

        if scroll_percentage is not None:
            # Scroll editor (COMMON)
            editor_scrollbar = self.editor.verticalScrollBar()
            editor_max = editor_scrollbar.maximum()
            editor_value = int(editor_max * scroll_percentage)
            editor_scrollbar.setValue(editor_value)

    finally:
        self.is_syncing_scroll = False

@abstractmethod
def _get_preview_scroll_percentage(self) -> Optional[float]:
    """
    Get current scroll percentage from preview widget.

    Returns:
        Scroll percentage (0.0 to 1.0), or None if not available
    """
    pass
```

**In `preview_handler.py`:** (implement abstract method)

```python
def _get_preview_scroll_percentage(self) -> Optional[float]:
    """Get scroll percentage from QTextBrowser scrollbar."""
    preview_scrollbar = self.preview.verticalScrollBar()
    preview_max = preview_scrollbar.maximum()

    if preview_max > 0:
        preview_value = preview_scrollbar.value()
        return preview_value / preview_max

    return None
```

**In `preview_handler_gpu.py`:** (implement abstract method)

```python
def _get_preview_scroll_percentage(self) -> Optional[float]:
    """
    Get scroll percentage from QWebEngineView (requires JavaScript callback).

    Note: Currently not fully implemented. Would require async JavaScript
    callback to get scroll position from web view.

    Returns:
        None (not implemented - primarily sync editor -> preview)
    """
    # TODO: Implement JavaScript callback to get scroll position
    # self.preview.page().runJavaScript(
    #     "window.scrollY / (document.body.scrollHeight - window.innerHeight)",
    #     lambda result: self._on_scroll_position_received(result)
    # )
    return None
```

**Impact:**
- **Before:** 29 lines (QTextBrowser) + 20 lines (QWebEngineView) = 49 total
- **After:** 8 lines + 10 lines in handlers + 16 lines in base = 34 total
- **Reduction:** 49 → 34 = **31% fewer lines**

---

## Summary of Changes

### Lines of Code Impact

| Method | Before (Total) | After (Total) | Reduction |
|--------|---------------|---------------|-----------|
| `handle_preview_complete()` | 54 | 22 | **59%** ↓ |
| `sync_editor_to_preview()` | 65 | 31 | **52%** ↓ |
| `sync_preview_to_editor()` | 49 | 34 | **31%** ↓ |
| **TOTAL** | **168** | **87** | **48%** ↓ |

### Duplication Percentage

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Code duplication in handlers | **~70%** | **~15%** | **79% improvement** |
| Lines in concrete handlers | 118 | 50 | **58% reduction** |
| Test compatibility | 100% | 100% | **No changes needed** |

---

## Implementation Plan

### Phase 1: Refactor `handle_preview_complete()` (30 min)

1. Add `_set_preview_html()` abstract method to base class
2. Add concrete `handle_preview_complete()` to base class
3. Update `preview_handler.py` to implement `_set_preview_html()`
4. Update `preview_handler_gpu.py` to implement `_set_preview_html()`
5. Remove old `handle_preview_complete()` from both handlers
6. Run tests: `pytest tests/unit/ui/test_preview*.py -v`

### Phase 2: Refactor `sync_editor_to_preview()` (30 min)

1. Add `_scroll_preview_to_percentage()` abstract method to base
2. Add concrete `sync_editor_to_preview()` to base
3. Update both handlers to implement `_scroll_preview_to_percentage()`
4. Remove old `sync_editor_to_preview()` from both handlers
5. Run tests

### Phase 3: Refactor `sync_preview_to_editor()` (30 min)

1. Add `_get_preview_scroll_percentage()` abstract method to base
2. Add concrete `sync_preview_to_editor()` to base
3. Update both handlers to implement `_get_preview_scroll_percentage()`
4. Remove old `sync_preview_to_editor()` from both handlers
5. Run tests

### Phase 4: Validation & Commit (30 min)

1. Run full test suite: `make test`
2. Test manually with GPU and software rendering
3. Update documentation in docstrings
4. Commit with message: `refactor: Reduce preview handler duplication from 70% to <20%`

**Total Estimated Time:** 2 hours

---

## Risk Assessment

### Low Risk ✅

- **Public API unchanged:** All existing code continues to work
- **Test compatibility:** No test changes needed (public methods same)
- **Incremental refactoring:** Can do one method at a time
- **Easy rollback:** Git history preserves old implementation

### Testing Strategy

1. **Unit tests:** Existing preview handler tests cover all methods
2. **Integration tests:** UI integration tests verify rendering
3. **Manual testing:** Test both GPU and software rendering modes
4. **Edge cases:** Empty documents, large documents, theme changes

---

## Benefits

1. **Maintainability:** Fix bugs once in base class, applies to all
2. **Readability:** Intent is clearer - common vs. widget-specific
3. **Extensibility:** Easy to add new preview widget types
4. **DRY:** Eliminates 48% of duplicate code
5. **Performance:** No performance impact (same operations)
6. **Quality:** Reduced code surface area for bugs

---

## Conclusion

This refactoring reduces preview handler duplication from **~70% to <20%** using the Template Method pattern. The changes are low-risk, maintain full backward compatibility, and improve code maintainability significantly.

**Recommendation:** Proceed with implementation in four phases (2 hours total).
