"""
Tests for Git Status Dialog.

Tests the GitStatusDialog class which provides a detailed file-level
view of Git repository status (v1.9.0+).
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from asciidoc_artisan.ui.git_status_dialog import GitStatusDialog


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


@pytest.fixture
def dialog(qtbot):
    """Create a Git status dialog for testing."""
    widget = GitStatusDialog(parent=None)
    qtbot.addWidget(widget)
    return widget


class TestGitStatusDialogInitialization:
    """Test dialog initialization."""

    def test_dialog_creation(self, dialog):
        """Test dialog can be created."""
        assert dialog is not None
        assert isinstance(dialog, GitStatusDialog)

    def test_has_branch_label(self, dialog):
        """Test dialog has branch label."""
        assert hasattr(dialog, "branch_label")
        assert dialog.branch_label is not None

    def test_has_tab_widget(self, dialog):
        """Test dialog has tab widget."""
        assert hasattr(dialog, "tab_widget")
        assert dialog.tab_widget is not None
        assert dialog.tab_widget.count() == 3  # Modified, Staged, Untracked

    def test_has_modified_tab(self, dialog):
        """Test dialog has modified files tab."""
        assert hasattr(dialog, "modified_table")
        assert dialog.modified_table is not None

    def test_has_staged_tab(self, dialog):
        """Test dialog has staged files tab."""
        assert hasattr(dialog, "staged_table")
        assert dialog.staged_table is not None

    def test_has_untracked_tab(self, dialog):
        """Test dialog has untracked files tab."""
        assert hasattr(dialog, "untracked_table")
        assert dialog.untracked_table is not None

    def test_has_refresh_button(self, dialog):
        """Test dialog has refresh button."""
        assert hasattr(dialog, "refresh_button")
        assert dialog.refresh_button is not None

    def test_has_close_button(self, dialog):
        """Test dialog has close button."""
        assert hasattr(dialog, "close_button")
        assert dialog.close_button is not None


class TestGitStatusDialogPopulation:
    """Test dialog data population."""

    def test_populate_empty_status(self, dialog):
        """Test populating dialog with empty status."""
        dialog.populate_status("main", [], [], [])

        assert dialog.branch_label.text() == "Branch: main"
        assert dialog.modified_table.rowCount() == 0
        assert dialog.staged_table.rowCount() == 0
        assert dialog.untracked_table.rowCount() == 0

    def test_populate_modified_files(self, dialog):
        """Test populating modified files list."""
        modified_files = [
            {"path": "file1.txt", "status": "M", "lines_added": "10", "lines_deleted": "5"},
            {"path": "file2.txt", "status": "M", "lines_added": "3", "lines_deleted": "1"},
        ]

        dialog.populate_status("main", modified_files, [], [])

        assert dialog.modified_table.rowCount() == 2
        # First file - columns are: Status, File, Lines
        assert dialog.modified_table.item(0, 0).text() == "Modified"
        assert dialog.modified_table.item(0, 1).text() == "file1.txt"
        assert dialog.modified_table.item(0, 2).text() == "+10 -5"

    def test_populate_staged_files(self, dialog):
        """Test populating staged files list."""
        staged_files = [
            {"path": "staged1.txt", "status": "A", "lines_added": "20", "lines_deleted": "8"},
        ]

        dialog.populate_status("feature", [], staged_files, [])

        assert dialog.branch_label.text() == "Branch: feature"
        assert dialog.staged_table.rowCount() == 1
        assert dialog.staged_table.item(0, 0).text() == "Added"
        assert dialog.staged_table.item(0, 1).text() == "staged1.txt"
        assert dialog.staged_table.item(0, 2).text() == "+20 -8"

    def test_populate_untracked_files(self, dialog):
        """Test populating untracked files list."""
        untracked_files = [
            {"path": "new1.txt", "status": "?"},
            {"path": "new2.txt", "status": "?"},
            {"path": "new3.txt", "status": "?"},
        ]

        dialog.populate_status("main", [], [], untracked_files)

        assert dialog.untracked_table.rowCount() == 3
        assert dialog.untracked_table.item(0, 0).text() == "Untracked"
        assert dialog.untracked_table.item(0, 1).text() == "new1.txt"
        assert dialog.untracked_table.item(0, 2).text() == "--"
        assert dialog.untracked_table.item(1, 1).text() == "new2.txt"
        assert dialog.untracked_table.item(2, 1).text() == "new3.txt"

    def test_populate_all_categories(self, dialog):
        """Test populating all file categories at once."""
        modified = [{"path": "mod.txt", "status": "M", "lines_added": "5", "lines_deleted": "2"}]
        staged = [{"path": "stage.txt", "status": "A", "lines_added": "10", "lines_deleted": "0"}]
        untracked = [{"path": "new.txt", "status": "?"}]

        dialog.populate_status("develop", modified, staged, untracked)

        assert dialog.branch_label.text() == "Branch: develop"
        assert dialog.modified_table.rowCount() == 1
        assert dialog.staged_table.rowCount() == 1
        assert dialog.untracked_table.rowCount() == 1

    def test_repopulate_clears_old_data(self, dialog):
        """Test that repopulating clears old data."""
        # First population
        modified1 = [
            {"path": "file1.txt", "status": "M", "lines_added": "5", "lines_deleted": "2"},
            {"path": "file2.txt", "status": "M", "lines_added": "3", "lines_deleted": "1"},
        ]
        dialog.populate_status("main", modified1, [], [])
        assert dialog.modified_table.rowCount() == 2

        # Second population (fewer files)
        modified2 = [{"path": "file3.txt", "status": "M", "lines_added": "1", "lines_deleted": "0"}]
        dialog.populate_status("main", modified2, [], [])
        assert dialog.modified_table.rowCount() == 1
        assert dialog.modified_table.item(0, 1).text() == "file3.txt"  # Column 1 is File


class TestGitStatusDialogSignals:
    """Test dialog signal emissions."""

    def test_refresh_button_emits_signal(self, dialog, qtbot):
        """Test refresh button emits refresh_requested signal."""
        with qtbot.waitSignal(dialog.refresh_requested, timeout=1000):
            dialog.refresh_button.click()

    def test_close_button_closes_dialog(self, dialog, qtbot):
        """Test close button closes the dialog."""
        dialog.show()
        dialog.close_button.click()
        # Dialog should be hidden or closed
        assert not dialog.isVisible()


class TestGitStatusDialogTabSwitching:
    """Test tab switching behavior."""

    def test_switch_to_staged_tab(self, dialog):
        """Test switching to staged files tab."""
        dialog.tab_widget.setCurrentIndex(1)  # Staged tab
        assert dialog.tab_widget.currentIndex() == 1

    def test_switch_to_untracked_tab(self, dialog):
        """Test switching to untracked files tab."""
        dialog.tab_widget.setCurrentIndex(2)  # Untracked tab
        assert dialog.tab_widget.currentIndex() == 2

    def test_default_tab_is_modified(self, dialog):
        """Test that Modified tab is shown by default."""
        assert dialog.tab_widget.currentIndex() == 0  # Modified tab


class TestGitStatusDialogTableFormat:
    """Test table formatting and structure."""

    def test_modified_table_has_three_columns(self, dialog):
        """Test modified table has Status, File, Lines columns."""
        assert dialog.modified_table.columnCount() == 3
        assert dialog.modified_table.horizontalHeaderItem(0).text() == "Status"
        assert dialog.modified_table.horizontalHeaderItem(1).text() == "File"
        assert dialog.modified_table.horizontalHeaderItem(2).text() == "Lines"

    def test_staged_table_has_three_columns(self, dialog):
        """Test staged table has Status, File, Lines columns."""
        assert dialog.staged_table.columnCount() == 3
        assert dialog.staged_table.horizontalHeaderItem(0).text() == "Status"
        assert dialog.staged_table.horizontalHeaderItem(1).text() == "File"
        assert dialog.staged_table.horizontalHeaderItem(2).text() == "Lines"

    def test_untracked_table_has_three_columns(self, dialog):
        """Test untracked table has Status, File, Lines columns (same structure)."""
        assert dialog.untracked_table.columnCount() == 3
        assert dialog.untracked_table.horizontalHeaderItem(0).text() == "Status"
        assert dialog.untracked_table.horizontalHeaderItem(1).text() == "File"
        assert dialog.untracked_table.horizontalHeaderItem(2).text() == "Lines"

    def test_tables_have_no_edit_triggers(self, dialog):
        """Test tables are read-only (no edit triggers)."""
        from PySide6.QtWidgets import QAbstractItemView

        assert (
            dialog.modified_table.editTriggers()
            == QAbstractItemView.EditTrigger.NoEditTriggers
        )
        assert (
            dialog.staged_table.editTriggers()
            == QAbstractItemView.EditTrigger.NoEditTriggers
        )
        assert (
            dialog.untracked_table.editTriggers()
            == QAbstractItemView.EditTrigger.NoEditTriggers
        )
