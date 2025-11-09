#!/bin/bash
#
# Claude Code Detailed Status Line
# Provides comprehensive context for minimal-verbosity mode
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
TEST_STATS=$(grep -o "[0-9]* passed" htmlcov/index.html 2>/dev/null | cut -d' ' -f1 || echo "?")
COVERAGE=$(grep -o "[0-9]*%" htmlcov/index.html 2>/dev/null | head -1 | tr -d '%' || echo "?")

# Type checking status
MYPY_STATUS=$(mypy src/asciidoc_artisan --strict 2>&1 | grep -q "Success" && echo "✓" || echo "✗")

# Linting status
RUFF_STATUS=$(ruff check src/asciidoc_artisan 2>&1 | grep -q "All checks passed" && echo "✓" || echo "✗")

# macOS optimization status
if [[ "$CPU_ARCH" == "arm64" ]]; then
    ARCH_INFO="Apple Silicon"
    OPTIMIZED="✓"
else
    ARCH_INFO="$CPU_ARCH"
    OPTIMIZED="—"
fi

# Build status line with all information
cat << EOF
${BOLD}${BLUE}┏━━ ${PROJECT_NAME} v${PROJECT_VERSION}${RESET}
${DIM}├─ Git${RESET}: ${GREEN}${GIT_BRANCH}${RESET} │ ${YELLOW}±${GIT_STATUS}${RESET} │ ↑${GIT_AHEAD} ↓${GIT_BEHIND}
${DIM}├─ Env${RESET}: Python ${PYTHON_VERSION} │ venv:${VENV_ACTIVE} │ ${ARCH_INFO} (opt:${OPTIMIZED})
${DIM}├─ QA ${RESET}: Tests:${TEST_STATS} (${COVERAGE}%) │ mypy:${MYPY_STATUS} │ ruff:${RUFF_STATUS}
${DIM}└─ OS ${RESET}: macOS ${OS_VERSION} │ $(date +"%H:%M:%S")
EOF
