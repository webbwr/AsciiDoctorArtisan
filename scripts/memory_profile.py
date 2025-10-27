"""
Simple memory profiling for AsciiDoc Artisan.

Measures memory usage for key operations.
"""

import gc
import sys
from pathlib import Path

import psutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def format_bytes(bytes_val):
    """Format bytes as MB."""
    return bytes_val / 1024 / 1024


def profile_operation(name, operation_func):
    """Profile a single operation."""
    process = psutil.Process()

    # Force garbage collection before measurement
    gc.collect()

    # Measure before
    mem_before = process.memory_info().rss

    # Run operation
    result = operation_func()

    # Measure after
    mem_after = process.memory_info().rss

    # Calculate delta
    mem_delta = mem_after - mem_before

    print(
        f"{name:<40} {format_bytes(mem_before):>10.2f} MB -> {format_bytes(mem_after):>10.2f} MB  (Δ {format_bytes(mem_delta):>8.2f} MB)"
    )

    return result


def main():
    """Run memory profiling."""
    print("=" * 100)
    print("MEMORY PROFILING - ASCIIDOC ARTISAN")
    print("=" * 100)

    process = psutil.Process()
    initial_mem = process.memory_info().rss

    print(f"\nInitial Memory: {format_bytes(initial_mem):.2f} MB")
    print(f"\n{'Operation':<40} {'Before':>12} -> {'After':>12}  {'Delta':>15}")
    print("-" * 100)

    # Test 1: Import main modules
    def import_modules():
        return True

    profile_operation("Import main modules", import_modules)

    # Test 2: Generate test content
    def generate_content():
        lines = []
        for i in range(1000):
            lines.append(f"== Section {i}\n")
            lines.append(f"Content for section {i}\n")
            lines.append("\n")
        return "\n".join(lines)

    test_content = profile_operation("Generate 1000-section document", generate_content)

    # Test 3: File operations
    def test_file_ops():
        import tempfile

        from asciidoc_artisan.core.file_operations import atomic_save_text

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".adoc") as f:
            temp_path = Path(f.name)
        atomic_save_text(temp_path, test_content)
        content = temp_path.read_text()
        temp_path.unlink()
        return content

    profile_operation("Write and read 1000-section file", test_file_ops)

    # Test 4: Cleanup
    def cleanup():
        gc.collect()
        return True

    profile_operation("Garbage collection", cleanup)

    # Final stats
    print("-" * 100)
    final_mem = process.memory_info().rss
    total_growth = final_mem - initial_mem

    print(f"\nFinal Memory: {format_bytes(final_mem):.2f} MB")
    print(f"Total Growth: {format_bytes(total_growth):.2f} MB")
    print(f"Growth %: {(total_growth / initial_mem * 100):.1f}%")

    # System-wide memory
    vm = psutil.virtual_memory()
    print("\nSystem Memory:")
    print(f"  Total: {format_bytes(vm.total):.2f} MB")
    print(f"  Available: {format_bytes(vm.available):.2f} MB")
    print(f"  Used: {vm.percent}%")

    print("\n" + "=" * 100)
    print("Memory profiling complete!")
    print("=" * 100)


if __name__ == "__main__":
    main()
