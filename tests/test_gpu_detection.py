"""
Tests for core.gpu_detection module.

Tests GPU detection, caching, and NPU detection functionality.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from asciidoc_artisan.core.gpu_detection import (
    GPUInfo,
    GPUCacheEntry,
    GPUDetectionCache,
)


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
            compute_capabilities=["cuda", "opencl", "vulkan"]
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
            compute_capabilities=["openvino"]
        )

        assert info.has_npu is True
        assert info.npu_type == "intel_npu"
        assert "openvino" in info.compute_capabilities

    def test_gpu_info_no_gpu(self):
        """Test GPUInfo when no GPU is available."""
        info = GPUInfo(
            has_gpu=False,
            can_use_webengine=False,
            reason="No GPU detected, using software rendering"
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
            compute_capabilities=["opencl", "vulkan"]
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
            timestamp=old_timestamp,
            gpu_info={"has_gpu": False},
            version="1.4.0"
        )

        assert entry.is_valid(ttl_days=7) is False

    def test_cache_entry_is_valid_invalid_timestamp(self):
        """Test cache entry with invalid timestamp."""
        entry = GPUCacheEntry(
            timestamp="invalid-timestamp",
            gpu_info={"has_gpu": False},
            version="1.5.0"
        )

        assert entry.is_valid(ttl_days=7) is False

    def test_cache_entry_custom_ttl(self):
        """Test cache entry validation with custom TTL."""
        timestamp = (datetime.now() - timedelta(days=5)).isoformat()
        entry = GPUCacheEntry(
            timestamp=timestamp,
            gpu_info={"has_gpu": True},
            version="1.5.0"
        )

        # Valid with 7 day TTL
        assert entry.is_valid(ttl_days=7) is True
        # Invalid with 3 day TTL
        assert entry.is_valid(ttl_days=3) is False


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
        with patch.object(GPUDetectionCache, "CACHE_FILE", tmp_path / "nonexistent.json"):
            result = GPUDetectionCache.load()
            assert result is None

    def test_load_valid_cache(self, tmp_path):
        """Test loading valid cache file."""
        cache_file = tmp_path / "gpu_cache.json"
        gpu_info = GPUInfo(has_gpu=True, gpu_type="nvidia", gpu_name="Test GPU")
        entry = GPUCacheEntry.from_gpu_info(gpu_info, "1.5.0")

        cache_file.write_text(json.dumps({
            "timestamp": entry.timestamp,
            "gpu_info": entry.gpu_info,
            "version": entry.version
        }))

        with patch.object(GPUDetectionCache, "CACHE_FILE", cache_file):
            loaded = GPUDetectionCache.load()
            assert loaded is not None
            assert loaded.has_gpu is True
            assert loaded.gpu_type == "nvidia"

    def test_load_expired_cache(self, tmp_path):
        """Test loading expired cache returns None."""
        cache_file = tmp_path / "gpu_cache.json"
        old_timestamp = (datetime.now() - timedelta(days=10)).isoformat()

        cache_file.write_text(json.dumps({
            "timestamp": old_timestamp,
            "gpu_info": {"has_gpu": False},
            "version": "1.0.0"
        }))

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
            has_gpu=True,
            gpu_type="intel",
            compute_capabilities=["opencl"]
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
            compute_capabilities=["cuda", "opencl", "vulkan"]
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
