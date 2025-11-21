#!/usr/bin/env python3
"""
Analyze codebase for MA (間) principle violations.

This script scans Python files for violations of the MA principle:
- Function length: ≤50 lines (excluding docstrings)
- Cyclomatic complexity: ≤10
- Parameter count: ≤4
- Nesting depth: ≤3
- Comment ratio: ≤15%
- Whitespace ratio: ≥2%
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MAMetrics:
    """MA principle metrics."""

    max_function_length: int = 50
    max_class_length: int = 300
    max_parameters: int = 4
    max_nesting: int = 3
    max_complexity: int = 10
    max_comment_ratio: float = 0.15
    min_whitespace_ratio: float = 0.02


@dataclass
class Violation:
    """MA principle violation."""

    file: str
    line: int
    type: str
    severity: str  # P0, P1, P2
    metric: str
    actual: Any
    threshold: Any
    message: str


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file: str
    lines: int
    functions: int
    classes: int
    violations: list[Violation] = field(default_factory=list)


class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity."""

    def __init__(self):
        self.complexity = 1
        self.nesting_depth = 0
        self.max_nesting = 0

    def visit_If(self, node):
        self.complexity += 1
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_While(self, node):
        self.complexity += 1
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_For(self, node):
        self.complexity += 1
        self.nesting_depth += 1
        self.max_nesting = max(self.max_nesting, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


class MAAnalyzer(ast.NodeVisitor):
    """Analyze Python AST for MA violations."""

    def __init__(self, file_path: Path, metrics: MAMetrics):
        self.file_path = file_path
        self.metrics = metrics
        self.violations: list[Violation] = []
        self.source_lines: list[str] = []

    def analyze(self, tree: ast.AST, source: str) -> list[Violation]:
        """Analyze AST for MA violations."""
        self.source_lines = source.splitlines()
        self.visit(tree)
        return self.violations

    def _get_function_body_lines(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Count function body lines excluding docstring."""
        if not node.body:
            return 0

        # Skip docstring
        start_idx = 0
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            start_idx = 1

        if start_idx >= len(node.body):
            return 0

        # Count lines from first real statement to end
        first_stmt = node.body[start_idx]
        last_stmt = node.body[-1]

        return last_stmt.end_lineno - first_stmt.lineno + 1  # type: ignore

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function for MA violations."""
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function for MA violations."""
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check function for violations."""
        # Function length
        body_lines = self._get_function_body_lines(node)
        if body_lines > self.metrics.max_function_length:
            severity = "P0" if body_lines > 100 else "P1"
            self.violations.append(
                Violation(
                    file=str(self.file_path),
                    line=node.lineno,
                    type="function_length",
                    severity=severity,
                    metric="lines",
                    actual=body_lines,
                    threshold=self.metrics.max_function_length,
                    message=f"Function '{node.name}' has {body_lines} lines (max: {self.metrics.max_function_length})",
                )
            )

        # Parameter count
        param_count = len(node.args.args)
        if param_count > self.metrics.max_parameters:
            self.violations.append(
                Violation(
                    file=str(self.file_path),
                    line=node.lineno,
                    type="parameter_count",
                    severity="P2",
                    metric="params",
                    actual=param_count,
                    threshold=self.metrics.max_parameters,
                    message=f"Function '{node.name}' has {param_count} parameters (max: {self.metrics.max_parameters})",
                )
            )

        # Complexity and nesting
        visitor = ComplexityVisitor()
        visitor.visit(node)

        if visitor.complexity > self.metrics.max_complexity:
            severity = "P1" if visitor.complexity > 15 else "P2"
            self.violations.append(
                Violation(
                    file=str(self.file_path),
                    line=node.lineno,
                    type="complexity",
                    severity=severity,
                    metric="cyclomatic",
                    actual=visitor.complexity,
                    threshold=self.metrics.max_complexity,
                    message=f"Function '{node.name}' has complexity {visitor.complexity} (max: {self.metrics.max_complexity})",
                )
            )

        if visitor.max_nesting > self.metrics.max_nesting:
            self.violations.append(
                Violation(
                    file=str(self.file_path),
                    line=node.lineno,
                    type="nesting",
                    severity="P2",
                    metric="depth",
                    actual=visitor.max_nesting,
                    threshold=self.metrics.max_nesting,
                    message=f"Function '{node.name}' has nesting depth {visitor.max_nesting} (max: {self.metrics.max_nesting})",
                )
            )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class for MA violations."""
        if node.end_lineno is None:
            self.generic_visit(node)
            return

        class_lines = node.end_lineno - node.lineno + 1

        if class_lines > self.metrics.max_class_length:
            severity = "P1" if class_lines > 500 else "P2"
            self.violations.append(
                Violation(
                    file=str(self.file_path),
                    line=node.lineno,
                    type="class_length",
                    severity=severity,
                    metric="lines",
                    actual=class_lines,
                    threshold=self.metrics.max_class_length,
                    message=f"Class '{node.name}' has {class_lines} lines (max: {self.metrics.max_class_length})",
                )
            )

        self.generic_visit(node)


def analyze_file(file_path: Path, metrics: MAMetrics) -> FileAnalysis:
    """Analyze a single Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return FileAnalysis(
            file=str(file_path),
            lines=0,
            functions=0,
            classes=0,
            violations=[],
        )

    # Count lines, functions, classes
    source_lines = source.splitlines()
    functions = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
    classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

    # Analyze AST
    analyzer = MAAnalyzer(file_path, metrics)
    violations = analyzer.analyze(tree, source)

    # Check comment ratio
    comment_lines = sum(1 for line in source_lines if line.strip().startswith("#"))
    comment_ratio = comment_lines / len(source_lines) if source_lines else 0

    if comment_ratio > metrics.max_comment_ratio:
        violations.append(
            Violation(
                file=str(file_path),
                line=1,
                type="comment_ratio",
                severity="P2",
                metric="ratio",
                actual=round(comment_ratio, 3),
                threshold=metrics.max_comment_ratio,
                message=f"File has {comment_ratio:.1%} comments (max: {metrics.max_comment_ratio:.0%})",
            )
        )

    # Check whitespace ratio
    blank_lines = sum(1 for line in source_lines if not line.strip())
    whitespace_ratio = blank_lines / len(source_lines) if source_lines else 0

    if whitespace_ratio < metrics.min_whitespace_ratio:
        violations.append(
            Violation(
                file=str(file_path),
                line=1,
                type="whitespace_ratio",
                severity="P2",
                metric="ratio",
                actual=round(whitespace_ratio, 3),
                threshold=metrics.min_whitespace_ratio,
                message=f"File has {whitespace_ratio:.1%} whitespace (min: {metrics.min_whitespace_ratio:.0%})",
            )
        )

    return FileAnalysis(
        file=str(file_path),
        lines=len(source_lines),
        functions=functions,
        classes=classes,
        violations=violations,
    )


def analyze_directory(directory: Path, metrics: MAMetrics, exclude_patterns: list[str]) -> list[FileAnalysis]:
    """Analyze all Python files in directory."""
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip excluded patterns
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        results.append(analyze_file(py_file, metrics))

    return results


def print_report(analyses: list[FileAnalysis], verbose: bool = False):
    """Print violation report."""
    print("=" * 80)
    print("MA (間) Principle Violation Analysis")
    print("=" * 80)
    print()

    # Collect all violations
    all_violations = []
    for analysis in analyses:
        all_violations.extend(analysis.violations)

    if not all_violations:
        print("✅ No MA principle violations found!")
        print()
        return

    # Group by severity
    p0_violations = [v for v in all_violations if v.severity == "P0"]
    p1_violations = [v for v in all_violations if v.severity == "P1"]
    p2_violations = [v for v in all_violations if v.severity == "P2"]

    # Summary
    print(f"⚠️  Total Violations: {len(all_violations)}")
    print(f"  - P0 (Critical): {len(p0_violations)} (>100 lines or complexity >15)")
    print(f"  - P1 (High): {len(p1_violations)} (>50 lines or complexity >10)")
    print(f"  - P2 (Medium): {len(p2_violations)} (other violations)")
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
        for v in sorted(p2_violations, key=lambda x: (x.file, x.line)):
            print(f"  {v.file}:{v.line}")
            print(f"    {v.message}")
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

    # Top violators
    print("Top 10 Files by Violation Count:")
    print("-" * 80)
    file_violations = {}
    for v in all_violations:
        file_violations[v.file] = file_violations.get(v.file, 0) + 1

    for file, count in sorted(file_violations.items(), key=lambda x: -x[1])[:10]:
        print(f"  {count:3d} violations: {file}")
    print()


def generate_json_report(analyses: list[FileAnalysis], output_path: Path):
    """Generate JSON report."""
    data = {
        "summary": {
            "total_files": len(analyses),
            "total_violations": sum(len(a.violations) for a in analyses),
            "p0_violations": sum(1 for a in analyses for v in a.violations if v.severity == "P0"),
            "p1_violations": sum(1 for a in analyses for v in a.violations if v.severity == "P1"),
            "p2_violations": sum(1 for a in analyses for v in a.violations if v.severity == "P2"),
        },
        "files": [
            {
                "file": a.file,
                "lines": a.lines,
                "functions": a.functions,
                "classes": a.classes,
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
    parser = argparse.ArgumentParser(description="Analyze codebase for MA principle violations")
    parser.add_argument("--directory", default="src/asciidoc_artisan", help="Directory to analyze")
    parser.add_argument("--json", help="Output JSON report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all violations including P2")
    parser.add_argument("--exclude", nargs="+", default=["__pycache__", ".pyc", "test_"], help="Patterns to exclude")

    args = parser.parse_args()

    # Create metrics
    metrics = MAMetrics()

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
    total_violations = sum(len(a.violations) for a in analyses)
    p0_violations = sum(1 for a in analyses for v in a.violations if v.severity == "P0")

    if p0_violations > 0:
        sys.exit(2)  # Exit code 2 for P0 violations
    elif total_violations > 0:
        sys.exit(1)  # Exit code 1 for any violations
    else:
        sys.exit(0)  # Exit code 0 for no violations


if __name__ == "__main__":
    main()
