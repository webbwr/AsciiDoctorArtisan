# How to Install

**Reading Level**: Grade 5.0

This guide shows how to get AsciiDoc Artisan.

## What You Need

You need:
- A computer
- Internet
- 10 minutes

## Quick Install

We made scripts. They do all!

### For Mac or Linux:

```bash
# Get it
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run it
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

### For Windows 11:

```powershell
# Get it
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan

# Run it
.\Install-AsciiDocArtisan.ps1
```

**What it does**:
- ✅ Checks Python
- ✅ Adds tools
- ✅ Adds Pandoc
- ✅ Checks Git
- ✅ Makes safe space
- ✅ Tests all
- ✅ Shows next steps

**Done! Skip to "Start the Program" below.**

---

## Slow Install

Want to do it by hand? Follow steps.

## Step 1: Get Python

Python makes it work.

**Do you have it?**
1. Open terminal
2. Type: `python3 --version`
3. Press Enter
4. See "Python 3.11"? Skip to Step 2!

**Get it if you need**:

**On Windows**:
1. Go to python.org
2. Click "Downloads"
3. Click "Download Python 3.12"
4. Open file
5. Check "Add Python to PATH"
6. Click "Install Now"

**On Mac**:
1. Open Terminal
2. Type: `brew install python3`
3. (No brew? Get from brew.sh first)

**On Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

## Step 2: Get Program

**Easy way (with Git)**:
1. Open terminal
2. Type:
```bash
cd ~/github
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
```

**Other way (no Git)**:
1. Go to github.com/webbwr/AsciiDoctorArtisan
2. Click green "Code" button
3. Click "Download ZIP"
4. Unzip file
5. Remember where!

## Step 3: Add Tools

Program needs tools.

**On Linux or Mac**:
```bash
chmod +x setup.sh
./setup.sh
```

**On any PC**:
```bash
pip install -r requirements.txt
```

Wait a bit.

## Step 4: Add Pandoc

Pandoc changes Word files. Optional.

**On Windows**:
1. Go to pandoc.org/installing.html
2. Get Windows file
3. Open it
4. Click install

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

**Or test self**:
```bash
python3 -c "import PySide6; print('Works!')"
python3 -c "import asciidoc3; print('Works!')"
```

See "Works!" both times? Done!

## Start Program

**Easy way**:
- **Windows**: Click `launch-asciidoc-artisan-gui.bat`
- **Mac/Linux**: Click `launch-asciidoc-artisan-gui.sh`

**Other way**:
```bash
python3 src/main.py
```

**If used installer**:
```bash
# Turn on space
source venv/bin/activate    # Mac/Linux
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Start
python src/main.py
```

## Problems?

### "Python not found"

**On Windows**:
1. Remove Python
2. Install again
3. Check "Add Python to PATH"

### "pip not found"

Type:
```bash
python3 -m ensurepip --upgrade
```

### "Can't run scripts" (Linux/Mac)

Type:
```bash
chmod +x install-asciidoc-artisan.sh launch-asciidoc-artisan-gui.sh
```

### "Can't run scripts" (Windows)

Open PowerShell as admin:
```powershell
Set-ExecutionPolicy RemoteSigned
```

### Still broke?

Try:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## What Got Added

**Main**:
- Python 3.11+
- PySide6
- asciidoc3

**Extra**:
- pypandoc
- pdfplumber
- Pandoc

## Check All

Type:

```bash
python3 --version
python3 -c "import PySide6, asciidoc3; print('All good!')"
pandoc --version
python3 src/main.py
```

## Update Later

**If used Git**:
```bash
cd AsciiDoctorArtisan
git pull
pip install -r requirements.txt --upgrade
```

**If got ZIP**:
1. Get new ZIP
2. Unzip
3. Type: `pip install -r requirements.txt --upgrade`

## Remove It

To delete:

1. Delete folder
2. Type: `pip uninstall PySide6 asciidoc3 pypandoc`

Settings are in hidden folder:
- **Windows**: `%APPDATA%/AsciiDocArtisan/`
- **Mac**: `~/Library/Application Support/AsciiDocArtisan/`
- **Linux**: `~/.config/AsciiDocArtisan/`

Delete folder to remove all.

## Next

Now:
1. Read [how-to-use.md](how-to-use.md)
2. Look at `templates/`
3. Start write!

## Need Help?

- Check README.md
- Look at GitHub issues
- Make new issue

---
**Reading level Grade 5.0 | Updated: 2025**
