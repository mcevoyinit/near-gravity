# CLAUDE.md

This file provides guidance to Claude Code when working with the NEAR Gravity Semantic Guard project.

## Project Overview

NEAR Gravity is a semantic guard system that combines AI-powered semantic analysis with NEAR blockchain for misinformation detection and consensus verification. The project integrates:

- **Multi-Agent RAG System**: Advanced semantic analysis with vector embeddings
- **NEAR Blockchain Integration**: Decentralized verification and storage
- **Shade Agent TEE**: Privacy-preserving confidential computing
- **Real-time UI**: Interactive semantic guard interface

## Project Structure

```
~/near/near-gravity/
├── api/                    # Flask API servers
│   ├── demo_app.py        # Standalone demo with realistic scenarios
│   └── integrated_app.py  # Full integration server
├── agents/                 # Multi-agent framework
├── rag/                   # RAG system components
├── services/              # NEAR and semantic services
├── contracts/             # Rust smart contracts
├── frontend/shade-agent/  # Next.js React UI
├── shade/near-shady-py/   # TEE privacy layer
└── scripts/               # Development and deployment scripts
```

## Development Commands

### Python Backend
- `python api/demo_app.py` - Start standalone demo API (port 5000)
- `python api/integrated_app.py` - Start full integration API
- `python -m pytest rag/tests/` - Run RAG tests
- `pip install -r requirements.txt` - Install Python dependencies

### Frontend (Next.js)
- `cd frontend/shade-agent && npm install` - Install dependencies
- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production

### RAG System
- `cd rag && python rag_service.py` - Start RAG service
- `bash scripts/launch.sh` - Launch RAG demo
- `python scripts/test_rag_api.py` - Test RAG endpoints

### Shade Agent (TEE)
- `cd shade/near-shady-py` - Navigate to Shade Agent
- `pip install -r requirements.txt && yarn install` - Install dependencies
- `docker-compose up` - Run TEE simulation

### Smart Contracts (Rust)
- Smart contracts are in `contracts/` directory
- Main contract: `semantic_guard_complete.rs`
- Uses NEAR SDK for blockchain integration

## Quick Start Commands

### 1. Start Everything (Automated)
```bash
./scripts/start-dev.sh
```

### 2. Manual Setup
```bash
# Install Python dependencies
pip install flask flask-cors requests openai

# Start API server
python api/demo_app.py

# In another terminal, start frontend
cd frontend/shade-agent
npm install
npm run dev
```

### 3. Test Integration
```bash
./scripts/test-integration.sh
```

## Environment Setup

### Required Dependencies
- **Python 3.8+**: Flask, requests, openai
- **Node.js 16+**: Next.js, React
- **Docker**: For Shade Agent TEE simulation

### API Keys (Optional)
- `OPENAI_API_KEY`: For enhanced semantic analysis
- `BRAVE_SEARCH_API_KEY`: For real search integration

### NEAR Integration
- `NEAR_ACCOUNT_ID`: NEAR account for blockchain operations
- `NEAR_PRIVATE_KEY`: Private key for transactions
- `NEAR_NETWORK`: testnet/mainnet

## Key URLs

- **Main UI**: http://localhost:3000/semantic-guard
- **API Health**: http://localhost:5000/near/health
- **API Endpoint**: http://localhost:5000/near/semantic-guard
- **Shade Agent**: http://localhost:3140 (when running)

## Demo Scenarios

The system includes 4 realistic demo scenarios:

1. **High Trust**: "climate change latest research" (consensus)
2. **Misinformation**: "covid vaccine safety" (outlier detection) 
3. **Mixed Signals**: "artificial intelligence jobs" (natural disagreement)
4. **Economic Uncertainty**: "economy recession 2024" (sensationalism detection)

## Architecture Notes

- **API Layer**: Flask servers handle requests and semantic analysis
- **Agent System**: Multi-agent framework for task orchestration
- **RAG System**: Vector embeddings and semantic similarity
- **Blockchain**: NEAR smart contracts for verification storage
- **Privacy**: Shade Agent provides TEE-based confidential computing

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 3000, 5000, 3140 are available
2. **Dependencies**: Run `pip install` and `npm install` in respective directories
3. **CORS errors**: API includes CORS headers for localhost development

### Testing
- Use `scripts/test-integration.sh` for end-to-end testing
- Check API health at `/near/health` endpoint
- Frontend should show 4 scenario cards with working interactions

## Development Workflow

1. **API First**: Start with `python api/demo_app.py`
2. **Frontend**: Launch UI with `npm run dev` in frontend directory
3. **Test Scenarios**: Click scenario cards to test semantic analysis
4. **Integration**: Use full integration server for complete functionality
5. **Privacy**: Add Shade Agent for TEE-based privacy features

This project demonstrates the integration of AI semantic analysis with blockchain verification, providing a complete solution for misinformation detection and consensus building.