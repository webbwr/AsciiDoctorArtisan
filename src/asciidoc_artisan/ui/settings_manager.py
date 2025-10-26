"""
Settings Manager - Handles application settings persistence and restoration.

This module provides the SettingsManager class which manages:
- Settings file location (platform-specific)
- Default settings creation
- Settings loading from disk
- Settings saving to disk
- UI state restoration (window geometry, splitter, fonts)
- AI conversion preference checking

Extracted from main_window.py as part of Phase 1 refactoring to reduce
the god class anti-pattern and improve modularity.
"""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QRect, QStandardPaths, QTimer
from PySide6.QtWidgets import QMainWindow, QSplitter

from asciidoc_artisan.core import (
    APP_NAME,
    EDITOR_FONT_SIZE,
    SETTINGS_FILENAME,
    Settings,
    atomic_save_json,
)

logger = logging.getLogger(__name__)

# Check for AI client availability
try:
    import ai_client  # noqa: F401

    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False


class SettingsManager:
    """
    Manages application settings persistence and UI state restoration.

    This class handles all settings-related operations including:
    - Platform-specific settings file location
    - Default settings creation
    - Loading/saving settings from/to disk
    - Restoring UI state from settings
    - AI conversion preference checking

    Usage:
        ```python
        manager = SettingsManager()
        settings = manager.load_settings()
        # ... use settings ...
        manager.save_settings(settings, window)
        ```
    """

    def __init__(self):
        """Initialize the settings manager."""
        self._settings_path = self.get_settings_path()

    def get_settings_path(self) -> Path:
        """
        Get platform-specific settings file path.

        Returns path to settings JSON file, creating parent directories if needed.
        Falls back to home directory if config directory cannot be created.

        Returns:
            Path to settings file

        Platform-specific locations:
            - Windows: %APPDATA%\\AsciiDoc Artisan\\AsciiDoc Artisan.json
            - Linux/WSL: ~/.config/AsciiDoc Artisan/AsciiDoc Artisan.json
            - macOS: ~/Library/Application Support/AsciiDoc Artisan/AsciiDoc Artisan.json
        """
        if platform.system() == "Windows":
            config_dir_str = os.environ.get("APPDATA")
            if config_dir_str:
                config_dir = Path(config_dir_str) / APP_NAME
            else:
                config_dir = Path.home() / "AppData" / "Roaming" / APP_NAME
        else:
            config_dir_str = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppConfigLocation
            )
            if config_dir_str:
                config_dir = Path(config_dir_str)
            else:
                config_dir = Path.home() / f".{APP_NAME.lower()}"

        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using config directory: {config_dir}")
        except Exception as e:
            logger.warning(f"Could not create config directory {config_dir}: {e}")
            return Path.home() / SETTINGS_FILENAME

        return config_dir / SETTINGS_FILENAME

    def create_default_settings(self) -> Settings:
        """
        Create default settings object.

        Sets platform-appropriate defaults for initial application state.

        Returns:
            Settings object with default values

        Defaults:
            - last_directory: Documents folder (Windows) or home (Unix)
            - dark_mode: True
            - auto_save_enabled: True
            - auto_save_interval: 300 seconds (5 minutes)
            - All other fields: None or False
        """
        if platform.system() == "Windows":
            docs_path = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
            last_dir = docs_path or str(Path.home() / "Documents")
        else:
            last_dir = str(Path.home())

        return Settings(
            last_directory=last_dir,
            last_file=None,
            git_repo_path=None,
            dark_mode=True,
            maximized=False,
            window_geometry=None,
            splitter_sizes=None,
            font_size=EDITOR_FONT_SIZE,
            auto_save_enabled=True,
            auto_save_interval=300,
            ai_conversion_enabled=False,
        )

    def load_settings(self) -> Settings:
        """
        Load settings from disk.

        Reads settings JSON file and deserializes into Settings object.
        Falls back to defaults if file doesn't exist or is invalid.

        Returns:
            Settings object (either loaded or default)

        Side effects:
            - Validates last_directory exists, resets to home if not
            - Logs warnings/errors for file issues
        """
        logger.info(f"Loading settings from: {self._settings_path}")

        if not self._settings_path.is_file():
            logger.info("Settings file not found, using defaults")
            return self.create_default_settings()

        try:
            with open(self._settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            settings = Settings.from_dict(data)

            # Validate last_directory exists
            if settings.last_directory and Path(settings.last_directory).is_dir():
                pass  # Valid directory
            else:
                settings.last_directory = str(Path.home())

            logger.info("Settings loaded successfully")
            return settings

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return self.create_default_settings()

    def save_settings(
        self,
        settings: Settings,
        window: QMainWindow,
        current_file_path: Optional[Path] = None,
    ) -> bool:
        """
        Save settings to disk with current application state.

        Updates settings object with current UI state and saves to JSON file
        using atomic write to prevent corruption.

        Args:
            settings: Settings object to save
            window: Main window to extract state from
            current_file_path: Current document path (optional)

        Returns:
            True if save successful, False otherwise

        Updates from window state:
            - last_directory: Parent directory of current file
            - last_file: Current file path
            - dark_mode: Dark mode toggle state
            - maximized: Window maximization state
            - window_geometry: Window position/size (if not maximized)
            - splitter_sizes: Editor/preview splitter sizes
            - font_size: Editor font size
        """
        # Update settings from current state
        if current_file_path:
            settings.last_directory = str(current_file_path.parent)
            settings.last_file = str(current_file_path)
        else:
            settings.last_file = None

        # Get dark mode state from action if available
        if hasattr(window, "dark_mode_act") and window.dark_mode_act:
            settings.dark_mode = window.dark_mode_act.isChecked()

        # Window geometry
        settings.maximized = window.isMaximized()
        if not window.isMaximized():
            geom = window.geometry()
            settings.window_geometry = {
                "x": geom.x(),
                "y": geom.y(),
                "width": geom.width(),
                "height": geom.height(),
            }
        else:
            settings.window_geometry = None

        # Splitter sizes
        if hasattr(window, "splitter") and window.splitter:
            settings.splitter_sizes = window.splitter.sizes()

        # Font size
        if hasattr(window, "editor") and window.editor:
            font = window.editor.font()
            settings.font_size = font.pointSize()

        # Atomic save
        settings_dict = settings.to_dict()
        if atomic_save_json(
            self._settings_path, settings_dict, encoding="utf-8", indent=2
        ):
            logger.info("Settings saved successfully")
            return True
        else:
            logger.error(f"Failed to save settings: {self._settings_path}")
            return False

    def restore_ui_settings(
        self, window: QMainWindow, splitter: QSplitter, settings: Settings
    ) -> None:
        """
        Restore UI state from settings.

        Applies saved splitter sizes and font size to the window.
        Uses QTimer for splitter to ensure layout is complete first.

        Args:
            window: Main window to restore state to
            splitter: Splitter widget to restore sizes
            settings: Settings object with saved state

        Side effects:
            - Sets splitter sizes (delayed 100ms)
            - Sets editor font size
            - Logs restoration actions
        """
        # Restore splitter sizes (delayed to ensure layout complete)
        if settings.splitter_sizes and len(settings.splitter_sizes) == 2:
            sizes = list(settings.splitter_sizes)
            # Only restore if both panes have reasonable sizes (not maximized)
            # Ensure both panes are visible by requiring both > 0
            if all(s > 0 for s in sizes):
                QTimer.singleShot(100, lambda: splitter.setSizes(sizes))
                logger.info(f"Restoring splitter sizes: {settings.splitter_sizes}")
            else:
                logger.info(f"Ignoring maximized splitter sizes: {settings.splitter_sizes}")

        # Restore font size
        if settings.font_size and settings.font_size != EDITOR_FONT_SIZE:
            if hasattr(window, "editor") and window.editor:
                font = window.editor.font()
                font.setPointSize(settings.font_size)
                window.editor.setFont(font)
                logger.info(f"Restoring font size: {settings.font_size}")

    def parse_window_geometry(self, settings: Settings) -> Optional[QRect]:
        """
        Parse window geometry from settings into QRect.

        Args:
            settings: Settings object with window_geometry dict

        Returns:
            QRect if valid geometry data exists, None otherwise

        Validates that all required keys (x, y, width, height) are present.
        """
        if not settings.window_geometry:
            return None

        geom = settings.window_geometry
        if all(key in geom for key in ["x", "y", "width", "height"]):
            return QRect(geom["x"], geom["y"], geom["width"], geom["height"])

        return None

    @staticmethod
    def get_ai_conversion_preference(settings: Settings) -> bool:
        """
        Get AI conversion preference with availability check.

        Returns True only if:
        - Claude client is available (can be imported)
        - Settings have AI conversion enabled
        - API key should be present in environment (checked by ClaudeClient)

        Args:
            settings: Settings object with ai_conversion_enabled field

        Returns:
            True if AI conversion should be used, False otherwise

        Requirements:
            FR-055: AI-Enhanced Conversion option
        """
        if not AI_CLIENT_AVAILABLE:
            return False
        return settings.ai_conversion_enabled
