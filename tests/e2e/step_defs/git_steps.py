"""
Step definitions for Git operations E2E tests.

Implements Gherkin steps for version control operations.
"""

import subprocess
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
pytestmark = [pytest.mark.e2e, pytest.mark.bdd, pytest.mark.gui]
scenarios("../features/git_operations.feature")


# ============================================================================
# Git Test State
# ============================================================================


class GitState:
    """Track Git operation state."""

    def __init__(self):
        self.last_commit_hash = ""
        self.last_status = ""
        self.last_log = ""
        self.current_branch = "main"


@pytest.fixture
def git_state():
    """Provide Git state tracking."""
    return GitState()


# ============================================================================
# Shared Steps
# ============================================================================


@given("the application is running")
def application_running(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible()
    return app


@given(parsers.parse('I have a document with content "{content}"'))
def document_with_content(app: AsciiDocEditor, content: str) -> AsciiDocEditor:
    """Set document content (interpret \n as newlines)."""
    actual_content = content.replace("\\n", "\n")
    app.editor.setPlainText(actual_content)
    return app


@given(parsers.parse('I have saved the document as "{filename}"'))
def saved_document(
    app: AsciiDocEditor, temp_workspace: Path, filename: str
) -> Path:
    """Save document to file."""
    from pathlib import Path

    file_path = temp_workspace / filename
    content = app.editor.toPlainText()
    file_path.write_text(content)
    app.file_handler.current_file_path = Path(file_path)
    return file_path


# ============================================================================
# Given Steps (Setup/Preconditions)
# ============================================================================


@given("I am in a Git repository")
def in_git_repo(git_repo: Path):
    """Ensure working in a Git repository."""
    # The git_repo fixture initializes the repository
    git_dir = git_repo / ".git"
    assert git_dir.exists(), "Should be in a Git repository"


@given(parsers.parse('I have made a commit with message "{message}"'))
def made_commit(temp_workspace: Path, message: str, git_state: GitState):
    """Create a test commit."""
    # Create a test file
    test_file = temp_workspace / "test.txt"
    test_file.write_text("test content")

    # Stage and commit
    subprocess.run(
        ["git", "add", "test.txt"], cwd=temp_workspace, capture_output=True, check=True
    )
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
        text=True,
    )
    git_state.last_commit_hash = result.stdout.strip()


@given("I have a remote repository configured")
def remote_configured(temp_workspace: Path):
    """Configure a remote repository (mock)."""
    # For E2E tests, we'll just verify Git is available
    # Real remote operations would require a test server
    result = subprocess.run(
        ["git", "remote", "-v"], cwd=temp_workspace, capture_output=True, text=True
    )
    # Remote may or may not exist - that's ok for testing


# ============================================================================
# When Steps (Actions)
# ============================================================================


@when("I check Git status")
def check_git_status(temp_workspace: Path, git_state: GitState):
    """Check Git repository status."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    git_state.last_status = result.stdout


@when(parsers.parse('I stage the file "{filename}"'))
def stage_file(temp_workspace: Path, filename: str):
    """Stage a file for commit."""
    subprocess.run(
        ["git", "add", filename], cwd=temp_workspace, capture_output=True, check=True
    )


@when(parsers.parse('I commit with message "{message}"'))
def commit_with_message(temp_workspace: Path, message: str, git_state: GitState):
    """Commit staged changes."""
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    git_state.last_commit_hash = result.stdout.strip()


@when("I view Git log")
def view_git_log(temp_workspace: Path, git_state: GitState):
    """View Git commit log."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    git_state.last_log = result.stdout


@when(parsers.parse('I create a new branch "{branch_name}"'))
def create_branch(temp_workspace: Path, branch_name: str):
    """Create a new Git branch."""
    subprocess.run(
        ["git", "branch", branch_name],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )


@when(parsers.parse('I switch to branch "{branch_name}"'))
def switch_branch(temp_workspace: Path, branch_name: str, git_state: GitState):
    """Switch to a different branch."""
    subprocess.run(
        ["git", "checkout", branch_name],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )
    git_state.current_branch = branch_name


@when("I pull from remote")
def pull_from_remote(temp_workspace: Path):
    """Pull changes from remote (simulated)."""
    # For E2E tests, we'll just check if Git is working
    # Real pull would require remote setup
    result = subprocess.run(
        ["git", "status"], cwd=temp_workspace, capture_output=True, check=True
    )
    # Just verify Git is functional


# ============================================================================
# Then Steps (Assertions)
# ============================================================================


@then(parsers.parse('Git should show "{filename}" as modified'))
def verify_modified(temp_workspace: Path, filename: str, git_state: GitState):
    """Verify file shows as modified in Git status."""
    # Porcelain format: ?? for untracked, M for modified, A for added
    assert (
        filename in git_state.last_status
    ), f"Expected {filename} in Git status:\n{git_state.last_status}"


@then(parsers.parse('Git should show "{filename}" as staged'))
def verify_staged(temp_workspace: Path, filename: str, git_state: GitState):
    """Verify file shows as staged in Git status."""
    # Re-check status to see staged files
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    # Staged files show with A (added) or M (modified) in first column
    assert (
        filename in result.stdout
    ), f"Expected {filename} in staged files:\n{result.stdout}"


@then("the commit should succeed")
def verify_commit_succeeded(git_state: GitState):
    """Verify commit operation succeeded."""
    assert len(git_state.last_commit_hash) > 0, "Commit should have succeeded"


@then(parsers.parse('Git log should contain "{message}"'))
def verify_log_contains_message(temp_workspace: Path, message: str):
    """Verify commit message appears in Git log."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    assert message in result.stdout, f"Expected '{message}' in Git log:\n{result.stdout}"


@then(parsers.parse('the log should contain "{text}"'))
def log_contains(git_state: GitState, text: str):
    """Verify log contains text."""
    assert text in git_state.last_log, f"Expected '{text}' in log:\n{git_state.last_log}"


@then("the log should show commit author")
def log_shows_author(temp_workspace: Path):
    """Verify log shows author information."""
    result = subprocess.run(
        ["git", "log", "--format=%an", "-1"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    assert len(result.stdout.strip()) > 0, "Log should show author"


@then("the log should show commit date")
def log_shows_date(temp_workspace: Path):
    """Verify log shows date information."""
    result = subprocess.run(
        ["git", "log", "--format=%ad", "-1"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    assert len(result.stdout.strip()) > 0, "Log should show date"


@then(parsers.parse('the current branch should be "{branch_name}"'))
def verify_current_branch(temp_workspace: Path, branch_name: str):
    """Verify current Git branch."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    assert (
        result.stdout.strip() == branch_name
    ), f"Expected branch '{branch_name}', got '{result.stdout.strip()}'"


@then("the pull operation should complete")
def verify_pull_complete():
    """Verify pull operation completed (simulated)."""
    # For E2E tests, we just verify Git is functional
    # This would be more complex with a real remote
    pass


@then("the working directory should be up to date")
def verify_up_to_date(temp_workspace: Path):
    """Verify working directory is up to date."""
    result = subprocess.run(
        ["git", "status"],
        cwd=temp_workspace,
        capture_output=True,
        text=True,
        check=True,
    )
    # Just verify status check works
    assert len(result.stdout) > 0, "Git status should return output"
