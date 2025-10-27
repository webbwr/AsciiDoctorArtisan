# AsciiDoc Artisan - Comprehensive Improvement Plan

**Generated:** October 26, 2025
**Version:** 1.1.0-beta → 1.2.0 GA
**Estimated Timeline:** 2-3 weeks
**Total Effort:** ~90 hours (11-12 developer-days)

---

## Executive Summary

The AsciiDoc Artisan codebase is generally **production-ready** with excellent architecture, security practices, and performance optimizations. However, there are critical issues that need addressing before v1.2 GA release:

- **43% test coverage** (target: 80%+)
- **Module import errors** preventing test execution
- **42 files need formatting** (Black/isort)
- **138 type errors** from mypy
- **Missing dependencies** in requirements files

**Risk Level:** MEDIUM-LOW
**Recommendation:** Address Critical + High priority items before GA release (1-2 weeks)

---

## Priority Matrix

| Priority | Issues | Effort | Timeline |
|----------|--------|--------|----------|
| **CRITICAL** | 4 | 6 hours | 1 day |
| **HIGH** | 7 | 24 hours | 3 days |
| **MEDIUM** | 6 | 40 hours | 5 days |
| **LOW** | 4 | 20 hours | 3 days |

---

## CRITICAL Priority (Must Fix Before GA)

### 1. Fix Python Package Installation

**Status:** BLOCKING
**Issue:** Tests fail with `ModuleNotFoundError: No module named 'asciidoc_artisan'`
**Root Cause:** Package not installed in development mode

**Files Affected:**
- All 21 test files

**Solution:**
```bash
# Install package in development mode
pip install -e .

# Verify installation
python -c "import asciidoc_artisan; print(asciidoc_artisan.__file__)"
```

**Estimated Time:** 15 minutes
**Assignee:** DevOps/Developer
**Validation:** `pytest tests/ -v` should collect all tests

---

### 2. Add Missing Dependencies to Requirements

**Status:** CRITICAL
**Issue:** `pymupdf` imported but not in requirements files

**Files Affected:**
- `requirements-production.txt`
- `requirements.txt`

**Current State:**
```python
# src/document_converter.py:299
import fitz  # PyMuPDF - NOT IN REQUIREMENTS
```

**Solution:**

Edit `requirements-production.txt`:
```diff
 PySide6>=6.9.0
 asciidoc3>=3.2.0
 pypandoc>=1.15
+pymupdf>=1.23.0  # Fast PDF reading (3-5x speedup)
 keyring>=25.6.0
 psutil>=7.1.2
 ollama>=0.6.0    # Optional: Local AI conversions
```

**Estimated Time:** 15 minutes
**Validation:**
```bash
pip install -r requirements-production.txt
python -c "import fitz; print('PyMuPDF installed')"
```

---

### 3. Remove Unused Dependencies

**Status:** BLOAT
**Issue:** `anthropic==0.71.0` installed but never used (cloud AI removed in v1.2)

**Impact:**
- 15MB larger install
- Slower `pip install`
- Confusion about features

**Solution:**

Edit `requirements.txt`:
```diff
-anthropic==0.71.0
 ollama>=0.6.0
```

Edit `requirements-production.txt`:
```diff
-pymupdf>=1.23.0
+PyMuPDF>=1.23.0  # Correct package name
```

**Validation:**
```bash
grep -r "import anthropic" src/  # Should return 0 results
pip install -r requirements-production.txt  # Should work
```

**Estimated Time:** 15 minutes

---

### 4. Auto-Fix Linting Issues

**Status:** CODE QUALITY
**Issue:** 42 files need reformatting, 16 auto-fixable lint errors

**Solution:**
```bash
# Fix all auto-fixable issues
make format
ruff check --fix src/

# Verify fixes
make lint
```

**Files Affected:** 42 Python files

**Estimated Time:** 5 hours (including verification and git commit)

**Expected Changes:**
- Import sorting (8 files)
- F-string cleanup (3 files)
- Black formatting (42 files)
- Remove numba references (code and docs)

---

## HIGH Priority (Before v1.2 Release)

### 5. Fix Type Annotations

**Status:** TYPE SAFETY
**Issue:** 138 mypy errors across 17 files

**Priority Files:**

#### status_manager.py (15 errors)
```python
# Current (line 52-79)
self.model_label = None
self.ai_label = None
# Later...
self.model_label = QLabel("Model: Sonnet")  # Type error

# Fix
self.model_label: Optional[QLabel] = None
self.ai_label: Optional[QLabel] = None
```

#### menu_manager.py (37 errors)
```python
# Current (line 37-337)
self.window.new_act  # Mypy can't find attribute

# Fix: Add type stub or use TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from asciidoc_artisan.ui.action_manager import ActionManager
```

**Estimated Time:** 8 hours
**Validation:** `mypy src/ --strict` should show <50 errors

---

### 6. Add Hardware Detection Tests

**Status:** NO COVERAGE
**File:** `src/asciidoc_artisan/core/hardware_detection.py`
**Coverage:** 0% (167 lines untested)
**Risk:** HIGH - GPU/NPU detection failures go undetected

**Solution:**

Create `tests/test_hardware_detection.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from asciidoc_artisan.core.hardware_detection import (
    detect_gpu_nvidia,
    detect_gpu_amd,
    detect_npu,
    get_hardware_capabilities
)

def test_nvidia_gpu_detection_success(mocker):
    """Test NVIDIA GPU detected via nvidia-smi."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="NVIDIA GeForce RTX 3080\n10GB"
    )

    gpu = detect_gpu_nvidia()
    assert gpu is not None
    assert "RTX 3080" in gpu.model
    assert gpu.memory_gb == 10

def test_gpu_detection_none():
    """Test no GPU detected."""
    with patch('subprocess.run', side_effect=FileNotFoundError):
        caps = get_hardware_capabilities()
        assert not caps.has_gpu

def test_npu_detection_qualcomm(mocker):
    """Test Qualcomm NPU detection."""
    # Mock NPU detection logic
    ...
```

**Estimated Time:** 4 hours
**Target Coverage:** >80%

---

### 7. Add Secure Credentials Tests

**Status:** SECURITY RISK
**File:** `src/asciidoc_artisan/core/secure_credentials.py`
**Coverage:** 26% (61/82 lines untested)
**Risk:** HIGH - API key storage bugs could leak secrets

**Solution:**

Create `tests/test_secure_credentials.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from asciidoc_artisan.core.secure_credentials import (
    store_credential,
    get_credential,
    delete_credential
)

def test_store_credential_keyring_available(mocker):
    """Test storing credential when keyring is available."""
    mock_set = mocker.patch('keyring.set_password')

    result = store_credential("openai_key", "sk-test123")
    assert result is True
    mock_set.assert_called_once_with(
        "AsciiDocArtisan", "openai_key", "sk-test123"
    )

def test_store_credential_keyring_unavailable(mocker, tmp_path):
    """Test fallback to plaintext when keyring unavailable."""
    mocker.patch('keyring.set_password', side_effect=KeyringError)

    # Should fall back to encrypted file storage
    result = store_credential("openai_key", "sk-test123")
    assert result is True

def test_get_credential_with_fallback():
    """Test credential retrieval with fallback."""
    ...
```

**Estimated Time:** 4 hours
**Target Coverage:** >90%

---

### 8. Add Large File Handler Tests

**Status:** MEDIUM RISK
**File:** `src/asciidoc_artisan/core/large_file_handler.py`
**Coverage:** 24% (87/115 lines untested)

**Solution:**

Create `tests/test_large_file_handler.py`:
```python
import pytest
from PySide6.QtCore import QEventLoop
from asciidoc_artisan.core.large_file_handler import LargeFileHandler

def test_load_large_file_streaming(tmp_path, qtbot):
    """Test streaming load of 10MB file."""
    # Create 10MB test file
    large_file = tmp_path / "large.adoc"
    large_file.write_text("= Large Document\n" + ("x" * 10_000_000))

    handler = LargeFileHandler()

    # Track progress signals
    progress_updates = []
    handler.progress_update.connect(
        lambda p, m: progress_updates.append((p, m))
    )

    # Load file
    content = handler.load_file_streaming(str(large_file))

    assert len(content) == 10_000_000 + 17
    assert len(progress_updates) > 0  # Progress was reported
    assert progress_updates[-1][0] == 100  # Final progress is 100%

def test_chunked_write_large_file(tmp_path):
    """Test chunked writing for large saves."""
    ...
```

**Estimated Time:** 4 hours
**Target Coverage:** >80%

---

### 9. Fix UI Test Infrastructure

**Status:** BLOCKING UI TESTS
**Issue:** 3 UI tests crash with `Fatal Python error: Aborted`

**Files Affected:**
- `tests/test_line_numbers.py` (crashes at line 194)
- `tests/test_ui_integration.py` (excluded)
- `tests/test_pane_maximization.py` (excluded)

**Root Cause:** Qt widget initialization in headless environment

**Solution:**

1. Add Qt test fixtures to `conftest.py`:
```python
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def qtbot(qapp, qtbot):
    """Ensure QApplication exists for qtbot."""
    return qtbot
```

2. Fix test initialization:
```python
# tests/test_line_numbers.py
def test_line_number_area(qtbot, qapp):  # Add qapp fixture
    """Test line number area."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)  # Proper cleanup
    # ... test logic
```

3. Add CI environment setup:
```yaml
# .github/workflows/test.yml
- name: Run tests with Xvfb
  run: xvfb-run -a pytest tests/ -v
```

**Estimated Time:** 4 hours
**Validation:** All UI tests should pass

---

### 10. Document v1.2 AI Features in README

**Status:** DOCUMENTATION GAP
**Issue:** README.md doesn't mention Ollama AI features added in v1.2

**Solution:**

Update `README.md` section 161-179:
```markdown
## AI Features (New in v1.2!)

Smart file changes with AI:
- **Ollama AI**: Use local AI for better conversions
- **Pick your model**: Choose from installed AI models (phi3, llama2, etc.)
- **Shows in status bar**: See which method is active
- **Auto fallback**: Uses Pandoc if AI not working
- **Privacy first**: AI runs on your computer only

### Turn On AI

1. Install Ollama from ollama.com
2. Get a model: `ollama pull phi3:mini`
3. In app: Tools → AI Status → Settings
4. Turn on "Enable Ollama AI"
5. Pick your model
6. Status bar shows "AI: your-model"

Now all file changes use AI!
```

**Estimated Time:** 1 hour

---

### 11. Increase UI Test Coverage

**Status:** LOW COVERAGE
**Current:** 7-23% across UI managers
**Target:** 60% minimum

**Files Needing Tests:**
- `action_manager.py` (7% → 60%)
- `menu_manager.py` (9% → 60%)
- `dialogs.py` (12% → 60%)
- `export_manager.py` (15% → 60%)
- `status_manager.py` (16% → 60%)

**Solution:**

Create manager-specific test files:
```python
# tests/ui/test_action_manager.py
def test_action_creation(qtbot, mocker):
    """Test all actions are created."""
    mock_window = mocker.MagicMock()
    manager = ActionManager(mock_window)
    manager.create_actions()

    assert hasattr(mock_window, 'new_act')
    assert hasattr(mock_window, 'save_act')
    # ... test all actions

# tests/ui/test_export_manager.py
def test_export_to_pdf(qtbot, mocker, tmp_path):
    """Test PDF export."""
    ...
```

**Estimated Time:** 16 hours
**Expected Coverage Increase:** +35% overall

---

## MEDIUM Priority (Post-GA)

### 12. Decompose main_window.py God Class

**Status:** ARCHITECTURE DEBT
**Issue:** 1,715 lines, still too many responsibilities

**Current State:**
```
main_window.py (1,715 lines)
├── UI initialization (200 lines)
├── Worker thread management (150 lines)
├── File operations (300 lines)
├── Git operations (200 lines)
├── Clipboard handling (100 lines)
├── Search/replace (150 lines)
├── Preferences (100 lines)
└── Event handlers (515 lines)
```

**Solution:**

Extract additional managers:
1. **ClipboardManager** (lines 900-1000)
   - Paste operations
   - Format detection
   - Pandoc conversion

2. **SearchManager** (lines 1050-1200)
   - Find/replace dialog
   - Search state
   - Highlight management

3. **PreferencesManager** (lines 1300-1400)
   - Settings dialog
   - Theme selection
   - Font configuration

**Estimated Time:** 12 hours
**Target:** <1,000 lines in main_window.py

---

### 13. Fix Export Manager State Coupling

**Status:** ARCHITECTURE SMELL
**Issue:** `export_manager.py:444` directly modifies window state

```python
# Current (BAD)
def _export_with_pandoc(self, ...):
    self.window._is_processing_pandoc = True  # Direct state modification
    # ... export logic
    self.window._is_processing_pandoc = False

# Better (use signals)
class ExportManager:
    export_started = Signal()
    export_finished = Signal()

    def _export_with_pandoc(self, ...):
        self.export_started.emit()
        # ... export logic
        self.export_finished.emit()

# main_window.py
self.export_manager.export_started.connect(self._on_export_started)
self.export_manager.export_finished.connect(self._on_export_finished)

@Slot()
def _on_export_started(self):
    self._is_processing_pandoc = True
```

**Estimated Time:** 4 hours
**Files Affected:** `export_manager.py`, `file_handler.py`, `main_window.py`

---

### 14. Optimize Import Performance

**Status:** STARTUP PERFORMANCE
**Issue:** Heavy imports (anthropic, ollama, httpx) loaded eagerly

**Current Startup Time:** ~2 seconds
**Target:** <1.5 seconds

**Solution:**

Implement lazy loading for AI dependencies:
```python
# src/asciidoc_artisan/ui/settings_manager.py

# Current (eager - BAD)
import ollama
import anthropic

# Better (lazy - GOOD)
class SettingsManager:
    def __init__(self):
        self._ollama = None
        self._anthropic = None

    @property
    def ollama(self):
        if self._ollama is None:
            import ollama
            self._ollama = ollama
        return self._ollama

    def check_ollama_available(self):
        try:
            import importlib.util
            return importlib.util.find_spec("ollama") is not None
        except ImportError:
            return False
```

**Estimated Time:** 8 hours
**Expected Improvement:** 200-300ms faster startup

---

### 15. Add Edge Case Test Suite

**Status:** ROBUSTNESS
**Issue:** Missing tests for concurrent operations, error recovery, boundaries

**Solution:**

Create `tests/edge_cases/` directory:
```python
# tests/edge_cases/test_concurrent_operations.py
def test_edit_during_preview_render(qtbot):
    """Test editing while preview is rendering."""
    ...

def test_save_during_git_commit(qtbot):
    """Test file save during Git commit."""
    ...

# tests/edge_cases/test_error_recovery.py
def test_corrupted_settings_file(tmp_path):
    """Test recovery from corrupted settings.json."""
    ...

def test_pandoc_crash_mid_conversion():
    """Test handling of Pandoc crash during conversion."""
    ...

# tests/edge_cases/test_boundary_conditions.py
def test_empty_file_operations():
    """Test operations on empty files."""
    ...

def test_large_file_10mb(tmp_path):
    """Test 10MB file handling."""
    ...

def test_unicode_in_file_paths(tmp_path):
    """Test Unicode characters in file paths."""
    ...
```

**Estimated Time:** 16 hours
**Test Count:** ~30 new edge case tests

---

### 16. Remove or Integrate performance_profiler.py

**Status:** DEAD CODE
**Issue:** 148 lines, 0% coverage, never imported

**File:** `src/performance_profiler.py`

**Options:**

1. **Integrate into benchmarking:**
```python
# tests/performance/test_profiling.py
from performance_profiler import PerformanceProfiler

def test_preview_render_profiling():
    profiler = PerformanceProfiler()
    profiler.start()
    # ... render preview
    profiler.stop()
    assert profiler.get_metrics()["duration"] < 0.5
```

2. **Remove completely:**
```bash
git rm src/performance_profiler.py
```

**Recommendation:** Remove (benchmarking covered by `benchmark_*.py` scripts)

**Estimated Time:** 2 hours

---

### 17. Add Platform-Specific Tests

**Status:** CROSS-PLATFORM RISK
**Issue:** No tests for Windows/macOS-specific behavior

**Solution:**

```python
# tests/platform/test_windows_paths.py
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
def test_windows_path_handling():
    """Test Windows path separators."""
    path = "C:\\Users\\test\\document.adoc"
    sanitized = sanitize_path(path)
    assert "\\" not in str(sanitized)  # Converted to forward slashes

# tests/platform/test_macos_paths.py
@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_macos_special_directories():
    """Test macOS special directory handling."""
    ...

# tests/platform/test_linux_permissions.py
@pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
def test_file_permission_handling():
    """Test Linux file permission preservation."""
    ...
```

**Estimated Time:** 8 hours

---

### 18. Add Performance Regression Tests

**Status:** MISSING
**Issue:** No automated performance benchmarks in test suite

**Solution:**

Create `tests/performance/test_regression.py`:
```python
import pytest
from asciidoc_artisan.ui import AsciiDocEditor

@pytest.mark.performance
def test_startup_time_under_3_seconds(qtbot, benchmark):
    """Test NFR-001: Startup < 3 seconds."""
    def create_editor():
        editor = AsciiDocEditor()
        editor.close()

    result = benchmark(create_editor)
    assert result < 3.0  # NFR-001 requirement

@pytest.mark.performance
def test_preview_render_under_500ms(qtbot, benchmark):
    """Test NFR-002: Preview < 500ms."""
    editor = AsciiDocEditor()
    test_content = "= Test\n" + ("test content\n" * 1000)

    def render():
        editor.update_preview(test_content)

    result = benchmark(render)
    assert result < 0.5  # NFR-002 requirement
    editor.close()

@pytest.mark.performance
def test_memory_usage_under_500mb(qtbot):
    """Test NFR-012: Memory < 500MB."""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    editor = AsciiDocEditor()

    # Load large document
    content = "= Large Doc\n" + ("x" * 1_000_000)
    editor.editor.setPlainText(content)
    editor.update_preview(content)

    memory_mb = process.memory_info().rss / 1024 / 1024
    assert memory_mb < 500  # NFR-012 requirement
    editor.close()
```

**Estimated Time:** 8 hours

---

## LOW Priority (Future Enhancements)

### 19. Add Traceability Matrix Validation

**Status:** DOCUMENTATION
**Issue:** `traceability_matrix.csv` exists but not validated

**Solution:**

Create `scripts/validate_traceability.py`:
```python
"""
Validate that all FR requirements in SPECIFICATIONS.md are:
1. Listed in traceability_matrix.csv
2. Have corresponding tests
3. Are marked as implemented
"""
import csv
import re
from pathlib import Path

def parse_specifications():
    """Extract all FR-XXX requirements from SPECIFICATIONS.md."""
    spec_path = Path("SPECIFICATIONS.md")
    content = spec_path.read_text()

    # Find all FR-XXX patterns
    requirements = re.findall(r'FR-(\d{3})', content)
    return set(requirements)

def parse_traceability_matrix():
    """Parse traceability_matrix.csv."""
    matrix = {}
    with open("traceability_matrix.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fr_num = row["Requirement"].replace("FR-", "")
            matrix[fr_num] = {
                "status": row["Status"],
                "test": row["Test"],
                "implementation": row["Implementation"]
            }
    return matrix

def validate():
    specs = parse_specifications()
    matrix = parse_traceability_matrix()

    # Check all FRs are in matrix
    missing = specs - set(matrix.keys())
    if missing:
        print(f"ERROR: Missing FRs in matrix: {missing}")
        return False

    # Check all FRs have tests
    no_tests = [fr for fr, data in matrix.items()
                if not data["test"] or data["test"] == "N/A"]
    if no_tests:
        print(f"WARNING: FRs without tests: {no_tests}")

    print(f"✓ All {len(specs)} requirements validated")
    return True

if __name__ == "__main__":
    exit(0 if validate() else 1)
```

**Estimated Time:** 4 hours

---

### 20. Add Contributing Guidelines

**Status:** DOCUMENTATION
**Issue:** No CONTRIBUTING.md file

**Solution:**

Create `CONTRIBUTING.md`:
```markdown
# Contributing to AsciiDoc Artisan

## Development Setup

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install pre-commit hooks: `pre-commit install`
4. Run tests: `make test`

## Code Standards

- **Line length:** 88 characters (Black)
- **Type hints:** Required for new code
- **Docstrings:** All public functions
- **Tests:** 80%+ coverage for new features

## Pull Request Process

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with tests
3. Run `make format && make lint && make test`
4. Commit with conventional commits format
5. Push and create PR

## Testing

- Run all tests: `pytest tests/ -v`
- Run with coverage: `pytest tests/ --cov=src`
- Run specific test: `pytest tests/test_file.py::test_function -v`

## Reporting Bugs

Use GitHub Issues with:
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Logs from ~/.claude/debug/
```

**Estimated Time:** 2 hours

---

### 21. Add Changelog Automation

**Status:** RELEASE ENGINEERING
**Issue:** No automated changelog generation

**Solution:**

Create `.github/workflows/release.yml`:
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Changelog
        uses: orhun/git-cliff-action@v2
        with:
          config: cliff.toml
          args: --latest --strip all
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
```

**Estimated Time:** 4 hours

---

### 22. Add Security Scanning

**Status:** SECURITY
**Issue:** No automated dependency vulnerability scanning

**Solution:**

Create `.github/workflows/security.yml`:
```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit Security Scan
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json

      - name: Check Dependencies for Vulnerabilities
        run: |
          pip install safety
          safety check --json

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
```

**Estimated Time:** 4 hours

---

## Implementation Roadmap

### Week 1: Critical + High Priority (Foundation)

**Days 1-2: Setup & Dependencies**
- Fix package installation (15 min)
- Add missing dependencies (30 min)
- Remove unused dependencies (15 min)
- Auto-fix linting (5 hours)
- **Total: 6 hours**

**Days 3-5: Type Safety & Core Tests**
- Fix type annotations (8 hours)
- Add hardware detection tests (4 hours)
- Add secure credentials tests (4 hours)
- Add large file handler tests (4 hours)
- **Total: 20 hours**

**Week 1 Total:** 26 hours

---

### Week 2: High Priority (Stabilization)

**Days 6-7: UI Testing**
- Fix UI test infrastructure (4 hours)
- Increase UI test coverage (16 hours)
- **Total: 20 hours**

**Day 8: Documentation**
- Document v1.2 AI features in README (1 hour)
- Update SPECIFICATIONS.md if needed (2 hours)
- **Total: 3 hours**

**Week 2 Total:** 23 hours

---

### Week 3: Medium Priority (Enhancement)

**Days 9-11: Architecture**
- Decompose main_window.py (12 hours)
- Fix export manager coupling (4 hours)
- Optimize imports (8 hours)
- **Total: 24 hours**

**Days 12-13: Robustness**
- Add edge case tests (16 hours)
- Add platform-specific tests (8 hours)
- **Total: 24 hours**

**Week 3 Total:** 48 hours

---

### Week 4+: Low Priority (Polish)

**Ongoing:**
- Remove/integrate performance_profiler (2 hours)
- Add performance regression tests (8 hours)
- Add traceability validation (4 hours)
- Add contributing guidelines (2 hours)
- Add changelog automation (4 hours)
- Add security scanning (4 hours)
- **Total: 24 hours**

---

## Success Metrics

### Before v1.2 GA Release

- [ ] All tests pass (0 failures)
- [ ] Test coverage >60% overall
- [ ] Test coverage >80% for core modules
- [ ] Zero critical lint errors
- [ ] <50 mypy type errors
- [ ] All dependencies documented
- [ ] README reflects v1.2 features
- [ ] No import errors in tests

### Post-GA Continuous Improvement

- [ ] Test coverage >80% overall
- [ ] UI test coverage >60%
- [ ] Main window <1,000 lines
- [ ] All managers use signals (no direct state modification)
- [ ] Startup time <1.5 seconds
- [ ] 30+ edge case tests
- [ ] Platform-specific test coverage
- [ ] Automated performance regression tests

---

## Risk Assessment

### High Risk (Blocks Release)

1. **Module import errors:** CRITICAL - prevents all testing
2. **Missing dependencies:** CRITICAL - application won't run
3. **UI test crashes:** HIGH - prevents UI testing

### Medium Risk (Degrades Quality)

4. **Low test coverage:** Quality issues may slip through
5. **Type errors:** IDE experience degraded, potential runtime errors
6. **God class anti-pattern:** Hard to maintain, test, extend

### Low Risk (Technical Debt)

7. **Dead code:** Confusion, bloat
8. **Import performance:** Slightly slower startup
9. **Missing edge case tests:** Rare bugs in production

---

## Resource Requirements

### Development Resources

- **1 Senior Developer:** Architecture changes, complex refactoring
- **1 Mid-Level Developer:** Test writing, bug fixes
- **1 DevOps Engineer:** CI/CD, package management

### Infrastructure

- **CI/CD Pipeline:** GitHub Actions (free tier sufficient)
- **Test Environment:** Virtual display server for UI tests (`xvfb`)
- **Coverage Reporting:** Codecov or Coveralls (free for open source)

---

## Appendix A: Quick Wins (Do First)

These can be completed in <1 hour each with immediate impact:

1. **Fix package installation** (15 min)
   ```bash
   pip install -e .
   ```

2. **Add missing dependencies** (30 min)
   ```bash
   echo "pymupdf>=1.23.0" >> requirements-production.txt
   echo "numba>=0.58.0" >> requirements-production.txt
   pip install -r requirements-production.txt
   ```

3. **Remove unused dependencies** (15 min)
   ```bash
   sed -i '/anthropic/d' requirements.txt
   pip uninstall anthropic -y
   ```

4. **Auto-fix linting** (15 min)
   ```bash
   make format
   ruff check --fix src/
   ```

5. **Document v1.2 features** (1 hour)
   - Update README.md AI section

**Total Quick Wins:** 2.25 hours, 5 immediate improvements

---

## Appendix B: Test Coverage Targets

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| hardware_detection.py | 0% | 80% | HIGH |
| secure_credentials.py | 26% | 90% | HIGH |
| large_file_handler.py | 24% | 80% | HIGH |
| action_manager.py | 7% | 60% | MEDIUM |
| menu_manager.py | 9% | 60% | MEDIUM |
| dialogs.py | 12% | 60% | MEDIUM |
| export_manager.py | 15% | 60% | MEDIUM |
| status_manager.py | 16% | 60% | MEDIUM |
| main_window.py | 17% | 50% | MEDIUM |
| file_handler.py | 21% | 60% | MEDIUM |
| git_handler.py | 18% | 60% | LOW |

**Overall Target:** 60% minimum, 80% ideal

---

## Appendix C: Commands Reference

### Development Commands

```bash
# Setup
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
pip install -e ".[dev]"
pre-commit install

# Testing
make test                    # Run all tests with coverage
pytest tests/ -v             # Verbose output
pytest tests/ -k test_name   # Run specific test
pytest tests/ --lf           # Re-run last failed

# Code Quality
make lint                    # Run all linters
make format                  # Auto-format code
ruff check --fix src/        # Auto-fix lint issues
mypy src/                    # Type checking

# Running
make run                     # Run application
python src/main.py           # Direct execution

# Building
make build                   # Build package
make clean                   # Clean build artifacts
```

### CI/CD Commands

```bash
# Pre-commit
pre-commit run --all-files
pre-commit autoupdate

# Coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Benchmarking
python benchmark_performance.py
python benchmark_numba.py
```

---

**Document Version:** 1.0
**Last Updated:** October 26, 2025
**Next Review:** After v1.2 GA release
