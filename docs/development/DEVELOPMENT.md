# AsciiDoctorArtisan - Development Guide

**For Developers** working on the AsciiDoctorArtisan project

---

## Quick Start

```bash
# Clone and setup
cd ~/AsciiDoctorArtisan
pip install -r requirements.txt

# Install development tools
pip install ruff black pre-commit

# Install pre-commit hooks
pre-commit install

# Run the application
python3 main.py
```

---

## Code Quality Tools

### Linting with Ruff
```bash
# Check code
ruff check *.py

# Auto-fix issues
ruff check *.py --fix

# Configuration: .ruff.toml
```

### Formatting with Black
```bash
# Format all Python files
black *.py

# Check without changing
black --check *.py

# Line length: 120 characters
```

### Pre-commit Hooks
```bash
# Installed automatically on git commit
# Runs: ruff, black, file validation

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

---

## Development Workflow

### 1. Before Making Changes
```bash
# Update to latest
git pull

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Making Changes
```bash
# Write code
# Pre-commit hooks run automatically on commit

# Or run manually
ruff check *.py --fix
black *.py
```

### 3. Committing
```bash
# Stage changes
git add .

# Commit (hooks run automatically)
git commit -m "feat: your feature description"

# Hooks will:
# - Run ruff linting
# - Run black formatting
# - Validate files
# - Block commit if errors found
```

### 4. Pushing
```bash
# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

---

## Code Standards

### Python Version
- **Target**: Python 3.13
- **Minimum**: Python 3.11

### Style Guide
- **Line length**: 120 characters
- **Quotes**: Double quotes
- **Indentation**: 4 spaces
- **Formatter**: Black

### Linting Rules
- All Pyflakes (F) errors must be fixed
- All pycodestyle (E/W) errors must be fixed
- Legacy patterns allowed (see `.ruff.toml`)

---

## Project Structure

```
AsciiDoctorArtisan/
├── main.py                  # Main application (1,078 lines)
├── main.py          # Windows-optimized (2,225 lines)
├── document_converter.py   # Document conversion (304 lines)
├── setup.py                # Installation (158 lines)
├── requirements.txt        # Development dependencies
├── requirements-production.txt  # Production dependencies
├── .ruff.toml             # Linting configuration
├── .pre-commit-config.yaml # Pre-commit hooks
└── docs/                   # Documentation
```

---

## Testing

### Manual Testing
```bash
# Test main application
python3 main.py

# Test Windows version
python3 main.py

# Test optimized version
```

### Feature Testing
- ✅ Create new AsciiDoc file
- ✅ Open existing file
- ✅ Live preview rendering
- ✅ DOCX import/export
- ✅ Git operations (commit, pull, push)
- ✅ Dark/Light theme toggle
- ✅ Font zoom controls

---

## Dependencies

### Core Dependencies
```bash
PySide6>=6.9.0         # Qt GUI framework
asciidoc3              # AsciiDoc processing
pypandoc               # Document conversion
```

### Development Dependencies
```bash
ruff                   # Linting
black                  # Formatting
pre-commit            # Git hooks
```

### External Requirements
- **Pandoc**: For DOCX conversion
- **Git**: For version control features

---

## Common Tasks

### Update Dependencies
```bash
# Check for updates
pip list --outdated

# Update all
pip install --upgrade -r requirements.txt

# Update production requirements
pip freeze > requirements-production.txt
```

### Run Linting
```bash
# Check all files
ruff check *.py

# Fix automatically
ruff check *.py --fix

# Check statistics
ruff check *.py --statistics
```

### Format Code
```bash
# Format all Python files
black *.py

# Check formatting
black --check *.py
```

### Update Pre-commit
```bash
# Update to latest versions
pre-commit autoupdate

# Run all hooks
pre-commit run --all-files
```

---

## Configuration Files

### .ruff.toml
```toml
# Linting configuration
target-version = "py313"
line-length = 120

[lint]
select = ["E", "F", "W", "I"]
ignore = ["E501", "E701", "E702", "E722"]
```

### .pre-commit-config.yaml
```yaml
# Pre-commit hooks
repos:
  - ruff (linting)
  - black (formatting)
  - general file validation
```

---

## Troubleshooting

### Pre-commit Not Running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Test
pre-commit run --all-files
```

### Linting Errors
```bash
# Auto-fix safe issues
ruff check *.py --fix

# See detailed errors
ruff check *.py --verbose
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify installation
python3 -c "import PySide6, asciidoc3, pypandoc; print('OK')"
```

### Git Commit Blocked
```bash
# Fix linting issues first
ruff check *.py --fix
black *.py

# Then commit
git commit

# Or skip hooks (not recommended)
git commit --no-verify
```

---

## Release Process

### 1. Update Version
```bash
# Update version in setup.py
# Update CHANGELOG.md
```

### 2. Run All Checks
```bash
# Linting
ruff check *.py

# Formatting
black --check *.py

# Pre-commit
pre-commit run --all-files
```

### 3. Test Application
```bash
# Run all versions
python3 main.py
python3 main.py
```

### 4. Create Release
```bash
# Tag version
git tag -a v1.0.0 -m "Release v1.0.0"

# Push to GitHub
git push origin main --tags
```

---

## Contributing

### Code Review Checklist
- [ ] Code follows project style guide
- [ ] All linting checks pass
- [ ] Code formatted with Black
- [ ] Pre-commit hooks pass
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Manual testing completed
- [ ] All linting checks pass
- [ ] Pre-commit hooks pass

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

---

## Resources

### Tools Documentation
- **Ruff**: https://docs.astral.sh/ruff/
- **Black**: https://black.readthedocs.io/
- **Pre-commit**: https://pre-commit.com/

### Project Documentation
- **README.md**: User documentation
- **IMPROVEMENTS.md**: Recent improvements
- **DEPENDENCY_UPDATE_SUMMARY.md**: Dependency changes
- **PROJECT_OVERVIEW.md**: Project statistics

### Python/Qt Resources
- **PySide6 Docs**: https://doc.qt.io/qtforpython/
- **AsciiDoc**: https://asciidoc.org/
- **Python Guide**: https://docs.python.org/3/

---

## Getting Help

### Issues
- Check existing documentation
- Search GitHub issues
- Create new issue with details

### Questions
- Review project documentation
- Check Qt/Python documentation
- Ask in GitHub discussions

---

**Happy coding!** 🚀

All contributions are welcome. Follow the guidelines above for smooth development experience.
