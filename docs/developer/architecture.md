# Implementation Reference - v1.5.0 Features

**Created:** October 28, 2025
**Last Updated:** November 6, 2025 (Lazy import patterns added)
**Applies To:** AsciiDoc Artisan v1.5.0+ (current: v1.9.1)
**Status:** v1.5.0 COMPLETE, actively maintained
**Purpose:** Technical reference for v1.5.0+ implementation details

---

## Overview

This document consolidates implementation details for v1.5.0 features:
- Worker Pool System
- Operation Cancellation
- Lazy Import System

For current development priorities, see [ROADMAP_v1.5.0.md](../ROADMAP_v1.5.0.md).

---

## 1. Worker Pool Implementation (v1.5.0-A)

**Status:** ✅ COMPLETE

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  WorkerManager (v1.5.0)                  │
│                                                           │
│  ┌────────────────────────────────────────────────┐    │
│  │     OptimizedWorkerPool (New)                  │    │
│  │  - Max threads: CPU_COUNT * 2 (configurable)   │    │
│  │  - Task prioritization                         │    │
│  │  - Task cancellation                           │    │
│  │  - Task coalescing                             │    │
│  └────────────────────────────────────────────────┘    │
│              │                                           │
│       ┌──────┴───────┬──────────┐                      │
│       ▼              ▼          ▼                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Render   │  │ Convert  │  │   Git    │            │
│  │  Task    │  │  Task    │  │  Task    │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Key Files

- **`src/asciidoc_artisan/workers/optimized_worker_pool.py`** - Pool implementation
- **`src/asciidoc_artisan/ui/worker_manager.py`** - Integration with main window

### Features

**Configurable Thread Pool:**
- QThreadPool-based execution
- Max threads: CPU_COUNT * 2 (default)
- Configurable via settings

**Task Prioritization:**
- CRITICAL: Immediate execution
- HIGH: User-initiated operations
- NORMAL: Background operations
- LOW: Deferred operations
- IDLE: Run when system is idle

**Task Cancellation:**
- Cancel individual tasks by task_id
- Cancel all pending tasks
- Automatic cleanup of cancelled tasks

**Task Coalescing:**
- Deduplicates similar preview rendering tasks
- Reduces redundant work
- Improves responsiveness

**Statistics Tracking:**
- Active task count
- Completed task count
- Pool utilization percentage

### Usage Example

```python
from asciidoc_artisan.workers.optimized_worker_pool import (
    get_worker_pool,
    TaskPriority,
)

# Get pool instance
pool = get_worker_pool()

# Submit a task
task = RenderTask(text="# Heading", api=api_instance)
task_id = pool.submit(task, priority=TaskPriority.HIGH)

# Connect signals
task.signals.finished.connect(on_render_complete)
task.signals.error.connect(on_render_error)

# Cancel if needed
pool.cancel_task(task_id)

# Get statistics
stats = pool.get_statistics()
print(f"Active tasks: {stats['active_tasks']}")
```

### Testing

**Test files:**
- `tests/test_optimized_worker_pool.py`

**Coverage:**
- Unit tests for pool operations
- Integration tests with main window
- Performance benchmarks

---

## 2. Operation Cancellation (v1.5.0-C)

**Status:** ✅ COMPLETE (Phase 1)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  StatusManager (v1.5.0)                  │
│                                                           │
│  ┌────────────────────────────────────────────────┐    │
│  │     Cancel Button (QPushButton)                 │    │
│  │  - Hidden by default                            │    │
│  │  - Shows during operation                       │    │
│  │  - Click → calls worker_manager.cancel_*()     │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                 │
│                        ▼                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │     WorkerManager                               │    │
│  │  - cancel_git_operation()                       │    │
│  │  - cancel_pandoc_operation()                    │    │
│  │  - cancel_preview_operation()                   │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                 │
│              ┌─────────┴─────────┐                     │
│              ▼                   ▼                     │
│  ┌────────────────┐   ┌────────────────┐             │
│  │   GitWorker     │   │  Other Workers  │             │
│  │  (v1.5.0-C)     │   │  (Future)       │             │
│  │                 │   │                 │             │
│  │  - _cancelled   │   │  - TODO         │             │
│  │  - cancel()     │   │                 │             │
│  │  - is_cancel()  │   │                 │             │
│  └────────────────┘   └────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Key Files

- **`src/asciidoc_artisan/ui/status_manager.py`** - Cancel button UI
- **`src/asciidoc_artisan/ui/worker_manager.py`** - Cancellation coordination
- **`src/asciidoc_artisan/workers/git_worker.py`** - Cancellation support

### Features

**Cancel Button UI:**
- Located in status bar
- Hidden by default
- Shows automatically during long operations
- Hides when operation completes

**Worker Cancellation:**
- GitWorker supports cancellation via threading.Event
- Workers check cancellation flag periodically
- Clean shutdown on cancellation

**Automatic UI Updates:**
- Status bar shows "Cancelling..." message
- Button disables during cancellation
- Re-enables on next operation

### Usage

**From UI:**
- Click cancel button in status bar during operation
- Operation stops gracefully
- Status message indicates cancellation

**From Code:**
```python
# Show cancel button for operation
self.status_manager.show_cancel_button(operation_name="Git Pull")

# Connect cancel button to cancellation handler
self.status_manager.cancel_button_clicked.connect(
    self.worker_manager.cancel_git_operation
)

# Hide button when operation completes
self.status_manager.hide_cancel_button()
```

### Phase 1 Implementation

**Complete:**
- Cancel button UI in status bar
- GitWorker cancellation support
- WorkerManager cancel methods

**Future (Phase 2):**
- PandocWorker cancellation
- PreviewWorker cancellation
- Progress bars with cancellation

### Testing

**Test files:**
- `tests/test_status_manager.py`
- `tests/test_worker_manager.py`
- `tests/test_git_worker.py`

---

## 3. Lazy Import System (v1.5.0-D)

**Status:** ✅ COMPLETE

### Overview

Deferred loading of heavy modules to improve startup performance:
- pypandoc
- asciidoc3
- document_converter

**Performance Impact:** ~50-100ms startup improvement

### Implementation

**Before (Eager Loading):**
```python
# main.py - ALL imports at module level
import pypandoc
import asciidoc3
from document_converter import DocumentConverter

PANDOC_AVAILABLE = True if pypandoc else False
```

**After (Lazy Loading):**
```python
# main.py - NO heavy imports at module level
# Heavy modules imported where actually used

# constants.py - Lazy function with global state caching
_pypandoc_checked = False
_pypandoc_available = False

def is_pandoc_available() -> bool:
    """Check if pypandoc is available (lazy evaluation with caching)."""
    global _pypandoc_checked, _pypandoc_available

    if not _pypandoc_checked:
        try:
            import pypandoc
            _pypandoc_available = True
        except ImportError:
            _pypandoc_available = False
        finally:
            _pypandoc_checked = True

    return _pypandoc_available
```

### Modified Files

**`src/main.py` (-37 lines):**
- Removed top-level imports
- Added comment explaining lazy import strategy
- Modules load on first use

**`src/asciidoc_artisan/core/constants.py` (+12 lines):**
- Added `is_pandoc_available()` function with lazy evaluation
- Global state caching for single evaluation
- Import happens when function first called

### Module Loading Strategy

**Eager (startup):**
- PySide6 core modules (required)
- Application settings
- Core constants

**Lazy (on first use):**
- pypandoc (when exporting to formats)
- asciidoc3 (when rendering preview)
- document_converter (when importing docs)
- pymupdf/fitz (when reading PDFs)
- ollama (when AI features enabled)

### Testing

**Verification:**
```bash
# Test startup time
time python src/main.py --version

# Before: ~3-5s
# After: ~2-3s (or better)
```

**Test files:**
- Existing tests continue to work
- No new tests needed (transparent change)

### Critical Patterns for Lazy Imports

**IMPORTANT:** Each function that uses a lazily-imported module MUST import it within its own scope.

**❌ INCORRECT - Helper method can't see parent's import:**
```python
def parent_function():
    import pypandoc  # Only visible in parent scope
    return helper_function()

def helper_function():
    # ❌ NameError: pypandoc not defined!
    pypandoc.convert_text(...)
```

**✅ CORRECT - Each function imports what it needs:**
```python
def parent_function():
    import pypandoc  # Parent has its own import
    return helper_function()

def helper_function():
    import pypandoc  # Helper has its own import ✓
    pypandoc.convert_text(...)
```

**Why This Matters:**
- Python function scopes are isolated
- Imports inside a function are only visible within that function
- Helper methods called by a function don't inherit the caller's imports
- This caused a critical production bug (November 6, 2025 - Issue #13 follow-up)

**Real-World Example (pandoc_worker.py):**
```python
def run_pandoc_conversion(self, source, to_format, from_format, ...):
    """Main conversion method."""
    import pypandoc  # ✓ Import for this function

    # ... validation logic ...

    # Call helper method
    return self._execute_pandoc_conversion(source, to_format, ...)

def _execute_pandoc_conversion(self, source, to_format, ...):
    """Helper method that actually does conversion."""
    import pypandoc  # ✓ MUST have its own import!

    # Use pypandoc here
    converted = pypandoc.convert_text(...)
    return converted
```

### Testing Lazy Imports

**IMPORTANT:** Module-level patching doesn't work with lazy imports. Use pytest fixtures with sys.modules injection.

**❌ INCORRECT - Module-level patch fails:**
```python
@patch("asciidoc_artisan.workers.pandoc_worker.pypandoc")
def test_conversion(mock_pypandoc):
    # ❌ AttributeError: module does not have attribute 'pypandoc'
    # (pypandoc isn't at module level, it's inside functions)
```

**✅ CORRECT - Fixture with sys.modules injection:**
```python
import sys
from unittest.mock import Mock
import pytest

@pytest.fixture
def mock_pypandoc():
    """Fixture that mocks pypandoc in sys.modules."""
    mock_module = Mock()
    mock_module.convert_text = Mock(return_value="# Converted")
    mock_module.convert_file = Mock(return_value="# Converted from file")

    # Inject mock into sys.modules
    original = sys.modules.get("pypandoc")
    sys.modules["pypandoc"] = mock_module

    yield mock_module  # Test can use this

    # Cleanup - restore original state
    if original is not None:
        sys.modules["pypandoc"] = original
    else:
        sys.modules.pop("pypandoc", None)

def test_conversion(mock_pypandoc):
    """Test uses fixture parameter."""
    worker = PandocWorker()
    worker.run_pandoc_conversion(...)

    # Fixture mock is used inside worker
    assert mock_pypandoc.convert_text.called
```

**How It Works:**
1. Fixture injects mock into `sys.modules` before test runs
2. When worker code does `import pypandoc`, it gets the mock
3. Test can access the mock via fixture parameter
4. Cleanup ensures no side effects between tests

**Special Case - Testing "Module Not Available":**
```python
@patch("asciidoc_artisan.workers.pandoc_worker.is_pandoc_available", return_value=False)
def test_pandoc_not_available(mock_is_available):
    """Test when pypandoc is NOT installed."""
    # Manually remove pypandoc from sys.modules
    original = sys.modules.get("pypandoc")
    if "pypandoc" in sys.modules:
        del sys.modules["pypandoc"]

    try:
        worker = PandocWorker()
        # Test error handling when pypandoc missing
        worker.run_pandoc_conversion(...)
        assert error_occurred
    finally:
        # Always restore original state
        if original is not None:
            sys.modules["pypandoc"] = original
```

### Lessons Learned (Critical Bug - November 6, 2025)

**Issue #13 Follow-up:** Incomplete lazy import refactoring caused critical production bug.

**Bug:** App crashed (segfault, exit code 139) when opening files
- Error: `NameError: name 'pypandoc' is not defined` at `pandoc_worker.py:371`
- Cause: Helper method `_execute_pandoc_conversion()` used pypandoc without importing it
- Impact: 100% of users couldn't open or convert files

**Root Cause:**
- Issue #13 added lazy import to parent method `run_pandoc_conversion()`
- Forgot to add lazy import to helper method `_execute_pandoc_conversion()`
- Helper methods need explicit imports (don't inherit from parent)

**Fix:** Added 1 line `import pypandoc` in helper method

**Why Tests Didn't Catch It:**
- Tests used module-level patching: `@patch("module.pypandoc")`
- This worked when pypandoc was at module level
- But with lazy imports, pypandoc only exists inside functions
- Tests needed fixture-based mocking (sys.modules injection)

**Prevention:**
1. ✅ Search for ALL usages when refactoring, including helper methods
2. ✅ Use grep to find all references: `grep -rn "pypandoc\." src/`
3. ✅ Update test infrastructure to match code patterns
4. ✅ Test production builds, not just unit tests
5. ✅ Each function imports what it uses (no assumptions about parent scope)

**Test Results After Fix:**
- Production: ✅ File opening/conversion works correctly
- Unit tests: ✅ 51/51 passing (100%)
- Manual testing: ✅ Verified app launches and converts files successfully

**Documentation:**
- `docs/completed/2025-11-06-critical-pypandoc-bugfix.md` - Full incident report

---

## Performance Summary (v1.5.0)

| Metric | v1.4.0 | v1.5.0 | Improvement |
|--------|--------|--------|-------------|
| Startup | 3-5s | 1.05s | **3-5x faster** |
| Code size | 1,719 lines | 577 lines | **66% reduction** (main_window.py) |
| Test coverage | 34% | 60%+ | **+26 points** |
| Total tests | ~400 | 481+ | **+88 tests** |
| Duplication | 60% | <30% | **50% reduction** (preview handlers) |

---

## Architecture Evolution

### v1.4.0 → v1.5.0 Changes

**Worker Management:**
- v1.4.0: Individual QThread workers
- v1.5.0: Centralized worker pool + legacy workers

**Main Window:**
- v1.4.0: 1,719 lines (monolithic)
- v1.5.0: 577 lines (modular with managers)

**Operations:**
- v1.4.0: Non-cancellable
- v1.5.0: Cancellable via UI button

**Imports:**
- v1.4.0: Eager loading (slow startup)
- v1.5.0: Lazy loading (fast startup)

**Code Quality:**
- v1.4.0: 34% test coverage
- v1.5.0: 60%+ test coverage

---

## Related Documentation

**Current Development:**
- [ROADMAP_v1.5.0.md](../ROADMAP_v1.5.0.md) - v1.6.0 tasks in progress
- [CLAUDE.md](../CLAUDE.md) - Architecture overview and coding standards

**Requirements:**
- [SPECIFICATIONS.md](../SPECIFICATIONS.md) - Functional requirements (FR-001 to FR-053)

**User Documentation:**
- [README.md](../README.md) - Installation and usage guide

---

**Last Updated:** October 28, 2025
**Applies To:** AsciiDoc Artisan v1.5.0+
**Next:** See ROADMAP_v1.5.0.md for v1.6.0 tasks
