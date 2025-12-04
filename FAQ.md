# FAQ

## General

**What is AsciiDoc Artisan?**
Desktop AsciiDoc editor with live preview, auto-complete, spell check, Git integration, and AI chat.

**Is it free?**
Yes, MIT License.

**What platforms?**
Linux, macOS, Windows.

## Installation

**Requirements:** Python 3.11+, Pandoc, wkhtmltopdf

```bash
# Linux/Mac
./install-asciidoc-artisan.sh

# Windows
.\Install-AsciiDocArtisan.ps1
```

**GPU needed?**
No, but gives 10-50x faster preview.

## Usage

**Start:** `make run` or `python3 src/main.py`

**Shortcuts:**

| Key | Action |
|-----|--------|
| Ctrl+N/O/S | New/Open/Save |
| Ctrl+F/H | Find/Replace |
| F3 | Find next |
| F7 | Spell check |
| F11 | Dark mode |
| Ctrl+G | Quick commit |

**Export:** File → Export → PDF/Word/HTML/Markdown

## Features

**Auto-complete:** Ctrl+Space triggers suggestions

**Spell check:** F7 toggle, right-click for fixes

**Git:** Ctrl+G quick commit, Ctrl+Shift+G status dialog

**AI chat:** Install Ollama, then Tools → AI Status

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Won't start | Check `python3 --version` ≥3.11 |
| No pypandoc | `pip install pypandoc` |
| No Pandoc | `sudo apt install pandoc` |
| PDF fails | `sudo apt install wkhtmltopdf` |
| Slow preview | Install GPU drivers |
| Git grayed | Initialize repo: `git init` |

## Performance

- Startup: 0.586s
- Preview: <50ms (GPU)
- Memory: ~150-220 MB

## Security

- Data stays local
- Atomic file saves
- API keys in OS keyring
- Telemetry opt-in only

## Development

```bash
make test    # Run tests
make format  # Format code
make lint    # Check types
```

---

*[Full docs: docs/user/user-guide.md]*
