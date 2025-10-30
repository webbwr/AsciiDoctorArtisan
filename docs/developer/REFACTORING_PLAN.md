# Repository Refactoring Plan
## Grandmaster Programmer & Librarian Edition

**Date:** October 29, 2025
**Goal:** Optimize repository structure for clarity, maintainability, and best practices

---

## Analysis Summary

### Repository Statistics
- Source files: 62 Python modules
- Test files: 74 test modules
- Documentation: 13 markdown files
- Scripts: 12 utility scripts
- Empty directories: 3 (placeholders)

### Issues to Address

#### 1. Empty Placeholder Directories
**Location:** `src/asciidoc_artisan/{claude,conversion,git}/`
**Status:** Contains only `__init__.py` files
**Action:** Remove - not currently used, YAGNI principle

#### 2. Duplicate Requirements Files
**Files:**
- `requirements-production.txt` (3.0K)
- `requirements-production-updated.txt` (3.2K)
- `requirements.txt` (2.2K, dev dependencies)

**Action:** Consolidate to single production file, keep dev separate

#### 3. Cache Directories
**Locations:**
- `.mypy_cache/` - Type checker cache
- `.ruff_cache/` - Linter cache
- `coverage_reports/` - Test coverage data

**Action:** Add to gitignore, remove from tracking

#### 4. Documentation Organization
**Current:**
- Root: CLAUDE.md, README.md, SPECIFICATIONS.md, ROADMAP, SECURITY.md
- docs/: 13 implementation/guide documents

**Action:** Create clear hierarchy
```
docs/
├── user/          # User-facing docs
├── developer/     # Development guides
├── architecture/  # Technical specs
└── operations/    # Deployment & ops
```

#### 5. Configuration Files
**Current:** Scattered in root (11 config files)
**Action:** Document purpose, ensure .editorconfig consistency

#### 6. Logs Directory
**Status:** Empty, exists only for gitkeep
**Action:** Remove, let app create as needed

---

## Refactoring Actions

### Phase 1: Cleanup Empty & Unused
- [ ] Remove `src/asciidoc_artisan/claude/`
- [ ] Remove `src/asciidoc_artisan/conversion/`
- [ ] Remove `src/asciidoc_artisan/git/`
- [ ] Remove `logs/` directory
- [ ] Delete `requirements-production-updated.txt`
- [ ] Rename `requirements-production.txt` to `requirements-prod.txt`

### Phase 2: Improve Gitignore
- [ ] Add `.mypy_cache/`
- [ ] Add `.ruff_cache/`
- [ ] Add `coverage_reports/`
- [ ] Add `.claude.json` (local session state)
- [ ] Add `coverage.json` (test artifact)

### Phase 3: Documentation Hierarchy
- [ ] Create `docs/architecture/`
- [ ] Move SPECIFICATIONS.md → docs/architecture/
- [ ] Move IMPLEMENTATION_COMPLETE.md → docs/architecture/
- [ ] Create `docs/user/`
- [ ] Move how-to-use.md → docs/user/
- [ ] Create `docs/developer/`
- [ ] Move how-to-contribute.md → docs/developer/
- [ ] Move REFACTORING_PLAN documents → docs/developer/
- [ ] Create `docs/operations/`
- [ ] Move SECURITY*.md → docs/operations/
- [ ] Update all internal references

### Phase 4: Root Level Cleanup
**Keep in root:**
- README.md (entry point)
- CLAUDE.md (AI assistant config)
- LICENSE
- ROADMAP_v1.5.0.md (current version)
- Makefile (build automation)
- pyproject.toml (package config)
- pytest.ini (test config)
- setup.py (packaging)
- .gitignore, .gitattributes
- .pre-commit-config.yaml
- .ruff.toml
- .editorconfig
- requirements.txt (dev)
- requirements-prod.txt (production)
- install-asciidoc-artisan.sh (installer)
- launch-asciidoc-artisan-gui.sh (launcher)

**Move or remove:**
- coverage.json → ignored
- .claude.json → ignored

### Phase 5: Test Structure Review
**Current structure is good:**
```
tests/
├── test_*.py (68 unit test files)
├── performance/ (3 benchmark tests)
└── conftest.py (pytest fixtures)
```

**Action:** No changes needed - well organized

### Phase 6: Configuration Documentation
- [ ] Create CONFIG.md documenting all config files
- [ ] Explain purpose of each root-level config
- [ ] Document settings and customization options

---

## Expected Outcomes

### Before Refactoring
```
./
├── 26 files in root (mix of docs, config, code)
├── docs/ (13 files, no organization)
├── src/ (3 empty placeholder dirs)
├── .mypy_cache/ (tracked)
├── .ruff_cache/ (tracked)
└── logs/ (empty directory)
```

### After Refactoring
```
./
├── 17 essential files in root (README, config, scripts)
├── docs/
│   ├── architecture/ (specs, implementation)
│   ├── developer/ (guides, refactoring plans)
│   ├── user/ (how-to guides)
│   └── operations/ (security, deployment)
├── src/ (no empty directories)
└── clean cache management (all ignored)
```

### Benefits
1. **Clarity:** Clear documentation hierarchy
2. **Maintainability:** No empty directories or duplicate files
3. **Performance:** Properly ignored cache directories
4. **Professionalism:** Clean, organized structure
5. **Onboarding:** New developers find docs easily
6. **Best practices:** Follows Python project standards

---

## Implementation Checklist

- [ ] Phase 1: Cleanup (Remove empty dirs, duplicates)
- [ ] Phase 2: Gitignore (Add cache dirs)
- [ ] Phase 3: Documentation (Reorganize hierarchy)
- [ ] Phase 4: Root cleanup (Remove artifacts)
- [ ] Phase 5: Test review (Verify structure)
- [ ] Phase 6: Config docs (Create CONFIG.md)
- [ ] Run full test suite
- [ ] Update CI/CD if needed
- [ ] Commit and push changes

---

## Risk Assessment

**Low Risk:**
- Removing empty directories
- Deleting duplicate requirements files
- Improving gitignore

**Medium Risk:**
- Moving documentation (need to update references)
- Reorganizing docs/ hierarchy

**Mitigation:**
- Test after each phase
- Use git for rollback capability
- Update all document references
- Run full test suite before committing

---

*Created by Claude Code - Grandmaster Programmer & Librarian Mode*
