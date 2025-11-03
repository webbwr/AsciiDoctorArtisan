# Test Coverage Improvement Strategy

## Current Status
- **Reported Coverage**: 60%+ (1,500+ tests)
- **Goal**: 100% coverage (CRITICAL priority)
- **Git Worker Tests**: 16/16 passing ✅
- **Blocker**: Property-based tests require hypothesis module (not in venv)

## Strategic Approach (Time-Efficient)

Given the challenge of running full coverage in current environment, here's a practical approach:

### Phase 1: Identify Coverage Gaps (2-4 hours)
1. Run coverage on individual module categories
2. Focus on modules with business logic (not just UI glue)
3. Create targeted test files for uncovered areas

### Phase 2: Write High-Value Tests First (20-30 hours)
**Priority Order:**
1. **Core Business Logic** (core/)
   - file_operations.py
   - settings.py
   - models.py (data validation)
   
2. **Workers** (workers/)
   - git_worker.py (already done ✅)
   - pandoc_worker.py
   - preview_worker.py
   - ollama_chat_worker.py

3. **UI Managers** (ui/)
   - menu_manager.py
   - theme_manager.py
   - status_manager.py
   - Git handlers

4. **Integration Points**
   - Conversion workflows
   - AI chat flows
   - Git status/commit flows

### Phase 3: Fill Remaining Gaps (10-20 hours)
- Edge cases
- Error paths
- Integration scenarios

## Pragmatic Targets

**By Week 2**: 75% coverage (+15%)
- Core modules at 90%+
- Workers at 85%+
  
**By Week 4**: 90% coverage (+30%)
- All business logic covered
- Integration tests for key workflows

**By Week 6**: 100% coverage (+40%)
- All edge cases
- All error paths
- Full integration coverage

## Immediate Actions

1. ✅ Fix missing hypothesis dependency (or skip those tests)
2. Run make test to see current baseline
3. Identify top 10 modules with lowest coverage
4. Write tests for those first
5. Iterate

## Acceptance Criteria

- All critical paths have tests
- All error conditions are tested
- No module below 90% coverage
- Integration tests for user workflows
- Performance tests don't regress
