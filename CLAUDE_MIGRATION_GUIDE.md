# Claude Agent SDK Migration Guide for AsciiDoc Artisan

This guide explains how to integrate the @anthropic-ai/claude-agent-sdk into AsciiDoc Artisan, adding AI-powered features to enhance your documentation workflow.

## Overview

Since AsciiDoc Artisan is a Python/PySide6 application and the claude-agent-sdk is a Node.js package, we've created a hybrid architecture:

1. **Node.js Service**: A REST API server using @anthropic-ai/claude-agent-sdk
2. **Python Client**: A module that communicates with the Node.js service
3. **GUI Integration**: Menu items and dialogs in the AsciiDoc Artisan interface

## Quick Start

### 1. Set Up the Node.js Service

```bash
# Navigate to the Claude integration directory
cd claude-integration

# Install dependencies (including @anthropic-ai/claude-agent-sdk)
npm install

# Create your environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get one from: https://console.anthropic.com/
```

### 2. Start the Claude Service

```bash
# Development mode
npm run dev

# Or production mode
npm start
```

The service will run on http://localhost:3000

### 3. Update Python Dependencies

```bash
# Install the updated Python requirements
pip install -r requirements.txt
```

### 4. Test the Integration

```python
# Test the Claude client
python -c "from claude_client import get_claude_client; print(get_claude_client().is_available())"
```

## Features Added

The integration provides these AI-powered features:

1. **Generate AsciiDoc Content**: Create documentation from prompts
2. **Improve Existing Content**: Enhance clarity and structure
3. **Generate Outlines**: Create structured documentation templates
4. **AsciiDoc Syntax Help**: Get instant answers about AsciiDoc

## Integration Methods

### Method 1: Full GUI Integration (Recommended)

Add the Claude menu to your AsciiDoc Artisan:

```python
# In adp.py, add this import at the top
from claude_integration_example import integrate_claude

# In the AsciiDocEditor.__init__ method, add:
try:
    self.claude_integration = integrate_claude(self)
except Exception as e:
    print(f"Claude integration not available: {e}")
```

### Method 2: Simple API Usage

Use the Claude client directly in your code:

```python
from claude_client import get_claude_client

claude = get_claude_client()

# Generate content
success, content, error = claude.generate_asciidoc(
    prompt="Create a REST API documentation template",
    context="For a Python Flask application"
)

if success:
    print(content)
```

### Method 3: Command-Line Tool

Create a simple CLI tool:

```python
#!/usr/bin/env python
import sys
from claude_client import get_claude_client

if len(sys.argv) < 2:
    print("Usage: claude-doc <prompt>")
    sys.exit(1)

claude = get_claude_client()
success, content, error = claude.generate_asciidoc(" ".join(sys.argv[1:]))

if success:
    print(content)
else:
    print(f"Error: {error}", file=sys.stderr)
    sys.exit(1)
```

## Architecture Details

### Node.js Service (claude-integration/server.js)

- Uses Express.js for the REST API
- Integrates @anthropic-ai/claude-agent-sdk
- Provides endpoints for various AI operations
- Handles authentication and error management

### Python Client (claude_client.py)

- Provides a clean Python interface
- Handles HTTP communication with the service
- Includes error handling and timeouts
- Thread-safe singleton pattern

### GUI Integration (claude_integration_example.py)

- Adds a "Claude AI" menu to the editor
- Uses Qt threads for non-blocking operations
- Integrates seamlessly with the editor's text handling

## Running in Production

### As a System Service (Linux)

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/asciidoc-claude.service
   ```

2. Add the service configuration (see claude-integration/README.md)

3. Enable and start:
   ```bash
   sudo systemctl enable asciidoc-claude
   sudo systemctl start asciidoc-claude
   ```

### As a Windows Service

1. Install node-windows:
   ```bash
   cd claude-integration
   npm install -g node-windows
   ```

2. Create a service installer script
3. Run as Administrator

## Troubleshooting

### Service Not Available

1. Check if Node.js service is running:
   ```bash
   curl http://localhost:3000/health
   ```

2. Check logs:
   ```bash
   # In the claude-integration directory
   npm start
   ```

### API Key Issues

1. Verify your .env file exists and contains:
   ```
   ANTHROPIC_API_KEY=sk-ant-api...
   ```

2. Ensure the key has proper permissions

### Connection Errors

1. Check firewall settings
2. Verify port 3000 is not in use
3. Try a different port in .env

## Future Enhancements

Consider these additional features:

1. **Auto-completion**: Use Claude for intelligent code/text completion
2. **Grammar Check**: Validate technical writing
3. **Translation**: Convert documentation to multiple languages
4. **Diagram Generation**: Create PlantUML/Mermaid diagrams from descriptions
5. **Interactive Chat**: Add a chat panel for continuous AI assistance

## Security Considerations

1. **API Key**: Never commit .env files to Git
2. **Rate Limiting**: Implement request throttling
3. **Input Validation**: Sanitize user inputs
4. **HTTPS**: Use SSL in production environments

## Cost Management

The Claude API has usage-based pricing. Consider:

1. Implementing usage tracking
2. Setting up spending alerts
3. Caching responses when appropriate
4. Using appropriate models (Sonnet vs Opus)

## Support

For issues or questions:

1. Check the logs in both Python and Node.js
2. Verify the Claude service health endpoint
3. Review the Anthropic API documentation
4. Open an issue in the GitHub repository

## Next Steps

1. Start the Claude service
2. Test the integration
3. Customize the features for your workflow
4. Consider contributing improvements back to the project

Happy documenting with AI assistance!