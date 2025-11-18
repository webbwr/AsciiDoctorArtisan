"""
Profile file I/O performance for AsciiDoc Artisan.

This script measures:
- File read/write performance
- Performance with various document sizes
- Memory usage during file operations

Usage:
    python tests/performance/profile_fileio.py
"""

import sys
import tempfile
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import psutil


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


def profile_file_operations():
    """Profile file load and save operations."""
    print("=" * 80)
    print("FILE I/O PERFORMANCE PROFILING")
    print("=" * 80)

    process = psutil.Process()
    results = []

    test_sizes = [
        (100, "Small (100 lines)"),
        (1000, "Medium (1,000 lines)"),
        (10000, "Large (10,000 lines)"),
        (50000, "Very Large (50,000 lines)"),
        (100000, "Huge (100,000 lines)"),
    ]

    print(f"\n{'Document Size':<30} {'Write (ms)':>12} {'Read (ms)':>12} {'Size (KB)':>12}")
    print("-" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        for num_lines, label in test_sizes:
            # Generate test document
            doc_content = generate_test_document(num_lines)
            file_path = Path(tmpdir) / f"test_{num_lines}.adoc"

            # Measure WRITE
            start_memory = process.memory_info().rss / 1024 / 1024
            start_time = time.perf_counter()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(doc_content)

            write_time = (time.perf_counter() - start_time) * 1000
            end_memory = process.memory_info().rss / 1024 / 1024

            file_size_kb = file_path.stat().st_size / 1024

            # Measure READ
            start_time = time.perf_counter()

            with open(file_path, "r", encoding="utf-8") as f:
                loaded_content = f.read()

            read_time = (time.perf_counter() - start_time) * 1000

            # Verify content
            assert len(loaded_content) == len(doc_content), "Content mismatch!"

            results.append(
                {
                    "size": label,
                    "num_lines": num_lines,
                    "write_ms": write_time,
                    "read_ms": read_time,
                    "file_size_kb": file_size_kb,
                    "memory_delta_mb": end_memory - start_memory,
                }
            )

            print(f"{label:<30} {write_time:>12.2f} {read_time:>12.2f} {file_size_kb:>12.2f}")

    print()
    return results


def analyze_results(results):
    """Analyze results and provide recommendations."""
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    # Find slowest operations
    slowest_write = max(results, key=lambda x: x["write_ms"])
    slowest_read = max(results, key=lambda x: x["read_ms"])

    fastest_write = min(results, key=lambda x: x["write_ms"])
    fastest_read = min(results, key=lambda x: x["read_ms"])

    print("\n### Write Performance")
    print(f"Fastest: {fastest_write['size']} - {fastest_write['write_ms']:.2f}ms")
    print(f"Slowest: {slowest_write['size']} - {slowest_write['write_ms']:.2f}ms")

    print("\n### Read Performance")
    print(f"Fastest: {fastest_read['size']} - {fastest_read['read_ms']:.2f}ms")
    print(f"Slowest: {slowest_read['size']} - {slowest_read['read_ms']:.2f}ms")

    # Calculate throughput for largest file
    largest = results[-1]
    write_mbps = (largest["file_size_kb"] / 1024) / (largest["write_ms"] / 1000)
    read_mbps = (largest["file_size_kb"] / 1024) / (largest["read_ms"] / 1000)

    print(f"\n### Throughput (largest file: {largest['file_size_kb']:.2f} KB)")
    print(f"Write: {write_mbps:.2f} MB/s")
    print(f"Read: {read_mbps:.2f} MB/s")

    # Estimate 1MB performance
    # Find a medium-large file to extrapolate from
    large_file = next((r for r in results if r["num_lines"] >= 10000), results[-1])
    mb_size = large_file["file_size_kb"] / 1024

    if mb_size > 0:
        write_per_mb = large_file["write_ms"] / mb_size
        read_per_mb = large_file["read_ms"] / mb_size

        print("\n### Estimated 1MB File Performance")
        print(f"Write: {write_per_mb:.2f}ms")
        print(f"Read: {read_per_mb:.2f}ms")

        # Check against target
        if write_per_mb > 100:
            print("  ⚠️  Write may exceed 100ms target for 1MB files")
            print("     Recommendation: Use async I/O, implement write buffering")
        else:
            print("  ✅ Write performance meets 100ms target")

        if read_per_mb > 100:
            print("  ⚠️  Read may exceed 100ms target for 1MB files")
            print("     Recommendation: Use async I/O, implement read caching")
        else:
            print("  ✅ Read performance meets 100ms target")

    print()


def main():
    """Run file I/O profiling."""
    print("\n" + "=" * 80)
    print("ASCIIDOC ARTISAN - FILE I/O PERFORMANCE PROFILING")
    print("=" * 80)

    process = psutil.Process()
    print(f"\nPython: {sys.version}")
    print(f"Process PID: {process.pid}")
    print(f"Initial Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB\n")

    # Run profiling
    results = profile_file_operations()

    # Analyze
    analyze_results(results)

    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    print("\n### High Priority Optimizations")
    print()
    print("1. **Async File Operations**")
    print("   - Use QThreadPool for file I/O")
    print("   - Don't block UI thread during load/save")
    print("   - Show progress indicator for large files")
    print()
    print("2. **File Watching**")
    print("   - Use QFileSystemWatcher efficiently")
    print("   - Debounce external file changes")
    print("   - Reload only when necessary")
    print()
    print("3. **Large File Handling**")
    print("   - Stream large files instead of loading entirely")
    print("   - Implement chunked reading for preview")
    print("   - Warn user for files > 10MB")
    print()

    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"\nFinal Memory: {final_memory:.2f} MB")
    print(f"Memory Growth: {final_memory - 14.5:.2f} MB")

    print("\n✅ File I/O profiling complete!")
    print()


if __name__ == "__main__":
    main()
