# Proposal: Add Spell Checker

**Status**: Draft (Example)
**Author**: AsciiDoc Artisan Team
**Date**: October 2025
**Reading Level**: Grade 6.0

## Problem

Users make spelling mistakes when writing documents. The program doesn't tell them when words are spelled wrong. This makes documents look bad and unprofessional.

## Solution

Add a spell checker that highlights misspelled words with a red wavy line. Users can right-click to see suggested corrections. The spell checker will use the system's spell check library or a Python library like `pyspellchecker`.

## Examples

### Example 1: Highlight Misspelled Words

**Before**:
```
User types: "The qwick brown fox jumps over the lasy dog"
Program shows: Plain text with no highlighting
```

**After**:
```
User types: "The qwick brown fox jumps over the lasy dog"
Program shows: Red wavy lines under "qwick" and "lasy"
```

### Example 2: Show Suggestions

**Before**:
```
User right-clicks misspelled word
Program shows: Regular context menu (cut, copy, paste)
```

**After**:
```
User right-clicks "qwick"
Program shows:
  - quick ← (suggestion)
  - quirk
  - Add to dictionary
  - Ignore
  ---
  - Cut
  - Copy
  - Paste
```

## Benefits

1. **Better documents** - Fewer spelling mistakes
2. **Faster writing** - Catch errors as you type
3. **Professional look** - Documents look more polished
4. **Easy to use** - Works like Word spell checker

## Risks

1. **Slow performance** - Could slow down typing on big documents
   - **How we handle it**: Only check visible text, use background thread

2. **Wrong language** - Might check in wrong language
   - **How we handle it**: Let user pick language in settings

3. **Technical words** - Might flag AsciiDoc keywords as wrong
   - **How we handle it**: Add common AsciiDoc words to dictionary

## Questions

- Which spell check library should we use?
- Should we check spelling as user types or only when they stop?
- Should we save user's custom dictionary?
- What languages should we support?

---

**Document Info**: Example proposal | Reading level Grade 6.0 | OpenSpec format
