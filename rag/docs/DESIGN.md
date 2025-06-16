# NearGravity RAG System Design

## Problem Space Background

### The Challenge
Traditional digital advertising is fundamentally broken for generative content:

1. **Static Targeting Fails**: Traditional ads rely on keywords and demographics, but generative content is:
   - Dynamic and personalized per user
   - Context-dependent without fixed keywords
   - Unpredictable in structure and format

2. **Privacy Violations**: Current ad systems require:
   - Extensive user tracking and cookies
   - Behavioral data collection
   - Third-party data sharing
   - Profile building across sites

3. **Semantic Corruption**: Injecting ads into content causes:
   - Loss of meaning and coherence
   - Disrupted user experience
   - Context misalignment
   - No verification of content integrity

4. **No Monetization Path**: Content creators lack:
   - Ways to monetize generative/AI content
   - Fair compensation models
   - Transparent value flows
   - User-centric incentives

### The NearGravity Solution

NearGravity reimagines advertising for the generative AI era through:

1. **Semantic Matching**: Using embeddings instead of keywords to understand intent
2. **Privacy-First**: Zero-knowledge processing in TEEs, no tracking required
3. **Semantic Integrity Guard (SIG)**: Mathematical guarantees on meaning preservation
4. **Blockchain Settlement**: Transparent, instant micropayments with audit trails

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Web App   │  │   Chrome    │  │   Python    │            │
│  │  (Next.js)  │  │  Extension  │  │  Pipeline   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      Flask API Service                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   RAG Endpoint (/rag)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                     RAG Service Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Message   │  │  Injection  │  │  Semantic   │            │
│  │  Processor  │  │   Matcher   │  │  Verifier   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Agent System Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Semantic   │  │  Matching   │  │  Delivery   │            │
│  │    Agent    │  │    Agent    │  │    Agent    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                     Data Storage Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Vector    │  │    Graph    │  │  Blockchain │            │
│  │     DB      │  │     DB      │  │    (TEN)    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** (Mo + MT)
   - User provides message content
   - Specifies output modality (text, code, structured)
   - Includes metadata (user_id, preferences)

2. **Embedding Generation**
   - FastEmbed creates semantic representation
   - 384-dimensional dense vectors
   - Cached for performance

3. **Injection Retrieval**
   - FAISS vector search for similar content
   - Constraint filtering (budget, rules)
   - Ranking by relevance + bid

4. **Semantic Combination**
   - Contextual merging of messages
   - Multiple strategies (inline, augmented)
   - Coherence preservation

5. **Content Generation**
   - LiteLLM for multi-model support
   - Modality-specific prompting
   - Format validation

6. **Semantic Verification**
   - Delta calculation (cosine + MI)
   - Threshold checking by type
   - Bounds enforcement

7. **Blockchain Recording**
   - Transaction creation
   - Semantic proof commitment
   - Micropayment execution

## Implementation Plan

### Phase 1: Core RAG Pipeline
- Message processing with embeddings
- Basic injection matching
- Simple content generation
- Local testing framework

### Phase 2: Semantic Integrity
- Delta calculation algorithms
- Threshold configuration
- Verification reporting
- Bounds enforcement

### Phase 3: Production Features
- FAISS integration for scale
- Multi-modal generation
- Blockchain recording
- Performance optimization

### Phase 4: Advanced Features
- TEE integration
- Zero-knowledge proofs
- Advanced matching strategies
- Real-time bidding

## Key Design Decisions

1. **Thread-based, not async**: Following existing pattern for consistency
2. **Flask HTTP server**: Integrating with existing API infrastructure
3. **Local embeddings**: Using FastEmbed for privacy and performance
4. **Modular agents**: Leveraging existing agent framework
5. **In-memory start**: Vector store in memory, then migrate to FAISS

## Models Required Locally

1. **FastEmbed** (all-MiniLM-L6-v2)
   - 384-dimensional embeddings
   - ~90MB model size
   - CPU-friendly performance

2. **Optional: Local LLM**
   - Llama 2 7B for testing
   - Or use API providers via LiteLLM

## Security Considerations

1. **Data Privacy**
   - All processing in local memory
   - No external data leakage
   - TEE-ready architecture

2. **Semantic Integrity**
   - Cryptographic commitments
   - Immutable audit trail
   - Verifiable transformations

3. **Access Control**
   - Provider authentication
   - User consent tracking
   - Rate limiting

## Performance Targets

- Embedding generation: <50ms
- Vector search: <100ms
- Content generation: <2s
- End-to-end: <3s
- Throughput: 100 req/s

## Next Steps

1. Review existing agent implementations
2. Design integration points
3. Create development roadmap
4. Set up local model environment
5. Begin implementation
