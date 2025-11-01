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
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import (
    EDITOR_FONT_FAMILY,
    EDITOR_FONT_SIZE,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)
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
        # This allows us to add chat components below the splitter
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter (editor + preview)
        self.editor.splitter = QSplitter(Qt.Orientation.Horizontal, self.editor)

        # Setup editor pane
        editor_container = self._create_editor_pane()
        self.editor.splitter.addWidget(editor_container)

        # Setup preview pane
        preview_container = self._create_preview_pane()
        self.editor.splitter.addWidget(preview_container)

        # Configure splitter
        self.editor.splitter.setStretchFactor(0, 1)
        self.editor.splitter.setStretchFactor(1, 1)

        # Set default 50/50 split - ensure both panes visible
        # This will be overridden by saved settings if they exist
        QTimer.singleShot(0, lambda: self.editor.splitter.setSizes([400, 400]))

        # Add splitter to main layout
        main_layout.addWidget(self.editor.splitter, 1)  # Stretch factor 1

        # Create chat panel (initially hidden, shown when AI enabled)
        from .chat_panel_widget import ChatPanelWidget
        self.editor.chat_panel = ChatPanelWidget(self.editor)
        self.editor.chat_panel.setMaximumHeight(300)  # Limit height to 300px
        self.editor.chat_panel.hide()  # Hidden by default
        main_layout.addWidget(self.editor.chat_panel, 0)  # No stretch

        # Create chat bar (initially hidden, shown when AI enabled + model set)
        from .chat_bar_widget import ChatBarWidget
        self.editor.chat_bar = ChatBarWidget(self.editor)
        self.editor.chat_bar.hide()  # Hidden by default
        main_layout.addWidget(self.editor.chat_bar, 0)  # No stretch

        # Set main container as central widget
        self.editor.setCentralWidget(main_container)

        # Setup synchronized scrolling
        self.editor._setup_synchronized_scrolling()

        # Setup status bar
        self.editor.status_bar = QStatusBar(self.editor)
        self.editor.setStatusBar(self.editor.status_bar)

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
        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        self.editor.editor.setFont(font)
        self.editor.editor.textChanged.connect(self.editor._start_preview_timer)
        editor_layout.addWidget(self.editor.editor)

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

        # Create preview widget (QTextBrowser for WSLg compatibility)
        self.editor.preview = QTextBrowser(self.editor)
        self.editor.preview.setOpenExternalLinks(True)
        logger.info("Using QTextBrowser for WSLg compatibility (no WebEngine)")
        preview_layout.addWidget(self.editor.preview)

        return preview_container

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
            f"background-color: {SEPARATOR_BACKGROUND_COLOR}; "
            f"border-bottom: 1px solid {SEPARATOR_BORDER_COLOR};"
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
        else:
            self.editor.preview_label = label

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
                background-color: {highlight_color.replace('0.2', '0.3')};
            }}
        """
        )
        max_btn.clicked.connect(lambda: self.editor._toggle_pane_maximize(pane_name))
        toolbar_layout.addWidget(max_btn)

        # Store button reference in editor
        if pane_name == "editor":
            self.editor.editor_max_btn = max_btn
        else:
            self.editor.preview_max_btn = max_btn

        return toolbar

    def setup_dynamic_sizing(self) -> None:
        """Set up window to dynamically resize based on screen size."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()

            # Calculate dimensions (80% of available space)
            width = int(available.width() * 0.8)
            height = int(available.height() * 0.8)

            # Ensure minimum size
            width = max(width, MIN_WINDOW_WIDTH)
            height = max(height, MIN_WINDOW_HEIGHT)

            # Center window on screen
            x = available.x() + (available.width() - width) // 2
            y = available.y() + (available.height() - height) // 2

            # Apply geometry if not maximized
            if not self.editor._start_maximized:
                if self.editor._initial_geometry:
                    self.editor.setGeometry(self.editor._initial_geometry)
                else:
                    self.editor.setGeometry(x, y, width, height)
            else:
                self.editor.showMaximized()
