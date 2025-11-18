"""
Secure file operation utilities.

This module provides secure file I/O functions that implement:
- Atomic writes (temp file + rename pattern) to prevent corruption
- Path sanitization to prevent directory traversal attacks

These functions are used throughout the application to ensure data integrity
and security per FR-015, FR-016, NFR-006, NFR-007, NFR-009.

Security Guarantees:
- FR-015: Atomic file writes prevent corruption on interruption
- FR-016: Path sanitization prevents directory traversal
- NFR-006: File save operations are atomic
- NFR-007: Never lose user data due to write failures
- NFR-009: Path sanitization prevents directory traversal attacks
"""

import logging
from pathlib import Path
from typing import Any

from . import json_utils

logger = logging.getLogger(__name__)


def sanitize_path(path_input: str | Path, allowed_base: Path | None = None) -> Path | None:
    """
    Sanitize file path to prevent directory traversal attacks.

    Implements FR-016 and NFR-009 security requirements by:
    - Checking for '..' components BEFORE resolving (security fix)
    - Resolving symbolic links and relative paths to absolute paths
    - Optionally validating path is within allowed base directory
    - Preventing directory traversal attacks

    Args:
        path_input: Path as string or Path object
        allowed_base: Optional base directory - if provided, resolved path
                     must be within this directory tree

    Returns:
        Resolved Path object if safe, None if suspicious patterns detected

    Security:
        - Checks for '..' BEFORE resolve() to catch traversal attempts
        - Resolves symbolic links and relative paths
        - Optional whitelist validation via allowed_base
        - Prevents directory traversal attacks (NFR-009)

    Examples:
        >>> sanitize_path("/home/user/doc.adoc")
        PosixPath('/home/user/doc.adoc')
        >>> sanitize_path("../../etc/passwd")
        None  # Blocked due to '..' traversal
        >>> sanitize_path("/home/user/doc.adoc", allowed_base=Path("/home/user"))
        PosixPath('/home/user/doc.adoc')
        >>> sanitize_path("/etc/passwd", allowed_base=Path("/home/user"))
        None  # Blocked - outside allowed base
    """
    try:
        # SECURITY FIX: Check for '..' BEFORE resolve() to catch traversal attempts
        # Previously, resolve() eliminated '..' before we could detect it
        path_obj = Path(path_input)
        if ".." in path_obj.parts:
            logger.warning(f"Path sanitization blocked suspicious path (contains '..'): {path_input}")
            return None

        # Now resolve to absolute path (eliminate symlinks, relative components)
        resolved_path = path_obj.resolve()

        # Optional: Validate path is within allowed base directory
        if allowed_base is not None:
            allowed_base_resolved = allowed_base.resolve()
            try:
                # Check if resolved_path is relative to allowed_base
                resolved_path.relative_to(allowed_base_resolved)
            except ValueError:
                logger.warning(
                    f"Path sanitization blocked path outside allowed base: {path_input} (base: {allowed_base})"
                )
                return None

        return resolved_path
    except Exception as e:
        logger.error(f"Path sanitization failed for {path_input}: {e}")
        return None


def atomic_save_text(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """
    Atomically save text content to file using temp file + rename pattern.

    Implements FR-015, NFR-006, NFR-007 reliability requirements.

    This prevents file corruption if the write operation is interrupted by
    crash, power loss, or other system failures. The atomic rename operation
    ensures the file is either fully written or not modified at all.

    Args:
        file_path: Target file path
        content: Text content to write
        encoding: Text encoding (default: utf-8)

    Returns:
        True if successful, False otherwise

    Implementation:
        1. Write to temporary file in same directory (.tmp extension)
        2. Perform atomic rename to target path (OS-level atomic operation)
        3. Cleanup temp file on failure

    Example:
        >>> atomic_save_text(Path("document.adoc"), "= My Document\\n\\nContent here")
        True
    """
    if not file_path:
        logger.error("atomic_save_text: file_path is None")
        return False

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        # Step 1: Write to temporary file
        temp_path.write_text(content, encoding=encoding)

        # Step 2: Atomic rename (OS guarantees atomicity)
        temp_path.replace(file_path)

        logger.debug(f"Atomic save successful: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Atomic save failed for {file_path}: {e}")

        # Step 3: Cleanup on failure
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")

        return False


def atomic_save_json(file_path: Path, data: dict[str, Any], encoding: str = "utf-8", indent: int = 2) -> bool:
    """
    Atomically save JSON data to file using temp file + rename pattern.

    Implements FR-015, NFR-006, NFR-007 for JSON serialization.
    Used primarily for settings persistence.

    Args:
        file_path: Target file path
        data: Dictionary to serialize as JSON
        encoding: Text encoding (default: utf-8)
        indent: JSON indentation for readability (default: 2)

    Returns:
        True if successful, False otherwise

    Example:
        >>> atomic_save_json(Path("settings.json"), {"theme": "dark", "font_size": 12})
        True
    """
    if not file_path:
        logger.error("atomic_save_json: file_path is None")
        return False

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        # Step 1: Write JSON to temporary file (3-5x faster with orjson via json_utils)
        with open(temp_path, "w", encoding=encoding) as f:
            json_utils.dump(data, f, indent=indent)

        # Step 2: Atomic rename
        temp_path.replace(file_path)

        logger.debug(f"Atomic JSON save successful: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Atomic JSON save failed for {file_path}: {e}")

        # Step 3: Cleanup on failure
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")

        return False
