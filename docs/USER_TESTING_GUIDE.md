# User Testing Guide

**Version**: 1.1.0
**Date**: October 26, 2025
**Reading Level**: Grade 5.0
**For**: Testing and validation

---

## What to Test

This guide helps you test all features of AsciiDoc Artisan.

### Quick Test (5 minutes)

Fast check that everything works:

1. **Start the app**
   ```bash
   cd /home/webbp/github/AsciiDoctorArtisan
   source venv/bin/activate
   python src/main.py
   ```

2. **Type some text**
   - Type: `= Hello World`
   - Type: `This is a test`
   - Check: Right side shows preview

3. **Save a file**
   - Click File → Save
   - Name it: `test.adoc`
   - Check: File saved

4. **Close and reopen**
   - Close app
   - Open app again
   - Check: Last file still open

---

## Full Test (30 minutes)

Complete test of all features:

### Test 1: Basic Editing

**What**: Type and edit text

**Steps**:
1. Create new file (File → New)
2. Type this:
   ```
   = My Document
   :toc:

   == First Section

   This is my text.

   * Item 1
   * Item 2

   == Second Section

   More content here.
   ```
3. Watch preview update as you type

**Expected**:
- ✓ Preview shows formatted text
- ✓ Title is big and bold
- ✓ Bullets show as list
- ✓ Table of contents appears

**If it fails**: Check logs, report error

---

### Test 2: File Operations

**What**: Save, open, and manage files

**Steps**:
1. Save file (Ctrl+S or File → Save)
2. Close app
3. Open app
4. Open same file (File → Open)
5. Edit text
6. Save again

**Expected**:
- ✓ File saves without errors
- ✓ File reopens correctly
- ✓ Changes save properly
- ✓ No data loss

**If it fails**: Check file permissions

---

### Test 3: Export Features

**What**: Export to different formats

**Steps**:
1. Open a file with content
2. Click File → Export → PDF
3. Choose location
4. Click File → Export → HTML
5. Choose location
6. Check both files exist

**Expected**:
- ✓ PDF created and readable
- ✓ HTML created and viewable
- ✓ Formatting preserved
- ✓ No errors shown

**If it fails**: Check if `wkhtmltopdf` and `pandoc` installed

---

### Test 4: Dark Mode

**What**: Switch between light and dark themes

**Steps**:
1. Click View → Dark Mode
2. Check colors changed
3. Click View → Dark Mode again
4. Check back to light

**Expected**:
- ✓ Dark mode is dark background
- ✓ Light mode is light background
- ✓ Text is readable in both
- ✓ Preview matches theme

**If it fails**: Check theme manager

---

### Test 5: Zoom Controls

**What**: Make text bigger and smaller

**Steps**:
1. Click View → Zoom In (or Ctrl++)
2. Check text is bigger
3. Click View → Zoom In again
4. Click View → Zoom Out (or Ctrl+-)
5. Check text is smaller

**Expected**:
- ✓ Editor text changes size
- ✓ Preview changes size too
- ✓ Smooth transition
- ✓ Readable at all sizes

**If it fails**: Fixed in latest version

---

### Test 6: Git Integration (Optional)

**What**: Save to Git (if in Git repo)

**Steps**:
1. Make sure file is in Git repo
2. Edit file
3. Click Git → Commit
4. Enter message: "Test commit"
5. Click OK
6. Click Git → Push (if remote exists)

**Expected**:
- ✓ Commit succeeds
- ✓ Push succeeds (if remote)
- ✓ Status shows "clean"
- ✓ No errors

**If it fails**: Check Git is installed and configured

---

### Test 7: Import PDF (v1.1 Feature)

**What**: Import text from PDF

**Steps**:
1. Get a PDF file with text
2. Click File → Import → PDF
3. Select the PDF
4. Check text appears

**Expected**:
- ✓ PDF opens quickly (3-5x faster)
- ✓ Text extracts correctly
- ✓ Tables convert to AsciiDoc
- ✓ Formatting preserved

**If it fails**: Check PyMuPDF installed

---

### Test 8: GPU Acceleration (v1.1 Feature)

**What**: Preview uses GPU

**Steps**:
1. Open app
2. Check logs for GPU message
3. Create large document (50+ sections)
4. Watch preview update

**Expected**:
- ✓ Logs show "GPU acceleration enabled"
- ✓ Preview is smooth and fast
- ✓ CPU usage is low (<50%)
- ✓ Updates in under 1 second

**If it fails**: Check GPU drivers installed

**Check logs**:
```bash
# Look for this in terminal:
# "GPU acceleration enabled - using QWebEngineView"
```

---

### Test 9: Performance (v1.1 Feature)

**What**: App is fast and responsive

**Steps**:
1. Create file with 100+ lines
2. Type quickly
3. Watch preview
4. Save file
5. Export to PDF

**Expected**:
- ✓ Typing feels instant
- ✓ Preview updates smoothly
- ✓ No lag or freezing
- ✓ Save is quick (<1 second)
- ✓ Export is fast (<3 seconds)

**If it fails**: Check hardware detection

**Run this to check**:
```bash
python src/asciidoc_artisan/core/hardware_detection.py
```

---

## Performance Benchmarks

### Expected Speeds (v1.1)

| Operation | Time | Notes |
|-----------|------|-------|
| App startup | <3 seconds | First time |
| Open file (1MB) | <500ms | Subsequent faster |
| Save file | <100ms | SSD recommended |
| Preview update | <350ms | With GPU |
| PDF export | <3 seconds | Depends on size |
| PDF import | 3-5x faster | vs v1.0 |

### System Requirements Met

**Minimum**:
- ✓ Python 3.11+
- ✓ 4GB RAM
- ✓ Any CPU
- ✓ Any GPU (or none)

**Recommended**:
- ✓ Python 3.12
- ✓ 8GB+ RAM
- ✓ 4+ CPU cores
- ✓ Dedicated GPU

---

## Common Issues

### Issue: App won't start

**Symptoms**: Error on launch
**Fix**:
```bash
source venv/bin/activate
pip install -r requirements-production.txt
python src/main.py
```

### Issue: Preview not showing

**Symptoms**: Right side is blank
**Fix**:
- Check if Qt WebEngine installed
- Try View → Update Preview
- Restart app

### Issue: Can't export PDF

**Symptoms**: Export fails with error
**Fix**:
```bash
# Install wkhtmltopdf
sudo apt install wkhtmltopdf
```

### Issue: Git operations fail

**Symptoms**: Git menu items error
**Fix**:
- Ensure file is in Git repo
- Run `git status` in terminal
- Configure Git:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  ```

### Issue: Slow performance

**Symptoms**: Laggy, unresponsive
**Fix**:
1. Check hardware:
   ```bash
   python src/asciidoc_artisan/core/hardware_detection.py
   ```
2. Update GPU drivers
3. Close other apps
4. Check system resources

---

## Bug Reporting

If you find bugs, report them with:

### What to Include

1. **What you did**
   - Step by step actions

2. **What happened**
   - Exact error message
   - Screenshot if possible

3. **What you expected**
   - What should have happened

4. **System info**
   - OS: (Windows/Mac/Linux)
   - Python version: `python --version`
   - App version: v1.1.0

5. **Logs**
   - Copy terminal output
   - Include any error messages

### Where to Report

Create issue on GitHub:
- https://github.com/webbwr/AsciiDoctorArtisan/issues

---

## Success Checklist

After testing, you should have:

- [ ] Started app successfully
- [ ] Created and edited file
- [ ] Saved file
- [ ] Reopened file
- [ ] Exported to PDF
- [ ] Exported to HTML
- [ ] Tried dark mode
- [ ] Tested zoom controls
- [ ] Imported PDF (if available)
- [ ] Checked performance is good
- [ ] No crashes or errors

**If all checked**: App is working well! ✓

**If some failed**: Report issues with details above.

---

## Advanced Testing

### Load Test

Test with large files:

1. Create file with 1000+ lines
2. Add many sections
3. Add many lists and tables
4. Test all operations

**Expected**:
- Still responsive
- Preview updates
- Save works
- Export works

### Stress Test

Test rapid operations:

1. Type very fast
2. Switch files quickly
3. Spam zoom controls
4. Toggle dark mode repeatedly

**Expected**:
- No crashes
- No freezing
- All operations complete
- No data loss

### Memory Test

Test memory usage:

1. Open large file
2. Leave app running 1 hour
3. Check memory usage
4. Create/edit/save many files

**Expected**:
- Memory stays under 500MB
- No memory leaks
- Performance stays good

**Check memory**:
```bash
python memory_profile.py
```

---

## Automated Tests

Run automated tests before manual testing:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_pdf_extractor.py -v
pytest tests/test_ui_integration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected**: All tests pass (400+)

---

## Performance Verification

### GPU Acceleration

**Test**: Is GPU being used?

```bash
# Start app
python src/main.py

# Look for in logs:
# "GPU acceleration enabled"
# "NVIDIA GeForce RTX..." (or your GPU)
```

**Or run**:
```bash
python src/asciidoc_artisan/core/hardware_detection.py
```

### PDF Speed

**Test**: Is PyMuPDF 3-5x faster?

1. Get a PDF with tables (10+ pages)
2. Import it: File → Import → PDF
3. Time how long it takes

**Expected**:
- Small PDF (1-5 pages): <1 second
- Medium PDF (10-20 pages): 1-3 seconds
- Large PDF (50+ pages): 3-10 seconds

Much faster than v1.0!

---

## Local AI Testing (Optional)

If Ollama is installed:

### Test Ollama

```bash
# Check Ollama is running
systemctl status ollama

# Test model
ollama run phi3:mini "What is AsciiDoc?"
```

**Expected**:
- Service is running
- Model responds quickly
- ~95 tokens/second

### Future AI Features

Not yet integrated into app, but ready:
- Grammar checking
- Text improvement
- Format suggestions

See `docs/OLLAMA_SETUP.md` for setup.

---

## Summary

### Quick Check

✓ All features work
✓ No crashes
✓ Performance is good
✓ GPU acceleration enabled
✓ PDF import is fast

### Report Results

Share your findings:
- What worked well
- What needs improvement
- Any bugs found
- Performance feedback

---

**Document Info**: User Testing Guide | v1.1.0 | Grade 5.0 | October 2025
