"""
Tests for AsciiDoc LSP document state manager.

Tests cover:
- Document open/close/update operations
- Thread safety
- Version tracking
"""

import pytest

from asciidoc_artisan.lsp.document_state import DocumentState


@pytest.fixture
def state() -> DocumentState:
    """Create document state instance."""
    return DocumentState()


class TestDocumentOperations:
    """Test document lifecycle operations."""

    def test_open_document(self, state: DocumentState) -> None:
        """Test opening a document."""
        uri = "file:///test.adoc"
        text = "= Title\n"
        version = 1

        state.open_document(uri, text, version)

        assert state.has_document(uri)
        assert state.get_document(uri) == text
        assert state.get_version(uri) == version

    def test_update_document(self, state: DocumentState) -> None:
        """Test updating document content."""
        uri = "file:///test.adoc"

        state.open_document(uri, "= Old Title\n", 1)
        state.update_document(uri, "= New Title\n", 2)

        assert state.get_document(uri) == "= New Title\n"
        assert state.get_version(uri) == 2

    def test_close_document(self, state: DocumentState) -> None:
        """Test closing a document."""
        uri = "file:///test.adoc"

        state.open_document(uri, "= Title\n", 1)
        state.close_document(uri)

        assert not state.has_document(uri)
        assert state.get_document(uri) is None

    def test_auto_open_on_update(self, state: DocumentState) -> None:
        """Test updating unopened document auto-opens it."""
        uri = "file:///test.adoc"

        # Update without opening first
        state.update_document(uri, "= Title\n", 1)

        # Should auto-open
        assert state.has_document(uri)
        assert state.get_document(uri) == "= Title\n"


class TestMultipleDocuments:
    """Test handling multiple documents."""

    def test_multiple_documents(self, state: DocumentState) -> None:
        """Test managing multiple documents."""
        state.open_document("file:///a.adoc", "= A\n", 1)
        state.open_document("file:///b.adoc", "= B\n", 1)
        state.open_document("file:///c.adoc", "= C\n", 1)

        assert len(state.get_all_uris()) == 3
        assert state.get_document("file:///a.adoc") == "= A\n"
        assert state.get_document("file:///b.adoc") == "= B\n"
        assert state.get_document("file:///c.adoc") == "= C\n"

    def test_get_all_uris(self, state: DocumentState) -> None:
        """Test getting all document URIs."""
        state.open_document("file:///a.adoc", "= A\n", 1)
        state.open_document("file:///b.adoc", "= B\n", 1)

        uris = state.get_all_uris()

        assert "file:///a.adoc" in uris
        assert "file:///b.adoc" in uris


class TestEdgeCases:
    """Test edge cases."""

    def test_get_nonexistent_document(self, state: DocumentState) -> None:
        """Test getting document that doesn't exist."""
        result = state.get_document("file:///nonexistent.adoc")
        assert result is None

    def test_get_version_nonexistent(self, state: DocumentState) -> None:
        """Test getting version of nonexistent document."""
        result = state.get_version("file:///nonexistent.adoc")
        assert result is None

    def test_close_nonexistent_document(self, state: DocumentState) -> None:
        """Test closing nonexistent document doesn't crash."""
        # Should not raise exception
        state.close_document("file:///nonexistent.adoc")

    def test_empty_document(self, state: DocumentState) -> None:
        """Test handling empty document."""
        uri = "file:///empty.adoc"

        state.open_document(uri, "", 1)

        assert state.has_document(uri)
        assert state.get_document(uri) == ""


class TestThreadSafety:
    """Test thread safety."""

    def test_concurrent_access(self, state: DocumentState) -> None:
        """Test concurrent document access."""
        import threading

        uri = "file:///test.adoc"
        state.open_document(uri, "= Initial\n", 1)

        errors = []

        def update_document(version: int) -> None:
            try:
                state.update_document(uri, f"= Version {version}\n", version)
            except Exception as e:
                errors.append(e)

        def read_document() -> None:
            try:
                _ = state.get_document(uri)
            except Exception as e:
                errors.append(e)

        # Create multiple threads for updates and reads
        threads = []
        for i in range(10):
            threads.append(threading.Thread(target=update_document, args=(i,)))
            threads.append(threading.Thread(target=read_document))

        # Run all threads
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete without errors
        assert len(errors) == 0
