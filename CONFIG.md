# Configuration Guide

This document explains all configuration files in the AsciiDoc Artisan repository and how to customize them.

---

## Quick Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `pyproject.toml` | Package metadata and build config | Adding dependencies, changing version |
| `pytest.ini` | Test runner configuration | Modifying test behavior |
| `.ruff.toml` | Code linter settings | Adjusting code style rules |
| `.pre-commit-config.yaml` | Git pre-commit hooks | Adding/removing automated checks |
| `.editorconfig` | Editor formatting standards | Changing indentation/line endings |
| `.gitignore` | Git exclusion patterns | Ignoring new file types |
| `.gitattributes` | Git file handling rules | Changing line ending behavior |
| `Makefile` | Build automation commands | Adding new make targets |
| `requirements.txt` | Development dependencies | Adding dev tools |
| `requirements-prod.txt` | Production dependencies | Adding runtime dependencies |

---

## Package Configuration

### `pyproject.toml`
**Purpose:** Python package metadata, build system, and tool configuration.

**Key Sections:**
```toml
[build-system]          # Build backend (setuptools)
[project]               # Package metadata (name, version, authors)
[project.dependencies]  # Runtime dependencies
[project.optional-dependencies]  # Dev dependencies
[tool.setuptools]       # Package discovery settings
```

**When to Edit:**
- Bumping version number
- Adding/removing dependencies
- Changing project metadata
- Configuring package installation

**Related Files:** `setup.py` (legacy support)

---

## Testing Configuration

### `pytest.ini`
**Purpose:** Configure pytest test runner behavior.

**Current Settings:**
```ini
[pytest]
testpaths = tests              # Where to find tests
python_files = test_*.py       # Test file naming pattern
python_classes = Test*         # Test class naming pattern
python_functions = test_*      # Test function naming pattern
addopts = -v --tb=short        # Default options (verbose, short tracebacks)
```

**Common Customizations:**
- Add `--cov=src` for coverage reports
- Add `-n auto` for parallel testing (requires pytest-xdist)
- Add `--maxfail=1` to stop after first failure
- Add markers for test categorization

---

## Code Quality Configuration

### `.ruff.toml`
**Purpose:** Configure Ruff linter and formatter (replaces flake8, black, isort).

**Current Settings:**
- Line length: 88 characters (Black default)
- Python version: 3.11+
- Selected rules: F (pyflakes), E/W (pycodestyle), I (isort)
- Ignored rules: E501 (line too long, handled by formatter)

**When to Edit:**
- Enabling additional ruff rules (UP, B, C90, etc.)
- Adjusting line length
- Excluding files or directories
- Configuring import sorting

**Documentation:** https://docs.astral.sh/ruff/

### `.pre-commit-config.yaml`
**Purpose:** Automated checks before git commits.

**Installed Hooks:**
1. **ruff** - Linting and formatting
2. **trailing-whitespace** - Remove trailing spaces
3. **end-of-file-fixer** - Ensure files end with newline
4. **check-yaml** - Validate YAML syntax
5. **check-toml** - Validate TOML syntax
6. **check-added-large-files** - Prevent committing large files
7. **check-merge-conflict** - Detect merge conflict markers

**Usage:**
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Skip hooks (emergency only)
git commit --no-verify
```

**When to Edit:**
- Adding new pre-commit hooks
- Adjusting hook versions
- Excluding files from specific hooks

---

## Editor Configuration

### `.editorconfig`
**Purpose:** Ensure consistent formatting across editors (VSCode, Vim, etc.).

**Current Standards:**
- Indent: 4 spaces (Python, Makefile exceptions)
- Line endings: LF (Unix)
- Charset: UTF-8
- Trim trailing whitespace: Yes
- Insert final newline: Yes

**Supported Editors:** VSCode, IntelliJ, Vim, Emacs, Sublime Text, and more.

**When to Edit:**
- Changing indentation style
- Adding file-type specific rules

---

## Version Control Configuration

### `.gitignore`
**Purpose:** Exclude files from git tracking.

**Categories:**
- Python artifacts (`__pycache__/`, `*.pyc`, `*.egg-info/`)
- Virtual environments (`venv/`, `env/`)
- IDEs (`.vscode/`, `.idea/`)
- Testing (`htmlcov/`, `.pytest_cache/`)
- Logs and temp files (`*.log`, `*.tmp`)
- Build artifacts (`build/`, `dist/`)

**When to Edit:**
- Adding new file types to ignore
- Excluding directories
- Debugging git tracking issues

### `.gitattributes`
**Purpose:** Configure how git handles files.

**Current Rules:**
- Text files: Auto line ending normalization
- Binary files: No line ending conversion
- Python files: Diff using Python syntax
- Markdown files: Diff using markdown syntax

**When to Edit:**
- Adding new file types
- Changing diff behavior
- Setting merge strategies

---

## Build Automation

### `Makefile`
**Purpose:** Simplify common development tasks.

**Available Targets:**
```bash
make help          # Show all commands
make install-dev   # Install dev environment
make run           # Run the application
make test          # Run tests with coverage
make lint          # Check code quality
make format        # Auto-format code
make clean         # Remove build artifacts
make build         # Build distribution package
```

**When to Edit:**
- Adding new commands
- Changing build process
- Customizing test commands

**Syntax:**
```makefile
target: dependencies
    command
```

---

## Dependency Management

### `requirements.txt`
**Purpose:** Development dependencies (testing, linting, formatting).

**Contains:**
- pytest, pytest-qt, pytest-cov (testing)
- ruff, black, mypy (code quality)
- pre-commit (git hooks)

**Update:**
```bash
pip install -r requirements.txt
pip freeze > requirements.txt  # Freeze versions
```

### `requirements-prod.txt`
**Purpose:** Production dependencies (runtime only).

**Contains:**
- PySide6 (Qt GUI framework)
- asciidoc3 (document processing)
- pypandoc (format conversion)
- pymupdf (PDF handling)

**Update:**
```bash
pip install -r requirements-prod.txt
```

**Best Practice:** Keep production dependencies minimal. Only include what's needed at runtime.

---

## Configuration Hierarchy

### Loading Order
1. `.editorconfig` - Editor picks up on file open
2. `pyproject.toml` - Read by pip/build tools
3. `pytest.ini` - Read by pytest
4. `.ruff.toml` - Read by ruff
5. `.pre-commit-config.yaml` - Read by pre-commit

### Precedence
- Project configs override user configs
- `.git/config` (repository) overrides `~/.gitconfig` (global)
- `pyproject.toml` can override other tool configs

---

## Customization Examples

### Stricter Linting
Edit `.ruff.toml`:
```toml
[tool.ruff]
select = ["F", "E", "W", "I", "N", "UP", "B", "C90"]
```

### Parallel Testing
Edit `pytest.ini`:
```ini
addopts = -v --tb=short -n auto
```

### Custom Make Target
Edit `Makefile`:
```makefile
watch:
    find src -name "*.py" | entr make test
```

---

## Troubleshooting

### "Pre-commit hook failed"
```bash
# Fix automatically
make format

# Or skip (not recommended)
git commit --no-verify
```

### "Import errors in tests"
```bash
# Install package in editable mode
pip install -e .
```

### "Ruff and Black conflict"
Both use 88-character line length by default. Conflicts should not occur.

---

## Related Documentation

- [How to Contribute](docs/developer/how-to-contribute.md) - Contribution workflow
- [Test Coverage Summary](docs/developer/TEST_COVERAGE_SUMMARY.md) - Testing guide
- [Performance Profiling](docs/developer/PERFORMANCE_PROFILING.md) - Benchmarking

---

*Last updated: October 29, 2025*
