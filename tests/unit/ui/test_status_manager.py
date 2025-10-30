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
        from unittest.mock import patch
        # Need to add status_bar attribute for StatusManager
        from PySide6.QtWidgets import QStatusBar
        main_window.status_bar = QStatusBar()
        main_window.setStatusBar(main_window.status_bar)

        manager = StatusManager(main_window)
        # Mock QMessageBox to prevent blocking on exec()
        with patch('asciidoc_artisan.ui.status_manager.QMessageBox') as mock_msgbox:
            # show_message signature: (level, title, text) from status_manager.py:109
            manager.show_message("info", "Test Title", "Test message")
            # Verify QMessageBox was created but don't let it block
            mock_msgbox.assert_called_once()

    def test_extract_document_version(self, main_window):
        from asciidoc_artisan.ui.status_manager import StatusManager
        from PySide6.QtWidgets import QStatusBar
        main_window.status_bar = QStatusBar()
        main_window.setStatusBar(main_window.status_bar)

        manager = StatusManager(main_window)
        # extract_document_version is a method, not standalone function
        text_with_version = ":version: 1.5.0\n\nContent"
        version = manager.extract_document_version(text_with_version)
        assert version == "1.5.0"
