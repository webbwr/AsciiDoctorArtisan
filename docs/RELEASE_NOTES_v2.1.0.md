# AsciiDoc Artisan v2.1.0 Release Notes

**Release Date:** December 5, 2025 | **Type:** Production Release

## Highlights

First production-stable release with LSP support, multi-core rendering, and GPU acceleration.

### Key Features

- **LSP Server** - IDE integration (completion, diagnostics, hover, symbols)
- **Multi-core Rendering** - 2-4x speedup on 4+ core systems
- **GPU Acceleration** - 10-50x faster preview (NVIDIA/AMD/Intel/Apple Silicon)
- **Ollama AI Chat** - Local AI assistance with phi3, llama3, mistral
- **Claude AI Integration** - Cloud AI via Anthropic API

## Metrics

| Metric | Value |
|--------|-------|
| Codebase | 44,201 lines / 171 files |
| Unit Tests | 5,308 (100% pass) |
| E2E Tests | 71 (100% pass) |
| Type Coverage | 100% (mypy --strict) |
| Requirements | 109 FRs implemented |
| Startup | 0.586s |

---

## Installation

### Quick Install (All Platforms)

```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

### Windows 11 (Native)

**Prerequisites:**
- Python 3.11+ from [python.org](https://python.org) (check "Add to PATH")
- [Pandoc](https://pandoc.org/installing.html) - document conversion
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) - PDF export

**Automated Install:**
```powershell
powershell -ExecutionPolicy Bypass -File install-asciidoc-artisan.ps1
```

**Manual Install:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-prod.txt
python src\main.py
```

**With Chocolatey:**
```powershell
choco install python312 pandoc wkhtmltopdf git gh
```

---

### Windows 11 WSL2

Best performance with GPU acceleration via WSLg.

**Setup WSL2:**
```powershell
# PowerShell (Admin)
wsl --install -d Ubuntu
wsl --update
```

**Inside WSL2:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.12 python3.12-venv python3-pip pandoc wkhtmltopdf git gh libxcb-xinerama0 libxcb-cursor0 -y
```

**Install:**
```bash
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Run:**
```bash
./run.sh              # Optimized
python3 src/main.py   # Normal
```

---

### macOS

**Prerequisites:**
```bash
brew install python@3.12 pandoc wkhtmltopdf git gh
```

**Install:**
```bash
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Run:**
```bash
./run.sh
```

**GPU:** Apple Silicon uses Metal automatically. Intel Macs use OpenGL.

---

### Linux (Ubuntu/Debian)

**Prerequisites:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip pandoc wkhtmltopdf git gh libxcb-xinerama0 libxcb-cursor0 -y
```

**Install:**
```bash
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Run:**
```bash
./run.sh
```

---

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3.12 python3-pip pandoc wkhtmltopdf git gh -y
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

---

### Linux (Arch)

```bash
sudo pacman -S python python-pip pandoc wkhtmltopdf git github-cli --noconfirm
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

---

## Command-Line Install (All Platforms)

```bash
# 1. Clone repository
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate (Linux/macOS)
source venv/bin/activate
# Or Windows: .\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements-prod.txt

# 5. Run
python3 src/main.py
```

---

## GPU Acceleration

Automatically detected. Verify with:

```bash
nvidia-smi          # NVIDIA
rocm-smi            # AMD
glxinfo | grep renderer  # Intel/Mesa
```

| GPU | Setup |
|-----|-------|
| NVIDIA | Install Windows driver (WSL2 uses passthrough) |
| AMD | Install ROCm or Mesa |
| Intel | Mesa pre-installed on Linux |
| Apple Silicon | Metal built-in, no setup |

---

## Optional: AI Features

### Ollama (Local AI)

```bash
# Linux/macOS
curl https://ollama.ai/install.sh | sh
ollama pull phi3:mini

# Windows: https://ollama.ai/download
```

### Claude (Cloud AI)

Get API key from https://console.anthropic.com

---

## Requirements

### Python Packages (Core)

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | 6.10+ | Qt GUI framework |
| asciidoc3 | 3.2+ | AsciiDoc rendering |
| pypandoc | 1.16+ | Document conversion |
| pymupdf | 1.26+ | PDF extraction |
| keyring | 25+ | Secure credential storage |
| psutil | 5.9+ | System monitoring |

### System Dependencies

| Tool | Required | Purpose |
|------|----------|---------|
| Pandoc | Yes | DOCX, Markdown, HTML conversion |
| wkhtmltopdf | Yes | PDF export |
| Git | No | Version control |
| GitHub CLI | No | GitHub integration |
| Ollama | No | Local AI |

---

## What's New in 2.1.0

- LSP server: `python -m asciidoc_artisan.lsp`
- ParallelBlockRenderer with ThreadPoolExecutor
- Code action, folding, formatting, semantic tokens providers
- Ollama model browser UI
- GPU detection improvements
- MA-principled code (cleaner, less over-commenting)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `pandoc not found` | Install Pandoc for your OS |
| `PDF export fails` | Install wkhtmltopdf |
| `Qt platform error` | `apt install libxcb-xinerama0` |
| `No display (WSL2)` | Run `wsl --update` |

---

## Settings Locations

- **Linux:** `~/.config/AsciiDocArtisan/`
- **macOS:** `~/Library/Application Support/AsciiDocArtisan/`
- **Windows:** `%APPDATA%/AsciiDocArtisan/`

---

*v2.1.0 | Production Ready | MIT License*

[Full Install Guide](../INSTALL.md) | [User Guide](user/user-guide.md) | [Troubleshooting](user/troubleshooting.md)
