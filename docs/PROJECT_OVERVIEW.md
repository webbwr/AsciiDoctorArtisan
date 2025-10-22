# 🎯 AsciiDoctorArtisan - Project Overview

## ✅ You Are Now in the AsciiDoctorArtisan Project!

**Location**: `/Users/rw/AsciiDoctorArtisan`

---

## 📊 Project Statistics

### Repository Information
- **Repository**: webbwr/AsciiDoctorArtisan
- **Owner**: Richard Webb (webbwr)
- **Status**: Private
- **Created**: September 8, 2025
- **Last Updated**: October 19, 2025
- **Stars**: ⭐ 1
- **Language**: Python

### Code Statistics
```
Total Python Code: 5,830 lines
├─ adp_windows.py: 2,225 lines (Windows-optimized version)
├─ adp_optimized.py: 2,065 lines (Performance-optimized)
├─ adp.py: 1,078 lines (Main application)
├─ pandoc_integration.py: 304 lines (Document conversion)
└─ setup.py: 158 lines (Installation setup)
```

### Recent Development Activity
- **Latest commit**: "fix: Ensure Editor and Preview labels match app text color"
- **Total commits**: 10+ recent commits
- **Active development**: Regular updates through October 2025
- **Focus areas**: PDF export, theme improvements, bug fixes

---

## 🎨 Project Description

**AsciiDoc Artisan** is a modern, feature-rich AsciiDoc editor built with Python and PySide6 (Qt for Python).

### Key Purpose
Professional AsciiDoc documentation toolkit with:
- Real-time live preview
- Multi-format document conversion
- Git integration
- Cross-platform support

---

## ✨ Core Features

### 1. **Editor Capabilities**
- ✅ Live HTML preview (real-time rendering)
- ✅ Syntax highlighting
- ✅ Auto-save functionality
- ✅ Font zoom controls
- ✅ Session management
- ✅ Dark/Light theme toggle

### 2. **Document Conversion** (via Pandoc)
- ✅ **Import from**:
  - Markdown (.md)
  - Microsoft Word (.docx)
  - HTML (.html)
  - LaTeX (.tex)
  - reStructuredText (.rst)
  - Org Mode (.org)
  - Textile (.textile)

- ✅ **Export to**:
  - HTML
  - PDF
  - DOCX
  - Other formats via Pandoc

### 3. **Git Integration**
- ✅ Commit files directly
- ✅ Pull from remote
- ✅ Push to remote
- ✅ Automatic staging

### 4. **UI/UX Features**
- ✅ Synchronized scrolling (editor ↔ preview)
- ✅ Pane maximization
- ✅ Window state persistence
- ✅ Cross-platform compatibility

---

## 🏗️ Project Structure

```
AsciiDoctorArtisan/
├── Core Application Files
│   ├── adp.py                    # Main application (1,078 lines)
│   ├── adp_windows.py            # Windows-optimized (2,225 lines)
│   ├── adp_optimized.py          # Performance version (2,065 lines)
│   ├── pandoc_integration.py     # Document conversion (304 lines)
│   └── setup.py                  # Installation setup (158 lines)
│
├── Configuration Files
│   ├── requirements.txt          # Production dependencies
│   ├── requirements-production.txt
│   └── AsciiDocArtisan.json      # App configuration
│
├── Documentation
│   ├── README.md                 # Main documentation
│   ├── QUICK_START.md            # Getting started guide
│   ├── INSTALLATION_COMPLETE.md  # Setup instructions
│   ├── PANDOC_INTEGRATION.md     # Conversion guide
│   ├── PDF_EXPORT_GUIDE.md       # PDF export help
│   ├── EXPORT_FORMATS_GUIDE.md   # Format conversion
│   ├── PANE_MAXIMIZE_GUIDE.md    # UI features
│   ├── SYNCHRONIZED_SCROLLING_GUIDE.md
│   ├── CONVERSION_TEST_GUIDE.md
│   └── asciidoc-verification-summary.md
│
├── Development Docs
│   ├── ANALYSIS_AND_MVP_PLAN.md  # Code analysis & roadmap
│   ├── UPDATE_PLAN.md            # Development plan
│   ├── OPTIMIZATION_REPORT.md    # Performance notes
│   ├── DELIVERABLES_SUMMARY.md   # Project deliverables
│   ├── CHANGELOG.md              # Version history
│   ├── RELEASE_NOTES_v1.0.0-beta.md
│   └── CONTRIBUTING.md           # Contribution guide
│
├── Scripts
│   ├── AsciiDocArtisanVerify.ps1 # Windows verification
│   └── (setup.sh, verify.sh would be here)
│
└── Other
    ├── LICENSE                    # MIT License
    ├── .gitignore
    ├── .gitattributes
    └── .github/
        └── copilot-instructions.md
```

---

## 🔧 Technical Stack

### Core Technologies
- **Python**: 3.11+ (3.12 recommended)
- **GUI Framework**: PySide6 6.9.0+ (Qt for Python)
- **Document Processing**: asciidoc3, pypandoc
- **Version Control**: Git integration

### Key Dependencies
```
PySide6>=6.9.0          # Qt GUI framework
asciidoc3               # AsciiDoc to HTML conversion
pypandoc                # Document format conversion
```

### External Requirements
- **Pandoc**: Required for DOCX/multi-format conversion
- **Git**: Optional, for version control features

---

## 🚀 Recent Development (Last 10 Commits)

1. ✅ **Fix**: Editor/Preview label colors match theme
2. ✅ **Fix**: Pane labels match app text style
3. ✅ **Feature**: PDF export with HTML fallback
4. ✅ **Feature**: HTML export as PDF alternative
5. ✅ **Improvement**: Better PDF engine detection
6. ✅ **Cleanup**: Remove test files
7. ✅ **Fix**: Correct asciidoc3 API usage
8. ✅ **Fix**: AsciiDoc→HTML before Pandoc conversion
9. ✅ **Cleanup**: More test file removal
10. ✅ **Fix**: Pandoc parameter ordering

### Development Focus Areas
- 📝 **PDF Export**: Enhanced with fallback options
- 🎨 **Theming**: Dark/Light mode improvements
- 🔄 **Conversion**: Better format handling
- 🐛 **Bug Fixes**: API usage corrections
- 🧹 **Cleanup**: Code organization

---

## 📋 Quick Reference

### Start the Application
```bash
# From project directory
cd ~/AsciiDoctorArtisan

# Run main version
python3 adp.py

# Run Windows-optimized version
python3 adp_windows.py

# Run performance-optimized version
python3 adp_optimized.py
```

### Essential Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save file |
| `Ctrl+D` | Toggle dark mode |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+F` | Find text |
| `F5` | Toggle dark mode |

---

## 🎯 Project Strengths

### Well-Documented
- ✅ **13+ documentation files**
- ✅ Comprehensive guides for all features
- ✅ Installation instructions for all platforms
- ✅ Troubleshooting documentation

### Multi-Platform
- ✅ Linux/WSL support
- ✅ Windows-optimized version
- ✅ macOS compatibility
- ✅ Platform-specific guides

### Feature-Rich
- ✅ Real-time preview
- ✅ Multi-format conversion
- ✅ Git integration
- ✅ Theme support
- ✅ Session persistence

### Active Development
- ✅ Recent commits (October 2025)
- ✅ Regular bug fixes
- ✅ Feature enhancements
- ✅ Continuous improvement

---

## 💡 Potential Improvements

### Code Organization
- Consider consolidating the 3 Python versions
- Create a unified codebase with platform detection
- Extract common functionality into modules

### Documentation
- Add API documentation for developers
- Create user manual
- Add video tutorials
- Setup GitHub Pages

### Features
- Add spell checking
- Implement find & replace
- Add code snippets
- Create template system
- Add collaborative editing

### Distribution
- Create installers (Windows .exe, macOS .app)
- Package for PyPI
- Add auto-update feature
- Create Docker image

---

## 🛠️ Development Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# Verify installation
./verify.sh  # Linux/Mac

# Windows verification
.\AsciiDocArtisanVerify.ps1
```

### Check Code
```bash
# Syntax check
python3 -m py_compile adp.py

# Check imports
python3 -c "import PySide6, asciidoc3, pypandoc; print('All OK')"
```

---

## 📊 Project Health

### ✅ Strengths
- Active development
- Comprehensive documentation
- Cross-platform support
- Well-structured code
- Git integration

### ⚠️ Areas for Improvement
- Code consolidation (3 versions)
- Test coverage
- Distribution packaging
- Community building (make public?)

---

## 🎯 Use Cases

### Perfect For:
- ✅ Technical writers
- ✅ Documentation specialists
- ✅ Developers writing docs
- ✅ Students and educators
- ✅ Anyone needing AsciiDoc editing

### Scenarios:
- Writing technical documentation
- Creating user manuals
- Authoring books and articles
- Converting from Word to AsciiDoc
- Git-based documentation workflows

---

## 📚 Next Steps

### To Work on This Project:
```bash
# Navigate to project
cd ~/AsciiDoctorArtisan

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 adp.py

# Start coding!
```

### To Understand the Code:
1. Read `ANALYSIS_AND_MVP_PLAN.md`
2. Review `adp.py` (main application)
3. Check `CHANGELOG.md` for history
4. Explore recent commits

### To Contribute:
1. Read `CONTRIBUTING.md`
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 🔗 Quick Links

- 📂 **Project Location**: `/Users/rw/AsciiDoctorArtisan`
- 🌐 **GitHub**: https://github.com/webbwr/AsciiDoctorArtisan
- 📖 **Main Docs**: [README.md](README.md)
- 🚀 **Quick Start**: [QUICK_START.md](QUICK_START.md)
- 📋 **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**🎉 You're now in the AsciiDoctorArtisan project! Ready to work on your professional AsciiDoc toolkit.**

**Made with ❤️ - A Python/PySide6 project for modern documentation** 📝✨
