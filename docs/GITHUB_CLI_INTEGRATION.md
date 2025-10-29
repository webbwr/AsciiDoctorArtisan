# GitHub CLI Integration - User Guide

**Version:** 1.6.0+
**Date:** October 29, 2025
**Status:** Production Ready

---

## Overview

AsciiDoc Artisan now integrates with GitHub CLI (`gh`) to provide seamless pull request and issue management directly from the editor. This feature allows you to:

- Create and list pull requests
- Create and list issues
- View repository information
- Open PRs and issues in your browser

All GitHub operations run in the background, keeping the editor responsive.

---

## Requirements

### 1. GitHub CLI Installation

The GitHub CLI (`gh`) must be installed on your system.

**Check if gh is installed:**
```bash
gh --version
# Should show: gh version 2.45.0 or higher
```

**Install GitHub CLI:**

**Linux (Debian/Ubuntu):**
```bash
sudo apt install gh
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install gh
```

**macOS:**
```bash
brew install gh
```

**Windows:**
```bash
winget install --id GitHub.cli
# or use: choco install gh
```

**Other methods:** See https://cli.github.com/manual/installation

---

### 2. GitHub Authentication

You must authenticate with GitHub before using integration features.

**Authenticate:**
```bash
gh auth login
```

Follow the prompts to:
1. Choose GitHub.com or GitHub Enterprise Server
2. Choose authentication method (SSH or HTTPS)
3. Complete authentication via browser or token

**Verify authentication:**
```bash
gh auth status
```

You should see:
```
✓ Logged in to github.com as your-username
✓ Git operations for github.com configured to use ssh protocol.
✓ Token: gho_************************************
```

---

### 3. Repository Setup

The Git repository must be linked to a GitHub remote.

**In AsciiDoc Artisan:**
1. Go to **Git → Set Repository**
2. Select your Git repository folder
3. Verify the repository is connected to GitHub

**Verify from command line:**
```bash
cd /path/to/your/repo
git remote -v
# Should show GitHub URL like:
# origin  git@github.com:username/repo.git (fetch)
```

---

## Features

### 1. Create Pull Request

**Menu:** Git → GitHub → Create Pull Request...

**Steps:**
1. Click **Git → GitHub → Create Pull Request**
2. Fill in the dialog:
   - **Title** (required): Brief, descriptive PR title
   - **Base branch**: Target branch (default: `main`)
   - **Head branch**: Your feature branch (auto-populated)
   - **Description**: Detailed explanation of changes
   - **Draft PR**: Check to create as draft (optional)
3. Click **Create PR**

**Dialog Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| Title | ✅ Yes | Short PR title (e.g., "Add user authentication") |
| Base branch | ✅ Yes | Target branch to merge into (usually `main` or `develop`) |
| Head branch | ✅ Yes | Your feature branch with changes |
| Description | ❌ No | Detailed explanation, testing notes, screenshots |
| Draft PR | ❌ No | Create as draft (not ready for review) |

**Validation:**
- Title cannot be empty
- Base branch cannot equal head branch
- If validation fails, the field shows a red border

**Result:**
- Status bar shows: "PR #42 created!" with PR number
- PR opens automatically in your browser (optional)

**Example:**
```
Title: Add dark mode support
Base: main
Head: feature/dark-mode
Description:
  This PR adds dark mode support to the application.

  Changes:
  - Added theme toggle in settings
  - Updated CSS for dark theme
  - Added user preference persistence

  Testing:
  - Verified toggle works in all dialogs
  - Checked theme persists across sessions
Draft: ☐ (unchecked)
```

---

### 2. List Pull Requests

**Menu:** Git → GitHub → List Pull Requests

**Features:**
- View all PRs in a table
- Filter by state: Open / Closed / Merged / All
- Double-click to open PR in browser
- Refresh button to reload data

**Table Columns:**

| Column | Description |
|--------|-------------|
| Number | PR number (#42) |
| Title | PR title |
| Author | GitHub username of PR creator |
| Status | Open, Closed, or Merged |
| Created | Creation date |
| URL | Full GitHub URL |

**State Filter:**
- **Open**: Show only open PRs (default)
- **Closed**: Show only closed PRs
- **Merged**: Show only merged PRs
- **All**: Show all PRs regardless of state

**Actions:**
- **Double-click row**: Opens PR in browser
- **Refresh button**: Fetches latest PR data from GitHub
- **Close button**: Closes dialog

**Empty State:**
If no PRs match the filter, the dialog shows:
```
No pull requests found
```

---

### 3. Create Issue

**Menu:** Git → GitHub → Create Issue...

**Steps:**
1. Click **Git → GitHub → Create Issue**
2. Fill in the dialog:
   - **Title** (required): Brief issue description
   - **Labels**: Comma-separated labels (optional)
   - **Description**: Detailed issue explanation
3. Click **Create Issue**

**Dialog Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| Title | ✅ Yes | Short issue title (e.g., "Login button not working") |
| Labels | ❌ No | Comma-separated (e.g., "bug, high-priority, ui") |
| Description | ❌ No | Detailed explanation, steps to reproduce, expected behavior |

**Common Labels:**
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `question` - Further information requested
- `help wanted` - Extra attention needed

**Validation:**
- Title cannot be empty
- If validation fails, the field shows a red border

**Result:**
- Status bar shows: "Issue #15 created!" with issue number
- Issue opens automatically in your browser (optional)

**Example:**
```
Title: Application crashes when opening large files
Labels: bug, high-priority
Description:
  **Problem:**
  The application crashes when attempting to open AsciiDoc files larger than 100MB.

  **Expected Behavior:**
  Large files should open successfully or show a warning message.

  **Steps to Reproduce:**
  1. Create an AsciiDoc file > 100MB
  2. Go to File → Open
  3. Select the large file
  4. Application freezes and crashes

  **Environment:**
  - OS: Ubuntu 22.04
  - Version: 1.5.0
  - File size: 125MB
```

---

### 4. List Issues

**Menu:** Git → GitHub → List Issues

**Features:**
- View all issues in a table
- Filter by state: Open / Closed / All
- Double-click to open issue in browser
- Refresh button to reload data

**Table Columns:**

| Column | Description |
|--------|-------------|
| Number | Issue number (#15) |
| Title | Issue title |
| Author | GitHub username of issue creator |
| Status | Open or Closed |
| Created | Creation date |
| URL | Full GitHub URL |

**State Filter:**
- **Open**: Show only open issues (default)
- **Closed**: Show only closed issues
- **All**: Show all issues regardless of state

**Actions:**
- **Double-click row**: Opens issue in browser
- **Refresh button**: Fetches latest issue data from GitHub
- **Close button**: Closes dialog

---

### 5. Repository Info

**Menu:** Git → GitHub → Repository Info

**Features:**
- View repository name and owner
- See repository description
- Check visibility (public/private)
- View statistics (stars, forks, watchers)

**Information Displayed:**
- Repository full name (owner/repo)
- Description
- Default branch
- Visibility (public/private)
- Homepage URL
- Statistics (if available)

---

## Keyboard Shortcuts

Currently, GitHub operations do not have keyboard shortcuts. Access them via:

**Menu Bar:**
```
Git → GitHub → [Feature]
```

**Future Enhancement:** Keyboard shortcuts may be added in v1.7.0+

---

## Error Handling

### Common Errors and Solutions

#### 1. "gh CLI not found"

**Error Message:**
```
Git command not found. Ensure Git is installed and in system PATH.
```

**Solution:**
1. Install GitHub CLI: `sudo apt install gh` (Linux) or `brew install gh` (macOS)
2. Verify installation: `gh --version`
3. Restart AsciiDoc Artisan

---

#### 2. "Not authenticated with GitHub"

**Error Message:**
```
Authentication required. Please run 'gh auth login' to authenticate.
```

**Solution:**
1. Open terminal
2. Run: `gh auth login`
3. Follow authentication prompts
4. Verify: `gh auth status`
5. Try operation again in AsciiDoc Artisan

---

#### 3. "No repository set"

**Error Message:**
```
No Repository
Please set a Git repository first (Git → Set Repository).
```

**Solution:**
1. Go to **Git → Set Repository**
2. Select folder containing `.git` directory
3. Verify repository is connected to GitHub remote
4. Try operation again

---

#### 4. "Not a Git repository"

**Error Message:**
```
Directory is not a Git repository.
```

**Solution:**
1. Navigate to project directory in terminal
2. Initialize Git: `git init`
3. Add remote: `git remote add origin git@github.com:username/repo.git`
4. Set repository in AsciiDoc Artisan
5. Try operation again

---

#### 5. "Operation timed out"

**Error Message:**
```
GitHub operation timed out after 60s.
Check network connection or try again.
```

**Solution:**
1. Check internet connection
2. Verify GitHub is accessible: `curl https://github.com`
3. Try operation again
4. If persistent, check firewall settings

---

#### 6. "Permission denied"

**Error Message:**
```
Permission denied. Check repository access rights.
```

**Solution:**
1. Verify you have write access to the repository
2. Check SSH key is configured: `gh auth status`
3. Try re-authenticating: `gh auth login`
4. Verify repository URL: `git remote -v`

---

## Limitations

### Current Limitations (v1.6.0)

1. **Draft PRs**: Draft flag is sent but requires gh CLI 2.45.0+
2. **Labels on PR Creation**: Only available via issue creation
3. **Assignees**: Cannot assign PRs/issues to users
4. **Reviewers**: Cannot request PR reviewers
5. **Milestones**: Cannot assign milestones
6. **Projects**: Cannot add to GitHub Projects
7. **Branches**: Cannot create/delete branches from UI
8. **CI Status**: Cannot view CI/CD status in PR list

### Planned Features (v1.7.0+)

- PR templates auto-loading
- Issue templates auto-loading
- CI/CD status indicator in PR list
- Assignee and reviewer selection
- Label management from UI
- Branch management
- Diff viewer for PRs
- Comment on PRs and issues
- Merge PRs from UI

---

## Best Practices

### 1. Commit Before Creating PR

Always commit and push your changes before creating a PR:

```bash
# In terminal
git add .
git commit -m "Your commit message"
git push origin feature-branch
```

Or use AsciiDoc Artisan's Git integration:
1. **Git → Commit** (Ctrl+Shift+C)
2. **Git → Push** (Ctrl+Shift+U)
3. **Git → GitHub → Create Pull Request**

---

### 2. Use Descriptive Titles

**Good PR Titles:**
- ✅ "Add user authentication with JWT tokens"
- ✅ "Fix memory leak in preview rendering"
- ✅ "Update documentation for GitHub CLI integration"

**Bad PR Titles:**
- ❌ "Fix bug"
- ❌ "Update code"
- ❌ "Changes"

---

### 3. Write Clear Descriptions

Include in PR/issue descriptions:
- **What**: What changes were made?
- **Why**: Why were these changes needed?
- **How**: How were the changes implemented?
- **Testing**: How were the changes tested?

**Example:**
```markdown
## Summary
Adds dark mode support to the application.

## Motivation
Users requested dark mode for better readability in low-light environments.

## Changes
- Added theme toggle in settings dialog
- Implemented CSS for dark theme
- Added theme preference persistence

## Testing
- Manual testing on Linux, macOS, Windows
- Verified theme persists across sessions
- Checked all dialogs render correctly
```

---

### 4. Use Labels Effectively

Organize issues with labels:
- `bug` - Defects and errors
- `enhancement` - New features
- `documentation` - Docs improvements
- `question` - Questions and discussions
- `good first issue` - Easy for new contributors
- `help wanted` - Need community help

---

### 5. Keep PRs Small

Smaller PRs are easier to review:
- ✅ One feature per PR
- ✅ < 500 lines changed
- ✅ Clear, focused changes
- ❌ Multiple unrelated features
- ❌ Massive refactoring + new features

---

## Troubleshooting

### Check System Status

**1. Verify gh CLI:**
```bash
gh --version
# Expected: gh version 2.45.0 or higher
```

**2. Verify authentication:**
```bash
gh auth status
# Should show: ✓ Logged in to github.com
```

**3. Verify repository:**
```bash
cd /path/to/repo
git remote -v
# Should show GitHub URL
```

**4. Test gh CLI:**
```bash
gh pr list
# Should show PRs or "no pull requests found"
```

---

### Enable Debug Logging

To enable detailed logging for troubleshooting:

1. Run AsciiDoc Artisan from terminal:
```bash
python3 src/main.py
```

2. Check logs for GitHub operations:
```
INFO - Dispatching GitHub operation: create_pull_request
INFO - Executing gh command: ['gh', 'pr', 'create', '--json', ...]
INFO - GitHub operation succeeded: PR #42 created
```

3. Look for errors:
```
ERROR - GitHub operation failed: authentication required
ERROR - Git command not found
```

---

### Clear GitHub Cache

If experiencing stale data:

```bash
# Clear gh CLI cache
rm -rf ~/.cache/gh/

# Re-authenticate
gh auth login
```

---

## Security Considerations

### 1. Credentials

- GitHub CLI stores credentials securely using OS keyring
- AsciiDoc Artisan never stores GitHub credentials
- All authentication handled by `gh` CLI

### 2. API Rate Limits

GitHub API has rate limits:
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

AsciiDoc Artisan operations count toward your rate limit.

### 3. Permissions

GitHub CLI requires these permissions:
- `repo` - Full control of private repositories
- `read:org` - Read org and team membership

Grant only necessary permissions during authentication.

---

## FAQ

### Q: Can I use GitHub Enterprise?

**A:** Yes! Authenticate with your GitHub Enterprise instance:
```bash
gh auth login --hostname github.company.com
```

Then use AsciiDoc Artisan normally. All operations will use your Enterprise instance.

---

### Q: Can I create PRs across forks?

**A:** Yes, but you must specify the head branch with owner:
```
Head: your-username:feature-branch
```

This tells GitHub to create a PR from your fork.

---

### Q: Why are some PRs not showing in the list?

**A:** Check the state filter (top of dialog):
- Default is "Open" - only shows open PRs
- Switch to "All" to see all PRs

Also check you're viewing the correct repository (Git → Set Repository).

---

### Q: Can I edit existing PRs or issues?

**A:** Not yet. v1.6.0 supports creating and viewing only. Editing will be added in v1.7.0.

For now, click the PR/issue row to open in browser, then edit there.

---

### Q: Does this work offline?

**A:** No. GitHub integration requires internet connection to communicate with GitHub API.

Git operations (commit, add, status) work offline, but GitHub features require network access.

---

### Q: How do I update gh CLI?

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt upgrade gh
```

**macOS:**
```bash
brew upgrade gh
```

**Windows:**
```bash
winget upgrade --id GitHub.cli
```

---

### Q: Can I use this with GitLab or Bitbucket?

**A:** No. This integration is GitHub-specific using GitHub CLI.

GitLab and Bitbucket support may be added in future versions if there's demand.

---

## Getting Help

### Documentation
- **User Guide**: This file
- **Architecture**: See `CLAUDE.md` for developer documentation
- **Specifications**: See `SPECIFICATIONS.md` for functional requirements

### Support Channels
- **GitHub Issues**: Report bugs at https://github.com/webbwr/AsciiDoctorArtisan/issues
- **Discussions**: Ask questions at https://github.com/webbwr/AsciiDoctorArtisan/discussions

### Reporting Issues

When reporting issues, include:
1. AsciiDoc Artisan version: Help → About
2. gh CLI version: `gh --version`
3. Operating system and version
4. Steps to reproduce
5. Expected vs actual behavior
6. Log output (if available)

**Example Issue Report:**
```markdown
**Environment:**
- AsciiDoc Artisan: 1.6.0
- gh CLI: 2.45.0
- OS: Ubuntu 22.04

**Steps to Reproduce:**
1. Click Git → GitHub → Create Pull Request
2. Fill in title and description
3. Click Create PR

**Expected:**
PR should be created successfully

**Actual:**
Error message: "Authentication required"

**Logs:**
ERROR - GitHub operation failed: authentication required
```

---

## Changelog

### v1.6.0 (October 2025) - Initial Release
- ✅ Create pull requests
- ✅ List pull requests with state filtering
- ✅ Create issues with labels
- ✅ List issues with state filtering
- ✅ View repository information
- ✅ Open PRs/issues in browser
- ✅ Background operations (non-blocking UI)
- ✅ Timeout protection (60s for network ops)
- ✅ Comprehensive error handling

### Planned for v1.7.0
- 🚧 PR templates auto-loading
- 🚧 Issue templates auto-loading
- 🚧 CI/CD status in PR list
- 🚧 Assignee selection
- 🚧 Reviewer requests
- 🚧 PR merging from UI

---

## Conclusion

The GitHub CLI integration brings powerful collaboration features directly into AsciiDoc Artisan. You can now manage pull requests and issues without leaving your editor, streamlining your workflow.

For technical details and architecture information, see:
- **Developer Guide**: `CLAUDE.md`
- **Implementation Report**: `/tmp/github_cli_integration_complete.md`

---

**Document Version:** 1.0
**Last Updated:** October 29, 2025
**Author:** AsciiDoc Artisan Development Team
