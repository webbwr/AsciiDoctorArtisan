# Cross-Platform Compatibility Guide

AsciiDoc Artisan supports Linux, macOS, and Windows through PySide6/Qt.

## Platform Support Matrix

| Feature | Linux | macOS | Windows |
|---------|-------|-------|---------|
| Core Editor | ✅ | ✅ | ✅ |
| Live Preview | ✅ | ✅ | ✅ |
| GPU Acceleration | ✅ | ✅ Metal | ✅ DirectX |
| Git Integration | ✅ | ✅ | ✅ |
| GitHub CLI | ✅ | ✅ | ✅ |
| Spell Check | ✅ | ✅ | ✅ |
| Templates | ✅ | ✅ | ✅ |
| LSP Server | ✅ | ✅ | ✅ |
| Export PDF | ✅ | ✅ | ✅ |
| Export DOCX | ✅ | ✅ | ✅ |

## Installation by Platform

### Linux (Ubuntu/Debian)

```bash
# System dependencies
sudo apt install python3.11 python3-pip pandoc wkhtmltopdf gh

# Install
pip install asciidoc-artisan
# or from source
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
pip install -e .
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3.11 pandoc wkhtmltopdf gh
pip install asciidoc-artisan
```

### Linux (Arch)

```bash
sudo pacman -S python pandoc wkhtmltopdf github-cli
pip install asciidoc-artisan
```

### macOS

```bash
# Using Homebrew
brew install python@3.11 pandoc wkhtmltopdf gh

pip install asciidoc-artisan
```

### Windows

```powershell
# Using Chocolatey
choco install python311 pandoc wkhtmltopdf gh

pip install asciidoc-artisan
```

Or download installers:
- Python: https://python.org
- Pandoc: https://pandoc.org
- wkhtmltopdf: https://wkhtmltopdf.org
- GitHub CLI: https://cli.github.com

## Platform-Specific Notes

### Linux

**WSL2 Support:**
- Full support with WSLg for GUI
- GPU passthrough via DirectX 12
- Use `DISPLAY=:0` for X11 apps

**GPU Detection:**
- NVIDIA: Requires `nvidia-smi`
- AMD: Requires `rocm-smi`
- Intel: Detected via OpenGL

### macOS

**Apple Silicon (M1/M2/M3):**
- Native ARM64 support via PySide6
- Metal GPU acceleration
- Neural Engine detection for AI features

**Intel Macs:**
- Full x86_64 support
- Metal GPU acceleration

**Security:**
- Keychain used for API key storage
- Requires Keychain Access permission

### Windows

**GPU Support:**
- NVIDIA: Auto-detected via nvidia-smi.exe
- AMD/Intel: DirectX 12 passthrough

**Path Handling:**
- All paths normalized to forward slashes internally
- Long path support (>260 chars) enabled

**Antivirus:**
- May need exclusion for real-time preview
- Qt WebEngine can trigger false positives

## Configuration Paths

| Platform | Settings Location |
|----------|-------------------|
| Linux | `~/.config/AsciiDocArtisan/` |
| macOS | `~/Library/Application Support/AsciiDocArtisan/` |
| Windows | `%APPDATA%\AsciiDocArtisan\` |

## Testing Cross-Platform

```bash
# Run platform-specific tests
pytest -m "not requires_gpu"  # No GPU required
pytest -m "requires_gpu"      # Requires GPU

# Run with display
DISPLAY=:0 pytest tests/e2e/  # Linux/WSL
pytest tests/e2e/              # macOS/Windows
```

## Known Issues

### Linux
- Qt WebEngine requires `libxcb-xinerama0` on some distros
- Wayland may require `QT_QPA_PLATFORM=xcb` fallback

### macOS
- First launch may require security approval
- Gatekeeper may block unsigned builds

### Windows
- Windows Defender may slow first launch
- High DPI scaling may need adjustment

## Reporting Platform Issues

When reporting issues, include:

1. Platform and version (e.g., Ubuntu 24.04, macOS 14.2, Windows 11)
2. Python version (`python --version`)
3. Qt version (`python -c "from PySide6 import QtCore; print(QtCore.__version__)"`)
4. GPU info (`python -m asciidoc_artisan.core.gpu_detection show`)

---

*AsciiDoc Artisan v2.1.0*
