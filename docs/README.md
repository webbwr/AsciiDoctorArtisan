# AsciiDoc Artisan Documentation

Welcome to the AsciiDoc Artisan documentation! This directory contains all project documentation organized by category.

## Documentation Structure

### 📐 Architecture (`architecture/`)
Technical specifications and implementation details.

- **IMPLEMENTATION_REFERENCE.md** - Feature implementation details (v1.5.0)
- **ARCHITECTURAL_ANALYSIS_2025.md** - Architecture analysis and patterns

**Note:** SPECIFICATIONS.md is now in the root directory for easier access.

### 👨‍💻 Developer (`developer/`)
Guides for contributing and developing the project.

- **how-to-contribute.md** - Contribution guidelines
- **PERFORMANCE_PROFILING.md** - Performance profiling guide
- **TEST_COVERAGE_SUMMARY.md** - Test coverage analysis
- **CONFIGURATION.md** - Configuration and setup guide
- **TEST_FIXES_QUICK_REF.md** - Quick reference for test fixes

### 📖 User (`user/`)
User-facing documentation and guides.

- **how-to-use.md** - User guide for all features
- **GITHUB_CLI_INTEGRATION.md** - GitHub CLI integration guide (v1.6.0)
- **OLLAMA_CHAT_GUIDE.md** - AI chat integration guide (v1.7.0)
- **PERFORMANCE_GUIDE.md** - Performance optimization guide (v1.7.0)
- **USER_TESTING_GUIDE.md** - User acceptance testing guide

### 🧪 Testing (`testing/`)
Test suite documentation and analysis.

- **README.md** - Testing directory overview
- **test_development_history.md** - Historical test development
- **test_analysis_2025-11-04.md** - Test suite analysis (Nov 4, 2025)
- **test_fixes_2025-11-04.md** - Test fix documentation (Nov 4, 2025)
- **test_hang_analysis_2025-11-04.md** - Test hang analysis (Nov 4, 2025)
- **test_suite_results_2025-11-04.md** - Test suite results (Nov 4, 2025)
- **STATUS_REPORT_2025-11-04.md** - Test status report (Nov 4, 2025)

### 📦 Archive (`archive/`)
Historical project documentation and completed initiatives.

**48 archived files** covering:
- Test coverage and QA documentation (v1.9.0)
- Test refactoring phases (v1.7.x)
- Chat integration development (v1.7.0)
- Phase completion summaries (v1.5.0-v1.7.0)
- Version-specific documentation (v1.7.0-v1.8.0)
- Optimization and refactoring (v1.4.0-v1.7.0)
- Consolidation and audit reports (v1.7.0+)

See [archive/README.md](archive/README.md) for complete index.

### 🔍 QA (`qa/`)
Quality assurance and testing documentation.

- **README.md** - QA directory overview
- **QA_EXECUTIVE_SUMMARY.md** - QA executive summary
- **QA_GRANDMASTER_AUDIT_2025.md** - Comprehensive QA audit (Oct 2025)
- **QA_INITIATIVE_COMPLETION.md** - QA initiative completion report (Oct 2025)
- **MEMORY_OPTIMIZATION_ANALYSIS.md** - Memory usage analysis (Oct 2025)
- **P0_TEST_FIXES_SUMMARY.md** - Priority 0 test fixes summary

### 🔒 Operations (`operations/`)
Security, deployment, and operational documentation.

- **SECURITY_AUDIT_GUIDE.md** - Security audit system guide
- **SECURITY_AUDIT_IMPLEMENTATION.md** - Security implementation details
- **SECURITY_AUDIT_REPORT.md** - Security audit report

### 🚀 v2.0.0 Planning (Active)
Comprehensive planning for v2.0.0 Advanced Editing features.

**Master Plan:**
- **v2.0.0_MASTER_PLAN.md** - Comprehensive master plan (16 weeks, 280+ tests)

**Feature Plans:**
- **v2.0.0_AUTOCOMPLETE_PLAN.md** - Auto-complete system (24-32h, 85 tests)
- **v2.0.0_SYNTAX_CHECKING_PLAN.md** - Syntax error detection (16-24h, 95 tests)
- **v2.0.0_TEMPLATES_PLAN.md** - Document templates (16-24h, 80 tests)

**Status:** Planning complete (2,774+ lines), implementation Q2-Q3 2026

### 📋 Roadmap & Planning
Project roadmap and planning documentation.

- **ROADMAP_RATIONALIZATION.md** - Comprehensive analysis of historical roadmaps (Nov 5, 2025)

### 📄 Root Documentation
Key files in the project root:

- **README.md** - Project overview and quick start (v1.9.0)
- **SPECIFICATIONS.md** - Functional requirements (107 specs: 84 implemented, 23 planned)
- **CLAUDE.md** - AI assistant configuration and project context
- **ROADMAP.md** - 2026-2027 strategic plan (v1.9.0 Complete ✅)
- **CHANGELOG.md** - Complete version history (v1.0.0 to v1.9.0)
- **LICENSE** - Project license (MIT)
- **SECURITY.md** - Security policy
- **QUICK_START_GUIDE.md** - Quick start guide

---

## Quick Links

### For Users
Start here: [How to Use](user/how-to-use.md)

### For Contributors
Start here: [How to Contribute](developer/how-to-contribute.md)

### For Architects
Start here: [Specifications](../SPECIFICATIONS.md)

### For Security
Start here: [Security Policy](../SECURITY.md)

---

## Recent Updates

### v1.9.0 - Improved Git Integration (November 3, 2025) ✅
- **Git Status Dialog:** File-level details with Modified/Staged/Untracked tabs
- **Quick Commit Widget:** Inline commit with Ctrl+G keyboard shortcut
- **Real-Time Status:** Branch name, file counts, color-coded indicators
- **Test coverage:** 53 tests (97% core test pass rate)
- **Keyboard shortcuts:** Ctrl+G (quick commit), Ctrl+Shift+G (status dialog)

### v1.8.0 - Find & Replace + Spell Checker (November 2, 2025) ✅
- **Find & Replace:** VSCode-style find bar with collapsible replace controls
- **Spell Checker:** Real-time spell checking with pyspellchecker
- **Keyboard shortcuts:** Ctrl+F (find), Ctrl+H (replace), F7 (toggle spell check), F11 (theme toggle)
- **Test coverage:** 54 tests (21 FindBar + 33 SearchEngine)

### v1.7.1 - 100% Test Coverage (November 2, 2025) ✅
- **Test pass rate:** 100% (82/82 tests passing)
- **Bug fixes:** All 24 test failures fixed (4-phase approach)
- **Documentation:** 770+ lines of new documentation
- **Quality:** Production-ready, enterprise-grade
- **Git:** Tagged as v1.7.1, released November 2, 2025

### v1.7.0 - Ollama AI Chat (November 1, 2025) ✅
- **AI Chat:** 4 context modes (document, syntax, general, editing)
- **History:** Persistent chat history (100 message limit)
- **UI:** ChatBarWidget, ChatPanelWidget, ChatManager
- **Worker:** Background threading for non-blocking AI
- **Tests:** 82 comprehensive tests (50 at 91% initially)

### v1.6.0 - GitHub CLI & Type Hints (October 31, 2025) ✅
- **Type hints:** 100% coverage (mypy --strict: 0 errors)
- **Async I/O:** Complete implementation
- **GitHub CLI:** Full integration with PR/Issue management
- **Test coverage:** 60%+ (621+ tests across 74 files)

---

## Documentation Consolidation (November 5, 2025)

**Major cleanup:**
- Deleted 8 obsolete root-level files (temporary progress reports, test logs)
- Merged `docs/archived/` into `docs/archive/` (14 files consolidated)
- Archived 4 docs-level test coverage files (now in archive/)
- Removed duplicate SPECIFICATIONS.md from docs/architecture/
- Updated archive README with comprehensive index (48 files)

**Result:** Clean, organized documentation structure with all historical content preserved in archive.

---

*Documentation last organized: November 5, 2025*
