"""
PipelineContext - 管道上下文管理器
===================================

负责在50层间传递数据的上下文容器
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


class PipelineContext:
    """
    PipelineContext - 管道上下文管理器
    
    负责在整个50层管道中传递数据
    """
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.user_input: str = ""
        self.request_id: str = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.created_at: datetime = datetime.now()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置数据"""
        self.data[key] = value
    
    def has(self, key: str) -> bool:
        """检查key是否存在"""
        return key in self.data
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def set_metadata(self, key: str, value: Any):
        """设置元数据"""
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'data': self.data,
            'metadata': self.metadata,
            'user_input': self.user_input,
            'request_id': self.request_id,
            'created_at': self.created_at.isoformat()
        }


def create_context() -> PipelineContext:
    """创建新的管道上下文"""
    return PipelineContext()
