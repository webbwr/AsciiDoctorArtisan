# Numba JIT Benchmark Findings

**Date**: October 26, 2025
**Numba Version**: 0.62.1
**Status**: ⚠️ NOT RECOMMENDED for String Operations

---

## Key Finding

**Numba JIT makes string processing SLOWER, not faster.**

### Benchmark Results

| Operation | Manual (Python) | Numba JIT | Result |
|-----------|----------------|-----------|--------|
| Cell Cleaning | 45.26µs | 255.02µs | 0.2x (5x SLOWER) |
| Heading Detection | 0.26ms | 2.90ms | 0.1x (11x SLOWER) |

---

## Why Numba is Slower

### 1. Compilation Overhead
- JIT compilation takes time
- Each function call has overhead
- Not worth it for small strings

### 2. String Operations
- Python's strings are already optimized in C
- Numba can't optimize Python strings well
- Native Python is faster

### 3. Best Use Cases for Numba
- **Good**: Number arrays (numpy)
- **Good**: Math loops
- **Good**: Scientific computing
- **Bad**: String manipulation
- **Bad**: Small operations

---

## Recommendation

### Remove Numba from This Project

**Reasons:**
1. Measurably slower for our use case
2. Adds dependency for no benefit
3. Python native code is faster
4. Simpler is better

**What to Keep:**
- GPU acceleration (2-5x faster) ✓
- PyMuPDF (3-5x faster) ✓

**What to Remove:**
- Numba JIT decorators
- Numba imports
- Numba documentation claims

---

## Alternative Optimizations

### For String Processing

**1. Use Built-in Methods:**
```python
# Fast - uses C implementation
text = " ".join(text.split())
```

**2. List Comprehensions:**
```python
# Fast - optimized by Python
result = [x for x in items if condition]
```

**3. Regular Expressions (re module):**
```python
# Fast - C-compiled
import re
text = re.sub(r'\s+', ' ', text)
```

### For Table Processing

**Use pandas or numpy:**
- These work well with Numba
- Already optimized
- Better for large data

---

## Action Items

### Immediate
1. Remove `@jit` decorators from code
2. Remove Numba imports
3. Update documentation
4. Update requirements.txt
5. Re-run tests

### Documentation Updates
1. Remove Numba claims from README.md
2. Update CHANGELOG.md
3. Update SPECIFICATIONS.md
4. Update performance docs

---

## Lessons Learned

### What We Learned

1. **Measure, Don't Guess**
   - Always benchmark before claiming speedup
   - Real data beats assumptions

2. **Right Tool for Job**
   - Numba is for numbers, not strings
   - Python strings are already fast

3. **Simpler is Better**
   - Fewer dependencies
   - Less complexity
   - More maintainable

### What Still Works

**GPU Acceleration** (Tier 1.1):
- 2-5x faster preview
- 30-50% less CPU
- ✓ Proven benefit

**PyMuPDF** (Tier 1.2):
- 3-5x faster PDF
- Real speedup
- ✓ Proven benefit

---

## Updated Performance Claims

### Before (Incorrect)
- Preview: 2-5x faster ✓
- PDF: 3-5x faster ✓
- Tables: 10-50x faster ✗ (WRONG)
- Text: 5-10x faster ✗ (WRONG)

### After (Correct)
- Preview: 2-5x faster ✓
- PDF: 3-5x faster ✓
- Overall: 2-5x faster ✓

**Total Real Speedup**: 2-5x (still excellent!)

---

## Next Steps

1. Remove Numba code
2. Update all docs
3. Keep GPU + PyMuPDF
4. Consider other optimizations:
   - C extensions for hot paths?
   - Better caching strategies?
   - Async file operations?

---

**Reading Level**: Grade 5.0
**Status**: Findings complete, action needed
**Priority**: Medium (misleading docs should be fixed)
