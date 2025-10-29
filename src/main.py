"""
AsciiDoc Artisan - Cross-Platform AsciiDoc Editor
==================================================

Fast desktop editor with live preview, GPU acceleration, and Git integration.
"""

import logging
import os
import platform
import sys
import warnings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check AI client availability (lazy import)
try:
    import ai_client  # noqa: F401
    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False
    logger.info("AI client not available. AI-enhanced conversion disabled.")


def _setup_gpu_acceleration() -> None:
    """Configure Qt GPU/NPU acceleration environment variables."""
    os.environ.setdefault("QT_OPENGL", "desktop")
    os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")
    os.environ.setdefault(
        "QTWEBENGINE_CHROMIUM_FLAGS",
        "--enable-gpu-rasterization --enable-zero-copy --enable-hardware-overlays "
        "--enable-features=VaapiVideoDecoder,VaapiVideoEncoder --use-gl=desktop "
        "--disable-gpu-driver-bug-workarounds",
    )
    # Enable NPU/AI acceleration if available
    os.environ.setdefault("OPENCV_DNN_BACKEND", "5")  # OpenVINO
    os.environ.setdefault("OPENCV_DNN_TARGET", "6")   # NPU
    logger.info("GPU/NPU acceleration configured")


def _create_app():
    """Create and configure QApplication."""
    from PySide6.QtWidgets import QApplication

    from asciidoc_artisan.core import APP_NAME

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan")

    # Platform-specific styling
    app.setStyle("windowsvista" if platform.system() == "Windows" else "Fusion")
    return app


def main() -> None:
    """Main application entry point."""
    warnings.filterwarnings("ignore", category=SyntaxWarning)

    # Setup GPU acceleration before creating QApplication
    _setup_gpu_acceleration()

    # Optional memory profiling
    profiler = None
    if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
        from asciidoc_artisan.core import get_profiler
        profiler = get_profiler()
        profiler.start()
        logger.info("Memory profiling enabled")
        profiler.take_snapshot("startup_begin")

    # Create app and window
    app = _create_app()
    if profiler:
        profiler.take_snapshot("after_app_init")

    from asciidoc_artisan.ui import AsciiDocEditor
    window = AsciiDocEditor()
    if profiler:
        profiler.take_snapshot("after_window_init")

    window.show()
    if profiler:
        profiler.take_snapshot("after_window_show")

    window.update_preview()
    if profiler:
        profiler.take_snapshot("after_initial_preview")

    # Run event loop
    exit_code = app.exec()

    # Log memory stats on exit
    if profiler:
        profiler.take_snapshot("before_exit")
        stats = profiler.get_statistics()
        logger.info(f"Memory statistics: {stats}")
        profiler.log_top_allocations(10)
        profiler.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
