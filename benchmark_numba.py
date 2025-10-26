#!/usr/bin/env python3
"""
Numba JIT Performance Benchmark

Tests the actual speedup from Numba JIT compilation on the hot paths.
"""

import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def benchmark_cell_cleaning():
    """Benchmark cell cleaning with and without JIT."""
    print("\n=== Cell Cleaning Benchmark ===")

    # Test data
    test_cell = "  Test   content\nwith\nmultiple\nnewlines  and   spaces  " * 50
    iterations = 10000

    # Manual version (no JIT)
    def clean_cell_manual(cell: str, max_length: int = 200) -> str:
        """Manual implementation without JIT."""
        if not cell:
            return ""

        cell = cell.replace("\n", " ").replace("\r", " ")

        # Manual space collapse
        cleaned = []
        last_was_space = False
        for char in cell:
            if char == " ":
                if not last_was_space:
                    cleaned.append(char)
                last_was_space = True
            else:
                cleaned.append(char)
                last_was_space = False

        cell = "".join(cleaned).strip()

        if len(cell) > max_length:
            cell = cell[:max_length - 3] + "..."

        return cell

    # Benchmark manual version
    start = time.perf_counter()
    for _ in range(iterations):
        result = clean_cell_manual(test_cell)
    end = time.perf_counter()
    manual_time = (end - start) / iterations * 1000000  # microseconds

    print(f"Manual (no JIT): {manual_time:.2f}µs per cell")

    # Try Numba version
    try:
        from numba import jit

        @jit(nopython=True, cache=True)
        def clean_cell_jit(cell: str, max_length: int = 200) -> str:
            """JIT-compiled version."""
            if not cell or len(cell) == 0:
                return ""

            # Replace newlines
            cell_list = list(cell)
            for i in range(len(cell_list)):
                if cell_list[i] == '\n' or cell_list[i] == '\r':
                    cell_list[i] = ' '

            # Manual space collapse
            cleaned = []
            last_was_space = False
            for char in cell_list:
                if char == ' ':
                    if not last_was_space:
                        cleaned.append(char)
                    last_was_space = True
                else:
                    cleaned.append(char)
                    last_was_space = False

            result = ''.join(cleaned).strip()

            if len(result) > max_length:
                result = result[:max_length - 3] + "..."

            return result

        # Warm up JIT
        _ = clean_cell_jit(test_cell)

        # Benchmark JIT version
        start = time.perf_counter()
        for _ in range(iterations):
            result = clean_cell_jit(test_cell)
        end = time.perf_counter()
        jit_time = (end - start) / iterations * 1000000  # microseconds

        speedup = manual_time / jit_time
        print(f"Numba JIT:       {jit_time:.2f}µs per cell")
        print(f"✓ Speedup:       {speedup:.1f}x faster")

    except ImportError:
        print("✗ Numba not installed")


def benchmark_heading_detection():
    """Benchmark heading detection with and without JIT."""
    print("\n=== Heading Detection Benchmark ===")

    test_lines = [
        "= Title",
        "== Section",
        "=== Subsection",
        "==== Sub-subsection",
        "Regular paragraph",
        "Another line",
    ] * 500
    iterations = 1000

    # Manual version
    def count_leading_equals_manual(line: str) -> int:
        """Manual implementation."""
        if not line or len(line) == 0:
            return 0

        count = 0
        for char in line:
            if char == '=':
                count += 1
            elif char in (' ', '\t'):
                if count > 0:
                    return count
                break
            else:
                break
        return 0

    # Benchmark manual
    start = time.perf_counter()
    for _ in range(iterations):
        for line in test_lines:
            _ = count_leading_equals_manual(line)
    end = time.perf_counter()
    manual_time = (end - start) / iterations * 1000  # milliseconds

    print(f"Manual (no JIT): {manual_time:.2f}ms per {len(test_lines)} lines")

    # Try Numba version
    try:
        from numba import jit

        @jit(nopython=True, cache=True)
        def count_leading_equals_jit(line: str) -> int:
            """JIT-compiled version."""
            if not line or len(line) == 0:
                return 0

            count = 0
            for char in line:
                if char == '=':
                    count += 1
                elif char in (' ', '\t'):
                    if count > 0:
                        return count
                    break
                else:
                    break
            return 0

        # Warm up JIT
        for line in test_lines[:10]:
            _ = count_leading_equals_jit(line)

        # Benchmark JIT
        start = time.perf_counter()
        for _ in range(iterations):
            for line in test_lines:
                _ = count_leading_equals_jit(line)
        end = time.perf_counter()
        jit_time = (end - start) / iterations * 1000  # milliseconds

        speedup = manual_time / jit_time
        print(f"Numba JIT:       {jit_time:.2f}ms per {len(test_lines)} lines")
        print(f"✓ Speedup:       {speedup:.1f}x faster")

    except ImportError:
        print("✗ Numba not installed")


def main():
    """Run all benchmarks."""
    print("="*60)
    print("Numba JIT Performance Benchmark")
    print("="*60)

    try:
        import numba
        print(f"\n✓ Numba version: {numba.__version__}")
    except ImportError:
        print("\n✗ Numba not installed")
        print("  Install with: pip install numba>=0.58.0")
        return

    benchmark_cell_cleaning()
    benchmark_heading_detection()

    print("\n" + "="*60)
    print("Benchmark Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
