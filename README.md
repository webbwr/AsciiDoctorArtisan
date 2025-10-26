# AsciiDoc Artisan

A simple program that helps you write AsciiDoc papers.

## What Does It Do?

AsciiDoc Artisan is a writing tool that:
- Shows you what your paper will look like as you type
- Lets you save and share your work with Git
- Can open many file types (Word, PDF, Markdown, HTML)
- Can save to many file types (Word, PDF, Markdown, HTML)
- Changes file types for you in the background
- Works on Windows, Mac, and Linux computers

## What You Need

Before you start, you need these programs:
- **Python 3.11 or newer** - Makes everything run
- **Pandoc** - Changes file types (needed for Word, PDF)
- **wkhtmltopdf** - Makes PDF files (needed for PDF save)
- **Git** - Helps save and share your work (you can skip this)

## How to Put It On Your Computer

### Easy Way - Automatic Install (Recommended)

We have special scripts that do everything for you!

**For Mac or Linux:**
```bash
# Get the program
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run the installer
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**For Windows 11:**
```powershell
# Get the program (in PowerShell)
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run the installer
.\Install-AsciiDocArtisan.ps1
```

The installer:
- Gets Python parts
- Gets Pandoc
- Checks Git
- Tests it works

### Do It Yourself

If you like to install by hand:

1. Get Python parts:
```bash
pip install -r requirements.txt
```

2. Get Pandoc and PDF tool:
   - **Linux**: `sudo apt install pandoc wkhtmltopdf`
   - **Mac**: `brew install pandoc wkhtmltopdf`
   - **Windows**: Get from pandoc.org and wkhtmltopdf.org

## How to Use It

### Start the Program

Open your terminal and type:
```bash
python3 src/main.py
```

On Windows, type:
```bash
python src\main.py
```

Or just click `launch-asciidoc-artisan-gui.sh` (Linux/Mac) or `launch-asciidoc-artisan-gui.bat` (Windows)

### Quick Keys

Fast ways to work:

| Press | Does |
|-------|------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Q | Close |
| Ctrl+F | Find |
| Ctrl+D | Dark mode |
| Ctrl++ | Bigger text |
| Ctrl+- | Smaller text |

### Open and Save Files

**Files You Can Open:**
- `.adoc` files (AsciiDoc files)
- `.md` files (Markdown files - changes to AsciiDoc)
- `.docx` files (Word files - changes to AsciiDoc)
- `.html` files (Web files - changes to AsciiDoc)
- `.pdf` files (PDF files - gets the text out)

All files open right away. No questions asked.

**To Open a File:**
1. Click `File` then `Open`
2. Pick your file
3. Click Open

The program changes it to AsciiDoc for you.

**To Save Your Work:**
1. Click `File` then `Save`
2. Type a name for your file
3. Click Save

**To Save in Other Formats:**
1. Click `File` then `Save As`
2. Pick what type you want:
   - AsciiDoc (.adoc)
   - Markdown (.md)
   - Word (.docx)
   - PDF (.pdf)
   - Web page (.html)
3. Type a name
4. Click Save

The program changes it for you. No questions asked.

### Use Git (Save Online)

If your file is in a Git folder:

**Pull** (Get new version):
- Click `Git` then `Pull`

**Commit** (Save changes):
1. Click `Git` then `Commit`
2. Type what you did
3. Click OK

**Push** (Send to web):
- Click `Git` then `Push`

## The View Window

The right side shows how your paper looks:
- Updates when you stop typing
- Moves as you write
- Shows bold, lists, titles

## Where Settings Are Saved

The program saves your settings here:
- **Linux**: `~/.config/AsciiDocArtisan/`
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`

## Common Problems

### "Can't find pypandoc"
**Fix**: Type `pip install pypandoc` in your terminal

### "Can't find Pandoc"
**Fix**: Get Pandoc from pandoc.org

### "Git doesn't work"
**Fix**: Make sure your file is in a Git folder (type `git status` to check)

### "Program won't start on Windows"
**Fix**: Run the installer again: `.\Install-AsciiDocArtisan.ps1`

## What's in the Project

Main folders:

```
AsciiDoctorArtisan/
├── src/         # Program code
├── templates/   # Example files
├── docs/        # Help files
├── tests/       # Tests
├── scripts/     # Helper scripts
└── LICENSE     # Use rules
```

## Want to Help?

You can help! Here's how:
1. Copy the project
2. Make changes
3. Send them to us

See [how-to-contribute.md](docs/how-to-contribute.md) for more.

## License

You can use this program for free! It uses the MIT License.

## More Help

Need help?
- **[How to Use](docs/how-to-use.md)** - All features
- **[How to Install](docs/how-to-install.md)** - Setup help
- **[How to Help](docs/how-to-contribute.md)** - Join us
- Look at GitHub issues
- Make a new issue for bugs

**Reading Level**: Grade 5.0 (Elementary)

## Thank You

This program uses these tools:
- **PySide6** - Makes windows and buttons
- **asciidoc3** - Turns AsciiDoc to HTML
- **pypandoc** - Changes file types
