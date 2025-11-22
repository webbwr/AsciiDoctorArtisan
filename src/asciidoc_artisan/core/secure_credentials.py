"""
Secure Credentials - OS keyring integration for AsciiDoc Artisan.

Provides secure credential storage using OS keyring (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux).
Phase 3 (v1.1) security feature ensures API keys never stored in plain text.

Security Features (FR-016): OS-level secure storage, no plain-text files, per-user isolation, automatic encryption, comprehensive audit logging.
"""

import getpass
import logging
from datetime import UTC, datetime

try:
    import keyring
    from keyring.errors import KeyringError

    KEYRING_AVAILABLE = True
except ImportError:  # pragma: no cover - Import-time exception, tested via subprocess
    KEYRING_AVAILABLE = False  # pragma: no cover

    # Create a dummy KeyringError class when keyring is not available
    class KeyringError(Exception):  # type: ignore[no-redef]  # pragma: no cover
        """Fallback KeyringError when keyring module is not available."""

        pass


logger = logging.getLogger(__name__)


class SecurityAudit:
    """Security audit logging for credential operations. Comprehensive logging with timestamp, user, action, service, status. Properties: No sensitive data logged, UTC timestamps, OS username attribution, action-based categorization, success/failure tracking. Format: SECURITY_AUDIT: timestamp=<ISO8601-UTC> user=<username> action=<action> service=<service> success=<bool>"""

    @staticmethod
    def log_event(action: str, service: str, success: bool = True) -> None:
        """Log security-relevant credential events (store_key, get_key, delete_key, check_key, etc.). Security: No API keys logged, failures don't prevent functionality, UTC timestamps."""
        try:
            timestamp = datetime.now(UTC).isoformat()
            user = getpass.getuser()

            logger.info(
                f"SECURITY_AUDIT: timestamp={timestamp} user={user} action={action} service={service} success={success}"
            )
        except Exception as e:
            # Never let audit logging break functionality
            try:
                logger.error(f"Audit logging failed: {e}")
            except Exception:
                # If even error logging fails, silently continue
                pass


class SecureCredentials:
    """Manages secure credential storage using OS keyring (Keychain, Credential Manager, Secret Service). Security: Credentials never stored in plain text, OS-level encryption, per-user isolation, automatic cleanup. Example: creds = SecureCredentials(); creds.store_api_key("anthropic", "sk-ant-..."); key = creds.get_api_key("anthropic"); creds.delete_api_key("anthropic")"""

    SERVICE_NAME = "AsciiDocArtisan"
    ANTHROPIC_KEY = "anthropic_api_key"

    def __init__(self) -> None:
        """Initialize SecureCredentials and verify keyring availability."""
        if not KEYRING_AVAILABLE:
            logger.warning("keyring library not available. Install with: pip install keyring")

    @staticmethod
    def is_available() -> bool:
        """Check if secure credential storage available. Returns True if keyring available and functional."""
        return KEYRING_AVAILABLE

    def store_api_key(self, service: str, api_key: str) -> bool:
        """Store API key securely in OS keyring. Returns True if successful, False otherwise. Security: OS encryption, current user only, no plain-text, audit logged."""
        # Log attempt
        SecurityAudit.log_event("store_key_attempt", service, success=True)

        if not KEYRING_AVAILABLE:
            logger.error("Cannot store API key: keyring not available")
            SecurityAudit.log_event("store_key", service, success=False)
            return False

        if not api_key or not api_key.strip():
            logger.error("Cannot store empty API key")
            SecurityAudit.log_event("store_key", service, success=False)
            return False

        try:
            username = f"{service}_key"
            keyring.set_password(self.SERVICE_NAME, username, api_key.strip())
            logger.info(f"Successfully stored API key for service: {service}")
            SecurityAudit.log_event("store_key", service, success=True)
            return True
        except KeyringError as e:
            logger.error(f"Failed to store API key for {service}: {e}")
            SecurityAudit.log_event("store_key", service, success=False)
            return False
        except Exception as e:
            logger.exception(f"Unexpected error storing API key for {service}: {e}")
            SecurityAudit.log_event("store_key", service, success=False)
            return False

    def get_api_key(self, service: str) -> str | None:
        """Retrieve API key from OS keyring. Returns key if found, None otherwise. Security: Retrieved from encrypted storage, requires OS authentication if locked, audit logged."""
        # Log retrieval attempt
        SecurityAudit.log_event("get_key_attempt", service, success=True)

        if not KEYRING_AVAILABLE:
            logger.error("Cannot retrieve API key: keyring not available")
            SecurityAudit.log_event("get_key", service, success=False)
            return None

        try:
            username = f"{service}_key"
            api_key: str | None = keyring.get_password(self.SERVICE_NAME, username)

            if api_key:
                logger.info(f"Successfully retrieved API key for service: {service}")
                SecurityAudit.log_event("get_key", service, success=True)
            else:
                logger.info(f"No API key found for service: {service}")
                SecurityAudit.log_event("get_key", service, success=False)

            return api_key
        except KeyringError as e:
            logger.error(f"Failed to retrieve API key for {service}: {e}")
            SecurityAudit.log_event("get_key", service, success=False)
            return None
        except Exception as e:
            logger.exception(f"Unexpected error retrieving API key for {service}: {e}")
            SecurityAudit.log_event("get_key", service, success=False)
            return None

    def delete_api_key(self, service: str) -> bool:
        """Delete API key from OS keyring. Returns True if successful, False otherwise. Security: Securely removes credential, no residual data, audit logged."""
        # Log deletion attempt
        SecurityAudit.log_event("delete_key_attempt", service, success=True)

        if not KEYRING_AVAILABLE:
            logger.error("Cannot delete API key: keyring not available")
            SecurityAudit.log_event("delete_key", service, success=False)
            return False

        try:
            username = f"{service}_key"
            keyring.delete_password(self.SERVICE_NAME, username)
            logger.info(f"Successfully deleted API key for service: {service}")
            SecurityAudit.log_event("delete_key", service, success=True)
            return True
        except KeyringError as e:
            # Key might not exist, which is fine
            logger.info(f"No API key to delete for {service}: {e}")
            SecurityAudit.log_event("delete_key", service, success=False)
            return False
        except Exception as e:
            logger.exception(f"Unexpected error deleting API key for {service}: {e}")
            SecurityAudit.log_event("delete_key", service, success=False)
            return False

    def has_api_key(self, service: str) -> bool:
        """Check if API key exists for service. Returns True if exists, False otherwise. Security: Audit logged."""
        # Log check attempt
        SecurityAudit.log_event("check_key_attempt", service, success=True)

        if not KEYRING_AVAILABLE:
            SecurityAudit.log_event("check_key", service, success=False)
            return False

        api_key = self.get_api_key(service)
        key_exists = api_key is not None and len(api_key.strip()) > 0

        # Log check result (note: get_api_key already logged its own events)
        SecurityAudit.log_event("check_key", service, success=key_exists)
        return key_exists

    # Convenience methods for Anthropic API key
    def store_anthropic_key(self, api_key: str) -> bool:
        """Store Anthropic API key securely (starts with 'sk-ant-'). Returns True if successful."""
        return self.store_api_key(self.ANTHROPIC_KEY, api_key)

    def get_anthropic_key(self) -> str | None:
        """Retrieve Anthropic API key. Returns key if found, None otherwise."""
        return self.get_api_key(self.ANTHROPIC_KEY)

    def delete_anthropic_key(self) -> bool:
        """Delete Anthropic API key. Returns True if successful."""
        return self.delete_api_key(self.ANTHROPIC_KEY)

    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key configured. Returns True if exists."""
        return self.has_api_key(self.ANTHROPIC_KEY)
