"""
GPU Detection for WSL2/Linux environments.

Detects GPU availability and provides information for enabling
hardware-accelerated rendering in Qt applications.

Implements caching to avoid repeated detection (reduces startup time by ~100ms).
"""

import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """GPU and NPU information container."""

    has_gpu: bool
    gpu_type: Optional[str] = None  # "nvidia", "amd", "intel", "unknown"
    gpu_name: Optional[str] = None
    driver_version: Optional[str] = None
    render_device: Optional[str] = None  # e.g., "/dev/dri/renderD128"
    can_use_webengine: bool = False
    reason: str = ""  # Explanation
    has_npu: bool = False  # Neural Processing Unit
    npu_type: Optional[str] = None  # "intel_npu", "qualcomm_npu", "amd_npu", etc.
    npu_name: Optional[str] = None
    compute_capabilities: list[str] = field(
        default_factory=list
    )  # ["cuda", "opencl", "vulkan", "openvino", etc.]


@dataclass
class GPUCacheEntry:
    """GPU detection cache entry."""

    timestamp: str  # ISO format
    gpu_info: dict  # Serialized GPUInfo
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
            cache_time = datetime.fromisoformat(self.timestamp)
            age = datetime.now() - cache_time
            return age < timedelta(days=ttl_days)
        except (ValueError, TypeError):
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

            data = json.loads(cls.CACHE_FILE.read_text())
            entry = GPUCacheEntry(**data)

            if not entry.is_valid(cls.CACHE_TTL_DAYS):
                logger.info("GPU cache expired")
                return None

            logger.info(f"GPU cache loaded (age: {entry.timestamp})")
            return entry.to_gpu_info()

        except Exception as e:
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
        return False, None

    # Look for render devices
    render_devices = list(dri_path.glob("renderD*"))
    if render_devices:
        return True, str(render_devices[0])

    # Look for card devices
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
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            gpu_name = parts[0].strip() if len(parts) > 0 else None
            driver_version = parts[1].strip() if len(parts) > 1 else None
            return True, gpu_name, driver_version

    except (FileNotFoundError, subprocess.TimeoutExpired):
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
            timeout=5,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse output for GPU name
            for line in result.stdout.split("\n"):
                if "Card series" in line or "Card model" in line:
                    gpu_name = line.split(":")[-1].strip()
                    return True, gpu_name

            return True, "AMD GPU (unknown model)"

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False, None


def check_intel_gpu() -> tuple[bool, Optional[str]]:
    """
    Check for Intel GPU.

    Returns:
        Tuple of (has_intel, gpu_name)
    """
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=5)

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
        result = subprocess.run(["glxinfo"], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "OpenGL renderer" in line:
                    renderer = line.split(":")[-1].strip()

                    # Check if software rendering
                    if "llvmpipe" in renderer.lower():
                        return False, renderer
                    elif "software" in renderer.lower():
                        return False, renderer
                    else:
                        return True, renderer

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False, None


def check_wslg_environment() -> bool:
    """
    Check if running in WSLg environment.

    Returns:
        True if WSLg detected
    """
    # Check for WSL-specific environment variables
    wsl_distro = os.environ.get("WSL_DISTRO_NAME")
    wsl_interop = os.environ.get("WSL_INTEROP")

    # Check for Wayland display (WSLg uses Wayland)
    wayland_display = os.environ.get("WAYLAND_DISPLAY")

    return bool(wsl_distro or wsl_interop or wayland_display)


def check_intel_npu() -> tuple[bool, Optional[str]]:
    """
    Check for Intel NPU (Neural Processing Unit).

    Returns:
        Tuple of (has_npu, npu_name)
    """
    # Check for Intel NPU via OpenVINO
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=5)

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


def detect_compute_capabilities() -> list[str]:
    """
    Detect available compute capabilities.

    Returns:
        List of available compute frameworks
    """
    capabilities = []

    # Check CUDA
    try:
        result = subprocess.run(
            ["nvidia-smi"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            capabilities.append("cuda")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check OpenCL
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "Platform Name" in result.stdout:
            capabilities.append("opencl")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check Vulkan
    try:
        result = subprocess.run(
            ["vulkaninfo", "--summary"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            capabilities.append("vulkan")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check OpenVINO (for NPU)
    if Path("/opt/intel/openvino").exists() or os.environ.get("OPENVINO_DIR"):
        capabilities.append("openvino")

    # Check ROCm (AMD)
    if Path("/opt/rocm").exists():
        capabilities.append("rocm")

    return capabilities


def detect_gpu() -> GPUInfo:
    """
    Detect GPU capabilities for Qt WebEngine.

    Returns:
        GPUInfo object with detection results
    """
    logger.info("Detecting GPU capabilities...")

    # Check for DRI devices
    has_dri, render_device = check_dri_devices()

    if not has_dri:
        return GPUInfo(
            has_gpu=False,
            can_use_webengine=False,
            reason="/dev/dri not found - GPU passthrough not configured",
        )

    # Check OpenGL renderer
    is_hardware, renderer_name = check_opengl_renderer()

    if not is_hardware:
        return GPUInfo(
            has_gpu=False,
            render_device=render_device,
            can_use_webengine=False,
            reason=f"Software rendering detected: {renderer_name}",
        )

    # Detect GPU type
    has_nvidia, nvidia_name, nvidia_driver = check_nvidia_gpu()
    has_amd, amd_name = check_amd_gpu()
    has_intel, intel_name = check_intel_gpu()

    # Determine GPU type and name
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
        gpu_type = "unknown"
        gpu_name = renderer_name
        driver_version = None

    # GPU acceleration works in WSLg with proper NVIDIA drivers
    # WSLg environment: GPU acceleration is automatically available
    can_use = True
    reason = f"Hardware acceleration available: {gpu_name}"

    # Detect NPU
    has_npu, npu_name = check_intel_npu()
    npu_type = "intel_npu" if has_npu else None

    # Detect compute capabilities
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

    # Try memory cache first
    if _cached_gpu_info is not None and not force_redetect:
        return _cached_gpu_info

    # Try disk cache if not forcing redetection
    if not force_redetect:
        cached_info = GPUDetectionCache.load()
        if cached_info is not None:
            _cached_gpu_info = cached_info
            log_gpu_info(_cached_gpu_info)
            return _cached_gpu_info

    # Perform full detection
    _cached_gpu_info = detect_gpu()
    log_gpu_info(_cached_gpu_info)

    # Save to disk cache
    from asciidoc_artisan.core import APP_VERSION

    GPUDetectionCache.save(_cached_gpu_info, APP_VERSION)

    return _cached_gpu_info


def main():
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
