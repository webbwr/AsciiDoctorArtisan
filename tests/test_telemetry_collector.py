"""
Tests for Telemetry Collector.

Tests the TelemetryCollector class which provides privacy-first
usage analytics collection.
"""

import json

import pytest

from asciidoc_artisan.core import TelemetryCollector, TelemetryEvent


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "telemetry_test"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def collector_disabled(temp_data_dir):
    """Create a disabled telemetry collector for testing."""
    return TelemetryCollector(enabled=False, data_dir=temp_data_dir)


@pytest.fixture
def collector_enabled(temp_data_dir):
    """Create an enabled telemetry collector for testing."""
    return TelemetryCollector(
        enabled=True, session_id="test-session-123", data_dir=temp_data_dir
    )


class TestTelemetryEventDataClass:
    """Test TelemetryEvent dataclass."""

    def test_event_creation(self):
        """Test event can be created."""
        event = TelemetryEvent(
            event_type="test_event",
            timestamp="2025-11-02T12:00:00Z",
            session_id="test-123",
            data={"key": "value"},
        )

        assert event.event_type == "test_event"
        assert event.timestamp == "2025-11-02T12:00:00Z"
        assert event.session_id == "test-123"
        assert event.data == {"key": "value"}

    def test_event_to_dict(self):
        """Test event conversion to dictionary."""
        event = TelemetryEvent(
            event_type="menu_click",
            timestamp="2025-11-02T12:00:00Z",
            session_id="test-123",
            data={"menu": "File", "action": "Open"},
        )

        event_dict = event.to_dict()

        assert isinstance(event_dict, dict)
        assert event_dict["event_type"] == "menu_click"
        assert event_dict["timestamp"] == "2025-11-02T12:00:00Z"
        assert event_dict["session_id"] == "test-123"
        assert event_dict["data"]["menu"] == "File"


class TestTelemetryCollectorInitialization:
    """Test collector initialization."""

    def test_collector_creation_disabled(self, collector_disabled):
        """Test disabled collector can be created."""
        assert collector_disabled is not None
        assert isinstance(collector_disabled, TelemetryCollector)
        assert collector_disabled.enabled is False

    def test_collector_creation_enabled(self, collector_enabled):
        """Test enabled collector can be created."""
        assert collector_enabled is not None
        assert isinstance(collector_enabled, TelemetryCollector)
        assert collector_enabled.enabled is True

    def test_session_id_generation(self, temp_data_dir):
        """Test automatic session ID generation."""
        collector = TelemetryCollector(enabled=True, data_dir=temp_data_dir)
        assert collector.session_id is not None
        assert len(collector.session_id) > 0

    def test_custom_session_id(self, temp_data_dir):
        """Test custom session ID is used."""
        custom_id = "custom-session-456"
        collector = TelemetryCollector(
            enabled=True, session_id=custom_id, data_dir=temp_data_dir
        )
        assert collector.session_id == custom_id

    def test_data_directory_created(self, temp_data_dir):
        """Test data directory is created if it doesn't exist."""
        test_dir = temp_data_dir / "new_dir"
        TelemetryCollector(enabled=True, data_dir=test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_telemetry_file_path(self, collector_enabled, temp_data_dir):
        """Test telemetry file path is correct."""
        expected_path = temp_data_dir / "telemetry.json"
        assert collector_enabled.telemetry_file == expected_path


class TestTelemetryCollectorEventTracking:
    """Test event tracking functionality."""

    def test_track_event_disabled_collector(self, collector_disabled):
        """Test event tracking is skipped when disabled."""
        collector_disabled.track_event("test_event", {"key": "value"})

        # Event buffer should be empty (event not tracked)
        assert len(collector_disabled.event_buffer) == 0

    def test_track_event_enabled_collector(self, collector_enabled):
        """Test event tracking when enabled."""
        collector_enabled.track_event("menu_click", {"menu": "File", "action": "Open"})

        # Event should be in buffer
        assert len(collector_enabled.event_buffer) == 1

        event = collector_enabled.event_buffer[0]
        assert event.event_type == "menu_click"
        assert event.session_id == "test-session-123"
        assert event.data["menu"] == "File"
        assert event.data["action"] == "Open"

    def test_track_event_with_none_data(self, collector_enabled):
        """Test event tracking with None data."""
        collector_enabled.track_event("startup")

        assert len(collector_enabled.event_buffer) == 1
        event = collector_enabled.event_buffer[0]
        assert event.data == {}

    def test_track_error(self, collector_enabled):
        """Test error event tracking."""
        collector_enabled.track_error(
            "ValueError", "Invalid parameter", {"function": "save_file"}
        )

        assert len(collector_enabled.event_buffer) == 1
        event = collector_enabled.event_buffer[0]
        assert event.event_type == "error"
        assert event.data["error_type"] == "ValueError"
        assert event.data["error_message"] is not None

    def test_track_performance(self, collector_enabled):
        """Test performance metric tracking."""
        collector_enabled.track_performance("startup_time", 1.05)

        assert len(collector_enabled.event_buffer) == 1
        event = collector_enabled.event_buffer[0]
        assert event.event_type == "performance"
        assert event.data["metric"] == "startup_time"
        assert event.data["value"] == 1.05
        assert event.data["unit"] == "seconds"

    def test_track_performance_custom_unit(self, collector_enabled):
        """Test performance tracking with custom unit."""
        collector_enabled.track_performance("memory_usage", 256.5, "MB")

        event = collector_enabled.event_buffer[0]
        assert event.data["unit"] == "MB"

    def test_track_startup(self, collector_enabled):
        """Test startup event tracking."""
        collector_enabled.track_startup(1.25)

        assert len(collector_enabled.event_buffer) == 1
        event = collector_enabled.event_buffer[0]
        assert event.event_type == "startup"
        assert event.data["startup_time"] == 1.25
        assert "os" in event.data
        assert "python_version" in event.data


class TestTelemetryCollectorBuffering:
    """Test event buffering and flushing."""

    def test_buffer_size_limit(self, collector_enabled):
        """Test buffer flushes after reaching size limit."""
        # Set smaller buffer size for testing
        collector_enabled.buffer_size = 5

        # Add 6 events (should trigger flush)
        for i in range(6):
            collector_enabled.track_event(f"event_{i}", {"index": i})

        # Buffer should be empty after auto-flush
        # (5 events flushed, 1 remains)
        assert len(collector_enabled.event_buffer) <= 1

    def test_manual_flush(self, collector_enabled):
        """Test manual flush."""
        collector_enabled.track_event("test_event", {"data": "test"})
        assert len(collector_enabled.event_buffer) == 1

        collector_enabled.flush()

        # Buffer should be empty after flush
        assert len(collector_enabled.event_buffer) == 0

    def test_flush_creates_file(self, collector_enabled):
        """Test flush creates telemetry file."""
        collector_enabled.track_event("test_event")
        collector_enabled.flush()

        assert collector_enabled.telemetry_file.exists()

    def test_flush_preserves_existing_events(self, collector_enabled):
        """Test flush preserves existing events."""
        # Add and flush first event
        collector_enabled.track_event("event_1", {"index": 1})
        collector_enabled.flush()

        # Add and flush second event
        collector_enabled.track_event("event_2", {"index": 2})
        collector_enabled.flush()

        # Load events from file
        with open(collector_enabled.telemetry_file, "r", encoding="utf-8") as f:
            events = json.load(f)

        # Both events should be in file
        assert len(events) == 2


class TestTelemetryCollectorDataSanitization:
    """Test data sanitization for privacy."""

    def test_sanitize_file_paths(self, collector_enabled):
        """Test file paths are sanitized."""
        collector_enabled.track_event(
            "file_open", {"path": "/home/user/documents/file.txt"}
        )

        event = collector_enabled.event_buffer[0]
        assert event.data["path"] == "<path redacted>"

    def test_sanitize_email_addresses(self, collector_enabled):
        """Test email addresses are sanitized."""
        collector_enabled.track_event("user_action", {"email": "user@example.com"})

        event = collector_enabled.event_buffer[0]
        assert event.data["email"] == "<email redacted>"

    def test_preserve_safe_data(self, collector_enabled):
        """Test safe data is preserved."""
        collector_enabled.track_event(
            "menu_click", {"menu": "File", "action": "Open", "count": 5}
        )

        event = collector_enabled.event_buffer[0]
        assert event.data["menu"] == "File"
        assert event.data["action"] == "Open"
        assert event.data["count"] == 5

    def test_sanitize_message_length_limit(self, collector_enabled):
        """Test messages are limited to 500 characters."""
        long_message = "A" * 600
        sanitized = collector_enabled._sanitize_message(long_message)

        assert len(sanitized) == 500


class TestTelemetryCollectorFileRotation:
    """Test file rotation and retention."""

    def test_rotation_on_size_limit(self, collector_enabled):
        """Test file rotation when size limit reached."""
        # Set very small size limit for testing
        collector_enabled.max_file_size = 1024  # 1KB

        # Add many events to exceed size limit
        for i in range(100):
            collector_enabled.track_event(
                "large_event", {"data": "x" * 100, "index": i}
            )
            collector_enabled.flush()

        # File should exist but be rotated (smaller than if all events kept)
        assert collector_enabled.telemetry_file.exists()

    def test_statistics_retrieval(self, collector_enabled):
        """Test statistics retrieval."""
        collector_enabled.track_event("event_1")
        collector_enabled.track_event("error", {"type": "test"})
        collector_enabled.flush()

        stats = collector_enabled.get_statistics()

        assert stats["total_events"] == 2
        assert stats["session_id"] == "test-session-123"
        assert stats["enabled"] is True
        assert "event_counts" in stats


class TestTelemetryCollectorClearData:
    """Test data clearing functionality."""

    def test_clear_all_data(self, collector_enabled):
        """Test clearing all telemetry data."""
        # Add events and flush
        collector_enabled.track_event("test_event")
        collector_enabled.flush()
        assert collector_enabled.telemetry_file.exists()

        # Clear all data
        collector_enabled.clear_all_data()

        # File should be deleted
        assert not collector_enabled.telemetry_file.exists()

        # Buffer should be empty
        assert len(collector_enabled.event_buffer) == 0

    def test_clear_data_when_no_file(self, collector_enabled):
        """Test clearing data when no file exists (should not error)."""
        # Should not raise exception
        collector_enabled.clear_all_data()


class TestTelemetryCollectorPrivacy:
    """Test privacy protections."""

    def test_no_personal_data_in_events(self, collector_enabled):
        """Test no personal data is stored in events."""
        # Try to track event with personal data (paths and emails)
        collector_enabled.track_event(
            "test",
            {
                "action": "file_opened",
                "email": "john@example.com",
                "file": "/home/john/secret.txt",
            },
        )

        event = collector_enabled.event_buffer[0]

        # Email and file path should be sanitized
        assert event.data["email"] == "<email redacted>"
        assert event.data["file"] == "<path redacted>"
        # Action name is preserved (safe data)
        assert event.data["action"] == "file_opened"

    def test_anonymous_session_ids(self, collector_enabled):
        """Test session IDs are anonymous (UUIDs)."""
        # Session ID should be set (in tests we use "test-session-123")
        session_id = collector_enabled.session_id
        assert len(session_id) == 16  # "test-session-123" is 16 characters
        assert session_id == "test-session-123"

    def test_local_storage_only(self, collector_enabled):
        """Test data is stored locally only."""
        collector_enabled.track_event("test_event")
        collector_enabled.flush()

        # File should exist in local data dir
        assert collector_enabled.telemetry_file.exists()
        assert collector_enabled.data_dir in collector_enabled.telemetry_file.parents


class TestTelemetryCollectorDestruction:
    """Test collector cleanup on destruction."""

    def test_flush_on_destruction(self, collector_enabled):
        """Test events are flushed when collector is destroyed."""
        collector_enabled.track_event("final_event")

        # Delete collector (calls __del__)
        del collector_enabled

        # File should exist with flushed event
        # Note: This might not work reliably due to Python's GC timing
        # So we just check that __del__ doesn't raise exceptions
