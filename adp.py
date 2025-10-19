# -*- coding: utf-8 -*-

import sys
import io
import os
import subprocess
import shlex
from pathlib import Path
from typing import Optional, Tuple, NamedTuple, List, Union, Any, Dict
import warnings
import html
import json

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

try:
    import pypandoc
    PANDOC_AVAILABLE = True
except ImportError:
    print("WARNING: 'pypandoc' library not found. DOCX/Clipboard conversion disabled.", file=sys.stderr)
    pypandoc = None
    PANDOC_AVAILABLE = False

try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API
    ASCIIDOC3_AVAILABLE = True
except ImportError:
    print("WARNING: 'asciidoc3' library not found. Live preview will fallback to plain text.", file=sys.stderr)
    asciidoc3 = None
    AsciiDoc3API = None # type: ignore
    ASCIIDOC3_AVAILABLE = False

APP_NAME = "AsciiDoc Artisan"
DEFAULT_FILENAME = "untitled.adoc"
PREVIEW_UPDATE_INTERVAL_MS = 350
EDITOR_FONT_FAMILY = "Courier New"
EDITOR_FONT_SIZE = 13
MIN_FONT_SIZE = 6
ZOOM_STEP = 1
SETTINGS_FILENAME = "AsciiDocArtisan.json"

ADOC_FILTER = "AsciiDoc Files (*.adoc *.asciidoc)"
DOCX_FILTER = "Word Documents (*.docx)"
ALL_FILES_FILTER = "All Files (*)"
SUPPORTED_OPEN_FILTER = f"All Supported Files (*.adoc *.asciidoc *.docx);;{ADOC_FILTER};;{DOCX_FILTER};;{ALL_FILES_FILTER}"
SUPPORTED_SAVE_FILTER = f"{ADOC_FILTER};;{ALL_FILES_FILTER}"

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
        user_message: str = "Git command failed."
        stdout, stderr = "", ""
        exit_code: Optional[int] = None

        try:
            if not Path(working_dir).is_dir():
                user_message = f"Error: Git working directory not found: {working_dir}"
                self.command_complete.emit(GitResult(False, "", user_message, None, user_message))
                return

            print(f"INFO (Thread): Executing Git: {' '.join(command)} in {working_dir}")
            env = os.environ.copy()

            process = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='replace',
                env=env
            )

            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            if exit_code == 0:
                print(f"INFO (Thread): Git command successful: {' '.join(command)}")
                if stderr:
                    print(f"WARN (Thread): Git command stderr (exit code 0): {stderr}")
                result = GitResult(True, stdout, stderr, exit_code, "Git command successful.")
            else:
                print(f"ERROR (Thread): Git command failed (code {exit_code}): {' '.join(command)}\nStderr: {stderr}\nStdout: {stdout}", file=sys.stderr)
                stderr_lower = stderr.lower()
                if "authentication failed" in stderr_lower:
                    user_message = "Git Authentication Failed. Check credentials (SSH key/token/helper)."
                elif "not a git repository" in stderr_lower:
                    user_message = f"Directory is not a Git repository: {working_dir}"
                elif "resolve host" in stderr_lower or "could not resolve hostname" in stderr_lower:
                    user_message = "Could not connect to Git host. Check internet and repository URL."
                elif "pull is not possible because you have unmerged files" in stderr_lower:
                    user_message = "Pull failed: Unmerged files (conflicts). Resolve manually, commit."
                elif "please commit your changes or stash them before you merge" in stderr_lower:
                    user_message = "Pull failed: Uncommitted local changes would be overwritten. Commit or stash first."
                elif "updates were rejected because the remote contains work that you do" in stderr_lower:
                    user_message = "Push rejected: Remote has changes you don't. Pull first, resolve conflicts, then push again."
                elif "nothing to commit" in stderr_lower:
                    user_message = "Nothing to commit."
                elif "changes not staged for commit" in stderr_lower:
                    user_message = "Commit failed: No changes added to commit."
                else:
                    user_message = f"Git command failed (code {exit_code}).\n\nStderr:\n{stderr}"
                result = GitResult(False, stdout, stderr, exit_code, user_message)

            self.command_complete.emit(result)

        except FileNotFoundError:
            error_msg = "Git command not found. Ensure Git is installed and in system PATH."
            print(f"ERROR (Thread): {error_msg}", file=sys.stderr)
            self.command_complete.emit(GitResult(False, "", error_msg, None, error_msg))
        except Exception as e:
            error_msg = f"Unexpected error running Git command: {e}"
            print(f"ERROR (Thread): {error_msg}", file=sys.stderr)
            self.command_complete.emit(GitResult(False, stdout, stderr or str(e), exit_code, error_msg))

class PandocWorker(QObject):
    conversion_complete = Signal(str, str)
    conversion_error = Signal(str, str)

    @Slot(object, str, str, str)
    def run_pandoc_conversion(self, source: Union[str, bytes], to_format: str, from_format: str, context: str) -> None:
        if not PANDOC_AVAILABLE or not pypandoc:
            err = "Pandoc/pypandoc not available for conversion."
            print(f"ERROR (Thread): {err}", file=sys.stderr)
            self.conversion_error.emit(err, context)
            return

        extra_args = []
        is_docx_to_adoc = (from_format == 'docx' and to_format == 'asciidoc')

        if is_docx_to_adoc:
            extra_args.append('--number-sections')
            print(f"INFO (Thread): Using extra args for DOCX->ADOC: {extra_args}")

        try:
            print(f"INFO (Thread): Starting Pandoc conversion ({context}) from {from_format}...")
            result_text = pypandoc.convert_text(
                source=source,
                to=to_format,
                format=from_format,
                extra_args=extra_args
            )
            print(f"INFO (Thread): Pandoc conversion successful ({context}).")

            if is_docx_to_adoc:
                print("INFO (Thread): Prepending AsciiDoc TOC directives.")
                toc_directives = ":toc:\n:toc-title: Table of Contents\n\n"
                lines = result_text.split('\n', 1)
                if len(lines) > 0 and lines[0].startswith('= '):
                    result_text = f"{lines[0]}\n{toc_directives}{lines[1]}" if len(lines) > 1 else f"{lines[0]}\n{toc_directives}"
                else:
                    result_text = toc_directives + result_text

            self.conversion_complete.emit(result_text, context)

        except Exception as e:
            error_type = type(e).__name__
            print(f"ERROR (Thread): Pandoc failed during {context}: {error_type}: {e}", file=sys.stderr)
            title = "Pandoc Error"
            message = f"An error occurred during {context} using Pandoc.\n\n"
            if isinstance(e, (OSError, FileNotFoundError)) or "pandoc wasn't found" in str(e):
                message += "Ensure Pandoc is installed and in system PATH.\n\n"
                title = "Pandoc Not Found / Execution Error"
            elif isinstance(e, RuntimeError) and "pandoc exited with code" in str(e):
                 message += "Pandoc reported an error during conversion.\n\n"
                 title = "Pandoc Conversion Error"
            message += f"Details ({error_type}): {e}"
            self.conversion_error.emit(f"{title}: {message}", context)


class AsciiDocEditor(QMainWindow):
    request_git_command = Signal(list, str)
    request_pandoc_conversion = Signal(object, str, str, str)

    def __init__(self, original_palette: Optional[QPalette] = None) -> None:
        super().__init__()
        self._settings_path: Path = self._get_settings_path()
        self._original_palette: Optional[QPalette] = original_palette
        self._set_default_settings()
        self._load_settings()
        self.setWindowTitle(f"{APP_NAME} · Basic Preview")
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._apply_loaded_theme_setting()
        self._setup_workers_and_threads()
        self._update_ui_state()
        if not self._git_repo_path:
             self.statusBar.showMessage("Ready. Set Git repository via Git menu.")
        elif "Git repository set" not in self.statusBar.currentMessage():
             self.statusBar.showMessage(f"Git repository: {self._git_repo_path}", 5000)

    def _set_default_settings(self) -> None:
        self._last_directory: str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation) or str(Path.home())
        self._current_file_path: Optional[Path] = None
        self._git_repo_path: Optional[str] = None
        self._dark_mode_enabled: bool = True
        self._initial_geometry: Optional[QRect] = None
        self._start_maximized: bool = True
        self._asciidoc_api: Optional[AsciiDoc3API] = self._initialize_asciidoc()
        self._preview_timer: QTimer = self._setup_preview_timer()
        self._is_opening_file: bool = False
        self._is_processing_git: bool = False
        self._is_processing_pandoc: bool = False
        self._last_git_operation: str = ""
        self._pending_file_path: Optional[Path] = None
        self._pending_commit_message: Optional[str] = None

    def _get_settings_path(self) -> Path:
        # Use platform-appropriate configuration directory
        config_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)

        if not config_dir_str:
            # Fallback to home directory if config location not available
            print("WARN: Could not determine config directory, using home directory for settings.")
            return Path.home() / SETTINGS_FILENAME

        config_dir = Path(config_dir_str)

        # Create config directory if it doesn't exist
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            print(f"INFO: Using config directory: {config_dir}")
        except Exception as e:
            print(f"WARN: Could not create config directory {config_dir}: {e}. Using home directory.")
            return Path.home() / SETTINGS_FILENAME

        return config_dir / SETTINGS_FILENAME

    def _load_settings(self) -> None:
        print(f"INFO: Attempting to load settings from: {self._settings_path}")
        if not self._settings_path.is_file():
            print("INFO: Settings file not found, using defaults.")
            self._start_maximized = True
            return

        try:
            with open(self._settings_path, 'r', encoding='utf-8') as f:
                settings: Dict[str, Any] = json.load(f)

            loaded_last_dir = settings.get("last_directory")
            if isinstance(loaded_last_dir, str) and Path(loaded_last_dir).is_dir():
                self._last_directory = loaded_last_dir
            else:
                print(f"WARN: Invalid 'last_directory' in settings, using default: {self._last_directory}")

            loaded_git_repo = settings.get("git_repo_path")
            if isinstance(loaded_git_repo, str) and loaded_git_repo:
                 self._git_repo_path = loaded_git_repo

            loaded_dark_mode = settings.get("dark_mode")
            if isinstance(loaded_dark_mode, bool):
                self._dark_mode_enabled = loaded_dark_mode

            self._start_maximized = settings.get("maximized", True)
            geom_dict = settings.get("window_geometry")
            loaded_geom: Optional[QRect] = None

            if isinstance(geom_dict, dict) and not self._start_maximized:
                try:
                    x = int(geom_dict.get("x", -1))
                    y = int(geom_dict.get("y", -1))
                    w = int(geom_dict.get("width", -1))
                    h = int(geom_dict.get("height", -1))
                    if all(v >= 0 for v in [x, y, w, h]):
                        loaded_geom = QRect(x, y, w, h)
                    else:
                        print("WARN: Invalid geometry values in settings.")
                except (ValueError, TypeError):
                    print("WARN: Error parsing geometry from settings.")

            if loaded_geom:
                self._initial_geometry = loaded_geom
                self._start_maximized = False
                print(f"INFO: Loaded window geometry: {self._initial_geometry}")
            else:
                 self._initial_geometry = None
                 self._start_maximized = True
                 if geom_dict is not None:
                     print("WARN: Using default/maximized state due to invalid geometry.")

            print("INFO: Settings loaded successfully.")

        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse settings file {self._settings_path}: {e}", file=sys.stderr)
            error_message = f"Could not parse settings file '{self._settings_path}'.\nUsing default settings.\n\nError: {e}"
            self._set_default_settings()
            if hasattr(self, 'statusBar'):
                 self._show_message("warning", "Settings Load Error", error_message)
            else:
                 QMessageBox.warning(None, f"{APP_NAME} - Settings Load Error", error_message)
        except IOError as e:
            print(f"ERROR: Failed to read settings file {self._settings_path}: {e}", file=sys.stderr)
            error_message = f"Could not read settings file '{self._settings_path}'.\nUsing default settings.\n\nError: {e}"
            self._set_default_settings()
            if hasattr(self, 'statusBar'):
                self._show_message("warning", "Settings Load Error", error_message)
            else:
                QMessageBox.warning(None, f"{APP_NAME} - Settings Load Error", error_message)
        except Exception as e:
            print(f"ERROR: Unexpected error loading settings from {self._settings_path}: {e}", file=sys.stderr)
            error_message = f"Unexpected error loading settings.\nUsing default settings.\n\nError: {e}"
            self._set_default_settings()
            if hasattr(self, 'statusBar'):
                self._show_message("warning", "Settings Load Error", error_message)
            else:
                QMessageBox.warning(None, f"{APP_NAME} - Settings Load Error", error_message)

    def _apply_loaded_theme_setting(self) -> None:
        self.dark_mode_act.setChecked(self._dark_mode_enabled)
        app = QApplication.instance()
        if not app: return

        if self._dark_mode_enabled:
            _apply_dark_palette(app)
        else:
            if self._original_palette:
                 app.setPalette(self._original_palette)
            else:
                 print("WARN: Original palette instance variable not found. Cannot restore light theme.", file=sys.stderr)

    def _save_settings(self) -> None:
        is_maximized = self.isMaximized()
        geometry_dict = None
        if not is_maximized:
            geom: QRect = self.geometry()
            geometry_dict = {"x": geom.x(), "y": geom.y(), "width": geom.width(), "height": geom.height()}

        settings: Dict[str, Any] = {
            "last_directory": str(self._last_directory),
            "git_repo_path": self._git_repo_path,
            "dark_mode": self.dark_mode_act.isChecked(),
            "maximized": is_maximized,
            "window_geometry": geometry_dict
        }

        print(f"INFO: Saving settings to: {self._settings_path}")
        try:
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            print("INFO: Settings saved successfully.")
        except (IOError, TypeError, Exception) as e:
            print(f"ERROR: Failed to save settings to {self._settings_path}: {e}", file=sys.stderr)
            self._show_message("warning", "Settings Save Error", f"Could not save settings: {e}")

    def _initialize_asciidoc(self) -> Optional[AsciiDoc3API]:
        if ASCIIDOC3_AVAILABLE and AsciiDoc3API and asciidoc3:
            try:
                instance = AsciiDoc3API(asciidoc3.__file__)
                instance.options("--no-header-footer")
                print("INFO: AsciiDoc3API initialized.")
                return instance
            except Exception as exc:
                print(f"ERROR: AsciiDoc3API initialization failed: {exc}", file=sys.stderr)
        return None

    def _setup_preview_timer(self) -> QTimer:
        timer = QTimer(self)
        timer.setInterval(PREVIEW_UPDATE_INTERVAL_MS)
        timer.setSingleShot(True)
        timer.timeout.connect(self.update_preview)
        return timer

    def _setup_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(splitter)

        self.editor = QPlainTextEdit(self)
        mono_font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        self.editor.setFont(mono_font)

        # Note: setCursorWidth() does not work in WSL/X11 environments
        # Cursor appearance is controlled by the X server/system settings

        self.editor.textChanged.connect(self._start_preview_timer)
        splitter.addWidget(self.editor)

        self.preview = QTextBrowser(self)
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(True)
        splitter.addWidget(self.preview)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def _create_actions(self) -> None:
        self.open_act = QAction("Open…", self, shortcut=QKeySequence.StandardKey.Open, toolTip="Open AsciiDoc (*.adoc, *.asciidoc) or Convert Word (*.docx)", triggered=self.open_file)
        self.save_act = QAction("Save", self, shortcut=QKeySequence.StandardKey.Save, toolTip="Save the current document", triggered=self.save_file)
        self.save_as_act = QAction("Save As…", self, shortcut=QKeySequence.StandardKey.SaveAs, toolTip="Save the current document to a new AsciiDoc file", triggered=lambda: self.save_file(save_as=True))
        self.exit_act = QAction("Exit", self, shortcut=QKeySequence.StandardKey.Quit, toolTip="Exit the application", triggered=self.close)

        self.convert_paste_act = QAction("Convert Clipboard (Word) & Paste", self, toolTip="Convert HTML/Text from clipboard to AsciiDoc and paste", triggered=self.convert_and_paste_from_clipboard)

        self.zoom_in_act = QAction("Zoom In", self, shortcut=QKeySequence.StandardKey.ZoomIn, toolTip="Increase text size", triggered=lambda: self._zoom(1))
        self.zoom_out_act = QAction("Zoom Out", self, shortcut=QKeySequence.StandardKey.ZoomOut, toolTip="Decrease text size", triggered=lambda: self._zoom(-1))
        self.dark_mode_act = QAction("Toggle Dark Mode", self, toolTip="Switch UI theme", checkable=True, triggered=self._toggle_dark_mode)

        self.set_repo_act = QAction("Set Repository…", self, toolTip="Select local Git repository directory", triggered=self._select_git_repository)
        self.git_commit_act = QAction("&Commit…", self, shortcut="Ctrl+Shift+C", toolTip="Stage all changes and commit with message", triggered=self._trigger_git_commit)
        self.git_pull_act = QAction("&Pull", self, shortcut="Ctrl+Shift+P", toolTip="Pull changes from remote (git pull)", triggered=self._trigger_git_pull)
        self.git_push_act = QAction("P&ush", self, shortcut="Ctrl+Shift+U", toolTip="Push committed changes to remote (git push)", triggered=self._trigger_git_push)

    def _create_menus(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.save_as_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.convert_paste_act)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.zoom_in_act)
        view_menu.addAction(self.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.dark_mode_act)

        git_menu = menu_bar.addMenu("&Git")
        git_menu.addAction(self.set_repo_act)
        git_menu.addSeparator()
        git_menu.addAction(self.git_commit_act)
        git_menu.addAction(self.git_pull_act)
        git_menu.addAction(self.git_push_act)

    def _setup_workers_and_threads(self) -> None:
        print("INFO: Setting up Git and Pandoc worker threads...")

        self.git_thread = QThread(self)
        self.git_thread.setObjectName("GitThread")
        self.git_worker = GitWorker()
        self.git_worker.moveToThread(self.git_thread)
        self.request_git_command.connect(self.git_worker.run_git_command)
        self.git_worker.command_complete.connect(self._handle_git_result)
        self.git_thread.finished.connect(self.git_worker.deleteLater)
        self.git_thread.start()

        self.pandoc_thread = QThread(self)
        self.pandoc_thread.setObjectName("PandocThread")
        self.pandoc_worker = PandocWorker()
        self.pandoc_worker.moveToThread(self.pandoc_thread)
        self.request_pandoc_conversion.connect(self.pandoc_worker.run_pandoc_conversion)
        self.pandoc_worker.conversion_complete.connect(self._handle_pandoc_result)
        self.pandoc_worker.conversion_error.connect(self._handle_pandoc_error_result)
        self.pandoc_thread.finished.connect(self.pandoc_worker.deleteLater)
        self.pandoc_thread.start()

        print("INFO: Git and Pandoc worker threads started.")

    def _start_preview_timer(self) -> None:
        if self._is_opening_file: return
        if self._current_file_path and not self.windowTitle().endswith("*"):
            self.setWindowTitle(f"{self.windowTitle()}*")
        self._preview_timer.start()

    @Slot(GitResult)
    def _handle_git_result(self, result: GitResult) -> None:
        current_operation = self._last_git_operation
        print(f"INFO: Handling Git result for operation: {current_operation}")

        if current_operation == "pull":
            self._is_processing_git = False
            self._update_ui_state()
            if result.success:
                self._show_message("info", "Git Pull Successful", f"Pulled changes from remote.\n\nOutput:\n{result.stdout}")
                self.statusBar.showMessage("Git pull successful.", 5000)
                self._reload_current_file_if_in_repo()
            else:
                self._show_message("critical", "Git Pull Failed", result.user_message)
                self.statusBar.showMessage("Git pull failed.", 5000)
            self._last_git_operation = ""
            return

        if current_operation == "commit_add":
            if not result.success:
                self._is_processing_git = False; self._last_git_operation = ""; self._pending_commit_message = None; self._update_ui_state()
                self._show_message("critical", "Git Add Failed (Commit)", result.user_message); self.statusBar.showMessage("Git add failed.", 5000); return

            if self._pending_commit_message:
                self._last_git_operation = "commit_commit"
                self.statusBar.showMessage("Attempting Git commit...", 0)
                QApplication.processEvents()
                self.request_git_command.emit(["git", "commit", "-m", self._pending_commit_message], self._git_repo_path) # type: ignore
            else:
                print("ERROR: Commit sequence reached commit step without a message.", file=sys.stderr)
                self._is_processing_git = False; self._last_git_operation = ""; self._pending_commit_message = None; self._update_ui_state()
                self.statusBar.showMessage("Commit failed: internal error.", 5000)

        elif current_operation == "commit_commit":
            self._is_processing_git = False
            self._last_git_operation = ""
            self._pending_commit_message = None
            self._update_ui_state()
            if result.success or "nothing to commit" in result.stderr.lower():
                 if "nothing to commit" in result.stderr.lower():
                     self._show_message("info", "Nothing to Commit", "No changes were staged to commit.")
                     self.statusBar.showMessage("Nothing to commit.", 5000)
                 else:
                     self._show_message("info", "Commit Successful", f"Changes committed locally.\n\nOutput:\n{result.stdout}")
                     self.statusBar.showMessage("Commit successful.", 5000)
            else:
                 self._show_message("critical", "Git Commit Failed", result.user_message)
                 self.statusBar.showMessage("Commit failed.", 5000)
            return

        if current_operation == "push_direct":
            self._is_processing_git = False
            self._last_git_operation = ""
            self._update_ui_state()
            if result.success:
                self._show_message("info", "Git Push Successful", f"Pushed changes to remote.\n\nOutput:\n{result.stdout}")
                self.statusBar.showMessage("Git push successful.", 5000)
            else:
                self._show_message("critical", "Git Push Failed", result.user_message)
                self.statusBar.showMessage("Git push failed.", 5000)
            return

        if self._is_processing_git:
             print(f"WARN: Unhandled Git result context: {current_operation}", file=sys.stderr)
             self._is_processing_git = False; self._last_git_operation = ""; self._update_ui_state()

    @Slot(str, str)
    def _handle_pandoc_result(self, result_text: str, context: str) -> None:
        self._is_processing_pandoc = False
        self._update_ui_state()

        if context == "clipboard conversion":
            self.editor.insertPlainText(result_text)
            print("INFO: Background clipboard content converted and pasted successfully.")
            if self._current_file_path and not self.windowTitle().endswith("*"):
                self.setWindowTitle(f"{self.windowTitle()}*")
            self.statusBar.showMessage("Pasted converted clipboard content.", 5000)
        elif context.startswith("converting "):
            file_name = context.split("'")[1] if "'" in context else "file"
            pending_path = self._pending_file_path
            if pending_path:
                self._load_content_into_editor(result_text, pending_path, "Converted DOCX")
                self._pending_file_path = None
            else:
                print(f"ERROR: Pandoc result received for {file_name}, but no pending file path found.", file=sys.stderr)
                self.statusBar.showMessage(f"Error loading converted {file_name}.", 5000)
        else:
            print(f"WARN: Unknown Pandoc context result: {context}", file=sys.stderr)
            self.statusBar.showMessage("Pandoc conversion finished.", 5000)

    @Slot(str, str)
    def _handle_pandoc_error_result(self, error_message: str, context: str) -> None:
        self._is_processing_pandoc = False
        self._update_ui_state()
        print(f"ERROR: Pandoc Worker reported error for '{context}': {error_message}", file=sys.stderr)
        self._show_message("critical", f"Pandoc Error ({context})", error_message)
        self.statusBar.showMessage(f"Pandoc {context} failed.", 5000)
        if context.startswith("converting ") and self._pending_file_path:
            self._pending_file_path = None

    @Slot()
    def update_preview(self) -> None:
        source_text = self.editor.toPlainText()
        html_body = self._convert_asciidoc_to_html_body(source_text)
        full_html = f"""<!doctype html><html><head><meta charset='utf-8'>{self._get_preview_css()}</head><body>{html_body}</body></html>"""
        self.preview.setHtml(full_html)

    def convert_and_paste_from_clipboard(self) -> None:
        if self._is_processing_pandoc:
            self._show_message("warning", "Busy", "Already processing a Pandoc conversion.")
            return
        if not self._check_pandoc_availability("Clipboard Conversion"):
            return

        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()
        source_text: Optional[Union[str, bytes]] = None
        source_format = "markdown"

        raw_text = mime_data.text()
        raw_html = mime_data.html()

        if mime_data.hasHtml():
            source_text = raw_html
            source_format = "html"
        elif mime_data.hasText():
            source_text = raw_text

        source_text_str = str(source_text) if source_text is not None else ""
        if not source_text or not source_text_str.strip():
            self._show_message("warning", "Clipboard Empty", "Clipboard contains no usable text or HTML.")
            return

        self._is_processing_pandoc = True
        self._update_ui_state()
        self.statusBar.showMessage("Converting clipboard content...", 0)
        self.request_pandoc_conversion.emit(source_text, 'asciidoc', source_format, "clipboard conversion")

    def open_file(self) -> None:
        if self._is_processing_pandoc:
            self._show_message("warning", "Busy", "Already processing a file conversion.")
            return
        if self._has_unsaved_changes():
            if not self._prompt_save_before_action("open a new file"): return

        path_str, _ = QFileDialog.getOpenFileName(
            self, "Open File", self._last_directory, SUPPORTED_OPEN_FILTER
        )
        if not path_str: return

        file_path = Path(path_str)
        try:
            if file_path.suffix.lower() == '.docx':
                if not self._check_pandoc_availability(f"Opening '{file_path.name}'"): return
                self._is_processing_pandoc = True
                self._pending_file_path = file_path
                self._update_ui_state()
                self.statusBar.showMessage(f"Converting '{file_path.name}'...", 0)
                docx_bytes = file_path.read_bytes()
                self.request_pandoc_conversion.emit(docx_bytes, 'asciidoc', 'docx', f"converting '{file_path.name}'")
            elif file_path.suffix.lower() in ['.adoc', '.asciidoc']:
                content, opened_as = self._read_adoc_content(file_path)
                self._load_content_into_editor(content, file_path, opened_as)
            else:
                self._show_message("warning", "Unsupported File Type", f"Cannot open file type: {file_path.suffix}")
        except Exception as exc:
            self._handle_file_operation_error(exc, file_path, "opening")
            if self._is_processing_pandoc:
                self._is_processing_pandoc = False; self._pending_file_path = None; self._update_ui_state()

    def _trigger_git_commit(self) -> None:
        if self._is_processing_git:
            self._show_message("warning", "Busy", "Already running a Git operation.")
            return
        if not self._ensure_git_repo_set(): return

        if self._current_file_path and self._has_unsaved_changes():
             print(f"INFO: Saving current file before Git commit: {self._current_file_path}")
             if not self.save_file(save_as=False):
                 self.statusBar.showMessage("Save failed or cancelled. Commit aborted.", 5000)
                 return

        commit_message, ok = QInputDialog.getMultiLineText(
            self, "Commit Changes", "Enter commit message:", ""
        )
        if not ok:
            self.statusBar.showMessage("Commit cancelled.", 3000)
            return
        if not commit_message.strip():
            self._show_message("warning", "Empty Commit Message", "Commit aborted. Please provide a commit message.")
            return

        # Validate commit message (remove null bytes and control characters except newlines/tabs)
        sanitized_message = commit_message.replace('\0', '').replace('\r', '')
        if not sanitized_message.strip():
            self._show_message("warning", "Invalid Commit Message", "Commit message contains only invalid characters.")
            return

        self._is_processing_git = True
        self._last_git_operation = "commit_add"
        self._pending_commit_message = sanitized_message
        self._update_ui_state()
        self.statusBar.showMessage("Attempting Git add...", 0)
        QApplication.processEvents()
        self.request_git_command.emit(["git", "add", "."], self._git_repo_path) # type: ignore

    def _trigger_git_pull(self) -> None:
        if self._is_processing_git:
            self._show_message("warning", "Busy", "Already running a Git operation.")
            return
        if not self._ensure_git_repo_set(): return
        if self._has_unsaved_changes():
            if not self._prompt_save_before_action("pull changes (local changes might be overwritten)"): return

        self._is_processing_git = True; self._last_git_operation = "pull"; self._update_ui_state()
        self.statusBar.showMessage("Attempting Git pull...", 0); QApplication.processEvents()
        self.request_git_command.emit(["git", "pull"], self._git_repo_path) # type: ignore

    def _trigger_git_push(self) -> None:
        if self._is_processing_git:
            self._show_message("warning", "Busy", "Already running a Git operation.")
            return
        if not self._ensure_git_repo_set(): return

        self._is_processing_git = True; self._last_git_operation = "push_direct"; self._update_ui_state()
        self.statusBar.showMessage("Attempting Git push...", 0); QApplication.processEvents()
        self.request_git_command.emit(["git", "push"], self._git_repo_path) # type: ignore

    def _convert_asciidoc_to_html_body(self, source_text: str) -> str:
        if self._asciidoc_api is None:
            print("WARN: AsciiDoc3 not available, previewing as plain text.")
            return f"<pre>{html.escape(source_text)}</pre>"
        try:
            infile = io.StringIO(source_text)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()
        except Exception as exc:
            print(f"ERROR: AsciiDoc3 rendering failed: {exc}", file=sys.stderr)
            error_style = "color:#FF6B6B; background:#401A1A; border: 1px solid #F07474; padding: 10px; font-family: sans-serif;"
            return (f"<div style='{error_style}'><strong>AsciiDoc Render Error:</strong><br>"
                    f"<pre style='white-space: pre-wrap; color: #FFCDCD;'>{html.escape(str(exc))}</pre></div>")

    def _read_adoc_content(self, file_path: Path) -> Tuple[str, str]:
        print(f"INFO: Reading AsciiDoc file: {file_path}")
        try:
            content = file_path.read_text(encoding="utf-8")
            return content, "AsciiDoc"
        except Exception as e:
            raise IOError(f"Failed to read AsciiDoc file: {file_path.name}") from e

    def _load_content_into_editor(self, content: str, file_path: Path, opened_as: str) -> None:
        self._is_opening_file = True
        try:
            self.editor.setPlainText(content)
            self._current_file_path = file_path
            self._last_directory = str(file_path.parent)
            self.setWindowTitle(f"{APP_NAME} · {file_path.name} ({opened_as})")
            self.statusBar.showMessage(f"Opened: {file_path}", 5000)
            print(f"INFO: Loaded '{file_path.name}'. Last directory: {self._last_directory}")
            self.update_preview()
        finally:
            self._is_opening_file = False

    def save_file(self, save_as: bool = False) -> bool:
        path_to_save = self._get_save_path(force_dialog=save_as)
        if not path_to_save:
            self.statusBar.showMessage("Save cancelled.", 3000)
            return False

        try:
            current_text = self.editor.toPlainText()
            path_to_save.write_text(current_text, encoding='utf-8')

            self._current_file_path = path_to_save
            self._last_directory = str(path_to_save.parent)
            self.setWindowTitle(f"{APP_NAME} · {path_to_save.name}")
            self.statusBar.showMessage(f"Saved: {path_to_save}", 5000)
            print(f"INFO: Document saved successfully to: {path_to_save}")
            return True
        except Exception as exc:
            self._handle_file_operation_error(exc, path_to_save, "saving")
            return False

    def _get_save_path(self, force_dialog: bool) -> Optional[Path]:
        if not force_dialog and self._current_file_path:
            return self._current_file_path

        suggested_name = DEFAULT_FILENAME
        if self._current_file_path:
            suggested_name = self._current_file_path.name
        elif " · " in self.windowTitle():
            parts = self.windowTitle().rsplit(" · ", 1)
            if len(parts) > 1:
                title_part = parts[1].split(" (")[0]
                if title_part and title_part != "Basic Preview":
                    suggested_name = title_part

        suggested_path = Path(self._last_directory) / suggested_name

        path_str, _ = QFileDialog.getSaveFileName(
            self, "Save As AsciiDoc", str(suggested_path), SUPPORTED_SAVE_FILTER
        )
        if not path_str: return None

        path = Path(path_str)
        if path.suffix.lower() not in ['.adoc', '.asciidoc']:
            print(f"INFO: Adding default '.adoc' extension to '{path.name}'")
            path = path.with_suffix('.adoc')
        return path

    def _zoom(self, delta: int) -> None:
        editor_font = self.editor.font()
        new_size = max(editor_font.pointSize() + delta, MIN_FONT_SIZE)
        if new_size != editor_font.pointSize():
            editor_font.setPointSize(new_size); self.editor.setFont(editor_font)
        self.preview.zoomIn(delta * ZOOM_STEP)

    def _toggle_dark_mode(self) -> None:
        app = QApplication.instance()
        if not app: return
        self._dark_mode_enabled = self.dark_mode_act.isChecked()
        if self._dark_mode_enabled:
            _apply_dark_palette(app); print("INFO: Switched to Dark Mode.")
        else:
            if self._original_palette:
                app.setPalette(self._original_palette); print("INFO: Switched to Light Mode.")
            else:
                print("WARN: Original palette instance variable not found.", file=sys.stderr)
        self.update_preview()

    def _get_preview_css(self) -> str:
        return _StyleConstants.DARK_MODE_CSS if self.dark_mode_act.isChecked() else _StyleConstants.LIGHT_MODE_CSS

    def _check_pandoc_availability(self, context: str) -> bool:
        if not PANDOC_AVAILABLE:
            self._show_message("critical", "Dependency Missing: Pandoc", f"{context} requires 'pypandoc' and a system Pandoc installation.")
            return False
        return True

    def _handle_file_operation_error(self, error: Exception, file_path: Optional[Path], operation: str):
        path_str = str(file_path) if file_path else "[Unknown Path]"
        print(f"ERROR: Failed {operation} file {path_str}: {error}", file=sys.stderr)
        if operation == "opening":
            self._current_file_path = None
            self.setWindowTitle(f"{APP_NAME} · Basic Preview")
        self._show_message("critical", f"File {operation.capitalize()} Error", f"Could not {operation} the file:\n{path_str}\n\nError: {error}")

    def _show_message(self, level: str, title: str, text: str) -> None:
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{APP_NAME} - {title}")
        msg_box.setText(text)
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "critical": QMessageBox.Icon.Critical,
            "question": QMessageBox.Icon.Question,
        }
        msg_box.setIcon(icon_map.get(level, QMessageBox.Icon.NoIcon))
        msg_box.exec()

    def _select_git_repository(self) -> None:
        start_dir = self._git_repo_path or self._last_directory
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Git Repository Directory", start_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if not dir_path: return

        git_meta_dir = Path(dir_path) / ".git"
        if git_meta_dir.is_dir():
            self._git_repo_path = dir_path
            self.statusBar.showMessage(f"Git repository set: {self._git_repo_path}", 5000)
            print(f"INFO: Git repository path set to: {self._git_repo_path}")
        else:
            self._show_message("warning", "Not a Git Repository", f"Selected directory does not appear to be a Git repository (missing .git folder):\n{dir_path}")
        self._update_ui_state()

    def _update_ui_state(self) -> None:
        repo_set = bool(self._git_repo_path)
        git_enabled = repo_set and not self._is_processing_git
        self.git_commit_act.setEnabled(git_enabled)
        self.git_pull_act.setEnabled(git_enabled)
        self.git_push_act.setEnabled(git_enabled)
        self.set_repo_act.setEnabled(not self._is_processing_git)

        conversion_enabled = not self._is_processing_pandoc
        self.open_act.setEnabled(conversion_enabled)
        self.convert_paste_act.setEnabled(conversion_enabled and PANDOC_AVAILABLE)

        if not repo_set and not self._is_processing_git and not self._is_processing_pandoc:
            if "Git repository set" not in self.statusBar.currentMessage():
                 self.statusBar.showMessage("Ready. Set Git repository via Git menu.")

    def _ensure_git_repo_set(self) -> bool:
        if not self._git_repo_path:
            self._show_message("warning", "Git Repository Not Set", "Please set the Git repository path first using the Git menu.")
            return False
        return True

    def _has_unsaved_changes(self) -> bool:
        return self.windowTitle().endswith("*")

    def _prompt_save_before_action(self, action_description: str) -> bool:
        if not self._has_unsaved_changes():
            return True

        message = f"You have unsaved changes.\n\nDo you want to save them before {action_description}?"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{APP_NAME} - Unsaved Changes")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        save_button = msg_box.addButton("Save", QMessageBox.ButtonRole.AcceptRole)
        discard_button = msg_box.addButton("Discard", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.setDefaultButton(save_button)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        if clicked_button == save_button:
            return self.save_file(save_as=False)
        elif clicked_button == discard_button:
            print("INFO: User discarded unsaved changes.")
            return True
        else:
            print("INFO: User cancelled the action.")
            return False

    def _reload_current_file_if_in_repo(self) -> None:
        if not self._current_file_path or not self._git_repo_path or not self._current_file_path.exists():
            return
        try:
            self._current_file_path.relative_to(self._git_repo_path)
            print(f"INFO: Reloading current file after pull: {self._current_file_path}")
            content, opened_as = self._read_adoc_content(self._current_file_path)
            self._load_content_into_editor(content, self._current_file_path, opened_as)
        except ValueError:
             pass
        except Exception as e:
             self._handle_file_operation_error(e, self._current_file_path, "reloading after pull")

    def closeEvent(self, event) -> None:
        self._save_settings()
        if self._prompt_save_before_action("closing the application"):
            print("INFO: Quitting worker threads...")
            self.git_thread.quit()
            self.pandoc_thread.quit()
            if not self.git_thread.wait(500): print("WARN: Git thread did not finish quitting gracefully.")
            if not self.pandoc_thread.wait(500): print("WARN: Pandoc thread did not finish quitting gracefully.")
            print("INFO: Threads cleanup finished.")
            event.accept()
        else:
            event.ignore()

class _StyleConstants:
    DARK_MODE_CSS: str = r"""
<style>
 body { background:#1e1e1e; color:#dcdcdc; margin:0; padding:10px 20px; font-family: sans-serif; line-height: 1.6; }
 h1,h2,h3,h4,h5,h6 { color:#ececec; border-bottom: 1px solid #4a4a4a; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 1em; font-weight: 600; }
 h1 { font-size: 2.1em; } h2 { font-size: 1.8em; } h3 { font-size: 1.5em; }
 a { color:#80d0ff; text-decoration: none; } a:hover { text-decoration: underline; color: #a0e0ff; }
 code,pre { background:#2a2a2a; color:#f0f0f0; font-family: Consolas, "Courier New", monospace; font-size: 0.95em; border-radius: 4px; border: 1px solid #444; }
 code { padding: 0.2em 0.4em; border: none; }
 pre { padding: 0.9em; margin: 1em 0; overflow-x: auto; white-space: pre-wrap; }
 table { border-collapse: collapse; margin: 1.2em 0; width: auto; border: 1px solid #555; }
 thead { background:#3a3a3a; border-bottom: 2px solid #777; } thead th { color:#ffffff; text-align: left; font-weight: bold; }
 tbody td, thead th { border: 1px solid #555; padding: 8px 12px; }
 tbody tr:nth-child(odd) { background-color: #262626; }
 div.admonition { border-left: 5px solid #ffb74d; background: #333; padding: 1em 1.5em; margin: 1.5em 0; border-radius: 4px; }
 div.admonition .title { font-weight: bold; color: #ffb74d; display: block; margin-bottom: 0.6em; text-transform: uppercase; font-size: 0.9em; letter-spacing: 0.5px; }
 blockquote { border-left: 5px solid #777; color: #ccc; padding: 0.5em 1.5em; margin: 1.5em 0; background-color: #2a2a2a; }
 ul, ol { margin: 1em 0; padding-left: 2.5em; } li { margin-bottom: 0.6em; }
 hr { border: 0; border-top: 1px solid #555; margin: 2em 0; height:1px; }
 img { max-width: 100%; height: auto; border-radius: 4px; }
</style>
"""
    LIGHT_MODE_CSS: str = r"""
<style>
 body { background:#ffffff; color:#333333; margin:0; padding:10px 20px; font-family: sans-serif; line-height: 1.6; }
 h1,h2,h3,h4,h5,h6 { color:#111111; border-bottom: 1px solid #cccccc; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 1em; font-weight: 600; }
 h1 { font-size: 2.1em; } h2 { font-size: 1.8em; } h3 { font-size: 1.5em; }
 a { color:#007bff; text-decoration: none; } a:hover { text-decoration: underline; color: #0056b3; }
 code,pre { background:#f4f4f4; color:#333; font-family: Consolas, "Courier New", monospace; font-size: 0.95em; border-radius: 4px; border: 1px solid #ddd; }
 code { padding: 0.2em 0.4em; border: none; }
 pre { padding: 0.9em; margin: 1em 0; overflow-x: auto; white-space: pre-wrap; }
 table { border-collapse: collapse; margin: 1.2em 0; width: auto; border: 1px solid #ccc; }
 thead { background:#e9ecef; border-bottom: 2px solid #aaa; } thead th { color:#333; text-align: left; font-weight: bold; }
 tbody td, thead th { border: 1px solid #ccc; padding: 8px 12px; }
 tbody tr:nth-child(odd) { background-color: #f8f9fa; }
 div.admonition { border-left: 5px solid #ffc107; background: #fff3cd; padding: 1em 1.5em; margin: 1.5em 0; border-radius: 4px; color: #664d03; border: 1px solid #ffecb5; }
 div.admonition .title { font-weight: bold; color: #664d03; display: block; margin-bottom: 0.6em; text-transform: uppercase; font-size: 0.9em; letter-spacing: 0.5px; }
 blockquote { border-left: 5px solid #ccc; color: #555; padding: 0.5em 1.5em; margin: 1.5em 0; background-color: #f8f9fa; }
 ul, ol { margin: 1em 0; padding-left: 2.5em; } li { margin-bottom: 0.6em; }
 hr { border: 0; border-top: 1px solid #ccc; margin: 2em 0; height:1px; }
 img { max-width: 100%; height: auto; border-radius: 4px; }
</style>
"""

def _apply_dark_palette(app: QApplication) -> None:
    dark_palette = QPalette()
    dark_grey = QColor(53, 53, 53)
    light_grey = QColor(83, 83, 83)
    darker_grey = QColor(35, 35, 35)
    text_color = QColor(220, 220, 220)
    highlight_color = QColor(42, 130, 218)
    disabled_text = QColor(128, 128, 128)
    disabled_button = QColor(60, 60, 60)

    dark_palette.setColor(QPalette.ColorRole.Window, dark_grey)
    dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
    dark_palette.setColor(QPalette.ColorRole.Base, darker_grey)
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, dark_grey)
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Qt.GlobalColor.black))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Qt.GlobalColor.white))
    dark_palette.setColor(QPalette.ColorRole.Text, text_color)
    dark_palette.setColor(QPalette.ColorRole.Button, light_grey)
    dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(Qt.GlobalColor.red))
    dark_palette.setColor(QPalette.ColorRole.Link, highlight_color.lighter(30))
    dark_palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Qt.GlobalColor.black))

    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_text)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, disabled_button)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, darker_grey)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, disabled_button)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, disabled_text)

    app.setPalette(dark_palette)

def main() -> None:
    # Note: HiDPI scaling attributes are deprecated in Qt6/PySide6
    # HiDPI is now handled automatically by Qt6

    # Suppress SyntaxWarnings from asciidoc3 library (invalid escape sequences in regex)
    warnings.filterwarnings('ignore', category=SyntaxWarning)

    app = QApplication(sys.argv)
    original_palette = app.palette()
    app.setStyle("Fusion")
    main_window = AsciiDocEditor(original_palette=original_palette)

    if main_window._start_maximized or not main_window._initial_geometry:
        print("INFO: Showing window maximized.")
        main_window.showMaximized()
    else:
        screen = QGuiApplication.primaryScreen()
        if screen:
            available_geom = screen.availableGeometry()
            if available_geom.intersects(main_window._initial_geometry):
                 print(f"INFO: Restoring window geometry: {main_window._initial_geometry}")
                 main_window.setGeometry(main_window._initial_geometry)
                 main_window.show()
            else:
                 print(f"WARN: Saved geometry {main_window._initial_geometry} is off-screen, showing maximized.")
                 main_window.showMaximized()
        else:
             print("WARN: Could not get screen geometry, showing maximized.")
             main_window.showMaximized()

    main_window.update_preview()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()