# NearGravity AG-UI Integration

## Overview

This directory contains the AG-UI integration for the NearGravity RAG protocol, creating a modern, real-time interface for semantic advertising demonstrations.

**Note**: All imports now use `rag.*` instead of `claude.*` to match the renamed directory structure.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AG-UI Frontend                                │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  Campaign Panel │         │ User Intent Panel│               │
│  │                 │         │                  │               │
│  │ • Add Injections│         │ • Send Messages  │               │
│  │ • View Campaigns│         │ • See Responses  │               │
│  │ • Bid Management│         │ • View Metrics   │               │
│  └─────────────────┘         └─────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                    AG-UI Protocol Events
                              │
┌─────────────────────────────────────────────────────────────────┐
│                 AG-UI Adapter                                    │
│  • Converts RAG events to AG-UI protocol                       │
│  • Handles real-time streaming                                 │
│  • Manages bidirectional communication                         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│              NearGravity RAG Engine                              │
│  • Enhanced RAG Processor                                      │
│  • Vector Store Service                                        │
│  • Semantic Verification                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Files

- `ag_ui_adapter.py` - Main AG-UI protocol adapter for NearGravity
- `event_schemas.py` - AG-UI event type definitions
- `frontend/` - React frontend with dual-panel interface
- `server.py` - Flask server with AG-UI integration
- `demo_runner.py` - Automated demo scenarios

## Quick Start

```bash
# Install dependencies
npm install

# Start the server
python3 server.py

# Open browser
open http://localhost:3000
```

## Features

### Campaign Panel (Left Side)
- ✅ Add injection messages
- ✅ Set bid amounts and targeting
- ✅ View active campaigns
- ✅ Real-time performance metrics

### User Intent Panel (Right Side)  
- ✅ Send user queries
- ✅ See RAG-enhanced responses
- ✅ View semantic verification scores
- ✅ Track processing pipeline

### Real-time Features
- 🔄 Live processing updates
- 📊 Streaming metrics
- 🧠 Semantic verification visualization
- ⚡ Instant feedback on all operations