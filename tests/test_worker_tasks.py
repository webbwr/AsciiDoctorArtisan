"""Tests for workers.worker_tasks module."""

import pytest
from unittest.mock import Mock


class TestWorkerTasks:
    """Test suite for worker task definitions."""

    def test_import_render_task(self):
        from asciidoc_artisan.workers.worker_tasks import RenderTask
        assert RenderTask is not None

    def test_import_task_signals(self):
        from asciidoc_artisan.workers.worker_tasks import TaskSignals
        assert TaskSignals is not None

    def test_task_signals_has_signals(self):
        from asciidoc_artisan.workers.worker_tasks import TaskSignals
        signals = TaskSignals()
        assert hasattr(signals, "started")
        assert hasattr(signals, "finished")
        assert hasattr(signals, "error")
        assert hasattr(signals, "cancelled")

    def test_render_task_creation(self):
        from asciidoc_artisan.workers.worker_tasks import RenderTask

        # Create a mock renderer
        mock_renderer = Mock()
        mock_renderer.render_to_html.return_value = "<html>Test</html>"

        task = RenderTask("Test content", mock_renderer)
        assert task is not None
        assert hasattr(task, "run")
