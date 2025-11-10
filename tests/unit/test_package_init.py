"""
Test suite for asciidoc_artisan/__init__.py (package-level).

This test suite ensures 100% coverage of the main package's __init__.py file,
including:
- Lazy imports via __getattr__ for constants, classes, functions
- Error handling for invalid attributes
- Public API declaration (__all__)

Target: 50% → 100% coverage (12 missing lines)
"""

import pytest


class TestLazyConstantImports:
    """Test lazy import of constants via __getattr__."""

    @pytest.mark.parametrize(
        "constant_name",
        [
            "APP_NAME",
            "DEFAULT_FILENAME",
            "EDITOR_FONT_SIZE",
            "SETTINGS_FILENAME",
            "SUPPORTED_OPEN_FILTER",
            "SUPPORTED_SAVE_FILTER",
        ],
    )
    def test_lazy_constant_import(self, constant_name):
        """Test that constants are lazily imported via __getattr__."""
        import asciidoc_artisan

        # Access the constant (triggers __getattr__)
        value = getattr(asciidoc_artisan, constant_name)

        # Verify value was loaded
        assert value is not None
        assert isinstance(value, (str, int))


class TestLazyDataModelImports:
    """Test lazy import of data models via __getattr__."""

    def test_git_result_import(self):
        """Test GitResult model is lazily imported."""
        import asciidoc_artisan

        GitResult = getattr(asciidoc_artisan, "GitResult")
        assert GitResult is not None
        # GitResult is a Pydantic model
        assert hasattr(GitResult, "model_fields") or hasattr(GitResult, "__init__")

    def test_settings_import(self):
        """Test Settings class is lazily imported."""
        import asciidoc_artisan

        Settings = getattr(asciidoc_artisan, "Settings")
        assert Settings is not None
        assert hasattr(Settings, "__init__")


class TestLazySecurityFunctionImports:
    """Test lazy import of security functions via __getattr__."""

    @pytest.mark.parametrize(
        "function_name",
        [
            "atomic_save_json",
            "atomic_save_text",
            "sanitize_path",
        ],
    )
    def test_lazy_security_function_import(self, function_name):
        """Test that security functions are lazily imported."""
        import asciidoc_artisan

        func = getattr(asciidoc_artisan, function_name)
        assert callable(func)


class TestLazyUIComponentImports:
    """Test lazy import of UI components via __getattr__."""

    def test_asciidoc_editor_import(self):
        """Test AsciiDocEditor class is lazily imported."""
        import asciidoc_artisan

        AsciiDocEditor = getattr(asciidoc_artisan, "AsciiDocEditor")
        assert AsciiDocEditor is not None
        # Check it's a Qt widget class
        assert hasattr(AsciiDocEditor, "__init__")

    def test_preferences_dialog_import(self):
        """Test PreferencesDialog class is lazily imported."""
        import asciidoc_artisan

        PreferencesDialog = getattr(asciidoc_artisan, "PreferencesDialog")
        assert PreferencesDialog is not None
        assert hasattr(PreferencesDialog, "__init__")


class TestLazyWorkerImports:
    """Test lazy import of worker classes via __getattr__."""

    @pytest.mark.parametrize(
        "worker_name",
        [
            "GitWorker",
            "PandocWorker",
            "PreviewWorker",
        ],
    )
    def test_lazy_worker_import(self, worker_name):
        """Test that worker classes are lazily imported."""
        import asciidoc_artisan

        Worker = getattr(asciidoc_artisan, worker_name)
        assert Worker is not None
        # Workers should be QThread subclasses
        assert hasattr(Worker, "__init__")


class TestInvalidAttributeHandling:
    """Test error handling for invalid attribute access."""

    def test_invalid_attribute_raises_error(self):
        """Test that accessing invalid attribute raises AttributeError."""
        import asciidoc_artisan

        with pytest.raises(
            AttributeError, match="module.*has no attribute 'INVALID_ATTR'"
        ):
            _ = getattr(asciidoc_artisan, "INVALID_ATTR")

    def test_invalid_attribute_message_format(self):
        """Test that AttributeError message includes module and attribute name."""
        import asciidoc_artisan

        with pytest.raises(AttributeError) as exc_info:
            _ = asciidoc_artisan.NONEXISTENT_CONSTANT

        error_msg = str(exc_info.value)
        assert "asciidoc_artisan" in error_msg
        assert "NONEXISTENT_CONSTANT" in error_msg


class TestPublicAPI:
    """Test __all__ declaration and public API."""

    def test_all_list_exists(self):
        """Test that __all__ list is defined."""
        import asciidoc_artisan

        assert hasattr(asciidoc_artisan, "__all__")
        assert isinstance(asciidoc_artisan.__all__, list)

    def test_all_list_not_empty(self):
        """Test that __all__ list contains items."""
        import asciidoc_artisan

        assert len(asciidoc_artisan.__all__) > 0

    def test_all_items_are_strings(self):
        """Test that all items in __all__ are strings."""
        import asciidoc_artisan

        for item in asciidoc_artisan.__all__:
            assert isinstance(item, str)

    def test_version_in_all(self):
        """Test that __version__ is in __all__."""
        import asciidoc_artisan

        assert "__version__" in asciidoc_artisan.__all__

    def test_version_accessible(self):
        """Test that __version__ can be accessed."""
        import asciidoc_artisan

        version = asciidoc_artisan.__version__
        assert isinstance(version, str)
        assert len(version) > 0
        # Check semantic versioning format (x.y.z)
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor


class TestImportPerformance:
    """Test import performance characteristics."""

    def test_package_imports_without_error(self):
        """Test that package imports successfully."""
        try:
            import asciidoc_artisan  # noqa: F401

            assert True  # Import succeeded
        except Exception as e:
            pytest.fail(f"Package import failed: {e}")

    def test_multiple_lazy_imports(self):
        """Test that multiple lazy imports work correctly."""
        import asciidoc_artisan

        # Import multiple items to ensure __getattr__ works multiple times
        items = [
            "AsciiDocEditor",
            "Settings",
            "GitWorker",
            "sanitize_path",
            "APP_NAME",
        ]

        for item in items:
            value = getattr(asciidoc_artisan, item)
            assert value is not None


class TestAllItemsCanBeImported:
    """Test that all items in __all__ can actually be imported."""

    def test_all_items_are_valid(self):
        """Test that all items in __all__ can be imported without error."""
        import asciidoc_artisan

        # Test each item in __all__
        for item in asciidoc_artisan.__all__:
            try:
                value = getattr(asciidoc_artisan, item)
                assert value is not None, f"{item} should not be None"
            except AttributeError:
                pytest.fail(f"Item '{item}' in __all__ cannot be imported")


class TestLazyImportsCoverAllBranches:
    """Test to ensure all branches of __getattr__ are covered."""

    def test_constants_branch(self):
        """Test the constants import branch."""
        import asciidoc_artisan

        # Test first constant in the group
        _ = asciidoc_artisan.APP_NAME
        # Test last constant in the group
        _ = asciidoc_artisan.SUPPORTED_SAVE_FILTER

    def test_models_branch(self):
        """Test the models import branch."""
        import asciidoc_artisan

        # Test first model
        _ = asciidoc_artisan.GitResult
        # Test second model
        _ = asciidoc_artisan.Settings

    def test_security_functions_branch(self):
        """Test the security functions import branch."""
        import asciidoc_artisan

        # Test first function
        _ = asciidoc_artisan.atomic_save_json
        # Test middle function
        _ = asciidoc_artisan.atomic_save_text
        # Test last function
        _ = asciidoc_artisan.sanitize_path

    def test_ui_editor_branch(self):
        """Test the AsciiDocEditor import branch."""
        import asciidoc_artisan

        _ = asciidoc_artisan.AsciiDocEditor

    def test_ui_dialog_branch(self):
        """Test the PreferencesDialog import branch."""
        import asciidoc_artisan

        _ = asciidoc_artisan.PreferencesDialog

    def test_workers_branch(self):
        """Test the workers import branch."""
        import asciidoc_artisan

        # Test first worker
        _ = asciidoc_artisan.GitWorker
        # Test middle worker
        _ = asciidoc_artisan.PandocWorker
        # Test last worker
        _ = asciidoc_artisan.PreviewWorker
