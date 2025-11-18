"""Tests for ui.settings_manager module."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QMainWindow, QSplitter

from asciidoc_artisan.core import Settings


@pytest.fixture
def temp_settings_file(tmp_path):
    """Create temporary settings file for testing."""
    settings_file = tmp_path / "test_settings.json"
    return settings_file


@pytest.fixture
def mock_window(qapp):
    """Create mock main window with required attributes."""
    window = QMainWindow()
    window.dark_mode_act = Mock()
    window.dark_mode_act.isChecked = Mock(return_value=True)
    window.splitter = QSplitter(Qt.Orientation.Horizontal)
    window.splitter.setSizes([400, 600])
    window.editor = Mock()
    font_mock = Mock()
    font_mock.pointSize = Mock(return_value=12)
    window.editor.font = Mock(return_value=font_mock)
    return window


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestSettingsManager:
    """Test suite for SettingsManager basic functionality."""

    def test_import(self):
        """Test SettingsManager can be imported."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        assert SettingsManager is not None

    def test_creation(self, qapp):
        """Test SettingsManager can be instantiated."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        assert manager is not None

    def test_has_settings_methods(self, qapp):
        """Test SettingsManager has expected methods."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        methods = [m for m in dir(manager) if any(x in m.lower() for x in ["get", "set", "load", "save"])]
        assert len(methods) > 0

    def test_initialization_sets_settings_path(self, qapp):
        """Test initialization sets _settings_path attribute."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        assert hasattr(manager, "_settings_path")
        assert isinstance(manager._settings_path, Path)

    def test_initialization_creates_timer(self, qapp):
        """Test initialization creates deferred save timer."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        assert hasattr(manager, "_pending_save_timer")
        assert manager._pending_save_timer.interval() == 100
        assert manager._pending_save_timer.isSingleShot()


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestSettingsPath:
    """Test suite for settings path resolution."""

    @patch("platform.system", return_value="Linux")
    @patch("asciidoc_artisan.ui.settings_manager.QStandardPaths.writableLocation")
    def test_get_settings_path_linux(self, mock_writable, mock_system, qapp):
        """Test settings path on Linux."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        mock_writable.return_value = "/home/user/.config/AsciiDocArtisan"
        manager = SettingsManager()

        path = manager.get_settings_path()
        assert "AsciiDocArtisan" in str(path)
        assert path.name == "AsciiDocArtisan.json"

    @patch("platform.system", return_value="Windows")
    def test_get_settings_path_windows(self, mock_system, qapp):
        """Test settings path on Windows."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        with patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            manager = SettingsManager()
            path = manager.get_settings_path()

            assert "AsciiDocArtisan" in str(path) or "AsciiDoc Artisan" in str(path)
            assert path.name == "AsciiDocArtisan.json"

    @patch("platform.system", return_value="Darwin")
    @patch("asciidoc_artisan.ui.settings_manager.QStandardPaths.writableLocation")
    def test_get_settings_path_macos(self, mock_writable, mock_system, qapp):
        """Test settings path on macOS."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        mock_writable.return_value = "/Users/test/Library/Application Support/AsciiDocArtisan"
        manager = SettingsManager()

        path = manager.get_settings_path()
        assert "AsciiDocArtisan" in str(path) or "AsciiDoc Artisan" in str(path)

    @patch("platform.system", return_value="Linux")
    @patch(
        "asciidoc_artisan.ui.settings_manager.QStandardPaths.writableLocation",
        return_value="",
    )
    def test_get_settings_path_fallback_when_no_writable(self, mock_writable, mock_system, qapp):
        """Test settings path falls back to home when no writable location."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        path = manager.get_settings_path()

        # Should fall back to ~/.asciidoc artisan
        assert Path.home() in path.parents or str(Path.home()) in str(path)


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestDefaultSettings:
    """Test suite for default settings creation."""

    @patch("platform.system", return_value="Windows")
    @patch("asciidoc_artisan.ui.settings_manager.QStandardPaths.writableLocation")
    def test_create_default_settings_windows(self, mock_writable, mock_system, qapp):
        """Test default settings on Windows uses Documents folder."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        mock_writable.return_value = "C:\\Users\\Test\\Documents"
        manager = SettingsManager()

        settings = manager.create_default_settings()

        assert isinstance(settings, Settings)
        assert settings.dark_mode is True
        assert settings.auto_save_enabled is True
        assert settings.auto_save_interval == 300
        assert settings.ai_conversion_enabled is False

    @patch("platform.system", return_value="Linux")
    def test_create_default_settings_linux(self, mock_system, qapp):
        """Test default settings on Linux uses home directory."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()

        assert settings.last_directory == str(Path.home())
        assert settings.dark_mode is True
        assert settings.font_size == 12  # EDITOR_FONT_SIZE default

    def test_default_settings_has_correct_structure(self, qapp):
        """Test default settings has all required fields."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()

        assert hasattr(settings, "last_directory")
        assert hasattr(settings, "dark_mode")
        assert hasattr(settings, "auto_save_enabled")
        assert hasattr(settings, "ai_conversion_enabled")


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestLoadSettings:
    """Test suite for settings loading."""

    def test_load_settings_creates_defaults_when_file_missing(self, qapp, temp_settings_file):
        """Test load_settings returns defaults when file doesn't exist."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file

        settings = manager.load_settings()

        assert isinstance(settings, Settings)
        assert settings.dark_mode is True  # Default value

    def test_load_settings_reads_existing_file(self, qapp, temp_settings_file):
        """Test load_settings reads and parses existing file."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        # Create valid settings file
        settings_data = {
            "last_directory": "/home/test",
            "dark_mode": False,
            "auto_save_enabled": True,
            "auto_save_interval": 600,
            "ai_conversion_enabled": False,
        }
        temp_settings_file.write_text(json.dumps(settings_data), encoding="utf-8")

        manager = SettingsManager()
        manager._settings_path = temp_settings_file

        settings = manager.load_settings()

        assert settings.dark_mode is False
        assert settings.auto_save_interval == 600

    def test_load_settings_handles_corrupt_file(self, qapp, temp_settings_file):
        """Test load_settings falls back to defaults on corrupt file."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        # Create corrupt JSON file
        temp_settings_file.write_text("{ invalid json", encoding="utf-8")

        manager = SettingsManager()
        manager._settings_path = temp_settings_file

        settings = manager.load_settings()

        # Should return defaults, not crash
        assert isinstance(settings, Settings)
        assert settings.dark_mode is True


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestSaveSettings:
    """Test suite for settings saving."""

    def test_save_settings_updates_from_window_state(self, qapp, temp_settings_file, mock_window):
        """Test save_settings extracts state from window."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        # Set window state
        mock_window.dark_mode_act.isChecked.return_value = False

        result = manager.save_settings(settings, mock_window)

        assert result is True
        assert settings.dark_mode is False

    def test_save_settings_schedules_deferred_save(self, qapp, temp_settings_file, mock_window):
        """Test save_settings schedules timer instead of saving immediately."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        manager.save_settings(settings, mock_window)

        # Timer should be active
        assert manager._pending_save_timer.isActive()
        assert manager._pending_save_data is not None

    def test_save_settings_with_current_file(self, qapp, temp_settings_file, mock_window):
        """Test save_settings updates last_file and last_directory."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        # Use tmp_path which exists, not /home/test which doesn't
        current_file = temp_settings_file.parent / "document.adoc"
        manager.save_settings(settings, mock_window, current_file)

        assert settings.last_file == str(current_file)
        # Settings.validate() may correct invalid directories, so just check it's set
        assert settings.last_directory is not None

    def test_save_settings_immediate_saves_synchronously(self, qapp, temp_settings_file, mock_window):
        """Test save_settings_immediate saves without delay."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        result = manager.save_settings_immediate(settings, mock_window)

        assert result is True
        assert temp_settings_file.exists()

        # Verify file content
        saved_data = json.loads(temp_settings_file.read_text())
        assert "dark_mode" in saved_data

    def test_save_settings_immediate_handles_failure(self, qapp, mock_window):
        """Test save_settings_immediate returns False on failure."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = Path("/invalid/path/settings.json")
        settings = manager.create_default_settings()

        result = manager.save_settings_immediate(settings, mock_window)

        assert result is False


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestRestoreUISettings:
    """Test suite for UI state restoration."""

    def test_restore_ui_settings_restores_splitter_sizes(self, qapp, mock_window):
        """Test restore_ui_settings sets splitter sizes."""
        from PySide6.QtWidgets import QLabel

        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.splitter_sizes = [300, 700]

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Editor"))
        splitter.addWidget(QLabel("Preview"))

        manager.restore_ui_settings(mock_window, splitter, settings)

        # Note: Actual sizes set via QTimer, so we just verify no crash

    def test_restore_ui_settings_migrates_2pane_to_3pane(self, qapp, mock_window):
        """Test restore_ui_settings handles 2-pane to 3-pane migration."""
        from PySide6.QtWidgets import QLabel

        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.splitter_sizes = [400, 600]  # 2-pane

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Editor"))
        splitter.addWidget(QLabel("Preview"))
        splitter.addWidget(QLabel("Chat"))  # 3-pane

        manager.restore_ui_settings(mock_window, splitter, settings)

        # Should not crash, migration happens internally

    def test_restore_ui_settings_sets_font_size(self, qapp, mock_window):
        """Test restore_ui_settings updates editor font."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.font_size = 14

        splitter = QSplitter(Qt.Orientation.Horizontal)

        manager.restore_ui_settings(mock_window, splitter, settings)

        # Font should be updated
        mock_window.editor.font.assert_called()


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestWindowGeometry:
    """Test suite for window geometry parsing."""

    def test_parse_window_geometry_valid(self, qapp):
        """Test parse_window_geometry with valid data."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.window_geometry = {"x": 100, "y": 200, "width": 800, "height": 600}

        rect = manager.parse_window_geometry(settings)

        assert isinstance(rect, QRect)
        assert rect.x() == 100
        assert rect.y() == 200
        assert rect.width() == 800
        assert rect.height() == 600

    def test_parse_window_geometry_none_when_no_data(self, qapp):
        """Test parse_window_geometry returns None when no geometry."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.window_geometry = None

        rect = manager.parse_window_geometry(settings)

        assert rect is None

    def test_parse_window_geometry_none_when_incomplete(self, qapp):
        """Test parse_window_geometry returns None when missing keys."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.window_geometry = {"x": 100, "y": 200}  # Missing width, height

        rect = manager.parse_window_geometry(settings)

        assert rect is None


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestAIConversionPreference:
    """Test suite for AI conversion preference."""

    def test_get_ai_conversion_preference_always_false(self, qapp):
        """Test get_ai_conversion_preference returns False (performance)."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        settings = Settings()
        settings.ollama_enabled = True
        settings.ollama_model = "llama2"

        # Should always return False for performance reasons
        result = SettingsManager.get_ai_conversion_preference(settings)

        assert result is False

    def test_get_ai_conversion_preference_is_static(self, qapp):
        """Test get_ai_conversion_preference is a static method."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        # Can call without instance
        settings = Settings()
        result = SettingsManager.get_ai_conversion_preference(settings)

        assert isinstance(result, bool)


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestDeferredSave:
    """Test suite for deferred save functionality."""

    def test_deferred_save_timer_fires(self, qapp, qtbot, temp_settings_file, mock_window):
        """Test _do_deferred_save is called after timer fires."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        # Trigger deferred save
        manager.save_settings(settings, mock_window)

        # Timer should be active with pending data
        assert manager._pending_save_timer.isActive()
        assert manager._pending_save_data is not None

        # Wait for timer to fire (100ms + margin)
        qtbot.wait(200)

        # File should be saved
        assert temp_settings_file.exists()
        assert manager._pending_save_data is None

    def test_deferred_save_coalesces_rapid_saves(self, qapp, qtbot, temp_settings_file, mock_window):
        """Test multiple rapid saves are coalesced into one."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        # Trigger multiple saves rapidly
        manager.save_settings(settings, mock_window)
        manager.save_settings(settings, mock_window)
        manager.save_settings(settings, mock_window)

        # Only one timer should be active
        assert manager._pending_save_timer.isActive()

        # Wait for timer to fire
        qtbot.wait(200)

        # File should be saved once
        assert temp_settings_file.exists()

    def test_deferred_save_handles_none_pending_data(self, qapp, temp_settings_file):
        """Test _do_deferred_save handles None pending data gracefully."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        manager._pending_save_data = None

        # Should not crash
        manager._do_deferred_save()

        # No file should be created
        assert not temp_settings_file.exists()

    def test_deferred_save_handles_save_failure(self, qapp, qtbot, mock_window):
        """Test _do_deferred_save handles atomic_save_json failure."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = Path("/invalid/path/settings.json")
        settings = manager.create_default_settings()

        # Trigger deferred save
        manager.save_settings(settings, mock_window)

        # Wait for timer to fire
        qtbot.wait(200)

        # Pending data should be cleared even on failure
        assert manager._pending_save_data is None


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestWindowGeometryEdgeCases:
    """Test suite for window geometry edge cases."""

    def test_save_maximized_window_clears_geometry(self, qapp, temp_settings_file, mock_window):
        """Test maximized window sets geometry to None."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        # Make window maximized
        mock_window.isMaximized = Mock(return_value=True)

        result = manager.save_settings_immediate(settings, mock_window)

        assert result is True
        assert settings.window_geometry is None

    def test_save_settings_immediate_without_current_file(self, qapp, temp_settings_file, mock_window):
        """Test save_settings_immediate when current_file_path is None."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        manager._settings_path = temp_settings_file
        settings = manager.create_default_settings()

        # Call without current_file_path (defaults to None)
        result = manager.save_settings_immediate(settings, mock_window, current_file_path=None)

        assert result is True
        assert settings.last_file is None


@pytest.mark.fr_004
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestSplitterSizeEdgeCases:
    """Test suite for splitter size restoration edge cases."""

    def test_restore_ui_ignores_invalid_splitter_sizes(self, qapp, mock_window):
        """Test restore_ui_settings ignores splitter sizes with 0 or negative values."""
        from PySide6.QtWidgets import QLabel

        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.splitter_sizes = [0, 600]  # Invalid: first pane is 0

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Editor"))
        splitter.addWidget(QLabel("Preview"))

        # Should not crash, should log and ignore
        manager.restore_ui_settings(mock_window, splitter, settings)

    def test_restore_ui_ignores_second_pane_zero(self, qapp, mock_window):
        """Test restore_ui_settings ignores when second pane is 0."""
        from PySide6.QtWidgets import QLabel

        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.splitter_sizes = [600, 0]  # Invalid: second pane is 0

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Editor"))
        splitter.addWidget(QLabel("Preview"))

        # Should not crash, should log and ignore
        manager.restore_ui_settings(mock_window, splitter, settings)

    def test_restore_ui_ignores_both_panes_zero(self, qapp, mock_window):
        """Test restore_ui_settings ignores when both panes are 0."""
        from PySide6.QtWidgets import QLabel

        from asciidoc_artisan.ui.settings_manager import SettingsManager

        manager = SettingsManager()
        settings = manager.create_default_settings()
        settings.splitter_sizes = [0, 0]  # Invalid: both panes are 0

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(QLabel("Editor"))
        splitter.addWidget(QLabel("Preview"))

        # Should not crash, should log and ignore
        manager.restore_ui_settings(mock_window, splitter, settings)
