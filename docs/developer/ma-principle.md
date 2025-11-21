# MA (間) Principle Guide

**Project:** AsciiDoc Artisan v2.0.8
**Date:** November 21, 2025
**Status:** Active Development Principle
**Audience:** Developers, Contributors, Designers

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is MA (間)?](#what-is-ma-)
3. [MA in Software Development](#ma-in-software-development)
4. [Application Areas](#application-areas)
5. [Code Guidelines](#code-guidelines)
6. [Documentation Guidelines](#documentation-guidelines)
7. [UI/UX Guidelines](#uiux-guidelines)
8. [Verification](#verification)
9. [Examples](#examples)

---

## Introduction

**MA (間)** is a fundamental Japanese aesthetic principle meaning "negative space," "pause," "interval," or "gap." It emphasizes what is NOT there as much as what IS there. In software development, MA translates to intentional simplicity, purposeful emptiness, and the art of omission.

### Core Philosophy

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

MA principles applied to AsciiDoc Artisan:
- **Less is more** - Remove unnecessary complexity
- **Intentional gaps** - Use whitespace purposefully
- **Minimal sufficiency** - Implement only what's needed
- **Graceful silence** - Don't over-communicate
- **Focused simplicity** - One purpose, done well

---

## What is MA (間)?

### Traditional Definition

In Japanese aesthetics, **MA (間)** represents:
- **Spatial**: Physical gaps between objects
- **Temporal**: Pauses in time or rhythm
- **Relational**: Space between people or concepts
- **Philosophical**: The void that gives meaning to substance

### Core Concepts

1. **Negative Space** - The emptiness that defines form
2. **Purposeful Pause** - Strategic silence in communication
3. **Minimalism** - Intentional reduction to essentials
4. **Balance** - Harmony between presence and absence
5. **Mindfulness** - Conscious choice of what to include/exclude

### Related Japanese Concepts

**MA (間)** works with other principles:
- **Wabi-Sabi (侘寂)** - Beauty in imperfection and impermanence
- **Kanso (簡素)** - Simplicity and elimination of clutter
- **Seijaku (静寂)** - Tranquility and active calm
- **Shibumi (渋み)** - Subtle, unobtrusive beauty

---

## MA in Software Development

### Translation to Code

| Japanese Concept | Software Application |
|-----------------|---------------------|
| **Negative space** | Whitespace in code, UI breathing room |
| **Purposeful pause** | Debouncing, rate limiting, loading states |
| **Minimalism** | Single Responsibility Principle, YAGNI |
| **Balance** | Signal-to-noise ratio in logs/output |
| **Mindfulness** | Intentional API design, conscious abstractions |

### The Three Levels of MA

#### 1. MA in Code Structure (Physical)
- Line breaks between logical sections
- Module boundaries and separation
- Function length and complexity limits
- Minimal parameter lists

#### 2. MA in Execution (Temporal)
- Debouncing and throttling
- Strategic delays for UX
- Asynchronous gaps
- Loading and transition states

#### 3. MA in Information (Conceptual)
- What NOT to log
- What NOT to display
- What NOT to implement
- What NOT to document

---

## Application Areas

### 1. Code Quality

**Apply MA through:**
- **YAGNI** (You Aren't Gonna Need It) - Don't build features speculatively
- **KISS** (Keep It Simple, Stupid) - Simplest solution that works
- **Single Responsibility** - Each component does ONE thing
- **Minimal APIs** - Expose only what's necessary
- **No Dead Code** - Remove unused imports, functions, classes

**Metrics:**
- Function length: <50 lines (prefer <25)
- Class length: <300 lines (prefer <200)
- Parameters: ≤4 per function
- Cyclomatic complexity: ≤10
- Nesting depth: ≤3 levels

### 2. Documentation

**Apply MA through:**
- **Concise writing** - Every word earns its place
- **No redundancy** - Say it once, say it well
- **Strategic whitespace** - Visual breathing room
- **Focus on "why"** - Code shows "how," docs explain "why"
- **No obvious comments** - `x = x + 1  # increment x` ❌

**Metrics:**
- Comments-to-code ratio: 5-15% (not more!)
- Documentation coverage: Public APIs only
- Line length: ≤88 characters
- Paragraph length: ≤5 sentences
- Section length: ≤2 screens

### 3. User Interface

**Apply MA through:**
- **Whitespace** - Don't fear empty space
- **Focused interactions** - One action per screen
- **Minimal chrome** - Remove decorative elements
- **Strategic color** - Use sparingly for emphasis
- **Quiet defaults** - Calm, unobtrusive design

**Metrics:**
- Interactive elements per screen: ≤7
- Color palette: 3-5 colors max
- Font families: 1-2 max
- Icon complexity: Simple, recognizable
- Animation duration: <300ms

### 4. User Experience

**Apply MA through:**
- **Loading states** - Purposeful pauses during transitions
- **Debouncing** - Reduce noise from rapid inputs
- **Progressive disclosure** - Show info when needed
- **Graceful degradation** - Fail quietly when appropriate
- **Subtle feedback** - Don't interrupt flow

**Metrics:**
- Debounce delay: 300-500ms for text input
- Toast duration: 3-5 seconds
- Modal frequency: Minimize interruptions
- Auto-save: Silent, in background
- Notifications: Opt-in, non-intrusive

---

## Code Guidelines

### 1. Whitespace and Formatting

**DO:**
```python
# ✅ Good MA - Breathing room between logical sections
def process_document(content: str) -> str:
    """Process document content."""
    # Validate input
    if not content:
        return ""

    # Parse content
    blocks = parse_blocks(content)

    # Transform blocks
    transformed = [transform(block) for block in blocks]

    # Return result
    return join_blocks(transformed)
```

**DON'T:**
```python
# ❌ Bad MA - Cramped, no breathing room
def process_document(content: str) -> str:
    """Process document content."""
    if not content:
        return ""
    blocks = parse_blocks(content)
    transformed = [transform(block) for block in blocks]
    return join_blocks(transformed)
```

### 2. Function Complexity

**DO:**
```python
# ✅ Good MA - Simple, focused functions
def validate_path(path: str) -> bool:
    """Check if path is valid."""
    return path and Path(path).exists()


def sanitize_path(path: str) -> str:
    """Remove dangerous path components."""
    return Path(path).resolve().as_posix()


def load_file(path: str) -> str:
    """Load file content safely."""
    if not validate_path(path):
        raise ValueError(f"Invalid path: {path}")

    safe_path = sanitize_path(path)
    return Path(safe_path).read_text()
```

**DON'T:**
```python
# ❌ Bad MA - Over-complex, doing too much
def load_file(path: str, encoding: str = 'utf-8',
              validate: bool = True, sanitize: bool = True,
              fallback: str = None, create_if_missing: bool = False,
              backup: bool = False, log: bool = True) -> str:
    """Load file with 8 different options."""
    # ... 50 lines of complex logic ...
```

### 3. API Design

**DO:**
```python
# ✅ Good MA - Minimal, focused API
class TemplateEngine:
    """Simple template engine."""

    def render(self, template: str, variables: dict) -> str:
        """Render template with variables."""
        ...

    def load(self, path: str) -> str:
        """Load template from file."""
        ...
```

**DON'T:**
```python
# ❌ Bad MA - Bloated API with too many options
class TemplateEngine:
    """Over-engineered template engine."""

    def render(self, template, variables, encoding, cache,
               strict, filters, globals, autoescape, ...): ...
    def render_string(self, ...): ...
    def render_file(self, ...): ...
    def render_with_cache(self, ...): ...
    def render_async(self, ...): ...
    def render_batch(self, ...): ...
    # ... 20 more methods ...
```

### 4. Error Messages

**DO:**
```python
# ✅ Good MA - Clear, concise, actionable
raise ValueError("File not found: document.adoc")
raise TypeError("Expected string, got int")
```

**DON'T:**
```python
# ❌ Bad MA - Verbose, redundant, obvious
raise ValueError(
    "An error occurred while trying to process your request. "
    "The system was unable to locate the specified file that "
    "you requested to open. The file path provided was "
    "document.adoc and this file does not exist in the "
    "filesystem at the current time. Please check that the "
    "file exists and try again."
)
```

### 5. Logging

**DO:**
```python
# ✅ Good MA - Strategic, meaningful logs
logger.debug("Cache hit: block_123")
logger.warning("GPU not available, using CPU fallback")
logger.error("Failed to save file: permission denied")
```

**DON'T:**
```python
# ❌ Bad MA - Excessive noise
logger.debug("Entering function render_preview")
logger.debug("Checking if content is not None")
logger.debug("Content is not None, proceeding")
logger.debug("Creating preview worker")
logger.debug("Preview worker created successfully")
logger.debug("Emitting signal to preview worker")
# ... 50 more debug logs for a single operation ...
```

---

## Documentation Guidelines

### 1. Comment Necessity

**DO:**
```python
# ✅ Good MA - Comments explain "why," not "what"

# Use temp file + rename for atomic writes (prevents corruption)
temp_path = path + ".tmp"
write_file(temp_path, content)
os.replace(temp_path, path)

# 24-hour cache to avoid 100ms GPU detection overhead
@lru_cache(maxsize=1)
def detect_gpu_cached() -> GPUInfo:
    return detect_gpu_immediate()
```

**DON'T:**
```python
# ❌ Bad MA - Obvious comments that add no value

# Create a temporary path by adding .tmp to the path
temp_path = path + ".tmp"

# Write the content to the temporary file
write_file(temp_path, content)

# Replace the original file with the temporary file
os.replace(temp_path, path)

# Return True to indicate success
return True
```

### 2. Docstring Brevity

**DO:**
```python
# ✅ Good MA - Concise, focused docstrings
def sanitize_path(path: str) -> str:
    """Remove dangerous path components (../, etc.)."""
    ...

def atomic_save(path: str, content: str) -> None:
    """Save file atomically via temp-file-then-rename."""
    ...
```

**DON'T:**
```python
# ❌ Bad MA - Verbose docstrings repeating obvious info
def sanitize_path(path: str) -> str:
    """Sanitize a file path by removing dangerous components.

    This function takes a file path as input and processes it
    to remove any dangerous path components such as parent
    directory references (../) that could be used for directory
    traversal attacks. The function returns the sanitized path
    as a string.

    Args:
        path: The file path to sanitize. This should be a string
              containing the path to a file or directory that needs
              to be sanitized for security purposes.

    Returns:
        A sanitized version of the input path with dangerous
        components removed, returned as a string type.

    Example:
        >>> path = "../etc/passwd"
        >>> sanitized = sanitize_path(path)
        >>> print(sanitized)
        etc/passwd
    """
    ...
```

### 3. README Structure

**DO:**
```markdown
# ✅ Good MA - Scannable, focused sections

# AsciiDoc Artisan

Fast AsciiDoc editor with live preview.

## Install

```bash
pip install asciidoc-artisan
```

## Usage

```bash
asciidoc-artisan document.adoc
```

See [User Guide](docs/guide.md) for details.
```

**DON'T:**
```markdown
# ❌ Bad MA - Wall of text, poor structure

# Welcome to AsciiDoc Artisan - The Ultimate AsciiDoc Editor

AsciiDoc Artisan is a comprehensive, feature-rich, cross-platform
desktop application for editing AsciiDoc documents with real-time
preview capabilities, built using PySide6/Qt framework...
[continues for 500 lines without headers or structure]
```

---

## UI/UX Guidelines

### 1. Visual Hierarchy

**DO:**
```
✅ Good MA - Clear hierarchy with whitespace

┌─────────────────────────────────────┐
│  Editor                             │
│                                     │
│  = Heading                          │
│                                     │
│  Content here...                    │
│                                     │
└─────────────────────────────────────┘

Status: Ready      Branch: main
```

**DON'T:**
```
❌ Bad MA - Cramped, cluttered

┌──────────────────────────┐
│Editor                    │
│=Heading                  │
│Content here...           │
│Status:Ready Branch:main  │
│Files:3 Lines:42 Words:89 │
│CPU:12% Mem:245MB GPU:OK  │
└──────────────────────────┘
```

### 2. Interaction Feedback

**DO:**
```python
# ✅ Good MA - Subtle, unobtrusive feedback
def save_file(self, path: str):
    """Save with minimal feedback."""
    atomic_save(path, content)
    self.status_bar.show_message("Saved", 2000)  # 2s, then disappears
```

**DON'T:**
```python
# ❌ Bad MA - Excessive, intrusive feedback
def save_file(self, path: str):
    """Save with excessive feedback."""
    dialog = QMessageBox()
    dialog.setWindowTitle("Saving File")
    dialog.setText("The file is being saved...")
    dialog.show()

    atomic_save(path, content)

    dialog.close()
    success_dialog = QMessageBox()
    success_dialog.setWindowTitle("Success!")
    success_dialog.setText(
        "The file has been saved successfully!\n\n"
        f"File: {path}\n"
        f"Size: {len(content)} bytes\n"
        f"Time: {datetime.now()}\n\n"
        "Click OK to continue."
    )
    success_dialog.exec()
```

### 3. Default States

**DO:**
```python
# ✅ Good MA - Calm, minimal defaults
settings = {
    'theme': 'light',
    'auto_save': True,
    'notifications': False,  # Opt-in
    'telemetry': False,      # Opt-in
    'animations': True,
}
```

**DON'T:**
```python
# ❌ Bad MA - Noisy, overwhelming defaults
settings = {
    'show_tips_on_startup': True,
    'show_changelog_on_update': True,
    'enable_animations': True,
    'enable_sounds': True,
    'enable_notifications': True,
    'enable_telemetry': True,
    'show_status_bar_stats': True,
    'show_toolbar_labels': True,
    'show_welcome_screen': True,
}
```

---

## Verification

### Automated Checks

**MA Linting Rules:**
```yaml
# .ma-lint.yaml
code:
  max_function_length: 50
  max_class_length: 300
  max_parameters: 4
  max_nesting: 3
  max_complexity: 10

documentation:
  max_comment_ratio: 0.15
  min_whitespace_ratio: 0.02
  max_line_length: 88

ui:
  max_colors: 5
  max_fonts: 2
  max_interactive_elements: 7
```

### Manual Review Questions

**Code Review Checklist:**
- [ ] Can I remove any code without losing functionality?
- [ ] Are all comments necessary (explaining "why," not "what")?
- [ ] Is there appropriate whitespace between logical sections?
- [ ] Are functions focused on a single responsibility?
- [ ] Can the API be simplified further?
- [ ] Are error messages concise and actionable?
- [ ] Is logging strategic (not excessive)?

**Documentation Review Checklist:**
- [ ] Can I remove any words without losing meaning?
- [ ] Is there visual breathing room (whitespace)?
- [ ] Are examples minimal but complete?
- [ ] Does each section have a clear purpose?
- [ ] Are headers and structure clear?

**UI Review Checklist:**
- [ ] Can I remove any UI elements without losing functionality?
- [ ] Is there sufficient whitespace?
- [ ] Are interactions focused and unobtrusive?
- [ ] Do defaults favor calm over busy?
- [ ] Are colors used sparingly and purposefully?

---

## Examples

### Before/After: File Operations

**BEFORE (No MA):**
```python
def save_file_with_all_bells_and_whistles(
    self, path, content, encoding='utf-8', backup=True,
    compress=False, encrypt=False, validate=True,
    notify=True, log=True, atomic=True, fsync=True
):
    """Save file with many options."""
    logger.info(f"Starting file save operation for {path}")
    logger.debug(f"Parameters: encoding={encoding}, backup={backup}, ...")

    if validate:
        logger.debug("Validating content...")
        if not self.validate_content(content):
            logger.error("Content validation failed!")
            QMessageBox.critical(self, "Error", "Invalid content!")
            return False

    if backup:
        logger.debug("Creating backup...")
        backup_path = path + ".backup"
        shutil.copy(path, backup_path)
        logger.info(f"Backup created at {backup_path}")

    # ... 50 more lines ...

    if notify:
        QMessageBox.information(
            self, "Success",
            f"File saved successfully!\n\nPath: {path}\n"
            f"Size: {len(content)} bytes\nEncoding: {encoding}"
        )

    logger.info("File save operation completed successfully")
    return True
```

**AFTER (With MA):**
```python
def save_file(self, path: str, content: str) -> None:
    """Save file atomically."""
    atomic_save_text(path, content)
    self.status_bar.show_message("Saved", 2000)
```

### Before/After: Error Handling

**BEFORE (No MA):**
```python
try:
    result = parse_document(content)
except ParseError as e:
    logger.error(f"ParseError occurred: {e}")
    logger.error(f"Error type: {type(e)}")
    logger.error(f"Error args: {e.args}")
    logger.error(f"Content length: {len(content)}")
    logger.error(f"Stack trace: {traceback.format_exc()}")

    QMessageBox.critical(
        self, "Parse Error",
        f"An error occurred while parsing the document.\n\n"
        f"Error details:\n{str(e)}\n\n"
        f"The system was unable to parse the document content. "
        f"This may be due to invalid AsciiDoc syntax or "
        f"unsupported features. Please review your document "
        f"and try again.\n\n"
        f"If this problem persists, please contact support."
    )
    return None
```

**AFTER (With MA):**
```python
try:
    result = parse_document(content)
except ParseError as e:
    logger.warning(f"Parse failed: {e}")
    self.status_bar.show_message(f"Parse error: {e}", 5000)
    return None
```

### Before/After: Documentation

**BEFORE (No MA):**
```markdown
# Getting Started with AsciiDoc Artisan

Welcome to AsciiDoc Artisan! This comprehensive guide will walk you
through the process of getting started with using AsciiDoc Artisan
for all your AsciiDoc editing needs. AsciiDoc Artisan is a powerful
and feature-rich text editor specifically designed for editing
AsciiDoc documents with a real-time preview feature that allows you
to see your changes immediately as you type.

## Installation Instructions

To install AsciiDoc Artisan on your computer, you will need to
follow these step-by-step instructions. First, you need to make
sure that you have Python installed on your system. Python is a
programming language that is required to run AsciiDoc Artisan.
You can check if Python is installed by opening a terminal window
and typing the command "python --version" without the quotes...
[continues for 50 paragraphs]
```

**AFTER (With MA):**
```markdown
# Quick Start

Install:
```bash
pip install asciidoc-artisan
```

Run:
```bash
asciidoc-artisan document.adoc
```

See [User Guide](guide.md) for details.
```

---

## Integration with Existing Principles

MA complements existing development principles:

### With SOLID Principles
- **Single Responsibility** ← MA: One focused purpose
- **Open/Closed** ← MA: Extend, don't modify (less change)
- **Liskov Substitution** ← MA: Simpler interfaces
- **Interface Segregation** ← MA: Minimal APIs
- **Dependency Inversion** ← MA: Loose coupling

### With Python Zen
- "Simple is better than complex" ← MA: Simplicity
- "Sparse is better than dense" ← MA: Whitespace
- "Readability counts" ← MA: Visual breathing room
- "Special cases aren't special enough" ← MA: No exceptions

### With YAGNI/KISS
- **YAGNI** ← MA: Only build what's needed
- **KISS** ← MA: Simplest solution
- **DRY** ← MA: No redundancy

---

## Adoption Strategy

### Phase 1: Awareness (Weeks 1-2)
- [ ] Read and understand this document
- [ ] Share with team
- [ ] Discuss interpretations and questions
- [ ] Identify obvious violations

### Phase 2: New Code (Weeks 3-4)
- [ ] Apply MA to all new code
- [ ] Review PRs for MA compliance
- [ ] Add MA checks to pre-commit hooks
- [ ] Document MA decisions

### Phase 3: Refactoring (Ongoing)
- [ ] Identify high-impact violations
- [ ] Refactor incrementally
- [ ] Measure improvements
- [ ] Celebrate simplifications

---

## Success Metrics

### Quantitative
- **Code**: LOC decreased by 10-20%
- **Functions**: Average length <30 lines
- **Complexity**: Average cyclomatic complexity <5
- **Comments**: Ratio 5-15% (not higher!)
- **Test time**: Reduced by 15-25%

### Qualitative
- **Readability**: Code reviews take less time
- **Maintainability**: Bugs easier to find/fix
- **Onboarding**: New contributors productive faster
- **Joy**: Developers enjoy working in codebase
- **Calm**: Users feel uninterrupted, focused

---

## Resources

### Books
- "The Art of UNIX Programming" - Eric S. Raymond
- "Zen and the Art of Motorcycle Maintenance" - Robert M. Pirsig
- "In Praise of Shadows" - Jun'ichirō Tanizaki

### Articles
- "Ma: Negative Space in Japanese Design"
- "The Power of Less" - Leo Babauta
- "Minimalism in Software Design"

### Examples
- **Go language** - Minimalist by design
- **Unix philosophy** - Do one thing well
- **Apple UI** - Purposeful negative space

---

## Conclusion

**MA (間)** is not about doing less work—it's about doing the RIGHT work. Every line of code, every comment, every UI element should earn its place. When in doubt, leave it out.

> "The ability to simplify means to eliminate the unnecessary so that the necessary may speak."
> — Hans Hofmann

**Practice MA:**
- Before adding, ask: "Is this necessary?"
- Before writing, ask: "Can I say less?"
- Before showing, ask: "Does this serve the user?"

**Remember:**
- Code is read more than written
- Silence speaks volumes
- Less is often more

---

**Version:** 1.0
**Last Updated:** Nov 21, 2025
**Maintained By:** Development Team
**Review Schedule:** Quarterly

**Related Documents:**
- [Architecture Guide](architecture.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Code Style Guide](code-style.md)
