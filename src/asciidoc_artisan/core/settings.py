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

    Attributes match the specification in SPECIFICATIONS.md (v1.7.0).

    All 18 fields (13 original + 5 chat settings):

    Core Settings:
    - last_directory: Last directory used for file operations
    - last_file: Last opened document path
    - git_repo_path: Detected Git repository root
    - dark_mode: Theme preference (True = dark, False = light)
    - maximized: Window maximization state
    - window_geometry: Window size/position when not maximized
    - splitter_sizes: Editor and preview pane widths
    - font_size: Persisted editor font size
    - auto_save_enabled: Auto-save feature toggle
    - auto_save_interval: Auto-save interval in seconds

    AI Settings:
    - ai_conversion_enabled: Deprecated (cloud AI removed in v1.2.0)
    - ollama_enabled: Enable Ollama AI integration (v1.1+)
    - ollama_model: Selected Ollama AI model name (v1.1+)

    Chat Settings (v1.7.0):
    - ollama_chat_enabled: Enable AI chat interface
    - ollama_chat_history: List of saved chat messages
    - ollama_chat_max_history: Maximum messages to store (default: 100)
    - ollama_chat_context_mode: Default interaction mode (document/syntax/general/editing)
    - ollama_chat_send_document: Include document content in context

    Security Note:
        Settings are stored locally only. No data is sent to cloud services.
        Use Ollama for local AI features (see docs/OLLAMA_SETUP.md).
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
    ollama_enabled: bool = True  # Enable Ollama by default for chat
    ollama_model: Optional[str] = "phi3:mini"  # Default model for chat

    # Chat settings (v1.7.0)
    ollama_chat_enabled: bool = True  # Enable chat by default
    ollama_chat_history: List[Dict[str, Any]] = field(default_factory=list)
    ollama_chat_max_history: int = 100
    ollama_chat_context_mode: str = "document"
    ollama_chat_send_document: bool = True

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

        Args:
            data: Dictionary from JSON deserialization

        Returns:
            Settings instance with valid fields populated
        """
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
