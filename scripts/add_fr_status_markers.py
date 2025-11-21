#!/usr/bin/env python3
"""
Add explicit status markers to all FRs in SPECIFICATIONS_AI.md.

This script:
1. Finds all FR definitions (## FR-XXX:)
2. Checks if they have an explicit **Status:** line
3. Adds "**Status:** ✅ Implemented" if missing
4. Preserves all other content and formatting

Usage:
    python3 scripts/add_fr_status_markers.py [--dry-run] [--file PATH]

Options:
    --dry-run   Show changes without modifying file
    --file PATH Specify custom path to SPECIFICATIONS_AI.md
"""

import argparse
import re
import sys
from pathlib import Path


def find_frs_needing_status(content: str) -> list[tuple[int, str]]:
    """Find FRs that lack explicit status markers.

    Args:
        content: Full content of SPECIFICATIONS_AI.md

    Returns:
        List of (line_number, fr_heading) tuples for FRs missing status
    """
    lines = content.split('\n')
    frs_needing_status = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is an FR heading
        fr_match = re.match(r'^## (FR-[0-9]+[a-z]?): (.+)$', line)
        if fr_match:
            fr_id = fr_match.group(1)
            fr_name = fr_match.group(2)

            # Look ahead for **Status:** line (within next 10 lines)
            # Also check for inline status in Category/Priority line
            has_status = False
            for j in range(i + 1, min(i + 11, len(lines))):
                # Check for standalone **Status:** line
                if re.match(r'^\*\*Status:\*\*', lines[j]):
                    has_status = True
                    break
                # Check for inline status (e.g., **Category:** ... | **Status:** ...)
                if '**Status:**' in lines[j]:
                    has_status = True
                    break
                # Stop if we hit another FR or major section
                if re.match(r'^## ', lines[j]) and j > i + 1:
                    break

            if not has_status:
                frs_needing_status.append((i, fr_id, fr_name))

        i += 1

    return frs_needing_status


def add_status_markers(content: str, dry_run: bool = False) -> tuple[str, int]:
    """Add status markers to FRs that lack them.

    Args:
        content: Full content of SPECIFICATIONS_AI.md
        dry_run: If True, don't modify content, just report

    Returns:
        (modified_content, count_added) tuple
    """
    lines = content.split('\n')
    count_added = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is an FR heading
        fr_match = re.match(r'^## (FR-[0-9]+[a-z]?): (.+)$', line)
        if fr_match:
            fr_id = fr_match.group(1)
            fr_name = fr_match.group(2)

            # Look ahead for **Status:** line (standalone or inline)
            has_status = False
            status_line_idx = None
            for j in range(i + 1, min(i + 11, len(lines))):
                # Check for standalone **Status:** line
                if re.match(r'^\*\*Status:\*\*', lines[j]):
                    has_status = True
                    status_line_idx = j
                    break
                # Check for inline status (e.g., **Category:** ... | **Status:** ...)
                if '**Status:**' in lines[j]:
                    has_status = True
                    break
                # Stop if we hit another FR or major section
                if re.match(r'^## ', lines[j]) and j > i + 1:
                    break

            if not has_status:
                # Find insertion point (after Category/Priority, before Dependencies/Version)
                # Pattern: FR heading, blank line, **Category:**, **Priority:**
                # Insert status after Priority

                insert_idx = i + 1

                # Skip blank line after heading
                if insert_idx < len(lines) and lines[insert_idx].strip() == '':
                    insert_idx += 1

                # Skip **Category:** line
                if insert_idx < len(lines) and re.match(r'^\*\*Category:\*\*', lines[insert_idx]):
                    insert_idx += 1

                # Skip **Priority:** line
                if insert_idx < len(lines) and re.match(r'^\*\*Priority:\*\*', lines[insert_idx]):
                    insert_idx += 1

                # Insert status marker here
                status_line = "**Status:** ✅ Implemented"

                if dry_run:
                    print(f"Would add status to {fr_id}: {fr_name} (line {i+1})")
                else:
                    lines.insert(insert_idx, status_line)

                count_added += 1

        i += 1

    if dry_run:
        return content, count_added
    else:
        return '\n'.join(lines), count_added


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add explicit status markers to FRs in SPECIFICATIONS_AI.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show changes without modifying file'
    )
    parser.add_argument(
        '--file',
        type=Path,
        default=Path('SPECIFICATIONS_AI.md'),
        help='Path to SPECIFICATIONS_AI.md (default: ./SPECIFICATIONS_AI.md)'
    )

    args = parser.parse_args()

    # Read file
    spec_file = args.file
    if not spec_file.exists():
        print(f"Error: File not found: {spec_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {spec_file}...")
    content = spec_file.read_text(encoding='utf-8')

    # Find FRs needing status
    frs_needing = find_frs_needing_status(content)
    print(f"Found {len(frs_needing)} FRs without explicit status markers")

    if len(frs_needing) == 0:
        print("✅ All FRs already have status markers!")
        return 0

    # Show first 10 FRs needing status
    print("\nSample FRs needing status markers:")
    for line_num, fr_id, fr_name in frs_needing[:10]:
        print(f"  {fr_id}: {fr_name} (line {line_num + 1})")
    if len(frs_needing) > 10:
        print(f"  ... and {len(frs_needing) - 10} more")

    # Add status markers
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
        modified_content, count = add_status_markers(content, dry_run=True)
        print(f"\nWould add {count} status markers")
    else:
        print("\n✏️  Adding status markers...")
        modified_content, count = add_status_markers(content, dry_run=False)

        # Write back to file
        spec_file.write_text(modified_content, encoding='utf-8')
        print(f"✅ Added {count} status markers to {spec_file}")
        print(f"\nTo verify: grep -E '^\\*\\*Status:\\*\\*' {spec_file} | wc -l")

    return 0


if __name__ == '__main__':
    sys.exit(main())
