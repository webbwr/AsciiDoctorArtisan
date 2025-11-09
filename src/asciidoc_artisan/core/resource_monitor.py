"""
Resource Monitor - Track system resources and document metrics.

This module provides real-time monitoring of system resources (memory, CPU)
and document characteristics (size, complexity) to enable adaptive performance
optimizations like dynamic debouncing intervals.

Phase 4 Enhancement (v1.1.0-beta):
- Memory usage tracking via psutil
- Document size and line count metrics
- Adaptive debouncing calculation based on document complexity
- Performance recommendations for large documents
"""

import logging
import platform
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import psutil for system monitoring
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system monitoring disabled")


@dataclass
class ResourceMetrics:
    """System resource metrics snapshot."""

    memory_used_mb: float
    memory_percent: float
    cpu_percent: float
    document_size_bytes: int
    document_line_count: int
    recommended_debounce_ms: int


@dataclass
class DocumentMetrics:
    """Document-specific metrics for performance optimization."""

    size_bytes: int
    line_count: int
    char_count: int
    is_large: bool  # True if document exceeds large document threshold


class ResourceMonitor:
    """
    Monitor system resources and document metrics.

    This class tracks:
    - Memory usage (via psutil if available)
    - CPU usage (via psutil if available)
    - Document size and complexity
    - Calculates adaptive debouncing intervals

    Usage:
        monitor = ResourceMonitor()
        metrics = monitor.get_metrics(document_text)
        debounce_ms = metrics.recommended_debounce_ms
    """

    # Thresholds for document classification
    SMALL_DOC_BYTES = 10_000  # 10 KB
    MEDIUM_DOC_BYTES = 100_000  # 100 KB
    LARGE_DOC_BYTES = 500_000  # 500 KB
    SMALL_DOC_LINES = 100
    MEDIUM_DOC_LINES = 1000
    LARGE_DOC_LINES = 5000

    # Debounce intervals (milliseconds)
    MIN_DEBOUNCE_MS = 50  # Fast response for small docs (was 200ms)
    NORMAL_DEBOUNCE_MS = 150  # Default - faster (was 350ms)
    MEDIUM_DEBOUNCE_MS = 300  # For medium docs (was 500ms)
    LARGE_DEBOUNCE_MS = 500  # For large docs (was 750ms)
    HUGE_DEBOUNCE_MS = 750  # For very large docs (was 1000ms)

    def __init__(self) -> None:
        """Initialize the resource monitor."""
        self.process: Optional["psutil.Process"] = None
        if PSUTIL_AVAILABLE:
            try:
                self.process = psutil.Process()
            except Exception as e:
                logger.warning(f"Failed to initialize psutil process: {e}")

    def get_document_metrics(self, text: str) -> DocumentMetrics:
        """
        Calculate document-specific metrics.

        Args:
            text: Document content

        Returns:
            DocumentMetrics with size, line count, and classification
        """
        size_bytes = len(text.encode("utf-8"))
        line_count = text.count("\n") + 1
        char_count = len(text)

        # Classify as large if it exceeds either threshold
        is_large = (
            size_bytes > self.LARGE_DOC_BYTES or line_count > self.LARGE_DOC_LINES
        )

        return DocumentMetrics(
            size_bytes=size_bytes,
            line_count=line_count,
            char_count=char_count,
            is_large=is_large,
        )

    def calculate_debounce_interval(self, text: str) -> int:
        """
        Calculate adaptive debounce interval based on document size.

        Strategy:
        - Small documents (<10KB, <100 lines): 200ms (fast response)
        - Normal documents (<100KB, <1000 lines): 350ms (current default)
        - Medium documents (<500KB, <5000 lines): 500ms
        - Large documents (>500KB, >5000 lines): 750-1000ms

        Args:
            text: Current document content

        Returns:
            Recommended debounce interval in milliseconds
        """
        doc_metrics = self.get_document_metrics(text)

        # Small document - fast response
        if (
            doc_metrics.size_bytes < self.SMALL_DOC_BYTES
            and doc_metrics.line_count < self.SMALL_DOC_LINES
        ):
            return self.MIN_DEBOUNCE_MS

        # Medium document
        if (
            doc_metrics.size_bytes < self.MEDIUM_DOC_BYTES
            and doc_metrics.line_count < self.MEDIUM_DOC_LINES
        ):
            return self.NORMAL_DEBOUNCE_MS

        # Large document
        if (
            doc_metrics.size_bytes < self.LARGE_DOC_BYTES
            and doc_metrics.line_count < self.LARGE_DOC_LINES
        ):
            return self.MEDIUM_DEBOUNCE_MS

        # Very large document - use longest debounce
        if (
            doc_metrics.size_bytes >= self.LARGE_DOC_BYTES * 2
            or doc_metrics.line_count >= self.LARGE_DOC_LINES * 2
        ):
            return self.HUGE_DEBOUNCE_MS

        # Default for large documents
        return self.LARGE_DEBOUNCE_MS

    def get_memory_usage(self) -> tuple[float, float]:
        """
        Get current memory usage.

        Returns:
            Tuple of (memory_mb, memory_percent)
            Returns (0.0, 0.0) if psutil unavailable
        """
        if not PSUTIL_AVAILABLE or self.process is None:
            return (0.0, 0.0)

        try:
            mem_info = self.process.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)  # Convert bytes to MB
            mem_percent = self.process.memory_percent()
            return (mem_mb, mem_percent)
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return (0.0, 0.0)

    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage.

        Returns:
            CPU usage percentage (0-100)
            Returns 0.0 if psutil unavailable
        """
        if not PSUTIL_AVAILABLE or self.process is None:
            return 0.0

        try:
            # First call initializes the measurement
            # Second call (with interval) gives actual reading
            return self.process.cpu_percent(interval=0.1)  # type: ignore[no-any-return]  # psutil returns float but typed as Any
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {e}")
            return 0.0

    def get_metrics(self, text: str) -> ResourceMetrics:
        """
        Get comprehensive resource and document metrics.

        Args:
            text: Current document content

        Returns:
            ResourceMetrics with system and document statistics
        """
        doc_metrics = self.get_document_metrics(text)
        memory_mb, memory_percent = self.get_memory_usage()
        cpu_percent = self.get_cpu_usage()
        debounce_ms = self.calculate_debounce_interval(text)

        return ResourceMetrics(
            memory_used_mb=memory_mb,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            document_size_bytes=doc_metrics.size_bytes,
            document_line_count=doc_metrics.line_count,
            recommended_debounce_ms=debounce_ms,
        )

    def is_available(self) -> bool:
        """
        Check if system monitoring is available.

        Returns:
            True if psutil is available and initialized
        """
        return PSUTIL_AVAILABLE and self.process is not None

    def get_platform_info(self) -> dict[str, str]:
        """
        Get platform information for diagnostics.

        Returns:
            Dictionary with platform details
        """
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "psutil_available": str(PSUTIL_AVAILABLE),
        }
