# Changelog

All notable changes to AsciiDoc Artisan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository cleanup (removed unused template files)
- MIT License
- This CHANGELOG file
- Comprehensive code analysis and MVP plan document

### Changed
- Improved configuration file handling
- Enhanced input sanitization for Git commands
- Better user-facing error messages

### Fixed
- Configuration file location now uses platform-appropriate paths

## [1.0.0-alpha] - 2025-10-19

### Added
- Initial release of AsciiDoc Artisan
- PySide6-based desktop GUI application
- Live HTML preview of AsciiDoc content
- Real-time rendering with AsciiDoc3
- File operations (Open, Save, Save As)
- DOCX import via Pandoc conversion
- Git integration (Commit, Pull, Push)
- Clipboard conversion (Word/HTML to AsciiDoc)
- Dark/Light theme toggle
- Font zoom controls (Ctrl+/Ctrl-)
- Settings persistence (window state, theme, last directory)
- Cross-platform support (Windows, Linux, macOS)
- Comprehensive documentation
- Setup and verification scripts for Linux/WSL
- PowerShell verification script for Windows
- Python dependencies management

### Dependencies
- PySide6 >= 6.9.0 (Qt GUI framework)
- asciidoc3 (AsciiDoc processing)
- pypandoc (Document conversion)
- System: git, pandoc

### Known Limitations
- Single file editing only (no project/multi-file support)
- No syntax highlighting in editor
- No find/replace functionality
- No undo/redo beyond Qt default
- No export to PDF (only HTML preview)
- Git operations require repository to be pre-configured

---

## Release Notes Format

### Types of Changes
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

---

[Unreleased]: https://github.com/webbwr/AsciiDoctorArtisan/compare/v1.0.0-alpha...HEAD
[1.0.0-alpha]: https://github.com/webbwr/AsciiDoctorArtisan/releases/tag/v1.0.0-alpha
