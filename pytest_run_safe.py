#!/usr/bin/env python3
"""
Safe pytest runner that avoids QtWebEngine initialization.

This script runs pytest with coverage while ensuring QtWebEngine
doesn't get initialized (which causes fork crashes).
"""

import os
import sys

# Disable problematic components BEFORE importing anything
os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["DISABLE_QTWEBENGINE_IN_TESTS"] = "1"

# Only run unit tests (integration tests may start Qt apps)
sys.exit(os.system("pytest tests/unit -q --tb=short --maxfail=5"))
