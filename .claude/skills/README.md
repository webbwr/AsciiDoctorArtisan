# Claude Code Skills - Quick Reference

This directory contains custom skills for Claude Code.

## Grandmaster TechWriter (TW)

**Status:** ✅ Registered & Auto-Activated
**Aliases:** `tw`, `techwriter`, `grade5`
**Triggers:** All .md, .rst, .txt, .adoc files

### Quick Commands

```bash
tw check README.md              # Check readability
tw improve docs/guide.md        # Apply improvements
tw watch CHANGELOG.md           # Watch for changes
tw batch docs/                  # Check all .md files
tw help                         # Show help
```

### What It Does

Writes technical documentation at ≤5th grade reading level while preserving 100% technical accuracy.

**7-Phase Process:**
1. **SPECIFY** - Understand intent & target audience
2. **PLAN** - Structure content logically
3. **DRAFT** - Write first version
4. **ANALYZE** - Check readability metrics
5. **REFINE** - Simplify & improve clarity
6. **VALIDATE** - Verify all checks pass
7. **DELIGHT** - Final polish for user experience

**Methodology:**
- **Japanese MA (間)** - Minimalism and negative space
- **Socratic Method** - Progressive concept building
- **Spec-Kit Validation** - "Unit tests for English"

### Target Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Grade Level | ≤5.0 | 5th grade reading level |
| Reading Ease | ≥70 | Easy to understand |
| Sentence Length | ≤15 words | Quick comprehension |
| Syllables/Word | ≤1.5 | Simple vocabulary |

### Auto-Activation

The skill automatically runs when you:
- Write or edit documentation files (.md, .rst, .adoc, .txt)
- Create README, CONTRIBUTING, or CHANGELOG files
- Use commands containing "document" or "explain"

**No manual invocation needed** - it works behind the scenes!

### Manual Usage

**Via Claude Code:**
```
@grandmaster-techwriter [file-to-improve]
```

**Via CLI:**
```bash
# Check readability
python3 scripts/readability_check.py README.md

# Get JSON output
python3 scripts/readability_check.py --json README.md

# Test from stdin
cat file.md | python3 scripts/readability_check.py --stdin
```

### Example Transformation

**Before (Grade 10.2):**
```
The application utilizes a multi-threaded architecture where Git
operations are executed asynchronously via QThread workers to
prevent blocking the main UI event loop.
```

**After (Grade 4.8):**
```
The app uses multiple threads. This means work happens at the
same time.

Git tasks run in worker threads. These are separate from the
main window. Why? So the app stays fast. The screen never freezes.
```

### Key Principles

**MA (間) - Minimalism:**
- Short sentences create breathing room
- White space is content
- One idea per sentence
- Remove the unnecessary

**Technical Integrity:**
- Never sacrifice accuracy
- Preserve precision
- Explain specialized terms on first use
- Verify all facts

**User Delight:**
- Make reading effortless
- Progressive disclosure of complexity
- Clear examples
- Actionable guidance

### File Locations

```
.claude/skills/
├── grandmaster-techwriter.md    # Skill implementation (932 lines)
├── manifest.json                 # Auto-activation config
├── aliases.sh                    # Shell aliases
└── README.md                     # This file

scripts/
├── tw                            # CLI wrapper
└── readability_check.py          # Automatic verification
```

### Adding New Skills

1. Create `skillname.md` in this directory
2. Add entry to `manifest.json`
3. Document it in this README
4. Add supporting tools to `scripts/` if needed

### Philosophy

> "Perfection is achieved not when there is nothing more to add,
> but when there is nothing left to take away." — Antoine de Saint-Exupéry

These skills help create documentation that:
- Respects the reader's time
- Maintains technical accuracy
- Achieves maximum clarity
- Delights users

---

*Last updated: October 31, 2025*
