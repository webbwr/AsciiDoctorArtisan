"""
Tests for ui.base_vcs_handler module.

Tests base VCS handler functionality including:
- Processing state management
- Readiness checks (template method pattern)
- UI state updates
- Operation lifecycle
"""

import pytest
from unittest.mock import Mock, MagicMock
from asciidoc_artisan.ui.base_vcs_handler import BaseVCSHandler


class ConcreteVCSHandler(BaseVCSHandler):
    """Concrete implementation for testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo_ready = True
        self.busy_message = "Handler is busy"

    def _check_repository_ready(self) -> bool:
        """Mock implementation."""
        return self.repo_ready

    def _get_busy_message(self) -> str:
        """Mock implementation."""
        return self.busy_message


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for BaseVCSHandler."""
    parent_window = Mock()
    parent_window._update_ui_state = Mock()

    settings_manager = Mock()
    status_manager = Mock()
    status_manager.show_message = Mock()

    return parent_window, settings_manager, status_manager


class TestBaseVCSHandlerInitialization:
    """Test BaseVCSHandler initialization."""

    def test_initialization(self, mock_dependencies):
        """Test handler initializes correctly."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.window == parent
        assert handler.settings_manager == settings
        assert handler.status_manager == status
        assert handler.is_processing is False
        assert handler.last_operation == ""

    def test_cannot_instantiate_abstract_base(self, mock_dependencies):
        """Test BaseVCSHandler cannot be instantiated directly."""
        parent, settings, status = mock_dependencies

        # Creating instance works
        handler = BaseVCSHandler(parent, settings, status)

        # But calling abstract methods raises NotImplementedError
        with pytest.raises(NotImplementedError):
            handler._check_repository_ready()

        with pytest.raises(NotImplementedError):
            handler._get_busy_message()


class TestReadinessChecks:
    """Test readiness check functionality."""

    def test_ensure_ready_when_ready(self, mock_dependencies):
        """Test _ensure_ready returns True when ready."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.repo_ready = True
        handler.is_processing = False

        assert handler._ensure_ready() is True
        # Should not show any message
        status.show_message.assert_not_called()

    def test_ensure_ready_when_repo_not_ready(self, mock_dependencies):
        """Test _ensure_ready returns False when repository not ready."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.repo_ready = False

        assert handler._ensure_ready() is False

    def test_ensure_ready_when_processing(self, mock_dependencies):
        """Test _ensure_ready returns False when already processing."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.repo_ready = True
        handler.is_processing = True  # Already busy

        assert handler._ensure_ready() is False

        # Should show busy message
        status.show_message.assert_called_once()
        call_args = status.show_message.call_args[0]
        assert call_args[0] == "warning"
        assert call_args[1] == "Busy"
        assert "busy" in call_args[2].lower()

    def test_ensure_ready_shows_correct_busy_message(self, mock_dependencies):
        """Test _ensure_ready shows handler-specific busy message."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.repo_ready = True
        handler.is_processing = True
        handler.busy_message = "Custom busy message"

        handler._ensure_ready()

        # Should show custom message
        call_args = status.show_message.call_args[0]
        assert call_args[2] == "Custom busy message"


class TestUIStateUpdates:
    """Test UI state update functionality."""

    def test_update_ui_state_calls_window(self, mock_dependencies):
        """Test _update_ui_state delegates to window."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler._update_ui_state()

        parent._update_ui_state.assert_called_once()

    def test_update_ui_state_handles_missing_method(self, mock_dependencies):
        """Test _update_ui_state handles missing _update_ui_state method."""
        parent, settings, status = mock_dependencies
        del parent._update_ui_state  # Remove method

        handler = ConcreteVCSHandler(parent, settings, status)

        # Should not crash
        handler._update_ui_state()


class TestOperationLifecycle:
    """Test operation lifecycle management."""

    def test_start_operation(self, mock_dependencies):
        """Test _start_operation marks operation as started."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler._start_operation("test_operation")

        assert handler.is_processing is True
        assert handler.last_operation == "test_operation"
        parent._update_ui_state.assert_called_once()

    def test_complete_operation_success(self, mock_dependencies):
        """Test _complete_operation marks operation as completed."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.is_processing = True
        handler.last_operation = "test_operation"

        handler._complete_operation(success=True)

        assert handler.is_processing is False
        parent._update_ui_state.assert_called_once()

    def test_complete_operation_failure(self, mock_dependencies):
        """Test _complete_operation handles failure."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.is_processing = True
        handler.last_operation = "failed_operation"

        handler._complete_operation(success=False)

        assert handler.is_processing is False
        parent._update_ui_state.assert_called_once()

    def test_complete_operation_default_success(self, mock_dependencies):
        """Test _complete_operation defaults to success=True."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.is_processing = True

        # Call without success parameter
        handler._complete_operation()

        assert handler.is_processing is False


class TestProcessingState:
    """Test processing state management."""

    def test_initial_state_not_processing(self, mock_dependencies):
        """Test handler starts in not-processing state."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.is_processing is False
        assert handler.last_operation == ""

    def test_processing_state_transitions(self, mock_dependencies):
        """Test processing state transitions correctly."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # Start operation
        handler._start_operation("operation1")
        assert handler.is_processing is True
        assert handler.last_operation == "operation1"

        # Complete operation
        handler._complete_operation()
        assert handler.is_processing is False
        assert handler.last_operation == "operation1"  # Preserved

        # Start another operation
        handler._start_operation("operation2")
        assert handler.is_processing is True
        assert handler.last_operation == "operation2"


class TestTemplateMethodPattern:
    """Test template method pattern implementation."""

    def test_check_repository_ready_required(self, mock_dependencies):
        """Test _check_repository_ready must be implemented."""
        parent, settings, status = mock_dependencies

        handler = BaseVCSHandler(parent, settings, status)

        with pytest.raises(NotImplementedError):
            handler._check_repository_ready()

    def test_get_busy_message_required(self, mock_dependencies):
        """Test _get_busy_message must be implemented."""
        parent, settings, status = mock_dependencies

        handler = BaseVCSHandler(parent, settings, status)

        with pytest.raises(NotImplementedError):
            handler._get_busy_message()

    def test_concrete_implementation_provides_methods(self, mock_dependencies):
        """Test concrete implementation can override abstract methods."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # Should not raise
        assert handler._check_repository_ready() is True
        assert handler._get_busy_message() == "Handler is busy"
