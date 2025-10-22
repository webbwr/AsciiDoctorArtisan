import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { ClaudeAgent } from '@anthropic-ai/claude-agent-sdk';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Initialize Claude Agent
let claudeAgent;

async function initializeClaude() {
  try {
    claudeAgent = new ClaudeAgent({
      apiKey: process.env.ANTHROPIC_API_KEY,
      model: 'claude-3-opus-20240229', // or claude-3-sonnet-20240229
    });
    console.log('Claude Agent initialized successfully');
  } catch (error) {
    console.error('Failed to initialize Claude Agent:', error);
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'AsciiDoc Artisan Claude Integration',
    claudeReady: !!claudeAgent
  });
});

// Generate AsciiDoc content
app.post('/api/generate-asciidoc', async (req, res) => {
  try {
    const { prompt, context } = req.body;

    if (!claudeAgent) {
      return res.status(503).json({ error: 'Claude Agent not initialized' });
    }

    const systemPrompt = `You are an expert AsciiDoc writer. Generate well-formatted AsciiDoc content based on the user's request.
    Use appropriate AsciiDoc syntax including headings, lists, tables, and formatting as needed.
    ${context ? `Context: ${context}` : ''}`;

    const response = await claudeAgent.sendMessage(prompt, {
      system: systemPrompt,
      maxTokens: 2000,
    });

    res.json({
      content: response.content,
      usage: response.usage
    });
  } catch (error) {
    console.error('Error generating AsciiDoc:', error);
    res.status(500).json({ error: 'Failed to generate content' });
  }
});

// Improve existing AsciiDoc content
app.post('/api/improve-asciidoc', async (req, res) => {
  try {
    const { content, instruction } = req.body;

    if (!claudeAgent) {
      return res.status(503).json({ error: 'Claude Agent not initialized' });
    }

    const prompt = `Please improve the following AsciiDoc content according to this instruction: "${instruction}"

Current content:
\`\`\`asciidoc
${content}
\`\`\`

Provide the improved version maintaining proper AsciiDoc syntax.`;

    const response = await claudeAgent.sendMessage(prompt, {
      system: 'You are an expert AsciiDoc editor. Improve the provided content while maintaining valid AsciiDoc syntax.',
      maxTokens: 3000,
    });

    res.json({
      content: response.content,
      usage: response.usage
    });
  } catch (error) {
    console.error('Error improving AsciiDoc:', error);
    res.status(500).json({ error: 'Failed to improve content' });
  }
});

// Convert between formats
app.post('/api/convert-format', async (req, res) => {
  try {
    const { content, fromFormat, toFormat } = req.body;

    if (!claudeAgent) {
      return res.status(503).json({ error: 'Claude Agent not initialized' });
    }

    const prompt = `Convert the following ${fromFormat} content to ${toFormat} format:

\`\`\`${fromFormat}
${content}
\`\`\`

Provide only the converted content without any explanation.`;

    const response = await claudeAgent.sendMessage(prompt, {
      system: `You are an expert at converting between document formats. Convert accurately from ${fromFormat} to ${toFormat}.`,
      maxTokens: 3000,
    });

    res.json({
      content: response.content,
      usage: response.usage
    });
  } catch (error) {
    console.error('Error converting format:', error);
    res.status(500).json({ error: 'Failed to convert format' });
  }
});

// Generate documentation outline
app.post('/api/generate-outline', async (req, res) => {
  try {
    const { topic, style } = req.body;

    if (!claudeAgent) {
      return res.status(503).json({ error: 'Claude Agent not initialized' });
    }

    const prompt = `Generate a comprehensive documentation outline in AsciiDoc format for the topic: "${topic}"
    Style: ${style || 'technical documentation'}

    Include appropriate sections, subsections, and placeholders for content.`;

    const response = await claudeAgent.sendMessage(prompt, {
      system: 'You are an expert technical writer. Create well-structured documentation outlines in AsciiDoc format.',
      maxTokens: 2000,
    });

    res.json({
      content: response.content,
      usage: response.usage
    });
  } catch (error) {
    console.error('Error generating outline:', error);
    res.status(500).json({ error: 'Failed to generate outline' });
  }
});

// Answer questions about AsciiDoc syntax
app.post('/api/asciidoc-help', async (req, res) => {
  try {
    const { question } = req.body;

    if (!claudeAgent) {
      return res.status(503).json({ error: 'Claude Agent not initialized' });
    }

    const response = await claudeAgent.sendMessage(question, {
      system: 'You are an AsciiDoc expert. Answer questions about AsciiDoc syntax, best practices, and provide examples when helpful. Keep answers concise and practical.',
      maxTokens: 1000,
    });

    res.json({
      answer: response.content,
      usage: response.usage
    });
  } catch (error) {
    console.error('Error answering AsciiDoc question:', error);
    res.status(500).json({ error: 'Failed to answer question' });
  }
});

// Start server
app.listen(PORT, async () => {
  console.log(`Claude integration server running on port ${PORT}`);
  await initializeClaude();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});