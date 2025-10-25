# Tasks for Spell Checker

**Status**: Draft (Example)
**Reading Level**: Grade 6.0

## Planning

- [x] Write proposal
- [ ] Get team feedback
- [ ] Decide which library to use
- [ ] Update proposal based on feedback
- [ ] Get final approval

## Design

- [ ] Design spell check UI (red wavy lines)
- [ ] Design suggestion menu
- [ ] Design settings panel for language selection
- [ ] Design custom dictionary storage format
- [ ] Review design with team

## Code Changes

### Backend

- [ ] Install spell check library (`pyspellchecker` or similar)
- [ ] Create `SpellChecker` class in new file `spell_checker.py`
- [ ] Add method to check word spelling
- [ ] Add method to get suggestions for misspelled word
- [ ] Add method to add word to custom dictionary
- [ ] Add method to load/save custom dictionary
- [ ] Create background worker for spell checking (`SpellCheckWorker`)

### Frontend/UI

- [ ] Add red wavy underline painter to editor widget
- [ ] Update editor to highlight misspelled words
- [ ] Add right-click context menu for suggestions
- [ ] Add "Add to Dictionary" option
- [ ] Add "Ignore" option
- [ ] Add language selection in Preferences dialog
- [ ] Show spell check status in status bar

### Documentation

- [ ] Update SPECIFICATIONS.md with spell check requirements
- [ ] Update README.md with spell check feature
- [ ] Update how-to-use.md with spell check instructions
- [ ] Add comments to spell checker code

## Testing

- [ ] Write unit tests for `SpellChecker` class
- [ ] Write tests for custom dictionary
- [ ] Write tests for background worker
- [ ] Test highlighting in editor
- [ ] Test context menu
- [ ] Test on Windows
- [ ] Test on Linux
- [ ] Test on Mac
- [ ] Test with real users

## Review

- [ ] Code review
- [ ] Test review
- [ ] Documentation review
- [ ] Performance review (check if typing is still fast)
- [ ] Final approval

## Deploy

- [ ] Merge to main branch
- [ ] Create release notes
- [ ] Tag version 1.2.0
- [ ] Announce new feature to users

## Archive

- [ ] Move to archive/2025-10-spell-checker/
- [ ] Update main SPECIFICATIONS.md
- [ ] Close related GitHub issues
- [ ] Document what we learned

---

**Document Info**: Example tasks | Reading level Grade 6.0 | OpenSpec format
