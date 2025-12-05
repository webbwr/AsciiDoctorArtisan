"""
GPU Detection Check Functions.

Extracted from gpu_detection.py for MA principle compliance.
Contains individual hardware detection functions for various GPU/NPU types.
"""

import logging
import os
import platform
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def check_dri_devices() -> tuple[bool, str | None]:
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


def check_nvidia_gpu() -> tuple[bool, str | None, str | None]:
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


def check_amd_gpu() -> tuple[bool, str | None]:
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


def check_intel_gpu() -> tuple[bool, str | None]:
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


def check_opengl_renderer() -> tuple[bool, str | None]:
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


def check_wsl2_cuda() -> tuple[bool, str | None, str | None]:
    """
    Check for WSL2 CUDA GPU support (DirectX 12 passthrough).

    WSL2 uses DirectX 12 GPU passthrough with CUDA libraries in /usr/lib/wsl/lib.
    This doesn't require /dev/dri devices like native Linux.

    Returns:
        Tuple of (has_cuda, gpu_name, driver_version)
    """
    # Check for WSL2 environment
    if not check_wslg_environment():
        return False, None, None

    # Check for WSL2 CUDA libraries
    wsl_lib_path = Path("/usr/lib/wsl/lib")
    if not wsl_lib_path.exists():
        return False, None, None

    # Look for CUDA library
    cuda_libs = list(wsl_lib_path.glob("libcuda.so*"))
    if not cuda_libs:
        return False, None, None

    # CUDA libraries found - try to get GPU info via Windows host
    gpu_name = "NVIDIA GPU (WSL2 DirectX passthrough)"
    driver_version = None

    # Try nvidia-smi.exe (Windows host)
    try:
        result = subprocess.run(
            ["/mnt/c/Windows/System32/nvidia-smi.exe", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            gpu_name = parts[0].strip() if len(parts) > 0 else gpu_name
            driver_version = parts[1].strip() if len(parts) > 1 else None

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    logger.info(f"WSL2 CUDA GPU detected: {gpu_name}")
    return True, gpu_name, driver_version


def check_intel_npu() -> tuple[bool, str | None]:
    """
    Check for Intel NPU (Neural Processing Unit).

    Intel 12th gen (Alder Lake) and newer CPUs have integrated NPUs.
    WSL2 may not expose /dev/accel but the NPU is still present on host.

    Returns:
        Tuple of (has_npu, npu_name)
    """
    # Check for Intel NPU via OpenVINO/clinfo
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

    # Check /dev/accel* devices (Intel NPU driver on native Linux)
    accel_path = Path("/dev")
    accel_devices = list(accel_path.glob("accel*"))
    if accel_devices:
        return True, "Intel NPU (detected via /dev/accel)"

    # Check CPU model for Intel 12th gen+ (Alder Lake and newer have NPU)
    # This works in WSL2 where /dev/accel is not exposed
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
            for line in cpuinfo.split("\n"):
                if "model name" in line.lower():
                    model = line.split(":")[-1].strip()
                    # Intel 12th gen (Alder Lake), 13th gen (Raptor Lake), 14th gen (Meteor Lake)
                    # and Core Ultra have integrated NPUs
                    if "Intel" in model:
                        # Check for generation number
                        import re

                        gen_match = re.search(r"(\d+)(?:th|st|nd|rd)\s+Gen", model)
                        if gen_match:
                            gen = int(gen_match.group(1))
                            if gen >= 12:
                                return True, f"Intel NPU ({model})"
                        # Check for Core Ultra (all have NPU)
                        if "Core Ultra" in model:
                            return True, f"Intel NPU ({model})"
                    break
    except (FileNotFoundError, PermissionError):
        pass

    return False, None


def check_macos_gpu() -> tuple[bool, str | None, str | None]:
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


def check_apple_neural_engine() -> tuple[bool, str | None]:
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


def check_compute_command(command: list[str], required_output: str | None = None) -> bool:
    """Check if compute framework command is available.

    MA principle: Extracted helper (13 lines) - focused command execution.

    Args:
        command: Command to execute (e.g., ["nvidia-smi"])
        required_output: Optional string that must appear in stdout

    Returns:
        True if command succeeded and output matches (if required)
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=1)
        if result.returncode != 0:
            return False
        if required_output and required_output not in result.stdout:
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_metal_availability() -> bool:
    """Check if Metal framework is available (macOS only).

    MA principle: Extracted helper (14 lines) - focused Metal detection.

    Returns:
        True if Metal is available on this macOS system
    """
    if platform.system() != "Darwin":
        return False

    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.returncode == 0 and "Metal" in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
