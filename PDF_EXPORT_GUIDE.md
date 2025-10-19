# PDF Export Guide

## PDF Engine Requirement

To export documents to PDF format, you need a PDF engine installed on your system. AsciiDoc Artisan will automatically detect and use any of the following engines:

### Recommended: wkhtmltopdf

The easiest option for most users:

**Ubuntu/Debian:**
```bash
sudo apt-get install wkhtmltopdf
```

**Windows:**
Download installer from: https://wkhtmltopdf.org/downloads.html

**macOS:**
```bash
brew install --cask wkhtmltopdf
```

### Alternative Options

1. **weasyprint** (Python-based)
   ```bash
   pip install weasyprint
   ```

2. **TeX Live** (for pdflatex/xelatex/lualatex)
   - Full LaTeX distribution
   - Larger download but excellent output
   - https://www.tug.org/texlive/

3. **Prince** (Commercial)
   - Professional-grade PDF output
   - https://www.princexml.com/

## How It Works

1. When you export to PDF, AsciiDoc Artisan checks for available PDF engines
2. It automatically selects the first available engine from the list above
3. If no engine is found, you'll see a helpful error message

## Troubleshooting

If you see "pdflatex not found" or similar errors:

1. Install one of the PDF engines listed above (wkhtmltopdf recommended)
2. Restart AsciiDoc Artisan after installation
3. Try the export again

## Alternative Export Options

If you cannot install a PDF engine, consider:
- Export to HTML (can be printed to PDF from browser)
- Export to DOCX (can be converted to PDF in Word/LibreOffice)
- Export to Markdown (for other tools)