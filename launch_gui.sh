#!/bin/bash
# AsciiDoc Artisan GUI Launcher for WSL2
#
# Supports three display methods:
# 1. WSLg (Windows 11 built-in) - auto-detected
# 2. VcXsrv/X410/Xming (external X Server on Windows)
# 3. QT_QPA_PLATFORM=offscreen (headless mode for testing)

echo "=== AsciiDoc Artisan GUI Launcher ==="
echo ""

# Function to test X connection
test_x_connection() {
    if command -v xset &> /dev/null; then
        if xset q &>/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Try Method 1: WSLg (Windows 11)
echo "Checking WSLg..."
if [ -S /tmp/.X11-unix/X0 ]; then
    export DISPLAY=:0
    export XDG_RUNTIME_DIR=/tmp/runtime-wsl
    export WAYLAND_DISPLAY=wayland-0
    echo "✓ WSLg detected, using DISPLAY=$DISPLAY"
    X_METHOD="WSLg"
elif [ -n "$WAYLAND_DISPLAY" ]; then
    echo "✓ Wayland display detected: $WAYLAND_DISPLAY"
    X_METHOD="Wayland"
else
    # Try Method 2: External X Server
    echo "WSLg not detected, trying external X Server..."
    export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0
    export LIBGL_ALWAYS_INDIRECT=1

    if test_x_connection; then
        echo "✓ External X Server connected at $DISPLAY"
        X_METHOD="External X Server"
    else
        echo "✗ No display available"
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
        echo "  export QT_QPA_PLATFORM=offscreen"
        echo "  python3 adp_windows.py"
        echo ""
        exit 1
    fi
fi

echo "Display configured: $DISPLAY"
echo "Method: $X_METHOD"
echo ""
echo "Launching AsciiDoc Artisan..."
echo ""

# Launch the application
cd /home/webbp/github/AsciiDoctorArtisan
python3 adp_windows.py

echo ""
echo "Application closed."
