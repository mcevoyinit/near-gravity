#!/usr/bin/env python3
"""
Test API key in Flask server context
"""
import os
import sys
import litellm
from flask import Flask, jsonify

# Fix tokenizer warning
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Set API key
os.environ['OPENAI_API_KEY'] = "your_openai_api_key"

app = Flask(__name__)

@app.route('/test-api')
def test_api():
    """Test API in Flask context"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"🔑 API Key in Flask: {api_key[:20]}...{api_key[-10:] if api_key else 'NONE'}")
        
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello from Flask!'"}],
            max_tokens=50,
            api_key=api_key
        )
        
        return jsonify({
            "status": "success",
            "content": response.choices[0].message.content,
            "api_key_length": len(api_key) if api_key else 0
        })
        
    except Exception as e:
        print(f"❌ API Error in Flask: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "api_key_set": bool(os.getenv('OPENAI_API_KEY'))
        }), 500

@app.route('/')
def index():
    return """
    <h1>API Test Server</h1>
    <p><a href="/test-api">Test OpenAI API</a></p>
    <p>Check console for debug output</p>
    """

if __name__ == '__main__':
    print(f"🔑 Starting with API key: {os.getenv('OPENAI_API_KEY')[:20]}...")
    app.run(port=5001, debug=True)