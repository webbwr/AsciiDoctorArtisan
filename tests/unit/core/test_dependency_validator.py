"""
Tests for DependencyValidator (v2.0.1).

Tests the dependency validation system that checks for required and
optional Python modules and system binaries.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core.dependency_validator import (
    Dependency,
    DependencyStatus,
    DependencyType,
    DependencyValidator,
    validate_dependencies,
)


@pytest.mark.unit
class TestEnums:
    """Test enum definitions."""

    def test_dependency_type_values(self):
        """Test DependencyType enum has correct values."""
        assert DependencyType.REQUIRED.value == "required"
        assert DependencyType.OPTIONAL.value == "optional"
        assert DependencyType.PYTHON.value == "python"
        assert DependencyType.SYSTEM.value == "system"

    def test_dependency_status_values(self):
        """Test DependencyStatus enum has correct values."""
        assert DependencyStatus.INSTALLED.value == "installed"
        assert DependencyStatus.MISSING.value == "missing"
        assert DependencyStatus.VERSION_MISMATCH.value == "version_mismatch"
        assert DependencyStatus.ERROR.value == "error"


@pytest.mark.unit
class TestDependencyDataclass:
    """Test Dependency dataclass."""

    def test_dependency_creation(self):
        """Test creating a Dependency instance."""
        dep = Dependency(
            name="test_module",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.INSTALLED,
            version="1.0.0",
        )

        assert dep.name == "test_module"
        assert dep.dep_type == DependencyType.REQUIRED
        assert dep.status == DependencyStatus.INSTALLED
        assert dep.version == "1.0.0"

    def test_dependency_optional_fields(self):
        """Test Dependency with optional fields."""
        dep = Dependency(
            name="optional_module",
            dep_type=DependencyType.OPTIONAL,
            status=DependencyStatus.MISSING,
            min_version="2.0.0",
            install_instructions="pip install optional_module",
            error_message="Module not found",
        )

        assert dep.min_version == "2.0.0"
        assert "pip install" in dep.install_instructions
        assert dep.error_message == "Module not found"


@pytest.mark.unit
class TestValidatorInitialization:
    """Test DependencyValidator initialization."""

    def test_validator_initialization(self):
        """Test validator initializes with empty dependency list."""
        validator = DependencyValidator()

        assert validator is not None
        assert isinstance(validator.dependencies, list)
        assert len(validator.dependencies) == 0


@pytest.mark.unit
class TestCheckPythonModule:
    """Test _check_python_module method."""

    def test_check_installed_python_module(self):
        """Test checking an installed Python module."""
        validator = DependencyValidator()

        # pytest is definitely installed in test environment
        validator._check_python_module(
            "pytest",
            DependencyType.REQUIRED,
            install_cmd="pip install pytest",
        )

        assert len(validator.dependencies) == 1
        dep = validator.dependencies[0]
        assert dep.name == "pytest"
        assert dep.status == DependencyStatus.INSTALLED
        assert dep.version is not None  # pytest has __version__

    def test_check_missing_python_module(self):
        """Test checking a missing Python module."""
        validator = DependencyValidator()

        validator._check_python_module(
            "nonexistent_module_12345",
            DependencyType.OPTIONAL,
            install_cmd="pip install nonexistent_module_12345",
        )

        assert len(validator.dependencies) == 1
        dep = validator.dependencies[0]
        assert dep.name == "nonexistent_module_12345"
        assert dep.status == DependencyStatus.MISSING
        assert dep.error_message is not None

    def test_check_module_with_version_attribute(self):
        """Test module with __version__ attribute."""
        validator = DependencyValidator()

        validator._check_python_module(
            "pytest",
            DependencyType.REQUIRED,
        )

        dep = validator.dependencies[0]
        assert dep.version is not None
        assert isinstance(dep.version, str)

    @patch("builtins.__import__")
    def test_check_module_version_mismatch(self, mock_import):
        """Test module with version mismatch."""
        # Mock module with old version
        mock_module = MagicMock()
        mock_module.__version__ = "1.0.0"
        mock_import.return_value = mock_module

        validator = DependencyValidator()
        validator._check_python_module(
            "test_module",
            DependencyType.REQUIRED,
            min_version="2.0.0",
        )

        dep = validator.dependencies[0]
        assert dep.status == DependencyStatus.VERSION_MISMATCH
        assert dep.version == "1.0.0"
        assert dep.min_version == "2.0.0"


@pytest.mark.unit
class TestCheckSystemBinary:
    """Test _check_system_binary method."""

    @patch("asciidoc_artisan.core.dependency_validator.shutil.which")
    def test_check_installed_system_binary(self, mock_which):
        """Test checking an installed system binary."""
        mock_which.return_value = "/usr/bin/git"

        validator = DependencyValidator()
        validator._check_system_binary(
            "git",
            DependencyType.OPTIONAL,
            install_cmd="brew install git",
        )

        assert len(validator.dependencies) == 1
        dep = validator.dependencies[0]
        assert dep.name == "git"
        assert dep.status == DependencyStatus.INSTALLED

    @patch("asciidoc_artisan.core.dependency_validator.shutil.which")
    def test_check_missing_system_binary(self, mock_which):
        """Test checking a missing system binary."""
        mock_which.return_value = None

        validator = DependencyValidator()
        validator._check_system_binary(
            "nonexistent_binary",
            DependencyType.OPTIONAL,
            install_cmd="install instructions",
        )

        assert len(validator.dependencies) == 1
        dep = validator.dependencies[0]
        assert dep.name == "nonexistent_binary"
        assert dep.status == DependencyStatus.MISSING
        assert "not found in PATH" in dep.error_message


@pytest.mark.unit
class TestGetBinaryVersion:
    """Test _get_binary_version method."""

    @patch("asciidoc_artisan.core.dependency_validator.subprocess.run")
    def test_get_binary_version_with_version_flag(self, mock_run):
        """Test getting binary version with --version flag."""
        mock_run.return_value = MagicMock(
            stdout="git version 2.39.0",
            stderr="",
            returncode=0,
        )

        validator = DependencyValidator()
        version = validator._get_binary_version("git")

        assert version == "git version 2.39.0"

    @patch("asciidoc_artisan.core.dependency_validator.subprocess.run")
    def test_get_binary_version_from_stderr(self, mock_run):
        """Test getting version from stderr output."""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="Version 1.0.0",
            returncode=0,
        )

        validator = DependencyValidator()
        version = validator._get_binary_version("test_binary")

        assert version == "Version 1.0.0"

    @patch("asciidoc_artisan.core.dependency_validator.subprocess.run")
    def test_get_binary_version_timeout(self, mock_run):
        """Test handling timeout when getting binary version."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)

        validator = DependencyValidator()
        version = validator._get_binary_version("slow_binary")

        assert version is None

    @patch("asciidoc_artisan.core.dependency_validator.subprocess.run")
    def test_get_binary_version_truncates_long_output(self, mock_run):
        """Test version output is truncated to 100 chars."""
        long_output = "v" * 200
        mock_run.return_value = MagicMock(
            stdout=long_output,
            stderr="",
            returncode=0,
        )

        validator = DependencyValidator()
        version = validator._get_binary_version("verbose_binary")

        assert len(version) == 100

    @patch("asciidoc_artisan.core.dependency_validator.subprocess.run")
    def test_get_binary_version_tries_multiple_flags(self, mock_run):
        """Test trying multiple version flags."""
        # First two calls fail, third succeeds
        mock_run.side_effect = [
            MagicMock(stdout="", stderr="", returncode=1),  # --version fails
            MagicMock(stdout="", stderr="", returncode=1),  # -v fails
            MagicMock(stdout="Version 1.0", stderr="", returncode=0),  # -V works
        ]

        validator = DependencyValidator()
        version = validator._get_binary_version("picky_binary")

        assert version == "Version 1.0"
        assert mock_run.call_count >= 3


@pytest.mark.unit
class TestVersionComparison:
    """Test _version_meets_requirement method."""

    def test_version_meets_exact_match(self):
        """Test exact version match."""
        validator = DependencyValidator()

        assert validator._version_meets_requirement("1.2.3", "1.2.3") is True

    def test_version_meets_newer(self):
        """Test newer version meets requirement."""
        validator = DependencyValidator()

        assert validator._version_meets_requirement("2.0.0", "1.2.3") is True
        assert validator._version_meets_requirement("1.3.0", "1.2.3") is True
        assert validator._version_meets_requirement("1.2.4", "1.2.3") is True

    def test_version_does_not_meet(self):
        """Test older version doesn't meet requirement."""
        validator = DependencyValidator()

        assert validator._version_meets_requirement("1.2.3", "2.0.0") is False
        assert validator._version_meets_requirement("1.2.3", "1.3.0") is False
        assert validator._version_meets_requirement("1.2.3", "1.2.4") is False

    def test_version_padding(self):
        """Test version comparison with different length versions."""
        validator = DependencyValidator()

        # 1.2 should be treated as 1.2.0
        assert validator._version_meets_requirement("1.2", "1.1.9") is True
        assert validator._version_meets_requirement("1.2", "1.2.1") is False

    def test_version_unparseable(self):
        """Test handling unparseable version strings."""
        validator = DependencyValidator()

        # Should return True (assume OK) for invalid versions
        assert validator._version_meets_requirement("invalid", "1.2.3") is True
        assert validator._version_meets_requirement("1.2.3", "invalid") is True


@pytest.mark.unit
class TestGetMissingDependencies:
    """Test get_missing_required and get_missing_optional methods."""

    def test_get_missing_required(self):
        """Test getting missing required dependencies."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "req1",
                DependencyType.REQUIRED,
                DependencyStatus.INSTALLED,
            ),
            Dependency(
                "req2",
                DependencyType.REQUIRED,
                DependencyStatus.MISSING,
            ),
            Dependency(
                "opt1",
                DependencyType.OPTIONAL,
                DependencyStatus.MISSING,
            ),
        ]

        missing = validator.get_missing_required()

        assert len(missing) == 1
        assert missing[0].name == "req2"

    def test_get_missing_optional(self):
        """Test getting missing optional dependencies."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "req1",
                DependencyType.REQUIRED,
                DependencyStatus.MISSING,
            ),
            Dependency(
                "opt1",
                DependencyType.OPTIONAL,
                DependencyStatus.INSTALLED,
            ),
            Dependency(
                "opt2",
                DependencyType.OPTIONAL,
                DependencyStatus.MISSING,
            ),
        ]

        missing = validator.get_missing_optional()

        assert len(missing) == 1
        assert missing[0].name == "opt2"


@pytest.mark.unit
class TestCriticalIssues:
    """Test has_critical_issues method."""

    def test_has_critical_issues_when_required_missing(self):
        """Test has_critical_issues returns True when required deps missing."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "req1",
                DependencyType.REQUIRED,
                DependencyStatus.MISSING,
            ),
        ]

        assert validator.has_critical_issues() is True

    def test_no_critical_issues_when_all_required_installed(self):
        """Test has_critical_issues returns False when all required installed."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "req1",
                DependencyType.REQUIRED,
                DependencyStatus.INSTALLED,
            ),
            Dependency(
                "opt1",
                DependencyType.OPTIONAL,
                DependencyStatus.MISSING,
            ),
        ]

        assert validator.has_critical_issues() is False

    def test_critical_issues_with_version_mismatch(self):
        """Test version mismatch counts as critical issue."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "req1",
                DependencyType.REQUIRED,
                DependencyStatus.VERSION_MISMATCH,
            ),
        ]

        assert validator.has_critical_issues() is True


@pytest.mark.unit
class TestValidationSummary:
    """Test get_validation_summary method."""

    def test_summary_with_all_installed(self):
        """Test summary when all dependencies installed."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "dep1",
                DependencyType.REQUIRED,
                DependencyStatus.INSTALLED,
            ),
            Dependency(
                "dep2",
                DependencyType.OPTIONAL,
                DependencyStatus.INSTALLED,
            ),
        ]

        summary = validator.get_validation_summary()

        assert "Total checked: 2" in summary
        assert "Installed: 2" in summary
        assert "Missing (required): 0" in summary

    def test_summary_with_missing_required(self):
        """Test summary includes missing required dependencies."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "critical_module",
                DependencyType.REQUIRED,
                DependencyStatus.MISSING,
                install_instructions="pip install critical_module",
            ),
        ]

        summary = validator.get_validation_summary()

        assert "CRITICAL" in summary
        assert "critical_module" in summary
        assert "pip install" in summary

    def test_summary_with_missing_optional(self):
        """Test summary includes missing optional dependencies."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "optional_module",
                DependencyType.OPTIONAL,
                DependencyStatus.MISSING,
            ),
        ]

        summary = validator.get_validation_summary()

        assert "Optional dependencies missing" in summary
        assert "optional_module" in summary


@pytest.mark.unit
class TestValidateAll:
    """Test validate_all method (integration test)."""

    @patch("builtins.__import__")
    @patch("asciidoc_artisan.core.dependency_validator.shutil.which")
    def test_validate_all_checks_multiple_dependencies(self, mock_which, mock_import):
        """Test validate_all checks both Python modules and system binaries."""
        # Mock Python module checks to succeed
        mock_module = MagicMock()
        mock_module.__version__ = "7.0.0"
        mock_import.return_value = mock_module

        # Mock system binary checks
        mock_which.return_value = "/usr/bin/pandoc"

        validator = DependencyValidator()
        result = validator.validate_all()

        # Should have checked multiple dependencies
        assert isinstance(result, list)
        assert len(result) > 0
        assert validator.dependencies == result


@pytest.mark.unit
class TestConvenienceFunction:
    """Test validate_dependencies convenience function."""

    @patch.object(DependencyValidator, "validate_all")
    def test_validate_dependencies_function(self, mock_validate):
        """Test validate_dependencies convenience function."""
        mock_validate.return_value = []

        result = validate_dependencies()

        assert isinstance(result, DependencyValidator)
        mock_validate.assert_called_once()


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_validator_summary(self):
        """Test summary with no dependencies checked."""
        validator = DependencyValidator()

        summary = validator.get_validation_summary()

        assert "Total checked: 0" in summary

    def test_multiple_missing_required_in_summary(self):
        """Test summary lists all missing required dependencies."""
        validator = DependencyValidator()
        validator.dependencies = [
            Dependency(
                "req1",
                DependencyType.REQUIRED,
                DependencyStatus.MISSING,
                install_instructions="install req1",
            ),
            Dependency(
                "req2",
                DependencyType.REQUIRED,
                DependencyStatus.MISSING,
                install_instructions="install req2",
            ),
        ]

        summary = validator.get_validation_summary()

        assert "req1" in summary
        assert "req2" in summary
        assert "install req1" in summary
        assert "install req2" in summary

    @patch("asciidoc_artisan.core.dependency_validator.subprocess.run")
    def test_get_binary_version_handles_exception(self, mock_run):
        """Test _get_binary_version handles unexpected exceptions."""
        mock_run.side_effect = Exception("Unexpected error")

        validator = DependencyValidator()
        version = validator._get_binary_version("broken_binary")

        # Should return None and not crash
        assert version is None

    @patch("builtins.__import__")
    def test_check_module_with_uppercase_version(self, mock_import):
        """Test module with uppercase VERSION attribute (lines 194-195)."""
        # Mock module with VERSION (not __version__)
        mock_module = type("MockModule", (), {})()
        mock_module.VERSION = "3.2.1"
        mock_import.return_value = mock_module

        validator = DependencyValidator()
        validator._check_python_module(
            "mock_module", DependencyType.OPTIONAL, min_version=None
        )

        assert len(validator.dependencies) == 1
        dep = validator.dependencies[0]
        assert dep.version == "3.2.1"
        assert dep.status == DependencyStatus.INSTALLED

    def test_missing_required_module_logs_error(self, caplog):
        """Test missing REQUIRED module logs error message (line 231)."""
        import logging

        caplog.set_level(logging.ERROR)

        validator = DependencyValidator()
        # Try to check a non-existent required module
        validator._check_python_module(
            "nonexistent_required_module_xyz123",
            DependencyType.REQUIRED,
            min_version=None,
        )

        # Should have logged an error for missing REQUIRED module
        assert any(
            "REQUIRED" in record.message
            and "nonexistent_required_module_xyz123" in record.message
            for record in caplog.records
        )
