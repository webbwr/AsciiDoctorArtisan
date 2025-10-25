# AsciiDoc Artisan Specification Improvement Plan

**Reading Level**: Grade 5.0 (Elementary)
**Based On**: OpenSpec analysis
**Purpose**: Make our specs better
**Date**: October 2025

## What We Learned from OpenSpec

OpenSpec taught us these ideas:

### Good Ideas to Copy

1. **Separate current from future**
   - Current specs = what exists now
   - Change specs = what we're building

2. **Group related things**
   - Keep feature specs together
   - Add tasks and designs in one place
   - Easy to find everything

3. **Clear workflow**
   - Draft proposal
   - Review and agree
   - Build it
   - Ship it
   - Archive it

4. **Make specs testable**
   - Every requirement has scenarios
   - Use SHALL/MUST language
   - Clear pass/fail tests

### Problems to Avoid

1. **Too complex** - Keep it simple
2. **Too long** - Split into small files
3. **Hard to read** - Use grade 5 language
4. **No examples** - Show real cases
5. **No visuals** - Add pictures

## Current State of Our Specs

### What We Have Now

**Main Spec** (SPECIFICATIONS.md):
- Grade 3.1 reading level ✓
- 463 lines
- All in one file
- No change tracking
- No task lists

**Technical Specs** (.specify/specs/):
- 5 different files
- Grade 6.4 to 18.1 reading level
- Scattered information
- Hard to update

### What Works

**Good things**:
1. Simple language (grade 3-5)
2. Clear requirements
3. Checkmarks for status
4. Examples included

### What Needs Work

**Problems**:
1. No way to track changes
2. No task management
3. No proposal system
4. Hard to work with AI
5. No version history
6. One big file

## Proposed New Structure

### OpenSpec-Style Organization

```
asciidoc-artisan/
├── specs/                  (Current truth)
│   ├── core.md            (Core features)
│   ├── editor.md          (Editor features)
│   ├── preview.md         (Preview features)
│   ├── git.md             (Git features)
│   ├── conversion.md      (File conversion)
│   └── ui.md              (User interface)
├── changes/               (Proposed changes)
│   └── [feature-name]/    (One feature)
│       ├── proposal.md    (Why we need it)
│       ├── tasks.md       (What to do)
│       ├── design.md      (How to build it)
│       └── specs/         (Spec changes)
│           └── [domain].md
└── archive/               (Completed changes)
    └── [date]-[feature]/  (Old proposals)
```

### Spec File Format

**Each spec file has**:
```markdown
# [Domain] Specifications

## Overview
[What this domain covers]

## Requirements

### Requirement: [Name]
[What it must do]

#### Scenario: [Test Case]
**Given**: [Starting state]
**When**: [Action happens]
**Then**: [Result must be]

#### Scenario: [Another Test]
...
```

### Change Proposal Format

**proposal.md**:
```markdown
# Proposal: [Feature Name]

## Problem
[What problem does this solve?]

## Solution
[How will we solve it?]

## Benefits
[Why is this good?]

## Risks
[What could go wrong?]
```

**tasks.md**:
```markdown
# Tasks for [Feature]

## Backend
- [ ] Task 1
- [ ] Task 2

## Frontend
- [ ] Task 3
- [ ] Task 4

## Testing
- [ ] Test 1
- [ ] Test 2
```

**specs/[domain].md**:
```markdown
## ADDED Requirements

### Requirement: [New Thing]
[Description]

#### Scenario: [Test]
...

## MODIFIED Requirements

### Requirement: [Changed Thing]
[New description]

## REMOVED Requirements

### Requirement: [Deleted Thing]
[Why we removed it]
```

## Implementation Plan

### Phase 1: Reorganize (Week 1)

**Goal**: Split into manageable pieces

**Tasks**:
1. Create new directory structure
2. Split SPECIFICATIONS.md into domains:
   - core.md (main features)
   - editor.md (text editing)
   - preview.md (live preview)
   - git.md (version control)
   - conversion.md (file types)
   - ui.md (interface)
3. Keep reading level at grade 5
4. Add examples to each domain

**Success**: Easy to find specific features

### Phase 2: Add Change System (Week 2)

**Goal**: Track new features properly

**Tasks**:
1. Create changes/ directory
2. Create first example change
3. Write change templates
4. Document workflow
5. Add validation script

**Success**: Can propose changes easily

### Phase 3: Improve Format (Week 3)

**Goal**: Make specs testable

**Tasks**:
1. Add scenarios to all requirements
2. Use SHALL/MUST language
3. Make tests clear
4. Add pass/fail criteria
5. Link to code

**Success**: Every requirement is testable

### Phase 4: Add Visuals (Week 4)

**Goal**: Make it easy to understand

**Tasks**:
1. Create workflow diagram
2. Add file structure picture
3. Show example proposals
4. Create quick reference
5. Add video walkthrough

**Success**: New contributors understand fast

### Phase 5: Tools and Automation (Week 5)

**Goal**: Make it easy to use

**Tasks**:
1. Create validation script
2. Add change generator
3. Build archive tool
4. Create templates
5. Add CLI helpers

**Success**: Automated checks work

## Specific Changes to Make

### Current SPECIFICATIONS.md

**Split into 6 files**:

**specs/core.md**:
- What AsciiDoc Artisan is
- Who uses it
- Main features
- Version info

**specs/editor.md**:
- Text editing
- Find and replace
- Go to line
- Keyboard shortcuts
- Status bar

**specs/preview.md**:
- Live HTML preview
- Update timing
- Synchronized scrolling
- Error handling
- Fallback modes

**specs/git.md**:
- Commit
- Push
- Pull
- Status display
- Error messages

**specs/conversion.md**:
- Import formats (.docx, .pdf)
- Export formats (HTML, PDF, etc.)
- AI conversion
- Quality checks
- Error handling

**specs/ui.md**:
- Window layout
- Menus
- Dark mode
- Font zoom
- Settings

### Add Change Template

**changes/_template/proposal.md**:
```markdown
# Proposal: [Feature Name]

**Status**: Draft
**Author**: [Your Name]
**Date**: [Today]

## Problem

What problem does this solve?

## Solution

How will we solve it?

## Examples

Show how it works:

### Example 1
[Before and after]

### Example 2
[Another case]

## Benefits

Why is this good:
1. Benefit 1
2. Benefit 2

## Risks

What could go wrong:
1. Risk 1 (and how we handle it)
2. Risk 2 (and how we handle it)

## Questions

What we need to decide:
- Question 1?
- Question 2?
```

### Add Validation Script

**scripts/validate-spec.sh**:
```bash
#!/bin/bash
# Check spec format

echo "Checking specs..."

# Check each requirement has scenario
# Check SHALL/MUST language used
# Check no broken links
# Check reading level

echo "Validation complete!"
```

### Add Quick Reference

**SPEC_GUIDE.md**:
```markdown
# Spec Guide (5 minutes)

## How to Write a Requirement

```markdown
### Requirement: Dark Mode Toggle

The program SHALL provide a button to switch colors.

#### Scenario: Toggle Dark Mode

**Given**: Program is in light mode
**When**: User clicks dark mode button
**Then**: Colors change to dark
```

## How to Propose a Change

1. Create folder: `changes/my-feature/`
2. Write proposal.md
3. List tasks in tasks.md
4. Show spec changes in specs/
5. Ask for review

## How to Test a Requirement

Each scenario shows:
- **Given** = Starting point
- **When** = What happens
- **Then** = Expected result

If result matches, test passes!
```

## Workflow for Contributors

### Adding New Features

**Step 1: Propose**
```bash
# Create change folder
mkdir -p changes/dark-mode-toggle

# Write proposal
# - What problem?
# - How to solve?
# - Why good?
```

**Step 2: Plan**
```bash
# List all tasks
# Break into small steps
# Assign to domains
```

**Step 3: Spec**
```bash
# Write requirements
# Add test scenarios
# Show before/after
```

**Step 4: Review**
```bash
# Team reviews proposal
# Discuss changes
# Agree on approach
```

**Step 5: Build**
```bash
# Work through tasks
# Check off completed
# Test scenarios
```

**Step 6: Archive**
```bash
# Move to archive/
# Update main specs
# Close proposal
```

### Modifying Existing Features

**Step 1: Find Current Spec**
```bash
# Look in specs/ folder
# Find the domain
# Read current requirement
```

**Step 2: Propose Change**
```bash
# Create change folder
# Show MODIFIED requirements
# Explain why changing
```

**Step 3: Follow Workflow**
```bash
# Same as adding features
# Review → Build → Archive
```

## Success Metrics

### Usability Metrics

**Measure**:
- Time to find a spec (goal: <1 minute)
- Time to propose change (goal: <5 minutes)
- Reading level (goal: grade 5)
- Contributor satisfaction (goal: 8/10)

### Quality Metrics

**Measure**:
- Requirements with scenarios (goal: 100%)
- Testable requirements (goal: 100%)
- Broken links (goal: 0)
- Outdated specs (goal: <5%)

### Adoption Metrics

**Measure**:
- Contributors using system (goal: 80%)
- Changes proposed (goal: 10/month)
- Specs updated (goal: weekly)
- Community satisfaction (goal: 9/10)

## Benefits of New System

### For Users

**Better**:
1. Easy to find what program can do
2. Clear test cases
3. Simple language
4. Visual guides

### For Contributors

**Better**:
1. Know where to add specs
2. Propose changes easily
3. Track progress with tasks
4. See history in archive

### For Project

**Better**:
1. Organized specifications
2. Change tracking
3. Version history
4. AI-friendly format

## Migration Steps

### Week 1: Setup

**Do**:
1. Create new directories
2. Split current spec
3. Keep both versions
4. Add README explaining

**Don't break**:
- Keep old files
- Add redirects
- Update links

### Week 2: First Change

**Do**:
1. Create example change
2. Document workflow
3. Get team feedback
4. Refine process

**Learn**:
- What works?
- What's confusing?
- What's missing?

### Week 3: Full Migration

**Do**:
1. Move all specs
2. Create templates
3. Add validation
4. Update docs

**Verify**:
- All specs moved
- Links work
- Examples clear

### Week 4: Launch

**Do**:
1. Announce new system
2. Create tutorial
3. Record video
4. Get feedback

**Support**:
- Answer questions
- Fix issues
- Improve docs

## Comparison: Before and After

### Before (Current)

**Structure**:
```
SPECIFICATIONS.md (one big file)
.specify/specs/ (5 scattered files)
```

**Problems**:
- Hard to find things
- No change tracking
- Can't see history
- No task management

**Reading Level**: Grade 3.1 (good!)

### After (Proposed)

**Structure**:
```
specs/ (6 domain files)
changes/ (active proposals)
archive/ (completed changes)
```

**Benefits**:
- Easy to navigate
- Track all changes
- See full history
- Manage tasks

**Reading Level**: Grade 5.0 (still simple!)

## Next Steps

### Immediate (This Week)

1. Get team feedback on plan
2. Create directory structure
3. Split SPECIFICATIONS.md
4. Create first example change

### Short Term (This Month)

1. Complete migration
2. Add templates
3. Write validation script
4. Create tutorial

### Long Term (3 Months)

1. Full adoption by team
2. All new features use system
3. Regular spec updates
4. Community contributions

## Questions to Answer

### Before Starting

- Does team agree with approach?
- Should we keep old format too?
- What's the migration timeline?
- Who will maintain specs?

### During Migration

- Are specs easy to find?
- Is change process clear?
- Do tasks help?
- What's confusing?

### After Launch

- Are people using it?
- Is it better than before?
- What needs improvement?
- Should we add features?

## Conclusion

**Main Ideas**:
1. Split big spec into small files
2. Track changes properly
3. Make it easy to contribute
4. Keep it simple (grade 5)

**Why Do This**:
- Easier to maintain
- Better for AI
- Clear for contributors
- Track history properly

**When to Start**:
Now! Small steps, big improvement.

---

**Document Info**: Spec improvement plan | Reading level Grade 5.0 | Based on OpenSpec | October 2025
