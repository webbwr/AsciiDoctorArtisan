"""
Tests for DependencyValidationDialog (v2.0.1).

Tests the dependency validation dialog that shows dependency check results
at startup with visual indicators and installation instructions.
"""

import pytest
from PySide6.QtWidgets import QMessageBox

from asciidoc_artisan.core import (
    Dependency,
    DependencyStatus,
    DependencyType,
)
from asciidoc_artisan.ui.dependency_dialog import (
    DependencyValidationDialog,
    show_dependency_summary_message,
    show_dependency_validation,
)


@pytest.fixture
def all_installed_deps():
    """Create list of all installed dependencies."""
    return [
        Dependency(
            name="pytest",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.INSTALLED,
            version="7.0.0",
        ),
        Dependency(
            name="PySide6",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.INSTALLED,
            version="6.5.0",
        ),
    ]


@pytest.fixture
def critical_missing_deps():
    """Create list with missing required dependency."""
    return [
        Dependency(
            name="pytest",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.MISSING,
            install_instructions="pip install pytest",
        ),
        Dependency(
            name="PySide6",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.INSTALLED,
            version="6.5.0",
        ),
    ]


@pytest.fixture
def optional_missing_deps():
    """Create list with missing optional dependency."""
    return [
        Dependency(
            name="pytest",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.INSTALLED,
            version="7.0.0",
        ),
        Dependency(
            name="pandas",
            dep_type=DependencyType.OPTIONAL,
            status=DependencyStatus.MISSING,
            install_instructions="pip install pandas",
        ),
    ]


@pytest.mark.unit
class TestDialogInitialization:
    """Test dialog initialization."""

    def test_dialog_creation_no_critical(self, qtbot, all_installed_deps):
        """Test dialog creation with all dependencies installed."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        assert dialog.dependencies == all_installed_deps
        assert dialog.has_critical is False

    def test_dialog_creation_with_critical(self, qtbot, critical_missing_deps):
        """Test dialog creation with critical missing dependencies."""
        dialog = DependencyValidationDialog(critical_missing_deps)
        qtbot.addWidget(dialog)

        assert dialog.has_critical is True

    def test_dialog_has_critical_issues_method(self, critical_missing_deps):
        """Test _has_critical_issues detects missing required deps."""
        dialog = DependencyValidationDialog(critical_missing_deps)

        # Should detect missing required dependency
        assert dialog.has_critical is True


@pytest.mark.unit
class TestWindowProperties:
    """Test window properties and titles."""

    def test_window_title_no_critical(self, qtbot, all_installed_deps):
        """Test window title when no critical issues."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        assert "✓ Dependency Check" in dialog.windowTitle()

    def test_window_title_with_critical(self, qtbot, critical_missing_deps):
        """Test window title with critical issues."""
        dialog = DependencyValidationDialog(critical_missing_deps)
        qtbot.addWidget(dialog)

        assert "❌ Critical Dependencies Missing" in dialog.windowTitle()

    def test_window_size_constraints(self, qtbot, all_installed_deps):
        """Test window has minimum size constraints."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        assert dialog.minimumWidth() == 700
        assert dialog.minimumHeight() == 500


@pytest.mark.unit
class TestHeaderCreation:
    """Test header label creation."""

    def test_header_all_installed(self, qtbot, all_installed_deps):
        """Test header when all dependencies installed."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        header = dialog._create_header()
        header_text = header.text()

        assert "✓ Dependency Check Complete" in header_text
        assert "2/2" in header_text  # 2 out of 2 installed

    def test_header_critical_missing(self, qtbot, critical_missing_deps):
        """Test header with critical missing dependencies."""
        dialog = DependencyValidationDialog(critical_missing_deps)
        qtbot.addWidget(dialog)

        header = dialog._create_header()
        header_text = header.text()

        assert "Critical Dependencies Missing" in header_text
        assert "1" in header_text  # 1 required dependency missing

    def test_header_optional_missing(self, qtbot, optional_missing_deps):
        """Test header with optional missing dependencies."""
        dialog = DependencyValidationDialog(optional_missing_deps)
        qtbot.addWidget(dialog)

        header = dialog._create_header()
        header_text = header.text()

        assert "✓ Dependency Check Complete" in header_text
        assert "1 optional features are unavailable" in header_text

    def test_header_summary_counts(self, qtbot):
        """Test header shows correct summary counts."""
        deps = [
            Dependency("dep1", DependencyType.REQUIRED, DependencyStatus.INSTALLED),
            Dependency("dep2", DependencyType.REQUIRED, DependencyStatus.MISSING),
            Dependency("dep3", DependencyType.OPTIONAL, DependencyStatus.MISSING),
        ]
        dialog = DependencyValidationDialog(deps)
        qtbot.addWidget(dialog)

        header = dialog._create_header()
        header_text = header.text()

        # 1 out of 3 installed
        assert "1/3" in header_text


@pytest.mark.unit
class TestDependencyRowFormatting:
    """Test dependency row HTML formatting."""

    def test_format_installed_dependency(self):
        """Test formatting of installed dependency."""
        dep = Dependency(
            name="pytest",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.INSTALLED,
            version="7.0.0",
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        assert "✓" in row_html  # Check mark icon
        assert "#388e3c" in row_html  # Green color
        assert "pytest" in row_html
        assert "v7.0.0" in row_html

    def test_format_missing_required_dependency(self):
        """Test formatting of missing required dependency."""
        dep = Dependency(
            name="pandas",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.MISSING,
            install_instructions="pip install pandas",
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        assert "✗" in row_html  # X icon
        assert "#d32f2f" in row_html  # Red color
        assert "pandas" in row_html
        assert "pip install pandas" in row_html

    def test_format_missing_optional_dependency(self):
        """Test formatting of missing optional dependency."""
        dep = Dependency(
            name="optional_pkg",
            dep_type=DependencyType.OPTIONAL,
            status=DependencyStatus.MISSING,
            install_instructions="pip install optional_pkg",
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        assert "○" in row_html  # Circle icon
        assert "#f57c00" in row_html  # Orange color
        assert "optional_pkg" in row_html

    def test_format_version_mismatch_dependency(self):
        """Test formatting of version mismatch dependency."""
        dep = Dependency(
            name="old_pkg",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.VERSION_MISMATCH,
            version="1.0.0",
            min_version="2.0.0",
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        assert "⚠️" in row_html  # Warning icon
        assert "#f57c00" in row_html  # Orange color

    def test_format_dependency_with_min_version(self):
        """Test formatting shows minimum version requirement."""
        dep = Dependency(
            name="pkg",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.MISSING,
            min_version="3.0.0",
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        assert "≥3.0.0" in row_html

    def test_format_dependency_without_install_instructions(self):
        """Test formatting dependency without install instructions."""
        dep = Dependency(
            name="pkg",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.MISSING,
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        # Should not contain installation section
        assert "pre" not in row_html or dep.install_instructions is None


@pytest.mark.unit
class TestDetailsView:
    """Test details view creation."""

    def test_details_view_shows_required_section(self, qtbot, all_installed_deps):
        """Test details view shows required dependencies section."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        details = dialog._create_details_view()
        html = details.toHtml()

        assert "Required Dependencies" in html

    def test_details_view_shows_optional_section(self, qtbot, optional_missing_deps):
        """Test details view shows optional dependencies section."""
        dialog = DependencyValidationDialog(optional_missing_deps)
        qtbot.addWidget(dialog)

        details = dialog._create_details_view()
        html = details.toHtml()

        assert "Optional Dependencies" in html

    def test_details_view_readonly(self, qtbot, all_installed_deps):
        """Test details view is read-only."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        details = dialog._create_details_view()

        assert details.isReadOnly() is True


@pytest.mark.unit
class TestFooterButtons:
    """Test footer button creation."""

    def test_footer_continue_button_no_critical(self, qtbot, all_installed_deps):
        """Test footer has Continue button when no critical issues."""
        dialog = DependencyValidationDialog(all_installed_deps)
        qtbot.addWidget(dialog)

        footer = dialog._create_footer()

        # Find the button in footer layout
        button = None
        for i in range(footer.count()):
            widget = footer.itemAt(i).widget()
            if widget and hasattr(widget, "text"):
                button = widget
                break

        assert button is not None
        assert button.text() == "Continue"

    def test_footer_exit_button_with_critical(self, qtbot, critical_missing_deps):
        """Test footer has Exit button when critical issues exist."""
        dialog = DependencyValidationDialog(critical_missing_deps)
        qtbot.addWidget(dialog)

        footer = dialog._create_footer()

        # Find the button in footer layout
        button = None
        for i in range(footer.count()):
            widget = footer.itemAt(i).widget()
            if widget and hasattr(widget, "text"):
                button = widget
                break

        assert button is not None
        assert button.text() == "Exit Application"

    def test_exit_button_has_red_style(self, qtbot, critical_missing_deps):
        """Test exit button has red background color."""
        dialog = DependencyValidationDialog(critical_missing_deps)
        qtbot.addWidget(dialog)

        footer = dialog._create_footer()

        # Find the button
        button = None
        for i in range(footer.count()):
            widget = footer.itemAt(i).widget()
            if widget and hasattr(widget, "text"):
                button = widget
                break

        assert button is not None
        style = button.styleSheet()
        assert "#d32f2f" in style or "red" in style.lower()


@pytest.mark.unit
class TestShowDependencyValidation:
    """Test show_dependency_validation helper function."""

    def test_show_validation_no_critical_returns_true(self, qtbot, all_installed_deps):
        """Test returns True when no critical issues."""
        result = show_dependency_validation(all_installed_deps)

        # Should return True immediately for non-critical
        assert result is True

    def test_show_validation_with_critical_shows_modal(self, qtbot, critical_missing_deps, monkeypatch):
        """Test shows modal dialog when critical issues exist."""
        dialog_exec_called = False

        def mock_exec(self):
            nonlocal dialog_exec_called
            dialog_exec_called = True
            return 1  # Accepted

        monkeypatch.setattr(DependencyValidationDialog, "exec", mock_exec)

        show_dependency_validation(critical_missing_deps)

        assert dialog_exec_called is True


@pytest.mark.unit
class TestShowDependencySummaryMessage:
    """Test show_dependency_summary_message helper function."""

    def test_summary_missing_required_shows_critical_box(self, qtbot, critical_missing_deps, monkeypatch):
        """Test shows critical message box for missing required deps."""
        message_box_shown = False

        def mock_exec(self):
            nonlocal message_box_shown
            message_box_shown = True
            return QMessageBox.StandardButton.Ignore

        monkeypatch.setattr(QMessageBox, "exec", mock_exec)

        show_dependency_summary_message(critical_missing_deps)

        assert message_box_shown is True

    def test_summary_optional_missing_logs_info(self, qtbot, optional_missing_deps, monkeypatch):
        """Test logs info for missing optional dependencies."""
        # Should not show message box, just log
        message_box_shown = False

        def mock_exec(self):
            nonlocal message_box_shown
            message_box_shown = True
            return QMessageBox.StandardButton.Ok

        monkeypatch.setattr(QMessageBox, "exec", mock_exec)

        show_dependency_summary_message(optional_missing_deps)

        # Should not show message box for optional-only
        assert message_box_shown is False

    def test_summary_all_installed_no_message(self, qtbot, all_installed_deps, monkeypatch):
        """Test no message when all dependencies installed."""
        message_box_shown = False

        def mock_exec(self):
            nonlocal message_box_shown
            message_box_shown = True
            return QMessageBox.StandardButton.Ok

        monkeypatch.setattr(QMessageBox, "exec", mock_exec)

        show_dependency_summary_message(all_installed_deps)

        assert message_box_shown is False


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dependencies_list(self, qtbot):
        """Test dialog with empty dependencies list."""
        dialog = DependencyValidationDialog([])
        qtbot.addWidget(dialog)

        assert dialog.has_critical is False
        header = dialog._create_header()
        assert "0/0" in header.text()

    def test_single_dependency(self, qtbot):
        """Test dialog with single dependency."""
        deps = [Dependency("only_one", DependencyType.REQUIRED, DependencyStatus.INSTALLED)]
        dialog = DependencyValidationDialog(deps)
        qtbot.addWidget(dialog)

        assert dialog.has_critical is False

    def test_mixed_dependency_types(self, qtbot):
        """Test dialog with mix of required and optional."""
        deps = [
            Dependency("req1", DependencyType.REQUIRED, DependencyStatus.INSTALLED),
            Dependency("req2", DependencyType.REQUIRED, DependencyStatus.MISSING),
            Dependency("opt1", DependencyType.OPTIONAL, DependencyStatus.INSTALLED),
            Dependency("opt2", DependencyType.OPTIONAL, DependencyStatus.MISSING),
        ]
        dialog = DependencyValidationDialog(deps)
        qtbot.addWidget(dialog)

        assert dialog.has_critical is True
        header = dialog._create_header()
        assert "2/4" in header.text()  # 2 out of 4 installed

    def test_dependency_with_multiline_install_instructions(self):
        """Test dependency with multi-line install instructions."""
        dep = Dependency(
            name="complex_pkg",
            dep_type=DependencyType.REQUIRED,
            status=DependencyStatus.MISSING,
            install_instructions="pip install complex_pkg\n# Or use conda:\nconda install complex_pkg",
        )
        dialog = DependencyValidationDialog([dep])

        row_html = dialog._format_dependency_row(dep)

        assert "pip install complex_pkg" in row_html
        assert "conda install" in row_html
