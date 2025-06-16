#!/usr/bin/env python3
"""
Semantic Guard Service for NearGravity NEAR Integration
Core service that integrates with NearGravity's RAG system for semantic analysis
"""
import numpy as np
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass

import sys
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import NearGravity core services
from rag.rag_service import RAGService
from models.entities.python.data_models import UserContextualMessage, InjectionMessage


@dataclass
class SemanticEmbedding:
    """Container for semantic embedding data"""
    result_id: str
    content: str
    embedding_vector: np.ndarray
    rag_metadata: Dict[str, Any]
    semantic_hash: str


@dataclass
class SemanticDistance:
    """Container for semantic distance calculation"""
    from_id: str
    to_id: str
    distance: float
    similarity_score: float
    calculation_method: str


@dataclass
class SemanticAnalysisResult:
    """Complete semantic analysis result"""
    query: str
    embeddings: List[SemanticEmbedding]
    distance_matrix: Dict[str, SemanticDistance]
    center_of_gravity: str
    outliers: List[Dict[str, Any]]
    threshold_used: float
    processing_time_ms: int
    metadata: Dict[str, Any]


class SemanticGuardService:
    """
    Core semantic guard service that leverages NearGravity's RAG system.
    Performs semantic analysis, distance calculation, and outlier detection.
    """
    
    def __init__(self, rag_service: RAGService):
        """
        Initialize semantic guard service.
        
        Args:
            rag_service: NearGravity RAG service instance
        """
        self.rag_service = rag_service
        self.embedding_cache = {}  # Cache embeddings for performance
        self.cache_ttl = 300  # 5 minutes
    
    def analyze_search_results(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        semantic_threshold: float = 0.75,
        user_id: str = "semantic_guard"
    ) -> SemanticAnalysisResult:
        """
        Perform complete semantic analysis on search results.
        
        Args:
            query: Original search query
            search_results: List of search result dictionaries
            semantic_threshold: Threshold for outlier detection
            user_id: User identifier for RAG processing
            
        Returns:
            SemanticAnalysisResult: Complete analysis results
        """
        start_time = time.time()
        
        # Step 1: Generate embeddings using NearGravity RAG
        embeddings = self._generate_embeddings(search_results, query, user_id)
        
        # Step 2: Calculate semantic distance matrix
        distance_matrix = self._calculate_distance_matrix(embeddings)
        
        # Step 3: Identify center of gravity
        center_of_gravity = self._find_center_of_gravity(embeddings, distance_matrix)
        
        # Step 4: Detect outliers
        outliers = self._detect_outliers(embeddings, distance_matrix, semantic_threshold)
        
        # Step 5: Compile results
        processing_time = int((time.time() - start_time) * 1000)
        
        return SemanticAnalysisResult(
            query=query,
            embeddings=embeddings,
            distance_matrix=distance_matrix,
            center_of_gravity=center_of_gravity,
            outliers=outliers,
            threshold_used=semantic_threshold,
            processing_time_ms=processing_time,
            metadata={
                "total_results": len(search_results),
                "total_distances": len(distance_matrix),
                "rag_service_model": getattr(self.rag_service, 'model', 'unknown'),
                "analysis_timestamp": int(time.time())
            }
        )
    
    def _generate_embeddings(
        self,
        search_results: List[Dict[str, Any]],
        query: str,
        user_id: str
    ) -> List[SemanticEmbedding]:
        """
        Generate semantic embeddings using NearGravity RAG service.
        
        Args:
            search_results: Search result data
            query: Original query for context
            user_id: User identifier
            
        Returns:
            list: List of SemanticEmbedding objects
        """
        embeddings = []
        
        for result in search_results:
            # Combine title and snippet for rich content
            content = f"{result.get('title', '')} {result.get('snippet', '')}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check cache first
            cached_embedding = self._get_cached_embedding(content_hash)
            if cached_embedding:
                embeddings.append(SemanticEmbedding(
                    result_id=result.get('id', f"result_{len(embeddings)}"),
                    content=content,
                    embedding_vector=cached_embedding['vector'],
                    rag_metadata=cached_embedding['metadata'],
                    semantic_hash=content_hash
                ))
                continue
            
            try:
                # Process through NearGravity RAG service
                rag_result = self.rag_service.process_message(
                    content=content,
                    user_id=user_id,
                    modality="structured",
                    metadata={
                        "source": "search_result",
                        "url": result.get('url', ''),
                        "rank": result.get('rank', 0),
                        "original_query": query,
                        "provider": result.get('provider', 'unknown')
                    }
                )
                
                if rag_result.get('status') == 'success':
                    # Extract embedding from semantic verification
                    semantic_verification = rag_result.get('semantic_verification', {})
                    
                    # Create embedding vector (mock for now - real implementation would extract from RAG)
                    # TODO: Extract actual embedding vector from NearGravity RAG system
                    embedding_vector = self._mock_embedding_from_content(content)
                    
                    # Cache the embedding
                    self._cache_embedding(content_hash, embedding_vector, rag_result)
                    
                    embeddings.append(SemanticEmbedding(
                        result_id=result.get('id', f"result_{len(embeddings)}"),
                        content=content,
                        embedding_vector=embedding_vector,
                        rag_metadata=rag_result,
                        semantic_hash=content_hash
                    ))
                else:
                    # Fallback: create mock embedding if RAG fails
                    print(f"RAG processing failed for result {result.get('id')}: {rag_result.get('error')}")
                    embedding_vector = self._mock_embedding_from_content(content)
                    
                    embeddings.append(SemanticEmbedding(
                        result_id=result.get('id', f"result_{len(embeddings)}"),
                        content=content,
                        embedding_vector=embedding_vector,
                        rag_metadata={"status": "fallback", "error": rag_result.get('error')},
                        semantic_hash=content_hash
                    ))
                    
            except Exception as e:
                print(f"Error processing result {result.get('id')} through RAG: {e}")
                # Create fallback embedding
                embedding_vector = self._mock_embedding_from_content(content)
                
                embeddings.append(SemanticEmbedding(
                    result_id=result.get('id', f"result_{len(embeddings)}"),
                    content=content,
                    embedding_vector=embedding_vector,
                    rag_metadata={"status": "error", "error": str(e)},
                    semantic_hash=content_hash
                ))
        
        return embeddings
    
    def _calculate_distance_matrix(
        self,
        embeddings: List[SemanticEmbedding]
    ) -> Dict[str, SemanticDistance]:
        """
        Calculate semantic distance matrix between all embedding pairs.
        Avoids duplicate calculations (A->B == B->A).
        
        Args:
            embeddings: List of semantic embeddings
            
        Returns:
            dict: Distance matrix with pair keys
        """
        distance_matrix = {}
        calculated_pairs = set()
        
        for i, embedding_a in enumerate(embeddings):
            for j, embedding_b in enumerate(embeddings):
                if i == j:  # Skip self-comparison
                    continue
                
                # Create consistent pair key (smaller ID first to avoid duplicates)
                pair_key = tuple(sorted([embedding_a.result_id, embedding_b.result_id]))
                if pair_key in calculated_pairs:
                    continue
                
                # Calculate cosine similarity
                similarity_score = cosine_similarity(
                    embedding_a.embedding_vector.reshape(1, -1),
                    embedding_b.embedding_vector.reshape(1, -1)
                )[0][0]
                
                # Convert similarity to distance (1 - similarity)
                distance = 1.0 - similarity_score
                
                # Store with directional key for easy lookup
                distance_obj = SemanticDistance(
                    from_id=embedding_a.result_id,
                    to_id=embedding_b.result_id,
                    distance=distance,
                    similarity_score=similarity_score,
                    calculation_method="cosine_distance"
                )
                
                distance_matrix[f"{embedding_a.result_id}->{embedding_b.result_id}"] = distance_obj
                
                # Also store reverse direction for easy lookup
                reverse_distance_obj = SemanticDistance(
                    from_id=embedding_b.result_id,
                    to_id=embedding_a.result_id,
                    distance=distance,
                    similarity_score=similarity_score,
                    calculation_method="cosine_distance"
                )
                distance_matrix[f"{embedding_b.result_id}->{embedding_a.result_id}"] = reverse_distance_obj
                
                calculated_pairs.add(pair_key)
        
        return distance_matrix
    
    def _find_center_of_gravity(
        self,
        embeddings: List[SemanticEmbedding],
        distance_matrix: Dict[str, SemanticDistance]
    ) -> str:
        """
        Find the result with minimum average distance to all others (center of gravity).
        
        Args:
            embeddings: List of semantic embeddings
            distance_matrix: Calculated distances
            
        Returns:
            str: Result ID of center of gravity
        """
        gravity_scores = {}
        
        for embedding in embeddings:
            total_distance = 0.0
            count = 0
            
            # Calculate average distance to all other results
            for other_embedding in embeddings:
                if embedding.result_id == other_embedding.result_id:
                    continue
                
                distance_key = f"{embedding.result_id}->{other_embedding.result_id}"
                if distance_key in distance_matrix:
                    total_distance += distance_matrix[distance_key].distance
                    count += 1
            
            # Store average distance (lower is better for center of gravity)
            if count > 0:
                gravity_scores[embedding.result_id] = total_distance / count
            else:
                gravity_scores[embedding.result_id] = float('inf')
        
        # Return result with minimum average distance
        if gravity_scores:
            return min(gravity_scores, key=gravity_scores.get)
        else:
            return embeddings[0].result_id if embeddings else "unknown"
    
    def _detect_outliers(
        self,
        embeddings: List[SemanticEmbedding],
        distance_matrix: Dict[str, SemanticDistance],
        threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Detect semantic outliers based on distance threshold.
        
        Args:
            embeddings: List of semantic embeddings
            distance_matrix: Calculated distances
            threshold: Distance threshold for outlier detection
            
        Returns:
            list: List of outlier information
        """
        outliers = []
        
        for embedding in embeddings:
            max_distance = 0.0
            outlier_distances = []
            
            # Check distances to all other results
            for other_embedding in embeddings:
                if embedding.result_id == other_embedding.result_id:
                    continue
                
                distance_key = f"{embedding.result_id}->{other_embedding.result_id}"
                if distance_key in distance_matrix:
                    distance = distance_matrix[distance_key].distance
                    max_distance = max(max_distance, distance)
                    
                    if distance > threshold:
                        outlier_distances.append({
                            "to_result": other_embedding.result_id,
                            "distance": distance,
                            "threshold_exceeded_by": distance - threshold
                        })
            
            # If this result has distances exceeding threshold, mark as outlier
            if outlier_distances:
                severity = "high" if max_distance > threshold * 1.5 else "medium"
                
                outliers.append({
                    "result_id": embedding.result_id,
                    "max_distance": max_distance,
                    "threshold": threshold,
                    "severity": severity,
                    "outlier_distances": outlier_distances,
                    "reason": f"Semantic distance exceeds threshold of {threshold}"
                })
        
        return outliers
    
    def _mock_embedding_from_content(self, content: str) -> np.ndarray:
        """
        Generate mock embedding vector from content.
        TODO: Replace with actual embedding extraction from NearGravity RAG.
        
        Args:
            content: Text content
            
        Returns:
            numpy array: Mock embedding vector
        """
        # Create deterministic but varied embeddings based on content
        np.random.seed(hash(content) % (2**32))
        
        # Generate 384-dimensional vector (common embedding size)
        embedding = np.random.normal(0, 1, 384)
        
        # Normalize to unit vector
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add some content-specific variation
        content_hash = hash(content.lower())
        variation = np.sin(np.arange(384) * content_hash) * 0.1
        embedding += variation
        
        # Re-normalize
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def _get_cached_embedding(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached embedding if still valid"""
        if content_hash in self.embedding_cache:
            cached_data, timestamp = self.embedding_cache[content_hash]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.embedding_cache[content_hash]
        return None
    
    def _cache_embedding(self, content_hash: str, vector: np.ndarray, metadata: Dict[str, Any]):
        """Cache embedding data"""
        self.embedding_cache[content_hash] = (
            {
                "vector": vector,
                "metadata": metadata
            },
            time.time()
        )
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.embedding_cache),
            "cache_ttl_seconds": self.cache_ttl
        }


# Factory function for creating semantic guard service
def create_semantic_guard_service(rag_service: RAGService) -> SemanticGuardService:
    """
    Factory function to create semantic guard service.
    
    Args:
        rag_service: NearGravity RAG service instance
        
    Returns:
        SemanticGuardService: Configured service instance
    """
    return SemanticGuardService(rag_service)