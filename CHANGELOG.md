# Changelog

All notable changes to AsciiDoc Artisan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Settings dataclass for structured configuration management (FR-045)
- Persistent splitter position between editor and preview panes (FR-045)
- Persistent font size across application sessions (FR-043)
- Comprehensive test suite with pytest infrastructure
- Unit tests for Settings dataclass persistence
- Unit tests for atomic file operations
- Unit tests for path sanitization security
- pytest.ini configuration for test organization
- Test markers for unit, integration, and GUI tests

### Changed
- **BREAKING**: Removed Claude AI integration (out of specification scope)
- Refactored settings management to use dataclass pattern
- Settings now stored in Settings dataclass matching specification
- All configuration persistence uses Settings.to_dict/from_dict
- Updated requirements.txt to remove anthropic and requests dependencies
- Improved README.md to focus on specification features only
- Enhanced settings restoration on application startup

### Removed
- Claude AI integration files (claude_client.py, claude_integration_example.py)
- Claude AI integration directory (claude-integration/)
- Claude AI documentation (CLAUDE_INTEGRATION.md, CLAUDE_MIGRATION_GUIDE.md, ANTHROPIC_SDK_INTEGRATION_SUMMARY.md)
- anthropic>=0.71.0 dependency
- requests>=2.31.0 dependency

### Fixed
- Settings now properly persist splitter sizes between sessions
- Font size now properly persists between application sessions
- Configuration file location now uses platform-appropriate paths

### Technical Improvements
- Code now fully aligned with project specification (.specify/specs/)
- All settings variables migrated from instance variables to Settings dataclass
- Added 14 passing unit tests with 100% success rate
- Improved code maintainability with structured settings management

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
