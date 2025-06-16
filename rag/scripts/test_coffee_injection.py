#!/usr/bin/env python3
"""
Quick test of coffee injection with lowered thresholds
"""
import os
import sys
import requests
import json

# Set API key
os.environ['OPENAI_API_KEY'] = "your_openai_api_key"

def test_coffee_injection():
    base_url = "http://localhost:5000"
    
    print("☕ Testing Coffee Injection with Lowered Thresholds")
    print("=" * 50)
    
    # 1. Add coffee injection
    print("1. Adding coffee shop campaign...")
    injection_data = {
        "content": "Start your morning with Blue Bottle Coffee's premium beans - perfectly roasted for sustained energy and focus!",
        "provider_id": "blue_bottle_coffee",
        "metadata": {
            "bid_amount": 0.003,
            "tags": ["coffee", "morning", "energy", "premium"],
            "category": "beverages"
        }
    }
    
    response = requests.post(f"{base_url}/api/inject", json=injection_data)
    if response.status_code == 201:
        print("   ✅ Coffee campaign added successfully")
    else:
        print(f"   ❌ Failed: {response.json()}")
        return
    
    # 2. Send user query about morning motivation
    print("\n2. Sending user query about morning motivation...")
    query_data = {
        "message": "I need morning motivation and energy to start my productive workday. Any tips?",
        "user_id": "coffee_test_user",
        "modality": "text"
    }
    
    response = requests.post(f"{base_url}/api/generate", json=query_data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        
        print("   ✅ Content generated successfully!")
        print(f"\n📝 Generated Content:")
        print("-" * 40)
        print(result['content'])
        print("-" * 40)
        
        print(f"\n🧠 Semantic Analysis:")
        delta = result['semantic_delta']
        print(f"   Cosine Similarity: {delta['cosine_similarity']:.3f}")
        print(f"   Composite Delta: {delta['composite_delta']:.3f}")
        print(f"   Within Bounds: {delta['is_within_bounds']}")
        print(f"   Processing Time: {result['processing_time_ms']:.0f}ms")
        
        # Check if coffee is mentioned
        content_lower = result['content'].lower()
        coffee_mentions = ['coffee', 'blue bottle', 'beans', 'roasted', 'caffeine']
        found_mentions = [mention for mention in coffee_mentions if mention in content_lower]
        
        if found_mentions:
            print(f"\n☕ Coffee Integration: ✅ SUCCESS")
            print(f"   Found mentions: {', '.join(found_mentions)}")
        else:
            print(f"\n☕ Coffee Integration: ❌ NOT FOUND")
            print(f"   The injection wasn't integrated into the response")
            
        return result['semantic_delta']['is_within_bounds']
    else:
        print(f"   ❌ Failed: {response.json()}")
        return False

def main():
    print("🌟 Testing NearGravity Coffee Injection")
    print("Making sure coffee ads appear in morning motivation content")
    print("")
    
    try:
        # Test server availability
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Start it with:")
            print("   python3 src/rag/ag_ui/server.py")
            return
        
        # Run test
        success = test_coffee_injection()
        
        if success:
            print(f"\n🎉 SUCCESS: Coffee injection working with lowered thresholds!")
            print(f"📊 Semantic integrity maintained while allowing relevant ads")
        else:
            print(f"\n⚠️ Coffee injection still not appearing in content")
            print(f"🔧 May need further threshold adjustment or debugging")
            
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running:")
        print("   python3 src/rag/ag_ui/server.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    main()