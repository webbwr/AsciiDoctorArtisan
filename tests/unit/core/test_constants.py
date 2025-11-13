"""
Tests for core.constants module.

Tests all constant definitions and ensures they have expected values.
"""

from asciidoc_artisan.core import constants


class TestConstants:
    """Test suite for application constants."""

    def test_app_name(self):
        """Test that APP_NAME is defined and is a string."""
        assert hasattr(constants, "APP_NAME")
        assert isinstance(constants.APP_NAME, str)
        assert len(constants.APP_NAME) > 0

    def test_app_version(self):
        """Test that APP_VERSION is defined and is a string."""
        assert hasattr(constants, "APP_VERSION")
        assert isinstance(constants.APP_VERSION, str)
        assert len(constants.APP_VERSION) > 0

    def test_supported_formats(self):
        """Test that supported file format filters are defined."""
        assert hasattr(constants, "SUPPORTED_OPEN_FILTER")
        assert isinstance(constants.SUPPORTED_OPEN_FILTER, str)
        # Should contain AsciiDoc format
        assert "adoc" in constants.SUPPORTED_OPEN_FILTER.lower()

    def test_default_filename(self):
        """Test that a default filename is defined."""
        assert hasattr(constants, "DEFAULT_FILENAME")
        assert isinstance(constants.DEFAULT_FILENAME, str)
        assert constants.DEFAULT_FILENAME.endswith(".adoc")

    def test_cache_settings(self):
        """Test that cache-related constants are defined."""
        # Check for cache size or similar settings
        cache_attrs = [attr for attr in dir(constants) if "CACHE" in attr.upper()]
        assert len(cache_attrs) > 0, "Should have cache-related constants"

    def test_timeout_settings(self):
        """Test that timeout constants are defined and reasonable."""
        timeout_attrs = [attr for attr in dir(constants) if "TIMEOUT" in attr.upper()]
        # If timeouts exist, they should be positive numbers
        for attr in timeout_attrs:
            value = getattr(constants, attr)
            if isinstance(value, (int, float)):
                assert value > 0, f"{attr} should be positive"

    def test_file_extensions(self):
        """Test that file extension constants are defined."""
        ext_attrs = [
            attr
            for attr in dir(constants)
            if "EXT" in attr.upper() or "EXTENSION" in attr.upper()
        ]
        # Should have at least one file extension defined
        assert len(ext_attrs) > 0, "Should have file extension constants"

    def test_no_private_constants_exposed(self):
        """Test that only public constants are exposed."""
        # Constants should not start with underscore (private)
        public_attrs = [
            attr
            for attr in dir(constants)
            if not attr.startswith("_") and attr.isupper()
        ]
        assert len(public_attrs) > 0, "Should have public constants"

    def test_constants_are_immutable_types(self):
        """Test that constants use immutable types where appropriate."""
        for attr in dir(constants):
            if attr.isupper() and not attr.startswith("_"):
                value = getattr(constants, attr)
                # Constants should generally be immutable types
                # (str, int, float, tuple, frozenset, etc.)
                assert isinstance(
                    value, (str, int, float, tuple, frozenset, bool, type(None))
                ), f"{attr} should be an immutable type, got {type(value)}"

    def test_all_constants_have_docstrings(self):
        """Test that the constants module has documentation."""
        assert constants.__doc__ is not None
        assert len(constants.__doc__.strip()) > 0

    def test_constants_module_attributes_exist(self):
        """Test that expected constant categories exist."""
        # The module should have __file__ attribute
        assert hasattr(constants, "__file__")
        # Should have __name__
        assert hasattr(constants, "__name__")
        assert constants.__name__ == "asciidoc_artisan.core.constants"

    def test_pypandoc_import_error_handling(self):
        """Test handling when pypandoc is not available (lines 112-113)."""
        import importlib
        import sys
        from unittest.mock import patch

        # Save original modules
        original_pypandoc = sys.modules.get("pypandoc")
        original_constants = sys.modules.get("asciidoc_artisan.core.constants")

        try:
            # Remove modules
            if "pypandoc" in sys.modules:
                del sys.modules["pypandoc"]
            if "asciidoc_artisan.core.constants" in sys.modules:
                del sys.modules["asciidoc_artisan.core.constants"]

            # Mock pypandoc import to raise ImportError
            import builtins

            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "pypandoc":
                    raise ImportError("Mock pypandoc not available")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                # Reload to trigger the import error path
                import asciidoc_artisan.core.constants as c

                importlib.reload(c)

                # Reset the lazy check cache
                c._pypandoc_checked = False
                c._pypandoc_available = False

                # is_pandoc_available() should return False when pypandoc is not available
                assert c.is_pandoc_available() is False

        finally:
            # Restore
            try:
                if original_pypandoc is not None:
                    sys.modules["pypandoc"] = original_pypandoc
                else:
                    if "pypandoc" in sys.modules:
                        del sys.modules["pypandoc"]

                if original_constants is not None:
                    sys.modules["asciidoc_artisan.core.constants"] = original_constants

                # Reload back to normal
                if "asciidoc_artisan.core.constants" in sys.modules:
                    import asciidoc_artisan.core.constants

                    importlib.reload(asciidoc_artisan.core.constants)
            except (ImportError, KeyError):
                pass

    def test_pypandoc_available_success_path(self):
        """Test when pypandoc IS available (line 124)."""
        import importlib

        # Reload constants to reset the cache
        importlib.reload(constants)

        # Reset the lazy check to force re-evaluation
        constants._pypandoc_checked = False
        constants._pypandoc_available = False

        # Call is_pandoc_available() which should check for pypandoc
        # This will hit line 124 if pypandoc is actually installed
        result = constants.is_pandoc_available()

        # Result depends on whether pypandoc is actually installed
        # but calling the function covers the code path
        assert isinstance(result, bool)

        # Call again to test the cached path
        result2 = constants.is_pandoc_available()
        assert result == result2  # Should be consistent

    def test_get_pandoc_available_function(self):
        """Test _get_pandoc_available function (line 137)."""
        # This is a wrapper around is_pandoc_available()
        result = constants._get_pandoc_available()

        # Should return a boolean
        assert isinstance(result, bool)

        # Should match is_pandoc_available()
        assert result == constants.is_pandoc_available()
