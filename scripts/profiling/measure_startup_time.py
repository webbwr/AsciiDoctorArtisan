#!/usr/bin/env python3
"""
Measure AsciiDoc Artisan startup time.

Tracks:
- Total application startup
- Import time
- Widget initialization
- First window display

Target (v1.5.0): < 2.0 seconds
Target (v1.6.0): < 1.5 seconds
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def measure_startup():
    """Measure application startup time."""
    print("=" * 70)
    print("AsciiDoc Artisan Startup Time Measurement")
    print("=" * 70)
    print()

    # Overall start
    overall_start = time.perf_counter()

    # Measure import time
    import_start = time.perf_counter()
    try:
        from PySide6.QtWidgets import QApplication

        from asciidoc_artisan.ui.main_window import AsciiDocEditor
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return
    import_time = (time.perf_counter() - import_start) * 1000

    # Measure Qt application init
    qt_start = time.perf_counter()
    app = QApplication.instance() or QApplication(sys.argv)
    qt_time = (time.perf_counter() - qt_start) * 1000

    # Measure main window creation
    window_start = time.perf_counter()
    AsciiDocEditor()
    window_time = (time.perf_counter() - window_start) * 1000

    # Total time
    total_time = (time.perf_counter() - overall_start) * 1000

    # Display results
    print("Startup Time Breakdown:")
    print(f"  Import modules:      {import_time:7.1f}ms")
    print(f"  Qt app init:         {qt_time:7.1f}ms")
    print(f"  Main window create:  {window_time:7.1f}ms")
    print(f"  {'─' * 40}")
    print(f"  Total:               {total_time:7.1f}ms ({total_time / 1000:.2f}s)")
    print()

    # Check against targets
    total_s = total_time / 1000

    print("Performance Targets:")
    print(f"  v1.5.0 target: < 2.0s  {'✅ PASS' if total_s < 2.0 else '❌ FAIL'}")
    print(f"  v1.6.0 target: < 1.5s  {'✅ PASS' if total_s < 1.5 else '⚠️  Not yet'}")
    print()

    # Percentage breakdown
    print("Time Distribution:")
    print(f"  Import:      {import_time / total_time * 100:5.1f}%")
    print(f"  Qt app:      {qt_time / total_time * 100:5.1f}%")
    print(f"  Window:      {window_time / total_time * 100:5.1f}%")
    print()

    print("=" * 70)

    # Don't show window - just exit
    app.quit()
    sys.exit(0)


if __name__ == "__main__":
    measure_startup()
