# Claude Code Configuration

This directory contains Claude Code configuration for minimal verbosity with detailed status line.

## Files

### `settings.json`
Project-level settings that configure Claude Code behavior:
- **Minimal Verbosity**: Concise, action-oriented responses
- **Detailed Status Line**: Rich context from `statusline.sh`
- **Structured Output**: Bullet points, checkmarks, no fluff

### `statusline.sh`
Bash script that generates comprehensive project context:
- Git status (branch, changes, ahead/behind)
- Python environment (version, venv status)
- Architecture (Apple Silicon optimization status)
- QA metrics (tests, coverage, type checking, linting)
- System information (macOS version, timestamp)

### `skills/`
Claude Code skills directory (auto-generated)

## Usage

### Automatic (Recommended)
Settings are automatically loaded when Claude Code runs in this project directory.

### Manual Override
To explicitly use these settings:
```bash
claude --settings .claude/settings.json
```

### Test Status Line
Run the statusline script directly:
```bash
.claude/statusline.sh
```

## Configuration Philosophy

**Minimal Verbosity Mode:**
- Skip confirmations and pleasantries
- Show results, not descriptions
- Use imperative statements ("Fixed X", not "I will fix X")
- Omit obvious observations
- Focus on what changed

**Detailed Status Line:**
- All project context visible at a glance
- No need to repeat state in responses
- Real-time Git, QA, and environment status
- Platform-specific optimizations shown
- Color-coded for quick scanning

## Example Output

**Status Line:**
```
┏━━ AsciiDocArtisan v2.0.0
├─ Git: main │ ±3 │ ↑1 ↓0
├─ Env: Python 3.13.3 │ venv:✓ │ Apple Silicon (opt:✓)
├─ QA : Tests:82 (95%) │ mypy:✓ │ ruff:✓
└─ OS : macOS 25.2 │ 12:30:45
```

**Claude Response (Minimal):**
```
✓ Fixed type errors (3 files)
✓ Committed: 'fix: Add strict type annotations'
✓ Pushed to origin/main
```

**vs Old Verbose Style:**
```
I'll help you fix the type errors. First, let me check the files...
I found 3 type errors that need to be fixed. Let me fix them now...
Great! I've successfully fixed all the type errors. Now I'll commit...
Perfect! Everything is committed and pushed. You're all set!
```

## Customization

### Modify Verbosity
Edit `settings.json` → `systemPromptAdditions` to adjust response style.

### Extend Status Line
Edit `statusline.sh` to add/remove information:
- Line 40-42: Git information
- Line 45-46: Python environment
- Line 49-50: Test statistics
- Line 53-54: Type checking
- Line 57-58: Linting

### Change Status Line Format
The format uses ANSI color codes:
- `${BOLD}${BLUE}` - Headers
- `${GREEN}` - Success indicators
- `${YELLOW}` - Warnings/changes
- `${DIM}` - Secondary information

## Maintenance

The statusline script caches some information for performance:
- Test stats: From `htmlcov/index.html`
- Type checking: Live check (slower)
- Linting: Live check (slower)

Run tests before expecting accurate test/coverage stats:
```bash
make test  # Generates htmlcov/index.html
```

## Architecture

```
.claude/
├── settings.json          # Claude Code configuration
├── statusline.sh          # Status line generator script
├── README.md             # This file
└── skills/               # Claude Code skills
    └── ...
```

## Version

- Created: 2025-11-09
- Claude Code Version: Compatible with claude-cli 1.x+
- Project: AsciiDoc Artisan v2.0.0

## See Also

- [Claude Code Settings Docs](https://code.claude.com/docs/en/settings)
- [Project CLAUDE.md](../CLAUDE.md) - Main development documentation
