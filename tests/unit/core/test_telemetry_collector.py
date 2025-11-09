"""
Tests for core.telemetry_collector module.

Tests privacy-first telemetry collection including:
- TelemetryEvent dataclass
- TelemetryCollector initialization and configuration
- Event tracking (track_event, track_error, track_performance, track_startup)
- Event buffering and flushing
- Privacy sanitization (PII removal)
- File rotation and retention (30 days)
- Statistics collection
- Data clearing (opt-out)
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from asciidoc_artisan.core.telemetry_collector import (
    EVENT_DIALOG_OPEN,
    EVENT_ERROR,
    EVENT_FEATURE_USE,
    EVENT_MENU_CLICK,
    EVENT_PERFORMANCE,
    EVENT_STARTUP,
    TelemetryCollector,
    TelemetryEvent,
)


class TestTelemetryEvent:
    """Test TelemetryEvent dataclass."""

    def test_event_creation(self):
        """Test creating a telemetry event."""
        event = TelemetryEvent(
            event_type="test_event",
            timestamp="2025-01-01T00:00:00Z",
            session_id="test-session-123",
            data={"key": "value"},
        )

        assert event.event_type == "test_event"
        assert event.timestamp == "2025-01-01T00:00:00Z"
        assert event.session_id == "test-session-123"
        assert event.data == {"key": "value"}

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = TelemetryEvent(
            event_type="test_event",
            timestamp="2025-01-01T00:00:00Z",
            session_id="test-session-123",
            data={"key": "value"},
        )

        event_dict = event.to_dict()

        assert event_dict["event_type"] == "test_event"
        assert event_dict["timestamp"] == "2025-01-01T00:00:00Z"
        assert event_dict["session_id"] == "test-session-123"
        assert event_dict["data"] == {"key": "value"}

    def test_event_default_data(self):
        """Test event with default empty data."""
        event = TelemetryEvent(
            event_type="test_event",
            timestamp="2025-01-01T00:00:00Z",
            session_id="test-session-123",
        )

        assert event.data == {}


class TestTelemetryCollectorInitialization:
    """Test TelemetryCollector initialization."""

    def test_initialization_disabled_by_default(self, tmp_path):
        """Test collector is disabled by default (opt-in)."""
        collector = TelemetryCollector(data_dir=tmp_path)

        assert collector.enabled is False

    def test_initialization_enabled(self, tmp_path):
        """Test collector can be enabled."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        assert collector.enabled is True

    def test_initialization_generates_session_id(self, tmp_path):
        """Test collector generates unique session ID."""
        collector = TelemetryCollector(data_dir=tmp_path)

        assert collector.session_id is not None
        assert len(collector.session_id) > 0

    def test_initialization_uses_provided_session_id(self, tmp_path):
        """Test collector uses provided session ID."""
        session_id = "test-session-123"
        collector = TelemetryCollector(session_id=session_id, data_dir=tmp_path)

        assert collector.session_id == session_id

    def test_initialization_creates_data_directory(self, tmp_path):
        """Test collector creates data directory."""
        data_dir = tmp_path / "telemetry"
        collector = TelemetryCollector(data_dir=data_dir)

        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_initialization_sets_telemetry_file_path(self, tmp_path):
        """Test collector sets telemetry file path."""
        collector = TelemetryCollector(data_dir=tmp_path)

        assert collector.telemetry_file == tmp_path / "telemetry.json"

    def test_initialization_sets_session_start_time(self, tmp_path):
        """Test collector sets session start time."""
        before = time.time()
        collector = TelemetryCollector(data_dir=tmp_path)
        after = time.time()

        assert before <= collector.session_start_time <= after

    def test_initialization_default_data_dir_linux(self, tmp_path):
        """Test default data directory on Linux."""
        with patch("platform.system", return_value="Linux"):
            collector = TelemetryCollector()

            expected_dir = Path.home() / ".config" / "AsciiDocArtisan"
            assert collector.data_dir == expected_dir


class TestEventTracking:
    """Test event tracking methods."""

    def test_track_event_when_disabled(self, tmp_path):
        """Test track_event does nothing when disabled."""
        collector = TelemetryCollector(enabled=False, data_dir=tmp_path)

        collector.track_event("test_event", {"key": "value"})

        assert len(collector.event_buffer) == 0

    def test_track_event_when_enabled(self, tmp_path):
        """Test track_event adds event to buffer when enabled."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_event("test_event", {"key": "value"})

        assert len(collector.event_buffer) == 1
        assert collector.event_buffer[0].event_type == "test_event"

    def test_track_event_with_no_data(self, tmp_path):
        """Test track_event works with no data parameter."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_event("test_event")

        assert len(collector.event_buffer) == 1
        assert collector.event_buffer[0].data == {}

    def test_track_event_creates_timestamp(self, tmp_path):
        """Test track_event creates UTC timestamp."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_event("test_event")

        event = collector.event_buffer[0]
        assert event.timestamp.endswith("Z")
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))

    def test_track_event_includes_session_id(self, tmp_path):
        """Test track_event includes session ID."""
        session_id = "test-session-123"
        collector = TelemetryCollector(
            enabled=True, session_id=session_id, data_dir=tmp_path
        )

        collector.track_event("test_event")

        assert collector.event_buffer[0].session_id == session_id

    def test_track_event_sanitizes_data(self, tmp_path):
        """Test track_event sanitizes data to remove PII."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_event("test_event", {"path": "/home/user/file.txt"})

        # Path should be redacted
        event_data = collector.event_buffer[0].data
        assert event_data["path"] == "<path redacted>"

    def test_track_error_when_disabled(self, tmp_path):
        """Test track_error does nothing when disabled."""
        collector = TelemetryCollector(enabled=False, data_dir=tmp_path)

        collector.track_error("ValueError", "Invalid parameter")

        assert len(collector.event_buffer) == 0

    def test_track_error_when_enabled(self, tmp_path):
        """Test track_error adds error event when enabled."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_error("ValueError", "Invalid parameter", {"function": "save"})

        assert len(collector.event_buffer) == 1
        event = collector.event_buffer[0]
        assert event.event_type == EVENT_ERROR
        assert event.data["error_type"] == "ValueError"
        assert event.data["error_message"] == "Invalid parameter"
        assert event.data["context"]["function"] == "save"

    def test_track_performance_when_disabled(self, tmp_path):
        """Test track_performance does nothing when disabled."""
        collector = TelemetryCollector(enabled=False, data_dir=tmp_path)

        collector.track_performance("startup_time", 1.05)

        assert len(collector.event_buffer) == 0

    def test_track_performance_when_enabled(self, tmp_path):
        """Test track_performance adds performance event when enabled."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_performance("startup_time", 1.05)

        assert len(collector.event_buffer) == 1
        event = collector.event_buffer[0]
        assert event.event_type == EVENT_PERFORMANCE
        assert event.data["metric"] == "startup_time"
        assert event.data["value"] == 1.05
        assert event.data["unit"] == "seconds"

    def test_track_performance_custom_unit(self, tmp_path):
        """Test track_performance with custom unit."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_performance("memory_usage", 128, "MB")

        event = collector.event_buffer[0]
        assert event.data["unit"] == "MB"

    def test_track_startup_when_disabled(self, tmp_path):
        """Test track_startup does nothing when disabled."""
        collector = TelemetryCollector(enabled=False, data_dir=tmp_path)

        collector.track_startup(1.05)

        assert len(collector.event_buffer) == 0

    def test_track_startup_when_enabled(self, tmp_path):
        """Test track_startup adds startup event when enabled."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.track_startup(1.05)

        assert len(collector.event_buffer) == 1
        event = collector.event_buffer[0]
        assert event.event_type == EVENT_STARTUP
        assert event.data["startup_time"] == 1.05
        assert "os" in event.data
        assert "python_version" in event.data


class TestEventBufferFlush:
    """Test event buffer and flushing."""

    def test_flush_when_disabled(self, tmp_path):
        """Test flush does nothing when disabled."""
        collector = TelemetryCollector(enabled=False, data_dir=tmp_path)
        collector.event_buffer.append(
            TelemetryEvent(
                event_type="test",
                timestamp="2025-01-01T00:00:00Z",
                session_id="test",
            )
        )

        collector.flush()

        assert not collector.telemetry_file.exists()

    def test_flush_writes_events_to_file(self, tmp_path):
        """Test flush writes events to JSON file."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test_event", {"key": "value"})

        collector.flush()

        assert collector.telemetry_file.exists()
        with open(collector.telemetry_file) as f:
            events = json.load(f)
        assert len(events) == 1
        assert events[0]["event_type"] == "test_event"

    def test_flush_clears_buffer(self, tmp_path):
        """Test flush clears event buffer."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test_event")

        collector.flush()

        assert len(collector.event_buffer) == 0

    def test_flush_appends_to_existing_file(self, tmp_path):
        """Test flush appends to existing events."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        # First flush
        collector.track_event("event1")
        collector.flush()

        # Second flush
        collector.track_event("event2")
        collector.flush()

        with open(collector.telemetry_file) as f:
            events = json.load(f)
        assert len(events) == 2

    def test_flush_auto_triggers_at_buffer_size(self, tmp_path):
        """Test flush automatically triggers when buffer is full."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.buffer_size = 5  # Small buffer for testing

        # Add events to fill buffer
        for i in range(5):
            collector.track_event(f"event{i}")

        # Buffer should be flushed automatically
        assert len(collector.event_buffer) == 0
        assert collector.telemetry_file.exists()

    def test_flush_with_empty_buffer(self, tmp_path):
        """Test flush with empty buffer does nothing."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        collector.flush()

        assert not collector.telemetry_file.exists()


class TestPrivacySanitization:
    """Test privacy sanitization methods."""

    def test_sanitize_data_preserves_basic_types(self, tmp_path):
        """Test sanitize_data preserves int/float/bool."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_data(
            {"count": 5, "ratio": 0.5, "enabled": True}
        )

        assert sanitized["count"] == 5
        assert sanitized["ratio"] == 0.5
        assert sanitized["enabled"] is True

    def test_sanitize_data_redacts_file_paths(self, tmp_path):
        """Test sanitize_data redacts file paths."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_data({"path": "/home/user/document.adoc"})

        assert sanitized["path"] == "<path redacted>"

    def test_sanitize_data_redacts_windows_paths(self, tmp_path):
        """Test sanitize_data redacts Windows paths."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_data({"path": "C:\\Users\\user\\file.txt"})

        assert sanitized["path"] == "<path redacted>"

    def test_sanitize_data_redacts_email_addresses(self, tmp_path):
        """Test sanitize_data redacts email addresses."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_data({"email": "user@example.com"})

        assert sanitized["email"] == "<email redacted>"

    def test_sanitize_data_recursively_sanitizes_nested_dicts(self, tmp_path):
        """Test sanitize_data works recursively."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_data(
            {"outer": {"inner": {"path": "/home/user/file.txt"}}}
        )

        assert sanitized["outer"]["inner"]["path"] == "<path redacted>"

    def test_sanitize_data_skips_complex_types(self, tmp_path):
        """Test sanitize_data skips complex types (lists, objects)."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_data({"list": [1, 2, 3], "object": Mock()})

        assert "list" not in sanitized
        assert "object" not in sanitized

    def test_sanitize_message_limits_length(self, tmp_path):
        """Test sanitize_message limits message to 500 chars."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        long_message = "A" * 1000
        sanitized = collector._sanitize_message(long_message)

        assert len(sanitized) == 500

    def test_sanitize_message_redacts_paths(self, tmp_path):
        """Test sanitize_message redacts file paths."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_message("Error in /home/user/file.txt")

        assert sanitized == "<path redacted>"

    def test_sanitize_message_redacts_emails(self, tmp_path):
        """Test sanitize_message redacts email addresses."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        sanitized = collector._sanitize_message("Contact user@example.com")

        assert sanitized == "<email redacted>"


class TestFileRotation:
    """Test file rotation and retention."""

    def test_rotate_events_keeps_recent_events(self, tmp_path):
        """Test rotate_events keeps events within 30 days."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        # Create recent event (today)
        recent_timestamp = datetime.utcnow().isoformat() + "Z"
        events = [
            {
                "event_type": "recent",
                "timestamp": recent_timestamp,
                "session_id": "test",
                "data": {},
            }
        ]

        rotated = collector._rotate_events(events)

        assert len(rotated) == 1

    def test_rotate_events_removes_old_events(self, tmp_path):
        """Test rotate_events removes events older than 30 days."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        # Create old event (31 days ago)
        old_date = datetime.utcnow() - timedelta(days=31)
        old_timestamp = old_date.isoformat() + "Z"
        events = [
            {
                "event_type": "old",
                "timestamp": old_timestamp,
                "session_id": "test",
                "data": {},
            }
        ]

        rotated = collector._rotate_events(events)

        assert len(rotated) == 0

    def test_rotate_events_skips_malformed_events(self, tmp_path):
        """Test rotate_events skips events with invalid timestamps."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        events = [
            {"event_type": "malformed", "timestamp": "invalid", "session_id": "test"}
        ]

        rotated = collector._rotate_events(events)

        assert len(rotated) == 0

    def test_get_file_size_returns_zero_for_nonexistent_file(self, tmp_path):
        """Test get_file_size returns 0 for nonexistent file."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        size = collector._get_file_size()

        assert size == 0

    def test_get_file_size_returns_actual_size(self, tmp_path):
        """Test get_file_size returns actual file size."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test_event", {"key": "value"})
        collector.flush()

        size = collector._get_file_size()

        assert size > 0


class TestStatistics:
    """Test statistics collection."""

    def test_get_statistics_returns_totals(self, tmp_path):
        """Test get_statistics returns total event count."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("event1")
        collector.track_event("event2")
        collector.flush()

        stats = collector.get_statistics()

        assert stats["total_events"] == 2

    def test_get_statistics_returns_event_counts_by_type(self, tmp_path):
        """Test get_statistics returns counts by event type."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event(EVENT_MENU_CLICK)
        collector.track_event(EVENT_MENU_CLICK)
        collector.track_event(EVENT_DIALOG_OPEN)
        collector.flush()

        stats = collector.get_statistics()

        assert stats["event_counts"][EVENT_MENU_CLICK] == 2
        assert stats["event_counts"][EVENT_DIALOG_OPEN] == 1

    def test_get_statistics_includes_session_id(self, tmp_path):
        """Test get_statistics includes session ID."""
        session_id = "test-session-123"
        collector = TelemetryCollector(
            enabled=True, session_id=session_id, data_dir=tmp_path
        )

        stats = collector.get_statistics()

        assert stats["session_id"] == session_id

    def test_get_statistics_includes_enabled_state(self, tmp_path):
        """Test get_statistics includes enabled state."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        stats = collector.get_statistics()

        assert stats["enabled"] is True

    def test_get_statistics_includes_file_info(self, tmp_path):
        """Test get_statistics includes file path and size."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test")
        collector.flush()

        stats = collector.get_statistics()

        assert stats["file_size"] > 0
        assert "telemetry.json" in stats["file_path"]


class TestDataClearing:
    """Test data clearing (opt-out)."""

    def test_clear_all_data_deletes_file(self, tmp_path):
        """Test clear_all_data deletes telemetry file."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test")
        collector.flush()

        collector.clear_all_data()

        assert not collector.telemetry_file.exists()

    def test_clear_all_data_clears_buffer(self, tmp_path):
        """Test clear_all_data clears event buffer."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test")

        collector.clear_all_data()

        assert len(collector.event_buffer) == 0

    def test_clear_all_data_handles_nonexistent_file(self, tmp_path):
        """Test clear_all_data handles nonexistent file gracefully."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)

        # Should not raise exception
        collector.clear_all_data()

        assert not collector.telemetry_file.exists()


class TestEventConstants:
    """Test event type constants."""

    def test_event_constants_exist(self):
        """Test all event type constants are defined."""
        assert EVENT_MENU_CLICK == "menu_click"
        assert EVENT_DIALOG_OPEN == "dialog_open"
        assert EVENT_ERROR == "error"
        assert EVENT_PERFORMANCE == "performance"
        assert EVENT_STARTUP == "startup"
        assert EVENT_FEATURE_USE == "feature_use"


class TestDestructor:
    """Test destructor behavior."""

    def test_destructor_flushes_events(self, tmp_path):
        """Test destructor flushes remaining events."""
        collector = TelemetryCollector(enabled=True, data_dir=tmp_path)
        collector.track_event("test")

        # Trigger destructor
        del collector

        # Events should be flushed to file
        telemetry_file = tmp_path / "telemetry.json"
        assert telemetry_file.exists()
        with open(telemetry_file) as f:
            events = json.load(f)
        assert len(events) == 1
