"""
Chat Message Data Model.

Extracted from models.py for MA principle compliance.
Contains models for Ollama AI chat conversations.
"""

from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    """
    Single message in an Ollama AI chat conversation.

    Used by OllamaChatWorker and ChatManager to represent both user messages
    and AI responses in the chat history.

    Attributes:
        role: Message sender ("user" or "assistant")
        content: Message text content
        timestamp: Unix timestamp when message was created
        model: Name of Ollama model that generated this message (for assistant messages)
        context_mode: Interaction mode when message was sent

    Validation:
        - role must be "user" or "assistant"
        - content cannot be empty
        - timestamp must be non-negative
        - context_mode must be one of allowed modes

    Example:
        ```python
        import time

        # User message
        user_msg = ChatMessage(
            role="user",
            content="How do I create a table in AsciiDoc?",
            timestamp=time.time(),
            model="gnokit/improve-grammer",
            context_mode="syntax"
        )

        # AI response
        ai_msg = ChatMessage(
            role="assistant",
            content="Here's how to create a table:\\n|===\\n|Header 1 |Header 2\\n|Cell 1   |Cell 2\\n|===",
            timestamp=time.time(),
            model="gnokit/improve-grammer",
            context_mode="syntax"
        )
        ```
    """

    role: str = Field(..., description='Message sender: "user" or "assistant"')
    content: str = Field(..., description="Message text content")
    timestamp: float = Field(..., description="Unix timestamp when message was created")
    model: str = Field(..., description="Ollama model name (e.g., gnokit/improve-grammer)")
    context_mode: str = Field(..., description='Context mode: "document", "syntax", "general", or "editing"')

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is either user or assistant."""
        allowed_roles = {"user", "assistant"}
        if v not in allowed_roles:
            raise ValueError(f"role must be one of {allowed_roles}, got '{v}'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        """Ensure timestamp is non-negative."""
        if v < 0:
            raise ValueError("timestamp must be non-negative")
        return v

    @field_validator("context_mode")
    @classmethod
    def validate_context_mode(cls, v: str) -> str:
        """Validate context mode is known."""
        allowed_modes = {"document", "syntax", "general", "editing"}
        if v not in allowed_modes:
            raise ValueError(f"context_mode must be one of {allowed_modes}, got '{v}'")
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }
