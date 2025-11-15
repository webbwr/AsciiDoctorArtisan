# AsciiDoc Artisan Documentation

**Last Updated:** November 15, 2025
**Version:** 2.0.2

Welcome to the AsciiDoc Artisan documentation hub. This index will help you find the right documentation for your needs.

---

## Quick Navigation

- [**User Guides**](#user-documentation) - Installation, features, and how-to guides
- [**Developer Docs**](#developer-documentation) - Architecture, contributing, and technical guides
- [**Planning**](#planning-documents) - Future feature roadmaps
- [**Completed Work**](#completed-work) - Session summaries and implementation reports
- [**Reports**](#reports) - QA audits, security reviews, and performance analysis

---

## User Documentation

**Location:** [`user/`](user/)

Guides for end users of AsciiDoc Artisan.

| Document | Description |
|----------|-------------|
| [User Guide](user/user-guide.md) | Complete guide to all features and functionality |
| [GitHub Integration](user/github-integration.md) | How to use GitHub CLI features (PR/Issue management) |
| [Ollama Chat](user/ollama-chat.md) | AI chat assistant with 4 context modes |
| [Performance Tips](user/performance-tips.md) | GPU acceleration, optimization, and performance tuning |
| [User Testing Guide](user/user-testing-guide.md) | Testing features and reporting issues |

---

## Developer Documentation

**Location:** [`developer/`](developer/)

Technical documentation for contributors and developers.

| Document | Description |
|----------|-------------|
| [Contributing Guide](developer/contributing.md) | How to contribute code, tests, and documentation |
| [Architecture](developer/architecture.md) | System architecture, design patterns, and lazy import guide |
| [Configuration](developer/configuration.md) | Development environment setup and configuration |
| [Test Coverage](developer/test-coverage.md) | Current test coverage metrics (96.4%, 3,638 tests) |
| [Performance Profiling](developer/performance-profiling.md) | Profiling tools and performance benchmarks |
| [Security Guide](developer/security-guide.md) | Security best practices and audit procedures |
| [Security Implementation](developer/security-implementation.md) | Security feature implementation details |

**Note:** Test suite evolution history is documented in [ROADMAP.md](../ROADMAP.md)

---

## Planning Documents

**Location:** [`planning/`](planning/)

Future feature roadmaps and implementation plans.

| Document | Description |
|----------|-------------|
| [v2.0.0 Master Plan](planning/v2.0.0-master-plan.md) | Complete roadmap for v2.0.0 release |
| [Autocomplete](planning/v2.0.0-autocomplete.md) | Smart autocomplete and code suggestions |
| [Syntax Checking](planning/v2.0.0-syntax-checking.md) | Real-time AsciiDoc syntax validation |
| [Templates](planning/v2.0.0-templates.md) | Document templates and snippets system |

---

## Completed Work

**Location:** [`completed/`](completed/)

Implementation reports and session summaries for completed work.

| Document | Description |
|----------|-------------|
| [November 6 Complete Summary](completed/2025-11-06-master-summary.md) | 3 sessions: lazy imports, comprehensive cleanup, critical bugfix (5 hours, production-ready) |
| [Issue #15: Duplication Reduction](completed/issue-15-duplication-reduction.md) | Preview handler refactoring using Template Method pattern (70% → <20% duplication) |
| [Issue #16: Test Parametrization](completed/issue-16-test-parametrization-analysis.md) | Analysis of test parametrization opportunities (47% reduction potential) |

---

## Reports

**Location:** [`reports/`](reports/)

Quality assurance, security audits, and performance analysis reports.

| Document | Description |
|----------|-------------|
| [QA Audit](reports/qa-audit.md) | Comprehensive quality assurance audit |
| [Memory Optimization](reports/memory-optimization.md) | Memory usage analysis and optimization recommendations |
| [Security Audit](reports/security-audit.md) | Security assessment and vulnerability analysis |

---

## Documentation Standards

**Complete Guide:** [DOCUMENTATION_STANDARDS.md](DOCUMENTATION_STANDARDS.md)

All documentation follows these standards:

- **Reading Level:** Grade 5.0 or below (Flesch-Kincaid) for user docs
- **Sentence Length:** 10-15 words average (user), 15-20 words (developer)
- **Formatting:** Markdown with consistent headings and tables
- **Code Examples:** Use syntax highlighting and clear explanations
- **Cross-References:** Use relative links between documents
- **Evergreen Naming:** No dates in filenames (use internal versioning)
- **File Organization:** Clear categorization (user/developer/testing/reports)

**Key Principles:**
- Evergreen naming (no date suffixes)
- Archive planning docs when milestones complete
- Delete duplicates immediately
- Quarterly audits for quality
- Version in content, not filename

Validate readability with:
```bash
python3 scripts/readability_check.py docs/path/to/file.md
```

---

## Additional Resources

- **Main Repository:** [GitHub](https://github.com/webbwr/AsciiDoctorArtisan)
- **CLAUDE.md:** Project instructions for AI assistants (in repository root)
- **SPECIFICATIONS_HU.md:** Complete functional requirements (in repository root)
- **ROADMAP.md:** Version roadmap and progress tracking (in repository root)

---

## Contributing to Documentation

Documentation improvements are welcome! See [Contributing Guide](developer/contributing.md) for:

- Documentation style guidelines
- How to add new documentation
- Review and approval process
- Testing documentation changes

---

## Recent Updates

### v1.9.0 - Improved Git Integration (November 3, 2025) ✅
- **Git Status Dialog:** File-level details with Modified/Staged/Untracked tabs
- **Quick Commit Widget:** Inline commit with Ctrl+G keyboard shortcut
- **Real-Time Status:** Branch name, file counts, color-coded indicators
- **Test coverage:** 53 tests (97% core test pass rate)

### v1.8.0 - Find & Replace + Spell Checker (November 2, 2025) ✅
- **Find & Replace:** VSCode-style find bar with collapsible replace controls
- **Spell Checker:** Real-time spell checking with pyspellchecker
- **Keyboard shortcuts:** Ctrl+F, Ctrl+H, F7, F11

### v1.7.1 - 100% Test Coverage (November 2, 2025) ✅
- **Test pass rate:** 100% (82/82 tests passing)
- **Bug fixes:** All 24 test failures fixed
- **Quality:** Production-ready, enterprise-grade

---

## Documentation Refactoring (November 6, 2025)

**Major reorganization:**
- Created logical folder structure: user/, developer/, planning/, completed/, reports/
- Renamed all files to consistent lowercase-hyphen naming
- Removed 61 obsolete/outdated files (70% reduction: 87 → 26 files)
- Consolidated security docs from operations/ to developer/
- Merged testing docs into developer/
- Created comprehensive navigation READMEs

**Result:** Clean, maintainable documentation structure optimized for discoverability.

---

**Questions or Suggestions?**
Open an issue on [GitHub](https://github.com/webbwr/AsciiDoctorArtisan/issues) or submit a pull request.

---

*Documentation last organized: November 6, 2025*
