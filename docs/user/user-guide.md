# How to Use

**Reading Level**: Grade 5.0

Learn to use AsciiDoc Artisan.

## Quick Links

1. [Get Started](#get-started)
2. [Write Docs](#write-docs)
3. [Auto-Complete](#auto-complete) ⭐ NEW
4. [Syntax Checking](#syntax-checking) ⭐ NEW
5. [Templates](#templates) ⭐ NEW
6. [Save and Open](#save-and-open)
7. [Find and Replace](#find-and-replace)
8. [Spell Check](#spell-check)
9. [Use Git](#use-git)
10. [GitHub CLI](#github-cli) ⭐ NEW
11. [Change Types](#change-types)
12. [Settings](#settings)
13. [Tips](#tips)

## Get Started

### What Is This

It helps you write docs.

**What it does:**
- Shows doc as you type
- Finds and changes words
- Checks your words
- Saves to Git
- Opens Word and PDF
- Saves to Word and PDF
- Changes file types

### First Time

1. Install (see [../../README.md#install-it](../../README.md#install-it))
2. Start - Click start file
3. Two sides:
   - Left: Type here
   - Right: See result

## Write Docs

### Type Words

Just type. Words show on left.

### Make Text Bold

**Bold** - Use stars
```
*This is bold*
```

**Italic** - Use lines
```
_This is italic*
```

**Big Titles** - Use equal signs
```
= Big Title
== Medium
=== Small
```

### Make Lists

**Simple list** - Use stars
```
* First
* Second
* Third
```

**Number list** - Use numbers
```
1. First
2. Second
3. Third
```

### Add Links

**Web link** - Type address
```
https://www.example.com
```

**Named link** - Add name
```
https://www.example.com[Click Here]
```

## Auto-Complete

**NEW in v2.0!** The app helps you type.

### What It Does

Auto-complete shows what to type next. It knows AsciiDoc rules.

**It helps with:**
- Headings (=, ==, ===)
- Lists (*, ., -)
- Bold and italic (*text*, _text_)
- Links and images
- Tables and blocks

### How to Use

**Auto way:**
1. Start typing
2. List appears by itself
3. Pick what you want
4. Press Enter

**Manual way:**
1. Type something
2. Press Ctrl+Space
3. See all choices
4. Pick one
5. Press Enter

### Examples

**Make a heading:**
1. Type `==`
2. See heading choices
3. Pick "Section Level 2"
4. Press Enter
5. Done!

**Make a list:**
1. Type `*`
2. See list choices
3. Pick "Bullet List"
4. Press Enter
5. Type list item

**Make bold text:**
1. Type `*`
2. Pick "Bold Text"
3. Type your words
4. Type `*` again
5. Done!

### Fuzzy Match

Can't spell? No problem!

Type close words. It finds them.

**Example:**
- Type "hed" → finds "heading"
- Type "tbl" → finds "table"
- Type "img" → finds "image"

### Turn It Off

Don't like auto-complete?

1. Click `Settings`
2. Find "Auto-Complete"
3. Turn it off
4. Click Save

### Speed

Very fast! Works with big docs.

**Speed:**
- 1,000 items: < 50ms
- Updates as you type
- No waiting

## Syntax Checking

**NEW in v2.0!** Finds mistakes as you type.

### What It Does

Checks your AsciiDoc. Shows errors.

**It finds:**
- Wrong headings
- Bad links
- Broken tables
- Missing parts
- Style mistakes

### How It Looks

**Errors show as:**
- Red squiggly lines
- Yellow warning lines
- Error list in panel

See the error? Fix it fast!

### Turn It On

Press F8 key. Or use menu:

1. Click `Tools`
2. Click `Syntax Check`
3. Now it checks

Press F8 again to turn off.

### See All Errors

1. Press F8
2. Error list opens
3. See all mistakes
4. Click one to jump there

### Fix Errors

**Two ways:**

**Way 1 - Jump to error:**
1. Press F8
2. Click error in list
3. Goes to that line
4. Fix it

**Way 2 - Quick fix:**
1. Click error
2. See suggestions
3. Pick one
4. Done!

### Error Colors

**Red** - Must fix:
- Broken syntax
- Missing parts
- Bad format

**Yellow** - Should fix:
- Style issues
- Best practice
- Warnings

**Green** - Good:
- No errors
- All correct

### Speed

Checks fast! No waiting.

**Speed:**
- 1,000 lines: < 100ms
- Checks as you type
- Real-time feedback

### Turn It Off

Don't need checking?

1. Press F8
2. Or click `Tools` → `Syntax Check`
3. Turns off

## Templates

**NEW in v2.0!** Start docs fast with templates.

### What Are Templates

Ready-made docs. Just fill in blanks.

**We have:**
- Technical Report
- User Manual
- Meeting Notes
- Blog Post
- README File
- Presentation

All ready to use!

### Use a Template

**Easy steps:**
1. Click `File`
2. Click `New from Template`
3. Pick template you want
4. Fill in the form
5. Click Create
6. Done! Doc is ready.

### Fill the Form

Templates ask questions.

**Example form:**
- Title: Type doc name
- Author: Type your name
- Date: Pick today
- Company: Type company name

Fill all fields. Click Create.

### What You Get

Full document! Just edit it.

**It has:**
- Correct structure
- Sample text
- Good format
- All parts ready

Change what you want. Keep the rest.

### Built-In Templates

**Technical Report:**
- Title page
- Table of contents
- Introduction
- Sections
- Conclusion
- References

**User Manual:**
- Cover page
- How to use
- Features
- Troubleshooting
- FAQ

**Meeting Notes:**
- Date and time
- Who came
- What we talked about
- Action items
- Next meeting

**Blog Post:**
- Title
- Author
- Date
- Content sections
- Tags

**README:**
- Project name
- What it does
- How to install
- How to use
- License

**Presentation:**
- Slides
- Title slide
- Content slides
- Thank you slide

### Make Your Own

Can make custom templates!

1. Make a doc
2. Use `{{variable}}` for blanks
3. Save as template
4. Use it later

**Example:**
```
= {{title}}
{{author}}
{{date}}

== Introduction

This is about {{topic}}.
```

### Template Speed

Very fast!

**Speed:**
- Loads in < 200ms
- Big templates work
- No waiting

### Tips

**Good ideas:**
- Pick right template
- Fill all fields
- Edit after
- Save your work

## Save and Open

### Save Your Work

Two ways to save.

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

## GitHub CLI

**NEW in v1.6!** Work with GitHub from the app.

### What You Need

**Need these installed:**
1. Git (see above)
2. GitHub CLI (`gh` command)
3. GitHub account

**Install GitHub CLI:**
- Linux: `sudo apt install gh`
- Mac: `brew install gh`
- Windows: Download from cli.github.com

**Login first:**
```
gh auth login
```

Follow the steps. Only do this once.

### What You Can Do

**From the app:**
- Make pull requests
- See pull requests
- Make issues
- See issues
- View repo on GitHub

All from `Git` → `GitHub` menu!

### Make Pull Request

Share your work with the team.

**Steps:**
1. Save and commit first
2. Click `Git` → `GitHub`
3. Click `Create Pull Request`
4. Fill in:
   - Title: What you did
   - Description: Why you did it
5. Click Create
6. Done!

**What happens:**
- Makes PR on GitHub
- Team can see it
- They can comment
- You can merge later

### See Pull Requests

Check what others did.

**Steps:**
1. Click `Git` → `GitHub`
2. Click `List Pull Requests`
3. See all PRs
4. Click one to open on GitHub

### Make Issue

Report a bug or idea.

**Steps:**
1. Click `Git` → `GitHub`
2. Click `Create Issue`
3. Fill in:
   - Title: Short problem
   - Body: Details
   - Labels: Type of issue
4. Click Create
5. Done!

**Good for:**
- Report bugs
- Ask for features
- Get help
- Track work

### See Issues

Check all issues.

**Steps:**
1. Click `Git` → `GitHub`
2. Click `List Issues`
3. See all issues
4. Click one to open

### View Repo

Open repo on GitHub.

**Steps:**
1. Click `Git` → `GitHub`
2. Click `View Repository`
3. Opens in web browser

Quick way to see the project online!

### Tips

**Good ideas:**
- Commit before making PR
- Write clear PR titles
- Add details to issues
- Check existing issues first

### Not Working?

**If GitHub menu is gray:**
1. Check `gh` installed: `gh --version`
2. Check logged in: `gh auth status`
3. Check in Git repo: `git status`

All three must work!

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
| Ctrl+H | Find and replace |
| F3 | Find next |
| Shift+F3 | Find before |
| F7 | Spell check on/off |
| F11 | Dark mode on/off |
| Ctrl++ | Bigger |
| Ctrl+- | Smaller |
| Ctrl+Q | Close |

### Find Words

Look for words:
1. Press Ctrl+F
2. Type word
3. Click Next or press F3
4. Click Previous or press Shift+F3
5. Press Esc to close

### Find and Replace

Change words:
1. Press Ctrl+H
2. Type word to find
3. Type new word
4. Click Replace (one)
5. Click Replace All (all)

### Spell Check

Check words:
1. Press F7 to turn on
2. See red lines
3. Right-click word
4. Pick correct word
5. Or add to list

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
