# Data Schemas

**v2.1.0** | Pydantic models for AI code generation

---

## [SPEC] Code Generation

```yaml
# AI INSTRUCTION: Generate Pydantic models from these schemas

generation_rules:
  base_config: |
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="forbid",
    )

  imports: |
    from dataclasses import dataclass, field
    from enum import Enum
    from pathlib import Path
    from pydantic import BaseModel, ConfigDict
    from typing import Any

  file_location: core/{name}_models.py
```

---

## [SPEC] Settings Schema

```yaml
# File: core/settings.py
# Storage: TOON format (auto-migrates from JSON)

Settings:
  description: "Application settings with TOON persistence"

  persistence:
    format: TOON
    fallback: JSON
    paths:
      linux: "~/.config/AsciiDocArtisan/AsciiDocArtisan.toon"
      windows: "%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.toon"
      macos: "~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.toon"

  fields:
    # Path fields
    last_directory:
      type: str
      default: "str(Path.home())"
      description: "Last opened directory"

    last_file:
      type: "str | None"
      default: null
      description: "Last opened file path"

    git_repo_path:
      type: "str | None"
      default: null
      description: "Active git repository"

    # UI state
    dark_mode:
      type: bool
      default: true
      description: "Dark theme enabled"

    maximized:
      type: bool
      default: true
      description: "Window maximized state"

    window_geometry:
      type: "dict[str, int] | None"
      default: null
      description: "{x, y, width, height}"

    splitter_sizes:
      type: "list[int] | None"
      default: null
      description: "[editor, preview, chat]"

    # Editor
    font_size:
      type: int
      default: 12
      range: [8, 72]
      description: "Editor font size"

    editor_font_family:
      type: str
      default: "Courier New"

    # Auto-save
    auto_save_enabled:
      type: bool
      default: true

    auto_save_interval:
      type: int
      default: 300
      unit: seconds

    # AI
    ai_backend:
      type: str
      default: "ollama"
      choices: [ollama, claude]

    ollama_enabled:
      type: bool
      default: true

    ollama_model:
      type: "str | None"
      default: "neural-chat:latest"

    ai_chat_enabled:
      type: bool
      default: true

    # Features
    spell_check_enabled:
      type: bool
      default: true

    spell_check_language:
      type: str
      default: "en"

    autocomplete_enabled:
      type: bool
      default: true

    syntax_check_realtime_enabled:
      type: bool
      default: true

    # Telemetry
    telemetry_enabled:
      type: bool
      default: false
      description: "Opt-in telemetry"

    telemetry_session_id:
      type: "str | None"
      default: null
```

---

## [SPEC] Git Models

```yaml
# File: core/git_models.py

GitResult:
  description: "Result from git command execution"
  fields:
    success:
      type: bool
      required: true
    stdout:
      type: str
      default: ""
    stderr:
      type: str
      default: ""
    exit_code:
      type: "int | None"
      default: null
    user_message:
      type: str
      required: true
      description: "Human-readable result message"

GitStatus:
  description: "Repository status summary"
  fields:
    branch:
      type: str
      default: ""
    modified_count:
      type: int
      default: 0
    staged_count:
      type: int
      default: 0
    untracked_count:
      type: int
      default: 0
    is_dirty:
      type: bool
      default: false
      computed: "modified_count > 0 or staged_count > 0"

GitHubResult:
  description: "Result from GitHub CLI command"
  fields:
    success:
      type: bool
      required: true
    data:
      type: "dict[str, Any] | list[Any] | None"
      default: null
    error:
      type: str
      default: ""
    user_message:
      type: str
      required: true
    operation:
      type: str
      choices: [pr_create, pr_list, issue_create, issue_list, repo_view]
```

---

## [SPEC] Completion Models

```yaml
# File: core/completion_models.py

CompletionKind:
  type: enum
  values:
    SYNTAX: 1       # AsciiDoc syntax (= == ===)
    ATTRIBUTE: 2    # :attribute:
    XREF: 3         # <<anchor>>
    INCLUDE: 4      # include::
    SNIPPET: 5      # Code snippets

CompletionItem:
  description: "Single completion suggestion"
  fields:
    text:
      type: str
      required: true
      description: "Display text"
    kind:
      type: CompletionKind
      required: true
    detail:
      type: str
      default: ""
      description: "Additional info"
    insert_text:
      type: "str | None"
      default: null
      description: "Text to insert (if different from text)"
    score:
      type: float
      default: 0.0
      description: "Relevance score for sorting"

CompletionContext:
  description: "Context for completion request"
  fields:
    line:
      type: str
      required: true
    line_number:
      type: int
      required: true
    column:
      type: int
      required: true
    prefix:
      type: str
      required: true
      description: "Text before cursor"
    manual:
      type: bool
      default: false
      description: "User triggered (Ctrl+Space)"
```

---

## [SPEC] Syntax Models

```yaml
# File: core/syntax_models.py

ErrorSeverity:
  type: enum
  values:
    ERROR: 1
    WARNING: 2
    INFO: 3

TextEdit:
  description: "Text range edit for quick fixes"
  fields:
    start_line:
      type: int
      required: true
    start_column:
      type: int
      required: true
    end_line:
      type: int
      required: true
    end_column:
      type: int
      required: true
    new_text:
      type: str
      required: true

QuickFix:
  description: "Suggested fix for syntax error"
  fields:
    title:
      type: str
      required: true
      description: "Display title for fix"
    edits:
      type: "list[TextEdit]"
      default: []

SyntaxErrorModel:
  description: "Syntax error with location and fixes"
  fields:
    code:
      type: str
      pattern: "[EWI][0-9]{3}"
      description: "Error code (E001, W002, I003)"
    severity:
      type: ErrorSeverity
      required: true
    message:
      type: str
      required: true
    line:
      type: int
      required: true
    column:
      type: int
      required: true
    length:
      type: int
      required: true
      description: "Length of error span"
    fixes:
      type: "list[QuickFix]"
      default: []
```

---

## [SPEC] Template Models

```yaml
# File: core/template_models.py

TemplateVariable:
  description: "Variable placeholder in template"
  fields:
    name:
      type: str
      required: true
      pattern: "[a-z_][a-z0-9_]*"
    description:
      type: str
      default: ""
    default:
      type: str
      default: ""
    required:
      type: bool
      default: false

Template:
  description: "Document template with variables"
  fields:
    name:
      type: str
      required: true
    description:
      type: str
      default: ""
    category:
      type: str
      default: "General"
      choices: [General, Technical, Academic, Business]
    content:
      type: str
      required: true
      description: "Template content with ${var} placeholders"
    variables:
      type: "list[TemplateVariable]"
      default: []
```

---

## [SPEC] Chat Models

```yaml
# File: core/chat_models.py

ChatMessage:
  description: "Single chat message"
  fields:
    role:
      type: str
      required: true
      choices: [user, assistant]
    content:
      type: str
      required: true
    timestamp:
      type: float
      required: true
      description: "Unix timestamp"
    model:
      type: str
      required: true
      description: "Model that generated response"
    context_mode:
      type: str
      required: true
      choices: [document, syntax, general, editing]
```

---

## [SPEC] GPU Models

```yaml
# File: core/gpu_models.py
# Cache: ~/.config/AsciiDocArtisan/gpu_cache.toon

GPUInfo:
  description: "Detected GPU information"
  fields:
    gpu_type:
      type: str
      choices: [nvidia, amd, intel, apple, software, unknown]
    gpu_name:
      type: str
      default: ""
    driver_version:
      type: str
      default: ""
    render_device:
      type: str
      default: ""
    supports_webengine:
      type: bool
      default: false
    supports_webgl:
      type: bool
      default: false

GPUCacheEntry:
  description: "Cached GPU detection result"
  fields:
    gpu_info:
      type: GPUInfo
      required: true
    timestamp:
      type: str
      required: true
      description: "ISO format timestamp"
    version:
      type: str
      required: true
      description: "App version when cached"

  methods:
    is_valid(ttl_days: int) -> bool:
      description: "Check if cache entry is within TTL"
```

---

## [SPEC] Telemetry Models

```yaml
# File: core/telemetry_collector.py
# Storage: ~/.config/AsciiDocArtisan/telemetry.toon

TelemetryEvent:
  description: "Single telemetry event"
  fields:
    event_type:
      type: str
      required: true
      choices: [menu_click, dialog_open, error, performance, startup, feature_use]
    timestamp:
      type: str
      required: true
      description: "ISO UTC timestamp"
    session_id:
      type: str
      required: true
      description: "Anonymous UUID"
    data:
      type: "dict[str, Any]"
      default: {}
      description: "Event-specific data (NO PII)"
```

---

## [SPEC] Example Generation

```python
# AI: Use this pattern to generate Pydantic models

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ErrorSeverity(Enum):
    """Syntax error severity levels."""
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


@dataclass
class TextEdit:
    """Text range edit for quick fixes."""
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    new_text: str


@dataclass
class QuickFix:
    """Suggested fix for syntax error."""
    title: str
    edits: list[TextEdit] = field(default_factory=list)


@dataclass
class SyntaxErrorModel:
    """Syntax error with location and fixes."""
    code: str  # Pattern: [EWI][0-9]{3}
    severity: ErrorSeverity
    message: str
    line: int
    column: int
    length: int
    fixes: list[QuickFix] = field(default_factory=list)
```

---

*v2.1.0 | AI code generation schemas | TOON format | Dec 5, 2025*
