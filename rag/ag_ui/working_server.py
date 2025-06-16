#!/usr/bin/env python3
"""
Working NearGravity Demo Server
Uses direct OpenAI API calls instead of LiteLLM
"""
import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import numpy as np

# Fix tokenizer warning first
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from backend.agentic.agent_embeddings import EmbeddingManager
from models.entities.python.data_models import InjectionMessage

class WorkingRAGServer:
    """RAG server with direct OpenAI API calls"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Simple storage
        self.injections = []
        self.embeddings = []
        
        # Embedding manager
        self.embedding_manager = EmbeddingManager()
        
        # OpenAI API config
        self.api_key = os.getenv('OPENAI_API_KEY', "your_openai_api_key").strip()
        
        # Setup routes
        self._setup_routes()
    
    def _call_openai_api(self, messages, model="gpt-4", max_tokens=500):
        """Direct OpenAI API call"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API Error: {response.status_code} - {response.text}")
    
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
                
                print(f"✅ Added injection: {injection['provider_id']}")
                
                return jsonify({
                    "status": "success",
                    "injection_id": injection["injection_id"]
                }), 201
                
            except Exception as e:
                print(f"❌ Add injection error: {e}")
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
                
                print(f"🧠 Processing query: {user_message[:50]}...")
                
                # Generate user embedding
                user_embedding = self.embedding_manager.embed_text(user_message)
                
                # Find best injection
                best_injection = None
                best_similarity = 0
                
                if self.injections and self.embeddings:
                    for i, (injection, embedding) in enumerate(zip(self.injections, self.embeddings)):
                        similarity = self.embedding_manager.similarity(user_embedding[0], embedding)
                        
                        print(f"   Similarity with {injection['provider_id']}: {similarity:.3f}")
                        
                        if similarity > best_similarity and similarity > 0.60:  # Lower threshold for demo
                            best_similarity = similarity
                            best_injection = injection
                
                # Create prompt with injection
                if best_injection:
                    # Natural integration prompt
                    combined_prompt = f"""User asks: "{user_message}"

Please provide helpful advice. Also naturally mention this relevant option: "{best_injection['content']}"

Make the mention feel natural and helpful, not like an advertisement."""
                    
                    injection_info = f"Used injection from {best_injection['provider_id']} (similarity: {best_similarity:.3f})"
                    print(f"✅ {injection_info}")
                else:
                    combined_prompt = user_message
                    injection_info = "No relevant injection found"
                    print("⚠️ No injection used")
                
                # Generate with direct OpenAI API
                messages = [
                    {"role": "system", "content": "You are a helpful assistant providing practical advice. When relevant options are mentioned, integrate them naturally into your helpful response."},
                    {"role": "user", "content": combined_prompt}
                ]
                
                start_time = time.time()
                
                print("🤖 Calling OpenAI API...")
                generated_content = self._call_openai_api(messages)
                
                processing_time = (time.time() - start_time) * 1000
                print(f"✅ Generated content in {processing_time:.0f}ms")
                
                # Simple semantic verification
                if best_injection:
                    original_emb = self.embedding_manager.embed_text(user_message)
                    generated_emb = self.embedding_manager.embed_text(generated_content)
                    semantic_similarity = self.embedding_manager.similarity(original_emb[0], generated_emb[0])
                    within_bounds = semantic_similarity > 0.60  # Lower threshold for demo
                else:
                    semantic_similarity = 1.0
                    within_bounds = True
                
                print(f"🧠 Semantic similarity: {semantic_similarity:.3f} ({'✅' if within_bounds else '❌'})")
                
                return jsonify({
                    "status": "success",
                    "content": str(generated_content),
                    "semantic_delta": {
                        "cosine_similarity": float(semantic_similarity),
                        "composite_delta": float(semantic_similarity),
                        "is_within_bounds": bool(within_bounds)
                    },
                    "processing_time_ms": float(processing_time),
                    "injection_used": str(injection_info),
                    "best_similarity": float(best_similarity) if best_injection else 0.0
                }), 200
                
            except Exception as e:
                print(f"❌ Generation error: {e}")
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
                "api_key_set": bool(self.api_key)
            }), 200
    
    def _get_frontend_html(self):
        """Get frontend HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>☕ NearGravity - Coffee Injection Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); min-height: 100vh; }
        .header { background: rgba(255, 255, 255, 0.95); padding: 1.5rem 2rem; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }
        .header h1 { color: #8B4513; font-size: 2rem; display: flex; align-items: center; gap: 0.5rem; }
        .header p { color: #A0522D; margin-top: 0.5rem; font-size: 1.1rem; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; padding: 2rem; max-width: 1200px; margin: 0 auto; }
        .panel { background: rgba(255, 255, 255, 0.95); border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .panel h2 { color: #8B4513; margin-bottom: 1.5rem; font-size: 1.4rem; display: flex; align-items: center; gap: 0.5rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; color: #8B4513; font-weight: 600; }
        input, textarea { width: 100%; padding: 0.75rem; border: 2px solid #DEB887; border-radius: 8px; font-size: 1rem; }
        input:focus, textarea:focus { outline: none; border-color: #8B4513; }
        textarea { resize: vertical; min-height: 80px; }
        .btn { background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-size: 1rem; cursor: pointer; width: 100%; font-weight: 600; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .response-area { background: #FFF8DC; border: 2px solid #DEB887; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; min-height: 120px; }
        .injections-list { max-height: 200px; overflow-y: auto; margin-top: 1rem; }
        .injection-item { background: #FFF8DC; border: 2px solid #DEB887; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; }
        .injection-provider { font-weight: 600; color: #8B4513; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.5rem; }
        .semantic-score { margin-top: 1rem; font-size: 0.9rem; font-weight: 600; }
        .score-good { color: #228B22; }
        .score-warning { color: #FF8C00; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .success { background: #90EE90; border: 2px solid #228B22; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
        .coffee-highlight { background: linear-gradient(135deg, #8B4513, #D2691E); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>☕ NearGravity Coffee Demo</h1>
        <p>🎯 Watch semantic advertising in action - Coffee shops meet morning motivation!</p>
    </div>
    
    <div class="container">
        <!-- Campaign Panel -->
        <div class="panel">
            <h2>☕ Coffee Shop Campaign</h2>
            
            <form id="injection-form">
                <div class="form-group">
                    <label>☕ Coffee Campaign Content</label>
                    <textarea id="injection-content" placeholder="Describe your coffee offering..." required>Start your morning with Blue Bottle Coffee's premium single-origin beans - hand-roasted for maximum energy and focus throughout your productive workday!</textarea>
                </div>
                
                <div class="grid-2">
                    <div class="form-group">
                        <label>🏪 Coffee Shop ID</label>
                        <input type="text" id="provider-id" value="blue_bottle_coffee" required>
                    </div>
                    
                    <div class="form-group">
                        <label>💰 Bid Amount ($)</label>
                        <input type="number" id="bid-amount" step="0.001" value="0.005" min="0">
                    </div>
                </div>
                
                <button type="submit" class="btn">☕ Launch Coffee Campaign</button>
            </form>
            
            <div class="injections-list" id="injections-list"></div>
        </div>
        
        <!-- User Intent Panel -->
        <div class="panel">
            <h2>🧠 User Morning Query</h2>
            
            <form id="query-form">
                <div class="form-group">
                    <label>💭 User's Morning Question</label>
                    <textarea id="user-message" required>I need some morning motivation and energy to start my productive workday. I feel sluggish and need tips to get energized. What should I do?</textarea>
                </div>
                
                <div class="form-group">
                    <label>👤 User ID</label>
                    <input type="text" id="user-id" value="morning_person_123" required>
                </div>
                
                <button type="submit" class="btn">🤖 Get Morning Advice</button>
            </form>
            
            <div class="response-area" id="response-area">
                <em>🌅 Enhanced morning advice with coffee recommendations will appear here...</em>
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
                            <div class="injection-provider">☕ ${injection.provider_id}</div>
                            <div>${injection.content}</div>
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = '<div style="text-align: center; color: #A0522D; padding: 1rem;">No coffee campaigns yet ☕</div>';
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
                        metadata: { bid_amount: bidAmount, category: 'coffee' }
                    })
                });
                
                if (response.ok) {
                    loadInjections();
                    document.getElementById('injections-list').innerHTML = '<div class="success">☕ Coffee campaign launched successfully! Now try the morning query →</div>';
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
            submitBtn.textContent = '☕ Brewing response...';
            
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
                    
                    // Highlight coffee mentions
                    let content = data.content;
                    const coffeeWords = ['coffee', 'Coffee', 'Blue Bottle', 'beans', 'roasted', 'caffeine', 'brew'];
                    coffeeWords.forEach(word => {
                        const regex = new RegExp(`\\b${word}\\b`, 'g');
                        content = content.replace(regex, `<span class="coffee-highlight">${word}</span>`);
                    });
                    
                    responseArea.innerHTML = `
                        <div style="font-weight: 600; margin-bottom: 1rem; color: #8B4513;">🌅 Enhanced Morning Advice:</div>
                        <div style="margin-bottom: 1rem; line-height: 1.6;">${content}</div>
                        <div class="semantic-score ${scoreClass}">
                            🧠 Semantic Integrity: ${delta.cosine_similarity.toFixed(3)} ${delta.is_within_bounds ? '✅' : '⚠️'}
                        </div>
                        <div style="font-size: 0.85rem; color: #A0522D; margin-top: 0.5rem; font-style: italic;">
                            📊 ${data.injection_used} | ⚡ ${data.processing_time_ms.toFixed(0)}ms
                        </div>
                    `;
                } else {
                    throw new Error(data.error || 'Generation failed');
                }
                
            } catch (error) {
                document.getElementById('response-area').innerHTML = `<div style="color: red;">❌ Error: ${error.message}</div>`;
            } finally {
                isProcessing = false;
                submitBtn.disabled = false;
                submitBtn.textContent = '🤖 Get Morning Advice';
            }
        });
        
        // Initialize
        loadInjections();
    </script>
</body>
</html>
        """
    
    def run(self, host='0.0.0.0', port=4444):
        """Run the server"""
        print("☕ Starting Working NearGravity Coffee Demo...")
        print(f"🌐 Interface: http://localhost:{port}")
        print("🎯 Direct OpenAI API integration - No LiteLLM issues!")
        print("🚀 Ready to show coffee injection in action!")
        
        self.app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    print(f"🔑 API Key: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
    
    server = WorkingRAGServer()
    server.run()