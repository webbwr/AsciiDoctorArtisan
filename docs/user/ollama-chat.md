# AI Chat Guide

Use AI chat to get help while writing. Chat works on your computer. No internet needed.

## What You Need

1. **Ollama installed** - Get it from ollama.com
2. **At least one model** - Download a model first

## Set It Up

### Step 1: Get a Model

Open your terminal. Type this:

```bash
ollama pull gnokit/improve-grammer
```

Wait a few minutes. This gets the AI model. It is free.

### Step 2: Turn on AI

1. Open AsciiDoc Artisan
2. Click **Tools** menu
3. Click **AI Status**
4. Click **Settings**
5. Check the box for "Enable Ollama AI"
6. Pick your model from the list
7. Check "Enable AI chat interface"
8. Click **OK**

Now you see a chat bar above the status bar.

## Use Chat

### Send a Message

1. Type your question in the chat bar
2. Press Enter (or click Send)
3. Wait for the AI
4. Read the answer in the chat panel

The panel shows below the chat bar. You can hide it by unchecking the chat box in settings.

### Chat Modes

Chat has 4 modes. Pick the one you need.

**1. Document Q&A**
- Ask about your paper
- AI reads your work first
- Good for: "What is the main topic?"

**2. Syntax Help**
- Learn AsciiDoc rules
- AI knows all the markup
- Good for: "How do I make a table?"

**3. General Chat**
- Ask anything
- AI does not read your paper
- Good for: "Explain REST APIs"

**4. Editing Suggestions**
- Get writing help
- AI reads your work first
- Good for: "How can I improve this?"

### Change Modes

Use the dropdown in the chat bar. Pick a mode. Then type your question.

## Chat Controls

### Model Picker

The first dropdown shows your models. Click it to change models. The new model works right away.

### Clear Button

Click "Clear" to erase all chat history. This cannot be undone.

### Cancel Button

This shows when AI is working. Click it to stop the AI.

## Settings

Click Tools → AI Status → Settings to change:

**Chat Settings:**
- Enable/disable chat
- Max messages to save (10-500)
- Default mode
- Send document text to AI (on/off)

**Why Turn Off Document Sending?**

Some modes send your paper to the AI. The AI needs it to answer. But it all stays on your computer. No cloud.

Turn it off if you want. Then "Document Q&A" and "Editing" modes will not work as well.

## Tips

### Fast Answers

- Use short questions
- Pick the right mode
- Smaller models are faster

### Better Answers

- Be specific
- Give context
- Try rephrasing if unclear

### Save Chat

Chat saves automatically. It stays when you close the app. You can save up to 100 messages (or change this).

To export chat to a file:
- Right click in chat panel (future feature)
- Or copy/paste messages

## Troubleshooting

**Chat bar not showing?**
- Check AI is enabled
- Check a model is picked
- Restart the app

**"Ollama service not running" error?**

Open terminal. Type:
```bash
ollama serve
```

Leave this open. Try chat again.

**Slow responses?**

- Use a smaller model (gnokit/improve-grammer is fast)
- Close other programs
- Give your computer more RAM

**Wrong answers?**

- Try a different model
- Ask the question differently
- Use a different chat mode

## Privacy

All chat happens on your computer. Nothing goes to the internet.

Your chat history saves in:
- Linux: `~/.config/AsciiDoc Artisan/AsciiDocArtisan.json`
- Windows: `%APPDATA%/AsciiDoc Artisan/AsciiDocArtisan.json`
- Mac: `~/Library/Application Support/AsciiDoc Artisan/AsciiDocArtisan.json`

Delete this file to erase all history.

## Models We Like

**Fast (500MB-2GB):**
- gnokit/improve-grammer (best for most tasks)
- llama3.2:1b (very fast, less smart)

**Smart (4GB-8GB):**
- mistral:7b (very good writing)
- llama3:8b (great all-around)

**Expert (12GB+, needs good computer):**
- codellama:13b (best for code)
- mixtral:8x7b (best overall)

## Get Help

**Problems?** See docs/OLLAMA_SETUP.md for more help.

**Questions?** File an issue on GitHub.

**Updates?** Pull new models with `ollama pull <model-name>`

---

*Last updated: 2025-11-01*
*Version: 1.7.0*
