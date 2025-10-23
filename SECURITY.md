# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in AsciiDoc Artisan, please report it by:

1. **Do NOT** open a public issue
2. Email the maintainer directly (check GitHub profile for contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- Initial response: Within 48 hours
- Status update: Within 7 days
- Fix timeline: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next release cycle

### What to Expect

- Acknowledgment of your report
- Regular updates on fix progress
- Credit in release notes (if desired)
- Notification when fix is released

## Security Best Practices

When using AsciiDoc Artisan:

1. **Keep Updated**: Always use the latest version
2. **Dependencies**: Regularly update dependencies
3. **File Sources**: Only open AsciiDoc files from trusted sources
4. **Git Operations**: Review git commands before execution
5. **Pandoc**: Ensure Pandoc is from official sources

## Known Security Considerations

### Git Integration
- Git operations execute shell commands
- Only use in trusted repositories
- Review commit messages before pushing

### File Operations
- Files are read/written with user permissions
- Auto-save creates temporary files
- Session state is stored locally

### External Dependencies
- asciidoc3: Processes markup (potential XSS in preview)
- pypandoc: Executes Pandoc (shell command execution)
- PySide6: Qt framework (inherits Qt security model)

## Security Updates

Security updates are released as:
- Patch versions for critical issues
- Announced in CHANGELOG.md
- Tagged with `security` label in releases
