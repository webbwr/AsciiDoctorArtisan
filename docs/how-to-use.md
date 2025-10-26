# How to Use

**Reading Level**: Grade 5.0

Learn to use AsciiDoc Artisan.

## Quick Links

1. [Get Started](#get-started)
2. [Write Docs](#write-docs)
3. [Save and Open](#save-and-open)
4. [Use Git](#use-git)
5. [Change Types](#change-types)
6. [Settings](#settings)
7. [Tips](#tips)

## Get Started

### What Is This

It helps you write docs.

**What it does:**
- Shows doc as you type
- Saves to Git
- Opens Word and PDF
- Saves to Word and PDF
- Changes file types

### First Time

1. Install (see how-to-install.md)
2. Start - Click start file
3. Two sides:
   - Left: Type here
   - Right: See result

## Write Docs

### Type Words

Just type. Words show on left.

### Make Text Bold

**Bold** - Use stars:
```
*This is bold*
```

**Italic** - Use lines:
```
_This is italic_
```

**Big Titles** - Use equal signs:
```
= Big Title
== Medium
=== Small
```

### Make Lists

**Simple list** - Use stars:
```
* First
* Second
* Third
```

**Number list** - Use numbers:
```
1. First
2. Second
3. Third
```

### Add Links

**Web link** - Type address:
```
https://www.example.com
```

**Named link** - Add name:
```
https://www.example.com[Click Here]
```

## Save and Open

### Save Your Work

Two ways to save:

**Save** (Ctrl+S):
- Saves same file
- Use this most

**Save As** (Ctrl+Shift+S):
- Makes new file
- Pick new name

### Open Files

1. Click `File`
2. Click `Open` (or Ctrl+O)
3. Find file
4. Click Open

### Types You Can Open

- **`.adoc`**: AsciiDoc
- **`.md`**: Markdown (turns to AsciiDoc)
- **`.docx`**: Word (turns to AsciiDoc)
- **`.html`**: Web (turns to AsciiDoc)
- **`.pdf`**: PDF (gets text)

All open fast.

## Use Git

Git saves work online.

### What You Need

File must be in Git folder.

**To check:**
1. Open terminal
2. Go to folder
3. Type: `git status`

If error, not in Git yet.

### Git Actions

**Pull** (Get new):
1. Click `Git`
2. Click `Pull`
3. File updates

**Commit** (Save):
1. Save first (Ctrl+S)
2. Click `Git`
3. Click `Commit`
4. Type what changed
5. Click OK

**Push** (Send):
1. Click `Git`
2. Click `Push`
3. Goes online

### Commit Notes

Good notes are short:
- ✓ "Fix spelling"
- ✓ "Add cats"
- ✗ "Changes"
- ✗ "asdf"

## Change Types

### Open Types

Opens many types.

**From Word**:
1. `File` → `Open`
2. Pick .docx
3. Opens

**From Markdown**:
1. `File` → `Open`
2. Pick .md
3. Opens

**From HTML**:
1. `File` → `Open`
2. Pick .html
3. Opens

**From PDF**:
1. `File` → `Open`
2. Pick .pdf
3. Gets text

All turn to AsciiDoc.

### Save to Types

Save to any type.

1. Click `File`
2. Click `Save As`
3. Pick type:
   - AsciiDoc
   - Markdown
   - Word
   - HTML
   - PDF
4. Type name
5. Click Save

Changes for you.

## Settings

### Dark Mode

Switch colors:
- Press Ctrl+D
- Or `View` → `Dark Mode`

### Text Size

Change text size:
- **Big**: Ctrl and +
- **Small**: Ctrl and -
- **Normal**: Ctrl and 0

### Auto-Save

Saves every few minutes. Press Ctrl+S any time.

## Tips

### Preview

Right side shows doc:
- **Updates fast**: Wait one second
- **Scrolls with you**: Follows you
- **Shows all**: Bold, lists, all

### Shortcuts

Work fast:

| Press | Does |
|-------|------|
| Ctrl+N | New |
| Ctrl+O | Open |
| Ctrl+S | Save |
| Ctrl+F | Find |
| Ctrl+G | Go to line |
| Ctrl+D | Dark |
| Ctrl++ | Bigger |
| Ctrl+- | Smaller |
| Ctrl+Q | Close |

### Find Words

Look for words:
1. Press Ctrl+F
2. Type word
3. Press Enter
4. Press Enter for next

### Go to Line

Jump to line:
1. Press Ctrl+G
2. Type number
3. Press Enter

### Status Bar

Bottom shows:
- Line
- File
- If changed
- Git

## Questions

### How to Make Table

Use pipes:
```
|===
| Name | Age

| Alice | 25
| Bob | 30
|===
```

### How to Add Pictures

Type:
```
image::pic.png[Picture]
```
Pic must be in same folder.

### How to Add Code

Put in box:
```
[source,python]
----
print("Hello")
----
```

### If Preview Broke

Wait after you type. If still broke:
1. Check `asciidoc3` is on
2. Click preview
3. Save and reopen

### How to Print

Two ways:
1. Save PDF, print it
2. Save HTML, print in browser

## More Help

- how-to-install.md for setup
- how-to-contribute.md to help
- GitHub for questions

## Remember

- **Save often**: Press Ctrl+S
- **Use Git**: Save online
- **Check preview**: See right side
- **Use shortcuts**: Work fast

Happy writing!

---
**Grade 5.0 | Updated: 2025**
