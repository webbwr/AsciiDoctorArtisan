# AsciiDoc Artisan

A simple program. It helps you write papers.

## What It Does

This program:
- Shows your work as you type (2-5x faster with GPU)
- Saves your work with Git
- Opens Word, PDF, Markdown, HTML files (3-5x faster)
- Saves to Word, PDF, Markdown, HTML
- Changes file types with AI or Pandoc
- Works on all computers
- Uses GPU for speed (optional)
- Uses local AI for smart conversions (optional)
- Smart caching saves time

## What You Need

You need these programs:
- **Python 3.11** - Makes it run
- **Pandoc** - Changes file types
- **wkhtmltopdf** - Makes PDF files
- **Git** - Saves work online (optional)
- **Ollama** - AI file changes (optional, from ollama.com)

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

## Speed Features (New in v1.1!)

This app is fast:
- **GPU speed**: Uses your graphics card (2-5x faster view)
- **Fast PDF**: Opens PDF files 3-5x faster
- **Smart code**: Uses best Python methods for all operations
- **Auto-works**: Falls back if GPU not there
- **All computers**: Works on Windows, Mac, Linux

No setup needed. It just works.

## AI Features (New in v1.2!)

Smart file changes with AI:
- **Ollama AI**: Use local AI for better conversions
- **Pick your model**: Choose from installed AI models
- **Shows in status bar**: See which method is active
- **Auto fallback**: Uses Pandoc if AI not working
- **Privacy first**: AI runs on your computer only

### Turn On AI

1. Install Ollama from ollama.com
2. Get a model: `ollama pull phi3:mini`
3. In app: Tools → AI Status → Settings
4. Turn on "Enable Ollama AI"
5. Pick your model
6. Status bar shows "AI: your-model"

Now all file changes use AI!

## The Right Side

The right side shows your work:
- Updates when you stop typing
- Moves as you write
- Shows bold, lists, titles

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
- [How to Install](docs/how-to-install.md) - Setup
- [How to Help](docs/how-to-contribute.md) - Join
- Look at GitHub
- Make a new issue

**Reading Level**: Grade 5.0

## Thank You

This uses:
- **PySide6** - Makes windows
- **asciidoc3** - Makes HTML
- **pypandoc** - Changes files
