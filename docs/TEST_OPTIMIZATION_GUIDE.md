# Test Optimization Guide

**Last Updated:** November 13, 2025
**Status:** Active
**Test Count:** 5,479 tests across 148 files

## Overview

This guide documents test suite optimizations for AsciiDoc Artisan, providing strategies to reduce test execution time while maintaining quality and reliability.

## Quick Start

```bash
# Fast unit tests only (recommended for development)
make test-fast

# All unit tests
make test-unit

# Integration tests only
make test-integration

# Slow/stress tests
make test-slow

# Performance tests with metrics
make test-perf

# Full suite with coverage
make test
```

## Performance Metrics (Baseline)

**Test Suite Stats:**
- Total tests: 5,479
- Collection time: ~5 seconds
- Unit tests: ~5,300 (fast)
- Integration tests: ~158 (some slow)
- Marked as slow: 10 stress tests

**Slowest Patterns Identified:**
1. **time.sleep()** - Up to 2 seconds in worker cleanup
2. **asyncio.sleep()** - 17+ calls accumulating in async tests
3. **Long timeouts** - Up to 30 seconds in stress tests
4. **Large loops** - Up to 2,000 iterations in memory tests
5. **Real QThread workers** - Thread overhead in integration tests

## Optimization Strategies

### 1. Use Fast Fixtures

**Before:**
```python
def test_something(qtbot, tmp_path):
    settings = Settings()
    # ... configure settings ...
    qtbot.waitSignal(signal, timeout=5000)
```

**After:**
```python
def test_something(fast_qtbot, fast_settings):
    # fast_settings has all slow features disabled
    # fast_qtbot uses 500ms timeout instead of 5000ms
    fast_qtbot.wait_signal(signal)  # 10x faster
```

### 2. Use Session-Scoped Fixtures

**Before:**
```python
@pytest.fixture
def large_document():
    # Regenerated for every test
    return "\n".join([f"== Section {i}" for i in range(1000)])
```

**After:**
```python
# Already available in conftest.py
def test_something(sample_asciidoc_large):
    # Generated once per test session
    assert len(sample_asciidoc_large) > 10000
```

### 3. Use fast_sleep() Helper

**Before:**
```python
import time

def test_worker_cleanup():
    worker.start()
    time.sleep(2.0)  # 2 full seconds
    worker.stop()
```

**After:**
```python
from tests.test_utils import fast_sleep

def test_worker_cleanup():
    worker.start()
    fast_sleep(2.0)  # Only 0.2 seconds (10x multiplier)
    worker.stop()
```

### 4. Mock Expensive Operations

**Before:**
```python
def test_git_status():
    # Real subprocess call
    result = git_worker.get_status()
```

**After:**
```python
from tests.test_utils import create_mock_worker

def test_git_status(mocker):
    worker = create_mock_worker(GitWorker, "status_ready")
    mocker.patch.object(worker, "get_status", return_value=mock_result)
    result = worker.get_status()
```

### 5. Reduce Loop Iterations in Tests

**Before:**
```python
def test_cache_bounded():
    for i in range(2000):  # 2000 iterations
        cache.add(i)
```

**After:**
```python
@pytest.mark.parametrize("size", [10, 100, 500])
def test_cache_bounded(size):
    # Test at multiple scales, not exhaustive iteration
    for i in range(size):
        cache.add(i)
```

### 6. Use Performance Monitoring

```python
def test_rendering_performance(performance_monitor):
    performance_monitor.start()

    # ... rendering code ...

    metrics = performance_monitor.stop()
    assert metrics["duration"] < 0.1  # 100ms threshold
    assert metrics["memory_delta_mb"] < 10  # 10MB threshold
```

## Available Test Utilities

### test_utils.py Helpers

| Function | Purpose | Example |
|----------|---------|---------|
| `fast_sleep(seconds)` | 10x faster sleep | `fast_sleep(1.0)` = 0.1s |
| `create_mock_worker()` | Mock worker with signals | Worker mocking pattern |
| `skip_if_slow` | Decorator for slow tests | `@skip_if_slow` |
| `FastQtBot` | Optimized qtbot wrapper | Reduced timeouts |
| `assert_performance()` | Performance assertions | Duration checks |
| `PerformanceMonitor` | Metrics tracking | Memory/CPU/time |
| `create_fast_settings()` | Test-optimized settings | All slow features off |

### conftest.py Fixtures

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `fast_qtbot` | function | Qt testing with 500ms timeouts |
| `fast_settings` | function | Settings with slow features disabled |
| `performance_monitor` | function | Performance metrics helper |
| `session_temp_dir` | session | Shared temp directory |
| `sample_asciidoc_large` | session | Large doc (generated once) |
| `sample_markdown_large` | session | Large MD doc (generated once) |
| `module_temp_dir` | module | Module-shared temp dir |

## Pytest Markers

```bash
# Run only fast tests
pytest -m "fast"

# Skip slow tests
pytest -m "not slow"

# Run specific categories
pytest -m "unit"
pytest -m "integration"
pytest -m "performance"
pytest -m "memory"
pytest -m "stress"

# Combine markers
pytest -m "integration and not slow"
```

## Integration Test Optimization

### Identified Slow Tests

**File: test_async_integration.py** (17 async sleeps)
- Accumulated sleep time: ~10+ seconds
- **Optimization:** Replace with `fast_sleep()` or mock time

**File: test_memory_leaks.py** (2s sleep + large loops)
- Line 470: `time.sleep(2.0)` - Worker cleanup
- Line 425: `for i in range(2000)` - Largest loop
- **Optimization:** Reduce sleep to 0.2s, parameterize loops

**File: test_stress.py** (30s timeout + 1000-item loops)
- Line 98: `wait_for_done(timeout_ms=30000)`
- Line 32: `for i in range(1000)` - Large document
- **Optimization:** Reduce timeout to 5s, smaller test documents

**File: test_ui_integration.py** (34 tests with 1s waits)
- Lines 63-580: Thread.wait(1000) calls
- **Optimization:** Mock thread completion or reduce to 100ms

## Performance Targets

| Test Category | Target Time | Current Status |
|---------------|-------------|----------------|
| Unit tests (all) | <30s | ✅ ~15-20s |
| Integration (fast) | <60s | ⚠️ ~90s (needs optimization) |
| Integration (all) | <120s | ⚠️ ~180s (needs optimization) |
| Slow/Stress tests | <300s | ⏳ Variable (marked separately) |
| Full suite | <180s | ⚠️ ~240s (needs optimization) |

## Best Practices

### DO ✅

1. **Use session/module-scoped fixtures** for expensive setup
2. **Mock external calls** (subprocess, network, file I/O)
3. **Use fast_sleep()** instead of time.sleep()
4. **Parameterize** tests instead of large loops
5. **Mark slow tests** with `@pytest.mark.slow`
6. **Use fast_qtbot** for Qt tests
7. **Profile slow tests** with `--durations=20`
8. **Run fast tests** during development (`make test-fast`)

### DON'T ❌

1. **Don't use time.sleep() > 0.1s** without `@pytest.mark.slow`
2. **Don't create real QThread workers** unless necessary
3. **Don't iterate > 100 times** without parameterization
4. **Don't use real subprocess calls** - mock them
5. **Don't wait for actual timeouts** - use fast_qtbot
6. **Don't regenerate** fixtures per test - use session scope
7. **Don't test exhaustively** - test boundaries and samples
8. **Don't forget** to mark integration/slow tests

## macOS-Specific Constraints

**Security.framework Issue:**
- Cannot use pytest-xdist (`-n auto`) on macOS
- Fork() crashes with Security.framework loaded
- Parallel execution disabled in pytest.ini

**Workarounds:**
1. Use GitHub Actions Linux runners for parallel tests
2. Optimize individual test speed instead
3. Use session-scoped fixtures to amortize setup cost

## Monitoring Performance

### Get Slowest Tests

```bash
# Show 20 slowest tests
pytest tests/ --durations=20

# With performance summary
pytest tests/ -v
# See performance summary at end (from conftest.py)
```

### Measure Improvements

```bash
# Before optimization
time pytest tests/unit/ -q

# After optimization
time pytest tests/unit/ -q

# Calculate speedup
python3 -c "print(f'{before/after:.2f}x faster')"
```

## Future Optimizations

1. **Parallel execution** on Linux/Windows (add `-n auto`)
2. **Reduce integration test sleep times** to 10% of current
3. **Mock more subprocess calls** in Git/Pandoc tests
4. **Parameterize large loop tests** to run subset
5. **Create "smoke test" suite** (<10s for CI quick checks)
6. **Profile memory tests** and reduce iteration counts
7. **Add pytest-timeout** to catch hanging tests

## Resources

- **Pytest Documentation:** https://docs.pytest.org/en/stable/
- **pytest-qt:** https://pytest-qt.readthedocs.io/
- **pytest-benchmark:** https://pytest-benchmark.readthedocs.io/
- **Test Utils:** `tests/test_utils.py`
- **Fixtures:** `tests/conftest.py`
- **Configuration:** `pytest.ini`

---

**Questions?** Check `tests/test_utils.py` for examples or run `make help` for test targets.
