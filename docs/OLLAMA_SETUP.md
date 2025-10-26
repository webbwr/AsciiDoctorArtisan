# Ollama Local AI Setup

**Date**: October 26, 2025
**Status**: ✅ Installed and Configured
**Version**: Ollama 0.12.6
**Model**: phi3:mini (3.8B parameters)

---

## What Was Done

### Installation

Ollama was installed successfully on WSL2 Ubuntu:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Service Status

Ollama is running as a system service:
- **Service**: `ollama.service`
- **API Endpoint**: `http://127.0.0.1:11434`
- **Status**: Active and running
- **GPU**: NVIDIA GPU detected and available

### Model Installed

**phi3:mini** - A fast, efficient model:
- **Size**: 2.2 GB
- **Parameters**: 3.8B
- **Speed**: ~95 tokens/second
- **Purpose**: Fast local AI for document assistance

### Test Results

Successfully tested with the prompt "What is AsciiDoc?":
- Model loaded in ~29 seconds (first run)
- Generated 106 tokens in 1.1 seconds
- Evaluation rate: 94.92 tokens/s
- Response was accurate and helpful

---

## How to Use

### Command Line

```bash
# Run a prompt
ollama run phi3:mini "Your question here"

# List installed models
ollama list

# Check service status
systemctl status ollama
```

### Python Integration (Future)

To integrate with AsciiDoc Artisan, install the Python library:

```bash
pip install ollama-python
```

Example usage:
```python
import ollama

response = ollama.generate(
    model='phi3:mini',
    prompt='Improve this text: ...'
)
print(response['response'])
```

---

## Performance

### Speed Metrics

| Metric | Value |
|--------|-------|
| Load time | 29.1s (first run, cached after) |
| Eval speed | 94.92 tokens/s |
| GPU | NVIDIA (detected and used) |
| Memory | ~2.2GB for model |

### Comparison

- **Local (Ollama)**: ~95 tokens/s, no network, private
- **Cloud API**: Variable latency, requires internet
- **Recommendation**: Use Ollama for privacy-sensitive work

---

## Next Steps

### Immediate

1. **Test other models** (optional)
   - `llama3:8b` - Better quality, slower
   - `codellama:7b` - Good for code

2. **Monitor memory usage**
   - Check RAM with larger models
   - Ensure system has enough resources

### Future Integration

1. **Add to AsciiDoc Artisan**
   - Create settings toggle
   - Add AI features menu
   - Implement grammar check
   - Add text improvement

2. **Features to Add**
   - Grammar checking
   - Text simplification
   - Format conversion help
   - Table extraction improvement

3. **UI Integration**
   - Settings checkbox for "Enable Local AI"
   - Model selection dropdown
   - Privacy-focused messaging

---

## System Requirements

### Minimum

- **RAM**: 4GB (for phi3:mini)
- **Disk**: 3GB for model
- **CPU**: Any modern CPU
- **GPU**: Optional (speeds up generation)

### Recommended

- **RAM**: 8GB+
- **Disk**: 10GB (for multiple models)
- **CPU**: 4+ cores
- **GPU**: NVIDIA/AMD (10x faster)

---

## Models Available

### Small & Fast (Good Start)

- **phi3:mini** (3.8B) - ✅ Installed
  - Size: 2.2GB
  - Speed: Very fast (~95 tokens/s)
  - Quality: Good for basic tasks

### Medium (Better Quality)

- **llama3:8b**
  - Size: ~4.7GB
  - Speed: Medium (~50 tokens/s)
  - Quality: Better understanding

### Large (Best Quality)

- **llama3:70b**
  - Size: ~40GB
  - Speed: Slow (~10 tokens/s)
  - Quality: Excellent
  - Requires: 64GB+ RAM

---

## Privacy & Security

### Benefits

- **Private**: All processing happens locally
- **Offline**: Works without internet
- **Secure**: Your documents never leave your computer
- **Free**: No API costs

### Best Practices

- Use local AI for sensitive documents
- Keep Ollama updated for security patches
- Monitor system resources
- Enable firewall (Ollama only binds to localhost)

---

## Troubleshooting

### Service Not Running

```bash
# Start the service
sudo systemctl start ollama

# Enable auto-start
sudo systemctl enable ollama
```

### Model Not Found

```bash
# Pull the model
ollama pull phi3:mini

# List available models
ollama list
```

### Slow Performance

1. Check if GPU is being used
2. Consider smaller model
3. Close other applications
4. Ensure enough RAM available

---

## Resources

**Official Docs**:
- https://ollama.ai/
- https://github.com/ollama/ollama

**Model Library**:
- https://ollama.ai/library

**Python Integration**:
- https://github.com/ollama/ollama-python

---

## Summary

✅ **Ollama installed and working**
✅ **phi3:mini model downloaded**
✅ **GPU acceleration enabled**
✅ **Service running automatically**
✅ **Ready for integration**

**Next**: Integrate into AsciiDoc Artisan UI (Phase 1 from TIER_3_RESEARCH.md)

---

**Reading Level**: Grade 5.0
**For**: Development and user reference
**Status**: Setup complete, ready for integration
