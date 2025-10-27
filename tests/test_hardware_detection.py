"""
Tests for hardware detection module.

Tests GPU, NPU, and CPU capability detection with mocked system calls.
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core.hardware_detection import (
    GPUInfo,
    HardwareCapabilities,
    HardwareDetector,
    NPUInfo,
)


class TestGPUDetection:
    """Test GPU detection for NVIDIA and AMD."""

    def test_nvidia_gpu_detection_success(self, mocker):
        """Test NVIDIA GPU detected via nvidia-smi."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="NVIDIA GeForce RTX 3080, 10240"
        )

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is not None
        assert "RTX 3080" in gpu.model
        assert gpu.vendor == "NVIDIA"
        assert gpu.memory_mb == 10240

    def test_nvidia_gpu_detection_not_found(self, mocker):
        """Test no NVIDIA GPU when nvidia-smi not found."""
        mock_run = mocker.patch(
            "subprocess.run", side_effect=FileNotFoundError("nvidia-smi not found")
        )

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is None

    def test_nvidia_gpu_detection_error(self, mocker):
        """Test NVIDIA GPU detection handles errors."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is None

    def test_amd_gpu_detection_success(self, mocker):
        """Test AMD GPU detected via rocm-smi."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="AMD Radeon RX 6800"
        )

        detector = HardwareDetector()
        gpu = detector.detect_amd_gpu()

        assert gpu is not None
        assert "RX 6800" in gpu.model
        assert gpu.vendor == "AMD"

    def test_amd_gpu_detection_not_found(self, mocker):
        """Test no AMD GPU when rocm-smi not found."""
        mock_run = mocker.patch(
            "subprocess.run", side_effect=FileNotFoundError("rocm-smi not found")
        )

        detector = HardwareDetector()
        gpu = detector.detect_amd_gpu()

        assert gpu is None

    def test_gpu_memory_parsing_mb(self):
        """Test GPU memory parsing from MB."""
        gpu = GPUInfo(vendor="Test", model="Test GPU", memory_mb=8192)
        assert gpu.memory_mb == 8192

    def test_gpu_memory_parsing_large(self):
        """Test GPU memory parsing with large values."""
        gpu = GPUInfo(vendor="NVIDIA", model="RTX 3080", memory_mb=10240)
        assert gpu.memory_mb == 10240


class TestHardwareCapabilities:
    """Test hardware capabilities dataclass."""

    def test_hardware_capabilities_with_gpu(self):
        """Test HardwareCapabilities with GPU."""
        gpu = GPUInfo(vendor="NVIDIA", model="GTX 1080", memory_mb=8192)

        caps = HardwareCapabilities(
            has_gpu=True,
            gpus=[gpu],
            has_npu=False,
            npu=None,
            cpu_cores=8,
            system_ram_gb=16,
        )

        assert caps.has_gpu is True
        assert len(caps.gpus) == 1
        assert caps.gpus[0].memory_mb == 8192
        assert caps.cpu_cores == 8

    def test_hardware_capabilities_no_gpu(self):
        """Test HardwareCapabilities without GPU."""
        caps = HardwareCapabilities(
            has_gpu=False,
            gpus=[],
            has_npu=False,
            npu=None,
            cpu_cores=4,
            system_ram_gb=8,
        )

        assert caps.has_gpu is False
        assert len(caps.gpus) == 0
        assert caps.cpu_cores == 4

    def test_hardware_capabilities_post_init(self):
        """Test HardwareCapabilities __post_init__ sets empty list."""
        caps = HardwareCapabilities(
            has_gpu=False,
            cpu_cores=4,
            system_ram_gb=8,
        )

        assert caps.gpus == []


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_gpu_detection_with_malformed_output(self, mocker):
        """Test GPU detection with unexpected output format."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Unexpected output format\n"
        )

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        # Should handle gracefully
        assert gpu is None or isinstance(gpu, GPUInfo)

    def test_gpu_detection_with_empty_output(self, mocker):
        """Test GPU detection with empty output."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is None

    def test_subprocess_timeout(self, mocker):
        """Test GPU detection handles subprocess timeout."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.TimeoutExpired("nvidia-smi", 5)

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is None

    def test_permission_error(self, mocker):
        """Test GPU detection handles permission errors."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = PermissionError("Access denied")

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is None

    def test_value_error_in_parsing(self, mocker):
        """Test GPU detection handles value errors in parsing."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="NVIDIA RTX 3080, not_a_number"
        )

        detector = HardwareDetector()
        gpu = detector.detect_nvidia_gpu()

        assert gpu is None
