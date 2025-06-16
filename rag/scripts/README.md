# RAG Scripts Directory

This directory contains all scripts for running and testing the NearGravity RAG system.

## Quick Start

```bash
cd /Users/mcevoyinit/ai/NearGravity/src/rag/scripts
./launch.sh
```

## Available Scripts

### Main Launchers
- **`launch.sh`** - Interactive launcher for all RAG demos (RECOMMENDED)
- **`launch_NearGravity_ag_ui.sh`** - Launch AG-UI with purple interface
- **`start_ag_ui_demo.sh`** - Start AG-UI demo scenarios
- **`run_ag_ui_updated.sh`** - Updated AG-UI launcher

### Development/Testing
- **`run_rag_api.py`** - Start standalone RAG API server
- **`test_rag_api.py`** - Test RAG API functionality
- **`test_coffee_injection.py`** - Test coffee injection specifically

## Demo Options

### 1. AG-UI Purple Interface (Recommended)
- **URL**: http://localhost:5002
- **Features**: Dual-panel interface, real-time streaming, coffee injection
- **Command**: `./launch.sh` → Choose option 1

### 2. Standalone Coffee Demo  
- **Features**: Direct coffee injection test, no server required
- **Command**: `./launch.sh` → Choose option 2

### 3. API Server + Test Suite
- **Features**: Full Flask API, comprehensive testing
- **Command**: `./launch.sh` → Choose option 3

### 4. Demo Scenarios
- **Features**: Automated demo scenarios on running AG-UI
- **Command**: `./launch.sh` → Choose option 4

## Environment Setup

All scripts automatically set:
- `OPENAI_API_KEY` 
- `TOKENIZERS_PARALLELISM=false`

## Coffee Injection Status

✅ **Coffee injection is working!**
- Similarity threshold lowered to 0.6
- Blue Bottle Coffee successfully integrates into responses
- Test with queries about "morning energy" or "productivity"

## Troubleshooting

- **Port conflicts**: Scripts use ports 5002 (AG-UI) and 5005 (API)
- **Server not responding**: Kill existing processes with `pkill -f server.py`
- **Import errors**: Scripts handle path resolution automatically