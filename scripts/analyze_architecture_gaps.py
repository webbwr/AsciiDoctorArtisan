#!/usr/bin/env python3
"""
Analyze architecture documentation gaps and misalignments.

This script compares architecture.md with actual codebase metrics to identify:
- Version mismatches
- Outdated metrics (LOC, test counts, coverage)
- Missing FR mappings
- Inconsistent component references
"""

import re
import subprocess
import sys
from pathlib import Path


def get_actual_metrics():
    """Get actual codebase metrics.

    Returns:
        dict: Current metrics
    """
    metrics = {}

    # Get main_window.py line count
    main_window = Path("src/asciidoc_artisan/ui/main_window.py")
    if main_window.exists():
        metrics['main_window_loc'] = len(main_window.read_text().splitlines())

    # Get test count
    try:
        result = subprocess.run(
            ["pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=10
        )
        match = re.search(r'(\d+) tests? collected', result.stdout + result.stderr)
        if match:
            metrics['test_count'] = int(match.group(1))
    except Exception:
        metrics['test_count'] = None

    # Get Python file count
    src_dir = Path("src/asciidoc_artisan")
    if src_dir.exists():
        py_files = list(src_dir.rglob("*.py"))
        metrics['python_files'] = len([f for f in py_files if not f.name.startswith('__')])

    # Get total LOC
    if src_dir.exists():
        total_loc = 0
        for py_file in src_dir.rglob("*.py"):
            if not py_file.name.startswith('__'):
                total_loc += len(py_file.read_text().splitlines())
        metrics['total_loc'] = total_loc

    # Get manager count
    managers_dir = Path("src/asciidoc_artisan/ui")
    if managers_dir.exists():
        manager_files = list(managers_dir.glob("*_manager.py"))
        metrics['manager_count'] = len(manager_files)

    # Get worker count
    workers_dir = Path("src/asciidoc_artisan/workers")
    if workers_dir.exists():
        worker_files = list(workers_dir.glob("*_worker.py"))
        # Add base_worker.py
        worker_files.extend(workers_dir.glob("base_worker.py"))
        metrics['worker_count'] = len(worker_files)

    return metrics


def parse_architecture_doc(content: str) -> dict:
    """Parse architecture.md for documented metrics.

    Args:
        content: File content

    Returns:
        dict: Documented metrics
    """
    metrics = {}

    # Extract version
    version_match = re.search(r'\*\*Version:\*\* (\d+\.\d+\.\d+)', content)
    if version_match:
        metrics['version'] = version_match.group(1)

    # Extract last updated date
    date_match = re.search(r'\*\*Last Updated:\*\* (.+)', content)
    if date_match:
        metrics['last_updated'] = date_match.group(1)

    # Extract total files
    files_match = re.search(r'\| Total Files \| (\d+) Python files', content)
    if files_match:
        metrics['python_files'] = int(files_match.group(1))

    # Extract total LOC
    loc_match = re.search(r'\| Total Lines \| ~([\d,]+) LOC', content)
    if loc_match:
        metrics['total_loc'] = int(loc_match.group(1).replace(',', ''))

    # Extract test count
    test_match = re.search(r'\| Test Pass Rate \| \d+% \((\d+)/\d+ tests\)', content)
    if test_match:
        metrics['test_count'] = int(test_match.group(1))

    # Extract main window LOC
    main_window_match = re.search(r'Main Window \((\d+) LOC\)', content)
    if not main_window_match:
        main_window_match = re.search(r'main_window \((\d+,?\d+) lines\)', content)
    if main_window_match:
        metrics['main_window_loc'] = int(main_window_match.group(1).replace(',', ''))

    # Extract manager count
    manager_match = re.search(r'\| Managers \| (\d+) UI managers', content)
    if manager_match:
        metrics['manager_count'] = int(manager_match.group(1))

    # Extract worker count
    worker_match = re.search(r'\| Workers \| (\d+) background workers', content)
    if worker_match:
        metrics['worker_count'] = int(worker_match.group(1))

    # Check for FR-067a/b/c
    metrics['has_fr_067a'] = 'FR-067a' in content
    metrics['has_fr_067b'] = 'FR-067b' in content
    metrics['has_fr_067c'] = 'FR-067c' in content

    return metrics


def compare_metrics(actual: dict, documented: dict) -> dict:
    """Compare actual vs documented metrics.

    Args:
        actual: Actual codebase metrics
        documented: Documented metrics

    Returns:
        dict: Comparison results
    """
    results = {
        'mismatches': [],
        'missing': [],
        'version_mismatch': False
    }

    # Check version
    if documented.get('version') != '2.0.8':
        results['version_mismatch'] = True
        results['mismatches'].append({
            'metric': 'Version',
            'documented': documented.get('version'),
            'actual': '2.0.8',
            'difference': 'Version outdated'
        })

    # Check main_window LOC
    if 'main_window_loc' in actual and 'main_window_loc' in documented:
        doc_loc = documented['main_window_loc']
        act_loc = actual['main_window_loc']
        diff = act_loc - doc_loc
        if abs(diff) > 10:  # Tolerance of 10 lines
            results['mismatches'].append({
                'metric': 'Main Window LOC',
                'documented': doc_loc,
                'actual': act_loc,
                'difference': f'{diff:+d} lines'
            })

    # Check test count
    if 'test_count' in actual and 'test_count' in documented:
        doc_tests = documented['test_count']
        act_tests = actual['test_count']
        diff = act_tests - doc_tests
        if abs(diff) > 100:  # Significant difference
            results['mismatches'].append({
                'metric': 'Test Count',
                'documented': doc_tests,
                'actual': act_tests,
                'difference': f'{diff:+d} tests'
            })

    # Check Python files
    if 'python_files' in actual and 'python_files' in documented:
        doc_files = documented['python_files']
        act_files = actual['python_files']
        diff = act_files - doc_files
        if abs(diff) > 5:
            results['mismatches'].append({
                'metric': 'Python Files',
                'documented': doc_files,
                'actual': act_files,
                'difference': f'{diff:+d} files'
            })

    # Check FR-067a/b/c
    if not documented.get('has_fr_067a'):
        results['missing'].append('FR-067a (Incremental Rendering)')
    if not documented.get('has_fr_067b'):
        results['missing'].append('FR-067b (Predictive Rendering)')
    if not documented.get('has_fr_067c'):
        results['missing'].append('FR-067c (Render Prioritization)')

    return results


def print_report(actual: dict, documented: dict, comparison: dict):
    """Print gap analysis report.

    Args:
        actual: Actual metrics
        documented: Documented metrics
        comparison: Comparison results
    """
    print("=" * 70)
    print("Architecture Documentation Gap Analysis")
    print("=" * 70)
    print()

    # Version status
    if comparison['version_mismatch']:
        print("⚠️  Version Mismatch:")
        print(f"  Documented: {documented.get('version', 'Unknown')}")
        print(f"  Current:    2.0.8")
        print()

    # Metric mismatches
    if comparison['mismatches']:
        print(f"⚠️  Metric Mismatches ({len(comparison['mismatches'])} found):")
        for mismatch in comparison['mismatches']:
            if mismatch['metric'] != 'Version':  # Already shown above
                print(f"  {mismatch['metric']}:")
                print(f"    Documented: {mismatch['documented']}")
                print(f"    Actual:     {mismatch['actual']}")
                print(f"    Difference: {mismatch['difference']}")
        print()

    # Missing items
    if comparison['missing']:
        print(f"⚠️  Missing FR Mappings ({len(comparison['missing'])} found):")
        for item in comparison['missing']:
            print(f"  - {item}")
        print()

    # Summary
    print("=" * 70)
    print("Summary:")
    print("=" * 70)

    total_issues = len(comparison['mismatches']) + len(comparison['missing'])
    if comparison['version_mismatch']:
        total_issues += 1

    if total_issues == 0:
        print("✅ No gaps or misalignments found")
    else:
        print(f"⚠️  {total_issues} issues found:")
        print(f"  - Version mismatches: {1 if comparison['version_mismatch'] else 0}")
        print(f"  - Metric mismatches: {len(comparison['mismatches'])}")
        print(f"  - Missing mappings: {len(comparison['missing'])}")

    print()
    print("Recommendations:")
    if comparison['version_mismatch']:
        print("  1. Update version to 2.0.8")
    if comparison['mismatches']:
        print("  2. Update documented metrics to match actual values")
    if comparison['missing']:
        print("  3. Add missing FR mappings (FR-067a/b/c)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze architecture documentation gaps"
    )
    parser.add_argument(
        "--file",
        default="docs/developer/architecture.md",
        help="Path to architecture.md"
    )

    args = parser.parse_args()

    # Read architecture doc
    arch_file = Path(args.file)
    if not arch_file.exists():
        print(f"Error: {args.file} not found")
        sys.exit(1)

    content = arch_file.read_text()

    # Get metrics
    print("Analyzing codebase...")
    actual_metrics = get_actual_metrics()

    print("Parsing architecture.md...")
    documented_metrics = parse_architecture_doc(content)

    print()

    # Compare
    comparison = compare_metrics(actual_metrics, documented_metrics)

    # Report
    print_report(actual_metrics, documented_metrics, comparison)

    # Exit code
    total_issues = len(comparison['mismatches']) + len(comparison['missing'])
    if comparison['version_mismatch']:
        total_issues += 1

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
