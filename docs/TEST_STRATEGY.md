# Test Strategy: Total Coverage with Bug-Finding Focus

## Principal Goal: Bug and Issue-Free Code

Tests exist to **FIND BUGS**, not to pass. A passing test suite with bugs in production is a failure of our testing strategy.

## Key Principles

### 1. COVERAGE: Every Line, Every Path
- **Target**: 95%+ line coverage, 90% branch coverage
- **Enforcement**: Tests fail if coverage drops below 90%
- Every line of code is a potential bug source
- Uncovered code is untested code is buggy code

### 2. FIND BUGS: Active Bug Hunting
- Tests should actively seek bugs, not just verify happy paths
- Use property-based testing (Hypothesis) with 500+ examples
- Use edge case fixtures for boundary testing
- Use fuzzing for randomized input testing

### 3. FAIL LOUDLY: No Silent Failures
- Warnings are treated as errors
- Strict xfail mode (xfail tests MUST fail)
- Detailed tracebacks with local variables
- Empty parameter sets fail immediately

### 4. EDGE CASES: Test the Boundaries
- Empty strings, null bytes, unicode edge cases
- Integer overflow, float precision, NaN handling
- Very long inputs, very short inputs
- Special characters, injection attempts

### 5. SECURITY FIRST: Critical Tests Run First
- Security tests are automatically ordered first
- Fail fast on critical security issues
- Path traversal, injection, and validation tests are mandatory

## Available Test Fixtures

### Edge Case Testing

```python
def test_handles_edge_cases(edge_case_strings):
    """Test with pre-defined problematic strings."""
    for name, value in edge_case_strings.items():
        result = my_function(value)
        assert result is not None, f"Failed on {name}"
```

### Memory Tracking

```python
def test_no_memory_leak(memory_tracker):
    """Verify function doesn't leak memory."""
    memory_tracker.start()
    for _ in range(1000):
        my_function()
    peak_mb = memory_tracker.stop()
    assert peak_mb < 100, f"Memory leak: {peak_mb}MB used"
```

### Random Fuzzing

```python
def test_random_inputs(random_fuzzer):
    """Fuzz test with random data."""
    for _ in range(100):
        random_string = random_fuzzer.string(max_length=1000)
        result = my_function(random_string)
        assert result is not None  # Invariant check
```

### Strict Mocking

```python
def test_api_usage(strict_mock):
    """Catch typos and API misuse."""
    api = strict_mock(["allowed_method"])
    api.allowed_method()  # OK
    api.typo_method()  # Raises AttributeError
```

### UI Event Simulation

```python
def test_button_click(ui_event_simulator, my_widget):
    """Test UI interactions."""
    ui_event_simulator.click(my_widget.button)
    assert my_widget.was_clicked
```

### No Exception Assertion

```python
def test_no_crash(assert_no_exception):
    """Ensure function never raises."""
    with assert_no_exception():
        risky_function()
```

## Coverage Configuration

```ini
[coverage:run]
branch = true
source = src/asciidoc_artisan

[coverage:report]
show_missing = true
precision = 2
fail_under = 90
```

## Running Tests

### Full Test Suite (Default)
```bash
make test
```

### Quick Tests (CI Mode)
```bash
HYPOTHESIS_PROFILE=quick pytest tests/
```

### Coverage Report
```bash
pytest --cov-report=html tests/
open coverage_html/index.html
```

### Security Tests Only
```bash
pytest -m security tests/
```

### Performance Tests Only
```bash
pytest -m performance tests/
```

## Test Categories

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Unit tests - single function/method |
| `@pytest.mark.integration` | Integration tests - component interactions |
| `@pytest.mark.e2e` | End-to-end tests - full workflows |
| `@pytest.mark.security` | Security tests - CRITICAL |
| `@pytest.mark.performance` | Performance benchmarks |
| `@pytest.mark.property` | Property-based tests (Hypothesis) |
| `@pytest.mark.edge_case` | Boundary condition tests |

## Test Organization

```
tests/
├── unit/           # Unit tests by module
│   ├── core/       # Core module tests
│   ├── ui/         # UI component tests
│   └── workers/    # Worker tests
├── integration/    # Integration tests
├── e2e/            # End-to-end tests
└── conftest.py     # Shared fixtures
```

## Writing New Tests

### DO: Write Bug-Finding Tests
```python
def test_handles_malicious_input():
    """Verify function doesn't crash on injection attempt."""
    malicious = "'; DROP TABLE users; --"
    result = sanitize_input(malicious)
    assert "DROP" not in result
```

### DON'T: Write Trivial Tests
```python
# BAD: This test doesn't find bugs
def test_function_exists():
    assert my_function is not None
```

### DO: Test Error Paths
```python
def test_handles_file_not_found():
    """Verify graceful handling of missing file."""
    with pytest.raises(FileNotFoundError):
        load_file("/nonexistent/path")
```

### DO: Use Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_roundtrip(text):
    """Verify encode/decode roundtrip."""
    assert decode(encode(text)) == text
```

## Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Line Coverage | 95%+ | ~95% |
| Branch Coverage | 90%+ | ~90% |
| Test Count | 5,000+ | 5,645 |
| Hypothesis Examples | 500/test | 500 |

## Philosophy

> "A test that always passes is not testing anything."

Tests must:
1. Be capable of failing when bugs exist
2. Actually exercise the code path
3. Verify correct behavior, not just "no crash"
4. Cover edge cases and error conditions
5. Be fast enough to run frequently
