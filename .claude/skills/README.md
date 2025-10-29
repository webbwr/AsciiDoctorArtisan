# Claude Code Skills

This directory contains custom skills for Claude Code.

## Available Skills

### grandmaster-techwriter.md

**Purpose:** Write and verify technical documentation at ≤5th grade reading level while preserving all technical content.

**Methodology:** Combines three powerful approaches:
- **Japanese MA (間)** - Minimalism and negative space
- **Socratic Method** - Questions guide discovery
- **GitHub Spec-Kit** - Spec-driven development with validation

**Key Features:**
- 7-phase spec-driven process (Specify → Plan → Draft → Analyze → Refine → Validate → Delight)
- "Unit tests for English" (completeness, clarity, consistency checklists)
- Automatic readability testing (Flesch-Kincaid)
- Self-iterating until Grade 5.0 + all checklists pass
- Technical accuracy verification
- Living documentation approach
- User delight optimization

**Auto-Activation:** ✅ ENABLED

This skill automatically activates for all documentation operations:
- Writing/editing .md, .rst, .adoc, .txt files
- Creating README, CONTRIBUTING, CHANGELOG files
- Any operation involving "document" or "explain"

No manual invocation needed! The skill runs automatically, scores documents, and ensures Grade 5.0 compliance.

**Manual Usage (if needed):**
```bash
@grandmaster-techwriter [file-to-improve]

# Or use CLI wrapper
./scripts/techwriter check README.md
./scripts/techwriter watch docs/guide.md
./scripts/techwriter batch docs/
```

**Supporting Tools:**
- `scripts/readability_check.py` - Automatic readability verification
- `scripts/techwriter` - CLI wrapper with watch/batch modes
- `.claude/config.json` - Auto-activation configuration
- `.git/hooks/pre-commit-readability` - Git hook for validation
- `.pre-commit-config.yaml` - Pre-commit readability check

## Testing Readability

Test any document's readability:

```bash
# Test a file
python3 scripts/readability_check.py README.md

# Test from stdin
cat file.md | python3 scripts/readability_check.py --stdin

# Get JSON output
python3 scripts/readability_check.py --json README.md
```

**Metrics:**
- **Grade Level:** Target ≤5.0 (5th grade)
- **Reading Ease:** Target ≥70 (Easy)
- **Sentence Length:** Target ≤15 words average
- **Syllables:** Target ≤1.5 per word

## Philosophy

> "Perfection is achieved not when there is nothing more to add,
> but when there is nothing left to take away."

These skills help create technical documentation that:
- Respects the reader's time
- Maintains technical accuracy
- Achieves maximum clarity
- Delights users

## Adding New Skills

1. Create `skillname.md` in this directory
2. Follow the existing pattern
3. Document the skill in this README
4. Add supporting tools to `scripts/` if needed

---

*Last updated: October 29, 2025*
