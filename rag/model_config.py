"""
Model configuration for RAG system
Switch between OpenAI and local DeepSeek model
"""
import os

# Model selection - DeepSeek as default
USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "true").lower() == "true"

# Model configurations
MODELS = {
    "openai": {
        "name": "gpt-3.5-turbo",
        "description": "OpenAI GPT-3.5 Turbo"
    },
    "local": {
        "name": "deepseek-r1-0528-qwen3-8b-mlx", 
        "description": "Local DeepSeek R1 (Qwen3 8B MLX)"
    }
}

def get_current_model():
    """Get the currently configured model"""
    if USE_LOCAL_MODEL:
        return MODELS["local"]
    else:
        return MODELS["openai"]

def get_model_name():
    """Get the model name for LLM calls"""
    return get_current_model()["name"]

def print_model_info():
    """Print current model configuration"""
    current = get_current_model()
    print(f"🤖 Using model: {current['description']} ({current['name']})")
    if USE_LOCAL_MODEL:
        print("🏠 Running locally at http://127.0.0.1:1234")
    else:
        print("☁️ Using OpenAI API")