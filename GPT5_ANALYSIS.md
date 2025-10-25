# GPT-5 Analysis and AsciiDoc Artisan Enhancement Plan

**Reading Level**: Grade 6.0 (Elementary/Middle School)
**Date**: October 2025
**Purpose**: Plan how GPT-5 can improve AsciiDoc Artisan

## What Is GPT-5?

GPT-5 is OpenAI's newest AI model. It came out in August 2025.

### Main Features

**Better at Everything**:
- Smarter than GPT-4
- Understands images and text together
- Can use tools and search the web
- Writes better code
- Follows instructions better

**Three Sizes**:
1. **GPT-5** - Full power ($1.25 input, $10 output per 1M tokens)
2. **GPT-5 Mini** - Medium power ($0.25 input, $2 output per 1M tokens)
3. **GPT-5 Nano** - Fast and cheap ($0.05 input, $0.40 output per 1M tokens)

**Big Memory**:
- Can remember up to 1 million tokens
- Can read very long documents
- Keeps track of whole conversation

## How GPT-5 Works Better

### Multimodal (Multiple Types at Once)

**What it means**:
GPT-5 can work with text, images, and files at the same time.

**Example**:
- Send it a screenshot of a document
- Ask it to turn the screenshot into AsciiDoc
- It understands both the picture and what you want

**Score**: 84.2% on multimodal tests (very good!)

### Structured Outputs

**What it means**:
GPT-5 can give answers in exact formats you want.

**Example**:
- You say "give me AsciiDoc with these sections"
- It gives you perfect AsciiDoc every time
- No need to fix the format

**Score**: 96.7% success on complex tasks

### Built-in Tools

**What GPT-5 includes**:
1. **Web Search** - Can look up current info
2. **File Search** - Can read and search files
3. **Image Generation** - Can make pictures
4. **Canvas** - Can edit documents together with you

### Better Reasoning

**What it means**:
GPT-5 thinks before it answers.

**How it helps**:
- More accurate conversions
- Better understanding of complex documents
- Fewer mistakes

## Current State of AsciiDoc Artisan AI

### What We Have Now

**File**: `src/asciidoc_artisan/claude/ai_client.py`

**What it does**:
- Uses Claude AI or OpenAI
- Helps convert documents
- Improves conversion quality

**Problems**:
1. Uses old API (GPT-4 or Claude)
2. No image understanding
3. No structured outputs
4. Basic prompts only
5. No web search
6. No reasoning mode

### Current Conversion Flow

```
1. User picks Word/PDF file
2. Pandoc converts to text
3. AI cleans up the text (optional)
4. Shows in editor
```

**Issues**:
- Loses formatting sometimes
- Can't read images in documents
- Doesn't understand tables well
- No way to verify quality

## GPT-5 Opportunities for AsciiDoc Artisan

### Opportunity 1: Smart Screenshot Conversion

**What**: Turn screenshots into AsciiDoc

**How it works**:
1. User takes screenshot of document
2. Pastes into AsciiDoc Artisan
3. GPT-5 reads the image
4. Converts to perfect AsciiDoc

**Benefits**:
- Works with any document
- No need for original file
- Understands layout and format
- Preserves tables and lists

**API to use**: GPT-5 with image input

### Opportunity 2: Perfect Structured Conversion

**What**: Get exact AsciiDoc format every time

**How it works**:
1. Define AsciiDoc schema (JSON format)
2. Send document to GPT-5
3. GPT-5 returns perfect AsciiDoc structure
4. No cleanup needed

**Benefits**:
- Consistent output
- No format errors
- Faster conversion
- Better quality

**API to use**: Structured Outputs feature

### Opportunity 3: Multi-Page Document Intelligence

**What**: Handle very long documents smartly

**How it works**:
1. Upload 100-page Word doc
2. GPT-5 reads entire thing (1M token context)
3. Maintains structure across all pages
4. Creates proper document outline

**Benefits**:
- Handle huge documents
- Keep context throughout
- Better chapter organization
- No page breaks issues

**API to use**: GPT-5 with large context window

### Opportunity 4: Real-Time Document Help

**What**: AI assistant while you write

**How it works**:
1. User writes AsciiDoc
2. GPT-5 watches for issues
3. Suggests improvements
4. Fixes formatting live

**Benefits**:
- Learn AsciiDoc faster
- Fewer mistakes
- Better writing
- Real-time help

**API to use**: GPT-5 with streaming

### Opportunity 5: Web-Enhanced Conversions

**What**: Add current information to documents

**How it works**:
1. Convert old document
2. GPT-5 finds outdated info
3. Uses web search to update
4. Adds current facts

**Benefits**:
- Documents stay current
- Auto-update statistics
- Add recent references
- Verify facts

**API to use**: GPT-5 with web search tool

### Opportunity 6: Smart Table Extraction

**What**: Perfect table conversion from any format

**How it works**:
1. Document has complex tables
2. GPT-5 understands table structure
3. Converts to AsciiDoc table format
4. Preserves all data and formatting

**Benefits**:
- No broken tables
- Keeps data accurate
- Proper alignment
- Works with merged cells

**API to use**: GPT-5 multimodal + structured outputs

### Opportunity 7: Format Verification

**What**: Check if AsciiDoc is correct

**How it works**:
1. User finishes document
2. Click "Verify Format"
3. GPT-5 checks for errors
4. Suggests fixes

**Benefits**:
- Catch errors early
- Learn correct format
- Professional output
- Less debugging

**API to use**: GPT-5 with reasoning

### Opportunity 8: PDF with Images Conversion

**What**: Convert PDFs that have pictures

**How it works**:
1. User opens PDF with images
2. GPT-5 reads text and images
3. Describes images in AsciiDoc
4. Places images correctly

**Benefits**:
- Handle complex PDFs
- Don't lose visual info
- Better documentation
- Complete conversion

**API to use**: GPT-5 multimodal

## Proposed Implementation Plan

### Phase 1: Basic GPT-5 Integration (Week 1-2)

**Goal**: Replace current AI with GPT-5 API

**Tasks**:
1. Install OpenAI SDK (latest version)
2. Update `ai_client.py` to use GPT-5 API
3. Add API key configuration
4. Test basic text conversion
5. Compare quality to current system

**Success**: GPT-5 API works for basic conversions

**Cost**: ~$0.50 per document (GPT-5 Mini)

### Phase 2: Structured Output Conversion (Week 3-4)

**Goal**: Use structured outputs for perfect AsciiDoc

**Tasks**:
1. Define AsciiDoc JSON schema
2. Create schema validator
3. Update conversion to use structured outputs
4. Add error handling
5. Test with various documents

**Success**: 100% valid AsciiDoc format

**Benefits**:
- No post-processing needed
- Consistent output
- Faster conversion

### Phase 3: Image/Screenshot Support (Week 5-6)

**Goal**: Convert images to AsciiDoc

**Tasks**:
1. Add screenshot paste feature
2. Send images to GPT-5 vision API
3. Handle image + text documents
4. Add image description in AsciiDoc
5. Test with real documents

**Success**: Can convert screenshots and image-heavy PDFs

**New Feature**: Import from clipboard images

### Phase 4: Long Document Handling (Week 7-8)

**Goal**: Handle documents over 100 pages

**Tasks**:
1. Implement chunking for large docs
2. Use GPT-5 large context (1M tokens)
3. Maintain document structure
4. Add progress indicator
5. Test with technical manuals

**Success**: Handle 500+ page documents

**Benefits**:
- No page limit
- Better structure preservation

### Phase 5: Real-Time Writing Assistant (Week 9-10)

**Goal**: AI helps while you write

**Tasks**:
1. Add "AI Assistant" panel
2. Implement streaming responses
3. Add suggestion system
4. Create keyboard shortcuts
5. Test with users

**Success**: Live suggestions as user types

**New Feature**: Smart autocomplete

### Phase 6: Web Search Integration (Week 11-12)

**Goal**: Update documents with current info

**Tasks**:
1. Enable GPT-5 web search tool
2. Add "Update Facts" button
3. Show sources for updates
4. Let user approve changes
5. Test with news documents

**Success**: Can update old documents with current data

**New Feature**: Fact checking

## Detailed Feature Specifications

### Feature 1: Screenshot to AsciiDoc

**User Flow**:
1. User takes screenshot (any format)
2. Pastes into AsciiDoc Artisan
3. Program shows preview
4. User clicks "Convert to AsciiDoc"
5. GPT-5 processes image
6. AsciiDoc appears in editor

**Technical Details**:
```python
# Pseudocode
async def convert_screenshot(image_data):
    response = await openai.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_data
                    },
                    {
                        "type": "text",
                        "text": "Convert this image to AsciiDoc format. Preserve all structure, headings, lists, and tables."
                    }
                ]
            }
        ],
        response_format={"type": "json_schema", "schema": asciidoc_schema}
    )
    return response.choices[0].message.content
```

**Testing**:
- Screenshot of Word doc
- Screenshot of PDF
- Screenshot of web page
- Photo of printed paper
- Complex tables

**Expected Quality**: 95%+ accuracy

### Feature 2: Structured AsciiDoc Output

**AsciiDoc Schema** (simplified):
```json
{
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "level": {"type": "integer"},
                    "content": {"type": "string"},
                    "subsections": {"type": "array"}
                }
            }
        },
        "tables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "headers": {"type": "array"},
                    "rows": {"type": "array"}
                }
            }
        }
    }
}
```

**Benefits**:
- Guaranteed valid format
- Easy to render
- Predictable structure
- No parsing errors

### Feature 3: AI Writing Assistant

**UI Design**:
```
+----------------------------------+
|  Editor          |  AI Assistant |
|                  |  ------------ |
|  = My Document   |  💡 Tips:     |
|                  |               |
|  Text here...    |  - Use `code` |
|                  |    for terms  |
|                  |               |
|                  |  ⚠ Warnings:  |
|                  |  - Missing    |
|                  |    title      |
+----------------------------------+
```

**Assistant Features**:
1. **Real-time tips** - Suggest AsciiDoc syntax
2. **Error detection** - Find format problems
3. **Auto-complete** - Finish your sentences
4. **Smart snippets** - Insert common patterns

**API Usage**:
- Streaming for real-time
- Low verbosity for quick tips
- GPT-5 Nano for speed/cost

### Feature 4: Web-Enhanced Conversion

**Example Use Case**:
```
Old document from 2020:
"Python 3.8 is the latest version"

GPT-5 with web search:
"Python 3.13 is the latest version (as of October 2025)"
```

**User Control**:
- Show what changed (diff view)
- Let user accept/reject
- Show sources
- Keep original if user wants

**Settings**:
```
☑ Update version numbers
☑ Update statistics
☐ Update examples
☐ Add recent references
```

## Cost Analysis

### Current System
- Pandoc: Free
- Optional AI: ~$0.10 per document (GPT-4)

### With GPT-5 (Estimated)

**Per Document Conversion**:
- Small doc (1-5 pages): $0.02 (GPT-5 Nano)
- Medium doc (5-50 pages): $0.15 (GPT-5 Mini)
- Large doc (50-500 pages): $1.50 (GPT-5)

**Real-Time Assistant** (per hour of writing):
- Continuous tips: $0.05/hour (GPT-5 Nano)
- On-demand help: $0.01/request (GPT-5 Nano)

**Total Monthly Cost** (heavy user, 100 docs):
- Current: $10/month
- With GPT-5: $15-25/month
- **Increase**: $5-15/month

**Ways to Save**:
1. Use GPT-5 Nano by default
2. Use GPT-5 Mini only for complex docs
3. Use GPT-5 full only for huge docs
4. Cache common prompts (70% savings)
5. Batch processing for multiple files

## Updated Specifications Needed

### New Requirements to Add

#### Requirement: Screenshot Conversion

The program SHALL convert screenshots to AsciiDoc.

##### Scenario: Paste Screenshot

**Given**: User copies screenshot to clipboard
**When**: User presses Ctrl+Shift+V
**Then**: Program asks "Convert this image to AsciiDoc?"

##### Scenario: Convert Screenshot

**Given**: User confirms screenshot conversion
**When**: GPT-5 processes image
**Then**: AsciiDoc text appears in editor

#### Requirement: Structured Output

The program SHALL use GPT-5 structured outputs.

##### Scenario: Guaranteed Format

**Given**: User converts Word document
**When**: Conversion completes
**Then**: Output is valid AsciiDoc with no format errors

#### Requirement: AI Writing Assistant

The program SHALL provide real-time writing help.

##### Scenario: Show Tips

**Given**: User types in editor
**When**: User makes syntax error
**Then**: AI panel shows how to fix it

##### Scenario: Auto-complete

**Given**: User starts typing heading
**When**: User presses Tab
**Then**: AI completes the heading format

#### Requirement: Large Document Support

The program SHALL handle documents over 100 pages.

##### Scenario: Convert Long Document

**Given**: User opens 500-page PDF
**When**: Conversion runs
**Then**: All pages convert with structure preserved

#### Requirement: Web-Enhanced Updates

The program SHALL update outdated information.

##### Scenario: Update Facts

**Given**: Document has old statistics
**When**: User clicks "Update Facts"
**Then**: AI finds current numbers and suggests changes

#### Requirement: Cost Control

The program SHALL let users control AI costs.

##### Scenario: Choose Model

**Given**: User is in settings
**When**: User picks AI model quality
**Then**: Program uses selected model (Nano/Mini/Full)

##### Scenario: Show Cost

**Given**: User converts document
**When**: Conversion completes
**Then**: Status bar shows estimated cost

### Modified Requirements

#### Requirement: Document Conversion (MODIFIED)

**Old**: The program SHALL convert Word and PDF to AsciiDoc using Pandoc.

**New**: The program SHALL convert Word, PDF, and images to AsciiDoc using Pandoc and GPT-5.

**Why**: Added image/screenshot conversion capability

#### Requirement: AI Integration (MODIFIED)

**Old**: The program MAY use AI to improve conversions (optional).

**New**: The program SHALL use GPT-5 for conversions and writing assistance.

**Why**: AI is now core feature with structured outputs

## Risk Assessment

### Technical Risks

**Risk 1: API Costs Too High**
- **Impact**: Users can't afford to use AI features
- **Probability**: Medium
- **Mitigation**:
  - Use GPT-5 Nano by default
  - Add cost caps in settings
  - Show cost before conversion
  - Cache common requests

**Risk 2: API Downtime**
- **Impact**: Conversions fail when OpenAI down
- **Probability**: Low
- **Mitigation**:
  - Keep Pandoc as fallback
  - Queue failed requests
  - Show clear error messages
  - Retry with exponential backoff

**Risk 3: Slow Performance**
- **Impact**: Conversions take too long
- **Probability**: Medium
- **Mitigation**:
  - Show progress bar
  - Use streaming for feedback
  - Process in background
  - Let user cancel

**Risk 4: Privacy Concerns**
- **Impact**: Users worried about sending docs to cloud
- **Probability**: Medium
- **Mitigation**:
  - Make AI optional
  - Show privacy policy clearly
  - Add local-only mode
  - Let users use own API key

### User Experience Risks

**Risk 1: Too Complex**
- **Impact**: Users confused by AI options
- **Probability**: Low
- **Mitigation**:
  - Smart defaults
  - Simple UI
  - Good documentation
  - Tutorial on first use

**Risk 2: Wrong Conversions**
- **Impact**: AI makes mistakes in output
- **Probability**: Low
- **Mitigation**:
  - Always show preview
  - Let user edit before saving
  - Provide "undo" button
  - Keep original file

## Success Metrics

### Quality Metrics

**Conversion Accuracy**:
- Goal: 95%+ correct format
- Measure: User satisfaction survey
- Test: 100 sample documents

**Speed**:
- Goal: < 10 seconds for normal document
- Measure: Average processing time
- Test: Documents 1-50 pages

**Cost**:
- Goal: < $0.20 per document average
- Measure: API usage tracking
- Test: Monthly cost reports

### User Metrics

**Adoption**:
- Goal: 80% of users try AI features
- Measure: Feature usage analytics
- Test: Track first 1000 users

**Satisfaction**:
- Goal: 4.5/5 stars average
- Measure: In-app feedback
- Test: Survey after 10 conversions

**Retention**:
- Goal: 60% use AI monthly
- Measure: Monthly active users
- Test: 6-month tracking

## Implementation Timeline

### Month 1: Foundation
- Week 1: GPT-5 API integration
- Week 2: Structured outputs
- Week 3: Testing and refinement
- Week 4: Documentation

### Month 2: Core Features
- Week 5: Screenshot conversion
- Week 6: Image handling
- Week 7: Large document support
- Week 8: Testing

### Month 3: Advanced Features
- Week 9: AI writing assistant
- Week 10: Real-time suggestions
- Week 11: Web search integration
- Week 12: Final testing

### Month 4: Polish and Launch
- Week 13: UI improvements
- Week 14: Performance optimization
- Week 15: Beta testing with users
- Week 16: Public launch

## Conclusion

GPT-5 offers major improvements for AsciiDoc Artisan:

**Main Benefits**:
1. **Better conversions** - 95%+ accuracy
2. **New capabilities** - Screenshots, images, huge docs
3. **Real-time help** - AI assistant while writing
4. **Structured output** - Perfect format every time
5. **Current info** - Web search for updates

**Reasonable Costs**:
- $0.02-$1.50 per document
- ~$15-25/month for heavy users
- Much better than hiring someone

**Low Risk**:
- Keep Pandoc as fallback
- Make AI optional
- Let users control costs
- Good error handling

**Bottom Line**: GPT-5 makes AsciiDoc Artisan much better without making it too expensive or complex.

---

**Document Info**: GPT-5 analysis and recommendations | Reading level Grade 6.0 | October 2025
