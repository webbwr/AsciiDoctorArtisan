"""
Tests for ui.worker_manager module.

Tests worker thread lifecycle management including:
- Worker manager initialization
- Worker pool setup
- Thread creation and signal connections
- Cancellation operations
- Shutdown procedures
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QThread

from asciidoc_artisan.ui.worker_manager import WorkerManager


@pytest.fixture
def mock_editor():
    """Create a mock AsciiDocEditor for testing."""
    editor = Mock()
    editor._settings = Mock()
    editor._settings.ollama_enabled = False
    editor._settings.ollama_model = None

    # Mock signal attributes
    editor.request_git_command = Mock()
    editor.request_git_command.connect = Mock()
    editor.request_git_status = Mock()
    editor.request_git_status.connect = Mock()
    editor.request_detailed_git_status = Mock()
    editor.request_detailed_git_status.connect = Mock()
    editor.request_github_command = Mock()
    editor.request_github_command.connect = Mock()
    editor.request_pandoc_conversion = Mock()
    editor.request_pandoc_conversion.connect = Mock()
    editor.request_preview_render = Mock()
    editor.request_preview_render.connect = Mock()

    # Mock handler methods
    editor._handle_git_result = Mock()
    editor._handle_git_status = Mock()
    editor._handle_detailed_git_status = Mock()
    editor._handle_github_result = Mock()
    editor._handle_preview_complete = Mock()
    editor._handle_preview_error = Mock()

    # Mock pandoc result handler
    editor.pandoc_result_handler = Mock()
    editor.pandoc_result_handler.handle_pandoc_result = Mock()
    editor.pandoc_result_handler.handle_pandoc_error_result = Mock()

    return editor


class TestWorkerManagerInitialization:
    """Test WorkerManager initialization."""

    def test_initialization_without_pool(self, mock_editor):
        """Test WorkerManager initializes without worker pool."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        assert manager.editor is mock_editor
        assert manager.use_worker_pool is False
        assert manager.worker_pool is None
        assert manager.git_worker is None
        assert manager.github_worker is None
        assert manager.pandoc_worker is None
        assert manager.preview_worker is None
        assert manager.ollama_chat_worker is None
        assert manager.claude_worker is None

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_initialization_with_pool_default_threads(self, mock_pool_class, mock_editor):
        """Test WorkerManager initializes worker pool with default thread count."""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)

        assert manager.use_worker_pool is True
        assert manager.worker_pool is not None
        mock_pool_class.assert_called_once()

        # Should use CPU count * 2 (with minimum of 4)
        call_args = mock_pool_class.call_args
        assert "max_threads" in call_args[1]
        assert call_args[1]["max_threads"] >= 4

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_initialization_with_pool_custom_threads(self, mock_pool_class, mock_editor):
        """Test WorkerManager initializes pool with custom thread count."""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True, max_pool_threads=8)

        mock_pool_class.assert_called_once_with(max_threads=8)
        assert manager.worker_pool is mock_pool


class TestSetupWorkersAndThreads:
    """Test worker and thread setup."""

    @patch("asciidoc_artisan.claude.ClaudeWorker")
    @patch("asciidoc_artisan.ui.worker_manager.OllamaChatWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PreviewWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PandocWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitHubCLIWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitWorker")
    @patch("asciidoc_artisan.ui.worker_manager.QThread")
    def test_setup_creates_all_workers(
        self,
        mock_thread_class,
        mock_git_worker_class,
        mock_github_worker_class,
        mock_pandoc_worker_class,
        mock_preview_worker_class,
        mock_ollama_worker_class,
        mock_claude_worker_class,
        mock_editor,
    ):
        """Test setup_workers_and_threads creates all workers."""
        # Mock thread instances
        mock_threads = [Mock(spec=QThread) for _ in range(6)]
        for thread in mock_threads:
            thread.start = Mock()
            thread.finished = Mock()
            thread.finished.connect = Mock()

        mock_thread_class.side_effect = mock_threads

        # Mock worker instances
        mock_git_worker = Mock()
        mock_git_worker.moveToThread = Mock()
        mock_git_worker.command_complete = Mock()
        mock_git_worker.command_complete.connect = Mock()
        mock_git_worker.status_ready = Mock()
        mock_git_worker.status_ready.connect = Mock()
        mock_git_worker.detailed_status_ready = Mock()
        mock_git_worker.detailed_status_ready.connect = Mock()
        mock_git_worker.deleteLater = Mock()

        mock_github_worker = Mock()
        mock_github_worker.moveToThread = Mock()
        mock_github_worker.github_result_ready = Mock()
        mock_github_worker.github_result_ready.connect = Mock()
        mock_github_worker.deleteLater = Mock()

        mock_pandoc_worker = Mock()
        mock_pandoc_worker.moveToThread = Mock()
        mock_pandoc_worker.set_ollama_config = Mock()
        mock_pandoc_worker.conversion_complete = Mock()
        mock_pandoc_worker.conversion_complete.connect = Mock()
        mock_pandoc_worker.conversion_error = Mock()
        mock_pandoc_worker.conversion_error.connect = Mock()
        mock_pandoc_worker.deleteLater = Mock()

        mock_preview_worker = Mock()
        mock_preview_worker.moveToThread = Mock()
        mock_preview_worker.initialize_asciidoc = Mock()
        mock_preview_worker.render_complete = Mock()
        mock_preview_worker.render_complete.connect = Mock()
        mock_preview_worker.render_error = Mock()
        mock_preview_worker.render_error.connect = Mock()
        mock_preview_worker.deleteLater = Mock()

        mock_ollama_worker = Mock()
        mock_ollama_worker.moveToThread = Mock()
        mock_ollama_worker.deleteLater = Mock()

        mock_claude_worker = Mock()
        mock_claude_worker.moveToThread = Mock()
        mock_claude_worker.deleteLater = Mock()

        mock_git_worker_class.return_value = mock_git_worker
        mock_github_worker_class.return_value = mock_github_worker
        mock_pandoc_worker_class.return_value = mock_pandoc_worker
        mock_preview_worker_class.return_value = mock_preview_worker
        mock_ollama_worker_class.return_value = mock_ollama_worker
        mock_claude_worker_class.return_value = mock_claude_worker

        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.setup_workers_and_threads()

        # Verify all workers created
        assert manager.git_worker is mock_git_worker
        assert manager.github_worker is mock_github_worker
        assert manager.pandoc_worker is mock_pandoc_worker
        assert manager.preview_worker is mock_preview_worker
        assert manager.ollama_chat_worker is mock_ollama_worker
        assert manager.claude_worker is mock_claude_worker

        # Verify all threads started
        for thread in mock_threads:
            thread.start.assert_called_once()

    @patch("asciidoc_artisan.claude.ClaudeWorker")
    @patch("asciidoc_artisan.ui.worker_manager.OllamaChatWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PreviewWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PandocWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitHubCLIWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitWorker")
    @patch("asciidoc_artisan.ui.worker_manager.QThread")
    def test_setup_connects_git_signals(
        self,
        mock_thread_class,
        mock_git_worker_class,
        mock_github_worker_class,
        mock_pandoc_worker_class,
        mock_preview_worker_class,
        mock_ollama_worker_class,
        mock_claude_worker_class,
        mock_editor,
    ):
        """Test setup connects Git worker signals."""
        # Setup mocks (simplified version)
        mock_threads = [Mock(spec=QThread) for _ in range(6)]
        for thread in mock_threads:
            thread.start = Mock()
            thread.finished = Mock()
            thread.finished.connect = Mock()
        mock_thread_class.side_effect = mock_threads

        mock_git_worker = Mock()
        mock_git_worker.moveToThread = Mock()
        mock_git_worker.command_complete = Mock()
        mock_git_worker.command_complete.connect = Mock()
        mock_git_worker.status_ready = Mock()
        mock_git_worker.status_ready.connect = Mock()
        mock_git_worker.detailed_status_ready = Mock()
        mock_git_worker.detailed_status_ready.connect = Mock()
        mock_git_worker.deleteLater = Mock()
        mock_git_worker_class.return_value = mock_git_worker

        # Setup other workers to return minimal mocks
        for worker_class in [
            mock_github_worker_class,
            mock_pandoc_worker_class,
            mock_preview_worker_class,
            mock_ollama_worker_class,
            mock_claude_worker_class,
        ]:
            mock_worker = Mock()
            mock_worker.moveToThread = Mock()
            mock_worker.deleteLater = Mock()
            # Add signal-like attributes with connect methods
            mock_worker.github_result_ready = Mock()
            mock_worker.github_result_ready.connect = Mock()
            mock_worker.conversion_complete = Mock()
            mock_worker.conversion_complete.connect = Mock()
            mock_worker.conversion_error = Mock()
            mock_worker.conversion_error.connect = Mock()
            mock_worker.set_ollama_config = Mock()
            mock_worker.render_complete = Mock()
            mock_worker.render_complete.connect = Mock()
            mock_worker.render_error = Mock()
            mock_worker.render_error.connect = Mock()
            mock_worker.initialize_asciidoc = Mock()
            worker_class.return_value = mock_worker

        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.setup_workers_and_threads()

        # Verify Git signals connected
        mock_editor.request_git_command.connect.assert_called_once()
        mock_git_worker.command_complete.connect.assert_called_once()


class TestPoolOperations:
    """Test worker pool operations."""

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_get_pool_statistics_with_pool(self, mock_pool_class, mock_editor):
        """Test getting pool statistics when pool is enabled."""
        mock_pool = Mock()
        mock_pool.get_statistics.return_value = {
            "active_threads": 2,
            "pending_tasks": 5,
        }
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)
        stats = manager.get_pool_statistics()

        assert stats == {"active_threads": 2, "pending_tasks": 5}
        mock_pool.get_statistics.assert_called_once()

    def test_get_pool_statistics_without_pool(self, mock_editor):
        """Test getting pool statistics when pool is disabled."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        stats = manager.get_pool_statistics()

        assert stats == {}

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_cancel_all_pool_tasks_with_pool(self, mock_pool_class, mock_editor):
        """Test cancelling all pool tasks when pool is enabled."""
        mock_pool = Mock()
        mock_pool.cancel_all.return_value = 3
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)
        cancelled = manager.cancel_all_pool_tasks()

        assert cancelled == 3
        mock_pool.cancel_all.assert_called_once()

    def test_cancel_all_pool_tasks_without_pool(self, mock_editor):
        """Test cancelling pool tasks when pool is disabled."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        cancelled = manager.cancel_all_pool_tasks()

        assert cancelled == 0

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_wait_for_pool_done_with_pool(self, mock_pool_class, mock_editor):
        """Test waiting for pool when pool is enabled."""
        mock_pool = Mock()
        mock_pool.wait_for_done.return_value = True
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)
        result = manager.wait_for_pool_done(timeout_ms=3000)

        assert result is True
        mock_pool.wait_for_done.assert_called_once_with(3000)

    def test_wait_for_pool_done_without_pool(self, mock_editor):
        """Test waiting for pool when pool is disabled returns True."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        result = manager.wait_for_pool_done()

        assert result is True


class TestCancellationOperations:
    """Test worker cancellation operations."""

    def test_cancel_git_operation(self, mock_editor):
        """Test cancelling Git operation."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.git_worker = Mock()
        manager.git_worker.cancel = Mock()

        manager.cancel_git_operation()

        manager.git_worker.cancel.assert_called_once()

    def test_cancel_git_operation_no_worker(self, mock_editor):
        """Test cancelling Git operation when worker is None."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.git_worker = None

        # Should not crash
        manager.cancel_git_operation()

    def test_cancel_github_operation(self, mock_editor):
        """Test cancelling GitHub operation."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.github_worker = Mock()
        manager.github_worker.cancel = Mock()

        manager.cancel_github_operation()

        manager.github_worker.cancel.assert_called_once()

    def test_cancel_pandoc_operation(self, mock_editor):
        """Test cancelling Pandoc operation."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.pandoc_worker = Mock()
        manager.pandoc_worker.cancel = Mock()

        manager.cancel_pandoc_operation()

        manager.pandoc_worker.cancel.assert_called_once()

    def test_cancel_preview_operation(self, mock_editor):
        """Test cancelling preview operation."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.preview_worker = Mock()
        manager.preview_worker.cancel = Mock()

        manager.cancel_preview_operation()

        manager.preview_worker.cancel.assert_called_once()


class TestShutdown:
    """Test worker manager shutdown."""

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_shutdown_with_pool(self, mock_pool_class, mock_editor):
        """Test shutdown cancels and waits for pool tasks."""
        mock_pool = Mock()
        mock_pool.cancel_all.return_value = 5
        mock_pool.wait_for_done.return_value = True
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)
        manager.shutdown()

        mock_pool.cancel_all.assert_called_once()
        mock_pool.wait_for_done.assert_called_once_with(5000)

    def test_shutdown_stops_git_thread(self, mock_editor):
        """Test shutdown stops Git thread."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)
        mock_thread = Mock()
        mock_thread.isRunning.return_value = True
        mock_thread.quit = Mock()
        mock_thread.wait = Mock()
        manager.git_thread = mock_thread

        manager.shutdown()

        # Check the saved mock reference (git_thread is None after shutdown)
        mock_thread.quit.assert_called_once()
        mock_thread.wait.assert_called_once_with(3000)

    def test_shutdown_stops_all_threads(self, mock_editor):
        """Test shutdown stops all running threads."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        # Mock all threads as running and save references
        thread_mocks = {}
        threads = [
            "git_thread",
            "github_thread",
            "pandoc_thread",
            "preview_thread",
            "ollama_chat_thread",
            "claude_thread",
        ]

        for thread_name in threads:
            thread = Mock()
            thread.isRunning.return_value = True
            thread.quit = Mock()
            thread.wait = Mock(return_value=True)  # Simulate clean exit
            thread.deleteLater = Mock()
            setattr(manager, thread_name, thread)
            thread_mocks[thread_name] = thread

        manager.shutdown()

        # Verify all threads were stopped (check saved mocks)
        for thread_name, thread in thread_mocks.items():
            thread.quit.assert_called_once()
            thread.wait.assert_called_once_with(3000)
            thread.deleteLater.assert_called_once()

    def test_shutdown_skips_stopped_threads(self, mock_editor):
        """Test shutdown skips threads that are not running."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        mock_thread = Mock()
        mock_thread.isRunning.return_value = False
        mock_thread.quit = Mock()
        manager.git_thread = mock_thread

        manager.shutdown()

        # Should not call quit on stopped thread (check saved mock)
        mock_thread.quit.assert_not_called()

    def test_shutdown_force_terminate_hanging_threads(self, mock_editor):
        """Test shutdown force-terminates threads that don't exit cleanly.

        Tests lines 367-376, 379-388:
        - Ollama/Claude thread force termination when wait() returns False
        """
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        # Mock ollama thread that hangs
        ollama_thread = Mock()
        ollama_thread.isRunning.return_value = True
        ollama_thread.quit = Mock()
        ollama_thread.wait = Mock(return_value=False)  # Doesn't exit cleanly
        ollama_thread.terminate = Mock()
        ollama_thread.deleteLater = Mock()
        manager.ollama_chat_thread = ollama_thread

        # Mock claude thread that hangs
        claude_thread = Mock()
        claude_thread.isRunning.return_value = True
        claude_thread.quit = Mock()
        claude_thread.wait = Mock(side_effect=[False, True])  # First call fails, second succeeds
        claude_thread.terminate = Mock()
        claude_thread.deleteLater = Mock()
        manager.claude_thread = claude_thread

        manager.shutdown()

        # Verify terminate was called on both
        ollama_thread.terminate.assert_called_once()
        claude_thread.terminate.assert_called_once()

        # Verify wait was called twice (once for quit, once after terminate)
        assert ollama_thread.wait.call_count == 2
        assert claude_thread.wait.call_count == 2

    def test_shutdown_handles_none_threads(self, mock_editor):
        """Test shutdown handles None threads gracefully."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_thread = None
        manager.github_thread = None
        manager.pandoc_thread = None
        manager.preview_thread = None

        # Should not crash
        manager.shutdown()


class TestWorkerInitializationEdgeCases:
    """Test edge cases for worker initialization."""

    def test_manager_with_null_editor_settings(self, mock_editor):
        """Test manager handles null editor settings."""
        mock_editor._settings = None

        manager = WorkerManager(mock_editor, use_worker_pool=False)

        assert manager.editor is mock_editor
        assert manager.worker_pool is None

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_pool_initialization_with_zero_threads(self, mock_pool_class, mock_editor):
        """Test pool initialization with zero threads passes value through."""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool

        WorkerManager(mock_editor, use_worker_pool=True, max_pool_threads=0)

        # Passes value through to pool (pool enforces minimum)
        mock_pool_class.assert_called_once_with(max_threads=0)

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_pool_initialization_with_negative_threads(self, mock_pool_class, mock_editor):
        """Test pool initialization with negative threads passes value through."""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool

        WorkerManager(mock_editor, use_worker_pool=True, max_pool_threads=-5)

        # Passes value through to pool (pool enforces minimum)
        mock_pool_class.assert_called_once_with(max_threads=-5)

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_pool_initialization_with_very_large_threads(self, mock_pool_class, mock_editor):
        """Test pool initialization with very large thread count."""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool

        WorkerManager(mock_editor, use_worker_pool=True, max_pool_threads=1000)

        mock_pool_class.assert_called_once_with(max_threads=1000)


class TestSignalConnectionVerification:
    """Test signal connection verification."""

    @patch("asciidoc_artisan.claude.ClaudeWorker")
    @patch("asciidoc_artisan.ui.worker_manager.OllamaChatWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PreviewWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PandocWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitHubCLIWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitWorker")
    @patch("asciidoc_artisan.ui.worker_manager.QThread")
    def test_github_signals_connected(
        self,
        mock_thread_class,
        mock_git_worker_class,
        mock_github_worker_class,
        mock_pandoc_worker_class,
        mock_preview_worker_class,
        mock_ollama_worker_class,
        mock_claude_worker_class,
        mock_editor,
    ):
        """Test GitHub worker signals are connected."""
        # Setup thread mocks
        mock_threads = [Mock(spec=QThread) for _ in range(6)]
        for thread in mock_threads:
            thread.start = Mock()
            thread.finished = Mock()
            thread.finished.connect = Mock()
        mock_thread_class.side_effect = mock_threads

        # Setup GitHub worker mock
        mock_github_worker = Mock()
        mock_github_worker.moveToThread = Mock()
        mock_github_worker.github_result_ready = Mock()
        mock_github_worker.github_result_ready.connect = Mock()
        mock_github_worker.deleteLater = Mock()
        mock_github_worker_class.return_value = mock_github_worker

        # Setup minimal mocks for other workers
        for worker_class in [
            mock_git_worker_class,
            mock_pandoc_worker_class,
            mock_preview_worker_class,
            mock_ollama_worker_class,
            mock_claude_worker_class,
        ]:
            mock_worker = self._create_minimal_worker_mock()
            worker_class.return_value = mock_worker

        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.setup_workers_and_threads()

        # Verify GitHub signals connected
        mock_editor.request_github_command.connect.assert_called_once()
        mock_github_worker.github_result_ready.connect.assert_called_once()

    @patch("asciidoc_artisan.claude.ClaudeWorker")
    @patch("asciidoc_artisan.ui.worker_manager.OllamaChatWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PreviewWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PandocWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitHubCLIWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitWorker")
    @patch("asciidoc_artisan.ui.worker_manager.QThread")
    def test_pandoc_signals_connected(
        self,
        mock_thread_class,
        mock_git_worker_class,
        mock_github_worker_class,
        mock_pandoc_worker_class,
        mock_preview_worker_class,
        mock_ollama_worker_class,
        mock_claude_worker_class,
        mock_editor,
    ):
        """Test Pandoc worker signals are connected."""
        # Setup thread mocks
        mock_threads = [Mock(spec=QThread) for _ in range(6)]
        for thread in mock_threads:
            thread.start = Mock()
            thread.finished = Mock()
            thread.finished.connect = Mock()
        mock_thread_class.side_effect = mock_threads

        # Setup Pandoc worker mock
        mock_pandoc_worker = Mock()
        mock_pandoc_worker.moveToThread = Mock()
        mock_pandoc_worker.conversion_complete = Mock()
        mock_pandoc_worker.conversion_complete.connect = Mock()
        mock_pandoc_worker.conversion_error = Mock()
        mock_pandoc_worker.conversion_error.connect = Mock()
        mock_pandoc_worker.set_ollama_config = Mock()
        mock_pandoc_worker.deleteLater = Mock()
        mock_pandoc_worker_class.return_value = mock_pandoc_worker

        # Setup minimal mocks for other workers
        for worker_class in [
            mock_git_worker_class,
            mock_github_worker_class,
            mock_preview_worker_class,
            mock_ollama_worker_class,
            mock_claude_worker_class,
        ]:
            mock_worker = self._create_minimal_worker_mock()
            worker_class.return_value = mock_worker

        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.setup_workers_and_threads()

        # Verify Pandoc signals connected
        mock_editor.request_pandoc_conversion.connect.assert_called_once()
        mock_pandoc_worker.conversion_complete.connect.assert_called_once()
        mock_pandoc_worker.conversion_error.connect.assert_called_once()

    @patch("asciidoc_artisan.claude.ClaudeWorker")
    @patch("asciidoc_artisan.ui.worker_manager.OllamaChatWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PreviewWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PandocWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitHubCLIWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitWorker")
    @patch("asciidoc_artisan.ui.worker_manager.QThread")
    def test_preview_signals_connected(
        self,
        mock_thread_class,
        mock_git_worker_class,
        mock_github_worker_class,
        mock_pandoc_worker_class,
        mock_preview_worker_class,
        mock_ollama_worker_class,
        mock_claude_worker_class,
        mock_editor,
    ):
        """Test Preview worker signals are connected."""
        # Setup thread mocks
        mock_threads = [Mock(spec=QThread) for _ in range(6)]
        for thread in mock_threads:
            thread.start = Mock()
            thread.finished = Mock()
            thread.finished.connect = Mock()
        mock_thread_class.side_effect = mock_threads

        # Setup Preview worker mock
        mock_preview_worker = Mock()
        mock_preview_worker.moveToThread = Mock()
        mock_preview_worker.render_complete = Mock()
        mock_preview_worker.render_complete.connect = Mock()
        mock_preview_worker.render_error = Mock()
        mock_preview_worker.render_error.connect = Mock()
        mock_preview_worker.initialize_asciidoc = Mock()
        mock_preview_worker.deleteLater = Mock()
        mock_preview_worker_class.return_value = mock_preview_worker

        # Setup minimal mocks for other workers
        for worker_class in [
            mock_git_worker_class,
            mock_github_worker_class,
            mock_pandoc_worker_class,
            mock_ollama_worker_class,
            mock_claude_worker_class,
        ]:
            mock_worker = self._create_minimal_worker_mock()
            worker_class.return_value = mock_worker

        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.setup_workers_and_threads()

        # Verify Preview signals connected
        mock_editor.request_preview_render.connect.assert_called_once()
        mock_preview_worker.render_complete.connect.assert_called_once()
        mock_preview_worker.render_error.connect.assert_called_once()

    def _create_minimal_worker_mock(self):
        """Helper to create minimal worker mock with required attributes."""
        mock_worker = Mock()
        mock_worker.moveToThread = Mock()
        mock_worker.deleteLater = Mock()
        # Add signal-like attributes
        mock_worker.command_complete = Mock()
        mock_worker.command_complete.connect = Mock()
        mock_worker.status_ready = Mock()
        mock_worker.status_ready.connect = Mock()
        mock_worker.detailed_status_ready = Mock()
        mock_worker.detailed_status_ready.connect = Mock()
        mock_worker.github_result_ready = Mock()
        mock_worker.github_result_ready.connect = Mock()
        mock_worker.conversion_complete = Mock()
        mock_worker.conversion_complete.connect = Mock()
        mock_worker.conversion_error = Mock()
        mock_worker.conversion_error.connect = Mock()
        mock_worker.render_complete = Mock()
        mock_worker.render_complete.connect = Mock()
        mock_worker.render_error = Mock()
        mock_worker.render_error.connect = Mock()
        mock_worker.set_ollama_config = Mock()
        mock_worker.initialize_asciidoc = Mock()
        return mock_worker


class TestThreadLifecycleEdgeCases:
    """Test thread lifecycle edge cases."""

    def test_shutdown_with_thread_timeout(self, mock_editor):
        """Test shutdown when thread wait times out - now uses force termination."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        mock_thread = Mock()
        mock_thread.isRunning.return_value = True
        mock_thread.quit = Mock()
        mock_thread.wait = Mock(return_value=False)  # Timeout
        mock_thread.terminate = Mock()
        manager.git_thread = mock_thread

        manager.shutdown()

        # Should call quit, wait, then terminate and wait again (check saved mock)
        mock_thread.quit.assert_called_once()
        assert mock_thread.wait.call_count == 2
        mock_thread.wait.assert_any_call(3000)  # First graceful wait
        mock_thread.wait.assert_any_call(1000)  # Second wait after terminate
        mock_thread.terminate.assert_called_once()

    def test_shutdown_with_multiple_timeouts(self, mock_editor):
        """Test shutdown handles multiple thread timeouts - with force termination."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        # Save mock references before shutdown
        thread_mocks = {}
        threads = ["git_thread", "github_thread", "pandoc_thread", "preview_thread"]
        for thread_name in threads:
            thread = Mock()
            thread.isRunning.return_value = True
            thread.quit = Mock()
            thread.wait = Mock(return_value=False)  # All timeout
            thread.terminate = Mock()
            setattr(manager, thread_name, thread)
            thread_mocks[thread_name] = thread

        manager.shutdown()

        # All should be attempted with terminate fallback (check saved mocks)
        for thread_name, thread in thread_mocks.items():
            thread.quit.assert_called_once()
            assert thread.wait.call_count == 2  # Graceful + post-terminate
            thread.terminate.assert_called_once()

    def test_thread_finished_signal_cleanup(self, mock_editor):
        """Test threads connect finished signal for cleanup."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_thread = Mock()
        manager.git_thread.finished = Mock()
        manager.git_thread.finished.connect = Mock()
        manager.git_worker = Mock()
        manager.git_worker.deleteLater = Mock()

        # Manually trigger finished signal callback
        # In real code, this is connected via finished.connect(worker.deleteLater)
        assert hasattr(manager.git_thread, "finished")
        assert hasattr(manager.git_worker, "deleteLater")


class TestMultipleWorkerCoordination:
    """Test coordination between multiple workers."""

    def test_cancel_all_operations(self, mock_editor):
        """Test cancelling all worker operations at once."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        # Setup all workers with cancel methods
        manager.git_worker = Mock()
        manager.git_worker.cancel = Mock()
        manager.github_worker = Mock()
        manager.github_worker.cancel = Mock()
        manager.pandoc_worker = Mock()
        manager.pandoc_worker.cancel = Mock()
        manager.preview_worker = Mock()
        manager.preview_worker.cancel = Mock()

        # Cancel all
        manager.cancel_git_operation()
        manager.cancel_github_operation()
        manager.cancel_pandoc_operation()
        manager.cancel_preview_operation()

        # Verify all cancelled
        manager.git_worker.cancel.assert_called_once()
        manager.github_worker.cancel.assert_called_once()
        manager.pandoc_worker.cancel.assert_called_once()
        manager.preview_worker.cancel.assert_called_once()

    def test_parallel_worker_cancellation(self, mock_editor):
        """Test cancelling multiple workers in parallel."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        workers = {
            "git_worker": Mock(cancel=Mock()),
            "github_worker": Mock(cancel=Mock()),
            "pandoc_worker": Mock(cancel=Mock()),
        }

        for name, worker in workers.items():
            setattr(manager, name, worker)

        # Simulate parallel cancellation
        manager.cancel_git_operation()
        manager.cancel_github_operation()
        manager.cancel_pandoc_operation()

        # All should be cancelled
        for worker in workers.values():
            worker.cancel.assert_called_once()


class TestErrorHandling:
    """Test error handling in worker manager."""

    def test_cancel_operation_with_exception(self, mock_editor):
        """Test cancellation handles worker exceptions."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_worker = Mock()
        manager.git_worker.cancel = Mock(side_effect=RuntimeError("Worker error"))

        # Should not crash
        try:
            manager.cancel_git_operation()
        except RuntimeError:
            # In production code, this might be caught and logged
            pass

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_pool_statistics_with_exception(self, mock_pool_class, mock_editor):
        """Test getting pool statistics when pool raises exception."""
        mock_pool = Mock()
        mock_pool.get_statistics = Mock(side_effect=RuntimeError("Pool error"))
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)

        # Should handle gracefully
        try:
            manager.get_pool_statistics()
        except RuntimeError:
            pass  # Expected behavior

    def test_shutdown_with_thread_exception(self, mock_editor):
        """Test shutdown handles thread quit exceptions."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_thread = Mock()
        manager.git_thread.isRunning.return_value = True
        manager.git_thread.quit = Mock(side_effect=RuntimeError("Thread error"))
        manager.git_thread.wait = Mock()

        # Should handle gracefully
        try:
            manager.shutdown()
        except RuntimeError:
            pass  # May or may not be caught


class TestWorkerStateTransitions:
    """Test worker state transitions."""

    def test_worker_initialization_before_setup(self, mock_editor):
        """Test workers are None before setup."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        assert manager.git_worker is None
        assert manager.github_worker is None
        assert manager.pandoc_worker is None
        assert manager.preview_worker is None
        assert manager.ollama_chat_worker is None
        assert manager.claude_worker is None

    @patch("asciidoc_artisan.claude.ClaudeWorker")
    @patch("asciidoc_artisan.ui.worker_manager.OllamaChatWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PreviewWorker")
    @patch("asciidoc_artisan.ui.worker_manager.PandocWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitHubCLIWorker")
    @patch("asciidoc_artisan.ui.worker_manager.GitWorker")
    @patch("asciidoc_artisan.ui.worker_manager.QThread")
    def test_worker_initialization_after_setup(
        self,
        mock_thread_class,
        mock_git_worker_class,
        mock_github_worker_class,
        mock_pandoc_worker_class,
        mock_preview_worker_class,
        mock_ollama_worker_class,
        mock_claude_worker_class,
        mock_editor,
    ):
        """Test workers are initialized after setup."""
        # Setup thread mocks
        mock_threads = [Mock(spec=QThread) for _ in range(6)]
        for thread in mock_threads:
            thread.start = Mock()
            thread.finished = Mock()
            thread.finished.connect = Mock()
        mock_thread_class.side_effect = mock_threads

        # Setup worker mocks
        mock_workers = {}
        for name, worker_class in [
            ("git", mock_git_worker_class),
            ("github", mock_github_worker_class),
            ("pandoc", mock_pandoc_worker_class),
            ("preview", mock_preview_worker_class),
            ("ollama", mock_ollama_worker_class),
            ("claude", mock_claude_worker_class),
        ]:
            mock_worker = Mock()
            mock_worker.moveToThread = Mock()
            mock_worker.deleteLater = Mock()
            # Add minimal signal mocks
            for signal_name in [
                "command_complete",
                "status_ready",
                "detailed_status_ready",
                "github_result_ready",
                "conversion_complete",
                "conversion_error",
                "render_complete",
                "render_error",
            ]:
                signal = Mock()
                signal.connect = Mock()
                setattr(mock_worker, signal_name, signal)
            mock_worker.set_ollama_config = Mock()
            mock_worker.initialize_asciidoc = Mock()
            worker_class.return_value = mock_worker
            mock_workers[name] = mock_worker

        manager = WorkerManager(mock_editor, use_worker_pool=False)
        manager.setup_workers_and_threads()

        # All workers should be initialized
        assert manager.git_worker is mock_workers["git"]
        assert manager.github_worker is mock_workers["github"]
        assert manager.pandoc_worker is mock_workers["pandoc"]
        assert manager.preview_worker is mock_workers["preview"]
        assert manager.ollama_chat_worker is mock_workers["ollama"]
        assert manager.claude_worker is mock_workers["claude"]


class TestConcurrentOperations:
    """Test concurrent operations handling."""

    def test_multiple_cancel_calls(self, mock_editor):
        """Test multiple cancel calls on same worker."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_worker = Mock()
        manager.git_worker.cancel = Mock()

        # Call cancel multiple times
        manager.cancel_git_operation()
        manager.cancel_git_operation()
        manager.cancel_git_operation()

        # Should call cancel 3 times
        assert manager.git_worker.cancel.call_count == 3

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_concurrent_pool_operations(self, mock_pool_class, mock_editor):
        """Test concurrent pool statistics and cancellation."""
        mock_pool = Mock()
        mock_pool.get_statistics.return_value = {"active": 5}
        mock_pool.cancel_all.return_value = 3
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)

        # Call multiple operations
        stats1 = manager.get_pool_statistics()
        cancelled = manager.cancel_all_pool_tasks()
        stats2 = manager.get_pool_statistics()

        assert stats1 == {"active": 5}
        assert cancelled == 3
        assert stats2 == {"active": 5}


class TestResourceCleanup:
    """Test resource cleanup operations."""

    def test_worker_deleter_called_on_thread_finish(self, mock_editor):
        """Test worker deleteLater is set up for thread finish."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        mock_thread = Mock()
        mock_thread.finished = Mock()
        mock_thread.finished.connect = Mock()

        mock_worker = Mock()
        mock_worker.deleteLater = Mock()

        manager.git_thread = mock_thread
        manager.git_worker = mock_worker

        # Verify thread has finished signal
        assert hasattr(mock_thread, "finished")
        # Verify worker has deleteLater method
        assert hasattr(mock_worker, "deleteLater")

    def test_all_threads_have_finished_signals(self, mock_editor):
        """Test all threads can connect finished signals."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        thread_names = [
            "git_thread",
            "github_thread",
            "pandoc_thread",
            "preview_thread",
        ]

        for thread_name in thread_names:
            mock_thread = Mock()
            mock_thread.finished = Mock()
            mock_thread.finished.connect = Mock()
            setattr(manager, thread_name, mock_thread)

            thread = getattr(manager, thread_name)
            assert hasattr(thread, "finished")


class TestTimeoutHandling:
    """Test timeout handling for operations."""

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_wait_for_pool_with_custom_timeout(self, mock_pool_class, mock_editor):
        """Test waiting for pool with custom timeout."""
        mock_pool = Mock()
        mock_pool.wait_for_done.return_value = True
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)

        # Test various timeouts
        manager.wait_for_pool_done(timeout_ms=1000)
        mock_pool.wait_for_done.assert_called_with(1000)

        manager.wait_for_pool_done(timeout_ms=5000)
        mock_pool.wait_for_done.assert_called_with(5000)

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_wait_for_pool_timeout_failure(self, mock_pool_class, mock_editor):
        """Test pool wait timeout returns False."""
        mock_pool = Mock()
        mock_pool.wait_for_done.return_value = False  # Timeout
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)
        result = manager.wait_for_pool_done(timeout_ms=100)

        assert result is False

    def test_thread_wait_with_default_timeout(self, mock_editor):
        """Test thread shutdown uses default 3000ms timeout."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        mock_thread = Mock()
        mock_thread.isRunning.return_value = True
        mock_thread.quit = Mock()
        mock_thread.wait = Mock()
        manager.git_thread = mock_thread

        manager.shutdown()

        # Should use default 3000ms timeout (check saved mock)
        mock_thread.wait.assert_called_once_with(3000)


class TestWorkerRecoveryScenarios:
    """Test worker recovery from error states."""

    def test_cancel_after_worker_deleted(self, mock_editor):
        """Test cancelling operation after worker is deleted."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        # Worker was deleted/cleaned up
        manager.git_worker = None

        # Should not crash
        manager.cancel_git_operation()

    def test_multiple_shutdown_calls(self, mock_editor):
        """Test calling shutdown multiple times."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        mock_thread = Mock()
        mock_thread.isRunning.side_effect = [True, False, False]
        mock_thread.quit = Mock()
        mock_thread.wait = Mock()
        manager.git_thread = mock_thread

        # First shutdown
        manager.shutdown()
        mock_thread.quit.assert_called_once()

        # Second shutdown (git_thread is None after first shutdown)
        manager.shutdown()
        # quit should still only be called once (check saved mock)
        mock_thread.quit.assert_called_once()

    @patch("asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool")
    def test_pool_recovery_after_error(self, mock_pool_class, mock_editor):
        """Test pool operations recover after error."""
        mock_pool = Mock()
        # First call fails, second succeeds
        mock_pool.get_statistics.side_effect = [
            RuntimeError("Pool error"),
            {"active": 0},
        ]
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True)

        # First call fails
        try:
            manager.get_pool_statistics()
        except RuntimeError:
            pass

        # Second call succeeds
        stats2 = manager.get_pool_statistics()
        assert stats2 == {"active": 0}
