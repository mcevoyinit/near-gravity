# agent_framework/core/base.py
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Callable

from pydantic import BaseModel, Field


# Base Models
class AgentStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    role: str  # "user", "assistant", "system"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentConfig(BaseModel):
    name: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    thread_pool_size: int = 5
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: AgentMessage
    callback: Optional[Callable] = Field(default=None, exclude=True)
    priority: int = 0
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    task_id: str
    agent_id: str
    status: AgentStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None