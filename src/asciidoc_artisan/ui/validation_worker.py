"""
Validation Worker - Background thread for installation validation and updates.

Extracted from installation_validator_dialog.py for MA principle compliance.
Handles Python package and system binary validation in a background thread.
"""

import logging
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class ValidationWorker(QThread):
    """Worker thread for validating installation and updating dependencies."""

    validation_complete = Signal(dict)  # {category: [(name, status, version, message)]}
    update_progress = Signal(str)  # Progress message
    update_complete = Signal(bool, str)  # (success, message)

    def __init__(self, action: str = "validate"):
        """
        Initialize validation worker.

        Args:
            action: "validate" or "update"
        """
        super().__init__()
        self.action = action

    def run(self) -> None:
        """Run validation or update in background thread."""
        try:
            if self.action == "validate":
                logger.info("Starting validation...")
                self._validate_installation()
                logger.info("Validation complete")
            elif self.action == "update":
                logger.info("Starting dependency update...")
                self._update_dependencies()
                logger.info("Update complete")
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            # Emit empty results on error
            if self.action == "validate":
                self.validation_complete.emit(
                    {
                        "python_packages": [("ERROR", "✗", "error", f"Validation failed: {str(e)}")],
                        "system_binaries": [],
                        "optional_tools": [],
                    }
                )

    def _validate_installation(self) -> None:
        """Validate all application requirements."""
        results = {
            "python_packages": [],
            "system_binaries": [],
            "optional_tools": [],
        }

        # Check Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 14):
            results["python_packages"].append(("Python", "✓", py_version, "Version OK"))  # pragma: no cover
        else:
            results["python_packages"].append(("Python", "✗", py_version, "Requires Python 3.14+"))

        # Check required Python packages
        required_packages = [
            ("PySide6", "6.9.0"),
            ("asciidoc3", "3.2.0"),
            ("pypandoc", "1.13"),
            ("pymupdf", "1.23.0"),
            ("keyring", "24.0.0"),
            ("psutil", "5.9.0"),
            ("pydantic", "2.0.0"),
            ("aiofiles", "24.1.0"),
            ("ollama", "0.4.0"),
        ]

        for package_name, min_version in required_packages:
            status, version, message = self._check_python_package(package_name, min_version)
            results["python_packages"].append((package_name, status, version, message))

        # Check system binaries
        system_binaries = [
            ("pandoc", True),  # Required
            ("wkhtmltopdf", True),  # Required
            ("git", False),  # Optional
            ("gh", False),  # Optional (GitHub CLI)
            ("ollama", False),  # Optional (AI)
        ]

        for binary_name, required in system_binaries:
            status, version, message = self._check_system_binary(binary_name, required)
            category = "system_binaries" if required else "optional_tools"
            results[category].append((binary_name, status, version, message))

        self.validation_complete.emit(results)

    def _check_python_package(self, package_name: str, min_version: str) -> tuple[str, str, str]:
        """
        Check if Python package is installed and meets minimum version.

        Args:
            package_name: Package name (e.g., "PySide6")
            min_version: Minimum required version (e.g., "6.9.0")

        Returns:
            (status, version, message) tuple
        """
        try:
            version = self._get_package_version(package_name)
            return self._validate_package_version(version, min_version)
        except ImportError:
            return ("✗", "not installed", f"Required: >={min_version}")
        except Exception as e:
            return ("✗", "error", f"Check failed: {str(e)[:50]}")

    def _get_package_version(self, package_name: str) -> str:
        """Import package and get version string.

        Args:
            package_name: Package name to import and check

        Returns:
            Version string or "unknown"

        Raises:
            ImportError: If package not installed
            ValueError: If package name not recognized
        """
        # Map package names to import names and version attributes
        package_map = {
            "PySide6": ("PySide6", "__version__"),
            "asciidoc3": ("asciidoc3", "__version__"),
            "pypandoc": ("pypandoc", "__version__"),
            "pymupdf": ("fitz", "__version__"),  # pymupdf imports as fitz
            "keyring": ("keyring", "__version__"),
            "psutil": ("psutil", "__version__"),
            "pydantic": ("pydantic", "__version__"),
            "aiofiles": ("aiofiles", "__version__"),
            "ollama": ("ollama", "__version__"),
        }

        if package_name not in package_map:
            raise ValueError(f"Unknown package: {package_name}")

        import_name, version_attr = package_map[package_name]

        # Dynamically import the module
        import importlib

        module = importlib.import_module(import_name)
        version = getattr(module, version_attr, "unknown")

        # For pymupdf, try fallback version attribute
        if version == "unknown" and import_name == "fitz":
            version = getattr(module, "version", "unknown")

        # Try alternative methods if still unknown
        if version == "unknown":
            version = self._get_version_from_metadata(package_name)

        if version == "unknown":
            version = self._get_version_from_pip(package_name)

        return version

    def _validate_package_version(self, version: str, min_version: str) -> tuple[str, str, str]:
        """Validate package version against minimum requirement.

        Args:
            version: Installed version string
            min_version: Minimum required version

        Returns:
            Tuple of (status_icon, version_string, message)
        """
        if version == "unknown":
            return ("⚠", version, "Installed (version unknown)")

        # Safely compare versions
        try:
            if self._version_compare(version, min_version) >= 0:
                return ("✓", version, "Version OK")
            else:
                return ("⚠", version, f"Upgrade recommended (>={min_version})")
        except Exception:
            # Version comparison failed, assume OK if installed
            return ("⚠", version, "Installed (version check failed)")

    def _check_system_binary(self, binary_name: str, required: bool) -> tuple[str, str, str]:
        """
        Check if system binary is installed.

        Args:
            binary_name: Binary name (e.g., "pandoc")
            required: Whether binary is required

        Returns:
            (status, version, message) tuple
        """
        try:
            # Check if binary exists
            result = subprocess.run(
                ["which", binary_name],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode != 0:
                if required:
                    return ("✗", "not installed", "Required for core features")
                else:
                    return ("○", "not installed", "Optional - not installed")

            # Get version
            version_result = subprocess.run(
                [binary_name, "--version"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if version_result.returncode == 0:
                # Extract first line of version output
                version = version_result.stdout.strip().split("\n")[0]
                # Limit version string to 50 chars
                if len(version) > 50:
                    version = version[:47] + "..."
                return ("✓", version, "Installed")
            else:
                return ("✓", "installed", "Installed (version unknown)")

        except subprocess.TimeoutExpired:
            return ("⚠", "timeout", "Version check timed out")
        except Exception as e:
            return ("✗", "error", f"Check failed: {str(e)}")

    def _update_dependencies(self) -> None:
        """Update all Python dependencies to latest versions."""
        self.update_progress.emit("Starting dependency update...")

        try:
            # Get path to requirements.txt
            # Assuming we're in src/asciidoc_artisan/ui/
            project_root = Path(__file__).parent.parent.parent.parent
            requirements_file = project_root / "requirements.txt"

            if not requirements_file.exists():
                self.update_complete.emit(False, f"requirements.txt not found at {requirements_file}")
                return

            self.update_progress.emit(f"Found requirements: {requirements_file}")

            # Run pip install --upgrade
            self.update_progress.emit("Running pip install --upgrade -r requirements.txt...")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "-r",
                    str(requirements_file),
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )

            if result.returncode == 0:
                self.update_progress.emit("✓ Dependencies updated successfully!")
                self.update_complete.emit(
                    True,
                    "All dependencies updated to latest versions.\n\n"
                    "Please restart the application to use updated packages.",
                )
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                self.update_progress.emit(f"✗ Update failed: {error_msg}")
                self.update_complete.emit(False, f"Update failed:\n\n{error_msg}")

        except subprocess.TimeoutExpired:
            self.update_complete.emit(False, "Update timed out after 5 minutes.\n\nPlease try again.")
        except Exception as e:
            self.update_complete.emit(False, f"Update failed:\n\n{str(e)}")

    def _get_version_from_metadata(self, package_name: str) -> str:
        """
        Get package version using importlib.metadata (Python 3.8+).

        Args:
            package_name: Package name (e.g., "PySide6")

        Returns:
            Version string or "unknown"
        """
        try:
            # Try importlib.metadata first (standard in Python 3.8+)
            from importlib import metadata

            version = metadata.version(package_name)
            logger.info(f"Found version {version} for {package_name} via metadata")
            return version
        except ImportError:
            # importlib.metadata not available (shouldn't happen in Python 3.8+)
            logger.debug("importlib.metadata not available")
            return "unknown"
        except metadata.PackageNotFoundError:
            # Package not found in metadata
            logger.debug(f"Package {package_name} not found in metadata")  # pragma: no cover
            return "unknown"  # pragma: no cover
        except Exception as e:
            logger.warning(f"Error getting version for {package_name} from metadata: {e}")
            return "unknown"

    def _get_version_from_pip(self, package_name: str) -> str:
        """
        Get package version from pip if __version__ is not available.

        Args:
            package_name: Package name (e.g., "PySide6")

        Returns:
            Version string or "unknown"
        """
        try:
            # Use pip show to get version
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode == 0:
                # Parse output for Version: line
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        logger.info(f"Found version {version} for {package_name} via pip")
                        return version

            return "unknown"
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout getting version for {package_name} from pip")
            return "unknown"
        except Exception as e:
            logger.warning(f"Error getting version for {package_name} from pip: {e}")
            return "unknown"

    def _version_compare(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version (e.g., "6.9.1")
            version2: Second version (e.g., "6.9.0")

        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        try:
            # Extract numeric parts only
            v1_parts = [int(x) for x in version1.split(".")[:3] if x.isdigit()]
            v2_parts = [int(x) for x in version2.split(".")[:3] if x.isdigit()]

            # Pad with zeros if needed
            while len(v1_parts) < 3:
                v1_parts.append(0)
            while len(v2_parts) < 3:
                v2_parts.append(0)

            # Compare
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1

            return 0
        except Exception:  # pragma: no cover
            # If version parsing fails, assume equal # pragma: no cover
            return 0  # pragma: no cover
