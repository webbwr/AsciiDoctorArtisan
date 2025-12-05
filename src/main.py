"""
Application entry point for AsciiDoc Artisan.

Configures GPU acceleration, creates the main window, and runs the Qt event loop.
Supports async/await via qasync for non-blocking file operations.
"""

import asyncio
import logging
import os
import platform
import sys
import warnings
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

try:
    import ai_client  # noqa: F401

    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False
    logger.info("AI client not available. AI-enhanced conversion disabled.")


def _setup_gpu_acceleration() -> None:
    """Configure GPU acceleration. Must be called before importing Qt."""
    system = platform.system()

    if system == "Darwin":
        try:
            from asciidoc_artisan.core.macos_optimizer import (
                configure_metal_optimization,
                log_optimization_status,
            )

            configure_metal_optimization()
            log_optimization_status()
            logger.info("macOS Metal GPU acceleration configured with Apple Silicon optimizations")
        except ImportError:
            logger.info("macOS detected - using native Metal GPU acceleration")
    else:
        is_wsl2 = os.environ.get("WSL_DISTRO_NAME") is not None

        if is_wsl2:
            # WSL2 uses DirectX passthrough - use ANGLE instead of desktop OpenGL
            os.environ.setdefault("QT_OPENGL", "angle")
            os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")
            os.environ.setdefault(
                "QTWEBENGINE_CHROMIUM_FLAGS",
                "--enable-gpu-rasterization "
                "--enable-zero-copy "
                "--enable-hardware-overlays "
                "--use-gl=angle "
                "--use-angle=d3d11 "
                "--disable-gpu-driver-bug-workarounds",
            )
            logger.info("WSL2 detected - using ANGLE GL backend via DirectX")
        else:
            os.environ.setdefault("QT_OPENGL", "desktop")
            os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")
            os.environ.setdefault(
                "QTWEBENGINE_CHROMIUM_FLAGS",
                "--enable-gpu-rasterization "
                "--enable-zero-copy "
                "--enable-hardware-overlays "
                "--enable-features=VaapiVideoDecoder,VaapiVideoEncoder "
                "--use-gl=desktop "
                "--disable-gpu-driver-bug-workarounds",
            )

        # NPU acceleration via OpenVINO
        os.environ.setdefault("OPENCV_DNN_BACKEND", "5")
        os.environ.setdefault("OPENCV_DNN_TARGET", "6")
        logger.info("GPU/NPU acceleration configured")


def _create_app() -> Any:
    """Create the QApplication instance."""
    from PySide6.QtWidgets import QApplication

    from asciidoc_artisan.core import APP_NAME

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan")

    if platform.system() == "Windows":
        app.setStyle("windowsvista")
    else:
        app.setStyle("Fusion")

    return app


async def _run_async_app(app: Any) -> None:
    """Run Qt application within asyncio event loop."""
    fut: asyncio.Future[None] = asyncio.Future()
    app.aboutToQuit.connect(lambda: fut.set_result(None))
    await fut


def main() -> None:  # noqa: C901
    """Application entry point."""
    warnings.filterwarnings("ignore", category=SyntaxWarning)

    # GPU setup must happen before Qt import
    _setup_gpu_acceleration()

    # Validate dependencies
    from asciidoc_artisan.core import validate_dependencies

    validator = validate_dependencies()
    logger.info(validator.get_validation_summary())

    if validator.has_critical_issues():
        logger.error("Critical dependencies are missing!")

    # Optional memory profiling
    profiler = None
    if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
        from asciidoc_artisan.core import get_profiler

        profiler = get_profiler()
        profiler.start()
        logger.info("Memory profiling enabled")
        profiler.take_snapshot("startup_begin")

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

    # Show dependency dialogs if needed
    missing_optional = validator.get_missing_optional()
    if len(missing_optional) > 0:
        logger.info(f"Showing dependency information: {len(missing_optional)} optional dependencies missing")
        from asciidoc_artisan.ui.dependency_dialog import show_dependency_summary_message

        show_dependency_summary_message(validator.dependencies, window)

    if validator.has_critical_issues():
        from asciidoc_artisan.ui.dependency_dialog import show_dependency_validation

        can_continue = show_dependency_validation(validator.dependencies, window)
        if not can_continue:
            logger.error("User chose to exit due to missing dependencies")
            sys.exit(1)

    # Apply font settings
    if hasattr(window, "dialog_manager"):
        window.dialog_manager._apply_font_settings()
        logger.info("Font settings applied on startup")

    # Trigger initial preview when worker is ready
    if hasattr(window, "preview_worker") and window.preview_worker:

        def trigger_initial_preview() -> None:
            window.update_preview()
            if profiler:
                profiler.take_snapshot("after_initial_preview")
            logger.info("Initial preview rendered after worker ready")

        window.preview_worker.ready.connect(trigger_initial_preview)
    else:
        window.update_preview()
        if profiler:
            profiler.take_snapshot("after_initial_preview")

    # Run event loop with async support
    try:
        import qasync

        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        logger.info("Using qasync event loop for async/await support")

        with loop:
            loop.run_until_complete(_run_async_app(app))
            exit_code = 0
    except ImportError:
        logger.warning("qasync not available - async file operations disabled")
        exit_code = app.exec()

    # Cleanup
    if profiler:
        profiler.take_snapshot("before_exit")
        stats = profiler.get_statistics()
        logger.info(f"Memory statistics: {stats}")
        profiler.log_top_allocations(10)
        profiler.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
