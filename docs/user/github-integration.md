# GitHub Integration

**v2.1.0** | PR and Issue management via GitHub CLI

---

## Setup

### 1. Install GitHub CLI

```bash
# Linux
sudo apt install gh

# Mac
brew install gh

# Windows
winget install --id GitHub.cli
```

### 2. Login

```bash
gh auth login
gh auth status  # Verify: ✓ Logged in
```

### 3. Set Repository

**Git → Set Repository** → Select folder with `.git`

---

## Features

| Feature | Menu Path |
|---------|-----------|
| Create PR | Git → GitHub → Create Pull Request |
| List PRs | Git → GitHub → List Pull Requests |
| Create Issue | Git → GitHub → Create Issue |
| List Issues | Git → GitHub → List Issues |
| Repo Info | Git → GitHub → Repository Info |

---

## Create Pull Request

1. Commit and push changes first
2. **Git → GitHub → Create Pull Request**
3. Fill: Title (required), Base branch, Description
4. Click **Create PR**

Opens in browser when complete.

---

## Create Issue

1. **Git → GitHub → Create Issue**
2. Fill: Title (required), Labels (comma-separated), Description
3. Click **Create Issue**

Common labels: `bug`, `enhancement`, `documentation`

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| "gh CLI not found" | Install: `sudo apt install gh` |
| "Not signed in" | Run: `gh auth login` |
| "No repo set" | **Git → Set Repository** |
| "Timeout" | Check internet, try again |

---

## Limits

- Cannot edit PRs/issues (use browser)
- Cannot assign reviewers
- Cannot merge from app

---

*v2.1.0 | Dec 5, 2025*
