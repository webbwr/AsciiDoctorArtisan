"""
Installation Validator Dialog - Validates app requirements and updates dependencies.

This dialog checks all application requirements (Python packages, system binaries,
optional tools) and provides one-click dependency updates.

Author: AsciiDoc Artisan Team
Version: 1.7.4
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QProgressBar,
    QGroupBox,
)

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

    def run(self):
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
                self.validation_complete.emit({
                    "python_packages": [("ERROR", "✗", "error", f"Validation failed: {str(e)}")],
                    "system_binaries": [],
                    "optional_tools": [],
                })

    def _validate_installation(self):
        """Validate all application requirements."""
        results = {
            "python_packages": [],
            "system_binaries": [],
            "optional_tools": [],
        }

        # Check Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 14):
            results["python_packages"].append(
                ("Python", "✓", py_version, "Version OK")
            )
        else:
            results["python_packages"].append(
                ("Python", "✗", py_version, "Requires Python 3.14+")
            )

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
            status, version, message = self._check_python_package(
                package_name, min_version
            )
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

    def _check_python_package(
        self, package_name: str, min_version: str
    ) -> Tuple[str, str, str]:
        """
        Check if Python package is installed and meets minimum version.

        Args:
            package_name: Package name (e.g., "PySide6")
            min_version: Minimum required version (e.g., "6.9.0")

        Returns:
            (status, version, message) tuple
        """
        try:
            # Import package to check if installed
            version = "unknown"

            if package_name == "PySide6":
                import PySide6
                version = getattr(PySide6, "__version__", "unknown")
            elif package_name == "asciidoc3":
                import asciidoc3
                version = getattr(asciidoc3, "__version__", "unknown")
            elif package_name == "pypandoc":
                import pypandoc
                version = getattr(pypandoc, "__version__", "unknown")
            elif package_name == "pymupdf":
                import fitz
                version = getattr(fitz, "__version__", getattr(fitz, "version", "unknown"))
            elif package_name == "keyring":
                import keyring
                version = getattr(keyring, "__version__", "unknown")
            elif package_name == "psutil":
                import psutil
                version = getattr(psutil, "__version__", "unknown")
            elif package_name == "pydantic":
                import pydantic
                version = getattr(pydantic, "__version__", "unknown")
            elif package_name == "aiofiles":
                import aiofiles
                version = getattr(aiofiles, "__version__", "unknown")
            elif package_name == "ollama":
                import ollama
                version = getattr(ollama, "__version__", "unknown")
            else:
                return ("✗", "unknown", "Unknown package")

            # Check version
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

        except ImportError:
            return ("✗", "not installed", f"Required: >={min_version}")
        except Exception as e:
            return ("✗", "error", f"Check failed: {str(e)[:50]}")

    def _check_system_binary(
        self, binary_name: str, required: bool
    ) -> Tuple[str, str, str]:
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

    def _update_dependencies(self):
        """Update all Python dependencies to latest versions."""
        self.update_progress.emit("Starting dependency update...")

        try:
            # Get path to requirements.txt
            # Assuming we're in src/asciidoc_artisan/ui/
            project_root = Path(__file__).parent.parent.parent.parent
            requirements_file = project_root / "requirements.txt"

            if not requirements_file.exists():
                self.update_complete.emit(
                    False, f"requirements.txt not found at {requirements_file}"
                )
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
            self.update_complete.emit(
                False, "Update timed out after 5 minutes.\n\nPlease try again."
            )
        except Exception as e:
            self.update_complete.emit(False, f"Update failed:\n\n{str(e)}")

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
        except Exception:
            # If version parsing fails, assume equal
            return 0


class InstallationValidatorDialog(QDialog):
    """Dialog for validating installation and updating dependencies."""

    def __init__(self, parent=None):
        """Initialize installation validator dialog."""
        super().__init__(parent)
        self.setWindowTitle("Installation Validator")
        self.setMinimumSize(700, 600)
        self.worker: Optional[ValidationWorker] = None

        self._setup_ui()
        self._start_validation()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Installation Validator")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        description = QLabel(
            "This tool validates all application requirements and allows you to\n"
            "update Python dependencies to their latest versions."
        )
        description.setStyleSheet("padding: 5px 10px; color: gray;")
        layout.addWidget(description)

        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet(
            "font-family: monospace; padding: 10px; background-color: #f5f5f5;"
        )
        layout.addWidget(self.results_text)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Progress label (hidden initially)
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("padding: 5px; font-style: italic;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Button bar
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Re-validate")
        self.validate_btn.clicked.connect(self._start_validation)
        button_layout.addWidget(self.validate_btn)

        self.update_btn = QPushButton("Update Dependencies")
        self.update_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;"
        )
        self.update_btn.clicked.connect(self._start_update)
        button_layout.addWidget(self.update_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def _start_validation(self):
        """Start validation in background thread."""
        if self.worker and self.worker.isRunning():
            return

        logger.info("Starting validation UI...")
        self.results_text.setPlainText("Validating installation...\n")
        self.validate_btn.setEnabled(False)
        self.update_btn.setEnabled(False)

        self.worker = ValidationWorker(action="validate")
        logger.info("Connecting signals...")
        self.worker.validation_complete.connect(self._show_validation_results)
        self.worker.finished.connect(self._validation_finished)
        logger.info("Starting worker thread...")
        self.worker.start()

    def _validation_finished(self):
        """Handle validation worker finished."""
        self.validate_btn.setEnabled(True)
        self.update_btn.setEnabled(True)

    def _show_validation_results(self, results: Dict[str, List[Tuple]]):
        """
        Display validation results.

        Args:
            results: {category: [(name, status, version, message)]}
        """
        logger.info(f"Displaying validation results: {len(results)} categories")
        logger.info(f"Python packages: {len(results.get('python_packages', []))}")
        logger.info(f"System binaries: {len(results.get('system_binaries', []))}")
        logger.info(f"Optional tools: {len(results.get('optional_tools', []))}")

        output = []

        # Python packages
        output.append("=" * 70)
        output.append("PYTHON PACKAGES")
        output.append("=" * 70)
        output.append("")

        for name, status, version, message in results.get("python_packages", []):
            output.append(f"{status} {name:20} {version:20} {message}")

        output.append("")

        # System binaries (required)
        output.append("=" * 70)
        output.append("SYSTEM BINARIES (Required)")
        output.append("=" * 70)
        output.append("")

        for name, status, version, message in results.get("system_binaries", []):
            output.append(f"{status} {name:20} {version:20} {message}")

        output.append("")

        # Optional tools
        output.append("=" * 70)
        output.append("OPTIONAL TOOLS")
        output.append("=" * 70)
        output.append("")

        for name, status, version, message in results.get("optional_tools", []):
            output.append(f"{status} {name:20} {version:20} {message}")

        output.append("")
        output.append("=" * 70)
        output.append("Legend: ✓=OK, ⚠=Warning, ✗=Missing/Error, ○=Optional not installed")
        output.append("=" * 70)

        result_text = "\n".join(output)
        logger.info(f"Setting text with {len(result_text)} characters, {len(output)} lines")
        self.results_text.setPlainText(result_text)
        logger.info("Text set successfully")

    def _start_update(self):
        """Start dependency update in background thread."""
        if self.worker and self.worker.isRunning():
            return

        # Confirm action
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Update Dependencies",
            "This will update all Python dependencies to their latest versions.\n\n"
            "The application will need to be restarted after the update.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.results_text.setPlainText("")
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.validate_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.close_btn.setEnabled(False)

        self.worker = ValidationWorker(action="update")
        self.worker.update_progress.connect(self._show_update_progress)
        self.worker.update_complete.connect(self._show_update_complete)
        self.worker.finished.connect(self._update_finished)
        self.worker.start()

    def _show_update_progress(self, message: str):
        """Show update progress message."""
        self.progress_label.setText(message)
        current = self.results_text.toPlainText()
        self.results_text.setPlainText(current + message + "\n")
        # Scroll to bottom
        cursor = self.results_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.results_text.setTextCursor(cursor)

    def _show_update_complete(self, success: bool, message: str):
        """Show update completion message."""
        from PySide6.QtWidgets import QMessageBox

        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

        if success:
            QMessageBox.information(self, "Update Complete", message)
            # Re-validate after successful update
            self._start_validation()
        else:
            QMessageBox.warning(self, "Update Failed", message)

    def _update_finished(self):
        """Handle update worker finished."""
        self.validate_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
