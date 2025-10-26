# What Changed

This tells what we did.

## Next Update (Not Out Yet)

### File Types - Big News!

You can now open many file types:
- Word files (.docx)
- Markdown files (.md)
- Web pages (.html)
- PDF files (.pdf)
- AsciiDoc files (.adoc)

You can save to many types too:
- Word (.docx)
- Markdown (.md)
- Web pages (.html)
- PDF (.pdf)
- AsciiDoc (.adoc)

All files open right away. No questions asked!

### Easier to Use

We took out the pop-up questions. The program just works now.

When you open a file, it changes to AsciiDoc. No waiting. No asking.

When you save a file, it changes the type for you. No pop-ups. No choices to make.

### What We Removed

We took out two dialog boxes:
- ImportOptionsDialog (no more import questions)
- ExportOptionsDialog (no more export questions)

This made the program simpler. It removed 186 lines of code we don't need.

### AI Helper is Now Optional

AI help is in Settings now. You don't see it every time.

Want AI help? Turn it on in Settings.
Don't want it? Just use Pandoc. It works great!

### New Tools You Need

You need wkhtmltopdf now. It makes PDF files.

Get it here:
- Linux: `sudo apt install wkhtmltopdf`
- Mac: `brew install wkhtmltopdf`
- Windows: Get from wkhtmltopdf.org

### What We Fixed

Files save better now. All types work right.

Binary files (like DOCX) work now. We fixed a bug there.

PDF making works great. If you don't have the PDF tool, we save HTML instead.

Settings work better. The window size saves. The font size saves too.

The code is cleaner. It fits our plan better. We have 71 tests. They all work!

## First Version - October 19, 2025

This is the first version! It has nice windows. You can see your work as you type.

You can open files. You can save files. It turns Word files into AsciiDoc.

It uses Git to save versions. You can copy from Word. It has dark mode and light mode.

You can make text bigger. It remembers your picks. It works on all computers.

**What you need:**
- PySide6 to make windows
- asciidoc3 to make HTML
- pypandoc to change files
- git and pandoc on your computer

**What doesn't work yet:**
- You can only open one file
- No colored text in the editor
- No find button
- Basic undo only
- Can't save as PDF yet
- Git must be set up first

---

**Reading**: Grade 5.0
