"""
TOON format utilities for settings persistence.

Token-Oriented Object Notation (TOON) is a compact, human-readable format
that reduces token count by 30-60% compared to JSON while preserving
full data fidelity.

v2.1.0: Added TOON support for settings with automatic JSON migration.

Features:
- 30-60% smaller than JSON
- Human-readable with YAML-like syntax
- Tabular arrays for uniform data
- Full JSON data model compatibility

Falls back to JSON if python-toon not available.
"""

import logging
from typing import Any, TextIO

from . import json_utils

logger = logging.getLogger(__name__)

# Try to import toon (python-toon package)
try:
    from toon import decode as toon_decode
    from toon import encode as toon_encode
    from toon.types import EncodeOptions

    HAS_TOON = True
    logger.debug("TOON format available (python-toon)")
except ImportError:
    HAS_TOON = False
    EncodeOptions = None
    toon_encode = None
    toon_decode = None
    logger.warning("python-toon not installed, falling back to JSON")


def loads(s: str) -> Any:
    """
    Deserialize TOON string to Python object.

    Args:
        s: TOON-formatted string

    Returns:
        Deserialized Python object
    """
    if HAS_TOON:
        try:
            return toon_decode(s)
        except Exception as e:
            logger.warning(f"TOON decode failed, trying JSON: {e}")
            # Fall back to JSON (for migration)
            return json_utils.loads(s)
    else:
        return json_utils.loads(s)


def dumps(obj: Any, indent: int = 2) -> str:
    """
    Serialize Python object to TOON string.

    Args:
        obj: Python object to serialize
        indent: Indentation spaces (default: 2)

    Returns:
        TOON-formatted string
    """
    if HAS_TOON and toon_encode is not None and EncodeOptions is not None:
        try:
            opts = EncodeOptions(indent=indent)
            result: str = toon_encode(obj, opts)
            return result
        except Exception as e:
            logger.warning(f"TOON encode failed, using JSON: {e}")
            return json_utils.dumps(obj, indent=indent)
    else:
        return json_utils.dumps(obj, indent=indent)


def load(fp: TextIO) -> Any:
    """
    Deserialize TOON from file object.

    Automatically detects JSON content and parses accordingly
    (for backward compatibility during migration).

    Args:
        fp: File object opened in text mode

    Returns:
        Deserialized Python object
    """
    content = fp.read()

    # Detect if content is JSON (starts with { or [)
    stripped = content.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        logger.info("Detected JSON format, parsing as JSON (migration)")
        return json_utils.loads(content)

    if HAS_TOON:
        try:
            return toon_decode(content)
        except Exception as e:
            logger.warning(f"TOON decode failed: {e}")
            # Try JSON as fallback
            return json_utils.loads(content)
    else:
        return json_utils.loads(content)


def dump(obj: Any, fp: TextIO, indent: int = 2) -> None:
    """
    Serialize Python object to TOON file.

    Args:
        obj: Python object to serialize
        fp: File object opened in text/write mode
        indent: Indentation spaces (default: 2)
    """
    toon_str = dumps(obj, indent=indent)
    fp.write(toon_str)


def is_toon_available() -> bool:
    """Check if TOON format is available."""
    return HAS_TOON
