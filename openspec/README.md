# OpenSpec Directory

**Reading Level**: Grade 6.0
**Based On**: OpenSpec framework

## What This Is

This folder holds our specification system. It helps us plan and track changes to AsciiDoc Artisan.

## Structure

```
openspec/
├── changes/         (Proposed changes - things we want to add)
│   ├── _template/   (Copy this to start a new change)
│   └── spell-checker/ (Example: adding spell check feature)
├── archive/         (Completed changes - things we already did)
└── README.md        (This file)
```

**Note**: The main spec file is `SPECIFICATIONS.md` in the root directory.

## How to Use This

### To Propose a New Feature

1. **Copy the template**:
   ```bash
   cp -r openspec/changes/_template openspec/changes/your-feature-name
   ```

2. **Fill out the files**:
   - `proposal.md` - Why we need it, how it works
   - `tasks.md` - What work needs to be done
   - `design.md` - Technical details
   - `specs/` - What requirements change

3. **Get feedback**:
   - Share with team
   - Discuss and improve
   - Get approval

4. **Build it**:
   - Follow the tasks
   - Check off items as you go
   - Test everything

5. **Archive it**:
   - Move to `archive/YYYY-MM-feature-name/`
   - Update main `SPECIFICATIONS.md`
   - Close related issues

### To View Changes

**See all proposed changes**:
```bash
ls openspec/changes/
```

**See completed changes**:
```bash
ls openspec/archive/
```

## File Templates

### proposal.md
- Problem statement
- Proposed solution
- Examples
- Benefits and risks
- Open questions

### tasks.md
- Planning tasks
- Design tasks
- Code tasks
- Testing tasks
- Review and deploy tasks

### design.md
- How it works
- What components change
- UI mockups
- API changes
- Testing strategy

### specs/*.md
- ADDED requirements
- MODIFIED requirements
- REMOVED requirements
- Uses Given/When/Then format

## Validation

Check if spec follows our format:

```bash
./scripts/validate-spec.sh
```

This checks:
- SHALL/MUST language
- Given/When/Then scenarios
- All domain sections present
- Version metadata
- Reading level

## Example

Look at `openspec/changes/spell-checker/` to see a complete example of how to propose a feature.

## Reading Level

All files in openspec should be written at Grade 6.0 level or below. Use:
- Short sentences
- Simple words
- Active voice
- Clear examples

Test with:
```bash
python3 check_readability.py openspec/changes/your-feature/proposal.md
```

## Questions?

- See main `SPECIFICATIONS.md` for current requirements
- See `SPEC_IMPROVEMENT_PLAN.md` for why we organized it this way
- See `OPENSPEC_ANALYSIS.md` for analysis of the OpenSpec framework

---

**Document Info**: OpenSpec directory guide | Reading level Grade 6.0 | October 2025
