#!/bin/bash
#
# Claude Code Detailed Status Line
# Provides comprehensive context for minimal-verbosity mode
# Performance optimized: Caches expensive QA checks (5-min TTL)
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
PROJECT_VERSION="2.0.5"

# Git information
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
GIT_STATUS=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
GIT_AHEAD=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo "0")
GIT_BEHIND=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo "0")

# System information
CPU_ARCH=$(uname -m)
OS_VERSION=$(uname -r | cut -d. -f1-2)

# Python environment
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
# Check if venv exists or is active
if [ -n "$VIRTUAL_ENV" ]; then
    VENV_ACTIVE="✓"
elif [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    VENV_ACTIVE="✓"
else
    VENV_ACTIVE="✗"
fi

# Test statistics (from last run)
# Try multiple sources in order of reliability: status.json > coverage.xml > index.html
if [ -f htmlcov/status.json ]; then
    COVERAGE=$(python3 -c "
try:
    import json
    data = json.load(open('htmlcov/status.json'))
    if 'files' in data:
        total_stmts = sum(f.get('index', {}).get('nums', {}).get('n_statements', 0) for f in data['files'].values())
        total_missing = sum(f.get('index', {}).get('nums', {}).get('n_missing', 0) for f in data['files'].values())
        if total_stmts > 0:
            pct = ((total_stmts - total_missing) / total_stmts) * 100
            print(f'{pct:.1f}')
        else:
            print('?')
    else:
        print('?')
except Exception:
    print('?')
" 2>/dev/null || echo "?")
    [ -z "$COVERAGE" ] && COVERAGE="?"
elif [ -f coverage.xml ]; then
    COVERAGE=$(python3 -c "
try:
    import xml.etree.ElementTree as ET
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    rate = float(root.attrib.get('line-rate', 0)) * 100
    print(f'{rate:.1f}')
except Exception:
    print('?')
" 2>/dev/null || echo "?")
    [ -z "$COVERAGE" ] && COVERAGE="?"
elif [ -f htmlcov/index.html ]; then
    COVERAGE=$(grep -o "[0-9]*%" htmlcov/index.html 2>/dev/null | head -1 | tr -d '%')
    [ -z "$COVERAGE" ] && COVERAGE="?"
else
    COVERAGE="?"
fi

# Get test statistics from /tmp/test_*.log (most recent and accurate)
TOTAL_TESTS=""
TEST_PASSED=""

if ls /tmp/test_*.log >/dev/null 2>&1; then
    # Get total collected tests from all log files
    TOTAL_TESTS=$(grep -h "collected" /tmp/test_*.log 2>/dev/null | grep -o "collected [0-9]* items" | cut -d' ' -f2 | awk '{s+=$1} END {print s}')
    # Only use if we got a valid number
    if ! [[ "$TOTAL_TESTS" =~ ^[0-9]+$ ]]; then
        TOTAL_TESTS=""
    fi

    # Get passed tests from all log files
    TEST_PASSED=$(grep -h "passed" /tmp/test_*.log 2>/dev/null | grep -o "[0-9]* passed" | cut -d' ' -f1 | awk '{s+=$1} END {print s}')
    # Only use if we got a valid number
    if ! [[ "$TEST_PASSED" =~ ^[0-9]+$ ]]; then
        TEST_PASSED=""
    fi
fi

# Fallback to .pytest_cache if /tmp/ logs not available
if [ -z "$TOTAL_TESTS" ] && [ -f .pytest_cache/v/cache/nodeids ]; then
    TOTAL_TESTS=$(python3 -c "
try:
    import json
    print(len(json.load(open('.pytest_cache/v/cache/nodeids'))))
except Exception:
    print('?')
" 2>/dev/null || echo "?")
else
    [ -z "$TOTAL_TESTS" ] && TOTAL_TESTS="?"
fi

# 2. Try test_run_fast.log (most recent full run)
if [ -z "$TEST_PASSED" ] && [ -f test_run_fast.log ]; then
    TEST_PASSED=$(grep -o "[0-9]* passed" test_run_fast.log 2>/dev/null | tail -1 | cut -d' ' -f1)
fi

# 3. Try .pytest_cache/v/cache/lastfailed (calculate passed = total - failed)
if [ -z "$TEST_PASSED" ] && [ -f .pytest_cache/v/cache/lastfailed ]; then
    FAILED_COUNT=$(python3 -c "import json; print(len(json.load(open('.pytest_cache/v/cache/lastfailed'))))" 2>/dev/null || echo "")
    if [ -n "$FAILED_COUNT" ] && [ "$TOTAL_TESTS" != "?" ]; then
        TEST_PASSED=$((TOTAL_TESTS - FAILED_COUNT))
    fi
fi

# 4. Try htmlcov/index.html (old coverage report)
if [ -z "$TEST_PASSED" ]; then
    TEST_PASSED=$(grep -o "[0-9]* passed" htmlcov/index.html 2>/dev/null | head -1 | cut -d' ' -f1)
fi

# 5. Default to unknown
if [ -z "$TEST_PASSED" ]; then
    TEST_PASSED="?"
fi

# Calculate percentage and format as "passed/total (pct%)"
if [ "$TOTAL_TESTS" != "?" ] && [ "$TEST_PASSED" != "?" ] && [ "$TOTAL_TESTS" -gt 0 ]; then
    TEST_PCT=$(awk "BEGIN {printf \"%.1f\", ($TEST_PASSED / $TOTAL_TESTS) * 100}")
    TEST_STATS="${TEST_PASSED}/${TOTAL_TESTS} (${TEST_PCT}%)"
elif [ "$TOTAL_TESTS" != "?" ] && [ "$TEST_PASSED" != "?" ]; then
    TEST_STATS="${TEST_PASSED}/${TOTAL_TESTS}"
else
    TEST_STATS="${TEST_PASSED}"
fi

# QA Status with caching (5-minute TTL)
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/asciidoc_artisan"
CACHE_FILE="$CACHE_DIR/qa_status.cache"
CACHE_TTL=300  # 5 minutes

mkdir -p "$CACHE_DIR"

# Check if cache is valid
CACHE_VALID=0
if [ -f "$CACHE_FILE" ]; then
    CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)))
    if [ "$CACHE_AGE" -lt "$CACHE_TTL" ]; then
        CACHE_VALID=1
    fi
fi

if [ "$CACHE_VALID" -eq 1 ]; then
    # Read from cache
    source "$CACHE_FILE"
else
    # Run expensive checks and cache results
    MYPY_STATUS=$(mypy src --strict 2>&1 | grep -q "Success" && echo "✓" || echo "✗")
    RUFF_STATUS=$(ruff check src 2>&1 | grep -q "All checks passed" && echo "✓" || echo "✗")

    # Write to cache
    cat > "$CACHE_FILE" << EOF
MYPY_STATUS="$MYPY_STATUS"
RUFF_STATUS="$RUFF_STATUS"
EOF
fi

# Architecture optimization status
if [[ "$CPU_ARCH" == "arm64" ]]; then
    ARCH_INFO="ARM64"
    OPTIMIZED="✓"
elif [[ "$CPU_ARCH" == "x86_64" ]]; then
    ARCH_INFO="x86_64"
    OPTIMIZED="✓"
else
    ARCH_INFO="$CPU_ARCH"
    OPTIMIZED="—"
fi

# OS name
OS_NAME=$(uname -s)

# Build status line with all information
cat << EOF
${BOLD}${BLUE}┏━━ ${PROJECT_NAME} v${PROJECT_VERSION}${RESET}
${DIM}├─ Git${RESET}: ${GREEN}${GIT_BRANCH}${RESET} │ ${YELLOW}±${GIT_STATUS}${RESET} │ ↑${GIT_AHEAD} ↓${GIT_BEHIND}
${DIM}├─ Env${RESET}: Python ${PYTHON_VERSION} │ venv:${VENV_ACTIVE} │ ${ARCH_INFO} (opt:${OPTIMIZED})
${DIM}├─ QA ${RESET}: Tests:${TEST_STATS} │ mypy:${MYPY_STATUS} │ ruff:${RUFF_STATUS}
${DIM}└─ OS ${RESET}: ${OS_NAME} ${OS_VERSION} │ $(date +"%H:%M:%S")
EOF
