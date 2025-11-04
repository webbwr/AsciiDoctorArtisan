"""Tests for ui.status_manager module."""

import pytest
from PySide6.QtWidgets import QMainWindow, QStatusBar, QPlainTextEdit
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.fixture
def main_window(qapp):
    """Create main window with required attributes for StatusManager."""
    window = QMainWindow()
    window.status_bar = QStatusBar()
    window.setStatusBar(window.status_bar)
    window._current_file_path = None
    window._unsaved_changes = False
    window.editor = QPlainTextEdit()
    window._settings = Mock()
    return window


class TestStatusManager:
    """Test suite for StatusManager."""

    def test_import(self):
        from asciidoc_artisan.ui.status_manager import StatusManager
        assert StatusManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        assert manager is not None

    def test_show_message(self, main_window):
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        # Mock QMessageBox to prevent blocking on exec()
        with patch('asciidoc_artisan.ui.status_manager.QMessageBox') as mock_msgbox:
            # show_message signature: (level, title, text) from status_manager.py:123
            manager.show_message("info", "Test Title", "Test message")
            # Verify QMessageBox was created but don't let it block
            mock_msgbox.assert_called_once()

    def test_extract_document_version(self, main_window):
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        # extract_document_version is a method, not standalone function
        text_with_version = ":version: 1.5.0\n\nContent"
        version = manager.extract_document_version(text_with_version)
        assert version == "1.5.0"

    # Window Title Tests

    def test_update_window_title_with_file(self, main_window):
        """Test window title updates with file path."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        main_window._current_file_path = Path("/home/user/document.adoc")
        main_window._unsaved_changes = False

        manager.update_window_title()

        assert "document.adoc" in main_window.windowTitle()
        assert "*" not in main_window.windowTitle()

    def test_update_window_title_no_file(self, main_window):
        """Test window title shows default filename when no file is open."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        main_window._current_file_path = None
        main_window._unsaved_changes = False

        manager.update_window_title()

        assert "untitled.adoc" in main_window.windowTitle()

    def test_update_window_title_with_unsaved_changes(self, main_window):
        """Test window title shows asterisk with unsaved changes."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        main_window._current_file_path = Path("/home/user/document.adoc")
        main_window._unsaved_changes = True

        manager.update_window_title()

        assert "*" in main_window.windowTitle()

    # Status Bar Message Tests

    def test_show_status_with_timeout(self, main_window):
        """Test status bar shows message with timeout."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        manager.show_status("Test message", 3000)

        # Message should be in status bar
        assert main_window.status_bar.currentMessage() == "Test message"

    def test_show_status_permanent(self, main_window):
        """Test status bar shows permanent message."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        manager.show_status("Permanent message", 0)

        assert main_window.status_bar.currentMessage() == "Permanent message"

    # Document Metrics Tests

    def test_count_words_basic(self, main_window):
        """Test word count for basic text."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        text = "This is a simple document with nine words here."
        count = manager.count_words(text)

        assert count == 9

    def test_count_words_excluding_attributes(self, main_window):
        """Test word count excludes AsciiDoc attributes."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        text = ":version: 1.0\n:author: Test\n\nThis has four words."
        count = manager.count_words(text)

        # Should exclude :version: and :author: lines
        assert count == 4

    def test_calculate_grade_level(self, main_window):
        """Test Flesch-Kincaid grade level calculation."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        # Simple text should have lower grade level
        simple_text = "The cat sat on the mat. It was warm."
        grade = manager.calculate_grade_level(simple_text)

        assert grade >= 0.0
        assert grade < 5.0  # Simple text should be elementary level

    def test_calculate_grade_level_empty(self, main_window):
        """Test grade level calculation with empty text."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        grade = manager.calculate_grade_level("")

        assert grade == 0.0

    def test_update_document_metrics(self, main_window):
        """Test document metrics update in status bar."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        # Initialize widgets
        manager.initialize_widgets()

        # Set document text (word count includes "=" as a word)
        main_window.editor.setPlainText(":version: 2.0.0\n\n= Document\n\nThis has five words.")

        manager.update_document_metrics()

        # Check version was extracted
        assert "2.0.0" in manager.version_label.text()

        # Check word count (includes "=" from heading = 6 total)
        assert "6" in manager.word_count_label.text()

        # Check grade level is displayed
        assert "Grade:" in manager.grade_level_label.text()

    # Version Extraction Tests

    def test_extract_version_revnumber(self, main_window):
        """Test version extraction from :revnumber: attribute."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        text = ":revnumber: 3.2.1\n\nContent"
        version = manager.extract_document_version(text)

        assert version == "3.2.1"

    def test_extract_version_from_title(self, main_window):
        """Test version extraction from title."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        text = "= AsciiDoc Artisan v1.9.0\n\nContent"
        version = manager.extract_document_version(text)

        assert version == "1.9.0"

    def test_extract_version_standalone(self, main_window):
        """Test version extraction from standalone version line."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        text = "Version: 4.5.6\n\nContent"
        version = manager.extract_document_version(text)

        assert version == "4.5.6"

    def test_extract_version_not_found(self, main_window):
        """Test version extraction returns None when no version found."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)

        text = "= Document\n\nNo version here."
        version = manager.extract_document_version(text)

        assert version is None

    # AI Status Tests

    def test_set_ai_model_ollama(self, main_window):
        """Test setting Ollama model in status bar."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        manager.initialize_widgets()

        manager.set_ai_model("llama2")

        assert "llama2" in manager.ai_status_label.text()
        assert "AI:" in manager.ai_status_label.text()

    def test_set_ai_model_pandoc(self, main_window):
        """Test setting Pandoc as conversion method."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        manager.initialize_widgets()

        manager.set_ai_model("Pandoc")

        assert "Pandoc" in manager.ai_status_label.text()
        assert "Conversion:" in manager.ai_status_label.text()

    def test_set_ai_model_clear(self, main_window):
        """Test clearing AI model from status bar."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        manager.initialize_widgets()

        manager.set_ai_model("llama2")
        assert manager.ai_status_label.text()  # Should have text

        manager.set_ai_model(None)
        assert manager.ai_status_label.text() == ""  # Should be empty

    # Cancel Button Tests

    def test_show_cancel_button(self, main_window):
        """Test showing cancel button for operation."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from PySide6.QtCore import QCoreApplication
        manager = StatusManager(main_window)
        manager.initialize_widgets()

        # Show the window so child widgets can be visible
        main_window.show()
        QCoreApplication.processEvents()

        manager.show_cancel_button("git")
        QCoreApplication.processEvents()

        assert manager.cancel_button.isVisible()
        assert manager._current_operation == "git"

    def test_hide_cancel_button(self, main_window):
        """Test hiding cancel button after operation."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from PySide6.QtCore import QCoreApplication
        manager = StatusManager(main_window)
        manager.initialize_widgets()

        # Show the window so child widgets can be visible
        main_window.show()
        QCoreApplication.processEvents()

        manager.show_cancel_button("pandoc")
        QCoreApplication.processEvents()
        assert manager.cancel_button.isVisible()

        manager.hide_cancel_button()
        QCoreApplication.processEvents()

        assert not manager.cancel_button.isVisible()
        assert manager._current_operation is None

    def test_on_cancel_clicked(self, main_window):
        """Test cancel button click delegates to worker_manager."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        manager = StatusManager(main_window)
        manager.initialize_widgets()

        # Mock worker_manager
        main_window.worker_manager = Mock()

        manager.show_cancel_button("git")
        manager._on_cancel_clicked()

        # Should call cancel_git_operation
        main_window.worker_manager.cancel_git_operation.assert_called_once()

        # Button should be hidden
        assert not manager.cancel_button.isVisible()

    # Git Status Tests (v1.9.0)

    def test_update_git_status_clean(self, main_window):
        """Test Git status display for clean repository."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from asciidoc_artisan.core import GitStatus

        manager = StatusManager(main_window)
        manager.initialize_widgets()

        status = GitStatus(
            branch="main",
            is_dirty=False,
            has_conflicts=False,
            modified_count=0,
            staged_count=0,
            untracked_count=0,
            ahead_count=0,
            behind_count=0,
        )

        manager.update_git_status(status)

        # Should show green color for clean repo
        assert "main" in manager.git_status_label.text()
        assert "#4ade80" in manager.git_status_label.styleSheet()  # Green

    def test_update_git_status_dirty(self, main_window):
        """Test Git status display for dirty repository."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from asciidoc_artisan.core import GitStatus

        manager = StatusManager(main_window)
        manager.initialize_widgets()

        status = GitStatus(
            branch="dev",
            is_dirty=True,
            has_conflicts=False,
            modified_count=3,
            staged_count=1,
            untracked_count=2,
            ahead_count=0,
            behind_count=0,
        )

        manager.update_git_status(status)

        # Should show yellow color and total change count (brief format)
        assert "dev" in manager.git_status_label.text()
        assert "●6" in manager.git_status_label.text()  # Total changes (3+1+2=6)
        assert "#fbbf24" in manager.git_status_label.styleSheet()  # Yellow

    def test_update_git_status_conflicts(self, main_window):
        """Test Git status display for repository with conflicts."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from asciidoc_artisan.core import GitStatus

        manager = StatusManager(main_window)
        manager.initialize_widgets()

        status = GitStatus(
            branch="feature",
            is_dirty=True,
            has_conflicts=True,
            modified_count=1,
            staged_count=0,
            untracked_count=0,
            ahead_count=0,
            behind_count=0,
        )

        manager.update_git_status(status)

        # Should show red color and conflict indicator
        assert "feature" in manager.git_status_label.text()
        assert "⚠" in manager.git_status_label.text()  # Conflict warning
        assert "#ef4444" in manager.git_status_label.styleSheet()  # Red

    def test_update_git_status_ahead_behind(self, main_window):
        """Test Git status display with ahead/behind (brief format shows clean)."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from asciidoc_artisan.core import GitStatus

        manager = StatusManager(main_window)
        manager.initialize_widgets()

        status = GitStatus(
            branch="sync",
            is_dirty=False,
            has_conflicts=False,
            modified_count=0,
            staged_count=0,
            untracked_count=0,
            ahead_count=2,
            behind_count=3,
        )

        manager.update_git_status(status)

        # Brief format: No local changes = clean status (ahead/behind not shown)
        assert "sync" in manager.git_status_label.text()
        assert "✓" in manager.git_status_label.text()  # Clean indicator
        assert "#4ade80" in manager.git_status_label.styleSheet()  # Green

    def test_restore_git_status_color(self, main_window):
        """Test Git status color restoration after theme change (v1.9.0+)."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from asciidoc_artisan.core import GitStatus

        manager = StatusManager(main_window)
        manager.initialize_widgets()

        # Set initial git status (dirty/yellow)
        status = GitStatus(
            branch="dev",
            is_dirty=True,
            has_conflicts=False,
            modified_count=3,
            staged_count=1,
            untracked_count=0,
            ahead_count=0,
            behind_count=0,
        )
        manager.update_git_status(status)

        # Verify initial color (brief format shows total changes: 3+1+0=4)
        assert "#fbbf24" in manager.git_status_label.styleSheet()  # Yellow
        assert "dev" in manager.git_status_label.text()
        assert "●4" in manager.git_status_label.text()  # Total changes

        # Clear the stylesheet (simulating theme change)
        manager.git_status_label.setStyleSheet("")

        # Verify color is cleared
        assert "" == manager.git_status_label.styleSheet()

        # Restore git status color
        manager.restore_git_status_color()

        # Verify color is restored
        assert "#fbbf24" in manager.git_status_label.styleSheet()  # Yellow restored
        assert "dev" in manager.git_status_label.text()
        assert "●4" in manager.git_status_label.text()  # Total changes
