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
    claude_model: Optional[str] = "claude-3-5-sonnet-20241022"  # Default Claude model

    # Chat settings (v1.7.0, v1.10.0+ backend-agnostic)
    ai_chat_enabled: bool = True  # Enable chat by default
    chat_history: List[Dict[str, Any]] = field(default_factory=list)
    chat_max_history: int = 100
    chat_context_mode: str = "document"
    chat_send_document: bool = True

    # Backward compatibility aliases (deprecated, kept for migration)
    ollama_chat_enabled: bool = True  # Deprecated: use ai_chat_enabled
    ollama_chat_history: List[Dict[str, Any]] = field(default_factory=list)  # Deprecated: use chat_history
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
    telemetry_session_id: Optional[str] = None  # Anonymous UUID, generated on first enable
    telemetry_opt_in_shown: bool = False  # Whether opt-in dialog has been shown

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary for JSON serialization.

        Returns:
            Dictionary representation suitable for json.dumps()
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """
        Create Settings instance from dictionary.

        Filters out unknown keys to maintain forward/backward compatibility
        when deserializing settings from older or newer versions.

        Performs migration from deprecated ollama_chat_* settings to new
        backend-agnostic chat_* settings (v1.10.0+).

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

        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
