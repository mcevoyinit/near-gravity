#!/usr/bin/env python3
"""
Quick test of OpenAI API connection
"""
import os
import litellm

# Set API key
os.environ['OPENAI_API_KEY'] = "your_openai_api_key"

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔑 Testing OpenAI API Connection...")
    print(f"API Key: {os.getenv('OPENAI_API_KEY')[:20]}...{os.getenv('OPENAI_API_KEY')[-10:]}")
    
    try:
        response = litellm.completion(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say 'Hello from NearGravity!'"}],
            max_tokens=50
        )
        
        print("✅ OpenAI API Connection: SUCCESS")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Connection: FAILED")
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = test_openai_connection()
    
    if success:
        print("\n🎉 API is working! You can now start the NearGravity server:")
        print("   python3 src/rag/ag_ui/server.py")
    else:
        print("\n🔧 API connection failed. Possible issues:")
        print("   1. Check API key is correct")
        print("   2. Check internet connection") 
        print("   3. Check OpenAI service status")
        print("   4. Verify API key has credits")