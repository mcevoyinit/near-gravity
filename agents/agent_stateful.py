# agent_framework/agents/memory_agent.py
from typing import List, Dict, Any
import numpy as np
import json
from datetime import datetime

from server.agents.agent_base import BaseAgent
from server.agents.agent_embeddings import EmbeddingManager
from server.agents.agent_model import AgentMessage
from server.agents.agent_vector_db import DGraphConnector


class MemoryAgent(BaseAgent):
    """Agent with memory capabilities using embeddings and DGraph"""

    def __init__(self, config, dgraph_addresses: List[str] = ["localhost:9080"]):
        super().__init__(config)
        self.embedding_manager = EmbeddingManager()
        self.dgraph = DGraphConnector(dgraph_addresses)
        self._setup_schema()

    def _setup_schema(self):
        """Setup DGraph schema for memories"""
        schema = """
        type Memory {
            content: string
            embedding: [float]
            metadata: string
            timestamp: datetime
            agent_id: string
        }

        content: string @index(fulltext) .
        timestamp: datetime @index(day) .
        agent_id: string @index(exact) .
        """
        try:
            self.dgraph.alter_schema(schema)
        except Exception as e:
            print(f"Schema setup warning: {e}")

    def store_memory(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store a memory with embeddings"""
        # Generate embedding
        embedding = self.embedding_manager.embed_text(content)[0]

        # Prepare mutation
        memory_obj = {
            "uid": "_:memory",
            "dgraph.type": "Memory",
            "content": content,
            "embedding": embedding.tolist(),
            "metadata": json.dumps(metadata),
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.id
        }

        # Store in DGraph
        result = self.dgraph.mutate(memory_obj)
        return result["uids"]["memory"]

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity"""
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_text(query)[0]

        # Query DGraph for memories from this agent
        query_string = """
        query search($agent_id: string) {
            memories(func: eq(agent_id, $agent_id)) @filter(type(Memory)) {
                uid
                content
                embedding
                metadata
                timestamp
            }
        }
        """

        variables = {"$agent_id": self.id}
        result = self.dgraph.query(query_string, variables)
        memories = result.get("memories", [])

        # Calculate similarities
        for memory in memories:
            if "embedding" in memory:
                mem_embedding = np.array(memory["embedding"])
                similarity = self.embedding_manager.similarity(query_embedding, mem_embedding)
                memory["similarity"] = float(similarity)
            else:
                memory["similarity"] = 0.0

        # Sort by similarity and return top results
        memories.sort(key=lambda x: x["similarity"], reverse=True)
        return memories[:limit]

    def search_by_text(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories by text matching"""
        query_string = """
        query search($query: string, $agent_id: string) {
            memories(func: alloftext(content, $query)) @filter(eq(agent_id, $agent_id) AND type(Memory)) {
                uid
                content
                metadata
                timestamp
            }
        }
        """

        variables = {"$query": query, "$agent_id": self.id}
        result = self.dgraph.query(query_string, variables)
        return result.get("memories", [])[:limit]

    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process message with memory context"""
        # Search for relevant memories
        relevant_memories = self.search_memories(message.content)

        # Store the current message as a memory
        memory_id = self.store_memory(
            message.content,
            {"role": message.role, "message_id": message.id}
        )

        # Build context from memories
        context = []
        for memory in relevant_memories[:3]:  # Top 3 most relevant
            context.append({
                "content": memory["content"],
                "similarity": memory.get("similarity", 0),
                "timestamp": memory.get("timestamp")
            })

        return {
            "stored_memory_id": memory_id,
            "relevant_memories": context,
            "total_memories_found": len(relevant_memories)
        }