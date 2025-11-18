# AsciiDoc Artisan Makefile
# Unified build system for Python app and AsciiDoc templates

# Python application variables
VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
BLACK = $(VENV)/bin/black
ISORT = $(VENV)/bin/isort
RUFF = $(VENV)/bin/ruff
MYPY = $(VENV)/bin/mypy
SRC_DIR = src
TESTS_DIR = tests

# AsciiDoc template variables
TEMPLATE_DIR = templates/default
TEMPLATE_DOCS = $(TEMPLATE_DIR)/docs
TEMPLATE_OUTPUT = $(TEMPLATE_DIR)/output
ASCIIDOCTOR = asciidoctor
ASCIIDOCTOR_PDF = asciidoctor-pdf

.PHONY: help install install-dev test test-fast test-unit test-integration test-slow lint format clean build run mutate mutate-report

# Default target
help:
	@echo "AsciiDoc Artisan Build System"
	@echo ""
	@echo "Python Application Commands:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make test             - Run all tests with coverage"
	@echo "  make test-fast        - Run fast tests only (unit, no slow)"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-slow        - Run slow tests only"
	@echo "  make test-perf        - Run performance tests with metrics"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make build            - Build package"
	@echo "  make run              - Run the application"
	@echo "  make mutate           - Run mutation testing (slow)"
	@echo "  make mutate-report    - Show mutation testing report"
	@echo ""
	@echo "AsciiDoc Template Commands:"
	@echo "  make template-html    - Build template HTML documentation"
	@echo "  make template-pdf     - Build template PDF documentation"
	@echo "  make template-clean   - Clean template output"
	@echo ""
	@echo "  make help             - Show this help message"

# Python Application Targets
install:
	$(PIP) install -r requirements-production.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	pre-commit install

test:
	$(PYTEST) $(TESTS_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

test-fast:
	@echo "Running fast tests (unit, no slow markers)..."
	$(PYTEST) $(TESTS_DIR)/unit/ -v -m "not slow" --durations=10

test-unit:
	@echo "Running unit tests only..."
	$(PYTEST) $(TESTS_DIR)/unit/ -v --durations=10

test-integration:
	@echo "Running integration tests..."
	$(PYTEST) $(TESTS_DIR)/integration/ -v --durations=10

test-slow:
	@echo "Running slow tests..."
	$(PYTEST) $(TESTS_DIR)/ -v -m "slow" --durations=20

test-perf:
	@echo "Running performance tests with detailed metrics..."
	$(PYTEST) $(TESTS_DIR)/performance/ $(TESTS_DIR)/integration/test_performance*.py -v --durations=20

lint:
	$(RUFF) check $(SRC_DIR)
	$(RUFF) format --check $(SRC_DIR)
	$(ISORT) --check-only $(SRC_DIR)
	$(MYPY) $(SRC_DIR) || true

format:
	$(RUFF) format $(SRC_DIR)
	$(ISORT) $(SRC_DIR)
	$(RUFF) check --fix $(SRC_DIR)

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
	$(PYTHON) -OO $(SRC_DIR)/main.py

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
