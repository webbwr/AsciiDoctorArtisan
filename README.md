# AsciiDoc Artisan

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
# Linux/Mac
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
./install-asciidoc-artisan.sh

# Windows
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
.\Install-AsciiDocArtisan.ps1
```

**Manual:** `pip install -r requirements.txt`

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
