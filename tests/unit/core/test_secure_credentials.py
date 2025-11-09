"""
Tests for secure credential storage module.

Tests keyring-based API key storage with mocked keyring operations.
"""

from asciidoc_artisan.core.secure_credentials import SecureCredentials


class TestSecureCredentials:
    """Test SecureCredentials class."""

    def test_init_creates_credentials_manager(self):
        """Test SecureCredentials initialization."""
        creds = SecureCredentials()
        assert creds.SERVICE_NAME == "AsciiDocArtisan"
        assert creds.ANTHROPIC_KEY == "anthropic_api_key"

    def test_is_available_returns_bool(self):
        """Test checking if keyring is available."""
        result = SecureCredentials.is_available()
        assert isinstance(result, bool)

    def test_store_api_key_success(self, mocker):
        """Test storing API key when keyring is available."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("openai", "sk-test123")

        assert result is True
        mock_set.assert_called_once_with("AsciiDocArtisan", "openai_key", "sk-test123")

    def test_store_api_key_strips_whitespace(self, mocker):
        """Test storing API key strips whitespace."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("openai", "  sk-test123  ")

        assert result is True
        mock_set.assert_called_once_with("AsciiDocArtisan", "openai_key", "sk-test123")

    def test_store_api_key_empty_fails(self, mocker):
        """Test storing empty API key fails."""
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("openai", "")

        assert result is False

    def test_store_api_key_whitespace_only_fails(self, mocker):
        """Test storing whitespace-only API key fails."""
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("openai", "   ")

        assert result is False

    def test_store_api_key_keyring_unavailable(self, mocker):
        """Test storing API key when keyring unavailable."""
        mocker.patch(
            "asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", False
        )

        creds = SecureCredentials()
        result = creds.store_api_key("openai", "sk-test123")

        assert result is False

    def test_store_api_key_keyring_error(self, mocker):
        """Test storing API key when keyring raises error."""
        from keyring.errors import KeyringError

        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mock_set.side_effect = KeyringError("Keyring locked")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("openai", "sk-test123")

        assert result is False

    def test_get_api_key_success(self, mocker):
        """Test retrieving API key from keyring."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = "sk-test123"
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        api_key = creds.get_api_key("openai")

        assert api_key == "sk-test123"
        mock_get.assert_called_once_with("AsciiDocArtisan", "openai_key")

    def test_get_api_key_not_found(self, mocker):
        """Test retrieving non-existent API key."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = None
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        api_key = creds.get_api_key("nonexistent")

        assert api_key is None

    def test_get_api_key_keyring_unavailable(self, mocker):
        """Test retrieving API key when keyring unavailable."""
        mocker.patch(
            "asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", False
        )

        creds = SecureCredentials()
        api_key = creds.get_api_key("openai")

        assert api_key is None

    def test_get_api_key_keyring_error(self, mocker):
        """Test retrieving API key when keyring raises error."""
        from keyring.errors import KeyringError

        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.side_effect = KeyringError("Keyring locked")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        api_key = creds.get_api_key("openai")

        assert api_key is None

    def test_delete_api_key_success(self, mocker):
        """Test deleting API key from keyring."""
        mock_delete = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.delete_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.delete_api_key("openai")

        assert result is True
        mock_delete.assert_called_once_with("AsciiDocArtisan", "openai_key")

    def test_delete_api_key_keyring_unavailable(self, mocker):
        """Test deleting API key when keyring unavailable."""
        mocker.patch(
            "asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", False
        )

        creds = SecureCredentials()
        result = creds.delete_api_key("openai")

        assert result is False

    def test_delete_api_key_not_found(self, mocker):
        """Test deleting non-existent API key."""
        from keyring.errors import KeyringError

        mock_delete = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.delete_password")
        mock_delete.side_effect = KeyringError("Password not found")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.delete_api_key("nonexistent")

        # Should return False when key doesn't exist
        assert result is False

    def test_has_api_key_exists(self, mocker):
        """Test checking if API key exists."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = "sk-test123"
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        has_key = creds.has_api_key("openai")

        assert has_key is True

    def test_has_api_key_not_exists(self, mocker):
        """Test checking if API key exists when it doesn't."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = None
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        has_key = creds.has_api_key("nonexistent")

        assert has_key is False

    def test_has_api_key_empty_string(self, mocker):
        """Test checking if API key exists when it's empty."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = "   "
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        has_key = creds.has_api_key("openai")

        assert has_key is False

    def test_has_api_key_keyring_unavailable(self, mocker):
        """Test checking if API key exists when keyring unavailable."""
        mocker.patch(
            "asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", False
        )

        creds = SecureCredentials()
        has_key = creds.has_api_key("openai")

        assert has_key is False


class TestAnthropicConvenienceMethods:
    """Test Anthropic-specific convenience methods."""

    def test_store_anthropic_key(self, mocker):
        """Test storing Anthropic API key."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_anthropic_key("sk-ant-test123")

        assert result is True
        mock_set.assert_called_once_with(
            "AsciiDocArtisan", "anthropic_api_key_key", "sk-ant-test123"
        )

    def test_get_anthropic_key(self, mocker):
        """Test retrieving Anthropic API key."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = "sk-ant-test123"
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        api_key = creds.get_anthropic_key()

        assert api_key == "sk-ant-test123"

    def test_delete_anthropic_key(self, mocker):
        """Test deleting Anthropic API key."""
        mock_delete = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.delete_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.delete_anthropic_key()

        assert result is True

    def test_has_anthropic_key(self, mocker):
        """Test checking if Anthropic API key exists."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.return_value = "sk-ant-test123"
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        has_key = creds.has_anthropic_key()

        assert has_key is True


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_unicode_in_api_key(self, mocker):
        """Test storing API key with unicode characters."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("test", "测试🔑key")

        assert result is True
        mock_set.assert_called_once_with("AsciiDocArtisan", "test_key", "测试🔑key")

    def test_very_long_api_key(self, mocker):
        """Test storing very long API key."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        long_key = "sk-" + ("x" * 10000)
        creds = SecureCredentials()
        result = creds.store_api_key("test", long_key)

        assert result is True

    def test_special_characters_in_service_name(self, mocker):
        """Test service name with special characters."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("test/service:123", "sk-test")

        assert result is True

    def test_unexpected_exception_in_store(self, mocker):
        """Test handling unexpected exception in store."""
        mock_set = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.set_password")
        mock_set.side_effect = RuntimeError("Unexpected error")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.store_api_key("test", "sk-test")

        assert result is False

    def test_unexpected_exception_in_get(self, mocker):
        """Test handling unexpected exception in get."""
        mock_get = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.get_password")
        mock_get.side_effect = RuntimeError("Unexpected error")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        api_key = creds.get_api_key("test")

        assert api_key is None

    def test_unexpected_exception_in_delete(self, mocker):
        """Test handling unexpected exception in delete."""
        mock_delete = mocker.patch("asciidoc_artisan.core.secure_credentials.keyring.delete_password")
        mock_delete.side_effect = RuntimeError("Unexpected error")
        mocker.patch("asciidoc_artisan.core.secure_credentials.KEYRING_AVAILABLE", True)

        creds = SecureCredentials()
        result = creds.delete_api_key("test")

        assert result is False


class TestImportErrorHandling:
    """Test import-time error handling (lines 29-31).

    Note: Lines 29-31 are import-time exception handlers marked with
    `pragma: no cover` because they execute only when the module is first
    loaded and keyring is unavailable. They are tested indirectly via:
    - All tests that mock KEYRING_AVAILABLE=False
    - Subprocess test (if keyring truly unavailable)
    """

    def test_keyring_unavailable_behavior_documented(self):
        """Document that ImportError handling sets fallback behavior."""
        from asciidoc_artisan.core.secure_credentials import (
            KEYRING_AVAILABLE,
            KeyringError,
        )

        # This test documents the expected behavior when keyring import fails:
        # 1. KEYRING_AVAILABLE is set to False (handled by lines 29-31)
        # 2. KeyringError falls back to Exception (handled by line 31)
        #
        # The existing 29 tests already thoroughly cover the
        # KEYRING_AVAILABLE=False code paths, validating the fallback works.

        # If keyring is available (normal case)
        if KEYRING_AVAILABLE:
            assert KeyringError.__name__ == "KeyringError"
        # If keyring unavailable (import error occurred)
        else:  # pragma: no cover
            assert KEYRING_AVAILABLE is False
            assert KeyringError == Exception


class TestAuditLoggingFailure:
    """Test audit logging failure scenarios."""

    def test_audit_log_exception_handling(self, mocker):
        """Test double exception handling in audit logging (lines 84-90)."""
        from asciidoc_artisan.core.secure_credentials import SecurityAudit

        # Mock logger to raise exception during info logging
        mock_logger = mocker.patch("asciidoc_artisan.core.secure_credentials.logger")
        mock_logger.info.side_effect = RuntimeError("Logging system failure")
        mock_logger.error.side_effect = RuntimeError("Error logging also fails")

        # Should not raise exception, silently continue
        SecurityAudit.log_event("store_key", "test_service", True)

        # Verify both info and error were attempted
        assert mock_logger.info.called
        assert mock_logger.error.called

    def test_audit_log_getuser_exception(self, mocker):
        """Test audit logging when getuser() fails."""
        import getpass

        from asciidoc_artisan.core.secure_credentials import SecurityAudit

        # Mock getuser() to raise exception
        mocker.patch.object(getpass, "getuser", side_effect=OSError("No user"))

        # Mock logger
        mock_logger = mocker.patch("asciidoc_artisan.core.secure_credentials.logger")

        # Should not raise exception, should log error
        SecurityAudit.log_event("test", "test_service", True)

        # Should have called error due to exception
        assert mock_logger.error.called
