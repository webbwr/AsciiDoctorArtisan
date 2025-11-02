"""
Tests for Installation Validator Dialog.

This test suite validates the installation validator dialog functionality,
including requirement validation and dependency updates.

Author: AsciiDoc Artisan Team
Version: 1.7.4
"""

import subprocess
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from asciidoc_artisan.ui.installation_validator_dialog import (
    InstallationValidatorDialog,
    ValidationWorker,
)


@pytest.fixture
def qapp():
    """Provide QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.processEvents()


@pytest.fixture
def dialog(qapp, qtbot):
    """Create installation validator dialog for testing."""
    # Mock the validation to prevent actual validation on init
    with patch.object(InstallationValidatorDialog, "_start_validation"):
        dlg = InstallationValidatorDialog()
        qtbot.addWidget(dlg)
        yield dlg
        dlg.close()


class TestValidationWorker:
    """Test ValidationWorker class."""

    def test_worker_init_validate(self):
        """Test worker initialization with validate action."""
        worker = ValidationWorker(action="validate")
        assert worker.action == "validate"

    def test_worker_init_update(self):
        """Test worker initialization with update action."""
        worker = ValidationWorker(action="update")
        assert worker.action == "update"

    def test_check_python_package_installed(self):
        """Test checking installed Python package."""
        worker = ValidationWorker()

        # PySide6 should be installed (we're using it!)
        status, version, message = worker._check_python_package("PySide6", "6.0.0")
        assert status in ("✓", "⚠")  # Either OK or needs upgrade
        assert version != "not installed"

    def test_check_python_package_not_installed(self):
        """Test checking package that's not installed."""
        worker = ValidationWorker()

        # Use a package that definitely doesn't exist
        with patch("builtins.__import__", side_effect=ImportError):
            status, version, message = worker._check_python_package(
                "nonexistent_package_xyz", "1.0.0"
            )
            assert status == "✗"
            assert version == "not installed"
            assert "Required" in message

    def test_check_system_binary_installed(self):
        """Test checking installed system binary."""
        worker = ValidationWorker()

        # Python should always be available
        with patch("subprocess.run") as mock_run:
            # Mock 'which' success
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            status, version, message = worker._check_system_binary("python3", True)

            # Should have called 'which'
            assert mock_run.call_count >= 1

    def test_check_system_binary_not_installed(self):
        """Test checking binary that's not installed."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            # Mock 'which' failure
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            status, version, message = worker._check_system_binary(
                "nonexistent_binary", True
            )

            assert status == "✗"
            assert version == "not installed"
            assert "Required" in message

    def test_check_system_binary_optional_not_installed(self):
        """Test checking optional binary that's not installed."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            # Mock 'which' failure
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")
            status, version, message = worker._check_system_binary(
                "optional_binary", False
            )

            assert status == "○"
            assert version == "not installed"
            assert "Optional" in message

    def test_version_compare_equal(self):
        """Test version comparison - equal versions."""
        worker = ValidationWorker()
        assert worker._version_compare("1.2.3", "1.2.3") == 0

    def test_version_compare_greater(self):
        """Test version comparison - first version greater."""
        worker = ValidationWorker()
        assert worker._version_compare("1.2.4", "1.2.3") == 1
        assert worker._version_compare("2.0.0", "1.9.9") == 1

    def test_version_compare_less(self):
        """Test version comparison - first version less."""
        worker = ValidationWorker()
        assert worker._version_compare("1.2.2", "1.2.3") == -1
        assert worker._version_compare("1.9.9", "2.0.0") == -1

    def test_version_compare_invalid(self):
        """Test version comparison with invalid versions."""
        worker = ValidationWorker()
        # Should not crash, returns 0 for equal
        result = worker._version_compare("invalid", "1.0.0")
        assert result == 0


class TestInstallationValidatorDialog:
    """Test InstallationValidatorDialog class."""

    def test_dialog_creation(self, dialog):
        """Test dialog is created successfully."""
        assert dialog is not None
        assert dialog.windowTitle() == "Installation Validator"

    def test_dialog_ui_elements(self, dialog):
        """Test all UI elements are present."""
        assert dialog.results_text is not None
        assert dialog.progress_bar is not None
        assert dialog.progress_label is not None
        assert dialog.validate_btn is not None
        assert dialog.update_btn is not None
        assert dialog.close_btn is not None

    def test_validate_button_click(self, dialog, qtbot):
        """Test clicking validate button."""
        with patch.object(dialog, "_start_validation") as mock_validate:
            qtbot.mouseClick(dialog.validate_btn, Qt.MouseButton.LeftButton)
            mock_validate.assert_called_once()

    def test_update_button_click(self, dialog, qtbot):
        """Test clicking update button."""
        with patch.object(dialog, "_start_update") as mock_update:
            qtbot.mouseClick(dialog.update_btn, Qt.MouseButton.LeftButton)
            mock_update.assert_called_once()

    def test_close_button_click(self, dialog, qtbot):
        """Test clicking close button."""
        with patch.object(dialog, "accept") as mock_accept:
            qtbot.mouseClick(dialog.close_btn, Qt.MouseButton.LeftButton)
            mock_accept.assert_called_once()

    def test_show_validation_results(self, dialog):
        """Test displaying validation results."""
        results = {
            "python_packages": [
                ("PySide6", "✓", "6.9.0", "Version OK"),
                ("missing_pkg", "✗", "not installed", "Required: >=1.0.0"),
            ],
            "system_binaries": [
                ("pandoc", "✓", "3.0.0", "Installed"),
                ("wkhtmltopdf", "✗", "not installed", "Required for core features"),
            ],
            "optional_tools": [
                ("git", "✓", "2.40.0", "Installed"),
                ("ollama", "○", "not installed", "Optional - not installed"),
            ],
        }

        dialog._show_validation_results(results)

        text = dialog.results_text.toPlainText()
        assert "PYTHON PACKAGES" in text
        assert "SYSTEM BINARIES" in text
        assert "OPTIONAL TOOLS" in text
        assert "PySide6" in text
        assert "pandoc" in text
        assert "git" in text

    def test_show_update_progress(self, dialog):
        """Test showing update progress."""
        dialog._show_update_progress("Installing packages...")
        text = dialog.results_text.toPlainText()
        assert "Installing packages..." in text
        assert dialog.progress_label.text() == "Installing packages..."

    def test_show_update_complete_success(self, dialog, qtbot):
        """Test showing successful update completion."""
        with patch("PySide6.QtWidgets.QMessageBox.information") as mock_info:
            with patch.object(dialog, "_start_validation") as mock_validate:
                dialog._show_update_complete(True, "Update successful!")
                mock_info.assert_called_once()
                # Should re-validate after successful update
                mock_validate.assert_called_once()

    def test_show_update_complete_failure(self, dialog, qtbot):
        """Test showing failed update completion."""
        with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog._show_update_complete(False, "Update failed!")
            mock_warning.assert_called_once()

    def test_start_validation_disables_buttons(self, dialog):
        """Test that starting validation disables buttons."""
        with patch.object(ValidationWorker, "start"):
            dialog._start_validation()
            # Buttons should be disabled during validation
            # (they'll be re-enabled when worker finishes)
            assert not dialog.validate_btn.isEnabled()
            assert not dialog.update_btn.isEnabled()

    def test_validation_finished_enables_buttons(self, dialog):
        """Test that validation finishing re-enables buttons."""
        # Disable buttons first
        dialog.validate_btn.setEnabled(False)
        dialog.update_btn.setEnabled(False)

        dialog._validation_finished()

        assert dialog.validate_btn.isEnabled()
        assert dialog.update_btn.isEnabled()

    def test_start_update_shows_confirmation(self, dialog, qtbot):
        """Test that starting update shows confirmation dialog."""
        with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
            from PySide6.QtWidgets import QMessageBox

            # User clicks No
            mock_question.return_value = QMessageBox.StandardButton.No

            dialog._start_update()

            mock_question.assert_called_once()
            # Worker should not be started if user cancels
            assert dialog.worker is None or not dialog.worker.isRunning()

    def test_start_update_confirmed(self, dialog, qtbot):
        """Test starting update after confirmation."""
        with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
            from PySide6.QtWidgets import QMessageBox

            # User clicks Yes
            mock_question.return_value = QMessageBox.StandardButton.Yes

            with patch.object(ValidationWorker, "start"):
                dialog._start_update()

                # Should show progress indicators
                assert dialog.progress_bar.isVisible()
                assert dialog.progress_label.isVisible()
                # Should disable buttons
                assert not dialog.validate_btn.isEnabled()
                assert not dialog.update_btn.isEnabled()
                assert not dialog.close_btn.isEnabled()

    def test_update_finished_enables_buttons(self, dialog):
        """Test that update finishing re-enables buttons."""
        # Disable buttons first
        dialog.validate_btn.setEnabled(False)
        dialog.update_btn.setEnabled(False)
        dialog.close_btn.setEnabled(False)

        dialog._update_finished()

        assert dialog.validate_btn.isEnabled()
        assert dialog.update_btn.isEnabled()
        assert dialog.close_btn.isEnabled()

    def test_worker_not_started_if_already_running(self, dialog):
        """Test that worker is not started if already running."""
        # Create a mock worker that reports as running
        dialog.worker = Mock(spec=ValidationWorker)
        dialog.worker.isRunning.return_value = True

        initial_text = dialog.results_text.toPlainText()
        dialog._start_validation()

        # Should not change text or start new worker
        assert dialog.results_text.toPlainText() == initial_text


class TestValidationWorkerRun:
    """Test ValidationWorker run method with actual validation."""

    def test_validate_installation_python_version(self, qtbot):
        """Test validation detects Python version."""
        worker = ValidationWorker(action="validate")

        results = {}

        def capture_results(r):
            nonlocal results
            results = r

        worker.validation_complete.connect(capture_results)
        worker.run()

        # Should have results
        assert "python_packages" in results
        assert len(results["python_packages"]) > 0

        # First item should be Python version check
        python_check = results["python_packages"][0]
        assert python_check[0] == "Python"
        # Should show current Python version
        assert python_check[2] == f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def test_validate_installation_checks_packages(self, qtbot):
        """Test validation checks all required packages."""
        worker = ValidationWorker(action="validate")

        results = {}

        def capture_results(r):
            nonlocal results
            results = r

        worker.validation_complete.connect(capture_results)
        worker.run()

        # Should check PySide6 (we're using it)
        package_names = [pkg[0] for pkg in results.get("python_packages", [])]
        assert "PySide6" in package_names

    def test_update_dependencies_missing_requirements(self, qtbot):
        """Test update fails gracefully if requirements.txt missing."""
        worker = ValidationWorker(action="update")

        success = None
        message = None

        def capture_complete(s, m):
            nonlocal success, message
            success = s
            message = m

        worker.update_complete.connect(capture_complete)

        # Mock Path.exists to return False
        with patch("pathlib.Path.exists", return_value=False):
            worker.run()

            assert success is False
            assert "not found" in message


# Integration test
class TestInstallationValidatorIntegration:
    """Integration tests for the complete validator flow."""

    def test_full_validation_flow(self, dialog, qtbot):
        """Test complete validation flow."""
        # Start validation
        with patch.object(ValidationWorker, "run") as mock_run:
            dialog._start_validation()

            # Worker should be created and started
            assert dialog.worker is not None
            mock_run.assert_called_once()

    def test_validation_result_display_flow(self, dialog, qtbot):
        """Test validation result display after worker completes."""
        # Create mock results
        results = {
            "python_packages": [("PySide6", "✓", "6.9.0", "Version OK")],
            "system_binaries": [("pandoc", "✓", "3.0.0", "Installed")],
            "optional_tools": [("git", "✓", "2.40.0", "Installed")],
        }

        # Trigger result display
        dialog._show_validation_results(results)

        # Verify all results are shown
        text = dialog.results_text.toPlainText()
        assert "PySide6" in text
        assert "6.9.0" in text
        assert "pandoc" in text
        assert "git" in text
