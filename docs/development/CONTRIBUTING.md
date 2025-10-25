# Contributing to AsciiDoc Artisan

Thank you for your interest in contributing to AsciiDoc Artisan! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing opinions and experiences

## How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - OS and Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Submitting Code

#### Development Setup

```bash
# Clone the repository
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest
```

#### Code Style Guidelines

1. **Follow PEP 8** with these specifications:
   - Line length: 88 characters (Black default)
   - Use double quotes for strings
   - Use trailing commas in multi-line structures

2. **Type Hints Required**:
   ```python
   def process_file(path: Path, encoding: str = "utf-8") -> Optional[str]:
       """Process file and return content."""
   ```

3. **Comprehensive Documentation**:
   - Every public function needs a docstring
   - Include parameter descriptions and return values
   - Add usage examples for complex functions

4. **Error Handling**:
   ```python
   try:
       result = risky_operation()
   except SpecificException as e:
       logger.error(f"Operation failed: {e}")
       # Always provide user-friendly error messages
       raise UserFriendlyException("What went wrong and how to fix it") from e
   ```

#### Testing Requirements

1. **Write tests for all new features**
2. **Maintain 80%+ code coverage**
3. **Test structure**:
   ```
   tests/
   ├── unit/           # Fast, isolated tests
   ├── integration/    # Component interaction tests
   └── e2e/           # End-to-end UI tests
   ```

4. **Test naming convention**:
   ```python
   def test_should_handle_empty_file_gracefully():
       # Given
       empty_file = create_temp_file("")

       # When
       result = process_file(empty_file)

       # Then
       assert result is None
   ```

#### Pull Request Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make focused commits**:
   - One logical change per commit
   - Clear, descriptive commit messages:
     ```
     Add syntax highlighting for AsciiDoc

     - Implement lexer for AsciiDoc syntax
     - Add theme support for light/dark modes
     - Include tests for edge cases
     ```

3. **Before submitting**:
   ```bash
   # Format code
   black .
   ruff check --fix .

   # Type check
   mypy .

   # Run tests
   pytest --cov

   # Update documentation if needed
   ```

4. **PR Description Template**:
   ```markdown
   ## Summary
   Brief description of changes

   ## Motivation
   Why these changes are needed

   ## Changes Made
   - Change 1
   - Change 2

   ## Testing
   How you tested the changes

   ## Screenshots (if UI changes)
   Before/After screenshots

   ## Checklist
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] Changelog entry added
   - [ ] No security vulnerabilities introduced
   ```

### Documentation Contributions

1. **User Documentation**: Help improve tutorials and guides
2. **Code Documentation**: Improve docstrings and comments
3. **API Documentation**: Keep API docs up-to-date
4. **Translations**: Help translate the application

### Security Vulnerabilities

**DO NOT** open public issues for security vulnerabilities. Instead:
1. Email security@asciidoc-artisan.org
2. Include detailed description and proof of concept
3. Allow 90 days for fix before public disclosure

## Development Philosophy

### Guiding Principles

1. **User First**: Every change should improve user experience
2. **Performance Matters**: Profile before optimizing
3. **Secure by Default**: Validate all inputs, sanitize all outputs
4. **Accessible**: Support screen readers and keyboard navigation
5. **Cross-Platform**: Test on Windows, macOS, and Linux

### Architecture Decisions

- **State Management**: Use enums for type-safe states
- **Threading**: Keep UI responsive with worker threads
- **Error Handling**: Never fail silently
- **Logging**: Log errors, not user data

## Review Process

### What Reviewers Look For

1. **Correctness**: Does it work as intended?
2. **Security**: Any vulnerabilities introduced?
3. **Performance**: No regressions?
4. **Maintainability**: Clear and well-documented?
5. **Tests**: Adequate coverage?

### Review Timeline

- Initial review: Within 3 days
- Follow-up reviews: Within 1 day
- Merge decision: Within 7 days total

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website
- Annual contributor spotlight

## Questions?

- **Discord**: [Join our community](https://discord.gg/asciidoc-artisan)
- **Forum**: [discussions.asciidoc-artisan.org](https://discussions.asciidoc-artisan.org)
- **Email**: dev@asciidoc-artisan.org

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make AsciiDoc Artisan better! 🚀