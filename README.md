# AsciiDoc Artisan

A simple program. It helps you write papers.

## What It Does

This program:
- Shows your work as you type
- Saves your work with Git
- Opens Word, PDF, Markdown, HTML files
- Saves to Word, PDF, Markdown, HTML
- Changes file types for you
- Works on all computers

## What You Need

You need these programs:
- **Python 3.11** - Makes it run
- **Pandoc** - Changes file types
- **wkhtmltopdf** - Makes PDF files
- **Git** - Saves work online (not required)

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

All files open fast. No wait.

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
