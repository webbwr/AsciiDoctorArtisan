#!/usr/bin/env python3
"""
Add missing implementation references to SPECIFICATIONS_AI.md.

This script adds implementation references to FRs that are missing them,
specifically FR-086 through FR-107 (v2.0 features).
"""

import re
import sys
from pathlib import Path

# Mapping of FR IDs to their implementation files
IMPLEMENTATION_MAP = {
    "FR-086": "src/asciidoc_artisan/ui/autocomplete_widget.py",
    "FR-087": "src/asciidoc_artisan/core/autocomplete_providers.py",
    "FR-088": "src/asciidoc_artisan/core/autocomplete_engine.py::fuzzy_match()",
    "FR-089": "src/asciidoc_artisan/core/autocomplete_engine.py",
    "FR-090": "src/asciidoc_artisan/core/autocomplete_providers.py",
    "FR-092": "src/asciidoc_artisan/ui/syntax_checker_manager.py",
    "FR-093": "src/asciidoc_artisan/ui/syntax_checker_manager.py",
    "FR-094": "src/asciidoc_artisan/ui/syntax_checker_manager.py",
    "FR-095": "src/asciidoc_artisan/core/syntax_validators.py",
    "FR-096": "src/asciidoc_artisan/core/syntax_checker.py",
    "FR-097": "src/asciidoc_artisan/core/syntax_checker.py",
    "FR-098": "src/asciidoc_artisan/core/syntax_checker.py",
    "FR-099": "src/asciidoc_artisan/core/syntax_checker.py",
    "FR-101": "src/asciidoc_artisan/core/template_engine.py",
    "FR-102": "src/asciidoc_artisan/core/template_manager.py",
    "FR-103": "src/asciidoc_artisan/ui/template_browser.py",
    "FR-104": "src/asciidoc_artisan/core/template_manager.py",
    "FR-105": "src/asciidoc_artisan/core/template_manager.py",
    "FR-106": "src/asciidoc_artisan/core/template_manager.py",
}


def add_implementation_references(content: str, dry_run: bool = False) -> tuple[str, int]:
    """Add implementation references to FRs that lack them.

    Args:
        content: SPECIFICATIONS_AI.md content
        dry_run: If True, only report changes without modifying

    Returns:
        Tuple of (modified_content, count_added)
    """
    count_added = 0
    modified_content = content

    for fr_id, impl_path in IMPLEMENTATION_MAP.items():
        # Find FR section
        pattern = rf'(## {fr_id}:.*?\n\n\*\*Category:.*?\n)'
        match = re.search(pattern, modified_content, re.DOTALL)

        if not match:
            print(f"Warning: Could not find {fr_id}")
            continue

        # Check if implementation reference already exists
        fr_section_start = match.start()
        fr_section_end = modified_content.find("\n\n**Acceptance:", fr_section_start)
        if fr_section_end == -1:
            fr_section_end = modified_content.find("\n\n---", fr_section_start)

        if fr_section_end == -1:
            print(f"Warning: Could not find section end for {fr_id}")
            continue

        fr_section = modified_content[fr_section_start:fr_section_end]

        if "**Implementation:**" in fr_section:
            continue

        # Add implementation reference after Category line
        category_line_end = match.end()
        impl_line = f"**Implementation:** `{impl_path}`\n"

        if dry_run:
            print(f"Would add to {fr_id}: {impl_line.strip()}")
        else:
            modified_content = (
                modified_content[:category_line_end] +
                impl_line +
                modified_content[category_line_end:]
            )

        count_added += 1

    return modified_content, count_added


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add missing implementation references to SPECIFICATIONS_AI.md"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying file"
    )
    parser.add_argument(
        "--file",
        default="SPECIFICATIONS_AI.md",
        help="Path to specifications file"
    )

    args = parser.parse_args()

    # Read file
    spec_file = Path(args.file)
    if not spec_file.exists():
        print(f"Error: {args.file} not found")
        sys.exit(1)

    with open(spec_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Add implementation references
    modified_content, count_added = add_implementation_references(content, args.dry_run)

    if args.dry_run:
        print(f"\nDry run complete: would add {count_added} implementation references")
    else:
        # Write back
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(modified_content)
        print(f"✅ Added {count_added} implementation references to {args.file}")

    sys.exit(0)


if __name__ == "__main__":
    main()
