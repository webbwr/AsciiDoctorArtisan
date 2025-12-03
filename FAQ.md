# Frequently Asked Questions (FAQ)

**Version:** 2.1.0
**Last Updated:** December 3, 2025
**Status:** Comprehensive

---

## Table of Contents

- [General Questions](#general-questions)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [Security](#security)
- [Development](#development)

---

## General Questions

### What is AsciiDoc Artisan?

AsciiDoc Artisan is a fast, smart program for writing documents. It shows your work as you type and helps you write better. It works with AsciiDoc files and can convert them to PDF, Word, HTML, and Markdown.

**Key Features:**
- Live preview (see changes instantly)
- Smart writing help (auto-complete)
- Spell check and error checking
- Git integration (save versions)
- AI chat help (Ollama)
- Very fast (GPU-accelerated, 10-50x faster)

### Is it free?

Yes! AsciiDoc Artisan is free and open source (MIT License). You can use it for anything - personal or commercial.

### What does "AsciiDoc" mean?

AsciiDoc is a way to write documents using plain text. You write `= Heading` instead of clicking "Bold". It's like Markdown but more powerful.

**Example:**
```asciidoc
= Document Title
Author Name

== Chapter 1

This is *bold* and this is _italic_.

* List item 1
* List item 2
```

### Which platforms are supported?

- ✅ **Linux** (Ubuntu, Debian, Fedora, Arch)
- ✅ **macOS** (10.15+)
- ✅ **Windows** (10, 11)

All features work on all platforms.

---

## Installation

### How do I install it?

**Easy way (recommended):**

**Linux/Mac:**
```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Windows:**
```powershell
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
.\Install-AsciiDocArtisan.ps1
```

The script installs everything you need automatically.

### What are the system requirements?

**Minimum:**
- Python 3.11+
- 2 GB RAM
- 100 MB disk space

**Recommended:**
- Python 3.12+
- 4 GB RAM
- GPU (NVIDIA, AMD, or Intel)
- 500 MB disk space

### Do I need Pandoc?

Yes! Pandoc converts files between formats. The install script gets it for you.

**Manual install:**
- Linux: `sudo apt install pandoc`
- Mac: `brew install pandoc`
- Windows: Download from pandoc.org

### Do I need a GPU?

No, but it helps! With a GPU:
- Preview is 10-50x faster
- Uses 70-90% less CPU
- Smoother scrolling

Without a GPU, everything still works, just slower.

---

## Usage

### How do I start the program?

```bash
./run.sh          # Fast mode (recommended)
# OR
make run          # Same thing
# OR
python3 src/main.py  # Normal mode
```

The program opens in a window. You see the editor on the left and preview on the right.

### How do I open a file?

1. Click **File** → **Open**
2. Pick your file
3. Click **Open**

Supported: `.adoc`, `.md`, `.docx`, `.html`, `.pdf`

### How do I save my work?

**Quick save:** Press `Ctrl+S`

**Or:**
1. Click **File** → **Save**
2. Type a file name
3. Click **Save**

**Auto-save:** Turn it on in Preferences (Tools → Preferences)

### How do I export to PDF?

1. Click **File** → **Export** → **Export as PDF**
2. Pick where to save it
3. Click **Save**

The PDF appears in a few seconds.

### What keyboard shortcuts work?

| Shortcut | What It Does |
|----------|--------------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Q` | Quit |
| `Ctrl+F` | Find text |
| `Ctrl+H` | Find and replace |
| `F3` | Find next |
| `Shift+F3` | Find previous |
| `F7` | Toggle spell check |
| `F11` | Dark mode |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |

See [User Guide](docs/user/user-guide.md) for all shortcuts.

---

## Features

### How does auto-complete work?

As you type, AsciiDoc Artisan suggests what comes next.

**Trigger:** Press `Ctrl+Space`

**Example:**
- Type `=` → suggests heading levels
- Type `*` → suggests list or bold
- Type `:` → suggests attributes

**Disable:** Tools → Preferences → uncheck "Enable auto-complete"

### How does spell check work?

Red squiggly lines appear under misspelled words.

**Fix a word:**
1. Right-click the red word
2. Pick the correct spelling
3. Click it

**Turn on/off:** Press `F7`

### How do I use Git?

If your folder is a Git repo, you can:

**Save a version (commit):**
1. Click **Git** → **Commit**
2. Type what you changed
3. Click **OK**

**Get new changes (pull):**
- Click **Git** → **Pull**

**Send changes (push):**
- Click **Git** → **Push**

### How do I use AI chat?

**Setup:**
1. Install Ollama: `brew install ollama` (Mac) or visit ollama.com
2. Get a model: `ollama pull gnokit/improve-grammer`
3. Enable in Tools → AI Status → Settings

**Use:**
1. Click **Chat** icon (or press `F9`)
2. Type your question
3. Get AI help

**Modes:**
- **Doc Q&A:** Ask about your document
- **Syntax:** Learn AsciiDoc
- **General:** General questions
- **Editing:** Fix grammar and style

### Do I need internet for AI?

No! Ollama runs on your computer. Your files never leave your machine.

---

## Troubleshooting

### The program won't start

**Check Python version:**
```bash
python3 --version
```

Must be 3.11 or higher. Update if needed.

**Reinstall:**
```bash
./install-asciidoc-artisan.sh
```

### Can't find pypandoc

Install it:
```bash
pip install pypandoc
```

If that fails:
```bash
pip install --break-system-packages pypandoc
```

### Can't find Pandoc

Get it from pandoc.org or:
- Linux: `sudo apt install pandoc`
- Mac: `brew install pandoc`
- Windows: Download installer from pandoc.org

### PDF export fails

**Install wkhtmltopdf:**
- Linux: `sudo apt install wkhtmltopdf`
- Mac: `brew install wkhtmltopdf`
- Windows: Download from wkhtmltopdf.org

### Preview is slow

**Get a GPU or update drivers:**

**Check GPU:**
```bash
# NVIDIA
nvidia-smi

# AMD
rocm-smi

# Intel
glxinfo | grep "OpenGL renderer"
```

**If no GPU:** Program still works, just slower.

### Git buttons are grayed out

**Two reasons:**

1. **Not in a Git repo:** Initialize one:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Git not installed:** Install git:
   - Linux: `sudo apt install git`
   - Mac: `brew install git`
   - Windows: Download from git-scm.com

### Spell check doesn't work

**Turn it on:** Press `F7`

**If still broken:**
```bash
pip install pyspellchecker
```

### Auto-complete doesn't work

**Turn it on:** Tools → Preferences → "Enable auto-complete"

**Manual trigger:** Press `Ctrl+Space`

### Windows security warning

Windows may warn that the program is unsigned. This is normal for open-source software.

**To run anyway:**
1. Click "More info"
2. Click "Run anyway"

**Or:** Build from source (see CONTRIBUTING.md)

---

## Performance

### How fast is it?

**Startup:** 0.586 seconds
**Preview update:** <50ms with GPU
**File operations:** Instant (even large files)

### How can I make it faster?

1. **Use GPU** (10-50x faster preview)
2. **Enable auto-save** (saves work automatically)
3. **Use `-OO` flag:** `python3 -OO src/main.py`
4. **Close unused programs** (free up RAM)

### How big can my documents be?

**Tested limits:**
- ✅ 10,000+ lines
- ✅ 1 MB+ file size
- ✅ Complex tables and images

**Performance:**
- <500ms render for 10,000 lines
- <100ms syntax check for 1,000 lines
- <200ms template load

### Does it use a lot of memory?

**Typical usage:**
- Base: ~100 MB
- With document: +5-20 MB
- With preview: +50-100 MB

**Total: ~150-220 MB** (very efficient!)

---

## Security

### Is my data safe?

Yes! Your data stays on your computer. The program doesn't upload anything.

**Security features:**
- Atomic file saves (no corruption)
- Path sanitization (no directory attacks)
- Secure subprocess calls (no injection)
- Encrypted API keys (OS keyring)

See [SECURITY.md](SECURITY.md) for details.

### Can I use it offline?

Yes! Everything works offline:
- Editing
- Preview
- File operations
- Ollama AI (local)

**Only needs internet for:**
- Git push/pull (if using remote)
- Claude AI (if using Anthropic API)
- GitHub CLI (if creating PRs/issues)

### Are my API keys safe?

Yes! API keys are stored in your OS-level secure keyring:
- **Windows:** Windows Credential Manager
- **macOS:** Keychain
- **Linux:** gnome-keyring or kwallet

Never stored in plain text files.

### What about telemetry?

**Telemetry is opt-in only.** You must explicitly enable it.

**What's collected (if enabled):**
- Program version
- OS version
- Feature usage (anonymous)
- Crash reports (anonymous)

**Never collected:**
- Your documents
- File names
- Personal information
- API keys

**Disable anytime:** Tools → Preferences → uncheck "Enable telemetry"

---

## Development

### How do I contribute?

1. Fork the repo on GitHub
2. Make your changes
3. Run tests: `make test`
4. Submit a pull request

See [CONTRIBUTING.md](docs/developer/contributing.md) for details.

### How do I run tests?

```bash
# All tests
make test

# Specific test file
pytest tests/test_file.py -v

# With coverage
make test  # Opens htmlcov/index.html
```

**Test status:**
- 5,548 unit tests (99.42% pass rate)
- 71 E2E scenarios (91.5% pass rate)
- 96.4% code coverage

### How do I build documentation?

```bash
# API documentation (planned)
sphinx-apidoc -o docs/api src/

# User documentation
# Edit files in docs/user/

# Developer documentation
# Edit files in docs/developer/
```

### How do I report bugs?

**For security bugs:** Email webbp@localhost

**For other bugs:**
1. Check [existing issues](https://github.com/webbwr/AsciiDoctorArtisan/issues)
2. If not found, create new issue
3. Include:
   - What you expected
   - What happened instead
   - Steps to reproduce
   - Your OS and Python version

### How do I request features?

Open a GitHub issue with:
1. Clear description of feature
2. Why it's useful
3. How it should work
4. Any mockups or examples

We review all feature requests!

### What's the project structure?

```
AsciiDoctorArtisan/
├── src/asciidoc_artisan/  # Source code
│   ├── core/              # Business logic
│   ├── ui/                # User interface
│   ├── workers/           # Background tasks
│   ├── claude/            # AI integration
│   └── conversion/        # Format conversion
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── e2e/              # End-to-end tests
│   └── performance/      # Benchmarks
├── docs/                  # Documentation
│   ├── user/             # User guides
│   ├── developer/        # Dev guides
│   └── reports/          # Analysis reports
├── templates/             # Document templates
└── scripts/               # Utility scripts
```

---

## More Help

### Where can I get more information?

**Documentation:**
- [README.md](README.md) - Project overview
- [User Guide](docs/user/user-guide.md) - All features
- [SPECIFICATIONS_AI.md](SPECIFICATIONS_AI.md) - Technical specs
- [ROADMAP.md](ROADMAP.md) - Future plans

**Community:**
- GitHub Issues - Bug reports and features
- GitHub Discussions - Questions and ideas

**Contact:**
- Project maintainer: webbp@localhost
- Security issues: webbp@localhost

### How often is it updated?

**Regular updates:** Monthly maintenance releases
**Security updates:** Within 7-30 days (depending on severity)
**Feature updates:** Quarterly

**Current version:** 2.1.0 (December 3, 2025)

### What's coming next?

See [ROADMAP.md](ROADMAP.md) for future plans.

**Included in v2.1.0:**
- LSP support (full Language Server Protocol)
- Multi-core rendering (2-4x speedup)
- Production stable

**Maintenance Mode (v2.1.x):**
- Bug fixes and stability
- Security updates
- Documentation updates

**Future (v3.0+):** Deferred
- Plugin system
- Collaboration

---

## Still Have Questions?

**Can't find your answer?**

1. Check [User Guide](docs/user/user-guide.md)
2. Search [GitHub Issues](https://github.com/webbwr/AsciiDoctorArtisan/issues)
3. Ask on GitHub Discussions
4. Email webbp@localhost

We're here to help!

---

**FAQ Version:** 2.1.0
**Last Updated:** December 3, 2025
**Questions Answered:** 50+
**Status:** ✅ Comprehensive

💡 **Tip:** Press `Ctrl+F` to search this FAQ for keywords
