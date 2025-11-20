# Frequently Asked Questions (FAQ)

Common questions about AsciiDoc Artisan.

**Version:** 2.0.6+ | **Last Updated:** November 20, 2025

---

## General Questions

### What is AsciiDoc Artisan?

A smart desktop app for writing AsciiDoc documents. It shows what your work looks like as you type. It has helpful features like auto-complete and spell check.

### Is it free to use?

Yes! It is free and open source (MIT License). You can use it for anything.

### What computers does it work on?

- Linux (Ubuntu, Debian, Fedora, Arch)
- macOS (10.15+)
- Windows (10/11)

Works on any computer that runs Python 3.11+.

### Do I need to know AsciiDoc?

No! The app helps you learn. It has:
- Auto-complete (suggests what to type)
- Syntax checking (finds mistakes)
- Templates (ready-made documents)
- Built-in help

### How is this different from a text editor?

**AsciiDoc Artisan:**
- Shows preview as you type
- Finds errors automatically
- Has AsciiDoc tools built-in
- One-click export to PDF/Word

**Regular editor:**
- Just shows plain text
- No preview
- Need separate tools
- More steps to export

---

## Features

### What file types can I open?

**Open:**
- AsciiDoc (.adoc)
- Markdown (.md)
- Word documents (.docx)
- PDF files (.pdf)
- HTML files (.html)

All convert to AsciiDoc automatically.

### What file types can I export to?

**Export:**
- HTML (.html)
- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- AsciiDoc (.adoc)

One click. No extra tools needed.

### Does it work with Git?

Yes! Built-in Git support:
- Commit changes
- Push to GitHub
- Pull updates
- See status
- Quick commit (Ctrl+G)

Need Git installed first.

### Can I use AI to help me write?

Yes! Two AI options:

**Ollama (Local AI):**
- Runs on your computer
- Private (no internet)
- Free forever
- Need to install Ollama first

**Claude AI (Cloud):**
- Very smart AI
- Needs API key
- Costs money (pay Anthropic)
- Best quality responses

### Does it check spelling?

Yes! Turn on with F7:
- Finds typos as you type
- Shows red lines under errors
- Suggests fixes
- Add custom words
- Multiple languages

### Does it have auto-complete?

Yes! Press Ctrl+Space:
- Suggests headings (=, ==, ===)
- Suggests formatting (*bold*, _italic_)
- Suggests lists (*, ., -)
- Fuzzy matching (finds close matches)
- Works as you type

### Can I use templates?

Yes! Built-in templates:
- Technical Report
- User Manual
- Meeting Notes
- Blog Post
- README
- Presentation

Make your own templates too!

---

## Performance

### Why is GPU acceleration recommended?

**With GPU (graphics card):**
- 10-50x faster preview
- Uses 70-90% less CPU
- Smoother scrolling
- Handles big documents

**Without GPU:**
- Still works fine!
- Uses CPU instead
- A bit slower
- Good for normal documents

### How fast is startup?

Normal: 0.5-1.0 seconds

First time might be slower (creates settings, finds GPU).

### Can it handle large documents?

Yes! Tested with:
- 10,000+ lines
- 100+ images
- Complex tables
- Long books

GPU helps with big documents.

### Why does preview update slowly?

**Normal delay:** 500ms (half second)

This is on purpose! Waits for you to stop typing. You can change this in settings.

---

## Installation & Setup

### What do I need to install?

**Required:**
- Python 3.11 or newer
- Pandoc (for file conversion)
- wkhtmltopdf (for PDF export)

**Optional:**
- Git (for version control)
- Ollama (for local AI)
- GPU drivers (for speed)

### How do I install it?

**Easy way:**
```bash
./install-asciidoc-artisan.sh  # Linux/Mac
```

**Manual way:**
```bash
pip install -r requirements.txt
```

See README.md for full instructions.

### Do I need a GPU?

No! GPU is optional:
- **With GPU:** Faster (recommended)
- **Without GPU:** Still works great

App picks best option automatically.

### What if I don't have Pandoc?

**Install Pandoc:**
- Linux: `sudo apt install pandoc`
- Mac: `brew install pandoc`
- Windows: Download from pandoc.org

**Without Pandoc:**
- Can't convert file types
- Can't export Word/PDF
- Everything else works

---

## Usage

### How do I create a new document?

1. Click File → New
2. Or press Ctrl+N
3. Or use template (File → New from Template)

### How do I save my work?

- Auto-save (optional): Saves automatically
- Manual save: Ctrl+S
- Save as: Ctrl+Shift+S

### How do I export to PDF?

1. Click File → Export → PDF
2. Pick location
3. Click Save
4. Done!

Or use File → Save As and choose .pdf

### How do I use auto-complete?

1. Start typing (example: `=`)
2. Press Ctrl+Space
3. Pick from list
4. Press Enter

Or just keep typing, it appears automatically!

### How do I fix spelling errors?

1. Turn on spell check (F7)
2. Right-click red underlined word
3. Pick correct spelling
4. Or add to dictionary

### How do I find and replace text?

1. Press Ctrl+F to find
2. Press Ctrl+H to replace
3. Type search word
4. Type replacement
5. Click Replace or Replace All

### How do I commit to Git?

**Quick way:**
1. Press Ctrl+G
2. Type commit message
3. Press Enter

**Full way:**
1. Click Git → Status (Ctrl+Shift+G)
2. Pick files to commit
3. Type message
4. Click Commit

---

## Troubleshooting

### It won't start. What do I do?

1. Check Python version: `python3 --version`
2. Check dependencies installed
3. Run from terminal to see errors
4. See troubleshooting.md guide

### Preview not showing. Why?

1. Wait 500ms (normal delay)
2. Check valid AsciiDoc syntax
3. Try restarting app
4. Check asciidoc3 installed

### Export to PDF fails. Why?

1. Is wkhtmltopdf installed?
2. Check: `wkhtmltopdf --version`
3. Install if missing
4. Try again

### Git menu grayed out. Why?

1. Not in Git folder
2. Run: `git init`
3. Or open different folder

### Ollama AI not working. Why?

1. Is Ollama installed?
2. Is it running? `ollama serve`
3. Model downloaded? `ollama pull llama2`
4. Enable in Settings → AI

See **troubleshooting.md** for more help!

---

## Customization

### Can I change the theme?

Yes! Dark mode:
- Press F11
- Or View → Toggle Dark Mode

More themes coming soon!

### Can I change font size?

Yes!
- Bigger: Ctrl++
- Smaller: Ctrl+-
- Or Settings → Editor → Font

### Can I change keyboard shortcuts?

Not yet. Coming in future version.

Default shortcuts match common apps (VS Code, etc.).

### Can I add custom templates?

Yes! See docs/user/user-guide.md for how to make templates.

### Can I change preview style?

Not directly. Preview shows standard AsciiDoc style.

You can edit the HTML after export.

---

## Comparison

### How is this different from VS Code + AsciiDoc?

**AsciiDoc Artisan:**
- Easy to use
- One app, all tools
- Fast preview
- No setup needed

**VS Code:**
- More powerful
- Many languages
- More plugins
- More complex

**Use AsciiDoc Artisan if:** You mainly write AsciiDoc

**Use VS Code if:** You code in many languages

### How is this different from Asciidoctor.org tools?

**AsciiDoc Artisan:**
- Desktop app with GUI
- Real-time preview
- All-in-one tool

**Asciidoctor:**
- Command-line tools
- More control
- More features
- Harder to use

**Both work together!** You can use both.

### Should I use this or Markdown?

**AsciiDoc is better for:**
- Books
- Technical docs
- Complex documents
- Multiple outputs

**Markdown is better for:**
- README files
- GitHub pages
- Simple notes
- Quick docs

**Good news:** This app opens Markdown files too!

### Can I still use my old AsciiDoc tools?

Yes! This app makes .adoc files. Use them anywhere:
- asciidoctor command
- GitHub (renders .adoc)
- Other tools
- Web converters

Standard AsciiDoc format. Not locked in.

---

## Advanced Questions

### Does it support includes?

Yes! Use standard AsciiDoc includes:
```
include::other_file.adoc[]
```

### Does it support math equations?

Yes! Use AsciiMath or LaTeX:
```
stem:[x = (-b +- sqrt(b^2-4ac))/(2a)]
```

### Can I use it offline?

Yes! Works fully offline:
- Edit documents
- Preview
- Export
- Save

Only need internet for:
- Claude AI (cloud)
- GitHub operations
- Updates (optional)

### Is my data private?

Yes!
- All files stay on your computer
- No telemetry
- No tracking
- Open source (can verify)

**Exception:** Claude API sends text to Anthropic (if you use it)

### Can I extend it with plugins?

Not yet. Plugin system planned for v3.0.0 (future).

### Can multiple people edit same file?

No. Not designed for real-time collaboration.

Use Git for team work:
- Each person makes changes
- Commit to Git
- Pull/merge changes

Real-time collab planned for v3.0.0 (future).

---

## Getting More Help

### Where is full documentation?

- **User Guide:** docs/user/user-guide.md
- **Troubleshooting:** docs/user/troubleshooting.md
- **Developer Guide:** docs/developer/

### How do I report bugs?

GitHub Issues: https://github.com/webbwr/AsciiDoctorArtisan/issues

**Include:**
- What you did
- What happened
- What you expected
- Error message
- Your version

### How do I request features?

Same place as bugs (GitHub Issues)!

Tell us:
- What feature you want
- Why you need it
- How it should work

### Can I contribute?

Yes! We welcome contributions:
- Bug fixes
- New features
- Documentation
- Testing
- Translations

See docs/developer/contributing.md

### Where can I get help from humans?

- GitHub Issues (technical help)
- GitHub Discussions (questions)
- Community forums (coming soon)

---

## About the Project

### Who made this?

Open source project. Many contributors. See GitHub for full list.

### What license is it?

MIT License. Free to use. Free to modify. Free to share.

### Where is the source code?

GitHub: https://github.com/webbwr/AsciiDoctorArtisan

### How can I support the project?

- Use it and tell others
- Report bugs
- Contribute code
- Write documentation
- Give feedback
- Star on GitHub ⭐

### What's the roadmap?

See ROADMAP.md for future plans.

**Coming soon:**
- More export formats
- Better templates
- More themes
- Performance improvements

**v3.0.0 (future):**
- Plugin system
- Language Server Protocol (LSP)
- Real-time collaboration
- Cloud sync

---

## Quick Tips

### Best practices for writing

1. Use templates to start
2. Enable auto-complete
3. Turn on spell check
4. Save often (or use auto-save)
5. Preview as you write
6. Use Git for versions

### Best performance

1. Use GPU if you have one
2. Keep documents under 5,000 lines
3. Use includes for big projects
4. Close preview for huge docs
5. Use SSD not HDD

### Learning AsciiDoc

1. Start with template
2. Use auto-complete to learn syntax
3. Check preview often
4. Read AsciiDoc user manual online
5. Practice with examples

---

**Didn't find your question?**
- Check troubleshooting.md
- Check user-guide.md
- Ask on GitHub Issues

**Remember:** Most questions are answered by:
- Reading README.md first
- Checking the docs/user/ folder
- Trying the built-in help

---

**Pro Tip:** Press F1 in the app for quick help! (coming soon)
