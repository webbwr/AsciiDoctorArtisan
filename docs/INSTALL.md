# Installation Guide

This guide shows you how to install AsciiDoc Artisan on your computer.

## Before You Start

You need these things first:
- A computer with Windows, Mac, or Linux
- Internet connection to download files
- About 10 minutes of time

## Step-by-Step Installation

### Step 1: Install Python

Python is the main program that runs AsciiDoc Artisan.

**Check if you have Python**:
1. Open terminal (Mac/Linux) or Command Prompt (Windows)
2. Type: `python3 --version` (or just `python --version` on Windows)
3. If you see "Python 3.11" or higher, you're good! Skip to Step 2.

**If you need to install Python**:

**Windows**:
1. Go to python.org
2. Click "Downloads"
3. Click "Download Python 3.12"
4. Run the installer
5. **Important**: Check the box that says "Add Python to PATH"
6. Click "Install Now"

**Mac**:
1. Open Terminal
2. Type: `brew install python3`
3. If you don't have Homebrew, get it from brew.sh first

**Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Download AsciiDoc Artisan

**Using Git** (easier for updates):
1. Open terminal
2. Go to where you want the program:
```bash
cd ~/github
```
3. Download it:
```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

**Without Git** (download zip file):
1. Go to github.com/webbwr/AsciiDoctorArtisan
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file
5. Remember where you put it!

### Step 3: Install Python Parts

The program needs some extra Python tools.

**Easy Way** (Linux/Mac):
```bash
chmod +x setup.sh
./setup.sh
```

**Regular Way** (any computer):
```bash
pip install -r requirements.txt
```

Wait a few minutes while it downloads and installs everything.

### Step 4: Install Pandoc (Optional but Helpful)

Pandoc helps change document types (Word to AsciiDoc, etc.)

**Windows**:
1. Go to pandoc.org/installing.html
2. Download the Windows installer
3. Run it
4. Click through the steps

**Mac**:
```bash
brew install pandoc
```

**Linux**:
```bash
sudo apt install pandoc
```

### Step 5: Test It Works

**Linux/Mac**:
```bash
chmod +x verify.sh
./verify.sh
```

**Windows**:
Right-click `AsciiDocArtisanVerify.ps1` and pick "Run with PowerShell"

**Or test manually**:
```bash
python3 -c "import PySide6; print('PySide6 OK')"
python3 -c "import asciidoc3; print('asciidoc3 OK')"
python3 -c "import pypandoc; print('pypandoc OK')"
```

If all say "OK", you're ready!

## Starting the Program

### Quick Start

**Windows**:
- Double-click `launch_gui.bat`

**Linux/Mac**:
- Double-click `launch_gui.sh`

### Command Line Start

**Windows**:
```bash
python src\main.py
```

**Linux/Mac**:
```bash
python3 src/main.py
```

## Common Installation Problems

### Problem: "Python is not recognized"

**Windows Fix**:
1. Uninstall Python
2. Install again
3. Make sure to check "Add Python to PATH"

### Problem: "pip: command not found"

**Fix**:
```bash
python3 -m ensurepip --upgrade
```

### Problem: "Permission denied" on Linux/Mac

**Fix**:
```bash
chmod +x setup.sh verify.sh launch_gui.sh
```

### Problem: "Can't install packages"

**Fix** - Try using a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Problem: "Qt platform plugin could not be initialized"

**Linux Fix**:
```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

### Problem: Windows says "Can't run scripts"

**Fix** - Open PowerShell as Administrator:
```powershell
Set-ExecutionPolicy RemoteSigned
```

## What Got Installed

Here's what you installed:

**Core Parts** (required):
- **Python 3.11+**: Runs everything
- **PySide6**: Makes the windows and buttons
- **asciidoc3**: Turns AsciiDoc into HTML

**Extra Parts** (optional but useful):
- **pypandoc**: Changes document types
- **pdfplumber**: Reads text from PDFs
- **Pandoc**: Helps with conversions

## Checking Your Installation

Run these commands to check everything:

```bash
# Check Python version
python3 --version

# Check if all parts are installed
python3 -c "import PySide6, asciidoc3, pypandoc; print('All parts OK!')"

# Check Pandoc
pandoc --version

# Try starting the program
python3 src/main.py
```

## Updating Later

### Update with Git

If you used Git to install:
```bash
cd AsciiDoctorArtisan
git pull
pip install -r requirements.txt --upgrade
```

### Update without Git

1. Download the new ZIP file
2. Unzip it
3. Copy your files to the new folder
4. Run: `pip install -r requirements.txt --upgrade`

## Uninstalling

To remove AsciiDoc Artisan:

1. Delete the program folder
2. Remove Python packages (if you want):
```bash
pip uninstall PySide6 asciidoc3 pypandoc pdfplumber
```

Your settings file stays at:
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`
- **Linux**: `~/.config/AsciiDocArtisan/`

Delete this folder if you want to remove all settings.

## Next Steps

Now that it's installed:
1. Read the USER_GUIDE.md file
2. Try opening the example files in `templates/`
3. Start writing!

## Need Help?

- Check the troubleshooting section in README.md
- Look at GitHub issues
- Create a new issue with your problem
