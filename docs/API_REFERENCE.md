# AsciiDoc Artisan API Reference

> Version 2.1.0 | Auto-generated API documentation

## Package Structure

```
asciidoc_artisan/
├── core/          # Core utilities, settings, file operations
├── ui/            # UI components, managers, dialogs
├── workers/       # Background thread workers
├── claude/        # Claude AI integration
└── lsp/           # Language Server Protocol
```

---

## Core Module (`asciidoc_artisan.core`)

### AppSettings

Application settings dataclass with persistence.

```python
from asciidoc_artisan.core import AppSettings

settings = AppSettings()
settings.font_size = 14
settings.dark_mode = True
settings.ollama_enabled = True
settings.ollama_model = "llama3.2"
```

**Key Attributes:**
| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `font_size` | int | 12 | Editor font size |
| `dark_mode` | bool | False | Dark theme enabled |
| `editor_font_family` | str | "Consolas" | Editor font |
| `spell_check_enabled` | bool | True | Spell check active |
| `ollama_enabled` | bool | False | Ollama AI enabled |
| `ollama_model` | str | "" | Selected Ollama model |
| `claude_model` | str | "" | Selected Claude model |
| `git_repo_path` | str | "" | Git repository path |
| `auto_save_enabled` | bool | True | Auto-save enabled |

---

### SecureCredentials

Secure API key management using system keyring.

```python
from asciidoc_artisan.core import SecureCredentials

creds = SecureCredentials()

# Check if key exists
if creds.has_anthropic_key():
    key = creds.get_anthropic_key()

# Store key securely
creds.set_anthropic_key("sk-ant-...")
```

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `has_anthropic_key()` | bool | Check if Anthropic key stored |
| `get_anthropic_key()` | str \| None | Retrieve stored key |
| `set_anthropic_key(key)` | bool | Store key securely |
| `delete_anthropic_key()` | bool | Remove stored key |

---

### File Operations

#### atomic_save_text

Atomic file write preventing corruption.

```python
from asciidoc_artisan.core.file_operations import atomic_save_text

success = atomic_save_text(Path("doc.adoc"), content, encoding="utf-8")
```

#### QtAsyncFileManager

Async file operations with Qt signals.

```python
from asciidoc_artisan.core import QtAsyncFileManager

manager = QtAsyncFileManager()
manager.read_complete.connect(on_read_done)
manager.write_complete.connect(on_write_done)

# Async read (non-blocking)
await manager.read_file(Path("document.adoc"))

# Async write with atomic save
await manager.write_file(Path("output.adoc"), content)

# Watch file for external changes
manager.watch_file(Path("document.adoc"))
```

**Signals:**
| Signal | Parameters | Description |
|--------|------------|-------------|
| `read_complete` | (Path, str) | File read finished |
| `write_complete` | (Path,) | File write finished |
| `operation_failed` | (str, Path, str) | Operation error |
| `file_changed_externally` | (Path,) | External modification |

---

### GPU Detection

```python
from asciidoc_artisan.core import GPUDetector

detector = GPUDetector()
info = detector.detect()

print(f"GPU: {info.gpu_name}")
print(f"Has GPU: {info.has_gpu}")
print(f"Metal available: {info.metal_available}")
```

---

## UI Module (`asciidoc_artisan.ui`)

### Main Window

```python
from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Create and show editor
editor = AsciiDocEditor()
editor.show()

# Access components
editor.editor          # QPlainTextEdit - main editor
editor.preview         # QWebEngineView - preview pane
editor.chat_panel      # ChatPanel - AI chat
editor.chat_bar        # ChatBarWidget - chat input

# File operations
editor.new_file()
editor.open_file("/path/to/doc.adoc")
editor.save_file()
editor.save_file(save_as=True)

# Export
editor.save_file_as_format("pdf")
editor.save_file_as_format("html")
editor.save_file_as_format("docx")
```

---

### Managers

#### FileHandler

```python
from asciidoc_artisan.ui.file_handler import FileHandler

handler = FileHandler(editor, window, settings_mgr, status_mgr)

# Signals
handler.file_opened.connect(on_file_opened)
handler.file_saved.connect(on_file_saved)
handler.file_modified.connect(on_modified_changed)

# Operations
handler.new_file()
handler.open_file("/path/to/file.adoc")
handler.save_file(save_as=False)

# State
if handler.has_unsaved_changes():
    handler.prompt_save_before_action("closing")
```

#### ExportManager

```python
from asciidoc_artisan.ui.export_manager import ExportManager

export_mgr = ExportManager(editor)

# Export to formats
export_mgr.save_file_as_format("pdf")
export_mgr.save_file_as_format("html")
export_mgr.save_file_as_format("docx")
export_mgr.save_file_as_format("md")
```

#### ThemeManager

```python
from asciidoc_artisan.ui.theme_manager import ThemeManager

theme_mgr = ThemeManager(editor, settings)

# Toggle dark mode
theme_mgr.toggle_dark_mode()

# Apply theme
theme_mgr.apply_theme(dark_mode=True)
```

#### ChatManager

```python
from asciidoc_artisan.ui.chat_manager import ChatManager

chat_mgr = ChatManager(editor, settings, chat_panel, chat_bar)

# Send message
chat_mgr.send_message("Explain this code", model="llama3.2", context="document")

# Clear history
chat_mgr.clear_history()

# Switch backend
chat_mgr.set_backend("ollama")  # or "claude"
```

---

### Dialogs

#### PerformanceDashboard

```python
from asciidoc_artisan.ui.performance_dashboard import (
    PerformanceDashboard,
    get_performance_collector,
)

# Show dashboard
dialog = PerformanceDashboard(parent)
dialog.exec()

# Record metrics in your code
collector = get_performance_collector()
collector.start_timer("my_operation")
# ... do work ...
elapsed = collector.stop_timer("my_operation")

# Direct metric recording
collector.record_metric("memory_usage", 256.5, "MB")
```

#### OllamaSettingsDialog

```python
from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

dialog = OllamaSettingsDialog(settings, parent)
if dialog.exec():
    updated_settings = dialog.get_settings()
```

---

## Workers Module (`asciidoc_artisan.workers`)

### PreviewWorker

Background rendering of AsciiDoc to HTML.

```python
from asciidoc_artisan.workers.preview_worker import PreviewWorker

worker = PreviewWorker()

# Connect signals
worker.render_complete.connect(on_render_done)
worker.error.connect(on_render_error)

# Request render
worker.render(asciidoc_content)
```

### GitWorker

Background Git operations.

```python
from asciidoc_artisan.workers.git_worker import GitWorker

worker = GitWorker()

# Connect signals
worker.operation_complete.connect(on_git_done)
worker.error.connect(on_git_error)

# Execute operations
worker.set_operation("status", repo_path)
worker.set_operation("commit", repo_path, message="Commit message")
worker.set_operation("push", repo_path)
worker.start()
```

### PandocWorker

Background document conversion.

```python
from asciidoc_artisan.workers.pandoc_worker import PandocWorker

worker = PandocWorker()

# Connect signals
worker.conversion_complete.connect(on_convert_done)

# Convert document
worker.convert(input_path, output_path, format="pdf")
worker.start()
```

### OllamaChatWorker

Background Ollama API calls.

```python
from asciidoc_artisan.workers.ollama_chat_worker import OllamaChatWorker

worker = OllamaChatWorker()

# Connect signals
worker.response_chunk.connect(on_chunk)  # Streaming
worker.response_complete.connect(on_complete)
worker.error.connect(on_error)

# Send message
worker.send_message(
    model="llama3.2",
    messages=[{"role": "user", "content": "Hello"}],
    context="document"
)
worker.start()
```

---

## Claude Module (`asciidoc_artisan.claude`)

### ClaudeClient

```python
from asciidoc_artisan.claude import ClaudeClient

client = ClaudeClient()

# Available models
print(ClaudeClient.AVAILABLE_MODELS)

# Send message
result = client.send_message(
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-sonnet-4-20250514"
)

if result.success:
    print(result.content)
else:
    print(f"Error: {result.error}")
```

### ClaudeWorker

Background Claude API calls.

```python
from asciidoc_artisan.claude import ClaudeWorker

worker = ClaudeWorker()

# Connect signals
worker.response_ready.connect(on_response)
worker.error.connect(on_error)

# Send message
worker.send_message(messages, model="claude-sonnet-4-20250514")
worker.start()
```

---

## Constants

```python
from asciidoc_artisan.core.constants import (
    APP_NAME,                    # "AsciiDoc Artisan"
    APP_VERSION,                 # "2.1.0"
    MAX_FILE_SIZE_MB,            # 50
    SUPPORTED_OPEN_FILTER,       # File dialog filter
    SUPPORTED_SAVE_FILTER,       # Save dialog filter
    is_pandoc_available,         # Check Pandoc installation
)
```

---

## Error Handling

### EnhancedErrorManager

```python
from asciidoc_artisan.ui.enhanced_errors import EnhancedErrorManager

error_mgr = EnhancedErrorManager(editor)

# Show contextual error with recovery actions
error_mgr.show_error("git_not_configured")
error_mgr.show_error("pandoc_not_found")
error_mgr.show_error("file_not_found", extra_details="/path/to/file")

# Classify exceptions
error_type = error_mgr.classify_exception(exc)
```

---

## Performance Metrics

```python
from asciidoc_artisan.ui.performance_dashboard import get_performance_collector

collector = get_performance_collector()

# Time an operation
collector.start_timer("file_open")
# ... operation ...
elapsed_ms = collector.stop_timer("file_open")

# Record direct metric
collector.record_metric("memory_usage", 256.0, "MB")

# Get all metrics
summary = collector.get_summary()
for name, data in summary.items():
    print(f"{name}: {data['current']:.1f}{data['unit']} (target: {data['target']})")
```

---

## Signal Reference

### Common Signals

| Component | Signal | Parameters | Description |
|-----------|--------|------------|-------------|
| FileHandler | `file_opened` | (Path,) | File opened |
| FileHandler | `file_saved` | (Path,) | File saved |
| FileHandler | `file_modified` | (bool,) | Unsaved changes state |
| PreviewWorker | `render_complete` | (str,) | HTML output |
| GitWorker | `operation_complete` | (str, bool, str) | Op, success, message |
| ChatManager | `message_received` | (str,) | AI response |
| ChatBarWidget | `message_sent` | (str, str, str) | Text, model, context |

---

## Type Annotations

All public APIs use Python type hints compatible with `mypy --strict`:

```python
def atomic_save_text(
    file_path: Path,
    content: str,
    encoding: str = "utf-8"
) -> bool: ...

async def read_file(
    file_path: Path,
    encoding: str = "utf-8"
) -> str | None: ...
```

---

*Generated for AsciiDoc Artisan v2.1.0*
