# AsciiDoc Artisan Specifications

**v2.1.0** | **109 FRs** | **Specification-Driven Coding**

---

## [SPEC] Code Generation Guide

```yaml
# AI INSTRUCTION: Use this document to generate code
# Sections marked [SPEC] are machine-parseable
# Generate code matching these exact patterns

code_generation:
  schemas: docs/SCHEMAS.md      # Pydantic models
  signals: docs/SIGNALS.md      # Qt signal contracts
  patterns: this_file           # Critical patterns below

imports:
  typing: "from typing import Any"
  pyside6: "from PySide6.QtCore import QThread, Signal"
  pathlib: "from pathlib import Path"
  dataclass: "from dataclasses import dataclass"
```

---

## [SPEC] Metrics

```yaml
version: 2.1.0
release_date: 2025-12-05

codebase:
  lines: 46244
  files: 181

testing:
  unit_tests: 5122
  e2e_tests: 17
  coverage: 95%

performance:
  startup_target: "<1.0s"
  startup_actual: "0.27s"
  preview_target: "<200ms"
  autocomplete_target: "<50ms"

storage:
  format: TOON
  fallback: JSON
  migration: automatic
```

---

## [SPEC] Worker Template

```python
# TEMPLATE: Generate workers using this pattern
# File: workers/{name}_worker.py

from PySide6.QtCore import QThread, Signal
from typing import Any

class {Name}Worker(QThread):
    """Worker for {description}."""

    # Define signals
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._cancelled = False
        self._queue: list[Any] = []

    def run(self) -> None:
        """Main worker loop."""
        while not self._cancelled:
            if not self._queue:
                self.msleep(10)
                continue
            item = self._queue.pop(0)
            try:
                result = self._process(item)
                self.result_ready.emit(result)
            except Exception as e:
                self.error_occurred.emit(str(e))

    def _process(self, item: Any) -> Any:
        """Override in subclass."""
        raise NotImplementedError

    def cancel(self) -> None:
        """Cancel worker."""
        self._cancelled = True

    def queue_request(self, item: Any) -> None:
        """Add item to queue."""
        self._queue.append(item)
```

---

## [SPEC] Handler Template

```python
# TEMPLATE: Generate handlers using this pattern
# File: ui/{name}_handler.py

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class {Name}Handler(QObject):
    """Handler for {description}."""

    # Signals
    operation_complete = Signal(object)
    operation_failed = Signal(str)

    def __init__(self, editor: "AsciiDocEditor") -> None:
        super().__init__(editor)
        self.editor = editor
        self._is_processing = False

    def do_operation(self) -> None:
        """Execute operation with reentrancy guard."""
        if self._is_processing:
            logger.warning("Operation already in progress")
            return

        self._is_processing = True
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            self.operation_failed.emit(str(e))
        finally:
            self._is_processing = False
```

---

## [SPEC] Atomic Write Pattern

```python
# TEMPLATE: All file writes must use this pattern
# File: core/file_operations.py

from pathlib import Path
from asciidoc_artisan.core import toon_utils

def atomic_save_text(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """Atomic text save: temp file + rename."""
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding=encoding) as f:
            f.write(content)
        temp_path.replace(file_path)
        return True
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        return False

def atomic_save_toon(file_path: Path, data: dict, indent: int = 2) -> bool:
    """Atomic TOON save: 30-60% smaller than JSON."""
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            toon_utils.dump(data, f, indent=indent)
        temp_path.replace(file_path)
        return True
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        return False
```

---

## [SPEC] Subprocess Safety

```python
# TEMPLATE: All subprocess calls must use this pattern
# NEVER use shell=True

import subprocess
from typing import list

def safe_subprocess(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Execute subprocess safely with shell=False."""
    result = subprocess.run(
        cmd,
        shell=False,  # REQUIRED: Never True
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr

# CORRECT:
subprocess.run(["git", "commit", "-m", message], shell=False)

# WRONG - NEVER DO THIS:
# subprocess.run(f"git commit -m {message}", shell=True)
```

---

## [SPEC] Test Template

```python
# TEMPLATE: Generate tests using this pattern
# File: tests/unit/{module}/test_{name}.py

import pytest
from unittest.mock import MagicMock, patch

class Test{Name}:
    """Test suite for {Name}."""

    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return {Name}()

    def test_basic_operation(self, instance):
        """Test basic functionality."""
        result = instance.do_operation()
        assert result is not None

    def test_error_handling(self, instance):
        """Test error cases."""
        with pytest.raises(ValueError):
            instance.do_invalid_operation()

    @pytest.mark.parametrize("input,expected", [
        ("valid", True),
        ("invalid", False),
    ])
    def test_parameterized(self, instance, input, expected):
        """Test multiple inputs."""
        result = instance.validate(input)
        assert result == expected
```

---

## [SPEC] Directory Structure

```yaml
# AI: Generate files in these locations

src/asciidoc_artisan/:
  core/:           # Business logic (no Qt)
    - settings.py
    - toon_utils.py
    - file_operations.py
    - *_models.py

  ui/:             # Qt widgets and handlers
    - main_window.py
    - *_handler.py
    - *_manager.py
    - *_widget.py
    - *_dialog.py

  workers/:        # QThread workers
    - base_worker.py
    - *_worker.py

  lsp/:            # Language Server Protocol
    - server.py
    - *_provider.py

tests/:
  unit/:           # Unit tests mirror src/ structure
  e2e/:            # End-to-end tests
  conftest.py      # Shared fixtures
```

---

## [SPEC] Error Codes

```yaml
# Use these codes in SyntaxErrorModel.code field

syntax_errors:
  E001: "Unclosed source block"
  E002: "Unclosed example block"
  E003: "Unclosed sidebar block"
  E004: "Unclosed quote block"
  E005: "Unclosed literal block"
  E006: "Unclosed table"
  E007: "Unclosed open block"
  E008: "Invalid heading level (only = to ======)"
  E009: "Duplicate anchor ID"
  E010: "Invalid block delimiter length"

semantic_errors:
  E100: "Broken cross-reference"
  E101: "Include file not found"
  E102: "Invalid include path"
  E103: "Circular include detected"
  E104: "Unknown attribute"

warnings:
  W001: "Heading level skipped"
  W002: "Empty section"
  W003: "Missing document title"
  W004: "Line exceeds 120 characters"
  W005: "Trailing whitespace"

info:
  I001: "Consider using semantic heading"
  I002: "Block could benefit from title"
  I003: "Consider using include directive"
```

---

## [SPEC] Functional Requirements

### Core Editor (FR-001 to FR-005)

```yaml
FR-001:
  name: Text Editor
  file: ui/main_window.py
  widget: QPlainTextEdit
  features: [syntax_highlight, line_wrap, tab_handling]

FR-002:
  name: Line Numbers
  file: ui/line_number_area.py
  class: LineNumberArea
  parent: QWidget

FR-003:
  name: Undo/Redo
  implementation: Qt built-in
  shortcuts: [Ctrl+Z, Ctrl+Y]

FR-004:
  name: Font Configuration
  file: core/settings.py
  fields: [editor_font_family, editor_font_size]

FR-005:
  name: State Persistence
  file: core/settings.py
  format: TOON
  migration: JSON to TOON automatic
```

### File Operations (FR-006 to FR-014)

```yaml
FR-006:
  name: Open File
  shortcut: Ctrl+O
  handler: ui/file_open_handler.py
  pattern: atomic_read

FR-007:
  name: Save File
  shortcut: Ctrl+S
  handler: ui/file_save_handler.py
  pattern: atomic_save_text

FR-008:
  name: Save As
  shortcut: Ctrl+Shift+S
  handler: ui/file_save_handler.py

FR-009:
  name: New File
  shortcut: Ctrl+N
  handler: ui/file_handler.py

FR-010:
  name: Recent Files
  file: core/recent_templates_tracker.py
  max_items: 10
  format: TOON

FR-011:
  name: Auto-Save
  file: ui/file_handler.py
  default_interval: 300  # seconds
  configurable: true
```

### Preview (FR-015 to FR-020)

```yaml
FR-015:
  name: Live Preview
  target: "<200ms"
  file: workers/preview_worker.py

FR-016:
  name: GPU Acceleration
  file: ui/preview_handler_gpu.py
  speedup: "10-50x"
  fallback: QTextBrowser

FR-017:
  name: Scroll Sync
  file: ui/preview_handler_base.py
  mode: bidirectional

FR-018:
  name: Incremental Rendering
  file: workers/incremental_renderer.py
  cache: LRU(100)

FR-019:
  name: Debounce
  file: ui/preview_handler_base.py
  delay: 300ms

FR-020:
  name: Theme Support
  file: ui/theme_manager.py
  method: CSS injection
```

### Git (FR-026 to FR-033)

```yaml
FR-026:
  name: Repo Detection
  file: ui/git_handler.py
  method: ".git directory check"

FR-027:
  name: Commit
  file: workers/git_worker.py
  signal: command_complete(GitResult)
  shell: false  # REQUIRED

FR-028:
  name: Pull
  file: workers/git_worker.py
  signal: command_complete(GitResult)

FR-029:
  name: Push
  file: workers/git_worker.py
  signal: command_complete(GitResult)
```

### AI Chat (FR-039 to FR-044)

```yaml
FR-039:
  name: Ollama Integration
  file: workers/ollama_chat_worker.py
  signals: [chat_response_ready, chat_response_chunk, chat_error]
  streaming: true

FR-040:
  name: Chat Panel
  file: ui/chat_panel_widget.py
  class: ChatPanelWidget
  parent: QWidget

FR-041:
  name: Context Modes
  modes: [document, syntax, general, editing]
  file: ui/chat_manager.py

FR-042:
  name: Chat History
  max_messages: 100
  file: ui/chat_manager.py
```

---

## [VALIDATE] Acceptance Criteria

```bash
# All must pass before merge

# Tests
make test                        # 5,139 tests must pass
pytest --cov=src --cov-fail-under=90

# Type safety
mypy --strict src/               # 0 errors required

# Security check
grep -r "shell=True" src/        # Must return empty
grep -r "shell = True" src/      # Must return empty

# Linting
ruff check src/                  # All checks passed
ruff format --check src/         # Already formatted
```

```yaml
# Performance requirements
startup: "<1.0s"
preview_render: "<200ms"
autocomplete: "<50ms"
file_open: "<500ms"
memory_baseline: "<100MB"
```

---

## [CONTEXT] Architecture Decisions

**Handler Architecture**
Original main_window.py exceeded 2,000 lines. MA principle requires <400 lines per file. Handlers split by domain.

**QThread Workers**
PySide6 signal/slot threading integrates with Qt event loop. Workers emit signals for UI updates.

**TOON Format**
30-60% smaller than JSON. Human-readable. Auto-migrates from legacy JSON files.

**Atomic Writes**
temp+rename pattern ensures complete file or nothing. Never partial writes on crash.

---

*v2.1.0 | 109 FRs | 46,244 lines | Specification-Driven | Dec 5, 2025*
