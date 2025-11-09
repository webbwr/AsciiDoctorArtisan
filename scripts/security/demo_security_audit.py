#!/usr/bin/env python3
"""
Security Audit Logging Demonstration Script

This script demonstrates the comprehensive audit logging system for credential operations.
Run this script to see example audit log outputs for all operations.

Usage:
    python scripts/demo_security_audit.py
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from asciidoc_artisan.core.secure_credentials import SecureCredentials


def setup_logging():
    """Configure logging to show audit entries clearly."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def print_section(title):
    """Print a section header."""
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print()


def demo_store_key(creds):
    """Demonstrate storing an API key."""
    print_section("1. STORING API KEY")
    success = creds.store_api_key("demo_service", "demo-api-key-12345")
    print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")


def demo_get_key(creds):
    """Demonstrate retrieving an API key."""
    print_section("2. RETRIEVING API KEY")
    key = creds.get_api_key("demo_service")
    print(f"Result: {'✓ Found key' if key else '✗ No key found'}")


def demo_check_key(creds):
    """Demonstrate checking if key exists."""
    print_section("3. CHECKING KEY EXISTS")
    exists = creds.has_api_key("demo_service")
    print(f"Result: {'✓ Key exists' if exists else '✗ Key does not exist'}")


def demo_delete_key(creds):
    """Demonstrate deleting an API key."""
    print_section("4. DELETING API KEY")
    deleted = creds.delete_api_key("demo_service")
    print(f"Result: {'✓ DELETED' if deleted else '✗ DELETE FAILED'}")


def demo_verify_deletion(creds):
    """Verify the key was deleted."""
    print_section("5. VERIFYING DELETION")
    exists = creds.has_api_key("demo_service")
    print(
        f"Result: {'✗ Key still exists (ERROR)' if exists else '✓ Key successfully removed'}"
    )


def demo_nonexistent_key(creds):
    """Demonstrate attempting to retrieve non-existent key."""
    print_section("6. RETRIEVING NON-EXISTENT KEY")
    key = creds.get_api_key("nonexistent_service")
    print(f"Result: {'✗ Found key (ERROR)' if key else '✓ Key not found (expected)'}")


def demo_anthropic_methods(creds):
    """Demonstrate Anthropic convenience methods."""
    print_section("7. ANTHROPIC CONVENIENCE METHODS")

    print("Storing Anthropic key...")
    creds.store_anthropic_key("sk-ant-demo-key-12345")

    print("Checking Anthropic key...")
    has_key = creds.has_anthropic_key()
    print(f"  {'✓ Key exists' if has_key else '✗ No key found'}")

    print("Deleting Anthropic key...")
    creds.delete_anthropic_key()
    print("  ✓ Deleted")


def print_summary():
    """Print summary information."""
    print()
    print("=" * 80)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Review the log output above to see SECURITY_AUDIT entries.")
    print()
    print("Each operation generates audit logs with the following format:")
    print("  SECURITY_AUDIT: timestamp=<ISO8601-UTC> user=<username> \\")
    print("                  action=<action> service=<service> success=<bool>")
    print()
    print("Audit logs are written to application logs for forensic analysis.")
    print()
    print("For more information, see: docs/SECURITY_AUDIT_GUIDE.md")
    print("To query logs, use: scripts/query_security_audit.sh")
    print()


def main():
    """Run the demonstration."""
    setup_logging()

    print()
    print("=" * 80)
    print("  SECURITY AUDIT LOGGING DEMONSTRATION")
    print("=" * 80)

    # Create credentials manager
    creds = SecureCredentials()

    # Check if keyring is available
    if not SecureCredentials.is_available():
        print()
        print("⚠ WARNING: Keyring not available.")
        print("  Audit logs will show failures, which is expected.")
        print("  Install keyring with: pip install keyring")

    # Run demonstrations
    demo_store_key(creds)
    demo_get_key(creds)
    demo_check_key(creds)
    demo_delete_key(creds)
    demo_verify_deletion(creds)
    demo_nonexistent_key(creds)
    demo_anthropic_methods(creds)

    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
