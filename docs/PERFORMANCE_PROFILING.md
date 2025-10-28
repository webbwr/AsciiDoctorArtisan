# Performance Profiling Guide

**AsciiDoc Artisan v1.5.0+**

This document explains how to use the performance profiling features built into the test suite.

## Overview

The test suite includes automatic performance tracking for all tests. This helps identify:

- Slow tests that need optimization
- Memory leaks
- Performance regressions
- CPU-intensive operations

## Automatic Performance Tracking

Every test is automatically profiled. No additional code needed!

The test suite tracks:
- **Execution time** - How long each test takes
- **Memory usage** - Memory before and after each test
- **CPU usage** - CPU consumption during test execution

## Running Tests with Performance Profiling

### Basic Usage

```bash
# Run all tests with performance summary
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage and performance
pytest tests/ --cov=src/asciidoc_artisan --cov-report=html -v
```

### Performance Summary

After tests complete, you'll see a performance summary:

```
================== Performance Summary ==================

Slowest 10 Tests:
  2.145s - tests/test_main_window.py::test_full_workflow
  1.823s - tests/test_preview_worker.py::test_large_document
  0.956s - tests/test_git_worker.py::test_git_operations
  ...

Highest Memory Usage (Top 10):
  +45.23MB - tests/test_main_window.py::test_full_workflow
  +12.67MB - tests/test_preview_worker.py::test_large_document
  -2.34MB - tests/test_lru_cache.py::test_cache_cleanup
  ...

Overall Statistics:
  Total tests: 481
  Total time: 125.34s
  Average time: 0.260s
  Peak memory: 512.45MB
```

## Performance Benchmarking

### Custom Benchmarks

Create benchmark tests using the `@pytest.mark.benchmark` marker:

```python
import pytest
import time

@pytest.mark.benchmark
def test_rendering_performance(sample_asciidoc):
    """Benchmark document rendering."""
    from asciidoc_artisan.workers.preview_worker import PreviewWorker

    worker = PreviewWorker()
    start = time.time()

    # Render document
    result = worker.render(sample_asciidoc)

    duration = time.time() - start

    # Assert performance target
    assert duration < 1.0, f"Rendering took {duration:.2f}s (target: <1.0s)"
```

### Running Only Benchmarks

```bash
# Run only benchmark tests
pytest tests/ -m benchmark -v

# Run benchmarks with detailed output
pytest tests/performance/ -v --tb=short
```

## Memory Profiling

### Detecting Memory Leaks

The performance tracker automatically detects memory increases. Large positive deltas may indicate leaks:

```python
def test_no_memory_leak():
    """Test that repeated operations don't leak memory."""
    from asciidoc_artisan.core.lru_cache import LRUCache

    cache = LRUCache(max_size=100)

    # Perform many operations
    for i in range(10000):
        cache.put(f"key_{i}", f"value_{i}")

    # Memory delta should be reasonable
    # Auto-tracked by performance_tracker fixture
```

### Manual Memory Profiling

For detailed memory profiling, use the memory profiler:

```python
from asciidoc_artisan.core.memory_profiler import MemoryProfiler

def test_with_memory_profiling():
    profiler = MemoryProfiler()

    profiler.start("operation_name")
    # ... perform operation ...
    profiler.stop("operation_name")

    report = profiler.generate_report()
    print(report)
```

## CPU Profiling

### Identifying CPU Hotspots

Use Python's built-in cProfile for detailed CPU profiling:

```bash
# Profile a specific test
python -m cProfile -o profile.stats -m pytest tests/test_incremental_renderer.py

# Analyze results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

### In-Test CPU Tracking

```python
import psutil
import os

def test_cpu_usage():
    process = psutil.Process(os.getpid())

    cpu_before = process.cpu_percent()

    # ... perform operation ...

    cpu_after = process.cpu_percent()

    # Ensure CPU usage is reasonable
    assert cpu_after < 80.0, f"High CPU usage: {cpu_after}%"
```

## Performance Regression Testing

### Setting Performance Baselines

Create baseline performance tests:

```python
import pytest

@pytest.mark.performance
def test_startup_time():
    """Test that application startup is under 2 seconds."""
    import time
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

    start = time.time()
    window = AsciiDocEditor()
    duration = time.time() - start

    # v1.5.0 target: 1.5s
    assert duration < 2.0, f"Startup took {duration:.2f}s"
```

### Continuous Monitoring

Run performance tests in CI/CD:

```bash
# Run performance tests only
pytest tests/ -m performance -v

# Fail if any test is too slow
pytest tests/ -v --durations=0 --maxfail=1
```

## Common Performance Issues

### Slow Tests

**Symptoms:** Tests taking >5 seconds

**Solutions:**
- Mock external dependencies (files, network, subprocesses)
- Use smaller test data
- Disable GUI rendering with `QT_QPA_PLATFORM=offscreen`

### Memory Leaks

**Symptoms:** Large positive memory deltas

**Solutions:**
- Clean up resources in teardown
- Use context managers
- Clear caches after tests

### High CPU Usage

**Symptoms:** Tests using >50% CPU

**Solutions:**
- Reduce iteration counts
- Use mocks instead of real operations
- Profile and optimize hot paths

## Performance Fixtures

### Custom Performance Fixtures

```python
# In conftest.py or test file
import pytest
import time

@pytest.fixture
def performance_timer():
    """Fixture to measure operation performance."""
    timings = {}

    class Timer:
        def measure(self, name, func):
            start = time.time()
            result = func()
            duration = time.time() - start
            timings[name] = duration
            return result

        def get_timings(self):
            return timings

    return Timer()

# Usage in test
def test_with_timer(performance_timer):
    result = performance_timer.measure("render", lambda: render_document())

    timings = performance_timer.get_timings()
    assert timings["render"] < 1.0
```

## Profiling Tools

### Recommended Tools

1. **pytest-benchmark** - Benchmark plugin for pytest
   ```bash
   pip install pytest-benchmark
   pytest tests/ --benchmark-only
   ```

2. **memory_profiler** - Line-by-line memory profiling
   ```bash
   pip install memory_profiler
   python -m memory_profiler script.py
   ```

3. **py-spy** - Sampling profiler
   ```bash
   pip install py-spy
   py-spy record -o profile.svg -- pytest tests/
   ```

4. **scalene** - CPU+GPU+memory profiler
   ```bash
   pip install scalene
   scalene pytest tests/
   ```

## Performance Metrics

### Key Metrics

| Metric | Target | Current (v1.5.0) |
|--------|--------|------------------|
| Startup Time | <1.5s | 1.05s ✅ |
| Preview Render (small doc) | <200ms | ~150ms ✅ |
| Preview Render (large doc) | <1.0s | ~800ms ✅ |
| Memory Usage (idle) | <200MB | ~150MB ✅ |
| Test Suite Runtime | <180s | ~125s ✅ |

### Tracking Trends

Keep historical performance data:

```bash
# Save performance metrics
pytest tests/ -v 2>&1 | tee performance-$(date +%Y%m%d).log

# Compare with baseline
diff performance-baseline.log performance-$(date +%Y%m%d).log
```

## Best Practices

1. **Always run tests with offscreen platform**
   ```bash
   QT_QPA_PLATFORM=offscreen pytest tests/ -v
   ```

2. **Use fixtures for expensive setup**
   ```python
   @pytest.fixture(scope="session")
   def expensive_resource():
       # Created once per test session
       return create_resource()
   ```

3. **Mock slow operations**
   ```python
   @patch("subprocess.run")
   def test_fast(mock_run):
       mock_run.return_value = Mock(returncode=0)
       # Test runs instantly
   ```

4. **Profile before optimizing**
   ```bash
   # Identify the actual bottleneck first
   pytest tests/test_slow.py -v --durations=10
   ```

5. **Set performance budgets**
   ```python
   MAX_RENDER_TIME = 1.0  # seconds

   assert duration < MAX_RENDER_TIME
   ```

## Reporting

### Generating Reports

```bash
# HTML coverage report with performance
pytest tests/ --cov=src/asciidoc_artisan --cov-report=html -v

# JSON output for CI/CD
pytest tests/ --json-report --json-report-file=report.json

# JUnit XML for integration
pytest tests/ --junitxml=junit.xml
```

### Analyzing Reports

```python
import json

with open("report.json") as f:
    data = json.load(f)

# Extract slow tests
slow_tests = [
    test for test in data["tests"]
    if test["duration"] > 1.0
]

print(f"Found {len(slow_tests)} slow tests")
```

## Continuous Improvement

### Performance Optimization Workflow

1. **Measure** - Run tests with profiling
2. **Identify** - Find slowest tests/functions
3. **Analyze** - Profile the slow code
4. **Optimize** - Implement improvements
5. **Verify** - Re-run tests to confirm
6. **Document** - Update performance targets

### Performance Review Checklist

- [ ] All tests complete in <180 seconds
- [ ] No test takes >5 seconds
- [ ] No memory leaks detected (negative deltas only)
- [ ] CPU usage stays <50% during tests
- [ ] Performance metrics documented
- [ ] Baselines updated for new features

## Troubleshooting

### Tests Timing Out

**Problem:** Tests hang or timeout

**Solution:**
```bash
# Add timeout to prevent hangs
pytest tests/ -v --timeout=30
```

### Inconsistent Performance

**Problem:** Test times vary wildly

**Solutions:**
- Close other applications
- Run on consistent hardware
- Disable CPU throttling
- Use `pytest-benchmark` for stable measurements

### High Memory in CI

**Problem:** Tests fail in CI due to memory limits

**Solutions:**
- Run tests in smaller batches
- Increase CI memory limits
- Use garbage collection between tests
- Mock large data structures

## Summary

The performance profiling system provides:

✅ **Automatic tracking** - Every test is profiled
✅ **Detailed reports** - Slowest tests, memory usage, CPU
✅ **Regression detection** - Catch performance issues early
✅ **Optimization guidance** - Identify bottlenecks quickly

Keep tracking performance to maintain AsciiDoc Artisan's fast, responsive user experience!

---

**Next Steps:**
1. Run test suite: `pytest tests/ -v`
2. Review performance summary
3. Investigate slow tests
4. Optimize and re-test
5. Update baselines

**Related Docs:**
- [Testing Guide](TESTING.md)
- [Coverage Report](../htmlcov/index.html)
- [Architecture](../CLAUDE.md)
