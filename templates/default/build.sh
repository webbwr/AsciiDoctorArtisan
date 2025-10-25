#!/bin/bash
# AsciiDoc Artisan Build Script

set -e

# Configuration
DOCS_DIR="docs"
OUTPUT_DIR="output"
MAIN_DOC="docs/index.adoc"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}==================================${NC}"
    echo -e "${BLUE}  AsciiDoc Artisan Build Script${NC}"
    echo -e "${BLUE}==================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_dependencies() {
    echo "Checking dependencies..."

    if ! command -v asciidoctor &> /dev/null; then
        print_error "asciidoctor not found. Please install it first."
        echo "  gem install asciidoctor"
        exit 1
    fi
    print_success "asciidoctor found"

    if command -v asciidoctor-pdf &> /dev/null; then
        print_success "asciidoctor-pdf found"
        HAS_PDF=true
    else
        echo "  asciidoctor-pdf not found (PDF generation disabled)"
        HAS_PDF=false
    fi
    echo ""
}

build_html() {
    echo "Building HTML documentation..."
    mkdir -p "$OUTPUT_DIR"

    if asciidoctor "$MAIN_DOC" -o "$OUTPUT_DIR/index.html"; then
        print_success "HTML built: $OUTPUT_DIR/index.html"
    else
        print_error "HTML build failed"
        return 1
    fi
}

build_pdf() {
    if [ "$HAS_PDF" = false ]; then
        echo "Skipping PDF build (asciidoctor-pdf not installed)"
        return 0
    fi

    echo "Building PDF documentation..."
    mkdir -p "$OUTPUT_DIR"

    if asciidoctor-pdf "$MAIN_DOC" -o "$OUTPUT_DIR/index.pdf"; then
        print_success "PDF built: $OUTPUT_DIR/index.pdf"
    else
        print_error "PDF build failed"
        return 1
    fi
}

clean_output() {
    echo "Cleaning output directory..."
    rm -rf "$OUTPUT_DIR"/*
    print_success "Output directory cleaned"
}

# Main script
print_header

case "${1:-html}" in
    html)
        check_dependencies
        build_html
        ;;
    pdf)
        check_dependencies
        build_pdf
        ;;
    both)
        check_dependencies
        build_html
        echo ""
        build_pdf
        ;;
    clean)
        clean_output
        ;;
    *)
        echo "Usage: $0 {html|pdf|both|clean}"
        echo ""
        echo "  html  - Build HTML documentation (default)"
        echo "  pdf   - Build PDF documentation"
        echo "  both  - Build both HTML and PDF"
        echo "  clean - Clean output directory"
        exit 1
        ;;
esac

echo ""
print_success "Build complete!"
