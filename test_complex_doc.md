# Advanced AsciiDoc Conversion Test

This document tests the enhanced conversion and WYSIWYG rendering capabilities.

## Document Features

### Text Formatting

This paragraph contains **bold text**, *italic text*, `inline code`, and ***bold italic*** text. We also have ~~strikethrough~~ and `monospace` formatting.

### Code Blocks with Syntax Highlighting

```python
def convert_to_asciidoc(file_path):
    """Convert any document to AsciiDoc format."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Process with pandoc
    result = pandoc.convert(content, 'asciidoc')
    return result
```

```javascript
// JavaScript example
const editor = new AsciiDocEditor({
    theme: 'dark',
    preview: true,
    wysiwyg: true
});
```

### Lists and Nested Items

1. First ordered item
   - Nested unordered item
   - Another nested item
     * Deep nested item
     * More nesting
2. Second ordered item
   1. Nested ordered
   2. Another nested
3. Third ordered item

### Tables

| Feature | Description | Status |
|---------|-------------|--------|
| Markdown Support | Convert MD to AsciiDoc | ✓ Complete |
| DOCX Support | Convert Word documents | ✓ Complete |
| PDF Support | Extract and convert | ⚠ Limited |
| WYSIWYG Preview | Real-time rendering | ✓ Enhanced |

### Blockquotes and Admonitions

> This is a blockquote that should be properly converted to AsciiDoc format with appropriate styling.
>
> It can span multiple paragraphs.

**Note:** This should become a NOTE admonition in AsciiDoc.

**Warning:** This should become a WARNING admonition.

**Important:** This should become an IMPORTANT admonition.

### Links and References

- [AsciiDoc Official Documentation](https://asciidoc.org)
- [Pandoc User Guide](https://pandoc.org/MANUAL.html)
- [GitHub Repository](https://github.com/webbwr/AsciiDoctorArtisan)

### Images

![AsciiDoc Logo](https://asciidoc.org/images/asciidoc-logo.png)

### Mathematical Expressions

When $a \ne 0$, there are two solutions to $(ax^2 + bx + c = 0)$:

$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$

### Document Metadata

- Author: Test User
- Date: 2024-10-19
- Version: 1.0.0

---

This comprehensive test document should demonstrate the full WYSIWYG capabilities of the enhanced AsciiDoc Artisan editor.