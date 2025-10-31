# GitHub and AsciiDoc Artisan

**Version:** 1.6.0+
**Date:** October 29, 2025
**Status:** Ready to use

---

## What This Does

AsciiDoc Artisan works with GitHub. You can do GitHub tasks right in the app.

What you can do:
- Make pull requests (PRs)
- See your pull requests
- Make issues
- See your issues
- Look at repo info
- Open PRs in your web browser
- Open issues in your web browser

All GitHub tasks run in the background. The app stays fast.

---

## What You Need

### 1. GitHub CLI Program

You need a program called GitHub CLI. Its short name is `gh`.

**Check if you have it:**

Type this in your terminal:
```bash
gh --version
```

You should see: `gh version 2.45.0` or higher.

**Get GitHub CLI:**

Pick your computer type:

**Linux (Ubuntu or Debian):**
```bash
sudo apt install gh
```

**Linux (Fedora or Red Hat):**
```bash
sudo dnf install gh
```

**Mac:**
```bash
brew install gh
```

**Windows:**
```bash
winget install --id GitHub.cli
```

Or use: `choco install gh`

**Need help?** Go to: https://cli.github.com/manual/installation

---

### 2. Log In to GitHub

You must log in to GitHub first.

**To log in:**

Type this:
```bash
gh auth login
```

Then answer these questions:
1. Pick GitHub.com or GitHub Enterprise
2. Pick SSH or HTTPS
3. Log in with your web browser or token

**Check if you are logged in:**

Type this:
```bash
gh auth status
```

You should see this:
```
✓ Logged in to github.com as your-username
✓ Git operations set up
✓ Token: gho_************************************
```

---

### 3. Set Up Your Repo

Your Git folder must link to GitHub.

**In the app:**
1. Click **Git**
2. Click **Set Repository**
3. Pick your Git folder
4. Check it links to GitHub

**Check from terminal:**

Type these commands:
```bash
cd /path/to/your/repo
git remote -v
```

You should see a GitHub web address like:
```
origin  git@github.com:username/repo.git (fetch)
```

---

## What You Can Do

### 1. Make a Pull Request

**Where to find it:** Git → GitHub → Create Pull Request

**How to do it:**

1. Click **Git** in the menu
2. Click **GitHub**
3. Click **Create Pull Request**
4. Fill in the form:
   - **Title** (you must fill this): Short name for your PR
   - **Base branch**: Where your code will go (often `main`)
   - **Head branch**: Your branch with changes (filled in for you)
   - **Description**: What you changed and why
   - **Draft PR**: Check this if not ready yet
5. Click **Create PR**

**What each field means:**

| Field | Must fill? | What it is |
|-------|-----------|------------|
| Title | Yes ✅ | Short name like "Add dark mode" |
| Base branch | Yes ✅ | Where to put your code (like `main`) |
| Head branch | Yes ✅ | Your branch with changes |
| Description | No ❌ | Tell what you changed |
| Draft PR | No ❌ | Check if not ready to merge |

**The app checks:**
- Title box is not empty
- Base and head are not the same
- If wrong, the box turns red

**What happens:**
- Status bar says: "PR #42 created!"
- PR opens in your web browser

**Example:**
```
Title: Add dark mode
Base: main
Head: feature/dark-mode
Description:
  This PR adds dark mode.

  What changed:
  - Added toggle in settings
  - Made new CSS for dark theme
  - Saves your choice

  Tests done:
  - Toggle works in all windows
  - Choice saves when you close app
Draft: ☐ (not checked)
```

---

### 2. List Pull Requests

**Menu:** Git → GitHub → List Pull Requests

**What it does:**
- Shows all PRs in a table
- Filter by state: Open / Closed / Merged / All
- Double-click to open PR in browser
- Refresh button to reload data

**Table Columns:**

| Column | What it shows |
|--------|---------------|
| Number | PR number (#42) |
| Title | PR title |
| Author | GitHub user who made the PR |
| Status | Open, Closed, or Merged |
| Created | Date the PR was made |
| URL | Full GitHub link |

**State Filter:**
- **Open**: Show only open PRs (default)
- **Closed**: Show only closed PRs
- **Merged**: Show only merged PRs
- **All**: Show all PRs

**What you can do:**
- **Double-click row**: Opens PR in browser
- **Refresh button**: Gets latest PR data from GitHub
- **Close button**: Closes dialog

**When no PRs exist:**
If no PRs match the filter, you see:
```
No pull requests found
```

---

### 3. Create Issue

**Menu:** Git → GitHub → Create Issue...

**How to do it:**
1. Click **Git → GitHub → Create Issue**
2. Fill in the form:
   - **Title** (required): Short issue name
   - **Labels**: Comma-separated tags (optional)
   - **Description**: Full details
3. Click **Create Issue**

**Form Fields:**

| Field | Required | What it means |
|-------|----------|---------------|
| Title | ✅ Yes | Short issue title (e.g., "Login button not working") |
| Labels | ❌ No | Comma-separated (e.g., "bug, high-priority, ui") |
| Description | ❌ No | Full details, steps to reproduce, what should happen |

**Common Labels:**
- `bug` - Something is not working
- `enhancement` - New feature request
- `documentation` - Doc improvements
- `question` - Need more info
- `help wanted` - Need extra help

**Form Checks:**
- Title cannot be empty
- If check fails, field shows red border

**What you see:**
- Status bar shows: "Issue #15 created!" with issue number
- Issue opens in browser (optional)

**Example:**
```
Title: App crashes when opening large files
Labels: bug, high-priority
Description:
  **Problem:**
  The app crashes when opening AsciiDoc files larger than 100MB.

  **What should happen:**
  Large files should open or show a warning.

  **How to make it happen:**
  1. Create an AsciiDoc file > 100MB
  2. Go to File → Open
  3. Pick the large file
  4. App freezes and crashes

  **Your setup:**
  - OS: Ubuntu 22.04
  - Version: 1.5.0
  - File size: 125MB
```

---

### 4. List Issues

**Menu:** Git → GitHub → List Issues

**What it does:**
- Shows all issues in a table
- Filter by state: Open / Closed / All
- Double-click to open issue in browser
- Refresh button to reload data

**Table Columns:**

| Column | What it shows |
|--------|---------------|
| Number | Issue number (#15) |
| Title | Issue title |
| Author | GitHub user who made the issue |
| Status | Open or Closed |
| Created | Date the issue was made |
| URL | Full GitHub link |

**State Filter:**
- **Open**: Show only open issues (default)
- **Closed**: Show only closed issues
- **All**: Show all issues

**What you can do:**
- **Double-click row**: Opens issue in browser
- **Refresh button**: Gets latest issue data from GitHub
- **Close button**: Closes dialog

---

### 5. View Repo Info

**Menu:** Git → GitHub → Repository Info

**What it does:**
- Shows repo name and owner
- Shows repo description
- Shows if public or private
- Shows stats (stars, forks, watchers)

**Info shown:**
- Full repo name (owner/repo)
- Description
- Default branch
- Public or private
- Homepage URL
- Stats (if available)

---

## Keyboard Shortcuts

There are no shortcuts yet for GitHub features. Use the menu:

**Menu Bar:**
```
Git → GitHub → [Feature]
```

**Future Plan:** Shortcuts may be added in v1.7.0+

---

## Error Handling

### Common Errors and Fixes

#### 1. "gh CLI not found"

**Error:**
```
Git command not found. Ensure Git is installed and in system PATH.
```

**How to fix:**
1. Install GitHub CLI: `sudo apt install gh` (Linux) or `brew install gh` (macOS)
2. Check install: `gh --version`
3. Restart AsciiDoc Artisan

---

#### 2. "Not signed in to GitHub"

**Error:**
```
Authentication required. Please run 'gh auth login' to authenticate.
```

**How to fix:**
1. Open terminal
2. Run: `gh auth login`
3. Follow sign-in steps
4. Check: `gh auth status`
5. Try again in AsciiDoc Artisan

---

#### 3. "No repo set"

**Error:**
```
No Repository
Please set a Git repository first (Git → Set Repository).
```

**How to fix:**
1. Go to **Git → Set Repository**
2. Pick folder with `.git` directory
3. Check repo is linked to GitHub
4. Try again

---

#### 4. "Not a Git repo"

**Error:**
```
Directory is not a Git repository.
```

**How to fix:**
1. Go to project folder in terminal
2. Init Git: `git init`
3. Add remote: `git remote add origin git@github.com:username/repo.git`
4. Set repo in AsciiDoc Artisan
5. Try again

---

#### 5. "Task took too long"

**Error:**
```
GitHub operation timed out after 60s.
Check network connection or try again.
```

**How to fix:**
1. Check internet connection
2. Test GitHub: `curl https://github.com`
3. Try again
4. If still fails, check firewall

---

#### 6. "Access denied"

**Error:**
```
Permission denied. Check repository access rights.
```

**How to fix:**
1. Check you can write to the repo
2. Check SSH key: `gh auth status`
3. Try signing in again: `gh auth login`
4. Check repo URL: `git remote -v`

---

## Limits

### Current Limits (v1.6.0)

1. **Draft PRs**: Draft flag needs gh CLI 2.45.0+
2. **Labels on PR**: Only works for issues, not PRs
3. **Assignees**: Cannot assign PRs or issues to users
4. **Reviewers**: Cannot ask for PR reviews
5. **Milestones**: Cannot add milestones
6. **Projects**: Cannot add to GitHub Projects
7. **Branches**: Cannot make or delete branches in app
8. **CI Status**: Cannot see build status in PR list

### Coming in v1.7.0+

- PR templates auto-load
- Issue templates auto-load
- Build status in PR list
- Assign users and reviewers
- Label tools in app
- Branch tools
- Diff viewer for PRs
- Comment on PRs and issues
- Merge PRs from app

---

## Good Habits

### 1. Commit Before Making PR

Save and push your changes first:

```bash
# In terminal
git add .
git commit -m "Your commit message"
git push origin feature-branch
```

Or use AsciiDoc Artisan Git tools:
1. **Git → Commit** (Ctrl+Shift+C)
2. **Git → Push** (Ctrl+Shift+U)
3. **Git → GitHub → Create Pull Request**

---

### 2. Use Clear Titles

**Good PR Titles:**
- ✅ "Add user login with JWT tokens"
- ✅ "Fix memory leak in preview"
- ✅ "Update docs for GitHub CLI"

**Bad PR Titles:**
- ❌ "Fix bug"
- ❌ "Update code"
- ❌ "Changes"

---

### 3. Write Clear Details

Add to PR and issue details:
- **What**: What did you change?
- **Why**: Why did you change it?
- **How**: How did you do it?
- **Testing**: How did you test it?

**Example:**
```markdown
## Summary
Adds dark mode to the app.

## Why
Users asked for dark mode for low light.

## Changes
- Added theme toggle in settings
- Made CSS for dark theme
- Saved theme choice

## Testing
- Tested on Linux, macOS, Windows
- Checked theme saves
- Checked all dialogs look good
```

---

### 4. Use Labels Well

Sort issues with labels:
- `bug` - Errors and defects
- `enhancement` - New features
- `documentation` - Doc fixes
- `question` - Questions
- `good first issue` - Easy for new people
- `help wanted` - Need help from others

---

### 5. Keep PRs Small

Small PRs are easier to review:
- ✅ One feature per PR
- ✅ Less than 500 lines changed
- ✅ Clear, focused changes
- ❌ Many features in one PR
- ❌ Big rewrites plus new features

---

## Fixing Problems

### Check Your Setup

**1. Check gh CLI:**
```bash
gh --version
# You should see: gh version 2.45.0 or higher
```

**2. Check sign in:**
```bash
gh auth status
# You should see: ✓ Logged in to github.com
```

**3. Check repo:**
```bash
cd /path/to/repo
git remote -v
# You should see GitHub URL
```

**4. Test gh CLI:**
```bash
gh pr list
# You should see PRs or "no pull requests found"
```

---

### Turn On Debug Logs

To see more details for fixing problems:

1. Run AsciiDoc Artisan from terminal:
```bash
python3 src/main.py
```

2. Look for GitHub logs:
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

If you see old data:

```bash
# Clear gh CLI cache
rm -rf ~/.cache/gh/

# Sign in again
gh auth login
```

---

## Security Notes

### 1. Sign-In Info

- GitHub CLI stores sign-in info safely in OS keyring
- AsciiDoc Artisan never stores GitHub sign-in info
- All sign-in handled by `gh` CLI

### 2. API Rate Limits

GitHub API has limits:
- Signed in: 5,000 requests per hour
- Not signed in: 60 requests per hour

AsciiDoc Artisan uses your limit.

### 3. Access Rights

GitHub CLI needs these rights:
- `repo` - Full control of private repos
- `read:org` - Read team info

Only grant what is needed when signing in.

---

## Questions and Answers

### Q: Can I use GitHub Enterprise?

**A:** Yes! Sign in to your GitHub Enterprise:
```bash
gh auth login --hostname github.company.com
```

Then use AsciiDoc Artisan normally. All actions use your Enterprise.

---

### Q: Can I make PRs across forks?

**A:** Yes, but you must add the owner to head branch:
```
Head: your-username:feature-branch
```

This tells GitHub to make a PR from your fork.

---

### Q: Why are some PRs missing from the list?

**A:** Check the state filter at top of dialog:
- Default is "Open" - only shows open PRs
- Switch to "All" to see all PRs

Also check you are in the right repo (Git → Set Repository).

---

### Q: Can I edit PRs or issues?

**A:** Not yet. v1.6.0 can create and view only. Editing comes in v1.7.0.

For now, click the PR or issue row to open in browser, then edit there.

---

### Q: Does this work offline?

**A:** No. GitHub features need internet to talk to GitHub API.

Git tools (commit, add, status) work offline, but GitHub features need network.

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

**A:** No. This works only with GitHub using GitHub CLI.

GitLab and Bitbucket may be added later if people ask for it.

---

## Getting Help

### Docs
- **User Guide**: This file
- **Dev Guide**: See `CLAUDE.md` for dev docs
- **Rules**: See `SPECIFICATIONS.md` for feature rules

### Help Channels
- **GitHub Issues**: Report bugs at https://github.com/webbwr/AsciiDoctorArtisan/issues
- **Discussions**: Ask questions at https://github.com/webbwr/AsciiDoctorArtisan/discussions

### How to Report Issues

When reporting issues, include:
1. AsciiDoc Artisan version: Help → About
2. gh CLI version: `gh --version`
3. Your OS and version
4. How to make it happen
5. What should happen vs what does happen
6. Log output (if you have it)

**Example Issue Report:**
```markdown
**Your Setup:**
- AsciiDoc Artisan: 1.6.0
- gh CLI: 2.45.0
- OS: Ubuntu 22.04

**How to Make It Happen:**
1. Click Git → GitHub → Create Pull Request
2. Fill in title and details
3. Click Create PR

**What Should Happen:**
PR should be created

**What Does Happen:**
Error message: "Authentication required"

**Logs:**
ERROR - GitHub operation failed: authentication required
```

---

## Change Log

### v1.6.0 (October 2025) - First Release
- ✅ Create pull requests
- ✅ List pull requests with state filter
- ✅ Create issues with labels
- ✅ List issues with state filter
- ✅ View repo info
- ✅ Open PRs and issues in browser
- ✅ Background tasks (UI stays fast)
- ✅ Timeout safety (60s for network)
- ✅ Full error handling

### Coming in v1.7.0
- 🚧 PR templates auto-load
- 🚧 Issue templates auto-load
- 🚧 Build status in PR list
- 🚧 Pick assignees
- 🚧 Request reviews
- 🚧 Merge PRs from app

---

## Wrap Up

The GitHub CLI feature brings team tools into AsciiDoc Artisan. You can now manage PRs and issues without leaving your editor. This makes your work easier.

For tech details and design info, see:
- **Dev Guide**: `CLAUDE.md`
- **Build Report**: `/tmp/github_cli_integration_complete.md`

---

**Doc Version:** 1.0
**Last Updated:** October 29, 2025
**Made By:** AsciiDoc Artisan Dev Team
