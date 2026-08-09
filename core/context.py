"""
Pipeline Context - 流水线上下文
在系统中全局使用的上下文对象
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PipelineContext:
    """管道上下文数据类 - 贯穿整个50层流水线的数据容器"""

    request_id: str = ""
    user_input: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)

    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    current_layer: int = 0

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def set(self, key: str, value: Any) -> None:
        """设置上下文数据"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)

    def has(self, key: str) -> bool:
        """检查是否存在指定键"""
        return key in self.data

    def remove(self, key: str) -> bool:
        """移除指定键"""
        if key in self.data:
            del self.data[key]
            return True
        return False

    def clear(self) -> None:
        """清空所有数据"""
        self.data.clear()
        self.errors.clear()
        self.execution_history.clear()

    def record_layer_execution(self, layer_num: int, output: Any = None) -> None:
        """记录层执行历史"""
        self.current_layer = layer_num
        self.execution_history.append({
            "layer": layer_num,
            "output_type": type(output).__name__ if output else "None",
            "has_output": output is not None,
            "timestamp": datetime.now().isoformat()
        })

    def add_error(self, layer_num: int, error: Exception, context: str = "") -> None:
        """记录错误"""
        self.errors.append({
            "layer": layer_num,
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "total_layers": self.current_layer,
            "layers_executed": len(self.execution_history),
            "errors_count": len(self.errors),
            "data_keys": list(self.data.keys()),
            "duration": (
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time else None
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "request_id": self.request_id,
            "user_input": self.user_input,
            "metadata": self.metadata,
            "data": self.data,
            "execution_history": self.execution_history,
            "errors": self.errors,
            "current_layer": self.current_layer,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
