#!/usr/bin/env python3
"""
Security Audit Log Analyzer

This script analyzes security audit logs to identify patterns, anomalies,
and generate security reports.

Usage:
    python scripts/analyze_security_audit.py [log_file]

If no log file is provided, it will search for logs in standard locations.
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional


class AuditLogEntry:
    """Represents a single audit log entry."""

    def __init__(self, timestamp: str, user: str, action: str, service: str, success: bool):
        self.timestamp = timestamp
        self.user = user
        self.action = action
        self.service = service
        self.success = success

    @classmethod
    def from_log_line(cls, line: str) -> Optional["AuditLogEntry"]:
        """Parse a log line into an AuditLogEntry."""
        pattern = r"SECURITY_AUDIT: timestamp=(?P<timestamp>\S+) user=(?P<user>\S+) action=(?P<action>\S+) service=(?P<service>\S+) success=(?P<success>\S+)"
        match = re.search(pattern, line)
        if match:
            data = match.groupdict()
            return cls(
                timestamp=data["timestamp"],
                user=data["user"],
                action=data["action"],
                service=data["service"],
                success=data["success"] == "True",
            )
        return None

    def __repr__(self):
        return f"AuditLogEntry({self.timestamp}, {self.user}, {self.action}, {self.service}, {self.success})"


class SecurityAuditAnalyzer:
    """Analyzes security audit logs."""

    def __init__(self):
        self.entries: List[AuditLogEntry] = []

    def load_from_file(self, filepath: Path):
        """Load audit entries from a log file."""
        with open(filepath, "r") as f:
            for line in f:
                if "SECURITY_AUDIT:" in line:
                    entry = AuditLogEntry.from_log_line(line)
                    if entry:
                        self.entries.append(entry)

    def load_from_stdin(self):
        """Load audit entries from stdin."""
        for line in sys.stdin:
            if "SECURITY_AUDIT:" in line:
                entry = AuditLogEntry.from_log_line(line)
                if entry:
                    self.entries.append(entry)

    def get_summary(self) -> Dict:
        """Generate summary statistics."""
        if not self.entries:
            return {"total": 0}

        return {
            "total": len(self.entries),
            "successful": sum(1 for e in self.entries if e.success),
            "failed": sum(1 for e in self.entries if not e.success),
            "unique_users": len(set(e.user for e in self.entries)),
            "unique_services": len(set(e.service for e in self.entries)),
            "unique_actions": len(set(e.action for e in self.entries)),
        }

    def get_action_breakdown(self) -> Counter:
        """Get breakdown by action type."""
        return Counter(e.action for e in self.entries)

    def get_service_breakdown(self) -> Counter:
        """Get breakdown by service."""
        return Counter(e.service for e in self.entries)

    def get_user_breakdown(self) -> Counter:
        """Get breakdown by user."""
        return Counter(e.user for e in self.entries)

    def get_failures(self) -> List[AuditLogEntry]:
        """Get all failed operations."""
        return [e for e in self.entries if not e.success]

    def get_user_failures(self) -> Dict[str, List[AuditLogEntry]]:
        """Get failures grouped by user."""
        failures = defaultdict(list)
        for entry in self.entries:
            if not entry.success:
                failures[entry.user].append(entry)
        return dict(failures)

    def get_service_failures(self) -> Dict[str, List[AuditLogEntry]]:
        """Get failures grouped by service."""
        failures = defaultdict(list)
        for entry in self.entries:
            if not entry.success:
                failures[entry.service].append(entry)
        return dict(failures)

    def print_report(self):
        """Print comprehensive security audit report."""
        print()
        print("=" * 80)
        print("  SECURITY AUDIT LOG ANALYSIS REPORT")
        print("=" * 80)
        print()

        # Summary
        summary = self.get_summary()
        print("SUMMARY")
        print("-" * 80)
        print(f"  Total entries:       {summary.get('total', 0):,}")
        print(f"  Successful:          {summary.get('successful', 0):,}")
        print(f"  Failed:              {summary.get('failed', 0):,}")
        if summary.get("total", 0) > 0:
            failure_rate = (summary.get("failed", 0) / summary["total"]) * 100
            print(f"  Failure rate:        {failure_rate:.2f}%")
        print(f"  Unique users:        {summary.get('unique_users', 0)}")
        print(f"  Unique services:     {summary.get('unique_services', 0)}")
        print(f"  Unique actions:      {summary.get('unique_actions', 0)}")
        print()

        # Actions breakdown
        print("OPERATIONS BY TYPE")
        print("-" * 80)
        actions = self.get_action_breakdown()
        for action, count in actions.most_common():
            print(f"  {action:30} {count:>8,}")
        print()

        # Services breakdown
        print("OPERATIONS BY SERVICE")
        print("-" * 80)
        services = self.get_service_breakdown()
        for service, count in services.most_common(10):  # Top 10
            print(f"  {service:30} {count:>8,}")
        if len(services) > 10:
            print(f"  ... and {len(services) - 10} more services")
        print()

        # Users breakdown
        print("OPERATIONS BY USER")
        print("-" * 80)
        users = self.get_user_breakdown()
        for user, count in users.most_common():
            print(f"  {user:30} {count:>8,}")
        print()

        # Failures
        failures = self.get_failures()
        if failures:
            print("FAILED OPERATIONS")
            print("-" * 80)
            print(f"  Total failures: {len(failures):,}")
            print()

            print("  By User:")
            user_failures = self.get_user_failures()
            for user, user_fails in user_failures.items():
                print(f"    {user:30} {len(user_fails):>8,} failures")
            print()

            print("  By Service:")
            service_failures = self.get_service_failures()
            for service, svc_fails in service_failures.items():
                print(f"    {service:30} {len(svc_fails):>8,} failures")
            print()

            print("  Recent Failures (last 10):")
            for entry in failures[-10:]:
                print(f"    {entry.timestamp} | {entry.user:15} | {entry.action:20} | {entry.service}")
        else:
            print("FAILURES")
            print("-" * 80)
            print("  No failures found ✓")
        print()

        # Security recommendations
        print("SECURITY RECOMMENDATIONS")
        print("-" * 80)
        if summary.get("failed", 0) > 10:
            print("  ⚠ High number of failures detected")
            print("    - Review failed operations for unauthorized access attempts")
            print("    - Consider implementing rate limiting")
        if summary.get("unique_users", 0) > 5:
            print("  ⚠ Multiple users accessing credentials")
            print("    - Review user access permissions")
            print("    - Ensure principle of least privilege")
        if len(failures) == 0:
            print("  ✓ No failures detected - system operating normally")
        print()

        print("=" * 80)
        print()


def find_log_files() -> List[Path]:
    """Find log files in standard locations."""
    locations = [
        Path.cwd() / "asciidoc_artisan.log",
        Path.home() / ".local" / "share" / "AsciiDocArtisan" / "asciidoc_artisan.log",
        Path("/tmp") / "asciidoc_artisan.log",
    ]

    found = []
    for loc in locations:
        if loc.exists() and loc.is_file():
            found.append(loc)

    return found


def main():
    """Main entry point."""
    analyzer = SecurityAuditAnalyzer()

    # Load logs
    if len(sys.argv) > 1:
        # Log file provided
        log_file = Path(sys.argv[1])
        if not log_file.exists():
            print(f"Error: Log file not found: {log_file}", file=sys.stderr)
            sys.exit(1)
        print(f"Loading logs from: {log_file}")
        analyzer.load_from_file(log_file)
    elif not sys.stdin.isatty():
        # Reading from stdin (pipe)
        print("Loading logs from stdin...")
        analyzer.load_from_stdin()
    else:
        # Search for log files
        log_files = find_log_files()
        if not log_files:
            print("Error: No log files found in standard locations", file=sys.stderr)
            print(
                "Usage: python scripts/analyze_security_audit.py [log_file]",
                file=sys.stderr,
            )
            print(
                "   or: grep SECURITY_AUDIT logs/* | python scripts/analyze_security_audit.py",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Found {len(log_files)} log file(s):")
        for lf in log_files:
            print(f"  - {lf}")
        print()

        for log_file in log_files:
            analyzer.load_from_file(log_file)

    # Generate report
    if analyzer.entries:
        analyzer.print_report()
    else:
        print("No audit log entries found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
