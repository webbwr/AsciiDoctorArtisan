#!/usr/bin/env python3
"""
Benchmark Predictive Rendering Performance (v1.6.0 Task 3)

Measures the performance improvement from predictive rendering by:
- Simulating editing sessions with and without prediction
- Measuring cache hit rates
- Calculating perceived latency reduction
- Testing different editing patterns (sequential, random, localized)

Target: 30-50% reduction in perceived preview latency
"""

# Add src to path
import sys
import time
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC_AVAILABLE = True
except ImportError:
    ASCIIDOC_AVAILABLE = False
    print("⚠️  asciidoc3 not available - install to run benchmarks")
    sys.exit(1)

from asciidoc_artisan.workers.incremental_renderer import (
    DocumentBlockSplitter,
    IncrementalPreviewRenderer,
)
from asciidoc_artisan.workers.predictive_renderer import (
    PredictivePreviewRenderer,
)


def generate_test_document(sections: int, lines_per_section: int = 20) -> str:
    """Generate a test AsciiDoc document."""
    lines = ["= Test Document", "", ":author: Test Author", "", ""]

    for i in range(sections):
        lines.append(f"== Section {i + 1}")
        lines.append("")
        for j in range(lines_per_section):
            lines.append(f"This is line {j + 1} of section {i + 1}.")
            if j % 5 == 4:
                lines.append("")  # Paragraph break

    return "\n".join(lines)


def simulate_edit(text: str, section_index: int, new_content: str) -> str:
    """Simulate editing a specific section."""
    lines = text.split("\n")
    section_count = 0

    for i, line in enumerate(lines):
        if line.startswith("== Section"):
            if section_count == section_index:
                # Insert new content after section heading
                lines.insert(i + 2, new_content)
                break
            section_count += 1

    return "\n".join(lines)


class BenchmarkRunner:
    """Run predictive rendering benchmarks."""

    def __init__(self):
        """Initialize benchmark runner."""
        self.asciidoc_api = None
        self.incremental_renderer = None
        self.predictive_renderer = None

        if ASCIIDOC_AVAILABLE:
            self._init_asciidoc()

    def _init_asciidoc(self):
        """Initialize AsciiDoc API."""
        self.asciidoc_api = AsciiDoc3API(asciidoc3.__file__)
        self.asciidoc_api.options("--no-header-footer")
        self.asciidoc_api.attributes["icons"] = "font"

        self.incremental_renderer = IncrementalPreviewRenderer(self.asciidoc_api)
        self.predictive_renderer = PredictivePreviewRenderer(self.incremental_renderer)

    def benchmark_without_prediction(
        self, text: str, edit_sequence: List[Tuple[int, str]], iterations: int = 10
    ) -> dict:
        """Benchmark rendering without predictive pre-rendering."""
        self.incremental_renderer.cache.clear()
        self.incremental_renderer.previous_blocks = []

        times = []

        for _ in range(iterations):
            current_text = text

            for section_idx, new_content in edit_sequence:
                # Simulate edit
                current_text = simulate_edit(current_text, section_idx, new_content)

                # Measure render time (no pre-rendering)
                start = time.perf_counter()
                self.incremental_renderer.render(current_text)
                duration = time.perf_counter() - start

                times.append(duration * 1000)  # Convert to ms

        cache_stats = self.incremental_renderer.cache.get_stats()

        return {
            "times_ms": times,
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "cache_hit_rate": cache_stats.get("hit_rate", 0.0),
        }

    def benchmark_with_prediction(self, text: str, edit_sequence: List[Tuple[int, str]], iterations: int = 10) -> dict:
        """Benchmark rendering with predictive pre-rendering."""
        self.incremental_renderer.cache.clear()
        self.incremental_renderer.previous_blocks = []
        self.predictive_renderer.predictor.reset_statistics()

        times = []

        for _ in range(iterations):
            current_text = text

            for section_idx, new_content in edit_sequence:
                # Simulate cursor at section being edited
                blocks = DocumentBlockSplitter.split(current_text)

                # Pre-render predicted blocks
                if blocks:
                    self.predictive_renderer.request_prediction(total_blocks=len(blocks), current_block=section_idx)

                    # Pre-render up to 3 blocks
                    for _ in range(3):
                        block_idx = self.predictive_renderer.get_next_prerender_block()
                        if block_idx is not None and block_idx < len(blocks):
                            block = blocks[block_idx]
                            rendered = self.incremental_renderer._render_block(block)
                            self.incremental_renderer.cache.put(block.id, rendered)

                # Simulate edit
                current_text = simulate_edit(current_text, section_idx, new_content)

                # Measure render time (with pre-cached blocks)
                start = time.perf_counter()
                self.incremental_renderer.render(current_text)
                duration = time.perf_counter() - start

                times.append(duration * 1000)  # Convert to ms

        cache_stats = self.incremental_renderer.cache.get_stats()
        pred_stats = self.predictive_renderer.get_statistics()

        return {
            "times_ms": times,
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "cache_hit_rate": cache_stats.get("hit_rate", 0.0),
            "prediction_hit_rate": pred_stats.get("hit_rate", 0.0),
            "predictions_made": pred_stats.get("predictions_made", 0),
        }

    def run_benchmarks(self):
        """Run all benchmarks."""
        print("=" * 70)
        print("Predictive Rendering Performance Benchmark (v1.6.0)")
        print("=" * 70)
        print()

        # Test scenarios
        scenarios = [
            {
                "name": "Sequential Editing (10 sections)",
                "doc_sections": 10,
                "edit_sequence": [(i, f"NEW CONTENT {i}") for i in range(5)],
            },
            {
                "name": "Random Editing (20 sections)",
                "doc_sections": 20,
                "edit_sequence": [
                    (3, "EDIT 1"),
                    (12, "EDIT 2"),
                    (7, "EDIT 3"),
                    (15, "EDIT 4"),
                    (1, "EDIT 5"),
                ],
            },
            {
                "name": "Localized Editing (30 sections)",
                "doc_sections": 30,
                "edit_sequence": [
                    (10, "EDIT A"),
                    (11, "EDIT B"),
                    (10, "EDIT C"),
                    (12, "EDIT D"),
                    (11, "EDIT E"),
                ],
            },
        ]

        for scenario in scenarios:
            print(f"\n{'─' * 70}")
            print(f"Scenario: {scenario['name']}")
            print(f"{'─' * 70}")

            doc = generate_test_document(scenario["doc_sections"])
            edit_seq = scenario["edit_sequence"]

            print(f"Document: {scenario['doc_sections']} sections")
            print(f"Edit sequence: {len(edit_seq)} edits")
            print()

            # Benchmark without prediction
            print("⏱️  Running without predictive rendering...")
            without = self.benchmark_without_prediction(doc, edit_seq)

            # Benchmark with prediction
            print("⏱️  Running with predictive rendering...")
            with_pred = self.benchmark_with_prediction(doc, edit_seq)

            # Calculate improvement
            improvement = (without["avg_ms"] - with_pred["avg_ms"]) / without["avg_ms"] * 100

            # Display results
            print()
            print("Results:")
            print("  Without Prediction:")
            print(f"    Average: {without['avg_ms']:.3f}ms")
            print(f"    Min:     {without['min_ms']:.3f}ms")
            print(f"    Max:     {without['max_ms']:.3f}ms")
            print(f"    Cache Hit Rate: {without['cache_hit_rate']:.1f}%")
            print()
            print("  With Prediction:")
            print(f"    Average: {with_pred['avg_ms']:.3f}ms")
            print(f"    Min:     {with_pred['min_ms']:.3f}ms")
            print(f"    Max:     {with_pred['max_ms']:.3f}ms")
            print(f"    Cache Hit Rate: {with_pred['cache_hit_rate']:.1f}%")
            print(f"    Prediction Hit Rate: {with_pred['prediction_hit_rate'] * 100:.1f}%")
            print(f"    Predictions Made: {with_pred['predictions_made']}")
            print()
            print(f"  ✨ Latency Improvement: {improvement:.1f}%")

            if improvement >= 30:
                print("  ✅ Target achieved! (≥30% reduction)")
            else:
                print("  ⚠️  Below target (30-50% expected)")

        print()
        print("=" * 70)
        print("Benchmark Complete")
        print("=" * 70)


def main():
    """Run benchmarks."""
    if not ASCIIDOC_AVAILABLE:
        return

    runner = BenchmarkRunner()
    runner.run_benchmarks()


if __name__ == "__main__":
    main()
