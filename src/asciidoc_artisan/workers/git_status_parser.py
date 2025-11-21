"""
Git Status Parser - Parses git status output into structured data.

Extracted from GitWorker to reduce class size (MA principle).
Handles parsing of git status --porcelain=v2 and git diff --numstat outputs.
"""

import logging
from typing import Any

from asciidoc_artisan.core import GitStatus

logger = logging.getLogger(__name__)


class GitStatusParser:
    """
    Parser for git status and diff output formats.

    This class was extracted from GitWorker to reduce class size per MA principle.

    Handles:
    - Porcelain v2 format parsing (git status --porcelain=v2)
    - Branch information extraction
    - File status code interpretation
    - Line count statistics from git diff --numstat
    """

    def parse_branch_head(self, line: str) -> str:
        """
        Parse branch name from git status v2 header.

        Args:
            line: Branch head line (e.g., "# branch.head main")

        Returns:
            Branch name or "HEAD (detached)" for detached state
        """
        branch = line.split(" ", 2)[2]
        if branch == "(detached)":
            branch = "HEAD (detached)"
        return branch

    def parse_ahead_behind(self, line: str) -> tuple[int, int]:
        """
        Parse ahead/behind counts from git status v2 header.

        Args:
            line: Branch ahead/behind line (e.g., "# branch.ab +2 -1")

        Returns:
            Tuple of (ahead_count, behind_count)
        """
        parts = line.split()
        if len(parts) >= 4:
            try:
                ahead = int(parts[2].replace("+", ""))
                behind = int(parts[3].replace("-", ""))
                return ahead, behind
            except ValueError:
                logger.warning(f"Failed to parse branch.ab: {line}")
        return 0, 0

    def parse_tracked_file_status(self, parts: list[str]) -> tuple[bool, bool, bool]:
        """
        Parse tracked file status codes.

        Args:
            parts: Split status line parts

        Returns:
            Tuple of (has_conflict, is_staged, is_modified)
        """
        if len(parts) < 2:
            return False, False, False

        xy_status = parts[1]
        has_conflict = "U" in xy_status
        x_status = xy_status[0] if len(xy_status) > 0 else "."
        y_status = xy_status[1] if len(xy_status) > 1 else "."
        is_staged = x_status != "."
        is_modified = y_status != "."

        return has_conflict, is_staged, is_modified

    def parse_status_line(self, line: str) -> dict[str, Any]:
        """
        Parse a single git status line and return updates to counters.

        Args:
            line: Single line from git status --porcelain=v2 output

        Returns:
            Dictionary with keys: branch, ahead_behind, has_conflict, modified, staged, untracked
        """
        result: dict[str, Any] = {
            "branch": None,
            "ahead_behind": None,
            "has_conflict": False,
            "modified": 0,
            "staged": 0,
            "untracked": 0,
        }

        # Parse branch headers
        if line.startswith("# branch.head "):
            result["branch"] = self.parse_branch_head(line)
        elif line.startswith("# branch.ab "):
            result["ahead_behind"] = self.parse_ahead_behind(line)

        # Parse tracked file status
        elif line.startswith("1 ") or line.startswith("2 "):
            parts = line.split(maxsplit=8)
            conflict, staged, modified = self.parse_tracked_file_status(parts)
            if conflict:
                result["has_conflict"] = True
            if staged:
                result["staged"] = 1
            if modified:
                result["modified"] = 1

        # Unmerged entry (always a conflict)
        elif line.startswith("u "):
            result["has_conflict"] = True
            result["modified"] = 1
            result["staged"] = 1

        # Untracked file
        elif line.startswith("? "):
            result["untracked"] = 1

        return result

    def parse_git_status_v2(self, stdout: str) -> GitStatus:
        """
        Parse git status --porcelain=v2 output into GitStatus model.

        Porcelain v2 format: https://git-scm.com/docs/git-status#_porcelain_format_version_2

        Status codes (XY):
        - First char (X): status in index (staged)
        - Second char (Y): status in working tree
        - '.' = unmodified, 'M' = modified, 'A' = added, 'D' = deleted, 'U' = unmerged

        Args:
            stdout: Output from git status --porcelain=v2 --branch

        Returns:
            GitStatus with parsed repository information
        """
        # Initialize counters
        branch = "unknown"
        modified_count = 0
        staged_count = 0
        untracked_count = 0
        has_conflicts = False
        ahead_count = 0
        behind_count = 0

        # Parse each line
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            # Parse line and update counters
            result = self.parse_status_line(line)
            if result["branch"]:
                branch = result["branch"]
            if result["ahead_behind"]:
                ahead_count, behind_count = result["ahead_behind"]
            if result["has_conflict"]:
                has_conflicts = True
            modified_count += result["modified"]
            staged_count += result["staged"]
            untracked_count += result["untracked"]

        # Calculate dirty status
        is_dirty = modified_count > 0 or staged_count > 0 or untracked_count > 0

        return GitStatus(
            branch=branch,
            modified_count=modified_count,
            staged_count=staged_count,
            untracked_count=untracked_count,
            has_conflicts=has_conflicts,
            ahead_count=ahead_count,
            behind_count=behind_count,
            is_dirty=is_dirty,
        )

    def parse_detailed_status_v2(
        self, stdout: str
    ) -> tuple[str, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        """
        Parse git status --porcelain=v2 output into file lists.

        Args:
            stdout: Output from git status --porcelain=v2 --branch

        Returns:
            Tuple of (branch, modified_files, staged_files, untracked_files)
            Each file list contains dicts with keys: path, status
        """
        branch = "unknown"
        modified_files: list[dict[str, str]] = []
        staged_files: list[dict[str, str]] = []
        untracked_files: list[dict[str, str]] = []

        lines = stdout.strip().split("\n")

        for line in lines:
            if not line:
                continue

            # Parse branch header
            if line.startswith("# branch.head "):
                branch = line.split(" ", 2)[2]
                if branch == "(detached)":
                    branch = "HEAD (detached)"

            # Parse tracked files (format: 1/2 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>)
            elif line.startswith("1 ") or line.startswith("2 "):
                parts = line.split(maxsplit=8)
                if len(parts) >= 9:
                    xy_status = parts[1]
                    file_path = parts[8]

                    # X = index status (staged), Y = working tree status
                    x_status = xy_status[0] if len(xy_status) > 0 else "."
                    y_status = xy_status[1] if len(xy_status) > 1 else "."

                    # Add to staged files if X != '.'
                    if x_status != ".":
                        staged_files.append({"path": file_path, "status": x_status})

                    # Add to modified files if Y != '.'
                    if y_status != ".":
                        modified_files.append({"path": file_path, "status": y_status})

            # Parse untracked files (format: ? <path>)
            elif line.startswith("? "):
                file_path = line[2:]  # Skip "? " prefix
                untracked_files.append({"path": file_path})

        return branch, modified_files, staged_files, untracked_files

    def parse_numstat_output(self, stdout: str) -> dict[str, dict[str, int]]:
        """
        Parse git diff --numstat output into line counts dictionary.

        Args:
            stdout: Output from git diff --numstat command

        Returns:
            Dictionary mapping file paths to {added, deleted} dicts

        Format:
            <added>\t<deleted>\t<path>
            Binary files show "-" for added/deleted
        """
        line_counts = {}
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) >= 3:
                added = int(parts[0]) if parts[0] != "-" else 0
                deleted = int(parts[1]) if parts[1] != "-" else 0
                path = parts[2]
                line_counts[path] = {"added": added, "deleted": deleted}

        return line_counts

    def update_files_with_line_counts(
        self, files: list[dict[str, Any]], line_counts: dict[str, dict[str, int]]
    ) -> None:
        """
        Update file dictionaries with line change counts.

        Args:
            files: List of file dicts (modified in place)
            line_counts: Dictionary mapping paths to {added, deleted} dicts
        """
        for file_dict in files:
            path = file_dict["path"]
            if path in line_counts:
                file_dict["lines_added"] = line_counts[path]["added"]
                file_dict["lines_deleted"] = line_counts[path]["deleted"]
            else:
                file_dict["lines_added"] = 0
                file_dict["lines_deleted"] = 0
