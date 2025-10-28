# Program Rules

**Reading Level**: Grade 5.0
**Version**: 1.5.0
**Last Updated**: October 28, 2025

## What This Is

This tells you what the program must do.

Each rule says what MUST happen.

## What The Program Does

This program helps you write papers.

It:

- Shows your work as you type
- Opens Word, PDF, Markdown files (10-50x faster with GPU)
- Saves to Word, PDF, Markdown
- Uses Git to save versions
- Works on all computers
- Uses GPU for speed (10-50x faster preview with hardware acceleration)
- Uses NPU for AI tasks when available
- Shows document version in status bar
- Starts fast (1.05 seconds in v1.5.0)
- Can cancel long tasks
- Uses less code (easier to fix)

Think of it like Word, but for AsciiDoc.

## Who Uses It

- People who write manuals
- People who write code
- Teachers and students
- Writers
- Teams

---

## Core Rules

### Rule: Works On All Computers

The program MUST work on Windows, Mac, and Linux.

**Test**: Run on each type. It must start with no errors.

### Rule: Needs Python 3.11

The program MUST need Python 3.11 or newer.

**Test**: Try with Python 3.10. It must show an error.

**Test**: Use Python 3.11. It must work.

### Rule: Free To Use

The program MUST be free. MIT License.

**Test**: Check LICENSE file. It must say MIT.

---

## Install Rules

### Rule: Easy Install

The program MUST have install scripts.

**Test**: Run the script. It must install all parts.

### Rule: Check What You Have

The install script MUST check for Python, Pandoc, Git.

**Test**: Run without Pandoc. Script must tell you.

### Rule: Make Safe Space

The install script MUST offer to make a safe space for tools.

**Test**: Say yes. Tools go in that space.

**Test**: Say no. Tools go on your computer.

### Rule: Test After Install

The install script MUST test everything.

**Test**: After install, script must check all parts work.

---

## Edit Rules

### Rule: Type Text

The program MUST let you type.

**Test**: Type "Hello". It must show in the editor.

### Rule: Copy And Paste

The program MUST let you copy, cut, paste.

**Test**: Press Ctrl+C. Text must copy.

**Test**: Press Ctrl+V. Text must paste.

### Rule: Undo And Redo

The program MUST let you undo.

**Test**: Make a change. Press Ctrl+Z. Change must go away.

**Test**: Press Ctrl+Y. Change must come back.

### Rule: Find Words

The program MUST let you find words.

**Test**: Search for "hello". Program must find it.

### Rule: Go To Line

The program MUST let you jump to a line.

**Test**: Go to line 50. Cursor must move there.

### Rule: Show Line Numbers

The program MUST show line numbers.

**Test**: Open program. Line numbers must show on left.

---

## Preview Rules

### Rule: Show Preview

The program MUST show HTML preview as true "what you see is what you get" (WYSIWYG).

**Test**: Type text. Wait 1 second. Preview must update.

### Rule: Move Together

The editor and preview MUST move together.

**Test**: Scroll editor. Preview must scroll too.

**Test**: Scroll preview. Editor must scroll too.

### Rule: Wait To Update

The preview MUST wait before it updates.

**Test**: Type fast. Preview must wait until you stop.

### Rule: Show Plain Text On Error

If HTML fails, program MUST show plain text.

**Test**: Break the HTML. Program must show text, not crash.

### Rule: Use GPU When Available (v1.1+, Enhanced v1.4)

The program MUST try to use GPU for fast rendering.

**Test**: Start app. Check logs for "GPU detected" and "Hardware acceleration available".

**Test**: No GPU? App must work with CPU.

**Test**: With GPU: Preview updates 10-50x faster.

### Rule: Hardware Acceleration (NEW v1.4)

The program MUST use GPU hardware acceleration automatically.

**Test**: Start app with NVIDIA GPU. Logs must show "QWebEngineView with acceleration".

**Test**: Preview must use GPU rasterization (check GPU usage with nvidia-smi).

**Test**: Scrolling must be smooth at 60fps+.

---

## Git Rules

### Rule: Commit Changes

The program MUST let you commit.

**Test**: In Git folder, commit must work.

**Test**: Not in Git folder, must show error.

### Rule: Push Changes

The program MUST let you push.

**Test**: Push must send commits to server.

**Test**: No server set up, must show error.

### Rule: Pull Changes

The program MUST let you pull.

**Test**: Pull must get new commits.

**Test**: If clash, must show message.

### Rule: Show Git Status

The program MUST show Git status.

**Test**: In Git folder, status bar shows folder name.

**Test**: Not in Git folder, shows "Not in Git".

---

## File Change Rules

### Rule: Open Word Files

The program MUST open .docx files.

**Test**: Open Word file. It must change to AsciiDoc.

**Test**: Bad Word file must show error.

### Rule: Open PDF Files

The program MUST open .pdf files.

**Test**: Open PDF. It must get text out.

### Rule: Open Markdown Files

The program MUST open .md files.

**Test**: Open Markdown. It must change to AsciiDoc.

### Rule: Open HTML Files

The program MUST open .html files.

**Test**: Open HTML. It must change to AsciiDoc.

### Rule: Save To HTML

The program MUST save to .html.

**Test**: Click Save As HTML. It must make HTML file.

### Rule: Save To PDF

The program MUST save to .pdf.

**Test**: Click Save As PDF. It must make PDF file.

### Rule: Save To Word

The program MUST save to .docx.

**Test**: Click Save As Word. It must make Word file.

### Rule: Save To Markdown

The program MUST save to .md.

**Test**: Click Save As Markdown. It must make MD file.

### Rule: AI Conversion Option

The program MUST let you choose AI or Pandoc for conversions.

**Test**: Go to Tools → AI Status → Settings. Toggle Ollama on/off.

**Test**: With Ollama on: Status bar shows "AI: model-name".

**Test**: With Ollama off: Status bar shows "Conversion: Pandoc".

### Rule: AI Model Selection

The program MUST let you pick which AI model to use.

**Test**: Open AI Status → Settings. See list of installed models.

**Test**: Pick a model. Status bar must update right away.

### Rule: AI Conversion Works

When Ollama is on, the program MUST use AI for conversions.

**Test**: Turn on Ollama. Export to Markdown. Check logs show "Ollama AI conversion".

**Test**: If AI fails, must fall back to Pandoc.

### Rule: Pandoc Fallback

The program MUST use Pandoc if AI is off or fails.

**Test**: Turn off Ollama. Export must still work with Pandoc.

**Test**: Break Ollama service. Export must fall back to Pandoc.

### Rule: Paste From Copy

The program MUST paste from copy area.

**Test**: Copy HTML. Paste it. Must change to AsciiDoc.

### Rule: No Questions

The program MUST NOT ask questions on open or save.

**Test**: Open any file. No pop-ups.

**Test**: Save As any type. No pop-ups.

---

## Look And Feel Rules

### Rule: New File

The program MUST let you make new files.

**Test**: Press Ctrl+N. Editor must clear.

### Rule: Open File

The program MUST let you open files.

**Test**: Press Ctrl+O. File picker must show.

### Rule: Save File

The program MUST let you save.

**Test**: Press Ctrl+S. File must save.

### Rule: Save As

The program MUST let you save as new name.

**Test**: Click Save As. Must ask for name.

### Rule: Dark Mode

The program MUST have dark mode.

**Test**: Press Ctrl+D. Colors must change to dark.

**Test**: Restart. Dark mode must stay on.

### Rule: Change Text Size

The program MUST let you zoom text.

**Test**: Press Ctrl++. Text must get bigger.

**Test**: Press Ctrl+-. Text must get smaller.

### Rule: Status Bar

The program MUST show info in status bar.

**Test**: Look at status bar. Must show document version (or "None").

**Test**: Look at status bar. Must show word count.

**Test**: Look at status bar. Must show grade level.

**Test**: Look at status bar. Must show AI/conversion status.

### Rule: Show Document Version (NEW v1.4)

The program MUST show document version in status bar.

**Test**: Open file with `:version: 1.3.0`. Status bar must show "v1.3.0".

**Test**: Open file with `*Version*: 2.0.0`. Status bar must show "v2.0.0".

**Test**: Open file with "AsciiDoc v1.4.0 Roadmap" title. Status bar must show "v1.4.0".

**Test**: Open file with no version. Status bar must show "None".

### Rule: Version Updates Automatically (NEW v1.4)

Version display MUST update when file changes.

**Test**: Open file. Add `:version: 1.5.0`. Status bar must update to "v1.5.0".

**Test**: Save file with version. Status bar must show version.

**Test**: Type version in editor. Status bar must update as you type.

### Rule: Fast Keys

The program MUST have keyboard shortcuts.

**Test**: Press Ctrl+N. New file must open.

**Test**: Press Ctrl+Q. Program must close.

Fast keys:

- Ctrl+N = New file
- Ctrl+O = Open file
- Ctrl+S = Save
- Ctrl+Q = Close
- Ctrl+F = Find
- Ctrl+D = Dark mode
- Ctrl++ = Big text
- Ctrl+- = Small text

### Rule: Remember Settings

The program MUST save your settings.

**Test**: Make window big. Close. Open. Window must be big.

**Test**: Open a file. Close. Open. Same file must open.

**Test**: Turn on dark mode. Close. Open. Dark mode must be on.

### Rule: Save Files Safely

The program MUST save files with no risk.

**Test**: Save file. Program must write to temp first, then replace.

**Test**: Disk full. Must show error and keep old file.

### Rule: Block Bad Paths

The program MUST stop dangerous paths.

**Test**: Try path like "../../../etc/passwd". Must block it.

---

## Build Rules

### Rule: Use Right Tools

The program MUST use:

- PySide6 6.9.0+ for windows (includes GPU support and QWebEngineView)
- asciidoc3 3.2.0+ for HTML
- pypandoc 1.11+ for file changes
- pymupdf 1.23.0+ for PDF reading (3-5x faster)
- keyring 24.0.0+ for safe keys
- psutil 5.9.0+ for system check
- Pandoc for conversions
- wkhtmltopdf for PDF
- Ollama (optional) for local AI features

**Test**: Install tools. All must work.

### Rule: Work In Background

The program MUST do slow work in background.

**Test**: Save to Git. Window must still work.

**Test**: Open big Word file. Window must still work.

### Rule: No Double Work

The program MUST stop two things at once.

**Test**: While saving, save button must turn off.

**Test**: While changing file, must wait for finish.

---

## Safety Rules

### Rule: No Data Sent Out

The program MUST NOT send data anywhere.

**Test**: Watch network. No data must go out.

### Rule: Save Local Only

The program MUST save everything on your computer.

**Test**: Check settings file. Must be in local folder.

Settings save here:

- Linux: `~/.config/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`
- Mac: `~/Library/Application Support/AsciiDocArtisan/`

### Rule: Safe Git Commands

The program MUST run Git safely.

**Test**: Run Git command. Must use safe method.

**Test**: Try Git without Git folder. Must check first.

---

## Speed Rules

### Rule: Start Fast

The program MUST start quick.

**Test**: Time it. Must show window in 3 seconds.

### Rule: Update Preview Fast

The preview MUST update smooth.

**Test**: Type text. Preview must update in 500ms (CPU) or 50ms (GPU).

**Note**: GPU speed makes this 10-50x faster (v1.4).

### Rule: Handle Big Files

The program MUST work with big files.

**Test**: Open 1 MB file. Must load smooth.

**Test**: Open 10 MB file. May be slow, but must work.

### Rule: Use Memory Well

The program MUST not waste memory.

**Test**: Run 8 hours. Memory use must stay same.

### Rule: Fast PDF Reading (v1.1+)

The program MUST read PDFs fast.

**Test**: Open PDF. Must use PyMuPDF (3-5x faster).

**Test**: Big PDF must open in half the time.

### Rule: GPU Acceleration (Enhanced v1.4)

The program MUST use GPU automatically when available.

**Test**: Start app with GPU. Logs show "GPU detected: NVIDIA GeForce RTX 4060".

**Test**: Logs show "Compute capabilities: cuda, opencl, vulkan".

**Test**: Preview uses QWebEngineView with GPU rasterization.

**Test**: CPU usage drops 70-90% compared to software rendering.

### Rule: NPU Detection (NEW v1.4)

The program MUST detect NPU if available.

**Test**: With Intel NPU: Logs show "NPU detected: Intel NPU".

**Test**: Logs show "OpenVINO backend configured".

**Test**: Without NPU: Program works normally with GPU/CPU.

---

## Hardware Acceleration Rules (NEW v1.4)

### Rule: Auto-Detect GPU

The program MUST detect GPU automatically.

**Test**: NVIDIA GPU: Detect via nvidia-smi.

**Test**: AMD GPU: Detect via rocm-smi.

**Test**: Intel GPU: Detect via clinfo and DRI devices.

**Test**: No GPU: Use software rendering, no crash.

### Rule: GPU Preview Rendering

The program MUST use GPU for preview when available.

**Test**: With GPU: Preview uses QWebEngineView.

**Test**: Chromium GPU flags enable: rasterization, zero-copy, hardware overlays.

**Test**: WebGL works in preview.

**Test**: Smooth 60fps+ scrolling.

### Rule: Compute Capabilities

The program MUST detect compute frameworks.

**Test**: CUDA detected with NVIDIA GPU.

**Test**: OpenCL detected when available.

**Test**: Vulkan detected when available.

**Test**: OpenVINO detected with NPU.

**Test**: ROCm detected with AMD GPU.

### Rule: Environment Configuration

The program MUST set GPU flags before starting.

**Test**: QT_OPENGL set to "desktop".

**Test**: QTWEBENGINE_CHROMIUM_FLAGS configured.

**Test**: NPU flags set when available.

### Rule: Hardware Fallback

The program MUST fall back gracefully.

**Test**: GPU fails: Use software rendering.

**Test**: QWebEngineView fails: Use QTextBrowser.

**Test**: No hardware acceleration: Program still works.

---

## Performance Rules (NEW v1.5.0)

### Rule: Fast Startup

The program MUST start fast.

**Test**: Time from run to window. Must be 2 seconds or less.

**Note**: v1.5.0 achieves 1.05s (beats v1.6.0 target!).

### Rule: Cancel Long Tasks

The program MUST let you stop long tasks.

**Test**: Start Git pull. Click cancel button. Task must stop.

**Test**: Cancel button must show during long tasks.

**Test**: Cancel button must hide when task done.

### Rule: Clean Code

The main window file MUST be small and easy to read.

**Test**: Count lines in main_window.py. Must be 700 or less.

**Note**: v1.5.0 achieves 577 lines (66% smaller than v1.4.0).

### Rule: Good Tests

The program MUST have tests for most code.

**Test**: Run coverage check. Must be 60% or more.

**Note**: v1.5.0 achieves 60%+ with 481+ tests.

---

## Test Rules

### Rule: Unit Tests

The program MUST have tests for all parts.

**Test**: Run `make test`. All must pass.

**Test**: Check coverage. Must be 60% or more (v1.5.0 target).

### Rule: Full Tests

The program MUST test real use.

**Test**: Test New, Open, Save, Save As. All must work.

**Test**: Test Commit, Push, Pull. All must work.

### Rule: Test All Computers

The program MUST be tested on all types.

**Test**: Run tests on Windows. All must pass.

**Test**: Run tests on Linux. All must pass.

**Test**: Run tests on Mac. All must pass.

---

## Version History

### Version 1.5.0 (Current)

**Status**: Complete
**Date**: October 28, 2025

**What's New**:

- ✅ **Fast startup** (1.05 seconds - beats v1.6.0 target!)
- ✅ **Main window refactoring** (577 lines, down from 1,719 - 66% smaller)
- ✅ **Worker pool system** (better task management)
- ✅ **Operation cancellation** (stop long tasks with button)
- ✅ **Lazy imports** (load tools only when needed)
- ✅ **Test coverage** (60%+ coverage, 481+ tests, +88 new tests)
- ✅ **Code quality** (less copied code in preview handlers)
- ✅ **Metrics collection** (track how fast things run)
- ✅ **Memory profiling** (find where memory goes)

**Performance**:
- Startup: 1.05s (3-5x faster than v1.4.0)
- Main window: 66% less code (easier to fix)
- Tests: 60%+ coverage (up from 34%)
- Preview: Still 10-50x faster with GPU (from v1.4.0)

### Version 1.4.0

**Status**: Production Ready
**Date**: October 27, 2025

**What's New**:

- ✅ **Full GPU/NPU hardware acceleration** (10-50x faster rendering)
- ✅ Auto-detect NVIDIA, AMD, Intel GPUs
- ✅ NPU detection and OpenVINO configuration
- ✅ Compute capabilities detection (CUDA, OpenCL, Vulkan, ROCm)
- ✅ QWebEngineView with GPU-accelerated preview
- ✅ Chromium hardware acceleration (rasterization, zero-copy, VAAPI)
- ✅ Smooth 60fps+ rendering with 70-90% less CPU usage
- ✅ **Document version display** in status bar
- ✅ Flexible version detection (AsciiDoc attributes, text labels, titles)
- ✅ Real-time version updates (on open, save, edit)
- ✅ Status bar reorganization (version first)
- ❌ Grammar system removed (simplified codebase)
- -2,067 lines of code (cleaner, faster)
- All tests passing

**Performance**:
- Preview: 10-50x faster with GPU
- CPU usage: 70-90% reduction
- Scrolling: Smooth 60fps+
- Hardware video decode: VAAPI enabled

### Version 1.3.0

**Status**: Deprecated
**Date**: October 27, 2025 (morning)

**What It Had**:

- Grammar checking with AI (removed in v1.4)
- LanguageTool integration (removed in v1.4)
- Ollama grammar worker (removed in v1.4)
- +4,362 lines (removed in v1.4 for simplicity)

**Why Removed**:
- Caused performance issues
- Added complexity without clear benefit
- User requested removal

### Version 1.2.0

**Status**: Production Ready
**Date**: October 26, 2025

**What's New**:

- ✅ Ollama AI conversions (fully working)
- ✅ AI Status menu with model selection
- ✅ Real-time status bar (shows active AI model)
- ✅ Automatic Pandoc fallback
- Removed cloud AI (Anthropic SDK)
- Privacy focused (no data leaves computer)
- All 400+ tests passing
- Clean codebase (removed 796 lines of cloud AI code)

### Version 1.1.0

**Status**: Works
**Date**: October 2025

**What's New**:

- GPU speed (2-5x faster preview - basic)
- Fast PDF reading (3-5x faster)
- Optimized Python code
- 400+ tests pass
- Works on all computers

### Version 1.0.0

**Status**: First release
**Date**: 2024

**What It Had**:

- Basic editing
- Basic preview
- First tests

---

## What We Might Add

Things for later:

### Edit

- Find and replace
- Auto-complete
- Color text

### Preview

- Zoom preview
- Print preview
- Change colors

### Git

- See old versions
- Compare versions
- Use branches
- Merge help

### Teams

- Share files
- Edit together
- Add notes
- Team rooms

### Local AI (Ollama) - ✅ IMPLEMENTED

**Current Features**:
- ✅ AI-powered format conversions (all formats)
- ✅ Model selection from installed Ollama models
- ✅ Real-time status bar updates
- ✅ Automatic Pandoc fallback

**Future Features**:
- Text improvement
- Auto-format suggestions
- Content summarization

### Hardware Acceleration - ✅ IMPLEMENTED (v1.4)

**Current Features**:
- ✅ Full GPU acceleration (NVIDIA, AMD, Intel)
- ✅ NPU detection and configuration
- ✅ Compute capabilities detection
- ✅ QWebEngineView GPU rendering
- ✅ Hardware video decode/encode

**Future Features**:
- GPU-accelerated PDF rendering
- NPU-based text analysis
- Vulkan direct rendering
- Performance metrics UI

---

## Summary

**What It Does**:
Helps you write AsciiDoc. Shows preview fast with GPU. Uses Git. Changes file types. Shows document version. Starts in 1 second. Can cancel tasks.

**Who It's For**:
Writers, coders, students, teachers, teams.

**Main Parts**:
GPU-accelerated preview, file changes, Git, works everywhere, safe, fast startup, clean code.

**Status**:
Version 1.5.0 - Complete

**Reading Level**:
Grade 5.0 - Easy to read!

**Hardware Support**:
GPU (NVIDIA, AMD, Intel), NPU (Intel), CPU (all systems)

---

**Doc Info**: Main rules | Grade 5.0 | v1.5.0 | October 28, 2025
