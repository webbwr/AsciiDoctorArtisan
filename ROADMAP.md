# AsciiDoc Artisan Development Roadmap
## 2026-2027 Strategic Plan

**Last Updated:** October 29, 2025
**Planning Horizon:** 18-24 months
**Based on:** Architectural Analysis 2025 + v1.6.0 Completion Review
**Status:** v1.5.0 ✅ | v1.6.0 ✅ | v1.7.0 PLANNED

---

## Vision Statement

Transform AsciiDoc Artisan into the **definitive AsciiDoc editor** - combining exceptional performance, extensibility, and user experience to become the clear leader in technical document authoring.

**Core Principles:**
1. **Performance First** - Fast startup, responsive UI, efficient rendering
2. **Extensibility** - Plugin architecture for community contributions
3. **Quality** - High test coverage, type safety, comprehensive documentation
4. **User-Centric** - Essential features, intuitive UX, accessibility

---

## Current State (v1.6.0) ✅

### Achievements

**Architecture:**
- Modular design with manager pattern
- 59 source modules (core: 19, ui: 29, workers: 10)
- Main window: 630 lines (down from 1,719)
- Clean separation of concerns

**Performance:**
- Startup: 1.05s (70-79% faster than v1.4.0)
- GPU-accelerated rendering (10-50x faster)
- Block detection: 10-14% improvement
- Predictive rendering: 28% latency reduction

**Quality:**
- Test coverage: 60%+ (up from 34%)
- 68 test files, 481+ total tests
- Only 2 TODOs/FIXMEs
- Comprehensive documentation

**Features:**
- GitHub CLI integration (PR/Issue management)
- Async I/O implementation
- Incremental rendering with caching
- Memory profiling system

### Technical Debt: LOW ✅
- Code duplication: <30%
- Maintainability: HIGH
- Dependencies: Current
- Security: No known issues

---

## Version 1.7.0 (Polish & Essential Features)

**Target Date:** Q1 2026 (January - March)
**Duration:** 2-3 months
**Effort:** 76-108 hours (1 developer, full-time)
**Focus:** Essential text editor features + code quality

### Goals

1. **Add missing essential features**
2. **Complete type hint coverage**
3. **Improve user experience**
4. **Prepare foundation for plugins**
5. **Enhance async I/O integration**

### Tasks

#### Task 1: Find & Replace System ⭐
**Priority:** CRITICAL | **Effort:** 8-12 hours

**Requirements:**
- Find text with regex support
- Replace single or all occurrences
- Case-sensitive/insensitive options
- Whole word matching
- Find in selection
- Replace preview

**Implementation:**
- New: `src/asciidoc_artisan/ui/find_replace_dialog.py` (~300 lines)
- New: `src/asciidoc_artisan/core/search_engine.py` (~200 lines)
- Modify: `src/asciidoc_artisan/ui/main_window.py` (+50 lines)
- Tests: `tests/test_find_replace.py` (25 tests)

**Success Criteria:**
- Ctrl+F opens find dialog
- Ctrl+H opens replace dialog
- Regex patterns work correctly
- All tests pass

---

#### Task 2: Type Hint Completion ⭐
**Priority:** HIGH | **Effort:** 16-24 hours

**Current:** 60% type coverage
**Target:** 100% type coverage

**Approach:**
1. Audit all modules for missing type hints (4 hours)
2. Add type hints to core/ modules (6 hours)
3. Add type hints to ui/ modules (8 hours)
4. Add type hints to workers/ modules (4 hours)
5. Run mypy strict mode, fix issues (4 hours)

**Files to Update:**
- All 59 source modules
- Focus on public APIs first
- Add `from __future__ import annotations` for Python 3.9 compat

**Success Criteria:**
- mypy passes with `--strict`
- All public functions have type hints
- All class attributes typed
- IDE autocomplete improved

---

#### Task 3: Spell Checker Integration ⭐
**Priority:** HIGH | **Effort:** 12-16 hours

**Features:**
- Real-time spell checking
- Underline misspelled words
- Right-click suggestions
- Custom dictionary support
- Language selection

**Implementation:**
- Dependency: `language_tool_python` or `pyspellchecker`
- New: `src/asciidoc_artisan/core/spell_checker.py` (~250 lines)
- New: `src/asciidoc_artisan/ui/spell_checker_ui.py` (~150 lines)
- Modify: `src/asciidoc_artisan/ui/main_window.py` (+30 lines)
- Tests: `tests/test_spell_checker.py` (20 tests)

**Success Criteria:**
- Spell checking works in editor
- Red underlines for errors
- Context menu with suggestions
- Can add to custom dictionary
- Performance: <100ms for typical documents

---

#### Task 4: Enhanced Async I/O ⭐
**Priority:** MEDIUM | **Effort:** 24-32 hours

**Current State:**
- async_file_ops.py exists but underutilized
- Most file operations still synchronous
- Mixed sync/async patterns

**Goals:**
1. Migrate file operations to async (8 hours)
2. Implement async file watcher (8 hours)
3. Add async context managers (4 hours)
4. Integrate with Qt event loop (8 hours)
5. Benchmark and optimize (4 hours)

**Files to Modify:**
- `src/asciidoc_artisan/core/async_file_ops.py` (enhance)
- `src/asciidoc_artisan/core/file_operations.py` (migrate to async)
- `src/asciidoc_artisan/ui/file_handler.py` (use async APIs)
- All file I/O call sites

**Success Criteria:**
- File open/save non-blocking
- Large file loads don't freeze UI
- File watcher detects external changes
- No performance regression
- All tests pass

---

#### Task 5: Telemetry System (Opt-In) ⭐
**Priority:** MEDIUM | **Effort:** 16-24 hours

**Purpose:**
- Understand user behavior
- Identify popular features
- Detect crash patterns
- Guide feature prioritization

**Implementation:**
- Dependency: `sentry-sdk` (errors) + custom analytics
- New: `src/asciidoc_artisan/core/telemetry.py` (~300 lines)
- New: `src/asciidoc_artisan/ui/telemetry_dialog.py` (opt-in UI)
- Config: Settings for telemetry preferences

**Data to Collect (with consent):**
- Feature usage frequency
- Crash reports (stack traces)
- Performance metrics (startup time, render time)
- Document size statistics (anonymized)
- Error patterns

**Privacy:**
- Opt-in only (ask on first launch)
- No personal data
- No document content
- Anonymous user ID
- Open-source collection code

**Success Criteria:**
- Clear opt-in dialog
- Can enable/disable anytime
- Data sent securely
- Privacy policy displayed
- GDPR compliant

---

### Minor Tasks

#### Task 6: Improved Error Messages
**Effort:** 4-6 hours

- User-friendly error dialogs
- Actionable error messages
- Error recovery suggestions
- Log errors to file

#### Task 7: Keyboard Shortcuts Customization
**Effort:** 6-8 hours

- Editable keyboard shortcuts
- Conflict detection
- Import/export shortcuts
- Restore defaults

#### Task 8: Recent Files Improvements
**Effort:** 4-6 hours

- Pin favorite files
- Clear recent files
- Show file paths on hover
- Limit recent files count (configurable)

#### Task 9: Performance Dashboard (Dev Tool)
**Effort:** 8-12 hours

- Show metrics in UI (debug mode)
- Render time graphs
- Memory usage graphs
- Cache hit rates

---

### Success Criteria (v1.7.0)

| Criterion | Target | Priority |
|-----------|--------|----------|
| Find & Replace working | ✅ Yes | CRITICAL |
| Type hint coverage | 100% | HIGH |
| Spell checker integrated | ✅ Yes | HIGH |
| Async I/O complete | ✅ Yes | MEDIUM |
| Telemetry opt-in | ✅ Yes | MEDIUM |
| Test coverage | >70% | HIGH |
| Startup time | <0.9s | MEDIUM |
| User satisfaction | >4.5/5 | HIGH |
| Zero critical bugs | ✅ Yes | CRITICAL |

### Timeline (v1.7.0)

```
Month 1 (Jan 2026):
- Week 1-2: Find & Replace + Spell Checker
- Week 3-4: Type Hints (core + ui modules)

Month 2 (Feb 2026):
- Week 1-2: Enhanced Async I/O
- Week 3-4: Telemetry System + Testing

Month 3 (Mar 2026):
- Week 1-2: Minor tasks + bug fixes
- Week 3-4: Documentation + release prep
```

**Release Target:** March 31, 2026

---

## Version 1.8.0 (Advanced Features & Extensibility)

**Target Date:** Q2-Q3 2026 (April - September)
**Duration:** 4-6 months
**Effort:** 120-172 hours (1 developer, full-time)
**Focus:** Auto-completion, syntax checking, plugin architecture

### Goals

1. **Add advanced editing features**
2. **Implement plugin architecture**
3. **Enable third-party extensions**
4. **Improve multi-level caching**
5. **Add document template system**

### Tasks

#### Task 1: Auto-Complete System ⭐⭐
**Priority:** CRITICAL | **Effort:** 24-32 hours

**Features:**
- AsciiDoc syntax completion
- Attribute name completion
- Cross-reference completion
- Include file completion
- Snippet expansion

**Implementation:**
- Dependency: `jedi` or custom parser
- New: `src/asciidoc_artisan/core/autocomplete.py` (~400 lines)
- New: `src/asciidoc_artisan/ui/completion_popup.py` (~250 lines)
- New: `src/asciidoc_artisan/core/asciidoc_parser.py` (~300 lines)
- Tests: `tests/test_autocomplete.py` (30 tests)

**Completion Types:**
1. **Syntax** - Headings (==), lists (-, *), blocks (----), attributes (:attr:)
2. **Attributes** - Built-in attributes ({doctitle}, {author}, etc.)
3. **Cross-refs** - Section IDs (<<section-id>>)
4. **Includes** - File paths (include::path/file.adoc[])
5. **Snippets** - Common patterns (code block, table, etc.)

**Success Criteria:**
- Ctrl+Space triggers completion
- Context-aware suggestions
- Fuzzy matching works
- Performance: <50ms for completion
- Works with large documents

---

#### Task 2: Syntax Error Detection ⭐⭐
**Priority:** HIGH | **Effort:** 16-24 hours

**Features:**
- Real-time syntax checking
- Error underlines (red squiggles)
- Warning underlines (yellow squiggles)
- Error explanations on hover
- Quick fixes for common errors

**Implementation:**
- New: `src/asciidoc_artisan/core/syntax_checker.py` (~350 lines)
- New: `src/asciidoc_artisan/ui/error_marker.py` (~200 lines)
- Enhance: `asciidoc_parser.py` (error recovery)
- Tests: `tests/test_syntax_checker.py` (25 tests)

**Error Categories:**
1. **Syntax errors** - Invalid AsciiDoc syntax
2. **Semantic errors** - Undefined cross-references
3. **Style warnings** - Inconsistent heading levels
4. **Best practices** - Missing attributes

**Success Criteria:**
- Errors shown in real-time
- Hover shows explanation
- Quick fixes available
- Doesn't slow down editing
- All tests pass

---

#### Task 3: Plugin Architecture (Phase 1) ⭐⭐⭐
**Priority:** CRITICAL | **Effort:** 40-60 hours

**Goals:**
1. Plugin discovery and loading
2. Basic plugin API
3. Sandboxed execution
4. Plugin lifecycle management

**Architecture:**
```
plugins/
├── __init__.py (plugin manager)
├── api.py (plugin API definitions)
├── loader.py (plugin discovery & loading)
├── sandbox.py (isolated execution)
└── manifest.py (plugin metadata)
```

**Plugin API (v1.0):**
```python
class Plugin:
    """Base plugin class"""
    name: str
    version: str
    author: str

    def on_load(self): pass
    def on_unload(self): pass
    def on_document_open(self, doc: Document): pass
    def on_document_save(self, doc: Document): pass
    def on_menu_requested(self) -> List[MenuItem]: pass
    def on_command(self, command: str, args: dict): pass
```

**Plugin Discovery:**
- Location: `~/.config/AsciiDocArtisan/plugins/`
- Manifest: `plugin.json` in each plugin directory
- Loading: On application startup
- Validation: JSON schema for manifests

**Sandboxing:**
- Restricted file system access
- No network access (without permission)
- Limited Qt API access
- Resource limits (CPU, memory)

**Implementation:**
- Dependency: `pluggy` (plugin framework)
- New directory: `src/asciidoc_artisan/plugins/` (8-10 files)
- New: Plugin manager UI in preferences
- Tests: `tests/test_plugins/` (30+ tests)
- Example plugins: 2-3 sample plugins

**Success Criteria:**
- Plugins load from directory
- Plugin API works
- Sandboxing prevents abuse
- Can enable/disable plugins
- Plugin errors don't crash app
- Documentation for plugin developers

---

#### Task 4: Multi-Level Caching System ⭐
**Priority:** MEDIUM | **Effort:** 24-32 hours

**Current:** Single-level LRU cache (memory only)
**Target:** Multi-level cache (memory + disk + persistent)

**Architecture:**
```
Cache Hierarchy:
L1: Memory (LRU, 100 blocks, hot data)
L2: Disk (SSD, 1000 blocks, warm data)
L3: Persistent (across sessions, user's most-edited docs)
```

**Implementation:**
- New: `src/asciidoc_artisan/core/multi_level_cache.py` (~400 lines)
- Enhance: `incremental_renderer.py` (use multi-level cache)
- New: Cache statistics and management UI
- Tests: `tests/test_multi_level_cache.py` (25 tests)

**Features:**
1. **Memory cache** - Existing LRU cache
2. **Disk cache** - Serialize to `~/.cache/AsciiDocArtisan/`
3. **Persistent cache** - Recent documents cached
4. **Smart prefetching** - Preload likely-needed blocks
5. **Cache management** - Clear cache, view stats

**Success Criteria:**
- Cache persists across sessions
- Disk cache speeds up reopened docs
- Prefetching reduces latency
- Cache size configurable
- Performance: <5ms cache lookup

---

#### Task 5: Document Templates System ⭐
**Priority:** MEDIUM | **Effort:** 16-24 hours

**Features:**
- Template library (built-in templates)
- Custom template creation
- Template variables ({{author}}, {{date}})
- Template categories
- Import/export templates

**Built-in Templates:**
1. **Article** - Standard article structure
2. **Book** - Multi-chapter book
3. **Report** - Technical report
4. **README** - Software README
5. **Manual** - User manual
6. **Slides** - Presentation

**Implementation:**
- New: `src/asciidoc_artisan/templates/` (template files)
- New: `src/asciidoc_artisan/ui/template_dialog.py` (~300 lines)
- New: `src/asciidoc_artisan/core/template_engine.py` (~250 lines)
- Tests: `tests/test_templates.py` (20 tests)

**Template Format:**
```
---
name: Article Template
category: General
author: AsciiDoc Artisan
version: 1.0
---
= {{title}}
{{author}} <{{email}}>
{{date}}

== Introduction
[Content here]
```

**Success Criteria:**
- File → New from Template works
- Variables replaced correctly
- Can create custom templates
- Template preview available
- All tests pass

---

### Minor Tasks (v1.8.0)

#### Task 6: Improved Git Integration
**Effort:** 8-12 hours

- Show Git status in status bar
- Color code modified/new files
- Quick commit dialog
- Git branch switching

#### Task 7: Export Presets
**Effort:** 6-8 hours

- Save export configurations
- One-click export with preset
- Share presets

#### Task 8: Editor Themes
**Effort:** 8-12 hours

- Syntax highlighting themes
- Import/export themes
- Theme preview
- Community theme sharing

---

### Success Criteria (v1.8.0)

| Criterion | Target | Priority |
|-----------|--------|----------|
| Auto-complete working | ✅ Yes | CRITICAL |
| Syntax checking active | ✅ Yes | HIGH |
| Plugin API released | ✅ v1.0 | CRITICAL |
| Multi-level caching | ✅ Yes | MEDIUM |
| Template system | ✅ Yes | MEDIUM |
| 5+ community plugins | ✅ Yes | HIGH |
| Test coverage | >75% | HIGH |
| Startup time | <0.8s | MEDIUM |
| User satisfaction | >4.6/5 | HIGH |

### Timeline (v1.8.0)

```
Month 1-2 (Apr-May 2026):
- Auto-complete system
- Syntax error detection

Month 3-4 (Jun-Jul 2026):
- Plugin architecture (Phase 1)
- Plugin API documentation

Month 5-6 (Aug-Sep 2026):
- Multi-level caching
- Document templates
- Testing & bug fixes
```

**Release Target:** September 30, 2026

---

## Version 2.0.0 (Next-Generation Architecture)

**Target Date:** Q4 2026 - Q2 2027 (October 2026 - June 2027)
**Duration:** 8-12 months
**Effort:** 360-500 hours (2 developers, full-time)
**Focus:** LSP, multi-core, marketplace, collaboration

### Goals

1. **Implement Language Server Protocol**
2. **Enable multi-core rendering**
3. **Launch plugin marketplace**
4. **Add collaborative editing (Phase 1)**
5. **Cloud integration**

### Major Tasks

#### Task 1: Language Server Protocol (LSP) ⭐⭐⭐
**Priority:** CRITICAL | **Effort:** 80-120 hours

**Goals:**
- Full LSP implementation for AsciiDoc
- IDE integration (VS Code, IntelliJ, etc.)
- Advanced language features

**LSP Features:**
1. **Auto-completion** - Symbols, attributes, cross-refs
2. **Go to Definition** - Jump to headings, includes
3. **Find References** - Find all uses of anchor
4. **Hover** - Show attribute values, anchor targets
5. **Diagnostics** - Syntax errors, warnings
6. **Document Symbols** - Outline view
7. **Rename** - Refactor IDs and attributes
8. **Code Actions** - Quick fixes

**Implementation:**
- Dependency: `pygls` (LSP server framework)
- New: `src/asciidoc_artisan/lsp/` directory (10-15 files)
- Separate process: `asciidoc-lsp-server` executable
- VS Code extension: `asciidoc-artisan-lsp`
- Tests: `tests/test_lsp/` (50+ tests)

**Benefits:**
- Use AsciiDoc Artisan from any editor
- Broader audience reach
- Community contributions easier
- Standardized language support

---

#### Task 2: Multi-Core Rendering ⭐⭐⭐
**Priority:** HIGH | **Effort:** 60-80 hours

**Current:** Single-threaded rendering
**Target:** Parallel rendering across CPU cores

**Architecture:**
```
Main Thread
  ├→ Coordinator: Split document into chunks
  ├→ Worker Pool: N processes (multiprocessing)
  │   ├→ Process 1: Render blocks 0-99
  │   ├→ Process 2: Render blocks 100-199
  │   └→ Process N: Render blocks 900-999
  └→ Aggregator: Combine results → final HTML
```

**Implementation:**
- New: `src/asciidoc_artisan/workers/parallel_renderer.py` (~500 lines)
- New: `src/asciidoc_artisan/workers/render_coordinator.py` (~300 lines)
- Modify: `preview_worker.py` (use parallel renderer for large docs)
- Tests: `tests/test_parallel_rendering.py` (30 tests)

**Optimizations:**
- Automatic chunk sizing based on document size
- Process pool reuse (avoid startup overhead)
- Shared memory for rendered blocks
- Work-stealing queue for load balancing

**Success Criteria:**
- 3-5x faster rendering for large documents (1000+ sections)
- Scales with CPU cores
- No race conditions
- Memory usage acceptable
- All tests pass

---

#### Task 3: Plugin Marketplace ⭐⭐
**Priority:** HIGH | **Effort:** 40-60 hours

**Features:**
- Browse plugins in-app
- Install/update/uninstall plugins
- Plugin ratings and reviews
- Search and categories
- Featured plugins

**Architecture:**
```
Client (AsciiDoc Artisan)
  ↓
Plugin API (REST)
  ↓
Backend (Flask or FastAPI)
  ↓
Database (PostgreSQL)
  ↓
Storage (S3 for plugin .zip files)
```

**Implementation:**
- Backend: Separate repository (`asciidoc-artisan-marketplace`)
- Client: `src/asciidoc_artisan/plugins/marketplace.py` (~400 lines)
- UI: `src/asciidoc_artisan/ui/marketplace_dialog.py` (~350 lines)
- Tests: Client-side only (30 tests)

**Security:**
- Plugin code signing (GPG signatures)
- Automated security scanning
- User reviews and ratings
- Verified developers badge

**Success Criteria:**
- Browse/install works in-app
- Plugins update automatically (opt-in)
- Security scanning active
- 20+ plugins at launch
- Documentation for publishers

---

#### Task 4: Collaborative Editing (Phase 1) ⭐⭐⭐
**Priority:** MEDIUM | **Effort:** 120-160 hours

**Goals:**
- Real-time multi-user editing
- Conflict-free merging
- Presence indicators (who's editing)
- Chat (optional)

**Architecture:**
- Algorithm: **CRDT** (Conflict-free Replicated Data Type)
- Backend: WebSocket server (FastAPI + WebSockets)
- Client: WebSocket connection + sync engine

**Implementation:**
- Dependency: `y-py` or `pycrdt` (CRDT library)
- New: `src/asciidoc_artisan/collaboration/` directory (12-15 files)
- Backend: Separate repository (`asciidoc-artisan-collab-server`)
- Tests: `tests/test_collaboration/` (40+ tests)

**Features (Phase 1):**
1. **Real-time sync** - Changes appear instantly
2. **Presence** - See who's online
3. **Cursor position** - See where others are editing
4. **Automatic conflict resolution** - CRDT merges automatically
5. **Offline support** - Sync when reconnected

**Success Criteria:**
- 2+ users can edit simultaneously
- No data loss
- Merge conflicts resolved automatically
- Latency <100ms for sync
- Works offline

---

#### Task 5: Cloud Integration ⭐
**Priority:** LOW | **Effort:** 60-80 hours

**Features:**
- Cloud storage (Dropbox, Google Drive, OneDrive)
- Automatic sync
- Version history
- Backup and restore

**Implementation:**
- Dependencies: `dropbox`, `google-api-python-client`, `onedrivesdk`
- New: `src/asciidoc_artisan/cloud/` directory (8-10 files)
- UI: Cloud storage settings in preferences
- Tests: `tests/test_cloud/` (25 tests)

**Success Criteria:**
- Connect to cloud services
- Automatic sync on save
- Conflict detection
- Version history accessible
- Offline mode works

---

### Minor Tasks (v2.0.0)

#### Task 6: Advanced Export Options
**Effort:** 12-16 hours

- Custom CSS for HTML export
- PDF styling options
- EPUB metadata
- Batch export

#### Task 7: Accessibility Improvements
**Effort:** 16-24 hours

- Screen reader support
- Keyboard navigation
- High contrast mode
- Font scaling

#### Task 8: Mobile Companion App (Research)
**Effort:** 40-60 hours (research + proof of concept)

- View documents on mobile
- Light editing
- Sync with desktop

---

### Success Criteria (v2.0.0)

| Criterion | Target | Priority |
|-----------|--------|----------|
| LSP implemented | ✅ Yes | CRITICAL |
| Multi-core rendering | ✅ Yes | HIGH |
| Plugin marketplace live | ✅ Yes | HIGH |
| Collaborative editing (Phase 1) | ✅ Yes | MEDIUM |
| Cloud integration | ✅ Yes | LOW |
| 50+ plugins available | ✅ Yes | HIGH |
| Test coverage | >80% | HIGH |
| Startup time | <0.7s | MEDIUM |
| User satisfaction | >4.7/5 | HIGH |

### Timeline (v2.0.0)

```
Phase 1 (Oct-Dec 2026): LSP + Multi-Core
- LSP server implementation
- Multi-core rendering
- Testing and optimization

Phase 2 (Jan-Mar 2027): Marketplace + Collab
- Plugin marketplace backend
- Collaborative editing (Phase 1)
- Beta testing

Phase 3 (Apr-Jun 2027): Polish + Release
- Cloud integration
- Bug fixes
- Documentation
- v2.0.0 release
```

**Release Target:** June 30, 2027

---

## Beyond v2.0.0 (Future Vision)

### v2.1.0+: Advanced Collaboration
- Video/audio calls in editor
- Document annotations and comments
- Review and approval workflows
- Team workspaces

### v2.2.0+: AI Integration
- AI-powered writing suggestions
- Automatic formatting
- Content generation
- Translation assistance

### v2.3.0+: Mobile Apps
- Native iOS app
- Native Android app
- Full feature parity with desktop
- Cross-platform sync

### v3.0.0+: Platform Evolution
- Web-based version (Electron or Tauri)
- Self-hosted server option
- Enterprise features (SSO, LDAP, audit logs)
- White-label licensing

---

## Performance Budget

### Targets by Version

| Metric | v1.6.0 (Current) | v1.7.0 | v1.8.0 | v2.0.0 |
|--------|------------------|--------|--------|--------|
| Startup Time | 1.05s | 0.9s | 0.8s | 0.7s |
| Preview (small, <100 sections) | 150-200ms | 100-150ms | 80-120ms | 60-100ms |
| Preview (large, 1000+ sections) | 600-750ms | 500-650ms | 300-500ms | 200-300ms |
| Memory (idle) | 60-100MB | 50-80MB | 45-75MB | 40-60MB |
| Test Coverage | 60% | 70% | 75% | 80% |
| Type Coverage | 60% | 100% | 100% | 100% |

---

## Resource Requirements

### Development Effort

| Version | Developer Months | Calendar Months | Team Size |
|---------|------------------|-----------------|-----------|
| v1.7.0 | 2-3 | 2-3 | 1 FTE |
| v1.8.0 | 4-6 | 4-6 | 1 FTE |
| v2.0.0 | 12-16 | 8-12 | 2 FTE |
| **Total** | **18-25** | **14-21** | **1-2 FTE** |

### Budget Estimates (Rough)

**Assumptions:**
- Developer rate: $75/hour (experienced Python/Qt developer)
- Cloud costs: $50/month (marketplace + collab server)

| Version | Development Cost | Infrastructure Cost | Total |
|---------|------------------|---------------------|-------|
| v1.7.0 | $5,700-$8,100 | $150 (3 months) | $5,850-$8,250 |
| v1.8.0 | $9,000-$12,900 | $300 (6 months) | $9,300-$13,200 |
| v2.0.0 | $27,000-$37,500 | $600 (12 months) | $27,600-$38,100 |
| **Total** | **$41,700-$58,500** | **$1,050** | **$42,750-$59,550** |

---

## Risk Management

### High-Risk Items

1. **Plugin Security**
   - **Risk:** Malicious plugins compromise user systems
   - **Mitigation:** Sandboxing, code review, marketplace moderation
   - **Contingency:** Kill switch to disable plugins remotely

2. **LSP Complexity**
   - **Risk:** LSP implementation is complex, may delay release
   - **Mitigation:** Use proven libraries (pygls), incremental implementation
   - **Contingency:** Ship with subset of LSP features in v2.0.0

3. **Collaborative Editing Data Loss**
   - **Risk:** Sync issues cause data loss
   - **Mitigation:** Extensive testing, automatic backups, version history
   - **Contingency:** Disable collab feature if critical bugs found

### Medium-Risk Items

4. **Multi-Core Performance**
   - **Risk:** Overhead negates performance gains
   - **Mitigation:** Benchmark thoroughly, optimize chunk size
   - **Contingency:** Fall back to single-threaded for small docs

5. **Type Hint Migration**
   - **Risk:** Breaking changes during type hint addition
   - **Mitigation:** Comprehensive test suite, gradual migration
   - **Contingency:** Type hints are non-breaking, can fix iteratively

### Low-Risk Items

6. **Find & Replace**
   - **Risk:** Minimal, well-understood feature
   - **Mitigation:** Use standard regex library, extensive tests
   - **Contingency:** Easy to fix bugs as found

7. **Spell Checker**
   - **Risk:** Minimal, using battle-tested library
   - **Mitigation:** Use language_tool_python or pyspellchecker
   - **Contingency:** Can disable if performance issues arise

---

## Success Metrics & KPIs

### User Acquisition

| Metric | v1.7.0 Target | v1.8.0 Target | v2.0.0 Target |
|--------|---------------|---------------|---------------|
| GitHub Stars | +100 | +300 | +500 |
| Weekly Downloads | 500 | 1,500 | 5,000 |
| Active Users | 1,000 | 3,000 | 10,000 |
| Plugin Downloads | - | 5,000 | 50,000 |

### User Engagement

| Metric | v1.7.0 Target | v1.8.0 Target | v2.0.0 Target |
|--------|---------------|---------------|---------------|
| Daily Active Users | 200 | 600 | 2,000 |
| Avg Session Length | 30 min | 45 min | 60 min |
| Retention (30-day) | 40% | 50% | 60% |
| NPS Score | >40 | >50 | >60 |

### Quality Metrics

| Metric | v1.7.0 Target | v1.8.0 Target | v2.0.0 Target |
|--------|---------------|---------------|---------------|
| Bug Reports/Month | <10 | <8 | <5 |
| Critical Bugs | 0 | 0 | 0 |
| Crash Rate | <0.1% | <0.05% | <0.01% |
| User Satisfaction | >4.5/5 | >4.6/5 | >4.7/5 |

---

## Competitive Positioning

### Target Position Evolution

**v1.7.0:** "The fastest AsciiDoc editor"
- Focus: Performance + essential features
- Compete with: AsciidocFX (speed), VS Code (features)

**v1.8.0:** "The most extensible AsciiDoc editor"
- Focus: Plugin ecosystem
- Compete with: VS Code (extensibility), Atom (plugins)

**v2.0.0:** "The definitive AsciiDoc platform"
- Focus: LSP + collaboration
- Compete with: Google Docs (collab), VS Code (LSP)

### Unique Selling Points

**Current (v1.6.0):**
1. ✅ Fastest startup (1.05s vs 5-10s for AsciidocFX)
2. ✅ GPU acceleration (10-50x faster preview)
3. ✅ Lightweight (60-100MB vs 500MB+ for Electron apps)
4. ✅ Native UI (Qt, not web-based)

**Future (v2.0.0):**
1. ✨ First AsciiDoc LSP server
2. ✨ Real-time collaboration
3. ✨ Thriving plugin ecosystem
4. ✨ Multi-platform (desktop + web + mobile)

---

## Community & Ecosystem

### Plugin Ecosystem Goals

**v1.8.0 Launch (Sep 2026):**
- 20+ plugins available
- 5+ plugin developers
- Plugin documentation complete
- Marketplace operational

**v2.0.0 Milestone (Jun 2027):**
- 50+ plugins available
- 20+ plugin developers
- Active plugin marketplace
- Community forums active

**v2.1.0+ Vision:**
- 200+ plugins
- Plugin revenue sharing
- Enterprise plugins
- Verified developer program

### Community Building

**Initiatives:**
1. **Documentation** - Comprehensive guides for users and developers
2. **Tutorials** - Video tutorials on YouTube
3. **Blog** - Monthly development updates
4. **Discord** - Community chat server
5. **Contributor Guide** - Lower barrier to contribution
6. **Bounties** - Pay for critical features/bugs
7. **Sponsorship** - GitHub Sponsors, Patreon

---

## Conclusion

This roadmap represents an ambitious 18-24 month plan to transform AsciiDoc Artisan from an excellent editor into **the definitive AsciiDoc platform**.

**Core Strategy:**
1. **v1.7.0:** Polish the basics, achieve feature parity
2. **v1.8.0:** Enable extensibility, build ecosystem
3. **v2.0.0:** Lead the market with LSP and collaboration

**Success Factors:**
- Strong architectural foundation (v1.5.0-v1.6.0) ✅
- Low technical debt ✅
- Engaged development team ✅
- Clear user demand 🎯
- Competitive advantages (performance, native UI) ✅

**Estimated Success Probability: 85%+**

The project is well-positioned for success. The architecture is solid, performance is excellent, and the codebase is maintainable. With focused execution on this roadmap, AsciiDoc Artisan can become the clear leader in AsciiDoc editing tools.

---

**Roadmap Status:** ACTIVE
**Last Updated:** October 29, 2025
**Next Review:** After v1.7.0 release (Q1 2026)
**Maintainer:** Development Team + Claude Code
**Questions:** See CLAUDE.md or GitHub Discussions

---

*"Make it work, make it right, make it fast, make it yours."*
*— AsciiDoc Artisan Development Philosophy*
