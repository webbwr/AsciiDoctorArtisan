"""
Integration tests for grammar checking workers.
"""

import pytest
from PySide6.QtCore import QCoreApplication, QTimer

from asciidoc_artisan.core import CheckingMode, GrammarConfig, GrammarResult
from asciidoc_artisan.workers import LanguageToolWorker, OllamaGrammarWorker


@pytest.fixture
def qapp():
    """Provide Qt application instance for worker tests."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.mark.integration
class TestLanguageToolWorker:
    """Test LanguageTool worker integration."""

    def test_worker_initialization(self, qapp, qtbot):
        """Test LanguageTool worker initializes."""
        worker = LanguageToolWorker()

        assert worker is not None
        assert not worker.isRunning()

    def test_worker_can_start(self, qapp, qtbot):
        """Test worker can be started."""
        worker = LanguageToolWorker()

        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        assert worker.isRunning()

        worker.quit()
        worker.wait(2000)

    def test_check_simple_text(self, qapp, qtbot):
        """Test checking simple text with intentional error."""
        worker = LanguageToolWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        # Text with grammar error
        test_text = "This is a test text with an mistake."

        result_received = []

        def on_result(result):
            result_received.append(result)

        worker.check_result.connect(on_result)

        # Request check
        worker.request_check.emit(test_text, "en-US")

        # Wait for result (with longer timeout for LanguageTool initialization)
        qtbot.waitUntil(lambda: len(result_received) > 0, timeout=10000)

        result = result_received[0]
        assert isinstance(result, GrammarResult)
        assert result.success is True
        assert result.word_count > 0

        worker.quit()
        worker.wait(2000)

    def test_check_clean_text(self, qapp, qtbot):
        """Test checking grammatically correct text."""
        worker = LanguageToolWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        test_text = "This is a perfectly correct sentence."

        result_received = []

        def on_result(result):
            result_received.append(result)

        worker.check_result.connect(on_result)
        worker.request_check.emit(test_text, "en-US")

        qtbot.waitUntil(lambda: len(result_received) > 0, timeout=10000)

        result = result_received[0]
        assert isinstance(result, GrammarResult)
        assert result.success is True
        assert result.word_count == 6

        worker.quit()
        worker.wait(2000)

    def test_initialization_signal(self, qapp, qtbot):
        """Test worker emits initialization complete signal."""
        worker = LanguageToolWorker()

        init_results = []

        def on_init(success):
            init_results.append(success)

        worker.initialization_complete.connect(on_init)
        worker.start()

        # Wait for initialization
        qtbot.waitUntil(lambda: len(init_results) > 0, timeout=10000)

        assert len(init_results) == 1
        # May be True or False depending on LanguageTool availability

        worker.quit()
        worker.wait(2000)

    def test_empty_text_handling(self, qapp, qtbot):
        """Test worker handles empty text gracefully."""
        worker = LanguageToolWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        result_received = []

        def on_result(result):
            result_received.append(result)

        worker.check_result.connect(on_result)
        worker.request_check.emit("", "en-US")

        qtbot.waitUntil(lambda: len(result_received) > 0, timeout=5000)

        result = result_received[0]
        assert isinstance(result, GrammarResult)
        assert result.word_count == 0

        worker.quit()
        worker.wait(2000)


@pytest.mark.integration
class TestOllamaGrammarWorker:
    """Test Ollama AI grammar worker integration."""

    def test_worker_initialization(self, qapp, qtbot):
        """Test Ollama worker initializes."""
        worker = OllamaGrammarWorker()

        assert worker is not None
        assert not worker.isRunning()

    def test_worker_can_start(self, qapp, qtbot):
        """Test Ollama worker can be started."""
        worker = OllamaGrammarWorker()

        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        assert worker.isRunning()

        worker.quit()
        worker.wait(2000)

    def test_initialization_signal(self, qapp, qtbot):
        """Test Ollama worker emits initialization signal."""
        worker = OllamaGrammarWorker()

        init_results = []

        def on_init(success):
            init_results.append(success)

        worker.initialization_complete.connect(on_init)
        worker.start()

        # Wait for initialization (may be slow if downloading model)
        qtbot.waitUntil(lambda: len(init_results) > 0, timeout=30000)

        assert len(init_results) == 1
        # May be False if Ollama not installed/configured

        worker.quit()
        worker.wait(2000)

    @pytest.mark.slow
    def test_check_text_if_available(self, qapp, qtbot):
        """Test checking text with Ollama if available."""
        worker = OllamaGrammarWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        test_text = "This sentence could be improved for clarity."

        result_received = []

        def on_result(result):
            result_received.append(result)

        worker.check_result.connect(on_result)
        worker.request_check.emit(test_text, "en-US")

        # Wait for result (Ollama can be slow)
        qtbot.waitUntil(lambda: len(result_received) > 0, timeout=30000)

        result = result_received[0]
        assert isinstance(result, GrammarResult)
        # Success depends on Ollama availability
        if result.success:
            assert result.word_count > 0

        worker.quit()
        worker.wait(2000)


@pytest.mark.integration
class TestWorkerCleanup:
    """Test worker cleanup and resource management."""

    def test_languagetool_worker_cleanup(self, qapp, qtbot):
        """Test LanguageTool worker cleans up properly."""
        worker = LanguageToolWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        # Stop worker
        worker.quit()
        success = worker.wait(5000)

        assert success
        assert not worker.isRunning()

    def test_ollama_worker_cleanup(self, qapp, qtbot):
        """Test Ollama worker cleans up properly."""
        worker = OllamaGrammarWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        # Stop worker
        worker.quit()
        success = worker.wait(5000)

        assert success
        assert not worker.isRunning()

    def test_multiple_workers_can_coexist(self, qapp, qtbot):
        """Test multiple workers can run simultaneously."""
        lt_worker = LanguageToolWorker()
        ollama_worker = OllamaGrammarWorker()

        lt_worker.start()
        ollama_worker.start()

        qtbot.waitUntil(lambda: lt_worker.isRunning(), timeout=2000)
        qtbot.waitUntil(lambda: ollama_worker.isRunning(), timeout=2000)

        assert lt_worker.isRunning()
        assert ollama_worker.isRunning()

        # Cleanup
        lt_worker.quit()
        ollama_worker.quit()
        lt_worker.wait(2000)
        ollama_worker.wait(2000)


@pytest.mark.integration
class TestWorkerErrorHandling:
    """Test worker error handling."""

    def test_invalid_language_code(self, qapp, qtbot):
        """Test worker handles invalid language code."""
        worker = LanguageToolWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        result_received = []

        def on_result(result):
            result_received.append(result)

        worker.check_result.connect(on_result)
        worker.request_check.emit("Test text", "invalid-lang")

        qtbot.waitUntil(lambda: len(result_received) > 0, timeout=5000)

        result = result_received[0]
        assert isinstance(result, GrammarResult)
        # Should handle gracefully (either fallback or error)

        worker.quit()
        worker.wait(2000)

    def test_very_long_text(self, qapp, qtbot):
        """Test worker handles very long text."""
        worker = LanguageToolWorker()
        worker.start()
        qtbot.waitUntil(lambda: worker.isRunning(), timeout=2000)

        # Generate long text
        long_text = "This is a sentence. " * 1000  # ~20KB

        result_received = []

        def on_result(result):
            result_received.append(result)

        worker.check_result.connect(on_result)
        worker.request_check.emit(long_text, "en-US")

        qtbot.waitUntil(lambda: len(result_received) > 0, timeout=15000)

        result = result_received[0]
        assert isinstance(result, GrammarResult)
        if result.success:
            assert result.word_count > 1000

        worker.quit()
        worker.wait(2000)
