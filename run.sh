#!/bin/bash
# AsciiDoc Artisan Optimized Launcher
# Runs Python with -OO flag to strip docstrings and __debug__ code for better performance

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run Python with optimization flags:
# -OO: Remove docstrings and assertions (maximum optimization)
#      - Strips __doc__ attributes (saves memory)
#      - Removes assert statements (faster execution)
#      - Disables __debug__ checks
exec python3 -OO src/main.py "$@"
