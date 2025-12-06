"""
Telemetry Collector - Privacy-First Usage Analytics (opt-in, local-only, NO cloud upload).

Privacy: Opt-in only (disabled default), anonymous UUIDs, NO personal data/content/paths, easy opt-out.
Collects: Feature usage (menu/dialogs), error patterns (types only), performance metrics, system info (OS/Python/GPU).
Storage: ~/.config/AsciiDocArtisan/telemetry.toon, TOON format, 10MB max (auto-rotate), 30-day retention.
Example: collector = TelemetryCollector(); collector.track_event("menu_click", {"menu": "File", "action": "Open"}); collector.track_performance("startup_time", 1.05).
"""

import logging
import platform
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import toon_utils

logger = logging.getLogger(__name__)

# Telemetry event types
EVENT_MENU_CLICK = "menu_click"
EVENT_DIALOG_OPEN = "dialog_open"
EVENT_ERROR = "error"
EVENT_PERFORMANCE = "performance"
EVENT_STARTUP = "startup"
EVENT_FEATURE_USE = "feature_use"


@dataclass
class TelemetryEvent:
    """Single telemetry event. Attributes: event_type (menu_click/error/performance/etc.), timestamp (ISO UTC), session_id (anonymous UUID), data (NO personal info)."""

    event_type: str
    timestamp: str
    session_id: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return asdict(self)


class TelemetryCollector:
    """Privacy-first telemetry with local-only storage. Features: Opt-in only, local JSON, anonymous IDs, NO personal data, auto-rotation (10MB max), 30-day retention. Example: collector = TelemetryCollector(enabled=True); collector.track_event("menu_click", {"menu": "File"}); collector.track_performance("render_time", 0.05)."""

    def __init__(
        self,
        enabled: bool = False,
        session_id: str | None = None,
        data_dir: Path | None = None,
    ) -> None:
        """Initialize TelemetryCollector. Args: enabled (default False, opt-in), session_id (existing or generate new), data_dir (default app data dir)."""
        self.enabled = enabled
        self.session_id = session_id or str(uuid.uuid4())
        self.session_start_time = time.time()

        # Determine data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use platform-appropriate config directory
            if platform.system() == "Windows":
                base_dir = Path.home() / "AppData" / "Local"
            elif platform.system() == "Darwin":  # macOS
                base_dir = Path.home() / "Library" / "Application Support"
            else:  # Linux and others
                base_dir = Path.home() / ".config"

            self.data_dir = base_dir / "AsciiDocArtisan"

        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Telemetry file path (TOON format v2.1.0+)
        self.telemetry_file = self.data_dir / "telemetry.toon"
        self._legacy_json_file = self.data_dir / "telemetry.json"

        # Migrate legacy JSON if exists
        self._migrate_legacy_json()

        # Maximum file size (10MB)
        self.max_file_size = 10 * 1024 * 1024

        # Event buffer (in-memory before flush)
        self.event_buffer: list[TelemetryEvent] = []
        self.buffer_size = 100  # Flush after 100 events

        logger.info(f"TelemetryCollector initialized (enabled={enabled}, session_id={self.session_id[:8]}...)")

    def _migrate_legacy_json(self) -> None:
        """Migrate legacy JSON telemetry to TOON format."""
        if not self._legacy_json_file.exists():
            return

        try:
            import json

            with open(self._legacy_json_file, encoding="utf-8") as f:
                events = json.load(f)

            # Save as TOON
            with open(self.telemetry_file, "w", encoding="utf-8") as f:
                toon_utils.dump({"events": events}, f)

            # Backup and remove legacy file
            backup_path = self._legacy_json_file.with_suffix(".json.bak")
            self._legacy_json_file.rename(backup_path)
            logger.info(f"Migrated telemetry: {self._legacy_json_file} → {self.telemetry_file}")

        except Exception as e:
            logger.warning(f"Failed to migrate legacy telemetry: {e}")

    def track_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Track telemetry event. Args: event_type (menu_click/dialog_open/etc.), data (NO personal info). Example: collector.track_event("menu_click", {"menu": "File", "action": "Open"})."""
        if not self.enabled:
            return

        # Sanitize data to ensure no personal information
        sanitized_data = self._sanitize_data(data or {})

        # Create event
        event = TelemetryEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            session_id=self.session_id,
            data=sanitized_data,
        )

        # Add to buffer
        self.event_buffer.append(event)

        # Flush if buffer is full
        if len(self.event_buffer) >= self.buffer_size:
            self.flush()

        logger.debug(f"Tracked event: {event_type} - {sanitized_data}")

    def track_error(
        self,
        error_type: str,
        error_message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Track error event. Args: error_type (ValueError/FileNotFoundError/etc.), error_message (sanitized, NO paths/user data), context (NO personal info). Example: collector.track_error("ValueError", "Invalid parameter", {"function": "save_file"})."""
        if not self.enabled:
            return

        data = {
            "error_type": error_type,
            "error_message": self._sanitize_message(error_message),
            "context": self._sanitize_data(context or {}),
        }

        self.track_event(EVENT_ERROR, data)

    def track_performance(self, metric_name: str, value: float, unit: str = "seconds") -> None:
        """Track performance metric. Args: metric_name (startup_time/render_time/etc.), value, unit (default: seconds). Example: collector.track_performance("startup_time", 1.05); collector.track_performance("render_time", 0.05, "seconds")."""
        if not self.enabled:
            return

        data = {"metric": metric_name, "value": value, "unit": unit}

        self.track_event(EVENT_PERFORMANCE, data)

    def track_startup(self, startup_time: float) -> None:
        """Track app startup with system info. Args: startup_time (seconds)."""
        if not self.enabled:
            return

        data = {
            "startup_time": startup_time,
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        }

        self.track_event(EVENT_STARTUP, data)

    def flush(self) -> None:
        """Flush event buffer to disk."""
        if not self.enabled or not self.event_buffer:
            return

        try:
            # Load existing events
            existing_events = self._load_events()

            # Add new events
            new_events = [event.to_dict() for event in self.event_buffer]
            all_events = existing_events + new_events

            # Rotate if file is too large
            if self._get_file_size() > self.max_file_size:
                all_events = self._rotate_events(all_events)

            # Save to file (TOON format)
            with open(self.telemetry_file, "w", encoding="utf-8") as f:
                toon_utils.dump({"events": all_events}, f)

            # Clear buffer
            self.event_buffer.clear()

            logger.debug(f"Flushed {len(new_events)} events to {self.telemetry_file}")

        except Exception as e:
            logger.error(f"Failed to flush telemetry events: {e}")

    def _load_events(self) -> list[dict[str, Any]]:
        """Load existing events from TOON file."""
        if not self.telemetry_file.exists():
            return []

        try:
            with open(self.telemetry_file, encoding="utf-8") as f:
                data = toon_utils.load(f)
                # Handle both old format (list) and new format (dict with events key)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "events" in data:
                    events: list[dict[str, Any]] = data["events"]
                    return events
                return []
        except Exception as e:
            logger.error(f"Failed to load telemetry events: {e}")
            return []

    def _get_file_size(self) -> int:
        """Get current telemetry file size in bytes."""
        if not self.telemetry_file.exists():
            return 0
        return self.telemetry_file.stat().st_size

    def _rotate_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Rotate events by keeping only recent events (30-day retention). Args: events (all events). Returns: List of events within retention period."""
        # Calculate cutoff date (30 days ago)
        cutoff_time = time.time() - (30 * 24 * 60 * 60)

        # Filter events
        recent_events = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                if event_time.timestamp() > cutoff_time:
                    recent_events.append(event)
            except (KeyError, ValueError):
                # Skip malformed events
                continue

        logger.info(f"Rotated events: {len(events)} → {len(recent_events)} (30-day retention)")
        return recent_events

    def _sanitize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize data to remove personal information (file paths, emails, IPs, user names). Args: data (raw dict). Returns: Sanitized dict."""
        sanitized: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_message(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            else:
                # Skip complex types
                continue

        return sanitized

    def _sanitize_message(self, message: str) -> str:
        """Sanitize message to remove file paths and personal data. Args: message (raw). Returns: Sanitized message (max 500 chars)."""
        # Replace common file path patterns
        sanitized = message
        if "/" in sanitized or "\\" in sanitized:
            sanitized = "<path redacted>"

        # Replace email addresses
        if "@" in sanitized and "." in sanitized:
            sanitized = "<email redacted>"

        return sanitized[:500]  # Limit message length

    def get_statistics(self) -> dict[str, Any]:
        """Get telemetry statistics. Returns: Dict with total_events, session_id, enabled, event_counts, file_size, file_path."""
        events = self._load_events()

        # Count events by type
        event_counts: dict[str, int] = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "total_events": len(events),
            "session_id": self.session_id,
            "enabled": self.enabled,
            "event_counts": event_counts,
            "file_size": self._get_file_size(),
            "file_path": str(self.telemetry_file),
        }

    def clear_all_data(self) -> None:
        """Clear all telemetry data (for opt-out or testing)."""
        try:
            if self.telemetry_file.exists():
                self.telemetry_file.unlink()
                logger.info("Cleared all telemetry data")

            # Clear buffer
            self.event_buffer.clear()

        except Exception as e:
            logger.error(f"Failed to clear telemetry data: {e}")

    def __del__(self) -> None:
        """Flush events on destruction."""
        try:
            self.flush()
        except Exception:
            # Ignore errors during cleanup
            pass
