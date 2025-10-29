# Security Scanning - Quick Reference Card

## 🚀 Quick Start

**View latest scan:**
```
GitHub → Actions → Security Scanning → Latest workflow run
```

**Download reports:**
```
Workflow run page → Artifacts → Download JSON reports
```

**Manually trigger scan:**
```
GitHub → Actions → Security Scanning → Run workflow
```

## 📊 Report Interpretation (30 Second Version)

| Icon | Meaning | Action |
|------|---------|--------|
| ✅ | No vulnerabilities | Great! Nothing to do |
| ⚠️ | Vulnerabilities found | Review severity, plan updates |
| ❌ | Scan failed | Check workflow logs |

## 🔍 Common Vulnerability Response

### If You See Vulnerabilities:

```bash
# 1. Download artifact JSON reports from GitHub Actions

# 2. Check severity in JSON
cat safety-report.json | jq '.[].severity'

# 3. See what versions fix it
cat pip-audit-report.json | jq '.dependencies[].vulns[].fix_versions'

# 4. Update requirements.txt with fixed version
# Edit: vulnerable-package>=1.5.0
# To:   vulnerable-package>=2.0.0

# 5. Test locally
pip install -r requirements.txt
make test

# 6. Commit if tests pass
git add requirements.txt
git commit -m "Security: Update vulnerable-package to v2.0.0"
git push
```

## 📋 Severity Guide

| Level | Response Time | Example |
|-------|---------------|---------|
| 🔴 **Critical** | Immediate (same day) | Remote code execution |
| 🟠 **High** | 1 week | Privilege escalation |
| 🟡 **Medium** | 1 month | Information disclosure |
| 🟢 **Low** | Next release | Minor issues |

## 🛠️ Manual Local Scan

```bash
# Install scanners
pip install safety pip-audit

# Run scans
safety check
pip-audit

# Or with JSON output
safety check --json > safety-local.json
pip-audit --format json > pip-audit-local.json
```

## 📝 JSON Report Structure

### Safety Report
```json
[{
  "package": "vulnerable-pkg",    # Package name
  "v": "1.5.0",                   # Your version
  "specs": ["<2.0.0"],            # Affected versions
  "severity": "high",             # Severity level
  "cve": "CVE-2023-12345"        # CVE identifier
}]
```

### pip-audit Report
```json
{
  "dependencies": [{
    "name": "vulnerable-pkg",     # Package name
    "version": "1.5.0",           # Your version
    "vulns": [{
      "id": "PYSEC-2023-123",     # Vulnerability ID
      "fix_versions": ["2.0.0"],  # Fixed in these versions
      "description": "..."        # Full description
    }]
  }]
}
```

## 🔧 Common Issues

### Issue: False Positive

**Solution:** Add to `.safety-policy.yml`:
```yaml
security:
  ignore-vulnerabilities:
    12345:
      reason: "Feature not used in our code"
      expires: "2025-12-31"
```

### Issue: No Fix Available

**Actions:**
1. Create GitHub issue with `security` label
2. Monitor for updates (weekly scans will catch)
3. Consider alternative packages
4. Document in `SECURITY.md`

### Issue: Breaking Change in Update

**Solution:**
```bash
# Test in isolated environment first
python -m venv test-update
source test-update/bin/activate
pip install vulnerable-package==2.0.0
pip install -r requirements.txt
make test

# If tests fail, investigate breaking changes
# Check package changelog/release notes
```

## 📅 Scan Schedule

- **Automatic:** Every push/PR to main/dev
- **Weekly:** Sunday at midnight UTC
- **Manual:** Anytime via GitHub Actions UI

## 🔗 Quick Links

- **CVE Lookup:** https://nvd.nist.gov
- **OSV Database:** https://osv.dev
- **GitHub Advisories:** https://github.com/advisories
- **Safety DB:** https://github.com/pyupio/safety-db
- **Full Guide:** `.github/workflows/SECURITY_SCANNING.md`

## 💡 Pro Tips

1. **Review weekly scans** - Catch new disclosures early
2. **Update regularly** - Don't wait for vulnerabilities
3. **Test updates** - Always run full test suite
4. **Document decisions** - Why vulnerabilities ignored
5. **Separate prod/dev deps** - Focus on production security

## 🆘 Getting Help

**Can't interpret report?**
→ Read full guide: `.github/workflows/SECURITY_SCANNING.md`

**Workflow not running?**
→ Check: Repository Settings → Actions → Enabled

**Need human review?**
→ Create issue with `security` label

---

**Quick Reference Version:** 1.0.0
**Last Updated:** October 29, 2025
