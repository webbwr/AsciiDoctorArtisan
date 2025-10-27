# AsciiDoc Artisan v1.4.0 Roadmap

**Target Release:** Q1 2026 (January-March)
**Focus:** Technical Debt & Architecture Improvements
**Status:** Planning Phase

---

## Executive Summary

Version 1.4.0 will focus on code quality improvements, architecture refinement, and developer experience enhancements. After the successful v1.3.0 grammar system release, this version addresses technical debt while maintaining stability.

**Goals:**
- Improve maintainability of large files (main_window.py)
- Increase test coverage to 85%+
- Reduce remaining linting issues
- Improve development workflow

---

## Priority 1: Architecture Refactoring (HIGH)

### 1.1 Decompose main_window.py
**Current State:** 1,716 lines - too large for easy maintenance
**Target:** Split into 5-7 smaller, focused modules
**Effort:** 12-16 hours

**Proposed Structure:**
```
src/asciidoc_artisan/ui/
├── main_window.py (300-400 lines) - Core window coordination
├── toolbar_manager.py (NEW) - Toolbar creation and management
├── dock_manager.py (NEW) - Dock widgets and panels
├── keyboard_manager.py (NEW) - Keyboard shortcuts and bindings
├── layout_manager.py (NEW) - Window layout and splitter management
└── window_state_manager.py (NEW) - Window state persistence
```

**Benefits:**
- Easier to understand and modify
- Better separation of concerns
- Reduced merge conflicts
- Improved testability

**Implementation Plan:**
1. Extract toolbar management (150-200 lines)
2. Extract dock management (100-150 lines)
3. Extract keyboard shortcuts (100-150 lines)
4. Extract layout management (150-200 lines)
5. Extract window state (100-150 lines)
6. Update tests to cover new modules
7. Verify all functionality still works

**Risk:** MEDIUM - Requires careful testing of UI integration

---

## Priority 2: Test Infrastructure (HIGH)

### 2.1 Fix UI Test Running in WSL
**Current State:** UI tests crash due to missing display
**Target:** All UI tests passing with xvfb
**Effort:** 2-3 hours

**Implementation:**
- Configure pytest-xvfb properly for WSL2
- Add xvfb startup scripts
- Update CI/CD to use xvfb-run
- Document testing in WSL environment

### 2.2 Increase Test Coverage
**Current State:** ~70-75% coverage
**Target:** 85%+ coverage
**Effort:** 8-12 hours

**Focus Areas:**
- UI components (currently 7-23%)
- Export manager (needs edge case tests)
- Grammar manager (add integration tests)
- Error handling paths
- Edge cases and boundary conditions

**Coverage Goals:**
```
Module                  Current  Target  Gap
────────────────────────────────────────────
ui/main_window.py       15%      75%     +60%
ui/export_manager.py    23%      80%     +57%
ui/grammar_manager.py   60%      90%     +30%
ui/file_handler.py      45%      85%     +40%
ui/git_handler.py       52%      85%     +33%
workers/*.py            80%      90%     +10%
core/*.py               85%      95%     +10%
```

---

## Priority 3: Code Quality (MEDIUM)

### 3.1 Eliminate Remaining Linting Issues
**Current State:** 36 linting errors
**Target:** 0 errors, warnings only
**Effort:** 2-4 hours

**Categories:**
- Unused variables in tests (27) - Clean up or mark with underscore
- Unused imports (6) - Remove
- Module import position (3) - Fix ordering

### 3.2 Add Type Hints Coverage
**Current State:** 100% mypy pass (0 errors)
**Target:** Increase type hint coverage in older modules
**Effort:** 4-6 hours

**Focus:**
- Add missing return type hints
- Add parameter type hints in older code
- Use modern type syntax (list[str] vs List[str])

---

## Priority 4: Performance Optimizations (MEDIUM)

### 4.1 Startup Time Reduction
**Current Goal:** Reduce startup time by 20%
**Effort:** 4-6 hours

**Strategies:**
- Profile import times
- Implement more lazy loading
- Optimize heavy module imports
- Defer GPU detection to first use

### 4.2 Memory Usage Optimization
**Current:** ~150-200MB baseline
**Target:** ~100-150MB baseline
**Effort:** 4-6 hours

**Strategies:**
- Review cache sizes
- Implement cache eviction policies
- Profile memory usage patterns
- Optimize large data structures

---

## Priority 5: Developer Experience (MEDIUM)

### 5.1 Improve Documentation
**Effort:** 4-6 hours

**Additions:**
- API documentation (Sphinx)
- Architecture diagrams
- Contributing guidelines
- Development setup guide
- Testing best practices

### 5.2 CI/CD Pipeline
**Effort:** 4-6 hours

**Goals:**
- GitHub Actions workflow
- Automated testing on push
- Automated linting checks
- Multi-platform testing (Linux, Windows, Mac)
- Code coverage reporting

---

## Priority 6: Feature Enhancements (LOW)

### 6.1 Grammar System Improvements
**Effort:** 6-8 hours

**Enhancements:**
- Custom dictionary support
- Grammar rule customization UI
- Multi-language support expansion
- Performance mode improvements
- Better error reporting

### 6.2 Export Enhancements
**Effort:** 4-6 hours

**Features:**
- Export templates system
- Batch export functionality
- Better DOCX styling options
- Export presets

---

## Timeline

### Phase 1: Architecture (Weeks 1-3)
- Week 1: Extract toolbar_manager and dock_manager
- Week 2: Extract keyboard_manager and layout_manager
- Week 3: Extract window_state_manager, testing

### Phase 2: Testing (Weeks 4-5)
- Week 4: Fix UI test infrastructure
- Week 5: Add missing test coverage

### Phase 3: Quality (Week 6)
- Week 6: Fix linting, add type hints

### Phase 4: Optimization (Week 7)
- Week 7: Performance profiling and optimization

### Phase 5: Documentation (Week 8)
- Week 8: API docs, CI/CD, final polish

---

## Success Metrics

| Metric | v1.3.0 | v1.4.0 Target | Improvement |
|--------|--------|---------------|-------------|
| **Largest File** | 1,716 lines | <500 lines | 71% reduction |
| **Test Coverage** | 75% | 85%+ | +10% |
| **Linting Errors** | 36 | 0 | 100% |
| **UI Tests Passing** | 0 (blocked) | 100% | ∞ |
| **Startup Time** | 2.5s | 2.0s | 20% faster |
| **Memory Usage** | 175MB | 125MB | 29% less |
| **Quality Score** | 9.3/10 | 9.7/10 | +0.4 |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Breaking UI during refactor** | MEDIUM | HIGH | Comprehensive UI testing, gradual refactoring |
| **Test infrastructure issues** | LOW | MEDIUM | Start with simple fixes, document setup |
| **Performance regression** | LOW | MEDIUM | Benchmark before/after each change |
| **Timeline slip** | MEDIUM | LOW | Prioritize HIGH items, defer LOW items |

---

## Non-Goals for v1.4.0

The following are explicitly **out of scope** for v1.4.0:

- ❌ New user-facing features (focus is technical debt)
- ❌ Major UI redesign (incremental improvements only)
- ❌ Cloud integration (deferred to v1.5.0)
- ❌ Plugin system (deferred to v2.0.0)
- ❌ Mobile app (not planned)

---

## Dependencies

**Required for Development:**
- pytest-xvfb (already installed)
- Sphinx (for API docs)
- coverage.py (for detailed coverage reports)
- memory_profiler (for memory optimization)

**Optional:**
- GitHub Actions (for CI/CD)
- pre-commit (already set up)

---

## Communication Plan

**Milestones:**
1. **Architecture Complete** - Announce main_window.py refactoring
2. **Tests Passing** - Announce 85% coverage achievement
3. **Quality Goals Met** - Announce 0 linting errors
4. **v1.4.0-beta** - Beta release for testing
5. **v1.4.0-GA** - General availability

**Channels:**
- GitHub Releases
- README.md updates
- CHANGELOG.md entries

---

## Getting Started

To begin working on v1.4.0:

```bash
# Create feature branch
git checkout -b feature/v1.4.0-refactoring

# Start with Priority 1.1 - Extract toolbar manager
# 1. Create new file: src/asciidoc_artisan/ui/toolbar_manager.py
# 2. Move toolbar-related methods from main_window.py
# 3. Update imports and instantiation
# 4. Run tests to verify nothing broke
# 5. Commit and push
```

---

**Status:** 📝 Planning Complete
**Next Action:** Begin Phase 1 - Architecture Refactoring
**Owner:** Development Team
**Last Updated:** October 27, 2025
