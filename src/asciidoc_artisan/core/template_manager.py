"""
Template manager for AsciiDoc Artisan.

Provides template file management with CRUD operations:
- Load templates from directories (built-in + custom)
- Create, read, update, delete templates
- Track recently used templates
"""

import logging
from pathlib import Path

from asciidoc_artisan.core.models import Template
from asciidoc_artisan.core.recent_templates_tracker import RecentTemplatesTracker
from asciidoc_artisan.core.template_engine import TemplateEngine
from asciidoc_artisan.core.template_serializer import (
    sanitize_template_filename,
    serialize_template,
)

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages template files with CRUD operations."""

    def __init__(self, engine: TemplateEngine) -> None:
        """Initialize template manager."""
        self.engine = engine
        self.built_in_dir = self._get_built_in_dir()
        self.custom_dir = self._get_custom_dir()
        self.templates: dict[str, Template] = {}

        self._recent_tracker = RecentTemplatesTracker(self.custom_dir)
        self.max_recent = self._recent_tracker.max_recent
        self._load_templates()

    def _get_built_in_dir(self) -> Path:
        """Get built-in template directory."""
        return Path(__file__).parent.parent / "templates"

    def _get_custom_dir(self) -> Path:
        """Get custom template directory, creating if needed."""
        try:
            from PySide6.QtCore import QStandardPaths

            config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        except ImportError:
            config_dir = str(Path.home() / ".config" / "AsciiDocArtisan")

        custom_dir = Path(config_dir) / "templates"
        custom_dir.mkdir(parents=True, exist_ok=True)
        return custom_dir

    def _load_templates(self) -> None:
        """Load all templates from built-in and custom directories."""
        self.templates = {}

        # Load built-in templates
        if self.built_in_dir.exists():
            for file_path in self.built_in_dir.glob("*.adoc"):
                try:
                    template = self.engine.parse_template(str(file_path))
                    self.templates[template.name] = template
                except Exception as e:
                    logger.error(f"Failed to load built-in template {file_path}: {e}")

        # Load custom templates (override built-in with same name)
        if self.custom_dir.exists():
            for file_path in self.custom_dir.glob("*.adoc"):
                try:
                    template = self.engine.parse_template(str(file_path))
                    self.templates[template.name] = template
                except Exception as e:
                    logger.error(f"Failed to load custom template {file_path}: {e}")

    def reload_templates(self) -> None:
        """Reload all templates from disk."""
        self._load_templates()

    def get_all_templates(self) -> list[Template]:
        """Get all available templates."""
        return list(self.templates.values())

    def get_template(self, name: str) -> Template | None:
        """Get template by name."""
        return self.templates.get(name)

    def get_templates_by_category(self, category: str) -> list[Template]:
        """Get templates in specific category."""
        return [t for t in self.templates.values() if t.category == category]

    def get_categories(self) -> list[str]:
        """Get all template categories."""
        return sorted({t.category for t in self.templates.values()})

    def create_template(self, template: Template, custom: bool = True) -> bool:
        """Create new template file. Returns True if successful."""
        target_dir = self.custom_dir if custom else self.built_in_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = sanitize_template_filename(template.name) + ".adoc"
        file_path = target_dir / filename

        if file_path.exists():
            logger.error(f"Template file already exists: {file_path}")
            return False

        try:
            content = serialize_template(template)
            file_path.write_text(content, encoding="utf-8")
            template.file_path = str(file_path)
            self.templates[template.name] = template
            return True
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False

    def update_template(self, template: Template) -> bool:
        """Update existing template file. Returns True if successful."""
        if not template.file_path or not Path(template.file_path).exists():
            logger.error(f"Template file not found: {template.file_path}")
            return False

        try:
            content = serialize_template(template)
            Path(template.file_path).write_text(content, encoding="utf-8")
            self.templates[template.name] = template
            return True
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            return False

    def delete_template(self, name: str) -> bool:
        """Delete template file. Only custom templates can be deleted."""
        template = self.templates.get(name)
        if not template or not template.file_path:
            return False

        file_path = Path(template.file_path)

        # Only allow deleting custom templates
        if not str(file_path).startswith(str(self.custom_dir)):
            logger.error(f"Cannot delete built-in template: {name}")
            return False

        try:
            file_path.unlink()
            del self.templates[name]
            self._recent_tracker.remove(name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False

    def add_to_recent(self, template_name: str) -> None:
        """Add template to recent list."""
        self._recent_tracker.add(template_name)

    def get_recent_templates(self) -> list[Template]:
        """Get recently used templates (most recent first)."""
        return self._recent_tracker.get_templates(self.templates)

    @property
    def recent(self) -> list[str]:
        """Get recent template names (backward compatibility)."""
        return self._recent_tracker.recent
