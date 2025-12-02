"""
Core data models for AsciiDoc Artisan.

This module re-exports model classes from their individual modules
for backward compatibility after MA principle extraction.

Model classes by domain:
- Git: GitResult, GitStatus, GitHubResult (git_models.py)
- Chat: ChatMessage (chat_models.py)
- Completion: CompletionKind, CompletionItem, CompletionContext (completion_models.py)
- Syntax: ErrorSeverity, TextEdit, QuickFix, SyntaxErrorModel (syntax_models.py)
- Template: TemplateVariable, Template (template_models.py)
"""

# Re-export all model classes for backward compatibility
from asciidoc_artisan.core.chat_models import ChatMessage
from asciidoc_artisan.core.completion_models import (
    CompletionContext,
    CompletionItem,
    CompletionKind,
)
from asciidoc_artisan.core.git_models import GitHubResult, GitResult, GitStatus
from asciidoc_artisan.core.syntax_models import (
    ErrorSeverity,
    QuickFix,
    SyntaxErrorModel,
    TextEdit,
)
from asciidoc_artisan.core.template_models import Template, TemplateVariable

__all__ = [
    # Git models
    "GitResult",
    "GitStatus",
    "GitHubResult",
    # Chat models
    "ChatMessage",
    # Completion models (v2.0.0+)
    "CompletionKind",
    "CompletionItem",
    "CompletionContext",
    # Syntax models (v2.0.0+)
    "ErrorSeverity",
    "TextEdit",
    "QuickFix",
    "SyntaxErrorModel",
    # Template models (v2.0.0+)
    "TemplateVariable",
    "Template",
]
