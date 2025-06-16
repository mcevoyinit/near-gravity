# agent_framework/core/agent.py
import queue
import threading
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional, Callable

from .agent_model import AgentConfig, AgentStatus, TaskRequest, TaskResult, AgentMessage


class BaseAgent(ABC):
    """Base agent class with thread-based processing"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = str(uuid.uuid4())
        self.status = AgentStatus.IDLE
        self.conversation_history: List[AgentMessage] = []
        self._history_lock = threading.RLock()
        self._status_lock = threading.Lock()

        # Task queue and processing threads
        self.task_queue = queue.PriorityQueue()
        self.result_queue = queue.Queue()
        self.workers = []
        self._shutdown = threading.Event()

        # Start worker threads
        self._start_workers()

    def _start_workers(self):
        """Start worker threads for processing tasks"""
        for i in range(self.config.thread_pool_size):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"{self.config.name}-worker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)

    def _worker_loop(self):
        """Worker thread loop"""
        while not self._shutdown.is_set():
            try:
                # Get task with timeout to check shutdown
                priority, task_request = self.task_queue.get(timeout=1.0)

                # Process the task
                result = self._process_task(task_request)

                # Put result in queue
                self.result_queue.put(result)

                # Call callback if provided
                if task_request.callback:
                    task_request.callback(result)

                self.task_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    def _process_task(self, task_request: TaskRequest) -> TaskResult:
        """Process a single task"""
        start_time = time.time()

        with self._status_lock:
            self.status = AgentStatus.PROCESSING

        try:
            # Add message to history
            self.add_to_history(task_request.message)

            # Call the abstract process method
            result = self.process(task_request.message)

            processing_time = time.time() - start_time

            with self._status_lock:
                self.status = AgentStatus.COMPLETED

            return TaskResult(
                task_id=task_request.id,
                agent_id=self.id,
                status=AgentStatus.COMPLETED,
                result=result,
                completed_at=datetime.utcnow(),
                processing_time=processing_time,
                metadata=task_request.metadata
            )

        except Exception as e:
            with self._status_lock:
                self.status = AgentStatus.ERROR

            return TaskResult(
                task_id=task_request.id,
                agent_id=self.id,
                status=AgentStatus.ERROR,
                error=str(e),
                completed_at=datetime.utcnow(),
                processing_time=time.time() - start_time
            )

    @abstractmethod
    def process(self, message: AgentMessage) -> Any:
        """Process a message and return a result - implemented by subclasses"""
        pass

    def submit_task(self, message: AgentMessage, priority: int = 0,
                    callback: Optional[Callable] = None) -> str:
        """Submit a task to the processing queue"""
        task_request = TaskRequest(
            message=message,
            priority=priority,
            callback=callback
        )

        # Lower priority number = higher priority
        self.task_queue.put((-priority, task_request))
        return task_request.id

    def add_to_history(self, message: AgentMessage):
        """Thread-safe addition to conversation history"""
        with self._history_lock:
            self.conversation_history.append(message)

    def get_history(self) -> List[AgentMessage]:
        """Thread-safe retrieval of conversation history"""
        with self._history_lock:
            return self.conversation_history.copy()

    def clear_history(self):
        """Thread-safe clearing of conversation history"""
        with self._history_lock:
            self.conversation_history = []

    def shutdown(self, wait: bool = True):
        """Shutdown the agent and its workers"""
        self._shutdown.set()

        if wait:
            for worker in self.workers:
                worker.join(timeout=5.0)

        with self._status_lock:
            self.status = AgentStatus.TERMINATED