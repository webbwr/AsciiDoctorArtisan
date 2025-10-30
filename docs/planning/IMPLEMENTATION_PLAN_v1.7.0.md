# v1.7.0 Implementation Plan
## Detailed Prioritized Execution Strategy

**Created:** October 29, 2025
**Target Release:** March 31, 2026
**Duration:** 12-14 weeks (Q1 2026)
**Total Effort:** 136-160 hours

---

## Executive Summary

This plan combines v1.7.0 feature development with critical QA initiatives to achieve:
- **Quality Score:** 82/100 → 95/100 (LEGENDARY)
- **Test Coverage:** 60% → 100%
- **Test Reliability:** 76.2% passing → 100% passing
- **Essential Features:** Find/Replace, Type Hints, Telemetry

**Strategy:** Execute QA Phase 1 (P0) first to unblock CI, then interleave features with QA work.

---

## Priority Classification

| Priority | Description | Blocking | Timeline |
|----------|-------------|----------|----------|
| **P0** | CRITICAL - Blocks release | Yes | Week 1-2 |
| **P1** | HIGH - Essential for v1.7.0 | Partially | Week 3-8 |
| **P2** | MEDIUM - Quality improvement | No | Week 9-12 |
| **P3** | LOW - Nice-to-have | No | Post-v1.7.0 |

---

## Implementation Schedule

### Week 1-2: CRITICAL FIXES (P0)
**Focus:** Fix broken tests, enable CI/CD
**Effort:** 20 hours
**Team:** 1 developer, full-time

---

#### Task P0-1: Fix Test Fixture Incompatibility
**Priority:** P0 | **Effort:** 8 hours | **Blocker:** YES

**Problem:** 120 tests failing due to Mock/QObject incompatibility

**Files Affected:**
- `tests/test_file_handler.py` (29 tests)
- `tests/test_preview_handler_base.py` (29 tests)
- `tests/test_ui_integration.py` (34 tests)
- `tests/test_github_handler.py` (28 tests)

**Implementation Steps:**
1. **Create Qt Fixture Factory** (2h)
   ```python
   # File: tests/fixtures/qt_fixtures.py

   import pytest
   from PySide6.QtWidgets import QMainWindow, QApplication
   from PySide6.QtCore import QTimer

   @pytest.fixture
   def qapp():
       """Create QApplication instance."""
       return QApplication.instance() or QApplication([])

   @pytest.fixture
   def main_window(qapp):
       """Create real QMainWindow for tests."""
       window = QMainWindow()
       yield window
       window.close()

   @pytest.fixture
   def mock_main_window():
       """Create properly spec'd mock."""
       from unittest.mock import MagicMock
       return MagicMock(spec=QMainWindow)
   ```

2. **Update test_file_handler.py** (2h)
   - Replace all `Mock()` parents with `main_window` fixture
   - Update 29 test functions
   - Verify all tests pass

3. **Update test_preview_handler_base.py** (2h)
   - Same pattern as file_handler
   - Update 29 test functions
   - Verify all tests pass

4. **Update test_ui_integration.py** (1h)
   - Update 34 test functions
   - Verify all tests pass

5. **Update test_github_handler.py** (1h)
   - Fix fixture usage
   - Verify scaffolding works

**Success Criteria:**
- ✅ 120 test errors → 0
- ✅ All 4 test files passing
- ✅ CI pipeline green
- ✅ No regressions in other tests

**Dependencies:** None
**Blocks:** All QA work, CI/CD setup

---

#### Task P0-2: Investigate Performance Test Failure
**Priority:** P0 | **Effort:** 4 hours | **Blocker:** YES

**Problem:** `test_benchmark_multiple_edits` failing - potential regression

**Investigation Plan:**
1. **Determine if flaky** (1h)
   ```bash
   # Run test 10x
   for i in {1..10}; do
       pytest tests/performance/test_incremental_rendering_benchmark.py::test_benchmark_multiple_edits -v
   done
   ```

2. **Profile actual performance** (2h)
   - Run with cProfile
   - Compare to baseline
   - Identify any regressions
   - Check cache hit rates

3. **Fix or adjust** (1h)
   - If regression: Fix the performance issue
   - If flaky: Adjust threshold or add retry
   - Document findings

**Success Criteria:**
- ✅ Root cause identified
- ✅ Test passing reliably (10/10 runs)
- ✅ Performance baseline documented
- ✅ No actual regressions

**Dependencies:** None
**Blocks:** Performance monitoring, CI gates

---

#### Task P0-3: Implement GitHub Handler Tests
**Priority:** P0 | **Effort:** 8 hours | **Blocker:** PARTIAL

**Problem:** 30 test stubs, 0 implementations - GitHub integration untested

**Implementation:**
1. **Initialization Tests** (1h - 4 tests)
   - Test GitHubHandler creation
   - Test dependency injection
   - Test signal connections
   - Test initial state

2. **Reentrancy Guards** (1h - 3 tests)
   - Test concurrent PR creation prevention
   - Test concurrent issue creation prevention
   - Test state management

3. **Pull Request Operations** (2h - 5 tests)
   - Test create_pull_request
   - Test list_pull_requests
   - Test PR filtering
   - Test error handling
   - Test signal emission

4. **Issue Operations** (1.5h - 4 tests)
   - Test create_issue
   - Test list_issues
   - Test issue filtering
   - Test error handling

5. **Repository Operations** (0.5h - 2 tests)
   - Test get_repo_info
   - Test error handling

6. **Error Handling** (1h - 4 tests)
   - Test gh not installed
   - Test authentication failure
   - Test network errors
   - Test timeout handling

7. **Signal/Slot Connections** (0.5h - 2 tests)
   - Test result_ready signal
   - Test operation_failed signal

8. **State Management** (0.5h - 2 tests)
   - Test operation tracking
   - Test cleanup

9. **Integration Workflows** (1h - 2 tests)
   - Test end-to-end PR creation
   - Test end-to-end issue creation

10. **Cleanup** (0.5h - 2 tests)
    - Test resource cleanup
    - Test signal disconnection

**Success Criteria:**
- ✅ 30/30 tests implemented
- ✅ All tests passing
- ✅ 100% coverage of github_handler.py
- ✅ No mock leaks

**Dependencies:** Task P0-1 (fixture infrastructure)
**Blocks:** GitHub integration confidence

---

### Week 3-4: ESSENTIAL FEATURES (P1) - Part 1
**Focus:** Find & Replace, Type Hints (core modules)
**Effort:** 20-28 hours
**Team:** 1 developer, full-time

---

#### Task P1-1: Find & Replace System
**Priority:** P1 | **Effort:** 8-12 hours | **User-Facing:** YES

**Implementation:**

**Phase 1: Core Search Engine** (3-4h)
```python
# File: src/asciidoc_artisan/core/search_engine.py

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SearchMatch:
    """Represents a search match."""
    start_pos: int
    end_pos: int
    line_number: int
    matched_text: str
    context_before: str
    context_after: str

class SearchEngine:
    """Advanced search with regex support."""

    def __init__(self):
        self.case_sensitive = False
        self.whole_word = False
        self.use_regex = False

    def search(self, text: str, pattern: str) -> List[SearchMatch]:
        """Find all matches."""
        if self.use_regex:
            return self._regex_search(text, pattern)
        else:
            return self._literal_search(text, pattern)

    def replace(self, text: str, pattern: str, replacement: str,
                replace_all: bool = False) -> Tuple[str, int]:
        """Replace matches. Returns (new_text, count)."""
        # Implementation here
```

**Phase 2: UI Dialog** (3-4h)
```python
# File: src/asciidoc_artisan/ui/find_replace_dialog.py

from PySide6.QtWidgets import (
    QDialog, QLineEdit, QCheckBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel
)

class FindReplaceDialog(QDialog):
    """Find and replace dialog."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.search_engine = SearchEngine()
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # Find input
        # Replace input
        # Options: Case sensitive, Whole word, Regex
        # Buttons: Find Next, Replace, Replace All
        pass
```

**Phase 3: Editor Integration** (1-2h)
- Add Ctrl+F/Ctrl+H shortcuts
- Integrate with main_window.py
- Add highlighting for matches

**Phase 4: Testing** (1-2h)
- 25 unit tests for SearchEngine
- 15 UI tests for FindReplaceDialog
- Integration tests

**Success Criteria:**
- ✅ Ctrl+F opens find dialog
- ✅ Ctrl+H opens replace dialog
- ✅ Regex patterns work
- ✅ Case sensitive toggle works
- ✅ Whole word matching works
- ✅ Replace preview works
- ✅ 40 tests passing

**Dependencies:** None
**User Impact:** HIGH - Essential feature

---

#### Task P1-2: Type Hints (Core Modules)
**Priority:** P1 | **Effort:** 6-8 hours | **Quality:** YES

**Scope:** Add type hints to all core/ modules (19 files)

**Implementation Plan:**
1. **Audit Current State** (1h)
   - Run `mypy --strict src/asciidoc_artisan/core/`
   - Document missing hints by module
   - Identify complex types

2. **Add Hints to Core Modules** (4-6h)
   - `adaptive_debouncer.py` (0.5h)
   - `async_file_ops.py` (0.5h)
   - `async_file_watcher.py` (0.5h)
   - `constants.py` (0.25h)
   - `file_operations.py` (0.5h)
   - `gpu_detection.py` (0.5h)
   - `hardware_detection.py` (0.5h)
   - `large_file_handler.py` (0.5h)
   - `lazy_importer.py` (0.5h)
   - `lru_cache.py` (0.5h)
   - `memory_profiler.py` (0.5h)
   - `models.py` (0.25h)
   - `qt_async_file_manager.py` (0.5h)
   - `resource_manager.py` (0.5h)
   - `resource_monitor.py` (0.5h)
   - `secure_credentials.py` (0.5h)
   - `settings.py` (0.5h)

3. **Fix mypy Errors** (1h)
   - Run `mypy --strict` again
   - Fix all errors
   - Add `# type: ignore` only where necessary

**Pattern:**
```python
# Before
def process_file(path, encoding="utf-8"):
    with open(path, encoding=encoding) as f:
        return f.read()

# After
from pathlib import Path
from typing import Optional

def process_file(path: Path, encoding: str = "utf-8") -> Optional[str]:
    """Process file and return contents."""
    try:
        with open(path, encoding=encoding) as f:
            return f.read()
    except IOError:
        return None
```

**Success Criteria:**
- ✅ `mypy --strict src/asciidoc_artisan/core/` passes
- ✅ All public functions typed
- ✅ All class attributes typed
- ✅ IDE autocomplete improved
- ✅ No regressions

**Dependencies:** None

---


#### Task P1-4: Type Hints (UI Modules)
**Priority:** P1 | **Effort:** 8-10 hours | **Quality:** YES

**Scope:** Add type hints to all ui/ modules (29 files)

**Implementation:** Same pattern as Task P1-2
- Audit current state (1h)
- Add hints to all ui/ modules (6-8h)
- Fix mypy errors (1h)

**Success Criteria:**
- ✅ `mypy --strict src/asciidoc_artisan/ui/` passes
- ✅ All public APIs typed
- ✅ IDE support improved

**Dependencies:** Task P1-2
**Blocks:** Task P1-5 (workers)

---

### Week 7-8: QA COVERAGE PUSH (P1)
**Focus:** Achieve 100% test coverage
**Effort:** 38 hours
**Team:** 1 developer, full-time

---

#### Task P1-5: Cover Low-Coverage Core Modules
**Priority:** P1 | **Effort:** 12 hours | **Quality:** YES

**Target:** 6 modules, ~380 lines to cover

**Module-by-Module Plan:**

**1. adaptive_debouncer.py** (2h)
- Current: 45% → Target: 100%
- Tests needed:
  - Debounce timer behavior
  - Adaptive interval adjustment
  - Edge cases (rapid triggers)
  - Cleanup behavior

**2. lazy_importer.py** (2h)
- Current: 40% → Target: 100%
- Tests needed:
  - Lazy module loading
  - Import caching
  - Error handling (missing modules)
  - Performance (no redundant imports)

**3. memory_profiler.py** (2h)
- Current: 55% → Target: 100%
- Tests needed:
  - Memory tracking
  - Profiling context manager
  - Report generation
  - Edge cases (low memory)

**4. secure_credentials.py** (2h)
- Current: 50% → Target: 100%
- Tests needed:
  - Keyring storage/retrieval
  - Encryption/decryption
  - Error handling (no keyring)
  - Fallback mechanisms

**5. hardware_detection.py** (2h)
- Current: 40% → Target: 100%
- Tests needed:
  - GPU detection
  - CPU capability detection
  - Cache behavior
  - Mock various hardware configs

**6. gpu_detection.py** (2h)
- Current: 60% → Target: 100%
- Tests needed:
  - CUDA detection
  - OpenCL detection
  - Cache TTL behavior
  - Fallback to CPU

**Success Criteria:**
- ✅ All 6 modules at 100% coverage
- ✅ Overall project coverage ≥70%
- ✅ No flaky tests
- ✅ All tests passing

**Dependencies:** None
**Quality Impact:** HIGH

---

#### Task P1-6: Add Async Integration Tests
**Priority:** P1 | **Effort:** 6 hours | **Quality:** YES

**Tests Needed:** 15 integration tests

**Category A: Async I/O Integration** (2h - 5 tests)
1. File load → async read → UI update flow
2. File save → async write → status update flow
3. File watch → external change → reload prompt
4. Concurrent operations → queue → UI feedback
5. Error propagation through async stack

**Category B: File Watcher Integration** (2h - 5 tests)
1. Watch file → modify externally → signal emitted
2. Watch file → delete externally → signal emitted
3. Watch file → replace watcher → cleanup verified
4. Long-running watcher → no memory leak
5. Watcher cleanup on app shutdown

**Category C: Performance Integration** (2h - 5 tests)
1. Async vs sync: compare UI responsiveness
2. Large file async load: no UI freeze
3. Multiple concurrent reads: performance acceptable
4. Async save during render: no conflicts
5. Async operation queue depth: bounded

**Success Criteria:**
- ✅ 15 integration tests passing
- ✅ End-to-end async workflows verified
- ✅ No memory leaks
- ✅ UI responsiveness maintained

**Dependencies:** Task P0-1 (fixtures)
**Quality Impact:** HIGH

---

#### Task P1-7: Add Edge Case Tests
**Priority:** P1 | **Effort:** 20 hours | **Quality:** YES

**Tests Needed:** 60 edge case tests

**Category A: File Operations** (7h - 20 tests)
- Files >100MB stress test
- Binary file handling
- Locked file scenarios
- Network drive operations (slow I/O)
- Symlink handling
- Permission errors (read-only, no access)
- Concurrent file access (race conditions)
- Interrupted I/O recovery
- Disk full errors
- Invalid UTF-8 sequences
- (10 more edge cases)

**Category B: UI Edge Cases** (7h - 20 tests)
- Window at 100x100 resolution
- Window at 8K resolution
- Rapid action triggers (1000 clicks/sec)
- Theme switching during operations
- Font size at 6pt
- Font size at 72pt
- Splitter at 0%
- Splitter at 100%
- Disconnected external monitors
- High DPI displays
- (10 more edge cases)

**Category C: Worker Thread Edge Cases** (6h - 20 tests)
- Worker death/resurrection
- Signal emission during shutdown
- Queue overflow scenarios
- Deadlock detection
- Thread pool exhaustion
- Worker timeout handling
- Concurrent worker requests
- Worker cancellation mid-operation
- Signal flooding (1000s of signals)
- Memory pressure during work
- (10 more edge cases)

**Success Criteria:**
- ✅ 60 edge case tests passing
- ✅ App resilient to extreme conditions
- ✅ Graceful degradation verified
- ✅ No crashes under stress

**Dependencies:** Task P0-1 (fixtures)
**Quality Impact:** MEDIUM

---

### Week 9-10: FINAL FEATURES + QA INFRASTRUCTURE (P1-P2)
**Focus:** Telemetry, Type Hints completion, Quality gates
**Effort:** 26-30 hours
**Team:** 1 developer, full-time

---

#### Task P1-8: Type Hints (Workers Modules)
**Priority:** P1 | **Effort:** 4-6 hours | **Quality:** YES

**Scope:** Add type hints to all workers/ modules (10 files)

**Success Criteria:**
- ✅ `mypy --strict src/asciidoc_artisan/workers/` passes
- ✅ 100% type coverage achieved
- ✅ All mypy checks pass

**Dependencies:** Task P1-4
**Blocks:** None (final type hint task)

---

#### Task P1-9: Telemetry System (Opt-In)
**Priority:** P1 | **Effort:** 16-24 hours | **User-Facing:** YES

**Implementation:**

**Phase 1: Core Telemetry** (6-8h)
```python
# File: src/asciidoc_artisan/core/telemetry.py

import sentry_sdk
from typing import Dict, Any, Optional
from pathlib import Path
import json
import hashlib

class TelemetryManager:
    """Privacy-focused telemetry."""

    def __init__(self):
        self.enabled = False
        self.anonymous_id = self._generate_anonymous_id()
        self._load_settings()

    def init_sentry(self):
        """Initialize Sentry for crash reports."""
        if self.enabled:
            sentry_sdk.init(
                dsn="...",  # Sentry DSN
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                before_send=self._sanitize_event
            )

    def track_event(self, event_name: str, properties: Dict[str, Any]):
        """Track feature usage."""
        if not self.enabled:
            return

        # Sanitize properties (no PII)
        safe_properties = self._sanitize_properties(properties)

        # Send to analytics backend
        self._send_event({
            'user_id': self.anonymous_id,
            'event': event_name,
            'properties': safe_properties,
            'timestamp': datetime.utcnow().isoformat()
        })

    def _sanitize_event(self, event, hint):
        """Remove any PII from crash reports."""
        # Remove file paths, document content, etc.
        return event
```

**Phase 2: Opt-In Dialog** (3-4h)
```python
# File: src/asciidoc_artisan/ui/telemetry_dialog.py

class TelemetryConsentDialog(QDialog):
    """GDPR-compliant opt-in dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Explanation of what data is collected
        # Privacy policy link
        # "Help improve" vs "No thanks" buttons
        # "Show this later" option
        pass
```

**Phase 3: Integration** (4-6h)
- Show dialog on first launch
- Add settings toggle
- Integrate with existing code
- Track key events:
  - Feature usage (Find, Replace, Export, etc.)
  - Performance metrics (startup time, render time)
  - Error patterns (types of exceptions)
  - Document stats (size, format - anonymized)

**Phase 4: Testing** (3-6h)
- 15 unit tests
- Privacy verification
- GDPR compliance check
- Opt-out verification

**Success Criteria:**
- ✅ Clear opt-in on first launch
- ✅ Can enable/disable anytime
- ✅ No PII collected
- ✅ Privacy policy visible
- ✅ GDPR compliant
- ✅ 15 tests passing

**Dependencies:** None
**User Impact:** LOW (optional)

---

#### Task P2-1: Property-Based Testing
**Priority:** P2 | **Effort:** 8 hours | **Quality:** YES

**Tool:** Hypothesis

**Implementation:**
```python
# File: tests/test_property_based.py

from hypothesis import given, strategies as st
import hypothesis

# Configure Hypothesis
hypothesis.settings.register_profile(
    "ci",
    max_examples=1000,
    deadline=None
)

@given(st.text(min_size=0, max_size=10000))
def test_render_never_crashes(text: str):
    """Any text input should render without crashing."""
    try:
        result = render_asciidoc(text)
        assert result is not None
        assert isinstance(result, str)
    except Exception as e:
        # Only specific exceptions allowed
        assert isinstance(e, (ValueError, IOError))

@given(st.integers(min_value=6, max_value=72))
def test_font_size_always_valid(size: int):
    """Any reasonable font size should work."""
    editor = QTextEdit()
    editor.setFontPointSize(size)
    assert editor.fontPointSize() == size

@given(st.text(), st.text())
def test_search_never_crashes(text: str, pattern: str):
    """Any search pattern should be safe."""
    engine = SearchEngine()
    try:
        matches = engine.search(text, pattern)
        assert isinstance(matches, list)
    except re.error:
        pass  # Invalid regex is OK to fail
```

**Test Areas:**
- AsciiDoc rendering (fuzzing)
- File operations (random paths/content)
- Settings (random values)
- UI inputs (random actions)

**Success Criteria:**
- ✅ 20 property-based tests added
- ✅ 5+ bugs found and fixed
- ✅ Hypothesis integrated into CI
- ✅ All tests passing

**Dependencies:** None
**Quality Impact:** HIGH

---

#### Task P2-2: Performance Regression CI
**Priority:** P2 | **Effort:** 6 hours | **Quality:** YES


**Implementation:**
1. **Create Baseline File** (1h)
   ```json
   {
     "startup_time": {
       "mean": 1.05,
       "stddev": 0.05,
       "max_allowed": 1.5
     },
     "file_load_1mb": {
       "mean": 250,
       "stddev": 20,
       "max_allowed": 300
     }
   }
   ```

2. **Add Benchmark Tests** (3h)
   ```python
   # File: tests/benchmarks/test_performance.py

   def test_startup_time(benchmark):
       """Benchmark application startup."""
       def startup():
           app = QApplication([])
           window = AsciiDocEditor()
           window.close()

       result = benchmark(startup)
       assert result < 1.5  # seconds

   def test_file_load_1mb(benchmark, tmp_path):
       """Benchmark 1MB file load."""
       large_file = tmp_path / "large.adoc"
       large_file.write_text("x" * 1_000_000)

       def load():
           handler.load_file(large_file)

       result = benchmark(load)
       assert result < 0.3  # seconds
   ```

3. **Configure CI** (2h)
   ```yaml

   name: Performance Tests

   on: [pull_request, push]

   jobs:
     benchmark:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Run benchmarks
           run: |
             pytest tests/benchmarks/ --benchmark-only \
               --benchmark-compare=baseline.json \
               --benchmark-compare-fail=mean:10%
         - name: Store results
           run: |
             pytest-benchmark compare
   ```

**Success Criteria:**
- ✅ Baseline stored in repo
- ✅ CI fails on >10% regression
- ✅ Performance history tracked
- ✅ Automated alerts

**Dependencies:** Task P0-2
**Quality Impact:** HIGH

---

### Week 11-12: POLISH & RELEASE PREP (P2-P3)
**Focus:** Minor features, documentation, release
**Effort:** 18-26 hours
**Team:** 1 developer, part-time

---

#### Task P2-3: Minor Features
**Priority:** P2 | **Effort:** 18-26 hours | **User-Facing:** YES

**Features:**

**1. Improved Error Messages** (4-6h)
- User-friendly error dialogs
- Actionable error messages
- Error recovery suggestions
- Log errors to file

**2. Keyboard Shortcuts Customization** (6-8h)
- Editable keyboard shortcuts
- Conflict detection
- Import/export shortcuts
- Restore defaults

**3. Recent Files Improvements** (4-6h)
- Pin favorite files
- Clear recent files
- Show file paths on hover
- Limit recent files count (configurable)

**4. Performance Dashboard** (4-6h)
- Show metrics in UI (debug mode)
- Render time graphs
- Memory usage graphs
- Cache hit rates

**Success Criteria:**
- ✅ All 4 features working
- ✅ User documentation updated
- ✅ 20+ tests added

**Dependencies:** None
**User Impact:** MEDIUM

---

#### Task P3-1: Documentation & Release
**Priority:** P3 | **Effort:** 8-12 hours | **Essential:** YES

**Activities:**
1. **Update User Documentation** (3-4h)
   - New features guide
   - Screenshots
   - Tutorial videos (optional)

2. **Update Developer Documentation** (2-3h)
   - API changes
   - Migration guide
   - Architecture updates

3. **Release Notes** (1-2h)
   - Changelog
   - Breaking changes
   - Upgrade guide

4. **Release Testing** (2-3h)
   - Fresh install test
   - Upgrade test
   - Cross-platform verification

**Success Criteria:**
- ✅ All docs updated
- ✅ Release notes complete
- ✅ Release candidate tested

**Dependencies:** All P1 tasks
**Blocks:** Release

---

## Summary Tables

### Effort by Phase

| Phase | Duration | Effort | Tasks | Priority |
|-------|----------|--------|-------|----------|
| Week 1-2 | 2 weeks | 20h | 3 | P0 |
| Week 3-4 | 2 weeks | 20-28h | 2 | P1 |
| Week 5-6 | 2 weeks | 20-24h | 2 | P1 |
| Week 7-8 | 2 weeks | 38h | 3 | P1 |
| Week 9-10 | 2 weeks | 26-30h | 3 | P1-P2 |
| Week 11-12 | 2 weeks | 18-26h | 2 | P2-P3 |
| **TOTAL** | **12 weeks** | **142-166h** | **15 tasks** | - |

---

### Effort by Category

| Category | Effort | % of Total | Priority |
|----------|--------|------------|----------|
| QA Fixes | 58h | 37% | P0-P1 |
| Feature Development | 52-76h | 41% | P1 |
| Type Hints | 18-24h | 14% | P1 |
| Infrastructure | 14h | 9% | P2 |
| Polish | 18-26h | 13% | P2-P3 |
| **TOTAL** | **142-166h** | **100%** | - |

---

### Success Metrics

| Metric | Current | Target | % Improvement |
|--------|---------|--------|---------------|
| Test Pass Rate | 76.2% | 100% | +31% |
| Test Coverage | 60% | 100% | +67% |
| Type Coverage | 60% | 100% | +67% |
| Quality Score | 82/100 | 95/100 | +16% |
| Test Errors | 120 | 0 | -100% |
| Failing Tests | 84 | 0 | -100% |

---

## Risk Management

### High Risks

**Risk 1: QA work takes longer than estimated**
- **Probability:** MEDIUM
- **Impact:** Release delay
- **Mitigation:** Start with P0 tasks immediately, accept 90% coverage if needed

**Risk 2: Type hints introduce regressions**
- **Probability:** LOW
- **Impact:** Test failures
- **Mitigation:** Comprehensive test suite, gradual rollout

**Risk 3: Feature scope creep**
- **Probability:** MEDIUM
- **Impact:** Schedule slip
- **Mitigation:** Strict prioritization, defer P3 tasks if needed

### Medium Risks

**Risk 4: Test fixture changes break existing tests**
- **Probability:** MEDIUM
- **Impact:** Additional debugging time
- **Mitigation:** Fix one file at a time, comprehensive testing

**Risk 5: Performance optimizations don't materialize**
- **Probability:** LOW
- **Impact:** Missed optimization goals
- **Mitigation:** Already fast, optimizations are bonus

---

## Dependencies Graph

```
P0-1 (Fix Fixtures) ──┬─> P0-3 (GitHub Tests)
                      ├─> P1-6 (Async Integration Tests)
                      └─> P1-7 (Edge Case Tests)

P0-2 (Perf Test) ─────> P2-2 (Performance CI)

P1-1 (Find/Replace) ──> [No blockers]

P1-2 (Type Hints Core) ──> P1-4 (Type Hints UI) ──> P1-8 (Type Hints Workers)

P1-5 (Cover Modules) ──> [Coverage goal]
P1-6 (Async Tests) ───┬──> [Coverage goal]
P1-7 (Edge Cases) ────┘

P1-9 (Telemetry) ──> [No blockers]

P2-1 (Property Testing) ──> [No blockers]

P2-3 (Minor Features) ──> P3-1 (Documentation)

ALL P1 TASKS ──> P3-1 (Release)
```

---

## Execution Strategy

### Parallel Workstreams

**Stream 1: Critical Path (P0 → P1 features)**
```
Week 1-2: P0-1, P0-2, P0-3 (Fix tests, CI)
Week 3-4: P1-1, P1-2 (Find/Replace, Type Hints Core)
Week 5-6: P1-4 (Type Hints UI)
```

**Stream 2: QA Push (After P0 complete)**
```
Week 7-8: P1-5, P1-6, P1-7 (Coverage push)
Week 9-10: P1-8, P2-1, P2-2 (Type Hints Workers, Property tests, Perf CI)
```

**Stream 3: Polish (Final sprint)**
```
Week 11-12: P1-9, P2-3, P3-1 (Telemetry, Minor features, Docs)
```

### Weekly Checkpoints

**Every Friday:**
- Review progress vs. plan
- Update risk assessment
- Adjust priorities if needed
- Report to stakeholders

---

## Success Criteria

### Must-Have (P0-P1)
- ✅ All 120 test errors fixed
- ✅ CI/CD green and reliable
- ✅ 100% test coverage achieved
- ✅ Find & Replace working
- ✅ Type hints 100% complete
- ✅ 100% test pass rate

### Should-Have (P2)
- ✅ Property-based testing active
- ✅ Performance regression CI
- ✅ Minor features complete
- ✅ Quality score 95/100

### Nice-to-Have (P3)
- ✅ Telemetry opt-in working
- ✅ Documentation complete
- ✅ Release notes polished

---

## Conclusion

This plan provides a clear path to v1.7.0 release with legendary quality (95/100). By executing P0 tasks first, we unblock CI and enable parallel development. The interleaved approach allows continuous progress on both features and quality.

**Target:** March 31, 2026
**Confidence:** 85% (high)
**Next Step:** Begin P0-1 (Fix Test Fixtures) immediately

---

**Plan Status:** APPROVED
**Last Updated:** October 29, 2025
**Maintained By:** Development Team + Claude Code
