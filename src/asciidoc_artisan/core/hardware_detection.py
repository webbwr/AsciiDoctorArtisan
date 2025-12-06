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

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """Information about detected GPU."""

    vendor: str  # 'NVIDIA', 'AMD', 'Intel', 'Apple'
    model: str
    memory_mb: int | None = None
    compute_capability: str | None = None


@dataclass
class NPUInfo:
    """Information about detected NPU."""

    vendor: str  # 'Intel', 'AMD', 'Qualcomm', 'Apple'
    model: str
    tops: int | None = None  # Trillion Operations Per Second


@dataclass
class HardwareCapabilities:
    """Complete hardware capabilities."""

    has_gpu: bool = False
    has_npu: bool = False
    gpus: list[GPUInfo] = field(default_factory=list)
    npu: NPUInfo | None = None
    cpu_cores: int = 0
    system_ram_gb: int = 0


class HardwareDetector:
    """Detect available hardware for acceleration."""

    @staticmethod
    def detect_nvidia_gpu() -> GPUInfo | None:
        """Detect NVIDIA GPU using nvidia-smi."""
        try:
            # Query nvidia-smi for GPU name and total memory in MB.
            # CSV format prevents parsing issues with spaces in names.
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,  # Prevent hanging if nvidia-smi is unresponsive.
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                if lines:
                    # Parse first GPU only (multi-GPU systems have multiple lines).
                    parts = lines[0].split(",")
                    if len(parts) >= 2:
                        model = parts[0].strip()
                        # Convert to int to handle both "8192" and "8192.0" formats.
                        memory_mb = int(float(parts[1].strip()))
                        logger.info(f"Detected NVIDIA GPU: {model} ({memory_mb}MB)")
                        return GPUInfo(vendor="NVIDIA", model=model, memory_mb=memory_mb)
        except (
            FileNotFoundError,  # nvidia-smi not installed.
            PermissionError,  # No access to nvidia-smi binary.
            subprocess.TimeoutExpired,  # Command took too long.
            ValueError,  # Memory value not a valid number.
        ) as e:
            # Debug level only - GPU absence is normal on many systems.
            logger.debug(f"NVIDIA GPU detection failed: {e}")

        return None

    @staticmethod
    def detect_amd_gpu() -> GPUInfo | None:
        """Detect AMD GPU using rocm-smi or lspci."""
        # Try rocm-smi first (ROCm-specific tool for AMD GPUs).
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Extract first line (GPU product name).
                model = result.stdout.strip().split("\n")[0]
                logger.info(f"Detected AMD GPU: {model}")
                return GPUInfo(vendor="AMD", model=model)
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            # rocm-smi not available - try fallback method.
            pass

        # Try lspci as fallback (works on all Linux systems).
        try:
            result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                # Scan PCI devices for AMD graphics cards.
                for line in result.stdout.split("\n"):
                    if "AMD" in line and ("VGA" in line or "Display" in line):
                        # Extract device description after last colon.
                        model = line.split(":")[-1].strip()
                        logger.info(f"Detected AMD GPU (via lspci): {model}")
                        return GPUInfo(vendor="AMD", model=model)
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            # lspci not available or failed.
            pass

        return None

    @staticmethod
    def detect_intel_gpu() -> GPUInfo | None:
        """Detect Intel GPU using lspci."""
        try:
            result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                # Scan PCI devices for Intel integrated graphics.
                for line in result.stdout.split("\n"):
                    if "Intel" in line and ("VGA" in line or "Display" in line):
                        # Extract device description after last colon.
                        model = line.split(":")[-1].strip()
                        logger.info(f"Detected Intel GPU: {model}")
                        return GPUInfo(vendor="Intel", model=model)
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            # lspci not available or failed.
            pass

        return None

    @staticmethod
    def detect_npu() -> NPUInfo | None:
        """Detect NPU (Neural Processing Unit).

        MA principle: Reduced from 56→16 lines by extracting 2 helpers (71% reduction).
        """
        system = platform.system()

        # Intel/AMD NPU detection (Windows/Linux)
        if system in ("Windows", "Linux"):
            npu = HardwareDetector._detect_intel_amd_npu()
            if npu:
                return npu

        # Apple Neural Engine (macOS)
        if system == "Darwin":
            return HardwareDetector._detect_apple_neural_engine()

        return None

    @staticmethod
    def _detect_intel_amd_npu() -> NPUInfo | None:
        """Detect Intel or AMD NPU via lscpu.

        MA principle: Extracted helper - focused Intel/AMD detection.

        Detects:
        - Intel Core Ultra (Meteor Lake) - dedicated NPU (10-16 TOPS)
        - Intel 11th-14th Gen - Intel GNA (Gaussian Neural Accelerator)
        - AMD Ryzen AI (7040/8040 series) - dedicated NPU (16-50 TOPS)

        Returns:
            NPUInfo if NPU detected, None otherwise
        """
        try:
            result = subprocess.run(["lscpu"], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                return None

            cpu_info = result.stdout.lower()

            # Intel Core Ultra has built-in NPU (Meteor Lake architecture)
            if "core ultra" in cpu_info or "meteor lake" in cpu_info:
                logger.info("Detected Intel NPU (Core Ultra)")
                return NPUInfo(
                    vendor="Intel",
                    model="Intel AI Boost",
                    tops=10,  # Core Ultra NPUs typically 10-16 TOPS
                )

            # Intel 11th-14th Gen has GNA (Gaussian Neural Accelerator)
            # GNA 2.0: 11th Gen, GNA 3.0: 12th-14th Gen
            if "11th gen intel" in cpu_info or "12th gen intel" in cpu_info:
                logger.info("Detected Intel GNA 2.0/3.0 (11th-12th Gen)")
                return NPUInfo(
                    vendor="Intel",
                    model="Intel GNA 3.0",
                    tops=1,  # GNA is lower performance than dedicated NPU
                )

            if "13th gen intel" in cpu_info or "14th gen intel" in cpu_info:
                logger.info("Detected Intel GNA 3.0 (13th-14th Gen)")
                return NPUInfo(
                    vendor="Intel",
                    model="Intel GNA 3.0",
                    tops=1,  # GNA provides ~1 TOPS for low-power AI inference
                )

            # AMD Ryzen AI has built-in NPU (7040/8040 series)
            if "ryzen ai" in cpu_info or "7040" in cpu_info or "8040" in cpu_info:
                logger.info("Detected AMD NPU (Ryzen AI)")
                return NPUInfo(
                    vendor="AMD",
                    model="Ryzen AI",
                    tops=16,  # Ryzen AI NPUs typically 16-50 TOPS
                )

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return None

    @staticmethod
    def _detect_apple_neural_engine() -> NPUInfo | None:
        """Detect Apple Neural Engine via sysctl.

        MA principle: Extracted helper (19 lines) - focused Apple detection.

        Returns:
            NPUInfo if Neural Engine detected, None otherwise
        """
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

        # Get physical cores (excludes hyperthreading).
        # Fall back to logical cores if physical count unavailable.
        cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count() or 1

        # Get total RAM in gigabytes.
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

        # Try each GPU vendor (may find multiple GPUs).
        nvidia_gpu = cls.detect_nvidia_gpu()
        if nvidia_gpu:
            gpus.append(nvidia_gpu)

        amd_gpu = cls.detect_amd_gpu()
        if amd_gpu:
            gpus.append(amd_gpu)

        intel_gpu = cls.detect_intel_gpu()
        if intel_gpu:
            gpus.append(intel_gpu)

        # Detect NPU (neural processing unit).
        npu = cls.detect_npu()

        # Get CPU info (cores and RAM).
        cpu_cores, ram_gb = cls.get_cpu_info()

        # Assemble complete hardware profile.
        caps = HardwareCapabilities(
            has_gpu=len(gpus) > 0,
            has_npu=npu is not None,
            gpus=gpus,
            npu=npu,
            cpu_cores=cpu_cores,
            system_ram_gb=ram_gb,
        )

        logger.info(f"Hardware detection complete: {len(gpus)} GPU(s), NPU: {npu is not None}")
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
                print(f"     Memory: {gpu.memory_mb} MB ({gpu.memory_mb / 1024:.1f} GB)")
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
