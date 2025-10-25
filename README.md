# AsciiDoc Artisan

A simple program that helps you write AsciiDoc papers.

## What Does It Do?

AsciiDoc Artisan is a writing tool that:
- Shows you what your paper will look like as you type
- Lets you save and share your work with Git
- Can change Word files and PDFs into AsciiDoc files
- Works on Windows, Mac, and Linux computers

## What You Need

Before you start, you need these programs:
- **Python 3.11 or newer** - Makes everything run
- **Pandoc** - Helps change file types (you can skip this)
- **Git** - Helps save and share your work (you can skip this)

## How to Put It On Your Computer

### Easy Way (Linux or WSL)

1. Open your terminal (the black window)
2. Type these lines:
```bash
cd ~/github
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
chmod +x setup.sh
./setup.sh
```

3. Test it works:
```bash
chmod +x verify.sh
./verify.sh
```

### Other Way (Any Computer)

1. Get Python parts:
```bash
pip install -r requirements.txt
```

2. Get Pandoc:
   - **Linux**: `sudo apt install pandoc`
   - **Mac**: `brew install pandoc`
   - **Windows**: Get it from pandoc.org

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

Or just click `launch_gui.sh` (Linux/Mac) or `launch_gui.bat` (Windows)

### Quick Keys

These make things faster:

| What You Press | What Happens |
|---------------|--------------|
| Ctrl+N | Make a new file |
| Ctrl+O | Open a file |
| Ctrl+S | Save your work |
| Ctrl+Q | Close the program |
| Ctrl+F | Find words |
| Ctrl+D | Switch light and dark |
| Ctrl++ | Make text bigger |
| Ctrl+- | Make text smaller |

### Open and Save Files

**Files You Can Open:**
- `.adoc` files (AsciiDoc files)
- `.docx` files (Word files - changes to AsciiDoc)
- `.pdf` files (PDF files - gets the text out)

**To Open a File:**
1. Click `File` then `Open`
2. Pick your file
3. Click Open

**To Save Your Work:**
1. Click `File` then `Save`
2. Type a name for your file
3. Click Save

### Use Git (Save to the Cloud)

If your file is in a Git folder, you can:

**Pull** (Get the newest version):
- Click `Git` then `Pull`

**Commit** (Save your changes):
1. Click `Git` then `Commit`
2. Type what you changed
3. Click OK

**Push** (Send to GitHub):
- Click `Git` then `Push`

## The View Window

The right side shows what your paper will look like:
- Changes as you type (after you stop for a bit)
- Moves with where you're writing
- Shows all your formatting (bold, lists, titles, etc.)

## Where Files Are Saved

The program remembers your settings in a file:
- **Linux**: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows**: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

## Common Problems

### "Can't find pypandoc"
**Fix**: Type `pip install pypandoc` in your terminal

### "Can't find Pandoc"
**Fix**: Get Pandoc from pandoc.org

### "Git doesn't work"
**Fix**: Make sure your file is in a Git folder (type `git status` to check)

### "Program won't start on Windows"
**Fix**: Right-click `launch_gui.bat` and pick "Run as administrator"

## What's in the Project

Here's what's in the folders:

```
AsciiDoctorArtisan/
├── src/                    # All the program code
│   ├── main.py            # Main program file
│   └── asciidoc_artisan/  # Helper code
├── templates/             # Example papers you can copy
├── docs/                  # Help files
│   ├── how-to-use.md     # How to use it (Grade 5.1)
│   ├── how-to-install.md # How to install it (Grade 3.2)
│   └── how-to-contribute.md # How to help (Grade 4.0)
├── tests/                # Code tests
├── README.md             # This file (Grade 5.0)
├── SPECIFICATIONS.md     # What it must do (Grade 3.1)
└── LICENSE              # Rules for using it
```

## Want to Help?

We'd love your help! Here's how:
1. Make a copy of the project (fork it)
2. Make your changes
3. Send us your changes (pull request)

See [how-to-contribute.md](docs/how-to-contribute.md) to learn more.

## License

You can use this program for free! It uses the MIT License.

## More Help

Need more help?
- **[How to Use](docs/how-to-use.md)** - All features explained (Grade 5.1)
- **[How to Install](docs/how-to-install.md)** - Step by step setup (Grade 3.2)
- **[What It Must Do](SPECIFICATIONS.md)** - All requirements (Grade 3.1)
- **[How to Help](docs/how-to-contribute.md)** - Join the team (Grade 4.0)
- Look at issues on GitHub
- Create a new issue if you find a bug

**Reading Level**: Grade 5.0 (Elementary)

## Thank You

This program uses these great tools:
- **PySide6** - Makes the windows and buttons
- **asciidoc3** - Turns AsciiDoc into HTML
- **pypandoc** - Changes file types
