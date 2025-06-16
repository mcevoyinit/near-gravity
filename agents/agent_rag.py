# agent_framework/agents/rag_agent.py
from typing import List, Dict, Any

from server.agents.agent_base import BaseAgent
from server.agents.agent_embeddings import EmbeddingManager
from server.agents.agent_llm_wrapper import LLMWrapper
from server.agents.agent_model import AgentConfig, AgentMessage
from server.agents.agent_stateful import MemoryAgent
from server.agents.agent_vector_db import DGraphConnector


class RAGAgent(BaseAgent):
    """Retrieval-Augmented Generation Agent"""

    def __init__(self, config: AgentConfig, dgraph_addresses: List[str] = ["localhost:9080"]):
        super().__init__(config)
        self.llm = LLMWrapper()
        self.embedding_manager = EmbeddingManager()
        self.dgraph = DGraphConnector(dgraph_addresses)
        self.memory_agent = MemoryAgent(config, dgraph_addresses)

    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process with RAG - retrieve context then generate"""
        # Retrieve relevant context
        memories = self.memory_agent.search_memories(message.content, limit=5)

        # Build context string
        context_parts = []
        for memory in memories:
            if memory.get("similarity", 0) > 0.7:  # Relevance threshold
                context_parts.append(f"- {memory['content']}")

        # Prepare enhanced prompt
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})

        # Add context if available
        if context_parts:
            context_prompt = "Relevant context:\n" + "\n".join(context_parts)
            messages.append({"role": "system", "content": context_prompt})

        # Add the user message
        messages.append({"role": message.role, "content": message.content})

        # Generate response with context
        response = self.llm.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Store the interaction
        self.memory_agent.store_memory(
            f"Q: {message.content}\nA: {response}",
            {"type": "qa_pair", "message_id": message.id}
        )

        return {
            "response": response,
            "context_used": len(context_parts),
            "relevant_memories": [
                {"content": m["content"], "similarity": m.get("similarity", 0)}
                for m in memories[:3]
            ]
        }