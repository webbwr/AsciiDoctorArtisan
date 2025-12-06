# AsciiDoc Artisan User Guide

> Version 2.1.0 | Getting Started Guide

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt install pandoc wkhtmltopdf gh

# Run
make run
# or
python3 src/main.py
```

### First Launch

1. **Open a file**: `File → Open` or `Ctrl+O`
2. **Start typing**: Left pane is the editor, right pane shows live preview
3. **Save**: `Ctrl+S` saves as `.adoc`, `File → Export As` for other formats

---

## Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  View  Git  GitHub  Tools  Help          [─][□][×]  │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│   EDITOR PANE                │   PREVIEW PANE                   │
│   (AsciiDoc source)          │   (Live HTML preview)            │
│                              │                                  │
│   = My Document              │   My Document                    │
│   :author: Me                │   ═══════════════                │
│                              │   Author: Me                     │
│   == Introduction            │                                  │
│                              │   Introduction                   │
│   This is a paragraph.       │   ───────────────                │
│                              │   This is a paragraph.           │
│                              │                                  │
├──────────────────────────────┴──────────────────────────────────┤
│ Ln 1, Col 1 | UTF-8 | document.adoc                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Features

### 1. Live Preview

The preview pane updates as you type, showing rendered HTML.

**Keyboard Shortcuts:**
| Action | Shortcut |
|--------|----------|
| Toggle sync scrolling | `View → Sync Scrolling` |
| Maximize editor | `View → Maximize Editor` |
| Maximize preview | `View → Maximize Preview` |
| Zoom in | `Ctrl++` |
| Zoom out | `Ctrl+-` |
| Reset zoom | `View → Reset Zoom` |

### 2. File Operations

| Action | Shortcut | Description |
|--------|----------|-------------|
| New | `Ctrl+N` | Create blank document |
| New from Template | `File → New from Template` | Use predefined templates |
| Open | `Ctrl+O` | Open existing file |
| Save | `Ctrl+S` | Save as AsciiDoc |
| Save As | `Ctrl+Shift+S` | Save with new name |

### 3. Export Formats

`File → Export As` supports:

| Format | Extension | Requirements |
|--------|-----------|--------------|
| AsciiDoc | `.adoc` | Built-in |
| GitHub Markdown | `.md` | Built-in |
| HTML | `.html` | Built-in |
| PDF | `.pdf` | Pandoc + wkhtmltopdf |
| Word | `.docx` | Pandoc |

### 4. Find & Replace

| Action | Shortcut |
|--------|----------|
| Find | `Ctrl+F` |
| Replace | `Ctrl+H` |
| Find Next | `F3` |
| Find Previous | `Shift+F3` |

---

## Git Integration

### Setup Repository

1. `Git → Set Repository`
2. Select folder containing `.git` directory
3. Status bar shows current branch

### Operations

| Action | Shortcut | Description |
|--------|----------|-------------|
| Quick Commit | `Ctrl+G` | Inline commit dialog |
| Full Commit | `Ctrl+Shift+G` | Full commit dialog |
| Pull | `Git → Pull` | Fetch & merge |
| Push | `Git → Push` | Push commits |
| Status | `Git → Git Status` | View changes |

### GitHub CLI Integration

Requires `gh` CLI tool authenticated:

```bash
gh auth login
```

Then access via `GitHub` menu:
- Create Pull Request
- List Pull Requests
- Create Issue
- List Issues
- View Repository

---

## AI Features (Optional)

### Ollama (Local AI)

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.2`
3. `Tools → Ollama AI Settings` → Enable → Select model

### Claude API

1. Get API key from https://console.anthropic.com
2. `Tools → Anthropic AI Settings` → Enter key
3. Select model (claude-sonnet-4, etc.)

### Using AI Chat

1. Toggle chat pane: `Tools → Show/Hide Chat Pane`
2. Type question in chat bar
3. Select context (document, selection, or none)

---

## Spell Check

- Toggle: `F7` or `Tools → Spell Check`
- Misspelled words are underlined in red
- Right-click for suggestions

---

## Templates

### Using Templates

1. `File → New from Template`
2. Browse categories (Article, Report, Book, etc.)
3. Fill in variables (title, author, etc.)
4. Click "Create"

### Recent Templates

Recent templates appear at the top of the template dialog.

---

## Keyboard Reference

### Essential

| Action | Shortcut |
|--------|----------|
| New file | `Ctrl+N` |
| Open | `Ctrl+O` |
| Save | `Ctrl+S` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |
| Find | `Ctrl+F` |
| Replace | `Ctrl+H` |

### Navigation

| Action | Shortcut |
|--------|----------|
| Find next | `F3` |
| Find previous | `Shift+F3` |
| Go to line | `Ctrl+G` |

### View

| Action | Shortcut |
|--------|----------|
| Zoom in | `Ctrl++` |
| Zoom out | `Ctrl+-` |
| Toggle dark mode | `F11` |
| Spell check | `F7` |

### Git

| Action | Shortcut |
|--------|----------|
| Quick commit | `Ctrl+G` |
| Full commit | `Ctrl+Shift+G` |

---

## Configuration

### Settings Location

| Platform | Path |
|----------|------|
| Linux | `~/.config/AsciiDocArtisan/AsciiDocArtisan.toon` |
| macOS | `~/Library/Application Support/AsciiDocArtisan/` |
| Windows | `%APPDATA%\AsciiDocArtisan\` |

### Key Settings

Access via `Tools → Application Settings`:

- **Font**: Editor font family and size
- **Theme**: Light/Dark mode
- **Preview**: Sync scrolling, zoom level
- **AI**: Ollama/Claude configuration
- **Git**: Default repository path

---

## Troubleshooting

### PDF Export Fails

```bash
# Install required tools
sudo apt install pandoc wkhtmltopdf
```

### Preview Not Updating

1. Check `View → Sync Scrolling` is enabled
2. Try `View → Reset Zoom`
3. Restart application

### Git Operations Fail

1. Verify repository is set: `Git → Set Repository`
2. Check Git is installed: `git --version`
3. Ensure you have write permissions

### Spell Check Not Working

1. Ensure hunspell is installed
2. Check language dictionaries exist
3. Toggle spell check off/on with `F7`

---

## AsciiDoc Quick Reference

### Headers

```asciidoc
= Document Title (Level 0)
== Section (Level 1)
=== Subsection (Level 2)
==== Sub-subsection (Level 3)
```

### Text Formatting

```asciidoc
*bold*
_italic_
`monospace`
*_bold italic_*
^superscript^
~subscript~
```

### Lists

```asciidoc
* Unordered item
** Nested item

. Numbered item
.. Nested numbered

Term:: Definition
```

### Links & Images

```asciidoc
https://example.com[Link text]
link:file.pdf[PDF download]

image::photo.jpg[Alt text]
image::diagram.png[Diagram, 300, 200]
```

### Code Blocks

```asciidoc
[source,python]
----
def hello():
    print("Hello World")
----
```

### Tables

```asciidoc
|===
|Header 1 |Header 2

|Cell 1
|Cell 2

|Cell 3
|Cell 4
|===
```

### Admonitions

```asciidoc
NOTE: This is a note.

TIP: This is a tip.

WARNING: This is a warning.

CAUTION: Be careful!

IMPORTANT: Pay attention!
```

---

## Getting Help

- **GitHub Issues**: https://github.com/webbwr/AsciiDoctorArtisan/issues
- **AsciiDoc Syntax**: https://docs.asciidoctor.org/asciidoc/latest/syntax-quick-reference/

---

*AsciiDoc Artisan v2.1.0*
