# AsciiDoc Artisan Makefile

# Variables
ASCIIDOCTOR = asciidoctor
ASCIIDOCTOR_PDF = asciidoctor-pdf
DOCS_DIR = docs
OUTPUT_DIR = output
IMAGES_DIR = images

# Source files
MAIN_DOC = $(DOCS_DIR)/index.adoc
ALL_DOCS = $(wildcard $(DOCS_DIR)/*.adoc)

# Output files
HTML_OUTPUT = $(OUTPUT_DIR)/index.html
PDF_OUTPUT = $(OUTPUT_DIR)/index.pdf

# Default target
.PHONY: all
all: html

# Build HTML
.PHONY: html
html: $(HTML_OUTPUT)

$(HTML_OUTPUT): $(ALL_DOCS)
	@echo "Building HTML documentation..."
	@mkdir -p $(OUTPUT_DIR)
	$(ASCIIDOCTOR) $(MAIN_DOC) -o $(HTML_OUTPUT)
	@echo "HTML documentation built: $(HTML_OUTPUT)"

# Build PDF
.PHONY: pdf
pdf: $(PDF_OUTPUT)

$(PDF_OUTPUT): $(ALL_DOCS)
	@echo "Building PDF documentation..."
	@mkdir -p $(OUTPUT_DIR)
	$(ASCIIDOCTOR_PDF) $(MAIN_DOC) -o $(PDF_OUTPUT)
	@echo "PDF documentation built: $(PDF_OUTPUT)"

# Build both HTML and PDF
.PHONY: both
both: html pdf

# Clean output directory
.PHONY: clean
clean:
	@echo "Cleaning output directory..."
	rm -rf $(OUTPUT_DIR)/*
	@echo "Output directory cleaned"

# Watch for changes and rebuild HTML
.PHONY: watch
watch:
	@echo "Watching for changes (press Ctrl+C to stop)..."
	@while true; do \
		inotifywait -q -e modify $(DOCS_DIR)/*.adoc; \
		make html; \
	done

# Open HTML in browser
.PHONY: open
open: html
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(HTML_OUTPUT); \
	elif command -v open > /dev/null; then \
		open $(HTML_OUTPUT); \
	else \
		echo "Please open $(HTML_OUTPUT) manually"; \
	fi

# Help
.PHONY: help
help:
	@echo "AsciiDoc Artisan Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make html    - Build HTML documentation (default)"
	@echo "  make pdf     - Build PDF documentation"
	@echo "  make both    - Build both HTML and PDF"
	@echo "  make clean   - Remove all generated files"
	@echo "  make watch   - Watch for changes and rebuild HTML"
	@echo "  make open    - Build HTML and open in browser"
	@echo "  make help    - Show this help message"
