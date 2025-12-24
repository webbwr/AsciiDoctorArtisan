# Project Task Breakdown

**Project**: AsciiDoc Artisan
**Version**: 2.1.0
**Date**: 2025-12-24
**Status**: Ready for Implementation

---

## Executive Summary

This document breaks down the AsciiDoc Artisan project into 120 atomic, implementable tasks organized into 8 phases. Each task is designed to be completed in 1-2 days maximum, with clear dependencies, acceptance criteria, and traceability to requirements and design components.

**Project Metrics**:
- **Total Tasks**: 120
- **Total Effort**: ~240-320 developer days
- **Requirements Coverage**: 184/184 (100%)
- **Target Platform**: Linux, Windows, macOS
- **Technology**: PySide6 6.9+, Python 3.11+

**Sprint Planning**:
- **Phase 1**: Foundation & Infrastructure (20 tasks, ~30 days)
- **Phase 2**: Core Editor & File Operations (18 tasks, ~25 days)
- **Phase 3**: Preview & Rendering (15 tasks, ~22 days)
- **Phase 4**: Git Integration (12 tasks, ~18 days)
- **Phase 5**: Advanced Features (22 tasks, ~35 days)
- **Phase 6**: LSP & Autocomplete (10 tasks, ~15 days)
- **Phase 7**: Testing & Quality (15 tasks, ~25 days)
- **Phase 8**: Documentation & DevOps (8 tasks, ~12 days)

---

## Phase 1: Foundation & Infrastructure

**Priority**: P0 (Critical Path)
**Duration**: ~30 days
**Dependencies**: None

### TASK-001: Project Structure & Build System
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: None
**Requirements**: NFR-036, NFR-039
**Design Refs**: Section 8 (Implementation Guidelines)

**Description**: Initialize project directory structure, setup.py/pyproject.toml, and Makefile

**Acceptance Criteria**:
- [ ] Directory structure matches design (src/asciidoc_artisan/{core,ui,workers,lsp,claude})
- [ ] pyproject.toml with dependencies (PySide6>=6.9, asciidoc3, python-toon)
- [ ] Makefile with targets: run, test, lint, format, install
- [ ] .gitignore includes: __pycache__, .pytest_cache, .mypy_cache, *.pyc

**Implementation Notes**:
- Use pyproject.toml for modern Python packaging
- Include both development and production dependencies
- Setup entry point: asciidoc_artisan = asciidoc_artisan.main:main

---

### TASK-002: Core Settings Manager
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-006, REQ-007, REQ-008, NFR-035
**Design Refs**: Section 1 (Settings Manager)
**Files**: `src/asciidoc_artisan/core/settings.py`

**Description**: Implement Settings class with TOON format storage and auto-migration from JSON

**Acceptance Criteria**:
- [ ] Settings class with get(key, default), set(key, value) methods
- [ ] setting_changed = Signal(str, object) for observers
- [ ] load_settings() reads from ~/.config/asciidoc-artisan/settings.toon
- [ ] save_settings() writes atomically with temp+rename
- [ ] migrate_from_json() auto-converts legacy .json files to .toon
- [ ] Default settings provided if file doesn't exist

**Implementation Notes**:
- Use QObject as base for signals
- Settings stored as nested dict internally
- Migration renames .json to .json.bak after successful conversion
- Settings directory created with 0o700 permissions

---

### TASK-003: TOON Utilities Wrapper
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-001
**Requirements**: TC-005, DEP-004
**Design Refs**: Section 1 (TOON Utilities)
**Files**: `src/asciidoc_artisan/core/toon_utils.py`

**Description**: Wrap python-toon library with project-specific utilities

**Acceptance Criteria**:
- [ ] dump(data, file, indent=2) function
- [ ] load(file) function returning dict
- [ ] dumps(data, indent=2) function returning string
- [ ] loads(content) function parsing TOON string
- [ ] Error handling with informative messages

**Implementation Notes**:
- Import from python-toon library
- Add type hints (dict[str, Any])
- Handle TOONDecodeError gracefully

---

### TASK-004: Atomic File Operations
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-003
**Requirements**: REQ-013, NFR-012, TC-008
**Design Refs**: Section 1 (File Operations), Section 3 (Atomic Write Pattern)
**Files**: `src/asciidoc_artisan/core/file_operations.py`

**Description**: Implement safe file I/O with atomic write pattern

**Acceptance Criteria**:
- [ ] atomic_save_text(file_path, content, encoding="utf-8") -> bool
- [ ] atomic_save_toon(file_path, data, indent=2) -> bool
- [ ] read_text_file(file_path) -> tuple[str, str] (content, encoding)
- [ ] detect_encoding(file_path) -> str (supports UTF-8, UTF-16, Latin-1, ASCII)
- [ ] All writes use temp+rename pattern (.tmp suffix)
- [ ] Cleanup temp files on failure

**Implementation Notes**:
- Use Path.replace() for atomic rename
- Detect encoding with chardet library or BOM detection
- Log all file operations with pathlib.Path
- Handle PermissionError, FileNotFoundError

---

### TASK-005: Document Models (Pydantic)
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-021, REQ-104
**Design Refs**: Section 1 (Document Model), Section 3 (Data Design)
**Files**: `src/asciidoc_artisan/core/document_models.py`

**Description**: Define Pydantic models for document state and metadata

**Acceptance Criteria**:
- [ ] DocumentModel dataclass with: path, content, encoding, modified, line_count, word_count
- [ ] SyntaxErrorModel dataclass with: line, column, code, message, severity
- [ ] GitResult dataclass with: command, returncode, stdout, stderr, duration_ms
- [ ] CompletionItem dataclass with: label, insert_text, kind, documentation, detail
- [ ] All models have type annotations and validators

**Implementation Notes**:
- Use @dataclass from dataclasses module
- Add @property methods for computed values (is_error, success)
- Error codes: E001-E104 (errors), W001-W005 (warnings), I001-I003 (info)

---

### TASK-006: AsciiDoc Converter
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-005
**Requirements**: REQ-026, REQ-028, REQ-033, REQ-040
**Design Refs**: Section 1 (AsciiDoc Converter)
**Files**: `src/asciidoc_artisan/core/asciidoc_converter.py`

**Description**: Wrapper for asciidoc3 library with theme support

**Acceptance Criteria**:
- [ ] convert_to_html(content, theme="dark") -> str
- [ ] apply_theme_css(html, theme) -> str (inject CSS)
- [ ] extract_syntax_errors(content) -> list[SyntaxErrorModel]
- [ ] Themes supported: dark, light
- [ ] Error handling for invalid AsciiDoc syntax
- [ ] Performance: <200ms for 10,000 lines

**Implementation Notes**:
- Use asciidoc3 API for rendering
- Theme CSS stored in src/asciidoc_artisan/themes/{dark,light}.css
- Parse asciidoc3 error output to extract line numbers

---

### TASK-007: Base Worker Template
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: TC-003, TC-004
**Design Refs**: Section 3 (Base Worker), Section 3 (Worker Thread Pattern)
**Files**: `src/asciidoc_artisan/workers/base_worker.py`

**Description**: Base class for all QThread workers with queue and cancellation

**Acceptance Criteria**:
- [ ] BaseWorker(QThread) with signals: result_ready, error_occurred, progress_changed
- [ ] queue_request(item) method adds to internal queue
- [ ] cancel() method sets cancellation flag
- [ ] run() method processes queue in loop
- [ ] _process(item) abstract method for subclasses
- [ ] Graceful shutdown on cancellation

**Implementation Notes**:
- Use QThread as base class
- Internal _queue as list with thread-safe access
- msleep(10) when queue empty to avoid busy-waiting
- Emit signals for cross-thread communication

---

### TASK-008: Main Application Entry Point
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-002
**Requirements**: NFR-001
**Design Refs**: Section 7 (Startup Optimization)
**Files**: `src/asciidoc_artisan/main.py`

**Description**: Application entry point with optimized startup sequence

**Acceptance Criteria**:
- [ ] main() function returns exit code
- [ ] QApplication initialization
- [ ] Settings loaded asynchronously
- [ ] Main window shown within 100ms (Phase 1)
- [ ] Workers started in Phase 3 (QTimer.singleShot)
- [ ] LSP server started in Phase 4 (QTimer.singleShot)
- [ ] Startup time measured and logged

**Implementation Notes**:
- Use QTimer for deferred initialization
- Phase 1 (0-100ms): Show window
- Phase 2 (100-200ms): Load settings async
- Phase 3 (200-300ms): Start workers
- Phase 4 (300-400ms): Start LSP server

---

### TASK-009: Theme Manager
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-002
**Requirements**: REQ-033, NFR-022
**Design Refs**: Section 2 (Theme Manager)
**Files**: `src/asciidoc_artisan/ui/theme_manager.py`

**Description**: Manage application themes (dark/light mode)

**Acceptance Criteria**:
- [ ] ThemeManager class with apply_theme(dark: bool) method
- [ ] DARK_STYLESHEET and LIGHT_STYLESHEET constants
- [ ] Applies to QMainWindow, QPlainTextEdit, QTextBrowser, QMenuBar, QStatusBar
- [ ] Theme change completes within 100ms
- [ ] Current theme persisted in settings

**Implementation Notes**:
- Use QApplication.setStyleSheet() for global styling
- Theme colors follow design specs (dark: #1e1e1e bg, light: #ffffff bg)
- Emit theme_changed signal for components to react

---

### TASK-010: Line Number Area Widget
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-003
**Design Refs**: Section 2 (Main Window), SPEC Editor Widget Template
**Files**: `src/asciidoc_artisan/ui/line_number_area.py`

**Description**: Line number gutter widget for editor

**Acceptance Criteria**:
- [ ] LineNumberArea(QWidget) class
- [ ] Displays line numbers aligned right
- [ ] Width adjusts automatically based on line count
- [ ] Current line highlighted with distinct background
- [ ] Updates in real-time on text changes
- [ ] Gutter color follows theme

**Implementation Notes**:
- Connect to editor.blockCountChanged and editor.updateRequest signals
- Calculate width based on digit count: log10(line_count) + 1
- Use QPainter for custom drawing
- Highlight current line with selection color

---

### TASK-011: Recent Files Tracker
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-002, TASK-004
**Requirements**: REQ-016, REQ-017
**Design Refs**: Section 1 (File Operations)
**Files**: `src/asciidoc_artisan/core/recent_templates_tracker.py`

**Description**: Track and persist recently opened files

**Acceptance Criteria**:
- [ ] add_recent_file(path: Path) method
- [ ] get_recent_files() -> list[Path] (max 10)
- [ ] Duplicates removed (most recent kept)
- [ ] Non-existent files purged on load
- [ ] Stored in ~/.config/asciidoc-artisan/recent_files.toon
- [ ] Atomic saves with temp+rename

**Implementation Notes**:
- Use TOON format: `files: ["/path1", "/path2"]`
- LRU eviction when max_items=10 exceeded
- Validate paths exist before returning

---

### TASK-012: Git Result Data Model
**Priority**: P1
**Effort**: XS (1-2 hours)
**Dependencies**: TASK-005
**Requirements**: REQ-045, REQ-046, REQ-047
**Design Refs**: Section 3 (Data Design)
**Files**: `src/asciidoc_artisan/core/git_models.py`

**Description**: Data models for Git operations

**Acceptance Criteria**:
- [ ] GitResult dataclass: command, returncode, stdout, stderr, duration_ms
- [ ] GitCommand dataclass: command, args, cwd
- [ ] success property returns returncode == 0
- [ ] All fields typed and validated

**Implementation Notes**:
- Use @dataclass decorator
- Add __str__ for logging
- duration_ms measured in worker

---

### TASK-013: Chat Panel Widget (UI)
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-067, REQ-076
**Design Refs**: Section 2 (Chat Panel Widget), SPEC Chat Panel Widget Template
**Files**: `src/asciidoc_artisan/ui/chat_panel_widget.py`

**Description**: AI chat panel with context mode selector and history

**Acceptance Criteria**:
- [ ] ChatPanelWidget(QWidget) class
- [ ] Context mode selector (QComboBox): Document, Syntax, General, Editing
- [ ] Chat history (QTextBrowser) with Markdown rendering
- [ ] Input field (QLineEdit) with placeholder "Ask AI..."
- [ ] message_submitted = Signal(str)
- [ ] context_mode_changed = Signal(str)
- [ ] Minimum width: 200 pixels

**Implementation Notes**:
- Use QVBoxLayout with spacing=4, margins=4
- Connect input returnPressed to submit handler
- Markdown rendering with QTextBrowser.setMarkdown()
- Collapsible via parent splitter

---

### TASK-014: Find Bar Widget (UI)
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-081, REQ-086
**Design Refs**: Section 2 (Find Bar Widget), SPEC Find Bar Widget Template
**Files**: `src/asciidoc_artisan/ui/find_bar_widget.py`

**Description**: Find and replace bar with regex support

**Acceptance Criteria**:
- [ ] FindBarWidget(QWidget) class
- [ ] Find field and Replace field (QLineEdit)
- [ ] Case checkbox and Regex checkbox
- [ ] Buttons: Find, Replace, Replace All, Close
- [ ] find_requested = Signal(str, bool, bool) (text, case_sensitive, regex)
- [ ] replace_requested = Signal(str, str) (find_text, replace_text)
- [ ] closed = Signal()

**Implementation Notes**:
- Use QHBoxLayout with compact spacing
- Close button shows "×" character
- Escape key triggers closed signal
- State persisted in settings

---

### TASK-015: Export Dialog (UI)
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-091, REQ-098, REQ-100
**Design Refs**: Section 2 (Export Dialog), SPEC Dialog Templates
**Files**: `src/asciidoc_artisan/ui/export_dialog.py`

**Description**: Export options dialog for multi-format export

**Acceptance Criteria**:
- [ ] ExportDialog(QDialog) class
- [ ] Format selector: HTML, PDF, DOCX, Markdown, LaTeX
- [ ] Output path field with Browse button
- [ ] "Open after export" checkbox
- [ ] "Include TOC" checkbox
- [ ] OK/Cancel buttons (QDialogButtonBox)
- [ ] get_result() returns export options dict

**Implementation Notes**:
- Use QVBoxLayout
- File dialog filters by format
- Default output path: same as source with new extension
- Settings persistence for last format and output directory

---

### TASK-016: Settings Dialog (UI)
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-002, TASK-009
**Requirements**: NFR-021, NFR-022
**Design Refs**: Section 2 (Settings Dialog), SPEC Dialog Templates
**Files**: `src/asciidoc_artisan/ui/settings_dialog.py`

**Description**: Tabbed settings dialog for application preferences

**Acceptance Criteria**:
- [ ] SettingsDialog(QDialog) class with QTabWidget
- [ ] Tabs: General, Editor, AI, Preview, Git, Privacy
- [ ] General: theme, language, startup options
- [ ] Editor: font family, font size, tab width, line wrap
- [ ] AI: Ollama host, model, temperature, context mode
- [ ] Preview: debounce delay, GPU enabled, theme
- [ ] Git: auto-stage, commit template
- [ ] Privacy: telemetry, crash reports
- [ ] Apply/OK/Cancel buttons
- [ ] Size: 600x500 pixels

**Implementation Notes**:
- Use QTabWidget for tabs
- Apply button saves settings without closing
- OK saves and closes, Cancel discards changes
- Live preview of font changes in editor tab

---

### TASK-017: Git Commit Dialog (UI)
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-012
**Requirements**: REQ-044, REQ-052
**Design Refs**: Section 2 (Git Commit Dialog), SPEC Dialog Templates
**Files**: `src/asciidoc_artisan/ui/git_commit_dialog.py`

**Description**: Quick commit dialog with staged files and diff preview

**Acceptance Criteria**:
- [ ] GitCommitDialog(QDialog) class
- [ ] Commit message field (QTextEdit) with validation
- [ ] Staged files list (QListWidget)
- [ ] Diff preview (QTextBrowser) with syntax highlighting
- [ ] Auto-stage current file checkbox
- [ ] Commit/Cancel buttons
- [ ] Validates commit message non-empty
- [ ] Shows "Auto-staged: {filename}" if applicable

**Implementation Notes**:
- Use QSplitter for resizable sections
- Color-code diff: green (additions), red (deletions)
- Disable Commit button if message empty
- Load staged files on dialog open

---

### TASK-018: About Dialog (UI)
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-001
**Requirements**: NFR-030
**Design Refs**: SPEC Dialog Templates
**Files**: `src/asciidoc_artisan/ui/about_dialog.py`

**Description**: About dialog with version info and credits

**Acceptance Criteria**:
- [ ] AboutDialog(QDialog) class
- [ ] Application logo/icon
- [ ] Version number from __version__
- [ ] Credits: contributors, libraries used
- [ ] License: GPL v3 (link to full text)
- [ ] Size: 400x300 pixels
- [ ] Close button

**Implementation Notes**:
- Use QVBoxLayout
- Logo centered with QLabel.setPixmap()
- Hyperlinks for external resources
- Modal dialog

---

### TASK-019: Status Bar Components
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: REQ-042, REQ-023, NFR-023
**Design Refs**: Section 2 (Main Window), SPEC Status Bar
**Files**: `src/asciidoc_artisan/ui/status_bar.py` (or integrated in main_window.py)

**Description**: Status bar with message, position, encoding, Git status

**Acceptance Criteria**:
- [ ] Sections: message (stretch), position (120px), encoding (80px), git_branch (100px), git_status (60px)
- [ ] Position format: "Ln {line}, Col {col}"
- [ ] Git branch format: "📌 {branch}"
- [ ] Git status format: "M:{modified} S:{staged}"
- [ ] Messages auto-clear after 5 seconds
- [ ] Error messages styled with red background

**Implementation Notes**:
- Use QStatusBar with QLabel widgets
- Connect to cursor position changed signal
- Git status updated via GitHandler signals
- Temporary messages with QTimer for auto-clear

---

### TASK-020: Application Icon & Resources
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-001
**Requirements**: NFR-022
**Design Refs**: Section 8 (Implementation Guidelines)
**Files**: `src/asciidoc_artisan/resources/`, `resources.qrc`

**Description**: Application icon, toolbar icons, and Qt resource file

**Acceptance Criteria**:
- [ ] Application icon (512x512, 256x256, 128x128, 64x64, 32x32, 16x16)
- [ ] Toolbar icons for common actions (Open, Save, Undo, Redo, etc.)
- [ ] resources.qrc Qt resource file
- [ ] Compiled resources.py with rcc
- [ ] Icons accessible via :/icons/name.png

**Implementation Notes**:
- Use SVG icons for scalability
- Icon theme: consistent style (Feather, Material, or Lucide)
- Dark/light mode icon variants
- Compile with: `pyside6-rcc resources.qrc -o resources.py`

---

## Phase 2: Core Editor & File Operations

**Priority**: P0 (Critical Path)
**Duration**: ~25 days
**Dependencies**: Phase 1

### TASK-021: Main Window Shell
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-008, TASK-010, TASK-019
**Requirements**: REQ-001, REQ-007, REQ-008
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Main application window with layout and menu structure

**Acceptance Criteria**:
- [ ] AsciiDocEditor(QMainWindow) class
- [ ] Central widget: QSplitter(horizontal) with 3 panels
- [ ] Editor pane: QPlainTextEdit with LineNumberArea
- [ ] Preview pane placeholder (QWidget)
- [ ] Chat pane placeholder (QWidget)
- [ ] Splitter ratios: [40, 40, 20] (editor, preview, chat)
- [ ] Minimum size: 1024x768 pixels
- [ ] Window title format: "{filename} - AsciiDoc Artisan"
- [ ] Status bar initialized

**Implementation Notes**:
- MA principle: keep main_window.py <400 lines
- Delegate domain logic to handlers (added in subsequent tasks)
- Use QSplitter for resizable panels
- Load/save window geometry and splitter positions in settings

---

### TASK-022: Menu Structure
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-021
**Requirements**: NFR-021
**Design Refs**: SPEC Menu Structure
**Files**: `src/asciidoc_artisan/ui/main_window.py` (create_menus method)

**Description**: Complete menu structure with shortcuts

**Acceptance Criteria**:
- [ ] File menu: New, Open, Recent, Save, Save As, Import, Export, Exit
- [ ] Edit menu: Undo, Redo, Cut, Copy, Paste, Find, Replace, Go to Line
- [ ] View menu: Dark Mode, Preview Panel, Chat Panel, Zoom In/Out/Reset
- [ ] Tools menu: Spell Check, Syntax Check, Templates, Settings
- [ ] Git menu: Quick Commit, Pull, Push, Status, Log
- [ ] GitHub menu: Create PR, List PRs, Create Issue, List Issues
- [ ] Help menu: User Guide, Keyboard Shortcuts, About
- [ ] All shortcuts documented in SPEC Keyboard Shortcuts

**Implementation Notes**:
- Use QAction for menu items
- Connect actions to placeholder slots (implement in handlers)
- Checkable actions for toggles (Dark Mode, Preview Panel, Chat Panel)
- Recent files submenu dynamically populated

---

### TASK-023: File Handler
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-004, TASK-011, TASK-021
**Requirements**: REQ-011 to REQ-022
**Design Refs**: Section 2 (File Handler), Section 3 (Handler Pattern)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`

**Description**: File operations handler (open, save, new, recent files)

**Acceptance Criteria**:
- [ ] FileHandler(QObject) class with reentrancy guard
- [ ] Signals: file_opened(Path), file_saved(Path), file_modified(bool), encoding_changed(str), error_occurred(str)
- [ ] Methods: open_file(), save_file(), save_as(), new_file()
- [ ] add_recent_file(path), load_recent_files()
- [ ] Auto-save timer with configurable interval (default 300s)
- [ ] Encoding detection (UTF-8, UTF-16, Latin-1, ASCII)
- [ ] Close warning dialog if document modified

**Implementation Notes**:
- Use QFileDialog for open/save dialogs
- Filters: "AsciiDoc (*.adoc *.asciidoc *.asc);;Text (*.txt);;All (*.*)"
- Auto-save only if file path exists (not for unsaved new files)
- Modified flag updates window title with asterisk

---

### TASK-024: Syntax Highlighter
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-021
**Requirements**: REQ-009
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/syntax_highlighter.py`

**Description**: AsciiDoc syntax highlighter for editor

**Acceptance Criteria**:
- [ ] AsciiDocHighlighter(QSyntaxHighlighter) class
- [ ] Highlights: headings (= to ======), bold (*text*), italic (_text_)
- [ ] Code blocks (```), lists (*, -, .), links, images
- [ ] Attributes (:name:), cross-refs (<<anchor>>)
- [ ] Comments (//), block delimiters (====, ----)
- [ ] Colors follow active theme (dark/light)
- [ ] Highlighting applied within 100ms of file load

**Implementation Notes**:
- Use QRegularExpression for pattern matching
- Highlighting rules as list of (pattern, format) tuples
- Theme colors from ThemeManager
- Apply to editor with editor.setDocument()

---

### TASK-025: Auto-Indentation Handler
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-021
**Requirements**: REQ-010
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/auto_indent_handler.py`

**Description**: Auto-indentation for lists and blocks

**Acceptance Criteria**:
- [ ] Detects list items (*, -, ., 1.)
- [ ] Detects block delimiters (====, ----)
- [ ] Auto-indents new line to match previous line level
- [ ] Supports nested lists up to 6 levels
- [ ] Respects tab vs. space configuration (settings)
- [ ] Completes within 20ms of Enter key press

**Implementation Notes**:
- Connect to editor.textChanged signal
- Calculate indentation from previous line's leading whitespace
- Insert spaces or tabs based on settings.tab_width
- Handle edge cases: empty lines, end of list

---

### TASK-026: Undo/Redo Integration
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-021
**Requirements**: REQ-004, REQ-005, NFR-024
**Design Refs**: Built-in QPlainTextEdit
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Wire undo/redo actions to editor

**Acceptance Criteria**:
- [ ] Undo action (Ctrl+Z) calls editor.undo()
- [ ] Redo action (Ctrl+Y, Ctrl+Shift+Z) calls editor.redo()
- [ ] Undo stack maintains minimum 100 operations
- [ ] Actions disabled when stack empty
- [ ] Operations complete within 50ms

**Implementation Notes**:
- QPlainTextEdit has built-in undo/redo
- Connect actions: undo_action.triggered.connect(editor.undo)
- Stack size configured with editor.document().setMaximumBlockCount()
- Enable/disable actions based on editor.document().isUndoAvailable()

---

### TASK-027: Cut/Copy/Paste Integration
**Priority**: P0
**Effort**: XS (1-2 hours)
**Dependencies**: TASK-021
**Requirements**: NFR-021
**Design Refs**: Built-in QPlainTextEdit
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Wire clipboard actions to editor

**Acceptance Criteria**:
- [ ] Cut action (Ctrl+X) calls editor.cut()
- [ ] Copy action (Ctrl+C) calls editor.copy()
- [ ] Paste action (Ctrl+V) calls editor.paste()
- [ ] Select All action (Ctrl+A) calls editor.selectAll()
- [ ] Actions work with system clipboard

**Implementation Notes**:
- QPlainTextEdit has built-in clipboard support
- Connect actions directly to editor methods
- No custom logic needed

---

### TASK-028: Font Configuration
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-002, TASK-021
**Requirements**: REQ-006
**Design Refs**: Section 1 (Settings Manager)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Apply font settings to editor

**Acceptance Criteria**:
- [ ] Load editor_font_family and editor_font_size from settings
- [ ] Apply to editor with QFont
- [ ] Default: Courier New, 12pt
- [ ] Font changes applied immediately without restart
- [ ] Connect to settings.setting_changed signal

**Implementation Notes**:
- Use QFont(family, size) and editor.setFont()
- React to setting_changed signal for live updates
- Monospace font recommended for code editing

---

### TASK-029: Modified Flag & Window Title
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-023
**Requirements**: REQ-021
**Design Refs**: Section 2 (File Handler)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`, `ui/main_window.py`

**Description**: Track document modified state and update window title

**Acceptance Criteria**:
- [ ] Modified flag set on text changes
- [ ] Modified flag cleared on successful save
- [ ] Window title format: "*{filename} - AsciiDoc Artisan" (modified)
- [ ] Window title format: "{filename} - AsciiDoc Artisan" (unmodified)
- [ ] file_modified signal emitted on flag change

**Implementation Notes**:
- Connect to editor.textChanged signal
- Emit file_modified signal
- Main window updates title on file_modified signal

---

### TASK-030: Close Warning Dialog
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-029
**Requirements**: REQ-022
**Design Refs**: Section 2 (File Handler)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Warn user before closing modified document

**Acceptance Criteria**:
- [ ] Dialog shown on closeEvent if document modified
- [ ] Buttons: Save, Discard, Cancel
- [ ] Save button saves file and closes
- [ ] Discard button closes without saving
- [ ] Cancel button cancels close
- [ ] Default button: Save

**Implementation Notes**:
- Override closeEvent(event) in main window
- Use QMessageBox.question()
- event.accept() to allow close, event.ignore() to cancel

---

### TASK-031: Encoding Detection & Selection
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-004, TASK-023
**Requirements**: REQ-023, REQ-024
**Design Refs**: Section 1 (File Operations)
**Files**: `src/asciidoc_artisan/core/file_operations.py`, `ui/file_handler.py`

**Description**: Detect file encoding and allow user selection

**Acceptance Criteria**:
- [ ] detect_encoding() supports UTF-8, UTF-16LE, UTF-16BE, Latin-1, ASCII
- [ ] BOM detection for UTF-16
- [ ] Defaults to UTF-8 if detection fails
- [ ] Encoding displayed in status bar
- [ ] Status bar menu for encoding selection
- [ ] Reload file with selected encoding

**Implementation Notes**:
- Use chardet library or manual BOM detection
- Status bar encoding label clickable → encoding menu
- Reload preserves cursor position
- Handle incompatible encodings with error dialog

---

### TASK-032: File Error Handling
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-023
**Requirements**: REQ-025
**Design Refs**: Section 6 (Security Design)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`

**Description**: Comprehensive error handling for file operations

**Acceptance Criteria**:
- [ ] FileNotFoundError → "File not found: {path}"
- [ ] PermissionError → "Permission denied: {path}"
- [ ] IsADirectoryError → "Path is a directory: {path}"
- [ ] OSError → "OS error: {message}"
- [ ] Error dialog shows file path and OS error code
- [ ] Operation rolled back (no partial writes)
- [ ] User returned to previous state

**Implementation Notes**:
- Try/except blocks around all file I/O
- Error messages sanitized (replace home with ~)
- Log errors with full stack trace
- Show user-friendly QMessageBox.critical()

---

### TASK-033: Recent Files Menu
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-011, TASK-022, TASK-023
**Requirements**: REQ-017, REQ-018
**Design Refs**: Section 2 (File Handler)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`, `ui/main_window.py`

**Description**: Populate and handle Recent Files menu

**Acceptance Criteria**:
- [ ] Recent Files submenu dynamically populated
- [ ] Shows 10 most recent files
- [ ] Reverse chronological order
- [ ] Format: "{filename} - {truncated_path}"
- [ ] Empty state: "No recent files" (disabled)
- [ ] Click opens file
- [ ] Non-existent files removed from list with error dialog

**Implementation Notes**:
- Clear menu and rebuild on update
- Truncate path to 50 characters with ...
- Load recent files on startup
- Add file to recent on successful open

---

### TASK-034: Auto-Save Timer
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-023
**Requirements**: REQ-019, REQ-020
**Design Refs**: Section 2 (File Handler)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`

**Description**: Auto-save timer for documents

**Acceptance Criteria**:
- [ ] setup_autosave(interval) method
- [ ] Default interval: 300 seconds (5 minutes)
- [ ] Timer resets on manual save
- [ ] Only saves if document modified and path exists
- [ ] Silent operation (no status bar message)
- [ ] Configurable in settings

**Implementation Notes**:
- Use QTimer with timeout signal
- Connect to on_autosave_timeout slot
- Check modified flag and path before saving
- Don't clear modified flag on auto-save

---

### TASK-035: New File Creation
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: TASK-023, TASK-030
**Requirements**: REQ-015
**Design Refs**: Section 2 (File Handler)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`

**Description**: Create new untitled document

**Acceptance Criteria**:
- [ ] new_file() method
- [ ] Prompts to save if current document modified
- [ ] New document titled "Untitled-{N}.adoc"
- [ ] Clears editor content
- [ ] Clears undo/redo history
- [ ] Sets modified flag to False

**Implementation Notes**:
- Increment counter for each new file
- Check modified flag and show save dialog if needed
- editor.clear() to reset content
- editor.document().clearUndoRedoStacks()

---

### TASK-036: Save/Save As Implementation
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-004, TASK-023
**Requirements**: REQ-013, REQ-014
**Design Refs**: Section 2 (File Handler), Section 3 (Atomic Write Pattern)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`

**Description**: Implement save and save as operations

**Acceptance Criteria**:
- [ ] save_file() saves to existing path or shows save dialog
- [ ] save_as() always shows save dialog
- [ ] Uses atomic_save_text() for integrity
- [ ] Save completes within 200ms for files <1MB
- [ ] Status bar shows "Saved: {filename}"
- [ ] Updates window title with new filename (save_as)
- [ ] Clears modified flag on success

**Implementation Notes**:
- Reentrancy guard: check _is_processing flag
- QFileDialog with default filter "*.adoc"
- Confirm overwrite for save_as
- Handle write errors with error dialog

---

### TASK-037: Open File Implementation
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-004, TASK-023, TASK-030
**Requirements**: REQ-011, REQ-012
**Design Refs**: Section 2 (File Handler)
**Files**: `src/asciidoc_artisan/ui/file_handler.py`

**Description**: Implement file open operation

**Acceptance Criteria**:
- [ ] open_file() shows QFileDialog
- [ ] Filters: .adoc, .asciidoc, .asc, .txt, *.*
- [ ] Remembers last opened directory
- [ ] Supports multi-file selection (future)
- [ ] Files up to 10MB loaded within 500ms
- [ ] UTF-8 encoding detection automatic
- [ ] Prompts to save if current document modified

**Implementation Notes**:
- QFileDialog.getOpenFileName()
- Remember directory in settings
- Load with read_text_file() from file_operations
- Add to recent files on success
- Emit file_opened signal

---

### TASK-038: Document State Persistence
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-002, TASK-021
**Requirements**: REQ-007, REQ-008
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Save/restore window state (geometry, splitter, open files)

**Acceptance Criteria**:
- [ ] save_state() on closeEvent
- [ ] load_state() on startup
- [ ] Saves window geometry (position, size)
- [ ] Saves splitter positions
- [ ] Saves open file paths
- [ ] Restoration completes within 500ms
- [ ] Graceful fallback if state file corrupted
- [ ] Default state for first launch

**Implementation Notes**:
- Store in ~/.config/asciidoc-artisan/editor_state.toon
- Use TOON format with atomic save
- Geometry: {x, y, width, height}
- Splitter: [size1, size2, size3]
- Open files: ["/path1", "/path2"]

---

## Phase 3: Preview & Rendering

**Priority**: P0 (Critical Path)
**Duration**: ~22 days
**Dependencies**: Phase 1, TASK-021

### TASK-039: Preview Worker
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-006, TASK-007
**Requirements**: REQ-028, REQ-032, REQ-035
**Design Refs**: Section 3 (Preview Worker)
**Files**: `src/asciidoc_artisan/workers/preview_worker.py`

**Description**: Background worker for AsciiDoc to HTML rendering

**Acceptance Criteria**:
- [x] PreviewWorker(BaseWorker) class
- [x] _process(item) converts AsciiDoc to HTML
- [x] Uses AsciiDocConverter
- [x] Implements LRU cache (100 blocks)
- [x] Cache hit rate >80% for typical editing
- [x] Timeout after 5 seconds
- [x] Target: <200ms for 10,000 lines

**Implementation Notes**:
- Use functools.lru_cache or custom LRUCache
- Hash content with hashlib.md5() for cache key
- Timeout with QTimer in worker
- Emit result_ready(html) signal

---

### TASK-040: Preview Handler Base
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-039
**Requirements**: REQ-027, REQ-030, REQ-031
**Design Refs**: Section 2 (Preview Handler Base), Section 3 (Debounce Pattern)
**Files**: `src/asciidoc_artisan/ui/preview_handler_base.py`

**Description**: Base preview handler with debouncing and scroll sync

**Acceptance Criteria**:
- [x] PreviewHandlerBase(QObject) class
- [x] Debounce timer (300ms configurable)
- [x] on_text_changed() restarts timer
- [x] on_debounce_timeout() queues preview update
- [x] on_preview_ready(html) updates preview widget
- [x] sync_scroll_editor_to_preview() bidirectional
- [x] sync_scroll_preview_to_editor() bidirectional
- [x] Scroll sync delay <100ms

**Implementation Notes**:
- QTimer with setSingleShot(True) for debounce
- Connect to editor.textChanged signal
- Calculate relative scroll position (percentage)
- Abstract update_preview_widget() for subclasses

---

### TASK-041: Preview Handler GPU (QWebEngineView)
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-040
**Requirements**: REQ-029, TC-009
**Design Refs**: Section 2 (Preview Handler GPU)
**Files**: `src/asciidoc_artisan/ui/preview_handler_gpu.py`

**Description**: GPU-accelerated preview using QWebEngineView

**Acceptance Criteria**:
- [x] PreviewHandlerGPU(PreviewHandlerBase) class
- [x] Uses QWebEngineView widget
- [x] GPU acceleration enabled (Accelerated2dCanvas, WebGL)
- [x] inject_theme_css(theme) injects custom CSS
- [x] handle_link_click(url) opens external links
- [x] 10-50x performance vs QTextBrowser
- [x] Automatic fallback if WebEngine unavailable

**Implementation Notes**:
- Import PySide6.QtWebEngineWidgets.QWebEngineView
- QWebEngineSettings for GPU settings
- CSS injection with runJavaScript()
- Catch ImportError and fall back to QTextBrowser

---

### TASK-042: Preview Panel Integration
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-021, TASK-040, TASK-041
**Requirements**: REQ-026, REQ-034
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Integrate preview panel into main window

**Acceptance Criteria**:
- [x] Replace preview placeholder with QWebEngineView or QTextBrowser
- [x] Initialize preview handler (GPU or fallback)
- [x] Connect editor.textChanged to preview handler
- [x] Toggle Preview Panel action (Ctrl+B)
- [x] Panel collapse/expand animated (200ms)
- [x] Splitter ratios adjusted automatically
- [x] Toggle state persisted in settings

**Implementation Notes**:
- Detect QWebEngineView availability
- Use PreviewHandlerGPU if available, else QTextBrowser fallback
- QSplitter.setSizes() for collapse/expand
- QPropertyAnimation for smooth transitions

---

### TASK-043: Preview Theme CSS
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-009, TASK-041
**Requirements**: REQ-033
**Design Refs**: Section 2 (Preview Handler GPU)
**Files**: `src/asciidoc_artisan/themes/dark.css`, `themes/light.css`

**Description**: CSS themes for preview panel

**Acceptance Criteria**:
- [x] dark.css with dark background (#1e1e1e), light text (#d4d4d4)
- [x] light.css with light background (#ffffff), dark text (#333333)
- [x] Syntax highlighting colors for code blocks
- [x] Consistent typography (headings, paragraphs, lists)
- [x] Table styling
- [x] Image max-width: 100%
- [x] Theme change applies within 100ms

**Implementation Notes**:
- Load CSS from files
- Inject with QWebEngineView.setHtml() or <style> tag
- Colors match editor theme
- Use CSS variables for easy customization

---

### TASK-044: Scroll Sync Implementation
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-040
**Requirements**: REQ-031
**Design Refs**: Section 2 (Preview Handler Base)
**Files**: `src/asciidoc_artisan/ui/preview_handler_base.py`

**Description**: Bidirectional scroll synchronization

**Acceptance Criteria**:
- [x] Editor scroll → preview scroll (sync delay <100ms)
- [x] Preview scroll → editor scroll (sync delay <100ms)
- [x] Maintains relative scroll position (%)
- [x] Works with QWebEngineView and QTextBrowser
- [x] Scroll sync can be disabled in settings

**Implementation Notes**:
- Connect to editor.verticalScrollBar().valueChanged
- Connect to preview.page().scrollPosition() (WebEngine) or preview.verticalScrollBar() (TextBrowser)
- Calculate percentage: value / maximum
- Set corresponding scroll: setValue(percentage * maximum)
- Use flag to prevent infinite loop

---

### TASK-045: Preview Zoom Controls
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-042
**Requirements**: REQ-036
**Design Refs**: Section 2 (Preview Handler Base)
**Files**: `src/asciidoc_artisan/ui/preview_handler_base.py`, `ui/main_window.py`

**Description**: Zoom in/out/reset for preview panel

**Acceptance Criteria**:
- [x] Zoom In action (Ctrl+Plus) increases zoom by 10%
- [x] Zoom Out action (Ctrl+Minus) decreases zoom by 10%
- [x] Reset Zoom action (Ctrl+0) resets to 100%
- [x] Zoom range: 50% to 300%
- [x] Zoom level persisted in settings
- [x] Works with both QWebEngineView and QTextBrowser

**Implementation Notes**:
- QWebEngineView: setZoomFactor(factor)
- QTextBrowser: use CSS transform or font size
- Store zoom level in settings
- Update zoom label in status bar

---

### TASK-046: Preview Error Display
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-039, TASK-040
**Requirements**: REQ-040
**Design Refs**: Section 3 (Preview Worker)
**Files**: `src/asciidoc_artisan/workers/preview_worker.py`, `ui/preview_handler_base.py`

**Description**: Display rendering errors in preview panel

**Acceptance Criteria**:
- [x] Error shown with line number and description
- [x] Error format: "Error at line {line}: {message}"
- [x] Previous valid preview retained
- [x] Error cleared on next successful render
- [x] Syntax errors styled with red background

**Implementation Notes**:
- Worker emits error_occurred(message, line) signal
- Preview handler displays error in preview pane
- Use HTML template for error display
- Include link to jump to error line in editor

---

### TASK-047: Preview Rendering Timeout
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-039
**Requirements**: REQ-035
**Design Refs**: Section 3 (Preview Worker)
**Files**: `src/asciidoc_artisan/workers/preview_worker.py`

**Description**: Timeout for long-running preview renders

**Acceptance Criteria**:
- [x] Timeout after 5 seconds
- [x] Worker thread terminated gracefully
- [x] Error message: "Preview render timeout (document too large)"
- [x] Previous preview content retained
- [x] Timeout configurable in settings

**Implementation Notes**:
- Use QTimer in worker thread
- Set timeout on each _process() call
- Cancel rendering on timeout
- Emit error_occurred signal with timeout message

---

### TASK-048: Incremental Rendering
**Priority**: P2
**Effort**: L (8-16 hours)
**Dependencies**: TASK-039
**Requirements**: REQ-032, TC-010
**Design Refs**: Section 3 (Preview Worker), Section 7 (Preview Performance)
**Files**: `src/asciidoc_artisan/workers/incremental_renderer.py`

**Description**: Incremental rendering with block-level caching

**Acceptance Criteria**:
- [x] Parse AsciiDoc into blocks
- [x] Hash each block for cache key
- [x] LRU cache with 100 block capacity
- [x] Only re-render changed blocks
- [x] Cache hit rate >80%
- [x] 50-70% performance improvement
- [x] Fallback to full render on parse errors

**Implementation Notes**:
- Block types: heading, paragraph, list, code block, table, etc.
- Use MD5 hash for cache keys
- LRU eviction when capacity exceeded
- Merge cached and new rendered blocks

---

### TASK-049: Export Preview to HTML
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-042, TASK-015
**Requirements**: REQ-039
**Design Refs**: Section 2 (Export Dialog)
**Files**: `src/asciidoc_artisan/ui/export_dialog.py`, `ui/preview_handler_base.py`

**Description**: Export current preview as standalone HTML

**Acceptance Criteria**:
- [x] Export Preview to HTML action in File menu
- [x] Includes embedded CSS and images
- [x] Preserves all formatting and styles
- [x] Opens in default browser if "Open after export" checked
- [x] Save dialog with .html filter
- [x] Self-contained (no external resources)

**Implementation Notes**:
- Get HTML from preview widget
- Inline CSS styles
- Base64 encode images
- Use QDesktopServices.openUrl() to open in browser

---

### TASK-050: Preview Panel Toggle
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-042
**Requirements**: REQ-034
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Toggle preview panel visibility

**Acceptance Criteria**:
- [x] Toggle Preview Panel action (Ctrl+B)
- [x] Panel collapse/expand animated (200ms)
- [x] Splitter ratios adjusted: [80, 0, 20] (collapsed) or [40, 40, 20] (expanded)
- [x] Toggle state persisted in settings
- [x] Menu item checkable

**Implementation Notes**:
- QSplitter.setSizes() for collapse/expand
- QPropertyAnimation for smooth transition
- Save state to settings on toggle
- Restore state on startup

---

### TASK-051: Debounce Configuration
**Priority**: P2
**Effort**: XS (1-2 hours)
**Dependencies**: TASK-040
**Requirements**: REQ-019
**Design Refs**: Section 2 (Preview Handler Base)
**Files**: `src/asciidoc_artisan/ui/preview_handler_base.py`, `ui/settings_dialog.py`

**Description**: Configurable debounce delay for preview updates

**Acceptance Criteria**:
- [x] Debounce delay configurable in settings (default 300ms)
- [x] Range: 100ms to 1000ms
- [x] Setting applied immediately
- [x] Slider in Settings > Preview tab

**Implementation Notes**:
- Store in settings.preview_debounce_ms
- React to setting_changed signal
- Update timer interval: timer.setInterval(ms)

---

### TASK-052: Preview Performance Monitoring
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-039
**Requirements**: NFR-002
**Design Refs**: Section 7 (Performance Design)
**Files**: `src/asciidoc_artisan/workers/preview_worker.py`

**Description**: Monitor and log preview rendering performance

**Acceptance Criteria**:
- [x] Measure rendering time with QElapsedTimer
- [x] Log warnings if >200ms
- [x] Emit performance metrics via signal
- [x] Display render time in status bar (optional)
- [x] Performance stats in debug mode

**Implementation Notes**:
- QElapsedTimer.start() before render, .elapsed() after
- Log to logger.debug()
- Emit performance_measured(duration_ms) signal
- Conditional display based on settings

---

### TASK-053: GPU Fallback Detection
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-041
**Requirements**: NFR-034
**Design Refs**: Section 2 (Preview Handler GPU)
**Files**: `src/asciidoc_artisan/ui/preview_handler_gpu.py`, `ui/main_window.py`

**Description**: Detect QWebEngineView availability and fall back gracefully

**Acceptance Criteria**:
- [x] Try importing PySide6.QtWebEngineWidgets
- [x] Catch ImportError and use QTextBrowser
- [x] User notification: "GPU acceleration unavailable, using fallback renderer"
- [x] Fallback mode persisted in settings
- [x] No crashes or errors on fallback

**Implementation Notes**:
- Try/except ImportError around QWebEngineView import
- Set settings.preview_gpu_enabled = False on fallback
- Log fallback reason
- Show info notification on first run

---

## Phase 4: Git Integration

**Priority**: P1 (High Priority)
**Duration**: ~18 days
**Dependencies**: Phase 1, TASK-021

### TASK-054: Git Worker
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-007, TASK-012
**Requirements**: REQ-045, REQ-046, REQ-047, NFR-011, TC-006
**Design Refs**: Section 3 (Git Worker), Section 6 (Subprocess Security)
**Files**: `src/asciidoc_artisan/workers/git_worker.py`

**Description**: Background worker for Git CLI operations

**Acceptance Criteria**:
- [x] GitWorker(BaseWorker) class
- [x] _process(item) executes Git commands
- [x] Always uses shell=False with list arguments
- [x] Commands: status, commit, pull, push, log
- [x] Timeout: 30 seconds
- [x] Emits GitResult on completion
- [x] Security validation: no shell=True in codebase

**Implementation Notes**:
- subprocess.run(["git", cmd, *args], shell=False, capture_output=True, text=True, timeout=30)
- Validate commands against whitelist
- Input validation on commit messages (no dangerous chars)
- Measure duration with time.time()

---

### TASK-055: Git Handler
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-054, TASK-017
**Requirements**: REQ-041 to REQ-055
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_handler.py`

**Description**: Git operations orchestration

**Acceptance Criteria**:
- [x] GitHandler(QObject) class
- [x] detect_repository() searches for .git directory
- [x] refresh_status() queues status check to worker
- [x] show_quick_commit_dialog() displays commit dialog
- [x] commit(message), pull(), push() methods
- [x] on_git_operation_complete(result) updates UI
- [x] Signals: repository_detected, status_updated, operation_complete, operation_failed

**Implementation Notes**:
- Search for .git up to filesystem root
- Worker coordination: queue command, connect signals
- Status bar updates on operation complete
- Error dialog on operation failure

---

### TASK-056: Git Status Display
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-019, TASK-055
**Requirements**: REQ-042, REQ-043
**Design Refs**: Section 2 (Git Handler), SPEC Status Bar
**Files**: `src/asciidoc_artisan/ui/git_handler.py`, `ui/main_window.py`

**Description**: Display Git status in status bar

**Acceptance Criteria**:
- [x] Status bar format: "📌 {branch_name}"
- [x] Git status format: "M:{modified} S:{staged}"
- [x] Updates on commit, pull, push, checkout
- [x] Detached HEAD shown as "HEAD@{hash}"
- [x] Status check completes within 200ms

**Implementation Notes**:
- Execute git status --porcelain
- Parse output: M (modified), A (added), D (deleted), ?? (untracked)
- Count modified and staged files
- Update status bar labels

---

### TASK-057: Quick Commit Dialog Implementation
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-017, TASK-055
**Requirements**: REQ-044, REQ-052
**Design Refs**: Section 2 (Git Commit Dialog)
**Files**: `src/asciidoc_artisan/ui/git_commit_dialog.py`

**Description**: Quick commit dialog with staged files and diff

**Acceptance Criteria**:
- [x] Displays staged files list
- [x] Shows diff preview with color coding
- [x] Commit message field with validation
- [x] Auto-stage current file checkbox
- [x] Commit button disabled if message empty
- [x] Executes git commit on Commit click

**Implementation Notes**:
- Load staged files on dialog open: git diff --cached --name-only
- Load diff: git diff --cached
- Color code diff: green (+), red (-)
- Validate message: non-empty, <500 chars
- Auto-stage with git add if checkbox enabled

---

### TASK-058: Git Pull/Push Operations
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-055
**Requirements**: REQ-046, REQ-047
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_handler.py`

**Description**: Implement pull and push operations

**Acceptance Criteria**:
- [x] pull() executes git pull --ff-only
- [x] push() executes git push
- [x] Shows progress dialog during operation
- [x] Success notification in status bar
- [x] Error dialog on failure (push rejection, merge conflicts)
- [x] Timeout: 30 seconds

**Implementation Notes**:
- Queue commands to GitWorker
- Show QProgressDialog with "Cancel" button
- Handle push rejection with error message
- Success message: "Pulled {N} commits" or "Pushed to origin"

---

### TASK-059: Git Status Panel
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-055
**Requirements**: REQ-048
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_status_panel.py`

**Description**: Panel showing modified, staged, and untracked files

**Acceptance Criteria**:
- [x] GitStatusPanel(QWidget) class
- [x] Files grouped by status: Modified, Staged, Untracked
- [x] Real-time updates on file changes
- [x] Double-click opens file diff
- [x] Right-click context menu: Stage, Unstage, Discard
- [x] Updates automatically

**Implementation Notes**:
- Use QTreeWidget with groups
- Connect to file system watcher for auto-updates
- Show diff in new dialog or preview pane
- Context menu actions queue Git commands

---

### TASK-060: Git Log Viewer
**Priority**: P2
**Effort**: L (8-16 hours)
**Dependencies**: TASK-055
**Requirements**: REQ-049
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_log_viewer.py`

**Description**: Commit history viewer

**Acceptance Criteria**:
- [ ] GitLogViewer(QWidget) class
- [ ] Shows last 50 commits
- [ ] Columns: Hash, Author, Date, Message
- [ ] Paginated (50 commits per page)
- [ ] Click commit shows full diff
- [ ] Next/Previous page buttons

**Implementation Notes**:
- Execute git log --oneline -n 50 --skip {offset}
- Parse output into table rows
- Click opens diff dialog: git show {hash}
- Format date with datetime.strptime()

---

### TASK-061: Git Diff Display
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-055
**Requirements**: REQ-054
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_diff_dialog.py`

**Description**: Side-by-side diff viewer

**Acceptance Criteria**:
- [ ] GitDiffDialog(QDialog) class
- [ ] Side-by-side layout with old/new versions
- [ ] Color-coded: green (additions), red (deletions), yellow (changes)
- [ ] Context lines: 3 before/after
- [ ] Syntax highlighting for code
- [ ] Close button

**Implementation Notes**:
- Execute git diff {file}
- Parse unified diff format
- Use QTextBrowser or QPlainTextEdit for display
- Syntax highlighting with QSyntaxHighlighter

---

### TASK-062: Git Branch Checkout
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-055
**Requirements**: REQ-055
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_branch_dialog.py`

**Description**: Branch switching dialog

**Acceptance Criteria**:
- [x] GitBranchDialog(QDialog) class
- [x] Lists all local branches
- [x] Indicates current branch with asterisk
- [x] Warns if uncommitted changes exist
- [x] Checkout button executes git checkout {branch}
- [x] Refreshes UI on successful checkout

**Implementation Notes**:
- Execute git branch to list branches
- Parse output: * indicates current branch
- Check git status for uncommitted changes
- Warn with QMessageBox if dirty working directory

---

### TASK-063: Git Command Timeout Handling
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-054
**Requirements**: REQ-050
**Design Refs**: Section 3 (Git Worker)
**Files**: `src/asciidoc_artisan/workers/git_worker.py`

**Description**: Timeout handling for Git operations

**Acceptance Criteria**:
- [x] Timeout after 30 seconds
- [x] Worker thread stopped gracefully
- [x] Error message: "Git operation timeout"
- [x] User can retry or cancel
- [x] Timeout configurable in settings

**Implementation Notes**:
- subprocess.run() with timeout=30
- Catch subprocess.TimeoutExpired
- Emit error_occurred signal
- Show retry dialog

---

### TASK-064: Git Error Handling
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-054, TASK-055
**Requirements**: REQ-051
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_handler.py`

**Description**: Comprehensive Git error handling

**Acceptance Criteria**:
- [x] Error dialog shows command and full error message
- [x] Logs error to application log file
- [x] User returned to previous state
- [x] Common errors: merge conflicts, push rejection, network errors
- [x] Actionable error messages

**Implementation Notes**:
- Check GitResult.returncode
- Parse stderr for error details
- Show QMessageBox.critical() with details
- Log with logger.error()

---

### TASK-065: Git Auto-Stage Current File
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-055, TASK-057
**Requirements**: REQ-052
**Design Refs**: Section 2 (Git Handler)
**Files**: `src/asciidoc_artisan/ui/git_handler.py`

**Description**: Auto-stage current file on commit

**Acceptance Criteria**:
- [x] Checkbox in Quick Commit dialog
- [x] Executes git add {current_file} before commit
- [x] Only stages if file is tracked
- [x] Shows "Auto-staged: {filename}" in dialog
- [x] Enabled by default (configurable in settings)

**Implementation Notes**:
- Check file tracked: git ls-files {file}
- Execute git add {file} before commit
- Update staged files list in dialog
- Setting: settings.git_auto_stage_current

---

## Phase 5: Advanced Features

**Priority**: P1-P2 (Medium to High Priority)
**Duration**: ~35 days
**Dependencies**: Phase 1-4

### TASK-066: Search Handler
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-014, TASK-021
**Requirements**: REQ-081 to REQ-090
**Design Refs**: Section 2 (Search Handler)
**Files**: `src/asciidoc_artisan/ui/search_handler.py`

**Description**: Find and replace functionality

**Acceptance Criteria**:
- [x] SearchHandler(QObject) class
- [x] show_find_bar(), show_replace_bar() methods
- [x] find_next(text, case_sensitive, regex), find_previous()
- [x] replace_current(find_text, replace_text), replace_all()
- [x] highlight_all_matches(text), clear_highlights()
- [x] Match count shown: "{current}/{total}"
- [x] Maximum 1,000 highlights

**Implementation Notes**:
- Use QTextCursor for searching
- Compiled regex patterns for performance
- Highlight with extra selections
- Confirmation dialog for replace_all if >20 replacements

---

### TASK-067: Find Bar Integration
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-014, TASK-066
**Requirements**: REQ-081, REQ-090
**Design Refs**: Section 2 (Search Handler)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Integrate find bar into main window

**Acceptance Criteria**:
- [x] Find action (Ctrl+F) shows find bar
- [x] Replace action (Ctrl+H) shows find bar with replace field
- [x] Escape closes find bar
- [x] Find bar positioned at bottom of editor
- [x] Focus moves to find field on show
- [x] Previous search term retained

**Implementation Notes**:
- Add find bar widget above status bar
- Connect signals to search handler
- Animate show/hide with QPropertyAnimation
- Store search term in settings

---

### TASK-068: Regex Search Validation
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-066
**Requirements**: REQ-085, NFR-013
**Design Refs**: Section 6 (Input Validation)
**Files**: `src/asciidoc_artisan/ui/search_handler.py`

**Description**: Validate regex patterns and show errors

**Acceptance Criteria**:
- [x] Validate regex pattern before search
- [x] Invalid regex shows error in find bar
- [x] Error message shows regex syntax error
- [x] Supports full Python regex syntax
- [x] Captured groups highlighted

**Implementation Notes**:
- Try re.compile(pattern)
- Catch re.error and display message
- Show error with red background in find field
- Clear error on valid pattern

---

### TASK-069: Chat Manager
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-013
**Requirements**: REQ-068 to REQ-075
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_manager.py`

**Description**: AI chat orchestration with Ollama

**Acceptance Criteria**:
- [x] ChatManager(QObject) class
- [x] submit_message(text) sends to Ollama
- [x] get_context_for_mode(mode) returns context
- [x] on_response_chunk(chunk) updates chat history
- [x] on_response_complete() marks response done
- [x] clear_history() clears all messages
- [x] insert_suggestion(code) inserts at cursor
- [x] Maximum 100 messages retained

**Implementation Notes**:
- Context modes: Document (full text), Syntax (current line), General (no context), Editing (selection)
- Queue to OllamaChatWorker
- Stream chunks to chat panel
- History saved to ~/.config/asciidoc-artisan/chat_history.toon

---

### TASK-070: Ollama Chat Worker
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-007, TASK-069
**Requirements**: REQ-069, REQ-070, REQ-071, REQ-078, REQ-079
**Design Refs**: Section 3 (Ollama Chat Worker)
**Files**: `src/asciidoc_artisan/workers/ollama_chat_worker.py`

**Description**: Background worker for Ollama API streaming

**Acceptance Criteria**:
- [x] OllamaChatWorker(BaseWorker) class
- [x] _process(item) sends POST to Ollama API
- [x] Streaming response with chunks
- [x] Signals: chat_response_chunk(str), chat_response_complete()
- [x] Timeout: 60 seconds
- [x] Connection error handling

**Implementation Notes**:
- POST http://localhost:11434/api/generate
- Payload: {model, prompt, temperature, stream: true}
- Iterate response.iter_lines() for chunks
- JSON.loads each chunk and emit response text

---

### TASK-071: Ollama Integration Detection
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-069
**Requirements**: REQ-066, REQ-078
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_manager.py`

**Description**: Detect Ollama service availability

**Acceptance Criteria**:
- [x] Check http://localhost:11434/api/tags on startup
- [x] Chat panel enabled if Ollama detected
- [x] Settings option for custom Ollama host
- [x] Retry button if connection fails
- [x] Error: "Ollama service not available at {host}"

**Implementation Notes**:
- Use requests.get() with timeout=2
- Catch requests.ConnectionError
- Show notification if unavailable
- Disable chat input if unavailable

---

### TASK-072: Chat History Management
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-069
**Requirements**: REQ-072, REQ-073
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_manager.py`

**Description**: Chat history with persistence

**Acceptance Criteria**:
- [x] Maximum 100 messages retained
- [x] Oldest messages removed on overflow
- [x] History saved to TOON file on exit
- [x] History restored on startup
- [x] Clear History action with confirmation

**Implementation Notes**:
- Store messages as list of {role, content, timestamp}
- Save to ~/.config/asciidoc-artisan/chat_history.toon
- LRU eviction when max reached
- Confirmation dialog for clear

---

### TASK-073: Chat Context Modes
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-069
**Requirements**: REQ-068
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_manager.py`

**Description**: Context mode selection for AI prompts

**Acceptance Criteria**:
- [x] Modes: Document, Syntax, General, Editing
- [x] Document: full editor text
- [x] Syntax: current line only
- [x] General: no context
- [x] Editing: selected text
- [x] Mode persisted in settings
- [x] System prompt updated on mode change

**Implementation Notes**:
- Context extracted based on mode
- Prepend to user message: "Context: {context}\n\nUser: {message}"
- Mode selector in chat panel
- Setting: settings.chat_context_mode

---

### TASK-074: AI Temperature Setting
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-069, TASK-016
**Requirements**: REQ-077
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/settings_dialog.py`, `ui/chat_manager.py`

**Description**: Configurable AI temperature parameter

**Acceptance Criteria**:
- [ ] Temperature slider in Settings > AI tab
- [ ] Range: 0.0 to 2.0
- [ ] Default: 0.7
- [ ] Takes effect on next message submission
- [ ] Tooltip explains temperature effect

**Implementation Notes**:
- QSlider with range 0-200, divide by 100 for value
- Pass to Ollama as temperature parameter
- Higher = more creative, lower = more deterministic

---

### TASK-075: Insert AI Suggestion
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-069
**Requirements**: REQ-075
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_manager.py`

**Description**: Insert AI-generated code/text into editor

**Acceptance Criteria**:
- [x] "Insert" button on code blocks in chat
- [x] Inserts at current cursor position
- [x] Proper indentation preserved
- [x] Cursor positioned after inserted text
- [x] Undo operation reverses insertion

**Implementation Notes**:
- Detect code blocks in Markdown: ```language\ncode\n```
- Add "Insert" button with onclick handler
- editor.textCursor().insertText(code)
- Match indentation to current line

---

### TASK-076: Copy Chat Message
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-069
**Requirements**: REQ-074
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_panel_widget.py`

**Description**: Copy chat messages to clipboard

**Acceptance Criteria**:
- [x] Right-click context menu on messages
- [x] Copy option copies to system clipboard
- [x] Preserves Markdown formatting
- [x] Code blocks copied as plain text
- [x] Confirmation tooltip: "Copied"

**Implementation Notes**:
- QTextBrowser.setContextMenuPolicy(Qt.CustomContextMenu)
- Connect customContextMenuRequested signal
- QMenu with "Copy" action
- QApplication.clipboard().setText()

---

### TASK-077: Model Selection
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-069
**Requirements**: REQ-076
**Design Refs**: Section 2 (Chat Manager)
**Files**: `src/asciidoc_artisan/ui/chat_panel_widget.py`

**Description**: Ollama model selector

**Acceptance Criteria**:
- [x] Model selector (QComboBox) in chat panel
- [x] Lists all locally available models
- [x] Current model shown in header
- [x] Model change applies to next message
- [x] Default model: "llama2"

**Implementation Notes**:
- GET http://localhost:11434/api/tags to list models
- Populate combo box with model names
- Store selected model in settings
- Pass to Ollama as model parameter

---

### TASK-078: Chat Panel Toggle
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-013, TASK-021
**Requirements**: REQ-080
**Design Refs**: Section 2 (Main Window)
**Files**: `src/asciidoc_artisan/ui/main_window.py`

**Description**: Toggle chat panel visibility

**Acceptance Criteria**:
- [x] Toggle Chat Panel action (Ctrl+Shift+C)
- [x] Panel collapse/expand animated (200ms)
- [x] Splitter ratios adjusted: [50, 50, 0] (collapsed) or [40, 40, 20] (expanded)
- [x] Toggle state persisted in settings
- [x] Menu item checkable

**Implementation Notes**:
- QSplitter.setSizes() for collapse/expand
- QPropertyAnimation for smooth transition
- Save state to settings on toggle
- Restore state on startup

---

### TASK-079: Pandoc Worker
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-007
**Requirements**: REQ-092 to REQ-096
**Design Refs**: Section 3 (Pandoc Worker)
**Files**: `src/asciidoc_artisan/workers/pandoc_worker.py`

**Description**: Multi-format export worker using pandoc

**Acceptance Criteria**:
- [x] PandocWorker(BaseWorker) class
- [x] Supports formats: HTML, PDF, DOCX, Markdown, LaTeX
- [x] Uses pypandoc library
- [x] Progress updates via signal
- [x] Export completes within target times (HTML: 2s, PDF: 5s)
- [x] Error handling for missing dependencies

**Implementation Notes**:
- Convert AsciiDoc → Markdown → target format
- pypandoc.convert_text(md_content, target_format, format="markdown", outputfile=str(path))
- Emit progress_changed for long operations
- Check pandoc installed with shutil.which("pandoc")

---

### TASK-080: Export Handler
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-015, TASK-079
**Requirements**: REQ-091, REQ-097, REQ-098, REQ-099, REQ-100
**Design Refs**: Section 2 (Export Dialog)
**Files**: `src/asciidoc_artisan/ui/export_handler.py`

**Description**: Export orchestration handler

**Acceptance Criteria**:
- [x] ExportHandler(QObject) class
- [x] show_export_dialog() displays export options
- [x] export_to_html(path), export_to_pdf(path), etc.
- [x] Progress dialog during export
- [x] "Open after export" functionality
- [x] Settings persistence (last format, output directory)

**Implementation Notes**:
- Queue to PandocWorker
- Show QProgressDialog with cancel button
- Open with QDesktopServices.openUrl() if checked
- Error dialog if pandoc/wkhtmltopdf not found

---

### TASK-081: Export Error Handling
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-080
**Requirements**: REQ-099
**Design Refs**: Section 2 (Export Handler)
**Files**: `src/asciidoc_artisan/ui/export_handler.py`

**Description**: Comprehensive export error handling

**Acceptance Criteria**:
- [x] Error shows missing dependencies (pandoc, wkhtmltopdf)
- [x] Suggests installation commands (apt, brew, choco)
- [x] Logs error for debugging
- [x] User can retry after installing dependencies
- [x] Graceful degradation (disable unsupported formats)

**Implementation Notes**:
- Check dependencies: shutil.which("pandoc"), shutil.which("wkhtmltopdf")
- Show installation instructions in error dialog
- Disable format buttons if dependency missing
- Suggest: "Install with: sudo apt install pandoc"

---

### TASK-082: GitHub Handler
**Priority**: P2
**Effort**: L (8-16 hours)
**Dependencies**: TASK-007
**Requirements**: REQ-056 to REQ-065
**Design Refs**: Section 2 (GitHub Handler), Section 4 (GitHub CLI API)
**Files**: `src/asciidoc_artisan/ui/github_handler.py`

**Description**: GitHub CLI integration handler

**Acceptance Criteria**:
- [x] GitHubHandler(QObject) class
- [x] detect_gh_cli() checks for gh command
- [x] check_auth_status() verifies authentication
- [x] create_pr(title, body, base, head) creates pull request
- [x] list_prs() lists open pull requests
- [x] create_issue(title, body, labels) creates issue
- [x] list_issues() lists open issues

**Implementation Notes**:
- Execute gh commands with subprocess (shell=False)
- Parse JSON output with json.loads()
- Queue to dedicated GitHubWorker
- Error handling for authentication failures

---

### TASK-083: Create PR Dialog
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-082
**Requirements**: REQ-058, REQ-059
**Design Refs**: Section 2 (GitHub Handler)
**Files**: `src/asciidoc_artisan/ui/github_pr_dialog.py`

**Description**: Create pull request dialog

**Acceptance Criteria**:
- [x] CreatePRDialog(QDialog) class
- [x] Fields: title, description, base branch, head branch
- [x] Auto-fills from current branch and recent commits
- [x] Validates required fields (title, base, head)
- [x] Opens PR URL in browser on success

**Implementation Notes**:
- Get current branch: git branch --show-current
- Get recent commits: git log --oneline -5
- Execute: gh pr create --title "{title}" --body "{body}" --base {base} --head {head}
- Parse PR URL from output and open with QDesktopServices

---

### TASK-084: GitHub List PRs/Issues
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-082
**Requirements**: REQ-060, REQ-063
**Design Refs**: Section 2 (GitHub Handler)
**Files**: `src/asciidoc_artisan/ui/github_list_dialog.py`

**Description**: List pull requests and issues

**Acceptance Criteria**:
- [x] GitHubListDialog(QDialog) class
- [x] Shows: PR/issue number, title, author, status, labels
- [x] Filter by: open, closed, assigned to me
- [x] Click item shows full description
- [x] Refresh button

**Implementation Notes**:
- Execute: gh pr list --json number,title,author,state
- Execute: gh issue list --json number,title,author,state,labels
- Parse JSON and populate QTableWidget
- Double-click opens in browser

---

### TASK-085: GitHub Authentication Check
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-082
**Requirements**: REQ-057, REQ-064
**Design Refs**: Section 2 (GitHub Handler)
**Files**: `src/asciidoc_artisan/ui/github_handler.py`

**Description**: GitHub CLI authentication status

**Acceptance Criteria**:
- [x] check_auth_status() executes gh auth status
- [x] Shows "Authenticated as {username}" in status bar
- [x] Prompts login if not authenticated
- [x] Login button opens gh auth login flow
- [x] Error handling with troubleshooting steps

**Implementation Notes**:
- Execute: gh auth status
- Parse output for username
- Show login dialog if not authenticated
- Suggestions: re-authentication, network check, permission verification

---

### TASK-086: Spell Check Integration (Optional) ✅
**Priority**: P3
**Effort**: L (8-16 hours)
**Dependencies**: TASK-021
**Requirements**: Optional (not in core requirements)
**Design Refs**: N/A
**Files**: `src/asciidoc_artisan/core/spell_checker.py`, `src/asciidoc_artisan/ui/spell_check_manager.py`, `src/asciidoc_artisan/ui/spell_context_menu.py`

**Description**: Spell checking with language detection

**Acceptance Criteria**:
- [x] SpellCheckManager class (UI integration)
- [x] Uses pyspellchecker library
- [x] Underlines misspelled words with red squiggly (standard convention)
- [x] Right-click shows suggestions (up to 5)
- [x] Add to dictionary option with persistence
- [x] Language selector in settings (en, es, fr, de supported)

**Implementation Notes**:
- Core: `spell_checker.py` (170 lines) - SpellChecker class with SpellError dataclass
- UI: `spell_check_manager.py` (192 lines) - Debounced checking (500ms), F7 toggle
- Menu: `spell_context_menu.py` (114 lines) - Context menu with suggestions
- Tests: 2,105 lines of tests with comprehensive coverage
- Custom dictionary stored in settings (TOON format)

---

### TASK-087: Go to Line Dialog
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-021
**Requirements**: NFR-021
**Design Refs**: N/A
**Files**: `src/asciidoc_artisan/ui/goto_line_dialog.py`

**Description**: Go to line number dialog

**Acceptance Criteria**:
- [x] GoToLineDialog(QDialog) class
- [x] Input field for line number
- [x] Validates line number (1 to max)
- [x] Jumps to line and centers in viewport
- [x] Shortcut: Ctrl+G

**Implementation Notes**:
- QInputDialog or custom dialog
- Validate input: 1 <= line <= editor.blockCount()
- Jump with: cursor.movePosition(QTextCursor.Start), cursor.movePosition(QTextCursor.Down, n=line-1)
- Center with editor.centerCursor()

---

## Phase 6: LSP & Autocomplete

**Priority**: P1-P2 (Medium to High Priority)
**Duration**: ~15 days
**Dependencies**: Phase 1

### TASK-088: LSP Server
**Priority**: P1
**Effort**: XL (16+ hours)
**Dependencies**: TASK-001
**Requirements**: REQ-101, REQ-105, REQ-106, REQ-107, REQ-108, REQ-109
**Design Refs**: Section 4 (LSP Server)
**Files**: `src/asciidoc_artisan/lsp/server.py`

**Description**: AsciiDoc Language Server Protocol implementation

**Acceptance Criteria**:
- [x] LSPServer class with JSON-RPC 2.0 support
- [x] Starts on localhost random port
- [x] Handles: initialize, textDocument/completion, textDocument/diagnostic, textDocument/hover, textDocument/formatting, textDocument/documentSymbol
- [x] Document state synchronization
- [x] Graceful shutdown
- [x] Auto-restart on crash (max 3 attempts)

**Implementation Notes**:
- Use pygls library for LSP framework
- JSON-RPC 2.0 over stdio or socket
- Delegate to specialized providers
- Store document state in memory
- Handle client disconnect gracefully

---

### TASK-089: Completion Provider
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-088
**Requirements**: REQ-102, REQ-103, NFR-003
**Design Refs**: Section 4 (Completion Provider)
**Files**: `src/asciidoc_artisan/lsp/completion_provider.py`

**Description**: Autocomplete suggestions for AsciiDoc elements

**Acceptance Criteria**:
- [x] CompletionProvider class
- [x] Trigger characters: :, [, {, <
- [x] Attribute completions (70+ built-in)
- [x] Block delimiter completions
- [x] Cross-reference completions
- [x] Include directive completions
- [x] Response time: <50ms

**Implementation Notes**:
- Pre-compute completion trie on startup
- O(k) lookup where k = prefix length
- CompletionItem with: label, insert_text, kind, documentation
- Filter completions based on trigger character

---

### TASK-090: Diagnostics Provider
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-088, TASK-006
**Requirements**: REQ-104, NFR-002
**Design Refs**: Section 4 (Diagnostics Provider)
**Files**: `src/asciidoc_artisan/lsp/diagnostics_provider.py`

**Description**: Real-time syntax checking

**Acceptance Criteria**:
- [x] DiagnosticsProvider class
- [x] Detects syntax errors (unclosed blocks, invalid delimiters)
- [x] Detects semantic errors (broken cross-refs, missing includes)
- [x] Categorizes by severity (error, warning, info)
- [x] Error codes: E001-E104, W001-W005, I001-I003
- [x] Updates within 500ms of text change

**Implementation Notes**:
- Parse AsciiDoc content for errors
- Check for unclosed blocks with stack
- Validate cross-references and includes
- Return list of Diagnostic objects with range, severity, message, code

---

### TASK-091: Hover Provider
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-088
**Requirements**: REQ-105
**Design Refs**: Section 4 (LSP Server)
**Files**: `src/asciidoc_artisan/lsp/hover_provider.py`

**Description**: Hover information for AsciiDoc elements

**Acceptance Criteria**:
- [x] HoverProvider class
- [x] Tooltip shows element documentation
- [x] Hover delay: 500ms
- [x] Supports: attributes, cross-references, includes
- [x] Markdown formatting in tooltip

**Implementation Notes**:
- Detect element at cursor position
- Lookup documentation from built-in database
- Return Hover object with Markdown content
- Position tooltip near cursor

---

### TASK-092: Formatting Provider
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-088
**Requirements**: REQ-107
**Design Refs**: Section 4 (LSP Server)
**Files**: `src/asciidoc_artisan/lsp/formatting_provider.py`

**Description**: Document formatting (beautification)

**Acceptance Criteria**:
- [x] FormattingProvider class
- [x] Formats entire document or selection
- [x] Preserves semantic structure
- [x] Respects user indentation settings
- [x] Undo operation reverses formatting

**Implementation Notes**:
- Normalize whitespace
- Align block delimiters
- Indent nested lists consistently
- Return list of TextEdit objects with ranges and new text

---

### TASK-093: Symbol Provider
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-088
**Requirements**: REQ-108
**Design Refs**: Section 4 (LSP Server)
**Files**: `src/asciidoc_artisan/lsp/symbol_provider.py`

**Description**: Document outline with symbols

**Acceptance Criteria**:
- [x] SymbolProvider class
- [x] Shows: headings, sections, blocks, images, tables
- [x] Hierarchical tree structure
- [x] Click symbol navigates to location
- [x] Updates on document changes

**Implementation Notes**:
- Parse document for symbols
- Build hierarchical tree based on heading levels
- Return list of DocumentSymbol objects with: name, kind, range
- Update on textDocument/didChange notification

---

### TASK-094: LSP Client Integration
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-088, TASK-021
**Requirements**: REQ-101
**Design Refs**: Section 4 (LSP Server)
**Files**: `src/asciidoc_artisan/ui/lsp_client.py`

**Description**: LSP client for editor integration

**Acceptance Criteria**:
- [x] LSPClient class
- [x] Connects to LSP server
- [x] Sends textDocument/didOpen, didChange, didSave notifications
- [x] Requests completions, diagnostics, hover
- [x] Displays diagnostics in editor (wavy underlines)
- [x] Shows completion popup

**Implementation Notes**:
- JSON-RPC 2.0 client over socket
- Send notifications on text changes (debounced)
- Request completions on trigger characters
- Display diagnostics with QTextEdit extra selections

---

### TASK-095: Autocomplete Popup
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-089, TASK-094
**Requirements**: REQ-102, REQ-103
**Design Refs**: Section 4 (Completion Provider)
**Files**: `src/asciidoc_artisan/ui/autocomplete_popup.py`

**Description**: Autocomplete dropdown widget

**Acceptance Criteria**:
- [x] AutocompletePopup(QListWidget) class
- [x] Shows completions below cursor
- [x] Keyboard navigation (Up, Down, Enter, Escape)
- [x] Mouse selection
- [x] Insert completion on selection
- [x] Snippet support for templates

**Implementation Notes**:
- Position popup at cursor with mapToGlobal()
- Populate from CompletionItem list
- Enter inserts, Escape closes
- Filter items as user types

---

### TASK-096: Diagnostics Display
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: TASK-090, TASK-094
**Requirements**: REQ-104
**Design Refs**: Section 4 (Diagnostics Provider)
**Files**: `src/asciidoc_artisan/ui/lsp_client.py`

**Description**: Display diagnostics in editor

**Acceptance Criteria**:
- [x] Errors: wavy red underline
- [x] Warnings: wavy yellow underline
- [x] Info: dotted blue underline
- [x] Tooltip shows error message on hover
- [x] Gutter icon for errors/warnings
- [x] Updates in real-time

**Implementation Notes**:
- Use QTextEdit extra selections for underlines
- Custom gutter painter for icons
- Tooltip on hover with QToolTip.showText()
- Clear diagnostics on successful render

---

### TASK-097: LSP Crash Recovery
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-088, TASK-094
**Requirements**: REQ-109
**Design Refs**: Section 4 (LSP Server)
**Files**: `src/asciidoc_artisan/ui/lsp_client.py`

**Description**: Auto-restart LSP server on crash

**Acceptance Criteria**:
- [x] Detects server crash (connection lost)
- [x] Restart attempt within 2 seconds
- [x] Maximum 3 restart attempts
- [x] Error notification after failed restarts
- [x] Graceful degradation (disable LSP features)

**Implementation Notes**:
- Monitor server process with subprocess.Popen
- Check returncode periodically
- Restart with exponential backoff (2s, 4s, 8s)
- Show notification: "LSP server crashed, retrying..."

---

## Phase 7: Testing & Quality

**Priority**: P0-P1 (Critical to High Priority)
**Duration**: ~25 days
**Dependencies**: All implementation phases

### TASK-098: Unit Test Infrastructure
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: TASK-001
**Requirements**: NFR-038, AC-001
**Design Refs**: Section 9 (Testing Strategy)
**Files**: `tests/conftest.py`, `tests/unit/conftest.py`

**Description**: pytest configuration and fixtures

**Acceptance Criteria**:
- [x] pytest.ini with coverage settings
- [x] conftest.py with shared fixtures
- [x] MockParentWidget fixture for Qt testing
- [x] temp_file, temp_dir fixtures
- [x] git_repo fixture for Git tests
- [x] pytest-qt plugin configured

**Implementation Notes**:
- pytest.ini: [tool:pytest] testpaths = tests, markers, addopts
- conftest.py: @pytest.fixture scope="session" for app
- MockParentWidget avoids QApplication requirement
- Use tmp_path built-in fixture

---

### TASK-099: Core Module Unit Tests
**Priority**: P0
**Effort**: XL (16+ hours)
**Dependencies**: TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-098
**Requirements**: NFR-038, AC-001
**Design Refs**: Section 9 (Unit Testing)
**Files**: `tests/unit/core/test_*.py`

**Description**: Unit tests for core modules

**Acceptance Criteria**:
- [x] test_settings.py: load, save, get, set, migrate_from_json
- [x] test_toon_utils.py: dump, load, dumps, loads
- [x] test_file_operations.py: atomic_save_text, atomic_save_toon, read_text_file, detect_encoding
- [x] test_document_models.py: model validation
- [x] test_asciidoc_converter.py: convert_to_html, extract_syntax_errors
- [x] Coverage: >90%

**Implementation Notes**:
- Use tmp_path for file tests
- Mock file I/O errors with pytest.raises
- Test edge cases: empty files, large files, invalid encoding
- Parametrize tests with @pytest.mark.parametrize

---

### TASK-100: Handler Unit Tests
**Priority**: P0
**Effort**: XL (16+ hours)
**Dependencies**: TASK-023, TASK-055, TASK-066, TASK-069, TASK-098
**Requirements**: NFR-038, AC-001
**Design Refs**: Section 9 (Unit Testing)
**Files**: `tests/unit/ui/test_*_handler.py`

**Description**: Unit tests for handlers

**Acceptance Criteria**:
- [x] test_file_handler.py: open, save, new, recent files, auto-save
- [x] test_git_handler.py: detect repo, status, commit, pull, push
- [x] test_search_handler.py: find, replace, regex, highlights
- [x] test_chat_manager.py: submit message, context modes, history
- [x] Coverage: >90%

**Implementation Notes**:
- Use MockParentWidget for editor mock
- Mock QFileDialog with monkeypatch
- Mock worker signals with qtbot.waitSignal
- Test reentrancy guards

---

### TASK-101: Worker Unit Tests
**Priority**: P0
**Effort**: L (8-16 hours)
**Dependencies**: TASK-007, TASK-039, TASK-054, TASK-070, TASK-079, TASK-098
**Requirements**: NFR-038, AC-001
**Design Refs**: Section 9 (Unit Testing)
**Files**: `tests/unit/workers/test_*.py`

**Description**: Unit tests for workers

**Acceptance Criteria**:
- [x] test_base_worker.py: queue, cancel, process
- [x] test_git_worker.py: Git commands, shell=False validation
- [x] test_preview_worker.py: rendering, caching, timeout
- [x] test_ollama_chat_worker.py: streaming, error handling (mock Ollama)
- [x] test_pandoc_worker.py: export formats, dependencies (mock pandoc)
- [x] Coverage: >90%

**Implementation Notes**:
- Use qtbot for QThread testing
- Mock subprocess calls with unittest.mock.patch
- Mock HTTP requests with responses library
- Test timeouts with QTimer

---

### TASK-102: LSP Unit Tests
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-088, TASK-089, TASK-090, TASK-098
**Requirements**: NFR-038, AC-001
**Design Refs**: Section 9 (Unit Testing)
**Files**: `tests/unit/lsp/test_*.py`

**Description**: Unit tests for LSP components

**Acceptance Criteria**:
- [x] test_server.py: LSP server lifecycle, requests
- [x] test_completion_provider.py: completions, trigger chars, performance
- [x] test_diagnostics_provider.py: error detection, categorization
- [x] test_hover_provider.py: hover content
- [x] test_formatting_provider.py: document formatting
- [x] Coverage: >90%

**Implementation Notes**:
- Mock LSP client with JSON-RPC messages
- Test completion response time <50ms
- Validate diagnostic ranges and messages
- Test all error codes

---

### TASK-103: Integration Tests
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: All implementation tasks, TASK-098
**Requirements**: AC-001
**Design Refs**: Section 9 (Integration Testing)
**Files**: `tests/integration/test_*.py`

**Description**: Integration tests for workflows

**Acceptance Criteria**:
- [x] test_git_workflow.py: detect repo → stage → commit
- [x] test_preview_workflow.py: edit → debounce → render → display
- [x] test_file_workflow.py: open → edit → save → recent
- [x] test_chat_workflow.py: submit → stream → insert (mock Ollama)
- [x] test_export_workflow.py: export → verify output (mock pandoc)
- [x] All tests pass

**Implementation Notes**:
- Use qtbot for UI interactions
- Create temporary Git repos
- Mock external services
- Test signal/slot chains

---

### TASK-104: End-to-End Tests
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: All implementation tasks, TASK-098
**Requirements**: AC-001, AC-009
**Design Refs**: Section 9 (End-to-End Testing)
**Files**: `tests/e2e/test_*.py`

**Description**: End-to-end user workflows

**Acceptance Criteria**:
- [x] test_document_lifecycle.py: new → edit → preview → save → export
- [x] test_git_lifecycle.py: open repo file → edit → commit → push
- [x] test_chat_lifecycle.py: ask question → receive answer → insert
- [x] test_search_lifecycle.py: find → replace all → verify
- [x] All workflows complete successfully

**Implementation Notes**:
- Full application startup
- Real file I/O (temp directories)
- Mock external APIs (Ollama, GitHub)
- Screenshot on failure for debugging

---

### TASK-105: Performance Benchmarks
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: All implementation tasks, TASK-098
**Requirements**: NFR-001 to NFR-010, AC-005
**Design Refs**: Section 9 (Performance Testing)
**Files**: `tests/performance/test_*.py`

**Description**: Performance benchmarks

**Acceptance Criteria**:
- [x] test_startup_time.py: <1.0s (current: 0.27s)
- [x] test_preview_render.py: <200ms for 10,000 lines
- [x] test_autocomplete.py: <50ms response
- [x] test_file_load.py: <500ms for 10MB files
- [x] test_search.py: <500ms for 50,000 lines
- [x] All benchmarks pass

**Implementation Notes**:
- Use pytest-benchmark for timing
- Generate test documents of varying sizes
- Assert on mean, not single runs
- Run multiple iterations for accuracy

---

### TASK-106: Type Checking (mypy)
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: All implementation tasks
**Requirements**: NFR-037, AC-002
**Design Refs**: Section 8 (Type Annotations)
**Files**: `mypy.ini`, all source files

**Description**: Enforce mypy --strict type checking

**Acceptance Criteria**:
- [x] mypy.ini configured with strict mode
- [x] All source files type-annotated
- [x] mypy --strict src/ returns 0 errors
- [x] CI/CD runs mypy check
- [x] No Any types except for Qt signals

**Implementation Notes**:
- mypy.ini: [mypy] strict = true, warn_return_any = true
- Type hints on all functions and methods
- Use typing.cast() for Qt objects where needed
- Ignore Qt internal types with # type: ignore[misc]

---

### TASK-107: Code Formatting (ruff)
**Priority**: P0
**Effort**: S (2-4 hours)
**Dependencies**: All implementation tasks
**Requirements**: NFR-039, AC-004
**Design Refs**: Section 8 (Code Formatting)
**Files**: `ruff.toml`, all source files

**Description**: Enforce ruff linting and formatting

**Acceptance Criteria**:
- [x] ruff.toml configured
- [x] ruff check src/ returns 0 errors
- [x] ruff format --check src/ returns formatted
- [x] CI/CD runs ruff checks
- [x] Line length: 100 characters

**Implementation Notes**:
- ruff.toml: line-length = 100, select = ["E", "F", "I"]
- Run ruff format src/ to auto-format
- Use # noqa: {code} for intentional violations
- Integrate with pre-commit hooks

---

### TASK-108: Security Audit
**Priority**: P0
**Effort**: M (4-8 hours)
**Dependencies**: All implementation tasks
**Requirements**: NFR-011, AC-003
**Design Refs**: Section 6 (Security Design)
**Files**: All source files

**Description**: Security audit for vulnerabilities

**Acceptance Criteria**:
- [x] grep -r "shell=True" src/ returns empty
- [x] All subprocess calls use shell=False with list args
- [x] Input validation on all user inputs
- [x] File paths validated (no path traversal)
- [x] Atomic writes used everywhere
- [x] No hardcoded secrets

**Implementation Notes**:
- Run security checks in CI/CD
- Use pip-audit for dependency vulnerabilities
- Review commit message validation
- Check file permission settings (600/700)

---

### TASK-109: Documentation Coverage
**Priority**: P1
**Effort**: M (4-8 hours)
**Dependencies**: All implementation tasks
**Requirements**: NFR-040, AC-007
**Design Refs**: Section 8 (Docstrings)
**Files**: All source files

**Description**: Docstring coverage for all public APIs

**Acceptance Criteria**:
- [x] All public functions have docstrings
- [x] All public classes have docstrings
- [x] Docstrings follow Google style
- [x] Includes: parameters, return values, exceptions, examples
- [x] pydocstyle src/ returns 0 errors

**Implementation Notes**:
- Use pydocstyle for validation
- Google-style docstrings: """Summary.\n\nArgs:\n    param: desc\n\nReturns:\n    desc"""
- Add examples for complex functions
- Private methods (_method) don't require docstrings

---

### TASK-110: Test Coverage Report
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-099 to TASK-105
**Requirements**: NFR-038, AC-001
**Design Refs**: Section 9 (Test Coverage)
**Files**: `.coveragerc`, CI/CD configuration

**Description**: Generate and enforce test coverage

**Acceptance Criteria**:
- [x] pytest --cov=src --cov-report=html --cov-fail-under=90
- [x] Coverage >90% (current: 95%)
- [x] HTML coverage report generated
- [x] CI/CD fails if coverage drops below 90%
- [x] Coverage badge in README

**Implementation Notes**:
- .coveragerc: [run] source = src, [report] fail_under = 90
- Exclude Qt event loop internals from coverage
- Generate HTML report for visualization
- Upload coverage to codecov.io

---

### TASK-111: Error Scenario Tests
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-098
**Requirements**: AC-009
**Design Refs**: Section 9 (Testing Strategy)
**Files**: `tests/unit/test_errors.py`, `tests/integration/test_error_handling.py`

**Description**: Test all "Unwanted Behavior" requirements

**Acceptance Criteria**:
- [x] REQ-025: File access errors
- [x] REQ-035: Preview render timeout
- [x] REQ-040: Preview rendering errors
- [x] REQ-050: Git command timeout
- [x] REQ-051: Git command failure
- [x] REQ-064: GitHub CLI errors
- [x] REQ-078: Ollama connection errors
- [x] REQ-079: Chat request timeout
- [x] REQ-099: Export failures
- [x] REQ-109: LSP server crash

**Implementation Notes**:
- Mock errors with pytest.raises
- Mock subprocess failures
- Mock network errors with responses
- Test error messages and user guidance

---

### TASK-112: Accessibility Testing
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: All UI tasks
**Requirements**: NFR-027, AC-010
**Design Refs**: Section 8 (Implementation Guidelines)
**Files**: `tests/accessibility/test_keyboard_nav.py`, `tests/accessibility/test_screen_reader.py`

**Description**: Test accessibility features

**Acceptance Criteria**:
- [x] All UI elements keyboard accessible
- [x] Tab order follows visual layout
- [x] Focus indicators visible
- [x] Screen reader compatible (NVDA/JAWS)
- [x] Contrast ratio: minimum 4.5:1

**Implementation Notes**:
- Test keyboard navigation with qtbot
- Verify accessible names with accessibleName()
- Test with NVDA screen reader
- Use WCAG color contrast checker

---

## Phase 8: Documentation & DevOps

**Priority**: P2 (Medium Priority)
**Duration**: ~12 days
**Dependencies**: All implementation phases

### TASK-113: User Guide
**Priority**: P2
**Effort**: L (8-16 hours)
**Dependencies**: All feature tasks
**Requirements**: NFR-030
**Design Refs**: N/A
**Files**: `docs/user_guide.md`, `docs/user_guide.html`

**Description**: Comprehensive user documentation

**Acceptance Criteria**:
- [x] Getting Started section
- [x] Editor features and shortcuts
- [x] Preview and themes
- [x] Git integration tutorial
- [x] AI chat usage
- [x] Export formats
- [x] Troubleshooting
- [x] FAQ
- [x] Searchable HTML version

**Implementation Notes**:
- Write in Markdown or AsciiDoc
- Convert to HTML with pandoc
- Include screenshots and examples
- Host in docs/ directory
- Accessible from Help menu

---

### TASK-114: Keyboard Shortcuts Reference
**Priority**: P2
**Effort**: S (2-4 hours)
**Dependencies**: TASK-022
**Requirements**: NFR-030
**Design Refs**: SPEC Keyboard Shortcuts
**Files**: `docs/shortcuts.md`

**Description**: Keyboard shortcuts reference

**Acceptance Criteria**:
- [x] All shortcuts documented
- [x] Grouped by category: File, Edit, View, Tools, Git, GitHub
- [x] Platform-specific variants (Ctrl vs Cmd)
- [x] Accessible from Help menu
- [x] Printable format

**Implementation Notes**:
- Extract from SPEC Keyboard Shortcuts
- Format as table: Shortcut | Action | Description
- Include in Help menu as dialog

---

### TASK-115: Architecture Diagrams (UML)
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: All implementation tasks
**Requirements**: N/A
**Design Refs**: Section 1 (Architecture Overview)
**Files**: `docs/ARCHITECTURE.md`

**Description**: UML diagrams for architecture

**Acceptance Criteria**:
- [x] System architecture diagram
- [x] Component diagram
- [x] Sequence diagrams for key workflows
- [x] Class diagrams for major components
- [x] Data flow diagrams
- [x] All diagrams in docs/ARCHITECTURE.md

**Implementation Notes**:
- Use PlantUML or Mermaid for diagrams
- Embed diagrams in Markdown
- Include: startup sequence, preview rendering, Git commit, chat flow
- Host alongside code documentation

---

### TASK-116: CI/CD Pipeline
**Priority**: P1
**Effort**: L (8-16 hours)
**Dependencies**: TASK-098, TASK-106, TASK-107, TASK-108
**Requirements**: NFR-019
**Design Refs**: N/A
**Files**: `.github/workflows/ci.yml`, `.gitlab-ci.yml`

**Description**: Continuous integration and deployment

**Acceptance Criteria**:
- [x] CI runs on: push, pull request
- [x] Jobs: lint (ruff), type-check (mypy), test (pytest), security (pip-audit)
- [x] Matrix: Python 3.11, 3.12 on Linux, Windows, macOS
- [x] Coverage report uploaded
- [x] Build artifacts for releases
- [x] Deploy documentation on release

**Implementation Notes**:
- Use GitHub Actions or GitLab CI
- Cache dependencies (pip, npm)
- Fail on: lint errors, type errors, test failures, coverage drop
- Generate release notes with conventional commits

---

### TASK-117: Release Packaging
**Priority**: P2
**Effort**: L (8-16 hours)
**Dependencies**: All implementation tasks
**Requirements**: NFR-031
**Design Refs**: N/A
**Files**: `setup.py`, `pyproject.toml`, `MANIFEST.in`, packaging scripts

**Description**: Package for distribution

**Acceptance Criteria**:
- [x] PyPI package (pip install asciidoc-artisan)
- [x] Standalone executables (PyInstaller): Windows .exe, macOS .app, Linux AppImage
- [x] Installers: Windows MSI, macOS DMG, Debian .deb, RPM .rpm
- [x] All dependencies bundled
- [x] Desktop integration (icons, file associations)

**Implementation Notes**:
- Use PyInstaller for executables
- Include PySide6, asciidoc3, python-toon
- Desktop files for Linux (.desktop)
- Info.plist for macOS
- Installer scripts with NSIS (Windows), dpkg (Debian), rpmbuild (RPM)

---

### TASK-118: Dependency Scanning
**Priority**: P1
**Effort**: S (2-4 hours)
**Dependencies**: TASK-001
**Requirements**: NFR-019
**Design Refs**: N/A
**Files**: `.github/workflows/security.yml`, `requirements.txt`

**Description**: Automated dependency vulnerability scanning

**Acceptance Criteria**:
- [x] pip-audit runs in CI/CD
- [x] Scans dependencies for CVEs
- [x] Fails on critical vulnerabilities
- [x] Weekly scheduled scans
- [x] Dependency update PRs (Dependabot/Renovate)

**Implementation Notes**:
- Use pip-audit or safety
- GitHub Dependabot for automatic PRs
- Pin major versions, allow patch updates
- Review security advisories quarterly

---

### TASK-119: First-Run Experience
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: TASK-021
**Requirements**: NFR-029
**Design Refs**: N/A
**Files**: `src/asciidoc_artisan/ui/welcome_dialog.py`, `src/asciidoc_artisan/ui/welcome_manager.py`

**Description**: Welcome dialog for first launch

**Acceptance Criteria**:
- [x] WelcomeDialog(QDialog) shown on first run
- [x] Shows: key features, keyboard shortcuts, settings
- [x] Option to open sample document
- [x] "Don't show again" checkbox
- [x] Quick start guide link (Help > Welcome Guide)

**Implementation Notes**:
- Detect first run with settings flag
- Sample document: docs/sample.adoc
- Show only once unless user requests
- Links to user guide and shortcuts

---

### TASK-120: README & Project Setup
**Priority**: P2
**Effort**: M (4-8 hours)
**Dependencies**: All tasks
**Requirements**: N/A
**Design Refs**: N/A
**Files**: `README.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`

**Description**: Project documentation and setup

**Acceptance Criteria**:
- [x] README with: description, features, installation, usage, screenshots
- [x] CONTRIBUTING with: development setup, coding standards, pull request process
- [x] LICENSE (GPL v3 or chosen license)
- [x] CHANGELOG with version history
- [x] Code of Conduct
- [x] Issue templates (bug, feature request)

**Implementation Notes**:
- Include badges: build status, coverage, version, license
- Screenshots of main window, preview, chat
- Quick start guide in README
- Contribution guidelines follow GitHub conventions

---

## Dependency Graph

```
Foundation Phase (P0)
TASK-001 → TASK-002 → TASK-008 → TASK-021 → TASK-022
    ↓          ↓
TASK-003 → TASK-004 → TASK-023
    ↓
TASK-005 → TASK-006 → TASK-039 → TASK-040 → TASK-041 → TASK-042
    ↓
TASK-007 → TASK-054 → TASK-055
         → TASK-039
         → TASK-070
         → TASK-079
         → TASK-088

Critical Path: TASK-001 → TASK-021 → TASK-023 → TASK-042
Estimated Duration: 30 + 25 + 22 = 77 days
```

**Parallelizable Work**:
- Phase 1 + Phase 6 (LSP) can run in parallel
- UI tasks (dialogs) can run in parallel with workers
- Testing can begin as soon as components complete

---

## Sprint Recommendations

### Sprint 1 (2 weeks): Foundation
**Goal**: Core infrastructure and settings
**Tasks**: TASK-001 to TASK-020 (20 tasks)
**Deliverable**: Working application skeleton with settings

### Sprint 2 (2 weeks): Core Editor
**Goal**: Editor and file operations
**Tasks**: TASK-021 to TASK-038 (18 tasks)
**Deliverable**: Fully functional editor with file I/O

### Sprint 3 (2 weeks): Preview
**Goal**: Live preview and rendering
**Tasks**: TASK-039 to TASK-053 (15 tasks)
**Deliverable**: Real-time preview with GPU acceleration

### Sprint 4 (2 weeks): Git
**Goal**: Git integration
**Tasks**: TASK-054 to TASK-065 (12 tasks)
**Deliverable**: Git operations (commit, pull, push)

### Sprint 5 (3 weeks): Advanced Features
**Goal**: Search, chat, export, GitHub
**Tasks**: TASK-066 to TASK-087 (22 tasks)
**Deliverable**: Search/replace, AI chat, export, GitHub integration

### Sprint 6 (2 weeks): LSP
**Goal**: Autocomplete and diagnostics
**Tasks**: TASK-088 to TASK-097 (10 tasks)
**Deliverable**: Working LSP with autocomplete

### Sprint 7 (3 weeks): Testing & Quality
**Goal**: Comprehensive testing and quality gates
**Tasks**: TASK-098 to TASK-112 (15 tasks)
**Deliverable**: 95% test coverage, all quality gates pass

### Sprint 8 (2 weeks): Documentation & Release
**Goal**: Documentation and packaging
**Tasks**: TASK-113 to TASK-120 (8 tasks)
**Deliverable**: Release-ready package with documentation

---

## Traceability Matrix

| Requirement ID | Task IDs | Coverage |
|----------------|----------|----------|
| REQ-001 | TASK-021 | ✓ |
| REQ-002 | TASK-021 | ✓ |
| REQ-003 | TASK-010 | ✓ |
| REQ-004 | TASK-026 | ✓ |
| REQ-005 | TASK-026 | ✓ |
| REQ-006 | TASK-002, TASK-028 | ✓ |
| REQ-007 | TASK-038 | ✓ |
| REQ-008 | TASK-038 | ✓ |
| REQ-009 | TASK-024 | ✓ |
| REQ-010 | TASK-025 | ✓ |
| REQ-011 to REQ-022 | TASK-023, TASK-029 to TASK-038 | ✓ |
| REQ-023 | TASK-031 | ✓ |
| REQ-024 | TASK-031 | ✓ |
| REQ-025 | TASK-032 | ✓ |
| REQ-026 to REQ-040 | TASK-039 to TASK-053 | ✓ |
| REQ-041 to REQ-055 | TASK-054 to TASK-065 | ✓ |
| REQ-056 to REQ-065 | TASK-082 to TASK-085 | ✓ |
| REQ-066 to REQ-080 | TASK-069 to TASK-078 | ✓ |
| REQ-081 to REQ-090 | TASK-066 to TASK-068 | ✓ |
| REQ-091 to REQ-100 | TASK-079 to TASK-081 | ✓ |
| REQ-101 to REQ-109 | TASK-088 to TASK-097 | ✓ |
| NFR-001 to NFR-040 | Multiple tasks | ✓ |
| TC-001 to TC-010 | Multiple tasks | ✓ |

**Total Coverage**: 184/184 requirements (100%)

---

## Quality Gate Status

**Task Planning Validation**:
- ✓ All design components have implementation tasks
- ✓ All API endpoints have corresponding tasks
- ✓ Database schemas have migration tasks (N/A - file-based storage)
- ✓ Each task has clear acceptance criteria
- ✓ Dependencies form valid DAG (no circular dependencies)
- ✓ Task estimates follow consistent scale (XS/S/M/L/XL)
- ✓ Testing tasks exist for each component
- ✓ Documentation tasks included
- ✓ Deployment/DevOps tasks specified
- ✓ No "orphaned" tasks without clear purpose

**Design Coverage**: 100% (All components tasked)
**Total Tasks**: 120 (XS: 8, S: 28, M: 48, L: 28, XL: 8)
**Critical Path**: ~77 days (Foundation → Core Editor → Preview)
**Ready for Implementation**: YES

### Risk Assessment
- **High Risk**: TASK-041 (GPU acceleration fallback), TASK-088 (LSP server complexity)
- **Dependencies**: TASK-001 blocks 15+ other tasks, TASK-021 blocks 10+ tasks
- **Resource Needs**: Qt/PySide6 expertise, LSP protocol knowledge, Git/GitHub CLI experience
- **External Dependencies**: Ollama (optional), pandoc (optional), GitHub CLI (optional)

### Implementation Recommendations
1. **Start with critical path**: TASK-001 → TASK-021 → TASK-023 → TASK-042
2. **Parallelize**: LSP tasks (Phase 6) can run alongside UI tasks
3. **Test early**: Write tests alongside implementation (not after)
4. **Incremental delivery**: Each sprint produces working increment
5. **Mock external services**: Don't block on Ollama, GitHub, pandoc during development

---

**Document Version**: 1.0
**Generated**: 2025-12-24
**Task Planning Agent**: Claude Agent (Task Planning Specialist)
**Next Phase**: Implementation (Sprints 1-8)
**File Location**: /home/webbp/github/AsciiDoctorArtisan/specs/TASK.md

---

*End of Task Breakdown Document*
