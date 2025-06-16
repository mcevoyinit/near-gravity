# Models Required for NearGravity RAG

## Embedding Models

### 1. FastEmbed - BAAI/bge-small-en-v1.5 (Recommended)
- **Size**: ~130MB
- **Dimensions**: 384
- **Performance**: ~2ms per embedding on CPU
- **Installation**: `pip install fastembed`
- **Auto-downloads**: Model downloads automatically on first use

### Alternative: all-MiniLM-L6-v2
- **Size**: ~90MB  
- **Dimensions**: 384
- **Performance**: Slightly faster but lower quality
- **Installation**: Same as above

## LLM Models (via LiteLLM)

### For Development/Testing

1. **OpenAI GPT-3.5-turbo** (API)
   - Set environment variable: `OPENAI_API_KEY`
   - Cost: ~$0.002 per 1K tokens
   - Quality: Good for most use cases

2. **Local Llama 2 7B** (Optional)
   - Download from HuggingFace: `TheBloke/Llama-2-7B-Chat-GGUF`
   - Size: ~4GB (quantized)
   - Run with: `llama-cpp-python` or `ollama`
   - Performance: ~5-10 tokens/sec on CPU

### For Production

1. **GPT-4** (API)
   - Better quality but higher cost
   - ~$0.03 per 1K tokens

2. **Claude 3** (API) 
   - Set: `ANTHROPIC_API_KEY`
   - Good for complex reasoning

3. **Mistral 7B** (Local or API)
   - Good balance of quality/cost
   - Can run locally or via API

## Setup Instructions

### 1. Install Dependencies
```bash
cd /Users/mcevoyinit/ai/NearGravity
pip install fastembed litellm numpy scikit-learn
```

### 2. Set Environment Variables
```bash
# For OpenAI (recommended for testing)
export OPENAI_API_KEY="your-key-here"

# For local models (optional)
export LITELLM_LOCAL_MODEL_PATH="/path/to/models"
```

### 3. Download Local Models (Optional)
```python
# For Llama 2 via Ollama
# Install: https://ollama.ai
# Then run: ollama pull llama2

# For manual download
from huggingface_hub import hf_hub_download
model_path = hf_hub_download(
    repo_id="TheBloke/Llama-2-7B-Chat-GGUF",
    filename="llama-2-7b-chat.Q4_K_M.gguf"
)
```

### 4. Verify Installation
```python
# Test embeddings
from fastembed import TextEmbedding
model = TextEmbedding("BAAI/bge-small-en-v1.5")
embeddings = list(model.embed(["Test text"]))
print(f"Embedding shape: {embeddings[0].shape}")

# Test LLM
import litellm
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

## Performance Considerations

### Embedding Generation
- Batch processing: Process multiple texts together
- Caching: Embeddings are cached automatically
- GPU: Not required, CPU is sufficient

### LLM Generation  
- Use GPT-3.5 for development (fast, cheap)
- Use local models for privacy-sensitive work
- Consider rate limiting for production

## Privacy Mode

For complete privacy (no external API calls):
1. Use local embedding model (already default)
2. Use local LLM (Llama 2 or Mistral)
3. Run everything in TEE (future enhancement)

## Cost Estimation

For 1000 requests/day:
- Embeddings: Free (local)
- GPT-3.5 generation: ~$2-5/day
- Storage: Minimal
- Total: ~$60-150/month

## Optimization Tips

1. **Pre-compute injection embeddings**: Done automatically
2. **Cache frequent queries**: Built into EnhancedRAGProcessor
3. **Batch similar requests**: Use batch processing API
4. **Use appropriate models**: Don't use GPT-4 unless needed
