#!/usr/bin/env python3
"""Analyze test coverage and identify gaps for the 60% → 100% coverage push."""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def load_coverage_data(status_file: Path) -> Dict:
    """Load coverage data from status.json."""
    with open(status_file) as f:
        return json.load(f)


def analyze_file_coverage(file_data: Dict) -> Tuple[str, float, int, int]:
    """Extract coverage metrics from file data."""
    nums = file_data["nums"]
    n_statements = nums["n_statements"]
    n_missing = nums["n_missing"]

    # Calculate coverage percentage
    coverage_pct = 0.0 if n_statements == 0 else ((n_statements - n_missing) / n_statements) * 100

    return file_data["file"], coverage_pct, n_statements, n_missing


def main():
    """Analyze coverage and generate report."""
    project_root = Path(__file__).parent.parent
    status_file = project_root / "htmlcov" / "status.json"

    if not status_file.exists():
        print(f"❌ Coverage report not found: {status_file}")
        print("Run: make test")
        sys.exit(1)

    data = load_coverage_data(status_file)
    files = data.get("files", {})

    # Analyze each file
    coverage_data = []
    total_statements = 0
    total_missing = 0

    for file_key, file_data in files.items():
        if "index" in file_data:
            file_path, cov_pct, stmts, missing = analyze_file_coverage(file_data["index"])
            coverage_data.append((file_path, cov_pct, stmts, missing))
            total_statements += stmts
            total_missing += missing

    # Calculate overall coverage
    overall_coverage = ((total_statements - total_missing) / total_statements) * 100 if total_statements > 0 else 0

    # Sort by coverage (ascending) to prioritize low-coverage files
    coverage_data.sort(key=lambda x: x[1])

    # Generate report
    print("=" * 100)
    print("📊 COVERAGE ANALYSIS - AsciiDoc Artisan Test Coverage Push")
    print("=" * 100)
    print(f"\n🎯 **OVERALL COVERAGE:** {overall_coverage:.1f}% ({total_statements - total_missing}/{total_statements} statements)")
    print(f"   Goal: 100% (need to cover {total_missing} more statements)\n")

    # Priority 1: Files with 0-50% coverage
    print("🔴 **CRITICAL PRIORITY** (0-50% coverage):")
    print("-" * 100)
    critical = [f for f in coverage_data if f[1] < 50]
    if critical:
        for file_path, cov_pct, stmts, missing in critical:
            print(f"   {cov_pct:5.1f}% | {missing:4d} missing | {file_path}")
    else:
        print("   ✅ None!")

    # Priority 2: Files with 50-75% coverage
    print(f"\n⚠️  **HIGH PRIORITY** (50-75% coverage):")
    print("-" * 100)
    high = [f for f in coverage_data if 50 <= f[1] < 75]
    if high:
        for file_path, cov_pct, stmts, missing in high:
            print(f"   {cov_pct:5.1f}% | {missing:4d} missing | {file_path}")
    else:
        print("   ✅ None!")

    # Priority 3: Files with 75-90% coverage
    print(f"\n📋 **MEDIUM PRIORITY** (75-90% coverage):")
    print("-" * 100)
    medium = [f for f in coverage_data if 75 <= f[1] < 90]
    if medium:
        for file_path, cov_pct, stmts, missing in medium[:10]:  # Show top 10
            print(f"   {cov_pct:5.1f}% | {missing:4d} missing | {file_path}")
        if len(medium) > 10:
            print(f"   ... and {len(medium) - 10} more files")
    else:
        print("   ✅ None!")

    # Priority 4: Files with 90-99% coverage
    print(f"\n✅ **LOW PRIORITY** (90-99% coverage):")
    print("-" * 100)
    low = [f for f in coverage_data if 90 <= f[1] < 100]
    print(f"   {len(low)} files need minor improvements")

    # Perfect coverage
    perfect = [f for f in coverage_data if f[1] == 100]
    print(f"\n🎉 **PERFECT COVERAGE** (100%):")
    print("-" * 100)
    print(f"   {len(perfect)} files with 100% coverage!")

    # Summary recommendations
    print("\n" + "=" * 100)
    print("📝 **RECOMMENDATIONS:**")
    print("=" * 100)
    print(f"   1. Start with {len(critical)} CRITICAL files (0-50% coverage)")
    print(f"   2. Then tackle {len(high)} HIGH priority files (50-75% coverage)")
    print(f"   3. Address {len(medium)} MEDIUM priority files (75-90% coverage)")
    print(f"   4. Polish {len(low)} LOW priority files (90-99% coverage)")
    print(f"\n   Total effort: ~{total_missing // 10} test cases needed (assuming ~10 statements per test)")
    print("=" * 100)


if __name__ == "__main__":
    main()
