# Code Style and Conventions

## Python Version
- Target: Python 3.11+ (testing with 3.13)
- Use modern Python features (type hints, dataclasses, etc.)

## Formatting
- **Line length**: 88 (Black default), 120 allowed for legacy
- **Formatter**: ruff-format (Black-compatible)
- **Import sorting**: isort (Black profile)
- **Quote style**: double quotes

## Type Hints
- **mypy --strict** enforced (0 errors required)
- All public functions must have type hints
- Use `Optional[T]` for nullable types
- Use `list`, `dict`, `set` (not `List`, `Dict`, `Set` from typing)

## Linting (ruff)
Enabled rules:
- E: pycodestyle errors
- F: Pyflakes
- W: pycodestyle warnings
- I: isort
- B: flake8-bugbear
- C4: flake8-comprehensions
- UP: pyupgrade

## Naming Conventions
- **Classes**: PascalCase (`MainWindow`, `PreviewHandler`)
- **Functions/methods**: snake_case (`process_document`, `_internal_helper`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_BUFFER_SIZE`)
- **Private**: prefix with underscore (`_cache`, `_is_processing`)

## Documentation
- Docstrings for public APIs (Google style preferred)
- Module-level docstrings for files
- Inline comments only for non-obvious logic

## File Organization
- **Max 400 lines per file** (MA principle)
- One class per file for large classes
- Group related functionality in modules

## Qt/PySide6 Patterns
- Use signals/slots for cross-thread communication
- Never update UI from worker threads
- Use `QThread` for blocking operations
- Emit signals with data, don't access UI directly

## Error Handling
- Use specific exception types
- Log errors with context
- Reentrancy guards: `if self._is_processing: return`

## Security
- Never use `shell=True` in subprocess
- Use `atomic_save_text()` for file writes
- Sanitize paths before use
- Validate all external input
