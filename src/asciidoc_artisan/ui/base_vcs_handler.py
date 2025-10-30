"""
Base VCS Handler - Shared functionality for version control handlers.

This module provides the BaseVCSHandler class which implements common patterns
for VCS operation handlers (Git, GitHub, etc.).

Used by:
- GitHandler (Git command operations)
- GitHubHandler (GitHub CLI operations)

Implements:
- Processing state management
- Readiness checks with template method pattern
- UI state updates
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor
    from asciidoc_artisan.ui.settings_manager import SettingsManager
    from asciidoc_artisan.ui.status_manager import StatusManager

logger = logging.getLogger(__name__)


class BaseVCSHandler:
    """
    Base class for version control system handlers.

    Provides common functionality for handlers that perform VCS operations:
    - Processing state management (prevent concurrent operations)
    - Readiness checks (repository + processing state)
    - UI state update delegation

    Subclasses must implement:
    - _check_repository_ready(): Check if repository is configured
    - _get_busy_message(): Get handler-specific busy message
    """

    def __init__(
        self,
        parent_window: "AsciiDocEditor",
        settings_manager: "SettingsManager",
        status_manager: "StatusManager",
    ):
        """
        Initialize base handler.

        Args:
            parent_window: Main window instance
            settings_manager: Settings manager instance
            status_manager: Status manager instance
        """
        self.window = parent_window
        self.settings_manager = settings_manager
        self.status_manager = status_manager

        # Processing state
        self.is_processing = False
        self.last_operation = ""

    def _ensure_ready(self) -> bool:
        """
        Ensure handler is ready for operations (Template Method pattern).

        Checks:
        1. Repository is configured (via _check_repository_ready)
        2. No operation currently in progress

        Returns:
            True if ready, False otherwise

        Note:
            Subclasses should call this before starting any operation.
        """
        # Check repository (subclass-specific)
        if not self._check_repository_ready():
            return False

        # Check if already processing
        if self.is_processing:
            self.status_manager.show_message(
                "warning", "Busy", self._get_busy_message()
            )
            return False

        return True

    def _check_repository_ready(self) -> bool:
        """
        Check if repository is configured and ready.

        Subclasses must implement this to provide handler-specific
        repository validation logic.

        Returns:
            True if repository ready, False otherwise

        Note:
            Should show appropriate error message to user if not ready.
        """
        raise NotImplementedError("Subclass must implement _check_repository_ready()")

    def _get_busy_message(self) -> str:
        """
        Get handler-specific busy message.

        Returns:
            Message to show when operation already in progress
        """
        raise NotImplementedError("Subclass must implement _get_busy_message()")

    def _update_ui_state(self) -> None:
        """
        Update UI state (delegate to main window).

        Triggers main window's UI state update to reflect current
        processing state (enable/disable menu items, etc.).
        """
        if hasattr(self.window, "_update_ui_state"):
            self.window._update_ui_state()

    def _start_operation(self, operation_name: str) -> None:
        """
        Mark operation as started.

        Args:
            operation_name: Name of operation for logging/tracking
        """
        self.is_processing = True
        self.last_operation = operation_name
        self._update_ui_state()
        logger.info(f"{self.__class__.__name__}: Started {operation_name}")

    def _complete_operation(self, success: bool = True) -> None:
        """
        Mark operation as completed.

        Args:
            success: Whether operation succeeded
        """
        logger.info(
            f"{self.__class__.__name__}: Completed {self.last_operation} "
            f"(success={success})"
        )
        self.is_processing = False
        self._update_ui_state()
