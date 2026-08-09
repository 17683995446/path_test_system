"""
Layer 1: Interaction Entry Layer (交互入口层)

该层负责处理用户交互入口，接收用户的原始输入并初始化上下文。
是整个管道系统的第一层，负责初步解析和验证用户意图。
"""

from typing import Any
from path_test_system.core.context import PipelineContext


class InteractionEntryLayer:
    """
    交互入口层

    负责接收和处理用户的原始交互输入，进行初步的格式化和验证，
    为后续处理层提供标准化的输入格式。

    Attributes:
        description: 层的功能描述
        input_type: 输入数据类型
        output_type: 输出数据类型
    """

    description: str = "交互入口层 - 接收用户原始输入并初始化管道上下文"
    input_type: str = "RawUserInput"
    output_type: str = "PipelineContext"

    def process(self, context: Any) -> PipelineContext:
        """
        处理用户输入并初始化管道上下文

        Args:
            context: 用户的原始输入，可以是字符串、字典或原始请求对象

        Returns:
            PipelineContext: 标准化的管道上下文对象，包含：
                - request_id: 请求唯一标识符
                - user_input: 解析后的用户输入文本
                - metadata: 附加元数据（如原始输入格式、时间戳等）

        Example:
            >>> layer = InteractionEntryLayer()
            >>> ctx = layer.process("测试登录功能")
            >>> print(ctx.request_id)  # UUID字符串
            >>> print(ctx.user_input)   # "测试登录功能"
        """
        if isinstance(context, str):
            return PipelineContext(
                request_id=self._generate_request_id(),
                user_input=context.strip(),
                metadata={"original_type": "string"}
            )
        elif isinstance(context, dict):
            return PipelineContext(
                request_id=context.get("request_id", self._generate_request_id()),
                user_input=context.get("input", ""),
                metadata=context.get("metadata", {})
            )
        elif isinstance(context, PipelineContext):
            return context
        else:
            return PipelineContext(
                request_id=self._generate_request_id(),
                user_input=str(context),
                metadata={"original_type": type(context).__name__}
            )

    def _generate_request_id(self) -> str:
        """生成唯一的请求ID"""
        import uuid
        return str(uuid.uuid4())
