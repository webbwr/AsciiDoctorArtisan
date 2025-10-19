# Testing Save as AsciiDoc Feature

## Feature Implementation Summary

The File → Save menu action has been updated to always save documents in AsciiDoc format (.adoc extension).

### Changes Made:

1. **Save Logic Update**: Modified the `save_file` method in `adp_windows.py` to:
   - Check if the current file has a non-AsciiDoc extension
   - Automatically convert the extension to `.adoc` when saving
   - Log the format conversion

2. **UI Update**: Updated the Save action's statusTip to indicate "Save the document as AsciiDoc format (.adoc)"

### How to Test:

1. **Open a non-AsciiDoc file**:
   - Use File → Open to open `test_save_functionality.md` (or any .md, .docx file)
   - The file will be converted to AsciiDoc and displayed in the editor

2. **Use File → Save**:
   - Press Ctrl+S or use File → Save
   - Notice the status bar message: "Saved as AsciiDoc: [filename].adoc"
   - The window title should update to show the new .adoc filename

3. **Verify the file**:
   - Check that a new `.adoc` file has been created
   - The original file remains unchanged
   - The saved file contains the AsciiDoc content

### Expected Behavior:

- **File → Save**: Always saves as `.adoc` format, regardless of the original file type
- **File → Save As**: Offers multiple format options (AsciiDoc, Markdown, Word, PDF)
- **Export As submenu**: Provides quick access to export in different formats

### Example Test Case:

1. Open `test_save_functionality.md`
2. Make a small edit (add a line)
3. Press Ctrl+S
4. Check that:
   - A file named `test_save_functionality.adoc` is created
   - The window title shows `test_save_functionality.adoc`
   - The status bar confirms "Saved as AsciiDoc"

This ensures that the primary working format is always AsciiDoc, while still allowing exports to other formats via Save As or Export As.