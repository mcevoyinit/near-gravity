#!/usr/bin/env python3
"""
Comprehensive test to analyze RAG matching issues
Tests different message lengths, similarity calculations, and thresholds
"""
import os
import sys
import numpy as np

# Add project paths
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from src.backend.agentic.agent_embeddings import EmbeddingManager
from src.models.entities.python.data_models import InjectionMessage
from src.rag.rag_processor import RAGProcessor
from src.backend.agentic.agent_model import AgentConfig, AgentMessage

def test_message_length_impact():
    """Test how message length affects similarity scores"""
    embedding_manager = EmbeddingManager()
    
    # Base user query
    base_query = "I need coffee"
    
    # Injection messages of different lengths
    injections = {
        "very_short": "Coffee!",
        "short": "Try Blue Bottle Coffee",
        "medium": "Start your morning with Blue Bottle Coffee premium beans",
        "long": "Start your morning with Blue Bottle Coffee premium single-origin beans - hand-roasted for maximum energy and focus throughout your productive workday!",
        "very_long": "Start your morning with Blue Bottle Coffee premium single-origin beans - hand-roasted for maximum energy and focus throughout your productive workday! Our expert roasters carefully select the finest beans from sustainable farms around the world, ensuring every cup delivers exceptional flavor and the perfect caffeine boost you need to tackle your daily challenges with confidence and clarity."
    }
    
    print("📏 Testing Message Length Impact on Similarity")
    print("=" * 60)
    print(f"Base Query: '{base_query}'")
    print()
    
    query_emb = embedding_manager.embed_text(base_query)[0]
    
    for length_type, injection_text in injections.items():
        injection_emb = embedding_manager.embed_text(injection_text)[0]
        similarity = embedding_manager.similarity(query_emb, injection_emb)
        
        print(f"{length_type.upper()}: {similarity:.4f}")
        print(f"  Text: {injection_text}")
        print(f"  Length: {len(injection_text)} chars")
        print(f"  Threshold (0.65): {'✅ PASS' if similarity > 0.65 else '❌ FAIL'}")
        print()

def test_semantic_variations():
    """Test similarity with semantically related but differently worded content"""
    embedding_manager = EmbeddingManager()
    
    # Test different ways of expressing similar concepts
    test_cases = [
        {
            "user_query": "I need energy for work",
            "injections": [
                "Blue Bottle Coffee for energy",
                "Premium coffee for workplace productivity", 
                "Get energized with artisan coffee",
                "Boost your work performance with coffee",
                "High-quality caffeine for professional focus"
            ]
        },
        {
            "user_query": "Looking for breakfast options",
            "injections": [
                "Try our morning pastries",
                "Fresh croissants and coffee",
                "Healthy breakfast bowls available",
                "Start your day with our breakfast menu",
                "Morning nutrition for busy professionals"
            ]
        },
        {
            "user_query": "Need something sweet",
            "injections": [
                "Delicious chocolate cookies",
                "Fresh baked desserts daily",
                "Sweet treats and confections", 
                "Artisan pastries and cakes",
                "Satisfy your sweet tooth here"
            ]
        }
    ]
    
    print("🔍 Testing Semantic Variations")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}: '{test_case['user_query']}'")
        
        query_emb = embedding_manager.embed_text(test_case['user_query'])[0]
        
        for j, injection in enumerate(test_case['injections'], 1):
            injection_emb = embedding_manager.embed_text(injection)[0]
            similarity = embedding_manager.similarity(query_emb, injection_emb)
            
            print(f"  {j}. {injection}")
            print(f"     Similarity: {similarity:.4f} {'✅' if similarity > 0.65 else '❌'}")
        print()

def test_threshold_analysis():
    """Test different threshold values to find optimal settings"""
    embedding_manager = EmbeddingManager()
    
    # Common matching scenarios
    test_pairs = [
        ("I need coffee", "Try Blue Bottle Coffee"),
        ("Looking for energy", "Premium coffee for energy boost"),
        ("Want breakfast", "Fresh morning pastries"),
        ("Need focus", "Coffee for workplace concentration"),
        ("Feeling tired", "Energizing premium coffee blend"),
        ("Want something sweet", "Delicious chocolate pastries"),
        ("Need a snack", "Healthy breakfast options"),
        ("Looking for drinks", "Artisan coffee and beverages")
    ]
    
    thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
    
    print("🎯 Threshold Analysis")
    print("=" * 60)
    
    # Calculate all similarities first
    similarities = []
    for user_msg, injection in test_pairs:
        user_emb = embedding_manager.embed_text(user_msg)[0]
        inj_emb = embedding_manager.embed_text(injection)[0]
        similarity = embedding_manager.similarity(user_emb, inj_emb)
        similarities.append((user_msg, injection, similarity))
    
    # Test each threshold
    for threshold in thresholds:
        matches = sum(1 for _, _, sim in similarities if sim >= threshold)
        print(f"Threshold {threshold}: {matches}/{len(similarities)} matches ({matches/len(similarities)*100:.1f}%)")
    
    print("\nDetailed Results:")
    for user_msg, injection, similarity in similarities:
        print(f"'{user_msg}' -> '{injection}': {similarity:.4f}")

def test_rag_processor_integration():
    """Test the full RAG processor with different scenarios"""
    print("🔄 Testing RAG Processor Integration")
    print("=" * 60)
    
    # Initialize RAG processor
    config = AgentConfig(
        name="test_rag",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=150
    )
    
    rag_processor = RAGProcessor(config)
    
    # Add some injection messages
    injections = [
        ("Start your morning with Blue Bottle Coffee - premium beans for energy!", "coffee_shop"),
        ("Fresh baked pastries and croissants available daily", "bakery"),
        ("Healthy smoothie bowls with organic fruits and proteins", "health_cafe"),
        ("Artisan sandwiches made with locally sourced ingredients", "deli"),
        ("Premium tea selection for afternoon relaxation", "tea_house")
    ]
    
    print("Adding injection messages...")
    for content, provider in injections:
        msg_id = rag_processor.add_injection_message(content, provider)
        print(f"  Added: {msg_id[:12]}... -> {content[:50]}...")
    
    print(f"\nTotal injection messages: {len(rag_processor.get_injection_messages())}")
    
    # Test different user queries
    test_queries = [
        "I need coffee for energy this morning",
        "Looking for breakfast options", 
        "Want something healthy to eat",
        "Need afternoon refreshment",
        "Looking for a quick lunch",
        "Want to try something new",  # Should not match well
        "Tell me about the weather"   # Should not match at all
    ]
    
    print("\nTesting queries:")
    for query in test_queries:
        message = AgentMessage(
            content=query,
            metadata={"user_id": "test_user", "modality": "text"}
        )
        
        result = rag_processor.process(message)
        
        print(f"\nQuery: '{query}'")
        print(f"Candidates found: {result['injection_candidates']}")
        print(f"Generated: {result['result'].content[:100]}...")
        if result['semantic_verification']:
            print(f"Semantic similarity: {result['semantic_verification'].cosine_similarity:.4f}")

def test_embedding_quality():
    """Test the quality and consistency of embeddings"""
    embedding_manager = EmbeddingManager()
    
    print("🧠 Testing Embedding Quality")
    print("=" * 60)
    
    # Test embedding consistency
    test_text = "Blue Bottle Coffee for morning energy"
    
    # Generate multiple embeddings for same text
    embeddings = []
    for i in range(3):
        emb = embedding_manager.embed_text(test_text)[0]
        embeddings.append(emb)
    
    # Check consistency
    sim_1_2 = embedding_manager.similarity(embeddings[0], embeddings[1])
    sim_1_3 = embedding_manager.similarity(embeddings[0], embeddings[2])
    sim_2_3 = embedding_manager.similarity(embeddings[1], embeddings[2])
    
    print(f"Embedding consistency test:")
    print(f"  Same text embedded 3 times")
    print(f"  Similarity 1-2: {sim_1_2:.6f}")
    print(f"  Similarity 1-3: {sim_1_3:.6f}")
    print(f"  Similarity 2-3: {sim_2_3:.6f}")
    print(f"  Expected: ~1.0 (should be identical)")
    
    # Test embedding dimensions and properties
    print(f"\nEmbedding properties:")
    print(f"  Dimensions: {len(embeddings[0])}")
    print(f"  Norm: {np.linalg.norm(embeddings[0]):.6f}")
    print(f"  Mean: {np.mean(embeddings[0]):.6f}")
    print(f"  Std: {np.std(embeddings[0]):.6f}")

if __name__ == '__main__':
    print("🔧 RAG Matching Analysis Suite")
    print("=" * 80)
    
    test_message_length_impact()
    print("\n" + "=" * 80)
    
    test_semantic_variations()
    print("=" * 80)
    
    test_threshold_analysis()
    print("\n" + "=" * 80)
    
    test_embedding_quality()
    print("\n" + "=" * 80)
    
    test_rag_processor_integration()
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")