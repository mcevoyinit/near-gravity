#!/bin/bash

# NearGravity AG-UI Demo - Updated for rag/ directory
echo "🌟 NEARGRAVITY AG-UI PROTOCOL DEMO"
echo "World's First Semantic Advertising Protocol"
echo "Powered by AG-UI Real-time Streaming"
echo "=========================================="

# Set environment
# Load environment variables if available
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY="your_openai_api_key"
    echo "⚠️  Warning: Using placeholder API key. Set OPENAI_API_KEY or create .env file."
fi
export TOKENIZERS_PARALLELISM=false

echo "✅ Environment configured"
echo "📁 Using updated rag/ directory structure"
echo ""

# Check if server is already running
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "🌐 Server already running at http://localhost:5000"
    echo "🚀 Launching demo scenarios..."
    echo ""
    python3 ../ag_ui/demo_launcher.py
else
    echo "🚀 Starting NearGravity AG-UI server..."
    echo ""
    echo "📱 Open in your browser: http://localhost:5000"
    echo "📡 Real-time events will stream automatically"
    echo "🎯 Use the dual-panel interface to:"
    echo "   • Left: Add advertising campaigns" 
    echo "   • Right: Send user queries"
    echo ""
    echo "🎬 Starting server now..."
    echo ""
    
    # Start the server (from rag/scripts directory)
    python3 ../ag_ui/server.py
fi