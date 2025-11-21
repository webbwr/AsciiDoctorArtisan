"""
GitHub Command Builder - Builds GitHub CLI command arguments.

Extracted from GitHubCLIWorker to reduce class size (MA principle).
Handles construction of gh command arguments for various operations.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from asciidoc_artisan.workers.github_cli_worker import GitHubCLIWorker


class GitHubCommandBuilder:
    """
    Builder for GitHub CLI command arguments.

    This class was extracted from GitHubCLIWorker to reduce class size
    per MA principle (520→298 lines).

    Handles:
    - PR creation/listing command construction
    - Issue creation/listing command construction
    - Repository info command construction
    """

    def __init__(self, worker: "GitHubCLIWorker") -> None:
        """
        Initialize the command builder.

        Args:
            worker: GitHubCLIWorker instance to delegate execution to
        """
        self.worker = worker

    def create_pull_request(
        self,
        title: str,
        body: str,
        base: str,
        head: str,
        working_dir: str | None = None,
    ) -> None:
        """
        Create a GitHub pull request.

        Args:
            title: PR title
            body: PR description/body
            base: Base branch (e.g., "main")
            head: Head branch (e.g., "feature-x")
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with PR number and URL in data field
        """
        # Build gh pr create command with JSON output
        args = [
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base,
            "--head",
            head,
            "--json",
            "number,url",
        ]
        self.worker.run_gh_command(args, working_dir, operation="pr_create")

    def list_pull_requests(self, state: str | None = None, working_dir: str | None = None) -> None:
        """
        List pull requests in the repository.

        Args:
            state: Filter by state: "open", "closed", "merged", or None for all
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with list of PRs in data field
        """
        args = [
            "pr",
            "list",
            "--json",
            "number,title,state,url,headRefName,author,createdAt",
        ]

        if state:
            args.extend(["--state", state])

        self.worker.run_gh_command(args, working_dir, operation="pr_list")

    def create_issue(self, title: str, body: str, working_dir: str | None = None) -> None:
        """
        Create a GitHub issue.

        Args:
            title: Issue title
            body: Issue description/body
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with issue number and URL in data field
        """
        args = [
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--json",
            "number,url",
        ]
        self.worker.run_gh_command(args, working_dir, operation="issue_create")

    def list_issues(self, state: str | None = None, working_dir: str | None = None) -> None:
        """
        List issues in the repository.

        Args:
            state: Filter by state: "open", "closed", or None for all
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with list of issues in data field
        """
        args = [
            "issue",
            "list",
            "--json",
            "number,title,state,url,labels,author,createdAt",
        ]

        if state:
            args.extend(["--state", state])

        self.worker.run_gh_command(args, working_dir, operation="issue_list")

    def get_repo_info(self, working_dir: str | None = None) -> None:
        """
        Get repository information.

        Args:
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with repo info in data field
        """
        args = [
            "repo",
            "view",
            "--json",
            "name,nameWithOwner,description,stargazerCount,forkCount,defaultBranchRef,visibility,url",
        ]
        self.worker.run_gh_command(args, working_dir, operation="repo_info")
