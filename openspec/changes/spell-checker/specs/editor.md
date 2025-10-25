# Specification Changes for Spell Checker

**Reading Level**: Grade 6.0
**Status**: Draft (Example)
**Domain**: Editor Specifications

## Overview

This shows what requirements change to add spell checking to the editor.

## ADDED Requirements

### Requirement: Spell Checking

The program SHALL check spelling as user types.

#### Scenario: Highlight Misspelled Word

**Given**: User types "helo world"
**When**: User stops typing
**Then**: Red wavy line appears under "helo"

#### Scenario: Show Suggestions

**Given**: Word "helo" has red wavy line
**When**: User right-clicks on "helo"
**Then**: Program shows suggestions: "hello", "help", "held"

#### Scenario: Fix Spelling

**Given**: User sees suggestions for "helo"
**When**: User clicks "hello"
**Then**: "helo" changes to "hello" and red line goes away

### Requirement: Custom Dictionary

The program SHALL let users add words to custom dictionary.

#### Scenario: Add to Dictionary

**Given**: Word "AsciiDoc" has red wavy line
**When**: User right-clicks and selects "Add to Dictionary"
**Then**: "AsciiDoc" no longer shows as misspelled

#### Scenario: Save Custom Dictionary

**Given**: User added "AsciiDoc" to dictionary
**When**: User closes and reopens program
**Then**: "AsciiDoc" is still in dictionary

### Requirement: Language Selection

The program SHALL let users choose spell check language.

#### Scenario: Change Language

**Given**: Program is checking English spelling
**When**: User changes language to Spanish in settings
**Then**: Program checks Spanish spelling

## MODIFIED Requirements

### Requirement: Editor Context Menu

**Old**: The program SHALL show context menu with Cut, Copy, Paste.

**New**: The program SHALL show context menu with spelling suggestions first (if word is misspelled), then Cut, Copy, Paste.

#### Scenario: Context Menu With Suggestions

**Given**: User right-clicks on misspelled word
**When**: Context menu appears
**Then**: Menu shows:
- Spelling suggestions
- "Add to Dictionary"
- "Ignore"
- Separator line
- Cut, Copy, Paste

**Why changed**: Need to add spell check options to existing context menu

### Requirement: Settings Persistence

**Old**: The program SHALL remember window size, colors, and last folder.

**New**: The program SHALL remember window size, colors, last folder, and spell check language.

#### Scenario: Remember Spell Check Language

**Given**: User sets spell check language to French
**When**: User closes and reopens program
**Then**: Spell check language is still French

**Why changed**: Need to save spell check language preference

## REMOVED Requirements

None - No requirements are removed for this feature.

---

**Document Info**: Example spec changes | Reading level Grade 6.0 | OpenSpec format
