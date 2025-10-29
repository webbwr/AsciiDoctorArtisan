# Security Audit Logging Guide

This guide explains how to use and query the comprehensive security audit logging system for credential operations in AsciiDoc Artisan.

## Overview

The security audit logging system provides forensic capabilities by tracking all credential operations. Every attempt to store, retrieve, check, or delete API keys is logged with full details.

## Log Format

All audit log entries follow this format:

```
SECURITY_AUDIT: timestamp=<ISO8601-UTC> user=<username> action=<action> service=<service> success=<bool>
```

### Field Descriptions

- **timestamp**: UTC timestamp in ISO 8601 format (e.g., `2025-10-29T11:38:49.059469+00:00`)
- **user**: OS username of the user performing the operation (from `getpass.getuser()`)
- **action**: The operation being performed
- **service**: Service identifier (e.g., `anthropic_api_key`, `openai`)
- **success**: Boolean indicating whether the operation succeeded

### Action Types

| Action | Description |
|--------|-------------|
| `store_key_attempt` | User initiated a request to store an API key |
| `store_key` | API key storage operation (final result) |
| `get_key_attempt` | User initiated a request to retrieve an API key |
| `get_key` | API key retrieval operation (final result) |
| `delete_key_attempt` | User initiated a request to delete an API key |
| `delete_key` | API key deletion operation (final result) |
| `check_key_attempt` | User initiated a request to check if key exists |
| `check_key` | Key existence check operation (final result) |

## Example Log Entries

### Successful Operations

```
2025-10-29 07:38:49,059 - asciidoc_artisan.core.secure_credentials - INFO - SECURITY_AUDIT: timestamp=2025-10-29T11:38:49.059469+00:00 user=webbp action=store_key_attempt service=anthropic_api_key success=True

2025-10-29 07:38:49,269 - asciidoc_artisan.core.secure_credentials - INFO - SECURITY_AUDIT: timestamp=2025-10-29T11:38:49.269409+00:00 user=webbp action=store_key service=anthropic_api_key success=True

2025-10-29 07:38:49,269 - asciidoc_artisan.core.secure_credentials - INFO - SECURITY_AUDIT: timestamp=2025-10-29T11:38:49.269480+00:00 user=webbp action=get_key_attempt service=anthropic_api_key success=True

2025-10-29 07:38:49,269 - asciidoc_artisan.core.secure_credentials - INFO - SECURITY_AUDIT: timestamp=2025-10-29T11:38:49.269709+00:00 user=webbp action=get_key service=anthropic_api_key success=True
```

### Failed Operations

```
2025-10-29 07:38:49,270 - asciidoc_artisan.core.secure_credentials - INFO - SECURITY_AUDIT: timestamp=2025-10-29T11:38:49.270564+00:00 user=webbp action=get_key service=nonexistent_service success=False
```

## Querying Audit Logs

### Using the Query Script

A convenient query script is provided at `scripts/query_security_audit.sh`:

```bash
# Show all audit entries
./scripts/query_security_audit.sh all

# Show only failed operations
./scripts/query_security_audit.sh failures

# Show operations for specific service
./scripts/query_security_audit.sh service anthropic_api_key

# Show operations by specific user
./scripts/query_security_audit.sh user webbp

# Show today's operations
./scripts/query_security_audit.sh today

# Show last N entries
./scripts/query_security_audit.sh last 100

# Show specific operation types
./scripts/query_security_audit.sh store     # All store operations
./scripts/query_security_audit.sh get       # All get operations
./scripts/query_security_audit.sh delete    # All delete operations
./scripts/query_security_audit.sh check     # All check operations
```

### Manual Queries (grep)

If log files are in known locations, you can query them directly:

```bash
# Find all audit entries
grep "SECURITY_AUDIT:" asciidoc_artisan.log

# Find failed operations
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "success=False"

# Find operations for specific service
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "service=anthropic_api_key"

# Find operations by specific user
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "user=webbp"

# Find operations in time range (example: October 29, 2025)
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "timestamp=2025-10-29"

# Find store operations
grep "SECURITY_AUDIT:" asciidoc_artisan.log | grep "action=store_key"
```

### Parsing for Analysis

Example Python script to parse and analyze audit logs:

```python
import re
from collections import Counter
from datetime import datetime

def parse_audit_log(log_line):
    """Parse a SECURITY_AUDIT log line into components."""
    pattern = r'SECURITY_AUDIT: timestamp=(?P<timestamp>\S+) user=(?P<user>\S+) action=(?P<action>\S+) service=(?P<service>\S+) success=(?P<success>\S+)'
    match = re.search(pattern, log_line)
    if match:
        return match.groupdict()
    return None

# Read log file
with open('asciidoc_artisan.log', 'r') as f:
    audit_entries = [parse_audit_log(line) for line in f if 'SECURITY_AUDIT:' in line]
    audit_entries = [e for e in audit_entries if e]  # Remove None values

# Analyze
print(f"Total audit entries: {len(audit_entries)}")

# Count by action
actions = Counter(e['action'] for e in audit_entries)
print(f"\nOperations by type:")
for action, count in actions.items():
    print(f"  {action}: {count}")

# Count failures
failures = [e for e in audit_entries if e['success'] == 'False']
print(f"\nTotal failures: {len(failures)}")

# Count by service
services = Counter(e['service'] for e in audit_entries)
print(f"\nOperations by service:")
for service, count in services.items():
    print(f"  {service}: {count}")

# Count by user
users = Counter(e['user'] for e in audit_entries)
print(f"\nOperations by user:")
for user, count in users.items():
    print(f"  {user}: {count}")
```

## Security Considerations

### What is Logged

- Operation type (store, get, delete, check)
- Service identifier
- Username (OS username)
- Timestamp (UTC)
- Success/failure status

### What is NOT Logged

- **API keys or passwords** - Never logged for security
- IP addresses
- Application state
- Request details

### Log Storage Recommendations

1. **File Permissions**: Ensure log files have restricted permissions
   ```bash
   chmod 600 asciidoc_artisan.log
   ```

2. **Log Rotation**: Implement log rotation to prevent disk space issues
   ```bash
   # Example logrotate configuration
   /path/to/asciidoc_artisan.log {
       daily
       rotate 90
       compress
       delaycompress
       missingok
       notifempty
   }
   ```

3. **Secure Storage**: Store logs in secure location with appropriate access controls

4. **Retention Policy**: Define and enforce log retention policies
   - Recommended: Keep audit logs for at least 90 days
   - For compliance: May need to keep for 1+ years

5. **Monitoring**: Set up alerts for suspicious patterns
   - Multiple failed operations
   - Operations outside business hours
   - Unusual service access patterns

### Forensic Analysis Use Cases

1. **Unauthorized Access Attempts**
   ```bash
   # Find all failed get_key operations
   ./scripts/query_security_audit.sh failures | grep "get_key"
   ```

2. **Credential Lifecycle Tracking**
   ```bash
   # Track all operations for a specific service
   ./scripts/query_security_audit.sh service anthropic_api_key
   ```

3. **User Activity Audit**
   ```bash
   # Review all operations by a specific user
   ./scripts/query_security_audit.sh user suspect_username
   ```

4. **Time-based Investigation**
   ```bash
   # Find operations during specific time period
   grep "SECURITY_AUDIT:" logs/*.log | grep "timestamp=2025-10-29T23:"
   ```

## Integration with External Systems

### Sending to Syslog

Configure Python logging to send to syslog:

```python
import logging
from logging.handlers import SysLogHandler

logger = logging.getLogger('asciidoc_artisan.core.secure_credentials')
syslog = SysLogHandler(address='/dev/log')
syslog.setLevel(logging.INFO)
logger.addHandler(syslog)
```

### Sending to External Monitoring

Example: Send to a monitoring service (e.g., Datadog, Splunk)

```python
import logging
import requests

class SecurityMonitoringHandler(logging.Handler):
    def __init__(self, api_endpoint, api_key):
        super().__init__()
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def emit(self, record):
        if 'SECURITY_AUDIT:' in record.getMessage():
            try:
                requests.post(
                    self.api_endpoint,
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    json={'message': record.getMessage(), 'level': record.levelname}
                )
            except Exception:
                pass  # Don't break on monitoring failure

# Add handler
logger = logging.getLogger('asciidoc_artisan.core.secure_credentials')
monitor = SecurityMonitoringHandler('https://api.monitoring.example.com/logs', 'your-api-key')
logger.addHandler(monitor)
```

## Testing the Audit System

Run the demonstration script to see audit logging in action:

```bash
python test_audit_demo.py
```

This will:
1. Store a test API key
2. Retrieve the key
3. Check if key exists
4. Delete the key
5. Verify deletion
6. Test Anthropic convenience methods

All operations will be logged with SECURITY_AUDIT entries.

## Troubleshooting

### No Audit Logs Appearing

1. **Check logging level**: Ensure INFO level is enabled
   ```python
   logging.basicConfig(level=logging.INFO)
   ```

2. **Check log handlers**: Verify handlers are configured
   ```python
   logger = logging.getLogger('asciidoc_artisan.core.secure_credentials')
   print(logger.handlers)  # Should not be empty
   ```

3. **Check for errors**: Look for "Audit logging failed" messages

### Audit Logging Failures

If audit logging fails, it will:
1. Not break application functionality
2. Log an error message: "Audit logging failed: <reason>"
3. Continue with the credential operation

### Performance Concerns

Audit logging is designed to be lightweight:
- Simple string formatting
- Single log call per operation
- No blocking I/O
- Failure doesn't impact operation

If performance is critical:
- Use asynchronous logging handlers
- Write to local files, not network
- Consider buffering log writes

## Compliance Considerations

This audit logging system can help meet compliance requirements:

- **SOC 2**: Logging of access to sensitive data
- **GDPR**: Audit trail for data access
- **HIPAA**: Access logs for protected information
- **PCI-DSS**: Logging of access to cardholder data

Consult with compliance experts for your specific requirements.

## Future Enhancements

Potential future improvements:
- Structured logging (JSON format)
- Real-time alerting
- Dashboard for visualization
- Anomaly detection
- Correlation with other system events
- Geographic IP tracking (if network-based)

---

**Last Updated**: October 29, 2025
**Version**: 1.5.0
