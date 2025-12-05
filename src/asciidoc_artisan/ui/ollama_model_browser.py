"""
Ollama Model Browser - Browse and download available models.

Allows users to browse the Ollama model library and download new models
directly from the application.

MA principle: ~400 lines after extracting model data to ollama_models_data.py.
"""

import logging
import subprocess

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.ui.ollama_models_data import AVAILABLE_MODELS

logger = logging.getLogger(__name__)


class ModelDownloadWorker(QThread):
    """Worker thread for downloading Ollama models."""

    progress = Signal(str)  # Progress message
    finished = Signal(bool, str)  # Success, message

    def __init__(self, model_name: str) -> None:
        super().__init__()
        self.model_name = model_name
        self._cancelled = False

    def run(self) -> None:
        """Download the model using ollama pull."""
        try:
            self.progress.emit(f"Starting download of {self.model_name}...")

            # Run ollama pull command
            process = subprocess.Popen(
                ["ollama", "pull", self.model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Read output line by line
            if process.stdout:
                for line in process.stdout:
                    if self._cancelled:
                        process.terminate()
                        self.finished.emit(False, "Download cancelled")
                        return
                    # Parse progress from ollama output
                    line = line.strip()
                    if line:
                        self.progress.emit(line)

            process.wait()

            if process.returncode == 0:
                self.finished.emit(True, f"Successfully downloaded {self.model_name}")
            else:
                self.finished.emit(False, f"Failed to download {self.model_name}")

        except FileNotFoundError:
            self.finished.emit(False, "Ollama not installed. Please install from https://ollama.ai")
        except Exception as e:
            self.finished.emit(False, f"Error: {e!s}")

    def cancel(self) -> None:
        """Cancel the download."""
        self._cancelled = True


class OllamaModelBrowser(QDialog):
    """
    Dialog for browsing and downloading Ollama models.

    Shows available models from the Ollama library and allows
    downloading them directly from the application.
    """

    model_downloaded = Signal(str)  # Emitted when a model is downloaded

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.installed_models: set[str] = set()
        self.download_worker: ModelDownloadWorker | None = None
        self._init_ui()
        self._load_installed_models()
        self._populate_model_list()

    def _init_ui(self) -> None:
        """Initialize the UI."""
        self.setWindowTitle("Ollama Model Library")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter models by name or description...")
        self.search_input.textChanged.connect(self._filter_models)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Main content with splitter
        splitter = QSplitter()

        # Left side: Model list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Available Models:")
        left_layout.addWidget(list_label)

        self.model_list = QListWidget()
        self.model_list.currentItemChanged.connect(self._on_model_selected)
        left_layout.addWidget(self.model_list)

        splitter.addWidget(left_widget)

        # Right side: Model details and actions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Model details group
        details_group = QGroupBox("Model Details")
        details_layout = QVBoxLayout()

        self.model_name_label = QLabel("Select a model")
        self.model_name_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        details_layout.addWidget(self.model_name_label)

        self.model_size_label = QLabel("")
        details_layout.addWidget(self.model_size_label)

        self.model_category_label = QLabel("")
        details_layout.addWidget(self.model_category_label)

        self.model_desc_text = QTextEdit()
        self.model_desc_text.setReadOnly(True)
        self.model_desc_text.setMaximumHeight(100)
        details_layout.addWidget(self.model_desc_text)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        details_layout.addWidget(self.status_label)

        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)

        # Download controls
        download_group = QGroupBox("Download")
        download_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        download_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setWordWrap(True)
        download_layout.addWidget(self.progress_label)

        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download Model")
        self.download_btn.clicked.connect(self._download_model)
        self.download_btn.setEnabled(False)
        button_layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_download)
        self.cancel_btn.setVisible(False)
        button_layout.addWidget(self.cancel_btn)

        download_layout.addLayout(button_layout)
        download_group.setLayout(download_layout)
        right_layout.addWidget(download_group)

        # Custom model input
        custom_group = QGroupBox("Download Custom Model")
        custom_layout = QHBoxLayout()

        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("Enter model name (e.g., llama3.2:latest)")
        custom_layout.addWidget(self.custom_input)

        self.custom_download_btn = QPushButton("Pull")
        self.custom_download_btn.clicked.connect(self._download_custom_model)
        custom_layout.addWidget(self.custom_download_btn)

        custom_group.setLayout(custom_layout)
        right_layout.addWidget(custom_group)

        right_layout.addStretch()

        splitter.addWidget(right_widget)
        splitter.setSizes([350, 450])

        layout.addWidget(splitter)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

    def _load_installed_models(self) -> None:
        """Load list of currently installed models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Skip header line
                for line in lines[1:]:
                    parts = line.split()
                    if parts:
                        self.installed_models.add(parts[0])
                logger.info(f"Loaded {len(self.installed_models)} installed models")
        except Exception as e:
            logger.error(f"Error loading installed models: {e}")

    def _populate_model_list(self) -> None:
        """Populate the model list with available models."""
        self.model_list.clear()

        for model in AVAILABLE_MODELS:
            name = model["name"]
            size = model["size"]
            category = model["category"]

            # Create list item
            item = QListWidgetItem()
            is_installed = name in self.installed_models

            # Format display text
            status = "✓ Installed" if is_installed else ""
            display_text = f"{name} ({size}) [{category}] {status}"
            item.setText(display_text)
            item.setData(256, model)  # Store model data

            # Style installed models differently
            if is_installed:
                item.setBackground(self.palette().alternateBase())

            self.model_list.addItem(item)

    def _filter_models(self, text: str) -> None:
        """Filter model list based on search text."""
        text = text.lower()
        for i in range(self.model_list.count()):
            item = self.model_list.item(i)
            if item:
                model = item.data(256)
                if model:
                    visible = (
                        text in model["name"].lower()
                        or text in model["description"].lower()
                        or text in model["category"].lower()
                    )
                    item.setHidden(not visible)

    def _on_model_selected(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        """Handle model selection change."""
        if not current:
            self.download_btn.setEnabled(False)
            return

        model = current.data(256)
        if not model:
            return

        name = model["name"]
        is_installed = name in self.installed_models

        self.model_name_label.setText(name)
        self.model_size_label.setText(f"Size: {model['size']}")
        self.model_category_label.setText(f"Category: {model['category']}")
        self.model_desc_text.setText(model["description"])

        if is_installed:
            self.status_label.setText("✓ Already installed")
            self.status_label.setStyleSheet("color: green;")
            self.download_btn.setText("Re-download")
        else:
            self.status_label.setText("Not installed")
            self.status_label.setStyleSheet("color: gray;")
            self.download_btn.setText("Download Model")

        self.download_btn.setEnabled(True)

    def _download_model(self) -> None:
        """Download the selected model."""
        current = self.model_list.currentItem()
        if not current:
            return

        model = current.data(256)
        if not model:
            return

        self._start_download(model["name"])

    def _download_custom_model(self) -> None:
        """Download a custom model by name."""
        model_name = self.custom_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "No Model Name", "Please enter a model name to download.")
            return

        self._start_download(model_name)

    def _start_download(self, model_name: str) -> None:
        """Start downloading a model."""
        if self.download_worker and self.download_worker.isRunning():
            QMessageBox.warning(self, "Download in Progress", "Please wait for the current download to finish.")
            return

        # Update UI
        self.download_btn.setEnabled(False)
        self.custom_download_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_label.setText(f"Downloading {model_name}...")

        # Start download worker
        self.download_worker = ModelDownloadWorker(model_name)
        self.download_worker.progress.connect(self._on_download_progress)
        self.download_worker.finished.connect(self._on_download_finished)
        self.download_worker.start()

    def _on_download_progress(self, message: str) -> None:
        """Handle download progress updates."""
        self.progress_label.setText(message)

        # Try to parse percentage from message
        if "%" in message:
            try:
                # Extract percentage
                import re

                match = re.search(r"(\d+)%", message)
                if match:
                    percent = int(match.group(1))
                    self.progress_bar.setRange(0, 100)
                    self.progress_bar.setValue(percent)
            except Exception:
                pass

    def _on_download_finished(self, success: bool, message: str) -> None:
        """Handle download completion."""
        self.download_btn.setEnabled(True)
        self.custom_download_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)

        if success:
            self.progress_label.setText(f"✓ {message}")
            self.progress_label.setStyleSheet("color: green;")

            # Refresh installed models
            self._load_installed_models()
            self._populate_model_list()

            # Emit signal
            if self.download_worker:
                self.model_downloaded.emit(self.download_worker.model_name)
        else:
            self.progress_label.setText(f"✗ {message}")
            self.progress_label.setStyleSheet("color: red;")

        self.download_worker = None

    def _cancel_download(self) -> None:
        """Cancel the current download."""
        if self.download_worker:
            self.download_worker.cancel()
            self.progress_label.setText("Cancelling...")
