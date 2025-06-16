"""
Test script for NearGravity RAG functionality
Demonstrates the complete flow from injection to generation
"""
import requests
import json
import time


BASE_URL = "http://localhost:5005/api/v1/rag"


def test_add_injections():
    """Add sample injection messages"""
    print("=== Adding Injection Messages ===")
    
    injections = [
        {
            "content": "Discover our premium Colombian coffee beans, roasted to perfection for your morning ritual.",
            "provider_id": "coffee_shop_123",
            "metadata": {
                "category": "beverage",
                "bid_amount": 0.002,
                "tags": ["coffee", "morning", "premium", "colombian"]
            }
        },
        {
            "content": "Start your day with our AI-powered productivity assistant that learns your habits.",
            "provider_id": "ai_startup_456",
            "metadata": {
                "category": "technology",
                "bid_amount": 0.003,
                "tags": ["morning", "productivity", "AI", "routine"]
            }
        },
        {
            "content": "Transform your mornings with our organic yoga mats made from sustainable materials.",
            "provider_id": "wellness_789",
            "metadata": {
                "category": "wellness",
                "bid_amount": 0.001,
                "tags": ["morning", "yoga", "wellness", "sustainable"]
            }
        }
    ]
    
    injection_ids = []
    for injection in injections:
        response = requests.post(f"{BASE_URL}/inject", json=injection)
        if response.status_code == 201:
            result = response.json()
            injection_ids.append(result['injection_id'])
            print(f"✓ Added injection: {result['injection_id']}")
        else:
            print(f"✗ Failed to add injection: {response.text}")
    
    return injection_ids


def test_generate_content():
    """Test content generation with different queries"""
    print("\n=== Testing Content Generation ===")
    
    test_cases = [
        {
            "message": "I'm looking for recommendations to improve my morning routine",
            "user_id": "test_user_1",
            "modality": "text",
            "constraints": {
                "semantic_threshold": 0.7,
                "max_injections": 2
            }
        },
        {
            "message": "What's the best way to start my day productively?",
            "user_id": "test_user_2",
            "modality": "text",
            "constraints": {
                "semantic_threshold": 0.75,
                "max_injections": 3
            }
        },
        {
            "message": "I need help organizing my morning schedule",
            "user_id": "test_user_3",
            "modality": "structured",
            "modality_params": {
                "format": "json",
                "schema": "schedule"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i + 1}:")
        print(f"Query: {test_case['message']}")
        
        response = requests.post(f"{BASE_URL}/generate", json=test_case)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Generated content successfully")
            print(f"  - Processing time: {result['processing_time_ms']:.2f}ms")
            print(f"  - Injections used: {result['injection_count']}")
            
            if result['semantic_delta']:
                print(f"  - Semantic similarity: {result['semantic_delta']['cosine_similarity']:.3f}")
                print(f"  - Within bounds: {result['semantic_delta']['is_within_bounds']}")
            
            print(f"\nGenerated Content:")
            print("-" * 50)
            print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            print("-" * 50)
        else:
            print(f"✗ Failed to generate content: {response.text}")


def test_semantic_verification():
    """Test semantic verification between texts"""
    print("\n=== Testing Semantic Verification ===")
    
    test_pairs = [
        {
            "original": "I want to improve my morning routine with better habits",
            "transformed": "I want to improve my morning routine with better habits. Discover our premium Colombian coffee beans, roasted to perfection for your morning ritual.",
            "transformation_type": "default"
        },
        {
            "original": "The quick brown fox jumps over the lazy dog",
            "transformed": "A fast brown fox leaps above the sleepy canine",
            "transformation_type": "translation"
        }
    ]
    
    for i, pair in enumerate(test_pairs):
        print(f"\nVerification {i + 1}:")
        response = requests.post(f"{BASE_URL}/verify", json=pair)
        
        if response.status_code == 200:
            result = response.json()
            delta = result['semantic_delta']
            print(f"✓ Semantic verification complete")
            print(f"  - Cosine similarity: {delta['cosine_similarity']:.3f}")
            print(f"  - Mutual info score: {delta['mutual_info_score']:.3f}")
            print(f"  - Composite delta: {delta['composite_delta']:.3f}")
            print(f"  - Within bounds: {delta['is_within_bounds']}")
            print(f"  - Threshold: {delta['threshold']}")
        else:
            print(f"✗ Verification failed: {response.text}")


def test_list_injections():
    """List all injections"""
    print("\n=== Listing All Injections ===")
    
    response = requests.get(f"{BASE_URL}/injections")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {result['total']} injections")
        for injection in result['injections']:
            print(f"  - {injection['injection_id']}: {injection['content'][:50]}...")
    else:
        print(f"✗ Failed to list injections: {response.text}")


def test_metrics():
    """Get system metrics"""
    print("\n=== System Metrics ===")
    
    response = requests.get(f"{BASE_URL}/metrics")
    if response.status_code == 200:
        result = response.json()
        
        print("Processor Metrics:")
        for key, value in result['processor_metrics'].items():
            print(f"  - {key}: {value}")
        
        print("\nStore Statistics:")
        for key, value in result['store_statistics'].items():
            print(f"  - {key}: {value}")
    else:
        print(f"✗ Failed to get metrics: {response.text}")


def main():
    """Run all tests"""
    print("NearGravity RAG Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("✗ RAG service is not healthy. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Please start the Flask server on port 5005.")
        return
    
    # Run tests
    injection_ids = test_add_injections()
    time.sleep(1)  # Give time for indexing
    
    test_generate_content()
    test_semantic_verification()
    test_list_injections()
    test_metrics()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")


if __name__ == "__main__":
    main()
