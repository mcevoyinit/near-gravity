"""
Core RAG Processor for NearGravity
Handles the end-to-end RAG flow using thread-based processing
"""
import threading
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from src.backend.agentic.agent_base import BaseAgent
from src.backend.agentic.agent_embeddings import EmbeddingManager
from src.backend.agentic.agent_llm_wrapper import LLMWrapper
from src.backend.agentic.agent_model import AgentConfig, AgentMessage
from src.backend.agentic.agent_vector_db import DGraphConnector
from src.matching_engine import MatcherEngine
from src.matching_engine.scoring import SimilarityWeightedBidStrategy
from src.models.dto.rag_models import SemanticDelta
from src.models.entities.python.data_models import FinalGeneratedResult, UserContextualMessage, OutputModalityTarget, \
    InjectionMessage
from src.services.crypto.crypto_service import NearGravityCryptoService


class RAGProcessor(BaseAgent):
    """
    Main RAG processor that orchestrates the complete flow from
    user message to generated content with semantic verification
    """
    
    # Semantic thresholds by transformation type
    SEMANTIC_THRESHOLDS = {
        "default": {"cosine": 0.70, "mutual_info": 0.65},  # Lowered for demo
        "summarization": {"cosine": 0.90, "mutual_info": 0.85},
        "translation": {"cosine": 0.92, "mutual_info": 0.90},
        "creative": {"cosine": 0.75, "mutual_info": 0.70}
    }
    
    def __init__(
        self,
        config: AgentConfig,
        dgraph_addresses: List[str] = ["localhost:9080"],
        crypto_config: Optional[Dict[str, str]] = None
    ):
        super().__init__(config)
        
        # Initialize components
        self.embedding_manager = EmbeddingManager()
        self.llm_wrapper = LLMWrapper()
        self.dgraph = DGraphConnector(dgraph_addresses)
        
        # Initialize matching engine
        self.matcher = MatcherEngine(
            scoring_strategy=SimilarityWeightedBidStrategy(),
            similarity_threshold=0.75,  # Raised for better relevance
            max_results=5
        )

        # Initialize crypto service if config provided
        self.crypto_service = None
        if crypto_config:
            self.crypto_service = NearGravityCryptoService(**crypto_config)

        # Thread-safe storage for injection messages
        self._injection_store_lock = threading.RLock()
        self._injection_messages = {}
        self._injection_embeddings = {}
        
        # Load existing injection messages from vector store
        self._load_injection_messages()

    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process a message through the complete RAG pipeline
        """
        start_time = time.time()

        # Parse the message content to extract user message and modality
        user_msg, modality = self._parse_message(message)

        # Step 1: Generate embedding for user message
        user_embedding = self._generate_embedding(user_msg.message)

        # Step 2: Retrieve relevant injection messages
        injection_candidates = self._retrieve_injections(
            user_embedding,
            user_msg.metadata
        )

        # Step 3: Select best injection and combine
        if injection_candidates:
            selected_injection = injection_candidates[0]
            combined_content = self._combine_messages(
                user_msg.message,
                selected_injection.content
            )
            
            # Step 4: Generate content in target modality
            generated_content = self._generate_content(
                combined_content,
                modality,
                user_msg
            )
        else:
            # No semantic match found - return "no vibe found"
            selected_injection = None
            generated_content = "no vibe found"

        # Step 5: Verify semantic integrity
        semantic_delta = self._verify_semantic_integrity(
            user_msg.message,
            generated_content,
            modality.modality
        )

        # Step 6: Record on contracts if available
        tx_hash = None
        if self.crypto_service and semantic_delta.is_within_bounds:
            tx_hash = self._record_on_blockchain(
                user_msg,
                selected_injection,
                generated_content,
                semantic_delta
            )

        # Create final result
        result = FinalGeneratedResult(
            content=generated_content,
            modality=modality.modality,
            user_message_id=user_msg.user_id,
            embedding_id=f"emb_{int(time.time() * 1000)}",
            metadata={
                "processing_time_ms": (time.time() - start_time) * 1000,
                "semantic_delta": {
                    "cosine_similarity": semantic_delta.cosine_similarity,
                    "composite_delta": semantic_delta.composite_delta,
                    "is_within_bounds": semantic_delta.is_within_bounds
                },
                "injection_used": selected_injection.message_id if selected_injection else None,
                "tx_hash": tx_hash
            }
        )

        return {
            "result": result,
            "semantic_verification": semantic_delta,
            "injection_candidates": len(injection_candidates)
        }

    def _parse_message(self, message: AgentMessage) -> Tuple[UserContextualMessage, OutputModalityTarget]:
        """Parse agent message into user message and modality target"""
        # Extract from metadata or create defaults
        metadata = message.metadata or {}

        user_msg = UserContextualMessage(
            message=message.content,
            user_id=metadata.get("user_id", "anonymous"),
            metadata=metadata
        )

        modality = OutputModalityTarget(
            modality=metadata.get("modality", "text"),
            parameters=metadata.get("modality_params", {})
        )

        return user_msg, modality

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using FastEmbed"""
        embedding = self.embedding_manager.embed_text(text)
        return embedding[0] if len(embedding.shape) > 1 else embedding

    def _retrieve_injections(
        self,
        user_embedding: np.ndarray,
        user_metadata: Dict[str, Any]
    ) -> List[InjectionMessage]:
        """Retrieve relevant injection messages based on embedding similarity"""
        with self._injection_store_lock:
            if not self._injection_embeddings:
                return []

            # Calculate similarities
            similarities = []
            for msg_id, embedding in self._injection_embeddings.items():
                similarity = self.embedding_manager.similarity(user_embedding, embedding)
                if similarity >= 0.6:  # Lowered threshold for better matching
                    similarities.append((msg_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top messages
            results = []
            for msg_id, _ in similarities[:5]:
                if msg_id in self._injection_messages:
                    results.append(self._injection_messages[msg_id])
            
            return results
    
    def _combine_messages(self, user_content: str, injection_content: str) -> str:
        """Combine user and injection messages while maintaining coherence"""
        # More assertive combination that ensures injection content is incorporated
        combined = f"""User request: {user_content}

Please help with the user's request while naturally mentioning this relevant option: "{injection_content}"

Make sure to include the specific details from the relevant option in your response."""
        return combined
    
    def _generate_content(
        self,
        combined_content: str,
        modality: OutputModalityTarget,
        user_msg: UserContextualMessage
    ) -> str:
        """Generate content in the target modality"""
        # Build messages for LLM
        messages = []
        
        # Add system prompt based on modality
        if modality.modality == "code":
            system_prompt = "You are an expert programmer. Generate clean, well-commented code."
        elif modality.modality == "structured":
            system_prompt = "You generate well-structured data in JSON format."
        else:
            system_prompt = "You are a helpful assistant that generates clear, engaging content."
        
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": combined_content})
        
        # Generate using LLM
        response = self.llm_wrapper.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return response
    
    def _verify_semantic_integrity(
        self,
        original: str,
        generated: str,
        transformation_type: str
    ) -> SemanticDelta:
        """Verify semantic integrity between original and generated content"""
        # Generate embeddings
        original_emb = self._generate_embedding(original)
        generated_emb = self._generate_embedding(generated)
        
        # Calculate cosine similarity
        cosine_sim = float(self.embedding_manager.similarity(original_emb, generated_emb))
        
        # Simple mutual information approximation (character overlap)
        char_set1 = set(original.lower())
        char_set2 = set(generated.lower())
        mutual_info = len(char_set1.intersection(char_set2)) / max(len(char_set1), len(char_set2))
        
        # Composite delta
        composite = 0.7 * cosine_sim + 0.3 * mutual_info
        
        # Get thresholds
        thresholds = self.SEMANTIC_THRESHOLDS.get(
            transformation_type,
            self.SEMANTIC_THRESHOLDS["default"]
        )
        
        # Check if within bounds
        is_within_bounds = (
            cosine_sim >= thresholds["cosine"] and
            mutual_info >= thresholds["mutual_info"]
        )
        
        return SemanticDelta(
            cosine_similarity=cosine_sim,
            mutual_info_score=mutual_info,
            composite_delta=composite,
            is_within_bounds=is_within_bounds,
            transformation_type=transformation_type,
            threshold=thresholds["cosine"]
        )
    
    def _record_on_blockchain(
        self,
        user_msg: UserContextualMessage,
        injection: Optional[InjectionMessage],
        generated_content: str,
        semantic_delta: SemanticDelta
    ) -> Optional[str]:
        """Record the transaction on contracts with semantic proof"""
        if not self.crypto_service:
            return None
        
        try:
            # Create transaction data
            tx_data = {
                "user_id": user_msg.user_id,
                "timestamp": user_msg.timestamp,
                "semantic_delta": {
                    "cosine": semantic_delta.cosine_similarity,
                    "composite": semantic_delta.composite_delta,
                    "within_bounds": semantic_delta.is_within_bounds
                },
                "injection_id": injection.message_id if injection else None
            }
            
            # Record on contracts
            # This would use the crypto service to record
            # For now, return mock transaction hash
            return f"0x{'0' * 64}"
            
        except Exception as e:
            print(f"Blockchain recording failed: {e}")
            return None
    
    def add_injection_message(
        self,
        content: str,
        provider_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add an injection message to the store"""
        # Generate ID
        message_id = f"inj_{int(time.time() * 1000)}"
        
        # Create injection message
        injection = InjectionMessage(
            message_id=message_id,
            content=content,
            provider_id=provider_id,
            metadata=metadata or {}
        )
        
        # Generate embedding
        embedding = self._generate_embedding(content)
        
        # Store thread-safely
        with self._injection_store_lock:
            self._injection_messages[message_id] = injection
            self._injection_embeddings[message_id] = embedding
        
        return message_id
    
    def get_injection_messages(self) -> List[InjectionMessage]:
        """Get all injection messages"""
        with self._injection_store_lock:
            return list(self._injection_messages.values())
    
    def _load_injection_messages(self):
        """Load injection messages from vector store files"""
        import json
        import os
        import numpy as np
        
        # Try multiple paths for vector store data
        possible_paths = [
            "./data/vector_store",
            "./src/rag/ag_ui/data/vector_store",
            "/Users/mcevoyinit/ai/NearGravity/src/rag/ag_ui/data/vector_store",
            "/Users/mcevoyinit/ai/NearGravity/data/vector_store"
        ]
        
        vector_store_path = None
        for path in possible_paths:
            messages_file = os.path.join(path, "messages.json")
            embeddings_file = os.path.join(path, "embeddings.npz")
            if os.path.exists(messages_file) and os.path.exists(embeddings_file):
                vector_store_path = path
                break
        
        if not vector_store_path:
            print("No vector store data found, starting with empty injection store")
            return
        
        try:
            # Load messages
            messages_file = os.path.join(vector_store_path, "messages.json")
            with open(messages_file, 'r') as f:
                messages_data = json.load(f)
            
            # Load embeddings
            embeddings_file = os.path.join(vector_store_path, "embeddings.npz")
            embeddings_data = np.load(embeddings_file)
            
            # Store in thread-safe manner
            with self._injection_store_lock:
                for msg_id, msg_data in messages_data.items():
                    # Create InjectionMessage object
                    injection = InjectionMessage(
                        message_id=msg_data["message_id"],
                        content=msg_data["content"],
                        provider_id=msg_data["provider_id"],
                        metadata=msg_data.get("metadata", {})
                    )
                    
                    # Store message
                    self._injection_messages[msg_id] = injection
                    
                    # Store embedding if available
                    if msg_id in embeddings_data.files:
                        self._injection_embeddings[msg_id] = embeddings_data[msg_id]
            
            print(f"✅ Loaded {len(self._injection_messages)} injection messages from {vector_store_path}")
            
        except Exception as e:
            print(f"Failed to load injection messages: {e}")
            print("Starting with empty injection store")
