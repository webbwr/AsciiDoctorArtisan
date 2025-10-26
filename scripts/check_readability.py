#!/usr/bin/env python3
"""
Check readability of documentation files.

Validates that documentation meets Grade 5.0 reading level requirement (NFR-018).
Uses Flesch-Kincaid Grade Level metric.

Technical documents (for developers) are excluded from scoring by default since
Flesch-Kincaid penalizes necessary technical vocabulary.

Usage:
    python scripts/check_readability.py                    # Check all docs
    python scripts/check_readability.py SPECIFICATIONS.md  # Check specific file
    python scripts/check_readability.py --max-grade 6.0    # Custom threshold
    python scripts/check_readability.py --include-technical # Include technical docs
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Set

try:
    import textstat
except ImportError:
    print("Error: textstat not installed")
    print("Install with: pip install textstat")
    sys.exit(1)

# Default technical documents (excluded from readability scoring)
# These are developer-focused and appropriately use technical vocabulary
DEFAULT_TECHNICAL_DOCS = {
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "how-to-contribute.md",
    "DEVELOPMENT.md",
    "ARCHITECTURE.md",
    "API.md",
}


class ReadabilityChecker:
    """Check readability of markdown documentation."""

    def __init__(self, max_grade: float = 5.0, exclude_technical: bool = True):
        """
        Initialize checker.

        Args:
            max_grade: Maximum acceptable Flesch-Kincaid grade level
            exclude_technical: Skip technical documents from scoring
        """
        self.max_grade = max_grade
        self.exclude_technical = exclude_technical
        self.results: List[Tuple[Path, float, bool, bool]] = []  # Added is_technical flag
        self.skipped: List[Path] = []

    def is_technical_doc(self, file_path: Path) -> bool:
        """
        Check if file is a technical document.

        Args:
            file_path: Path to check

        Returns:
            True if file is technical (developer-focused)
        """
        return file_path.name in DEFAULT_TECHNICAL_DOCS

    def check_file(self, file_path: Path) -> Tuple[float, bool]:
        """
        Check readability of a single file.

        Args:
            file_path: Path to markdown file

        Returns:
            Tuple of (grade_level, passed)
        """
        try:
            # Check if this is a technical document
            is_technical = self.is_technical_doc(file_path)

            # Skip technical docs if exclude_technical is True
            if is_technical and self.exclude_technical:
                self.skipped.append(file_path)
                return 0.0, True  # Not scored, but not failed

            text = file_path.read_text(encoding="utf-8")

            # Remove markdown syntax that interferes with readability scoring
            cleaned_text = self._clean_markdown(text)

            # Calculate Flesch-Kincaid Grade Level
            grade_level = textstat.flesch_kincaid_grade(cleaned_text)

            passed = grade_level <= self.max_grade

            self.results.append((file_path, grade_level, passed, is_technical))

            return grade_level, passed

        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return 0.0, False

    def _clean_markdown(self, text: str) -> str:
        """
        Remove markdown syntax for readability analysis.

        Args:
            text: Raw markdown text

        Returns:
            Cleaned text without markdown syntax
        """
        import re

        # Remove code blocks (including language specifiers)
        text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`]+`", "", text)

        # Remove table structures
        text = re.sub(r"\|[-\s\|]+\|", "", text)  # Table separators
        text = re.sub(r"\|", " ", text)  # Remaining pipes

        # Remove headers (keep the text)
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

        # Remove links but keep text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        # Remove images
        text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)

        # Remove bold/italic markers (keep text)
        text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^\*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)

        # Remove list markers
        text = re.sub(r"^[\*\-\+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

        # Remove checkboxes
        text = re.sub(r"- \[[ x]\]\s+", "", text)

        # Remove horizontal rules
        text = re.sub(r"^[\-\*\_]{3,}$", "", text, flags=re.MULTILINE)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove extra whitespace
        text = re.sub(r"\n\n+", "\n\n", text)
        text = re.sub(r"  +", " ", text)

        return text.strip()

    def print_results(self):
        """Print readability check results."""
        print("\n" + "=" * 70)
        print("READABILITY CHECK RESULTS (NFR-018)")
        print("=" * 70)
        print(f"Target: Flesch-Kincaid Grade {self.max_grade} or below\n")

        # Print skipped technical documents first
        if self.skipped:
            print("Technical documents (skipped):")
            for file_path in sorted(self.skipped):
                print(f"  ⊘ SKIP  {file_path.name:30s}  (developer-focused)")
            print()

        passed_count = sum(1 for _, _, passed, _ in self.results if passed)
        total_count = len(self.results)

        if self.results:
            print("User-facing documents:")
            for file_path, grade_level, passed, is_technical in sorted(self.results):
                status = "✓ PASS" if passed else "✗ FAIL"
                tech_marker = " [TECH]" if is_technical else ""
                print(f"{status}  {file_path.name:30s}  Grade {grade_level:.1f}{tech_marker}")

        print("\n" + "=" * 70)
        print(f"Results: {passed_count}/{total_count} user-facing files passed")
        if self.skipped:
            print(f"Skipped: {len(self.skipped)} technical documents")
        print("=" * 70)

        if passed_count < total_count:
            print("\n⚠  Some files exceed the readability threshold!")
            print("   Simplify language in failed files to meet NFR-018.")
            return False
        else:
            print("\n✓  All user-facing files meet readability requirements!")
            if self.skipped:
                print("   Technical documents are appropriately detailed for developers.")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check documentation readability (NFR-018)"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (default: all documentation files)",
    )
    parser.add_argument(
        "--max-grade",
        type=float,
        default=5.0,
        help="Maximum acceptable grade level (default: 5.0)",
    )
    parser.add_argument(
        "--include-technical",
        action="store_true",
        help="Include technical documents in scoring (default: exclude)",
    )

    args = parser.parse_args()

    # Determine files to check
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        # Default: check all documentation files
        project_root = Path(__file__).parent.parent
        files_to_check = [
            project_root / "SPECIFICATIONS.md",
            project_root / "README.md",
            project_root / "CLAUDE.md",
            project_root / "SECURITY.md",
        ]
        # Add docs directory if it exists
        docs_dir = project_root / "docs"
        if docs_dir.exists():
            files_to_check.extend(docs_dir.glob("*.md"))

    # Filter to existing files
    files_to_check = [f for f in files_to_check if f.exists()]

    if not files_to_check:
        print("No files to check!")
        return 1

    # Run readability checks
    checker = ReadabilityChecker(
        max_grade=args.max_grade,
        exclude_technical=not args.include_technical
    )

    for file_path in files_to_check:
        checker.check_file(file_path)

    # Print results and exit with appropriate code
    success = checker.print_results()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
