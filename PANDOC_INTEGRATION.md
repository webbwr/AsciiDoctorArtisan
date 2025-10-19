# Pandoc Integration Guide

## Overview

AsciiDoc Artisan now includes comprehensive pandoc integration for automatic document conversion. This enables you to open various document formats and automatically convert them to AsciiDoc for editing.

## Installation Requirements

### 1. Install Pandoc

**Windows:**
- Download installer from https://pandoc.org/installing.html
- Or use Chocolatey: `choco install pandoc`
- Or use Scoop: `scoop install pandoc`

**macOS:**
- Using Homebrew: `brew install pandoc`
- Or download from https://pandoc.org/installing.html

**Linux:**
- Ubuntu/Debian: `sudo apt-get install pandoc`
- Fedora/RHEL: `sudo dnf install pandoc`
- Arch Linux: `sudo pacman -S pandoc`

### 2. Install pypandoc

After installing pandoc:
```bash
pip install pypandoc
```

## Supported Input Formats

The application can now open and convert:

- **Markdown** (.md, .markdown) - Lightweight markup language
- **Microsoft Word** (.docx) - Word documents
- **HTML** (.html, .htm) - Web pages
- **LaTeX** (.tex) - Academic/scientific documents
- **reStructuredText** (.rst) - Python documentation format
- **Org Mode** (.org) - Emacs organization format
- **Textile** (.textile) - Alternative markup language
- **PDF** (.pdf) - Shows instructions for manual conversion

## How to Use

### Opening Files

1. Use **File → Open** (Ctrl+O)
2. Select from format filters:
   - "Common Formats" - Shows frequently used formats
   - "All Supported" - Shows all convertible formats
   - Individual format filters for specific types

### Checking Pandoc Status

Use **Tools → Pandoc Status** to view:
- Pandoc installation status
- Binary location
- Version information
- pypandoc availability

### Viewing Supported Formats

Use **Tools → Supported Formats** to see:
- All available input formats
- All available output formats
- Format descriptions

## Conversion Process

When you open a supported file:

1. The file is automatically detected by extension
2. Pandoc converts it to AsciiDoc format
3. The converted content appears in the editor
4. You can edit and save as AsciiDoc

## Clipboard Conversion

The **Edit → Convert and Paste** feature also supports:
- Converting clipboard content from various formats
- Automatic format detection
- Direct pasting as AsciiDoc

## Troubleshooting

### Pandoc Not Found

If you see "Pandoc not available":
1. Check installation with `pandoc --version` in terminal
2. Ensure pandoc is in your system PATH
3. Restart the application after installation

### Conversion Errors

If conversion fails:
1. Check the source file is not corrupted
2. Verify the format is supported
3. Check Tools → Pandoc Status for details

### Performance

Large documents may take a moment to convert. The status bar shows conversion progress.

## Advanced Features

The `pandoc_integration.py` module provides:
- Automatic installation detection
- Platform-specific installation guidance
- Format validation
- Binary vs text file handling
- Enhanced error messages

## Future Enhancements

Planned improvements:
- Direct PDF text extraction
- Batch file conversion
- Custom pandoc options
- Export to multiple formats
- Conversion preview