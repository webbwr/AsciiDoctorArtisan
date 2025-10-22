# AsciiDoc Artisan - Enhanced Conversion Test Guide

## 🚀 New Conversion Features

The application now provides a complete WYSIWYG experience when converting documents:

### What's New:

1. **Progress Indicators During Conversion**
   - Editor shows: `// Converting filename to AsciiDoc...`
   - Preview shows: "Converting document..." message
   - Status bar displays conversion details

2. **Raw AsciiDoc Markup in Editor**
   - After conversion, see the actual AsciiDoc syntax
   - Edit the markup directly
   - Changes update preview in real-time

3. **WYSIWYG Preview**
   - Right pane shows rendered HTML
   - Proper formatting, headers, lists, etc.
   - Updates automatically after conversion

## 🧪 Testing the Enhanced Conversion

### Test 1: Markdown File
1. Open `test_conversion.md` using File → Open
2. Watch the conversion progress messages
3. See the raw AsciiDoc markup in the left editor pane:
   ```asciidoc
   = Test Document for AsciiDoc Artisan

   This is a *test document* to demonstrate...
   ```
4. See the WYSIWYG preview in the right pane

### Test 2: Word Document
1. Open any `.docx` file
2. Watch the background conversion
3. Edit the resulting AsciiDoc markup
4. Preview updates automatically

### Test 3: HTML File
1. Open any `.html` file
2. See HTML converted to clean AsciiDoc
3. Preview shows properly formatted content

## 📝 What to Look For

### In the Editor (Left Pane):
- Raw AsciiDoc syntax
- Proper conversion of:
  - Headers: `= Title` (level 1), `== Section` (level 2)
  - Bold: `*bold text*`
  - Italic: `_italic text_`
  - Code blocks: `[source,language]` followed by `----`
  - Links: `https://example.com[Link Text]`

### In the Preview (Right Pane):
- Rendered HTML output
- Proper formatting
- Working links
- Syntax-highlighted code blocks
- Tables and lists

## 🎯 Conversion Flow

```
1. Select File → Open
2. Choose document (MD, DOCX, HTML, etc.)
3. Progress shown in editor/preview/status
4. Pandoc converts in background thread
5. Raw AsciiDoc appears in editor
6. Preview shows rendered content
7. Ready to edit!
```

## 💡 Tips

- The conversion happens in a background thread - UI stays responsive
- Large documents may take a moment to convert
- If conversion fails, you'll see detailed error information
- The raw markup allows precise control over formatting
- Preview updates as you type (with slight debounce)

## 🐛 Testing Error Handling

Try opening a corrupted file to see the improved error handling:
- Clear error messages
- Editor and preview show failure state
- Detailed information about what went wrong

Enjoy the enhanced WYSIWYG experience!