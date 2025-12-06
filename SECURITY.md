# Security Policy

**v2.1.0** | Dec 5, 2025

---

## Supported Versions

| Version | Status |
|---------|--------|
| 2.1.x | ✅ Current |
| 2.0.x | ✅ Maintenance |
| < 2.0 | ❌ Unsupported |

---

## Security Features

| Feature | Implementation |
|---------|----------------|
| Atomic Writes | temp+rename pattern (FR-069) |
| Path Sanitization | Blocks traversal attacks (FR-068) |
| Subprocess Safety | Always `shell=False` (FR-070) |
| Credential Storage | OS keyring encryption (FR-071) |
| Local-First | No cloud uploads without action |

---

## Reporting Vulnerabilities

**Email:** webbp@localhost
**Subject:** [SECURITY] Brief description
**Response:** Within 48 hours

### Include

1. What the bug does
2. Steps to reproduce
3. Impact assessment
4. Suggested fix (optional)

### Do NOT

- Post publicly before fix
- Exploit the vulnerability
- Share before disclosure

---

## Response Timeline

| Severity | Response | Patch |
|----------|----------|-------|
| Critical | 24 hours | 7 days |
| High | 48 hours | 30 days |
| Medium | 72 hours | 90 days |
| Low | 1 week | Next release |

---

## Threat Model

| Threat | Risk | Mitigation |
|--------|------|------------|
| Path Traversal | Low | `sanitize_path()` |
| Command Injection | Low | `shell=False` |
| Credential Theft | Medium | OS keyring |
| Malicious Files | Medium | Input validation |

**Out of Scope:** Physical access, OS vulnerabilities, social engineering

---

## Best Practices

**Users:**
- Keep updated
- Verify downloads from official sites
- Review changes before commit

**Developers:**
- Review PRs for security
- Never commit API keys
- Use `pip-audit` for scanning

---

## Testing

| Metric | Value |
|--------|-------|
| Unit tests | 5,122 |
| E2E tests | 17 |
| Integration tests | 17 |
| Security tests | 377 |
| Coverage | 98% |

---

## OWASP Top 10 (2021)

| ID | Category | Status |
|----|----------|--------|
| A01 | Broken Access Control | ✅ Mitigated |
| A02 | Cryptographic Failures | ✅ Mitigated |
| A03 | Injection | ✅ Prevented |
| A08 | Data Integrity | ✅ Atomic writes |

---

## Resources

- [SPECIFICATIONS.md](SPECIFICATIONS.md) — Security FRs (FR-068 to FR-072)
- [security-guide.md](docs/developer/security-guide.md) — Audit logging

---

*v2.1.0 | Security Policy | Dec 5, 2025*
