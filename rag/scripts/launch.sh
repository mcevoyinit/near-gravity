#!/bin/bash

# NearGravity RAG Package Launcher
# Centralized launcher for all RAG demos and services

echo "🌟 NEARGRAVITY RAG PACKAGE"
echo "Semantic Advertising Protocol"
echo "================================"
echo "🔧 Auto-cleanup: Existing processes will be killed"
echo ""

# Function to kill process on port
kill_port() {
    local port=$1
    local process_name=$2
    echo "🔍 Checking port $port for existing processes..."
    
    # Find process on port and kill it
    local pid=$(lsof -ti tcp:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "⚡ Killing existing $process_name process (PID: $pid) on port $port"
        kill -9 $pid 2>/dev/null
        sleep 2
        echo "✅ Port $port cleared"
    else
        echo "✅ Port $port is available"
    fi
}

# Set environment
# Check if OPENAI_API_KEY is set, otherwise use placeholder
if [ -z "$OPENAI_API_KEY" ]; then
    # Load environment variables if available
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    export OPENAI_API_KEY="your_openai_api_key"
    echo "⚠️  Warning: Using placeholder API key. Set OPENAI_API_KEY or create .env file."
fi
    echo "⚠️  Warning: Using placeholder API key. Set OPENAI_API_KEY environment variable for real functionality."
fi
export TOKENIZERS_PARALLELISM=false

echo "Available demos:"
echo "1. 🌐 AG-UI Purple Interface (Recommended)"
echo "2. 🔧 API Server + Test Suite"
echo "3. 📊 Run Demo Scenarios"
echo ""

read -p "Choose demo (1-3): " choice

case $choice in
    1)
        echo "🚀 Starting AG-UI Purple Interface..."
        echo "📱 Will open at: http://localhost:5002"
        echo "🤖 Using DeepSeek R1 local model"
        echo "🎯 Test any campaign/message combinations!"
        echo ""
        
        # Kill any existing process on port 5002
        kill_port 5002 "AG-UI server"
        
        cd ../ag_ui
        PORT=5002 python3 server.py
        ;;
    2)
        echo "🔧 Starting API Server..."
        echo "📱 Server: http://localhost:5005"
        echo ""
        
        # Kill any existing process on port 5005
        kill_port 5005 "API server"
        
        cd ../../..
        python3 src/backend/api/app.py &
        sleep 3
        echo "🧪 Running Test Suite..."
        python3 src/rag/tests/test_rag_demo.py
        ;;
    3)
        echo "📊 Running Demo Scenarios on AG-UI..."
        
        # Check if AG-UI is running, if not start it
        if ! curl -s http://localhost:5002 > /dev/null 2>&1; then
            echo "🚀 AG-UI not running, starting it first..."
            kill_port 5002 "AG-UI server"
            cd ../ag_ui
            PORT=5002 python3 server.py &
            sleep 5
            echo "✅ AG-UI started, now launching demos..."
        else
            echo "✅ Server running, launching demos..."
        fi
        
        cd ../ag_ui
        python3 demo_launcher.py
        ;;
    *)
        echo "Invalid choice. Please run again and choose 1-3."
        ;;
esac