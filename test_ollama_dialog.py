#!/usr/bin/env python3
"""Test script to verify Ollama integration works as in the dialogs.py code."""

import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama_load():
    """Test loading Ollama models like the dialog does."""
    try:
        import ollama
        logger.info("✓ Ollama library imported successfully")

        try:
            response = ollama.list()
            logger.info(f"✓ Ollama API response type: {type(response)}")

            # Handle both old API (dict with "models" key) and new API (direct list)
            if isinstance(response, dict):
                models_data = response.get("models", [])
                logger.info(f"✓ Using dict API - found {len(models_data)} models")
            elif hasattr(response, 'models'):
                models_data = response.models if isinstance(response.models, list) else list(response.models)
                logger.info(f"✓ Using new API with .models attribute - found {len(models_data)} models")
            else:
                # Assume response is the models list directly
                models_data = response if isinstance(response, list) else []
                logger.info(f"✓ Using direct list API - found {len(models_data)} models")

            if not models_data:
                logger.warning("⚠️ No models installed")
                return False

            # Extract model names properly
            models = []
            for model in models_data:
                # Handle both dict (old API) and object (new API) formats
                if isinstance(model, dict):
                    name = model.get("name") or model.get("model", "Unknown")
                elif hasattr(model, 'model'):
                    name = model.model
                elif hasattr(model, 'name'):
                    name = model.name
                else:
                    name = str(model)

                models.append(name)
                logger.info(f"  - {name}")

            logger.info(f"✓ Successfully loaded {len(models)} Ollama models")
            return True

        except Exception as e:
            logger.error(f"❌ Ollama service error: {type(e).__name__}: {e}", exc_info=True)
            return False

    except ImportError as e:
        logger.error(f"❌ Ollama import error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_ollama_load()
    sys.exit(0 if success else 1)
