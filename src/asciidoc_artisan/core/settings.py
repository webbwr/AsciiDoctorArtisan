"""
Application settings data model and persistence.

This module contains the Settings dataclass which stores all user preferences
and application state that should persist across sessions.

Settings are serialized to JSON in platform-appropriate configuration directories:
- Linux/WSL: ~/.config/AsciiDoc Artisan/AsciiDocArtisan.json
- Windows: %APPDATA%/AsciiDoc Artisan/AsciiDocArtisan.json
- macOS: ~/Library/Application Support/AsciiDoc Artisan/AsciiDocArtisan.json

Specification Reference: Lines 478-520 (Data Model - Settings)
Security: API keys are explicitly NOT stored here (FR-061)
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .constants import EDITOR_FONT_SIZE


@dataclass
class Settings:
    """
    Application settings with persistence support.

    Attributes match the specification in SPECIFICATIONS.md (v1.8.0).

    All 27 fields (13 original + 5 chat settings + 6 font settings + 3 spell check):

    Core Settings:
    - last_directory: Last directory used for file operations
    - last_file: Last opened document path
    - git_repo_path: Detected Git repository root
    - dark_mode: Theme preference (True = dark, False = light)
    - maximized: Window maximization state
    - window_geometry: Window size/position when not maximized
    - splitter_sizes: Editor and preview pane widths
    - font_size: Persisted editor font size (deprecated, use editor_font_size)
    - auto_save_enabled: Auto-save feature toggle
    - auto_save_interval: Auto-save interval in seconds

    Font Settings (v1.7.0):
    - editor_font_family: Editor font family (default: "Courier New")
    - editor_font_size: Editor font size in points (default: 12)
    - preview_font_family: Preview pane font family (default: "Arial")
    - preview_font_size: Preview pane font size in points (default: 12)
    - chat_font_family: Chat pane font family (default: "Arial")
    - chat_font_size: Chat pane font size in points (default: 11)

    AI Settings:
    - ai_conversion_enabled: Deprecated (cloud AI removed in v1.2.0)
    - ai_backend: Selected AI backend ("ollama" or "claude", default: "ollama")
    - ollama_enabled: Enable Ollama AI integration (v1.1+)
    - ollama_model: Selected Ollama AI model name (v1.1+)
    - claude_model: Selected Claude AI model name (v1.10.0+)

    Chat Settings (v1.7.0):
    - ai_chat_enabled: Enable AI chat interface (works with both backends)
    - chat_history: List of saved chat messages (backend-agnostic)
    - chat_max_history: Maximum messages to store (default: 100)
    - chat_context_mode: Default interaction mode (document/syntax/general/editing)
    - chat_send_document: Include document content in context

    Spell Check Settings (v1.8.0):
    - spell_check_enabled: Enable spell checking (default: True)
    - spell_check_language: Language code (default: "en")
    - spell_check_custom_words: Custom dictionary words

    Telemetry Settings (v1.8.0):
    - telemetry_enabled: Enable privacy-first telemetry (default: False, opt-in only)
    - telemetry_session_id: Persistent anonymous session ID (UUID)
    - telemetry_opt_in_shown: Whether opt-in dialog has been shown

    Security Note:
        Settings are stored locally only. No data is sent to cloud services.
        Use Ollama for local AI features (see docs/OLLAMA_SETUP.md).
        Telemetry is local-only (NO cloud upload) and completely optional.
    """

    last_directory: str = field(default_factory=lambda: str(Path.home()))
    last_file: Optional[str] = None
    git_repo_path: Optional[str] = None
    dark_mode: bool = True
    maximized: bool = True  # Start maximized by default
    window_geometry: Optional[Dict[str, int]] = None
    splitter_sizes: Optional[List[int]] = None
    font_size: int = EDITOR_FONT_SIZE
    auto_save_enabled: bool = True
    auto_save_interval: int = 300
    ai_conversion_enabled: bool = False

    # AI Backend settings (v1.10.0+)
    ai_backend: str = "ollama"  # "ollama" or "claude"
    ollama_enabled: bool = True  # Enable Ollama by default for chat
    ollama_model: Optional[str] = "gnokit/improve-grammer"  # Default model for chat
    claude_model: Optional[str] = (
        "claude-sonnet-4-20250514"  # Default Claude model (Claude Sonnet 4)
    )

    # Chat settings (v1.7.0, v1.10.0+ backend-agnostic)
    ai_chat_enabled: bool = True  # Enable chat by default
    chat_history: List[Dict[str, Any]] = field(default_factory=list)
    chat_max_history: int = 100
    chat_context_mode: str = "document"
    chat_send_document: bool = True

    # Backward compatibility aliases (deprecated, kept for migration)
    ollama_chat_enabled: bool = True  # Deprecated: use ai_chat_enabled
    ollama_chat_history: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Deprecated: use chat_history
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
    spell_check_custom_words: List[str] = field(default_factory=list)

    # Telemetry settings (v1.8.0)
    telemetry_enabled: bool = False  # Opt-in only (GDPR compliant)
    telemetry_session_id: Optional[str] = (
        None  # Anonymous UUID, generated on first enable
    )
    telemetry_opt_in_shown: bool = False  # Whether opt-in dialog has been shown

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for json.dumps()
        """
        return asdict(self)

    @staticmethod
    def _migrate_claude_model(model: Optional[str]) -> Optional[str]:
        """
        Migrate deprecated Claude 3.5 model names to Claude 4 equivalents.

        This ensures backward compatibility when users upgrade from versions
        that used Claude 3.5 models (pre-v1.9.1).

        Args:
            model: Model identifier (may be old or new format)

        Returns:
            Migrated model identifier, or None if input was None

        Example:
            >>> Settings._migrate_claude_model("claude-3-5-sonnet-20241022")
            'claude-sonnet-4-20250514'
            >>> Settings._migrate_claude_model("claude-sonnet-4-20250514")
            'claude-sonnet-4-20250514'
        """
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
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """
        Create Settings instance from dictionary.

        Filters out unknown keys to maintain forward/backward compatibility
        when deserializing settings from older or newer versions.

        Performs migrations:
        - ollama_chat_* settings → chat_* settings (v1.10.0+)
        - Claude 3.5 model names → Claude 4 model names (v1.9.1+)

        Args:
            data: Dictionary from JSON deserialization

        Returns:
            Settings instance with valid fields populated
        """
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

    def validate(self) -> "Settings":
        """
        Validate all settings fields and apply corrections.

        Checks all fields for valid types and value ranges, applying defaults
        for invalid values. Logs all validation issues for debugging.

        Returns:
            Self (for chaining)

        Validation rules:
            - last_directory: Must be valid string path, defaults to home
            - last_file: Optional string path, set to None if invalid
            - git_repo_path: Optional string path, set to None if invalid
            - dark_mode: Must be bool, defaults to True
            - maximized: Must be bool, defaults to True
            - window_geometry: Optional dict with x,y,width,height keys
            - splitter_sizes: Optional list of integers, must have 2-3 elements
            - font_size: Integer 8-72, defaults to 12
            - auto_save_enabled: Must be bool, defaults to True
            - auto_save_interval: Integer 30-3600, defaults to 300
            - ai_backend: Must be "ollama" or "claude", defaults to "ollama"
            - ollama_model: Optional string
            - claude_model: Optional string
            - ai_chat_enabled: Must be bool, defaults to True
            - chat_max_history: Integer 10-1000, defaults to 100
            - chat_context_mode: Must be document/syntax/general/editing
            - chat_send_document: Must be bool, defaults to True
            - editor_font_family: Non-empty string, defaults to "Courier New"
            - editor_font_size: Integer 8-72, defaults to 12
            - preview_font_family: Non-empty string, defaults to "Arial"
            - preview_font_size: Integer 8-72, defaults to 12
            - chat_font_family: Non-empty string, defaults to "Arial"
            - chat_font_size: Integer 8-72, defaults to 11
            - spell_check_enabled: Must be bool, defaults to True
            - spell_check_language: Non-empty string, defaults to "en"
            - spell_check_custom_words: Must be list of strings
            - telemetry_enabled: Must be bool, defaults to False
            - telemetry_session_id: Optional string (UUID format)
            - telemetry_opt_in_shown: Must be bool, defaults to False
        """
        import logging

        logger = logging.getLogger(__name__)
        issues = []

        # Validate last_directory (string, must exist)
        if not isinstance(self.last_directory, str) or not self.last_directory:
            issues.append(f"Invalid last_directory: {self.last_directory}")
            self.last_directory = str(Path.home())
        elif not Path(self.last_directory).is_dir():
            issues.append(f"last_directory does not exist: {self.last_directory}")
            self.last_directory = str(Path.home())

        # Validate last_file (optional string)
        if self.last_file is not None and (
            not isinstance(self.last_file, str) or not self.last_file
        ):
            issues.append(f"Invalid last_file: {self.last_file}")
            self.last_file = None

        # Validate git_repo_path (optional string)
        if self.git_repo_path is not None and (
            not isinstance(self.git_repo_path, str) or not self.git_repo_path
        ):
            issues.append(f"Invalid git_repo_path: {self.git_repo_path}")
            self.git_repo_path = None

        # Validate dark_mode (bool)
        if not isinstance(self.dark_mode, bool):
            issues.append(f"Invalid dark_mode: {self.dark_mode}")
            self.dark_mode = True

        # Validate maximized (bool)
        if not isinstance(self.maximized, bool):
            issues.append(f"Invalid maximized: {self.maximized}")
            self.maximized = True

        # Validate window_geometry (optional dict)
        if self.window_geometry is not None:
            if not isinstance(self.window_geometry, dict):
                issues.append(
                    f"Invalid window_geometry type: {type(self.window_geometry)}"
                )
                self.window_geometry = None
            elif not all(
                key in self.window_geometry for key in ["x", "y", "width", "height"]
            ):
                issues.append(
                    f"Missing window_geometry keys: {self.window_geometry.keys()}"
                )
                self.window_geometry = None

        # Validate splitter_sizes (optional list of 2-3 ints)
        if self.splitter_sizes is not None:
            if not isinstance(self.splitter_sizes, list):
                issues.append(
                    f"Invalid splitter_sizes type: {type(self.splitter_sizes)}"
                )
                self.splitter_sizes = None
            elif not (2 <= len(self.splitter_sizes) <= 3):
                issues.append(
                    f"Invalid splitter_sizes length: {len(self.splitter_sizes)}"
                )
                self.splitter_sizes = None
            elif not all(isinstance(s, int) and s >= 0 for s in self.splitter_sizes):
                issues.append(f"Invalid splitter_sizes values: {self.splitter_sizes}")
                self.splitter_sizes = None

        # Validate font_size (int 8-72)
        if not isinstance(self.font_size, int) or not (8 <= self.font_size <= 72):
            issues.append(f"Invalid font_size: {self.font_size}")
            self.font_size = 12

        # Validate auto_save_enabled (bool)
        if not isinstance(self.auto_save_enabled, bool):
            issues.append(f"Invalid auto_save_enabled: {self.auto_save_enabled}")
            self.auto_save_enabled = True

        # Validate auto_save_interval (int 30-3600)
        if not isinstance(self.auto_save_interval, int) or not (
            30 <= self.auto_save_interval <= 3600
        ):
            issues.append(f"Invalid auto_save_interval: {self.auto_save_interval}")
            self.auto_save_interval = 300

        # Validate ai_backend (string: "ollama" or "claude")
        if not isinstance(self.ai_backend, str) or self.ai_backend not in [
            "ollama",
            "claude",
        ]:
            issues.append(f"Invalid ai_backend: {self.ai_backend}")
            self.ai_backend = "ollama"

        # Validate ollama_enabled (bool)
        if not isinstance(self.ollama_enabled, bool):
            issues.append(f"Invalid ollama_enabled: {self.ollama_enabled}")
            self.ollama_enabled = True

        # Validate ollama_model (optional string)
        if self.ollama_model is not None and (
            not isinstance(self.ollama_model, str) or not self.ollama_model
        ):
            issues.append(f"Invalid ollama_model: {self.ollama_model}")
            self.ollama_model = None

        # Validate claude_model (optional string)
        if self.claude_model is not None and (
            not isinstance(self.claude_model, str) or not self.claude_model
        ):
            issues.append(f"Invalid claude_model: {self.claude_model}")
            self.claude_model = None

        # Validate ai_chat_enabled (bool)
        if not isinstance(self.ai_chat_enabled, bool):
            issues.append(f"Invalid ai_chat_enabled: {self.ai_chat_enabled}")
            self.ai_chat_enabled = True

        # Validate chat_history (list of dicts)
        if not isinstance(self.chat_history, list):
            issues.append(f"Invalid chat_history type: {type(self.chat_history)}")
            self.chat_history = []

        # Validate chat_max_history (int 10-1000)
        if not isinstance(self.chat_max_history, int) or not (
            10 <= self.chat_max_history <= 1000
        ):
            issues.append(f"Invalid chat_max_history: {self.chat_max_history}")
            self.chat_max_history = 100

        # Validate chat_context_mode (string)
        valid_modes = ["document", "syntax", "general", "editing"]
        if (
            not isinstance(self.chat_context_mode, str)
            or self.chat_context_mode not in valid_modes
        ):
            issues.append(f"Invalid chat_context_mode: {self.chat_context_mode}")
            self.chat_context_mode = "document"

        # Validate chat_send_document (bool)
        if not isinstance(self.chat_send_document, bool):
            issues.append(f"Invalid chat_send_document: {self.chat_send_document}")
            self.chat_send_document = True

        # Validate font settings
        if not isinstance(self.editor_font_family, str) or not self.editor_font_family:
            issues.append(f"Invalid editor_font_family: {self.editor_font_family}")
            self.editor_font_family = "Courier New"

        if not isinstance(self.editor_font_size, int) or not (
            8 <= self.editor_font_size <= 72
        ):
            issues.append(f"Invalid editor_font_size: {self.editor_font_size}")
            self.editor_font_size = 12

        if (
            not isinstance(self.preview_font_family, str)
            or not self.preview_font_family
        ):
            issues.append(f"Invalid preview_font_family: {self.preview_font_family}")
            self.preview_font_family = "Arial"

        if not isinstance(self.preview_font_size, int) or not (
            8 <= self.preview_font_size <= 72
        ):
            issues.append(f"Invalid preview_font_size: {self.preview_font_size}")
            self.preview_font_size = 12

        if not isinstance(self.chat_font_family, str) or not self.chat_font_family:
            issues.append(f"Invalid chat_font_family: {self.chat_font_family}")
            self.chat_font_family = "Arial"

        if not isinstance(self.chat_font_size, int) or not (
            8 <= self.chat_font_size <= 72
        ):
            issues.append(f"Invalid chat_font_size: {self.chat_font_size}")
            self.chat_font_size = 11

        # Validate spell check settings
        if not isinstance(self.spell_check_enabled, bool):
            issues.append(f"Invalid spell_check_enabled: {self.spell_check_enabled}")
            self.spell_check_enabled = True

        if (
            not isinstance(self.spell_check_language, str)
            or not self.spell_check_language
        ):
            issues.append(f"Invalid spell_check_language: {self.spell_check_language}")
            self.spell_check_language = "en"

        if not isinstance(self.spell_check_custom_words, list):
            issues.append(
                f"Invalid spell_check_custom_words type: {type(self.spell_check_custom_words)}"
            )
            self.spell_check_custom_words = []
        elif not all(isinstance(w, str) for w in self.spell_check_custom_words):
            issues.append("spell_check_custom_words contains non-string values")
            self.spell_check_custom_words = [
                w for w in self.spell_check_custom_words if isinstance(w, str)
            ]

        # Validate telemetry settings
        if not isinstance(self.telemetry_enabled, bool):
            issues.append(f"Invalid telemetry_enabled: {self.telemetry_enabled}")
            self.telemetry_enabled = False

        if self.telemetry_session_id is not None and (
            not isinstance(self.telemetry_session_id, str)
            or not self.telemetry_session_id
        ):
            issues.append(f"Invalid telemetry_session_id: {self.telemetry_session_id}")
            self.telemetry_session_id = None

        if not isinstance(self.telemetry_opt_in_shown, bool):
            issues.append(
                f"Invalid telemetry_opt_in_shown: {self.telemetry_opt_in_shown}"
            )
            self.telemetry_opt_in_shown = False

        # Log all issues
        if issues:
            logger.warning(f"Settings validation found {len(issues)} issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("Settings validation: all fields valid")

        return self
