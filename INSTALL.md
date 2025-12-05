# Installation Guide

**v2.1.0** | Python 3.11+ | PySide6 6.9+

---

## Quick Start

```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

Then follow your platform instructions below.

---

## Windows 11 (Native)

### 1. Install Prerequisites

```powershell
# Python 3.11+ (from python.org or Chocolatey)
choco install python312

# Required
choco install pandoc wkhtmltopdf

# Optional
choco install git gh
```

### 2. Install App

```powershell
# Automated
powershell -ExecutionPolicy Bypass -File install-asciidoc-artisan.ps1

# Manual
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-prod.txt
```

### 3. Run

```powershell
python src\main.py
```

---

## Windows 11 WSL2

WSL2 provides better performance and GPU acceleration.

### 1. Enable WSL2

```powershell
# PowerShell (Admin)
wsl --install -d Ubuntu
wsl --update
```

### 2. Install Prerequisites (in WSL2)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.12 python3.12-venv python3-pip -y
sudo apt install pandoc wkhtmltopdf git gh -y
sudo apt install libxcb-xinerama0 libxcb-cursor0 -y
```

### 3. Install App

```bash
./install-asciidoc-artisan.sh
```

### 4. Run

```bash
make run
```

---

## macOS

### 1. Install Prerequisites

```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Dependencies
brew install python@3.12 pandoc wkhtmltopdf git gh
```

### 2. Install App

```bash
./install-asciidoc-artisan.sh
```

### 3. Run

```bash
make run
```

**Notes:**
- Apple Silicon (M1/M2/M3): Metal GPU acceleration
- Intel Macs: OpenGL acceleration

---

## Linux (Ubuntu/Debian)

### 1. Install Prerequisites

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.12 python3.12-venv python3-pip -y
sudo apt install pandoc wkhtmltopdf git gh -y
sudo apt install libxcb-xinerama0 libxcb-cursor0 libgl1-mesa-glx -y
```

### 2. Install App

```bash
./install-asciidoc-artisan.sh
```

### 3. Run

```bash
make run
```

---

## Linux (Fedora)

```bash
sudo dnf update -y
sudo dnf install python3.12 python3-pip pandoc wkhtmltopdf git gh libxcb mesa-libGL -y
./install-asciidoc-artisan.sh
```

---

## Linux (Arch)

```bash
sudo pacman -Syu
sudo pacman -S python python-pip pandoc wkhtmltopdf git github-cli --noconfirm
./install-asciidoc-artisan.sh
```

---

## GPU Acceleration

Auto-detected. Provides 10-50x faster preview.

### Verify GPU

| GPU | Command |
|-----|---------|
| NVIDIA | `nvidia-smi` |
| AMD | `rocm-smi` |
| Intel | `glxinfo \| grep "OpenGL renderer"` |

### Driver Notes

| GPU | Notes |
|-----|-------|
| NVIDIA | WSL2: Use Windows driver only |
| AMD | Install ROCm or Mesa |
| Intel | Mesa pre-installed |
| Apple Silicon | Metal built-in |

---

## Optional: AI Features

### Ollama (Local AI)

```bash
curl https://ollama.ai/install.sh | sh
ollama pull phi3:mini
```

### Claude (Cloud AI)

1. Get API key: https://console.anthropic.com
2. Enter in app: Settings > AI > API Key

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Pandoc not found | Install pandoc for your OS |
| PDF export fails | Install wkhtmltopdf |
| Qt platform error | Install libxcb dependencies |
| No display (WSL2) | Run `wsl --update` |
| GPU not detected | Check drivers |

### Logs

```bash
cat logs/launcher.log
cat ~/.config/AsciiDocArtisan/app.log
```

---

## Development Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/unit/ -q
mypy --strict src/
```

---

## Uninstall

```bash
rm -rf venv/
rm -rf ~/.config/AsciiDocArtisan/  # Linux
```

---

*v2.1.0 | MIT License | [Report Issues](https://github.com/webbwr/AsciiDoctorArtisan/issues)*
