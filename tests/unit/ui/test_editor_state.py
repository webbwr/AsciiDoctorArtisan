"""Tests for ui.editor_state module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestEditorState:
    """Test suite for EditorState."""

    def test_import(self):
        from asciidoc_artisan.ui.editor_state import EditorState
        assert EditorState is not None

    def test_creation(self):
        from asciidoc_artisan.ui.editor_state import EditorState
        state = EditorState()
        assert state is not None

    def test_state_tracking(self):
        from asciidoc_artisan.ui.editor_state import EditorState
        state = EditorState()
        # Should have attributes for tracking state
        attrs = [a for a in dir(state) if not a.startswith("_")]
        assert len(attrs) > 0
