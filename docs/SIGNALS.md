# Signal/Slot Contracts

**v2.1.0** | Qt signal definitions for worker generation

---

## Usage

AI: Use these signal definitions when generating QThread worker classes.

---

## Worker Signals

### GitWorker

```yaml
file: workers/git_worker.py
base: BaseWorker
signals:
  command_complete: {type: GitResult}
  status_ready: {type: GitStatus}
  detailed_status_ready: {type: dict}
```

### GitHubCLIWorker

```yaml
file: workers/github_cli_worker.py
base: BaseWorker
signals:
  github_result_ready: {type: GitHubResult}
```

### PandocWorker

```yaml
file: workers/pandoc_worker.py
base: QThread
signals:
  conversion_complete: {type: "(str, str)"}  # (format, output_path)
  conversion_error: {type: "(str, str)"}     # (format, error_message)
  progress_update: {type: str}
```

### PreviewWorker

```yaml
file: workers/preview_worker.py
base: QThread
signals:
  render_complete: {type: str}  # HTML content
  render_error: {type: str}
  ready: {type: null}
```

### OllamaChatWorker

```yaml
file: workers/ollama_chat_worker.py
base: QThread
signals:
  chat_response_ready: {type: ChatMessage}
  chat_response_chunk: {type: str}
  chat_error: {type: str}
  operation_cancelled: {type: null}
```

### ClaudeWorker

```yaml
file: claude/claude_worker.py
base: QThread
signals:
  response_ready: {type: ClaudeResult}
  connection_tested: {type: ClaudeResult}
  error_occurred: {type: str}
```

---

## Handler Signals

### FileHandler

```yaml
file: ui/file_handler.py
base: QObject
signals:
  file_opened: {type: Path}
  file_saved: {type: Path}
  file_modified: {type: bool}
  file_changed_externally: {type: Path}
```

### PreviewHandlerBase

```yaml
file: ui/preview_handler_base.py
base: QObject
signals:
  preview_updated: {type: str}
  preview_error: {type: str}
```

### QuickCommitWidget

```yaml
file: ui/quick_commit_widget.py
base: QWidget
signals:
  commit_requested: {type: str}
  cancelled: {type: null}
```

---

## Core Signals

### AsyncFileWatcher

```yaml
file: core/async_file_watcher.py
base: QObject
signals:
  file_modified: {type: Path}
  file_deleted: {type: Path}
  file_created: {type: Path}
  error: {type: str}
```

### QtAsyncFileManager

```yaml
file: core/qt_async_file_manager.py
base: QObject
signals:
  read_complete: {type: "(Path, str)"}
  write_complete: {type: Path}
  operation_failed: {type: "(str, Path, str)"}
  file_changed_externally: {type: Path}
```

---

## Error Codes

```yaml
# For SyntaxErrorModel.code field

syntax_errors:  # E001-E099
  E001: "Unclosed source block"
  E002: "Unclosed example block"
  E006: "Unclosed table"
  E008: "Invalid heading level"
  E009: "Duplicate anchor ID"

semantic_errors:  # E100-E199
  E100: "Broken cross-reference"
  E101: "Include file not found"
  E103: "Circular include"

warnings:  # W001-W099
  W001: "Heading level skipped"
  W002: "Empty section"
  W004: "Long line (>120 chars)"

style_issues:  # I001-I099
  I001: "Consider semantic heading"
  I002: "Block could use title"
```

---

*v2.1.0 | Signal/slot contracts | Dec 5, 2025*
