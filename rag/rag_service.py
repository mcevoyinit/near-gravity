"""
RAG Service for NearGravity
High-level service interface for the RAG processor
"""
import threading
from typing import Dict, Any, List, Optional
import time

from backend.agentic.agent_model import AgentConfig, AgentMessage
from rag.rag_processor import RAGProcessor
from models.entities.python.data_models import (
    UserContextualMessage,
    OutputModalityTarget,
    FinalGeneratedResult
)


class RAGService:
    """
    Service wrapper for RAG processing
    Provides a simple interface for the complete RAG flow
    """
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        dgraph_addresses: List[str] = ["localhost:9080"],
        crypto_config: Optional[Dict[str, str]] = None
    ):
        # Create agent config
        config = AgentConfig(
            name="NearGravityRAG",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt="You are NearGravity's content generation system.",
            thread_pool_size=3
        )
        
        # Initialize processor
        self.processor = RAGProcessor(
            config=config,
            dgraph_addresses=dgraph_addresses,
            crypto_config=crypto_config
        )
        
        # Results tracking
        self._results_lock = threading.Lock()
        self._results = {}
    
    def process_message(
        self,
        content: str,
        user_id: str,
        modality: str = "text",
        modality_params: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the RAG pipeline
        
        Args:
            content: The user's message content
            user_id: User identifier
            modality: Output modality (text, code, structured)
            modality_params: Parameters for modality generation
            metadata: Additional metadata
            
        Returns:
            Dictionary containing the result and processing details
        """
        # Create agent message
        agent_msg = AgentMessage(
            content=content,
            role="user",
            metadata={
                "user_id": user_id,
                "modality": modality,
                "modality_params": modality_params or {},
                **(metadata or {})
            }
        )
        
        # Submit task and wait for result
        task_id = self.processor.submit_task(agent_msg)
        
        # Wait for result (with timeout)
        result = self._wait_for_result(task_id, timeout=30.0)
        
        if result:
            return {
                "status": "success",
                "task_id": task_id,
                "result": result.get("result"),
                "semantic_verification": result.get("semantic_verification"),
                "processing_time_ms": result.get("result", {}).metadata.get("processing_time_ms", 0)
            }
        else:
            return {
                "status": "timeout",
                "task_id": task_id,
                "error": "Processing timeout"
            }
    
    def add_injection_content(
        self,
        content: str,
        provider_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add injection content to the system
        
        Args:
            content: The injection message content
            provider_id: Provider identifier
            metadata: Additional metadata
            
        Returns:
            The injection message ID
        """
        return self.processor.add_injection_message(
            content=content,
            provider_id=provider_id,
            metadata=metadata
        )
    
    def _wait_for_result(self, task_id: str, timeout: float) -> Optional[Dict[str, Any]]:
        """Wait for a task result with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check processor's result queue
            try:
                result = self.processor.result_queue.get(timeout=0.1)
                if result.task_id == task_id:
                    # Store result
                    with self._results_lock:
                        self._results[task_id] = result.result
                    return result.result
                else:
                    # Put back if not our result
                    self.processor.result_queue.put(result)
            except:
                pass
            
            time.sleep(0.1)
        
        return None
    
    def get_injection_messages(self) -> List[Dict[str, Any]]:
        """Get all injection messages in the system"""
        messages = self.processor.get_injection_messages()
        return [
            {
                "message_id": msg.message_id,
                "content": msg.content,
                "provider_id": msg.provider_id,
                "metadata": msg.metadata
            }
            for msg in messages
        ]
    
    def shutdown(self):
        """Shutdown the service and cleanup resources"""
        self.processor.shutdown(wait=True)
