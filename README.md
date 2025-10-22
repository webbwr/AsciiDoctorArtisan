# AsciiDoc Artisan

A modern, feature-rich AsciiDoc editor with live preview, built with Python and PySide6.

## Features

- **Live Preview**: Real-time HTML preview of your AsciiDoc content
- **Syntax Highlighting**: Clear, monospace editor optimized for AsciiDoc
- **Document Conversion**: Import/export DOCX files via Pandoc
- **Git Integration**: Commit, pull, and push directly from the editor
- **Dark Mode**: Toggle between light and dark themes
- **Auto-save**: Automatic saving with configurable intervals
- **Font Zoom**: Easily adjust editor font size
- **Session Management**: Remembers last opened file and window state
- **Cross-platform**: Works on Windows, Linux, and macOS

## Requirements

- **Python**: 3.11+ (3.12 recommended)
- **PySide6**: 6.9.0 or higher
- **asciidoc3**: For AsciiDoc to HTML conversion
- **pypandoc**: For DOCX import/export (optional)
- **Pandoc**: Required for DOCX conversion (install separately)
- **Git**: Required for version control features (optional)

## Installation

### Quick Setup (Linux/WSL)

```bash
# Clone the repository
cd ~/github  # or your preferred location
git clone https://github.com/YOUR_USERNAME/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run the setup script
chmod +x setup.sh
./setup.sh

# Verify installation
chmod +x verify.sh
./verify.sh
```

### Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Pandoc (Ubuntu/Debian)
sudo apt install pandoc

# Install Pandoc (macOS)
brew install pandoc

# Install Pandoc (Windows)
# Download from: https://pandoc.org/installing.html
```

### Windows Setup

```powershell
# Run the PowerShell verification script
.\AsciiDocArtisanVerify.ps1

# This script will:
# - Check Python installation
# - Install required packages
# - Verify Pandoc availability
# - Fix common PATH issues
```

## Usage

### Starting the Application

```bash
# Linux/WSL/macOS
python3 adp_windows.py

# Windows
python adp_windows.py
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+Q` | Quit |
| `Ctrl+F` | Find text |
| `Ctrl+G` | Go to line |
| `Ctrl+D` | Toggle dark mode |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |

### File Operations

**Supported Formats:**
- `.adoc` - AsciiDoc files (native)
- `.asciidoc` - AsciiDoc files (native)
- `.docx` - Word documents (via Pandoc conversion)

**Opening Files:**
1. Click `File → Open` or press `Ctrl+O`
2. Select an AsciiDoc or DOCX file
3. DOCX files are automatically converted to AsciiDoc

**Saving Files:**
1. Click `File → Save` or press `Ctrl+S`
2. For new files, choose a location and filename
3. Files are saved with `.adoc` extension by default

### Git Operations

**Requirements:**
- File must be in a Git repository
- Git must be installed and accessible

**Available Operations:**
- `Git → Pull`: Pull latest changes from remote
- `Git → Commit`: Commit current file changes
- `Git → Push`: Push commits to remote

**Commit Workflow:**
1. Save your file (`Ctrl+S`)
2. Select `Git → Commit`
3. Enter commit message when prompted
4. File is staged and committed automatically

### Preview Features

The preview pane shows a live HTML rendering of your AsciiDoc:
- **Auto-refresh**: Updates as you type (350ms delay)
- **Synchronized scrolling**: Preview follows editor position
- **Full AsciiDoc support**: All standard AsciiDoc syntax
- **Fallback mode**: Shows plain text if asciidoc3 unavailable

## Configuration

Settings are automatically stored in a platform-appropriate location:
- **Linux/WSL**: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows**: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **macOS**: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

**Configuration Format:**
```json
{
  "last_directory": "/path/to/documents",
  "git_repo_path": "/path/to/repo",
  "dark_mode": true,
  "maximized": true,
  "window_geometry": null
}
```

**Configuration Options:**
- `last_directory`: Last opened file location
- `git_repo_path`: Git repository path (auto-detected)
- `dark_mode`: Enable/disable dark theme
- `maximized`: Window maximization state
- `window_geometry`: Window size/position (when not maximized)

**Note:** The configuration file is created automatically on first run.

## Project Structure

```
AsciiDoctorArtisan/
├── adp_windows.py                   # Main application
├── pandoc_integration.py            # Document conversion module
├── setup.py                         # Package setup
├── requirements.txt                 # Python dependencies (flexible)
├── requirements-production.txt      # Pinned production versions
├── LICENSE                          # MIT License
├── CHANGELOG.md                     # Version history
├── CONTRIBUTING.md                  # Contribution guidelines
├── README.md                        # This file
├── docs/                            # Documentation
│   ├── QUICK_START.md
│   ├── INSTALLATION_COMPLETE.md
│   ├── ANALYSIS_AND_MVP_PLAN.md
│   └── ... (guides and release notes)
├── scripts/                         # Setup and verification scripts
│   └── AsciiDocArtisanVerify.ps1
├── .github/                         # GitHub configuration
│   └── copilot-instructions.md
└── .gitignore                       # Git exclusions
```

## Troubleshooting

### Common Issues

**Issue: "WARNING: 'pypandoc' library not found"**
- **Solution**: Install pypandoc: `pip install pypandoc`
- **Note**: DOCX conversion will be disabled without this

**Issue: "WARNING: 'asciidoc3' library not found"**
- **Solution**: Install asciidoc3: `pip install asciidoc3`
- **Note**: Preview will show plain text without this

**Issue: "Pandoc not found in PATH"**
- **Solution**: Install Pandoc from https://pandoc.org/installing.html
- **Linux**: `sudo apt install pandoc`
- **macOS**: `brew install pandoc`

**Issue: Git operations fail**
- **Solution**: Ensure file is in a Git repository
- **Check**: Run `git status` in the file's directory

**Issue: Application won't start on Windows**
- **Solution**: Run `AsciiDocArtisanVerify.ps1` to diagnose
- **Common fix**: Disable Microsoft Store Python aliases

### Windows-Specific Issues

See [asciidoc-verification-summary.md](asciidoc-verification-summary.md) for detailed troubleshooting of:
- PowerShell version issues
- Python installation problems
- Missing dependencies
- PATH configuration

## Development

### Running Tests

```bash
# Verify installation
./verify.sh

# Check Python syntax
python3 -m py_compile adp_windows.py

# Check dependencies
python3 -c "import PySide6, asciidoc3, pypandoc; print('All OK')"
```

### Scripts

- `setup.sh`: Automated setup for Linux/WSL
- `verify.sh`: Verify installation and dependencies
- `AsciiDocArtisanVerify.ps1`: Windows setup and verification

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with:
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Qt bindings for Python
- [asciidoc3](https://github.com/asciidoc-py/asciidoc-py) - AsciiDoc processing
- [pypandoc](https://github.com/JessicaTegner/pypandoc) - Document conversion

## Support

For issues and questions:
- Create an issue on GitHub
- Check [asciidoc-verification-summary.md](asciidoc-verification-summary.md) for common solutions
