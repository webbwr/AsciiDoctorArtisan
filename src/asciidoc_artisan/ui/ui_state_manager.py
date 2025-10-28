"""
UI State Manager - Manages UI element state based on application state.

Implements:
- Action enable/disable based on processing state
- AI status bar updates
- Pandoc availability checking
- Git readiness checking

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)

# Check for Pandoc availability
try:
    import pypandoc

    PANDOC_AVAILABLE = True
except ImportError:
    pypandoc = None
    PANDOC_AVAILABLE = False


class UIStateManager:
    """Manages UI state based on application processing state.

    This class encapsulates logic for enabling/disabling UI actions based
    on current processing state (Git, Pandoc), and updating status indicators.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the UIStateManager with a reference to the main editor."""
        self.editor = editor

    def update_ui_state(self) -> None:
        """
        Update UI element states based on current processing state.

        Enables/disables actions based on:
        - Pandoc processing state
        - Git processing state
        - Git repository availability
        - Pandoc availability
        """
        # Save/Save As actions - disabled during Pandoc processing
        is_processing_pandoc = self.editor.file_operations_manager._is_processing_pandoc
        self.editor.action_manager.save_act.setEnabled(not is_processing_pandoc)
        self.editor.action_manager.save_as_act.setEnabled(not is_processing_pandoc)

        # Export actions - disabled during Pandoc processing
        export_enabled = not is_processing_pandoc
        self.editor.action_manager.save_as_adoc_act.setEnabled(export_enabled)
        self.editor.action_manager.save_as_md_act.setEnabled(
            export_enabled and PANDOC_AVAILABLE
        )
        self.editor.action_manager.save_as_docx_act.setEnabled(
            export_enabled and PANDOC_AVAILABLE
        )
        self.editor.action_manager.save_as_html_act.setEnabled(export_enabled)
        self.editor.action_manager.save_as_pdf_act.setEnabled(
            export_enabled and PANDOC_AVAILABLE
        )

        # Git actions - disabled during Git processing or if no repo
        git_ready = (
            bool(self.editor._settings.git_repo_path)
            and not self.editor._is_processing_git
        )
        self.editor.action_manager.git_commit_act.setEnabled(git_ready)
        self.editor.action_manager.git_pull_act.setEnabled(git_ready)
        self.editor.action_manager.git_push_act.setEnabled(git_ready)

        # Convert and paste - requires Pandoc and not processing
        self.editor.action_manager.convert_paste_act.setEnabled(
            PANDOC_AVAILABLE and not is_processing_pandoc
        )

        # Update AI status bar
        self.update_ai_status_bar()

    def update_ai_status_bar(self) -> None:
        """Update AI model name in status bar based on settings."""
        if self.editor._settings.ollama_enabled and self.editor._settings.ollama_model:
            # Show selected Ollama model
            self.editor.status_manager.set_ai_model(self.editor._settings.ollama_model)
        else:
            # Show Pandoc as fallback conversion method
            self.editor.status_manager.set_ai_model("Pandoc")

    def check_pandoc_availability(self, context: str) -> bool:
        """
        Check if Pandoc is available for document conversion.

        Args:
            context: Context string describing the operation requiring Pandoc

        Returns:
            True if Pandoc is available, False otherwise (shows error dialog)
        """
        if not PANDOC_AVAILABLE:
            self.editor.status_manager.show_message(
                "critical",
                "Pandoc Not Available",
                f"{context} requires Pandoc and pypandoc.\n"
                "Please install them first:\n\n"
                "1. Install pandoc from https://pandoc.org\n"
                "2. Run: pip install pypandoc",
            )
            return False
        return True
