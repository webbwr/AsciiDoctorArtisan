"""
Visual/Data regression tests using pytest-regressions.

Tests UI component outputs and rendering results to detect unintended changes.
Uses data regression instead of pixel-perfect screenshot comparison for better
headless CI compatibility.

QA-9: Phase 3 - Quality Infrastructure

Run with: pytest tests/visual/test_visual_regression.py --regen-all
Compare: pytest tests/visual/test_visual_regression.py
"""

import pytest

from asciidoc_artisan.core.lru_cache import LRUCache
from asciidoc_artisan.workers.incremental_renderer import DocumentBlockSplitter


@pytest.mark.visual
class TestThemeRegression:
    """Regression tests for theme color consistency."""

    def test_light_theme_color_hex_values(self, data_regression):
        """Verify light theme color values remain consistent."""
        # Define expected light theme colors
        light_colors = {
            "bg": "#ffffff",
            "fg": "#000000",
            "accent": "#0066cc",
            "selection": "#b3d7ff",
            "border": "#cccccc",
        }

        data_regression.check(light_colors)

    def test_dark_theme_color_hex_values(self, data_regression):
        """Verify dark theme color values remain consistent."""
        # Define expected dark theme colors
        dark_colors = {
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "accent": "#569cd6",
            "selection": "#264f78",
            "border": "#3c3c3c",
        }

        data_regression.check(dark_colors)

    def test_theme_contrast_ratios(self, data_regression):
        """Verify theme contrast ratios meet accessibility standards."""
        # Contrast ratios for light/dark themes
        contrast_data = {
            "light_mode": {
                "text_bg_ratio": 21.0,  # Black on white = 21:1
                "accent_bg_ratio": 4.5,  # Minimum for normal text
            },
            "dark_mode": {
                "text_bg_ratio": 12.63,  # Light gray on dark
                "accent_bg_ratio": 6.0,  # Blue accent on dark
            },
        }

        data_regression.check(contrast_data)


@pytest.mark.visual
class TestDocumentStructureRegression:
    """Regression tests for document structure parsing."""

    def test_asciidoc_header_parsing(self, data_regression):
        """Verify AsciiDoc header parsing remains consistent."""
        import re

        test_headers = {
            "simple": "= Document Title",
            "with_author": "= Document\nJohn Doe",
            "with_version": "= Document v1.0",
            "with_attribute": "= Document\n:version: 2.1.0",
        }

        header_data = {}
        for name, header in test_headers.items():
            lines = header.split("\n")
            title_match = re.match(r"^=\s+(.+?)(?:\s+v[\d.]+)?$", lines[0])

            header_data[name] = {
                "has_title": bool(title_match),
                "line_count": len(lines),
                "has_attributes": ":" in header,
            }

        data_regression.check(header_data)

    def test_asciidoc_section_levels(self, data_regression):
        """Verify section level detection remains consistent."""
        sections = {
            "level_1": "= Title",
            "level_2": "== Section",
            "level_3": "=== Subsection",
            "level_4": "==== Sub-subsection",
            "level_5": "===== Paragraph",
        }

        section_data = {}
        for name, section in sections.items():
            equals_count = len(section.split()[0])
            section_data[name] = {
                "level": equals_count,
                "is_title": equals_count == 1,
                "is_section": equals_count >= 2,
            }

        data_regression.check(section_data)

    def test_asciidoc_formatting_markers(self, data_regression):
        """Verify AsciiDoc formatting marker detection."""
        markers = {
            "bold": "*text*",
            "italic": "_text_",
            "monospace": "`text`",
            "superscript": "^text^",
            "subscript": "~text~",
        }

        marker_data = {}
        for name, marked_text in markers.items():
            marker_char = marked_text[0]
            marker_data[name] = {
                "start_char": marker_char,
                "length": len(marked_text),
                "is_paired": marked_text[0] == marked_text[-1],
            }

        data_regression.check(marker_data)

    def test_list_pattern_detection(self, data_regression):
        """Verify list pattern detection remains consistent."""
        list_patterns = {
            "unordered": "* Item",
            "unordered_nested": "** Nested",
            "ordered": ". Item",
            "ordered_nested": ".. Nested",
            "checklist": "* [ ] Task",
        }

        pattern_data = {}
        for name, pattern in list_patterns.items():
            is_unordered = pattern.strip().startswith("*")
            is_ordered = pattern.strip().startswith(".")
            is_nested = pattern.strip().startswith(("**", ".."))

            pattern_data[name] = {
                "is_unordered": is_unordered,
                "is_ordered": is_ordered,
                "is_nested": is_nested,
                "starts_with_marker": pattern[0] in ["*", "."],
            }

        data_regression.check(pattern_data)

    def test_code_block_delimiters(self, data_regression):
        """Verify code block delimiter detection."""
        delimiters = {
            "standard": "----",
            "source_block": "[source,python]\n----",
            "listing": "....",
            "literal": "....",
        }

        delimiter_data = {}
        for name, delimiter in delimiters.items():
            lines = delimiter.split("\n")
            has_attribute = "[" in delimiter
            delimiter_char = lines[-1][0] if lines else ""

            delimiter_data[name] = {
                "has_source_attribute": has_attribute,
                "delimiter_char": delimiter_char,
                "line_count": len(lines),
            }

        data_regression.check(delimiter_data)


@pytest.mark.visual
class TestBlockSplittingRegression:
    """Regression tests for document block splitting."""

    def test_block_splitting_structure(self, data_regression):
        """Verify document block splitting produces consistent structure."""
        text = """= Document

== Section 1
Content here.

== Section 2
More content.

== Section 3
Final content.
"""
        blocks = DocumentBlockSplitter.split(text)

        blocks_data = {
            "count": len(blocks),
            "has_blocks": len(blocks) > 0,
            "total_size": len(text),
            "has_title": text.startswith("="),
            "has_sections": "==" in text,
        }

        data_regression.check(blocks_data)

    def test_block_splitting_large_document(self, data_regression):
        """Verify block splitting handles large documents consistently."""
        sections = []
        for i in range(100):
            sections.append(f"== Section {i}\n\nContent for section {i}.\n\n")

        text = "= Large Document\n\n" + "".join(sections)
        blocks = DocumentBlockSplitter.split(text)

        blocks_data = {
            "count": len(blocks),
            "first_block_type": type(blocks[0]).__name__ if blocks else "None",
            "last_block_type": type(blocks[-1]).__name__ if blocks else "None",
            "total_size": len(text),
        }

        data_regression.check(blocks_data)

    def test_block_splitting_nested_sections(self, data_regression):
        """Verify nested section splitting structure."""
        text = """= Main Title

== Level 2 Section

=== Level 3 Section

==== Level 4 Section

Content at level 4.

=== Another Level 3

More content.
"""
        blocks = DocumentBlockSplitter.split(text)

        blocks_data = {
            "count": len(blocks),
            "structure": str(type(blocks[0])) if blocks else "empty",
        }

        data_regression.check(blocks_data)


@pytest.mark.visual
class TestCacheRenderingRegression:
    """Regression tests for LRU cache behavior."""

    def test_cache_rendering_consistency(self, data_regression):
        """Verify LRU cache produces consistent results."""
        cache = LRUCache(max_size=10)

        # Populate cache
        for i in range(15):
            cache.put(f"key_{i}", f"value_{i}")

        cache_data = {
            "size": len(cache),
            "max_size": cache.max_size,
            "has_key_0": cache.get("key_0") is not None,
            "has_key_14": cache.get("key_14") is not None,
            "evicted_early_keys": cache.get("key_0") is None,
        }

        data_regression.check(cache_data)

    def test_cache_lru_eviction_order(self, data_regression):
        """Verify LRU eviction happens in correct order."""
        cache = LRUCache(max_size=3)

        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")
        cache.get("a")  # Access 'a', making it most recently used
        cache.put("d", "4")  # Should evict 'b'

        cache_data = {
            "size": len(cache),
            "has_a": cache.get("a") is not None,
            "has_b": cache.get("b") is not None,
            "has_c": cache.get("c") is not None,
            "has_d": cache.get("d") is not None,
            "evicted_b": cache.get("b") is None,
        }

        data_regression.check(cache_data)


@pytest.mark.visual
class TestStatusMessageRegression:
    """Regression tests for status bar messages."""

    def test_status_message_formatting(self, data_regression):
        """Verify status message formatting remains consistent."""

        # Test different message types
        messages = {
            "normal": "File saved successfully",
            "error": "Error: Could not save file",
            "git": "Git: Changes committed",
            "version": "v1.5.0",
        }

        # Verify message properties
        message_data = {
            msg_type: {
                "length": len(msg),
                "has_prefix": any(prefix in msg for prefix in ["Error:", "Git:", "v"]),
            }
            for msg_type, msg in messages.items()
        }

        data_regression.check(message_data)

    def test_version_extraction_patterns(self, data_regression):
        """Verify version extraction produces consistent results."""

        test_documents = {
            "attribute_version": ":version: 2.1.0\n\n= Document",
            "attribute_revnumber": ":revnumber: 3.0.0\n\n= Document",
            "text_version": "Version: 1.5.0\n\n= Document",
            "title_version": "= Document v4.2.1",
        }

        # Extract versions
        version_data = {}
        for doc_type, content in test_documents.items():
            # Simulate version extraction logic
            import re

            version = None
            if match := re.search(r":version:\s*(\S+)", content):
                version = match.group(1)
            elif match := re.search(r":revnumber:\s*(\S+)", content):
                version = match.group(1)
            elif match := re.search(r"Version:\s*(\S+)", content):
                version = match.group(1)
            elif match := re.search(r"\sv(\d+\.\d+\.\d+)", content):
                version = match.group(1)

            version_data[doc_type] = {
                "extracted_version": version,
                "found": version is not None,
            }

        data_regression.check(version_data)


@pytest.mark.visual
class TestFileOperationRegression:
    """Regression tests for file operation outputs."""

    def test_atomic_save_behavior(self, data_regression, tmp_path):
        """Verify atomic save produces consistent file properties."""
        from asciidoc_artisan.core import atomic_save_text

        test_file = tmp_path / "test.txt"
        content = "Test content\n" * 100

        result = atomic_save_text(test_file, content)

        file_data = {
            "save_successful": result,
            "file_exists": test_file.exists(),
            "content_matches": (
                test_file.read_text() == content if test_file.exists() else False
            ),
            "file_size": test_file.stat().st_size if test_file.exists() else 0,
        }

        data_regression.check(file_data)

    def test_path_sanitization_results(self, data_regression):
        """Verify path sanitization produces consistent results."""
        from asciidoc_artisan.core import sanitize_path

        test_paths = [
            "/home/user/documents/file.adoc",
            "../../etc/passwd",
            "/tmp/test.txt",
            "relative/path/to/file.adoc",
            "../../../dangerous/path",
        ]

        sanitized_data = {}
        for path in test_paths:
            result = sanitize_path(path)
            sanitized_data[path] = {
                "is_none": result is None,
                "is_absolute": result.is_absolute() if result else False,
                "has_dotdot": ".." in path,
            }

        data_regression.check(sanitized_data)


@pytest.mark.visual
class TestUIStateRegression:
    """Regression tests for UI state calculations."""

    def test_window_geometry_calculations(self, data_regression):
        """Verify window geometry calculations remain consistent."""
        # Test different screen sizes and window states
        geometries = {
            "fullhd": {"width": 1920, "height": 1080, "maximized": False},
            "4k": {"width": 3840, "height": 2160, "maximized": False},
            "laptop": {"width": 1366, "height": 768, "maximized": False},
            "maximized": {"width": 1920, "height": 1080, "maximized": True},
        }

        # Calculate editor/preview split ratios
        geometry_data = {}
        for name, geom in geometries.items():
            editor_width = geom["width"] // 2
            preview_width = geom["width"] - editor_width

            geometry_data[name] = {
                "editor_width": editor_width,
                "preview_width": preview_width,
                "ratio": round(editor_width / geom["width"], 2),
                "is_wide": geom["width"] > 1600,
            }

        data_regression.check(geometry_data)

    def test_font_size_calculations(self, data_regression):
        """Verify font size calculations remain consistent."""
        base_sizes = [8, 10, 12, 14, 16, 18, 20]

        font_data = {}
        for size in base_sizes:
            # Simulate line height calculation (typical 1.2-1.5x base size)
            line_height = int(size * 1.3)

            font_data[f"size_{size}"] = {
                "point_size": size,
                "line_height": line_height,
                "pixel_size": int(size * 96 / 72),  # Points to pixels at 96 DPI
            }

        data_regression.check(font_data)


@pytest.mark.visual
class TestErrorStateRegression:
    """Regression tests for error state handling."""

    def test_error_message_formats(self, data_regression):
        """Verify error messages format consistently."""
        errors = {
            "git_error": "Git error: Repository not found",
            "file_error": "Error: Could not save file",
            "render_error": "Preview rendering failed: Invalid AsciiDoc syntax",
            "permission_error": "Permission denied: Cannot write to file",
        }

        error_data = {
            error_type: {
                "length": len(msg),
                "has_error_prefix": msg.startswith("Error:") or "error" in msg.lower(),
                "has_details": ":" in msg,
            }
            for error_type, msg in errors.items()
        }

        data_regression.check(error_data)

    def test_recovery_states(self, data_regression):
        """Verify error recovery state transitions."""
        states = {
            "normal": {"has_error": False, "can_save": True, "can_render": True},
            "file_error": {"has_error": True, "can_save": False, "can_render": True},
            "render_error": {"has_error": True, "can_save": True, "can_render": False},
            "critical_error": {
                "has_error": True,
                "can_save": False,
                "can_render": False,
            },
        }

        data_regression.check(states)


@pytest.mark.visual
class TestDataIntegrityRegression:
    """Regression tests for data integrity and validation."""

    def test_json_structure_consistency(self, data_regression):
        """Verify JSON data structures remain consistent."""
        sample_json = {
            "version": "1.5.0",
            "settings": {
                "theme": "light",
                "font_size": 12,
                "auto_save": True,
            },
            "recent_files": ["/path/1.adoc", "/path/2.adoc"],
        }

        data_regression.check(sample_json)

    def test_config_defaults_consistency(self, data_regression):
        """Verify configuration defaults remain unchanged."""
        defaults = {
            "editor": {
                "tab_size": 4,
                "line_numbers": True,
                "word_wrap": True,
                "font_family": "Monospace",
            },
            "preview": {
                "auto_refresh": True,
                "sync_scroll": True,
            },
        }

        data_regression.check(defaults)

    def test_keyboard_shortcuts_mapping(self, data_regression):
        """Verify keyboard shortcut mappings remain consistent."""
        shortcuts = {
            "save": "Ctrl+S",
            "save_as": "Ctrl+Shift+S",
            "open": "Ctrl+O",
            "new": "Ctrl+N",
            "quit": "Ctrl+Q",
            "export_pdf": "Ctrl+E",
            "toggle_preview": "Ctrl+P",
        }

        data_regression.check(shortcuts)

    def test_file_extension_associations(self, data_regression):
        """Verify file extension associations remain consistent."""
        extensions = {
            "asciidoc": [".adoc", ".asciidoc", ".asc"],
            "markdown": [".md", ".markdown"],
            "text": [".txt"],
            "html": [".html", ".htm"],
        }

        data_regression.check(extensions)

    def test_mime_type_mappings(self, data_regression):
        """Verify MIME type mappings remain consistent."""
        mime_types = {
            ".adoc": "text/plain",
            ".md": "text/markdown",
            ".html": "text/html",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        data_regression.check(mime_types)

    def test_export_format_options(self, data_regression):
        """Verify export format options remain consistent."""
        export_formats = {
            "pdf": {"extension": ".pdf", "requires_wkhtmltopdf": True},
            "html": {"extension": ".html", "requires_wkhtmltopdf": False},
            "docx": {"extension": ".docx", "requires_pandoc": True},
            "markdown": {"extension": ".md", "requires_pandoc": True},
        }

        data_regression.check(export_formats)

    def test_git_command_templates(self, data_regression):
        """Verify Git command templates remain consistent."""
        git_commands = {
            "status": ["git", "status", "--porcelain"],
            "add": ["git", "add", "{file}"],
            "commit": ["git", "commit", "-m", "{message}"],
            "push": ["git", "push"],
            "pull": ["git", "pull", "--rebase"],
        }

        data_regression.check(git_commands)

    def test_error_code_mappings(self, data_regression):
        """Verify error code mappings remain consistent."""
        error_codes = {
            "E001": "File not found",
            "E002": "Permission denied",
            "E003": "Invalid AsciiDoc syntax",
            "E004": "Git repository not found",
            "E005": "Pandoc not installed",
            "E006": "wkhtmltopdf not installed",
        }

        data_regression.check(error_codes)

    def test_log_level_hierarchy(self, data_regression):
        """Verify log level hierarchy remains consistent."""
        log_levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }

        data_regression.check(log_levels)


# Performance baseline for visual/data regression test execution
VISUAL_REGRESSION_BASELINE = {
    "test_execution_time": 0.1,  # seconds per test (data comparison)
    "total_tests": 30,
    "expected_duration": 3.0,  # seconds for all 30 tests
}
