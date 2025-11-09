"""
Profile block detection performance.

Measures the performance of the current block detection algorithm
to establish a baseline before optimization.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from asciidoc_artisan.workers.incremental_renderer import DocumentBlockSplitter


def generate_test_document(sections: int, lines_per_section: int) -> str:
    """Generate a test AsciiDoc document."""
    lines = []
    lines.append("= Test Document\n\n")

    for i in range(sections):
        lines.append(f"== Section {i}\n\n")

        for j in range(lines_per_section):
            lines.append(f"This is line {j} of section {i}. " * 10)
            lines.append("\n")

        lines.append("\n")

    return "".join(lines)


def profile_block_detection(iterations: int = 100):
    """Profile block detection performance."""
    print("=" * 60)
    print("Block Detection Performance Profiling")
    print("=" * 60)

    # Test cases
    test_cases = [
        (10, 10, "Small document (10 sections, 10 lines each)"),
        (50, 20, "Medium document (50 sections, 20 lines each)"),
        (100, 50, "Large document (100 sections, 50 lines each)"),
        (500, 10, "Many sections (500 sections, 10 lines each)"),
    ]

    results = []

    for sections, lines_per_section, description in test_cases:
        print(f"\n{description}")
        print("-" * 60)

        # Generate test document
        doc = generate_test_document(sections, lines_per_section)
        doc_size = len(doc)
        doc_lines = doc.count("\n")

        print(f"Document size: {doc_size:,} characters")
        print(f"Document lines: {doc_lines:,}")

        # Warm up
        DocumentBlockSplitter.split(doc)

        # Profile
        start = time.perf_counter()
        for _ in range(iterations):
            blocks = DocumentBlockSplitter.split(doc)
        duration = time.perf_counter() - start

        avg_time_ms = (duration / iterations) * 1000
        blocks_found = len(blocks)
        throughput_kb_per_sec = (doc_size * iterations / 1024) / duration

        print(f"Blocks found: {blocks_found}")
        print(f"Average time: {avg_time_ms:.3f} ms")
        print(f"Throughput: {throughput_kb_per_sec:.1f} KB/s")
        print(f"Lines/sec: {(doc_lines * iterations / duration):.0f}")

        results.append(
            {
                "description": description,
                "sections": sections,
                "doc_size": doc_size,
                "doc_lines": doc_lines,
                "blocks": blocks_found,
                "avg_time_ms": avg_time_ms,
                "throughput_kb_s": throughput_kb_per_sec,
            }
        )

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for result in results:
        print(f"\n{result['description']}")
        print(f"  Time: {result['avg_time_ms']:.3f} ms")
        print(f"  Throughput: {result['throughput_kb_s']:.1f} KB/s")

    # Baseline metrics
    print("\n" + "=" * 60)
    print("Baseline Metrics (for optimization target)")
    print("=" * 60)

    medium_result = results[1]  # Medium document
    print("Medium document (50 sections, 20 lines each):")
    print(f"  Current: {medium_result['avg_time_ms']:.3f} ms")
    print(f"  Target (20% improvement): {medium_result['avg_time_ms'] * 0.8:.3f} ms")
    print(f"  Target (30% improvement): {medium_result['avg_time_ms'] * 0.7:.3f} ms")


if __name__ == "__main__":
    profile_block_detection(iterations=100)
