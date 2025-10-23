"""
Unit tests for Settings dataclass and persistence.
"""
from pathlib import Path

import pytest

from adp_windows import Settings


@pytest.mark.unit
class TestSettings:
    """Test Settings dataclass functionality."""

    def test_settings_defaults(self):
        """Test Settings initializes with correct defaults."""
        settings = Settings()
        assert settings.last_directory == str(Path.home())
        assert settings.last_file is None
        assert settings.git_repo_path is None
        assert settings.dark_mode is True
        assert settings.maximized is False
        assert settings.window_geometry is None
        assert settings.splitter_sizes is None
        assert settings.font_size == 12
        assert settings.auto_save_enabled is True
        assert settings.auto_save_interval == 300
        assert settings.ai_conversion_enabled is False

    def test_settings_to_dict(self):
        """Test Settings converts to dictionary correctly."""
        settings = Settings(
            last_directory="/test/path",
            dark_mode=False,
            font_size=14
        )
        data = settings.to_dict()

        assert isinstance(data, dict)
        assert data["last_directory"] == "/test/path"
        assert data["dark_mode"] is False
        assert data["font_size"] == 14

    def test_settings_from_dict(self):
        """Test Settings loads from dictionary correctly."""
        data = {
            "last_directory": "/test/path",
            "last_file": "/test/file.adoc",
            "dark_mode": False,
            "maximized": True,
            "font_size": 16,
            "splitter_sizes": [400, 600]
        }

        settings = Settings.from_dict(data)
        assert settings.last_directory == "/test/path"
        assert settings.last_file == "/test/file.adoc"
        assert settings.dark_mode is False
        assert settings.maximized is True
        assert settings.font_size == 16
        assert settings.splitter_sizes == [400, 600]

    def test_settings_from_dict_filters_unknown_keys(self):
        """Test Settings.from_dict filters out unknown keys."""
        data = {
            "last_directory": "/test/path",
            "unknown_key": "should be ignored",
            "another_unknown": 123
        }

        settings = Settings.from_dict(data)
        assert settings.last_directory == "/test/path"
        assert not hasattr(settings, "unknown_key")
        assert not hasattr(settings, "another_unknown")

    def test_settings_roundtrip(self):
        """Test Settings can be serialized and deserialized."""
        original = Settings(
            last_directory="/test/path",
            last_file="/test/file.adoc",
            git_repo_path="/test/repo",
            dark_mode=False,
            maximized=True,
            window_geometry={"x": 100, "y": 100, "width": 800, "height": 600},
            splitter_sizes=[350, 650],
            font_size=14,
            auto_save_enabled=True,
            auto_save_interval=600,
            ai_conversion_enabled=True
        )


        data = original.to_dict()
        restored = Settings.from_dict(data)


        assert restored.last_directory == original.last_directory
        assert restored.last_file == original.last_file
        assert restored.git_repo_path == original.git_repo_path
        assert restored.dark_mode == original.dark_mode
        assert restored.maximized == original.maximized
        assert restored.window_geometry == original.window_geometry
        assert restored.splitter_sizes == original.splitter_sizes
        assert restored.font_size == original.font_size
        assert restored.auto_save_enabled == original.auto_save_enabled
        assert restored.auto_save_interval == original.auto_save_interval
        assert restored.ai_conversion_enabled == original.ai_conversion_enabled
