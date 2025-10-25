# AsciiDoc Artisan - Deep Performance & Resource Optimization Plan

**Version:** 1.0  
**Date:** October 25, 2025  
**Baseline:** Post-refactoring (1,647-line main_window)  
**Target:** 2-3x performance improvement, 30-50% resource reduction  
**Timeline:** 4-6 weeks (8-12 sprints)

---

## Executive Summary

This plan outlines a comprehensive performance optimization strategy for AsciiDoc Artisan, targeting:
- **Startup time reduction:** 50-70% faster
- **Memory footprint:** 30-40% reduction
- **Preview rendering:** 3-5x faster for large documents
- **CPU usage:** 40-60% reduction during editing
- **File I/O:** 2-3x faster save/load operations

All optimizations will maintain backward compatibility and current functionality.

---

## 📊 Current Performance Baseline

### Measured Metrics (to be established)
```python
# Startup Performance
- Cold start time:          TBD ms
- Warm start time:          TBD ms
- First paint time:         TBD ms
- Time to interactive:      TBD ms

# Memory Usage
- Base memory (empty doc):  TBD MB
- Memory (1MB document):    TBD MB
- Memory (10MB document):   TBD MB
- Memory leak rate:         TBD MB/hour

# Runtime Performance
- Preview render (100 lines):   TBD ms
- Preview render (1000 lines):  TBD ms
- Preview render (10000 lines): TBD ms
- Text input latency:           TBD ms
- Scroll performance:           TBD fps

# File Operations
- Load 1MB file:           TBD ms
- Save 1MB file:           TBD ms
- Export to PDF (1MB):     TBD ms
- Git commit (10 files):   TBD ms

# CPU Usage
- Idle:                    TBD %
- Active typing:           TBD %
- Preview rendering:       TBD %
- Background workers:      TBD %
```

---

## Phase 1: Profiling & Measurement (Week 1)

### Objectives
- Establish accurate performance baselines
- Identify performance bottlenecks
- Create automated performance regression tests
- Set up continuous performance monitoring

### Tasks

#### 1.1 Performance Profiling Infrastructure
```python
# Create: tests/performance/test_performance_baseline.py

import time
import psutil
import pytest
from pathlib import Path

class PerformanceProfiler:
    """Track and measure application performance."""
    
    def __init__(self):
        self.metrics = {}
        self.process = psutil.Process()
    
    @contextmanager
    def measure_time(self, operation: str):
        """Measure operation execution time."""
        start = time.perf_counter()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        
        yield
        
        end = time.perf_counter()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        self.metrics[operation] = {
            'time_ms': (end - start) * 1000,
            'memory_mb': end_memory,
            'memory_delta_mb': end_memory - start_memory,
        }
    
    def measure_startup(self, app):
        """Measure application startup time."""
        # Cold start
        # Warm start
        # First paint
        # Time to interactive
    
    def measure_preview_performance(self, editor, document_size):
        """Measure preview rendering performance."""
        # Small doc (100 lines)
        # Medium doc (1000 lines)
        # Large doc (10000 lines)
    
    def measure_memory_usage(self, app):
        """Measure memory footprint."""
        # Base memory
        # Memory growth over time
        # Memory leaks
    
    def generate_report(self) -> dict:
        """Generate performance report."""
        return {
            'timestamp': time.time(),
            'metrics': self.metrics,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'platform': platform.system(),
            }
        }

# Automated performance tests
@pytest.mark.performance
def test_startup_performance(profiler):
    """Ensure startup meets performance targets."""
    with profiler.measure_time('startup'):
        app = create_app()
    
    assert profiler.metrics['startup']['time_ms'] < 1000  # < 1 second

@pytest.mark.performance
def test_preview_performance(profiler, editor):
    """Ensure preview rendering meets targets."""
    document = generate_test_document(1000)  # 1000 lines
    
    with profiler.measure_time('preview_1000_lines'):
        render_preview(document)
    
    assert profiler.metrics['preview_1000_lines']['time_ms'] < 100  # < 100ms
```

#### 1.2 CPU Profiling
```bash
# Profile application with cProfile
python -m cProfile -o profile.stats src/main.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats

# Profile memory with memory_profiler
pip install memory_profiler
python -m memory_profiler src/main.py
```

#### 1.3 Identify Bottlenecks
- [ ] Profile startup sequence
- [ ] Profile preview rendering pipeline
- [ ] Profile file I/O operations
- [ ] Profile worker thread performance
- [ ] Profile signal/slot connections
- [ ] Profile widget creation/destruction

**Deliverables:**
- Performance baseline report
- Bottleneck identification document
- Automated performance test suite
- CI/CD integration for performance tracking

---

## Phase 2: Memory Optimization (Weeks 2-3)

### Objectives
- Reduce memory footprint by 30-40%
- Eliminate memory leaks
- Implement efficient caching strategies
- Optimize data structures

### 2.1 Object Lifecycle Management

#### Current Issues
```python
# Issue: Objects not properly cleaned up
class MainWindow:
    def __init__(self):
        self._temp_dir = tempfile.TemporaryDirectory()  # Never cleaned up properly
        self.preview_cache = {}  # Unbounded cache
        self.undo_stack = []  # No size limit
```

#### Optimization
```python
class MainWindow:
    def __init__(self):
        # Use context managers for resources
        self._resource_manager = ResourceManager()
        
        # Implement bounded caches
        from functools import lru_cache
        self.preview_cache = LRUCache(maxsize=100)
        
        # Limit undo stack
        self.undo_stack = deque(maxlen=100)
    
    def cleanup(self):
        """Explicit cleanup for better control."""
        self._resource_manager.cleanup_all()
        self.preview_cache.clear()
        self.undo_stack.clear()

class ResourceManager:
    """Centralized resource management."""
    
    def __init__(self):
        self._resources = []
        self._temp_dirs = []
    
    def register_temp_dir(self) -> Path:
        """Create and track temporary directory."""
        temp_dir = tempfile.TemporaryDirectory()
        self._temp_dirs.append(temp_dir)
        return Path(temp_dir.name)
    
    def cleanup_all(self):
        """Clean up all registered resources."""
        for temp_dir in self._temp_dirs:
            try:
                temp_dir.cleanup()
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir: {e}")
        self._temp_dirs.clear()
```

#### Tasks
- [ ] Implement ResourceManager for centralized cleanup
- [ ] Add `__del__` methods to critical classes
- [ ] Use weak references where appropriate
- [ ] Implement proper signal disconnection
- [ ] Add memory leak detection tests

### 2.2 Efficient Data Structures

#### Current Issues
```python
# Inefficient: Storing full document in multiple places
class Editor:
    self.content = text  # Full text
    self.undo_stack = [full_text_1, full_text_2, ...]  # Redundant copies
```

#### Optimization
```python
# Use rope data structure for efficient text operations
from pyropes import Rope

class OptimizedEditor:
    def __init__(self):
        self.content = Rope()  # Efficient for large text
        
        # Store only deltas in undo stack
        self.undo_stack = deque(maxlen=100)  # Store (position, old_text, new_text)
    
    def apply_edit(self, position: int, old_text: str, new_text: str):
        """Apply edit and store delta."""
        self.undo_stack.append((position, old_text, new_text))
        self.content = self.content.delete(position, len(old_text))
        self.content = self.content.insert(position, new_text)
```

#### Tasks
- [ ] Replace string concatenation with Rope or similar
- [ ] Implement delta-based undo/redo
- [ ] Use generators instead of lists where possible
- [ ] Optimize CSS caching strategy
- [ ] Use `__slots__` for frequently created objects

### 2.3 Lazy Loading & On-Demand Initialization

```python
class LazyMainWindow:
    """Lazy initialization of expensive components."""
    
    def __init__(self):
        self._git_handler = None
        self._export_manager = None
        self._preview_cache = None
    
    @property
    def git_handler(self):
        """Lazy load git handler only when needed."""
        if self._git_handler is None:
            self._git_handler = GitHandler(self)
        return self._git_handler
    
    @property
    def export_manager(self):
        """Lazy load export manager only when needed."""
        if self._export_manager is None:
            self._export_manager = ExportManager(self)
        return self._export_manager
```

#### Tasks
- [ ] Identify candidates for lazy initialization
- [ ] Implement lazy properties for heavy components
- [ ] Defer worker thread creation until needed
- [ ] Load plugins/extensions on-demand

**Deliverables:**
- 30-40% memory reduction
- Zero memory leaks
- Bounded cache implementations
- Lazy loading for expensive components

---

## Phase 3: CPU & Rendering Optimization (Weeks 3-4)

### Objectives
- Reduce CPU usage during idle/typing by 40-60%
- Optimize preview rendering by 3-5x
- Minimize UI thread blocking
- Implement efficient debouncing/throttling

### 3.1 Preview Rendering Optimization

#### Current Issues
```python
# Issue: Full re-render on every keystroke
def _on_text_changed(self):
    self.preview_timer.start(500)  # Debounced but still full render

def update_preview(self):
    full_text = self.editor.toPlainText()  # Get all text
    html = convert_to_html(full_text)  # Convert all
    self.preview.setHtml(html)  # Replace all
```

#### Optimization Strategy

##### 3.1.1 Incremental Rendering
```python
class IncrementalPreviewRenderer:
    """Render only changed portions of document."""
    
    def __init__(self):
        self.document_cache = {}  # Cache rendered blocks
        self.last_text = ""
        self.block_size = 50  # Lines per block
    
    def render_incremental(self, new_text: str) -> str:
        """Render only changed blocks."""
        # Find changed blocks
        old_blocks = self._split_blocks(self.last_text)
        new_blocks = self._split_blocks(new_text)
        
        changed_blocks = self._diff_blocks(old_blocks, new_blocks)
        
        # Render only changed blocks
        for block_id in changed_blocks:
            self.document_cache[block_id] = self._render_block(new_blocks[block_id])
        
        # Assemble final HTML from cache
        html = self._assemble_html(self.document_cache)
        
        self.last_text = new_text
        return html
    
    def _split_blocks(self, text: str) -> dict:
        """Split document into renderable blocks."""
        lines = text.split('\n')
        blocks = {}
        
        for i in range(0, len(lines), self.block_size):
            block_id = i // self.block_size
            blocks[block_id] = '\n'.join(lines[i:i+self.block_size])
        
        return blocks
    
    def _diff_blocks(self, old_blocks, new_blocks):
        """Find which blocks changed."""
        changed = set()
        
        for block_id in set(old_blocks.keys()) | set(new_blocks.keys()):
            if old_blocks.get(block_id) != new_blocks.get(block_id):
                changed.add(block_id)
        
        return changed
```

##### 3.1.2 Virtual Scrolling for Large Documents
```python
class VirtualScrollPreview:
    """Render only visible portion of document."""
    
    def __init__(self, viewport_height: int):
        self.viewport_height = viewport_height
        self.render_buffer = 2  # Render 2x viewport
        self.visible_range = (0, 0)
    
    def update_visible_range(self, scroll_position: int):
        """Update which portion of document is visible."""
        # Calculate visible line range
        start_line = scroll_position // self.line_height
        end_line = start_line + (self.viewport_height // self.line_height)
        
        # Add buffer
        start_line = max(0, start_line - self.render_buffer)
        end_line = end_line + self.render_buffer
        
        if (start_line, end_line) != self.visible_range:
            self.visible_range = (start_line, end_line)
            self.render_visible_portion()
    
    def render_visible_portion(self):
        """Render only the visible portion."""
        start, end = self.visible_range
        visible_text = self.get_lines(start, end)
        html = self.convert_to_html(visible_text)
        self.update_preview_html(html, start, end)
```

##### 3.1.3 Web Worker for Preview Rendering
```python
# Use QWebEngineScript to run rendering in web worker
class WebWorkerRenderer:
    """Offload rendering to web worker."""
    
    def __init__(self, preview: QWebEngineView):
        self.preview = preview
        self._setup_web_worker()
    
    def _setup_web_worker(self):
        """Inject web worker script."""
        worker_script = QWebEngineScript()
        worker_script.setSourceCode("""
            // Create web worker for rendering
            const renderWorker = new Worker('render-worker.js');
            
            renderWorker.onmessage = function(e) {
                // Update DOM with rendered HTML
                document.getElementById('content').innerHTML = e.data.html;
            };
            
            window.renderAsciiDoc = function(text) {
                renderWorker.postMessage({
                    action: 'render',
                    text: text
                });
            };
        """)
        
        self.preview.page().scripts().insert(worker_script)
    
    def render_async(self, text: str):
        """Send text to web worker for rendering."""
        self.preview.page().runJavaScript(
            f"window.renderAsciiDoc({json.dumps(text)});"
        )
```

#### Tasks
- [ ] Implement incremental rendering
- [ ] Add virtual scrolling for large documents
- [ ] Use web workers for heavy rendering
- [ ] Cache rendered HTML blocks
- [ ] Optimize AsciiDoc→HTML conversion

### 3.2 Adaptive Debouncing

```python
class AdaptiveDebouncer:
    """Adaptive debouncing based on document size and system load."""
    
    def __init__(self):
        self.base_delay = 200  # ms
        self.max_delay = 2000  # ms
        self.last_trigger = 0
        self.system_monitor = SystemMonitor()
    
    def get_delay(self, document_size: int) -> int:
        """Calculate optimal delay based on conditions."""
        # Base delay increases with document size
        size_factor = min(document_size / 10000, 5.0)
        
        # Increase delay if CPU is busy
        cpu_factor = self.system_monitor.get_cpu_usage() / 100
        
        # Increase delay if memory is tight
        memory_factor = 1.0
        if self.system_monitor.get_memory_pressure() > 0.8:
            memory_factor = 2.0
        
        delay = self.base_delay * size_factor * (1 + cpu_factor) * memory_factor
        return min(int(delay), self.max_delay)

class SystemMonitor:
    """Monitor system resources."""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)
    
    def get_memory_pressure(self) -> float:
        """Get memory pressure (0.0-1.0)."""
        vm = psutil.virtual_memory()
        return vm.percent / 100.0
    
    def should_throttle(self) -> bool:
        """Check if we should throttle operations."""
        return (
            self.get_cpu_usage() > 80 or
            self.get_memory_pressure() > 0.9
        )
```

#### Tasks
- [ ] Implement adaptive debouncing
- [ ] Add system resource monitoring
- [ ] Throttle operations under load
- [ ] Implement request coalescing

### 3.3 Worker Thread Optimization

```python
class OptimizedWorkerPool:
    """Efficient worker thread pool."""
    
    def __init__(self, max_workers: int = None):
        if max_workers is None:
            max_workers = max(2, psutil.cpu_count() - 1)
        
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(max_workers)
        self.pending_tasks = {}
    
    def submit_task(self, task_id: str, runnable: QRunnable):
        """Submit task, canceling duplicate tasks."""
        # Cancel pending duplicate task
        if task_id in self.pending_tasks:
            old_task = self.pending_tasks[task_id]
            old_task.cancel()
        
        self.pending_tasks[task_id] = runnable
        self.pool.start(runnable)
    
    def cancel_all(self, task_type: str):
        """Cancel all tasks of a specific type."""
        for task_id, task in list(self.pending_tasks.items()):
            if task_id.startswith(task_type):
                task.cancel()
                del self.pending_tasks[task_id]

# Cancelable runnable
class CancelableRunnable(QRunnable):
    """Runnable that can be canceled."""
    
    def __init__(self):
        super().__init__()
        self._is_canceled = False
    
    def cancel(self):
        """Cancel this task."""
        self._is_canceled = True
    
    def run(self):
        """Run task with cancellation checks."""
        for chunk in self.process_chunks():
            if self._is_canceled:
                return  # Exit early
            
            # Process chunk
            result = self.process_chunk(chunk)
            
            if self._is_canceled:
                return
        
        self.emit_result()
```

#### Tasks
- [ ] Implement cancelable runnables
- [ ] Add worker pool management
- [ ] Implement task prioritization
- [ ] Add progress reporting for long tasks

**Deliverables:**
- 3-5x faster preview rendering
- 40-60% CPU reduction during editing
- Adaptive performance based on system load
- Virtual scrolling for large documents

---

## Phase 4: I/O Optimization (Week 4)

### Objectives
- 2-3x faster file loading/saving
- Asynchronous I/O for large files
- Efficient Git operations
- Optimized export pipeline

### 4.1 Asynchronous File I/O

```python
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

class AsyncFileHandler:
    """Asynchronous file operations."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def load_file_async(self, file_path: Path) -> str:
        """Load file asynchronously."""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        return content
    
    async def save_file_async(self, file_path: Path, content: str):
        """Save file asynchronously."""
        # Write to temp file first
        temp_path = file_path.with_suffix('.tmp')
        
        async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        # Atomic rename
        await asyncio.to_thread(temp_path.rename, file_path)
    
    async def load_large_file_streaming(self, file_path: Path) -> AsyncIterator[str]:
        """Stream large file in chunks."""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            chunk_size = 8192  # 8KB chunks
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

# Integration with Qt
class QtAsyncBridge:
    """Bridge between async and Qt signals."""
    
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def _run_loop(self):
        """Run event loop in background thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def run_async(self, coro, callback):
        """Run coroutine and call callback with result."""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.add_done_callback(lambda f: callback(f.result()))
```

#### Tasks
- [ ] Implement async file I/O
- [ ] Add progress reporting for large files
- [ ] Use memory-mapped files for huge documents
- [ ] Implement streaming for exports

### 4.2 File Format Optimization

```python
# Compress large documents
import zlib
import pickle

class OptimizedDocumentStorage:
    """Optimized document storage format."""
    
    @staticmethod
    def save_compressed(file_path: Path, data: dict):
        """Save with compression."""
        # Pickle data
        serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Compress
        compressed = zlib.compress(serialized, level=6)
        
        # Write atomically
        temp_path = file_path.with_suffix('.tmp')
        temp_path.write_bytes(compressed)
        temp_path.rename(file_path)
    
    @staticmethod
    def load_compressed(file_path: Path) -> dict:
        """Load compressed document."""
        compressed = file_path.read_bytes()
        serialized = zlib.decompress(compressed)
        return pickle.loads(serialized)
```

#### Tasks
- [ ] Add compression for large documents
- [ ] Optimize JSON serialization
- [ ] Use binary formats where appropriate
- [ ] Implement delta saving (save only changes)

### 4.3 Git Operation Optimization

```python
class OptimizedGitHandler:
    """Optimized Git operations."""
    
    def __init__(self):
        self.git_cache = {}
        self.last_status_check = 0
        self.status_cache_duration = 5  # seconds
    
    async def get_status_cached(self) -> dict:
        """Get git status with caching."""
        now = time.time()
        
        if now - self.last_status_check < self.status_cache_duration:
            return self.git_cache.get('status', {})
        
        # Run git status asynchronously
        status = await self._run_git_async(['status', '--porcelain'])
        
        self.git_cache['status'] = status
        self.last_status_check = now
        
        return status
    
    async def batch_add_commit_push(self, files: list, message: str):
        """Batch git operations."""
        # Combine operations to reduce overhead
        commands = [
            ['add'] + files,
            ['commit', '-m', message],
            ['push']
        ]
        
        # Run in parallel where possible
        await self._run_git_batch(commands)
```

#### Tasks
- [ ] Cache git status/info
- [ ] Batch git operations
- [ ] Use libgit2 for better performance
- [ ] Implement background git refresh

**Deliverables:**
- 2-3x faster file operations
- Async I/O for large files
- Optimized git operations
- Compressed document storage

---

## Phase 5: Qt-Specific Optimizations (Week 5)

### Objectives
- Optimize widget creation/destruction
- Minimize signal/slot overhead
- Efficient event handling
- Reduce paint events

### 5.1 Widget Optimization

```python
class OptimizedMainWindow(QMainWindow):
    """Optimized Qt widget patterns."""
    
    def __init__(self):
        super().__init__()
        
        # Defer widget updates until shown
        self.setAttribute(Qt.WA_DontShowOnScreen, True)
        self._setup_ui()
        self.setAttribute(Qt.WA_DontShowOnScreen, False)
        
        # Use widget attributes for performance
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Reduce unnecessary repaints
        self.setUpdatesEnabled(False)
        self._populate_data()
        self.setUpdatesEnabled(True)
    
    def batch_updates(self, updates: callable):
        """Batch widget updates to reduce repaints."""
        self.setUpdatesEnabled(False)
        try:
            updates()
        finally:
            self.setUpdatesEnabled(True)
            self.update()  # Single repaint
```

#### Tasks
- [ ] Use widget attributes for performance
- [ ] Batch widget updates
- [ ] Minimize widget hierarchy depth
- [ ] Use QWidget instead of QMainWindow where possible

### 5.2 Signal/Slot Optimization

```python
# Current: String-based connections (slow)
button.clicked.connect(self.on_button_clicked)

# Optimized: Direct connections
button.clicked.connect(self.on_button_clicked, Qt.DirectConnection)

# Avoid auto-connections
class MyWidget(QWidget):
    # Don't use @pyqtSlot with string signatures
    @pyqtSlot()  # Better
    def on_button_clicked(self):
        pass

# Use signal coalescing
class CoalescedSignal:
    """Coalesce rapid signals into batches."""
    
    def __init__(self, signal, delay_ms: int = 100):
        self.signal = signal
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._emit)
        self.delay_ms = delay_ms
        self.pending_args = None
    
    def emit(self, *args):
        """Coalesce signals."""
        self.pending_args = args
        self.timer.start(self.delay_ms)
    
    def _emit(self):
        """Emit coalesced signal."""
        if self.pending_args:
            self.signal.emit(*self.pending_args)
            self.pending_args = None
```

#### Tasks
- [ ] Use direct signal connections
- [ ] Implement signal coalescing
- [ ] Disconnect signals when not needed
- [ ] Reduce signal/slot overhead

### 5.3 Event Handling Optimization

```python
class OptimizedEventHandling(QWidget):
    """Optimized event handling patterns."""
    
    def __init__(self):
        super().__init__()
        
        # Install event filter only when needed
        self.event_filter = CustomEventFilter()
        
    def enable_event_filtering(self):
        """Enable event filtering."""
        if not self.event_filter:
            self.event_filter = CustomEventFilter()
        self.installEventFilter(self.event_filter)
    
    def disable_event_filtering(self):
        """Disable event filtering."""
        if self.event_filter:
            self.removeEventFilter(self.event_filter)
    
    def event(self, event: QEvent) -> bool:
        """Optimized event handling."""
        # Fast path for common events
        if event.type() == QEvent.Paint:
            return self.handle_paint_fast(event)
        
        # Ignore unnecessary events
        if event.type() in (QEvent.ToolTip, QEvent.HoverMove):
            return True  # Ignore
        
        return super().event(event)
```

#### Tasks
- [ ] Optimize event filters
- [ ] Minimize paint events
- [ ] Use fast paths for common events
- [ ] Reduce event propagation

**Deliverables:**
- Faster widget creation/destruction
- Reduced signal/slot overhead
- Optimized event handling
- Fewer paint events

---

## Phase 6: Startup Optimization (Week 5-6)

### Objectives
- 50-70% faster startup time
- Lazy module loading
- Deferred initialization
- Splash screen with progress

### 6.1 Import Optimization

```python
# Current: Import everything upfront
import PySide6.QtCore
import PySide6.QtWidgets
import PySide6.QtGui
# ... many more imports

# Optimized: Lazy imports
class LazyImporter:
    """Lazy import modules on first use."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._module = None
    
    def __getattr__(self, name):
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return getattr(self._module, name)

# Usage
QtWidgets = LazyImporter('PySide6.QtWidgets')
QtCore = LazyImporter('PySide6.QtCore')

# Or use __import__
def get_pandoc():
    """Lazy import pandoc."""
    global pypandoc
    if 'pypandoc' not in globals():
        import pypandoc as _pypandoc
        pypandoc = _pypandoc
    return pypandoc
```

#### Tasks
- [ ] Implement lazy module imports
- [ ] Defer optional dependency loading
- [ ] Profile import times
- [ ] Remove unused imports

### 6.2 Startup Sequence Optimization

```python
class OptimizedStartup:
    """Optimized application startup sequence."""
    
    def __init__(self):
        self.splash = None
        self.progress = 0
    
    def start_with_splash(self):
        """Start application with splash screen."""
        # Create splash screen (fast)
        self.splash = self._create_splash()
        self.splash.show()
        
        # Process events to show splash
        QApplication.processEvents()
        
        # Initialize in stages
        self._init_stage_1()  # Critical components only
        self.update_splash("Loading UI...", 30)
        
        self._init_stage_2()  # UI components
        self.update_splash("Loading handlers...", 60)
        
        self._init_stage_3()  # Handlers and workers
        self.update_splash("Finalizing...", 90)
        
        self._init_stage_4()  # Nice-to-have features
        self.update_splash("Ready!", 100)
        
        # Show main window
        self.main_window.show()
        self.splash.finish(self.main_window)
    
    def _init_stage_1(self):
        """Critical initialization only."""
        # Settings
        # Core services
        # Minimal UI
    
    def _init_stage_2(self):
        """UI initialization."""
        # Create widgets
        # Setup layout
    
    def _init_stage_3(self):
        """Handler initialization."""
        # File handler
        # Preview handler
        # Export handler
    
    def _init_stage_4(self):
        """Optional features."""
        # Git integration
        # Plugins
        # AI features
```

#### Tasks
- [ ] Add splash screen with progress
- [ ] Stage initialization sequence
- [ ] Defer non-critical initialization
- [ ] Show window ASAP

### 6.3 Settings Loading Optimization

```python
class FastSettingsLoader:
    """Optimized settings loading."""
    
    def __init__(self):
        self.settings_cache = {}
        self.use_cache = True
    
    def load_settings_fast(self) -> dict:
        """Load settings with caching."""
        # Check cache first
        cache_file = self.get_cache_path()
        if cache_file.exists() and self.is_cache_valid(cache_file):
            return self.load_from_cache(cache_file)
        
        # Load from source
        settings = self.load_from_source()
        
        # Update cache
        self.save_to_cache(cache_file, settings)
        
        return settings
    
    def is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache is still valid."""
        # Check age
        age = time.time() - cache_file.stat().st_mtime
        if age > 3600:  # 1 hour
            return False
        
        # Check if source changed
        source_file = self.get_settings_path()
        if source_file.stat().st_mtime > cache_file.stat().st_mtime:
            return False
        
        return True
    
    def load_from_cache(self, cache_file: Path) -> dict:
        """Load from binary cache (fast)."""
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    def save_to_cache(self, cache_file: Path, settings: dict):
        """Save to binary cache."""
        with open(cache_file, 'wb') as f:
            pickle.dump(settings, f, protocol=pickle.HIGHEST_PROTOCOL)
```

#### Tasks
- [ ] Cache parsed settings
- [ ] Use binary format for cache
- [ ] Validate cache freshness
- [ ] Load settings asynchronously

**Deliverables:**
- 50-70% faster startup
- Splash screen with progress
- Lazy module loading
- Cached settings loading

---

## Phase 7: Build & Packaging Optimization (Week 6)

### Objectives
- Smaller distribution size
- Faster installation
- Optimized Python bytecode
- Bundled dependencies

### 7.1 Python Optimization

```bash
# Compile Python to optimized bytecode
python -O -m compileall -b src/

# Use PyPy for better performance (optional)
pypy3 -m pip install -r requirements.txt
pypy3 src/main.py

# Profile-guided optimization
python -m cProfile -o profile.stats src/main.py
python -m pstats profile.stats
```

#### Tasks
- [ ] Compile to optimized bytecode (.pyo)
- [ ] Remove unused dependencies
- [ ] Use minimal dependency versions
- [ ] Consider PyPy for deployment

### 7.2 Asset Optimization

```bash
# Optimize images
optipng images/*.png
jpegoptim images/*.jpg

# Minify CSS
cssnano styles.css -o styles.min.css

# Compress resources
tar -czf resources.tar.gz resources/
```

#### Tasks
- [ ] Optimize image assets
- [ ] Minify CSS/JavaScript
- [ ] Compress resource files
- [ ] Remove unused assets

### 7.3 Distribution Optimization

```python
# setup.py optimizations
setup(
    name='asciidoc_artisan',
    # ... other settings
    
    # Optimize installation
    zip_safe=True,
    include_package_data=False,  # Only include what's needed
    
    # Exclude unnecessary files
    exclude_package_data={
        '': ['*.pyc', '*.pyo', '__pycache__', '*.so'],
    },
    
    # Use compiled extensions where possible
    ext_modules=[
        Extension('fast_renderer', ['src/fast_renderer.c']),
    ],
)
```

#### Tasks
- [ ] Optimize package structure
- [ ] Use compiled extensions
- [ ] Create minimal distribution
- [ ] Optimize installer

**Deliverables:**
- 30-50% smaller distribution
- Faster installation
- Optimized bytecode
- Efficient packaging

---

## Phase 8: Monitoring & Continuous Optimization (Ongoing)

### Objectives
- Real-time performance monitoring
- Automated performance regression detection
- User telemetry (opt-in)
- Continuous improvement

### 8.1 Performance Monitoring

```python
class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'memory_mb': 500,
            'cpu_percent': 80,
            'render_time_ms': 100,
        }
    
    def record_metric(self, name: str, value: float):
        """Record performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'timestamp': time.time(),
        })
        
        # Check threshold
        if name in self.thresholds:
            if value > self.thresholds[name]:
                self.alert_threshold_exceeded(name, value)
    
    def alert_threshold_exceeded(self, name: str, value: float):
        """Alert when threshold exceeded."""
        logger.warning(
            f"Performance threshold exceeded: {name}={value} "
            f"(threshold: {self.thresholds[name]})"
        )
    
    def get_statistics(self) -> dict:
        """Get performance statistics."""
        stats = {}
        for name, values in self.metrics.items():
            recent = [v['value'] for v in values[-100:]]  # Last 100
            stats[name] = {
                'mean': sum(recent) / len(recent),
                'min': min(recent),
                'max': max(recent),
                'current': recent[-1] if recent else 0,
            }
        return stats
```

### 8.2 Regression Testing

```python
# Automated performance regression tests
@pytest.mark.performance
def test_no_performance_regression(baseline_metrics):
    """Ensure no performance regression."""
    current_metrics = measure_current_performance()
    
    # Check each metric
    for metric, current_value in current_metrics.items():
        baseline_value = baseline_metrics[metric]
        
        # Allow 10% regression tolerance
        tolerance = baseline_value * 0.10
        
        assert current_value <= baseline_value + tolerance, (
            f"Performance regression detected in {metric}: "
            f"{current_value} > {baseline_value} (baseline)"
        )
```

### 8.3 User Telemetry (Opt-in)

```python
class TelemetryCollector:
    """Collect anonymous usage telemetry (opt-in)."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.session_id = str(uuid.uuid4())
    
    def record_event(self, event_type: str, data: dict):
        """Record telemetry event."""
        if not self.enabled:
            return
        
        event = {
            'session_id': self.session_id,
            'timestamp': time.time(),
            'event_type': event_type,
            'data': data,
        }
        
        # Send asynchronously to server
        self.send_async(event)
    
    def collect_system_info(self) -> dict:
        """Collect system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'platform': platform.system(),
            'python_version': platform.python_version(),
        }
```

**Deliverables:**
- Real-time performance monitoring
- Automated regression detection
- Opt-in user telemetry
- Performance dashboard

---

## Implementation Timeline

### Week 1: Profiling & Baseline
- [ ] Setup profiling infrastructure
- [ ] Establish performance baselines
- [ ] Create automated performance tests
- [ ] Identify bottlenecks

### Weeks 2-3: Memory Optimization
- [ ] Implement ResourceManager
- [ ] Add bounded caches
- [ ] Optimize data structures
- [ ] Implement lazy loading

### Weeks 3-4: CPU & Rendering
- [ ] Incremental preview rendering
- [ ] Virtual scrolling
- [ ] Adaptive debouncing
- [ ] Worker pool optimization

### Week 4: I/O Optimization
- [ ] Async file operations
- [ ] Git operation caching
- [ ] Compressed storage
- [ ] Streaming for large files

### Week 5: Qt & Startup
- [ ] Widget optimization
- [ ] Signal/slot efficiency
- [ ] Lazy imports
- [ ] Splash screen

### Week 6: Build & Package
- [ ] Optimized bytecode
- [ ] Asset optimization
- [ ] Minimal distribution
- [ ] Performance monitoring

---

## Success Metrics

### Performance Targets
| Metric | Baseline | Target | Stretch Goal |
|--------|----------|--------|--------------|
| Startup time | TBD ms | -50% | -70% |
| Memory (1MB doc) | TBD MB | -30% | -40% |
| Preview (1000 lines) | TBD ms | -60% | -80% |
| CPU (idle) | TBD % | -40% | -60% |
| File save (1MB) | TBD ms | -50% | -67% |
| Distribution size | TBD MB | -30% | -50% |

### Quality Gates
- ✅ Zero performance regressions
- ✅ All tests passing
- ✅ No memory leaks
- ✅ No functionality loss
- ✅ User-facing metrics improved

---

## Risk Mitigation

### Risks
1. **Performance vs. Features** - May need to compromise features
   - Mitigation: Make optimizations optional/configurable
   
2. **Compatibility** - Qt version dependencies
   - Mitigation: Test across Qt versions
   
3. **Complexity** - Optimizations add complexity
   - Mitigation: Extensive documentation and tests

4. **User Impact** - Changes may affect workflow
   - Mitigation: Beta testing and gradual rollout

### Rollback Plan
- Keep feature flags for all optimizations
- Maintain performance baseline metrics
- Easy rollback via configuration
- Gradual deployment to users

---

## Conclusion

This optimization plan provides a comprehensive, phased approach to achieving 2-3x performance improvement while maintaining code quality and functionality. Each phase builds on the previous one, with clear deliverables and success metrics.

**Key Principles:**
- Measure first, optimize second
- No premature optimization
- Maintain backward compatibility
- Test extensively
- Document thoroughly

**Expected Outcome:**
- 50-70% faster startup
- 30-40% less memory usage
- 3-5x faster preview rendering
- 40-60% lower CPU usage
- Significantly improved user experience

---

**Status:** ✅ PLAN READY FOR REVIEW  
**Next Step:** Begin Phase 1 (Profiling & Baseline)  
**Owner:** Development Team  
**Timeline:** 6 weeks (12 sprints)

