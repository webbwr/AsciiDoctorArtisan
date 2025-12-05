# User Guide

**v2.1.0** | AsciiDoc editor with live preview

---

## Quick Start

1. Install: `pip install -r requirements.txt`
2. Run: `make run` or `python3 src/main.py`
3. Type left → See preview right

---

## Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+N/O/S | New / Open / Save |
| Ctrl+F/H | Find / Replace |
| F3 | Find next |
| F7 | Spell check |
| F8 | Syntax check |
| F11 | Dark mode |
| Ctrl+G | Quick commit |
| Ctrl+Space | Auto-complete |

---

## Writing AsciiDoc

```asciidoc
= Title
== Section
=== Subsection

*bold* _italic_ `code`

* Bullet list
. Numbered list

https://example.com[Link text]
image::photo.png[Alt text]

|===
| Header 1 | Header 2
| Cell 1   | Cell 2
|===
```

---

## Auto-Complete

- Triggers automatically as you type
- Press **Ctrl+Space** for manual trigger
- Fuzzy matching: type "hdr" → finds "heading"

---

## Syntax Checking

- Press **F8** to toggle
- Red = errors, Yellow = warnings
- Click error to jump to line

---

## Templates

**File → New from Template**

Built-in: Technical Report, User Manual, Meeting Notes, Blog Post, README, Presentation

Custom: Use `{{variable}}` placeholders

---

## File Operations

| Format | Open | Save |
|--------|------|------|
| AsciiDoc (.adoc) | ✅ | ✅ |
| Markdown (.md) | ✅ | ✅ |
| Word (.docx) | ✅ | ✅ |
| PDF (.pdf) | ✅ | ✅ |
| HTML (.html) | ✅ | ✅ |

---

## Git

| Action | How |
|--------|-----|
| Commit | Git → Commit (Ctrl+Shift+C) |
| Push | Git → Push (Ctrl+Shift+U) |
| Pull | Git → Pull |
| Status | Git → Status Dialog |

---

## Settings

| Location | Path |
|----------|------|
| Linux | `~/.config/AsciiDocArtisan/` |
| Mac | `~/Library/Application Support/AsciiDocArtisan/` |
| Windows | `%APPDATA%/AsciiDocArtisan/` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Preview blank | Install asciidoc3: `pip install asciidoc3` |
| PDF export fails | Install wkhtmltopdf |
| Pandoc errors | Install pandoc |

---

*v2.1.0 | Dec 5, 2025*
