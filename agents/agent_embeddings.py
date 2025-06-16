# agent_framework/models/embeddings.py
from fastembed import TextEmbedding
import numpy as np
from typing import List, Union
import threading


class EmbeddingManager:
    """Thread-safe manager for text embeddings using FastEmbed"""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name)
        self._lock = threading.Lock()

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text (thread-safe)"""
        with self._lock:
            if isinstance(text, str):
                text = [text]

            embeddings = list(self.model.embed(text))
            return np.array(embeddings)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed texts in batches for efficiency"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed_text(batch)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        return np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

    def similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate pairwise similarity matrix"""
        normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return np.dot(normalized, normalized.T)