# NearGravity RAG Quick Start Guide

## Prerequisites

1. Python 3.8+ installed
2. NearGravity repository cloned
3. Virtual environment activated

## Installation

```bash
# Navigate to project
cd /Users/mcevoyinit/ai/NearGravity

# Install RAG dependencies
pip install fastembed litellm numpy scikit-learn

# Set OpenAI API key (for testing)
export OPENAI_API_KEY="your-key-here"
```

## Integration with Existing App

1. **Update your app.py**:

```python
# In imports section, add:
from rag.api.rag_routes import rag_bp

# In create_app() function, add:
app.register_blueprint(rag_bp, url_prefix='/api/v1/rag')
```

2. **Start the server**:

```bash
cd src
python backend/api/app.py
```

## Testing the RAG System

### 1. Add Injection Messages

```bash
curl -X POST http://localhost:5005/api/v1/rag/inject \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Premium coffee beans for your morning",
    "provider_id": "coffee_shop_123",
    "metadata": {
      "tags": ["coffee", "morning"],
      "bid_amount": 0.002
    }
  }'
```

### 2. Generate Content

```bash
curl -X POST http://localhost:5005/api/v1/rag/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I improve my morning routine?",
    "user_id": "test_user",
    "modality": "text"
  }'
```

### 3. Run Full Demo

```bash
python src/rag/test_rag_demo.py
```

## Architecture Overview

```
User Request → Embedding → Vector Search → Injection Selection
                                ↓
                        Semantic Combination
                                ↓
                        Content Generation
                                ↓
                        Semantic Verification
                                ↓
                        Response + Blockchain Record
```

## Key Components

1. **EnhancedRAGProcessor**: Orchestrates the flow
2. **VectorStoreService**: Manages injection messages
3. **Flask API Routes**: HTTP endpoints
4. **Semantic Verifier**: Ensures content integrity

## Configuration Options

- **Embedding Model**: BAAI/bge-small-en-v1.5 (default)
- **LLM Model**: gpt-3.5-turbo (default)
- **Semantic Threshold**: 0.85 (adjustable)
- **Cache TTL**: 3600 seconds

## Troubleshooting

1. **Import errors**: Ensure all dependencies installed
2. **API key errors**: Check OPENAI_API_KEY is set
3. **Port conflicts**: Change PORT in environment
4. **Memory issues**: Reduce thread pool size

## Next Steps

1. Add more injection messages for testing
2. Experiment with different modalities
3. Monitor metrics at `/api/v1/rag/metrics`
4. Configure FAISS for production scale

## Support

- Check logs in console for debugging
- Review DESIGN.md for architecture details
- See MODELS_GUIDE.md for model options
