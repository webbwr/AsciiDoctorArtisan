# AsciiDoc Artisan - Documentation Index

**Last Updated:** November 9, 2025
**Version:** 2.0.0 ✅ Production Ready

This index provides quick access to all project documentation.

---

## 📘 Essential Documentation (Start Here)

### For Users
- **[README.md](README.md)** - Project overview, installation, and quick start guide
- **[docs/user/](docs/user/)** - User guides and tutorials

### For Developers
- **[CLAUDE.md](CLAUDE.md)** - Complete developer guide and AI assistant instructions
- **[SPECIFICATIONS.md](SPECIFICATIONS.md)** - Functional requirements and feature specifications
- **[docs/developer/](docs/developer/)** - Developer guides and API documentation

### For Contributors
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[ROADMAP.md](ROADMAP.md)** - Future plans and feature roadmap
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting

---

## 📂 Documentation Organization

### Root Directory
```
README.md              - Project overview
CLAUDE.md              - Developer guide (42KB)
SPECIFICATIONS.md      - Requirements (37KB)
CHANGELOG.md           - Version history (18KB)
ROADMAP.md             - Future planning (24KB)
SECURITY.md            - Security policy (2KB)
```

### docs/ Directory Structure
```
docs/
├── user/              - User-facing guides
├── developer/         - Developer documentation
├── planning/          - Project planning documents
├── reports/           - Analysis and metrics
├── completed/         - Finished milestone docs
└── archive/           - Historical documentation
    ├── v2.0.0/        - v2.0.0 planning and progress
    ├── historical/    - Architecture analyses
    └── snapshots/     - Documentation snapshots
```

---

## 📚 Documentation by Category

### Installation & Setup
- [README.md](README.md#installation) - Installation instructions
- [install-asciidoc-artisan.sh](install-asciidoc-artisan.sh) - Linux/Mac installer
- [install-asciidoc-artisan.ps1](install-asciidoc-artisan.ps1) - Windows PowerShell installer
- [requirements.txt](requirements.txt) - Python dependencies

### Features & Usage
- [SPECIFICATIONS.md](SPECIFICATIONS.md) - Complete feature list (84 rules)
- [docs/user/](docs/user/) - User guides
- [CHANGELOG.md](CHANGELOG.md) - Feature history by version

### Development
- [CLAUDE.md](CLAUDE.md) - Architecture, patterns, and workflows
- [docs/developer/](docs/developer/) - API docs and guides
- [ROADMAP.md](ROADMAP.md) - Future features and timeline

### Testing & Quality
- [tests/](tests/) - Comprehensive test suite
- [docs/reports/](docs/reports/) - Test coverage and metrics

---

## 🗂️ Archived Documentation

### v2.0.0 (Completed November 2025)
Located in `docs/archive/v2.0.0/`:
- **V2_0_0_PROGRESS.md** - Complete milestone tracking
- **TEST_ISSUES_AGGREGATE.md** - Test issue resolution log
- **v2.0.0_MASTER_PLAN.md** - Master implementation plan
- **v2.0.0_AUTOCOMPLETE_PLAN.md** - Auto-complete feature plan
- **v2.0.0_SYNTAX_CHECKING_PLAN.md** - Syntax checking plan
- **v2.0.0_TEMPLATES_PLAN.md** - Template system plan
- **v2.0.0_INTEGRATION_GUIDE.md** - Integration guide

**Status:** All v2.0.0 features complete (100% test pass rate, production-ready)

### Historical Analyses
Located in `docs/archive/historical/`:
- **THREADING_ARCHITECTURE_ANALYSIS.md** - Threading model analysis

### Documentation Snapshots
Located in `docs/archive/snapshots/`:
- **DOCUMENTATION_SCORECARD_2025-11-06.md** - Documentation quality snapshot

---

## 🎯 Quick Reference

### For New Users
1. Start with [README.md](README.md)
2. Run installer for your OS
3. Check [docs/user/](docs/user/) for guides

### For New Developers
1. Read [CLAUDE.md](CLAUDE.md) - Complete developer guide
2. Review [SPECIFICATIONS.md](SPECIFICATIONS.md) - Feature requirements
3. Explore [docs/developer/](docs/developer/) - API docs
4. Run `make test` to verify setup

### For Contributors
1. Read [CLAUDE.md](CLAUDE.md#development-workflow)
2. Check [ROADMAP.md](ROADMAP.md) for planned features
3. Review [SECURITY.md](SECURITY.md) for security practices
4. Follow coding standards in [CLAUDE.md](CLAUDE.md#coding-standards)

---

## 📊 Documentation Stats

**Total Documentation:** ~214KB across all files
**Active Documentation:** ~136KB (current)
**Archived Documentation:** ~78KB (historical)

**Key Documents:**
- CLAUDE.md: 42KB - Most comprehensive
- SPECIFICATIONS.md: 37KB - All requirements
- ROADMAP.md: 24KB - Future planning
- CHANGELOG.md: 18KB - Version history

---

## 🔍 Finding Documentation

### By Topic
- **Installation**: README.md, install scripts
- **Features**: SPECIFICATIONS.md, CHANGELOG.md
- **Architecture**: CLAUDE.md (main_window.py, threading model)
- **Testing**: CLAUDE.md (testing section), tests/
- **Security**: SECURITY.md, CLAUDE.md (security patterns)
- **AI Integration**: CLAUDE.md (Ollama, Claude sections)

### By Audience
- **End Users**: README.md, docs/user/, CHANGELOG.md
- **Developers**: CLAUDE.md, SPECIFICATIONS.md, docs/developer/
- **Contributors**: All above + ROADMAP.md, SECURITY.md
- **Project Managers**: ROADMAP.md, CHANGELOG.md, docs/reports/

---

## 📝 Documentation Standards

All documentation follows:
- **Reading Level**: Grade 5.0 or below (elementary school level)
- **Sentence Length**: ≤15 words average
- **Format**: GitHub-flavored Markdown
- **Validation**: Checked with `scripts/readability_check.py`

---

## 🔄 Keeping Documentation Updated

**Current Status:** ✅ All documentation is up-to-date (as of Nov 9, 2025)

**Update Schedule:**
- README.md: Updated with each major release
- CHANGELOG.md: Updated with every version bump
- ROADMAP.md: Reviewed quarterly
- CLAUDE.md: Updated when architecture changes
- SPECIFICATIONS.md: Updated when requirements change

**Archive Policy:**
- Planning docs → Archive when milestone complete
- Progress tracking → Archive when release ships
- Analysis docs → Archive when findings integrated
- Snapshots → Archive immediately after creation

---

## 📞 Documentation Help

**Found an issue?**
- Report via GitHub Issues: https://github.com/webbwr/AsciiDoctorArtisan/issues
- Include: Document name, section, and description

**Need clarification?**
- Check CLAUDE.md - Most comprehensive
- Search SPECIFICATIONS.md - All features
- Review archived docs - Historical context

---

**Last Major Update:** v2.0.0 release (November 2025)
**Next Review:** v2.1.0 planning (Q1 2026)
