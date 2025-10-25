# Developer Guide

**Reading Level**: Grade 4.0 (Elementary)

A guide for people who want to help improve AsciiDoc Artisan or understand how it works.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Code Structure](#code-structure)
3. [How Things Work](#how-things-work)
4. [Making Changes](#making-changes)
5. [Testing Your Changes](#testing-your-changes)
6. [Sending Your Changes](#sending-your-changes)

## Project Setup

### What You Need

Before you start coding:
- Python 3.11 or newer
- Git (for getting the code and saving changes)
- A code editor (like VS Code, PyCharm, or any you like)
- Basic Python knowledge

### Getting the Code

1. **Fork the project**:
   - Go to github.com/webbwr/AsciiDoctorArtisan
   - Click "Fork" button (top right)
   - This makes your own copy

2. **Download your copy**:
```bash
cd ~/github
git clone https://github.com/YOUR-USERNAME/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

3. **Install everything**:
```bash
# Install basic parts
pip install -r requirements.txt

# Install developer tools
pip install -r requirements-dev.txt

# Or use Make
make install-dev
```

## Code Structure

### Main Folders

Here's where everything lives:

```
src/
├── main.py                     # Start here - main program
├── ai_client.py               # Talks to AI services
├── document_converter.py       # Changes document types
├── performance_profiler.py     # Checks how fast things run
└── asciidoc_artisan/          # Main code package
    ├── core/                  # Basic stuff all parts need
    │   ├── constants.py       # Numbers and text that don't change
    │   ├── models.py          # Data structures
    │   ├── settings.py        # User settings
    │   └── file_operations.py # Reading and writing files safely
    ├── ui/                    # Windows and buttons
    │   ├── main_window.py     # Main program window
    │   ├── dialogs.py         # Pop-up windows
    │   └── *_manager.py       # Helpers for different parts
    ├── workers/               # Background tasks
    │   ├── git_worker.py      # Git operations
    │   ├── pandoc_worker.py   # Document conversion
    │   └── preview_worker.py  # Updates the preview
    ├── git/                   # Git tools
    └── conversion/            # Document conversion tools
```

### Important Files

**main.py**:
- Starts the program
- Sets up the window
- Connects all the parts

**ui/main_window.py**:
- The main window you see
- Has the editor and preview
- Handles menu clicks

**workers/*.py**:
- Run tasks in the background
- Don't freeze the program
- Send messages when done

**core/settings.py**:
- Saves user preferences
- Remembers last file opened
- Stores window size and position

## How Things Work

### Starting Up

When you run the program:

1. `main.py` starts
2. Creates the main window
3. Loads settings from last time
4. Opens last file (if there was one)
5. Shows the window

### Typing in the Editor

When you type:

1. Text goes in the editor (left side)
2. Timer waits 350ms (in case you type more)
3. Timer triggers preview update
4. Preview worker turns AsciiDoc into HTML
5. HTML shows in preview (right side)

### Saving Files

When you save:

1. Get text from editor
2. Write to a temp file first (for safety)
3. If that works, replace old file
4. Show "saved" message
5. Update window title

### Git Operations

When you commit:

1. Get commit message from you
2. Run git commands in background
3. Show progress message
4. Show success or error
5. Enable buttons again

## Making Changes

### Code Style

We use these rules:
- **Line length**: 88 characters max
- **Formatting**: Black formatter
- **Imports**: Sorted with isort
- **Type hints**: Add them to functions
- **Comments**: Explain the "why", not the "what"

### Before You Code

1. **Create a branch**:
```bash
git checkout -b my-new-feature
```

2. **Make small changes**:
   - Fix one thing at a time
   - Keep commits small
   - Test as you go

3. **Write clear commit messages**:
```
Good: "Add dark mode to settings dialog"
Bad: "Fixed stuff"
```

### Adding a New Feature

Let's say you want to add a "word count" feature:

1. **Plan it out**:
   - Where does it show? (status bar)
   - When does it update? (when you type)
   - What does it count? (words, characters)

2. **Write the code**:
```python
# In main_window.py

def update_word_count(self):
    """Count words in the document."""
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
   - Try very large file

### Code Formatting

Before you commit:

```bash
# Format all code
make format

# Or do it manually
black src/
isort src/
```

### Checking Your Code

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
2. Create new file
3. Type some text
4. Save the file
5. Close and reopen
6. Check preview works
7. Try dark mode
8. Try Git features (if in Git folder)

### Test Checklist

- [ ] Program starts without errors
- [ ] Can type in editor
- [ ] Preview updates
- [ ] Can save file
- [ ] Can open file
- [ ] Dark mode works
- [ ] Keyboard shortcuts work
- [ ] Git commands work
- [ ] Settings save correctly

### Testing on Different Systems

If you can, test on:
- Windows
- Mac
- Linux

Each system might act differently!

## Sending Your Changes

### Getting Ready

1. **Make sure everything works**:
```bash
make lint
make format
python3 src/main.py  # Test it runs
```

2. **Commit your changes**:
```bash
git add .
git commit -m "Add word count feature"
```

3. **Push to GitHub**:
```bash
git push origin my-new-feature
```

### Creating a Pull Request

1. Go to GitHub
2. Click "Pull requests"
3. Click "New pull request"
4. Pick your branch
5. Write a clear description:
   - What did you change?
   - Why did you change it?
   - How do you test it?
6. Click "Create pull request"

### Pull Request Description Template

```markdown
## What This Does

Add word count feature to status bar

## Why

Users asked for a way to see how many words they've written

## How to Test

1. Open the program
2. Type some words
3. Look at bottom of window
4. Should see "Words: X"

## Screenshots

(Add a picture if it helps)
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

1. Create new class in ui/dialogs.py:
```python
class WordCountDialog(QDialog):
    def __init__(self, word_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Word Count")
        # Add widgets here
```

2. Use it in main_window.py:
```python
def show_word_count(self):
    count = len(self.editor.toPlainText().split())
    dialog = WordCountDialog(count, self)
    dialog.exec()
```

### Adding a Setting

1. Add to Settings model in core/models.py:
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

## Getting Help

Stuck? Try these:

1. **Read the code**: Look at similar features
2. **Check issues**: Someone might have asked before
3. **Ask questions**: Create a GitHub issue
4. **Read documentation**: Check docs/ folder

## Code Review Tips

When your pull request is reviewed:
- Don't take it personally - we all learn!
- Ask questions if you don't understand
- Make the changes they suggest
- Say thanks!

## Remember

- **Test your changes**: Always check it works
- **Small commits**: One feature at a time
- **Clear messages**: Explain what and why
- **Ask for help**: No question is too small
- **Have fun**: We're building something cool!

## Next Steps

1. Look at "good first issue" tags on GitHub
2. Fix a small bug
3. Add a simple feature
4. Help improve documentation

Welcome to the team!
