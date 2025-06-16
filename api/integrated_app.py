#!/usr/bin/env python3
"""
Integrated NearGravity NEAR Semantic Guard Application
Combines RAG, Agentic, and NEAR systems for complete semantic analysis
"""
import sys
import os
from pathlib import Path
import time
import logging

# Add hack directory to path for imports
hack_path = str(Path(__file__).parent.parent)
if hack_path not in sys.path:
    sys.path.insert(0, hack_path)

# Add main src directory for core NearGravity imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Try to import NearGravity services
try:
    from agents.agent_manager import AgentManager
    from agents.agent_rag import RAGAgent
    from rag.rag_service import RAGService
    from services.semantic_guard_service import create_semantic_guard_service
    from services.search_service import create_search_service
    from services.near_service import create_near_service
    FULL_INTEGRATION = True
    logger.info("Full NearGravity integration loaded successfully")
except ImportError as e:
    logger.warning(f"Full integration not available, using demo mode: {e}")
    FULL_INTEGRATION = False
    # Import demo fallback
    from demo_app import MockSearchService, MockSemanticService, MockNEARService

class IntegratedSemanticGuard:
    """Integrated semantic guard using full NearGravity architecture"""
    
    def __init__(self):
        self.full_integration = FULL_INTEGRATION
        
        if self.full_integration:
            self._init_full_services()
        else:
            self._init_demo_services()
    
    def _init_full_services(self):
        """Initialize full NearGravity services"""
        try:
            # Initialize agent manager
            self.agent_manager = AgentManager()
            
            # Initialize RAG service
            self.rag_service = RAGService()
            
            # Initialize specialized services
            self.search_service = create_search_service()
            self.semantic_service = create_semantic_guard_service(self.rag_service)
            self.near_service = create_near_service()
            
            # Register agents
            rag_agent = RAGAgent(
                agent_id="rag_agent_001",
                rag_service=self.rag_service
            )
            self.agent_manager.register_agent(rag_agent)
            
            logger.info("Full integration services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize full services: {e}")
            self.full_integration = False
            self._init_demo_services()
    
    def _init_demo_services(self):
        """Initialize demo fallback services"""
        self.search_service = MockSearchService()
        self.semantic_service = MockSemanticService()
        self.near_service = MockNEARService()
        logger.info("Demo services initialized")
    
    def analyze_query(self, query: str, max_results: int = 5, 
                     semantic_threshold: float = 0.75) -> Dict[str, Any]:
        """Perform integrated semantic analysis"""
        start_time = time.time()
        
        try:
            # Step 1: Search aggregation
            search_results = self.search_service.search(
                query=query,
                count=max_results,
                prefer_mock=not self.full_integration
            )
            
            # Step 2: Semantic analysis
            if self.full_integration:
                analysis_result = self._analyze_with_agents(
                    query, search_results, semantic_threshold
                )
            else:
                analysis_result = self.semantic_service.analyze_search_results(
                    query=query,
                    search_results=search_results,
                    semantic_threshold=semantic_threshold
                )
            
            # Step 3: Process results
            processed_results = self._process_results(search_results, analysis_result)
            
            # Step 4: Store on NEAR
            analysis_id = self._store_analysis(query, processed_results, analysis_result)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "query": query,
                "results": processed_results,
                "semantic_analysis": self._format_analysis(analysis_result),
                "metadata": {
                    "analysis_id": analysis_id,
                    "integration_mode": "full" if self.full_integration else "demo",
                    "processing_time_ms": processing_time,
                    "services_used": self._get_services_status(),
                    "timestamp": int(time.time())
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _analyze_with_agents(self, query: str, search_results: List[Dict], 
                           threshold: float) -> Dict[str, Any]:
        """Use agent system for semantic analysis"""
        try:
            # Create agent task
            task_data = {
                "query": query,
                "search_results": search_results,
                "semantic_threshold": threshold,
                "analysis_type": "semantic_guard"
            }
            
            # Submit to agent manager
            result = self.agent_manager.submit_task(
                task_type="semantic_analysis",
                task_data=task_data,
                priority="high"
            )
            
            return result.get("analysis", {})
            
        except Exception as e:
            logger.warning(f"Agent analysis failed, using fallback: {e}")
            return self.semantic_service.analyze_search_results(
                query=query,
                search_results=search_results,
                semantic_threshold=threshold
            )
    
    def _process_results(self, search_results: List[Dict], 
                        analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and enrich search results with semantic data"""
        processed_results = []
        
        for result in search_results:
            # Find semantic metadata
            embedding = next(
                (e for e in analysis_result.get("embeddings", []) 
                 if e.get("result_id") == result["id"]),
                None
            )
            
            # Check outlier status
            is_outlier = any(
                o.get("result_id") == result["id"] 
                for o in analysis_result.get("outliers", [])
            )
            
            # Calculate gravity score
            center_id = analysis_result.get("center_of_gravity")
            distance_key = f"{center_id}->{result['id']}"
            gravity_score = analysis_result.get("distance_matrix", {}).get(distance_key, 0.0)
            
            if isinstance(gravity_score, dict):
                gravity_score = gravity_score.get("distance", 0.0)
            
            processed_results.append({
                "id": result["id"],
                "title": result["title"],
                "snippet": result["snippet"],
                "url": result["url"],
                "rank": result["rank"],
                "is_center_of_gravity": result["id"] == center_id,
                "is_outlier": is_outlier,
                "gravity_score": gravity_score,
                "semantic_hash": embedding.get("semantic_hash") if embedding else None,
                "source_type": result.get("source_type", "unknown"),
                "scenario": result.get("scenario", "balanced")
            })
        
        return processed_results
    
    def _format_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis results for API response"""
        # Convert distance matrix to simple format
        distance_matrix = analysis_result.get("distance_matrix", {})
        distance_matrix_simple = {}
        
        for key, value in distance_matrix.items():
            if isinstance(value, dict):
                distance_matrix_simple[key] = value.get("distance", value)
            else:
                distance_matrix_simple[key] = value
        
        return {
            "center_of_gravity": {
                "result_id": analysis_result.get("center_of_gravity"),
                "gravity_score": 0.0,
                "reason": "Result with minimum average semantic distance"
            },
            "outliers": analysis_result.get("outliers", []),
            "distance_matrix": distance_matrix_simple,
            "threshold_used": analysis_result.get("threshold_used", 0.75),
            "total_comparisons": len(distance_matrix_simple) // 2,
            "processing_time_ms": analysis_result.get("processing_time_ms", 0),
            "embeddings_generated": len(analysis_result.get("embeddings", [])),
            "scenario": analysis_result.get("scenario", "balanced")
        }
    
    def _store_analysis(self, query: str, results: List[Dict], 
                       analysis: Dict[str, Any]) -> Optional[str]:
        """Store analysis on NEAR contracts"""
        try:
            if self.near_service and hasattr(self.near_service, 'submit_semantic_analysis'):
                storage_result = self.near_service.submit_semantic_analysis(
                    prefix="integrated_semantic_guard",
                    identifier=f"query_{int(time.time())}",
                    analysis_data={
                        "query": query,
                        "results": results,
                        "semantic_analysis": analysis
                    }
                )
                return storage_result.get("storage_key")
        except Exception as e:
            logger.warning(f"NEAR storage failed: {e}")
        
        return None
    
    def _get_services_status(self) -> Dict[str, Any]:
        """Get status of all integrated services"""
        status = {
            "integration_mode": "full" if self.full_integration else "demo",
            "search_service": True,
            "semantic_service": True,
            "near_service": False,
            "agent_manager": False,
            "rag_service": False
        }
        
        if self.full_integration:
            try:
                status["agent_manager"] = bool(self.agent_manager)
                status["rag_service"] = bool(self.rag_service)
                status["near_service"] = (
                    self.near_service and 
                    hasattr(self.near_service, 'health_check') and
                    self.near_service.health_check()
                )
            except Exception as e:
                logger.warning(f"Service status check failed: {e}")
        
        return status

# Initialize integrated service
semantic_guard = IntegratedSemanticGuard()

@app.route('/near/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "integrated_semantic_guard",
        "status": "healthy",
        "timestamp": int(time.time()),
        "integration_mode": "full" if FULL_INTEGRATION else "demo",
        "components": semantic_guard._get_services_status()
    })

@app.route('/near/semantic-guard', methods=['POST'])
def analyze_semantic_guard():
    """Main semantic guard analysis endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        query = data.get('query')
        if not query:
            return jsonify({"error": "Query parameter required"}), 400
        
        max_results = data.get('max_results', 5)
        semantic_threshold = data.get('semantic_threshold', 0.75)
        
        # Validate parameters
        if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
            return jsonify({"error": "max_results must be between 1 and 10"}), 400
        
        if not isinstance(semantic_threshold, (int, float)) or semantic_threshold < 0 or semantic_threshold > 2:
            return jsonify({"error": "semantic_threshold must be between 0 and 2"}), 400
        
        # Perform analysis
        result = semantic_guard.analyze_query(
            query=query,
            max_results=max_results,
            semantic_threshold=semantic_threshold
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Analysis request failed: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "integration_mode": "full" if FULL_INTEGRATION else "demo"
        }), 500

@app.route('/near/status', methods=['GET'])
def system_status():
    """Detailed system status endpoint"""
    try:
        status = {
            "system": "NearGravity NEAR Semantic Guard",
            "version": "1.0.0",
            "integration_mode": "full" if FULL_INTEGRATION else "demo",
            "uptime": time.time(),
            "services": semantic_guard._get_services_status(),
            "capabilities": {
                "semantic_analysis": True,
                "multi_agent_processing": FULL_INTEGRATION,
                "rag_integration": FULL_INTEGRATION,
                "near_blockchain": semantic_guard._get_services_status().get("near_service", False),
                "real_time_search": True,
                "outlier_detection": True,
                "consensus_building": True
            },
            "performance": {
                "avg_processing_time_ms": 2500,
                "max_concurrent_requests": 50,
                "supported_languages": ["en"],
                "max_search_results": 10
            }
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Status request failed: {e}")
        return jsonify({
            "error": "Status check failed",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NearGravity NEAR Semantic Guard - Integrated Server")
    print("=" * 60)
    print(f"Integration Mode: {'FULL' if FULL_INTEGRATION else 'DEMO'}")
    print(f"UI Available: http://localhost:3000/semantic-guard")
    print(f"API Health: http://localhost:5000/near/health")
    print(f"System Status: http://localhost:5000/near/status")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=True)