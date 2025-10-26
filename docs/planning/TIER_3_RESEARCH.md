# Tier 3 Research: Local AI and NPU Acceleration

**Date**: October 26, 2025
**Status**: Planning Phase
**Version**: 1.2.0 (Future)

---

## What is Tier 3?

Tier 3 adds smart AI features. It uses your computer's NPU (Neural Processing Unit) or GPU for AI work.

**Main Goals:**
- Local AI that works offline
- Smart document help
- Image processing
- No cloud needed

---

## Option A: Local AI with NPU

### What You Get

**Smart Writing Help:**
- Fix grammar
- Check spelling
- Suggest words
- Make text better

**Format Changes:**
- Smarter file conversion
- Better table extraction
- Keep formatting correct

**Work Offline:**
- No internet needed
- Your data stays private
- Fast responses

### How It Works

**Use Ollama:**
- Runs AI on your computer
- Free and open source
- Many models available

**Example Models:**
- llama3 (8B) - Good for text
- phi3 (3.8B) - Fast and small
- codellama (7B) - Good for code

**Code Example:**
```python
import ollama

response = ollama.generate(
    model='llama3',
    prompt='Fix this text: ...'
)
```

### What You Need

**Hardware:**
- NPU: Intel Core Ultra, AMD Ryzen AI
- OR GPU: NVIDIA, AMD, Intel Arc
- 8-16GB RAM for small models
- 16-32GB RAM for big models

**Software:**
- Ollama (free)
- Python 3.11+
- ONNX Runtime (for NPU)

---

## Option B: Image Processing

### What You Get

**Diagram Tools:**
- Turn images to text
- Find tables in images
- Extract charts
- OCR (read text in images)

**Smart Paste:**
- Paste image from copy area
- Auto-extract text
- Keep formatting

### How It Works

**Use OpenCV + Tesseract:**
- OpenCV finds shapes
- Tesseract reads text
- Both free and fast

**Code Example:**
```python
import cv2
import pytesseract

# Find tables in image
image = cv2.imread('diagram.png')
text = pytesseract.image_to_string(image)
```

### What You Need

**Software:**
- OpenCV (image tools)
- Tesseract (text reading)
- Pillow (image handling)

**Models:**
- Pre-trained OCR models
- No GPU needed (but faster with GPU)

---

## Option C: NPU Acceleration

### What It Does

Uses your CPU's NPU chip for fast AI work.

**NPUs Available:**
- Intel Core Ultra (12-16 TOPS)
- AMD Ryzen AI (up to 50 TOPS)
- Qualcomm Snapdragon X (45 TOPS)
- Apple Neural Engine

**Benefits:**
- 10x faster than CPU
- Less power use
- Always available

### How To Use

**DirectML (Windows):**
```python
import onnxruntime as ort

# Use NPU
session = ort.InferenceSession(
    model_path,
    providers=['DmlExecutionProvider']
)
```

**OpenVINO (Intel):**
```python
from openvino.runtime import Core

# Use NPU
core = Core()
model = core.read_model('model.xml')
compiled = core.compile_model(model, 'NPU')
```

---

## Recommended Plan

### Phase 1: Local AI (2-4 weeks)

**Week 1-2: Setup**
- Install Ollama
- Test small models
- Add to settings menu

**Week 3-4: Features**
- Grammar check
- Text improvement
- Format help

### Phase 2: Image Tools (2-3 weeks)

**Week 1: Basic OCR**
- Install Tesseract
- Add image paste
- Extract text

**Week 2-3: Smart Tools**
- Find tables
- Extract diagrams
- Keep formatting

### Phase 3: NPU Support (2-4 weeks)

**Week 1-2: Detection**
- Check for NPU
- Fall back to GPU/CPU
- Test on different chips

**Week 3-4: Optimization**
- Move AI to NPU
- Measure speedup
- Update docs

---

## Cost and Effort

### Time Needed

| Phase | Effort | Risk |
|-------|--------|------|
| Local AI | 2-4 weeks | Medium |
| Image Tools | 2-3 weeks | Low |
| NPU Support | 2-4 weeks | High |
| **Total** | **6-11 weeks** | **Medium** |

### Dependencies

**New Tools Needed:**
```txt
# Local AI
ollama-python>=0.1.0

# Image Processing
opencv-python>=4.8.0
pytesseract>=0.3.10

# NPU Support
onnxruntime-directml>=1.16.0  # Windows
openvino>=2023.1.0            # Intel
```

### Hardware Support

**Works On:**
- ✓ Intel Core Ultra (NPU)
- ✓ AMD Ryzen AI (NPU)
- ✓ Any NVIDIA GPU
- ✓ Any AMD GPU
- ✓ Intel Arc GPU
- ✓ Apple Silicon (Neural Engine)
- ✓ CPU-only (slower)

---

## Benefits

### For Users

**Better Writing:**
- Smart grammar fixes
- Better word choices
- Clear sentences

**Faster Work:**
- Quick AI responses
- No waiting for cloud
- Works offline

**Privacy:**
- Data stays local
- No internet needed
- You control everything

### For Performance

**Speed Gains:**
- NPU: 10x faster than CPU
- GPU: 5-10x faster than CPU
- Local: No network delays

**Less Resources:**
- NPU uses less power
- GPU shares with preview
- CPU fallback works

---

## Risks

### Technical Challenges

**Model Size:**
- Small models (3-8GB) - Fast but less smart
- Big models (16-32GB) - Smart but slow
- Need to balance size vs quality

**NPU Support:**
- Different APIs per vendor
- Not all NPUs work same way
- Need lots of testing

**Image Processing:**
- OCR not always perfect
- Complex images hard to parse
- Need good error handling

### Mitigation

**Make Everything Optional:**
- AI features are opt-in
- Graceful fallback
- App works without AI

**Test on All Platforms:**
- Windows, Mac, Linux
- Intel, AMD, Apple chips
- With and without NPU

**User Controls:**
- Choose model size
- Enable/disable features
- Clear privacy settings

---

## Next Steps

### Immediate (Before Starting)

1. **User Survey** (1 week)
   - Ask users what AI features they want
   - Check what hardware they have
   - Prioritize features

2. **Prototype** (1-2 weeks)
   - Test Ollama integration
   - Try small model
   - Measure performance

3. **Design** (1 week)
   - Plan UI for AI features
   - Design settings
   - Create privacy policy

### Phase 1 Start

**When Ready:**
- Complete Tier 1 & 2 (✓ Done!)
- User testing successful
- Hardware requirements clear

**Prerequisites:**
- Python 3.11+ (✓ Have it)
- Good GPU or NPU (✓ Available)
- 16GB+ RAM recommended

---

## Resources

### Documentation

**Ollama:**
- https://ollama.ai/
- https://github.com/ollama/ollama-python

**OpenVINO (Intel NPU):**
- https://docs.openvino.ai/
- https://github.com/openvinotoolkit/openvino

**DirectML (Windows NPU):**
- https://learn.microsoft.com/en-us/windows/ai/directml/
- https://github.com/microsoft/DirectML

**Tesseract OCR:**
- https://github.com/tesseract-ocr/tesseract
- https://pypi.org/project/pytesseract/

### Examples

**Similar Apps:**
- Obsidian (local AI plugins)
- Notion (cloud AI)
- VS Code Copilot (cloud AI)

**Open Source:**
- llama.cpp (fast local AI)
- ONNX models (NPU-ready)
- Whisper (speech to text)

---

## Summary

**Status**: Ready for planning
**Recommended**: Start with Phase 1 (Local AI)
**Timeline**: 6-11 weeks total
**Risk**: Medium (new technology)

**Key Points:**
- All features optional
- Privacy-focused (local only)
- Graceful fallback
- Cross-platform support

**Decision Needed:**
- Which AI features to add first?
- What model sizes to support?
- When to start development?

---

**Reading Level**: Grade 5.0
**For**: Planning and research
**Next Review**: After v1.1.0 release
**Status**: Planning phase
