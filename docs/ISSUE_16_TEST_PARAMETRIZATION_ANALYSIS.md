# Issue #16: Test Parametrization Analysis

**Date:** November 6, 2025
**Status:** Analysis Complete
**Estimated Implementation:** 3-5 days for high-priority items

---

## Executive Summary

The test suite contains numerous opportunities for parametrization using `@pytest.mark.parametrize`. Converting duplicate test patterns to parametrized versions will:
- **Reduce test code by ~30-40%** (estimated 200-300 lines)
- **Improve maintainability** (single test covers multiple cases)
- **Enhance readability** (test data clearly separated from test logic)
- **Maintain 100% coverage** (no loss of test effectiveness)

**Current State:**
- 621+ total tests across 74 test files
- Only 18 tests currently use `@pytest.mark.parametrize`
- Significant duplication in edge case and boundary value tests

---

## High-Priority Parametrization Opportunities

### 1. Scroll Edge Case Tests (Preview Handlers)

**Location:** `tests/unit/ui/test_preview_handler.py`

**Current Pattern (4 separate tests):**
```python
def test_handles_negative_scroll_value(self, ...):
    handler.sync_editor_to_preview(-10)
    # assert behavior

def test_handles_scroll_value_exceeding_maximum(self, ...):
    handler.sync_editor_to_preview(9999)
    # assert behavior

def test_handles_very_large_scroll_values(self, ...):
    handler.sync_editor_to_preview(10**6)
    # assert behavior

def test_handles_zero_scroll_value(self, ...):
    handler.sync_editor_to_preview(0)
    # assert behavior
```

**Parametrized Version (1 test):**
```python
@pytest.mark.parametrize("scroll_value,description", [
    (-10, "negative"),
    (9999, "exceeding maximum"),
    (10**6, "very large"),
    (0, "zero"),
])
def test_handles_scroll_edge_cases(self, mock_editor, mock_preview,
                                    mock_parent_window, scroll_value, description):
    """Test scroll synchronization with edge case values."""
    handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

    # Should not crash
    handler.sync_editor_to_preview(scroll_value)

    # Verify behavior based on value type
    if scroll_value < 0:
        # Assert negative handling
    elif scroll_value > preview_max:
        # Assert max clamping
    # ... etc
```

**Impact:** 4 tests → 1 parametrized test (75% reduction)

---

### 2. CSS/HTML Edge Cases

**Location:** `tests/unit/ui/test_preview_handler.py`

**Current Pattern (3+ separate tests):**
```python
def test_handles_empty_html_in_css_wrapping(self, ...):
    html = ""
    result = handler._wrap_with_css(html)
    assert "<html>" in result

def test_handles_html_with_existing_style_tags(self, ...):
    html = "<style>existing</style><p>content</p>"
    result = handler._wrap_with_css(html)
    # assertions

def test_handles_null_html_gracefully(self, ...):
    html = None
    # test handling
```

**Parametrized Version:**
```python
@pytest.mark.parametrize("html,expected_contains,description", [
    ("", "<html>", "empty string"),
    ("<style>existing</style><p>content</p>", "<style>", "existing style tags"),
    (None, "", "null value"),
    ("<script>alert('xss')</script>", "Content-Security-Policy", "XSS attempt"),
    ("a" * 10000, "body", "very large content"),
])
def test_css_wrapping_edge_cases(self, mock_editor, mock_preview,
                                 mock_parent_window, html, expected_contains, description):
    """Test CSS wrapping with various HTML inputs."""
    handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

    if html is None:
        with pytest.raises(TypeError):
            handler._wrap_with_css(html)
    else:
        result = handler._wrap_with_css(html)
        assert expected_contains in result
```

**Impact:** 3-5 tests → 1 parametrized test (60-80% reduction)

---

### 3. Adaptive Debouncer Config Tests

**Location:** `tests/unit/core/test_adaptive_debouncer.py`

**Current Pattern (multiple config tests):**
```python
def test_custom_config(self):
    config = DebounceConfig(min_delay=100, max_delay=2000)
    # test

def test_default_config(self):
    config = DebounceConfig()
    # test same logic with different values

def test_config_validation(self):
    with pytest.raises(ValueError):
        DebounceConfig(min_delay=-1)
```

**Parametrized Version:**
```python
@pytest.mark.parametrize("min_delay,max_delay,should_raise,description", [
    (100, 2000, False, "custom valid"),
    (200, 1000, False, "default values"),
    (-1, 1000, True, "negative min_delay"),
    (1000, 100, True, "min > max"),
    (0, 5000, False, "zero min_delay"),
])
def test_debounce_config(self, min_delay, max_delay, should_raise, description):
    """Test DebounceConfig with various parameter combinations."""
    if should_raise:
        with pytest.raises(ValueError):
            DebounceConfig(min_delay=min_delay, max_delay=max_delay)
    else:
        config = DebounceConfig(min_delay=min_delay, max_delay=max_delay)
        assert config.min_delay == min_delay
        assert config.max_delay == max_delay
```

**Impact:** 3-5 tests → 1 parametrized test

---

### 4. Ollama Chat Context Modes

**Location:** `tests/test_ollama_chat_worker.py`, `tests/test_chat_bar_widget.py`

**Current Pattern:**
```python
def test_document_mode(self):
    worker.send_message(..., context_mode="document", ...)
    # assertions

def test_syntax_mode(self):
    worker.send_message(..., context_mode="syntax", ...)
    # assertions

def test_general_mode(self):
    worker.send_message(..., context_mode="general", ...)
    # assertions

def test_editing_mode(self):
    worker.send_message(..., context_mode="editing", ...)
    # assertions
```

**Parametrized Version:**
```python
@pytest.mark.parametrize("context_mode,expected_system_prompt_contains", [
    ("document", "working on the document"),
    ("syntax", "AsciiDoc syntax"),
    ("general", "helpful AI assistant"),
    ("editing", "improve document quality"),
])
def test_context_modes(self, qtbot, context_mode, expected_system_prompt_contains):
    """Test Ollama worker with all context modes."""
    worker = OllamaChatWorker()
    worker.send_message(
        message="test question",
        model="qwen2.5-coder:7b",
        context_mode=context_mode,
        history=[],
        document_content="test doc"
    )

    # Verify system prompt contains expected text
    # (implementation-specific assertions)
```

**Impact:** 4 tests → 1 parametrized test (75% reduction)

---

### 5. Git Result Status Tests

**Location:** `tests/unit/workers/test_git_worker.py`

**Current Pattern:**
```python
def test_success_result(self):
    result = GitResult(success=True, output="OK", error="")
    # assertions

def test_failure_result(self):
    result = GitResult(success=False, output="", error="Failed")
    # assertions

def test_result_with_command(self):
    result = GitResult(success=True, output="OK", error="", command="git status")
    # assertions
```

**Parametrized Version:**
```python
@pytest.mark.parametrize("success,output,error,command,expected_str", [
    (True, "OK", "", None, "Success: OK"),
    (False, "", "Failed", None, "Error: Failed"),
    (True, "OK", "", "git status", "git status"),
    (False, "", "Not found", "git pull", "git pull failed"),
])
def test_git_result_variations(self, success, output, error, command, expected_str):
    """Test GitResult with various combinations."""
    result = GitResult(
        success=success,
        output=output,
        error=error,
        command=command
    )

    assert result.success == success
    assert result.output == output
    assert result.error == error
    assert result.command == command
    assert expected_str in str(result)
```

**Impact:** 3-4 tests → 1 parametrized test

---

## Medium-Priority Opportunities

### 6. Document Size Edge Cases (Adaptive Debouncer)

**Files:**
- `tests/unit/core/test_adaptive_debouncer.py`
- `tests/unit/ui/test_preview_handler_base.py`

**Pattern:** Tests with different document sizes (< 10KB, 10-100KB, > 100KB, > 1MB)

**Parametrization:**
```python
@pytest.mark.parametrize("doc_size,expected_delay_range", [
    (5_000, (100, 300)),      # < 10KB: fast
    (50_000, (250, 500)),     # 10-100KB: medium
    (500_000, (500, 1000)),   # > 100KB: slow
    (2_000_000, (800, 1500)), # > 1MB: very slow
])
def test_document_size_delays(self, doc_size, expected_delay_range):
    ...
```

**Impact:** 4-6 tests → 1 parametrized test

---

### 7. File Format Conversion Tests

**Location:** `tests/unit/workers/test_pandoc_worker.py`

**Pattern:** Tests for each format conversion (adoc→md, md→docx, adoc→html, etc.)

**Parametrization:**
```python
@pytest.mark.parametrize("source_format,target_format,expected_result", [
    ("adoc", "md", "# Heading"),
    ("md", "docx", "Document"),
    ("adoc", "html", "<h1>"),
    ("adoc", "pdf", "%PDF"),
])
def test_format_conversions(self, source_format, target_format, expected_result):
    ...
```

**Impact:** 8-12 tests → 1-2 parametrized tests

---

### 8. Theme Manager CSS Generation

**Location:** `tests/unit/ui/test_theme_manager.py`

**Pattern:** Tests for dark/light mode CSS generation

**Parametrization:**
```python
@pytest.mark.parametrize("dark_mode,expected_bg,expected_text", [
    (True, "#1a1a1a", "#e0e0e0"),
    (False, "#ffffff", "#000000"),
])
def test_css_generation(self, dark_mode, expected_bg, expected_text):
    ...
```

**Impact:** 2 tests → 1 parametrized test

---

## Low-Priority Opportunities

### 9. Import/Creation Tests

**Pattern:** Every test file has `test_import` and `test_creation` methods

**Note:** These are often unique to each module, so parametrization may not provide significant benefit. However, for modules with similar initialization patterns, fixture-based parametrization could reduce boilerplate.

---

## Implementation Strategy

### Phase 1: High-Priority Items (2 days)
1. Scroll edge cases (preview handlers)
2. CSS/HTML edge cases
3. Ollama context modes
4. Git result variations

**Expected Impact:** ~40-50 lines reduced, 15-20 tests consolidated

### Phase 2: Medium-Priority Items (2 days)
1. Document size variations
2. Format conversion tests
3. Theme CSS generation

**Expected Impact:** ~60-80 lines reduced, 20-30 tests consolidated

### Phase 3: Review & Refine (1 day)
1. Run full test suite verification
2. Update test documentation
3. Identify remaining opportunities
4. Create parametrization guidelines document

---

## Benefits of Parametrization

### Code Maintainability
**Before:**
```python
def test_format_adoc_to_md(self):
    result = convert("adoc", "md", "= Heading")
    assert "# Heading" in result

def test_format_adoc_to_html(self):
    result = convert("adoc", "html", "= Heading")
    assert "<h1>" in result

def test_format_adoc_to_docx(self):
    result = convert("adoc", "docx", "= Heading")
    assert is_valid_docx(result)
```

**After:**
```python
@pytest.mark.parametrize("source,target,input_text,expected", [
    ("adoc", "md", "= Heading", "# Heading"),
    ("adoc", "html", "= Heading", "<h1>"),
    ("adoc", "docx", "= Heading", lambda r: is_valid_docx(r)),
])
def test_format_conversion(self, source, target, input_text, expected):
    result = convert(source, target, input_text)
    if callable(expected):
        assert expected(result)
    else:
        assert expected in result
```

### Benefits:
1. **Single point of modification** - Add new format tests by adding one line
2. **Clear test matrix** - All test cases visible in parameter list
3. **Consistent structure** - Same test logic applied uniformly
4. **Easy debugging** - pytest shows which parameter combo failed

---

## Risks & Mitigation

### Risk 1: Over-Parametrization
**Problem:** Parametrizing tests that are fundamentally different makes them harder to understand.

**Mitigation:**
- Only parametrize tests that share >80% of their logic
- Keep parameter lists short (<10 cases)
- Use descriptive parameter names

### Risk 2: Loss of Test Clarity
**Problem:** Parametrized tests can be harder to understand than separate tests.

**Mitigation:**
- Add detailed docstrings explaining parameter meanings
- Use descriptive IDs: `pytest.param(..., id="negative_scroll")`
- Group related test cases together

### Risk 3: Test Coverage Gaps
**Problem:** Converting multiple tests to one parametrized test might miss edge cases.

**Mitigation:**
- Run coverage analysis before and after
- Verify same assertions are made for all parameters
- Add extra parameter combinations to increase coverage

---

## Parametrization Best Practices

### 1. Use Descriptive IDs
```python
@pytest.mark.parametrize("value", [
    pytest.param(-10, id="negative"),
    pytest.param(0, id="zero"),
    pytest.param(9999, id="exceeding_max"),
])
```

### 2. Keep Parameters Focused
**Bad:**
```python
@pytest.mark.parametrize("a,b,c,d,e,f,g,h,i,j", [...])  # Too many!
```

**Good:**
```python
@pytest.mark.parametrize("scroll_value,expected_behavior", [...])
```

### 3. Document Complex Parameters
```python
@pytest.mark.parametrize("config,expected", [
    # (min_delay, max_delay, target_fps) -> expected_delay
    ((100, 1000, 60), 200),
    ((200, 2000, 30), 400),
])
def test_adaptive_calculation(self, config, expected):
    """Test adaptive delay calculation with various configs.

    Parameters:
        config: Tuple of (min_delay, max_delay, target_fps)
        expected: Expected calculated delay in milliseconds
    """
    ...
```

### 4. Use Fixtures with Parametrize
```python
@pytest.fixture(params=["dark", "light"])
def theme_mode(request):
    return request.param

def test_css_generation(self, theme_mode):
    """Test CSS generation for all themes (parametrized via fixture)."""
    ...
```

---

## Estimated Impact Summary

| Category | Tests Before | Tests After | Lines Saved | Time Saved (Running) |
|----------|--------------|-------------|-------------|----------------------|
| High Priority | 25-30 | 5-6 | ~80 lines | ~2-3 seconds |
| Medium Priority | 30-40 | 8-10 | ~100 lines | ~3-5 seconds |
| Low Priority | 50+ | 30-40 | ~60 lines | ~1-2 seconds |
| **TOTAL** | **105-120** | **43-56** | **~240 lines** | **~6-10 seconds** |

**Overall Reduction:** ~47% fewer test functions, ~30% fewer lines

---

## Conclusion

Test parametrization offers significant benefits with minimal risk. The high-priority items alone would reduce test code by 15-20% while maintaining full coverage. Implementation should proceed incrementally with thorough verification at each phase.

**Recommendation:** Proceed with Phase 1 (high-priority items) first, evaluate results, then continue with Phase 2.
