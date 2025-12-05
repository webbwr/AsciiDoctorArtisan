"""
Ollama Model Catalog - Available models for the model browser.

MA principle: Extracted data (~210 lines) from ollama_model_browser.py.
"""

from typing import Any

# Popular Ollama models with descriptions
AVAILABLE_MODELS: list[dict[str, Any]] = [
    {
        "name": "llama3.2:latest",
        "size": "2.0 GB",
        "description": "Meta's Llama 3.2 - Fast, efficient general-purpose model",
        "category": "General",
    },
    {
        "name": "llama3.2:1b",
        "size": "1.3 GB",
        "description": "Llama 3.2 1B parameter - Ultra lightweight",
        "category": "General",
    },
    {
        "name": "llama3.1:8b",
        "size": "4.7 GB",
        "description": "Llama 3.1 8B - Balanced performance and quality",
        "category": "General",
    },
    {
        "name": "llama3.1:70b",
        "size": "40 GB",
        "description": "Llama 3.1 70B - High quality, requires significant RAM",
        "category": "General",
    },
    {
        "name": "mistral:latest",
        "size": "4.4 GB",
        "description": "Mistral 7B - Excellent reasoning and instruction following",
        "category": "General",
    },
    {
        "name": "mixtral:8x7b",
        "size": "26 GB",
        "description": "Mixtral 8x7B - Mixture of experts, very capable",
        "category": "General",
    },
    {
        "name": "phi3:latest",
        "size": "2.2 GB",
        "description": "Microsoft Phi-3 - Small but powerful",
        "category": "General",
    },
    {
        "name": "phi3:medium",
        "size": "7.9 GB",
        "description": "Microsoft Phi-3 Medium - Better quality",
        "category": "General",
    },
    {
        "name": "gemma2:2b",
        "size": "1.6 GB",
        "description": "Google Gemma 2 2B - Lightweight and fast",
        "category": "General",
    },
    {
        "name": "gemma2:9b",
        "size": "5.5 GB",
        "description": "Google Gemma 2 9B - Balanced performance",
        "category": "General",
    },
    {
        "name": "gemma2:27b",
        "size": "16 GB",
        "description": "Google Gemma 2 27B - High quality",
        "category": "General",
    },
    {
        "name": "qwen2.5:latest",
        "size": "4.7 GB",
        "description": "Alibaba Qwen 2.5 - Strong multilingual support",
        "category": "General",
    },
    {
        "name": "qwen2.5:0.5b",
        "size": "397 MB",
        "description": "Qwen 2.5 0.5B - Extremely lightweight",
        "category": "General",
    },
    {
        "name": "qwen2.5:72b",
        "size": "41 GB",
        "description": "Qwen 2.5 72B - Top tier quality",
        "category": "General",
    },
    {
        "name": "qwen2.5-coder:latest",
        "size": "4.7 GB",
        "description": "Qwen 2.5 Coder - Optimized for programming",
        "category": "Code",
    },
    {
        "name": "qwen2.5-coder:1.5b",
        "size": "986 MB",
        "description": "Qwen 2.5 Coder 1.5B - Fast code completion",
        "category": "Code",
    },
    {
        "name": "qwen2.5-coder:7b",
        "size": "4.7 GB",
        "description": "Qwen 2.5 Coder 7B - Best balance for coding",
        "category": "Code",
    },
    {
        "name": "qwen2.5-coder:32b",
        "size": "18 GB",
        "description": "Qwen 2.5 Coder 32B - Top coding performance",
        "category": "Code",
    },
    {
        "name": "codellama:latest",
        "size": "3.8 GB",
        "description": "Meta CodeLlama - Specialized for code generation",
        "category": "Code",
    },
    {
        "name": "codellama:13b",
        "size": "7.4 GB",
        "description": "CodeLlama 13B - Better code understanding",
        "category": "Code",
    },
    {
        "name": "codellama:34b",
        "size": "19 GB",
        "description": "CodeLlama 34B - Advanced code generation",
        "category": "Code",
    },
    {
        "name": "deepseek-coder:6.7b",
        "size": "3.8 GB",
        "description": "DeepSeek Coder - Strong code generation",
        "category": "Code",
    },
    {
        "name": "starcoder2:3b",
        "size": "1.7 GB",
        "description": "StarCoder2 3B - Fast code completion",
        "category": "Code",
    },
    {
        "name": "starcoder2:15b",
        "size": "9.1 GB",
        "description": "StarCoder2 15B - High quality code generation",
        "category": "Code",
    },
    {
        "name": "dolphin-mixtral:8x7b",
        "size": "26 GB",
        "description": "Dolphin Mixtral - Uncensored, creative",
        "category": "Creative",
    },
    {
        "name": "neural-chat:latest",
        "size": "4.1 GB",
        "description": "Intel Neural Chat - Conversational AI",
        "category": "Chat",
    },
    {
        "name": "starling-lm:latest",
        "size": "4.1 GB",
        "description": "Starling LM - RLHF-trained for helpfulness",
        "category": "Chat",
    },
    {
        "name": "yi:latest",
        "size": "3.5 GB",
        "description": "Yi 6B - Bilingual (English/Chinese)",
        "category": "General",
    },
    {
        "name": "orca-mini:latest",
        "size": "1.9 GB",
        "description": "Orca Mini - Small but capable",
        "category": "General",
    },
    {
        "name": "tinyllama:latest",
        "size": "637 MB",
        "description": "TinyLlama 1.1B - Extremely small",
        "category": "General",
    },
    {
        "name": "llava:latest",
        "size": "4.5 GB",
        "description": "LLaVA - Vision + Language model",
        "category": "Vision",
    },
    {
        "name": "llava:13b",
        "size": "8.0 GB",
        "description": "LLaVA 13B - Better vision understanding",
        "category": "Vision",
    },
    {
        "name": "bakllava:latest",
        "size": "4.5 GB",
        "description": "BakLLaVA - Vision model based on Mistral",
        "category": "Vision",
    },
    {
        "name": "nomic-embed-text:latest",
        "size": "274 MB",
        "description": "Nomic Embed - Text embeddings model",
        "category": "Embeddings",
    },
    {
        "name": "mxbai-embed-large:latest",
        "size": "670 MB",
        "description": "MixedBread Embed - High quality embeddings",
        "category": "Embeddings",
    },
]
