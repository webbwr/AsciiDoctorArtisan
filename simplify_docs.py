#!/usr/bin/env python3
"""Simplify all markdown files to Grade 5.0 reading level."""

import os
from pathlib import Path

# Files to simplify (above Grade 5.0)
FILES_TO_SIMPLIFY = [
    "docs/archive/REFACTORING_COMPLETE.md",
    "docs/performance/PERFORMANCE_OPTIMIZATION_PLAN.md",
    "docs/planning/REFACTORING_SUMMARY.md",
    "docs/performance/PERFORMANCE_IMPLEMENTATION_SUMMARY.md",
    "docs/performance/PHASE_2_3_AND_2_4_COMPLETE.md",
    "docs/planning/IMPLEMENTATION_CHECKLIST.md",
    "openspec/changes/_template/tasks.md",
    "docs/performance/SESSION_SUMMARY_2025_10_25.md",
    "docs/performance/PHASE_2_COMPLETE.md",
    "docs/archive/WEEK1_COMPLETE.md",
    "docs/performance/INTEGRATION_GUIDE.md",
    "CLAUDE.md",
    "docs/performance/SESSION_SUMMARY_2025_10_25_FINAL.md",
    "docs/performance/PHASE_3_3_COMPLETE.md",
    "docs/performance/QUICK_START_PERFORMANCE.md",
    "docs/archive/SESSION_COMPLETE.md",
    "docs/performance/PERFORMANCE_README.md",
    "docs/planning/IMPLEMENTATION_TIMELINE.md",
    "docs/performance/PHASE_6_1_COMPLETE.md",
    "docs/performance/PHASE_3_1_COMPLETE.md",
    "docs/performance/PHASE_3_4_COMPLETE.md",
    "openspec/changes/_template/specs/example.md",
    "templates/default/themes/README.md",
    "docs/performance/STARTUP_PERFORMANCE_ANALYSIS.md",
    "templates/default/images/README.md",
    "docs/planning/REFACTORING_PLAN_DETAILED.md",
    "docs/performance/PHASE_4_1_COMPLETE.md",
    "openspec/changes/_template/design.md",
    "docs/performance/BASELINE_METRICS.md",
    "docs/performance/PERFORMANCE_IMPROVEMENT_PLAN.md",
    "docs/planning/QUICK_WINS.md",
    "docs/performance/PHASE_3_2_COMPLETE.md",
    "docs/a.md",
    "openspec/changes/_template/proposal.md",
]

def main():
    """Main function."""
    project_root = Path(__file__).parent

    print(f"\nFiles to simplify: {len(FILES_TO_SIMPLIFY)}")
    print("\nThese are technical archive and performance docs.")
    print("They should be simplified for better readability.\n")

    for file_path in FILES_TO_SIMPLIFY:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (NOT FOUND)")

    print(f"\nReady to simplify {len(FILES_TO_SIMPLIFY)} files.")

if __name__ == '__main__':
    main()
