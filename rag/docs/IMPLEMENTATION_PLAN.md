# NearGravity RAG Implementation Plan

## Overview

Building on the existing NearGravity infrastructure, we'll implement a complete RAG (Retrieval-Augmented Generation) system that enables semantic-aware ad injection while maintaining privacy and content integrity.

## Existing Infrastructure Analysis

### What We Have

1. **Agent Framework** (`src/backend/agentic/`)
   - Thread-based processing with BaseAgent
   - LLMWrapper using LiteLLM for multi-model support
   - EmbeddingManager using FastEmbed
   - DGraphConnector for vector storage
   - Existing RAGAgent skeleton

2. **Data Models** (`src/models/entities/python/`)
   - UserContextualMessage
   - OutputModalityTarget
   - InjectionMessage
   - FinalGeneratedResult

3. **Matching Engine** (`src/matching_engine/`)
   - Constraint validation
   - Scoring strategies
   - Similarity providers

4. **Crypto Service** (`src/services/crypto/`)
   - TEN network integration
   - Token operations
   - Transaction recording

5. **API Layer** (`src/backend/api/`)
   - Flask-based REST API
   - Existing route structure

### What We Need to Build

1. **Enhanced RAG Processor**
   - Semantic combination strategies
   - Multi-modal content generation
   - Semantic integrity verification

2. **Vector Store Integration**
   - In-memory store for development
   - FAISS integration for production
   - Embedding cache management

3. **API Endpoints**
   - `/rag/generate` - Main generation endpoint
   - `/rag/inject` - Add injection messages
   - `/rag/verify` - Semantic verification

4. **Testing Framework**
   - Unit tests for each component
   - Integration tests for full flow
   - Performance benchmarks

## Implementation Phases

### Phase 1: Core RAG Components (Week 1)

1. **Update RAG Processor** (`src/claude/rag_processor.py`)
   ```python
   class EnhancedRAGProcessor(RAGProcessor):
       - Implement semantic combination strategies
       - Add modality-specific generation
       - Integrate with matching engine
   ```

2. **Create Vector Store Service** (`src/claude/vector_store.py`)
   ```python
   class VectorStoreService:
       - In-memory storage with persistence
       - Efficient similarity search
       - Batch operations support
   ```

3. **Implement Semantic Verifier** (`src/claude/semantic_verifier.py`)
   ```python
   class SemanticVerifier:
       - Delta calculation algorithms
       - Threshold management
       - Verification reporting
   ```

### Phase 2: API Integration (Week 2)

1. **Create Flask Routes** (`src/claude/api/rag_routes.py`)
   ```python
   @rag_bp.route('/generate', methods=['POST'])
   def generate_content():
       # Main RAG endpoint
   
   @rag_bp.route('/inject', methods=['POST'])
   def add_injection():
       # Add injection message
   
   @rag_bp.route('/verify', methods=['POST'])
   def verify_semantic():
       # Verify semantic integrity
   ```

2. **Update Main App** (`src/backend/api/app.py`)
   - Register RAG blueprint
   - Add middleware for auth
   - Configure rate limiting

### Phase 3: Production Features (Week 3)

1. **FAISS Integration**
   - Replace in-memory with FAISS
   - Implement index persistence
   - Add clustering for scale

2. **Caching Layer**
   - Embedding cache with TTL
   - Result cache for common queries
   - Distributed cache support

3. **Monitoring & Metrics**
   - Processing time tracking
   - Semantic delta analytics
   - Error rate monitoring

### Phase 4: Advanced Features (Week 4)

1. **TEE Integration**
   - Confidential computing setup
   - Secure enclave processing
   - Attestation framework

2. **Blockchain Recording**
   - Smart contract integration
   - Micropayment flows
   - Audit trail generation

## Technical Decisions

### Models

1. **Embeddings**: FastEmbed with BAAI/bge-small-en-v1.5
   - 384 dimensions
   - Good multilingual support
   - Fast CPU inference

2. **Generation**: LiteLLM with multiple providers
   - GPT-3.5/4 for quality
   - Local Llama 2 for testing
   - Mistral for cost efficiency

### Storage

1. **Development**: In-memory with JSON persistence
2. **Production**: FAISS with DGraph metadata
3. **Cache**: Redis for distributed caching

### Processing

1. **Threading**: Consistent with agent framework
2. **Queues**: Priority-based task processing
3. **Batching**: For embedding generation

## API Design

### Generate Content
```
POST /api/v1/rag/generate
{
    "message": "Looking for morning coffee recommendations",
    "user_id": "user123",
    "modality": "text",
    "modality_params": {
        "style": "conversational",
        "length": "medium"
    },
    "constraints": {
        "semantic_threshold": 0.85,
        "max_injections": 3
    }
}

Response:
{
    "content": "Generated content with injections...",
    "semantic_delta": {
        "cosine_similarity": 0.89,
        "is_within_bounds": true
    },
    "transaction_hash": "0x...",
    "processing_time_ms": 1250
}
```

### Add Injection
```
POST /api/v1/rag/inject
{
    "content": "Premium coffee beans from Colombia",
    "provider_id": "coffee_shop_123",
    "metadata": {
        "category": "beverage",
        "bid_amount": 0.001,
        "targeting": ["coffee", "morning", "premium"]
    }
}

Response:
{
    "injection_id": "inj_1234567890",
    "status": "active"
}
```

## Testing Strategy

1. **Unit Tests**
   - Each component in isolation
   - Mock external dependencies
   - Coverage > 80%

2. **Integration Tests**
   - Full RAG flow
   - Database interactions
   - API endpoints

3. **Performance Tests**
   - Latency benchmarks
   - Throughput testing
   - Memory profiling

## Security Considerations

1. **Input Validation**
   - Message length limits
   - Injection content filtering
   - Rate limiting per user

2. **Data Privacy**
   - No PII in embeddings
   - Encrypted storage
   - Audit logging

3. **Access Control**
   - API key authentication
   - Provider verification
   - User consent tracking

## Deployment

1. **Development**
   - Local Flask server
   - SQLite for persistence
   - Mock blockchain

2. **Staging**
   - Docker containers
   - PostgreSQL + Redis
   - Testnet blockchain

3. **Production**
   - Kubernetes deployment
   - Distributed FAISS
   - Mainnet integration

## Success Metrics

1. **Performance**
   - P95 latency < 2s
   - Throughput > 100 req/s
   - Error rate < 0.1%

2. **Quality**
   - Semantic similarity > 0.85
   - User satisfaction > 4.5/5
   - Injection relevance > 0.8

3. **Business**
   - CTR improvement > 2x
   - Revenue per user increase
   - Provider retention > 80%
