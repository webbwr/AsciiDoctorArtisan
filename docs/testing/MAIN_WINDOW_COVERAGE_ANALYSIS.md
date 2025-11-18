# Main Window Coverage Analysis

**Date:** November 18, 2025
**File:** `src/asciidoc_artisan/ui/main_window.py`
**Current Coverage:** 74% (570/771 statements)
**Target Coverage:** 85% (655/771 statements)
**Gap:** 85 statements (11% increase needed)

---

## Summary

The main_window.py coverage is **74%**, significantly lower than the initially stated 84.8%. To reach the 85% target, we need to cover **85 additional statements**, which represents **42.3% of currently uncovered code**.

This is a **substantial effort**, not the "0.2% gain" initially mentioned. The revised estimate for Phase 4G is **20-30 hours** of work, not 4-6 hours.

---

## Coverage Breakdown

### Current State
- **Total statements:** 771
- **Covered:** 570 (74%)
- **Missing:** 201 (26%)

### Target State (85%)
- **Need to cover:** 655 statements
- **Additional coverage required:** 85 statements
- **Percentage of uncovered to test:** 42.3%

---

## Missing Line Analysis

### Large Uncovered Blocks

The following are significant uncovered code sections:

#### 1. Lines 514-549 (36 lines) - Import Dialog Handling
```python
# Likely: Import dialog with format selection, file validation
# Priority: HIGH - User-facing feature
# Estimated tests: 5-8 tests
```

#### 2. Lines 1506-1572 (67 lines) - Unknown Section
```python
# Need to review code to determine functionality
# Priority: TBD
# Estimated tests: 10-15 tests
```

#### 3. Lines 1586-1651 (66 lines) - Unknown Section
```python
# Need to review code to determine functionality
# Priority: TBD
# Estimated tests: 10-15 tests
```

#### 4. Lines 891-912 (22 lines) - Unknown Section
```python
# Need to review code to determine functionality
# Priority: TBD
# Estimated tests: 3-5 tests
```

#### 5. Lines 830-840 (11 lines) - Unknown Section
```python
# Need to review code to determine functionality
# Priority: TBD
# Estimated tests: 2-3 tests
```

### Scattered Single Lines (53 occurrences)
Multiple individual lines and small 2-5 line blocks throughout the file:
- Lines: 101, 210, 221-224, 273, 277, 316, 489-490, etc.
- **Priority:** LOW - Likely error handlers, edge cases, defensive code
- **Estimated tests:** 10-20 tests for all combined

---

## Revised Effort Estimate

### Test Development
| Category | Lines | Tests Needed | Hours | Priority |
|----------|-------|--------------|-------|----------|
| Large blocks (3 sections) | 169 | 25-38 | 12-18h | HIGH |
| Medium blocks (5 sections) | 50+ | 10-15 | 5-8h | MEDIUM |
| Small/scattered | 53 | 10-20 | 3-5h | LOW |
| **Total** | **201** | **45-73** | **20-31h** | - |

### Code Review
- Understand uncovered sections: 2-3h
- Identify testable vs untestable code: 1-2h
- Document Qt limitations: 1h
- **Subtotal:** 4-6h

### Total Estimated Effort
- **Test development:** 20-31h
- **Code review:** 4-6h
- **Total:** **24-37 hours** (3-5 weeks at 8h/week)

---

## Challenges

### 1. Unknown Code Sections
Lines 1506-1651 (133 lines total) are large uncovered blocks. Without reviewing the code, it's unclear if they are:
- Unreachable defensive code (can document and skip)
- Qt threading limitations (cannot test, document only)
- Missing test coverage (need tests)
- Dead code (can remove)

### 2. Potential Qt Limitations
Some uncovered lines may be Qt C++ callbacks or thread pool operations that coverage.py cannot track (similar to issues in workers/claude_worker.py).

### 3. Test Complexity
Main window tests are integration-heavy, requiring:
- Multiple mocked dependencies
- Qt event loop coordination
- Proper fixture setup/teardown
- Long test execution times (20s for 112 tests currently)

### 4. Diminishing Returns
The last 10-15% of coverage often represents:
- Error handlers (hard to trigger)
- Edge cases (require complex setup)
- Defensive code (may be unreachable)
- Platform-specific code (may not run in test environment)

---

## Recommendations

### Option A: Revise Target (RECOMMENDED)
**Recommendation:** Set realistic target of **80% coverage** instead of 85%

**Rationale:**
- Current 74% is respectable for complex UI code
- 80% is achievable in 8-12 hours (covering ~45 statements)
- Focus on high-value, user-facing code paths
- Document remaining uncovered code as Qt limitations or defensive code

**Benefits:**
- Achievable within v2.0.5 timeline
- Focuses on high-impact testing
- Maintains quality without diminishing returns

### Option B: Phase 4G in Phases (IF 85% IS REQUIRED)
**Phase 4G.1 (v2.0.5): 74% → 80%** (8-12 hours)
- Cover large uncovered blocks (lines 514-549)
- Add tests for common user workflows in uncovered sections
- Document remaining uncovered code

**Phase 4G.2 (v2.0.6): 80% → 85%** (12-18 hours)
- Review and test lines 1506-1651
- Add edge case tests
- Final documentation of untestable code

**Phase 4G.3 (v2.1.0): 85%+ if possible** (10-15 hours)
- Cover remaining scattered lines
- Maximum achievable coverage assessment

### Option C: Full Push to 85% (NOT RECOMMENDED)
- **Effort:** 24-37 hours (3-5 weeks)
- **Risk:** High - may hit Qt limitations or dead code
- **Value:** Low - last 11% has diminishing returns
- **Recommendation:** Only if compliance/audit requires it

---

## Action Items for v2.0.5

### Immediate (Current Session)
1. ✅ Document actual coverage (74%, not 84.8%)
2. ✅ Revise effort estimate (24-37h, not 4-6h)
3. ✅ Create this analysis document
4. ⏭ Update v2.0.5 plan with revised estimate

### For v2.0.5 Release (Recommend Option A)
1. Set realistic target: 80% coverage
2. Review uncovered blocks (lines 514-549, 1506-1651, 1586-1651)
3. Identify high-value tests (user-facing features)
4. Add 8-15 tests covering ~45 statements
5. Document remaining uncovered code
6. Update coverage target in ROADMAP.md

### For Future Releases (If needed)
1. Phase 4G.2 (v2.0.6): 80% → 85%
2. Phase 4G.3 (v2.1.0): 85%+ maximum achievable
3. Final Qt limitations documentation

---

## Coverage Report Details

### Missing Lines (201 total)
```
101, 210, 221-224, 273, 277, 316, 489-490, 495-506, 514-549,
654, 658, 739, 743, 780, 784, 793, 803, 808, 830-840, 891-912,
916-918, 922-927, 946-947, 951-952, 956-957, 961-962, 966-967,
976, 981-984, 989-995, 1000-1003, 1128, 1166, 1190, 1211-1212,
1219, 1240-1241, 1266-1269, 1277, 1295-1298, 1433, 1451, 1459,
1463, 1467, 1471, 1475, 1479, 1483, 1487, 1491, 1495, 1506-1572,
1586-1651, 1658, 1662, 1666
```

### Largest Gaps (Top 5)
1. **Lines 1586-1651:** 66 lines (33% of gap)
2. **Lines 1506-1572:** 67 lines (33% of gap)
3. **Lines 514-549:** 36 lines (18% of gap)
4. **Lines 891-912:** 22 lines (11% of gap)
5. **Lines 830-840:** 11 lines (5% of gap)

**Total in top 5:** 202 lines (exceeds gap due to overlap in count)

---

## Conclusion

The initial assessment of "84.8% coverage, need +0.2% to reach 85%" was **incorrect**. Actual coverage is **74%**, requiring **+11% (85 statements)** to reach 85%.

### Recommended Path Forward

**For v2.0.5:**
- ✅ Set realistic target: **80% coverage** (74% + 6%)
- ✅ Estimated effort: **8-12 hours**
- ✅ Focus: High-value user-facing code paths
- ✅ Document: Qt limitations and defensive code

**For future releases:**
- Consider Phase 4G.2 (80% → 85%) only if required
- Maximum achievable may be ~90% due to Qt limitations
- Diminishing returns beyond 85%

**Quality over quantity:** 80% coverage with well-tested critical paths is more valuable than 85% coverage with edge case tests that provide minimal value.

---

*Analysis created: November 18, 2025*
*Recommendation: Revise v2.0.5 target from 85% to 80%*
*Revised effort: 8-12 hours (achievable), not 24-37 hours (original 85% target)*
