#!/usr/bin/env python3
"""
Simplified NearGravity AG-UI Server
Fixed threading and API connection issues
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import litellm
import numpy as np

# Fix tokenizer warning first
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from backend.agentic.agent_embeddings import EmbeddingManager
from models.entities.python.data_models import InjectionMessage

class SimpleRAGServer:
    """Simplified RAG server without complex threading"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Simple storage
        self.injections = []
        self.embeddings = []
        
        # Embedding manager
        self.embedding_manager = EmbeddingManager()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main interface"""
            return self._get_frontend_html()
        
        @self.app.route('/api/inject', methods=['POST'])
        def add_injection():
            """Add injection message"""
            try:
                data = request.get_json()
                
                if not data or 'content' not in data or 'provider_id' not in data:
                    return jsonify({"error": "Missing required fields"}), 400
                
                # Create injection
                injection = {
                    "injection_id": f"inj_{int(time.time() * 1000)}",
                    "content": data['content'],
                    "provider_id": data['provider_id'],
                    "metadata": data.get('metadata', {})
                }
                
                # Generate embedding
                embedding = self.embedding_manager.embed_text(injection['content'])
                
                # Store
                self.injections.append(injection)
                self.embeddings.append(embedding[0])
                
                return jsonify({
                    "status": "success",
                    "injection_id": injection["injection_id"]
                }), 201
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate_content():
            """Generate content with RAG"""
            try:
                data = request.get_json()
                
                if not data or 'message' not in data:
                    return jsonify({"error": "Missing message field"}), 400
                
                user_message = data['message']
                user_id = data.get('user_id', 'demo_user')
                
                # Generate user embedding
                user_embedding = self.embedding_manager.embed_text(user_message)
                
                # Find best injection
                best_injection = None
                best_similarity = 0
                
                if self.injections and self.embeddings:
                    for i, (injection, embedding) in enumerate(zip(self.injections, self.embeddings)):
                        similarity = self.embedding_manager.similarity(user_embedding[0], embedding)
                        
                        if similarity > best_similarity and similarity > 0.7:  # Threshold
                            best_similarity = similarity
                            best_injection = injection
                
                # Create prompt
                if best_injection:
                    combined_prompt = f"{user_message}\n\n[Relevant context: {best_injection['content']}]"
                    injection_info = f"Used injection from {best_injection['provider_id']}"
                else:
                    combined_prompt = user_message
                    injection_info = "No relevant injection found"
                
                # Generate with LiteLLM
                messages = [
                    {"role": "system", "content": "You are a helpful assistant. Provide clear, helpful advice."},
                    {"role": "user", "content": combined_prompt}
                ]
                
                start_time = time.time()
                
                # Debug API key
                api_key = os.getenv('OPENAI_API_KEY')
                print(f"🔑 Using API key: {api_key[:20]}...{api_key[-10:] if api_key else 'NONE'}")
                
                response = litellm.completion(
                    model="gpt-4",  # Using GPT-4 for better reliability
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                    api_key=api_key  # Explicitly pass API key
                )
                
                generated_content = response.choices[0].message.content
                processing_time = (time.time() - start_time) * 1000
                
                # Simple semantic verification
                if best_injection:
                    original_emb = self.embedding_manager.embed_text(user_message)
                    generated_emb = self.embedding_manager.embed_text(generated_content)
                    semantic_similarity = self.embedding_manager.similarity(original_emb[0], generated_emb[0])
                    within_bounds = semantic_similarity > 0.70  # Lowered threshold
                else:
                    semantic_similarity = 1.0
                    within_bounds = True
                
                return jsonify({
                    "status": "success",
                    "content": generated_content,
                    "semantic_delta": {
                        "cosine_similarity": float(semantic_similarity),
                        "composite_delta": float(semantic_similarity),
                        "is_within_bounds": within_bounds
                    },
                    "processing_time_ms": processing_time,
                    "injection_used": injection_info,
                    "best_similarity": float(best_similarity) if best_injection else 0
                }), 200
                
            except Exception as e:
                print(f"Generation error: {e}")
                return jsonify({"error": f"Generation failed: {str(e)}"}), 500
        
        @self.app.route('/api/injections', methods=['GET'])
        def list_injections():
            """List all injections"""
            return jsonify({
                "status": "success",
                "injections": self.injections,
                "total": len(self.injections)
            }), 200
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check"""
            return jsonify({
                "status": "healthy",
                "injections_count": len(self.injections),
                "api_key_set": bool(os.getenv('OPENAI_API_KEY'))
            }), 200
    
    def _get_frontend_html(self):
        """Get simplified frontend HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NearGravity - Semantic Advertising Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .header { background: rgba(255, 255, 255, 0.95); padding: 1rem 2rem; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }
        .header h1 { color: #4a5568; font-size: 1.8rem; }
        .header p { color: #718096; margin-top: 0.25rem; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; padding: 2rem; max-width: 1200px; margin: 0 auto; }
        .panel { background: rgba(255, 255, 255, 0.95); border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .panel h2 { color: #4a5568; margin-bottom: 1.5rem; font-size: 1.4rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; color: #4a5568; font-weight: 500; }
        input, textarea { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; }
        input:focus, textarea:focus { outline: none; border-color: #667eea; }
        textarea { resize: vertical; min-height: 80px; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-size: 1rem; cursor: pointer; width: 100%; }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .response-area { background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-top: 1rem; min-height: 100px; }
        .injections-list { max-height: 200px; overflow-y: auto; margin-top: 1rem; }
        .injection-item { background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; }
        .injection-provider { font-weight: 600; color: #4a5568; margin-bottom: 0.25rem; }
        .semantic-score { margin-top: 0.5rem; font-size: 0.9rem; }
        .score-good { color: #48bb78; }
        .score-warning { color: #ed8936; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>☕ NearGravity - Semantic Advertising Demo</h1>
        <p>Simplified version - Add campaigns and test semantic matching</p>
    </div>
    
    <div class="container">
        <!-- Campaign Panel -->
        <div class="panel">
            <h2>💉 Campaign Management</h2>
            
            <form id="injection-form">
                <div class="form-group">
                    <label>Campaign Content</label>
                    <textarea id="injection-content" placeholder="e.g., Try our premium Colombian coffee beans!" required></textarea>
                </div>
                
                <div class="grid-2">
                    <div class="form-group">
                        <label>Provider ID</label>
                        <input type="text" id="provider-id" placeholder="coffee_shop_123" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Bid Amount</label>
                        <input type="number" id="bid-amount" step="0.001" placeholder="0.001" min="0">
                    </div>
                </div>
                
                <button type="submit" class="btn">🚀 Add Campaign</button>
            </form>
            
            <div class="injections-list" id="injections-list"></div>
        </div>
        
        <!-- User Intent Panel -->
        <div class="panel">
            <h2>🧠 User Intent Processing</h2>
            
            <form id="query-form">
                <div class="form-group">
                    <label>User Message</label>
                    <textarea id="user-message" placeholder="e.g., I need morning motivation and energy" required></textarea>
                </div>
                
                <div class="form-group">
                    <label>User ID</label>
                    <input type="text" id="user-id" value="demo_user" required>
                </div>
                
                <button type="submit" class="btn">🤖 Generate Content</button>
            </form>
            
            <div class="response-area" id="response-area">
                <em>Generated content will appear here...</em>
            </div>
        </div>
    </div>

    <script>
        let isProcessing = false;
        
        // Load injections
        async function loadInjections() {
            try {
                const response = await fetch('/api/injections');
                const data = await response.json();
                
                const list = document.getElementById('injections-list');
                
                if (data.injections && data.injections.length > 0) {
                    list.innerHTML = data.injections.map(injection => `
                        <div class="injection-item">
                            <div class="injection-provider">${injection.provider_id}</div>
                            <div>${injection.content.substring(0, 100)}...</div>
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = '<div style="text-align: center; color: #a0aec0; padding: 1rem;">No campaigns yet</div>';
                }
            } catch (error) {
                console.error('Failed to load injections:', error);
            }
        }
        
        // Add injection
        document.getElementById('injection-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const content = document.getElementById('injection-content').value;
            const providerId = document.getElementById('provider-id').value;
            const bidAmount = parseFloat(document.getElementById('bid-amount').value) || 0;
            
            try {
                const response = await fetch('/api/inject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content,
                        provider_id: providerId,
                        metadata: { bid_amount: bidAmount }
                    })
                });
                
                if (response.ok) {
                    document.getElementById('injection-form').reset();
                    loadInjections();
                } else {
                    const error = await response.json();
                    alert('Failed: ' + error.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
        
        // Generate content
        document.getElementById('query-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (isProcessing) return;
            isProcessing = true;
            
            const message = document.getElementById('user-message').value;
            const userId = document.getElementById('user-id').value;
            
            const submitBtn = e.target.querySelector('button');
            submitBtn.disabled = true;
            submitBtn.textContent = '🔄 Processing...';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, user_id: userId })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const responseArea = document.getElementById('response-area');
                    const delta = data.semantic_delta;
                    
                    let scoreClass = 'score-good';
                    if (delta.cosine_similarity < 0.7) scoreClass = 'score-warning';
                    
                    responseArea.innerHTML = `
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">Generated Content:</div>
                        <div style="margin-bottom: 1rem;">${data.content}</div>
                        <div class="semantic-score ${scoreClass}">
                            🧠 Semantic Score: ${delta.cosine_similarity.toFixed(3)} ${delta.is_within_bounds ? '✅' : '⚠️'}
                        </div>
                        <div style="font-size: 0.8rem; color: #718096; margin-top: 0.5rem;">
                            ${data.injection_used} | Processing: ${data.processing_time_ms.toFixed(0)}ms
                        </div>
                    `;
                } else {
                    throw new Error(data.error || 'Generation failed');
                }
                
            } catch (error) {
                document.getElementById('response-area').innerHTML = `<div style="color: red;">Error: ${error.message}</div>`;
            } finally {
                isProcessing = false;
                submitBtn.disabled = false;
                submitBtn.textContent = '🤖 Generate Content';
            }
        });
        
        // Initialize
        loadInjections();
        
        // Example data
        document.getElementById('injection-content').value = "Start your morning with Blue Bottle Coffee's premium beans for sustained energy and focus!";
        document.getElementById('provider-id').value = "blue_bottle_coffee";
        document.getElementById('bid-amount').value = "0.002";
        document.getElementById('user-message').value = "I need morning motivation and energy to start my productive workday. Any tips?";
    </script>
</body>
</html>
        """
    
    def run(self, host='0.0.0.0', port=3333):
        """Run the server"""
        print("☕ Starting Simplified NearGravity Demo...")
        print(f"🌐 Interface: http://localhost:{port}")
        print("🚀 Ready for coffee injection demos!")
        
        self.app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    # Set API key
    if not os.getenv('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = "your_openai_api_key"
    
    print(f"🔑 API Key: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
    
    server = SimpleRAGServer()
    server.run()