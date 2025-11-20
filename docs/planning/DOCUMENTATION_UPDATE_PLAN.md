# Documentation Update Plan

**Date:** November 20, 2025
**Status:** Planning
**Version:** v2.0.6+
**Estimated Effort:** 1-2 weeks

---

## Overview

**Goal:** Update and expand documentation for v2.0.6 release, improving user onboarding and contributor experience.

**Current State:**
- ✅ Comprehensive SPECIFICATIONS_AI.md (107 FRs)
- ✅ CLAUDE.md for AI development
- ✅ Basic README.md (Grade 5.0 reading level)
- ✅ Some technical documentation
- ❌ Missing: Architecture guide for contributors
- ❌ Missing: Updated screenshots (v2.0.x features)
- ❌ Missing: Video tutorials
- ❌ Missing: Expanded examples

**Benefits:**
- Improved user onboarding
- Easier contributor adoption
- Better feature discovery
- Reduced support burden
- Professional presentation

---

## Documentation Audit

### Existing Documentation

#### ✅ Well-Documented
- `SPECIFICATIONS_AI.md` - Comprehensive FR specifications
- `SPECIFICATIONS_HU.md` - Human-readable quick reference
- `CLAUDE.md` - AI development guide (just updated!)
- `README.md` - User guide (Grade 5.0, excellent)
- `CHANGELOG.md` - Version history
- `SECURITY.md` - Security policy
- Test documentation in test files

#### ⚠️ Needs Updates
- `docs/user/user-guide.md` - Missing v2.0.x features
- `docs/developer/contributing.md` - Basic, needs expansion
- Architecture documentation - Scattered, needs consolidation
- Screenshots - Outdated, missing new features
- Examples - Limited

#### ❌ Missing
- Architecture overview guide
- Video tutorials
- API documentation (if exposing API)
- Plugin development guide (future)
- Troubleshooting guide (expanded)
- FAQ

---

## Documentation Updates

### Priority 1: User Documentation (Days 1-4)

#### 1.1 Update User Guide

**File:** `docs/user/user-guide.md`

**Current Issues:**
- Missing v2.0.0 features (auto-complete, syntax checking, templates)
- Missing v1.8+ features (find & replace, spell check)
- No screenshots of new features
- Limited troubleshooting

**Updates Needed:**
1. **Auto-Complete Section** (NEW)
   - How to trigger (Ctrl+Space)
   - Available completions
   - Fuzzy matching
   - Screenshots

2. **Syntax Checking Section** (NEW)
   - Real-time validation
   - Error navigation (F8)
   - Error display
   - Screenshots

3. **Templates Section** (NEW)
   - Built-in templates
   - Creating custom templates
   - Template variables
   - Template browser
   - Screenshots

4. **Find & Replace** (Expand)
   - Detailed examples
   - Regex patterns
   - Case sensitivity
   - Screenshots

5. **Spell Check** (Expand)
   - Language support
   - Custom dictionary
   - Adding words
   - Screenshots

6. **GitHub CLI Integration** (NEW)
   - Creating PRs
   - Managing issues
   - Repository view
   - Screenshots

**Deliverables:**
- [ ] Updated user-guide.md with all v2.0.x features
- [ ] 15-20 new screenshots
- [ ] Step-by-step tutorials
- [ ] Updated table of contents

#### 1.2 Expand Troubleshooting Guide

**New File:** `docs/user/troubleshooting.md`

**Sections:**
1. **Installation Issues**
   - Missing dependencies (Pandoc, wkhtmltopdf)
   - Python version conflicts
   - PySide6 installation
   - Platform-specific issues

2. **Runtime Issues**
   - Application won't start
   - GPU detection failures
   - Preview rendering issues
   - Export failures
   - Git integration problems

3. **Performance Issues**
   - Slow startup
   - Laggy preview
   - Memory usage
   - CPU usage

4. **Feature-Specific Issues**
   - AI chat not working (Ollama)
   - Claude API errors
   - Spell check not working
   - Auto-complete not triggering

5. **Error Messages**
   - Common error messages explained
   - How to report bugs
   - Diagnostic commands

**Deliverables:**
- [ ] Comprehensive troubleshooting guide
- [ ] Error message reference
- [ ] Diagnostic commands

#### 1.3 Create FAQ

**New File:** `docs/user/FAQ.md`

**Sections:**
1. **General Questions**
   - What is AsciiDoc Artisan?
   - What platforms are supported?
   - Is it free?
   - How do I get help?

2. **Features**
   - What file formats can I open?
   - Can I export to PDF/DOCX/HTML?
   - Does it support Git?
   - Can I use AI assistance?

3. **Performance**
   - Why is GPU acceleration recommended?
   - How fast is the startup?
   - Does it work without GPU?

4. **Customization**
   - Can I change themes?
   - Can I add custom templates?
   - Can I extend functionality?

5. **Comparison**
   - How is it different from VS Code + AsciiDoc?
   - How is it different from Asciidoctor.org?
   - Should I use this or X?

**Deliverables:**
- [ ] FAQ document with 20+ questions
- [ ] Quick answers with links to detailed docs

#### 1.4 Create Quick Start Guide

**New File:** `docs/user/quick-start.md`

**Content:**
- 5-minute getting started guide
- First document walkthrough
- Key features overview
- Next steps

**Deliverables:**
- [ ] Quick start guide (1-2 pages)
- [ ] Screenshots of key steps

#### 1.5 Screenshots & Media

**Tasks:**
1. Take new screenshots of all features
2. Annotate screenshots with callouts
3. Create animated GIFs for complex workflows
4. Organize in `docs/images/` directory

**Screenshots Needed:**
- Main window overview
- Auto-complete in action
- Syntax checking (error display)
- Template browser
- Template variable dialog
- Find & replace bar
- Spell check context menu
- Git status dialog
- Quick commit widget
- GitHub CLI dialogs
- Ollama chat panel
- Claude chat integration
- Theme switching
- Export dialogs
- Preferences dialog

**Deliverables:**
- [ ] 20+ high-quality screenshots
- [ ] 5+ animated GIFs
- [ ] Organized image directory

---

### Priority 2: Developer Documentation (Days 5-8)

#### 2.1 Architecture Guide

**New File:** `docs/developer/architecture.md`

**Sections:**
1. **High-Level Overview**
   - Application structure
   - Design patterns (Manager pattern)
   - Threading model
   - Data flow

2. **Core Components**
   - MainWindow (controller)
   - Managers (menu, theme, status, file, git, export)
   - Workers (Git, Pandoc, Preview, Ollama, Claude)
   - Core modules (settings, file ops, GPU detection)

3. **Manager Pattern**
   - Why managers?
   - Manager responsibilities
   - Manager lifecycle
   - Creating new managers

4. **Threading Architecture**
   - QThread workers
   - Signal/slot communication
   - Reentrancy guards
   - Threading best practices

5. **GPU Acceleration**
   - Detection mechanism
   - Caching strategy
   - Fallback handling
   - Performance benefits

6. **Settings System**
   - QStandardPaths
   - JSON serialization
   - Settings migrations
   - Platform differences

7. **Security**
   - Atomic file writes
   - Path sanitization
   - Subprocess safety (shell=False)
   - Input validation

8. **Extension Points**
   - Adding new export formats
   - Adding new themes
   - Adding new templates
   - Adding new AI models

**Deliverables:**
- [ ] Comprehensive architecture guide (10+ pages)
- [ ] Architecture diagrams (Mermaid)
- [ ] Code examples
- [ ] Best practices

#### 2.2 Contributing Guide (Expanded)

**File:** `docs/developer/contributing.md` (expand existing)

**New Sections:**
1. **Development Setup**
   - Detailed installation steps
   - IDE setup (VS Code, PyCharm)
   - Pre-commit hooks
   - Running tests

2. **Code Standards**
   - Style guide (ruff-format, 88 chars)
   - Type hints (mypy --strict)
   - Docstring conventions
   - Testing requirements

3. **Development Workflow**
   - Branch strategy
   - Commit message format
   - PR process
   - Code review checklist

4. **Testing**
   - Unit tests (pytest)
   - Integration tests
   - E2E tests (new)
   - Coverage requirements
   - Running specific tests

5. **Common Tasks**
   - Adding new feature
   - Fixing bug
   - Updating dependencies
   - Writing tests
   - Updating documentation

6. **Release Process**
   - Version numbering
   - Changelog updates
   - Release checklist
   - Distribution

**Deliverables:**
- [ ] Expanded contributing guide (8+ pages)
- [ ] Setup checklists
- [ ] Workflow diagrams
- [ ] Code review template

#### 2.3 Testing Guide

**New File:** `docs/developer/testing.md`

**Sections:**
1. **Testing Philosophy**
   - Test pyramid
   - Coverage goals
   - When to write tests

2. **Unit Testing**
   - Writing unit tests
   - Mocking strategies
   - QtBot usage (pytest-qt)
   - MockParentWidget pattern

3. **Integration Testing**
   - Integration test patterns
   - External dependency handling
   - Test markers (@live_api, @requires_gpu)

4. **E2E Testing** (NEW)
   - Using pytest-bdd
   - Writing feature files
   - Step definitions
   - Running E2E tests

5. **Test Organization**
   - Directory structure
   - Naming conventions
   - Fixtures and conftest.py
   - Test markers

6. **Coverage**
   - Measuring coverage
   - Coverage goals by module
   - Qt threading limitations
   - Improving coverage

**Deliverables:**
- [ ] Comprehensive testing guide
- [ ] Test examples
- [ ] Coverage best practices

#### 2.4 API Documentation (Optional)

**Task:** Generate API docs from docstrings

**Tools:**
- Sphinx + autodoc
- mkdocs + mkdocstrings

**Deliverables:**
- [ ] Generated API documentation (if needed)
- [ ] Hosted on GitHub Pages (optional)

---

### Priority 3: Examples & Tutorials (Days 9-10)

#### 3.1 Sample Documents

**Directory:** `examples/documents/`

**Samples:**
1. `technical-report.adoc` - Technical report example
2. `user-manual.adoc` - User manual example
3. `api-documentation.adoc` - API docs example
4. `presentation.adoc` - Presentation slides
5. `book-chapter.adoc` - Book chapter
6. `blog-post.adoc` - Blog post
7. `readme.adoc` - README file

**Deliverables:**
- [ ] 7+ sample documents
- [ ] README explaining each sample

#### 3.2 Tutorial Series

**Directory:** `docs/tutorials/`

**Tutorials:**
1. **Tutorial 1: Your First Document**
   - Create, edit, preview, save
   - Basic AsciiDoc syntax
   - Exporting to PDF

2. **Tutorial 2: Using Templates**
   - Choosing template
   - Filling variables
   - Customizing template

3. **Tutorial 3: Git Workflow**
   - Initialize repository
   - Making commits
   - Quick commit feature

4. **Tutorial 4: Advanced Editing**
   - Auto-complete
   - Find & replace
   - Spell check

5. **Tutorial 5: AI Assistance**
   - Setting up Ollama
   - Chatting with AI
   - Getting syntax help

**Deliverables:**
- [ ] 5 step-by-step tutorials
- [ ] Screenshots for each step
- [ ] Sample files

#### 3.3 Video Tutorials (Optional)

**Videos:**
1. Getting Started (5 min)
2. Key Features Overview (10 min)
3. Git Integration Demo (5 min)
4. AI Chat Demo (5 min)

**Deliverables:**
- [ ] 4 tutorial videos
- [ ] Hosted on YouTube
- [ ] Linked from README

---

## Documentation Standards

### Writing Style
- **User Docs:** Grade 5.0 reading level (Flesch-Kincaid)
- **Developer Docs:** Grade 8-10 (technical but clear)
- **Code Examples:** Well-commented, runnable
- **Screenshots:** High-quality, annotated

### Validation
```bash
# Check readability (existing script)
python3 scripts/readability_check.py docs/user/user-guide.md

# Target: Grade 5.0 for user docs
# Target: Grade 8-10 for developer docs
```

### Format
- Markdown (.md)
- Mermaid diagrams for architecture
- GitHub-flavored markdown
- Relative links

---

## Implementation Plan

### Week 1: User Documentation

**Day 1-2: User Guide Updates**
- [ ] Update user-guide.md with v2.0.x features
- [ ] Take 20+ screenshots
- [ ] Add step-by-step tutorials

**Day 3: Troubleshooting & FAQ**
- [ ] Create troubleshooting.md
- [ ] Create FAQ.md
- [ ] Create quick-start.md

**Day 4: Screenshots & Media**
- [ ] Capture all screenshots
- [ ] Create animated GIFs
- [ ] Organize image directory

### Week 2: Developer Documentation

**Day 5-6: Architecture Guide**
- [ ] Write architecture.md
- [ ] Create architecture diagrams
- [ ] Add code examples

**Day 7: Contributing & Testing**
- [ ] Expand contributing.md
- [ ] Create testing.md
- [ ] Add workflow diagrams

**Day 8-9: Examples & Tutorials**
- [ ] Create sample documents
- [ ] Write tutorial series
- [ ] Test all examples

**Day 10: Review & Polish**
- [ ] Review all documentation
- [ ] Check readability scores
- [ ] Fix broken links
- [ ] Update DOCUMENTATION_INDEX.md

---

## Success Metrics

### Completeness
- [ ] All v2.0.x features documented
- [ ] Architecture guide complete
- [ ] Contributing guide expanded
- [ ] 20+ screenshots added
- [ ] 5+ tutorials written

### Quality
- [ ] User docs at Grade 5.0 reading level
- [ ] Developer docs clear and comprehensive
- [ ] All code examples tested
- [ ] No broken links

### Usability
- [ ] New users can get started in <10 minutes
- [ ] Contributors understand architecture
- [ ] Common issues covered in troubleshooting
- [ ] FAQ answers common questions

---

## Documentation Structure (Final)

```
docs/
├── README.md                          # Documentation index
├── user/
│   ├── quick-start.md                # NEW: 5-minute guide
│   ├── user-guide.md                 # UPDATED: Complete guide
│   ├── troubleshooting.md            # NEW: Troubleshooting
│   ├── FAQ.md                        # NEW: Frequently asked questions
│   ├── performance-tips.md           # Existing
│   ├── github-integration.md         # Existing
│   └── ollama-chat.md                # Existing
├── developer/
│   ├── architecture.md               # NEW: Architecture guide
│   ├── contributing.md               # UPDATED: Expanded guide
│   ├── testing.md                    # NEW: Testing guide
│   ├── configuration.md              # Existing
│   ├── security-guide.md             # Existing
│   └── performance-profiling.md      # Existing
├── tutorials/
│   ├── 01-first-document.md          # NEW
│   ├── 02-using-templates.md         # NEW
│   ├── 03-git-workflow.md            # NEW
│   ├── 04-advanced-editing.md        # NEW
│   └── 05-ai-assistance.md           # NEW
├── images/
│   ├── user/                         # User guide screenshots
│   ├── developer/                    # Developer diagrams
│   └── tutorials/                    # Tutorial screenshots
├── planning/                         # This directory (planning docs)
│   ├── E2E_TEST_PLAN.md
│   └── DOCUMENTATION_UPDATE_PLAN.md
└── sessions/                         # Work session notes

examples/
├── documents/                        # NEW: Sample documents
│   ├── technical-report.adoc
│   ├── user-manual.adoc
│   ├── api-documentation.adoc
│   └── README.md
└── templates/                        # Existing templates
```

---

## Next Steps

1. ✅ Review and approve this plan
2. Start with user guide updates (highest impact)
3. Capture screenshots (batch operation)
4. Write architecture guide (highest value for contributors)
5. Expand contributing guide
6. Create tutorials
7. Update DOCUMENTATION_INDEX.md

---

**Status:** Ready to begin
**Priority:** High (improves adoption)
**Timeline:** 1-2 weeks
**Owner:** Development team
