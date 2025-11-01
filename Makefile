# AsciiDoc Artisan Makefile
# Unified build system for Python app and AsciiDoc templates

# Python application variables
PYTHON = python3
SRC_DIR = src
TESTS_DIR = tests

# AsciiDoc template variables
TEMPLATE_DIR = templates/default
TEMPLATE_DOCS = $(TEMPLATE_DIR)/docs
TEMPLATE_OUTPUT = $(TEMPLATE_DIR)/output
ASCIIDOCTOR = asciidoctor
ASCIIDOCTOR_PDF = asciidoctor-pdf

.PHONY: help install install-dev test lint format clean build run mutate mutate-report

# Default target
help:
	@echo "AsciiDoc Artisan Build System"
	@echo ""
	@echo "Python Application Commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package"
	@echo "  make run          - Run the application"
	@echo "  make mutate       - Run mutation testing (slow)"
	@echo "  make mutate-report - Show mutation testing report"
	@echo ""
	@echo "AsciiDoc Template Commands:"
	@echo "  make template-html    - Build template HTML documentation"
	@echo "  make template-pdf     - Build template PDF documentation"
	@echo "  make template-clean   - Clean template output"
	@echo ""
	@echo "  make help             - Show this help message"

# Python Application Targets
install:
	pip install -r requirements-production.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest $(TESTS_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

lint:
	ruff check $(SRC_DIR)
	black --check $(SRC_DIR)
	isort --check-only $(SRC_DIR)
	mypy $(SRC_DIR) || true

format:
	black $(SRC_DIR)
	isort $(SRC_DIR)
	ruff check --fix $(SRC_DIR)

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

run:
	$(PYTHON) $(SRC_DIR)/main.py

# Mutation Testing (Phase 5 QA)
mutate:
	@echo "Running mutation testing (this may take a while)..."
	mutmut run --paths-to-mutate=$(SRC_DIR)/asciidoc_artisan/core/,$(SRC_DIR)/asciidoc_artisan/workers/

mutate-report:
	@echo "Mutation Testing Results:"
	mutmut results
	@echo ""
	@echo "For detailed report, run: mutmut html"

# AsciiDoc Template Targets
.PHONY: template-html template-pdf template-clean

template-html:
	@echo "Building template HTML documentation..."
	@mkdir -p $(TEMPLATE_OUTPUT)
	$(ASCIIDOCTOR) $(TEMPLATE_DOCS)/index.adoc -o $(TEMPLATE_OUTPUT)/index.html
	@echo "Template HTML built: $(TEMPLATE_OUTPUT)/index.html"

template-pdf:
	@echo "Building template PDF documentation..."
	@mkdir -p $(TEMPLATE_OUTPUT)
	$(ASCIIDOCTOR_PDF) $(TEMPLATE_DOCS)/index.adoc -o $(TEMPLATE_OUTPUT)/index.pdf
	@echo "Template PDF built: $(TEMPLATE_OUTPUT)/index.pdf"

template-clean:
	@echo "Cleaning template output..."
	rm -rf $(TEMPLATE_OUTPUT)/*
	@echo "Template output cleaned"
