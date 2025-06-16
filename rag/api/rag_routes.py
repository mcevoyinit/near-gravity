"""
Flask routes for RAG functionality
"""
from flask import Blueprint, request, jsonify
import time
from typing import Dict, Any

from ..enhanced_rag_processor import EnhancedRAGProcessor
from ..vector_store_service import VectorStoreService
from backend.agentic.agent_model import AgentConfig, AgentMessage
from models.entities.python.data_models import InjectionMessage

# Create blueprint
rag_bp = Blueprint('rag', __name__)

# Initialize services (in production, use dependency injection)
_processor = None
_vector_store = None


def get_processor():
    """Get or create RAG processor"""
    global _processor
    if _processor is None:
        config = AgentConfig(
            name="NearGravityRAG",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000,
            system_prompt="You are NearGravity's content generation system.",
            thread_pool_size=3
        )
        _processor = EnhancedRAGProcessor(config)
    return _processor


def get_vector_store():
    """Get or create vector store"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService(use_faiss=False)
    return _vector_store


@rag_bp.route('/generate', methods=['POST'])
def generate_content():
    """
    Generate content using RAG
    
    Request body:
    {
        "message": "User message content",
        "user_id": "user123",
        "modality": "text|code|structured",
        "modality_params": {},
        "constraints": {
            "semantic_threshold": 0.85,
            "max_injections": 3
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data:
            return jsonify({"error": "Missing required field: message"}), 400
        
        # Extract parameters
        message_content = data['message']
        user_id = data.get('user_id', 'anonymous')
        modality = data.get('modality', 'text')
        modality_params = data.get('modality_params', {})
        constraints = data.get('constraints', {})
        
        # Create agent message
        agent_message = AgentMessage(
            content=message_content,
            role="user",
            metadata={
                "user_id": user_id,
                "modality": modality,
                "modality_params": modality_params,
                "semantic_threshold": constraints.get("semantic_threshold", 0.85),
                "max_injections": constraints.get("max_injections", 3)
            }
        )
        
        # Process through RAG
        processor = get_processor()
        start_time = time.time()
        
        # Submit task and wait for result
        task_id = processor.submit_task(agent_message)
        result = processor._wait_for_task(task_id, timeout=30.0)
        
        if result is None:
            return jsonify({"error": "Processing timeout"}), 504
        
        # Format response
        processing_time = (time.time() - start_time) * 1000
        
        response = {
            "status": "success",
            "content": result.get("result", {}).content if result.get("result") else "",
            "modality": modality,
            "semantic_delta": {
                "cosine_similarity": result.get("semantic_verification", {}).cosine_similarity,
                "is_within_bounds": result.get("semantic_verification", {}).is_within_bounds,
                "composite_delta": result.get("semantic_verification", {}).composite_delta
            } if result.get("semantic_verification") else None,
            "processing_time_ms": processing_time,
            "injection_count": result.get("injection_candidates", 0),
            "transaction_hash": result.get("result", {}).metadata.get("tx_hash") if result.get("result") else None
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/inject', methods=['POST'])
def add_injection():
    """
    Add an injection message
    
    Request body:
    {
        "content": "Injection message content",
        "provider_id": "provider123",
        "metadata": {
            "category": "coffee",
            "bid_amount": 0.001,
            "tags": ["coffee", "morning"]
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'content' not in data or 'provider_id' not in data:
            return jsonify({"error": "Missing required fields: content, provider_id"}), 400
        
        # Create injection message
        injection = InjectionMessage(
            message_id=f"inj_{int(time.time() * 1000)}",
            content=data['content'],
            provider_id=data['provider_id'],
            metadata=data.get('metadata', {})
        )
        
        # Generate embedding
        processor = get_processor()
        embedding = processor._generate_embedding(injection.content)
        
        # Store in vector store
        vector_store = get_vector_store()
        message_id = vector_store.add_message(injection, embedding, injection.metadata)
        
        # Also add to processor's internal store
        processor.add_injection_message(
            content=injection.content,
            provider_id=injection.provider_id,
            metadata=injection.metadata
        )
        
        return jsonify({
            "status": "success",
            "injection_id": message_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/verify', methods=['POST'])
def verify_semantic():
    """
    Verify semantic integrity between two texts
    
    Request body:
    {
        "original": "Original text",
        "transformed": "Transformed text",
        "transformation_type": "default|summarization|translation|creative"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'original' not in data or 'transformed' not in data:
            return jsonify({"error": "Missing required fields: original, transformed"}), 400
        
        original = data['original']
        transformed = data['transformed']
        transformation_type = data.get('transformation_type', 'default')
        
        # Verify semantic integrity
        processor = get_processor()
        semantic_delta = processor._verify_semantic_integrity(
            original,
            transformed,
            transformation_type
        )
        
        return jsonify({
            "status": "success",
            "semantic_delta": {
                "cosine_similarity": semantic_delta.cosine_similarity,
                "mutual_info_score": semantic_delta.mutual_info_score,
                "composite_delta": semantic_delta.composite_delta,
                "is_within_bounds": semantic_delta.is_within_bounds,
                "transformation_type": semantic_delta.transformation_type,
                "threshold": semantic_delta.threshold
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/injections', methods=['GET'])
def list_injections():
    """List all injection messages"""
    try:
        vector_store = get_vector_store()
        messages = vector_store.get_all_messages()
        
        return jsonify({
            "status": "success",
            "injections": [
                {
                    "injection_id": msg.message_id,
                    "content": msg.content,
                    "provider_id": msg.provider_id,
                    "metadata": msg.metadata
                }
                for msg in messages
            ],
            "total": len(messages)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/injections/<injection_id>', methods=['GET'])
def get_injection(injection_id):
    """Get a specific injection message"""
    try:
        vector_store = get_vector_store()
        message = vector_store.get_message(injection_id)
        
        if not message:
            return jsonify({"error": "Injection not found"}), 404
        
        return jsonify({
            "status": "success",
            "injection": {
                "injection_id": message.message_id,
                "content": message.content,
                "provider_id": message.provider_id,
                "metadata": message.metadata
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/injections/<injection_id>', methods=['DELETE'])
def delete_injection(injection_id):
    """Delete an injection message"""
    try:
        vector_store = get_vector_store()
        success = vector_store.delete_message(injection_id)
        
        if not success:
            return jsonify({"error": "Injection not found"}), 404
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get RAG system metrics"""
    try:
        processor = get_processor()
        vector_store = get_vector_store()
        
        processor_metrics = processor.get_metrics()
        store_stats = vector_store.get_statistics()
        
        return jsonify({
            "status": "success",
            "processor_metrics": processor_metrics,
            "store_statistics": store_stats
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check processor
        processor = get_processor()
        processor_healthy = processor.status != "ERROR"
        
        # Check vector store
        vector_store = get_vector_store()
        store_healthy = True  # Simple check
        
        healthy = processor_healthy and store_healthy
        
        return jsonify({
            "status": "healthy" if healthy else "unhealthy",
            "components": {
                "processor": "healthy" if processor_healthy else "unhealthy",
                "vector_store": "healthy" if store_healthy else "unhealthy"
            }
        }), 200 if healthy else 503
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503
