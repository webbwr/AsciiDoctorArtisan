# Testing Guide

Comprehensive guide to testing AsciiDoc Artisan.

**Version:** 2.0.7+ | **For:** Contributors and developers

---

## Table of Contents

1. [Overview](#overview)
2. [Test Organization](#test-organization)
3. [Running Tests](#running-tests)
4. [Writing Unit Tests](#writing-unit-tests)
5. [Writing Integration Tests](#writing-integration-tests)
6. [Writing E2E Tests](#writing-e2e-tests)
7. [Qt/GUI Testing](#qtgui-testing)
8. [Test Fixtures](#test-fixtures)
9. [Mocking Strategies](#mocking-strategies)
10. [Coverage](#coverage)
11. [Best Practices](#best-practices)

---

## Overview

### Testing Philosophy

**Test Pyramid:**
```
         /\
        /E2E\      10% - E2E workflow tests
       /------\
      /Integr \   20% - Integration tests
     /----------\
    /   Unit     \ 70% - Unit tests
   /--------------\
```

**Goals:**
- **96%+ coverage** - High code coverage
- **100% pass rate** - All tests must pass
- **Fast execution** - Unit tests < 1 second
- **Maintainable** - Clear, readable tests

### Current Statistics

- **Unit/Integration tests:** 5,548 total (5,516 passing, 22 skipped) - 99.42% pass rate
- **E2E/BDD tests:** 71 scenarios across 10 suites (63 passing) - 88.7% pass rate
- **Overall:** 5,619 tests (5,579 passing, 32 skipped, 8 investigating) - 99.3% pass rate
- **Coverage:** 96%
- **Execution time:** ~30 seconds (full suite)

---

## Test Organization

### Directory Structure

```
tests/
├── unit/                      # Unit tests (70%)
│   ├── core/                 # Core module tests
│   │   ├── test_settings.py
│   │   ├── test_gpu_detection.py
│   │   ├── test_file_operations.py
│   │   └── ...
│   ├── ui/                   # UI component tests
│   │   ├── test_main_window.py
│   │   ├── test_menu_manager.py
│   │   ├── test_theme_manager.py
│   │   └── ...
│   ├── workers/              # Worker tests
│   │   ├── test_git_worker.py
│   │   ├── test_pandoc_worker.py
│   │   └── ...
│   └── claude/               # Claude AI tests
│       ├── test_claude_client.py
│       └── test_claude_worker.py
├── integration/              # Integration tests (20%)
│   ├── test_git_integration.py
│   ├── test_pandoc_integration.py
│   └── test_ui_integration.py
├── e2e/                      # End-to-end tests (10%)
│   ├── conftest.py
│   ├── features/
│   │   ├── document_editing.feature
│   │   ├── export_workflows.feature
│   │   └── git_operations.feature
│   └── step_defs/
│       ├── document_steps.py
│       └── export_steps.py
├── performance/              # Performance tests
│   ├── test_benchmarks.py
│   └── test_performance_baseline.py
└── conftest.py               # Shared fixtures

```

### Test Naming Conventions

**Files:**
- `test_<module>.py` - Basic tests
- `test_<module>_extended.py` - Extended tests
- `test_<module>_coverage.py` - Coverage improvement tests

**Functions:**
- `test_<what_it_tests>` - Descriptive names
- `test_<class>_<method>` - Class method tests
- `test_<feature>_<scenario>` - Feature tests

**Examples:**
```python
# Good names
def test_settings_get_returns_default():
    pass

def test_git_worker_commit_with_message():
    pass

def test_main_window_opens_file():
    pass

# Bad names
def test_1():
    pass

def test_stuff():
    pass
```

---

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/core/test_settings.py -v

# Run specific test
pytest tests/unit/core/test_settings.py::test_settings_get -v

# Run tests for specific module
pytest tests/unit/core/ --cov=asciidoc_artisan.core --cov-report=term-missing
```

### Common Commands

```bash
# Fast tests only (unit, no slow markers)
make test-fast

# Unit tests only
make test-unit

# Integration tests
make test-integration

# E2E tests
pytest tests/e2e/ -v

# With coverage
pytest tests/ --cov=src/asciidoc_artisan --cov-report=html

# Specific marker
pytest -m "not live_api"  # Skip live API tests
pytest -m "requires_gpu"  # Only GPU tests

# Parallel execution (if supported)
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Very verbose
pytest tests/ -vv
```

### Test Markers

Configured in `pyproject.toml`:

```python
@pytest.mark.unit  # Unit test
@pytest.mark.integration  # Integration test
@pytest.mark.gui  # GUI test (uses qtbot)
@pytest.mark.slow  # Slow test (>1 second)
@pytest.mark.live_api  # Requires live API (skip in CI)
@pytest.mark.requires_gpu  # Requires GPU hardware
@pytest.mark.performance  # Performance test
```

**Usage:**
```python
@pytest.mark.slow
@pytest.mark.integration
def test_large_document_export():
    """Test exporting large document (slow)."""
    pass
```

---

## Writing Unit Tests

### Basic Unit Test

```python
def test_settings_get_default():
    """Test getting non-existent setting returns default."""
    settings = Settings()
    result = settings.get('nonexistent.key', 'default_value')
    assert result == 'default_value'
```

### Testing Classes

```python
class TestFileManager:
    """Tests for FileManager class."""

    def test_new_file_clears_editor(self, mock_parent):
        """Test new file clears editor content."""
        manager = FileManager(mock_parent)
        manager.new_file()

        mock_parent.editor.clear.assert_called_once()
        assert manager.current_file is None
        assert manager.is_modified is False

    def test_save_file_writes_content(self, mock_parent, tmp_path):
        """Test saving file writes content to disk."""
        manager = FileManager(mock_parent)
        test_file = tmp_path / "test.adoc"
        manager.current_file = str(test_file)

        mock_parent.editor.toPlainText.return_value = "= Test Content"

        manager.save_file()

        assert test_file.exists()
        assert test_file.read_text() == "= Test Content"
```

### Testing Exceptions

```python
def test_open_file_handles_missing_file(mock_parent):
    """Test opening missing file shows error."""
    manager = FileManager(mock_parent)

    with pytest.raises(FileNotFoundError):
        manager.open_file("/nonexistent/file.adoc")
```

---

## Writing Integration Tests

### Testing External Tools

```python
@pytest.mark.integration
def test_pandoc_conversion():
    """Test Pandoc converts Markdown to AsciiDoc."""
    markdown = "# Heading\n\nParagraph"

    converter = PandocConverter()
    asciidoc = converter.convert(markdown, 'markdown', 'asciidoc')

    assert "= Heading" in asciidoc
    assert "Paragraph" in asciidoc
```

### Testing Git Integration

```python
@pytest.mark.integration
def test_git_commit(git_repo, tmp_path):
    """Test committing changes to Git repository."""
    # Setup
    test_file = tmp_path / "test.adoc"
    test_file.write_text("= Test")

    worker = GitWorker()
    worker.repo_path = str(tmp_path)

    # Execute
    result = worker.commit("Test commit")

    # Verify
    assert result['success'] is True
    assert "Test commit" in result['message']
```

---

## Writing E2E Tests

### E2E Testing Philosophy

**Goal:** Verify user-facing workflows work correctly without testing implementation details.

**Key principles:**
1. **Test mechanisms, not exact outputs** - Verify functionality exists and works, not specific strings
2. **Stakeholder-readable** - Use Gherkin syntax for business-readable scenarios
3. **Isolation-aware** - Tests may pass individually but fail in suites due to Qt state cleanup
4. **API-consistent** - Keep step definitions aligned with current API signatures

**Current status:** 71 scenarios across 10 test suites, 88.7% pass rate (63/71 passing)

### Test Suites

**Available E2E test suites** (`tests/e2e/features/`):
- `document_editing.feature` - Create, edit, save documents (14/14 passing ✅)
- `export_functionality.feature` - Export to PDF/HTML/DOCX (6/6 passing ✅)
- `git_integration.feature` - Git operations (7/7 passing ✅)
- `user_preferences.feature` - Settings and preferences (6/8 passing ⏸️)
- `syntax_checking.feature` - Real-time validation (8/9 passing ⏸️)
- `autocomplete.feature` - Code completion (6/6 passing ✅)
- `ollama_integration.feature` - AI chat (6/6 individual ⏸️)
- `spell_check.feature` - Spell checking (6 scenarios, skipped - threading issues)
- `find_replace.feature` - Search operations (7/7 passing ✅)
- `document_tabs.feature` - Multi-document (7/7 passing ✅)

See `tests/e2e/E2E_TEST_STATUS.md` for detailed status and investigation notes.

### Using pytest-bdd

**1. Create feature file** (`tests/e2e/features/document_editing.feature`):
```gherkin
Feature: Document Editing
  As a user
  I want to edit documents
  So that I can write documentation

  Background:
    Given the application is running

  Scenario: Create new document
    When I create a new document
    Then the editor should be empty
    And the window title should contain "Untitled"

  Scenario: Type and save content
    Given I have created a new document
    When I type "= My Document" in the editor
    And I save the document as "test.adoc"
    Then the file should exist
    And the document should have no unsaved changes
```

**2. Write step definitions** (`tests/e2e/step_defs/document_steps.py`):
```python
"""
Step definitions for document editing E2E tests.

Implements Gherkin steps for document creation, editing, and saving.
"""
import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from asciidoc_artisan.ui.main_window import AsciiDocEditor

# Load all scenarios from the feature file
pytestmark = [pytest.mark.e2e, pytest.mark.bdd, pytest.mark.gui]
scenarios("../features/document_editing.feature")

# Background step - runs before each scenario
@given("the application is running")
def application_running(app: AsciiDocEditor) -> AsciiDocEditor:
    """Verify application is running and ready."""
    assert app.isVisible(), "Application window should be visible"
    return app

@when("I create a new document")
def create_new_document(app: AsciiDocEditor):
    """Create a new document."""
    app.file_manager.new_file()

@then("the editor should be empty")
def editor_empty(app: AsciiDocEditor):
    """Verify editor is empty."""
    assert app.editor.toPlainText() == "", "Editor should be empty"

@then(parsers.parse('the window title should contain "{text}"'))
def window_title_contains(app: AsciiDocEditor, text: str):
    """Verify window title contains text."""
    assert text in app.windowTitle(), f"Window title should contain '{text}'"
```

### E2E Testing Patterns

**Pattern 1: Verify mechanisms, not exact outputs**
```python
# ❌ BAD - Tests implementation details
@then("I should see 3 auto-completion suggestions")
def see_suggestions(app):
    suggestions = app.autocomplete_manager.get_suggestions()
    assert len(suggestions) == 3

# ✅ GOOD - Tests mechanism works
@then("I should see auto-completion suggestions")
def see_suggestions(app):
    widget = app.autocomplete_manager.widget
    assert widget is not None, "Auto-completion widget exists"
    assert hasattr(app, "autocomplete_manager"), "Manager initialized"
```

**Pattern 2: Handle API signatures correctly**
```python
# ❌ BAD - Old API signature
app.chat_panel.add_user_message("Hello", "2025-11-20")

# ✅ GOOD - Current API signature
model = app.chat_bar.get_current_model()
context_mode = app.chat_bar.get_current_context_mode()
app.chat_panel.add_user_message("Hello", model, context_mode, 1732099200.0)
```

**Pattern 3: Handle private attributes**
```python
# ❌ BAD - Assumes public attribute
settings_file = app.settings_manager.settings_path

# ✅ GOOD - Uses private attribute correctly
settings_file = app._settings_manager._settings_path
```

**Pattern 4: Use state tracking fixtures**
```python
class TestState:
    """Track test operation state."""
    def __init__(self):
        self.messages_sent = []
        self.responses_received = []

@pytest.fixture
def test_state():
    """Provide test state tracking."""
    return TestState()

@when("I send a message")
def send_message(app, test_state, qtbot):
    message = "Test message"
    test_state.messages_sent.append(message)
    app.send_message(message)
    qtbot.wait(100)
```

### Common Issues and Solutions

**Issue 1: Tests pass individually but fail in suites**

**Cause:** pytest-qt teardown doesn't fully clean Qt application state

**Solution:** Document in E2E_TEST_STATUS.md, run individually for verification:
```bash
pytest tests/e2e/step_defs/ollama_steps.py::test_send_message -v
```

**Issue 2: Threading-related hangs**

**Cause:** Qt event loop + QTimer + worker thread interaction deadlocks

**Solution:** Skip tests with clear documentation:
```python
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skip(
        reason="KNOWN ISSUE: Hangs in toggle_spell_check() - Qt threading. "
        "Feature works in production, E2E tests need thread isolation."
    ),
]
```

**Issue 3: Unused variables in step definitions**

**Cause:** Capturing results that aren't actually verified

**Solution:** Remove unused assignments:
```python
# ❌ BAD - 'result' unused
result = subprocess.run([...])  # F841: assigned but never used

# ✅ GOOD - No assignment if not needed
subprocess.run([...])
```

### Running E2E Tests

**Run all E2E tests:**
```bash
pytest tests/e2e/ -m e2e -v
```

**Run specific suite:**
```bash
pytest tests/e2e/step_defs/document_steps.py -v
```

**Run specific scenario:**
```bash
pytest tests/e2e/ -k "create_new_document" -v
```

**Run with no coverage (faster):**
```bash
pytest tests/e2e/ -m e2e -v --no-cov
```

**Skip slow/problematic tests:**
```bash
pytest tests/e2e/ -m "e2e and not live_api" -v
```

### Debugging E2E Tests

**Enable verbose output:**
```bash
pytest tests/e2e/ -v -s  # -s shows print statements
```

**Run with Qt debugging:**
```bash
QT_LOGGING_RULES="*.debug=true" pytest tests/e2e/ -v -s
```

**Check E2E status documentation:**
```bash
cat tests/e2e/E2E_TEST_STATUS.md
```

**Run single test for isolation:**
```bash
pytest tests/e2e/step_defs/file.py::test_name -v -s
```

### Best Practices

1. **Keep step definitions simple** - One action per step
2. **Use fixtures for state** - Track test state in fixture objects
3. **Use qtbot.wait()** - Give Qt event loop time to process
4. **Document known issues** - Mark skipped tests with clear reasons
5. **Verify mechanisms** - Test that features work, not exact outputs
6. **Keep APIs current** - Update step definitions when APIs change
7. **Test individually first** - Verify tests pass alone before suite runs

---

## Qt/GUI Testing

### Using pytest-qt (qtbot)

```python
def test_button_click(qtbot):
    """Test button click triggers action."""
    widget = MyWidget()
    qtbot.addWidget(widget)

    # Click button
    qtbot.mouseClick(widget.button, Qt.LeftButton)

    # Verify result
    assert widget.action_called is True
```

### Waiting for Signals

```python
def test_worker_completes(qtbot):
    """Test worker completes and emits signal."""
    worker = GitWorker()

    # Wait for signal (5 second timeout)
    with qtbot.waitSignal(worker.result_ready, timeout=5000):
        worker.run_git_command(["status"])

    # Signal emitted, test passes
```

### Waiting for Conditions

```python
def test_preview_updates(qtbot, app):
    """Test preview updates after typing."""
    app.editor.setPlainText("= Test")

    # Wait for condition (max 2 seconds)
    def preview_updated():
        return "Test" in app.preview.toHtml()

    qtbot.waitUntil(preview_updated, timeout=2000)
```

### MockParentWidget Pattern

**Problem:** PySide6 C++ rejects MagicMock parents

**Solution:** Use real QWidget with tracking

```python
# In tests/unit/ui/conftest.py
class MockParentWidget(QWidget):
    """Mock parent for testing dialogs."""

    def __init__(self):
        super().__init__()
        self.refresh_from_settings_called = False
        self.status_bar_updates = []
        self.model_changes = []

    def refresh_from_settings(self):
        self.refresh_from_settings_called = True

    def show_status_message(self, msg):
        self.status_bar_updates.append(msg)

@pytest.fixture
def mock_parent_widget(qtbot):
    """Provide mock parent widget."""
    widget = MockParentWidget()
    qtbot.addWidget(widget)
    yield widget
    widget.close()
```

**Usage:**
```python
def test_dialog_with_parent(mock_parent_widget):
    """Test dialog with real Qt parent."""
    dialog = PreferencesDialog(parent=mock_parent_widget)
    dialog.accept()

    assert mock_parent_widget.refresh_from_settings_called
```

---

## Test Fixtures

### Shared Fixtures (conftest.py)

```python
import pytest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

@pytest.fixture(scope="session")
def qapp():
    """Provide QApplication for session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

@pytest.fixture
def app(qtbot, qapp):
    """Provide main application window."""
    from asciidoc_artisan.ui.main_window import AsciiDocEditor
    window = AsciiDocEditor()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    yield window
    window.close()

@pytest.fixture
def temp_workspace(tmp_path):
    """Provide temporary workspace."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace

@pytest.fixture
def git_repo(temp_workspace):
    """Provide Git repository."""
    subprocess.run(["git", "init"], cwd=temp_workspace)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=temp_workspace
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=temp_workspace
    )
    return temp_workspace
```

---

## Mocking Strategies

### Mocking External Commands

```python
def test_git_commit_calls_subprocess(monkeypatch):
    """Test git commit calls subprocess correctly."""
    called_commands = []

    def mock_run(cmd, **kwargs):
        called_commands.append(cmd)
        return Mock(returncode=0, stdout="Success", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    worker = GitWorker()
    worker.commit("Test message")

    assert called_commands[0] == ["git", "commit", "-m", "Test message"]
```

### Mocking File Operations

```python
def test_save_file_atomic(monkeypatch, tmp_path):
    """Test atomic file save."""
    write_called = False

    def mock_atomic_save(path, content):
        nonlocal write_called
        write_called = True

    monkeypatch.setattr(
        "asciidoc_artisan.core.atomic_save_text",
        mock_atomic_save
    )

    manager = FileManager(mock_parent)
    manager.current_file = str(tmp_path / "test.adoc")
    manager.save_file()

    assert write_called
```

### Mocking Qt Dialogs

```python
def test_confirm_dialog_yes(monkeypatch):
    """Test user confirms action."""
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: QMessageBox.Yes
    )

    manager = FileManager(mock_parent)
    result = manager.confirm_discard()

    assert result is True
```

---

## Coverage

### Measuring Coverage

```bash
# Generate HTML coverage report
pytest tests/ --cov=src/asciidoc_artisan --cov-report=html

# Open report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

**By Module Type:**
- **Core modules:** 99-100% (non-threaded)
- **UI managers:** 95-99%
- **Workers (QThread):** 93-98% (threading limitations)
- **Overall project:** >96%

### Coverage Limitations

**Qt Threading:**
```python
# coverage.py cannot track QThread.run() or QRunnable
class Worker(QThread):
    def run(self):
        # This code may show as uncovered
        # even though tests verify functionality
        result = do_work()
        self.result_ready.emit(result)
```

**Solution:** Test functionality, accept lower coverage for workers.

### Finding Missing Coverage

```bash
# Show missing lines
pytest tests/unit/core/ --cov=asciidoc_artisan.core --cov-report=term-missing

# Example output:
# asciidoc_artisan/core/settings.py    95%   12-15, 42
#                                            ^^^^^^^^ Missing lines
```

---

## Best Practices

### DO:

✅ **Write descriptive test names**
```python
def test_file_manager_saves_with_atomic_write():
    pass
```

✅ **Use fixtures for setup**
```python
@pytest.fixture
def configured_manager(mock_parent):
    manager = FileManager(mock_parent)
    manager.setup()
    return manager
```

✅ **Test one thing per test**
```python
def test_new_file_clears_editor():
    """Test ONLY that new file clears editor."""
    pass

def test_new_file_resets_filename():
    """Separate test for filename reset."""
    pass
```

✅ **Use qtbot for Qt tests**
```python
def test_widget(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)  # Auto cleanup
```

✅ **Mock external dependencies**
```python
def test_without_actual_git(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mock_run)
```

### DON'T:

❌ **Don't test Qt internals**
```python
# Bad
def test_qwidget_has_show_method():
    assert hasattr(QWidget(), 'show')
```

❌ **Don't use time.sleep()**
```python
# Bad
time.sleep(1)  # Fragile and slow

# Good
qtbot.waitSignal(signal, timeout=1000)
```

❌ **Don't test multiple things**
```python
# Bad
def test_everything():
    test_save()
    test_load()
    test_export()
```

❌ **Don't ignore test failures**
```python
# Bad
@pytest.mark.skip("Fails sometimes")

# Good - Fix the test or document investigation
@pytest.mark.skip(reason="Qt font system edge case, needs investigation")
```

---

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          sudo apt-get install pandoc wkhtmltopdf
      - name: Run tests
        run: |
          pytest tests/ --cov --cov-report=xml -m "not live_api and not requires_gpu"
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Tests Hang

**Cause:** QThread not finishing

**Solution:**
```python
# Add timeout to waitSignal
with qtbot.waitSignal(worker.finished, timeout=5000):
    worker.start()
```

### ImportError in Tests

**Cause:** PYTHONPATH not set

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Qt Platform Plugin Error

**Cause:** No display available

**Solution:**
```bash
# Use offscreen platform
export QT_QPA_PLATFORM=offscreen
pytest tests/
```

---

## Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

### Project Files

- `pyproject.toml` - Test configuration
- `tests/conftest.py` - Shared fixtures
- `tests/unit/ui/conftest.py` - UI test fixtures
- `tests/e2e/conftest.py` - E2E test fixtures

### Tools

- `make test` - Run all tests
- `make test-fast` - Fast tests only
- `make test-unit` - Unit tests
- `pytest --markers` - List all markers

---

**Questions?** See contributing.md or ask on GitHub!
