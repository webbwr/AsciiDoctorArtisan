# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AsciiDoc Artisan.

Build commands:
  Linux:   pyinstaller asciidoc_artisan.spec
  macOS:   pyinstaller asciidoc_artisan.spec
  Windows: pyinstaller asciidoc_artisan.spec

Output: dist/AsciiDocArtisan/
"""

import sys
from pathlib import Path

# Application metadata
APP_NAME = "AsciiDocArtisan"
APP_VERSION = "2.1.0"
MAIN_SCRIPT = "src/main.py"

# Determine platform
is_windows = sys.platform == "win32"
is_macos = sys.platform == "darwin"
is_linux = sys.platform.startswith("linux")

# Data files to include
datas = [
    ("src/asciidoc_artisan/templates", "asciidoc_artisan/templates"),
    ("LICENSE", "."),
    ("README.md", "."),
]

# Hidden imports required by PySide6 and dependencies
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineCore",
    "PySide6.QtNetwork",
    "PySide6.QtPrintSupport",
    "asciidoc_artisan.core",
    "asciidoc_artisan.ui",
    "asciidoc_artisan.workers",
    "asciidoc_artisan.claude",
    "asciidoc_artisan.lsp",
    "keyring.backends",
    "keyrings.alt",
    "ollama",
    "anthropic",
    "pydantic",
    "orjson",
    "xxhash",
    "rapidfuzz",
    "qasync",
    "aiofiles",
    "pymupdf",
    "pypandoc",
]

# Exclude unnecessary modules to reduce size
excludes = [
    "tkinter",
    "matplotlib",
    "scipy",
    "numpy.testing",
    "PIL.ImageTk",
    "test",
    "unittest",
    "pytest",
]

# Analysis
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

# Remove duplicate binaries/datas
pyz = PYZ(a.pure)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico" if is_windows else ("assets/icon.icns" if is_macos else None),
)

# Collect all files
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# macOS app bundle
if is_macos:
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon="assets/icon.icns",
        bundle_identifier="com.webbwr.asciidocartisan",
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": "AsciiDoc Artisan",
            "CFBundleVersion": APP_VERSION,
            "CFBundleShortVersionString": APP_VERSION,
            "CFBundleIdentifier": "com.webbwr.asciidocartisan",
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,  # Support dark mode
            "LSMinimumSystemVersion": "11.0",
        },
    )
