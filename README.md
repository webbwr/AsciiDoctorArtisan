# AsciiDoc Artisan

A simple program. It helps you write papers. It is very fast.

## What It Does

This program does many things:
- Shows your work as you type
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
- Chat with AI about your work (new!)

The GPU makes it 10-50x faster. That means much faster than before.

AI chat helps you in 4 ways:
- Ask about your paper
- Learn AsciiDoc rules
- Get help with writing
- Fix your work

All AI works on your computer. No cloud needed.

## What You Need

You need these programs first:
- **Python 3.11** - Makes it run
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

Type this:
```bash
python3 src/main.py
```

On Windows, type this:
```bash
python src\main.py
```

Or just click the start file.

### Fast Keys

| Press | What It Does |
|-------|--------------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Q | Close |
| Ctrl+F | Find text |
| Ctrl+D | Dark mode |
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
ollama pull phi3:mini
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

Look at the status bar. It should say: `AI: phi3:mini`

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

See our guide: [how-to-contribute.md](docs/how-to-contribute.md)

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

**Current Version**: 1.7.0 (Phase 1 Optimization Complete!)

**What's New in v1.7.0:**
- Preview is 40-50% faster
- Uses 30% less memory
- Theme switch is instant
- All type hints added (100%)
- Over 621 tests now
- Starts in 1.05 seconds
- GPU makes it 10-50x faster

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
