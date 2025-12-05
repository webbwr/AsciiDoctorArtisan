# Contributing Guide

**v2.1.0** | How to contribute to AsciiDoc Artisan

---

## Setup

```bash
git clone https://github.com/YOUR-USERNAME/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
pip install -r requirements.txt -r requirements-dev.txt
```

---

## Workflow

1. Create branch: `git checkout -b feature-name`
2. Make changes (follow MA principle: <400 lines/file)
3. Format: `make format`
4. Lint: `make lint`
5. Test: `make test`
6. Commit: Clear message explaining "why"
7. Push and create PR

---

## Code Style

- **Line length:** 88 max
- **Formatter:** Black + isort
- **Types:** Add hints to all functions
- **Comments:** Explain "why", not "what"

---

## Testing

```bash
make test              # All tests
pytest tests/unit/     # Unit only
make lint              # Lint check
```

All tests must pass before PR merge.

---

## PR Template

```markdown
## What
Brief description

## Why
Reason for change

## Testing
How to verify
```

---

## Structure

```
src/asciidoc_artisan/
├── core/      # Settings, file ops
├── ui/        # Handlers, dialogs
├── workers/   # Background tasks
└── lsp/       # Language server
```

---

*v2.1.0 | Dec 5, 2025*
