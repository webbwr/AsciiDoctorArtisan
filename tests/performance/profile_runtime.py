"""
Profile runtime performance for AsciiDoc Artisan.

This script measures:
- AsciiDoc to HTML conversion time
- Preview rendering performance
- File I/O operations (load/save)
- Memory usage during operations

Usage:
    python tests/performance/profile_runtime.py
"""

import io
import sys
import tempfile
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import psutil

# Test if asciidoc3 is available
try:
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC_AVAILABLE = True
except ImportError:
    print("Warning: asciidoc3 not available, some tests will be skipped")
    ASCIIDOC_AVAILABLE = False


def generate_test_document(num_lines: int) -> str:
    """Generate test AsciiDoc document."""
    lines = [
        "= Performance Test Document",
        ":toc:",
        ":numbered:",
        "",
        "== Introduction",
        "",
        "This is a test document for performance benchmarking.",
        "",
    ]

    for i in range(1, num_lines // 15):
        lines.extend(
            [
                f"== Section {i}",
                "",
                f"This is section {i} with some content.",
                "",
                "* Item 1 with detailed description",
                "* Item 2 with more information",
                "* Item 3 with examples",
                "",
                "[source,python]",
                "----",
                "def example_function():",
                "    return 'test data'",
                "----",
                "",
                f"Additional paragraph with more content for section {i}.",
                "",
            ]
        )

    return "\n".join(lines)


def profile_asciidoc_conversion():
    """Profile AsciiDoc to HTML conversion."""
    if not ASCIIDOC_AVAILABLE:
        print("\n⚠️  AsciiDoc3 not available - skipping conversion tests")
        return {}

    print("=" * 80)
    print("PROFILING ASCIIDOC CONVERSION")
    print("=" * 80)

    process = psutil.Process()
    results = []

    test_sizes = [
        (100, "Small (100 lines)"),
        (1000, "Medium (1,000 lines)"),
        (5000, "Large (5,000 lines)"),
        (10000, "Very Large (10,000 lines)"),
    ]

    print(
        f"\n{'Document Size':<30} {'Time (ms)':>12} {'Memory (MB)':>12} {'HTML Size (KB)':>15}"
    )
    print("-" * 80)

    for num_lines, label in test_sizes:
        # Generate test document
        doc_content = generate_test_document(num_lines)
        doc_size_kb = len(doc_content) / 1024

        # Measure conversion
        asciidoc_api = AsciiDoc3API()
        asciidoc_api.options("--no-header-footer")
        asciidoc_api.attributes["icons"] = "font"
        asciidoc_api.attributes["source-highlighter"] = "highlight.js"

        # Warm up (avoid cold start bias)
        infile_warmup = io.StringIO(doc_content)
        outfile_warmup = io.StringIO()
        asciidoc_api.execute(infile_warmup, outfile_warmup, backend="html5")

        # Actual measurement
        infile = io.StringIO(doc_content)
        outfile = io.StringIO()

        start_memory = process.memory_info().rss / 1024 / 1024
        start_time = time.perf_counter()

        asciidoc_api.execute(infile, outfile, backend="html5")

        end_time = time.perf_counter()
        end_memory = process.memory_info().rss / 1024 / 1024

        html_output = outfile.getvalue()
        html_size_kb = len(html_output) / 1024

        time_ms = (end_time - start_time) * 1000
        memory_mb = end_memory - start_memory

        results.append(
            {
                "size": label,
                "num_lines": num_lines,
                "doc_size_kb": doc_size_kb,
                "time_ms": time_ms,
                "memory_mb": memory_mb,
                "html_size_kb": html_size_kb,
            }
        )

        print(f"{label:<30} {time_ms:>12.2f} {memory_mb:>12.2f} {html_size_kb:>15.2f}")

    print()
    return results


def profile_file_operations():
    """Profile file load and save operations."""
    print("=" * 80)
    print("PROFILING FILE I/O OPERATIONS")
    print("=" * 80)

    psutil.Process()
    results = []

    test_sizes = [
        (100, "Small (100 lines)"),
        (1000, "Medium (1,000 lines)"),
        (10000, "Large (10,000 lines)"),
        (50000, "Very Large (50,000 lines)"),
    ]

    print(
        f"\n{'Document Size':<30} {'Save (ms)':>12} {'Load (ms)':>12} {'File Size (KB)':>15}"
    )
    print("-" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        for num_lines, label in test_sizes:
            # Generate test document
            doc_content = generate_test_document(num_lines)
            file_path = Path(tmpdir) / f"test_{num_lines}.adoc"

            # Measure SAVE
            start_time = time.perf_counter()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(doc_content)
            save_time = (time.perf_counter() - start_time) * 1000

            file_size_kb = file_path.stat().st_size / 1024

            # Measure LOAD
            start_time = time.perf_counter()
            with open(file_path, "r", encoding="utf-8") as f:
                f.read()
            load_time = (time.perf_counter() - start_time) * 1000

            results.append(
                {
                    "size": label,
                    "num_lines": num_lines,
                    "save_ms": save_time,
                    "load_ms": load_time,
                    "file_size_kb": file_size_kb,
                }
            )

            print(
                f"{label:<30} {save_time:>12.2f} {load_time:>12.2f} {file_size_kb:>15.2f}"
            )

    print()
    return results


def profile_memory_usage():
    """Profile memory usage patterns."""
    print("=" * 80)
    print("PROFILING MEMORY USAGE")
    print("=" * 80)

    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024

    print(f"\nInitial Memory: {initial_memory:.2f} MB")

    # Test memory with different document sizes
    test_sizes = [100, 1000, 5000, 10000]
    documents = {}

    print(f"\n{'Operation':<40} {'Memory (MB)':>12} {'Delta (MB)':>12}")
    print("-" * 80)

    last_memory = initial_memory

    for size in test_sizes:
        doc = generate_test_document(size)
        documents[size] = doc

        current_memory = process.memory_info().rss / 1024 / 1024
        delta = current_memory - last_memory

        print(
            f"Generated {size} line document{'':<17} {current_memory:>12.2f} {delta:>12.2f}"
        )
        last_memory = current_memory

    # Test memory with conversion (if available)
    if ASCIIDOC_AVAILABLE:
        asciidoc_api = AsciiDoc3API()
        asciidoc_api.options("--no-header-footer")

        for size in [100, 1000, 5000]:
            infile = io.StringIO(documents[size])
            outfile = io.StringIO()

            asciidoc_api.execute(infile, outfile, backend="html5")
            outfile.getvalue()

            current_memory = process.memory_info().rss / 1024 / 1024
            delta = current_memory - last_memory

            print(
                f"Converted {size} line document{'':<17} {current_memory:>12.2f} {delta:>12.2f}"
            )
            last_memory = current_memory

    # Cleanup and measure
    documents.clear()
    import gc

    gc.collect()

    final_memory = process.memory_info().rss / 1024 / 1024
    delta = final_memory - last_memory

    print(f"After cleanup (gc.collect()){'':<18} {final_memory:>12.2f} {delta:>12.2f}")

    print(f"\nPeak Memory: {final_memory:.2f} MB")
    print(f"Total Growth: {final_memory - initial_memory:.2f} MB")
    print()


def analyze_results(conversion_results, io_results):
    """Analyze results and provide recommendations."""
    print("=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)

    if conversion_results:
        print("\n### AsciiDoc Conversion Performance")
        print()

        # Find slowest conversion
        slowest = max(conversion_results, key=lambda x: x["time_ms"])
        fastest = min(conversion_results, key=lambda x: x["time_ms"])

        print(f"Fastest: {fastest['size']} - {fastest['time_ms']:.2f}ms")
        print(f"Slowest: {slowest['size']} - {slowest['time_ms']:.2f}ms")

        # Check against targets
        medium_doc = next(
            (r for r in conversion_results if r["num_lines"] == 1000), None
        )
        if medium_doc and medium_doc["time_ms"] > 200:
            print(
                f"\n⚠️  1000-line conversion ({medium_doc['time_ms']:.2f}ms) exceeds 200ms target"
            )
            print("   Recommendation: Implement caching, optimize AsciiDoc settings")
        else:
            print("\n✅ 1000-line conversion meets target (< 200ms)")

    if io_results:
        print("\n### File I/O Performance")
        print()

        # Find slowest operations
        slowest_save = max(io_results, key=lambda x: x["save_ms"])
        slowest_load = max(io_results, key=lambda x: x["load_ms"])

        print(f"Slowest Save: {slowest_save['size']} - {slowest_save['save_ms']:.2f}ms")
        print(f"Slowest Load: {slowest_load['size']} - {slowest_load['load_ms']:.2f}ms")

        # Estimate 1MB performance
        large_doc = next((r for r in io_results if r["num_lines"] == 10000), None)
        if large_doc:
            # Extrapolate to 1MB (rough estimate)
            mb_size = large_doc["file_size_kb"] / 1024
            save_per_mb = large_doc["save_ms"] / mb_size
            load_per_mb = large_doc["load_ms"] / mb_size

            print("\nEstimated 1MB file performance:")
            print(f"  Save: {save_per_mb:.2f}ms/MB")
            print(f"  Load: {load_per_mb:.2f}ms/MB")

            if save_per_mb > 100 or load_per_mb > 100:
                print("  ⚠️  May exceed 100ms target for 1MB files")
            else:
                print("  ✅ Likely to meet 100ms target for 1MB files")

    print()


def main():
    """Run all runtime profiling tests."""
    print("\n" + "=" * 80)
    print("ASCIIDOC ARTISAN - RUNTIME PERFORMANCE PROFILING")
    print("=" * 80)

    process = psutil.Process()
    print(f"\nPython: {sys.version}")
    print(f"Process PID: {process.pid}")
    print(f"Initial Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")

    # Run profiling tests
    conversion_results = profile_asciidoc_conversion()
    io_results = profile_file_operations()
    profile_memory_usage()

    # Analyze
    analyze_results(conversion_results, io_results)

    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    print("\n### High Priority Optimizations")
    print()
    print("1. **Preview Caching**")
    print("   - Cache HTML output for unchanged content")
    print("   - Implement LRU cache with size limit")
    print("   - Clear cache on document modification")
    print()
    print("2. **Incremental Rendering**")
    print("   - Only re-render changed sections")
    print("   - Use diff algorithm for content updates")
    print("   - Maintain AST for faster updates")
    print()
    print("3. **Debouncing**")
    print("   - Adaptive debounce delay based on document size")
    print("   - Cancel pending renders on new input")
    print("   - Show 'rendering...' indicator for long operations")
    print()

    print("✅ Runtime profiling complete!")
    print()


if __name__ == "__main__":
    main()
