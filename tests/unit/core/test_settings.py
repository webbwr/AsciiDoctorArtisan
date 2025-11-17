"""
Unit tests for Settings dataclass and persistence.
"""

from pathlib import Path

import pytest

from asciidoc_artisan.core import Settings


@pytest.mark.fr_004
@pytest.mark.fr_074
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
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
        assert settings.maximized is True  # Default changed to True (start maximized)
        assert settings.window_geometry is None
        assert settings.splitter_sizes is None
        assert settings.font_size == 12
        assert settings.auto_save_enabled is True
        assert settings.auto_save_interval == 300
        assert settings.ai_conversion_enabled is False

    def test_settings_to_dict(self):
        """Test Settings converts to dictionary correctly."""
        settings = Settings(last_directory="/test/path", dark_mode=False, font_size=14)
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
            "splitter_sizes": [400, 600],
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
            "another_unknown": 123,
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
            ai_conversion_enabled=True,
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


@pytest.mark.fr_004
@pytest.mark.fr_074
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestSettingsMigration:
    """Test backward compatibility migrations in Settings.from_dict()."""

    def test_migrate_ollama_chat_enabled_to_ai_chat_enabled(self):
        """Test migration of deprecated ollama_chat_enabled to ai_chat_enabled."""
        data = {"ollama_chat_enabled": False}
        settings = Settings.from_dict(data)
        assert settings.ai_chat_enabled is False

    def test_migrate_ollama_chat_history_to_chat_history(self):
        """Test migration of deprecated ollama_chat_history to chat_history."""
        history = [{"role": "user", "content": "test"}]
        data = {"ollama_chat_history": history}
        settings = Settings.from_dict(data)
        assert settings.chat_history == history

    def test_migrate_ollama_chat_max_history_to_chat_max_history(self):
        """Test migration of deprecated ollama_chat_max_history to chat_max_history."""
        data = {"ollama_chat_max_history": 50}
        settings = Settings.from_dict(data)
        assert settings.chat_max_history == 50

    def test_migrate_ollama_chat_context_mode_to_chat_context_mode(self):
        """Test migration of deprecated ollama_chat_context_mode to chat_context_mode."""
        data = {"ollama_chat_context_mode": "syntax"}
        settings = Settings.from_dict(data)
        assert settings.chat_context_mode == "syntax"

    def test_migrate_ollama_chat_send_document_to_chat_send_document(self):
        """Test migration of deprecated ollama_chat_send_document to chat_send_document."""
        data = {"ollama_chat_send_document": False}
        settings = Settings.from_dict(data)
        assert settings.chat_send_document is False

    def test_migration_prefers_new_keys_over_old(self):
        """Test that new keys take precedence over deprecated keys."""
        data = {
            "ollama_chat_enabled": False,
            "ai_chat_enabled": True,  # Should win
        }
        settings = Settings.from_dict(data)
        assert settings.ai_chat_enabled is True

    def test_migrate_claude_35_sonnet_20241022_to_claude_4(self):
        """Test migration of claude-3-5-sonnet-20241022 to Claude 4."""
        data = {"claude_model": "claude-3-5-sonnet-20241022"}
        settings = Settings.from_dict(data)
        assert settings.claude_model == "claude-sonnet-4-20250514"

    def test_migrate_claude_35_sonnet_20240620_to_claude_4(self):
        """Test migration of claude-3-5-sonnet-20240620 to Claude 4."""
        data = {"claude_model": "claude-3-5-sonnet-20240620"}
        settings = Settings.from_dict(data)
        assert settings.claude_model == "claude-sonnet-4-20250514"

    def test_migrate_claude_35_haiku_to_claude_4(self):
        """Test migration of claude-3-5-haiku-20241022 to Claude 4."""
        data = {"claude_model": "claude-3-5-haiku-20241022"}
        settings = Settings.from_dict(data)
        assert settings.claude_model == "claude-haiku-4-5"

    def test_claude_model_no_migration_for_new_models(self):
        """Test that new Claude 4 model names are not migrated."""
        data = {"claude_model": "claude-sonnet-4-20250514"}
        settings = Settings.from_dict(data)
        assert settings.claude_model == "claude-sonnet-4-20250514"

    def test_claude_model_migration_handles_none(self):
        """Test that None claude_model is handled gracefully."""
        data = {"claude_model": None}
        settings = Settings.from_dict(data)
        assert settings.claude_model is None

    def test_claude_model_migration_handles_unknown_model(self):
        """Test that unknown model names pass through unchanged."""
        data = {"claude_model": "custom-model-name"}
        settings = Settings.from_dict(data)
        assert settings.claude_model == "custom-model-name"


@pytest.mark.fr_004
@pytest.mark.fr_074
@pytest.mark.fr_010
@pytest.mark.fr_011
@pytest.mark.fr_005
@pytest.mark.unit
class TestSettingsValidation:
    """Test Settings.validate() method for all field validation."""

    def test_validate_empty_last_directory_uses_home(self, tmp_path):
        """Test validation corrects empty last_directory to home."""
        settings = Settings(last_directory="")
        validated = settings.validate()
        assert validated.last_directory == str(Path.home())

    def test_validate_nonexistent_directory_uses_home(self):
        """Test validation corrects non-existent directory to home."""
        settings = Settings(last_directory="/nonexistent/path/12345")
        validated = settings.validate()
        assert validated.last_directory == str(Path.home())

    def test_validate_valid_directory_unchanged(self, tmp_path):
        """Test validation keeps valid directory unchanged."""
        test_dir = str(tmp_path)
        settings = Settings(last_directory=test_dir)
        validated = settings.validate()
        assert validated.last_directory == test_dir

    def test_validate_invalid_last_file_set_to_none(self):
        """Test validation sets invalid last_file to None."""
        settings = Settings(last_file="")
        validated = settings.validate()
        assert validated.last_file is None

    def test_validate_valid_last_file_unchanged(self):
        """Test validation keeps valid last_file unchanged."""
        settings = Settings(last_file="/valid/path.adoc")
        validated = settings.validate()
        assert validated.last_file == "/valid/path.adoc"

    def test_validate_invalid_dark_mode_uses_default(self):
        """Test validation corrects invalid dark_mode to True."""
        settings = Settings()
        settings.dark_mode = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.dark_mode is True

    def test_validate_invalid_maximized_uses_default(self):
        """Test validation corrects invalid maximized to True."""
        settings = Settings()
        settings.maximized = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.maximized is True

    def test_validate_invalid_window_geometry_set_to_none(self):
        """Test validation sets invalid window_geometry to None."""
        settings = Settings(window_geometry={"incomplete": "data"})  # type: ignore
        validated = settings.validate()
        assert validated.window_geometry is None

    def test_validate_valid_window_geometry_unchanged(self):
        """Test validation keeps valid window_geometry unchanged."""
        geom = {"x": 100, "y": 100, "width": 800, "height": 600}
        settings = Settings(window_geometry=geom)
        validated = settings.validate()
        assert validated.window_geometry == geom

    def test_validate_invalid_splitter_sizes_set_to_none(self):
        """Test validation sets invalid splitter_sizes to None."""
        settings = Settings(splitter_sizes=[100])  # Too few elements
        validated = settings.validate()
        assert validated.splitter_sizes is None

    def test_validate_font_size_too_small(self):
        """Test validation corrects font_size below minimum."""
        settings = Settings(font_size=5)
        validated = settings.validate()
        assert validated.font_size == 12

    def test_validate_font_size_too_large(self):
        """Test validation corrects font_size above maximum."""
        settings = Settings(font_size=100)
        validated = settings.validate()
        assert validated.font_size == 12

    def test_validate_valid_font_size_unchanged(self):
        """Test validation keeps valid font_size unchanged."""
        settings = Settings(font_size=14)
        validated = settings.validate()
        assert validated.font_size == 14

    def test_validate_invalid_auto_save_interval_uses_default(self):
        """Test validation corrects invalid auto_save_interval."""
        settings = Settings(auto_save_interval=10)  # Too small
        validated = settings.validate()
        assert validated.auto_save_interval == 300

    def test_validate_auto_save_interval_too_large(self):
        """Test validation corrects auto_save_interval above maximum."""
        settings = Settings(auto_save_interval=5000)
        validated = settings.validate()
        assert validated.auto_save_interval == 300

    def test_validate_invalid_ai_backend(self):
        """Test validation corrects invalid ai_backend."""
        settings = Settings()
        settings.ai_backend = "invalid"  # type: ignore
        validated = settings.validate()
        assert validated.ai_backend == "ollama"

    def test_validate_valid_ai_backend_unchanged(self):
        """Test validation keeps valid ai_backend unchanged."""
        settings = Settings(ai_backend="claude")
        validated = settings.validate()
        assert validated.ai_backend == "claude"

    def test_validate_chat_max_history_too_small(self):
        """Test validation corrects chat_max_history below minimum."""
        settings = Settings(chat_max_history=5)
        validated = settings.validate()
        assert validated.chat_max_history == 100

    def test_validate_chat_max_history_too_large(self):
        """Test validation corrects chat_max_history above maximum."""
        settings = Settings(chat_max_history=2000)
        validated = settings.validate()
        assert validated.chat_max_history == 100

    def test_validate_invalid_chat_context_mode(self):
        """Test validation corrects invalid chat_context_mode."""
        settings = Settings()
        settings.chat_context_mode = "invalid"  # type: ignore
        validated = settings.validate()
        assert validated.chat_context_mode == "document"

    def test_validate_valid_chat_context_mode_unchanged(self):
        """Test validation keeps valid chat_context_mode unchanged."""
        for mode in ["document", "syntax", "general", "editing"]:
            settings = Settings(chat_context_mode=mode)
            validated = settings.validate()
            assert validated.chat_context_mode == mode

    def test_validate_editor_font_size_too_small(self):
        """Test validation corrects editor_font_size below minimum."""
        settings = Settings(editor_font_size=5)
        validated = settings.validate()
        assert validated.editor_font_size == 12

    def test_validate_editor_font_size_too_large(self):
        """Test validation corrects editor_font_size above maximum."""
        settings = Settings(editor_font_size=100)
        validated = settings.validate()
        assert validated.editor_font_size == 12

    def test_validate_preview_font_size_too_small(self):
        """Test validation corrects preview_font_size below minimum."""
        settings = Settings(preview_font_size=5)
        validated = settings.validate()
        assert validated.preview_font_size == 12

    def test_validate_preview_font_size_too_large(self):
        """Test validation corrects preview_font_size above maximum."""
        settings = Settings(preview_font_size=100)
        validated = settings.validate()
        assert validated.preview_font_size == 12

    def test_validate_chat_font_size_too_small(self):
        """Test validation corrects chat_font_size below minimum."""
        settings = Settings(chat_font_size=5)
        validated = settings.validate()
        assert validated.chat_font_size == 11

    def test_validate_chat_font_size_too_large(self):
        """Test validation corrects chat_font_size above maximum."""
        settings = Settings(chat_font_size=100)
        validated = settings.validate()
        assert validated.chat_font_size == 11

    def test_validate_empty_editor_font_family(self):
        """Test validation corrects empty editor_font_family."""
        settings = Settings(editor_font_family="")
        validated = settings.validate()
        assert validated.editor_font_family == "Courier New"

    def test_validate_empty_preview_font_family(self):
        """Test validation corrects empty preview_font_family."""
        settings = Settings(preview_font_family="")
        validated = settings.validate()
        assert validated.preview_font_family == "Arial"

    def test_validate_empty_chat_font_family(self):
        """Test validation corrects empty chat_font_family."""
        settings = Settings(chat_font_family="")
        validated = settings.validate()
        assert validated.chat_font_family == "Arial"

    def test_validate_invalid_spell_check_custom_words(self):
        """Test validation corrects spell_check_custom_words with non-strings."""
        settings = Settings(spell_check_custom_words=["valid", 123, None])  # type: ignore
        validated = settings.validate()
        assert validated.spell_check_custom_words == ["valid"]

    def test_validate_valid_spell_check_custom_words_unchanged(self):
        """Test validation keeps valid spell_check_custom_words unchanged."""
        words = ["word1", "word2", "word3"]
        settings = Settings(spell_check_custom_words=words)
        validated = settings.validate()
        assert validated.spell_check_custom_words == words

    def test_validate_invalid_telemetry_enabled(self):
        """Test validation corrects invalid telemetry_enabled."""
        settings = Settings()
        settings.telemetry_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.telemetry_enabled is False

    def test_validate_returns_self(self):
        """Test that validate() returns the Settings instance."""
        settings = Settings()
        result = settings.validate()
        assert result is settings

    def test_validate_logs_issues(self, caplog):
        """Test that validate() logs validation issues."""
        import logging

        caplog.set_level(logging.WARNING)

        settings = Settings(font_size=5, chat_max_history=2000)
        settings.validate()

        assert "Settings validation found" in caplog.text
        assert "Invalid font_size" in caplog.text
        assert "Invalid chat_max_history" in caplog.text

    def test_validate_logs_success_when_valid(self, caplog):
        """Test that validate() logs success when all fields valid."""
        import logging

        caplog.set_level(logging.INFO)

        settings = Settings()
        settings.validate()

        assert "Settings validation: all fields valid" in caplog.text

    def test_validate_invalid_git_repo_path_set_to_none(self):
        """Test validation sets invalid git_repo_path to None."""
        settings = Settings(git_repo_path="")
        validated = settings.validate()
        assert validated.git_repo_path is None

    def test_validate_invalid_window_geometry_type(self):
        """Test validation sets non-dict window_geometry to None."""
        settings = Settings()
        settings.window_geometry = "not a dict"  # type: ignore
        validated = settings.validate()
        assert validated.window_geometry is None

    def test_validate_invalid_splitter_sizes_type(self):
        """Test validation sets non-list splitter_sizes to None."""
        settings = Settings()
        settings.splitter_sizes = "not a list"  # type: ignore
        validated = settings.validate()
        assert validated.splitter_sizes is None

    def test_validate_invalid_splitter_sizes_wrong_length(self):
        """Test validation sets wrong-length splitter_sizes to None."""
        settings = Settings(splitter_sizes=[100, 200, 300, 400])  # Too many
        validated = settings.validate()
        assert validated.splitter_sizes is None

    def test_validate_invalid_splitter_sizes_negative_values(self):
        """Test validation sets splitter_sizes with negative values to None."""
        settings = Settings(splitter_sizes=[100, -200])
        validated = settings.validate()
        assert validated.splitter_sizes is None

    def test_validate_invalid_auto_save_enabled(self):
        """Test validation corrects invalid auto_save_enabled."""
        settings = Settings()
        settings.auto_save_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.auto_save_enabled is True

    def test_validate_invalid_ollama_enabled(self):
        """Test validation corrects invalid ollama_enabled."""
        settings = Settings()
        settings.ollama_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.ollama_enabled is True

    def test_validate_invalid_ai_chat_enabled(self):
        """Test validation corrects invalid ai_chat_enabled."""
        settings = Settings()
        settings.ai_chat_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.ai_chat_enabled is True

    def test_validate_invalid_spell_check_enabled(self):
        """Test validation corrects invalid spell_check_enabled."""
        settings = Settings()
        settings.spell_check_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.spell_check_enabled is True

    def test_validate_empty_spell_check_language(self):
        """Test validation corrects empty spell_check_language."""
        settings = Settings(spell_check_language="")
        validated = settings.validate()
        assert validated.spell_check_language == "en"

    def test_validate_invalid_spell_check_custom_words_type(self):
        """Test validation corrects spell_check_custom_words with wrong type."""
        settings = Settings()
        settings.spell_check_custom_words = "not a list"  # type: ignore
        validated = settings.validate()
        assert validated.spell_check_custom_words == []

    def test_validate_invalid_telemetry_session_id(self):
        """Test validation corrects invalid telemetry_session_id."""
        settings = Settings(telemetry_session_id="")
        validated = settings.validate()
        assert validated.telemetry_session_id is None

    def test_validate_invalid_telemetry_opt_in_shown(self):
        """Test validation corrects invalid telemetry_opt_in_shown."""
        settings = Settings()
        settings.telemetry_opt_in_shown = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.telemetry_opt_in_shown is False

    def test_validate_invalid_ollama_model(self):
        """Test validation corrects invalid ollama_model."""
        settings = Settings(ollama_model="")
        validated = settings.validate()
        assert validated.ollama_model is None

    def test_validate_invalid_claude_model(self):
        """Test validation corrects invalid claude_model."""
        settings = Settings(claude_model="")
        validated = settings.validate()
        assert validated.claude_model is None

    def test_validate_invalid_chat_history_type(self):
        """Test validation corrects chat_history with wrong type."""
        settings = Settings()
        settings.chat_history = "not a list"  # type: ignore
        validated = settings.validate()
        assert validated.chat_history == []

    def test_validate_invalid_chat_send_document(self):
        """Test validation corrects invalid chat_send_document."""
        settings = Settings()
        settings.chat_send_document = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.chat_send_document is True

    # v2.0.0 feature validation tests
    def test_validate_invalid_autocomplete_enabled(self):
        """Test validation corrects invalid autocomplete_enabled."""
        settings = Settings()
        settings.autocomplete_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.autocomplete_enabled is True

    def test_validate_invalid_autocomplete_delay(self):
        """Test validation corrects invalid autocomplete_delay."""
        settings = Settings(autocomplete_delay=50)  # Too small
        validated = settings.validate()
        assert validated.autocomplete_delay == 300

    def test_validate_autocomplete_delay_too_large(self):
        """Test validation corrects autocomplete_delay above maximum."""
        settings = Settings(autocomplete_delay=10000)  # Too large
        validated = settings.validate()
        assert validated.autocomplete_delay == 300

    def test_validate_invalid_autocomplete_min_chars(self):
        """Test validation corrects invalid autocomplete_min_chars."""
        settings = Settings(autocomplete_min_chars=0)  # Too small
        validated = settings.validate()
        assert validated.autocomplete_min_chars == 2

    def test_validate_autocomplete_min_chars_too_large(self):
        """Test validation corrects autocomplete_min_chars above maximum."""
        settings = Settings(autocomplete_min_chars=20)  # Too large
        validated = settings.validate()
        assert validated.autocomplete_min_chars == 2

    def test_validate_invalid_syntax_check_realtime_enabled(self):
        """Test validation corrects invalid syntax_check_realtime_enabled."""
        settings = Settings()
        settings.syntax_check_realtime_enabled = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.syntax_check_realtime_enabled is True

    def test_validate_invalid_syntax_check_delay(self):
        """Test validation corrects invalid syntax_check_delay."""
        settings = Settings(syntax_check_delay=50)  # Too small
        validated = settings.validate()
        assert validated.syntax_check_delay == 500

    def test_validate_syntax_check_delay_too_large(self):
        """Test validation corrects syntax_check_delay above maximum."""
        settings = Settings(syntax_check_delay=20000)  # Too large
        validated = settings.validate()
        assert validated.syntax_check_delay == 500

    def test_validate_invalid_syntax_check_show_underlines(self):
        """Test validation corrects invalid syntax_check_show_underlines."""
        settings = Settings()
        settings.syntax_check_show_underlines = "not a bool"  # type: ignore
        validated = settings.validate()
        assert validated.syntax_check_show_underlines is True

    def test_validate_invalid_template_last_category(self):
        """Test validation corrects invalid template_last_category."""
        settings = Settings()
        settings.template_last_category = 123  # type: ignore
        validated = settings.validate()
        assert validated.template_last_category == "All"

    def test_validate_invalid_template_recent_limit(self):
        """Test validation corrects invalid template_recent_limit."""
        settings = Settings(template_recent_limit=0)  # Too small
        validated = settings.validate()
        assert validated.template_recent_limit == 10

    def test_validate_template_recent_limit_too_large(self):
        """Test validation corrects template_recent_limit above maximum."""
        settings = Settings(template_recent_limit=100)  # Too large
        validated = settings.validate()
        assert validated.template_recent_limit == 10
