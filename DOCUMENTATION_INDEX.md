# AsciiDoc Artisan - Documentation Index

**Last Updated:** November 18, 2025
**Version:** 2.0.4 ✅ Production Ready

Complete guide to all project documentation with quick navigation.

---

## 📘 Essential Documentation (Start Here)

### For Users
- **[README.md](README.md)** - Project overview, installation, and quick start
- **[docs/user/](docs/user/)** - User guides and feature tutorials
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - Complete developer guide and AI assistant instructions
- **[SPECIFICATIONS_HU.md](SPECIFICATIONS_HU.md)** - Human-readable functional requirements (107 FRs)
- **[SPECIFICATIONS_AI.md](SPECIFICATIONS_AI.md)** - AI-optimized specs with test requirements
- **[docs/developer/](docs/developer/)** - Developer guides and API documentation
- **[docs/testing/](docs/testing/)** - Test framework and FR traceability guides

### For Contributors
- **[ROADMAP.md](ROADMAP.md)** - Future plans and feature roadmap
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting
- **[docs/developer/contributing.md](docs/developer/contributing.md)** - Contributing guidelines

---

## 📂 Documentation Organization

### Root Directory
```
README.md                  - Project overview
CLAUDE.md                  - Developer guide (11KB)
SPECIFICATIONS_HU.md       - Human specs (24KB)
SPECIFICATIONS_AI.md       - AI specs (156KB)
CHANGELOG.md               - Version history (21KB)
ROADMAP.md                 - Future planning (11KB)
SECURITY.md                - Security policy
DOCUMENTATION_INDEX.md     - This file
```

### docs/ Directory Structure
```
docs/
├── user/              - User-facing guides and tutorials
├── developer/         - Developer documentation and API guides
├── testing/           - Test framework and traceability docs
│   ├── FR_TEST_MAPPING.md          - FR to test file mapping
│   └── PYTEST_MARKERS_GUIDE.md     - Pytest markers guide
├── reports/           - Analysis, metrics, and audit reports
├── completed/         - Finished milestone documentation
└── archive/           - Historical documentation
    ├── v2.0.0/        - v2.0.0 planning and progress
    ├── v2.0.1/        - v2.0.1 test suite repair
    ├── historical/    - Architecture analyses
    └── snapshots/     - Documentation snapshots
```

### OpenSpec Directory (Feature Planning)
```
openspec/
├── README.md          - OpenSpec workflow guide
└── changes/           - Active feature proposals
```

---

## 📚 Documentation by Category

### Installation & Setup
- [README.md](README.md#installation) - Installation instructions
- [install-asciidoc-artisan.sh](install-asciidoc-artisan.sh) - Linux/Mac installer
- [install-asciidoc-artisan.ps1](install-asciidoc-artisan.ps1) - Windows PowerShell installer
- [requirements.txt](requirements.txt) - Python dependencies

### Specifications & Requirements

**Human-Readable:**
- [SPECIFICATIONS_HU.md](SPECIFICATIONS_HU.md) - Quick reference for all 107 FRs
- Best for: Feature review, implementation status, quick FR lookup

**AI-Optimized:**
- [SPECIFICATIONS_AI.md](SPECIFICATIONS_AI.md) - Complete specs with test requirements
- Best for: AI-assisted development, writing tests, implementation details
- Includes: Acceptance criteria, API contracts, test requirements, dependency graphs

### Features & Usage
- [SPECIFICATIONS_HU.md](SPECIFICATIONS_HU.md) - Complete feature list (107 FRs)
- [docs/user/](docs/user/) - User guides and tutorials
- [CHANGELOG.md](CHANGELOG.md) - Feature history by version

### Development & Architecture
- [CLAUDE.md](CLAUDE.md) - Architecture, patterns, and workflows
- [docs/developer/](docs/developer/) - API docs and development guides
- [docs/developer/architecture.md](docs/developer/architecture.md) - System architecture
- [docs/developer/contributing.md](docs/developer/contributing.md) - Contribution guide
- [ROADMAP.md](ROADMAP.md) - Future features and timeline

### Testing & Quality Assurance

**Test Framework:**
- [docs/testing/PYTEST_MARKERS_GUIDE.md](docs/testing/PYTEST_MARKERS_GUIDE.md) - Pytest markers guide
- [docs/testing/FR_TEST_MAPPING.md](docs/testing/FR_TEST_MAPPING.md) - FR to test mapping
- [tests/](tests/) - Comprehensive test suite (5,479 tests)

**Test Coverage & Reports:**
- [docs/developer/test-coverage.md](docs/developer/test-coverage.md) - Test coverage metrics
- [docs/reports/](docs/reports/) - QA audits and performance analysis

**Pytest Marker System (87/107 FRs):**
```bash
# Run tests for specific FR:
pytest -m fr_034  # GitHub CLI tests
pytest -m fr_085  # Auto-complete tests

# List all FR markers:
pytest --markers | grep fr_
```

### Security & Best Practices
- [SECURITY.md](SECURITY.md) - Security policy
- [docs/developer/security-guide.md](docs/developer/security-guide.md) - Security best practices
- [docs/developer/security-implementation.md](docs/developer/security-implementation.md) - Security features

### Planning & Future Work
- [ROADMAP.md](ROADMAP.md) - Version roadmap and feature planning
- [openspec/](openspec/) - Active feature proposals and specifications
- [openspec/README.md](openspec/README.md) - OpenSpec workflow guide

---

## 🗂️ Archived Documentation

### v2.0.1 (November 13, 2025)
**Focus:** Test Suite Repair

Located in `docs/archive/v2.0.1/`:
- **TEST_FIX_SUMMARY.md** - Complete test fix report (2,205 passing, 3 skipped)
- **hung_tests_log.txt** - Process cleanup log

**Status:** ✅ COMPLETE - Test suite stabilized at 99.86% pass rate

### v2.0.0 (November 8-9, 2025)
**Focus:** Advanced Editing Features (Auto-complete, Syntax Checking, Templates)

Located in `docs/archive/v2.0.0/`:
- **V2_0_0_PROGRESS.md** - Complete milestone tracking
- **TEST_ISSUES_AGGREGATE.md** - Test issue resolution log
- **v2.0.0_MASTER_PLAN.md** - Master implementation plan
- **v2.0.0_AUTOCOMPLETE_PLAN.md** - Auto-complete feature plan
- **v2.0.0_SYNTAX_CHECKING_PLAN.md** - Syntax checking plan
- **v2.0.0_TEMPLATES_PLAN.md** - Template system plan
- **v2.0.0_INTEGRATION_GUIDE.md** - Integration guide
- **planning/** subdirectory - Detailed planning docs

**Status:** ✅ COMPLETE - All features delivered ahead of schedule (2 days vs 16 weeks)

### Historical Analyses
Located in `docs/archive/historical/`:
- **THREADING_ARCHITECTURE_ANALYSIS.md** - Threading model analysis

### Documentation Snapshots
Located in `docs/archive/snapshots/`:
- **CHECKPOINT_2025-11-12.md** - Project checkpoint snapshot
- **PHASE_2_TEST_EXPANSION_SUMMARY.md** - Test expansion phase summary
- **DOCUMENTATION_SCORECARD_2025-11-06.md** - Documentation quality snapshot
- **2025-11-06-master-summary.md** - Nov 6 complete work summary
- **TEST_SUITE_FIXES_GUIDE.md** - Test suite fix guide

---

## 🎯 Quick Reference

### For New Users
1. Start with [README.md](README.md)
2. Run installer for your OS
3. Check [docs/user/](docs/user/) for feature guides

### For New Developers
1. Read [CLAUDE.md](CLAUDE.md) - Complete developer guide
2. Review [SPECIFICATIONS_HU.md](SPECIFICATIONS_HU.md) - Feature requirements
3. Explore [docs/developer/](docs/developer/) - API docs
4. Check [docs/testing/PYTEST_MARKERS_GUIDE.md](docs/testing/PYTEST_MARKERS_GUIDE.md) - Test framework
5. Run `make test` to verify setup

### For AI-Assisted Development
1. Use [SPECIFICATIONS_AI.md](SPECIFICATIONS_AI.md) - AI-optimized specs
2. Check [docs/testing/FR_TEST_MAPPING.md](docs/testing/FR_TEST_MAPPING.md) - Test requirements
3. Follow [CLAUDE.md](CLAUDE.md) - Development patterns

### For Contributors
1. Read [docs/developer/contributing.md](docs/developer/contributing.md) - Contribution guide
2. Check [ROADMAP.md](ROADMAP.md) for planned features
3. Review [SECURITY.md](SECURITY.md) for security practices
4. Follow coding standards in [CLAUDE.md](CLAUDE.md#standards)

---

## 📊 Documentation Stats

**Total Documentation:** ~223KB across all files
**Active Documentation:** ~223KB (current)
**Archived Documentation:** Historical versions in docs/archive/

**Key Documents:**
- SPECIFICATIONS_AI.md: 156KB - AI-optimized with test requirements
- SPECIFICATIONS_HU.md: 24KB - Human-readable quick reference
- CHANGELOG.md: 21KB - Complete version history
- CLAUDE.md: 11KB - Developer guide
- ROADMAP.md: 11KB - Future planning

**Test Suite:**
- 5,479 total tests
- 87/107 FRs with pytest markers (81% coverage)
- 149 test files

---

## 🔍 Finding Documentation

### By Topic
- **Installation**: README.md, install scripts
- **Features**: SPECIFICATIONS_HU.md, CHANGELOG.md
- **Architecture**: CLAUDE.md (main_window.py, threading model)
- **Testing**: docs/testing/, PYTEST_MARKERS_GUIDE.md
- **Security**: SECURITY.md, CLAUDE.md (security patterns)
- **AI Integration**: CLAUDE.md (Ollama, Claude sections)
- **FR Traceability**: FR_TEST_MAPPING.md, pytest markers

### By Audience
- **End Users**: README.md, docs/user/, CHANGELOG.md
- **Developers**: CLAUDE.md, SPECIFICATIONS_HU.md, docs/developer/
- **AI Assistants**: SPECIFICATIONS_AI.md, CLAUDE.md, FR_TEST_MAPPING.md
- **Contributors**: All above + ROADMAP.md, SECURITY.md, docs/developer/contributing.md
- **Project Managers**: ROADMAP.md, CHANGELOG.md, docs/reports/

### By Task
- **Implementing a Feature**: SPECIFICATIONS_AI.md → CLAUDE.md → docs/developer/
- **Writing Tests**: PYTEST_MARKERS_GUIDE.md → FR_TEST_MAPPING.md
- **Reviewing Code**: CLAUDE.md → SPECIFICATIONS_HU.md → SECURITY.md
- **Planning Work**: ROADMAP.md → openspec/

---

## 📝 Documentation Standards

All documentation follows:
- **Reading Level**: Grade 5.0 or below (Flesch-Kincaid)
- **Sentence Length**: ≤15 words average
- **Format**: GitHub-flavored Markdown
- **Validation**: `python3 scripts/readability_check.py <file>`

**Auto-Simplification:**
- `.claude/skills/grandmaster-techwriter.md` - Auto Grade 5.0 tech writing skill
- Auto-activates for documentation files
- Self-iterates until Grade ≤5.0 readability

---

## 🔄 Keeping Documentation Updated

**Current Status:** ✅ All documentation up-to-date (as of Nov 15, 2025)

**Update Schedule:**
- README.md: Updated with each major release
- CHANGELOG.md: Updated with every version bump
- ROADMAP.md: Reviewed quarterly
- CLAUDE.md: Updated when architecture changes
- SPECIFICATIONS_HU.md: Updated when requirements change
- SPECIFICATIONS_AI.md: Updated with SPECIFICATIONS_HU.md
- FR_TEST_MAPPING.md: Updated when tests change

**Archive Policy:**
- Planning docs → Archive when milestone complete
- Progress tracking → Archive when release ships
- Analysis docs → Archive when findings integrated
- Snapshots → Archive immediately after creation

**Recent Updates:**
- **Nov 15**: Pytest marker framework complete (87/107 FRs)
- **Nov 15**: SPECIFICATIONS.md → SPECIFICATIONS_HU.md rename
- **Nov 15**: SPECIFICATIONS_V2.md → SPECIFICATIONS_AI.md rename
- **Nov 15**: Added docs/testing/ documentation
- **Nov 13**: v2.0.1 test suite repair documentation archived
- **Nov 9**: v2.0.0 planning docs moved to archive

---

## 📞 Documentation Help

**Found an issue?**
- Report via GitHub Issues: https://github.com/webbwr/AsciiDoctorArtisan/issues
- Include: Document name, section, and description

**Need clarification?**
- Check CLAUDE.md - Most comprehensive developer guide
- Search SPECIFICATIONS_HU.md - All features and requirements
- Review SPECIFICATIONS_AI.md - Detailed implementation specs
- Review archived docs - Historical context
- See [docs/archive/README.md](docs/archive/README.md) for archive organization

**Using Pytest Markers?**
- See [docs/testing/PYTEST_MARKERS_GUIDE.md](docs/testing/PYTEST_MARKERS_GUIDE.md)
- Check [docs/testing/FR_TEST_MAPPING.md](docs/testing/FR_TEST_MAPPING.md)

---

## 🗺️ Documentation Roadmap

### Completed (Nov 2025)
- ✅ Pytest marker framework (87/107 FRs)
- ✅ Dual specification system (HU + AI)
- ✅ Testing documentation structure
- ✅ FR traceability system

### In Progress
- 📝 OpenSpec proposal templates
- 📝 API documentation expansion

### Planned (Q1 2026)
- 📋 Video tutorials for features
- 📋 Interactive feature demos
- 📋 Developer onboarding guide

---

**Last Major Update:** Pytest marker framework + spec restructure (November 15, 2025)
**Next Review:** v2.1.0 planning (Q1 2026)
