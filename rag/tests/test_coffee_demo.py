#!/usr/bin/env python3
"""
Test the coffee injection demo
"""
import requests
import json
import time

def test_coffee_injection():
    """Test the full coffee injection flow"""
    base_url = "http://localhost:4444"
    
    # 1. Add coffee injection
    print("☕ Step 1: Adding coffee injection...")
    injection_data = {
        "content": "Start your morning with Blue Bottle Coffee premium single-origin beans - hand-roasted for maximum energy and focus throughout your productive workday!",
        "provider_id": "blue_bottle_coffee",
        "metadata": {
            "bid_amount": 0.005,
            "category": "coffee"
        }
    }
    
    response = requests.post(
        f"{base_url}/api/inject",
        headers={"Content-Type": "application/json"},
        json=injection_data
    )
    
    if response.status_code == 201:
        print("✅ Coffee injection added successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Failed to add injection: {response.status_code} - {response.text}")
        return False
    
    # 2. Test morning motivation query
    print("\n🌅 Step 2: Testing morning motivation query...")
    query_data = {
        "message": "I need some morning motivation and energy to start my productive workday. I feel sluggish and need tips to get energized. What should I do?",
        "user_id": "morning_person_123"
    }
    
    response = requests.post(
        f"{base_url}/api/generate",
        headers={"Content-Type": "application/json"},
        json=query_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Content generated successfully!")
        print(f"\n🤖 Generated Content:")
        print(f"{result['content']}")
        print(f"\n📊 Injection Info: {result['injection_used']}")
        print(f"🧠 Semantic Score: {result['semantic_delta']['cosine_similarity']:.3f}")
        print(f"⚡ Processing Time: {result['processing_time_ms']:.0f}ms")
        
        # Check if coffee is mentioned
        coffee_mentioned = any(word in result['content'].lower() for word in ['coffee', 'blue bottle', 'beans', 'caffeine'])
        print(f"\n☕ Coffee Injection Success: {'✅ YES' if coffee_mentioned else '❌ NO'}")
        
        return coffee_mentioned
    else:
        print(f"❌ Failed to generate content: {response.status_code} - {response.text}")
        return False

def main():
    print("🧪 Testing NearGravity Coffee Injection Demo")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:4444/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start it first:")
        print("   python3 src/rag/ag_ui/working_server.py")
        return
    
    # Run the test
    success = test_coffee_injection()
    
    if success:
        print("\n🎉 Coffee injection demo working perfectly!")
        print("🌐 Open http://localhost:4444 to see the full UI")
    else:
        print("\n⚠️ Coffee injection needs debugging")

if __name__ == '__main__':
    main()