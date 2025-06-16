# NearGravity Claude RAG Implementation

## Overview

This package implements the core Retrieval-Augmented Generation (RAG) flow for NearGravity, enabling semantic-aware ad injection into generative content while maintaining privacy and semantic integrity.

## Problem Space

Traditional advertising fails with generative content because:
1. **No static keywords** - Content is dynamic and personalized
2. **Privacy concerns** - User data is exposed through tracking
3. **Semantic drift** - Ad injection can corrupt message meaning
4. **No verification** - Can't prove content integrity

NearGravity solves this through:
1. **Semantic matching** - Using embeddings instead of keywords
2. **Zero-knowledge processing** - TEE/confidential computing
3. **Semantic Integrity Guard** - Bounded delta verification
4. **Blockchain recording** - Immutable audit trail

## Architecture

The system follows a thread-based (not async) pipeline:

```
User Message (Mo) → Embedding → Vector Search → Injection Selection (Mi)
                                      ↓
                              Semantic Combination
                                      ↓
                              Content Generation (FR)
                                      ↓
                              Semantic Verification
                                      ↓
                              Blockchain Recording
```

## Components

### 1. Message Processor
- Handles incoming user messages
- Generates embeddings using FastEmbed
- Manages message flow through pipeline

### 2. Injection Matcher
- Searches vector store for relevant injection messages
- Uses FAISS for efficient similarity search
- Applies constraint filtering (budget, rules, etc.)

### 3. Semantic Combiner
- Combines user message with injection message
- Maintains semantic coherence
- Multiple combination strategies (contextual, inline, augmented)

### 4. Content Generator
- Generates final content in requested modality
- Uses LiteLLM for multi-model support
- Handles text, code, structured data formats

### 5. Semantic Verifier
- Calculates semantic delta between original and generated
- Ensures delta stays within acceptable bounds
- Uses cosine similarity and mutual information metrics

### 6. Blockchain Recorder
- Records transaction on TEN network
- Includes semantic proof commitments
- Handles micropayments between parties

## Data Flow

1. **Input**: UserContextualMessage + OutputModalityTarget
2. **Retrieval**: Find relevant InjectionMessages via vector similarity
3. **Augmentation**: Combine messages while preserving semantics
4. **Generation**: Create content in target modality
5. **Verification**: Ensure semantic integrity maintained
6. **Recording**: Commit to blockchain with proofs

## Key Features

- **Thread-based processing** (no async/await)
- **Privacy-preserving** (TEE-ready architecture)
- **Multi-modal support** (text, code, structured data)
- **Semantic guarantees** (bounded delta verification)
- **Blockchain integration** (TEN network)
