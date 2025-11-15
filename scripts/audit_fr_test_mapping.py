#!/usr/bin/env python3
"""
Audit FR-to-Test Mapping

Analyzes existing tests and maps them to functional requirements from
SPECIFICATIONS_AI.md. Generates FR_TEST_MAPPING.md showing compliance status.

Usage:
    python3 scripts/audit_fr_test_mapping.py
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict
import re

# FR to component mapping based on SPECIFICATIONS_AI.md and implementation files
FR_COMPONENT_MAP = {
    # Core Editing (FR-001-020)
    "FR-001": ["text_editor", "editor", "main_window"],
    "FR-002": ["line_number", "editor"],
    "FR-003": ["undo", "redo", "editor"],
    "FR-004": ["font", "editor", "settings"],
    "FR-005": ["editor_state", "state", "settings"],
    "FR-006": ["open", "file_operations"],
    "FR-007": ["save", "file_operations"],
    "FR-008": ["save_as", "file_operations"],
    "FR-009": ["new_document", "file_operations"],
    "FR-010": ["recent_files", "file_operations"],
    "FR-011": ["auto_save", "file_operations"],
    "FR-012": ["import", "docx", "document_converter"],
    "FR-013": ["import", "pdf", "document_converter"],
    "FR-014": ["import", "markdown", "document_converter"],
    "FR-015": ["preview", "live_preview", "preview_worker"],
    "FR-016": ["gpu", "preview_handler_gpu"],
    "FR-017": ["scroll", "sync", "scroll_manager"],
    "FR-018": ["incremental_renderer", "preview"],
    "FR-019": ["debounce", "preview"],
    "FR-020": ["theme", "preview"],

    # Export & Conversion (FR-021-025)
    "FR-021": ["export", "html", "pandoc"],
    "FR-022": ["export", "pdf", "pandoc"],
    "FR-023": ["export", "docx", "pandoc"],
    "FR-024": ["export", "markdown", "pandoc"],
    "FR-025": ["export", "ollama", "ai"],

    # Git Integration (FR-026-033)
    "FR-026": ["git", "repo", "git_worker"],
    "FR-027": ["git", "commit", "git_worker"],
    "FR-028": ["git", "pull", "git_worker"],
    "FR-029": ["git", "push", "git_worker"],
    "FR-030": ["git", "status_bar"],
    "FR-031": ["git", "status_dialog", "dialog"],
    "FR-032": ["git", "quick_commit"],
    "FR-033": ["git", "cancel"],

    # GitHub CLI (FR-034-038)
    "FR-034": ["github", "pr", "create"],
    "FR-035": ["github", "pr", "list"],
    "FR-036": ["github", "issue", "create"],
    "FR-037": ["github", "issue", "list"],
    "FR-038": ["github", "repo", "view"],

    # AI Features (FR-039-044)
    "FR-039": ["ollama", "chat", "panel"],
    "FR-040": ["ollama", "chat", "modes"],
    "FR-041": ["ollama", "model", "selection"],
    "FR-042": ["ollama", "history"],
    "FR-043": ["ollama", "integration"],
    "FR-044": ["ollama", "status", "indicator"],

    # Find & Replace (FR-045-049)
    "FR-045": ["find", "bar", "search"],
    "FR-046": ["replace", "search"],
    "FR-047": ["search", "engine"],
    "FR-048": ["search", "ui"],
    "FR-049": ["search", "performance"],

    # Spell Check (FR-050-054)
    "FR-050": ["spell", "check", "spell_checker"],
    "FR-051": ["spell", "suggestions"],
    "FR-052": ["spell", "dictionary", "custom"],
    "FR-053": ["spell", "language", "multi"],
    "FR-054": ["spell", "performance"],

    # UI & UX (FR-055-061)
    "FR-055": ["theme", "manager"],
    "FR-056": ["status", "bar"],
    "FR-057": ["metrics", "document"],
    "FR-058": ["menu", "structure"],
    "FR-059": ["preferences", "dialog", "settings"],
    "FR-060": ["keyboard", "shortcuts"],
    "FR-061": ["accessibility"],

    # Performance (FR-062-068)
    "FR-062": ["startup", "performance"],
    "FR-063": ["worker", "pool", "optimized"],
    "FR-064": ["async", "io"],
    "FR-065": ["lazy", "loading"],
    "FR-066": ["resource", "monitor"],
    "FR-067": ["import", "optimization"],
    "FR-067a": ["string", "optimization"],
    "FR-067b": ["pdf", "optimization"],
    "FR-067c": ["binary", "optimization"],
    "FR-068": ["memory", "management"],

    # Security (FR-069-072)
    "FR-069": ["atomic", "write", "file_operations"],
    "FR-070": ["path", "sanitization", "security"],
    "FR-071": ["subprocess", "safety", "security"],
    "FR-072": ["input", "validation", "security"],

    # Additional Features (FR-073-084)
    "FR-073": ["telemetry"],
    "FR-074": ["crash", "report"],
    "FR-075": ["type", "safety", "mypy"],
    "FR-076": ["test", "coverage", "pytest"],
    "FR-077": ["documentation", "docs"],
    "FR-078": ["help", "system"],
    "FR-079": ["update", "check"],
    "FR-080": ["plugin", "system"],
    "FR-081": ["custom", "theme"],
    "FR-082": ["export", "preset"],
    "FR-083": ["macro", "recording"],
    "FR-084": ["lru", "cache"],

    # Auto-Complete (FR-085-090)
    "FR-085": ["autocomplete", "engine"],
    "FR-086": ["autocomplete", "context"],
    "FR-087": ["autocomplete", "provider"],
    "FR-088": ["autocomplete", "fuzzy"],
    "FR-089": ["autocomplete", "widget", "ui"],
    "FR-090": ["autocomplete", "performance"],

    # Syntax Checking (FR-091-099)
    "FR-091": ["syntax", "checker"],
    "FR-092": ["syntax", "error", "detection"],
    "FR-093": ["syntax", "error", "display"],
    "FR-094": ["syntax", "quick", "fix"],
    "FR-095": ["syntax", "navigation"],
    "FR-096": ["syntax", "validation"],
    "FR-097": ["syntax", "rule", "engine"],
    "FR-098": ["syntax", "custom", "rule"],
    "FR-099": ["syntax", "performance"],

    # Templates (FR-100-107)
    "FR-100": ["template", "manager"],
    "FR-101": ["template", "builtin"],
    "FR-102": ["template", "custom"],
    "FR-103": ["template", "variable"],
    "FR-104": ["template", "engine"],
    "FR-105": ["template", "ui"],
    "FR-106": ["template", "browser"],
    "FR-107": ["template", "performance"],
}


def get_all_test_files():
    """Get list of all test files."""
    tests_dir = Path("tests")
    return sorted(tests_dir.rglob("test_*.py"))


def count_tests_in_file(test_file):
    """Count number of tests in a file using pytest --collect-only."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", str(test_file), "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Parse output to count tests
        lines = result.stdout.strip().split("\n")
        for line in reversed(lines):
            # Look for "X selected" or "X/Y deselected/selected"
            if "selected" in line:
                # Extract number before "selected"
                match = re.search(r"(\d+)\s+selected", line)
                if match:
                    return int(match.group(1))
        return 0
    except Exception as e:
        print(f"Warning: Could not count tests in {test_file}: {e}", file=sys.stderr)
        return 0


def map_file_to_frs(test_file):
    """Map a test file to likely FRs based on filename and component keywords."""
    file_str = str(test_file).lower()
    matched_frs = []

    for fr_id, keywords in FR_COMPONENT_MAP.items():
        for keyword in keywords:
            if keyword.lower() in file_str:
                matched_frs.append(fr_id)
                break  # One match per FR is enough

    return matched_frs


def generate_mapping():
    """Generate FR-to-test mapping."""
    print("Phase 1: Analyzing test files...")
    test_files = get_all_test_files()
    print(f"Found {len(test_files)} test files")

    # Map FRs to test files
    fr_to_tests = defaultdict(list)
    file_to_test_count = {}

    print("\nPhase 2: Mapping test files to FRs...")
    for i, test_file in enumerate(test_files, 1):
        print(f"  [{i}/{len(test_files)}] Analyzing {test_file.name}...", end="\r")
        test_count = count_tests_in_file(test_file)
        file_to_test_count[test_file] = test_count

        matched_frs = map_file_to_frs(test_file)
        for fr_id in matched_frs:
            fr_to_tests[fr_id].append((test_file, test_count))

    print("\n\nPhase 3: Generating summary...")

    # Print summary
    print(f"\n{'='*80}")
    print("FR-to-Test Mapping Summary")
    print(f"{'='*80}\n")

    total_frs_mapped = 0
    total_tests_mapped = 0

    for fr_id in sorted(FR_COMPONENT_MAP.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        if fr_id in fr_to_tests:
            tests = fr_to_tests[fr_id]
            total_test_count = sum(count for _, count in tests)
            total_frs_mapped += 1
            total_tests_mapped += total_test_count

            print(f"{fr_id}: {len(tests)} test files, {total_test_count} tests")
            for test_file, count in tests:
                print(f"  - {test_file.relative_to('tests')} ({count} tests)")
        else:
            print(f"{fr_id}: ⚠️  NO TESTS FOUND")

    print(f"\n{'='*80}")
    print(f"Total FRs with tests: {total_frs_mapped}/107")
    print(f"Total FRs without tests: {107 - total_frs_mapped}/107")
    print(f"Total tests mapped: {total_tests_mapped}")
    print(f"{'='*80}\n")

    return fr_to_tests, file_to_test_count


if __name__ == "__main__":
    generate_mapping()
