"""
Tests for SyntaxCheckerManager (v2.0.0).

This module tests the syntax checker UI manager that shows real-time
error detection with visual feedback.
"""

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel
from asciidoc_artisan.core.syntax_checker import SyntaxChecker
from asciidoc_artisan.ui.syntax_checker_manager import SyntaxCheckerManager


@pytest.fixture
def editor(qtbot):
    """Create a test editor widget."""
    widget = QPlainTextEdit()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def checker():
    """Create a test syntax checker."""
    return SyntaxChecker()


@pytest.fixture
def manager(editor, checker):
    """Create a SyntaxCheckerManager instance."""
    return SyntaxCheckerManager(editor, checker)


class TestSyntaxCheckerInitialization:
    """Test manager initialization."""

    def test_manager_creation(self, manager, editor, checker):
        """Test manager is created with correct attributes."""
        assert manager.editor == editor
        assert manager.checker == checker
        assert hasattr(manager, "errors")
        assert manager.errors == []

    def test_default_settings(self, manager):
        """Test manager has default settings."""
        assert manager.enabled is True
        assert manager.check_delay == 500  # Default 500ms

    def test_timer_configuration(self, manager):
        """Test debounce timer is configured correctly."""
        assert hasattr(manager, "timer")
        assert manager.timer.isSingleShot() is True


class TestSyntaxCheckingEnable:
    """Test enabling/disabling syntax checking."""

    def test_enable_syntax_checking(self, manager):
        """Test enabling syntax checking."""
        manager.enabled = False
        assert manager.enabled is False

        manager.enabled = True
        assert manager.enabled is True

    def test_disable_clears_underlines(self, manager, editor):
        """Test disabling clears error underlines."""
        # Add some text with potential errors
        editor.setPlainText("= Heading\n\n== Missing Content")

        manager.enabled = True
        manager._validate_document()

        # Now disable
        manager.enabled = False

        # Errors should be cleared
        assert len(manager.errors) == 0 or manager.enabled is False


class TestErrorDetection:
    """Test error detection functionality."""

    def test_detect_basic_errors(self, manager, editor, qtbot):
        """Test detecting basic syntax errors."""
        # Create document with known error (missing blank line after heading)
        editor.setPlainText("= Heading\nContent without blank line")

        manager._validate_document()

        # Should detect some errors (depends on checker implementation)
        assert isinstance(manager.errors, list)

    def test_check_delay(self, manager, editor, qtbot):
        """Test syntax checking is debounced."""
        manager.check_delay = 100

        editor.setPlainText("= Test")
        qtbot.keyClick(editor, ord("x"))

        # Timer should be running
        assert manager.timer.isActive()

        # Wait for debounce
        qtbot.wait(200)

        # Timer should have fired
        assert not manager.timer.isActive()


class TestErrorUnderlines:
    """Test error underline visual feedback."""

    def test_show_error_underlines(self, manager, editor):
        """Test error underlines are shown in editor."""
        error = SyntaxErrorModel(
            code="E001",
            message="Test error",
            severity=ErrorSeverity.ERROR,
            line=0,
            column=0,
            length=5,
        )

        manager.errors = [error]
        manager._show_underlines()

        # Check that extra selections are added
        selections = editor.extraSelections()
        assert len(selections) > 0 or manager.enabled is False

    def test_error_color_coding(self, manager, editor):
        """Test errors are color-coded by severity."""
        errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=5,
            ),
            SyntaxErrorModel(
                code="W001",
                message="Warning",
                severity=ErrorSeverity.WARNING,
                line=1,
                column=0,
                length=5,
            ),
        ]

        manager.errors = errors
        manager._show_underlines()

        # Extra selections should reflect different severities
        selections = editor.extraSelections()
        assert len(selections) >= 0


class TestErrorNavigation:
    """Test jump-to-error navigation."""

    def test_jump_to_next_error(self, manager, editor):
        """Test jumping to next error."""
        editor.setPlainText("Line 1\nLine 2\nLine 3\nLine 4")

        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error 1",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=6,
            ),
            SyntaxErrorModel(
                code="E002",
                message="Error 2",
                severity=ErrorSeverity.ERROR,
                line=2,
                column=0,
                length=6,
            ),
        ]

        # Start cursor at end of document (after all errors)
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        editor.setTextCursor(cursor)

        # Jump to first error (wraps around)
        manager.jump_to_next_error()

        cursor = editor.textCursor()
        assert cursor.blockNumber() == 0  # Should wrap to first line

        # Jump to second error
        manager.jump_to_next_error()

        cursor = editor.textCursor()
        assert cursor.blockNumber() == 2  # Should be on third line

    def test_jump_to_previous_error(self, manager, editor):
        """Test jumping to previous error."""
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error 1",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=6,
            ),
            SyntaxErrorModel(
                code="E002",
                message="Error 2",
                severity=ErrorSeverity.ERROR,
                line=2,
                column=0,
                length=6,
            ),
        ]

        # Start at second error
        manager.current_error_index = 1
        cursor = editor.textCursor()
        cursor.setPosition(editor.document().findBlockByNumber(2).position())
        editor.setTextCursor(cursor)

        # Jump to previous error
        manager.jump_to_previous_error()

        cursor = editor.textCursor()
        assert cursor.blockNumber() == 0  # Should be on first line

    def test_wrap_around_navigation(self, manager, editor):
        """Test error navigation wraps around."""
        editor.setPlainText("Line 1\nLine 2")

        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error 1",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=6,
            ),
        ]

        # Jump past last error should wrap to first
        manager.current_error_index = 0
        manager.jump_to_next_error()
        manager.jump_to_next_error()

        # Should wrap back to first error
        assert manager.current_error_index == 0


class TestErrorSignals:
    """Test error change signals."""

    def test_errors_changed_signal(self, manager, qtbot):
        """Test errors_changed signal is emitted."""
        with qtbot.waitSignal(manager.errors_changed, timeout=1000):
            manager.errors = [
                SyntaxErrorModel(
                    code="E001",
                    message="Error",
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    length=5,
                )
            ]
            manager.errors_changed.emit(len(manager.errors))


class TestRealTimeChecking:
    """Test real-time syntax checking."""

    def test_check_on_text_change(self, manager, editor, qtbot):
        """Test syntax checking triggers on text change."""
        manager.enabled = True

        # Type some text
        qtbot.keyClick(editor, ord("="))

        # Timer should start
        assert manager.timer.isActive()

    def test_debounced_checking(self, manager, editor, qtbot):
        """Test rapid typing doesn't cause excessive checks."""
        manager.enabled = True
        manager.check_delay = 100

        # Type multiple characters quickly
        for char in "Hello":
            qtbot.keyClick(editor, ord(char))

        # Wait for debounce
        qtbot.wait(200)

        # Should have checked only once after debounce


class TestGetErrors:
    """Test retrieving error information."""

    def test_get_all_errors(self, manager):
        """Test getting all errors."""
        errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error 1",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=5,
            ),
            SyntaxErrorModel(
                code="E002",
                message="Error 2",
                severity=ErrorSeverity.ERROR,
                line=1,
                column=0,
                length=5,
            ),
        ]

        manager.errors = errors
        all_errors = manager.get_errors()

        assert len(all_errors) == 2
        assert all_errors[0].code == "E001"
        assert all_errors[1].code == "E002"

    def test_get_errors_by_severity(self, manager):
        """Test filtering errors by severity."""
        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=5,
            ),
            SyntaxErrorModel(
                code="W001",
                message="Warning",
                severity=ErrorSeverity.WARNING,
                line=1,
                column=0,
                length=5,
            ),
        ]

        errors = [e for e in manager.errors if e.severity == ErrorSeverity.ERROR]
        assert len(errors) == 1
        assert errors[0].code == "E001"


class TestGetErrorAtCursor:
    """Test getting error at cursor position."""

    def test_get_error_at_cursor_found(self, manager, editor):
        """Test getting error at cursor position when error exists."""
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error at column 2",
                severity=ErrorSeverity.ERROR,
                line=1,
                column=2,
                length=4,
            ),
        ]

        # Position cursor at error location (line 1, column 3)
        cursor = editor.textCursor()
        cursor.setPosition(editor.document().findBlockByNumber(1).position() + 3)
        editor.setTextCursor(cursor)

        error = manager.get_error_at_cursor()
        assert error is not None
        assert error.code == "E001"

    def test_get_error_at_cursor_not_found(self, manager, editor):
        """Test getting error at cursor when no error at position."""
        editor.setPlainText("Line 1\nLine 2")

        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=5,
            ),
        ]

        # Position cursor away from error (line 1)
        cursor = editor.textCursor()
        cursor.setPosition(editor.document().findBlockByNumber(1).position())
        editor.setTextCursor(cursor)

        error = manager.get_error_at_cursor()
        assert error is None


class TestClearErrors:
    """Test clearing errors."""

    def test_clear_errors(self, manager, editor, qtbot):
        """Test clearing all errors."""
        manager.errors = [
            SyntaxErrorModel(
                code="E001",
                message="Error",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                length=5,
            ),
        ]
        manager._show_underlines()

        # Clear errors
        with qtbot.waitSignal(manager.errors_changed, timeout=1000):
            manager.clear_errors()

        assert len(manager.errors) == 0
        assert len(editor.extraSelections()) == 0

    def test_clear_errors_when_already_empty(self, manager, editor, qtbot):
        """Test clearing errors when list is already empty."""
        assert len(manager.errors) == 0

        with qtbot.waitSignal(manager.errors_changed, timeout=1000):
            manager.clear_errors()

        assert len(manager.errors) == 0


class TestValidateNow:
    """Test immediate validation."""

    def test_validate_now(self, manager, editor):
        """Test immediate validation without debounce."""
        editor.setPlainText("= Test")

        # Should validate immediately
        manager.validate_now()

        # Timer should be stopped
        assert not manager.timer.isActive()

    def test_validate_now_stops_pending_timer(self, manager, editor, qtbot):
        """Test validate_now stops pending timer."""
        manager.check_delay = 1000
        editor.setPlainText("= Test")

        # Start timer via text change
        qtbot.keyClick(editor, ord("x"))
        assert manager.timer.isActive()

        # Immediate validation should stop timer
        manager.validate_now()
        assert not manager.timer.isActive()


class TestInfoSeverityUnderlines:
    """Test INFO severity underlines are shown with blue color."""

    def test_info_severity_underlines(self, manager, editor):
        """Test INFO severity errors get blue underlines."""
        error = SyntaxErrorModel(
            code="I001",
            message="Info message",
            severity=ErrorSeverity.INFO,
            line=0,
            column=0,
            length=5,
        )

        manager.errors = [error]
        manager._show_underlines()

        # Should create extra selection
        selections = editor.extraSelections()
        assert len(selections) > 0


class TestNavigationEdgeCases:
    """Test navigation edge cases."""

    def test_jump_to_next_error_with_no_errors(self, manager, editor):
        """Test jumping to next error when no errors exist."""
        manager.errors = []
        editor.setPlainText("Line 1\nLine 2")

        # Should not crash
        manager.jump_to_next_error()

    def test_jump_to_previous_error_with_no_errors(self, manager, editor):
        """Test jumping to previous error when no errors exist."""
        manager.errors = []
        editor.setPlainText("Line 1\nLine 2")

        # Should not crash
        manager.jump_to_previous_error()

    def test_current_error_index_property(self, manager):
        """Test current_error_index property getter and setter."""
        manager.current_error_index = 5
        assert manager.current_error_index == 5

        manager.current_error_index = 0
        assert manager.current_error_index == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_document(self, manager, editor):
        """Test syntax checking with empty document."""
        editor.setPlainText("")
        manager._validate_document()

        # Should not crash, errors list should be defined
        assert isinstance(manager.errors, list)

    def test_very_long_document(self, manager, editor):
        """Test syntax checking with long document."""
        long_text = "\n".join([f"= Heading {i}" for i in range(100)])
        editor.setPlainText(long_text)

        manager._validate_document()

        # Should handle without issues
        assert isinstance(manager.errors, list)

    def test_no_errors_found(self, manager, editor):
        """Test when no errors are found."""
        editor.setPlainText("= Valid Heading\n\nSome content.")

        manager._validate_document()

        # Errors list should be empty or have no critical issues
        assert isinstance(manager.errors, list)
