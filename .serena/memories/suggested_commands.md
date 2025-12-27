# Suggested Commands

## Running the Application
```bash
make run                    # Optimized (-OO flag)
python3 src/main.py         # Normal run
venv/bin/python -OO src/main.py  # Direct venv
```

## Testing
```bash
make test                   # All tests + coverage
make test-fast              # Unit tests only (no slow markers)
make test-unit              # Unit tests only
make test-integration       # Integration tests
make test-slow              # Slow tests only
make test-perf              # Performance tests

# Single module
pytest tests/unit/MODULE/ -v

# Single test file (WSL2 - skip WebEngine)
ASCIIDOC_ARTISAN_NO_WEBENGINE=1 pytest tests/path/to/test.py -v

# Run with coverage
pytest tests/ --cov=src/asciidoc_artisan --cov-report=term-missing
```

## Code Quality
```bash
make format                 # Format code (ruff-format, isort)
make lint                   # Run linters (ruff, mypy)

# Individual tools
ruff format src/            # Format
ruff check src/ --fix       # Lint + autofix
isort src/                  # Sort imports
mypy src/                   # Type checking
```

## Build & Clean
```bash
make build                  # Build package
make clean                  # Clean artifacts
```

## Mutation Testing
```bash
make mutate                 # Run mutation testing
make mutate-report          # Show mutation report
```

## System Dependencies
```bash
sudo apt install pandoc wkhtmltopdf gh
```

## Git Operations
```bash
git status -sb              # Short status
git diff --stat             # Diff summary
git add . && git commit -m "message"
```

## WSL2 Notes
- Set `ASCIIDOC_ARTISAN_NO_WEBENGINE=1` to skip Qt WebEngine tests
- Use `QT_QPA_PLATFORM=offscreen` for headless testing
