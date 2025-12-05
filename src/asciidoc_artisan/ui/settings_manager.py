"""
Settings Manager - Handles application settings persistence and restoration.

Manages: Platform-specific file location, defaults, load/save, UI state restoration (geometry, splitter, fonts), AI conversion preference.
Extracted from main_window.py (Phase 1) to reduce god class anti-pattern, improve modularity.
"""

import logging
import os
import platform
from pathlib import Path
from typing import Any

from PySide6.QtCore import QRect, QStandardPaths, QTimer
from PySide6.QtWidgets import QMainWindow, QSplitter

from asciidoc_artisan.core import (
    APP_NAME,
    EDITOR_FONT_SIZE,
    SETTINGS_FILENAME,
    SETTINGS_FILENAME_JSON,
    Settings,
    atomic_save_toon,
    toon_utils,
)

logger = logging.getLogger(__name__)

# AI client removed - using Ollama for local AI features instead
AI_CLIENT_AVAILABLE = False


class SettingsManager:
    """Manages application settings persistence and UI state restoration. Handles: platform-specific file location, defaults, load/save, UI restoration, AI preference."""

    def __init__(self) -> None:
        """Initialize the settings manager."""
        self._settings_path = self.get_settings_path()

        # Deferred save mechanism (QA-12: Async Settings Save)
        self._pending_save_timer = QTimer()
        self._pending_save_timer.setSingleShot(True)
        self._pending_save_timer.setInterval(100)  # 100ms delay
        self._pending_save_timer.timeout.connect(self._do_deferred_save)
        self._pending_save_data: dict[str, Any] | None = None

    def get_settings_path(self) -> Path:
        """Get platform-specific settings file path. Creates parent dirs if needed, falls back to home if fails. Locations: Windows %APPDATA%, Linux ~/.config, macOS ~/Library/Application Support."""
        if platform.system() == "Windows":
            config_dir_str = os.environ.get("APPDATA")
            if config_dir_str:
                config_dir = Path(config_dir_str) / APP_NAME
            else:
                config_dir = Path.home() / "AppData" / "Roaming" / APP_NAME
        else:
            config_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
            if config_dir_str:
                config_dir = Path(config_dir_str)
            else:
                config_dir = Path.home() / f".{APP_NAME.lower()}"

        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using config directory: {config_dir}")
        except Exception as e:
            logger.warning(f"Could not create config directory {config_dir}: {e}")
            return Path.home() / SETTINGS_FILENAME  # type: ignore[no-any-return]  # Path / str returns Any in some contexts

        return config_dir / SETTINGS_FILENAME  # type: ignore[no-any-return]  # Path / str returns Any in some contexts

    def create_default_settings(self) -> Settings:
        """Create default settings object. Defaults: last_directory (Documents/home), dark_mode (True), auto_save_enabled (True), auto_save_interval (300s), others None/False."""
        if platform.system() == "Windows":
            docs_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
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

    def _get_legacy_json_path(self) -> Path:
        """Get path to legacy JSON settings file for migration."""
        return Path(self._settings_path.parent / SETTINGS_FILENAME_JSON)

    def _migrate_json_to_toon(self) -> Settings | None:
        """Migrate legacy JSON settings to TOON format. Returns Settings if migration successful, None otherwise."""
        json_path = self._get_legacy_json_path()
        if not json_path.is_file():
            return None

        try:
            import json

            logger.info(f"Migrating legacy JSON settings: {json_path}")
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            settings = Settings.from_dict(data)
            settings.validate()

            # Save as TOON format
            if atomic_save_toon(self._settings_path, settings.to_dict(), indent=2):
                logger.info(f"Migration successful: {json_path} → {self._settings_path}")
                # Rename old JSON file to .json.bak
                backup_path = json_path.with_suffix(".json.bak")
                json_path.rename(backup_path)
                logger.info(f"Legacy settings backed up: {backup_path}")
                return settings

        except Exception as e:
            logger.warning(f"JSON migration failed: {e}")

        return None

    def load_settings(self) -> Settings:
        """Load settings from TOON file. Falls back to JSON migration if TOON not found. Validates all fields, logs errors."""
        logger.info(f"Loading settings from: {self._settings_path}")

        # Try TOON file first
        if self._settings_path.is_file():
            try:
                with open(self._settings_path, encoding="utf-8") as f:
                    data = toon_utils.load(f)

                settings = Settings.from_dict(data)
                settings.validate()

                logger.info("Settings loaded successfully (TOON format)")
                return settings

            except Exception as e:
                logger.error(f"Failed to load TOON settings: {e}")

        # Try migrating from legacy JSON
        migrated = self._migrate_json_to_toon()
        if migrated:
            return migrated

        # Fall back to defaults
        logger.info("No settings found, using defaults")
        return self.create_default_settings()

    def save_settings(
        self,
        settings: Settings,
        window: QMainWindow,
        current_file_path: Path | None = None,
    ) -> bool:
        """Schedule deferred settings save (non-blocking). Updates settings from UI state, schedules save after 100ms delay (prevents blocking, coalesces rapid requests). For immediate save (app exit), use save_settings_immediate(). Updates: last_directory/file, dark_mode, maximized, window_geometry, splitter_sizes, font_size. Returns True (scheduled, not complete)."""
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

        # Validate settings before saving
        settings.validate()

        # Schedule deferred save (non-blocking)
        settings_dict = settings.to_dict()
        self._pending_save_data = settings_dict

        # Restart timer (coalesces rapid saves)
        self._pending_save_timer.start()

        logger.debug("Settings save scheduled (deferred)")
        return True

    def _do_deferred_save(self) -> None:
        """Perform actual deferred save. Called by QTimer after 100ms delay, saves pending data to TOON file."""
        if self._pending_save_data is None:
            return

        # Save to disk (TOON format)
        if atomic_save_toon(
            self._settings_path,
            self._pending_save_data,
            encoding="utf-8",
            indent=2,
        ):
            logger.info("Settings saved successfully (deferred, TOON format)")
        else:
            logger.error(f"Failed to save settings: {self._settings_path}")

        # Clear pending data
        self._pending_save_data = None

    def save_settings_immediate(
        self,
        settings: Settings,
        window: QMainWindow,
        current_file_path: Path | None = None,
    ) -> bool:
        """Save settings immediately (blocking). Use for critical operations (app shutdown) where settings must be saved before exiting. Returns True if successful, False otherwise."""
        # Update settings from current state (same as save_settings)
        if current_file_path:
            settings.last_directory = str(current_file_path.parent)
            settings.last_file = str(current_file_path)
        else:
            settings.last_file = None

        if hasattr(window, "dark_mode_act") and window.dark_mode_act:
            settings.dark_mode = window.dark_mode_act.isChecked()

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

        if hasattr(window, "splitter") and window.splitter:
            settings.splitter_sizes = window.splitter.sizes()

        if hasattr(window, "editor") and window.editor:
            font = window.editor.font()
            settings.font_size = font.pointSize()

        # Validate settings before saving
        settings.validate()

        # Immediate save (blocking, TOON format)
        settings_dict = settings.to_dict()
        if atomic_save_toon(self._settings_path, settings_dict, encoding="utf-8", indent=2):
            logger.info("Settings saved successfully (immediate, TOON format)")
            return True
        else:
            logger.error(f"Failed to save settings: {self._settings_path}")
            return False

    def restore_ui_settings(self, window: QMainWindow, splitter: QSplitter, settings: Settings) -> None:
        """Restore UI state from settings. Applies saved splitter sizes and font size. Uses QTimer for splitter (100ms delay) to ensure layout complete. Side effects: Sets splitter sizes (delayed), font size, logs actions."""
        # Restore splitter sizes (delayed to ensure layout complete)
        # Support both 2-pane (legacy) and 3-pane (with chat) layouts
        if settings.splitter_sizes:
            sizes = list(settings.splitter_sizes)
            num_panes = len(splitter.sizes())

            # Handle migration from 2-pane to 3-pane layout
            if len(sizes) == 2 and num_panes == 3:
                # Legacy 2-pane settings: add chat pane with 0 width (hidden)
                sizes.append(0)
                logger.info("Migrating 2-pane splitter settings to 3-pane layout")

            if len(sizes) == num_panes:
                # Only restore if first two panes have reasonable sizes
                # Third pane (chat) can be 0 (hidden)
                if sizes[0] > 0 and sizes[1] > 0:
                    QTimer.singleShot(100, lambda: splitter.setSizes(sizes))
                    logger.info(f"Restoring splitter sizes: {sizes}")
                else:
                    logger.info(f"Ignoring maximized splitter sizes: {sizes}")
            else:
                logger.warning(f"Splitter size mismatch: saved={len(sizes)}, actual={num_panes}")

        # Restore font size
        if settings.font_size and settings.font_size != EDITOR_FONT_SIZE:
            if hasattr(window, "editor") and window.editor:
                font = window.editor.font()
                font.setPointSize(settings.font_size)
                window.editor.setFont(font)
                logger.info(f"Restoring font size: {settings.font_size}")

    def parse_window_geometry(self, settings: Settings) -> QRect | None:
        """Parse window geometry from settings into QRect. Returns QRect if valid geometry (x, y, width, height) exists, None otherwise."""
        if not settings.window_geometry:
            return None

        geom = settings.window_geometry
        if all(key in geom for key in ["x", "y", "width", "height"]):
            return QRect(geom["x"], geom["y"], geom["width"], geom["height"])

        return None

    @staticmethod
    def get_ai_conversion_preference(settings: Settings) -> bool:
        """Get AI conversion preference with availability check. PERFORMANCE: Disabled by default (Ollama takes 30-60s per file). Always returns False to use fast Pandoc conversion. Users manually trigger AI via menu. Requirements: FR-055 (AI-Enhanced Conversion, Ollama)."""
        # PERFORMANCE FIX: Disable automatic AI conversion on file open
        # Ollama takes 30-60 seconds per file, making file opening too slow
        # Users can manually trigger AI conversion when needed
        return False

        # Original logic (disabled for performance):
        # if not getattr(settings, "ollama_enabled", False):
        #     return False
        # if not getattr(settings, "ollama_model", None):
        #     return False
        # try:
        #     import ollama
        #     return True
        # except ImportError:
        #     return False
