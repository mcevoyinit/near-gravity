#!/bin/bash

echo "🚀 NEAR Gravity Semantic Guard - Status Check"
echo "============================================="
echo

# Check API Health
echo "🔍 Checking API Health (Port 5000)..."
if curl -s http://localhost:5000/near/health > /dev/null; then
    echo "✅ API Server: RUNNING"
    echo "   Health: $(curl -s http://localhost:5000/near/health | jq -r .status 2>/dev/null || echo 'OK')"
else
    echo "❌ API Server: NOT RUNNING"
fi

echo

# Check Frontend
echo "🔍 Checking Frontend (Port 3000)..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: RUNNING"
    echo "   URL: http://localhost:3000/semantic-guard"
else
    echo "❌ Frontend: NOT RUNNING"
fi

echo

# Check Shade Agent (if running)
echo "🔍 Checking Shade Agent (Port 3140)..."
if curl -s http://localhost:3140 > /dev/null; then
    echo "✅ Shade Agent: RUNNING"
else
    echo "⚠️  Shade Agent: NOT RUNNING (optional)"
fi

echo
echo "🎯 Demo URLs:"
echo "   Main UI: http://localhost:3000/semantic-guard"
echo "   API Health: http://localhost:5000/near/health"
echo "   API Endpoint: http://localhost:5000/near/semantic-guard"
echo
echo "🧪 Test API directly:"
echo "   curl -X POST http://localhost:5000/near/semantic-guard \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"climate change latest research\", \"max_results\": 5}'"
echo