"""GPU Detection Check Functions."""

import logging
import os
import platform
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def check_dri_devices() -> tuple[bool, str | None]:
    """Check for /dev/dri/ devices. Returns (has_devices, device_path)."""
    dri_path = Path("/dev/dri")
    if not dri_path.exists():
        return False, None

    render_devices = list(dri_path.glob("renderD*"))
    if render_devices:
        return True, str(render_devices[0])

    card_devices = list(dri_path.glob("card*"))
    if card_devices:
        return True, str(card_devices[0])

    return False, None


def check_nvidia_gpu() -> tuple[bool, str | None, str | None]:
    """Check for NVIDIA GPU. Returns (has_nvidia, gpu_name, driver_version)."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            gpu_name = parts[0].strip() if len(parts) > 0 else None
            driver_version = parts[1].strip() if len(parts) > 1 else None
            return True, gpu_name, driver_version
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None, None


def check_amd_gpu() -> tuple[bool, str | None]:
    """Check for AMD GPU. Returns (has_amd, gpu_name)."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showproductname"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.split("\n"):
                if "Card series" in line or "Card model" in line:
                    return True, line.split(":")[-1].strip()
            return True, "AMD GPU (unknown model)"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None


def check_intel_gpu() -> tuple[bool, str | None]:
    """Check for Intel GPU. Returns (has_intel, gpu_name)."""
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=0.5)
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.split("\n"):
                if "Device Name" in line and "Intel" in line:
                    return True, line.split("Device Name")[-1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None


def check_opengl_renderer() -> tuple[bool, str | None]:
    """Check OpenGL renderer. Returns (is_hardware, renderer_name)."""
    try:
        result = subprocess.run(["glxinfo"], capture_output=True, text=True, timeout=0.5)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "OpenGL renderer" in line:
                    renderer = line.split(":")[-1].strip()
                    if "llvmpipe" in renderer.lower() or "software" in renderer.lower():
                        return False, renderer
                    return True, renderer
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None


def check_wslg_environment() -> bool:
    """Check if running in WSLg environment."""
    wsl_distro = os.environ.get("WSL_DISTRO_NAME")
    wsl_interop = os.environ.get("WSL_INTEROP")
    wayland_display = os.environ.get("WAYLAND_DISPLAY")
    return bool(wsl_distro or wsl_interop or wayland_display)


def check_wsl2_cuda() -> tuple[bool, str | None, str | None]:
    """Check for WSL2 CUDA GPU support. Returns (has_cuda, gpu_name, driver_version)."""
    if not check_wslg_environment():
        return False, None, None

    wsl_lib_path = Path("/usr/lib/wsl/lib")
    if not wsl_lib_path.exists():
        return False, None, None

    cuda_libs = list(wsl_lib_path.glob("libcuda.so*"))
    if not cuda_libs:
        return False, None, None

    gpu_name = "NVIDIA GPU (WSL2 DirectX passthrough)"
    driver_version = None

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


def _check_npu_via_clinfo() -> tuple[bool, str | None]:
    """Check for Intel NPU via clinfo."""
    try:
        result = subprocess.run(["clinfo"], capture_output=True, text=True, timeout=0.5)
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.split("\n"):
                if "Device Name" in line and ("NPU" in line or "Neural" in line):
                    return True, line.split("Device Name")[-1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None


def _check_npu_via_cpuinfo() -> tuple[bool, str | None]:
    """Check for Intel NPU via /proc/cpuinfo."""
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line.lower():
                    model = line.split(":")[-1].strip()
                    if "Intel" not in model:
                        break
                    gen_match = re.search(r"(\d+)(?:th|st|nd|rd)\s+Gen", model)
                    if gen_match and int(gen_match.group(1)) >= 12:
                        return True, f"Intel NPU ({model})"
                    if "Core Ultra" in model:
                        return True, f"Intel NPU ({model})"
                    break
    except (FileNotFoundError, PermissionError):
        pass
    return False, None


def check_intel_npu() -> tuple[bool, str | None]:
    """Check for Intel NPU. Returns (has_npu, npu_name)."""
    found, name = _check_npu_via_clinfo()
    if found:
        return True, name

    accel_devices = list(Path("/dev").glob("accel*"))
    if accel_devices:
        return True, "Intel NPU (detected via /dev/accel)"

    return _check_npu_via_cpuinfo()


def check_macos_gpu() -> tuple[bool, str | None, str | None]:
    """Check for macOS GPU. Returns (has_gpu, gpu_name, metal_version)."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu_name = None
            metal_version = None
            for line in result.stdout.split("\n"):
                if "Chipset Model:" in line or "GPU:" in line:
                    gpu_name = line.split(":")[-1].strip()
                elif "Metal:" in line or "Metal Support:" in line:
                    metal_version = line.split(":")[-1].strip()
            if gpu_name:
                return True, gpu_name, metal_version
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        if result.returncode == 0 and result.stdout.strip():
            cpu_brand = result.stdout.strip()
            if "Apple M" in cpu_brand:
                return True, f"{cpu_brand} Integrated GPU", "Metal 4"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False, None, None


def check_apple_neural_engine() -> tuple[bool, str | None]:
    """Check for Apple Neural Engine. Returns (has_npu, npu_name)."""
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        if result.returncode == 0 and result.stdout.strip():
            cpu_brand = result.stdout.strip()
            if "Apple M" in cpu_brand:
                if "Ultra" in cpu_brand:
                    return True, f"{cpu_brand} Neural Engine (32-core)"
                return True, f"{cpu_brand} Neural Engine (16-core)"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False, None


def check_compute_command(command: list[str], required_output: str | None = None) -> bool:
    """Check if compute framework command is available."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=0.5)
        if result.returncode != 0:
            return False
        if required_output and required_output not in result.stdout:
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_metal_availability() -> bool:
    """Check if Metal framework is available (macOS only)."""
    if platform.system() != "Darwin":
        return False
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=0.5,
        )
        return result.returncode == 0 and "Metal" in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
