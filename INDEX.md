# 🏆 NearGravity NEAR Semantic Guard - Hackathon Package Index

**Complete AI + Blockchain Semantic Analysis System**

---

## 🚀 Quick Start (30 seconds)

```bash
cd src/hack
./scripts/start-dev.sh
```

**Then visit:** http://localhost:3000/semantic-guard

---

## 📋 Project Index

| Component | File/Directory | Status | Purpose |
|-----------|---------------|--------|---------|
| **🎯 Main Demo** | [`./scripts/start-dev.sh`](./scripts/start-dev.sh) | ✅ Ready | Automated startup script |
| **🌐 Live UI** | [`./frontend/shade-agent/`](./frontend/shade-agent/) | ✅ Running | Interactive semantic guard interface |
| **🔥 API Server** | [`./api/demo_app.py`](./api/demo_app.py) | ✅ Running | Standalone demo with 4 scenarios |
| **🧠 Full Integration** | [`./api/integrated_app.py`](./api/integrated_app.py) | ✅ Ready | Complete NearGravity + NEAR integration |
| **📖 Documentation** | [`./docs/PROJECT_BREAKDOWN.md`](./docs/PROJECT_BREAKDOWN.md) | ✅ Complete | Comprehensive technical breakdown |

## 🎮 Demo Scenarios

| Scenario | Query | Result | Visual |
|----------|-------|--------|--------|
| **🟢 High Trust** | "climate change latest research" | No outliers detected | Green cards, ✅ trusted badges |
| **🔴 Misinformation** | "covid vaccine safety" | Conspiracy source flagged | Red cards, 🚨 danger badges |
| **🟡 Mixed Signals** | "artificial intelligence jobs" | Legitimate disagreement | Yellow cards, mixed indicators |
| **🟠 Economic Uncertainty** | "economy recession 2024" | Alarmist content flagged | Orange cards, ⚠️ warnings |

## 🔧 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI   │───▶│   Flask API     │───▶│  NEAR Contract  │
│  (Port 3000)   │    │  (Port 5000)    │    │   (Blockchain)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
  User Interaction      Semantic Analysis         Immutable Storage
  4 Scenario Cards      RAG + Agent System        Verification Records
  Real-time Results     Distance Computation      Oracle Consensus
```

## 💻 Technical Integration

| System | Source Location | Integration Status | Key Features |
|--------|----------------|-------------------|--------------|
| **Agent Framework** | `src/backend/agentic/` | ✅ Fully integrated | Multi-agent task orchestration |
| **RAG System** | `src/rag/` | ✅ Fully integrated | Vector embeddings, semantic analysis |
| **NEAR Services** | `src/near/services/` | ✅ Custom built | Blockchain storage, consensus |
| **Smart Contracts** | `./blockchain/` | ✅ Production ready | Complete NEAR Rust contracts |

## 📊 API Quick Reference

### Main Endpoint
```bash
# POST /contracts/semantic-guard
curl -X POST http://localhost:5000/near/semantic-guard \
  -H "Content-Type: application/json" \
  -d '{"query": "climate change latest research", "max_results": 5}'
```

### Health Check
```bash
# GET /contracts/health
curl http://localhost:5000/near/health
```

**Expected Response:**
```json
{
  "service": "semantic_guard",
  "status": "healthy",
  "components": {
    "search_service": true,
    "semantic_service": true,
    "near_service": true
  }
}
```

## 🧪 Testing

```bash
# Run integration tests
./scripts/test-integration.sh

# Performance test
./scripts/test-integration.sh --performance

# Manual API test
curl -X POST http://localhost:5000/near/semantic-guard \
  -d '{"query": "test", "max_results": 3}'
```

## 🏗️ File Structure

```
src/hack/
├── README.md                    # Main project documentation
├── INDEX.md                     # This file - quick reference
├── api/                         # API Gateway Layer
│   ├── demo_app.py             # ✅ Standalone demo server
│   └── integrated_app.py       # ✅ Full NearGravity integration
├── agents/                      # Multi-Agent Framework
│   ├── agent_manager.py        # ✅ Agent orchestration
│   ├── agent_rag.py           # ✅ RAG-specific agent
│   └── agent_*.py             # ✅ Additional agents
├── rag/                        # RAG System Components
│   ├── rag_service.py         # ✅ Core RAG service
│   ├── vector_store_service.py # ✅ Vector storage
│   └── api/                   # ✅ RAG API routes
├── services/                   # NEAR & Semantic Services
│   ├── near_service.py        # ✅ Blockchain integration
│   ├── semantic_guard_service.py # ✅ Semantic analysis
│   └── search_service.py      # ✅ Multi-provider search
├── blockchain/                 # Smart Contracts
│   ├── semantic_guard_complete.rs # ✅ Full NEAR contract
│   └── semantic_guard_contract.rs # ✅ Contract utilities
├── frontend/                   # React/Next.js UI
│   └── shade-agent/           # ✅ Interactive interface
├── shade/                      # TEE & Privacy Components
│   └── near-shady-py/         # ✅ Python Shade Agent integration
├── scripts/                    # Automation Scripts
│   ├── start-dev.sh          # ✅ Development startup
│   └── test-integration.sh   # ✅ Integration testing
└── docs/                      # Documentation
    └── PROJECT_BREAKDOWN.md  # ✅ Technical deep dive
```

## 🎯 Hackathon Tracks

### Primary: Main Track ($10,000)
**Innovation:** First semantic AI + blockchain integration on NEAR
- ✅ Real-time misinformation detection
- ✅ Decentralized consensus mechanisms  
- ✅ Economic incentive alignment

### Secondary: Shade Agents ($2,000)
**Privacy Integration:** Confidential semantic analysis
- ✅ Privacy-focused agent architecture
- ✅ Encrypted processing capabilities
- ✅ Anonymous outlier reporting

## 🌟 Key Innovations

1. **🔬 Realistic Semantic Distances**
   - High Trust: 0.13-0.45 (strong consensus)
   - Misinformation: 0.85-1.04 (clear outliers)
   - Mixed Signals: 0.49-0.82 (natural disagreement)

2. **🎨 Visual Semantic Indicators**
   - Color-coded result cards by source type
   - Emoji indicators for different scenarios
   - Real-time badge updates

3. **🔗 Complete Blockchain Integration**
   - Immutable analysis storage
   - Multi-oracle consensus
   - Prediction market ready

4. **⚡ Production-Ready Architecture**
   - Agent-based processing
   - Horizontal scaling support
   - Comprehensive error handling

## 🏁 Demo Walkthrough

1. **Start Services:** `./scripts/start-dev.sh`
2. **Open UI:** http://localhost:3000/semantic-guard
3. **Try Scenarios:** Click any colored scenario card
4. **Watch Analysis:** See real-time semantic processing
5. **Explore Results:** View outlier detection and consensus

## 📞 Support & Resources

- **Demo:** http://localhost:3000/semantic-guard
- **API Docs:** `./docs/PROJECT_BREAKDOWN.md`
- **Source Code:** All files included in `src/hack/`
- **Smart Contract:** `./blockchain/semantic_guard_complete.rs`
- **Test Suite:** `./scripts/test-integration.sh`

---

*Built for NEAR Hackathon - Combining NearGravity's RAG infrastructure with blockchain verification*