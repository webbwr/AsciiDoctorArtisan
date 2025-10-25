# AsciiDoc Artisan

A simple program that helps you write and edit AsciiDoc documents.

## What Does It Do?

AsciiDoc Artisan is a writing tool that:
- Shows you what your document will look like as you type
- Lets you save and share your work with Git
- Can change Word documents and PDFs into AsciiDoc files
- Works on Windows, Mac, and Linux computers

## What You Need

Before you start, you need these programs on your computer:
- **Python 3.11 or newer** - The main program that runs everything
- **Pandoc** - Helps convert different document types (optional but helpful)
- **Git** - Helps save and share your work (optional)

## How to Install

### Easy Way (Linux or WSL)

1. Open your terminal
2. Type these commands:
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

### Regular Way (Any Computer)

1. Install Python parts:
```bash
pip install -r requirements.txt
```

2. Install Pandoc:
   - **Linux**: `sudo apt install pandoc`
   - **Mac**: `brew install pandoc`
   - **Windows**: Download from pandoc.org

## How to Use It

### Starting the Program

Open your terminal and type:
```bash
python3 src/main.py
```

On Windows, type:
```bash
python src\main.py
```

Or just double-click `launch_gui.sh` (Linux/Mac) or `launch_gui.bat` (Windows)

### Quick Keys

These shortcuts make things faster:

| What You Press | What Happens |
|---------------|--------------|
| Ctrl+N | Make a new file |
| Ctrl+O | Open a file |
| Ctrl+S | Save your work |
| Ctrl+Q | Close the program |
| Ctrl+F | Find words in your document |
| Ctrl+D | Switch between light and dark colors |
| Ctrl++ | Make text bigger |
| Ctrl+- | Make text smaller |

### Opening and Saving Files

**Files You Can Open:**
- `.adoc` files (AsciiDoc files)
- `.docx` files (Word documents - will be changed to AsciiDoc)
- `.pdf` files (PDF documents - text will be pulled out)

**To Open a File:**
1. Click `File` menu, then `Open`
2. Pick your file
3. Click the Open button

**To Save Your Work:**
1. Click `File` menu, then `Save`
2. Type a name for your file
3. Click the Save button

### Using Git (Saving to the Cloud)

If your file is in a Git folder, you can:

**Pull** (Get the newest version):
- Click `Git` menu, then `Pull`

**Commit** (Save your changes):
1. Click `Git` menu, then `Commit`
2. Type a short message about what you changed
3. Click OK

**Push** (Send to GitHub):
- Click `Git` menu, then `Push`

## The Preview Window

The right side of the screen shows what your document will look like:
- Updates as you type (after you stop typing for a moment)
- Scrolls along with where you're writing
- Shows all AsciiDoc formatting (bold, lists, headings, etc.)

## Where Files Are Saved

The program remembers your settings in a special file:
- **Linux**: `~/.config/AsciiDocArtisan/AsciiDocArtisan.json`
- **Windows**: `%APPDATA%/AsciiDocArtisan/AsciiDocArtisan.json`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/AsciiDocArtisan.json`

## Common Problems

### "Can't find pypandoc"
**Fix**: Type `pip install pypandoc` in your terminal

### "Can't find Pandoc"
**Fix**: Install Pandoc from pandoc.org

### "Git doesn't work"
**Fix**: Make sure your file is in a Git folder (check by typing `git status`)

### "Program won't start on Windows"
**Fix**: Right-click `launch_gui.bat` and pick "Run as administrator"

## Project Folders

Here's what's in the project:

```
AsciiDoctorArtisan/
├── src/                    # All the program code
│   ├── main.py            # Main program file
│   └── asciidoc_artisan/  # Helper code
├── templates/             # Example documents you can copy
├── docs/                  # Help files
│   ├── user/             # Guides for users
│   └── development/      # Guides for programmers
├── tests/                # Code tests
├── README.md             # This file
└── LICENSE              # Rules for using this program
```

## Want to Help?

We'd love your help! Here's how:
1. Make a copy of the project (fork it)
2. Make your changes
3. Send us your changes (pull request)

## License

You can use this program for free! It uses the MIT License.

## More Help

Need more help?
- **[How to Use Guide](docs/how-to-use.md)** - Complete guide to all features
- **[How to Install Guide](docs/how-to-install.md)** - Detailed installation help
- **[Specifications](SPECIFICATIONS.md)** - What the program must do (Grade 5.8)
- **[How to Contribute](docs/how-to-contribute.md)** - Help improve the program
- Look at issues on GitHub
- Create a new issue if you find a bug

**Reading Level**: Grade 6.1 (Elementary/Middle School)

## Thank You

This program uses these great tools:
- **PySide6** - Makes the windows and buttons
- **asciidoc3** - Turns AsciiDoc into HTML
- **pypandoc** - Changes document types
