"""
Tests for core.gpu_detection module.

Comprehensive test suite for GPU detection, caching, and NPU detection.

This file consolidates tests from:
- test_gpu_detection.py (original, 71 tests)
- test_gpu_cache.py (merged, 13 unique tests added)

Tests cover:
- GPUInfo dataclass creation and validation
- GPU cache entry creation, validation, and serialization
- GPU detection cache save/load operations with TTL
- Cache clearing and error handling
- DRI device detection (/dev/dri/*)
- Vendor-specific GPU detection (NVIDIA, AMD, Intel)
- OpenGL renderer detection
- WSLg environment detection
- Intel NPU (Neural Processing Unit) detection
- Compute capability detection (CUDA, OpenCL, Vulkan, OpenVINO)
- Main GPU detection logic
- GPU information logging
- High-level get_gpu_info() API with caching
- CLI interface

Consolidated: November 2, 2025 (Phase 3 Task 3.1)
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core.gpu_detection import (
    GPUCacheEntry,
    GPUDetectionCache,
    GPUInfo,
    check_amd_gpu,
    check_dri_devices,
    check_intel_gpu,
    check_intel_npu,
    check_nvidia_gpu,
    check_opengl_renderer,
    check_wslg_environment,
    detect_compute_capabilities,
    detect_gpu,
    get_gpu_info,
    log_gpu_info,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_cache_file(tmp_path, monkeypatch):
    """Use temporary cache file for testing."""
    cache_file = tmp_path / "gpu_cache.json"
    monkeypatch.setattr(GPUDetectionCache, "CACHE_FILE", cache_file)
    return cache_file


@pytest.fixture
def sample_gpu_info():
    """Create sample GPUInfo for testing."""
    return GPUInfo(
        has_gpu=True,
        gpu_type="nvidia",
        gpu_name="NVIDIA GeForce RTX 4060 Laptop GPU",
        driver_version="581.57",
        render_device="/dev/dri/renderD128",
        can_use_webengine=True,
        reason="Hardware acceleration available",
        has_npu=False,
        npu_type=None,
        npu_name=None,
        compute_capabilities=["cuda", "opencl", "vulkan"],
    )


# ============================================================================
# GPU INFO TESTS
# ============================================================================


class TestGPUInfo:
    """Test suite for GPUInfo dataclass."""

    def test_gpu_info_creation_minimal(self):
        """Test creating GPUInfo with minimal required fields."""
        info = GPUInfo(has_gpu=False)

        assert info.has_gpu is False
        assert info.gpu_type is None
        assert info.gpu_name is None
        assert info.driver_version is None
        assert info.can_use_webengine is False
        assert info.has_npu is False
        assert info.compute_capabilities == []

    def test_gpu_info_creation_full_nvidia(self):
        """Test creating GPUInfo for NVIDIA GPU."""
        info = GPUInfo(
            has_gpu=True,
            gpu_type="nvidia",
            gpu_name="NVIDIA GeForce RTX 4060",
            driver_version="535.104.05",
            render_device="/dev/dri/renderD128",
            can_use_webengine=True,
            reason="NVIDIA GPU detected with CUDA support",
            compute_capabilities=["cuda", "opencl", "vulkan"],
        )

        assert info.has_gpu is True
        assert info.gpu_type == "nvidia"
        assert "RTX 4060" in info.gpu_name
        assert info.can_use_webengine is True
        assert "cuda" in info.compute_capabilities

    def test_gpu_info_with_npu(self):
        """Test GPUInfo with NPU (Neural Processing Unit)."""
        info = GPUInfo(
            has_gpu=True,
            gpu_type="intel",
            has_npu=True,
            npu_type="intel_npu",
            npu_name="Intel Neural Processing Unit",
            compute_capabilities=["openvino"],
        )

        assert info.has_npu is True
        assert info.npu_type == "intel_npu"
        assert "openvino" in info.compute_capabilities

    def test_gpu_info_no_gpu(self):
        """Test GPUInfo when no GPU is available."""
        info = GPUInfo(
            has_gpu=False,
            can_use_webengine=False,
            reason="No GPU detected, using software rendering",
        )

        assert info.has_gpu is False
        assert info.can_use_webengine is False
        assert "software rendering" in info.reason


class TestGPUCacheEntry:
    """Test suite for GPUCacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        gpu_info = GPUInfo(has_gpu=True, gpu_type="nvidia")
        entry = GPUCacheEntry.from_gpu_info(gpu_info, version="1.5.0")

        assert entry.version == "1.5.0"
        assert isinstance(entry.timestamp, str)
        assert isinstance(entry.gpu_info, dict)
        assert entry.gpu_info["has_gpu"] is True

    def test_cache_entry_to_gpu_info(self):
        """Test reconstructing GPUInfo from cache entry."""
        original = GPUInfo(
            has_gpu=True,
            gpu_type="amd",
            gpu_name="AMD Radeon RX 6800",
            compute_capabilities=["opencl", "vulkan"],
        )

        entry = GPUCacheEntry.from_gpu_info(original, "1.5.0")
        reconstructed = entry.to_gpu_info()

        assert reconstructed.has_gpu == original.has_gpu
        assert reconstructed.gpu_type == original.gpu_type
        assert reconstructed.gpu_name == original.gpu_name
        assert reconstructed.compute_capabilities == original.compute_capabilities

    def test_cache_entry_is_valid_fresh(self):
        """Test that fresh cache entry is valid."""
        gpu_info = GPUInfo(has_gpu=True)
        entry = GPUCacheEntry.from_gpu_info(gpu_info, "1.5.0")

        assert entry.is_valid(ttl_days=7) is True

    def test_cache_entry_is_valid_expired(self):
        """Test that old cache entry is invalid."""
        old_timestamp = (datetime.now() - timedelta(days=10)).isoformat()
        entry = GPUCacheEntry(
            timestamp=old_timestamp, gpu_info={"has_gpu": False}, version="1.4.0"
        )

        assert entry.is_valid(ttl_days=7) is False

    def test_cache_entry_is_valid_invalid_timestamp(self):
        """Test cache entry with invalid timestamp."""
        entry = GPUCacheEntry(
            timestamp="invalid-timestamp", gpu_info={"has_gpu": False}, version="1.5.0"
        )

        assert entry.is_valid(ttl_days=7) is False

    def test_cache_entry_custom_ttl(self):
        """Test cache entry validation with custom TTL."""
        timestamp = (datetime.now() - timedelta(days=5)).isoformat()
        entry = GPUCacheEntry(
            timestamp=timestamp, gpu_info={"has_gpu": True}, version="1.5.0"
        )

        # Valid with 7 day TTL
        assert entry.is_valid(ttl_days=7) is True
        # Invalid with 3 day TTL
        assert entry.is_valid(ttl_days=3) is False

    @pytest.mark.parametrize(
        "timestamp,ttl_days,expected_valid,test_id",
        [
            (datetime.now().isoformat(), 7, True, "fresh"),
            ((datetime.now() - timedelta(days=10)).isoformat(), 7, False, "expired"),
            ("invalid-timestamp", 7, False, "invalid_timestamp"),
        ],
    )
    def test_cache_entry_validation(self, timestamp, ttl_days, expected_valid, test_id):
        """Test cache entry validation with various timestamp scenarios.

        Parametrized test covering:
        - Fresh entries (valid)
        - Expired entries (invalid)
        - Invalid timestamp format (invalid)
        """
        entry = GPUCacheEntry(timestamp=timestamp, gpu_info={}, version="1.4.1")
        assert entry.is_valid(ttl_days=ttl_days) == expected_valid


class TestGPUDetectionCache:
    """Test suite for GPUDetectionCache."""

    def test_cache_file_path(self):
        """Test that cache file path is properly defined."""
        assert GPUDetectionCache.CACHE_FILE.is_absolute()
        assert "AsciiDocArtisan" in str(GPUDetectionCache.CACHE_FILE)
        assert "gpu_cache.json" in str(GPUDetectionCache.CACHE_FILE)

    def test_cache_ttl_defined(self):
        """Test that cache TTL is defined."""
        assert GPUDetectionCache.CACHE_TTL_DAYS > 0
        assert isinstance(GPUDetectionCache.CACHE_TTL_DAYS, int)

    def test_load_no_cache_file(self, tmp_path):
        """Test loading when cache file doesn't exist."""
        with patch.object(
            GPUDetectionCache, "CACHE_FILE", tmp_path / "nonexistent.json"
        ):
            result = GPUDetectionCache.load()
            assert result is None

    def test_load_valid_cache(self, tmp_path):
        """Test loading valid cache file."""
        cache_file = tmp_path / "gpu_cache.json"
        gpu_info = GPUInfo(has_gpu=True, gpu_type="nvidia", gpu_name="Test GPU")
        entry = GPUCacheEntry.from_gpu_info(gpu_info, "1.5.0")

        cache_file.write_text(
            json.dumps(
                {
                    "timestamp": entry.timestamp,
                    "gpu_info": entry.gpu_info,
                    "version": entry.version,
                }
            )
        )

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            loaded = GPUDetectionCache.load()
            assert loaded is not None
            assert loaded.has_gpu is True
            assert loaded.gpu_type == "nvidia"

    def test_load_expired_cache(self, tmp_path):
        """Test loading expired cache returns None."""
        cache_file = tmp_path / "gpu_cache.json"
        old_timestamp = (datetime.now() - timedelta(days=10)).isoformat()

        cache_file.write_text(
            json.dumps(
                {
                    "timestamp": old_timestamp,
                    "gpu_info": {"has_gpu": False},
                    "version": "1.0.0",
                }
            )
        )

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            loaded = GPUDetectionCache.load()
            assert loaded is None

    def test_load_corrupted_cache(self, tmp_path):
        """Test loading corrupted cache file returns None."""
        cache_file = tmp_path / "gpu_cache.json"
        cache_file.write_text("{ invalid json }")

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            loaded = GPUDetectionCache.load()
            assert loaded is None

    def test_save_cache(self, tmp_path):
        """Test saving GPU info to cache."""
        cache_file = tmp_path / "gpu_cache.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        gpu_info = GPUInfo(
            has_gpu=True, gpu_type="intel", compute_capabilities=["opencl"]
        )

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            GPUDetectionCache.save(gpu_info, version="1.5.0")

            assert cache_file.exists()
            data = json.loads(cache_file.read_text())
            assert data["gpu_info"]["has_gpu"] is True
            assert data["gpu_info"]["gpu_type"] == "intel"
            assert data["version"] == "1.5.0"

    def test_save_cache_creates_directory(self, tmp_path):
        """Test that save creates cache directory if it doesn't exist."""
        cache_file = tmp_path / "new_dir" / "gpu_cache.json"
        gpu_info = GPUInfo(has_gpu=False)

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            GPUDetectionCache.save(gpu_info, version="1.5.0")

            assert cache_file.exists()
            assert cache_file.parent.exists()

    def test_save_cache_overwrites_existing(self, tmp_path):
        """Test that save overwrites existing cache file."""
        cache_file = tmp_path / "gpu_cache.json"
        cache_file.write_text("old content")

        gpu_info = GPUInfo(has_gpu=True, gpu_type="amd")

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            GPUDetectionCache.save(gpu_info, version="2.0.0")

            data = json.loads(cache_file.read_text())
            assert data["version"] == "2.0.0"
            assert "old content" not in cache_file.read_text()

    def test_round_trip_cache(self, tmp_path):
        """Test saving and loading cache (round trip)."""
        cache_file = tmp_path / "gpu_cache.json"

        original = GPUInfo(
            has_gpu=True,
            gpu_type="nvidia",
            gpu_name="GeForce RTX 3090",
            driver_version="470.82.00",
            can_use_webengine=True,
            compute_capabilities=["cuda", "opencl", "vulkan"],
        )

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            # Save
            GPUDetectionCache.save(original, version="1.5.0")

            # Load
            loaded = GPUDetectionCache.load()

            assert loaded is not None
            assert loaded.has_gpu == original.has_gpu
            assert loaded.gpu_type == original.gpu_type
            assert loaded.gpu_name == original.gpu_name
            assert loaded.driver_version == original.driver_version
            assert loaded.can_use_webengine == original.can_use_webengine
            assert loaded.compute_capabilities == original.compute_capabilities

    def test_save_cache_generic_exception(self, tmp_path, mocker):
        """Test save_cache handles generic exception (lines 112-114)."""
        cache_file = tmp_path / "gpu_cache.json"

        # Mock write_text to raise generic exception
        mock_write = mocker.patch.object(Path, "write_text")
        mock_write.side_effect = RuntimeError("Unexpected error")

        gpu_info = GPUInfo(has_gpu=True)

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            result = GPUDetectionCache.save(gpu_info, "1.5.0")
            assert result is False

    def test_cache_format(self, mock_cache_file, sample_gpu_info):
        """Test cache file has correct JSON format."""
        GPUDetectionCache.save(sample_gpu_info, "1.4.1")

        data = json.loads(mock_cache_file.read_text())

        assert "timestamp" in data
        assert "gpu_info" in data
        assert "version" in data
        assert data["version"] == "1.4.1"
        assert data["gpu_info"]["gpu_type"] == "nvidia"

    def test_cache_with_npu(self, mock_cache_file):
        """Test caching GPU info with NPU."""
        gpu_info_with_npu = GPUInfo(
            has_gpu=True,
            gpu_type="intel",
            gpu_name="Intel Iris Xe Graphics",
            can_use_webengine=True,
            has_npu=True,
            npu_type="intel_npu",
            npu_name="Intel NPU",
            compute_capabilities=["opencl", "openvino"],
        )

        # Save and load
        GPUDetectionCache.save(gpu_info_with_npu, "1.4.1")
        loaded = GPUDetectionCache.load()

        assert loaded is not None
        assert loaded.has_npu is True
        assert loaded.npu_type == "intel_npu"
        assert loaded.npu_name == "Intel NPU"
        assert "openvino" in loaded.compute_capabilities

    def test_cache_without_gpu(self, mock_cache_file):
        """Test caching when no GPU detected."""
        no_gpu_info = GPUInfo(
            has_gpu=False,
            can_use_webengine=False,
            reason="No GPU detected",
            compute_capabilities=[],
        )

        # Save and load
        GPUDetectionCache.save(no_gpu_info, "1.4.1")
        loaded = GPUDetectionCache.load()

        assert loaded is not None
        assert loaded.has_gpu is False
        assert loaded.reason == "No GPU detected"
        assert len(loaded.compute_capabilities) == 0

    def test_cache_ttl_boundary(self, mock_cache_file, sample_gpu_info):
        """Test cache TTL boundary conditions."""
        # Save cache
        GPUDetectionCache.save(sample_gpu_info, "1.4.1")

        # Manually modify timestamp to be exactly at TTL boundary
        data = json.loads(mock_cache_file.read_text())
        boundary_time = datetime.now() - timedelta(days=7, seconds=-1)
        data["timestamp"] = boundary_time.isoformat()
        mock_cache_file.write_text(json.dumps(data))

        # Should still be valid (less than 7 days)
        loaded = GPUDetectionCache.load()
        assert loaded is not None

        # Modify to be just over TTL
        over_time = datetime.now() - timedelta(days=7, seconds=1)
        data["timestamp"] = over_time.isoformat()
        mock_cache_file.write_text(json.dumps(data))

        # Should be expired
        loaded = GPUDetectionCache.load()
        assert loaded is None


class TestCacheClear:
    """Test GPUDetectionCache.clear() method."""

    def test_clear_existing_cache(self, tmp_path):
        """Test clearing existing cache file."""
        cache_file = tmp_path / "gpu_cache.json"
        cache_file.write_text("{}")

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            assert cache_file.exists()
            GPUDetectionCache.clear()
            assert not cache_file.exists()

    def test_clear_nonexistent_cache(self, tmp_path):
        """Test clearing when cache doesn't exist."""
        cache_file = tmp_path / "gpu_cache.json"

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            assert not cache_file.exists()
            # Should not raise error
            GPUDetectionCache.clear()

    def test_clear_permission_error(self, tmp_path, mocker):
        """Test clear handles permission error."""
        cache_file = tmp_path / "gpu_cache.json"
        cache_file.write_text("{}")

        mock_unlink = mocker.patch.object(Path, "unlink")
        mock_unlink.side_effect = PermissionError("Cannot delete")

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            # Should log warning but not raise
            GPUDetectionCache.clear()


class TestCheckDRIDevices:
    """Test check_dri_devices() function."""

    def test_dri_with_render_device(self, mocker):
        """Test detecting /dev/dri/renderD* device."""
        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_dri = MagicMock()
        mock_path.return_value = mock_dri
        mock_dri.exists.return_value = True
        mock_dri.glob.side_effect = [
            [Path("/dev/dri/renderD128")],  # render devices
        ]

        has_dri, device = check_dri_devices()
        assert has_dri is True
        assert "renderD128" in str(device)

    def test_dri_with_card_device(self, mocker):
        """Test detecting /dev/dri/card* device."""
        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_dri = MagicMock()
        mock_path.return_value = mock_dri
        mock_dri.exists.return_value = True
        mock_dri.glob.side_effect = [
            [],  # No render devices
            [Path("/dev/dri/card0")],  # card devices
        ]

        has_dri, device = check_dri_devices()
        assert has_dri is True
        assert "card0" in str(device)

    def test_dri_not_exists(self, mocker):
        """Test when /dev/dri doesn't exist."""
        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_dri = MagicMock()
        mock_path.return_value = mock_dri
        mock_dri.exists.return_value = False

        has_dri, device = check_dri_devices()
        assert has_dri is False
        assert device is None

    def test_dri_no_devices(self, mocker):
        """Test when /dev/dri exists but no devices."""
        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_dri = MagicMock()
        mock_path.return_value = mock_dri
        mock_dri.exists.return_value = True
        mock_dri.glob.return_value = []

        has_dri, device = check_dri_devices()
        assert has_dri is False
        assert device is None


class TestCheckNvidiaGPU:
    """Test check_nvidia_gpu() function."""

    def test_nvidia_gpu_detected(self, mocker):
        """Test NVIDIA GPU detected via nvidia-smi."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="NVIDIA GeForce RTX 4060, 535.104.05\n"
        )

        has_nvidia, gpu_name, driver_version = check_nvidia_gpu()
        assert has_nvidia is True
        assert "RTX 4060" in gpu_name
        assert driver_version == "535.104.05"

    def test_nvidia_smi_not_found(self, mocker):
        """Test nvidia-smi not installed."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("nvidia-smi not found")

        has_nvidia, gpu_name, driver_version = check_nvidia_gpu()
        assert has_nvidia is False
        assert gpu_name is None
        assert driver_version is None

    def test_nvidia_smi_timeout(self, mocker):
        """Test nvidia-smi timeout."""
        import subprocess

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.TimeoutExpired("nvidia-smi", 5)

        has_nvidia, gpu_name, driver_version = check_nvidia_gpu()
        assert has_nvidia is False

    def test_nvidia_smi_empty_output(self, mocker):
        """Test nvidia-smi returns empty output."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        has_nvidia, gpu_name, driver_version = check_nvidia_gpu()
        assert has_nvidia is False


class TestCheckAMDGPU:
    """Test check_amd_gpu() function."""

    def test_amd_gpu_detected_card_series(self, mocker):
        """Test AMD GPU detected via rocm-smi (Card series)."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Card series: AMD Radeon RX 6800\n"
        )

        has_amd, gpu_name = check_amd_gpu()
        assert has_amd is True
        assert "RX 6800" in gpu_name

    def test_amd_gpu_detected_card_model(self, mocker):
        """Test AMD GPU detected via rocm-smi (Card model)."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Card model: AMD Radeon Pro W6800\n"
        )

        has_amd, gpu_name = check_amd_gpu()
        assert has_amd is True
        assert "W6800" in gpu_name

    def test_amd_gpu_unknown_model(self, mocker):
        """Test AMD GPU detected but model unknown."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stdout="Some other output\n")

        has_amd, gpu_name = check_amd_gpu()
        assert has_amd is True
        assert "unknown model" in gpu_name

    def test_rocm_smi_not_found(self, mocker):
        """Test rocm-smi not installed."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("rocm-smi not found")

        has_amd, gpu_name = check_amd_gpu()
        assert has_amd is False
        assert gpu_name is None


class TestCheckIntelGPU:
    """Test check_intel_gpu() function."""

    def test_intel_gpu_detected(self, mocker):
        """Test Intel GPU detected via clinfo."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Device Name: Intel(R) UHD Graphics 620\n"
        )

        has_intel, gpu_name = check_intel_gpu()
        assert has_intel is True
        assert "Intel" in gpu_name
        assert "620" in gpu_name

    def test_clinfo_not_found(self, mocker):
        """Test clinfo not installed."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("clinfo not found")

        has_intel, gpu_name = check_intel_gpu()
        assert has_intel is False
        assert gpu_name is None

    def test_clinfo_no_intel_device(self, mocker):
        """Test clinfo output but no Intel device."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Device Name: Some Other GPU\n"
        )

        has_intel, gpu_name = check_intel_gpu()
        assert has_intel is False


class TestCheckOpenGLRenderer:
    """Test check_opengl_renderer() function."""

    def test_hardware_renderer(self, mocker):
        """Test hardware OpenGL renderer."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="OpenGL renderer string: NVIDIA GeForce RTX 4060\n"
        )

        is_hardware, renderer = check_opengl_renderer()
        assert is_hardware is True
        assert "RTX 4060" in renderer

    def test_software_renderer_llvmpipe(self, mocker):
        """Test software renderer (llvmpipe)."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="OpenGL renderer string: llvmpipe (LLVM 12.0.0)\n"
        )

        is_hardware, renderer = check_opengl_renderer()
        assert is_hardware is False
        assert "llvmpipe" in renderer

    def test_software_renderer_generic(self, mocker):
        """Test software renderer (generic software)."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="OpenGL renderer string: Software Rasterizer\n"
        )

        is_hardware, renderer = check_opengl_renderer()
        assert is_hardware is False
        assert "Software" in renderer

    def test_glxinfo_not_found(self, mocker):
        """Test glxinfo not installed."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("glxinfo not found")

        is_hardware, renderer = check_opengl_renderer()
        assert is_hardware is False
        assert renderer is None


class TestCheckWSLgEnvironment:
    """Test check_wslg_environment() function."""

    def test_wslg_detected_wsl_distro(self, mocker):
        """Test WSLg detected via WSL_DISTRO_NAME."""
        mocker.patch.dict("os.environ", {"WSL_DISTRO_NAME": "Ubuntu"})
        assert check_wslg_environment() is True

    def test_wslg_detected_wsl_interop(self, mocker):
        """Test WSLg detected via WSL_INTEROP."""
        mocker.patch.dict("os.environ", {"WSL_INTEROP": "/run/WSL/1_interop"})
        assert check_wslg_environment() is True

    def test_wslg_detected_wayland(self, mocker):
        """Test WSLg detected via WAYLAND_DISPLAY."""
        mocker.patch.dict("os.environ", {"WAYLAND_DISPLAY": "wayland-0"})
        assert check_wslg_environment() is True

    def test_wslg_not_detected(self, mocker):
        """Test WSLg not detected."""
        mocker.patch.dict("os.environ", {}, clear=True)
        assert check_wslg_environment() is False


class TestCheckIntelNPU:
    """Test check_intel_npu() function."""

    def test_intel_npu_via_clinfo(self, mocker):
        """Test Intel NPU detected via clinfo."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Device Name: Intel(R) NPU Accelerator\n"
        )

        has_npu, npu_name = check_intel_npu()
        assert has_npu is True
        assert "NPU" in npu_name

    def test_intel_npu_via_accel_device(self, mocker):
        """Test Intel NPU detected via /dev/accel* device."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("clinfo not found")

        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_accel = MagicMock()
        mock_path.return_value = mock_accel
        mock_accel.glob.return_value = [Path("/dev/accel0")]

        has_npu, npu_name = check_intel_npu()
        assert has_npu is True
        assert "Intel NPU" in npu_name

    def test_no_npu_detected(self, mocker):
        """Test no NPU detected."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("clinfo not found")

        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_accel = MagicMock()
        mock_path.return_value = mock_accel
        mock_accel.glob.return_value = []

        has_npu, npu_name = check_intel_npu()
        assert has_npu is False
        assert npu_name is None


class TestDetectComputeCapabilities:
    """Test detect_compute_capabilities() function."""

    def test_cuda_detected(self, mocker):
        """Test CUDA capability detected."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=0)

        capabilities = detect_compute_capabilities()
        assert "cuda" in capabilities

    def test_opencl_detected(self, mocker):
        """Test OpenCL capability detected."""
        mock_run = mocker.patch("subprocess.run")
        # Need enough side_effect values for all subprocess.run calls (CUDA, OpenCL, Vulkan, Metal on macOS)
        mock_run.side_effect = [
            FileNotFoundError("nvidia-smi not found"),  # No CUDA
            MagicMock(returncode=0, stdout="Platform Name: Intel OpenCL"),  # OpenCL
            FileNotFoundError("vulkaninfo not found"),  # No Vulkan
            FileNotFoundError("system_profiler not found"),  # No Metal (or not macOS)
        ]

        capabilities = detect_compute_capabilities()
        assert "opencl" in capabilities

    def test_vulkan_detected(self, mocker):
        """Test Vulkan capability detected."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = [
            FileNotFoundError("nvidia-smi not found"),  # No CUDA
            FileNotFoundError("clinfo not found"),  # No OpenCL
            MagicMock(returncode=0),  # Vulkan
            FileNotFoundError("system_profiler not found"),  # No Metal (or not macOS)
        ]

        capabilities = detect_compute_capabilities()
        assert "vulkan" in capabilities

    def test_openvino_detected(self, mocker):
        """Test OpenVINO capability detected."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError()  # No command-line tools

        mock_path = mocker.patch("asciidoc_artisan.core.gpu_detection.Path")
        mock_openvino = MagicMock()
        mock_path.return_value = mock_openvino
        mock_openvino.exists.return_value = True

        capabilities = detect_compute_capabilities()
        assert "openvino" in capabilities

    def test_rocm_detected(self, mocker):
        """Test ROCm capability detected."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError()  # No command-line tools

        def mock_path_side_effect(path_str):
            mock_p = MagicMock()
            if "/opt/rocm" in path_str:
                mock_p.exists.return_value = True
            else:
                mock_p.exists.return_value = False
            return mock_p

        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.Path",
            side_effect=mock_path_side_effect,
        )

        capabilities = detect_compute_capabilities()
        assert "rocm" in capabilities


class TestDetectGPU:
    """Test detect_gpu() function."""

    def test_detect_gpu_no_dri(self, mocker):
        """Test GPU detection when /dev/dri not found."""
        # Mock platform to test Linux code path
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.platform.system", return_value="Linux"
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_dri_devices",
            return_value=(False, None),
        )

        gpu_info = detect_gpu()
        assert gpu_info.has_gpu is False
        assert gpu_info.can_use_webengine is False
        assert "dri not found" in gpu_info.reason.lower()

    def test_detect_gpu_software_renderer(self, mocker):
        """Test GPU detection with software renderer."""
        # Mock platform to test Linux code path
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.platform.system", return_value="Linux"
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_dri_devices",
            return_value=(True, "/dev/dri/renderD128"),
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_opengl_renderer",
            return_value=(False, "llvmpipe"),
        )

        gpu_info = detect_gpu()
        assert gpu_info.has_gpu is False
        assert gpu_info.can_use_webengine is False
        assert "Software rendering" in gpu_info.reason

    @pytest.mark.parametrize(
        "gpu_type,render_device,opengl_renderer,nvidia_return,amd_return,intel_return,wslg,npu_return,capabilities,expected_type,expected_name_fragment,expected_has_npu,test_id",
        [
            # NVIDIA GPU
            (
                "nvidia",
                "/dev/dri/renderD128",
                "NVIDIA RTX 4060",
                (True, "NVIDIA RTX 4060", "535.104"),
                (False, None),
                (False, None),
                True,
                (False, None),
                ["cuda", "vulkan"],
                "nvidia",
                "RTX 4060",
                False,
                "nvidia",
            ),
            # AMD GPU
            (
                "amd",
                "/dev/dri/renderD128",
                "AMD Radeon",
                (False, None, None),
                (True, "AMD Radeon RX 6800"),
                (False, None),
                False,
                (False, None),
                ["rocm"],
                "amd",
                "RX 6800",
                False,
                "amd",
            ),
            # Intel GPU with NPU
            (
                "intel",
                "/dev/dri/card0",
                "Intel UHD",
                (False, None, None),
                (False, None),
                (True, "Intel UHD 620"),
                False,
                (True, "Intel NPU"),
                ["opencl", "openvino"],
                "intel",
                "620",
                True,
                "intel",
            ),
            # Unknown GPU type
            (
                "unknown",
                "/dev/dri/card0",
                "Unknown Renderer",
                (False, None, None),
                (False, None),
                (False, None),
                False,
                (False, None),
                [],
                "unknown",
                None,
                False,
                "unknown",
            ),
        ],
    )
    def test_detect_gpu_by_type(
        self,
        mocker,
        gpu_type,
        render_device,
        opengl_renderer,
        nvidia_return,
        amd_return,
        intel_return,
        wslg,
        npu_return,
        capabilities,
        expected_type,
        expected_name_fragment,
        expected_has_npu,
        test_id,
    ):
        """Test GPU detection for various GPU types.

        Parametrized test covering:
        - NVIDIA GPU with CUDA
        - AMD GPU with ROCm
        - Intel GPU with NPU
        - Unknown GPU type
        """
        # Mock platform to test Linux code path
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.platform.system", return_value="Linux"
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_dri_devices",
            return_value=(True, render_device),
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_opengl_renderer",
            return_value=(True, opengl_renderer),
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_nvidia_gpu",
            return_value=nvidia_return,
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_amd_gpu", return_value=amd_return
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_intel_gpu",
            return_value=intel_return,
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_wslg_environment",
            return_value=wslg,
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.check_intel_npu",
            return_value=npu_return,
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.detect_compute_capabilities",
            return_value=capabilities,
        )

        gpu_info = detect_gpu()
        assert gpu_info.has_gpu is True
        assert gpu_info.gpu_type == expected_type
        if expected_name_fragment:
            assert expected_name_fragment in gpu_info.gpu_name
        assert gpu_info.has_npu == expected_has_npu


class TestLogGPUInfo:
    """Test log_gpu_info() function."""

    def test_log_gpu_with_all_info(self, mocker):
        """Test logging GPU info with all details."""
        mock_logger = mocker.patch("asciidoc_artisan.core.gpu_detection.logger")

        gpu_info = GPUInfo(
            has_gpu=True,
            gpu_type="nvidia",
            gpu_name="NVIDIA RTX 4060",
            driver_version="535.104",
            render_device="/dev/dri/renderD128",
            can_use_webengine=True,
            reason="Hardware acceleration available",
            has_npu=True,
            npu_type="intel_npu",
            npu_name="Intel NPU",
            compute_capabilities=["cuda", "vulkan"],
        )

        log_gpu_info(gpu_info)

        # Verify logging calls
        assert mock_logger.info.call_count >= 6  # Multiple info logs

    def test_log_no_gpu(self, mocker):
        """Test logging when no GPU detected."""
        mock_logger = mocker.patch("asciidoc_artisan.core.gpu_detection.logger")

        gpu_info = GPUInfo(has_gpu=False, reason="No GPU detected")

        log_gpu_info(gpu_info)

        # Verify warning logged
        mock_logger.warning.assert_called_once()

    def test_log_gpu_no_npu(self, mocker):
        """Test logging GPU without NPU."""
        mock_logger = mocker.patch("asciidoc_artisan.core.gpu_detection.logger")

        gpu_info = GPUInfo(
            has_gpu=True,
            gpu_type="intel",
            gpu_name="Intel UHD 620",
            reason="Hardware available",
        )

        log_gpu_info(gpu_info)

        # Verify "No NPU" logged
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("No NPU" in str(call) for call in calls)


class TestGetGPUInfo:
    """Test get_gpu_info() function."""

    def test_get_gpu_info_memory_cache(self, mocker):
        """Test get_gpu_info uses memory cache."""
        import asciidoc_artisan.core.gpu_detection as gpu_mod

        # Reset cache
        gpu_mod._cached_gpu_info = None

        mock_detect = mocker.patch("asciidoc_artisan.core.gpu_detection.detect_gpu")
        mock_detect.return_value = GPUInfo(has_gpu=True, gpu_type="nvidia")

        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.load",
            return_value=None,
        )
        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.save",
            return_value=True,
        )
        mocker.patch("asciidoc_artisan.core.gpu_detection.log_gpu_info")
        # Patch APP_VERSION in the core module where it's imported from
        mocker.patch("asciidoc_artisan.core.APP_VERSION", "1.5.0")

        # First call - should detect
        info1 = get_gpu_info()
        assert mock_detect.call_count == 1

        # Second call - should use memory cache
        info2 = get_gpu_info()
        assert mock_detect.call_count == 1  # Still 1 (cached)
        assert info1 is info2

    def test_get_gpu_info_disk_cache(self, mocker):
        """Test get_gpu_info uses disk cache."""
        import asciidoc_artisan.core.gpu_detection as gpu_mod

        # Reset memory cache
        gpu_mod._cached_gpu_info = None

        cached_info = GPUInfo(has_gpu=True, gpu_type="amd")
        mock_load = mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.load"
        )
        mock_load.return_value = cached_info

        mock_detect = mocker.patch("asciidoc_artisan.core.gpu_detection.detect_gpu")
        mocker.patch("asciidoc_artisan.core.gpu_detection.log_gpu_info")

        info = get_gpu_info()

        # Should load from disk, not detect
        assert mock_detect.call_count == 0
        assert info.gpu_type == "amd"

    def test_get_gpu_info_force_redetect(self, mocker):
        """Test get_gpu_info with force_redetect."""
        import asciidoc_artisan.core.gpu_detection as gpu_mod

        # Set memory cache
        gpu_mod._cached_gpu_info = GPUInfo(has_gpu=False)

        mock_detect = mocker.patch("asciidoc_artisan.core.gpu_detection.detect_gpu")
        mock_detect.return_value = GPUInfo(has_gpu=True, gpu_type="intel")

        mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.save",
            return_value=True,
        )
        mocker.patch("asciidoc_artisan.core.gpu_detection.log_gpu_info")
        # Patch APP_VERSION in the core module where it's imported from
        mocker.patch("asciidoc_artisan.core.APP_VERSION", "1.5.0")

        # Force redetect
        info = get_gpu_info(force_redetect=True)

        # Should detect even with cache
        assert mock_detect.call_count == 1
        assert info.has_gpu is True


class TestMainCLI:
    """Test main() CLI function."""

    def test_main_clear_command(self, mocker, capsys):
        """Test main() with 'clear' command."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py", "clear"])
        mock_clear = mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.clear"
        )

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "GPU cache cleared" in captured.out
        mock_clear.assert_called_once()

    def test_main_show_command_with_cache(self, mocker, capsys):
        """Test main() with 'show' command (cache exists)."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py", "show"])
        mock_load = mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.load"
        )
        mock_load.return_value = GPUInfo(
            has_gpu=True,
            gpu_type="nvidia",
            gpu_name="RTX 4060",
            has_npu=True,
            npu_name="Intel NPU",
            compute_capabilities=["cuda"],
        )

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "RTX 4060" in captured.out
        assert "nvidia" in captured.out
        assert "Intel NPU" in captured.out

    def test_main_show_command_no_cache(self, mocker, capsys):
        """Test main() with 'show' command (no cache)."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py", "show"])
        mock_load = mocker.patch(
            "asciidoc_artisan.core.gpu_detection.GPUDetectionCache.load"
        )
        mock_load.return_value = None

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "No cached GPU info" in captured.out

    def test_main_detect_command(self, mocker, capsys):
        """Test main() with 'detect' command."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py", "detect"])
        mock_get = mocker.patch("asciidoc_artisan.core.gpu_detection.get_gpu_info")
        mock_get.return_value = GPUInfo(
            has_gpu=True,
            gpu_type="amd",
            gpu_name="AMD RX 6800",
            driver_version="21.10",
            has_npu=False,
            compute_capabilities=["rocm", "vulkan"],
        )

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "AMD RX 6800" in captured.out
        assert "amd" in captured.out
        assert "21.10" in captured.out

    def test_main_detect_command_with_npu(self, mocker, capsys):
        """Test main() with 'detect' command with NPU (line 536)."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py", "detect"])
        mock_get = mocker.patch("asciidoc_artisan.core.gpu_detection.get_gpu_info")
        mock_get.return_value = GPUInfo(
            has_gpu=True,
            gpu_type="intel",
            gpu_name="Intel UHD 620",
            driver_version="1.0.0",
            has_npu=True,
            npu_name="Intel NPU",
            compute_capabilities=["opencl", "openvino"],
        )

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "Intel UHD 620" in captured.out
        assert "Intel NPU" in captured.out

    def test_main_unknown_command(self, mocker, capsys):
        """Test main() with unknown command."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py", "invalid"])

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "Unknown command" in captured.out
        assert "Usage" in captured.out

    def test_main_no_command(self, mocker, capsys):
        """Test main() with no command."""
        mocker.patch.object(sys, "argv", ["gpu_detection.py"])

        from asciidoc_artisan.core.gpu_detection import main

        main()

        captured = capsys.readouterr()
        assert "GPU Detection Cache Manager" in captured.out
        assert "Commands:" in captured.out
