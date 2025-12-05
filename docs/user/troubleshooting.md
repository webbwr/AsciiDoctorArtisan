# Troubleshooting

**v2.1.0** | Quick fixes for common issues

---

## Installation

| Issue | Fix |
|-------|-----|
| Python version error | Need Python 3.11+: `python3 --version` |
| Package install fails | Use venv: `python3 -m venv venv && source venv/bin/activate` |
| Pandoc not found | `sudo apt install pandoc` (Linux) / `brew install pandoc` (Mac) |
| wkhtmltopdf missing | `sudo apt install wkhtmltopdf` / `brew install wkhtmltopdf` |
| PySide6 fails | `pip install --upgrade pip && pip install PySide6>=6.9.0` |

---

## Startup

| Issue | Fix |
|-------|-----|
| Window doesn't appear | `QT_QPA_PLATFORM=xcb python3 src/main.py` |
| "No Qt platform plugin" | `sudo apt install libxcb-xinerama0 libxcb-cursor0` |
| Slow startup (>2s) | Clear cache: `rm -rf ~/.cache/asciidoc_artisan/` |

---

## Runtime

| Issue | Fix |
|-------|-----|
| Preview not updating | Wait 500ms (debounce), or restart app |
| GPU not detected | Delete cache: `rm -rf ~/.cache/asciidoc_artisan/gpu_detection.json` |
| High memory | Restart app, clear recent files |
| PDF export fails | Check wkhtmltopdf: `which wkhtmltopdf` |
| DOCX export fails | Check Pandoc 2.0+: `pandoc --version` |

---

## Git Integration

| Issue | Fix |
|-------|-----|
| Git menu disabled | Ensure folder has `.git`: `git status` |
| Commit fails | Set user: `git config user.name "Name" && git config user.email "email"` |
| Push denied | Check SSH keys or HTTPS token |

---

## AI Features

| Issue | Fix |
|-------|-----|
| Ollama unavailable | Start service: `ollama serve` |
| "Invalid API key" | Check key at console.anthropic.com |
| Slow responses | Use smaller model: `ollama pull phi3` |

---

## Error Messages

| Message | Meaning | Fix |
|---------|---------|-----|
| ModuleNotFoundError | Package missing | `pip install <package>` |
| Pandoc not found | Pandoc missing | Install Pandoc |
| GPU detection failed | No GPU found | Works on CPU (slower) |
| Permission denied | No file access | Check `ls -l` permissions |

---

## Get Help

1. Check this guide
2. Search [GitHub Issues](https://github.com/webbwr/AsciiDoctorArtisan/issues)
3. Report bug with: version, platform, error message, steps to reproduce

---

*v2.1.0 | Dec 5, 2025*
