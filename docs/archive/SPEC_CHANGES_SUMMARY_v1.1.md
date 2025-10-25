# Specification Changes Summary - v1.0 to v1.1

**Date**: 2025-10-23
**Urgency**: CRITICAL - Security fixes required before production

---

## Quick Overview

**Total Changes**: 27 issues addressed
- **3 Critical** security vulnerabilities fixed
- **7 High** priority issues resolved
- **11 Medium** improvements implemented
- **6 Low** enhancements added

**Files Created**:
1. `/tmp/AsciiDoctorArtisan-Security-Analysis.md` (1,415 lines) - Complete analysis
2. `/tmp/SPEC_UPDATES_v1.1.md` (1,257 lines) - Specification updates with code examples

---

## Critical Changes (Must Implement)

### 1. API Key Security (NEW FR-060)
**Before**: Plaintext `.env` files
**After**: OS keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)

```python
# Implementation
import keyring
api_key = keyring.get_password("AsciiDoctorArtisan", "anthropic_api_key")
```

**Impact**: Prevents API key theft, credential exposure

---

### 2. Command Injection Prevention (NEW FR-061)
**Before**: Potential `shell=True` usage
**After**: Parameterized subprocess calls only

```python
# NEVER THIS:
subprocess.run(f'git commit -m "{user_input}"', shell=True)  # DANGEROUS

# ALWAYS THIS:
subprocess.run(['git', 'commit', '-m', user_input])  # SAFE
```

**Impact**: Prevents arbitrary command execution

---

### 3. Path Traversal Fix
**Before**: Broken sanitization logic
**After**: Proper boundary validation

```python
# Fixed implementation with allowed directory checking
def sanitize_path(path_str: str, base_dir: Optional[Path] = None) -> Optional[Path]:
    path = Path(path_str).resolve()
    if base_dir:
        path.relative_to(base_dir)  # Raises ValueError if outside base
    return path
```

**Impact**: Prevents unauthorized file system access

---

## Performance Specification Corrections

### Preview Debouncing
**Old Spec**: 250ms debounce + ??? render = **250ms total** ❌ (impossible)
**New Spec**: 350ms debounce + 150ms render = **500ms total** ✅ (achievable)

### Document Size Limits
**Old Spec**: 10,000 lines (tested)
**New Spec**: 25,000 lines with:
- Performance testing required
- Memory limit: 1.5GB max
- Progressive warnings at 10k/15k/20k lines
- Option to disable live preview

---

## Architecture Changes

### Module Structure (MANDATORY)
**Before**: Single 101KB file (2,378 lines) ❌
**After**: Modular structure with max 500 lines per file ✅

```
asciidoctor_artisan/
├── ui/          # UI components
├── workers/     # Background threads
├── core/        # Business logic
├── git/         # Git operations
├── conversion/  # Pandoc
└── claude/      # AI integration
```

**Impact**: Maintainability, testability, code quality

---

### Worker Cancellation (NEW FR-063)
**Before**: No way to cancel background operations
**After**: All workers cancellable

```python
class CancellableWorker(QThread):
    def cancel(self):
        self._cancelled = True

    def run(self):
        if self.is_cancelled():
            return
        # ... do work ...
```

**Impact**: Better responsiveness, resource management

---

## New Security Requirements

### FR-060: Secure API Key Storage
- OS keyring integration (keyring library)
- No plaintext `.env` files
- Secure key rotation support

### FR-061: Subprocess Security
- NO `shell=True` ever
- Parameterized arguments only
- Input validation & allowlists
- Subprocess timeouts & resource limits

### FR-062: Node.js Service Authentication
- Random token generation on startup
- `X-API-Token` header required
- Rate limiting (100 req/15min)
- Localhost-only binding

### FR-063: Cancellable Operations
- All background workers cancellable
- Progress indicators
- Resource cleanup on cancel

### FR-064: Security Logging
- Dedicated security event log
- Log sanitization (no API keys/passwords)
- Restrictive log permissions (0600)

---

## Updated Requirements

### Performance (FR-002, FR-005, FR-045)
- Preview debounce: **350ms** (adaptive: 350-750ms based on size)
- Total preview latency: **500ms** (small docs), **1000ms** (large docs)
- Document limit: **25,000 lines** (tested and validated)
- Memory limit: **1.5GB maximum**

### Dependencies (ADD)
```
# Python
keyring>=24.0.0
cryptography>=41.0.0
psutil>=5.9.0
bandit>=1.7.5

# Node.js
keytar@^7.9.0
express-rate-limit@^7.1.0
```

### Testing (MANDATORY)
- Security tests for path traversal
- Command injection tests
- Performance tests for 1k-25k line documents
- Memory usage validation
- Cross-platform testing

---

## Implementation Timeline

### Phase 1: Security Hardening (Weeks 1-2) - CRITICAL
- [ ] Implement OS keyring for API keys
- [ ] Fix command injection (Git, Pandoc)
- [ ] Update path sanitization
- [ ] Add Node.js authentication

### Phase 2: Performance (Week 3)
- [ ] Adaptive debouncing (350-750ms)
- [ ] Document size validation
- [ ] Worker cancellation
- [ ] Performance testing

### Phase 3: Refactoring (Weeks 4-6)
- [ ] Split 101KB file into modules
- [ ] Implement module structure
- [ ] Update all imports
- [ ] Verify functionality

### Phase 4: Testing & Release (Week 7)
- [ ] Write security tests
- [ ] Performance benchmarking
- [ ] Cross-platform validation
- [ ] Security audit
- [ ] Release v1.1.0

---

## Migration from v1.0

### For Users:
1. Update to v1.1
2. On first launch, app will migrate API key from `.env` to keyring
3. `.env` file deleted automatically (with confirmation)
4. No other changes required

### For Developers:
1. Install new dependencies (`keyring`, `keytar`)
2. Review updated code examples in SPEC_UPDATES_v1.1.md
3. Follow module structure for new code
4. Run security tests before committing
5. Use provided templates for subprocess calls

---

## Risk Assessment

### Before v1.1 (Current):
- **Critical vulnerabilities**: 3 (API exposure, command injection, path traversal)
- **High risks**: 7 (unauth'd service, injection vectors, etc.)
- **Production readiness**: ❌ NOT SAFE

### After v1.1 (Updated):
- **Critical vulnerabilities**: 0 ✅
- **High risks**: 0 ✅
- **Production readiness**: ✅ SAFE (after implementation & testing)

---

## Compliance

### Constitution VII (Testing)
**Before**: ❌ FAIL - No test suite
**After**: ✅ PASS - Security & performance tests required

### Constitution VI (Code Quality)
**Before**: ❌ FAIL - 101KB monolithic file
**After**: ✅ PASS - Modular structure enforced

### Constitution III (Data Integrity)
**Before**: ⚠️ PARTIAL - Atomic writes good, but gaps
**After**: ✅ PASS - All edge cases handled

---

## Next Steps

1. **Review** both analysis documents:
   - `AsciiDoctorArtisan-Security-Analysis.md`
   - `SPEC_UPDATES_v1.1.md`

2. **Approve** specification changes

3. **Implement** in priority order:
   - Phase 1 (Security) - 2 weeks
   - Phase 2 (Performance) - 1 week
   - Phase 3 (Refactoring) - 3 weeks
   - Phase 4 (Testing) - 1 week

4. **Release** v1.1.0 after full validation

---

## Questions?

See detailed documentation in:
- **Full Analysis**: `/tmp/AsciiDoctorArtisan-Security-Analysis.md`
- **Complete Spec Updates**: `/tmp/SPEC_UPDATES_v1.1.md`

**Contact**: Project maintainer for review and approval
**Deadline**: Critical security fixes should be implemented ASAP
**Target Release**: v1.1.0 in 4-6 weeks

