#!/usr/bin/env python3
"""
Analyze documentation for MA (間) principle violations.

This script scans Markdown files for violations of the MA principle:
- Line length: ≤88 characters
- Whitespace ratio: ≥2% (blank lines)
- Paragraph length: ≤10 lines
- Reading grade: ≤5.0 (Flesch-Kincaid)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import textstat
except ImportError:
    print("Warning: textstat not installed. Reading grade checks will be skipped.")
    print("Install with: pip install textstat")
    textstat = None


@dataclass
class DocMAMetrics:
    """MA principle metrics for documentation."""

    max_line_length: int = 88
    min_whitespace_ratio: float = 0.02
    max_paragraph_lines: int = 10
    max_reading_grade: float = 5.0


@dataclass
class DocViolation:
    """Documentation MA principle violation."""

    file: str
    line: int
    type: str
    severity: str  # P0, P1, P2
    metric: str
    actual: Any
    threshold: Any
    message: str


@dataclass
class DocAnalysis:
    """Analysis results for a single doc file."""

    file: str
    lines: int
    violations: list[DocViolation] = field(default_factory=list)


def analyze_doc_file(file_path: Path, metrics: DocMAMetrics) -> DocAnalysis:
    """Analyze a single Markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return DocAnalysis(file=str(file_path), lines=0, violations=[])

    lines = content.splitlines()
    violations = []

    # Check line length
    for i, line in enumerate(lines, start=1):
        # Skip code blocks and tables
        if line.strip().startswith(("```", "|", "    ")):
            continue

        if len(line) > metrics.max_line_length:
            violations.append(
                DocViolation(
                    file=str(file_path),
                    line=i,
                    type="line_length",
                    severity="P2",
                    metric="characters",
                    actual=len(line),
                    threshold=metrics.max_line_length,
                    message=f"Line exceeds {metrics.max_line_length} characters ({len(line)} chars)",
                )
            )

    # Check whitespace ratio
    blank_lines = sum(1 for line in lines if not line.strip())
    whitespace_ratio = blank_lines / len(lines) if lines else 0

    if whitespace_ratio < metrics.min_whitespace_ratio:
        violations.append(
            DocViolation(
                file=str(file_path),
                line=1,
                type="whitespace_ratio",
                severity="P1",
                metric="ratio",
                actual=round(whitespace_ratio, 3),
                threshold=metrics.min_whitespace_ratio,
                message=f"File has {whitespace_ratio:.1%} whitespace (min: {metrics.min_whitespace_ratio:.0%})",
            )
        )

    # Check paragraph length
    paragraph_start = None
    paragraph_lines = []

    for i, line in enumerate(lines, start=1):
        # Skip code blocks, headings, lists, tables
        if re.match(r"^(```|#+\s|[-*]\s|\d+\.\s|\|)", line.strip()):
            if paragraph_start and paragraph_lines:
                # Check previous paragraph
                if len(paragraph_lines) > metrics.max_paragraph_lines:
                    violations.append(
                        DocViolation(
                            file=str(file_path),
                            line=paragraph_start,
                            type="paragraph_length",
                            severity="P2",
                            metric="lines",
                            actual=len(paragraph_lines),
                            threshold=metrics.max_paragraph_lines,
                            message=f"Paragraph has {len(paragraph_lines)} lines (max: {metrics.max_paragraph_lines})",
                        )
                    )
            paragraph_start = None
            paragraph_lines = []
            continue

        # Blank line ends paragraph
        if not line.strip():
            if paragraph_start and paragraph_lines:
                if len(paragraph_lines) > metrics.max_paragraph_lines:
                    violations.append(
                        DocViolation(
                            file=str(file_path),
                            line=paragraph_start,
                            type="paragraph_length",
                            severity="P2",
                            metric="lines",
                            actual=len(paragraph_lines),
                            threshold=metrics.max_paragraph_lines,
                            message=f"Paragraph has {len(paragraph_lines)} lines (max: {metrics.max_paragraph_lines})",
                        )
                    )
            paragraph_start = None
            paragraph_lines = []
            continue

        # Continue paragraph
        if paragraph_start is None:
            paragraph_start = i
        paragraph_lines.append(line)

    # Check last paragraph
    if paragraph_start and paragraph_lines:
        if len(paragraph_lines) > metrics.max_paragraph_lines:
            violations.append(
                DocViolation(
                    file=str(file_path),
                    line=paragraph_start,
                    type="paragraph_length",
                    severity="P2",
                    metric="lines",
                    actual=len(paragraph_lines),
                    threshold=metrics.max_paragraph_lines,
                    message=f"Paragraph has {len(paragraph_lines)} lines (max: {metrics.max_paragraph_lines})",
                )
            )

    # Check reading grade (if textstat available)
    if textstat:
        # Extract prose content (skip code blocks)
        prose_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if not in_code_block and line.strip() and not re.match(r"^(#+\s|[-*]\s|\d+\.\s|\|)", line.strip()):
                # Remove markdown formatting
                clean_line = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", line)  # Links
                clean_line = re.sub(r"[*_`]", "", clean_line)  # Emphasis
                clean_line = re.sub(r"^>\s*", "", clean_line)  # Quotes
                prose_lines.append(clean_line)

        prose = " ".join(prose_lines)

        if prose and len(prose) > 100:  # Need enough text for meaningful score
            try:
                grade = textstat.flesch_kincaid_grade(prose)
                if grade > metrics.max_reading_grade:
                    severity = "P0" if grade > 10 else "P1"
                    violations.append(
                        DocViolation(
                            file=str(file_path),
                            line=1,
                            type="reading_grade",
                            severity=severity,
                            metric="grade",
                            actual=round(grade, 1),
                            threshold=metrics.max_reading_grade,
                            message=f"Reading grade {grade:.1f} (max: {metrics.max_reading_grade})",
                        )
                    )
            except Exception:
                pass  # Skip if textstat fails

    return DocAnalysis(
        file=str(file_path),
        lines=len(lines),
        violations=violations,
    )


def analyze_directory(directory: Path, metrics: DocMAMetrics, exclude_patterns: list[str]) -> list[DocAnalysis]:
    """Analyze all Markdown files in directory."""
    results = []

    for md_file in directory.rglob("*.md"):
        # Skip excluded patterns
        if any(pattern in str(md_file) for pattern in exclude_patterns):
            continue

        results.append(analyze_doc_file(md_file, metrics))

    return results


def print_report(analyses: list[DocAnalysis], verbose: bool = False):
    """Print violation report."""
    print("=" * 80)
    print("MA (間) Principle Documentation Violation Analysis")
    print("=" * 80)
    print()

    # Collect all violations
    all_violations = []
    for analysis in analyses:
        all_violations.extend(analysis.violations)

    if not all_violations:
        print("✅ No MA principle violations found in documentation!")
        print()
        return

    # Group by severity
    p0_violations = [v for v in all_violations if v.severity == "P0"]
    p1_violations = [v for v in all_violations if v.severity == "P1"]
    p2_violations = [v for v in all_violations if v.severity == "P2"]

    # Summary
    print(f"⚠️  Total Violations: {len(all_violations)}")
    print(f"  - P0 (Critical): {len(p0_violations)} (grade >10)")
    print(f"  - P1 (High): {len(p1_violations)} (grade >5 or low whitespace)")
    print(f"  - P2 (Medium): {len(p2_violations)} (line length, paragraph length)")
    print()

    # P0 violations
    if p0_violations:
        print("🔴 P0 Violations (Critical - Fix Immediately):")
        print("-" * 80)
        for v in sorted(p0_violations, key=lambda x: (x.file, x.line)):
            print(f"  {v.file}:{v.line}")
            print(f"    {v.message}")
        print()

    # P1 violations
    if p1_violations:
        print("🟡 P1 Violations (High Priority):")
        print("-" * 80)
        for v in sorted(p1_violations, key=lambda x: (x.file, x.line)):
            print(f"  {v.file}:{v.line}")
            print(f"    {v.message}")
        print()

    # P2 violations (only if verbose)
    if p2_violations and verbose:
        print("🟢 P2 Violations (Medium Priority):")
        print("-" * 80)
        # Group by file
        files_with_p2 = {}
        for v in p2_violations:
            files_with_p2.setdefault(v.file, []).append(v)

        for file, violations in sorted(files_with_p2.items()):
            print(f"  {file}: {len(violations)} violations")
        print()

    # Statistics by type
    print("=" * 80)
    print("Violation Statistics:")
    print("=" * 80)
    violation_types = {}
    for v in all_violations:
        violation_types[v.type] = violation_types.get(v.type, 0) + 1

    for vtype, count in sorted(violation_types.items(), key=lambda x: -x[1]):
        print(f"  {vtype}: {count}")
    print()


def generate_json_report(analyses: list[DocAnalysis], output_path: Path):
    """Generate JSON report."""
    all_violations = []
    for analysis in analyses:
        all_violations.extend(analysis.violations)

    data = {
        "summary": {
            "total_files": len(analyses),
            "total_violations": len(all_violations),
            "p0_violations": sum(1 for v in all_violations if v.severity == "P0"),
            "p1_violations": sum(1 for v in all_violations if v.severity == "P1"),
            "p2_violations": sum(1 for v in all_violations if v.severity == "P2"),
        },
        "files": [
            {
                "file": a.file,
                "lines": a.lines,
                "violations": [
                    {
                        "line": v.line,
                        "type": v.type,
                        "severity": v.severity,
                        "metric": v.metric,
                        "actual": v.actual,
                        "threshold": v.threshold,
                        "message": v.message,
                    }
                    for v in a.violations
                ],
            }
            for a in analyses
            if a.violations  # Only include files with violations
        ],
    }

    output_path.write_text(json.dumps(data, indent=2))
    print(f"JSON report written to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze documentation for MA principle violations")
    parser.add_argument("--directory", default="docs", help="Directory to analyze")
    parser.add_argument("--json", help="Output JSON report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all violations including P2")
    parser.add_argument(
        "--exclude", nargs="+", default=["node_modules", ".git", "__pycache__"], help="Patterns to exclude"
    )

    args = parser.parse_args()

    # Create metrics
    metrics = DocMAMetrics()

    # Analyze directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {args.directory} not found")
        sys.exit(1)

    print(f"Analyzing {args.directory}...")
    analyses = analyze_directory(directory, metrics, args.exclude)

    # Print report
    print_report(analyses, verbose=args.verbose)

    # Generate JSON report
    if args.json:
        generate_json_report(analyses, Path(args.json))

    # Exit code
    all_violations = []
    for analysis in analyses:
        all_violations.extend(analysis.violations)

    p0_violations = sum(1 for v in all_violations if v.severity == "P0")

    if p0_violations > 0:
        sys.exit(2)  # Exit code 2 for P0 violations
    elif all_violations:
        sys.exit(1)  # Exit code 1 for any violations
    else:
        sys.exit(0)  # Exit code 0 for no violations


if __name__ == "__main__":
    main()
