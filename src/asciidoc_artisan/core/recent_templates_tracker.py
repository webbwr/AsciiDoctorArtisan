"""
Recent Templates Tracker - Manages recently used templates list.

Extracted from TemplateManager to reduce class size (MA principle).
Handles tracking, persisting, and retrieving recently used templates.
"""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asciidoc_artisan.core.models import Template

logger = logging.getLogger(__name__)


class RecentTemplatesTracker:
    """
    Tracks recently used templates.

    Extracted from TemplateManager per MA principle (~70 lines).

    Features:
    - Most recent template first in list
    - Limited to max_recent items (default: 10)
    - Persisted to disk as JSON
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
            storage_dir: Directory to store recent.json
            max_recent: Maximum number of recent templates to track
        """
        self.storage_dir = storage_dir
        self.max_recent = max_recent
        self.recent: list[str] = []
        self._load()

    def _load(self) -> None:
        """Load recent templates list from disk."""
        recent_file = self.storage_dir / "recent.json"
        if recent_file.exists():
            try:
                with open(recent_file) as f:
                    self.recent = json.load(f)
            except Exception:
                self.recent = []

    def _save(self) -> None:
        """Save recent templates list to disk."""
        recent_file = self.storage_dir / "recent.json"
        try:
            with open(recent_file, "w") as f:
                json.dump(self.recent, f)
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
