# AsciiDoc Artisan

**Version 1.9.1** | November 2025

A simple program. It helps you write papers. It is very fast.

## What It Does

This program does many things:
- Shows your work as you type
- Finds and changes words (new!)
- Saves your work with Git
- Works with GitHub
- Opens Word files
- Opens PDF files
- Opens Markdown files
- Opens HTML files
- Saves to all those types
- Changes file types for you
- Works on all computers
- Uses your graphics card (GPU) for speed
- Works with AI to help you
- Chat with AI about your work

The GPU makes it 10-50x faster. That means much faster than before.

AI chat helps you in 4 ways:
- Ask about your paper
- Learn AsciiDoc rules
- Get help with writing
- Fix your work

All AI works on your computer. No cloud needed.

## What You Need

You need these programs first:
- **Python 3.14** - Makes it run
- **Pandoc** - Changes file types
- **wkhtmltopdf** - Makes PDF files

You might want these too:
- **Git** - Saves work online (not required)
- **GitHub CLI** - Work with GitHub (not required)
- **Ollama** - AI help (not required)
- **GPU drivers** - For speed (not required)

## Install It

### Easy Way

We have scripts. They do it all for you.

**Mac or Linux:**
```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Windows:**
```powershell
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
.\Install-AsciiDocArtisan.ps1
```

The script does this:
- Gets Python parts
- Gets Pandoc
- Checks Git
- Tests it

### Install By Hand

If you want to do it yourself:

1. Get Python parts:
```bash
pip install -r requirements.txt
```

2. Get Pandoc and PDF tool:
   - **Linux**: Type `sudo apt install pandoc wkhtmltopdf`
   - **Mac**: Type `brew install pandoc wkhtmltopdf`
   - **Windows**: Get from pandoc.org and wkhtmltopdf.org

## Use It

### Start It

**Best way (fast):**
```bash
./run.sh
```
Or use Make:
```bash
make run
```

**Other ways:**
```bash
python3 -OO src/main.py  # Fast mode
python3 src/main.py      # Normal mode
```

On Windows:
```bash
python -OO src\main.py
```

The `-OO` flag makes it faster. It removes doc text. It uses less memory.

### Fast Keys

| Press | What It Does |
|-------|--------------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Q | Close |
| Ctrl+F | Find text |
| Ctrl+H | Find and replace text |
| F3 | Find next |
| Shift+F3 | Find before |
| F7 | Turn spell check on or off |
| F11 | Dark mode |
| Ctrl++ | Make text big |
| Ctrl+- | Make text small |

### Open Files

**You can open these:**
- AsciiDoc files (.adoc)
- Markdown files (.md)
- Word files (.docx)
- Web files (.html)
- PDF files (.pdf)

All files open fast. PDF files open 3 to 5 times faster than before.

**How to open a file:**
1. Click `File` then click `Open`
2. Pick your file
3. Click the Open button

The program changes it to AsciiDoc for you.

### Save Files

**To save your work:**
1. Click `File` then click `Save`
2. Type a name for your file
3. Click the Save button

**To save as a different type:**
1. Click `File` then click `Save As`
2. Pick what type you want:
   - AsciiDoc (.adoc)
   - Markdown (.md)
   - Word (.docx)
   - PDF (.pdf)
   - Web page (.html)
3. Type a name for your file
4. Click the Save button

The program changes it for you. No wait time.

### Find and Replace

New in v1.8!

You can find words in your work. You can change them too.

**To find words:**
1. Press `Ctrl+F`
2. Type what you want to find
3. It shows all matches in yellow
4. Click `Next` to go to each one
5. Click `Previous` to go back

The bar shows how many it found (like "5 of 23").

**To change words:**
1. Press `Ctrl+H`
2. Type what you want to find
3. Type what you want instead
4. Click `Replace` to change one at a time
5. Click `Replace All` to change them all

When you click `Replace All`, it asks you first. This keeps you safe.

**Match case:**
- Check the box to match big and small letters
- Uncheck to match all letters the same

Press `Esc` to close the find bar.

### Spell Check

New in v1.8!

The app can check your words. It shows red lines under wrong words.

**To use spell check:**
1. It works by itself when you type
2. Wrong words get red lines under them
3. Right-click on a red word to see fixes
4. Pick the right word from the list

**To turn spell check on or off:**
- Press `F7` key
- Or click `Tools` then click `Toggle Spell Check`

**When you see a red line:**
1. Right-click the word
2. See a list of correct words
3. Click one to fix it
4. Or click `Add to Dictionary` to save the word
5. Or click `Ignore` to skip it this time

The spell check looks at all your words. It works while you type. It finds words that are not right.

### Use Git

If you are in a Git folder, you can use Git.

**Pull** means get new work from the web:
- Click `Git` then click `Pull`

**Commit** means save your work:
1. Click `Git` then click `Commit`
2. Type what you did
3. Click OK

**Push** means send work to the web:
- Click `Git` then click `Push`

## GPU Speed

New in v1.4!

This app uses your graphics card. This makes it very fast.

What you get:
- Preview is 10 to 50 times faster
- Uses 70% to 90% less CPU
- Finds your GPU by itself
- Works with NVIDIA cards
- Works with AMD cards
- Works with Intel cards
- Still works if no GPU found

**What GPUs work:**
- NVIDIA (with CUDA, OpenCL, or Vulkan)
- AMD (with ROCm, OpenCL, or Vulkan)
- Intel (with OpenCL or Vulkan)
- Intel NPU (with OpenVINO)

No setup needed. The app finds your card. It uses it by itself.

**Check if GPU works:**

The app shows this at start:
```
[INFO] GPU detected: NVIDIA GeForce RTX 4060 Laptop GPU
[INFO] Compute capabilities: cuda, opencl, vulkan
[INFO] Using GPU for preview
```

## AI Help

New in v1.2!

The app can use AI. This makes file changes better.

**What AI does:**
- Makes smarter file changes
- Keeps your format better
- Knows what code blocks are
- Knows what tables are
- Works better with complex files

**Where does AI run?**

AI runs on your own computer. Your files never leave your machine. This keeps your work safe.

**What AI programs work:**
- Ollama (we use this)
- Models: phi3, llama2, mistral

### Turn On AI

**Step 1: Get Ollama**

Visit ollama.com. Follow the steps for your computer.

Or type these:

For Mac:
```bash
brew install ollama
```

For Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

For Windows: Get the installer from ollama.com

**Step 2: Get an AI model**

Type this:
```bash
ollama pull gnokit/improve-grammer
```

This gets a small, fast AI model. Good for most work.

Other choices:
```bash
ollama pull llama2        # Better but slower
ollama pull mistral       # Middle choice
ollama pull codellama     # Good for code files
```

**Step 3: Turn it on**

1. Open the app
2. Click **Tools**
3. Click **AI Status**
4. Click **Settings**
5. Check the "Enable Ollama AI" box
6. Pick your model from the list
7. Click "Save"

**Step 4: Check it works**

Look at the status bar. It should say: `AI: gnokit/improve-grammer`

Try to change a file type. The AI will do it for you.

**Note:** If Ollama is not running, the app uses Pandoc instead. The app still works.

## The Preview

The right side shows your work as you type.

What it does:
- Updates when you stop typing
- Moves as you write
- Shows bold text
- Shows lists
- Shows titles
- Scrolls at 60 frames per second

With GPU, this is instant. No wait time.

## Where Settings Save

The app saves your settings here:
- **Linux**: `~/.config/AsciiDocArtisan/`
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`

## Fix Problems

### Can't find pypandoc

Type this in your terminal:
```bash
pip install pypandoc
```

### Can't find Pandoc

Get it from pandoc.org

### Git does not work

Make sure you are in a Git folder.

To check, type:
```bash
git status
```

### Won't start on Windows

Run the install script again.

### GPU not found

Check if you have GPU drivers.

To check NVIDIA:
```bash
nvidia-smi
```

To check AMD:
```bash
rocm-smi
```

To check Intel:
```bash
glxinfo | grep "OpenGL renderer"
```

The app works without a GPU. It just uses your CPU instead.

## What's Inside

Main parts of the program:

```
AsciiDoctorArtisan/
├── src/         # The code
├── templates/   # Example files
├── docs/        # Help files
├── tests/       # Test code
├── scripts/     # Helper tools
└── LICENSE      # Legal rules
```

## Help Us

You can help make this better!

How to help:
1. Copy the code to your computer
2. Make it better
3. Send it back to us

See our guide: [how-to-contribute.md](docs/developer/how-to-contribute.md)

## License

This is free to use! We use the MIT License.

## Get Help

Need more help?
- [How to Use](docs/user/how-to-use.md) - All features
- [GitHub Guide](docs/user/GITHUB_CLI_INTEGRATION.md) - Pull requests and issues
- [Performance Guide](docs/user/PERFORMANCE_GUIDE.md) - Speed tips and fixes
- [Ollama Chat Guide](docs/user/OLLAMA_CHAT_GUIDE.md) - AI chat help
- Look at our GitHub page
- Make a new issue on GitHub

**Reading Level**: Grade 5.0 or below

## Version

**Current Version**: 1.9.1 (Complete)

**What's New in v1.9.1:**
- Comprehensive codebase cleanup (7 issues fixed)
- Critical pypandoc bugfix (file opening fixed)
- Test infrastructure modernized
- Zero technical debt achieved
- 3,638 tests passing (96.4% coverage)

**What's New in v1.9.0:**
- Enhanced Git Status Display (real-time updates)
- Git Status Dialog with file details (Ctrl+Shift+G)
- Quick Commit Widget (Ctrl+G for fast commits)
- Color-coded Git indicators (clean, changes, conflicts)
- Improved Git workflow for power users

**What's New in v1.8.0:**
- Find and Replace words in your work
- Spell check with red lines under wrong words
- Right-click to see word fixes
- Add words to your own word list
- Press F7 to turn spell check on or off

**What's New in v1.7.1:**
- All 82 tests passing (100% pass rate)
- Full Ollama Chat feature tested
- Complete documentation added
- All bugs fixed (24 test failures → 0)
- Production ready quality

**What's New in v1.7.0:**
- AI Chat with 4 help modes
- Ask about your document
- Learn AsciiDoc syntax
- Get writing help
- Edit suggestions
- Chat history saved (100 messages)
- Works offline (your computer only)

**What's New in v1.6.0:**
- Works with GitHub now
- Can make pull requests
- Can make issues
- Faster file reading (async I/O)
- Faster block detection (10-14% better)

## Thank You

This app uses these tools:
- **PySide6** - Makes the windows (with GPU speed)
- **asciidoc3** - Makes HTML files
- **pypandoc** - Changes file types
- **pymupdf** - Reads PDF files fast
- **ollama** - Runs AI on your computer (if you want)
