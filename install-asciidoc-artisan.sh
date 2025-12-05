#!/bin/bash
# AsciiDoc Artisan Installation Script for Mac/Linux
# VERSION: 2.1.0
# Usage: chmod +x install-asciidoc-artisan.sh && ./install-asciidoc-artisan.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PYTHON_MIN_VERSION="3.11"
ERRORS=0
WARNINGS=0

print_header() { echo -e "\n${BLUE}=== $1 ===${NC}\n"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; WARNINGS=$((WARNINGS + 1)); }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

version_ge() { [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]; }

# Step 1: Detect OS
print_header "Detecting Operating System"
OS_TYPE=$(uname -s)
case "$OS_TYPE" in
    Darwin*)
        OS_NAME="macOS"
        PACKAGE_MANAGER="brew"
        print_success "Detected: macOS"
        ;;
    Linux*)
        OS_NAME="Linux"
        [ -f /etc/os-release ] && . /etc/os-release && OS_NAME="$NAME"
        if command -v apt-get &> /dev/null; then PACKAGE_MANAGER="apt"
        elif command -v dnf &> /dev/null; then PACKAGE_MANAGER="dnf"
        elif command -v yum &> /dev/null; then PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then PACKAGE_MANAGER="pacman"
        else PACKAGE_MANAGER="unknown"
        fi
        print_success "Detected: $OS_NAME ($PACKAGE_MANAGER)"
        ;;
    *)
        print_error "Unsupported OS: $OS_TYPE"
        exit 1
        ;;
esac

# Step 2: Find Python 3.11+
print_header "Checking Python Installation"
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON_VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)
        if version_ge "$PYTHON_MAJOR_MINOR" "$PYTHON_MIN_VERSION"; then
            PYTHON_CMD=$cmd
            print_success "Found Python $PYTHON_VERSION at $(which $cmd)"
            break
        else
            print_warning "Found Python $PYTHON_VERSION (need >= $PYTHON_MIN_VERSION)"
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python $PYTHON_MIN_VERSION+ not found"
    echo ""
    echo "Install Python:"
    case "$OS_NAME" in
        macOS) echo "  brew install python@3.12" ;;
        *) echo "  sudo apt install python3.12 python3.12-venv python3-pip" ;;
    esac
    exit 1
fi

# Step 3: Verify pip
print_header "Checking pip"
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_info "Installing pip..."
    case "$OS_NAME" in
        macOS) $PYTHON_CMD -m ensurepip --upgrade ;;
        *) sudo apt install python3-pip -y ;;
    esac
fi
PIP_VERSION=$($PYTHON_CMD -m pip --version 2>&1 | awk '{print $2}')
print_success "pip $PIP_VERSION"

# Step 4: Install system dependencies
print_header "Installing System Dependencies"

# Pandoc (required)
if ! command -v pandoc &> /dev/null; then
    print_info "Installing Pandoc..."
    case "$PACKAGE_MANAGER" in
        brew) brew install pandoc ;;
        apt) sudo apt update && sudo apt install pandoc -y ;;
        dnf|yum) sudo $PACKAGE_MANAGER install pandoc -y ;;
        pacman) sudo pacman -S pandoc --noconfirm ;;
        *) print_warning "Install Pandoc manually: https://pandoc.org/installing.html" ;;
    esac
fi
command -v pandoc &> /dev/null && print_success "Pandoc $(pandoc --version | head -n1 | awk '{print $2}')" || print_warning "Pandoc not installed"

# wkhtmltopdf (required for PDF export)
if ! command -v wkhtmltopdf &> /dev/null; then
    print_info "Installing wkhtmltopdf..."
    case "$PACKAGE_MANAGER" in
        brew) brew install wkhtmltopdf ;;
        apt) sudo apt install wkhtmltopdf -y ;;
        dnf|yum) sudo $PACKAGE_MANAGER install wkhtmltopdf -y ;;
        pacman) sudo pacman -S wkhtmltopdf --noconfirm ;;
        *) print_warning "Install wkhtmltopdf manually" ;;
    esac
fi
command -v wkhtmltopdf &> /dev/null && print_success "wkhtmltopdf installed" || print_warning "wkhtmltopdf not installed (PDF export disabled)"

# Git (optional)
command -v git &> /dev/null && print_success "Git $(git --version | awk '{print $3}')" || print_warning "Git not installed (optional)"

# GitHub CLI (optional)
command -v gh &> /dev/null && print_success "GitHub CLI installed" || print_info "GitHub CLI not installed (optional: sudo apt install gh)"

# Step 5: Virtual environment
print_header "Virtual Environment Setup"
read -p "Create virtual environment? (recommended) [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_info "Creating venv..."
    $PYTHON_CMD -m venv venv
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
        PYTHON_CMD="python"
        print_success "Virtual environment created and activated"
    else
        print_error "Failed to create venv"
        exit 1
    fi
else
    print_warning "Installing globally (not recommended)"
fi

# Step 6: Install Python packages
print_header "Installing Python Dependencies"
$PYTHON_CMD -m pip install --upgrade pip --quiet

if [ -f "requirements-prod.txt" ]; then
    print_info "Installing from requirements-prod.txt..."
    $PYTHON_CMD -m pip install -r requirements-prod.txt --quiet
    print_success "Production dependencies installed"
elif [ -f "requirements.txt" ]; then
    print_info "Installing from requirements.txt..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet
    print_success "Dependencies installed"
else
    print_info "Installing core packages..."
    $PYTHON_CMD -m pip install "PySide6>=6.9.0" "asciidoc3>=3.2.0" "pypandoc>=1.11" "pymupdf>=1.26.0" "keyring>=24.0.0" "psutil>=5.9.0" --quiet
    print_success "Core packages installed"
fi

# Step 7: Validate installation
print_header "Validating Installation"

# Check key packages
for pkg in PySide6 asciidoc3 pypandoc fitz keyring psutil; do
    if $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
        print_success "$pkg"
    else
        print_error "$pkg not importable"
    fi
done

# Test application import
if $PYTHON_CMD -c "from asciidoc_artisan.ui.main_window import AsciiDocEditor" 2>/dev/null; then
    print_success "Application modules verified"
else
    print_warning "Run 'pip install -e .' for editable install"
fi

# Summary
print_header "Installation Summary"
echo "Python:   $($PYTHON_CMD --version)"
echo "Location: $(which $PYTHON_CMD)"
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    print_success "Installation complete!"
    echo ""
    echo "Run the application:"
    echo "  ./run.sh              # Optimized mode"
    echo "  python3 src/main.py   # Normal mode"
    echo ""
    [ -d "venv" ] && echo "Reactivate venv: source venv/bin/activate"
    exit 0
else
    print_error "Installation failed with $ERRORS errors"
    exit 1
fi
