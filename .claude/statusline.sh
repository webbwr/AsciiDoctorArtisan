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
PROJECT_VERSION="2.0.0"

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
VENV_ACTIVE=$([ -n "$VIRTUAL_ENV" ] && echo "✓" || echo "✗")

# Test statistics (from last run)
# Try multiple sources in order of reliability: status.json > coverage.xml > index.html
if [ -f htmlcov/status.json ]; then
    COVERAGE=$(python3 -c "
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
" 2>/dev/null)
    [ -z "$COVERAGE" ] && COVERAGE="?"
elif [ -f coverage.xml ]; then
    COVERAGE=$(python3 -c "import xml.etree.ElementTree as ET; tree=ET.parse('coverage.xml'); root=tree.getroot(); rate=float(root.attrib.get('line-rate', 0))*100; print(f'{rate:.1f}')" 2>/dev/null)
    [ -z "$COVERAGE" ] && COVERAGE="?"
elif [ -f htmlcov/index.html ]; then
    COVERAGE=$(grep -o "[0-9]*%" htmlcov/index.html 2>/dev/null | head -1 | tr -d '%')
    [ -z "$COVERAGE" ] && COVERAGE="?"
else
    COVERAGE="?"
fi

# Get test statistics from .pytest_cache (most reliable)
if [ -f .pytest_cache/v/cache/nodeids ]; then
    TOTAL_TESTS=$(python3 -c "import json; print(len(json.load(open('.pytest_cache/v/cache/nodeids'))))" 2>/dev/null || echo "?")
else
    TOTAL_TESTS="?"
fi

# Get passed tests from multiple sources (in order of preference)
TEST_PASSED=""

# 1. Try test_run_fast.log (most recent full run)
if [ -f test_run_fast.log ]; then
    TEST_PASSED=$(grep -o "[0-9]* passed" test_run_fast.log 2>/dev/null | tail -1 | cut -d' ' -f1)
fi

# 2. Try .pytest_cache/v/cache/lastfailed (calculate passed = total - failed)
if [ -z "$TEST_PASSED" ] && [ -f .pytest_cache/v/cache/lastfailed ]; then
    FAILED_COUNT=$(python3 -c "import json; print(len(json.load(open('.pytest_cache/v/cache/lastfailed'))))" 2>/dev/null || echo "")
    if [ -n "$FAILED_COUNT" ] && [ "$TOTAL_TESTS" != "?" ]; then
        TEST_PASSED=$((TOTAL_TESTS - FAILED_COUNT))
    fi
fi

# 3. Try htmlcov/index.html (old coverage report)
if [ -z "$TEST_PASSED" ]; then
    TEST_PASSED=$(grep -o "[0-9]* passed" htmlcov/index.html 2>/dev/null | head -1 | cut -d' ' -f1)
fi

# 4. Default to unknown
if [ -z "$TEST_PASSED" ]; then
    TEST_PASSED="?"
fi

# Format as "passed/total"
if [ "$TOTAL_TESTS" != "?" ] && [ "$TEST_PASSED" != "?" ]; then
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
    MYPY_STATUS=$(mypy src/asciidoc_artisan --strict 2>&1 | grep -q "Success" && echo "✓" || echo "✗")
    RUFF_STATUS=$(ruff check src/asciidoc_artisan 2>&1 | grep -q "All checks passed" && echo "✓" || echo "✗")

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
${DIM}├─ QA ${RESET}: Tests:${TEST_STATS} (${COVERAGE}%) │ mypy:${MYPY_STATUS} │ ruff:${RUFF_STATUS}
${DIM}└─ OS ${RESET}: ${OS_NAME} ${OS_VERSION} │ $(date +"%H:%M:%S")
EOF
