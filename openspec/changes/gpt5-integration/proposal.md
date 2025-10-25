# Proposal: GPT-5 Integration

**Status**: ✅ APPROVED - High Priority (v1.2.0/1.3.0)
**Author**: AsciiDoc Artisan Team
**Date**: October 2025
**Decision Date**: October 25, 2025
**Reading Level**: Grade 6.0
**Based On**: GPT-5 API release (August 2025)

## Problem

Current AI integration has limits:
1. Uses old GPT-4 or Claude API
2. Can't read images or screenshots
3. No structured output guarantee
4. Limited to text-only documents
5. Can't handle very long documents
6. No real-time writing help

Users need:
- Convert screenshots to AsciiDoc
- Handle complex PDFs with images
- Get perfect format every time
- Work with huge documents (500+ pages)
- Get help while writing

## Solution

Upgrade to GPT-5 API with these new features:

1. **Multimodal Input** - Handle text and images together
2. **Structured Outputs** - Get perfect AsciiDoc format
3. **Large Context** - Process up to 1M tokens (huge docs)
4. **Built-in Tools** - Web search, file search
5. **Three Models** - Nano (fast), Mini (balanced), Full (powerful)
6. **Real-Time Streaming** - Live suggestions while typing

## Examples

### Example 1: Screenshot Conversion

**Before**:
```
User has screenshot of document
Can't convert it - need original file
Must retype or use OCR
OCR often makes mistakes
```

**After**:
```
User pastes screenshot (Ctrl+Shift+V)
GPT-5 reads image and understands structure
Converts to perfect AsciiDoc in 5 seconds
Preserves headings, lists, tables
```

### Example 2: Perfect Format

**Before**:
```
Convert Word doc → sometimes broken tables
Manual cleanup needed
Headings might be wrong level
Lists might be malformed
```

**After**:
```
Convert Word doc → always perfect AsciiDoc
GPT-5 uses structured output schema
No cleanup needed
100% valid format guaranteed
```

### Example 3: Huge Documents

**Before**:
```
500-page technical manual
Pandoc loses context after each page
Structure breaks down
Chapters get mixed up
```

**After**:
```
500-page technical manual
GPT-5 reads entire document (1M tokens)
Maintains structure throughout
Perfect chapter organization
Cross-references preserved
```

### Example 4: Writing Assistant

**Before**:
```
User types AsciiDoc
No help available
Must check syntax manually
Learn by trial and error
```

**After**:
```
User types AsciiDoc
AI panel shows tips in real-time
"Use `backticks` for inline code"
Auto-complete common patterns
Fix errors as you type
```

## Benefits

1. **Better Quality** - 95%+ conversion accuracy (up from 80%)
2. **New Capabilities** - Screenshots, images, huge docs
3. **Faster Workflow** - No manual cleanup needed
4. **Learn Faster** - AI teaches AsciiDoc as you write
5. **Handle Anything** - Any document type, any size
6. **Save Time** - 50% faster document conversion
7. **More Professional** - Perfect format every time

## Risks

1. **API Costs** - Could be expensive for heavy users
   - **How we handle it**:
     - Use GPT-5 Nano by default ($0.05/1M tokens)
     - Let users choose model size
     - Show estimated cost before conversion
     - Add cost caps in settings
     - Cache common requests (70% savings)

2. **Privacy Concerns** - Documents sent to OpenAI servers
   - **How we handle it**:
     - Make AI features optional
     - Clear privacy notice
     - Let users use own API key
     - Keep Pandoc as local-only fallback
     - Don't store documents on cloud

3. **API Downtime** - Features break when OpenAI down
   - **How we handle it**:
     - Automatic fallback to Pandoc
     - Queue failed requests for retry
     - Clear error messages
     - Show status in real-time

4. **Complexity** - Too many AI options confuses users
   - **How we handle it**:
     - Smart defaults (GPT-5 Mini for most docs)
     - Simple UI with "Convert" button
     - Advanced settings hidden
     - Good documentation and tutorial

5. **Wrong Output** - AI makes mistakes sometimes
   - **How we handle it**:
     - Always show preview before saving
     - Let user edit in preview
     - Provide "Undo" button
     - Keep original file safe
     - Add "Verify Format" feature

## Questions

1. **Which GPT-5 model should be default?**
   - Option A: GPT-5 Nano (fastest, cheapest)
   - Option B: GPT-5 Mini (balanced)
   - Option C: GPT-5 Full (best quality)
   - **Recommendation**: GPT-5 Mini by default

2. **Should AI features be always-on or opt-in?**
   - Option A: On by default (better experience)
   - Option B: Off by default (user choice)
   - **Recommendation**: On by default with easy disable

3. **How to handle API keys?**
   - Option A: Users bring own key (more control)
   - Option B: We provide shared key (easier)
   - Option C: Both options available
   - **Recommendation**: Option C - both available

4. **Should we keep Claude support?**
   - Option A: Remove Claude, GPT-5 only
   - Option B: Support both GPT-5 and Claude
   - **Recommendation**: Support both, GPT-5 default

5. **Real-time assistant - always on or on-demand?**
   - Option A: Always watching and suggesting
   - Option B: Only when user asks (Ctrl+Space)
   - **Recommendation**: Option B to avoid distraction

## Cost Analysis

### Per Document (Estimated)

**Small Document** (1-5 pages, ~2K tokens):
- GPT-5 Nano: $0.001 (~0.1 cent)
- GPT-5 Mini: $0.009 (~1 cent)
- GPT-5 Full: $0.045 (~5 cents)

**Medium Document** (10-50 pages, ~20K tokens):
- GPT-5 Nano: $0.009 (~1 cent)
- GPT-5 Mini: $0.09 (~9 cents)
- GPT-5 Full: $0.45 (~45 cents)

**Large Document** (100+ pages, ~100K tokens):
- GPT-5 Nano: $0.045 (~5 cents)
- GPT-5 Mini: $0.45 (~45 cents)
- GPT-5 Full: $2.25 (~$2.25)

### Monthly Cost (Heavy User, 100 docs/month)

**Mix of sizes** (70 small, 25 medium, 5 large):
- Using Nano: ~$1.50/month
- Using Mini: ~$15/month
- Using Full: ~$75/month

**Recommended Strategy**:
- Nano for quick conversions
- Mini for normal documents (default)
- Full for complex/important documents
- **Average user**: ~$10-20/month

## Implementation Phases

### Phase 1: Basic Integration (2 weeks)
- Install OpenAI Python SDK
- Update `ai_client.py` for GPT-5
- Add model selection
- Basic text conversion
- Cost tracking

### Phase 2: Structured Outputs (2 weeks)
- Define AsciiDoc JSON schema
- Implement structured output requests
- Validate output format
- Error handling
- Testing

### Phase 3: Multimodal Support (2 weeks)
- Screenshot paste feature
- Image handling in PDFs
- Vision API integration
- Preview before conversion
- Testing

### Phase 4: Large Documents (2 weeks)
- Large context support (1M tokens)
- Progress indicators
- Chunking strategy for huge files
- Memory management
- Testing

### Phase 5: Writing Assistant (2 weeks)
- AI assistant panel UI
- Real-time suggestions
- Streaming implementation
- Keyboard shortcuts
- Testing

### Phase 6: Polish (2 weeks)
- Cost optimization
- Error handling
- Documentation
- User testing
- Launch

**Total Time**: 12 weeks (3 months)

## Success Criteria

**Quality**:
- ✅ 95%+ conversion accuracy
- ✅ 100% valid AsciiDoc format
- ✅ < 5% error rate

**Performance**:
- ✅ < 10 seconds for normal document
- ✅ Real-time suggestions < 1 second
- ✅ No freezing during conversion

**Cost**:
- ✅ Average < $0.20 per document
- ✅ Monthly cost < $25 for heavy users
- ✅ Budget controls working

**User Satisfaction**:
- ✅ 4.5/5 star rating
- ✅ 80% feature adoption
- ✅ 60% monthly retention

---

**Document Info**: GPT-5 integration proposal | Reading level Grade 6.0 | October 2025
