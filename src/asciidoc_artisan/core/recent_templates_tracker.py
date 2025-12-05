"""
Recent Templates Tracker - Manages recently used templates list.

Extracted from TemplateManager to reduce class size (MA principle).
Handles tracking, persisting, and retrieving recently used templates.
v2.1.0: Uses TOON format for storage.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from . import toon_utils

if TYPE_CHECKING:
    from asciidoc_artisan.core.models import Template

logger = logging.getLogger(__name__)


class RecentTemplatesTracker:
    """
    Tracks recently used templates (TOON format).

    Extracted from TemplateManager per MA principle (~70 lines).

    Features:
    - Most recent template first in list
    - Limited to max_recent items (default: 10)
    - Persisted to disk as TOON
    - Thread-safe list operations

    Example:
        tracker = RecentTemplatesTracker(storage_dir=custom_dir)
        tracker.add("Technical Article")
        recent = tracker.get_names()  # ["Technical Article"]
    """

    def __init__(self, storage_dir: Path, max_recent: int = 10) -> None:
        """
        Initialize recent templates tracker.

        Args:
            storage_dir: Directory to store recent.toon
            max_recent: Maximum number of recent templates to track
        """
        self.storage_dir = storage_dir
        self.max_recent = max_recent
        self.recent: list[str] = []
        self._recent_file = self.storage_dir / "recent.toon"
        self._legacy_file = self.storage_dir / "recent.json"
        self._load()

    def _migrate_legacy_json(self) -> list[str] | None:
        """Migrate legacy JSON to TOON format."""
        if not self._legacy_file.exists():
            return None

        try:
            import json

            with open(self._legacy_file) as f:
                data = json.load(f)

            # Save as TOON
            with open(self._recent_file, "w") as f:
                toon_utils.dump({"recent": data}, f)

            # Backup legacy file
            backup_path = self._legacy_file.with_suffix(".json.bak")
            self._legacy_file.rename(backup_path)
            logger.info(f"Migrated recent templates: {self._legacy_file} → {self._recent_file}")

            return data
        except Exception as e:
            logger.warning(f"Failed to migrate legacy recent templates: {e}")
            return None

    def _load(self) -> None:
        """Load recent templates list from disk (TOON format)."""
        if self._recent_file.exists():
            try:
                with open(self._recent_file) as f:
                    data = toon_utils.load(f)
                    # Handle both old format (list) and new format (dict)
                    if isinstance(data, list):
                        self.recent = data
                    elif isinstance(data, dict) and "recent" in data:
                        self.recent = data["recent"]
                    else:
                        self.recent = []
            except Exception:
                self.recent = []
        elif self._legacy_file.exists():
            # Migrate legacy JSON
            migrated = self._migrate_legacy_json()
            self.recent = migrated if migrated else []
        else:
            self.recent = []

    def _save(self) -> None:
        """Save recent templates list to disk (TOON format)."""
        try:
            with open(self._recent_file, "w") as f:
                toon_utils.dump({"recent": self.recent}, f)
        except Exception as e:
            logger.error(f"Failed to save recent templates: {e}")

    def add(self, template_name: str) -> None:
        """
        Add template to recent list.

        Most recent template is first in list. List is limited to
        max_recent items.

        Args:
            template_name: Name of template
        """
        # Remove if already in list
        if template_name in self.recent:
            self.recent.remove(template_name)

        # Add to front
        self.recent.insert(0, template_name)

        # Limit size
        self.recent = self.recent[: self.max_recent]

        # Persist to disk
        self._save()

    def remove(self, template_name: str) -> None:
        """
        Remove template from recent list.

        Args:
            template_name: Name of template to remove
        """
        if template_name in self.recent:
            self.recent.remove(template_name)
            self._save()

    def get_names(self) -> list[str]:
        """
        Get list of recent template names.

        Returns:
            List of template names in recent order
        """
        return list(self.recent)

    def get_templates(self, templates_dict: dict[str, "Template"]) -> list["Template"]:
        """
        Get recent templates from a templates dictionary.

        Args:
            templates_dict: Dictionary mapping names to Template objects

        Returns:
            List of Template objects in recent order
        """
        templates = []
        for name in self.recent:
            if name in templates_dict:
                templates.append(templates_dict[name])
        return templates

    def clear(self) -> None:
        """Clear all recent templates."""
        self.recent = []
        self._save()
