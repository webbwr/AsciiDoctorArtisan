# AsciiDoc Artisan Specifications

**v2.1.0** | **109 FRs** | **Specification-Driven Coding**

---

## Document Structure

This specification enables **architecture and code generation** from requirements.

| Marker | Purpose | Audience |
|--------|---------|----------|
| `[CONTEXT]` | Rationale, history, decisions | Human readers |
| `[SPEC]` | Machine-parseable requirements | AI coding assistants |
| `[SCHEMA]` | Data models for code generation | AI coding assistants |
| `[SIGNALS]` | Signal/slot contracts | AI coding assistants |
| `[VALIDATE]` | Acceptance criteria and tests | Both |

---

## [CONTEXT] Project Overview

AsciiDoc Artisan is a desktop AsciiDoc editor with live preview, built on PySide6/Qt. The project follows specification-driven development where every feature maps to a Functional Requirement (FR).

**Design Philosophy:**
- Manager Architecture (MA): No file exceeds 400 lines
- Thread Safety: All slow operations run in QThread workers
- Atomic Operations: File writes use temp+rename pattern
- Type Safety: Full mypy --strict compliance

**Technology Stack:**
- PySide6 6.9+ (Qt bindings)
- Python 3.11+
- asciidoc3 (AsciiDoc processing)
- pypandoc (format conversion)
- pymupdf (PDF handling)
- pydantic (data validation)

---

## [SPEC] Project Metrics

```yaml
# AI: Use these values for validation and documentation
version: 2.1.0
release_date: 2025-12-05
status: public_release

codebase:
  lines: 46457
  files: 180
  package: asciidoc_artisan.{core,ui,workers,lsp,claude}

testing:
  unit_tests: 5122
  e2e_tests: 17
  total_tests: 5139
  coverage: 95%
  pass_rate: 100%

quality:
  type_checker: mypy --strict
  type_errors: 0
  linter: ruff
  formatter: ruff-format

performance:
  startup: 0.27s
  preview_latency: <200ms
  autocomplete: 20-40ms
```

---

## [SCHEMA] Data Models

AI: Generate Pydantic models from these schemas. All models use `model_config = {"frozen": False, "validate_assignment": True}`.

### Settings Schema

```yaml
# AI: Generate dataclass in core/settings.py
Settings:
  description: "Application settings with JSON persistence"
  persistence_path:
    linux: ~/.config/AsciiDocArtisan/AsciiDocArtisan.json
    windows: "%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json"
    macos: ~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json

  fields:
    # Path settings
    last_directory: {type: str, default: "Path.home()", validation: "directory_exists"}
    last_file: {type: "str | None", default: null}
    git_repo_path: {type: "str | None", default: null}

    # UI settings
    dark_mode: {type: bool, default: true}
    maximized: {type: bool, default: true}
    window_geometry: {type: "dict[str, int] | None", default: null, keys: [x, y, width, height]}
    splitter_sizes: {type: "list[int] | None", default: null, length: "2-3"}
    font_size: {type: int, default: 12, range: "8-72", deprecated: true}

    # Auto-save
    auto_save_enabled: {type: bool, default: true}
    auto_save_interval: {type: int, default: 300, range: "30-3600", unit: seconds}

    # AI backend
    ai_backend: {type: str, default: "ollama", choices: [ollama, claude]}
    ollama_enabled: {type: bool, default: true}
    ollama_model: {type: "str | None", default: "gnokit/improve-grammer"}
    claude_model: {type: "str | None", default: "claude-sonnet-4-20250514"}

    # Chat
    ai_chat_enabled: {type: bool, default: true}
    chat_history: {type: "list[dict[str, Any]]", default: []}
    chat_max_history: {type: int, default: 100, range: "10-1000"}
    chat_context_mode: {type: str, default: "document", choices: [document, syntax, general, editing]}
    chat_send_document: {type: bool, default: true}

    # Fonts
    editor_font_family: {type: str, default: "Courier New"}
    editor_font_size: {type: int, default: 12, range: "8-72"}
    preview_font_family: {type: str, default: "Arial"}
    preview_font_size: {type: int, default: 12, range: "8-72"}
    chat_font_family: {type: str, default: "Arial"}
    chat_font_size: {type: int, default: 11, range: "8-72"}

    # Spell check
    spell_check_enabled: {type: bool, default: true}
    spell_check_language: {type: str, default: "en"}
    spell_check_custom_words: {type: "list[str]", default: []}

    # Autocomplete
    autocomplete_enabled: {type: bool, default: true}
    autocomplete_delay: {type: int, default: 300, range: "100-5000", unit: ms}
    autocomplete_min_chars: {type: int, default: 2, range: "1-10"}

    # Syntax checking
    syntax_check_realtime_enabled: {type: bool, default: true}
    syntax_check_delay: {type: int, default: 500, range: "100-10000", unit: ms}
    syntax_check_show_underlines: {type: bool, default: true}

    # Templates
    template_last_category: {type: str, default: "All"}
    template_recent_limit: {type: int, default: 10, range: "1-50"}

    # Telemetry (opt-in)
    telemetry_enabled: {type: bool, default: false}
    telemetry_session_id: {type: "str | None", default: null}
    telemetry_opt_in_shown: {type: bool, default: false}

  methods:
    to_dict: "Returns dict for JSON serialization"
    from_dict: "Creates Settings from dict with migration support"
    validate: "Validates all fields, applies corrections, returns self"
```

### Git Models Schema

```yaml
# AI: Generate Pydantic models in core/git_models.py

GitResult:
  description: "Result of Git operation execution"
  fields:
    success: {type: bool, required: true, description: "True if operation succeeded"}
    stdout: {type: str, default: "", description: "Standard output"}
    stderr: {type: str, default: "", description: "Standard error"}
    exit_code: {type: "int | None", default: null, description: "Process exit code"}
    user_message: {type: str, required: true, validation: "non_empty", description: "Human-readable status"}

GitStatus:
  description: "Git repository status information"
  fields:
    branch: {type: str, default: "", description: "Current branch name"}
    modified_count: {type: int, default: 0, validation: "non_negative"}
    staged_count: {type: int, default: 0, validation: "non_negative"}
    untracked_count: {type: int, default: 0, validation: "non_negative"}
    has_conflicts: {type: bool, default: false}
    ahead_count: {type: int, default: 0, validation: "non_negative"}
    behind_count: {type: int, default: 0, validation: "non_negative"}
    is_dirty: {type: bool, default: false}

GitHubResult:
  description: "Result of GitHub CLI operation"
  fields:
    success: {type: bool, required: true}
    data: {type: "dict | list | None", default: null, description: "Parsed JSON from gh CLI"}
    error: {type: str, default: ""}
    user_message: {type: str, required: true, validation: "non_empty"}
    operation: {type: str, required: true, choices: [pr_create, pr_list, issue_create, issue_list, repo_view, repo_info, pr, issue, repo, gh, cancelled, unknown]}
```

### Chat Models Schema

```yaml
# AI: Generate Pydantic model in core/chat_models.py

ChatMessage:
  description: "Single message in AI chat conversation"
  fields:
    role: {type: str, required: true, choices: [user, assistant]}
    content: {type: str, required: true, validation: "non_empty"}
    timestamp: {type: float, required: true, validation: "non_negative", description: "Unix timestamp"}
    model: {type: str, required: true, description: "AI model name"}
    context_mode: {type: str, required: true, choices: [document, syntax, general, editing]}
```

### Completion Models Schema

```yaml
# AI: Generate Pydantic models in core/completion_models.py

CompletionKind:
  type: enum
  values:
    SYNTAX: "syntax"      # AsciiDoc syntax elements
    ATTRIBUTE: "attribute" # Document attributes
    XREF: "xref"          # Cross-references
    INCLUDE: "include"    # Include paths
    SNIPPET: "snippet"    # Code snippets

CompletionItem:
  description: "Auto-complete suggestion"
  fields:
    text: {type: str, required: true, validation: "non_empty", description: "Display text"}
    kind: {type: CompletionKind, required: true}
    detail: {type: str, default: "", description: "Short description"}
    documentation: {type: str, default: "", description: "Full docs (markdown)"}
    insert_text: {type: "str | None", default: null, description: "Text to insert"}
    sort_text: {type: "str | None", default: null}
    filter_text: {type: "str | None", default: null}
    score: {type: float, default: 0.0, range: "0-100"}

CompletionContext:
  description: "Context for auto-complete request"
  fields:
    line: {type: str, required: true, description: "Current line text"}
    line_number: {type: int, required: true, validation: "non_negative"}
    column: {type: int, required: true, validation: "non_negative"}
    prefix: {type: str, required: true, description: "Text before cursor"}
    trigger_char: {type: "str | None", default: null}
    manual: {type: bool, default: false, description: "Ctrl+Space triggered"}
  properties:
    word_before_cursor: "Extract word before cursor from prefix"
```

### Syntax Models Schema

```yaml
# AI: Generate Pydantic models in core/syntax_models.py

ErrorSeverity:
  type: enum
  values:
    ERROR: "error"      # Red - breaks rendering
    WARNING: "warning"  # Yellow - semantic issues
    INFO: "info"        # Blue - style suggestions

TextEdit:
  description: "Single text edit for quick fixes"
  fields:
    start_line: {type: int, required: true, validation: "non_negative"}
    start_column: {type: int, required: true, validation: "non_negative"}
    end_line: {type: int, required: true, validation: "non_negative"}
    end_column: {type: int, required: true, validation: "non_negative"}
    new_text: {type: str, required: true}

QuickFix:
  description: "Quick fix suggestion"
  fields:
    title: {type: str, required: true, validation: "non_empty"}
    edits: {type: "list[TextEdit]", default: []}

SyntaxErrorModel:
  description: "Syntax error with position and fixes"
  fields:
    code: {type: str, required: true, pattern: "[EWI][0-9]{3}", description: "E001, W001, I001"}
    severity: {type: ErrorSeverity, required: true}
    message: {type: str, required: true, validation: "non_empty"}
    line: {type: int, required: true, validation: "non_negative"}
    column: {type: int, required: true, validation: "non_negative"}
    length: {type: int, required: true, validation: "non_negative"}
    fixes: {type: "list[QuickFix]", default: []}
```

### Template Models Schema

```yaml
# AI: Generate Pydantic models in core/template_models.py

TemplateVariable:
  description: "Template variable definition"
  fields:
    name: {type: str, required: true}
    description: {type: str, default: ""}
    default: {type: str, default: ""}
    required: {type: bool, default: false}

Template:
  description: "Document template definition"
  fields:
    name: {type: str, required: true}
    description: {type: str, default: ""}
    category: {type: str, default: "General"}
    content: {type: str, required: true}
    variables: {type: "list[TemplateVariable]", default: []}
```

---

## [SIGNALS] Signal/Slot Contracts

AI: Use these signal definitions when generating worker classes.

### Worker Signals

```yaml
# AI: Signal definitions for QThread workers

GitWorker:
  file: workers/git_worker.py
  base_class: BaseWorker
  signals:
    command_complete: {type: GitResult, description: "Git command finished"}
    status_ready: {type: GitStatus, description: "Repository status available"}
    detailed_status_ready: {type: dict, description: "Full status with file lists"}

GitHubCLIWorker:
  file: workers/github_cli_worker.py
  base_class: BaseWorker
  signals:
    github_result_ready: {type: GitHubResult, description: "GitHub CLI result"}

PandocWorker:
  file: workers/pandoc_worker.py
  base_class: QThread
  signals:
    conversion_complete: {type: "(str, str)", description: "(format, output_path)"}
    conversion_error: {type: "(str, str)", description: "(format, error_message)"}
    progress_update: {type: str, description: "Status message"}

PreviewWorker:
  file: workers/preview_worker.py
  base_class: QThread
  signals:
    render_complete: {type: str, description: "HTML content"}
    render_error: {type: str, description: "Error message"}
    ready: {type: null, description: "Worker initialized"}

OllamaChatWorker:
  file: workers/ollama_chat_worker.py
  base_class: QThread
  signals:
    chat_response_ready: {type: ChatMessage, description: "Complete response"}
    chat_response_chunk: {type: str, description: "Streaming chunk"}
    chat_error: {type: str, description: "Error message"}
    operation_cancelled: {type: null, description: "Cancellation confirmed"}

ClaudeWorker:
  file: claude/claude_worker.py
  base_class: QThread
  signals:
    response_ready: {type: object, description: "ClaudeResult"}
    connection_tested: {type: object, description: "ClaudeResult"}
    error_occurred: {type: str, description: "Error message"}

WorkerTask:
  file: workers/worker_tasks.py
  base_class: QObject
  signals:
    started: {type: null}
    progress: {type: "(int, str)", description: "(percentage, message)"}
    finished: {type: object, description: "Result"}
    error: {type: str}
    cancelled: {type: null}
```

### UI Handler Signals

```yaml
# AI: Signal definitions for UI handlers

FileHandler:
  file: ui/file_handler.py
  base_class: QObject
  signals:
    file_opened: {type: Path}
    file_saved: {type: Path}
    file_modified: {type: bool, description: "Unsaved changes state"}
    file_changed_externally: {type: Path}

PreviewHandlerBase:
  file: ui/preview_handler_base.py
  base_class: QObject
  signals:
    preview_updated: {type: str, description: "HTML content"}
    preview_error: {type: str}

QuickCommitWidget:
  file: ui/quick_commit_widget.py
  base_class: QWidget
  signals:
    commit_requested: {type: str, description: "Commit message"}
    cancelled: {type: null}
```

### Core Signals

```yaml
# AI: Signal definitions for core utilities

AsyncFileWatcher:
  file: core/async_file_watcher.py
  base_class: QObject
  signals:
    file_modified: {type: Path}
    file_deleted: {type: Path}
    file_created: {type: Path}
    error: {type: str}

QtAsyncFileManager:
  file: core/qt_async_file_manager.py
  base_class: QObject
  signals:
    read_complete: {type: "(Path, str)", description: "(path, content)"}
    write_complete: {type: Path}
    operation_failed: {type: "(str, Path, str)", description: "(operation, path, error)"}
    file_changed_externally: {type: Path}

LargeFileHandler:
  file: core/large_file_handler.py
  base_class: QObject
  signals:
    progress_update: {type: "(int, str)", description: "(percentage, message)"}
    file_loaded: {type: "(str, Path)", description: "(content, file_path)"}
```

---

## [SPEC] Critical Patterns

AI: MUST follow these patterns. Violations cause bugs.

### Threading Pattern

```python
# REQUIRED: All slow operations use QThread
# FILE: workers/*_worker.py

from PySide6.QtCore import QThread, Signal
from asciidoc_artisan.core.models import GitResult  # Example

class Worker(QThread):
    result_ready = Signal(GitResult)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._cancelled = False

    def run(self) -> None:
        try:
            if self._cancelled:
                return
            result = self._do_work()
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def cancel(self) -> None:
        self._cancelled = True
```

### Reentrancy Guard Pattern

```python
# REQUIRED: Prevent concurrent operations
# WHERE: Any method that triggers async work

def start_operation(self) -> None:
    if self._is_processing:
        return  # Guard against reentrancy
    self._is_processing = True
    try:
        # ... operation ...
    finally:
        self._is_processing = False
```

### Atomic Write Pattern

```python
# REQUIRED: All file writes use atomic_save_text
# FILE: core/file_operations.py

from asciidoc_artisan.core.file_operations import atomic_save_text
atomic_save_text(path, content)  # Uses temp file + rename
```

### Subprocess Safety Pattern

```python
# REQUIRED: Never use shell=True
# FILE: workers/git_worker.py, workers/github_cli_worker.py

import subprocess

def _build_subprocess_kwargs(
    self,
    working_dir: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    return {
        "cwd": working_dir,
        "capture_output": True,
        "text": True,
        "check": False,
        "shell": False,  # CRITICAL: prevents command injection
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
    }

# Usage:
subprocess.run(["git", "commit", "-m", message], **self._build_subprocess_kwargs())
# NEVER: subprocess.run(f"git commit -m {message}", shell=True)
```

### Manager Delegation Pattern

```python
# REQUIRED: main_window.py delegates to managers
# FILE: ui/main_window.py

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # Managers handle domain logic
        self.file_manager = FileManager(self)
        self.git_manager = GitManager(self)
        self.theme_manager = ThemeManager(self)
        self.status_manager = StatusManager(self)
        self.export_manager = ExportManager(self)
        self.menu_manager = MenuManager(self)
        # Logic lives in managers, NOT in MainWindow
```

### BaseWorker Pattern

```python
# REQUIRED: Workers inherit from BaseWorker for subprocess execution
# FILE: workers/base_worker.py

from PySide6.QtCore import QObject

class BaseWorker(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def reset_cancellation(self) -> None:
        self._cancelled = False

    def _check_cancellation(self) -> bool:
        return self._cancelled

    def _validate_working_directory(self, working_dir: str) -> bool:
        return Path(working_dir).is_dir()

    def _execute_subprocess(
        self,
        command: list[str],
        working_dir: str | None = None,
        timeout: int = 30,
    ) -> subprocess.CompletedProcess[str]:
        kwargs = self._build_subprocess_kwargs(working_dir, timeout)
        return subprocess.run(command, **kwargs)
```

---

## [SPEC] Error Codes

AI: Use these standardized error codes in syntax validation.

```yaml
# Error codes for SyntaxErrorModel.code field

syntax_errors:  # E001-E099 (red, breaks rendering)
  E001: "Unclosed source block"
  E002: "Unclosed example block"
  E003: "Unclosed sidebar block"
  E004: "Unclosed quote block"
  E005: "Unclosed literal block"
  E006: "Unclosed table"
  E007: "Unclosed passthrough block"
  E008: "Invalid heading level (exceeds parent)"
  E009: "Duplicate anchor ID"
  E010: "Missing required attribute"

semantic_errors:  # E100-E199 (red, semantic issues)
  E100: "Broken cross-reference (target not found)"
  E101: "Include file not found"
  E102: "Invalid attribute value"
  E103: "Circular include detected"
  E104: "Missing include file extension"

warnings:  # W001-W099 (yellow, potential issues)
  W001: "Heading level skipped"
  W002: "Empty section"
  W003: "Duplicate heading text"
  W004: "Long line (exceeds 120 characters)"
  W005: "Trailing whitespace"
  W006: "Mixed indentation (tabs and spaces)"
  W007: "Missing blank line before block"

style_issues:  # I001-I099 (blue, suggestions)
  I001: "Consider using semantic heading"
  I002: "Block could use title"
  I003: "Attribute could be simplified"
  I004: "Consider using include for repeated content"
  I005: "Section ordering suggestion"
```

---

## [SPEC] Directory Structure

AI: Generate files in these locations.

```yaml
# Project structure for code generation

src/
  main.py                           # Entry point
  asciidoc_artisan/
    __init__.py

    core/                           # Domain logic (no Qt UI)
      __init__.py
      settings.py                   # Settings dataclass
      models.py                     # Re-exports all models
      git_models.py                 # GitResult, GitStatus, GitHubResult
      chat_models.py                # ChatMessage
      completion_models.py          # CompletionKind, CompletionItem, CompletionContext
      syntax_models.py              # ErrorSeverity, TextEdit, QuickFix, SyntaxErrorModel
      template_models.py            # TemplateVariable, Template
      file_operations.py            # atomic_save_text, sanitize_path
      search_engine.py              # Find/replace logic
      spell_checker.py              # Spell check with pyspellchecker
      autocomplete_engine.py        # Completion logic
      syntax_checker.py             # Validation rules
      template_engine.py            # Template processing
      constants.py                  # App constants

    ui/                             # Qt UI components
      __init__.py
      main_window.py                # MainWindow (coordinator only)

      # Managers (domain-specific UI logic)
      file_manager.py               # File operations UI
      git_manager.py                # Git UI integration
      theme_manager.py              # Theme switching
      status_manager.py             # Status bar
      export_manager.py             # Export dialogs
      menu_manager.py               # Menu actions
      action_manager.py             # QAction factory
      spell_check_manager.py        # Spell check UI
      autocomplete_manager.py       # Autocomplete UI
      syntax_checker_manager.py     # Syntax check UI

      # Widgets
      find_bar_widget.py            # Find/replace bar
      chat_panel_widget.py          # AI chat panel
      chat_bar_widget.py            # Chat input bar
      quick_commit_widget.py        # Git quick commit
      line_number_area.py           # Editor line numbers
      autocomplete_widget.py        # Completion popup

      # Dialogs
      git_status_dialog.py          # Git status dialog
      github_dialogs.py             # GitHub PR/issue dialogs
      settings_editor_dialog.py     # Settings editor

      # Preview
      preview_handler_base.py       # Preview base class
      preview_handler_gpu.py        # GPU-accelerated preview
      preview_css_manager.py        # Preview themes

    workers/                        # Background threads
      __init__.py
      base_worker.py                # BaseWorker class
      git_worker.py                 # Git operations
      github_cli_worker.py          # GitHub CLI
      pandoc_worker.py              # Format conversion
      preview_worker.py             # Preview rendering
      ollama_chat_worker.py         # Ollama AI chat
      incremental_renderer.py       # Incremental preview

    claude/                         # Claude AI integration
      __init__.py
      claude_client.py              # API client
      claude_worker.py              # Background worker

    lsp/                            # Language Server Protocol
      __init__.py
      server.py                     # LSP server
      providers/                    # LSP providers

tests/
  unit/                             # Unit tests (pytest)
    core/
    ui/
    workers/
    claude/
    lsp/
  e2e/                              # End-to-end tests
  conftest.py                       # Shared fixtures
```

---

## [SPEC] Functional Requirements

### FR-001 to FR-005: Core Editor

| FR | Feature | Implementation | Validation |
|----|---------|----------------|------------|
| 001 | Text Editor | `ui/main_window.py` → QPlainTextEdit | Editor accepts input |
| 002 | Line Numbers | `ui/line_number_area.py` | 8 unit tests pass |
| 003 | Undo/Redo | Qt built-in | Ctrl+Z/Ctrl+Y work |
| 004 | Font Config | `core/settings.py` → monospace 10pt | Settings persist |
| 005 | State Persist | `core/settings.py` → cursor/scroll | Restore on reopen |

```yaml
# AI: Implementation details
FR-001:
  file: src/asciidoc_artisan/ui/main_window.py
  widget: QPlainTextEdit
  field_name: editor

FR-002:
  file: src/asciidoc_artisan/ui/line_number_area.py
  class: LineNumberArea
  tests: tests/unit/ui/test_line_number_area.py
  test_count: 8
```

### FR-006 to FR-014: File Operations

| FR | Feature | File | Notes |
|----|---------|------|-------|
| 006 | Open File | `ui/file_manager.py` | Ctrl+O |
| 007 | Save File | `ui/file_manager.py` | Atomic write, 15 tests |
| 008 | Save As | `ui/file_manager.py` | Ctrl+Shift+S |
| 009 | New File | `ui/file_manager.py` | Ctrl+N |
| 010 | Recent Files | `core/settings.py` | Max 10 entries |
| 011 | Auto-Save | `ui/file_manager.py` | 5-minute interval |
| 012 | DOCX Import | `core/document_converter.py` | python-docx |
| 013 | PDF Import | `core/document_converter.py` | PyMuPDF |
| 014 | Markdown Import | `workers/pandoc_worker.py` | Pandoc |

```yaml
# AI: Critical requirement
FR-007:
  file: src/asciidoc_artisan/ui/file_manager.py
  tests: tests/unit/ui/test_file_manager.py
  test_count: 15
  CRITICAL: Must use atomic_save_text(), never direct write

FR-011:
  interval_minutes: 5
  condition: document_modified AND file_path_exists
  timer_class: QTimer
```

### FR-015 to FR-020: Live Preview

| FR | Feature | File | Performance |
|----|---------|------|-------------|
| 015 | Live Preview | `workers/preview_worker.py` | <200ms |
| 016 | GPU Accel | `ui/preview_handler_gpu.py` | 10-50x speedup |
| 017 | Scroll Sync | `ui/preview_handler_base.py` | 8 tests |
| 018 | Incremental | `workers/incremental_renderer.py` | LRU(100) |
| 019 | Debounce | `ui/preview_handler_base.py` | 500ms |
| 020 | Preview Themes | `ui/preview_css_manager.py` | CSS injection |

### FR-021 to FR-025: Export

| FR | Feature | File | Tool |
|----|---------|------|------|
| 021 | HTML Export | `ui/export_manager.py` | asciidoc3 |
| 022 | PDF Export | `ui/export_manager.py` | wkhtmltopdf |
| 023 | DOCX Export | `workers/pandoc_worker.py` | Pandoc |
| 024 | Markdown Export | `workers/pandoc_worker.py` | Pandoc |
| 025 | AI Assist | `workers/ollama_chat_worker.py` | Ollama |

### FR-026 to FR-033: Git Integration

| FR | Feature | File | Notes |
|----|---------|------|-------|
| 026 | Repo Detection | `ui/git_manager.py` | .git directory check |
| 027 | Commit | `workers/git_worker.py` | shell=False required |
| 028 | Pull | `workers/git_worker.py` | 8 tests |
| 029 | Push | `workers/git_worker.py` | Async |
| 030 | Status Display | `ui/status_manager.py` | Icons: checkmark/warning |
| 031 | Status Dialog | `ui/git_status_dialog.py` | 3-tab layout |
| 032 | Quick Commit | `ui/quick_commit_widget.py` | Ctrl+G |
| 033 | Cancel Operation | `workers/git_worker.py` | Cancelable workers |

### FR-034 to FR-038: GitHub CLI

| FR | Feature | File | Command |
|----|---------|------|---------|
| 034 | Create PR | `workers/github_cli_worker.py` | gh pr create |
| 035 | List PRs | `workers/github_cli_worker.py` | gh pr list |
| 036 | Create Issue | `workers/github_cli_worker.py` | gh issue create |
| 037 | List Issues | `workers/github_cli_worker.py` | gh issue list |
| 038 | Repo Info | `workers/github_cli_worker.py` | gh repo view |

### FR-039 to FR-044: AI Integration

| FR | Feature | File | Notes |
|----|---------|------|-------|
| 039 | Ollama Client | `workers/ollama_chat_worker.py` | 82 tests |
| 040 | Chat Panel | `ui/chat_panel_widget.py` | Dockable |
| 041 | Chat Modes | `ui/chat_bar_widget.py` | 4 modes |
| 042 | Chat History | `core/settings.py` | Max 100 messages |
| 043 | Model Select | `ui/chat_bar_widget.py` | Dropdown |
| 044 | Panel Toggle | `ui/menu_manager.py` | Tools menu |

### FR-045 to FR-054: Find & Spell Check

| FR | Feature | File |
|----|---------|------|
| 045 | Search Engine | `core/search_engine.py` |
| 046 | Find Bar | `ui/find_bar_widget.py` |
| 047 | Navigation | `ui/find_bar_widget.py` |
| 048 | Replace | `ui/find_bar_widget.py` |
| 049 | Replace All | `core/search_engine.py` |
| 050 | Spell Check | `core/spell_checker.py` |
| 051 | Check Manager | `ui/spell_check_manager.py` |
| 052 | Context Menu | `ui/spell_check_manager.py` |
| 053 | Custom Dict | `core/spell_checker.py` |
| 054 | Languages | `core/spell_checker.py` |

### FR-055 to FR-067c: UI & Performance

| FR | Feature | Target |
|----|---------|--------|
| 055 | Theme System | Dark/Light |
| 056 | Status Bar | File info |
| 057 | Doc Metrics | Word count |
| 058 | Window Title | File name |
| 059 | Splitter | Resizable |
| 060 | Toolbar | Actions |
| 061 | Menu System | Full menus |
| 062 | Startup | <1.0s |
| 063 | Thread Pool | CPU x 2 |
| 064 | Memory | <100MB |
| 065 | Async I/O | aiofiles |
| 066 | Block Render | 10-14% |
| 067 | Cache Hit | >50% |
| 067a | Incremental | 10-50x |
| 067b | Predictive | >20% |
| 067c | Priority | Visible first |

### FR-068 to FR-072: Security

| FR | Feature | Implementation |
|----|---------|----------------|
| 068 | Path Sanitization | `sanitize_path()` |
| 069 | Atomic Writes | temp + rename |
| 070 | Subprocess Safety | shell=False |
| 071 | Credential Storage | OS keyring |
| 072 | HTTPS Only | SSL/TLS |

### FR-073 to FR-109: Infrastructure & Features

| FR | Feature | Notes |
|----|---------|-------|
| 073-084 | Infrastructure | Telemetry, settings, tests |
| 085-090 | Autocomplete | <50ms response |
| 091-099 | Syntax Check | Real-time validation |
| 100-107 | Templates | 6 built-in types |
| 108 | MA Compliance | <400 lines/file |
| 109 | LSP Protocol | 108 tests |

---

## [VALIDATE] Acceptance Criteria

### Mandatory Checks

```bash
# AI: Run ALL validation commands. ALL must pass.

# 1. Test Suite
make test
# Expected: 5,139 tests pass, 0 failures

# 2. Type Checking
mypy --strict src/
# Expected: Success: no issues found

# 3. Security Audit
grep -r "shell=True" src/
# Expected: No matches (exit code 1)

grep -r "subprocess.run.*shell" src/ | grep -v "shell=False"
# Expected: No matches (exit code 1)

# 4. MA Compliance
find src/ -name "*.py" -exec wc -l {} \; | awk '$1 > 400 {print}'
# Expected: Empty output (no files over 400 lines)

# 5. Model Validation
python -c "from asciidoc_artisan.core.models import *; print('Models OK')"
# Expected: Models OK
```

### Performance Benchmarks

| Operation | Target | Validation Command |
|-----------|--------|-------------------|
| Startup | <1.0s | `time python -c "import asciidoc_artisan"` |
| Preview | <200ms | `pytest tests/unit/workers/test_preview_worker.py -v` |
| Autocomplete | <50ms | `pytest tests/unit/lsp/ -v` |

---

## [SPEC] Quick Reference

```yaml
# AI: Copy-paste commands for common tasks

run_app:
  optimized: make run
  normal: python3 src/main.py

test:
  all: make test
  unit: pytest tests/unit/ -v
  e2e: pytest tests/e2e/ -v
  single: pytest tests/unit/MODULE/ -v
  coverage: pytest --cov=src/asciidoc_artisan --cov-report=term-missing

quality:
  format: make format
  lint: make lint
  types: mypy --strict src/

dependencies:
  python: pip install -r requirements.txt
  system: sudo apt install pandoc wkhtmltopdf gh

code_generation:
  models: "Generate from [SCHEMA] sections"
  workers: "Generate from [SIGNALS] sections"
  patterns: "Follow [SPEC] Critical Patterns"
```

---

## [CONTEXT] Architecture Decisions

**Why Manager Architecture?**
The codebase originally had a monolithic main_window.py exceeding 2,000 lines. MA refactoring split responsibilities into focused managers, each under 400 lines, improving maintainability and testability.

**Why QThread over asyncio?**
PySide6/Qt has native signal/slot threading that integrates cleanly with the GUI event loop. QThread workers communicate via signals, avoiding callback complexity.

**Why Atomic Writes?**
Power loss during file writes corrupts data. The temp+rename pattern ensures either the old or new file exists completely—never a partial write.

**Why Pydantic Models?**
Pydantic provides runtime validation, JSON serialization, and type hints in one package. All data crossing boundaries (settings, worker results, API responses) uses validated models.

---

## [CONTEXT] Change History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2025-12-05 | Public release, specification-driven coding |
| 2.0.0 | 2025-11-15 | LSP integration, 109 FRs |
| 1.5.0 | 2025-10-01 | AI integration (Ollama) |
| 1.0.0 | 2025-08-01 | Initial release |

---

*v2.1.0 | 109 FRs | Specification-Driven | Code-Generatable | Dec 5, 2025*
