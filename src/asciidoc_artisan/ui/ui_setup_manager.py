"""
UI Setup Manager - Handles main window UI initialization.

Implements:
- Editor/Preview pane setup
- Toolbar creation
- Widget layout and styling
- Splitter configuration

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import (
    EDITOR_FONT_FAMILY,
    EDITOR_FONT_SIZE,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)
from asciidoc_artisan.ui.find_bar_widget import FindBarWidget
from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
from asciidoc_artisan.ui.toolbar_factory import ToolbarFactory

if TYPE_CHECKING:  # pragma: no cover
    from .main_window import AsciiDocEditor

import logging

logger = logging.getLogger(__name__)

# UI Color Constants
SEPARATOR_BACKGROUND_COLOR = "rgba(128, 128, 128, 0.1)"
SEPARATOR_BORDER_COLOR = "#888"
EDITOR_HIGHLIGHT_COLOR_ADD = "rgba(74, 222, 128, 0.2)"
EDITOR_HIGHLIGHT_HOVER_ADD = "rgba(74, 222, 128, 0.3)"
PREVIEW_HIGHLIGHT_COLOR_ADD = "rgba(74, 158, 255, 0.2)"
PREVIEW_HIGHLIGHT_HOVER_ADD = "rgba(74, 158, 255, 0.3)"


class UISetupManager:
    """Manages main window UI initialization and setup.

    This class encapsulates all UI setup logic for the main editor window,
    including editor/preview panes, toolbars, and layout configuration.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """
        Initialize the UISetupManager with a reference to the main editor.

        MA principle: Delegates toolbar creation to ToolbarFactory (extracted class).
        """
        self.editor = editor
        self._toolbar_factory = ToolbarFactory(editor)

    def setup_ui(self) -> None:
        """
        Set up the complete UI including editor, preview, chat, and toolbars.

        MA principle: Reduced from 67→16 lines by extracting 4 helper methods.
        """
        self.editor.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        main_container, main_layout = self._setup_main_container()
        self._setup_main_splitter(main_layout)
        self._setup_auxiliary_widgets(main_layout)

        self.editor.setCentralWidget(main_container)
        self.editor._setup_synchronized_scrolling()

        self._setup_status_bar()
        self.setup_dynamic_sizing()

    def _setup_main_container(self) -> tuple[QWidget, QVBoxLayout]:
        """Create main container widget and layout."""
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        return main_container, main_layout

    def _setup_main_splitter(self, main_layout: QVBoxLayout) -> None:
        """Create and configure main splitter with editor, preview, and chat panes."""
        # Create main splitter (editor + preview + chat)
        self.editor.splitter = QSplitter(Qt.Orientation.Horizontal, self.editor)

        # Setup panes
        self.editor.splitter.addWidget(self._create_editor_pane())
        self.editor.splitter.addWidget(self._create_preview_pane())
        self.editor.splitter.addWidget(self._create_chat_pane())

        # Configure splitter stretch factors - all panes user-resizable
        self.editor.splitter.setStretchFactor(0, 2)  # Editor (2/5 when chat visible)
        self.editor.splitter.setStretchFactor(1, 2)  # Preview (2/5 when chat visible)
        self.editor.splitter.setStretchFactor(2, 1)  # Chat (1/5 when visible, user-resizable)

        # Set default proportional splits
        # Will be overridden by saved settings if they exist
        QTimer.singleShot(0, lambda: self._set_default_splitter_sizes())

        # Add splitter to main layout
        main_layout.addWidget(self.editor.splitter, 1)  # Stretch factor 1

    def _setup_auxiliary_widgets(self, main_layout: QVBoxLayout) -> None:
        """Setup find bar and quick commit widget."""
        # Setup find bar (hidden by default, shown with Ctrl+F)
        self.editor.find_bar = FindBarWidget(self.editor)
        main_layout.addWidget(self.editor.find_bar)

        # Setup quick commit widget (hidden by default, shown with Ctrl+G, v1.9.0+)
        from .quick_commit_widget import QuickCommitWidget

        self.editor.quick_commit_widget = QuickCommitWidget(self.editor)
        main_layout.addWidget(self.editor.quick_commit_widget)

    def _setup_status_bar(self) -> None:
        """Setup and initialize status bar."""
        self.editor.status_bar = QStatusBar(self.editor)
        self.editor.setStatusBar(self.editor.status_bar)

        # Clear status bar on startup
        self.editor.status_bar.clearMessage()

        # Initialize status manager widgets now that status bar exists
        self.editor.status_manager.initialize_widgets()

    def _create_editor_pane(self) -> QWidget:
        """Create the editor pane with toolbar and text editor.

        Returns:
            QWidget containing editor pane
        """
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # Create toolbar
        editor_toolbar = self._toolbar_factory.create_toolbar("Editor", "#4ade80", "editor", EDITOR_HIGHLIGHT_COLOR_ADD)
        editor_layout.addWidget(editor_toolbar)

        # Create text editor
        self.editor.editor = LineNumberPlainTextEdit(self.editor)

        # Initialize extra selection lists for combining highlights
        self.editor.editor.spell_check_selections = []
        self.editor.editor.search_selections = []

        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        self.editor.editor.setFont(font)
        self.editor.editor.textChanged.connect(self.editor._start_preview_timer)
        editor_layout.addWidget(self.editor.editor)

        # Connect undo/redo buttons to editor (now that editor exists)
        self.editor.editor_undo_btn.clicked.connect(self.editor.editor.undo)
        self.editor.editor_redo_btn.clicked.connect(self.editor.editor.redo)

        # Update button states when undo/redo availability changes
        self.editor.editor.document().undoAvailable.connect(self.editor.editor_undo_btn.setEnabled)
        self.editor.editor.document().redoAvailable.connect(self.editor.editor_redo_btn.setEnabled)

        # Set initial button states
        self.editor.editor_undo_btn.setEnabled(self.editor.editor.document().isUndoAvailable())
        self.editor.editor_redo_btn.setEnabled(self.editor.editor.document().isRedoAvailable())

        return editor_container

    def _create_preview_pane(self) -> QWidget:
        """Create the preview pane with toolbar and preview widget.

        Returns:
            QWidget containing preview pane
        """
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        # Create toolbar
        preview_toolbar = self._toolbar_factory.create_toolbar(
            "Preview", "#4a9eff", "preview", PREVIEW_HIGHLIGHT_COLOR_ADD
        )
        preview_layout.addWidget(preview_toolbar)

        # Create preview widget with automatic GPU detection
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        self.editor.preview = create_preview_widget(self.editor)

        # Only QTextBrowser has setOpenExternalLinks, not QWebEngineView
        if hasattr(self.editor.preview, "setOpenExternalLinks"):
            self.editor.preview.setOpenExternalLinks(True)

        preview_layout.addWidget(self.editor.preview)

        return preview_container

    def _create_chat_pane(self) -> QWidget:
        """Create the chat pane with toolbar, chat panel, and chat bar.

        Returns:
            QWidget containing chat pane
        """
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Set minimum and maximum width constraints for chat pane
        # Min: 250px (enough for controls), Max: 600px (not too wide)
        chat_container.setMinimumWidth(250)
        chat_container.setMaximumWidth(600)

        # Create toolbar
        chat_toolbar = self._toolbar_factory.create_toolbar("AI Chat", "#ff9800", "chat", "rgba(255, 152, 0, 0.2)")
        chat_layout.addWidget(chat_toolbar)

        # Create chat panel (message display)
        from .chat_panel_widget import ChatPanelWidget

        self.editor.chat_panel = ChatPanelWidget(self.editor)
        chat_layout.addWidget(self.editor.chat_panel, 1)  # Stretch to fill

        # Create chat bar (input controls) at bottom
        from .chat_bar_widget import ChatBarWidget

        self.editor.chat_bar = ChatBarWidget(self.editor)
        self.editor.chat_bar.setMinimumHeight(70)  # Two rows: controls + input
        chat_layout.addWidget(self.editor.chat_bar, 0)  # No stretch

        # Store reference to chat container for visibility control
        self.editor.chat_container = chat_container

        # Initially hide chat pane (will be shown when AI enabled)
        chat_container.hide()

        return chat_container

    def _set_default_splitter_sizes(self) -> None:
        """Set default splitter sizes based on window width and chat visibility."""
        # Get current window width
        window_width = self.editor.width()

        # Check if chat is visible
        chat_visible = hasattr(self.editor, "chat_container") and self.editor.chat_container.isVisible()

        if chat_visible:
            # Proportional: 2/5 editor, 2/5 preview, 1/5 chat
            editor_width = int(window_width * 0.4)
            preview_width = int(window_width * 0.4)
            chat_width = int(window_width * 0.2)
            self.editor.splitter.setSizes([editor_width, preview_width, chat_width])
            logger.info(f"Default sizes (with chat): {editor_width}, {preview_width}, {chat_width}")
        else:
            # Without chat: 1/2 editor, 1/2 preview, 0 chat
            editor_width = int(window_width * 0.5)
            preview_width = int(window_width * 0.5)
            self.editor.splitter.setSizes([editor_width, preview_width, 0])
            logger.info(f"Default sizes (no chat): {editor_width}, {preview_width}, 0")

    def setup_dynamic_sizing(self) -> None:
        """Set up window to dynamically resize based on screen size."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()

            # Start maximized by default (user preference)
            # Override with saved settings if not maximized
            if self.editor._start_maximized:
                self.editor.showMaximized()
            else:
                # Calculate dimensions (80% of available space)
                width = int(available.width() * 0.8)
                height = int(available.height() * 0.8)

                # Ensure minimum size
                width = max(width, MIN_WINDOW_WIDTH)
                height = max(height, MIN_WINDOW_HEIGHT)

                # Center window on screen
                x = available.x() + (available.width() - width) // 2
                y = available.y() + (available.height() - height) // 2

                # Apply saved geometry or calculated geometry
                if self.editor._initial_geometry:
                    self.editor.setGeometry(self.editor._initial_geometry)
                else:
                    self.editor.setGeometry(x, y, width, height)
