# AsciiDoc Artisan - Complete Specification

**Version**: 1.1.0-beta
**Specification Format**: OpenSpec + Microsoft Spec-Kit
**Last Updated**: October 26, 2025
**Status**: Reverse-Engineered from Implementation

---

## Product Intent

AsciiDoc Artisan is a desktop application for writing, editing, and converting AsciiDoc documents with live preview. It provides a unified workspace for technical writers, developers, educators, and documentation teams who need to create professional documentation with Git version control, multi-format document conversion, and optional AI-enhanced format translation.

### Core Vision

Provide a simple, safe, and performant AsciiDoc editor that:
- Works offline with no telemetry
- Respects user privacy
- Supports professional workflows with Git integration
- Handles document conversions intelligently
- Never disrupts user focus

### Target Users

1. **Technical Writers** - Software documentation, API guides, user manuals
2. **Software Developers** - READMEs, code documentation, architecture documents
3. **Educators/Students** - Papers, course materials, research documentation
4. **Documentation Teams** - Collaborative documentation using Git
5. **Content Creators** - Multi-format document conversion and publication

---

## Feature Overview

### 1. Core Editing
- Plain text editor with line numbers
- Standard operations: type, copy, paste, undo, redo
- Font size control and zoom
- Find and replace
- Line navigation

### 2. Live Preview
- Real-time HTML preview as you type
- Synchronized scrolling
- Debounced updates (350ms default)
- Adaptive rendering for large documents
- Dark/light theme support

### 3. File Operations
- Create, open, save, save-as
- Multi-format import: AsciiDoc, Markdown, DOCX, HTML, PDF, LaTeX, RST, Org
- Multi-format export: AsciiDoc, Markdown, DOCX, HTML, PDF
- Atomic file writes
- Path sanitization
- Large file optimizations

### 4. Git Integration
- Commit with custom messages
- Push and pull operations
- Repository status display
- Background processing
- Safe subprocess execution

### 5. Document Conversion
- Pandoc integration
- PDF text extraction
- AI-enhanced conversion (optional)
- Automatic fallback to Pandoc
- Clipboard content conversion

### 6. User Experience
- Dark mode support
- Window state persistence
- Keyboard shortcuts
- Cross-platform (Windows, Mac, Linux)
- Status bar with contextual messages

### 7. Performance
- Background worker threads
- Adaptive debouncing
- Resource monitoring
- Incremental rendering
- Large file handling

### 8. Security & Privacy
- No telemetry
- Local-only data storage
- Atomic file writes
- Path traversal protection
- Secure credential storage
- Safe subprocess execution

---

## Functional Requirements

### FR-001 to FR-010: Core Editor Features

#### FR-001: Plain Text Editing
**Intent**: Provide basic text editing for AsciiDoc content

**Specification**:
- The system MUST provide a plain text editor widget
- The editor MUST support UTF-8 encoding
- The editor MUST handle line endings correctly on all platforms

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:401`

**Test Criteria**:
- User can type text
- Text appears in editor
- UTF-8 characters display correctly
- Line endings preserved on save/load

---

#### FR-002: Live HTML Preview
**Intent**: Show rendered HTML as user types

**Specification**:
- The system MUST display live HTML preview of AsciiDoc content
- The preview MUST use a separate pane
- The preview MUST render using asciidoc3 engine

**Implementation**: `src/asciidoc_artisan/workers/preview_worker.py`

**Dependencies**: asciidoc3 >= 3.2.0

**Test Criteria**:
- Preview pane shows HTML rendering
- AsciiDoc syntax renders correctly
- Images and tables display properly

---

#### FR-003: Automatic Preview Updates
**Intent**: Keep preview synchronized with editor

**Specification**:
- The system MUST automatically update preview when editor content changes
- Updates MUST trigger on textChanged signal
- Updates MUST be debounced to prevent excessive rendering

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:404,579-604`

**Related**: FR-004 (Debouncing)

**Test Criteria**:
- Type in editor → preview updates
- Rapid typing → preview waits before updating
- Final update reflects all changes

---

#### FR-004: Debounced Updates
**Intent**: Prevent performance issues from rapid updates

**Specification**:
- The system MUST debounce preview updates with 350ms default delay
- The system MUST use adaptive debouncing (200-1000ms) based on document size
- Debounce timer MUST reset on each change

**Implementation**:
- `src/asciidoc_artisan/core/constants.py:22`
- `src/asciidoc_artisan/core/resource_monitor.py:120-167`

**Algorithm**:
```python
if document_size < 1KB:
    debounce = 200ms
elif document_size < 10KB:
    debounce = 350ms
else:
    debounce = min(1000ms, 350ms + (size_in_kb * 10))
```

**Test Criteria**:
- Small doc: updates after 200ms
- Medium doc: updates after 350ms
- Large doc: updates after up to 1000ms

---

#### FR-005: Line Numbers
**Intent**: Help users navigate code and track position

**Specification**:
- The system MUST display line numbers in the editor
- Line numbers MUST appear on the left side
- Line numbers MUST update as content changes
- Line numbers MUST be clickable for selection

**Implementation**: `src/asciidoc_artisan/ui/line_number_area.py`

**Test Criteria**:
- Line numbers visible on left
- Numbers update when lines added/removed
- Current line highlighted

---

#### FR-006: Copy/Cut/Paste
**Intent**: Standard clipboard operations

**Specification**:
- The system MUST support copy (Ctrl+C)
- The system MUST support cut (Ctrl+X)
- The system MUST support paste (Ctrl+V)
- Operations MUST work with system clipboard

**Implementation**: Qt built-in functionality

**Test Criteria**:
- Copy text → clipboard contains text
- Cut text → text removed, clipboard contains text
- Paste → clipboard content inserted

---

#### FR-007: Undo/Redo
**Intent**: Allow users to revert changes

**Specification**:
- The system MUST support undo (Ctrl+Z)
- The system MUST support redo (Ctrl+Y or Ctrl+Shift+Z)
- Undo stack MUST have unlimited depth
- Undo/redo MUST work across all editing operations

**Implementation**: Qt built-in functionality

**Test Criteria**:
- Make changes → undo → changes reverted
- Undo → redo → changes restored
- Multiple undo/redo operations work

---

#### FR-008: Find Text
**Intent**: Search for text within document

**Specification**:
- The system MUST provide text search functionality (Ctrl+F)
- Search MUST be case-sensitive by default
- Search MUST highlight matches
- Search MUST support find next/previous

**Implementation**: Qt built-in find functionality

**Test Criteria**:
- Press Ctrl+F → search dialog appears
- Enter text → matches highlighted
- Find next → jumps to next match

---

#### FR-009: Go To Line
**Intent**: Quick navigation to specific line

**Specification**:
- The system MUST allow navigation to specific line numbers (Ctrl+G)
- Dialog MUST show current line number
- Dialog MUST validate input (1 to max line)
- Cursor MUST move to specified line

**Implementation**: `src/asciidoc_artisan/ui/main_window.py`

**Test Criteria**:
- Press Ctrl+G → dialog appears
- Enter line 50 → cursor moves to line 50
- Invalid input → error message

---

#### FR-010: Background Rendering
**Intent**: Prevent UI freezing during preview rendering

**Specification**:
- The system MUST render previews in background thread
- Main UI thread MUST remain responsive during rendering
- Background thread MUST emit result signal when complete
- Thread MUST use Qt QThread for cross-platform compatibility

**Implementation**: `src/asciidoc_artisan/workers/preview_worker.py`

**Architecture**:
```
Main Thread              Preview Thread
    │                         │
    ├──textChanged─────►  Queue update
    │                         │
    │                    Render AsciiDoc
    │                         │
    │◄────HTML signal──── Emit result
    │                         │
 Update preview               │
```

**Test Criteria**:
- Large document rendering → UI still responsive
- Can type while rendering in progress
- Preview updates when rendering completes

**Related**: NFR-005 (Background Threading)

---

### FR-011 to FR-020: File Operations

#### FR-011: New File
**Intent**: Create empty document

**Specification**:
- The system MUST create new empty documents (Ctrl+N)
- New document MUST be named "untitled.adoc"
- If current document has unsaved changes, MUST prompt to save
- New document MUST appear in editor

**Implementation**: `src/asciidoc_artisan/ui/file_handler.py`

**Test Criteria**:
- Ctrl+N → new empty document
- With unsaved changes → save prompt appears
- Editor cleared and ready for new content

---

#### FR-012: Open File
**Intent**: Load existing document from disk

**Specification**:
- The system MUST open existing files (Ctrl+O)
- MUST show file picker dialog
- MUST support formats: .adoc, .asciidoc, .md, .markdown, .docx, .html, .htm, .pdf, .tex, .rst, .org, .textile
- MUST convert non-AsciiDoc formats to AsciiDoc on import
- MUST update window title with filename
- MUST detect Git repository if file is in one

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:657-815`

**File Type Detection**:
```python
if extension in ['.adoc', '.asciidoc']:
    # Load directly
elif extension in ['.md', '.markdown', '.docx', '.html', '.tex', '.rst']:
    # Convert via Pandoc
elif extension == '.pdf':
    # Extract text via pdfplumber
```

**Test Criteria**:
- Ctrl+O → file picker appears
- Select .adoc file → loads directly
- Select .md file → converts to AsciiDoc
- Select .pdf file → extracts text

**Related**: FR-021 to FR-024 (Import conversions)

---

#### FR-013: Save File
**Intent**: Persist document to disk

**Specification**:
- The system MUST save current document (Ctrl+S)
- If new document, MUST prompt for filename (Save As)
- MUST use atomic write operation
- MUST preserve file permissions
- MUST update window title (remove asterisk)
- MUST update last saved time

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:861-973`

**Test Criteria**:
- Ctrl+S → file saved
- New file → save as dialog appears
- Asterisk removed from title after save
- File exists on disk with correct content

**Related**: FR-015 (Atomic Writes)

---

#### FR-014: Save As
**Intent**: Save document with new name/location

**Specification**:
- The system MUST save document with new name
- MUST show file picker dialog with save mode
- MUST suggest current filename if document has one
- MUST support same formats as Open
- MUST update current filename to new name

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:861-973`

**Test Criteria**:
- Select Save As → file picker appears
- Choose new name → file saved with new name
- Window title updates to new name

---

#### FR-015: Atomic File Writes
**Intent**: Prevent file corruption on failure

**Specification**:
- The system MUST use atomic writes for all file saves
- MUST write to temporary file first (.tmp extension)
- MUST perform atomic rename to target path
- MUST clean up temporary file on error
- MUST preserve original file if write fails

**Implementation**: `src/asciidoc_artisan/core/file_operations.py:65-118`

**Algorithm**:
```python
1. Create temp_file = target_file + ".tmp"
2. Write content to temp_file
3. Atomic rename: temp_file -> target_file
4. If error: delete temp_file, preserve original
```

**Rationale**: Atomic rename is OS-level atomic operation. Either fully succeeds or fully fails. Prevents partial writes on crash/power loss.

**Test Criteria**:
- Save file → .tmp file created then renamed
- Simulate crash during write → original file intact
- Disk full error → original file intact

**Related**: NFR-006, NFR-007 (Data Integrity)

---

#### FR-016: Path Sanitization
**Intent**: Prevent directory traversal attacks

**Specification**:
- The system MUST sanitize all file paths before operations
- MUST resolve to absolute paths
- MUST reject paths containing ".." components
- MUST log rejected paths
- MUST return None for invalid paths

**Implementation**: `src/asciidoc_artisan/core/file_operations.py:27-62`

**Algorithm**:
```python
1. Convert to Path object
2. Resolve to absolute path (resolve symlinks)
3. Check if ".." in path.parts
4. If yes: log warning, return None
5. If no: return sanitized path
```

**Blocked Examples**:
- `../../etc/passwd` → Blocked
- `/tmp/../etc/passwd` → Blocked
- `~/documents/../.ssh/id_rsa` → Blocked

**Test Criteria**:
- Valid path → returns path
- Path with ".." → returns None and logs warning
- Symlink → resolves to real path

**Related**: NFR-009 (Security)

---

#### FR-017: Auto-Save
**Intent**: Prevent data loss from crashes

**Specification**:
- The system MUST auto-save open documents every 5 minutes
- User MUST be able to disable via preferences
- Auto-save interval MUST be configurable (default: 300 seconds)
- Auto-save MUST only save if document is modified
- Auto-save MUST NOT trigger if no file is open

**Implementation**: `src/asciidoc_artisan/ui/file_handler.py`

**Configuration**: `src/asciidoc_artisan/core/settings.py:58-59`

**Test Criteria**:
- Make changes → wait 5 minutes → file auto-saved
- Disable auto-save in preferences → no auto-save
- No open file → no auto-save timer running

---

#### FR-018: Unsaved Changes Warning
**Intent**: Prevent accidental data loss

**Specification**:
- The system MUST warn before closing with unsaved changes
- Warning MUST appear on: window close, new file, open file, quit
- Warning MUST offer: Save, Don't Save, Cancel
- Save button MUST trigger save operation
- Don't Save MUST discard changes
- Cancel MUST abort close operation

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:1488-1506`

**Test Criteria**:
- Make changes → close window → warning appears
- Click Save → file saved, window closes
- Click Don't Save → window closes without saving
- Click Cancel → window stays open

---

#### FR-019: Large File Handling
**Intent**: Handle documents larger than 10MB

**Specification**:
- The system MUST optimize loading for files > 1MB
- MUST use chunked reading for files > 10MB
- MUST show progress indicator for files > 10MB
- MUST disable live preview for files > 50MB
- MUST warn user for files > 50MB

**Implementation**: `src/asciidoc_artisan/core/large_file_handler.py`

**Thresholds**:
- < 1MB: Normal loading
- 1-10MB: Chunked reading
- 10-50MB: Progress indicator + chunked reading
- \> 50MB: Preview disabled, load-only mode

**Test Criteria**:
- 5MB file → loads normally
- 20MB file → progress bar appears
- 60MB file → warning + preview disabled

**Related**: NFR-003 (Performance)

---

#### FR-020: Last File Restoration
**Intent**: Resume where user left off

**Specification**:
- The system MUST restore last opened file on startup
- MUST restore cursor position
- MUST restore scroll position
- MUST NOT restore if file was deleted
- MUST clear last file on explicit "New" command

**Implementation**: `src/asciidoc_artisan/core/settings.py:50`

**Test Criteria**:
- Open file → close app → reopen → same file open
- Cursor and scroll position restored
- File deleted → starts with new empty document

---

### FR-021 to FR-030: Document Conversion

#### FR-021: Import Markdown
**Intent**: Convert Markdown to AsciiDoc

**Specification**:
- The system MUST convert Markdown files (.md, .markdown) to AsciiDoc on import
- MUST use Pandoc for conversion
- MUST preserve: headers, lists, links, code blocks, tables, inline formatting
- MUST handle GitHub Flavored Markdown
- MUST show progress during conversion

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py`

**Pandoc Command**: `pandoc -f markdown -t asciidoc --wrap=none`

**Test Criteria**:
- Import .md file → converts to AsciiDoc
- Headers converted correctly (# → =)
- Code blocks preserved with language hints
- Tables converted to AsciiDoc table syntax

---

#### FR-022: Import DOCX
**Intent**: Convert Microsoft Word to AsciiDoc

**Specification**:
- The system MUST convert DOCX files to AsciiDoc on import
- MUST use Pandoc for binary format handling
- MUST preserve: styles, headings, lists, tables, images (as links)
- MUST handle complex formatting gracefully
- MUST show progress during conversion

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py:154-159`

**Pandoc Command**: `pandoc -f docx -t asciidoc --wrap=none --extract-media=./images`

**Test Criteria**:
- Import .docx file → converts to AsciiDoc
- Headings preserved with correct levels
- Tables converted to AsciiDoc format
- Images extracted and referenced

---

#### FR-023: Import HTML
**Intent**: Convert HTML to AsciiDoc

**Specification**:
- The system MUST convert HTML files to AsciiDoc on import
- MUST use Pandoc for conversion
- MUST handle: semantic HTML5, headings, lists, tables, links, code blocks
- MUST strip: scripts, styles, metadata

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py`

**Pandoc Command**: `pandoc -f html -t asciidoc --wrap=none`

**Test Criteria**:
- Import .html file → converts to AsciiDoc
- Semantic structure preserved
- Scripts and styles removed

---

#### FR-024: Import PDF
**Intent**: Extract text from PDF files

**Specification**:
- The system MUST extract text from PDF files on import
- MUST use pdfplumber for text extraction
- MUST preserve: page structure, tables, text order
- MUST insert page markers (// Page N)
- MUST handle: multi-column layouts, tables, images (as placeholders)
- MUST format tables as AsciiDoc tables

**Implementation**: `src/document_converter.py:283-493`

**Algorithm**:
```python
For each page in PDF:
    1. Extract text in reading order
    2. Insert page marker
    3. Detect and extract tables
    4. Format tables as AsciiDoc
    5. Append to output
```

**Table Extraction**:
- Uses pdfplumber's table detection
- Converts to AsciiDoc table format
- Handles cell spanning, alignment

**Test Criteria**:
- Import .pdf file → text extracted
- Page markers present (// Page 1)
- Tables converted to AsciiDoc table syntax
- Text order logical and readable

---

#### FR-025: Export HTML
**Intent**: Generate standalone HTML from AsciiDoc

**Specification**:
- The system MUST export documents to HTML format
- MUST use asciidoc3 for rendering
- MUST generate standalone HTML (with CSS)
- MUST preserve all formatting, code blocks, tables
- MUST embed or link images

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:1009-1031`

**Output**: Standalone HTML5 document with embedded CSS

**Test Criteria**:
- Export to .html → valid HTML5 file created
- Opens in browser with correct formatting
- All content rendered correctly

---

#### FR-026: Export PDF
**Intent**: Generate PDF from AsciiDoc

**Specification**:
- The system MUST export documents to PDF format
- MUST use Pandoc with PDF engine (wkhtmltopdf, weasyprint, or pdflatex)
- MUST auto-detect available PDF engine
- MUST preserve formatting, page breaks, headers
- MUST show progress during conversion

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py:162-208`

**PDF Engine Priority**:
1. wkhtmltopdf (best for HTML-like output)
2. weasyprint (good for web content)
3. pdflatex (best for academic papers)

**Test Criteria**:
- Export to .pdf → PDF file created
- PDF opens and renders correctly
- Formatting preserved

---

#### FR-027: Export DOCX
**Intent**: Generate Microsoft Word document

**Specification**:
- The system MUST export documents to DOCX format
- MUST use Pandoc for conversion
- MUST preserve headings, lists, tables, inline formatting
- MUST handle images (embedded or linked)

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py:209-211`

**Pandoc Command**: `pandoc -f asciidoc -t docx -o output.docx`

**Test Criteria**:
- Export to .docx → Word file created
- Opens in Microsoft Word
- Formatting preserved

---

#### FR-028: Export Markdown
**Intent**: Convert AsciiDoc to Markdown

**Specification**:
- The system MUST export documents to Markdown format
- MUST use Pandoc with --wrap=none
- MUST generate GitHub Flavored Markdown
- MUST preserve code blocks with language hints
- MUST convert tables to Markdown table syntax

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py:212-217`

**Pandoc Command**: `pandoc -f asciidoc -t gfm --wrap=none`

**Test Criteria**:
- Export to .md → Markdown file created
- Valid GFM syntax
- Renders correctly on GitHub

---

#### FR-029: Clipboard Conversion
**Intent**: Convert pasted content to AsciiDoc

**Specification**:
- The system SHOULD convert clipboard content to AsciiDoc on paste
- MUST handle HTML clipboard content
- MUST handle Markdown clipboard content
- MUST preserve plain text as-is
- Conversion MUST be optional (user preference)

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:1292-1294`

**Test Criteria**:
- Copy HTML from browser → paste → converts to AsciiDoc
- Copy Markdown → paste → converts to AsciiDoc
- Copy plain text → paste → inserts as-is

---

#### FR-030: No Conversion Prompts
**Intent**: Seamless conversion workflow

**Specification**:
- The system MUST NOT prompt user during automatic conversions
- All conversions MUST happen silently
- Progress MUST be shown in status bar
- Errors MUST be shown in non-modal dialogs
- Pandoc MUST be default conversion method (no prompts about AI)

**Implementation**: Throughout `pandoc_worker.py`

**Test Criteria**:
- Import file → no conversion prompt
- Export file → no conversion prompt
- Only status bar feedback

---

### FR-031 to FR-040: Git Integration

#### FR-031: Select Git Repository
**Intent**: Connect document to version control

**Specification**:
- The system MUST allow user to select Git repository folder
- MUST validate folder is a Git repository
- MUST save repository path in settings
- MUST detect repository automatically if file is in Git folder
- MUST update status bar with repository name

**Implementation**: `src/asciidoc_artisan/ui/git_handler.py`

**Validation**: Check for `.git` folder in selected directory

**Test Criteria**:
- Select folder with .git → repository connected
- Status bar shows repository name
- Select non-Git folder → error message

---

#### FR-032: Git Commit
**Intent**: Save changes to version control

**Specification**:
- The system MUST commit changes with user-provided message
- MUST auto-save current file before commit
- MUST execute: `git add <file> && git commit -m "<message>"`
- MUST run in background thread
- MUST show progress in status bar
- MUST display success/error message

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py`

**Workflow**:
```
1. Save current file
2. Get commit message from user
3. Execute: git add <file>
4. Execute: git commit -m "<message>"
5. Show result in status bar
```

**Test Criteria**:
- Git → Commit → dialog appears
- Enter message → file committed
- Status bar shows success

---

#### FR-033: Git Push
**Intent**: Upload commits to remote server

**Specification**:
- The system MUST push commits to remote repository
- MUST execute: `git push` in background thread
- MUST show progress during network operation
- MUST handle authentication errors gracefully
- MUST display success/error message

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py`

**Test Criteria**:
- Git → Push → commits uploaded
- Status bar shows progress
- Authentication error → user-friendly message

---

#### FR-034: Git Pull
**Intent**: Download changes from remote server

**Specification**:
- The system MUST pull changes from remote repository
- MUST execute: `git pull` in background thread
- MUST reload file if current file was updated
- MUST warn if local changes would be overwritten
- MUST handle merge conflicts gracefully

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py`

**Test Criteria**:
- Git → Pull → changes downloaded
- File reloaded if changed remotely
- Merge conflict → error message with instructions

---

#### FR-035: Git Status Display
**Intent**: Show repository state at a glance

**Specification**:
- The system MUST show Git repository status in status bar
- MUST display repository name if in Git repo
- MUST display "Not in Git repository" if not in repo
- MUST update status when repository changes
- MUST enable/disable Git menu items based on status

**Implementation**: `src/asciidoc_artisan/ui/status_manager.py`

**Test Criteria**:
- In Git repo → status bar shows repo name
- Not in Git repo → status bar shows "Not in Git repository"
- Git menu items enabled/disabled appropriately

---

#### FR-036: Background Git Operations
**Intent**: Keep UI responsive during network operations

**Specification**:
- The system MUST execute Git commands in background thread
- Main UI thread MUST remain responsive
- Background thread MUST use QThread
- Thread MUST emit signal when operation completes
- Thread MUST NOT perform any UI operations

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py`

**Architecture**:
```
Main Thread              Git Thread
    │                         │
    ├──git_operation─────►  Execute
    │                         │
    │                    Run subprocess
    │                         │
    │◄────result signal─── Emit result
    │                         │
 Update UI                    │
```

**Test Criteria**:
- Git push → UI still responsive
- Can type during Git operation
- Status updates when operation completes

**Related**: NFR-005 (Background Threading)

---

#### FR-037: Git Error Handling
**Intent**: Provide helpful error messages

**Specification**:
- The system MUST provide user-friendly Git error messages
- MUST translate technical errors to plain language
- MUST handle: authentication errors, network errors, merge conflicts, uncommitted changes
- MUST suggest solutions in error messages

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py:134-162`

**Error Translation Examples**:
- `authentication failed` → "Git Authentication Failed. Check credentials (SSH key/token/helper)."
- `network unreachable` → "Network Error. Check internet connection."
- `CONFLICT` → "Merge Conflict. Resolve conflicts manually."

**Test Criteria**:
- Authentication error → helpful message
- Network error → helpful message
- Each error suggests solution

---

#### FR-038: Auto-Save Before Commit
**Intent**: Ensure committed version matches editor

**Specification**:
- The system MUST save current file before Git commit
- Save MUST complete before commit starts
- User MUST NOT be prompted for save
- Unsaved changes indicator MUST clear after save

**Implementation**: `src/asciidoc_artisan/ui/git_handler.py`

**Test Criteria**:
- Make changes → commit → file saved automatically
- Asterisk removed from title
- Committed version matches editor content

---

#### FR-039: Git Repository Detection
**Intent**: Auto-configure Git features

**Specification**:
- The system MUST auto-detect if current file is in Git repository
- Detection MUST occur on file open
- Detection MUST search parent directories for .git folder
- Detection MUST update status bar
- Detection MUST enable/disable Git menu items

**Implementation**: `src/asciidoc_artisan/ui/git_handler.py`

**Algorithm**:
```python
1. Get current file's directory
2. Walk up directory tree
3. Check each directory for .git folder
4. If found: repository detected
5. Update UI accordingly
```

**Test Criteria**:
- Open file in Git repo → Git features enabled
- Open file not in repo → Git features disabled
- Status bar reflects repository status

---

#### FR-040: Git Command Validation
**Intent**: Provide clear feedback if Git not installed

**Specification**:
- The system MUST validate Git is installed before executing commands
- MUST check for `git` command in system PATH
- MUST show friendly error if Git not found
- Error MUST include installation instructions

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py:121-126`

**Error Message**: "Git command not found. Ensure Git is installed and in system PATH."

**Test Criteria**:
- Git not installed → error with instructions
- Git installed → commands execute normally

---

### FR-041 to FR-053: User Interface

#### FR-041: Dark Mode
**Intent**: Reduce eye strain in low light

**Specification**:
- The system MUST support dark color theme
- MUST toggle with Ctrl+D keyboard shortcut
- MUST save preference in settings
- MUST apply to all UI elements: editor, preview, dialogs
- MUST provide smooth transition between themes

**Implementation**: `src/asciidoc_artisan/ui/theme_manager.py`

**Color Palette**:
- Dark mode: #2b2b2b background, #f0f0f0 text
- Light mode: #ffffff background, #000000 text

**Test Criteria**:
- Ctrl+D → theme toggles
- All UI elements update
- Preference persists across restarts

---

#### FR-042: Font Size Control
**Intent**: Improve readability for all users

**Specification**:
- The system MUST allow zoom in/out of editor text
- MUST support Ctrl++ (zoom in), Ctrl+- (zoom out), Ctrl+0 (reset)
- MUST enforce minimum font size of 8pt
- MUST have no maximum font size limit
- MUST save font size in settings
- MUST apply only to editor (not preview)

**Implementation**: `src/asciidoc_artisan/ui/editor_state.py`

**Range**: 8pt to unlimited (practical max ~72pt)

**Test Criteria**:
- Ctrl++ → text larger
- Ctrl+- → text smaller
- Ctrl+0 → reset to default (12pt)
- Below 8pt → stops decreasing

---

#### FR-043: Synchronized Scrolling
**Intent**: Keep editor and preview aligned

**Specification**:
- The system MUST synchronize scroll position between editor and preview
- MUST be bidirectional: editor → preview and preview → editor
- MUST calculate relative position (e.g., 50% down document)
- MUST be toggleable via user preference
- MUST prevent scroll loops

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:499-542`

**Algorithm**:
```python
editor_position = editor.verticalScrollBar().value()
editor_max = editor.verticalScrollBar().maximum()
relative_position = editor_position / editor_max if editor_max > 0 else 0

preview_max = preview.verticalScrollBar().maximum()
preview_position = relative_position * preview_max
preview.verticalScrollBar().setValue(preview_position)
```

**Test Criteria**:
- Scroll editor → preview scrolls
- Scroll preview → editor scrolls
- Relative position maintained
- Toggle off → scrolling independent

---

#### FR-044: Pane Maximization
**Intent**: Focus on editor or preview

**Specification**:
- The system MUST allow maximizing editor or preview pane
- MUST provide maximize button on each pane
- Maximize MUST hide other pane temporarily
- Restore MUST bring back both panes
- Splitter position MUST be remembered

**Implementation**: `src/asciidoc_artisan/ui/editor_state.py`

**Test Criteria**:
- Click maximize on editor → preview hides
- Click restore → preview returns
- Splitter position restored correctly

---

#### FR-045: Status Bar
**Intent**: Provide contextual feedback

**Specification**:
- The system MUST display contextual status messages
- MUST show: file operations, Git operations, conversions, errors, warnings
- Messages MUST time out after 5 seconds for info messages
- Errors MUST persist until user action
- Status bar MUST also show: Git repository name, line/column position

**Implementation**: `src/asciidoc_artisan/ui/status_manager.py`

**Message Types**:
- Info: "File saved successfully" (5s timeout)
- Warning: "Large file detected" (persist)
- Error: "Git command failed" (persist)
- Progress: "Converting document..." (until complete)

**Test Criteria**:
- Save file → status shows "Saved"
- Error occurs → status shows error
- Info message → disappears after 5 seconds

---

#### FR-046: Window State Persistence
**Intent**: Resume UI layout

**Specification**:
- The system MUST save and restore window size
- MUST save and restore window position
- MUST save and restore maximization state
- MUST validate position is on screen (handle multi-monitor changes)
- MUST apply defaults if no saved state

**Implementation**: `src/asciidoc_artisan/core/settings.py:54-55`

**Defaults**:
- Size: 1200x800
- Position: Centered on primary screen
- Maximized: False

**Test Criteria**:
- Resize window → close → reopen → size restored
- Move window → close → reopen → position restored
- Maximize → close → reopen → maximized

---

#### FR-047: Splitter Position Persistence
**Intent**: Remember editor/preview ratio

**Specification**:
- The system MUST save and restore splitter position between editor and preview
- MUST save as list of two integers (widths)
- MUST apply default 50/50 if no saved state
- MUST validate total equals window width

**Implementation**: `src/asciidoc_artisan/core/settings.py:55`

**Default**: [600, 600] (50/50 split)

**Test Criteria**:
- Adjust splitter → close → reopen → position restored
- Ratio maintained when window resized

---

#### FR-048: Keyboard Shortcuts
**Intent**: Efficient keyboard-driven workflow

**Specification**:
- The system MUST provide keyboard shortcuts for all major operations
- Shortcuts MUST follow platform conventions
- Shortcuts MUST be documented in menus
- Shortcuts MUST be customizable (future enhancement)

**Implementation**: `src/asciidoc_artisan/ui/action_manager.py`

**Platform Conventions**:
- Windows/Linux: Ctrl+Key
- macOS: Cmd+Key (auto-mapped by Qt)

**Test Criteria**:
- All shortcuts listed work
- Menus show shortcuts
- Shortcuts work even when menus closed

**Full List**: See FR-053

---

#### FR-049: Cross-Platform Support
**Intent**: Work on all major operating systems

**Specification**:
- The system MUST run on Windows 10+, macOS 12+, Linux (Ubuntu 20.04+)
- MUST use platform-appropriate UI conventions
- MUST use platform-appropriate file paths
- MUST use platform-appropriate settings storage
- MUST detect platform at runtime

**Implementation**: Platform detection in `src/asciidoc_artisan/core/constants.py:14`

**Platform-Specific**:
- Settings: QStandardPaths for platform paths
- Fonts: Platform-specific defaults (Consolas vs Courier New)
- Shortcuts: Auto-mapped by Qt

**Test Criteria**:
- Runs on Windows without errors
- Runs on macOS without errors
- Runs on Linux without errors
- UI looks native on each platform

**Dependencies**: Python 3.11+, PySide6 6.9.0+

**Related**: NFR-022 (Platform Requirements)

---

#### FR-050: Settings Persistence
**Intent**: Remember user preferences

**Specification**:
- The system MUST save settings to platform-appropriate location
- Linux/WSL: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- Windows: `%APPDATA%\AsciiDocArtisan\AsciiDocArtisan.json`
- macOS: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`
- MUST create directory if it doesn't exist
- MUST use JSON format
- MUST use atomic writes

**Implementation**: `src/asciidoc_artisan/ui/settings_manager.py`

**Settings Schema**:
```json
{
  "last_directory": "/home/user/documents",
  "last_file": "/home/user/documents/doc.adoc",
  "git_repo_path": "/home/user/repo",
  "dark_mode": true,
  "maximized": false,
  "window_geometry": {"x": 100, "y": 100, "width": 1200, "height": 800},
  "splitter_sizes": [600, 600],
  "font_size": 12,
  "auto_save_enabled": true,
  "auto_save_interval": 300,
  "ai_conversion_enabled": false
}
```

**Test Criteria**:
- Change setting → close → reopen → setting persists
- Settings file created in correct location
- Valid JSON format

**Related**: FR-015 (Atomic Writes)

---

#### FR-051: Window Title
**Intent**: Show current file and save state

**Specification**:
- The system MUST display current filename in window title
- Format: "AsciiDoc Artisan - filename.adoc"
- MUST append asterisk for unsaved changes: "AsciiDoc Artisan - filename.adoc*"
- MUST show "untitled.adoc" for new files
- MUST update immediately when filename or save state changes

**Implementation**: `src/asciidoc_artisan/ui/status_manager.py`

**Test Criteria**:
- New file → title shows "untitled.adoc"
- Open file → title shows filename
- Make changes → asterisk appears
- Save → asterisk disappears

---

#### FR-052: Progress Indicators
**Intent**: Show feedback for long operations

**Specification**:
- The system MUST show progress for long operations
- Operations: large file loading, document conversions, Git network operations
- MUST use progress dialogs for operations > 2 seconds
- MUST use status bar messages for operations < 2 seconds
- Progress dialogs MUST be non-modal (allow cancel)

**Implementation**: `src/asciidoc_artisan/ui/main_window.py:1148-1180`

**Test Criteria**:
- Load large file → progress dialog appears
- Convert document → status bar shows progress
- Can cancel long operations

---

#### FR-053: Complete Keyboard Shortcuts
**Intent**: Full keyboard accessibility

**Specification**: The system MUST support these shortcuts:

**File Operations**:
- Ctrl+N: New file
- Ctrl+O: Open file
- Ctrl+S: Save file
- Ctrl+Shift+S: Save As
- Ctrl+Q: Quit application

**Editing**:
- Ctrl+Z: Undo
- Ctrl+Y: Redo (Ctrl+Shift+Z on macOS)
- Ctrl+C: Copy
- Ctrl+X: Cut
- Ctrl+V: Paste
- Ctrl+A: Select All
- Ctrl+F: Find text
- Ctrl+G: Go to line

**View**:
- Ctrl+D: Toggle dark mode
- Ctrl++: Zoom in (Ctrl+= also works)
- Ctrl+-: Zoom out
- Ctrl+0: Reset zoom

**Implementation**: `src/asciidoc_artisan/ui/action_manager.py`

**Test Criteria**: All shortcuts listed function correctly

---

### FR-054 to FR-062: AI-Enhanced Conversion (Optional)

#### FR-054: Claude API Integration
**Intent**: Leverage AI for superior document conversion

**Specification**:
- The system MUST integrate with Anthropic Claude API for AI-enhanced conversions
- MUST use claude-3-5-sonnet-20241022 model
- MUST authenticate using API key from environment variable
- MUST handle rate limiting and retries
- MUST be optional (user can disable)

**Implementation**: `src/ai_client.py`

**API Configuration**:
- Model: claude-3-5-sonnet-20241022
- Max tokens: 4096
- Temperature: 0 (deterministic)

**Test Criteria**:
- API key set → AI conversions available
- API key not set → falls back to Pandoc
- Rate limit → automatic retry with backoff

**Dependencies**: anthropic >= 0.40.0

**Related**: NFR-012 (API Key Security)

---

#### FR-055: AI Conversion Preference
**Intent**: User control over AI usage

**Specification**:
- The system MUST allow user to enable/disable AI conversion
- MUST provide checkbox in Edit → Preferences dialog
- Default MUST be disabled (Pandoc only)
- Setting MUST persist in settings file
- Setting MUST apply immediately (no restart required)

**Implementation**:
- UI: `src/asciidoc_artisan/ui/dialogs.py:44`
- Setting: `src/asciidoc_artisan/core/settings.py:59`

**Test Criteria**:
- Preferences → AI checkbox unchecked by default
- Check box → AI conversions enabled
- Uncheck box → AI conversions disabled
- Setting persists across restarts

---

#### FR-056: Complex Structure Preservation
**Intent**: Superior conversion quality with AI

**Specification**:
- The system MUST use AI to preserve complex document structures
- MUST handle: nested lists, tables, code blocks, cross-references, inline formatting
- MUST maintain: semantic meaning, document hierarchy, formatting intent
- MUST produce valid AsciiDoc output
- Quality MUST be superior to Pandoc for complex documents

**Implementation**: `src/ai_client.py:229-252`

**AI Prompt Engineering**:
- Clear instructions for AsciiDoc syntax
- Examples of desired output
- Emphasis on preserving structure
- Request for valid markup

**Test Criteria**:
- Convert complex Word doc → structure preserved
- Nested lists maintain hierarchy
- Tables convert with correct syntax
- Code blocks with language hints

---

#### FR-057: Automatic Fallback
**Intent**: Guarantee conversion always works

**Specification**:
- The system MUST automatically fallback to Pandoc if AI conversion fails
- Fallback MUST be silent (no user intervention)
- Status bar MUST indicate fallback occurred
- Fallback MUST trigger on: API errors, rate limits, timeouts, invalid output
- Final result MUST always be valid AsciiDoc

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py:120-133`

**Fallback Conditions**:
- API key not set → immediate Pandoc fallback
- API rate limit → retry 3x, then Pandoc
- API timeout → Pandoc fallback
- Invalid AI output → Pandoc fallback

**Test Criteria**:
- AI fails → Pandoc succeeds, no user action needed
- Status bar shows "AI failed, using Pandoc"
- Final document is valid AsciiDoc

---

#### FR-058: API Key Validation
**Intent**: Fail fast with clear errors

**Specification**:
- The system MUST validate Claude API key before conversion
- Key MUST come from ANTHROPIC_API_KEY environment variable only
- Validation MUST occur on first AI conversion attempt
- Invalid key MUST trigger immediate fallback to Pandoc
- Error message MUST suggest checking environment variable

**Implementation**: `src/ai_client.py:89-104`

**Validation**: Minimal API call to check key validity

**Test Criteria**:
- Valid key → AI conversions work
- Invalid key → error message, fallback to Pandoc
- No key → silent fallback to Pandoc

**Related**: FR-061 (API Key Security)

---

#### FR-059: Progress Indicators
**Intent**: Feedback during AI operations

**Specification**:
- The system MUST show progress during AI conversion operations
- Status bar MUST show: "Initializing AI conversion...", "Converting with Claude AI...", "Conversion completed in X.Xs"
- Progress MUST be real-time (updated as operation proceeds)
- User MUST be able to cancel operation

**Implementation**: `src/asciidoc_artisan/workers/pandoc_worker.py:372-432`

**Progress States**:
1. "Initializing AI conversion..."
2. "Sending to Claude API..."
3. "Processing response..."
4. "Conversion completed in 2.3s"

**Test Criteria**:
- AI conversion → progress messages appear
- Can cancel during conversion
- Final time displayed accurately

---

#### FR-060: Error Handling & Retry
**Intent**: Robust error recovery

**Specification**:
- The system MUST retry AI conversions on transient errors
- MUST retry on: rate limit (429), connection errors, timeouts
- Max retries: 3 with exponential backoff (2^attempt seconds)
- MUST fallback to Pandoc after max retries
- MUST log all errors for debugging

**Implementation**: `src/ai_client.py:143-217`

**Retry Logic**:
```python
for attempt in range(3):
    try:
        result = call_api()
        return result
    except RateLimitError:
        wait = 2 ** attempt  # 1s, 2s, 4s
        time.sleep(wait)
# After 3 failures: fallback to Pandoc
```

**Test Criteria**:
- Rate limit → retries 3 times
- Permanent error → immediate fallback
- Network error → retries then fallback

---

#### FR-061: API Key Security
**Intent**: Never expose API keys

**Specification**:
- The system MUST NOT store API keys in settings files
- API keys MUST come from environment variables only
- MUST use: ANTHROPIC_API_KEY environment variable
- MUST NOT log API keys
- MUST NOT transmit API keys except to Claude API

**Implementation**: `src/asciidoc_artisan/core/settings.py:44-46`

**Rationale**: Settings files may be backed up, shared, or committed to Git. API keys in environment variables are more secure.

**Test Criteria**:
- Check settings file → no API key present
- Set ANTHROPIC_API_KEY → AI works
- Unset variable → AI disabled

**Related**: NFR-012 (Security)

---

#### FR-062: Rate Limiting
**Intent**: Handle API limits gracefully

**Specification**:
- The system MUST handle API rate limiting gracefully
- MUST detect 429 (Too Many Requests) responses
- MUST implement exponential backoff (2^attempt seconds)
- MUST show user-friendly message: "API rate limit reached. Retrying in X seconds..."
- MUST fallback to Pandoc after max retries

**Implementation**: `src/ai_client.py:181-192`

**Test Criteria**:
- Trigger rate limit → automatic retry
- Status bar shows retry countdown
- After max retries → fallback to Pandoc

---

## Non-Functional Requirements

### NFR-001: Preview Update Latency
**Intent**: Responsive live preview

**Specification**:
- Preview rendering MUST complete in < 350ms (95th percentile)
- MUST measure from text change to preview update complete
- MUST be achieved through background threading and debouncing
- MUST degrade gracefully for large documents (up to 1000ms acceptable)

**Measurement**: `src/performance_profiler.py:144`

**Target Performance**:
- Small doc (< 1KB): < 200ms
- Medium doc (1-10KB): < 350ms
- Large doc (> 10KB): < 1000ms

**Implementation**: `src/asciidoc_artisan/workers/preview_worker.py`

**Test Method**:
1. Start timer on textChanged signal
2. Stop timer on preview update complete
3. Verify 95% of samples < 350ms

---

### NFR-002: Application Startup Time
**Intent**: Fast application launch

**Specification**:
- Application MUST start in < 3 seconds on standard hardware
- Standard hardware: Dual-core CPU, 4GB RAM, SSD
- MUST measure from process start to window visible
- MUST include: module imports, UI construction, settings load, last file restore

**Measurement**: `src/performance_profiler.py:89`

**Breakdown**:
- Module imports: < 1s
- UI construction: < 1s
- Settings load: < 0.1s
- Last file restore: < 1s

**Optimizations**:
- Lazy imports where possible
- Minimal initialization work
- Async last file load

**Test Method**:
```bash
time python src/main.py
```

---

### NFR-003: Large File Handling
**Intent**: Handle documents of all sizes

**Specification**:
- The system MUST handle files up to 10 MB without crashing
- The system SHOULD handle files up to 50 MB with degraded performance
- Files > 50 MB MAY disable live preview
- MUST use chunked loading for files > 10 MB
- MUST show progress for files > 10 MB

**Implementation**: `src/asciidoc_artisan/core/large_file_handler.py`

**Performance Targets**:
- 1 MB file: Normal performance
- 10 MB file: Load in < 5s
- 50 MB file: Load in < 20s, preview disabled

**Memory Limits**:
- 1 MB file: < 100 MB RAM
- 10 MB file: < 500 MB RAM
- 50 MB file: < 2 GB RAM

**Test Method**:
1. Create test files of various sizes
2. Measure load time
3. Monitor memory usage
4. Verify no crashes

---

### NFR-004: Memory Usage
**Intent**: Efficient resource usage

**Specification**:
- The system MUST use < 500 MB for typical documents (< 1 MB)
- The system MAY use up to 2 GB for large documents (10+ MB)
- MUST not leak memory over extended sessions
- MUST release memory when files closed

**Measurement**: `src/performance_profiler.py:205`

**Monitoring**: `src/asciidoc_artisan/core/resource_monitor.py`

**Targets**:
- Idle: < 200 MB
- Small doc: < 500 MB
- Large doc: < 2 GB
- Memory growth over 1 hour: < 10%

**Test Method**:
1. Monitor memory with psutil
2. Load/close multiple documents
3. Verify memory returns to baseline
4. Run extended session (1 hour+)

---

### NFR-005: Background Threading
**Intent**: Responsive UI during long operations

**Specification**:
- Long-running operations MUST execute in background threads
- Operations include: Git commands, Pandoc conversions, preview rendering
- MUST use Qt QThread for cross-platform compatibility
- MUST NOT perform UI operations from background threads
- MUST communicate via signals/slots only

**Implementation**: `src/asciidoc_artisan/workers/`

**Threading Model**:
```
Main Thread (UI)
    ├── Editor widget
    ├── Preview widget
    └── Signals to workers

Worker Threads (3)
    ├── GitWorker (QThread)
    ├── PandocWorker (QThread)
    └── PreviewWorker (QThread)
```

**Test Method**:
1. Start long operation (e.g., Git push)
2. Verify UI remains responsive
3. Verify can type during operation
4. Verify operation completes successfully

---

### NFR-006: Atomic File Operations
**Intent**: Never corrupt user data

**Specification**:
- All file saves MUST be atomic (temp file + rename)
- MUST prevent corruption on crash, power loss, disk full
- MUST use OS-level atomic rename operation
- MUST clean up temp files on error
- MUST preserve original file if write fails

**Implementation**: `src/asciidoc_artisan/core/file_operations.py:65-118`

**Algorithm**:
1. Write to `<filename>.tmp`
2. Atomic rename `<filename>.tmp` → `<filename>`
3. On error: delete `.tmp`, preserve original

**Guarantees**:
- File is never in partial state
- Either old version or new version exists
- No data loss on interruption

**Test Method**:
1. Simulate crash during save
2. Verify original file intact or new file complete
3. Verify no partial files
4. Test on all platforms

---

### NFR-007: Data Integrity
**Intent**: Never lose user data

**Specification**:
- The system MUST never lose user data due to write failures
- MUST handle: disk full, permission denied, filesystem errors
- MUST show error message with details
- MUST allow retry or save to different location
- MUST keep data in editor even if save fails

**Implementation**: Throughout file operations code

**Error Handling**:
- Disk full → "Insufficient disk space. Free space and retry."
- Permission denied → "Cannot write to file. Check permissions."
- Filesystem error → "Filesystem error: <details>. Try saving elsewhere."

**Recovery**:
1. Show error dialog
2. Keep data in editor
3. Allow retry save
4. Allow save as different file

**Test Method**:
1. Fill disk → attempt save → verify error, data intact
2. Remove write permission → attempt save → verify error, data intact
3. Network drive disconnect → verify error, data intact

---

### NFR-008: Safe Git Operations
**Intent**: Prevent destructive Git commands

**Specification**:
- The system MUST NOT use destructive Git flags without confirmation
- Forbidden flags: `--force`, `--hard`, `--no-verify` (unless user explicitly requests)
- MUST use safe defaults: `git pull` (not `git pull --rebase --force`)
- MUST warn before any operation that could lose data

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py:11`

**Safe Commands**:
- `git add <file>` (safe)
- `git commit -m "<message>"` (safe)
- `git push` (safe, requires remote)
- `git pull` (safe, may require merge)

**Forbidden**:
- `git push --force` (destructive)
- `git reset --hard` (data loss)
- `git clean -fd` (data loss)

**Test Method**:
1. Verify no destructive flags in code
2. Test common operations don't lose data
3. Verify warnings appear for risky operations

---

### NFR-009: Path Traversal Protection
**Intent**: Prevent security vulnerabilities

**Specification**:
- The system MUST sanitize all file paths to prevent directory traversal attacks
- MUST reject paths containing ".." components
- MUST resolve symlinks to real paths
- MUST log rejected paths for security auditing
- MUST return None for invalid paths (not throw exception)

**Implementation**: `src/asciidoc_artisan/core/file_operations.py:27-62`

**Attack Prevention**:
- Input: `../../etc/passwd` → Blocked
- Input: `~/documents/../.ssh/id_rsa` → Blocked
- Input: `/tmp/../etc/passwd` → Blocked

**Test Method**:
1. Attempt to open `../../etc/passwd`
2. Verify rejected with log entry
3. Attempt various traversal patterns
4. Verify all blocked

---

### NFR-010: Subprocess Security
**Intent**: Prevent command injection attacks

**Specification**:
- The system MUST use parameterized subprocess calls (shell=False)
- MUST pass arguments as list, never as string
- MUST NOT use shell=True anywhere in codebase
- MUST validate all inputs to subprocess calls
- MUST NOT allow user input in command construction without validation

**Implementation**: `src/asciidoc_artisan/workers/git_worker.py:94-103`

**Safe Pattern**:
```python
# GOOD
subprocess.run(["git", "commit", "-m", message], shell=False)

# BAD (vulnerable to injection)
subprocess.run(f"git commit -m '{message}'", shell=True)
```

**Test Method**:
1. Code review for shell=True
2. Test with malicious input: `message = "test'; rm -rf /;'"`
3. Verify command not executed
4. Verify input treated as data, not code

---

### NFR-011: No Telemetry
**Intent**: Absolute user privacy

**Specification**:
- The system MUST NOT send any data to external servers (except explicit AI API calls)
- All settings MUST be stored locally
- MUST NOT include: crash reporting, analytics, usage tracking, error reporting
- User MUST NOT need to opt-out (privacy by default)
- Code MUST be auditable for privacy

**Implementation**: No telemetry code exists

**Exceptions**:
- Claude API calls (explicit user feature, optional)
- Pandoc (local process)
- Git (user's own servers)

**Test Method**:
1. Network monitoring during use
2. Verify no unexpected connections
3. Code audit for telemetry libraries
4. Verify settings file contains no identifiers

---

### NFR-012: API Key Handling
**Intent**: Secure API credential management

**Specification**:
- API keys MUST come from environment variables only
- API keys MUST NOT be stored in configuration files
- API keys MUST NOT be logged
- API keys MUST NOT be displayed in UI
- MUST use: ANTHROPIC_API_KEY environment variable

**Implementation**: `src/asciidoc_artisan/core/settings.py:44-46`

**Security Measures**:
- Read from os.environ only
- No persistence
- No logging (even debug logs)
- No display in dialogs

**Test Method**:
1. Search settings file for API key → not found
2. Search logs for API key → not found
3. Set env var → AI works
4. Unset env var → AI disabled

---

### NFR-013: Error Recovery
**Intent**: Graceful error handling

**Specification**:
- The system MUST recover gracefully from all errors without crashing
- MUST use try-except blocks for all risky operations
- MUST show user-friendly error dialogs
- MUST log errors for debugging
- MUST continue running after error

**Implementation**: Throughout codebase with comprehensive exception handling

**Error Categories**:
- File I/O errors → Show dialog, keep editor open
- Network errors → Show dialog, retry option
- Conversion errors → Fallback, show warning
- Git errors → Show dialog, suggest solution

**Test Method**:
1. Trigger various errors
2. Verify no crashes
3. Verify error messages helpful
4. Verify can continue working

---

### NFR-014: Auto-Save
**Intent**: Protect against data loss

**Specification**:
- The system MUST auto-save every 5 minutes to prevent data loss
- Auto-save interval MUST be user-configurable (default: 300 seconds)
- User MUST be able to disable via preferences
- Auto-save MUST NOT interfere with manual saves
- Auto-save MUST use atomic writes

**Implementation**: `src/asciidoc_artisan/ui/file_handler.py`

**Configuration**: `src/asciidoc_artisan/core/settings.py:58-59`

**Test Method**:
1. Make changes
2. Wait 5 minutes
3. Verify file saved automatically
4. Crash app → verify changes saved

---

### NFR-015: Crash Recovery
**Intent**: Resume after unexpected shutdown

**Specification**:
- The system MUST restore last opened file on restart after crash
- MUST restore cursor position
- MUST restore scroll position
- MUST restore unsaved changes if auto-save occurred
- Settings MUST be saved incrementally (not only on clean exit)

**Implementation**: `src/asciidoc_artisan/core/settings.py:50`

**Incremental Saving**:
- Save settings after every file operation
- Save settings after preference changes
- Never rely on clean shutdown

**Test Method**:
1. Open file, make changes
2. Kill process (simulate crash)
3. Restart
4. Verify file reopened
5. If auto-save triggered, verify changes present

---

### NFR-016: Type Hints
**Intent**: Code quality and IDE support

**Specification**:
- All public functions MUST have comprehensive type hints
- MUST include parameter types and return types
- MUST pass mypy type checking
- MUST use typing module for complex types
- Type hints MUST be accurate (not just Any)

**Verification**: mypy type checking

**Example**:
```python
def atomic_save_text(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    ...
```

**Test Method**:
```bash
mypy src/ --strict
```

---

### NFR-017: Documentation
**Intent**: Maintainable codebase

**Specification**:
- All classes and public methods MUST have docstrings
- Docstrings MUST use Google style format
- MUST include: description, arguments, returns, raises, examples (where helpful)
- MUST reference specification requirements (FR-XXX, NFR-XXX)

**Format**:
```python
def function(arg1: str, arg2: int) -> bool:
    """
    One-line summary.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When and why

    Example:
        >>> function("test", 42)
        True
    """
```

**Test Method**:
1. Code review
2. Documentation coverage tool
3. Verify FR/NFR references present

---

### NFR-018: Reading Level
**Intent**: Accessible documentation

**Specification**:
- User-facing documentation MUST be written at Grade 5.0 reading level or below
- MUST use: short sentences, simple words, active voice
- MUST avoid: jargon, complex sentences, passive voice
- Applies to: README, SPECIFICATIONS, help dialogs, error messages

**Measurement**: Flesch-Kincaid Grade Level

**Tools**: `check_readability.py` (if exists)

**Test Method**:
```bash
python check_readability.py README.md
# Output: Grade 5.0 or below
```

**Related Files**:
- `/home/webbp/github/AsciiDoctorArtisan/README.md`
- `/home/webbp/github/AsciiDoctorArtisan/SPECIFICATIONS.md`

---

### NFR-019: Test Coverage
**Intent**: Reliable software through testing

**Specification**:
- The system MUST have 80%+ test coverage
- All critical paths MUST be tested
- All error handling MUST be tested
- Test suite MUST pass 100%
- MUST use pytest framework

**Current Status**: 71/71 tests passing (100% pass rate)

**Implementation**: `src/../tests/`

**Test Method**:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Coverage Targets**:
- Core logic: 90%+
- UI code: 70%+ (harder to test)
- Workers: 90%+
- File operations: 100% (critical)

---

### NFR-020: Accessibility
**Intent**: Usable by all users

**Specification**:
- The system SHOULD support keyboard-only navigation
- All operations MUST be accessible via keyboard shortcuts
- Focus indicators MUST be visible
- Screen reader support SHOULD be considered (future enhancement)
- Color contrast MUST meet WCAG AA standards

**Keyboard Navigation**:
- Tab: Move between UI elements
- Shortcuts: All major operations
- Menus: Accessible via Alt+Key

**Test Method**:
1. Unplug mouse
2. Perform all operations via keyboard
3. Verify all operations accessible

---

### NFR-021: Python Version
**Intent**: Modern Python features and security

**Specification**:
- The system MUST require Python 3.11 or newer
- Recommended: Python 3.12 for best performance
- MUST fail gracefully with error message on older Python
- Error message MUST suggest upgrading Python

**Implementation**: `setup.py`, `pyproject.toml`

**Rationale**:
- Python 3.11: Performance improvements, better type hints
- Python 3.12: Even faster, improved error messages

**Test Method**:
```bash
python3.10 src/main.py
# Should show: "Python 3.11+ required"
```

---

### NFR-022: Platform Support
**Intent**: Cross-platform compatibility

**Specification**:
- The system MUST run on Windows 10+, macOS 12+, Linux (Ubuntu 20.04+)
- MUST use platform-appropriate conventions
- MUST test on all platforms before release
- Platform-specific bugs MUST be documented

**Platform-Specific**:
- File paths: Platform-agnostic (pathlib)
- Settings: QStandardPaths
- Shortcuts: Qt auto-mapping
- Fonts: Platform defaults

**Test Matrix**:
| Platform | Version | Python | Status |
|----------|---------|--------|--------|
| Windows | 10, 11 | 3.11, 3.12 | ✓ |
| macOS | 12+ | 3.11, 3.12 | ✓ |
| Ubuntu | 20.04, 22.04 | 3.11, 3.12 | ✓ |

**Test Method**:
1. Install on each platform
2. Run test suite
3. Manual testing of UI
4. Verify platform conventions followed

---

### NFR-023: Dependency Management
**Intent**: Reproducible builds

**Specification**:
- All production dependencies MUST be pinned to specific versions
- Development dependencies MAY use version ranges
- MUST document all dependencies with purpose
- MUST minimize number of dependencies
- MUST audit dependencies for security

**Implementation**: `requirements-production.txt`

**Version Pinning**:
```
PySide6==6.9.0  # Exact version
asciidoc3==3.2.0  # Exact version
anthropic>=0.40.0  # Minimum version (API compatibility)
```

**Test Method**:
```bash
pip install -r requirements-production.txt
# Verify consistent installation
```

---

## Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Main Window (UI Thread)                  │
│  ┌──────────────┐              ┌──────────────┐        │
│  │   Editor     │◄───sync───►  │   Preview    │        │
│  │  QPlainText  │  scrolling    │ QTextBrowser │        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ Git Worker  │  │Pandoc Worker │  │Preview Worker│
│  (QThread)  │  │   (QThread)  │  │   (QThread)  │
└─────────────┘  └──────────────┘  └──────────────┘
         │                │                │
         ▼                ▼                ▼
   Git Commands    Pandoc/AI API    AsciiDoc3 API
```

### Module Structure

```
src/asciidoc_artisan/
├── core/                    # Business logic
│   ├── settings.py          # Settings model (FR-050)
│   ├── models.py            # Data models
│   ├── file_operations.py   # File I/O (FR-015, FR-016)
│   ├── constants.py         # Constants
│   ├── resource_monitor.py  # Performance monitoring (NFR-004)
│   └── large_file_handler.py # Large files (NFR-003)
│
├── ui/                      # User interface
│   ├── main_window.py       # Main window controller
│   ├── menu_manager.py      # Menu management
│   ├── theme_manager.py     # Theming (FR-041)
│   ├── status_manager.py    # Status bar (FR-045)
│   ├── file_handler.py      # File operations (FR-011-020)
│   ├── export_manager.py    # Export (FR-025-028)
│   ├── preview_handler.py   # Preview (FR-002-004)
│   ├── git_handler.py       # Git UI (FR-031-040)
│   ├── action_manager.py    # Keyboard shortcuts (FR-048)
│   ├── editor_state.py      # Editor state (FR-042, FR-044)
│   ├── settings_manager.py  # Settings persistence (FR-050)
│   ├── dialogs.py           # Dialogs (FR-055)
│   └── line_number_area.py  # Line numbers (FR-005)
│
├── workers/                 # Background workers
│   ├── git_worker.py        # Git operations (FR-031-040)
│   ├── pandoc_worker.py     # Conversion (FR-021-030, FR-054-062)
│   └── preview_worker.py    # Preview rendering (FR-002-004)
│
└── conversion/              # Conversion utilities
    └── document_converter.py # PDF extraction (FR-024)
```

### Data Flow Diagrams

**File Open Flow**:
```
User → File Dialog → Path → FileHandler
                              ↓
                     File type detection
                              ↓
         ┌────────────────────┴──────────────────┐
         │                                        │
    .adoc/.asciidoc                      Other formats
         │                                        │
    Direct load                          PandocWorker
         │                                 ↓ Convert
         └──────────→ Editor ←────────────┘
                        ↓
                   PreviewWorker → Preview
```

**Document Conversion Flow**:
```
User → Export → Format → PandocWorker
                              ↓
                     AI enabled?
                          ┌─Yes─┐
                          │     No
                          │      │
                    ClaudeClient Pandoc
                          │      │
                       Success? ─┘
                          │
                         No
                          │
                     Fallback to Pandoc
                          │
                      Save file
```

### Threading Model

**Main Thread**: UI operations only
- Editor widget
- Preview widget
- Dialogs and menus
- Signal emission

**Worker Threads** (3 separate QThreads):
1. **GitWorker**: Git subprocess execution
2. **PandocWorker**: Document conversion
3. **PreviewWorker**: AsciiDoc rendering

**Communication**: Qt signals/slots (thread-safe)

---

## Dependencies

### Production Dependencies

```python
# GUI Framework (FR-001, FR-002, etc.)
PySide6==6.9.0
PySide6-Addons==6.9.0
PySide6-Essentials==6.9.0

# Document Processing (FR-002, FR-021-030)
asciidoc3==3.2.0
pypandoc==1.11

# PDF Support (FR-024)
pdfplumber==0.11.0

# AI Integration (FR-054-062)
anthropic==0.40.0

# Security (NFR-012)
keyring>=24.3.0

# Performance Monitoring (NFR-004)
psutil>=5.9.0

# Optional Utilities
MarkupSafe==2.1.3
```

### System Dependencies

```bash
# Required
Python 3.11+ (3.12 recommended)
Pandoc 2.x+

# Optional
wkhtmltopdf (for PDF export)
Git 2.x+ (for version control)
```

### Development Dependencies

```python
# Testing (NFR-019)
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-cov>=4.1.0

# Code Quality (NFR-016)
black>=23.12.0
ruff>=0.1.9
mypy>=1.8.0
```

---

## Testing Strategy

### Unit Tests
- All core logic functions
- File operations
- Settings persistence
- Data models

### Integration Tests
- Worker thread communication
- File open/save workflows
- Conversion pipelines

### UI Tests
- Qt test framework (pytest-qt)
- Keyboard shortcuts
- Menu actions
- Dialog interactions

### Performance Tests
- Preview update latency (NFR-001)
- Startup time (NFR-002)
- Large file handling (NFR-003)
- Memory usage (NFR-004)

### Security Tests
- Path traversal attempts (NFR-009)
- Command injection attempts (NFR-010)
- API key handling (NFR-012)

---

## Appendix: Requirement Traceability

### Code to Requirements Mapping

| File | Primary Requirements |
|------|---------------------|
| `main_window.py` | FR-001-053 (Core UI) |
| `preview_worker.py` | FR-002-004, FR-010, NFR-001 |
| `git_worker.py` | FR-031-040, NFR-008, NFR-010 |
| `pandoc_worker.py` | FR-021-030, FR-054-062 |
| `file_operations.py` | FR-015-016, NFR-006-007, NFR-009 |
| `settings.py` | FR-050, FR-061 |
| `large_file_handler.py` | FR-019, NFR-003 |
| `resource_monitor.py` | NFR-004 |
| `theme_manager.py` | FR-041 |
| `ai_client.py` | FR-054-062 |

---

**Document Status**: Complete
**Specification Format**: OpenSpec + Microsoft Spec-Kit Compatible
**Total Requirements**: 85 (62 Functional, 23 Non-Functional)
**Coverage**: 100% of implemented features
**Reverse Engineered**: October 26, 2025
