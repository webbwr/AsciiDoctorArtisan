# Specification-Driven Coding with Claude Code

**Guide for Using SPECIFICATIONS_AI.md with AI-Assisted Development**

---

## Table of Contents

- [Introduction](#introduction)
- [What is Specification-Driven Coding?](#what-is-specification-driven-coding)
- [Getting Started](#getting-started)
- [Workflows](#workflows)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Introduction

This guide shows you how to use the enhanced `SPECIFICATIONS_AI.md` format to develop features with Claude Code (AI assistant). The specification-driven approach lets you describe what you want, and Claude implements it based on detailed, actionable specifications.

### Why Specification-Driven Coding?

**Traditional Approach:**
```
You: "Add a save button"
AI: "Where? What should it do? How should it look?"
You: "Um... just a normal save button"
AI: *Makes assumptions, may not match your needs*
```

**Specification-Driven Approach:**
```
You: "Implement FR-007"
AI: *Reads FR-007 from SPECIFICATIONS_AI.md*
AI: *Sees acceptance criteria, API contract, examples*
AI: *Implements exactly per specification*
AI: *Writes tests per test requirements*
```

### Prerequisites

- Access to Claude Code (claude.ai/code or CLI)
- AsciiDoc Artisan codebase
- `SPECIFICATIONS_AI.md` in repository root
- Basic understanding of the codebase structure

---

## What is Specification-Driven Coding?

Specification-driven coding means:
1. **Specifications are the source of truth** - Code implements specs
2. **AI reads specs to implement features** - No ambiguity
3. **Specs include everything needed** - Acceptance criteria, tests, examples
4. **Iterative refinement** - Specs evolve with the project

### Key Principles

1. **Write Clear Specs First** - Before any code
2. **Make Specs Actionable** - Include acceptance criteria, examples
3. **Include Test Requirements** - Define expected test coverage
4. **Provide Examples** - Show expected inputs/outputs
5. **Document Dependencies** - Link related requirements

---

## Getting Started

### Step 1: Open Claude Code

**Option A: Web Interface**
1. Go to https://claude.ai/code
2. Upload your repository or connect via GitHub

**Option B: CLI**
```bash
cd ~/github/AsciiDoctorArtisan
claude-code
```

### Step 2: Reference SPECIFICATIONS_AI.md

Claude Code automatically reads `SPECIFICATIONS_AI.md` when you reference it.

**Simple Reference:**
```
You: "Implement FR-001"

Claude: *Reads SPECIFICATIONS_AI.md*
Claude: *Finds FR-001: Text Editor*
Claude: *Implements based on acceptance criteria*
```

### Step 3: Review the Implementation

Claude will:
1. Read the FR specification
2. Implement according to acceptance criteria
3. Write tests per test requirements
4. Verify against examples
5. Present code for your review

---

## Workflows

### Workflow 1: Implement a New Feature

**Scenario:** You want to add a new feature.

**Steps:**

1. **Write the FR Specification**
   ```
   You: "I want to add an auto-save feature. Here's what I need:
   - Auto-save every 5 minutes
   - Only if document has unsaved changes
   - Show last auto-save time in status bar"

   Claude: "I'll create FR-084: Auto-Save for you. Let me draft the specification."
   ```

2. **Review and Refine the Spec**
   ```
   Claude: *Creates FR-084 with acceptance criteria, API contract, examples*

   You: "Add a preference to enable/disable auto-save"

   Claude: *Updates FR-084 acceptance criteria*
   ```

3. **Implement the Feature**
   ```
   You: "Implement FR-084"

   Claude: *Reads FR-084*
   Claude: *Implements auto-save timer, UI updates, preferences*
   Claude: *Writes 10 tests as specified*
   ```

4. **Verify Implementation**
   ```
   You: "Run verification steps for FR-084"

   Claude: *Follows verification steps from spec*
   Claude: *Reports results*
   ```

### Workflow 2: Fix a Bug

**Scenario:** A feature doesn't work as specified.

**Steps:**

1. **Identify the FR**
   ```
   You: "The save function is corrupting files. This is related to FR-007."
   ```

2. **Check Against Acceptance Criteria**
   ```
   You: "Does the current implementation meet all acceptance criteria in FR-007?"

   Claude: *Checks code against FR-007 acceptance criteria*
   Claude: "The atomic write operation is missing. Criterion #2 is not met."
   ```

3. **Fix to Match Spec**
   ```
   You: "Update the save function to match FR-007 specification"

   Claude: *Re-implements to match atomic write pattern*
   Claude: *Adds missing error handling per examples*
   ```

4. **Verify Fix**
   ```
   You: "Run FR-007 verification steps"

   Claude: *Tests atomic behavior*
   Claude: *Confirms all acceptance criteria met*
   ```

### Workflow 3: Refactor Existing Code

**Scenario:** Code needs improvement while maintaining functionality.

**Steps:**

1. **Reference the Spec**
   ```
   You: "Refactor the text editor to improve performance, but maintain FR-001 compliance"
   ```

2. **Verify Against Acceptance Criteria**
   ```
   Claude: *Refactors code*
   Claude: *Checks against FR-001 acceptance criteria*
   Claude: *Ensures all 9 criteria still met*
   ```

3. **Run Tests**
   ```
   Claude: *Runs 15 tests specified in FR-001*
   Claude: *Reports all tests passing*
   ```

### Workflow 4: Add Tests for Existing Feature

**Scenario:** Feature works but needs better test coverage.

**Steps:**

1. **Check Test Requirements**
   ```
   You: "What tests are required for FR-015 (Live Preview)?"

   Claude: *Reads FR-015 test requirements*
   Claude: "Minimum 12 tests, 90% coverage target"
   Claude: "Currently have 8 tests (67% coverage)"
   ```

2. **Add Missing Tests**
   ```
   You: "Add the missing tests for FR-015"

   Claude: *Reads test requirements section*
   Claude: *Writes 4 additional tests*
   Claude: *Achieves 92% coverage*
   ```

---

## Examples

### Example 1: Implement from Scratch

**You:**
```
Implement FR-001: Text Editor

Use the specification in SPECIFICATIONS_AI.md. Follow all acceptance
criteria, implement the API contract, and write the required tests.
```

**Claude Response:**
```
I'll implement FR-001: Text Editor based on SPECIFICATIONS_AI.md.

Reading specification...
✓ Found FR-001 with 9 acceptance criteria
✓ API contract defined: AsciiDocEditor class
✓ 3 examples provided
✓ Test requirements: 15 tests, 95% coverage

Implementing:
1. Creating AsciiDocEditor class (extends QPlainTextEdit)
2. Adding syntax highlighter
3. Adding line number area
4. Implementing API methods (set_content, get_content, set_font)
5. Writing 15 tests
6. Verifying against examples

[Shows implementation code]

All 9 acceptance criteria met ✓
15 tests written and passing ✓
Coverage: 96% (exceeds 95% target) ✓
```

### Example 2: Verify Compliance

**You:**
```
Check if the current save implementation complies with FR-007 specification.
```

**Claude Response:**
```
Checking FR-007 compliance...

Reading FR-007: Save Files from SPECIFICATIONS_AI.md

Acceptance Criteria Check:
✓ 1. Saves current editor content to file path
✓ 2. Uses atomic write (temp file + rename)
✓ 3. Keyboard shortcut Ctrl+S triggers save
✓ 4. Updates window title to remove unsaved marker (*)
✓ 5. Displays save confirmation in status bar
✗ 6. Handle save errors gracefully - MISSING error dialog
✓ 7. Preserves file permissions on save
✓ 8. UTF-8 encoding by default
✓ 9. Creates parent directories if missing

Result: 8/9 criteria met (89%)
Issue: Error handling needs improvement (criterion #6)

Would you like me to fix the missing error handling?
```

### Example 3: Generate Tests from Spec

**You:**
```
Generate tests for FR-007 based on the test requirements in SPECIFICATIONS_AI.md
```

**Claude Response:**
```
Reading FR-007 test requirements...

Test Requirements:
- Minimum: 15 tests
- Coverage: 100%
- Types: Unit (8), Integration (2), Security (2), Edge cases (3)

Generating tests:

1. Unit Tests - Basic save success (3 tests):
   - test_save_basic()
   - test_save_with_utf8_content()
   - test_save_returns_true_on_success()

2. Unit Tests - Error conditions (5 tests):
   - test_save_permission_denied()
   - test_save_disk_full()
   - test_save_invalid_path()
   - test_save_readonly_file()
   - test_save_missing_directory()

3. Unit Tests - Edge cases (3 tests):
   - test_save_empty_content()
   - test_save_unicode_content()
   - test_save_large_file_10mb()

4. Integration Tests (2 tests):
   - test_save_updates_window_title()
   - test_save_updates_status_bar()

5. Security Tests (2 tests):
   - test_save_sanitizes_path()
   - test_save_prevents_directory_traversal()

Total: 15 tests ✓
Coverage estimate: 100% ✓

[Shows test code]
```

### Example 4: Understand Dependencies

**You:**
```
What FRs do I need to implement before FR-018 (Incremental Render)?
```

**Claude Response:**
```
Checking dependencies for FR-018 in SPECIFICATIONS_AI.md...

Dependency Chain:
1. FR-001: Text Editor (foundational)
   └─> 2. FR-015: Live Preview (base preview system)
       └─> 3. FR-018: Incremental Render (optimization)

Prerequisites (must implement first):
✓ FR-001: Text Editor - Already implemented
✓ FR-015: Live Preview - Already implemented

FR-018 is ready to implement!

Related FRs (recommended to implement together):
- FR-019: Debounce (complements incremental rendering)
- FR-084: LRU Cache (used by incremental renderer)

Would you like me to implement FR-018 now?
```

---

## Best Practices

### 1. Always Reference the Spec

**Good:**
```
You: "Implement FR-015 per SPECIFICATIONS_AI.md"
```

**Better:**
```
You: "Implement FR-015. Verify all acceptance criteria are met and
write tests per test requirements."
```

**Best:**
```
You: "Implement FR-015. Use the code pattern from implementation
guidance. Run verification steps when done."
```

### 2. Use Acceptance Criteria for Verification

**After Implementation:**
```
You: "Verify FR-007 implementation against acceptance criteria"

Claude: [Checks each criterion one by one]
```

**During Code Review:**
```
You: "Does this PR meet all acceptance criteria for FR-034?"

Claude: [Reviews code against FR-034 criteria]
```

### 3. Reference Examples for Clarity

**When Stuck:**
```
You: "The save function isn't working right. Show me Example 2 from FR-007."

Claude: [Shows error handling example]
Claude: "Your code is missing the try/except block shown in Example 2."
```

### 4. Use Test Requirements as Guide

**Before Testing:**
```
You: "What test coverage is required for FR-050?"

Claude: "Minimum 10 tests, 90% coverage, types: unit, integration, edge cases"
```

**After Testing:**
```
You: "Do we meet FR-050 test requirements?"

Claude: "Yes! 12 tests written (>10 minimum), 94% coverage (>90% target)"
```

### 5. Check Dependencies First

**Before Starting:**
```
You: "What FRs are prerequisites for FR-091?"

Claude: [Shows dependency tree]
Claude: "All prerequisites implemented ✓"
```

### 6. Use API Contracts for Consistency

**During Implementation:**
```
You: "Implement the save function matching the API contract in FR-007"

Claude: [Implements with exact signature from spec]
```

### 7. Follow Implementation Guidance

**For Best Practices:**
```
You: "What's the recommended approach for FR-016 GPU Acceleration?"

Claude: [Shows implementation guidance from spec]
Claude: "Use QWebEngineView, implement 24hr cache, fallback to CPU..."
```

---

## Advanced Usage

### Creating New Specifications

**Template Usage:**
```
You: "Create FR-108 for a markdown export feature using the FR template
from SPECIFICATIONS_AI.md"

Claude: [Creates new FR using template structure]
Claude: [Includes acceptance criteria, API contract, examples, test requirements]
```

### Batch Implementation

**Multiple FRs:**
```
You: "Implement FRs 021-025 (Export System). Check dependencies and
implement in correct order."

Claude: [Checks dependency map]
Claude: [Implements in order: FR-021, FR-022, FR-023, FR-024, FR-025]
```

### Specification Updates

**Enhance Existing FR:**
```
You: "Update FR-015 to include performance requirements for 50,000 line documents"

Claude: [Updates FR-015 acceptance criteria]
Claude: [Adds performance test requirement]
Claude: [Updates examples]
```

---

## Troubleshooting

### Issue: "I don't know which FR to implement"

**Solution:**
```
You: "Which FRs are not yet implemented?"

Claude: [Checks FR status in SPECIFICATIONS_AI.md]
Claude: "All 107 FRs are implemented ✓"
```

Or:
```
You: "What critical FRs are highest priority?"

Claude: [Shows Critical priority FRs]
Claude: "FR-001, FR-006, FR-007, FR-015, FR-069, FR-070, FR-075, FR-076"
```

### Issue: "Implementation doesn't match spec"

**Solution:**
```
You: "The current implementation of FR-007 doesn't use atomic writes.
Fix it to match the specification."

Claude: [Reads FR-007 implementation guidance]
Claude: [Updates code to use atomic write pattern]
Claude: [Verifies against acceptance criteria]
```

### Issue: "Not enough tests"

**Solution:**
```
You: "FR-015 requires 12 tests but we only have 5. Add the missing tests."

Claude: [Reads FR-015 test requirements]
Claude: [Identifies missing test types]
Claude: [Writes 7 additional tests]
```

### Issue: "Spec is incomplete"

**Solution:**
```
You: "FR-050 is missing examples. Add 3 examples showing typical usage."

Claude: [Updates FR-050]
Claude: [Adds input/output examples]
```

---

## Tips and Tricks

### Tip 1: Use FR Numbers in Commit Messages

```bash
git commit -m "feat: Implement FR-085 auto-complete (closes #42)"
```

### Tip 2: Reference Specs in Code Comments

```python
def save_file(path: str) -> bool:
    """Save file atomically per FR-007.

    Implementation follows FR-007 acceptance criteria #1-#9.
    Uses atomic write pattern from FR-007 implementation guidance.
    """
```

### Tip 3: Link Issues to FRs

```
GitHub Issue: "Save corrupts files"
Comment: "Related to FR-007. Current implementation doesn't meet
acceptance criterion #2 (atomic writes)."
```

### Tip 4: Use Specs for Code Review

```
PR Description: "Implements FR-091: Real-Time Syntax Checking"
Checklist:
- [x] All 9 acceptance criteria met
- [x] API contract followed
- [x] 15 tests written (100% coverage)
- [x] Verification steps pass
```

### Tip 5: Generate Documentation from Specs

```
You: "Generate user documentation for FR-040 (Chat Panel) based on
the examples in SPECIFICATIONS_AI.md"

Claude: [Extracts examples]
Claude: [Creates user guide with screenshots placeholders]
```

---

## Workflow Checklist

### Before Starting

- [ ] Read the FR specification in SPECIFICATIONS_AI.md
- [ ] Check dependencies (implement prerequisites first)
- [ ] Review acceptance criteria
- [ ] Read examples to understand expected behavior
- [ ] Note test requirements

### During Implementation

- [ ] Follow API contract exactly
- [ ] Implement all acceptance criteria
- [ ] Use code patterns from implementation guidance
- [ ] Apply security considerations
- [ ] Meet performance constraints

### After Implementation

- [ ] Write tests per test requirements
- [ ] Run verification steps
- [ ] Check all acceptance criteria met
- [ ] Measure test coverage
- [ ] Update FR status if needed

---

## Resources

### Documentation
- `SPECIFICATIONS_AI.md` - Enhanced specification format (use this)
- `SPECIFICATIONS.md` - Original format (legacy reference)
- [GitHub: Spec-Driven Development](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Kiro: Future of Software Development](https://kiro.dev/blog/kiro-and-the-future-of-software-development/)

### Project Files
- `CLAUDE.md` - AI assistant guide
- `README.md` - User guide
- `docs/developer/contributing.md` - Contribution guidelines

---

## Quick Reference

### Common Commands

**Implement a feature:**
```
"Implement FR-XXX per SPECIFICATIONS_AI.md"
```

**Check compliance:**
```
"Verify FR-XXX implementation against acceptance criteria"
```

**Add tests:**
```
"Generate tests for FR-XXX per test requirements"
```

**Check dependencies:**
```
"What FRs are prerequisites for FR-XXX?"
```

**Update spec:**
```
"Update FR-XXX to add [new requirement]"
```

---

## Summary

Specification-driven coding with Claude Code means:

1. **Write clear specifications first** (SPECIFICATIONS_AI.md)
2. **Reference FRs when implementing** ("Implement FR-XXX")
3. **Verify against acceptance criteria** (Built into each FR)
4. **Write tests per requirements** (Test section in each FR)
5. **Use examples for clarity** (Examples section in each FR)
6. **Follow implementation guidance** (Security, performance, patterns)

**Result:** Consistent, well-tested, specification-compliant code with minimal ambiguity.

---

**Version:** 1.0
**Last Updated:** November 15, 2025
**For:** AsciiDoc Artisan v2.0.2+
