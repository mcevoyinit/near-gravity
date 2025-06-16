#!/bin/bash

echo "🚀 Starting NEAR Gravity Semantic Guard"
echo "======================================="

# Kill any existing processes on the ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3140 | xargs kill -9 2>/dev/null || true

echo "🔧 Starting API Server (port 5000)..."
python /Users/mcevoyinit/near/near-gravity/api/demo_app.py &
API_PID=$!

echo "🎨 Starting Frontend (port 3000)..."
npm run dev --prefix /Users/mcevoyinit/near/near-gravity/frontend/shade-agent &
FRONTEND_PID=$!

# Wait a bit for services to start
sleep 5

echo "✅ Services started!"
echo
echo "🎯 URLs:"
echo "   Main UI: http://localhost:3000/semantic-guard"
echo "   API Health: http://localhost:5000/near/health"
echo
echo "💡 Press Ctrl+C to stop all services"

# Keep script running and handle interruption
trap 'echo "🛑 Stopping services..."; kill $API_PID $FRONTEND_PID 2>/dev/null; exit' INT

# Wait for user to interrupt
while true; do
    sleep 1
done