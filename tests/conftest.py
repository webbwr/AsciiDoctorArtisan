"""
Pytest configuration and fixtures for AsciiDoc Artisan tests.

Provides shared fixtures, performance profiling, and coverage tracking.

Performance Optimizations:
- Session-scoped fixtures for expensive setup
- Fast mock factories
- Optimized Qt application handling
- Performance metrics tracking
"""

import os
import time
from pathlib import Path

import psutil
import pytest

# Plugin registration must be at root conftest level
pytest_plugins = ["pytest_bdd"]

# Set Qt to use offscreen platform for headless testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests marked with requires_gpu when GPU unavailable."""
    skip_gpu = pytest.mark.skip(reason="requires_gpu: QWebEngine not available in test environment")
    for item in items:
        if "requires_gpu" in item.keywords:
            item.add_marker(skip_gpu)


# Disable keyring to prevent macOS Security.framework issues
os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

# Performance tracking
_test_metrics = {}


# Using pytest-qt's built-in qapp fixture for Qt application lifecycle
# pytest-qt automatically manages QApplication instance


@pytest.fixture
def temp_dir(tmp_path) -> Path:
    """Provide a temporary directory for test file operations."""
    return tmp_path


@pytest.fixture
def sample_asciidoc() -> str:
    """Provide sample AsciiDoc content for testing."""
    return """= Test Document
:author: Test Author
:version: 1.0.0

== Introduction

This is a test document.

=== Subsection

Some content here.

== Features

* Feature 1
* Feature 2
* Feature 3

== Code Example

[source,python]
----
def hello():
    print("Hello, World!")
----

== Conclusion

The end.
"""


@pytest.fixture
def sample_markdown() -> str:
    """Provide sample Markdown content for testing."""
    return """# Test Document

## Introduction

This is a test document.

### Subsection

Some content here.

## Features

- Feature 1
- Feature 2
- Feature 3

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

The end.
"""


@pytest.fixture(autouse=True)
def performance_tracker(request):
    """
    Automatically track performance metrics for each test.

    Records:
    - Execution time
    - Memory usage before/after
    - CPU usage
    """
    process = psutil.Process()

    # Capture initial state
    start_time = time.time()
    start_mem = process.memory_info().rss / 1024 / 1024  # MB
    _start_cpu = process.cpu_percent()  # For future use

    yield

    # Capture final state
    end_time = time.time()
    end_mem = process.memory_info().rss / 1024 / 1024  # MB
    end_cpu = process.cpu_percent()

    # Store metrics
    test_name = request.node.nodeid
    _test_metrics[test_name] = {
        "duration": end_time - start_time,
        "memory_start_mb": start_mem,
        "memory_end_mb": end_mem,
        "memory_delta_mb": end_mem - start_mem,
        "cpu_percent": end_cpu,
    }


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Print performance summary after test run.

    Shows:
    - Slowest tests
    - Highest memory usage tests
    - Overall statistics
    """
    if not _test_metrics:
        return

    terminalreporter.write_sep("=", "Performance Summary")

    # Sort by duration
    by_duration = sorted(_test_metrics.items(), key=lambda x: x[1]["duration"], reverse=True)

    terminalreporter.write_line("\nSlowest 10 Tests:")
    for test_name, metrics in by_duration[:10]:
        terminalreporter.write_line(f"  {metrics['duration']:.3f}s - {test_name}")

    # Sort by memory
    by_memory = sorted(_test_metrics.items(), key=lambda x: abs(x[1]["memory_delta_mb"]), reverse=True)

    terminalreporter.write_line("\nHighest Memory Usage (Top 10):")
    for test_name, metrics in by_memory[:10]:
        delta = metrics["memory_delta_mb"]
        sign = "+" if delta > 0 else ""
        terminalreporter.write_line(f"  {sign}{delta:.2f}MB - {test_name}")

    # Overall statistics
    total_duration = sum(m["duration"] for m in _test_metrics.values())
    avg_duration = total_duration / len(_test_metrics)
    max_memory = max(m["memory_end_mb"] for m in _test_metrics.values())

    terminalreporter.write_line("\nOverall Statistics:")
    terminalreporter.write_line(f"  Total tests: {len(_test_metrics)}")
    terminalreporter.write_line(f"  Total time: {total_duration:.2f}s")
    terminalreporter.write_line(f"  Average time: {avg_duration:.3f}s")
    terminalreporter.write_line(f"  Peak memory: {max_memory:.2f}MB")


@pytest.fixture
def mock_git_repo(temp_dir) -> Path:
    """
    Create a mock Git repository for testing.

    Returns the path to the temporary Git repo.
    """
    import subprocess

    repo_path = temp_dir / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    test_file = repo_path / "test.txt"
    test_file.write_text("Initial content")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    return repo_path


@pytest.fixture
def coverage_report_dir(tmp_path) -> Path:
    """Provide directory for coverage reports."""
    report_dir = tmp_path / "coverage"
    report_dir.mkdir()
    return report_dir


@pytest.fixture
def test_settings(tmp_path):
    """
    Provide test-safe settings that prevent UI dialogs.

    Automatically disables:
    - Telemetry opt-in dialog (sets telemetry_opt_in_shown=True)
    - Ollama integration (prevents network calls)
    - Git features (prevents subprocess calls)
    """
    from asciidoc_artisan.core import Settings

    settings = Settings()
    # Prevent telemetry dialog from showing
    settings.telemetry_opt_in_shown = True
    settings.telemetry_enabled = False
    settings.telemetry_session_id = None

    # Disable features that make external calls
    settings.ollama_enabled = False
    settings.ollama_model = None
    settings.ai_conversion_enabled = False
    settings.ai_chat_enabled = False

    # Safe defaults for testing
    settings.last_directory = str(tmp_path)
    settings.last_file = None
    settings.git_repo_path = None

    return settings


# ============================================================================
# Session-Scoped Fixtures (Performance Optimization)
# ============================================================================


@pytest.fixture(scope="session")
def session_temp_dir(tmp_path_factory):
    """
    Session-scoped temporary directory.

    Use for expensive setup that can be shared across tests.
    """
    return tmp_path_factory.mktemp("session")


@pytest.fixture(scope="session")
def sample_asciidoc_large():
    """
    Large AsciiDoc document for performance testing.

    Generated once per session to avoid repeated string building.
    """
    sections = []
    for i in range(100):
        sections.append(
            f"""
== Section {i}

This is section {i} with content.

=== Subsection {i}.1

* Item 1
* Item 2
* Item 3

[source,python]
----
def function_{i}():
    return {i}
----
"""
        )
    return "= Large Test Document\n" + "\n".join(sections)


@pytest.fixture(scope="session")
def sample_markdown_large():
    """
    Large Markdown document for performance testing.

    Generated once per session.
    """
    sections = []
    for i in range(100):
        sections.append(
            f"""
## Section {i}

This is section {i} with content.

### Subsection {i}.1

- Item 1
- Item 2
- Item 3

```python
def function_{i}():
    return {i}
```
"""
        )
    return "# Large Test Document\n" + "\n".join(sections)


@pytest.fixture(scope="module")
def module_temp_dir(tmp_path_factory):
    """
    Module-scoped temporary directory.

    Use for tests in the same module that can share temp dir.
    """
    return tmp_path_factory.mktemp("module")


# ============================================================================
# Fast Mock Factories
# ============================================================================


@pytest.fixture
def fast_qtbot(qtbot):
    """
    Optimized qtbot with reduced timeout defaults.

    Uses 500ms timeout instead of 5000ms for faster test execution.
    """
    from tests.test_utils import FastQtBot

    return FastQtBot(qtbot)


@pytest.fixture
def fast_settings(tmp_path):
    """
    Test settings with all slow features disabled.

    Optimized for test performance:
    - No telemetry
    - No AI features
    - No network calls
    - Instant preview updates
    """
    from tests.test_utils import create_fast_settings

    return create_fast_settings(tmp_path)


@pytest.fixture
def performance_monitor():
    """
    Performance monitoring helper for tests.

    Usage:
        def test_something(performance_monitor):
            performance_monitor.start()
            # ... test code ...
            metrics = performance_monitor.stop()
            assert metrics["duration"] < 1.0
    """
    from tests.test_utils import PerformanceMonitor

    return PerformanceMonitor()
