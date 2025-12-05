# AsciiDoc Artisan

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/Qt-PySide6-41CD52.svg)](https://doc.qt.io/qtforpython/)
[![Tests](https://img.shields.io/badge/Tests-5,139_passing-success.svg)](tests/)
[![Type Check](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)

**Desktop AsciiDoc editor with live preview**

| Metric | Value |
|--------|-------|
| Version | 2.1.0 |
| Code | 45,900 lines / 180 files |
| Tests | 5,139 (95% coverage) |
| Startup | 0.27s |

---

## Features

| Feature | Details |
|---------|---------|
| Live Preview | GPU accelerated (10-50x faster) |
| Auto-Complete | Fuzzy matching, <50ms |
| Syntax Check | Real-time, quick fixes |
| Templates | 6 built-in + custom |
| Find/Replace | Regex support |
| Spell Check | 4 languages |
| Git | Commit, push, pull |
| GitHub CLI | PRs, issues |
| AI Chat | Ollama (local) |
| Import | DOCX, PDF, Markdown, HTML |
| Export | HTML, PDF, DOCX, Markdown |

---

## Install

**Requirements:** Python 3.11+, Pandoc, wkhtmltopdf

```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Linux/Mac/WSL2
./install-asciidoc-artisan.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File install-asciidoc-artisan.ps1
```

**Manual:** `pip install -r requirements-prod.txt`

**Full Guide:** [INSTALL.md](INSTALL.md)

---

## Run

```bash
make run                 # Recommended
python3 -OO src/main.py  # Fast mode
```

---

## Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save file |
| Ctrl+F | Find |
| Ctrl+H | Replace |
| Ctrl+Space | Auto-complete |
| F3 | Find next |
| F7 | Spell check |
| F8 | Syntax check |
| F11 | Dark mode |
| Ctrl+G | Quick commit |

---

## Optional Tools

| Tool | Purpose | Install |
|------|---------|---------|
| Git | Version control | Pre-installed |
| GitHub CLI | PRs, issues | `sudo apt install gh` |
| Ollama | AI chat | ollama.com |

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [User Guide](docs/user/user-guide.md) | How to use |
| [INSTALL.md](INSTALL.md) | Setup guide |
| [FAQ](FAQ.md) | Common questions |
| [Troubleshooting](docs/user/troubleshooting.md) | Fix issues |
| [GitHub Integration](docs/user/github-integration.md) | Git workflow |

---

## Settings

**Format:** [TOON](https://github.com/toon-format/toon) (Token-Oriented Object Notation)
- 30-60% smaller than JSON
- Human-readable
- Auto-migrates from JSON

| Platform | Path |
|----------|------|
| Linux | `~/.config/AsciiDocArtisan/AsciiDocArtisan.toon` |
| Windows | `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.toon` |
| macOS | `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.toon` |

---

## License

MIT License. Free to use and modify.

---

*v2.1.0 | 45,900 lines | 5,139 tests | [CHANGELOG](CHANGELOG.md)*
