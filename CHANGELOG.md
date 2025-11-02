# Changelog

All notable changes to AsciiDoc Artisan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2025-11-02 (IN PROGRESS)

### Added
- **Find & Replace System** - Fast text search and replacement
  - SearchEngine with regex support (`core/search_engine.py`, 420 lines)
  - Non-modal find bar at bottom of window (`ui/find_bar_widget.py`, 380+ lines)
  - Keyboard shortcuts: Ctrl+F (Find), Ctrl+H (Replace), F3 (Next), Shift+F3 (Previous)
  - Live search with yellow highlighting for all matches
  - Match counter display (e.g., "5 of 23")
  - Collapsible replace controls with toggle button
  - Replace All with confirmation dialog
  - Case-sensitive and whole word search options
  - Wrap-around navigation support
- **Spell Checker Integration** - Real-time spell checking with suggestions
  - SpellChecker engine with pyspellchecker (`core/spell_checker.py`, 306 lines)
  - SpellCheckManager UI integration (`ui/spell_check_manager.py`, 368 lines)
  - Red squiggly underlines for misspelled words
  - Right-click context menu with up to 5 suggestions
  - "Add to Dictionary" (persists across sessions)
  - "Ignore Word" (session only)
  - F7 keyboard shortcut to toggle spell checking on/off
  - Debounced checking (500ms delay after typing stops)
  - Multiple language support (en, es, fr, de, etc.)
  - Custom dictionary persistence in settings
- **F11 Theme Toggle** - Quick keyboard shortcut for dark/light mode
  - F11 key toggles between Dark and Light themes
  - Bidirectional toggle (Dark ↔ Light ↔ Dark)
  - Syncs with View menu checkbox
  - Updates all UI elements (editor, preview, chat, labels)
  - Persists theme preference across restarts
- **Privacy-First Telemetry System** - Optional usage analytics (opt-in only)
  - TelemetryCollector with local-only storage (`core/telemetry_collector.py`, 464 lines)
  - GDPR-compliant opt-in dialog (`ui/telemetry_opt_in_dialog.py`, 262 lines)
  - Anonymous session IDs (UUIDs, no personal data)
  - Data sanitization (removes paths, emails, IPs)
  - 30-day retention with auto-rotation
  - 10MB max file size with auto-cleanup
  - Tracks: feature usage, error patterns, performance metrics, system info
  - Does NOT track: names, emails, IPs, document content, file paths, keystrokes
  - Three-option dialog: Accept, Decline, Remind Me Later
  - Easy opt-out anytime in Settings

### Dependencies
- Added `pyspellchecker>=0.8.0` for spell checking functionality

### Changed
- Enhanced Settings with 6 new fields:
  - Spell check (3 fields):
    - `spell_check_enabled: bool` (default: True)
    - `spell_check_language: str` (default: "en")
    - `spell_check_custom_words: List[str]` (persistent)
  - Telemetry (3 fields):
    - `telemetry_enabled: bool` (default: False, opt-in only)
    - `telemetry_session_id: Optional[str]` (anonymous UUID)
    - `telemetry_opt_in_shown: bool` (dialog shown flag)
- Updated keyboard shortcuts:
  - F7: Toggle spell checking
  - F11: Toggle dark/light theme (replaces Ctrl+D)
  - Ctrl+F: Open find bar
  - Ctrl+H: Open find & replace
  - F3: Find next
  - Shift+F3: Find previous
- Enhanced `action_manager.py` with Qt.Key imports for function keys

### Testing
- Added 54 tests for Find & Replace system
  - 21 tests for FindBarWidget (UI components)
  - 33 tests for SearchEngine (core logic)
- Spell checker core functionality verified
  - Word checking, suggestions, dictionary management
  - Performance: <100ms per spell check operation
- Added 31 tests for Telemetry System
  - Event tracking, buffering, data sanitization
  - Privacy protections, file rotation, destruction
  - 100% test pass rate

### Documentation
- Updated README.md with Find & Replace and Spell Check sections
- Updated ROADMAP.md with v1.8.0 progress (3/3 tasks complete)
- Updated CLAUDE.md with v1.8.0 feature details
- Updated docs/user/how-to-use.md with new shortcuts and features
- Updated CHANGELOG.md with complete v1.8.0 documentation
- All documentation maintains Grade 5.0 reading level

### Git Commits (November 2, 2025)
- `be8768e` - SearchEngine core logic (Phase 1)
- `fee32ef` - FindBarWidget UI (Phase 2)
- `d99ed32` - Find/Replace integration (Phase 3)
- `4757c91` - Replace functionality (Phase 4)
- `8e1d95f` - Find/Replace documentation
- `d0ff4dc` - README and ROADMAP updates
- `0fefa20` - Spell checker implementation
- `ee1ca6a` - Spell checker linting fixes
- `19afce1` - Spell checker documentation
- `276781f` - F11 keyboard shortcut for theme toggle
- `a3d78cd` - Documentation updates for v1.8.0
- `cf45b77` - ROADMAP and CHANGELOG updates
- `1fe3ee0` - Privacy-First Telemetry System

## [1.7.4] - 2025-11-02

### Security
- **CRITICAL FIX:** Path traversal vulnerability (Issue #8)
  - Fixed sanitize_path() to check '..' BEFORE resolve()
  - Added optional allowed_base parameter for whitelist validation
  - Prevents attacks like '/tmp/../../../etc/passwd'

### Fixed
- Path sanitization logic now detects directory traversal attempts correctly
- Added 8 comprehensive security tests (11 total path sanitization tests)

### Documentation
- Created SECURITY_AUDIT_REPORT.md (comprehensive security audit of issues #6-#10)
- All 5 GitHub security issues verified and closed (#6, #7, #8, #9, #10)

### Changed
- sanitize_path() signature: now accepts optional allowed_base parameter
- Enhanced test coverage for path security (100% for file_operations)

## [1.7.1] - 2025-11-02

### Added
- Comprehensive Ollama integration documentation (`docs/OLLAMA_INTEGRATION.md`)
- Complete project status report (`PROJECT_STATUS_v1.7.0.md`)
- Enhanced requirements.txt with detailed Ollama installation instructions

### Fixed
- All 24 test failures in Ollama Chat feature test suite (100% pass rate achieved)
- Phase 1: 8 method name mismatches between tests and implementation
- Phase 2: 2 mock configuration issues (Mock return_value settings)
- Phase 3: 10 missing methods in ChatManager (implemented 6 helper methods)
- Phase 4: 4 logic/behavior test mismatches (Qt visibility inheritance)

### Changed
- Test suite now at 100% pass rate (82/82 tests passing, up from 91%)
- Improved test coverage for all Ollama Chat components
- Updated documentation to reflect production-ready status

### Documentation
- Created comprehensive integration guide (187 lines)
- Created complete project status report (583 lines)
- Updated TEST_FAILURE_ANALYSIS.md with completion status
- Enhanced requirements.txt with platform-specific installation instructions

## [1.7.0] - 2025-11-01

### Added
- **Ollama AI Chat Integration** - Interactive AI chat with 4 context modes
  - Document Q&A mode - Ask questions about current document
  - Syntax Help mode - AsciiDoc formatting assistance
  - General Chat mode - General questions and conversations
  - Editing Suggestions mode - Document improvement feedback
- Background worker thread (`OllamaChatWorker`) for non-blocking AI processing
- Chat UI components:
  - `ChatBarWidget` - User input interface with model/mode selectors
  - `ChatPanelWidget` - Message display with scrollable history
  - `ChatManager` - Orchestration layer for bar ↔ worker ↔ panel communication
- Persistent chat history (100 message limit, JSON serialization)
- Cancellation support with 60-second timeout for AI operations
- Document context injection with debouncing (2KB max)
- Model switching (gnokit/improve-grammer, deepseek-coder, qwen3, etc.)

### Changed
- Added `ollama>=0.4.0` as production dependency
- Enhanced settings with Ollama chat configuration options
- Improved UI layout to accommodate chat components

### Documentation
- Added Ollama setup instructions to README.md
- Documented 4 context modes and use cases
- Added troubleshooting guide for common Ollama issues

### Testing
- Added 82 comprehensive tests for Ollama Chat feature
  - 27 tests for ChatManager (orchestration)
  - 28 tests for ChatBarWidget (UI controls)
  - 22 tests for OllamaChatWorker (background processing)
  - 5 integration tests (currently skipped, require live Ollama)

## [1.6.0] - 2025-10-31

### Added
- **GitHub CLI Integration** - PR and Issue management
  - Create pull requests from UI
  - List and view PRs with filtering (Open/Closed/Merged/All)
  - Create issues directly from application
  - List and view issues with filtering
  - View repository information
- Type hints completion (mypy --strict: 0 errors, 100% coverage)
- Async I/O with aiofiles for non-blocking file operations
- Predictive rendering system for faster preview updates
- Block detection optimization (10-14% performance improvement)

### Changed
- Migrated to mypy strict mode with full type coverage
- Enhanced GitHub menu with 5 new actions
- Improved performance for large document editing

### Testing
- Added 49 tests for GitHub CLI integration (100% pass rate)
- Added 30 scaffolded tests for GitHub handler

## [1.5.0] - 2025-10-28

### Added
- Lazy import system for heavy modules (3-5x faster startup)
- Worker pool system with task prioritization
- Operation cancellation support (cancel button in status bar)
- Memory profiling and optimization tools

### Changed
- **1.05s startup time** (beats v1.6.0 target of 1.5s)
- Main window refactored from 1,719 to 561 lines (67% reduction)
- Test coverage increased to 60%+ (up from 34%)
- 621+ total tests (+228 new tests since v1.4.0)

### Performance
- Startup: 3-5x faster than v1.4.0
- Preview: Incremental rendering with block cache
- Memory: String interning for memory reduction

## [1.4.1] - 2025-10-20

### Changed
- CSS generation moved from main_window to theme_manager (63 lines reduced)
- Main window size reduced from 1,723 to 1,614 lines
- Further refactoring for code maintainability

## [1.4.0] - 2025-10-15

### Added
- **Full GPU/NPU hardware acceleration** with automatic detection
- GPU-accelerated preview (QWebEngineView) - 10-50x faster rendering
- Software fallback (QTextBrowser) for systems without GPU
- GPU detection caching (24-hour TTL) in `~/.cache/asciidoc_artisan/`
- Document version display in status bar (auto-extracts from :version: or :revnumber:)
- Support for NVIDIA (CUDA/OpenCL/Vulkan), AMD (ROCm/OpenCL/Vulkan), Intel (OpenCL/Vulkan), Intel NPU (OpenVINO)
- WSLg automatic fallback if GPU initialization fails

### Removed
- Grammar checking system (v1.3.0 feature) - performance issues, user feedback
- 2,067 lines of grammar-related code removed

### Changed
- Preview rendering now 70-90% less CPU usage with GPU acceleration
- Automatic hardware detection - no user configuration needed

## [1.3.0] - 2025-09-25

### Added
- Grammar checking system with language-tool-python
- Real-time grammar suggestions in editor
- Configurable grammar rules

### Removed in v1.4.0
- Grammar system removed due to performance issues and user feedback
- Users should use external grammar tools (Grammarly, LanguageTool) via copy/paste

## [1.2.0] - 2025-08-15

### Added
- **Ollama AI for document conversion** - smart format conversion using local AI
- Automatic Pandoc fallback if Ollama unavailable
- Status bar shows active conversion method (AI or Pandoc)
- Model selection: gnokit/improve-grammer (recommended), llama2, mistral, codellama

### Changed
- Document conversion now AI-assisted with better quality
- Settings UI enhanced with Ollama configuration

## [1.1.0] - 2025-07-10

### Changed
- **Major refactoring**: Modularized from monolithic adp.py (1000+ lines)
  - Phase 1: Core utilities → `core/` module
  - Phase 2: Workers → `workers/` module
  - Phase 3: Dialogs → `ui/dialogs.py`
  - Phase 4: Main window → `ui/main_window.py`
  - Phase 5: UI managers → `ui/{menu,theme,status,file,export,git,preview,action,settings,editor_state}_manager.py`
  - Phase 6: Constants consolidated in `core/constants.py`, CSS moved to `theme_manager.py`

### Performance
- PyMuPDF integration for PDF reading (3-5x faster than pdfplumber)
- Incremental rendering with block-based cache (LRU, 100 blocks max)
- Performance hot path optimizations

## [1.0.0] - 2025-06-01

### Added
- Initial release of AsciiDoc Artisan
- Live preview of AsciiDoc documents
- Dark/light theme support
- Document conversion (DOCX, PDF, HTML, Markdown)
- Git integration (pull, commit, push)
- Recent files menu
- Settings persistence (QStandardPaths)
- Cross-platform support (Linux, Windows, macOS)

### Dependencies
- PySide6 6.9.0+ (Qt GUI framework)
- asciidoc3 3.2.0+ (AsciiDoc to HTML)
- pypandoc 1.13+ (document conversion)
- pymupdf 1.23.0+ (PDF reading)

---

## Unreleased

### Planned for v1.7.x
- [ ] Streaming response display for Ollama Chat (real-time updates)
- [ ] Model switching in UI without restart
- [ ] Chat history export (JSON, text formats)
- [ ] Custom system prompts per context mode
- [ ] RAG (Retrieval-Augmented Generation) for large documents

### Planned for v1.8.0
- [ ] Find & Replace system
- [ ] Spell checker integration
- [ ] Telemetry system (opt-in)
- [ ] Worker pool migration (complete)
- [ ] Multiple model support (simultaneous Ollama conversations)
- [ ] Chat branching and conversation trees

---

## Version Format

**Version scheme**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, major feature additions
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes, documentation updates, minor improvements

**Tag format**: `vMAJOR.MINOR.PATCH` (e.g., v1.7.1)

---

## Links

- **Repository**: https://github.com/webbwr/AsciiDoctorArtisan
- **Issues**: https://github.com/webbwr/AsciiDoctorArtisan/issues
- **Documentation**: See `docs/` directory
- **Roadmap**: See `ROADMAP.md`
