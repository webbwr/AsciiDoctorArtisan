# Test Limitations on macOS

**Last Updated:** November 9, 2025
**Status:** Active limitations requiring awareness

## Overview

This document outlines known testing limitations on macOS, particularly those related to fork() restrictions in macOS frameworks and platform-specific test failures.

## Critical macOS Limitations

### 1. QtWebEngine Fork Crash (BLOCKING)

**Issue:** macOS does NOT support fork() in multi-threaded processes when certain frameworks are loaded.

**Affected Frameworks:**
- **QtWebEngineCore** (Chromium-based web rendering)
- **macOS Security.framework** (keyring access)

**Root Cause:**
```
CFRunLoopWakeUp.cold.2: "Unable to send message to wake up port."
Error: "multi-threaded process forked"
Exception: EXC_BREAKPOINT (SIGTRAP) or EXC_BAD_ACCESS (SIGSEGV)
```

When pytest-cov attempts to fork processes for coverage collection, any code that has initialized QtWebEngineCore or Security.framework will crash the forked child process.

**Solution Implemented:**
- Disable keyring via `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`
- Disable QtWebEngine via `DISABLE_QTWEBENGINE_IN_TESTS=1`
- Mock keyring globally in `conftest.py` before any imports
- Set Qt to offscreen mode: `QT_QPA_PLATFORM=offscreen`
- Remove all multiprocessing pytest flags (no --forked, -n, etc.)

**Files:**
- `conftest.py` - Sets environment variables BEFORE any imports
- `pyproject.toml` - Pytest configuration with environment settings
- `pytest_run_safe.py` - Safe test runner for unit tests only

### 2. Platform-Specific GPU Detection Test Failures

**Issue:** GPU detection tests are written for Linux/NVIDIA but running on macOS with Apple Silicon.

**Failing Tests (5 total):**
1. `test_opencl_detected` - Mock StopIteration error
2. `test_vulkan_detected` - Mock StopIteration error
3. `test_detect_gpu_no_dri` - Detects Apple M1 Ultra instead of "no GPU"
4. `test_detect_gpu_software_renderer` - Detects Apple M1 Ultra instead of software renderer
5. `test_detect_gpu_by_type[nvidia...]` - Detects apple instead of nvidia

**Status:** NON-BLOCKING - These are acceptable platform-specific failures
- Tests expect Linux GPU detection patterns (DRI devices, NVIDIA tools)
- macOS uses Metal GPU API instead of OpenGL/Vulkan/OpenCL
- Apple Silicon has integrated GPU (not discrete like NVIDIA)

**Recommendation:** Skip these tests on macOS or add platform-conditional expectations

## Test Execution Strategy

### Safe Test Runner

Use `pytest_run_safe.py` for crash-free test execution:

```bash
python3 pytest_run_safe.py
```

This script:
- Sets all environment variables correctly BEFORE imports
- Runs only `tests/unit` (avoids integration tests that might start Qt apps)
- Uses `-q --tb=short --maxfail=5` for concise output

### Standard pytest Execution

```bash
pytest tests/unit -q --tb=short
```

**What to expect:**
- 400 unit tests collected
- 395 passing (98.75% pass rate)
- 5 failures (all GPU detection platform-specific)
- No crashes (with environment variables set)

### Environment Variables Required

**In `conftest.py` (auto-loaded):**
```python
os.environ['PYTHON_KEYRING_BACKEND'] = 'keyring.backends.null.Keyring'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox --disable-dev-shm-usage'
os.environ['DISABLE_QTWEBENGINE_IN_TESTS'] = '1'
```

**In `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
env = [
    "QT_QPA_PLATFORM=offscreen",
    "PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring",
]
```

## Coverage Limitations

### Current Status

**Coverage collection works** but with limitations:
- Unit tests can be run with coverage: `pytest tests/unit --cov=src/asciidoc_artisan`
- Integration tests may fail if they initialize QtWebEngine
- Some tests must be skipped on macOS

### Recommendations

1. **Split test suites:**
   - Unit tests: Fast, no Qt app initialization
   - Integration tests: Full Qt app, skip on macOS in CI

2. **Use pytest markers:**
   ```python
   @pytest.mark.skipif(sys.platform == "darwin", reason="macOS fork limitation")
   def test_with_qtwebengine():
       ...
   ```

3. **Mock QtWebEngine in tests:**
   - Avoid importing QtWebEngine modules in test files
   - Use mock preview handlers instead

## Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| QtWebEngine fork crash | MITIGATED | Environment variables + conftest.py |
| Security.framework crash | MITIGATED | Mocked keyring |
| GPU detection failures | ACCEPTED | Platform-specific, non-blocking |
| Coverage <100% | IN PROGRESS | Incremental improvement |

## Future Work

1. Add platform-conditional GPU detection tests
2. Mock QtWebEngine more comprehensively
3. Separate integration tests into `tests/integration/`
4. Add CI matrix for Linux/macOS/Windows test execution
5. Document coverage gaps and create targeted tests

## References

- **macOS fork() restrictions:** https://developer.apple.com/library/archive/technotes/tn2083/_index.html
- **QtWebEngine Chromium base:** https://doc.qt.io/qt-6/qtwebengine-overview.html
- **pytest-cov fork issues:** https://github.com/pytest-dev/pytest-cov/issues/237

---

**For questions or issues, see:**
- `conftest.py` - Test configuration
- `pytest_run_safe.py` - Safe test runner
- `pyproject.toml` - Pytest settings
