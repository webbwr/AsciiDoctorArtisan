# What AsciiDoc Artisan Must Do

**Reading Level**: Grade 5.0 (Elementary)
**Version**: 1.1.0
**Last Updated**: October 2025

This paper tells you what AsciiDoc Artisan needs to do.

## What This Paper Is For

This tells you:
- What the program does
- Who uses it
- What it can do
- How we know it works

## What Is AsciiDoc Artisan?

AsciiDoc Artisan helps people write papers. It's a program that:

- Shows your work while you type
- Changes Word files to AsciiDoc
- Saves to Git so you can track changes
- Works on Windows, Mac, and Linux

Think of it like Word, but for AsciiDoc files.

### Why Use AsciiDoc?

AsciiDoc is:
- Plain text (works on any computer)
- Easy to read
- Good with Git
- Can do what Word does

### What Makes It Special?

1. See changes right away
2. Never loses your work
3. Works with other programs
4. Easy to use
5. Free

## Who Uses It?

### 1. People Who Write Instructions
They write manuals. They need to see how it looks.

### 2. People Who Write Code
They write README files. They want Git.

### 3. Teachers and Students
They write papers. They need to change file types.

### 4. Writers
They make long papers. They like plain text.

### 5. Teams
They share files. They need good tools.

## Main Things It Does

### 1. Live View

**What it does**:
- Shows HTML on the right side
- Changes as you type
- Moves with where you're typing

**Why it's good**:
You don't need to save and open a web page.

### 2. Change File Types

**What you can open**:
- .adoc files
- .docx files (Word)
- .pdf files (gets the text)

**What you can save as**:
- HTML (web pages)
- PDF (print files)
- Word (.docx)
- Markdown (.md)

**Why it's good**:
Work with any file type.

### 3. Git Help

**What you can do**:
- Save changes (commit)
- Send to GitHub (push)
- Get new version (pull)

**Why it's good**:
Track all your changes. Work with teams.

### 4. Safe Saving

**How it works**:
- Saves to test file first
- Only replaces old file if it works
- Your file is safe if computer stops

**Why it's good**:
Your work won't break.

### 5. Remembers Things

**What it remembers**:
- Last file you used
- Window size
- Light or dark colors
- Text size

**Why it's good**:
Start right away. No setup needed.

### 6. Easy to Use

**What's in it**:
- Clear menus
- Quick keys (Ctrl+S to save)
- Dark mode
- Make text bigger or smaller

**Why it's good**:
Anyone can learn it fast.

## What It Must Do

Things the program must be able to do:

### Files

**Must have**:
- ✓ Make new files
- ✓ Open files
- ✓ Save files
- ✓ Save with new name
- ✓ Remember last file

**Would be nice**:
- List of recent files

### Editing

**Must have**:
- ✓ Type and edit
- ✓ Copy and paste
- ✓ Undo
- ✓ Find words

**Would be nice**:
- Find and change
- Check spelling

### Preview

**Must have**:
- ✓ Show HTML
- ✓ Change as you type
- ✓ Move with you

**Would be nice**:
- Make preview bigger

### Change Types

**Must have**:
- ✓ Open Word files
- ✓ Open PDFs
- ✓ Save as HTML
- ✓ Save as PDF

**Would be nice**:
- Open more types

### Git

**Must have**:
- ✓ Save changes
- ✓ Send to server
- ✓ Get from server

**Would be nice**:
- See old versions

### Look and Feel

**Must have**:
- ✓ Light and dark
- ✓ Make text bigger
- ✓ Quick keys
- ✓ Bottom bar shows info

**Would be nice**:
- Pick colors

### Settings

**Must have**:
- ✓ Remember window size
- ✓ Remember colors
- ✓ Remember last folder

**Would be nice**:
- Pick your own quick keys

## How We Build It

### What We Use

**Python 3.11 or newer**

Why Python?
- Easy to write
- Works everywhere
- Lots of tools

### Main Tools

**PySide6** (version 6.9.0+)
- Makes windows
- Makes buttons
- Handles clicks

**asciidoc3** (version 10.2.1+)
- Turns AsciiDoc to HTML
- Makes the preview

**pypandoc** (version 1.13+)
- Changes file types

**Pandoc** (separate program)
- Does the real work
- Must install it

### How It's Built

```
Parts:
- Main Window (what you see)
- Editor (where you type)
- Preview (shows HTML)
- Git Tools
- File Changer
- Settings
```

### How It Works

**When you type**:
1. You type on left
2. Program waits a bit
3. Changes to HTML
4. Shows on right

**When you save**:
1. Gets your text
2. Writes to test file
3. If good, replaces old file
4. Updates title

**When you change types**:
1. Pick file to open
2. Sees what type it is
3. Changes to AsciiDoc
4. Shows in editor

## How We Test It

### What We Test

**Basic Stuff**:
- Can you make files?
- Can you open files?
- Can you save files?
- Does typing work?

**Preview**:
- Does it show HTML?
- Does it change?
- Does it move right?

**Changing Types**:
- Can it open Word files?
- Can it open PDFs?
- Can it save as PDF?

**Git**:
- Can you save changes?
- Can you send to server?
- Can you get from server?

**Buttons and Menus**:
- Do buttons work?
- Do menus work?
- Do quick keys work?
- Does dark mode work?

### How We Test

**Computer Tests**:
- Computer runs tests
- Checks if it works
- Runs when we change code

**People Tests**:
- People try it
- Click all buttons
- Try to break it

**System Tests**:
- Test on Windows
- Test on Mac
- Test on Linux

### When We Test

- When we add new stuff
- Before we share it
- When someone finds a bug
- Often to catch problems

## Keeping It Safe

### File Safety

**How we keep files safe**:
- Use safe saving
- Check file paths
- Check all inputs
- Handle errors well

**What this means**:
Your files won't break. Bad files can't hurt you.

### Code Safety

**What we do**:
- Check what you type
- Check file names
- Stop bad code
- Use safe tools

**What this means**:
Program won't do bad things.

### Privacy

**What we take**:
- Nothing! All stays on your computer

**What we don't do**:
- Don't send data out
- Don't watch you
- Don't save passwords
- Don't share files

**API Keys**:
If you use AI, you give your own key. We never see it.

## How Fast It Should Be

### Speed

Should be:
- Fast to start (3 seconds)
- Quick to save (1 second)
- Smooth preview (half second)
- Never freeze

### Memory

Should:
- Use normal memory
- Not get slow
- Clean up after itself
- Handle big files

### File Sizes

Works good with:
- Files up to 1 MB (normal)
- Files up to 10 MB (big)
- Slow with files over 10 MB

## Ideas for Later

Things we might add:

### More Stuff
- Check spelling
- Find and change
- More save types
- Different colors
- Add-ons

### Better Git
- See old versions
- Compare versions
- Use branches

### Work Together
- Share with teams
- Edit at same time
- Leave notes

### Better AI
- Better changes
- Writing help
- Auto-fix format

## Old Versions

**Version 1.1.0** (Now)
- All main stuff works
- Tests pass
- Works everywhere
- Safe

**Version 1.0.0** (Before)
- First try
- Basic stuff
- First tests

## Questions?

**Where are full details?**
Look in `.specify/specs/` folder.

**Found a bug?**
Tell us on GitHub. Say what happened.

**Can I help?**
Yes! Read [how-to-contribute.md](docs/how-to-contribute.md).

**Is it free?**
Yes! MIT License means free for all.

## Summary

**What it does**:
Helps you write AsciiDoc with live view and Git.

**Who it's for**:
Writers, coders, students, teachers, teams.

**Main stuff**:
Live view, change types, Git, safe saves, easy to use.

**Status**:
Version 1.1.0 - Works well.

**How hard to read**:
Grade 5.0 - Anyone can read it!

---

**Document Info**: Main spec | Reading level Grade 5.0 | October 2025 | Version 1.1.0
