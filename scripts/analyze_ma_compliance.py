#!/usr/bin/env python3
"""
Analyze MA (間) Principle Compliance - Unified Analysis Script.

This script combines code and documentation analysis to provide a comprehensive
MA principle compliance report. It wraps the existing analysis scripts and
generates a unified summary report.

Usage:
    python3 scripts/analyze_ma_compliance.py [OPTIONS]

Options:
    --output FILE       Output report file (default: docs/reports/ma_compliance_report.md)
    --json              Also output JSON reports
    --verbose           Verbose output
    --code-only         Analyze code only
    --docs-only         Analyze documentation only

Exit Codes:
    0 - No violations
    1 - P1/P2 violations found
    2 - P0 (critical) violations found
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def run_analysis_script(script_path: str, json_output: str, verbose: bool = False) -> dict[str, Any]:
    """
    Run an analysis script and return the JSON results.

    Args:
        script_path: Path to the analysis script
        json_output: Path for JSON output
        verbose: Enable verbose output

    Returns:
        Dictionary with analysis results

    Raises:
        RuntimeError: If script execution fails
    """
    cmd = ["python3", script_path, "--json", json_output]
    if verbose:
        cmd.append("--verbose")

    print(f"Running {Path(script_path).name}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )

        # Read JSON results
        with open(json_output, encoding="utf-8") as f:
            data = json.load(f)

        # Print script output if verbose
        if verbose and result.stdout:
            print(result.stdout)

        return data

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Analysis script timed out: {script_path}")
    except FileNotFoundError:
        raise RuntimeError(f"Analysis script not found: {script_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON output: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to run analysis script: {e}")


def count_violations_by_severity(violations: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count violations by severity level.

    Args:
        violations: List of violation dictionaries

    Returns:
        Dictionary with counts per severity (P0, P1, P2)
    """
    counts = {"P0": 0, "P1": 0, "P2": 0}
    for v in violations:
        severity = v.get("severity", "P2")
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def count_violations_by_type(violations: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count violations by type.

    Args:
        violations: List of violation dictionaries

    Returns:
        Dictionary with counts per violation type
    """
    counts: dict[str, int] = {}
    for v in violations:
        vtype = v.get("type", "unknown")
        counts[vtype] = counts.get(vtype, 0) + 1
    return counts


def format_severity_table(severity_counts: dict[str, int]) -> str:
    """
    Format severity breakdown as markdown table.

    Args:
        severity_counts: Dictionary with severity counts

    Returns:
        Markdown table string
    """
    lines = [
        "| Severity | Count | Description |",
        "|----------|-------|-------------|",
        f"| **P0 (Critical)** | {severity_counts.get('P0', 0)} | Functions >100 lines or complexity >15 |",
        f"| **P1 (High)** | {severity_counts.get('P1', 0)} | Functions >50 lines or complexity >10 |",
        f"| **P2 (Medium)** | {severity_counts.get('P2', 0)} | Parameter count, nesting, comments |",
    ]
    return "\n".join(lines)


def format_type_table(type_counts: dict[str, int], total: int) -> str:
    """
    Format violation type breakdown as markdown table.

    Args:
        type_counts: Dictionary with type counts
        total: Total violation count

    Returns:
        Markdown table string
    """
    lines = [
        "| Type | Count | Percentage |",
        "|------|-------|------------|",
    ]

    # Sort by count descending
    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

    for vtype, count in sorted_types:
        percentage = (count / total * 100) if total > 0 else 0
        # Format type name for display
        display_name = vtype.replace("_", " ").title()
        lines.append(f"| {display_name} | {count} | {percentage:.1f}% |")

    return "\n".join(lines)


def get_top_violators(data: dict[str, Any], limit: int = 10) -> list[tuple[str, int, int]]:
    """
    Get top violating files.

    Args:
        data: Analysis data dictionary
        limit: Maximum number of files to return

    Returns:
        List of (file, violation_count, critical_count) tuples
    """
    file_violations: dict[str, dict[str, int]] = {}

    # Count violations per file
    for v in data.get("violations", []):
        file_path = v.get("file", "unknown")
        severity = v.get("severity", "P2")

        if file_path not in file_violations:
            file_violations[file_path] = {"total": 0, "critical": 0}

        file_violations[file_path]["total"] += 1
        if severity == "P0":
            file_violations[file_path]["critical"] += 1

    # Convert to sorted list
    violators = [(file, counts["total"], counts["critical"]) for file, counts in file_violations.items()]

    # Sort by total violations, then by critical
    violators.sort(key=lambda x: (x[1], x[2]), reverse=True)

    return violators[:limit]


def format_top_violators_table(violators: list[tuple[str, int, int]]) -> str:
    """
    Format top violators as markdown table.

    Args:
        violators: List of (file, total, critical) tuples

    Returns:
        Markdown table string
    """
    lines = [
        "| Rank | File | Violations | Critical |",
        "|------|------|------------|----------|",
    ]

    for i, (file, total, critical) in enumerate(violators, 1):
        # Shorten file path for display
        short_file = file.replace("src/asciidoc_artisan/", "")
        lines.append(f"| {i} | `{short_file}` | {total} | {critical} |")

    return "\n".join(lines)


def get_critical_violations(violations: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    """
    Get critical (P0) violations sorted by severity metric.

    Args:
        violations: List of violation dictionaries
        limit: Maximum number to return

    Returns:
        List of critical violations
    """
    critical = [v for v in violations if v.get("severity") == "P0"]

    # Sort by actual value (descending)
    critical.sort(key=lambda x: x.get("actual", 0), reverse=True)

    return critical[:limit]


def format_critical_violations(violations: list[dict[str, Any]]) -> str:
    """
    Format critical violations as markdown list.

    Args:
        violations: List of critical violation dictionaries

    Returns:
        Markdown list string
    """
    lines = []

    for i, v in enumerate(violations, 1):
        file = v.get("file", "").replace("src/asciidoc_artisan/", "")
        line = v.get("line", 0)
        vtype = v.get("type", "")
        actual = v.get("actual", 0)
        message = v.get("message", "")

        lines.append(f"{i}. `{file}:{line}` - {message} - **{actual} {vtype}** ❌")

    return "\n".join(lines)


def generate_report(
    code_data: dict[str, Any] | None,
    docs_data: dict[str, Any] | None,
    output_path: str,
) -> int:
    """
    Generate unified MA compliance report.

    Args:
        code_data: Code analysis results (or None if skipped)
        docs_data: Documentation analysis results (or None if skipped)
        output_path: Output file path

    Returns:
        Exit code (0=clean, 1=violations, 2=critical violations)
    """
    # Count totals
    code_violations = code_data.get("violations", []) if code_data else []
    docs_violations = docs_data.get("violations", []) if docs_data else []

    code_severity = count_violations_by_severity(code_violations)
    docs_severity = count_violations_by_severity(docs_violations)

    total_code = len(code_violations)
    total_docs = len(docs_violations)
    total_all = total_code + total_docs

    total_p0 = code_severity.get("P0", 0) + docs_severity.get("P0", 0)
    total_p1 = code_severity.get("P1", 0) + docs_severity.get("P1", 0)
    total_p2 = code_severity.get("P2", 0) + docs_severity.get("P2", 0)

    # Determine status
    if total_p0 > 0:
        status = "CRITICAL VIOLATIONS FOUND"
        exit_code = 2
    elif total_p1 > 0 or total_p2 > 0:
        status = "VIOLATIONS FOUND"
        exit_code = 1
    else:
        status = "COMPLIANT"
        exit_code = 0

    # Generate report content
    report_lines = [
        "# MA (間) Principle Compliance Report",
        "",
        "**Project:** AsciiDoc Artisan",
        f"**Date:** {datetime.now().strftime('%B %d, %Y')}",
        "**Analysis Type:** MA (間) Principle Compliance Audit",
        f"**Status:** {status}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "**MA (間) Principle:** Japanese aesthetic concept of negative space applied to code and documentation. "
        "Emphasizes simplicity, intentional whitespace, and minimal sufficiency.",
        "",
        "**Key Findings:**",
    ]

    if code_data:
        report_lines.append(
            f"- **Codebase**: {total_code} violations "
            f"({code_severity.get('P0', 0)} P0, "
            f"{code_severity.get('P1', 0)} P1, "
            f"{code_severity.get('P2', 0)} P2)"
        )

    if docs_data:
        report_lines.append(
            f"- **Documentation**: {total_docs} violations "
            f"({docs_severity.get('P0', 0)} P0, "
            f"{docs_severity.get('P1', 0)} P1, "
            f"{docs_severity.get('P2', 0)} P2)"
        )

    report_lines.extend(
        [
            f"- **Total**: {total_all} violations across code and documentation",
            "",
        ]
    )

    # Impact assessment
    if total_p0 > 0:
        impact = "CRITICAL - Critical violations require immediate attention"
    elif total_p1 > 20:
        impact = "HIGH - Significant violations need systematic cleanup"
    elif total_p1 > 0:
        impact = "MODERATE - Some violations should be addressed"
    else:
        impact = "LOW - Minor improvements possible"

    report_lines.extend(
        [
            f"**Impact:** {impact}",
            "",
            "---",
            "",
        ]
    )

    # Codebase violations section
    if code_data:
        report_lines.extend(
            [
                f"## Codebase Violations ({total_code} Total)",
                "",
                "### Severity Breakdown",
                "",
                format_severity_table(code_severity),
                "",
            ]
        )

        # Violation types
        if code_violations:
            type_counts = count_violations_by_type(code_violations)
            report_lines.extend(
                [
                    "### Violation Types",
                    "",
                    format_type_table(type_counts, total_code),
                    "",
                ]
            )

        # Top violators
        violators = get_top_violators(code_data, limit=10)
        if violators:
            report_lines.extend(
                [
                    "### Top Violators (Files)",
                    "",
                    format_top_violators_table(violators),
                    "",
                ]
            )

        # Critical violations
        critical = get_critical_violations(code_violations, limit=20)
        if critical:
            report_lines.extend(
                [
                    "### Critical P0 Violations",
                    "",
                    format_critical_violations(critical),
                    "",
                ]
            )

    # Documentation violations section
    if docs_data:
        report_lines.extend(
            [
                f"## Documentation Violations ({total_docs} Total)",
                "",
                "### Severity Breakdown",
                "",
                format_severity_table(docs_severity),
                "",
            ]
        )

        # Violation types
        if docs_violations:
            type_counts = count_violations_by_type(docs_violations)
            report_lines.extend(
                [
                    "### Violation Types",
                    "",
                    format_type_table(type_counts, total_docs),
                    "",
                ]
            )

    # Recommendations
    report_lines.extend(
        [
            "---",
            "",
            "## Recommendations",
            "",
        ]
    )

    if total_p0 > 0:
        report_lines.extend(
            [
                "### Priority 1: Fix Critical Violations (P0)",
                "",
                f"**Count:** {total_p0} violations",
                "**Timeline:** Immediate (1-2 weeks)",
                "",
                "Critical violations significantly impact code maintainability and should be fixed immediately.",
                "",
            ]
        )

    if total_p1 > 0:
        report_lines.extend(
            [
                "### Priority 2: Address High-Priority Violations (P1)",
                "",
                f"**Count:** {total_p1} violations",
                "**Timeline:** Short-term (2-4 weeks)",
                "",
                "High-priority violations should be addressed systematically to improve code quality.",
                "",
            ]
        )

    if total_p2 > 0:
        report_lines.extend(
            [
                "### Priority 3: Clean Up Medium-Priority Violations (P2)",
                "",
                f"**Count:** {total_p2} violations",
                "**Timeline:** Medium-term (1-2 months)",
                "",
                "Medium-priority violations can be addressed gradually as part of regular maintenance.",
                "",
            ]
        )

    # Footer
    report_lines.extend(
        [
            "---",
            "",
            "## Related Documentation",
            "",
            "**MA Principle Guidelines:**",
            "- `docs/developer/ma-principle.md` - Comprehensive guide with examples and patterns",
            "",
            "**Functional Requirements:**",
            "- `SPECIFICATIONS_AI.md:FR-108` - MA Principle specification",
            "- `SPECIFICATIONS_HU.md:FR-108` - MA Principle quick reference",
            "",
            "**Analysis Scripts:**",
            "- `scripts/analyze_ma_violations.py` - Python codebase analyzer",
            "- `scripts/analyze_ma_violations_docs.py` - Markdown documentation analyzer",
            "- `scripts/analyze_ma_compliance.py` - Unified compliance analyzer (this script)",
            "",
            "---",
            "",
            "**Report Status:** ✅ COMPLETE",
            f"**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}",
            "**Analyst:** Claude Code MA Compliance Analyzer",
            "",
        ]
    )

    # Write report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n✓ Report generated: {output_file}")
    print(f"\n📊 Summary: {total_all} violations ({total_p0} P0, {total_p1} P1, {total_p2} P2)")

    return exit_code


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze MA principle compliance across code and documentation")
    parser.add_argument(
        "--output",
        default="docs/reports/ma_compliance_report.md",
        help="Output report file (default: docs/reports/ma_compliance_report.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output JSON reports",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--code-only",
        action="store_true",
        help="Analyze code only",
    )
    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Analyze documentation only",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.code_only and args.docs_only:
        print("Error: Cannot specify both --code-only and --docs-only")
        return 1

    # Set up paths
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"
    reports_dir = project_root / "docs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    code_script = scripts_dir / "analyze_ma_violations.py"
    docs_script = scripts_dir / "analyze_ma_violations_docs.py"

    code_json = reports_dir / "ma_violations_codebase.json"
    docs_json = reports_dir / "ma_violations_documentation.json"

    # Run analyses
    code_data = None
    docs_data = None

    try:
        if not args.docs_only:
            if not code_script.exists():
                print(f"Error: Code analysis script not found: {code_script}")
                return 1
            code_data = run_analysis_script(str(code_script), str(code_json), args.verbose)

        if not args.code_only:
            if not docs_script.exists():
                print(f"Error: Documentation analysis script not found: {docs_script}")
                return 1
            docs_data = run_analysis_script(str(docs_script), str(docs_json), args.verbose)

        # Generate report
        exit_code = generate_report(code_data, docs_data, args.output)

        # Clean up JSON files if not requested
        if not args.json:
            if code_json.exists():
                code_json.unlink()
            if docs_json.exists():
                docs_json.unlink()

        return exit_code

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
