#!/usr/bin/env python3
"""
Direct OpenAI API test (bypassing LiteLLM)
"""
import os
import requests
import json

# Set API key
api_key = "your_openai_api_key"

def test_direct_openai():
    """Test OpenAI API directly with requests"""
    print("🔑 Testing Direct OpenAI API Connection...")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Say 'Hello from direct OpenAI API!'"}
        ],
        "max_tokens": 50
    }
    
    try:
        print("📡 Making direct API request...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("✅ Direct OpenAI API: SUCCESS")
            print(f"Response: {content}")
            return True
        else:
            print("❌ Direct OpenAI API: FAILED")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_api_key_validity():
    """Test if API key is valid"""
    print("\n🔍 Testing API Key Validity...")
    
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API Key is valid")
            models = response.json()
            gpt4_available = any('gpt-4' in model['id'] for model in models['data'])
            print(f"GPT-4 Available: {'✅' if gpt4_available else '❌'}")
            return True
        elif response.status_code == 401:
            print("❌ API Key is invalid or expired")
            return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking API key: {e}")
        return False

def main():
    print("🧪 OpenAI API Diagnostic Test")
    print("=" * 40)
    
    # Test 1: API Key validity
    key_valid = test_api_key_validity()
    
    if not key_valid:
        print("\n💡 Possible solutions:")
        print("   1. Check if API key is correct")
        print("   2. Verify API key hasn't expired")
        print("   3. Check OpenAI account has credits")
        print("   4. Visit: https://platform.openai.com/api-keys")
        return
    
    # Test 2: Direct API call
    api_working = test_direct_openai()
    
    if api_working:
        print("\n🎉 OpenAI API is working correctly!")
        print("The issue might be with LiteLLM or the Flask server context.")
        print("\n💡 Possible solutions:")
        print("   1. Try bypassing LiteLLM")
        print("   2. Check Flask server environment")
        print("   3. Test with different model (gpt-3.5-turbo)")
    else:
        print("\n❌ Direct API call failed")
        print("There might be a network or account issue.")

if __name__ == '__main__':
    main()