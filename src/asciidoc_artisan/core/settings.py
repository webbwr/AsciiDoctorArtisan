"""
Application settings data model and persistence.

Settings dataclass stores user preferences, persists to JSON in platform-appropriate dirs (Linux: ~/.config/AsciiDoc Artisan/AsciiDocArtisan.json, Windows: %APPDATA%/AsciiDoc Artisan/AsciiDocArtisan.json, macOS: ~/Library/Application Support/AsciiDoc Artisan/AsciiDocArtisan.json).
Security: API keys NOT stored here (FR-061).
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .constants import EDITOR_FONT_SIZE


@dataclass
class Settings:
    """Application settings with persistence (35 fields: 13 core, 6 font, 5 AI, 5 chat, 3 spell, 3 autocomplete, 3 syntax, 2 template, 3 telemetry). Core: last_directory/file, git_repo_path, dark_mode, maximized, window_geometry, splitter_sizes, font_size (deprecated), auto_save (enabled/interval). Font: editor/preview/chat (family/size). AI: ai_backend (ollama/claude), ollama_enabled/model, claude_model. Chat: ai_chat_enabled, history, max_history, context_mode, send_document. Spell: enabled, language, custom_words. Autocomplete: enabled, delay, min_chars. Syntax: realtime_enabled, delay, show_underlines. Template: last_category, recent_limit. Telemetry: enabled (opt-in), session_id (UUID), opt_in_shown. Security: Local storage only, no cloud uploads, Ollama for local AI."""

    last_directory: str = field(default_factory=lambda: str(Path.home()))
    last_file: str | None = None
    git_repo_path: str | None = None
    dark_mode: bool = True
    maximized: bool = True  # Start maximized by default
    window_geometry: dict[str, int] | None = None
    splitter_sizes: list[int] | None = None
    font_size: int = EDITOR_FONT_SIZE
    auto_save_enabled: bool = True
    auto_save_interval: int = 300
    ai_conversion_enabled: bool = False

    # AI Backend settings (v1.10.0+)
    ai_backend: str = "ollama"  # "ollama" or "claude"
    ollama_enabled: bool = True  # Enable Ollama by default for chat
    ollama_model: str | None = "gnokit/improve-grammer"  # Default model for chat
    claude_model: str | None = "claude-sonnet-4-20250514"  # Default Claude model (Claude Sonnet 4)

    # Chat settings (v1.7.0, v1.10.0+ backend-agnostic)
    ai_chat_enabled: bool = True  # Enable chat by default
    chat_history: list[dict[str, Any]] = field(default_factory=list)
    chat_max_history: int = 100
    chat_context_mode: str = "document"
    chat_send_document: bool = True

    # Backward compatibility aliases (deprecated, kept for migration)
    ollama_chat_enabled: bool = True  # Deprecated: use ai_chat_enabled
    ollama_chat_history: list[dict[str, Any]] = field(default_factory=list)  # Deprecated: use chat_history
    ollama_chat_max_history: int = 100  # Deprecated: use chat_max_history
    ollama_chat_context_mode: str = "document"  # Deprecated: use chat_context_mode
    ollama_chat_send_document: bool = True  # Deprecated: use chat_send_document

    # Font settings (v1.7.0)
    editor_font_family: str = "Courier New"
    editor_font_size: int = 12
    preview_font_family: str = "Arial"
    preview_font_size: int = 12
    chat_font_family: str = "Arial"
    chat_font_size: int = 11

    # Spell check settings (v1.8.0)
    spell_check_enabled: bool = True
    spell_check_language: str = "en"
    spell_check_custom_words: list[str] = field(default_factory=list)

    # Auto-complete settings (v2.0.0)
    autocomplete_enabled: bool = True
    autocomplete_delay: int = 300  # milliseconds
    autocomplete_min_chars: int = 2

    # Syntax checking settings (v2.0.0)
    syntax_check_realtime_enabled: bool = True
    syntax_check_delay: int = 500  # milliseconds
    syntax_check_show_underlines: bool = True

    # Template settings (v2.0.0)
    template_last_category: str = "All"
    template_recent_limit: int = 10

    # Telemetry settings (v1.8.0)
    telemetry_enabled: bool = False  # Opt-in only (GDPR compliant)
    telemetry_session_id: str | None = None  # Anonymous UUID, generated on first enable
    telemetry_opt_in_shown: bool = False  # Whether opt-in dialog has been shown

    # First-run experience settings (v2.1.0)
    welcome_shown: bool = False  # Whether welcome dialog has been shown on first run

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary for JSON serialization. Returns dict suitable for json.dumps()."""
        return asdict(self)

    @staticmethod
    def _migrate_claude_model(model: str | None) -> str | None:
        """Migrate deprecated Claude 3.5 model names to Claude 4 equivalents (backward compatibility for pre-v1.9.1). Args: model (old/new format). Returns: Migrated model or None. Example: 'claude-3-5-sonnet-20241022' → 'claude-sonnet-4-20250514'."""
        if not model:
            return model

        # Migration map: Claude 3.5 → Claude 4
        migrations = {
            "claude-3-5-sonnet-20241022": "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20240620": "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022": "claude-haiku-4-5",
        }

        if model in migrations:
            new_model = migrations[model]
            # Log migration for debugging (using print since we're in a dataclass)
            print(f"Settings: Migrated Claude model {model} → {new_model}")
            return new_model

        return model

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        """Create Settings from dict with forward/backward compatibility (filters unknown keys). Migrations: ollama_chat_* → chat_* (v1.10.0+), Claude 3.5 → Claude 4 (v1.9.1+). Args: data (JSON dict). Returns: Settings with valid fields."""
        # Migrate deprecated ollama_chat_* settings to new chat_* settings (v1.10.0)
        if "ollama_chat_enabled" in data and "ai_chat_enabled" not in data:
            data["ai_chat_enabled"] = data["ollama_chat_enabled"]

        if "ollama_chat_history" in data and "chat_history" not in data:
            data["chat_history"] = data["ollama_chat_history"]

        if "ollama_chat_max_history" in data and "chat_max_history" not in data:
            data["chat_max_history"] = data["ollama_chat_max_history"]

        if "ollama_chat_context_mode" in data and "chat_context_mode" not in data:
            data["chat_context_mode"] = data["ollama_chat_context_mode"]

        if "ollama_chat_send_document" in data and "chat_send_document" not in data:
            data["chat_send_document"] = data["ollama_chat_send_document"]

        # Migrate deprecated Claude 3.5 model names to Claude 4 (v1.9.1+)
        if "claude_model" in data:
            data["claude_model"] = cls._migrate_claude_model(data["claude_model"])

        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def _validate_bool(self, field_name: str, default: bool, issues: list[str]) -> None:
        """Validate boolean field."""
        value = getattr(self, field_name)
        if not isinstance(value, bool):
            issues.append(f"Invalid {field_name}: {value}")
            setattr(self, field_name, default)

    def _validate_int_range(self, field_name: str, min_val: int, max_val: int, default: int, issues: list[str]) -> None:
        """Validate integer field within range."""
        value = getattr(self, field_name)
        if not isinstance(value, int) or not (min_val <= value <= max_val):
            issues.append(f"Invalid {field_name}: {value}")
            setattr(self, field_name, default)

    def _validate_string(self, field_name: str, default: str, issues: list[str], optional: bool = False) -> None:
        """Validate string field."""
        value = getattr(self, field_name)
        if optional and value is None:
            return
        if value is None or not isinstance(value, str) or not value:
            issues.append(f"Invalid {field_name}: {value}")
            setattr(self, field_name, default if not optional else None)

    def _validate_string_choice(self, field_name: str, choices: list[str], default: str, issues: list[str]) -> None:
        """Validate string field against allowed choices."""
        value = getattr(self, field_name)
        if not isinstance(value, str) or value not in choices:
            issues.append(f"Invalid {field_name}: {value}")
            setattr(self, field_name, default)

    def _validate_directory_path(self, field_name: str, default: str, issues: list[str]) -> None:
        """Validate directory path exists."""
        value = getattr(self, field_name)
        if not isinstance(value, str) or not value:
            issues.append(f"Invalid {field_name}: {value}")
            setattr(self, field_name, default)
        elif not Path(value).is_dir():
            issues.append(f"{field_name} does not exist: {value}")
            setattr(self, field_name, default)

    def _validate_window_geometry(self, issues: list[str]) -> None:
        """Validate window geometry dict structure."""
        if self.window_geometry is not None:
            if not isinstance(self.window_geometry, dict):
                issues.append(f"Invalid window_geometry type: {type(self.window_geometry)}")
                self.window_geometry = None
            elif not all(key in self.window_geometry for key in ["x", "y", "width", "height"]):
                issues.append(f"Missing window_geometry keys: {self.window_geometry.keys()}")
                self.window_geometry = None

    def _validate_splitter_sizes(self, issues: list[str]) -> None:
        """Validate splitter sizes list structure."""
        if self.splitter_sizes is not None:
            if not isinstance(self.splitter_sizes, list):
                issues.append(f"Invalid splitter_sizes type: {type(self.splitter_sizes)}")
                self.splitter_sizes = None
            elif not (2 <= len(self.splitter_sizes) <= 3):
                issues.append(f"Invalid splitter_sizes length: {len(self.splitter_sizes)}")
                self.splitter_sizes = None
            elif not all(isinstance(s, int) and s >= 0 for s in self.splitter_sizes):
                issues.append(f"Invalid splitter_sizes values: {self.splitter_sizes}")
                self.splitter_sizes = None

    def _validate_list_of_strings(self, field_name: str, issues: list[str]) -> None:
        """Validate list contains only strings."""
        value = getattr(self, field_name)
        if not isinstance(value, list):
            issues.append(f"Invalid {field_name} type: {type(value)}")
            setattr(self, field_name, [])
        elif not all(isinstance(item, str) for item in value):
            issues.append(f"{field_name} contains non-string values")
            setattr(self, field_name, [item for item in value if isinstance(item, str)])

    def _validate_path_settings(self, issues: list[str]) -> None:
        """Validate directory and file path settings. MA principle: Extracted (3 calls)."""
        self._validate_directory_path("last_directory", str(Path.home()), issues)
        self._validate_string("last_file", "", issues, optional=True)
        self._validate_string("git_repo_path", "", issues, optional=True)

    def _validate_ui_settings(self, issues: list[str]) -> None:
        """Validate UI appearance and layout settings. MA principle: Extracted (5 calls)."""
        self._validate_bool("dark_mode", True, issues)
        self._validate_bool("maximized", True, issues)
        self._validate_window_geometry(issues)
        self._validate_splitter_sizes(issues)
        self._validate_int_range("font_size", 8, 72, 12, issues)

    def _validate_auto_save_settings(self, issues: list[str]) -> None:
        """Validate auto-save configuration. MA principle: Extracted (2 calls)."""
        self._validate_bool("auto_save_enabled", True, issues)
        self._validate_int_range("auto_save_interval", 30, 3600, 300, issues)

    def _validate_ai_settings(self, issues: list[str]) -> None:
        """Validate AI backend settings. MA principle: Extracted (5 calls)."""
        self._validate_string_choice("ai_backend", ["ollama", "claude"], "ollama", issues)
        self._validate_bool("ollama_enabled", True, issues)
        self._validate_string("ollama_model", "", issues, optional=True)
        self._validate_string("claude_model", "", issues, optional=True)
        self._validate_bool("ai_chat_enabled", True, issues)

    def _validate_chat_settings(self, issues: list[str]) -> None:
        """Validate chat configuration. MA principle: Extracted (6 calls)."""
        if not isinstance(self.chat_history, list):
            issues.append(f"Invalid chat_history type: {type(self.chat_history)}")
            self.chat_history = []

        self._validate_int_range("chat_max_history", 10, 1000, 100, issues)
        self._validate_string_choice(
            "chat_context_mode",
            ["document", "syntax", "general", "editing"],
            "document",
            issues,
        )
        self._validate_bool("chat_send_document", True, issues)

    def _validate_font_settings(self, issues: list[str]) -> None:
        """Validate font family and size settings. MA principle: Extracted (6 calls)."""
        self._validate_string("editor_font_family", "Courier New", issues)
        self._validate_int_range("editor_font_size", 8, 72, 12, issues)
        self._validate_string("preview_font_family", "Arial", issues)
        self._validate_int_range("preview_font_size", 8, 72, 12, issues)
        self._validate_string("chat_font_family", "Arial", issues)
        self._validate_int_range("chat_font_size", 8, 72, 11, issues)

    def _validate_spell_check_settings(self, issues: list[str]) -> None:
        """Validate spell check configuration. MA principle: Extracted (3 calls)."""
        self._validate_bool("spell_check_enabled", True, issues)
        self._validate_string("spell_check_language", "en", issues)
        self._validate_list_of_strings("spell_check_custom_words", issues)

    def _validate_autocomplete_settings(self, issues: list[str]) -> None:
        """Validate autocomplete configuration. MA principle: Extracted (3 calls)."""
        self._validate_bool("autocomplete_enabled", True, issues)
        self._validate_int_range("autocomplete_delay", 100, 5000, 300, issues)
        self._validate_int_range("autocomplete_min_chars", 1, 10, 2, issues)

    def _validate_syntax_check_settings(self, issues: list[str]) -> None:
        """Validate syntax checking configuration. MA principle: Extracted (3 calls)."""
        self._validate_bool("syntax_check_realtime_enabled", True, issues)
        self._validate_int_range("syntax_check_delay", 100, 10000, 500, issues)
        self._validate_bool("syntax_check_show_underlines", True, issues)

    def _validate_template_settings(self, issues: list[str]) -> None:
        """Validate template configuration. MA principle: Extracted (2 calls)."""
        self._validate_string("template_last_category", "All", issues)
        self._validate_int_range("template_recent_limit", 1, 50, 10, issues)

    def _validate_telemetry_settings(self, issues: list[str]) -> None:
        """Validate telemetry configuration. MA principle: Extracted (3 calls)."""
        self._validate_bool("telemetry_enabled", False, issues)
        self._validate_string("telemetry_session_id", "", issues, optional=True)
        self._validate_bool("telemetry_opt_in_shown", False, issues)

    def _validate_first_run_settings(self, issues: list[str]) -> None:
        """Validate first-run experience settings. MA principle: Extracted (1 call)."""
        self._validate_bool("welcome_shown", False, issues)

    def _log_validation_results(self, issues: list[str]) -> None:
        """Log validation results. MA principle: Extracted (6 lines)."""
        import logging

        logger = logging.getLogger(__name__)
        if issues:
            logger.warning(f"Settings validation found {len(issues)} issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("Settings validation: all fields valid")

    def validate(self) -> "Settings":
        """Validate all settings fields and apply corrections (MA: 96→27 lines, 12 helpers, 72% reduction). Checks types, ranges, applies defaults for invalid values, logs issues. Returns: Self (chaining)."""
        issues: list[str] = []

        # Validate all settings categories
        self._validate_path_settings(issues)
        self._validate_ui_settings(issues)
        self._validate_auto_save_settings(issues)
        self._validate_ai_settings(issues)
        self._validate_chat_settings(issues)
        self._validate_font_settings(issues)
        self._validate_spell_check_settings(issues)
        self._validate_autocomplete_settings(issues)
        self._validate_syntax_check_settings(issues)
        self._validate_template_settings(issues)
        self._validate_telemetry_settings(issues)
        self._validate_first_run_settings(issues)

        # Log results
        self._log_validation_results(issues)

        return self
