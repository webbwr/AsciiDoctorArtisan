# Task Completion Checklist

## Before Committing Changes

### 1. Run Formatters
```bash
make format
# Or individually:
ruff format src/
isort src/
```

### 2. Run Linters
```bash
make lint
# Or individually:
ruff check src/
mypy src/
```

### 3. Run Tests
```bash
# Fast check (unit tests, no slow)
make test-fast

# Full test suite with coverage
make test

# If touching specific module:
pytest tests/unit/MODULE/ -v
```

### 4. Verify Coverage
- Maintain 95%+ coverage
- No coverage regression on changed code

### 5. Check Type Safety
```bash
mypy src/ --strict
# Should report 0 errors
```

## Code Review Checklist

- [ ] No `shell=True` in subprocess calls
- [ ] Reentrancy guards on handlers (`_is_processing`)
- [ ] UI updates only through signals (not from threads)
- [ ] Atomic file writes (not direct writes)
- [ ] Logic delegated to handlers (not in main_window.py)
- [ ] Max 400 lines per file
- [ ] Type hints on all public functions
- [ ] Tests for new functionality

## Commit Message Format
```
type(scope): brief description

- Detail 1
- Detail 2

🤖 Generated with Claude Code
```

Types: feat, fix, refactor, docs, test, perf, chore

## WSL2 Testing Notes
- Set `ASCIIDOC_ARTISAN_NO_WEBENGINE=1` for tests without GPU
- Some Qt tests may need `QT_QPA_PLATFORM=offscreen`
