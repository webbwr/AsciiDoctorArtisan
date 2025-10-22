#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for AsciiDoc Artisan

This script configures the package for distribution via PyPI or direct installation.
Follows modern Python packaging standards (PEP 517/518).
"""

import sys
from pathlib import Path

from setuptools import find_packages, setup

# Ensure minimum Python version
if sys.version_info < (3, 11):
    sys.exit("Error: AsciiDoc Artisan requires Python 3.11 or higher.")

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
try:
    long_description = readme_path.read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "A modern, feature-rich AsciiDoc editor with live preview."

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
try:
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback requirements if file not found
    requirements = [
        "PySide6>=6.9.0",
        "asciidoc3>=3.2.0",
        "pypandoc>=1.11",
    ]

# Optional dependencies for development
extras_require = {
    "dev": [
        "pytest>=7.4.0",
        "pytest-qt>=4.2.0",
        "pytest-cov>=4.1.0",
        "black>=23.0.0",
        "ruff>=0.1.0",
        "mypy>=1.5.0",
        "types-setuptools>=68.0.0",
    ],
    "docs": [
        "sphinx>=7.0.0",
        "sphinx-rtd-theme>=1.3.0",
        "sphinx-autodoc-typehints>=1.24.0",
    ],
    "build": [
        "pyinstaller>=6.0.0",
        "wheel>=0.41.0",
        "build>=1.0.0",
    ],
}

# All extra dependencies
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    # Package metadata
    name="asciidoc-artisan",
    version="2.0.0",
    author="AsciiDoc Artisan Team",
    author_email="support@asciidoc-artisan.org",
    description="A modern, feature-rich AsciiDoc editor with live preview",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webbwr/AsciiDoctorArtisan",
    project_urls={
        "Bug Tracker": "https://github.com/webbwr/AsciiDoctorArtisan/issues",
        "Documentation": "https://asciidoc-artisan.readthedocs.io",
        "Source Code": "https://github.com/webbwr/AsciiDoctorArtisan",
        "Changelog": "https://github.com/webbwr/AsciiDoctorArtisan/blob/main/CHANGELOG.md",
    },
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "asciidoc_artisan": [
            "resources/*.png",
            "resources/*.ico",
            "resources/*.json",
            "templates/*.adoc",
        ],
    },
    # Scripts and entry points
    entry_points={
        "console_scripts": [
            "asciidoc-artisan=asciidoc_artisan.main:main",
            "ada=asciidoc_artisan.main:main",  # Short alias
        ],
        "gui_scripts": [
            "asciidoc-artisan-gui=asciidoc_artisan.main:main",
        ],
    },
    # Dependencies
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require=extras_require,
    # PyPI classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Text Editors",
        "Topic :: Text Processing :: Markup",
        "Typing :: Typed",
    ],
    # Keywords for search
    keywords=[
        "asciidoc",
        "editor",
        "documentation",
        "markup",
        "preview",
        "qt",
        "pyside6",
        "git",
        "pandoc",
    ],
    # Platform specification
    platforms=["any"],
    # License
    license="MIT",
    license_files=["LICENSE"],
    # Testing
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.0",
        "pytest-qt>=4.2.0",
    ],
    # Build configuration
    zip_safe=False,  # Don't install as zip for resource access
)
