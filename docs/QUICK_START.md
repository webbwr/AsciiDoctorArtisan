# AsciiDoc Artisan - Quick Start Guide

## 🚀 Application is Now Running!

The AsciiDoc Artisan editor should now be open on your display. If you don't see the window, check your taskbar or use Alt+Tab.

## ✨ New Features Added

### 1. **Enhanced File Format Support**
- Open files in multiple formats: Markdown, HTML, LaTeX, RST, and more
- Automatic conversion to AsciiDoc format
- Use **File → Open** to try different file types

### 2. **Pandoc Integration**
- **Tools → Pandoc Status**: Check pandoc installation
- **Tools → Supported Formats**: View all available formats
- Automatic format detection and conversion

### 3. **Supported Input Formats**
- **Markdown** (.md, .markdown)
- **HTML** (.html, .htm)
- **Microsoft Word** (.docx)
- **LaTeX** (.tex)
- **reStructuredText** (.rst)
- **Org Mode** (.org)
- **Textile** (.textile)
- **PDF** (.pdf) - Shows helpful instructions

## 🧪 Test the Features

### Test Markdown Conversion
1. Click **File → Open**
2. Select "Common Formats" or "All Supported" from the file type dropdown
3. Open any `.md` file (or create one)
4. Watch it convert automatically to AsciiDoc!

### Test Pandoc Status
1. Click **Tools → Pandoc Status**
2. See detailed information about your pandoc installation
3. Version 3.1.3 is installed and ready

### Create a Test Document
Try typing this in the editor:
```asciidoc
= My AsciiDoc Document
Author Name
:toc: left
:icons: font

== Introduction

This is a test of the *AsciiDoc Artisan* editor with _enhanced features_.

=== Code Example

[source,python]
----
def hello_world():
    print("Hello from AsciiDoc Artisan!")
----

=== Features

* Automatic preview updates
* Multiple format support
* Git integration
* Dark/Light themes
```

## 🎯 Key Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **Ctrl+N**: New file
- **Ctrl+Z/Y**: Undo/Redo
- **Ctrl+=/-**: Zoom in/out
- **F5**: Toggle dark mode

## 📝 What's Next?

1. Try opening different file formats
2. Test the live preview (right panel)
3. Explore the Git menu for version control
4. Use Edit → Convert and Paste for clipboard content

## 🐛 Troubleshooting

If the window doesn't appear:
- Ensure X11 server is running (for WSL users)
- Check `echo $DISPLAY` returns `:0` or similar
- Try running with: `DISPLAY=:0 python adp_windows.py`

## 📚 Documentation

- See `PANDOC_INTEGRATION.md` for format conversion details
- See `README.md` for full feature list
- See `CONTRIBUTING.md` for contribution guidelines

Enjoy using AsciiDoc Artisan with its powerful features!