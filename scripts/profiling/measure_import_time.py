#!/usr/bin/env python3
"""
Measure import time for AsciiDoc Artisan.

Focus on module import performance (main startup bottleneck).

Target (v1.5.0): Startup < 2.0s
Target (v1.6.0): Startup < 1.5s
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def measure_imports():
    """Measure import time for all major modules."""
    print("=" * 70)
    print("AsciiDoc Artisan Import Time Measurement")
    print("=" * 70)
    print()

    results = []

    # Test 1: Core imports
    start = time.perf_counter()
    core_time = (time.perf_counter() - start) * 1000
    results.append(("Core Python modules", core_time))

    # Test 2: PySide6
    start = time.perf_counter()
    pyside_time = (time.perf_counter() - start) * 1000
    results.append(("PySide6 Qt Framework", pyside_time))

    # Test 3: AsciiDoc
    start = time.perf_counter()
    try:
        import asciidoc3
        from asciidoc3.asciidoc3api import AsciiDoc3API

        asciidoc_time = (time.perf_counter() - start) * 1000
    except ImportError:
        asciidoc_time = 0
    results.append(("asciidoc3", asciidoc_time))

    # Test 4: Pandoc
    start = time.perf_counter()
    try:
        import pypandoc

        pandoc_time = (time.perf_counter() - start) * 1000
    except ImportError:
        pandoc_time = 0
    results.append(("pypandoc", pandoc_time))

    # Test 5: PyMuPDF
    start = time.perf_counter()
    try:
        import pymupdf

        pymupdf_time = (time.perf_counter() - start) * 1000
    except ImportError:
        pymupdf_time = 0
    results.append(("pymupdf", pymupdf_time))

    # Test 6: Application modules
    start = time.perf_counter()
    app_time = (time.perf_counter() - start) * 1000
    results.append(("Application modules", app_time))

    # Calculate total
    total_time = sum(t for _, t in results)

    # Display results
    print("Import Time Breakdown:")
    for name, time_ms in results:
        pct = (time_ms / total_time * 100) if total_time > 0 else 0
        print(f"  {name:25s} {time_ms:7.1f}ms  ({pct:5.1f}%)")

    print(f"  {'─' * 50}")
    print(
        f"  {'Total import time':25s} {total_time:7.1f}ms  ({total_time / 1000:.2f}s)"
    )
    print()

    # Estimate total startup (imports + window creation ~500ms)
    window_overhead = 500  # Estimated window creation time
    estimated_total = total_time + window_overhead

    print("Estimated Total Startup:")
    print(f"  Import time:        {total_time:7.1f}ms")
    print(f"  Window creation:    {window_overhead:7.1f}ms (estimated)")
    print(f"  {'─' * 40}")
    print(
        f"  Total:              {estimated_total:7.1f}ms ({estimated_total / 1000:.2f}s)"
    )
    print()

    # Check targets
    estimated_s = estimated_total / 1000

    print("Performance Targets:")
    print(
        f"  v1.5.0 target: < 2.0s  {'✅ PASS' if estimated_s < 2.0 else '❌ FAIL'} ({estimated_s:.2f}s)"
    )
    print(
        f"  v1.6.0 target: < 1.5s  {'✅ PASS' if estimated_s < 1.5 else '⚠️  Close ({:.2f}s)'.format(estimated_s)}"
    )
    print()

    # Optimization recommendations
    print("Optimization Opportunities:")
    slow_imports = [(name, time_ms) for name, time_ms in results if time_ms > 100]
    if slow_imports:
        for name, time_ms in sorted(slow_imports, key=lambda x: x[1], reverse=True):
            print(f"  - {name}: {time_ms:.0f}ms (consider lazy loading)")
    else:
        print("  ✅ All imports are fast (< 100ms each)")

    print()
    print("=" * 70)


if __name__ == "__main__":
    measure_imports()
