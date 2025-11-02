"""Tests for ui.editor_state module."""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_main_window(qapp):
    """Create a mock main window for EditorState."""
    return Mock()


class TestEditorState:
    """Test suite for EditorState."""

    def test_import(self):
        from asciidoc_artisan.ui.editor_state import EditorState
        assert EditorState is not None

    def test_creation(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState
        state = EditorState(mock_main_window)  # Requires main_window argument
        assert state is not None

    def test_state_tracking(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState
        state = EditorState(mock_main_window)  # Requires main_window argument
        # Should have attributes for tracking state
        attrs = [a for a in dir(state) if not a.startswith("_")]
        assert len(attrs) > 0
