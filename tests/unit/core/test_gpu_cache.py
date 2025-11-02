"""
Tests for GPU detection caching.

Tests the GPUDetectionCache system that reduces startup time by caching
GPU detection results to disk.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from asciidoc_artisan.core.gpu_detection import (
    GPUInfo,
    GPUCacheEntry,
    GPUDetectionCache,
    get_gpu_info
)


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
        compute_capabilities=["cuda", "opencl", "vulkan"]
    )


def test_cache_entry_creation(sample_gpu_info):
    """Test cache entry can be created from GPUInfo."""
    entry = GPUCacheEntry.from_gpu_info(sample_gpu_info, "1.4.1")

    assert entry.version == "1.4.1"
    assert entry.gpu_info["gpu_name"] == "NVIDIA GeForce RTX 4060 Laptop GPU"
    assert entry.gpu_info["gpu_type"] == "nvidia"
    assert entry.gpu_info["has_gpu"] is True
    assert "cuda" in entry.gpu_info["compute_capabilities"]


def test_cache_entry_to_gpu_info(sample_gpu_info):
    """Test reconstructing GPUInfo from cache entry."""
    entry = GPUCacheEntry.from_gpu_info(sample_gpu_info, "1.4.1")
    reconstructed = entry.to_gpu_info()

    assert reconstructed.gpu_name == sample_gpu_info.gpu_name
    assert reconstructed.gpu_type == sample_gpu_info.gpu_type
    assert reconstructed.has_gpu == sample_gpu_info.has_gpu
    assert reconstructed.compute_capabilities == sample_gpu_info.compute_capabilities


@pytest.mark.parametrize("timestamp,ttl_days,expected_valid,test_id", [
    (datetime.now().isoformat(), 7, True, "fresh"),
    ((datetime.now() - timedelta(days=10)).isoformat(), 7, False, "expired"),
    ("invalid-timestamp", 7, False, "invalid_timestamp"),
])
def test_cache_entry_validation(timestamp, ttl_days, expected_valid, test_id):
    """Test cache entry validation with various timestamp scenarios.

    Parametrized test covering:
    - Fresh entries (valid)
    - Expired entries (invalid)
    - Invalid timestamp format (invalid)
    """
    entry = GPUCacheEntry(
        timestamp=timestamp,
        gpu_info={},
        version="1.4.1"
    )
    assert entry.is_valid(ttl_days=ttl_days) == expected_valid


def test_cache_save_creates_file(mock_cache_file, sample_gpu_info):
    """Test cache save creates cache file."""
    assert not mock_cache_file.exists()

    result = GPUDetectionCache.save(sample_gpu_info, "1.4.1")

    assert result is True
    assert mock_cache_file.exists()


def test_cache_save_and_load(mock_cache_file, sample_gpu_info):
    """Test saving and loading cache."""
    # Save
    assert GPUDetectionCache.save(sample_gpu_info, "1.4.1")
    assert mock_cache_file.exists()

    # Load
    loaded = GPUDetectionCache.load()
    assert loaded is not None
    assert loaded.gpu_name == "NVIDIA GeForce RTX 4060 Laptop GPU"
    assert loaded.gpu_type == "nvidia"
    assert loaded.has_gpu is True
    assert "cuda" in loaded.compute_capabilities


def test_cache_load_nonexistent_file(mock_cache_file):
    """Test loading cache when file doesn't exist."""
    assert not mock_cache_file.exists()

    loaded = GPUDetectionCache.load()
    assert loaded is None


def test_cache_load_expired(mock_cache_file, sample_gpu_info):
    """Test loading expired cache returns None."""
    # Create expired cache entry
    expired_entry = GPUCacheEntry(
        timestamp=(datetime.now() - timedelta(days=10)).isoformat(),
        gpu_info=sample_gpu_info.__dict__,
        version="1.4.1"
    )

    # Manually write expired cache
    mock_cache_file.parent.mkdir(parents=True, exist_ok=True)
    mock_cache_file.write_text(
        json.dumps({
            "timestamp": expired_entry.timestamp,
            "gpu_info": expired_entry.gpu_info,
            "version": expired_entry.version
        })
    )

    loaded = GPUDetectionCache.load()
    assert loaded is None


def test_cache_load_invalid_json(mock_cache_file):
    """Test loading cache with invalid JSON."""
    mock_cache_file.parent.mkdir(parents=True, exist_ok=True)
    mock_cache_file.write_text("invalid json{")

    loaded = GPUDetectionCache.load()
    assert loaded is None


def test_cache_clear(mock_cache_file, sample_gpu_info):
    """Test cache clearing."""
    # Save cache
    GPUDetectionCache.save(sample_gpu_info, "1.4.1")
    assert mock_cache_file.exists()

    # Clear cache
    GPUDetectionCache.clear()
    assert not mock_cache_file.exists()


def test_cache_clear_nonexistent():
    """Test clearing cache when file doesn't exist."""
    # Should not raise error
    GPUDetectionCache.clear()


def test_cache_format(mock_cache_file, sample_gpu_info):
    """Test cache file has correct JSON format."""
    GPUDetectionCache.save(sample_gpu_info, "1.4.1")

    data = json.loads(mock_cache_file.read_text())

    assert "timestamp" in data
    assert "gpu_info" in data
    assert "version" in data
    assert data["version"] == "1.4.1"
    assert data["gpu_info"]["gpu_type"] == "nvidia"


def test_get_gpu_info_uses_cache(mock_cache_file, sample_gpu_info, monkeypatch):
    """Test get_gpu_info uses cache when available."""
    # Save cache
    GPUDetectionCache.save(sample_gpu_info, "1.4.1")

    # Reset memory cache
    import asciidoc_artisan.core.gpu_detection as gpu_module
    gpu_module._cached_gpu_info = None

    # Mock detect_gpu to verify it's not called
    detect_called = []

    def mock_detect():
        detect_called.append(True)
        return sample_gpu_info

    monkeypatch.setattr(gpu_module, "detect_gpu", mock_detect)

    # Get GPU info should use cache
    info = get_gpu_info()

    assert len(detect_called) == 0  # detect_gpu not called
    assert info.gpu_name == sample_gpu_info.gpu_name


def test_get_gpu_info_force_redetect(mock_cache_file, sample_gpu_info, monkeypatch):
    """Test get_gpu_info force_redetect bypasses cache."""
    # Save cache
    GPUDetectionCache.save(sample_gpu_info, "1.4.1")

    # Mock detect_gpu to verify it IS called
    detect_called = []

    def mock_detect():
        detect_called.append(True)
        return sample_gpu_info

    import asciidoc_artisan.core.gpu_detection as gpu_module
    monkeypatch.setattr(gpu_module, "detect_gpu", mock_detect)

    # Force redetection
    info = get_gpu_info(force_redetect=True)

    assert len(detect_called) == 1  # detect_gpu WAS called
    assert info.gpu_name == sample_gpu_info.gpu_name


def test_cache_with_npu(mock_cache_file):
    """Test caching GPU info with NPU."""
    gpu_info_with_npu = GPUInfo(
        has_gpu=True,
        gpu_type="intel",
        gpu_name="Intel Iris Xe Graphics",
        can_use_webengine=True,
        has_npu=True,
        npu_type="intel_npu",
        npu_name="Intel NPU",
        compute_capabilities=["opencl", "openvino"]
    )

    # Save and load
    GPUDetectionCache.save(gpu_info_with_npu, "1.4.1")
    loaded = GPUDetectionCache.load()

    assert loaded is not None
    assert loaded.has_npu is True
    assert loaded.npu_type == "intel_npu"
    assert loaded.npu_name == "Intel NPU"
    assert "openvino" in loaded.compute_capabilities


def test_cache_without_gpu(mock_cache_file):
    """Test caching when no GPU detected."""
    no_gpu_info = GPUInfo(
        has_gpu=False,
        can_use_webengine=False,
        reason="No GPU detected",
        compute_capabilities=[]
    )

    # Save and load
    GPUDetectionCache.save(no_gpu_info, "1.4.1")
    loaded = GPUDetectionCache.load()

    assert loaded is not None
    assert loaded.has_gpu is False
    assert loaded.reason == "No GPU detected"
    assert len(loaded.compute_capabilities) == 0


def test_cache_ttl_boundary(mock_cache_file, sample_gpu_info):
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
