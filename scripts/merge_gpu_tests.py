#!/usr/bin/env python3
"""
Script to merge GPU test files for Phase 3 Task 3.1.

Merges test_gpu_cache.py and test_hardware_detection.py into test_gpu_detection.py.
"""

import re
from pathlib import Path

# Define project root
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "unit" / "core"

# Files
BASE_FILE = TESTS_DIR / "test_gpu_detection.py"
CACHE_FILE = TESTS_DIR / "test_gpu_cache.py"
HARDWARE_FILE = TESTS_DIR / "test_hardware_detection.py"

# Tests to skip (duplicates already in base file)
SKIP_TESTS = {
    "test_cache_entry_creation",
    "test_cache_entry_to_gpu_info",
    "test_get_gpu_info_force_redetect",
}


def extract_fixtures(content):
    """Extract fixture definitions from file content."""
    fixture_pattern = r"@pytest\.fixture[^\n]*\ndef\s+(\w+)\([^)]*\):[^@]+"
    fixtures = re.findall(fixture_pattern, content, re.MULTILINE | re.DOTALL)
    return fixtures


def extract_tests(content):
    """Extract test function definitions."""
    # Match test functions
    test_pattern = r"((?:@pytest\.mark\.[^\n]+\n)*def\s+test_\w+\([^)]*\):(?:[^d]|d(?!ef\s))*?)(?=\n(?:def\s|class\s|$))"
    tests = re.findall(test_pattern, content, re.MULTILINE | re.DOTALL)
    return tests


def extract_test_classes(content):
    """Extract test class definitions."""
    class_pattern = r"(class\s+Test\w+:[^c]*?)(?=\nclass\s|\Z)"
    classes = re.findall(class_pattern, content, re.MULTILINE | re.DOTALL)
    return classes


def get_test_name(test_def):
    """Extract test name from test definition."""
    match = re.search(r"def\s+(test_\w+)\(", test_def)
    return match.group(1) if match else None


def main():
    print("=" * 70)
    print("GPU Test Files Consolidation - Phase 3 Task 3.1")
    print("=" * 70)

    # Read base file
    print("\n1. Reading base file (test_gpu_detection.py)...")
    base_content = BASE_FILE.read_text()
    print(
        f"   Base file: {len(base_content)} characters, {base_content.count('def test_')} tests"
    )

    # Read cache file
    print("\n2. Reading cache file (test_gpu_cache.py)...")
    cache_content = CACHE_FILE.read_text()
    cache_tests = extract_tests(cache_content)
    cache_fixtures = extract_fixtures(cache_content)
    print(
        f"   Cache file: {len(cache_tests)} test functions, {len(cache_fixtures)} fixtures"
    )

    # Read hardware file
    print("\n3. Reading hardware file (test_hardware_detection.py)...")
    hardware_content = HARDWARE_FILE.read_text()
    hardware_classes = extract_test_classes(hardware_content)
    hardware_fixtures = extract_fixtures(hardware_content)
    print(
        f"   Hardware file: {len(hardware_classes)} test classes, {len(hardware_fixtures)} fixtures"
    )

    # Filter out duplicate tests from cache
    print("\n4. Filtering duplicate tests...")
    unique_cache_tests = []
    skipped = []
    for test in cache_tests:
        test_name = get_test_name(test)
        if test_name in SKIP_TESTS:
            skipped.append(test_name)
            print(f"   Skipping duplicate: {test_name}")
        else:
            unique_cache_tests.append(test)

    print(f"\n   Kept {len(unique_cache_tests)} unique tests from cache file")
    print(f"   Skipped {len(skipped)} duplicates: {', '.join(skipped)}")

    # Analyze what needs to be added
    print("\n5. Analysis Summary:")
    print(f"   - Base file tests: {base_content.count('def test_')}")
    print(f"   - Cache tests to merge: {len(unique_cache_tests)}")
    print(f"   - Hardware classes to merge: {len(hardware_classes)}")
    print(
        f"   - Total after merge: ~{base_content.count('def test_') + len(unique_cache_tests) + sum(c.count('def test_') for c in hardware_classes)}"
    )

    print("\n6. Files identified for manual merge:")
    print(f"   ✓ {BASE_FILE} (base)")
    print(f"   ✓ {CACHE_FILE} (source)")
    print(f"   ✓ {HARDWARE_FILE} (source)")

    print("\n" + "=" * 70)
    print("Manual merge required - files too complex for automatic merge")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Open test_gpu_detection.py in editor")
    print("2. Add mock_cache_file fixture if not present")
    print("3. Merge 13 unique cache tests into appropriate classes")
    print("4. Merge hardware test classes")
    print("5. Run pytest to validate")


if __name__ == "__main__":
    main()
