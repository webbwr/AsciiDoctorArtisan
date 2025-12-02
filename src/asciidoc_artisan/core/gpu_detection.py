"""
GPU Detection for WSL2/Linux environments.

Detects GPU availability and provides information for enabling
hardware-accelerated rendering in Qt applications.

Implements caching to avoid repeated detection (reduces startup time by ~100ms).

This module orchestrates GPU detection using helper modules:
- gpu_models.py: Data classes (GPUInfo, GPUCacheEntry)
- gpu_cache.py: Persistent cache management
- gpu_checks.py: Individual hardware check functions
"""

import logging
import os
import platform
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from asciidoc_artisan.core.gpu_cache import GPUDetectionCache
from asciidoc_artisan.core.gpu_checks import (
    check_amd_gpu,
    check_apple_neural_engine,
    check_compute_command,
    check_dri_devices,
    check_intel_gpu,
    check_intel_npu,
    check_macos_gpu,
    check_metal_availability,
    check_nvidia_gpu,
    check_opengl_renderer,
    check_wslg_environment,
)
from asciidoc_artisan.core.gpu_models import GPUCacheEntry, GPUInfo

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = [
    "GPUInfo",
    "GPUCacheEntry",
    "GPUDetectionCache",
    "check_dri_devices",
    "check_nvidia_gpu",
    "check_amd_gpu",
    "check_intel_gpu",
    "check_opengl_renderer",
    "check_wslg_environment",
    "check_intel_npu",
    "check_macos_gpu",
    "check_apple_neural_engine",
    "detect_compute_capabilities",
    "detect_gpu",
    "log_gpu_info",
    "get_gpu_info",
]


def detect_compute_capabilities() -> list[str]:
    """
    Detect available compute capabilities using parallel checks.

    MA principle: Parallel command checks reduce detection time.

    Returns:
        List of available compute frameworks
    """
    capabilities: list[str] = []

    # Define command-based framework checks
    command_checks = [
        ("cuda", ["nvidia-smi"], None),
        ("opencl", ["clinfo"], "Platform Name"),
        ("vulkan", ["vulkaninfo", "--summary"], None),
    ]

    # Run command checks in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures: dict[Future[bool], str] = {
            executor.submit(check_compute_command, command, required): name
            for name, command, required in command_checks
        }

        for future in as_completed(futures, timeout=3.0):
            name = futures[future]
            try:
                if future.result():
                    capabilities.append(name)
            except Exception:
                pass  # Skip failed checks

    # Check path-based frameworks (fast, no parallelization needed)
    if Path("/opt/intel/openvino").exists() or os.environ.get("OPENVINO_DIR"):
        capabilities.append("openvino")

    if Path("/opt/rocm").exists():
        capabilities.append("rocm")

    # Check macOS Metal
    if check_metal_availability():
        capabilities.append("metal")

    return capabilities


def detect_gpu() -> GPUInfo:
    """
    Detect GPU capabilities for Qt WebEngine.

    Returns:
        GPUInfo object with detection results
    """
    logger.info("Detecting GPU capabilities...")

    # Detect based on platform
    if platform.system() == "Darwin":
        return _detect_macos_gpu()

    return _detect_linux_windows_gpu()


def _detect_macos_gpu() -> GPUInfo:
    """Detect GPU on macOS (Metal framework)."""
    logger.info("Detected macOS - checking for Metal GPU support")

    # Check for Metal GPU
    has_macos_gpu, macos_gpu_name, metal_version = check_macos_gpu()
    if not has_macos_gpu:
        return GPUInfo(
            has_gpu=False,
            can_use_webengine=False,
            reason="No Metal-compatible GPU detected on macOS",
        )

    # Detect additional capabilities
    has_npu, npu_name = check_apple_neural_engine()
    compute_capabilities = detect_compute_capabilities()

    # macOS with Metal GPU - fully supported
    return GPUInfo(
        has_gpu=True,
        gpu_type="apple",
        gpu_name=macos_gpu_name,
        driver_version=metal_version,
        render_device="Metal",
        can_use_webengine=True,
        reason=f"Hardware acceleration available: {macos_gpu_name} (Metal {metal_version or 'supported'})",
        has_npu=has_npu,
        npu_type="apple_neural_engine" if has_npu else None,
        npu_name=npu_name,
        compute_capabilities=compute_capabilities,
        metal_version=metal_version,
    )


def _detect_linux_windows_gpu() -> GPUInfo:
    """Detect GPU on Linux/Windows (DRI devices)."""
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

    # Detect GPU vendor and capabilities
    gpu_type, gpu_name, driver_version = _detect_gpu_vendor(renderer_name)
    has_npu, npu_name = check_intel_npu()
    compute_capabilities = detect_compute_capabilities()

    return GPUInfo(
        has_gpu=True,
        gpu_type=gpu_type,
        gpu_name=gpu_name,
        driver_version=driver_version,
        render_device=render_device,
        can_use_webengine=True,
        reason=f"Hardware acceleration available: {gpu_name}",
        has_npu=has_npu,
        npu_type="intel_npu" if has_npu else None,
        npu_name=npu_name,
        compute_capabilities=compute_capabilities,
    )


def _detect_gpu_vendor(renderer_name: str | None) -> tuple[str, str | None, str | None]:
    """
    Detect GPU vendor (NVIDIA, AMD, Intel) using parallel checks.

    MA principle: Parallel vendor checks reduce detection time by ~60% (500ms → 200ms).

    Args:
        renderer_name: Fallback renderer name (may be None)

    Returns:
        Tuple of (gpu_type, gpu_name, driver_version)
    """
    results: dict[str, Any] = {}

    # Run GPU vendor checks in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures: dict[Future[Any], str] = {
            executor.submit(check_nvidia_gpu): "nvidia",
            executor.submit(check_amd_gpu): "amd",
            executor.submit(check_intel_gpu): "intel",
        }

        for future in as_completed(futures, timeout=3.0):
            vendor = futures[future]
            try:
                results[vendor] = future.result()
            except Exception:
                results[vendor] = None

    # Evaluate results in priority order (NVIDIA > AMD > Intel)
    nvidia_result = results.get("nvidia")
    if nvidia_result and nvidia_result[0]:  # has_nvidia
        return ("nvidia", nvidia_result[1], nvidia_result[2])

    amd_result = results.get("amd")
    if amd_result and amd_result[0]:  # has_amd
        return ("amd", amd_result[1], None)

    intel_result = results.get("intel")
    if intel_result and intel_result[0]:  # has_intel
        return ("intel", intel_result[1], None)

    # Unknown vendor
    return ("unknown", renderer_name, None)


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
_cached_gpu_info: GPUInfo | None = None


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
            print("Usage: python -m asciidoc_artisan.core.gpu_detection [clear|show|detect]")
    else:
        print("GPU Detection Cache Manager")
        print("Usage: python -m asciidoc_artisan.core.gpu_detection [clear|show|detect]")
        print("")
        print("Commands:")
        print("  clear  - Clear GPU cache")
        print("  show   - Show cached GPU info")
        print("  detect - Force GPU detection and update cache")


if __name__ == "__main__":
    main()
