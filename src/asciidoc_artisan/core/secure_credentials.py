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
"""

import logging
from typing import Optional

try:
    import keyring
    from keyring.errors import KeyringError

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    KeyringError = Exception  # type: ignore

logger = logging.getLogger(__name__)


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
        """
        if not KEYRING_AVAILABLE:
            logger.error("Cannot store API key: keyring not available")
            return False

        if not api_key or not api_key.strip():
            logger.error("Cannot store empty API key")
            return False

        try:
            username = f"{service}_key"
            keyring.set_password(self.SERVICE_NAME, username, api_key.strip())
            logger.info(f"Successfully stored API key for service: {service}")
            return True
        except KeyringError as e:
            logger.error(f"Failed to store API key for {service}: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error storing API key for {service}: {e}")
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
        """
        if not KEYRING_AVAILABLE:
            logger.error("Cannot retrieve API key: keyring not available")
            return None

        try:
            username = f"{service}_key"
            api_key = keyring.get_password(self.SERVICE_NAME, username)

            if api_key:
                logger.info(f"Successfully retrieved API key for service: {service}")
            else:
                logger.info(f"No API key found for service: {service}")

            return api_key
        except KeyringError as e:
            logger.error(f"Failed to retrieve API key for {service}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error retrieving API key for {service}: {e}")
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
        """
        if not KEYRING_AVAILABLE:
            logger.error("Cannot delete API key: keyring not available")
            return False

        try:
            username = f"{service}_key"
            keyring.delete_password(self.SERVICE_NAME, username)
            logger.info(f"Successfully deleted API key for service: {service}")
            return True
        except KeyringError as e:
            # Key might not exist, which is fine
            logger.info(f"No API key to delete for {service}: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error deleting API key for {service}: {e}")
            return False

    def has_api_key(self, service: str) -> bool:
        """Check if an API key exists for a service.

        Args:
            service: Service identifier (e.g., 'anthropic', 'openai')

        Returns:
            True if key exists, False otherwise
        """
        if not KEYRING_AVAILABLE:
            return False

        api_key = self.get_api_key(service)
        return api_key is not None and len(api_key.strip()) > 0

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
