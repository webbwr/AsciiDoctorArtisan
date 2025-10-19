# Test Document for AsciiDoc Artisan

This is a **test document** to demonstrate the automatic conversion from Markdown to AsciiDoc.

## Features to Test

### Text Formatting

- **Bold text** using double asterisks
- *Italic text* using single asterisks
- `Inline code` using backticks
- ~~Strikethrough~~ text

### Code Blocks

```python
# Python example
def convert_to_asciidoc(content):
    """Convert markdown to AsciiDoc format"""
    return pandoc.convert(content, 'asciidoc')
```

### Lists

1. First ordered item
2. Second ordered item
   - Nested unordered item
   - Another nested item
3. Third ordered item

### Links and Images

- [AsciiDoc Official Site](https://asciidoc.org)
- [Pandoc Documentation](https://pandoc.org)

### Blockquotes

> This is a blockquote that should convert nicely to AsciiDoc format.
> It can span multiple lines.

### Tables

| Format | Extension | Description |
|--------|-----------|-------------|
| Markdown | .md | Simple markup |
| AsciiDoc | .adoc | Powerful docs |
| HTML | .html | Web format |

---

**Try opening this file in AsciiDoc Artisan to see the automatic conversion!**