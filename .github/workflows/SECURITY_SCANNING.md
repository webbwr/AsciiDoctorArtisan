# Security Scanning Workflow Guide

## Overview

This document explains the automated security scanning workflow for AsciiDoc Artisan. The workflow uses two complementary tools to scan Python dependencies for known security vulnerabilities.

## Tools Used

### 1. Safety

**Purpose:** Scans against Safety DB (curated vulnerability database)

**Strengths:**
- Curated database maintained by PyUp.io
- Focus on high-quality, verified vulnerabilities
- Fast scanning with low false positives
- Excellent for catching common CVEs

**Database:** https://github.com/pyupio/safety-db

### 2. pip-audit

**Purpose:** Scans against OSV (Open Source Vulnerabilities database)

**Strengths:**
- Broader coverage from multiple sources
- Includes GitHub Security Advisories
- Aggregates PyPA advisories
- Often catches vulnerabilities Safety misses

**Database:** https://osv.dev

## When Scans Run

The security workflow triggers automatically in these scenarios:

1. **On Push to Main/Dev Branches**
   - Ensures production and development branches are secure
   - Runs after code is merged

2. **On Pull Requests to Main/Dev**
   - Catches vulnerabilities before merging
   - Non-blocking (reports but doesn't fail PRs)

3. **Weekly Schedule (Sunday at Midnight UTC)**
   - Catches newly disclosed vulnerabilities
   - Ensures ongoing security monitoring
   - Even if no code changes occur

4. **Manual Trigger**
   - Can be triggered manually from GitHub Actions UI
   - Useful for ad-hoc security audits

## Workflow Jobs

### Job 1: Safety Security Scan

**Runtime:** ~2-5 minutes

**Steps:**
1. Checkout code
2. Set up Python 3.12
3. Install Safety scanner
4. Install project dependencies
5. Run Safety scan
6. Generate summary report
7. Upload JSON results as artifact

**Output:**
- `safety-report.json` - Detailed vulnerability report
- GitHub Actions summary with vulnerability count

### Job 2: pip-audit Security Scan

**Runtime:** ~2-5 minutes

**Steps:**
1. Checkout code
2. Set up Python 3.12
3. Install pip-audit scanner
4. Install project dependencies
5. Run pip-audit scan
6. Generate summary report
7. Upload JSON results as artifact

**Output:**
- `pip-audit-report.json` - Detailed vulnerability report
- GitHub Actions summary with vulnerability count

### Job 3: Security Scan Summary

**Runtime:** ~30 seconds

**Purpose:** Aggregates results from both scanners into unified report

**Output:**
- Unified summary in GitHub Actions
- Links to detailed reports
- Actionable next steps

## How to Interpret Results

### Viewing Reports

1. **In GitHub Actions UI:**
   - Navigate to Actions → Security Scanning workflow
   - Click on the latest run
   - View "Summary" tab for quick overview
   - Each job shows pass/fail status and vulnerability counts

2. **Detailed Reports (Artifacts):**
   - Scroll to bottom of workflow run page
   - Download artifacts: `safety-security-report` and `pip-audit-security-report`
   - Extract JSON files for detailed analysis

### Understanding Vulnerability Reports

#### Safety Report Format

```json
[
  {
    "advisory": "Brief description of the vulnerability",
    "cve": "CVE-2023-12345",
    "id": "safety-12345",
    "package": "vulnerable-package",
    "severity": "high",
    "specs": ["<2.0.0"],
    "v": "1.5.0"
  }
]
```

**Key Fields:**
- `package`: Name of vulnerable package
- `v`: Installed version
- `specs`: Version ranges affected by vulnerability
- `severity`: Severity level (low/medium/high/critical)
- `advisory`: Human-readable description
- `cve`: CVE identifier (if available)

#### pip-audit Report Format

```json
{
  "dependencies": [
    {
      "name": "vulnerable-package",
      "version": "1.5.0",
      "vulns": [
        {
          "id": "PYSEC-2023-123",
          "fix_versions": ["2.0.0"],
          "description": "Detailed vulnerability description",
          "aliases": ["CVE-2023-12345", "GHSA-xxxx-xxxx-xxxx"]
        }
      ]
    }
  ]
}
```

**Key Fields:**
- `name`: Package name
- `version`: Installed version
- `vulns`: Array of vulnerabilities affecting this package
- `fix_versions`: Versions that fix the vulnerability
- `id`: OSV vulnerability identifier
- `aliases`: Related identifiers (CVE, GitHub Advisory)

### Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **Critical** | Actively exploited, remote code execution | Immediate patching required |
| **High** | Serious vulnerabilities, privilege escalation | Patch within 1 week |
| **Medium** | Moderate impact, information disclosure | Patch within 1 month |
| **Low** | Minor issues, requires specific conditions | Patch when convenient |

### Example Workflow Output

#### Clean Scan (No Vulnerabilities)

```
✅ Safety Security Scan Results
   No vulnerabilities found
   Scan completed at: 2025-10-29 00:00:00 UTC

✅ pip-audit Security Scan Results
   No vulnerabilities found
   Scan completed at: 2025-10-29 00:00:05 UTC

🔒 Security Scan Summary
   Repository: webbwr/AsciiDoctorArtisan
   Branch: main
   Safety Scan: ✅ No vulnerabilities found
   pip-audit Scan: ✅ No vulnerabilities found
```

#### Vulnerable Dependencies Detected

```
⚠️ Safety Security Scan Results
   3 vulnerabilities found
   See uploaded artifacts for detailed report.

⚠️ pip-audit Security Scan Results
   2 packages with vulnerabilities found
   See uploaded artifacts for detailed report.

🔒 Security Scan Summary
   Repository: webbwr/AsciiDoctorArtisan
   Branch: main
   Safety Scan: ⚠️ Found 3 vulnerabilities
   pip-audit Scan: ⚠️ Found 2 packages with vulnerabilities

   Next Steps:
   - Review detailed reports in workflow artifacts
   - Check vulnerability severity and affected versions
   - Update vulnerable dependencies where possible
   - Create issues for vulnerabilities requiring investigation
```

## Responding to Vulnerabilities

### Step 1: Assess Severity

1. Download and review detailed reports
2. Check CVE details at https://nvd.nist.gov
3. Determine if vulnerability affects your usage

**Questions to ask:**
- Is the vulnerable function/feature used in our code?
- Does the vulnerability require specific conditions?
- Is there active exploitation in the wild?
- What's the CVSS score?

### Step 2: Check for Updates

```bash
# Check if newer version is available
pip index versions <package-name>

# Test update in isolated environment
python -m venv test-env
source test-env/bin/activate
pip install <package-name>==<new-version>
pip install -r requirements.txt
pytest tests/
```

### Step 3: Update Dependencies

If update is safe:

```bash
# Update requirements.txt
# Change: vulnerable-package>=1.5.0
# To:     vulnerable-package>=2.0.0

# Install and test
pip install -r requirements.txt
make test

# Commit changes
git add requirements.txt
git commit -m "Security: Update vulnerable-package to v2.0.0 (fixes CVE-2023-12345)"
git push
```

### Step 4: If No Fix Available

If no patched version exists:

1. **Create GitHub Issue:**
   - Title: `[Security] CVE-2023-12345 in vulnerable-package`
   - Include severity, description, and affected version
   - Tag with `security` label

2. **Consider Alternatives:**
   - Search for alternative packages
   - Temporary workarounds (input validation, sandboxing)
   - Contact package maintainer

3. **Monitor for Updates:**
   - Weekly scans will catch new patches
   - Subscribe to package security advisories
   - Check GitHub Security Advisories

### Step 5: Document Decision

Update `SECURITY.md` with:
- Known vulnerabilities and mitigation strategies
- Reasons for not updating (if applicable)
- Compensating controls implemented
- Timeline for future updates

## Advanced Configuration

### Using Safety API Key (Optional)

Safety offers a commercial API with more frequent database updates and additional features.

**To enable:**

1. Get API key from https://pyup.io
2. Add as GitHub Secret:
   - Repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `SAFETY_API_KEY`
   - Value: Your API key

3. Update workflow (`.github/workflows/security.yml`):

```yaml
- name: Run Safety scan
  env:
    SAFETY_API_KEY: ${{ secrets.SAFETY_API_KEY }}
  run: |
    safety check --key $SAFETY_API_KEY --json > safety-report.json || true
```

### Customizing Scan Frequency

Edit `.github/workflows/security.yml`:

```yaml
schedule:
  # Daily at 2 AM UTC
  - cron: '0 2 * * *'

  # Or twice weekly (Monday and Thursday at midnight)
  - cron: '0 0 * * 1,4'
```

**Cron syntax:** `minute hour day-of-month month day-of-week`

### Ignoring False Positives

If a vulnerability is a false positive or doesn't apply:

**For Safety:**

Create `.safety-policy.yml` in repository root:

```yaml
security:
  ignore-vulnerabilities:
    # Ignore specific vulnerability ID
    12345:
      reason: "This vulnerability requires feature X which we don't use"
      expires: "2025-12-31"
```

**For pip-audit:**

Use `--ignore-vuln` flag in workflow:

```yaml
- name: Run pip-audit scan
  run: |
    pip-audit --ignore-vuln PYSEC-2023-123 --format json > pip-audit-report.json || true
```

### Failing PRs on Vulnerabilities

To make scans blocking (fail PRs with vulnerabilities):

Remove `continue-on-error: true` from scan steps:

```yaml
- name: Run Safety scan
  run: |
    safety check --json > safety-report.json
    safety check  # Will fail workflow if vulnerabilities found
```

**⚠️ Warning:** This can block legitimate PRs if:
- Vulnerability is in development dependency only
- No patched version is available yet
- Vulnerability doesn't affect your use case

## Troubleshooting

### Workflow Fails to Run

**Issue:** Workflow doesn't trigger on push/PR

**Solutions:**
1. Check workflow file is in `.github/workflows/` directory
2. Verify YAML syntax: https://yaml-online-parser.appspot.com
3. Ensure file is committed to repository
4. Check GitHub Actions is enabled: Repository Settings → Actions

### "Permission denied" Errors

**Issue:** Cannot upload artifacts or write summaries

**Solution:** Ensure GitHub token has correct permissions:

```yaml
permissions:
  contents: read
  actions: write
```

### Dependency Installation Fails

**Issue:** `pip install -r requirements.txt` fails

**Solutions:**
1. Check for system dependencies (Pandoc, wkhtmltopdf)
2. Add installation steps:

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y pandoc wkhtmltopdf
```

### Scan Times Out

**Issue:** Workflow exceeds 10-minute timeout

**Solutions:**
1. Increase timeout: `timeout-minutes: 20`
2. Install only production dependencies:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements-production.txt
```

### JSON Report Parsing Fails

**Issue:** `jq` command fails to parse report

**Solution:** Add error handling:

```yaml
vuln_count=$(jq '. | length' safety-report.json 2>/dev/null || echo "error")
if [ "$vuln_count" = "error" ]; then
  echo "⚠️ Could not parse report" >> $GITHUB_STEP_SUMMARY
fi
```

## Best Practices

1. **Review Reports Weekly**
   - Even if no alerts, check for new advisories
   - Stay informed about security trends

2. **Update Dependencies Regularly**
   - Don't wait for vulnerabilities to be found
   - Keep dependencies current (within major version)

3. **Test Before Updating**
   - Always run full test suite after updates
   - Check for breaking changes in release notes

4. **Document Decisions**
   - Record why vulnerabilities are ignored
   - Update security documentation

5. **Monitor Upstream Projects**
   - Subscribe to security mailing lists
   - Watch critical dependencies on GitHub

6. **Separate Production Dependencies**
   - Keep `requirements-production.txt` minimal
   - Development tools don't need same security rigor

## Additional Resources

- **Safety Documentation:** https://docs.pyup.io/docs/safety-20-policy-file
- **pip-audit Documentation:** https://github.com/pypa/pip-audit
- **OSV Database:** https://osv.dev
- **CVE Database:** https://nvd.nist.gov
- **GitHub Security Advisories:** https://github.com/advisories
- **Python Security Response Team:** https://www.python.org/news/security/
- **AsciiDoc Artisan Security Policy:** `SECURITY.md`

## Support

For questions or issues with the security scanning workflow:

1. Check this documentation
2. Review closed issues: https://github.com/webbwr/AsciiDoctorArtisan/issues
3. Create new issue with `security` and `workflow` labels
4. Include workflow run URL and error messages

---

**Last Updated:** October 29, 2025
**Workflow Version:** 1.0.0
**Maintained By:** AsciiDoc Artisan Security Team
