# Documentation Structure

**Version**: 1.2.0
**Date**: October 26, 2025
**Status**: Consolidated and up-to-date

---

## Core Documentation

### README.md
**Purpose**: Main user documentation and quick start guide
**Audience**: End users, new users
**Contains**:
- What the program does
- Installation instructions (quick and manual)
- Basic usage
- Keyboard shortcuts
- AI features setup (Ollama)
- Speed features (GPU)
- Troubleshooting

### SPECIFICATIONS.md
**Purpose**: Technical specifications and requirements
**Audience**: Developers, technical users, testers
**Contains**:
- Program rules (what MUST work)
- Test procedures for all features
- Version history
- AI conversion specifications
- System requirements
- Future features roadmap

### CLAUDE.md
**Purpose**: Instructions for AI assistants (Claude Code)
**Audience**: AI developers, Claude Code
**Contains**:
- Project overview
- Code structure
- Development workflows
- Performance hot paths
- Common commands

### SECURITY.md
**Purpose**: Security policy and vulnerability reporting
**Audience**: Security researchers, users
**Contains**:
- Supported versions
- Reporting procedures
- Security best practices

---

## User Guides (docs/)

### docs/how-to-use.md
**Purpose**: Detailed user manual
**Audience**: Users learning all features
**Contains**:
- Step-by-step feature guides
- Examples
- Tips and tricks

### docs/how-to-contribute.md
**Purpose**: Contributor guidelines
**Audience**: Contributors, developers
**Contains**:
- How to contribute
- Code style
- Pull request process
- Testing requirements

### docs/USER_TESTING_GUIDE.md
**Purpose**: Testing procedures and checklists
**Audience**: Testers, QA, developers
**Contains**:
- Feature tests (10 test suites)
- Performance benchmarks
- AI conversion tests
- Expected results

---

## Deleted Files (Redundant)

These files were removed during consolidation:

### Old Summaries (root)
- ❌ ANTHROPIC_REMOVAL_SUMMARY.md → Info in SPECIFICATIONS.md
- ❌ SPEC_CONSOLIDATION_SUMMARY.md → Old change log
- ❌ STATUS_BAR_METRICS_SUMMARY.md → Old change log
- ❌ CHANGELOG.md → Replaced by version history in SPECIFICATIONS.md

### Redundant Docs (docs/)
- ❌ docs/index.md → Redundant with README.md
- ❌ docs/how-to-install.md → Already in README.md
- ❌ docs/OLLAMA_SETUP.md → Merged into README.md and SPECIFICATIONS.md
- ❌ docs/planning/ → Research notes (implemented)

---

## Documentation Principles

1. **No Redundancy**: Each piece of information appears once
2. **Clear Audience**: Each file has specific target audience
3. **Up-to-Date**: All files reflect v1.2.0 features
4. **Grade 5.0**: All docs written at Grade 5.0 reading level
5. **Practical**: Focus on what users/developers need

---

## Quick Reference

**New user?** → Start with README.md
**Want to contribute?** → Read docs/how-to-contribute.md
**Learning features?** → Read docs/how-to-use.md
**Testing?** → Use docs/USER_TESTING_GUIDE.md
**Technical specs?** → Read SPECIFICATIONS.md
**AI assistant?** → Read CLAUDE.md

---

**Total Files**: 7 core documents (down from 15+)
**Reading Level**: Grade 5.0
**Status**: ✅ Consolidated and current
