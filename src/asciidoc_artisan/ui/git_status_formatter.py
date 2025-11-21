"""
Git Status Formatter - Formats Git status for status bar display.

Extracted from StatusManager to reduce class size (MA principle).
Handles Git status display text, colors, and tooltips.
"""

from asciidoc_artisan.core import GitStatus


class GitStatusFormatter:
    """
    Git status formatter for status bar display.

    This class was extracted from StatusManager to reduce class size
    per MA principle (496→~382 lines).

    Handles:
    - Git status display state (text, color, description)
    - Git status tooltip generation
    """

    def determine_git_display_state(self, status: GitStatus) -> tuple[str, str, str]:
        """
        Determine Git status display text, color, and description.

        Args:
            status: GitStatus object

        Returns:
            Tuple of (text, color, status_desc)
        """
        branch = status.branch
        total_changes = status.modified_count + status.staged_count + status.untracked_count

        if status.has_conflicts:
            # Red for conflicts
            return (f"{branch} ⚠", "#ef4444", "Conflicts")
        elif total_changes > 0:
            # Yellow for changes (show count)
            return (f"{branch} ●{total_changes}", "#fbbf24", "Changes")
        else:
            # Green for clean
            return (f"{branch} ✓", "#4ade80", "Clean")

    def build_git_tooltip(self, status: GitStatus, status_desc: str, total_changes: int) -> str:
        """
        Build detailed Git status tooltip.

        Args:
            status: GitStatus object
            status_desc: Status description
            total_changes: Total number of changes

        Returns:
            Tooltip text
        """
        tooltip_parts = [
            f"Git Repository Status: {status_desc}",
            f"Branch: {status.branch}",
            "",
        ]

        if status.has_conflicts:
            tooltip_parts.append("⚠ CONFLICTS DETECTED - Resolve before committing")
            tooltip_parts.append("")

        if total_changes > 0:
            tooltip_parts.append("Changes:")
            if status.modified_count > 0:
                tooltip_parts.append(f"  Modified: {status.modified_count} files")
            if status.staged_count > 0:
                tooltip_parts.append(f"  Staged: {status.staged_count} files")
            if status.untracked_count > 0:
                tooltip_parts.append(f"  Untracked: {status.untracked_count} files")
        else:
            tooltip_parts.append("✓ Working tree clean")

        tooltip_parts.append("")
        tooltip_parts.append("Click to view detailed status (Ctrl+Shift+G)")

        return "\n".join(tooltip_parts)
