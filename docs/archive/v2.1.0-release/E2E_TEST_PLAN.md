# E2E Integration Test Plan

**Date:** November 20, 2025
**Status:** Planning
**Version:** v2.0.6+
**Estimated Effort:** 1-2 weeks

---

## Overview

**Goal:** Add end-to-end integration tests to complement existing unit tests (96% coverage).

**Current Gap:**
- ✅ Excellent unit test coverage (5,548 tests, 96%)
- ✅ Component-level testing (managers, workers, core)
- ❌ Missing: Full workflow integration tests
- ❌ Missing: User journey validation
- ❌ Missing: Cross-component interaction tests

**Benefits:**
- Catch integration bugs that unit tests miss
- Document user workflows as executable specs
- Enable safer refactoring for v3.0.0
- Increase confidence in releases
- Complement existing unit tests

---

## Framework Selection

### Option 1: pytest-bdd (Recommended) ✅

**Pros:**
- Integrates seamlessly with existing pytest suite
- Gherkin syntax for readable scenarios
- Already have pytest-qt for GUI testing
- Minimal new dependencies
- Natural fit with current workflow

**Cons:**
- Learning curve for Gherkin syntax
- Slightly more verbose than raw pytest

**Installation:**
```bash
pip install pytest-bdd
```

### Option 2: behave

**Pros:**
- Pure BDD framework
- Great for non-technical stakeholders
- Separate from unit tests

**Cons:**
- Separate test runner
- Duplicate configuration
- Less integration with pytest

**Decision:** Use **pytest-bdd** for consistency with existing test infrastructure.

---

## Test Scenarios

### Priority 1: Core Workflows (Must Have)

#### 1. Document Creation & Editing
```gherkin
Feature: Document Creation and Editing
  As a user
  I want to create and edit AsciiDoc documents
  So that I can write documentation

  Scenario: Create new document and save
    Given the application is running
    When I create a new document
    And I type "= My Document" in the editor
    And I save the file as "test.adoc"
    Then the file "test.adoc" should exist
    And the preview should show "My Document" as heading

  Scenario: Open existing document
    Given a file "sample.adoc" exists with content "= Sample"
    When I open the file "sample.adoc"
    Then the editor should show "= Sample"
    And the preview should render the content

  Scenario: Edit and auto-save
    Given I have a document open
    When I enable auto-save
    And I type "New content"
    And I wait 3 seconds
    Then the file should be automatically saved
```

#### 2. Export Workflows
```gherkin
Feature: Document Export
  As a user
  I want to export my documents to different formats
  So that I can share them with others

  Scenario: Export to HTML
    Given I have a document open with content "= Test"
    When I select "Export > HTML"
    And I save as "output.html"
    Then the file "output.html" should exist
    And it should contain valid HTML

  Scenario: Export to PDF
    Given I have a document open with content "= Test"
    When I select "Export > PDF"
    And I save as "output.pdf"
    Then the file "output.pdf" should exist
    And it should be a valid PDF

  Scenario: Export to DOCX
    Given I have a document open
    When I export to DOCX format
    Then the DOCX file should preserve formatting
```

#### 3. Git Operations
```gherkin
Feature: Git Integration
  As a user
  I want to use Git version control
  So that I can track my document changes

  Scenario: Initialize repository and commit
    Given I have a document saved as "doc.adoc"
    And the folder is not a Git repository
    When I initialize a Git repository
    And I commit with message "Initial commit"
    Then the Git status should show clean working tree

  Scenario: Stage and commit changes
    Given I am in a Git repository
    And I have modified "doc.adoc"
    When I open the Git status dialog
    And I stage the file "doc.adoc"
    And I commit with message "Update document"
    Then the commit should succeed
    And the file should be committed

  Scenario: Quick commit workflow
    Given I have unsaved changes in "doc.adoc"
    When I press Ctrl+G
    And I enter commit message "Quick fix"
    Then the changes should be committed
```

#### 4. Find & Replace
```gherkin
Feature: Find and Replace
  As a user
  I want to search and replace text
  So that I can quickly update my documents

  Scenario: Find text
    Given I have content "Hello World\nHello Universe"
    When I press Ctrl+F
    And I search for "Hello"
    Then I should see 2 matches highlighted

  Scenario: Replace single occurrence
    Given I have content "Hello World"
    When I press Ctrl+H
    And I search for "World" and replace with "Universe"
    And I click "Replace"
    Then the content should be "Hello Universe"

  Scenario: Replace all occurrences
    Given I have content "test test test"
    When I replace all "test" with "demo"
    Then the content should be "demo demo demo"
```

#### 5. Template Usage
```gherkin
Feature: Document Templates
  As a user
  I want to use document templates
  So that I can quickly start new projects

  Scenario: Create from template
    Given I select "File > New from Template"
    When I choose the "Technical Report" template
    And I fill in the template variables:
      | Variable | Value |
      | title    | My Report |
      | author   | John Doe |
      | date     | 2025-11-20 |
    Then the document should contain the filled template

  Scenario: Browse templates
    Given I open the template browser
    When I view available templates
    Then I should see at least 6 built-in templates
```

### Priority 2: AI Features (Should Have)

#### 6. Ollama Chat Integration
```gherkin
Feature: AI Chat Assistance
  As a user
  I want to chat with AI about my documents
  So that I can get writing help

  @live_api
  Scenario: Ask question about document
    Given Ollama is running with model "llama2"
    And I have a document open
    When I open the chat panel
    And I ask "What is this document about?"
    Then I should receive an AI response

  @live_api
  Scenario: Get syntax help
    Given the chat panel is open
    When I select "AsciiDoc Syntax Help" mode
    And I ask "How do I create a table?"
    Then the AI should explain table syntax
```

### Priority 3: Advanced Features (Nice to Have)

#### 7. Spell Check
```gherkin
Feature: Spell Checking
  As a user
  I want spell checking
  So that I can avoid typos

  Scenario: Enable spell check
    Given I have content with misspelled word "wrld"
    When I press F7 to enable spell check
    Then the word "wrld" should be underlined in red

  Scenario: Accept suggestion
    Given spell check is enabled
    And the word "wrld" is misspelled
    When I right-click on "wrld"
    And I select suggestion "world"
    Then the word should be corrected to "world"
```

#### 8. Auto-Complete
```gherkin
Feature: Auto-Completion
  As a user
  I want auto-completion suggestions
  So that I can write faster

  Scenario: Trigger auto-complete
    Given I am typing in the editor
    When I type "==" and press Ctrl+Space
    Then I should see section heading suggestions

  Scenario: Accept completion
    Given auto-complete is showing suggestions
    When I select "Section Level 2"
    Then "== " should be inserted
```

---

## Test Organization

### Directory Structure
```
tests/
├── e2e/                          # End-to-end tests
│   ├── conftest.py              # Shared fixtures
│   ├── features/                # Gherkin feature files
│   │   ├── document_editing.feature
│   │   ├── export_workflows.feature
│   │   ├── git_operations.feature
│   │   ├── find_replace.feature
│   │   ├── templates.feature
│   │   ├── ai_chat.feature
│   │   ├── spell_check.feature
│   │   └── autocomplete.feature
│   └── step_defs/               # Step definitions
│       ├── __init__.py
│       ├── document_steps.py
│       ├── export_steps.py
│       ├── git_steps.py
│       ├── find_replace_steps.py
│       ├── template_steps.py
│       ├── ai_steps.py
│       ├── spell_steps.py
│       └── autocomplete_steps.py
```

### Shared Fixtures (conftest.py)
```python
import pytest
from pytestqt.qtbot import QtBot
from PySide6.QtWidgets import QApplication
from asciidoc_artisan.ui.main_window import MainWindow

@pytest.fixture
def app(qtbot: QtBot) -> MainWindow:
    """Launch application for E2E testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    return window

@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for file operations."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    return workspace

@pytest.fixture
def sample_document(temp_workspace):
    """Create sample AsciiDoc document."""
    doc = temp_workspace / "sample.adoc"
    doc.write_text("= Sample Document\n\nThis is a test.")
    return doc
```

---

## Implementation Plan

### Phase 1: Setup & Infrastructure (Days 1-2)

**Tasks:**
1. Install pytest-bdd: `pip install pytest-bdd`
2. Update requirements.txt and pyproject.toml
3. Create directory structure: `tests/e2e/`
4. Create shared fixtures in `conftest.py`
5. Write first simple feature file (document creation)
6. Implement step definitions
7. Verify test runs successfully

**Acceptance Criteria:**
- [ ] pytest-bdd installed and configured
- [ ] Directory structure created
- [ ] First E2E test passing
- [ ] Documentation for running E2E tests

### Phase 2: Core Workflows (Days 3-5)

**Tasks:**
1. Document editing scenarios (create, open, save)
2. Export workflows (HTML, PDF, DOCX)
3. Git operations (commit, push, pull)
4. Find & replace workflows
5. Template usage

**Acceptance Criteria:**
- [ ] 5+ feature files with 15+ scenarios
- [ ] All Priority 1 scenarios passing
- [ ] Covers main user workflows

### Phase 3: AI & Advanced Features (Days 6-7)

**Tasks:**
1. Ollama chat integration tests (@live_api marker)
2. Spell check workflows
3. Auto-complete scenarios
4. Error handling and edge cases

**Acceptance Criteria:**
- [ ] AI tests with proper mocking/skipping
- [ ] Advanced feature scenarios passing
- [ ] Edge case coverage

### Phase 4: Documentation & CI (Days 8-10)

**Tasks:**
1. Write E2E testing guide
2. Document running tests locally
3. Add E2E tests to CI/CD pipeline
4. Create test execution reports
5. Update CLAUDE.md with E2E info

**Acceptance Criteria:**
- [ ] Comprehensive E2E testing documentation
- [ ] CI/CD integration (optional in CI)
- [ ] Test reports generated
- [ ] CLAUDE.md updated

---

## Running E2E Tests

### Local Execution

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific feature
pytest tests/e2e/features/document_editing.feature -v

# Run with live API tests (requires Ollama)
pytest tests/e2e/ -v -m "not live_api"  # Skip live API
pytest tests/e2e/ -v -m "live_api"      # Only live API

# Run with HTML report
pytest tests/e2e/ -v --html=e2e_report.html
```

### CI/CD Integration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
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
          sudo apt-get install -y xvfb pandoc wkhtmltopdf
      - name: Run E2E tests
        run: |
          xvfb-run pytest tests/e2e/ -v -m "not live_api"
```

---

## Success Metrics

### Test Coverage
- **Target:** 10-15 E2E test scenarios
- **Coverage:** All major user workflows
- **Pass Rate:** 100% (excluding @live_api in CI)

### Quality
- **Readability:** Gherkin scenarios readable by non-developers
- **Maintainability:** Step definitions reusable across scenarios
- **Speed:** E2E suite completes in <5 minutes

### Documentation
- **Guide:** Complete E2E testing guide written
- **Examples:** Sample scenarios documented
- **CI/CD:** Integration documented

---

## Risk Mitigation

### Risk 1: Qt GUI Timing Issues
**Mitigation:** Use qtbot.wait* methods, generous timeouts

### Risk 2: External Dependencies (Pandoc, Git)
**Mitigation:** Mock external calls, use subprocess capture

### Risk 3: Test Flakiness
**Mitigation:** Proper setup/teardown, isolated workspaces

### Risk 4: Long Execution Time
**Mitigation:** Run in parallel, skip slow tests in CI

---

## Next Steps

1. ✅ Review and approve this plan
2. Create `tests/e2e/` directory structure
3. Install pytest-bdd dependency
4. Write first feature file (document_editing.feature)
5. Implement step definitions
6. Verify first test passes
7. Iterate on remaining scenarios

---

**Status:** Ready to begin
**Priority:** High (fills testing gap)
**Timeline:** 1-2 weeks
**Owner:** Development team
