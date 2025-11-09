#!/usr/bin/env python3
"""
Profile import times for AsciiDoc Artisan modules.

Identifies heavy imports and optimization opportunities.
"""

import importlib
import sys
import time
from pathlib import Path
from typing import List, Tuple


def profile_import(module_name: str) -> Tuple[str, float]:
    """Profile a single module import time."""
    start = time.perf_counter()
    try:
        importlib.import_module(module_name)
        elapsed = time.perf_counter() - start
        return (module_name, elapsed)
    except ImportError:
        return (module_name, -1.0)  # Failed import


def main() -> None:
    """Profile all AsciiDoc Artisan module imports."""
    # Add src to path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    # Modules to profile (in order of import)
    modules = [
        # Core modules
        "asciidoc_artisan.core.constants",
        "asciidoc_artisan.core.settings",
        "asciidoc_artisan.core.models",
        "asciidoc_artisan.core.file_operations",
        "asciidoc_artisan.core.gpu_detection",
        "asciidoc_artisan.core.lazy_importer",
        "asciidoc_artisan.core.async_file_handler",
        # Workers
        "asciidoc_artisan.workers.git_worker",
        "asciidoc_artisan.workers.pandoc_worker",
        "asciidoc_artisan.workers.preview_worker",
        "asciidoc_artisan.workers.ollama_chat_worker",
        "asciidoc_artisan.workers.github_cli_worker",
        # UI components
        "asciidoc_artisan.ui.theme_manager",
        "asciidoc_artisan.ui.status_manager",
        "asciidoc_artisan.ui.menu_manager",
        "asciidoc_artisan.ui.file_handler",
        "asciidoc_artisan.ui.git_handler",
        "asciidoc_artisan.ui.github_handler",
        "asciidoc_artisan.ui.preview_handler_gpu",
        "asciidoc_artisan.ui.chat_manager",
        "asciidoc_artisan.ui.main_window",
        # Heavy external dependencies
        "PySide6.QtCore",
        "PySide6.QtWidgets",
        "PySide6.QtWebEngineWidgets",
        "asciidoc3",
        "pypandoc",
        "fitz",  # PyMuPDF
    ]

    print("=" * 70)
    print("Import Time Profiling - AsciiDoc Artisan")
    print("=" * 70)
    print()

    results: List[Tuple[str, float]] = []

    for module in modules:
        module_name, elapsed = profile_import(module)
        results.append((module_name, elapsed))

        if elapsed < 0:
            status = "FAILED"
        elif elapsed < 0.010:
            status = "⚡ FAST"
        elif elapsed < 0.050:
            status = "✓ OK"
        elif elapsed < 0.200:
            status = "⚠ SLOW"
        else:
            status = "❌ HEAVY"

        if elapsed >= 0:
            print(f"{status:10} {elapsed:6.3f}s  {module_name}")
        else:
            print(f"{status:10} {'---':>6}  {module_name}")

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)

    successful = [(m, t) for m, t in results if t >= 0]
    if successful:
        total_time = sum(t for _, t in successful)
        heavy_imports = [(m, t) for m, t in successful if t >= 0.200]
        slow_imports = [(m, t) for m, t in successful if 0.050 <= t < 0.200]

        print(f"Total import time: {total_time:.3f}s")
        print(f"Modules profiled: {len(successful)}/{len(modules)}")
        print()

        if heavy_imports:
            print(f"Heavy imports (≥200ms): {len(heavy_imports)}")
            for module, elapsed in sorted(heavy_imports, key=lambda x: -x[1]):
                print(f"  {elapsed:6.3f}s  {module}")
            print()

        if slow_imports:
            print(f"Slow imports (50-200ms): {len(slow_imports)}")
            for module, elapsed in sorted(slow_imports, key=lambda x: -x[1]):
                print(f"  {elapsed:6.3f}s  {module}")
            print()

        # Recommendations
        print("Optimization Opportunities:")
        print()

        if heavy_imports:
            print("1. Heavy Imports - Consider lazy loading:")
            for module, _ in heavy_imports[:3]:
                print(f"   - {module}")
            print()

        if slow_imports:
            print("2. Slow Imports - Review for optimization:")
            for module, _ in slow_imports[:3]:
                print(f"   - {module}")
            print()

        # Check current lazy loading status
        print("3. Current Lazy Loading:")
        lazy_modules = [
            "asciidoc_artisan.workers.pandoc_worker",
            "asciidoc_artisan.workers.preview_worker",
            "asciidoc_artisan.ui.preview_handler_gpu",
        ]
        for module in lazy_modules:
            status = "✓" if module in [m for m, _ in successful] else "✗"
            print(f"   {status} {module}")


if __name__ == "__main__":
    main()
