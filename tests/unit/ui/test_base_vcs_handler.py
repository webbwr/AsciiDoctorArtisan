"""
Tests for ui.base_vcs_handler module.

Tests base VCS handler functionality including:
- Processing state management
- Readiness checks (template method pattern)
- UI state updates
- Operation lifecycle
"""

from unittest.mock import Mock

import pytest

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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
class TestMultipleOperationSequences:
    """Test handling multiple operations in sequence."""

    def test_multiple_operations_sequence(self, mock_dependencies):
        """Test handler can execute multiple operations sequentially."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # First operation
        handler._start_operation("operation1")
        assert handler.is_processing is True
        assert handler.last_operation == "operation1"

        handler._complete_operation()
        assert handler.is_processing is False

        # Second operation
        handler._start_operation("operation2")
        assert handler.is_processing is True
        assert handler.last_operation == "operation2"

        handler._complete_operation()
        assert handler.is_processing is False

        # Third operation
        handler._start_operation("operation3")
        assert handler.is_processing is True
        assert handler.last_operation == "operation3"

    def test_rapid_operation_succession(self, mock_dependencies):
        """Test rapid succession of operations."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        for i in range(10):
            handler._start_operation(f"operation{i}")
            assert handler.is_processing is True
            assert handler.last_operation == f"operation{i}"
            handler._complete_operation()
            assert handler.is_processing is False

    def test_operations_with_mixed_success_failure(self, mock_dependencies):
        """Test operations with alternating success/failure."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # Success
        handler._start_operation("op1")
        handler._complete_operation(success=True)

        # Failure
        handler._start_operation("op2")
        handler._complete_operation(success=False)

        # Success
        handler._start_operation("op3")
        handler._complete_operation(success=True)

        assert handler.is_processing is False
        assert handler.last_operation == "op3"


@pytest.mark.unit
class TestLastOperationTracking:
    """Test last_operation tracking."""

    def test_last_operation_empty_initially(self, mock_dependencies):
        """Test last_operation is empty string initially."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.last_operation == ""

    def test_last_operation_updates_on_start(self, mock_dependencies):
        """Test last_operation updates when operation starts."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("first_operation")
        assert handler.last_operation == "first_operation"

    def test_last_operation_preserved_after_completion(self, mock_dependencies):
        """Test last_operation preserved after operation completes."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("completed_operation")
        handler._complete_operation()

        assert handler.last_operation == "completed_operation"
        assert handler.is_processing is False

    def test_last_operation_overwritten_by_next(self, mock_dependencies):
        """Test last_operation overwritten by next operation."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("first")
        handler._complete_operation()
        assert handler.last_operation == "first"

        handler._start_operation("second")
        assert handler.last_operation == "second"

    def test_last_operation_with_empty_string(self, mock_dependencies):
        """Test last_operation can be empty string."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("")
        assert handler.last_operation == ""

    def test_last_operation_with_special_characters(self, mock_dependencies):
        """Test last_operation handles special characters."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("operation_with-special.chars:123")
        assert handler.last_operation == "operation_with-special.chars:123"


@pytest.mark.unit
class TestReadinessCheckEdgeCases:
    """Test edge cases for readiness checks."""

    def test_ensure_ready_with_repo_not_ready_and_processing(self, mock_dependencies):
        """Test _ensure_ready when both repo not ready and processing."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.repo_ready = False
        handler.is_processing = True

        # Should return False (repo not ready checked first)
        assert handler._ensure_ready() is False

    def test_ensure_ready_called_multiple_times_while_processing(
        self, mock_dependencies
    ):
        """Test _ensure_ready called repeatedly while processing."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.repo_ready = True
        handler.is_processing = True

        # Call multiple times
        assert handler._ensure_ready() is False
        assert handler._ensure_ready() is False
        assert handler._ensure_ready() is False

        # Should show message each time
        assert status.show_message.call_count == 3

    def test_ensure_ready_toggles_with_repo_state(self, mock_dependencies):
        """Test _ensure_ready reflects repo state changes."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # Initially ready
        handler.repo_ready = True
        assert handler._ensure_ready() is True

        # Repo becomes unavailable
        handler.repo_ready = False
        assert handler._ensure_ready() is False

        # Repo available again
        handler.repo_ready = True
        assert handler._ensure_ready() is True

    def test_ensure_ready_repo_ready_changes_during_processing(self, mock_dependencies):
        """Test repo_ready changes don't matter when processing."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.is_processing = True

        # Even if repo is ready, should return False
        handler.repo_ready = True
        assert handler._ensure_ready() is False

        # Even if repo is not ready, should still return False
        handler.repo_ready = False
        assert handler._ensure_ready() is False


@pytest.mark.unit
class TestUIStateUpdateEdgeCases:
    """Test edge cases for UI state updates."""

    def test_update_ui_state_called_multiple_times(self, mock_dependencies):
        """Test _update_ui_state can be called multiple times."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._update_ui_state()
        handler._update_ui_state()
        handler._update_ui_state()

        assert parent._update_ui_state.call_count == 3

    def test_update_ui_state_with_none_window(self, mock_dependencies):
        """Test _update_ui_state handles None window."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.window = None

        # Should not crash
        handler._update_ui_state()

    def test_update_ui_state_during_operation(self, mock_dependencies):
        """Test _update_ui_state works during operation."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("test")
        handler._update_ui_state()

        assert (
            parent._update_ui_state.call_count == 2
        )  # Once in _start_operation, once manually

    def test_update_ui_state_called_by_start_and_complete(self, mock_dependencies):
        """Test _update_ui_state called by both start and complete operations."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("test")
        handler._complete_operation()

        assert parent._update_ui_state.call_count == 2


@pytest.mark.unit
class TestOperationLifecycleEdgeCases:
    """Test edge cases for operation lifecycle."""

    def test_complete_operation_without_starting(self, mock_dependencies):
        """Test _complete_operation can be called without starting."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # Complete without starting (is_processing already False)
        handler._complete_operation()

        assert handler.is_processing is False

    def test_start_operation_while_already_processing(self, mock_dependencies):
        """Test _start_operation can be called while already processing."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("operation1")
        assert handler.is_processing is True

        # Start another operation (overwrites)
        handler._start_operation("operation2")
        assert handler.is_processing is True
        assert handler.last_operation == "operation2"

    def test_operation_with_very_long_name(self, mock_dependencies):
        """Test operation with very long name."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        long_name = "operation_" + "x" * 1000
        handler._start_operation(long_name)

        assert handler.last_operation == long_name

    def test_complete_operation_success_parameter_false(self, mock_dependencies):
        """Test _complete_operation with explicit success=False."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler._start_operation("failing_operation")

        handler._complete_operation(success=False)

        assert handler.is_processing is False


@pytest.mark.unit
class TestConcreteImplementationEdgeCases:
    """Test edge cases for concrete implementation."""

    def test_concrete_handler_can_change_repo_ready(self, mock_dependencies):
        """Test concrete handler can change repo_ready state."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler.repo_ready = True
        assert handler._check_repository_ready() is True

        handler.repo_ready = False
        assert handler._check_repository_ready() is False

    def test_concrete_handler_can_change_busy_message(self, mock_dependencies):
        """Test concrete handler can change busy message."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler.busy_message = "Custom message 1"
        assert handler._get_busy_message() == "Custom message 1"

        handler.busy_message = "Custom message 2"
        assert handler._get_busy_message() == "Custom message 2"

    def test_concrete_handler_defaults(self, mock_dependencies):
        """Test concrete handler has expected defaults."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.repo_ready is True
        assert handler.busy_message == "Handler is busy"


@pytest.mark.unit
class TestProcessingStateAdvanced:
    """Test advanced processing state scenarios."""

    def test_processing_state_persists_across_ensure_ready_calls(
        self, mock_dependencies
    ):
        """Test is_processing state persists across _ensure_ready calls."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        handler._start_operation("test")
        assert handler.is_processing is True

        # Call _ensure_ready multiple times
        handler._ensure_ready()
        handler._ensure_ready()

        assert handler.is_processing is True

    def test_processing_state_isolation(self, mock_dependencies):
        """Test two handlers have isolated processing states."""
        parent, settings, status = mock_dependencies

        handler1 = ConcreteVCSHandler(parent, settings, status)
        handler2 = ConcreteVCSHandler(parent, settings, status)

        handler1._start_operation("op1")
        assert handler1.is_processing is True
        assert handler2.is_processing is False

        handler2._start_operation("op2")
        assert handler1.is_processing is True
        assert handler2.is_processing is True

        handler1._complete_operation()
        assert handler1.is_processing is False
        assert handler2.is_processing is True


@pytest.mark.unit
class TestAttributeStorage:
    """Test attribute storage and access."""

    def test_window_reference_stored(self, mock_dependencies):
        """Test window reference is stored correctly."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.window is parent

    def test_settings_manager_reference_stored(self, mock_dependencies):
        """Test settings_manager reference is stored correctly."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.settings_manager is settings

    def test_status_manager_reference_stored(self, mock_dependencies):
        """Test status_manager reference is stored correctly."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        assert handler.status_manager is status

    def test_all_attributes_accessible(self, mock_dependencies):
        """Test all attributes are accessible."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)

        # Should not raise AttributeError
        assert hasattr(handler, "window")
        assert hasattr(handler, "settings_manager")
        assert hasattr(handler, "status_manager")
        assert hasattr(handler, "is_processing")
        assert hasattr(handler, "last_operation")


@pytest.mark.unit
class TestBusyMessageFormatting:
    """Test busy message formatting."""

    def test_busy_message_empty_string(self, mock_dependencies):
        """Test busy message can be empty string."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.busy_message = ""
        handler.is_processing = True

        handler._ensure_ready()

        # Should show empty message
        call_args = status.show_message.call_args[0]
        assert call_args[2] == ""

    def test_busy_message_with_newlines(self, mock_dependencies):
        """Test busy message can contain newlines."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.busy_message = "Line 1\nLine 2\nLine 3"
        handler.is_processing = True

        handler._ensure_ready()

        call_args = status.show_message.call_args[0]
        assert "Line 1\nLine 2\nLine 3" in call_args[2]

    def test_busy_message_with_special_characters(self, mock_dependencies):
        """Test busy message can contain special characters."""
        parent, settings, status = mock_dependencies

        handler = ConcreteVCSHandler(parent, settings, status)
        handler.busy_message = "Special: <>&\"'\t"
        handler.is_processing = True

        handler._ensure_ready()

        call_args = status.show_message.call_args[0]
        assert call_args[2] == "Special: <>&\"'\t"
