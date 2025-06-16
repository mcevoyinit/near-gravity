#!/usr/bin/env python3
"""
NearGravity RAG API Server
Run this to start the RAG service for testing
"""
import os
import sys

# Add src to Python path (from rag/scripts directory)
project_root = os.path.join(os.path.dirname(__file__), '../../../..')
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from flask import Flask
from rag.api.rag_routes import rag_bp

def create_app():
    """Create Flask application with RAG routes"""
    app = Flask(__name__)
    
    # Register RAG blueprint
    app.register_blueprint(rag_bp, url_prefix='/api/v1/rag')
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            "service": "NearGravity RAG API",
            "status": "running",
            "endpoints": {
                "generate": "/api/v1/rag/generate",
                "inject": "/api/v1/rag/inject", 
                "verify": "/api/v1/rag/verify",
                "injections": "/api/v1/rag/injections",
                "metrics": "/api/v1/rag/metrics",
                "health": "/api/v1/rag/health"
            }
        }
    
    return app

if __name__ == '__main__':
    print("🚀 Starting NearGravity RAG API...")
    print("📊 This will auto-download the embedding model (~130MB) on first use")
    print("🔑 Set OPENAI_API_KEY environment variable for LLM generation")
    print()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. LLM generation may fail.")
        print("   Set with: export OPENAI_API_KEY='your-key-here'")
        print()
    
    app = create_app()
    
    print("🌐 API will be available at:")
    print("   http://localhost:5000")
    print("   http://localhost:5000/api/v1/rag/health")
    print()
    print("📚 Example usage:")
    print("   curl -X POST http://localhost:5000/api/v1/rag/generate \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"I need coffee recommendations\", \"user_id\": \"test\"}'")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)