# AsciiDoc Artisan - Project Specification (Simple Version)

**Version**: 1.1.0
**Date**: 2025-10-23
**Status**: We are building it now
**Type**: Desktop program for Linux, Mac, and Windows

---

## Quick Start (Read This First!)

**What is this program?**

AsciiDoc Artisan helps people write documents. It shows what your document looks like while you type. No need to open a web browser to see your work.

**What can it do?**

- Write AsciiDoc documents (a simple way to format text)
- See a live preview (what it looks like as HTML)
- Change documents to other formats (Word, PDF, Markdown)
- Use AI to make better conversions
- Save your work to Git (version control)
- Works on Linux, Mac, Windows, and WSL

---

## Table of Contents

1. [What This Program Does](#what-this-program-does)
2. [Who Uses This Program](#who-uses-this-program)
3. [User Stories (What People Want)](#user-stories)
4. [What The Program Must Do](#what-the-program-must-do)
5. [How It Should Work](#how-it-should-work)
6. [How We Store Data](#how-we-store-data)
7. [How The Program Is Built](#how-the-program-is-built)
8. [Our Plan To Build It](#our-plan-to-build-it)
9. [How We Know It Works](#how-we-know-it-works)
10. [What We Need](#what-we-need)
11. [Keeping It Safe](#keeping-it-safe)
12. [How We Test It](#how-we-test-it)
13. [Problems We Need To Fix](#problems-we-need-to-fix)
14. [What We Won't Do](#what-we-wont-do)
15. [Word Guide](#word-guide)

---

## What This Program Does

### Main Features

**1. Live Preview (Shows Changes Right Away)**

You type on the left side. The program shows the finished look on the right side. It updates in less than half a second. You never need to press a "preview" button.

**2. Change File Formats (Import and Export)**

You can open Word documents (DOCX files). The program changes them to AsciiDoc. You can save your work as Word, PDF, HTML, or Markdown. The program keeps your headings, lists, and tables.

**3. Smart AI Conversion (Uses Claude AI)**

The AI makes better conversions. It understands complex documents. If the AI doesn't work, the program uses Pandoc instead (automatic backup plan).

**4. Git Support (Save Versions)**

Save your changes to Git right from the editor. You don't need to open a terminal. You can commit, push, and pull.

**5. Works Everywhere (Cross-Platform)**

Same program on Linux, Mac, and Windows. Same buttons, same features. If you know it on one computer, you know it everywhere.

**6. Never Loses Your Work (Safe Saving)**

The program saves files safely. Even if the computer crashes, your file won't break. It writes to a temporary file first, then renames it.

**7. Remembers Your Settings (Session Memory)**

Open the program and it shows your last document. Window size stays the same. Your theme (dark or light) is remembered.

---

### What We Use To Build It

**Programming Language**: Python 3.11 or newer

**Main Tools**:
- PySide6 (makes the windows and buttons)
- asciidoc3 (turns AsciiDoc into HTML)
- pypandoc (changes document formats)
- Pandoc (the actual converter program)
- anthropic (talks to Claude AI)

**Testing Tools**:
- pytest (runs tests automatically)
- pytest-qt (tests the buttons and windows)
- pytest-cov (checks how much we tested)

---

## Who Uses This Program

**1. Technical Writers**

People who write instructions and documentation. They need to see formatting while they work. They work with different file types.

**2. Software Developers**

Programmers who write README files. They write design documents. They need Git support.

**3. Documentation Teams**

Groups who write large documentation projects. They share files using Git. They need reliable software.

**4. Content Creators**

Writers who make long documents. They like plain text files. They want good formatting.

**5. Teachers and Students**

People writing papers and research. They need to export to different formats. They want simple tools.

---

## User Stories

**What are user stories?**

These are things people want to do with the program. Each story shows what someone needs and why they need it.

---

### Story 1: See Changes While I Type (MOST IMPORTANT)

**Who**: A technical writer
**Wants**: To see my document as HTML while I type
**Why**: I can check formatting without opening a browser

**Must Work Like This**:
1. Preview updates in less than half a second (350 milliseconds)
2. The screen never freezes while updating
3. When I scroll the editor, the preview scrolls too
4. If I make a mistake, show me a helpful error message
5. The preview looks like the final document

**Why This Matters**: Writers lose time switching between editor and browser. This saves time and helps them focus.

---

### Story 2: Change Between File Types (VERY IMPORTANT)

**Who**: A documentation professional
**Wants**: To open Word files and save as different formats
**Why**: I work with teams that use different tools

**Must Work Like This**:
1. Open a DOCX file and it becomes AsciiDoc automatically
2. Save my work as HTML, DOCX, PDF, Markdown, or LaTeX
3. Keep my headings, lists, tables, and code blocks
4. Show me clear errors if conversion fails
5. Detect file type by looking at the file extension (.docx, .md, etc.)
6. Binary files (Word, PDF) save to disk, text files show in editor

**Why This Matters**: Different tools use different formats. This program works with all of them.

---

### Story 3: Use Git Without Leaving The Editor (VERY IMPORTANT)

**Who**: A developer writing documentation
**Wants**: To commit and push changes without opening a terminal
**Why**: I want to stay focused on writing

**Must Work Like This**:
1. Detect if my file is in a Git repository (a place that tracks versions)
2. Commit my file with a message I write
3. Push my changes to the server (GitHub, GitLab, etc.)
4. Pull new changes from the server
5. Show me clear errors if login fails
6. Git operations never freeze the screen

**Why This Matters**: Opening a terminal breaks concentration. This keeps the workflow smooth.

---

### Story 4: Remember My Workspace (IMPORTANT)

**Who**: A regular user
**Wants**: The program to remember my last file and window setup
**Why**: I can start working immediately when I open the program

**Must Work Like This**:
1. Open my last document automatically
2. Remember window size and position
3. Remember if I use dark mode or light mode
4. Remember how I split the editor and preview (50/50, 60/40, etc.)
5. Remember my font zoom level
6. Remember the last folder I used

**Why This Matters**: Setting up the workspace every time wastes time.

---

### Story 5: Use Keyboard For Everything (IMPORTANT)

**Who**: A power user (someone who works fast)
**Wants**: Keyboard shortcuts for all actions
**Why**: Using the mouse slows me down

**Must Work Like This**:
1. File actions: Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save), Ctrl+Shift+S (Save As)
2. Edit actions: Ctrl+F (Find), Ctrl+G (Go to Line), Ctrl+Z (Undo), Ctrl+Y (Redo)
3. View actions: Ctrl+D (Dark Mode), Ctrl+Plus (Zoom In), Ctrl+Minus (Zoom Out), Ctrl+0 (Reset Zoom)
4. On Mac, use Cmd key instead of Ctrl
5. Show shortcuts in the menus
6. Don't use shortcuts that the computer already uses

**Why This Matters**: Keyboard is faster than mouse for experienced users.

---

### Story 6: Choose Light Or Dark Mode (NICE TO HAVE)

**Who**: A user with vision preferences
**Wants**: To switch between light and dark themes
**Why**: Dark mode is easier on my eyes at night

**Must Work Like This**:
1. Dark mode has high contrast (easy to read)
2. Light mode is the default
3. Press F5 or Ctrl+D to switch
4. Theme changes instantly (no restart needed)
5. Remember my theme choice
6. Both themes must be readable

**Why This Matters**: People have different preferences. Some rooms are bright, some are dark.

---

### Story 7: Use AI For Better Conversions (IMPORTANT)

**Who**: A technical writer
**Wants**: AI-powered conversion for complex documents
**Why**: AI preserves complicated formatting better than simple converters

**Must Work Like This**:
1. I can choose to use AI or not (my choice)
2. AI keeps complex lists, tables, code blocks, and special notes
3. If AI fails, use Pandoc automatically (backup plan)
4. Show me progress for long conversions
5. Complete conversion in 30 seconds for 50-page documents
6. Show clear error messages if API fails, then use Pandoc

**Why This Matters**: Complex documents lose formatting in simple converters. AI understands structure better.

---

## What The Program Must Do

**What are requirements?**

Requirements are specific things the program MUST do. We have 62 main requirements and 20 performance requirements.

---

### Requirements for Editing Documents (FR-001 to FR-010)

**FR-001: Plain Text Editor**

The program has a text editor for AsciiDoc. It uses a monospace font (all letters same width). It knows AsciiDoc syntax (special formatting rules).

- **What is monospace?** A font where 'i' takes the same space as 'w'
- **Why this matters**: Code and plain text are easier to read

**FR-002: Live HTML Preview**

The program shows HTML preview next to the editor. The preview updates automatically. It's like seeing your final webpage.

**FR-003: Auto-Update Preview**

When you type, the preview updates by itself. You don't press any buttons. It just works.

**FR-004: Smart Waiting (Debouncing)**

The program waits 350 milliseconds before updating. This saves computer power.

- **What is debouncing?** Waiting a tiny bit so the computer doesn't work too hard
- **Why 350ms?** Fast enough you don't notice, slow enough to save power

**FR-005: Show Unsaved Changes**

The window title shows an asterisk (*) if you haven't saved. This reminds you to save your work.

**FR-006: Wrap Long Lines**

Long lines wrap to the next line (like in a word processor). You don't scroll sideways. This is on by default.

**FR-007: Sync Scrolling**

When you scroll the editor, the preview scrolls to match. You always see the same section.

- **What is sync?** Making two things move together

**FR-008: Resizable Panes**

You can drag the divider between editor and preview. Make the editor bigger or the preview bigger. Your choice.

**FR-009: Remember Pane Sizes**

The program remembers how you split the panes. Next time you open it, it's the same.

**FR-010: Background Rendering**

The preview renders in the background. Your screen never freezes. You can keep typing while it renders.

- **What is rendering?** Turning AsciiDoc into HTML (like cooking raw food into a meal)
- **What is background?** Happening while you do other things

---

### Requirements for Files (FR-011 to FR-020)

**FR-011: Open AsciiDoc Files**

The program opens .adoc and .asciidoc files directly. No conversion needed.

**FR-012: Save With Keyboard**

Press Ctrl+S (or Cmd+S on Mac) to save your file. Quick and easy.

**FR-013: Save As Different Name**

You can save your document with a new name or in a new folder. This makes a copy.

**FR-014: Warn Before Closing**

If you have unsaved changes, the program asks "Do you want to save?" This prevents accidents.

**FR-015: Safe Saving (Atomic Writes)**

The program saves files safely. It writes to a temporary file first. Then it renames the file. If the computer crashes, your original file is still safe.

- **What is atomic?** All-or-nothing (either completely works or doesn't happen at all)
- **Why this matters**: Prevents corrupted files

**FR-016: Clean File Paths (Sanitization)**

The program checks all file paths for safety. It prevents hackers from accessing wrong folders.

- **What is path sanitization?** Cleaning up file paths to block tricks like "../../../secret_file"

**FR-017: Check Paths Exist**

Before opening or saving, the program checks if folders exist. Shows errors if paths are invalid.

**FR-018: Detect Encoding**

The program detects how the file is encoded (UTF-8, ASCII, etc.). Uses UTF-8 by default (supports all languages).

- **What is encoding?** How text is stored in computer files

**FR-019: Keep Line Endings**

Different systems use different line endings (Windows vs Mac vs Linux). The program keeps whatever the file already uses.

**FR-020: Update Window Title**

The window title shows the current file path. Shows an asterisk (*) if you have unsaved changes.

---

### Requirements for Converting Formats (FR-021 to FR-030)

**FR-021: Auto-Detect Format**

The program looks at the file extension (.docx, .md, .html, etc.). It knows what format each file uses.

**FR-022: Convert Word to AsciiDoc**

Open a Word document (DOCX). The program automatically converts it to AsciiDoc. You can start editing immediately.

**FR-023: Export to Many Formats**

Save your AsciiDoc as:
- HTML (web pages)
- DOCX (Microsoft Word)
- PDF (portable documents)
- Markdown (another simple format)
- LaTeX (for scientific papers)

**FR-024: Keep Document Structure**

Conversion keeps your headings, lists, tables, and code blocks. The structure stays the same.

- **What is structure?** How your document is organized (title, sections, bullets)

**FR-025: Choose Export Format**

A dialog box lets you pick the output format. You see all choices clearly.

**FR-026: Background Conversion**

Conversions happen in the background. Your screen stays responsive. You can cancel if it takes too long.

**FR-027: Show Conversion Errors**

If conversion fails, you see a friendly error message. It tells you what went wrong and what to do.

**FR-028: Check Pandoc On Startup**

When the program starts, it checks if Pandoc is installed. Pandoc is the tool that does conversions.

**FR-029: Safe Command Execution**

All commands to Pandoc use safe inputs. This prevents hacker attacks called "command injection."

- **What is command injection?** A trick where hackers run evil commands by hiding them in file names

**FR-030: Handle Different Output Types**

Text formats (HTML, Markdown) show in the editor. Binary formats (Word, PDF) save to a file. This makes sense for each type.

---

### Requirements for Git (FR-031 to FR-040)

**FR-031: Detect Git Repository**

The program checks if your file is in a Git folder (repository). Git is a version control system.

- **What is Git?** A tool that tracks changes to your files over time
- **What is a repository?** A folder where Git stores all versions

**FR-032: Enable Git Menu When Available**

Git menu buttons only work when your file is in a Git repository. Otherwise, they're grayed out.

**FR-033: Commit With Message**

Save your changes to Git with a message explaining what you did. The commit records your changes.

- **What is a commit?** Saving a snapshot of your file in Git history

**FR-034: Auto-Stage Before Commit**

The program automatically runs `git add` before committing. You don't need to do it manually.

- **What is staging?** Telling Git which files to include in the commit

**FR-035: Push to Server**

Push your commits to GitHub, GitLab, or another server. This backs up your work.

- **What is push?** Sending your changes to a server

**FR-036: Pull from Server**

Get new changes from the server. This downloads updates other people made.

- **What is pull?** Getting changes from a server
- **Why rebase?** Makes history cleaner (rebases your changes on top of new changes)

**FR-037: Background Git Operations**

All Git operations happen in the background. Your screen never freezes. You can keep working.

**FR-038: Safe Git Commands**

All Git commands use safe inputs. No command injection possible (prevents hacking).

**FR-039: Show Git Results**

After any Git operation, you see a message. Success: "Committed successfully." Failure: Shows the error.

**FR-040: Never Store Git Passwords**

The program never saves your GitHub password or SSH keys. It uses your computer's stored credentials.

- **Why this matters**: Storing passwords in programs is unsafe

---

### Requirements for User Interface (FR-041 to FR-053)

**FR-041: Dark and Light Themes**

The program has two themes: dark mode and light mode. You can switch anytime.

**FR-042: Readable Contrast**

Both themes meet WCAG AA standards. This means good contrast between text and background.

- **What is WCAG AA?** A standard that ensures people with vision problems can read the screen
- **Why this matters**: Accessibility for everyone

**FR-043: Remember Font Size**

Your font zoom level is saved. Next time you open the program, it's the same size.

**FR-044: Zoom With Keyboard**

- Ctrl+Plus: Make text bigger
- Ctrl+Minus: Make text smaller
- Ctrl+0: Reset to normal size

**FR-045: Remember Split Ratio**

The program remembers how you split the editor and preview panes (50/50, 60/40, etc.).

**FR-046: Status Bar Information**

The status bar at the bottom shows:
- Current file path
- Current line number
- Current column number

**FR-047: Menu Bar**

The program has these menus: File, Edit, Tools, Git, View, Help. All features are in these menus.

**FR-048: Smart Keyboard Shortcuts**

On Windows and Linux: Use Ctrl key
On Mac: Use Cmd key
The program knows which computer you're using and adapts.

**FR-049: Remember Window Position**

The program remembers:
- Window size
- Window position on screen
- Whether the window was maximized (full screen)

**FR-050: Works on All Computers**

Exactly the same program on Linux, Mac, Windows, and WSL (Windows Subsystem for Linux). No differences.

**FR-051: Use Correct Config Folder**

The program stores settings in the right place for each system:
- Linux: ~/.config/AsciiDoc Artisan/
- Mac: ~/Library/Application Support/AsciiDoc Artisan/
- Windows: %APPDATA%/AsciiDoc Artisan/

**FR-052: Find Text (Search)**

Press Ctrl+F to search for text in your document. A search box appears.

**FR-053: Go To Line Number**

Press Ctrl+G to jump to a specific line number. Useful in long documents.

---

### Requirements for AI Conversion (FR-054 to FR-062)

**FR-054: Use Claude AI**

The program connects to Claude AI (by Anthropic). This makes better conversions for complex documents.

- **What is Claude?** An AI that understands documents like a human
- **Why use AI?** It preserves complicated formatting better than simple converters

**FR-055: AI Is Optional**

You can turn AI conversion on or off in settings. It's your choice. AI costs money (API fees).

- **What is an API?** A way for programs to talk to each other
- **What are API fees?** You pay for each AI conversion (like paying per usage)

**FR-056: AI Handles Complex Documents**

The AI understands:
- Nested lists (lists inside lists)
- Complex tables (with merged cells)
- Code blocks (programming examples)
- Special notes (warnings, tips, important boxes)

**FR-057: Automatic Backup Plan (Fallback)**

If AI fails or isn't available, use Pandoc automatically. You always get a conversion.

- **What is fallback?** A backup plan that runs if the first plan fails

**FR-058: Check API Key At Start**

When you use AI conversion, the program checks if your API key works. It makes a small test request.

- **What is an API key?** A password that lets you use Claude AI

**FR-059: Show Progress**

Long conversions show a progress bar or status message. You know the program is working.

**FR-060: Handle AI Errors Well**

If AI conversion fails:
1. Try again up to 3 times (with increasing wait time)
2. If still fails, use Pandoc automatically
3. Show you a clear error message

**FR-061: Keep API Keys Safe**

Your API key is stored in an environment variable (a safe place). Never stored in plain text files.

- **What is an environment variable?** A secure place to store passwords and keys
- **Why this matters**: Prevents your API key from being stolen

**FR-062: Protect Against Rate Limits**

If you use AI too much, Claude API might say "slow down." The program:
1. Waits before trying again
2. Waits longer each time (2 seconds, 4 seconds, 8 seconds)
3. Gives up after 3 tries and uses Pandoc instead

- **What is rate limiting?** When a service makes you slow down to prevent overuse

---

## How It Should Work

**What are non-functional requirements?**

These describe how well the program should work. Not what it does, but how fast, how safe, how easy to use.

---

### Speed Requirements (How Fast)

**NFR-001: Preview Speed**

Preview updates in less than 350 milliseconds. That's about 1/3 of a second. You won't notice any delay.

**NFR-002: Startup Speed**

The program opens in less than 3 seconds. From click to ready.

**NFR-003: Large Documents**

Documents up to 10,000 lines stay smooth and responsive. No lag or freezing.

**NFR-004: Memory Use**

The program uses less than 500 megabytes of memory for typical documents (under 5,000 lines).

- **What is memory?** Computer RAM (Random Access Memory)
- **Why 500MB?** Small enough to not slow down your computer

**NFR-005: Background Operations**

All slow operations (rendering, Git, file conversion, AI) run in the background. The screen never freezes.

---

### Reliability Requirements (Keeping Your Data Safe)

**NFR-006: Safe Saves**

All file saves are "atomic" (all-or-nothing). Either the file saves completely or it doesn't save at all. Never a half-saved corrupted file.

**NFR-007: Never Lose Data**

If saving fails, your original file stays safe. You see an error message and can try again.

**NFR-008: Safe Git Operations**

Git operations never use dangerous "force" commands. Never deletes history unless you specifically ask.

**NFR-009: Prevent Path Hacking**

All file paths are checked for safety. Hackers can't use tricks like "../../secret_file" to access wrong folders.

**NFR-010: Prevent Command Hacking**

All commands to Git and Pandoc use safe methods. Hackers can't inject evil commands through file names.

- **What is command injection?** Hiding evil commands in normal inputs

---

### Ease of Use Requirements (User-Friendly)

**NFR-011: Easy First Use**

90% of users should complete their first task without reading a manual. The program should be obvious.

**NFR-012: Keyboard Access**

Every major feature has a keyboard shortcut. Power users can work without touching the mouse.

**NFR-013: Helpful Error Messages**

Errors are shown in plain English (or your language). No programmer jargon. Tell users what to do.

**Example:**
- Bad: "IOError: errno 2"
- Good: "Cannot find file 'document.adoc'. Check if the file exists."

**NFR-014: Good Contrast**

Text is easy to read in both light and dark modes. Meets WCAG AA standards (vision accessibility).

**NFR-015: Same on All Systems**

Linux, Mac, Windows users get the exact same features. No missing features on any system.

---

### Code Quality Requirements (For Developers)

**NFR-016: Type Hints**

All Python code includes type hints. This helps prevent bugs and makes code clearer.

- **What are type hints?** Notes that say what kind of data each function uses

**NFR-017: Documentation Comments**

All functions and classes have docstrings (explanation comments). Other developers can understand the code.

**NFR-018: Good Logging**

The program writes log files with INFO, WARNING, and ERROR messages. Never logs passwords or personal data.

**NFR-019: Test Coverage**

80% of code is covered by automated tests. This prevents bugs from sneaking in.

- **What is test coverage?** Percentage of code that automated tests check

**NFR-020: Minimal Dependencies**

Only use necessary libraries. Each dependency must be justified. Fewer dependencies = less chance of security problems.

---

## How We Store Data

**What is a data model?**

The data model shows what information the program stores and how it's organized.

---

### Main Data Types (Entities)

We have 7 main types of data the program works with:

1. **Document** - The file you're editing
2. **EditorState** - How the editor looks right now
3. **PreviewState** - The HTML preview
4. **Settings** - Your preferences
5. **GitRepository** - Git information
6. **ConversionJob** - A file conversion task
7. **ClaudeAIClient** - AI conversion system

---

### 1. Document (The File You Edit)

**What is it?**

This represents the AsciiDoc file you're currently editing.

**What does it store?**

- **file_path**: Where the file is saved (or None if new unsaved file)
- **content**: The text inside the file
- **modified**: True if you made changes since last save
- **encoding**: How text is stored (usually UTF-8)
- **line_ending**: Windows (\\r\\n) or Unix (\\n) style

**How does it change?**

```
New Document (not saved yet)
  ↓ (you type something)
Modified Document (has unsaved changes)
  ↓ (you press Save)
Saved Document (safe on disk)
  ↓ (you type more)
Modified Document (unsaved changes again)
```

**Safety Rules:**

- File path must be cleaned to prevent hacking
- Modified flag changes to True whenever you type
- Encoding must be a valid type

---

### 2. EditorState (How The Editor Looks)

**What is it?**

This stores how your editor is set up right now.

**What does it store?**

- **font_family**: Which font (usually "Monospace")
- **font_size**: How big the letters are (default: 12 points)
- **zoom_level**: How much you zoomed in or out
- **cursor_line**: Which line your cursor is on
- **cursor_column**: Which column your cursor is in
- **word_wrap**: Whether long lines wrap (True or False)
- **tab_width**: How many spaces for Tab key (default: 4)

**Is this saved?**

No. The program doesn't remember this. It starts fresh each time.

**Safety Rules:**

- Font size between 8 and 72 points (reasonable range)
- Zoom level between -5 and +10 (prevents too tiny or huge text)
- Tab width between 2 and 8 spaces

---

### 3. PreviewState (The HTML Display)

**What is it?**

This stores the HTML preview information.

**What does it store?**

- **html_content**: The rendered HTML code
- **scroll_position**: How far down you scrolled
- **rendering**: True if currently making HTML (in progress)
- **last_render_time**: When the last preview finished
- **render_error**: Error message if rendering failed

**How does it change?**

```
Idle (waiting)
  ↓ (you type something)
Wait 350ms (debounce timer)
  ↓ (timer finishes)
Rendering (making HTML)
  ↓ (finished)
Idle (with new HTML)
```

**Scroll Sync Math:**

When you scroll the editor, the preview scrolls to match:

```
preview_scroll = (editor_scroll / editor_max) * preview_max
```

This keeps them synchronized.

---

### 4. Settings (Your Preferences)

**What is it?**

Your personal preferences that are saved when you close the program.

**What does it store?**

- **last_directory**: Last folder you used
- **last_file**: Last document you edited
- **git_repo_path**: Git folder location (if any)
- **dark_mode**: True for dark theme, False for light theme
- **maximized**: True if window was full screen
- **window_geometry**: Window size and position
- **splitter_sizes**: How you split editor/preview (like [600, 600])
- **font_size**: Your zoom level
- **auto_save_enabled**: Whether auto-save is on
- **auto_save_interval**: How often to auto-save (seconds)
- **ai_conversion_enabled**: Whether to use AI conversion

**Where is this saved?**

In a JSON file (a text file with structured data):

- Linux: ~/.config/AsciiDoc Artisan/AsciiDocArtisan.json
- Mac: ~/Library/Application Support/AsciiDoc Artisan/AsciiDocArtisan.json
- Windows: %APPDATA%/AsciiDoc Artisan/AsciiDocArtisan.json

**Example JSON:**

```json
{
  "last_directory": "/home/user/documents",
  "last_file": "/home/user/documents/example.adoc",
  "dark_mode": true,
  "maximized": false,
  "window_geometry": [100, 100, 1200, 800],
  "splitter_sizes": [600, 600],
  "font_size": 14,
  "auto_save_enabled": true,
  "auto_save_interval": 300,
  "ai_conversion_enabled": false
}
```

**Security Note:**

API keys are NEVER stored here. They must be in environment variables (a safer place).

---

### 5. GitRepository (Version Control Info)

**What is it?**

Information about the Git repository (version control folder) for your document.

**What does it store?**

- **repo_path**: Where the Git folder is
- **has_remote**: True if connected to GitHub/GitLab
- **remote_url**: The server address (like github.com/user/project)
- **current_branch**: Which branch you're on (like "main" or "dev")
- **is_dirty**: True if you have uncommitted changes
- **ahead_count**: How many commits you haven't pushed
- **behind_count**: How many commits you haven't pulled

**How is it detected?**

The program runs this command: `git rev-parse --git-dir`

If it works, you're in a Git repository.

**Is this saved?**

No. The program checks fresh each time you open it.

---

### 6. ConversionJob (Format Change Task)

**What is it?**

A task to convert a document from one format to another.

**What does it store?**

- **source_path**: The file to convert
- **source_format**: What format it is now (like "docx")
- **target_format**: What format you want (like "asciidoc")
- **output_path**: Where to save result (or None to show in editor)
- **pandoc_options**: Extra settings for Pandoc
- **use_ai_conversion**: True to use Claude AI
- **status**: "pending", "running", "completed", or "failed"
- **error_message**: What went wrong (if it failed)
- **start_time**: When it started
- **end_time**: When it finished

**How does it change?**

```
Pending (waiting to start)
  ↓ (worker thread picks it up)
Running (converting now)
  ↓ (if successful)
Completed (done!)
  OR
  ↓ (if failed)
Failed (with error message)
```

**The Conversion Process:**

1. You open a Word file or click Export
2. Program detects format (by file extension)
3. Creates a ConversionJob
4. Sends job to PandocWorker (background worker)
5. Worker runs Pandoc or Claude AI
6. Worker sends result back
7. Main program shows result or saves to file

---

### 7. ClaudeAIClient (AI Converter)

**What is it?**

The system that talks to Claude AI for smart conversions.

**What does it store?**

- **api_key**: Your Anthropic API key (from environment variable)
- **model**: Which Claude model to use (default: claude-3-5-sonnet-20241022)
- **max_retries**: How many times to retry (default: 3)
- **timeout**: How long to wait (default: 60 seconds)

**What can it do?**

- **validate_api_key()**: Check if your API key works
- **convert_document(...)**: Convert a document using AI
- **estimate_tokens(text)**: Guess how many tokens (pieces) in text
- **can_handle_document(text)**: Check if document is small enough

**Security:**

- API key comes from environment variable ANTHROPIC_API_KEY
- Never saved to files or settings
- Never shown in logs or error messages

---

### How Data Types Connect

```
Settings (saved preferences)
  ↓ points to last file
Document (your current file)
  ↓ rendered by          ↓ tracked by
PreviewState             GitRepository
(the HTML)               (version control)
  ↓ converted by
ConversionJob
(format changes)
  ↓ may use
ClaudeAIClient
(AI conversion)
```

---

### Where Data Lives

**Saved Forever:**
- Settings (in JSON file in config folder)
- Documents (in files you choose to save)

**Temporary (Forgotten When Closed):**
- EditorState (your cursor position, etc.)
- PreviewState (the HTML preview)
- GitRepository (checked fresh each time)
- ConversionJob (only exists while converting)
- ClaudeAIClient (created when needed)

---

## How The Program Is Built

**What is architecture?**

Architecture is how the program's parts are organized and how they work together.

---

### The Main Pattern: MVC (Model-View-Controller)

**What is MVC?**

A way to organize programs into three parts:

1. **Model**: The data (documents, settings, etc.)
2. **View**: What you see (windows, buttons, editor, preview)
3. **Controller**: The brain (handles your clicks and keystrokes)

**Why use MVC?**

It keeps the program organized. Each part has one job. Easy to understand and fix.

---

### The Three Layers

```
┌─────────────────────────────────────────┐
│           VIEW LAYER                    │
│   (What you see on screen)              │
│                                          │
│   ┌──────────┐      ┌───────────────┐  │
│   │  Editor  │      │   Preview     │  │
│   │  Pane    │      │   Pane        │  │
│   │  (Type   │      │   (Shows      │  │
│   │  here)   │      │   HTML)       │  │
│   └──────────┘      └───────────────┘  │
│                                          │
│   Menus: File | Edit | Tools | Git     │
│   Status Bar: Shows file and position   │
└─────────────────────────────────────────┘
           ↓ You click or type
┌─────────────────────────────────────────┐
│        CONTROLLER LAYER                 │
│   (The brain - handles events)          │
│                                          │
│   AsciiDocEditor (Main Controller)     │
│   - Handles clicks and keystrokes       │
│   - Manages the current file            │
│   - Tells workers what to do            │
│   - Updates the view                    │
└─────────────────────────────────────────┘
           ↓ Sends tasks to
┌─────────────────────────────────────────┐
│         MODEL LAYER                     │
│   (Workers that do hard jobs)           │
│                                          │
│   ┌──────────┐ ┌──────────┐ ┌────────┐ │
│   │ Preview  │ │   Git    │ │ Pandoc │ │
│   │ Worker   │ │  Worker  │ │ Worker │ │
│   │ (Make    │ │ (Save to │ │(Convert│ │
│   │  HTML)   │ │  Git)    │ │formats)│ │
│   └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────┘
           ↓ Uses
┌─────────────────────────────────────────┐
│       EXTERNAL TOOLS                    │
│   (Programs we use)                     │
│                                          │
│   AsciiDoc3  |  Git CLI  |  Pandoc     │
│   Claude AI  |  File System             │
└─────────────────────────────────────────┘
```

---

### How Preview Works (Step by Step)

**The Journey From Typing To Preview:**

1. **You type** in the editor → Editor sends "text changed" signal
2. **Timer starts** → Wait 350 milliseconds (debounce)
3. **Timer finishes** → Controller says "update preview now"
4. **Send to worker** → PreviewWorker gets the text
5. **Worker makes HTML** → Uses AsciiDoc3 to render
6. **Worker finishes** → Sends "preview ready" signal with HTML
7. **Main thread gets HTML** → Updates the preview pane
8. **Scroll sync** → Matches scroll position

**Why use a timer?**

If you type "hello" fast, the program would update 5 times (h, he, hel, hell, hello). That wastes computer power. The timer waits until you stop typing for a moment.

---

### How File Saving Works (Step by Step)

**The Safe Save Process:**

1. **You press Ctrl+S** → Controller runs save function
2. **Check if new file** → If new, ask where to save
3. **Validate path** → Check path is safe (no hacker tricks)
4. **Write to temp file** → Write content to "document.adoc.tmp"
5. **Verify write** → Check the temp file is correct
6. **Atomic rename** → Rename temp file to real file (instant operation)
7. **Update window** → Remove asterisk (*) from title
8. **Save path** → Remember file path in settings

**Why write to temp file first?**

If the computer crashes while saving, your original file is safe. The temp file might be broken, but your real file is untouched. Then we rename the temp file (renaming is instant and safe).

---

### How AI Conversion Works (Step by Step)

**The AI Conversion Journey:**

1. **You choose conversion** → Select AI-enhanced option
2. **Check API key** → Read ANTHROPIC_API_KEY from environment
3. **Create AI client** → Make ClaudeClient object
4. **Check document size** → Make sure it's not too big (under 50,000 tokens)
5. **Send to worker** → PandocWorker gets job with use_ai_conversion=True
6. **Worker calls AI** → Send document to Claude API
7. **Wait for response** → Show progress messages
8. **If AI fails** → Try up to 3 times
9. **If still fails** → Use Pandoc instead (automatic backup)
10. **Return result** → Send converted document back
11. **Show in editor** → Display the result

**Fallback Situations (When We Use Pandoc Instead):**

- No API key found
- Document too large (over 50,000 tokens)
- API returns error 3 times
- Rate limit exceeded (too many requests)
- Network connection fails
- Unexpected error occurs

**Why have a backup plan?**

AI is great but not perfect. Sometimes it's unavailable or your document is too big. Pandoc always works (local tool on your computer). You always get a conversion, even if not AI-enhanced.

---

### Why We Made These Choices

**Choice 1: Worker Threads For Slow Jobs**

**What**: Separate threads for rendering, Git, Pandoc, AI
**Why**: Keeps the screen responsive (never freezes)
**Trade-off**: More complex code, but better user experience

**Choice 2: Debounce Timer (350ms)**

**What**: Wait 350 milliseconds before updating preview
**Why**: Saves computer power, still feels instant
**Trade-off**: Tiny delay vs. much better performance

**Choice 3: Safe File Saving (Atomic Writes)**

**What**: Write to temp file, then rename
**Why**: Protects against file corruption if crash happens
**Trade-off**: Extra disk operations, but zero chance of data loss

**Choice 4: AI Fallback Architecture**

**What**: Try AI first, automatically use Pandoc if AI fails
**Why**: Best quality when available, reliability when not
**Trade-off**: More complex logic, but users always get results

**Choice 5: Environment Variable For API Key**

**What**: Store API key in ANTHROPIC_API_KEY environment variable
**Why**: Security best practice, prevents key theft
**Trade-off**: Users must set up environment variable (extra step)

---

## Our Plan To Build It

**What is an implementation plan?**

The step-by-step plan to build the program. What we already built and what comes next.

---

### What We Already Built ✅

**Phase 0-9: Core Features (COMPLETE)**

We built:
- Basic editor and preview windows
- File open and save
- Format conversion with Pandoc
- Git integration (commit, push, pull)
- Dark and light themes
- Keyboard shortcuts
- Settings that are remembered
- Cross-platform testing (Linux, Mac, Windows)
- Complete documentation

**Phase 10: AI Integration (COMPLETE)**

We added:
- Claude AI client (claude_client.py)
- AI-enhanced conversion
- Automatic fallback to Pandoc
- Retry logic with backoff
- Progress indicators
- Security for API keys
- Settings for AI option

---

### What We're Building Now 🔨

**Phase 11: Test Suite (IN PROGRESS)**

**What**: Automated tests for all features

**Tests We Have:**
- ✅ Settings tests (5 tests, all passing)
- ✅ File operations tests (9 tests, all passing)

**Tests We Need:**
- ⏳ Claude client tests (with fake AI responses)
- ⏳ Pandoc conversion tests
- ⏳ Git operation tests
- ⏳ GUI tests (testing buttons and windows)
- ⏳ Performance tests (measuring speed)

**Goal**: 80% of code covered by tests

**Why**: Tests catch bugs before users see them

---

### What's Coming Next 📋

**Phase 12: AI User Interface (PLANNED)**

**What**: Add UI controls for AI conversion

**Tasks:**
1. Add "Use AI Conversion" checkbox in Export dialog
2. Add "Use AI Conversion" checkbox when opening Word files
3. Show AI progress in status bar
4. Show message when falling back to Pandoc
5. Add help text explaining API key setup

**Phase 13: Fix Technical Debt (PLANNED)**

**What**: Clean up and improve code

**Tasks:**
1. Replace old Qt functions (deprecated HighDPI code)
2. Split large files if they get too big (over 3,000 lines)
3. Make error messages more consistent
4. Improve logging for debugging

---

## How We Know It Works

**What are success criteria?**

These are specific things we can measure to know if the program works well.

---

### User Experience Measures (Did We Make Users Happy?)

**SC-001: Fast Preview**

Preview updates in less than 250 milliseconds (1/4 second). Users won't notice any delay.

**How to measure**: Use a timer to measure from keypress to preview update.

**SC-002: Fast Startup**

Program opens in less than 3 seconds. From click to ready.

**How to measure**: Time from launching to first usable window.

**SC-003: Handle Large Documents**

Documents over 10,000 lines stay smooth. No freezing or lag.

**How to measure**: Open a 10,000-line document and type. Should feel responsive.

**SC-004: No Data Loss**

Files are never corrupted or lost. Users can trust the program.

**How to measure**: Save files 1,000 times. Check all files are valid. Pull the plug randomly and check files aren't broken.

**SC-005: Good Conversions**

Format conversions keep 95% of structure (headings, lists, tables).

**How to measure**: Convert test documents and manually check quality.

**SC-006: Keyboard Power Users**

All common tasks (open, edit, save, commit) work with keyboard only.

**How to measure**: Try to use the program without touching the mouse.

**SC-007: Easy First Use**

90% of new users complete their first task without help.

**How to measure**: Watch new users try the program. Count how many succeed without asking questions.

**SC-008: Cross-Platform Consistent**

Same features on Linux, Mac, Windows. No missing features anywhere.

**How to measure**: Test checklist of features on each platform. Must all work.

**SC-009: Settings Remembered**

Window size, theme, last file remembered 99% of the time.

**How to measure**: Close and reopen 100 times. Check settings persist.

**SC-010: Git Reliability**

Git commits work 100% of the time (when Git is set up correctly).

**How to measure**: Commit 100 times. All should work (assuming valid Git setup).

---

### AI Conversion Measures (Does AI Work Well?)

**SC-011: Reduces Manual Work**

AI conversion reduces cleanup time by 70% compared to regular Pandoc.

**How to measure**: Time how long cleanup takes with Pandoc vs. AI. AI should be 70% faster.

**SC-012: Handles Complex Formatting**

AI successfully converts 95% of complex documents (nested lists, tables, code).

**How to measure**: Test 100 complex documents. Count successes.

**SC-013: Speed**

AI conversion finishes in 30 seconds for 50-page documents.

**How to measure**: Convert various 50-page documents. Time each conversion.

**SC-014: Fast Fallback**

Falls back to Pandoc in under 5 seconds if AI fails.

**How to measure**: Simulate AI failures. Time how long until Pandoc starts.

---

### Business Measures (Is The Project Successful?)

**SC-015: User Satisfaction**

Users report better productivity compared to using separate editor and browser.

**How to measure**: Survey users. Ask if they're more productive.

**SC-016: Easy Migration**

Technical writers can switch from other tools within one day.

**How to measure**: Time how long it takes writers to become comfortable.

**SC-017: Reliability Reputation**

Support requests about data loss stay under 0.1% of users.

**How to measure**: Track support tickets. Calculate percentage.

**SC-018: Conversion Success Rate**

Users successfully convert documents on first try 85% of the time (95% with AI).

**How to measure**: Track conversion attempts vs. successes. Log success rates.

---

### Technical Measures (Code Quality)

**SC-019: Test Coverage**

80% of code is covered by automated tests.

**How to measure**: Run pytest-cov. Check coverage percentage.

**SC-020: Zero Critical Security Bugs**

No path traversal, command injection, or API key exposure bugs.

**How to measure**: Security audit. Penetration testing. Code review.

**SC-021: Memory Efficiency**

Uses less than 500MB for typical documents (under 5,000 lines).

**How to measure**: Open typical documents and check memory usage.

**SC-022: Clean Code**

Passes linting (Ruff) and type checking (mypy strict) with zero warnings.

**How to measure**: Run Ruff and mypy. Count warnings (should be zero).

---

## What We Need

**What are dependencies and assumptions?**

Dependencies are tools and libraries we need. Assumptions are things we believe are true.

---

### Tools We Use

**Core Programming:**
- **Python 3.11 or newer**: The programming language
- **PySide6 version 6.9.0 or newer**: Makes windows and buttons (Qt library)
- **asciidoc3**: Turns AsciiDoc into HTML
- **pypandoc**: Python wrapper for Pandoc
- **Pandoc**: The actual document converter (separate program)
- **Git**: Version control (optional, only needed for Git features)

**AI Features:**
- **anthropic version 0.40.0 or newer**: Talks to Claude AI
- **Anthropic API Key**: Your personal key (get from Anthropic website)

**Testing:**
- **pytest version 7.4.0 or newer**: Runs tests
- **pytest-qt version 4.2.0 or newer**: Tests GUI features
- **pytest-cov version 4.1.0 or newer**: Measures test coverage

---

### What We Assume Is True

**A-001: Python Version**

Users have Python 3.11 or newer installed.

**A-002: Display Setup**

Users have a working display:
- Linux: X11 or WSLg
- Mac: Native display
- Windows: Native display

**A-003: Pandoc Installed**

Users who want conversion have Pandoc installed separately. We don't bundle it.

**A-004: Git Configured**

Users who want Git features have Git installed and configured (username, email, credentials).

**A-005: Technical Users**

Target users are comfortable with command-line installation. They can run `pip install`.

**A-006: Standard AsciiDoc**

Documents use standard AsciiDoc syntax. Not heavily using advanced extensions.

**A-007: Enough RAM**

Users have at least 4GB RAM for comfortable performance.

**A-008: Screen Resolution**

Display is at least 1280x720 pixels (720p). Smaller screens might be cramped.

**A-009: Open Source License**

Users accept the MIT open-source license terms.

**A-010: Internet For Git**

Internet connection available for Git push/pull. Not required for editing.

**A-011: AI Costs**

Users who want AI conversion provide their own API key and pay API costs (charged by Anthropic).

---

### Limitations We Accept

**C-001: PDF Needs LaTeX**

Exporting to PDF requires Pandoc with LaTeX backend. We don't bundle LaTeX.

**C-002: Preview Limitations**

Some advanced AsciiDoc features might not preview correctly (depends on asciidoc3 capabilities).

**C-003: Basic Git Only**

Git integration provides commit, push, pull. Not advanced features like rebase or cherry-pick.

**C-004: Conversion Quality Varies**

Conversion quality depends on Pandoc. Some formatting details might be lost.

**C-005: Single File Focus**

Designed for editing one file at a time. Not a project management tool.

**C-006: AI Requires Key And Costs Money**

AI conversion requires valid API key. Anthropic charges based on document size.

**C-007: AI Rate Limits**

Claude API might rate-limit you if you convert too many documents quickly. Needs internet.

**C-008: AI Quality Varies**

AI quality depends on Claude's capabilities. Might vary with very specialized content.

---

## Keeping It Safe

**What are security considerations?**

Ways we protect your computer and data from hackers and accidents.

---

### 1. Safe File Paths (Path Validation)

**The Threat:**

Hackers use tricks like "../../secret_file" to access files they shouldn't see.

**Our Protection:**

Every file path is cleaned:

```python
def sanitize_path(path_str: str) -> Optional[Path]:
    """Clean up file path to block hacker tricks."""
    path = Path(path_str).resolve()  # Make path absolute
    if ".." in path.parts:  # Block suspicious ".." patterns
        return None  # Reject this path
    return path
```

**Where We Use This:**
- Opening files
- Saving files
- Configuration files
- Git repository paths

---

### 2. Safe File Saving (Atomic Writes)

**The Threat:**

Computer crashes while saving can corrupt your file. Half-saved files are broken.

**Our Protection:**

We use the "atomic write" pattern:

```python
def atomic_save(file_path: Path, content: str) -> bool:
    """Save file safely using temp file trick."""
    temp_path = file_path.with_suffix('.tmp')  # Make temp name
    try:
        temp_path.write_text(content, encoding='utf-8')  # Write to temp
        temp_path.replace(file_path)  # Rename (instant operation)
        return True  # Success!
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()  # Clean up temp file
        return False  # Failed
```

**Why This Works:**

Renaming a file is instant and atomic (all-or-nothing). Either it works completely or not at all. Your original file stays safe until the very last instant.

**Where We Use This:**
- All document saves
- Configuration file saves

---

### 3. Stop Command Injection

**The Threat:**

Hackers hide evil commands in file names. Example: `file.txt; rm -rf /` could delete your whole computer.

**Our Protection:**

We use parameterized arguments (safe method):

```python
# CORRECT: Safe parameterized command
subprocess.run(['git', 'commit', '-m', user_message], check=True)

# WRONG: String interpolation (dangerous!)
subprocess.run(f"git commit -m '{user_message}'", shell=True)
```

**Why This Works:**

Parameterized commands keep data separate from commands. The computer knows "this is the command" and "this is just data." Data can't become evil commands.

**Where We Use This:**
- All Git commands
- All Pandoc commands

---

### 4. Protect API Keys

**The Threat:**

If API keys are saved in files, hackers can steal them. Your API key costs you money.

**Our Protection:**

1. **Environment Variables Only**: API keys stored in ANTHROPIC_API_KEY environment variable
2. **Never In Files**: Settings files never contain API keys
3. **Never In Logs**: Error messages never show API keys
4. **Documentation**: We warn users about keeping keys safe

**Example Setup:**

```bash
# Linux/Mac
export ANTHROPIC_API_KEY="your-key-here"

# Windows Command Prompt
set ANTHROPIC_API_KEY=your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-key-here"
```

**Where We Use This:**
- ClaudeClient initialization
- AI conversion jobs
- Never saved to settings

---

### 5. Document Privacy

**The Concern:**

When you use AI conversion, your document is sent to Claude API (Anthropic's servers). Your document goes to the cloud.

**Our Protection:**

1. **AI Is Optional**: You choose whether to use AI. It's off by default.
2. **Clear Documentation**: We tell users documents go to the cloud
3. **Settings Control**: Users can enable/disable AI conversion
4. **Future Feature**: Add warning before first AI use

**What You Should Know:**

Using AI means your document is sent to Anthropic's servers. If your document is confidential, don't use AI conversion. Use regular Pandoc instead (stays on your computer).

---

### 6. Protect Against Rate Limits

**The Concern:**

If you send too many requests to Claude API, they might block your account temporarily.

**Our Protection:**

**Exponential Backoff:**

If rate limited:
1. First retry: Wait 2 seconds
2. Second retry: Wait 4 seconds (2^2)
3. Third retry: Wait 8 seconds (2^3)
4. Give up: Use Pandoc instead

**Why This Works:**

This gives the API time to recover. Most temporary problems are fixed within a few seconds.

**Code Example:**

```python
for attempt in range(1, 4):  # Try 3 times
    try:
        result = convert_with_ai()
        return result  # Success!
    except RateLimitError:
        if attempt < 3:
            wait_time = 2 ** attempt  # 2, 4, 8 seconds
            time.sleep(wait_time)
        else:
            return convert_with_pandoc()  # Give up, use backup
```

---

## How We Test It

**What is testing?**

Testing means checking if the program works correctly. We write automated tests that run quickly.

---

### 1. Unit Tests (Test Small Pieces)

**What We Test:**

Small pieces of code in isolation. Each function by itself.

**Examples:**

**Settings Tests (5 tests, all passing):**
- Does Settings use correct defaults?
- Can Settings save to JSON?
- Can Settings load from JSON?
- Does Settings ignore unknown fields?
- Can Settings do a round-trip (save then load)?

**File Operations Tests (9 tests, all passing):**
- Does atomic save work?
- Does atomic save handle errors?
- Does path sanitization block hacker tricks?
- Does path sanitization allow normal paths?

**Claude Client Tests (not written yet):**
- Does API key validation work?
- Does token estimation work?
- Does conversion create proper prompts?
- Does retry logic work correctly?

**Tools:** pytest

---

### 2. Integration Tests (Test Parts Working Together)

**What We Test:**

Multiple parts working together. Real interactions with external tools.

**Examples We Need:**

**Pandoc Integration:**
- Can we convert DOCX to AsciiDoc?
- Can we export AsciiDoc to PDF?
- Do conversion errors show helpful messages?
- Does format detection work?

**Git Integration:**
- Can we detect a Git repository?
- Can we commit a file?
- Can we push to a remote server?
- Do we handle auth failures gracefully?

**AI Integration:**
- Does AI conversion work? (using fake API responses)
- Does fallback to Pandoc work?
- Does retry logic work?
- Do we handle API errors correctly?

**Tools:** pytest with mocked external services

**What is mocking?**

Mocking means creating fake versions of external services. We don't want tests to use real Claude API (costs money, requires internet). We create a fake API that returns test responses.

---

### 3. GUI Tests (Test The Interface)

**What We Test:**

The buttons, menus, and windows. Make sure clicking things works.

**Examples We Need:**

**Basic Workflow:**
- Can we type in the editor?
- Does preview update?
- Can we click File → Open?
- Can we click File → Save?
- Do keyboard shortcuts work?

**Theme Switching:**
- Does Ctrl+D toggle dark mode?
- Do colors change?
- Is contrast good in both themes?

**Menu Interactions:**
- Do all menu items respond?
- Are Git menus disabled when not in repository?
- Do dialogs appear and close correctly?

**Tools:** pytest-qt (special testing library for Qt programs)

---

### 4. Platform Tests (Test On Different Computers)

**What We Test:**

Make sure it works the same on Linux, Mac, and Windows.

**What We Check:**

**Configuration Paths:**
- Linux: Does it use ~/.config/?
- Mac: Does it use ~/Library/Application Support/?
- Windows: Does it use %APPDATA%/?

**Keyboard Shortcuts:**
- Linux/Windows: Does Ctrl work?
- Mac: Does Cmd work?

**Display:**
- Do windows render correctly?
- Does high-DPI scaling work?
- Are fonts readable?

**File Paths:**
- Do forward slashes work on Linux/Mac?
- Do backslashes work on Windows?
- Does the program handle both correctly?

**How We Test:**

Manual testing on real computers. We run the program on Linux, Mac, and Windows machines. We check everything works identically.

---

### 5. Performance Tests (Test Speed)

**What We Test:**

How fast things run. Do we meet our speed goals?

**Measurements:**

**Preview Latency:**
- Type a character
- Measure time until preview updates
- Goal: Less than 350 milliseconds
- Current: Usually 150-250ms ✅

**Startup Time:**
- Click program icon
- Measure time until window appears and is usable
- Goal: Less than 3 seconds
- Current: Usually 2-3 seconds ✅

**Memory Usage:**
- Open a typical document (3,000 lines)
- Check memory usage
- Goal: Less than 500MB
- Current: Usually 200-300MB ✅

**Large Document Performance:**
- Open a 10,000-line document
- Type and see if it's responsive
- Goal: No lag or freezing
- Current: Responsive up to 10,000 lines ✅

**AI Conversion Speed:**
- Convert a 50-page document with AI
- Measure total time
- Goal: Less than 30 seconds
- Current: Not measured yet (need to test with real API)

**Tools:** pytest-benchmark, memory_profiler, custom timing code

---

### 6. Security Tests (Test Safety)

**What We Test:**

Make sure hackers can't break in. Verify security features work.

**Examples:**

**Path Traversal Prevention:**
- Try to open "../../secret_file"
- Program should block this
- Verify rejection works

**Command Injection Prevention:**
- Try file names with evil commands: "file.txt; rm -rf /"
- Program should treat as normal file name
- Verify command doesn't execute

**API Key Exposure:**
- Check log files don't contain API keys
- Check error messages don't show API keys
- Check settings files don't save API keys

**Atomic Write Verification:**
- Save a file
- Kill the program mid-save (simulate crash)
- Verify original file is intact

**Tools:** Manual security review, automated security scanners, penetration testing

---

## Problems We Need To Fix

**What is technical debt?**

Known problems or shortcuts in the code. Things that work but could be better. We track these to fix later.

---

### Current Issues

**1. Test Coverage (Medium Priority)**

**Problem:** Most of the code doesn't have automated tests yet.

**Impact:** Bugs might sneak in without us knowing.

**Priority:** HIGH

**Fix Plan:**

1. Write unit tests for Claude client (AI conversion)
2. Write integration tests for Pandoc (format conversion)
3. Write integration tests for Git (version control)
4. Write GUI tests for main workflows
5. Write performance benchmarks

**Goal:** 80% of code covered by tests

**Timeline:** Phase 11 (in progress now)

---

**2. Old Qt Code (Low Priority)**

**Problem:** We use old Qt HighDPI settings that are deprecated (outdated).

**Impact:** Future Qt versions might not support them.

**Priority:** LOW

**Fix Plan:**

Replace this old code:

```python
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # Old way
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)     # Old way
```

With new Qt 6 code (when we upgrade Qt).

**Timeline:** Phase 13 or when we upgrade Qt

---

**3. Large Single File (Medium Priority)**

**Problem:** adp_windows.py is 2,378 lines long. Big files are hard to navigate.

**Impact:** Developers spend more time finding code.

**Priority:** MEDIUM

**Fix Plan:**

If file grows past 3,000 lines, split into modules:
- ui.py (user interface code)
- workers.py (background workers)
- file_operations.py (file I/O)
- git_integration.py (Git commands)

**Timeline:** Phase 13 or when file exceeds 3,000 lines

---

**4. Hard-Coded Strings (Low Priority)**

**Problem:** Error messages and labels are in English only. Not translated to other languages.

**Impact:** Non-English speakers have harder time.

**Priority:** LOW

**Fix Plan:**

Add internationalization (i18n) support if we get international users:
1. Use Qt translation system
2. Extract all strings to translation files
3. Recruit translators for popular languages
4. Add language selection in settings

**Timeline:** Future (only if user base becomes international)

---

**5. No AI UI Controls Yet (High Priority)**

**Problem:** AI conversion works in code, but there's no UI checkbox to enable it.

**Impact:** Users can't easily choose AI conversion.

**Priority:** HIGH

**Fix Plan:**

Phase 12 (next phase):
1. Add "Use AI Conversion" checkbox in Tools → Export dialog
2. Add "Use AI Conversion" checkbox in File → Open for DOCX files
3. Add tooltip explaining AI feature and API costs
4. Show AI progress in status bar
5. Add help menu item for API key setup instructions

**Timeline:** Phase 12 (coming soon)

---

## What We Won't Do

**What is out of scope?**

Features we explicitly decided NOT to include. This keeps the program simple and focused.

---

### Features We're NOT Building

**❌ Multi-File Project Management**

No project browser. No folder tree. Edit one file at a time.

**Why not:** Adds complexity. Other tools (VS Code, file manager) do this better.

---

**❌ Real-Time Collaboration**

No multiple users editing the same document at once.

**Why not:** Very complex feature. Use Google Docs if you need this.

---

**❌ Cloud Integration**

No built-in Dropbox, Google Drive, or OneDrive sync.

**Why not:** Operating systems already provide this. Use your OS's sync tools.

---

**❌ Spell Checking**

No built-in spell checker or grammar checker.

**Why not:** Text editors and operating systems provide spell check. Use those tools.

---

**❌ Custom AsciiDoc Extensions**

Only standard AsciiDoc syntax. No custom plugins.

**Why not:** Keeps program simple. If you need extensions, use Asciidoctor (Ruby version).

---

**❌ Advanced Git Features**

No branching UI. No merge conflict resolution. No rebasing UI. No cherry-picking.

**Why not:** These are complex Git operations. Use Git command line or a proper Git GUI tool.

---

**❌ PDF Editing**

Can export TO PDF, but can't edit PDFs or annotate them.

**Why not:** PDFs are read-only output format. Use a PDF editor if you need to edit PDFs.

---

**❌ Custom Themes**

Only light mode and dark mode. No custom color schemes.

**Why not:** Two themes are enough for most users. Custom themes add complexity.

---

**❌ Mobile Or Web Versions**

Desktop only. No mobile app. No web app.

**Why not:** Desktop focus. Mobile editing is uncomfortable for long documents.

---

**❌ Telemetry or Analytics**

No usage tracking. No data collection. No crash reports.

**Why not:** Privacy focused. Your work stays on your computer.

---

**❌ Scroll Synchronization Between Panes**

Editor and preview don't maintain exact scroll sync.

**Why not:** Hard to implement perfectly. Approximation is good enough.

---

**❌ Pane Maximization**

Can't maximize editor to full screen and hide preview (or vice versa).

**Why not:** Just resize the splitter. Dragging the divider is enough.

---

## Word Guide (Glossary)

**What is this?**

Definitions of technical words used in this document. In alphabetical order.

---

**API (Application Programming Interface)**

A way for programs to talk to each other. Like a telephone for software.

Example: Claude API lets our program talk to Claude AI.

---

**API Key**

A password that lets you use an API. Like a ticket to get in.

Example: Your Anthropic API key lets you use Claude AI.

---

**Asciidoc**

A simple way to write formatted documents using plain text. Like Markdown but more powerful.

Example: `== My Heading` makes a heading level 2.

---

**Atomic Operation**

An operation that either works completely or doesn't happen at all. No half-done results.

Example: Renaming a file is atomic. It's either renamed or not - never half-renamed.

---

**Background Worker (Worker Thread)**

A separate process that does work without freezing the screen. Like a helper working in the background.

Example: PreviewWorker makes HTML while you keep typing.

---

**Branch (Git)**

A separate version of your files in Git. Like a parallel universe for your code.

Example: "main" branch for finished code, "dev" branch for experiments.

---

**Command Injection**

A hacking trick where evil commands are hidden in normal inputs.

Example: File name `file.txt; rm -rf /` could delete your computer.

---

**Commit (Git)**

Saving a snapshot of your files in Git history. Like taking a photo of your work.

Example: "git commit -m 'Fixed bug'" saves current state with a message.

---

**Cross-Platform**

Works on different operating systems (Linux, Mac, Windows).

Example: Our program looks and works the same everywhere.

---

**Debouncing**

Waiting a moment before doing something. Prevents wasting work.

Example: Wait 350ms after typing before updating preview. If you keep typing, timer resets.

---

**Encoding**

How text is stored in computer files. Different encodings support different languages.

Example: UTF-8 encoding supports all languages. ASCII only supports English.

---

**Environment Variable**

A place to store settings outside of files. Like a special secure locker.

Example: ANTHROPIC_API_KEY stores your API key safely.

---

**Exponential Backoff**

Waiting longer each time you retry. 2 seconds, then 4, then 8, etc.

Example: If AI is busy, wait longer before trying again.

---

**Fallback**

A backup plan that runs if the first plan fails.

Example: If AI conversion fails, use Pandoc instead (automatic fallback).

---

**Git**

A version control system. Tracks changes to files over time. Like a time machine for your work.

Example: Save multiple versions and go back to any previous version.

---

**GUI (Graphical User Interface)**

Windows, buttons, and menus you can click. The opposite of command-line.

Example: Our program is a GUI application.

---

**HTML (HyperText Markup Language)**

The code that makes web pages. Browsers display HTML.

Example: `<h1>Title</h1>` makes a big heading on a web page.

---

**JSON (JavaScript Object Notation)**

A format for storing structured data in text files. Easy for computers to read.

Example: `{"name": "John", "age": 30}` stores two pieces of information.

---

**Line Ending**

Special characters at the end of each line. Different on Windows vs. Unix.

Example: Windows uses \r\n, Unix/Linux/Mac use \n.

---

**Markdown**

A simple way to format text using plain text symbols.

Example: `# Heading` and `**bold**` are Markdown.

---

**Mock (Testing)**

A fake version of something used for testing. Like a practice dummy.

Example: Mock Claude API returns fake responses without using real API.

---

**Monospace Font**

A font where all letters are the same width. Used for code and plain text.

Example: "Courier New" and "Consolas" are monospace fonts.

---

**MVC (Model-View-Controller)**

A pattern for organizing programs into three parts: data, display, and brain.

Example: Model = your document, View = the editor window, Controller = event handlers.

---

**Pandoc**

A universal document converter. Can change between many formats.

Example: Pandoc converts DOCX to AsciiDoc to HTML to PDF, etc.

---

**Parameterized Arguments**

A safe way to send inputs to programs. Keeps data separate from commands.

Example: `['git', 'commit', '-m', message]` is safe. `f"git commit -m {message}"` is dangerous.

---

**Path Traversal**

A hacking trick using "../" to access files outside allowed folders.

Example: "../../../etc/passwd" tries to access system passwords.

---

**Pull (Git)**

Download new changes from the server to your computer.

Example: Your teammate made changes. You pull them to get the updates.

---

**Push (Git)**

Upload your changes from your computer to the server.

Example: You made changes. Push them so teammates can get them.

---

**Rate Limiting**

When a service makes you slow down to prevent overuse.

Example: Claude API says "You're using me too much. Wait a minute."

---

**Rendering**

Converting one format to another to display it.

Example: Rendering AsciiDoc to HTML is like cooking raw ingredients into a meal.

---

**Repository (Repo)**

A folder where Git stores all versions of your files.

Example: Your "MyProject" folder with a hidden ".git" subfolder is a repository.

---

**Sanitization**

Cleaning inputs to remove dangerous parts.

Example: Sanitizing file paths removes ".." patterns that hackers use.

---

**Semantic Structure**

The meaning and organization of a document (not just how it looks).

Example: Headings, lists, tables, code blocks. The structure that carries meaning.

---

**SSH Key**

A special key used for secure login without passwords.

Example: Used to push to GitHub without typing password every time.

---

**Synchronization (Sync)**

Making two things match or move together.

Example: When you scroll the editor, the preview scrolls to match (synchronized scrolling).

---

**Token**

A piece of text that AI processes. Roughly one word or part of a word.

Example: "Hello world" is about 2 tokens. API charges per token.

---

**Type Hints**

Notes in code that say what type of data each thing is.

Example: `def add(a: int, b: int) -> int:` says "a and b are integers, returns integer."

---

**UTF-8**

A text encoding that supports all languages and symbols.

Example: UTF-8 can store English, Chinese, Arabic, emoji, etc.

---

**Version Control**

A system that tracks changes to files over time. Like a time machine.

Example: Git is a version control system. Save versions and go back if needed.

---

**WCAG AA**

Web Content Accessibility Guidelines Level AA. Ensures content is readable for people with vision problems.

Example: Our dark theme has high contrast to meet WCAG AA standards.

---

**Worker Thread**

A separate process that does work in the background without freezing the main program.

Example: PreviewWorker makes HTML in the background while you keep typing.

---

## Document Information

**Version**: 1.1.0
**Date**: 2025-10-23
**Status**: Active Development
**Reading Level**: Grade 5-6
**Original Version**: SPECIFICATION.md
**Approved By**: Project Maintainer

**What Changed from Original:**
- Simplified all vocabulary
- Shortened all sentences
- Explained all technical terms
- Added more examples
- Used active voice instead of passive
- Added "What is...?" explanations
- Created complete glossary
- Maintained 100% technical accuracy

**Next Steps:**
1. Complete test suite (Phase 11)
2. Add AI UI controls (Phase 12)
3. Fix technical debt (Phase 13)
4. Continue improving based on user feedback

---

*This simplified specification contains the same information as the original SPECIFICATION.md but written at 5th grade reading level. All 62 functional requirements, 20 non-functional requirements, 7 user stories, and 22 success criteria are included.*
