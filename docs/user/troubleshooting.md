# Troubleshooting Guide

Quick help for common problems with AsciiDoc Artisan.

**Version:** 2.0.6+ | **Last Updated:** November 20, 2025

---

## Installation Issues

### Python Version Problems

**Problem:** Error says "Python 3.11+ required"

**Solution:**
1. Check your Python: `python3 --version`
2. Need Python 3.11 or newer
3. Install Python 3.11+ from python.org
4. Try again

**Problem:** Package install fails

**Solution:**
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### Missing Dependencies

**Problem:** "Pandoc not found"

**Solution:**
- **Linux:** `sudo apt install pandoc`
- **Mac:** `brew install pandoc`
- **Windows:** Download from pandoc.org
- Check install: `pandoc --version`

**Problem:** "wkhtmltopdf not found" or PDF export fails

**Solution:**
- **Linux:** `sudo apt install wkhtmltopdf`
- **Mac:** `brew install wkhtmltopdf`
- **Windows:** Download from wkhtmltopdf.org
- Check install: `wkhtmltopdf --version`

### PySide6 Installation Fails

**Problem:** Cannot install PySide6

**Solution:**
```bash
# Try installing separately
pip install --upgrade pip
pip install PySide6>=6.9.0

# If still fails, check system requirements
# Need: C++ compiler, Qt dependencies
```

---

## Startup Issues

### Application Won't Start

**Problem:** Window does not appear

**Check:**
1. Any error messages in terminal?
2. Is Qt platform plugin available?
3. GPU drivers installed?

**Solution:**
```bash
# Run with debug output
python3 src/main.py

# Try without GPU acceleration
QT_QPA_PLATFORM=offscreen python3 src/main.py

# Check Qt plugins
python3 -c "from PySide6 import QtWidgets; print('Qt OK')"
```

**Problem:** "No Qt platform plugin" error

**Solution:**
```bash
# Linux: Install Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Set Qt platform explicitly
export QT_QPA_PLATFORM=xcb
python3 src/main.py
```

### Slow Startup

**Problem:** Takes more than 5 seconds to start

**Normal startup:** 0.5-1.0 seconds

**Causes:**
- First run (creating settings)
- GPU detection (cached after first run)
- Large recent files list
- Slow disk

**Solutions:**
1. Wait for GPU cache (24 hours)
2. Clear recent files: Settings → Clear Recent
3. Use SSD if possible
4. Check GPU cache: `~/.cache/asciidoc_artisan/`

---

## Runtime Issues

### GPU Detection Fails

**Problem:** "No GPU detected" or "Using CPU fallback"

**Check GPU:**
```bash
# NVIDIA
nvidia-smi

# AMD
rocm-smi

# Intel
glxinfo | grep "OpenGL renderer"
```

**Solution:**
1. Install GPU drivers
2. Delete GPU cache: `rm -rf ~/.cache/asciidoc_artisan/`
3. Restart application
4. **Note:** App works fine without GPU (just slower)

**Problem:** Wrong GPU detected

**Solution:**
- Delete cache: `rm -rf ~/.cache/asciidoc_artisan/gpu_detection.json`
- Restart application
- GPU re-detected automatically

### Preview Not Updating

**Problem:** Preview shows old content

**Solutions:**
1. Wait 500ms (debounce delay)
2. Click in preview panel to focus
3. Restart application if stuck
4. Check preview handler status

**Problem:** Preview shows errors

**Check:**
1. Valid AsciiDoc syntax?
2. Asciidoc3 installed? `pip show asciidoc3`
3. Check logs for errors

---

## Export Issues

### PDF Export Fails

**Problem:** "Failed to export PDF"

**Causes:**
- wkhtmltopdf not installed
- Invalid content
- Permission error

**Solutions:**
```bash
# Check wkhtmltopdf
which wkhtmltopdf
wkhtmltopdf --version

# Install if missing
sudo apt install wkhtmltopdf  # Linux
brew install wkhtmltopdf      # Mac

# Try manual export
wkhtmltopdf test.html test.pdf
```

### DOCX Export Issues

**Problem:** DOCX export fails or formatting wrong

**Solution:**
1. Check Pandoc: `pandoc --version`
2. Pandoc 2.0+ required
3. Update: `sudo apt install pandoc` (Linux)
4. Complex tables may not convert perfectly

### HTML Export

**Problem:** HTML missing styles

**Solution:**
- Styles embedded in HTML
- Open in web browser to verify
- Check asciidoc3 installation

---

## Git Integration Issues

### Git Options Disabled

**Problem:** Git menu items grayed out

**Causes:**
- Not in Git repository
- Git not installed
- No .git folder

**Solutions:**
```bash
# Check if in Git repo
git status

# Initialize repo if needed
git init
git config user.name "Your Name"
git config user.email "you@example.com"

# Check Git installed
git --version
```

### Commit Fails

**Problem:** "Git commit failed"

**Check:**
1. Staged files? `git status`
2. User name set? `git config user.name`
3. Email set? `git config user.email`
4. Valid commit message?

**Solution:**
```bash
# Set Git user
git config user.name "Your Name"
git config user.email "your@email.com"

# Try manual commit
git add .
git commit -m "Test commit"
```

### Push/Pull Fails

**Problem:** "Permission denied" or "Authentication failed"

**Solution:**
1. Check remote: `git remote -v`
2. Set up SSH keys or HTTPS token
3. Test connection: `git fetch`
4. See Git documentation for auth setup

---

## AI Integration Issues

### Ollama Not Working

**Problem:** "Ollama not available" or AI chat disabled

**Check:**
```bash
# Is Ollama running?
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

**Solution:**
1. Install Ollama from ollama.com
2. Pull model: `ollama pull llama2`
3. Start service: `ollama serve`
4. Enable in Settings → AI

**Problem:** Chat responses slow or timeout

**Solutions:**
- Use smaller model (phi3 instead of llama2)
- Increase timeout in settings
- Check CPU/RAM usage
- GPU helps but not required

### Claude API Errors

**Problem:** "Invalid API key" or "Authentication failed"

**Solution:**
1. Get API key from console.anthropic.com
2. Enter in Settings → Claude API
3. Key stored securely in system keyring
4. Check key is active and has credits

**Problem:** "Rate limit exceeded"

**Solution:**
- Wait a few minutes
- Reduce request frequency
- Upgrade API plan if needed

---

## Feature-Specific Issues

### Auto-Complete Not Working

**Problem:** Ctrl+Space does nothing

**Check:**
1. Cursor in editor?
2. Valid context (after `=`, `*`, etc.)?
3. Auto-complete enabled in settings?

**Solution:**
- Enable: Settings → Editor → Auto-Complete
- Try different position in text
- Restart if stuck

### Syntax Checking Not Showing Errors

**Problem:** No error highlighting

**Solution:**
1. Enable: F8 or Tools → Syntax Check
2. Wait for validation (runs on typing)
3. Errors show as red squiggles
4. Press F8 to navigate errors

### Spell Check Not Working

**Problem:** No red underlines for typos

**Solution:**
1. Enable: F7 or Tools → Toggle Spell Check
2. Check language: Settings → Spell Check
3. Install language dictionary if needed
4. Right-click word for suggestions

### Find & Replace Issues

**Problem:** Find not working or wrong results

**Check:**
1. Search text correct?
2. Case sensitive enabled?
3. Regex mode?
4. Wrap around enabled?

**Solution:**
- Try toggling case sensitivity
- Disable regex if not needed
- Check search starts at cursor
- Use Ctrl+F to open find bar

---

## Performance Issues

### High CPU Usage

**Causes:**
- Preview rendering large document
- Real-time syntax checking
- Multiple Git operations
- No GPU acceleration

**Solutions:**
1. Disable preview temporarily
2. Use GPU if available
3. Close other applications
4. Reduce document size
5. Disable syntax check for large files

### High Memory Usage

**Normal:** 200-500 MB
**High:** > 1 GB

**Causes:**
- Very large document
- Many recent files
- Preview cache
- Memory leak (rare)

**Solutions:**
1. Close and reopen application
2. Clear recent files
3. Split large documents
4. Report if memory keeps growing

### Laggy Preview

**Problem:** Preview updates slowly

**Solutions:**
1. Enable GPU acceleration (auto-detected)
2. Reduce document size
3. Increase debounce delay: Settings → Preview
4. Close other apps
5. Use faster computer :)

---

## File Issues

### Cannot Open File

**Problem:** "Failed to open file" error

**Causes:**
- File does not exist
- No read permission
- File locked by another program
- Unsupported format

**Solutions:**
```bash
# Check file exists
ls -l /path/to/file.adoc

# Check permissions
chmod 644 /path/to/file.adoc

# Close file in other programs
```

### Cannot Save File

**Problem:** "Failed to save file" error

**Causes:**
- No write permission
- Disk full
- File locked
- Invalid path

**Solutions:**
```bash
# Check disk space
df -h

# Check permissions
ls -ld /path/to/directory

# Save to different location
# Use File → Save As
```

---

## Platform-Specific Issues

### Linux Issues

**Problem:** Missing libraries

**Solution:**
```bash
# Install Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4

# Install dev tools
sudo apt install python3-dev build-essential
```

### macOS Issues

**Problem:** "App from unidentified developer"

**Solution:**
1. System Preferences → Security & Privacy
2. Click "Open Anyway"
3. Or run from terminal first

**Problem:** Permissions for keychain

**Solution:**
- Grant permissions when prompted
- Needed for Claude API key storage

### Windows Issues

**Problem:** DLL errors on startup

**Solution:**
- Install Visual C++ Redistributable
- Download from microsoft.com
- Restart after install

**Problem:** Git not found

**Solution:**
- Install Git from git-scm.com
- Add to PATH during install
- Restart application

---

## Getting More Help

### Check Logs

**Location:**
- Linux: `~/.local/share/AsciiDocArtisan/logs/`
- Windows: `%APPDATA%/AsciiDocArtisan/logs/`
- macOS: `~/Library/Application Support/AsciiDocArtisan/logs/`

**View logs:**
```bash
tail -f ~/.local/share/AsciiDocArtisan/logs/asciidoc_artisan.log
```

### Run Diagnostics

```bash
# Check Python version
python3 --version

# Check dependencies
pip list | grep -E "PySide6|asciidoc3|pypandoc|pymupdf"

# Check external tools
pandoc --version
wkhtmltopdf --version
git --version
ollama --version  # if using AI

# Check GPU
nvidia-smi  # NVIDIA
rocm-smi    # AMD
```

### Report Bug

**Before reporting:**
1. Check this troubleshooting guide
2. Check existing issues on GitHub
3. Try on latest version

**Include:**
- Version: `python3 src/main.py --version`
- Platform: Linux/Mac/Windows
- Python version
- Error message (full text)
- Steps to reproduce
- Logs (if relevant)

**Report at:**
- GitHub Issues: https://github.com/webbwr/AsciiDoctorArtisan/issues

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'X'"

**Meaning:** Python package not installed

**Fix:** `pip install X`

### "Pandoc not found"

**Meaning:** Pandoc not installed or not in PATH

**Fix:** Install Pandoc (see above)

### "GPU detection failed, using CPU fallback"

**Meaning:** No GPU found, app uses CPU

**Fix:** Install GPU drivers or ignore (works fine on CPU)

### "Failed to connect to Ollama"

**Meaning:** Ollama service not running

**Fix:** Run `ollama serve` in terminal

### "API key invalid"

**Meaning:** Claude API key wrong or expired

**Fix:** Check key in console.anthropic.com

### "Permission denied"

**Meaning:** No file/folder permission

**Fix:** Check file permissions with `ls -l`

---

## Still Need Help?

1. **Documentation:** docs/user/user-guide.md
2. **FAQ:** docs/user/FAQ.md
3. **GitHub Issues:** Report bugs and get help
4. **Community:** GitHub Discussions

**Remember:** Most issues are solved by:
- Checking dependencies installed
- Restarting the application
- Checking file permissions
- Reading error messages carefully

---

**Tip:** Use `make help` to see all available commands for development and testing.
