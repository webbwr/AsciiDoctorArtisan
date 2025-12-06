"""Integration tests for SettingsManager - Settings persistence & restoration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Force software rendering for WSL2 compatibility
os.environ.setdefault("ASCIIDOC_ARTISAN_NO_WEBENGINE", "1")

from PySide6.QtCore import QByteArray
from PySide6.QtWidgets import QMainWindow


@pytest.fixture
def settings_manager():
    """Create SettingsManager for testing."""
    from asciidoc_artisan.ui.settings_manager import SettingsManager

    manager = SettingsManager()
    return manager


@pytest.fixture
def test_settings():
    """Create test Settings instance."""
    from asciidoc_artisan.core import Settings

    settings = Settings()
    settings.font_size = 14
    settings.dark_mode = True
    settings.editor_font_family = "Consolas"
    settings.spell_check_enabled = True
    return settings


@pytest.fixture
def mock_window(qtbot):
    """Create a mock main window for settings tests."""
    window = QMainWindow()
    qtbot.addWidget(window)

    # Mock the necessary methods that save_settings uses
    window.isMaximized = Mock(return_value=False)
    window.saveGeometry = Mock(return_value=QByteArray())

    # Mock splitter (optional component)
    mock_splitter = Mock()
    mock_splitter.saveState = Mock(return_value=QByteArray())
    window.main_splitter = mock_splitter

    return window


@pytest.mark.integration
class TestSettingsManagerIntegration:
    """Test SettingsManager end-to-end workflows."""

    def test_settings_manager_initialization(self, settings_manager):
        """Integration: SettingsManager initializes correctly."""
        assert settings_manager is not None
        assert hasattr(settings_manager, "load_settings")
        assert hasattr(settings_manager, "save_settings")

    def test_load_default_settings(self, settings_manager):
        """Integration: Default settings load when no file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(settings_manager, "get_settings_path", return_value=Path(tmpdir) / "settings.json"):
                settings = settings_manager.load_settings()
                assert settings is not None
                assert hasattr(settings, "font_size")
                assert hasattr(settings, "dark_mode")

    def test_settings_round_trip(self, settings_manager, test_settings, mock_window):
        """Integration: Settings save and load correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"

            # Patch the cached settings path directly (set during __init__)
            settings_manager._settings_path = settings_path

            # Save settings (using immediate save)
            settings_manager.save_settings_immediate(test_settings, mock_window)

            # Verify file exists
            assert settings_path.exists()

            # Load settings back
            loaded = settings_manager.load_settings()

            # Verify key values preserved
            assert loaded.font_size == test_settings.font_size
            assert loaded.dark_mode == test_settings.dark_mode


@pytest.mark.integration
class TestSettingsPersistenceIntegration:
    """Test settings persistence across sessions."""

    def test_font_settings_persistence(self, settings_manager, test_settings, mock_window):
        """Integration: Font settings persist correctly."""
        test_settings.font_size = 18
        test_settings.editor_font_family = "Monaco"

        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"

            with patch.object(settings_manager, "get_settings_path", return_value=settings_path):
                settings_manager.save_settings_immediate(test_settings, mock_window)
                loaded = settings_manager.load_settings()

                assert loaded.font_size == 18
                assert loaded.editor_font_family == "Monaco"

    def test_theme_settings_persistence(self, settings_manager, test_settings, mock_window):
        """Integration: Theme settings persist correctly."""
        test_settings.dark_mode = False

        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"

            with patch.object(settings_manager, "get_settings_path", return_value=settings_path):
                settings_manager.save_settings_immediate(test_settings, mock_window)
                loaded = settings_manager.load_settings()

                assert loaded.dark_mode is False

    def test_ai_settings_persistence(self, settings_manager, test_settings, mock_window):
        """Integration: AI settings persist correctly."""
        test_settings.ollama_enabled = True
        test_settings.ollama_model = "llama3.2"

        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"

            with patch.object(settings_manager, "get_settings_path", return_value=settings_path):
                settings_manager.save_settings_immediate(test_settings, mock_window)
                loaded = settings_manager.load_settings()

                assert loaded.ollama_enabled is True
                assert loaded.ollama_model == "llama3.2"


@pytest.mark.integration
class TestSettingsRecoveryIntegration:
    """Test settings recovery from corruption."""

    def test_corrupted_json_recovery(self, settings_manager):
        """Integration: Corrupted settings file returns defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"

            # Write corrupted JSON
            settings_path.write_text("{invalid json content")

            with patch.object(settings_manager, "get_settings_path", return_value=settings_path):
                # Should return default settings, not crash
                settings = settings_manager.load_settings()
                assert settings is not None

    def test_missing_fields_recovery(self, settings_manager):
        """Integration: Missing fields filled with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = Path(tmpdir) / "settings.json"

            # Patch the cached settings path directly
            settings_manager._settings_path = settings_path

            # Write partial settings
            settings_path.write_text('{"font_size": 16}')

            settings = settings_manager.load_settings()

            # Should have font_size from file
            assert settings.font_size == 16
            # Should have defaults for other fields
            assert hasattr(settings, "dark_mode")


@pytest.mark.integration
class TestPlatformSettingsIntegration:
    """Test platform-specific settings paths."""

    def test_settings_path_exists(self, settings_manager):
        """Integration: Settings path is valid for current platform."""
        path = settings_manager.get_settings_path()

        # Path should be a Path object
        assert isinstance(path, Path)

        # Parent directory should be creatable
        assert path.parent.exists() or path.parent.parent.exists()

    def test_settings_save_to_directory(self, settings_manager, test_settings, mock_window):
        """Integration: Settings save to existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the settings directory (SettingsManager expects parent to exist)
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir(parents=True, exist_ok=True)
            settings_path = subdir / "settings.json"

            # Patch the cached settings path directly
            settings_manager._settings_path = settings_path

            settings_manager.save_settings_immediate(test_settings, mock_window)

            # Settings file should have been created
            assert settings_path.exists()
