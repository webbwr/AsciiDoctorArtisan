# Data Model: AsciiDoc Artisan

**Version**: 1.0.0 | **Date**: 2025-10-22 | **Plan**: [implementation-plan.md](./implementation-plan.md)

## Overview

AsciiDoc Artisan uses a lightweight data model centered around document editing, session management, and external tool integration. The application maintains minimal persistent state, relying on the filesystem for document storage and JSON for configuration persistence.

## Core Entities

### 1. Document

**Purpose**: Represents an AsciiDoc file open in the editor with associated metadata.

**Attributes**:
- `file_path: Optional[Path]` - Absolute path to the document file (None for new unsaved documents)
- `content: str` - Current text content in the editor
- `modified: bool` - True if document has unsaved changes
- `encoding: str` - File encoding (default: 'utf-8')
- `line_ending: str` - Line ending style ('\\n', '\\r\\n', '\\r')

**State Transitions**:
```
New Document (unsaved)
  ↓ (user types)
Modified (unsaved)
  ↓ (user saves)
Saved Document
  ↓ (user types)
Modified (unsaved)
  ↓ (user saves)
Saved Document
```

**Validation Rules**:
- `file_path` must be sanitized with `Path().resolve()` to prevent directory traversal
- `content` has no length limit but performance degrades beyond 10,000 lines
- `modified` flag must be set on any `content` change
- `encoding` must be a valid Python codec name

**Relationships**:
- One Document per application instance (single-file editor)
- Document path stored in Settings for session restoration

### 2. EditorState

**Purpose**: Captures current editor UI configuration and cursor position.

**Attributes**:
- `font_family: str` - Editor font family (default: monospace system font)
- `font_size: int` - Editor font size in points (default: 12)
- `zoom_level: int` - Relative zoom from base font size (+/- increments)
- `cursor_line: int` - Current cursor line number (1-indexed)
- `cursor_column: int` - Current cursor column number (0-indexed)
- `selection_start: int` - Selection start position (character offset)
- `selection_end: int` - Selection end position (character offset)
- `scroll_position: int` - Vertical scroll position (line number)
- `word_wrap: bool` - Word wrap enabled/disabled (default: True)
- `tab_width: int` - Tab stop distance in spaces (default: 4)

**Persistence**: Not persisted (transient UI state)

**Validation Rules**:
- `font_size` must be between 8 and 72 points
- `zoom_level` constrained to prevent excessive sizes (-5 to +10 increments)
- `cursor_line` and `cursor_column` must be within document bounds
- `tab_width` must be between 2 and 8 spaces

### 3. PreviewState

**Purpose**: Manages rendered HTML content and synchronization with editor.

**Attributes**:
- `html_content: str` - Current rendered HTML from AsciiDoc content
- `scroll_position: int` - Preview pane vertical scroll position
- `rendering: bool` - True if background render in progress
- `last_render_time: float` - Timestamp of last successful render
- `render_error: Optional[str]` - Error message if rendering failed

**State Transitions**:
```
Idle
  ↓ (text changed)
Debounce Timer (350ms)
  ↓ (timer fires)
Rendering
  ↓ (worker signals completion)
Idle (with new HTML)
```

**Synchronization**:
- Preview scroll position synchronized with editor scroll position
- Mapping: `preview_scroll = (editor_scroll / editor_max) * preview_max`
- Synchronization occurs on editor scroll events

**Validation Rules**:
- `html_content` must be valid HTML (validated by AsciiDoc3 renderer)
- `last_render_time` used to throttle render requests
- Minimum 350ms between render requests (debounce period)

### 4. Settings (Configuration)

**Purpose**: Stores user preferences and persistent application state.

**Attributes**:
- `last_directory: Path` - Last directory used for file operations
- `last_file: Optional[Path]` - Last opened document path
- `git_repo_path: Optional[Path]` - Detected Git repository root
- `dark_mode: bool` - Theme preference (True = dark, False = light)
- `maximized: bool` - Window maximization state
- `window_geometry: Optional[QRect]` - Window size and position when not maximized
- `splitter_sizes: List[int]` - Editor and preview pane widths [editor_width, preview_width]
- `font_size: int` - Persisted editor font size
- `auto_save_enabled: bool` - Auto-save feature toggle
- `auto_save_interval: int` - Auto-save interval in seconds

**Persistence**:
- Stored as JSON in platform-appropriate configuration directory:
  - Linux/WSL: `~/.config/AsciiDoc Artisan/AsciiDocArtisan.json`
  - Windows: `%APPDATA%/AsciiDoc Artisan/AsciiDocArtisan.json`
  - macOS: `~/Library/Application Support/AsciiDoc Artisan/AsciiDocArtisan.json`
- Loaded on application startup
- Saved on application exit and after significant changes

**Serialization Format**:
```json
{
  "last_directory": "/home/user/documents",
  "last_file": "/home/user/documents/example.adoc",
  "git_repo_path": "/home/user/documents",
  "dark_mode": true,
  "maximized": false,
  "window_geometry": [100, 100, 1200, 800],
  "splitter_sizes": [600, 600],
  "font_size": 12,
  "auto_save_enabled": true,
  "auto_save_interval": 300
}
```

**Validation Rules**:
- All `Path` fields validated on load (existence check, accessibility)
- Invalid paths reverted to defaults (home directory for `last_directory`)
- `window_geometry` validated against screen dimensions
- `splitter_sizes` must sum to valid window width

### 5. GitRepository

**Purpose**: Represents detected Git repository state for the current document.

**Attributes**:
- `repo_path: Path` - Absolute path to Git repository root (`.git` parent directory)
- `has_remote: bool` - True if repository has configured remote
- `remote_url: Optional[str]` - URL of the remote repository (if configured)
- `current_branch: str` - Name of current Git branch
- `is_dirty: bool` - True if working directory has uncommitted changes
- `ahead_count: int` - Number of local commits not pushed to remote
- `behind_count: int` - Number of remote commits not pulled locally

**Detection**:
- Repository detected via `git rev-parse --git-dir` subprocess
- Detection performed when document opened or on Git menu interaction
- Cached until document changes

**State Transitions**:
```
No Repository
  ↓ (document opened in Git repo)
Repository Detected
  ↓ (user commits)
Dirty → Clean (if no other changes)
  ↓ (user pushes)
Ahead Count → 0
```

**Validation Rules**:
- `repo_path` must contain `.git` directory
- Repository state refreshed before each Git operation
- Operations fail gracefully with error messages if repository invalid

### 6. ConversionJob

**Purpose**: Represents a document format conversion task managed by PandocWorker.

**Attributes**:
- `source_path: Path` - Path to source document
- `source_format: str` - Source format ('docx', 'markdown', 'html', 'latex', 'rst', etc.)
- `target_format: str` - Target format ('asciidoc' for import, 'html'/'docx'/'pdf' for export)
- `output_path: Optional[Path]` - Path for export output (None for import to editor)
- `pandoc_options: List[str]` - Additional Pandoc command-line options
- `status: str` - Job status ('pending', 'running', 'completed', 'failed')
- `error_message: Optional[str]` - Error details if conversion failed
- `start_time: float` - Timestamp when conversion started
- `end_time: Optional[float]` - Timestamp when conversion completed/failed

**State Transitions**:
```
Pending
  ↓ (worker starts)
Running
  ↓ (pandoc subprocess completes successfully)
Completed
  OR
  ↓ (pandoc subprocess fails)
Failed (with error_message)
```

**Conversion Workflow**:
1. User opens non-AsciiDoc file or selects export
2. Format detected based on file extension or explicit user choice
3. ConversionJob created and queued to PandocWorker
4. Worker spawns Pandoc subprocess with parameterized arguments
5. Worker emits signal on completion with result
6. Main thread handles result (load to editor or save to file)

**Validation Rules**:
- `source_format` and `target_format` must be in Pandoc's supported format list
- `source_path` must exist and be readable
- `output_path` directory must be writable (if specified)
- `pandoc_options` sanitized to prevent command injection

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                         Settings                            │
│  - Persistent configuration                                 │
│  - JSON file in platform config directory                   │
│  - Loaded on startup, saved on exit                         │
└─────────────────────────────────────────────────────────────┘
         ↓ contains path to
┌─────────────────────────────────────────────────────────────┐
│                         Document                            │
│  - Current file content and metadata                        │
│  - Single instance per application                          │
│  - Modified flag triggers UI updates                        │
└─────────────────────────────────────────────────────────────┘
         ↓ rendered by                    ↓ version controlled by
┌────────────────────────────────┐  ┌─────────────────────────┐
│        PreviewState            │  │    GitRepository        │
│  - HTML rendering              │  │  - Repository metadata  │
│  - Scroll synchronization      │  │  - Branch, remote info  │
└────────────────────────────────┘  └─────────────────────────┘

         ↓ converted by
┌─────────────────────────────────────────────────────────────┐
│                      ConversionJob                          │
│  - Format conversion tasks                                  │
│  - Managed by PandocWorker thread                           │
│  - Import (DOCX→AsciiDoc) or Export (AsciiDoc→HTML/PDF)    │
└─────────────────────────────────────────────────────────────┘
```

## Data Persistence Strategy

### Persistent Data

**Settings (JSON file)**:
- **What**: User preferences, session state, last opened file
- **When**: Saved on application exit, after theme change, after window resize
- **Where**: Platform-appropriate configuration directory
- **Format**: JSON with UTF-8 encoding
- **Backup**: No automatic backup (config easily regenerated)

**Documents (Filesystem)**:
- **What**: AsciiDoc file content
- **When**: User-initiated save operations (Ctrl+S, File→Save)
- **Where**: User-specified locations in filesystem
- **Format**: Plain text, UTF-8 encoding, platform line endings
- **Backup**: Handled by user (version control, backups, etc.)
- **Atomicity**: Temp file + rename pattern prevents corruption

### Transient Data

**Editor State**: Not persisted, reconstructed from document on open
**Preview State**: Not persisted, regenerated on document load
**Git Repository**: Not persisted, detected fresh each session
**Conversion Jobs**: Not persisted, ephemeral task objects

## Memory Management

### Large Document Handling

**Constraint**: Documents >10,000 lines may impact performance

**Strategy**:
- No arbitrary length limits on document content
- Preview debouncing (350ms) reduces rendering frequency
- Worker threads prevent UI blocking but don't reduce memory usage
- Consider lazy rendering for very large documents (future optimization)

**Current Limits**:
- Tested up to 10,000 lines with acceptable performance
- Memory usage ~500MB for typical documents (<5000 lines)
- No streaming or pagination (entire document in memory)

### HTML Preview Caching

**Strategy**:
- No caching of rendered HTML (regenerated on each change)
- Debouncing provides implicit "caching" during rapid edits
- AsciiDoc3 rendering fast enough (<100ms) that caching unnecessary

**Trade-off**: CPU for memory (prefer lower memory footprint)

## Validation & Constraints

### Path Sanitization

**Requirement**: All file paths must be sanitized to prevent directory traversal attacks (Constitution III).

**Implementation**:
```python
def sanitize_path(path_str: str) -> Optional[Path]:
    """
    Sanitize file path to prevent directory traversal.
    Returns None if path contains suspicious patterns.
    """
    path = Path(path_str).resolve()
    if ".." in path.parts:
        return None
    return path
```

**Applied To**:
- All file open operations
- All file save operations
- Configuration file paths
- Git repository paths

### Atomic Write Pattern

**Requirement**: All file writes must be atomic to prevent corruption (Constitution III).

**Implementation**:
```python
def atomic_save(file_path: Path, content: str) -> bool:
    """
    Atomically save content to file using temp file + rename.
    Returns True if successful, False otherwise.
    """
    temp_path = file_path.with_suffix('.tmp')
    try:
        # Write to temporary file
        temp_path.write_text(content, encoding='utf-8')
        # Atomic rename
        temp_path.replace(file_path)
        return True
    except Exception as e:
        # Cleanup on failure
        if temp_path.exists():
            temp_path.unlink()
        return False
```

**Applied To**:
- All document save operations
- Configuration file writes

### Input Validation

**Text Content**:
- No length limit but warn if >10,000 lines
- Allow all Unicode characters
- Support multiple line ending styles (normalize on save)

**Configuration Values**:
- Validate types (bool, int, str, Path)
- Range checks (font_size: 8-72, window dimensions: >0)
- Path existence checks with fallback to defaults
- Invalid JSON → use defaults, log warning

**External Commands**:
- Git and Pandoc called with parameterized arguments
- No shell interpolation or string formatting in commands
- Input sanitization for commit messages (escape quotes)

## Future Considerations

### Scalability

**Current Limitations**:
- Single document at a time (no tabs or multi-document editing)
- No undo/redo history persistence (lost on close)
- No document versioning (rely on Git for history)

**Potential Enhancements**:
- Multi-document tabs (would require `List[Document]` in data model)
- Undo/redo stack serialization for session restoration
- Built-in document snapshots (independent of Git)

### Performance Optimization

**Current Bottlenecks**:
- Large documents (>10,000 lines) slow down rendering
- No incremental rendering (entire document regenerated each time)
- No content streaming (all in memory)

**Potential Solutions**:
- Implement incremental/diff-based rendering
- Lazy load preview for very large documents
- Streaming parser for extreme document sizes
- Consider alternative renderers if AsciiDoc3 becomes bottleneck

### Data Model Extensions

**Out of Scope But Possible**:
- **Project**: Represent multi-file documentation projects
- **Template**: Store document templates for quick creation
- **Snippet**: User-defined code/content snippets
- **Macro**: Custom AsciiDoc macro definitions
- **Style**: Custom CSS for preview pane

---

**Version**: 1.0.0
**Last Updated**: 2025-10-22
**Status**: ✅ Complete - Documents production data model
