"""Tests for ui.status_manager module."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


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
        if hasattr(manager, "show_message"):
            manager.show_message("Test message")
            # Should not raise exception

    def test_extract_document_version(self):
        from asciidoc_artisan.ui.status_manager import extract_document_version
        # Test with version attribute
        text_with_version = ":version: 1.5.0\n\nContent"
        version = extract_document_version(text_with_version)
        assert version == "1.5.0" or "1.5.0" in version
