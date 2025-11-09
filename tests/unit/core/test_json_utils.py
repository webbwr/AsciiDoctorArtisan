"""
Tests for core.json_utils module.

Tests fast JSON utilities with orjson and fallback to stdlib json.
"""

import io
import sys
from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestJSONUtils:
    """Test JSON utility functions."""

    def test_import(self):
        """Test json_utils can be imported."""
        from asciidoc_artisan.core import json_utils

        assert json_utils is not None

    def test_loads_with_string(self):
        """Test loads() with string input."""
        from asciidoc_artisan.core.json_utils import loads

        result = loads('{"key": "value"}')
        assert result == {"key": "value"}

    def test_loads_with_bytes(self):
        """Test loads() with bytes input."""
        from asciidoc_artisan.core.json_utils import loads

        result = loads(b'{"key": "value"}')
        assert result == {"key": "value"}

    def test_dumps_compact(self):
        """Test dumps() with compact output."""
        from asciidoc_artisan.core.json_utils import dumps

        result = dumps({"key": "value"})
        assert "key" in result
        assert "value" in result

    def test_dumps_with_indent(self):
        """Test dumps() with indentation."""
        from asciidoc_artisan.core.json_utils import dumps

        result = dumps({"key": "value"}, indent=2)
        assert "key" in result
        assert "value" in result

    def test_load_from_file(self):
        """Test load() from file object."""
        from asciidoc_artisan.core.json_utils import load

        fp = io.StringIO('{"key": "value"}')
        result = load(fp)
        assert result == {"key": "value"}

    def test_dump_to_file(self):
        """Test dump() to file object."""
        from asciidoc_artisan.core.json_utils import dump

        fp = io.StringIO()
        dump({"key": "value"}, fp)
        fp.seek(0)
        content = fp.read()
        assert "key" in content
        assert "value" in content

    def test_dump_to_file_with_indent(self):
        """Test dump() to file with indentation."""
        from asciidoc_artisan.core.json_utils import dump

        fp = io.StringIO()
        dump({"key": "value"}, fp, indent=2)
        fp.seek(0)
        content = fp.read()
        assert "key" in content
        assert "value" in content


@pytest.mark.unit
class TestJSONUtilsFallback:
    """Test JSON utilities fallback to stdlib when orjson unavailable."""

    def test_loads_fallback_with_string(self):
        """Test loads() fallback with string input."""
        # Hide orjson to force fallback
        with patch.dict(sys.modules, {"orjson": None}):
            # Reimport to trigger fallback path
            import importlib

            from asciidoc_artisan.core import json_utils

            importlib.reload(json_utils)

            result = json_utils.loads('{"key": "value"}')
            assert result == {"key": "value"}

    def test_loads_fallback_with_bytes(self):
        """Test loads() fallback with bytes input."""
        # Hide orjson to force fallback
        with patch.dict(sys.modules, {"orjson": None}):
            import importlib

            from asciidoc_artisan.core import json_utils

            importlib.reload(json_utils)

            result = json_utils.loads(b'{"key": "value"}')
            assert result == {"key": "value"}

    def test_dumps_fallback_compact(self):
        """Test dumps() fallback with compact output."""
        with patch.dict(sys.modules, {"orjson": None}):
            import importlib

            from asciidoc_artisan.core import json_utils

            importlib.reload(json_utils)

            result = json_utils.dumps({"key": "value"})
            assert "key" in result
            assert "value" in result

    def test_dumps_fallback_with_indent(self):
        """Test dumps() fallback with indentation."""
        with patch.dict(sys.modules, {"orjson": None}):
            import importlib

            from asciidoc_artisan.core import json_utils

            importlib.reload(json_utils)

            result = json_utils.dumps({"key": "value"}, indent=2)
            assert "key" in result
            assert "value" in result

    def test_load_fallback_from_file(self):
        """Test load() fallback from file object."""
        with patch.dict(sys.modules, {"orjson": None}):
            import importlib

            from asciidoc_artisan.core import json_utils

            importlib.reload(json_utils)

            fp = io.StringIO('{"key": "value"}')
            result = json_utils.load(fp)
            assert result == {"key": "value"}


@pytest.mark.unit
class TestJSONUtilsEdgeCases:
    """Test edge cases for JSON utilities."""

    def test_loads_with_empty_string(self):
        """Test loads() with empty string raises error."""
        from asciidoc_artisan.core.json_utils import loads

        with pytest.raises(Exception):  # JSONDecodeError or similar
            loads("")

    def test_loads_with_invalid_json(self):
        """Test loads() with invalid JSON raises error."""
        from asciidoc_artisan.core.json_utils import loads

        with pytest.raises(Exception):
            loads("{invalid json}")

    def test_dumps_with_complex_object(self):
        """Test dumps() with nested objects."""
        from asciidoc_artisan.core.json_utils import dumps

        obj = {"key1": {"nested": "value"}, "key2": [1, 2, 3]}
        result = dumps(obj)
        assert "key1" in result
        assert "nested" in result
        assert "key2" in result

    def test_load_dump_roundtrip(self):
        """Test load/dump roundtrip preserves data."""
        from asciidoc_artisan.core.json_utils import dump, load

        original = {"key": "value", "number": 42, "list": [1, 2, 3]}

        fp = io.StringIO()
        dump(original, fp)
        fp.seek(0)
        result = load(fp)

        assert result == original
