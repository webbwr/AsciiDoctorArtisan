# AsciiDoc Artisan Specifications

**Reading Level**: Grade 8.0 (Middle School)

This document lists all the specifications (rules and requirements) for building AsciiDoc Artisan.

## What Are Specifications?

Specifications are like a blueprint for building a house. They tell us:
- What the program must do
- How it should work
- What features it needs
- How to test if it works right

Think of them as a checklist we follow when building the program.

## Our Specification Files

We have several specification documents. Each one serves a different purpose:

### Main Specifications

| File | Size | Reading Level | Purpose | For Who |
|------|------|---------------|---------|---------|
| **SPECIFICATION_SIMPLE.md** | 2,557 lines | Grade 6.4 | Easy-to-read version | Everyone |
| **SPECIFICATION.md** | 1,261 lines | Grade 13.4 | Technical details | Developers |
| **project-specification.md** | 503 lines | Grade 9.6 | Current project plan | Team members |
| **SPECIFICATION_ANALYSIS.md** | 204 lines | Grade 11.6 | How specs changed | Project managers |

### Archived Files

| File | Size | Reading Level | Status |
|------|------|---------------|--------|
| **project-specification-v1.0-ARCHIVED.md** | 582 lines | Grade 18.1 | Old version (saved for history) |

## Which One Should You Read?

**If you're new** → Read **SPECIFICATION_SIMPLE.md** (Grade 6.4)
- Written in simple words
- Easy to understand
- Covers all the basics
- Good starting point

**If you're building the program** → Read **SPECIFICATION.md** (Grade 13.4)
- Full technical details
- All requirements listed
- Testing procedures
- Security rules

**If you're planning work** → Read **project-specification.md** (Grade 9.6)
- Current development plan
- What we're building now
- Upcoming features
- Timeline

**If you're checking progress** → Read **SPECIFICATION_ANALYSIS.md** (Grade 11.6)
- Compares old and new specs
- Shows what changed
- Explains why we changed it

## Location of Spec Files

All specification files are in:
```
.specify/specs/
├── SPECIFICATION_SIMPLE.md          (recommended for beginners)
├── SPECIFICATION.md                 (full technical spec)
├── project-specification.md         (current plan)
├── SPECIFICATION_ANALYSIS.md        (change analysis)
└── project-specification-v1.0-ARCHIVED.md (old version)
```

## Key Information in the Specs

### Version Information
- **Current Version**: 1.1.0
- **Status**: Active development
- **Last Updated**: October 2024

### What the Program Must Do

The specifications define these main requirements:

**1. Core Features** (Must Have):
- Live preview of AsciiDoc documents
- Save and open files
- Convert documents (Word, PDF to AsciiDoc)
- Export to multiple formats (HTML, PDF, etc.)
- Dark mode theme
- Keyboard shortcuts

**2. Git Features** (Must Have):
- Commit changes
- Push to remote
- Pull from remote
- Status display

**3. Safety Features** (Must Have):
- Safe file saving (no data loss)
- Path security (prevent bad file access)
- Input validation
- Error handling

**4. AI Features** (Optional):
- AI-enhanced document conversion
- Better quality conversions
- Automatic fallback to Pandoc

### Technical Requirements

**Programming Language**: Python 3.11 or newer

**Main Libraries**:
- PySide6 (version 6.9.0+) - Makes windows and buttons
- asciidoc3 (version 10.2.1+) - Converts AsciiDoc to HTML
- pypandoc (version 1.13+) - Document conversion
- Pandoc (system binary) - Required for conversions

**Testing Requirements**:
- All features must have tests
- Tests must pass before release
- Coverage should be 70% or higher
- Must work on Windows, Mac, and Linux

### Performance Requirements

- Preview updates in less than 500ms
- Program starts in less than 3 seconds
- File saves complete in less than 1 second
- No freezing during operations

### Security Requirements

1. **File Safety**:
   - Use atomic file saves
   - Validate all file paths
   - Check permissions before writing

2. **Input Validation**:
   - Check all user inputs
   - Prevent code injection
   - Validate file formats

3. **Credentials**:
   - Store API keys securely
   - Never log sensitive data
   - Use environment variables

## How We Track Requirements

Each requirement has a code like "FR-001" (Functional Requirement 001) or "NFR-001" (Non-Functional Requirement 001).

**Functional Requirements (FR)**: What the program does
- FR-001: Open AsciiDoc files
- FR-002: Save AsciiDoc files
- FR-003: Live preview
- And so on...

**Non-Functional Requirements (NFR)**: How it should work
- NFR-001: Fast performance
- NFR-002: Easy to use
- NFR-003: Secure
- And so on...

## How We Test Against Specs

We check each requirement to make sure it works:

1. **Unit Tests**: Test individual pieces
2. **Integration Tests**: Test how pieces work together
3. **Manual Tests**: People try using it
4. **Platform Tests**: Check on Windows, Mac, Linux

Every requirement in the spec has a matching test.

## Making Changes to Specs

If we need to change a specification:

1. **Discuss** why we need the change
2. **Document** what will change
3. **Update** all spec files
4. **Review** with the team
5. **Test** the new requirement

Changes are tracked in SPECIFICATION_ANALYSIS.md.

## Reading the Specs

### For Beginners

Start with **SPECIFICATION_SIMPLE.md**:
1. Read the "Quick Start" section first
2. Look at "What This Program Does"
3. Check "User Stories" to see examples
4. Skip the technical parts for now

### For Developers

Start with **SPECIFICATION.md**:
1. Read all functional requirements (FR-*)
2. Check non-functional requirements (NFR-*)
3. Review technical architecture section
4. Study testing requirements

### For Project Managers

Start with **project-specification.md**:
1. Check current status
2. Review upcoming milestones
3. Look at resource requirements
4. Check timeline

## Specification Summary

Here's what each main requirement category covers:

### File Operations (FR-001 to FR-020)
- Opening files
- Saving files
- File formats supported
- Auto-save features

### Editing Features (FR-021 to FR-040)
- Text editing
- Syntax highlighting
- Find and replace
- Line numbers

### Preview Features (FR-041 to FR-050)
- Live HTML preview
- Synchronized scrolling
- Preview updates
- Fallback modes

### Conversion Features (FR-051 to FR-065)
- Import formats (DOCX, PDF)
- Export formats (HTML, PDF, etc.)
- AI conversion
- Quality checks

### Git Features (FR-066 to FR-075)
- Commit
- Push
- Pull
- Status display

### UI Features (FR-076 to FR-090)
- Dark mode
- Font zoom
- Window state
- Keyboard shortcuts

## Questions About Specs?

If you have questions about the specifications:

1. **Read SPECIFICATION_SIMPLE.md first** - Simplest version
2. **Check the specific requirement** - Find the FR or NFR code
3. **Look at examples** - User stories show how it works
4. **Ask on GitHub** - Create an issue with your question

## Keeping Specs Updated

We update specifications when:
- Adding new features
- Changing how something works
- Fixing bugs that need spec changes
- Getting feedback from users

All changes are documented and reviewed before being accepted.

## Summary

- **5 specification files** total
- **Average reading level**: Grade 11.8 (varies by file)
- **Easiest to read**: SPECIFICATION_SIMPLE.md (Grade 6.4)
- **Most detailed**: SPECIFICATION.md (1,261 lines)
- **Current version**: 1.1.0
- **Status**: Active development

---

**Document Info**: Location `.specify/specs/` | Reading level Grade 8.0 | Last updated: 2025
