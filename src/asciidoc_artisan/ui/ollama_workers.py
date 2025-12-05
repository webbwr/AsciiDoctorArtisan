"""
Ollama Worker Threads - Download and delete workers for model management.

MA principle: Extracted from ollama_model_browser.py to keep files under 400 lines.
"""

import logging
import subprocess

from PySide6.QtCore import QThread, Signal

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
            process = subprocess.Popen(
                ["ollama", "pull", self.model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if process.stdout:
                for line in process.stdout:
                    if self._cancelled:
                        process.terminate()
                        self.finished.emit(False, "Download cancelled")
                        return
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


class ModelDeleteWorker(QThread):
    """Worker thread for deleting Ollama models."""

    finished = Signal(bool, str)  # Success, message

    def __init__(self, model_name: str) -> None:
        super().__init__()
        self.model_name = model_name

    def run(self) -> None:
        """Delete the model using ollama rm."""
        try:
            result = subprocess.run(
                ["ollama", "rm", self.model_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                self.finished.emit(True, f"Deleted {self.model_name}")
            else:
                self.finished.emit(False, f"Failed to delete: {result.stderr.strip()}")
        except FileNotFoundError:
            self.finished.emit(False, "Ollama not installed")
        except Exception as e:
            self.finished.emit(False, f"Error: {e!s}")
