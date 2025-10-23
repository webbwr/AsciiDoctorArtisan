# AsciiDoc Artisan - Complete Project Specification

**Version**: 1.1.0
**Date**: 2025-10-23
**Status**: Active Development
**Project Type**: Cross-Platform Desktop GUI Application

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Vision & Objectives](#vision--objectives)
3. [User Stories](#user-stories)
4. [Functional Requirements](#functional-requirements)
5. [Non-Functional Requirements](#non-functional-requirements)
6. [Data Model](#data-model)
7. [System Architecture](#system-architecture)
8. [Implementation Plan](#implementation-plan)
9. [Success Criteria](#success-criteria)
10. [Dependencies & Assumptions](#dependencies--assumptions)
11. [Security Considerations](#security-considerations)
12. [Testing Strategy](#testing-strategy)
13. [Technical Debt](#technical-debt)
14. [Out of Scope](#out-of-scope)

---

## Executive Summary

**AsciiDoc Artisan** is a professional cross-platform desktop application for AsciiDoc document authoring with real-time HTML preview. The application provides seamless document format conversion via Pandoc, Git version control integration, AI-enhanced format conversion using Claude API, and an intuitive user interface supporting both light and dark themes.

### Key Features

- **Real-time Preview**: Live HTML rendering of AsciiDoc content with <350ms latency
- **Format Conversion**: Import/export DOCX, Markdown, HTML, LaTeX, RST via Pandoc
- **AI-Enhanced Conversion**: Intelligent format conversion using Anthropic Claude API
- **Git Integration**: Commit, push, pull operations directly from the editor
- **Cross-Platform**: Identical functionality on Linux, macOS, Windows, and WSL
- **Data Integrity**: Atomic file writes preventing corruption
- **Session Persistence**: Restore window state, last file, and preferences

### Technical Stack

- **Language**: Python 3.11+
- **GUI Framework**: PySide6 (Qt for Python) ≥6.9.0
- **Rendering**: asciidoc3 for AsciiDoc to HTML conversion
- **Conversion**: pypandoc wrapper for Pandoc universal document converter
- **AI Integration**: anthropic SDK ≥0.40.0 for Claude API
- **Testing**: pytest, pytest-qt, pytest-cov

---

## Vision & Objectives

### Vision Statement

Provide technical writers and documentation professionals with a unified, distraction-free environment for AsciiDoc authoring that eliminates context switching between editor and browser while preserving the power of plain-text workflows.

### Primary Objectives

1. **Eliminate Context Switching**: Real-time preview removes need to manually regenerate and view output
2. **Preserve Plain Text Workflow**: AsciiDoc files remain editable in any text editor
3. **Enable Format Interoperability**: Seamless import/export across documentation formats
4. **Maintain Version Control Integration**: First-class Git support for documentation workflows
5. **Ensure Cross-Platform Consistency**: Identical experience on all major operating systems
6. **Guarantee Data Integrity**: Zero tolerance for file corruption or data loss
7. **Enhance Conversion Quality**: AI-powered conversion for complex document structures

### Target Users

- **Technical Writers**: Creating API documentation, user guides, knowledge bases
- **Software Developers**: Writing README files, design documents, project wikis
- **Documentation Teams**: Collaborating on large-scale documentation projects
- **Content Creators**: Producing structured long-form content in plain text
- **Academics**: Authoring papers, theses, and research documentation

---

## User Stories

### US-001: Real-Time Document Editing (Priority: P0 - Critical)

**As a** technical writer,
**I want** to see my AsciiDoc content rendered as HTML in real-time,
**So that** I can immediately verify formatting without switching to a browser.

**Acceptance Criteria:**
1. Preview updates within 350ms of typing
2. No UI blocking during preview rendering
3. Scroll position synchronized between editor and preview
4. Syntax errors displayed with helpful error messages
5. Preview styling matches final output expectations

---

### US-002: Document Format Conversion (Priority: P1 - High)

**As a** documentation professional,
**I want** to import DOCX files and export AsciiDoc to multiple formats,
**So that** I can integrate with teams using different documentation tools.

**Acceptance Criteria:**
1. Import DOCX files with automatic conversion to AsciiDoc
2. Export to HTML, DOCX, PDF, Markdown, LaTeX formats
3. Semantic structure preserved (headings, lists, tables, code blocks)
4. Conversion errors displayed with actionable guidance
5. Format detection automatic based on file extension
6. Binary formats (DOCX, PDF) saved to file, text formats shown in editor

---

### US-003: Git Version Control Integration (Priority: P1 - High)

**As a** developer writing documentation,
**I want** to commit and push changes without leaving the editor,
**So that** I can maintain version control workflow efficiency.

**Acceptance Criteria:**
1. Detect if current file is in a Git repository
2. Commit current file with user-provided message
3. Push commits to remote repository
4. Pull updates from remote repository
5. Clear error messages for authentication failures
6. Git operations never block the UI

---

### US-004: Session State Persistence (Priority: P2 - Medium)

**As a** regular user,
**I want** the application to remember my last opened file and window layout,
**So that** I can resume work immediately without reconfiguration.

**Acceptance Criteria:**
1. Last opened file path restored on startup
2. Window size, position, and maximization state preserved
3. Dark/light theme preference persisted
4. Editor/preview pane split ratio maintained
5. Font zoom level remembered across sessions
6. Last used directory for file dialogs retained

---

### US-005: Keyboard-Driven Workflow (Priority: P2 - Medium)

**As a** power user,
**I want** keyboard shortcuts for all major operations,
**So that** I can work efficiently without using the mouse.

**Acceptance Criteria:**
1. File operations: Ctrl+N/O/S/Shift+S (New/Open/Save/Save As)
2. Edit operations: Ctrl+F/G/Z/Y (Find/Go to Line/Undo/Redo)
3. View operations: Ctrl+D (Dark Mode), Ctrl+Plus/Minus/0 (Zoom)
4. Platform adaptation: Cmd key on macOS, Ctrl on Windows/Linux
5. Shortcuts discoverable via menu labels
6. No conflicts with system shortcuts

---

### US-006: Theme Customization (Priority: P3 - Nice to Have)

**As a** user with visual preferences,
**I want** to switch between light and dark themes,
**So that** I can work comfortably in different lighting conditions.

**Acceptance Criteria:**
1. Dark mode with high contrast (WCAG AA compliant)
2. Light mode as default theme
3. Theme toggle via F5 or Ctrl+D shortcut
4. Instant theme switching without restart
5. Theme preference persisted across sessions
6. Both themes tested for readability

---

### US-007: AI-Assisted Format Conversion (Priority: P2 - Medium)

**As a** technical writer,
**I want** AI-enhanced document conversion for complex formatting,
**So that** I can preserve semantic structure and reduce manual cleanup.

**Acceptance Criteria:**
1. Optional AI-enhanced conversion using Claude API
2. Preserves complex formatting (nested lists, tables, code blocks, admonitions)
3. Automatic fallback to Pandoc if AI unavailable or fails
4. Progress indicators during long AI operations
5. Conversion completes within 30 seconds for documents up to 50 pages
6. Clear error messages for API failures with fallback notification

---

## Functional Requirements

### Document Editing (FR-001 to FR-010)

**FR-001**: System SHALL provide a plain-text editor for AsciiDoc content with monospace font and syntax awareness.

**FR-002**: System SHALL display live HTML preview of current document content in adjacent pane.

**FR-003**: System SHALL update preview automatically when document content changes.

**FR-004**: System SHALL debounce preview updates with 350ms delay to prevent performance issues during rapid typing.

**FR-005**: System SHALL indicate unsaved changes in window title (asterisk) and modified flag.

**FR-006**: System SHALL enable word wrap in editor by default.

**FR-007**: System SHALL synchronize scroll position between editor and preview panes.

**FR-008**: System SHALL allow users to resize editor and preview panes via draggable splitter.

**FR-009**: System SHALL persist splitter position across application sessions.

**FR-010**: System SHALL render preview in background worker thread to prevent UI blocking.

---

### File Operations (FR-011 to FR-020)

**FR-011**: System SHALL open .adoc and .asciidoc files directly without conversion.

**FR-012**: System SHALL save files with Ctrl+S keyboard shortcut (Cmd+S on macOS).

**FR-013**: System SHALL provide "Save As" functionality to save document to new location.

**FR-014**: System SHALL prompt user before closing unsaved documents.

**FR-015**: System SHALL use atomic file writes (temp file + rename) to prevent corruption.

**FR-016**: System SHALL sanitize all file paths using Path().resolve() to prevent directory traversal.

**FR-017**: System SHALL validate file paths for existence and accessibility before operations.

**FR-018**: System SHALL detect file encoding automatically (default UTF-8).

**FR-019**: System SHALL preserve line ending style (LF, CRLF, CR) from original file.

**FR-020**: System SHALL update window title with current file path and modified indicator.

---

### Format Conversion (FR-021 to FR-030)

**FR-021**: System SHALL detect document format based on file extension (.docx, .md, .html, .tex, .rst).

**FR-022**: System SHALL convert DOCX files to AsciiDoc format on open.

**FR-023**: System SHALL export AsciiDoc to HTML, DOCX, PDF, Markdown, and LaTeX formats.

**FR-024**: System SHALL preserve semantic structure during conversion (headings, lists, tables, code blocks).

**FR-025**: System SHALL provide format selection dialog for export operations.

**FR-026**: System SHALL execute format conversions in background worker thread.

**FR-027**: System SHALL display conversion errors with user-friendly messages.

**FR-028**: System SHALL verify Pandoc availability on application startup.

**FR-029**: System SHALL use parameterized arguments for Pandoc subprocess (no shell interpolation).

**FR-030**: System SHALL load converted text formats into editor, save binary formats to file.

---

### Git Integration (FR-031 to FR-040)

**FR-031**: System SHALL detect if current file is in a Git repository via `git rev-parse --git-dir`.

**FR-032**: System SHALL enable Git menu items only when file is in a repository.

**FR-033**: System SHALL commit current file with user-provided commit message.

**FR-034**: System SHALL stage file automatically before commit (git add).

**FR-035**: System SHALL push committed changes to remote repository (git push).

**FR-036**: System SHALL pull updates from remote repository (git pull --rebase).

**FR-037**: System SHALL execute all Git operations in background worker thread.

**FR-038**: System SHALL use parameterized arguments for Git subprocess (no shell interpolation).

**FR-039**: System SHALL display Git operation results (success/failure) in status messages.

**FR-040**: System SHALL never store Git credentials (use system-configured credentials).

---

### User Interface (FR-041 to FR-053)

**FR-041**: System SHALL provide dark mode and light mode themes.

**FR-042**: System SHALL ensure WCAG AA contrast ratios for both themes.

**FR-043**: System SHALL persist editor font size across sessions.

**FR-044**: System SHALL support font zoom via Ctrl+Plus/Minus/0 shortcuts.

**FR-045**: System SHALL persist splitter sizes (editor/preview pane ratio) across sessions.

**FR-046**: System SHALL display status bar with file path, line/column numbers.

**FR-047**: System SHALL provide menu bar with File, Edit, Tools, Git, View, Help menus.

**FR-048**: System SHALL support platform-aware keyboard shortcuts (Ctrl on Windows/Linux, Cmd on macOS).

**FR-049**: System SHALL restore window geometry (size, position, maximization) on startup.

**FR-050**: System SHALL work identically on Linux, macOS, Windows, and WSL.

**FR-051**: System SHALL detect platform and use appropriate configuration directory (XDG/AppData/Application Support).

**FR-052**: System SHALL provide Find functionality (Ctrl+F) for searching document content.

**FR-053**: System SHALL provide Go to Line functionality (Ctrl+G) for navigation.

---

### AI-Enhanced Format Conversion (FR-054 to FR-062)

**FR-054**: System SHALL integrate Claude API for AI-enhanced document format conversion.

**FR-055**: System SHALL provide user option to enable AI-Enhanced Conversion in settings.

**FR-056**: System SHALL use Claude AI to handle complex document structures (nested lists, tables, code blocks, admonitions).

**FR-057**: System SHALL automatically fall back to standard Pandoc conversion if Claude API fails or is unavailable.

**FR-058**: System SHALL validate Anthropic API key on initialization (minimal test request).

**FR-059**: System SHALL display progress indicators during long-running AI conversion operations.

**FR-060**: System SHALL handle AI API errors gracefully with retry logic and fallback.

**FR-061**: System SHALL store Anthropic API keys securely via environment variables (ANTHROPIC_API_KEY), never in plain text configuration.

**FR-062**: System SHALL implement rate limiting protection with exponential backoff (max 3 retries) for AI API calls.

---

## Non-Functional Requirements

### Performance Requirements

**NFR-001**: Preview updates SHALL complete within 350ms of user input (95th percentile).

**NFR-002**: Application startup SHALL complete within 3 seconds to usable editor window.

**NFR-003**: UI SHALL remain responsive during document editing for files up to 10,000 lines.

**NFR-004**: Memory usage SHALL remain under 500MB for typical documents (<5000 lines).

**NFR-005**: All long-running operations (rendering, Git, Pandoc, AI API) SHALL execute in background threads.

### Reliability Requirements

**NFR-006**: File save operations SHALL be atomic to prevent corruption on crashes or interruptions.

**NFR-007**: Application SHALL never lose user data due to file write failures.

**NFR-008**: Git operations SHALL never use force flags or destructive commands without user confirmation.

**NFR-009**: Path sanitization SHALL prevent directory traversal attacks.

**NFR-010**: Subprocess calls SHALL use parameterized arguments to prevent command injection.

### Usability Requirements

**NFR-011**: 90% of users SHALL successfully complete first document editing task without documentation.

**NFR-012**: All major operations SHALL be accessible via keyboard shortcuts.

**NFR-013**: Error messages SHALL be user-friendly and actionable (no raw stack traces).

**NFR-014**: WCAG AA contrast ratios SHALL be maintained for both light and dark themes.

**NFR-015**: Application SHALL function identically on Linux, macOS, Windows with no platform-specific feature degradation.

### Maintainability Requirements

**NFR-016**: Codebase SHALL use comprehensive type hints (PEP 484) throughout.

**NFR-017**: All public classes and methods SHALL have docstrings.

**NFR-018**: Logging SHALL use structured levels (INFO, WARNING, ERROR) with no sensitive data exposure.

**NFR-019**: Code SHALL maintain 80%+ test coverage for core functionality.

**NFR-020**: External dependencies SHALL be minimized and well-justified.

---

## Data Model

### Core Entities

#### 1. Document

**Purpose**: Represents an AsciiDoc file open in the editor with associated metadata.

**Attributes**:
- `file_path: Optional[Path]` - Absolute path to document file (None for new unsaved documents)
- `content: str` - Current text content in the editor
- `modified: bool` - True if document has unsaved changes
- `encoding: str` - File encoding (default: 'utf-8')
- `line_ending: str` - Line ending style ('\\n', '\\r\\n', '\\r')

**State Transitions**:
```
New Document (unsaved)
  ↓ (user types)
Modified (unsaved)
  ↓ (user saves)
Saved Document
  ↓ (user types)
Modified (unsaved)
```

**Validation Rules**:
- `file_path` sanitized with `Path().resolve()` to prevent directory traversal
- `modified` flag set on any content change
- `encoding` must be valid Python codec name

---

#### 2. EditorState

**Purpose**: Captures current editor UI configuration and cursor position.

**Attributes**:
- `font_family: str` - Editor font family (default: monospace system font)
- `font_size: int` - Editor font size in points (default: 12)
- `zoom_level: int` - Relative zoom from base font size
- `cursor_line: int` - Current cursor line number (1-indexed)
- `cursor_column: int` - Current cursor column number (0-indexed)
- `word_wrap: bool` - Word wrap enabled/disabled (default: True)
- `tab_width: int` - Tab stop distance in spaces (default: 4)

**Persistence**: Transient (not persisted)

**Validation Rules**:
- `font_size` between 8 and 72 points
- `zoom_level` constrained to prevent excessive sizes (-5 to +10)
- `tab_width` between 2 and 8 spaces

---

#### 3. PreviewState

**Purpose**: Manages rendered HTML content and synchronization with editor.

**Attributes**:
- `html_content: str` - Current rendered HTML from AsciiDoc
- `scroll_position: int` - Preview pane vertical scroll position
- `rendering: bool` - True if background render in progress
- `last_render_time: float` - Timestamp of last successful render
- `render_error: Optional[str]` - Error message if rendering failed

**State Transitions**:
```
Idle
  ↓ (text changed)
Debounce Timer (350ms)
  ↓ (timer fires)
Rendering
  ↓ (worker completes)
Idle (with new HTML)
```

**Synchronization**:
- Preview scroll synchronized with editor scroll
- Mapping: `preview_scroll = (editor_scroll / editor_max) * preview_max`

---

#### 4. Settings

**Purpose**: Stores user preferences and persistent application state.

**Attributes**:
- `last_directory: Path` - Last directory used for file operations
- `last_file: Optional[Path]` - Last opened document path
- `git_repo_path: Optional[Path]` - Detected Git repository root
- `dark_mode: bool` - Theme preference (True = dark, False = light)
- `maximized: bool` - Window maximization state
- `window_geometry: Optional[QRect]` - Window size/position when not maximized
- `splitter_sizes: List[int]` - Editor and preview pane widths
- `font_size: int` - Persisted editor font size
- `auto_save_enabled: bool` - Auto-save feature toggle
- `auto_save_interval: int` - Auto-save interval in seconds (default: 300)
- `ai_conversion_enabled: bool` - AI-enhanced conversion option (default: False)

**Persistence**:
- Stored as JSON in platform-appropriate configuration directory:
  - Linux/WSL: `~/.config/AsciiDoc Artisan/AsciiDocArtisan.json`
  - Windows: `%APPDATA%/AsciiDoc Artisan/AsciiDocArtisan.json`
  - macOS: `~/Library/Application Support/AsciiDoc Artisan/AsciiDocArtisan.json`

**Serialization Format**:
```json
{
  "last_directory": "/home/user/documents",
  "last_file": "/home/user/documents/example.adoc",
  "git_repo_path": "/home/user/documents",
  "dark_mode": true,
  "maximized": false,
  "window_geometry": [100, 100, 1200, 800],
  "splitter_sizes": [600, 600],
  "font_size": 12,
  "auto_save_enabled": true,
  "auto_save_interval": 300,
  "ai_conversion_enabled": false
}
```

**Security Note**: Anthropic API keys are NEVER stored in Settings. API keys must be provided via `ANTHROPIC_API_KEY` environment variable per FR-061.

---

#### 5. GitRepository

**Purpose**: Represents detected Git repository state for current document.

**Attributes**:
- `repo_path: Path` - Absolute path to Git repository root
- `has_remote: bool` - True if repository has configured remote
- `remote_url: Optional[str]` - URL of remote repository
- `current_branch: str` - Name of current Git branch
- `is_dirty: bool` - True if working directory has uncommitted changes
- `ahead_count: int` - Number of local commits not pushed
- `behind_count: int` - Number of remote commits not pulled

**Detection**:
- Detected via `git rev-parse --git-dir` subprocess
- Cached until document changes

---

#### 6. ConversionJob

**Purpose**: Represents a document format conversion task managed by PandocWorker.

**Attributes**:
- `source_path: Path` - Path to source document
- `source_format: str` - Source format (docx, markdown, html, latex, rst)
- `target_format: str` - Target format (asciidoc, html, docx, pdf)
- `output_path: Optional[Path]` - Path for export output (None for import)
- `pandoc_options: List[str]` - Additional Pandoc options
- `use_ai_conversion: bool` - Use Claude AI for conversion (FR-055)
- `status: str` - Job status (pending, running, completed, failed)
- `error_message: Optional[str]` - Error details if conversion failed
- `start_time: float` - Timestamp when conversion started
- `end_time: Optional[float]` - Timestamp when conversion completed

**State Transitions**:
```
Pending
  ↓ (worker starts)
Running (AI or Pandoc)
  ↓ (subprocess completes)
Completed
  OR
  ↓ (failure)
Failed (with error_message)
```

---

#### 7. ClaudeAIClient

**Purpose**: Manages interaction with Anthropic Claude API for AI-enhanced conversion.

**Attributes**:
- `api_key: str` - Anthropic API key (from environment)
- `model: str` - Claude model (default: claude-3-5-sonnet-20241022)
- `max_retries: int` - Maximum retry attempts (default: 3)
- `timeout: int` - API request timeout in seconds (default: 60)

**Methods**:
- `validate_api_key() -> bool` - Validate API key with minimal request
- `convert_document(...) -> ConversionResult` - AI-enhanced conversion
- `estimate_tokens(text: str) -> int` - Token count estimation
- `can_handle_document(content: str) -> bool` - Size validation

**Security**:
- API key read from ANTHROPIC_API_KEY environment variable only
- Never persisted to disk or configuration files

---

### Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                         Settings                            │
│  - Persistent configuration                                 │
│  - JSON file in platform config directory                   │
└─────────────────────────────────────────────────────────────┘
         ↓ contains path to
┌─────────────────────────────────────────────────────────────┐
│                         Document                            │
│  - Current file content and metadata                        │
│  - Single instance per application                          │
└─────────────────────────────────────────────────────────────┘
         ↓ rendered by        ↓ version controlled by
┌──────────────────────┐  ┌───────────────────────────────────┐
│    PreviewState      │  │      GitRepository                │
│  - HTML rendering    │  │  - Repository metadata            │
└──────────────────────┘  └───────────────────────────────────┘
         ↓ converted by
┌─────────────────────────────────────────────────────────────┐
│                      ConversionJob                          │
│  - Format conversion tasks                                  │
│  - Managed by PandocWorker thread                           │
│  - May use ClaudeAIClient for AI conversion                 │
└─────────────────────────────────────────────────────────────┘
         ↓ may use
┌─────────────────────────────────────────────────────────────┐
│                    ClaudeAIClient                           │
│  - AI-enhanced conversion                                   │
│  - Claude API integration                                   │
└─────────────────────────────────────────────────────────────┘
```

---

### Data Persistence Strategy

**Persistent Data**:
- **Settings (JSON file)**: User preferences, session state, last opened file
- **Documents (Filesystem)**: AsciiDoc file content in user-specified locations
- **Atomicity**: Temp file + rename pattern prevents corruption

**Transient Data**:
- **EditorState**: Not persisted, reconstructed from document on open
- **PreviewState**: Not persisted, regenerated on document load
- **GitRepository**: Not persisted, detected fresh each session
- **ConversionJob**: Not persisted, ephemeral task objects

---

## System Architecture

### Architecture Pattern

**Model-View-Controller (MVC)** with **Event-Driven GUI**

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Window (View)                     │
│  ┌────────────────────┐ ┌─────────────────────────────────┐ │
│  │   Editor Pane      │ │      Preview Pane               │ │
│  │  (QPlainTextEdit)  │ │    (QTextBrowser)               │ │
│  │  - Syntax aware    │ │  - HTML rendering               │ │
│  │  - Word wrap       │ │  - Auto-refresh                 │ │
│  └────────────────────┘ └─────────────────────────────────┘ │
│  Menu: File | Edit | Tools | Git | View | Help             │
│  Status: File path | Modified | Line/Col                    │
└─────────────────────────────────────────────────────────────┘
                            ↓ Events
┌─────────────────────────────────────────────────────────────┐
│                    Controller Layer                         │
│         AsciiDocEditor (Main Controller)                    │
│  - Event handlers (open, save, convert, commit)            │
│  - State management (current file, modified flag)          │
└─────────────────────────────────────────────────────────────┘
                            ↓ Delegates
┌─────────────────────────────────────────────────────────────┐
│                    Worker Threads (Model)                   │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐   │
│  │PreviewWorker │ │  GitWorker   │ │  PandocWorker     │   │
│  │- Render HTML │ │- Commit      │ │- Convert formats  │   │
│  │- Debounce    │ │- Push/Pull   │ │- AI conversion    │   │
│  └──────────────┘ └──────────────┘ └───────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ Uses
┌─────────────────────────────────────────────────────────────┐
│               External Dependencies (Services)              │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐   │
│  │ AsciiDoc3API │ │  Git CLI     │ │  Pandoc CLI       │   │
│  │ ClaudeClient │ │  subprocess  │ │  pypandoc wrapper │   │
│  └──────────────┘ └──────────────┘ └───────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Diagrams

#### Editor → Preview Flow

1. User types in editor → `textChanged` signal
2. Debounce timer (350ms) starts/restarts
3. Timer fires → `_on_text_changed()` handler
4. Content queued to `PreviewWorker` thread
5. Worker renders HTML via `AsciiDoc3API`
6. Worker emits `preview_ready` signal
7. Main thread updates `QTextBrowser`
8. Scroll synchronization applied

#### File Save Flow

1. User presses Ctrl+S → `_on_save()` handler
2. Path validation and sanitization
3. Content written to temporary file `{filename}.tmp`
4. Verify write successful
5. Atomic rename: `os.rename(tmp, target)`
6. Update window title, set modified=False
7. Persist file path to settings

#### AI-Enhanced Conversion Flow

1. User selects conversion with AI enabled
2. Check ANTHROPIC_API_KEY environment variable
3. Create ClaudeClient instance
4. Validate document size (<50k tokens)
5. Queue to PandocWorker with use_ai_conversion=True
6. Worker calls ClaudeClient.convert_document()
7. AI conversion with retry logic (max 3 attempts)
8. On failure → fallback to standard Pandoc
9. Emit completion signal with result
10. Main thread displays result or error

---

### Key Design Decisions

#### 1. Worker Threads for Long Operations

**Decision**: Use QThread-based workers for rendering, Git, Pandoc, AI API
**Rationale**: Prevents UI blocking, maintains responsiveness
**Trade-off**: Added complexity vs. non-blocking UI

#### 2. Debounced Preview Updates

**Decision**: 350ms timer-based debouncing
**Rationale**: Reduces CPU load during rapid typing, meets latency requirement
**Trade-off**: Slight delay vs. CPU efficiency

#### 3. Atomic File Writes

**Decision**: Temp file + rename pattern
**Rationale**: Non-negotiable data integrity requirement
**Trade-off**: Extra I/O vs. corruption prevention

#### 4. AI Fallback Architecture

**Decision**: Try AI first, automatically fallback to Pandoc
**Rationale**: Best conversion quality while maintaining reliability
**Trade-off**: Increased complexity vs. enhanced user experience

#### 5. Environment Variable API Keys

**Decision**: ANTHROPIC_API_KEY from environment only
**Rationale**: Security best practice, prevents credential leakage
**Trade-off**: User setup complexity vs. security guarantee

---

## Implementation Plan

### Completed Phases

#### Phase 0-9: Foundation to v1.0.0-beta ✅ Complete

- Core editor and preview functionality
- File operations with atomic writes
- Format conversion via Pandoc
- Git integration
- UI theming (dark/light modes)
- Keyboard shortcuts
- Session persistence
- Cross-platform testing
- Complete documentation

#### Phase 10: AI Integration ✅ Complete (v1.1.0)

**Completed Work:**
1. Added AI requirements to specification (FR-054 to FR-062)
2. Created `claude_client.py` module (333 lines)
   - ClaudeClient class with full Anthropic SDK integration
   - API key validation and token estimation
   - Exponential backoff retry logic (max 3 attempts)
   - Progress callback support
3. Enhanced PandocWorker with AI integration
   - Added `use_ai_conversion` parameter
   - Implemented `_try_ai_conversion()` method
   - Automatic fallback to Pandoc on AI failures
4. Updated Settings dataclass
   - Added `ai_conversion_enabled` field
   - Updated tests (all 5 tests passing)
5. Added anthropic ≥0.40.0 to dependencies

**AI Features Implemented:**
- Complex formatting preservation (nested lists, tables, code blocks)
- Rate limiting protection with exponential backoff
- Graceful degradation to Pandoc on failures
- Progress indicators for long operations
- Secure API key handling (environment variables only)

---

### In Progress

#### Phase 11: Test Suite Implementation (In Progress)

**Priority**: HIGH - Constitution requirement

**Tasks:**
1. ✅ Unit tests for Settings dataclass (5 tests passing)
2. ✅ Unit tests for file operations (9 tests passing)
3. ⏳ Unit tests for claude_client module (pending)
4. ⏳ Integration tests for Pandoc conversion (pending)
5. ⏳ Integration tests for Git operations (pending)
6. ⏳ Integration tests for AI conversion with mocked API (pending)
7. ⏳ GUI tests with pytest-qt (pending)
8. ⏳ Performance benchmarks (pending)

**Acceptance Criteria:**
- 80%+ code coverage for core functionality
- All critical paths tested (save, render, convert, AI)
- Platform-specific tests pass on Linux, macOS, Windows

---

### Planned

#### Phase 12: UI for AI Conversion (Planned)

**Tasks:**
1. Add checkbox for "AI-Enhanced Conversion" in Tools→Export dialog
2. Add checkbox for "AI-Enhanced Conversion" in File→Open dialog
3. Display AI conversion progress in status bar
4. Show fallback notification when AI unavailable
5. Add API key setup guidance in Help menu

#### Phase 13: Technical Debt Resolution (Planned)

**Tasks:**
1. Replace deprecated Qt HighDPI attributes
2. Refactor monolith if exceeds 3000 LOC
3. Improve error message consistency
4. Comprehensive logging for diagnostics

---

## Success Criteria

### User Experience Metrics (SC-001 to SC-010)

**SC-001**: Users can edit documents with live preview updates occurring within 250ms of input

**SC-002**: Application starts in under 3 seconds from launch to usable editor window

**SC-003**: Users can edit documents exceeding 10,000 lines without UI freezing or lag

**SC-004**: Application successfully opens, edits, and saves AsciiDoc files without data loss or corruption

**SC-005**: Format conversion preserves document structure (headings, lists, tables) with 95% fidelity

**SC-006**: Users can complete common workflows (open, edit, save, commit) entirely via keyboard shortcuts

**SC-007**: 90% of users successfully complete their first document editing task without consulting documentation

**SC-008**: Application functions identically on Linux, macOS, and Windows with no platform-specific feature degradation

**SC-009**: Session state (last file, window geometry, theme) persists correctly across 99% of application restarts

**SC-010**: Git commit operations complete successfully without data loss in 100% of cases where repository is valid

---

### AI Conversion Metrics (SC-011 to SC-014)

**SC-011**: AI-enhanced conversion reduces manual cleanup time by 70% compared to standard Pandoc conversion for complex documents

**SC-012**: AI conversion successfully handles 95% of complex formatting scenarios (nested lists, tables, code blocks) without manual intervention

**SC-013**: AI conversion completes within 30 seconds for documents up to 50 pages

**SC-014**: AI conversion falls back to standard Pandoc seamlessly within 5 seconds if API fails

---

### Business/Product Metrics (SC-015 to SC-018)

**SC-015**: Users report improved productivity compared to separate editor + preview tool workflows (measured via user surveys)

**SC-016**: Technical writers can migrate from proprietary documentation tools within one day of using the application

**SC-017**: Support requests related to data loss or corruption remain under 0.1% of user base

**SC-018**: Users successfully convert documents between formats on first attempt 85% of the time (95% with AI assistance)

---

### Technical Metrics (SC-019 to SC-022)

**SC-019**: Code maintains 80%+ test coverage for core functionality

**SC-020**: Zero critical security vulnerabilities (path traversal, command injection, API key exposure) in production releases

**SC-021**: Memory usage remains under 500MB for typical documents (<5000 lines)

**SC-022**: Application passes linting (Ruff) and type checking (mypy strict) with zero warnings

---

## Dependencies & Assumptions

### External Dependencies

**Core Dependencies:**
- **Python 3.11+**: Core runtime environment
- **PySide6 ≥6.9.0**: Qt bindings for GUI framework
- **asciidoc3**: AsciiDoc to HTML conversion engine
- **pypandoc**: Python wrapper for Pandoc document converter
- **Pandoc**: Universal document converter (external system dependency)
- **Git**: Version control system (optional, for Git integration features)

**AI Dependencies:**
- **anthropic ≥0.40.0**: Anthropic Python SDK for Claude AI integration
- **Anthropic API Key**: Required for AI-enhanced format conversion (user-provided via environment)

**Testing Dependencies:**
- **pytest ≥7.4.0**: Testing framework
- **pytest-qt ≥4.2.0**: GUI testing support
- **pytest-cov ≥4.1.0**: Coverage reporting

---

### Assumptions

**A-001**: Users have Python 3.11 or higher installed on their system

**A-002**: Users have display environment configured (X11/WSLg on Linux, native on macOS/Windows)

**A-003**: Users who want document conversion have Pandoc installed separately

**A-004**: Users who want Git integration have Git configured with valid credentials

**A-005**: Target users are technical enough to use command-line installation for dependencies

**A-006**: Documents primarily use standard AsciiDoc syntax without heavy use of advanced extensions

**A-007**: Users have at least 4GB RAM available for comfortable application performance

**A-008**: Display resolution is at least 1280x720 for proper UI layout

**A-009**: Users accept open-source MIT license terms for the application

**A-010**: Network connectivity is available for Git push/pull operations but not required for core editing

**A-011**: Users who want AI-enhanced conversion provide their own Anthropic API key and accept associated usage costs

---

### Constraints & Limitations

**C-001**: PDF export requires Pandoc with LaTeX backend installed separately

**C-002**: Some advanced AsciiDoc features may have limited preview support based on asciidoc3 capabilities

**C-003**: Git integration provides basic commit/push/pull operations but not advanced Git features (rebasing, cherry-picking, etc.)

**C-004**: Format conversion fidelity depends on Pandoc capabilities and may lose some formatting details

**C-005**: Application is designed for single-user, single-file editing (not multi-user collaboration)

**C-006**: AI-enhanced conversion requires valid Anthropic API key and incurs usage costs based on document size

**C-007**: AI conversion may be rate-limited by Anthropic API and requires internet connectivity

**C-008**: AI conversion quality depends on Claude model capabilities and may vary with complex or domain-specific content

---

## Security Considerations

### Path Validation & Safety

**Requirement**: All file paths must be sanitized to prevent directory traversal attacks.

**Implementation**:
```python
def sanitize_path(path_str: str) -> Optional[Path]:
    """Sanitize file path to prevent directory traversal."""
    path = Path(path_str).resolve()
    if ".." in path.parts:
        return None
    return path
```

**Applied To**:
- All file open/save operations
- Configuration file paths
- Git repository paths

---

### Atomic Write Pattern

**Requirement**: All file writes must be atomic to prevent corruption.

**Implementation**:
```python
def atomic_save(file_path: Path, content: str) -> bool:
    """Atomically save content using temp file + rename."""
    temp_path = file_path.with_suffix('.tmp')
    try:
        temp_path.write_text(content, encoding='utf-8')
        temp_path.replace(file_path)  # Atomic rename
        return True
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        return False
```

**Applied To**:
- All document save operations
- Configuration file writes

---

### Command Injection Prevention

**Requirement**: External commands must use parameterized arguments, never shell interpolation.

**Implementation**:
```python
# CORRECT: Parameterized arguments
subprocess.run(['git', 'commit', '-m', user_message], check=True)

# WRONG: Shell interpolation (vulnerable)
subprocess.run(f"git commit -m '{user_message}'", shell=True)
```

**Applied To**:
- All Git subprocess calls
- All Pandoc subprocess calls

---

### API Key Security

**Requirements**:
- API keys stored securely via environment variables only (FR-061)
- Never persisted to disk or configuration files
- Error messages sanitized to avoid exposing API keys

**Implementation**:
- Anthropic API keys read from `ANTHROPIC_API_KEY` environment variable
- Settings dataclass explicitly excludes API key fields
- ClaudeClient error handling sanitizes API error messages
- Documentation warns users about cloud processing

**Applied To**:
- ClaudeClient initialization
- ConversionJob with AI option
- Error logging and user messages

---

### Document Privacy

**Requirements**:
- Warn users that documents are sent to Claude API (cloud processing)
- Validate documents for sensitive content before AI conversion
- Provide opt-out mechanism (AI conversion is optional)

**Implementation**:
- `ai_conversion_enabled` setting defaults to False
- User must explicitly enable AI conversion
- Documentation includes privacy considerations
- Future: Add sensitive content detection heuristics

---

### Rate Limiting & API Safety

**Requirements**:
- Implement exponential backoff for rate limit errors
- Prevent account suspension due to excessive requests
- Graceful degradation when API unavailable

**Implementation**:
- Exponential backoff: 2^attempt seconds (max 3 retries)
- Rate limit detection via `RateLimitError` exception
- Automatic fallback to Pandoc on persistent failures
- Progress indicators keep user informed

---

## Testing Strategy

### Unit Tests

**Scope**: Core functionality (file I/O, conversion, configuration)

**Coverage**:
- Settings dataclass serialization/deserialization ✅ (5 tests passing)
- File operations (atomic writes, path sanitization) ✅ (9 tests passing)
- ClaudeClient methods (pending)
- Format detection logic (pending)
- Git command construction (pending)

**Tools**: pytest, pytest-cov

---

### Integration Tests

**Scope**: External tool integration

**Coverage**:
- Pandoc conversion workflows (pending)
- Git operations (commit, push, pull) (pending)
- AI API integration with mocked responses (pending)
- AsciiDoc rendering (pending)
- Cross-module interactions (pending)

**Mocking Strategy**:
- Mock Anthropic API responses for AI tests
- Mock Git subprocess for deterministic tests
- Mock Pandoc subprocess for format tests

---

### GUI Tests

**Scope**: Critical user workflows using pytest-qt

**Coverage**:
- Document editing and preview (pending)
- File open/save dialogs (pending)
- Theme switching (pending)
- Keyboard shortcuts (pending)
- Menu interactions (pending)

**Tools**: pytest-qt, QTest

---

### Platform Tests

**Scope**: Verify behavior on Linux, macOS, Windows

**Coverage**:
- Platform-specific configuration paths
- Keyboard shortcut adaptations (Ctrl vs Cmd)
- Display rendering and scaling
- File path handling differences

**Manual Testing**: Required for each platform

---

### Performance Tests

**Scope**: Measure latency, memory, startup time

**Metrics**:
- Preview update latency (<350ms requirement)
- Memory usage for typical documents (<500MB)
- Startup time (<3 seconds)
- AI conversion time (<30 seconds for 50 pages)
- Large document responsiveness (10,000 lines)

**Tools**: pytest-benchmark, memory_profiler, custom profiling

---

### Security Tests

**Scope**: Validate security implementations

**Coverage**:
- Path traversal prevention
- Command injection prevention
- API key exposure detection
- Atomic write integrity
- Credential storage validation

**Tools**: Manual security review, automated linting

---

## Technical Debt

### Current Technical Debt

| Debt Item | Impact | Priority | Mitigation Plan |
|-----------|--------|----------|-----------------|
| Test Coverage | Medium - No automated testing for GUI, workers, AI | HIGH | Implement pytest suite with pytest-qt; Start with critical paths |
| Deprecation Warnings | Low - Qt HighDPI attributes deprecated | LOW | Replace deprecated Qt APIs in future Qt upgrade |
| Single-File Monolith | Medium - adp_windows.py at 2,378 lines | MEDIUM | Refactor into modules when >3000 LOC |
| Hard-Coded Strings | Low - Not internationalized | LOW | Add i18n/l10n if international userbase emerges |
| AI UI Integration | Medium - No UI controls for AI option yet | HIGH | Add checkboxes in conversion dialogs |

---

## Out of Scope

**The following capabilities are explicitly NOT included in this specification:**

❌ **Multi-file project management**: No project browser or workspace management
❌ **Real-time collaboration**: No concurrent editing with multiple users
❌ **Cloud integration**: No built-in cloud storage or synchronization
❌ **Spell checking or grammar analysis**: Users should use external tools
❌ **Custom AsciiDoc extensions or plugins**: Standard AsciiDoc syntax only
❌ **Advanced Git features**: Branching, merging, rebasing handled outside application
❌ **PDF editing or annotation**: PDF is export-only target
❌ **Custom themes beyond light/dark**: No user-customizable color schemes
❌ **Mobile or web versions**: Desktop application only
❌ **Telemetry or analytics**: No usage tracking or data collection
❌ **Scroll synchronization**: Not implemented (nice-to-have)
❌ **Pane maximization**: Splitter is sufficient
❌ **Font size persistence beyond zoom**: Users can zoom
❌ **Auto-save configuration UI**: Hardcoded 5 minutes

---

## Appendix: Version History

### v1.1.0 (2025-10-23)
- Added AI-assisted format conversion (FR-054 to FR-062)
- Added User Story 7 for AI conversion
- Added AI success criteria (SC-011 to SC-014)
- Integrated Anthropic Claude API via anthropic SDK ≥0.40.0
- Implemented ClaudeClient with retry logic and fallback
- Enhanced PandocWorker with AI conversion support
- Updated Settings with ai_conversion_enabled field
- Added comprehensive security requirements for API keys
- Updated testing strategy for AI integration

### v1.0.0 (2025-10-22)
- Initial complete specification
- Core editing and preview functionality
- Format conversion via Pandoc
- Git version control integration
- Cross-platform support (Linux, macOS, Windows, WSL)
- Dark/light themes
- Session persistence
- Complete documentation

---

**Specification Version**: 1.1.0
**Last Updated**: 2025-10-23
**Approved By**: Project Maintainer
**Status**: Active Development - AI Integration Complete, Test Suite In Progress
**Next Steps**: Complete test suite, add UI for AI conversion option, resolve technical debt

---

*This consolidated specification supersedes all previous specification documents:*
- *project-specification.md (v1.0.0)*
- *data-model.md*
- *implementation-plan.md*
- *project-specification-KISS.md (rejected alternative)*
