# Documentation Standards & Maintenance Guide

**Last Updated:** November 18, 2025
**Version:** 2.0.4
**Status:** ✅ ACTIVE

This guide establishes standards for maintaining the AsciiDoc Artisan documentation ecosystem.

---

## 📋 Evergreen Naming Convention

**Principle:** Use dateless filenames for all ongoing reports and reviews.

### Standard Pattern

**✅ Correct:**
- `documentation-review.md`
- `qa-audit.md`
- `memory-optimization.md`
- `security-audit.md`

**❌ Incorrect:**
- `documentation-review-2025-11-06.md`
- `qa-audit-2025.md`
- `memory-optimization-2025.md`

### Version Tracking

Use internal document headers for versioning:

```markdown
# Document Title

**Last Updated:** November 18, 2025
**Version:** 2.0.4
**Status:** ✅ PRODUCTION-READY

[Content...]

---

## Document History

- Nov 18, 2025: Documentation consolidation (v2.0.4)
- Nov 15, 2025: Major update for v2.0.2
- Nov 6, 2025: Initial comprehensive review
```

### Benefits

- **Timeless URLs** - Links never break when content updates
- **Easy Updates** - Edit content without renaming files
- **Version in Content** - Date context maintained in headers
- **Semantic Versioning** - History tracked in content, not filename
- **Git History** - `git log --follow` tracks file evolution

---

## 🗄️ Archive Strategy

**Principle:** Keep documentation lean by archiving completed work and deleting duplicates.

### When to Archive

**Move to `docs/archive/` when:**
1. **Planning docs** - Milestone is complete and feature is shipped
2. **Progress tracking** - Release has shipped and progress is final
3. **Analysis docs** - Findings have been integrated into codebase
4. **Snapshots** - Immediately after creation (historical record)

### Archive Structure

```
docs/archive/
├── README.md (archive navigation guide)
├── v2.0.0/ (version-specific archives)
│   ├── V2_0_0_PROGRESS.md
│   ├── TEST_ISSUES_AGGREGATE.md
│   └── v2.0.0_*.md (final implementation docs)
├── v2.0.1/ (version-specific archives)
│   └── TEST_FIX_SUMMARY.md
├── historical/ (architecture analyses)
│   └── THREADING_ARCHITECTURE_ANALYSIS.md
└── snapshots/ (documentation snapshots)
    └── CHECKPOINT_2025-11-12.md
```

### What to Keep vs. Delete

**Keep (Final Versions):**
- Most complete implementation documents
- Final progress reports
- Comprehensive analysis documents
- Historical snapshots

**Delete (Duplicates):**
- Draft versions when final exists
- Redundant planning docs
- Duplicate content in multiple locations
- Outdated iterations of same document

### Archive Process

1. **Identify candidate** - Planning complete or milestone shipped
2. **Check for duplicates** - Compare with existing archive content
3. **Move final version** - Use `git mv` to preserve history
4. **Delete duplicates** - Use `git rm` for old versions
5. **Update references** - Fix any cross-references in active docs
6. **Commit with context** - Clear commit message explaining archive

---

## 🔍 Regular Audit Schedule

**Principle:** Quarterly audits maintain documentation quality and organization.

### Audit Frequency

**Weekly:**
- Review for duplicate content
- Check for misplaced files
- Verify cross-references
- Update version numbers
- Check readability compliance

**After Major Releases:**
- Archive planning documents
- Update version references
- Verify all links work
- Update DOCUMENTATION_INDEX.md

### Audit Checklist

#### 1. Duplicate Detection

```bash
# Find files with similar names
find docs/ -name "*.md" | sort | grep -E "(.+)-[0-9]{4}\.md"

# Check for duplicate content
find docs/archive/ -type f -name "*.md" -exec wc -l {} \; | sort -n
```

**Actions:**
- [ ] Identify files with date suffixes
- [ ] Compare draft vs. final versions
- [ ] Delete redundant copies
- [ ] Keep only most complete version

#### 2. File Placement Review

```bash
# Check for misplaced files in root docs/
ls -1 docs/*.md | grep -v README.md
```

**Actions:**
- [ ] Verify developer docs in `docs/developer/`
- [ ] Verify user docs in `docs/user/`
- [ ] Verify reports in `docs/reports/`
- [ ] Verify testing docs in `docs/testing/`
- [ ] Move any misplaced files

#### 3. Cross-Reference Verification

```bash
# Check for broken links
grep -r "\](.*\.md)" docs/ --include="*.md" | \
  grep -v "https://" | \
  cut -d: -f2 | \
  sed 's/.*\](\(.*\)).*/\1/' | \
  sort -u
```

**Actions:**
- [ ] Verify all internal links work
- [ ] Update references to renamed files
- [ ] Fix broken cross-references
- [ ] Check external URLs (if any)

#### 4. Version Consistency

```bash
# Check version references
grep -r "Version.*:" docs/ --include="*.md" | \
  grep -v "archive" | \
  cut -d: -f3 | \
  sort -u
```

**Actions:**
- [ ] Update version numbers to current
- [ ] Check pyproject.toml as source of truth
- [ ] Update "Last Updated" dates
- [ ] Verify CHANGELOG.md alignment

#### 5. Readability Compliance

```bash
# Check user docs for Grade 5.0 compliance
python3 scripts/readability_check.py docs/user/*.md
```

**Actions:**
- [ ] Verify user docs ≤ Grade 5.0
- [ ] Check sentence length (≤15 words average)
- [ ] Verify developer docs appropriately technical
- [ ] Update any non-compliant sections

---

## 📁 File Organization Rules

### Directory Structure

```
docs/
├── README.md ✅ Main navigation hub
├── user/ ✅ User-facing guides (Grade 5.0)
├── developer/ ✅ Developer guides and API docs
├── testing/ ✅ Test framework and FR traceability
├── reports/ ✅ Ongoing audits and reviews
├── completed/ ✅ Finished milestone documentation
└── archive/ ✅ Historical documentation
    ├── v2.0.0/ (version archives)
    ├── v2.0.1/ (version archives)
    ├── historical/ (architecture analyses)
    └── snapshots/ (documentation snapshots)
```

### File Naming Conventions

**Standard Format:**
- Use lowercase with hyphens: `test-coverage.md`
- Avoid underscores: ~~`test_coverage.md`~~
- No dates in filename: ~~`report-2025.md`~~
- Descriptive names: `performance-profiling.md` (not `perf.md`)

**Exceptions:**
- Root level files: `README.md`, `CHANGELOG.md`, `ROADMAP.md`
- Specification files: `SPECIFICATIONS_HU.md`, `SPECIFICATIONS_AI.md`
- Environment-specific: `CLAUDE.md`, `SECURITY.md`

---

## 📝 Content Standards

### Document Header Template

All documentation should include:

```markdown
# Document Title

**Last Updated:** November 15, 2025
**Version:** 2.0.2
**Status:** ✅ PRODUCTION-READY / 🚧 DRAFT / ⚠️ DEPRECATED

Brief description of document purpose.

---

## Table of Contents (if > 200 lines)

[Standard sections...]
```

### Readability Guidelines

**User Documentation (docs/user/):**
- **Target:** Grade 5.0 (Flesch-Kincaid)
- **Sentence Length:** ≤15 words average
- **Vocabulary:** Simple, common words
- **Validation:** `python3 scripts/readability_check.py <file>`

**Developer Documentation (docs/developer/):**
- **Target:** Grade 6-8 (technical but clear)
- **Sentence Length:** ≤20 words average
- **Vocabulary:** Technical terms acceptable with explanations
- **Focus:** Accuracy over simplicity

### Markdown Standards

**Formatting:**
- GitHub-flavored Markdown
- ATX-style headings (`#` not underlines)
- Fenced code blocks with language tags
- Consistent list formatting (prefer `-` for bullets)

**Code Examples:**
```markdown
```bash
# Good: Language tag, clear description
make test
```
```

**Links:**
- Use relative paths for internal docs: `[Guide](../user/user-guide.md)`
- Descriptive link text: `[Contributing Guide](contributing.md)` (not `[click here]`)
- Verify links before commit

---

## 🔄 Maintenance Workflow

### 1. Document Creation

**Before Creating New Document:**
1. Check if similar document exists
2. Verify correct location (user/developer/testing/reports)
3. Use evergreen naming (no dates)
4. Include standard header
5. Add to appropriate README.md

**Template:**
```markdown
# New Document Title

**Last Updated:** YYYY-MM-DD
**Version:** 2.0.4
**Status:** 🚧 DRAFT

Purpose and scope of this document.

---

[Content...]
```

### 2. Document Updates

**When Updating Existing Document:**
1. Update "Last Updated" date
2. Increment version (semantic versioning)
3. Add entry to "Document History" section
4. Verify cross-references still work
5. Run readability check if user-facing
6. Commit with descriptive message

### 3. Document Archival

**Moving to Archive:**
```bash
# 1. Create version archive directory if needed
mkdir -p docs/archive/v2.1.0/

# 2. Move document (preserve history)
git mv docs/planning/v2.1.0-plan.md docs/archive/v2.1.0/

# 3. Update cross-references
grep -r "v2.1.0-plan.md" docs/ --include="*.md"
# Edit any files that reference the moved document

# 4. Commit
git commit -m "docs: Archive v2.1.0 planning docs (milestone complete)"
```

### 4. Duplicate Removal

**Identifying Duplicates:**
```bash
# Find similar file sizes
find docs/ -name "*.md" -exec wc -l {} \; | sort -n | uniq -d -w 5

# Compare content
diff <(head -50 file1.md) <(head -50 file2.md)
```

**Removing Duplicates:**
```bash
# 1. Verify which version is more complete
wc -l file1.md file2.md

# 2. Remove less complete version
git rm docs/path/to/duplicate.md

# 3. Update any references
grep -r "duplicate.md" docs/

# 4. Commit
git commit -m "docs: Remove duplicate X (kept final version in Y)"
```

---

## 📊 Quality Metrics

### Documentation Health Indicators

**Green (Healthy):**
- ✅ All user docs ≤ Grade 5.0
- ✅ No duplicate content
- ✅ All cross-references work
- ✅ Version numbers consistent
- ✅ Files in correct directories
- ✅ Evergreen naming followed

**Yellow (Needs Attention):**
- ⚠️ Some user docs > Grade 5.0
- ⚠️ Minor cross-reference issues
- ⚠️ 1-2 dated filenames remaining
- ⚠️ Files need categorization

**Red (Action Required):**
- ❌ Multiple duplicates found
- ❌ Broken cross-references
- ❌ Version inconsistencies
- ❌ Many dated filenames
- ❌ Disorganized structure

### Current Status (Nov 18, 2025)

**Overall Health:** ✅ GREEN

- Total files: 56 markdown files
- Duplicates: 0 (removed Nov 18)
- Evergreen naming: 100% (all reports)
- Organization: Excellent (consolidated Nov 18)
- Cross-references: All working
- Version consistency: 100% (v2.0.4)
- Documentation consolidation: 40% duplication removed (203 lines net reduction)

---

## 🎯 Best Practices

### DO:
- ✅ Use evergreen filenames for all ongoing documents
- ✅ Archive planning docs when milestones complete
- ✅ Delete duplicates immediately when found
- ✅ Verify cross-references after any rename
- ✅ Run quarterly audits
- ✅ Use `git mv` to preserve history
- ✅ Update README files when adding new docs
- ✅ Include "Last Updated" in all documents
- ✅ Test user docs for Grade 5.0 compliance

### DON'T:
- ❌ Add dates to filenames (use internal versioning)
- ❌ Keep draft versions after final is complete
- ❌ Move files without updating cross-references
- ❌ Skip readability checks for user docs
- ❌ Create new directories without purpose
- ❌ Use `git rm` without checking references
- ❌ Commit renamed files without updating links
- ❌ Archive current/active documentation

---

## 📞 Questions & Support

**Documentation Issues:**
- Report via GitHub Issues: https://github.com/webbwr/AsciiDoctorArtisan/issues
- Tag with: `documentation` label

**Audit Reports:**
- Store in: `docs/reports/`
- Use evergreen naming: `documentation-audit.md`
- Update quarterly

**Standards Updates:**
- Propose changes via PR
- Update this document
- Notify in CHANGELOG.md

---

**Next Audit:** February 15, 2026 (Q1 2026)
**Responsible:** Grandmaster Librarian
**Status:** ✅ Standards Active and Enforced

---

## Recent Improvements

### November 18, 2025 Consolidation

**Changes Made:**
- Documentation consolidation: 40% duplication removed
- 4 files deleted (duplicate content)
- 203 lines net reduction
- Testing docs merged into unified TESTING_README.md
- Version updated to v2.0.4 across all docs
- Test count updated to 5,498 tests

**Files Affected:**
- DOCUMENTATION_INDEX.md - Updated stats and recent changes
- DOCUMENTATION_STANDARDS.md - Updated version and status
- documentation-review.md - Updated quality metrics
- All cross-references verified

**Quality Improvements:**
- Eliminated redundant archive strategy details
- Removed duplicate file organization content
- Consolidated quality assessment sections
- Maintained unique content from each file
