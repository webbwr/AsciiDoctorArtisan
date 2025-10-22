<!--
Sync Impact Report:
Version change: None → 1.0.0 (Initial ratification)
Modified principles: N/A (Initial creation)
Added sections: All sections (initial creation)
Removed sections: N/A
Templates requiring updates:
  ✅ Updated: constitution.md (this file)
  ✅ Updated: Created from template
Follow-up TODOs: None
-->

# AsciiDoc Artisan Constitution

## Core Principles

### I. Cross-Platform Excellence
**MUST** support Linux, macOS, and Windows with WSL compatibility as first-class citizens. All features **MUST** function identically across platforms without platform-specific degradation. GUI components **MUST** render correctly on all supported platforms with proper scaling for high-DPI displays. File operations **MUST** handle platform-specific path separators and line endings transparently.

**Rationale**: Desktop applications serve diverse user environments. Platform lock-in or degraded experiences on any platform violate user trust and limit adoption. Cross-platform consistency ensures feature parity and reduces maintenance burden.

### II. User Experience First
Interface design **MUST** prioritize clarity, responsiveness, and intuitiveness over feature density. Live preview **MUST** update within 350ms of user input. All file operations **MUST** provide immediate visual feedback. Dark/light theme support is **MANDATORY** with proper contrast ratios meeting WCAG AA standards. Keyboard shortcuts **MUST** follow platform conventions (Ctrl/Cmd awareness).

**Rationale**: A powerful feature set means nothing if users cannot access it efficiently. Response time impacts user flow and productivity. Accessibility features enable broader adoption and demonstrate professional quality.

### III. Data Integrity & Safety (NON-NEGOTIABLE)
All file operations **MUST** use atomic writes to prevent data corruption. Session state **MUST** persist automatically with last-opened file, window geometry, and user preferences. Auto-save **MUST** be configurable with sane defaults. Git integration **MUST** never force-push or execute destructive operations without explicit user confirmation. Path sanitization **MUST** prevent directory traversal attacks.

**Rationale**: User data is sacred. Data loss or corruption destroys trust instantly and irreparably. Security vulnerabilities expose users to exploitation. Every design decision must protect user work.

### IV. Performance & Optimization
Preview rendering **MUST** be debounced and asynchronous to prevent UI blocking. Large documents (>10,000 lines) **MUST** remain responsive. Memory usage **MUST** be monitored and optimized to prevent leaks. Worker threads **MUST** handle CPU-intensive operations (Git, Pandoc) without freezing the main UI. Startup time **MUST NOT** exceed 3 seconds on standard hardware.

**Rationale**: Performance directly impacts user satisfaction and workflow efficiency. Unresponsive applications frustrate users and reduce productivity. Resource efficiency enables deployment on varied hardware configurations.

### V. Format Interoperability
Document conversion **MUST** preserve semantic structure and formatting fidelity. Import/export **MUST** support AsciiDoc, Markdown, HTML, DOCX, LaTeX, reStructuredText with graceful degradation for unsupported features. Pandoc integration **MUST** handle errors gracefully with clear user feedback. Clipboard operations **MUST** support multiple formats with automatic detection.

**Rationale**: Users operate in heterogeneous document ecosystems. Lock-in to single formats reduces utility. Seamless conversion enables broader workflows and collaboration across tool boundaries.

### VI. Code Quality & Maintainability
All code **MUST** include comprehensive type hints (PEP 484). Documentation **MUST** exist for all public APIs with parameter descriptions, return values, and usage examples. Naming **MUST** be self-documenting and consistent. Error handling **MUST** be comprehensive with informative messages. Logging **MUST** provide actionable diagnostic information without exposing sensitive data.

**Rationale**: Code is read far more than written. Future maintainers (including yourself) depend on clear, well-documented code. Type safety catches errors at development time. Proper error handling and logging accelerate debugging and reduce support burden.

### VII. Testing & Verification
All features **MUST** have corresponding test coverage focusing on user-facing functionality. Syntax validation **MUST** pass before commits. Dependencies **MUST** be verified on startup with clear error messages for missing components. Platform-specific behavior **MUST** be tested on target platforms. Breaking changes **MUST** be detected through contract tests.

**Rationale**: Untested code is broken code waiting to manifest. Test coverage provides confidence for refactoring and feature additions. Early validation catches issues before they reach users.

## Development Workflow

### Code Organization
- **Single-Responsibility Principle**: Classes and functions **MUST** have one clear purpose
- **Separation of Concerns**: UI, business logic, and data access **MUST** be separated
- **Dependency Injection**: Hard dependencies **MUST** be minimized and injected where possible
- **Configuration Management**: Settings **MUST** use platform-appropriate directories (XDG on Linux, AppData on Windows)

### Review & Quality Gates
- All changes **MUST** pass linting (Ruff) with no warnings
- All changes **MUST** pass type checking (mypy) with strict mode
- Breaking changes **MUST** be documented in CHANGELOG.md
- User-facing changes **MUST** update relevant documentation
- Security vulnerabilities **MUST** be addressed before other work

### Git Practices
- Commit messages **MUST** follow Conventional Commits format
- Feature branches **MUST** be rebased onto main before merging
- Commits **MUST** be atomic and represent logical units of work
- History **MUST** remain clean and readable (no merge commits in feature branches)

## Documentation Standards

### User Documentation
- **Quick Start Guide**: Get users productive in <5 minutes
- **Feature Guides**: One guide per major feature with screenshots/examples
- **Troubleshooting**: Platform-specific issues with solutions
- **Keyboard Shortcuts**: Complete reference with platform differences noted

### Technical Documentation
- **Architecture Overview**: System components and their interactions
- **API Documentation**: All public interfaces with examples
- **Development Setup**: Complete steps from clone to running
- **Contributing Guide**: Standards, workflow, and expectations

### Documentation Maintenance
- Documentation **MUST** be updated concurrently with code changes
- Broken links **MUST** be fixed immediately upon detection
- Examples **MUST** be tested and verified to work
- Screenshots **MUST** be updated when UI changes

## Security Requirements

### Input Validation
- All file paths **MUST** be sanitized to prevent directory traversal
- All user input **MUST** be validated before processing
- External process execution (Git, Pandoc) **MUST** use parameterized calls, never shell interpolation
- File type detection **MUST** use safe methods (magic bytes, not extension alone)

### Data Protection
- No credentials or secrets **MUST** be stored in configuration files
- Git operations **MUST** use existing user credentials, never custom storage
- Temporary files **MUST** be created securely and cleaned up reliably
- Error messages **MUST NOT** expose sensitive file paths or user information

### Dependency Management
- Dependencies **MUST** be pinned in requirements-production.txt
- Dependency updates **MUST** be tested before merging
- Security advisories **MUST** be monitored and addressed promptly
- Unused dependencies **MUST** be removed to minimize attack surface

## Governance

### Constitution Authority
This constitution **SUPERSEDES** all other development practices, guidelines, or conventions. When conflicts arise between this constitution and other documentation, the constitution takes precedence. Amendments require:

1. **Justification**: Written rationale for the change
2. **Impact Analysis**: Assessment of affected code and workflows
3. **Migration Plan**: Steps to bring existing code into compliance
4. **Version Bump**: Appropriate semantic version increment
5. **Documentation Update**: All references updated concurrently

### Compliance Review
All pull requests **MUST** verify compliance with constitutional principles. Complexity **MUST** be justified with clear rationale demonstrating value that outweighs maintenance burden. Technical debt **MAY** be accepted only with:
- Explicit documentation of the debt
- Timeline and plan for resolution
- Approval from project maintainer

### Amendment Process
Constitution amendments follow semantic versioning:
- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

All amendments **MUST** include:
- Sync Impact Report documenting affected templates and documents
- Updated version number and last amended date
- Clear reasoning for the change

### Development Guidance
For runtime development guidance during feature implementation, refer to:
- `README.md` - Project overview and quick start
- `docs/DEVELOPMENT.md` - Development environment setup
- `docs/CONTRIBUTING.md` - Contribution workflow and standards
- `docs/PROJECT_OVERVIEW.md` - Architecture and design decisions

**Version**: 1.0.0 | **Ratified**: 2025-10-22 | **Last Amended**: 2025-10-22
