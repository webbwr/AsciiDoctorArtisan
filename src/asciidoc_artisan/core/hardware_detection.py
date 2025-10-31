"""
Hardware Detection Module for AsciiDoc Artisan

Detects available hardware acceleration:
- GPU (NVIDIA, AMD, Intel)
- NPU (Neural Processing Unit)
- CPU capabilities

Used to optimize AI workloads and display capabilities to users.
"""

import logging
import platform
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """Information about detected GPU."""

    vendor: str  # 'NVIDIA', 'AMD', 'Intel', 'Apple'
    model: str
    memory_mb: Optional[int] = None
    compute_capability: Optional[str] = None


@dataclass
class NPUInfo:
    """Information about detected NPU."""

    vendor: str  # 'Intel', 'AMD', 'Qualcomm', 'Apple'
    model: str
    tops: Optional[int] = None  # Trillion Operations Per Second


@dataclass
class HardwareCapabilities:
    """Complete hardware capabilities."""

    has_gpu: bool = False
    has_npu: bool = False
    gpus: List[GPUInfo] = field(default_factory=list)
    npu: Optional[NPUInfo] = None
    cpu_cores: int = 0
    system_ram_gb: int = 0


class HardwareDetector:
    """Detect available hardware for acceleration."""

    @staticmethod
    def detect_nvidia_gpu() -> Optional[GPUInfo]:
        """Detect NVIDIA GPU using nvidia-smi."""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                if lines:
                    # Parse first GPU
                    parts = lines[0].split(",")
                    if len(parts) >= 2:
                        model = parts[0].strip()
                        memory_mb = int(float(parts[1].strip()))
                        logger.info(f"Detected NVIDIA GPU: {model} ({memory_mb}MB)")
                        return GPUInfo(
                            vendor="NVIDIA", model=model, memory_mb=memory_mb
                        )
        except (
            FileNotFoundError,
            PermissionError,
            subprocess.TimeoutExpired,
            ValueError,
        ) as e:
            logger.debug(f"NVIDIA GPU detection failed: {e}")

        return None

    @staticmethod
    def detect_amd_gpu() -> Optional[GPUInfo]:
        """Detect AMD GPU using rocm-smi or lspci."""
        # Try rocm-smi first
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                model = result.stdout.strip().split("\n")[0]
                logger.info(f"Detected AMD GPU: {model}")
                return GPUInfo(vendor="AMD", model=model)
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            pass

        # Try lspci as fallback
        try:
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "AMD" in line and ("VGA" in line or "Display" in line):
                        model = line.split(":")[-1].strip()
                        logger.info(f"Detected AMD GPU (via lspci): {model}")
                        return GPUInfo(vendor="AMD", model=model)
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            pass

        return None

    @staticmethod
    def detect_intel_gpu() -> Optional[GPUInfo]:
        """Detect Intel GPU using lspci."""
        try:
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "Intel" in line and ("VGA" in line or "Display" in line):
                        model = line.split(":")[-1].strip()
                        logger.info(f"Detected Intel GPU: {model}")
                        return GPUInfo(vendor="Intel", model=model)
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            pass

        return None

    @staticmethod
    def detect_npu() -> Optional[NPUInfo]:
        """Detect NPU (Neural Processing Unit)."""
        system = platform.system()

        # Intel NPU detection (Core Ultra CPUs)
        if system == "Windows" or system == "Linux":
            try:
                result = subprocess.run(
                    ["lscpu"], capture_output=True, text=True, timeout=5
                )

                if result.returncode == 0:
                    cpu_info = result.stdout.lower()

                    # Intel Core Ultra has NPU
                    if "core ultra" in cpu_info or "meteor lake" in cpu_info:
                        logger.info("Detected Intel NPU (Core Ultra)")
                        return NPUInfo(
                            vendor="Intel",
                            model="Intel AI Boost",
                            tops=10,  # Core Ultra NPUs typically 10-16 TOPS
                        )

                    # AMD Ryzen AI
                    if (
                        "ryzen ai" in cpu_info
                        or "7040" in cpu_info
                        or "8040" in cpu_info
                    ):
                        logger.info("Detected AMD NPU (Ryzen AI)")
                        return NPUInfo(
                            vendor="AMD",
                            model="Ryzen AI",
                            tops=16,  # Ryzen AI NPUs typically 16-50 TOPS
                        )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # Apple Neural Engine
        if system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0 and "Apple" in result.stdout:
                    logger.info("Detected Apple Neural Engine")
                    return NPUInfo(
                        vendor="Apple",
                        model="Apple Neural Engine",
                        tops=15,  # Apple M-series NPUs
                    )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return None

    @staticmethod
    def get_cpu_info() -> tuple[int, int]:
        """Get CPU cores and system RAM.

        Returns:
            Tuple of (cpu_cores, ram_gb)
        """
        import psutil

        cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1
        ram_bytes = psutil.virtual_memory().total
        ram_gb = int(ram_bytes / (1024**3))

        return cpu_cores, ram_gb

    @classmethod
    def detect_all(cls) -> HardwareCapabilities:
        """Detect all available hardware.

        Returns:
            HardwareCapabilities with detected hardware
        """
        logger.info("Detecting hardware capabilities...")

        gpus = []

        # Try each GPU vendor
        nvidia_gpu = cls.detect_nvidia_gpu()
        if nvidia_gpu:
            gpus.append(nvidia_gpu)

        amd_gpu = cls.detect_amd_gpu()
        if amd_gpu:
            gpus.append(amd_gpu)

        intel_gpu = cls.detect_intel_gpu()
        if intel_gpu:
            gpus.append(intel_gpu)

        # Detect NPU
        npu = cls.detect_npu()

        # Get CPU info
        cpu_cores, ram_gb = cls.get_cpu_info()

        caps = HardwareCapabilities(
            has_gpu=len(gpus) > 0,
            has_npu=npu is not None,
            gpus=gpus,
            npu=npu,
            cpu_cores=cpu_cores,
            system_ram_gb=ram_gb,
        )

        logger.info(
            f"Hardware detection complete: {len(gpus)} GPU(s), NPU: {npu is not None}"
        )
        return caps


def print_hardware_report() -> None:
    """Print a human-readable hardware report."""
    caps = HardwareDetector.detect_all()

    print("=" * 60)
    print("HARDWARE CAPABILITIES REPORT")
    print("=" * 60)

    print("\nCPU:")
    print(f"  Cores: {caps.cpu_cores}")
    print(f"  System RAM: {caps.system_ram_gb} GB")

    if caps.has_gpu:
        print(f"\nGPU ({len(caps.gpus)} detected):")
        for i, gpu in enumerate(caps.gpus, 1):
            print(f"  {i}. {gpu.vendor} - {gpu.model}")
            if gpu.memory_mb:
                print(
                    f"     Memory: {gpu.memory_mb} MB ({gpu.memory_mb / 1024:.1f} GB)"
                )
    else:
        print("\nGPU: None detected")

    if caps.has_npu and caps.npu:
        print("\nNPU:")
        print(f"  Vendor: {caps.npu.vendor}")
        print(f"  Model: {caps.npu.model}")
        if caps.npu.tops:
            print(f"  Performance: {caps.npu.tops} TOPS")
    else:
        print("\nNPU: None detected")

    print("\n" + "=" * 60)
    print("ACCELERATION CAPABILITIES")
    print("=" * 60)

    if caps.has_gpu:
        print("✓ GPU acceleration available for:")
        print("  - Preview rendering (2-5x faster)")
        print("  - AI workloads (5-10x faster)")
    else:
        print("✗ GPU acceleration not available")
        print("  - Using CPU fallback (slower)")

    if caps.has_npu:
        print("✓ NPU acceleration available for:")
        print("  - AI inference (10x faster, low power)")
        print("  - Local AI models")
    else:
        print("✗ NPU acceleration not available")
        print("  - Can still use GPU or CPU for AI")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run detection and print report
    print_hardware_report()
