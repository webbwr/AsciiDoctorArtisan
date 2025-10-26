# Program Rules

**Reading Level**: Grade 5.0
**Version**: 1.1.0
**Last Updated**: October 2025

## What This Is

This tells you what the program must do.

Each rule says what MUST happen.

## What The Program Does

This program helps you write papers.

It:
- Shows your work as you type
- Opens Word, PDF, Markdown files
- Saves to Word, PDF, Markdown
- Uses Git to save versions
- Works on all computers

Think of it like Word, but for AsciiDoc.

## Who Uses It

- People who write manuals
- People who write code
- Teachers and students
- Writers
- Teams

---

## Core Rules

### Rule: Works On All Computers

The program MUST work on Windows, Mac, and Linux.

**Test**: Run on each type. It must start with no errors.

### Rule: Needs Python 3.11

The program MUST need Python 3.11 or newer.

**Test**: Try with Python 3.10. It must show an error.

**Test**: Use Python 3.11. It must work.

### Rule: Free To Use

The program MUST be free. MIT License.

**Test**: Check LICENSE file. It must say MIT.

---

## Install Rules

### Rule: Easy Install

The program MUST have install scripts.

**Test**: Run the script. It must install all parts.

### Rule: Check What You Have

The install script MUST check for Python, Pandoc, Git.

**Test**: Run without Pandoc. Script must tell you.

### Rule: Make Safe Space

The install script MUST offer to make a safe space for tools.

**Test**: Say yes. Tools go in that space.

**Test**: Say no. Tools go on your computer.

### Rule: Test After Install

The install script MUST test everything.

**Test**: After install, script must check all parts work.

---

## Edit Rules

### Rule: Type Text

The program MUST let you type.

**Test**: Type "Hello". It must show in the editor.

### Rule: Copy And Paste

The program MUST let you copy, cut, paste.

**Test**: Press Ctrl+C. Text must copy.

**Test**: Press Ctrl+V. Text must paste.

### Rule: Undo And Redo

The program MUST let you undo.

**Test**: Make a change. Press Ctrl+Z. Change must go away.

**Test**: Press Ctrl+Y. Change must come back.

### Rule: Find Words

The program MUST let you find words.

**Test**: Search for "hello". Program must find it.

### Rule: Go To Line

The program MUST let you jump to a line.

**Test**: Go to line 50. Cursor must move there.

### Rule: Show Line Numbers

The program MUST show line numbers.

**Test**: Open program. Line numbers must show on left.

---

## Preview Rules

### Rule: Show Preview

The program MUST show HTML preview.

**Test**: Type text. Wait 1 second. Preview must update.

### Rule: Move Together

The editor and preview MUST move together.

**Test**: Scroll editor. Preview must scroll too.

**Test**: Scroll preview. Editor must scroll too.

### Rule: Wait To Update

The preview MUST wait before it updates.

**Test**: Type fast. Preview must wait until you stop.

### Rule: Show Plain Text On Error

If HTML fails, program MUST show plain text.

**Test**: Break the HTML. Program must show text, not crash.

---

## Git Rules

### Rule: Commit Changes

The program MUST let you commit.

**Test**: In Git folder, commit must work.

**Test**: Not in Git folder, must show error.

### Rule: Push Changes

The program MUST let you push.

**Test**: Push must send commits to server.

**Test**: No server set up, must show error.

### Rule: Pull Changes

The program MUST let you pull.

**Test**: Pull must get new commits.

**Test**: If clash, must show message.

### Rule: Show Git Status

The program MUST show Git status.

**Test**: In Git folder, status bar shows folder name.

**Test**: Not in Git folder, shows "Not in Git".

---

## File Change Rules

### Rule: Open Word Files

The program MUST open .docx files.

**Test**: Open Word file. It must change to AsciiDoc.

**Test**: Bad Word file must show error.

### Rule: Open PDF Files

The program MUST open .pdf files.

**Test**: Open PDF. It must get text out.

### Rule: Open Markdown Files

The program MUST open .md files.

**Test**: Open Markdown. It must change to AsciiDoc.

### Rule: Open HTML Files

The program MUST open .html files.

**Test**: Open HTML. It must change to AsciiDoc.

### Rule: Save To HTML

The program MUST save to .html.

**Test**: Click Save As HTML. It must make HTML file.

### Rule: Save To PDF

The program MUST save to .pdf.

**Test**: Click Save As PDF. It must make PDF file.

### Rule: Save To Word

The program MUST save to .docx.

**Test**: Click Save As Word. It must make Word file.

### Rule: Save To Markdown

The program MUST save to .md.

**Test**: Click Save As Markdown. It must make MD file.

### Rule: Paste From Copy

The program MUST paste from copy area.

**Test**: Copy HTML. Paste it. Must change to AsciiDoc.

### Rule: No Questions

The program MUST NOT ask questions on open or save.

**Test**: Open any file. No pop-ups.

**Test**: Save As any type. No pop-ups.

---

## Look And Feel Rules

### Rule: New File

The program MUST let you make new files.

**Test**: Press Ctrl+N. Editor must clear.

### Rule: Open File

The program MUST let you open files.

**Test**: Press Ctrl+O. File picker must show.

### Rule: Save File

The program MUST let you save.

**Test**: Press Ctrl+S. File must save.

### Rule: Save As

The program MUST let you save as new name.

**Test**: Click Save As. Must ask for name.

### Rule: Dark Mode

The program MUST have dark mode.

**Test**: Press Ctrl+D. Colors must change to dark.

**Test**: Restart. Dark mode must stay on.

### Rule: Change Text Size

The program MUST let you zoom text.

**Test**: Press Ctrl++. Text must get bigger.

**Test**: Press Ctrl+-. Text must get smaller.

### Rule: Status Bar

The program MUST show info in status bar.

**Test**: Look at status bar. Must show line number.

**Test**: Look at status bar. Must show file path.

### Rule: Fast Keys

The program MUST have keyboard shortcuts.

**Test**: Press Ctrl+N. New file must open.

**Test**: Press Ctrl+Q. Program must close.

Fast keys:
- Ctrl+N = New file
- Ctrl+O = Open file
- Ctrl+S = Save
- Ctrl+Q = Close
- Ctrl+F = Find
- Ctrl+D = Dark mode
- Ctrl++ = Big text
- Ctrl+- = Small text

### Rule: Remember Settings

The program MUST save your settings.

**Test**: Make window big. Close. Open. Window must be big.

**Test**: Open a file. Close. Open. Same file must open.

**Test**: Turn on dark mode. Close. Open. Dark mode must be on.

### Rule: Save Files Safely

The program MUST save files with no risk.

**Test**: Save file. Program must write to temp first, then replace.

**Test**: Disk full. Must show error and keep old file.

### Rule: Block Bad Paths

The program MUST stop dangerous paths.

**Test**: Try path like "../../../etc/passwd". Must block it.

---

## Build Rules

### Rule: Use Right Tools

The program MUST use:
- PySide6 6.9.0+ for windows
- asciidoc3 10.2.1+ for HTML
- pypandoc 1.13+ for file changes
- Pandoc for conversions
- wkhtmltopdf for PDF

**Test**: Install tools. All must work.

### Rule: Work In Background

The program MUST do slow work in background.

**Test**: Save to Git. Window must still work.

**Test**: Open big Word file. Window must still work.

### Rule: No Double Work

The program MUST stop two things at once.

**Test**: While saving, save button must turn off.

**Test**: While changing file, must wait for finish.

---

## Safety Rules

### Rule: No Data Sent Out

The program MUST NOT send data anywhere.

**Test**: Watch network. No data must go out.

### Rule: Save Local Only

The program MUST save everything on your computer.

**Test**: Check settings file. Must be in local folder.

Settings save here:
- Linux: `~/.config/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`
- Mac: `~/Library/Application Support/AsciiDocArtisan/`

### Rule: Safe Git Commands

The program MUST run Git safely.

**Test**: Run Git command. Must use safe method.

**Test**: Try Git without Git folder. Must check first.

---

## Speed Rules

### Rule: Start Fast

The program MUST start quick.

**Test**: Time it. Must show window in 3 seconds.

### Rule: Update Preview Fast

The preview MUST update smooth.

**Test**: Type text. Preview must update in 500ms.

### Rule: Handle Big Files

The program MUST work with big files.

**Test**: Open 1 MB file. Must load smooth.

**Test**: Open 10 MB file. May be slow, but must work.

### Rule: Use Memory Well

The program MUST not waste memory.

**Test**: Run 8 hours. Memory use must stay same.

---

## Test Rules

### Rule: Unit Tests

The program MUST have tests for all parts.

**Test**: Run `make test`. All must pass.

**Test**: Check coverage. Must be 80% or more.

### Rule: Full Tests

The program MUST test real use.

**Test**: Test New, Open, Save, Save As. All must work.

**Test**: Test Commit, Push, Pull. All must work.

### Rule: Test All Computers

The program MUST be tested on all types.

**Test**: Run tests on Windows. All must pass.

**Test**: Run tests on Linux. All must pass.

**Test**: Run tests on Mac. All must pass.

---

## Version History

### Version 1.1.0 (Now)

**Status**: Works
**Date**: October 2025

**What's New**:
- All parts work
- 71 tests pass
- Works on all computers
- Safe and secure
- Simple rules

### Version 1.0.0 (Old)

**Status**: First try
**Date**: 2024

**What It Had**:
- Basic edit
- Basic preview
- First tests

---

## What We Might Add

Things for later:

### Edit
- Check spelling
- Find and replace
- Auto-complete
- Color text

### Preview
- Zoom preview
- Print preview
- Change colors

### Git
- See old versions
- Compare versions
- Use branches
- Merge help

### Teams
- Share files
- Edit together
- Add notes
- Team rooms

### AI
- Better file changes
- Writing help
- Auto-format
- Make content

---

## Summary

**What It Does**:
Helps you write AsciiDoc. Shows preview. Uses Git. Changes file types.

**Who It's For**:
Writers, coders, students, teachers, teams.

**Main Parts**:
Live preview, file changes, Git, works everywhere, safe.

**Status**:
Version 1.1.0 - Ready to use.

**Reading Level**:
Grade 5.0 - Easy to read!

---

**Doc Info**: Main rules | Grade 5.0 | v1.1.0 | October 2025
