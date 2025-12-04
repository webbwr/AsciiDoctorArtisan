# AsciiDoc Artisan Refactoring & Optimization Plan

**Generated:** 2025-12-02
**Codebase:** 41,009 lines across 122 files
**Architecture:** Manager pattern with 17 managers, 12 handlers

---

## Executive Summary

The codebase is production-ready with good separation of concerns. Refactoring focuses on:
1. **MA Principle compliance** - Reduce oversized classes
2. **Performance optimization** - Parallel GPU detection, caching
3. **Code deduplication** - Extract common patterns
4. **Naming consistency** - Unify handler/manager conventions

**Estimated effort:** 11-15 hours
**Expected improvement:** 20-30% maintainability, 15-20% performance gains

---

## Phase 1: Quick Wins (3-4 hours)

### 1.1 Extract Dialog Factory

**Problem:** Duplicate `_create_ok_cancel_buttons()` across 3+ files (~180 lines)

**Files affected:**
- `src/asciidoc_artisan/ui/dialogs.py`
- `src/asciidoc_artisan/ui/github_dialogs.py`
- `src/asciidoc_artisan/ui/installation_validator_dialog.py`

**Create:** `src/asciidoc_artisan/ui/dialog_factory.py`

```python
"""Dialog Factory - Reusable dialog components (MA principle extraction)."""

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QVBoxLayout, QPushButton
)

class DialogFactory:
    """Factory for creating common dialog components."""

    @staticmethod
    def create_button_box(
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        ok_handler: callable = None,
        cancel_handler: callable = None,
    ) -> QDialogButtonBox:
        """Create standard OK/Cancel button box."""
        button_box = QDialogButtonBox()
        ok_btn = button_box.addButton(ok_text, QDialogButtonBox.AcceptRole)
        cancel_btn = button_box.addButton(cancel_text, QDialogButtonBox.RejectRole)
        if ok_handler:
            ok_btn.clicked.connect(ok_handler)
        if cancel_handler:
            cancel_btn.clicked.connect(cancel_handler)
        return button_box

    @staticmethod
    def create_dialog_layout(
        title: str,
        content_widget: QWidget,
        parent: QWidget = None,
    ) -> tuple[QDialog, QVBoxLayout]:
        """Create dialog with standard layout."""
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        layout.addWidget(content_widget)
        return dialog, layout
```

**Effort:** 1 hour
**Impact:** -180 lines duplication

---

### 1.2 Cache Autocomplete Data

**Problem:** `_get_block_data()` regenerates on every provider instantiation

**File:** `src/asciidoc_artisan/core/autocomplete_providers.py` (630 lines)

**Current:**
```python
class BlockCompletionProvider:
    def __init__(self):
        self.items = self._get_block_data()  # Regenerated each time
```

**Optimized:**
```python
# Module-level cache (lazy singleton)
_BLOCK_DATA_CACHE: list[CompletionItem] | None = None
_LINK_ITEMS_CACHE: list[CompletionItem] | None = None

def _get_block_data_cached() -> list[CompletionItem]:
    """Get block data with module-level caching."""
    global _BLOCK_DATA_CACHE
    if _BLOCK_DATA_CACHE is None:
        _BLOCK_DATA_CACHE = _build_block_data()
    return _BLOCK_DATA_CACHE

class BlockCompletionProvider:
    def __init__(self):
        self.items = _get_block_data_cached()
```

**Effort:** 30 minutes
**Impact:** 50-100ms faster initialization

---

### 1.3 Debounce Status Manager Updates

**Problem:** `_update_metrics()` called on every status change

**File:** `src/asciidoc_artisan/ui/status_manager.py` (317 lines)

**Add debouncing:**
```python
from PySide6.QtCore import QTimer

class StatusManager:
    def __init__(self):
        self._metrics_timer = QTimer()
        self._metrics_timer.setSingleShot(True)
        self._metrics_timer.setInterval(200)  # 200ms debounce
        self._metrics_timer.timeout.connect(self._do_update_metrics)

    def _update_metrics(self):
        """Schedule debounced metrics update."""
        if not self._metrics_timer.isActive():
            self._metrics_timer.start()

    def _do_update_metrics(self):
        """Actually perform metrics calculation."""
        # Original _update_metrics() logic here
```

**Effort:** 30 minutes
**Impact:** Reduced CPU usage during rapid typing

---

## Phase 2: Split Oversized Managers (4-5 hours)

### 2.1 Split action_manager.py (341 lines → 5 modules)

**Problem:** 33 methods handling all menu actions in one file

**Current structure:**
```
action_manager.py (341 lines)
├── 11 file actions
├── 8 edit actions
├── 7 view actions
├── 6 git actions
├── 5 tools actions
└── 3 help actions
```

**Proposed structure:**
```
src/asciidoc_artisan/ui/actions/
├── __init__.py          # Re-exports ActionManager
├── action_manager.py    # Coordinator (80 lines)
├── file_actions.py      # File menu (60 lines)
├── edit_actions.py      # Edit menu (50 lines)
├── view_actions.py      # View menu (45 lines)
├── git_actions.py       # Git menu (40 lines)
└── tools_actions.py     # Tools + Help (50 lines)
```

**Implementation:**
1. Create `actions/` subdirectory
2. Extract action creation methods to domain-specific modules
3. Keep `ActionManager` as thin coordinator
4. Update imports in `main_window.py`

**Effort:** 2 hours
**Impact:** 65% reduction in main file, clearer organization

---

### 2.2 Split chat_manager.py (452 lines → 3 classes)

**Problem:** Handles UI + routing + backend coordination

**Proposed split:**
```
chat_manager.py (50 lines) - Coordinator
├── ChatUIController (210 lines)
│   ├── _update_panel_visibility()
│   ├── _render_messages()
│   └── _handle_user_input()
│
├── ChatMessageRouter (120 lines)
│   ├── _route_to_ollama()
│   ├── _route_to_anthropic()
│   └── _handle_response()
│
└── ChatHistoryManager (70 lines)
    ├── _load_history()
    ├── _save_history()
    └── _trim_history()
```

**Effort:** 2 hours
**Impact:** Clear separation of concerns

---

### 2.3 Split status_manager.py (317 lines → 3 classes)

**Problem:** 28 methods handling widgets + formatting + messages + dialogs

**Proposed split:**
```
status_manager.py (60 lines) - Coordinator
├── StatusBarWidgetManager (150 lines)
│   ├── _create_widgets()
│   ├── _update_git_status()
│   └── _update_document_metrics()
│
├── StatusMessageQueue (80 lines)
│   ├── show_message()
│   ├── _queue_message()
│   └── _process_queue()
│
└── StatusFormatter (30 lines)
    ├── format_error()
    ├── format_success()
    └── format_warning()
```

**Effort:** 1.5 hours
**Impact:** Easier testing, clearer responsibilities

---

## Phase 3: Performance Optimization (2-3 hours)

### 3.1 Parallelize GPU Detection

**Problem:** Sequential GPU vendor checks (~500ms total)

**File:** `src/asciidoc_artisan/core/gpu_detection.py` (743 lines)

**Current (sequential):**
```python
def detect_gpu():
    nvidia = check_nvidia_gpu()   # ~100-200ms
    amd = check_amd_gpu()         # ~100-200ms
    intel = check_intel_gpu()     # ~100-200ms
    # Total: 300-600ms sequential
```

**Optimized (parallel):**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

GPU_CHECKS = [
    ('nvidia', check_nvidia_gpu),
    ('amd', check_amd_gpu),
    ('intel', check_intel_gpu),
]

def detect_gpu_parallel() -> GPUInfo:
    """Detect GPU using parallel vendor checks."""
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(check_func): vendor
            for vendor, check_func in GPU_CHECKS
        }
        for future in as_completed(futures, timeout=3.0):
            vendor = futures[future]
            try:
                results[vendor] = future.result()
            except Exception:
                results[vendor] = None
    return _select_best_gpu(results)
```

**Effort:** 1 hour
**Impact:** 60% faster GPU detection (500ms → 200ms)

---

### 3.2 Cache Compiled Stylesheets

**Problem:** Theme CSS regenerated on every application

**File:** `src/asciidoc_artisan/ui/ui_setup_manager.py` (303 lines)

**Add caching:**
```python
_STYLESHEET_CACHE: dict[str, str] = {}

def get_cached_stylesheet(theme: str, variant: str) -> str:
    """Get stylesheet with caching."""
    cache_key = f"{theme}:{variant}"
    if cache_key not in _STYLESHEET_CACHE:
        _STYLESHEET_CACHE[cache_key] = _compile_stylesheet(theme, variant)
    return _STYLESHEET_CACHE[cache_key]
```

**Effort:** 30 minutes
**Impact:** Instant theme switching after first load

---

### 3.3 Optimize Template Parsing

**Problem:** Templates re-parsed on every file load

**File:** `src/asciidoc_artisan/core/template_manager.py` (539 lines)

**Add hash-based caching:**
```python
import hashlib

_TEMPLATE_CACHE: dict[str, Template] = {}

def get_cached_template(content: str) -> Template:
    """Get parsed template with content-hash caching."""
    content_hash = hashlib.md5(content.encode()).hexdigest()
    if content_hash not in _TEMPLATE_CACHE:
        _TEMPLATE_CACHE[content_hash] = parse_template(content)
    return _TEMPLATE_CACHE[content_hash]
```

**Effort:** 30 minutes
**Impact:** Faster repeated template loads

---

## Phase 4: Architectural Improvements (2-3 hours)

### 4.1 Unify Handler/Manager Naming

**Problem:** Inconsistent naming (17 managers + 12 handlers)

**Proposal:** Rename all to `*Manager` pattern

| Current Name | New Name |
|-------------|----------|
| `file_open_handler.py` | `file_open_manager.py` |
| `file_save_handler.py` | `file_save_manager.py` |
| `preview_handler.py` | `preview_manager.py` |
| `telemetry_dialog_handler.py` | `telemetry_dialog_manager.py` |
| `user_message_handler.py` | `user_message_manager.py` |

**Effort:** 1 hour (renaming + import updates)
**Impact:** Consistent naming, easier navigation

---

### 4.2 Consolidate Preview Handlers

**Problem:** Three overlapping preview files
- `preview_handler_base.py` (664 lines)
- `preview_handler.py` (extends base)
- `preview_handler_gpu.py` (extends base)

**Proposed:** Factory pattern
```python
# preview_manager.py
def create_preview_manager(use_gpu: bool = True) -> PreviewManager:
    """Factory for creating appropriate preview manager."""
    if use_gpu and gpu_available():
        return GPUPreviewManager()
    return CPUPreviewManager()

class PreviewManager(Protocol):
    """Protocol for preview rendering."""
    def render(self, content: str) -> str: ...
    def update(self) -> None: ...
```

**Effort:** 1.5 hours
**Impact:** Clearer abstraction, easier testing

---

### 4.3 Reduce main_window.py Imports

**Problem:** 40 imports creating tight coupling

**Current:**
```python
# 40+ explicit imports
from asciidoc_artisan.ui.chat_manager import ChatManager
from asciidoc_artisan.ui.status_manager import StatusManager
# ... 35 more
```

**Proposed:** Service container pattern
```python
# services.py
class ServiceContainer:
    """Dependency injection container for managers."""

    def __init__(self, settings: Settings):
        self._services: dict[type, Any] = {}
        self._settings = settings

    def get(self, service_type: type[T]) -> T:
        """Get or create service instance."""
        if service_type not in self._services:
            self._services[service_type] = self._create_service(service_type)
        return self._services[service_type]

# main_window.py
container = ServiceContainer(settings)
self.status_manager = container.get(StatusManager)
self.chat_manager = container.get(ChatManager)
```

**Effort:** 2 hours
**Impact:** Decoupled manager instantiation, easier testing

---

## Implementation Order

### Week 1: Quick Wins
1. [ ] Extract dialog_factory.py (1h)
2. [ ] Cache autocomplete data (30m)
3. [ ] Debounce status updates (30m)
4. [ ] Run tests, verify no regressions

### Week 2: Manager Splits
5. [ ] Split action_manager.py (2h)
6. [ ] Split chat_manager.py (2h)
7. [ ] Split status_manager.py (1.5h)
8. [ ] Update tests for new structure

### Week 3: Performance
9. [ ] Parallelize GPU detection (1h)
10. [ ] Cache stylesheets (30m)
11. [ ] Cache templates (30m)
12. [ ] Performance benchmarks

### Week 4: Architecture
13. [ ] Unify naming conventions (1h)
14. [ ] Consolidate preview handlers (1.5h)
15. [ ] Implement service container (2h)
16. [ ] Final testing and documentation

---

## Risk Assessment

| Change | Risk Level | Mitigation |
|--------|-----------|-----------|
| Dialog factory | Low | New file, no breaking changes |
| Cache additions | Low | Optional feature flags |
| Manager splits | Medium | Careful import management |
| Naming changes | Medium | Automated refactoring tools |
| Service container | Medium | Gradual migration |
| Preview consolidation | Medium | Keep backward compatibility |

---

## Success Metrics

| Metric | Before | Target | Measurement |
|--------|--------|--------|-------------|
| Largest manager | 452 lines | <250 lines | `wc -l` |
| action_manager.py | 341 lines | 80 lines | `wc -l` |
| GPU detection | ~500ms | ~200ms | Benchmark |
| main_window imports | 40 | <25 | grep count |
| Code duplication | ~180 lines | ~0 | Analysis |
| mypy errors | 0 | 0 | `make lint` |
| Test pass rate | 99.4% | 99.4%+ | `make test` |

---

## MA Principle Compliance Checklist

- [ ] No manager exceeds 300 lines
- [ ] Each class has single responsibility
- [ ] Methods under 50 lines
- [ ] Clear module boundaries
- [ ] Minimal cross-module dependencies
- [ ] Lazy loading where appropriate
- [ ] Cached expensive computations

---

*Plan generated by Claude Code analysis on 2025-12-02*
