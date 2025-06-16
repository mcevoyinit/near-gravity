#!/usr/bin/env python3
"""
Test similarity between coffee injection and morning motivation query
"""
import os
import sys

# Add project paths
project_root = os.path.join(os.path.dirname(__file__), '.')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from src.backend.agentic.agent_embeddings import EmbeddingManager

def test_similarity():
    """Test similarity between coffee content and motivation query"""
    embedding_manager = EmbeddingManager()
    
    # Coffee injection content
    coffee_content = "Start your morning with Blue Bottle Coffee premium single-origin beans - hand-roasted for maximum energy and focus throughout your productive workday!"
    
    # User query
    user_query = "I need some morning motivation and energy to start my productive workday. I feel sluggish and need tips to get energized. What should I do?"
    
    # Generate embeddings
    print("🧠 Generating embeddings...")
    coffee_embedding = embedding_manager.embed_text(coffee_content)
    query_embedding = embedding_manager.embed_text(user_query)
    
    # Calculate similarity
    similarity = embedding_manager.similarity(query_embedding[0], coffee_embedding[0])
    
    print(f"☕ Coffee Content: {coffee_content}")
    print(f"💭 User Query: {user_query}")
    print(f"🔢 Similarity Score: {similarity:.4f}")
    print(f"📏 Current Threshold: 0.65")
    print(f"✅ Would Pass: {'YES' if similarity > 0.65 else 'NO'}")
    
    # Test with different queries
    test_queries = [
        "I need morning energy and focus for work",
        "Looking for coffee recommendations for productivity",
        "How to get energized in the morning?",
        "Best morning drinks for focus and energy",
        "Need caffeine boost for workday"
    ]
    
    print("\n🧪 Testing with different queries:")
    for i, query in enumerate(test_queries, 1):
        q_emb = embedding_manager.embed_text(query)
        sim = embedding_manager.similarity(q_emb[0], coffee_embedding[0])
        print(f"{i}. {query}")
        print(f"   Similarity: {sim:.4f} {'✅' if sim > 0.65 else '❌'}")

if __name__ == '__main__':
    test_similarity()