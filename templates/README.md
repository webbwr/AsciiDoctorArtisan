# AsciiDoc Templates

This folder has templates for docs.

## What's Here

### default/

Default template has:

- **docs/** - Doc files
- **images/** - Pictures
- **themes/** - Looks
- **output/** - Made files
- **build.sh** - Build script
- **Makefile** - Build help
- **asciidoc-config.yml** - Settings
- **README.adoc** - Info

## How to Use

### Way 1: Copy

```bash
# Copy it
cp -r templates/default/* /path/to/your/project/

# Go there
cd /path/to/your/project/

# Build
./build.sh html
# or
make html
```

### Way 2: Build Here

```bash
# Build HTML
make template-html

# Build PDF
make template-pdf

# Clean
make template-clean
```

## Make New

To make new:

1. Copy `default/`
2. Change files
3. Update settings
4. Test

## Parts

```
template-name/
├── docs/       # Docs
├── images/     # Pics
├── themes/     # Looks
├── output/     # Made
├── build.sh   # Script
├── Makefile   # Help
└── README.adoc # Info
```

## Build Tools

Build with:

- **build.sh** - Bash
- **Makefile** - Make
- Direct commands

## Output Types

Make:

- HTML
- PDF
- EPUB
- DocBook

## Help

- [Docs](https://asciidoctor.org/docs/)
- [Quick Help](https://asciidoctor.org/docs/asciidoc-syntax-quick-reference/)
- [Language](https://docs.asciidoctor.org/asciidoc/latest/)
