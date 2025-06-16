"""
Vector Store Service for managing injection messages
Provides in-memory storage with optional FAISS backend
"""
import json
import os
import threading
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS not available, using in-memory search")

from models.entities.python.data_models import InjectionMessage
from backend.agentic.agent_embeddings import EmbeddingManager


class VectorStoreService:
    """
    Vector store for injection messages with similarity search
    Supports both in-memory and FAISS backends
    """
    
    def __init__(
        self,
        embedding_dim: int = 384,
        use_faiss: bool = False,
        persist_path: str = "./data/vector_store",
        index_type: str = "Flat"  # Flat, IVF, HNSW
    ):
        self.embedding_dim = embedding_dim
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Storage
        self.messages: Dict[str, InjectionMessage] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        
        # FAISS index
        self.index = None
        self.id_map: Dict[int, str] = {}  # FAISS ID to message ID
        
        # Initialize index
        if self.use_faiss:
            self._init_faiss_index(index_type)
        
        # Load persisted data
        self._load_from_disk()
        
        # Embedding manager for similarity calculations
        self.embedding_manager = EmbeddingManager()
    
    def _init_faiss_index(self, index_type: str):
        """Initialize FAISS index based on type"""
        if index_type == "Flat":
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product
        elif index_type == "IVF":
            quantizer = faiss.IndexFlatIP(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
            self.index.nprobe = 10
        elif index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
    
    def add_message(
        self,
        message: InjectionMessage,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add an injection message with its embedding"""
        with self._lock:
            # Store message and embedding
            self.messages[message.message_id] = message
            self.embeddings[message.message_id] = embedding
            self.metadata[message.message_id] = metadata or {}
            
            # Add to FAISS if available
            if self.use_faiss and self.index is not None:
                # Normalize for inner product
                norm_embedding = embedding / np.linalg.norm(embedding)
                faiss_id = len(self.id_map)
                self.id_map[faiss_id] = message.message_id
                self.index.add(np.array([norm_embedding]))
            
            # Persist
            self._save_to_disk()
            
            return message.message_id
    
    def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.75,  # Raised for better relevance
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[InjectionMessage, float]]:
        """Search for similar messages"""
        with self._lock:
            if not self.embeddings:
                return []
            
            if self.use_faiss and self.index is not None:
                results = self._search_faiss(query_embedding, top_k * 2)  # Get more for filtering
            else:
                results = self._search_memory(query_embedding, top_k * 2)
            
            # Apply filters and threshold
            filtered_results = []
            for msg_id, score in results:
                if score < threshold:
                    continue
                
                message = self.messages.get(msg_id)
                if not message:
                    continue
                
                # Apply filters
                if filters and not self._match_filters(message, filters):
                    continue
                
                filtered_results.append((message, score))
            
            # Return top k after filtering
            return filtered_results[:top_k]
    
    def _search_faiss(
        self,
        query_embedding: np.ndarray,
        k: int
    ) -> List[Tuple[str, float]]:
        """Search using FAISS index"""
        # Normalize query
        norm_query = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(np.array([norm_query]), k)
        
        # Convert to message IDs
        results = []
        for i, score in enumerate(scores[0]):
            if indices[0][i] < 0:  # Invalid index
                continue
            msg_id = self.id_map.get(indices[0][i])
            if msg_id:
                results.append((msg_id, float(score)))
        
        return results
    
    def _search_memory(
        self,
        query_embedding: np.ndarray,
        k: int
    ) -> List[Tuple[str, float]]:
        """Search using in-memory similarity"""
        similarities = []
        
        for msg_id, embedding in self.embeddings.items():
            similarity = self.embedding_manager.similarity(query_embedding, embedding)
            similarities.append((msg_id, float(similarity)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:k]
    
    def _match_filters(
        self,
        message: InjectionMessage,
        filters: Dict[str, Any]
    ) -> bool:
        """Check if message matches filters"""
        for key, value in filters.items():
            if key == "provider_id" and message.provider_id != value:
                return False
            elif key == "tags":
                msg_tags = message.metadata.get("tags", [])
                if not any(tag in msg_tags for tag in value):
                    return False
            elif key in message.metadata:
                if message.metadata[key] != value:
                    return False
        
        return True
    
    def get_message(self, message_id: str) -> Optional[InjectionMessage]:
        """Get message by ID"""
        with self._lock:
            return self.messages.get(message_id)
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        with self._lock:
            if message_id not in self.messages:
                return False
            
            # Remove from stores
            del self.messages[message_id]
            if message_id in self.embeddings:
                del self.embeddings[message_id]
            if message_id in self.metadata:
                del self.metadata[message_id]
            
            # Rebuild FAISS index if needed
            if self.use_faiss:
                self._rebuild_faiss_index()
            
            # Persist
            self._save_to_disk()
            
            return True
    
    def _rebuild_faiss_index(self):
        """Rebuild FAISS index from current embeddings"""
        if not self.use_faiss or not self.index:
            return
        
        # Create new index
        self.index.reset()
        self.id_map.clear()
        
        # Add all embeddings
        for i, (msg_id, embedding) in enumerate(self.embeddings.items()):
            norm_embedding = embedding / np.linalg.norm(embedding)
            self.index.add(np.array([norm_embedding]))
            self.id_map[i] = msg_id
    
    def update_message(
        self,
        message_id: str,
        message: Optional[InjectionMessage] = None,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing message"""
        with self._lock:
            if message_id not in self.messages:
                return False
            
            # Update components
            if message:
                self.messages[message_id] = message
            if embedding is not None:
                self.embeddings[message_id] = embedding
                if self.use_faiss:
                    self._rebuild_faiss_index()
            if metadata is not None:
                self.metadata[message_id] = metadata
            
            # Persist
            self._save_to_disk()
            
            return True
    
    def get_all_messages(self) -> List[InjectionMessage]:
        """Get all messages"""
        with self._lock:
            return list(self.messages.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics"""
        with self._lock:
            return {
                "total_messages": len(self.messages),
                "total_embeddings": len(self.embeddings),
                "providers": len(set(m.provider_id for m in self.messages.values())),
                "using_faiss": self.use_faiss,
                "index_trained": self.index.is_trained if self.use_faiss and self.index else False
            }
    
    def _save_to_disk(self):
        """Persist data to disk"""
        # Save messages
        messages_file = self.persist_path / "messages.json"
        with open(messages_file, 'w') as f:
            messages_data = {
                msg_id: {
                    "message_id": msg.message_id,
                    "content": msg.content,
                    "provider_id": msg.provider_id,
                    "metadata": msg.metadata
                }
                for msg_id, msg in self.messages.items()
            }
            json.dump(messages_data, f, indent=2)
        
        # Save embeddings as numpy array
        if self.embeddings:
            embeddings_file = self.persist_path / "embeddings.npz"
            np.savez_compressed(
                embeddings_file,
                **{msg_id: emb for msg_id, emb in self.embeddings.items()}
            )
        
        # Save metadata
        metadata_file = self.persist_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save FAISS index if available
        if self.use_faiss and self.index and self.index.ntotal > 0:
            index_file = self.persist_path / "faiss.index"
            faiss.write_index(self.index, str(index_file))
            
            # Save ID mapping
            id_map_file = self.persist_path / "id_map.json"
            with open(id_map_file, 'w') as f:
                json.dump(self.id_map, f)
    
    def _load_from_disk(self):
        """Load persisted data from disk"""
        # Load messages
        messages_file = self.persist_path / "messages.json"
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages_data = json.load(f)
                for msg_id, msg_data in messages_data.items():
                    self.messages[msg_id] = InjectionMessage(**msg_data)
        
        # Load embeddings
        embeddings_file = self.persist_path / "embeddings.npz"
        if embeddings_file.exists():
            embeddings_data = np.load(embeddings_file)
            for msg_id in embeddings_data.files:
                self.embeddings[msg_id] = embeddings_data[msg_id]
        
        # Load metadata
        metadata_file = self.persist_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
        
        # Load FAISS index
        if self.use_faiss:
            index_file = self.persist_path / "faiss.index"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))
                
                # Load ID mapping
                id_map_file = self.persist_path / "id_map.json"
                if id_map_file.exists():
                    with open(id_map_file, 'r') as f:
                        id_map_data = json.load(f)
                        self.id_map = {int(k): v for k, v in id_map_data.items()}
