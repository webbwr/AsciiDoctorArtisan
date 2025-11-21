#!/bin/bash
#
# Claude Code Detailed Status Line
# Provides comprehensive context for minimal-verbosity mode
# Performance optimized: Caches expensive QA checks (5-min TTL)
# MA Principle: Extracted functions for maintainability
#

# Colors for output
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
CYAN='\033[36m'

# Project information
PROJECT_NAME="AsciiDocArtisan"
PROJECT_VERSION="2.0.8"

# MA Principle: Extract coverage detection (37→15 lines)
get_coverage() {
    if [ -f htmlcov/status.json ]; then
        python3 -c "
try:
    import json
    data = json.load(open('htmlcov/status.json'))
    if 'files' in data:
        total_stmts = sum(f.get('index', {}).get('nums', {}).get('n_statements', 0) for f in data['files'].values())
        total_missing = sum(f.get('index', {}).get('nums', {}).get('n_missing', 0) for f in data['files'].values())
        print(f'{((total_stmts - total_missing) / total_stmts) * 100:.1f}' if total_stmts > 0 else '?')
    else: print('?')
except Exception: print('?')
" 2>/dev/null || echo "?"
    elif [ -f coverage.xml ]; then
        python3 -c "
try:
    import xml.etree.ElementTree as ET
    print(f'{float(ET.parse(\"coverage.xml\").getroot().attrib.get(\"line-rate\", 0)) * 100:.1f}')
except Exception: print('?')
" 2>/dev/null || echo "?"
    elif [ -f htmlcov/index.html ]; then
        grep -o "[0-9]*%" htmlcov/index.html 2>/dev/null | head -1 | tr -d '%' || echo "?"
    else
        echo "?"
    fi
}

# MA Principle: Extract test count from logs (24→12 lines)
get_test_count_from_logs() {
    if ls /tmp/test_*.log >/dev/null 2>&1; then
        COUNT=$(grep -h "$1" /tmp/test_*.log 2>/dev/null | grep -o "$2" | cut -d' ' -f$3 | awk '{s+=$1} END {print s}')
        [[ "$COUNT" =~ ^[0-9]+$ ]] && echo "$COUNT" || echo ""
    else
        echo ""
    fi
}

# MA Principle: Extract test statistics gathering (70→46 lines)
get_test_statistics() {
    local TOTAL_TESTS="" TEST_PASSED=""

    # Get total and passed from /tmp/test_*.log (most recent)
    TOTAL_TESTS=$(get_test_count_from_logs "collected" "collected [0-9]* items" 2)
    TEST_PASSED=$(get_test_count_from_logs "passed" "[0-9]* passed" 1)

    # Fallback for passed tests if primary method failed
    if [ -z "$TEST_PASSED" ]; then
        TEST_PASSED=$(grep -ch "PASSED" /tmp/test_*.log 2>/dev/null | awk '{s+=$1} END {print s}')
        [[ ! "$TEST_PASSED" =~ ^[0-9]+$ ]] && TEST_PASSED=""
    fi

    # Fallback to .pytest_cache for total tests
    if [ -z "$TOTAL_TESTS" ] && [ -f .pytest_cache/v/cache/nodeids ]; then
        TOTAL_TESTS=$(python3 -c "try: import json; print(len(json.load(open('.pytest_cache/v/cache/nodeids')))); except: print('?')" 2>/dev/null || echo "?")
    else
        [ -z "$TOTAL_TESTS" ] && TOTAL_TESTS="?"
    fi

    # Try test_run_fast.log if still missing passed count
    [ -z "$TEST_PASSED" ] && [ -f test_run_fast.log ] && TEST_PASSED=$(grep -o "[0-9]* passed" test_run_fast.log 2>/dev/null | tail -1 | cut -d' ' -f1)

    # Calculate from lastfailed if needed
    if [ -z "$TEST_PASSED" ] && [ -f .pytest_cache/v/cache/lastfailed ] && [ "$TOTAL_TESTS" != "?" ]; then
        FAILED_COUNT=$(python3 -c "try: import json; print(len(json.load(open('.pytest_cache/v/cache/lastfailed')))); except: pass" 2>/dev/null || echo "")
        [ -n "$FAILED_COUNT" ] && TEST_PASSED=$((TOTAL_TESTS - FAILED_COUNT))
    fi

    # Try htmlcov/index.html as last resort
    [ -z "$TEST_PASSED" ] && TEST_PASSED=$(grep -o "[0-9]* passed" htmlcov/index.html 2>/dev/null | head -1 | cut -d' ' -f1)
    [ -z "$TEST_PASSED" ] && TEST_PASSED="?"

    # Calculate percentage and format
    if [ "$TOTAL_TESTS" != "?" ] && [ "$TEST_PASSED" != "?" ] && [ "$TOTAL_TESTS" -gt 0 ]; then
        TEST_PCT=$(awk "BEGIN {printf \"%.1f\", ($TEST_PASSED / $TOTAL_TESTS) * 100}")
        echo "${TEST_PASSED}/${TOTAL_TESTS} (${TEST_PCT}%)"
    elif [ "$TOTAL_TESTS" != "?" ] && [ "$TEST_PASSED" != "?" ]; then
        echo "${TEST_PASSED}/${TOTAL_TESTS}"
    else
        echo "${TEST_PASSED}"
    fi
}

# MA Principle: Extract MA violation parsing (14 lines)
parse_ma_violations() {
    local MA_OUTPUT="$1"

    # Extract violation counts using grep and awk for robustness
    # Format: "  - P0 (Critical): 0 (>100 lines or complexity >15)"
    local P0=$(echo "$MA_OUTPUT" | grep -E "^\s*-\s*P0 \(Critical\):" | head -1 | awk -F': ' '{print $2}' | awk '{print $1}' | tr -d '\n\r ')
    local P1=$(echo "$MA_OUTPUT" | grep -E "^\s*-\s*P1 \(High\):" | head -1 | awk -F': ' '{print $2}' | awk '{print $1}' | tr -d '\n\r ')
    local TOTAL=$(echo "$MA_OUTPUT" | grep "Total Violations:" | head -1 | awk '{print $NF}' | tr -d '\n\r ')

    # Default to 0 if extraction failed
    [ -z "$P0" ] && P0="0"
    [ -z "$P1" ] && P1="0"
    [ -z "$TOTAL" ] && TOTAL="0"

    echo "${P0}|${P1}|${TOTAL}"
}

# MA Principle: Extract QA checks (30→20 lines)
run_qa_checks() {
    MYPY_STATUS=$(mypy src --strict 2>&1 | grep -q "Success" && echo "✓" || echo "✗")
    RUFF_STATUS=$(ruff check src 2>&1 | grep -q "All checks passed" && echo "✓" || echo "✗")

    # MA Principle compliance
    if [ -f scripts/analyze_ma_violations.py ]; then
        MA_OUTPUT=$(python3 scripts/analyze_ma_violations.py 2>&1 || true)
        MA_PARSED=$(parse_ma_violations "$MA_OUTPUT")

        MA_P0=$(echo "$MA_PARSED" | cut -d'|' -f1)
        MA_P1=$(echo "$MA_PARSED" | cut -d'|' -f2)
        MA_TOTAL=$(echo "$MA_PARSED" | cut -d'|' -f3)

        MA_STATUS=$( [ "$MA_P0" -eq 0 ] 2>/dev/null && echo "✓" || echo "✗" )
        MA_VIOLATIONS="P0:${MA_P0} P1:${MA_P1} (${MA_TOTAL} total)"
    else
        MA_STATUS="—"
        MA_VIOLATIONS="not configured"
    fi

    # Write to cache
    cat > "$1" << EOF
MYPY_STATUS="$MYPY_STATUS"
RUFF_STATUS="$RUFF_STATUS"
MA_STATUS="$MA_STATUS"
MA_VIOLATIONS="$MA_VIOLATIONS"
EOF
}

# MA Principle: Extract cached QA status (56→21 lines)
get_cached_qa_status() {
    local CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/asciidoc_artisan"
    local CACHE_FILE="$CACHE_DIR/qa_status.cache"
    local CACHE_TTL=300  # 5 minutes

    mkdir -p "$CACHE_DIR"

    # Check if cache is valid
    local CACHE_VALID=0
    if [ -f "$CACHE_FILE" ]; then
        CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)))
        [ "$CACHE_AGE" -lt "$CACHE_TTL" ] && CACHE_VALID=1
    fi

    if [ "$CACHE_VALID" -eq 1 ]; then
        source "$CACHE_FILE"  # Read from cache
    else
        run_qa_checks "$CACHE_FILE"  # Run checks and cache
        source "$CACHE_FILE"
    fi
}

# ============================================================================
# Display Formatting Functions (MA Principle)
# ============================================================================

# MA Principle: Extract Git info gathering (10 lines)
get_git_info() {
    local BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
    local STATUS=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    local AHEAD=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo "0")
    local BEHIND=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo "0")
    echo "${BRANCH}|${STATUS}|${AHEAD}|${BEHIND}"
}

# MA Principle: Extract Python env detection (8 lines)
get_python_env() {
    local VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
    local VENV="✗"
    if [ -n "$VIRTUAL_ENV" ] || ([ -d "venv" ] && [ -f "venv/bin/python" ]); then
        VENV="✓"
    fi
    echo "${VERSION}|${VENV}"
}

# MA Principle: Extract system info (8 lines)
get_system_info() {
    local ARCH=$(uname -m)
    local OPT="✓"
    [[ "$ARCH" != "arm64" && "$ARCH" != "x86_64" ]] && OPT="—"
    local OS=$(uname -s)
    local VER=$(uname -r | cut -d. -f1-2)
    echo "${ARCH}|${OPT}|${OS}|${VER}"
}

# MA Principle: Extract display lines (24 lines)
build_status_display() {
    # Parse all info
    local GIT_INFO=$(get_git_info)
    local PY_INFO=$(get_python_env)
    local SYS_INFO=$(get_system_info)

    local GIT_BRANCH=$(echo "$GIT_INFO" | cut -d'|' -f1)
    local GIT_STATUS=$(echo "$GIT_INFO" | cut -d'|' -f2)
    local GIT_AHEAD=$(echo "$GIT_INFO" | cut -d'|' -f3)
    local GIT_BEHIND=$(echo "$GIT_INFO" | cut -d'|' -f4)

    local PY_VER=$(echo "$PY_INFO" | cut -d'|' -f1)
    local VENV=$(echo "$PY_INFO" | cut -d'|' -f2)

    local ARCH=$(echo "$SYS_INFO" | cut -d'|' -f1)
    local OPT=$(echo "$SYS_INFO" | cut -d'|' -f2)
    local OS=$(echo "$SYS_INFO" | cut -d'|' -f3)
    local OS_VER=$(echo "$SYS_INFO" | cut -d'|' -f4)

    # Display (MA principle: focused, scannable lines)
    cat << EOF
${BOLD}${BLUE}┏━━ ${PROJECT_NAME} v${PROJECT_VERSION}${RESET}
${DIM}├─ Git${RESET}: ${GREEN}${GIT_BRANCH}${RESET} │ ${YELLOW}±${GIT_STATUS}${RESET} │ ↑${GIT_AHEAD} ↓${GIT_BEHIND}
${DIM}├─ Env${RESET}: Python ${PY_VER} │ venv:${VENV} │ ${ARCH} (opt:${OPT})
${DIM}├─ QA ${RESET}: mypy:${MYPY_STATUS} │ ruff:${RUFF_STATUS} │ MA:${MA_STATUS} ${MA_VIOLATIONS}
${DIM}├─ TST${RESET}: ${TEST_STATS} │ Coverage:${COVERAGE}%
${DIM}└─ OS ${RESET}: ${OS} ${OS_VER} │ $(date +"%H:%M:%S")
EOF
}

# ============================================================================
# Main Status Line Generation
# ============================================================================

# Gather metrics
COVERAGE=$(get_coverage)
TEST_STATS=$(get_test_statistics)
get_cached_qa_status

# Build and display status
build_status_display
