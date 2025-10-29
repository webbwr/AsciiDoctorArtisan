# GitHub Actions Workflows

This directory contains automated workflows for continuous integration, testing, and security scanning.

## Available Workflows

### 1. Security Scanning (`security.yml`)

**Status:** ✅ Active and ready to use

Automated dependency security scanning using Safety and pip-audit.

- **Triggers:** Push to main/dev, PRs, weekly schedule, manual dispatch
- **Tools:** Safety (Safety DB) + pip-audit (OSV database)
- **Runtime:** ~5 minutes
- **Non-blocking:** Reports vulnerabilities but doesn't fail PRs

**Quick Links:**
- 📚 [Full Documentation](SECURITY_SCANNING.md) - Complete setup and usage guide
- 🚀 [Quick Reference](SECURITY_QUICK_REFERENCE.md) - 30-second cheat sheet

**To trigger manually:**
```
GitHub → Actions → Security Scanning → Run workflow
```

### 2. CI/CD Pipeline (`ci.yml`)

## ⚠️ Manual Setup Required

The CI/CD workflow file `ci.yml` couldn't be pushed automatically due to OAuth scope restrictions. Please add it manually using one of the methods below.

---

## Method 1: GitHub Web Interface (Recommended)

1. Navigate to your repository on GitHub
2. Click on **Actions** tab
3. Click **New workflow**
4. Click **set up a workflow yourself**
5. Copy and paste the contents of `ci.yml` from this directory
6. Commit directly to main branch

---

## Method 2: GitHub CLI

If you have GitHub CLI installed with proper permissions:

```bash
# Refresh auth with workflow scope
gh auth refresh -s workflow

# Add and commit the workflow file
git add .github/workflows/ci.yml
git commit -m "ci: Add GitHub Actions workflow"
git push origin main
```

---

## Method 3: Personal Access Token

1. Generate a new token at: https://github.com/settings/tokens
2. Select scopes: `repo`, `workflow`
3. Update your git remote:
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/webbwr/AsciiDoctorArtisan.git
   git add .github/workflows/ci.yml
   git commit -m "ci: Add GitHub Actions workflow"
   git push origin main
   ```

---

## Workflow File Location

The complete workflow file is at:
```
.github/workflows/ci.yml
```

**Status:** Created locally, ready to add to repository

---

## What the Workflow Does

### Jobs:

1. **Lint** - Code quality checks
   - ruff (linting)
   - black (formatting)
   - isort (import sorting)
   - mypy (type checking)

2. **Test** - Cross-platform testing
   - OS: Ubuntu, Windows, macOS
   - Python: 3.11, 3.12
   - Coverage reporting to Codecov

3. **Build** - Package verification
   - Build distribution packages
   - Verify with twine

4. **Security** - Security scanning
   - safety (dependency vulnerabilities)
   - bandit (code security issues)

### Triggers:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

---

## After Adding the Workflow

1. **Verify it appears** in the Actions tab
2. **Trigger a test run** by pushing a small change
3. **Review results** for all jobs
4. **Check coverage** on Codecov (if configured)

---

## Optional: Codecov Setup

To enable coverage reporting:

1. Sign up at https://codecov.io with your GitHub account
2. Add the repository
3. Add `CODECOV_TOKEN` as a repository secret:
   - Go to Settings > Secrets and variables > Actions
   - New repository secret
   - Name: `CODECOV_TOKEN`
   - Value: (from Codecov dashboard)

Without this token, coverage reporting will be skipped (non-blocking).

---

## Troubleshooting

### Workflow doesn't appear
- Ensure file is in `.github/workflows/` directory
- Ensure file has `.yml` or `.yaml` extension
- Check Actions tab for any parsing errors

### Tests fail on specific platforms
- Review logs in the Actions tab
- Check system dependencies installation
- Verify platform-specific code paths

### Security job fails
- Review safety/bandit reports in artifacts
- Update vulnerable dependencies
- Fix security issues in code

---

## Next Steps After Setup

1. ✅ Verify workflow runs successfully
2. ✅ Check all jobs pass (Lint, Test, Build, Security)
3. ✅ Review test coverage reports
4. ✅ Set up branch protection rules (optional)
5. ✅ Configure required status checks (optional)

---

For more information, see:
- GitHub Actions docs: https://docs.github.com/en/actions
- Workflow syntax: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
