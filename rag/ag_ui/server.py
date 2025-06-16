"""
NearGravity AG-UI Server
Flask server with SSE support for AG-UI protocol streaming
"""
import os
import sys
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Import from current rag directory
current_dir = os.path.dirname(__file__)
rag_dir = os.path.dirname(current_dir)
sys.path.insert(0, rag_dir)

try:
    from enhanced_rag_processor import EnhancedRAGProcessor
    from vector_store_service import VectorStoreService
    from ag_ui.ag_ui_adapter import NearGravityAGUIAdapter, AGUIEvent
    from backend.agentic.agent_model import AgentConfig, AgentMessage
    from models.entities.python.data_models import InjectionMessage
except ImportError:
    # Fallback imports with full paths
    from src.rag.enhanced_rag_processor import EnhancedRAGProcessor
    from src.rag.vector_store_service import VectorStoreService
    from src.rag.ag_ui.ag_ui_adapter import NearGravityAGUIAdapter, AGUIEvent
    from src.backend.agentic.agent_model import AgentConfig, AgentMessage
    from src.models.entities.python.data_models import InjectionMessage

class NearGravityAGUIServer:
    """
    Flask server that integrates NearGravity RAG with AG-UI protocol
    Provides dual-panel interface and real-time event streaming
    """
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend
        
        # AG-UI Adapter (initialize first)
        self.ag_ui = NearGravityAGUIAdapter()
        self.ag_ui.subscribe(self._handle_ag_ui_event)
        
        # Event streaming
        self._event_subscribers = []
        self._events_lock = threading.Lock()
        
        # Initialize NearGravity components
        self._init_NearGravity()
        
        # Setup routes
        self._setup_routes()
    
    def _init_NearGravity(self):
        """Initialize NearGravity RAG components"""
        config = AgentConfig(
            name="NearGravityAGUI",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000,
            system_prompt="You are NearGravity's semantic advertising system.",
            thread_pool_size=3
        )
        
        self.rag_processor = EnhancedRAGProcessor(config)
        self.vector_store = VectorStoreService(use_faiss=False)
        
        # Start AG-UI session
        self.ag_ui.start_rag_session()
    
    def _handle_ag_ui_event(self, event: AGUIEvent):
        """Handle AG-UI events and broadcast to subscribers"""
        with self._events_lock:
            event_data = f"data: {json.dumps(event.to_dict())}\n\n"
            
            # Remove disconnected subscribers
            active_subscribers = []
            for subscriber in self._event_subscribers:
                try:
                    subscriber.put(event_data)
                    active_subscribers.append(subscriber)
                except:
                    # Subscriber disconnected
                    pass
            
            self._event_subscribers = active_subscribers
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve the main AG-UI interface"""
            return self._get_frontend_html()
        
        @self.app.route('/api/events')
        def events():
            """SSE endpoint for AG-UI events"""
            def event_stream():
                import queue
                
                # Create subscriber queue
                subscriber_queue = queue.Queue()
                
                with self._events_lock:
                    self._event_subscribers.append(subscriber_queue)
                
                # Send initial state
                initial_event = AGUIEvent(
                    event_type="state_update",
                    data=self.ag_ui.get_system_metrics()
                )
                yield f"data: {json.dumps(initial_event.to_dict())}\n\n"
                
                try:
                    while True:
                        try:
                            # Get event from queue (blocking)
                            event_data = subscriber_queue.get(timeout=30)
                            yield event_data
                        except queue.Empty:
                            # Send keepalive
                            yield "data: {\"type\": \"keepalive\"}\n\n"
                except GeneratorExit:
                    # Client disconnected
                    with self._events_lock:
                        if subscriber_queue in self._event_subscribers:
                            self._event_subscribers.remove(subscriber_queue)
            
            return Response(
                event_stream(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        
        @self.app.route('/api/inject', methods=['POST'])
        def add_injection():
            """Add injection message (Campaign Panel)"""
            try:
                data = request.get_json()
                
                # Validate input
                if not data or 'content' not in data or 'provider_id' not in data:
                    return jsonify({"error": "Missing required fields"}), 400
                
                # Create injection
                injection = InjectionMessage(
                    message_id=f"inj_{int(time.time() * 1000)}",
                    content=data['content'],
                    provider_id=data['provider_id'],
                    metadata=data.get('metadata', {})
                )
                
                # Generate embedding and store
                embedding = self.rag_processor._generate_embedding(injection.content)
                message_id = self.vector_store.add_message(injection, embedding, injection.metadata)
                
                # Add to processor
                self.rag_processor.add_injection_message(
                    content=injection.content,
                    provider_id=injection.provider_id,
                    metadata=injection.metadata
                )
                
                # Notify AG-UI
                self.ag_ui.injection_added({
                    "injection_id": message_id,
                    "content": injection.content,
                    "provider_id": injection.provider_id,
                    "metadata": injection.metadata
                })
                
                return jsonify({
                    "status": "success",
                    "injection_id": message_id
                }), 201
                
            except Exception as e:
                self.ag_ui.error_occurred(f"Failed to add injection: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/generate', methods=['POST'])
        def generate_content():
            """Generate content with RAG (User Intent Panel)"""
            try:
                data = request.get_json()
                
                if not data or 'message' not in data:
                    return jsonify({"error": "Missing message field"}), 400
                
                user_message = data['message']
                user_id = data.get('user_id', 'demo_user')
                
                # Notify AG-UI of user query
                self.ag_ui.user_query_received(user_message, user_id)
                
                # Create AgentMessage
                agent_message = AgentMessage(
                    content=user_message,
                    role="user",
                    metadata={
                        "user_id": user_id,
                        "modality": data.get("modality", "text"),
                        "modality_params": data.get("modality_params", {})
                    }
                )
                
                # Process with instrumented RAG
                result = self._process_with_ag_ui_events(agent_message)
                
                return jsonify({
                    "status": "success",
                    "content": result['result'].content,
                    "semantic_delta": {
                        "cosine_similarity": result['semantic_verification'].cosine_similarity,
                        "composite_delta": result['semantic_verification'].composite_delta,
                        "is_within_bounds": result['semantic_verification'].is_within_bounds
                    },
                    "processing_time_ms": result['result'].metadata.get('processing_time_ms'),
                    "injection_count": result.get("injection_candidates", 0)
                }), 200
                
            except Exception as e:
                self.ag_ui.error_occurred(f"Content generation failed: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/injections', methods=['GET'])
        def list_injections():
            """List all injections"""
            try:
                messages = self.vector_store.get_all_messages()
                return jsonify({
                    "status": "success",
                    "injections": [
                        {
                            "injection_id": msg.message_id,
                            "content": msg.content,
                            "provider_id": msg.provider_id,
                            "metadata": msg.metadata
                        }
                        for msg in messages
                    ],
                    "total": len(messages)
                }), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/metrics', methods=['GET'])
        def get_metrics():
            """Get system metrics"""
            try:
                processor_metrics = self.rag_processor.get_metrics()
                store_stats = self.vector_store.get_statistics()
                ag_ui_metrics = self.ag_ui.get_system_metrics()
                
                return jsonify({
                    "status": "success",
                    "processor_metrics": processor_metrics,
                    "store_statistics": store_stats,
                    "ag_ui_state": ag_ui_metrics
                }), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def _process_with_ag_ui_events(self, message: AgentMessage) -> Dict[str, Any]:
        """Process RAG request with AG-UI event emission"""
        start_time = time.time()
        
        # Step 1: Embedding Generation
        self.ag_ui.embedding_generated(
            text=message.content,
            embedding_dim=384,
            processing_time_ms=(time.time() - start_time) * 1000
        )
        
        # Step 2: Process through RAG (this will trigger more events)
        result = self.rag_processor.process(message)
        
        # Step 3: Emit completion
        self.ag_ui.rag_processing_complete({
            "content": result['result'].content,
            "metadata": result['result'].metadata
        })
        
        return result
    
    def _get_frontend_html(self):
        """Get the AG-UI frontend HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NearGravity - Semantic Advertising Protocol</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header h1 {
            color: #4a5568;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .header p {
            color: #718096;
            margin-top: 0.25rem;
        }
        
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
            min-height: calc(100vh - 120px);
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .panel h2 {
            color: #4a5568;
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #4a5568;
            font-weight: 500;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .events-log {
            background: #1a202c;
            border-radius: 8px;
            padding: 1rem;
            height: 300px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
            margin-top: 1rem;
        }
        
        .event {
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-radius: 4px;
            border-left: 3px solid #4299e1;
        }
        
        .event.agent_start { border-left-color: #48bb78; }
        .event.agent_step { border-left-color: #4299e1; }
        .event.agent_tool_call { border-left-color: #ed8936; }
        .event.completion { border-left-color: #9f7aea; }
        .event.error { border-left-color: #f56565; }
        
        .event-type {
            color: #a0aec0;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        
        .event-content {
            color: #e2e8f0;
            margin-top: 0.25rem;
        }
        
        .injections-list {
            max-height: 200px;
            overflow-y: auto;
            margin-top: 1rem;
        }
        
        .injection-item {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .injection-provider {
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.25rem;
        }
        
        .injection-content {
            color: #718096;
            font-size: 0.9rem;
        }
        
        .response-area {
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            min-height: 100px;
        }
        
        .semantic-score {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }
        
        .score-good { color: #48bb78; }
        .score-warning { color: #ed8936; }
        .score-bad { color: #f56565; }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-left: 0.5rem;
        }
        
        .status-active { background: #48bb78; animation: pulse 2s infinite; }
        .status-idle { background: #a0aec0; }
        .status-processing { background: #ed8936; animation: pulse 1s infinite; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌟 NearGravity - Semantic Advertising Protocol</h1>
        <p>World's first semantic integrity advertising system powered by AG-UI</p>
    </div>
    
    <div class="container">
        <!-- Campaign Panel (Left) -->
        <div class="panel">
            <h2>💉 Campaign Management <span class="status-indicator status-idle" id="campaign-status"></span></h2>
            
            <form id="injection-form">
                <div class="form-group">
                    <label>Campaign Content</label>
                    <textarea id="injection-content" placeholder="e.g., Try our premium Colombian coffee beans for the perfect morning brew!" required></textarea>
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
                
                <div class="form-group">
                    <label>Tags (comma-separated)</label>
                    <input type="text" id="tags" placeholder="coffee, morning, premium">
                </div>
                
                <button type="submit" class="btn">🚀 Add Campaign</button>
            </form>
            
            <div class="injections-list" id="injections-list">
                <!-- Injections will appear here -->
            </div>
        </div>
        
        <!-- User Intent Panel (Right) -->
        <div class="panel">
            <h2>🧠 User Intent Processing <span class="status-indicator status-idle" id="processing-status"></span></h2>
            
            <form id="query-form">
                <div class="form-group">
                    <label>User Message</label>
                    <textarea id="user-message" placeholder="e.g., I need morning motivation and energy to start my productive day" required></textarea>
                </div>
                
                <div class="grid-2">
                    <div class="form-group">
                        <label>User ID</label>
                        <input type="text" id="user-id" value="demo_user" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Modality</label>
                        <select id="modality">
                            <option value="text">Text</option>
                            <option value="code">Code</option>
                            <option value="structured">Structured</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="btn">🤖 Generate Content</button>
            </form>
            
            <div class="response-area" id="response-area">
                <em>Generated content will appear here...</em>
            </div>
        </div>
    </div>
    
    <!-- Events Log (Full Width) -->
    <div style="padding: 0 2rem 2rem;">
        <div class="panel">
            <h2>📡 Real-time Event Stream</h2>
            <div class="events-log" id="events-log">
                <div class="event">
                    <div class="event-type">system</div>
                    <div class="event-content">AG-UI Protocol initialized. Waiting for events...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // AG-UI Event Stream Connection
        let eventSource = null;
        let isProcessing = false;
        
        function initEventStream() {
            eventSource = new EventSource('/api/events');
            
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    handleAGUIEvent(data);
                } catch (e) {
                    console.log('Keepalive or invalid JSON:', event.data);
                }
            };
            
            eventSource.onerror = function(event) {
                console.error('EventSource failed:', event);
                updateProcessingStatus('error');
            };
        }
        
        function handleAGUIEvent(event) {
            addEventToLog(event);
            
            // Update UI based on event type
            switch(event.event_type) {
                case 'agent_start':
                    updateProcessingStatus('active');
                    break;
                    
                case 'user_input':
                    updateProcessingStatus('processing');
                    break;
                    
                case 'completion':
                    updateProcessingStatus('active');
                    displayGeneratedContent(event.data);
                    break;
                    
                case 'agent_error':
                    updateProcessingStatus('error');
                    break;
                    
                case 'state_update':
                    updateCampaignStatus(event.data);
                    break;
            }
        }
        
        function addEventToLog(event) {
            const log = document.getElementById('events-log');
            const eventEl = document.createElement('div');
            eventEl.className = `event ${event.event_type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const eventType = event.event_type.replace('_', ' ');
            let content = '';
            
            switch(event.event_type) {
                case 'agent_start':
                    content = `🚀 ${event.data.agent_name} started`;
                    break;
                case 'user_input':
                    content = `👤 User query: "${event.data.message.substring(0, 50)}..."`;
                    break;
                case 'agent_step':
                    content = `🔄 ${event.data.step_description}`;
                    break;
                case 'agent_tool_call':
                    content = `🛠️ ${event.data.tool_description}`;
                    break;
                case 'completion':
                    content = `✅ Content generated successfully`;
                    break;
                case 'agent_error':
                    content = `❌ ${event.data.error_message}`;
                    break;
                default:
                    content = JSON.stringify(event.data).substring(0, 100);
            }
            
            eventEl.innerHTML = `
                <div class="event-type">${timestamp} - ${eventType}</div>
                <div class="event-content">${content}</div>
            `;
            
            log.appendChild(eventEl);
            log.scrollTop = log.scrollHeight;
        }
        
        function updateProcessingStatus(status) {
            const indicator = document.getElementById('processing-status');
            indicator.className = `status-indicator status-${status}`;
        }
        
        function updateCampaignStatus(data) {
            const indicator = document.getElementById('campaign-status');
            const state = data.agent_state || {};
            
            if (state.injections_count > 0) {
                indicator.className = 'status-indicator status-active';
            } else {
                indicator.className = 'status-indicator status-idle';
            }
            
            loadInjections();
        }
        
        function displayGeneratedContent(data) {
            const responseArea = document.getElementById('response-area');
            const content = data.content || '';
            const summary = data.processing_summary || {};
            
            let semanticClass = 'score-good';
            if (summary.semantic_score < 0.7) semanticClass = 'score-bad';
            else if (summary.semantic_score < 0.8) semanticClass = 'score-warning';
            
            responseArea.innerHTML = `
                <div style="font-weight: 600; margin-bottom: 0.5rem;">Generated Content:</div>
                <div style="margin-bottom: 1rem;">${content}</div>
                <div class="semantic-score ${semanticClass}">
                    🧠 Semantic Score: ${(summary.semantic_score || 0).toFixed(3)}
                    ${summary.quality_verified ? '✅' : '⚠️'}
                </div>
                <div style="font-size: 0.8rem; color: #718096; margin-top: 0.5rem;">
                    Processing time: ${summary.total_time_ms || 0}ms
                </div>
            `;
        }
        
        async function loadInjections() {
            try {
                const response = await fetch('/api/injections');
                const data = await response.json();
                
                const list = document.getElementById('injections-list');
                
                if (data.injections && data.injections.length > 0) {
                    list.innerHTML = data.injections.map(injection => `
                        <div class="injection-item">
                            <div class="injection-provider">${injection.provider_id}</div>
                            <div class="injection-content">${injection.content.substring(0, 100)}...</div>
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = '<div style="text-align: center; color: #a0aec0; padding: 2rem;">No campaigns added yet</div>';
                }
            } catch (error) {
                console.error('Failed to load injections:', error);
            }
        }
        
        // Form handlers
        document.getElementById('injection-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const content = document.getElementById('injection-content').value;
            const providerId = document.getElementById('provider-id').value;
            const bidAmount = parseFloat(document.getElementById('bid-amount').value) || 0;
            const tags = document.getElementById('tags').value.split(',').map(t => t.trim()).filter(t => t);
            
            try {
                const response = await fetch('/api/inject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content,
                        provider_id: providerId,
                        metadata: {
                            bid_amount: bidAmount,
                            tags,
                            category: tags[0] || 'general'
                        }
                    })
                });
                
                if (response.ok) {
                    document.getElementById('injection-form').reset();
                    loadInjections();
                } else {
                    const error = await response.json();
                    alert('Failed to add campaign: ' + error.error);
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            }
        });
        
        document.getElementById('query-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (isProcessing) return;
            isProcessing = true;
            
            const message = document.getElementById('user-message').value;
            const userId = document.getElementById('user-id').value;
            const modality = document.getElementById('modality').value;
            
            const submitBtn = e.target.querySelector('button');
            submitBtn.disabled = true;
            submitBtn.textContent = '🔄 Processing...';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message,
                        user_id: userId,
                        modality
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Generation failed');
                }
                
            } catch (error) {
                alert('Generation failed: ' + error.message);
                updateProcessingStatus('error');
            } finally {
                isProcessing = false;
                submitBtn.disabled = false;
                submitBtn.textContent = '🤖 Generate Content';
            }
        });
        
        // Initialize
        initEventStream();
        loadInjections();
        
        // Example data
        document.getElementById('injection-content').value = "Try our premium Colombian coffee beans for the perfect morning brew! Ethically sourced, expertly roasted.";
        document.getElementById('provider-id').value = "blue_bottle_coffee";
        document.getElementById('bid-amount').value = "0.002";
        document.getElementById('tags').value = "coffee, morning, premium, ethical";
        
        document.getElementById('user-message').value = "I need some morning motivation and energy to start my productive workday. Any tips?";
    </script>
</body>
</html>
        """
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the server"""
        print("🌟 Starting NearGravity AG-UI Server...")
        print(f"🌐 Interface: http://localhost:{port}")
        print(f"📡 Events: http://localhost:{port}/api/events")
        print("🚀 Ready for semantic advertising demos!")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    # Fix tokenizer warning
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    # Load environment variables from .env file
    from pathlib import Path
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Set OpenAI API key if not set
    if not os.getenv('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = "your_openai_api_key"
    
    print(f"🔑 API Key status: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
    
    server = NearGravityAGUIServer()
    port = int(os.getenv('PORT', 5001))  # Default to 5001
    server.run(port=port, debug=False)