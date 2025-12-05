# AsciiDoc Artisan

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/Qt-PySide6-41CD52.svg)](https://doc.qt.io/qtforpython/)
[![Release](https://img.shields.io/github/v/release/webbwr/AsciiDoctorArtisan)](https://github.com/webbwr/AsciiDoctorArtisan/releases)

**v2.1.0** | Desktop AsciiDoc editor with live preview

## Features

- Live preview (GPU: 10-50x faster)
- Auto-complete & syntax checking
- Templates (6 built-in + custom)
- Find/Replace, Spell Check
- Git & GitHub integration
- AI chat (Ollama, local)
- Import: DOCX, PDF, Markdown, HTML

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

**Full Guide:** [INSTALL.md](INSTALL.md) - Windows 11, WSL2, macOS, Linux

## Run

```bash
make run              # Recommended
python3 -OO src/main.py  # Fast mode
```

## Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+N/O/S | New/Open/Save |
| Ctrl+F/H | Find/Replace |
| F3 | Find next |
| F7 | Spell check |
| F11 | Dark mode |
| Ctrl+G | Quick commit |

## Optional

- **Git** - Version control
- **GitHub CLI** - `sudo apt install gh`
- **Ollama** - AI chat (ollama.com)

## Docs

- [User Guide](docs/user/user-guide.md)
- [FAQ](FAQ.md)
- [Troubleshooting](docs/user/troubleshooting.md)
- [GitHub Integration](docs/user/github-integration.md)

## Settings

- Linux: `~/.config/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`
- Mac: `~/Library/Application Support/AsciiDocArtisan/`

## License

MIT License - Free to use

---

*v2.1.0 | 46,457 lines | 5,139 tests | [CHANGELOG](CHANGELOG.md)*
