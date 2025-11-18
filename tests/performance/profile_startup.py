"""
Profile application startup performance.

This script measures:
- Import time for all modules
- Application initialization time
- Memory usage during startup
- Top time-consuming operations

Usage:
    python tests/performance/profile_startup.py
"""

import cProfile
import io
import pstats
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import psutil


def profile_imports():
    """Profile module import times."""
    print("=" * 80)
    print("PROFILING MODULE IMPORTS")
    print("=" * 80)

    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024
    start_time = time.perf_counter()

    # Profile each major import
    imports = [
        ("PySide6.QtWidgets", "from PySide6.QtWidgets import QApplication"),
        ("PySide6.QtCore", "from PySide6.QtCore import QObject, Signal"),
        ("asciidoc_artisan.core", "from asciidoc_artisan.core import APP_NAME"),
        ("asciidoc_artisan.ui", "from asciidoc_artisan.ui import AsciiDocEditor"),
    ]

    results = []
    for name, import_stmt in imports:
        t0 = time.perf_counter()
        m0 = process.memory_info().rss / 1024 / 1024

        try:
            exec(import_stmt)

            t1 = time.perf_counter()
            m1 = process.memory_info().rss / 1024 / 1024

            results.append({"module": name, "time_ms": (t1 - t0) * 1000, "memory_mb": m1 - m0})
        except Exception as e:
            results.append({"module": name, "time_ms": 0, "memory_mb": 0, "error": str(e)})

    total_time = time.perf_counter() - start_time
    total_memory = process.memory_info().rss / 1024 / 1024 - start_memory

    print(f"\n{'Module':<40} {'Time (ms)':>12} {'Memory (MB)':>12}")
    print("-" * 80)
    for r in results:
        if "error" in r:
            print(f"{r['module']:<40} {'ERROR':>12} {'-':>12}")
        else:
            print(f"{r['module']:<40} {r['time_ms']:>12.2f} {r['memory_mb']:>12.2f}")

    print("-" * 80)
    print(f"{'TOTAL IMPORTS':<40} {total_time * 1000:>12.2f} {total_memory:>12.2f}")
    print()

    return results


def profile_application_init():
    """Profile application initialization with cProfile."""
    print("=" * 80)
    print("PROFILING APPLICATION INITIALIZATION")
    print("=" * 80)

    # Set Qt platform to offscreen to avoid GUI display
    import os

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PySide6.QtWidgets import QApplication

    from asciidoc_artisan.core import APP_NAME
    from asciidoc_artisan.ui import AsciiDocEditor

    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024

    # Profile with cProfile
    profiler = cProfile.Profile()
    profiler.enable()

    start_time = time.perf_counter()

    # Initialize application
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan")

    # Create main window (but don't show it)
    AsciiDocEditor()

    end_time = time.perf_counter()

    profiler.disable()

    end_memory = process.memory_info().rss / 1024 / 1024

    # Print timing results
    print(f"\nInitialization Time: {(end_time - start_time) * 1000:.2f} ms")
    print(f"Memory Used: {end_memory - start_memory:.2f} MB")
    print(f"Total Memory: {end_memory:.2f} MB")

    # Analyze profile data
    print("\n" + "=" * 80)
    print("TOP 20 TIME-CONSUMING FUNCTIONS")
    print("=" * 80)

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)
    print(s.getvalue())

    # Save detailed profile
    profile_file = Path(__file__).parent / "startup_profile.stats"
    profiler.dump_stats(str(profile_file))
    print(f"\nDetailed profile saved to: {profile_file}")
    print(f"View with: python -m pstats {profile_file}")

    # Cleanup
    app.quit()

    return {
        "init_time_ms": (end_time - start_time) * 1000,
        "memory_mb": end_memory - start_memory,
        "total_memory_mb": end_memory,
    }


def profile_component_creation():
    """Profile individual component creation times."""
    print("\n" + "=" * 80)
    print("PROFILING INDIVIDUAL COMPONENTS")
    print("=" * 80)

    import os

    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication, QPlainTextEdit, QTextBrowser

    app = QApplication.instance() or QApplication(sys.argv)
    process = psutil.Process()

    components = [
        ("QPlainTextEdit", lambda: QPlainTextEdit()),
        ("QTextBrowser", lambda: QTextBrowser()),
        ("QSettings", lambda: QSettings("AsciiDoc Artisan", "AsciiDocArtisan")),
    ]

    results = []
    print(f"\n{'Component':<30} {'Time (ms)':>12} {'Memory (MB)':>12}")
    print("-" * 80)

    for name, creator in components:
        t0 = time.perf_counter()
        m0 = process.memory_info().rss / 1024 / 1024

        try:
            obj = creator()

            t1 = time.perf_counter()
            m1 = process.memory_info().rss / 1024 / 1024

            time_ms = (t1 - t0) * 1000
            memory_mb = m1 - m0

            results.append({"component": name, "time_ms": time_ms, "memory_mb": memory_mb})

            print(f"{name:<30} {time_ms:>12.2f} {memory_mb:>12.2f}")

            # Cleanup
            del obj
        except Exception as e:
            print(f"{name:<30} {'ERROR':>12} {str(e)}")
            results.append({"component": name, "error": str(e)})

    print()
    app.quit()
    return results


def main():
    """Run all profiling tests."""
    print("\n" + "=" * 80)
    print("ASCIIDOC ARTISAN - STARTUP PERFORMANCE PROFILING")
    print("=" * 80)

    process = psutil.Process()
    print(f"\nPython: {sys.version}")
    print(f"Process PID: {process.pid}")
    print(f"Initial Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")

    # Run profiling tests
    import_results = profile_imports()
    init_results = profile_application_init()
    profile_component_creation()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_import_time = sum(r.get("time_ms", 0) for r in import_results)
    total_import_memory = sum(r.get("memory_mb", 0) for r in import_results)

    print("\nImport Phase:")
    print(f"  Time: {total_import_time:.2f} ms")
    print(f"  Memory: {total_import_memory:.2f} MB")

    print("\nInitialization Phase:")
    print(f"  Time: {init_results['init_time_ms']:.2f} ms")
    print(f"  Memory: {init_results['memory_mb']:.2f} MB")

    print("\nTotal Startup:")
    print(f"  Time: {total_import_time + init_results['init_time_ms']:.2f} ms")
    print(f"  Memory: {init_results['total_memory_mb']:.2f} MB")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    # Analyze and provide recommendations
    if total_import_time > 500:
        print("\n⚠️  Import time is high (>500ms)")
        print("   Consider: Lazy loading, defer non-critical imports")

    if init_results["init_time_ms"] > 1000:
        print("\n⚠️  Initialization time is high (>1000ms)")
        print("   Consider: Deferred widget creation, async initialization")

    if init_results["memory_mb"] > 200:
        print("\n⚠️  Startup memory usage is high (>200MB)")
        print("   Consider: Lazy loading, object pooling, cache limits")

    print("\n✅ Profile complete! Check startup_profile.stats for detailed analysis.")
    print("   Run: python -m pstats tests/performance/startup_profile.stats")
    print()


if __name__ == "__main__":
    main()
