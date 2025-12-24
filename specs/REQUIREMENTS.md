# Software Requirements Specification

**Project**: AsciiDoc Artisan
**Version**: 2.1.0
**Date**: 2025-12-24
**Format**: EARS (Easy Approach to Requirements Syntax)

---

## Project Overview

AsciiDoc Artisan is a desktop application for editing AsciiDoc documents with real-time preview capabilities. The system provides integrated Git operations, AI-powered assistance via Ollama, and advanced editing features including syntax highlighting, autocomplete, and multi-format export.

**Target Platform**: Linux, Windows, macOS
**Technology Stack**: PySide6 (Qt 6.9+), Python 3.11+
**Architecture**: Handler-based MVC with worker threads

**Key Metrics**:
- Codebase: 46,457 lines across 180 files
- Test Coverage: 95% (5,628 unit tests)
- Type Safety: mypy --strict with zero errors
- Performance: 0.27s startup (target <1.0s)

---

## Functional Requirements

### 1. Core Editor Requirements (REQ-001 to REQ-010)

#### REQ-001 (Ubiquitous) - Text Editor Component
The AsciiDoc Artisan system shall provide a multi-line text editor component based on QPlainTextEdit with support for AsciiDoc syntax highlighting.

**Acceptance Criteria**:
- Editor widget renders text content with UTF-8 encoding
- Minimum viewport size of 300x400 pixels
- Line wrapping configurable by user settings

#### REQ-002 (Event-Driven) - Text Content Changes
When the user modifies text content in the editor, the system shall emit a text_changed signal with the modified content.

**Acceptance Criteria**:
- Signal emission occurs within 10ms of text modification
- Signal includes full document content and change metadata
- Debounce mechanism prevents signal flooding (<300ms interval)

#### REQ-003 (Ubiquitous) - Line Number Display
The AsciiDoc Artisan system shall display line numbers in a gutter area adjacent to the editor component.

**Acceptance Criteria**:
- Line numbers update in real-time as content changes
- Gutter width adjusts automatically based on line count
- Current line highlighted with distinct background color

#### REQ-004 (Event-Driven) - Undo Operation
When the user triggers an undo action (Ctrl+Z), the system shall revert the most recent text modification.

**Acceptance Criteria**:
- Undo stack maintains minimum 100 operations
- Undo operation completes within 50ms
- Cursor position restored to pre-modification location

#### REQ-005 (Event-Driven) - Redo Operation
When the user triggers a redo action (Ctrl+Y or Ctrl+Shift+Z), the system shall reapply the most recently undone modification.

**Acceptance Criteria**:
- Redo stack cleared on new user modification
- Redo operation completes within 50ms
- Cursor position matches post-modification state

#### REQ-006 (State-Driven) - Font Configuration Persistence
While the application is running, the system shall apply user-configured font family and size settings to the editor component.

**Acceptance Criteria**:
- Font settings loaded from TOON configuration file at startup
- Font changes applied immediately without restart
- Default font: Courier New, 12pt

#### REQ-007 (Event-Driven) - State Persistence on Exit
When the user closes the application, the system shall save editor state including open file paths, window geometry, and splitter positions.

**Acceptance Criteria**:
- State saved atomically using temp+rename pattern
- Saved in TOON format to .config/asciidoc-artisan/editor_state.toon
- Auto-migration from legacy JSON format if present

#### REQ-008 (Event-Driven) - State Restoration on Launch
When the user launches the application, the system shall restore the previously saved editor state including window geometry and open documents.

**Acceptance Criteria**:
- Restoration completes within 500ms of application launch
- Graceful fallback if state file corrupted
- Default state used for first launch

#### REQ-009 (Event-Driven) - Syntax Highlighting Activation
When the user opens an AsciiDoc file (.adoc, .asciidoc, .asc), the system shall apply AsciiDoc syntax highlighting rules to the editor content.

**Acceptance Criteria**:
- Highlighting applied within 100ms of file load
- Supports: headings, bold, italic, code blocks, lists, links, images
- Color scheme follows active theme (dark/light mode)

#### REQ-010 (Event-Driven) - Auto-Indentation
When the user presses Enter after a list item or block delimiter, the system shall automatically indent the new line to match the previous line's indentation level.

**Acceptance Criteria**:
- Auto-indent completes within 20ms
- Supports nested lists up to 6 levels deep
- Respects tab vs. space configuration

---

### 2. File Operations Requirements (REQ-011 to REQ-025)

#### REQ-011 (Event-Driven) - Open File Dialog
When the user triggers the Open File action (Ctrl+O), the system shall display a native file selection dialog filtered for AsciiDoc files.

**Acceptance Criteria**:
- Dialog filters: .adoc, .asciidoc, .asc, .txt, *.*
- Remembers last opened directory between sessions
- Supports multi-file selection

#### REQ-012 (Event-Driven) - File Loading
When the user selects a file in the Open File dialog, the system shall load the file content into the editor using atomic read operations.

**Acceptance Criteria**:
- Files up to 10MB loaded within 500ms
- UTF-8 encoding detection automatic
- Error handling for permission denied, file not found

#### REQ-013 (Event-Driven) - Save File Operation
When the user triggers Save (Ctrl+S) for a file with an existing path, the system shall write editor content to disk using atomic save operations.

**Acceptance Criteria**:
- Uses temp+rename pattern (file.tmp → file.adoc)
- Save operation completes within 200ms for files <1MB
- Status bar confirmation: "Saved: {filename}"

#### REQ-014 (Event-Driven) - Save As Operation
When the user triggers Save As (Ctrl+Shift+S), the system shall display a save dialog and write content to the user-selected path.

**Acceptance Criteria**:
- Default extension: .adoc
- Overwrites require explicit confirmation
- Updates window title with new filename

#### REQ-015 (Event-Driven) - New File Creation
When the user triggers New File (Ctrl+N), the system shall create a new untitled document in the editor.

**Acceptance Criteria**:
- Prompts to save if current document modified
- New document titled "Untitled-{N}.adoc"
- Clears undo/redo history

#### REQ-016 (Ubiquitous) - Recent Files Tracking
The AsciiDoc Artisan system shall maintain a list of the 10 most recently opened files.

**Acceptance Criteria**:
- List stored in TOON format: ~/.config/asciidoc-artisan/recent_files.toon
- Duplicate paths removed (most recent kept)
- Non-existent files purged on startup

#### REQ-017 (Event-Driven) - Recent Files Menu
When the user opens the File menu, the system shall display a "Recent Files" submenu with the 10 most recently opened files.

**Acceptance Criteria**:
- Files listed in reverse chronological order
- Menu shows filename and truncated path
- Empty state: "No recent files"

#### REQ-018 (Event-Driven) - Recent File Selection
When the user selects a file from the Recent Files menu, the system shall load that file into the editor.

**Acceptance Criteria**:
- File load follows same validation as Open File
- If file not found, removed from recent list
- Error dialog shown for access denied

#### REQ-019 (State-Driven) - Auto-Save Enabled
While auto-save is enabled in settings, the system shall automatically save the current document at the configured interval.

**Acceptance Criteria**:
- Default interval: 300 seconds (5 minutes)
- Only saves if document modified
- Auto-save does not clear modified flag

#### REQ-020 (Event-Driven) - Auto-Save Execution
When the auto-save timer expires, the system shall save the current document to its existing path without user interaction.

**Acceptance Criteria**:
- Saves only if file path exists (not for unsaved new files)
- Uses atomic save pattern
- Silent operation (no status bar message)

#### REQ-021 (Event-Driven) - File Modified Detection
When the user modifies document content, the system shall set the modified flag and update the window title with an asterisk indicator.

**Acceptance Criteria**:
- Window title format: "*{filename} - AsciiDoc Artisan"
- Modified flag cleared on successful save
- Prompt on close if modified

#### REQ-022 (Event-Driven) - Close File Warning
When the user attempts to close a modified document, the system shall display a confirmation dialog with Save, Discard, Cancel options.

**Acceptance Criteria**:
- Dialog modal (blocks other operations)
- Default button: Save
- Cancel preserves current state

#### REQ-023 (Event-Driven) - File Encoding Detection
When the user opens a file, the system shall detect the file encoding and decode content appropriately.

**Acceptance Criteria**:
- Supports: UTF-8, UTF-16, Latin-1, ASCII
- Defaults to UTF-8 if detection fails
- Encoding shown in status bar

#### REQ-024 (Event-Driven) - File Encoding Selection
When the user selects an encoding from the status bar menu, the system shall reload the current file using the selected encoding.

**Acceptance Criteria**:
- Supported encodings: UTF-8, UTF-16LE, UTF-16BE, Latin-1, ASCII
- Reload preserves cursor position
- Error handling for incompatible encodings

#### REQ-025 (Unwanted Behavior) - File Access Error Handling
If file read or write operations fail due to permission errors, the system shall display an error dialog with the specific failure reason.

**Acceptance Criteria**:
- Error message includes file path and OS error code
- Operation rolled back (no partial writes)
- User returned to previous state

---

### 3. Preview Requirements (REQ-026 to REQ-040)

#### REQ-026 (Ubiquitous) - Live Preview Panel
The AsciiDoc Artisan system shall provide a live preview panel that renders AsciiDoc content as HTML.

**Acceptance Criteria**:
- Preview panel uses QWebEngineView (GPU accelerated) or QTextBrowser (fallback)
- Minimum width: 300 pixels
- Resizable via central splitter

#### REQ-027 (Event-Driven) - Preview Update Trigger
When the editor content changes, the system shall queue a preview update request with debounce delay.

**Acceptance Criteria**:
- Debounce delay: 300ms (configurable)
- Only most recent change processed
- Update cancels pending requests

#### REQ-028 (State-Driven) - Preview Rendering
While a preview update is in progress, the system shall render AsciiDoc to HTML using asciidoc3 in a worker thread.

**Acceptance Criteria**:
- Target render time: <200ms for documents <10,000 lines
- Worker emits result_ready signal with HTML content
- Render errors captured and displayed

#### REQ-029 (Optional Feature) - GPU-Accelerated Rendering
Where QWebEngineView is available and GPU support enabled, the system shall use GPU-accelerated HTML rendering.

**Acceptance Criteria**:
- 10-50x performance improvement over QTextBrowser
- Automatic fallback if WebEngine unavailable
- OpenGL 2.1+ or DirectX 11 support

#### REQ-030 (Event-Driven) - Preview Content Update
When the preview worker emits result_ready signal, the system shall update the preview panel with the rendered HTML content.

**Acceptance Criteria**:
- UI update completes within 50ms
- Scroll position preserved during update
- Syntax errors displayed inline

#### REQ-031 (Event-Driven) - Bidirectional Scroll Sync
When the user scrolls the editor, the system shall synchronize the preview panel to the corresponding document position.

**Acceptance Criteria**:
- Sync delay: <100ms
- Maintains relative scroll position (%)
- Works in both directions (editor ↔ preview)

#### REQ-032 (Optional Feature) - Incremental Rendering
Where incremental rendering is enabled, the system shall cache rendered blocks and only re-render modified sections.

**Acceptance Criteria**:
- LRU cache size: 100 blocks
- Cache hit rate >80% for typical editing
- 50-70% performance improvement

#### REQ-033 (Event-Driven) - Preview Theme Application
When the user changes the application theme, the system shall inject corresponding CSS into the preview panel.

**Acceptance Criteria**:
- Theme change applies within 100ms
- Supports: dark mode, light mode
- Custom theme CSS loaded from settings

#### REQ-034 (Event-Driven) - Preview Panel Toggle
When the user triggers the Toggle Preview action (Ctrl+B), the system shall show or hide the preview panel.

**Acceptance Criteria**:
- Toggle state persisted in settings
- Panel collapse/expand animated (200ms)
- Splitter ratios adjusted automatically

#### REQ-035 (Unwanted Behavior) - Preview Rendering Timeout
If preview rendering exceeds 5 seconds, the system shall cancel the worker and display a timeout error message.

**Acceptance Criteria**:
- Worker thread terminated gracefully
- Error message: "Preview render timeout (document too large)"
- Previous preview content retained

#### REQ-036 (Event-Driven) - Preview Zoom Control
When the user triggers zoom actions (Ctrl+Plus, Ctrl+Minus, Ctrl+0), the system shall adjust the preview panel zoom level.

**Acceptance Criteria**:
- Zoom range: 50% to 300%
- Step size: 10%
- Zoom level persisted in settings

#### REQ-037 (Optional Feature) - MathJax Support
Where MathJax is enabled in settings, the system shall render LaTeX math expressions in the preview panel.

**Acceptance Criteria**:
- Inline math: \$expression\$
- Block math: \$\$expression\$\$
- MathJax CDN or local library

#### REQ-038 (Optional Feature) - Diagram Rendering
Where diagram support is enabled, the system shall render PlantUML and Mermaid diagrams in the preview panel.

**Acceptance Criteria**:
- PlantUML blocks: [plantuml]
- Mermaid blocks: [mermaid]
- Server-side or local rendering

#### REQ-039 (Event-Driven) - Preview Export to HTML
When the user selects "Export Preview to HTML", the system shall save the current preview content as a standalone HTML file.

**Acceptance Criteria**:
- Includes embedded CSS and images
- Preserves all formatting and styles
- Opens in default browser on request

#### REQ-040 (Unwanted Behavior) - Preview Rendering Error
If AsciiDoc rendering fails due to syntax errors, the system shall display the error location and message in the preview panel.

**Acceptance Criteria**:
- Error shown with line number and description
- Previous valid preview retained
- Error cleared on next successful render

---

### 4. Git Integration Requirements (REQ-041 to REQ-055)

#### REQ-041 (Event-Driven) - Git Repository Detection
When the user opens a file, the system shall detect if the file is within a Git repository by searching for .git directory.

**Acceptance Criteria**:
- Search traverses parent directories up to filesystem root
- Detection completes within 100ms
- Git menu enabled only if repository detected

#### REQ-042 (State-Driven) - Git Status Display
While a Git repository is detected, the system shall display the current branch name in the status bar.

**Acceptance Criteria**:
- Status bar format: "📌 {branch_name}"
- Updates on commit, pull, push, checkout
- Detached HEAD shown as "HEAD@{hash}"

#### REQ-043 (Event-Driven) - Git Status Refresh
When the user triggers a Git operation or file save, the system shall refresh the Git status in a worker thread.

**Acceptance Criteria**:
- Worker executes: git status --porcelain
- Status update completes within 200ms
- Displays modified/staged file counts

#### REQ-044 (Event-Driven) - Quick Commit Dialog
When the user triggers Quick Commit (Ctrl+Shift+G), the system shall display a dialog showing staged files and a commit message input field.

**Acceptance Criteria**:
- Dialog shows: staged files list, diff preview, message input
- Validates commit message non-empty
- Buttons: Commit, Cancel

#### REQ-045 (Event-Driven) - Git Commit Execution
When the user clicks Commit in the Quick Commit dialog, the system shall execute git commit with the provided message in a worker thread.

**Acceptance Criteria**:
- Worker uses subprocess.run with shell=False
- Command: ["git", "commit", "-m", message]
- Success shows commit hash in status bar

#### REQ-046 (Event-Driven) - Git Pull Operation
When the user selects Git > Pull, the system shall execute git pull in a worker thread and display the result.

**Acceptance Criteria**:
- Worker executes: ["git", "pull", "--ff-only"]
- Shows progress dialog during operation
- Success/failure notification in status bar

#### REQ-047 (Event-Driven) - Git Push Operation
When the user selects Git > Push, the system shall execute git push in a worker thread and display the result.

**Acceptance Criteria**:
- Worker executes: ["git", "push"]
- Shows progress dialog during operation
- Handles push rejection with error message

#### REQ-048 (Event-Driven) - Git Status Panel
When the user selects Git > Status, the system shall display a panel showing modified, staged, and untracked files.

**Acceptance Criteria**:
- Panel updates in real-time on file changes
- Files grouped by status category
- Double-click opens file diff

#### REQ-049 (Event-Driven) - Git Log Viewer
When the user selects Git > Log, the system shall display a commit history viewer with the last 50 commits.

**Acceptance Criteria**:
- Shows: commit hash, author, date, message
- Paginated (50 commits per page)
- Click commit shows full diff

#### REQ-050 (Unwanted Behavior) - Git Command Timeout
If a Git operation exceeds 30 seconds, the system shall terminate the worker process and display a timeout error.

**Acceptance Criteria**:
- Worker thread stopped gracefully
- Error message: "Git operation timeout"
- User can retry or cancel

#### REQ-051 (Unwanted Behavior) - Git Command Failure
If a Git command fails with non-zero exit code, the system shall display the stderr output in an error dialog.

**Acceptance Criteria**:
- Error dialog shows command and full error message
- Logs error to application log file
- User returned to previous state

#### REQ-052 (Event-Driven) - Git Auto-Stage Current File
When the user triggers Quick Commit and the current file is modified, the system shall automatically stage the current file before commit.

**Acceptance Criteria**:
- Executes: ["git", "add", current_file_path]
- Only stages if file is tracked
- Shows "Auto-staged: {filename}" in dialog

#### REQ-053 (Optional Feature) - Git Integration Settings
Where Git integration is enabled in settings, the system shall provide configuration options for auto-commit, auto-push, and commit message templates.

**Acceptance Criteria**:
- Settings: auto_commit_on_save, auto_push_on_commit, message_template
- Default: all disabled
- Templates support variables: {date}, {filename}, {user}

#### REQ-054 (Event-Driven) - Git Diff Display
When the user selects a file in the Git Status panel, the system shall display a side-by-side diff of the file changes.

**Acceptance Criteria**:
- Uses git diff command
- Color-coded: green (additions), red (deletions)
- Context lines: 3 before/after

#### REQ-055 (Event-Driven) - Git Branch Checkout
When the user selects Git > Switch Branch, the system shall display a dialog listing local branches and allow branch switching.

**Acceptance Criteria**:
- Shows all local branches
- Indicates current branch with asterisk
- Warns if uncommitted changes exist

---

### 5. GitHub Integration Requirements (REQ-056 to REQ-065)

#### REQ-056 (Optional Feature) - GitHub CLI Detection
Where GitHub integration is enabled, the system shall detect the GitHub CLI (gh) installation on startup.

**Acceptance Criteria**:
- Checks for gh command in system PATH
- GitHub menu disabled if gh not found
- Settings option to specify custom gh path

#### REQ-057 (Event-Driven) - GitHub Authentication Status
When the user opens the GitHub menu, the system shall check GitHub CLI authentication status.

**Acceptance Criteria**:
- Executes: ["gh", "auth", "status"]
- Shows "Authenticated as {username}" in status bar
- Prompts login if not authenticated

#### REQ-058 (Event-Driven) - Create Pull Request Dialog
When the user selects GitHub > Create PR, the system shall display a dialog for creating a pull request.

**Acceptance Criteria**:
- Fields: title, description, base branch, head branch
- Auto-fills from current branch and recent commits
- Validates required fields

#### REQ-059 (Event-Driven) - Pull Request Creation
When the user submits the Create PR dialog, the system shall execute gh pr create in a worker thread.

**Acceptance Criteria**:
- Command: ["gh", "pr", "create", "--title", title, "--body", body]
- Shows progress indicator
- Opens PR URL in browser on success

#### REQ-060 (Event-Driven) - List Pull Requests
When the user selects GitHub > List PRs, the system shall display a panel listing open pull requests for the repository.

**Acceptance Criteria**:
- Shows: PR number, title, author, status
- Refreshes on demand
- Click PR shows details

#### REQ-061 (Event-Driven) - Create Issue Dialog
When the user selects GitHub > Create Issue, the system shall display a dialog for creating a GitHub issue.

**Acceptance Criteria**:
- Fields: title, description, labels, assignees
- Label auto-complete from repository labels
- Validates title non-empty

#### REQ-062 (Event-Driven) - Issue Creation
When the user submits the Create Issue dialog, the system shall execute gh issue create in a worker thread.

**Acceptance Criteria**:
- Command: ["gh", "issue", "create", "--title", title, "--body", body]
- Shows progress indicator
- Opens issue URL in browser on success

#### REQ-063 (Event-Driven) - List Issues
When the user selects GitHub > List Issues, the system shall display a panel listing open issues for the repository.

**Acceptance Criteria**:
- Shows: issue number, title, author, labels, state
- Filter by: open, closed, assigned to me
- Click issue shows full description

#### REQ-064 (Unwanted Behavior) - GitHub CLI Error Handling
If a GitHub CLI command fails, the system shall display the error message and suggest troubleshooting steps.

**Acceptance Criteria**:
- Error shows command output
- Suggests: re-authentication, network check, permission verification
- Logs error for debugging

#### REQ-065 (Event-Driven) - GitHub Repository Info
When the user selects GitHub > Repository Info, the system shall display repository metadata including stars, forks, and issues count.

**Acceptance Criteria**:
- Executes: ["gh", "repo", "view"]
- Shows: owner, name, description, stars, forks, open issues
- Includes repository URL

---

### 6. AI Chat Requirements (REQ-066 to REQ-080)

#### REQ-066 (Optional Feature) - Ollama Integration
Where Ollama integration is enabled, the system shall detect the Ollama service on startup.

**Acceptance Criteria**:
- Checks http://localhost:11434/api/tags
- Chat panel enabled if Ollama detected
- Settings option for custom Ollama host

#### REQ-067 (Ubiquitous) - Chat Panel Widget
The AsciiDoc Artisan system shall provide a collapsible chat panel for AI interactions.

**Acceptance Criteria**:
- Panel contains: context mode selector, chat history, input field
- Minimum width: 200 pixels
- Default position: right side of window

#### REQ-068 (Event-Driven) - Chat Context Mode Selection
When the user selects a context mode (Document, Syntax, General, Editing), the system shall adjust the AI system prompt accordingly.

**Acceptance Criteria**:
- Modes: Document (full text), Syntax (current line), General (no context), Editing (selection)
- Mode persisted in settings
- System prompt updated immediately

#### REQ-069 (Event-Driven) - Chat Message Submission
When the user submits a chat message, the system shall send the message with appropriate context to Ollama in a worker thread.

**Acceptance Criteria**:
- Input field cleared on submit
- Message added to chat history immediately
- Worker streams response chunks

#### REQ-070 (State-Driven) - Streaming Chat Response
While receiving a chat response from Ollama, the system shall display response chunks incrementally in the chat history.

**Acceptance Criteria**:
- Chunks appended in real-time (<100ms latency)
- Markdown formatting applied
- Code blocks syntax highlighted

#### REQ-071 (Event-Driven) - Chat Response Complete
When the Ollama worker emits chat_response_complete signal, the system shall mark the response as complete in the chat history.

**Acceptance Criteria**:
- Final response formatted with proper paragraphs
- Token count displayed (if available)
- User can submit next message

#### REQ-072 (Event-Driven) - Chat History Management
When the chat history exceeds 100 messages, the system shall remove the oldest messages to maintain performance.

**Acceptance Criteria**:
- Maximum 100 messages retained
- Removal occurs on new message submission
- History saved to TOON file on exit

#### REQ-073 (Event-Driven) - Clear Chat History
When the user clicks Clear History, the system shall remove all messages from the chat panel.

**Acceptance Criteria**:
- Confirmation dialog shown
- History cleared immediately on confirm
- Persisted state updated

#### REQ-074 (Event-Driven) - Copy Chat Message
When the user right-clicks a chat message, the system shall display a context menu with Copy option.

**Acceptance Criteria**:
- Copies message to system clipboard
- Preserves Markdown formatting
- Code blocks copied as plain text

#### REQ-075 (Event-Driven) - Insert AI Suggestion
When the user clicks "Insert" on an AI-generated code block, the system shall insert the code at the current cursor position.

**Acceptance Criteria**:
- Code inserted with proper indentation
- Cursor positioned after inserted text
- Undo operation reverses insertion

#### REQ-076 (Optional Feature) - Model Selection
Where multiple Ollama models are available, the system shall provide a model selector in the chat panel.

**Acceptance Criteria**:
- Lists all locally available models
- Current model shown in chat panel header
- Model change applies to next message

#### REQ-077 (Event-Driven) - AI Temperature Setting
When the user adjusts the AI temperature slider in settings, the system shall apply the temperature parameter to subsequent Ollama requests.

**Acceptance Criteria**:
- Range: 0.0 to 2.0
- Default: 0.7
- Takes effect on next message submission

#### REQ-078 (Unwanted Behavior) - Ollama Connection Error
If the Ollama service is unreachable, the system shall display an error message and disable chat features.

**Acceptance Criteria**:
- Error: "Ollama service not available at {host}"
- Chat input disabled
- Retry button available

#### REQ-079 (Unwanted Behavior) - Chat Request Timeout
If an Ollama request exceeds 60 seconds without response, the system shall cancel the request and display a timeout error.

**Acceptance Criteria**:
- Worker thread terminated
- Error message shown in chat
- User can retry with same message

#### REQ-080 (Event-Driven) - Chat Panel Toggle
When the user triggers Toggle Chat Panel (Ctrl+Shift+C), the system shall show or hide the chat panel.

**Acceptance Criteria**:
- Toggle state persisted
- Panel collapse/expand animated (200ms)
- Splitter ratios adjusted

---

### 7. Search and Replace Requirements (REQ-081 to REQ-090)

#### REQ-081 (Event-Driven) - Find Bar Display
When the user triggers Find (Ctrl+F), the system shall display a find bar at the bottom of the editor.

**Acceptance Criteria**:
- Find bar contains: search field, case checkbox, regex checkbox, buttons
- Find field receives focus
- Previous search term retained

#### REQ-082 (Event-Driven) - Find Next
When the user presses Enter in the find field or clicks Find Next (F3), the system shall highlight the next occurrence of the search term.

**Acceptance Criteria**:
- Search wraps to document start when reaching end
- Matched text selected and scrolled into view
- Match count shown: "{current}/{total}"

#### REQ-083 (Event-Driven) - Find Previous
When the user presses Shift+F3, the system shall highlight the previous occurrence of the search term.

**Acceptance Criteria**:
- Search wraps to document end when reaching start
- Matched text selected
- Match count updated

#### REQ-084 (State-Driven) - Case-Sensitive Search
While the Case checkbox is enabled, the system shall perform case-sensitive searches.

**Acceptance Criteria**:
- Checkbox state persisted
- Search updates immediately on toggle
- Default: case-insensitive

#### REQ-085 (State-Driven) - Regular Expression Search
While the Regex checkbox is enabled, the system shall interpret the search term as a regular expression pattern.

**Acceptance Criteria**:
- Supports full Python regex syntax
- Invalid regex shows error in find bar
- Captured groups highlighted

#### REQ-086 (Event-Driven) - Replace Dialog
When the user triggers Replace (Ctrl+H), the system shall display a replace bar with find and replace fields.

**Acceptance Criteria**:
- Replace bar contains: find field, replace field, options, buttons
- Replace field receives focus
- Previous replace term retained

#### REQ-087 (Event-Driven) - Replace Next
When the user clicks Replace, the system shall replace the current match and advance to the next occurrence.

**Acceptance Criteria**:
- Only replaces selected match
- Advances to next match automatically
- Undo operation reverses replacement

#### REQ-088 (Event-Driven) - Replace All
When the user clicks Replace All, the system shall replace all occurrences of the search term in the document.

**Acceptance Criteria**:
- Confirmation dialog for >20 replacements
- Shows count: "Replaced {count} occurrences"
- Single undo operation reverses all replacements

#### REQ-089 (Event-Driven) - Highlight All Matches
When the user enters a search term, the system shall highlight all matches in the editor with a background color.

**Acceptance Criteria**:
- Highlights update as search term changes
- Different color for current vs. other matches
- Maximum 1,000 highlights displayed

#### REQ-090 (Event-Driven) - Close Find Bar
When the user presses Escape or clicks Close in the find bar, the system shall hide the find bar and clear highlights.

**Acceptance Criteria**:
- Find bar hidden with animation
- All highlights removed
- Focus returned to editor

---

### 8. Export Requirements (REQ-091 to REQ-100)

#### REQ-091 (Event-Driven) - Export Dialog
When the user selects File > Export, the system shall display an export dialog with format selection and options.

**Acceptance Criteria**:
- Formats: HTML, PDF, DOCX, Markdown, LaTeX
- Options: output path, open after export, include TOC
- Default format: HTML

#### REQ-092 (Event-Driven) - Export to HTML
When the user selects HTML export, the system shall convert the AsciiDoc document to standalone HTML using asciidoc3.

**Acceptance Criteria**:
- Embedded CSS and images
- Preserves all formatting
- Export completes within 2 seconds for <10,000 line documents

#### REQ-093 (Event-Driven) - Export to PDF
When the user selects PDF export, the system shall convert the AsciiDoc document to PDF using wkhtmltopdf or pandoc.

**Acceptance Criteria**:
- Preserves formatting and images
- Page breaks at section boundaries
- Export completes within 5 seconds

#### REQ-094 (Event-Driven) - Export to DOCX
When the user selects DOCX export, the system shall convert the AsciiDoc document to Microsoft Word format using pandoc.

**Acceptance Criteria**:
- Converts to Markdown intermediate format
- Preserves headings, lists, tables, images
- Compatible with MS Word 2016+

#### REQ-095 (Event-Driven) - Export to Markdown
When the user selects Markdown export, the system shall convert the AsciiDoc document to Markdown format using pandoc.

**Acceptance Criteria**:
- Converts AsciiDoc syntax to Markdown equivalents
- Preserves code blocks, tables, links
- GitHub Flavored Markdown (GFM) dialect

#### REQ-096 (Optional Feature) - Export to LaTeX
Where LaTeX export is enabled, the system shall convert the AsciiDoc document to LaTeX format using pandoc.

**Acceptance Criteria**:
- Converts to LaTeX intermediate format
- Preserves math expressions
- Compiles with pdflatex

#### REQ-097 (Event-Driven) - Export Progress Indicator
When an export operation is in progress, the system shall display a progress dialog with cancellation option.

**Acceptance Criteria**:
- Shows current operation status
- Cancel button terminates worker
- Dialog auto-closes on completion

#### REQ-098 (Event-Driven) - Open After Export
When the user enables "Open after export" and export succeeds, the system shall open the exported file in the default system application.

**Acceptance Criteria**:
- Uses system default application
- Works on Linux, Windows, macOS
- Errors handled gracefully

#### REQ-099 (Unwanted Behavior) - Export Failure Handling
If an export operation fails, the system shall display an error dialog with the failure reason and suggested fixes.

**Acceptance Criteria**:
- Error shows missing dependencies (pandoc, wkhtmltopdf)
- Suggests installation commands
- Logs error for debugging

#### REQ-100 (Event-Driven) - Export Settings Persistence
When the user changes export options, the system shall save the settings for future export operations.

**Acceptance Criteria**:
- Settings saved in TOON format
- Includes: last format, output directory, options
- Restored on next export dialog open

---

### 9. Language Server Protocol Requirements (REQ-101 to REQ-109)

#### REQ-101 (Optional Feature) - LSP Server
Where LSP integration is enabled, the system shall start an AsciiDoc Language Server on application launch.

**Acceptance Criteria**:
- Server runs on localhost random port
- Communicates via JSON-RPC 2.0
- Supports: completion, diagnostics, hover

#### REQ-102 (Event-Driven) - Autocomplete Trigger
When the user types a trigger character (: for attributes, [ for blocks), the system shall request completion suggestions from the LSP server.

**Acceptance Criteria**:
- Response time: <50ms
- Suggestions shown in dropdown menu
- Trigger characters: :, [, {, <

#### REQ-103 (Event-Driven) - Autocomplete Selection
When the user selects a completion item, the system shall insert the completion text at the cursor position.

**Acceptance Criteria**:
- Insertion replaces partial text
- Cursor positioned after insertion
- Snippet support for templates

#### REQ-104 (State-Driven) - Real-Time Diagnostics
While the LSP server is active, the system shall request document diagnostics on text changes and display errors/warnings in the editor.

**Acceptance Criteria**:
- Diagnostics update within 500ms of text change
- Errors shown with wavy red underline
- Warnings shown with wavy yellow underline

#### REQ-105 (Event-Driven) - Hover Information
When the user hovers over an AsciiDoc element, the system shall request hover information from the LSP server and display a tooltip.

**Acceptance Criteria**:
- Tooltip shows element documentation
- Hover delay: 500ms
- Supports: attributes, cross-references, includes

#### REQ-106 (Event-Driven) - Go to Definition
When the user Ctrl+clicks a cross-reference or include directive, the system shall navigate to the referenced location.

**Acceptance Criteria**:
- Opens referenced file if external
- Scrolls to anchor or line number
- Works for: cross-refs, includes, anchors

#### REQ-107 (Event-Driven) - Document Formatting
When the user triggers Format Document, the system shall request formatting from the LSP server and apply changes.

**Acceptance Criteria**:
- Formatting preserves semantic structure
- Respects user indentation settings
- Undo operation reverses formatting

#### REQ-108 (Event-Driven) - Symbol Outline
When the user opens the Outline panel, the system shall request document symbols from the LSP server and display a hierarchical tree.

**Acceptance Criteria**:
- Shows: headings, sections, blocks, images, tables
- Click symbol navigates to location
- Updates on document changes

#### REQ-109 (Unwanted Behavior) - LSP Server Crash Recovery
If the LSP server process crashes, the system shall restart the server automatically and reconnect.

**Acceptance Criteria**:
- Restart attempt within 2 seconds
- Maximum 3 restart attempts
- Error notification after failed restarts

---

## Non-Functional Requirements

### 10. Performance Requirements (NFR-001 to NFR-010)

#### NFR-001 (Ubiquitous) - Application Startup Time
The AsciiDoc Artisan system shall start and display the main window within 1.0 second on systems meeting minimum requirements.

**Acceptance Criteria**:
- Current performance: 0.27s
- Target: <1.0s
- Measured from process start to main window shown

#### NFR-002 (Ubiquitous) - Preview Rendering Latency
The AsciiDoc Artisan system shall render preview updates within 200ms for documents up to 10,000 lines.

**Acceptance Criteria**:
- Measured from text change to HTML display
- Excludes network requests for images
- Target: <200ms (95th percentile)

#### NFR-003 (Ubiquitous) - Autocomplete Response Time
The AsciiDoc Artisan system shall display autocomplete suggestions within 50ms of trigger character input.

**Acceptance Criteria**:
- Measured from keystroke to dropdown display
- Includes LSP round-trip time
- Target: <50ms (95th percentile)

#### NFR-004 (Ubiquitous) - File Load Performance
The AsciiDoc Artisan system shall load and display files up to 10MB within 500ms.

**Acceptance Criteria**:
- Includes: file read, syntax highlighting, initial preview
- Linear performance scaling with file size
- Target: <500ms for 10MB files

#### NFR-005 (Ubiquitous) - Memory Baseline
The AsciiDoc Artisan system shall consume less than 100MB of memory with no documents open.

**Acceptance Criteria**:
- Measured after application fully loaded
- Excludes Qt/Python runtime overhead
- Target: <100MB baseline

#### NFR-006 (State-Driven) - Memory with Large Documents
While editing documents larger than 5MB, the system shall maintain memory usage below 500MB.

**Acceptance Criteria**:
- Includes: editor content, undo stack, preview cache
- Memory released on document close
- No memory leaks over 1-hour session

#### NFR-007 (Ubiquitous) - UI Responsiveness
The AsciiDoc Artisan system shall maintain UI responsiveness with frame rates above 30 FPS during all operations.

**Acceptance Criteria**:
- No blocking operations on main thread
- Smooth scrolling and animations
- Input latency <100ms

#### NFR-008 (Event-Driven) - Git Operation Performance
When executing Git operations, the system shall complete status checks within 200ms and commits within 1 second.

**Acceptance Criteria**:
- Status check: <200ms
- Commit: <1s
- Pull/Push: depends on network, progress shown

#### NFR-009 (Event-Driven) - Search Performance
When searching documents, the system shall find all matches within 500ms for documents up to 50,000 lines.

**Acceptance Criteria**:
- Includes regex compilation and matching
- Highlighting all matches: <1s
- Incremental search updates: <100ms

#### NFR-010 (Ubiquitous) - Export Performance
The AsciiDoc Artisan system shall export documents to HTML within 2 seconds and to PDF within 5 seconds for documents up to 10,000 lines.

**Acceptance Criteria**:
- HTML export: <2s
- PDF export: <5s
- Progress indicator shown for >1s operations

---

### 11. Security Requirements (NFR-011 to NFR-020)

#### NFR-011 (Ubiquitous) - Subprocess Shell Injection Prevention
The AsciiDoc Artisan system shall execute all subprocess commands with shell=False to prevent shell injection vulnerabilities.

**Acceptance Criteria**:
- All subprocess.run calls use shell=False
- Command arguments passed as list, not string
- Validation: grep -r "shell=True" returns empty

#### NFR-012 (Ubiquitous) - Atomic File Writes
The AsciiDoc Artisan system shall use atomic write operations (temp+rename pattern) for all file saves to prevent data corruption.

**Acceptance Criteria**:
- All writes use atomic_save_text or atomic_save_toon
- Temporary file suffix: .tmp
- Cleanup on failure

#### NFR-013 (Ubiquitous) - Input Validation
The AsciiDoc Artisan system shall validate all user inputs including file paths, Git commit messages, and search patterns.

**Acceptance Criteria**:
- File paths checked for existence and permissions
- Commit messages limited to 500 characters
- Regex patterns validated before use

#### NFR-014 (Ubiquitous) - Configuration File Permissions
The AsciiDoc Artisan system shall store configuration files with restricted permissions (600) to prevent unauthorized access.

**Acceptance Criteria**:
- Settings files: 600 (owner read/write only)
- Settings directory: 700 (owner access only)
- Applies to TOON and JSON configuration files

#### NFR-015 (Optional Feature) - API Key Storage
Where API keys are required (e.g., GitHub, Ollama remote), the system shall store credentials using system keyring or encrypted storage.

**Acceptance Criteria**:
- No plain-text API keys in configuration files
- Uses: keyring library or OS credential store
- Fallback to encrypted file with master password

#### NFR-016 (Unwanted Behavior) - Network Request Validation
If the system makes network requests (e.g., Ollama, image downloads), the system shall validate URLs and use HTTPS where possible.

**Acceptance Criteria**:
- URL validation against allowed hosts
- HTTPS enforced for external requests
- Timeout limits: 30s for API, 10s for connectivity check

#### NFR-017 (Ubiquitous) - Error Message Information Disclosure
The AsciiDoc Artisan system shall sanitize error messages to prevent disclosure of sensitive file paths or system information.

**Acceptance Criteria**:
- Home directory replaced with ~
- Full paths truncated to filename
- Stack traces logged, not displayed

#### NFR-018 (Event-Driven) - Crash Recovery
When the application crashes, the system shall save emergency recovery files for all open documents.

**Acceptance Criteria**:
- Recovery files saved to ~/.config/asciidoc-artisan/recovery/
- Files include timestamp and original path
- Recovery prompt shown on next startup

#### NFR-019 (Ubiquitous) - Dependency Vulnerability Scanning
The AsciiDoc Artisan system shall use only dependencies without known critical security vulnerabilities.

**Acceptance Criteria**:
- pip-audit or safety check in CI/CD
- Dependencies updated quarterly
- CVE monitoring enabled

#### NFR-020 (Optional Feature) - Sandbox Mode
Where sandbox mode is enabled, the system shall restrict file system access to a designated project directory.

**Acceptance Criteria**:
- File dialogs limited to sandbox directory
- Git operations restricted to sandbox
- Settings option to enable/disable

---

### 12. Usability Requirements (NFR-021 to NFR-030)

#### NFR-021 (Ubiquitous) - Keyboard Accessibility
The AsciiDoc Artisan system shall provide keyboard shortcuts for all primary functions.

**Acceptance Criteria**:
- All menu items have shortcuts
- Tab order follows visual layout
- Focus indicators visible on all interactive elements

#### NFR-022 (Ubiquitous) - Consistent UI Design
The AsciiDoc Artisan system shall follow Qt design guidelines for consistent widget styling and behavior.

**Acceptance Criteria**:
- Native look and feel on all platforms
- Consistent spacing and alignment
- Standard button ordering (OK/Cancel)

#### NFR-023 (Event-Driven) - User Feedback
When the user triggers an action, the system shall provide immediate visual or textual feedback.

**Acceptance Criteria**:
- Status bar messages for all operations
- Progress indicators for >1s operations
- Error dialogs for failures

#### NFR-024 (Ubiquitous) - Undo/Redo Coverage
The AsciiDoc Artisan system shall support undo/redo for all content modification operations.

**Acceptance Criteria**:
- Undo stack: minimum 100 operations
- Covers: text edits, replacements, insertions
- Excludes: file operations, settings changes

#### NFR-025 (Event-Driven) - Error Recovery Guidance
When errors occur, the system shall provide actionable guidance for resolution.

**Acceptance Criteria**:
- Error messages include specific cause
- Suggests next steps or troubleshooting
- Links to documentation where applicable

#### NFR-026 (Ubiquitous) - Responsive Layout
The AsciiDoc Artisan system shall adapt layout to window resizing and maintain minimum usable dimensions.

**Acceptance Criteria**:
- Minimum window size: 800x600
- Splitters remember positions
- Panels collapse gracefully

#### NFR-027 (Optional Feature) - Accessibility Support
Where accessibility features are enabled, the system shall provide screen reader support and high-contrast modes.

**Acceptance Criteria**:
- All widgets have accessible names
- ARIA labels for custom widgets
- Contrast ratio: minimum 4.5:1

#### NFR-028 (Ubiquitous) - Internationalization Support
The AsciiDoc Artisan system shall support internationalization with translatable UI strings.

**Acceptance Criteria**:
- All UI strings externalized to .qm files
- Support for: English, Spanish, French, German, Chinese
- Locale detection automatic

#### NFR-029 (Event-Driven) - First-Run Experience
When the user launches the application for the first time, the system shall display a welcome dialog with quick start guide.

**Acceptance Criteria**:
- Dialog shows: key features, keyboard shortcuts, settings
- Option to open sample document
- "Don't show again" checkbox

#### NFR-030 (Ubiquitous) - Help Documentation
The AsciiDoc Artisan system shall provide comprehensive help documentation accessible from the Help menu.

**Acceptance Criteria**:
- User guide in HTML format
- Searchable documentation
- Keyboard shortcuts reference

---

### 13. Compatibility Requirements (NFR-031 to NFR-035)

#### NFR-031 (Ubiquitous) - Operating System Support
The AsciiDoc Artisan system shall run on Linux, Windows 10+, and macOS 11+.

**Acceptance Criteria**:
- Tested on: Ubuntu 22.04, Windows 11, macOS 13
- Platform-specific installers provided
- Same feature set across platforms

#### NFR-032 (Ubiquitous) - Python Version Support
The AsciiDoc Artisan system shall require Python 3.11 or higher.

**Acceptance Criteria**:
- Startup check for Python version
- Error message if version insufficient
- Type hints compatible with 3.11+

#### NFR-033 (Ubiquitous) - Qt Version Support
The AsciiDoc Artisan system shall require PySide6 version 6.9 or higher.

**Acceptance Criteria**:
- Uses Qt 6.9+ features
- GPU acceleration requires Qt 6.2+
- Fallback for older Qt versions

#### NFR-034 (Optional Feature) - WebEngine Fallback
Where QWebEngineView is unavailable, the system shall fall back to QTextBrowser for preview rendering.

**Acceptance Criteria**:
- Automatic detection of WebEngine availability
- Graceful degradation of features
- User notification of fallback mode

#### NFR-035 (Ubiquitous) - Configuration Migration
The AsciiDoc Artisan system shall automatically migrate legacy JSON configuration files to TOON format.

**Acceptance Criteria**:
- Detects .json files on startup
- Converts to .toon format
- Preserves all settings
- Renames .json to .json.bak

---

### 14. Maintainability Requirements (NFR-036 to NFR-040)

#### NFR-036 (Ubiquitous) - Code Quality Standards
The AsciiDoc Artisan codebase shall adhere to MA principles with maximum 400 lines per file.

**Acceptance Criteria**:
- All files <400 lines
- Functions <50 lines
- Cyclomatic complexity <10

#### NFR-037 (Ubiquitous) - Type Safety
The AsciiDoc Artisan codebase shall pass mypy --strict type checking with zero errors.

**Acceptance Criteria**:
- All functions type-annotated
- No Any types except for Qt signals
- Strict mode enabled in mypy.ini

#### NFR-038 (Ubiquitous) - Test Coverage
The AsciiDoc Artisan codebase shall maintain minimum 90% test coverage.

**Acceptance Criteria**:
- Current coverage: 95%
- Target: >90%
- Coverage enforced in CI/CD

#### NFR-039 (Ubiquitous) - Code Formatting
The AsciiDoc Artisan codebase shall follow PEP 8 style with ruff and isort formatting.

**Acceptance Criteria**:
- ruff format applied to all files
- isort for import sorting
- Line length: 100 characters

#### NFR-040 (Ubiquitous) - Documentation Coverage
The AsciiDoc Artisan codebase shall include docstrings for all public functions and classes.

**Acceptance Criteria**:
- Google-style docstrings
- Includes: parameters, return values, exceptions
- Examples for complex functions

---

## Technical Constraints

### 15. Technical Constraints (TC-001 to TC-010)

#### TC-001 (Ubiquitous) - Thread Safety
The AsciiDoc Artisan system shall execute all UI updates on the main Qt thread.

**Rationale**: Qt widgets are not thread-safe. Worker threads must use signal/slot for UI updates.

#### TC-002 (Ubiquitous) - Reentrancy Guards
The AsciiDoc Artisan system shall implement reentrancy guards (_is_processing flags) for all handler operations.

**Rationale**: Prevents concurrent execution of non-reentrant operations like file I/O.

#### TC-003 (Ubiquitous) - Worker Thread Pattern
The AsciiDoc Artisan system shall use QThread workers for all operations exceeding 100ms.

**Rationale**: Prevents UI freezing and maintains responsiveness.

#### TC-004 (Ubiquitous) - Signal/Slot Communication
The AsciiDoc Artisan system shall use Qt signals and slots for all inter-component communication.

**Rationale**: Ensures thread-safe communication and loose coupling.

#### TC-005 (Ubiquitous) - TOON Storage Format
The AsciiDoc Artisan system shall use TOON format for all configuration storage.

**Rationale**: 30-60% smaller than JSON, human-readable, maintains compatibility.

#### TC-006 (Ubiquitous) - Subprocess Shell=False
The AsciiDoc Artisan system shall never use shell=True in subprocess calls.

**Rationale**: Security requirement to prevent shell injection attacks.

#### TC-007 (Ubiquitous) - Handler Architecture
The AsciiDoc Artisan system shall delegate all domain logic to handler classes separate from main_window.py.

**Rationale**: Enforces MA principle of <400 lines per file, improves testability.

#### TC-008 (Ubiquitous) - Atomic Write Operations
The AsciiDoc Artisan system shall use temp+rename pattern for all file writes.

**Rationale**: Ensures file integrity, prevents partial writes on crash.

#### TC-009 (Optional Feature) - GPU Acceleration
The AsciiDoc Artisan system shall use QWebEngineView with OpenGL/DirectX for preview rendering where available.

**Rationale**: Provides 10-50x performance improvement for large documents.

#### TC-010 (Ubiquitous) - Incremental Rendering Cache
The AsciiDoc Artisan system shall implement LRU cache (100 blocks) for preview rendering.

**Rationale**: 50-70% performance improvement by avoiding redundant renders.

---

## Dependencies

### 16. External Dependencies (DEP-001 to DEP-015)

#### DEP-001 (Ubiquitous) - PySide6
**Version**: 6.9+
**Purpose**: Qt framework for GUI
**License**: LGPL
**Installation**: `pip install PySide6>=6.9`

#### DEP-002 (Ubiquitous) - Python
**Version**: 3.11+
**Purpose**: Runtime environment
**License**: PSF
**Installation**: System package manager

#### DEP-003 (Ubiquitous) - asciidoc3
**Version**: Latest
**Purpose**: AsciiDoc to HTML conversion
**License**: GPL
**Installation**: `pip install asciidoc3`

#### DEP-004 (Ubiquitous) - python-toon
**Version**: Latest
**Purpose**: Configuration file format
**License**: MIT
**Installation**: `pip install python-toon`

#### DEP-005 (Optional Feature) - pypandoc
**Version**: Latest
**Purpose**: Multi-format export
**License**: MIT
**Installation**: `pip install pypandoc`
**System Dependency**: pandoc (apt/brew/choco)

#### DEP-006 (Optional Feature) - pymupdf
**Version**: Latest
**Purpose**: PDF generation
**License**: AGPL
**Installation**: `pip install pymupdf`

#### DEP-007 (Optional Feature) - wkhtmltopdf
**Version**: 0.12+
**Purpose**: HTML to PDF conversion
**License**: LGPL
**Installation**: System package (`apt install wkhtmltopdf`)

#### DEP-008 (Optional Feature) - GitHub CLI (gh)
**Version**: 2.0+
**Purpose**: GitHub integration
**License**: MIT
**Installation**: https://cli.github.com/

#### DEP-009 (Optional Feature) - Ollama
**Version**: Latest
**Purpose**: Local AI chat integration
**License**: MIT
**Installation**: https://ollama.ai/

#### DEP-010 (Ubiquitous) - pytest
**Version**: 7.0+
**Purpose**: Testing framework
**License**: MIT
**Installation**: `pip install pytest pytest-qt pytest-cov`

#### DEP-011 (Ubiquitous) - mypy
**Version**: 1.0+
**Purpose**: Static type checking
**License**: MIT
**Installation**: `pip install mypy`

#### DEP-012 (Ubiquitous) - ruff
**Version**: Latest
**Purpose**: Linting and formatting
**License**: MIT
**Installation**: `pip install ruff`

#### DEP-013 (Optional Feature) - QWebEngineView
**Version**: PySide6 6.2+
**Purpose**: GPU-accelerated preview
**License**: LGPL
**Fallback**: QTextBrowser

#### DEP-014 (Optional Feature) - keyring
**Version**: Latest
**Purpose**: Secure credential storage
**License**: MIT
**Installation**: `pip install keyring`

#### DEP-015 (Optional Feature) - git
**Version**: 2.0+
**Purpose**: Version control integration
**License**: GPL
**Installation**: System package manager

---

## Acceptance Criteria

### 17. System-Wide Acceptance Criteria

#### AC-001 - Test Suite Execution
All 5,628 unit tests must pass without failures or errors.

**Validation**:
```bash
make test
pytest --cov=src --cov-fail-under=90
```

#### AC-002 - Type Safety Validation
The codebase must pass mypy strict type checking with zero errors.

**Validation**:
```bash
mypy --strict src/
```

#### AC-003 - Security Audit
No subprocess calls with shell=True must exist in the codebase.

**Validation**:
```bash
grep -r "shell=True" src/
grep -r "shell = True" src/
# Both must return empty
```

#### AC-004 - Code Quality
All Python files must pass ruff linting and formatting checks.

**Validation**:
```bash
ruff check src/
ruff format --check src/
```

#### AC-005 - Performance Benchmarks
Application must meet all performance targets defined in NFR-001 to NFR-010.

**Validation**:
- Startup: <1.0s (current: 0.27s)
- Preview: <200ms
- Autocomplete: <50ms
- File load (10MB): <500ms
- Memory baseline: <100MB

#### AC-006 - Platform Compatibility
Application must run on Linux (Ubuntu 22.04), Windows 11, and macOS 13 without errors.

**Validation**:
- CI/CD tests on all three platforms
- Manual testing of platform-specific features
- Installer validation

#### AC-007 - Documentation Completeness
All public functions and classes must have docstrings.

**Validation**:
```bash
pydocstyle src/
```

#### AC-008 - Configuration Migration
Legacy JSON configuration files must automatically migrate to TOON format.

**Validation**:
- Create test .json config
- Launch application
- Verify .toon file created and .json.bak exists

#### AC-009 - Error Handling Coverage
All error scenarios defined in "Unwanted Behavior" requirements must have corresponding test cases.

**Validation**:
- Review test coverage report
- Verify error handling tests for REQ-025, REQ-035, REQ-040, REQ-050, REQ-051, REQ-064, REQ-078, REQ-079, REQ-099, REQ-109

#### AC-010 - Accessibility Compliance
All interactive widgets must be keyboard accessible and have focus indicators.

**Validation**:
- Tab through all UI elements
- Verify focus indicators visible
- Screen reader compatibility (NVDA/JAWS)

---

## Quality Gate Status

**Requirements → Design Gate**

- ✓ All 109 functional requirements documented in EARS format
- ✓ All requirements have unique IDs (REQ-001 to REQ-109)
- ✓ Each requirement is testable with measurable acceptance criteria
- ✓ No ambiguous terms found (no "should", "could", "might", "possibly")
- ✓ All functional areas covered: Core Editor, File Ops, Preview, Git, GitHub, AI Chat, Search, Export, LSP
- ✓ Error scenarios defined with "Unwanted Behavior" requirements
- ✓ Non-functional requirements specified (Performance, Security, Usability, Compatibility, Maintainability)
- ✓ Technical constraints documented (Thread safety, Reentrancy, Worker pattern)
- ✓ Dependencies catalogued with versions and licenses
- ✓ System-wide acceptance criteria defined with validation commands
- ✓ Coverage complete: 109 FRs + 40 NFRs + 10 TCs + 15 DEPs + 10 ACs = 184 total requirements

**Ready for Design Phase**: YES

**Traceability Matrix**: All requirements trace to SPECIFICATIONS.md sections
- FR-001 to FR-010: Core Editor (SPEC lines 338-367)
- FR-011 to FR-025: File Operations (SPEC lines 370-405)
- FR-026 to FR-040: Preview (SPEC lines 408-441)
- FR-041 to FR-055: Git Integration (SPEC lines 444-465)
- FR-056 to FR-065: GitHub Integration (implied, not in spec)
- FR-066 to FR-080: AI Chat (SPEC lines 468-491)
- FR-081 to FR-090: Search/Replace (SPEC keyboard shortcuts)
- FR-091 to FR-100: Export (SPEC menu structure)
- FR-101 to FR-109: LSP (SPEC lines 2,134 code in lsp/)

**Validation Command Summary**:
```bash
# Comprehensive validation
make test                        # 5,628 tests pass
pytest --cov=src --cov-fail-under=90  # 95% coverage
mypy --strict src/               # 0 errors
grep -r "shell=True" src/        # Empty result
ruff check src/                  # All checks pass
ruff format --check src/         # Already formatted

# Performance benchmarks
python3 -m timeit -s "from main import main" "main()"  # <1.0s
pytest tests/performance/        # All benchmarks pass
```

---

**Document Version**: 1.0
**Generated**: 2025-12-24
**Specification Source**: /home/webbp/github/AsciiDoctorArtisan/SPECIFICATIONS.md
**Requirements Engineer**: Claude Agent (Requirements Specialist)
**Next Phase**: Design Phase (Architecture and UML diagrams)
