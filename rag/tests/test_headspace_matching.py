#!/usr/bin/env python3
"""
Test semantic matching with Headspace meditation vs Coffee campaigns
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

def test_headspace_vs_coffee_matching():
    """Test which campaign matches better for different user intents"""
    embedding_manager = EmbeddingManager()
    
    # Campaigns
    campaigns = {
        "headspace": "Try out free offer on the headspace meditation app",
        "coffee": "Try our premium Colombian coffee beans for the perfect morning brew! Ethically sourced, expertly roasted."
    }
    
    # User queries
    test_queries = [
        "I need some morning motivation and energy to start my productive workday. Any tips?",
        "I'm feeling stressed and anxious about work. How can I calm down?", 
        "Looking for ways to focus better during meetings",
        "Need help with mindfulness and meditation techniques",
        "Want something to help me wake up in the morning",
        "I have trouble concentrating at work",
        "Need to reduce stress levels naturally",
        "Looking for productivity boosters for busy mornings"
    ]
    
    print("🧠 Headspace vs Coffee Campaign Matching")
    print("=" * 60)
    
    # Generate campaign embeddings
    campaign_embeddings = {}
    for name, content in campaigns.items():
        campaign_embeddings[name] = embedding_manager.embed_text(content)[0]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        query_emb = embedding_manager.embed_text(query)[0]
        
        scores = {}
        for name, emb in campaign_embeddings.items():
            similarity = embedding_manager.similarity(query_emb, emb)
            scores[name] = similarity
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        winner = sorted_scores[0]
        print(f"   🥇 Winner: {winner[0].upper()} ({winner[1]:.4f})")
        
        for name, score in sorted_scores:
            threshold_pass = "✅" if score >= 0.65 else "❌"
            print(f"   {name}: {score:.4f} {threshold_pass}")
        
        # Check if both pass threshold
        both_pass = all(score >= 0.65 for _, score in scores.items())
        if both_pass:
            print("   ⚠️  CONFLICT: Both campaigns pass threshold!")

def test_stress_vs_energy_queries():
    """Test specific stress vs energy intent differentiation"""
    embedding_manager = EmbeddingManager()
    
    print("\n🎯 Stress vs Energy Intent Analysis")
    print("=" * 60)
    
    # Specific test cases
    test_cases = [
        {
            "category": "STRESS/ANXIETY",
            "queries": [
                "I'm feeling overwhelmed and stressed",
                "Need help managing anxiety",
                "Looking for ways to relax and unwind",
                "Can't stop worrying about work"
            ]
        },
        {
            "category": "ENERGY/PRODUCTIVITY", 
            "queries": [
                "Need more energy for morning workouts",
                "Looking for productivity boost",
                "Want to feel more alert in meetings",
                "Need something to help me wake up"
            ]
        }
    ]
    
    campaigns = {
        "headspace": "Try out free offer on the headspace meditation app",
        "coffee": "Try our premium Colombian coffee beans for the perfect morning brew!"
    }
    
    # Generate embeddings
    headspace_emb = embedding_manager.embed_text(campaigns["headspace"])[0]
    coffee_emb = embedding_manager.embed_text(campaigns["coffee"])[0]
    
    for case in test_cases:
        print(f"\n📂 {case['category']} Queries:")
        
        for query in case["queries"]:
            query_emb = embedding_manager.embed_text(query)[0]
            
            headspace_sim = embedding_manager.similarity(query_emb, headspace_emb)
            coffee_sim = embedding_manager.similarity(query_emb, coffee_emb)
            
            if headspace_sim > coffee_sim:
                winner = "HEADSPACE"
                margin = headspace_sim - coffee_sim
            else:
                winner = "COFFEE" 
                margin = coffee_sim - headspace_sim
            
            print(f"   '{query}'")
            print(f"     Winner: {winner} (margin: +{margin:.3f})")
            print(f"     Headspace: {headspace_sim:.4f}, Coffee: {coffee_sim:.4f}")

def test_threshold_impact():
    """Test what happens at different thresholds"""
    embedding_manager = EmbeddingManager()
    
    print("\n📊 Threshold Impact Analysis")
    print("=" * 60)
    
    query = "I'm feeling stressed and need to relax"
    campaigns = {
        "headspace": "Try out free offer on the headspace meditation app",
        "coffee": "Try our premium Colombian coffee beans for the perfect morning brew!"
    }
    
    query_emb = embedding_manager.embed_text(query)[0]
    
    scores = {}
    for name, content in campaigns.items():
        emb = embedding_manager.embed_text(content)[0]
        scores[name] = embedding_manager.similarity(query_emb, emb)
    
    thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75]
    
    print(f"Query: '{query}'")
    print(f"Headspace: {scores['headspace']:.4f}")
    print(f"Coffee: {scores['coffee']:.4f}")
    print()
    
    for threshold in thresholds:
        headspace_pass = scores['headspace'] >= threshold
        coffee_pass = scores['coffee'] >= threshold
        
        if headspace_pass and coffee_pass:
            result = "CONFLICT (both pass)"
        elif headspace_pass:
            result = "Headspace only"
        elif coffee_pass:
            result = "Coffee only"
        else:
            result = "No matches"
        
        print(f"Threshold {threshold}: {result}")

if __name__ == '__main__':
    test_headspace_vs_coffee_matching()
    test_stress_vs_energy_queries() 
    test_threshold_impact()