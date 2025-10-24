#!/usr/bin/env python3
"""
Performance Profiling Script for AsciiDoc Artisan

Benchmarks:
1. Startup time (application initialization)
2. Preview rendering latency
3. Memory usage
4. Module import times

Usage:
    python3 profile_performance.py

Requirements:
    - QT_QPA_PLATFORM=offscreen (for headless mode)
    - All dependencies installed
"""

import os
import sys
import time
import traceback
import tracemalloc
from pathlib import Path

# Set offscreen platform for headless testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

def profile_imports():
    """Profile module import times."""
    print("=" * 70)
    print("MODULE IMPORT PROFILING")
    print("=" * 70)

    imports = [
        ("asciidoc_artisan", "Main package"),
        ("asciidoc_artisan.core", "Core module"),
        ("asciidoc_artisan.workers", "Workers module"),
        ("asciidoc_artisan.ui", "UI module"),
    ]

    results = []
    for module, desc in imports:
        start = time.perf_counter()
        try:
            __import__(module)
            elapsed = (time.perf_counter() - start) * 1000
            results.append((module, desc, elapsed, True))
            print(f"✅ {module:30s} {elapsed:7.2f}ms - {desc}")
        except Exception as e:
            results.append((module, desc, 0, False))
            print(f"❌ {module:30s} FAILED - {e}")

    print()
    return results


def profile_startup():
    """Profile application startup time."""
    print("=" * 70)
    print("STARTUP TIME PROFILING")
    print("=" * 70)

    # Measure class import
    start = time.perf_counter()
    from asciidoc_artisan import AsciiDocEditor
    import_time = (time.perf_counter() - start) * 1000
    print(f"AsciiDocEditor import: {import_time:.2f}ms")

    # Measure QApplication creation
    start = time.perf_counter()
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    qapp_time = (time.perf_counter() - start) * 1000
    print(f"QApplication creation: {qapp_time:.2f}ms")

    # Measure editor instantiation
    start = time.perf_counter()
    try:
        editor = AsciiDocEditor()
        init_time = (time.perf_counter() - start) * 1000
        print(f"AsciiDocEditor init:   {init_time:.2f}ms")

        total_startup = import_time + qapp_time + init_time
        print(f"\n{'Total Startup Time:':20s} {total_startup:.2f}ms")

        # Check against spec requirement (NFR-002: < 3 seconds)
        spec_limit = 3000  # ms
        if total_startup < spec_limit:
            print(f"✅ PASS - Under {spec_limit}ms requirement (NFR-002)")
        else:
            print(f"❌ FAIL - Exceeds {spec_limit}ms requirement (NFR-002)")

        print()
        return editor, {
            'import_time': import_time,
            'qapp_time': qapp_time,
            'init_time': init_time,
            'total': total_startup,
            'passes_spec': total_startup < spec_limit
        }
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()
        return None, None


def profile_preview_rendering(editor):
    """Profile preview rendering latency."""
    print("=" * 70)
    print("PREVIEW RENDERING PROFILING")
    print("=" * 70)

    if not editor:
        print("❌ Skipped - No editor instance")
        return None

    # Test documents of varying complexity
    test_docs = [
        ("Simple", "= Simple Document\n\nJust a paragraph."),
        ("Medium", "= Medium Document\n\n" + "\n\n".join([f"== Section {i}\n\nParagraph {i}" for i in range(10)])),
        ("Complex", "= Complex Document\n\n" + "\n\n".join([
            f"== Section {i}\n\n"
            f"Some text with *bold* and _italic_.\n\n"
            f"[source,python]\n----\ndef example():\n    return True\n----\n\n"
            f"[NOTE]\n====\nThis is a note.\n===="
            for i in range(5)
        ])),
    ]

    results = []
    spec_limit = 350  # ms (NFR-001: < 350ms, 95th percentile)

    for name, content in test_docs:
        times = []
        for i in range(10):  # 10 iterations
            editor.editor.setPlainText(content)
            start = time.perf_counter()
            editor.update_preview()
            # Process events to complete rendering
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(0.95 * len(times))]

        passes = p95_time < spec_limit
        status = "✅ PASS" if passes else "❌ FAIL"

        print(f"{name:10s} - Avg: {avg_time:6.2f}ms, P95: {p95_time:6.2f}ms {status}")
        results.append({
            'name': name,
            'avg': avg_time,
            'p95': p95_time,
            'passes_spec': passes
        })

    print(f"\nSpec Requirement (NFR-001): < {spec_limit}ms (95th percentile)")
    print()
    return results


def profile_memory_usage(editor):
    """Profile memory usage."""
    print("=" * 70)
    print("MEMORY USAGE PROFILING")
    print("=" * 70)

    if not editor:
        print("❌ Skipped - No editor instance")
        return None

    tracemalloc.start()

    # Load a typical document
    typical_doc = "= Document\n\n" + "\n\n".join([
        f"== Section {i}\n\nContent for section {i}."
        for i in range(50)
    ])

    editor.editor.setPlainText(typical_doc)
    editor.update_preview()

    from PySide6.QtWidgets import QApplication
    QApplication.processEvents()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    current_mb = current / 1024 / 1024
    peak_mb = peak / 1024 / 1024

    spec_limit = 500  # MB (NFR-004: < 500MB for typical documents)
    passes = peak_mb < spec_limit
    status = "✅ PASS" if passes else "❌ FAIL"

    print(f"Current Memory: {current_mb:6.2f}MB")
    print(f"Peak Memory:    {peak_mb:6.2f}MB {status}")
    print(f"\nSpec Requirement (NFR-004): < {spec_limit}MB for typical documents")
    print()

    return {
        'current_mb': current_mb,
        'peak_mb': peak_mb,
        'passes_spec': passes
    }


def generate_report(import_results, startup_results, preview_results, memory_results):
    """Generate performance report."""
    print("=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)

    # Startup Summary
    if startup_results:
        print(f"\nStartup Time: {startup_results['total']:.2f}ms")
        print(f"  - Import:    {startup_results['import_time']:.2f}ms")
        print(f"  - QApp:      {startup_results['qapp_time']:.2f}ms")
        print(f"  - Init:      {startup_results['init_time']:.2f}ms")
        print(f"  Spec Status: {'✅ PASS' if startup_results['passes_spec'] else '❌ FAIL'}")

    # Preview Summary
    if preview_results:
        print(f"\nPreview Rendering (P95):")
        all_pass = all(r['passes_spec'] for r in preview_results)
        for r in preview_results:
            print(f"  - {r['name']:10s}: {r['p95']:.2f}ms ({'✅' if r['passes_spec'] else '❌'})")
        print(f"  Spec Status: {'✅ PASS' if all_pass else '❌ FAIL'}")

    # Memory Summary
    if memory_results:
        print(f"\nMemory Usage: {memory_results['peak_mb']:.2f}MB")
        print(f"  Spec Status: {'✅ PASS' if memory_results['passes_spec'] else '❌ FAIL'}")

    # Overall Compliance
    print(f"\n{'=' * 70}")
    all_tests_pass = (
        (not startup_results or startup_results['passes_spec']) and
        (not preview_results or all(r['passes_spec'] for r in preview_results)) and
        (not memory_results or memory_results['passes_spec'])
    )

    if all_tests_pass:
        print("✅ ALL PERFORMANCE REQUIREMENTS MET")
    else:
        print("⚠️  SOME PERFORMANCE REQUIREMENTS NOT MET")
    print("=" * 70)
    print()

    return {
        'startup': startup_results,
        'preview': preview_results,
        'memory': memory_results,
        'all_pass': all_tests_pass
    }


def main():
    """Main profiling entry point."""
    print("\n" + "=" * 70)
    print("ASCIIDOC ARTISAN - PERFORMANCE PROFILING")
    print("=" * 70)
    print()

    # Profile imports
    import_results = profile_imports()

    # Profile startup
    editor, startup_results = profile_startup()

    # Profile preview rendering
    preview_results = profile_preview_rendering(editor) if editor else None

    # Profile memory usage
    memory_results = profile_memory_usage(editor) if editor else None

    # Generate summary
    report = generate_report(import_results, startup_results, preview_results, memory_results)

    # Save results
    print("Performance profiling complete!")
    print()

    return report


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProfiling interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ PROFILING FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)
