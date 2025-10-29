# Security Scanning Workflow - Example Output

This document shows real-world examples of what the security scanning workflow output looks like.

## Table of Contents

1. [Clean Scan (No Vulnerabilities)](#clean-scan-no-vulnerabilities)
2. [Vulnerabilities Detected](#vulnerabilities-detected)
3. [Individual Job Outputs](#individual-job-outputs)
4. [Artifact Contents](#artifact-contents)

---

## Clean Scan (No Vulnerabilities)

### GitHub Actions Summary View

```
🔒 Security Scan Summary

Repository: webbwr/AsciiDoctorArtisan
Branch: main
Commit: 4fc650912a8b3c7d2e1f9a6b8c3d4e5f6a7b8c9d
Scan Date: 2025-10-29 00:00:15 UTC

---

### Safety Scan
✅ No vulnerabilities found

### pip-audit Scan
✅ No vulnerabilities found

---

Next Steps:
- Review detailed reports in workflow artifacts
- Check vulnerability severity and affected versions
- Update vulnerable dependencies where possible
- Create issues for vulnerabilities requiring investigation
```

### Job Status Display

```
✅ safety-check          Completed in 2m 34s
✅ pip-audit-check      Completed in 2m 18s
✅ security-summary     Completed in 24s
```

### Individual Job Output: Safety

```
Safety Security Scan Results

✅ No vulnerabilities found

Scan completed at: 2025-10-29 00:00:08 UTC
```

### Individual Job Output: pip-audit

```
pip-audit Security Scan Results

✅ No vulnerabilities found

Scan completed at: 2025-10-29 00:00:13 UTC
```

---

## Vulnerabilities Detected

### GitHub Actions Summary View

```
🔒 Security Scan Summary

Repository: webbwr/AsciiDoctorArtisan
Branch: dev
Commit: abc123def456ghi789jkl012mno345pqr678stu
Scan Date: 2025-10-29 12:30:45 UTC

---

### Safety Scan
⚠️ Found 3 vulnerabilities

### pip-audit Scan
⚠️ Found 2 packages with vulnerabilities

---

Next Steps:
- Review detailed reports in workflow artifacts
- Check vulnerability severity and affected versions
- Update vulnerable dependencies where possible
- Create issues for vulnerabilities requiring investigation
```

### Job Status Display

```
⚠️ safety-check          Completed with warnings in 2m 41s
⚠️ pip-audit-check      Completed with warnings in 2m 29s
✅ security-summary     Completed in 26s
```

### Individual Job Output: Safety (With Vulnerabilities)

```
Safety Security Scan Results

⚠️ 3 vulnerabilities found

See uploaded artifacts for detailed report.

Scan completed at: 2025-10-29 12:30:35 UTC
```

### Console Output Excerpt (Safety)

```
Run safety check

╭────────────────────────────────────────────────────────────────────────────╮
│                                                                            │
│                               /$$$$$$            /$$                       │
│                              /$$__  $$          | $$                       │
│           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$        │
│          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$        │
│         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$        │
│          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$        │
│          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$        │
│         |_______/  \_______/|__/     \_______/   \___/   \____  $$        │
│                                                          /$$  | $$        │
│                                                         |  $$$$$$/        │
│  by safetycli.com                                       \______/         │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

 REPORT

+==============================================================================+
│                                                                              │
│                    VULNERABILITIES FOUND                                     │
│                                                                              │
+==============================================================================+

-> Vulnerability found in cryptography version 41.0.5
   Vulnerability ID: 67895
   Affected spec: <41.0.6
   ADVISORY: Cryptography 41.0.5 and earlier are vulnerable to Bleichenbacher
   timing attacks. An attacker may be able to decrypt RSA ciphertext by making
   repeated queries to a server. Fixed in 41.0.6+
   Severity: HIGH
   CVE: CVE-2023-50782

-> Vulnerability found in requests version 2.31.0
   Vulnerability ID: 62019
   Affected spec: <2.32.0
   ADVISORY: The requests library could be vulnerable to SSRF attacks when
   redirecting to untrusted hosts. Fixed in 2.32.0+
   Severity: MEDIUM
   CVE: CVE-2024-35195

-> Vulnerability found in certifi version 2023.7.22
   Vulnerability ID: 62044
   Affected spec: <2024.7.4
   ADVISORY: Certifi prior to 2024.07.04 includes a root certificate from
   TrustCor that has been removed from Mozilla, Chrome, and Apple trust stores.
   Fixed in 2024.7.4+
   Severity: LOW
   CVE: CVE-2023-37920

+==============================================================================+

  3 vulnerabilities reported

  For commercial support and access to additional features visit:
  https://safetycli.com
```

### Individual Job Output: pip-audit (With Vulnerabilities)

```
pip-audit Security Scan Results

⚠️ 2 packages with vulnerabilities found

See uploaded artifacts for detailed report.

Scan completed at: 2025-10-29 12:30:41 UTC
```

### Console Output Excerpt (pip-audit)

```
Run pip-audit

Found 2 known vulnerabilities in 2 packages

Name         Version  ID                  Fix Versions
------------ -------- ------------------- ------------
cryptography 41.0.5   PYSEC-2023-252      41.0.6,42.0.0
requests     2.31.0   GHSA-9wx4-h78v-vm56 2.32.0
```

---

## Individual Job Outputs

### Safety Check Job - Full Output

```
Run actions/checkout@v4
  Syncing repository: webbwr/AsciiDoctorArtisan
  Checking out ref: refs/heads/main
  ✓ Checked out to: /home/runner/work/AsciiDoctorArtisan/AsciiDoctorArtisan

Run actions/setup-python@v5
  Successfully set up CPython (3.12.5)
  Python version: 3.12.5
  ✓ Successfully installed pip 24.0
  ✓ Successfully restored cache

Run python -m pip install --upgrade pip
  Requirement already satisfied: pip in /opt/hostedtoolcache/Python/3.12.5/x64/lib/python3.12/site-packages (24.0)
  Collecting pip
    Downloading pip-24.2-py3-none-any.whl (1.8 MB)
  Installing collected packages: pip
  Successfully installed pip-24.2

Run pip install safety
  Collecting safety
    Downloading safety-3.2.7-py3-none-any.whl (85 kB)
  Collecting click>=8.0.2 (from safety)
    Using cached click-8.1.7-py3-none-any.whl (97 kB)
  ...
  Successfully installed safety-3.2.7 click-8.1.7 ...

Run pip install -r requirements.txt
  Collecting PySide6>=6.9.0 (from -r requirements.txt (line 11))
    Downloading PySide6-6.9.0-cp312-cp312-manylinux_2_28_x86_64.whl (512 MB)
  ...
  Successfully installed 35 packages

Run safety check
  [Output shown in previous section]

Run echo "## Safety Security Scan Results" >> $GITHUB_STEP_SUMMARY
  ✓ Summary generated

Run actions/upload-artifact@v4
  Artifact name: safety-security-report
  Root directory: /home/runner/work/AsciiDoctorArtisan/AsciiDoctorArtisan
  Files: 1
  Size: 2.4 KB
  ✓ Artifact uploaded successfully
```

### pip-audit Check Job - Full Output

```
Run actions/checkout@v4
  ✓ Checked out to: /home/runner/work/AsciiDoctorArtisan/AsciiDoctorArtisan

Run actions/setup-python@v5
  ✓ Successfully set up CPython (3.12.5)
  ✓ Successfully restored cache

Run python -m pip install --upgrade pip
  ✓ Successfully installed pip-24.2

Run pip install pip-audit
  Collecting pip-audit
    Downloading pip_audit-2.7.3-py3-none-any.whl (324 kB)
  ...
  Successfully installed pip-audit-2.7.3 ...

Run pip install -r requirements.txt
  ✓ Successfully installed 35 packages

Run pip-audit
  [Output shown in previous section]

Run echo "## pip-audit Security Scan Results" >> $GITHUB_STEP_SUMMARY
  ✓ Summary generated

Run actions/upload-artifact@v4
  ✓ Artifact uploaded successfully
```

---

## Artifact Contents

### Safety Report JSON (`safety-report.json`)

```json
[
  {
    "vulnerability": "Cryptography vulnerable to Bleichenbacher timing attacks",
    "ignored": false,
    "more_info_url": "https://pyup.io/v/67895/f17",
    "package_name": "cryptography",
    "vulnerable_spec": "<41.0.6",
    "all_vulnerable_specs": [
      "<41.0.6"
    ],
    "analyzed_version": "41.0.5",
    "advisory": "Cryptography 41.0.5 and earlier are vulnerable to Bleichenbacher timing attacks. An attacker may be able to decrypt RSA ciphertext by making repeated queries to a server that uses the RSA decryption API. The vulnerability affects the cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15 padding implementation. Users should upgrade to cryptography 41.0.6 or later. This vulnerability is tracked as CVE-2023-50782.",
    "is_transitive": false,
    "published_date": "2023-12-05",
    "fixed_in": [
      "41.0.6",
      "42.0.0"
    ],
    "closest_versions_without_known_vulnerabilities": [
      "41.0.6"
    ],
    "resources": [
      "CVE-2023-50782"
    ],
    "CVE": "CVE-2023-50782",
    "severity": {
      "source": "nvd",
      "cvss": {
        "version": "3.1",
        "base_score": 7.5,
        "vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
      }
    },
    "affected_versions": [],
    "more_info_path": "/v/67895/f17"
  },
  {
    "vulnerability": "requests allows redirects to untrusted hosts",
    "ignored": false,
    "more_info_url": "https://pyup.io/v/62019/f17",
    "package_name": "requests",
    "vulnerable_spec": "<2.32.0",
    "all_vulnerable_specs": [
      "<2.32.0"
    ],
    "analyzed_version": "2.31.0",
    "advisory": "The requests library in versions prior to 2.32.0 could be vulnerable to SSRF attacks when redirecting to untrusted hosts. The library should properly validate redirect targets. Users should upgrade to requests 2.32.0 or later. This vulnerability is tracked as CVE-2024-35195.",
    "is_transitive": false,
    "published_date": "2024-05-20",
    "fixed_in": [
      "2.32.0"
    ],
    "closest_versions_without_known_vulnerabilities": [
      "2.32.0"
    ],
    "resources": [
      "CVE-2024-35195"
    ],
    "CVE": "CVE-2024-35195",
    "severity": {
      "source": "nvd",
      "cvss": {
        "version": "3.1",
        "base_score": 5.6,
        "vector_string": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L"
      }
    },
    "affected_versions": [],
    "more_info_path": "/v/62019/f17"
  },
  {
    "vulnerability": "Certifi includes TrustCor root certificate",
    "ignored": false,
    "more_info_url": "https://pyup.io/v/62044/f17",
    "package_name": "certifi",
    "vulnerable_spec": "<2024.7.4",
    "all_vulnerable_specs": [
      "<2024.7.4"
    ],
    "analyzed_version": "2023.7.22",
    "advisory": "Certifi prior to 2024.07.04 includes a root certificate from TrustCor that has been removed from Mozilla, Chrome, and Apple trust stores. Users should upgrade to certifi 2024.7.4 or later. This vulnerability is tracked as CVE-2023-37920.",
    "is_transitive": true,
    "published_date": "2023-07-25",
    "fixed_in": [
      "2024.7.4"
    ],
    "closest_versions_without_known_vulnerabilities": [
      "2024.7.4"
    ],
    "resources": [
      "CVE-2023-37920"
    ],
    "CVE": "CVE-2023-37920",
    "severity": {
      "source": "nvd",
      "cvss": {
        "version": "3.1",
        "base_score": 3.7,
        "vector_string": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N"
      }
    },
    "affected_versions": [],
    "more_info_path": "/v/62044/f17"
  }
]
```

### pip-audit Report JSON (`pip-audit-report.json`)

```json
{
  "dependencies": [
    {
      "name": "cryptography",
      "version": "41.0.5",
      "vulns": [
        {
          "id": "PYSEC-2023-252",
          "fix_versions": [
            "41.0.6",
            "42.0.0"
          ],
          "description": "Cryptography is a package designed to expose cryptographic primitives and recipes to Python developers. In affected versions `Cipher.update_into` would accept Python objects which implement the buffer protocol, but provide only immutable buffers. This would allow immutable objects (such as `bytes`) to be mutated, thus violating fundamental rules of Python and resulting in corrupted output. This now correctly raises an exception. This issue has been present since `update_into` was originally introduced in cryptography 1.8.",
          "aliases": [
            "CVE-2023-50782",
            "GHSA-3ww4-gg4f-jr7f"
          ]
        }
      ],
      "skip_reason": null
    },
    {
      "name": "requests",
      "version": "2.31.0",
      "vulns": [
        {
          "id": "GHSA-9wx4-h78v-vm56",
          "fix_versions": [
            "2.32.0"
          ],
          "description": "Requests is a HTTP library. Since Requests 2.3.0, Requests has been leaking Proxy-Authorization headers to destination servers when redirected to an HTTPS endpoint. This is a product of how we use `rebuild_proxies` to reattach the `Proxy-Authorization` header to requests. For HTTP connections sent through the tunnel, the proxy will identify the header in the request itself and remove it prior to forwarding to the destination server. However when sent over HTTPS, the `Proxy-Authorization` header must be sent in the CONNECT request as the proxy has no visibility into the tunneled request. This results in Requests forwarding proxy credentials to the destination server unintentionally, allowing a malicious actor to potentially exfiltrate sensitive information. This issue has been patched in version 2.32.0.",
          "aliases": [
            "CVE-2024-35195",
            "PYSEC-2024-60"
          ]
        }
      ],
      "skip_reason": null
    }
  ]
}
```

---

## How to Read the Outputs

### Understanding Job Status Icons

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | Success | Job completed without issues |
| ⚠️ | Warning | Job completed but found vulnerabilities (non-blocking) |
| ❌ | Failure | Job failed to complete |
| 🔄 | Running | Job is currently executing |
| ⏸️ | Pending | Job is queued and waiting |

### Interpreting Severity Scores (CVSS)

CVSS scores range from 0.0 to 10.0:

| Score Range | Severity | Action Required |
|-------------|----------|-----------------|
| 9.0 - 10.0 | **Critical** | Immediate patching (same day) |
| 7.0 - 8.9 | **High** | Patch within 1 week |
| 4.0 - 6.9 | **Medium** | Patch within 1 month |
| 0.1 - 3.9 | **Low** | Patch when convenient |
| 0.0 | **None** | Informational only |

### Transitive vs Direct Dependencies

- **Direct dependency:** Package explicitly listed in `requirements.txt`
- **Transitive dependency:** Installed as a requirement of another package
- **In JSON:** `"is_transitive": true` indicates transitive

**Example:**
```
requests (direct)
  └── certifi (transitive - required by requests)
```

---

## Real-World Response Example

### Scenario: High Severity Vulnerability Detected

**Workflow output shows:**
```
⚠️ Found 1 high severity vulnerability in cryptography 41.0.5
CVE-2023-50782: Bleichenbacher timing attack
Fix available: 41.0.6+
```

**Developer response:**

1. **Review details** (download artifact):
   ```bash
   cat safety-report.json | jq '.[] | select(.package_name=="cryptography")'
   ```

2. **Check if fix is available**:
   ```bash
   pip index versions cryptography
   # Latest: 42.0.1
   ```

3. **Test update locally**:
   ```bash
   python -m venv test-update
   source test-update/bin/activate
   pip install cryptography==42.0.1
   pip install -r requirements.txt
   make test
   # All tests pass ✓
   ```

4. **Update requirements.txt**:
   ```diff
   - cryptography>=41.0.5
   + cryptography>=42.0.1
   ```

5. **Commit and push**:
   ```bash
   git add requirements.txt
   git commit -m "Security: Update cryptography to 42.0.1 (fixes CVE-2023-50782)"
   git push
   ```

6. **Verify fix**:
   - Wait for workflow to run on push
   - Check that vulnerability no longer appears
   - Next scan should show ✅ clean

---

**Document Version:** 1.0.0
**Last Updated:** October 29, 2025
**For:** AsciiDoc Artisan v1.5.0+
