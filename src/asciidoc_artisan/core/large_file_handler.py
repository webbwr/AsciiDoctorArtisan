"""
Large File Handler - Optimizations for handling large documents.

Provides streaming, chunking, and progress tracking for files > 1MB.
Implements performance optimizations per specification requirements.
"""

import logging
from pathlib import Path
from typing import Tuple

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

# File size thresholds (in bytes)
SMALL_FILE = 1024 * 1024  # 1 MB
MEDIUM_FILE = 5 * 1024 * 1024  # 5 MB
LARGE_FILE = 10 * 1024 * 1024  # 10 MB

# Preview optimization settings
PREVIEW_CHUNK_SIZE = 100000  # Characters to render for large files
PREVIEW_DISABLE_THRESHOLD = 50 * 1024 * 1024  # 50 MB - disable live preview


class LargeFileHandler(QObject):
    """
    Handles large file operations with optimization strategies.

    Strategies:
    - Small files (< 1MB): Normal loading
    - Medium files (1-10MB): Chunked preview, progress indicators
    - Large files (> 10MB): Lazy loading, preview optimization
    """

    progress_update = Signal(int, str)  # (percentage, message)
    file_loaded = Signal(str, Path)  # (content, file_path)

    def __init__(self):
        super().__init__()
        self._last_file_size = 0

    @staticmethod
    def get_file_size_category(file_path: Path) -> str:
        """
        Categorize file by size.

        Args:
            file_path: Path to file

        Returns:
            Category: 'small', 'medium', or 'large'
        """
        try:
            size = file_path.stat().st_size
            if size < SMALL_FILE:
                return "small"
            elif size < LARGE_FILE:
                return "medium"
            else:
                return "large"
        except Exception:
            return "small"

    @staticmethod
    def should_optimize_preview(file_size: int) -> bool:
        """
        Check if preview should be optimized for this file size.

        Args:
            file_size: Size in bytes

        Returns:
            True if preview should use optimization
        """
        return file_size > SMALL_FILE

    @staticmethod
    def should_disable_preview(file_size: int) -> bool:
        """
        Check if live preview should be disabled for this file size.

        Args:
            file_size: Size in bytes

        Returns:
            True if preview should be disabled
        """
        return file_size > PREVIEW_DISABLE_THRESHOLD

    def load_file_optimized(
        self, file_path: Path, encoding: str = "utf-8"
    ) -> Tuple[bool, str, str]:
        """
        Load file with size-appropriate optimizations.

        Args:
            file_path: Path to file
            encoding: Text encoding

        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            file_size = file_path.stat().st_size
            self._last_file_size = file_size
            category = self.get_file_size_category(file_path)

            logger.info(
                f"Loading {category} file: {file_path.name} ({file_size / 1024:.1f} KB)"
            )

            if category == "small":
                return self._load_small_file(file_path, encoding)
            elif category == "medium":
                return self._load_medium_file(file_path, encoding, file_size)
            else:
                return self._load_large_file(file_path, encoding, file_size)

        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            return False, "", f"Failed to load file: {e}"

    def _load_small_file(self, file_path: Path, encoding: str) -> Tuple[bool, str, str]:
        """Load small file normally (< 1MB)."""
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                content = f.read()
            return True, content, ""
        except Exception as e:
            return False, "", str(e)

    def _load_medium_file(
        self, file_path: Path, encoding: str, file_size: int
    ) -> Tuple[bool, str, str]:
        """Load medium file with progress indicators (1-10MB)."""
        try:
            self.progress_update.emit(0, f"Loading {file_path.name}...")

            # Read in chunks for progress feedback
            chunk_size = 1024 * 1024  # 1 MB chunks
            chunks = []
            bytes_read = 0

            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    chunks.append(chunk)
                    bytes_read += len(chunk.encode(encoding))

                    # Update progress
                    progress = int((bytes_read / file_size) * 100)
                    self.progress_update.emit(progress, f"Loading... {progress}%")

            content = "".join(chunks)
            self.progress_update.emit(100, "Load complete")

            return True, content, ""

        except Exception as e:
            self.progress_update.emit(0, "Load failed")
            return False, "", str(e)

    def _load_large_file(
        self, file_path: Path, encoding: str, file_size: int
    ) -> Tuple[bool, str, str]:
        """Load large file with chunked reading (> 10MB)."""
        try:
            self.progress_update.emit(0, f"Loading large file: {file_path.name}...")

            # For very large files, read line by line for better memory management
            lines = []
            bytes_read = 0
            last_progress = 0

            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                for line in f:
                    lines.append(line)
                    bytes_read += len(line.encode(encoding))

                    # Update progress every 5%
                    progress = int((bytes_read / file_size) * 100)
                    if progress - last_progress >= 5:
                        self.progress_update.emit(progress, f"Loading... {progress}%")
                        last_progress = progress

            content = "".join(lines)
            self.progress_update.emit(100, "Large file loaded")

            logger.info(
                f"Loaded large file: {len(content)} characters, {len(lines)} lines"
            )

            return True, content, ""

        except Exception as e:
            self.progress_update.emit(0, "Load failed")
            return False, "", str(e)

    @staticmethod
    def get_preview_content(content: str, max_chars: int = PREVIEW_CHUNK_SIZE) -> str:
        """
        Get optimized content for preview rendering.

        For large documents, returns only a portion to speed up rendering.

        Args:
            content: Full document content
            max_chars: Maximum characters to include

        Returns:
            Content for preview (may be truncated)
        """
        if len(content) <= max_chars:
            return content

        # Truncate at a line boundary
        truncated = content[:max_chars]
        last_newline = truncated.rfind("\n")
        if last_newline > 0:
            truncated = truncated[:last_newline]

        # Add truncation notice
        remaining = len(content) - len(truncated)
        notice = f"\n\n[Preview truncated - {remaining:,} characters not shown for performance]"

        return truncated + notice

    @staticmethod
    def estimate_load_time(file_size: int) -> str:
        """
        Estimate load time for a file.

        Args:
            file_size: Size in bytes

        Returns:
            Human-readable estimate
        """
        # Rough estimate: 10 MB/second reading speed
        seconds = file_size / (10 * 1024 * 1024)

        if seconds < 1:
            return "< 1 second"
        elif seconds < 5:
            return f"~{int(seconds)} seconds"
        else:
            return f"~{int(seconds / 60)} minutes"
