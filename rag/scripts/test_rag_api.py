#!/usr/bin/env python3
"""
Test the NearGravity RAG API end-to-end
"""
import os
import sys
import json

# Add src to Python path (from rag/scripts directory)
project_root = os.path.join(os.path.dirname(__file__), '../../../..')
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from flask import Flask
from rag.api.rag_routes import rag_bp

def test_rag_system():
    """Test the RAG system directly without HTTP server"""
    print("🧪 Testing NearGravity RAG System...")
    
    # Create Flask app for testing
    app = Flask(__name__)
    app.register_blueprint(rag_bp, url_prefix='/api/v1/rag')
    
    with app.test_client() as client:
        
        # Test 1: Health Check
        print("\n1️⃣ Testing health endpoint...")
        response = client.get('/api/v1/rag/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test 2: Add an injection message
        print("\n2️⃣ Adding injection message...")
        injection_data = {
            "content": "Try our premium Colombian coffee beans for the perfect morning brew!",
            "provider_id": "coffee_shop_123",
            "metadata": {
                "category": "beverages",
                "bid_amount": 0.001,
                "tags": ["coffee", "morning", "premium"]
            }
        }
        
        response = client.post('/api/v1/rag/inject', 
                              json=injection_data,
                              content_type='application/json')
        print(f"Status: {response.status_code}")
        inject_result = response.get_json()
        print(f"Response: {inject_result}")
        
        # Test 3: List injections
        print("\n3️⃣ Listing injections...")
        response = client.get('/api/v1/rag/injections')
        print(f"Status: {response.status_code}")
        injections = response.get_json()
        print(f"Total injections: {injections.get('total', 0)}")
        
        # Test 4: Test semantic verification
        print("\n4️⃣ Testing semantic verification...")
        verify_data = {
            "original": "I need morning energy and motivation",
            "transformed": "I need morning energy and motivation. Try our premium Colombian coffee beans for the perfect morning brew!",
            "transformation_type": "default"
        }
        
        response = client.post('/api/v1/rag/verify',
                              json=verify_data,
                              content_type='application/json')
        print(f"Status: {response.status_code}")
        verify_result = response.get_json()
        print(f"Semantic delta: {verify_result}")
        
        # Test 5: Generate content (this will likely fail without OpenAI key)
        print("\n5️⃣ Testing content generation...")
        gen_data = {
            "message": "I need some morning motivation and energy to start my day productively",
            "user_id": "test_user_123",
            "modality": "text",
            "modality_params": {
                "style": "conversational",
                "length": "medium"
            }
        }
        
        response = client.post('/api/v1/rag/generate',
                              json=gen_data,
                              content_type='application/json')
        print(f"Status: {response.status_code}")
        gen_result = response.get_json()
        print(f"Generation result: {json.dumps(gen_result, indent=2)}")
        
        # Test 6: Get metrics
        print("\n6️⃣ Getting system metrics...")
        response = client.get('/api/v1/rag/metrics')
        print(f"Status: {response.status_code}")
        metrics = response.get_json()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")

if __name__ == '__main__':
    # Set a dummy OpenAI key to prevent warnings
    os.environ['OPENAI_API_KEY'] = 'sk-test-key-for-testing'
    
    test_rag_system()