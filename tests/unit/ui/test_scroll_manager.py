"""Tests for ui.scroll_manager module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestScrollManager:
    """Test suite for ScrollManager."""

    def test_import(self):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        assert ScrollManager is not None

    def test_creation(self):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager()
        assert manager is not None

    def test_scroll_sync_capability(self):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager()
        # Should have scroll synchronization methods
        methods = [m for m in dir(manager) if "scroll" in m.lower() or "sync" in m.lower()]
        assert len(methods) > 0
