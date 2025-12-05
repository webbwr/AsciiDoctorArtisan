# Configuration Guide

**v2.1.0** | Project configuration files

---

## Quick Reference

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies |
| `pytest.ini` | Test runner config |
| `.ruff.toml` | Linter settings |
| `.pre-commit-config.yaml` | Git hooks |
| `.editorconfig` | Editor formatting |
| `Makefile` | Build commands |
| `requirements.txt` | Dev dependencies |
| `requirements-prod.txt` | Production dependencies |

---

## pyproject.toml

Package metadata and build configuration.

**Edit when:** Bumping version, adding dependencies

---

## pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short
```

**Edit when:** Changing test behavior

---

## .ruff.toml

- Line length: 88
- Python: 3.11+
- Rules: F, E, W, I

**Edit when:** Adjusting code style

---

## .pre-commit-config.yaml

**Hooks:**
1. ruff (lint + format)
2. trailing-whitespace
3. end-of-file-fixer
4. check-yaml, check-toml
5. check-added-large-files

```bash
pre-commit install       # Setup
pre-commit run --all     # Manual run
```

---

## .editorconfig

- Indent: 4 spaces
- Line endings: LF
- Charset: UTF-8
- Trim trailing whitespace

---

## Makefile

```bash
make help        # Show commands
make run         # Run app
make test        # Run tests
make lint        # Check code
make format      # Format code
make clean       # Remove artifacts
```

---

## Dependencies

**requirements.txt** — Dev tools (pytest, ruff, mypy)

**requirements-prod.txt** — Runtime (PySide6, asciidoc3, pypandoc)

```bash
pip install -r requirements.txt
pip install -r requirements-prod.txt
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Pre-commit failed | `make format` |
| Import errors | `pip install -e .` |

---

*v2.1.0 | Dec 5, 2025*
