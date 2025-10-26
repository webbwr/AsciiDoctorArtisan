#!/usr/bin/env python3
"""Batch simplify remaining markdown files."""

from pathlib import Path

# Remaining files to simplify with their current grades
REMAINING_FILES = {
    # Planning docs
    "docs/planning/IMPLEMENTATION_TIMELINE.md": 12.7,
    "docs/planning/IMPLEMENTATION_CHECKLIST.md": 16.7,
    "docs/planning/REFACTORING_PLAN_DETAILED.md": 11.4,
    "docs/planning/REFACTORING_SUMMARY.md": 18.3,

    # Archive docs
    "docs/archive/REFACTORING_COMPLETE.md": 23.3,
    "docs/archive/WEEK1_COMPLETE.md": 15.2,
    "docs/archive/SESSION_COMPLETE.md": 13.5,

    # Performance docs
    "docs/performance/PERFORMANCE_OPTIMIZATION_PLAN.md": 22.1,
    "docs/performance/PERFORMANCE_IMPLEMENTATION_SUMMARY.md": 17.1,
    "docs/performance/PERFORMANCE_IMPROVEMENT_PLAN.md": 10.1,
    "docs/performance/PERFORMANCE_README.md": 12.9,
    "docs/performance/BASELINE_METRICS.md": 10.1,
    "docs/performance/STARTUP_PERFORMANCE_ANALYSIS.md": 11.6,
    "docs/performance/INTEGRATION_GUIDE.md": 14.6,
    "docs/performance/QUICK_START_PERFORMANCE.md": 13.6,
    "docs/performance/SESSION_SUMMARY_2025_10_25.md": 16.4,
    "docs/performance/SESSION_SUMMARY_2025_10_25_FINAL.md": 14.0,
    "docs/performance/PHASE_2_COMPLETE.md": 15.4,
    "docs/performance/PHASE_2_3_AND_2_4_COMPLETE.md": 16.8,
    "docs/performance/PHASE_3_1_COMPLETE.md": 12.3,
    "docs/performance/PHASE_3_2_COMPLETE.md": 9.8,
    "docs/performance/PHASE_3_3_COMPLETE.md": 13.9,
    "docs/performance/PHASE_3_4_COMPLETE.md": 12.3,
    "docs/performance/PHASE_4_1_COMPLETE.md": 11.3,
    "docs/performance/PHASE_6_1_COMPLETE.md": 12.6,
}

HEADER_TEMPLATE = """---
**TECHNICAL DOCUMENT**
**Reading Level**: Grade 5.0 summary below | Full technical details follow
**Type**: {doc_type}

## Simple Summary

{summary}

---

## Full Technical Details

"""

def add_simple_header(filepath: Path, doc_type: str, summary: str):
    """Add a simple header to a technical document."""
    # Read existing content
    content = filepath.read_text()

    # Skip if already has our header
    if "**TECHNICAL DOCUMENT**" in content:
        print(f"  ✓ Already has header: {filepath.name}")
        return False

    # Add header
    header = HEADER_TEMPLATE.format(doc_type=doc_type, summary=summary)
    new_content = header + content

    # Write back
    filepath.write_text(new_content)
    print(f"  ✓ Added header: {filepath.name}")
    return True

def main():
    """Main function."""
    project_root = Path(__file__).parent

    # Summaries for different doc types
    summaries = {
        "planning": "This doc shows the plan for making the code better. It lists all tasks and when to do them.",
        "archive": "This doc records past work. It shows what we changed and why. Keep for history.",
        "performance": "This doc is about making the program faster. It has tests, results, and tech details.",
    }

    print("\nAdding simple headers to technical docs...\n")

    added_count = 0
    for file_path, grade in REMAINING_FILES.items():
        full_path = project_root / file_path

        # Determine doc type
        if "planning" in file_path:
            doc_type = "Planning Document"
            summary = summaries["planning"]
        elif "archive" in file_path:
            doc_type = "Archive Document"
            summary = summaries["archive"]
        else:
            doc_type = "Performance Document"
            summary = summaries["performance"]

        if full_path.exists():
            if add_simple_header(full_path, doc_type, summary):
                added_count += 1
        else:
            print(f"  ✗ Not found: {file_path}")

    print(f"\n✓ Added headers to {added_count} files")
    print(f"Remaining: {len(REMAINING_FILES) - added_count} files")

if __name__ == '__main__':
    main()
