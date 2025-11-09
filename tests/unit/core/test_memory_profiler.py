"""
Tests for memory profiler.

Tests the MemoryProfiler system that tracks application memory usage
to identify optimization opportunities.
"""

import time

from asciidoc_artisan.core.memory_profiler import (
    MemoryProfiler,
    MemorySnapshot,
    get_profiler,
    profile_memory,
)


def test_profiler_initialization():
    """Test profiler initializes correctly."""
    profiler = MemoryProfiler()

    assert profiler.top_n == 10
    assert not profiler.is_running
    assert len(profiler.snapshots) == 0


def test_profiler_start_stop():
    """Test profiler can start and stop."""
    profiler = MemoryProfiler()

    assert not profiler.is_running

    profiler.start()
    assert profiler.is_running

    profiler.stop()
    assert not profiler.is_running


def test_profiler_start_twice_warning():
    """Test starting profiler twice logs warning."""
    profiler = MemoryProfiler()

    profiler.start()
    profiler.start()  # Should log warning but not fail

    assert profiler.is_running
    profiler.stop()


def test_take_snapshot():
    """Test taking memory snapshot."""
    profiler = MemoryProfiler()
    profiler.start()

    # Allocate some memory to ensure we have allocations to track
    data = [0] * 10000

    snapshot = profiler.take_snapshot("test snapshot")

    assert snapshot is not None
    assert snapshot.current_mb > 0
    assert snapshot.peak_mb >= snapshot.current_mb
    assert snapshot.description == "test snapshot"
    assert len(profiler.snapshots) == 1

    # Keep reference
    assert len(data) == 10000

    profiler.stop()


def test_take_snapshot_without_start():
    """Test taking snapshot without starting profiler."""
    profiler = MemoryProfiler()

    snapshot = profiler.take_snapshot("test")

    assert snapshot is None


def test_multiple_snapshots():
    """Test taking multiple snapshots."""
    profiler = MemoryProfiler()
    profiler.start()

    snap1 = profiler.take_snapshot("first")
    time.sleep(0.01)  # Small delay

    # Allocate some memory
    _ = [0] * 100000  # ~800KB

    snap2 = profiler.take_snapshot("second")

    assert len(profiler.snapshots) == 2
    assert snap2.current_mb >= snap1.current_mb  # Should have grown
    assert snap2.timestamp > snap1.timestamp

    profiler.stop()


def test_get_memory_usage():
    """Test getting memory usage from OS."""
    profiler = MemoryProfiler()

    mem_mb, mem_percent = profiler.get_memory_usage()

    # May be 0.0 if psutil unavailable
    assert isinstance(mem_mb, float)
    assert isinstance(mem_percent, float)
    assert mem_mb >= 0.0
    assert mem_percent >= 0.0


def test_compare_snapshots():
    """Test comparing two snapshots."""
    profiler = MemoryProfiler()
    profiler.start()

    profiler.take_snapshot("first")

    # Allocate memory
    large_list = [0] * 1000000

    profiler.take_snapshot("second")

    # Should not raise error
    profiler.compare_snapshots(0, 1)

    # Keep reference to avoid garbage collection
    assert len(large_list) == 1000000

    profiler.stop()


def test_compare_snapshots_invalid_indices():
    """Test comparing snapshots with invalid indices."""
    profiler = MemoryProfiler()
    profiler.start()

    profiler.take_snapshot("only one")

    # Should not raise error, just log
    profiler.compare_snapshots(0, 5)  # Index 5 doesn't exist
    profiler.compare_snapshots(10, 20)  # Both invalid

    profiler.stop()


def test_get_statistics_empty():
    """Test statistics when no snapshots."""
    profiler = MemoryProfiler()

    stats = profiler.get_statistics()

    assert stats["snapshots_count"] == 0
    assert stats["profiler_running"] is False


def test_get_statistics_with_snapshots():
    """Test statistics with multiple snapshots."""
    profiler = MemoryProfiler()
    profiler.start()

    profiler.take_snapshot("1")
    profiler.take_snapshot("2")
    profiler.take_snapshot("3")

    stats = profiler.get_statistics()

    assert stats["snapshots_count"] == 3
    assert stats["profiler_running"] is True
    assert stats["current_mb"] > 0
    assert stats["peak_mb"] >= stats["min_mb"]
    assert stats["avg_mb"] > 0
    assert "total_growth_mb" in stats

    profiler.stop()


def test_clear_snapshots():
    """Test clearing snapshots."""
    profiler = MemoryProfiler()
    profiler.start()

    profiler.take_snapshot("1")
    profiler.take_snapshot("2")
    assert len(profiler.snapshots) == 2

    profiler.clear_snapshots()
    assert len(profiler.snapshots) == 0

    profiler.stop()


def test_get_snapshot_count():
    """Test getting snapshot count."""
    profiler = MemoryProfiler()
    profiler.start()

    assert profiler.get_snapshot_count() == 0

    profiler.take_snapshot("1")
    assert profiler.get_snapshot_count() == 1

    profiler.take_snapshot("2")
    assert profiler.get_snapshot_count() == 2

    profiler.stop()


def test_get_latest_snapshot():
    """Test getting latest snapshot."""
    profiler = MemoryProfiler()

    assert profiler.get_latest_snapshot() is None

    profiler.start()

    snap1 = profiler.take_snapshot("first")
    assert profiler.get_latest_snapshot() == snap1

    snap2 = profiler.take_snapshot("second")
    assert profiler.get_latest_snapshot() == snap2

    profiler.stop()


def test_global_profiler():
    """Test global profiler instance."""
    prof1 = get_profiler()
    prof2 = get_profiler()

    # Should return same instance
    assert prof1 is prof2


def test_profile_memory_decorator():
    """Test memory profiling decorator."""
    profiler = get_profiler()
    profiler.start()

    initial_count = profiler.get_snapshot_count()

    @profile_memory("test_function")
    def allocate_memory():
        return [0] * 100000

    result = allocate_memory()

    # Should have 2 new snapshots (before and after)
    assert profiler.get_snapshot_count() == initial_count + 2

    # Check snapshot descriptions
    snapshots = profiler.snapshots[-2:]
    assert "before" in snapshots[0].description
    assert "after" in snapshots[1].description

    # Keep reference
    assert len(result) == 100000

    profiler.stop()


def test_profile_memory_decorator_auto_start():
    """Test decorator auto-starts profiler if not running."""
    # Create new profiler instance
    import asciidoc_artisan.core.memory_profiler as mp

    mp._global_profiler = None

    profiler = get_profiler()
    assert not profiler.is_running

    @profile_memory("auto_start_test")
    def dummy():
        return "done"

    result = dummy()

    # Profiler should have auto-started
    assert profiler.is_running
    assert profiler.get_snapshot_count() >= 2

    profiler.stop()


def test_memory_snapshot_str():
    """Test MemorySnapshot string representation."""
    snapshot = MemorySnapshot(
        timestamp=time.time(),
        current_mb=50.5,
        peak_mb=75.3,
        top_allocations=[],
        description="test snapshot",
    )

    s = str(snapshot)
    assert "50.5MB" in s
    assert "75.3MB" in s
    assert "test snapshot" in s


def test_log_top_allocations():
    """Test logging top allocations."""
    profiler = MemoryProfiler()
    profiler.start()

    # Allocate various sizes
    small = [0] * 1000
    medium = [0] * 10000
    large = [0] * 100000

    # Should not raise error
    profiler.log_top_allocations(5)

    # Keep references
    assert len(small) + len(medium) + len(large) > 0

    profiler.stop()


def test_log_top_allocations_without_start():
    """Test logging allocations without starting profiler."""
    profiler = MemoryProfiler()

    # Should not raise error, just log warning
    profiler.log_top_allocations(10)


def test_profiler_memory_growth_detection():
    """Test profiler can detect memory growth."""
    profiler = MemoryProfiler()
    profiler.start()

    snap1 = profiler.take_snapshot("before allocation")
    initial_mb = snap1.current_mb

    # Allocate significant memory
    large_data = [0] * 5000000  # ~40MB

    snap2 = profiler.take_snapshot("after allocation")

    # Should show growth
    assert snap2.current_mb > initial_mb

    stats = profiler.get_statistics()
    assert stats["total_growth_mb"] > 0

    # Keep reference
    assert len(large_data) == 5000000

    profiler.stop()


def test_snapshot_top_allocations():
    """Test snapshot captures top allocations."""
    profiler = MemoryProfiler(top_n=5)
    profiler.start()

    # Allocate memory
    data = [0] * 100000

    snapshot = profiler.take_snapshot("with allocations")

    assert len(snapshot.top_allocations) > 0
    assert len(snapshot.top_allocations) <= 5

    for location, size in snapshot.top_allocations:
        assert isinstance(location, str)
        assert isinstance(size, int)
        assert size > 0

    # Keep reference
    assert len(data) == 100000

    profiler.stop()


def test_profiler_custom_top_n():
    """Test profiler with custom top_n value."""
    profiler = MemoryProfiler(top_n=3)

    assert profiler.top_n == 3

    profiler.start()
    snapshot = profiler.take_snapshot("test")

    # Should have at most 3 allocations
    assert len(snapshot.top_allocations) <= 3

    profiler.stop()


def test_psutil_import_error_handling():
    """Test graceful handling when psutil unavailable."""
    import sys
    from unittest.mock import patch

    # Mock psutil to be unavailable
    with patch.dict(sys.modules, {"psutil": None}):
        # Re-import to trigger ImportError path
        import importlib

        from asciidoc_artisan.core import memory_profiler

        importlib.reload(memory_profiler)

        # Should still work, just with limited functionality
        profiler = memory_profiler.MemoryProfiler()
        mem_mb, mem_percent = profiler.get_memory_usage()

        # Should return 0.0 when psutil unavailable
        assert mem_mb == 0.0
        assert mem_percent == 0.0


def test_psutil_process_init_error():
    """Test handling of psutil Process initialization error."""
    from unittest.mock import patch

    with patch("asciidoc_artisan.core.memory_profiler.PSUTIL_AVAILABLE", True):
        with patch("asciidoc_artisan.core.memory_profiler.psutil") as mock_psutil:
            # Mock Process() to raise exception
            mock_psutil.Process.side_effect = Exception("Test error")

            profiler = MemoryProfiler()

            # Should handle error gracefully
            assert profiler.process is None


def test_main_cli_function(capsys):
    """Test main CLI demonstration function."""
    from asciidoc_artisan.core.memory_profiler import main

    # Run main function
    main()

    captured = capsys.readouterr()

    # Should print expected sections
    assert "Memory Profiler Demo" in captured.out
    assert "1. Taking initial snapshot" in captured.out
    assert "2. Allocating 10MB" in captured.out
    assert "3. Allocating another 5MB" in captured.out
    assert "4. Comparing snapshots" in captured.out
    assert "5. Statistics" in captured.out
    assert "6. Top allocations" in captured.out
    assert "Done!" in captured.out


def test_memory_snapshot_dataclass():
    """Test MemorySnapshot as dataclass."""
    snapshot = MemorySnapshot(
        timestamp=1234567890.0,
        current_mb=100.5,
        peak_mb=150.7,
        top_allocations=[("test.py:10", 1024)],
        description="test",
    )

    assert snapshot.timestamp == 1234567890.0
    assert snapshot.current_mb == 100.5
    assert snapshot.peak_mb == 150.7
    assert len(snapshot.top_allocations) == 1
    assert snapshot.description == "test"


def test_compare_snapshots_edge_cases():
    """Test snapshot comparison edge cases."""
    profiler = MemoryProfiler()
    profiler.start()

    profiler.take_snapshot("snap1")

    # Compare same snapshot
    profiler.compare_snapshots(0, 0)

    # Compare with negative index (should handle gracefully)
    profiler.compare_snapshots(-1, 0)

    profiler.stop()


def test_get_memory_usage_without_psutil():
    """Test get_memory_usage when psutil unavailable."""
    profiler = MemoryProfiler()

    # Mock PSUTIL_AVAILABLE to False
    from unittest.mock import patch

    with patch("asciidoc_artisan.core.memory_profiler.PSUTIL_AVAILABLE", False):
        mem_mb, mem_percent = profiler.get_memory_usage()

        assert mem_mb == 0.0
        assert mem_percent == 0.0


def test_stop_when_not_running():
    """Test stop() when profiler is not running (line 121)."""
    profiler = MemoryProfiler()

    # Not started yet
    assert not profiler.is_running

    # Calling stop should return early
    profiler.stop()

    # Should still not be running
    assert not profiler.is_running


def test_snapshot_without_description():
    """Test take_snapshot() without description uses logger.debug (line 175)."""
    profiler = MemoryProfiler()
    profiler.start()

    # Take snapshot without description
    snapshot = profiler.take_snapshot()  # No description argument

    # Should still create snapshot
    assert snapshot is not None
    assert snapshot.description == ""

    profiler.stop()


def test_snapshot_with_no_traceback():
    """Test take_snapshot() when traceback is None (line 158)."""
    from unittest.mock import MagicMock, patch

    profiler = MemoryProfiler()
    profiler.start()

    # Mock tracemalloc.take_snapshot to return stats with no traceback
    mock_stat = MagicMock()
    mock_stat.size = 1024
    mock_stat.traceback = None  # Force no traceback

    mock_snapshot = MagicMock()
    mock_snapshot.statistics.return_value = [mock_stat]

    with patch("tracemalloc.take_snapshot", return_value=mock_snapshot):
        snapshot = profiler.take_snapshot("test")

        # Should handle missing traceback with "unknown"
        assert snapshot is not None
        # Check top_allocations contains "unknown" location
        if snapshot.top_allocations:
            location, size = snapshot.top_allocations[0]
            assert location == "unknown"

    profiler.stop()


def test_log_top_allocations_with_no_traceback():
    """Test log_top_allocations() when traceback is None (line 220)."""
    from unittest.mock import MagicMock, patch

    profiler = MemoryProfiler()
    profiler.start()

    # Mock tracemalloc.take_snapshot to return stats with no traceback
    mock_stat = MagicMock()
    mock_stat.size = 2048
    mock_stat.traceback = None  # Force no traceback

    mock_snapshot = MagicMock()
    mock_snapshot.statistics.return_value = [mock_stat]

    with patch("tracemalloc.take_snapshot", return_value=mock_snapshot):
        # Should log "unknown" location
        profiler.log_top_allocations(5)

    profiler.stop()


def test_get_memory_usage_exception():
    """Test get_memory_usage() exception handling (lines 195-197)."""
    from unittest.mock import MagicMock, patch

    profiler = MemoryProfiler()

    # Ensure process is set (not None)
    with patch("asciidoc_artisan.core.memory_profiler.PSUTIL_AVAILABLE", True):
        with patch(
            "asciidoc_artisan.core.memory_profiler.psutil.Process"
        ) as mock_process_class:
            # Create a mock process that raises exception
            mock_process = MagicMock()
            mock_process.memory_info.side_effect = Exception("Memory access error")
            mock_process_class.return_value = mock_process

            # Reinitialize profiler with mocked process
            profiler_with_process = MemoryProfiler()

            # This should trigger exception handling
            mem_mb, mem_percent = profiler_with_process.get_memory_usage()

            # Should return safe defaults on exception
            assert mem_mb == 0.0
            assert mem_percent == 0.0
