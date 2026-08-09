"""
Task request model for the path testing system.

This module defines the TaskRequest class which represents a task
to be executed within the path testing framework.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class TaskPriority(Enum):
    """
    Task priority levels for scheduling and execution order.

    Attributes:
        LOW: Low priority tasks, executed when resources are available.
        NORMAL: Standard priority tasks with default scheduling.
        HIGH: High priority tasks that should be executed promptly.
        CRITICAL: Critical tasks that require immediate attention.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """
    Task execution status states.

    Attributes:
        PENDING: Task is waiting to be executed.
        RUNNING: Task is currently being executed.
        COMPLETED: Task has finished successfully.
        FAILED: Task has failed during execution.
        CANCELLED: Task was cancelled before completion.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskRequest:
    """
    Represents a task request within the path testing system.

    A TaskRequest encapsulates all information needed to execute a testing task,
    including the target, parameters, priority, and metadata.

    Attributes:
        task_id: Unique identifier for the task.
        task_type: Type/category of the task (e.g., "path_analysis", "coverage_test").
        target: The target to be tested (file path, function name, module, etc.).
        parameters: Dictionary of task-specific parameters.
        priority: Execution priority level of the task.
        status: Current execution status of the task.
        parent_id: Optional parent task ID for task dependencies.
        metadata: Additional metadata for the task.
        timeout: Optional timeout in seconds for task execution.
        retry_count: Number of times the task has been retried.
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated.

    Example:
        >>> request = TaskRequest(
        ...     task_id="task_001",
        ...     task_type="path_analysis",
        ...     target="/path/to/module.py",
        ...     parameters={"depth": 3, "max_paths": 100},
        ...     priority=TaskPriority.HIGH
        ... )
        >>> print(request.task_id)
        task_001
    """
    task_id: str
    task_type: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None
    retry_count: int = 0
    created_at: Optional[float] = None
    updated_at: Optional[float] = None

    def __post_init__(self) -> None:
        """
        Validate and initialize the task request after dataclass initialization.
        """
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.task_type:
            raise ValueError("task_type cannot be empty")
        if not self.target:
            raise ValueError("target cannot be empty")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("timeout must be positive")

    def mark_running(self) -> None:
        """
        Mark the task as currently running.

        Updates the status to RUNNING and sets the updated_at timestamp.
        """
        self.status = TaskStatus.RUNNING
        self.updated_at = None

    def mark_completed(self) -> None:
        """
        Mark the task as successfully completed.

        Updates the status to COMPLETED and sets the updated_at timestamp.
        """
        self.status = TaskStatus.COMPLETED
        self.updated_at = None

    def mark_failed(self, error: Optional[str] = None) -> None:
        """
        Mark the task as failed.

        Args:
            error: Optional error message describing the failure.
        """
        self.status = TaskStatus.FAILED
        self.metadata["error"] = error
        self.updated_at = None

    def increment_retry(self) -> None:
        """
        Increment the retry count for the task.
        """
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.updated_at = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the task request to a dictionary representation.

        Returns:
            Dictionary containing all task request data.
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "target": self.target,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
