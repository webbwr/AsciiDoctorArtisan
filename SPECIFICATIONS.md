# AsciiDoc Artisan Specifications

**v2.1.0** | **109 FRs** | **Specification-Driven Coding**

---

## [SPEC] Code Generation Guide

```yaml
# AI INSTRUCTION: Use this document to generate code
# Sections marked [SPEC] are machine-parseable
# Generate code matching these exact patterns

code_generation:
  schemas: docs/SCHEMAS.md      # Pydantic models
  signals: docs/SIGNALS.md      # Qt signal contracts
  patterns: this_file           # Critical patterns below

imports:
  typing: "from typing import Any"
  pyside6: "from PySide6.QtCore import QThread, Signal"
  pathlib: "from pathlib import Path"
  dataclass: "from dataclasses import dataclass"
```

---

## [SPEC] Metrics

```yaml
version: 2.1.0
release_date: 2025-12-05

codebase:
  lines: 46457
  files: 180

testing:
  unit_tests: 5628
  e2e_tests: 17
  integration_tests: 17
  coverage: 95%

performance:
  startup_target: "<1.0s"
  startup_actual: "0.27s"
  preview_target: "<200ms"
  autocomplete_target: "<50ms"

storage:
  format: TOON
  fallback: JSON
  migration: automatic
```

---

## [SPEC] Worker Template

```python
# TEMPLATE: Generate workers using this pattern
# File: workers/{name}_worker.py

from PySide6.QtCore import QThread, Signal
from typing import Any

class {Name}Worker(QThread):
    """Worker for {description}."""

    # Define signals
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._cancelled = False
        self._queue: list[Any] = []

    def run(self) -> None:
        """Main worker loop."""
        while not self._cancelled:
            if not self._queue:
                self.msleep(10)
                continue
            item = self._queue.pop(0)
            try:
                result = self._process(item)
                self.result_ready.emit(result)
            except Exception as e:
                self.error_occurred.emit(str(e))

    def _process(self, item: Any) -> Any:
        """Override in subclass."""
        raise NotImplementedError

    def cancel(self) -> None:
        """Cancel worker."""
        self._cancelled = True

    def queue_request(self, item: Any) -> None:
        """Add item to queue."""
        self._queue.append(item)
```

---

## [SPEC] Handler Template

```python
# TEMPLATE: Generate handlers using this pattern
# File: ui/{name}_handler.py

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class {Name}Handler(QObject):
    """Handler for {description}."""

    # Signals
    operation_complete = Signal(object)
    operation_failed = Signal(str)

    def __init__(self, editor: "AsciiDocEditor") -> None:
        super().__init__(editor)
        self.editor = editor
        self._is_processing = False

    def do_operation(self) -> None:
        """Execute operation with reentrancy guard."""
        if self._is_processing:
            logger.warning("Operation already in progress")
            return

        self._is_processing = True
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            self.operation_failed.emit(str(e))
        finally:
            self._is_processing = False
```

---

## [SPEC] Atomic Write Pattern

```python
# TEMPLATE: All file writes must use this pattern
# File: core/file_operations.py

from pathlib import Path
from asciidoc_artisan.core import toon_utils

def atomic_save_text(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """Atomic text save: temp file + rename."""
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding=encoding) as f:
            f.write(content)
        temp_path.replace(file_path)
        return True
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        return False

def atomic_save_toon(file_path: Path, data: dict, indent: int = 2) -> bool:
    """Atomic TOON save: 30-60% smaller than JSON."""
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            toon_utils.dump(data, f, indent=indent)
        temp_path.replace(file_path)
        return True
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        return False
```

---

## [SPEC] Subprocess Safety

```python
# TEMPLATE: All subprocess calls must use this pattern
# NEVER use shell=True

import subprocess
from typing import list

def safe_subprocess(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Execute subprocess safely with shell=False."""
    result = subprocess.run(
        cmd,
        shell=False,  # REQUIRED: Never True
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr

# CORRECT:
subprocess.run(["git", "commit", "-m", message], shell=False)

# WRONG - NEVER DO THIS:
# subprocess.run(f"git commit -m {message}", shell=True)
```

---

## [SPEC] Test Template

```python
# TEMPLATE: Generate tests using this pattern
# File: tests/unit/{module}/test_{name}.py

import pytest
from unittest.mock import MagicMock, patch

class Test{Name}:
    """Test suite for {Name}."""

    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return {Name}()

    def test_basic_operation(self, instance):
        """Test basic functionality."""
        result = instance.do_operation()
        assert result is not None

    def test_error_handling(self, instance):
        """Test error cases."""
        with pytest.raises(ValueError):
            instance.do_invalid_operation()

    @pytest.mark.parametrize("input,expected", [
        ("valid", True),
        ("invalid", False),
    ])
    def test_parameterized(self, instance, input, expected):
        """Test multiple inputs."""
        result = instance.validate(input)
        assert result == expected
```

---

## [SPEC] Directory Structure

```yaml
# AI: Generate files in these locations

src/asciidoc_artisan/:
  core/:           # Business logic (no Qt)
    - settings.py
    - toon_utils.py
    - file_operations.py
    - *_models.py

  ui/:             # Qt widgets and handlers
    - main_window.py
    - *_handler.py
    - *_manager.py
    - *_widget.py
    - *_dialog.py

  workers/:        # QThread workers
    - base_worker.py
    - *_worker.py

  lsp/:            # Language Server Protocol
    - server.py
    - *_provider.py

tests/:
  unit/:           # Unit tests mirror src/ structure
  e2e/:            # End-to-end tests
  conftest.py      # Shared fixtures
```

---

## [SPEC] Error Codes

```yaml
# Use these codes in SyntaxErrorModel.code field

syntax_errors:
  E001: "Unclosed source block"
  E002: "Unclosed example block"
  E003: "Unclosed sidebar block"
  E004: "Unclosed quote block"
  E005: "Unclosed literal block"
  E006: "Unclosed table"
  E007: "Unclosed open block"
  E008: "Invalid heading level (only = to ======)"
  E009: "Duplicate anchor ID"
  E010: "Invalid block delimiter length"

semantic_errors:
  E100: "Broken cross-reference"
  E101: "Include file not found"
  E102: "Invalid include path"
  E103: "Circular include detected"
  E104: "Unknown attribute"

warnings:
  W001: "Heading level skipped"
  W002: "Empty section"
  W003: "Missing document title"
  W004: "Line exceeds 120 characters"
  W005: "Trailing whitespace"

info:
  I001: "Consider using semantic heading"
  I002: "Block could benefit from title"
  I003: "Consider using include directive"
```

---

## [SPEC] Functional Requirements

### Core Editor (FR-001 to FR-005)

```yaml
FR-001:
  name: Text Editor
  file: ui/main_window.py
  widget: QPlainTextEdit
  features: [syntax_highlight, line_wrap, tab_handling]

FR-002:
  name: Line Numbers
  file: ui/line_number_area.py
  class: LineNumberArea
  parent: QWidget

FR-003:
  name: Undo/Redo
  implementation: Qt built-in
  shortcuts: [Ctrl+Z, Ctrl+Y]

FR-004:
  name: Font Configuration
  file: core/settings.py
  fields: [editor_font_family, editor_font_size]

FR-005:
  name: State Persistence
  file: core/settings.py
  format: TOON
  migration: JSON to TOON automatic
```

### File Operations (FR-006 to FR-014)

```yaml
FR-006:
  name: Open File
  shortcut: Ctrl+O
  handler: ui/file_open_handler.py
  pattern: atomic_read

FR-007:
  name: Save File
  shortcut: Ctrl+S
  handler: ui/file_save_handler.py
  pattern: atomic_save_text

FR-008:
  name: Save As
  shortcut: Ctrl+Shift+S
  handler: ui/file_save_handler.py

FR-009:
  name: New File
  shortcut: Ctrl+N
  handler: ui/file_handler.py

FR-010:
  name: Recent Files
  file: core/recent_templates_tracker.py
  max_items: 10
  format: TOON

FR-011:
  name: Auto-Save
  file: ui/file_handler.py
  default_interval: 300  # seconds
  configurable: true
```

### Preview (FR-015 to FR-020)

```yaml
FR-015:
  name: Live Preview
  target: "<200ms"
  file: workers/preview_worker.py

FR-016:
  name: GPU Acceleration
  file: ui/preview_handler_gpu.py
  speedup: "10-50x"
  fallback: QTextBrowser

FR-017:
  name: Scroll Sync
  file: ui/preview_handler_base.py
  mode: bidirectional

FR-018:
  name: Incremental Rendering
  file: workers/incremental_renderer.py
  cache: LRU(100)

FR-019:
  name: Debounce
  file: ui/preview_handler_base.py
  delay: 300ms

FR-020:
  name: Theme Support
  file: ui/theme_manager.py
  method: CSS injection
```

### Git (FR-026 to FR-033)

```yaml
FR-026:
  name: Repo Detection
  file: ui/git_handler.py
  method: ".git directory check"

FR-027:
  name: Commit
  file: workers/git_worker.py
  signal: command_complete(GitResult)
  shell: false  # REQUIRED

FR-028:
  name: Pull
  file: workers/git_worker.py
  signal: command_complete(GitResult)

FR-029:
  name: Push
  file: workers/git_worker.py
  signal: command_complete(GitResult)
```

### AI Chat (FR-039 to FR-044)

```yaml
FR-039:
  name: Ollama Integration
  file: workers/ollama_chat_worker.py
  signals: [chat_response_ready, chat_response_chunk, chat_error]
  streaming: true

FR-040:
  name: Chat Panel
  file: ui/chat_panel_widget.py
  class: ChatPanelWidget
  parent: QWidget

FR-041:
  name: Context Modes
  modes: [document, syntax, general, editing]
  file: ui/chat_manager.py

FR-042:
  name: Chat History
  max_messages: 100
  file: ui/chat_manager.py
```

---

## [VALIDATE] Acceptance Criteria

```bash
# All must pass before merge

# Tests
make test                        # 5,628 tests must pass
pytest --cov=src --cov-fail-under=90

# Type safety
mypy --strict src/               # 0 errors required

# Security check
grep -r "shell=True" src/        # Must return empty
grep -r "shell = True" src/      # Must return empty

# Linting
ruff check src/                  # All checks passed
ruff format --check src/         # Already formatted
```

```yaml
# Performance requirements
startup: "<1.0s"
preview_render: "<200ms"
autocomplete: "<50ms"
file_open: "<500ms"
memory_baseline: "<100MB"
```

---

## [CONTEXT] Architecture Decisions

**Handler Architecture**
Original main_window.py exceeded 2,000 lines. MA principle requires <400 lines per file. Handlers split by domain.

**QThread Workers**
PySide6 signal/slot threading integrates with Qt event loop. Workers emit signals for UI updates.

**TOON Format**
30-60% smaller than JSON. Human-readable. Auto-migrates from legacy JSON files.

**Atomic Writes**
temp+rename pattern ensures complete file or nothing. Never partial writes on crash.

---

## [SPEC] UI Layout

```yaml
# AI: Generate main window layout using this structure

MainWindow:
  class: AsciiDocEditor
  base: QMainWindow
  file: ui/main_window.py
  min_size: [1024, 768]

  layout:
    central_widget: QSplitter(horizontal)
    children:
      - editor_pane:
          widget: QPlainTextEdit
          features: [line_numbers, syntax_highlight, auto_indent]
          min_width: 300

      - preview_pane:
          widget: QWebEngineView | QTextBrowser
          gpu_accelerated: true
          min_width: 300

      - chat_pane:
          widget: ChatPanelWidget
          collapsible: true
          default_visible: true
          min_width: 200

  splitter_ratios: [40, 40, 20]  # editor, preview, chat
```

---

## [SPEC] Widget Templates

### Editor Widget

```python
# TEMPLATE: Editor with line numbers
# File: ui/main_window.py (editor section)

from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QPainter, QColor


class LineNumberArea(QWidget):
    """Line number gutter for editor."""

    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Editor with line numbers and syntax highlighting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        # Connect signals
        self.blockCountChanged.connect(self._update_line_number_width)
        self.updateRequest.connect(self._update_line_number_area)

        # Initial setup
        self._update_line_number_width(0)
        self.setFont(QFont("Courier New", 12))
```

### Chat Panel Widget

```python
# TEMPLATE: Chat panel with input and history
# File: ui/chat_panel_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QComboBox
from PySide6.QtCore import Signal


class ChatPanelWidget(QWidget):
    """AI chat panel with history and context modes."""

    message_submitted = Signal(str)
    context_mode_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Context mode selector
        self.context_combo = QComboBox()
        self.context_combo.addItems(["Document", "Syntax", "General", "Editing"])
        self.context_combo.currentTextChanged.connect(self._on_context_changed)
        layout.addWidget(self.context_combo)

        # Chat history
        self.history = QTextBrowser()
        self.history.setOpenExternalLinks(True)
        layout.addWidget(self.history, stretch=1)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AI...")
        self.input_field.returnPressed.connect(self._on_submit)
        layout.addWidget(self.input_field)
```

### Find Bar Widget

```python
# TEMPLATE: Find/replace bar
# File: ui/find_bar_widget.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QCheckBox
from PySide6.QtCore import Signal


class FindBarWidget(QWidget):
    """Find and replace bar."""

    find_requested = Signal(str, bool, bool)  # text, case_sensitive, regex
    replace_requested = Signal(str, str)
    closed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Find field
        self.find_field = QLineEdit()
        self.find_field.setPlaceholderText("Find...")
        self.find_field.returnPressed.connect(self._on_find)
        layout.addWidget(self.find_field)

        # Replace field
        self.replace_field = QLineEdit()
        self.replace_field.setPlaceholderText("Replace...")
        layout.addWidget(self.replace_field)

        # Options
        self.case_checkbox = QCheckBox("Case")
        self.regex_checkbox = QCheckBox("Regex")
        layout.addWidget(self.case_checkbox)
        layout.addWidget(self.regex_checkbox)

        # Buttons
        self.find_btn = QPushButton("Find")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("All")
        self.close_btn = QPushButton("×")
        layout.addWidget(self.find_btn)
        layout.addWidget(self.replace_btn)
        layout.addWidget(self.replace_all_btn)
        layout.addWidget(self.close_btn)
```

---

## [SPEC] Dialog Templates

```python
# TEMPLATE: Standard dialog pattern
# File: ui/{name}_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt


class {Name}Dialog(QDialog):
    """Dialog for {description}."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("{Title}")
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Content area
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_result(self) -> dict:
        """Override to return dialog result."""
        return {}
```

```yaml
# Dialog specifications

dialogs:
  SettingsDialog:
    file: ui/settings_dialog.py
    tabs: [General, Editor, AI, Privacy]
    size: [600, 500]

  TemplateDialog:
    file: ui/template_dialog.py
    features: [template_list, preview, variables]
    size: [700, 500]

  AboutDialog:
    file: ui/about_dialog.py
    content: [logo, version, credits, license]
    size: [400, 300]

  ExportDialog:
    file: ui/export_dialog.py
    formats: [HTML, PDF, DOCX, Markdown]
    options: [output_path, open_after]

  GitCommitDialog:
    file: ui/git_commit_dialog.py
    fields: [message, staged_files, diff_preview]
    buttons: [Commit, Cancel]
```

---

## [SPEC] Menu Structure

```yaml
# AI: Generate menus using this structure

menus:
  File:
    items:
      - {label: "New", shortcut: "Ctrl+N", action: new_file}
      - {label: "Open...", shortcut: "Ctrl+O", action: open_file}
      - {label: "Open Recent", submenu: recent_files}
      - {type: separator}
      - {label: "Save", shortcut: "Ctrl+S", action: save_file}
      - {label: "Save As...", shortcut: "Ctrl+Shift+S", action: save_as}
      - {type: separator}
      - {label: "Import", submenu: import_menu}
      - {label: "Export", submenu: export_menu}
      - {type: separator}
      - {label: "Exit", shortcut: "Ctrl+Q", action: close}

  Edit:
    items:
      - {label: "Undo", shortcut: "Ctrl+Z", action: undo}
      - {label: "Redo", shortcut: "Ctrl+Y", action: redo}
      - {type: separator}
      - {label: "Cut", shortcut: "Ctrl+X", action: cut}
      - {label: "Copy", shortcut: "Ctrl+C", action: copy}
      - {label: "Paste", shortcut: "Ctrl+V", action: paste}
      - {type: separator}
      - {label: "Find...", shortcut: "Ctrl+F", action: show_find}
      - {label: "Replace...", shortcut: "Ctrl+H", action: show_replace}
      - {label: "Go to Line...", shortcut: "Ctrl+G", action: goto_line}

  View:
    items:
      - {label: "Dark Mode", shortcut: "F11", action: toggle_theme, checkable: true}
      - {label: "Preview Panel", action: toggle_preview, checkable: true}
      - {label: "Chat Panel", action: toggle_chat, checkable: true}
      - {type: separator}
      - {label: "Zoom In", shortcut: "Ctrl++", action: zoom_in}
      - {label: "Zoom Out", shortcut: "Ctrl+-", action: zoom_out}
      - {label: "Reset Zoom", shortcut: "Ctrl+0", action: zoom_reset}

  Tools:
    items:
      - {label: "Spell Check", shortcut: "F7", action: spell_check}
      - {label: "Syntax Check", shortcut: "F8", action: syntax_check}
      - {type: separator}
      - {label: "Templates...", action: show_templates}
      - {label: "Settings...", action: show_settings}

  Git:
    items:
      - {label: "Quick Commit...", shortcut: "Ctrl+Shift+G", action: quick_commit}
      - {label: "Pull", action: git_pull}
      - {label: "Push", action: git_push}
      - {type: separator}
      - {label: "Status", action: git_status}
      - {label: "Log", action: git_log}

  GitHub:
    items:
      - {label: "Create PR...", action: github_create_pr}
      - {label: "List PRs", action: github_list_prs}
      - {type: separator}
      - {label: "Create Issue...", action: github_create_issue}
      - {label: "List Issues", action: github_list_issues}

  Help:
    items:
      - {label: "User Guide", action: show_help}
      - {label: "Keyboard Shortcuts", action: show_shortcuts}
      - {type: separator}
      - {label: "About", action: show_about}
```

---

## [SPEC] Keyboard Shortcuts

```yaml
# Complete keyboard shortcut reference

shortcuts:
  # File operations
  file:
    Ctrl+N: new_file
    Ctrl+O: open_file
    Ctrl+S: save_file
    Ctrl+Shift+S: save_as
    Ctrl+W: close_file
    Ctrl+Q: quit

  # Edit operations
  edit:
    Ctrl+Z: undo
    Ctrl+Y: redo
    Ctrl+Shift+Z: redo  # Alternative
    Ctrl+X: cut
    Ctrl+C: copy
    Ctrl+V: paste
    Ctrl+A: select_all
    Ctrl+D: duplicate_line

  # Find/Replace
  search:
    Ctrl+F: show_find
    Ctrl+H: show_replace
    F3: find_next
    Shift+F3: find_previous
    Ctrl+G: goto_line
    Escape: close_find_bar

  # View
  view:
    F11: toggle_dark_mode
    Ctrl+Plus: zoom_in
    Ctrl+Minus: zoom_out
    Ctrl+0: zoom_reset
    Ctrl+B: toggle_preview
    Ctrl+Shift+C: toggle_chat

  # Tools
  tools:
    F7: spell_check
    F8: syntax_check
    Ctrl+Space: autocomplete
    Ctrl+Shift+T: insert_template

  # Git
  git:
    Ctrl+Shift+G: quick_commit
    Ctrl+Shift+P: git_pull
    Ctrl+Shift+U: git_push

  # Editor
  editor:
    Tab: indent
    Shift+Tab: unindent
    Ctrl+/: toggle_comment
    Ctrl+Enter: insert_line_below
    Ctrl+Shift+Enter: insert_line_above
```

---

## [SPEC] Theme System

```yaml
# Theme specification

themes:
  dark:
    name: "Dark"
    colors:
      background: "#1e1e1e"
      foreground: "#d4d4d4"
      selection: "#264f78"
      line_highlight: "#2d2d2d"
      gutter_bg: "#252526"
      gutter_fg: "#858585"

    syntax:
      keyword: "#569cd6"
      string: "#ce9178"
      comment: "#6a9955"
      number: "#b5cea8"
      heading: "#4ec9b0"
      link: "#3794ff"
      bold: "#d4d4d4"
      italic: "#9cdcfe"

  light:
    name: "Light"
    colors:
      background: "#ffffff"
      foreground: "#333333"
      selection: "#add6ff"
      line_highlight: "#f3f3f3"
      gutter_bg: "#f5f5f5"
      gutter_fg: "#999999"

    syntax:
      keyword: "#0000ff"
      string: "#a31515"
      comment: "#008000"
      number: "#098658"
      heading: "#267f99"
      link: "#0066cc"
      bold: "#333333"
      italic: "#333333"
```

```python
# TEMPLATE: Theme manager
# File: ui/theme_manager.py

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor


class ThemeManager:
    """Manages application themes."""

    DARK_STYLESHEET = '''
        QMainWindow { background-color: #1e1e1e; }
        QPlainTextEdit { background-color: #1e1e1e; color: #d4d4d4; }
        QTextBrowser { background-color: #252526; color: #d4d4d4; }
        QMenuBar { background-color: #333333; color: #d4d4d4; }
        QMenu { background-color: #252526; color: #d4d4d4; }
        QStatusBar { background-color: #007acc; color: white; }
    '''

    LIGHT_STYLESHEET = '''
        QMainWindow { background-color: #ffffff; }
        QPlainTextEdit { background-color: #ffffff; color: #333333; }
        QTextBrowser { background-color: #f5f5f5; color: #333333; }
    '''

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.dark_mode = True

    def apply_theme(self, dark: bool) -> None:
        """Apply theme to application."""
        self.dark_mode = dark
        stylesheet = self.DARK_STYLESHEET if dark else self.LIGHT_STYLESHEET
        self.app.setStyleSheet(stylesheet)
```

---

## [SPEC] Status Bar

```yaml
# Status bar specification

status_bar:
  sections:
    - name: message
      stretch: 1
      default: "Ready"

    - name: position
      width: 120
      format: "Ln {line}, Col {col}"

    - name: encoding
      width: 80
      default: "UTF-8"

    - name: git_branch
      width: 100
      icon: "branch"
      format: "{branch}"

    - name: git_status
      width: 60
      format: "M:{modified} S:{staged}"

  messages:
    file_saved: "Saved: {filename}"
    file_opened: "Opened: {filename}"
    git_commit: "Committed: {short_hash}"
    export_complete: "Exported to {format}: {path}"
    error: "Error: {message}"

  duration: 5000  # ms for temporary messages
```

---

## [SPEC] User Flows

```yaml
# Key user interaction flows

flows:
  open_file:
    steps:
      1: {action: "Ctrl+O or File > Open", ui: show_file_dialog}
      2: {action: "Select file", ui: file_dialog}
      3: {action: "Click Open", result: file_loaded}
      4: {feedback: status_bar, message: "Opened: {filename}"}
      5: {update: [editor_content, preview, window_title]}

  save_file:
    steps:
      1: {action: "Ctrl+S or File > Save", check: has_path}
      2a: {if: has_path, action: atomic_save}
      2b: {if: no_path, action: show_save_dialog}
      3: {feedback: status_bar, message: "Saved: {filename}"}
      4: {update: [modified_flag, window_title]}

  git_commit:
    steps:
      1: {action: "Ctrl+Shift+G", ui: show_quick_commit}
      2: {display: [staged_files, diff_preview]}
      3: {input: commit_message}
      4: {action: "Click Commit", start: git_worker}
      5: {feedback: status_bar, message: "Committed: {hash}"}
      6: {update: git_status}

  ai_chat:
    steps:
      1: {action: "Type in chat input", input: message}
      2: {action: "Press Enter", start: ollama_worker}
      3: {feedback: chat_history, streaming: true}
      4: {complete: append_response}

  find_replace:
    steps:
      1: {action: "Ctrl+F", ui: show_find_bar}
      2: {input: search_text}
      3: {action: "Press Enter or F3", highlight: matches}
      4: {optional: "Ctrl+H", input: replace_text}
      5: {action: "Replace or Replace All", update: editor}
      6: {action: "Escape", ui: hide_find_bar}
```

---

## [SPEC] Feedback Patterns

```yaml
# User feedback specifications

feedback:
  status_bar:
    success:
      duration: 5000
      style: "background-color: #28a745; color: white;"
    error:
      duration: 10000
      style: "background-color: #dc3545; color: white;"
    info:
      duration: 3000
      style: "background-color: #007bff; color: white;"

  notifications:
    toast:
      position: bottom_right
      duration: 3000
      max_visible: 3

  progress:
    indeterminate:
      widget: QProgressBar
      style: "indeterminate"
    determinate:
      widget: QProgressBar
      range: [0, 100]

  dialogs:
    error:
      icon: QMessageBox.Critical
      buttons: [Ok]
    warning:
      icon: QMessageBox.Warning
      buttons: [Ok, Cancel]
    question:
      icon: QMessageBox.Question
      buttons: [Yes, No, Cancel]
    info:
      icon: QMessageBox.Information
      buttons: [Ok]

  editor:
    syntax_error:
      underline: wavy_red
      tooltip: error_message
      gutter: error_icon
    warning:
      underline: wavy_yellow
      tooltip: warning_message
      gutter: warning_icon
    spell_error:
      underline: dotted_blue
      context_menu: suggestions
```

---

## [SPEC] Accessibility

```yaml
# Accessibility requirements

accessibility:
  keyboard:
    - "All features accessible via keyboard"
    - "Tab order follows visual layout"
    - "Focus indicators visible"

  screen_reader:
    - "All widgets have accessible names"
    - "Status changes announced"
    - "Dialog content readable"

  contrast:
    minimum_ratio: 4.5
    large_text_ratio: 3.0

  font_scaling:
    min_size: 8
    max_size: 72
    step: 2
```

---

*v2.1.0 | 109 FRs | 46,457 lines | UI/UX Spec | Dec 5, 2025*
