# AsciiDoc Artisan Specifications

**Reading Level**: Grade 6.0 (Elementary/Middle School)
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

## Core Specifications

This covers what AsciiDoc Artisan is and what it does.

### What Is AsciiDoc Artisan?

AsciiDoc Artisan helps people write papers. It's a program that:

- Shows your work while you type
- Changes Word files to AsciiDoc
- Saves to Git so you can track changes
- Works on Windows, Mac, and Linux

Think of it like Word, but for AsciiDoc files.

### Requirements

#### Requirement: Cross-Platform Support

The program SHALL work on Windows, Mac, and Linux.

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

#### Requirement: Python Version

The program SHALL require Python 3.11 or newer.

##### Scenario: Check Python Version

**Given**: Python 3.11 or higher installed
**When**: Program starts
**Then**: Program runs successfully

##### Scenario: Reject Old Python

**Given**: Python 3.10 or lower installed
**When**: User tries to start program
**Then**: Program shows error about Python version

#### Requirement: Free and Open Source

The program SHALL be free to use under MIT License.

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

## Installation Specifications

This covers how users install and set up the program.

### Requirements

#### Requirement: Automated Installation Scripts

The program SHALL provide automated installation scripts for all supported platforms.

##### Scenario: Mac/Linux Installation

**Given**: User has Mac or Linux computer
**When**: User runs install-asciidoc-artisan.sh
**Then**: Script checks Python version, installs dependencies, creates virtual environment, and validates installation

##### Scenario: Windows Installation

**Given**: User has Windows 11 with PowerShell 7
**When**: User runs Install-AsciiDocArtisan.ps1
**Then**: Script checks Python version, installs dependencies, creates virtual environment, and validates installation

##### Scenario: Installation Validation

**Given**: User completes automated installation
**When**: Installation finishes
**Then**: Script reports all dependencies installed correctly with zero errors

#### Requirement: Dependency Checking

Installation scripts SHALL verify all required dependencies before proceeding.

##### Scenario: Check Python Version

**Given**: User runs installation script
**When**: Script starts
**Then**: Script checks for Python 3.11 or higher and reports version found

##### Scenario: Check System Dependencies

**Given**: User runs installation script
**When**: Script checks dependencies
**Then**: Script verifies Pandoc and Git are available or offers to install them

##### Scenario: Report Missing Dependencies

**Given**: Required dependency is missing
**When**: Script detects missing dependency
**Then**: Script shows clear installation instructions for that dependency

#### Requirement: Virtual Environment Support

Installation scripts SHALL offer to create a Python virtual environment.

##### Scenario: Create Virtual Environment

**Given**: User chooses to create virtual environment
**When**: Script creates venv
**Then**: All dependencies install in isolated environment

##### Scenario: Skip Virtual Environment

**Given**: User chooses to skip virtual environment
**When**: Installation continues
**Then**: Dependencies install globally with user permission

#### Requirement: Installation Validation

Installation scripts SHALL validate the complete installation after setup.

##### Scenario: Validate Python Packages

**Given**: Installation completes
**When**: Script runs validation
**Then**: Script confirms PySide6, asciidoc3, and pypandoc can be imported

##### Scenario: Validate System Commands

**Given**: Installation completes
**When**: Script runs validation
**Then**: Script confirms python, pip, pandoc, and git commands are available

##### Scenario: Report Installation Status

**Given**: Installation and validation complete
**When**: Script finishes
**Then**: Script shows summary with error count, warning count, and next steps

#### Requirement: Cross-Platform Installation

Installation scripts SHALL support platform-specific package managers.

##### Scenario: Detect macOS Package Manager

**Given**: User runs script on macOS
**When**: Script needs to install Pandoc
**Then**: Script uses Homebrew (brew) if available

##### Scenario: Detect Linux Package Manager

**Given**: User runs script on Linux
**When**: Script needs to install system packages
**Then**: Script detects and uses apt, dnf, or yum appropriately

##### Scenario: Windows Package Manager

**Given**: User runs script on Windows 11
**When**: Script needs to install Pandoc
**Then**: Script offers to use winget for automated installation

---

## Editor Specifications

This covers the text editing features.

### Requirements

#### Requirement: Basic Text Editing

The program SHALL let users type and edit text.

##### Scenario: Type Text

**Given**: Program is open
**When**: User types "Hello World"
**Then**: Text appears in editor

##### Scenario: Edit Text

**Given**: Text exists in editor
**When**: User changes text
**Then**: Changes appear immediately

#### Requirement: Copy and Paste

The program SHALL support copy, cut, and paste.

##### Scenario: Copy Text

**Given**: Text is selected
**When**: User presses Ctrl+C
**Then**: Text is copied to clipboard

##### Scenario: Paste Text

**Given**: Text is in clipboard
**When**: User presses Ctrl+V
**Then**: Text is pasted at cursor

#### Requirement: Undo and Redo

The program SHALL support undo and redo.

##### Scenario: Undo Change

**Given**: User made a change
**When**: User presses Ctrl+Z
**Then**: Change is undone

##### Scenario: Redo Change

**Given**: User undid a change
**When**: User presses Ctrl+Y
**Then**: Change is redone

#### Requirement: Find Text

The program SHALL let users find words.

##### Scenario: Find Word

**Given**: Document contains "hello"
**When**: User searches for "hello"
**Then**: Program highlights "hello"

#### Requirement: Go to Line

The program SHALL let users jump to a line number.

##### Scenario: Jump to Line

**Given**: Document has 100 lines
**When**: User goes to line 50
**Then**: Cursor moves to line 50

#### Requirement: Line Numbers

The program SHALL show line numbers.

##### Scenario: View Line Numbers

**Given**: Program is open
**When**: User looks at editor
**Then**: Line numbers show on left side

---

## Preview Specifications

This covers the live HTML preview feature.

### Requirements

#### Requirement: Live HTML Preview

The program SHALL show HTML preview of AsciiDoc text.

##### Scenario: Show Preview

**Given**: User types AsciiDoc text
**When**: User stops typing for 350 milliseconds
**Then**: HTML preview updates on right side

##### Scenario: Preview Updates

**Given**: Preview is showing content
**When**: User changes text
**Then**: Preview updates after short delay

#### Requirement: Move Together

The program SHALL move editor and preview together.

##### Scenario: Move Editor

**Given**: Paper is long
**When**: User moves in editor
**Then**: Preview moves to same spot

##### Scenario: Move Preview

**Given**: Paper is long
**When**: User moves in preview
**Then**: Editor moves to same spot

#### Requirement: Wait to Update

The program SHALL wait before it updates the preview.

##### Scenario: Wait for Typing

**Given**: User types fast
**When**: User types many letters quick
**Then**: Preview waits for typing to stop

#### Requirement: Show Plain Text

The program SHALL show plain text if HTML fails.

##### Scenario: Fix Errors

**Given**: HTML making fails
**When**: Error happens
**Then**: Program shows plain text with line numbers

---

## Git Specifications

This covers version control integration.

### Requirements

#### Requirement: Git Commit

The program SHALL let users commit changes.

##### Scenario: Commit Changes

**Given**: File is in Git repository
**When**: User clicks Git > Commit and enters message
**Then**: Changes are committed with that message

##### Scenario: Commit Without Repository

**Given**: File is not in Git repository
**When**: User tries to commit
**Then**: Program shows error message

#### Requirement: Git Push

The program SHALL let users push to remote.

##### Scenario: Push Changes

**Given**: Repository has remote configured
**When**: User clicks Git > Push
**Then**: Commits are sent to remote server

##### Scenario: Push Without Remote

**Given**: Repository has no remote
**When**: User tries to push
**Then**: Program shows error message

#### Requirement: Git Pull

The program SHALL let users pull from remote.

##### Scenario: Pull Changes

**Given**: Remote has new commits
**When**: User clicks Git > Pull
**Then**: New changes download to local repository

##### Scenario: Pull Clash

**Given**: Your copy and server copy both changed
**When**: User pulls
**Then**: Program shows clash message

#### Requirement: Git Status Display

The program SHALL show Git status in status bar.

##### Scenario: Show Repository Status

**Given**: File is in Git repository
**When**: User opens file
**Then**: Status bar shows repository name

##### Scenario: Show Non-Repository Status

**Given**: File is not in Git repository
**When**: User opens file
**Then**: Status bar shows "Not in Git repository"

---

## Conversion Specifications

This covers document format conversion.

### Requirements

#### Requirement: Import Word Files

The program SHALL convert Word files to AsciiDoc.

##### Scenario: Open Word File

**Given**: User has .docx file
**When**: User opens the file
**Then**: Program converts it to AsciiDoc

##### Scenario: Handle Conversion Error

**Given**: Word file is corrupted
**When**: User tries to open it
**Then**: Program shows error message

#### Requirement: Import PDF Files

The program SHALL extract text from PDF files.

##### Scenario: Open PDF File

**Given**: User has .pdf file
**When**: User opens the file
**Then**: Program extracts text to editor

##### Scenario: PDF With Tables

**Given**: PDF has tables
**When**: User opens it
**Then**: Tables are formatted in AsciiDoc

#### Requirement: Export to HTML

The program SHALL export to HTML format.

##### Scenario: Export HTML

**Given**: User has AsciiDoc document
**When**: User clicks File > Export > HTML
**Then**: Program creates HTML file

#### Requirement: Export to PDF

The program SHALL export to PDF format.

##### Scenario: Export PDF

**Given**: User has AsciiDoc document
**When**: User clicks File > Export > PDF
**Then**: Program creates PDF file

#### Requirement: Export to Word

The program SHALL export to Word format.

##### Scenario: Export Word

**Given**: User has AsciiDoc document
**When**: User clicks File > Export > Word
**Then**: Program creates .docx file

#### Requirement: Paste from Copy

The program SHALL paste HTML from copy area.

##### Scenario: Paste HTML

**Given**: User copies HTML stuff
**When**: User clicks File > Import > Clipboard
**Then**: Program changes HTML to AsciiDoc

---

## User Interface Specifications

This covers how the program looks and works.

### Requirements

#### Requirement: File Operations

The program SHALL provide file menu operations.

##### Scenario: New File

**Given**: Program is open
**When**: User presses Ctrl+N
**Then**: Editor clears and shows new blank file

##### Scenario: Open File

**Given**: User has .adoc file
**When**: User presses Ctrl+O and selects file
**Then**: File content appears in editor

##### Scenario: Save File

**Given**: User edited text
**When**: User presses Ctrl+S
**Then**: File is saved to disk

##### Scenario: Save As

**Given**: User has new file
**When**: User clicks File > Save As
**Then**: Program asks for file name and saves

#### Requirement: Dark Mode

The program SHALL support dark color scheme.

##### Scenario: Toggle Dark Mode

**Given**: Program is in light mode
**When**: User presses Ctrl+D
**Then**: Colors change to dark theme

##### Scenario: Remember Dark Mode

**Given**: User enabled dark mode
**When**: User restarts program
**Then**: Dark mode is still on

#### Requirement: Font Zoom

The program SHALL let users change text size.

##### Scenario: Zoom In

**Given**: Editor shows normal text
**When**: User presses Ctrl++
**Then**: Text gets bigger

##### Scenario: Zoom Out

**Given**: Editor shows normal text
**When**: User presses Ctrl+-
**Then**: Text gets smaller

#### Requirement: Status Bar

The program SHALL show information in status bar.

##### Scenario: Show Line and Column

**Given**: User is typing
**When**: User looks at status bar
**Then**: Status bar shows line and column number

##### Scenario: Show Git Status

**Given**: File is in Git repository
**When**: User opens file
**Then**: Status bar shows repository name

##### Scenario: Show File Path

**Given**: File is open
**When**: User looks at status bar
**Then**: Status bar shows full file path

#### Requirement: Keyboard Shortcuts

The program SHALL provide keyboard shortcuts.

##### Scenario: Use Shortcuts

**Given**: Program is open
**When**: User presses keyboard shortcut
**Then**: Action happens immediately

Common shortcuts:
- Ctrl+N - New file
- Ctrl+O - Open file
- Ctrl+S - Save file
- Ctrl+Q - Quit program
- Ctrl+F - Find text
- Ctrl+D - Dark mode
- Ctrl++ - Zoom in
- Ctrl+- - Zoom out

#### Requirement: Settings Persistence

The program SHALL remember user settings.

##### Scenario: Save Window Size

**Given**: User resizes window
**When**: User closes and reopens program
**Then**: Window is same size

##### Scenario: Save Last File

**Given**: User opens a file
**When**: User closes and reopens program
**Then**: Same file opens automatically

##### Scenario: Save Theme

**Given**: User changes to dark mode
**When**: User closes and reopens program
**Then**: Dark mode is still active

#### Requirement: Safe File Saving

The program SHALL save files safely.

##### Scenario: Atomic Save

**Given**: User saves file
**When**: Save operation runs
**Then**: Program writes to temp file first, then replaces original

##### Scenario: Save Error

**Given**: Disk is full
**When**: User tries to save
**Then**: Program shows error and keeps original file

#### Requirement: Path Security

The program SHALL prevent path attacks.

##### Scenario: Sanitize Paths

**Given**: User provides file path
**When**: Program processes path
**Then**: Program blocks dangerous paths like "../../../etc/passwd"

---

## Technical Specifications

This covers how the program is built.

### Requirements

#### Requirement: Dependencies

The program SHALL use these main libraries:

- **PySide6** 6.9.0+ - Makes windows and buttons
- **asciidoc3** 10.2.1+ - Turns AsciiDoc to HTML
- **pypandoc** 1.13+ - Changes file types
- **Pandoc** (separate program) - Does the conversion work

##### Scenario: Check Dependencies

**Given**: Python 3.11+ is installed
**When**: User runs `pip install -r requirements.txt`
**Then**: All dependencies install successfully

#### Requirement: Work in Background

The program SHALL do slow work in the background.

##### Scenario: Git in Background

**Given**: User saves a big file to Git
**When**: Git work starts
**Then**: Program window still works

##### Scenario: Change Files in Background

**Given**: User changes a big Word file
**When**: Change work starts
**Then**: Program window still works

#### Requirement: No Double Work

The program SHALL stop you from doing two things at once.

##### Scenario: Stop Double Save

**Given**: Git save is running
**When**: User tries to save again
**Then**: Save button turns off

##### Scenario: Stop Double Change

**Given**: File change is running
**When**: User tries another change
**Then**: Program waits for first to finish

---

## Security Specifications

This covers how we keep things safe.

### Requirements

#### Requirement: No Data Collection

The program SHALL NOT send data to external servers.

##### Scenario: Check Network

**Given**: Program is running
**When**: User monitors network traffic
**Then**: No data is sent out

#### Requirement: Local Storage Only

The program SHALL store all data locally.

##### Scenario: Check Settings

**Given**: User changes settings
**When**: Program saves settings
**Then**: Settings file is in local config directory

Platform locations:
- Linux: `~/.config/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`
- Mac: `~/Library/Application Support/AsciiDocArtisan/`

#### Requirement: Safe Git Work

The program SHALL run Git in a safe way.

##### Scenario: Use Safe Commands

**Given**: Program runs Git command
**When**: Command starts
**Then**: Program uses safe method

##### Scenario: Check Repository First

**Given**: User tries Git work
**When**: Program checks
**Then**: Program makes sure file is in Git first

---

## Performance Specifications

This covers how fast it should be.

### Requirements

#### Requirement: Fast Startup

The program SHALL start quickly.

##### Scenario: Measure Startup Time

**Given**: Program is not running
**When**: User starts program
**Then**: Window appears within 3 seconds

#### Requirement: Responsive Preview

The program SHALL update preview smoothly.

##### Scenario: Preview Delay

**Given**: User types in editor
**When**: User stops typing
**Then**: Preview updates within 500 milliseconds

#### Requirement: Handle Large Files

The program SHALL work with big files.

##### Scenario: Open 1 MB File

**Given**: User has 1 MB .adoc file
**When**: User opens it
**Then**: Program loads it smoothly

##### Scenario: Open 10 MB File

**Given**: User has 10 MB .adoc file
**When**: User opens it
**Then**: Program loads it but may be slower

#### Requirement: Use Memory Well

The program SHALL use computer memory well.

##### Scenario: No Memory Waste

**Given**: Program runs for 8 hours
**When**: User checks memory use
**Then**: Memory use stays the same

---

## Testing Specifications

This covers how we test the program.

### Requirements

#### Requirement: Unit Tests

The program SHALL have unit tests for all features.

##### Scenario: Run Tests

**Given**: Developer has code
**When**: Developer runs `make test`
**Then**: All tests pass

##### Scenario: Test Coverage

**Given**: Tests are complete
**When**: Coverage report is generated
**Then**: Coverage is 80% or higher

#### Requirement: Integration Tests

The program SHALL have integration tests.

##### Scenario: Test File Operations

**Given**: Test suite runs
**When**: File operation tests run
**Then**: New, Open, Save, Save As all work

##### Scenario: Test Git Operations

**Given**: Test repository exists
**When**: Git tests run
**Then**: Commit, Push, Pull all work

#### Requirement: Platform Tests

The program SHALL be tested on all platforms.

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
- Security features implemented
- OpenSpec-style specifications

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

**Document Info**: Main specification | Reading level Grade 6.0 | Version 1.1.0 | October 2025
