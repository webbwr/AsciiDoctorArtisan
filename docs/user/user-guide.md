# User Guide

**v2.1.0** | AsciiDoc editor with live preview

---

## Quick Start

1. Run: `make run`
2. Type in left pane
3. See preview in right pane

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save file |
| Ctrl+Shift+S | Save as |
| Ctrl+F | Find |
| Ctrl+H | Replace |
| Ctrl+G | Quick commit |
| Ctrl+Space | Auto-complete |
| F3 | Find next |
| Shift+F3 | Find previous |
| F7 | Spell check |
| F8 | Syntax check |
| F11 | Toggle dark mode |
| Escape | Close dialogs |

---

## Writing AsciiDoc

### Basic Syntax

```asciidoc
= Document Title
== Section
=== Subsection

*bold* _italic_ `code`

* Bullet item
** Nested item

. Numbered item
.. Nested numbered

https://example.com[Link text]
image::photo.png[Alt text]
```

### Tables

```asciidoc
|===
| Header 1 | Header 2

| Cell 1   | Cell 2
| Cell 3   | Cell 4
|===
```

### Code Blocks

```asciidoc
[source,python]
----
def hello():
    print("Hello")
----
```

---

## Auto-Complete

- Triggers as you type
- Press **Ctrl+Space** for manual trigger
- Fuzzy matching: "hdr" finds "heading"
- Response time: <50ms

---

## Syntax Checking

- Press **F8** to toggle
- Red underline = error
- Yellow underline = warning
- Click error to jump to line
- Lightbulb shows quick fixes

---

## Spell Check

- Press **F7** to check document
- Right-click word for suggestions
- Add words to custom dictionary

### Languages

| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| fr | French |
| de | German |

---

## Templates

**File → New from Template**

| Template | Use Case |
|----------|----------|
| Technical Report | Formal documentation |
| User Manual | Product guides |
| Meeting Notes | Meeting records |
| Blog Post | Articles |
| README | Project docs |
| Presentation | Slides |

Custom templates: Use `{{variable}}` placeholders.

---

## File Operations

| Format | Open | Save |
|--------|------|------|
| AsciiDoc (.adoc) | Yes | Yes |
| Markdown (.md) | Yes | Yes |
| Word (.docx) | Yes | Yes |
| PDF (.pdf) | Yes | Yes |
| HTML (.html) | Yes | Yes |

---

## Git Integration

| Action | Menu | Shortcut |
|--------|------|----------|
| Commit | Git → Commit | Ctrl+Shift+C |
| Push | Git → Push | Ctrl+Shift+U |
| Pull | Git → Pull | - |
| Status | Git → Status | - |
| Quick Commit | Git → Quick | Ctrl+G |

---

## AI Chat

1. Open chat panel (View → AI Chat)
2. Select model from dropdown
3. Type question
4. Press Enter or click Send

### Chat Modes

| Mode | Description |
|------|-------------|
| Document | Include current document |
| Syntax | AsciiDoc help |
| General | General questions |
| Editing | Writing assistance |

---

## Settings

| Platform | Location |
|----------|----------|
| Linux | `~/.config/AsciiDocArtisan/` |
| macOS | `~/Library/Application Support/AsciiDocArtisan/` |
| Windows | `%APPDATA%/AsciiDocArtisan/` |

---

## Performance Tips

1. Use GPU acceleration (auto-detected)
2. Close unused panels
3. Enable incremental preview
4. Use smaller documents for fastest preview

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Preview blank | Install asciidoc3 |
| PDF export fails | Install wkhtmltopdf |
| Slow preview | Check GPU drivers |
| Spell check fails | Install pyspellchecker |

---

*v2.1.0 | [Full Docs](../../README.md)*
