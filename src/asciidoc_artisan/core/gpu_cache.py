"""
GPU Detection Cache Management.

Extracted from gpu_detection.py for MA principle compliance.
Handles persistent caching of GPU detection results.
v2.1.0: Uses TOON format for cache storage.
"""

import logging
from dataclasses import asdict
from pathlib import Path

from asciidoc_artisan.core.gpu_models import GPUCacheEntry, GPUInfo

from . import toon_utils

logger = logging.getLogger(__name__)


class GPUDetectionCache:
    """Persistent cache for GPU detection results (TOON format)."""

    CACHE_FILE = Path.home() / ".config" / "AsciiDocArtisan" / "gpu_cache.toon"
    LEGACY_CACHE_FILE = Path.home() / ".config" / "AsciiDocArtisan" / "gpu_cache.json"
    CACHE_TTL_DAYS = 7

    @classmethod
    def _migrate_legacy_json(cls) -> dict | None:
        """Migrate legacy JSON cache to TOON format."""
        if not cls.LEGACY_CACHE_FILE.exists():
            return None

        try:
            import json

            data = json.loads(cls.LEGACY_CACHE_FILE.read_text())

            # Save as TOON
            cls.CACHE_FILE.write_text(toon_utils.dumps(data))

            # Backup legacy file
            backup_path = cls.LEGACY_CACHE_FILE.with_suffix(".json.bak")
            cls.LEGACY_CACHE_FILE.rename(backup_path)
            logger.info(f"Migrated GPU cache: {cls.LEGACY_CACHE_FILE} → {cls.CACHE_FILE}")

            return data
        except Exception as e:
            logger.warning(f"Failed to migrate legacy GPU cache: {e}")
            return None

    @classmethod
    def load(cls) -> GPUInfo | None:
        """Load GPU info from cache if valid."""
        try:
            # Try TOON file first
            if cls.CACHE_FILE.exists():
                data = toon_utils.loads(cls.CACHE_FILE.read_text())
            elif cls.LEGACY_CACHE_FILE.exists():
                # Migrate legacy JSON
                data = cls._migrate_legacy_json()
                if data is None:
                    return None
            else:
                logger.debug("GPU cache file not found")
                return None

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
        """Save GPU info to cache (TOON format)."""
        try:
            cls.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

            entry = GPUCacheEntry.from_gpu_info(gpu_info, version)
            cls.CACHE_FILE.write_text(toon_utils.dumps(asdict(entry)))

            logger.info("GPU cache saved (TOON format)")
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
