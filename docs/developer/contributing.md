# Developer Guide

**Reading Level**: Grade 4.0 (Elementary)

A guide for people who want to help make AsciiDoc Artisan better.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Code Structure](#code-structure)
3. [How Things Work](#how-things-work)
4. [Making Changes](#making-changes)
5. [Testing Your Changes](#testing-your-changes)
6. [Sending Your Changes](#sending-your-changes)
7. [Repository Cleanup](#repository-cleanup)

## Project Setup

### What You Need

Before you start:
- Python 3.11 or newer
- Git (for getting code)
- A code editor (like VS Code)
- Basic Python skills

### Getting the Code

1. **Fork the project**:
   - Go to github.com/webbwr/AsciiDoctorArtisan
   - Click "Fork" button
   - This makes your own copy

2. **Get your copy**:
```bash
cd ~/github
git clone https://github.com/YOUR-USERNAME/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

3. **Install all**:
```bash
# Install basic parts
pip install -r requirements.txt

# Install dev tools
pip install -r requirements-dev.txt

# Or use Make
make install-dev
```

## Code Structure

### Main Folders

Here's where things live:

```
src/
├── main.py                     # Start here
├── ai_client.py               # Talks to AI
├── document_converter.py       # Changes files
├── performance_profiler.py     # Checks speed
└── asciidoc_artisan/          # Main code
    ├── core/                  # Basic stuff
    │   ├── constants.py       # Fixed numbers
    │   ├── models.py          # Data shapes
    │   ├── settings.py        # User settings
    │   └── file_operations.py # Read/write files
    ├── ui/                    # Windows
    │   ├── main_window.py     # Main window
    │   ├── dialogs.py         # Pop-ups
    │   └── *_manager.py       # Helpers
    ├── workers/               # Background tasks
    │   ├── git_worker.py      # Git stuff
    │   ├── pandoc_worker.py   # Change files
    │   └── preview_worker.py  # Updates view
    ├── git/                   # Git tools
    └── conversion/            # File changes
```

### Important Files

**main.py**:
- Starts the program
- Sets up the window
- Connects all parts

**ui/main_window.py**:
- The main window
- Has the editor
- Has the preview
- Handles menu clicks

**workers/*.py**:
- Run tasks in background
- Don't freeze program
- Send messages when done

**core/settings.py**:
- Saves what you like
- Remembers last file
- Stores window size

## How Things Work

### Starting Up

When you run the program:

1. `main.py` starts
2. Makes the main window
3. Loads settings
4. Opens last file
5. Shows the window

### Typing in Editor

When you type:

1. Text goes in editor
2. Timer waits 350ms
3. Timer starts preview
4. Preview worker makes HTML
5. HTML shows on right

### Saving Files

When you save:

1. Get text from editor
2. Write to temp file first
3. If that works, replace old file
4. Show "saved" message
5. Update window title

### Git Work

When you commit:

1. Get commit message
2. Run git in background
3. Show progress
4. Show done or error
5. Turn buttons back on

## Making Changes

### Code Style

We use these rules:
- **Line length**: 88 max
- **Format**: Black
- **Imports**: Sorted with isort
- **Type hints**: Add to functions
- **Comments**: Explain the "why"

### Before You Code

1. **Make a branch**:
```bash
git checkout -b my-new-feature
```

2. **Make small changes**:
   - Fix one thing at a time
   - Keep commits small
   - Test as you go

3. **Write clear messages**:
```
Good: "Add dark mode to settings"
Bad: "Fixed stuff"
```

### Adding New Features

Say you want to add "word count":

1. **Plan it**:
   - Where does it show? (status bar)
   - When does it update? (when you type)
   - What does it count? (words)

2. **Write the code**:
```python
# In main_window.py

def update_word_count(self):
    """Count words."""
    text = self.editor.toPlainText()
    words = len(text.split())
    self.status_bar.showMessage(f"Words: {words}")
```

3. **Connect it**:
```python
# In __init__

self.editor.textChanged.connect(self.update_word_count)
```

4. **Test it**:
   - Type some words
   - Check the count is right
   - Try empty file
   - Try big file

### Code Format

Before you commit:

```bash
# Format all code
make format

# Or do it by hand
black src/
isort src/
```

### Check Your Code

```bash
# Check for problems
make lint

# Run type checker
mypy src/
```

## Testing Your Changes

### Manual Testing

Always test these:
1. Start the program
2. Make new file
3. Type some text
4. Save the file
5. Close and open again
6. Check preview works
7. Try dark mode
8. Try Git (if in Git folder)

### Test List

- [ ] Program starts
- [ ] Can type
- [ ] Preview updates
- [ ] Can save
- [ ] Can open
- [ ] Dark mode works
- [ ] Keys work
- [ ] Git works
- [ ] Settings save

### Automated Tests

We have two types of automated tests:

**Unit tests** (5,254 tests):
```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_file.py -v

# Check coverage
pytest --cov=asciidoc_artisan --cov-report=html
```

**E2E tests** (3 tests):
```bash
# Run all E2E tests
pytest tests/e2e/ -m e2e -v

# Run without coverage (faster)
pytest tests/e2e/ -v --no-cov
```

**Before sending changes**:
1. All tests must pass: `make test`
2. No lint errors: `make lint`
3. Format code: `make format`

See [Testing Guide](testing.md) for detailed test writing instructions.

### Test on Different Systems

If you can, test on:
- Windows
- Mac
- Linux

Each system acts different!

## Sending Your Changes

### Getting Ready

1. **Make sure it works**:
```bash
make lint
make format
python3 src/main.py
```

2. **Commit your changes**:
```bash
git add .
git commit -m "Add word count"
```

3. **Push to GitHub**:
```bash
git push origin my-new-feature
```

### Making a Pull Request

1. Go to GitHub
2. Click "Pull requests"
3. Click "New pull request"
4. Pick your branch
5. Write what you did:
   - What did you change?
   - Why did you change it?
   - How do you test it?
6. Click "Create pull request"

### Pull Request Template

```markdown
## What This Does

Add word count to status bar

## Why

Users asked for word count

## How to Test

1. Open the program
2. Type some words
3. Look at bottom
4. Should see "Words: X"

## Screenshots

(Add a picture)
```

## Common Tasks

### Adding a Menu Item

1. Find `_create_actions()` in main_window.py
2. Add your action:
```python
self.word_count_act = QAction("Word Count", self)
self.word_count_act.triggered.connect(self.show_word_count)
```

3. Add to menu:
```python
view_menu.addAction(self.word_count_act)
```

### Adding a Dialog

1. Make new class in ui/dialogs.py:
```python
class WordCountDialog(QDialog):
    def __init__(self, word_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Word Count")
        # Add stuff here
```

2. Use it in main_window.py:
```python
def show_word_count(self):
    count = len(self.editor.toPlainText().split())
    dialog = WordCountDialog(count, self)
    dialog.exec()
```

### Adding a Setting

1. Add to Settings in core/models.py:
```python
@dataclass
class Settings:
    show_word_count: bool = True
```

2. Use it:
```python
if self._settings.show_word_count:
    self.update_word_count()
```

## Repository Cleanup

Keep the code clean and organized.

### Before You Commit

Clean up old build files:

```bash
make clean
```

This removes:
- Old Python cache (`__pycache__/`, `*.pyc`)
- Test files (`.pytest_cache`, `.coverage`)
- Build files (`build/`, `dist/`, `*.egg-info`)
- Type check cache (`.mypy_cache`, `.ruff_cache`)

### Automatic Cleanup

Pre-commit hooks clean before push:

```bash
# Install hooks (one time)
pre-commit install --hook-type pre-push

# Now cleanup runs before each git push
```

The hook runs `make clean` for you!

### What to Clean

**Clean these**:
- Build artifacts (`build/`, `dist/`)
- Python bytecode (`*.pyc`, `__pycache__/`)
- Test cache (`.pytest_cache`, `htmlcov/`)
- Type caches (`.mypy_cache`, `.ruff_cache`)

**Keep these**:
- Source code (`src/`, `tests/`)
- Configuration (`.editorconfig`, `.pre-commit-config.yaml`)
- Virtual environment (`venv/`)

### Editor Config

The `.editorconfig` file helps all editors use same style:

- **Spaces**: Use spaces, not tabs (except Makefiles)
- **Python**: 4 spaces per indent
- **YAML/JSON**: 2 spaces per indent
- **Line endings**: Unix style (LF)

Most editors read this file. No setup needed!

## Getting Help

Stuck? Try these:

1. **Read the code**: Look at similar parts
2. **Check issues**: Someone might have asked
3. **Ask questions**: Make a GitHub issue
4. **Read docs**: Check docs/ folder

## Code Review Tips

When your pull request is reviewed:
- Don't take it hard - we all learn!
- Ask questions if unclear
- Make the changes they suggest
- Say thanks!

## Remember

- **Test your changes**: Always check it works
- **Small commits**: One feature at a time
- **Clear messages**: Explain what and why
- **Ask for help**: No question is too small
- **Have fun**: We're making something cool!

## Next Steps

1. Look at "good first issue" tags
2. Fix a small bug
3. Add a simple feature
4. Help with docs

Welcome to the team!
