# Signal/Slot Contracts

**v2.1.0** | Qt signal definitions for AI code generation

---

## [SPEC] Code Generation

```yaml
# AI INSTRUCTION: Generate workers/handlers with these signal contracts

generation_rules:
  imports: |
    from PySide6.QtCore import QObject, QThread, Signal
    from pathlib import Path
    from typing import Any

  signal_syntax: |
    # Define as class attribute
    signal_name = Signal(type)
    signal_name = Signal(type1, type2)  # Multiple args
    signal_name = Signal()              # No args

  connection_syntax: |
    # Connect in __init__ or setup
    self.worker.signal_name.connect(self._handle_signal)

  emit_syntax: |
    # Emit from worker thread
    self.signal_name.emit(value)
```

---

## [SPEC] Worker Signals

### GitWorker

```yaml
file: workers/git_worker.py
base: BaseWorker
imports:
  - "from asciidoc_artisan.core.models import GitResult, GitStatus"

signals:
  command_complete:
    type: GitResult
    description: "Emitted when git command finishes"
    emit_on: [commit, pull, push, reset, checkout]

  status_ready:
    type: GitStatus
    description: "Emitted with repository status"
    emit_on: [status_check]

  detailed_status_ready:
    type: dict
    description: "Emitted with full status details"
    emit_on: [detailed_status_check]

methods:
  commit(message: str) -> None
  pull() -> None
  push() -> None
  check_status() -> None
```

### GitHubCLIWorker

```yaml
file: workers/github_cli_worker.py
base: BaseWorker
imports:
  - "from asciidoc_artisan.core.models import GitHubResult"

signals:
  github_result_ready:
    type: GitHubResult
    description: "Emitted when GitHub CLI command completes"
    emit_on: [pr_create, pr_list, issue_create, issue_list, repo_view]

methods:
  create_pr(title: str, body: str, base: str) -> None
  list_prs(state: str) -> None
  create_issue(title: str, body: str) -> None
  list_issues(state: str) -> None
  view_repo() -> None
```

### PandocWorker

```yaml
file: workers/pandoc_worker.py
base: QThread

signals:
  conversion_complete:
    type: "(str, str)"
    args: [format, output_path]
    description: "Emitted when conversion succeeds"

  conversion_error:
    type: "(str, str)"
    args: [format, error_message]
    description: "Emitted when conversion fails"

  progress_update:
    type: str
    description: "Status message during conversion"

methods:
  convert(input_path: Path, output_format: str, output_path: Path) -> None
  cancel() -> None
```

### PreviewWorker

```yaml
file: workers/preview_worker.py
base: QThread

signals:
  render_complete:
    type: str
    description: "HTML content of rendered preview"

  render_error:
    type: str
    description: "Error message on render failure"

  ready:
    type: null
    description: "Worker is ready to accept requests"

methods:
  render(content: str) -> None
  cancel() -> None
```

### OllamaChatWorker

```yaml
file: workers/ollama_chat_worker.py
base: QThread
imports:
  - "from asciidoc_artisan.core.models import ChatMessage"

signals:
  chat_response_ready:
    type: ChatMessage
    description: "Complete response received"

  chat_response_chunk:
    type: str
    description: "Streaming chunk received"

  chat_error:
    type: str
    description: "Error during chat"

  operation_cancelled:
    type: null
    description: "Request was cancelled"

methods:
  send_message(message: str, context_mode: str, model: str) -> None
  cancel() -> None
```

### ClaudeWorker

```yaml
file: claude/claude_worker.py
base: QThread
imports:
  - "from asciidoc_artisan.claude.claude_client import ClaudeResult"

signals:
  response_ready:
    type: ClaudeResult
    description: "Claude API response received"

  connection_tested:
    type: ClaudeResult
    description: "Connection test result"

  error_occurred:
    type: str
    description: "Error during API call"

methods:
  send_request(prompt: str, context: str | None) -> None
  test_connection() -> None
  cancel() -> None
```

---

## [SPEC] Handler Signals

### FileHandler

```yaml
file: ui/file_handler.py
base: QObject

signals:
  file_opened:
    type: Path
    description: "File successfully opened"

  file_saved:
    type: Path
    description: "File successfully saved"

  file_modified:
    type: bool
    description: "Document modified state changed"

  file_changed_externally:
    type: Path
    description: "File changed outside editor"

methods:
  new_file() -> None
  open_file(path: Path | None) -> bool
  save_file() -> bool
  save_as() -> bool
```

### PreviewHandlerBase

```yaml
file: ui/preview_handler_base.py
base: QObject

signals:
  preview_updated:
    type: str
    description: "Preview HTML updated"

  preview_error:
    type: str
    description: "Preview render error"

methods:
  update_preview(content: str) -> None
  schedule_update() -> None
```

### GitHandler

```yaml
file: ui/git_handler.py
base: QObject

signals:
  status_changed:
    type: GitStatus
    description: "Repository status changed"

  operation_complete:
    type: GitResult
    description: "Git operation finished"

methods:
  commit(message: str) -> None
  pull() -> None
  push() -> None
  refresh_status() -> None
```

---

## [SPEC] Widget Signals

### QuickCommitWidget

```yaml
file: ui/quick_commit_widget.py
base: QWidget

signals:
  commit_requested:
    type: str
    description: "User submitted commit message"

  cancelled:
    type: null
    description: "User cancelled commit"
```

### FindBarWidget

```yaml
file: ui/find_bar_widget.py
base: QWidget

signals:
  find_requested:
    type: str
    description: "User requested search"

  replace_requested:
    type: "(str, str)"
    args: [find_text, replace_text]
    description: "User requested replace"

  closed:
    type: null
    description: "Find bar closed"
```

### ChatBarWidget

```yaml
file: ui/chat_bar_widget.py
base: QWidget

signals:
  message_submitted:
    type: str
    description: "User submitted chat message"

  context_mode_changed:
    type: str
    description: "Context mode selection changed"
```

---

## [SPEC] Core Signals

### AsyncFileWatcher

```yaml
file: core/async_file_watcher.py
base: QObject

signals:
  file_modified:
    type: Path
    description: "Watched file was modified"

  file_deleted:
    type: Path
    description: "Watched file was deleted"

  file_created:
    type: Path
    description: "New file created in watched dir"

  error:
    type: str
    description: "Watcher error occurred"

methods:
  watch(path: Path) -> None
  unwatch(path: Path) -> None
  stop() -> None
```

### QtAsyncFileManager

```yaml
file: core/qt_async_file_manager.py
base: QObject

signals:
  read_complete:
    type: "(Path, str)"
    args: [path, content]
    description: "File read completed"

  write_complete:
    type: Path
    description: "File write completed"

  operation_failed:
    type: "(str, Path, str)"
    args: [operation, path, error]
    description: "File operation failed"

  file_changed_externally:
    type: Path
    description: "External file change detected"

methods:
  read_file(path: Path) -> None
  write_file(path: Path, content: str) -> None
```

---

## [SPEC] Error Codes

```yaml
# Reference for SyntaxErrorModel.code field
# Pattern: [EWI][0-9]{3}

# E: Errors (must fix)
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
  E105: "Invalid attribute value"

# W: Warnings (should fix)
warnings:
  W001: "Heading level skipped"
  W002: "Empty section"
  W003: "Missing document title"
  W004: "Line exceeds 120 characters"
  W005: "Trailing whitespace"
  W006: "Tab character in content"
  W007: "Missing blank line before block"

# I: Info (suggestions)
info:
  I001: "Consider using semantic heading"
  I002: "Block could benefit from title"
  I003: "Consider using include directive"
  I004: "Long paragraph, consider splitting"
  I005: "Consider adding alt text to image"
```

---

## [SPEC] Signal Connection Example

```python
# AI: Use this pattern for signal connections

from PySide6.QtCore import QObject, Signal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor


class ExampleHandler(QObject):
    """Handler with signal connections."""

    # Define signals
    operation_complete = Signal(object)
    operation_failed = Signal(str)

    def __init__(self, editor: "AsciiDocEditor") -> None:
        super().__init__(editor)
        self.editor = editor

        # Create worker
        self._worker = ExampleWorker()

        # Connect worker signals to handler slots
        self._worker.result_ready.connect(self._on_result_ready)
        self._worker.error_occurred.connect(self._on_error)

        # Start worker thread
        self._worker.start()

    def _on_result_ready(self, result: object) -> None:
        """Handle worker result on main thread."""
        # Safe to update UI here
        self.operation_complete.emit(result)

    def _on_error(self, error: str) -> None:
        """Handle worker error on main thread."""
        self.operation_failed.emit(error)

    def do_operation(self, data: str) -> None:
        """Queue operation for worker."""
        self._worker.queue_request(data)
```

---

## [SPEC] Worker Implementation Example

```python
# AI: Use this pattern for worker implementation

from PySide6.QtCore import QThread, Signal
from typing import Any


class ExampleWorker(QThread):
    """Background worker with signal communication."""

    # Signals (emitted from worker thread)
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._cancelled = False
        self._queue: list[Any] = []

    def run(self) -> None:
        """Main worker loop - runs in separate thread."""
        while not self._cancelled:
            if not self._queue:
                self.msleep(10)
                continue

            item = self._queue.pop(0)
            try:
                result = self._process(item)
                # Emit signal to main thread
                self.result_ready.emit(result)
            except Exception as e:
                self.error_occurred.emit(str(e))

    def _process(self, item: Any) -> Any:
        """Process single item. Override in subclass."""
        raise NotImplementedError

    def queue_request(self, item: Any) -> None:
        """Add item to processing queue."""
        self._queue.append(item)

    def cancel(self) -> None:
        """Signal worker to stop."""
        self._cancelled = True
```

---

*v2.1.0 | Signal/slot contracts | AI code generation | Dec 5, 2025*
