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

- **REFACTORING_PLAN.md** - Phase 1-3 optimization strategy (Complete)
- **OPTIMIZATION_SUMMARY.md** - Phase 1 technical report (Complete)
- **PHASE_2_SUMMARY.md** - Phase 2 analysis and completion report (Nov 2025)
- **READABILITY_REPORT_20251031.md** - Documentation readability audit (Oct 2025)

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

- **README.md** - Project overview and quick start (v1.7.0)
- **CLAUDE.md** - AI assistant configuration and project context
- **ROADMAP.md** - 2026-2027 strategic plan (Phase 1 Complete ✅)
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

### v1.7.1 Phase 2 Optimization (November 1, 2025) ✅
- **String interning:** Expanded from 17 to 67+ tokens
- **Memory usage:** Additional 15-25% reduction for string allocations
- **Worker pool migration:** Deferred (architectural complexity)
- **Async I/O completion:** Deferred (minimal gains)
- **Time invested:** 2 hours (smart, focused approach)

### v1.7.0 Phase 1 Optimization (November 1, 2025) ✅
- **Preview latency:** 40-50% faster
- **Memory usage:** 30% reduction
- **CSS generation:** Zero overhead
- **Documentation:** PERFORMANCE_GUIDE.md added
- **Archives:** Optimization docs moved to archive/

### v1.6.0 Completion (October 31, 2025) ✅
- **Type hints:** 100% coverage (mypy --strict: 0 errors)
- **Async I/O:** Complete implementation
- **GitHub CLI:** Full integration with PR/Issue management
- **Test coverage:** 60%+ (621+ tests across 74 files)

---

*Documentation last organized: November 1, 2025*
