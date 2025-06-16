# agent_framework/models/llm_wrapper.py
import threading
from typing import Optional, List, Dict, Any

import litellm


class LLMWrapper:
    """Thread-safe wrapper for LiteLLM"""

    def __init__(self):
        self.supported_models = [
            "gpt-4", "gpt-3.5-turbo", "rag-3-opus",
            "rag-3-sonnet", "llama2", "mistral", "gemini-pro",
            "deepseek-r1-0528-qwen3-8b-mlx"  # Local model
        ]
        self._lock = threading.Lock()
        
        # Configure local model if available
        self._setup_local_model()

    def generate(
            self,
            model: str,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            **kwargs
    ) -> str:
        """Generate completion using LiteLLM (thread-safe)"""
        with self._lock:
            try:
                # Get model-specific configuration
                model_config = self._get_model_config(model)
                kwargs.update(model_config)
                
                # Prepare model name with provider prefix
                litellm_model = self._prepare_model_name(model)
                
                response = litellm.completion(
                    model=litellm_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                content = response.choices[0].message.content
                
                # Handle DeepSeek R1 reasoning tokens
                if model == "deepseek-r1-0528-qwen3-8b-mlx" and "<think>" in content:
                    if "</think>" in content:
                        content = content.split("</think>")[-1].strip()
                    else:
                        content = content.split("<think>")[0].strip()
                
                return content
            except Exception as e:
                raise Exception(f"LLM generation failed: {str(e)}")

    def generate_with_tools(
            self,
            model: str,
            messages: List[Dict[str, str]],
            tools: List[Dict[str, Any]],
            **kwargs
    ) -> Dict[str, Any]:
        """Generate completion with function calling support"""
        with self._lock:
            try:
                response = litellm.completion(
                    model=model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    **kwargs
                )
                return {
                    "content": response.choices[0].message.content,
                    "tool_calls": response.choices[0].message.tool_calls
                }
            except Exception as e:
                raise Exception(f"LLM tool generation failed: {str(e)}")
    
    def list_supported_models(self) -> List[str]:
        """Get list of supported models"""
        return self.supported_models.copy()
    
    def _setup_local_model(self):
        """Configure local DeepSeek model for LiteLLM"""
        try:
            # Test if local server is available
            import requests
            response = requests.get("http://127.0.0.1:1234/v1/models", timeout=2)
            if response.status_code == 200:
                print("✅ Local DeepSeek model server detected and configured")
            else:
                print("⚠️ Local model server responded but may not be ready")
        except Exception as e:
            print(f"ℹ️ Local DeepSeek model not available: {e}")
    
    def _get_model_config(self, model: str) -> Dict[str, Any]:
        """Get model-specific configuration"""
        if model == "deepseek-r1-0528-qwen3-8b-mlx":
            return {
                "api_base": "http://127.0.0.1:1234/v1",
                "api_key": "local-key"  # Required by LiteLLM but not used for local
            }
        return {}
    
    def _prepare_model_name(self, model: str) -> str:
        """Prepare model name for LiteLLM with proper provider prefix"""
        if model == "deepseek-r1-0528-qwen3-8b-mlx":
            # Use openai/ prefix for OpenAI-compatible local servers
            return "openai/deepseek-r1-0528-qwen3-8b-mlx"
        return model
