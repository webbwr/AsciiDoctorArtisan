# Claude Code Skills

This directory contains custom skills for Claude Code.

## Available Skills

### grandmaster-techwriter.md

**Purpose:** Write and verify technical documentation at ≤5th grade reading level while preserving all technical content.

**Key Features:**
- Automatic readability testing (Flesch-Kincaid)
- Japanese MA (間) principles - minimalism and negative space
- Socratic teaching method - questions guide understanding
- Self-iterating until Grade 5.0 achieved
- Technical accuracy verification
- User delight optimization

**Usage:**
```
@grandmaster-techwriter [file-to-improve]
```

Or in conversation:
```
Write documentation for [topic] using the grandmaster-techwriter skill
```

**Supporting Tools:**
- `scripts/readability_check.py` - Automatic readability verification

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
