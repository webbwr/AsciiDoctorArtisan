"""
Auto-complete manager for AsciiDoc Artisan (v2.0.0+).

This module coordinates auto-complete between the editor and popup widget.
Handles debouncing, context extraction, and completion insertion.

Key features:
- Automatic completion on typing (300ms debounce)
- Manual trigger with Ctrl+Space
- Context-aware completion (detects current line, cursor position)
- Smart text insertion (deletes word prefix, inserts completion)
- Configurable enable/disable and delay settings

Architecture:
    Editor textChanged → Debounce timer (300ms)
    → Extract context → Query engine → Show widget
    → User selects → Insert text → Hide widget

Example:
    ```python
    from asciidoc_artisan.ui.autocomplete_manager import AutoCompleteManager
    from asciidoc_artisan.core.autocomplete_engine import AutoCompleteEngine

    editor = QPlainTextEdit()
    engine = AutoCompleteEngine()
    engine.add_provider(SyntaxProvider())

    manager = AutoCompleteManager(editor, engine)
    manager.enabled = True  # Enable auto-complete

    # Manual trigger
    manager.trigger_manual()  # Show completions immediately
    ```
"""

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QPlainTextEdit

from asciidoc_artisan.core.autocomplete_engine import AutoCompleteEngine
from asciidoc_artisan.core.models import CompletionContext, CompletionItem
from asciidoc_artisan.ui.autocomplete_widget import AutoCompleteWidget


class AutoCompleteManager(QObject):
    """
    Manages auto-complete for editor.

    Coordinates completion between editor and popup widget. Handles
    debouncing for automatic completion, manual triggering, context
    extraction, and text insertion.

    Attributes:
        editor: Editor widget
        engine: Auto-complete engine
        widget: Popup completion widget
        enabled: Enable/disable auto-complete
        auto_delay: Debounce delay in milliseconds (default: 300ms)

    Settings:
        - autocomplete_enabled: bool (default: True)
        - autocomplete_delay: int (default: 300ms)
        - autocomplete_min_chars: int (default: 2)

    Performance:
        - Debounced to avoid excessive completions
        - <50ms completion query (cached)
        - No blocking operations

    Example:
        ```python
        manager = AutoCompleteManager(editor, engine)

        # Enable/disable
        manager.enabled = True

        # Configure delay
        manager.auto_delay = 500  # 500ms delay

        # Manual trigger (Ctrl+Space)
        manager.trigger_manual()
        ```
    """

    def __init__(self, editor: QPlainTextEdit, engine: AutoCompleteEngine) -> None:
        """
        Initialize auto-complete manager.

        Args:
            editor: Editor widget to attach auto-complete
            engine: Auto-complete engine with providers
        """
        super().__init__()
        self.editor = editor
        self.engine = engine
        self.widget = AutoCompleteWidget(editor)

        # Debounce timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._show_completions)

        # Settings
        self.enabled = True
        self._auto_delay = 300  # ms (private, use property)
        self.timer.setInterval(self._auto_delay)  # Initialize timer interval
        self.min_chars = 2  # Minimum characters to trigger auto-complete

        # Connect editor signals
        self.editor.textChanged.connect(self._on_text_changed)

        # Connect widget signals
        self.widget.item_selected.connect(self._insert_completion)
        self.widget.cancelled.connect(self._on_cancelled)

    @property
    def auto_delay(self) -> int:
        """
        Get auto-complete debounce delay in milliseconds.

        Returns:
            Delay in milliseconds (minimum 100ms)
        """
        return self._auto_delay

    @auto_delay.setter
    def auto_delay(self, value: int) -> None:
        """
        Set auto-complete debounce delay.

        Args:
            value: Delay in milliseconds (enforces minimum 100ms)
        """
        self._auto_delay = max(100, value)  # Enforce minimum 100ms
        self.timer.setInterval(self._auto_delay)

    def _on_text_changed(self) -> None:
        """
        Handle text change in editor.

        Restarts debounce timer for automatic completion. Only triggers
        if auto-complete is enabled and minimum character count is met.
        """
        if not self.enabled:
            return

        # Check minimum characters
        context = self._get_context()
        if len(context.word_before_cursor) < self.min_chars:
            self.widget.hide()
            self.timer.stop()
            return

        # Restart debounce timer
        self.timer.stop()
        self.timer.start(self.auto_delay)

    def _show_completions(self) -> None:
        """
        Show completion popup (automatic trigger).

        Extracts context, queries engine, and displays widget if
        completions are found.
        """
        # Get context
        context = self._get_context()

        # Get completions
        items = self.engine.get_completions(context, max_items=20)

        if items:
            # Position widget below cursor
            cursor_rect = self.editor.cursorRect()
            pos = self.editor.mapToGlobal(cursor_rect.bottomLeft())
            self.widget.move(pos)

            # Show widget
            self.widget.show_completions(items)
        else:
            # No completions - hide widget
            self.widget.hide()

    def trigger_manual(self) -> None:
        """
        Manually trigger completion (Ctrl+Space).

        Shows all available completions immediately without delay.
        Use for explicit user action (keyboard shortcut).

        Example:
            ```python
            # In main window
            def keyPressEvent(self, event):
                if event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.ControlModifier:
                    self.autocomplete_manager.trigger_manual()
            ```
        """
        context = self._get_context()
        context.manual = True  # Mark as manual trigger

        items = self.engine.get_completions(context, max_items=50)

        if items:
            cursor_rect = self.editor.cursorRect()
            pos = self.editor.mapToGlobal(cursor_rect.bottomLeft())
            self.widget.move(pos)
            self.widget.show_completions(items)

    def _get_context(self) -> CompletionContext:
        """
        Extract completion context from editor.

        Gets current cursor position, line text, and surrounding context
        for completion matching.

        Returns:
            CompletionContext with cursor position and line text
        """
        cursor = self.editor.textCursor()
        line_number = cursor.blockNumber()
        column = cursor.columnNumber()

        block = cursor.block()
        line = block.text()
        prefix = line[:column]

        return CompletionContext(
            line=line,
            line_number=line_number,
            column=column,
            prefix=prefix,
            trigger_char=prefix[-1] if prefix else None,
            manual=False,
        )

    def _insert_completion(self, item: CompletionItem) -> None:
        """
        Insert completion text into editor.

        Deletes the word before cursor and inserts the completion text.
        Uses insert_text if available, otherwise uses text.

        Args:
            item: Completion item to insert
        """
        cursor = self.editor.textCursor()

        # Delete word before cursor
        context = self._get_context()
        word = context.word_before_cursor
        for _ in range(len(word)):
            cursor.deletePreviousChar()

        # Insert completion text
        insert_text = item.insert_text if item.insert_text else item.text
        cursor.insertText(insert_text)

        self.editor.setTextCursor(cursor)

        # Hide widget
        self.widget.hide()

    def _on_cancelled(self) -> None:
        """
        Handle cancellation (Escape key).

        Returns focus to editor.
        """
        self.editor.setFocus()

    def hide_completions(self) -> None:
        """
        Hide completion widget.

        Use this to programmatically close the completion popup.

        Example:
            ```python
            # When editor loses focus
            def focusOutEvent(self, event):
                self.autocomplete_manager.hide_completions()
            ```
        """
        self.widget.hide()
        self.timer.stop()
