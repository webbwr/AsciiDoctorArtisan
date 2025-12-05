"""
Contextual Help - F1 help system for context-sensitive assistance.

Provides:
- F1 key triggers help for focused widget
- Contextual help based on cursor position
- Quick reference popups
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Help content for different contexts
CONTEXT_HELP = {
    "editor": {
        "title": "AsciiDoc Editor",
        "content": """
<h3>Editor Shortcuts</h3>
<table>
<tr><td><b>Ctrl+Space</b></td><td>Trigger auto-complete</td></tr>
<tr><td><b>Ctrl+Z/Y</b></td><td>Undo/Redo</td></tr>
<tr><td><b>Ctrl+F</b></td><td>Find in document</td></tr>
<tr><td><b>Ctrl+H</b></td><td>Find and replace</td></tr>
<tr><td><b>F7</b></td><td>Toggle spell check</td></tr>
<tr><td><b>F8</b></td><td>Jump to next syntax error</td></tr>
</table>

<h3>AsciiDoc Quick Reference</h3>
<pre>
= Document Title     (Level 0 heading)
== Section           (Level 1 heading)
=== Subsection       (Level 2 heading)

*bold*  _italic_  `monospace`

.Block title
----
Code block
----

* Bullet list
. Numbered list

image::file.png[Alt text]
link:url[Link text]
</pre>
""",
    },
    "preview": {
        "title": "Document Preview",
        "content": """
<h3>Preview Pane</h3>
<p>Shows a live rendering of your AsciiDoc document.</p>

<h3>Features</h3>
<ul>
<li><b>Auto-refresh:</b> Updates as you type</li>
<li><b>Sync scrolling:</b> Follows editor position</li>
<li><b>GPU accelerated:</b> Smooth rendering</li>
</ul>

<h3>Tips</h3>
<ul>
<li>Click links to open in browser</li>
<li>Use View → Maximize Preview for full screen</li>
<li>Toggle dark mode with F11</li>
</ul>
""",
    },
    "chat": {
        "title": "AI Chat Assistant",
        "content": """
<h3>AI Chat</h3>
<p>Ask questions about AsciiDoc or get help with your document.</p>

<h3>Context Modes</h3>
<ul>
<li><b>Document:</b> AI sees your entire document</li>
<li><b>Selection:</b> AI sees selected text only</li>
<li><b>General:</b> No document context</li>
</ul>

<h3>Example Questions</h3>
<ul>
<li>"How do I create a table?"</li>
<li>"Convert this to a numbered list"</li>
<li>"Explain this error message"</li>
<li>"Suggest a better heading"</li>
</ul>
""",
    },
    "find_bar": {
        "title": "Find & Replace",
        "content": """
<h3>Find Shortcuts</h3>
<table>
<tr><td><b>F3</b></td><td>Find next</td></tr>
<tr><td><b>Shift+F3</b></td><td>Find previous</td></tr>
<tr><td><b>Ctrl+H</b></td><td>Show replace</td></tr>
<tr><td><b>Escape</b></td><td>Close find bar</td></tr>
</table>

<h3>Options</h3>
<ul>
<li><b>Match Case:</b> Case-sensitive search</li>
<li><b>Whole Word:</b> Match complete words only</li>
<li><b>Regex:</b> Use regular expressions</li>
</ul>
""",
    },
    "git": {
        "title": "Git Integration",
        "content": """
<h3>Git Shortcuts</h3>
<table>
<tr><td><b>Ctrl+G</b></td><td>Quick commit</td></tr>
<tr><td><b>Ctrl+Shift+G</b></td><td>Commit dialog</td></tr>
</table>

<h3>Workflow</h3>
<ol>
<li>Edit your document</li>
<li>Press Ctrl+G for quick commit</li>
<li>Enter a commit message</li>
<li>Use Git → Push to sync</li>
</ol>
""",
    },
    "default": {
        "title": "AsciiDoc Artisan Help",
        "content": """
<h3>Quick Start</h3>
<ol>
<li>Write AsciiDoc in the editor (left)</li>
<li>See live preview (right)</li>
<li>Use AI chat for help (sidebar)</li>
</ol>

<h3>Key Shortcuts</h3>
<table>
<tr><td><b>Ctrl+N</b></td><td>New file</td></tr>
<tr><td><b>Ctrl+O</b></td><td>Open file</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save file</td></tr>
<tr><td><b>Ctrl+F</b></td><td>Find</td></tr>
<tr><td><b>F1</b></td><td>Context help</td></tr>
<tr><td><b>F11</b></td><td>Toggle dark mode</td></tr>
</table>

<p>Press F1 while focused on any widget for specific help.</p>
""",
    },
}


class HelpDialog(QDialog):
    """Dialog for displaying contextual help."""

    def __init__(self, title: str, content: str, parent: QWidget | None = None) -> None:
        """Initialize help dialog."""
        super().__init__(parent)
        self.setWindowTitle(f"Help: {title}")
        self.setMinimumSize(450, 400)
        self._setup_ui(title, content)

    def _setup_ui(self, title: str, content: str) -> None:
        """Set up dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(f"<h2>{title}</h2>")
        layout.addWidget(title_label)

        # Content browser
        browser = QTextBrowser()
        browser.setHtml(content)
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class ContextualHelp(QObject):
    """
    Manages F1 contextual help system.

    Features:
    - F1 shows help for focused widget
    - Context-aware help content
    - Quick reference popups
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize contextual help manager."""
        super().__init__(editor)
        self.editor = editor

    def show_help_for_widget(self, widget: QWidget | None = None) -> None:
        """Show help for the specified or focused widget."""
        if widget is None:
            widget = QApplication.focusWidget()

        context = self._determine_context(widget)
        help_data = CONTEXT_HELP.get(context, CONTEXT_HELP["default"])

        dialog = HelpDialog(help_data["title"], help_data["content"], self.editor)
        dialog.exec()

    def _determine_context(self, widget: QWidget | None) -> str:
        """Determine help context from widget."""
        if widget is None:
            return "default"

        # Check widget identity
        if widget is self.editor.editor or self._is_child_of(widget, self.editor.editor):
            return "editor"

        if widget is self.editor.preview or self._is_child_of(widget, self.editor.preview):
            return "preview"

        if hasattr(self.editor, "chat_bar"):
            if widget is self.editor.chat_bar or self._is_child_of(widget, self.editor.chat_bar):
                return "chat"

        if hasattr(self.editor, "chat_panel"):
            if widget is self.editor.chat_panel or self._is_child_of(widget, self.editor.chat_panel):
                return "chat"

        if hasattr(self.editor, "find_bar"):
            if widget is self.editor.find_bar or self._is_child_of(widget, self.editor.find_bar):
                return "find_bar"

        if hasattr(self.editor, "quick_commit_widget"):
            if widget is self.editor.quick_commit_widget or self._is_child_of(widget, self.editor.quick_commit_widget):
                return "git"

        return "default"

    def _is_child_of(self, widget: QWidget, parent: QWidget) -> bool:
        """Check if widget is a child of parent."""
        current = widget.parent()
        while current is not None:
            if current is parent:
                return True
            current = current.parent() if hasattr(current, "parent") else None
        return False

    def show_quick_tip(self, text: str, widget: QWidget | None = None) -> None:
        """Show a quick tooltip near widget."""
        if widget is None:
            widget = QApplication.focusWidget()

        if widget:
            pos = widget.mapToGlobal(QPoint(10, widget.height()))
            QToolTip.showText(pos, text, widget, widget.rect(), 5000)
