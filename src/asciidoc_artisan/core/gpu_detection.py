"""
GPU Detection for WSL2/Linux environments.

Detects GPU availability and provides information for enabling
hardware-accelerated rendering in Qt applications.

Implements caching to avoid repeated detection (reduces startup time by ~100ms).
"""

import json
import logging
import os
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """GPU and NPU information container."""

    has_gpu: bool
    gpu_type: Optional[str] = None  # "nvidia", "amd", "intel", "apple", "unknown"
    gpu_name: Optional[str] = None
    driver_version: Optional[str] = None
    render_device: Optional[str] = (
        None  # e.g., "/dev/dri/renderD128" (Linux) or "Metal" (macOS)
    )
    can_use_webengine: bool = False
    reason: str = ""  # Explanation
    has_npu: bool = False  # Neural Processing Unit
    npu_type: Optional[str] = None  # "intel_npu", "apple_neural_engine", etc.
    npu_name: Optional[str] = None
    compute_capabilities: list[str] = field(
        default_factory=list
    )  # ["cuda", "opencl", "vulkan", "openvino", "metal", etc.]
    metal_version: Optional[str] = None  # Metal framework version (macOS only)


@dataclass
class GPUCacheEntry:
    """GPU detection cache entry."""

    timestamp: str  # ISO format
    gpu_info: Dict[str, Any]  # Serialized GPUInfo
    version: str  # App version

    @classmethod
    def from_gpu_info(cls, gpu_info: GPUInfo, version: str) -> "GPUCacheEntry":
        """Create cache entry from GPUInfo."""
        return cls(
            timestamp=datetime.now().isoformat(),
            gpu_info=asdict(gpu_info),
            version=version,
        )

    def to_gpu_info(self) -> GPUInfo:
        """Reconstruct GPUInfo from cache."""
        return GPUInfo(**self.gpu_info)

    def is_valid(self, ttl_days: int = 7) -> bool:
        """Check if cache entry is still valid."""
        try:
            # Parse timestamp and calculate age.
            cache_time = datetime.fromisoformat(self.timestamp)
            age = datetime.now() - cache_time
            # Cache is valid if younger than TTL.
            return age < timedelta(days=ttl_days)
        except (ValueError, TypeError):
            # Invalid timestamp format - treat as expired.
            return False


class GPUDetectionCache:
    """Persistent cache for GPU detection results."""

    CACHE_FILE = Path.home() / ".config" / "AsciiDocArtisan" / "gpu_cache.json"
    CACHE_TTL_DAYS = 7

    @classmethod
    def load(cls) -> Optional[GPUInfo]:
        """Load GPU info from cache if valid."""
        try:
            if not cls.CACHE_FILE.exists():
                logger.debug("GPU cache file not found")
                return None

            # Read and parse cache file JSON.
            data = json.loads(cls.CACHE_FILE.read_text())
            entry = GPUCacheEntry(**data)

            # Check if cache is still fresh (within TTL).
            if not entry.is_valid(cls.CACHE_TTL_DAYS):
                logger.info("GPU cache expired")
                return None

            logger.info(f"GPU cache loaded (age: {entry.timestamp})")
            return entry.to_gpu_info()

        except Exception as e:
            # Corrupted cache file - will re-detect GPU.
            logger.warning(f"Failed to load GPU cache: {e}")
            return None

    @classmethod
    def save(cls, gpu_info: GPUInfo, version: str) -> bool:
        """Save GPU info to cache."""
        try:
            cls.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

            entry = GPUCacheEntry.from_gpu_info(gpu_info, version)
            cls.CACHE_FILE.write_text(json.dumps(asdict(entry), indent=2))

            logger.info("GPU cache saved")
            return True

        except Exception as e:
            logger.error(f"Failed to save GPU cache: {e}")
            return False

    @classmethod
    def clear(cls) -> None:
        """Clear GPU cache."""
        try:
            if cls.CACHE_FILE.exists():
                cls.CACHE_FILE.unlink()
                logger.info("GPU cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear GPU cache: {e}")


def check_dri_devices() -> tuple[bool, Optional[str]]:
    """
    Check for /dev/dri/ devices (DRI = Direct Rendering Infrastructure).

    Returns:
        Tuple of (has_devices, device_path)
    """
    dri_path = Path("/dev/dri")

    if not dri_path.exists():
        # No DRI directory - GPU passthrough not configured.
        return False, None

    # Look for render devices (preferred for GPU acceleration).
    render_devices = list(dri_path.glob("renderD*"))
    if render_devices:
        return True, str(render_devices[0])

    # Look for card devices (legacy fallback).
    card_devices = list(dri_path.glob("card*"))
    if card_devices:
        return True, str(card_devices[0])

    return False, None


def check_nvidia_gpu() -> tuple[bool, Optional[str], Optional[str]]:
    """
    Check for NVIDIA GPU.

    Returns:
        Tuple of (has_nvidia, gpu_name, driver_version)
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=1,  # Prevent hanging if nvidia-smi is slow.
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse CSV output (GPU name, driver version).
            parts = result.stdout.strip().split(",")
            gpu_name = parts[0].strip() if len(parts) > 0 else None
            driver_version = parts[1].strip() if len(parts) > 1 else None
            return True, gpu_name, driver_version

    except (FileNotFoundError, subprocess.TimeoutExpired):
        # nvidia-smi not installed or failed.
        pass

    return False, None, None


def check_amd_gpu() -> tuple[bool, Optional[str]]:
    """
    Check for AMD GPU.

    Returns:
        Tuple of (has_amd, gpu_name)
    """
    try:
        result = subprocess.run(
            ["rocm-smi", "--showproductname"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse output for GPU name (varies by ROCm version).
            for line in result.stdout.split("\n"):
                if "Card series" in line or "Card model" in line:
                    gpu_name = line.split(":")[-1].strip()
                    return True, gpu_name

            # ROCm found GPU but format not recognized.
            return True, "AMD GPU (unknown model)"

    except (FileNotFoundError, subprocess.TimeoutExpired):
        # rocm-smi not installed or timed out.
        pass

    return False, None


def check_intel_gpu() -> tuple[bool, Optional[str]]:
    """
    Check for Intel GPU.

    Returns:
        Tuple of (has_intel, gpu_name)
    """
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=1)

        if result.returncode == 0 and result.stdout.strip():
            # Look for Intel device
            for line in result.stdout.split("\n"):
                if "Device Name" in line and "Intel" in line:
                    gpu_name = line.split("Device Name")[-1].strip()
                    return True, gpu_name

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False, None


def check_opengl_renderer() -> tuple[bool, Optional[str]]:
    """
    Check OpenGL renderer (software vs hardware).

    Returns:
        Tuple of (is_hardware, renderer_name)
    """
    try:
        result = subprocess.run(["glxinfo"], capture_output=True, text=True, timeout=1)

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "OpenGL renderer" in line:
                    renderer = line.split(":")[-1].strip()

                    # Check if software rendering (CPU fallback).
                    if "llvmpipe" in renderer.lower():
                        # LLVM pipe is Mesa's software renderer.
                        return False, renderer
                    elif "software" in renderer.lower():
                        return False, renderer
                    else:
                        # Hardware renderer detected.
                        return True, renderer

    except (FileNotFoundError, subprocess.TimeoutExpired):
        # glxinfo not installed or failed.
        pass

    return False, None


def check_wslg_environment() -> bool:
    """
    Check if running in WSLg environment.

    Returns:
        True if WSLg detected
    """
    # Check for WSL-specific environment variables (Windows Subsystem for Linux).
    wsl_distro = os.environ.get("WSL_DISTRO_NAME")
    wsl_interop = os.environ.get("WSL_INTEROP")

    # Check for Wayland display (WSLg uses Wayland for graphics).
    wayland_display = os.environ.get("WAYLAND_DISPLAY")

    # Return true if any WSL indicator is present.
    return bool(wsl_distro or wsl_interop or wayland_display)


def check_intel_npu() -> tuple[bool, Optional[str]]:
    """
    Check for Intel NPU (Neural Processing Unit).

    Returns:
        Tuple of (has_npu, npu_name)
    """
    # Check for Intel NPU via OpenVINO
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=1)

        if result.returncode == 0 and result.stdout.strip():
            # Look for Intel NPU device
            for line in result.stdout.split("\n"):
                if "Device Name" in line and ("NPU" in line or "Neural" in line):
                    npu_name = line.split("Device Name")[-1].strip()
                    return True, npu_name

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check /dev/accel* devices (Intel NPU driver)
    accel_path = Path("/dev")
    accel_devices = list(accel_path.glob("accel*"))
    if accel_devices:
        return True, "Intel NPU (detected via /dev/accel)"

    return False, None


def check_macos_gpu() -> tuple[bool, Optional[str], Optional[str]]:
    """
    Check for macOS GPU (Metal framework).

    Returns:
        Tuple of (has_gpu, gpu_name, metal_version)
    """
    try:
        # Check for Metal support via system_profiler
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse output for GPU name and Metal version
            gpu_name = None
            metal_version = None

            for line in result.stdout.split("\n"):
                # Look for Chipset Model or GPU name
                if "Chipset Model:" in line or "GPU:" in line:
                    gpu_name = line.split(":")[-1].strip()
                # Look for Metal version
                elif "Metal:" in line or "Metal Support:" in line:
                    metal_version = line.split(":")[-1].strip()

            # If we found GPU info, return it
            if gpu_name:
                return True, gpu_name, metal_version

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try alternate method - sysctl for Apple Silicon
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        if result.returncode == 0 and result.stdout.strip():
            cpu_brand = result.stdout.strip()
            # Apple Silicon (M1, M2, M3, M4) includes integrated GPU
            if "Apple M" in cpu_brand:
                # Extract chip name (e.g., "Apple M1 Ultra")
                return True, f"{cpu_brand} Integrated GPU", "Metal 4"

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False, None, None


def check_apple_neural_engine() -> tuple[bool, Optional[str]]:
    """
    Check for Apple Neural Engine (NPU on Apple Silicon).

    Returns:
        Tuple of (has_npu, npu_name)
    """
    try:
        # Check for Apple Silicon chip via sysctl
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        if result.returncode == 0 and result.stdout.strip():
            cpu_brand = result.stdout.strip()
            # Apple Silicon (M1+) includes Neural Engine
            if "Apple M" in cpu_brand:
                # Extract core count if available
                try:
                    # Try to get Neural Engine core count
                    # M1: 16-core, M1 Pro/Max: 16-core, M1 Ultra: 32-core
                    # M2: 16-core, M2 Pro/Max: 16-core, M2 Ultra: 32-core
                    # M3: 16-core, M3 Pro/Max: 16-core
                    if "Ultra" in cpu_brand:
                        return True, f"{cpu_brand} Neural Engine (32-core)"
                    elif "Max" in cpu_brand or "Pro" in cpu_brand:
                        return True, f"{cpu_brand} Neural Engine (16-core)"
                    else:
                        return True, f"{cpu_brand} Neural Engine (16-core)"
                except Exception:
                    # Fallback - just report it exists
                    return True, f"{cpu_brand} Neural Engine"

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False, None


def detect_compute_capabilities() -> list[str]:
    """
    Detect available compute capabilities.

    Returns:
        List of available compute frameworks
    """
    capabilities = []

    # Check CUDA (NVIDIA GPU compute).
    try:
        result = subprocess.run(
            ["nvidia-smi"], capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            capabilities.append("cuda")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # CUDA not available.
        pass

    # Check OpenCL (cross-platform GPU compute).
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=1)
        if result.returncode == 0 and "Platform Name" in result.stdout:
            capabilities.append("opencl")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # OpenCL not available.
        pass

    # Check Vulkan (modern graphics and compute API).
    try:
        result = subprocess.run(
            ["vulkaninfo", "--summary"], capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            capabilities.append("vulkan")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # Vulkan not available.
        pass

    # Check OpenVINO (Intel NPU framework).
    if Path("/opt/intel/openvino").exists() or os.environ.get("OPENVINO_DIR"):
        capabilities.append("openvino")

    # Check ROCm (AMD GPU compute framework).
    if Path("/opt/rocm").exists():
        capabilities.append("rocm")

    # Check Metal (macOS GPU framework).
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            if result.returncode == 0 and "Metal" in result.stdout:
                capabilities.append("metal")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return capabilities


def detect_gpu() -> GPUInfo:
    """
    Detect GPU capabilities for Qt WebEngine.

    Returns:
        GPUInfo object with detection results
    """
    logger.info("Detecting GPU capabilities...")

    # macOS detection (Metal framework)
    if platform.system() == "Darwin":
        logger.info("Detected macOS - checking for Metal GPU support")

        # Check for macOS GPU (Metal)
        has_macos_gpu, macos_gpu_name, metal_version = check_macos_gpu()

        if not has_macos_gpu:
            # No GPU detected on macOS
            return GPUInfo(
                has_gpu=False,
                can_use_webengine=False,
                reason="No Metal-compatible GPU detected on macOS",
            )

        # GPU detected - check for Neural Engine (NPU)
        has_npu, npu_name = check_apple_neural_engine()
        npu_type = "apple_neural_engine" if has_npu else None

        # Detect compute capabilities
        compute_capabilities = detect_compute_capabilities()

        # macOS with Metal GPU detected, but QtWebEngine not compatible
        # Use QTextBrowser (software rendering) to avoid crashes
        return GPUInfo(
            has_gpu=True,
            gpu_type="apple",
            gpu_name=macos_gpu_name,
            driver_version=metal_version,
            render_device="Metal",
            can_use_webengine=False,  # Disabled on macOS - QtWebEngine crashes with Metal
            reason=f"macOS Metal GPU detected ({macos_gpu_name}) - using software rendering (QtWebEngine not compatible)",
            has_npu=has_npu,
            npu_type=npu_type,
            npu_name=npu_name,
            compute_capabilities=compute_capabilities,
            metal_version=metal_version,
        )

    # Linux/Windows detection (DRI devices)
    # Check for DRI devices (required for GPU access in Linux).
    has_dri, render_device = check_dri_devices()

    if not has_dri:
        # No GPU passthrough - cannot use hardware acceleration.
        return GPUInfo(
            has_gpu=False,
            can_use_webengine=False,
            reason="/dev/dri not found - GPU passthrough not configured",
        )

    # Check OpenGL renderer (hardware vs software).
    is_hardware, renderer_name = check_opengl_renderer()

    if not is_hardware:
        # Software rendering detected - GPU not usable.
        return GPUInfo(
            has_gpu=False,
            render_device=render_device,
            can_use_webengine=False,
            reason=f"Software rendering detected: {renderer_name}",
        )

    # Detect GPU type (NVIDIA, AMD, or Intel).
    has_nvidia, nvidia_name, nvidia_driver = check_nvidia_gpu()
    has_amd, amd_name = check_amd_gpu()
    has_intel, intel_name = check_intel_gpu()

    # Determine which GPU vendor is present (prioritize NVIDIA).
    if has_nvidia:
        gpu_type = "nvidia"
        gpu_name = nvidia_name
        driver_version = nvidia_driver
    elif has_amd:
        gpu_type = "amd"
        gpu_name = amd_name
        driver_version = None
    elif has_intel:
        gpu_type = "intel"
        gpu_name = intel_name
        driver_version = None
    else:
        # GPU present but vendor unknown.
        gpu_type = "unknown"
        gpu_name = renderer_name
        driver_version = None

    # GPU acceleration works in WSLg with proper drivers.
    # WSLg environment: GPU acceleration is automatically available.
    can_use = True
    reason = f"Hardware acceleration available: {gpu_name}"

    # Detect NPU (neural processing unit).
    has_npu, npu_name = check_intel_npu()
    npu_type = "intel_npu" if has_npu else None

    # Detect compute capabilities (CUDA, OpenCL, Vulkan, etc.).
    compute_capabilities = detect_compute_capabilities()

    return GPUInfo(
        has_gpu=True,
        gpu_type=gpu_type,
        gpu_name=gpu_name,
        driver_version=driver_version,
        render_device=render_device,
        can_use_webengine=can_use,
        reason=reason,
        has_npu=has_npu,
        npu_type=npu_type,
        npu_name=npu_name,
        compute_capabilities=compute_capabilities,
    )


def log_gpu_info(gpu_info: GPUInfo) -> None:
    """
    Log GPU and NPU information.

    Args:
        gpu_info: GPUInfo object
    """
    if gpu_info.has_gpu:
        logger.info(f"GPU detected: {gpu_info.gpu_name} ({gpu_info.gpu_type})")
        if gpu_info.driver_version:
            logger.info(f"Driver version: {gpu_info.driver_version}")
        if gpu_info.metal_version:
            logger.info(f"Metal version: {gpu_info.metal_version}")
        logger.info(f"Render device: {gpu_info.render_device}")
        logger.info(f"WebEngine GPU support: {gpu_info.can_use_webengine}")
    else:
        logger.warning(f"No GPU detected: {gpu_info.reason}")

    # Log NPU info
    if gpu_info.has_npu:
        logger.info(f"NPU detected: {gpu_info.npu_name} ({gpu_info.npu_type})")
    else:
        logger.info("No NPU detected")

    # Log compute capabilities
    if gpu_info.compute_capabilities:
        logger.info(f"Compute capabilities: {', '.join(gpu_info.compute_capabilities)}")
    else:
        logger.info("No compute capabilities detected")

    logger.info(f"Status: {gpu_info.reason}")


# Cached GPU info (detect once per session)
_cached_gpu_info: Optional[GPUInfo] = None


def get_gpu_info(force_redetect: bool = False) -> GPUInfo:
    """
    Get GPU information (cached in memory and on disk).

    Args:
        force_redetect: Force re-detection even if cached

    Returns:
        GPUInfo object
    """
    global _cached_gpu_info

    # Try memory cache first (fastest).
    if _cached_gpu_info is not None and not force_redetect:
        return _cached_gpu_info

    # Try disk cache if not forcing redetection (avoids slow detection).
    if not force_redetect:
        cached_info = GPUDetectionCache.load()
        if cached_info is not None:
            # Populate memory cache from disk.
            _cached_gpu_info = cached_info
            log_gpu_info(_cached_gpu_info)
            return _cached_gpu_info

    # Perform full detection (slow - runs external commands).
    _cached_gpu_info = detect_gpu()
    log_gpu_info(_cached_gpu_info)

    # Save to disk cache for future runs (reduces startup time).
    from asciidoc_artisan.core import APP_VERSION

    GPUDetectionCache.save(_cached_gpu_info, APP_VERSION)

    return _cached_gpu_info


def main() -> None:
    """CLI for GPU cache management."""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "clear":
            GPUDetectionCache.clear()
            print("GPU cache cleared")
        elif command == "show":
            info = GPUDetectionCache.load()
            if info:
                print(f"Cached GPU: {info.gpu_name}")
                print(f"Type: {info.gpu_type}")
                print(f"Capabilities: {', '.join(info.compute_capabilities)}")
                if info.has_npu:
                    print(f"NPU: {info.npu_name}")
            else:
                print("No cached GPU info")
        elif command == "detect":
            info = get_gpu_info(force_redetect=True)
            print(f"Detected GPU: {info.gpu_name}")
            print(f"Type: {info.gpu_type}")
            print(f"Driver: {info.driver_version}")
            print(f"Capabilities: {', '.join(info.compute_capabilities)}")
            if info.has_npu:
                print(f"NPU: {info.npu_name}")
        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python -m asciidoc_artisan.core.gpu_detection [clear|show|detect]"
            )
    else:
        print("GPU Detection Cache Manager")
        print(
            "Usage: python -m asciidoc_artisan.core.gpu_detection [clear|show|detect]"
        )
        print("")
        print("Commands:")
        print("  clear  - Clear GPU cache")
        print("  show   - Show cached GPU info")
        print("  detect - Force GPU detection and update cache")


if __name__ == "__main__":
    main()
