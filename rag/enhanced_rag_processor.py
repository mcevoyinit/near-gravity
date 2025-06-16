"""
Enhanced RAG Processor for NearGravity
Builds on existing RAGProcessor with production features
"""
import json
import threading
import time
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

import os
import sys

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from .rag_processor import RAGProcessor
    from .model_config import SemanticDelta
except ImportError:
    try:
        from rag_processor import RAGProcessor
        from models.dto.rag_models import SemanticDelta
    except ImportError:
        from src.rag.rag_processor import RAGProcessor
        from src.models.dto.rag_models import SemanticDelta

from src.backend.agentic.agent_model import AgentConfig, AgentMessage
from src.models.entities.python.data_models import (
    UserContextualMessage, 
    OutputModalityTarget,
    InjectionMessage,
    FinalGeneratedResult
)


class CombinationStrategy:
    """Base class for message combination strategies"""
    
    def combine(self, user_msg: str, injection_msg: str) -> str:
        raise NotImplementedError


class ContextualCombination(CombinationStrategy):
    """Add injection as contextual information"""
    
    def combine(self, user_msg: str, injection_msg: str) -> str:
        return f"{user_msg}\n\n[Relevant context: {injection_msg}]"


class InlineCombination(CombinationStrategy):
    """Weave injection naturally into message"""
    
    def combine(self, user_msg: str, injection_msg: str) -> str:
        # Simple inline - in production, use NLP to find insertion points
        sentences = user_msg.split('. ')
        if len(sentences) > 1:
            # Insert after first sentence
            sentences.insert(1, injection_msg)
            return '. '.join(sentences)
        else:
            return f"{user_msg} {injection_msg}"


class AugmentedCombination(CombinationStrategy):
    """Add injection as additional information"""
    
    def combine(self, user_msg: str, injection_msg: str) -> str:
        return f"{user_msg}\n\nYou might also be interested in: {injection_msg}"


class EnhancedRAGProcessor(RAGProcessor):
    """
    Enhanced RAG processor with production features:
    - Multiple combination strategies
    - Caching layer
    - Detailed metrics
    - Batch processing support
    """
    
    def __init__(
        self,
        config: AgentConfig,
        dgraph_addresses: List[str] = ["localhost:9080"],
        crypto_config: Optional[Dict[str, str]] = None,
        enable_cache: bool = True,
        cache_ttl: int = 3600
    ):
        super().__init__(config, dgraph_addresses, crypto_config)
        
        # Combination strategies
        self.combination_strategies = {
            "contextual": ContextualCombination(),
            "inline": InlineCombination(),
            "augmented": AugmentedCombination()
        }
        
        # Caching
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self._embedding_cache = {}
        self._cache_lock = threading.RLock()
        
        # Metrics
        self._metrics_lock = threading.Lock()
        self._metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_processing_time": 0,
            "avg_semantic_delta": 0,
            "total_injections_used": 0
        }
    
    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Enhanced processing with metrics and caching"""
        start_time = time.time()
        
        # Update metrics
        with self._metrics_lock:
            self._metrics["total_requests"] += 1
        
        # Process through parent
        result = super().process(message)
        
        # Update metrics
        processing_time = (time.time() - start_time) * 1000
        with self._metrics_lock:
            # Running average
            n = self._metrics["total_requests"]
            self._metrics["avg_processing_time"] = (
                (self._metrics["avg_processing_time"] * (n - 1) + processing_time) / n
            )
            
            # Update semantic delta average
            if "semantic_verification" in result:
                delta = result["semantic_verification"].composite_delta
                self._metrics["avg_semantic_delta"] = (
                    (self._metrics["avg_semantic_delta"] * (n - 1) + delta) / n
                )
        
        return result
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding with caching"""
        if not self.enable_cache:
            return super()._generate_embedding(text)
        
        # Check cache
        cache_key = hash(text)
        with self._cache_lock:
            if cache_key in self._embedding_cache:
                entry = self._embedding_cache[cache_key]
                if time.time() - entry["timestamp"] < self.cache_ttl:
                    with self._metrics_lock:
                        self._metrics["cache_hits"] += 1
                    return entry["embedding"]
        
        # Cache miss - generate
        with self._metrics_lock:
            self._metrics["cache_misses"] += 1
        
        embedding = super()._generate_embedding(text)
        
        # Store in cache
        with self._cache_lock:
            self._embedding_cache[cache_key] = {
                "embedding": embedding,
                "timestamp": time.time()
            }
            
            # Simple cache eviction - remove oldest if > 1000 entries
            if len(self._embedding_cache) > 1000:
                oldest_key = min(
                    self._embedding_cache.keys(),
                    key=lambda k: self._embedding_cache[k]["timestamp"]
                )
                del self._embedding_cache[oldest_key]
        
        return embedding
    
    def _combine_messages(
        self, 
        user_content: str, 
        injection_content: str,
        strategy: str = "contextual"
    ) -> str:
        """Combine messages using specified strategy"""
        if strategy not in self.combination_strategies:
            strategy = "contextual"
        
        combiner = self.combination_strategies[strategy]
        return combiner.combine(user_content, injection_content)
    
    def _select_combination_strategy(
        self,
        user_msg: UserContextualMessage,
        injection: InjectionMessage
    ) -> str:
        """Select best combination strategy based on context"""
        # Simple heuristic - in production, use ML model
        user_length = len(user_msg.message.split())
        
        if user_length < 20:
            # Short messages - inline works better
            return "inline"
        elif user_length > 100:
            # Long messages - contextual to avoid disruption
            return "contextual"
        else:
            # Medium - augmented for natural flow
            return "augmented"
    
    def process_batch(
        self,
        messages: List[AgentMessage],
        priority: int = 0
    ) -> List[str]:
        """Process multiple messages in batch"""
        task_ids = []
        
        # Submit all tasks
        for msg in messages:
            task_id = self.submit_task(msg, priority=priority)
            task_ids.append(task_id)
        
        # Wait for all results
        results = []
        for task_id in task_ids:
            # Wait for each result
            result = self._wait_for_task(task_id, timeout=30.0)
            results.append(result)
        
        return results
    
    def _wait_for_task(self, task_id: str, timeout: float) -> Optional[Dict[str, Any]]:
        """Wait for a specific task to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check result queue
                result = self.result_queue.get(timeout=0.1)
                if result.task_id == task_id:
                    return result.result
                else:
                    # Not our result, put it back
                    self.result_queue.put(result)
            except:
                pass
            
            time.sleep(0.1)
        
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self._metrics_lock:
            return self._metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics counters"""
        with self._metrics_lock:
            self._metrics = {
                "total_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "avg_processing_time": 0,
                "avg_semantic_delta": 0,
                "total_injections_used": 0
            }
    
    def optimize_injection_selection(
        self,
        injection_candidates: List[InjectionMessage],
        user_metadata: Dict[str, Any]
    ) -> List[InjectionMessage]:
        """Optimize injection selection based on multiple factors"""
        if not injection_candidates:
            return []
        
        # Score each injection
        scored_injections = []
        for injection in injection_candidates:
            score = self._score_injection(injection, user_metadata)
            scored_injections.append((injection, score))
        
        # Sort by score
        scored_injections.sort(key=lambda x: x[1], reverse=True)
        
        # Return top selections
        return [inj for inj, _ in scored_injections[:3]]
    
    def _score_injection(
        self,
        injection: InjectionMessage,
        user_metadata: Dict[str, Any]
    ) -> float:
        """Score an injection based on relevance and business rules"""
        score = 0.0
        
        # Base relevance score (would come from vector similarity)
        score += 0.5
        
        # Boost for matching user preferences
        if "preferences" in user_metadata:
            prefs = user_metadata["preferences"]
            if any(pref in injection.metadata.get("tags", []) for pref in prefs):
                score += 0.2
        
        # Boost for provider bid amount
        bid = injection.metadata.get("bid_amount", 0)
        score += min(bid * 100, 0.3)  # Cap bid influence
        
        # Recency boost
        if "created_at" in injection.metadata:
            age_hours = (time.time() - injection.metadata["created_at"]) / 3600
            if age_hours < 24:
                score += 0.1
        
        return score
