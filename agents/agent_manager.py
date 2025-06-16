# agent_framework/orchestrator/manager.py
import threading
import time
from collections import defaultdict
from typing import Dict, List, Optional, Any, Callable

from server.agents.agent_base import BaseAgent
from server.agents.agent_model import TaskResult, AgentMessage, AgentStatus


class AgentManager:
    """Thread-based orchestrator for managing multiple agents"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self._agents_lock = threading.RLock()

        # Global result storage
        self.results: Dict[str, TaskResult] = {}
        self._results_lock = threading.Lock()

        # Routing
        self._round_robin_index = 0
        self._rr_lock = threading.Lock()

        # Monitoring
        self.task_history = defaultdict(list)
        self._history_lock = threading.Lock()

    def register_agent(self, agent: BaseAgent) -> str:
        """Register an agent with the manager"""
        with self._agents_lock:
            self.agents[agent.id] = agent
            return agent.id

    def unregister_agent(self, agent_id: str):
        """Remove an agent from the manager"""
        with self._agents_lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.shutdown()
                del self.agents[agent_id]

    def submit_task(self, agent_id: str, message: AgentMessage,
                    priority: int = 0, callback: Optional[Callable] = None) -> str:
        """Submit a task to a specific agent"""
        with self._agents_lock:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")

            agent = self.agents[agent_id]

        # Create wrapper callback to store results
        def result_callback(result: TaskResult):
            with self._results_lock:
                self.results[result.task_id] = result

            with self._history_lock:
                self.task_history[agent_id].append(result)

            if callback:
                callback(result)

        task_id = agent.submit_task(message, priority, result_callback)
        return task_id

    def broadcast_task(self, message: AgentMessage, priority: int = 0) -> List[str]:
        """Send a task to all agents"""
        task_ids = []

        with self._agents_lock:
            agent_ids = list(self.agents.keys())

        for agent_id in agent_ids:
            try:
                task_id = self.submit_task(agent_id, message, priority)
                task_ids.append(task_id)
            except Exception as e:
                print(f"Failed to submit to agent {agent_id}: {e}")

        return task_ids

    def route_task(self, message: AgentMessage, strategy: str = "round_robin",
                   priority: int = 0) -> str:
        """Route task based on strategy"""

        if strategy == "round_robin":
            return self._round_robin_route(message, priority)

        elif strategy == "least_busy":
            return self._least_busy_route(message, priority)

        elif strategy == "capability":
            return self._capability_route(message, priority)

        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")

    def _round_robin_route(self, message: AgentMessage, priority: int) -> str:
        """Round-robin routing"""
        with self._agents_lock:
            if not self.agents:
                raise ValueError("No agents available")

            agent_ids = list(self.agents.keys())

        with self._rr_lock:
            agent_id = agent_ids[self._round_robin_index % len(agent_ids)]
            self._round_robin_index += 1

        return self.submit_task(agent_id, message, priority)

    def _least_busy_route(self, message: AgentMessage, priority: int) -> str:
        """Route to least busy agent"""
        with self._agents_lock:
            if not self.agents:
                raise ValueError("No agents available")

            # Find agent with smallest queue
            least_busy_id = None
            min_queue_size = float('inf')

            for agent_id, agent in self.agents.items():
                queue_size = agent.task_queue.qsize()
                if queue_size < min_queue_size:
                    min_queue_size = queue_size
                    least_busy_id = agent_id

            if least_busy_id is None:
                least_busy_id = list(self.agents.keys())[0]

        return self.submit_task(least_busy_id, message, priority)

    def _capability_route(self, message: AgentMessage, priority: int) -> str:
        """Route based on agent capabilities (requires metadata)"""
        # This is a simplified version - you could extend this
        # to match message content with agent capabilities

        with self._agents_lock:
            # Look for agents with specific capabilities
            for agent_id, agent in self.agents.items():
                if "capabilities" in agent.config.metadata:
                    capabilities = agent.config.metadata["capabilities"]
                    # Simple keyword matching
                    for capability in capabilities:
                        if capability.lower() in message.content.lower():
                            return self.submit_task(agent_id, message, priority)

            # Fallback to round-robin
            return self._round_robin_route(message, priority)

    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """Get result for a task, optionally waiting"""
        start_time = time.time()

        while True:
            with self._results_lock:
                if task_id in self.results:
                    return self.results[task_id]

            if timeout is not None and (time.time() - start_time) > timeout:
                return None

            time.sleep(0.1)  # Poll interval

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for an agent"""
        with self._history_lock:
            history = self.task_history.get(agent_id, [])

        if not history:
            return {"total_tasks": 0}

        completed = [t for t in history if t.status == AgentStatus.COMPLETED]
        errors = [t for t in history if t.status == AgentStatus.ERROR]

        avg_time = sum(t.processing_time or 0 for t in completed) / len(completed) if completed else 0

        return {
            "total_tasks": len(history),
            "completed": len(completed),
            "errors": len(errors),
            "error_rate": len(errors) / len(history),
            "avg_processing_time": avg_time
        }

    def shutdown_all(self):
        """Shutdown all agents"""
        with self._agents_lock:
            for agent in self.agents.values():
                agent.shutdown()