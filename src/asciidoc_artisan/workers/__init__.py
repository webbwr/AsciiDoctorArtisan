"""
Workers module - Background thread workers for long-running operations.

This module contains QObject-based worker classes that execute operations
in background QThreads to prevent UI blocking:

- GitWorker: Git version control operations
- PandocWorker: Document format conversion (Pandoc + AI)
- PreviewWorker: AsciiDoc HTML rendering
- LanguageToolWorker: Grammar checking with LanguageTool (v1.3.0+)
- OllamaGrammarWorker: AI-powered grammar/style checking (v1.3.0+)

All workers implement NFR-005: Long-running operations SHALL execute
in background threads to maintain UI responsiveness.

Usage Example:
    ```python
    from asciidoc_artisan.workers import GitWorker, PandocWorker, PreviewWorker
    from asciidoc_artisan.workers import LanguageToolWorker, OllamaGrammarWorker
    from PySide6.QtCore import QThread

    # Create worker and thread
    git_worker = GitWorker()
    git_thread = QThread()
    git_worker.moveToThread(git_thread)
    git_thread.start()

    # Connect signals
    git_worker.command_complete.connect(self._on_git_done)

    # Execute work
    git_worker.run_git_command(["git", "status"], "/path/to/repo")
    ```
"""

from .git_worker import GitWorker
from .language_tool_worker import LanguageToolWorker
from .ollama_grammar_worker import OllamaGrammarWorker
from .pandoc_worker import PandocWorker
from .preview_worker import PreviewWorker

__all__ = [
    "GitWorker",
    "LanguageToolWorker",
    "OllamaGrammarWorker",
    "PandocWorker",
    "PreviewWorker",
]
