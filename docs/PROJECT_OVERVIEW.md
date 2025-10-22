# 🎯 AsciiDoctorArtisan - Project Overview

## ✅ You Are Now in the AsciiDoctorArtisan Project!

**Location**: `/home/webbp/github/AsciiDoctorArtisan`

---

## 📊 Project Statistics

### Repository Information
- **Repository**: webbwr/AsciiDoctorArtisan
- **Owner**: Richard Webb (webbwr)
- **Status**: Active Development
- **Language**: Python
- **Framework**: PySide6 (Qt for Python)
- **License**: MIT

### Code Statistics
```
Total Python Code: 2,824 lines
├─ adp_windows.py: 2,378 lines (Main application)
├─ pandoc_integration.py: 295 lines (Document conversion)
└─ setup.py: 151 lines (Installation setup)
```

### Recent Development Activity
- **Latest**: Repository cleanup and optimization
- **Focus**: Spec-driven development with GitHub Spec Kit
- **Documentation**: 12 focused guides in docs/
- **Structure**: Streamlined with clear separation of concerns

---

## 🎨 Project Description

**AsciiDoc Artisan** is a modern, feature-rich AsciiDoc editor built with Python and PySide6 (Qt for Python).

### Core Features
- **Live Preview**: Real-time HTML rendering of AsciiDoc
- **Multi-Format Support**: Import/export DOCX, Markdown, HTML, LaTeX, RST
- **Git Integration**: Commit, pull, push directly from the editor
- **Dark/Light Themes**: Toggle with F5
- **Synchronized Scrolling**: Preview follows editor position
- **Font Zoom**: Ctrl +/- for quick size adjustments
- **Auto-save**: Configurable automatic saving
- **Session Persistence**: Remembers last opened files

---

## 🏗️ Project Structure

```
AsciiDoctorArtisan/
├── adp_windows.py                   # Main application
├── pandoc_integration.py            # Document conversion
├── setup.py                         # Package setup
├── requirements.txt                 # Flexible dependencies
├── requirements-production.txt      # Pinned versions
├── docs/                            # All documentation
│   ├── QUICK_START.md
│   ├── INSTALLATION_COMPLETE.md
│   ├── PANDOC_INTEGRATION.md
│   └── ... (feature guides)
├── scripts/                         # Setup scripts
│   └── AsciiDocArtisanVerify.ps1
├── .github/                         # GitHub configuration
│   └── copilot-instructions.md
├── .specify/                        # Spec-driven development
│   ├── memory/
│   ├── scripts/
│   └── templates/
└── .claude/                         # Claude Code commands (gitignored)
```

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python3 adp_windows.py
```

### Key Dependencies
- **PySide6** ≥ 6.9.0 - Qt GUI framework
- **asciidoc3** - AsciiDoc rendering engine
- **pypandoc** - Document conversion wrapper
- **Pandoc** (external) - Universal document converter

---

## 📚 Documentation

### User Guides
- **QUICK_START.md** - Get started in minutes
- **INSTALLATION_COMPLETE.md** - Detailed setup guide
- **PANDOC_INTEGRATION.md** - Format conversion details
- **EXPORT_FORMATS_GUIDE.md** - Export capabilities
- **PDF_EXPORT_GUIDE.md** - PDF generation
- **SYNCHRONIZED_SCROLLING_GUIDE.md** - Editor/preview sync
- **PANE_MAXIMIZE_GUIDE.md** - UI customization

### Technical Guides
- **DEVELOPMENT.md** - Development setup
- **CONTRIBUTING.md** - Contribution guidelines
- **CONVERSION_TEST_GUIDE.md** - Testing conversions
- **asciidoc-verification-summary.md** - Windows troubleshooting

### Release Information
- **RELEASE_NOTES_v1.0.0-beta.md** - Beta release notes

---

## 🔧 Development

### Spec-Driven Development
The project uses GitHub Spec Kit for structured development:

**Claude Code Slash Commands:**
- `/speckit.constitution` - Project principles
- `/speckit.specify` - Feature specifications
- `/speckit.plan` - Implementation planning
- `/speckit.tasks` - Task generation
- `/speckit.implement` - Execution

### Testing
```bash
# Check Python syntax
python3 -m py_compile adp_windows.py

# Verify dependencies
python3 -c "import PySide6, asciidoc3, pypandoc; print('All OK')"
```

### Contributing
See `CONTRIBUTING.md` for guidelines on:
- Code style and standards
- Pull request process
- Issue reporting
- Development workflow

---

## 🎯 Current Status

**Version**: 1.0.0-beta
**Status**: Active Development
**Primary Platform**: Cross-platform (Linux, macOS, Windows)
**WSL Support**: ✅ Full support with WSLg

### Recent Achievements
- ✅ Repository cleanup and optimization (-1,458 lines)
- ✅ Streamlined documentation structure
- ✅ GitHub Spec Kit integration
- ✅ Enhanced security (.claude/ in .gitignore)
- ✅ Professional project organization

---

## 🌟 Features Highlights

### Document Conversion
- Import: DOCX, Markdown, HTML, LaTeX, RST, Org, Textile
- Export: HTML, PDF (via Pandoc), DOCX
- Clipboard conversion with smart format detection

### Editor Features
- Syntax-aware editing
- Find and replace
- Go to line
- Word wrap
- Tab size configuration
- Monospace font with TypeWriter hint

### Git Integration
- In-app commits with custom messages
- Pull from remote
- Push to remote
- Repository auto-detection
- Status integration

### User Interface
- Clean, professional layout
- Splitter for resizable panes
- Dark/Light theme toggle
- Font zoom (Ctrl +/-)
- Session persistence
- Window state memory

---

## 📧 Support

For issues, questions, or contributions:
1. Check existing documentation in `docs/`
2. Review `CONTRIBUTING.md` for guidelines
3. Open an issue on GitHub
4. Follow spec-driven development workflow

---

*Last Updated: 2025-10-22*
*Ready for development and contribution*
