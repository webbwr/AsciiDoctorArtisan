"""
Setup script for AsciiDoc Artisan

Modern Python packaging following PEP 517/518 standards.
"""

import sys
from pathlib import Path

from setuptools import find_packages, setup

if sys.version_info < (3, 14):
    sys.exit("Error: Requires Python 3.14+")

BASE_DIR = Path(__file__).parent

try:
    long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "Modern, feature-rich AsciiDoc editor with live preview"

try:
    requirements = [
        line.strip()
        for line in (BASE_DIR / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
except FileNotFoundError:
    requirements = ["PySide6>=6.9.0", "asciidoc3>=3.2.0", "pypandoc>=1.11"]

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

extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="asciidoc-artisan",
    version="2.0.0",
    author="AsciiDoc Artisan Team",
    author_email="support@asciidoc-artisan.org",
    description="Modern, feature-rich AsciiDoc editor with live preview",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webbwr/AsciiDoctorArtisan",
    project_urls={
        "Bug Tracker": "https://github.com/webbwr/AsciiDoctorArtisan/issues",
        "Documentation": "https://asciidoc-artisan.readthedocs.io",
        "Source Code": "https://github.com/webbwr/AsciiDoctorArtisan",
        "Changelog": "https://github.com/webbwr/AsciiDoctorArtisan/blob/main/CHANGELOG.md",
    },
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
    entry_points={
        "console_scripts": [
            "asciidoc-artisan=src.main:main",
            "ada=src.main:main",
        ],
        "gui_scripts": [
            "asciidoc-artisan-gui=src.main:main",
        ],
    },
    python_requires=">=3.14",
    install_requires=requirements,
    extras_require=extras_require,
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
        "Programming Language :: Python :: 3.14",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Text Editors",
        "Topic :: Text Processing :: Markup",
        "Typing :: Typed",
    ],
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
    platforms=["any"],
    license="MIT",
    license_files=["LICENSE"],
    test_suite="tests",
    tests_require=["pytest>=7.4.0", "pytest-qt>=4.2.0"],
    zip_safe=False,
)
