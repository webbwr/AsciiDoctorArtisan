# Testing the Security Workflow

This guide shows how to test the security scanning workflow locally and verify it works correctly.

## Prerequisites

```bash
# Install scanning tools
pip install safety pip-audit

# Verify installation
safety --version
pip-audit --version
```

## Test 1: Local Scan (Clean Dependencies)

**Purpose:** Verify scanners work with your current dependencies

```bash
# Navigate to project root
cd /home/webbp/github/AsciiDoctorArtisan

# Install dependencies
pip install -r requirements.txt

# Run Safety scan
echo "Running Safety scan..."
safety check
echo "Exit code: $?"

# Run pip-audit scan
echo "Running pip-audit scan..."
pip-audit
echo "Exit code: $?"
```

**Expected result:**
```
✅ Both scans complete without errors
✅ Exit code 0 if no vulnerabilities
✅ Exit code 64 (Safety) or 1 (pip-audit) if vulnerabilities found
```

## Test 2: JSON Output Generation

**Purpose:** Test artifact generation (what workflow uploads)

```bash
# Safety JSON report
safety check --json > safety-test-report.json
cat safety-test-report.json | jq '.'

# pip-audit JSON report
pip-audit --format json --desc > pip-audit-test-report.json
cat pip-audit-test-report.json | jq '.'

# Verify files created
ls -lh *test-report.json
```

**Expected result:**
```
✅ Two JSON files created
✅ Valid JSON format (jq parses without error)
✅ Contains vulnerability data (if any found)
```

## Test 3: Simulate Workflow Locally

**Purpose:** Run the exact same commands the workflow runs

Create test script: `test-security-workflow.sh`

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "Security Workflow Local Test"
echo "=========================================="
echo ""

# Simulate Safety job
echo "Job 1: Safety Security Scan"
echo "----------------------------"

# Install Safety
pip install -q safety

# Install dependencies
pip install -q -r requirements.txt

# Run Safety scan
echo "Running Safety scan..."
safety check --json > safety-report.json || true
safety check || echo "::warning::Safety found vulnerabilities"

# Generate summary
if [ -f safety-report.json ]; then
  vuln_count=$(jq '. | length' safety-report.json 2>/dev/null || echo "0")
  if [ "$vuln_count" -gt 0 ]; then
    echo "⚠️ Found $vuln_count vulnerabilities"
  else
    echo "✅ No vulnerabilities found"
  fi
fi

echo ""
echo "=========================================="
echo ""

# Simulate pip-audit job
echo "Job 2: pip-audit Security Scan"
echo "-------------------------------"

# Install pip-audit
pip install -q pip-audit

# Run pip-audit scan
echo "Running pip-audit scan..."
pip-audit --format json --desc > pip-audit-report.json || true
pip-audit || echo "::warning::pip-audit found vulnerabilities"

# Generate summary
if [ -f pip-audit-report.json ]; then
  vuln_count=$(jq '.dependencies | length' pip-audit-report.json 2>/dev/null || echo "0")
  if [ "$vuln_count" -gt 0 ]; then
    echo "⚠️ Found $vuln_count packages with vulnerabilities"
  else
    echo "✅ No vulnerabilities found"
  fi
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Artifacts generated:"
ls -lh safety-report.json pip-audit-report.json
echo ""
echo "To view reports:"
echo "  cat safety-report.json | jq '.'"
echo "  cat pip-audit-report.json | jq '.'"
```

**Run the test:**

```bash
chmod +x test-security-workflow.sh
./test-security-workflow.sh
```

**Expected result:**
```
✅ Script completes without errors
✅ Two report files generated
✅ Summary shows vulnerability counts
✅ Matches what workflow would output
```

## Test 4: Workflow Validation

**Purpose:** Verify workflow YAML is valid

```bash
# Install YAML validator
pip install pyyaml

# Validate syntax
python3 << EOF
import yaml
with open('.github/workflows/security.yml') as f:
    workflow = yaml.safe_load(f)
    print("✓ YAML is valid")
    print(f"Workflow name: {workflow['name']}")
    print(f"Jobs: {', '.join(workflow['jobs'].keys())}")
EOF
```

**Expected result:**
```
✓ YAML is valid
Workflow name: Security Scanning
Jobs: safety-check, pip-audit-check, security-summary
```

## Test 5: Trigger Workflow (GitHub)

**Purpose:** Test actual workflow execution on GitHub

```bash
# Commit workflow file (if not already done)
git add .github/workflows/security.yml
git commit -m "ci: Add security scanning workflow"
git push origin main

# Or trigger manually via GitHub CLI
gh workflow run security.yml
gh workflow view security.yml
gh run list --workflow=security.yml
```

**Verify on GitHub:**

1. Navigate to: `https://github.com/webbwr/AsciiDoctorArtisan/actions`
2. Find "Security Scanning" workflow
3. Click on the latest run
4. Check all jobs completed successfully
5. Download artifacts and verify contents

**Expected result:**
```
✅ Workflow appears in Actions tab
✅ Triggered automatically or manually
✅ All three jobs complete
✅ Artifacts uploaded successfully
✅ Summary shows results
```

## Test 6: Vulnerability Response Simulation

**Purpose:** Test the full vulnerability remediation workflow

**Simulate vulnerable dependency:**

```bash
# Temporarily downgrade a package to known vulnerable version
pip install 'cryptography==41.0.5'  # Has CVE-2023-50782

# Run scans
safety check
pip-audit

# Should report vulnerability
```

**Fix vulnerability:**

```bash
# Update to patched version
pip install 'cryptography>=42.0.0'

# Re-run scans
safety check
pip-audit

# Should be clean now
```

**Expected result:**
```
✅ Downgraded version triggers vulnerability alerts
✅ Both scanners detect the issue
✅ Updated version passes scans
✅ Process mirrors real-world remediation
```

## Test 7: Scheduled Trigger Verification

**Purpose:** Verify cron schedule is correct

```bash
# Check workflow schedule
grep -A 2 "schedule:" .github/workflows/security.yml

# Verify cron syntax
# Expected: - cron: '0 0 * * 0'
# Means: Sunday at midnight UTC
```

**Cron schedule decoder:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
0 0 * * 0  →  Sunday at 00:00 UTC
```

**Verify next run time:**
```bash
# Using GitHub CLI
gh workflow view security.yml
```

## Test 8: Artifact Download and Analysis

**Purpose:** Practice downloading and analyzing reports

```bash
# Download artifacts from latest run
gh run list --workflow=security.yml --limit 1
LATEST_RUN=$(gh run list --workflow=security.yml --limit 1 --json databaseId --jq '.[0].databaseId')

gh run download $LATEST_RUN

# Extract and view reports
cd safety-security-report/
cat safety-report.json | jq '.'

cd ../pip-audit-security-report/
cat pip-audit-report.json | jq '.'

# Count vulnerabilities
safety_vulns=$(jq '. | length' ../safety-security-report/safety-report.json)
audit_vulns=$(jq '.dependencies | length' ../pip-audit-security-report/pip-audit-report.json)

echo "Safety found: $safety_vulns vulnerabilities"
echo "pip-audit found: $audit_vulns packages with vulnerabilities"
```

## Test 9: Performance Benchmarking

**Purpose:** Measure scan times

```bash
# Benchmark Safety
time safety check

# Benchmark pip-audit
time pip-audit

# Expected times:
# - Safety: 5-15 seconds
# - pip-audit: 10-30 seconds
# - Full workflow: ~5 minutes (includes setup)
```

## Test 10: Integration with CI/CD

**Purpose:** Verify workflow integrates with existing CI

```bash
# Check for conflicts with existing workflows
ls -la .github/workflows/

# Verify workflow runs in parallel with others
# (GitHub Actions allows concurrent workflows)

# Check that security scan doesn't block PRs
# (continue-on-error: true should allow)
```

## Troubleshooting Tests

### Test fails: "Command not found"

```bash
# Install missing tools
pip install safety pip-audit jq

# Or using apt (Linux)
sudo apt install jq
```

### Test fails: "Invalid YAML"

```bash
# Use online validator
# https://yaml-online-parser.appspot.com/

# Or install yamllint
pip install yamllint
yamllint .github/workflows/security.yml
```

### Test fails: "Permission denied"

```bash
# For workflow files
chmod +x test-security-workflow.sh

# For GitHub Actions
gh auth refresh -s workflow
```

### Test fails: "Network error"

```bash
# Retry with verbose output
safety check --debug
pip-audit --verbose

# Check proxy/firewall settings
```

## Automated Test Suite

Create `tests/test_security_workflow.py` for automated testing:

```python
"""Test security workflow functionality."""

import json
import subprocess
from pathlib import Path


def test_safety_installed():
    """Verify Safety is installed."""
    result = subprocess.run(
        ["safety", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Safety" in result.stdout


def test_pip_audit_installed():
    """Verify pip-audit is installed."""
    result = subprocess.run(
        ["pip-audit", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_safety_scan():
    """Run Safety scan and check JSON output."""
    result = subprocess.run(
        ["safety", "check", "--json"],
        capture_output=True,
        text=True
    )
    # Exit code 64 means vulnerabilities found, 0 means clean
    assert result.returncode in [0, 64]

    # Verify valid JSON
    if result.stdout:
        data = json.loads(result.stdout)
        assert isinstance(data, list)


def test_pip_audit_scan():
    """Run pip-audit scan and check JSON output."""
    result = subprocess.run(
        ["pip-audit", "--format", "json"],
        capture_output=True,
        text=True
    )
    # Exit code 1 means vulnerabilities found, 0 means clean
    assert result.returncode in [0, 1]

    # Verify valid JSON
    if result.stdout:
        data = json.loads(result.stdout)
        assert "dependencies" in data


def test_workflow_yaml_exists():
    """Verify workflow file exists and is valid YAML."""
    import yaml

    workflow_path = Path(".github/workflows/security.yml")
    assert workflow_path.exists()

    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)
        assert workflow["name"] == "Security Scanning"
        assert "jobs" in workflow
        assert "safety-check" in workflow["jobs"]
        assert "pip-audit-check" in workflow["jobs"]


def test_workflow_triggers():
    """Verify workflow has correct triggers."""
    import yaml

    with open(".github/workflows/security.yml") as f:
        workflow = yaml.safe_load(f)
        assert "push" in workflow["on"]
        assert "pull_request" in workflow["on"]
        assert "schedule" in workflow["on"]
        assert "workflow_dispatch" in workflow["on"]
```

**Run automated tests:**

```bash
pytest tests/test_security_workflow.py -v
```

## Success Criteria

✅ **All tests pass** - No errors in any test scenario
✅ **Workflow runs** - Triggers successfully on GitHub
✅ **Artifacts generated** - JSON reports uploaded
✅ **Summaries display** - GitHub Actions shows results
✅ **Documentation clear** - Team understands how to use
✅ **Response tested** - Vulnerability remediation works

## Next Steps After Testing

1. ✅ Commit workflow to repository
2. ✅ Monitor first few runs for issues
3. ✅ Share documentation with team
4. ✅ Set up notifications for security alerts
5. ✅ Schedule regular review of scan results
6. ✅ Integrate into development process

---

**Test Suite Version:** 1.0.0
**Last Updated:** October 29, 2025
**Compatible With:** AsciiDoc Artisan v1.5.0+
