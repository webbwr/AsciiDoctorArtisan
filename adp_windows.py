#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AsciiDoc Artisan - Windows-Optimized Version
============================================

Enhanced for Windows with proper window management, dynamic screen sizing,
and improved file navigation.
"""

import sys
import io
import os
import subprocess
import shlex
import uuid
import tempfile
from pathlib import Path
from typing import Optional, Tuple, NamedTuple, List, Union, Any, Dict
import warnings
import html
import json
import logging
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QPlainTextEdit,
    QMessageBox,
    QFileDialog,
    QStatusBar,
    QTextBrowser,
    QInputDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
)
from PySide6.QtGui import (
    QAction,
    QPalette,
    QColor,
    QFont,
    QKeySequence,
    QGuiApplication,
    QScreen,
    QIcon,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QUrl,
    QStandardPaths,
    QObject,
    QThread,
    Signal,
    Slot,
    QRect,
    QSize,
)

# Optional dependencies and enhanced pandoc integration
try:
    import pypandoc
    PANDOC_AVAILABLE = True
except ImportError:
    logger.warning("pypandoc not found. Document conversion limited.")
    pypandoc = None
    PANDOC_AVAILABLE = False

# Import enhanced pandoc integration
try:
    from pandoc_integration import pandoc, ensure_pandoc_available
    ENHANCED_PANDOC = True
except ImportError:
    logger.warning("Enhanced pandoc integration not available")
    pandoc = None
    ensure_pandoc_available = None
    ENHANCED_PANDOC = False

try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API
    ASCIIDOC3_AVAILABLE = True
except ImportError:
    logger.warning("asciidoc3 not found. Live preview will use plain text.")
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

# Constants
APP_NAME = "AsciiDoc Artisan"
DEFAULT_FILENAME = "untitled.adoc"
PREVIEW_UPDATE_INTERVAL_MS = 350
EDITOR_FONT_FAMILY = "Consolas" if platform.system() == "Windows" else "Courier New"
EDITOR_FONT_SIZE = 12  # More reasonable default
MIN_FONT_SIZE = 8
ZOOM_STEP = 1
SETTINGS_FILENAME = "AsciiDocArtisan.json"

# File filters - Windows-friendly
ADOC_FILTER = "AsciiDoc Files (*.adoc *.asciidoc)"
DOCX_FILTER = "Microsoft Word 365 Documents (*.docx)"
PDF_FILTER = "Adobe Acrobat PDF Files (*.pdf)"
MD_FILTER = "GitHub Markdown Files (*.md *.markdown)"
HTML_FILTER = "HTML Files (*.html *.htm)"
LATEX_FILTER = "LaTeX Files (*.tex)"
RST_FILTER = "reStructuredText Files (*.rst)"
ORG_FILTER = "Org Mode Files (*.org)"
TEXTILE_FILTER = "Textile Files (*.textile)"
ALL_FILES_FILTER = "All Files (*)"

# Common formats for quick access
COMMON_FORMATS = "*.adoc *.asciidoc *.docx *.pdf *.md *.markdown *.html *.htm"
# All supported formats
ALL_FORMATS = "*.adoc *.asciidoc *.docx *.pdf *.md *.markdown *.html *.htm *.tex *.rst *.org *.textile"

SUPPORTED_OPEN_FILTER = f"Common Formats ({COMMON_FORMATS});;All Supported ({ALL_FORMATS});;{ADOC_FILTER};;{MD_FILTER};;{DOCX_FILTER};;{HTML_FILTER};;{LATEX_FILTER};;{RST_FILTER};;{PDF_FILTER};;{ALL_FILES_FILTER}"
SUPPORTED_SAVE_FILTER = f"{ADOC_FILTER};;{MD_FILTER};;{DOCX_FILTER};;{HTML_FILTER};;{PDF_FILTER};;{ALL_FILES_FILTER}"


class GitResult(NamedTuple):
    success: bool
    stdout: str
    stderr: str
    exit_code: Optional[int]
    user_message: str


class GitWorker(QObject):
    command_complete = Signal(GitResult)

    @Slot(list, str)
    def run_git_command(self, command: List[str], working_dir: str) -> None:
        user_message = "Git command failed."
        stdout, stderr = "", ""
        exit_code = None

        try:
            if not Path(working_dir).is_dir():
                user_message = f"Error: Git working directory not found: {working_dir}"
                self.command_complete.emit(GitResult(False, "", user_message, None, user_message))
                return

            logger.info(f"Executing Git: {' '.join(command)} in {working_dir}")

            # Windows-specific: Use shell=True for git commands on Windows
            shell = platform.system() == "Windows"

            process = subprocess.run(
                command if not shell else ' '.join(command),
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                shell=shell,
                encoding='utf-8',
                errors='replace',
            )

            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            if exit_code == 0:
                logger.info(f"Git command successful: {' '.join(command)}")
                result = GitResult(True, stdout, stderr, exit_code, "Git command successful.")
            else:
                user_message = self._analyze_git_error(stderr, command)
                logger.error(f"Git command failed (code {exit_code}): {user_message}")
                result = GitResult(False, stdout, stderr, exit_code, user_message)

            self.command_complete.emit(result)

        except FileNotFoundError:
            error_msg = "Git command not found. Ensure Git is installed and in system PATH."
            logger.error(error_msg)
            self.command_complete.emit(GitResult(False, "", error_msg, None, error_msg))
        except Exception as e:
            error_msg = f"Unexpected error running Git command: {e}"
            logger.exception("Unexpected Git error")
            self.command_complete.emit(GitResult(False, stdout, stderr or str(e), exit_code, error_msg))

    def _analyze_git_error(self, stderr: str, command: List[str]) -> str:
        stderr_lower = stderr.lower()

        if "authentication failed" in stderr_lower:
            return "Git Authentication Failed. Check credentials (SSH key/token/helper)."
        elif "not a git repository" in stderr_lower:
            return "Directory is not a Git repository."
        elif "resolve host" in stderr_lower:
            return "Could not connect to Git host. Check internet and repository URL."
        elif "nothing to commit" in stderr_lower:
            return "Nothing to commit."
        else:
            return f"Git command failed: {stderr[:200]}"


class PandocWorker(QObject):
    conversion_complete = Signal(str, str)
    conversion_error = Signal(str, str)

    @Slot(object, str, str, str, object)
    def run_pandoc_conversion(self, source: Union[str, bytes, Path], to_format: str, from_format: str, context: str, output_file: Optional[Path] = None) -> None:
        if not PANDOC_AVAILABLE or not pypandoc:
            err = "Pandoc/pypandoc not available for conversion."
            logger.error(err)
            self.conversion_error.emit(err, context)
            return

        try:
            logger.info(f"Starting Pandoc conversion ({context})")

            # Enhanced pandoc options for better AsciiDoc output
            extra_args = [
                '--wrap=preserve',          # Preserve line breaks
                '--reference-links',        # Use reference-style links
                '--standalone',            # Produce complete document
                '--toc-depth=3',          # Include TOC depth info
            ]

            # Add format-specific options
            if from_format == 'docx':
                extra_args.extend([
                    '--extract-media=.',   # Extract images from DOCX
                ])

            # Add output format-specific options
            if to_format == 'pdf':
                # Basic PDF options that work without LaTeX
                extra_args.extend([
                    '--variable=geometry:margin=1in',  # Standard margins
                    '--variable=fontsize=11pt',  # Readable font size
                    '--highlight-style=tango',  # Code highlighting
                ])
                # Try to find an available PDF engine
                import subprocess
                pdf_engines = [
                    'wkhtmltopdf',  # Popular HTML to PDF converter
                    'weasyprint',   # Python-based engine
                    'prince',       # Commercial but excellent
                    'pdflatex',     # LaTeX-based (default)
                    'xelatex',      # LaTeX variant
                    'lualatex',     # LaTeX variant
                    'context',      # ConTeXt engine
                    'pdfroff',      # Groff-based engine
                ]

                pdf_engine_found = False
                for engine in pdf_engines:
                    try:
                        subprocess.run([engine, '--version'], capture_output=True, check=True)
                        extra_args.append(f'--pdf-engine={engine}')
                        logger.info(f"Using PDF engine: {engine}")
                        pdf_engine_found = True
                        break
                    except:
                        continue

                if not pdf_engine_found:
                    # No PDF engine found - try to use pandoc's HTML output
                    logger.warning("No PDF engine found. Will use HTML as intermediate format.")
            elif to_format == 'docx':
                # DOCX options are simple
                pass
            elif to_format == 'markdown':
                extra_args.extend([
                    '--wrap=none',  # Don't wrap lines
                ])

            # For PDF and DOCX, we need to write to file
            if output_file and to_format in ['pdf', 'docx']:
                # Convert file to file for binary formats
                if isinstance(source, Path):
                    pypandoc.convert_file(
                        source_file=str(source),
                        to=to_format,
                        format=from_format,
                        outputfile=str(output_file),
                        extra_args=extra_args
                    )
                else:
                    # Convert text to file
                    pypandoc.convert_text(
                        source=source,
                        to=to_format,
                        format=from_format,
                        outputfile=str(output_file),
                        extra_args=extra_args
                    )
                result_text = f"File saved to: {output_file}"
            else:
                # Convert to text for text formats or when no output file specified
                # If source is a Path, read its content first
                if isinstance(source, Path):
                    source_content = source.read_text(encoding='utf-8')
                else:
                    source_content = source

                result_text = pypandoc.convert_text(
                    source=source_content,
                    to=to_format,
                    format=from_format,
                    extra_args=extra_args
                )

                # Post-process the AsciiDoc to ensure quality
                if to_format == 'asciidoc':
                    result_text = self._enhance_asciidoc_output(result_text)

            logger.info(f"Pandoc conversion successful ({context})")
            self.conversion_complete.emit(result_text, context)

        except Exception as e:
            logger.exception(f"Pandoc conversion failed: {context}")
            self.conversion_error.emit(str(e), context)

    def _enhance_asciidoc_output(self, text: str) -> str:
        """Post-process AsciiDoc output for better quality."""
        import re

        # Ensure document has a proper title if missing
        if not text.strip().startswith('='):
            lines = text.strip().split('\n')
            # Try to extract title from first heading
            for i, line in enumerate(lines):
                if line.startswith('=='):
                    title = line[2:].strip()
                    lines.insert(0, f"= {title}\n")
                    lines[i + 1] = line  # Adjust the original line
                    break
            else:
                # No heading found, add a generic title
                lines.insert(0, "= Converted Document\n")
            text = '\n'.join(lines)

        # Fix common conversion issues
        # Convert [source] blocks to proper format
        text = re.sub(r'\[source\](\w+)', r'[source,\1]', text)

        # Ensure proper spacing around headers
        text = re.sub(r'\n(=+\s+[^\n]+)\n(?!=)', r'\n\n\1\n', text)

        # Fix table formatting
        text = re.sub(r'\|===\n\n', r'|===\n', text)

        # Ensure admonition blocks have proper formatting
        text = re.sub(r'(?m)^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s*', r'\n\1: ', text)

        return text


class AsciiDocEditor(QMainWindow):
    request_git_command = Signal(list, str)
    request_pandoc_conversion = Signal(object, str, str, str, object)

    def __init__(self) -> None:
        super().__init__()
        self._settings_path = self._get_settings_path()
        self._set_default_settings()
        self._load_settings()
        self.setWindowTitle(f"{APP_NAME} · Basic Preview")

        # Windows-specific window flags for proper behavior
        if platform.system() == "Windows":
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowTitleHint |
                Qt.WindowType.WindowSystemMenuHint |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )

        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._apply_theme()
        self._setup_workers_and_threads()
        self._update_ui_state()

        # Set up auto-save
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start(300000)  # 5 minutes

    def _set_default_settings(self) -> None:
        # Use Windows Documents folder by default
        if platform.system() == "Windows":
            docs_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            self._last_directory = docs_path or str(Path.home() / "Documents")
        else:
            self._last_directory = str(Path.home())

        self._current_file_path: Optional[Path] = None
        self._git_repo_path: Optional[Path] = None
        self._dark_mode_enabled = True
        self._initial_geometry = None
        self._start_maximized = False  # Don't maximize by default
        self._asciidoc_api = self._initialize_asciidoc()
        self._preview_timer = self._setup_preview_timer()
        self._is_opening_file = False
        self._is_processing_git = False
        self._is_processing_pandoc = False
        self._last_git_operation = ""
        self._pending_file_path: Optional[Path] = None
        self._pending_commit_message: Optional[str] = None
        self._unsaved_changes = False
        self._sync_scrolling = True  # Enable synchronized scrolling by default
        self._is_syncing_scroll = False  # Prevent infinite scroll loops
        self._maximized_pane = None  # Track which pane is maximized
        self._saved_splitter_sizes = None  # Save splitter sizes for restore
        self._pending_export_path: Optional[Path] = None  # For export operations
        self._pending_export_format: Optional[str] = None  # Format being exported
        self._temp_dir = tempfile.TemporaryDirectory()  # For temporary files

    def _get_settings_path(self) -> Path:
        # Windows-friendly settings location
        if platform.system() == "Windows":
            config_dir_str = os.environ.get('APPDATA')
            if config_dir_str:
                config_dir = Path(config_dir_str) / APP_NAME
            else:
                config_dir = Path.home() / "AppData" / "Roaming" / APP_NAME
        else:
            config_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
            if config_dir_str:
                config_dir = Path(config_dir_str)
            else:
                config_dir = Path.home() / f".{APP_NAME.lower()}"

        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using config directory: {config_dir}")
        except Exception as e:
            logger.warning(f"Could not create config directory {config_dir}: {e}")
            return Path.home() / SETTINGS_FILENAME

        return config_dir / SETTINGS_FILENAME

    def _load_settings(self) -> None:
        logger.info(f"Loading settings from: {self._settings_path}")

        if not self._settings_path.is_file():
            logger.info("Settings file not found, using defaults")
            return

        try:
            with open(self._settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Load directory setting
            if 'last_directory' in settings:
                dir_path = settings['last_directory']
                if Path(dir_path).is_dir():
                    self._last_directory = dir_path

            # Load other settings
            self._git_repo_path = settings.get('git_repo_path')
            self._dark_mode_enabled = settings.get('dark_mode', True)
            self._start_maximized = settings.get('maximized', False)

            # Load window geometry if not maximized
            if not self._start_maximized and 'window_geometry' in settings:
                geom = settings['window_geometry']
                if all(key in geom for key in ['x', 'y', 'width', 'height']):
                    self._initial_geometry = QRect(
                        geom['x'], geom['y'], geom['width'], geom['height']
                    )

            logger.info("Settings loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def _save_settings(self) -> None:
        settings = {
            'last_directory': self._last_directory,
            'git_repo_path': self._git_repo_path,
            'dark_mode': self.dark_mode_act.isChecked(),
            'maximized': self.isMaximized()
        }

        # Save geometry if not maximized
        if not self.isMaximized():
            geom = self.geometry()
            settings['window_geometry'] = {
                'x': geom.x(),
                'y': geom.y(),
                'width': geom.width(),
                'height': geom.height()
            }

        try:
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def _initialize_asciidoc(self) -> Optional[AsciiDoc3API]:
        if ASCIIDOC3_AVAILABLE and AsciiDoc3API and asciidoc3:
            try:
                instance = AsciiDoc3API(asciidoc3.__file__)
                # Enhanced options for better HTML output
                instance.options("--no-header-footer")

                # Set attributes for better rendering
                instance.attributes['icons'] = 'font'  # Use font icons
                instance.attributes['source-highlighter'] = 'highlight.js'  # Syntax highlighting
                instance.attributes['toc'] = 'left'  # Table of contents
                instance.attributes['sectanchors'] = ''  # Section anchors
                instance.attributes['sectnums'] = ''  # Section numbering
                instance.attributes['imagesdir'] = '.'  # Images directory

                logger.info("AsciiDoc3API initialized with enhanced attributes")
                return instance
            except Exception as exc:
                logger.error(f"AsciiDoc3API initialization failed: {exc}")
        return None

    def _setup_preview_timer(self) -> QTimer:
        timer = QTimer(self)
        timer.setInterval(PREVIEW_UPDATE_INTERVAL_MS)
        timer.setSingleShot(True)
        timer.timeout.connect(self.update_preview)
        return timer

    def _setup_ui(self) -> None:
        # Set minimum window size
        self.setMinimumSize(800, 600)

        # Create central splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(self.splitter)

        # Create editor container with maximize button
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # Editor toolbar
        editor_toolbar = QWidget()
        editor_toolbar.setFixedHeight(30)
        editor_toolbar.setStyleSheet("background-color: rgba(128, 128, 128, 0.1); border-bottom: 1px solid #888;")
        editor_toolbar_layout = QHBoxLayout(editor_toolbar)
        editor_toolbar_layout.setContentsMargins(5, 2, 5, 2)

        self.editor_label = QLabel("Editor")
        # Store label as instance variable to update color dynamically
        # Set initial color based on current theme
        if self._dark_mode_enabled:
            self.editor_label.setStyleSheet("color: white;")
        else:
            self.editor_label.setStyleSheet("color: black;")
        editor_toolbar_layout.addWidget(self.editor_label)
        editor_toolbar_layout.addStretch()

        # Editor maximize/restore button
        self.editor_max_btn = QPushButton("⬜")  # Maximize icon
        self.editor_max_btn.setFixedSize(24, 24)
        self.editor_max_btn.setToolTip("Maximize editor")
        self.editor_max_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #888;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: #aaa;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.editor_max_btn.clicked.connect(lambda: self._toggle_pane_maximize('editor'))
        editor_toolbar_layout.addWidget(self.editor_max_btn)

        editor_layout.addWidget(editor_toolbar)

        # Create editor
        self.editor = QPlainTextEdit(self)
        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        self.editor.setFont(font)
        self.editor.textChanged.connect(self._start_preview_timer)
        editor_layout.addWidget(self.editor)

        self.splitter.addWidget(editor_container)

        # Create preview container with maximize button
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        # Preview toolbar
        preview_toolbar = QWidget()
        preview_toolbar.setFixedHeight(30)
        preview_toolbar.setStyleSheet("background-color: rgba(128, 128, 128, 0.1); border-bottom: 1px solid #888;")
        preview_toolbar_layout = QHBoxLayout(preview_toolbar)
        preview_toolbar_layout.setContentsMargins(5, 2, 5, 2)

        self.preview_label = QLabel("Preview")
        # Store label as instance variable to update color dynamically
        # Set initial color based on current theme
        if self._dark_mode_enabled:
            self.preview_label.setStyleSheet("color: white;")
        else:
            self.preview_label.setStyleSheet("color: black;")
        preview_toolbar_layout.addWidget(self.preview_label)
        preview_toolbar_layout.addStretch()

        # Preview maximize/restore button
        self.preview_max_btn = QPushButton("⬜")  # Maximize icon
        self.preview_max_btn.setFixedSize(24, 24)
        self.preview_max_btn.setToolTip("Maximize preview")
        self.preview_max_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #888;
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: #aaa;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.preview_max_btn.clicked.connect(lambda: self._toggle_pane_maximize('preview'))
        preview_toolbar_layout.addWidget(self.preview_max_btn)

        preview_layout.addWidget(preview_toolbar)

        # Create preview
        self.preview = QTextBrowser(self)
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(True)
        preview_layout.addWidget(self.preview)

        self.splitter.addWidget(preview_container)

        # Set equal sizes
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # Track maximized state (already initialized in _set_default_settings)

        # Set up synchronized scrolling
        self._setup_synchronized_scrolling()

        # Create status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # Set up dynamic window sizing
        self._setup_dynamic_sizing()

    def _setup_dynamic_sizing(self):
        """Set up window to dynamically resize based on screen size."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()

            # Use 80% of screen size by default
            default_width = int(available.width() * 0.8)
            default_height = int(available.height() * 0.8)

            # Apply initial geometry if loaded, otherwise use defaults
            if self._initial_geometry and available.intersects(self._initial_geometry):
                self.setGeometry(self._initial_geometry)
            else:
                # Center window on screen
                self.resize(default_width, default_height)
                self.move(
                    (available.width() - default_width) // 2 + available.x(),
                    (available.height() - default_height) // 2 + available.y()
                )

            # Apply maximized state if needed
            if self._start_maximized:
                self.showMaximized()

    def _setup_synchronized_scrolling(self):
        """Set up synchronized scrolling between editor and preview."""
        # Connect scroll signals
        editor_scrollbar = self.editor.verticalScrollBar()
        preview_scrollbar = self.preview.verticalScrollBar()

        editor_scrollbar.valueChanged.connect(self._sync_editor_to_preview)
        preview_scrollbar.valueChanged.connect(self._sync_preview_to_editor)

    def _sync_editor_to_preview(self, value):
        """Synchronize preview scroll position with editor."""
        if not self._sync_scrolling or self._is_syncing_scroll:
            return

        self._is_syncing_scroll = True
        try:
            editor_scrollbar = self.editor.verticalScrollBar()
            preview_scrollbar = self.preview.verticalScrollBar()

            # Calculate scroll percentage
            editor_max = editor_scrollbar.maximum()
            if editor_max > 0:
                scroll_percentage = value / editor_max
                preview_value = int(preview_scrollbar.maximum() * scroll_percentage)
                preview_scrollbar.setValue(preview_value)
        finally:
            self._is_syncing_scroll = False

    def _sync_preview_to_editor(self, value):
        """Synchronize editor scroll position with preview."""
        if not self._sync_scrolling or self._is_syncing_scroll:
            return

        self._is_syncing_scroll = True
        try:
            editor_scrollbar = self.editor.verticalScrollBar()
            preview_scrollbar = self.preview.verticalScrollBar()

            # Calculate scroll percentage
            preview_max = preview_scrollbar.maximum()
            if preview_max > 0:
                scroll_percentage = value / preview_max
                editor_value = int(editor_scrollbar.maximum() * scroll_percentage)
                editor_scrollbar.setValue(editor_value)
        finally:
            self._is_syncing_scroll = False

    def _create_actions(self) -> None:
        # File actions with shortcuts
        self.new_act = QAction("&New", self,
            shortcut=QKeySequence.StandardKey.New,
            statusTip="Create a new file",
            triggered=self.new_file
        )

        self.open_act = QAction("&Open...", self,
            shortcut=QKeySequence.StandardKey.Open,
            statusTip="Open a file",
            triggered=self.open_file
        )

        self.save_act = QAction("&Save", self,
            shortcut=QKeySequence.StandardKey.Save,
            statusTip="Save the document as AsciiDoc format (.adoc)",
            triggered=self.save_file
        )

        self.save_as_act = QAction("Save &As...", self,
            shortcut=QKeySequence.StandardKey.SaveAs,
            statusTip="Save with a new name",
            triggered=lambda: self.save_file(save_as=True)
        )

        # Export format actions
        self.save_as_adoc_act = QAction("AsciiDoc (*.adoc)", self,
            statusTip="Save as AsciiDoc file",
            triggered=lambda: self.save_file_as_format('adoc')
        )

        self.save_as_md_act = QAction("GitHub Markdown (*.md)", self,
            statusTip="Export to GitHub Markdown format",
            triggered=lambda: self.save_file_as_format('md')
        )

        self.save_as_docx_act = QAction("Microsoft Word (*.docx)", self,
            statusTip="Export to Microsoft Office 365 Word format",
            triggered=lambda: self.save_file_as_format('docx')
        )

        self.save_as_html_act = QAction("HTML Web Page (*.html)", self,
            statusTip="Export to HTML format (can print to PDF from browser)",
            triggered=lambda: self.save_file_as_format('html')
        )

        self.save_as_pdf_act = QAction("Adobe PDF (*.pdf)", self,
            statusTip="Export to Adobe Acrobat PDF format",
            triggered=lambda: self.save_file_as_format('pdf')
        )

        self.exit_act = QAction("E&xit", self,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip="Exit the application",
            triggered=self.close
        )

        # Edit actions
        self.undo_act = QAction("&Undo", self,
            shortcut=QKeySequence.StandardKey.Undo,
            statusTip="Undo last action",
            triggered=self.editor.undo
        )

        self.redo_act = QAction("&Redo", self,
            shortcut=QKeySequence.StandardKey.Redo,
            statusTip="Redo last action",
            triggered=self.editor.redo
        )

        self.cut_act = QAction("Cu&t", self,
            shortcut=QKeySequence.StandardKey.Cut,
            statusTip="Cut selection",
            triggered=self.editor.cut
        )

        self.copy_act = QAction("&Copy", self,
            shortcut=QKeySequence.StandardKey.Copy,
            statusTip="Copy selection",
            triggered=self.editor.copy
        )

        self.paste_act = QAction("&Paste", self,
            shortcut=QKeySequence.StandardKey.Paste,
            statusTip="Paste from clipboard",
            triggered=self.editor.paste
        )

        self.convert_paste_act = QAction("Convert && Paste", self,
            shortcut="Ctrl+Shift+V",
            statusTip="Convert clipboard content to AsciiDoc",
            triggered=self.convert_and_paste_from_clipboard
        )

        # View actions
        self.zoom_in_act = QAction("Zoom &In", self,
            shortcut=QKeySequence.StandardKey.ZoomIn,
            statusTip="Increase font size",
            triggered=lambda: self._zoom(1)
        )

        self.zoom_out_act = QAction("Zoom &Out", self,
            shortcut=QKeySequence.StandardKey.ZoomOut,
            statusTip="Decrease font size",
            triggered=lambda: self._zoom(-1)
        )

        self.dark_mode_act = QAction("&Dark Mode", self,
            checkable=True,
            checked=self._dark_mode_enabled,
            statusTip="Toggle dark mode",
            triggered=self._toggle_dark_mode
        )

        self.sync_scrolling_act = QAction("&Synchronized Scrolling", self,
            checkable=True,
            checked=self._sync_scrolling,
            statusTip="Toggle synchronized scrolling between editor and preview",
            triggered=self._toggle_sync_scrolling
        )

        # Pane maximize actions
        self.maximize_editor_act = QAction("Maximize &Editor", self,
            shortcut="Ctrl+Shift+E",
            statusTip="Toggle maximize editor pane",
            triggered=lambda: self._toggle_pane_maximize('editor')
        )

        self.maximize_preview_act = QAction("Maximize &Preview", self,
            shortcut="Ctrl+Shift+R",
            statusTip="Toggle maximize preview pane",
            triggered=lambda: self._toggle_pane_maximize('preview')
        )

        # Git actions
        self.set_repo_act = QAction("Set &Repository...", self,
            statusTip="Select Git repository",
            triggered=self._select_git_repository
        )

        self.git_commit_act = QAction("&Commit...", self,
            shortcut="Ctrl+Shift+C",
            statusTip="Commit changes",
            triggered=self._trigger_git_commit
        )

        self.git_pull_act = QAction("&Pull", self,
            shortcut="Ctrl+Shift+P",
            statusTip="Pull from remote",
            triggered=self._trigger_git_pull
        )

        self.git_push_act = QAction("P&ush", self,
            shortcut="Ctrl+Shift+U",
            statusTip="Push to remote",
            triggered=self._trigger_git_push
        )

        # Tools menu actions
        self.pandoc_status_act = QAction("&Pandoc Status", self,
            statusTip="Check Pandoc installation status",
            triggered=self._show_pandoc_status
        )

        self.pandoc_formats_act = QAction("Supported &Formats", self,
            statusTip="Show supported conversion formats",
            triggered=self._show_supported_formats
        )

    def _create_menus(self) -> None:
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addSeparator()
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.save_as_act)

        # Export submenu
        export_menu = file_menu.addMenu("&Export As")
        export_menu.addAction(self.save_as_adoc_act)
        export_menu.addAction(self.save_as_md_act)
        export_menu.addAction(self.save_as_docx_act)
        export_menu.addAction(self.save_as_html_act)
        export_menu.addAction(self.save_as_pdf_act)

        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.convert_paste_act)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.zoom_in_act)
        view_menu.addAction(self.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.dark_mode_act)
        view_menu.addAction(self.sync_scrolling_act)
        view_menu.addSeparator()
        view_menu.addAction(self.maximize_editor_act)
        view_menu.addAction(self.maximize_preview_act)

        # Git menu
        git_menu = menubar.addMenu("&Git")
        git_menu.addAction(self.set_repo_act)
        git_menu.addSeparator()
        git_menu.addAction(self.git_commit_act)
        git_menu.addAction(self.git_pull_act)
        git_menu.addAction(self.git_push_act)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.pandoc_status_act)
        tools_menu.addAction(self.pandoc_formats_act)

    def _setup_workers_and_threads(self) -> None:
        logger.info("Setting up worker threads...")

        # Git thread
        self.git_thread = QThread(self)
        self.git_worker = GitWorker()
        self.git_worker.moveToThread(self.git_thread)
        self.request_git_command.connect(self.git_worker.run_git_command)
        self.git_worker.command_complete.connect(self._handle_git_result)
        self.git_thread.finished.connect(self.git_worker.deleteLater)
        self.git_thread.start()

        # Pandoc thread
        self.pandoc_thread = QThread(self)
        self.pandoc_worker = PandocWorker()
        self.pandoc_worker.moveToThread(self.pandoc_thread)
        self.request_pandoc_conversion.connect(self.pandoc_worker.run_pandoc_conversion)
        self.pandoc_worker.conversion_complete.connect(self._handle_pandoc_result)
        self.pandoc_worker.conversion_error.connect(self._handle_pandoc_error_result)
        self.pandoc_thread.finished.connect(self.pandoc_worker.deleteLater)
        self.pandoc_thread.start()

    def _start_preview_timer(self) -> None:
        if self._is_opening_file:
            return
        self._unsaved_changes = True
        self._update_window_title()
        self._preview_timer.start()

    def _update_window_title(self) -> None:
        title = APP_NAME
        if self._current_file_path:
            title = f"{APP_NAME} - {self._current_file_path.name}"
        else:
            title = f"{APP_NAME} - {DEFAULT_FILENAME}"

        if self._unsaved_changes:
            title += "*"

        self.setWindowTitle(title)

    def _apply_theme(self) -> None:
        if self._dark_mode_enabled:
            self._apply_dark_theme()
            # Update label colors for dark mode
            if hasattr(self, 'editor_label'):
                self.editor_label.setStyleSheet("color: white;")
            if hasattr(self, 'preview_label'):
                self.preview_label.setStyleSheet("color: white;")
        else:
            # Light theme (default Windows theme)
            QApplication.setPalette(QApplication.style().standardPalette())
            # Update label colors for light mode
            if hasattr(self, 'editor_label'):
                self.editor_label.setStyleSheet("color: black;")
            if hasattr(self, 'preview_label'):
                self.preview_label.setStyleSheet("color: black;")

    def _apply_dark_theme(self) -> None:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(palette)

    @Slot()
    def new_file(self) -> None:
        """Create a new file."""
        if self._unsaved_changes:
            if not self._prompt_save_before_action("creating a new file"):
                return

        self.editor.clear()
        self._current_file_path = None
        self._unsaved_changes = False
        self._update_window_title()
        self.statusBar.showMessage("New file created")

    @Slot()
    def open_file(self) -> None:
        """Open a file with proper Windows dialog."""
        if self._is_processing_pandoc:
            self._show_message("warning", "Busy", "Already processing a file conversion.")
            return

        if self._unsaved_changes:
            if not self._prompt_save_before_action("opening a new file"):
                return

        # Windows-friendly file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self._last_directory,
            SUPPORTED_OPEN_FILTER,
            options=QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option()
        )

        if not file_path:
            return

        file_path = Path(file_path)
        self._last_directory = str(file_path.parent)

        try:
            suffix = file_path.suffix.lower()
            if suffix == '.pdf':
                # PDF conversion requires special handling
                self._show_message(
                    "info",
                    "PDF Support Limited",
                    "Direct PDF to AsciiDoc conversion is not yet supported.\n\n"
                    "To work with PDF content:\n"
                    "1. Copy text from your PDF viewer\n"
                    "2. Paste into the editor\n"
                    "3. Format as AsciiDoc\n\n"
                    "Full PDF support is planned for a future release."
                )
                return
            elif suffix in ['.docx', '.md', '.markdown', '.html', '.htm', '.tex', '.rst', '.org', '.textile']:
                # Convert using Pandoc
                if not self._check_pandoc_availability(f"Opening {suffix.upper()[1:]}"):
                    return

                self._is_processing_pandoc = True
                self._pending_file_path = file_path
                self._update_ui_state()

                # Clear editor and show conversion message
                self.editor.setPlainText(f"// Converting {file_path.name} to AsciiDoc...\n// Please wait...")
                self.preview.setHtml("<h3>Converting document...</h3><p>The preview will update when conversion is complete.</p>")
                self.statusBar.showMessage(f"Converting '{file_path.name}' from {suffix.upper()[1:]} to AsciiDoc...")

                # Determine the input format for pandoc
                format_map = {
                    '.docx': ('docx', 'binary'),
                    '.md': ('markdown', 'text'),
                    '.markdown': ('markdown', 'text'),
                    '.html': ('html', 'text'),
                    '.htm': ('html', 'text'),
                    '.tex': ('latex', 'text'),
                    '.rst': ('rst', 'text'),
                    '.org': ('org', 'text'),
                    '.textile': ('textile', 'text')
                }

                input_format, file_type = format_map.get(suffix, ('markdown', 'text'))

                # Read file content based on type
                if file_type == 'binary':
                    file_content = file_path.read_bytes()
                else:
                    file_content = file_path.read_text(encoding='utf-8')

                # Log the conversion start
                logger.info(f"Starting conversion of {file_path.name} from {input_format} to asciidoc")

                self.request_pandoc_conversion.emit(
                    file_content, 'asciidoc', input_format, f"converting '{file_path.name}'", None
                )
            else:
                # Open AsciiDoc directly
                content = file_path.read_text(encoding='utf-8')
                self._load_content_into_editor(content, file_path)

        except Exception as e:
            logger.exception(f"Failed to open file: {file_path}")
            self._show_message("critical", "Error", f"Failed to open file:\n{e}")

    def _load_content_into_editor(self, content: str, file_path: Path) -> None:
        self._is_opening_file = True
        try:
            # Set the raw AsciiDoc markup in the editor
            self.editor.setPlainText(content)
            self._current_file_path = file_path
            self._unsaved_changes = False
            self._update_window_title()

            # Update status with file type info
            if file_path.suffix.lower() in ['.md', '.markdown', '.docx', '.html', '.htm', '.tex', '.rst', '.org', '.textile']:
                self.statusBar.showMessage(f"Converted and opened: {file_path} → AsciiDoc")
            else:
                self.statusBar.showMessage(f"Opened: {file_path}")

            # Ensure preview updates with the rendered content
            self.update_preview()

            # Log the operation
            logger.info(f"Loaded content into editor: {file_path}")
        finally:
            self._is_opening_file = False

    @Slot()
    def save_file(self, save_as: bool = False) -> bool:
        """Save file with Windows-friendly dialog."""
        if save_as or not self._current_file_path:
            # Show save dialog
            suggested_name = self._current_file_path.name if self._current_file_path else DEFAULT_FILENAME
            suggested_path = Path(self._last_directory) / suggested_name

            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Save File",
                str(suggested_path),
                SUPPORTED_SAVE_FILTER,
                options=QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option()
            )

            if not file_path:
                return False

            file_path = Path(file_path)
            logger.info(f"Save As dialog - file_path: {file_path}, selected_filter: {selected_filter}")

            # Determine format based on selected filter or file extension
            format_type = 'adoc'  # default

            # First check the selected filter
            if MD_FILTER in selected_filter:
                format_type = 'md'
            elif DOCX_FILTER in selected_filter:
                format_type = 'docx'
            elif HTML_FILTER in selected_filter:
                format_type = 'html'
            elif PDF_FILTER in selected_filter:
                format_type = 'pdf'
            elif file_path.suffix:
                # If no specific filter selected, determine by extension
                ext = file_path.suffix.lower()
                if ext in ['.md', '.markdown']:
                    format_type = 'md'
                elif ext == '.docx':
                    format_type = 'docx'
                elif ext in ['.html', '.htm']:
                    format_type = 'html'
                elif ext == '.pdf':
                    format_type = 'pdf'

            # Ensure correct extension
            if format_type == 'md' and not file_path.suffix:
                file_path = file_path.with_suffix('.md')
            elif format_type == 'docx' and not file_path.suffix:
                file_path = file_path.with_suffix('.docx')
            elif format_type == 'html' and not file_path.suffix:
                file_path = file_path.with_suffix('.html')
            elif format_type == 'pdf' and not file_path.suffix:
                file_path = file_path.with_suffix('.pdf')
            elif format_type == 'adoc' and not file_path.suffix:
                file_path = file_path.with_suffix('.adoc')

            # If saving as non-AsciiDoc format, use export functionality
            if format_type != 'adoc':
                logger.info(f"Calling _save_as_format_internal with file_path={file_path}, format_type={format_type}")
                return self._save_as_format_internal(file_path, format_type)

        else:
            # For regular save, always use AsciiDoc format
            file_path = self._current_file_path

            # If current file is not an AsciiDoc file, change extension to .adoc
            if file_path.suffix.lower() not in ['.adoc', '.asciidoc']:
                # Change extension to .adoc
                file_path = file_path.with_suffix('.adoc')
                logger.info(f"Converting save format from {self._current_file_path.suffix} to .adoc")

        # Save as AsciiDoc
        try:
            content = self.editor.toPlainText()
            file_path.write_text(content, encoding='utf-8')

            self._current_file_path = file_path
            self._last_directory = str(file_path.parent)
            self._unsaved_changes = False
            self._update_window_title()
            self.statusBar.showMessage(f"Saved as AsciiDoc: {file_path}")
            return True

        except Exception as e:
            logger.exception(f"Failed to save file: {file_path}")
            self._show_message("critical", "Save Error", f"Failed to save file:\n{e}")
            return False

    def _save_as_format_internal(self, file_path: Path, format_type: str) -> bool:
        """Internal method to save file in specified format without showing dialog."""
        logger.info(f"_save_as_format_internal called - file_path: {file_path}, format_type: {format_type}")
        # Get current content
        content = self.editor.toPlainText()

        # For native AsciiDoc format, just save directly
        if format_type == 'adoc':
            try:
                file_path.write_text(content, encoding='utf-8')
                self._current_file_path = file_path
                self._last_directory = str(file_path.parent)
                self._unsaved_changes = False
                self._update_window_title()
                self.statusBar.showMessage(f"Saved as AsciiDoc: {file_path}")
                return True
            except Exception as e:
                logger.exception(f"Failed to save AsciiDoc file: {file_path}")
                self._show_message("critical", "Save Error", f"Failed to save AsciiDoc file:\n{e}")
                return False

        # For HTML format, convert directly without pandoc
        if format_type == 'html':
            self.statusBar.showMessage(f"Saving as HTML...")
            try:
                # Use asciidoc3api to convert to HTML
                infile = io.StringIO(content)
                outfile = io.StringIO()
                self._asciidoc_api.execute(infile, outfile, backend="html5")
                html_content = outfile.getvalue()

                # Save HTML directly
                file_path.write_text(html_content, encoding='utf-8')
                self.statusBar.showMessage(f"Saved as HTML: {file_path}")
                logger.info(f"Successfully saved as HTML: {file_path}")
                return True
            except Exception as e:
                logger.exception(f"Failed to save HTML file: {e}")
                self._show_message("critical", "Save Error", f"Failed to save HTML file:\n{e}")
                return False

        # Check pandoc availability for other formats
        if not self._check_pandoc_availability(f"Save as {format_type.upper()}"):
            return False

        # For other formats, use pandoc conversion in background
        self.statusBar.showMessage(f"Saving as {format_type.upper()}...")

        # Convert AsciiDoc to HTML first (pandoc doesn't support AsciiDoc input)
        try:
            # Use asciidoc3api to convert to HTML
            infile = io.StringIO(content)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            html_content = outfile.getvalue()
        except Exception as e:
            logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
            self._show_message("critical", "Conversion Error", f"Failed to convert AsciiDoc to HTML:\n{e}")
            return False

        # Create temporary HTML file for conversion
        temp_html = Path(self._temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
        try:
            temp_html.write_text(html_content, encoding='utf-8')
        except Exception as e:
            self._show_message("critical", "Save Error", f"Failed to create temporary file:\n{e}")
            return False

        # Show conversion in progress
        # self._show_conversion_progress(f"Saving as {format_type.upper()}")
        self.statusBar.showMessage(f"Saving as {format_type.upper()}...")

        # For PDF and DOCX, pass the output file directly
        if format_type in ['pdf', 'docx']:
            # For PDF without engine, save HTML and provide instructions
            if format_type == 'pdf' and not self._check_pdf_engine_available():
                # Save as HTML with PDF-like styling
                try:
                    # Add print-friendly CSS to HTML
                    styled_html = self._add_print_css_to_html(html_content)
                    html_path = file_path.with_suffix('.html')
                    html_path.write_text(styled_html, encoding='utf-8')

                    self.statusBar.showMessage(f"Saved as HTML (PDF-ready): {html_path}")
                    self._show_message(
                        "information",
                        "PDF Export Alternative",
                        f"Saved as HTML with print styling: {html_path}\n\n"
                        f"To create PDF:\n"
                        f"1. Open this file in your browser\n"
                        f"2. Press Ctrl+P (or Cmd+P on Mac)\n"
                        f"3. Select 'Save as PDF'\n\n"
                        f"The HTML includes print-friendly styling for optimal PDF output."
                    )
                    return False
                except Exception as e:
                    logger.exception(f"Failed to save HTML for PDF: {e}")

            logger.info(f"Emitting pandoc conversion request for {format_type} - temp_html: {temp_html}, output: {file_path}")
            self.request_pandoc_conversion.emit(
                temp_html,
                format_type,  # to_format (target)
                'html',       # from_format (source)
                f"Exporting to {format_type.upper()}",
                file_path
            )
        else:
            # For text formats, get the result and save it
            self.request_pandoc_conversion.emit(
                temp_html,
                format_type,  # to_format (target)
                'html',       # from_format (source)
                f"Exporting to {format_type.upper()}",
                None
            )
            # Store target path for when conversion completes
            self._pending_export_path = file_path
            self._pending_export_format = format_type

        # Update current file path for AsciiDoc files
        if format_type == 'adoc':
            self._current_file_path = file_path
            self._last_directory = str(file_path.parent)
            self._unsaved_changes = False
            self._update_window_title()

        return True

    def save_file_as_format(self, format_type: str) -> bool:
        """Save/export file in specified format using background conversion."""
        # Determine file filter and suggested extension based on format
        format_filters = {
            'adoc': (ADOC_FILTER, '.adoc'),
            'md': (MD_FILTER, '.md'),
            'docx': (DOCX_FILTER, '.docx'),
            'html': (HTML_FILTER, '.html'),
            'pdf': (PDF_FILTER, '.pdf')
        }

        if format_type not in format_filters:
            self._show_message("warning", "Export Error", f"Unsupported format: {format_type}")
            return False

        file_filter, suggested_ext = format_filters[format_type]

        # Prepare suggested filename
        if self._current_file_path:
            suggested_name = self._current_file_path.stem + suggested_ext
        else:
            suggested_name = "document" + suggested_ext

        suggested_path = Path(self._last_directory) / suggested_name

        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export as {format_type.upper()}",
            str(suggested_path),
            file_filter,
            options=QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option()
        )

        if not file_path:
            return False

        file_path = Path(file_path)

        # Ensure correct extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(suggested_ext)

        # Get current content
        content = self.editor.toPlainText()

        # For native AsciiDoc format, just save directly
        if format_type == 'adoc':
            try:
                file_path.write_text(content, encoding='utf-8')
                self.statusBar.showMessage(f"Saved as AsciiDoc: {file_path}")
                return True
            except Exception as e:
                logger.exception(f"Failed to save AsciiDoc file: {file_path}")
                self._show_message("critical", "Export Error", f"Failed to save AsciiDoc file:\n{e}")
                return False

        # For HTML format, convert directly without pandoc
        if format_type == 'html':
            self.statusBar.showMessage(f"Exporting to HTML...")
            try:
                # Use asciidoc3api to convert to HTML
                infile = io.StringIO(content)
                outfile = io.StringIO()
                self._asciidoc_api.execute(infile, outfile, backend="html5")
                html_content = outfile.getvalue()

                # Save HTML directly
                file_path.write_text(html_content, encoding='utf-8')
                self.statusBar.showMessage(f"Exported to HTML: {file_path}")
                logger.info(f"Successfully exported to HTML: {file_path}")
                return True
            except Exception as e:
                logger.exception(f"Failed to export HTML file: {e}")
                self._show_message("critical", "Export Error", f"Failed to export HTML file:\n{e}")
                return False

        # For other formats, use pandoc conversion in background
        self.statusBar.showMessage(f"Exporting to {format_type.upper()}...")

        # Convert AsciiDoc to HTML first (pandoc doesn't support AsciiDoc input)
        try:
            # Use asciidoc3api to convert to HTML
            infile = io.StringIO(content)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            html_content = outfile.getvalue()
        except Exception as e:
            logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
            self._show_message("critical", "Conversion Error", f"Failed to convert AsciiDoc to HTML:\n{e}")
            return False

        # Create temporary HTML file for conversion
        temp_html = Path(self._temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
        try:
            temp_html.write_text(html_content, encoding='utf-8')
        except Exception as e:
            self._show_message("critical", "Export Error", f"Failed to create temporary file:\n{e}")
            return False

        # Show conversion in progress
        # self._show_conversion_progress(f"Exporting to {format_type.upper()}")
        self.statusBar.showMessage(f"Exporting to {format_type.upper()}...")

        # For PDF and DOCX, pass the output file directly
        if format_type in ['pdf', 'docx']:
            # For PDF without engine, save HTML and provide instructions
            if format_type == 'pdf' and not self._check_pdf_engine_available():
                # Save as HTML with PDF-like styling
                try:
                    # Add print-friendly CSS to HTML
                    styled_html = self._add_print_css_to_html(html_content)
                    html_path = file_path.with_suffix('.html')
                    html_path.write_text(styled_html, encoding='utf-8')

                    self.statusBar.showMessage(f"Exported as HTML (PDF-ready): {html_path}")
                    self._show_message(
                        "information",
                        "PDF Export Alternative",
                        f"Exported as HTML with print styling: {html_path}\n\n"
                        f"To create PDF:\n"
                        f"1. Open this file in your browser\n"
                        f"2. Press Ctrl+P (or Cmd+P on Mac)\n"
                        f"3. Select 'Save as PDF'\n\n"
                        f"The HTML includes print-friendly styling for optimal PDF output."
                    )
                    return True
                except Exception as e:
                    logger.exception(f"Failed to save HTML for PDF: {e}")

            self.request_pandoc_conversion.emit(
                temp_html,
                format_type,  # to_format (target)
                'html',       # from_format (source)
                f"Exporting to {format_type.upper()}",
                file_path
            )
            self._pending_export_path = None  # Don't need to save later
            self._pending_export_format = None
        else:
            # For text formats, get the result and save it
            self.request_pandoc_conversion.emit(
                temp_html,
                format_type,  # to_format (target)
                'html',       # from_format (source)
                f"Exporting to {format_type.upper()}",
                None
            )
            # Store target path for when conversion completes
            self._pending_export_path = file_path
            self._pending_export_format = format_type

        return True

    def _check_pdf_engine_available(self) -> bool:
        """Check if any PDF engine is available."""
        import subprocess
        pdf_engines = ['wkhtmltopdf', 'weasyprint', 'pdflatex', 'xelatex', 'lualatex']

        for engine in pdf_engines:
            try:
                subprocess.run([engine, '--version'], capture_output=True, check=True)
                return True
            except:
                continue

        return False

    def _add_print_css_to_html(self, html_content: str) -> str:
        """Add print-friendly CSS to HTML for better PDF output."""
        print_css = """
        <style type="text/css" media="print">
            @page {
                size: letter;
                margin: 1in;
            }
            body {
                font-family: Georgia, serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #000;
            }
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
                font-family: Helvetica, Arial, sans-serif;
            }
            pre, code {
                font-family: Consolas, Monaco, monospace;
                font-size: 9pt;
                background-color: #f5f5f5;
                page-break-inside: avoid;
            }
            table {
                border-collapse: collapse;
                page-break-inside: avoid;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            a {
                color: #000;
                text-decoration: underline;
            }
            @media screen {
                body {
                    max-width: 8.5in;
                    margin: 0 auto;
                    padding: 1in;
                }
            }
        </style>
        """

        # Insert CSS before </head> or after <html>
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', print_css + '</head>')
        elif '<html>' in html_content:
            html_content = html_content.replace('<html>', '<html>' + print_css)
        else:
            # Prepend if no head tag
            html_content = print_css + html_content

        return html_content

    def _auto_save(self) -> None:
        """Auto-save current file if there are unsaved changes."""
        if self._current_file_path and self._unsaved_changes:
            try:
                content = self.editor.toPlainText()
                self._current_file_path.write_text(content, encoding='utf-8')
                self.statusBar.showMessage("Auto-saved", 2000)
                logger.info(f"Auto-saved: {self._current_file_path}")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")

    @Slot()
    def update_preview(self) -> None:
        source_text = self.editor.toPlainText()
        html_body = self._convert_asciidoc_to_html_body(source_text)
        full_html = f"""<!doctype html>
<html>
<head>
    <meta charset='utf-8'>
    <style>{self._get_preview_css()}</style>
</head>
<body>
    {html_body}
</body>
</html>"""
        self.preview.setHtml(full_html)

    def _convert_asciidoc_to_html_body(self, source_text: str) -> str:
        if self._asciidoc_api is None:
            return f"<pre>{html.escape(source_text)}</pre>"

        try:
            infile = io.StringIO(source_text)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()
        except Exception as exc:
            logger.error(f"AsciiDoc rendering failed: {exc}")
            return f"<div style='color:red'>Render Error: {html.escape(str(exc))}</div>"

    def _get_preview_css(self) -> str:
        # Enhanced CSS for better AsciiDoc WYSIWYG rendering
        if self._dark_mode_enabled:
            return """
                body {
                    background:#1e1e1e; color:#dcdcdc;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
                }
                h1,h2,h3,h4,h5,h6 { color:#ececec; margin-top: 1.5em; margin-bottom: 0.5em; }
                h1 { font-size: 2.2em; border-bottom: 2px solid #444; padding-bottom: 0.3em; }
                h2 { font-size: 1.8em; border-bottom: 1px solid #333; padding-bottom: 0.2em; }
                h3 { font-size: 1.4em; }
                a { color:#80d0ff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                code { background:#2a2a2a; color:#f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
                pre { background:#2a2a2a; color:#f0f0f0; padding: 15px; overflow-x: auto; border-radius: 5px; }
                pre code { background: none; padding: 0; }
                blockquote { border-left: 4px solid #666; margin: 1em 0; padding-left: 1em; color: #aaa; }
                table { border-collapse: collapse; width: 100%; margin: 1em 0; }
                th, td { border: 1px solid #444; padding: 8px; text-align: left; }
                th { background: #2a2a2a; font-weight: bold; }
                ul, ol { padding-left: 2em; margin: 1em 0; }
                .admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
                .admonitionblock.note { background: #1e3a5f; border-left: 4px solid #4a90e2; }
                .admonitionblock.tip { background: #1e4d2b; border-left: 4px solid #5cb85c; }
                .admonitionblock.warning { background: #5d4037; border-left: 4px solid #ff9800; }
                .admonitionblock.caution { background: #5d4037; border-left: 4px solid #f44336; }
                .admonitionblock.important { background: #4a148c; border-left: 4px solid #9c27b0; }
                .imageblock { text-align: center; margin: 1em 0; }
                .imageblock img { max-width: 100%; height: auto; }
            """
        else:
            return """
                body {
                    background:#ffffff; color:#333333;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
                }
                h1,h2,h3,h4,h5,h6 { color:#111111; margin-top: 1.5em; margin-bottom: 0.5em; }
                h1 { font-size: 2.2em; border-bottom: 2px solid #ddd; padding-bottom: 0.3em; }
                h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
                h3 { font-size: 1.4em; }
                a { color:#007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                code { background:#f8f8f8; color:#333; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; border: 1px solid #e1e4e8; }
                pre { background:#f8f8f8; color:#333; padding: 15px; overflow-x: auto; border-radius: 5px; border: 1px solid #e1e4e8; }
                pre code { background: none; padding: 0; border: none; }
                blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding-left: 1em; color: #666; }
                table { border-collapse: collapse; width: 100%; margin: 1em 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #f8f8f8; font-weight: bold; }
                ul, ol { padding-left: 2em; margin: 1em 0; }
                .admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
                .admonitionblock.note { background: #e3f2fd; border-left: 4px solid #2196f3; }
                .admonitionblock.tip { background: #e8f5e9; border-left: 4px solid #4caf50; }
                .admonitionblock.warning { background: #fff3e0; border-left: 4px solid #ff9800; }
                .admonitionblock.caution { background: #ffebee; border-left: 4px solid #f44336; }
                .admonitionblock.important { background: #f3e5f5; border-left: 4px solid #9c27b0; }
                .imageblock { text-align: center; margin: 1em 0; }
                .imageblock img { max-width: 100%; height: auto; }
            """

    def _zoom(self, delta: int) -> None:
        font = self.editor.font()
        new_size = max(MIN_FONT_SIZE, font.pointSize() + delta)
        font.setPointSize(new_size)
        self.editor.setFont(font)
        self.preview.zoomIn(delta)

    def _toggle_dark_mode(self) -> None:
        self._dark_mode_enabled = self.dark_mode_act.isChecked()
        self._apply_theme()
        self.update_preview()

    def _toggle_sync_scrolling(self) -> None:
        self._sync_scrolling = self.sync_scrolling_act.isChecked()
        self.statusBar.showMessage(
            f"Synchronized scrolling {'enabled' if self._sync_scrolling else 'disabled'}",
            5000
        )

    def _toggle_pane_maximize(self, pane: str) -> None:
        """Toggle maximize/restore for a specific pane."""
        if self._maximized_pane == pane:
            # Restore normal view
            self._restore_panes()
        elif self._maximized_pane is not None:
            # Another pane is maximized, switch to this pane
            self._maximize_pane(pane)
        else:
            # No pane is maximized, maximize the requested pane
            self._maximize_pane(pane)

    def _maximize_pane(self, pane: str) -> None:
        """Maximize a specific pane."""
        # Only save splitter sizes if not already maximized
        if self._maximized_pane is None:
            self._saved_splitter_sizes = self.splitter.sizes()

        if pane == 'editor':
            # Hide preview pane
            self.splitter.setSizes([self.splitter.width(), 0])
            self.editor_max_btn.setText("⬛")  # Restore icon
            self.editor_max_btn.setToolTip("Restore editor")
            # Don't disable the preview button - just show it can't be maximized
            self.preview_max_btn.setEnabled(True)
            # Reset preview button if it was maximized
            self.preview_max_btn.setText("⬜")
            self.preview_max_btn.setToolTip("Maximize preview")
            self.statusBar.showMessage("Editor maximized", 3000)
        else:  # preview
            # Hide editor pane
            self.splitter.setSizes([0, self.splitter.width()])
            self.preview_max_btn.setText("⬛")  # Restore icon
            self.preview_max_btn.setToolTip("Restore preview")
            # Don't disable the editor button - just show it can't be maximized
            self.editor_max_btn.setEnabled(True)
            # Reset editor button if it was maximized
            self.editor_max_btn.setText("⬜")
            self.editor_max_btn.setToolTip("Maximize editor")
            self.statusBar.showMessage("Preview maximized", 3000)

        self._maximized_pane = pane

    def _restore_panes(self) -> None:
        """Restore panes to their previous sizes."""
        if self._saved_splitter_sizes and len(self._saved_splitter_sizes) == 2:
            # Ensure the saved sizes are valid
            total = sum(self._saved_splitter_sizes)
            if total > 0:
                self.splitter.setSizes(self._saved_splitter_sizes)
            else:
                # Fallback to equal sizes
                width = self.splitter.width()
                self.splitter.setSizes([width // 2, width // 2])
        else:
            # Default to equal sizes
            width = self.splitter.width()
            self.splitter.setSizes([width // 2, width // 2])

        # Reset buttons
        self.editor_max_btn.setText("⬜")  # Maximize icon
        self.editor_max_btn.setToolTip("Maximize editor")
        self.editor_max_btn.setEnabled(True)
        self.preview_max_btn.setText("⬜")  # Maximize icon
        self.preview_max_btn.setToolTip("Maximize preview")
        self.preview_max_btn.setEnabled(True)

        self._maximized_pane = None
        self.statusBar.showMessage("View restored", 3000)

    def convert_and_paste_from_clipboard(self) -> None:
        if not self._check_pandoc_availability("Clipboard Conversion"):
            return

        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()

        source_text = None
        source_format = "markdown"

        if mime_data.hasHtml():
            source_text = mime_data.html()
            source_format = "html"
        elif mime_data.hasText():
            source_text = mime_data.text()

        if not source_text:
            self._show_message("info", "Empty Clipboard", "No text or HTML found in clipboard.")
            return

        self._is_processing_pandoc = True
        self._update_ui_state()
        self.statusBar.showMessage("Converting clipboard content...")
        self.request_pandoc_conversion.emit(source_text, 'asciidoc', source_format, "clipboard conversion", None)

    def _select_git_repository(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Git Repository",
            self._git_repo_path or self._last_directory,
            QFileDialog.Option.ShowDirsOnly
        )

        if not dir_path:
            return

        if not (Path(dir_path) / ".git").is_dir():
            self._show_message("warning", "Not a Git Repository",
                              "Selected directory is not a Git repository.")
            return

        self._git_repo_path = dir_path
        self.statusBar.showMessage(f"Git repository set: {dir_path}")
        self._update_ui_state()

    def _trigger_git_commit(self) -> None:
        if not self._ensure_git_ready():
            return

        if self._unsaved_changes:
            if not self.save_file():
                return

        message, ok = QInputDialog.getMultiLineText(
            self, "Commit Message", "Enter commit message:", ""
        )

        if not ok or not message.strip():
            return

        self._is_processing_git = True
        self._last_git_operation = "commit"
        self._pending_commit_message = message
        self._update_ui_state()

        self.statusBar.showMessage("Committing changes...")
        self.request_git_command.emit(["git", "add", "."], self._git_repo_path)

    def _trigger_git_pull(self) -> None:
        if not self._ensure_git_ready():
            return

        self._is_processing_git = True
        self._last_git_operation = "pull"
        self._update_ui_state()

        self.statusBar.showMessage("Pulling from remote...")
        self.request_git_command.emit(["git", "pull"], self._git_repo_path)

    def _trigger_git_push(self) -> None:
        if not self._ensure_git_ready():
            return

        self._is_processing_git = True
        self._last_git_operation = "push"
        self._update_ui_state()

        self.statusBar.showMessage("Pushing to remote...")
        self.request_git_command.emit(["git", "push"], self._git_repo_path)

    def _ensure_git_ready(self) -> bool:
        if not self._git_repo_path:
            self._show_message("info", "No Repository",
                              "Please set a Git repository first.")
            return False
        if self._is_processing_git:
            self._show_message("warning", "Busy", "Git operation in progress.")
            return False
        return True

    @Slot(GitResult)
    def _handle_git_result(self, result: GitResult) -> None:
        if self._last_git_operation == "commit" and result.success:
            # Continue with actual commit
            self.request_git_command.emit(
                ["git", "commit", "-m", self._pending_commit_message],
                self._git_repo_path
            )
            self._last_git_operation = "commit_final"
            return

        self._is_processing_git = False
        self._update_ui_state()

        if result.success:
            self._show_message("info", "Success", result.user_message)
        else:
            self._show_message("critical", "Git Error", result.user_message)

        self._last_git_operation = ""
        self._pending_commit_message = None

    @Slot(str, str)
    def _handle_pandoc_result(self, result: str, context: str) -> None:
        self._is_processing_pandoc = False
        self._update_ui_state()

        if context == "clipboard conversion":
            self.editor.insertPlainText(result)
            self.statusBar.showMessage("Pasted converted content")
        elif "Exporting to" in context and ("File saved to:" in result or self._pending_export_path):
            # Handle export operation
            try:
                if "File saved to:" in result:
                    # File was saved by pandoc directly (PDF/DOCX)
                    self.statusBar.showMessage(f"Exported successfully: {result.split(': ', 1)[1]}")
                elif self._pending_export_format == 'pdf':
                    # For PDF, result might be binary data, so handle differently
                    # Pandoc should have created the file directly
                    if self._pending_export_path.exists():
                        self.statusBar.showMessage(f"Exported to PDF: {self._pending_export_path}")
                    else:
                        # If not, write the result as text (unlikely for PDF)
                        self._pending_export_path.write_text(result, encoding='utf-8')
                        self.statusBar.showMessage(f"Exported to {self._pending_export_format.upper()}: {self._pending_export_path}")
                else:
                    # For text formats (MD), write the result
                    self._pending_export_path.write_text(result, encoding='utf-8')
                    self.statusBar.showMessage(f"Saved as {self._pending_export_format.upper()}: {self._pending_export_path}")

                logger.info(f"Successfully saved as {self._pending_export_format}: {self._pending_export_path}")
            except Exception as e:
                logger.exception(f"Failed to save export file: {self._pending_export_path}")
                self._show_message("critical", "Export Error", f"Failed to save exported file:\n{e}")
            finally:
                self._pending_export_path = None
                self._pending_export_format = None
        elif self._pending_file_path:
            # Load the raw AsciiDoc markup into the editor
            self._load_content_into_editor(result, self._pending_file_path)
            self._pending_file_path = None

            # Log successful conversion
            logger.info(f"Successfully converted {context}")

            # Force immediate preview update
            QTimer.singleShot(100, self.update_preview)

    @Slot(str, str)
    def _handle_pandoc_error_result(self, error: str, context: str) -> None:
        self._is_processing_pandoc = False
        file_path = self._pending_file_path
        self._pending_file_path = None
        export_path = self._pending_export_path
        self._pending_export_path = None
        self._pending_export_format = None
        self._update_ui_state()
        self.statusBar.showMessage(f"Conversion failed: {context}")

        # If this was an export operation, don't clear the editor
        if export_path and "Exporting to" in context:
            # Special handling for PDF export failures
            if "PDF" in context and ("pdflatex" in error or "pdf-engine" in error or "No such file or directory" in error):
                error_msg = (
                    f"Failed to export to PDF:\n\n"
                    f"Pandoc could not find a PDF engine on your system.\n\n"
                    f"Solution: Export to HTML instead\n"
                    f"1. File → Save As → Select 'HTML Files (*.html)'\n"
                    f"2. Open the HTML file in your browser\n"
                    f"3. Press Ctrl+P and select 'Save as PDF'\n\n"
                    f"Technical details:\n{error}"
                )
            else:
                error_msg = f"Failed to export to {export_path.suffix[1:].upper()}:\n{error}"

            self._show_message(
                "critical",
                "Export Error",
                error_msg
            )
            return

        # Clear the editor and preview for file open operations
        self.editor.clear()
        self.preview.setHtml("<h3>Conversion Failed</h3><p>Unable to convert the document.</p>")

        # Show detailed error
        error_msg = f"{context} failed:\n\n{error}"
        if file_path:
            error_msg += f"\n\nFile: {file_path}"

        self._show_message("critical", "Conversion Error", error_msg)

    def _update_ui_state(self) -> None:
        # File operations
        # Enable save even without a file (will trigger save as dialog)
        self.save_act.setEnabled(not self._is_processing_pandoc)
        self.save_as_act.setEnabled(not self._is_processing_pandoc)

        # Export operations
        export_enabled = not self._is_processing_pandoc
        self.save_as_adoc_act.setEnabled(export_enabled)
        self.save_as_md_act.setEnabled(export_enabled and PANDOC_AVAILABLE)
        self.save_as_docx_act.setEnabled(export_enabled and PANDOC_AVAILABLE)
        self.save_as_html_act.setEnabled(export_enabled)  # HTML doesn't need pandoc
        self.save_as_pdf_act.setEnabled(export_enabled and PANDOC_AVAILABLE)

        # Git operations
        git_ready = bool(self._git_repo_path) and not self._is_processing_git
        self.git_commit_act.setEnabled(git_ready)
        self.git_pull_act.setEnabled(git_ready)
        self.git_push_act.setEnabled(git_ready)

        # Pandoc operations
        self.convert_paste_act.setEnabled(PANDOC_AVAILABLE and not self._is_processing_pandoc)

    def _check_pandoc_availability(self, context: str) -> bool:
        if ENHANCED_PANDOC and ensure_pandoc_available:
            # Use enhanced pandoc integration
            is_available, message = ensure_pandoc_available()
            if not is_available:
                self._show_message(
                    "critical",
                    "Pandoc Setup Required",
                    f"{context} requires Pandoc.\n\n{message}"
                )
                return False
            return True
        elif not PANDOC_AVAILABLE:
            # Fallback to basic check
            self._show_message("critical", "Pandoc Not Available",
                             f"{context} requires Pandoc and pypandoc.\n"
                             "Please install them first:\n\n"
                             "1. Install pandoc from https://pandoc.org\n"
                             "2. Run: pip install pypandoc")
            return False
        return True

    def _show_pandoc_status(self) -> None:
        """Show detailed pandoc installation status."""
        if ENHANCED_PANDOC and pandoc:
            # Get detailed status from enhanced integration
            is_available, status = ensure_pandoc_available()

            details = f"Pandoc Status:\n\n"
            details += f"Binary found: {'Yes' if pandoc.pandoc_path else 'No'}\n"
            if pandoc.pandoc_path:
                details += f"Location: {pandoc.pandoc_path}\n"
            details += f"Version: {pandoc.pandoc_version or 'Unknown'}\n"
            details += f"pypandoc: {'Available' if pandoc.pypandoc_available else 'Not installed'}\n\n"
            details += f"Status: {status}"

            self._show_message("info", "Pandoc Status", details)
        else:
            # Basic status
            status = "Pandoc Status:\n\n"
            status += f"PANDOC_AVAILABLE: {PANDOC_AVAILABLE}\n"
            status += f"pypandoc module: {'Imported' if pypandoc else 'Not found'}\n\n"

            if not PANDOC_AVAILABLE:
                status += "To enable document conversion:\n"
                status += "1. Install pandoc from https://pandoc.org\n"
                status += "2. Run: pip install pypandoc"

            self._show_message("info", "Pandoc Status", status)

    def _show_supported_formats(self) -> None:
        """Show supported input and output formats."""
        if ENHANCED_PANDOC and pandoc and pandoc.pypandoc_available:
            # Get formats from enhanced integration
            message = "Supported Conversion Formats:\n\n"

            # Key input formats for this application
            key_inputs = ['markdown', 'docx', 'html', 'latex', 'rst', 'org']
            available_inputs = [f for f in key_inputs if pandoc.is_format_supported(f, 'input')]

            message += "INPUT FORMATS:\n"
            for fmt in available_inputs:
                desc = pandoc.get_format_info(fmt)
                message += f"  • {fmt}: {desc}\n"

            message += f"\nTotal input formats: {len(pandoc.supported_formats['input'])}\n"

            message += "\nOUTPUT FORMATS:\n"
            message += f"  • asciidoc: {pandoc.get_format_info('asciidoc')}\n"
            message += f"  • markdown: {pandoc.get_format_info('markdown')}\n"
            message += f"  • html: {pandoc.get_format_info('html')}\n"

            message += f"\nTotal output formats: {len(pandoc.supported_formats['output'])}"

            self._show_message("info", "Supported Formats", message)
        else:
            self._show_message(
                "warning",
                "Format Information Unavailable",
                "Pandoc is not properly configured.\n\n"
                "When configured, you can convert between many formats including:\n"
                "• Markdown to AsciiDoc\n"
                "• DOCX to AsciiDoc\n"
                "• HTML to AsciiDoc\n"
                "• And many more..."
            )

    def _show_message(self, level: str, title: str, text: str) -> None:
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "critical": QMessageBox.Icon.Critical,
        }

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon_map.get(level, QMessageBox.Icon.Information))
        msg.exec()

    def _prompt_save_before_action(self, action: str) -> bool:
        if not self._unsaved_changes:
            return True

        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"Save changes before {action}?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def closeEvent(self, event):
        """Handle window close event."""
        if not self._prompt_save_before_action("closing"):
            event.ignore()
            return

        # Save settings
        self._save_settings()

        # Stop threads
        logger.info("Shutting down worker threads...")
        self.git_thread.quit()
        self.pandoc_thread.quit()

        # Wait briefly for threads
        self.git_thread.wait(1000)
        self.pandoc_thread.wait(1000)

        # Clean up temp directory
        try:
            self._temp_dir.cleanup()
        except:
            pass  # Ignore errors during cleanup

        event.accept()


def main():
    # Enable high DPI support
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Suppress warnings
    warnings.filterwarnings('ignore', category=SyntaxWarning)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan")

    # Set application style
    if platform.system() == "Windows":
        app.setStyle("windowsvista")  # Modern Windows style
    else:
        app.setStyle("Fusion")

    # Create and show main window
    window = AsciiDocEditor()
    window.show()

    # Initial preview
    window.update_preview()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()