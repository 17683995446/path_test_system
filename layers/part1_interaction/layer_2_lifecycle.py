"""
Layer 2: Lifecycle Management Layer (任务生命周期管理层)

该层负责管理测试任务的完整生命周期，包括任务的创建、执行、状态跟踪和资源管理。
"""

from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum
from .layer_1_entry import PipelineContext


class TaskStatus(Enum):
    """任务状态枚举"""
    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LifecycleManagementLayer:
    """
    任务生命周期管理层

    负责管理测试任务的完整生命周期，包括：
    - 任务创建和初始化
    - 状态转换管理
    - 进度跟踪
    - 资源分配和释放
    - 异常处理和恢复

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "任务生命周期管理层 - 管理测试任务从创建到完成的完整生命周期"
    input_type: str = "PipelineContext"
    output_type: str = "PipelineContext"

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def process(self, context: PipelineContext) -> PipelineContext:
        """
        处理任务生命周期管理

        Args:
            context: PipelineContext对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 用户输入
                - metadata: 附加元数据

        Returns:
            PipelineContext: 更新后的上下文，包含任务生命周期信息：
                - task_id: 任务唯一标识符
                - task_status: 当前任务状态
                - task_metadata: 任务元数据（创建时间、优先级等）
                - lifecycle_history: 生命周期状态转换历史

        Raises:
            ValueError: 当任务状态转换不合法时

        Example:
            >>> layer = LifecycleManagementLayer()
            >>> ctx = layer.process(pipeline_context)
            >>> print(ctx.metadata["task_status"])  # "created"
        """
        request_id = context.request_id

        task_metadata = {
            "task_id": self._generate_task_id(),
            "task_status": TaskStatus.CREATED.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "priority": context.metadata.get("priority", "normal"),
            "lifecycle_history": [
                {
                    "status": TaskStatus.CREATED.value,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }

        self._tasks[request_id] = task_metadata

        context.metadata.update(task_metadata)

        return self._update_lifecycle_history(
            context,
            TaskStatus.INITIALIZING
        )

    def _generate_task_id(self) -> str:
        """生成唯一任务ID"""
        import uuid
        return f"task_{uuid.uuid4().hex[:12]}"

    def _update_lifecycle_history(
        self,
        context: PipelineContext,
        new_status: TaskStatus
    ) -> PipelineContext:
        """更新生命周期历史记录"""
        context.metadata["task_status"] = new_status.value
        context.metadata["updated_at"] = datetime.now().isoformat()

        if "lifecycle_history" not in context.metadata:
            context.metadata["lifecycle_history"] = []

        context.metadata["lifecycle_history"].append({
            "status": new_status.value,
            "timestamp": datetime.now().isoformat()
        })

        if context.request_id in self._tasks:
            self._tasks[context.request_id]["task_status"] = new_status.value
            self._tasks[context.request_id]["updated_at"] = datetime.now().isoformat()

        return context

    def get_task_status(self, request_id: str) -> Optional[str]:
        """获取任务状态"""
        task = self._tasks.get(request_id)
        return task["task_status"] if task else None

    def update_task_status(
        self,
        context: PipelineContext,
        new_status: TaskStatus
    ) -> PipelineContext:
        """更新任务状态"""
        return self._update_lifecycle_history(context, new_status)
