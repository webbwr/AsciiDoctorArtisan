# AsciiDoc Artisan

A simple program. It helps you write papers with GPU-accelerated performance.

## What It Does

This program:
- Shows your work as you type (10-50x faster with GPU)
- Saves your work with Git
- Works with GitHub (make PRs and issues)
- Opens Word, PDF, Markdown, HTML files (3-5x faster)
- Saves to Word, PDF, Markdown, HTML
- Changes file types with AI or Pandoc
- Works on all computers
- Uses GPU for speed (automatic)
- Uses NPU for AI tasks (when available)
- Uses local AI for smart conversions (optional)
- Shows document version in status bar

## What You Need

You need these programs:
- **Python 3.11** - Makes it run
- **Pandoc** - Changes file types
- **wkhtmltopdf** - Makes PDF files
- **Git** - Saves work online (optional)
- **GitHub CLI (gh)** - Work with GitHub (optional, from cli.github.com)
- **Ollama** - AI file changes (optional, from ollama.com)
- **GPU drivers** - For hardware acceleration (automatic)

## Install It

### Easy Way (Best)

We have scripts. They do it all.

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

The script:
- Gets Python parts
- Gets Pandoc
- Checks Git
- Tests it

### Do It By Hand

If you want to do it yourself:

1. Get Python parts:
```bash
pip install -r requirements.txt
```

2. Get Pandoc and PDF tool:
   - **Linux**: `sudo apt install pandoc wkhtmltopdf`
   - **Mac**: `brew install pandoc wkhtmltopdf`
   - **Windows**: Get from pandoc.org and wkhtmltopdf.org

## Use It

### Start It

Type this:
```bash
python3 src/main.py
```

On Windows:
```bash
python src\main.py
```

Or click the start file.

### Fast Keys

| Press | Does |
|-------|------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Q | Close |
| Ctrl+F | Find |
| Ctrl+D | Dark mode |
| Ctrl++ | Big text |
| Ctrl+- | Small text |

### Open Files

**What you can open:**
- AsciiDoc files (.adoc)
- Markdown files (.md)
- Word files (.docx)
- Web files (.html)
- PDF files (.pdf)

All files open fast. PDF files open 3-5x faster than before.

**How to open:**
1. Click `File` then `Open`
2. Pick your file
3. Click Open

It changes to AsciiDoc for you.

### Save Files

**Save your work:**
1. Click `File` then `Save`
2. Type a name
3. Click Save

**Save as other types:**
1. Click `File` then `Save As`
2. Pick type:
   - AsciiDoc (.adoc)
   - Markdown (.md)
   - Word (.docx)
   - PDF (.pdf)
   - Web page (.html)
3. Type a name
4. Click Save

It changes it for you. No wait.

### Use Git

If in a Git folder:

**Pull** (Get new work):
- Click `Git` then `Pull`

**Commit** (Save work):
1. Click `Git` then `Commit`
2. Type what you did
3. Click OK

**Push** (Send to web):
- Click `Git` then `Push`

## GPU Acceleration (New in v1.4!)

This app uses your graphics card for speed:
- **10-50x faster preview** - GPU-accelerated rendering
- **70-90% less CPU use** - Smooth performance
- **Automatic detection** - Works with NVIDIA, AMD, Intel GPUs
- **NPU support** - Uses Intel NPU for AI tasks
- **Smooth scrolling** - 60fps+ with hardware acceleration
- **Auto fallback** - Works without GPU too

**What it detects:**
- NVIDIA GPUs (CUDA, OpenCL, Vulkan)
- AMD GPUs (ROCm, OpenCL, Vulkan)
- Intel GPUs (OpenCL, Vulkan)
- Intel NPU (OpenVINO)

No setup needed. It detects your hardware and uses it automatically.

**Check GPU status:**
The app shows in logs at startup:
```
[INFO] GPU detected: NVIDIA GeForce RTX 4060 Laptop GPU (nvidia)
[INFO] Compute capabilities: cuda, opencl, vulkan
[INFO] QWebEngineView with acceleration
```

## AI Features (v1.2+)

Smart document conversions with local AI:

**What it does:**
- **Smarter conversions**: AI understands document structure better than rule-based tools
- **Local AI**: Uses Ollama running on your computer (no cloud, no data leaves your machine)
- **Pick your model**: Choose from installed models (phi3, llama2, mistral, etc.)
- **Auto fallback**: Uses Pandoc if AI not available or if conversion fails
- **Real-time status**: Status bar shows which method is active

**Why use AI?**
- Better preserves document formatting and structure
- Understands context (e.g., code blocks, tables, lists)
- Handles complex documents with nested elements
- Improves quality of Markdown ↔ AsciiDoc conversions

### Turn On AI

**Step 1: Install Ollama**
```bash
# Visit ollama.com and follow installation instructions for your OS
# Or use these quick commands:

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download installer from ollama.com
```

**Step 2: Install an AI model**
```bash
# Recommended lightweight model (good for most documents)
ollama pull phi3:mini

# Other options:
ollama pull llama2        # Better quality, slower
ollama pull mistral       # Balanced performance
ollama pull codellama     # Best for code-heavy documents
```

**Step 3: Enable in AsciiDoc Artisan**
1. Open the app
2. Go to: **Tools** → **AI Status** → **Settings**
3. Check "Enable Ollama AI"
4. Select your model from the dropdown
5. Click "Save"

**Step 4: Verify it's working**
- Status bar shows: `AI: phi3:mini` (or your chosen model)
- Try converting a document (File → Import or File → Export)
- AI will process the conversion automatically

**Note:** If Ollama isn't running or the model isn't available, the app automatically uses Pandoc instead.

## The Right Side

The right side shows your work:
- Updates when you stop typing (instant with GPU)
- Moves as you write
- Shows bold, lists, titles
- Smooth 60fps scrolling

## Where It Saves

Settings save here:
- **Linux**: `~/.config/AsciiDocArtisan/`
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`

## Fix Problems

### Can't find pypandoc
Type this: `pip install pypandoc`

### Can't find Pandoc
Get it from pandoc.org

### Git does not work
Make sure you are in a Git folder.
Type `git status` to check.

### Won't start on Windows
Run the install script again.

### GPU not detected
Check if you have GPU drivers installed:
- NVIDIA: `nvidia-smi`
- AMD: `rocm-smi`
- Intel: `glxinfo | grep "OpenGL renderer"`

The app works without GPU (uses CPU instead).

## What's Inside

Main parts:

```
AsciiDoctorArtisan/
├── src/         # Code
├── templates/   # Examples
├── docs/        # Help
├── tests/       # Tests
├── scripts/     # Tools
└── LICENSE     # Rules
```

## Help Us

You can help!
1. Copy the code
2. Make it better
3. Send it back

See [how-to-contribute.md](docs/how-to-contribute.md) for more.

## License

This is free! MIT License.

## Get Help

Need help?
- [How to Use](docs/how-to-use.md) - All features
- [GitHub Integration](docs/GITHUB_CLI_INTEGRATION.md) - Pull requests and issues
- Look at GitHub
- Make a new issue

**Reading Level**: Grade 5.0

## Version

**Current Version**: 1.5.0

**What's New in v1.5.0:**
- ✅ Fast startup (1.05 seconds)
- ✅ Worker pool system
- ✅ Operation cancellation
- ✅ 60%+ test coverage (481+ tests, 69 test files)
- ✅ Main window: 561 lines (67% smaller)
- ✅ GPU acceleration (10-50x faster from v1.4.0)
- ✅ Grandmaster TechWriter skill (automatic Grade 5.0 docs)

## Thank You

This uses:
- **PySide6** - Makes windows (with GPU acceleration)
- **asciidoc3** - Makes HTML
- **pypandoc** - Changes files
- **pymupdf** - Fast PDF reading
- **ollama** - Local AI (optional)
