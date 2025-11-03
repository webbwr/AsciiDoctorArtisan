"""
Tests for ui.worker_manager module.

Tests worker thread lifecycle management including:
- Worker manager initialization
- Worker pool setup
- Thread creation and signal connections
- Cancellation operations
- Shutdown procedures
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
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

    @patch('asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool')
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

    @patch('asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool')
    def test_initialization_with_pool_custom_threads(self, mock_pool_class, mock_editor):
        """Test WorkerManager initializes pool with custom thread count."""
        mock_pool = Mock()
        mock_pool_class.return_value = mock_pool

        manager = WorkerManager(mock_editor, use_worker_pool=True, max_pool_threads=8)

        mock_pool_class.assert_called_once_with(max_threads=8)
        assert manager.worker_pool is mock_pool


class TestSetupWorkersAndThreads:
    """Test worker and thread setup."""

    @patch('asciidoc_artisan.ui.worker_manager.ClaudeWorker')
    @patch('asciidoc_artisan.ui.worker_manager.OllamaChatWorker')
    @patch('asciidoc_artisan.ui.worker_manager.PreviewWorker')
    @patch('asciidoc_artisan.ui.worker_manager.PandocWorker')
    @patch('asciidoc_artisan.ui.worker_manager.GitHubCLIWorker')
    @patch('asciidoc_artisan.ui.worker_manager.GitWorker')
    @patch('asciidoc_artisan.ui.worker_manager.QThread')
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

    @patch('asciidoc_artisan.ui.worker_manager.ClaudeWorker')
    @patch('asciidoc_artisan.ui.worker_manager.OllamaChatWorker')
    @patch('asciidoc_artisan.ui.worker_manager.PreviewWorker')
    @patch('asciidoc_artisan.ui.worker_manager.PandocWorker')
    @patch('asciidoc_artisan.ui.worker_manager.GitHubCLIWorker')
    @patch('asciidoc_artisan.ui.worker_manager.GitWorker')
    @patch('asciidoc_artisan.ui.worker_manager.QThread')
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

    @patch('asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool')
    def test_get_pool_statistics_with_pool(self, mock_pool_class, mock_editor):
        """Test getting pool statistics when pool is enabled."""
        mock_pool = Mock()
        mock_pool.get_statistics.return_value = {"active_threads": 2, "pending_tasks": 5}
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

    @patch('asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool')
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

    @patch('asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool')
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

    @patch('asciidoc_artisan.ui.worker_manager.OptimizedWorkerPool')
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
        manager.git_thread = Mock()
        manager.git_thread.isRunning.return_value = True
        manager.git_thread.quit = Mock()
        manager.git_thread.wait = Mock()

        manager.shutdown()

        manager.git_thread.quit.assert_called_once()
        manager.git_thread.wait.assert_called_once_with(2000)

    def test_shutdown_stops_all_threads(self, mock_editor):
        """Test shutdown stops all running threads."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        # Mock all threads as running
        threads = [
            'git_thread',
            'github_thread',
            'pandoc_thread',
            'preview_thread',
        ]

        for thread_name in threads:
            thread = Mock()
            thread.isRunning.return_value = True
            thread.quit = Mock()
            thread.wait = Mock()
            setattr(manager, thread_name, thread)

        manager.shutdown()

        # Verify all threads were stopped
        for thread_name in threads:
            thread = getattr(manager, thread_name)
            thread.quit.assert_called_once()
            thread.wait.assert_called_once_with(2000)

    def test_shutdown_skips_stopped_threads(self, mock_editor):
        """Test shutdown skips threads that are not running."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_thread = Mock()
        manager.git_thread.isRunning.return_value = False
        manager.git_thread.quit = Mock()

        manager.shutdown()

        # Should not call quit on stopped thread
        manager.git_thread.quit.assert_not_called()

    def test_shutdown_handles_none_threads(self, mock_editor):
        """Test shutdown handles None threads gracefully."""
        manager = WorkerManager(mock_editor, use_worker_pool=False)

        manager.git_thread = None
        manager.github_thread = None
        manager.pandoc_thread = None
        manager.preview_thread = None

        # Should not crash
        manager.shutdown()
