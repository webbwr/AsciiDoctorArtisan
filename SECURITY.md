# Security

## Supported Versions

We fix security bugs in these versions:

| Version | Supported |
| ------- | --------- |
| 2.0.x   | ✓ Yes     |
| 1.9.x   | ✓ Yes     |
| 1.8.x   | ✓ Yes     |
| < 1.8   | ✗ No      |

## Report a Bug

If you find a security bug, please help us fix it.

### How to Report

1. **Do not** post it publicly
2. Send us an email instead
3. Tell us these things:
   - What the bug does
   - How to make it happen
   - What could break
   - How to fix it (if you know)

### Our Response Times

We will reply within 2 days. We send updates every week.

Fix times depend on how bad the bug is:
- Critical bugs get fixed in 7 days
- High bugs get fixed in 30 days
- Medium bugs get fixed in 90 days
- Low bugs get fixed in next release

### What We Will Do

- Thank you for the report
- Keep you informed of our progress
- Give you credit if you want it
- Tell you when we release the fix

## Stay Secure

Follow these tips to stay safe.

Use the latest version. Always update to the newest one.

Keep all tools up to date. This keeps you safe.

Only open files you trust. Bad files can cause problems.

Review changes before you commit them. Check what Git will do.

Download tools from official sites only. Get Pandoc from pandoc.org.

## Security Notes

### Git Commands
Git runs on your computer. Only use it with safe files. Review all changes before you save.

### File Operations
The program reads and writes files. Auto-save makes backup files. Your files stay on your computer.

### External Tools
The program uses these tools. All are open source and safe.

- asciidoc3 renders your content
- pypandoc converts file formats
- PySide6 creates the windows

## Recent Security Fixes

**v2.0.5 (November 2025):**
- Code quality improvements and defensive code audit
- Comprehensive security testing (5,481 tests passing)
- All subprocess calls use secure list form (no shell injection)

**v1.7.4 (October 2025):**
- Fixed path traversal bug (Issue #8)
- All file paths now checked for safety
- No more directory escape attacks

See CHANGELOG.md for all security fixes.

## Security Updates

We announce security fixes in three ways. We update the version numbers. We update the CHANGELOG file. We add release notes with a security tag.

---

**Reading Level**: Grade 5.0
**Last Updated**: November 2025
