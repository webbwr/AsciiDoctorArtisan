# Security Audit Logging

**v2.1.0** | Credential operation audit trail

---

## Log Format

```
SECURITY_AUDIT: timestamp=<ISO8601> user=<name> action=<action> service=<service> success=<bool>
```

---

## Actions

| Action | Description |
|--------|-------------|
| `store_key_attempt` | Key storage requested |
| `store_key` | Storage result |
| `get_key_attempt` | Key retrieval requested |
| `get_key` | Retrieval result |
| `delete_key_attempt` | Key deletion requested |
| `delete_key` | Deletion result |

---

## Query Script

```bash
./scripts/query_security_audit.sh all        # All entries
./scripts/query_security_audit.sh failures   # Failed ops
./scripts/query_security_audit.sh service anthropic_api_key
./scripts/query_security_audit.sh user webbp
./scripts/query_security_audit.sh today
```

---

## Manual Queries

```bash
grep "SECURITY_AUDIT:" asciidoc_artisan.log
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "success=False"
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "service=anthropic"
```

---

## What is Logged

- Operation type
- Service identifier
- Username
- Timestamp (UTC)
- Success/failure

## What is NOT Logged

- API keys or passwords
- IP addresses
- Request details

---

## Security Recommendations

| Area | Recommendation |
|------|----------------|
| Permissions | `chmod 600 asciidoc_artisan.log` |
| Rotation | Daily, keep 90 days |
| Retention | 90 days minimum |
| Monitoring | Alert on multiple failures |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No logs | Check `logging.basicConfig(level=logging.INFO)` |
| Missing handler | Verify logger has handlers attached |

---

*v2.1.0 | Dec 5, 2025*
