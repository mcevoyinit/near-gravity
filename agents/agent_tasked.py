# agent_framework/agents/task_agent.py
from typing import Dict, Any

from server.agents.agent_base import BaseAgent
from server.agents.agent_llm_wrapper import LLMWrapper
from server.agents.agent_model import AgentMessage


class TaskAgent(BaseAgent):
    """Agent for processing specific tasks with LLM"""

    def __init__(self, config):
        super().__init__(config)
        self.llm = LLMWrapper()

    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process a task message"""
        # Get conversation history
        history = self.get_history()

        # Prepare messages for LLM
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})

        # Add conversation history
        for msg in history[:-1]:  # All except the current message
            messages.append({"role": msg.role, "content": msg.content})

        # Add current message
        messages.append({"role": message.role, "content": message.content})

        # Generate response
        response = self.llm.generate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Add response to history
        response_msg = AgentMessage(content=response, role="assistant")
        self.add_to_history(response_msg)

        return {
            "response": response,
            "model_used": self.config.model,
            "conversation_length": len(self.get_history())
        }
