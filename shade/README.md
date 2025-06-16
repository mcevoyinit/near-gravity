# Shade Agent Integration - TEE Privacy Layer

This directory contains the Shade Agent integration for the NearGravity NEAR Semantic Guard, providing confidential computing capabilities through Trusted Execution Environments (TEE).

## 🔐 What is Shade Agent?

Shade Agent enables confidential semantic analysis by running the Python Flask application inside a Trusted Execution Environment, ensuring:

- **Data Privacy**: Queries and analysis results remain encrypted
- **Computation Integrity**: TEE provides tamper-proof execution
- **Attestation**: Cryptographic proof of secure execution
- **Isolation**: Complete separation from host system

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  Shade Agent    │───▶│   TEE (Phala)   │
│   (Frontend)    │    │  (Python API)   │    │   Execution     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
  Public Interface      Privacy Layer           Secure Computing
  Standard HTTP         Encrypted Transport     Attestation + Proof
  Semantic Queries      Private Processing      Confidential Results
```

## 🚀 Quick Start

### Local Development (TEE Simulation)
```bash
cd contracts-shady-py/
# Install Python dependencies
pip install -r requirements.txt
# Install Node.js dependencies
yarn install
# Run in Docker with TEE simulation
docker-compose up
```

### Access Points
- **Shade Agent API**: http://localhost:3140
- **Python Test App**: http://localhost:3000

### Test Endpoints
```bash
# Get TEE ephemeral account
curl http://localhost:3000/api/address

# Test cryptographic signing in TEE
curl http://localhost:3000/api/test-sign
```

## 🔧 Integration with Semantic Guard

The Shade Agent can be integrated with the main semantic guard system for private analysis:

```python
# Example: Private semantic analysis
import requests

# Route queries through TEE
response = requests.post('http://localhost:3000/api/semantic-private', {
    'query': 'sensitive information query',
    'privacy_level': 'high'
})
```

## 🎯 Hackathon Value Proposition

### Privacy-First Misinformation Detection
1. **Confidential Queries**: Users can analyze sensitive topics without exposure
2. **Private Embeddings**: Vector calculations happen in secure enclave
3. **Anonymous Reporting**: Outlier detection without revealing query source
4. **Secure Aggregation**: Multi-party consensus without data sharing

### Technical Innovation
- **First TEE + AI Integration**: Novel combination of confidential computing and semantic analysis
- **Python in TEE**: Demonstrates flexibility beyond JavaScript
- **Production Ready**: Full Docker orchestration and deployment pipeline
- **NEAR Integration**: Seamless blockchain verification of TEE attestations

## 📁 File Structure

```
near-shady-py/
├── app.py                 # Main Python Flask application
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies and scripts
├── Dockerfile            # Multi-stage container build
├── docker-compose.yaml   # TEE simulation orchestration
├── .yarnrc.yml          # Yarn 4 configuration
└── README.md            # Detailed setup instructions
```

## 🔐 Security Features

### TEE Attestation
- Cryptographic proof of secure execution
- Hardware-based security guarantees
- Remote attestation verification

### Data Protection
- Memory encryption in TEE
- Secure key management
- Private computation guarantees

### Blockchain Integration
- TEE attestation stored on NEAR
- Immutable proof of secure analysis
- Decentralized verification network

## 🚀 Production Deployment

For production deployment to Phala Cloud:

```bash
# Set environment variables
export DOCKER_TAG=your-docker-hub/shade-semantic-guard
export PHALA_API_KEY=your-phala-api-key

# Deploy to TEE network
yarn shade-agent-cli
```

## 🎮 Demo Integration

The Shade Agent seamlessly integrates with the main demo:

1. **Standard Mode**: Regular semantic analysis (current demo)
2. **Privacy Mode**: Same analysis but in TEE with attestation
3. **Hybrid Mode**: Public consensus + private outlier detection

This provides judges with a complete privacy-preserving misinformation detection system that maintains all the functionality of the main demo while adding confidential computing capabilities.

---

**Ready to experience privacy-first semantic verification? Run the Shade Agent and see TEE in action!** 🔐