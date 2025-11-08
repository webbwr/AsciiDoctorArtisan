"""
Fast JSON utilities using orjson (3-5x faster than standard json module).

Hot path optimization (v1.9.1): Uses native C implementation for JSON encoding/decoding.
Falls back to standard json if orjson not available.

Performance:
- loads(): 3-5x faster than json.loads()
- dumps(): 3-5x faster than json.dumps()
- load(): 3-5x faster than json.load()
- dump(): 3-5x faster than json.dump()

Protocol boundary: Uses native C (orjson) to separate control plane (Python)
from data plane (JSON serialization). Avoids Python object marshalling overhead.
"""

import json as stdlib_json
from typing import Any, TextIO

# Try to import orjson (3-5x faster native C implementation)
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def loads(s: str | bytes) -> Any:
    """
    Deserialize JSON string to Python object (3-5x faster with orjson).

    Args:
        s: JSON string or bytes

    Returns:
        Deserialized Python object
    """
    if HAS_ORJSON:
        # orjson.loads() accepts both str and bytes
        if isinstance(s, str):
            return orjson.loads(s)
        return orjson.loads(s)
    else:
        # Standard json only accepts str
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return stdlib_json.loads(s)


def dumps(obj: Any, indent: int | None = None) -> str:
    """
    Serialize Python object to JSON string (3-5x faster with orjson).

    Args:
        obj: Python object to serialize
        indent: Indentation spaces (None for compact)

    Returns:
        JSON string
    """
    if HAS_ORJSON:
        # orjson returns bytes, decode to str for compatibility
        options = 0
        if indent is not None:
            # orjson uses OPT_INDENT_2 for pretty printing (always 2 spaces)
            options = orjson.OPT_INDENT_2

        result: str = orjson.dumps(obj, option=options).decode("utf-8")
        return result
    else:
        # Standard json.dumps()
        return stdlib_json.dumps(obj, indent=indent)


def load(fp: TextIO) -> Any:
    """
    Deserialize JSON from file object (3-5x faster with orjson).

    Args:
        fp: File object opened in text mode

    Returns:
        Deserialized Python object
    """
    content = fp.read()

    if HAS_ORJSON:
        return orjson.loads(content)
    else:
        return stdlib_json.loads(content)


def dump(obj: Any, fp: TextIO, indent: int | None = None) -> None:
    """
    Serialize Python object to JSON file (3-5x faster with orjson).

    Args:
        obj: Python object to serialize
        fp: File object opened in text/write mode
        indent: Indentation spaces (None for compact)
    """
    json_str = dumps(obj, indent=indent)
    fp.write(json_str)
