# Specification Changes for GPT-5 Integration

**Reading Level**: Grade 6.0
**Status**: Draft
**Domains**: Conversion, Editor, User Interface

## Overview

This shows what requirements change to add GPT-5 AI features to AsciiDoc Artisan.

## ADDED Requirements

### Requirement: Screenshot Conversion

The program SHALL convert screenshots to AsciiDoc using GPT-5 vision.

#### Scenario: Paste Screenshot

**Given**: User copies screenshot to clipboard
**When**: User presses Ctrl+Shift+V
**Then**: Dialog asks "Convert this image to AsciiDoc?"

#### Scenario: Convert Screenshot

**Given**: User confirms screenshot conversion
**When**: GPT-5 processes the image
**Then**: AsciiDoc text appears in editor within 10 seconds

#### Scenario: Handle Screenshot Error

**Given**: Screenshot is too blurry to read
**When**: Conversion fails
**Then**: Program shows error "Image not clear enough" and keeps screenshot in clipboard

### Requirement: Structured Output Conversion

The program SHALL use GPT-5 structured outputs for guaranteed valid AsciiDoc.

#### Scenario: Perfect Format

**Given**: User converts Word document
**When**: Conversion completes
**Then**: Output is 100% valid AsciiDoc with no format errors

#### Scenario: Verify Structure

**Given**: Conversion produces output
**When**: Program validates the output
**Then**: All headings, lists, and tables are correctly formatted

### Requirement: Large Document Support

The program SHALL handle documents larger than 100 pages using GPT-5.

#### Scenario: Convert 500-Page Document

**Given**: User opens 500-page PDF
**When**: Conversion runs
**Then**: All 500 pages convert with structure preserved

#### Scenario: Show Progress

**Given**: Large document is converting
**When**: User looks at status bar
**Then**: Status bar shows "Converting page 150/500 (30%)"

#### Scenario: Handle Memory

**Given**: Converting very large document
**When**: Process uses too much memory
**Then**: Program uses chunking strategy automatically

### Requirement: AI Writing Assistant

The program SHALL provide real-time AI writing help.

#### Scenario: Show Syntax Tips

**Given**: User types invalid AsciiDoc syntax
**When**: AI detects the error
**Then**: AI panel shows "Did you mean: `code` instead of 'code'?"

#### Scenario: Auto-complete

**Given**: User types "== " (heading start)
**When**: User presses Ctrl+Space
**Then**: AI suggests common heading patterns

#### Scenario: Toggle Assistant

**Given**: AI assistant is showing
**When**: User clicks "Hide AI" button
**Then**: Assistant panel closes and doesn't show tips

### Requirement: Model Selection

The program SHALL let users choose GPT-5 model size.

#### Scenario: Choose Model

**Given**: User is in AI settings
**When**: User selects "GPT-5 Mini" from dropdown
**Then**: All conversions use GPT-5 Mini

#### Scenario: Auto Model Selection

**Given**: User converts 3-page document
**When**: Auto-select is enabled
**Then**: Program uses GPT-5 Nano (cheapest)

#### Scenario: Override Model

**Given**: User is converting important document
**When**: User checks "Use best quality"
**Then**: Program uses GPT-5 Full regardless of size

### Requirement: Cost Tracking

The program SHALL track and display AI API costs.

#### Scenario: Show Cost After Conversion

**Given**: User converts document
**When**: Conversion completes
**Then**: Status bar shows "Cost: $0.09" for 3 seconds

#### Scenario: Monthly Cost Summary

**Given**: User clicks AI > Usage Stats
**When**: Dialog opens
**Then**: Shows "This month: $12.50 (85 documents)"

#### Scenario: Cost Warning

**Given**: User is about to convert huge document
**When**: Estimated cost is over $5
**Then**: Dialog warns "This will cost about $5.50. Continue?"

### Requirement: API Key Management

The program SHALL support user-provided OpenAI API keys.

#### Scenario: Enter API Key

**Given**: User has OpenAI API key
**When**: User enters key in settings
**Then**: Program uses user's key instead of shared key

#### Scenario: Test API Key

**Given**: User entered API key
**When**: User clicks "Test Connection"
**Then**: Program verifies key works and shows "Connected ✓"

#### Scenario: Key Error

**Given**: User enters invalid API key
**When**: Conversion tries to run
**Then**: Error shows "API key invalid. Check settings."

### Requirement: Privacy Mode

The program SHALL offer local-only conversion mode.

#### Scenario: Enable Privacy Mode

**Given**: User is in settings
**When**: User checks "Privacy Mode (no cloud AI)"
**Then**: All conversions use Pandoc only

#### Scenario: Privacy Warning

**Given**: Privacy mode is off
**When**: User converts sensitive document
**Then**: First time shows "This will send to OpenAI. Enable Privacy Mode in settings to avoid this."

### Requirement: Fallback to Pandoc

The program SHALL automatically fall back to Pandoc when GPT-5 fails.

#### Scenario: API Down

**Given**: OpenAI API is unreachable
**When**: User tries to convert document
**Then**: Program shows "AI unavailable, using Pandoc" and converts anyway

#### Scenario: Retry Failed Request

**Given**: API request failed with timeout
**When**: Program waits 5 seconds
**Then**: Program retries up to 3 times before giving up

## MODIFIED Requirements

### Requirement: Import Word Files (MODIFIED)

**Old**: The program SHALL convert Word files to AsciiDoc using Pandoc.

**New**: The program SHALL convert Word files to AsciiDoc using GPT-5 with structured outputs, falling back to Pandoc if GPT-5 unavailable.

#### Scenario: GPT-5 Conversion

**Given**: User opens .docx file
**When**: GPT-5 is available
**Then**: GPT-5 converts with perfect structure

**Why changed**: GPT-5 provides better quality and guaranteed format

### Requirement: Import PDF Files (MODIFIED)

**Old**: The program SHALL extract text from PDF files using pdfplumber.

**New**: The program SHALL convert PDF files to AsciiDoc using GPT-5 vision API to handle both text and images.

#### Scenario: PDF With Images

**Given**: PDF has text and images
**When**: User opens the file
**Then**: GPT-5 converts text and describes images in AsciiDoc

**Why changed**: Can now handle images in PDFs, not just text

### Requirement: Clipboard Import (MODIFIED)

**Old**: The program SHALL import HTML from clipboard using Pandoc.

**New**: The program SHALL import HTML or images from clipboard using GPT-5 vision for images, Pandoc for HTML.

#### Scenario: Paste Image

**Given**: User copied screenshot
**When**: User presses Ctrl+Shift+V
**Then**: GPT-5 converts image to AsciiDoc

**Why changed**: Added image paste capability

### Requirement: Settings Persistence (MODIFIED)

**Old**: The program SHALL remember window size, colors, last folder, and spell check language.

**New**: The program SHALL remember window size, colors, last folder, spell check language, GPT-5 model choice, and API key.

#### Scenario: Remember AI Settings

**Given**: User set GPT-5 model to "Mini" and entered API key
**When**: User closes and reopens program
**Then**: GPT-5 Mini is selected and API key is saved (encrypted)

**Why changed**: Need to save AI preferences

### Requirement: File Operations (MODIFIED)

**Old**: The program SHALL provide New, Open, Save, Save As operations.

**New**: The program SHALL provide New, Open, Save, Save As operations, plus Paste Image (Ctrl+Shift+V) and Verify Format (Ctrl+Shift+F).

#### Scenario: Verify Format

**Given**: User finished writing document
**When**: User presses Ctrl+Shift+F
**Then**: GPT-5 checks format and shows "✓ Format is correct" or lists errors

**Why changed**: Added AI-powered format verification

## REMOVED Requirements

None - No existing requirements are removed. All new features are additions or improvements.

---

**Document Info**: GPT-5 spec changes | Reading level Grade 6.0 | October 2025
