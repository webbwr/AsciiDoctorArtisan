# Data Schemas

**v2.1.0** | Pydantic model definitions for code generation

---

## Usage

AI: Generate Pydantic models from these schemas. Use `model_config = {"frozen": False, "validate_assignment": True}`.

---

## Settings

```yaml
# File: core/settings.py
Settings:
  description: "Application settings with JSON persistence"
  persistence_path:
    linux: ~/.config/AsciiDocArtisan/AsciiDocArtisan.json
    windows: "%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json"
    macos: ~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json

  fields:
    # Paths
    last_directory: {type: str, default: "Path.home()"}
    last_file: {type: "str | None", default: null}
    git_repo_path: {type: "str | None", default: null}

    # UI
    dark_mode: {type: bool, default: true}
    maximized: {type: bool, default: true}
    window_geometry: {type: "dict[str, int] | None", default: null}
    splitter_sizes: {type: "list[int] | None", default: null}

    # Auto-save
    auto_save_enabled: {type: bool, default: true}
    auto_save_interval: {type: int, default: 300, unit: seconds}

    # AI
    ai_backend: {type: str, default: "ollama", choices: [ollama, claude]}
    ollama_enabled: {type: bool, default: true}
    ollama_model: {type: "str | None", default: "gnokit/improve-grammer"}

    # Fonts
    editor_font_family: {type: str, default: "Courier New"}
    editor_font_size: {type: int, default: 12, range: "8-72"}

    # Features
    spell_check_enabled: {type: bool, default: true}
    autocomplete_enabled: {type: bool, default: true}
    syntax_check_realtime_enabled: {type: bool, default: true}
```

---

## Git Models

```yaml
# File: core/git_models.py

GitResult:
  fields:
    success: {type: bool, required: true}
    stdout: {type: str, default: ""}
    stderr: {type: str, default: ""}
    exit_code: {type: "int | None", default: null}
    user_message: {type: str, required: true}

GitStatus:
  fields:
    branch: {type: str, default: ""}
    modified_count: {type: int, default: 0}
    staged_count: {type: int, default: 0}
    untracked_count: {type: int, default: 0}
    is_dirty: {type: bool, default: false}

GitHubResult:
  fields:
    success: {type: bool, required: true}
    data: {type: "dict | list | None", default: null}
    error: {type: str, default: ""}
    user_message: {type: str, required: true}
    operation: {type: str, choices: [pr_create, pr_list, issue_create, issue_list, repo_view]}
```

---

## Completion Models

```yaml
# File: core/completion_models.py

CompletionKind:
  type: enum
  values: [SYNTAX, ATTRIBUTE, XREF, INCLUDE, SNIPPET]

CompletionItem:
  fields:
    text: {type: str, required: true}
    kind: {type: CompletionKind, required: true}
    detail: {type: str, default: ""}
    insert_text: {type: "str | None", default: null}
    score: {type: float, default: 0.0}

CompletionContext:
  fields:
    line: {type: str, required: true}
    line_number: {type: int, required: true}
    column: {type: int, required: true}
    prefix: {type: str, required: true}
    manual: {type: bool, default: false}
```

---

## Syntax Models

```yaml
# File: core/syntax_models.py

ErrorSeverity:
  type: enum
  values: [ERROR, WARNING, INFO]

TextEdit:
  fields:
    start_line: {type: int, required: true}
    start_column: {type: int, required: true}
    end_line: {type: int, required: true}
    end_column: {type: int, required: true}
    new_text: {type: str, required: true}

QuickFix:
  fields:
    title: {type: str, required: true}
    edits: {type: "list[TextEdit]", default: []}

SyntaxErrorModel:
  fields:
    code: {type: str, pattern: "[EWI][0-9]{3}"}
    severity: {type: ErrorSeverity, required: true}
    message: {type: str, required: true}
    line: {type: int, required: true}
    column: {type: int, required: true}
    length: {type: int, required: true}
    fixes: {type: "list[QuickFix]", default: []}
```

---

## Template Models

```yaml
# File: core/template_models.py

TemplateVariable:
  fields:
    name: {type: str, required: true}
    description: {type: str, default: ""}
    default: {type: str, default: ""}
    required: {type: bool, default: false}

Template:
  fields:
    name: {type: str, required: true}
    description: {type: str, default: ""}
    category: {type: str, default: "General"}
    content: {type: str, required: true}
    variables: {type: "list[TemplateVariable]", default: []}
```

---

## Chat Models

```yaml
# File: core/chat_models.py

ChatMessage:
  fields:
    role: {type: str, choices: [user, assistant]}
    content: {type: str, required: true}
    timestamp: {type: float, required: true}
    model: {type: str, required: true}
    context_mode: {type: str, choices: [document, syntax, general, editing]}
```

---

*v2.1.0 | AI code generation schemas | Dec 5, 2025*
