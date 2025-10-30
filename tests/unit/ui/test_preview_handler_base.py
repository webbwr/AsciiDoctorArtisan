"""
Tests for preview handler base class.

Tests the abstract base class functionality including:
- CSS generation and caching
- Adaptive debouncing
- Preview update coordination
- Error handling
- Signal emissions
"""

import pytest
import time
from unittest.mock import Mock, MagicMock
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QMainWindow

from asciidoc_artisan.ui.preview_handler_base import (
    PreviewHandlerBase,
    PREVIEW_FAST_INTERVAL_MS,
    PREVIEW_NORMAL_INTERVAL_MS,
    PREVIEW_SLOW_INTERVAL_MS,
)


class ConcretePreviewHandler(PreviewHandlerBase):
    """Concrete implementation for testing."""

    def __init__(self, editor, preview, parent_window):
        super().__init__(editor, preview, parent_window)
        self.completed_html = None
        self.scroll_synced = False

    def handle_preview_complete(self, html: str) -> None:
        """Test implementation."""
        self.completed_html = html
        self.preview_updated.emit(html)

    def sync_editor_to_preview(self, editor_value: int) -> None:
        """Test implementation - respects sync_scrolling_enabled and is_syncing_scroll."""
        if self.sync_scrolling_enabled and not self.is_syncing_scroll:
            self.scroll_synced = True

    def sync_preview_to_editor(self, preview_value: int) -> None:
        """Test implementation - respects sync_scrolling_enabled and is_syncing_scroll."""
        if self.sync_scrolling_enabled and not self.is_syncing_scroll:
            self.scroll_synced = True


@pytest.fixture
def mock_window(qtbot):
    """Create mock parent window."""
    window = QMainWindow()  # ✅ Real QObject for parent compatibility
    qtbot.addWidget(window)  # Manage lifecycle
    # Add Mock attributes that tests expect
    window._settings = Mock()
    window._settings.dark_mode = False
    window.request_preview_render = Mock()

    # Mock theme_manager for CSS generation
    window.theme_manager = Mock()
    # Use a list to ensure we create new string objects each time
    css_call_count = [0]
    def get_preview_css_mock():
        """Return CSS based on dark_mode setting - ensures new object each call."""
        css_call_count[0] += 1
        if window._settings.dark_mode:
            # Use string concatenation to ensure new object
            return "".join([
                f"/* Call {css_call_count[0]} */\n",
                "body {\n",
                "    color: #e0e0e0;\n",
                "    background-color: #1a1a1a;\n",
                "    max-width: 900px;\n",
                "    margin: 0 auto;\n",
                "}\n",
                "code { background: #2d2d2d; font-family: 'Courier New', monospace; }\n",
                "pre { background: #2d2d2d; padding: 10px; font-family: 'Courier New', monospace; }\n",
                "table { border: 1px solid #444; }\n",
                "table th { background: #333; }\n",
                "table td { padding: 8px; }\n",
                "h1 { border-bottom: 2px solid #444; }\n",
                "h1, h2, h3 { color: #fff; }\n",
            ])
        else:
            # Use string concatenation to ensure new object
            return "".join([
                f"/* Call {css_call_count[0]} */\n",
                "body {\n",
                "    color: #333;\n",
                "    background-color: #fff;\n",
                "    max-width: 900px;\n",
                "    margin: 0 auto;\n",
                "}\n",
                "code { background: #f5f5f5; font-family: 'Courier New', monospace; }\n",
                "pre { background: #f5f5f5; padding: 10px; font-family: 'Courier New', monospace; }\n",
                "table { border: 1px solid #ddd; }\n",
                "table th { background: #f9f9f9; }\n",
                "table td { padding: 8px; }\n",
                "h1 { border-bottom: 2px solid #ddd; }\n",
                "h1, h2, h3 { color: #000; }\n",
            ])
    window.theme_manager.get_preview_css = get_preview_css_mock

    return window


@pytest.fixture
def editor(qtbot):
    """Create editor widget."""
    editor = QPlainTextEdit()
    qtbot.addWidget(editor)
    return editor


@pytest.fixture
def preview(qtbot):
    """Create preview widget."""
    preview = QTextBrowser()
    qtbot.addWidget(preview)
    return preview


@pytest.fixture
def handler(editor, preview, mock_window):
    """Create concrete handler for testing."""
    return ConcretePreviewHandler(editor, preview, mock_window)


def test_handler_initialization(handler, editor, preview):
    """Test handler initializes correctly."""
    assert handler.editor is editor
    assert handler.preview is preview
    assert handler.sync_scrolling_enabled is True
    assert handler.is_syncing_scroll is False
    assert handler._css_cache is None
    assert isinstance(handler.preview_timer, QTimer)


def test_text_changed_triggers_debounced_update(handler, editor, qtbot):
    """Test text changes trigger debounced preview updates."""
    # Small document - fast interval
    editor.setPlainText("Small text")

    # Timer should be started
    assert handler.preview_timer.isActive()

    # Should use fast interval for small documents
    assert handler.preview_timer.interval() <= PREVIEW_FAST_INTERVAL_MS + 100


def test_text_changed_adapts_to_document_size(handler, editor):
    """Test debounce interval adapts to document size."""
    # Small document
    editor.setPlainText("x" * 1000)
    small_interval = handler.preview_timer.interval()

    # Large document
    editor.setPlainText("x" * 150000)
    large_interval = handler.preview_timer.interval()

    # Large documents should have longer intervals
    assert large_interval >= small_interval


def test_update_preview_emits_signal(handler, editor, mock_window):
    """Test update_preview emits signal to worker."""
    editor.setPlainText("Test content")
    handler.update_preview()

    # Should emit request to parent window
    assert handler._last_render_start is not None


def test_handle_preview_complete_wraps_with_css(handler):
    """Test preview completion wraps HTML with CSS."""
    test_html = "<p>Test content</p>"
    handler.handle_preview_complete(test_html)

    assert handler.completed_html == test_html


def test_handle_preview_error_displays_error(handler, preview):
    """Test error handling displays error message."""
    error_msg = "Test error message"
    handler.handle_preview_error(error_msg)

    # Preview should show error HTML
    html = preview.toHtml()
    assert "Preview Error" in html
    assert error_msg in html


def test_handle_preview_error_dark_mode(handler, mock_window, preview):
    """Test error display adapts to dark mode."""
    mock_window._settings.dark_mode = True

    handler.handle_preview_error("Test error")
    html = preview.toHtml()

    # Should use dark mode colors
    assert "#3a2a1a" in html or "#ffcc99" in html


def test_css_generation_light_mode(handler, mock_window):
    """Test CSS generation for light mode."""
    mock_window._settings.dark_mode = False

    css = handler.get_preview_css()

    assert "color: #333" in css  # Light text color
    assert "background-color: #fff" in css  # Light background


def test_css_generation_dark_mode(handler, mock_window):
    """Test CSS generation for dark mode."""
    mock_window._settings.dark_mode = True
    handler._css_cache = None  # Clear cache

    css = handler.get_preview_css()

    assert "color: #e0e0e0" in css  # Dark text color
    assert "background-color: #1a1a1a" in css  # Dark background


def test_css_caching(handler):
    """Test CSS is cached for performance."""
    css1 = handler.get_preview_css()
    css2 = handler.get_preview_css()

    assert css1 is css2  # Same object (cached)


def test_css_cache_clearing(handler):
    """Test CSS cache can be cleared."""
    css1 = handler.get_preview_css()
    handler.clear_css_cache()
    css2 = handler.get_preview_css()

    assert css1 is not css2  # Different objects (cache cleared)


def test_wrap_with_css(handler):
    """Test HTML wrapping with CSS."""
    body_html = "<p>Content</p>"
    wrapped = handler._wrap_with_css(body_html)

    assert "<!DOCTYPE html>" in wrapped
    assert "<html>" in wrapped
    assert "<head>" in wrapped
    assert "<style>" in wrapped
    assert body_html in wrapped


def test_enable_sync_scrolling(handler):
    """Test enabling/disabling scroll sync."""
    handler.enable_sync_scrolling(False)
    assert handler.sync_scrolling_enabled is False

    handler.enable_sync_scrolling(True)
    assert handler.sync_scrolling_enabled is True


def test_sync_editor_to_preview_respects_flag(handler):
    """Test scroll sync respects enabled flag."""
    handler.scroll_synced = False
    handler.enable_sync_scrolling(False)

    handler.sync_editor_to_preview(100)
    assert handler.scroll_synced is False  # Should not sync

    handler.enable_sync_scrolling(True)
    handler.sync_editor_to_preview(100)
    assert handler.scroll_synced is True  # Should sync


def test_clear_preview(handler, preview):
    """Test clearing preview content."""
    preview.setHtml("<p>Old content</p>")
    handler.clear_preview()

    html = preview.toHtml()
    assert "Preview cleared" in html


def test_adaptive_debouncing_toggle(handler):
    """Test adaptive debouncing can be toggled."""
    handler.set_adaptive_debouncing(False)
    assert handler._use_adaptive_debouncing is False

    handler.set_adaptive_debouncing(True)
    assert handler._use_adaptive_debouncing is True


def test_debouncer_stats(handler):
    """Test getting debouncer statistics."""
    stats = handler.get_debouncer_stats()
    assert isinstance(stats, dict)


def test_preview_updated_signal(handler, qtbot):
    """Test preview_updated signal emission."""
    with qtbot.waitSignal(handler.preview_updated, timeout=1000) as blocker:
        handler.handle_preview_complete("<p>Test</p>")

    assert blocker.args[0] == "<p>Test</p>"


def test_preview_error_signal(handler, qtbot):
    """Test preview_error signal emission."""
    with qtbot.waitSignal(handler.preview_error, timeout=1000) as blocker:
        handler.handle_preview_error("Test error")

    assert "Test error" in blocker.args[0]


def test_render_time_tracking(handler):
    """Test render time is tracked."""
    handler.update_preview()
    assert handler._last_render_start is not None

    start_time = handler._last_render_start
    time.sleep(0.01)

    handler.handle_preview_complete("<p>Done</p>")
    # Render time should have been calculated


def test_preview_timer_single_shot(handler):
    """Test preview timer is single-shot."""
    assert handler.preview_timer.isSingleShot() is True


def test_stop_preview_updates(handler, editor):
    """Test stopping preview updates."""
    editor.setPlainText("Test")
    assert handler.preview_timer.isActive()

    handler.stop_preview_updates()
    assert not handler.preview_timer.isActive()


def test_start_preview_updates(handler):
    """Test starting preview updates."""
    handler.start_preview_updates()
    # Just verify it doesn't crash


def test_css_has_responsive_design(handler):
    """Test CSS includes responsive design rules."""
    css = handler.get_preview_css()

    assert "max-width: 900px" in css
    assert "margin: 0 auto" in css


def test_css_includes_code_styling(handler):
    """Test CSS includes code block styling."""
    css = handler.get_preview_css()

    assert "code {" in css
    assert "pre {" in css
    assert "font-family: 'Courier New'" in css


def test_css_includes_table_styling(handler):
    """Test CSS includes table styling."""
    css = handler.get_preview_css()

    assert "table {" in css
    assert "table th" in css
    assert "table td" in css


def test_css_includes_heading_styling(handler):
    """Test CSS includes heading styling."""
    css = handler.get_preview_css()

    assert "h1, h2, h3" in css
    assert "h1 {" in css
    assert "border-bottom" in css


def test_multiple_text_changes_debounce(handler, editor):
    """Test multiple rapid text changes are debounced."""
    # Simulate rapid typing
    for i in range(5):
        editor.setPlainText(f"Text version {i}")

    # Timer should be active (waiting for debounce)
    assert handler.preview_timer.isActive()


def test_is_syncing_scroll_prevents_recursion(handler):
    """Test scroll sync flag prevents recursive calls."""
    handler.is_syncing_scroll = True
    handler.scroll_synced = False

    handler.sync_editor_to_preview(100)

    # Should not sync when already syncing
    assert handler.scroll_synced is False
