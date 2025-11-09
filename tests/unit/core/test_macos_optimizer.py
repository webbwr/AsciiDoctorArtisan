"""
Tests for macOS Optimizer - Apple Silicon & Metal Performance (v2.0.0).

Tests macOS-specific optimizations including Apple Silicon detection,
Metal GPU configuration, unified memory management, and APFS optimizations.
"""

import json
import multiprocessing
import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core.macos_optimizer import (
    MacOSOptimizationInfo,
    configure_metal_optimization,
    detect_macos_capabilities,
    enable_apfs_optimizations,
    get_optimal_thread_count,
    log_optimization_status,
    optimize_unified_memory_usage,
)


@pytest.mark.unit
class TestMacOSOptimizationInfoDataclass:
    """Test MacOSOptimizationInfo dataclass."""

    def test_dataclass_creation(self):
        """Test creating MacOSOptimizationInfo instance."""
        info = MacOSOptimizationInfo()

        assert info.is_macos is False
        assert info.is_apple_silicon is False
        assert info.chip_name == ""
        assert info.metal_version == ""
        assert info.unified_memory_gb == 0
        assert info.performance_cores == 0
        assert info.efficiency_cores == 0
        assert info.neural_engine_cores == 0
        assert info.gpu_cores == 0
        assert info.metal_feature_set == ""
        assert info.apfs_enabled is False
        assert info.gcd_available is False

    def test_dataclass_with_values(self):
        """Test dataclass with custom values."""
        info = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            chip_name="Apple M2 Pro",
            metal_version="Metal 3",
            unified_memory_gb=16,
            performance_cores=6,
            efficiency_cores=4,
            neural_engine_cores=16,
            gpu_cores=19,
            metal_feature_set="Metal 3 v1",
            apfs_enabled=True,
            gcd_available=True,
        )

        assert info.is_macos is True
        assert info.chip_name == "Apple M2 Pro"
        assert info.unified_memory_gb == 16


@pytest.mark.unit
class TestDetectMacOSCapabilities:
    """Test macOS capability detection."""

    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_not_macos(self, mock_system):
        """Test detection returns default info when not macOS."""
        mock_system.return_value = "Linux"

        info = detect_macos_capabilities()

        assert info.is_macos is False
        assert info.is_apple_silicon is False

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_macos_intel(self, mock_system, mock_machine, mock_run):
        """Test detection on Intel Mac."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "x86_64"
        mock_run.return_value = MagicMock(
            stdout="File System Personality: APFS",
            returncode=0,
        )

        info = detect_macos_capabilities()

        assert info.is_macos is True
        assert info.is_apple_silicon is False
        assert info.gcd_available is True

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_apple_silicon_m1(self, mock_system, mock_machine, mock_run):
        """Test detection on Apple M1."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        # Mock sysctl calls
        mock_run.side_effect = [
            MagicMock(stdout="Apple M1\n", returncode=0),  # brand_string
            MagicMock(stdout="17179869184\n", returncode=0),  # memsize (16GB)
            MagicMock(stdout="4\n", returncode=0),  # perflevel0
            MagicMock(stdout="4\n", returncode=0),  # perflevel1
            MagicMock(stdout="", returncode=1),  # system_profiler fails
            MagicMock(stdout="APFS\n", returncode=0),  # diskutil
        ]

        info = detect_macos_capabilities()

        assert info.is_macos is True
        assert info.is_apple_silicon is True
        assert "M1" in info.chip_name
        assert info.unified_memory_gb == 16
        assert info.performance_cores == 4
        assert info.efficiency_cores == 4
        assert info.neural_engine_cores == 16  # M1 has 16 cores
        assert info.apfs_enabled is True

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_apple_silicon_m2_max(self, mock_system, mock_machine, mock_run):
        """Test detection on Apple M2 Max."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        mock_run.side_effect = [
            MagicMock(stdout="Apple M2 Max\n", returncode=0),
            MagicMock(stdout="34359738368\n", returncode=0),  # 32GB
            MagicMock(stdout="8\n", returncode=0),
            MagicMock(stdout="4\n", returncode=0),
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="APFS\n", returncode=0),
        ]

        info = detect_macos_capabilities()

        assert "M2 Max" in info.chip_name
        assert info.unified_memory_gb == 32
        assert info.neural_engine_cores == 16  # M2 Max has 16 cores

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_with_metal_info(self, mock_system, mock_machine, mock_run):
        """Test detection with Metal GPU information."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        metal_json = {
            "SPDisplaysDataType": [
                {
                    "spdisplays_mtlgpufamilymacOS": "Metal 3 v1",
                    "sppci_model": "Apple M1 Pro 16-core GPU",
                }
            ]
        }

        mock_run.side_effect = [
            MagicMock(stdout="Apple M1 Pro\n", returncode=0),
            MagicMock(stdout="17179869184\n", returncode=0),
            MagicMock(stdout="6\n", returncode=0),
            MagicMock(stdout="2\n", returncode=0),
            MagicMock(stdout=json.dumps(metal_json), returncode=0),
            MagicMock(stdout="APFS\n", returncode=0),
        ]

        info = detect_macos_capabilities()

        assert info.metal_version == "Metal 3 v1"
        assert info.metal_feature_set == "Metal 3 v1"
        assert info.gpu_cores == 16

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_gpu_core_counts(self, mock_system, mock_machine, mock_run):
        """Test detection of various GPU core counts."""
        test_cases = [
            ("64-core GPU", 64),
            ("48-core GPU", 48),
            ("32-core GPU", 32),
            ("24-core GPU", 24),
            ("16-core GPU", 16),
            ("10-core GPU", 10),
            ("8-core GPU", 8),
        ]

        for chip_type, expected_cores in test_cases:
            mock_system.return_value = "Darwin"
            mock_machine.return_value = "arm64"

            metal_json = {
                "SPDisplaysDataType": [
                    {
                        "spdisplays_mtlgpufamilymacOS": "Metal 3",
                        "sppci_model": f"Apple M1 {chip_type}",
                    }
                ]
            }

            mock_run.side_effect = [
                MagicMock(stdout="Apple M1\n", returncode=0),
                MagicMock(stdout="17179869184\n", returncode=0),
                MagicMock(stdout="8\n", returncode=0),
                MagicMock(stdout="2\n", returncode=0),
                MagicMock(stdout=json.dumps(metal_json), returncode=0),
                MagicMock(stdout="APFS\n", returncode=0),
            ]

            info = detect_macos_capabilities()
            assert info.gpu_cores == expected_cores, f"Failed for {chip_type}"

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_handles_subprocess_timeout(self, mock_system, mock_machine, mock_run):
        """Test graceful handling of subprocess timeout."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"
        mock_run.side_effect = subprocess.TimeoutExpired("sysctl", 1)

        info = detect_macos_capabilities()

        # Should return partial info without crashing
        assert info.is_macos is True
        assert info.is_apple_silicon is True

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_handles_json_decode_error(self, mock_system, mock_machine, mock_run):
        """Test handling of malformed JSON from system_profiler."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        mock_run.side_effect = [
            MagicMock(stdout="Apple M1\n", returncode=0),
            MagicMock(stdout="17179869184\n", returncode=0),
            MagicMock(stdout="4\n", returncode=0),
            MagicMock(stdout="4\n", returncode=0),
            MagicMock(stdout="invalid json{", returncode=0),  # Malformed JSON
            MagicMock(stdout="APFS\n", returncode=0),
        ]

        info = detect_macos_capabilities()

        # Should still detect basic info even with JSON error
        assert info.is_apple_silicon is True
        assert info.metal_version == ""  # JSON parsing failed

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_m3_neural_engine(self, mock_system, mock_machine, mock_run):
        """Test M3 chip neural engine detection."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        mock_run.side_effect = [
            MagicMock(stdout="Apple M3 Pro\n", returncode=0),
            MagicMock(stdout="17179869184\n", returncode=0),
            MagicMock(stdout="6\n", returncode=0),
            MagicMock(stdout="6\n", returncode=0),
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="APFS\n", returncode=0),
        ]

        info = detect_macos_capabilities()

        assert "M3" in info.chip_name
        assert info.neural_engine_cores == 16

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_m1_ultra_neural_engine(self, mock_system, mock_machine, mock_run):
        """Test M1 Ultra neural engine detection."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        mock_run.side_effect = [
            MagicMock(stdout="Apple M1 Ultra\n", returncode=0),
            MagicMock(stdout="68719476736\n", returncode=0),  # 64GB
            MagicMock(stdout="16\n", returncode=0),
            MagicMock(stdout="4\n", returncode=0),
            MagicMock(stdout="", returncode=1),
            MagicMock(stdout="APFS\n", returncode=0),
        ]

        info = detect_macos_capabilities()

        assert "M1 Ultra" in info.chip_name
        assert info.neural_engine_cores == 32  # Ultra has 32 cores


@pytest.mark.unit
class TestConfigureMetalOptimization:
    """Test Metal GPU optimization configuration."""

    def test_configure_metal_default(self):
        """Test Metal configuration with defaults."""
        config = configure_metal_optimization()

        assert config["memory_pool_size"] == "auto"
        assert config["shader_cache_enabled"] is True
        assert config["async_compute"] is True
        assert config["texture_compression"] == "astc"
        assert config["command_buffer_reuse"] is True
        assert config["mtl_hud"] is False

    @patch.dict(os.environ, {"METAL_DEBUG": "1"})
    def test_configure_metal_debug_mode(self):
        """Test Metal configuration in debug mode."""
        config = configure_metal_optimization()

        assert config["mtl_hud"] is True
        assert os.environ["METAL_DEVICE_WRAPPER_TYPE"] == "1"
        assert os.environ["METAL_DEBUG_ERROR_MODE"] == "assert"

    @patch.dict(os.environ, {"METAL_DEBUG": "0"})
    def test_configure_metal_production_mode(self):
        """Test Metal configuration in production mode."""
        config = configure_metal_optimization()

        assert config["mtl_hud"] is False


@pytest.mark.unit
class TestOptimizeUnifiedMemoryUsage:
    """Test unified memory optimization."""

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_optimize_memory_not_apple_silicon(self, mock_detect):
        """Test returns empty config when not Apple Silicon."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=False,
        )

        config = optimize_unified_memory_usage()

        assert config == {}

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_optimize_memory_apple_silicon_16gb(self, mock_detect):
        """Test memory optimization for 16GB Apple Silicon."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            unified_memory_gb=16,
        )

        config = optimize_unified_memory_usage()

        # 16GB = 16384MB
        # 50% app limit = 8192MB
        # 25% GPU pool = 4096MB
        assert config["app_memory_limit_mb"] == 8192
        assert config["gpu_memory_pool_mb"] == 4096
        assert config["use_zero_copy"] is True
        assert config["unified_memory"] is True
        assert config["memory_pressure_threshold"] == 0.8

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_optimize_memory_apple_silicon_32gb(self, mock_detect):
        """Test memory optimization for 32GB Apple Silicon."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            unified_memory_gb=32,
        )

        config = optimize_unified_memory_usage()

        assert config["app_memory_limit_mb"] == 16384
        assert config["gpu_memory_pool_mb"] == 8192


@pytest.mark.unit
class TestGetOptimalThreadCount:
    """Test optimal thread count calculation."""

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_thread_count_not_apple_silicon(self, mock_detect):
        """Test uses CPU count when not Apple Silicon."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=False,
        )

        thread_count = get_optimal_thread_count()

        expected = multiprocessing.cpu_count()
        assert thread_count == expected

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_thread_count_apple_silicon_m1(self, mock_detect):
        """Test thread count for Apple M1 (4 P-cores)."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            performance_cores=4,
            efficiency_cores=4,
        )

        thread_count = get_optimal_thread_count()

        # P-cores * 2 = 4 * 2 = 8
        assert thread_count == 8

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_thread_count_apple_silicon_m1_pro(self, mock_detect):
        """Test thread count for Apple M1 Pro (6 P-cores)."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            performance_cores=6,
            efficiency_cores=2,
        )

        thread_count = get_optimal_thread_count()

        # P-cores * 2 = 6 * 2 = 12
        assert thread_count == 12


@pytest.mark.unit
class TestEnableApfsOptimizations:
    """Test APFS optimization configuration."""

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_apfs_not_enabled(self, mock_detect):
        """Test returns empty config when APFS not enabled."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            apfs_enabled=False,
        )

        config = enable_apfs_optimizations()

        assert config == {}

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_apfs_enabled(self, mock_detect):
        """Test APFS optimizations when enabled."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            apfs_enabled=True,
        )

        config = enable_apfs_optimizations()

        assert config["use_cloning"] is True
        assert config["atomic_save_native"] is True
        assert config["fast_directory_sizing"] is True
        assert config["enable_compression"] is False


@pytest.mark.unit
class TestLogOptimizationStatus:
    """Test optimization status logging."""

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    @patch("asciidoc_artisan.core.macos_optimizer.logger")
    def test_log_status_not_macos(self, mock_logger, mock_detect):
        """Test logging when not on macOS."""
        mock_detect.return_value = MacOSOptimizationInfo(is_macos=False)

        log_optimization_status()

        # Should log that macOS is not detected
        assert any("Not running on macOS" in str(call) for call in mock_logger.info.call_args_list)

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    @patch("asciidoc_artisan.core.macos_optimizer.logger")
    def test_log_status_apple_silicon(self, mock_logger, mock_detect):
        """Test logging for Apple Silicon Mac."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            chip_name="Apple M2 Pro",
            unified_memory_gb=16,
            performance_cores=6,
            efficiency_cores=4,
            gpu_cores=19,
            neural_engine_cores=16,
            metal_feature_set="Metal 3 v1",
            apfs_enabled=True,
            gcd_available=True,
        )

        log_optimization_status()

        # Check that key information was logged
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Apple Silicon" in call for call in log_calls)
        assert any("16 GB" in call for call in log_calls)
        assert any("APFS" in call for call in log_calls)

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    @patch("asciidoc_artisan.core.macos_optimizer.logger")
    def test_log_status_intel_mac(self, mock_logger, mock_detect):
        """Test logging for Intel Mac."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=False,
            apfs_enabled=True,
            gcd_available=True,
        )

        log_optimization_status()

        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("Intel Mac" in call for call in log_calls)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("asciidoc_artisan.core.macos_optimizer.subprocess.run")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.machine")
    @patch("asciidoc_artisan.core.macos_optimizer.platform.system")
    def test_detect_with_all_subprocess_failures(self, mock_system, mock_machine, mock_run):
        """Test detection when all subprocess calls fail."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        info = detect_macos_capabilities()

        # Should still mark as Apple Silicon even with failures
        assert info.is_macos is True
        assert info.is_apple_silicon is True
        # But values should remain default
        assert info.unified_memory_gb == 0
        assert info.performance_cores == 0

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_optimize_memory_zero_memory(self, mock_detect):
        """Test memory optimization with 0GB detected."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            unified_memory_gb=0,
        )

        config = optimize_unified_memory_usage()

        # Should still return config with 0 values
        assert config["app_memory_limit_mb"] == 0
        assert config["gpu_memory_pool_mb"] == 0

    @patch("asciidoc_artisan.core.macos_optimizer.detect_macos_capabilities")
    def test_thread_count_zero_cores(self, mock_detect):
        """Test thread count when 0 P-cores detected."""
        mock_detect.return_value = MacOSOptimizationInfo(
            is_macos=True,
            is_apple_silicon=True,
            performance_cores=0,
        )

        thread_count = get_optimal_thread_count()

        # 0 * 2 = 0
        assert thread_count == 0
