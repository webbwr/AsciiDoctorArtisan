#!/usr/bin/env bash
# AsciiDoc Artisan - Verification Script for Linux/WSL
# Verifies all dependencies are correctly installed

echo "========================================"
echo "AsciiDoc Artisan - Dependency Verification"
echo "========================================"
echo ""

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

OVERALL_STATUS=0

check_command() {
    local cmd=$1
    local required=${2:-true}

    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $cmd is installed"
        if [ "$cmd" = "python3" ]; then
            echo "  $(python3 --version)"
        elif [ "$cmd" = "git" ]; then
            echo "  $(git --version)"
        elif [ "$cmd" = "pandoc" ]; then
            echo "  $(pandoc --version | head -1)"
        elif [ "$cmd" = "asciidoc3" ]; then
            echo "  $(asciidoc3 --version 2>&1 | head -1)"
        fi
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $cmd is NOT installed (REQUIRED)"
            OVERALL_STATUS=1
        else
            echo -e "${YELLOW}⚠${NC} $cmd is NOT installed (optional)"
        fi
        return 1
    fi
}

check_python_package() {
    local pkg=$1
    local required=${2:-true}

    if python3 -m pip show "$pkg" &> /dev/null; then
        local version=$(python3 -m pip show "$pkg" | grep "^Version:" | cut -d' ' -f2)
        echo -e "${GREEN}✓${NC} $pkg: $version"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $pkg: NOT INSTALLED (REQUIRED)"
            OVERALL_STATUS=1
        else
            echo -e "${YELLOW}⚠${NC} $pkg: NOT INSTALLED (optional)"
        fi
        return 1
    fi
}

echo "System Commands:"
echo "----------------"
check_command python3 true
check_command pip3 true
check_command git true
check_command pandoc true
check_command asciidoc3 true

echo ""
echo "Python Packages:"
echo "----------------"
check_python_package PySide6 true
check_python_package asciidoc3 true
check_python_package pypandoc true

echo ""
echo "PATH Configuration:"
echo "-------------------"
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    echo -e "${GREEN}✓${NC} ~/.local/bin is in PATH"
else
    echo -e "${YELLOW}⚠${NC} ~/.local/bin is NOT in PATH"
    echo "  Add this to ~/.bashrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "  Then run: source ~/.bashrc"
fi

echo ""
echo "Python Environment:"
echo "-------------------"
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python: $PYTHON_VERSION"

PIP_VERSION=$(python3 -m pip --version 2>&1 | head -1)
echo "Pip: $PIP_VERSION"

# Check Python Scripts directory
USER_SCRIPTS=$(python3 -m site --user-base 2>/dev/null)/bin
if [ -d "$USER_SCRIPTS" ]; then
    echo "User Scripts Dir: $USER_SCRIPTS"
    if [ -f "$USER_SCRIPTS/asciidoc3" ]; then
        echo -e "${GREEN}✓${NC} asciidoc3 found in user scripts"
    else
        echo -e "${YELLOW}⚠${NC} asciidoc3 NOT found in user scripts"
    fi
else
    echo -e "${YELLOW}⚠${NC} User scripts directory not found"
fi

echo ""
echo "========================================"
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All critical dependencies verified!${NC}"
    echo ""
    echo "Environment is ready for AsciiDoc Artisan."
else
    echo -e "${RED}✗ Some dependencies are missing${NC}"
    echo ""
    echo "Please run ./setup.sh to install missing dependencies."
fi
echo "========================================"
echo ""

exit $OVERALL_STATUS
