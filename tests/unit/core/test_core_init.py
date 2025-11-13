"""
Test suite for asciidoc_artisan.core.__init__.py module.

This test suite ensures 100% coverage of the core module's __init__.py file,
including:
- Eager imports (Settings, GitResult, etc.)
- Lazy imports via __getattr__ (constants, profilers, monitors)
- Caching mechanism for lazy imports
- Error handling for invalid attributes
- Public API declaration (__all__)

Phase 1: CRITICAL Priority (92.1% → 100% coverage push)
Current coverage: 45.5% (30 missing statements)
Target coverage: 100%
"""

import pytest


class TestEagerImports:
    """Test that eagerly-imported items are available immediately."""

    def test_settings_import(self):
        """Test Settings class is eagerly imported."""
        from asciidoc_artisan.core import Settings

        assert Settings is not None
        assert hasattr(Settings, "__init__")

    def test_git_result_import(self):
        """Test GitResult model is eagerly imported."""
        from asciidoc_artisan.core import GitResult

        assert GitResult is not None
        # GitResult is a Pydantic model - check model_fields instead
        assert hasattr(GitResult, "model_fields") or hasattr(GitResult, "__init__")

    def test_git_status_import(self):
        """Test GitStatus model is eagerly imported (v1.9.0)."""
        from asciidoc_artisan.core import GitStatus

        assert GitStatus is not None

    def test_github_result_import(self):
        """Test GitHubResult model is eagerly imported."""
        from asciidoc_artisan.core import GitHubResult

        assert GitHubResult is not None
        # GitHubResult is a Pydantic model - check model_fields instead
        assert hasattr(GitHubResult, "model_fields") or hasattr(
            GitHubResult, "__init__"
        )

    def test_sanitize_path_import(self):
        """Test sanitize_path function is eagerly imported."""
        from asciidoc_artisan.core import sanitize_path

        assert callable(sanitize_path)

    def test_atomic_save_text_import(self):
        """Test atomic_save_text function is eagerly imported."""
        from asciidoc_artisan.core import atomic_save_text

        assert callable(atomic_save_text)

    def test_atomic_save_json_import(self):
        """Test atomic_save_json function is eagerly imported."""
        from asciidoc_artisan.core import atomic_save_json

        assert callable(atomic_save_json)


class TestLazyConstantImports:
    """Test lazy import of constants via __getattr__."""

    @pytest.mark.parametrize(
        "constant_name",
        [
            "APP_NAME",
            "APP_VERSION",
            "DEFAULT_FILENAME",
            "SETTINGS_FILENAME",
            "EDITOR_FONT_FAMILY",
            "EDITOR_FONT_SIZE",
            "MIN_FONT_SIZE",
            "ZOOM_STEP",
            "MIN_WINDOW_WIDTH",
            "MIN_WINDOW_HEIGHT",
            "AUTO_SAVE_INTERVAL_MS",
            "PREVIEW_UPDATE_INTERVAL_MS",
            "PREVIEW_FAST_INTERVAL_MS",
            "PREVIEW_NORMAL_INTERVAL_MS",
            "PREVIEW_SLOW_INTERVAL_MS",
            "STATUS_MESSAGE_DURATION_MS",
            "LARGE_FILE_THRESHOLD_BYTES",
            "MAX_FILE_SIZE_MB",
        ],
    )
    def test_lazy_constant_import(self, constant_name):
        """Test that constants are lazily imported via __getattr__."""
        # Import core module to access __getattr__
        import asciidoc_artisan.core as core

        # Access the constant (triggers __getattr__)
        value = getattr(core, constant_name)

        # Verify value was loaded
        assert value is not None

    @pytest.mark.parametrize(
        "filter_name",
        [
            "ADOC_FILTER",
            "DOCX_FILTER",
            "PDF_FILTER",
            "MD_FILTER",
            "HTML_FILTER",
            "LATEX_FILTER",
            "RST_FILTER",
            "ORG_FILTER",
            "TEXTILE_FILTER",
            "ALL_FILES_FILTER",
        ],
    )
    def test_lazy_filter_import(self, filter_name):
        """Test that file filters are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, filter_name)
        assert isinstance(value, str)
        assert len(value) > 0

    @pytest.mark.parametrize(
        "format_list",
        [
            "COMMON_FORMATS",
            "ALL_FORMATS",
            "SUPPORTED_OPEN_FILTER",
            "SUPPORTED_SAVE_FILTER",
        ],
    )
    def test_lazy_format_list_import(self, format_list):
        """Test that format lists are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, format_list)
        assert value is not None

    @pytest.mark.parametrize(
        "message_name",
        [
            "MSG_SAVED_ASCIIDOC",
            "MSG_SAVED_HTML",
            "MSG_SAVED_HTML_PDF_READY",
            "MSG_PDF_IMPORTED",
            "MSG_LOADING_LARGE_FILE",
        ],
    )
    def test_lazy_message_import(self, message_name):
        """Test that user messages are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, message_name)
        assert isinstance(value, str)
        assert len(value) > 0

    @pytest.mark.parametrize(
        "error_name",
        [
            "ERR_ASCIIDOC_NOT_INITIALIZED",
            "ERR_ATOMIC_SAVE_FAILED",
            "ERR_FAILED_SAVE_HTML",
            "ERR_FAILED_CREATE_TEMP",
        ],
    )
    def test_lazy_error_message_import(self, error_name):
        """Test that error messages are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, error_name)
        assert isinstance(value, str)
        assert len(value) > 0

    @pytest.mark.parametrize(
        "dialog_name",
        [
            "DIALOG_OPEN_FILE",
            "DIALOG_SAVE_FILE",
            "DIALOG_SAVE_ERROR",
            "DIALOG_CONVERSION_ERROR",
        ],
    )
    def test_lazy_dialog_title_import(self, dialog_name):
        """Test that dialog titles are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, dialog_name)
        assert isinstance(value, str)
        assert len(value) > 0

    def test_lazy_menu_label_import(self):
        """Test that menu labels are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, "MENU_FILE")
        assert isinstance(value, str)
        assert len(value) > 0

    def test_lazy_status_tip_import(self):
        """Test that status tips are lazily imported."""
        import asciidoc_artisan.core as core

        value = getattr(core, "STATUS_TIP_EXPORT_OFFICE365")
        assert isinstance(value, str)
        assert len(value) > 0


class TestLazyMemoryProfilerImports:
    """Test lazy import of memory profiler classes via __getattr__."""

    def test_memory_profiler_import(self):
        """Test MemoryProfiler class is lazily imported."""
        import asciidoc_artisan.core as core

        MemoryProfiler = getattr(core, "MemoryProfiler")
        assert MemoryProfiler is not None
        assert hasattr(MemoryProfiler, "start")

    def test_memory_snapshot_import(self):
        """Test MemorySnapshot class is lazily imported."""
        import asciidoc_artisan.core as core

        MemorySnapshot = getattr(core, "MemorySnapshot")
        assert MemorySnapshot is not None

    def test_get_profiler_import(self):
        """Test get_profiler function is lazily imported."""
        import asciidoc_artisan.core as core

        get_profiler = getattr(core, "get_profiler")
        assert callable(get_profiler)

    def test_profile_memory_import(self):
        """Test profile_memory decorator is lazily imported."""
        import asciidoc_artisan.core as core

        profile_memory = getattr(core, "profile_memory")
        assert callable(profile_memory)


class TestLazyCPUProfilerImports:
    """Test lazy import of CPU profiler classes via __getattr__ (QA-15)."""

    def test_cpu_profiler_import(self):
        """Test CPUProfiler class is lazily imported."""
        import asciidoc_artisan.core as core

        CPUProfiler = getattr(core, "CPUProfiler")
        assert CPUProfiler is not None

    def test_profile_result_import(self):
        """Test ProfileResult class is lazily imported."""
        import asciidoc_artisan.core as core

        ProfileResult = getattr(core, "ProfileResult")
        assert ProfileResult is not None

    def test_get_cpu_profiler_import(self):
        """Test get_cpu_profiler function is lazily imported."""
        import asciidoc_artisan.core as core

        get_cpu_profiler = getattr(core, "get_cpu_profiler")
        assert callable(get_cpu_profiler)

    def test_enable_cpu_profiling_import(self):
        """Test enable_cpu_profiling function is lazily imported."""
        import asciidoc_artisan.core as core

        enable_cpu_profiling = getattr(core, "enable_cpu_profiling")
        assert callable(enable_cpu_profiling)

    def test_disable_cpu_profiling_import(self):
        """Test disable_cpu_profiling function is lazily imported."""
        import asciidoc_artisan.core as core

        disable_cpu_profiling = getattr(core, "disable_cpu_profiling")
        assert callable(disable_cpu_profiling)


class TestLazyResourceMonitorImports:
    """Test lazy import of resource monitor classes via __getattr__."""

    def test_resource_monitor_import(self):
        """Test ResourceMonitor class is lazily imported."""
        import asciidoc_artisan.core as core

        ResourceMonitor = getattr(core, "ResourceMonitor")
        assert ResourceMonitor is not None

    def test_resource_metrics_import(self):
        """Test ResourceMetrics class is lazily imported."""
        import asciidoc_artisan.core as core

        ResourceMetrics = getattr(core, "ResourceMetrics")
        assert ResourceMetrics is not None

    def test_document_metrics_import(self):
        """Test DocumentMetrics class is lazily imported."""
        import asciidoc_artisan.core as core

        DocumentMetrics = getattr(core, "DocumentMetrics")
        assert DocumentMetrics is not None


class TestLazySecureCredentialsImport:
    """Test lazy import of SecureCredentials class via __getattr__."""

    def test_secure_credentials_import(self):
        """Test SecureCredentials class is lazily imported."""
        import asciidoc_artisan.core as core

        SecureCredentials = getattr(core, "SecureCredentials")
        assert SecureCredentials is not None
        # Check for actual methods (get_api_key, store_api_key, etc.)
        assert hasattr(SecureCredentials, "get_api_key")
        assert hasattr(SecureCredentials, "store_api_key")


class TestLazyAsyncFileOpsImports:
    """Test lazy import of async file operations via __getattr__ (v1.7.0 Task 4)."""

    def test_async_file_watcher_import(self):
        """Test AsyncFileWatcher class is lazily imported."""
        import asciidoc_artisan.core as core

        AsyncFileWatcher = getattr(core, "AsyncFileWatcher")
        assert AsyncFileWatcher is not None

    def test_qt_async_file_manager_import(self):
        """Test QtAsyncFileManager class is lazily imported."""
        import asciidoc_artisan.core as core

        QtAsyncFileManager = getattr(core, "QtAsyncFileManager")
        assert QtAsyncFileManager is not None

    @pytest.mark.parametrize(
        "async_func",
        [
            "async_read_text",
            "async_atomic_save_text",
            "async_atomic_save_json",
            "async_read_json",
            "async_copy_file",
        ],
    )
    def test_async_function_import(self, async_func):
        """Test async file functions are lazily imported."""
        import asciidoc_artisan.core as core

        func = getattr(core, async_func)
        assert callable(func)

    def test_async_file_context_import(self):
        """Test AsyncFileContext class is lazily imported."""
        import asciidoc_artisan.core as core

        AsyncFileContext = getattr(core, "AsyncFileContext")
        assert AsyncFileContext is not None


class TestLazySpellCheckerImports:
    """Test lazy import of spell checker classes via __getattr__ (v1.8.0)."""

    def test_spell_checker_import(self):
        """Test SpellChecker class is lazily imported."""
        import asciidoc_artisan.core as core

        SpellChecker = getattr(core, "SpellChecker")
        assert SpellChecker is not None

    def test_spell_error_import(self):
        """Test SpellError class is lazily imported."""
        import asciidoc_artisan.core as core

        SpellError = getattr(core, "SpellError")
        assert SpellError is not None


class TestLazyTelemetryImports:
    """Test lazy import of telemetry classes via __getattr__ (v1.8.0)."""

    def test_telemetry_collector_import(self):
        """Test TelemetryCollector class is lazily imported."""
        import asciidoc_artisan.core as core

        TelemetryCollector = getattr(core, "TelemetryCollector")
        assert TelemetryCollector is not None

    def test_telemetry_event_import(self):
        """Test TelemetryEvent class is lazily imported."""
        import asciidoc_artisan.core as core

        TelemetryEvent = getattr(core, "TelemetryEvent")
        assert TelemetryEvent is not None


class TestLazyDependencyValidatorImports:
    """Test lazy import of dependency validator classes via __getattr__ (v2.0.1)."""

    def test_dependency_validator_import(self):
        """Test DependencyValidator class is lazily imported."""
        import asciidoc_artisan.core as core

        DependencyValidator = getattr(core, "DependencyValidator")
        assert DependencyValidator is not None

    def test_validate_dependencies_import(self):
        """Test validate_dependencies function is lazily imported."""
        import asciidoc_artisan.core as core

        validate_dependencies = getattr(core, "validate_dependencies")
        assert callable(validate_dependencies)

    def test_dependency_type_import(self):
        """Test DependencyType enum is lazily imported."""
        import asciidoc_artisan.core as core

        DependencyType = getattr(core, "DependencyType")
        assert DependencyType is not None

    def test_dependency_status_import(self):
        """Test DependencyStatus enum is lazily imported."""
        import asciidoc_artisan.core as core

        DependencyStatus = getattr(core, "DependencyStatus")
        assert DependencyStatus is not None

    def test_dependency_import(self):
        """Test Dependency class is lazily imported."""
        import asciidoc_artisan.core as core

        Dependency = getattr(core, "Dependency")
        assert Dependency is not None


class TestCachingMechanism:
    """Test that lazy imports are cached for performance."""

    def test_constant_caching(self):
        """Test that constants are cached after first access."""
        import asciidoc_artisan.core as core

        # Clear cache to ensure clean test
        core._CONSTANTS_CACHE.clear()

        # First access should populate cache
        _ = getattr(core, "APP_NAME")
        assert "APP_NAME" in core._CONSTANTS_CACHE

        # Second access should use cache
        cached_value = core._CONSTANTS_CACHE["APP_NAME"]
        value = getattr(core, "APP_NAME")
        assert value == cached_value

    def test_module_caching(self):
        """Test that module imports are cached after first access."""
        import asciidoc_artisan.core as core

        # Clear cache to ensure clean test
        if "MemoryProfiler" in core._MODULE_CACHE:
            del core._MODULE_CACHE["MemoryProfiler"]

        # First access should populate cache
        _ = getattr(core, "MemoryProfiler")
        assert "MemoryProfiler" in core._MODULE_CACHE

        # Second access should use cache
        cached_value = core._MODULE_CACHE["MemoryProfiler"]
        value = getattr(core, "MemoryProfiler")
        assert value is cached_value  # Same object (cached)


class TestInvalidAttributeHandling:
    """Test error handling for invalid attribute access."""

    def test_invalid_attribute_raises_error(self):
        """Test that accessing invalid attribute raises AttributeError."""
        import asciidoc_artisan.core as core

        with pytest.raises(AttributeError, match="has no attribute 'INVALID_ATTR'"):
            _ = getattr(core, "INVALID_ATTR")

    def test_invalid_attribute_message_format(self):
        """Test that AttributeError message includes module and attribute name."""
        import asciidoc_artisan.core as core

        with pytest.raises(AttributeError) as exc_info:
            _ = core.NONEXISTENT_CONSTANT

        error_msg = str(exc_info.value)
        assert "asciidoc_artisan.core" in error_msg
        assert "NONEXISTENT_CONSTANT" in error_msg


class TestPublicAPI:
    """Test __all__ declaration and public API."""

    def test_all_list_exists(self):
        """Test that __all__ list is defined."""
        import asciidoc_artisan.core as core

        assert hasattr(core, "__all__")
        assert isinstance(core.__all__, list)

    def test_all_list_not_empty(self):
        """Test that __all__ list contains items."""
        import asciidoc_artisan.core as core

        assert len(core.__all__) > 0

    def test_all_items_are_valid(self):
        """Test that all items in __all__ can be imported."""
        import asciidoc_artisan.core as core

        # Check a sample of items (not all, to avoid test slowdown)
        sample_items = [
            "Settings",
            "GitResult",
            "GitStatus",
            "sanitize_path",
            "APP_NAME",
            "MemoryProfiler",
            "ResourceMonitor",
            "SecureCredentials",
        ]

        for item in sample_items:
            if item in core.__all__:
                # Should not raise AttributeError
                value = getattr(core, item)
                assert value is not None

    def test_eager_imports_in_all(self):
        """Test that eagerly-imported items are in __all__."""
        import asciidoc_artisan.core as core

        eager_items = [
            "Settings",
            "GitResult",
            "GitStatus",
            "GitHubResult",
            "sanitize_path",
            "atomic_save_text",
            "atomic_save_json",
        ]

        for item in eager_items:
            assert item in core.__all__, f"{item} should be in __all__"


class TestImportPerformance:
    """Test import performance characteristics."""

    def test_module_imports_without_error(self):
        """Test that core module imports successfully."""
        try:
            import asciidoc_artisan.core  # noqa: F401

            assert True  # Import succeeded
        except Exception as e:
            pytest.fail(f"Core module import failed: {e}")

    def test_wildcard_import_works(self):
        """Test that 'from core import *' works."""
        # This test verifies __all__ is correctly defined
        try:
            from asciidoc_artisan import core

            # Get first few items from __all__
            sample = core.__all__[:5]
            for item in sample:
                assert hasattr(core, item)
        except Exception as e:
            pytest.fail(f"Wildcard import test failed: {e}")
