# Grandmaster TechWriter (TW) - Quick Reference

**Registered:** ✅ Yes (System-wide)
**Aliases:** `tw`, `techwriter`, `grade5`
**Auto-activate:** ✅ Enabled for all .md, .rst, .txt, .adoc files

## Quick Commands

```bash
# Check readability of any file
tw check README.md

# Improve a document (interactive)
tw improve docs/guide.md

# Watch file and auto-check on changes
tw watch CHANGELOG.md

# Batch check all markdown files in a directory
tw batch docs/

# Show help
tw help
```

## When It Auto-Activates

The skill automatically runs when you:
- Write or edit documentation files (.md, .rst, .adoc, .txt)
- Create README, CONTRIBUTING, or CHANGELOG files
- Use words like "document" or "explain" in commands

## What It Does

**Phase 1: SPECIFY** - Understand intent
**Phase 2: PLAN** - Structure content
**Phase 3: DRAFT** - Write first version
**Phase 4: ANALYZE** - Check metrics
**Phase 5: REFINE** - Simplify and improve
**Phase 6: VALIDATE** - Verify all checks pass
**Phase 7: DELIGHT** - Final polish

## Target Metrics

- **Grade Level:** ≤5.0 (5th grade)
- **Reading Ease:** ≥70 (Easy)
- **Sentence Length:** ≤15 words average
- **Syllables:** ≤1.5 per word

## Key Principles

**MA (間) - Japanese Minimalism:**
- Short sentences create breathing room
- White space is content
- One idea per sentence
- Remove the unnecessary

**Socratic Method:**
- Lead with questions
- Build concepts progressively
- Help readers discover understanding

**Technical Integrity:**
- Never sacrifice accuracy
- Preserve precision
- Explain specialized terms
- Verify all facts

## File Locations

- Skill file: `.claude/skills/grandmaster-techwriter.md`
- Wrapper script: `scripts/tw`
- Readability checker: `scripts/readability_check.py`
- Config: `.claude/config.json`
- Manifest: `.claude/skills/manifest.json`

## Examples

**Before (Grade 10):**
```
The application utilizes a multi-threaded architecture where Git
operations are executed asynchronously via QThread workers to
prevent blocking the main UI event loop.
```

**After (Grade 5):**
```
The app uses multiple threads. This means work happens at the
same time.

Git tasks run in worker threads. These are separate from the
main window. Why? So the app stays fast. The screen never freezes.
```

## Testing

```bash
# Test any file
python3 scripts/readability_check.py README.md

# Test from stdin
cat file.md | python3 scripts/readability_check.py --stdin

# Get JSON output
python3 scripts/readability_check.py --json README.md
```

## Getting Help

```bash
tw help                    # Show command help
cat .claude/skills/grandmaster-techwriter.md  # Read full methodology
```

---

*Quick Reference - Last updated: October 30, 2025*
