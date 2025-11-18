"""
Dependency Validator - Validates system and Python dependencies at startup.

This module checks for required and optional dependencies and provides
clear feedback to the user about what's installed and what's missing.

Checks:
- System binaries (pandoc, wkhtmltopdf, git, gh, ollama)
- Python modules (PySide6, asciidoc3, pypandoc, etc.)
- Dependency versions where applicable
- Provides installation instructions for missing dependencies

v2.0.1: Created for comprehensive startup validation
"""

import logging
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Dependency type classification."""

    REQUIRED = "required"  # Must be present for app to work
    OPTIONAL = "optional"  # Nice to have, but app works without it
    PYTHON = "python"  # Python module dependency
    SYSTEM = "system"  # System binary dependency


class DependencyStatus(Enum):
    """Dependency status after validation."""

    INSTALLED = "installed"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"
    ERROR = "error"


@dataclass
class Dependency:
    """Represents a single dependency."""

    name: str
    dep_type: DependencyType
    status: DependencyStatus
    version: str | None = None
    min_version: str | None = None
    install_instructions: str | None = None
    error_message: str | None = None


class DependencyValidator:
    """Validates all application dependencies."""

    def __init__(self) -> None:
        """Initialize the dependency validator."""
        self.dependencies: list[Dependency] = []

    def validate_all(self) -> list[Dependency]:
        """
        Validate all dependencies.

        Returns:
            List of Dependency objects with their validation status
        """
        logger.info("Starting dependency validation...")

        # Check Python modules (required)
        self._check_python_module(
            "PySide6",
            DependencyType.REQUIRED,
            min_version="6.9.0",
            install_cmd="pip install 'PySide6>=6.9.0'",
        )
        self._check_python_module(
            "asciidoc3",
            DependencyType.REQUIRED,
            min_version="3.2.0",
            install_cmd="pip install 'asciidoc3>=3.2.0'",
        )

        # Check Python modules (optional but commonly used)
        self._check_python_module(
            "pypandoc",
            DependencyType.OPTIONAL,
            min_version="1.13",
            install_cmd="pip install 'pypandoc>=1.13'",
        )
        self._check_python_module(
            "pymupdf",
            DependencyType.OPTIONAL,
            min_version="1.23.0",
            install_cmd="pip install 'pymupdf>=1.23.0'",
        )
        self._check_python_module(
            "keyring",
            DependencyType.REQUIRED,
            min_version="24.0.0",
            install_cmd="pip install 'keyring>=24.0.0'",
        )
        self._check_python_module(
            "psutil",
            DependencyType.REQUIRED,
            min_version="5.9.0",
            install_cmd="pip install 'psutil>=5.9.0'",
        )
        self._check_python_module(
            "ollama",
            DependencyType.OPTIONAL,
            min_version="0.4.0",
            install_cmd="pip install 'ollama>=0.4.0'",
        )
        self._check_python_module(
            "anthropic",
            DependencyType.OPTIONAL,
            min_version="0.72.0",
            install_cmd="pip install 'anthropic>=0.72.0'",
        )

        # Check system binaries (optional)
        self._check_system_binary(
            "pandoc",
            DependencyType.OPTIONAL,
            install_cmd="Install from: https://pandoc.org/installing.html\n"
            "macOS: brew install pandoc\n"
            "Ubuntu/Debian: sudo apt install pandoc\n"
            "Windows: Download installer from pandoc.org",
        )
        self._check_system_binary(
            "wkhtmltopdf",
            DependencyType.OPTIONAL,
            install_cmd="Install from: https://wkhtmltopdf.org/downloads.html\n"
            "macOS: brew install wkhtmltopdf\n"
            "Ubuntu/Debian: sudo apt install wkhtmltopdf\n"
            "Windows: Download installer from wkhtmltopdf.org",
        )
        self._check_system_binary(
            "git",
            DependencyType.OPTIONAL,
            install_cmd="Install from: https://git-scm.com/downloads\n"
            "macOS: brew install git\n"
            "Ubuntu/Debian: sudo apt install git\n"
            "Windows: Download installer from git-scm.com",
        )
        self._check_system_binary(
            "gh",
            DependencyType.OPTIONAL,
            install_cmd="Install from: https://cli.github.com/\n"
            "macOS: brew install gh\n"
            "Ubuntu/Debian: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md\n"
            "Windows: Download installer from cli.github.com",
        )
        self._check_system_binary(
            "ollama",
            DependencyType.OPTIONAL,
            install_cmd="Install from: https://ollama.com/download\n"
            "macOS: Download from ollama.com/download\n"
            "Linux: curl -fsSL https://ollama.com/install.sh | sh\n"
            "Windows: Download installer from ollama.com",
        )

        logger.info(f"Dependency validation complete: {len(self.dependencies)} checked")
        return self.dependencies

    def _check_python_module(
        self,
        module_name: str,
        dep_type: DependencyType,
        min_version: str | None = None,
        install_cmd: str | None = None,
    ) -> None:
        """
        Check if a Python module is available and meets version requirements.

        Args:
            module_name: Name of the module to import
            dep_type: Type of dependency (REQUIRED or OPTIONAL)
            min_version: Minimum required version (optional)
            install_cmd: Installation command to suggest
        """
        try:
            # Import the module
            module = __import__(module_name)

            # Get version if available
            version = None
            if hasattr(module, "__version__"):
                version = module.__version__
            elif hasattr(module, "VERSION"):
                version = module.VERSION

            # Check version if minimum specified
            status = DependencyStatus.INSTALLED
            if min_version and version:
                if not self._version_meets_requirement(version, min_version):
                    status = DependencyStatus.VERSION_MISMATCH

            self.dependencies.append(
                Dependency(
                    name=module_name,
                    dep_type=dep_type,
                    status=status,
                    version=version,
                    min_version=min_version,
                    install_instructions=install_cmd,
                )
            )

            logger.debug(f"✓ Python module '{module_name}' found (version: {version or 'unknown'})")

        except ImportError as e:
            self.dependencies.append(
                Dependency(
                    name=module_name,
                    dep_type=dep_type,
                    status=DependencyStatus.MISSING,
                    min_version=min_version,
                    install_instructions=install_cmd,
                    error_message=str(e),
                )
            )

            if dep_type == DependencyType.REQUIRED:
                logger.error(f"✗ REQUIRED Python module '{module_name}' is missing!")
            else:
                logger.info(f"○ Optional Python module '{module_name}' not found")

    def _check_system_binary(
        self,
        binary_name: str,
        dep_type: DependencyType,
        install_cmd: str | None = None,
    ) -> None:
        """
        Check if a system binary is available in PATH.

        Args:
            binary_name: Name of the binary to check
            dep_type: Type of dependency (usually OPTIONAL for system binaries)
            install_cmd: Installation instructions to suggest
        """
        # Check if binary exists in PATH
        binary_path = shutil.which(binary_name)

        if binary_path:
            # Try to get version
            version = self._get_binary_version(binary_name)

            self.dependencies.append(
                Dependency(
                    name=binary_name,
                    dep_type=dep_type,
                    status=DependencyStatus.INSTALLED,
                    version=version,
                    install_instructions=install_cmd,
                )
            )

            logger.debug(f"✓ System binary '{binary_name}' found at {binary_path} (version: {version or 'unknown'})")

        else:
            self.dependencies.append(
                Dependency(
                    name=binary_name,
                    dep_type=dep_type,
                    status=DependencyStatus.MISSING,
                    install_instructions=install_cmd,
                    error_message=f"{binary_name} not found in PATH",
                )
            )

            logger.info(f"○ Optional system binary '{binary_name}' not found in PATH")

    def _get_binary_version(self, binary_name: str) -> str | None:
        """
        Get the version of a system binary.

        Args:
            binary_name: Name of the binary

        Returns:
            Version string or None if unable to determine
        """
        try:
            # Try common version flags
            for flag in ["--version", "-v", "-V", "version"]:
                try:
                    result = subprocess.run(
                        [binary_name, flag],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )

                    # Check both stdout and stderr
                    output = result.stdout or result.stderr

                    if output and len(output.strip()) > 0:
                        # Take first line, strip extra whitespace
                        version = output.split("\n")[0].strip()
                        # Limit length to avoid huge output
                        return version[:100] if version else None

                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

        except Exception as e:
            logger.debug(f"Could not get version for {binary_name}: {e}")

        return None

    def _version_meets_requirement(self, current: str, minimum: str) -> bool:
        """
        Check if current version meets minimum requirement.

        Args:
            current: Current version string (e.g., "1.2.3")
            minimum: Minimum required version (e.g., "1.2.0")

        Returns:
            True if current >= minimum, False otherwise
        """
        try:
            # Parse version strings (handle semantic versioning: X.Y.Z)
            current_parts = [int(x) for x in current.split(".")[:3]]
            minimum_parts = [int(x) for x in minimum.split(".")[:3]]

            # Pad to ensure same length
            while len(current_parts) < 3:
                current_parts.append(0)
            while len(minimum_parts) < 3:
                minimum_parts.append(0)

            return current_parts >= minimum_parts

        except (ValueError, AttributeError):
            # If we can't parse, assume version is OK
            logger.debug(f"Could not compare versions: current={current}, minimum={minimum}")
            return True

    def get_missing_required(self) -> list[Dependency]:
        """
        Get list of missing required dependencies.

        Returns:
            List of missing required dependencies
        """
        return [
            dep
            for dep in self.dependencies
            if dep.dep_type == DependencyType.REQUIRED and dep.status != DependencyStatus.INSTALLED
        ]

    def get_missing_optional(self) -> list[Dependency]:
        """
        Get list of missing optional dependencies.

        Returns:
            List of missing optional dependencies
        """
        return [
            dep
            for dep in self.dependencies
            if dep.dep_type == DependencyType.OPTIONAL and dep.status != DependencyStatus.INSTALLED
        ]

    def has_critical_issues(self) -> bool:
        """
        Check if there are any critical dependency issues.

        Returns:
            True if required dependencies are missing or have version issues
        """
        return len(self.get_missing_required()) > 0

    def get_validation_summary(self) -> str:
        """
        Get a human-readable validation summary.

        Returns:
            Formatted summary string
        """
        total = len(self.dependencies)
        installed = len([d for d in self.dependencies if d.status == DependencyStatus.INSTALLED])
        missing_required = len(self.get_missing_required())
        missing_optional = len(self.get_missing_optional())

        summary = "Dependency Validation Summary:\n"
        summary += f"  Total checked: {total}\n"
        summary += f"  Installed: {installed}\n"
        summary += f"  Missing (required): {missing_required}\n"
        summary += f"  Missing (optional): {missing_optional}\n"

        if missing_required > 0:
            summary += "\n⚠️  CRITICAL: Required dependencies are missing!\n"
            for dep in self.get_missing_required():
                summary += f"  - {dep.name}"
                if dep.install_instructions:
                    summary += f"\n    Install: {dep.install_instructions}\n"

        if missing_optional > 0:
            summary += "\nℹ️  Optional dependencies missing (features limited):\n"
            for dep in self.get_missing_optional():
                summary += f"  - {dep.name}\n"

        return summary


# Convenience function for quick validation
def validate_dependencies() -> DependencyValidator:
    """
    Validate all dependencies and return validator instance.

    Returns:
        DependencyValidator instance with validation results
    """
    validator = DependencyValidator()
    validator.validate_all()
    return validator
