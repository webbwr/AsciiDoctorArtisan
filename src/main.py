"""
AsciiDoc Artisan - Windows-Optimized Version
============================================

Enhanced for Windows with proper window management, dynamic screen sizing,
and improved file navigation.
"""

import logging
import platform
import sys
import warnings

try:
    import ai_client  # noqa: F401

    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info("AI client not available. AI-enhanced conversion disabled.")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import from refactored core module
from PySide6.QtWidgets import (
    QApplication,
)

from asciidoc_artisan.core import (
    APP_NAME,
)

# Import from refactored workers module
# Import from refactored UI module
from asciidoc_artisan.ui import (
    AsciiDocEditor,
)

try:
    import pypandoc

    PANDOC_AVAILABLE = True
except ImportError:
    logger.warning("pypandoc not found. Document conversion limited.")
    pypandoc = None
    PANDOC_AVAILABLE = False


try:
    from document_converter import ensure_pandoc_available, pandoc

    ENHANCED_PANDOC = True
except ImportError:
    logger.warning("Enhanced document converter not available")
    pandoc = None  # type: ignore[assignment]
    ensure_pandoc_available = None  # type: ignore[assignment]
    ENHANCED_PANDOC = False

try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    logger.warning("asciidoc3 not found. Live preview will use plain text.")
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

# ============================================================================
# REFACTORING NOTE: Constants, Settings, GitResult, and file operations
# have been extracted to asciidoc_artisan.core module (Phase 1 of architectural
# refactoring to resolve technical debt per specification line 1197).
# These are now imported above from asciidoc_artisan.core.
# ============================================================================


# ============================================================================
# REFACTORING NOTE: Dialog class (PreferencesDialog) has been extracted to
# asciidoc_artisan.ui.dialogs module (Phase 3 of architectural refactoring to
# resolve technical debt per specification line 1197). This is now imported
# above from asciidoc_artisan.ui.dialogs.
# ============================================================================

# ============================================================================
# REFACTORING NOTE: Worker classes (GitWorker, PandocWorker, PreviewWorker)
# have been extracted to asciidoc_artisan.workers module (Phase 2 of
# architectural refactoring to resolve technical debt per specification line 1197).
# These are now imported above from asciidoc_artisan.workers.
# ============================================================================

# ============================================================================
# REFACTORING NOTE: AsciiDocEditor class has been extracted to
# asciidoc_artisan.ui.main_window module (Phase 4 of architectural
# refactoring to resolve technical debt per specification line 1197).
# The class is now imported above from asciidoc_artisan.ui.
# ============================================================================


def main() -> None:

    warnings.filterwarnings("ignore", category=SyntaxWarning)

    # Enable GPU acceleration for Qt
    # Must be set BEFORE creating QApplication
    import os
    os.environ.setdefault("QT_OPENGL", "desktop")
    os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--enable-gpu-rasterization --enable-zero-copy --enable-hardware-overlays --enable-features=VaapiVideoDecoder,VaapiVideoEncoder --use-gl=desktop --disable-gpu-driver-bug-workarounds")

    # Enable NPU/AI acceleration if available
    os.environ.setdefault("OPENCV_DNN_BACKEND", "5")  # OpenVINO backend
    os.environ.setdefault("OPENCV_DNN_TARGET", "6")  # NPU target

    logger.info("GPU acceleration flags set for Qt")

    # Start memory profiler if enabled (v1.4.1 optimization)
    profiler = None
    if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
        from asciidoc_artisan.core import get_profiler
        profiler = get_profiler()
        profiler.start()
        logger.info("Memory profiling enabled")
        profiler.take_snapshot("startup_begin")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan")

    if platform.system() == "Windows":
        app.setStyle("windowsvista")
    else:
        app.setStyle("Fusion")

    if profiler:
        profiler.take_snapshot("after_app_init")

    window = AsciiDocEditor()

    if profiler:
        profiler.take_snapshot("after_window_init")

    window.show()

    if profiler:
        profiler.take_snapshot("after_window_show")

    window.update_preview()

    if profiler:
        profiler.take_snapshot("after_initial_preview")

    exit_code = app.exec()

    # Log memory statistics on exit
    if profiler:
        profiler.take_snapshot("before_exit")
        stats = profiler.get_statistics()
        logger.info(f"Memory statistics: {stats}")
        profiler.log_top_allocations(10)
        profiler.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
