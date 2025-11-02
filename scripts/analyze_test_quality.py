#!/usr/bin/env python3
"""
Analyze test quality by counting assertions per test.

Identifies weak tests with 0-1 assertions that might need strengthening or removal.
"""

import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"

def count_assertions_in_test(test_content):
    """Count assertion statements in a test function."""
    # Count different types of assertions
    assert_patterns = [
        r'\bassert\s+',  # Standard assert
        r'\.assert',     # Method assertions (e.g., mock.assert_called)
        r'pytest\.raises', # Exception assertions
        r'pytest\.warns',  # Warning assertions
    ]

    count = 0
    for pattern in assert_patterns:
        count += len(re.findall(pattern, test_content))

    return count

def extract_tests(file_path):
    """Extract test functions from a file."""
    content = file_path.read_text()

    # Match test functions (including decorators)
    test_pattern = r'((?:@[^\n]+\n)*\s*def\s+test_\w+\([^)]*\):(?:[^d]|d(?!ef\s))*?)(?=\n\s*(?:def\s|class\s|@pytest|$))'
    tests = re.findall(test_pattern, content, re.MULTILINE | re.DOTALL)

    results = []
    for test_code in tests:
        # Extract test name
        name_match = re.search(r'def\s+(test_\w+)', test_code)
        if not name_match:
            continue

        test_name = name_match.group(1)
        assertion_count = count_assertions_in_test(test_code)

        results.append({
            'name': test_name,
            'assertions': assertion_count,
            'code': test_code[:200]  # First 200 chars for preview
        })

    return results

def main():
    print("=" * 80)
    print("Test Quality Analysis - Phase 4")
    print("=" * 80)

    # Find all test files
    test_files = list(TESTS_DIR.rglob("test_*.py"))
    print(f"\nAnalyzing {len(test_files)} test files...")

    # Analyze each file
    weak_tests = []
    stats = defaultdict(int)

    for test_file in test_files:
        tests = extract_tests(test_file)

        for test in tests:
            assertion_count = test['assertions']
            stats[assertion_count] += 1

            if assertion_count <= 1:
                weak_tests.append({
                    'file': str(test_file.relative_to(PROJECT_ROOT)),
                    'name': test['name'],
                    'assertions': assertion_count,
                    'preview': test['code']
                })

    # Print statistics
    print("\n" + "=" * 80)
    print("Assertion Count Distribution")
    print("=" * 80)
    for count in sorted(stats.keys()):
        print(f"{count:2d} assertions: {stats[count]:4d} tests")

    # Print weak tests
    print("\n" + "=" * 80)
    print(f"Weak Tests (0-1 assertions): {len(weak_tests)} tests")
    print("=" * 80)

    # Group by file
    by_file = defaultdict(list)
    for test in weak_tests:
        by_file[test['file']].append(test)

    # Print top 10 files with most weak tests
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)

    print(f"\nTop 10 files with weak tests:")
    for i, (file_path, tests) in enumerate(sorted_files[:10], 1):
        print(f"\n{i}. {file_path} ({len(tests)} weak tests)")
        for test in tests[:3]:  # Show first 3
            print(f"   - {test['name']} ({test['assertions']} assertions)")

    # Print overall summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    total_tests = sum(stats.values())
    weak_count = stats[0] + stats[1]
    weak_pct = (weak_count / total_tests * 100) if total_tests > 0 else 0

    print(f"Total tests analyzed: {total_tests}")
    print(f"Tests with 0 assertions: {stats[0]}")
    print(f"Tests with 1 assertion: {stats[1]}")
    print(f"Weak tests (0-1): {weak_count} ({weak_pct:.1f}%)")
    print(f"Strong tests (2+): {total_tests - weak_count} ({100-weak_pct:.1f}%)")

    print("\nRecommendation:")
    if weak_pct < 5:
        print("✅ Test quality is EXCELLENT. Very few weak tests.")
    elif weak_pct < 10:
        print("✅ Test quality is GOOD. Some weak tests could be strengthened.")
    elif weak_pct < 20:
        print("⚠️  Test quality is FAIR. Many weak tests need attention.")
    else:
        print("❌ Test quality needs improvement. Too many weak tests.")

if __name__ == "__main__":
    main()
