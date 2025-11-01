"""
Secure Credentials - OS keyring integration for AsciiDoc Artisan.

This module provides secure credential storage using the operating system's
keyring service (Keychain on macOS, Credential Manager on Windows,
Secret Service on Linux).

This is a Phase 3 (v1.1) security feature that ensures API keys and sensitive
data are never stored in plain text.

Security Features (FR-016):
- OS-level secure storage
- No plain-text credential files
- Per-user credential isolation
- Automatic encryption by OS keyring
- Comprehensive audit logging for forensic analysis
"""

import getpass
import logging
from datetime import datetime, timezone
from typing import Optional

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
    """Security audit logging for credential operations.

    This class provides comprehensive audit logging for all credential operations
    to enable forensic analysis and security monitoring. All events are logged
    with consistent format including timestamp, user, action, service, and status.

    Security Properties:
    - No sensitive data (API keys) logged
    - UTC timestamps for consistency
    - User attribution via OS username
    - Action-based categorization
    - Success/failure tracking

    Log Format:
        SECURITY_AUDIT: timestamp=<ISO8601-UTC> user=<username> action=<action> service=<service> success=<bool>

    Example:
        >>> SecurityAudit.log_event("store_key", "anthropic", success=True)
        # Logs: SECURITY_AUDIT: timestamp=2025-10-29T12:34:56.789Z user=webbp action=store_key service=anthropic success=True
    """

    @staticmethod
    def log_event(action: str, service: str, success: bool = True) -> None:
        """Log security-relevant credential events.

        Args:
            action: Action performed (store_key, get_key, delete_key, check_key, etc.)
            service: Service identifier (e.g., 'anthropic', 'openai')
            success: Whether the operation succeeded

        Security:
            - No API keys or sensitive data are logged
            - Failures are logged but don't prevent functionality
            - UTC timestamps for timezone-independent forensics
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            user = getpass.getuser()

            logger.info(
                f"SECURITY_AUDIT: "
                f"timestamp={timestamp} "
                f"user={user} "
                f"action={action} "
                f"service={service} "
                f"success={success}"
            )
        except Exception as e:
            # Never let audit logging break functionality
            try:
                logger.error(f"Audit logging failed: {e}")
            except Exception:
                # If even error logging fails, silently continue
                pass


class SecureCredentials:
    """Manages secure credential storage using OS keyring.

    This class provides a secure interface for storing and retrieving
    sensitive credentials like API keys. It uses the system keyring
    (Keychain, Credential Manager, Secret Service) for encryption.

    Security Properties:
    - Credentials never stored in plain text
    - OS-level encryption
    - Per-user isolation
    - Automatic cleanup on delete

    Example:
        >>> creds = SecureCredentials()
        >>> creds.store_api_key("anthropic", "sk-ant-...")
        >>> key = creds.get_api_key("anthropic")
        >>> creds.delete_api_key("anthropic")
    """

    SERVICE_NAME = "AsciiDocArtisan"
    ANTHROPIC_KEY = "anthropic_api_key"

    def __init__(self) -> None:
        """Initialize SecureCredentials and verify keyring availability."""
        if not KEYRING_AVAILABLE:
            logger.warning(
                "keyring library not available. Install with: pip install keyring"
            )

    @staticmethod
    def is_available() -> bool:
        """Check if secure credential storage is available.

        Returns:
            True if keyring is available and functional
        """
        return KEYRING_AVAILABLE

    def store_api_key(self, service: str, api_key: str) -> bool:
        """Store an API key securely in the OS keyring.

        Args:
            service: Service identifier (e.g., 'anthropic', 'openai')
            api_key: The API key to store securely

        Returns:
            True if successfully stored, False otherwise

        Security:
            - Key is encrypted by OS keyring
            - Only accessible to current user
            - No plain-text storage
            - All operations are audit logged
        """
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

    def get_api_key(self, service: str) -> Optional[str]:
        """Retrieve an API key from the OS keyring.

        Args:
            service: Service identifier (e.g., 'anthropic', 'openai')

        Returns:
            The API key if found, None otherwise

        Security:
            - Key retrieved from encrypted storage
            - Requires OS authentication if keyring is locked
            - All access attempts are audit logged
        """
        # Log retrieval attempt
        SecurityAudit.log_event("get_key_attempt", service, success=True)

        if not KEYRING_AVAILABLE:
            logger.error("Cannot retrieve API key: keyring not available")
            SecurityAudit.log_event("get_key", service, success=False)
            return None

        try:
            username = f"{service}_key"
            api_key: Optional[str] = keyring.get_password(self.SERVICE_NAME, username)

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
        """Delete an API key from the OS keyring.

        Args:
            service: Service identifier (e.g., 'anthropic', 'openai')

        Returns:
            True if successfully deleted, False otherwise

        Security:
            - Securely removes credential from OS keyring
            - No residual data left in storage
            - All deletion attempts are audit logged
        """
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
        """Check if an API key exists for a service.

        Args:
            service: Service identifier (e.g., 'anthropic', 'openai')

        Returns:
            True if key exists, False otherwise

        Security:
            - All existence checks are audit logged
        """
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
        """Store Anthropic API key securely.

        Args:
            api_key: Anthropic API key (starts with 'sk-ant-')

        Returns:
            True if successfully stored
        """
        return self.store_api_key(self.ANTHROPIC_KEY, api_key)

    def get_anthropic_key(self) -> Optional[str]:
        """Retrieve Anthropic API key.

        Returns:
            API key if found, None otherwise
        """
        return self.get_api_key(self.ANTHROPIC_KEY)

    def delete_anthropic_key(self) -> bool:
        """Delete Anthropic API key.

        Returns:
            True if successfully deleted
        """
        return self.delete_api_key(self.ANTHROPIC_KEY)

    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is configured.

        Returns:
            True if key exists
        """
        return self.has_api_key(self.ANTHROPIC_KEY)
