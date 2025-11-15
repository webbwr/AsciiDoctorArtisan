# Pytest Markers Usage Guide

**Purpose:** Enable FR-based test selection and traceability
**Date:** November 15, 2025
**Version:** 1.0

---

## Overview

All 107 functional requirements from SPECIFICATIONS_V2.md now have corresponding pytest markers. This enables:

- ✅ Running tests for specific FRs
- ✅ Counting tests per FR
- ✅ Measuring coverage per FR
- ✅ Tracing FRs to actual test code

---

## Available Markers

### FR Markers (107 total)

**Core Editing (FR-001-020):**
- `@pytest.mark.fr_001` - Text Editor
- `@pytest.mark.fr_002` - Line Numbers
- `@pytest.mark.fr_003` - Undo/Redo
- ... (all FRs through FR-020)

**Export & Conversion (FR-021-025):**
- `@pytest.mark.fr_021` - Export HTML
- `@pytest.mark.fr_022` - Export PDF
- ... (through FR-025)

**Git Integration (FR-026-033):**
- `@pytest.mark.fr_026` - Select Repo
- `@pytest.mark.fr_027` - Git Commit
- ... (through FR-033)

**(See pytest.ini for complete list of all 107 markers)**

### Test Type Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.edge_case` - Edge case tests

---

## How to Add Markers to Tests

### Single FR, Single Type

```python
import pytest

@pytest.mark.fr_007
@pytest.mark.unit
def test_save_basic(tmp_path):
    """Test basic file save operation.

    FR-007: Save Files
    Requirement: Save current editor content to file path
    """
    # Test code here
    pass
```

### Multiple FRs (Test Covers Multiple Requirements)

```python
@pytest.mark.fr_006  # Open Files
@pytest.mark.fr_007  # Save Files
@pytest.mark.integration
def test_open_edit_save_workflow(tmp_path):
    """Test complete file workflow.

    FR-006: Open Files
    FR-007: Save Files
    Integration test for full edit-save cycle
    """
    # Test code here
    pass
```

### Security Test Example

```python
@pytest.mark.fr_007
@pytest.mark.fr_070  # Path Sanitization
@pytest.mark.security
def test_save_sanitizes_path():
    """Test path sanitization during save.

    FR-007: Save Files
    FR-070: Path Sanitization
    Security requirement: Prevent directory traversal
    """
    malicious_path = "../../etc/passwd"

    with pytest.raises(ValueError, match="Invalid path"):
        save_file(malicious_path, "content")
```

### Edge Case Example

```python
@pytest.mark.fr_007
@pytest.mark.edge_case
def test_save_empty_content(tmp_path):
    """Test saving empty file content.

    FR-007: Save Files
    Edge case: Empty content should create empty file
    """
    file_path = tmp_path / "empty.adoc"

    result = save_file(file_path, "")

    assert result is True
    assert file_path.read_text() == ""
```

---

## Running Tests by Marker

### Run All Tests for Specific FR

```bash
# Run all tests for FR-007 (Save Files)
pytest -m fr_007 -v

# Run with coverage
pytest -m fr_007 --cov=src/asciidoc_artisan/core/file_operations
```

### Count Tests for Specific FR

```bash
# Count tests for FR-007
pytest -m fr_007 --collect-only -q

# Output: "15 tests collected"
```

### Run Tests by Type

```bash
# Run all unit tests
pytest -m unit -v

# Run all security tests
pytest -m security -v

# Run all integration tests
pytest -m integration -v
```

### Combine Markers (AND logic)

```bash
# Run security tests for FR-007
pytest -m "fr_007 and security" -v

# Run unit tests for FR-015
pytest -m "fr_015 and unit" -v
```

### Combine Markers (OR logic)

```bash
# Run tests for FR-006 OR FR-007
pytest -m "fr_006 or fr_007" -v
```

### Exclude Markers (NOT logic)

```bash
# Run all tests EXCEPT slow ones
pytest -m "not slow" -v

# Run FR-007 tests EXCEPT integration tests
pytest -m "fr_007 and not integration" -v
```

---

## Verify FR Requirements

### Check Test Count vs SPECIFICATIONS_V2.md

```bash
# FR-007 requires minimum 15 tests
pytest -m fr_007 --collect-only -q
# Should show: "15+ tests collected"

# FR-015 requires minimum 12 tests
pytest -m fr_015 --collect-only -q
# Should show: "12+ tests collected"
```

### Check Coverage vs Target

```bash
# FR-007 requires 100% coverage
pytest -m fr_007 --cov=src/asciidoc_artisan/core/file_operations --cov-report=term-missing

# FR-015 requires 90% coverage
pytest -m fr_015 --cov=src/asciidoc_artisan/workers/preview_worker --cov-report=term-missing
```

### Verify Test Types Present

```bash
# FR-007 requires: 8 unit, 2 integration, 2 security, 3 edge cases
pytest -m "fr_007 and unit" --collect-only -q        # Should show 8+
pytest -m "fr_007 and integration" --collect-only -q # Should show 2+
pytest -m "fr_007 and security" --collect-only -q    # Should show 2+
pytest -m "fr_007 and edge_case" --collect-only -q   # Should show 3+
```

---

## Best Practices

### 1. Always Add FR Markers

Every test should have at least one `@pytest.mark.fr_XXX` marker identifying which requirement(s) it tests.

**Good:**
```python
@pytest.mark.fr_007
@pytest.mark.unit
def test_save_basic():
    pass
```

**Bad:**
```python
def test_save_basic():  # No FR marker!
    pass
```

### 2. Add Test Type Markers

Always classify tests by type: `unit`, `integration`, `security`, `performance`, or `edge_case`.

### 3. Update Docstrings

Include FR number and requirement description in test docstrings:

```python
@pytest.mark.fr_007
@pytest.mark.security
def test_save_sanitizes_path():
    """Test path sanitization during save.

    FR-007: Save Files
    Requirement: Sanitize file paths to prevent directory traversal
    Security: Prevent malicious path access
    """
    pass
```

### 4. Multiple FRs for Integration Tests

Integration tests that span multiple features should have multiple FR markers:

```python
@pytest.mark.fr_026  # Git Repo Selection
@pytest.mark.fr_027  # Git Commit
@pytest.mark.integration
def test_git_commit_workflow():
    """Test complete Git commit workflow."""
    pass
```

### 5. Keep Markers Aligned with SPECIFICATIONS_V2.md

When FR requirements change in SPECIFICATIONS_V2.md, update corresponding test markers and counts.

---

## Migration Strategy

### Phase 2A: Critical FRs (Priority 1)
**Target:** 1-2 days

Add markers to tests for critical FRs:
- FR-001 (Text Editor)
- FR-007 (Save Files)
- FR-015 (Live Preview)
- FR-069-072 (Security FRs)
- FR-075-076 (Type Safety, Test Coverage)

### Phase 2B: High-Priority FRs (Priority 2)
**Target:** 3-5 days

Add markers to tests for:
- FR-002-020 (Core Editing)
- FR-026-033 (Git Integration)
- FR-039-044 (AI Features)

### Phase 2C: All Remaining FRs (Priority 3)
**Target:** 1-2 weeks

Complete marker coverage for all 107 FRs.

---

## Automated Marker Addition

### Script Template

Create `scripts/add_fr_markers.py` to help automate marker addition:

```python
#!/usr/bin/env python3
"""
Add FR markers to test files based on filename/directory.

Usage:
    python3 scripts/add_fr_markers.py tests/unit/core/test_file_operations.py --fr 007
"""
import ast
import sys
from pathlib import Path

def add_marker_to_test(file_path, fr_number, test_type="unit"):
    """Add @pytest.mark.fr_XXX to all test functions in file."""
    # Implementation here
    pass

if __name__ == "__main__":
    # Parse arguments and add markers
    pass
```

---

## Validation

### Pre-Commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Verify new tests have FR markers

NEW_TESTS=$(git diff --cached --name-only | grep "test_.*\.py$")

for test_file in $NEW_TESTS; do
    if ! grep -q "@pytest.mark.fr_" "$test_file"; then
        echo "ERROR: $test_file missing FR marker"
        echo "Add @pytest.mark.fr_XXX to new tests"
        exit 1
    fi
done
```

### CI/CD Check

```bash
# In CI pipeline, verify all tests have FR markers
python3 scripts/verify_fr_markers.py
```

---

## Reporting

### Generate FR Coverage Report

```bash
# Count tests per FR
for fr in {001..107}; do
    count=$(pytest -m fr_$fr --collect-only -q 2>/dev/null | grep "selected" | awk '{print $1}')
    echo "FR-$fr: $count tests"
done > fr_test_counts.txt
```

### Generate Test Type Distribution

```bash
# For FR-007, show test type breakdown
echo "FR-007 Test Distribution:"
echo "  Unit:        $(pytest -m 'fr_007 and unit' --collect-only -q 2>/dev/null | grep "selected" | awk '{print $1}')"
echo "  Integration: $(pytest -m 'fr_007 and integration' --collect-only -q 2>/dev/null | grep "selected" | awk '{print $1}')"
echo "  Security:    $(pytest -m 'fr_007 and security' --collect-only -q 2>/dev/null | grep "selected" | awk '{print $1}')"
echo "  Edge Cases:  $(pytest -m 'fr_007 and edge_case' --collect-only -q 2>/dev/null | grep "selected" | awk '{print $1}')"
```

---

## Troubleshooting

### Marker Not Recognized

**Error:** `PytestUnknownMarkWarning: Unknown pytest.mark.fr_007`

**Solution:** Ensure pytest.ini has `--strict-markers` and all FR markers are defined in the `markers` section.

### No Tests Collected

```bash
$ pytest -m fr_007 --collect-only
# 0 tests collected
```

**Cause:** No tests have been tagged with `@pytest.mark.fr_007` yet.

**Solution:** Add markers to test files covering FR-007.

### Marker Expression Syntax Error

```bash
$ pytest -m "fr_007 and security" -v
# ERROR: Wrong expression
```

**Solution:** Use proper Boolean syntax:
- AND: `"fr_007 and security"`
- OR: `"fr_007 or fr_006"`
- NOT: `"fr_007 and not slow"`

---

## Examples from Codebase

### File Operations (FR-006, FR-007)

```python
# tests/unit/core/test_file_operations.py

import pytest
from asciidoc_artisan.core.file_operations import open_file, save_file

@pytest.mark.fr_006
@pytest.mark.unit
def test_open_file_basic(tmp_path):
    """Test basic file open operation (FR-006)."""
    file_path = tmp_path / "test.adoc"
    file_path.write_text("# Test")

    content = open_file(file_path)

    assert content == "# Test"

@pytest.mark.fr_007
@pytest.mark.unit
def test_save_file_basic(tmp_path):
    """Test basic file save operation (FR-007)."""
    file_path = tmp_path / "test.adoc"

    result = save_file(file_path, "# Test")

    assert result is True
    assert file_path.read_text() == "# Test"

@pytest.mark.fr_007
@pytest.mark.fr_070  # Path Sanitization
@pytest.mark.security
def test_save_file_sanitizes_path():
    """Test path sanitization (FR-007, FR-070)."""
    malicious_path = "../../etc/passwd"

    with pytest.raises(ValueError, match="Invalid path"):
        save_file(malicious_path, "content")
```

---

## Next Steps

1. ✅ pytest.ini configured with all 107 FR markers
2. ⏳ Add markers to critical FR test files (FR-001, FR-007, FR-015, FR-069-076)
3. ⏳ Verify marker functionality with `pytest -m fr_XXX`
4. ⏳ Expand markers to all test files incrementally
5. ⏳ Create automated marker addition script
6. ⏳ Add pre-commit hook to enforce markers on new tests

---

**Status:** Phase 2 Framework Complete
**Next:** Begin adding markers to critical FR test files
**Documentation:** See SPECIFICATIONS_V2.md for FR requirements
