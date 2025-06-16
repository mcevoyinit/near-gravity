# Local Model Setup Guide

## Overview

The NearGravity RAG system now supports local DeepSeek R1 models as an alternative to OpenAI API calls.

## Configuration

### Using OpenAI (Default)
```bash
python3 standalone_coffee_demo.py
# Uses: gpt-3.5-turbo via OpenAI API
```

### Using Local DeepSeek Model
```bash
USE_LOCAL_MODEL=true python3 standalone_coffee_demo.py  
# Uses: deepseek-r1-0528-qwen3-8b-mlx via http://127.0.0.1:1234
```

## Local Model Server Setup

To use the local DeepSeek model, you need to have the server running at `http://127.0.0.1:1234`.

### Requirements
- DeepSeek R1 model (Qwen3 8B MLX)
- OpenAI-compatible API server
- Server running on port 1234

### Verification
Test if your local server is working:
```bash
curl http://127.0.0.1:1234/v1/models
```

Should return a JSON response with available models.

## Benefits of Local Model

✅ **Privacy**: All processing stays local  
✅ **Cost**: No API fees  
✅ **Speed**: Potentially faster inference  
✅ **Reliability**: No network dependency  
✅ **Control**: Full control over model behavior  

## Integration Status

The following components now support local models:

- ✅ `agent_llm_wrapper.py` - LLM wrapper with local model support
- ✅ `model_config.py` - Configuration management
- ✅ `standalone_coffee_demo.py` - Demo with model switching
- 🔄 `rag_processor.py` - Uses LLM wrapper (automatic support)
- 🔄 `ag_ui/server.py` - Uses LLM wrapper (automatic support)

## Troubleshooting

**Connection timeout**: Ensure the local model server is running and responding
**Port conflicts**: Change the port in `model_config.py` if needed
**Model loading**: DeepSeek models may take time to load initially

## Next Steps

1. Start your local DeepSeek server at port 1234
2. Set `USE_LOCAL_MODEL=true` environment variable
3. Run any RAG demo to test local model integration