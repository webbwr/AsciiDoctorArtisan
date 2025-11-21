#!/usr/bin/env python3
"""
Analyze FR completeness in SPECIFICATIONS_AI.md.

This script checks for:
- Missing implementation references
- Missing examples
- Missing test requirements
- Incomplete acceptance criteria

Usage:
    python3 scripts/analyze_fr_gaps.py
    python3 scripts/analyze_fr_gaps.py --verbose
    python3 scripts/analyze_fr_gaps.py --format json
"""

import json
import re
import sys


def analyze_fr_completeness(spec_file="SPECIFICATIONS_AI.md"):
    """Analyze FR completeness and report gaps.

    Args:
        spec_file: Path to specifications file

    Returns:
        dict: Analysis report with gaps
    """
    with open(spec_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all FR sections
    fr_pattern = r"## (FR-\d+[a-z]?): (.+?)\n\n(.*?)(?=\n## FR-|\Z)"
    matches = re.findall(fr_pattern, content, re.DOTALL)

    report = {
        "total_frs": len(matches),
        "complete_frs": 0,
        "missing_implementation": [],
        "missing_examples": [],
        "missing_test_requirements": [],
        "incomplete_criteria": [],
        "fr_details": {},
    }

    for fr_id, fr_name, fr_content in matches:
        has_impl = "**Implementation:**" in fr_content
        has_examples = "### Examples" in fr_content or "### Example" in fr_content
        has_test_req = "### Test Requirements" in fr_content

        # Check acceptance criteria
        unchecked = fr_content.count("- [ ]")
        checked = fr_content.count("- [x]")

        # Store FR details
        fr_details = {
            "name": fr_name,
            "has_implementation": has_impl,
            "has_examples": has_examples,
            "has_test_requirements": has_test_req,
            "criteria_checked": checked,
            "criteria_unchecked": unchecked,
            "is_complete": has_impl and has_examples and has_test_req and unchecked == 0,
        }

        report["fr_details"][fr_id] = fr_details

        if fr_details["is_complete"]:
            report["complete_frs"] += 1

        if not has_impl:
            report["missing_implementation"].append((fr_id, fr_name))
        if not has_examples:
            report["missing_examples"].append((fr_id, fr_name))
        if not has_test_req:
            report["missing_test_requirements"].append((fr_id, fr_name))
        if unchecked > 0:
            report["incomplete_criteria"].append((fr_id, fr_name, unchecked))

    # Calculate percentages
    report["completeness_percent"] = (report["complete_frs"] / report["total_frs"]) * 100
    report["impl_coverage_percent"] = (
        (report["total_frs"] - len(report["missing_implementation"])) / report["total_frs"]
    ) * 100
    report["examples_coverage_percent"] = (
        (report["total_frs"] - len(report["missing_examples"])) / report["total_frs"]
    ) * 100
    report["test_req_coverage_percent"] = (
        (report["total_frs"] - len(report["missing_test_requirements"])) / report["total_frs"]
    ) * 100

    return report


def print_report(report, verbose=False):
    """Print analysis report in human-readable format.

    Args:
        report: Analysis report dict
        verbose: If True, show detailed FR information
    """
    print("=" * 60)
    print("FR Completeness Analysis")
    print("=" * 60)
    print()

    print(f"Total FRs: {report['total_frs']}")
    print(f"Complete FRs: {report['complete_frs']} ({report['completeness_percent']:.1f}%)")
    print()

    print("Component Coverage:")
    print(f"  Implementation References: {report['impl_coverage_percent']:.1f}%")
    print(f"  Examples: {report['examples_coverage_percent']:.1f}%")
    print(f"  Test Requirements: {report['test_req_coverage_percent']:.1f}%")
    print()

    print("Gaps Identified:")
    print(f"  Missing Implementation: {len(report['missing_implementation'])} FRs")
    print(f"  Missing Examples: {len(report['missing_examples'])} FRs")
    print(f"  Missing Test Requirements: {len(report['missing_test_requirements'])} FRs")
    print(f"  Incomplete Criteria: {len(report['incomplete_criteria'])} FRs")
    print()

    if verbose:
        print("-" * 60)
        print("Missing Implementation References:")
        for fr_id, fr_name in report["missing_implementation"][:10]:
            print(f"  {fr_id}: {fr_name}")
        if len(report["missing_implementation"]) > 10:
            print(f"  ... and {len(report['missing_implementation']) - 10} more")
        print()

        print("Missing Examples:")
        for fr_id, fr_name in report["missing_examples"][:10]:
            print(f"  {fr_id}: {fr_name}")
        if len(report["missing_examples"]) > 10:
            print(f"  ... and {len(report['missing_examples']) - 10} more")
        print()

        print("Missing Test Requirements:")
        for fr_id, fr_name in report["missing_test_requirements"][:10]:
            print(f"  {fr_id}: {fr_name}")
        if len(report["missing_test_requirements"]) > 10:
            print(f"  ... and {len(report['missing_test_requirements']) - 10} more")
        print()

    print("=" * 60)
    print("Recommendations:")
    print("=" * 60)

    if report["impl_coverage_percent"] < 100:
        print("1. Add implementation references to missing FRs")
        print(f"   Priority: HIGH ({len(report['missing_implementation'])} FRs)")

    if report["test_req_coverage_percent"] < 100:
        print("2. Add test requirements to missing FRs")
        print(f"   Priority: HIGH ({len(report['missing_test_requirements'])} FRs)")

    if report["examples_coverage_percent"] < 80:
        print("3. Add examples to missing FRs")
        print(f"   Priority: MEDIUM ({len(report['missing_examples'])} FRs)")

    if report["completeness_percent"] == 100:
        print("✅ All FRs are complete!")
    else:
        print(f"\nTarget: 90%+ completeness (currently {report['completeness_percent']:.1f}%)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze FR completeness in SPECIFICATIONS_AI.md")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed gap information")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--file", default="SPECIFICATIONS_AI.md", help="Path to specifications file")

    args = parser.parse_args()

    # Run analysis
    report = analyze_fr_completeness(args.file)

    # Output results
    if args.format == "json":
        # Remove tuple items for JSON serialization
        report_json = report.copy()
        report_json["missing_implementation"] = [
            {"id": fr_id, "name": fr_name} for fr_id, fr_name in report["missing_implementation"]
        ]
        report_json["missing_examples"] = [
            {"id": fr_id, "name": fr_name} for fr_id, fr_name in report["missing_examples"]
        ]
        report_json["missing_test_requirements"] = [
            {"id": fr_id, "name": fr_name} for fr_id, fr_name in report["missing_test_requirements"]
        ]
        report_json["incomplete_criteria"] = [
            {"id": fr_id, "name": fr_name, "unchecked": count}
            for fr_id, fr_name, count in report["incomplete_criteria"]
        ]
        print(json.dumps(report_json, indent=2))
    else:
        print_report(report, verbose=args.verbose)

    # Exit code based on completeness
    if report["completeness_percent"] < 90:
        sys.exit(1)  # Fail if less than 90% complete
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
