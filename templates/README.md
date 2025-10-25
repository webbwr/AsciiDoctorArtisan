# AsciiDoc Templates

This directory contains AsciiDoc project templates for creating documentation.

## Available Templates

### default/

The default AsciiDoc project template includes:

- **docs/** - Documentation source files (index.adoc, chapter1.adoc, chapter2.adoc)
- **images/** - Image assets directory
- **themes/** - Custom themes and stylesheets
- **output/** - Generated output (HTML, PDF)
- **build.sh** - Build script for generating documentation
- **Makefile** - Build automation
- **asciidoc-config.yml** - Configuration file
- **README.adoc** - Template README

## Using Templates

### Option 1: Copy Template to New Location

```bash
# Copy the default template to your project
cp -r templates/default/* /path/to/your/project/

# Navigate to your project
cd /path/to/your/project/

# Build documentation
./build.sh html
# or
make html
```

### Option 2: Build from Repository

```bash
# Build template HTML
make template-html

# Build template PDF
make template-pdf

# Clean template output
make template-clean
```

## Creating New Templates

To create a new template:

1. Copy the `default/` directory
2. Customize the structure and content
3. Update configuration files
4. Test the build process

## Template Structure

```
template-name/
├── docs/                   # Documentation source
│   ├── index.adoc         # Main document
│   ├── chapter1.adoc      # Sample chapter
│   └── chapter2.adoc      # Sample chapter
├── images/                # Image assets
├── themes/                # Custom themes
├── output/                # Generated output
├── build.sh              # Build script
├── Makefile              # Build automation
├── asciidoc-config.yml   # Configuration
└── README.adoc           # Template README
```

## Build Tools

Templates include multiple build options:

- **build.sh** - Bash script for Linux/WSL/macOS
- **Makefile** - Make-based build system
- Direct asciidoctor commands

## Output Formats

Templates support generating:

- HTML (single page or chunked)
- PDF (via asciidoctor-pdf)
- EPUB (via asciidoctor-epub3)
- DocBook (for further processing)

## Resources

- [AsciiDoctor Documentation](https://asciidoctor.org/docs/)
- [AsciiDoc Syntax Quick Reference](https://asciidoctor.org/docs/asciidoc-syntax-quick-reference/)
- [AsciiDoc Language Documentation](https://docs.asciidoctor.org/asciidoc/latest/)
