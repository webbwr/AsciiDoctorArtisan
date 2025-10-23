# AsciiDoc Artisan - KISS Specification v2.0

**Status**: PROPOSED (Simplified from v1.0)
**Date**: 2025-10-23
**Principle**: Keep It Simple, Stupid

---

## Vision Statement

**"Edit AsciiDoc files with instant HTML preview."**

That's it. No more, no less.

---

## Core Value Proposition

Enable technical writers to see their AsciiDoc content rendered as HTML while they type, eliminating the need to switch between an editor and a browser.

**What we ARE**:
- A simple text editor
- A live HTML preview
- A tool that saves files safely

**What we are NOT**:
- A Git client (use git CLI)
- A format converter (use pandoc CLI)
- An IDE (use VS Code for that)
- A collaboration tool (use Google Docs)

---

## User Story (Single Story)

```
As a technical writer,
I want to edit AsciiDoc and see the HTML preview instantly,
So I can focus on content without switching tools.

Acceptance Criteria:
1. I can type AsciiDoc in the left pane
2. I see rendered HTML in the right pane automatically
3. Changes appear in preview within 1 second
4. I can save my work with Ctrl+S
5. The application warns me before closing unsaved work
```

---

## Functional Requirements

**Total: 15 Requirements** (down from 53)

### Document Editing (5 requirements)

- **FR-001**: System SHALL provide a plain text editor for AsciiDoc content
- **FR-002**: System SHALL display live HTML preview of the current content
- **FR-003**: System SHALL enable word wrap in the editor by default
- **FR-004**: System SHALL update preview automatically when content changes
- **FR-005**: System SHALL indicate unsaved changes in the window title (asterisk)

### File Operations (5 requirements)

- **FR-006**: System SHALL open .adoc and .asciidoc files
- **FR-007**: System SHALL save files with Ctrl+S keyboard shortcut
- **FR-008**: System SHALL provide "Save As" to save to a new location
- **FR-009**: System SHALL prompt user before closing unsaved documents
- **FR-010**: System SHALL use atomic file writes to prevent corruption

### User Interface (5 requirements)

- **FR-011**: System SHALL provide dark and light theme options
- **FR-012**: System SHALL support keyboard shortcuts: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Q
- **FR-013**: System SHALL display editor and preview side-by-side with resizable splitter
- **FR-014**: System SHALL work identically on Linux, macOS, and Windows
- **FR-015**: System SHALL remember window size, position, and last directory

---

## Non-Functional Requirements

### Performance

- Preview updates: Fast enough (no hard requirement)
- Startup time: Reasonable (no hard requirement)
- Memory usage: Efficient (no hard requirement)

**Rationale**: Measure first, optimize if needed. Premature optimization wastes time.

### Usability

- No tutorial needed for basic usage
- Obvious how to open, edit, and save files
- Keyboard shortcuts follow platform conventions

### Reliability

- No data loss on crashes (atomic writes)
- Clear error messages for file operations
- Graceful handling of invalid AsciiDoc

---

## Technical Architecture

### Simple Stack

```
┌─────────────────────────────────────┐
│     Main Window (QMainWindow)       │
│  ┌─────────────┐ ┌────────────────┐ │
│  │   Editor    │ │    Preview     │ │
│  │QPlainTextEdit│ │ QTextBrowser   │ │
│  └─────────────┘ └────────────────┘ │
└─────────────────────────────────────┘
           ↓
    asciidoc3.render()
    (synchronous, <50ms)
```

**No worker threads. No async. No complexity.**

### Data Model

**Two entities only**:

1. **Document**
   - file_path: Optional[Path]
   - content: str
   - modified: bool

2. **Settings**
   - last_directory: str
   - dark_mode: bool
   - window_geometry: dict

**That's all the state we need.**

### Dependencies

```
# Production
PySide6>=6.9.0      # GUI framework
asciidoc3           # AsciiDoc rendering

# Development
pytest>=7.4.0       # Testing
pytest-qt>=4.2.0    # GUI testing
```

**Total: 4 dependencies** (down from 6+)

---

## Implementation Guidelines

### Code Size Target

- **Total LOC**: <1,000 lines
- **Main file**: <500 lines
- **Settings**: <100 lines
- **Utils**: <200 lines
- **Tests**: <300 lines

### Simplicity Rules

1. **No premature optimization** - Profile before optimizing
2. **No worker threads** - Synchronous is fine for <10,000 line docs
3. **No complex state** - Minimal settings, minimal entities
4. **Use Qt defaults** - Don't reinvent what Qt provides
5. **Delete before adding** - Remove code whenever possible

### Feature Rejection Criteria

**Reject any feature that**:
- Requires >100 LOC to implement
- Adds external dependencies
- Requires threading/async
- Duplicates existing tools (git, pandoc, etc.)
- Benefits <10% of users

---

## Out of Scope (Explicit Non-Requirements)

**The following are NOT part of this project**:

❌ Git integration (users have git CLI)
❌ Format conversion (users have pandoc CLI)
❌ Syntax highlighting (plain text is fine)
❌ Spell checking (use external tools)
❌ Find/Replace (Qt provides Ctrl+F)
❌ Go to line (low value)
❌ Undo/Redo beyond Qt default
❌ Multiple file tabs (single file focus)
❌ Project management (out of scope)
❌ Collaboration features (not an editor concern)
❌ Cloud sync (use Dropbox/Git)
❌ Plugin system (adds complexity)
❌ Custom themes (dark/light is enough)
❌ Scroll synchronization (nice-to-have)
❌ Pane maximization (splitter is enough)
❌ Font size persistence (users can zoom)
❌ Splitter size persistence (users can resize)
❌ Auto-save configuration (hardcode 5 minutes)
❌ Last file reopening (user's choice)

---

## Success Criteria

### User Metrics

- ✅ User can edit and preview AsciiDoc without instructions
- ✅ Works on Linux, macOS, Windows without platform-specific issues
- ✅ No data loss reported in 100 sessions
- ✅ Preview updates feel instant (subjective, <1 second)

### Technical Metrics

- ✅ Code is <1,000 LOC
- ✅ Test coverage >70%
- ✅ Zero threading bugs (because no threading)
- ✅ Startup time <1 second
- ✅ Memory usage <100MB for typical docs

### Project Metrics

- ✅ MVP delivered in 2-4 weeks
- ✅ New developer can understand code in <1 hour
- ✅ Can add new feature in <1 day
- ✅ Zero "too complex" feedback from contributors

---

## Development Phases

### Phase 1: Minimal Editor (Week 1)
- Basic QMainWindow with editor and preview
- Open/Save .adoc files
- Synchronous preview rendering
- **Deliverable**: Can edit and preview

### Phase 2: Polish (Week 2)
- Dark/Light theme toggle
- Settings persistence (3 fields)
- Keyboard shortcuts
- **Deliverable**: Usable daily driver

### Phase 3: Testing (Week 3)
- Unit tests for Settings
- Unit tests for file I/O
- GUI tests for main workflows
- **Deliverable**: >70% coverage

### Phase 4: Documentation (Week 4)
- README with screenshots
- Keyboard shortcuts reference
- Installation instructions
- **Deliverable**: v1.0 release

---

## Comparison to Original Specification

| Aspect | Original v1.0 | KISS v2.0 | Change |
|--------|---------------|-----------|--------|
| **Functional Requirements** | 53 | 15 | -72% |
| **User Stories** | 6 | 1 | -83% |
| **Spec Document Lines** | 1,366 | ~300 | -78% |
| **Target LOC** | 3,000+ | <1,000 | -67% |
| **Worker Threads** | 3 | 0 | -100% |
| **External Integrations** | 3 | 1 | -67% |
| **Settings Fields** | 10 | 3 | -70% |
| **Dependencies** | 6+ | 4 | -33% |
| **Development Time** | 3-6 months | 2-4 weeks | -80% |

---

## Migration from v1.0

If migrating from the over-engineered v1.0 specification:

### Remove Immediately
- Delete `GitWorker`, `PandocWorker`, `PreviewWorker` classes
- Delete `pandoc_integration.py` module
- Delete Git menu and related commands
- Delete pane maximization logic
- Delete scroll synchronization
- Delete 7 Settings fields

### Simplify
- Convert `PreviewWorker` to synchronous `_update_preview()` method
- Reduce Settings to 3 fields
- Remove all threading/async code
- Use Qt defaults for Find/Replace

### Keep
- Main window structure
- Editor and preview panes
- File open/save logic (atomic writes)
- Settings persistence (simplified)
- Dark/Light theme
- Keyboard shortcuts

---

## Appendix: Why KISS Matters

### Real-World Evidence

**Complex v1.0 Specification Issues**:
- 3,147 LOC → harder to maintain
- 3 worker threads → race condition bugs
- 53 FRs → scope creep
- 3-6 month timeline → slow delivery
- High onboarding cost → fewer contributors

**KISS v2.0 Benefits**:
- <1,000 LOC → easy to understand
- No threading → no race conditions
- 15 FRs → focused scope
- 2-4 week timeline → fast iteration
- Low complexity → more contributors

### The KISS Principle

> "Simplicity is the ultimate sophistication." - Leonardo da Vinci

> "Make things as simple as possible, but not simpler." - Einstein

> "The best code is no code at all." - Jeff Atwood

### Complexity Budget

Every feature has a cost:
- **Lines of code** to implement
- **Tests** to maintain
- **Documentation** to write
- **Bugs** to fix
- **Mental overhead** to understand

**KISS principle**: Only pay these costs if value > cost.

For AsciiDoc Artisan, **editing + preview** is 90% of the value.
Everything else is <10% of value but 70% of complexity.

**Conclusion**: Remove the 70% complexity, keep the 90% value.

---

## Final Recommendation

**Adopt this KISS specification** and refactor the codebase accordingly.

**Expected outcomes**:
- ✅ 75% less code to maintain
- ✅ 10x faster development cycles
- ✅ Zero threading bugs
- ✅ Easier to contribute
- ✅ Better user experience (fewer features to learn)

**Risk**: Low. Simple code is more reliable than complex code.

---

**Specification Version**: 2.0 (KISS Edition)
**Date**: 2025-10-23
**Status**: PROPOSED
**Supersedes**: v1.0 (over-engineered specification)
**Next Step**: Review and approve this simplified approach
