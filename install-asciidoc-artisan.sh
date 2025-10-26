#!/bin/bash
# AsciiDoc Artisan - Full Clean Installation Script for Mac/Linux
# This script performs a complete installation with dependency validation

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.11"
REQUIRED_PYTHON_PACKAGES=(
    "PySide6>=6.9.0"
    "asciidoc3>=3.2.0"
    "pypandoc>=1.11"
    "pdfplumber>=0.10.0"
    "keyring>=24.0.0"
    "psutil>=5.9.0"
)

# Track validation results
ERRORS=0
WARNINGS=0

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Version comparison function
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Step 1: Detect OS
print_header "Step 1: Detecting Operating System"

OS_TYPE=$(uname -s)
case "$OS_TYPE" in
    Darwin*)
        OS_NAME="macOS"
        PACKAGE_MANAGER="brew"
        print_success "Detected: macOS"
        ;;
    Linux*)
        OS_NAME="Linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS_NAME="$NAME"
        fi
        # Detect package manager
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        else
            PACKAGE_MANAGER="unknown"
        fi
        print_success "Detected: $OS_NAME"
        ;;
    *)
        print_error "Unsupported operating system: $OS_TYPE"
        exit 1
        ;;
esac

print_info "Package manager: $PACKAGE_MANAGER"

# Step 2: Check Python installation
print_header "Step 2: Checking Python Installation"

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
            print_warning "Found Python $PYTHON_VERSION (too old, need >= $PYTHON_MIN_VERSION)"
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python $PYTHON_MIN_VERSION or higher not found"
    echo ""
    echo "Installation instructions:"
    if [ "$OS_NAME" = "macOS" ]; then
        echo "  brew install python@3.12"
    elif [ "$PACKAGE_MANAGER" = "apt" ]; then
        echo "  sudo apt update"
        echo "  sudo apt install python3.12 python3.12-venv python3-pip"
    else
        echo "  Please install Python $PYTHON_MIN_VERSION or higher from python.org"
    fi
    exit 1
fi

# Step 3: Check pip
print_header "Step 3: Checking pip Installation"

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip not found for $PYTHON_CMD"
    echo ""
    echo "Installing pip..."
    if [ "$OS_NAME" = "macOS" ]; then
        $PYTHON_CMD -m ensurepip --upgrade
    elif [ "$PACKAGE_MANAGER" = "apt" ]; then
        sudo apt install python3-pip
    fi

    # Verify pip installation
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_error "Failed to install pip"
        exit 1
    fi
fi

PIP_VERSION=$($PYTHON_CMD -m pip --version 2>&1 | awk '{print $2}')
print_success "pip $PIP_VERSION found"

# Step 4: Check system dependencies
print_header "Step 4: Checking System Dependencies"

# Check Pandoc
if command -v pandoc &> /dev/null; then
    PANDOC_VERSION=$(pandoc --version | head -n1 | awk '{print $2}')
    print_success "Pandoc $PANDOC_VERSION found"
else
    print_warning "Pandoc not found (required for document conversion)"
    echo ""
    echo "Installing Pandoc..."
    if [ "$OS_NAME" = "macOS" ]; then
        if command -v brew &> /dev/null; then
            brew install pandoc
        else
            print_error "Homebrew not found. Install from: https://pandoc.org/installing.html"
        fi
    elif [ "$PACKAGE_MANAGER" = "apt" ]; then
        sudo apt update
        sudo apt install pandoc -y
    elif [ "$PACKAGE_MANAGER" = "dnf" ] || [ "$PACKAGE_MANAGER" = "yum" ]; then
        sudo $PACKAGE_MANAGER install pandoc -y
    else
        print_warning "Please install Pandoc manually from: https://pandoc.org/installing.html"
    fi

    # Verify installation
    if command -v pandoc &> /dev/null; then
        PANDOC_VERSION=$(pandoc --version | head -n1 | awk '{print $2}')
        print_success "Pandoc $PANDOC_VERSION installed successfully"
    else
        print_warning "Pandoc installation failed - document conversion features will be limited"
    fi
fi

# Check Git (optional but recommended)
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    print_success "Git $GIT_VERSION found"
else
    print_warning "Git not found (optional - needed for Git integration features)"
    echo "  Install from: https://git-scm.com/downloads"
fi

# Step 5: Create virtual environment (optional but recommended)
print_header "Step 5: Virtual Environment Setup"

read -p "Create virtual environment? (recommended) [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_info "Creating virtual environment in ./venv"
    $PYTHON_CMD -m venv venv

    # Activate virtual environment
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
        print_success "Virtual environment created and activated"
        PYTHON_CMD="python"  # Use venv python
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_warning "Skipping virtual environment (installing globally)"
fi

# Step 6: Install Python dependencies
print_header "Step 6: Installing Python Dependencies"

print_info "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --quiet

if [ -f "requirements-production.txt" ]; then
    print_info "Installing from requirements-production.txt..."
    $PYTHON_CMD -m pip install -r requirements-production.txt --quiet
    print_success "Production dependencies installed"
elif [ -f "requirements.txt" ]; then
    print_info "Installing from requirements.txt..."
    $PYTHON_CMD -m pip install -r requirements.txt --quiet
    print_success "Dependencies installed"
else
    print_info "Installing core packages..."
    for package in "${REQUIRED_PYTHON_PACKAGES[@]}"; do
        print_info "Installing $package..."
        $PYTHON_CMD -m pip install "$package" --quiet
    done
    print_success "Core packages installed"
fi

# Step 7: Run post-install tasks
print_header "Step 7: Post-Installation Tasks"

# Run asciidoc3 post-install if available
if command -v asciidoc3_postinstall &> /dev/null; then
    print_info "Running asciidoc3 post-install..."
    asciidoc3_postinstall &> /dev/null || true
    print_success "asciidoc3 configured"
else
    print_warning "asciidoc3_postinstall not found in PATH"
fi

# Step 8: Validation
print_header "Step 8: Validating Installation"

# Validate Python packages
print_info "Checking installed packages..."
for package in "${REQUIRED_PYTHON_PACKAGES[@]}"; do
    PACKAGE_NAME=$(echo "$package" | cut -d'>' -f1 | cut -d'=' -f1)
    if $PYTHON_CMD -c "import $PACKAGE_NAME" 2> /dev/null || \
       $PYTHON_CMD -c "import ${PACKAGE_NAME//-/_}" 2> /dev/null; then
        VERSION=$($PYTHON_CMD -m pip show "$PACKAGE_NAME" 2>/dev/null | grep Version | awk '{print $2}')
        print_success "$PACKAGE_NAME $VERSION"
    else
        print_error "$PACKAGE_NAME not found or cannot be imported"
    fi
done

# Validate system commands
print_info "Checking system commands..."
COMMANDS=("$PYTHON_CMD" "pip" "pandoc" "git")
for cmd in "${COMMANDS[@]}"; do
    if [ "$cmd" = "git" ] || [ "$cmd" = "pandoc" ]; then
        # Optional dependencies
        if command -v $cmd &> /dev/null; then
            print_success "$cmd: $(which $cmd)"
        else
            print_warning "$cmd: not found (optional)"
        fi
    else
        # Required dependencies
        if command -v $cmd &> /dev/null; then
            print_success "$cmd: $(which $cmd)"
        else
            print_error "$cmd: not found (required)"
        fi
    fi
done

# Test application launch
print_info "Testing application import..."
if $PYTHON_CMD -c "from asciidoc_artisan.ui.main_window import AsciiDocEditor" 2> /dev/null; then
    print_success "Application modules can be imported"
else
    print_warning "Application modules not yet installed (run: pip install -e .)"
fi

# Step 9: Summary
print_header "Installation Summary"

echo "Python Version:    $($PYTHON_CMD --version)"
echo "Python Location:   $(which $PYTHON_CMD)"
echo "Pip Version:       $($PYTHON_CMD -m pip --version | awk '{print $2}')"
echo ""
echo "Errors:            $ERRORS"
echo "Warnings:          $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    print_success "Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Launch the application:"
    echo "     ./launch-asciidoc-artisan-gui.sh"
    echo "  2. Or run directly:"
    echo "     $PYTHON_CMD src/main.py"
    echo ""
    if [ -d "venv" ]; then
        echo "  Note: Virtual environment is active. To deactivate:"
        echo "     deactivate"
        echo ""
        echo "  To reactivate later:"
        echo "     source venv/bin/activate"
        echo ""
    fi
    exit 0
else
    print_error "Installation completed with $ERRORS errors"
    echo ""
    echo "Please resolve the errors above and try again."
    exit 1
fi
