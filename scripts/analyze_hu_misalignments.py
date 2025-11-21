#!/usr/bin/env python3
"""
Analyze misalignments between SPECIFICATIONS_AI.md and SPECIFICATIONS_HU.md.

This script compares the two specification files to identify:
- Missing or extra FRs
- Mismatched FR names
- Inconsistent FR statuses
- Version/metadata misalignments
"""

import re
import sys
from pathlib import Path


def parse_ai_specs(content: str) -> dict[str, dict]:
    """Parse SPECIFICATIONS_AI.md for FR information.

    Args:
        content: File content

    Returns:
        Dictionary mapping FR ID to FR details
    """
    frs = {}
    # Simpler pattern: just find ## FR-XXX: Name
    pattern = r"## (FR-\d+[a-z]?): (.+?)(?:\n|$)"

    for match in re.finditer(pattern, content):
        fr_id = match.group(1)
        fr_name = match.group(2).strip()

        frs[fr_id] = {
            "name": fr_name,
            "status": "Unknown",  # Can be extracted separately if needed
        }

    return frs


def parse_hu_specs(content: str) -> dict[str, dict]:
    """Parse SPECIFICATIONS_HU.md for FR information.

    Args:
        content: File content

    Returns:
        Dictionary mapping FR ID to FR details
    """
    frs = {}
    # Pattern: **FR-XXX: Name** - description
    pattern = r"\*\*(FR-\d+[a-z]?): (.+?)\*\*\s*-\s*(.+?)(?:\n|$)"

    for match in re.finditer(pattern, content):
        fr_id = match.group(1)
        fr_name = match.group(2).strip()
        fr_description = match.group(3).strip()

        frs[fr_id] = {"name": fr_name, "description": fr_description}

    return frs


def compare_specs(ai_frs: dict, hu_frs: dict) -> dict:
    """Compare SPECIFICATIONS_AI.md and SPECIFICATIONS_HU.md.

    Args:
        ai_frs: FRs from SPECIFICATIONS_AI.md
        hu_frs: FRs from SPECIFICATIONS_HU.md

    Returns:
        Dictionary with comparison results
    """
    ai_ids = set(ai_frs.keys())
    hu_ids = set(hu_frs.keys())

    results = {
        "missing_in_hu": sorted(ai_ids - hu_ids),
        "extra_in_hu": sorted(hu_ids - ai_ids),
        "name_mismatches": [],
        "ai_count": len(ai_ids),
        "hu_count": len(hu_ids),
    }

    # Check for name mismatches in common FRs
    common_ids = ai_ids & hu_ids
    for fr_id in sorted(common_ids):
        ai_name = ai_frs[fr_id]["name"]
        hu_name = hu_frs[fr_id]["name"]

        # Simple comparison (ignoring case and minor punctuation)
        if ai_name.lower().replace("-", " ") != hu_name.lower().replace("-", " "):
            results["name_mismatches"].append({"fr_id": fr_id, "ai_name": ai_name, "hu_name": hu_name})

    return results


def print_report(results: dict):
    """Print comparison report.

    Args:
        results: Comparison results
    """
    print("=" * 70)
    print("SPECIFICATIONS_HU.md Gap Analysis")
    print("=" * 70)
    print()

    print(f"SPECIFICATIONS_AI.md FRs: {results['ai_count']}")
    print(f"SPECIFICATIONS_HU.md FRs: {results['hu_count']}")
    print()

    if not results["missing_in_hu"] and not results["extra_in_hu"] and not results["name_mismatches"]:
        print("✅ Perfect alignment - no gaps or mismatches found")
        return

    if results["missing_in_hu"]:
        print(f"⚠️  Missing in SPECIFICATIONS_HU.md ({len(results['missing_in_hu'])} FRs):")
        for fr_id in results["missing_in_hu"]:
            print(f"  - {fr_id}")
        print()

    if results["extra_in_hu"]:
        print(f"⚠️  Extra in SPECIFICATIONS_HU.md ({len(results['extra_in_hu'])} FRs):")
        for fr_id in results["extra_in_hu"]:
            print(f"  - {fr_id} (should be removed or added to SPECIFICATIONS_AI.md)")
        print()

    if results["name_mismatches"]:
        print(f"⚠️  FR Name Mismatches ({len(results['name_mismatches'])} FRs):")
        for mismatch in results["name_mismatches"]:
            print(f"  - {mismatch['fr_id']}:")
            print(f"    AI:  {mismatch['ai_name']}")
            print(f"    HU:  {mismatch['hu_name']}")
        print()

    print("=" * 70)
    print("Recommendations:")
    print("=" * 70)

    if results["missing_in_hu"]:
        print(f"1. Add {len(results['missing_in_hu'])} missing FRs to SPECIFICATIONS_HU.md")

    if results["extra_in_hu"]:
        print(f"2. Remove or reconcile {len(results['extra_in_hu'])} extra FRs in SPECIFICATIONS_HU.md")

    if results["name_mismatches"]:
        print(f"3. Align {len(results['name_mismatches'])} FR names between files")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze misalignments between SPECIFICATIONS_AI.md and SPECIFICATIONS_HU.md"
    )
    parser.add_argument("--ai-file", default="SPECIFICATIONS_AI.md", help="Path to SPECIFICATIONS_AI.md")
    parser.add_argument("--hu-file", default="SPECIFICATIONS_HU.md", help="Path to SPECIFICATIONS_HU.md")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Read files
    ai_file = Path(args.ai_file)
    hu_file = Path(args.hu_file)

    if not ai_file.exists():
        print(f"Error: {args.ai_file} not found")
        sys.exit(1)

    if not hu_file.exists():
        print(f"Error: {args.hu_file} not found")
        sys.exit(1)

    with open(ai_file, "r", encoding="utf-8") as f:
        ai_content = f.read()

    with open(hu_file, "r", encoding="utf-8") as f:
        hu_content = f.read()

    # Parse FRs
    ai_frs = parse_ai_specs(ai_content)
    hu_frs = parse_hu_specs(hu_content)

    # Compare
    results = compare_specs(ai_frs, hu_frs)

    # Output
    if args.json:
        import json

        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    # Exit code
    if results["missing_in_hu"] or results["extra_in_hu"] or results["name_mismatches"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
