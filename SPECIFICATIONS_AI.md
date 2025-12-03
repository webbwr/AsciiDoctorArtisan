# AsciiDoc Artisan Functional Specifications (Spec-Driven Development)

```yaml
---
specification:
  name: "AsciiDoc Artisan Functional Requirements"
  version: "2.0.9"
  status: "Production-Ready"
  last_updated: "2025-12-03"
  format_version: "2.0-ai-actionable"

metadata:
  total_requirements: 109
  sub_requirements: 3  # FR-067a, FR-067b, FR-067c
  total_fr_definitions: 112
  implemented: 109  # FR-109 (LSP) now implemented
  partial: 0
  planned: 0
  scope: "Feature-complete, maintenance mode"
  future_work: "Out of scope (plugins, collaboration deferred)"

codebase_metrics:
  total_lines: 44935
  total_files: 171
  main_window_lines: 1798

quality_metrics:
  unit_tests_total: 5285
  e2e_tests_total: 71
  type_coverage: 100.0
  mypy_strict_errors: 0

ai_guidance:
  format: "specification-driven-development"
  parseable: true
  actionable: true
  test_driven: true
---
```

## Introduction

This specification follows **AI Specification-Driven Development** principles:

1. **Actionable**: Each FR includes acceptance criteria, examples, and verification steps
2. **Machine-Parseable**: Structured format with consistent sections
3. **Test-Driven**: Explicit test requirements and coverage targets
4. **Implementation-Guided**: Code patterns, security, and performance guidance

### How to Use This Spec

**For AI Agents:**
- Each FR is self-contained and actionable
- Follow the API Contract to implement features
- Use Examples to understand expected behavior
- Meet all Acceptance Criteria before marking complete
- Write tests according to Test Requirements

**For Developers:**
- Use Implementation Guidance for best practices
- Follow Code Patterns for consistency
- Reference Dependencies before starting work
- Use Verification steps to confirm correctness

---

## Dependency Map

**Comprehensive FR dependency relationships across all 107 requirements**

```mermaid
graph TD
    %% Core Editing Foundation (FR-001-020)
    FR001[FR-001: Text Editor] --> FR002[FR-002: Line Numbers]
    FR001 --> FR003[FR-003: Undo/Redo]
    FR001 --> FR004[FR-004: Font Customization]
    FR001 --> FR005[FR-005: Editor State]
    FR001 --> FR006[FR-006: Open Files]

    %% File Operations Chain
    FR006 --> FR007[FR-007: Save Files]
    FR007 --> FR008[FR-008: Save As]
    FR006 --> FR009[FR-009: New Document]
    FR007 --> FR010[FR-010: Recent Files]
    FR007 --> FR011[FR-011: Auto-Save]

    %% Import Chain (to Editor)
    FR012[FR-012: Import DOCX] --> FR001
    FR013[FR-013: Import PDF] --> FR001
    FR014[FR-014: Import Markdown] --> FR001

    %% Preview Chain
    FR001 --> FR015[FR-015: Live Preview]
    FR015 --> FR016[FR-016: GPU Acceleration]
    FR015 --> FR017[FR-017: Scroll Sync]
    FR015 --> FR018[FR-018: Incremental Render]
    FR015 --> FR019[FR-019: Debounce]
    FR015 --> FR020[FR-020: Preview Themes]

    %% Export Chain (from Preview)
    FR015 --> FR021[FR-021: Export HTML]
    FR015 --> FR022[FR-022: Export PDF]
    FR015 --> FR023[FR-023: Export DOCX]
    FR015 --> FR024[FR-024: Export Markdown]
    FR043[FR-043: Ollama Integration] --> FR025[FR-025: AI Export Enhancement]

    %% Git Integration Chain
    FR026[FR-026: Select Repo] --> FR027[FR-027: Git Commit]
    FR026 --> FR028[FR-028: Git Pull]
    FR026 --> FR029[FR-029: Git Push]
    FR026 --> FR030[FR-030: Git Status Bar]
    FR026 --> FR031[FR-031: Git Status Dialog]
    FR026 --> FR032[FR-032: Quick Commit]
    FR026 --> FR033[FR-033: Cancel Git Ops]

    %% GitHub CLI Chain
    FR026 --> FR034[FR-034: Create PR]
    FR026 --> FR035[FR-035: List PRs]
    FR026 --> FR036[FR-036: Create Issue]
    FR026 --> FR037[FR-037: List Issues]
    FR026 --> FR038[FR-038: View Repo]

    %% AI Features Chain
    FR039[FR-039: Ollama Chat Panel] --> FR040[FR-040: Chat Modes]
    FR039 --> FR041[FR-041: Model Selection]
    FR039 --> FR042[FR-042: Chat History]
    FR039 --> FR043
    FR039 --> FR044[FR-044: Status Indicator]

    %% Find & Replace Chain
    FR001 --> FR047[FR-047: Search Engine]
    FR047 --> FR045[FR-045: Find Bar]
    FR047 --> FR046[FR-046: Replace]
    FR047 --> FR048[FR-048: UI Integration]
    FR047 --> FR049[FR-049: Search Performance]

    %% Spell Check Chain
    FR001 --> FR050[FR-050: Real-Time Spell Check]
    FR050 --> FR051[FR-051: Suggestions]
    FR050 --> FR052[FR-052: Custom Dictionary]
    FR050 --> FR053[FR-053: Multi-Language]
    FR050 --> FR054[FR-054: Performance]

    %% UI & UX Chain
    FR001 --> FR055[FR-055: Theme Support]
    FR001 --> FR056[FR-056: Status Bar]
    FR001 --> FR057[FR-057: Document Metrics]
    FR001 --> FR058[FR-058: Menu Structure]
    FR001 --> FR059[FR-059: Preferences Dialog]
    FR001 --> FR060[FR-060: Keyboard Shortcuts]
    FR001 --> FR061[FR-061: Accessibility]

    %% Performance Chain
    FR062[FR-062: Fast Startup] --> FR063[FR-063: Worker Pool]
    FR062 --> FR064[FR-064: Async I/O]
    FR062 --> FR065[FR-065: Lazy Loading]
    FR062 --> FR066[FR-066: Resource Monitor]
    FR062 --> FR067[FR-067: Optimized Imports]
    FR062 --> FR067a[FR-067a: String Optimization]
    FR062 --> FR067b[FR-067b: PDF Reading Optimization]
    FR062 --> FR067c[FR-067c: Binary Operations]
    FR068[FR-068: Memory Management] --> FR066

    %% Security Chain
    FR007 --> FR069[FR-069: Atomic Writes]
    FR069 --> FR070[FR-070: Path Sanitization]
    FR069 --> FR071[FR-071: Subprocess Safety]
    FR069 --> FR072[FR-072: Input Validation]

    %% Additional Features (Standalone)
    FR073[FR-073: Telemetry]
    FR074[FR-074: Crash Reports]
    FR075[FR-075: Type Safety]
    FR076[FR-076: Test Coverage]
    FR077[FR-077: Documentation]
    FR078[FR-078: Help System]
    FR079[FR-079: Update Check]
    FR080[FR-080: Keyboard Reference]
    FR081[FR-081: Custom Themes]
    FR082[FR-082: Export Presets]
    FR083[FR-083: Macro Recording]
    FR084[FR-084: LRU Cache]

    %% Auto-Complete Chain (v2.0)
    FR001 --> FR085[FR-085: Auto-Complete Engine]
    FR085 --> FR086[FR-086: Context Detection]
    FR085 --> FR087[FR-087: Completion Provider]
    FR085 --> FR088[FR-088: Fuzzy Matching]
    FR085 --> FR089[FR-089: UI Widget]
    FR085 --> FR090[FR-090: Performance]

    %% Syntax Checking Chain (v2.0)
    FR001 --> FR091[FR-091: Syntax Checker]
    FR091 --> FR092[FR-092: Error Detection]
    FR091 --> FR093[FR-093: Error Display]
    FR091 --> FR094[FR-094: Quick Fixes]
    FR091 --> FR095[FR-095: Navigation]
    FR091 --> FR096[FR-096: Real-Time Validation]
    FR091 --> FR097[FR-097: Rule Engine]
    FR091 --> FR098[FR-098: Custom Rules]
    FR091 --> FR099[FR-099: Performance]

    %% Template System Chain (v2.0)
    FR001 --> FR100[FR-100: Template Manager]
    FR100 --> FR101[FR-101: Built-In Templates]
    FR100 --> FR102[FR-102: Custom Templates]
    FR100 --> FR103[FR-103: Template Variables]
    FR100 --> FR104[FR-104: Template Engine]
    FR100 --> FR105[FR-105: UI Integration]
    FR100 --> FR106[FR-106: Template Browser]
    FR100 --> FR107[FR-107: Performance]

    %% Cross-System Dependencies
    FR018 --> FR084
    FR016 --> FR062
    FR068 --> FR084
```

---

## Priority Classification

### Critical (Must Have)
FR-001, FR-006, FR-007, FR-015, FR-069, FR-070, FR-075, FR-076

### High (Core Features)
FR-002 to FR-005, FR-008 to FR-014, FR-016 to FR-020, FR-021 to FR-025

### Medium (Enhanced Features)
FR-026 to FR-061, FR-073 to FR-084

### Low (Advanced Features)
FR-062 to FR-072, FR-085 to FR-107

---

## FR Index (Quick Lookup)

### Core Editing (FR-001-020)
- **FR-001:** Text Editor | **FR-002:** Line Numbers | **FR-003:** Undo/Redo | **FR-004:** Font Customization | **FR-005:** Editor State
- **FR-006:** Open Files | **FR-007:** Save Files | **FR-008:** Save As | **FR-009:** New Document | **FR-010:** Recent Files
- **FR-011:** Auto-Save | **FR-012:** Import DOCX | **FR-013:** Import PDF | **FR-014:** Import Markdown
- **FR-015:** Live Preview | **FR-016:** GPU Acceleration | **FR-017:** Scroll Sync | **FR-018:** Incremental Render | **FR-019:** Debounce | **FR-020:** Preview Themes

### Export & Conversion (FR-021-025)
- **FR-021:** Export HTML | **FR-022:** Export PDF | **FR-023:** Export DOCX | **FR-024:** Export Markdown | **FR-025:** AI Export Enhancement

### Git Integration (FR-026-033)
- **FR-026:** Select Repo | **FR-027:** Git Commit | **FR-028:** Git Pull | **FR-029:** Git Push
- **FR-030:** Git Status Bar | **FR-031:** Git Status Dialog | **FR-032:** Quick Commit | **FR-033:** Cancel Git Ops

### GitHub CLI (FR-034-038)
- **FR-034:** Create PR | **FR-035:** List PRs | **FR-036:** Create Issue | **FR-037:** List Issues | **FR-038:** View Repo

### AI Features (FR-039-044)
- **FR-039:** Ollama Chat Panel | **FR-040:** Chat Modes | **FR-041:** Model Selection | **FR-042:** Chat History | **FR-043:** Ollama Integration | **FR-044:** Status Indicator

### Find & Replace (FR-045-049)
- **FR-045:** Find Bar | **FR-046:** Replace | **FR-047:** Search Engine | **FR-048:** UI Integration | **FR-049:** Search Performance

### Spell Check (FR-050-054)
- **FR-050:** Real-Time Spell Check | **FR-051:** Suggestions | **FR-052:** Custom Dictionary | **FR-053:** Multi-Language | **FR-054:** Performance

### UI & UX (FR-055-061)
- **FR-055:** Theme Support | **FR-056:** Status Bar | **FR-057:** Document Metrics | **FR-058:** Menu Structure
- **FR-059:** Preferences Dialog | **FR-060:** Keyboard Shortcuts | **FR-061:** Accessibility

### Performance (FR-062-068)
- **FR-062:** Fast Startup | **FR-063:** Worker Pool | **FR-064:** Async I/O | **FR-065:** Resource Monitoring
- **FR-066:** Memory Optimization | **FR-067:** Cache Strategy | **FR-067a:** Incremental Rendering | **FR-067b:** Predictive Rendering | **FR-067c:** Render Prioritization | **FR-068:** Path Sanitization

### Security (FR-069-072)
- **FR-069:** Atomic Writes | **FR-070:** Subprocess Safety | **FR-071:** Secure Credentials | **FR-072:** HTTPS Enforcement

### Additional Features (FR-073-084)
- **FR-073:** Telemetry | **FR-074:** Settings Persistence | **FR-075:** Type Safety | **FR-076:** Test Coverage
- **FR-077:** User Documentation | **FR-078:** Inline Help | **FR-079:** Tooltips | **FR-080:** Keyboard Reference
- **FR-081:** About Dialog | **FR-082:** Auto-Update | **FR-083:** Backup System | **FR-084:** LRU Cache

### Auto-Complete (FR-085-090)
- **FR-085:** Auto-Complete Engine | **FR-086:** Completion Popup | **FR-087:** Syntax-Aware | **FR-088:** Fuzzy Matching | **FR-089:** Completion Cache | **FR-090:** Custom Completions

### Syntax Checking (FR-091-099)
- **FR-091:** Real-Time Syntax Checking | **FR-092:** Error Highlighting | **FR-093:** Error Navigation | **FR-094:** Error Panel
- **FR-095:** Syntax Rules | **FR-096:** Quick Fixes | **FR-097:** Configurable Rules | **FR-098:** Performance Optimization | **FR-099:** Error Recovery

### Templates (FR-100-107)
- **FR-100:** Template System | **FR-101:** Template Variables | **FR-102:** Custom Templates | **FR-103:** Template Preview
- **FR-104:** Template Metadata | **FR-105:** Template Categories | **FR-106:** Template Sharing | **FR-107:** Template Engine

---

## FR-001: Text Editor

**Category:** Core Editing
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** None (foundational)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/main_window.py`

### Description

Provide a multi-line text editing component with AsciiDoc syntax highlighting and line numbers for document creation and editing.

### Acceptance Criteria

- [x] Editor displays AsciiDoc text with syntax highlighting
- [x] Line numbers visible and synchronized with text
- [x] Supports standard text editing operations (type, delete, select, copy, paste)
- [x] Syntax highlighting updates in real-time as user types
- [x] Editor handles large documents (10,000+ lines) without lag (<500ms render)
- [x] Tab key inserts spaces (configurable: 2 or 4 spaces)
- [x] Line wrapping configurable (on/off)
- [x] Font customization (family, size)
- [x] Undo/redo support (Ctrl+Z/Ctrl+Y)

### API Contract

```python
class AsciiDocEditor(QPlainTextEdit):
    """Main text editor widget for AsciiDoc content.

    Provides syntax-highlighted editing with line numbers,
    undo/redo, and efficient rendering for large documents.
    """

    # Signals
    content_changed: Signal = Signal(str)  # Emitted when text changes
    cursor_position_changed: Signal = Signal(int, int)  # line, column

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize editor with syntax highlighter and line numbers.

        Args:
            parent: Parent widget (optional)
        """

    def set_content(self, content: str) -> None:
        """Set editor content programmatically.

        Args:
            content: AsciiDoc text to display

        Raises:
            ValueError: If content is None
        """

    def get_content(self) -> str:
        """Get current editor content.

        Returns:
            Current AsciiDoc text as string
        """

    def set_font(self, family: str, size: int) -> None:
        """Set editor font.

        Args:
            family: Font family name (e.g., "Monospace")
            size: Font size in points (8-72)

        Raises:
            ValueError: If size out of range
        """
```

### Examples

**Example 1: User Types Heading**

*Input:*
```
User types: = Document Title
```

*Output:*
```
Text displayed with heading-1 highlighting:
- Larger font size
- Bold weight
- Distinct color (e.g., blue)
```

**Example 2: API Content Setting**

*Input:*
```python
editor = AsciiDocEditor()
editor.set_content("== Section\n\nParagraph text.")
```

*Output:*
```
Editor displays:
Line 1: == Section (heading-2 highlighting)
Line 2: (blank)
Line 3: Paragraph text. (normal text)
```

**Example 3: Large Document Performance**

*Input:*
```python
# 10,000 line document
content = "\n".join([f"Line {i}" for i in range(10000)])
editor.set_content(content)
```

*Output:*
```
Renders in <500ms
Line numbers 1-10000 visible
Smooth scrolling maintained
```

### Test Requirements

- **Minimum Tests:** 15
- **Coverage Target:** 95%+
- **Test Types:**
  - Unit: Content get/set (3 tests)
  - Unit: Syntax highlighting rules (5 tests)
  - Integration: Editor + line numbers (4 tests)
  - Integration: Editor + highlighter (2 tests)
  - Performance: 10K line render <500ms (1 test)

### Implementation Guidance

**Approach:**
1. Extend `QPlainTextEdit` as base class
2. Attach `QSyntaxHighlighter` subclass for AsciiDoc highlighting
3. Use `LineNumberArea` widget painted in margin
4. Connect `textChanged` signal to update line numbers
5. Implement custom `paintEvent` for line number area

**Security:**
- Sanitize pasted content for malicious HTML/scripts
- Validate document size limit (default: 10MB)
- Prevent regex DoS in syntax highlighting patterns

**Performance:**
- Use incremental highlighting (only highlight visible lines)
- Implement lazy loading for documents >5K lines
- Debounce highlight updates (100ms after typing stops)
- Cache syntax highlight results per line

**Code Pattern:**
```python
class AsciiDocEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Setup components
        self.highlighter = AsciiDocHighlighter(self.document())
        self.line_number_area = LineNumberArea(self)
        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.cursorPositionChanged.connect(self._on_cursor_moved)
```

### Verification Steps

1. **Basic Functionality:**
   - Open editor
   - Type "= My Title"
   - Verify heading syntax highlighting appears

2. **Line Numbers:**
   - Type 50 lines of text
   - Verify line numbers 1-50 appear correctly
   - Scroll and verify numbers stay synchronized

3. **Performance:**
   - Load 10,000 line document
   - Measure render time <500ms
   - Verify smooth scrolling

4. **Edge Cases:**
   - Empty document: No errors
   - Unicode content: Renders correctly
   - Very long lines (10K chars): Wraps properly

---

## FR-007: Save Files

**Category:** File Operations
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor), FR-069 (Atomic Writes), FR-068 (Path Sanitization)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/core/file_operations.py::atomic_save_text()`

### Description

Save editor content to disk using atomic write operations to prevent file corruption, with support for keyboard shortcut (Ctrl+S) and automatic backup.

### Acceptance Criteria

- [x] Save current editor content to file path
- [x] Use atomic write (temp file + rename) to prevent corruption
- [x] Keyboard shortcut Ctrl+S triggers save
- [x] Update window title to remove unsaved marker (*)
- [x] Display save confirmation in status bar
- [x] Handle save errors gracefully (permission denied, disk full)
- [x] Preserve file permissions on save
- [x] UTF-8 encoding by default
- [x] Create parent directories if missing

### API Contract

```python
def atomic_save_text(
    file_path: str | Path,
    content: str,
    encoding: str = "utf-8"
) -> bool:
    """Save text content to file atomically.

    Writes to temporary file first, then renames to target path.
    This prevents corruption if save interrupted.

    Args:
        file_path: Target file path
        content: Text content to save
        encoding: Text encoding (default: utf-8)

    Returns:
        True if save successful, False otherwise

    Raises:
        PermissionError: If no write permission
        OSError: If disk full or I/O error
        ValueError: If file_path is None or empty

    Example:
        >>> atomic_save_text("/path/file.adoc", "= Title\n\nContent")
        True
    """
```

### Examples

**Example 1: Basic Save**

*Input:*
```python
content = "= My Document\n\nSome content here."
result = atomic_save_text("/home/user/doc.adoc", content)
```

*Output:*
```
Result: True
File /home/user/doc.adoc created with content
Permissions: 0644 (rw-r--r--)
Status bar: "Saved doc.adoc"
Window title: "AsciiDoc Artisan - doc.adoc" (no *)
```

**Example 2: Save Error Handling**

*Input:*
```python
# Try to save to read-only directory
atomic_save_text("/root/protected.adoc", "content")
```

*Output:*
```
Raises: PermissionError
Error dialog: "Cannot save file: Permission denied"
Original file unchanged
No corruption occurred
```

**Example 3: User Workflow**

*Input:*
```
User edits document
User presses Ctrl+S
```

*Output:*
```
1. Content written atomically
2. Window title updated (remove *)
3. Status bar shows "Saved [filename]"
4. No data loss even if interrupted
```

### Test Requirements

- **Minimum Tests:** 15
- **Coverage Target:** 100%
- **Test Types:**
  - Unit: Basic save success (3 tests)
  - Unit: Error conditions (5 tests - permissions, disk full, invalid path)
  - Unit: Edge cases (3 tests - empty content, unicode, large file)
  - Integration: Save + UI update (2 tests)
  - Security: Path sanitization (2 tests)

**Example Test:**
```python
def test_atomic_save_prevents_corruption(tmp_path):
    """Verify atomic save doesn't corrupt file if interrupted."""
    file_path = tmp_path / "test.adoc"
    file_path.write_text("original content")

    # Simulate interruption during save
    with patch('os.rename', side_effect=OSError):
        result = atomic_save_text(file_path, "new content")

    assert result is False
    assert file_path.read_text() == "original content"  # Unchanged
```

### Implementation Guidance

**Approach:**
1. Generate temporary filename (e.g., `.test.adoc.tmp.XXXXX`)
2. Write content to temp file
3. Set correct permissions on temp file
4. Atomically rename temp file to target (os.replace())
5. Catch all exceptions and clean up temp file

**Security:**
- Validate and sanitize file path (prevent directory traversal)
- Set secure file permissions (0644)
- Prevent overwriting system files (/etc, /usr)
- Validate content size before write

**Performance:**
- Write in chunks for large files (>10MB)
- Use buffered I/O (io.BufferedWriter)
- Avoid loading entire content in memory for huge files

**Code Pattern:**
```python
def atomic_save_text(file_path: str | Path, content: str) -> bool:
    path = Path(sanitize_path(file_path))
    temp_path = path.with_suffix(path.suffix + ".tmp")

    try:
        # Write to temp file
        temp_path.write_text(content, encoding="utf-8")
        # Atomic rename
        temp_path.replace(path)
        return True
    except Exception as e:
        logger.error(f"Save failed: {e}")
        temp_path.unlink(missing_ok=True)  # Cleanup
        return False
```

### Verification Steps

1. **Normal Save:**
   - Create new document
   - Type content
   - Press Ctrl+S
   - Verify file exists with correct content

2. **Atomic Behavior:**
   - Open existing file
   - Modify content
   - Kill process during save (simulate crash)
   - Verify original file intact OR new content saved (no corruption)

3. **Error Handling:**
   - Try saving to /root (permission denied)
   - Verify error message displayed
   - Verify editor content preserved

4. **Performance:**
   - Save 10MB file
   - Measure save time <1 second

---

## FR-002: Line Numbers

**Category:** Core Editing
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/line_number_area.py`

### Description

Display line numbers alongside the text editor for easy navigation and reference. Line numbers update automatically as text is added or removed, and stay synchronized with editor scrolling.

### Acceptance Criteria

- [x] Line numbers visible in left margin of editor
- [x] Numbers synchronized with editor lines (1-to-1 mapping)
- [x] Numbers update automatically when lines added/removed
- [x] Numbers stay visible when scrolling
- [x] Width adjusts based on line count (1-9999+ lines)
- [x] Colors adapt to theme (dark/light mode)
- [x] No performance impact for large documents (10,000+ lines)
- [x] Numbers right-aligned for readability

### API Contract

```python
class LineNumberArea(QWidget):
    """Widget that displays line numbers for a QPlainTextEdit.

    This widget sits alongside the editor and shows line numbers
    for each visible line. It automatically updates when the editor
    is scrolled or text is added/removed.
    """

    def __init__(self, editor: QPlainTextEdit) -> None:
        """Initialize line number area.

        Args:
            editor: The QPlainTextEdit to show line numbers for
        """

    def sizeHint(self) -> QSize:
        """Return the recommended size for this widget."""

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint line numbers.

        Args:
            event: Paint event
        """


class LineNumberMixin:
    """Mixin class to add line number functionality to QPlainTextEdit.

    Usage:
        class MyEditor(LineNumberMixin, QPlainTextEdit):
            def __init__(self):
                super().__init__()
                self.setup_line_numbers()
    """

    def setup_line_numbers(self) -> None:
        """Set up line number area and connect signals."""

    def line_number_area_width(self) -> int:
        """Calculate width needed for line numbers.

        Returns:
            Width in pixels for line number area
        """

    def update_line_number_area_width(self, _: Any) -> None:
        """Update viewport margins to make room for line numbers."""

    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        """Update line number area when editor scrolls or changes.

        Args:
            rect: Rectangle that needs updating
            dy: Vertical scroll offset
        """

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        """Paint line numbers in the line number area.

        Args:
            event: Paint event
        """
```

### Examples

**Example 1: Basic Usage**

*Input:*
```python
from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit

editor = LineNumberPlainTextEdit()
editor.setPlainText("Line 1\nLine 2\nLine 3")
```

*Output:*
```
  1 | Line 1
  2 | Line 2
  3 | Line 3
```

**Example 2: Dynamic Update**

*Input:*
```python
editor = LineNumberPlainTextEdit()
editor.setPlainText("Line 1\nLine 2")
# User presses Enter at end of line 1
```

*Output:*
```
  1 | Line 1
  2 |
  3 | Line 2
```
Line numbers automatically renumber.

**Example 3: Large Document**

*Input:*
```python
# 1,000 line document
content = "\n".join([f"Line {i}" for i in range(1, 1001)])
editor.setPlainText(content)
```

*Output:*
```
    1 | Line 1
    2 | Line 2
  ...
 1000 | Line 1000
```
Width adjusts to 4 digits, right-aligned.

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 95%+
- **Test Types:**
  - Unit: Width calculation (2 tests)
  - Unit: Number painting (2 tests)
  - Integration: Editor + line numbers (3 tests)
  - Performance: 10K line update <50ms (1 test)

### Implementation Guidance

**Approach:**
1. Create `LineNumberArea` widget extending `QWidget`
2. Create `LineNumberMixin` for adding to `QPlainTextEdit`
3. Connect to `blockCountChanged` signal for line count updates
4. Connect to `updateRequest` signal for scroll/edit updates
5. Calculate width based on digit count of max line number
6. Paint visible line numbers in `paintEvent`

**Security:**
- No user input processed (read-only display)
- No file I/O operations

**Performance:**
- Only paint visible line numbers (not entire document)
- Use Qt's built-in block iteration (efficient)
- Cache font metrics calculations
- Debounce width updates (only when digit count changes)

**Code Pattern:**
```python
class LineNumberPlainTextEdit(LineNumberMixin, QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_line_numbers()
```

### Verification Steps

1. **Basic Display:**
   - Open editor
   - Type 10 lines of text
   - Verify line numbers 1-10 appear in left margin
   - Verify numbers right-aligned

2. **Dynamic Updates:**
   - Add line in middle (press Enter)
   - Verify all subsequent numbers increment
   - Delete line
   - Verify all subsequent numbers decrement

3. **Scrolling:**
   - Create 100-line document
   - Scroll to line 50
   - Verify line 50 visible with correct number
   - Verify numbers stay synchronized

4. **Theme:**
   - Toggle dark mode (F11)
   - Verify line number colors change
   - Verify background color adapts to theme

---

## FR-003: Undo/Redo

**Category:** Core Editing
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor)
**Version:** 1.7.2
**Implementation:** Qt's built-in `QPlainTextEdit` undo stack

### Description

Provide undo/redo functionality for text editing operations using Qt's built-in undo stack. Users can reverse and reapply changes with keyboard shortcuts or toolbar buttons.

### Acceptance Criteria

- [x] Undo reverts last edit operation (Ctrl+Z)
- [x] Redo reapplies undone operation (Ctrl+Y or Ctrl+Shift+Z)
- [x] Unlimited undo/redo history (memory permitting)
- [x] Undo/redo available via toolbar buttons
- [x] Undo/redo available via Edit menu
- [x] Keyboard shortcuts work consistently
- [x] Undo stack cleared when new document loaded
- [x] Multi-step undo (undo multiple operations)

### API Contract

```python
# Qt Built-in API (QPlainTextEdit)
class QPlainTextEdit:
    """Qt's text editor with built-in undo/redo stack."""

    def undo(self) -> None:
        """Undo the last operation if available."""

    def redo(self) -> None:
        """Redo the last undone operation if available."""

    def setUndoRedoEnabled(self, enable: bool) -> None:
        """Enable or disable undo/redo functionality.

        Args:
            enable: True to enable, False to disable
        """

    # Signals
    undoAvailable: Signal = Signal(bool)  # Emitted when undo availability changes
    redoAvailable: Signal = Signal(bool)  # Emitted when redo availability changes
```

### Examples

**Example 1: Basic Undo**

*Input:*
```
User types: "Hello"
User presses Ctrl+Z
```

*Output:*
```
Text reverts to: ""
```

**Example 2: Multi-Step Undo**

*Input:*
```
User types: "Line 1"
User presses Enter
User types: "Line 2"
User presses Ctrl+Z (once)
User presses Ctrl+Z (twice)
```

*Output:*
```
After first Ctrl+Z: "Line 1\n"
After second Ctrl+Z: "Line 1"
After third Ctrl+Z: ""
```

**Example 3: Redo After Undo**

*Input:*
```
User types: "Test"
User presses Ctrl+Z (undo)
User presses Ctrl+Y (redo)
```

*Output:*
```
After undo: ""
After redo: "Test"
```

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 95%+
- **Test Types:**
  - Unit: Undo single operation (2 tests)
  - Unit: Redo single operation (2 tests)
  - Unit: Multi-step undo (2 tests)
  - Integration: Undo/redo with toolbar (2 tests)
  - Integration: Undo/redo with menu (2 tests)

### Implementation Guidance

**Approach:**
1. Use Qt's built-in `QPlainTextEdit` undo stack (already implemented)
2. Enable undo/redo with `setUndoRedoEnabled(True)`
3. Create QAction for undo with `Ctrl+Z` shortcut
4. Create QAction for redo with `Ctrl+Y` and `Ctrl+Shift+Z` shortcuts
5. Connect actions to `undo()` and `redo()` methods
6. Connect `undoAvailable` signal to update undo button state
7. Connect `redoAvailable` signal to update redo button state

**Security:**
- No security concerns (read-only undo stack)
- Undo stack cleared on new document load (prevent data leaks)

**Performance:**
- Qt's undo stack is optimized for performance
- Memory usage proportional to edit history size
- Consider limiting undo stack size for very large documents (default: unlimited)

**Code Pattern:**
```python
# Setup in main window
self.editor.setUndoRedoEnabled(True)

# Create actions
undo_action = QAction("Undo", self)
undo_action.setShortcut(QKeySequence.StandardKey.Undo)
undo_action.triggered.connect(self.editor.undo)

redo_action = QAction("Redo", self)
redo_action.setShortcut(QKeySequence.StandardKey.Redo)
redo_action.triggered.connect(self.editor.redo)

# Update button states
self.editor.undoAvailable.connect(undo_action.setEnabled)
self.editor.redoAvailable.connect(redo_action.setEnabled)
```

### Verification Steps

1. **Basic Undo:**
   - Type text
   - Press Ctrl+Z
   - Verify text disappears
   - Verify undo button becomes disabled when no more undo

2. **Basic Redo:**
   - Type text
   - Press Ctrl+Z (undo)
   - Press Ctrl+Y (redo)
   - Verify text reappears

3. **Toolbar:**
   - Click undo button
   - Verify same as Ctrl+Z
   - Click redo button
   - Verify same as Ctrl+Y

4. **Multi-Step:**
   - Type 10 separate words
   - Press Ctrl+Z 5 times
   - Verify 5 words removed
   - Press Ctrl+Y 3 times
   - Verify 3 words restored

---

## FR-004: Font Customization

**Category:** Core Editing
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor), FR-074 (Settings)
**Version:** 1.7.0
**Implementation:** `src/asciidoc_artisan/core/settings.py`, UI in main window

### Description

Allow users to customize font family and size for editor, preview, and chat panes. Settings persist across sessions and provide live preview of changes.

### Acceptance Criteria

- [x] User can change editor font family
- [x] User can change editor font size (8-72 points)
- [x] User can change preview pane font family
- [x] User can change preview pane font size
- [x] User can change chat pane font family
- [x] User can change chat pane font size
- [x] Font settings persist across app restarts
- [x] Default fonts: Editor (Courier New 12pt), Preview (Arial 12pt), Chat (Arial 11pt)
- [x] Live preview when selecting fonts

### API Contract

```python
# Settings (stored in JSON)
class Settings(BaseModel):
    """Application settings with Pydantic validation."""

    # Editor font settings
    editor_font_family: str = "Courier New"
    editor_font_size: int = Field(default=12, ge=8, le=72)

    # Preview font settings
    preview_font_family: str = "Arial"
    preview_font_size: int = Field(default=12, ge=8, le=72)

    # Chat font settings
    chat_font_family: str = "Arial"
    chat_font_size: int = Field(default=11, ge=8, le=72)

    def save(self) -> None:
        """Save settings to disk (JSON format)."""

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from disk.

        Returns:
            Settings instance with loaded or default values
        """


# Font Application (in main window)
def apply_editor_font(self, family: str, size: int) -> None:
    """Apply font to editor.

    Args:
        family: Font family name (e.g., "Courier New")
        size: Font size in points (8-72)

    Raises:
        ValueError: If size out of range
    """

def apply_preview_font(self, family: str, size: int) -> None:
    """Apply font to preview pane.

    Args:
        family: Font family name
        size: Font size in points (8-72)
    """
```

### Examples

**Example 1: Change Editor Font**

*Input:*
```python
settings = Settings.load()
settings.editor_font_family = "Monospace"
settings.editor_font_size = 14
settings.save()

# Apply to editor
editor.setFont(QFont("Monospace", 14))
```

*Output:*
```
Editor displays text in Monospace 14pt font
Setting persists after app restart
```

**Example 2: Font Dialog**

*Input:*
```
User: Edit → Preferences → Fonts
User selects: "Courier New" font, 16pt size
User clicks OK
```

*Output:*
```
Editor font changes to Courier New 16pt
Change visible immediately (live preview)
Setting saved to ~/.config/AsciiDocArtisan/AsciiDocArtisan.json
```

**Example 3: Default Fonts**

*Input:*
```python
# First run (no settings file)
settings = Settings.load()
print(f"Editor: {settings.editor_font_family} {settings.editor_font_size}pt")
print(f"Preview: {settings.preview_font_family} {settings.preview_font_size}pt")
print(f"Chat: {settings.chat_font_family} {settings.chat_font_size}pt")
```

*Output:*
```
Editor: Courier New 12pt
Preview: Arial 12pt
Chat: Arial 11pt
```

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Settings validation (3 tests - valid, min, max)
  - Unit: Settings persistence (3 tests - save, load, defaults)
  - Integration: Font application (3 tests - editor, preview, chat)
  - Integration: Font dialog (3 tests - change, cancel, defaults)

### Implementation Guidance

**Approach:**
1. Define font settings in `Settings` Pydantic model
2. Add validation for font size (8-72 points)
3. Create font selection dialog (QFontDialog)
4. Apply font using `QFont(family, size)`
5. Save settings on font change
6. Load and apply fonts on app startup

**Security:**
- Validate font family against system fonts
- Sanitize font size (8-72 range)
- No file I/O beyond settings JSON

**Performance:**
- Font changes are instant (Qt optimized)
- Settings saved asynchronously
- No performance impact for typical usage

**Code Pattern:**
```python
# Font selection dialog
font, ok = QFontDialog.getFont(self.editor.font(), self)
if ok:
    # Apply to editor
    self.editor.setFont(font)

    # Save to settings
    self._settings.editor_font_family = font.family()
    self._settings.editor_font_size = font.pointSize()
    self._settings.save()
```

### Verification Steps

1. **Change Editor Font:**
   - Open Preferences dialog
   - Select new font (e.g., Monaco 14pt)
   - Verify editor updates immediately
   - Restart app
   - Verify font persists

2. **Change Preview Font:**
   - Open Preferences
   - Select preview font (e.g., Helvetica 13pt)
   - Verify preview pane updates
   - Check JSON file has correct values

3. **Font Size Range:**
   - Try setting size to 7 (invalid)
   - Verify error or clamped to 8
   - Try setting size to 73 (invalid)
   - Verify error or clamped to 72
   - Try setting size to 16 (valid)
   - Verify accepted

4. **Defaults:**
   - Delete settings file
   - Restart app
   - Verify default fonts applied

---

## FR-005: Editor State

**Category:** Core Editing
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor), FR-074 (Settings)
**Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/ui/editor_state.py`

### Description

Save and restore editor state including cursor position, scroll position, selection, pane sizes, zoom level, and theme. State persists across sessions for seamless resumption of work.

### Acceptance Criteria

- [x] Save cursor position (line, column)
- [x] Restore cursor position on file reopen
- [x] Save scroll position (vertical scroll offset)
- [x] Restore scroll position on file reopen
- [x] Save text selection (start, end)
- [x] Restore text selection on file reopen
- [x] Save splitter pane sizes
- [x] Restore splitter pane sizes on app restart
- [x] Save zoom level (editor and preview)
- [x] Restore zoom level on app restart
- [x] Save dark mode preference
- [x] Restore dark mode on app restart

### API Contract

```python
class EditorState:
    """Manage editor and window state."""

    def __init__(self, main_window: "AsciiDocEditor") -> None:
        """Initialize EditorState.

        Args:
            main_window: Main window instance (for accessing widgets and settings)
        """

    def zoom(self, delta: int) -> None:
        """Zoom editor and preview.

        Args:
            delta: Zoom direction (+1 for in, -1 for out)

        Raises:
            ValueError: If delta not in [-1, 1]
        """

    def toggle_maximize_editor(self) -> None:
        """Toggle editor pane maximization."""

    def toggle_maximize_preview(self) -> None:
        """Toggle preview pane maximization."""

    def toggle_dark_mode(self) -> None:
        """Toggle between dark and light themes."""

    def save_state(self) -> None:
        """Save current editor state to settings."""

    def restore_state(self) -> None:
        """Restore editor state from settings."""

    def handle_close_event(self, event: QCloseEvent) -> None:
        """Handle window close event, save state.

        Args:
            event: Close event
        """


# Settings State (in Settings model)
class Settings(BaseModel):
    """Application settings."""

    # Window state
    maximized: bool = True
    window_geometry: dict[str, int] | None = None
    splitter_sizes: list[int] | None = None

    # Theme
    dark_mode: bool = True

    # Zoom (implicitly via font_size)
    editor_font_size: int = 12
```

### Examples

**Example 1: Cursor Position Persistence**

*Input:*
```
User opens file.adoc
User places cursor at line 42, column 15
User closes app
User reopens app
User reopens file.adoc
```

*Output:*
```
Cursor restored to line 42, column 15
```

**Example 2: Splitter Sizes**

*Input:*
```
User adjusts splitter: Editor 60%, Preview 40%
User closes app
User restarts app
```

*Output:*
```
Splitter restored to 60/40 split
```

**Example 3: Zoom Level**

*Input:*
```
User presses Ctrl++ (zoom in 3 times)
Font size increases: 12 → 13 → 14 → 15
User closes app
User restarts app
```

*Output:*
```
Font size restored to 15pt
```

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 95%+
- **Test Types:**
  - Unit: State save (3 tests - cursor, scroll, selection)
  - Unit: State restore (3 tests - cursor, scroll, selection)
  - Integration: Splitter state (2 tests - save, restore)
  - Integration: Zoom state (2 tests - in, out)
  - Integration: Theme state (2 tests - save, restore)

### Implementation Guidance

**Approach:**
1. Create `EditorState` class to manage all state operations
2. Save state on window close event
3. Save state on file close
4. Restore state on app startup
5. Restore state on file open
6. Use Settings model for persistence
7. Track cursor position via `QTextCursor.position()`
8. Track scroll via `QScrollBar.value()`

**Security:**
- No sensitive data in state (only UI positions)
- Settings file has 0644 permissions

**Performance:**
- State save/restore is <10ms
- No performance impact during editing
- Lazy state updates (on close, not every keystroke)

**Code Pattern:**
```python
class EditorState:
    def save_state(self):
        """Save current state to settings."""
        # Cursor position
        cursor = self.editor.textCursor()
        self._settings.cursor_position = cursor.position()

        # Scroll position
        scrollbar = self.editor.verticalScrollBar()
        self._settings.scroll_position = scrollbar.value()

        # Splitter sizes
        self._settings.splitter_sizes = self.splitter.sizes()

        # Save to disk
        self._settings.save()

    def restore_state(self):
        """Restore state from settings."""
        if self._settings.cursor_position is not None:
            cursor = self.editor.textCursor()
            cursor.setPosition(self._settings.cursor_position)
            self.editor.setTextCursor(cursor)

        if self._settings.scroll_position is not None:
            scrollbar = self.editor.verticalScrollBar()
            scrollbar.setValue(self._settings.scroll_position)

        if self._settings.splitter_sizes is not None:
            self.splitter.setSizes(self._settings.splitter_sizes)
```

### Verification Steps

1. **Cursor Position:**
   - Open file
   - Place cursor at line 50
   - Close and reopen app
   - Verify cursor at line 50

2. **Scroll Position:**
   - Open large file (1000+ lines)
   - Scroll to line 500
   - Close and reopen app
   - Verify scroll position at line 500

3. **Splitter:**
   - Adjust splitter to 70/30 split
   - Close app
   - Restart app
   - Verify splitter at 70/30 split

4. **Zoom:**
   - Press Ctrl++ 5 times
   - Close app
   - Restart app
   - Verify zoom level maintained

5. **Theme:**
   - Toggle dark mode (F11)
   - Close app
   - Restart app
   - Verify theme preserved

---

## FR-006: Open Files

**Category:** File Operations
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor), FR-068 (Path Sanitization)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/file_operations_manager.py::open_file()`

### Description

Open AsciiDoc files from disk with support for multiple file formats (.adoc, .asciidoc, .asc, .txt). Provides file picker dialog, atomic read operations, and automatic format detection.

### Acceptance Criteria

- [x] Support .adoc file extension
- [x] Support .asciidoc file extension
- [x] Support .asc file extension
- [x] Support .txt file extension (plain text)
- [x] Keyboard shortcut Ctrl+O
- [x] File picker dialog shows supported formats
- [x] Load file content into editor
- [x] Update window title with filename
- [x] Add to recent files list
- [x] Handle file read errors gracefully (permissions, not found)
- [x] Use atomic read operations
- [x] Validate file path (sanitization)
- [x] UTF-8 encoding by default

### API Contract

```python
class FileOperationsManager:
    """Manages file open/save operations."""

    def open_file(self, file_path: str | Path | None = None) -> bool:
        """Open file in editor.

        Args:
            file_path: Path to file. If None, show file picker dialog.

        Returns:
            True if file opened successfully, False otherwise

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If no read permission
            ValueError: If file_path is invalid or suspicious

        Side Effects:
            - Loads file content into editor
            - Updates window title
            - Adds to recent files list
            - Emits file_opened signal

        Example:
            >>> manager.open_file("/home/user/doc.adoc")
            True
            >>> manager.open_file()  # Shows file picker
            True  # If user selects file and clicks Open
        """

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content from disk.

        Args:
            file_path: Path to file

        Returns:
            File content as string (UTF-8)

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If no read permission
            UnicodeDecodeError: If file is not UTF-8
        """


# Constants
SUPPORTED_OPEN_FILTER = (
    "AsciiDoc Files (*.adoc *.asciidoc *.asc);;"
    "Text Files (*.txt);;"
    "All Files (*)"
)
```

### Examples

**Example 1: Open via Dialog**

*Input:*
```
User presses Ctrl+O
User selects /home/user/document.adoc
User clicks Open
```

*Output:*
```
File picker shows:
- AsciiDoc Files (*.adoc *.asciidoc *.asc)
- Text Files (*.txt)
- All Files (*)

File content loaded into editor
Window title: "AsciiDoc Artisan - document.adoc"
Status bar: "Opened document.adoc"
Recent files: document.adoc added to list
```

**Example 2: Open via API**

*Input:*
```python
manager = FileOperationsManager(main_window)
success = manager.open_file("/docs/guide.asciidoc")
```

*Output:*
```
File /docs/guide.asciidoc loaded
Window title: "AsciiDoc Artisan - guide.asciidoc"
Recent files updated
Returns: True
```

**Example 3: Error Handling**

*Input:*
```python
# Try to open non-existent file
manager.open_file("/missing/file.adoc")
```

*Output:*
```
Raises: FileNotFoundError
Error dialog: "Cannot open file: File not found"
Editor content unchanged
Returns: False
```

### Test Requirements

- **Minimum Tests:** 15
- **Coverage Target:** 95%+
- **Test Types:**
  - Unit: File reading (3 tests - .adoc, .asciidoc, .txt)
  - Unit: Error conditions (4 tests - not found, permission, invalid path, encoding)
  - Integration: File picker dialog (2 tests - select, cancel)
  - Integration: Window updates (3 tests - title, status, recent files)
  - Integration: Format detection (3 tests - .adoc, .asciidoc, .asc)

### Implementation Guidance

**Approach:**
1. Show QFileDialog with SUPPORTED_OPEN_FILTER
2. Validate selected file path with `sanitize_path()`
3. Read file content with UTF-8 encoding
4. Load content into editor via `set_content()`
5. Update window title with filename
6. Add to recent files list (max 10)
7. Emit file_opened signal
8. Show success message in status bar

**Security:**
- Validate file path with `sanitize_path()` (prevent directory traversal)
- Check file size before reading (warn if >10MB)
- Validate file is readable
- Use UTF-8 encoding with error handling

**Performance:**
- Files >1MB use streaming I/O (LargeFileHandler)
- Files >10MB show progress dialog
- Lazy loading for very large files
- Read operations are fast (<100ms for typical files)

**Code Pattern:**
```python
def open_file(self, file_path=None):
    # Show dialog if path not provided
    if file_path is None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "Open AsciiDoc File",
            "",
            SUPPORTED_OPEN_FILTER
        )
        if not file_path:
            return False  # User cancelled

    # Validate path
    path = sanitize_path(file_path)
    if path is None:
        logger.error(f"Invalid path: {file_path}")
        return False

    try:
        # Read file
        content = path.read_text(encoding="utf-8")

        # Update editor
        self.window.editor.set_content(content)

        # Update UI
        self.window.setWindowTitle(f"{APP_NAME} - {path.name}")
        self.window.current_file_path = path

        # Add to recent files
        self._add_to_recent_files(path)

        return True
    except Exception as e:
        logger.error(f"Failed to open file: {e}")
        self._show_error_dialog(f"Cannot open file: {e}")
        return False
```

### Verification Steps

1. **Basic Open:**
   - Press Ctrl+O
   - Select document.adoc
   - Verify content appears in editor
   - Verify window title shows "AsciiDoc Artisan - document.adoc"

2. **Supported Formats:**
   - Open file.adoc → Success
   - Open file.asciidoc → Success
   - Open file.asc → Success
   - Open file.txt → Success

3. **Error Handling:**
   - Try opening /root/protected.adoc (permission denied)
   - Verify error dialog shown
   - Verify editor content unchanged

4. **Recent Files:**
   - Open 3 different files
   - Check File → Recent Files menu
   - Verify 3 files listed in order (most recent first)

5. **Large Files:**
   - Open 5MB file
   - Verify loads without delay
   - Open 15MB file
   - Verify progress dialog appears

---

## FR-008: Save As

**Category:** File Operations
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-007 (Save Files), FR-068 (Path Sanitization), FR-069 (Atomic Writes)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/file_operations_manager.py::save_file_as()`

### Description

Save current document to a new file path, allowing users to create copies or change file location/name. Uses atomic write operations and updates window title with new filename.

### Acceptance Criteria

- [x] Keyboard shortcut Ctrl+Shift+S
- [x] File picker dialog for destination path
- [x] Support .adoc extension (default)
- [x] Support .asciidoc extension
- [x] Support .txt extension
- [x] Use atomic write (prevent corruption)
- [x] Update window title with new filename
- [x] Update current file path to new location
- [x] Add new file to recent files list
- [x] Handle write errors gracefully

### API Contract

```python
def save_file_as(self) -> bool:
    """Save current document to new file path.

    Returns:
        True if saved successfully, False if user cancelled or error

    Side Effects:
        - Shows file save dialog
        - Writes content to selected path
        - Updates window title
        - Updates current_file_path
        - Adds to recent files
    """
```

### Examples

**Example 1: Save As New Name**

*Input:*
```
User presses Ctrl+Shift+S
User selects /docs/report_v2.adoc
User clicks Save
```

*Output:*
```
File saved to /docs/report_v2.adoc
Window title: "AsciiDoc Artisan - report_v2.adoc"
Current path updated
Recent files: report_v2.adoc added
Status: "Saved as report_v2.adoc"
```

**Example 2: Create Copy**

*Input:*
```
Current file: project.adoc
User: File → Save As
User selects: project_backup.adoc
```

*Output:*
```
Original file: project.adoc (unchanged)
New file: project_backup.adoc (created)
Current document now linked to project_backup.adoc
```

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 90%+
- **Test Types:** Unit (5), Integration (3), Error handling (2)

### Implementation Guidance

**Approach:** Show QFileDialog, validate path, use atomic_save_text(), update UI state

**Security:** Validate path with sanitize_path(), prevent overwriting system files

**Performance:** Atomic write <1s for typical files

---

## FR-009: New Document

**Category:** File Operations
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/file_operations_manager.py::new_file()`

### Description

Create a new blank AsciiDoc document. Prompts to save if current document has unsaved changes, then clears editor and resets window state.

### Acceptance Criteria

- [x] Keyboard shortcut Ctrl+N
- [x] Prompt to save if current document modified
- [x] Clear editor content
- [x] Reset window title to "Untitled.adoc"
- [x] Clear current file path
- [x] Reset undo/redo stack
- [x] Don't prompt if current document empty and unchanged

### API Contract

```python
def new_file(self) -> bool:
    """Create new blank document.

    Returns:
        True if new document created, False if user cancelled

    Side Effects:
        - Prompts to save if unsaved changes
        - Clears editor content
        - Resets window title
        - Clears undo stack
    """
```

### Examples

**Example 1: New from Clean State**

*Input:*
```
Current: Untitled.adoc (empty, no changes)
User presses Ctrl+N
```

*Output:*
```
Editor cleared
Window title: "AsciiDoc Artisan - Untitled.adoc"
No save prompt (document was empty)
```

**Example 2: New with Unsaved Changes**

*Input:*
```
Current: document.adoc (modified, unsaved)
User presses Ctrl+N
```

*Output:*
```
Dialog: "Save changes to document.adoc?"
  - Save: Saves current, then creates new
  - Don't Save: Discards changes, creates new
  - Cancel: Returns to document.adoc
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 95%+
- **Test Types:** Unit (4), Integration (4)

### Implementation Guidance

**Approach:** Check for unsaved changes, prompt if needed, clear editor, reset state

**Security:** No security concerns (in-memory operation)

**Performance:** Instant (<10ms)

---

## FR-010: Recent Files

**Category:** File Operations
**Priority:** Medium
**Status:** ✅ Implemented
**Dependencies:** FR-006 (Open Files), FR-074 (Settings)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/core/settings.py::recent_files`

### Description

Track recently opened files (max 10) and display in File menu for quick access. List persists across sessions and updates automatically when files are opened.

### Acceptance Criteria

- [x] Track up to 10 most recent files
- [x] Display in File → Recent Files submenu
- [x] Most recent file appears first
- [x] Clicking item opens that file
- [x] Persist list across app restarts
- [x] Remove non-existent files from list
- [x] Show full path in tooltip

### API Contract

```python
class Settings(BaseModel):
    """Application settings."""

    recent_files: list[str] = Field(default_factory=list, max_length=10)

def add_recent_file(self, file_path: str) -> None:
    """Add file to recent files list.

    Args:
        file_path: Absolute path to file
    """

def get_recent_files(self) -> list[str]:
    """Get list of recent files (most recent first)."""
```

### Examples

**Example 1: Opening Recent File**

*Input:*
```
Recent files: [/docs/a.adoc, /docs/b.adoc, /docs/c.adoc]
User: File → Recent Files → b.adoc
```

*Output:*
```
File /docs/b.adoc opened
Recent files reordered: [/docs/b.adoc, /docs/a.adoc, /docs/c.adoc]
```

**Example 2: List Limit**

*Input:*
```
Recent files: [file1.adoc, ..., file10.adoc] (10 files)
User opens file11.adoc
```

*Output:*
```
Recent files: [file11.adoc, file1.adoc, ..., file9.adoc]
file10.adoc removed (oldest dropped)
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 90%+
- **Test Types:** Unit (5), Integration (3)

### Implementation Guidance

**Approach:** Maintain list in Settings, update on file open, display in menu

**Security:** Validate paths before adding to list

**Performance:** List operations O(1) for append, menu update <50ms

---

## FR-011: Auto-Save

**Category:** File Operations
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-007 (Save Files), FR-074 (Settings)
**Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/ui/file_operations_manager.py::auto_save`

### Description

Automatically save current document at regular intervals to prevent data loss. Configurable interval (default 5 minutes), only saves if document has unsaved changes.

### Acceptance Criteria

- [x] Auto-save enabled by default
- [x] Default interval: 5 minutes (300 seconds)
- [x] Only save if document modified
- [x] Only save if file path is known
- [x] User can enable/disable in settings
- [x] User can configure interval (1-60 minutes)
- [x] Show auto-save indicator in status bar
- [x] Use atomic write operations

### API Contract

```python
class Settings(BaseModel):
    """Application settings."""

    auto_save_enabled: bool = True
    auto_save_interval: int = Field(default=300, ge=60, le=3600)  # seconds

class AutoSaveTimer:
    """Auto-save timer manager."""

    def __init__(self, interval: int = 300):
        """Initialize timer with interval in seconds."""

    def start(self) -> None:
        """Start auto-save timer."""

    def stop(self) -> None:
        """Stop auto-save timer."""

    def reset(self) -> None:
        """Reset timer to interval."""
```

### Examples

**Example 1: Auto-Save Trigger**

*Input:*
```
User edits document.adoc
Time: 5 minutes pass
Document has unsaved changes
```

*Output:*
```
Auto-save triggered
File saved atomically
Status bar: "Auto-saved at 14:32"
Timer resets
```

**Example 2: Skip When Unchanged**

*Input:*
```
Document: document.adoc
State: No unsaved changes
Time: 5 minutes pass
```

*Output:*
```
Auto-save skipped (no changes)
Timer resets
```

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 95%+
- **Test Types:** Unit (6), Integration (4), Timer (2)

### Implementation Guidance

**Approach:** QTimer triggers check every interval, save if modified and path exists

**Security:** Use same security as manual save (atomic writes, path validation)

**Performance:** Timer overhead <1ms, save operation same as manual save

---

## FR-012: Import DOCX

**Category:** File Operations
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-006 (Open Files)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/document_converter.py::docx_to_asciidoc()`

### Description

Import Microsoft Word (.docx) files and convert to AsciiDoc format. Uses python-docx library to extract text, preserving basic formatting (headings, lists, bold, italic).

### Acceptance Criteria

- [x] Support .docx file format
- [x] Convert headings (Heading 1 → =, Heading 2 → ==, etc.)
- [x] Convert bold text (*bold*)
- [x] Convert italic text (_italic_)
- [x] Convert bullet lists
- [x] Convert numbered lists
- [x] Preserve paragraph breaks
- [x] Handle large files (>10MB)
- [x] Show progress for long conversions

### API Contract

```python
def docx_to_asciidoc(docx_path: str | Path) -> str:
    """Convert DOCX file to AsciiDoc format.

    Args:
        docx_path: Path to .docx file

    Returns:
        Converted AsciiDoc text

    Raises:
        FileNotFoundError: If docx file doesn't exist
        ValueError: If file is not valid DOCX format
    """
```

### Examples

**Example 1: Basic Conversion**

*Input DOCX:*
```
Heading 1: Introduction
This is a paragraph with **bold** and *italic* text.
• Bullet item 1
• Bullet item 2
```

*Output AsciiDoc:*
```
= Introduction

This is a paragraph with *bold* and _italic_ text.

* Bullet item 1
* Bullet item 2
```

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:** Unit (6), Integration (3), Large file (1)

### Implementation Guidance

**Approach:** Use python-docx to parse, map styles to AsciiDoc syntax

**Security:** Validate DOCX format, limit file size

**Performance:** ~1-5 seconds for typical documents

---

## FR-013: Import PDF

**Category:** File Operations
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-006 (Open Files)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/document_converter.py::pdf_to_text()`

### Description

Extract text from PDF files using PyMuPDF (3-5x faster than alternatives). Preserves text content but not complex formatting. Optimized for large files.

### Acceptance Criteria

- [x] Support .pdf file format
- [x] Extract all text content
- [x] Preserve paragraph breaks
- [x] Handle multi-page documents
- [x] Use PyMuPDF for performance
- [x] Handle large PDFs (100+ pages)
- [x] Show progress indicator
- [x] Handle password-protected PDFs (prompt for password)

### API Contract

```python
def pdf_to_text(pdf_path: str | Path) -> str:
    """Extract text from PDF file.

    Args:
        pdf_path: Path to .pdf file

    Returns:
        Extracted text as string

    Raises:
        FileNotFoundError: If PDF doesn't exist
        PermissionError: If PDF is encrypted without password
    """
```

### Examples

**Example 1: PDF Text Extraction**

*Input:*
```
User: File → Import → PDF
User selects: report.pdf (10 pages)
```

*Output:*
```
Progress: "Extracting page 1/10..."
...
Progress: "Extracting page 10/10..."
Text loaded into editor
Window title: "AsciiDoc Artisan - report.adoc"
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 80%+
- **Test Types:** Unit (4), Integration (3), Large file (1)

### Implementation Guidance

**Approach:** Use PyMuPDF fitz library, extract page by page

**Security:** Validate PDF format, handle malformed files

**Performance:** PyMuPDF is 3-5x faster than alternatives, ~1s per page

---

## FR-014: Import Markdown

**Category:** File Operations
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-006 (Open Files)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/pandoc_worker.py`

### Description

Convert Markdown (.md) files to AsciiDoc format using Pandoc. Preserves headings, lists, code blocks, links, and other Markdown syntax.

### Acceptance Criteria

- [x] Support .md file format
- [x] Convert via Pandoc (background worker)
- [x] Convert headings (# → =, ## → ==, etc.)
- [x] Convert code blocks
- [x] Convert inline code
- [x] Convert links
- [x] Convert images
- [x] Convert tables
- [x] Handle large files
- [x] Show conversion progress

### API Contract

```python
class PandocWorker(QObject):
    """Background worker for Pandoc conversion."""

    conversion_complete = Signal(str)  # Converted text
    conversion_failed = Signal(str)    # Error message

    def convert_markdown_to_asciidoc(self, md_path: str) -> None:
        """Convert Markdown to AsciiDoc.

        Args:
            md_path: Path to .md file

        Emits:
            conversion_complete: On success with converted text
            conversion_failed: On error with error message
        """
```

### Examples

**Example 1: Markdown Conversion**

*Input Markdown:*
```markdown
# Title

This is a paragraph with `inline code`.

## Section

- Item 1
- Item 2

```python
print("code block")
```
```

*Output AsciiDoc:*
```
= Title

This is a paragraph with `inline code`.

== Section

* Item 1
* Item 2

[source,python]
----
print("code block")
----
```

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:** Unit (5), Integration (4), Pandoc (1)

### Implementation Guidance

**Approach:** Use Pandoc worker thread, convert via subprocess

**Security:** Use shell=False, validate paths, timeout protection

**Performance:** 1-3 seconds for typical files, scales with file size

---

## FR-015: Live Preview

**Category:** Preview System
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor)
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/preview_worker.py`

### Description

Real-time AsciiDoc preview pane showing rendered HTML output. Updates automatically as user types, with debouncing to prevent performance issues. Uses background worker thread to avoid blocking UI.

### Acceptance Criteria

- [x] Live preview pane showing rendered HTML
- [x] Auto-update on text changes (debounced)
- [x] Background rendering (worker thread)
- [x] Performance <200ms for small docs (<1000 lines)
- [x] Performance <750ms for large docs (1000-10000 lines)
- [x] Error messages shown in preview on invalid AsciiDoc
- [x] Preserve scroll position during updates
- [x] Support all AsciiDoc syntax (headings, lists, code, tables, etc.)

### API Contract

```python
class PreviewWorker(QObject):
    """Background worker for AsciiDoc rendering."""

    preview_ready = Signal(str)  # Rendered HTML
    preview_error = Signal(str)  # Error message

    def render_asciidoc(self, content: str) -> None:
        """Render AsciiDoc to HTML.

        Args:
            content: AsciiDoc text to render

        Emits:
            preview_ready: On success with HTML
            preview_error: On parse error with message
        """
```

### Examples

**Example 1: Basic Rendering**

*Input (Editor):*
```
= Document Title

== Section 1

This is a *bold* paragraph with _italic_ text.
```

*Output (Preview):*
```html
<h1>Document Title</h1>
<h2>Section 1</h2>
<p>This is a <strong>bold</strong> paragraph with <em>italic</em> text.</p>
```

### Test Requirements

- **Minimum Tests:** 15
- **Coverage Target:** 90%+
- **Test Types:** Unit (8), Integration (5), Performance (2)

### Implementation Guidance

**Approach:** Worker thread renders with asciidoc3, signal/slot for UI updates

**Performance:** Debounce 500ms, incremental rendering for large docs

---

## FR-016: GPU Acceleration

**Category:** Preview System
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** FR-015 (Live Preview)
**Version:** 1.4.0
**Implementation:** `src/asciidoc_artisan/ui/preview_handler_gpu.py`

### Description

GPU-accelerated preview rendering using QWebEngineView for 10-50x faster rendering and 70-90% less CPU usage. Auto-detects GPU availability with CPU fallback. 24-hour cache for GPU detection.

### Acceptance Criteria

- [x] Auto-detect GPU (NVIDIA, AMD, Intel)
- [x] Use QWebEngineView when GPU available
- [x] Fallback to QTextBrowser if no GPU
- [x] 10-50x rendering speedup with GPU
- [x] 70-90% CPU usage reduction
- [x] 24hr cache for GPU detection
- [x] Support CUDA, OpenCL, Vulkan, ROCm, Intel NPU
- [x] Smooth scrolling with GPU rendering

### API Contract

```python
def detect_gpu() -> tuple[bool, str]:
    """Detect GPU availability.

    Returns:
        (has_gpu, gpu_info) tuple

    Caches result for 24 hours in:
        ~/.cache/asciidoc_artisan/gpu_detection.json
    """

class PreviewHandlerGPU:
    """GPU-accelerated preview handler."""

    def __init__(self, parent: QWidget):
        """Initialize with GPU auto-detection."""

    def set_html(self, html: str) -> None:
        """Render HTML (GPU accelerated if available)."""
```

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 85%+
- **Test Types:** Unit (6), Integration (4), GPU detection (2)

### Implementation Guidance

**Approach:** Detect GPU on startup, use QWebEngineView if available

**Performance:** 10-50x faster than CPU-only, 70-90% less CPU

---

## FR-017: Scroll Sync

**Category:** Preview System
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-015 (Live Preview)
**Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/ui/scroll_manager.py`

### Description

Bidirectional scroll synchronization between editor and preview panes. When user scrolls one pane, the other scrolls proportionally to maintain visual alignment.

### Acceptance Criteria

- [x] Editor scroll → Preview scroll
- [x] Preview scroll → Editor scroll
- [x] Proportional scrolling (not 1:1 line mapping)
- [x] Toggle on/off (F11 or menu)
- [x] No scroll loops (prevent infinite feedback)
- [x] Smooth scrolling experience
- [x] Persist sync state in settings

### API Contract

```python
class ScrollManager:
    """Manage editor ↔ preview scroll synchronization."""

    def __init__(self, editor: QPlainTextEdit, preview: QWidget):
        """Initialize scroll manager."""

    def enable_sync(self) -> None:
        """Enable bidirectional scroll sync."""

    def disable_sync(self) -> None:
        """Disable scroll sync."""

    def sync_editor_to_preview(self, value: int) -> None:
        """Sync editor scroll position to preview."""

    def sync_preview_to_editor(self, value: int) -> None:
        """Sync preview scroll position to editor."""
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 90%+
- **Test Types:** Unit (4), Integration (4)

### Implementation Guidance

**Approach:** Connect scrollbar signals, use proportional mapping

**Performance:** <10ms per scroll event

---

## FR-018: Incremental Render

**Category:** Preview System
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-015 (Live Preview)
**Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/incremental_renderer.py`

### Description

Block-based incremental rendering with LRU cache for 3-5x faster edits. Only re-renders changed blocks, caches results using MD5 hashing.

### Acceptance Criteria

- [x] Block detection (split document into logical blocks)
- [x] MD5 hash tracking for change detection
- [x] LRU cache (max 100 blocks)
- [x] Only render changed blocks
- [x] 3-5x faster for small edits
- [x] Merge rendered blocks into full HTML
- [x] Cache hit rate >80% for typical editing

### API Contract

```python
class IncrementalPreviewRenderer:
    """Incremental block-based renderer with caching."""

    def __init__(self, cache_size: int = 100):
        """Initialize with LRU cache."""

    def render(self, content: str) -> str:
        """Render AsciiDoc incrementally.

        Returns:
            Fully rendered HTML
        """

    def get_cache_stats(self) -> dict:
        """Get cache statistics (hits, misses, hit rate)."""
```

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 90%+
- **Test Types:** Unit (7), Performance (3), Cache (2)

### Implementation Guidance

**Approach:** Split by blank lines, hash blocks, cache rendered HTML

**Performance:** 3-5x faster edits, >80% cache hit rate

---

## FR-019: Debounce

**Category:** Preview System
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** FR-015 (Live Preview)
**Version:** 1.5.0
**Implementation:** Preview debouncing in main window

### Description

Adaptive debouncing for preview updates to prevent excessive rendering during rapid typing. Default 500ms delay, dynamically adjusted based on document size.

### Acceptance Criteria

- [x] Default debounce delay: 500ms
- [x] Adaptive delay (longer for larger docs)
- [x] Cancel pending renders on new input
- [x] Show "Rendering..." indicator during delay
- [x] No render lag during typing
- [x] Configurable delay in settings (100ms-2000ms)

### API Contract

```python
class DebounceTimer:
    """Debounce timer for preview updates."""

    def __init__(self, delay_ms: int = 500):
        """Initialize with delay in milliseconds."""

    def trigger(self, callback: callable) -> None:
        """Trigger callback after delay.

        Resets timer if called again before delay expires.
        """

    def cancel(self) -> None:
        """Cancel pending callback."""
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 95%+
- **Test Types:** Unit (5), Integration (3)

### Implementation Guidance

**Approach:** QTimer with restart on new input

**Performance:** Prevents excessive rendering, smooth typing

---

## FR-020: Preview Themes

**Category:** Preview System
**Priority:** Medium
**Status:** ✅ Implemented
**Dependencies:** FR-015 (Live Preview), FR-055 (Themes)
**Version:** 1.0.0
**Implementation:** CSS injection in preview

### Description

Preview pane theme follows application theme (dark/light mode). CSS injection for consistent styling.

### Acceptance Criteria

- [x] Dark mode CSS for preview
- [x] Light mode CSS for preview
- [x] Auto-switch with app theme toggle (F11)
- [x] Preserve preview colors/fonts
- [x] Syntax highlighting in code blocks
- [x] Readable in both themes

### API Contract

```python
def apply_preview_theme(preview_widget: QWidget, dark_mode: bool) -> None:
    """Apply theme CSS to preview.

    Args:
        preview_widget: Preview widget
        dark_mode: True for dark theme, False for light
    """
```

### Test Requirements

- **Minimum Tests:** 6
- **Coverage Target:** 85%+
- **Test Types:** Unit (4), Integration (2)

### Implementation Guidance

**Approach:** Inject CSS into preview HTML based on theme

**Performance:** Instant theme switching

---

## FR-069: Atomic Writes

**Category:** Security
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** None
**Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/core/file_operations.py::atomic_save_text()`

### Description

Atomic file write operations using temp file + rename pattern to prevent file corruption if save interrupted. Critical for data integrity.

### Acceptance Criteria

- [x] Write to temporary file first
- [x] Atomic rename to target path (os.replace())
- [x] No corruption if interrupted (crash/power loss)
- [x] Preserve file permissions
- [x] Clean up temp file on error
- [x] UTF-8 encoding by default
- [x] Used by all save operations

### API Contract

```python
def atomic_save_text(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """Save text content atomically.

    Writes to temporary file first, then renames to target path.
    Prevents corruption if save interrupted.

    Args:
        file_path: Target file path
        content: Text content to save
        encoding: Text encoding (default: utf-8)

    Returns:
        True if save successful, False otherwise

    Raises:
        PermissionError: If no write permission
        OSError: If disk full or I/O error
    """
```

### Examples

**Example 1: Normal Save**

*Input:*
```python
atomic_save_text(Path("/docs/file.adoc"), "content")
```

*Output:*
```
1. Write to /docs/.file.adoc.tmp
2. Rename /docs/.file.adoc.tmp → /docs/file.adoc
Result: True, file saved atomically
```

**Example 2: Interrupted Save**

*Input:*
```python
# Process crashes during write to temp file
atomic_save_text(Path("/docs/file.adoc"), "content")
# <CRASH>
```

*Output:*
```
Temp file may exist: /docs/.file.adoc.tmp
Original file intact: /docs/file.adoc (unchanged)
No corruption occurred
```

### Test Requirements

- **Minimum Tests:** 15 (same as FR-007)
- **Coverage Target:** 100%
- **Test Types:** Unit (8), Integration (5), Error handling (2)

### Implementation Guidance

**Approach:** Write to `{filename}.tmp`, then `os.replace()` for atomicity

**Security:** Prevent temp file disclosure, clean up on error

**Performance:** Same speed as regular write, atomicity adds <5ms

---

## FR-070: Subprocess Safety

**Category:** Security
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** None
**Version:** 1.0.0
**Implementation:** All worker files use `shell=False`

### Description

All subprocess calls use `shell=False` with list-form arguments to prevent shell injection attacks. Critical security requirement for Git, Pandoc, and other external commands.

### Acceptance Criteria

- [x] All subprocess calls use shell=False
- [x] All arguments passed as list (not string)
- [x] No user input in shell commands
- [x] Timeout protection (60s default)
- [x] Verified in GitWorker
- [x] Verified in PandocWorker
- [x] Verified in GitHubCLIWorker

### API Contract

```python
# CORRECT (safe)
subprocess.run(
    ["git", "commit", "-m", user_message],
    shell=False,  # Prevents shell injection
    timeout=60
)

# INCORRECT (vulnerable to injection)
subprocess.run(
    f"git commit -m '{user_message}'",
    shell=True  # DANGEROUS!
)
```

### Examples

**Example 1: Safe Git Command**

*Input:*
```python
message = "fix: update docs"
subprocess.run(["git", "commit", "-m", message], shell=False)
```

*Output:*
```
Executes: git commit -m "fix: update docs"
No shell injection possible
Safe even if message contains special chars
```

**Example 2: Prevented Injection**

*Input:*
```python
# Malicious input
message = "valid'; rm -rf /; echo 'pwned"

# Safe execution
subprocess.run(["git", "commit", "-m", message], shell=False)
```

*Output:*
```
Git receives literal message string
No shell expansion
rm -rf / never executed
Injection prevented
```

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 100%
- **Test Types:** Unit (6), Security (4)

### Implementation Guidance

**Approach:** Always use list form, never shell=True

**Security:** Validates ALL subprocess calls in codebase

**Performance:** No performance impact

---

## FR-071: Secure Credentials

**Category:** Security
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** None
**Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/core/secure_credentials.py`

### Description

Store sensitive credentials (API keys) in OS keyring, never in plain text files. Uses keyring library for secure cross-platform credential storage.

### Acceptance Criteria

- [x] Store credentials in OS keyring
- [x] Never store in plain text files
- [x] Never store in settings JSON
- [x] Cross-platform support (Linux/Mac/Windows)
- [x] Used for Anthropic API keys
- [x] Secure get/set/delete operations
- [x] No credentials in logs

### API Contract

```python
class SecureCredentials:
    """Secure credential storage using OS keyring."""

    @staticmethod
    def set_credential(service: str, username: str, password: str) -> None:
        """Store credential in OS keyring.

        Args:
            service: Service name (e.g., "anthropic_api")
            username: Username/key identifier
            password: API key/password to store
        """

    @staticmethod
    def get_credential(service: str, username: str) -> str | None:
        """Retrieve credential from OS keyring.

        Returns:
            Credential if found, None otherwise
        """

    @staticmethod
    def delete_credential(service: str, username: str) -> None:
        """Delete credential from OS keyring."""
```

### Examples

**Example 1: Store API Key**

*Input:*
```python
SecureCredentials.set_credential(
    "anthropic_api",
    "default",
    "sk-ant-..."
)
```

*Output:*
```
Linux: Stored in GNOME Keyring / KDE Wallet
Mac: Stored in macOS Keychain
Windows: Stored in Windows Credential Manager
Never in plain text files
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 95%+
- **Test Types:** Unit (5), Integration (3)

### Implementation Guidance

**Approach:** Use keyring library, fallback to encrypted file if keyring unavailable

**Security:** OS-level encryption, never plain text

**Performance:** Keyring access <50ms

---

## FR-072: HTTPS Enforcement

**Category:** Security
**Priority:** High
**Status:** ✅ Implemented
**Dependencies:** None
**Version:** 1.0.0
**Implementation:** httpx library with SSL verification

### Description

All HTTP requests use HTTPS with SSL certificate verification. No insecure HTTP connections allowed for API calls.

### Acceptance Criteria

- [x] All API calls use HTTPS
- [x] SSL certificate verification enabled
- [x] No HTTP (insecure) connections
- [x] Used for Anthropic API
- [x] Used for Ollama API (localhost exception)
- [x] Certificate validation errors shown to user

### API Contract

```python
import httpx

# CORRECT (secure)
response = httpx.get(
    "https://api.anthropic.com/...",
    verify=True  # SSL verification enabled
)

# INCORRECT (insecure)
response = httpx.get(
    "http://api.anthropic.com/...",  # HTTP not HTTPS!
    verify=False  # Disables SSL verification!
)
```

### Examples

**Example 1: Secure API Call**

*Input:*
```python
response = httpx.post(
    "https://api.anthropic.com/v1/messages",
    headers={"x-api-key": api_key},
    json=payload,
    verify=True
)
```

*Output:*
```
SSL certificate verified
Encrypted connection established
Request sent securely
```

### Test Requirements

- **Minimum Tests:** 6
- **Coverage Target:** 90%+
- **Test Types:** Unit (4), Integration (2)

### Implementation Guidance

**Approach:** Use httpx with verify=True, reject HTTP URLs

**Security:** Prevents MITM attacks, ensures encryption

**Performance:** SSL handshake adds ~100ms per connection

---

## FR-075: Type Safety

**Category:** Quality
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** None
**Version:** 1.6.0 (modernized Nov 2025)
**Implementation:** 100% type hints across 95 files

### Description

Complete type hint coverage with mypy --strict validation. Modern Python 3.12+ syntax (list, dict, X | None). Zero mypy errors enforced by CI.

### Acceptance Criteria

- [x] 100% type hint coverage
- [x] mypy --strict passes (0 errors)
- [x] Python 3.12+ syntax (list, dict, X | None)
- [x] All functions have type hints
- [x] All class attributes typed
- [x] Generic types used correctly
- [x] 95 files fully typed

### API Contract

```python
# Modern Python 3.12+ syntax
def process_files(
    paths: list[str],  # Not List[str]
    config: dict[str, Any],  # Not Dict[str, Any]
    timeout: int | None = None  # Not Optional[int]
) -> tuple[bool, str]:  # Not Tuple[bool, str]
    """Process files with full type safety."""
```

### Examples

**Example 1: Function Typing**

*Input:*
```python
def save_file(path: str | Path, content: str) -> bool:
    """Save file atomically.

    Args:
        path: File path (string or Path object)
        content: Text content to save

    Returns:
        True if successful, False otherwise
    """
```

**Example 2: Class Typing**

*Input:*
```python
class Settings(BaseModel):
    """Application settings with full type safety."""

    recent_files: list[str] = Field(default_factory=list)
    font_size: int = Field(default=12, ge=8, le=72)
    dark_mode: bool = True
```

### Test Requirements

- **Minimum Tests:** mypy validation (not unit tests)
- **Coverage Target:** 100% type coverage
- **Test Types:** Static analysis (mypy --strict)

### Implementation Guidance

**Approach:** Add type hints to all functions, classes, variables

**Security:** Catches type errors at development time

**Performance:** No runtime impact (static analysis only)

---

## FR-076: Test Coverage

**Category:** Quality
**Priority:** Critical
**Status:** ✅ Implemented
**Dependencies:** None
**Version:** 2.0.8
**Implementation:** 5,548 unit tests (99.42% pass) + 71 E2E scenarios (91.5% pass), 96.4% coverage

### Description

Comprehensive test suite with 96.4% code coverage. 5,548 unit tests (5,516 passing, 22 skipped) + 71 E2E BDD scenarios (65 passing, 6 skipped). pytest + pytest-qt + pytest-bdd framework.

### Acceptance Criteria

- [x] 96.4% code coverage (near maximum achievable)
- [x] 5,548 unit tests (99.42% pass rate)
- [x] 71 E2E scenarios (91.5% pass rate, 100% individually)
- [x] 22 unit tests skipped (documented reasons)
- [x] 6 E2E tests skipped (Qt threading limitations)
- [x] pytest + pytest-qt + pytest-bdd framework
- [x] Coverage report generated (htmlcov/)
- [x] Pre-commit hooks enforce tests

### API Contract

```python
# Test structure
def test_feature_name(qtbot):
    """Test feature with Qt integration.

    Args:
        qtbot: pytest-qt fixture for GUI testing
    """
    # Arrange
    widget = MyWidget()
    qtbot.addWidget(widget)

    # Act
    widget.do_something()

    # Assert
    assert widget.state == expected_state
```

### Examples

**Example 1: Running Tests**

*Input:*
```bash
make test
```

*Output:*
```
===== test session starts =====
collected 5479 items

tests/test_core.py ................  [ 10%]
tests/test_ui.py ...................  [ 30%]
...
===== 204 passed in 45.23s =====

Coverage: 96.4%
Report: htmlcov/index.html
```

### Test Requirements

- **Minimum Tests:** 200+ (currently 204)
- **Coverage Target:** 100% (currently 96.4%)
- **Test Types:** Unit (150+), Integration (40+), GUI (14+)

### Implementation Guidance

**Approach:** pytest + pytest-qt, comprehensive coverage

**Security:** Tests validate security features

**Performance:** Full test suite ~45s

---

## FR-021: Export HTML

**Category:** Export System | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-015 (Live Preview) | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/pandoc_worker.py`

### Description
Export AsciiDoc to standalone HTML with embedded CSS. Uses asciidoc3 for rendering.

### Acceptance Criteria
- [x] Export to .html format | [x] Standalone HTML (no external dependencies)
- [x] Embedded CSS styling | [x] Preserve all AsciiDoc features
- [x] Keyboard shortcut Ctrl+E → HTML | [x] File save dialog

### API Contract
```python
def export_html(content: str, output_path: Path) -> bool:
    """Export AsciiDoc to HTML."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 85%+ | **Types:** Unit (5), Integration (3)

---

## FR-022: Export PDF

**Category:** Export System | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-021 (Export HTML) | **Version:** 1.0.0
**Implementation:** `wkhtmltopdf` via subprocess

### Description
Export AsciiDoc to PDF using wkhtmltopdf (HTML → PDF pipeline).

### Acceptance Criteria
- [x] Export to .pdf format | [x] Requires wkhtmltopdf installed
- [x] Page formatting preserved | [x] Hyperlinks work in PDF
- [x] Handle large documents (100+ pages) | [x] Show progress indicator

### API Contract
```python
def export_pdf(html_content: str, output_path: Path) -> bool:
    """Export HTML to PDF using wkhtmltopdf."""
```

### Test Requirements
**Min Tests:** 6 | **Coverage:** 80%+ | **Types:** Unit (4), Integration (2)

---

## FR-023: Export DOCX

**Category:** Export System | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/pandoc_worker.py`

### Description
Export AsciiDoc to Microsoft Word (.docx) using Pandoc. Optional AI enhancement via Ollama.

### Acceptance Criteria
- [x] Export to .docx format | [x] Use Pandoc for conversion
- [x] Optional Ollama AI enhancement | [x] Preserve formatting (headings, lists, tables)
- [x] Background worker (non-blocking) | [x] Error handling for Pandoc failures

### API Contract
```python
class PandocWorker(QObject):
    conversion_complete = Signal(str)
    def export_docx(self, content: str, output_path: Path, use_ai: bool = False) -> None:
        """Export to DOCX, optionally AI-enhanced."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-024: Export Markdown

**Category:** Export System | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/pandoc_worker.py`

### Description
Export AsciiDoc to Markdown format using Pandoc conversion.

### Acceptance Criteria
- [x] Export to .md format | [x] Use Pandoc worker
- [x] Convert headings correctly | [x] Convert code blocks
- [x] Convert tables | [x] Handle conversion errors

### API Contract
```python
def export_markdown(content: str, output_path: Path) -> bool:
    """Export AsciiDoc to Markdown via Pandoc."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 85%+ | **Types:** Unit (5), Integration (3)

---

## FR-025: AI Export Enhancement

**Category:** Export System | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-039 (Ollama) | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/workers/ollama_chat_worker.py`

### Description
AI-enhanced export using Ollama (improve-grammar, llama2, mistral, codellama models). Fallback to Pandoc if Ollama unavailable.

### Acceptance Criteria
- [x] Ollama AI models: improve-grammar, llama2, mistral, codellama
- [x] Fallback to Pandoc if Ollama unavailable | [x] 2KB context window
- [x] Background processing | [x] Error handling with user notification

### API Contract
```python
class OllamaChatWorker(QObject):
    enhancement_complete = Signal(str)
    def enhance_export(self, content: str, model: str = "improve-grammar") -> None:
        """Enhance content with AI before export."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 80%+ | **Types:** Unit (7), Integration (5)

---

## FR-026: Select Repository

**Category:** Git Integration | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/git_worker.py`

### Description
Select Git repository for version control operations. Auto-detects if current directory is a Git repo on startup.

### Acceptance Criteria
- [x] Auto-detect Git repo on startup | [x] Manual repo selection dialog
- [x] Validate selected path is Git repo | [x] Display current repo in status bar
- [x] Enable/disable Git features based on repo status | [x] Handle non-repo directories gracefully

### API Contract
```python
class GitWorker(BaseWorker):
    repo_selected = Signal(str)  # Repository path
    def select_repo(self, path: str | Path) -> None:
        """Select Git repository for operations."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 90%+ | **Types:** Unit (5), Integration (3)

---

## FR-027: Git Commit

**Category:** Git Integration | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/git_worker.py`

### Description
Commit changes with message. Supports staged files, all changes, or selective commit. Background worker prevents UI blocking.

### Acceptance Criteria
- [x] Commit with message | [x] Stage + commit in one operation
- [x] Selective file commit | [x] Commit all tracked changes
- [x] Validation: non-empty message | [x] Background processing (QThread)
- [x] Success/error notifications | [x] Reentrancy guard (_is_processing_git)

### API Contract
```python
class GitWorker(BaseWorker):
    commit_complete = Signal(bool, str)  # (success, message)
    def commit(self, message: str, files: list[str] | None = None) -> None:
        """Commit changes with message.

        Args:
            message: Commit message (required, non-empty)
            files: Specific files to commit, or None for all staged
        """
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 95%+ | **Types:** Unit (7), Integration (5)

---

## FR-028: Git Pull

**Category:** Git Integration | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/git_worker.py`

### Description
Pull changes from remote repository. Handles merge conflicts, fast-forward, and errors. 60-second timeout.

### Acceptance Criteria
- [x] Pull from current branch's remote | [x] Handle fast-forward merges
- [x] Detect merge conflicts | [x] Show detailed error messages
- [x] 60-second timeout | [x] Background processing
- [x] Reentrancy guard | [x] Update status bar after pull

### API Contract
```python
class GitWorker(BaseWorker):
    pull_complete = Signal(bool, str)  # (success, output)
    def pull(self) -> None:
        """Pull changes from remote repository."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 90%+ | **Types:** Unit (6), Integration (4)

---

## FR-029: Git Push

**Category:** Git Integration | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/workers/git_worker.py`

### Description
Push local commits to remote repository. Validates remote exists, handles errors, prevents force push without confirmation.

### Acceptance Criteria
- [x] Push to current branch's remote | [x] Validate remote configured
- [x] Handle push rejection (needs pull) | [x] Detailed error messages
- [x] 60-second timeout | [x] Background processing
- [x] Reentrancy guard | [x] Confirm before force push

### API Contract
```python
class GitWorker(BaseWorker):
    push_complete = Signal(bool, str)  # (success, output)
    def push(self, force: bool = False) -> None:
        """Push commits to remote.

        Args:
            force: If True, force push (requires confirmation)
        """
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 90%+ | **Types:** Unit (6), Integration (4)

---

## FR-030: Git Status Bar

**Category:** Git Integration | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.9.0
**Implementation:** `src/asciidoc_artisan/ui/git_manager.py`

### Description
Display Git status in status bar: branch name, modified/staged/untracked counts, color indicators.

### Acceptance Criteria
- [x] Show current branch name | [x] Modified file count (yellow)
- [x] Staged file count (green) | [x] Untracked file count (blue)
- [x] Update on file changes | [x] Click to open Git Status Dialog
- [x] Hide when not in Git repo

### API Contract
```python
class GitManager:
    def update_status_bar(self) -> None:
        """Update Git status in status bar."""
    def format_status(self, branch: str, modified: int, staged: int, untracked: int) -> str:
        """Format status text with color indicators."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 85%+ | **Types:** Unit (5), Integration (3)

---

## FR-031: Git Status Dialog

**Category:** Git Integration | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.9.0
**Implementation:** `src/asciidoc_artisan/ui/git_status_dialog.py`

### Description
Full Git status dialog with 3 tabs (Modified/Staged/Untracked), checkboxes for staging, commit action. Shortcut: Ctrl+Shift+G.

### Acceptance Criteria
- [x] 3 tabs: Modified, Staged, Untracked | [x] Checkboxes to stage/unstage files
- [x] Commit button with message input | [x] Refresh button
- [x] Double-click file to view diff | [x] Ctrl+Shift+G shortcut
- [x] Auto-refresh after Git operations | [x] File path display with icons

### API Contract
```python
class GitStatusDialog(QDialog):
    def __init__(self, parent: QWidget, git_worker: GitWorker):
        """Initialize Git status dialog."""
    def refresh_status(self) -> None:
        """Refresh Git status from worker."""
    def stage_selected_files(self) -> None:
        """Stage files checked in Modified tab."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 85%+ | **Types:** Unit (8), Integration (7)

---

## FR-032: Quick Commit Widget

**Category:** Git Integration | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026, FR-027 | **Version:** 1.9.0
**Implementation:** `src/asciidoc_artisan/ui/quick_commit_widget.py`

### Description
Inline commit widget at bottom of window. Type message, press Enter to commit. Shortcuts: Ctrl+G to focus, Esc to hide.

### Acceptance Criteria
- [x] Single-line message input | [x] Enter key commits
- [x] Esc key hides widget | [x] Ctrl+G shortcut to show/focus
- [x] Show modified file count | [x] Disable if no changes
- [x] Clear message after commit | [x] Show commit success/error

### API Contract
```python
class QuickCommitWidget(QWidget):
    def __init__(self, parent: QWidget, git_worker: GitWorker):
        """Initialize quick commit widget."""
    def show_and_focus(self) -> None:
        """Show widget and focus message input."""
    def commit_changes(self) -> None:
        """Commit with current message."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-033: Cancel Git Operations

**Category:** Git Integration | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/workers/git_worker.py`

### Description
Cancel long-running Git operations (pull, push, large commits). Terminate subprocess, reset state, notify user.

### Acceptance Criteria
- [x] Cancel button during operations | [x] Terminate subprocess
- [x] Reset reentrancy guards | [x] User notification
- [x] Clean up temp resources | [x] No corruption on cancel

### API Contract
```python
class GitWorker(BaseWorker):
    operation_cancelled = Signal()
    def cancel_operation(self) -> None:
        """Cancel current Git operation."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 80%+ | **Types:** Unit (5), Integration (3)

---

## FR-034: Create Pull Request

**Category:** GitHub CLI | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026 (Git) | **Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/workers/github_cli_worker.py`

### Description
Create GitHub pull request via gh CLI. Input: title, description, base branch. Validates repo, handles errors, opens PR URL in browser.

### Acceptance Criteria
- [x] Create PR with title and description | [x] Select base branch (default: main)
- [x] Validate gh CLI installed | [x] Validate GitHub repo configured
- [x] Open PR URL in browser after creation | [x] 60-second timeout
- [x] Background processing (QThread) | [x] Detailed error messages

### API Contract
```python
class GitHubCLIWorker(BaseWorker):
    pr_created = Signal(str)  # PR URL
    def create_pr(self, title: str, body: str, base: str = "main") -> None:
        """Create pull request.

        Args:
            title: PR title (required, non-empty)
            body: PR description
            base: Base branch (default: main)
        """
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Integration (5)

---

## FR-035: List Pull Requests

**Category:** GitHub CLI | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/workers/github_cli_worker.py`

### Description
List open pull requests for current repo. Shows PR number, title, author, status. Click to open in browser.

### Acceptance Criteria
- [x] List open PRs | [x] Display: PR#, title, author, status
- [x] Filter by state (open/closed/all) | [x] Click PR to open in browser
- [x] Refresh button | [x] Handle repo with no PRs
- [x] Error handling for network issues

### API Contract
```python
class GitHubCLIWorker(BaseWorker):
    prs_listed = Signal(list)  # List of PR dicts
    def list_prs(self, state: str = "open") -> None:
        """List pull requests.

        Args:
            state: PR state filter (open/closed/all)
        """
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-036: Create Issue

**Category:** GitHub CLI | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/workers/github_cli_worker.py`

### Description
Create GitHub issue via gh CLI. Input: title, description, labels (optional). Opens issue URL in browser after creation.

### Acceptance Criteria
- [x] Create issue with title and body | [x] Optional labels
- [x] Validate gh CLI and repo | [x] Open issue URL in browser
- [x] 60-second timeout | [x] Background processing
- [x] Error handling for network/auth failures

### API Contract
```python
class GitHubCLIWorker(BaseWorker):
    issue_created = Signal(str)  # Issue URL
    def create_issue(self, title: str, body: str, labels: list[str] | None = None) -> None:
        """Create GitHub issue.

        Args:
            title: Issue title (required)
            body: Issue description
            labels: Optional list of label names
        """
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-037: List Issues

**Category:** GitHub CLI | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/workers/github_cli_worker.py`

### Description
List issues for current repo. Filter by state, labels. Display: issue#, title, author, labels, status.

### Acceptance Criteria
- [x] List issues (open/closed/all) | [x] Display: issue#, title, author, labels
- [x] Filter by labels | [x] Click issue to open in browser
- [x] Refresh button | [x] Sort by created/updated date
- [x] Handle repo with no issues

### API Contract
```python
class GitHubCLIWorker(BaseWorker):
    issues_listed = Signal(list)  # List of issue dicts
    def list_issues(self, state: str = "open", labels: list[str] | None = None) -> None:
        """List GitHub issues.

        Args:
            state: Issue state (open/closed/all)
            labels: Filter by labels
        """
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-038: View Repository

**Category:** GitHub CLI | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** FR-026 | **Version:** 1.6.0
**Implementation:** `src/asciidoc_artisan/workers/github_cli_worker.py`

### Description
Open current repository in browser. Uses gh CLI to get repo URL and opens in default browser.

### Acceptance Criteria
- [x] Get repo URL via gh CLI | [x] Open in default browser
- [x] Handle non-GitHub repos gracefully | [x] Error notification
- [x] Keyboard shortcut (Ctrl+Alt+G) | [x] Menu item: Git → GitHub → View Repo

### API Contract
```python
class GitHubCLIWorker(BaseWorker):
    repo_url_ready = Signal(str)  # Repository URL
    def get_repo_url(self) -> None:
        """Get GitHub repository URL."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 80%+ | **Types:** Unit (5), Integration (3)

---

## FR-039: Ollama Chat Panel

**Category:** AI Features | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/ui/chat_panel_widget.py`

### Description
Chat interface for Ollama local AI models. Sidebar panel with message history, model selection, 4 chat modes. 2KB context window, 100-message history.

### Acceptance Criteria
- [x] Sidebar chat panel (dockable) | [x] Message input area (multi-line)
- [x] Chat history display (scrollable) | [x] Model selection dropdown
- [x] 4 chat modes: Doc Q&A, Syntax Help, General, Editing | [x] 2KB context window
- [x] Persistent 100-message history | [x] Clear history button
- [x] Keyboard shortcuts: Ctrl+Return to send | [x] Error handling and status indicators

### API Contract
```python
class ChatPanelWidget(QWidget):
    def __init__(self, parent: QWidget, ollama_worker: OllamaChatWorker):
        """Initialize chat panel."""
    def send_message(self, text: str, mode: str) -> None:
        """Send message to Ollama."""
    def append_message(self, role: str, content: str) -> None:
        """Add message to history."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 85%+ | **Types:** Unit (9), Integration (6)

---

## FR-040: Ollama Chat Modes

**Category:** AI Features | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-039 | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/workers/ollama_chat_worker.py`

### Description
4 specialized chat modes with tailored system prompts: Doc Q&A (answer questions about document), Syntax Help (AsciiDoc syntax), General (coding/writing), Editing (improve text).

### Acceptance Criteria
- [x] Doc Q&A mode: Includes current document context | [x] Syntax Help mode: AsciiDoc reference
- [x] General mode: Coding and writing assistance | [x] Editing mode: Text improvement suggestions
- [x] Mode selector in chat panel | [x] System prompts tailored per mode
- [x] Context injection (2KB limit) | [x] Clear mode indicators

### API Contract
```python
class OllamaChatWorker(QObject):
    def set_chat_mode(self, mode: str) -> None:
        """Set chat mode.

        Args:
            mode: One of 'doc_qa', 'syntax_help', 'general', 'editing'
        """
    def send_message(self, text: str, context: str | None = None) -> None:
        """Send message with optional document context."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (8), Integration (4)

---

## FR-041: Ollama Model Selection

**Category:** AI Features | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-039 | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/workers/ollama_chat_worker.py`

### Description
Model selection for Ollama: improve-grammar, llama2, mistral, codellama. Auto-detect available models, fallback to default if model unavailable.

### Acceptance Criteria
- [x] Model dropdown in chat panel | [x] Auto-detect installed models
- [x] Default models: improve-grammar, llama2, mistral, codellama | [x] Fallback to first available
- [x] Model switch preserves history | [x] Show model status (available/unavailable)
- [x] Persist selected model in settings

### API Contract
```python
class OllamaChatWorker(QObject):
    models_detected = Signal(list)  # Available models
    def detect_models(self) -> None:
        """Detect available Ollama models."""
    def set_model(self, model_name: str) -> None:
        """Set active model."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-042: Ollama Chat History

**Category:** AI Features | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** FR-039 | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/ui/chat_panel_widget.py`

### Description
Persistent chat history (100 messages). Save to JSON, load on startup. Clear history button, export history to file.

### Acceptance Criteria
- [x] 100-message limit (FIFO) | [x] Save to JSON file
- [x] Load history on startup | [x] Clear history button
- [x] Export history to .txt file | [x] Timestamp each message
- [x] Separate history per model | [x] History path: ~/.config/AsciiDocArtisan/chat_history.json

### API Contract
```python
class ChatPanelWidget(QWidget):
    def save_history(self) -> None:
        """Save chat history to JSON."""
    def load_history(self) -> None:
        """Load chat history from JSON."""
    def clear_history(self) -> None:
        """Clear all messages."""
    def export_history(self, path: Path) -> None:
        """Export history to text file."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 90%+ | **Types:** Unit (7), Integration (5)

---

## FR-043: Ollama Integration

**Category:** AI Features | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/workers/ollama_chat_worker.py`

### Description
Background worker for Ollama API. Async requests, timeout handling, error recovery. Validate Ollama installation, handle connection errors.

### Acceptance Criteria
- [x] Background worker (QThread) | [x] Async HTTP requests to Ollama API
- [x] 30-second timeout per request | [x] Validate Ollama installed and running
- [x] Connection error handling | [x] Model not found errors
- [x] Retry logic (3 attempts) | [x] Status signals: processing, success, error

### API Contract
```python
class OllamaChatWorker(QObject):
    response_ready = Signal(str)  # AI response
    error_occurred = Signal(str)  # Error message
    processing_started = Signal()
    processing_finished = Signal()

    def send_request(self, prompt: str, model: str, context: str | None = None) -> None:
        """Send request to Ollama API."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 85%+ | **Types:** Unit (9), Integration (4), Error handling (2)

---

## FR-044: Ollama Status Indicator

**Category:** AI Features | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** FR-043 | **Version:** 1.2.0
**Implementation:** `src/asciidoc_artisan/ui/chat_panel_widget.py`

### Description
Status indicator in chat panel: Ollama available/unavailable, processing animation, error states. Color-coded icons.

### Acceptance Criteria
- [x] Status icon: green (ready), yellow (processing), red (error), gray (unavailable)
- [x] Processing animation (spinner) | [x] Tooltip with status details
- [x] Auto-detect on startup | [x] Manual refresh button
- [x] Status text: "Ready", "Processing...", "Error: ...", "Ollama not available"

### API Contract
```python
class ChatPanelWidget(QWidget):
    def update_status(self, status: str, message: str = "") -> None:
        """Update status indicator.

        Args:
            status: One of 'ready', 'processing', 'error', 'unavailable'
            message: Optional detailed status message
        """
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 80%+ | **Types:** Unit (5), Integration (3)

---

## FR-045: Find Bar

**Category:** Find & Replace | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor) | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/ui/find_bar_widget.py`

### Description
VSCode-style find bar at bottom of editor. Case-sensitive, whole word, regex modes. F3/Shift+F3 navigation, Esc to hide. Highlights all matches.

### Acceptance Criteria
- [x] Find bar at bottom of editor | [x] Case-sensitive toggle
- [x] Whole word match toggle | [x] Regex mode toggle
- [x] Highlight all matches (yellow background) | [x] Current match (orange background)
- [x] Match count display (e.g., "3 of 12") | [x] F3 (next), Shift+F3 (previous)
- [x] Ctrl+F to show/focus | [x] Esc to hide | [x] Wrap search

### API Contract
```python
class FindBarWidget(QWidget):
    def __init__(self, parent: QWidget, editor: QPlainTextEdit):
        """Initialize find bar."""
    def show_and_focus(self) -> None:
        """Show bar and focus search input."""
    def find_next(self) -> bool:
        """Find next match."""
    def find_previous(self) -> bool:
        """Find previous match."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 90%+ | **Types:** Unit (9), Integration (6)

---

## FR-046: Replace Functionality

**Category:** Find & Replace | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-045 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/ui/find_bar_widget.py`

### Description
Replace current match or all matches. Confirm before replace-all. Undo support. Ctrl+H shortcut.

### Acceptance Criteria
- [x] Replace input field | [x] Replace button (current match)
- [x] Replace All button | [x] Confirm dialog for replace-all
- [x] Undo support (single undo for replace-all) | [x] Ctrl+H to show replace
- [x] Show replace count (e.g., "12 replacements") | [x] Disable if no matches

### API Contract
```python
class FindBarWidget(QWidget):
    def replace_current(self) -> bool:
        """Replace current match."""
    def replace_all(self) -> int:
        """Replace all matches.

        Returns:
            Number of replacements made
        """
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 90%+ | **Types:** Unit (7), Integration (5)

---

## FR-047: Search Engine

**Category:** Find & Replace | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/core/search_engine.py`

### Description
Core search engine with regex, case-insensitive, whole-word modes. Efficient for large documents (10K+ lines). <50ms for 10K lines.

### Acceptance Criteria
- [x] Plain text search | [x] Case-insensitive search
- [x] Whole word matching | [x] Regex pattern matching
- [x] Find all matches (returns positions) | [x] Performance <50ms for 10K lines
- [x] Handle invalid regex gracefully | [x] Empty pattern returns empty results

### API Contract
```python
class SearchEngine:
    def find_all(
        self,
        text: str,
        pattern: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        regex: bool = False
    ) -> list[tuple[int, int]]:
        """Find all matches.

        Returns:
            List of (start_pos, end_pos) tuples
        """
```

### Test Requirements
**Min Tests:** 20 | **Coverage:** 95%+ | **Types:** Unit (15), Performance (3), Edge cases (2)

---

## FR-048: Find & Replace UI Integration

**Category:** Find & Replace | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-045, FR-046 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/ui/find_bar_widget.py`

### Description
Integrate find/replace with editor. Highlight matches, scroll to current match, preserve cursor position, keyboard navigation.

### Acceptance Criteria
- [x] Highlight matches in editor | [x] Scroll to current match (centered)
- [x] Preserve editor selection after close | [x] Clear highlights on close
- [x] Incremental search (highlight while typing) | [x] Debounce highlighting (100ms)
- [x] Status text: "No matches", "X of Y", "Invalid regex"

### API Contract
```python
class FindBarWidget(QWidget):
    def highlight_matches(self, matches: list[tuple[int, int]]) -> None:
        """Highlight all matches in editor."""
    def scroll_to_match(self, match_index: int) -> None:
        """Scroll editor to show match."""
    def clear_highlights(self) -> None:
        """Remove all match highlights."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-049: Search Performance Optimization

**Category:** Find & Replace | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-047 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/core/search_engine.py`

### Description
Optimize search for large documents. Incremental search, debouncing, background thread for 50K+ lines. Cancel long-running searches.

### Acceptance Criteria
- [x] Debounce search input (100ms) | [x] Incremental search (update as typing)
- [x] Background search for 50K+ lines | [x] Cancel button for long searches
- [x] Performance <50ms for 10K lines | [x] Performance <500ms for 50K lines
- [x] Progress indicator for long searches | [x] Don't block UI during search

### API Contract
```python
class SearchEngine:
    def search_async(
        self,
        text: str,
        pattern: str,
        callback: Callable[[list[tuple[int, int]]], None]
    ) -> None:
        """Async search for large documents."""
    def cancel_search(self) -> None:
        """Cancel ongoing search."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Performance (5)

---

## FR-050: Real-Time Spell Check

**Category:** Spell Check | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-001 (Text Editor) | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/core/spell_checker.py`

### Description
Real-time spell checking with red squiggly underlines. F7 to toggle. Uses pyspellchecker, supports multiple languages. Ignore code blocks and URLs.

### Acceptance Criteria
- [x] Red squiggly underlines for misspelled words | [x] F7 to toggle on/off
- [x] Ignore code blocks, URLs, email addresses | [x] Ignore technical terms (e.g., AsciiDoc, Qt)
- [x] Multi-language support (en, es, fr, de) | [x] Real-time checking as user types
- [x] Debounce checking (200ms) | [x] Show status in status bar

### API Contract
```python
class SpellChecker:
    def __init__(self, language: str = "en"):
        """Initialize spell checker."""
    def check_word(self, word: str) -> bool:
        """Check if word is spelled correctly."""
    def get_suggestions(self, word: str, max_suggestions: int = 5) -> list[str]:
        """Get spelling suggestions."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 90%+ | **Types:** Unit (10), Integration (5)

---

## FR-051: Spell Check Suggestions

**Category:** Spell Check | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-050 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/ui/spell_check_manager.py`

### Description
Right-click context menu shows 5 spelling suggestions. Click to replace. "Add to Dictionary" and "Ignore" options.

### Acceptance Criteria
- [x] Right-click misspelled word shows menu | [x] Show 5 suggestions (max)
- [x] Click suggestion to replace word | [x] "Add to Dictionary" option
- [x] "Ignore" option (session-only) | [x] "Ignore All" option
- [x] Keyboard navigation (arrow keys, Enter)

### API Contract
```python
class SpellCheckManager:
    def show_context_menu(self, word: str, position: QPoint) -> None:
        """Show spell check context menu."""
    def replace_word(self, old_word: str, new_word: str) -> None:
        """Replace misspelled word."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Integration (5)

---

## FR-052: Custom Dictionary

**Category:** Spell Check | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-050 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/core/spell_checker.py`

### Description
Custom dictionary for technical terms, names, project-specific words. Save to JSON, load on startup. Add/remove words via UI.

### Acceptance Criteria
- [x] Add words to custom dictionary | [x] Remove words from dictionary
- [x] Save to JSON: ~/.config/AsciiDocArtisan/custom_dictionary.json | [x] Load on startup
- [x] Per-language dictionaries | [x] Case-sensitive option
- [x] Export/import dictionary | [x] Dictionary editor dialog

### API Contract
```python
class SpellChecker:
    def add_to_dictionary(self, word: str) -> None:
        """Add word to custom dictionary."""
    def remove_from_dictionary(self, word: str) -> None:
        """Remove word from dictionary."""
    def save_dictionary(self) -> None:
        """Save custom dictionary to JSON."""
    def load_dictionary(self) -> None:
        """Load custom dictionary from JSON."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 90%+ | **Types:** Unit (8), Integration (4)

---

## FR-053: Multi-Language Spell Check

**Category:** Spell Check | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** FR-050 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/core/spell_checker.py`

### Description
Support multiple languages: English, Spanish, French, German. Language selector in preferences. Auto-detect language (optional).

### Acceptance Criteria
- [x] Support en, es, fr, de | [x] Language selector in preferences
- [x] Switch language without restart | [x] Auto-detect language (optional)
- [x] Download dictionaries on demand | [x] Show current language in status bar

### API Contract
```python
class SpellChecker:
    def set_language(self, language: str) -> None:
        """Set spell check language.

        Args:
            language: ISO 639-1 code (en, es, fr, de)
        """
    def detect_language(self, text: str) -> str:
        """Auto-detect text language."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 80%+ | **Types:** Unit (6), Integration (4)

---

## FR-054: Spell Check Performance

**Category:** Spell Check | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-050 | **Version:** 1.8.0
**Implementation:** `src/asciidoc_artisan/core/spell_checker.py`

### Description
Optimize spell checking for large documents. Incremental checking, word caching, background thread. <100ms for 1K lines.

### Acceptance Criteria
- [x] Incremental checking (only changed words) | [x] Word cache (LRU, 1000 words)
- [x] Background thread for large docs (10K+ lines) | [x] Performance <100ms for 1K lines
- [x] Performance <500ms for 10K lines | [x] Don't block UI during checking
- [x] Cancel long-running checks | [x] Progress indicator for large docs

### API Contract
```python
class SpellChecker:
    def check_async(
        self,
        text: str,
        callback: Callable[[dict[str, bool]], None]
    ) -> None:
        """Async spell check for large documents."""
    def cancel_check(self) -> None:
        """Cancel ongoing spell check."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Performance (5)

---

## FR-055: Theme Support

**Category:** UI & UX | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/theme_manager.py`

### Description
Light and dark themes for editor and UI. System theme detection, manual override. Theme selector in preferences. Persist theme choice.

### Acceptance Criteria
- [x] Light theme | [x] Dark theme
- [x] System theme detection (auto) | [x] Manual theme override
- [x] Theme selector in preferences | [x] Persist theme in settings
- [x] Apply theme without restart | [x] Syntax highlighting adapts to theme

### API Contract
```python
class ThemeManager:
    def set_theme(self, theme: str) -> None:
        """Set application theme.

        Args:
            theme: One of 'light', 'dark', 'auto'
        """
    def get_current_theme(self) -> str:
        """Get current theme name."""
    def detect_system_theme(self) -> str:
        """Detect system theme (light/dark)."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-056: Status Bar

**Category:** UI & UX | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/status_manager.py`

### Description
Status bar showing: line/col, file size, encoding, Git branch, spell check status. Clickable segments for quick actions.

### Acceptance Criteria
- [x] Line:Col position | [x] File size (KB/MB)
- [x] Encoding (UTF-8) | [x] Git branch (if in repo)
- [x] Spell check status (on/off, language) | [x] Clickable segments
- [x] Update in real-time | [x] Tooltips for segments

### API Contract
```python
class StatusManager:
    def update_position(self, line: int, col: int) -> None:
        """Update cursor position display."""
    def update_file_size(self, size_bytes: int) -> None:
        """Update file size display."""
    def update_git_info(self, branch: str, modified: int) -> None:
        """Update Git status."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Integration (5)

---

## FR-057: Document Metrics

**Category:** UI & UX | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.7.0
**Implementation:** `src/asciidoc_artisan/ui/metrics_dialog.py`

### Description
Document metrics dialog: word count, character count, line count, reading time, paragraph count. Update in real-time or on-demand.

### Acceptance Criteria
- [x] Word count | [x] Character count (with/without spaces)
- [x] Line count | [x] Paragraph count
- [x] Estimated reading time | [x] Selected text metrics
- [x] Real-time updates (debounced 500ms) | [x] Keyboard shortcut (Ctrl+Shift+M)

### API Contract
```python
class MetricsDialog(QDialog):
    def __init__(self, parent: QWidget, editor: QPlainTextEdit):
        """Initialize metrics dialog."""
    def calculate_metrics(self, text: str) -> dict[str, int]:
        """Calculate document metrics."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 85%+ | **Types:** Unit (6), Integration (4)

---

## FR-058: Menu Structure

**Category:** UI & UX | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/menu_manager.py`

### Description
Organized menu structure: File, Edit, View, Git, Tools, Help. Standard shortcuts, recent files, export options.

### Acceptance Criteria
- [x] File menu: New, Open, Save, Save As, Recent Files, Export, Quit
- [x] Edit menu: Undo, Redo, Cut, Copy, Paste, Find, Replace
- [x] View menu: Themes, Zoom, Toggle Preview, Toggle Spell Check
- [x] Git menu: Commit, Pull, Push, Status, GitHub
- [x] Tools menu: Metrics, Preferences, Ollama Chat
- [x] Help menu: Documentation, About
- [x] Standard shortcuts (Ctrl+N, Ctrl+S, etc.)

### API Contract
```python
class MenuManager:
    def create_menus(self) -> None:
        """Create application menus."""
    def update_recent_files(self, files: list[str]) -> None:
        """Update recent files menu."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 80%+ | **Types:** Unit (9), Integration (6)

---

## FR-059: Preferences Dialog

**Category:** UI & UX | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.3.0
**Implementation:** `src/asciidoc_artisan/ui/preferences_dialog.py`

### Description
Preferences dialog with tabs: Editor, Appearance, Git, Spell Check, AI. Save/load preferences from JSON.

### Acceptance Criteria
- [x] Tabbed interface (5 tabs) | [x] Editor: font, tab size, line wrap, auto-save
- [x] Appearance: theme, font size | [x] Git: author name/email
- [x] Spell Check: language, custom dictionary | [x] AI: Ollama model, API key
- [x] Save preferences to JSON | [x] Load on startup
- [x] Apply changes without restart | [x] Reset to defaults button

### API Contract
```python
class PreferencesDialog(QDialog):
    def __init__(self, parent: QWidget, settings: Settings):
        """Initialize preferences dialog."""
    def save_preferences(self) -> None:
        """Save all preferences to settings."""
    def load_preferences(self) -> None:
        """Load preferences from settings."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 85%+ | **Types:** Unit (9), Integration (6)

---

## FR-060: Keyboard Shortcuts

**Category:** UI & UX | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/main_window.py`

### Description
Comprehensive keyboard shortcuts for all actions. Standard shortcuts (Ctrl+S, Ctrl+F) plus custom (F7, F3). Show shortcuts in menus and tooltips.

### Acceptance Criteria
- [x] File: Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save)
- [x] Edit: Ctrl+Z (Undo), Ctrl+Y (Redo), Ctrl+F (Find), Ctrl+H (Replace)
- [x] Git: Ctrl+G (Quick Commit), Ctrl+Shift+G (Git Status)
- [x] View: F7 (Spell Check), F11 (Scroll Sync), Ctrl+Shift+M (Metrics)
- [x] Navigation: F3 (Find Next), Shift+F3 (Find Prev), Ctrl+Return (Ollama)
- [x] Show shortcuts in menus | [x] Tooltips include shortcuts

### API Contract
```python
class MainWindow(QMainWindow):
    def setup_shortcuts(self) -> None:
        """Configure keyboard shortcuts."""
```

### Test Requirements
**Min Tests:** 20 | **Coverage:** 80%+ | **Types:** Unit (12), Integration (8)

---

## FR-061: Accessibility

**Category:** UI & UX | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.9.0
**Implementation:** `src/asciidoc_artisan/ui/main_window.py`

### Description
Accessibility features: keyboard navigation, screen reader support, high contrast mode, focus indicators, ARIA labels.

### Acceptance Criteria
- [x] Full keyboard navigation (Tab, Shift+Tab) | [x] Screen reader labels (accessible names)
- [x] High contrast theme option | [x] Focus indicators (visible outlines)
- [x] ARIA labels for UI elements | [x] Alt text for icons
- [x] Semantic HTML in preview | [x] Minimum contrast ratio 4.5:1

### API Contract
```python
class MainWindow(QMainWindow):
    def setup_accessibility(self) -> None:
        """Configure accessibility features."""
    def set_accessible_names(self) -> None:
        """Set accessible names for widgets."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 75%+ | **Types:** Unit (7), Integration (5)

---

## FR-062: Fast Startup

**Category:** Performance | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/main.py`, `src/asciidoc_artisan/ui/main_window.py`

### Description
Fast application startup (<1s target, 0.586s achieved). Lazy loading, deferred initialization, optimized imports. Measured 0.586s on standard hardware.

### Acceptance Criteria
- [x] Startup time <1 second | [x] Measured: 0.586s achieved
- [x] Lazy load non-critical modules | [x] Deferred worker initialization
- [x] GPU detection cached (24hr) | [x] Optimized import order
- [x] No blocking operations on startup | [x] Splash screen (optional, <100ms)

### API Contract
```python
def main() -> int:
    """Application entry point with optimized startup."""
    # Lazy imports, deferred init, fast path to window show
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 80%+ | **Types:** Unit (4), Performance (4)

---

## FR-063: Worker Pool

**Category:** Performance | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/optimized_worker_pool.py`

### Description
Optimized thread pool for background tasks. Priority queue, task cancellation, dynamic sizing. Prevents UI blocking, efficient resource use.

### Acceptance Criteria
- [x] Priority queue (high/normal/low) | [x] Task cancellation support
- [x] Dynamic thread pool sizing | [x] Thread reuse (no repeated creation)
- [x] Max threads: 8 (configurable) | [x] Task metadata tracking
- [x] Background tasks don't block UI | [x] Graceful shutdown

### API Contract
```python
class OptimizedWorkerPool:
    def submit_task(self, task: Callable, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Submit task to pool.

        Returns:
            Task ID for tracking/cancellation
        """
    def cancel_task(self, task_id: str) -> bool:
        """Cancel pending or running task."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 90%+ | **Types:** Unit (9), Integration (4), Concurrency (2)

---

## FR-064: Async I/O

**Category:** Performance | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/*_worker.py`

### Description
Async file I/O for large documents. Non-blocking reads/writes, progress callbacks. Prevents UI freezing on 10MB+ files.

### Acceptance Criteria
- [x] Async file read (QThread) | [x] Async file write (QThread)
- [x] Progress callbacks (% complete) | [x] Cancellable operations
- [x] Handle 10MB+ files without blocking | [x] Timeout: 60s for large files
- [x] Error handling and recovery

### API Contract
```python
class FileOperationsManager:
    def read_file_async(self, path: Path, callback: Callable[[str], None]) -> None:
        """Read file asynchronously."""
    def write_file_async(self, path: Path, content: str, callback: Callable[[bool], None]) -> None:
        """Write file asynchronously."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Integration (3), Performance (2)

---

## FR-065: Resource Monitoring

**Category:** Performance | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.7.0
**Implementation:** `src/asciidoc_artisan/core/resource_monitor.py`

### Description
Monitor CPU, memory, thread usage. Optional debug panel showing real-time metrics. Helps identify performance bottlenecks.

### Acceptance Criteria
- [x] Monitor CPU usage | [x] Monitor memory usage (MB)
- [x] Monitor thread count | [x] Monitor worker pool queue size
- [x] Debug panel (toggle with F12) | [x] Update interval: 1 second
- [x] Log warnings if memory >500MB | [x] Export metrics to CSV

### API Contract
```python
class ResourceMonitor:
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
    def get_memory_usage(self) -> int:
        """Get memory usage in MB."""
    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 80%+ | **Types:** Unit (6), Integration (4)

---

## FR-066: Memory Optimization

**Category:** Performance | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.5.0
**Implementation:** Multiple files

### Description
Memory optimizations: object pooling, weak references, cache limits. Target <200MB for typical documents, <500MB for large docs.

### Acceptance Criteria
- [x] Memory <200MB for typical docs (<1MB) | [x] Memory <500MB for large docs (10MB+)
- [x] LRU caches with size limits | [x] Weak references for non-critical data
- [x] Object pooling for frequently created objects | [x] Explicit cleanup on file close
- [x] No memory leaks (tested with 100 open/close cycles)

### API Contract
```python
# Cache size limits enforced across codebase
BLOCK_CACHE_MAX_SIZE = 100  # blocks
GPU_CACHE_TTL = 24 * 3600   # 24 hours
WORD_CACHE_MAX_SIZE = 1000  # words
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 80%+ | **Types:** Unit (7), Performance (5)

---

## FR-067: Cache Strategy

**Category:** Performance | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/incremental_renderer.py`

### Description
Multi-level caching: block cache (LRU 100 blocks), GPU detection (24hr), spell check words (LRU 1K). MD5 hashing for invalidation.

### Acceptance Criteria
- [x] Block cache: LRU, 100 blocks max | [x] GPU detection cache: 24 hours
- [x] Spell check word cache: LRU, 1000 words | [x] MD5 hashing for cache keys
- [x] Cache hit rate >80% for typical editing | [x] Cache invalidation on content change
- [x] Cache persistence optional

### API Contract
```python
class BlockCache:
    def __init__(self, max_size: int = 100):
        """Initialize LRU cache."""
    def get(self, key: str) -> str | None:
        """Get cached value."""
    def put(self, key: str, value: str) -> None:
        """Store value in cache."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 90%+ | **Types:** Unit (10), Performance (5)

---

## FR-067a: Incremental Rendering

**Category:** Performance | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** FR-018, FR-067 | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/incremental_renderer.py`

### Description
Incremental preview rendering using block-based cache. Only re-render changed blocks. 10-50x speedup for large docs with small edits.

### Acceptance Criteria
- [x] Block-based document splitting | [x] MD5 hashing for change detection
- [x] Re-render only changed blocks | [x] LRU cache (100 blocks)
- [x] 10-50x speedup for incremental edits | [x] Fallback to full render if >50% changed
- [x] Performance <100ms for incremental render

### API Contract
```python
class IncrementalPreviewRenderer:
    def render_incremental(self, content: str, previous_content: str | None = None) -> str:
        """Render only changed blocks."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 90%+ | **Types:** Unit (10), Performance (5)

---

## FR-067b: Predictive Rendering

**Category:** Performance | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** FR-018 | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/predictive_renderer.py`

### Description
Predict which blocks user will edit next based on cursor position and scroll. Pre-render predicted blocks in background.

### Acceptance Criteria
- [x] Track cursor position and scroll | [x] Predict next 3 blocks to edit
- [x] Pre-render predicted blocks in background | [x] Cache pre-rendered blocks
- [x] Fallback to on-demand if prediction wrong | [x] Don't block UI for predictions
- [x] Improve perceived performance for sequential editing

### API Contract
```python
class PredictiveRenderer:
    def predict_next_blocks(self, cursor_position: int, scroll_position: int) -> list[str]:
        """Predict next blocks to render."""
    def prerender_blocks(self, block_ids: list[str]) -> None:
        """Pre-render blocks in background."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 80%+ | **Types:** Unit (6), Integration (4)

---

## FR-067c: Render Prioritization

**Category:** Performance | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-063 | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/workers/optimized_worker_pool.py`

### Description
Prioritize render tasks: user edits (high), scroll (normal), background (low). Ensure responsive UI during heavy load.

### Acceptance Criteria
- [x] 3 priority levels: high, normal, low | [x] User edit triggers: high priority
- [x] Scroll triggers: normal priority | [x] Background/predictive: low priority
- [x] High priority tasks preempt low priority | [x] UI remains responsive <100ms
- [x] Queue visualization in debug panel

### API Contract
```python
class TaskPriority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3

class OptimizedWorkerPool:
    def submit_task(self, task: Callable, priority: TaskPriority) -> str:
        """Submit prioritized task."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Integration (3), Performance (2)

---

## FR-068: Path Sanitization

**Category:** Security | **Priority:** Critical | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/core/security.py`

### Description
Sanitize file paths to prevent directory traversal attacks. Validate paths before file operations. Reject paths with "..", absolute paths outside allowed dirs.

### Acceptance Criteria
- [x] Reject "../" directory traversal | [x] Reject absolute paths outside project
- [x] Normalize paths (resolve symlinks) | [x] Validate before all file operations
- [x] Whitelist allowed directories | [x] Log rejected paths
- [x] Raise SecurityError for violations

### API Contract
```python
def sanitize_path(path: str | Path, base_dir: Path) -> Path:
    """Sanitize and validate file path.

    Args:
        path: User-provided path
        base_dir: Base directory (must stay within)

    Returns:
        Sanitized absolute path

    Raises:
        SecurityError: If path escapes base_dir
    """
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 100%+ | **Types:** Unit (10), Security (5)

---

## FR-073: Telemetry

**Category:** Analytics | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.7.0
**Implementation:** `src/asciidoc_artisan/core/telemetry.py`

### Description
Optional anonymous usage telemetry. Track feature usage, performance metrics, errors. Opt-in only, full transparency. Helps improve UX.

### Acceptance Criteria
- [x] Opt-in only (disabled by default) | [x] Anonymous (no PII)
- [x] Track: feature usage, performance, errors | [x] Full transparency (show collected data)
- [x] Export telemetry to JSON | [x] Settings toggle
- [x] Local storage only (no remote upload) | [x] Respect user privacy

### API Contract
```python
class Telemetry:
    def track_event(self, event: str, metadata: dict[str, Any] | None = None) -> None:
        """Track usage event."""
    def track_performance(self, operation: str, duration_ms: float) -> None:
        """Track performance metric."""
    def export_data(self, path: Path) -> None:
        """Export telemetry data to JSON."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 80%+ | **Types:** Unit (6), Integration (4)

---

## FR-074: Settings Persistence

**Category:** Core | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/core/settings.py`

### Description
Persist user settings to JSON. Load on startup, save on change. Settings: theme, font, Git config, spell check, preferences.

### Acceptance Criteria
- [x] Save to JSON: ~/.config/AsciiDocArtisan/settings.json | [x] Load on startup
- [x] Save on setting change (debounced 500ms) | [x] Settings: theme, font, Git, spell, AI
- [x] Atomic writes (temp + rename) | [x] Schema validation
- [x] Migration on version change | [x] Reset to defaults option

### API Contract
```python
class Settings:
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value."""
    def set(self, key: str, value: Any) -> None:
        """Set setting value."""
    def save(self) -> None:
        """Save settings to disk."""
    def load(self) -> None:
        """Load settings from disk."""
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
```

### Test Requirements
**Min Tests:** 15 | **Coverage:** 95%+ | **Types:** Unit (10), Integration (5)

---

## FR-077: User Documentation

**Category:** Documentation | **Priority:** High | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `docs/`, `README.md`

### Description
Comprehensive user documentation: installation, features, keyboard shortcuts, troubleshooting. Grade 5.0 readability (Flesch-Kincaid).

### Acceptance Criteria
- [x] Installation guide | [x] Feature documentation
- [x] Keyboard shortcuts reference | [x] Troubleshooting guide
- [x] Screenshots for key features | [x] Grade 5.0 readability
- [x] Markdown format | [x] Searchable

### Test Requirements
**Min Tests:** 5 | **Coverage:** N/A | **Types:** Readability (5)

---

## FR-078: Inline Help

**Category:** Documentation | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.3.0
**Implementation:** `src/asciidoc_artisan/ui/help_panel.py`

### Description
Inline help panel showing context-sensitive tips. Keyboard shortcut: F1. Help topics: AsciiDoc syntax, Git, features.

### Acceptance Criteria
- [x] F1 shows help panel | [x] Context-sensitive help topics
- [x] Search help topics | [x] Quick reference cards
- [x] AsciiDoc syntax examples | [x] Git workflow help
- [x] Keyboard shortcuts | [x] Close with Esc

### API Contract
```python
class HelpPanel(QDockWidget):
    def show_topic(self, topic: str) -> None:
        """Show specific help topic."""
    def search(self, query: str) -> list[str]:
        """Search help topics."""
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 80%+ | **Types:** Unit (6), Integration (4)

---

## FR-079: Tooltips

**Category:** UI & UX | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** UI widgets

### Description
Comprehensive tooltips for all UI elements. Show on hover (500ms delay). Include keyboard shortcuts where applicable.

### Acceptance Criteria
- [x] Tooltips for all buttons | [x] Tooltips for all menu items
- [x] Tooltips for status bar segments | [x] Include keyboard shortcuts
- [x] 500ms hover delay | [x] Clear, concise text
- [x] Consistent formatting

### Test Requirements
**Min Tests:** 5 | **Coverage:** N/A | **Types:** Manual (5)

---

## FR-080: Keyboard Shortcuts Reference

**Category:** Documentation | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-060 | **Version:** 1.0.0
**Implementation:** `docs/KEYBOARD_SHORTCUTS.md`

### Description
Quick reference card for all keyboard shortcuts. Accessible via Help → Keyboard Shortcuts. Printable format.

### Acceptance Criteria
- [x] List all shortcuts (50+) | [x] Organized by category
- [x] Help menu item | [x] Dialog with searchable table
- [x] Printable format (HTML export) | [x] Show in tooltips
- [x] Customizable shortcuts (future)

### API Contract
```python
class ShortcutsDialog(QDialog):
    def show_shortcuts(self, category: str | None = None) -> None:
        """Show keyboard shortcuts dialog."""
```

### Test Requirements
**Min Tests:** 8 | **Coverage:** 80%+ | **Types:** Unit (5), Integration (3)

---

## FR-081: About Dialog

**Category:** UI & UX | **Priority:** Low | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.0.0
**Implementation:** `src/asciidoc_artisan/ui/about_dialog.py`

### Description
About dialog showing version, authors, license, dependencies. Help → About.

### Acceptance Criteria
- [x] Application version | [x] Authors and contributors
- [x] License (MIT) | [x] Dependencies list
- [x] GitHub link | [x] Help → About menu item
- [x] Close with Esc | [x] Check for updates button

### API Contract
```python
class AboutDialog(QDialog):
    def __init__(self, parent: QWidget):
        """Initialize about dialog."""
```

### Test Requirements
**Min Tests:** 5 | **Coverage:** 75%+ | **Types:** Unit (3), Integration (2)

---

## FR-082: Auto-Update

**Category:** Updates | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.7.0
**Implementation:** `src/asciidoc_artisan/core/updater.py`

### Description
Check for updates on startup (opt-in). Notify user of new versions. Link to GitHub releases.

### Acceptance Criteria
- [x] Check for updates on startup (opt-in) | [x] Query GitHub API (releases)
- [x] Notify if newer version available | [x] Link to release notes
- [x] Manual check: Help → Check for Updates | [x] Respect privacy (anonymous check)
- [x] 5-second timeout | [x] Cache check result (24hr)

### API Contract
```python
class Updater:
    def check_for_updates(self) -> tuple[bool, str]:
        """Check for updates.

        Returns:
            (update_available, latest_version)
        """
```

### Test Requirements
**Min Tests:** 10 | **Coverage:** 80%+ | **Types:** Unit (6), Integration (4)

---

## FR-083: Backup System

**Category:** Data Safety | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** None | **Version:** 1.7.0
**Implementation:** `src/asciidoc_artisan/core/backup.py`

### Description
Auto-backup on save (optional). Keep last 10 backups. Backup location: ~/.local/share/AsciiDocArtisan/backups/.

### Acceptance Criteria
- [x] Auto-backup on save (opt-in) | [x] Keep last 10 backups (FIFO)
- [x] Backup location: ~/.local/share/AsciiDocArtisan/backups/ | [x] Filename: {original}_backup_{timestamp}.adoc
- [x] Restore from backup dialog | [x] Manual backup: File → Create Backup
- [x] Clean old backups (>10) | [x] Atomic copy

### API Contract
```python
class BackupManager:
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file."""
    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """Restore from backup."""
    def list_backups(self, file_path: Path) -> list[Path]:
        """List available backups."""
```

### Test Requirements
**Min Tests:** 12 | **Coverage:** 85%+ | **Types:** Unit (7), Integration (5)

---

## FR-084: LRU Cache

**Category:** Performance | **Priority:** Medium | **Status:** ✅ Implemented
**Dependencies:** FR-067 | **Version:** 1.5.0
**Implementation:** `src/asciidoc_artisan/core/lru_cache.py`

### Description
Generic LRU cache implementation. Used for block cache, word cache, GPU detection. Configurable size, TTL support.

### Acceptance Criteria
- [x] Generic LRU implementation | [x] Configurable max size
- [x] Optional TTL (time-to-live) | [x] Thread-safe
- [x] Get/put/remove/clear operations | [x] Hit rate tracking
- [x] Evict oldest on overflow | [x] O(1) get/put performance

### API Contract
```python
class LRUCache:
    def __init__(self, max_size: int, ttl: int | None = None):
        """Initialize LRU cache.

        Args:
            max_size: Maximum cache entries
            ttl: Time-to-live in seconds (None = no expiry)
        """
    def get(self, key: str) -> Any | None:
        """Get value from cache."""
    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
    def get_hit_rate(self) -> float:
        """Get cache hit rate (0.0-1.0)."""
```

### Test Requirements
**Min Tests:** 20 | **Coverage:** 95%+ | **Types:** Unit (15), Performance (5)

---

## FR-085: Auto-Complete Engine

**Category:** Auto-Complete | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/autocomplete_engine.py`

Context-aware auto-complete for AsciiDoc syntax. Ctrl+Space trigger, fuzzy matching, <50ms for 1K items. Suggests headings, attributes, cross-refs.

**Acceptance:** Context-aware suggestions | Fuzzy matching | <50ms latency | 1K+ completion items
**API:** `class AutoCompleteEngine: def get_completions(context: str) -> list[Completion]`
**Tests:** 15 tests, 90%+ coverage

### Test Requirements

- **Minimum Tests:** 15
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Context detection (5 tests)
  - Unit: Provider registration (4 tests)
  - Integration: Editor integration (4 tests)
  - Performance: <50ms for 1K completions (2 tests)

---

## FR-086: Completion Popup

**Category:** Auto-Complete | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/ui/autocomplete_widget.py`

Popup widget showing completion suggestions. Arrow keys navigate, Enter accepts, Esc cancels. Shows 10 items max.

**Acceptance:** Popup on Ctrl+Space | Arrow navigation | Enter accepts | Max 10 items | Icon + description
**API:** `class CompletionPopup(QListWidget): def show_completions(items: list[Completion])`
**Tests:** 12 tests, 85%+ coverage

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Show/hide popup (4 tests)
  - Unit: Item navigation (4 tests)
  - Integration: Editor integration (2 tests)
  - UI: Arrow keys, Enter, Esc (2 tests)

---

## FR-087: Syntax-Aware Completions

**Category:** Auto-Complete | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/autocomplete_providers.py`

AsciiDoc syntax completions: headings (=), lists (*), attributes (:), cross-refs (<<>>), blocks (----).

**Acceptance:** Heading levels | List types | Attributes | Cross-refs | Code blocks | Tables
**API:** `def get_syntax_completions(position: int, text: str) -> list[Completion]`
**Tests:** 20 tests, 90%+ coverage

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Completion types (5 tests)
  - Unit: Context detection (3 tests)
  - Integration: Engine integration (2 tests)

---

## FR-088: Fuzzy Matching

**Category:** Auto-Complete | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/autocomplete_engine.py::fuzzy_match()`

Fuzzy string matching for completions. Ranks by relevance. Supports abbreviations (e.g., "hdr" matches "header").

**Acceptance:** Fuzzy match algorithm | Relevance ranking | Abbreviation support | <10ms for 1K items
**API:** `def fuzzy_match(query: str, candidates: list[str]) -> list[tuple[str, float]]`
**Tests:** 15 tests, 95%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Match algorithm (4 tests)
  - Unit: Scoring logic (2 tests)
  - Performance: <10ms for 1K items (2 tests)

---

## FR-089: Completion Cache

**Category:** Auto-Complete | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/autocomplete_engine.py`

Cache completion items. Invalidate on document change. LRU cache, 1K items max.

**Acceptance:** LRU cache | 1K items | Invalidate on change | Hit rate >80%
**API:** `class CompletionCache(LRUCache): def get_completions_cached(context: str)`
**Tests:** 10 tests, 85%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Cache hit/miss (3 tests)
  - Unit: Cache invalidation (3 tests)
  - Performance: Cache benefit verification (2 tests)

---

## FR-090: Custom Completions

**Category:** Auto-Complete | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/autocomplete_providers.py`

User-defined completion snippets. Load from JSON. Supports placeholders ${1}, ${2}.

**Acceptance:** Load from JSON | Placeholders | Tab navigation | Save custom snippets
**API:** `class CustomCompletions: def add_snippet(trigger: str, template: str)`
**Tests:** 10 tests, 80%+ coverage

### Test Requirements

- **Minimum Tests:** 6
- **Coverage Target:** 80%+
- **Test Types:**
  - Unit: Provider registration (3 tests)
  - Unit: Priority handling (2 tests)
  - Integration: Engine integration (1 test)

---

## FR-091: Real-Time Syntax Checking

**Category:** Syntax Checking | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/syntax_checker.py`

Real-time AsciiDoc syntax validation. Highlights errors inline. <100ms for 1K lines. F8 to navigate errors.

**Acceptance:** Real-time validation | Inline highlights | <100ms latency | Error list panel | F8 navigation
**API:** `class SyntaxChecker: def check_syntax(text: str) -> list[SyntaxError]`
**Tests:** 20 tests, 95%+ coverage

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Validation logic (5 tests)
  - Unit: Error detection (3 tests)
  - Integration: Editor integration (2 tests)
  - Performance: <100ms for 1K lines (2 tests)

---

## FR-092: Error Highlighting

**Category:** Syntax Checking | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/ui/syntax_checker_manager.py`

Color-coded error highlights: red (errors), yellow (warnings), blue (info). Squiggly underlines in editor.

**Acceptance:** 3 severity levels | Color-coded | Squiggly underlines | Tooltips with error details
**API:** `class ErrorHighlighter: def highlight_errors(errors: list[SyntaxError])`
**Tests:** 12 tests, 90%+ coverage

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Highlight logic (4 tests)
  - Unit: Error colors (3 tests)
  - Integration: Editor integration (2 tests)
  - UI: Visual indicators (1 test)

---

## FR-093: Error Navigation

**Category:** Syntax Checking | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/ui/syntax_checker_manager.py`

Navigate errors with F8 (next), Shift+F8 (previous). Jump to error location, show error message.

**Acceptance:** F8 next error | Shift+F8 previous | Jump to location | Show message | Wrap around
**API:** `def next_error() -> SyntaxError | None`
**Tests:** 10 tests, 85%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Navigation logic (3 tests)
  - Unit: Error position tracking (2 tests)
  - Integration: Editor integration (2 tests)
  - UI: F8 key handling (1 test)

---

## FR-094: Error Panel

**Category:** Syntax Checking | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/ui/syntax_checker_manager.py`

Error list panel (bottom). Shows all errors with line numbers. Click to jump. Filter by severity.

**Acceptance:** List all errors | Line numbers | Click to jump | Filter by severity | Refresh button
**API:** `class ErrorPanel(QDockWidget): def update_errors(errors: list[SyntaxError])`
**Tests:** 10 tests, 80%+ coverage

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Error list management (4 tests)
  - Unit: Panel show/hide (2 tests)
  - Integration: Checker integration (2 tests)
  - UI: Click navigation (2 tests)

---

## FR-095: Syntax Rules

**Category:** Syntax Checking | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/syntax_validators.py`

AsciiDoc syntax validation rules: heading structure, attribute syntax, cross-ref validity, block delimiters, list consistency.

**Acceptance:** 20+ validation rules | Heading hierarchy | Attributes | Cross-refs | Blocks | Lists
**API:** `class ValidationRule: def validate(text: str) -> list[SyntaxError]`
**Tests:** 25 tests, 95%+ coverage

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Rule definitions (6 tests)
  - Unit: Validation logic (4 tests)
  - Integration: Checker integration (2 tests)

---

## FR-096: Quick Fixes

**Category:** Syntax Checking | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/syntax_checker.py`

Suggest quick fixes for common errors. Click lightbulb icon or Ctrl+. to apply fix.

**Acceptance:** 10+ quick fix types | Lightbulb icon | Ctrl+. shortcut | Apply fix | Undo support
**API:** `class QuickFix: def get_fixes(error: SyntaxError) -> list[Fix]`
**Tests:** 15 tests, 85%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 80%+
- **Test Types:**
  - Unit: Fix suggestions (4 tests)
  - Unit: Fix application (2 tests)
  - Integration: Editor integration (1 test)
  - UI: Context menu (1 test)

---

## FR-097: Configurable Rules

**Category:** Syntax Checking | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/syntax_checker.py`

Enable/disable validation rules. Configure rule severity. Save preferences.

**Acceptance:** Enable/disable rules | Configure severity | Preferences UI | Save to settings
**API:** `class RuleConfig: def set_rule_enabled(rule: str, enabled: bool)`
**Tests:** 8 tests, 80%+ coverage

### Test Requirements

- **Minimum Tests:** 6
- **Coverage Target:** 80%+
- **Test Types:**
  - Unit: Rule enable/disable (3 tests)
  - Unit: Severity configuration (2 tests)
  - Integration: Settings persistence (1 test)

---

## FR-098: Performance Optimization

**Category:** Syntax Checking | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/syntax_checker.py`

Optimize syntax checking: incremental validation, debouncing (200ms), background thread, cancel on type.

**Acceptance:** Incremental validation | 200ms debounce | Background thread | <100ms for 1K lines
**API:** `def check_incremental(changes: list[Change]) -> list[SyntaxError]`
**Tests:** 12 tests, 90%+ coverage

### Test Requirements

- **Minimum Tests:** 5
- **Coverage Target:** 85%+
- **Test Types:**
  - Performance: Batch validation (2 tests)
  - Performance: Incremental checking (2 tests)
  - Performance: Large document handling (1 test)

---

## FR-099: Error Recovery

**Category:** Syntax Checking | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/syntax_checker.py`

Graceful error recovery. Continue validation after error. Don't block on parse failures.

**Acceptance:** Continue after errors | Don't block | Partial validation | Error boundaries
**API:** `def validate_with_recovery(text: str) -> ValidationResult`
**Tests:** 10 tests, 85%+ coverage

### Test Requirements

- **Minimum Tests:** 6
- **Coverage Target:** 80%+
- **Test Types:**
  - Unit: Error recovery logic (3 tests)
  - Unit: Partial validation (2 tests)
  - Integration: Checker integration (1 test)

---

## FR-100: Template System

**Category:** Templates | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_manager.py`

Document templates: Article, Book, Report, Resume, Presentation, Letter. New Document → From Template.

**Acceptance:** 6 built-in templates | Template selector dialog | Variables | Preview | Custom templates
**API:** `class TemplateManager: def create_from_template(name: str, vars: dict) -> str`
**Tests:** 15 tests, 90%+ coverage

### Test Requirements

- **Minimum Tests:** 15
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Template load/save (5 tests)
  - Unit: Template management (4 tests)
  - Integration: Manager integration (3 tests)
  - File I/O: Template file operations (3 tests)

---

## FR-101: Template Variables

**Category:** Templates | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_engine.py`

Template variables with Handlebars syntax: {{title}}, {{author}}, {{date}}. Input dialog on template selection.

**Acceptance:** Handlebars syntax | Variable input dialog | Default values | Validation
**API:** `def substitute_variables(template: str, vars: dict[str, str]) -> str`
**Tests:** 12 tests, 90%+ coverage

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Variable substitution (5 tests)
  - Unit: Handlebars parsing (3 tests)
  - Integration: Engine integration (2 tests)

---

## FR-102: Custom Templates

**Category:** Templates | **Priority:** Medium | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_manager.py`

User-defined templates. Save current document as template. Load from ~/.local/share/AsciiDocArtisan/templates/.

**Acceptance:** Save as template | Load custom templates | Template metadata | Edit templates
**API:** `def save_as_template(name: str, content: str, metadata: dict)`
**Tests:** 10 tests, 85%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Add/remove templates (3 tests)
  - Unit: Template validation (2 tests)
  - Integration: Manager integration (2 tests)
  - File I/O: Custom template storage (1 test)

---

## FR-103: Template Preview

**Category:** Templates | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/ui/template_browser.py`

Preview template before applying. Show rendered output in dialog. Edit variables before apply.

**Acceptance:** Preview dialog | Rendered output | Edit variables | Apply/Cancel
**API:** `class TemplatePreview(QDialog): def show_preview(template: str)`
**Tests:** 8 tests, 80%+ coverage

### Test Requirements

- **Minimum Tests:** 10
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Preview rendering (4 tests)
  - Unit: Preview updates (2 tests)
  - Integration: Browser integration (2 tests)
  - UI: Preview pane display (2 tests)

---

## FR-104: Template Metadata

**Category:** Templates | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_manager.py`

Template metadata: name, description, author, category, tags. Display in template selector.

**Acceptance:** Metadata fields | JSON format | Display in selector | Search/filter
**API:** `class TemplateMetadata: name: str; description: str; author: str; tags: list[str]`
**Tests:** 8 tests, 80%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 85%+
- **Test Types:**
  - Unit: Metadata read/write (4 tests)
  - Unit: Metadata validation (2 tests)
  - Integration: Manager integration (2 tests)

---

## FR-105: Template Categories

**Category:** Templates | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_manager.py`

Organize templates by category: Document, Academic, Business, Personal, Technical, Other.

**Acceptance:** 6 categories | Category filter | Sort by category | Custom categories
**API:** `enum TemplateCategory: DOCUMENT, ACADEMIC, BUSINESS, PERSONAL, TECHNICAL, OTHER`
**Tests:** 6 tests, 75%+ coverage

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 80%+
- **Test Types:**
  - Unit: Category logic (3 tests)
  - Unit: Category filtering (2 tests)
  - Integration: Browser integration (2 tests)
  - UI: Category filters (1 test)

---

## FR-106: Template Sharing

**Category:** Templates | **Priority:** Low | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_manager.py`

Export templates to .zip. Import templates from .zip. Share templates with others.

**Acceptance:** Export to ZIP | Import from ZIP | Include metadata | Validation
**API:** `def export_template(name: str, path: Path) -> bool`
**Tests:** 10 tests, 80%+ coverage

### Test Requirements

- **Minimum Tests:** 6
- **Coverage Target:** 75%+
- **Test Types:**
  - Unit: Export/import logic (2 tests)
  - Unit: Template validation (2 tests)
  - Integration: Manager integration (1 test)
  - File I/O: Template file operations (1 test)

---

## FR-107: Template Engine

**Category:** Templates | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.0
**Implementation:** `src/asciidoc_artisan/core/template_engine.py`

Template rendering engine. Handlebars syntax, conditionals, loops. <200ms for typical template.

**Acceptance:** Handlebars syntax | Conditionals {{#if}} | Loops {{#each}} | Helpers | <200ms render
**API:** `class TemplateEngine: def render(template: str, context: dict) -> str`
**Tests:** 20 tests, 95%+ coverage

### Test Requirements

- **Minimum Tests:** 12
- **Coverage Target:** 90%+
- **Test Types:**
  - Unit: Template rendering (5 tests)
  - Unit: Variable processing (3 tests)
  - Integration: Template integration (2 tests)
  - Performance: <200ms template load (2 tests)

---

## FR-108: MA (間) Principle

**Category:** Development Standards | **Priority:** High | **Status:** 📋 Planned | **Version:** 2.0.8
**Implementation:** `docs/developer/ma-principle.md`, `scripts/analyze_ma_violations.py`

Japanese aesthetic principle of negative space applied to code and documentation. Remove unnecessary complexity, embrace intentional whitespace, achieve minimal sufficiency.

**Acceptance:** ≤10 cyclomatic complexity | ≤15% comment ratio | ≥2% whitespace ratio | ≤50 lines/function | ≤4 params
**Metrics:** Function length, complexity, nesting depth, comment ratio, whitespace, parameter count
**Tests:** Automated linting rules, manual code review checklist

### Description

MA (間, pronounced "ma") is the Japanese concept of negative space—the intentional void that gives meaning to what surrounds it. In software development, MA translates to:

- **Less is more**: Remove unnecessary complexity, comments, and features
- **Intentional gaps**: Use whitespace purposefully to separate logical sections
- **Minimal sufficiency**: Implement only what's needed, nothing more
- **Graceful silence**: Don't over-communicate through excessive logging or comments
- **Focused simplicity**: One purpose per function/class, done well

### Acceptance Criteria

**Code Quality:**
- [ ] No function exceeds 50 lines (excluding docstrings)
- [ ] No function exceeds cyclomatic complexity of 10
- [ ] No function has more than 4 parameters
- [ ] No nesting deeper than 3 levels
- [ ] Comment ratio ≤15% (excluding docstrings)
- [ ] Whitespace ratio ≥2% (blank lines between logical sections)

**Documentation:**
- [ ] Comments explain "why", not "what"
- [ ] No redundant docstrings that restate function signatures
- [ ] README uses whitespace to separate sections
- [ ] Maximum 88 characters per line
- [ ] Grade 5.0 or lower (Flesch-Kincaid readability)

**UI/UX:**
- [ ] Maximum 5 colors in UI theme
- [ ] Maximum 2 font families
- [ ] Maximum 7±2 interactive elements per view
- [ ] Whitespace ratio ≥30% of screen area
- [ ] Maximum 3-level menu hierarchy

### Metrics and Thresholds

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
  max_comment_ratio: 0.15      # Code comments
  min_whitespace_ratio: 0.02   # Blank lines in docs
  max_line_length: 88          # Characters per line
  max_reading_grade: 5.0       # Flesch-Kincaid grade level

ui:
  max_colors: 5                # UI color palette
  max_fonts: 2                 # Font families
  max_interactive_elements: 7  # Per view (Miller's Law)
  min_whitespace_ratio: 0.30   # Screen area
```

### Test Requirements

- **Minimum Tests:** 8
- **Coverage Target:** 100% (automated checks)
- **Test Types:**
  - Lint: Function length checks (1 test)
  - Lint: Complexity checks (1 test)
  - Lint: Comment ratio checks (1 test)
  - Lint: Whitespace ratio checks (1 test)
  - Integration: Full codebase scan (1 test)
  - Integration: Documentation scan (1 test)
  - Manual: Code review checklist (1 verification)
  - Manual: UI review checklist (1 verification)

### Implementation Guidance

**Phase 1: Documentation (Week 1)**
1. Create `docs/developer/ma-principle.md` ✅ (completed)
2. Add MA principle to SPECIFICATIONS_AI.md (this FR)
3. Create verification checklist
4. Document MA patterns and anti-patterns

**Phase 2: Automation (Week 2)**
1. Create `scripts/analyze_ma_violations.py`
   - Scan Python files for violations
   - Generate violation report with file:line references
   - Exit code 1 if violations exceed threshold
2. Add pre-commit hook for MA checks
3. Integrate with CI/CD pipeline

**Phase 3: Remediation (Weeks 3-4)**
1. Run analysis on entire codebase
2. Prioritize violations (P0: >100 lines, P1: >50 lines, P2: complexity >10)
3. Refactor high-priority violations
4. Update tests to maintain coverage
5. Document patterns used in refactoring

**Code Pattern Example:**

```python
# ✅ Good MA - Breathing room, focused, minimal
def process_document(content: str) -> str:
    """Process document content."""
    # Validate input
    if not content:
        return ""

    # Parse content
    blocks = parse_blocks(content)

    # Transform blocks
    transformed = [transform(block) for block in blocks]

    # Return result
    return join_blocks(transformed)

# ❌ Bad MA - Cramped, no whitespace, poor separation
def process_document(content: str) -> str:
    """Process document content."""
    if not content:
        return ""
    blocks = parse_blocks(content)
    transformed = [transform(block) for block in blocks]
    return join_blocks(transformed)
```

**Security Considerations:**
- MA principle reduces attack surface by removing unnecessary code
- Fewer lines = fewer bugs = fewer vulnerabilities
- Clear, simple code is easier to audit for security issues

**Performance:**
- Simpler code often performs better (fewer branches, better CPU cache utilization)
- Reduced complexity improves JIT optimization opportunities
- MA-compliant code typically has lower memory footprint

### Verification Steps

**Automated Checks:**
```bash
# Run MA violation analysis
python3 scripts/analyze_ma_violations.py

# Expected output: List of violations with priorities
# Exit code 0 if all checks pass, 1 if violations found

# Run pre-commit hook
pre-commit run ma-principle-check --all-files
```

**Manual Review:**
1. Open random Python file from `src/asciidoc_artisan/`
2. Verify no function >50 lines (excluding docstrings)
3. Verify whitespace between logical sections
4. Verify comments explain "why", not "what"
5. Check cyclomatic complexity: `radon cc <file> -s`
6. Review UI for visual breathing room

**Success Criteria:**
- 95%+ of functions comply with MA metrics
- Zero P0 violations (>100 lines or complexity >15)
- <5 P1 violations (<50 lines or complexity >10)
- Documentation passes Grade 5.0 readability
- UI maintains 30%+ whitespace ratio

### Dependencies

This FR affects and is complemented by:
- **All FRs**: MA principle applies to all feature implementations
- **FR-001 to FR-107**: Existing features should be reviewed for MA compliance
- **SOLID principles**: MA complements Single Responsibility (SRP)
- **YAGNI**: "You Aren't Gonna Need It" aligns with MA's minimal sufficiency
- **KISS**: "Keep It Simple, Stupid" shares MA's simplicity focus

### Examples

**Example 1: Function Length Violation**
```python
# ❌ Before (78 lines, violates MA)
def handle_git_commit(...):
    # 78 lines of logic

# ✅ After (split into focused functions)
def handle_git_commit(...):
    validated = _validate_commit_inputs(...)
    staged = _stage_files(...)
    return _execute_commit(staged)

def _validate_commit_inputs(...): ...  # 15 lines
def _stage_files(...): ...              # 12 lines
def _execute_commit(...): ...           # 18 lines
```

**Example 2: Complexity Violation**
```python
# ❌ Before (cyclomatic complexity 12)
def process_file(path):
    if path.exists():
        if path.is_file():
            if path.suffix == ".adoc":
                if path.stat().st_size > 0:
                    # nested processing...

# ✅ After (complexity 4, early returns)
def process_file(path):
    if not path.exists():
        return None
    if not path.is_file():
        return None
    if path.suffix != ".adoc":
        return None
    if path.stat().st_size == 0:
        return None

    return _process_asciidoc(path)
```

**Example 3: Whitespace Ratio**
```python
# ❌ Before (0% whitespace ratio - cramped)
def calculate_metrics(data):
    total = sum(data)
    avg = total / len(data)
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    std_dev = variance ** 0.5
    return {"total": total, "avg": avg, "std_dev": std_dev}

# ✅ After (8% whitespace ratio - breathing room)
def calculate_metrics(data):
    # Calculate basic stats
    total = sum(data)
    avg = total / len(data)

    # Calculate variance
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    std_dev = variance ** 0.5

    # Return results
    return {"total": total, "avg": avg, "std_dev": std_dev}
```

### Related Principles

**MA complements existing principles:**
- **SOLID**: MA reinforces Single Responsibility (one purpose per function)
- **YAGNI**: MA's minimal sufficiency = "You Aren't Gonna Need It"
- **KISS**: MA's simplicity = "Keep It Simple, Stupid"
- **DRY**: MA opposes over-abstraction that violates DRY
- **Zen of Python**: "Simple is better than complex", "Readability counts"

**MA adds unique value:**
- **Intentional whitespace**: Not covered by SOLID/YAGNI/KISS
- **Aesthetic considerations**: Code as art, not just function
- **Cognitive load reduction**: Visual breathing room reduces mental fatigue
- **Cultural wisdom**: 1000+ years of Japanese aesthetic philosophy

### References

- `docs/developer/ma-principle.md` - Comprehensive MA guide (21KB)
- Zen of Python: `python3 -c "import this"`
- Clean Code by Robert C. Martin (Uncle Bob)
- The Art of Readable Code by Boswell & Foucher
- Japanese aesthetics: Wabi-sabi (侘寂), Ma (間), Yugen (幽玄)

---

## FR-109: Language Server Protocol (LSP)

**Category:** Developer Tools | **Priority:** High | **Status:** ✅ Implemented | **Version:** 2.0.9
**Implementation:** `src/asciidoc_artisan/lsp/`

Full Language Server Protocol implementation for AsciiDoc documents, enabling IDE-like features in any LSP-compatible editor.

**Acceptance:** Completion <100ms | Diagnostics <200ms | 54 tests passing | MA compliant (<250 lines/module)

### Description

Provides a complete LSP server using pygls that integrates with editors like VSCode, Neovim, and Emacs:

- **Completion**: Context-aware auto-complete for syntax, attributes, cross-references
- **Diagnostics**: Real-time syntax validation using existing SyntaxChecker
- **Hover**: Documentation on hover for AsciiDoc elements
- **Go-to-definition**: Navigate to anchor definitions from cross-references
- **Document symbols**: Hierarchical outline view of document structure

### Acceptance Criteria

- [x] LSP server starts via `python -m asciidoc_artisan.lsp`
- [x] Completion provides context-aware suggestions (<100ms)
- [x] Diagnostics validates syntax in real-time (<200ms)
- [x] Hover shows documentation for AsciiDoc elements
- [x] Go-to-definition navigates to anchors
- [x] Document symbols provides outline view
- [x] All modules follow MA principle (<250 lines)
- [x] 54 tests with 100% pass rate

### API Contract

```python
# Start LSP server
python -m asciidoc_artisan.lsp           # stdio mode
python -m asciidoc_artisan.lsp --tcp     # TCP mode (port 2087)

# Server capabilities
from asciidoc_artisan.lsp import AsciiDocLanguageServer
server = AsciiDocLanguageServer()
server.start_io()
```

### Architecture (MA Compliant)

| Module | Lines | Purpose |
|--------|-------|---------|
| `server.py` | ~200 | Core LSP server with pygls |
| `completion_provider.py` | ~250 | Auto-complete logic |
| `diagnostics_provider.py` | ~180 | Syntax validation |
| `hover_provider.py` | ~200 | Hover documentation |
| `symbols_provider.py` | ~200 | Document outline |
| `document_state.py` | ~80 | Thread-safe state management |

### Test Requirements

- **Minimum Tests:** 54 (implemented)
- **Coverage Target:** 95%+
- **Test Types:**
  - Completion: 17 tests (syntax, attributes, xrefs, includes)
  - Diagnostics: 9 tests (validation, severity mapping)
  - Hover: 10 tests (syntax, attributes, plain text)
  - Symbols: 10 tests (headings, anchors, definitions)
  - Document state: 8 tests (CRUD, thread safety)

### Dependencies

- `pygls>=2.0.0` - Python LSP server framework
- `lsprotocol>=2025.0.0` - LSP type definitions
- `FR-097` (SyntaxChecker) - Reuses existing validation
- `FR-096` (AutoComplete) - Shares completion patterns

---

## FR Template (For Remaining FRs)

For the remaining FRs, use this template structure:

```markdown
## FR-XXX: Feature Name

**Category:** [Category]
**Priority:** [Critical/High/Medium/Low]
**Status:** [✅ Implemented / 🟡 Partial / ❌ Not Implemented / 📋 Planned]
**Dependencies:** FR-YYY, FR-ZZZ
**Version:** X.Y.Z
**Implementation:** `path/to/file.py::function_or_class()`

### Description
[Clear, actionable description of what the feature does and why it exists]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### API Contract (if applicable)
\```python
[Function/class signatures with full type hints and docstrings]
\```

### Examples
[3-5 concrete examples showing inputs and expected outputs]

### Test Requirements
- Minimum Tests: X
- Coverage Target: Y%
- Test Types: [unit, integration, performance, security]

### Implementation Guidance
- Approach: [Step-by-step implementation strategy]
- Security: [Security considerations]
- Performance: [Performance constraints and optimization tips]
- Code Pattern: [Example code structure]

### Verification Steps
[How to manually verify the implementation works correctly]
```

---

## Next Steps

**To complete this refactoring:**

1. ✅ Create enhanced format for FR-001 and FR-007 (samples)
2. 📋 Enhance top 20 critical FRs with full format
3. 📋 Add concise versions of remaining FRs using template
4. 📋 Add dependency map for all FRs
5. 📋 Add machine-readable frontmatter (YAML)
6. 📋 Create FR index for quick lookup
7. 📋 Add cross-reference links between FRs

**Benefits:**
- AI can implement features directly from spec
- Clear acceptance criteria for verification
- Test requirements guide TDD approach
- Dependencies prevent implementation order issues
- Examples clarify expected behavior
- Security/performance guidance baked in

---

## See Also

- [GitHub: Spec-Driven Development with AI](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Kiro: The Future of Software Development](https://kiro.dev/blog/kiro-and-the-future-of-software-development/)
- Original SPECIFICATIONS.md (legacy format)
- FR Implementation Matrix (status tracking)

---

**Version:** 2.0-ai-actionable
**Last Updated:** November 15, 2025
**Format:** Specification-Driven Development (AI-Compatible)
