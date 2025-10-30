# Tests Directory

This directory contains all test files for AsciiDoc Artisan.

## Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests (test individual components)
│   ├── core/               # Tests for core/ modules
│   ├── ui/                 # Tests for UI components
│   └── workers/            # Tests for worker threads
├── integration/            # Integration tests (test component interactions)
└── performance/            # Performance benchmarks and profiling
```

## Test Categories

### Unit Tests (`unit/`)
Test individual components in isolation.

- **core/**: Core functionality tests (file operations, LRU cache, resource monitoring, etc.)
- **ui/**: UI component tests (dialogs, managers, handlers)
- **workers/**: Worker thread tests (Git, Pandoc, preview rendering)

### Integration Tests (`integration/`)
Test how components work together.

Examples:
- `test_async_integration.py` - Async file operations integration
- `test_memory_leaks.py` - Memory leak detection
- `test_ui_integration.py` - Full UI workflow tests

### Performance Tests (`performance/`)
Benchmark performance and profile resource usage.

Examples:
- `test_performance_baseline.py` - Performance regression detection
- `test_virtual_scroll_benchmark.py` - Virtual scrolling performance
- `profile_*.py` - Profiling scripts

## Running Tests

### Run All Tests
```bash
make test
# or
pytest tests/
```

### Run Specific Category
```bash
pytest tests/unit/                  # All unit tests
pytest tests/unit/core/             # Core module tests only
pytest tests/integration/           # Integration tests only
pytest tests/performance/           # Performance tests only
```

### Run Individual Test File
```bash
pytest tests/unit/core/test_file_operations.py -v
```

### Run With Coverage
```bash
pytest tests/ --cov=asciidoc_artisan --cov-report=html
# Open htmlcov/index.html in browser
```

## Writing New Tests

### File Naming
- Unit test: `test_<module_name>.py`
- Integration test: `test_<feature>_integration.py`
- Performance test: `test_<feature>_benchmark.py` or `profile_<feature>.py`

### Test Structure
```python
import pytest

class TestFeatureName:
    """Test suite for FeatureName."""

    def test_basic_functionality(self):
        """Test basic feature functionality."""
        # Arrange
        expected = "result"

        # Act
        actual = function_under_test()

        # Assert
        assert actual == expected
```

### Using Fixtures
Shared fixtures are in `conftest.py`:
```python
def test_with_temp_file(tmp_path):
    """Test using temporary file (tmp_path fixture from pytest)."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

## Coverage Goals

**Target**: 100% coverage for critical modules

**Current Coverage**:
- `core/file_operations.py`: 100%
- `core/lru_cache.py`: 100%
- `core/resource_monitor.py`: 100%
- `core/constants.py`: 100%
- `core/async_file_ops.py`: 100%
- `core/async_file_handler.py`: 91%
- `core/async_file_watcher.py`: 98%

Run `make test` to see full coverage report.
