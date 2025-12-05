"""macOS Optimizer - Apple Silicon & Metal Performance Optimizations."""

import logging
import os
import platform
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MacOSOptimizationInfo:
    """macOS optimization configuration and capabilities."""

    is_macos: bool = False
    is_apple_silicon: bool = False
    chip_name: str = ""
    metal_version: str = ""
    unified_memory_gb: int = 0
    performance_cores: int = 0
    efficiency_cores: int = 0
    neural_engine_cores: int = 0
    gpu_cores: int = 0
    metal_feature_set: str = ""
    apfs_enabled: bool = False
    gcd_available: bool = False


def _run_sysctl(key: str, timeout: int = 1) -> str | None:
    """Run sysctl command and return output."""
    try:
        result = subprocess.run(["sysctl", "-n", key], capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    return None


def _detect_chip_name(info: MacOSOptimizationInfo) -> None:
    """Detect Apple Silicon chip name."""
    brand = _run_sysctl("machdep.cpu.brand_string")
    if brand:
        for chip in ["M4", "M3", "M2", "M1"]:
            if chip in brand:
                info.chip_name = brand
                break


def _detect_memory_size(info: MacOSOptimizationInfo) -> None:
    """Detect unified memory size in GB."""
    mem_str = _run_sysctl("hw.memsize")
    if mem_str:
        try:
            info.unified_memory_gb = int(mem_str) // (1024**3)
        except ValueError:
            pass


def _detect_performance_cores(info: MacOSOptimizationInfo) -> None:
    """Detect performance core count."""
    cores_str = _run_sysctl("hw.perflevel0.physicalcpu")
    if cores_str:
        try:
            info.performance_cores = int(cores_str)
        except ValueError:
            pass


def _detect_efficiency_cores(info: MacOSOptimizationInfo) -> None:
    """Detect efficiency core count."""
    cores_str = _run_sysctl("hw.perflevel1.physicalcpu")
    if cores_str:
        try:
            info.efficiency_cores = int(cores_str)
        except ValueError:
            pass


def _detect_metal_and_gpu(info: MacOSOptimizationInfo) -> None:
    """Detect Metal version and GPU core count."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType", "-detailLevel", "mini", "-json"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            import json

            try:
                data = json.loads(result.stdout)
                displays = data.get("SPDisplaysDataType", [])
                for display in displays:
                    metal_info = display.get("spdisplays_mtlgpufamilymacOS", "")
                    if metal_info:
                        info.metal_version = metal_info
                        if "Metal" in metal_info:
                            info.metal_feature_set = metal_info
                    chip_type = display.get("sppci_model", "")
                    if "GPU" in chip_type:
                        for cores, pattern in [
                            (64, "64-core"),
                            (48, "48-core"),
                            (32, "32-core"),
                            (24, "24-core"),
                            (16, "16-core"),
                            (10, "10-core"),
                            (8, "8-core"),
                        ]:
                            if pattern in chip_type:
                                info.gpu_cores = cores
                                break
            except (json.JSONDecodeError, KeyError):
                pass
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass


def _infer_neural_engine_cores(info: MacOSOptimizationInfo) -> None:
    """Infer Neural Engine core count from chip name."""
    if not info.chip_name:
        return
    is_ultra = "Ultra" in info.chip_name
    if any(chip in info.chip_name for chip in ["M1", "M2", "M3", "M4"]):
        info.neural_engine_cores = 32 if is_ultra else 16


def _detect_apfs(info: MacOSOptimizationInfo) -> None:
    """Detect APFS filesystem availability."""
    try:
        result = subprocess.run(["diskutil", "info", "/"], capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            info.apfs_enabled = "APFS" in result.stdout
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass


def detect_macos_capabilities() -> MacOSOptimizationInfo:
    """Detect macOS platform capabilities for optimization."""
    info = MacOSOptimizationInfo()

    if platform.system() != "Darwin":
        return info

    info.is_macos = True

    try:
        arch = platform.machine()
        info.is_apple_silicon = arch == "arm64"

        if info.is_apple_silicon:
            _detect_chip_name(info)
            _detect_memory_size(info)
            _detect_performance_cores(info)
            _detect_efficiency_cores(info)
            _detect_metal_and_gpu(info)
            _infer_neural_engine_cores(info)

        _detect_apfs(info)
        info.gcd_available = True
    except Exception as e:
        logger.debug(f"macOS capability detection error: {e}")

    return info


def configure_metal_optimization() -> dict[str, str | bool]:
    """Configure Metal GPU for optimal performance."""
    config: dict[str, str | bool] = {
        "memory_pool_size": "auto",
        "shader_cache_enabled": True,
        "async_compute": True,
        "texture_compression": "astc",
        "command_buffer_reuse": True,
        "mtl_hud": False,
    }

    if os.getenv("METAL_DEBUG", "0") == "1":
        config["mtl_hud"] = True
        os.environ["METAL_DEVICE_WRAPPER_TYPE"] = "1"
        os.environ["METAL_DEBUG_ERROR_MODE"] = "assert"

    logger.info(f"Metal optimization configured: {config}")
    return config


def optimize_unified_memory_usage() -> dict[str, int | bool | float]:
    """Optimize memory usage for Apple Silicon unified memory."""
    info = detect_macos_capabilities()

    if not info.is_apple_silicon:
        return {}

    total_mem_mb = info.unified_memory_gb * 1024
    app_memory_limit_mb = int(total_mem_mb * 0.5)
    gpu_memory_pool_mb = int(total_mem_mb * 0.25)

    config = {
        "app_memory_limit_mb": app_memory_limit_mb,
        "gpu_memory_pool_mb": gpu_memory_pool_mb,
        "use_zero_copy": True,
        "unified_memory": True,
        "memory_pressure_threshold": 0.8,
    }

    logger.info(
        f"Unified memory: {info.unified_memory_gb}GB total, {app_memory_limit_mb}MB app, {gpu_memory_pool_mb}MB GPU"
    )
    return config


def get_optimal_thread_count() -> int:
    """Get optimal thread count for Apple Silicon."""
    info = detect_macos_capabilities()

    if not info.is_apple_silicon:
        import multiprocessing

        return multiprocessing.cpu_count()

    optimal_threads = info.performance_cores * 2
    logger.info(f"Optimal threads: {optimal_threads} (P: {info.performance_cores}, E: {info.efficiency_cores})")
    return optimal_threads


def enable_apfs_optimizations() -> dict[str, bool]:
    """Enable APFS-specific file system optimizations."""
    info = detect_macos_capabilities()

    if not info.apfs_enabled:
        return {}

    config = {
        "use_cloning": True,
        "atomic_save_native": True,
        "fast_directory_sizing": True,
        "enable_compression": False,
    }

    logger.info("APFS optimizations enabled")
    return config


def log_optimization_status() -> None:
    """Log comprehensive macOS optimization status."""
    info = detect_macos_capabilities()

    if not info.is_macos:
        logger.info("Not running on macOS - optimizations disabled")
        return

    logger.info("=" * 60)
    logger.info("macOS Optimization Status")
    logger.info("=" * 60)

    if info.is_apple_silicon:
        logger.info(f"✓ Apple Silicon: {info.chip_name}")
        logger.info(
            f"  Memory: {info.unified_memory_gb}GB | CPU: {info.performance_cores}P+{info.efficiency_cores}E | GPU: {info.gpu_cores} | NPU: {info.neural_engine_cores}"
        )
        logger.info(f"  Metal: {info.metal_feature_set or 'Supported'}")
    else:
        logger.info("✓ Intel Mac detected")

    if info.apfs_enabled:
        logger.info("✓ APFS optimizations enabled")
    if info.gcd_available:
        logger.info("✓ Grand Central Dispatch available")
    logger.info("=" * 60)
