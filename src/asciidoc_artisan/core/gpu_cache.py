"""
GPU Detection Cache Management.

Extracted from gpu_detection.py for MA principle compliance.
Handles persistent caching of GPU detection results.
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path

from asciidoc_artisan.core.gpu_models import GPUCacheEntry, GPUInfo

logger = logging.getLogger(__name__)


class GPUDetectionCache:
    """Persistent cache for GPU detection results."""

    CACHE_FILE = Path.home() / ".config" / "AsciiDocArtisan" / "gpu_cache.json"
    CACHE_TTL_DAYS = 7

    @classmethod
    def load(cls) -> GPUInfo | None:
        """Load GPU info from cache if valid."""
        try:
            if not cls.CACHE_FILE.exists():
                logger.debug("GPU cache file not found")
                return None

            # Read and parse cache file JSON.
            data = json.loads(cls.CACHE_FILE.read_text())
            entry = GPUCacheEntry(**data)

            # Check if cache is still fresh (within TTL).
            if not entry.is_valid(cls.CACHE_TTL_DAYS):
                logger.info("GPU cache expired")
                return None

            logger.info(f"GPU cache loaded (age: {entry.timestamp})")
            return entry.to_gpu_info()

        except Exception as e:
            # Corrupted cache file - will re-detect GPU.
            logger.warning(f"Failed to load GPU cache: {e}")
            return None

    @classmethod
    def save(cls, gpu_info: GPUInfo, version: str) -> bool:
        """Save GPU info to cache."""
        try:
            cls.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

            entry = GPUCacheEntry.from_gpu_info(gpu_info, version)
            cls.CACHE_FILE.write_text(json.dumps(asdict(entry), indent=2))

            logger.info("GPU cache saved")
            return True

        except Exception as e:
            logger.error(f"Failed to save GPU cache: {e}")
            return False

    @classmethod
    def clear(cls) -> None:
        """Clear GPU cache."""
        try:
            if cls.CACHE_FILE.exists():
                cls.CACHE_FILE.unlink()
                logger.info("GPU cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear GPU cache: {e}")
