# Quick Start Guide

Get started with AsciiDoc Artisan in 5 minutes!

**Version:** 2.0.6+ | **For:** New users

---

## Step 1: Install (2 minutes)

### Check What You Need

```bash
# Check Python version (need 3.11+)
python3 --version

# If too old, get new Python from python.org
```

### Install the App

**Easy Way (Linux/Mac):**
```bash
git clone https://github.com/webbwr/AsciiDoctorArtisan.git
cd AsciiDoctorArtisan
chmod +x install-asciidoc-artisan.sh
./install-asciidoc-artisan.sh
```

**Manual Way:**
```bash
pip install -r requirements.txt
```

### Install Required Tools

**Linux:**
```bash
sudo apt install pandoc wkhtmltopdf
```

**Mac:**
```bash
brew install pandoc wkhtmltopdf
```

**Windows:**
- Download Pandoc from pandoc.org
- Download wkhtmltopdf from wkhtmltopdf.org

---

## Step 2: Start the App (30 seconds)

```bash
# Start the app
make run

# Or
python3 src/main.py
```

**What you see:**
- Window opens (0.5-1 second)
- Two panels: editor (left) and preview (right)
- Menu bar at top
- Status bar at bottom

---

## Step 3: Create Your First Document (2 minutes)

### Option A: Use a Template (Easier!)

1. Click **File** → **New from Template**
2. Pick **Technical Report**
3. Fill in the form:
   - Title: "My First Document"
   - Author: Your name
   - Date: Today
4. Click **Create**
5. Done! You have a document!

### Option B: Start from Scratch

1. Click **File** → **New** (or Ctrl+N)
2. Type this:
```
= My First Document
Your Name
v1.0, 2025-11-20

== Introduction

This is my first AsciiDoc document!

== What I Learned

* AsciiDoc is easy
* The preview updates as I type
* I can export to PDF

== Conclusion

This was fun!
```

3. Watch the preview update on the right!

---

## Step 4: Use Key Features (1 minute)

### Try Auto-Complete

1. Type `==` (two equals)
2. Press **Ctrl+Space**
3. See suggestions!
4. Pick one
5. Press Enter

### Try Find & Replace

1. Press **Ctrl+F**
2. Type "easy"
3. See it highlight
4. Try **Ctrl+H** to replace

### Try Spell Check

1. Press **F7** (turns spell check on)
2. Type a wrong word: "helo wrld"
3. See red underlines
4. Right-click for suggestions

---

## Step 5: Save and Export (1 minute)

### Save Your Work

1. Press **Ctrl+S**
2. Pick a location
3. Type name: `my-doc.adoc`
4. Click Save

### Export to PDF

1. Click **File** → **Export** → **PDF**
2. Pick location
3. Click Save
4. Open the PDF!

---

## Next Steps

### Learn More Features

- **Git Support:** Version control built-in
- **AI Chat:** Get writing help (optional)
- **Templates:** Make your own templates
- **Themes:** Switch to dark mode (F11)

### Read Full Guide

See docs/user/user-guide.md for all features.

### Get Help

- **Questions:** docs/user/FAQ.md
- **Problems:** docs/user/troubleshooting.md
- **Bugs:** GitHub Issues

---

## Quick Reference

### Keyboard Shortcuts

| Keys | Action |
|------|--------|
| Ctrl+N | New document |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+F | Find |
| Ctrl+H | Replace |
| F7 | Toggle spell check |
| F11 | Dark mode |
| Ctrl++ | Bigger font |
| Ctrl+- | Smaller font |

### AsciiDoc Basics

| Syntax | Result |
|--------|--------|
| `= Title` | Document title |
| `== Heading` | Main heading |
| `=== Subheading` | Subheading |
| `*bold*` | **bold** text |
| `_italic_` | _italic_ text |
| `* item` | Bullet list |
| `. item` | Numbered list |

### Menu Quick Access

- **File Menu:** New, Open, Save, Export
- **Edit Menu:** Undo, Redo, Find, Replace
- **View Menu:** Dark Mode, Font Size
- **Tools Menu:** Spell Check, Syntax Check
- **Git Menu:** Commit, Push, Pull (if in Git folder)

---

## Common First-Time Questions

### "The preview is not updating!"

Wait 500ms (half second). It waits for you to stop typing. This is normal!

### "Git menu is grayed out!"

You are not in a Git folder. Run `git init` first, or open a Git folder.

### "Where are my settings saved?"

- Linux: `~/.config/AsciiDocArtisan/`
- Windows: `%APPDATA%/AsciiDocArtisan/`
- Mac: `~/Library/Application Support/AsciiDocArtisan/`

### "Can I use my old AsciiDoc files?"

Yes! Just open them. File → Open → pick your .adoc file.

### "How do I learn AsciiDoc syntax?"

1. Use auto-complete (Ctrl+Space)
2. Check the preview
3. Use templates
4. Read asciidoc.org documentation

---

## Tips for Beginners

1. **Start with template** - Easier than blank page
2. **Use auto-complete** - Helps you learn syntax
3. **Watch preview** - See what it looks like
4. **Save often** - Ctrl+S is your friend
5. **Try dark mode** - F11 for easy on eyes
6. **Enable spell check** - F7 to avoid typos

---

## You're Ready!

You now know how to:
- ✅ Start the app
- ✅ Create documents
- ✅ Use key features
- ✅ Save and export
- ✅ Get help

**Have fun writing!** 🎉

---

**What's Next?**

- Try all the templates
- Export to different formats
- Set up Git if you want versions
- Try AI chat if you want help
- Read the full user guide

**Need help?** Check FAQ.md or troubleshooting.md!
