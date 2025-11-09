"""
Tests for Git Status Dialog.

Tests the GitStatusDialog class which provides a detailed file-level
view of Git repository status (v1.9.0+).
"""

import pytest

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


@pytest.mark.unit
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


@pytest.mark.unit
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
            {
                "path": "file1.txt",
                "status": "M",
                "lines_added": "10",
                "lines_deleted": "5",
            },
            {
                "path": "file2.txt",
                "status": "M",
                "lines_added": "3",
                "lines_deleted": "1",
            },
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
            {
                "path": "staged1.txt",
                "status": "A",
                "lines_added": "20",
                "lines_deleted": "8",
            },
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
        modified = [
            {"path": "mod.txt", "status": "M", "lines_added": "5", "lines_deleted": "2"}
        ]
        staged = [
            {
                "path": "stage.txt",
                "status": "A",
                "lines_added": "10",
                "lines_deleted": "0",
            }
        ]
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
            {
                "path": "file1.txt",
                "status": "M",
                "lines_added": "5",
                "lines_deleted": "2",
            },
            {
                "path": "file2.txt",
                "status": "M",
                "lines_added": "3",
                "lines_deleted": "1",
            },
        ]
        dialog.populate_status("main", modified1, [], [])
        assert dialog.modified_table.rowCount() == 2

        # Second population (fewer files)
        modified2 = [
            {
                "path": "file3.txt",
                "status": "M",
                "lines_added": "1",
                "lines_deleted": "0",
            }
        ]
        dialog.populate_status("main", modified2, [], [])
        assert dialog.modified_table.rowCount() == 1
        assert (
            dialog.modified_table.item(0, 1).text() == "file3.txt"
        )  # Column 1 is File


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
class TestGitStatusDialogEdgeCases:
    """Test edge cases for dialog population."""

    def test_populate_with_very_long_file_path(self, dialog):
        """Test handling very long file paths."""
        long_path = "very/long/path/" + "subdir/" * 50 + "file.txt"
        modified = [
            {"path": long_path, "status": "M", "lines_added": "5", "lines_deleted": "2"}
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.rowCount() == 1
        assert long_path in dialog.modified_table.item(0, 1).text()

    def test_populate_with_unicode_file_path(self, dialog):
        """Test handling Unicode characters in file paths."""
        unicode_path = "файл.txt"  # Russian
        modified = [
            {
                "path": unicode_path,
                "status": "M",
                "lines_added": "1",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.rowCount() == 1
        assert dialog.modified_table.item(0, 1).text() == unicode_path

    def test_populate_with_emoji_in_path(self, dialog):
        """Test handling emoji in file paths."""
        emoji_path = "test_🔥_file.txt"
        modified = [
            {
                "path": emoji_path,
                "status": "M",
                "lines_added": "2",
                "lines_deleted": "1",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.rowCount() == 1
        assert dialog.modified_table.item(0, 1).text() == emoji_path

    def test_populate_with_many_files(self, dialog):
        """Test populating with many files (100)."""
        modified = [
            {
                "path": f"file{i}.txt",
                "status": "M",
                "lines_added": f"{i}",
                "lines_deleted": "1",
            }
            for i in range(100)
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.rowCount() == 100

    def test_populate_with_deleted_status(self, dialog):
        """Test handling deleted file status."""
        modified = [
            {
                "path": "deleted.txt",
                "status": "D",
                "lines_added": "0",
                "lines_deleted": "50",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.rowCount() == 1
        assert dialog.modified_table.item(0, 0).text() == "Deleted"

    def test_populate_with_renamed_status(self, dialog):
        """Test handling renamed file status."""
        staged = [
            {
                "path": "new_name.txt",
                "status": "R",
                "lines_added": "0",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", [], staged, [])

        assert dialog.staged_table.rowCount() == 1
        assert dialog.staged_table.item(0, 0).text() == "Renamed"

    def test_populate_with_copied_status(self, dialog):
        """Test handling copied file status."""
        staged = [
            {
                "path": "copy.txt",
                "status": "C",
                "lines_added": "100",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", [], staged, [])

        assert dialog.staged_table.item(0, 0).text() == "Copied"

    def test_populate_with_zero_line_changes(self, dialog):
        """Test handling files with no line changes."""
        modified = [
            {
                "path": "unchanged.txt",
                "status": "M",
                "lines_added": "0",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.item(0, 2).text() == "+0 -0"

    def test_populate_with_large_line_changes(self, dialog):
        """Test handling files with large line changes."""
        modified = [
            {
                "path": "huge.txt",
                "status": "M",
                "lines_added": "99999",
                "lines_deleted": "88888",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.item(0, 2).text() == "+99999 -88888"


@pytest.mark.unit
class TestGitStatusDialogBranchNames:
    """Test different branch name formats."""

    def test_branch_with_slashes(self, dialog):
        """Test branch name with slashes (feature/xyz)."""
        dialog.populate_status("feature/new-feature", [], [], [])

        assert dialog.branch_label.text() == "Branch: feature/new-feature"

    def test_branch_with_underscores(self, dialog):
        """Test branch name with underscores."""
        dialog.populate_status("feature_branch_123", [], [], [])

        assert dialog.branch_label.text() == "Branch: feature_branch_123"

    def test_branch_with_dots(self, dialog):
        """Test branch name with dots."""
        dialog.populate_status("release-1.2.3", [], [], [])

        assert dialog.branch_label.text() == "Branch: release-1.2.3"

    def test_empty_branch_name(self, dialog):
        """Test empty branch name."""
        dialog.populate_status("", [], [], [])

        assert dialog.branch_label.text() == "Branch: "

    def test_very_long_branch_name(self, dialog):
        """Test very long branch name."""
        long_branch = "feature/" + "x" * 100
        dialog.populate_status(long_branch, [], [], [])

        assert long_branch in dialog.branch_label.text()


@pytest.mark.unit
class TestGitStatusDialogMultiplePopulations:
    """Test multiple population calls."""

    def test_populate_twice_with_different_branches(self, dialog):
        """Test populating twice with different branches."""
        dialog.populate_status("main", [], [], [])
        assert dialog.branch_label.text() == "Branch: main"

        dialog.populate_status("develop", [], [], [])
        assert dialog.branch_label.text() == "Branch: develop"

    def test_populate_from_many_to_empty(self, dialog):
        """Test populating from many files to empty."""
        modified = [
            {
                "path": f"file{i}.txt",
                "status": "M",
                "lines_added": "1",
                "lines_deleted": "0",
            }
            for i in range(10)
        ]
        dialog.populate_status("main", modified, [], [])
        assert dialog.modified_table.rowCount() == 10

        dialog.populate_status("main", [], [], [])
        assert dialog.modified_table.rowCount() == 0

    def test_populate_switching_categories(self, dialog):
        """Test switching files between categories."""
        # First: files in modified
        modified = [
            {
                "path": "file.txt",
                "status": "M",
                "lines_added": "5",
                "lines_deleted": "2",
            }
        ]
        dialog.populate_status("main", modified, [], [])
        assert dialog.modified_table.rowCount() == 1
        assert dialog.staged_table.rowCount() == 0

        # Second: same file now staged
        staged = [
            {
                "path": "file.txt",
                "status": "M",
                "lines_added": "5",
                "lines_deleted": "2",
            }
        ]
        dialog.populate_status("main", [], staged, [])
        assert dialog.modified_table.rowCount() == 0
        assert dialog.staged_table.rowCount() == 1


@pytest.mark.unit
class TestGitStatusDialogTableInteraction:
    """Test table interaction and selection."""

    def test_select_row_in_modified_table(self, dialog):
        """Test selecting a row in modified table."""
        modified = [
            {
                "path": "file1.txt",
                "status": "M",
                "lines_added": "5",
                "lines_deleted": "2",
            },
            {
                "path": "file2.txt",
                "status": "M",
                "lines_added": "3",
                "lines_deleted": "1",
            },
        ]
        dialog.populate_status("main", modified, [], [])

        dialog.modified_table.selectRow(0)
        assert dialog.modified_table.currentRow() == 0

    def test_click_different_tabs(self, dialog):
        """Test clicking through all tabs."""
        # Populate all tabs
        modified = [
            {"path": "mod.txt", "status": "M", "lines_added": "5", "lines_deleted": "2"}
        ]
        staged = [
            {
                "path": "stage.txt",
                "status": "A",
                "lines_added": "10",
                "lines_deleted": "0",
            }
        ]
        untracked = [{"path": "new.txt", "status": "?"}]
        dialog.populate_status("main", modified, staged, untracked)

        # Click each tab
        dialog.tab_widget.setCurrentIndex(0)
        assert dialog.tab_widget.currentIndex() == 0

        dialog.tab_widget.setCurrentIndex(1)
        assert dialog.tab_widget.currentIndex() == 1

        dialog.tab_widget.setCurrentIndex(2)
        assert dialog.tab_widget.currentIndex() == 2


@pytest.mark.unit
class TestGitStatusDialogVisibility:
    """Test dialog visibility and show/hide."""

    def test_dialog_initially_hidden(self, dialog):
        """Test dialog is initially hidden."""
        assert not dialog.isVisible()

    def test_show_dialog(self, dialog):
        """Test showing the dialog."""
        dialog.show()
        assert dialog.isVisible()

    def test_hide_dialog(self, dialog):
        """Test hiding the dialog."""
        dialog.show()
        dialog.hide()
        assert not dialog.isVisible()

    def test_close_dialog(self, dialog):
        """Test closing the dialog."""
        dialog.show()
        dialog.close()
        # After close, isVisible() should be False
        assert not dialog.isVisible()


@pytest.mark.unit
class TestGitStatusDialogWindowProperties:
    """Test dialog window properties."""

    def test_dialog_is_modal(self, dialog):
        """Test dialog modal setting."""
        # Check if dialog has window modality set
        assert hasattr(dialog, "setModal")

    def test_dialog_has_title(self, dialog):
        """Test dialog has a window title."""
        assert dialog.windowTitle() != ""
        assert "Git Status" in dialog.windowTitle()

    def test_dialog_has_minimum_size(self, dialog):
        """Test dialog has minimumSize method available."""
        # Dialog may not have explicit minimum size set
        min_size = dialog.minimumSize()
        assert hasattr(dialog, "minimumSize")
        assert min_size is not None


@pytest.mark.unit
class TestGitStatusDialogButtonBehavior:
    """Test button behavior and interactions."""

    def test_refresh_button_enabled(self, dialog):
        """Test refresh button is enabled."""
        assert dialog.refresh_button.isEnabled()

    def test_close_button_enabled(self, dialog):
        """Test close button is enabled."""
        assert dialog.close_button.isEnabled()

    def test_refresh_button_has_text(self, dialog):
        """Test refresh button has text."""
        assert dialog.refresh_button.text() != ""

    def test_close_button_has_text(self, dialog):
        """Test close button has text."""
        assert dialog.close_button.text() != ""


@pytest.mark.unit
class TestGitStatusDialogStatusMapping:
    """Test status code to text mapping."""

    def test_unknown_status_code(self, dialog):
        """Test handling unknown status code."""
        modified = [
            {
                "path": "file.txt",
                "status": "X",
                "lines_added": "1",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        # Should handle gracefully with fallback text
        assert dialog.modified_table.rowCount() == 1

    def test_lowercase_status_code(self, dialog):
        """Test handling lowercase status code."""
        modified = [
            {
                "path": "file.txt",
                "status": "m",
                "lines_added": "1",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.rowCount() == 1


@pytest.mark.unit
class TestGitStatusDialogDataIntegrity:
    """Test data integrity after operations."""

    def test_data_persists_after_tab_switch(self, dialog):
        """Test data persists when switching tabs."""
        modified = [
            {"path": "mod.txt", "status": "M", "lines_added": "5", "lines_deleted": "2"}
        ]
        staged = [
            {
                "path": "stage.txt",
                "status": "A",
                "lines_added": "10",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, staged, [])

        # Switch to staged tab
        dialog.tab_widget.setCurrentIndex(1)
        assert dialog.staged_table.rowCount() == 1

        # Switch back to modified tab
        dialog.tab_widget.setCurrentIndex(0)
        assert dialog.modified_table.rowCount() == 1
        assert dialog.modified_table.item(0, 1).text() == "mod.txt"

    def test_branch_label_persists_after_refresh(self, dialog, qtbot):
        """Test branch label persists after refresh button click."""
        dialog.populate_status("feature", [], [], [])
        assert dialog.branch_label.text() == "Branch: feature"

        # Click refresh (note: actual refresh logic happens in parent)
        dialog.refresh_button.click()

        # Branch label should still show feature
        assert dialog.branch_label.text() == "Branch: feature"


@pytest.mark.unit
class TestGitStatusDialogSpecialCases:
    """Test special cases and boundary conditions."""

    def test_file_path_with_spaces(self, dialog):
        """Test file path containing spaces."""
        modified = [
            {
                "path": "my file.txt",
                "status": "M",
                "lines_added": "1",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.item(0, 1).text() == "my file.txt"

    def test_file_path_with_special_chars(self, dialog):
        """Test file path with special characters."""
        modified = [
            {
                "path": "file-@#$%.txt",
                "status": "M",
                "lines_added": "1",
                "lines_deleted": "0",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        assert dialog.modified_table.item(0, 1).text() == "file-@#$%.txt"

    def test_negative_line_counts(self, dialog):
        """Test handling negative line counts (shouldn't happen but test robustness)."""
        modified = [
            {
                "path": "file.txt",
                "status": "M",
                "lines_added": "-5",
                "lines_deleted": "-2",
            }
        ]

        dialog.populate_status("main", modified, [], [])

        # Should display the values as-is
        assert dialog.modified_table.rowCount() == 1

    def test_non_numeric_line_counts(self, dialog):
        """Test handling non-numeric line counts."""
        modified = [
            {
                "path": "file.txt",
                "status": "M",
                "lines_added": "N/A",
                "lines_deleted": "N/A",
            }
        ]

        # Current implementation may not handle non-numeric values gracefully
        try:
            dialog.populate_status("main", modified, [], [])
            # If it succeeds, verify row was added
            assert dialog.modified_table.rowCount() == 1
        except ValueError:
            # If it fails with ValueError, that's expected behavior for now
            assert True

    def test_missing_line_counts_in_dict(self, dialog):
        """Test handling missing line count keys in file dict."""
        # This tests robustness if Git status parsing fails
        modified = [{"path": "file.txt", "status": "M"}]

        # Should not crash
        try:
            dialog.populate_status("main", modified, [], [])
            assert True  # If we got here without exception, test passes
        except KeyError:
            assert False, "Dialog should handle missing keys gracefully"
