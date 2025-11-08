"""
Auto-complete popup widget for AsciiDoc Artisan (v2.0.0+).

This module provides a popup list widget for displaying completion items.
Supports keyboard navigation (Up/Down, Enter, Escape) and mouse selection.

Key features:
- VSCode-style popup list below cursor
- Keyboard navigation with Up/Down arrows
- Enter to select, Escape to cancel
- Mouse click to select
- Shows item details in tooltip
- Auto-hides when selection made

Architecture:
    User types → AutoCompleteManager → show_completions()
    → AutoCompleteWidget displays items → User selects
    → item_selected Signal → Manager inserts text

Example:
    ```python
    from asciidoc_artisan.ui.autocomplete_widget import AutoCompleteWidget
    from asciidoc_artisan.core.models import CompletionItem, CompletionKind

    widget = AutoCompleteWidget(parent_editor)
    widget.item_selected.connect(lambda item: print(f"Selected: {item.text}"))

    items = [
        CompletionItem(text="= Heading", kind=CompletionKind.SYNTAX),
        CompletionItem(text="== Section", kind=CompletionKind.SYNTAX),
    ]

    widget.show_completions(items)
    ```
"""

from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget

from asciidoc_artisan.core.models import CompletionItem


class AutoCompleteWidget(QListWidget):
    """
    Popup list widget for displaying completion items.

    Displays completion items in a popup list below the editor cursor.
    Supports keyboard navigation (Up/Down, Enter, Escape) and mouse
    selection. Auto-hides when item selected or cancelled.

    Signals:
        item_selected: Emitted when user selects a completion item
        cancelled: Emitted when user cancels (Escape key)

    Attributes:
        items: Current list of completion items displayed

    UI Behavior:
        - Enter/Return: Select current item
        - Escape: Cancel and hide
        - Up/Down: Navigate list
        - Click: Select item
        - Other keys: Pass through to editor

    Example:
        ```python
        widget = AutoCompleteWidget(editor)
        widget.item_selected.connect(on_item_selected)
        widget.cancelled.connect(on_cancelled)

        # Show completions
        widget.show_completions([
            CompletionItem(text="= Title", kind=CompletionKind.SYNTAX),
            CompletionItem(text="== Section", kind=CompletionKind.SYNTAX),
        ])
        ```
    """

    # Signals
    item_selected = Signal(CompletionItem)  # User selected a completion
    cancelled = Signal()  # User cancelled (Escape)

    def __init__(self, parent: QWidget) -> None:
        """
        Initialize auto-complete widget.

        Args:
            parent: Parent widget (usually the editor)
        """
        super().__init__(parent)
        self.items: List[CompletionItem] = []

        # Configure widget appearance
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMaximumHeight(200)
        self.setMinimumWidth(300)

        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)

        # Hide by default
        self.hide()

    def show_completions(self, items: List[CompletionItem]) -> None:
        """
        Show completion items in popup.

        Clears existing items, populates list with new items, and displays
        the widget. Automatically selects first item.

        Args:
            items: List of completion items to display

        Example:
            ```python
            widget.show_completions([
                CompletionItem(text="[source]", kind=CompletionKind.SYNTAX),
                CompletionItem(text="[quote]", kind=CompletionKind.SYNTAX),
            ])
            ```
        """
        self.items = items
        self.clear()

        for item in items:
            list_item = QListWidgetItem(item.text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)  # Store CompletionItem

            # Set tooltip with detail and documentation
            tooltip = item.detail
            if item.documentation:
                tooltip += f"\n\n{item.documentation}"
            list_item.setToolTip(tooltip)

            self.addItem(list_item)

        if items:
            self.setCurrentRow(0)
            self.show()
            self.setFocus()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle keyboard navigation.

        Keyboard shortcuts:
        - Enter/Return: Select current item and hide
        - Escape: Cancel and hide
        - Up/Down: Navigate list
        - Other keys: Pass through to parent editor

        Args:
            event: Qt key event
        """
        key = event.key()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Select current item
            current = self.currentItem()
            if current:
                item = current.data(Qt.ItemDataRole.UserRole)
                self.item_selected.emit(item)
                self.hide()
        elif key == Qt.Key.Key_Escape:
            # Cancel
            self.cancelled.emit()
            self.hide()
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            # Navigate list
            super().keyPressEvent(event)
        else:
            # Pass to parent editor
            parent = self.parent()
            if parent:
                parent.keyPressEvent(event)

    def _on_item_clicked(self, list_item: QListWidgetItem) -> None:
        """
        Handle item click (mouse selection).

        Emits item_selected signal and hides widget.

        Args:
            list_item: Qt list item that was clicked
        """
        item = list_item.data(Qt.ItemDataRole.UserRole)
        self.item_selected.emit(item)
        self.hide()
