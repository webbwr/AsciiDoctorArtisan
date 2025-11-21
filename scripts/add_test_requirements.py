#!/usr/bin/env python3
"""
Add missing test requirements to SPECIFICATIONS_AI.md.

This script adds test requirements to FRs 085-107 that are missing them.
"""

import re
import sys
from pathlib import Path

# Test requirements for each FR
TEST_REQUIREMENTS = {
    "FR-085": {
        "min_tests": 15,
        "coverage": "90%+",
        "types": [
            "Unit: Context detection (5 tests)",
            "Unit: Provider registration (4 tests)",
            "Integration: Editor integration (4 tests)",
            "Performance: <50ms for 1K completions (2 tests)",
        ],
    },
    "FR-086": {
        "min_tests": 12,
        "coverage": "85%+",
        "types": [
            "Unit: Show/hide popup (4 tests)",
            "Unit: Item navigation (4 tests)",
            "Integration: Editor integration (2 tests)",
            "UI: Arrow keys, Enter, Esc (2 tests)",
        ],
    },
    "FR-087": {
        "min_tests": 10,
        "coverage": "85%+",
        "types": [
            "Unit: Completion types (5 tests)",
            "Unit: Context detection (3 tests)",
            "Integration: Engine integration (2 tests)",
        ],
    },
    "FR-088": {
        "min_tests": 8,
        "coverage": "90%+",
        "types": [
            "Unit: Match algorithm (4 tests)",
            "Unit: Scoring logic (2 tests)",
            "Performance: <10ms for 1K items (2 tests)",
        ],
    },
    "FR-089": {
        "min_tests": 8,
        "coverage": "85%+",
        "types": [
            "Unit: Cache hit/miss (3 tests)",
            "Unit: Cache invalidation (3 tests)",
            "Performance: Cache benefit verification (2 tests)",
        ],
    },
    "FR-090": {
        "min_tests": 6,
        "coverage": "80%+",
        "types": [
            "Unit: Provider registration (3 tests)",
            "Unit: Priority handling (2 tests)",
            "Integration: Engine integration (1 test)",
        ],
    },
    "FR-091": {
        "min_tests": 12,
        "coverage": "90%+",
        "types": [
            "Unit: Validation logic (5 tests)",
            "Unit: Error detection (3 tests)",
            "Integration: Editor integration (2 tests)",
            "Performance: <100ms for 1K lines (2 tests)",
        ],
    },
    "FR-092": {
        "min_tests": 10,
        "coverage": "85%+",
        "types": [
            "Unit: Highlight logic (4 tests)",
            "Unit: Error colors (3 tests)",
            "Integration: Editor integration (2 tests)",
            "UI: Visual indicators (1 test)",
        ],
    },
    "FR-093": {
        "min_tests": 8,
        "coverage": "85%+",
        "types": [
            "Unit: Navigation logic (3 tests)",
            "Unit: Error position tracking (2 tests)",
            "Integration: Editor integration (2 tests)",
            "UI: F8 key handling (1 test)",
        ],
    },
    "FR-094": {
        "min_tests": 10,
        "coverage": "85%+",
        "types": [
            "Unit: Error list management (4 tests)",
            "Unit: Panel show/hide (2 tests)",
            "Integration: Checker integration (2 tests)",
            "UI: Click navigation (2 tests)",
        ],
    },
    "FR-095": {
        "min_tests": 12,
        "coverage": "90%+",
        "types": [
            "Unit: Rule definitions (6 tests)",
            "Unit: Validation logic (4 tests)",
            "Integration: Checker integration (2 tests)",
        ],
    },
    "FR-096": {
        "min_tests": 8,
        "coverage": "80%+",
        "types": [
            "Unit: Fix suggestions (4 tests)",
            "Unit: Fix application (2 tests)",
            "Integration: Editor integration (1 test)",
            "UI: Context menu (1 test)",
        ],
    },
    "FR-097": {
        "min_tests": 6,
        "coverage": "80%+",
        "types": [
            "Unit: Rule enable/disable (3 tests)",
            "Unit: Severity configuration (2 tests)",
            "Integration: Settings persistence (1 test)",
        ],
    },
    "FR-098": {
        "min_tests": 5,
        "coverage": "85%+",
        "types": [
            "Performance: Batch validation (2 tests)",
            "Performance: Incremental checking (2 tests)",
            "Performance: Large document handling (1 test)",
        ],
    },
    "FR-099": {
        "min_tests": 6,
        "coverage": "80%+",
        "types": [
            "Unit: Error recovery logic (3 tests)",
            "Unit: Partial validation (2 tests)",
            "Integration: Checker integration (1 test)",
        ],
    },
    "FR-100": {
        "min_tests": 15,
        "coverage": "90%+",
        "types": [
            "Unit: Template load/save (5 tests)",
            "Unit: Template management (4 tests)",
            "Integration: Manager integration (3 tests)",
            "File I/O: Template file operations (3 tests)",
        ],
    },
    "FR-101": {
        "min_tests": 10,
        "coverage": "85%+",
        "types": [
            "Unit: Variable substitution (5 tests)",
            "Unit: Handlebars parsing (3 tests)",
            "Integration: Engine integration (2 tests)",
        ],
    },
    "FR-102": {
        "min_tests": 8,
        "coverage": "85%+",
        "types": [
            "Unit: Add/remove templates (3 tests)",
            "Unit: Template validation (2 tests)",
            "Integration: Manager integration (2 tests)",
            "File I/O: Custom template storage (1 test)",
        ],
    },
    "FR-103": {
        "min_tests": 10,
        "coverage": "85%+",
        "types": [
            "Unit: Preview rendering (4 tests)",
            "Unit: Preview updates (2 tests)",
            "Integration: Browser integration (2 tests)",
            "UI: Preview pane display (2 tests)",
        ],
    },
    "FR-104": {
        "min_tests": 8,
        "coverage": "85%+",
        "types": [
            "Unit: Metadata read/write (4 tests)",
            "Unit: Metadata validation (2 tests)",
            "Integration: Manager integration (2 tests)",
        ],
    },
    "FR-105": {
        "min_tests": 8,
        "coverage": "80%+",
        "types": [
            "Unit: Category logic (3 tests)",
            "Unit: Category filtering (2 tests)",
            "Integration: Browser integration (2 tests)",
            "UI: Category filters (1 test)",
        ],
    },
    "FR-106": {
        "min_tests": 6,
        "coverage": "75%+",
        "types": [
            "Unit: Export/import logic (2 tests)",
            "Unit: Template validation (2 tests)",
            "Integration: Manager integration (1 test)",
            "File I/O: Template file operations (1 test)",
        ],
    },
    "FR-107": {
        "min_tests": 12,
        "coverage": "90%+",
        "types": [
            "Unit: Template rendering (5 tests)",
            "Unit: Variable processing (3 tests)",
            "Integration: Template integration (2 tests)",
            "Performance: <200ms template load (2 tests)",
        ],
    },
}


def format_test_requirements(fr_id: str) -> str:
    """Format test requirements section for an FR.

    Args:
        fr_id: FR identifier (e.g., 'FR-085')

    Returns:
        Formatted test requirements section
    """
    req = TEST_REQUIREMENTS.get(fr_id)
    if not req:
        return ""

    lines = [
        "",
        "### Test Requirements",
        "",
        f"- **Minimum Tests:** {req['min_tests']}",
        f"- **Coverage Target:** {req['coverage']}",
        "- **Test Types:**",
    ]

    for test_type in req["types"]:
        lines.append(f"  - {test_type}")

    return "\n".join(lines)


def add_test_requirements(content: str, dry_run: bool = False) -> tuple[str, int]:
    """Add test requirements to FRs that lack them.

    Args:
        content: SPECIFICATIONS_AI.md content
        dry_run: If True, only report changes without modifying

    Returns:
        Tuple of (modified_content, count_added)
    """
    count_added = 0
    modified_content = content

    for fr_id in TEST_REQUIREMENTS.keys():
        # Find FR section - look for the Examples section if it exists, or --- if not
        pattern = rf"(## {fr_id}:.*?)(\n### Examples|\n---)"
        match = re.search(pattern, modified_content, re.DOTALL)

        if not match:
            print(f"Warning: Could not find {fr_id}")
            continue

        # Check if test requirements already exist
        fr_section = match.group(1)
        if "### Test Requirements" in fr_section:
            continue

        # Add test requirements before Examples or ---
        insert_pos = match.start(2)
        test_req_section = format_test_requirements(fr_id)

        if dry_run:
            print(f"Would add test requirements to {fr_id}")
        else:
            modified_content = modified_content[:insert_pos] + test_req_section + "\n" + modified_content[insert_pos:]

        count_added += 1

    return modified_content, count_added


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Add missing test requirements to SPECIFICATIONS_AI.md")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying file")
    parser.add_argument("--file", default="SPECIFICATIONS_AI.md", help="Path to specifications file")

    args = parser.parse_args()

    # Read file
    spec_file = Path(args.file)
    if not spec_file.exists():
        print(f"Error: {args.file} not found")
        sys.exit(1)

    with open(spec_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Add test requirements
    modified_content, count_added = add_test_requirements(content, args.dry_run)

    if args.dry_run:
        print(f"\nDry run complete: would add {count_added} test requirement sections")
    else:
        # Write back
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(modified_content)
        print(f"✅ Added {count_added} test requirement sections to {args.file}")

    sys.exit(0)


if __name__ == "__main__":
    main()
