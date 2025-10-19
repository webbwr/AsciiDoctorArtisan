#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AsciiDoc Artisan - Professional AsciiDoc Editor
==============================================

A modern, feature-rich AsciiDoc editor with live preview capabilities.
Optimized for high-DPI displays and professional documentation workflows.

Author: AsciiDoc Artisan Team
License: See LICENSE file
Python: 3.11+ required
"""

# Standard Library Imports
# These are Python's built-in modules - no installation needed
import sys
import io
import os
import subprocess
import shlex
from pathlib import Path
from typing import Optional, Tuple, NamedTuple, List, Union, Any, Dict, Callable
import warnings
import html
import json
import logging
from enum import Enum, auto
from dataclasses import dataclass
from contextlib import contextmanager
import time
from functools import lru_cache, wraps
from collections import deque
import threading

# Third-Party Imports - Qt Framework
# PySide6 is Qt for Python - provides the GUI framework
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
)
from PySide6.QtGui import (
    QAction,
    QPalette,
    QColor,
    QFont,
    QKeySequence,
    QGuiApplication,
    QScreen,
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
)

# Optional Dependencies with Graceful Fallback
# These enhance functionality but aren't required
try:
    import pypandoc
    PANDOC_AVAILABLE = True
except ImportError:
    logging.warning("pypandoc not found. DOCX conversion disabled.")
    pypandoc = None
    PANDOC_AVAILABLE = False

try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API
    ASCIIDOC3_AVAILABLE = True
except ImportError:
    logging.warning("asciidoc3 not found. Live preview will use plain text.")
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================
# These values control application behavior and can be adjusted as needed

# Application Identity
APP_NAME = "AsciiDoc Artisan"
APP_VERSION = "1.0.0"
DEFAULT_FILENAME = "untitled.adoc"

# UI Configuration
PREVIEW_UPDATE_INTERVAL_MS = 350  # Milliseconds between preview updates
PREVIEW_DEBOUNCE_MS = 150        # Debounce time for keystrokes
EDITOR_FONT_FAMILY = "Courier New"
EDITOR_FONT_SIZE = 18            # Optimized for 5K displays
MIN_FONT_SIZE = 10               # Minimum readable font size
MAX_FONT_SIZE = 72               # Maximum font size
ZOOM_STEP = 1                    # Font size change per zoom action

# File Paths
SETTINGS_FILENAME = "AsciiDocArtisan.json"
LOG_FILENAME = "AsciiDocArtisan.log"

# Window Geometry (optimized for 5K displays)
DEFAULT_WINDOW_WIDTH = 4096      # 80% of 5120 (5K width)
DEFAULT_WINDOW_HEIGHT = 2304     # 80% of 2880 (5K height)

# Process Timeouts (in seconds)
GIT_COMMAND_TIMEOUT = 30         # Maximum time for git operations
PANDOC_TIMEOUT = 60              # Maximum time for document conversion

# File Dialog Filters
# These define what files appear in open/save dialogs
ADOC_FILTER = "AsciiDoc Files (*.adoc *.asciidoc)"
DOCX_FILTER = "Word Documents (*.docx)"
ALL_FILES_FILTER = "All Files (*)"
SUPPORTED_OPEN_FILTER = (
    f"All Supported Files (*.adoc *.asciidoc *.docx);;"
    f"{ADOC_FILTER};;{DOCX_FILTER};;{ALL_FILES_FILTER}"
)
SUPPORTED_SAVE_FILTER = f"{ADOC_FILTER};;{ALL_FILES_FILTER}"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Set up comprehensive logging for debugging and monitoring

def setup_logging() -> logging.Logger:
    """
    Configure application-wide logging.

    Creates a logger that writes to both file and console with appropriate
    formatting and log levels.

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter('%(levelname)s: %(message)s')

    # File handler for detailed logs
    try:
        log_path = Path.home() / ".asciidoc-artisan" / LOG_FILENAME
        log_path.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")

    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logging()

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================
# Type-safe representations of states and data

class GitOperation(Enum):
    """Enumeration of all possible Git operations."""
    NONE = auto()
    PULL = auto()
    COMMIT_ADD = auto()
    COMMIT_FINALIZE = auto()
    PUSH = auto()
    STATUS = auto()

class ProcessingState(Enum):
    """Application processing states."""
    IDLE = auto()
    PROCESSING_GIT = auto()
    PROCESSING_PANDOC = auto()
    OPENING_FILE = auto()
    SAVING_FILE = auto()

@dataclass
class AppSettings:
    """
    Application settings data structure.

    This class holds all persistent application settings that are
    saved between sessions.
    """
    last_directory: str
    git_repo_path: Optional[str]
    dark_mode: bool
    window_maximized: bool
    window_geometry: Optional[Dict[str, int]]
    font_size: int
    preview_interval: int
    autosave_enabled: bool
    autosave_interval: int

    @classmethod
    def default(cls) -> 'AppSettings':
        """Create settings with default values."""
        return cls(
            last_directory=str(Path.home() / "Documents"),
            git_repo_path=None,
            dark_mode=True,
            window_maximized=True,
            window_geometry=None,
            font_size=EDITOR_FONT_SIZE,
            preview_interval=PREVIEW_UPDATE_INTERVAL_MS,
            autosave_enabled=True,
            autosave_interval=300,  # 5 minutes
        )

class GitResult(NamedTuple):
    """
    Result of a Git command execution.

    Attributes:
        success: Whether the command executed successfully
        stdout: Standard output from the command
        stderr: Standard error output from the command
        exit_code: Process exit code (None if process failed to start)
        user_message: Human-readable message for the user
    """
    success: bool
    stdout: str
    stderr: str
    exit_code: Optional[int]
    user_message: str

# ============================================================================
# UTILITY FUNCTIONS AND DECORATORS
# ============================================================================

def debounce(wait_time: float):
    """
    Decorator that debounces function calls.

    Prevents a function from being called too frequently by delaying
    execution until a certain time has passed without new calls.

    Args:
        wait_time: Seconds to wait before executing

    Example:
        @debounce(0.5)
        def save_file():
            # This will only run 0.5 seconds after the last call
            pass
    """
    def decorator(func: Callable) -> Callable:
        timer: Optional[threading.Timer] = None
        lock = threading.Lock()

        @wraps(func)
        def debounced(*args, **kwargs):
            nonlocal timer

            def call_func():
                with lock:
                    func(*args, **kwargs)

            with lock:
                if timer is not None:
                    timer.cancel()
                timer = threading.Timer(wait_time, call_func)
                timer.start()

        return debounced
    return decorator

@contextmanager
def timed_operation(operation_name: str):
    """
    Context manager for timing operations.

    Logs the duration of any code block for performance monitoring.

    Args:
        operation_name: Description of the operation being timed

    Example:
        with timed_operation("File save"):
            save_large_file()
        # Logs: "File save completed in 0.123 seconds"
    """
    start_time = time.time()
    logger.debug(f"Starting {operation_name}")
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.debug(f"{operation_name} completed in {duration:.3f} seconds")

def sanitize_path(path_str: str) -> Optional[Path]:
    """
    Sanitize and validate a file path.

    Prevents directory traversal attacks and validates paths.

    Args:
        path_str: User-provided path string

    Returns:
        Path object if valid, None if invalid/dangerous
    """
    try:
        path = Path(path_str).resolve()

        # Check for directory traversal attempts
        if ".." in path.parts:
            logger.warning(f"Directory traversal attempt blocked: {path_str}")
            return None

        # Ensure path is under allowed directories
        home_path = Path.home()
        if not (path.is_relative_to(home_path) or
                path.is_relative_to(Path("/tmp")) or
                path.is_relative_to(Path.cwd())):
            logger.warning(f"Path outside allowed directories: {path_str}")
            return None

        return path

    except Exception as e:
        logger.error(f"Invalid path: {path_str} - {e}")
        return None

def sanitize_git_input(text: str) -> str:
    """
    Sanitize text for use in Git commands.

    Removes potentially dangerous characters that could be used
    for command injection or to break Git operations.

    Args:
        text: User input to be sanitized

    Returns:
        Sanitized text safe for Git operations
    """
    # Remove null bytes and control characters except newlines and tabs
    sanitized = text.replace('\0', '')

    # Remove other control characters but keep newlines and tabs
    import string
    allowed_chars = string.printable + '\n\t'
    sanitized = ''.join(c for c in sanitized if c in allowed_chars)

    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()

    # Limit length to prevent extremely long inputs
    max_length = 10000  # Reasonable limit for commit messages
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... (truncated)"

    return sanitized

# ============================================================================
# WORKER THREAD CLASSES
# ============================================================================
# These handle long-running operations without blocking the UI

class GitWorker(QObject):
    """
    Worker thread for Git operations.

    Executes Git commands in a separate thread to keep the UI responsive.
    Emits signals when operations complete.
    """

    # Signal emitted when a Git command completes
    command_complete = Signal(GitResult)

    @Slot(list, str)
    def run_git_command(self, command: List[str], working_dir: str) -> None:
        """
        Execute a Git command asynchronously.

        This method runs in a separate thread to avoid blocking the UI.
        It handles various error conditions and provides user-friendly
        error messages.

        Args:
            command: Git command as a list (e.g., ['git', 'status'])
            working_dir: Directory to run the command in
        """
        # Initialize result variables
        user_message = "Git command failed."
        stdout, stderr = "", ""
        exit_code = None

        try:
            # Validate working directory
            safe_path = sanitize_path(working_dir)
            if not safe_path or not safe_path.is_dir():
                user_message = f"Invalid or non-existent directory: {working_dir}"
                logger.error(user_message)
                result = GitResult(False, "", user_message, None, user_message)
                self.command_complete.emit(result)
                return

            logger.info(f"Executing Git command: {' '.join(command)} in {safe_path}")

            # Prepare environment (inherit current environment)
            env = os.environ.copy()

            # Execute Git command with timeout
            process = subprocess.run(
                command,
                cwd=str(safe_path),
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
                encoding='utf-8',
                errors='replace',  # Replace invalid UTF-8 sequences
                env=env,
                timeout=GIT_COMMAND_TIMEOUT  # Prevent hanging
            )

            # Capture results
            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            # Determine success and create appropriate user message
            if exit_code == 0:
                logger.info(f"Git command successful: {' '.join(command)}")
                if stderr:
                    logger.warning(f"Git stderr (exit 0): {stderr}")
                result = GitResult(True, stdout, stderr, exit_code, "Git command successful.")
            else:
                # Analyze error and provide helpful message
                user_message = self._analyze_git_error(stderr, stdout, command)
                logger.error(f"Git command failed (exit {exit_code}): {user_message}")
                result = GitResult(False, stdout, stderr, exit_code, user_message)

            self.command_complete.emit(result)

        except subprocess.TimeoutExpired:
            user_message = f"Git command timed out after {GIT_COMMAND_TIMEOUT} seconds"
            logger.error(user_message)
            self.command_complete.emit(GitResult(False, "", user_message, None, user_message))

        except FileNotFoundError:
            user_message = "Git not found. Please install Git and ensure it's in your system PATH."
            logger.error(user_message)
            self.command_complete.emit(GitResult(False, "", user_message, None, user_message))

        except Exception as e:
            user_message = f"Unexpected error running Git: {type(e).__name__}: {e}"
            logger.exception("Unexpected Git error")
            self.command_complete.emit(GitResult(False, stdout, str(e), exit_code, user_message))

    def _analyze_git_error(self, stderr: str, stdout: str, command: List[str]) -> str:
        """
        Analyze Git error output and provide user-friendly message.

        Examines error text to determine the likely cause and suggests
        solutions.

        Args:
            stderr: Standard error output from Git
            stdout: Standard output from Git
            command: The command that was executed

        Returns:
            Human-readable error message with suggestions
        """
        stderr_lower = stderr.lower()

        # Check for common error patterns
        error_patterns = {
            "authentication failed": "Git Authentication Failed. Check your credentials (SSH key/token/credential helper).",
            "permission denied": "Permission denied. Check repository access rights and authentication.",
            "not a git repository": "Not a Git repository. Initialize with 'git init' or clone an existing repository.",
            "could not resolve host": "Cannot connect to remote. Check internet connection and repository URL.",
            "unmerged files": "Merge conflicts exist. Resolve conflicts and commit changes.",
            "uncommitted changes": "Uncommitted changes would be overwritten. Commit or stash changes first.",
            "remote contains work": "Remote has new changes. Pull first, resolve any conflicts, then push.",
            "nothing to commit": "No changes to commit. Working directory is clean.",
            "changes not staged": "No changes staged. Use 'git add' to stage changes first.",
            "repository not found": "Repository not found. Check the remote URL.",
            "branch diverged": "Local and remote branches have diverged. Merge or rebase required."
        }

        # Find matching error pattern
        for pattern, message in error_patterns.items():
            if pattern in stderr_lower:
                return message

        # Generic message if no pattern matches
        return f"Git command failed: {stderr[:200]}{'...' if len(stderr) > 200 else ''}"

class PandocWorker(QObject):
    """
    Worker thread for Pandoc document conversions.

    Handles conversions between document formats (e.g., DOCX to AsciiDoc)
    in a separate thread.
    """

    # Signals for conversion results
    conversion_complete = Signal(str, str)  # (result_text, context)
    conversion_error = Signal(str, str)     # (error_message, context)

    @Slot(object, str, str, str)
    def run_pandoc_conversion(
        self,
        source: Union[str, bytes],
        to_format: str,
        from_format: str,
        context: str
    ) -> None:
        """
        Convert document content between formats using Pandoc.

        Args:
            source: Source content (text or binary data)
            to_format: Target format (e.g., 'asciidoc')
            from_format: Source format (e.g., 'docx', 'html')
            context: Description of the operation for logging
        """
        # Check if Pandoc is available
        if not PANDOC_AVAILABLE or not pypandoc:
            error_msg = "Pandoc is not available. Please install pandoc and pypandoc."
            logger.error(error_msg)
            self.conversion_error.emit(error_msg, context)
            return

        # Prepare conversion arguments
        extra_args = []
        is_docx_to_adoc = (from_format == 'docx' and to_format == 'asciidoc')

        if is_docx_to_adoc:
            # Special handling for DOCX to AsciiDoc conversion
            extra_args.extend([
                '--number-sections',      # Number sections automatically
                '--wrap=none',            # Don't wrap lines
                '--extract-media=media',  # Extract embedded images
            ])
            logger.info(f"DOCX to AsciiDoc conversion with args: {extra_args}")

        try:
            # Perform conversion
            logger.info(f"Starting Pandoc conversion: {context}")
            with timed_operation(f"Pandoc {from_format} to {to_format}"):
                result_text = pypandoc.convert_text(
                    source=source,
                    to=to_format,
                    format=from_format,
                    extra_args=extra_args
                )

            # Post-process for specific conversions
            if is_docx_to_adoc:
                result_text = self._enhance_asciidoc_output(result_text)

            logger.info(f"Pandoc conversion successful: {context}")
            self.conversion_complete.emit(result_text, context)

        except Exception as e:
            # Handle conversion errors
            error_msg = self._analyze_pandoc_error(e, context)
            logger.exception(f"Pandoc conversion failed: {context}")
            self.conversion_error.emit(error_msg, context)

    def _enhance_asciidoc_output(self, asciidoc_text: str) -> str:
        """
        Enhance AsciiDoc output from Pandoc conversion.

        Adds standard AsciiDoc headers and improves formatting.

        Args:
            asciidoc_text: Raw AsciiDoc from Pandoc

        Returns:
            Enhanced AsciiDoc text
        """
        # Add table of contents directives
        toc_directives = ":toc:\n:toc-title: Table of Contents\n:toclevels: 3\n\n"

        # Split into lines for processing
        lines = asciidoc_text.split('\n', 1)

        # If document starts with a title, insert TOC after it
        if lines and lines[0].startswith('= '):
            if len(lines) > 1:
                enhanced = f"{lines[0]}\n{toc_directives}{lines[1]}"
            else:
                enhanced = f"{lines[0]}\n{toc_directives}"
        else:
            # Otherwise, prepend TOC
            enhanced = toc_directives + asciidoc_text

        return enhanced

    def _analyze_pandoc_error(self, error: Exception, context: str) -> str:
        """
        Analyze Pandoc errors and provide helpful messages.

        Args:
            error: The exception that occurred
            context: Description of what was being converted

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        error_str = str(error)

        if isinstance(error, (OSError, FileNotFoundError)) or "pandoc wasn't found" in error_str:
            return (
                "Pandoc Not Found\n\n"
                "Please install Pandoc from https://pandoc.org/installing.html\n"
                "and ensure it's in your system PATH."
            )
        elif isinstance(error, RuntimeError) and "pandoc exited with code" in error_str:
            return (
                f"Pandoc Conversion Error\n\n"
                f"Pandoc failed to convert the document.\n"
                f"This may be due to unsupported content or format issues.\n\n"
                f"Details: {error_str[:200]}"
            )
        else:
            return f"Conversion Error ({error_type})\n\n{error_str[:300]}"

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class AsciiDocEditor(QMainWindow):
    """
    Main application window for AsciiDoc Artisan.

    This class manages the entire application, including:
    - User interface setup and management
    - File operations (open, save, convert)
    - Git integration
    - Live preview functionality
    - Settings persistence
    """

    # Custom signals for thread communication
    request_git_command = Signal(list, str)
    request_pandoc_conversion = Signal(object, str, str, str)

    def __init__(self, original_palette: Optional[QPalette] = None) -> None:
        """
        Initialize the AsciiDoc editor.

        Args:
            original_palette: System's original color palette for theme switching
        """
        super().__init__()

        # Store original palette for light mode
        self._original_palette = original_palette

        # Initialize application state
        self._init_state()

        # Load saved settings
        self._settings = self._load_settings()

        # Set up the user interface
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._apply_theme()

        # Initialize worker threads
        self._setup_workers()

        # Update UI based on current state
        self._update_ui_state()

        # Show welcome message
        self._show_welcome_message()

        logger.info("AsciiDoc Artisan initialized successfully")

    def _init_state(self) -> None:
        """Initialize application state variables."""
        # File management
        self._current_file: Optional[Path] = None
        self._last_saved_content: str = ""

        # Processing state
        self._state = ProcessingState.IDLE
        self._git_operation = GitOperation.NONE

        # Pending operations
        self._pending_file: Optional[Path] = None
        self._pending_commit_msg: Optional[str] = None

        # Preview management
        self._preview_timer: Optional[QTimer] = None
        self._last_preview_update = 0

        # AsciiDoc converter
        self._asciidoc_api: Optional[AsciiDoc3API] = None

    def _setup_ui(self) -> None:
        """Create and configure the user interface."""
        # Create central splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(splitter)

        # Create editor with monospace font
        self.editor = QPlainTextEdit(self)
        font = QFont(EDITOR_FONT_FAMILY, self._settings.font_size)
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.editor.setFont(font)

        # Enable word wrap and set tab size
        self.editor.setWordWrapMode(self.editor.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.editor.setTabStopDistance(
            self.editor.fontMetrics().horizontalAdvance(' ') * 4
        )

        # Connect editor signals with debouncing
        self.editor.textChanged.connect(self._on_text_changed)
        splitter.addWidget(self.editor)

        # Create preview browser
        self.preview = QTextBrowser(self)
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(True)
        splitter.addWidget(self.preview)

        # Set equal sizes for editor and preview
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        # Create status bar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # Set up preview timer
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)

        # Initialize AsciiDoc converter
        self._asciidoc_api = self._init_asciidoc()

    def _create_actions(self) -> None:
        """Create all application actions."""
        # File actions
        self.open_act = QAction(
            "Open…", self,
            shortcut=QKeySequence.StandardKey.Open,
            statusTip="Open a file or convert DOCX",
            triggered=self.open_file
        )

        self.save_act = QAction(
            "Save", self,
            shortcut=QKeySequence.StandardKey.Save,
            statusTip="Save the current document",
            triggered=self.save_file
        )

        self.save_as_act = QAction(
            "Save As…", self,
            shortcut=QKeySequence.StandardKey.SaveAs,
            statusTip="Save with a new name",
            triggered=lambda: self.save_file(save_as=True)
        )

        self.exit_act = QAction(
            "Exit", self,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip="Exit the application",
            triggered=self.close
        )

        # Edit actions
        self.convert_paste_act = QAction(
            "Convert && Paste from Clipboard", self,
            shortcut="Ctrl+Shift+V",
            statusTip="Convert clipboard content to AsciiDoc",
            triggered=self.convert_and_paste
        )

        # View actions
        self.zoom_in_act = QAction(
            "Zoom In", self,
            shortcut=QKeySequence.StandardKey.ZoomIn,
            statusTip="Increase font size",
            triggered=lambda: self._zoom(1)
        )

        self.zoom_out_act = QAction(
            "Zoom Out", self,
            shortcut=QKeySequence.StandardKey.ZoomOut,
            statusTip="Decrease font size",
            triggered=lambda: self._zoom(-1)
        )

        self.dark_mode_act = QAction(
            "Dark Mode", self,
            checkable=True,
            checked=self._settings.dark_mode,
            statusTip="Toggle dark mode",
            triggered=self._toggle_theme
        )

        # Git actions
        self.set_repo_act = QAction(
            "Set Repository…", self,
            statusTip="Choose Git repository location",
            triggered=self._select_git_repo
        )

        self.git_commit_act = QAction(
            "&Commit…", self,
            shortcut="Ctrl+Shift+C",
            statusTip="Commit changes to Git",
            triggered=self._git_commit
        )

        self.git_pull_act = QAction(
            "&Pull", self,
            shortcut="Ctrl+Shift+P",
            statusTip="Pull changes from remote",
            triggered=self._git_pull
        )

        self.git_push_act = QAction(
            "P&ush", self,
            shortcut="Ctrl+Shift+U",
            statusTip="Push changes to remote",
            triggered=self._git_push
        )

    def _create_menus(self) -> None:
        """Create application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.save_as_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.convert_paste_act)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.zoom_in_act)
        view_menu.addAction(self.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.dark_mode_act)

        # Git menu
        git_menu = menubar.addMenu("&Git")
        git_menu.addAction(self.set_repo_act)
        git_menu.addSeparator()
        git_menu.addAction(self.git_commit_act)
        git_menu.addAction(self.git_pull_act)
        git_menu.addAction(self.git_push_act)

    def _setup_workers(self) -> None:
        """Initialize worker threads for background operations."""
        # Git worker thread
        self.git_thread = QThread(self)
        self.git_thread.setObjectName("GitWorkerThread")
        self.git_worker = GitWorker()
        self.git_worker.moveToThread(self.git_thread)

        # Connect signals
        self.request_git_command.connect(self.git_worker.run_git_command)
        self.git_worker.command_complete.connect(self._handle_git_result)
        self.git_thread.finished.connect(self.git_worker.deleteLater)

        # Start thread
        self.git_thread.start()

        # Pandoc worker thread
        self.pandoc_thread = QThread(self)
        self.pandoc_thread.setObjectName("PandocWorkerThread")
        self.pandoc_worker = PandocWorker()
        self.pandoc_worker.moveToThread(self.pandoc_thread)

        # Connect signals
        self.request_pandoc_conversion.connect(self.pandoc_worker.run_pandoc_conversion)
        self.pandoc_worker.conversion_complete.connect(self._handle_pandoc_result)
        self.pandoc_worker.conversion_error.connect(self._handle_pandoc_error)
        self.pandoc_thread.finished.connect(self.pandoc_worker.deleteLater)

        # Start thread
        self.pandoc_thread.start()

        logger.info("Worker threads initialized")

    def _load_settings(self) -> AppSettings:
        """
        Load settings from disk or create defaults.

        Returns:
            AppSettings object with loaded or default settings
        """
        settings_path = self._get_settings_path()

        if not settings_path.exists():
            logger.info("No settings file found, using defaults")
            return AppSettings.default()

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Create settings with defaults, then update with loaded values
            settings = AppSettings.default()

            # Update each field if present in loaded data
            if 'last_directory' in data and Path(data['last_directory']).is_dir():
                settings.last_directory = data['last_directory']

            if 'git_repo_path' in data:
                settings.git_repo_path = data['git_repo_path']

            if 'dark_mode' in data:
                settings.dark_mode = bool(data['dark_mode'])

            if 'window_maximized' in data:
                settings.window_maximized = bool(data['window_maximized'])

            if 'window_geometry' in data:
                settings.window_geometry = data['window_geometry']

            if 'font_size' in data:
                settings.font_size = max(MIN_FONT_SIZE,
                                        min(MAX_FONT_SIZE, int(data['font_size'])))

            logger.info("Settings loaded successfully")
            return settings

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self._show_message(
                "warning",
                "Settings Load Error",
                f"Could not load settings: {e}\nUsing defaults."
            )
            return AppSettings.default()

    def _save_settings(self) -> None:
        """Save current settings to disk."""
        settings_path = self._get_settings_path()

        # Prepare settings data
        settings_data = {
            'last_directory': self._settings.last_directory,
            'git_repo_path': self._settings.git_repo_path,
            'dark_mode': self.dark_mode_act.isChecked(),
            'font_size': self.editor.font().pointSize(),
            'window_maximized': self.isMaximized(),
        }

        # Add window geometry if not maximized
        if not self.isMaximized():
            geom = self.geometry()
            settings_data['window_geometry'] = {
                'x': geom.x(),
                'y': geom.y(),
                'width': geom.width(),
                'height': geom.height()
            }

        try:
            # Ensure settings directory exists
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Write settings
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)

            logger.info("Settings saved successfully")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def _get_settings_path(self) -> Path:
        """Get the path for settings file."""
        config_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppConfigLocation
        )

        if config_dir:
            return Path(config_dir) / APP_NAME / SETTINGS_FILENAME
        else:
            # Fallback to home directory
            return Path.home() / f".{APP_NAME.lower()}" / SETTINGS_FILENAME

    @lru_cache(maxsize=1)
    def _init_asciidoc(self) -> Optional[AsciiDoc3API]:
        """
        Initialize AsciiDoc converter with caching.

        Returns:
            Configured AsciiDoc3API instance or None if unavailable
        """
        if not ASCIIDOC3_AVAILABLE or not AsciiDoc3API:
            return None

        try:
            api = AsciiDoc3API(asciidoc3.__file__)
            api.options("--no-header-footer")
            logger.info("AsciiDoc3 API initialized")
            return api
        except Exception as e:
            logger.error(f"Failed to initialize AsciiDoc3: {e}")
            return None

    def _apply_theme(self) -> None:
        """Apply the current theme settings."""
        app = QApplication.instance()
        if not app:
            return

        if self.dark_mode_act.isChecked():
            apply_dark_theme(app)
        else:
            if self._original_palette:
                app.setPalette(self._original_palette)
            else:
                logger.warning("No original palette available for light theme")

    def _show_welcome_message(self) -> None:
        """Display welcome message in status bar."""
        if self._settings.git_repo_path:
            self.statusBar.showMessage(
                f"Ready. Git: {Path(self._settings.git_repo_path).name}"
            )
        else:
            self.statusBar.showMessage("Ready. Set Git repository via Git menu.")

    def _update_ui_state(self) -> None:
        """Update UI element states based on current application state."""
        # Determine what should be enabled
        is_idle = (self._state == ProcessingState.IDLE)
        git_ready = bool(self._settings.git_repo_path) and is_idle
        pandoc_ready = PANDOC_AVAILABLE and is_idle

        # File operations
        self.open_act.setEnabled(is_idle)
        self.save_act.setEnabled(is_idle and self._current_file is not None)
        self.save_as_act.setEnabled(is_idle)

        # Edit operations
        self.convert_paste_act.setEnabled(pandoc_ready)

        # Git operations
        self.set_repo_act.setEnabled(is_idle)
        self.git_commit_act.setEnabled(git_ready)
        self.git_pull_act.setEnabled(git_ready)
        self.git_push_act.setEnabled(git_ready)

    def _show_message(self, level: str, title: str, message: str) -> None:
        """
        Show a message dialog to the user.

        Args:
            level: Message level ('info', 'warning', 'critical', 'question')
            title: Dialog title
            message: Message text
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{APP_NAME} - {title}")
        msg_box.setText(message)

        icon_map = {
            'info': QMessageBox.Icon.Information,
            'warning': QMessageBox.Icon.Warning,
            'critical': QMessageBox.Icon.Critical,
            'question': QMessageBox.Icon.Question
        }

        msg_box.setIcon(icon_map.get(level, QMessageBox.Icon.NoIcon))
        msg_box.exec()

    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.windowTitle().endswith("*")

    def _mark_as_modified(self) -> None:
        """Mark the document as having unsaved changes."""
        if not self.windowTitle().endswith("*"):
            self.setWindowTitle(f"{self.windowTitle()}*")

    def _on_text_changed(self) -> None:
        """Handle text changes in the editor."""
        if self._state == ProcessingState.OPENING_FILE:
            return  # Ignore changes while loading

        # Mark as modified
        if self._current_file:
            self._mark_as_modified()

        # Reset preview timer for debouncing
        if self._preview_timer:
            self._preview_timer.stop()
            self._preview_timer.start(PREVIEW_DEBOUNCE_MS)

    def _update_preview(self) -> None:
        """Update the preview pane with rendered content."""
        with timed_operation("Preview update"):
            source = self.editor.toPlainText()
            html = self._render_asciidoc(source)

            # Preserve scroll position
            scrollbar = self.preview.verticalScrollBar()
            scroll_pos = scrollbar.value()

            self.preview.setHtml(html)

            # Restore scroll position
            scrollbar.setValue(scroll_pos)

    def _render_asciidoc(self, source: str) -> str:
        """
        Render AsciiDoc source to HTML.

        Args:
            source: AsciiDoc source text

        Returns:
            Complete HTML document with styling
        """
        # Convert AsciiDoc to HTML body
        if self._asciidoc_api:
            try:
                infile = io.StringIO(source)
                outfile = io.StringIO()
                self._asciidoc_api.execute(infile, outfile, backend="html5")
                body = outfile.getvalue()
            except Exception as e:
                logger.error(f"AsciiDoc rendering failed: {e}")
                body = self._render_error(e)
        else:
            # Fallback to plain text
            body = f"<pre>{html.escape(source)}</pre>"

        # Wrap in complete HTML document
        style = self._get_preview_style()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Preview</title>
            {style}
        </head>
        <body>
            {body}
        </body>
        </html>
        """

    def _render_error(self, error: Exception) -> str:
        """Render an error message for the preview."""
        return f"""
        <div class="error">
            <h3>Rendering Error</h3>
            <pre>{html.escape(str(error))}</pre>
        </div>
        """

    def _get_preview_style(self) -> str:
        """Get CSS styles for preview based on current theme."""
        if self.dark_mode_act.isChecked():
            return DARK_PREVIEW_STYLE
        else:
            return LIGHT_PREVIEW_STYLE

    @Slot()
    def open_file(self) -> None:
        """Open a file or convert DOCX."""
        # Check for unsaved changes
        if self._has_unsaved_changes():
            response = self._prompt_save_changes("opening a new file")
            if response == "cancel":
                return
            elif response == "save":
                if not self.save_file():
                    return

        # Show file dialog
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self._settings.last_directory,
            SUPPORTED_OPEN_FILTER
        )

        if not path:
            return

        file_path = Path(path)
        self._settings.last_directory = str(file_path.parent)

        # Handle different file types
        if file_path.suffix.lower() == '.docx':
            self._convert_docx_file(file_path)
        elif file_path.suffix.lower() in ['.adoc', '.asciidoc']:
            self._open_asciidoc_file(file_path)
        else:
            self._show_message(
                "warning",
                "Unsupported File Type",
                f"Cannot open files of type: {file_path.suffix}"
            )

    def _open_asciidoc_file(self, path: Path) -> None:
        """Open an AsciiDoc file."""
        try:
            self._state = ProcessingState.OPENING_FILE
            content = path.read_text(encoding='utf-8')

            # Load into editor
            self.editor.setPlainText(content)
            self._current_file = path
            self._last_saved_content = content

            # Update UI
            self.setWindowTitle(f"{APP_NAME} - {path.name}")
            self.statusBar.showMessage(f"Opened: {path}")

            # Update preview
            self._update_preview()

        except Exception as e:
            logger.exception(f"Failed to open file: {path}")
            self._show_message(
                "critical",
                "Open Error",
                f"Failed to open file:\n{path}\n\nError: {e}"
            )
        finally:
            self._state = ProcessingState.IDLE
            self._update_ui_state()

    def _convert_docx_file(self, path: Path) -> None:
        """Convert and open a DOCX file."""
        if not PANDOC_AVAILABLE:
            self._show_message(
                "critical",
                "Pandoc Not Available",
                "DOCX conversion requires Pandoc.\n"
                "Please install pandoc and pypandoc."
            )
            return

        # Set processing state
        self._state = ProcessingState.PROCESSING_PANDOC
        self._pending_file = path
        self._update_ui_state()

        # Update status
        self.statusBar.showMessage(f"Converting {path.name}...")

        # Read file and request conversion
        try:
            content = path.read_bytes()
            self.request_pandoc_conversion.emit(
                content,
                'asciidoc',
                'docx',
                f'converting {path.name}'
            )
        except Exception as e:
            logger.exception(f"Failed to read DOCX file: {path}")
            self._show_message(
                "critical",
                "Read Error",
                f"Failed to read file:\n{path}\n\nError: {e}"
            )
            self._state = ProcessingState.IDLE
            self._pending_file = None
            self._update_ui_state()

    @Slot()
    def save_file(self, save_as: bool = False) -> bool:
        """
        Save the current file.

        Args:
            save_as: Whether to show save dialog even if file has a path

        Returns:
            True if saved successfully, False otherwise
        """
        # Determine save path
        if save_as or not self._current_file:
            path = self._get_save_path()
            if not path:
                return False
        else:
            path = self._current_file

        # Save file
        try:
            self._state = ProcessingState.SAVING_FILE
            content = self.editor.toPlainText()

            with timed_operation(f"Saving {path.name}"):
                path.write_text(content, encoding='utf-8')

            # Update state
            self._current_file = path
            self._last_saved_content = content
            self._settings.last_directory = str(path.parent)

            # Update UI
            self.setWindowTitle(f"{APP_NAME} - {path.name}")
            self.statusBar.showMessage(f"Saved: {path}")

            logger.info(f"File saved: {path}")
            return True

        except Exception as e:
            logger.exception(f"Failed to save file: {path}")
            self._show_message(
                "critical",
                "Save Error",
                f"Failed to save file:\n{path}\n\nError: {e}"
            )
            return False
        finally:
            self._state = ProcessingState.IDLE
            self._update_ui_state()

    def _get_save_path(self) -> Optional[Path]:
        """Get path for saving via dialog."""
        # Determine suggested name
        if self._current_file:
            suggested = str(self._current_file)
        else:
            suggested = str(Path(self._settings.last_directory) / DEFAULT_FILENAME)

        # Show save dialog
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            suggested,
            SUPPORTED_SAVE_FILTER
        )

        if not path:
            return None

        # Ensure proper extension
        path_obj = Path(path)
        if path_obj.suffix.lower() not in ['.adoc', '.asciidoc']:
            path_obj = path_obj.with_suffix('.adoc')

        return path_obj

    @Slot()
    def convert_and_paste(self) -> None:
        """Convert clipboard content and paste as AsciiDoc."""
        if not PANDOC_AVAILABLE:
            self._show_message(
                "warning",
                "Pandoc Not Available",
                "Clipboard conversion requires Pandoc."
            )
            return

        # Get clipboard content
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()

        # Determine source format and content
        if mime_data.hasHtml():
            source = mime_data.html()
            source_format = "html"
        elif mime_data.hasText():
            source = mime_data.text()
            source_format = "markdown"  # Assume markdown for plain text
        else:
            self._show_message(
                "info",
                "No Content",
                "Clipboard contains no text or HTML to convert."
            )
            return

        # Request conversion
        self._state = ProcessingState.PROCESSING_PANDOC
        self._update_ui_state()
        self.statusBar.showMessage("Converting clipboard content...")

        self.request_pandoc_conversion.emit(
            source,
            'asciidoc',
            source_format,
            'clipboard conversion'
        )

    def _zoom(self, direction: int) -> None:
        """
        Zoom editor and preview.

        Args:
            direction: 1 to zoom in, -1 to zoom out
        """
        # Update editor font
        font = self.editor.font()
        new_size = font.pointSize() + (direction * ZOOM_STEP)
        new_size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, new_size))

        if new_size != font.pointSize():
            font.setPointSize(new_size)
            self.editor.setFont(font)

        # Update preview zoom
        self.preview.zoomIn(direction)

        # Show current zoom level
        self.statusBar.showMessage(f"Font size: {new_size}pt", 2000)

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self._apply_theme()
        self._update_preview()  # Re-render with new theme

        theme_name = "Dark" if self.dark_mode_act.isChecked() else "Light"
        logger.info(f"Switched to {theme_name} theme")

    def _select_git_repo(self) -> None:
        """Select Git repository directory."""
        start_dir = self._settings.git_repo_path or self._settings.last_directory

        path = QFileDialog.getExistingDirectory(
            self,
            "Select Git Repository",
            start_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if not path:
            return

        # Verify it's a Git repository
        git_dir = Path(path) / ".git"
        if not git_dir.is_dir():
            self._show_message(
                "warning",
                "Not a Git Repository",
                f"Selected directory is not a Git repository:\n{path}\n\n"
                "Initialize with 'git init' or select a different directory."
            )
            return

        # Save selection
        self._settings.git_repo_path = path
        self._update_ui_state()
        self.statusBar.showMessage(f"Git repository: {Path(path).name}")
        logger.info(f"Git repository set to: {path}")

    def _git_commit(self) -> None:
        """Commit changes to Git."""
        if not self._ensure_git_ready():
            return

        # Save current file if modified
        if self._has_unsaved_changes():
            if not self.save_file():
                return

        # Get commit message
        message, ok = QInputDialog.getMultiLineText(
            self,
            "Commit Changes",
            "Enter commit message:",
            ""
        )

        if not ok:
            return

        # Sanitize and validate message
        message = sanitize_git_input(message)
        if not message:
            self._show_message(
                "warning",
                "Empty Message",
                "Please provide a commit message."
            )
            return

        # Start commit process
        self._state = ProcessingState.PROCESSING_GIT
        self._git_operation = GitOperation.COMMIT_ADD
        self._pending_commit_msg = message
        self._update_ui_state()

        self.statusBar.showMessage("Adding files to Git...")
        self.request_git_command.emit(
            ["git", "add", "."],
            self._settings.git_repo_path
        )

    def _git_pull(self) -> None:
        """Pull changes from remote."""
        if not self._ensure_git_ready():
            return

        # Check for unsaved changes
        if self._has_unsaved_changes():
            response = self._prompt_save_changes("pulling changes")
            if response == "cancel":
                return
            elif response == "save":
                if not self.save_file():
                    return

        # Execute pull
        self._state = ProcessingState.PROCESSING_GIT
        self._git_operation = GitOperation.PULL
        self._update_ui_state()

        self.statusBar.showMessage("Pulling from remote...")
        self.request_git_command.emit(
            ["git", "pull"],
            self._settings.git_repo_path
        )

    def _git_push(self) -> None:
        """Push changes to remote."""
        if not self._ensure_git_ready():
            return

        # Execute push
        self._state = ProcessingState.PROCESSING_GIT
        self._git_operation = GitOperation.PUSH
        self._update_ui_state()

        self.statusBar.showMessage("Pushing to remote...")
        self.request_git_command.emit(
            ["git", "push"],
            self._settings.git_repo_path
        )

    def _ensure_git_ready(self) -> bool:
        """Check if Git operations can proceed."""
        if not self._settings.git_repo_path:
            self._show_message(
                "info",
                "No Repository",
                "Please set a Git repository first using the Git menu."
            )
            return False

        if self._state != ProcessingState.IDLE:
            self._show_message(
                "warning",
                "Busy",
                "Another operation is in progress. Please wait."
            )
            return False

        return True

    def _prompt_save_changes(self, action: str) -> str:
        """
        Prompt user about unsaved changes.

        Args:
            action: Description of action requiring the prompt

        Returns:
            'save', 'discard', or 'cancel'
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{APP_NAME} - Unsaved Changes")
        msg_box.setText(f"Save changes before {action}?")
        msg_box.setInformativeText("Your changes will be lost if you don't save them.")

        save_btn = msg_box.addButton("Save", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg_box.addButton("Don't Save", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.setDefaultButton(save_btn)
        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked == save_btn:
            return "save"
        elif clicked == discard_btn:
            return "discard"
        else:
            return "cancel"

    @Slot(GitResult)
    def _handle_git_result(self, result: GitResult) -> None:
        """Handle Git operation results."""
        operation = self._git_operation

        # Reset state
        self._state = ProcessingState.IDLE
        self._git_operation = GitOperation.NONE
        self._update_ui_state()

        # Handle based on operation type
        if operation == GitOperation.COMMIT_ADD:
            if result.success:
                # Continue with commit
                self._state = ProcessingState.PROCESSING_GIT
                self._git_operation = GitOperation.COMMIT_FINALIZE
                self._update_ui_state()

                self.statusBar.showMessage("Committing changes...")
                self.request_git_command.emit(
                    ["git", "commit", "-m", self._pending_commit_msg],
                    self._settings.git_repo_path
                )
            else:
                self._pending_commit_msg = None
                self._show_message("critical", "Git Error", result.user_message)

        elif operation == GitOperation.COMMIT_FINALIZE:
            self._pending_commit_msg = None
            if result.success or "nothing to commit" in result.stderr:
                if "nothing to commit" in result.stderr:
                    self._show_message("info", "No Changes", "Nothing to commit.")
                else:
                    self._show_message("info", "Success", "Changes committed.")
                    self.statusBar.showMessage("Committed successfully", 3000)
            else:
                self._show_message("critical", "Commit Failed", result.user_message)

        elif operation == GitOperation.PULL:
            if result.success:
                self._show_message("info", "Success", "Pulled latest changes.")
                self.statusBar.showMessage("Pull successful", 3000)
                # Reload current file if it might have changed
                self._reload_current_file()
            else:
                self._show_message("critical", "Pull Failed", result.user_message)

        elif operation == GitOperation.PUSH:
            if result.success:
                self._show_message("info", "Success", "Pushed changes to remote.")
                self.statusBar.showMessage("Push successful", 3000)
            else:
                self._show_message("critical", "Push Failed", result.user_message)

    @Slot(str, str)
    def _handle_pandoc_result(self, result: str, context: str) -> None:
        """Handle Pandoc conversion results."""
        self._state = ProcessingState.IDLE
        self._update_ui_state()

        if context == "clipboard conversion":
            # Insert at cursor
            self.editor.insertPlainText(result)
            self.statusBar.showMessage("Pasted converted content", 3000)

        elif context.startswith("converting"):
            # Load converted file
            if self._pending_file:
                self.editor.setPlainText(result)
                self._current_file = self._pending_file.with_suffix('.adoc')
                self._last_saved_content = ""  # Mark as unsaved

                self.setWindowTitle(f"{APP_NAME} - {self._current_file.name}*")
                self.statusBar.showMessage(f"Converted: {self._pending_file.name}")
                self._update_preview()

                self._pending_file = None

    @Slot(str, str)
    def _handle_pandoc_error(self, error: str, context: str) -> None:
        """Handle Pandoc conversion errors."""
        self._state = ProcessingState.IDLE
        self._pending_file = None
        self._update_ui_state()

        self._show_message("critical", "Conversion Error", error)
        self.statusBar.showMessage("Conversion failed", 3000)

    def _reload_current_file(self) -> None:
        """Reload current file if it exists."""
        if not self._current_file or not self._current_file.exists():
            return

        try:
            # Check if file is in repository
            if self._settings.git_repo_path:
                repo_path = Path(self._settings.git_repo_path)
                try:
                    self._current_file.relative_to(repo_path)
                    # File is in repo, reload it
                    self._open_asciidoc_file(self._current_file)
                except ValueError:
                    # File not in repository
                    pass
        except Exception as e:
            logger.error(f"Failed to reload file: {e}")

    def closeEvent(self, event) -> None:
        """Handle application close event."""
        # Check for unsaved changes
        if self._has_unsaved_changes():
            response = self._prompt_save_changes("exiting")
            if response == "cancel":
                event.ignore()
                return
            elif response == "save":
                if not self.save_file():
                    event.ignore()
                    return

        # Save settings
        self._save_settings()

        # Stop worker threads
        logger.info("Stopping worker threads...")
        self.git_thread.quit()
        self.pandoc_thread.quit()

        # Wait for threads to finish
        if not self.git_thread.wait(1000):
            logger.warning("Git thread did not stop gracefully")
            self.git_thread.terminate()

        if not self.pandoc_thread.wait(1000):
            logger.warning("Pandoc thread did not stop gracefully")
            self.pandoc_thread.terminate()

        logger.info("Application closing")
        event.accept()

# ============================================================================
# THEME STYLES
# ============================================================================

DARK_PREVIEW_STYLE = """
<style>
body {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    margin: 20px;
    max-width: 900px;
}

h1, h2, h3, h4, h5, h6 {
    color: #e0e0e0;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 { border-bottom: 2px solid #444; padding-bottom: 0.3em; }
h2 { border-bottom: 1px solid #333; padding-bottom: 0.2em; }

a { color: #69b7ff; text-decoration: none; }
a:hover { text-decoration: underline; }

code {
    background-color: #2d2d2d;
    border: 1px solid #3e3e3e;
    border-radius: 3px;
    padding: 0.2em 0.4em;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 0.9em;
}

pre {
    background-color: #2d2d2d;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    padding: 1em;
    overflow-x: auto;
}

pre code {
    background-color: transparent;
    border: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #4a4a4a;
    margin-left: 0;
    padding-left: 1em;
    color: #aaa;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #444;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #2d2d2d;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #252525;
}

.error {
    background-color: #3c1414;
    border: 1px solid #c41414;
    color: #ff6b6b;
    padding: 1em;
    border-radius: 5px;
    margin: 1em 0;
}

.admonition {
    padding: 1em;
    margin: 1em 0;
    border-radius: 5px;
    border-left: 4px solid;
}

.note { background-color: #1e3a5f; border-color: #3a7bc8; }
.tip { background-color: #1e5f3a; border-color: #3ac87a; }
.warning { background-color: #5f3a1e; border-color: #c8783a; }
.important { background-color: #5f1e3a; border-color: #c83a78; }
</style>
"""

LIGHT_PREVIEW_STYLE = """
<style>
body {
    background-color: #ffffff;
    color: #333333;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    margin: 20px;
    max-width: 900px;
}

h1, h2, h3, h4, h5, h6 {
    color: #1a1a1a;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 { border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
h2 { border-bottom: 1px solid #eee; padding-bottom: 0.2em; }

a { color: #0066cc; text-decoration: none; }
a:hover { text-decoration: underline; }

code {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 0.2em 0.4em;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 1em;
    overflow-x: auto;
}

pre code {
    background-color: transparent;
    border: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #ddd;
    margin-left: 0;
    padding-left: 1em;
    color: #666;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

.error {
    background-color: #ffebee;
    border: 1px solid #ffcdd2;
    color: #c62828;
    padding: 1em;
    border-radius: 5px;
    margin: 1em 0;
}

.admonition {
    padding: 1em;
    margin: 1em 0;
    border-radius: 5px;
    border-left: 4px solid;
}

.note { background-color: #e3f2fd; border-color: #2196f3; }
.tip { background-color: #e8f5e9; border-color: #4caf50; }
.warning { background-color: #fff3e0; border-color: #ff9800; }
.important { background-color: #fce4ec; border-color: #e91e63; }
</style>
"""

def apply_dark_theme(app: QApplication) -> None:
    """Apply dark theme to the application."""
    palette = QPalette()

    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(212, 212, 212))

    # Base colors (text fields, etc.)
    palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))

    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(212, 212, 212))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(212, 212, 212))

    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor(105, 183, 255))

    # ToolTip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)

    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.WindowText, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.Text, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.ButtonText, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.HighlightedText, QColor(128, 128, 128))

    app.setPalette(palette)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main application entry point."""
    # Set up high DPI support (Qt6 handles this automatically)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan Team")

    # Store original palette
    original_palette = app.palette()

    # Set Fusion style for consistent appearance
    app.setStyle("Fusion")

    # Suppress warnings from third-party libraries
    warnings.filterwarnings('ignore', category=SyntaxWarning)

    # Create and show main window
    window = AsciiDocEditor(original_palette)

    # Set window geometry
    if window._settings.window_maximized:
        window.showMaximized()
    elif window._settings.window_geometry:
        # Restore saved geometry
        geom = window._settings.window_geometry
        window.setGeometry(geom['x'], geom['y'], geom['width'], geom['height'])
        window.show()
    else:
        # Default size
        window.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # Center on screen
        screen = app.primaryScreen()
        if screen:
            screen_rect = screen.availableGeometry()
            window_rect = window.frameGeometry()
            window_rect.moveCenter(screen_rect.center())
            window.move(window_rect.topLeft())

        window.show()

    # Initial preview update
    window._update_preview()

    # Run application
    logger.info(f"{APP_NAME} v{APP_VERSION} started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()