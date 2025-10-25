# What AsciiDoc Artisan Must Do

**Reading Level**: Grade 5.8 (Elementary)
**Version**: 1.1.0
**Last Updated**: October 2025

This document tells you everything AsciiDoc Artisan needs to do. Think of it like a checklist we use when building the program.

## What This Document Is For

This explains:
- What the program does
- Who uses it
- What features it has
- How we know it works

If you want to understand what we're building, read this!

## Table of Contents

1. [What Is AsciiDoc Artisan?](#what-is-asciidoc-artisan)
2. [Who Uses This Program?](#who-uses-this-program)
3. [Main Features](#main-features)
4. [What It Must Do](#what-it-must-do)
5. [How We Build It](#how-we-build-it)
6. [How We Test It](#how-we-test-it)
7. [Keeping It Safe](#keeping-it-safe)

---

## What Is AsciiDoc Artisan?

AsciiDoc Artisan helps people write documents. It's a program that:

- **Shows your work** while you type (live preview)
- **Changes file types** (Word to AsciiDoc, AsciiDoc to PDF, etc.)
- **Saves to Git** so you can track changes
- **Works everywhere** (Windows, Mac, Linux)

Think of it like Microsoft Word, but for AsciiDoc files. AsciiDoc is a simple way to format text (like making headings, lists, and bold words).

### Why Use AsciiDoc?

AsciiDoc is:
- **Plain text** - Works on any computer
- **Easy to read** - No weird codes
- **Version friendly** - Works great with Git
- **Powerful** - Can do everything Word can do

### What Makes This Program Special?

1. **See changes right away** - No need to press a button
2. **Never loses your work** - Saves files safely
3. **Works with other programs** - Opens Word files, saves as PDF
4. **Easy to use** - Simple buttons and menus
5. **Free and open** - Anyone can use it

---

## Who Uses This Program?

### 1. Technical Writers
People who write instructions and manuals. They need to see how it looks while they work.

### 2. Software Developers
Programmers who write README files and documentation. They want Git built in.

### 3. Teachers and Students
People writing papers and reports. They need to change file types easily.

### 4. Content Creators
Writers making long documents. They like plain text that works everywhere.

### 5. Documentation Teams
Groups who share files and work together. They need reliable tools.

---

## Main Features

Here's what the program does:

### 1. Live Preview (See Changes Right Away)

**What it does**:
- Shows HTML version on the right side
- Updates as you type (in less than half a second)
- Scrolls along with where you're typing

**Why it matters**:
You don't need to save and open in a browser. See your work immediately.

### 2. File Conversion (Change File Types)

**What you can open**:
- `.adoc` files (AsciiDoc)
- `.docx` files (Word documents)
- `.pdf` files (PDF documents - pulls out text)

**What you can save as**:
- HTML (web pages)
- PDF (print documents)
- Word (.docx)
- Markdown (.md)
- Plain text (.txt)

**Why it matters**:
Work with any file type. Share with people using different programs.

### 3. Git Support (Track Changes)

**What you can do**:
- **Commit** - Save your changes
- **Push** - Send to GitHub
- **Pull** - Get newest version
- **Status** - See what changed

**Why it matters**:
Keep track of all your changes. Work with teams. Never lose old versions.

### 4. Safe Saving (Never Lose Work)

**How it works**:
- Saves to a temporary file first
- Only replaces old file if save works
- If computer crashes, your file is safe

**Why it matters**:
Your documents are protected even if something goes wrong.

### 5. Remember Your Setup (Session Memory)

**What it remembers**:
- Last file you opened
- Window size and position
- Light or dark colors
- Text size (zoom level)
- Last folder you used

**Why it matters**:
Start working right away. No need to set everything up again.

### 6. Easy to Use (Simple Interface)

**What's included**:
- Clear menus (File, Edit, View, Git, Help)
- Keyboard shortcuts (Ctrl+S to save, etc.)
- Dark mode option
- Font zoom (make text bigger or smaller)

**Why it matters**:
Anyone can learn it quickly. Works like other programs you know.

---

## What It Must Do

Here are all the things the program must be able to do:

### File Operations

**Must have**:
- ✓ Create new files
- ✓ Open files (.adoc, .docx, .pdf)
- ✓ Save files
- ✓ Save As (pick new name/place)
- ✓ Remember last file opened
- ✓ Auto-save every few minutes

**Nice to have**:
- Recent files list
- File templates

### Text Editing

**Must have**:
- ✓ Type and edit text
- ✓ Copy, cut, paste
- ✓ Undo and redo
- ✓ Find text
- ✓ Go to line number
- ✓ Show line numbers

**Nice to have**:
- Find and replace
- Spell check

### Preview Window

**Must have**:
- ✓ Show HTML preview
- ✓ Update as you type
- ✓ Scroll along with editor
- ✓ Work even if preview breaks

**Nice to have**:
- Zoom preview
- Print preview

### Document Conversion

**Must have**:
- ✓ Import Word files (.docx)
- ✓ Import PDFs (.pdf) - text only
- ✓ Export to HTML
- ✓ Export to PDF
- ✓ Keep formatting (headings, lists, etc.)

**Nice to have**:
- Import Markdown
- Export to more formats

### Git Features

**Must have**:
- ✓ Commit changes
- ✓ Push to remote
- ✓ Pull from remote
- ✓ Show status

**Nice to have**:
- Branch management
- Conflict resolution

### User Interface

**Must have**:
- ✓ Light and dark mode
- ✓ Make text bigger/smaller (zoom)
- ✓ Keyboard shortcuts
- ✓ Status bar (shows line number, file name)
- ✓ Menu bar (File, Edit, View, etc.)

**Nice to have**:
- Customizable colors
- Different fonts

### Settings

**Must have**:
- ✓ Remember window size
- ✓ Remember dark/light mode
- ✓ Remember last folder
- ✓ Remember zoom level
- ✓ Save settings automatically

**Nice to have**:
- Custom keyboard shortcuts
- Editor preferences

---

## How We Build It

### Programming Language
**Python 3.11 or newer**

Why Python?
- Easy to read and write
- Works on all computers
- Lots of helpful tools available

### Main Tools We Use

**PySide6** (version 6.9.0+)
- Makes windows and buttons
- Creates menus
- Handles clicks and typing

**asciidoc3** (version 10.2.1+)
- Turns AsciiDoc into HTML
- Handles all formatting
- Processes the preview

**pypandoc** (version 1.13+)
- Changes file types
- Converts Word to AsciiDoc
- Exports to different formats

**Pandoc** (system program)
- Does the actual conversion
- Must be installed separately
- Required for file conversion

### How It's Organized

```
Program Parts:
├── Main Window (what you see)
├── Editor (where you type)
├── Preview (shows HTML)
├── Git Tools (version control)
├── File Converter (changes types)
└── Settings (remembers preferences)
```

### How It Works

**When you type**:
1. You type in the editor (left side)
2. Program waits a moment (so it's not too fast)
3. Converts AsciiDoc to HTML
4. Shows HTML in preview (right side)

**When you save**:
1. Gets text from editor
2. Writes to temporary file
3. If successful, replaces old file
4. Updates window title

**When you convert**:
1. Pick file to open
2. Program detects file type
3. Converts to AsciiDoc
4. Shows in editor

---

## How We Test It

### What We Test

**Basic Operations**:
- Can you create a new file?
- Can you open files?
- Can you save files?
- Does typing work?

**Preview**:
- Does it show HTML?
- Does it update when you type?
- Does it scroll correctly?
- Does it handle errors?

**Conversions**:
- Can it open Word files?
- Can it open PDFs?
- Can it export to PDF?
- Does formatting stay correct?

**Git**:
- Can you commit?
- Can you push?
- Can you pull?
- Do errors show up clearly?

**User Interface**:
- Do buttons work?
- Do menus work?
- Do keyboard shortcuts work?
- Does dark mode work?

### How We Test

**1. Automatic Tests**
- Computer runs tests
- Checks if features work
- Runs every time we change code

**2. Manual Tests**
- People try using it
- Click all the buttons
- Try to break it
- Check on different computers

**3. Platform Tests**
- Test on Windows
- Test on Mac
- Test on Linux
- Make sure it works everywhere

### When We Test

- Every time we add a feature
- Before we release a new version
- When someone reports a bug
- Regularly to catch problems early

---

## Keeping It Safe

### File Safety

**How we protect files**:
- Use safe file saving (atomic saves)
- Check file paths (prevent bad access)
- Validate all inputs
- Handle errors gracefully

**What this means**:
Your files won't get corrupted. Bad files can't harm your computer.

### Code Safety

**What we do**:
- Check all user input
- Validate file names
- Prevent code injection
- Use secure libraries

**What this means**:
The program won't do anything harmful. Your documents stay private.

### Privacy

**What we collect**:
- Nothing! All data stays on your computer

**What we don't do**:
- Don't send data to internet
- Don't track what you do
- Don't save passwords
- Don't share your files

**API Keys**:
If you use AI features, you provide your own API key. We never see it.

---

## Performance Goals

### Speed Requirements

The program should be:
- **Fast to start** - Opens in 3 seconds or less
- **Quick to save** - Saves in 1 second or less
- **Smooth preview** - Updates in half a second or less
- **Never freeze** - Always responds to clicks

### Memory Use

The program should:
- Use reasonable memory (not too much)
- Not slow down over time
- Clean up after itself
- Handle large files well

### File Size Limits

Works well with:
- Files up to 1 MB (typical)
- Can handle files up to 10 MB (large)
- May be slow with files over 10 MB

---

## Future Ideas

Things we might add later:

### More Features
- Spell checking
- Find and replace
- More export formats
- Custom themes
- Plugin system

### Better Git
- See file history
- Compare versions
- Manage branches
- Resolve conflicts

### Collaboration
- Share files with teams
- Real-time editing
- Comments and notes
- Review changes

### AI Improvements
- Better conversions
- Writing suggestions
- Auto-formatting
- Smart completion

---

## Version History

**Version 1.1.0** (Current)
- All main features working
- Tests passing
- Works on all platforms
- Safe and secure

**Version 1.0.0** (Previous)
- First release
- Basic features
- Initial testing

---

## Questions?

**Where are the full specifications?**
Look in `.specify/specs/` folder for detailed technical specs.

**What if I find a bug?**
Report it on GitHub. Tell us what happened and how to repeat it.

**Can I help build this?**
Yes! Read [how-to-contribute.md](docs/how-to-contribute.md) to learn how.

**Is this really free?**
Yes! MIT License means you can use it for anything.

---

## Summary

**What it does**:
Helps you write AsciiDoc documents with live preview, file conversion, and Git support.

**Who it's for**:
Writers, developers, students, teachers, and documentation teams.

**Main features**:
Live preview, file conversion, Git integration, safe saving, easy to use.

**Current status**:
Version 1.1.0 - Working and stable.

**Reading level**:
Grade 5.8 (Elementary) - Anyone can understand!

---

**Document Info**: This is the main specification | Reading level Grade 5.8 | Last updated October 2025 | Version 1.1.0
