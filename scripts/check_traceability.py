#!/usr/bin/env python3
"""
Automated Traceability Checker - Validates FR/NFR references.

This script validates that all requirements in SPECIFICATION_COMPLETE.md
have corresponding implementations in the codebase.

Usage:
    python scripts/check_traceability.py                 # Full check
    python scripts/check_traceability.py --verbose       # Detailed output
    python scripts/check_traceability.py --matrix        # Generate matrix
    python scripts/check_traceability.py --requirement FR-001  # Check one
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class TraceabilityChecker:
    """Check traceability between requirements and code."""

    def __init__(self, project_root: Path):
        """
        Initialize checker.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.spec_file = project_root / ".specify" / "SPECIFICATION_COMPLETE.md"
        self.src_dir = project_root / "src"

        self.requirements: Dict[str, Dict] = {}
        self.code_references: Dict[str, Set[str]] = {}
        self.broken_references: List[Tuple[str, str]] = []
        self.missing_implementations: List[str] = []

    def extract_requirements(self) -> None:
        """Extract all FR/NFR requirements from specification."""
        if not self.spec_file.exists():
            print(f"Error: Specification file not found: {self.spec_file}")
            sys.exit(1)

        content = self.spec_file.read_text(encoding="utf-8")

        # Pattern to match requirement headers like "#### FR-001:" or "### NFR-001:"
        req_pattern = r"(?:^|\n)#{3,4}\s+((?:FR|NFR)-\d{3}(?:-\d{3})?):?\s+(.+?)(?:\n|$)"

        for match in re.finditer(req_pattern, content):
            req_id = match.group(1)
            req_title = match.group(2).strip()

            # Extract implementation reference if exists
            impl_pattern = rf"{re.escape(req_id)}[\s\S]*?\*\*Implementation\*\*:\s*`([^`]+)`"
            impl_match = re.search(impl_pattern, content)
            impl_ref = impl_match.group(1) if impl_match else None

            self.requirements[req_id] = {
                "title": req_title,
                "implementation": impl_ref
            }

    def find_code_references(self) -> None:
        """Find all FR/NFR references in source code using grep."""
        # Get all requirement IDs
        req_ids = list(self.requirements.keys())

        if not req_ids:
            print("No requirements found!")
            return

        # Search for each requirement in source code
        for req_id in req_ids:
            # Use grep to find files mentioning this requirement
            try:
                result = subprocess.run(
                    ["grep", "-r", "-l", req_id, str(self.src_dir)],
                    capture_output=True,
                    text=True,
                    check=False
                )

                if result.returncode == 0:
                    # Found files - store them
                    files = result.stdout.strip().split("\n")
                    # Convert to relative paths
                    rel_files = set()
                    for f in files:
                        if f:
                            try:
                                rel_path = Path(f).relative_to(self.project_root)
                                rel_files.add(str(rel_path))
                            except ValueError:
                                rel_files.add(f)
                    self.code_references[req_id] = rel_files
                else:
                    # Not found in code
                    self.code_references[req_id] = set()

            except Exception as e:
                print(f"Error searching for {req_id}: {e}")
                self.code_references[req_id] = set()

    def validate_implementation_references(self) -> None:
        """Validate that implementation references point to existing files."""
        for req_id, req_data in self.requirements.items():
            impl_ref = req_data.get("implementation")

            if not impl_ref:
                continue

            # Parse implementation reference (format: "path/file.py:line" or just "path/file.py")
            file_path = impl_ref.split(":")[0] if ":" in impl_ref else impl_ref

            # Check if file exists
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.broken_references.append((req_id, impl_ref))

    def find_missing_implementations(self) -> None:
        """Find requirements with no code references."""
        for req_id, files in self.code_references.items():
            if not files and req_id in self.requirements:
                # Check if it has an implementation reference
                impl_ref = self.requirements[req_id].get("implementation")
                if impl_ref:
                    # Has spec reference but not found in code search
                    # Might be in a file we didn't search (tests, etc.)
                    continue
                else:
                    # No implementation reference and not found in code
                    self.missing_implementations.append(req_id)

    def print_results(self, verbose: bool = False) -> bool:
        """
        Print traceability check results.

        Args:
            verbose: Print detailed information

        Returns:
            True if all checks pass, False otherwise
        """
        print("\n" + "=" * 70)
        print("TRACEABILITY CHECK RESULTS")
        print("=" * 70)

        total_reqs = len(self.requirements)
        traced_reqs = sum(1 for files in self.code_references.values() if files)

        print(f"\nTotal Requirements: {total_reqs}")
        print(f"Requirements with Code References: {traced_reqs}")
        print(f"Traceability Rate: {traced_reqs/total_reqs*100:.1f}%")

        # Broken implementation references
        if self.broken_references:
            print(f"\n⚠️  BROKEN IMPLEMENTATION REFERENCES: {len(self.broken_references)}")
            for req_id, ref in self.broken_references:
                print(f"  - {req_id}: {ref} (file not found)")
        else:
            print("\n✓ No broken implementation references")

        # Missing implementations
        if self.missing_implementations:
            print(f"\n⚠️  MISSING IMPLEMENTATIONS: {len(self.missing_implementations)}")
            if verbose:
                for req_id in self.missing_implementations:
                    title = self.requirements[req_id]["title"]
                    print(f"  - {req_id}: {title}")
            else:
                print(f"  Run with --verbose to see details")
        else:
            print("\n✓ All requirements have implementations")

        # Verbose output - show all mappings
        if verbose:
            print("\n" + "-" * 70)
            print("DETAILED TRACEABILITY")
            print("-" * 70)

            for req_id in sorted(self.requirements.keys()):
                title = self.requirements[req_id]["title"]
                files = self.code_references.get(req_id, set())
                impl_ref = self.requirements[req_id].get("implementation")

                print(f"\n{req_id}: {title}")
                if impl_ref:
                    status = "✗" if (req_id, impl_ref) in self.broken_references else "✓"
                    print(f"  Spec: {status} {impl_ref}")
                if files:
                    print(f"  Code: ✓ Found in {len(files)} file(s)")
                    for f in sorted(files):
                        print(f"        - {f}")
                elif not impl_ref:
                    print(f"  Code: ✗ No references found")

        print("\n" + "=" * 70)

        # Determine pass/fail
        has_issues = bool(self.broken_references or self.missing_implementations)

        if has_issues:
            print("❌ TRACEABILITY CHECK FAILED")
            print("   Fix broken references and missing implementations")
            return False
        else:
            print("✅ TRACEABILITY CHECK PASSED")
            print("   All requirements traced to code")
            return True

    def generate_matrix(self, output_file: Path) -> None:
        """
        Generate traceability matrix CSV.

        Args:
            output_file: Path to output CSV file
        """
        import csv

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Requirement ID", "Title", "Spec Reference", "Code Files", "Status"])

            # Data rows
            for req_id in sorted(self.requirements.keys()):
                title = self.requirements[req_id]["title"]
                impl_ref = self.requirements[req_id].get("implementation", "")
                files = self.code_references.get(req_id, set())

                # Determine status
                if (req_id, impl_ref) in self.broken_references:
                    status = "BROKEN_REF"
                elif req_id in self.missing_implementations:
                    status = "MISSING"
                elif files or impl_ref:
                    status = "TRACED"
                else:
                    status = "UNKNOWN"

                # Format file list
                file_list = "; ".join(sorted(files)) if files else ""

                writer.writerow([req_id, title, impl_ref, file_list, status])

        print(f"\n✓ Traceability matrix written to: {output_file}")

    def check_single_requirement(self, req_id: str) -> None:
        """
        Check a single requirement.

        Args:
            req_id: Requirement ID (e.g., "FR-001")
        """
        if req_id not in self.requirements:
            print(f"Error: Requirement {req_id} not found in specification")
            return

        print("\n" + "=" * 70)
        print(f"REQUIREMENT: {req_id}")
        print("=" * 70)

        req_data = self.requirements[req_id]
        print(f"\nTitle: {req_data['title']}")

        impl_ref = req_data.get("implementation")
        if impl_ref:
            status = "✗ BROKEN" if (req_id, impl_ref) in self.broken_references else "✓ Valid"
            print(f"\nSpec Reference: {status}")
            print(f"  {impl_ref}")
        else:
            print(f"\nSpec Reference: None specified")

        files = self.code_references.get(req_id, set())
        if files:
            print(f"\nCode References: ✓ Found in {len(files)} file(s)")
            for f in sorted(files):
                print(f"  - {f}")
        else:
            print(f"\nCode References: ✗ No references found")

        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check traceability between requirements and code"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed traceability information"
    )
    parser.add_argument(
        "--matrix", "-m",
        action="store_true",
        help="Generate traceability matrix CSV"
    )
    parser.add_argument(
        "--requirement", "-r",
        help="Check a single requirement (e.g., FR-001)"
    )
    parser.add_argument(
        "--output", "-o",
        default="traceability_matrix.csv",
        help="Output file for matrix (default: traceability_matrix.csv)"
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Create checker
    checker = TraceabilityChecker(project_root)

    # Extract requirements from spec
    print("Extracting requirements from specification...")
    checker.extract_requirements()
    print(f"Found {len(checker.requirements)} requirements")

    # Find code references
    print("Searching for requirement references in code...")
    checker.find_code_references()

    # Validate implementation references
    print("Validating implementation references...")
    checker.validate_implementation_references()

    # Find missing implementations
    checker.find_missing_implementations()

    # Single requirement check
    if args.requirement:
        checker.check_single_requirement(args.requirement)
        return 0

    # Generate matrix if requested
    if args.matrix:
        output_path = project_root / args.output
        checker.generate_matrix(output_path)

    # Print results
    success = checker.print_results(verbose=args.verbose)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
