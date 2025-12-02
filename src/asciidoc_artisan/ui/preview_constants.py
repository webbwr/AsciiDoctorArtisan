"""
Preview constants for AsciiDoc Artisan.

Extracted from preview_handler_base.py for MA principle compliance.
Contains debounce intervals and Content Security Policy configuration.

DEBOUNCE INTERVALS:
These define how long to wait before updating preview.
Shorter intervals = faster updates but more CPU usage.

CONTENT SECURITY POLICY (CSP):
Security rules for preview HTML to prevent XSS attacks.
Applied to all HTML rendered in preview widget.

Example:
    ```python
    from asciidoc_artisan.ui.preview_constants import (
        PREVIEW_FAST_INTERVAL_MS,
        CSP_POLICY,
    )

    timer.start(PREVIEW_FAST_INTERVAL_MS)
    html = f'<meta http-equiv="Content-Security-Policy" content="{CSP_POLICY}">'
    ```
"""

# === DEBOUNCE INTERVAL CONSTANTS ===
# These define how long to wait before updating preview
# Shorter intervals = faster updates but more CPU usage

PREVIEW_INSTANT_MS = 0
"""Instant for tiny documents (<1KB) - zero latency!"""

PREVIEW_FAST_INTERVAL_MS = 25
"""25ms for small documents (2x faster than previous)."""

PREVIEW_NORMAL_INTERVAL_MS = 100
"""100ms for medium documents (was 150ms)."""

PREVIEW_SLOW_INTERVAL_MS = 250
"""250ms for large documents (was 300ms)."""

# === CONTENT SECURITY POLICY (CSP) ===
# Security rules for preview HTML to prevent XSS attacks
# Applied to all HTML rendered in preview widget

CSP_POLICY = (
    "default-src 'self'; "  # Only load resources from same origin
    "script-src 'unsafe-eval'; "  # Allow Qt runJavaScript() for scroll sync
    "object-src 'none'; "  # Block plugins (Flash, Java applets, etc.)
    "style-src 'unsafe-inline'; "  # Allow inline CSS (required for AsciiDoc)
    "img-src 'self' data:; "  # Images from same origin or data URIs only
    "base-uri 'self'; "  # Restrict base URL (prevent base tag attacks)
    "form-action 'none'"  # Block all form submissions (no forms in preview)
)
"""
Content Security Policy for preview HTML.

Security rules:
- default-src 'self': Only load resources from same origin
- script-src 'unsafe-eval': Allow Qt runJavaScript() for scroll sync
- object-src 'none': Block plugins (Flash, Java applets)
- style-src 'unsafe-inline': Allow inline CSS (required for AsciiDoc)
- img-src 'self' data:: Images from same origin or data URIs only
- base-uri 'self': Restrict base URL (prevent base tag attacks)
- form-action 'none': Block all form submissions
"""

# === ERROR DISPLAY COLORS ===
# Color schemes for error display based on theme

ERROR_COLORS_DARK = {
    "bg": "#3a2a1a",
    "text": "#ffcc99",
    "heading": "#ff6666",
    "pre_bg": "#2a2a2a",
}
"""Error display colors for dark theme."""

ERROR_COLORS_LIGHT = {
    "bg": "#fff3cd",
    "text": "#856404",
    "heading": "#dc3545",
    "pre_bg": "#f8f9fa",
}
"""Error display colors for light theme."""

# === FALLBACK CSS ===
# Used when ThemeManager is not available (shouldn't happen in production)

FALLBACK_CSS = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}
"""
"""Fallback CSS when ThemeManager is not available."""
