"""
GPU Detection Data Models.

Extracted from gpu_detection.py for MA principle compliance.
Contains data structures for GPU/NPU information and caching.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class GPUInfo:
    """GPU and NPU information container."""

    has_gpu: bool
    gpu_type: str | None = None  # "nvidia", "amd", "intel", "apple", "unknown"
    gpu_name: str | None = None
    driver_version: str | None = None
    render_device: str | None = None  # e.g., "/dev/dri/renderD128" (Linux) or "Metal" (macOS)
    can_use_webengine: bool = False
    reason: str = ""  # Explanation
    has_npu: bool = False  # Neural Processing Unit
    npu_type: str | None = None  # "intel_npu", "apple_neural_engine", etc.
    npu_name: str | None = None
    compute_capabilities: list[str] = field(
        default_factory=list
    )  # ["cuda", "opencl", "vulkan", "openvino", "metal", etc.]
    metal_version: str | None = None  # Metal framework version (macOS only)


@dataclass
class GPUCacheEntry:
    """GPU detection cache entry."""

    timestamp: str  # ISO format
    gpu_info: dict[str, Any]  # Serialized GPUInfo
    version: str  # App version

    @classmethod
    def from_gpu_info(cls, gpu_info: GPUInfo, version: str) -> "GPUCacheEntry":
        """Create cache entry from GPUInfo."""
        return cls(
            timestamp=datetime.now().isoformat(),
            gpu_info=asdict(gpu_info),
            version=version,
        )

    def to_gpu_info(self) -> GPUInfo:
        """Reconstruct GPUInfo from cache."""
        return GPUInfo(**self.gpu_info)

    def is_valid(self, ttl_days: int = 7) -> bool:
        """Check if cache entry is still valid."""
        try:
            # Parse timestamp and calculate age.
            cache_time = datetime.fromisoformat(self.timestamp)
            age = datetime.now() - cache_time
            # Cache is valid if younger than TTL.
            return age < timedelta(days=ttl_days)
        except (ValueError, TypeError):
            # Invalid timestamp format - treat as expired.
            return False
