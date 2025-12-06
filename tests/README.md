# Tests

**v2.1.0** | 5,628 unit + 17 E2E + 17 integration tests

## Structure

```
tests/
├── conftest.py      # Shared fixtures
├── unit/            # Unit tests
│   ├── core/        # Core module tests
│   ├── ui/          # UI component tests
│   └── workers/     # Worker thread tests
├── e2e/             # End-to-end tests (BDD)
├── integration/     # Integration tests
└── performance/     # Benchmarks
```

## Run Tests

```bash
make test                    # All tests + coverage
pytest tests/unit/           # Unit tests only
pytest tests/e2e/            # E2E tests only
pytest tests/unit/core/      # Specific module
pytest -v tests/file.py      # Single file
```

## Coverage

```bash
make test                    # Generates htmlcov/
open htmlcov/index.html      # View report
```

**Current:** 98% coverage

## Writing Tests

```python
def test_feature_name():
    # Arrange
    expected = "result"

    # Act
    actual = function_under_test()

    # Assert
    assert actual == expected
```

## Markers

- `@pytest.mark.requires_gpu` - Needs GPU hardware
- `@pytest.mark.live_api` - Needs Ollama running

---

*See [docs/developer/testing.md](../docs/developer/testing.md) for full guide*
