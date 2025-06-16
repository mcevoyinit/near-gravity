#!/usr/bin/env python3
"""
Test sleep mattress campaign vs sleep issue query
"""
import os
import sys

# Add project paths
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from src.backend.agentic.agent_embeddings import EmbeddingManager

def test_sleep_campaign_matching():
    """Test sleep mattress campaign matching"""
    embedding_manager = EmbeddingManager()
    
    # Sleep campaign
    sleep_campaign = """Discover the sleep revolution with our premium mattresses, designed to transform every night into a serene escape. Experience unparalleled comfort with layers of adaptive foam that cradle your body, providing perfect support and alignment. Our mattresses are crafted with breathable materials to keep you cool and refreshed, ensuring a blissful, uninterrupted sleep. Say goodbye to restless nights and awaken rejuvenated, ready to seize the day. Join thousands of satisfied customers who have upgraded their sleep quality. Elevate your bedtime routine with our exceptional mattresses—where luxury meets restorative rest. Sweet dreams await!"""
    
    # User query
    user_query = "I wish i could rest better at night, I fight my chest tight and am uncomfortable"
    
    # Generate embeddings
    campaign_emb = embedding_manager.embed_text(sleep_campaign)[0]
    query_emb = embedding_manager.embed_text(user_query)[0]
    
    # Calculate similarity
    similarity = embedding_manager.similarity(query_emb, campaign_emb)
    
    print("🛏️ Sleep Campaign Matching Test")
    print("=" * 60)
    print(f"Campaign: {sleep_campaign[:100]}...")
    print(f"User Query: {user_query}")
    print()
    print(f"Similarity Score: {similarity:.4f}")
    print(f"Current Threshold: 0.65")
    print(f"Would Pass: {'✅ YES' if similarity >= 0.65 else '❌ NO'}")
    print()
    
    # Test different thresholds
    thresholds = [0.5, 0.55, 0.6, 0.65, 0.7]
    print("Threshold Analysis:")
    for threshold in thresholds:
        status = "✅ PASS" if similarity >= threshold else "❌ FAIL"
        print(f"  {threshold}: {status}")
    
    # Test variations of sleep queries
    print("\n🧪 Testing Similar Sleep Queries:")
    sleep_queries = [
        "I can't sleep well at night",
        "Need better rest and comfort",
        "My back hurts when I sleep",
        "Looking for better sleep quality",
        "Uncomfortable sleeping position",
        "Restless nights and poor sleep",
        "Need a more comfortable bed"
    ]
    
    for i, query in enumerate(sleep_queries, 1):
        q_emb = embedding_manager.embed_text(query)[0]
        sim = embedding_manager.similarity(q_emb, campaign_emb)
        threshold_65 = "✅" if sim >= 0.65 else "❌"
        threshold_60 = "✅" if sim >= 0.60 else "❌"
        print(f"  {i}. '{query}'")
        print(f"     Score: {sim:.4f} | @0.65: {threshold_65} | @0.60: {threshold_60}")

def test_campaign_length_impact():
    """Test how campaign length affects matching"""
    embedding_manager = EmbeddingManager()
    
    user_query = "I wish i could rest better at night, I fight my chest tight and am uncomfortable"
    
    # Different length versions of sleep campaign
    campaigns = {
        "short": "Premium mattresses for better sleep and comfort",
        "medium": "Discover premium mattresses designed for comfort. Experience better sleep with adaptive foam support.",
        "long": """Discover the sleep revolution with our premium mattresses, designed to transform every night into a serene escape. Experience unparalleled comfort with layers of adaptive foam that cradle your body, providing perfect support and alignment.""",
        "full": """Discover the sleep revolution with our premium mattresses, designed to transform every night into a serene escape. Experience unparalleled comfort with layers of adaptive foam that cradle your body, providing perfect support and alignment. Our mattresses are crafted with breathable materials to keep you cool and refreshed, ensuring a blissful, uninterrupted sleep. Say goodbye to restless nights and awaken rejuvenated, ready to seize the day. Join thousands of satisfied customers who have upgraded their sleep quality. Elevate your bedtime routine with our exceptional mattresses—where luxury meets restorative rest. Sweet dreams await!"""
    }
    
    print("\n📏 Campaign Length Impact Analysis")
    print("=" * 60)
    
    query_emb = embedding_manager.embed_text(user_query)[0]
    
    for length_type, campaign_text in campaigns.items():
        campaign_emb = embedding_manager.embed_text(campaign_text)[0]
        similarity = embedding_manager.similarity(query_emb, campaign_emb)
        
        print(f"{length_type.upper()}:")
        print(f"  Text: {campaign_text[:80]}...")
        print(f"  Length: {len(campaign_text)} chars")
        print(f"  Score: {similarity:.4f}")
        print(f"  @0.65: {'✅ PASS' if similarity >= 0.65 else '❌ FAIL'}")
        print(f"  @0.60: {'✅ PASS' if similarity >= 0.60 else '❌ FAIL'}")
        print()

if __name__ == '__main__':
    test_sleep_campaign_matching()
    test_campaign_length_impact()