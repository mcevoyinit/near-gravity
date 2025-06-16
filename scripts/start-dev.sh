#!/bin/bash
# Development startup script for NearGravity NEAR Semantic Guard

set -e

echo "🚀 Starting NearGravity NEAR Semantic Guard Development Environment"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the hack directory
HACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HACK_DIR"

echo -e "${BLUE}📁 Working directory: $HACK_DIR${NC}"

# Check Python dependencies
echo -e "${YELLOW}🔧 Checking Python dependencies...${NC}"
if ! python3 -c "import flask, flask_cors, requests" 2>/dev/null; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install flask flask-cors requests openai contracts-sdk-py
fi

# Check Node.js dependencies for frontend
echo -e "${YELLOW}🔧 Checking Node.js dependencies...${NC}"
if [ -d "frontend/shade-agent/node_modules" ]; then
    echo -e "${GREEN}✅ Node.js dependencies found${NC}"
else
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    cd frontend/shade-agent
    npm install
    cd "$HACK_DIR"
fi

# Start the backend API server
echo -e "${BLUE}🔥 Starting API Server (Backend)...${NC}"
cd api

# Try integrated app first, fallback to demo
if python3 -c "import sys; sys.path.insert(0, '..'); from agents.agent_manager import AgentManager" 2>/dev/null; then
    echo -e "${GREEN}✅ Full integration available - starting integrated app${NC}"
    python3 integrated_app.py &
else
    echo -e "${YELLOW}⚠️  Full integration not available - starting demo app${NC}"
    python3 demo_app.py &
fi

API_PID=$!
echo -e "${GREEN}✅ API Server started (PID: $API_PID)${NC}"

# Wait for API to be ready
echo -e "${YELLOW}⏳ Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5000/near/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API Server is ready!${NC}"
        break
    fi
    sleep 1
done

# Start the frontend
echo -e "${BLUE}🎨 Starting Frontend (UI)...${NC}"
cd "$HACK_DIR/frontend/shade-agent"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "${YELLOW}⏳ Waiting for frontend to be ready...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    sleep 1
done

echo ""
echo "🎉 Development Environment Ready!"
echo "=================================="
echo -e "${GREEN}🌐 Frontend UI: http://localhost:3000/semantic-guard${NC}"
echo -e "${GREEN}🔧 API Health: http://localhost:5000/near/health${NC}"
echo -e "${GREEN}📊 System Status: http://localhost:5000/near/status${NC}"
echo ""
echo -e "${BLUE}📋 Test Commands:${NC}"
echo "curl -X POST http://localhost:5000/near/semantic-guard \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"climate change latest research\", \"max_results\": 5}'"
echo ""
echo -e "${YELLOW}💡 Try these demo scenarios:${NC}"
echo "• High Trust: 'climate change latest research'"
echo "• Misinformation: 'covid vaccine safety'"
echo "• Mixed Signals: 'artificial intelligence jobs'"
echo "• Economic Uncertainty: 'economy recession 2024'"
echo ""
echo -e "${RED}🛑 To stop: kill $API_PID $FRONTEND_PID${NC}"

# Keep script running
wait