# Contributing to AsciiDoc Artisan

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- System dependencies: `pandoc`, `wkhtmltopdf`, `gh` (GitHub CLI)

### Installation

```bash
# Clone repository
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install system dependencies (Ubuntu/Debian)
sudo apt install pandoc wkhtmltopdf gh
```

### Running the Application

```bash
make run          # Optimized mode
python3 src/main.py  # Normal mode
```

## Code Standards

### Architecture (MA Principle)

- **Files under 400 lines** - S-tier compliance required
- **Focused functions** - Single responsibility
- **Clean delegation** - Managers delegate to specialized components

### Style Guidelines

```bash
# Format code
make format       # Runs ruff format + isort

# Lint code
make lint         # Runs ruff + mypy --strict

# Run all quality checks
make quality
```

### Type Safety

- All code must pass `mypy --strict`
- Use type hints for function signatures
- Document complex types with docstrings

### Testing

```bash
# Run all tests
make test

# Run specific test module
pytest tests/unit/core/test_settings.py -v

# Run with coverage
pytest --cov=src/asciidoc_artisan --cov-report=term-missing

# Run E2E tests
pytest tests/e2e/ -v
```

**Test Requirements:**
- Unit tests for new functionality
- Integration tests for external tool interactions
- E2E tests for user workflows
- Minimum 95% coverage for new code

### Commit Messages

Format: `type: description`

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/dependency updates

Example:
```
feat: Add template preview in template dialog

- Preview renders template with sample variables
- Updates in real-time as user types
```

## Pull Request Process

1. **Fork** the repository
2. **Create branch** from `main`: `git checkout -b feat/your-feature`
3. **Make changes** following code standards
4. **Run tests**: `make test`
5. **Run quality checks**: `make lint`
6. **Commit** with descriptive message
7. **Push** to your fork
8. **Open PR** against `main` branch

### PR Checklist

- [ ] Code follows MA principle (files < 400 lines)
- [ ] All tests pass (`make test`)
- [ ] Lint passes (`make lint`)
- [ ] Type check passes (`mypy --strict`)
- [ ] New functionality has tests
- [ ] Documentation updated if needed

## Project Structure

```
src/asciidoc_artisan/
├── core/       # Settings, file ops, search, GPU detection
├── ui/         # Main window, managers, dialogs
├── workers/    # QThread workers (git, pandoc, preview)
├── claude/     # Claude AI integration
├── lsp/        # Language Server Protocol
└── templates/  # Built-in document templates

tests/
├── unit/       # Unit tests by module
├── integration/# Integration tests
└── e2e/        # End-to-end tests
```

## Feature Requests

Open an issue with:
- Clear description of the feature
- Use case / motivation
- Proposed implementation (optional)

## Bug Reports

Open an issue with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- System info (OS, Python version, Qt version)

## Security Issues

For security vulnerabilities, please email directly rather than opening a public issue.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

*AsciiDoc Artisan v2.1.0*
