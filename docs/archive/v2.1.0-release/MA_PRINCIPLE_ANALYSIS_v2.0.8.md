# MA (間) Principle Analysis Report

**Project:** AsciiDoc Artisan v2.0.8
**Date:** November 21, 2025
**Analysis Type:** MA (間) Principle Compliance Audit
**Status:** VIOLATIONS FOUND

---

## Executive Summary

**MA (間) Principle:** Japanese aesthetic concept of negative space applied to code and documentation. Emphasizes simplicity, intentional whitespace, and minimal sufficiency.

**Key Findings:**
- **Codebase**: 224 violations (17 P0, 79 P1, 128 P2)
- **Documentation**: 471 violations (0 P0, 0 P1, 471 P2)
- **Total**: 695 violations across code and documentation

**Impact:** MODERATE - Critical codebase violations require immediate attention

---

## MA Principle Metrics

### Code Quality Thresholds

```yaml
code:
  max_function_length: 50      # Lines (excluding docstrings)
  max_class_length: 300        # Lines (excluding docstrings)
  max_parameters: 4            # Function parameters
  max_nesting: 3               # Nested blocks (if/for/while)
  max_complexity: 10           # Cyclomatic complexity
  max_comment_ratio: 0.15      # Comments / total lines
  min_whitespace_ratio: 0.02   # Blank lines / total lines

documentation:
  max_line_length: 88          # Characters per line
  min_whitespace_ratio: 0.02   # Blank lines in docs
  max_paragraph_lines: 10      # Lines per paragraph
  max_reading_grade: 5.0       # Flesch-Kincaid grade level
```

---

## Codebase Violations (224 Total)

### Severity Breakdown

| Severity | Count | Description |
|----------|-------|-------------|
| **P0 (Critical)** | 17 | Functions >100 lines or complexity >15 |
| **P1 (High)** | 79 | Functions >50 lines or complexity >10 |
| **P2 (Medium)** | 128 | Parameter count, nesting, comments |

### Violation Types

| Type | Count | Percentage |
|------|-------|------------|
| Function Length | 76 | 33.9% |
| Nesting Depth | 42 | 18.8% |
| Cyclomatic Complexity | 38 | 17.0% |
| Class Length | 35 | 15.6% |
| Parameter Count | 28 | 12.5% |
| Comment Ratio | 5 | 2.2% |

### Top Violators (Files)

| Rank | File | Violations | Critical |
|------|------|------------|----------|
| 1 | `ui/chat_manager.py` | 14 | 1 |
| 2 | `workers/git_worker.py` | 12 | 1 |
| 3 | `workers/pandoc_worker.py` | 9 | 0 |
| 4 | `core/gpu_detection.py` | 8 | 1 |
| 5 | `workers/github_cli_worker.py` | 7 | 1 |
| 6 | `ui/main_window.py` | 7 | 1 |
| 7 | `ui/dialog_manager.py` | 7 | 0 |
| 8 | `ui/dialogs.py` | 7 | 1 |
| 9 | `ui/installation_validator_dialog.py` | 6 | 0 |
| 10 | `ui/action_manager.py` | 6 | 2 |

### Critical P0 Violations (17 Total)

**Functions Exceeding 100 Lines:**

1. `core/__init__.py:124` - `__getattr__()` - **221 lines** ❌
2. `core/settings.py:249` - `validate()` - **218 lines** ❌
3. `ui/action_manager.py:436` - `create_actions()` - **416 lines** ❌
4. `core/autocomplete_providers.py:94` - `_build_completion_items()` - **183 lines** ❌
5. `ui/action_manager.py:893` - `create_menus()` - **159 lines** ❌
6. `ui/main_window.py:247` - `__init__()` - **157 lines** ❌
7. `ui/ui_setup_manager.py:244` - `_create_toolbar()` - **150 lines** ❌
8. `core/macos_optimizer.py:42` - `detect_macos_capabilities()` - **149 lines** ❌
9. `ui/file_operations_manager.py:351` - `save_as_format_internal()` - **148 lines** ❌
10. `ui/dialogs.py:256` - `_init_ui()` - **136 lines** ❌
11. `workers/github_cli_worker.py:111` - `run_gh_command()` - **135 lines** ❌
12. `ui/find_bar_widget.py:85` - `_setup_ui()` - **132 lines** ❌
13. `ui/telemetry_opt_in_dialog.py:91` - `_setup_ui()` - **129 lines** ❌
14. `workers/git_worker.py:69` - `run_git_command()` - **121 lines** ❌
15. `core/gpu_detection.py:486` - `detect_gpu()` - **114 lines** ❌
16. `ui/export_helpers.py:114` - `add_print_css_to_html()` - **107 lines** ❌
17. `ui/worker_manager.py:99` - `setup_workers_and_threads()` - **102 lines** ❌

**High Complexity (>15):**

- `core/settings.py:249` - `validate()` - **Complexity 77** ❌
- `core/macos_optimizer.py:42` - `detect_macos_capabilities()` - **Complexity 34** ❌
- `core/__init__.py:124` - `__getattr__()` - **Complexity 23** ❌
- `claude/claude_client.py:159` - `send_message()` - **Complexity 19** ❌

### Patterns Identified

**1. UI Setup Functions (12 violations)**
- Pattern: `_setup_ui()`, `_init_ui()`, `__init__()` methods in dialog/widget classes
- Root Cause: UI layout code not extracted to separate methods
- Example: `find_bar_widget.py:_setup_ui()` (132 lines)
- Fix: Extract widget creation, signal connections, and styling to separate methods

**2. Manager Classes (6 violations)**
- Pattern: Large manager classes (`ActionManager`, `ChatManager`, `GitWorker`, `PandocWorker`)
- Root Cause: God object pattern - too many responsibilities
- Example: `ActionManager` (978 lines total)
- Fix: Split into focused sub-managers or extract helper modules

**3. Command Execution (3 violations)**
- Pattern: `run_git_command()`, `run_gh_command()` methods
- Root Cause: Single function handles all command types + error handling
- Example: `git_worker.py:run_git_command()` (121 lines)
- Fix: Extract command-specific handlers to separate methods

**4. Validation Logic (2 violations)**
- Pattern: `validate()`, `validate_all()` methods
- Root Cause: Single method validates all fields with nested conditionals
- Example: `settings.py:validate()` (218 lines, complexity 77)
- Fix: Extract field-specific validators to separate methods

**5. Dynamic Import/Attribute Access (2 violations)**
- Pattern: `__getattr__()` methods with extensive import logic
- Root Cause: Lazy loading all imports in single method
- Example: `core/__init__.py:__getattr__()` (221 lines, complexity 23)
- Fix: Use import hooks or explicit lazy imports per module

---

## Documentation Violations (471 Total)

### Severity Breakdown

| Severity | Count | Description |
|----------|-------|-------------|
| **P0 (Critical)** | 0 | Reading grade >10 |
| **P1 (High)** | 0 | Reading grade >5 or low whitespace |
| **P2 (Medium)** | 471 | Line length >88 or paragraph >10 lines |

### Violation Types

| Type | Count | Percentage |
|------|-------|------------|
| Line Length (>88 chars) | 421 | 89.4% |
| Paragraph Length (>10 lines) | 50 | 10.6% |

### Assessment

**Overall:** Documentation violations are all low-priority (P2). Most are line length violations which can be auto-fixed with text reformatting tools.

**No Critical Issues:** No reading grade violations, indicating documentation is generally well-written and accessible.

---

## Prioritized Recommendations

### Phase 1: Critical Fixes (P0 - Must Fix)

**Priority 1.1: Monster Functions (17 functions >100 lines)**

Estimated Effort: 2-3 weeks

**Top 5 Targets:**
1. `ui/action_manager.py:create_actions()` - 416 lines → Extract action creation to category methods
2. `core/__init__.py:__getattr__()` - 221 lines → Use import hooks or explicit lazy imports
3. `core/settings.py:validate()` - 218 lines, complexity 77 → Extract field validators
4. `core/autocomplete_providers.py:_build_completion_items()` - 183 lines → Extract item builders per type
5. `ui/action_manager.py:create_menus()` - 159 lines → Extract menu builders per category

**Refactoring Strategy:**
```python
# ❌ Before (416 lines)
def create_actions(self):
    # File menu actions (50 lines)
    # Edit menu actions (40 lines)
    # View menu actions (35 lines)
    # ... (10+ more categories)

# ✅ After (split into focused methods)
def create_actions(self):
    self._create_file_actions()      # 25 lines
    self._create_edit_actions()      # 22 lines
    self._create_view_actions()      # 18 lines
    # ... (one method per category, <30 lines each)

def _create_file_actions(self): ...  # 25 lines
def _create_edit_actions(self): ...  # 22 lines
def _create_view_actions(self): ...  # 18 lines
```

**Priority 1.2: High Complexity (4 functions complexity >15)**

Estimated Effort: 1 week

**Targets:**
1. `core/settings.py:validate()` - Complexity 77 → Extract validators per field group
2. `core/macos_optimizer.py:detect_macos_capabilities()` - Complexity 34 → Extract detection methods
3. `core/__init__.py:__getattr__()` - Complexity 23 → Simplify import logic
4. `claude/claude_client.py:send_message()` - Complexity 19 → Extract error handling

**Refactoring Strategy:**
```python
# ❌ Before (complexity 77)
def validate(self):
    if self.font_family:
        if not isinstance(self.font_family, str):
            # ... validation logic
        elif len(self.font_family) > 100:
            # ... more validation
    if self.font_size:
        # ... (repeat for 20+ fields)

# ✅ After (complexity per method <5)
def validate(self):
    self._validate_font_settings()    # Complexity 4
    self._validate_editor_settings()  # Complexity 3
    self._validate_preview_settings() # Complexity 4
    # ... (one method per setting group)
```

### Phase 2: High Priority Fixes (P1 - Should Fix)

**Priority 2.1: Large Functions (76 functions 50-100 lines)**

Estimated Effort: 4-6 weeks

**Strategy:** Extract logical sections to helper methods. Target 20-30 lines per method.

**Priority 2.2: High Complexity (38 functions complexity 10-15)**

Estimated Effort: 3-4 weeks

**Strategy:** Apply early returns, extract complex conditionals to methods, simplify nested logic.

**Priority 2.3: Large Classes (35 classes >300 lines)**

Estimated Effort: 6-8 weeks

**Top Targets:**
- `ui/action_manager.py:ActionManager` - 978 lines → Split into `MenuManager`, `ToolbarManager`, `ActionRegistry`
- `ui/chat_manager.py:ChatManager` - 950 lines → Extract `OllamaModelManager`, `ChatHistoryManager`
- `workers/git_worker.py:GitWorker` - 638 lines → Extract `GitStatusParser`, `GitCommandRunner`
- `workers/pandoc_worker.py:PandocWorker` - 586 lines → Extract format-specific converters
- `ui/preview_handler_base.py:PreviewHandlerBase` - 514 lines → Extract error handling, caching logic

### Phase 3: Medium Priority Fixes (P2 - Nice to Have)

**Priority 3.1: Parameter Count (28 functions >4 params)**

Estimated Effort: 1-2 weeks

**Strategy:** Group related parameters into dataclasses or config objects.

**Priority 3.2: Nesting Depth (42 functions >3 levels)**

Estimated Effort: 2-3 weeks

**Strategy:** Apply early returns, extract nested blocks to methods.

**Priority 3.3: Documentation Line Length (421 violations)**

Estimated Effort: 1 week

**Strategy:** Auto-reformat with text wrapping tools. Low priority as doesn't affect functionality.

---

## Automation

### Scripts Created

**1. `scripts/analyze_ma_violations.py`**
- **Purpose:** Scan Python codebase for MA violations
- **Usage:** `python3 scripts/analyze_ma_violations.py [--json FILE] [--verbose]`
- **Output:** Text report + optional JSON
- **Exit Codes:** 0 (no violations), 1 (any violations), 2 (P0 violations)

**2. `scripts/analyze_ma_violations_docs.py`**
- **Purpose:** Scan Markdown documentation for MA violations
- **Usage:** `python3 scripts/analyze_ma_violations_docs.py [--json FILE] [--verbose]`
- **Output:** Text report + optional JSON
- **Exit Codes:** 0 (no violations), 1 (any violations), 2 (P0 violations)

### Integration with CI/CD

**Pre-commit Hook (Optional):**
```yaml
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: ma-principle-check
      name: MA Principle Check
      entry: python3 scripts/analyze_ma_violations.py
      language: system
      pass_filenames: false
      # Allow P1/P2 violations, fail only on P0
      # (Exit code 2 fails, exit code 1 passes with warning)
```

**GitHub Actions Workflow (Recommended):**
```yaml
# .github/workflows/ma-principle.yml
name: MA Principle Check

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python3 scripts/analyze_ma_violations.py --json ma_violations.json
        continue-on-error: true  # Allow P1/P2, report P0 as warnings
      - uses: actions/upload-artifact@v3
        with:
          name: ma-violations-report
          path: ma_violations.json
```

---

## Success Metrics

### Target Compliance Levels

| Metric | Current | Target (6 months) | Target (12 months) |
|--------|---------|-------------------|---------------------|
| P0 Violations | 17 | 0 | 0 |
| P1 Violations | 79 | <20 | <5 |
| P2 Violations | 128 | <50 | <20 |
| Functions >50 lines | 76 | <20 | <10 |
| Complexity >10 | 38 | <10 | <5 |
| Classes >300 lines | 35 | <15 | <5 |

### Code Quality Impact

**Expected Improvements:**
- **Testability:** +30% (smaller functions easier to unit test)
- **Maintainability:** +40% (reduced cognitive load)
- **Onboarding Time:** -25% (simpler codebase, easier to understand)
- **Bug Density:** -20% (lower complexity correlates with fewer bugs)
- **Code Review Time:** -30% (focused, readable functions)

---

## Timeline

### Immediate (This Session) ✅

**Completed:**
- [x] Define MA principle for project
- [x] Create comprehensive MA principle guide (`docs/developer/ma-principle.md`)
- [x] Add MA principle as FR-108 to SPECIFICATIONS_AI.md and SPECIFICATIONS_HU.md
- [x] Create codebase analysis script (`scripts/analyze_ma_violations.py`)
- [x] Create documentation analysis script (`scripts/analyze_ma_violations_docs.py`)
- [x] Run analysis on codebase (224 violations found)
- [x] Run analysis on documentation (471 violations found)
- [x] Generate JSON reports for both analyses
- [x] Create comprehensive summary report (this document)

**Effort:** 3-4 hours

### Short-Term (Weeks 1-4)

**Priority:** Fix all P0 violations

**Tasks:**
1. Refactor 17 monster functions (>100 lines)
2. Reduce complexity in 4 high-complexity functions (>15)
3. Update tests to maintain coverage
4. Document refactoring patterns used

**Effort:** 3-4 weeks (60-80 hours)

### Medium-Term (Months 2-3)

**Priority:** Fix majority of P1 violations

**Tasks:**
1. Refactor 76 large functions (50-100 lines)
2. Reduce complexity in 38 functions (10-15)
3. Split 35 large classes into focused modules
4. Target: <20 P1 violations remaining

**Effort:** 6-8 weeks (120-160 hours)

### Long-Term (Months 4-6)

**Priority:** Fix remaining P1 and high-priority P2 violations

**Tasks:**
1. Address parameter count violations
2. Reduce nesting depth
3. Clean up documentation line length
4. Target: <5 P1 violations, <50 P2 violations

**Effort:** 4-6 weeks (80-120 hours)

---

## Related Documentation

**MA Principle Guidelines:**
- `docs/developer/ma-principle.md` - Comprehensive 21KB guide with examples, patterns, and adoption strategy

**Functional Requirements:**
- `SPECIFICATIONS_AI.md:FR-108` - MA Principle specification with acceptance criteria and test requirements
- `SPECIFICATIONS_HU.md:FR-108` - MA Principle quick reference

**Analysis Scripts:**
- `scripts/analyze_ma_violations.py` - Python codebase analyzer
- `scripts/analyze_ma_violations_docs.py` - Markdown documentation analyzer

**Analysis Reports:**
- `docs/reports/ma_violations_codebase.json` - Detailed codebase violations (JSON)
- `docs/reports/ma_violations_documentation.json` - Detailed documentation violations (JSON)
- `docs/reports/MA_PRINCIPLE_ANALYSIS_v2.0.8.md` - This comprehensive summary report

---

## Conclusion

**Current State:** AsciiDoc Artisan has 695 MA principle violations (224 code, 471 docs), with 17 critical (P0) issues requiring immediate attention.

**Recommended Action:**
1. **Immediate:** Fix all 17 P0 violations (3-4 weeks)
2. **Short-term:** Address high-impact P1 violations in top 10 files (2-3 months)
3. **Long-term:** Systematic cleanup of remaining violations (4-6 months)

**Impact After Fixes:**
- Improved testability and maintainability
- Reduced cognitive load for developers
- Lower bug density
- Faster code reviews
- Better alignment with Japanese aesthetic principles of simplicity and intentional design

---

**Report Status:** ✅ COMPLETE
**Analysis Date:** November 21, 2025
**Analyst:** Claude Code
**Version:** 1.0
