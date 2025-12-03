"""
Document State Manager for LSP server.

MA principle: ~80 lines focused on document content management.

Manages open documents and their content for the LSP server.
Provides efficient access to document text for feature providers.
"""

import logging
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents an open document."""

    uri: str
    text: str
    version: int


class DocumentState:
    """
    Thread-safe document state manager.

    Stores open document content for LSP feature providers.
    Uses a lock for thread safety as LSP handlers run concurrently.

    Attributes:
        _documents: Map of URI to Document
        _lock: Threading lock for safe access
    """

    def __init__(self) -> None:
        """Initialize document state."""
        self._documents: dict[str, Document] = {}
        self._lock = threading.Lock()

    def open_document(self, uri: str, text: str, version: int) -> None:
        """
        Register an opened document.

        Args:
            uri: Document URI
            text: Document content
            version: Document version
        """
        with self._lock:
            self._documents[uri] = Document(uri=uri, text=text, version=version)
            logger.debug(f"Opened document: {uri} (v{version})")

    def update_document(self, uri: str, text: str, version: int) -> None:
        """
        Update document content.

        Args:
            uri: Document URI
            text: New content
            version: New version
        """
        with self._lock:
            if uri in self._documents:
                self._documents[uri] = Document(uri=uri, text=text, version=version)
                logger.debug(f"Updated document: {uri} (v{version})")
            else:
                # Auto-open if not tracked
                self._documents[uri] = Document(uri=uri, text=text, version=version)
                logger.debug(f"Auto-opened document: {uri} (v{version})")

    def close_document(self, uri: str) -> None:
        """
        Remove a closed document.

        Args:
            uri: Document URI
        """
        with self._lock:
            if uri in self._documents:
                del self._documents[uri]
                logger.debug(f"Closed document: {uri}")

    def get_document(self, uri: str) -> str | None:
        """
        Get document content.

        Args:
            uri: Document URI

        Returns:
            Document text or None if not found
        """
        with self._lock:
            doc = self._documents.get(uri)
            return doc.text if doc else None

    def get_version(self, uri: str) -> int | None:
        """
        Get document version.

        Args:
            uri: Document URI

        Returns:
            Document version or None if not found
        """
        with self._lock:
            doc = self._documents.get(uri)
            return doc.version if doc else None

    def has_document(self, uri: str) -> bool:
        """
        Check if document is open.

        Args:
            uri: Document URI

        Returns:
            True if document is tracked
        """
        with self._lock:
            return uri in self._documents

    def get_all_uris(self) -> list[str]:
        """
        Get all open document URIs.

        Returns:
            List of document URIs
        """
        with self._lock:
            return list(self._documents.keys())
