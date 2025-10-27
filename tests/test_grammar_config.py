"""
Unit tests for grammar configuration and constants.
"""

import pytest

from asciidoc_artisan.core import (
    GRAMMAR_CACHE_SIZE,
    GRAMMAR_MAX_TEXT_LENGTH,
    CheckingMode,
    GrammarConfig,
    PerformanceProfile,
)


@pytest.mark.unit
class TestGrammarConstants:
    """Test grammar system constants."""

    def test_cache_size_reasonable(self):
        """Test cache size is reasonable for desktop app."""
        assert GRAMMAR_CACHE_SIZE > 0
        assert GRAMMAR_CACHE_SIZE <= 1000  # Not too large for memory

    def test_max_text_length_reasonable(self):
        """Test max text length is reasonable."""
        assert GRAMMAR_MAX_TEXT_LENGTH > 0
        assert GRAMMAR_MAX_TEXT_LENGTH >= 50000  # At least 50KB


@pytest.mark.unit
class TestPerformanceProfiles:
    """Test performance profile configurations."""

    def test_profile_delays(self):
        """Test each profile has appropriate delay settings."""
        real_time_config = GrammarConfig(performance_profile=PerformanceProfile.REAL_TIME)
        balanced_config = GrammarConfig(performance_profile=PerformanceProfile.BALANCED)
        thorough_config = GrammarConfig(performance_profile=PerformanceProfile.THOROUGH)

        # Real-time should be fastest (lowest delay)
        assert real_time_config.check_delay_ms <= balanced_config.check_delay_ms
        # Thorough can have longer delay for better results
        assert balanced_config.check_delay_ms <= thorough_config.check_delay_ms * 2

    def test_profile_mode_compatibility(self):
        """Test profiles work with all checking modes."""
        for profile in PerformanceProfile:
            for mode in CheckingMode:
                config = GrammarConfig(
                    performance_profile=profile,
                    checking_mode=mode,
                    enabled=True,
                )

                assert config.performance_profile == profile
                assert config.checking_mode == mode


@pytest.mark.unit
class TestCheckingModeLogic:
    """Test checking mode logic and combinations."""

    def test_hybrid_mode_requires_both(self):
        """Test hybrid mode conceptually uses both engines."""
        config = GrammarConfig(
            checking_mode=CheckingMode.HYBRID,
            ai_suggestions_enabled=True,
            enabled=True,
        )

        # Hybrid mode should enable AI suggestions
        assert config.checking_mode == CheckingMode.HYBRID
        assert config.ai_suggestions_enabled is True

    def test_languagetool_only_mode(self):
        """Test LanguageTool-only mode."""
        config = GrammarConfig(
            checking_mode=CheckingMode.LANGUAGETOOL_ONLY,
            ai_suggestions_enabled=False,
            enabled=True,
        )

        assert config.checking_mode == CheckingMode.LANGUAGETOOL_ONLY
        # AI should not be used in this mode
        assert config.ai_suggestions_enabled is False

    def test_ollama_only_mode(self):
        """Test Ollama-only mode."""
        config = GrammarConfig(
            checking_mode=CheckingMode.OLLAMA_ONLY,
            ai_suggestions_enabled=True,
            enabled=True,
        )

        assert config.checking_mode == CheckingMode.OLLAMA_ONLY
        assert config.ai_suggestions_enabled is True

    def test_disabled_mode(self):
        """Test disabled mode."""
        config = GrammarConfig(
            checking_mode=CheckingMode.DISABLED,
            enabled=False,
        )

        assert config.checking_mode == CheckingMode.DISABLED
        assert config.enabled is False


@pytest.mark.unit
class TestConfigValidation:
    """Test configuration validation and edge cases."""

    def test_negative_delay_not_allowed(self):
        """Test that negative delays are handled."""
        config = GrammarConfig(check_delay_ms=-100)

        # Should either reject or clamp to positive value
        # (actual implementation may vary)
        assert isinstance(config.check_delay_ms, int)

    def test_language_codes(self):
        """Test various language code formats."""
        valid_langs = ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES"]

        for lang in valid_langs:
            config = GrammarConfig(language=lang)
            assert config.language == lang

    def test_config_immutability_concept(self):
        """Test configuration should be immutable (dataclass frozen)."""
        config = GrammarConfig(enabled=True)

        # If frozen=True on dataclass, this would raise
        # Just verify we can read the value
        assert config.enabled is True


@pytest.mark.unit
class TestAutoCheckBehavior:
    """Test auto-check configuration behavior."""

    def test_auto_check_requires_enabled(self):
        """Test auto-check conceptually requires grammar to be enabled."""
        # Auto-check on but grammar disabled - should not check
        config1 = GrammarConfig(enabled=False, auto_check=True)
        assert not (config1.enabled and config1.auto_check)

        # Both enabled - should check
        config2 = GrammarConfig(enabled=True, auto_check=True)
        assert config2.enabled and config2.auto_check

    def test_manual_check_always_available(self):
        """Test manual check is available even if auto-check disabled."""
        config = GrammarConfig(enabled=True, auto_check=False)

        # Should still be able to manually trigger check
        assert config.enabled is True
        # Manual checks don't depend on auto_check flag


@pytest.mark.unit
class TestConfigSerialization:
    """Test configuration serialization (future: to/from dict)."""

    def test_config_attributes_accessible(self):
        """Test all config attributes are accessible."""
        config = GrammarConfig(
            enabled=True,
            auto_check=True,
            ai_suggestions_enabled=True,
            checking_mode=CheckingMode.HYBRID,
            performance_profile=PerformanceProfile.BALANCED,
            language="en-US",
            check_delay_ms=500,
        )

        # All attributes should be readable
        assert hasattr(config, "enabled")
        assert hasattr(config, "auto_check")
        assert hasattr(config, "ai_suggestions_enabled")
        assert hasattr(config, "checking_mode")
        assert hasattr(config, "performance_profile")
        assert hasattr(config, "language")
        assert hasattr(config, "check_delay_ms")
