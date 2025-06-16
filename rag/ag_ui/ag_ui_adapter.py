"""
AG-UI Protocol Adapter for NearGravity RAG System
Converts NearGravity RAG events to AG-UI standardized events
"""
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import asyncio
import threading
from datetime import datetime

class AGUIEventType(str, Enum):
    """AG-UI Standard Event Types"""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end" 
    AGENT_ERROR = "agent_error"
    AGENT_MESSAGE = "agent_message"
    AGENT_STATE = "agent_state"
    AGENT_STEP = "agent_step"
    AGENT_TOOL_CALL = "agent_tool_call"
    AGENT_TOOL_RESULT = "agent_tool_result"
    USER_INPUT = "user_input"
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    STATE_UPDATE = "state_update"
    PROGRESS_UPDATE = "progress_update"
    COMPLETION = "completion"
    ERROR = "error"
    CUSTOM = "custom"

@dataclass
class AGUIEvent:
    """AG-UI Event Structure"""
    event_type: AGUIEventType
    data: Dict[str, Any]
    timestamp: str = None
    session_id: str = None
    agent_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())

    def to_dict(self):
        return asdict(self)

class NearGravityAGUIAdapter:
    """
    Adapter that converts NearGravity RAG operations into AG-UI protocol events
    Enables real-time streaming of the RAG process to frontend
    """
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.agent_id = "NearGravity-rag-agent"
        
        # Event subscribers
        self._subscribers: List[Callable[[AGUIEvent], None]] = []
        
        # State tracking
        self.current_state = {
            "injections_count": 0,
            "processing_step": None,
            "last_semantic_score": None,
            "total_requests": 0,
            "active_providers": []
        }
        
        # Processing pipeline states
        self.pipeline_steps = [
            "embedding_generation",
            "injection_search", 
            "semantic_matching",
            "content_generation",
            "integrity_verification",
            "blockchain_recording"
        ]
    
    def subscribe(self, callback: Callable[[AGUIEvent], None]):
        """Subscribe to AG-UI events"""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[AGUIEvent], None]):
        """Unsubscribe from AG-UI events"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def _emit_event(self, event: AGUIEvent):
        """Emit event to all subscribers"""
        event.session_id = self.session_id
        event.agent_id = self.agent_id
        
        for callback in self._subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in AG-UI callback: {e}")
    
    def start_rag_session(self):
        """Start a new RAG processing session"""
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_START,
            data={
                "agent_name": "NearGravity RAG Processor",
                "capabilities": [
                    "semantic_injection_matching",
                    "content_generation", 
                    "integrity_verification",
                    "real_time_bidding"
                ],
                "session_id": self.session_id
            }
        )
        self._emit_event(event)
    
    def injection_added(self, injection_data: Dict[str, Any]):
        """Handle injection message addition"""
        self.current_state["injections_count"] += 1
        
        # Add to active providers
        provider_id = injection_data.get("provider_id")
        if provider_id not in self.current_state["active_providers"]:
            self.current_state["active_providers"].append(provider_id)
        
        # Emit injection addition event
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_MESSAGE,
            data={
                "message": f"💉 New injection added from {provider_id}",
                "content": injection_data.get("content"),
                "metadata": {
                    "injection_id": injection_data.get("injection_id"),
                    "provider_id": provider_id,
                    "bid_amount": injection_data.get("metadata", {}).get("bid_amount"),
                    "category": injection_data.get("metadata", {}).get("category")
                },
                "type": "injection_added"
            }
        )
        self._emit_event(event)
        
        # Update state
        self._update_state()
    
    def user_query_received(self, query: str, user_id: str):
        """Handle user query input"""
        event = AGUIEvent(
            event_type=AGUIEventType.USER_INPUT,
            data={
                "message": query,
                "user_id": user_id,
                "intent": "content_generation_request"
            }
        )
        self._emit_event(event)
        
        # Start processing workflow
        self.start_rag_processing(query)
    
    def start_rag_processing(self, query: str):
        """Start the RAG processing pipeline"""
        self.current_state["processing_step"] = "starting"
        self.current_state["total_requests"] += 1
        
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_STEP,
            data={
                "step_name": "rag_processing_start",
                "step_description": "Starting semantic advertising pipeline",
                "input": query,
                "pipeline_steps": self.pipeline_steps
            }
        )
        self._emit_event(event)
        self._update_state()
    
    def embedding_generated(self, text: str, embedding_dim: int, processing_time_ms: float):
        """Handle embedding generation step"""
        self.current_state["processing_step"] = "embedding_generation"
        
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_STEP,
            data={
                "step_name": "embedding_generation",
                "step_description": f"Generated {embedding_dim}D semantic embedding",
                "metrics": {
                    "embedding_dimensions": embedding_dim,
                    "processing_time_ms": processing_time_ms,
                    "text_length": len(text)
                },
                "status": "completed"
            }
        )
        self._emit_event(event)
        self._update_state()
    
    def injection_search_results(self, candidates: List[Dict], similarity_scores: List[float]):
        """Handle injection search results"""
        self.current_state["processing_step"] = "injection_search"
        
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_STEP,
            data={
                "step_name": "injection_search",
                "step_description": f"Found {len(candidates)} relevant injections",
                "results": {
                    "candidate_count": len(candidates),
                    "top_similarity": max(similarity_scores) if similarity_scores else 0,
                    "avg_similarity": sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
                    "candidates": [
                        {
                            "provider_id": c.get("provider_id"),
                            "content_preview": c.get("content", "")[:50] + "...",
                            "similarity": score,
                            "bid_amount": c.get("metadata", {}).get("bid_amount", 0)
                        }
                        for c, score in zip(candidates, similarity_scores)
                    ]
                },
                "status": "completed"
            }
        )
        self._emit_event(event)
        self._update_state()
    
    def content_generation_start(self, combined_prompt: str):
        """Handle content generation start"""
        self.current_state["processing_step"] = "content_generation"
        
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_TOOL_CALL,
            data={
                "tool_name": "llm_generator",
                "tool_description": "Generate enhanced content with semantic injection",
                "input": {
                    "prompt_length": len(combined_prompt),
                    "model": "gpt-3.5-turbo",
                    "prompt_preview": combined_prompt[:100] + "..."
                }
            }
        )
        self._emit_event(event)
        self._update_state()
    
    def content_generation_complete(self, generated_content: str, processing_time_ms: float):
        """Handle content generation completion"""
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_TOOL_RESULT,
            data={
                "tool_name": "llm_generator",
                "result": {
                    "content": generated_content,
                    "content_length": len(generated_content),
                    "processing_time_ms": processing_time_ms
                },
                "status": "success"
            }
        )
        self._emit_event(event)
    
    def semantic_verification(self, original: str, generated: str, verification_result: Dict):
        """Handle semantic verification step"""
        self.current_state["processing_step"] = "integrity_verification"
        self.current_state["last_semantic_score"] = verification_result.get("composite_delta", 0)
        
        is_within_bounds = verification_result.get("is_within_bounds", False)
        
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_STEP,
            data={
                "step_name": "semantic_verification",
                "step_description": "Verifying semantic integrity",
                "verification": {
                    "cosine_similarity": verification_result.get("cosine_similarity", 0),
                    "mutual_info_score": verification_result.get("mutual_info_score", 0),
                    "composite_delta": verification_result.get("composite_delta", 0),
                    "threshold": verification_result.get("threshold", 0.85),
                    "is_within_bounds": is_within_bounds,
                    "transformation_type": verification_result.get("transformation_type", "default")
                },
                "status": "completed",
                "quality_gate": "passed" if is_within_bounds else "warning"
            }
        )
        self._emit_event(event)
        self._update_state()
    
    def rag_processing_complete(self, final_result: Dict):
        """Handle RAG processing completion"""
        self.current_state["processing_step"] = "completed"
        
        event = AGUIEvent(
            event_type=AGUIEventType.COMPLETION,
            data={
                "result_type": "enhanced_content",
                "content": final_result.get("content"),
                "metadata": final_result.get("metadata", {}),
                "processing_summary": {
                    "total_time_ms": final_result.get("metadata", {}).get("processing_time_ms"),
                    "semantic_score": self.current_state["last_semantic_score"],
                    "injections_used": final_result.get("metadata", {}).get("injection_used") is not None,
                    "quality_verified": final_result.get("metadata", {}).get("semantic_delta", {}).get("is_within_bounds", False)
                }
            }
        )
        self._emit_event(event)
        self._update_state()
    
    def error_occurred(self, error_message: str, error_context: Dict = None):
        """Handle error in processing"""
        event = AGUIEvent(
            event_type=AGUIEventType.AGENT_ERROR,
            data={
                "error_message": error_message,
                "error_context": error_context or {},
                "recovery_suggestions": [
                    "Check API key configuration",
                    "Verify network connectivity", 
                    "Try with a shorter message"
                ]
            }
        )
        self._emit_event(event)
    
    def _update_state(self):
        """Update and broadcast current state"""
        event = AGUIEvent(
            event_type=AGUIEventType.STATE_UPDATE,
            data={
                "agent_state": self.current_state.copy(),
                "capabilities": {
                    "injections_available": self.current_state["injections_count"] > 0,
                    "providers_active": len(self.current_state["active_providers"]),
                    "processing_active": self.current_state["processing_step"] is not None
                }
            }
        )
        self._emit_event(event)

    def get_system_metrics(self):
        """Get comprehensive system metrics"""
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "current_state": self.current_state,
            "timestamp": datetime.utcnow().isoformat()
        }