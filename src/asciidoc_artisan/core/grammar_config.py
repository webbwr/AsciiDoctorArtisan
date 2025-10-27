"""
Grammar Configuration - Constants and settings for grammar checking system.

This module provides centralized configuration management for the hybrid
grammar checking system.

Implements:
- FR-066: Grammar checking configuration
- FR-067: Performance tuning constants
- FR-068: AsciiDoc content filtering rules

Architecture:
- Centralized constants
- Type-safe configuration
- Environment-aware settings
- Performance profiles

Author: AsciiDoc Artisan Development Team
Version: 1.3.0
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Pattern, Set


# ============================================================================
# PERFORMANCE CONSTANTS
# ============================================================================

# Debounce timers (milliseconds)
LANGUAGETOOL_DEBOUNCE_MS = 500      # Fast: LanguageTool is quick
OLLAMA_DEBOUNCE_MS = 2000           # Slow: Give Ollama time
HYBRID_DEBOUNCE_MS = 500            # Start with LanguageTool, Ollama follows

# Processing timeouts (milliseconds)
LANGUAGETOOL_TIMEOUT_MS = 5000      # 5 seconds max for LanguageTool
OLLAMA_TIMEOUT_MS = 30000           # 30 seconds max for Ollama AI

# Cache settings
LANGUAGETOOL_CACHE_SIZE = 100       # Store 100 recent checks
OLLAMA_CACHE_SIZE = 20              # Store 20 recent AI checks (memory-intensive)
CACHE_TTL_SECONDS = 3600            # Cache expires after 1 hour

# Document size thresholds
SMALL_DOCUMENT_CHARS = 1000         # < 1K chars
MEDIUM_DOCUMENT_CHARS = 5000        # 1K-5K chars
LARGE_DOCUMENT_CHARS = 20000        # 5K-20K chars
HUGE_DOCUMENT_CHARS = 50000         # > 20K chars

# Chunk processing for large documents
MAX_CHUNK_SIZE_CHARS = 10000        # Max 10K chars per chunk
MIN_CHUNK_SIZE_CHARS = 1000         # Min 1K chars per chunk
CHUNK_OVERLAP_CHARS = 200           # 200 char overlap between chunks


# ============================================================================
# LANGUAGETOOL CONFIGURATION
# ============================================================================

# Supported languages
LANGUAGETOOL_LANGUAGES = {
    "en-US": "English (US)",
    "en-GB": "English (UK)",
    "en-CA": "English (Canada)",
    "en-AU": "English (Australia)",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "it": "Italian",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "zh-CN": "Chinese (Simplified)",
    "ja": "Japanese",
}

# Default language
LANGUAGETOOL_DEFAULT_LANGUAGE = "en-US"

# LanguageTool server settings
LANGUAGETOOL_SERVER_PORT = 8081     # Default port (if running standalone)
LANGUAGETOOL_MAX_TEXT_LENGTH = 50000  # Max 50K chars per request

# Rules to disable by default (noisy/low-value rules)
LANGUAGETOOL_DISABLED_RULES_DEFAULT: Set[str] = {
    "WHITESPACE_RULE",               # Too many false positives in code
    "EN_QUOTES",                     # AsciiDoc has its own quoting rules
    "DOUBLE_PUNCTUATION",            # Sometimes intentional in examples
}


# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================

# Supported grammar models (pre-configured)
OLLAMA_GRAMMAR_MODELS = {
    "gnokit/improve-grammar": {
        "name": "Improve Grammar (Gemma 2B)",
        "size": "1.6GB",
        "speed": "fast",
        "quality": "good",
        "description": "Lightweight model for basic grammar improvements",
    },
    "ifioravanti/mistral-grammar-checker": {
        "name": "Mistral Grammar Checker (7B)",
        "size": "4.1GB",
        "speed": "medium",
        "quality": "excellent",
        "description": "High-quality grammar and style checking",
    },
    "pdevine/grammarfix": {
        "name": "Grammar Fix",
        "size": "varies",
        "speed": "medium",
        "quality": "good",
        "description": "General grammar fixing model",
    },
}

# Default Ollama model
OLLAMA_DEFAULT_MODEL = "gnokit/improve-grammar"

# Ollama API settings
OLLAMA_API_BASE_URL = "http://localhost:11434"  # Default Ollama server
OLLAMA_MAX_RETRIES = 3                          # Retry failed requests
OLLAMA_RETRY_DELAY_MS = 1000                    # 1 second between retries


# ============================================================================
# ASCIIDOC CONTENT FILTERING
# ============================================================================

# Patterns to exclude from grammar checking (compiled regexes)
ASCIIDOC_EXCLUDE_PATTERNS: List[Pattern] = [
    # Document attributes
    re.compile(r'^:[\w-]+:.*$', re.MULTILINE),

    # Comments
    re.compile(r'^//.*$', re.MULTILINE),
    re.compile(r'////.*?////', re.DOTALL),

    # Block attributes
    re.compile(r'^\[.*?\]$', re.MULTILINE),

    # Code blocks (listing blocks)
    re.compile(r'^----\n.*?\n----$', re.MULTILINE | re.DOTALL),
    re.compile(r'^====\n.*?\n====$', re.MULTILINE | re.DOTALL),

    # Literal blocks
    re.compile(r'^\.\.\.\.\n.*?\n\.\.\.\.$', re.MULTILINE | re.DOTALL),

    # Source code blocks
    re.compile(r'^\[source,.*?\]\n----\n.*?\n----$', re.MULTILINE | re.DOTALL),

    # Inline code
    re.compile(r'`[^`]+`'),
    re.compile(r'\+[^+]+\+'),

    # Inline pass-through
    re.compile(r'\+\+\+.*?\+\+\+'),
    re.compile(r'\$\$.*?\$\$'),

    # Block macros
    re.compile(r'^(image|video|audio|include)::.*?\[.*?\]$', re.MULTILINE),

    # Inline macros
    re.compile(r'(image|icon|kbd|btn|menu):.*?\[.*?\]'),

    # URLs and emails
    re.compile(r'https?://\S+'),
    re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b'),

    # Anchor IDs
    re.compile(r'\[\[.*?\]\]'),
    re.compile(r'\[#.*?\]'),
]

# Content that should be preserved but marked for special handling
ASCIIDOC_SPECIAL_CONTEXTS = {
    "code": r'`[^`]+`',
    "emphasis": r'_[^_]+_',
    "strong": r'\*[^*]+\*',
    "monospace": r'`[^`]+`',
}


# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Underline styles
class UnderlineStyle(Enum):
    """Visual styles for grammar underlines."""
    WAVE = "wave"           # Wavy underline (default)
    DOT = "dot"             # Dotted underline
    DASH = "dash"           # Dashed underline
    SINGLE = "single"       # Single solid underline


# Default underline style
DEFAULT_UNDERLINE_STYLE = UnderlineStyle.WAVE

# Tooltip delay (milliseconds)
TOOLTIP_DELAY_MS = 500

# Grammar panel settings
GRAMMAR_PANEL_DEFAULT_WIDTH = 300
GRAMMAR_PANEL_MIN_WIDTH = 200
GRAMMAR_PANEL_MAX_WIDTH = 600


# ============================================================================
# PERFORMANCE PROFILES
# ============================================================================

@dataclass
class PerformanceProfile:
    """Performance profile for grammar checking.

    Defines timing and behavior parameters for different performance levels.
    """

    name: str
    languagetool_debounce_ms: int
    ollama_debounce_ms: int
    ollama_enabled: bool
    cache_enabled: bool
    chunk_large_documents: bool
    max_suggestions: int = 100  # Limit displayed suggestions


# Predefined performance profiles
PERFORMANCE_PROFILES = {
    "realtime": PerformanceProfile(
        name="Real-time (Fastest)",
        languagetool_debounce_ms=300,
        ollama_debounce_ms=0,  # Disabled
        ollama_enabled=False,
        cache_enabled=True,
        chunk_large_documents=True,
        max_suggestions=50,
    ),
    "balanced": PerformanceProfile(
        name="Balanced (Recommended)",
        languagetool_debounce_ms=500,
        ollama_debounce_ms=2000,
        ollama_enabled=True,
        cache_enabled=True,
        chunk_large_documents=True,
        max_suggestions=100,
    ),
    "thorough": PerformanceProfile(
        name="Thorough (Most Accurate)",
        languagetool_debounce_ms=1000,
        ollama_debounce_ms=3000,
        ollama_enabled=True,
        cache_enabled=False,  # Always fresh check
        chunk_large_documents=False,  # Check entire doc
        max_suggestions=200,
    ),
}

DEFAULT_PERFORMANCE_PROFILE = "balanced"


# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    "languagetool_not_installed": (
        "LanguageTool library not found. "
        "Install with: pip install language-tool-python"
    ),
    "languagetool_init_failed": (
        "Failed to initialize LanguageTool server. "
        "Ensure Java 8+ is installed."
    ),
    "ollama_not_installed": (
        "Ollama library not found. "
        "Install with: pip install ollama"
    ),
    "ollama_service_down": (
        "Ollama service not running. "
        "Start with: ollama serve"
    ),
    "ollama_model_not_found": (
        "Ollama model not found. "
        "Pull with: ollama pull {model}"
    ),
    "document_too_large": (
        "Document exceeds maximum size ({max_size} chars). "
        "Grammar checking may be slow or incomplete."
    ),
    "check_timeout": (
        "Grammar check timed out after {timeout}ms. "
        "Try checking a smaller section."
    ),
}


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log levels for different components
LOG_LEVELS = {
    "grammar_manager": "INFO",
    "languagetool_worker": "INFO",
    "ollama_worker": "INFO",
    "cache": "DEBUG",
    "filter": "DEBUG",
}

# Log message formats
LOG_FORMAT_SHORT = "[%(levelname)s] %(name)s: %(message)s"
LOG_FORMAT_DETAILED = (
    "[%(asctime)s] [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_cache_dir() -> Path:
    """Get platform-specific cache directory for grammar data.

    Returns:
        Path to cache directory (creates if doesn't exist)
    """
    import platform

    if platform.system() == "Windows":
        cache_dir = Path.home() / "AppData" / "Local" / "AsciiDocArtisan" / "Grammar"
    elif platform.system() == "Darwin":  # macOS
        cache_dir = Path.home() / "Library" / "Caches" / "AsciiDocArtisan" / "Grammar"
    else:  # Linux and others
        cache_dir = Path.home() / ".cache" / "asciidoc-artisan" / "grammar"

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def estimate_processing_time(char_count: int, use_ollama: bool = False) -> int:
    """Estimate processing time for a document.

    Args:
        char_count: Number of characters in document
        use_ollama: Whether Ollama AI will be used

    Returns:
        Estimated time in milliseconds
    """
    # LanguageTool: ~10ms per 1000 chars
    lt_time = (char_count / 1000) * 10

    # Ollama: ~500ms per 1000 chars (much slower)
    ollama_time = (char_count / 1000) * 500 if use_ollama else 0

    # Overhead
    overhead = 100

    return int(lt_time + ollama_time + overhead)


def should_chunk_document(char_count: int) -> bool:
    """Determine if document should be chunked for processing.

    Args:
        char_count: Number of characters in document

    Returns:
        True if document should be chunked
    """
    return char_count > LARGE_DOCUMENT_CHARS


def calculate_chunk_size(char_count: int) -> int:
    """Calculate optimal chunk size for a document.

    Args:
        char_count: Total document characters

    Returns:
        Chunk size in characters
    """
    if char_count <= LARGE_DOCUMENT_CHARS:
        return char_count  # Don't chunk

    # Target 3-5 chunks for huge documents
    if char_count > HUGE_DOCUMENT_CHARS:
        return char_count // 5

    # Use standard chunk size
    return MAX_CHUNK_SIZE_CHARS


# ============================================================================
# VERSION INFO
# ============================================================================

GRAMMAR_SYSTEM_VERSION = "1.3.0"
GRAMMAR_SYSTEM_NAME = "Legendary Grammar System"
GRAMMAR_SYSTEM_CODENAME = "Grandmaster"
