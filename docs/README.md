# AsciiDoc Artisan Documentation

Welcome to the AsciiDoc Artisan documentation! This directory contains all project documentation organized by category.

## Documentation Structure

### 📐 Architecture (`architecture/`)
Technical specifications and implementation details.

- **SPECIFICATIONS.md** - Complete functional requirements (84 rules)
- **IMPLEMENTATION_REFERENCE.md** - Feature implementation details (v1.5.0)
- **ARCHITECTURAL_ANALYSIS_2025.md** - Architecture analysis and patterns

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

### 📋 Planning (`planning/`)
Project planning and task completion summaries.

- **README.md** - Planning directory overview
- **IMPLEMENTATION_PLAN_v1.7.0.md** - v1.7.0 implementation plan
- **TASK_4_COMPLETION_SUMMARY.md** - Async I/O task completion (v1.6.0)

### 📦 Archive (`archive/`)
Historical project documentation and completed initiatives.

- **README.md** - Archive index and guide
- **REFACTORING_PLAN.md** - Phase 1-3 optimization strategy (Complete)
- **OPTIMIZATION_SUMMARY.md** - Phase 1 technical report (Complete)
- **PHASE_2_SUMMARY.md** - Phase 2 analysis and completion report (Nov 2025)
- **READABILITY_REPORT_20251031.md** - Documentation readability audit (Oct 2025)
- **PROJECT_STATUS_v1.7.0.md** - v1.7.0/v1.7.1 project status report (583 lines)
- **TEST_FAILURE_ANALYSIS_v1.7.1.md** - Test fix documentation (4-phase approach)
- **CHAT_*.md** (4 files) - Historical session reports from v1.7.0 development

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

### 📄 Root Documentation
Key files in the project root:

- **README.md** - Project overview and quick start (v1.7.1)
- **CLAUDE.md** - AI assistant configuration and project context
- **ROADMAP.md** - 2026-2027 strategic plan (v1.7.1 Complete ✅)
- **CHANGELOG.md** - Complete version history (v1.0.0 to v1.7.1)
- **RELEASE_NOTES_v1.7.1.md** - Comprehensive release notes
- **LICENSE** - Project license (MIT)
- **SECURITY.md** - Security policy

---

## Quick Links

### For Users
Start here: [How to Use](user/how-to-use.md)

### For Contributors
Start here: [How to Contribute](developer/how-to-contribute.md)

### For Architects
Start here: [Specifications](architecture/SPECIFICATIONS.md)

### For Security
Start here: [Security Policy](../SECURITY.md)

---

## Recent Updates

### v1.7.1 - 100% Test Coverage (November 2, 2025) ✅
- **Test pass rate:** 100% (82/82 tests passing)
- **Bug fixes:** All 24 test failures fixed (4-phase approach)
- **Documentation:** 770+ lines of new documentation
  - CHANGELOG.md - Complete version history
  - RELEASE_NOTES_v1.7.1.md - User-facing release notes
  - PROJECT_STATUS_v1.7.0.md - Comprehensive status report
  - OLLAMA_INTEGRATION.md - Integration guide
  - TEST_FAILURE_ANALYSIS.md - Test fix documentation
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

*Documentation last organized: November 2, 2025*
