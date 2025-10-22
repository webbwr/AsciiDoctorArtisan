# Claude AI Integration for AsciiDoc Artisan

This directory contains the Node.js service that provides AI-powered features to AsciiDoc Artisan using the @anthropic-ai/claude-agent-sdk.

## Features

- **Generate AsciiDoc Content**: Create new documentation from prompts
- **Improve Existing Content**: Enhance and refine your AsciiDoc documents
- **Format Conversion**: Convert between Markdown, HTML, and AsciiDoc
- **Generate Outlines**: Create structured documentation outlines
- **AsciiDoc Help**: Get instant answers about AsciiDoc syntax

## Setup

1. **Install Node.js** (v18 or higher)
   ```bash
   # Check if Node.js is installed
   node --version
   ```

2. **Install Dependencies**
   ```bash
   cd claude-integration
   npm install
   ```

3. **Configure API Key**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your Anthropic API key
   # Get your API key from: https://console.anthropic.com/
   ```

4. **Start the Service**
   ```bash
   # Development mode (with auto-reload)
   npm run dev

   # Production mode
   npm start
   ```

The service will start on port 3000 by default.

## Integration with AsciiDoc Artisan

The Python application can now use the `claude_client.py` module to interact with Claude:

```python
from claude_client import get_claude_client

# Get the client instance
claude = get_claude_client()

# Check if service is available
if claude.is_available():
    # Generate content
    success, content, error = claude.generate_asciidoc(
        "Create a getting started guide for Python",
        context="For beginners"
    )

    if success:
        print(content)
```

## API Endpoints

### Health Check
- **GET** `/health`
- Returns service status and Claude availability

### Generate AsciiDoc
- **POST** `/api/generate-asciidoc`
- Body: `{ "prompt": "...", "context": "..." }`

### Improve AsciiDoc
- **POST** `/api/improve-asciidoc`
- Body: `{ "content": "...", "instruction": "..." }`

### Convert Format
- **POST** `/api/convert-format`
- Body: `{ "content": "...", "fromFormat": "markdown", "toFormat": "asciidoc" }`

### Generate Outline
- **POST** `/api/generate-outline`
- Body: `{ "topic": "...", "style": "technical" }`

### AsciiDoc Help
- **POST** `/api/asciidoc-help`
- Body: `{ "question": "..." }`

## Running as a System Service

For production use, you can run this as a system service:

### Linux (systemd)
Create `/etc/systemd/system/asciidoc-claude.service`:

```ini
[Unit]
Description=AsciiDoc Artisan Claude Integration
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/claude-integration
ExecStart=/usr/bin/node server.js
Restart=on-failure
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### Windows (Task Scheduler)
1. Create a batch file `start-claude.bat`:
   ```batch
   cd /d "C:\path\to\claude-integration"
   node server.js
   ```
2. Use Task Scheduler to run at startup

## Troubleshooting

1. **Service not available**: Make sure Node.js service is running
2. **API errors**: Check your Anthropic API key in `.env`
3. **Connection refused**: Verify the service port (default: 3000)

## Development

To modify the Claude integration:

1. Edit `server.js` to add new endpoints
2. Update `claude_client.py` to add corresponding Python methods
3. Test thoroughly before integrating with the main app