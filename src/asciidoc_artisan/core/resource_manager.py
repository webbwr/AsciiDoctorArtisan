"""
Resource Manager - Track and clean up temporary resources.

This module manages temporary files, directories, and other resources
to prevent memory leaks and disk space waste.

Implements Phase 2.1 of Performance Optimization Plan:
- Track temporary files and directories
- Automatic cleanup on exit
- Resource lifetime management
- Memory leak prevention

Features:
- Temp file tracking
- Temp directory management
- Cleanup on exit via atexit
- Context manager support
- Resource statistics
"""

import atexit
import logging
import os
import shutil
import tempfile
from typing import Optional, Set

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manages temporary resources and ensures cleanup.

    Tracks temporary files and directories, ensuring they are
    cleaned up when no longer needed or when the application exits.

    Example:
        # Singleton usage
        rm = ResourceManager.get_instance()

        # Create tracked temp file
        temp_file = rm.create_temp_file(suffix='.html')

        # Create tracked temp directory
        temp_dir = rm.create_temp_directory()

        # Manual cleanup
        rm.cleanup_all()

        # Automatic cleanup on exit (via atexit)
    """

    _instance: Optional["ResourceManager"] = None

    def __init__(self):
        """Initialize ResourceManager."""
        self._temp_files: Set[str] = set()
        self._temp_directories: Set[str] = set()
        self._cleaned_up = False

        # Register cleanup on exit
        atexit.register(self.cleanup_all)

        logger.debug("ResourceManager initialized")

    @classmethod
    def get_instance(cls) -> "ResourceManager":
        """
        Get singleton instance.

        Returns:
            ResourceManager instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_temp_file(
        self,
        suffix: str = "",
        prefix: str = "asciidoc_artisan_",
        dir: Optional[str] = None,
        text: bool = True,
    ) -> str:
        """
        Create tracked temporary file.

        Args:
            suffix: File suffix (e.g., '.html')
            prefix: File prefix
            dir: Directory to create file in (None = default temp)
            text: True for text mode, False for binary

        Returns:
            Path to temporary file
        """
        # Create temp file
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)

        # Close file descriptor (caller will open file)
        os.close(fd)

        # Track file
        self._temp_files.add(path)

        logger.debug(f"Created temp file: {path}")
        return path

    def create_temp_directory(
        self,
        suffix: str = "",
        prefix: str = "asciidoc_artisan_",
        dir: Optional[str] = None,
    ) -> str:
        """
        Create tracked temporary directory.

        Args:
            suffix: Directory suffix
            prefix: Directory prefix
            dir: Parent directory (None = default temp)

        Returns:
            Path to temporary directory
        """
        # Create temp directory
        path = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

        # Track directory
        self._temp_directories.add(path)

        logger.debug(f"Created temp directory: {path}")
        return path

    def register_temp_file(self, path: str) -> None:
        """
        Register existing file for cleanup.

        Args:
            path: Path to file
        """
        self._temp_files.add(path)
        logger.debug(f"Registered temp file: {path}")

    def register_temp_directory(self, path: str) -> None:
        """
        Register existing directory for cleanup.

        Args:
            path: Path to directory
        """
        self._temp_directories.add(path)
        logger.debug(f"Registered temp directory: {path}")

    def unregister_temp_file(self, path: str) -> None:
        """
        Unregister file (won't be cleaned up).

        Args:
            path: Path to file
        """
        self._temp_files.discard(path)
        logger.debug(f"Unregistered temp file: {path}")

    def unregister_temp_directory(self, path: str) -> None:
        """
        Unregister directory (won't be cleaned up).

        Args:
            path: Path to directory
        """
        self._temp_directories.discard(path)
        logger.debug(f"Unregistered temp directory: {path}")

    def cleanup_file(self, path: str) -> bool:
        """
        Clean up specific file.

        Args:
            path: Path to file

        Returns:
            True if cleaned up successfully
        """
        if path not in self._temp_files:
            return False

        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Cleaned up temp file: {path}")

            self._temp_files.discard(path)
            return True

        except Exception as exc:
            logger.warning(f"Failed to cleanup temp file {path}: {exc}")
            return False

    def cleanup_directory(self, path: str) -> bool:
        """
        Clean up specific directory.

        Args:
            path: Path to directory

        Returns:
            True if cleaned up successfully
        """
        if path not in self._temp_directories:
            return False

        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                logger.debug(f"Cleaned up temp directory: {path}")

            self._temp_directories.discard(path)
            return True

        except Exception as exc:
            logger.warning(f"Failed to cleanup temp directory {path}: {exc}")
            return False

    def cleanup_all(self) -> None:
        """Clean up all tracked resources."""
        if self._cleaned_up:
            return

        logger.info("ResourceManager cleanup starting")

        # Cleanup files
        files_cleaned = 0
        for path in list(self._temp_files):
            if self.cleanup_file(path):
                files_cleaned += 1

        # Cleanup directories
        dirs_cleaned = 0
        for path in list(self._temp_directories):
            if self.cleanup_directory(path):
                dirs_cleaned += 1

        logger.info(
            f"ResourceManager cleanup complete: "
            f"{files_cleaned} files, {dirs_cleaned} directories"
        )

        self._cleaned_up = True

    def get_statistics(self) -> dict:
        """
        Get resource statistics.

        Returns:
            Dictionary with resource counts
        """
        return {
            "temp_files": len(self._temp_files),
            "temp_directories": len(self._temp_directories),
            "cleaned_up": self._cleaned_up,
        }

    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup_all()


class TempFileContext:
    """
    Context manager for temporary file.

    Example:
        with TempFileContext(suffix='.html') as temp_file:
            # Use temp_file path
            with open(temp_file, 'w') as f:
                f.write('<html>...</html>')
        # Temp file automatically cleaned up
    """

    def __init__(
        self,
        suffix: str = "",
        prefix: str = "asciidoc_artisan_",
        dir: Optional[str] = None,
        text: bool = True,
    ):
        """
        Initialize temp file context.

        Args:
            suffix: File suffix
            prefix: File prefix
            dir: Directory
            text: Text mode flag
        """
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.text = text
        self.path: Optional[str] = None
        self.rm = ResourceManager.get_instance()

    def __enter__(self) -> str:
        """
        Create temp file.

        Returns:
            Path to temp file
        """
        self.path = self.rm.create_temp_file(
            suffix=self.suffix, prefix=self.prefix, dir=self.dir, text=self.text
        )
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temp file."""
        if self.path:
            self.rm.cleanup_file(self.path)
        return False


class TempDirectoryContext:
    """
    Context manager for temporary directory.

    Example:
        with TempDirectoryContext() as temp_dir:
            # Use temp_dir path
            file_path = os.path.join(temp_dir, 'output.html')
            with open(file_path, 'w') as f:
                f.write('<html>...</html>')
        # Temp directory automatically cleaned up
    """

    def __init__(
        self,
        suffix: str = "",
        prefix: str = "asciidoc_artisan_",
        dir: Optional[str] = None,
    ):
        """
        Initialize temp directory context.

        Args:
            suffix: Directory suffix
            prefix: Directory prefix
            dir: Parent directory
        """
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.path: Optional[str] = None
        self.rm = ResourceManager.get_instance()

    def __enter__(self) -> str:
        """
        Create temp directory.

        Returns:
            Path to temp directory
        """
        self.path = self.rm.create_temp_directory(
            suffix=self.suffix, prefix=self.prefix, dir=self.dir
        )
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temp directory."""
        if self.path:
            self.rm.cleanup_directory(self.path)
        return False
