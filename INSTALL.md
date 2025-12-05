# AsciiDoc Artisan Installation Guide

**Version 2.1.0** | Python 3.11+ | PySide6 6.9+

## Quick Start

```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

Then follow your platform-specific instructions below.

---

## Windows 11 (Native)

### Prerequisites

1. **Python 3.11+**
   ```powershell
   # Option A: Download from python.org
   # https://www.python.org/downloads/ (check "Add to PATH")

   # Option B: Chocolatey
   choco install python312
   ```

2. **System Dependencies**
   ```powershell
   # Pandoc (required - document conversion)
   choco install pandoc

   # wkhtmltopdf (required - PDF export)
   choco install wkhtmltopdf

   # Git (optional - version control)
   choco install git

   # GitHub CLI (optional - GitHub integration)
   choco install gh
   ```

### Install

**Automated:**
```powershell
powershell -ExecutionPolicy Bypass -File install-asciidoc-artisan.ps1
```

**Manual:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-prod.txt
```

### Run

```powershell
python src\main.py
```

---

## Windows 11 WSL2 (Ubuntu)

WSL2 provides better performance and GPU acceleration via WSLg.

### Prerequisites

1. **Enable WSL2**
   ```powershell
   # PowerShell (Admin)
   wsl --install -d Ubuntu
   wsl --update
   ```

2. **Inside WSL2 (Ubuntu)**
   ```bash
   sudo apt update && sudo apt upgrade -y

   # Python 3.11+
   sudo apt install python3.12 python3.12-venv python3-pip -y

   # System dependencies
   sudo apt install pandoc wkhtmltopdf git gh -y

   # GUI support (WSLg is built-in on Windows 11)
   sudo apt install libxcb-xinerama0 libxcb-cursor0 -y
   ```

### Install

**Automated:**
```bash
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Manual:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
```

### Run

```bash
# Standard
python3 src/main.py

# Optimized (strips debug code)
./run.sh

# With GPU acceleration check
./launch-asciidoc-artisan-gui.sh
```

### WSL2 Display Notes

- **WSLg (Windows 11 22H2+)**: Works out of the box
- **Older Windows**: Install VcXsrv or X410, then set `DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0`

---

## macOS

### Prerequisites

1. **Homebrew**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python 3.11+**
   ```bash
   brew install python@3.12
   ```

3. **System Dependencies**
   ```bash
   brew install pandoc wkhtmltopdf git gh
   ```

### Install

**Automated:**
```bash
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Manual:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
```

### Run

```bash
python3 src/main.py
# or
./run.sh
```

### macOS Notes

- **Apple Silicon (M1/M2/M3)**: Full native support with Metal GPU acceleration
- **Intel Macs**: OpenGL acceleration available

---

## Linux (Ubuntu/Debian)

### Prerequisites

```bash
sudo apt update && sudo apt upgrade -y

# Python 3.11+
sudo apt install python3.12 python3.12-venv python3-pip -y

# System dependencies
sudo apt install pandoc wkhtmltopdf git gh -y

# Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0 libgl1-mesa-glx -y
```

### Install

**Automated:**
```bash
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Manual:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
```

### Run

```bash
python3 src/main.py
# or
./run.sh
```

---

## Linux (Fedora/RHEL)

### Prerequisites

```bash
sudo dnf update -y

# Python 3.11+
sudo dnf install python3.12 python3-pip -y

# System dependencies
sudo dnf install pandoc wkhtmltopdf git gh -y

# Qt dependencies
sudo dnf install libxcb mesa-libGL -y
```

### Install

Same as Ubuntu (use install script or manual pip install).

---

## Linux (Arch)

### Prerequisites

```bash
sudo pacman -Syu

# Dependencies
sudo pacman -S python python-pip pandoc wkhtmltopdf git github-cli --noconfirm
```

### Install

Same as Ubuntu (use install script or manual pip install).

---

## GPU Acceleration

AsciiDoc Artisan automatically detects and uses GPU acceleration for 10-50x faster preview rendering.

### Verify GPU

```bash
# NVIDIA
nvidia-smi

# AMD
rocm-smi

# Intel
glxinfo | grep "OpenGL renderer"
```

### GPU-Specific Setup

| GPU | Driver | Notes |
|-----|--------|-------|
| NVIDIA | Latest NVIDIA drivers | WSL2: Install Windows driver only |
| AMD | ROCm or Mesa | `sudo apt install rocm-smi` |
| Intel | Mesa (pre-installed) | OpenVINO optional for NPU |
| Apple Silicon | Metal (built-in) | No setup needed |

---

## Optional: AI Features

### Ollama (Local AI)

```bash
# Linux/macOS
curl https://ollama.ai/install.sh | sh
ollama pull phi3:mini  # Recommended model

# Windows
# Download from https://ollama.ai/download
```

### Anthropic Claude (Cloud AI)

1. Get API key from https://console.anthropic.com
2. Enter in app: Settings > AI > Anthropic API Key

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `pandoc not found` | Install Pandoc for your OS |
| `PDF export fails` | Install wkhtmltopdf |
| `Qt platform error` | Install libxcb dependencies |
| `No display` (WSL2) | Ensure WSLg is enabled: `wsl --update` |
| `GPU not detected` | Check drivers with `nvidia-smi` or `glxinfo` |

### Logs

```bash
# Launcher log
cat logs/launcher.log

# Application log
cat ~/.config/AsciiDocArtisan/app.log
```

---

## Development Install

```bash
# Clone and install in editable mode
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/unit/ -q

# Type check
mypy --strict src/
```

---

## Uninstall

```bash
# Remove virtual environment
rm -rf venv/

# Remove settings (optional)
rm -rf ~/.config/AsciiDocArtisan/  # Linux
rm -rf ~/Library/Application\ Support/AsciiDocArtisan/  # macOS
# Windows: %APPDATA%/AsciiDocArtisan/
```

---

*v2.1.0 | MIT License | [Report Issues](https://github.com/webbwr/AsciiDoctorArtisan/issues)*
