"""
Toolbar Factory - Creates styled toolbars and buttons for panes.

Extracted from UISetupManager to reduce class size (MA principle).
Handles creation of toolbars with labels, undo/redo/commit/maximize buttons.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

if TYPE_CHECKING:  # pragma: no cover
    from .main_window import AsciiDocEditor

# UI Color Constants
SEPARATOR_BACKGROUND_COLOR = "rgba(128, 128, 128, 0.1)"
SEPARATOR_BORDER_COLOR = "#888"


class ToolbarFactory:
    """
    Factory for creating styled toolbars and buttons.

    This class was extracted from UISetupManager to reduce class size
    per MA principle (511→253 lines).

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the ToolbarFactory with a reference to the main editor."""
        self.editor = editor

    def _create_toolbar_widget(self) -> QWidget:
        """
        Create toolbar widget with styling.

        Returns:
            Styled toolbar widget

        MA principle: Extracted from _create_toolbar (7 lines).
        """
        toolbar = QWidget()
        toolbar.setFixedHeight(30)
        toolbar.setStyleSheet(
            f"background-color: {SEPARATOR_BACKGROUND_COLOR}; border-bottom: 1px solid {SEPARATOR_BORDER_COLOR};"
        )
        return toolbar

    def _create_toolbar_label(self, label_text: str, color: str, pane_name: str) -> QLabel:
        """
        Create and store toolbar label.

        Args:
            label_text: Text for the label
            color: Label color
            pane_name: Pane name for reference storage

        Returns:
            Styled QLabel

        MA principle: Extracted from _create_toolbar (13 lines).
        """
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Store label reference in editor for theme updates
        if pane_name == "editor":
            self.editor.editor_label = label
        elif pane_name == "preview":
            self.editor.preview_label = label
        elif pane_name == "chat":
            self.editor.chat_label = label

        return label

    def _create_undo_button(self, color: str, highlight_color: str) -> QPushButton:
        """
        Create undo button with styling.

        Args:
            color: Button border and text color
            highlight_color: Hover background color

        Returns:
            Styled undo button

        MA principle: Extracted from _create_toolbar (28 lines).
        """
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
        return undo_btn

    def _create_redo_button(self, color: str, highlight_color: str) -> QPushButton:
        """
        Create redo button with styling.

        Args:
            color: Button border and text color
            highlight_color: Hover background color

        Returns:
            Styled redo button

        MA principle: Extracted from _create_toolbar (28 lines).
        """
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
        return redo_btn

    def _create_commit_button(self, color: str, highlight_color: str) -> QPushButton:
        """
        Create quick commit button with styling.

        Args:
            color: Button border and text color
            highlight_color: Hover background color

        Returns:
            Styled commit button

        MA principle: Extracted from _create_toolbar (29 lines).
        """
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
        return commit_btn

    def _create_maximize_button(self, color: str, highlight_color: str, pane_name: str) -> QPushButton:
        """
        Create maximize button with styling.

        Args:
            color: Button border and text color
            highlight_color: Hover background color
            pane_name: Pane name for maximize callback

        Returns:
            Styled maximize button

        MA principle: Extracted from _create_toolbar (23 lines).
        """
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
        return max_btn

    def _store_button_reference(self, button: QPushButton, pane_name: str, button_type: str) -> None:
        """
        Store button reference in editor.

        Args:
            button: Button to store
            pane_name: Pane name ("editor", "preview", "chat")
            button_type: Button type ("max", "undo", "redo", "commit")

        MA principle: Extracted from _create_toolbar (7 lines).
        """
        ref_name = f"{pane_name}_{button_type}_btn"
        setattr(self.editor, ref_name, button)

    def create_toolbar(self, label_text: str, color: str, pane_name: str, highlight_color: str) -> QWidget:
        """
        Create a toolbar with label and buttons.

        Args:
            label_text: Text for the toolbar label
            color: Color for the label and button border
            pane_name: Name of the pane (for maximize callback)
            highlight_color: Color for button hover effect

        Returns:
            QWidget containing the toolbar

        MA principle: Reduced from 162→40 lines by extracting 7 helper methods.
        """
        # Create toolbar widget and layout
        toolbar = self._create_toolbar_widget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)

        # Add label with stretch
        label = self._create_toolbar_label(label_text, color, pane_name)
        toolbar_layout.addWidget(label)
        toolbar_layout.addStretch()

        # Add editor-specific buttons (undo/redo/commit)
        if pane_name == "editor":
            undo_btn = self._create_undo_button(color, highlight_color)
            toolbar_layout.addWidget(undo_btn)
            self._store_button_reference(undo_btn, pane_name, "undo")

            redo_btn = self._create_redo_button(color, highlight_color)
            toolbar_layout.addWidget(redo_btn)
            self._store_button_reference(redo_btn, pane_name, "redo")

            commit_btn = self._create_commit_button(color, highlight_color)
            toolbar_layout.addWidget(commit_btn)
            self.editor.quick_commit_btn = commit_btn

        # Add maximize button
        max_btn = self._create_maximize_button(color, highlight_color, pane_name)
        toolbar_layout.addWidget(max_btn)
        self._store_button_reference(max_btn, pane_name, "max")

        return toolbar
