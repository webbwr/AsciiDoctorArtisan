"""
Tests for Installation Validator Dialog.

This test suite validates the installation validator dialog functionality,
including requirement validation and dependency updates.

Author: AsciiDoc Artisan Team
Version: 1.7.4
"""

import subprocess
import sys
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

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
    # Mock the worker to prevent actual validation on init
    with patch(
        "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker.start"
    ):
        dlg = InstallationValidatorDialog()
        qtbot.addWidget(dlg)
        yield dlg
        dlg.close()


@pytest.mark.unit
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

        # Use a package from the hardcoded list that might not be installed
        # Mock the import to simulate it not being installed
        with patch("builtins.__import__", side_effect=ImportError):
            status, version, message = worker._check_python_package(
                "ollama",
                "1.0.0",  # Use known package name so import is attempted
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
        # Should not crash; invalid version parsed as [] → [0,0,0] < [1,0,0] → -1
        result = worker._version_compare("invalid", "1.0.0")
        assert result == -1


@pytest.mark.unit
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

    def test_validate_button_click(self, dialog, qapp, qtbot):
        """Test clicking validate button."""
        # Reset worker to simulate fresh state and re-enable buttons
        dialog.worker = None
        dialog.validate_btn.setEnabled(True)
        dialog.update_btn.setEnabled(True)

        # Mock ValidationWorker to prevent actual validation
        with patch(
            "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker"
        ) as MockWorker:
            mock_worker = MockWorker.return_value
            mock_worker.isRunning.return_value = False

            qtbot.mouseClick(dialog.validate_btn, Qt.MouseButton.LeftButton)
            qapp.processEvents()  # Process Qt events

            # Verify worker was created and started
            MockWorker.assert_called_once_with(action="validate")
            mock_worker.start.assert_called_once()

    def test_update_button_click(self, dialog, qapp, qtbot):
        """Test clicking update button."""
        # Reset worker and enable buttons
        dialog.worker = None
        dialog.update_btn.setEnabled(True)

        # Mock QMessageBox to auto-confirm and ValidationWorker to prevent actual update
        with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
            from PySide6.QtWidgets import QMessageBox

            mock_question.return_value = QMessageBox.StandardButton.Yes

            with patch(
                "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker"
            ) as MockWorker:
                mock_worker = MockWorker.return_value
                mock_worker.isRunning.return_value = False

                qtbot.mouseClick(dialog.update_btn, Qt.MouseButton.LeftButton)
                qapp.processEvents()  # Process Qt events

                # Verify worker was created with update action
                MockWorker.assert_called_once_with(action="update")
                mock_worker.start.assert_called_once()

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
        # Mock ValidationWorker to prevent actual validation
        with patch(
            "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker"
        ) as MockWorker:
            mock_worker = MockWorker.return_value
            mock_worker.isRunning.return_value = False

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

    @pytest.mark.skip(
        reason="QMessageBox local import makes mocking complex - covered by integration tests"
    )
    def test_start_update_confirmed(self, dialog, qapp, qtbot):
        """Test starting update after confirmation."""
        # Reset worker to simulate fresh state and enable buttons
        dialog.worker = None
        dialog.validate_btn.setEnabled(True)
        dialog.update_btn.setEnabled(True)
        dialog.close_btn.setEnabled(True)

        with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
            from PySide6.QtWidgets import QMessageBox

            # User clicks Yes
            mock_question.return_value = QMessageBox.StandardButton.Yes

            # Mock ValidationWorker to prevent actual update
            with patch(
                "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker"
            ) as MockWorker:
                mock_worker = MockWorker.return_value
                mock_worker.isRunning.return_value = False

                dialog._start_update()
                qapp.processEvents()  # Process Qt events

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

    def test_update_not_started_if_worker_running(self, dialog):
        """Test that update is not started if worker is already running."""
        # Create a mock worker that reports as running
        dialog.worker = Mock(spec=ValidationWorker)
        dialog.worker.isRunning.return_value = True

        # Try to start update (should return early)
        dialog._start_update()

        # Worker should not be recreated or started
        # Original worker should still be there
        assert dialog.worker.isRunning.return_value is True


@pytest.mark.unit
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
        assert (
            python_check[2]
            == f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

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
@pytest.mark.unit
class TestInstallationValidatorIntegration:
    """Integration tests for the complete validator flow."""

    def test_full_validation_flow(self, dialog, qtbot):
        """Test complete validation flow."""
        # Mock ValidationWorker to prevent actual validation
        with patch(
            "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker"
        ) as MockWorker:
            mock_worker = MockWorker.return_value
            mock_worker.isRunning.return_value = False

            # Start validation
            dialog._start_validation()

            # Worker should be created and started
            assert dialog.worker is not None
            MockWorker.assert_called_once_with(action="validate")
            mock_worker.start.assert_called_once()

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


@pytest.mark.unit
class TestDependencyUpdateFlow:
    """Test dependency update success flow."""

    def test_update_dependencies_success(self, qtbot):
        """Test successful dependency update flow."""
        worker = ValidationWorker(action="update")

        progress_messages = []
        success = None
        message = None

        def capture_progress(msg):
            nonlocal progress_messages
            progress_messages.append(msg)

        def capture_complete(s, m):
            nonlocal success, message
            success = s
            message = m

        worker.update_progress.connect(capture_progress)
        worker.update_complete.connect(capture_complete)

        # Mock Path.exists to return True
        with patch("pathlib.Path.exists", return_value=True):
            # Mock subprocess.run for pip install
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=0, stdout="Successfully installed", stderr=""
                )

                worker.run()

                # Check progress messages were emitted
                assert len(progress_messages) > 0
                assert any("Found requirements" in msg for msg in progress_messages)
                assert any("Running pip install" in msg for msg in progress_messages)
                assert any("successfully" in msg for msg in progress_messages)

                # Check successful completion
                assert success is True
                assert "restart" in message.lower()

    def test_update_dependencies_pip_failure(self, qtbot):
        """Test dependency update with pip failure."""
        worker = ValidationWorker(action="update")

        success = None
        message = None

        def capture_complete(s, m):
            nonlocal success, message
            success = s
            message = m

        worker.update_complete.connect(capture_complete)

        # Mock Path.exists to return True
        with patch("pathlib.Path.exists", return_value=True):
            # Mock subprocess.run for pip install failure
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="",
                    stderr="ERROR: Could not install packages",
                )

                worker.run()

                # Check failed completion
                assert success is False
                assert "failed" in message.lower()

    def test_update_dependencies_timeout(self, qtbot):
        """Test dependency update timeout handling."""
        worker = ValidationWorker(action="update")

        success = None
        message = None

        def capture_complete(s, m):
            nonlocal success, message
            success = s
            message = m

        worker.update_complete.connect(capture_complete)

        # Mock Path.exists to return True
        with patch("pathlib.Path.exists", return_value=True):
            # Mock subprocess.run to raise TimeoutExpired
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(
                    cmd=["pip"], timeout=300
                )

                worker.run()

                # Check timeout handling
                assert success is False
                assert "timed out" in message.lower()

    def test_update_dependencies_general_exception(self, qtbot):
        """Test dependency update general exception handling."""
        worker = ValidationWorker(action="update")

        success = None
        message = None

        def capture_complete(s, m):
            nonlocal success, message
            success = s
            message = m

        worker.update_complete.connect(capture_complete)

        # Mock Path.exists to raise exception
        with patch("pathlib.Path.exists", side_effect=RuntimeError("Disk error")):
            worker.run()

            # Check exception handling
            assert success is False
            assert "failed" in message.lower()


@pytest.mark.unit
class TestVersionDetectionFallbacks:
    """Test version detection fallback methods."""

    def test_get_version_from_metadata_success(self):
        """Test getting version from importlib.metadata successfully."""
        worker = ValidationWorker()

        with patch("importlib.metadata.version") as mock_version:
            mock_version.return_value = "1.2.3"

            version = worker._get_version_from_metadata("test_package")

            assert version == "1.2.3"
            mock_version.assert_called_once_with("test_package")

    def test_get_version_from_metadata_import_error(self):
        """Test _get_version_from_metadata with ImportError."""
        worker = ValidationWorker()

        # Mock importlib import to raise ImportError
        with patch("builtins.__import__", side_effect=ImportError):
            version = worker._get_version_from_metadata("test_package")
            assert version == "unknown"

    def test_get_version_from_metadata_package_not_found(self):
        """Test _get_version_from_metadata with PackageNotFoundError."""
        worker = ValidationWorker()

        with patch("importlib.metadata.version") as mock_version:
            from importlib.metadata import PackageNotFoundError

            mock_version.side_effect = PackageNotFoundError

            version = worker._get_version_from_metadata("nonexistent_package")

            assert version == "unknown"

    def test_get_version_from_metadata_general_exception(self):
        """Test _get_version_from_metadata with general exception."""
        worker = ValidationWorker()

        with patch("importlib.metadata.version") as mock_version:
            mock_version.side_effect = RuntimeError("Unexpected error")

            version = worker._get_version_from_metadata("test_package")

            assert version == "unknown"

    def test_get_version_from_pip_success(self):
        """Test getting version from pip show successfully."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Name: test-package\nVersion: 2.3.4\nLocation: /usr/local",
                stderr="",
            )

            version = worker._get_version_from_pip("test-package")

            assert version == "2.3.4"

    def test_get_version_from_pip_failure(self):
        """Test getting version from pip when command fails."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1, stdout="", stderr="Package not found"
            )

            version = worker._get_version_from_pip("nonexistent")

            assert version == "unknown"

    def test_get_version_from_pip_timeout(self):
        """Test _get_version_from_pip timeout handling."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=["pip"], timeout=2)

            version = worker._get_version_from_pip("test-package")

            assert version == "unknown"

    def test_get_version_from_pip_exception(self):
        """Test _get_version_from_pip exception handling."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = RuntimeError("Subprocess error")

            version = worker._get_version_from_pip("test-package")

            assert version == "unknown"


@pytest.mark.unit
class TestDarkModeTheme:
    """Test dark mode theme application."""

    def test_apply_theme_dark_mode(self, qapp, qtbot):
        """Test theme application with dark mode enabled."""
        # Create real QWidget parent with mock settings
        mock_parent = QWidget()
        mock_settings = Mock()
        mock_settings.dark_mode = True
        mock_parent._settings = mock_settings

        # Mock the worker to prevent actual validation
        with patch(
            "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker.start"
        ):
            dialog = InstallationValidatorDialog(parent=mock_parent)
            qtbot.addWidget(dialog)

            # Verify dark theme colors are applied
            stylesheet = dialog.styleSheet()
            assert "#2b2b2b" in stylesheet or "2b2b2b" in stylesheet.lower()

            # Clean up
            dialog.close()
            mock_parent.deleteLater()

    def test_apply_theme_light_mode(self, qapp, qtbot):
        """Test theme application with light mode (default)."""
        # Create real QWidget parent with mock settings
        mock_parent = QWidget()
        mock_settings = Mock()
        mock_settings.dark_mode = False
        mock_parent._settings = mock_settings

        # Mock the worker to prevent actual validation
        with patch(
            "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker.start"
        ):
            dialog = InstallationValidatorDialog(parent=mock_parent)
            qtbot.addWidget(dialog)

            # Verify light theme colors are applied
            stylesheet = dialog.styleSheet()
            assert "#ffffff" in stylesheet or "ffffff" in stylesheet.lower()

            # Clean up
            dialog.close()
            mock_parent.deleteLater()

    def test_apply_theme_no_parent(self, qapp, qtbot):
        """Test theme application with no parent (defaults to light)."""
        # Mock the worker to prevent actual validation
        with patch(
            "asciidoc_artisan.ui.installation_validator_dialog.ValidationWorker.start"
        ):
            dialog = InstallationValidatorDialog(parent=None)
            qtbot.addWidget(dialog)

            # Should default to light mode
            stylesheet = dialog.styleSheet()
            assert "#ffffff" in stylesheet or "ffffff" in stylesheet.lower()

            # Clean up
            dialog.close()


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_worker_run_exception_validate(self, qtbot):
        """Test exception handling in ValidationWorker.run() for validate action."""
        worker = ValidationWorker(action="validate")

        results = {}

        def capture_results(r):
            nonlocal results
            results = r

        worker.validation_complete.connect(capture_results)

        # Mock _validate_installation to raise exception
        with patch.object(
            worker, "_validate_installation", side_effect=RuntimeError("Test error")
        ):
            worker.run()

            # Should emit error results
            assert "python_packages" in results
            assert len(results["python_packages"]) > 0
            error_entry = results["python_packages"][0]
            assert error_entry[0] == "ERROR"
            assert "failed" in error_entry[3].lower()

    def test_check_python_package_exception(self):
        """Test exception handling in _check_python_package()."""
        worker = ValidationWorker()

        # Mock import to raise unexpected exception (not ImportError)
        with patch("builtins.__import__", side_effect=RuntimeError("Unexpected error")):
            status, version, message = worker._check_python_package("PySide6", "6.0.0")

            assert status == "✗"
            assert version == "error"
            assert "Check failed" in message

    def test_version_compare_exception(self):
        """Test exception handling in _version_compare()."""
        worker = ValidationWorker()

        # These should not crash even with invalid input
        result = worker._version_compare("invalid.version", "1.2.3")
        # Invalid version parses to [], padded to [0,0,0], valid is [1,2,3]
        # [0,0,0] < [1,2,3] → -1
        assert result == -1

        result = worker._version_compare("1.2.3", "also.invalid")
        # Valid version [1,2,3], invalid version [0,0,0]
        # [1,2,3] > [0,0,0] → 1
        assert result == 1

    def test_check_system_binary_timeout(self):
        """Test system binary check timeout handling."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            # Simulate timeout on 'which' command
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=["which"], timeout=2)

            status, version, message = worker._check_system_binary("test_binary", True)

            assert status == "⚠"
            assert version == "timeout"
            assert "timed out" in message.lower()

    def test_check_system_binary_general_exception(self):
        """Test system binary check general exception handling."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = RuntimeError("Unexpected error")

            status, version, message = worker._check_system_binary("test_binary", True)

            assert status == "✗"
            assert version == "error"
            assert "Check failed" in message


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_check_unknown_package(self):
        """Test checking a package not in the hardcoded list."""
        worker = ValidationWorker()

        status, version, message = worker._check_python_package(
            "completely_unknown_package", "1.0.0"
        )

        assert status == "✗"
        assert version == "unknown"
        assert "Unknown package" in message

    def test_check_package_version_unknown_from_attribute(self):
        """Test package with unknown version from __version__ attribute."""
        worker = ValidationWorker()

        # Mock PySide6 import to return unknown version
        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "PySide6":
                    mock_module = Mock()
                    # Set __version__ to unknown
                    mock_module.__version__ = "unknown"
                    return mock_module
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            # Also mock the fallback methods to return unknown
            with patch.object(
                worker, "_get_version_from_metadata", return_value="unknown"
            ):
                with patch.object(
                    worker, "_get_version_from_pip", return_value="unknown"
                ):
                    status, version, message = worker._check_python_package(
                        "PySide6", "6.0.0"
                    )

                    assert status == "⚠"
                    assert version == "unknown"
                    assert "version unknown" in message.lower()

    def test_check_package_version_fallback_to_pip(self):
        """Test version fallback to pip when metadata fails."""
        worker = ValidationWorker()

        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "PySide6":
                    mock_module = Mock()
                    mock_module.__version__ = "unknown"
                    return mock_module
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            # Mock metadata to return unknown, pip to return valid version
            with patch.object(
                worker, "_get_version_from_metadata", return_value="unknown"
            ):
                with patch.object(
                    worker, "_get_version_from_pip", return_value="6.9.0"
                ):
                    status, version, message = worker._check_python_package(
                        "PySide6", "6.0.0"
                    )

                    # Should use pip version
                    assert version == "6.9.0"
                    assert status == "✓"

    def test_check_package_version_comparison_failure(self):
        """Test package version check when comparison fails."""
        worker = ValidationWorker()

        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "PySide6":
                    mock_module = Mock()
                    mock_module.__version__ = "weird.version.format"
                    return mock_module
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            # Mock _version_compare to raise exception
            with patch.object(
                worker, "_version_compare", side_effect=RuntimeError("Compare failed")
            ):
                status, version, message = worker._check_python_package(
                    "PySide6", "6.0.0"
                )

                assert status == "⚠"
                assert "version check failed" in message.lower()

    def test_check_package_version_upgrade_recommended(self):
        """Test package with version below minimum."""
        worker = ValidationWorker()

        with patch("builtins.__import__") as mock_import:

            def import_side_effect(name, *args, **kwargs):
                if name == "PySide6":
                    mock_module = Mock()
                    mock_module.__version__ = "5.0.0"
                    return mock_module
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            status, version, message = worker._check_python_package("PySide6", "6.0.0")

            assert status == "⚠"
            assert version == "5.0.0"
            assert "Upgrade recommended" in message

    def test_check_system_binary_long_version_truncation(self):
        """Test system binary version string truncation."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:
            # Mock 'which' success
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Mock version command with very long output
            def run_side_effect(*args, **kwargs):
                if args[0][0] == "which":
                    return Mock(returncode=0, stdout="", stderr="")
                else:  # version command
                    long_version = "x" * 100  # 100 character version string
                    return Mock(returncode=0, stdout=long_version, stderr="")

            mock_run.side_effect = run_side_effect

            status, version, message = worker._check_system_binary("test_binary", True)

            # Version should be truncated to 50 chars (47 + "...")
            assert len(version) == 50
            assert version.endswith("...")

    def test_check_system_binary_version_unknown_fallback(self):
        """Test system binary with failed version check but binary exists."""
        worker = ValidationWorker()

        with patch("subprocess.run") as mock_run:

            def run_side_effect(*args, **kwargs):
                if args[0][0] == "which":
                    # Binary exists
                    return Mock(returncode=0, stdout="/usr/bin/binary", stderr="")
                else:  # version command fails
                    return Mock(returncode=1, stdout="", stderr="")

            mock_run.side_effect = run_side_effect

            status, version, message = worker._check_system_binary("test_binary", True)

            assert status == "✓"
            assert version == "installed"
            assert "version unknown" in message.lower()
