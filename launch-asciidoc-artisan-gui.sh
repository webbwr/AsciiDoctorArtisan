#!/bin/bash
# AsciiDoc Artisan GUI Launcher for WSL2
#
# Supports three display methods:
# 1. WSLg (Windows 11 built-in) - auto-detected
# 2. VcXsrv/X410/Xming (external X Server on Windows)
# 3. QT_QPA_PLATFORM=offscreen (headless mode for testing)
#
# Usage: ./launch-asciidoc-artisan-gui.sh [OPTIONS]
# Options:
#   --debug       Enable debug mode with verbose logging
#   --headless    Run in headless mode (no display)
#   --check-only  Only check dependencies, don't launch
#   --help        Show this help message

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/launcher.log"
VENV_DIR="$PROJECT_DIR/venv"
MAIN_SCRIPT="$PROJECT_DIR/src/main.py"

# Parse command line arguments
DEBUG_MODE=false
HEADLESS_MODE=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        --headless)
            HEADLESS_MODE=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --help)
            echo "AsciiDoc Artisan GUI Launcher"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --debug       Enable debug mode with verbose logging"
            echo "  --headless    Run in headless mode (no display)"
            echo "  --check-only  Only check dependencies, don't launch"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Setup logging
mkdir -p "$LOG_DIR"
echo "=== Launch attempt at $(date) ===" >> "$LOG_FILE"

log_info() {
    echo "[INFO] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[ERROR] $1" | tee -a "$LOG_FILE" >&2
}

log_debug() {
    if [ "$DEBUG_MODE" = true ]; then
        echo "[DEBUG] $1" | tee -a "$LOG_FILE"
    fi
}

echo "=== AsciiDoc Artisan GUI Launcher ==="
echo ""

log_info "Script directory: $SCRIPT_DIR"
log_info "Project directory: $PROJECT_DIR"
log_debug "Debug mode: $DEBUG_MODE"
log_debug "Headless mode: $HEADLESS_MODE"

# Function to test X connection
test_x_connection() {
    if command -v xset &> /dev/null; then
        if xset q &>/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to check Python version
check_python_version() {
    log_info "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        return 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

    log_info "Python version: $PYTHON_VERSION"

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        log_error "Python 3.11+ required, found $PYTHON_VERSION"
        return 1
    fi

    log_info "✓ Python version OK"
    return 0
}

# Function to check virtual environment
check_virtual_env() {
    log_info "Checking virtual environment..."

    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found at: $VENV_DIR"
        log_info "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements-production.txt"
        return 1
    fi

    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        log_error "Virtual environment activation script not found"
        return 1
    fi

    log_info "✓ Virtual environment found"
    return 0
}

# Function to check required Python packages
check_dependencies() {
    log_info "Checking Python dependencies..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Map of package names to their import names
    # Format: "package_name:import_name"
    REQUIRED_PACKAGES=("PySide6:PySide6" "asciidoc3:asciidoc3" "pypandoc:pypandoc" "pymupdf:fitz")
    OPTIONAL_PACKAGES=("numba:numba")
    MISSING_PACKAGES=()
    MISSING_OPTIONAL=()

    for package_spec in "${REQUIRED_PACKAGES[@]}"; do
        IFS=':' read -r package import_name <<< "$package_spec"
        log_debug "Checking for $package (import as $import_name)..."
        if ! python3 -c "import $import_name" &> /dev/null; then
            MISSING_PACKAGES+=("$package")
            log_error "Missing required package: $package"
        else
            log_debug "✓ $package found"
        fi
    done

    for package_spec in "${OPTIONAL_PACKAGES[@]}"; do
        IFS=':' read -r package import_name <<< "$package_spec"
        log_debug "Checking for optional package: $package (import as $import_name)..."
        if ! python3 -c "import $import_name" &> /dev/null; then
            MISSING_OPTIONAL+=("$package")
            log_info "Optional package not installed: $package (performance may be reduced)"
        else
            log_debug "✓ $package found"
        fi
    done

    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        log_error "Missing required packages: ${MISSING_PACKAGES[*]}"
        log_info "Install with: pip install -r requirements-production.txt"
        return 1
    fi

    log_info "✓ All required dependencies installed"
    if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
        log_info "Note: Optional packages missing: ${MISSING_OPTIONAL[*]}"
    fi

    return 0
}

# Function to check system dependencies
check_system_dependencies() {
    log_info "Checking system dependencies..."

    MISSING_SYSTEM=()

    # Check pandoc
    if ! command -v pandoc &> /dev/null; then
        MISSING_SYSTEM+=("pandoc")
        log_error "pandoc not found"
    else
        PANDOC_VERSION=$(pandoc --version | head -n1)
        log_info "✓ $PANDOC_VERSION"
    fi

    # Check wkhtmltopdf
    if ! command -v wkhtmltopdf &> /dev/null; then
        MISSING_SYSTEM+=("wkhtmltopdf")
        log_error "wkhtmltopdf not found (PDF export will not work)"
    else
        log_info "✓ wkhtmltopdf found"
    fi

    # Check git (optional)
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        log_info "✓ $GIT_VERSION"
    else
        log_info "Git not found (version control features disabled)"
    fi

    if [ ${#MISSING_SYSTEM[@]} -gt 0 ]; then
        log_error "Missing system dependencies: ${MISSING_SYSTEM[*]}"
        log_info "Install with: sudo apt install ${MISSING_SYSTEM[*]}"
        return 1
    fi

    log_info "✓ System dependencies OK"
    return 0
}

# Function to detect GPU capabilities
check_gpu_support() {
    log_info "Checking GPU capabilities..."

    GPU_AVAILABLE=false
    GPU_INFO=""

    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1)
        if [ -n "$GPU_INFO" ]; then
            GPU_AVAILABLE=true
            log_info "✓ NVIDIA GPU detected: $GPU_INFO"
        fi
    fi

    # Check for AMD GPU
    if [ "$GPU_AVAILABLE" = false ] && command -v rocm-smi &> /dev/null; then
        GPU_INFO=$(rocm-smi --showproductname 2>/dev/null | grep "GPU" | head -n1)
        if [ -n "$GPU_INFO" ]; then
            GPU_AVAILABLE=true
            log_info "✓ AMD GPU detected: $GPU_INFO"
        fi
    fi

    # Check for Intel GPU
    if [ "$GPU_AVAILABLE" = false ] && [ -d "/sys/class/drm" ]; then
        if ls /sys/class/drm/card*/device/vendor 2>/dev/null | xargs cat 2>/dev/null | grep -q "0x8086"; then
            GPU_AVAILABLE=true
            GPU_INFO="Intel GPU"
            log_info "✓ Intel GPU detected"
        fi
    fi

    # Check OpenGL support
    if command -v glxinfo &> /dev/null; then
        OPENGL_VERSION=$(glxinfo 2>/dev/null | grep "OpenGL version" | cut -d':' -f2 | xargs)
        if [ -n "$OPENGL_VERSION" ]; then
            log_info "✓ OpenGL version: $OPENGL_VERSION"
            export QT_OPENGL=desktop
        else
            log_info "OpenGL not available, using software rendering"
            export QT_OPENGL=software
        fi
    else
        log_debug "glxinfo not available, cannot check OpenGL support"
    fi

    if [ "$GPU_AVAILABLE" = true ]; then
        log_info "✓ GPU acceleration available"
        export QT_ENABLE_HIGHDPI_SCALING=1
    else
        log_info "No GPU detected, using software rendering"
    fi

    return 0
}

# Run dependency checks
echo ""
log_info "=== Running Pre-flight Checks ==="
echo ""

CHECKS_FAILED=false

if ! check_python_version; then
    CHECKS_FAILED=true
fi

if ! check_virtual_env; then
    CHECKS_FAILED=true
fi

if ! check_dependencies; then
    CHECKS_FAILED=true
fi

if ! check_system_dependencies; then
    CHECKS_FAILED=true
fi

check_gpu_support

if [ "$CHECKS_FAILED" = true ]; then
    log_error "Pre-flight checks failed, cannot launch application"
    exit 1
fi

if [ "$CHECK_ONLY" = true ]; then
    log_info "All checks passed (--check-only mode, exiting)"
    exit 0
fi

echo ""
log_info "=== Configuring Display ==="
echo ""

# Configure display mode
if [ "$HEADLESS_MODE" = true ]; then
    log_info "Running in headless mode (--headless)"
    export QT_QPA_PLATFORM=offscreen
    X_METHOD="Headless"
else
    # Try Method 1: WSLg (Windows 11)
    log_info "Checking WSLg..."
    if [ -S /tmp/.X11-unix/X0 ]; then
        export DISPLAY=:0
        export XDG_RUNTIME_DIR=/tmp/runtime-wsl
        export WAYLAND_DISPLAY=wayland-0
        log_info "✓ WSLg detected, using DISPLAY=$DISPLAY"
        X_METHOD="WSLg"
    elif [ -n "$WAYLAND_DISPLAY" ]; then
        log_info "✓ Wayland display detected: $WAYLAND_DISPLAY"
        X_METHOD="Wayland"
    else
        # Try Method 2: External X Server
        log_info "WSLg not detected, trying external X Server..."
        export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0
        export LIBGL_ALWAYS_INDIRECT=1

        if test_x_connection; then
            log_info "✓ External X Server connected at $DISPLAY"
            X_METHOD="External X Server"
        else
            log_error "No display available"
            echo ""
            echo "Solutions:"
            echo ""
            echo "Option A - Windows 11 WSLg (Recommended):"
            echo "  1. Ensure Windows 11 is up to date"
            echo "  2. Run: wsl --update"
            echo "  3. Restart WSL: wsl --shutdown"
            echo ""
            echo "Option B - External X Server:"
            echo "  1. Install VcXsrv: https://sourceforge.net/projects/vcxsrv/"
            echo "  2. Run XLaunch with 'Disable access control' checked"
            echo "  3. Allow in Windows Firewall if prompted"
            echo ""
            echo "Option C - Run in headless mode (for testing):"
            echo "  $0 --headless"
            echo ""
            exit 1
        fi
    fi
fi

log_info "Display configured: ${DISPLAY:-N/A}"
log_info "Method: $X_METHOD"
echo ""

# Activate virtual environment
log_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
log_info "✓ Virtual environment activated"

# Change to project directory
cd "$PROJECT_DIR" || {
    log_error "Failed to change to project directory: $PROJECT_DIR"
    exit 1
}

echo ""
log_info "=== Launching AsciiDoc Artisan ==="
echo ""

# Set error handler
trap 'handle_error $? $LINENO' ERR

handle_error() {
    local exit_code=$1
    local line_number=$2
    log_error "Application exited with error code $exit_code at line $line_number"
    log_error "Check $LOG_FILE for details"
    exit $exit_code
}

# Launch the application
log_info "Starting application from: $MAIN_SCRIPT"
log_debug "Working directory: $(pwd)"
log_debug "Python: $(which python3)"
log_debug "DISPLAY: ${DISPLAY:-N/A}"
log_debug "QT_QPA_PLATFORM: ${QT_QPA_PLATFORM:-N/A}"

if [ "$DEBUG_MODE" = true ]; then
    log_info "Debug mode enabled, output will be verbose"
    python3 "$MAIN_SCRIPT" 2>&1 | tee -a "$LOG_FILE"
else
    python3 "$MAIN_SCRIPT" 2>> "$LOG_FILE"
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    log_info "Application closed normally"
else
    log_error "Application exited with code $EXIT_CODE"
    log_info "Check $LOG_FILE for details"
fi

exit $EXIT_CODE
