#!/usr/bin/env bash
# AsciiDoc Artisan Setup Script for Linux/WSL
# Installs all dependencies required for the AsciiDoc Artisan application

set -e  # Exit on error

echo "========================================"
echo "AsciiDoc Artisan - Dependency Setup"
echo "========================================"
echo ""

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${YELLOW}✗${NC} $1 is not installed"
        return 1
    fi
}

install_system_deps() {
    echo -e "${BLUE}Step 1: Installing system dependencies...${NC}"

    # Check if we have sudo
    if ! command -v sudo &> /dev/null; then
        echo -e "${RED}Error: sudo not found. Please install packages manually.${NC}"
        exit 1
    fi

    # Update package lists
    echo "Updating package lists..."
    echo "7861" | sudo -S apt update -qq

    # Install required system packages
    echo "Installing git, pandoc, python3, and pip..."
    echo "7861" | sudo -S apt install -y \
        git \
        pandoc \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libgl1-mesa-glx \
        libxkbcommon-x11-0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xinerama0 \
        libxcb-xfixes0

    echo -e "${GREEN}✓ System dependencies installed${NC}"
}

install_python_deps() {
    echo -e "${BLUE}Step 2: Installing Python packages...${NC}"

    # Upgrade pip first
    python3 -m pip install --upgrade pip --quiet

    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "Installing Python packages from requirements.txt..."
        python3 -m pip install -r requirements.txt --user --upgrade
        echo -e "${GREEN}✓ Python packages installed${NC}"
    else
        echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
        echo "Installing packages individually..."
        python3 -m pip install --user --upgrade PySide6>=6.9.0
        python3 -m pip install --user --upgrade asciidoc3
        python3 -m pip install --user --upgrade pypandoc
    fi

    # Run asciidoc3 post-install if available
    if command -v asciidoc3_postinstall &> /dev/null; then
        echo "Running asciidoc3 post-install..."
        asciidoc3_postinstall
    fi
}

verify_installation() {
    echo ""
    echo -e "${BLUE}Step 3: Verifying installation...${NC}"
    echo ""

    # Check system commands
    check_command git
    check_command pandoc
    check_command python3
    check_command pip3

    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

    # Check Python packages
    echo ""
    echo "Python Packages:"

    if python3 -m pip show PySide6 &> /dev/null; then
        PYSIDE_VERSION=$(python3 -m pip show PySide6 | grep "^Version:" | cut -d' ' -f2)
        echo -e "${GREEN}✓${NC} PySide6: $PYSIDE_VERSION"
    else
        echo -e "${RED}✗${NC} PySide6: NOT INSTALLED"
    fi

    if python3 -m pip show asciidoc3 &> /dev/null; then
        ASCIIDOC_VERSION=$(python3 -m pip show asciidoc3 | grep "^Version:" | cut -d' ' -f2)
        echo -e "${GREEN}✓${NC} asciidoc3: $ASCIIDOC_VERSION"
    else
        echo -e "${RED}✗${NC} asciidoc3: NOT INSTALLED"
    fi

    if python3 -m pip show pypandoc &> /dev/null; then
        PYPANDOC_VERSION=$(python3 -m pip show pypandoc | grep "^Version:" | cut -d' ' -f2)
        echo -e "${GREEN}✓${NC} pypandoc: $PYPANDOC_VERSION"
    else
        echo -e "${RED}✗${NC} pypandoc: NOT INSTALLED"
    fi

    # Check if asciidoc3 command is available
    echo ""
    if check_command asciidoc3; then
        ASCIIDOC_CMD_VERSION=$(asciidoc3 --version 2>&1 | head -1)
        echo "  Version: $ASCIIDOC_CMD_VERSION"
    else
        echo -e "${YELLOW}Note: asciidoc3 command not in PATH. You may need to add ~/.local/bin to PATH${NC}"
        echo -e "${YELLOW}Add this to your ~/.bashrc:${NC}"
        echo -e "${YELLOW}  export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    fi
}

add_to_path() {
    echo ""
    echo -e "${BLUE}Step 4: Checking PATH configuration...${NC}"

    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}~/.local/bin is not in your PATH${NC}"
        echo "Adding to ~/.bashrc..."
        echo '' >> ~/.bashrc
        echo '# Add Python user scripts to PATH' >> ~/.bashrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo -e "${GREEN}✓ Added ~/.local/bin to PATH in ~/.bashrc${NC}"
        echo -e "${YELLOW}IMPORTANT: Run 'source ~/.bashrc' or restart your terminal${NC}"
    else
        echo -e "${GREEN}✓ ~/.local/bin is already in PATH${NC}"
    fi
}

# Main execution
echo "This script will install:"
echo "  - Git (version control)"
echo "  - Pandoc (document converter)"
echo "  - Python 3 + pip"
echo "  - PySide6 (Qt GUI framework)"
echo "  - asciidoc3 (AsciiDoc processor)"
echo "  - pypandoc (Python Pandoc interface)"
echo ""
echo "Press Ctrl+C to cancel, or Enter to continue..."
read -r

# Run installation steps
install_system_deps
install_python_deps
verify_installation
add_to_path

echo ""
echo "========================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run: source ~/.bashrc  (or restart your terminal)"
echo "  2. Verify: ./verify.sh"
echo "  3. Check: python3 --version && asciidoc3 --version"
echo ""
echo "To use the AsciiDoc Artisan application:"
echo "  - Ensure adp.py is in the project"
echo "  - Run: python3 adp.py"
echo ""
