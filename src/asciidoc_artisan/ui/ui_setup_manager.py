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
    QHBoxLayout,
    QLabel,
    QPushButton,
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

if TYPE_CHECKING:
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
        """Initialize the UISetupManager with a reference to the main editor."""
        self.editor = editor

    def setup_ui(self) -> None:
        """Set up the complete UI including editor, preview, chat, and toolbars."""
        # Set minimum window size
        self.editor.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Create main container widget and layout
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter (editor + preview + chat)
        self.editor.splitter = QSplitter(Qt.Orientation.Horizontal, self.editor)

        # Setup editor pane
        editor_container = self._create_editor_pane()
        self.editor.splitter.addWidget(editor_container)

        # Setup preview pane
        preview_container = self._create_preview_pane()
        self.editor.splitter.addWidget(preview_container)

        # Setup chat pane (persistent right pane)
        chat_container = self._create_chat_pane()
        self.editor.splitter.addWidget(chat_container)

        # Configure splitter stretch factors - all panes user-resizable
        self.editor.splitter.setStretchFactor(0, 2)  # Editor (2/5 when chat visible)
        self.editor.splitter.setStretchFactor(1, 2)  # Preview (2/5 when chat visible)
        self.editor.splitter.setStretchFactor(
            2, 1
        )  # Chat (1/5 when visible, user-resizable)

        # Set default proportional splits
        # Will be overridden by saved settings if they exist
        QTimer.singleShot(0, lambda: self._set_default_splitter_sizes())

        # Add splitter to main layout
        main_layout.addWidget(self.editor.splitter, 1)  # Stretch factor 1

        # Setup find bar (hidden by default, shown with Ctrl+F)
        self.editor.find_bar = FindBarWidget(self.editor)
        main_layout.addWidget(self.editor.find_bar)

        # Setup quick commit widget (hidden by default, shown with Ctrl+G, v1.9.0+)
        from .quick_commit_widget import QuickCommitWidget

        self.editor.quick_commit_widget = QuickCommitWidget(self.editor)
        main_layout.addWidget(self.editor.quick_commit_widget)

        # Set main container as central widget
        self.editor.setCentralWidget(main_container)

        # Setup synchronized scrolling
        self.editor._setup_synchronized_scrolling()

        # Setup status bar
        self.editor.status_bar = QStatusBar(self.editor)
        self.editor.setStatusBar(self.editor.status_bar)

        # Clear status bar on startup
        self.editor.status_bar.clearMessage()

        # Initialize status manager widgets now that status bar exists
        self.editor.status_manager.initialize_widgets()

        # Setup dynamic window sizing
        self.setup_dynamic_sizing()

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
        editor_toolbar = self._create_toolbar(
            "Editor", "#4ade80", "editor", EDITOR_HIGHLIGHT_COLOR_ADD
        )
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
        self.editor.editor.document().undoAvailable.connect(
            self.editor.editor_undo_btn.setEnabled
        )
        self.editor.editor.document().redoAvailable.connect(
            self.editor.editor_redo_btn.setEnabled
        )

        # Set initial button states
        self.editor.editor_undo_btn.setEnabled(
            self.editor.editor.document().isUndoAvailable()
        )
        self.editor.editor_redo_btn.setEnabled(
            self.editor.editor.document().isRedoAvailable()
        )

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
        preview_toolbar = self._create_toolbar(
            "Preview", "#4a9eff", "preview", PREVIEW_HIGHLIGHT_COLOR_ADD
        )
        preview_layout.addWidget(preview_toolbar)

        # Create preview widget with automatic GPU detection
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        self.editor.preview = create_preview_widget(self.editor)
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
        chat_toolbar = self._create_toolbar(
            "AI Chat", "#ff9800", "chat", "rgba(255, 152, 0, 0.2)"
        )
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

    def _create_toolbar(
        self, label_text: str, color: str, pane_name: str, highlight_color: str
    ) -> QWidget:
        """Create a toolbar with label and maximize button.

        Args:
            label_text: Text for the toolbar label
            color: Color for the label and button border
            pane_name: Name of the pane (for maximize callback)
            highlight_color: Color for button hover effect

        Returns:
            QWidget containing the toolbar
        """
        toolbar = QWidget()
        toolbar.setFixedHeight(30)
        toolbar.setStyleSheet(
            f"background-color: {SEPARATOR_BACKGROUND_COLOR}; border-bottom: 1px solid {SEPARATOR_BORDER_COLOR};"
        )
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)

        # Create label
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {color}; font-weight: bold;")
        toolbar_layout.addWidget(label)
        toolbar_layout.addStretch()

        # Store label reference in editor for theme updates
        if pane_name == "editor":
            self.editor.editor_label = label
        elif pane_name == "preview":
            self.editor.preview_label = label
        elif pane_name == "chat":
            self.editor.chat_label = label

        # Add undo/redo buttons for editor pane only
        if pane_name == "editor":
            # Undo button
            undo_btn = QPushButton("↶")
            undo_btn.setFixedSize(24, 24)
            undo_btn.setToolTip("Undo (Ctrl+Z)")
            undo_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {color};
                    border-radius: 3px;
                    padding: 2px;
                    color: {color};
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {highlight_color};
                    border-color: {color};
                }}
                QPushButton:pressed {{
                    background-color: {highlight_color.replace("0.2", "0.3")};
                }}
                QPushButton:disabled {{
                    color: {color.replace(")", ", 0.3)")};
                    border-color: {color.replace(")", ", 0.3)")};
                }}
            """
            )
            toolbar_layout.addWidget(undo_btn)
            self.editor.editor_undo_btn = undo_btn

            # Redo button
            redo_btn = QPushButton("↷")
            redo_btn.setFixedSize(24, 24)
            redo_btn.setToolTip("Redo (Ctrl+Shift+Z)")
            redo_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {color};
                    border-radius: 3px;
                    padding: 2px;
                    color: {color};
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {highlight_color};
                    border-color: {color};
                }}
                QPushButton:pressed {{
                    background-color: {highlight_color.replace("0.2", "0.3")};
                }}
                QPushButton:disabled {{
                    color: {color.replace(")", ", 0.3)")};
                    border-color: {color.replace(")", ", 0.3)")};
                }}
            """
            )
            toolbar_layout.addWidget(redo_btn)
            self.editor.editor_redo_btn = redo_btn

            # Quick commit button (v1.9.0+)
            commit_btn = QPushButton("✓")
            commit_btn.setFixedSize(24, 24)
            commit_btn.setToolTip("Quick Commit (Ctrl+G)")
            commit_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {color};
                    border-radius: 3px;
                    padding: 2px;
                    color: {color};
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {highlight_color};
                    border-color: {color};
                }}
                QPushButton:pressed {{
                    background-color: {highlight_color.replace("0.2", "0.3")};
                }}
                QPushButton:disabled {{
                    color: {color.replace(")", ", 0.3)")};
                    border-color: {color.replace(")", ", 0.3)")};
                }}
            """
            )
            commit_btn.clicked.connect(self.editor._show_quick_commit)
            toolbar_layout.addWidget(commit_btn)
            self.editor.quick_commit_btn = commit_btn

        # Create maximize button
        max_btn = QPushButton("⬜")
        max_btn.setFixedSize(24, 24)
        max_btn.setToolTip(f"Maximize {pane_name}")
        max_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {color};
                border-radius: 3px;
                padding: 2px;
                color: {color};
            }}
            QPushButton:hover {{
                background-color: {highlight_color};
                border-color: {color};
            }}
            QPushButton:pressed {{
                background-color: {highlight_color.replace("0.2", "0.3")};
            }}
        """
        )
        max_btn.clicked.connect(lambda: self.editor._toggle_pane_maximize(pane_name))
        toolbar_layout.addWidget(max_btn)

        # Store button reference in editor
        if pane_name == "editor":
            self.editor.editor_max_btn = max_btn
        elif pane_name == "preview":
            self.editor.preview_max_btn = max_btn
        elif pane_name == "chat":
            self.editor.chat_max_btn = max_btn

        return toolbar

    def _set_default_splitter_sizes(self) -> None:
        """Set default splitter sizes based on window width and chat visibility."""
        # Get current window width
        window_width = self.editor.width()

        # Check if chat is visible
        chat_visible = (
            hasattr(self.editor, "chat_container")
            and self.editor.chat_container.isVisible()
        )

        if chat_visible:
            # Proportional: 2/5 editor, 2/5 preview, 1/5 chat
            editor_width = int(window_width * 0.4)
            preview_width = int(window_width * 0.4)
            chat_width = int(window_width * 0.2)
            self.editor.splitter.setSizes([editor_width, preview_width, chat_width])
            logger.info(
                f"Default sizes (with chat): {editor_width}, {preview_width}, {chat_width}"
            )
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
