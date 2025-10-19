# Save As Functionality Fix Summary

## Issue Found
The File → Save As functionality was not saving files when different formats were selected. The root cause was a call to a non-existent method `_show_conversion_progress`.

## Fixes Applied

1. **Removed calls to missing method**:
   - Replaced `_show_conversion_progress()` calls with `statusBar.showMessage()`
   - This was causing exceptions that prevented the save operation from completing

2. **Added debug logging**:
   - Added logging to trace the Save As dialog flow
   - Added logging to track pandoc conversion requests
   - This will help debug any future issues

## How to Test the Fix

1. **Create or open a document** in AsciiDoc Artisan
2. **Use File → Save As** (or Ctrl+Shift+S)
3. **Select a format from the dropdown**:
   - GitHub Markdown Files (*.md *.markdown)
   - Microsoft Word 365 Documents (*.docx)
   - Adobe Acrobat PDF Files (*.pdf)
4. **Enter a filename** and click Save
5. **Verify the file is created** in the selected format

## Expected Behavior

- **Markdown (.md)**: Creates a Markdown file with the converted content
- **Word (.docx)**: Creates a Word document (requires pandoc)
- **PDF (.pdf)**: Creates a PDF file (requires pandoc and optional PDF engine)
- **AsciiDoc (.adoc)**: Saves directly without conversion

## Technical Details

The Save As process now:
1. Shows the save dialog with format options
2. Determines the format from the selected filter
3. For non-AsciiDoc formats:
   - Creates a temporary AsciiDoc file
   - Uses pandoc to convert to the target format
   - Shows progress in the status bar
   - Handles the conversion result appropriately

The application is currently running (ID: 311962) for testing.