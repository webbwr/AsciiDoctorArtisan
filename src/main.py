"""
===============================================================================
APPLICATION ENTRY POINT - Where the Program Starts
===============================================================================

FILE PURPOSE:
This is the main.py file - the starting point for the entire application.
When you run "python src/main.py", this file runs first.

WHAT THIS FILE DOES:
1. Sets up the computer's graphics card (GPU) for fast rendering
2. Creates the main application window
3. Starts the program and keeps it running
4. Handles cleanup when you close the application

FOR BEGINNERS:
Think of this file as the "power button" for the app. It turns everything on
in the right order, then waits for you to use the program. When you quit,
it turns everything off safely.

KEY CONCEPTS:
- Entry Point: The first code that runs when you start the program
- GPU Acceleration: Using your graphics card to make things faster
- Event Loop: Keeps the program running and responding to user actions
- Logging: Recording what the program does (like a diary)
"""

import asyncio  # For async/await support
import logging  # For recording what the program does
import os  # For reading/setting environment variables
import platform  # For detecting Windows/Linux/Mac
import sys  # For command-line arguments and exit codes
import warnings  # For suppressing non-critical warnings
from typing import Any  # Type hints

# === LOGGING SETUP ===
# Configure logging - this creates a "diary" of what the program does
# Level INFO means we record important events, but not every tiny detail
logging.basicConfig(
    level=logging.INFO,  # Record INFO, WARNING, and ERROR messages
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Time, source, level, message
)
logger = logging.getLogger(__name__)  # Get a logger for this file

# === CHECK FOR OPTIONAL AI CLIENT ===
# Try to import the AI client library (for smart document conversion)
# If it's not installed, that's okay - the app still works without it
try:
    import ai_client  # noqa: F401  # Optional library for AI features

    AI_CLIENT_AVAILABLE = True  # Flag: AI features are available
except ImportError:
    # ImportError means the library isn't installed - that's fine!
    AI_CLIENT_AVAILABLE = False  # Flag: AI features disabled
    logger.info("AI client not available. AI-enhanced conversion disabled.")


def _setup_gpu_acceleration() -> None:
    """
    Configure GPU (Graphics Card) Acceleration.

    WHY WE DO THIS:
    Your computer has a powerful graphics card (GPU) that can render things
    much faster than the main processor (CPU). This function tells Qt (our UI
    framework) to use the GPU for drawing the preview window.

    RESULT:
    - 10-50x faster preview rendering
    - 70-90% less CPU usage
    - Smoother scrolling and zooming

    HOW IT WORKS:
    We set "environment variables" - special settings the operating system reads
    before starting the program. These tell Qt to enable GPU features.
    """
    # Tell Qt to use desktop OpenGL (the graphics API for 3D acceleration)
    os.environ.setdefault("QT_OPENGL", "desktop")

    # Configure X11 OpenGL integration (Linux/WSL specific)
    os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")

    # Pass special flags to Chromium (the web engine used for preview)
    # These flags enable various GPU acceleration features
    os.environ.setdefault(
        "QTWEBENGINE_CHROMIUM_FLAGS",
        "--enable-gpu-rasterization "  # Use GPU to draw shapes/text
        "--enable-zero-copy "  # Share memory between GPU and CPU (faster)
        "--enable-hardware-overlays "  # Use GPU for video playback
        "--enable-features=VaapiVideoDecoder,VaapiVideoEncoder "  # Hardware video
        "--use-gl=desktop "  # Use desktop OpenGL
        "--disable-gpu-driver-bug-workarounds",  # Assume modern drivers
    )

    # === OPTIONAL: NPU (Neural Processing Unit) ACCELERATION ===
    # Some modern CPUs (Intel 11th gen+) have built-in AI chips called NPUs
    # OpenVINO can use these for even faster AI operations
    os.environ.setdefault("OPENCV_DNN_BACKEND", "5")  # Backend 5 = OpenVINO
    os.environ.setdefault("OPENCV_DNN_TARGET", "6")  # Target 6 = NPU

    logger.info("GPU/NPU acceleration configured")


def _create_app() -> Any:
    """
    Create the Main Application Object.

    WHAT IS QApplication?:
    In Qt (our UI framework), QApplication is the main controller for the entire
    program. There can only be ONE QApplication per program. It handles:
    - Creating windows
    - Processing mouse clicks and keyboard input
    - Managing the event loop (keeps program running)

    WHY IMPORT HERE?:
    We import PySide6 inside the function (not at the top of the file) because:
    1. GPU environment variables must be set BEFORE importing Qt
    2. This is called "lazy importing" - only import when needed

    RETURNS:
    The QApplication object that controls the entire program
    """
    # Import Qt's main application class
    from PySide6.QtWidgets import QApplication

    # Import our app's name from the constants file
    from asciidoc_artisan.core import APP_NAME

    # Create the application object
    # sys.argv contains command-line arguments (like "python main.py --debug")
    app = QApplication(sys.argv)

    # Set the application name (shows in taskbar, window titles, etc.)
    app.setApplicationName(APP_NAME)

    # Set organization name (used for settings file location)
    app.setOrganizationName("AsciiDoc Artisan")

    # === PLATFORM-SPECIFIC STYLING ===
    # Different operating systems have different look-and-feel
    # - Windows: Use "windowsvista" style (native Windows look)
    # - Linux/Mac: Use "Fusion" style (cross-platform modern look)
    if platform.system() == "Windows":
        app.setStyle("windowsvista")  # Native Windows appearance
    else:
        app.setStyle("Fusion")  # Modern cross-platform style

    return app  # Return the application object


async def _run_async_app(app: Any) -> None:
    """
    Run Qt application asynchronously.

    This helper function allows the Qt event loop to run within asyncio,
    enabling async/await for file operations and other async tasks.

    Args:
        app: QApplication instance

    v1.7.0: Added for Enhanced Async I/O (Task 4)
    """
    # Create a future that completes when the app quits
    fut: asyncio.Future[None] = asyncio.Future()

    # Connect app's aboutToQuit signal to resolve the future
    app.aboutToQuit.connect(lambda: fut.set_result(None))

    # Wait for app to quit
    await fut


def main() -> None:
    """
    Main Entry Point - The First Function That Runs.

    STARTUP SEQUENCE:
    1. Ignore harmless warnings
    2. Enable GPU acceleration
    3. (Optional) Start memory profiler
    4. Create application object
    5. Create main window
    6. Show window on screen
    7. Render initial preview
    8. Start event loop (wait for user actions) with async support
    9. When user quits: clean up and exit

    FOR DEVELOPERS:
    This function follows the "setup, run, cleanup" pattern:
    - Setup: Prepare everything before showing the window
    - Run: Keep the program running (event loop) with async/await support
    - Cleanup: Save data and release resources before exit

    v1.7.0: Enhanced with qasync for async/await file operations
    """
    # === STEP 1: IGNORE HARMLESS WARNINGS ===
    # Some Python warnings are not helpful (like SyntaxWarning from dependencies)
    # We filter them out to avoid cluttering the log
    warnings.filterwarnings("ignore", category=SyntaxWarning)

    # === STEP 2: SETUP GPU ACCELERATION ===
    # IMPORTANT: This MUST happen before creating QApplication
    # Once Qt is imported, it's too late to change GPU settings
    _setup_gpu_acceleration()

    # === STEP 3: OPTIONAL MEMORY PROFILING ===
    # For developers: Track memory usage to find leaks
    # Enable by setting environment variable: ASCIIDOC_ARTISAN_PROFILE_MEMORY=1
    profiler = None
    if os.environ.get("ASCIIDOC_ARTISAN_PROFILE_MEMORY"):
        from asciidoc_artisan.core import get_profiler

        profiler = get_profiler()  # Get the memory profiler
        profiler.start()  # Start tracking memory allocations
        logger.info("Memory profiling enabled")
        profiler.take_snapshot("startup_begin")  # Snapshot 1: At startup

    # === STEP 4: CREATE APPLICATION OBJECT ===
    app = _create_app()
    if profiler:
        profiler.take_snapshot("after_app_init")  # Snapshot 2: After Qt initialized

    # === STEP 5: CREATE MAIN WINDOW ===
    # Import here (lazy import) to ensure GPU settings are applied first
    from asciidoc_artisan.ui import AsciiDocEditor

    window = AsciiDocEditor()  # Create the main window (doesn't show yet)
    if profiler:
        profiler.take_snapshot("after_window_init")  # Snapshot 3: After window created

    # === STEP 6: SHOW WINDOW ON SCREEN ===
    window.show()  # Make window visible to user
    if profiler:
        profiler.take_snapshot("after_window_show")  # Snapshot 4: After window shown

    # === STEP 7: RENDER INITIAL PREVIEW ===
    # Generate the first preview so user sees content immediately
    window.update_preview()
    if profiler:
        profiler.take_snapshot(
            "after_initial_preview"
        )  # Snapshot 5: After first render

    # === STEP 8: START EVENT LOOP (WITH ASYNC SUPPORT) ===
    # This is where the program "runs" - it processes user actions in a loop:
    # - Wait for user to click a button, type text, etc.
    # - Process that action
    # - Update the screen
    # - Repeat until user quits
    # The loop only exits when the user closes the window
    #
    # v1.7.0: We use qasync to bridge Qt's event loop with Python's asyncio,
    # allowing async/await for non-blocking file operations
    try:
        import qasync

        # Create qasync event loop that bridges Qt and asyncio
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)

        logger.info("Using qasync event loop for async/await support")

        # Run event loop with async support
        # Note: We use a context manager to ensure proper cleanup
        with loop:
            # Start Qt's event loop within the asyncio loop
            loop.run_until_complete(_run_async_app(app))
            exit_code = 0  # Success

    except ImportError:
        # Fallback to standard Qt event loop if qasync not available
        logger.warning("qasync not available - async file operations disabled")
        exit_code = app.exec()  # Run standard event loop (blocks until quit)

    # === STEP 9: CLEANUP AND EXIT ===
    # User has quit - log memory stats if profiling was enabled
    if profiler:
        profiler.take_snapshot("before_exit")  # Final snapshot before exit
        stats = profiler.get_statistics()
        logger.info(f"Memory statistics: {stats}")
        profiler.log_top_allocations(10)  # Show top 10 memory users
        profiler.stop()  # Stop profiling

    # Exit the program with the exit code from Qt
    # Exit code 0 = success, non-zero = error
    sys.exit(exit_code)


# === PYTHON ENTRY POINT ===
# This special if-statement checks: "Am I being run directly?"
# - If you run "python main.py": This is True, so main() runs
# - If someone imports this file: This is False, so main() doesn't run
if __name__ == "__main__":
    main()  # Start the application!
