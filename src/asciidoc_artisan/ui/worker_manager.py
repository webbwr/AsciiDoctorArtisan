"""
Worker Manager - Handles worker thread initialization and lifecycle.

Implements:
- Git worker thread setup
- Pandoc worker thread setup
- Preview worker thread setup
- Signal/slot connections
- Thread lifecycle management

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread

from asciidoc_artisan.workers import GitWorker, PandocWorker, PreviewWorker

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)

# Check for AsciiDoc3 availability
try:
    from asciidoc3 import asciidoc3

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    asciidoc3 = None
    ASCIIDOC3_AVAILABLE = False


class WorkerManager:
    """Manages worker threads for Git, Pandoc, and Preview operations.

    This class encapsulates all worker thread initialization, signal/slot
    connections, and lifecycle management.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the WorkerManager with a reference to the main editor."""
        self.editor = editor
        self.git_thread: QThread | None = None
        self.git_worker: GitWorker | None = None
        self.pandoc_thread: QThread | None = None
        self.pandoc_worker: PandocWorker | None = None
        self.preview_thread: QThread | None = None
        self.preview_worker: PreviewWorker | None = None

    def setup_workers_and_threads(self) -> None:
        """Set up all worker threads (Git, Pandoc, Preview) with signal connections."""
        logger.info("Setting up worker threads...")

        # Git Worker
        self.git_thread = QThread(self.editor)
        self.git_worker = GitWorker()
        self.git_worker.moveToThread(self.git_thread)
        self.editor.request_git_command.connect(self.git_worker.run_git_command)
        self.git_worker.command_complete.connect(self.editor._handle_git_result)
        self.git_thread.finished.connect(self.git_worker.deleteLater)
        self.git_thread.start()

        # Pandoc Worker
        self.pandoc_thread = QThread(self.editor)
        self.pandoc_worker = PandocWorker()
        self.pandoc_worker.moveToThread(self.pandoc_thread)

        # Initialize Ollama configuration from settings
        self.pandoc_worker.set_ollama_config(
            getattr(self.editor._settings, "ollama_enabled", False),
            getattr(self.editor._settings, "ollama_model", None),
        )

        self.editor.request_pandoc_conversion.connect(
            self.pandoc_worker.run_pandoc_conversion
        )
        self.pandoc_worker.conversion_complete.connect(
            self.editor.pandoc_result_handler.handle_pandoc_result
        )
        self.pandoc_worker.conversion_error.connect(
            self.editor.pandoc_result_handler.handle_pandoc_error_result
        )
        self.pandoc_thread.finished.connect(self.pandoc_worker.deleteLater)
        self.pandoc_thread.start()

        # Preview Worker
        self.preview_thread = QThread(self.editor)
        self.preview_worker = PreviewWorker()
        self.preview_worker.moveToThread(self.preview_thread)

        if ASCIIDOC3_AVAILABLE and asciidoc3:
            self.preview_worker.initialize_asciidoc(asciidoc3.__file__)

        self.editor.request_preview_render.connect(self.preview_worker.render_preview)
        self.preview_worker.render_complete.connect(
            self.editor._handle_preview_complete
        )
        self.preview_worker.render_error.connect(self.editor._handle_preview_error)
        self.preview_thread.finished.connect(self.preview_worker.deleteLater)
        self.preview_thread.start()

        logger.info("All worker threads started (Git, Pandoc, Preview)")

        # Store references on main window for backward compatibility
        self.editor.git_thread = self.git_thread
        self.editor.git_worker = self.git_worker
        self.editor.pandoc_thread = self.pandoc_thread
        self.editor.pandoc_worker = self.pandoc_worker
        self.preview_thread = self.preview_thread
        self.editor.preview_worker = self.preview_worker
