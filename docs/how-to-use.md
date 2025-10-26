# How to Use AsciiDoc Artisan

**Reading Level**: Grade 5.1 (Elementary)

A simple guide to help you use AsciiDoc Artisan.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Writing Documents](#writing-documents)
3. [Saving and Opening Files](#saving-and-opening-files)
4. [Using Git](#using-git)
5. [Changing Document Types](#changing-document-types)
6. [Settings and Preferences](#settings-and-preferences)
7. [Tips and Tricks](#tips-and-tricks)

## Getting Started

### What is AsciiDoc Artisan?

AsciiDoc Artisan is a program that helps you write documents using AsciiDoc. Think of it like a special word processor that:
- Shows you what your document looks like while you write
- Helps you save your work online with Git
- Can open many file types (Word, PDF, Markdown, HTML)
- Can save to many file types (Word, PDF, Markdown, HTML)
- Changes file types for you in the background

### First Time Setup

1. **Install the program** (see [how-to-install.md](how-to-install.md) for steps)
2. **Start the program** by double-clicking the launch file
3. The program opens with two windows:
   - Left side: Where you type
   - Right side: Shows what it looks like

## Writing Documents

### Basic Writing

Just start typing! Everything you type appears on the left side.

### Making Text Look Different

**Bold Text**: Put stars around words
```
*This text is bold*
```

**Italic Text**: Put underscores around words
```
_This text is italic_
```

**Big Headings**: Use equal signs
```
= Big Title
== Medium Heading
=== Small Heading
```

### Making Lists

**Simple List**: Start lines with a star
```
* First thing
* Second thing
* Third thing
```

**Numbered List**: Start lines with a number and dot
```
1. First step
2. Second step
3. Third step
```

### Adding Links

**Web Links**: Just type the address
```
https://www.example.com
```

**Named Links**: Put the address and name together
```
https://www.example.com[Click Here]
```

## Saving and Opening Files

### Saving Your Work

There are two ways to save:

**Save** (Ctrl+S):
- Saves to the same file
- Use this most of the time

**Save As** (Ctrl+Shift+S):
- Saves to a new file
- Lets you pick a new name and place

### Opening Files

1. Click `File` menu
2. Click `Open` (or press Ctrl+O)
3. Find your file
4. Click the Open button

### File Types You Can Open

- **`.adoc` files**: Regular AsciiDoc files
- **`.md` files**: Markdown files (changes to AsciiDoc)
- **`.docx` files**: Word documents (changes to AsciiDoc)
- **`.html` files**: Web pages (changes to AsciiDoc)
- **`.pdf` files**: PDF files (pulls out the text)

All files open right away. No questions asked.

## Using Git

Git helps you save your work online and keep track of changes.

### What You Need

Your file must be in a Git folder. To check:
1. Open terminal/command prompt
2. Go to your file's folder
3. Type: `git status`

If you see an error, you're not in a Git folder yet.

### Git Actions

**Pull** (Get newest version):
1. Click `Git` menu
2. Click `Pull`
3. Your file updates with any changes from online

**Commit** (Save your changes):
1. Save your file first (Ctrl+S)
2. Click `Git` menu
3. Click `Commit`
4. Type a message about what you changed
5. Click OK

**Push** (Send to online):
1. Click `Git` menu
2. Click `Push`
3. Your changes go to GitHub or your Git server

### Commit Messages

Good commit messages are short and clear:
- ✓ "Fix spelling in chapter 2"
- ✓ "Add new section about cats"
- ✗ "Made changes"
- ✗ "asdf"

## Changing Document Types

### Opening Different Types

The program can open many file types:

**From Word (.docx)**:
1. Click `File` → `Open`
2. Pick a .docx file
3. Opens as AsciiDoc right away

**From Markdown (.md)**:
1. Click `File` → `Open`
2. Pick a .md file
3. Opens as AsciiDoc right away

**From HTML (.html)**:
1. Click `File` → `Open`
2. Pick an .html file
3. Opens as AsciiDoc right away

**From PDF (.pdf)**:
1. Click `File` → `Open`
2. Pick a .pdf file
3. Pulls out the text

All files change to AsciiDoc. No questions asked.

### Saving to Different Types

You can save to any type:

1. Click `File` menu
2. Click `Save As`
3. Pick what type you want:
   - AsciiDoc (.adoc)
   - Markdown (.md)
   - Word (.docx)
   - Web page (.html)
   - PDF (.pdf)
4. Type a file name
5. Click Save

The program changes it for you. No questions asked.

## Settings and Preferences

### Dark Mode

Switch between light and dark colors:
- Press Ctrl+D
- Or click `View` → `Toggle Dark Mode`

### Text Size

Make text bigger or smaller:
- **Bigger**: Press Ctrl and +
- **Smaller**: Press Ctrl and -
- **Normal size**: Press Ctrl and 0

### Auto-Save

The program saves your work automatically every few minutes. You can still save anytime with Ctrl+S.

## Tips and Tricks

### Preview Window

The right side shows what your document looks like:
- **Updates as you type**: Wait a second after you stop typing
- **Scrolls with you**: The preview follows where you're writing
- **Shows all formatting**: Bold, lists, headings, everything

### Keyboard Shortcuts

Learn these to work faster:

| Press This | To Do This |
|-----------|-----------|
| Ctrl+N | Make new file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+F | Find words |
| Ctrl+G | Jump to line number |
| Ctrl+D | Dark mode on/off |
| Ctrl++ | Bigger text |
| Ctrl+- | Smaller text |
| Ctrl+Q | Close program |

### Find and Replace

Look for specific words:
1. Press Ctrl+F
2. Type the word you want to find
3. Press Enter to find it
4. Press Enter again to find the next one

### Go to Line

Jump to a specific line:
1. Press Ctrl+G
2. Type the line number
3. Press Enter

### The Status Bar

At the bottom of the screen, you see:
- Current line number
- File name
- Whether file has been changed since last save
- Git status

## Common Questions

### How do I make a table?

Use pipes and lines:
```
|===
| Name | Age | City

| Alice | 25 | Boston
| Bob | 30 | Seattle
|===
```

### How do I add pictures?

Type this:
```
image::picture.png[Picture description]
```
The picture file must be in the same folder as your document.

### How do I add code?

Put code in a special box:
```
[source,python]
----
print("Hello World")
----
```

### What if the preview doesn't update?

The preview updates after you stop typing for a moment. If it still doesn't work:
1. Make sure `asciidoc3` is installed
2. Try clicking in the preview window
3. Save your file and reopen it

### Can I print my document?

Yes! Two ways:
1. Export to PDF, then print the PDF
2. Export to HTML, open in browser, then print

## Need More Help?

- Check [how-to-install.md](how-to-install.md) for setup problems
- Check [how-to-contribute.md](how-to-contribute.md) if you want to help
- Look for issues on GitHub
- Create a new issue to ask questions

## Remember

- **Save often**: Press Ctrl+S after making changes
- **Commit regularly**: Save to Git when you finish a section
- **Preview shows all**: Use the right side to check your formatting
- **Shortcuts save time**: Learn the keyboard shortcuts

Happy writing!

---
**Document Info**: Reading level Grade 5.1 | Last updated: 2025
