# Project Specification: AsciiDoc Artisan

**Feature Branch**: `main`
**Created**: 2025-10-22
**Status**: Complete - Production v1.0.0-beta
**Scope**: Complete desktop application for AsciiDoc document authoring with live preview and multi-format conversion

## Executive Summary

AsciiDoc Artisan is a professional-grade, cross-platform desktop application that enables users to author, edit, and convert AsciiDoc documents with real-time HTML preview. The application provides seamless integration with Git version control, comprehensive document format conversion via Pandoc, and an intuitive user interface supporting both light and dark themes.

**Target Users**: Technical writers, documentation engineers, content creators, and software developers who need professional AsciiDoc authoring tools.

**Core Value Proposition**: Unified environment for AsciiDoc document creation that combines powerful editing capabilities with instant visual feedback, eliminating context switching between editor and preview tools.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Edit AsciiDoc Documents with Live Preview (Priority: P1)

A technical writer opens the application to create documentation for a software project. They write AsciiDoc markup in the editor and immediately see the rendered HTML output in the adjacent preview pane. As they type, the preview updates within 250ms, providing instant visual feedback on document structure, formatting, and content presentation. The user can edit the document in the Edit pane (AsciiDoc markup) and in the Preview pane (WYSIWYG); both panes synchronize document content, so the user can always see both the source and the published output.   

**Why this priority**: This is the core value proposition. Without reliable editing and preview, the application has no primary purpose. This story represents the minimal viable product.

**Independent Test**: Can be thoroughly tested by launching the application, typing AsciiDoc content in the editor pane, and verifying that the preview pane updates within 250ms, showing properly rendered HTML. Delivers immediate value as a standalone AsciiDoc editor with preview.

**Acceptance Scenarios**:

1. **Given** the application is running with an empty document, **When** the user types AsciiDoc content including headings, lists, and formatting, **Then** the preview pane displays the correctly rendered HTML within 250ms
2. **Given** the user has a document open with content, **When** they make edits to any section, **Then** the preview updates to reflect the changes without losing scroll position
3. **Given** the user is editing a large document (>10,000 lines), **When** they type or scroll, **Then** the application remains responsive without UI freezing
4. **Given** the user has the application in dark mode, **When** viewing the preview, **Then** the preview content displays with appropriate contrast and theme consistency

---

### User Story 2 - Open and Save AsciiDoc Files (Priority: P1)

A documentation engineer needs to open existing AsciiDoc files from their project repository and save changes. They use File→Open to browse to their documentation folder, select a .adoc file, and it opens in the editor with the preview automatically updated. After making changes, they save the file with Ctrl+S, and the application persists the changes atomically to prevent data corruption. The user can also open a GitHub Markdown (MD) file, a Microsoft Word (DOCX) file, or an Adobe Acrobat (PDF) file. These file formats will be automatically converted to the AsciiDoctor (ADOC) files in the background. 

**Why this priority**: File I/O is fundamental to any editor. Without reliable file operations, users cannot work with their existing documentation or preserve their work.

**Independent Test**: Can be tested by creating a test .adoc file externally, opening it in the application, making edits, saving, and verifying the changes persist correctly. Also test by attempting to save during system interruptions to verify atomic write protection.

**Acceptance Scenarios**:

1. **Given** the user selects File→Open, **When** they browse to and select a .adoc file, **Then** the file opens in the editor with content displayed and preview rendered
2. **Given** the user has an unsaved document with changes, **When** they attempt to close or open another file, **Then** the application prompts to save changes
3. **Given** the user is editing a document, **When** they press Ctrl+S (or Cmd+S on macOS), **Then** the file saves atomically and the title bar updates to remove the modified indicator
4. **Given** the user creates a new document, **When** they save for the first time, **Then** a save dialog appears, allowing them to choose a location and filename with the .adoc extension by default
5. **Given** the application loses power during save, **When** the system restarts, **Then** the file contains either the complete previous version or the complete new version (no partial writes or corruption)

---

### User Story 3 - Convert Documents Between Formats (Priority: P2)

A content creator receives documentation in a GitHub Markdown (.md), Word format (.docx), or Adobe Acrobat (.pdf) format that needs to be converted to AsciiDoc for version control. They open the initial file through File→Open, and the application automatically converts it to AsciiDoc markup while preserving structure, headings, lists, and formatting. They can then edit in AsciiDoc format and export back to various formats (MD, HTML, DOCX, PDF) via Tools→Export.

**Why this priority**: Format interoperability enables migration from other documentation systems and collaboration with non-AsciiDoc users. This significantly expands the application's utility and addressable use cases.

**Independent Test**: Can be tested by importing various document formats (DOCX, Markdown, HTML), verifying conversion fidelity, editing the converted content, and exporting to different formats. Delivers value as a document conversion tool even without other features.

**Acceptance Scenarios**:

1. **Given** the user selects File→Open with file type "All Supported Formats", **When** they select a .docx file, **Then** the application converts it to AsciiDoc and displays both editor and preview
2. **Given** the user has a Markdown (.md) file, **When** they open it, **Then** the content converts to AsciiDoc syntax while preserving headings, lists, code blocks, and links
3. **Given** the user has an AsciiDoc document open, **When** they select Tools→Export As→HTML, **Then** the application exports a standalone HTML file with embedded styles
4. **Given** Pandoc is not installed, **When** the user attempts to open a DOCX file, **Then** the application displays a clear error message with instructions to install Pandoc
5. **Given** a complex document with tables and images, **When** converting between formats, **Then** the application preserves semantic structure with graceful degradation for unsupported elements

---

### User Story 4 - Git Version Control Integration (Priority: P2)

A software developer maintains documentation alongside code in a Git repository. They edit documentation in AsciiDoc Artisan, and when ready to commit changes, they select Git→Commit, enter a commit message, and the application stages and commits the current file. They can also pull the latest changes and push to the remote repository without leaving the editor.

**Why this priority**: Version control integration eliminates context switching to a terminal or separate Git GUI tools. For developers, this is a high-value workflow enhancement but not essential for basic editing.

**Independent Test**: Can be tested by opening a file in a Git repository, making changes, committing via Git menu, and verifying the commit appears in git log. Delivers value as integrated version control for documentation workflows.

**Acceptance Scenarios**:

1. **Given** the current file is in a Git repository, **When** the user makes changes and selects Git→Commit, **Then** a dialog prompts for a commit message
2. **Given** the user enters a commit message and confirms, **When** the commit executes, **Then** the file is staged and committed with the provided message
3. **Given** the repository has a remote configured, **When** the user selects Git→Push, **Then** local commits are pushed to the remote without requiring command-line interaction
4. **Given** the user selects Git→Pull, **When** there are remote changes, **Then** the application pulls changes and reloads the current file if affected
5. **Given** the file is not in a Git repository, **When** the user opens the Git menu, **Then** Git commands are disabled with a message indicating no repository detected

---

### User Story 5 - Persistent Session and Preferences (Priority: P3)

A user closes AsciiDoc Artisan after working on documentation. The next time they launch the application, it automatically reopens the last file and Git repository they were editing, restores the window size and position, and applies their preferred theme (dark/light). Their font size, zoom level, and splitter position between editor and preview are preserved.

**Why this priority**: Session persistence significantly improves user experience and workflow continuity, but is not essential for basic functionality. Users can manually reopen files and reconfigure the layout if needed.

**Independent Test**: This can be tested by configuring the window layout, zoom level, and theme, closing the application, and verifying that all settings restore correctly on the next launch. Delivers comfort and efficiency improvements.

**Acceptance Scenarios**:

1. **Given** the user has a file open when they close the application, **When** they relaunch, **Then** the same file reopens at the same scroll position
2. **Given** the user has set a custom window size and position, **When** they relaunch, **Then** the window restores to the exact dimensions and screen location
3. **Given** the user has enabled dark mode, **When** they restart the application, **Then** dark mode remains active
4. **Given** the user has adjusted editor font size to 16pt, **When** they reopen the application, **Then** the editor font size remains 16pt
5. **Given** the user has adjusted the splitter between editor and preview to 60/40, **When** they restart, **Then** the splitter position is preserved

---

### User Story 6 - Keyboard Shortcuts and Productivity Features (Priority: P3)

An experienced user relies on keyboard shortcuts to achieve an efficient workflow. They use Ctrl+N for a new document, Ctrl+O to open, Ctrl+S to save, Ctrl+F to find text, Ctrl+G to go to a specific line, Ctrl+D to toggle dark mode, and Ctrl+/- to adjust font zoom. All shortcuts follow platform conventions (Cmd on macOS, Ctrl on Windows/Linux).

**Why this priority**: Keyboard shortcuts dramatically improve productivity for power users but are not required for basic functionality. Users can access all features through menus.

**Independent Test**: Can be tested by executing each keyboard shortcut and verifying the expected action occurs. Delivers efficiency gains for regular users.

**Acceptance Scenarios**:

1. **Given** the application is active, **When** the user presses Ctrl+N (Cmd+N on macOS), **Then** a new empty document opens
2. **Given** the user has a document open, **When** they press Ctrl+F, **Then** a find dialog appears
3. **Given** the user presses Ctrl+G, **When** they enter a line number, **Then** the editor scrolls to and highlights that line
4. **Given** the current font size is 12pt, **When** the user presses Ctrl+Plus three times, **Then** the font size increases to 15pt
5. **Given** the application is in light mode, **When** the user presses Ctrl+D or F5, **Then** the theme switches to dark mode instantly

---

### Edge Cases

- **What happens when the user opens a corrupt or invalid AsciiDoc file?**
  The application displays the raw content in the editor and shows an error message in the preview pane, indicating a parsing failure with details about the issue location.

- **How does the system handle opening extremely large files (>100MB)?**
  The application displays a warning about potential performance impact and offers to open in read-only mode with preview disabled, or to proceed with standard editing (which may be slower).

- **What happens when Pandoc is not installed but the user tries to open a DOCX file?**
  The application detects the missing dependency on startup and, when attempting conversion, displays a clear error message with installation instructions and a link to the Pandoc download page.

- **How does the application handle file conflicts when pulling from Git?**
  If Git pull results in merge conflicts, the application detects this and displays a message instructing the user to resolve conflicts in their Git client before continuing.

- **What happens when the user modifies a file externally while it's open in the application?**
  The application detects the external change and prompts the user to reload the file or keep their current unsaved changes.

- **How does the system handle missing fonts or rendering issues?**
  The application falls back to system default monospace fonts and logs the issue. Preview rendering uses browser defaults if custom fonts fail to load.

- **What happens when saving to a location without write permissions?**
  The application displays an error dialog indicating insufficient permissions and offers to save to a different location via Save As dialog.

## Requirements *(mandatory)*

### Functional Requirements

#### Document Editing & Preview

- **FR-001**: System MUST provide a text editor with syntax highlighting optimized for AsciiDoc markup
- **FR-002**: System MUST display a live HTML preview of the AsciiDoc content updated within 250ms of user input
- **FR-003**: System MUST provide a button in the Edir and Preview pane to toggle between a full pane and split-pane views.
- **FR-004**: System MUST support word wrap and configurable tab stops (4 spaces default)
- **FR-005**: System MUST debounce preview updates to prevent UI blocking during rapid typing
- **FR-006**: System MUST maintain scroll synchronization between editor and preview panes
- **FR-007**: System MUST provide find and replace functionality with Ctrl+F keyboard shortcut
- **FR-008**: System MUST provide "go to line" functionality with Ctrl+G keyboard shortcut

#### File Operations

- **FR-009**: System MUST support opening .adoc and .asciidoc files natively
- **FR-010**: System MUST perform atomic writes to prevent file corruption during save operations
- **FR-011**: System MUST prompt users to save unsaved changes before closing documents or applications
- **FR-012**: System MUST track file modification state and display an indicator in the window title
- **FR-013**: System MUST handle platform-specific path separators and line endings transparently
- **FR-014**: System MUST validate file paths to prevent directory traversal attacks
- **FR-015**: System MUST provide "Save As" functionality to save documents to new locations

#### Format Conversion

- **FR-016**: System MUST integrate with Pandoc to support all document conversion
- **FR-016**: System MUST support importing DOCX, Markdown, HTML, LaTeX, reStructuredText, Org, and Textile formats
- **FR-018**: System MUST automatically detect file format and convert to AsciiDoc on open
- **FR-019**: System MUST support exporting to HTML, DOCX, and PDF formats via Pandoc
- **FR-020**: System MUST handle Pandoc errors gracefully with informative user messages
- **FR-021**: System MUST check for Pandoc availability on startup and display warnings if missing
- **FR-022**: System MUST preserve semantic structure (headings, lists, tables) during format conversion with graceful degradation for unsupported elements

#### Git Integration

- **FR-023**: System MUST detect if the current file is in a Git repository
- **FR-024**: System MUST provide Git commit functionality accessible via menu (Git→Commit)
- **FR-025**: System MUST stage and commit the current file with a user-provided commit message
- **FR-026**: System MUST support Git pull operations to fetch remote changes
- **FR-027**: System MUST support Git push operations to publish local commits
- **FR-028**: System MUST never execute destructive Git operations (force push, hard reset) without explicit user confirmation
- **FR-029**: System MUST disable Git menu options when file is not in a repository

#### User Interface & Experience

- **FR-031**: System MUST provide both light and dark theme options
- **FR-032**: System MUST support theme toggle via keyboard shortcut (F5 or Ctrl+D)
- **FR-033**: System MUST meet WCAG AA contrast ratio requirements for both themes
- **FR-034**: System MUST provide a resizable splitter between editor and preview panes
- **FR-036**: System MUST support font zoom via Ctrl+Plus, Ctrl+Minus, Ctrl+0 keyboard shortcuts
- **FR-036**: System MUST provide keyboard shortcuts following platform conventions (Ctrl on Windows/Linux, Cmd on macOS)
- **FR-037**: System MUST render correctly on high-DPI displays with proper scaling
- **FR-038**: System MUST display status bar with current file information

#### Session & Configuration

- **FR-039**: System MUST persist user preferences using platform-appropriate configuration directories (XDG on Linux, AppData on Windows, Application Support on macOS)
- **FR-040**: System MUST remember the last opened file path and reopen on application launch
- **FR-041**: System MUST save and restore window geometry (size, position, maximized state)
- **FR-042**: System MUST persist user theme preference (light/dark)
- **FR-043**: System MUST save and restore editor font zoom level
- **FR-045**: System MUST persist splitter position between editor and preview panes
- **FR-045**: Configuration file MUST use JSON format for human readability and editability

#### Performance & Reliability

- **FR-045**: System MUST remain responsive when editing documents up to 10,000 lines
- **FR-046**: System MUST start within 3 seconds on standard hardware
- **FR-047**: System MUST use worker threads for CPU-intensive operations (Git, Pandoc, AsciiDoc rendering)
- **FR-048**: System MUST handle memory efficiently to prevent leaks during extended sessions
- **FR-049**: System MUST provide comprehensive error logging for debugging without exposing sensitive data

#### Cross-Platform Compatibility

- **FR-050**: System MUST function identically on Linux, macOS, and Windows platforms
- **FR-051**: System MUST support WSL (Windows Subsystem for Linux) with WSLg for GUI display
- **FR-052**: System MUST handle platform-specific file path conventions transparently
- **FR-053**: System MUST adapt keyboard shortcuts to platform conventions (Ctrl vs Cmd)

### Key Entities

- **Document**: Represents an AsciiDoc file open in the editor with content, file path, modification state, and scroll position
- **EditorState**: Captures current editor configuration, including font size, zoom level, cursor position, and selection
- **PreviewState**: Manages rendered HTML content, scroll position, and synchronization status with the editor
- **Configuration**: Stores user preferences including theme, last opened file, window geometry, and persistent settings
- **GitRepository**: Represents a detected Git repository with path, remote configuration, and current status
- **ConversionJob**: Represents a document format conversion task with source format, target format, Pandoc options, and conversion status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can edit documents with live preview updates occurring within 250ms of input
- **SC-002**: Application starts in under 3 seconds from launch to usable editor window
- **SC-003**: Users can edit documents exceeding 10,000 lines without UI freezing or lag
- **SC-004**: Application successfully opens, edits, and saves AsciiDoc files without data loss or corruption
- **SC-005**: Format conversion preserves document structure (headings, lists, tables) with 95% fidelity
- **SC-006**: Users can complete common workflows (open, edit, save, commit) entirely via keyboard shortcuts
- **SC-007**: 90% of users successfully complete their first document editing task without consulting documentation
- **SC-008**: Application functions identically on Linux, macOS, and Windows with no platform-specific feature degradation
- **SC-009**: Session state (last file, window geometry, theme) persists correctly across 99% of application restarts
- **SC-010**: Git commit operations complete successfully without data loss in 100% of cases where repository is valid

### User Experience Goals

- **SC-011**: Users report improved productivity compared to separate editor + preview tool workflows (measured via user surveys)
- **SC-012**: Technical writers can migrate from proprietary documentation tools within one day of using the application
- **SC-013**: Support requests related to data loss or corruption remain under 0.1% of user base
- **SC-014**: Users successfully convert documents between formats on first attempt 85% of the time

### Technical Excellence

- **SC-015**: Code maintains 80%+ test coverage for core functionality
- **SC-016**: Zero critical security vulnerabilities (path traversal, command injection) in production releases
- **SC-017**: Memory usage remains under 500MB for typical documents (<5000 lines)
- **SC-018**: Application passes linting (Ruff) and type checking (mypy strict) with zero warnings

## Dependencies & Assumptions

### External Dependencies

- **Python 3.11+**: Core runtime environment
- **PySide6 ≥6.9.0**: Qt bindings for GUI framework
- **asciidoc3**: AsciiDoc to HTML conversion engine
- **pypandoc**: Python wrapper for Pandoc document converter
- **Pandoc**: Universal document converter (external system dependency)
- **Git**: Version control system (optional, for Git integration features)

### Assumptions

- **A-001**: Users have Python 3.11 or higher installed on their system
- **A-002**: Users have display environment configured (X11/WSLg on Linux, native on macOS/Windows)
- **A-003**: Users who want document conversion have Pandoc installed separately
- **A-004**: Users who want Git integration have Git configured with valid credentials
- **A-005**: Target users are technical enough to use command-line installation for dependencies
- **A-006**: Documents primarily use standard AsciiDoc syntax without heavy use of advanced extensions
- **A-007**: Users have at least 4GB RAM available for comfortable application performance
- **A-008**: Display resolution is at least 1280x720 for proper UI layout
- **A-009**: Users accept open-source MIT license terms for the application
- **A-010**: Network connectivity is available for Git push/pull operations but not required for core editing

### Constraints & Limitations

- **C-001**: PDF export requires Pandoc with LaTeX backend installed separately
- **C-002**: Some advanced AsciiDoc features may have limited preview support based on asciidoc3 capabilities
- **C-003**: Git integration provides basic commit/push/pull operations but not advanced Git features (rebasing, cherry-picking, etc.)
- **C-004**: Format conversion fidelity depends on Pandoc capabilities and may lose some formatting details
- **C-005**: Application is designed for single-user, single-file editing (not multi-user collaboration)

## Out of Scope

The following capabilities are explicitly **not included** in this specification:

- **Multi-file project management**: No project browser or workspace management
- **Real-time collaboration**: No concurrent editing with multiple users
- **Cloud integration**: No built-in cloud storage or synchronization
- **Spell checking or grammar analysis**: Users should use external tools
- **Custom AsciiDoc extensions or plugins**: Standard AsciiDoc syntax only
- **Advanced Git features**: Branching, merging, and rebasing handled outside the application
- **PDF editing or annotation**: PDF is export-only target
- **Custom themes beyond light/dark**: No user-customizable color schemes
- **Mobile or web versions**: Desktop application only
- **Telemetry or analytics**: No usage tracking or data collection

## Implementation Notes for Developers

### Architecture Patterns

- **MVC Pattern**: Separate UI (View), application logic (Controller), and data models
- **Worker Threads**: Offload CPU-intensive tasks (rendering, Git, Pandoc) to background threads
- **Debouncing**: Use timer-based debouncing for preview updates to prevent performance issues
- **Atomic Writes**: Use temporary file + rename pattern to ensure atomic file writes

### Technology Choices

- **PySide6**: Chosen for Qt's mature cross-platform GUI capabilities and broad platform support
- **asciidoc3**: Python-native AsciiDoc processor for preview rendering
- **Pandoc**: Industry-standard document converter with extensive format support

### Testing Strategy

- **Unit Tests**: Core functionality (file I/O, conversion, configuration)
- **Integration Tests**: Pandoc integration, Git integration, cross-module interactions
- **UI Tests**: Critical user workflows using pytest-qt
- **Platform Tests**: Verify behavior on Linux, macOS, Windows
- **Performance Tests**: Measure preview update latency, memory usage, startup time

### Security Considerations

- **Path Validation**: All file paths must be sanitized using Path().resolve() and validated
- **Command Injection**: Git and Pandoc must be called with parameterized arguments, never shell interpolation
- **Credential Storage**: Never store Git credentials; use system-configured credentials only
- **Error Messages**: Avoid exposing full file paths or system information in user-facing errors

---

**Specification Version**: 1.0.0
**Last Updated**: 2025-10-22
**Approved By**: Project Maintainer
**Next Steps**: Refer to the constitution for development standards; Use `/speckit.plan` to generate an implementation plan
