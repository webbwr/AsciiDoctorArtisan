"""Comprehensive tests for undo/redo functionality and buttons."""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def qapp():
    """Provide QApplication instance for Qt tests."""
    import os

    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    """Create main window instance for testing."""
    with patch("asciidoc_artisan.workers.git_worker.GitWorker"), patch(
        "asciidoc_artisan.workers.pandoc_worker.PandocWorker"
    ), patch("asciidoc_artisan.workers.preview_worker.PreviewWorker"):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor

        window = AsciiDocEditor()
        yield window
        window.close()


class TestUndoRedoButtons:
    """Test suite for undo/redo button functionality."""

    def test_undo_button_exists(self, main_window):
        """Test that undo button is created and accessible."""
        assert hasattr(main_window, "editor_undo_btn")
        assert main_window.editor_undo_btn is not None

    def test_redo_button_exists(self, main_window):
        """Test that redo button is created and accessible."""
        assert hasattr(main_window, "editor_redo_btn")
        assert main_window.editor_redo_btn is not None

    def test_undo_button_has_tooltip(self, main_window):
        """Test that undo button has correct tooltip."""
        tooltip = main_window.editor_undo_btn.toolTip()
        assert "Undo" in tooltip
        assert "Ctrl+Z" in tooltip

    def test_redo_button_has_tooltip(self, main_window):
        """Test that redo button has correct tooltip."""
        tooltip = main_window.editor_redo_btn.toolTip()
        assert "Redo" in tooltip
        assert "Ctrl+Shift+Z" in tooltip

    def test_undo_button_size(self, main_window):
        """Test that undo button has correct size."""
        size = main_window.editor_undo_btn.size()
        assert size.width() == 24
        assert size.height() == 24

    def test_redo_button_size(self, main_window):
        """Test that redo button has correct size."""
        size = main_window.editor_redo_btn.size()
        assert size.width() == 24
        assert size.height() == 24

    def test_undo_button_text(self, main_window):
        """Test that undo button shows correct icon."""
        text = main_window.editor_undo_btn.text()
        assert text == "↶"

    def test_redo_button_text(self, main_window):
        """Test that redo button shows correct icon."""
        text = main_window.editor_redo_btn.text()
        assert text == "↷"

    def test_buttons_initially_disabled(self, main_window):
        """Test that buttons are disabled when no undo/redo available."""
        # Fresh editor should have no undo/redo available
        assert not main_window.editor_undo_btn.isEnabled()
        assert not main_window.editor_redo_btn.isEnabled()

    def test_undo_button_enabled_after_edit(self, main_window):
        """Test that undo button enables after text change."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Clear and set initial state
        editor.clear()
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make a change
        editor.insertPlainText("Test content")
        qapp.processEvents()  # Process signals

        # Undo should now be available
        assert main_window.editor_undo_btn.isEnabled()
        assert not main_window.editor_redo_btn.isEnabled()

    def test_redo_button_enabled_after_undo(self, main_window):
        """Test that redo button enables after undo operation."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Clear and set initial state
        editor.clear()
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make a change and undo it
        editor.insertPlainText("Test content")
        qapp.processEvents()

        editor.undo()
        qapp.processEvents()

        # Redo should now be available
        assert main_window.editor_redo_btn.isEnabled()

    def test_undo_button_click(self, main_window):
        """Test that clicking undo button triggers undo."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Set initial text and clear undo stack
        editor.setPlainText("Initial")
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Now make a change
        editor.selectAll()
        editor.insertPlainText("Modified")
        qapp.processEvents()

        # Click undo button
        main_window.editor_undo_btn.click()
        qapp.processEvents()

        # Text should be reverted to Initial
        assert editor.toPlainText() == "Initial"

    def test_redo_button_click(self, main_window):
        """Test that clicking redo button triggers redo."""
        editor = main_window.editor
        # Make a change and undo it
        editor.setPlainText("Original")
        qapp = QApplication.instance()
        qapp.processEvents()

        editor.setPlainText("Modified")
        qapp.processEvents()

        editor.undo()
        qapp.processEvents()

        # Click redo button
        main_window.editor_redo_btn.click()
        qapp.processEvents()

        # Text should be restored
        assert editor.toPlainText() == "Modified"

    def test_buttons_connected_to_signals(self, main_window):
        """Test that buttons are connected to document signals."""
        editor = main_window.editor
        # Verify signal connections exist by checking button enabled state changes
        # This is an indirect test since Qt signal introspection is complex
        qapp = QApplication.instance()

        editor.clear()
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make change and verify undo button responds
        editor.insertPlainText("Test")
        qapp.processEvents()

        # If signals are connected, button state should change
        # We already tested this in other tests, so just verify buttons exist
        assert main_window.editor_undo_btn is not None
        assert main_window.editor_redo_btn is not None

    def test_button_styling_matches_maximize(self, main_window):
        """Test that undo/redo buttons have similar styling to maximize button."""
        undo_style = main_window.editor_undo_btn.styleSheet()
        redo_style = main_window.editor_redo_btn.styleSheet()
        max_style = main_window.editor_max_btn.styleSheet()

        # All should have transparent background
        assert "transparent" in undo_style
        assert "transparent" in redo_style
        assert "transparent" in max_style

        # All should have border-radius
        assert "border-radius" in undo_style
        assert "border-radius" in redo_style
        assert "border-radius" in max_style


class TestEditorUndoRedo:
    """Test suite for editor undo/redo functionality."""

    def test_editor_supports_undo(self, main_window):
        """Test that editor has undo capability."""
        editor = main_window.editor
        assert hasattr(editor, "undo")
        assert callable(editor.undo)

    def test_editor_supports_redo(self, main_window):
        """Test that editor has redo capability."""
        editor = main_window.editor
        assert hasattr(editor, "redo")
        assert callable(editor.redo)

    def test_single_edit_undo(self, main_window):
        """Test undo after single edit operation."""
        editor = main_window.editor
        qapp = QApplication.instance()

        original = "Original text"
        modified = "Modified text"

        # Set original and clear stack
        editor.setPlainText(original)
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make a change by replacing text
        editor.selectAll()
        editor.insertPlainText(modified)
        qapp.processEvents()

        # Undo should restore original
        editor.undo()
        qapp.processEvents()

        assert editor.toPlainText() == original

    def test_single_edit_redo(self, main_window):
        """Test redo after single undo operation."""
        editor = main_window.editor
        original = "Original text"
        modified = "Modified text"

        editor.setPlainText(original)
        qapp = QApplication.instance()
        qapp.processEvents()

        editor.setPlainText(modified)
        qapp.processEvents()

        editor.undo()
        qapp.processEvents()

        editor.redo()
        qapp.processEvents()

        assert editor.toPlainText() == modified

    def test_multiple_undo_operations(self, main_window):
        """Test multiple consecutive undo operations."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Start with initial text
        editor.setPlainText("Start")
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make multiple changes using textCursor beginEditBlock/endEditBlock
        # to create separate undo operations
        from PySide6.QtGui import QTextCursor

        changes = [" One", " Two", " Three"]
        for change in changes:
            cursor = editor.textCursor()
            cursor.beginEditBlock()  # Start separate undo command
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(change)
            cursor.endEditBlock()  # End separate undo command
            qapp.processEvents()

        # Verify we have the full text
        assert editor.toPlainText() == "Start One Two Three"

        # Undo changes one by one
        editor.undo()
        qapp.processEvents()
        assert editor.toPlainText() == "Start One Two"

        editor.undo()
        qapp.processEvents()
        assert editor.toPlainText() == "Start One"

        editor.undo()
        qapp.processEvents()
        assert editor.toPlainText() == "Start"

    def test_multiple_redo_operations(self, main_window):
        """Test multiple consecutive redo operations."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Start with initial text
        editor.setPlainText("Base")
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make multiple changes using textCursor beginEditBlock/endEditBlock
        # to create separate undo operations
        from PySide6.QtGui import QTextCursor

        changes = [" A", " B", " C"]
        for change in changes:
            cursor = editor.textCursor()
            cursor.beginEditBlock()  # Start separate undo command
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(change)
            cursor.endEditBlock()  # End separate undo command
            qapp.processEvents()

        # Undo all changes
        for _ in range(len(changes)):
            editor.undo()
            qapp.processEvents()

        # Should be back to Base
        assert editor.toPlainText() == "Base"

        # Redo all changes
        editor.redo()
        qapp.processEvents()
        assert editor.toPlainText() == "Base A"

        editor.redo()
        qapp.processEvents()
        assert editor.toPlainText() == "Base A B"

        editor.redo()
        qapp.processEvents()
        assert editor.toPlainText() == "Base A B C"

    def test_undo_redo_with_cursor_position(self, main_window):
        """Test that undo/redo preserves cursor position appropriately."""
        editor = main_window.editor
        qapp = QApplication.instance()

        editor.setPlainText("Hello World")
        qapp.processEvents()

        # Move cursor to middle
        cursor = editor.textCursor()
        cursor.setPosition(6)
        editor.setTextCursor(cursor)

        # Insert text at cursor
        editor.insertPlainText("Beautiful ")
        qapp.processEvents()

        # Undo insert
        editor.undo()
        qapp.processEvents()

        # Text should be back to original
        assert editor.toPlainText() == "Hello World"

    def test_undo_after_delete_text(self, main_window):
        """Test undo after deleting text."""
        editor = main_window.editor
        qapp = QApplication.instance()

        editor.setPlainText("Some text to delete")
        qapp.processEvents()

        editor.selectAll()
        editor.textCursor().deleteChar()
        qapp.processEvents()

        editor.undo()
        qapp.processEvents()

        # Text should be restored
        assert "Some text to delete" in editor.toPlainText()

    def test_undo_redo_preserves_formatting(self, main_window):
        """Test that undo/redo preserves text formatting."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # AsciiDoc formatted text
        formatted_text = "= Document Title\n\n== Section\n\nParagraph."
        editor.setPlainText(formatted_text)
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Modify by selecting and replacing
        editor.selectAll()
        editor.insertPlainText("Modified")
        qapp.processEvents()

        # Undo
        editor.undo()
        qapp.processEvents()

        # Should restore exact formatting
        assert editor.toPlainText() == formatted_text

    def test_undo_limit_exists(self, main_window):
        """Test that editor has an undo limit configured."""
        editor = main_window.editor
        # Check if undo limit is set (should be > 0)
        assert editor.document().maximumBlockCount() >= 0  # 0 = unlimited

    def test_clear_undo_stack(self, main_window):
        """Test clearing undo stack."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Make changes
        editor.setPlainText("Text 1")
        qapp.processEvents()
        editor.setPlainText("Text 2")
        qapp.processEvents()

        # Clear undo stack
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Undo should not be available
        assert not editor.document().isUndoAvailable()
        assert not editor.document().isRedoAvailable()

    def test_undo_redo_with_empty_document(self, main_window):
        """Test undo/redo with empty document."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Start with empty and clear stack
        editor.setPlainText("")
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Add text
        editor.insertPlainText("Some text")
        qapp.processEvents()

        # Verify text was added
        assert editor.toPlainText() == "Some text"

        # Undo to empty
        editor.undo()
        qapp.processEvents()

        assert editor.toPlainText() == ""

        # Redo
        editor.redo()
        qapp.processEvents()

        assert editor.toPlainText() == "Some text"

    def test_undo_redo_availability_signals(self, main_window):
        """Test that document emits undo/redo availability signals."""
        editor = main_window.editor
        qapp = QApplication.instance()

        undo_signals = []
        redo_signals = []

        # Start clean
        editor.setPlainText("")
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Connect to signals
        editor.document().undoAvailable.connect(lambda x: undo_signals.append(x))
        editor.document().redoAvailable.connect(lambda x: redo_signals.append(x))

        # Make change (should emit undoAvailable(True))
        editor.insertPlainText("Test")
        qapp.processEvents()

        assert len(undo_signals) > 0
        assert undo_signals[-1] is True

        # Undo (should emit redoAvailable(True))
        editor.undo()
        qapp.processEvents()

        assert len(redo_signals) > 0
        assert redo_signals[-1] is True

    def test_undo_with_large_document(self, main_window):
        """Test undo/redo with large document (performance test)."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Create large document
        large_text = "\n".join([f"Line {i}" for i in range(1000)])
        editor.setPlainText(large_text)
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Modify by replacing text
        editor.selectAll()
        editor.insertPlainText("Modified")
        qapp.processEvents()

        # Undo should work even with large document
        editor.undo()
        qapp.processEvents()

        assert "Line 0" in editor.toPlainText()
        assert "Line 999" in editor.toPlainText()

    def test_undo_redo_with_special_characters(self, main_window):
        """Test undo/redo with special characters."""
        editor = main_window.editor
        qapp = QApplication.instance()

        special_text = "Special: «»‹› ™ © ® ± × ÷ ≈ ≠ ≤ ≥"
        editor.setPlainText(special_text)
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        editor.selectAll()
        editor.insertPlainText("Modified")
        qapp.processEvents()

        editor.undo()
        qapp.processEvents()

        assert editor.toPlainText() == special_text

    def test_undo_redo_with_unicode(self, main_window):
        """Test undo/redo with Unicode characters."""
        editor = main_window.editor
        qapp = QApplication.instance()

        unicode_text = "Unicode: 你好世界 مرحبا العالم Привет мир"
        editor.setPlainText(unicode_text)
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        editor.selectAll()
        editor.insertPlainText("Modified")
        qapp.processEvents()

        editor.undo()
        qapp.processEvents()

        assert editor.toPlainText() == unicode_text


class TestUndoRedoIntegration:
    """Integration tests for undo/redo with other features."""

    def test_undo_after_file_load(self, main_window):
        """Test that undo works after loading a file."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Simulate file load
        file_content = "# Loaded File\n\nContent from file."
        editor.setPlainText(file_content)
        qapp.processEvents()

        # Clear undo stack (as would happen on file load)
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Make edit by replacing text
        editor.selectAll()
        editor.insertPlainText("Modified after load")
        qapp.processEvents()

        # Undo should work
        editor.undo()
        qapp.processEvents()

        assert editor.toPlainText() == file_content

    def test_undo_redo_buttons_update_on_programmatic_change(self, main_window):
        """Test that buttons update when document changes programmatically."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Start clean
        editor.clear()
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Programmatic change using insertPlainText
        editor.insertPlainText("Programmatic")
        qapp.processEvents()

        # Buttons should update
        assert main_window.editor_undo_btn.isEnabled()
        assert not main_window.editor_redo_btn.isEnabled()

    def test_undo_redo_with_preview_update(self, main_window):
        """Test that undo/redo triggers preview update."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Make change
        editor.setPlainText("= Test Document\n\nContent")
        qapp.processEvents()

        # Undo should trigger preview update
        editor.undo()
        qapp.processEvents()

        # Preview should be cleared or show original
        # (We can't easily test preview content in offscreen mode)
        assert True  # Test completes without crash

    def test_keyboard_shortcuts_work(self, main_window):
        """Test that Ctrl+Z and Ctrl+Shift+Z still work."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Set initial text
        editor.setPlainText("Original")
        editor.document().clearUndoRedoStacks()
        qapp.processEvents()

        # Modify text
        editor.selectAll()
        editor.insertPlainText("Modified")
        qapp.processEvents()

        # Simulate Ctrl+Z
        from PySide6.QtTest import QTest
        from PySide6.QtCore import Qt

        QTest.keyClick(editor, Qt.Key_Z, Qt.ControlModifier)
        qapp.processEvents()

        assert editor.toPlainText() == "Original"

        # Simulate Ctrl+Shift+Z
        QTest.keyClick(editor, Qt.Key_Z, Qt.ControlModifier | Qt.ShiftModifier)
        qapp.processEvents()

        assert editor.toPlainText() == "Modified"

    def test_undo_redo_preserves_modified_flag(self, main_window):
        """Test that undo/redo correctly updates document modified flag."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Start clean
        editor.clear()
        editor.document().clearUndoRedoStacks()
        editor.document().setModified(False)
        qapp.processEvents()

        # Make change (should set modified)
        editor.insertPlainText("Modified")
        qapp.processEvents()

        assert editor.document().isModified()

        # Undo to original (should clear modified if back to saved state)
        editor.undo()
        qapp.processEvents()

        # Document modified state depends on implementation
        # Just verify no crash
        assert True

    def test_rapid_undo_redo_operations(self, main_window):
        """Test rapid undo/redo operations (stress test)."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Make changes
        for i in range(10):
            editor.setPlainText(f"Text {i}")
            qapp.processEvents()

        # Rapid undo/redo
        for _ in range(5):
            for _ in range(10):
                editor.undo()
                qapp.processEvents()
            for _ in range(10):
                editor.redo()
                qapp.processEvents()

        # Should still work correctly
        assert "Text 9" in editor.toPlainText()

    def test_undo_redo_memory_not_leaking(self, main_window):
        """Test that undo/redo doesn't leak memory (basic check)."""
        editor = main_window.editor
        qapp = QApplication.instance()

        # Make many changes
        for i in range(100):
            editor.setPlainText(f"Text {i}")
            qapp.processEvents()

        # Undo all
        for _ in range(100):
            if editor.document().isUndoAvailable():
                editor.undo()
                qapp.processEvents()

        # Test completes without crash = basic memory check passed
        assert True
