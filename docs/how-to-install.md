# How to Install

**Reading Level**: Grade 5.0 (Elementary)

This guide shows you how to put AsciiDoc Artisan on your computer.

## What You Need

Before you start:
- A computer (Windows, Mac, or Linux)
- Internet to download files
- About 10 minutes

## Quick Install (Easiest Way!)

We made special scripts that do everything for you!

### For Mac or Linux:

```bash
# Get the program
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run the installer (it does everything!)
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

### For Windows 11:

```powershell
# Get the program (in PowerShell 7)
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run the installer (it does everything!)
.\Install-AsciiDocArtisan.ps1
```

**What the installer does**:
- ✅ Checks you have Python 3.11 or newer
- ✅ Adds all Python tools needed
- ✅ Adds Pandoc (for changing files)
- ✅ Checks if Git is there
- ✅ Makes a safe space for the program
- ✅ Tests everything works
- ✅ Shows you what to do next

**That's it! Skip to "Start the Program" below.**

---

## Slow Install (Do It Yourself)

Want to do it by hand? Follow these steps:

## Step 1: Get Python

Python makes the program work.

**Do you have Python?**
1. Open a black window (called terminal or command prompt)
2. Type: `python3 --version` and press Enter
3. If you see "Python 3.11" or bigger, skip to Step 2!

**Get Python if you need it**:

**On Windows**:
1. Go to python.org
2. Click "Downloads"
3. Click "Download Python 3.12"
4. Open the file you downloaded
5. Check the box "Add Python to PATH" (very important!)
6. Click "Install Now"

**On Mac**:
1. Open Terminal
2. Type: `brew install python3`
3. (If that doesn't work, get Homebrew from brew.sh first)

**On Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

## Step 2: Get the Program

**Easy way (if you have Git)**:
1. Open terminal
2. Type these lines:
```bash
cd ~/github
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

**Other way (if you don't have Git)**:
1. Go to github.com/webbwr/AsciiDoctorArtisan
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file
5. Remember where you put it!

## Step 3: Add Python Tools

The program needs extra tools.

**On Linux or Mac**:
```bash
chmod +x setup.sh
./setup.sh
```

**On any computer**:
```bash
pip install -r requirements.txt
```

Wait a few minutes. It's downloading things.

## Step 4: Add Pandoc (You Can Skip This)

Pandoc changes Word files to AsciiDoc. It helps but isn't required.

**On Windows**:
1. Go to pandoc.org/installing.html
2. Get the Windows file
3. Open it
4. Click the buttons to install

**On Mac**:
```bash
brew install pandoc
```

**On Linux**:
```bash
sudo apt install pandoc
```

## Step 5: Test It

Make sure it works!

**On Linux or Mac**:
```bash
chmod +x verify.sh
./verify.sh
```

**On Windows**:
Right-click `scripts\verify-environment.ps1` and pick "Run with PowerShell"

**Or test yourself**:
```bash
python3 -c "import PySide6; print('Works!')"
python3 -c "import asciidoc3; print('Works!')"
```

If you see "Works!" both times, you're done!

## Start the Program

**Easy way**:
- **Windows**: Double-click `launch-asciidoc-artisan-gui.bat`
- **Mac/Linux**: Double-click `launch-asciidoc-artisan-gui.sh`

**Other way**:
```bash
python3 src/main.py
```

**If you used the installer and made a virtual environment**:
```bash
# First, turn on the virtual environment
source venv/bin/activate    # Mac/Linux
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Then start the program
python src/main.py
```

## Problems?

### "Python not found"

**On Windows**:
1. Uninstall Python
2. Install it again
3. Check "Add Python to PATH" this time

### "pip not found"

Type this:
```bash
python3 -m ensurepip --upgrade
```

### "Can't run scripts" (on Linux/Mac)

Type this:
```bash
chmod +x install-asciidoc-artisan.sh launch-asciidoc-artisan-gui.sh
```

### "Can't run scripts" (on Windows)

Open PowerShell as boss (right-click, pick "Run as administrator"):
```powershell
Set-ExecutionPolicy RemoteSigned
```

### Still doesn't work?

Try this:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## What Got Installed

**Main stuff** (required):
- Python 3.11+ (runs everything)
- PySide6 (makes windows)
- asciidoc3 (makes HTML)

**Extra stuff** (helpful):
- pypandoc (changes files)
- pdfplumber (reads PDFs)
- Pandoc (converts documents)

## Check Everything

Type these to check:

```bash
python3 --version
python3 -c "import PySide6, asciidoc3; print('All good!')"
pandoc --version
python3 src/main.py
```

## Update Later

**If you used Git**:
```bash
cd AsciiDoctorArtisan
git pull
pip install -r requirements.txt --upgrade
```

**If you downloaded ZIP**:
1. Download new ZIP
2. Unzip it
3. Type: `pip install -r requirements.txt --upgrade`

## Remove It

To delete everything:

1. Delete the program folder
2. Type: `pip uninstall PySide6 asciidoc3 pypandoc`

Your settings are in a hidden folder. Find it at:
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`
- **Linux**: `~/.config/AsciiDocArtisan/`

Delete that folder to remove all settings.

## What's Next?

Now that it works:
1. Read [how-to-use.md](how-to-use.md) to learn how to use it
2. Look at examples in `templates/`
3. Start writing!

## Need Help?

- Check README.md for more help
- Look at issues on GitHub
- Create a new issue if you find a problem

---
**Document Info**: Reading level Grade 5.0 | Last updated: 2025
