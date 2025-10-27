#!/usr/bin/env python3
"""
Test script for the Legendary Grammar System.

This script tests the complete grammar checking system independently
before integration into the main application.

Usage:
    python test_grammar_system.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication

from asciidoc_artisan.core.grammar_models import GrammarSource
from asciidoc_artisan.workers import LanguageToolWorker, OllamaGrammarWorker


def test_languagetool_worker():
    """Test LanguageTool worker standalone."""
    print("\n" + "=" * 70)
    print("TEST 1: LanguageTool Worker")
    print("=" * 70)

    worker = LanguageToolWorker()

    # Wait for initialization
    initialized = False

    def on_init_complete(success):
        nonlocal initialized
        initialized = success
        print(f"✅ Initialization: {'SUCCESS' if success else 'FAILED'}")

    def on_result(result):
        print(f"\n📊 Result:")
        print(f"   Success: {result.success}")
        print(f"   Suggestions: {result.suggestion_count}")
        print(f"   Processing time: {result.processing_time_ms}ms")
        print(f"   Word count: {result.word_count}")
        print(f"   Cached: {result.cached}")

        if result.suggestions:
            print(f"\n   Issues found:")
            for i, sugg in enumerate(result.suggestions[:3], 1):
                print(f"   {i}. [{sugg.start}:{sugg.end}] {sugg.message}")
                if sugg.replacements:
                    print(f"      → Suggestion: {sugg.replacements[0]}")

        QCoreApplication.quit()

    worker.initialization_complete.connect(on_init_complete)
    worker.grammar_result_ready.connect(on_result)

    # Initialize
    worker.initialize_tool("en-US")

    # Wait for initialization
    QTimer.singleShot(2000, lambda: check_initialization(worker, initialized))

    def check_initialization(w, init):
        if not init:
            print("❌ Initialization timeout")
            QCoreApplication.quit()
            return

        # Test text with errors
        test_text = """
        This is a example of text with some error in it.
        There is many grammar mistake here.
        Its important to check this carefully.
        """

        print(f"\n📝 Checking text ({len(test_text)} chars)...")
        w.check_text(test_text)


def test_ollama_worker():
    """Test Ollama worker standalone."""
    print("\n" + "=" * 70)
    print("TEST 2: Ollama Grammar Worker")
    print("=" * 70)

    worker = OllamaGrammarWorker()

    def on_result(result):
        print(f"\n📊 Result:")
        print(f"   Success: {result.success}")
        print(f"   Source: {result.source}")
        print(f"   Suggestions: {result.suggestion_count}")
        print(f"   Processing time: {result.processing_time_ms}ms")
        print(f"   Model: {result.model_name}")

        if result.error_message:
            print(f"   Error: {result.error_message}")

        if result.suggestions:
            print(f"\n   AI Suggestions:")
            for i, sugg in enumerate(result.suggestions[:3], 1):
                print(f"   {i}. {sugg.message}")
                if sugg.replacements:
                    print(f"      → {sugg.replacements[0]}")

        QCoreApplication.quit()

    worker.grammar_result_ready.connect(on_result)

    # Configure
    worker.set_config(True, "gnokit/improve-grammar")
    worker.set_prompt_style("structured")

    # Test text
    test_text = """
    This text have some grammar errors that need fixing.
    The sentences is not structured very good.
    """

    print(f"\n📝 Checking with Ollama ({len(test_text)} chars)...")
    print("   (This may take 2-3 seconds...)")

    worker.check_text(test_text)


def test_worker_statistics():
    """Test worker statistics."""
    print("\n" + "=" * 70)
    print("TEST 3: Worker Statistics")
    print("=" * 70)

    worker = LanguageToolWorker()

    def on_init(_):
        # Run multiple checks
        texts = [
            "This is a test.",
            "Another test with a error.",
            "The third test have mistakes.",
        ]

        for text in texts:
            worker.check_text(text)

        # Wait a bit
        QTimer.singleShot(2000, show_stats)

    def show_stats():
        stats = worker.get_statistics()
        print("\n📊 Statistics:")
        print(f"   Total checks: {stats['total_checks']}")
        print(f"   Total suggestions: {stats['total_suggestions']}")
        print(f"   Avg time: {stats['avg_processing_time_ms']:.1f}ms")
        print(f"   Cache size: {stats['cache_size']}")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"   Circuit breaker open: {stats['circuit_breaker_open']}")

        QCoreApplication.quit()

    worker.initialization_complete.connect(on_init)
    worker.initialize_tool("en-US")


def main():
    """Run all tests."""
    print("\n🏆 LEGENDARY GRAMMAR SYSTEM - Test Suite")
    print("=" * 70)

    app = QCoreApplication(sys.argv)

    # Choose test
    print("\nAvailable tests:")
    print("1. LanguageTool Worker")
    print("2. Ollama Worker")
    print("3. Worker Statistics")
    print("4. All tests")

    try:
        choice = input("\nSelect test (1-4): ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "1"  # Default

    print()

    if choice == "1":
        test_languagetool_worker()
    elif choice == "2":
        test_ollama_worker()
    elif choice == "3":
        test_worker_statistics()
    elif choice == "4":
        # Run all sequentially
        print("Running all tests sequentially...")
        test_languagetool_worker()
        app.exec()
        app = QCoreApplication(sys.argv)
        test_ollama_worker()
        app.exec()
        app = QCoreApplication(sys.argv)
        test_worker_statistics()
    else:
        print("Invalid choice, running test 1")
        test_languagetool_worker()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
