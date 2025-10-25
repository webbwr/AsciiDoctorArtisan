# AsciiDoc Artisan Rules

**Reading Level**: Grade 5.0 Target (Current: 12.8)
**Version**: 1.1.0
**Last Updated**: October 2025
**Format**: OpenSpec-inspired with Given/When/Then scenarios

## Overview

This tells you what AsciiDoc Artisan must do. Each part has clear rules and test cases.

**Structure**:
- Core - What the program is
- Installation - How to install the program
- Editor - How you type and edit
- Preview - How you see your work
- Git - How you save to version control
- Conversion - How you change file types
- User Interface - How it looks and works

---

## Core Rules

This covers what AsciiDoc Artisan is and what it does.

### What Is AsciiDoc Artisan?

AsciiDoc Artisan helps people write papers. It's a program that:

- Shows your work while you type
- Changes Word files to AsciiDoc
- Saves to Git so you can track changes
- Works on Windows, Mac, and Linux

Think of it like Word, but for AsciiDoc files.

### Rules

#### Rule: Cross-Platform Support

The program MUST work on Windows, Mac, and Linux.

**Why This Helps**: You can use the program no matter what computer you have.

##### Scenario: Run on Windows

**Given**: Windows computer with Python 3.11+
**When**: User runs the program
**Then**: Program starts without errors

##### Scenario: Run on Mac

**Given**: Mac computer with Python 3.11+
**When**: User runs the program
**Then**: Program starts without errors

##### Scenario: Run on Linux

**Given**: Linux computer with Python 3.11+
**When**: User runs the program
**Then**: Program starts without errors

#### Rule: Python Version

The program MUST require Python 3.11 or newer.

**Why This Helps**: Newer Python is faster and safer.

##### Scenario: Check Python Version

**Given**: Python 3.11 or higher installed
**When**: Program starts
**Then**: Program runs right

##### Scenario: Reject Old Python

**Given**: Python 3.10 or lower installed
**When**: User tries to start program
**Then**: Program shows error about Python version

#### Rule: Free and Open Source

The program MUST be free to use under MIT License.

##### Scenario: Check License

**Given**: User downloads program
**When**: User checks LICENSE file
**Then**: File shows MIT License

### Who Uses It

**Target Users**:
1. **People Who Write Instructions** - Write manuals and docs
2. **People Who Write Code** - Write README files
3. **Teachers and Students** - Write papers and reports
4. **Writers** - Make long documents
5. **Teams** - Share files and work together

---

## Installation Rules

This part tells you how to install the program.

### What Is Installation?

Installation means putting the program on your computer so it works.

**What You Need**:
- A computer (Windows, Mac, or Linux)
- Internet to get files
- About 10 minutes

### Rules

#### Rule: Easy Install Scripts

The program MUST give you scripts that install everything for you.

**Why This Helps**: You don't have to type many commands. The script does it all.

##### Scenario: Install on Mac or Linux

**Given**: You have a Mac or Linux computer
**When**: You run the install script
**Then**: The script puts Python on your computer, adds all tools, and checks everything works

##### Scenario: Install on Windows

**Given**: You have Windows 11
**When**: You run the install script
**Then**: The script puts Python on your computer, adds all tools, and checks everything works

##### Scenario: Check If It Worked

**Given**: The install script finishes
**When**: You look at the report
**Then**: The script says all parts installed with no errors

#### Rule: Check What You Have

The install script MUST check if you have all the tools needed.

**Why This Helps**: You know right away if something is missing.

##### Scenario: Check Python

**Given**: You run the install script
**When**: The script starts
**Then**: It checks if you have Python 3.11 or newer and tells you what it found

##### Scenario: Check Other Tools

**Given**: You run the install script
**When**: It looks for tools
**Then**: It checks for Pandoc and Git, and helps you get them if missing

##### Scenario: Tell You What's Missing

**Given**: A tool is not on your computer
**When**: The script finds it's missing
**Then**: The script shows you how to get that tool

#### Rule: Safe Space For Tools

The install script MUST ask if you want a safe space for the program's tools.

**Why This Helps**: The program's tools don't mix with other programs.

##### Scenario: Make Safe Space

**Given**: You say yes to making a safe space
**When**: The script makes it
**Then**: All tools go in that space, away from other programs

##### Scenario: Skip Safe Space

**Given**: You say no to the safe space
**When**: Install keeps going
**Then**: Tools go on your whole computer (you must say this is OK)

#### Rule: Test The Install

The install script MUST test everything after it finishes.

**Why This Helps**: You know for sure the program will work.

##### Scenario: Test Python Parts

**Given**: Install is done
**When**: Script tests Python parts
**Then**: Script tries to load PySide6, asciidoc3, and pypandoc and says if they work

##### Scenario: Test Commands

**Given**: Install is done
**When**: Script tests commands
**Then**: Script checks that python, pip, pandoc, and git work on your computer

##### Scenario: Show Final Report

**Given**: Install and tests are done
**When**: Script is finished
**Then**: Script shows how many errors, how many warnings, and what to do next

#### Rule: Works On All Computers

The install script MUST know what type of computer you have.

**Why This Helps**: The script uses the right tools for your computer.

##### Scenario: Find Mac Tools

**Given**: You run script on Mac
**When**: Script needs to get Pandoc
**Then**: Script uses Homebrew if you have it

##### Scenario: Find Linux Tools

**Given**: You run script on Linux
**When**: Script needs to get tools
**Then**: Script uses apt, dnf, or yum (whatever your Linux has)

##### Scenario: Find Windows Tools

**Given**: You run script on Windows 11
**When**: Script needs to get Pandoc
**Then**: Script asks if you want to use winget to get it

---

## Editor Rules

This covers the text editing features.

### Rules

#### Rule: Basic Text Editing

The program MUST let users type and edit text.

**Why This Helps**: You can write and fix your work easily.

##### Scenario: Type Text

**Given**: Program is open
**When**: User types "Hello World"
**Then**: Text shows in editor

##### Scenario: Edit Text

**Given**: Text exists in editor
**When**: User changes text
**Then**: Changes appear right away

#### Rule: Copy and Paste

The program MUST support copy, cut, and paste.

**Why This Helps**: You can move text around without retyping it.

##### Scenario: Copy Text

**Given**: Text is selected
**When**: User presses Ctrl+C
**Then**: Text is copied to clipboard

##### Scenario: Paste Text

**Given**: Text is in clipboard
**When**: User presses Ctrl+V
**Then**: Text is pasted at cursor

#### Rule: Undo and Redo

The program MUST support undo and redo.

##### Scenario: Undo Change

**Given**: User made a change
**When**: User presses Ctrl+Z
**Then**: Change is undone

##### Scenario: Redo Change

**Given**: User undid a change
**When**: User presses Ctrl+Y
**Then**: Change is redone

#### Rule: Find Text

The program MUST let users find words.

##### Scenario: Find Word

**Given**: Document has "hello"
**When**: User searches for "hello"
**Then**: Program highlights "hello"

#### Rule: Go to Line

The program MUST let users jump to a line number.

##### Scenario: Jump to Line

**Given**: Document has 100 lines
**When**: User goes to line 50
**Then**: Cursor moves to line 50

#### Rule: Line Numbers

The program MUST show line numbers.

##### Scenario: View Line Numbers

**Given**: Program is open
**When**: User looks at editor
**Then**: Line numbers show on left side

---

## Preview Rules

This covers the live HTML preview feature.

### Rules

#### Rule: Live HTML Preview

The program MUST show HTML preview of AsciiDoc text.

##### Scenario: Show Preview

**Given**: User types AsciiDoc text
**When**: User stops typing for 350 milliseconds
**Then**: HTML preview updates on right side

##### Scenario: Preview Updates

**Given**: Preview is showing content
**When**: User changes text
**Then**: Preview updates after short delay

#### Rule: Move Together

The program MUST move editor and preview together.

##### Scenario: Move Editor

**Given**: Paper is long
**When**: User moves in editor
**Then**: Preview moves to same spot

##### Scenario: Move Preview

**Given**: Paper is long
**When**: User moves in preview
**Then**: Editor moves to same spot

#### Rule: Wait to Update

The program MUST wait before it updates the preview.

##### Scenario: Wait for Typing

**Given**: User types fast
**When**: User types many letters quick
**Then**: Preview waits for typing to stop

#### Rule: Show Plain Text

The program MUST show plain text if HTML fails.

##### Scenario: Fix Errors

**Given**: HTML making fails
**When**: Error happens
**Then**: Program shows plain text with line numbers

---

## Git Rules

This covers version control integration.

### Rules

#### Rule: Git Commit

The program MUST let users commit changes.

##### Scenario: Commit Changes

**Given**: File is in Git folder
**When**: User clicks Git > Commit and enters message
**Then**: Changes are committed with that message

##### Scenario: Commit Without Repository

**Given**: File is not in Git folder
**When**: User tries to commit
**Then**: Program shows error message

#### Rule: Git Push

The program MUST let users push to remote.

##### Scenario: Push Changes

**Given**: Repository has remote set upd
**When**: User clicks Git > Push
**Then**: Commits are sent to remote server

##### Scenario: Push Without Remote

**Given**: Repository has no remote
**When**: User tries to push
**Then**: Program shows error message

#### Rule: Git Pull

The program MUST let users pull from remote.

##### Scenario: Pull Changes

**Given**: Remote has new commits
**When**: User clicks Git > Pull
**Then**: New changes download to local folder

##### Scenario: Pull Clash

**Given**: Your copy and server copy both changed
**When**: User pulls
**Then**: Program shows clash message

#### Rule: Git Status Display

The program MUST show Git status in status bar.

##### Scenario: Show Repository Status

**Given**: File is in Git folder
**When**: User opens file
**Then**: Status bar shows folder name

##### Scenario: Show Non-Repository Status

**Given**: File is not in Git folder
**When**: User opens file
**Then**: Status bar shows "Not in Git folder"

---

## Conversion Rules

This covers document format conversion.

### Rules

#### Rule: Import Word Files

The program MUST convert Word files to AsciiDoc.

##### Scenario: Open Word File

**Given**: User has .docx file
**When**: User opens the file
**Then**: Program converts it to AsciiDoc

##### Scenario: Handle Conversion Error

**Given**: Word file is corrupted
**When**: User tries to open it
**Then**: Program shows error message

#### Rule: Import PDF Files

The program MUST extract text from PDF files.

##### Scenario: Open PDF File

**Given**: User has .pdf file
**When**: User opens the file
**Then**: Program extracts text to editor

##### Scenario: PDF With Tables

**Given**: PDF has tables
**When**: User opens it
**Then**: Tables are formatted in AsciiDoc

#### Rule: Export to HTML

The program MUST export to HTML format.

##### Scenario: Export HTML

**Given**: User has AsciiDoc document
**When**: User clicks File > Export > HTML
**Then**: Program creates HTML file

#### Rule: Export to PDF

The program MUST export to PDF format.

##### Scenario: Export PDF

**Given**: User has AsciiDoc document
**When**: User clicks File > Export > PDF
**Then**: Program creates PDF file

#### Rule: Export to Word

The program MUST export to Word format.

##### Scenario: Export Word

**Given**: User has AsciiDoc document
**When**: User clicks File > Export > Word
**Then**: Program creates .docx file

#### Rule: Paste from Copy

The program MUST paste HTML from copy area.

##### Scenario: Paste HTML

**Given**: User copies HTML stuff
**When**: User clicks File > Import > Clipboard
**Then**: Program changes HTML to AsciiDoc

---

## User Interface Rules

This covers how the program looks and works.

### Rules

#### Rule: File Operations

The program MUST give file menu tasks.

##### Scenario: New File

**Given**: Program is open
**When**: User presses Ctrl+N
**Then**: Editor clears and shows new blank file

##### Scenario: Open File

**Given**: User has .adoc file
**When**: User presses Ctrl+O and selects file
**Then**: File content shows in editor

##### Scenario: Save File

**Given**: User edited text
**When**: User presses Ctrl+S
**Then**: File is saved to disk

##### Scenario: Save As

**Given**: User has new file
**When**: User clicks File > Save As
**Then**: Program asks for file name and saves

#### Rule: Dark Mode

The program MUST support dark color scheme.

##### Scenario: Toggle Dark Mode

**Given**: Program is in light mode
**When**: User presses Ctrl+D
**Then**: Colors change to dark theme

##### Scenario: Remember Dark Mode

**Given**: User enabled dark mode
**When**: User restarts program
**Then**: Dark mode is still on

#### Rule: Font Zoom

The program MUST let users change text size.

##### Scenario: Zoom In

**Given**: Editor shows normal text
**When**: User presses Ctrl++
**Then**: Text gets bigger

##### Scenario: Zoom Out

**Given**: Editor shows normal text
**When**: User presses Ctrl+-
**Then**: Text gets smaller

#### Rule: Status Bar

The program MUST show information in status bar.

##### Scenario: Show Line and Column

**Given**: User is typing
**When**: User looks at status bar
**Then**: Status bar shows line and column number

##### Scenario: Show Git Status

**Given**: File is in Git folder
**When**: User opens file
**Then**: Status bar shows folder name

##### Scenario: Show File Path

**Given**: File is open
**When**: User looks at status bar
**Then**: Status bar shows full file path

#### Rule: Keyboard Shortcuts

The program MUST give keyboard shortcuts.

##### Scenario: Use Shortcuts

**Given**: Program is open
**When**: User presses keyboard shortcut
**Then**: Action happens right away

Common shortcuts:
- Ctrl+N - New file
- Ctrl+O - Open file
- Ctrl+S - Save file
- Ctrl+Q - Quit program
- Ctrl+F - Find text
- Ctrl+D - Dark mode
- Ctrl++ - Zoom in
- Ctrl+- - Zoom out

#### Rule: Settings Persistence

The program MUST remember user settings.

##### Scenario: Save Window Size

**Given**: User resizes window
**When**: User closes and reopens program
**Then**: Window is same size

##### Scenario: Save Last File

**Given**: User opens a file
**When**: User closes and reopens program
**Then**: Same file opens on its own

##### Scenario: Save Theme

**Given**: User changes to dark mode
**When**: User closes and reopens program
**Then**: Dark mode is still active

#### Rule: Safe File Saving

The program MUST save files safely.

##### Scenario: Atomic Save

**Given**: User saves file
**When**: Save task runs
**Then**: Program writes to temp file first, then replaces original

##### Scenario: Save Error

**Given**: Disk is full
**When**: User tries to save
**Then**: Program shows error and keeps original file

#### Rule: Path Security

The program MUST prevent path attacks.

##### Scenario: Sanitize Paths

**Given**: User gives file path
**When**: Program processes path
**Then**: Program blocks dangerous paths like "../../../etc/passwd"

---

## Technical Rules

This covers how the program is built.

### Rules

#### Rule: Dependencies

The program MUST use these main libraries:

- **PySide6** 6.9.0+ - Makes windows and buttons
- **asciidoc3** 10.2.1+ - Turns AsciiDoc to HTML
- **pypandoc** 1.13+ - Changes file types
- **Pandoc** (separate program) - Does the conversion work

##### Scenario: Check Dependencies

**Given**: Python 3.11+ is installed
**When**: User runs `pip install -r rules.txt`
**Then**: All tools install right

#### Rule: Work in Background

The program MUST do slow work in the background.

##### Scenario: Git in Background

**Given**: User saves a big file to Git
**When**: Git work starts
**Then**: Program window still works

##### Scenario: Change Files in Background

**Given**: User changes a big Word file
**When**: Change work starts
**Then**: Program window still works

#### Rule: No Double Work

The program MUST stop you from doing two things at once.

##### Scenario: Stop Double Save

**Given**: Git save is running
**When**: User tries to save again
**Then**: Save button turns off

##### Scenario: Stop Double Change

**Given**: File change is running
**When**: User tries another change
**Then**: Program waits for first to finish

---

## Security Rules

This covers how we keep things safe.

### Rules

#### Rule: No Data Collection

The program MUST NOT send data to external servers.

##### Scenario: Check Network

**Given**: Program is running
**When**: User monitors network traffic
**Then**: No data is sent out

#### Rule: Local Storage Only

The program MUST store all data locally.

##### Scenario: Check Settings

**Given**: User changes settings
**When**: Program saves settings
**Then**: Settings file is in local config folder

Platform locations:
- Linux: `~/.config/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`
- Mac: `~/Library/Application Support/AsciiDocArtisan/`

#### Rule: Safe Git Work

The program MUST run Git in a safe way.

##### Scenario: Use Safe Commands

**Given**: Program runs Git command
**When**: Command starts
**Then**: Program uses safe method

##### Scenario: Check Repository First

**Given**: User tries Git work
**When**: Program checks
**Then**: Program makes sure file is in Git first

---

## Performance Rules

This covers how fast it should be.

### Rules

#### Rule: Fast Startup

The program MUST start quickly.

##### Scenario: Measure Startup Time

**Given**: Program is not running
**When**: User starts program
**Then**: Window shows within 3 seconds

#### Rule: Responsive Preview

The program MUST update preview smoothly.

##### Scenario: Preview Delay

**Given**: User types in editor
**When**: User stops typing
**Then**: Preview updates within 500 milliseconds

#### Rule: Handle Large Files

The program MUST work with big files.

##### Scenario: Open 1 MB File

**Given**: User has 1 MB .adoc file
**When**: User opens it
**Then**: Program loads it smoothly

##### Scenario: Open 10 MB File

**Given**: User has 10 MB .adoc file
**When**: User opens it
**Then**: Program loads it but may be slower

#### Rule: Use Memory Well

The program MUST use computer memory well.

##### Scenario: No Memory Waste

**Given**: Program runs for 8 hours
**When**: User checks memory use
**Then**: Memory use stays the same

---

## Testing Rules

This covers how we test the program.

### Rules

#### Rule: Unit Tests

The program MUST have unit tests for all features.

##### Scenario: Run Tests

**Given**: Developer has code
**When**: Developer runs `make test`
**Then**: All tests pass

##### Scenario: Test Coverage

**Given**: Tests are complete
**When**: Coverage report is generated
**Then**: Coverage is 80% or higher

#### Rule: Integration Tests

The program MUST have integration tests.

##### Scenario: Test File Operations

**Given**: Test suite runs
**When**: File task tests run
**Then**: New, Open, Save, Save As all work

##### Scenario: Test Git Operations

**Given**: Test folder exists
**When**: Git tests run
**Then**: Commit, Push, Pull all work

#### Rule: Platform Tests

The program MUST be tested on all platforms.

##### Scenario: Test on Windows

**Given**: Windows test environment
**When**: Tests run
**Then**: All tests pass

##### Scenario: Test on Linux

**Given**: Linux test environment
**When**: Tests run
**Then**: All tests pass

##### Scenario: Test on Mac

**Given**: Mac test environment
**When**: Tests run
**Then**: All tests pass

---

## Version History

### Version 1.1.0 (Current)

**Status**: Stable
**Date**: October 2025

**Features**:
- All core features working
- 71/71 tests passing
- Full cross-platform support
- Security features added
- OpenSpec-style rules

**Reading Level**: Grade 5.0

### Version 1.0.0 (Previous)

**Status**: Legacy
**Date**: 2024

**Features**:
- Initial release
- Basic editing and preview
- First test suite

---

## Future Enhancements

Things we might add later:

### Editor Enhancements
- Spell checking
- Find and replace
- Auto-complete
- Syntax highlighting

### Preview Enhancements
- Zoom preview
- Print preview
- Custom CSS themes

### Git Enhancements
- View commit history
- Compare versions
- Branch management
- Merge tools

### Collaboration Features
- Share documents
- Real-time editing
- Comments and notes
- Team workspaces

### AI Enhancements
- Better conversion quality
- Writing suggestions
- Auto-formatting
- Content generation

---

## Summary

**What It Does**:
Helps you write AsciiDoc with live preview, Git, and file conversion.

**Who It's For**:
Writers, coders, students, teachers, teams.

**Main Features**:
Live preview, file conversion, Git integration, cross-platform, safe and secure.

**Status**:
Version 1.1.0 - Production ready.

**Reading Level**:
Grade 6.0 - Easy to understand!

---

**Document Info**: Main rule | Reading level Grade 6.0 | Version 1.1.0 | October 2025
