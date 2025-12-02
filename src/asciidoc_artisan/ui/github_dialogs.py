"""
GitHub Dialogs - Pop-ups for Pull Requests and Issues.

This module re-exports dialog classes from their individual modules
for backward compatibility after MA principle extraction.

Dialog classes:
- BaseListDialog: Base class for PR/Issue list views (github_base_dialog.py)
- CreatePullRequestDialog: Form to create a new PR (github_pr_dialogs.py)
- PullRequestListDialog: Table showing all PRs (github_pr_dialogs.py)
- CreateIssueDialog: Form to create a new issue (github_issue_dialogs.py)
- IssueListDialog: Table showing all issues (github_issue_dialogs.py)

Validation helpers:
- _show_validation_error: Show red border on invalid field
- _clear_validation_error: Remove red border when fixed
- _validate_required_text: Check if field is not empty

Implements FR-054 to FR-060 (GitHub CLI Integration features).
"""

# Re-export all dialog classes for backward compatibility
from asciidoc_artisan.ui.github_base_dialog import BaseListDialog
from asciidoc_artisan.ui.github_issue_dialogs import CreateIssueDialog, IssueListDialog
from asciidoc_artisan.ui.github_pr_dialogs import (
    CreatePullRequestDialog,
    PullRequestListDialog,
)
from asciidoc_artisan.ui.github_validation import (
    _clear_validation_error,
    _show_validation_error,
    _validate_required_text,
    clear_validation_error,
    show_validation_error,
    validate_required_text,
)

__all__ = [
    # Dialog classes
    "BaseListDialog",
    "CreatePullRequestDialog",
    "PullRequestListDialog",
    "CreateIssueDialog",
    "IssueListDialog",
    # Validation helpers (public API)
    "show_validation_error",
    "clear_validation_error",
    "validate_required_text",
    # Validation helpers (backward compat with underscore prefix)
    "_show_validation_error",
    "_clear_validation_error",
    "_validate_required_text",
]
